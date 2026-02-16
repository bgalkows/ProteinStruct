"""FastAPI main app logic"""

import logging
import subprocess
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.config import DEFAULT_NUM_SEQUENCES, MODEL_WEIGHTS_FILE
from app.dependencies import cleanup, parse_design_params, save_upload
from app.proteinmpnn.wrapper import design_sequences
from app.schemas import DesignMetadata, DesignResponse
from app.validation import PDBValidationError, validate_pdb

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown events"""
    if not MODEL_WEIGHTS_FILE.exists():
        raise RuntimeError(
            f"Model weights not found at {MODEL_WEIGHTS_FILE}. "
            "Run: python scripts/download_weights.py"
        )
    app.state.model_ready = True
    print(f"Model ready: {MODEL_WEIGHTS_FILE}")

    yield


app = FastAPI(
    title="ProteinMPNN Mini-Service",
    version="0.1.0",
    lifespan=lifespan,
)
app.state.model_ready = False


@app.get("/health")
def health():
    """Liveness probe."""
    return {
        "status": "ok",
        "model_loaded": app.state.model_ready,
    }


@app.get("/")
def root():
    """Redirect to health for browser"""
    return {"message": "ProteinMPNN service", "docs": "/docs"}


@app.post("/design", response_model=DesignResponse)
async def design(
    pdb_file: UploadFile = File(...),
    chains: str = Form(...),
    num_sequences: int = Form(default=DEFAULT_NUM_SEQUENCES),
):
    """Design protein sequences for a given PDB structure."""
    # Parse and validate form params
    try:
        params = parse_design_params(chains, num_sequences)
    except ValueError as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})

    # Save upload to temp file
    tmp_path = await save_upload(pdb_file)
    try:
        # Validate PDB structure
        structure = validate_pdb(tmp_path, params.chains)

        # Count residues across requested chains
        num_residues = 0
        for chain_id in params.chains:
            chain = structure[0][chain_id]
            num_residues += sum(1 for r in chain if r.get_id()[0] == " ")

        # Run ProteinMPNN
        sequences = design_sequences(
            pdb_path=str(tmp_path),
            chains=params.chains,
            num_sequences=params.num_sequences,
        )

        return DesignResponse(
            metadata=DesignMetadata(
                num_residues=num_residues,
                chains=params.chains,
                num_sequences=len(sequences),
            ),
            sequences=sequences,
        )

    except PDBValidationError as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})

    except subprocess.TimeoutExpired:
        return JSONResponse(
            status_code=504,
            content={"detail": "ProteinMPNN timed out"},
        )

    except Exception:
        logger.exception("Unexpected error in /design")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    finally:
        cleanup(tmp_path)