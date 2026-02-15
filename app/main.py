""" FastAPI main app logic"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import MODEL_WEIGHTS_FILE


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown events."""
    # Model weights check
    if not MODEL_WEIGHTS_FILE.exists():
        print(f"WARNING: Model weights not found at {MODEL_WEIGHTS_FILE}")
        app.state.model_ready = False
    else:
        app.state.model_ready = True
        print(f"Model ready: {MODEL_WEIGHTS_FILE}")
    
    yield
    

app = FastAPI(
    title="ProteinMPNN Mini-Service",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/health")
def health():
    """Liveness probe."""
    return {
        "status": "ok",
        "model_loaded": app.state.model_ready
    }


@app.get("/")
def root():
    """Redirect to health for browser"""
    return {"message": "ProteinMPNN service", "docs": "/docs"}