"""Pydantic models for the /design endpoint"""

from pydantic import BaseModel, Field

from app.config import DEFAULT_NUM_SEQUENCES, MAX_SEQUENCES


class DesignMetadata(BaseModel):
    num_residues: int
    chains: list[str]
    num_sequences: int


class DesignResponse(BaseModel):
    status: str = "success"
    metadata: DesignMetadata
    native_sequence: str
    sequences: list[str]


class DesignParams(BaseModel):
    """Validated form parameters for /design."""

    chains: list[str] = Field(min_length=1)
    num_sequences: int = Field(
        default=DEFAULT_NUM_SEQUENCES, ge=1, le=MAX_SEQUENCES
    )