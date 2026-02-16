"""PDB data validation for ProteinMPNN"""

from pathlib import Path

from Bio.PDB import PDBParser
from Bio.PDB.Structure import Structure

from app.config import MAX_PDB_SIZE_MB, MIN_CA_ATOMS


class PDBValidationError(ValueError):
    """Raised when a PDB file fails validation. Maps to HTTP 422"""


def validate_pdb(
    pdb_path: Path,
    chains: list[str],
    max_size_mb: float = MAX_PDB_SIZE_MB,
) -> Structure:
    """Validate a PDB file for ProteinMPNN consumption.

    Checks run in order of increasing cost. Returns the parsed BioPython
    Structure on success so the caller can reuse it.

    Raises:
        PDBValidationError: On any validation failure.
    """
    _check_file_size(pdb_path, max_size_mb)
    _check_has_atom_records(pdb_path)
    structure = _parse_structure(pdb_path)
    _check_chains_exist(structure, chains)
    _check_backbone(structure, chains)
    return structure


def _check_file_size(pdb_path: Path, max_size_mb: float) -> None:
    try:
        size_bytes = pdb_path.stat().st_size
    except FileNotFoundError:
        raise PDBValidationError(f"PDB file not found: {pdb_path}")
    size_mb = size_bytes / (1024 * 1024)
    if size_mb > max_size_mb:
        raise PDBValidationError(
            f"PDB file exceeds {max_size_mb} MB limit ({size_mb:.1f} MB)"
        )


def _check_has_atom_records(pdb_path: Path) -> None:
    with open(pdb_path) as f:
        for line in f:
            if line.startswith("ATOM  "):
                return
    raise PDBValidationError("PDB file contains no ATOM records")


def _parse_structure(pdb_path: Path) -> Structure:
    parser = PDBParser(QUIET=True)
    try:
        structure = parser.get_structure("input", str(pdb_path))
    except Exception as e:
        raise PDBValidationError(f"Failed to parse PDB file: {e}") from e
    return structure


def _check_chains_exist(structure: Structure, chains: list[str]) -> None:
    available = {chain.get_id() for chain in structure[0]}
    missing = set(chains) - available
    if missing:
        raise PDBValidationError(
            f"Chain(s) {sorted(missing)} not found in structure. "
            f"Available chains: {sorted(available)}"
        )


def _check_backbone(structure: Structure, chains: list[str]) -> None:
    for chain_id in chains:
        chain = structure[0][chain_id]
        standard_residues = [r for r in chain if r.get_id()[0] == " "]
        if not standard_residues:
            raise PDBValidationError(
                f"Chain {chain_id} has no standard amino acid residues"
            )
        ca_count = sum(1 for r in standard_residues if "CA" in r)
        if ca_count < MIN_CA_ATOMS:
            raise PDBValidationError(
                f"Chain {chain_id} has only {ca_count} CA atoms "
                f"(minimum {MIN_CA_ATOMS} required for ProteinMPNN)"
            )


# Helper
def count_hetatm(pdb_path: str) -> int:
    """Count HETATM records in PDB file"""
    with open(pdb_path) as f:
        return sum(1 for line in f if line.startswith("HETATM"))