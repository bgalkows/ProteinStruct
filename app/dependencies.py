"""FastAPI dependencies for file upload handling."""

import json
import tempfile
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.schemas import DesignParams


async def save_upload(upload: UploadFile) -> Path:
    """Save an UploadFile to a uniquely-named temp file. Caller must delete."""
    suffix = Path(upload.filename or "upload.pdb").suffix or ".pdb"
    tmp = Path(tempfile.gettempdir()) / f"mpnn_{uuid.uuid4().hex}{suffix}"
    content = await upload.read()
    tmp.write_bytes(content)
    return tmp


def parse_design_params(chains: str, num_sequences: int) -> DesignParams:
    """Parse and validate the chains JSON string + num_sequences."""
    try:
        chains_list = json.loads(chains)
    except (json.JSONDecodeError, TypeError) as e:
        raise ValueError(f"Invalid chains JSON: {e}") from e

    if not isinstance(chains_list, list) or not all(
        isinstance(c, str) for c in chains_list
    ):
        raise ValueError("chains must be a JSON array of strings")

    return DesignParams(chains=chains_list, num_sequences=num_sequences)


def cleanup(path: Path) -> None:
    """Remove a temp file, ignoring errors."""
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass
