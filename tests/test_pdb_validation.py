import pytest
from pathlib import Path

from Bio.PDB.Structure import Structure

from app.validation.pdb import PDBValidationError, validate_pdb
from app.config import TEST_PDBS_DIR


# --- Happy path ---

def test_valid_pdb_1ubq():
    result = validate_pdb(TEST_PDBS_DIR / "1UBQ.pdb", chains=["A"])
    assert result is not None


def test_valid_pdb_returns_structure():
    result = validate_pdb(TEST_PDBS_DIR / "1UBQ.pdb", chains=["A"])
    assert isinstance(result, Structure)


# --- File-level failures ---

def test_file_not_found():
    with pytest.raises(PDBValidationError, match="not found"):
        validate_pdb(Path("/nonexistent/file.pdb"), chains=["A"])


def test_file_too_large(tmp_path):
    big_file = tmp_path / "big.pdb"
    big_file.write_bytes(b"x" * (11 * 1024 * 1024))
    with pytest.raises(PDBValidationError, match="exceeds"):
        validate_pdb(big_file, chains=["A"], max_size_mb=10)


def test_empty_file(tmp_path):
    empty = tmp_path / "empty.pdb"
    empty.write_text("")
    with pytest.raises(PDBValidationError, match="no ATOM records"):
        validate_pdb(empty, chains=["A"])


def test_no_atom_records(tmp_path):
    f = tmp_path / "header_only.pdb"
    f.write_text("HEADER    TEST\nREMARK nothing here\nEND\n")
    with pytest.raises(PDBValidationError, match="no ATOM records"):
        validate_pdb(f, chains=["A"])


# --- Parse failures ---

def test_malformed_atom_records(tmp_path):
    f = tmp_path / "garbled.pdb"
    f.write_text(
        "ATOM      1  N   ALA A   1     "
        "XXXXX YYYYY ZZZZZ  1.00  0.00           N\nEND\n"
    )
    with pytest.raises(PDBValidationError):
        validate_pdb(f, chains=["A"])


# --- Chain validation ---

def test_chain_not_found():
    with pytest.raises(PDBValidationError, match="Chain.*Z.*not found"):
        validate_pdb(TEST_PDBS_DIR / "1UBQ.pdb", chains=["Z"])


def test_chain_not_found_shows_available():
    with pytest.raises(PDBValidationError, match="Available chains.*A"):
        validate_pdb(TEST_PDBS_DIR / "1UBQ.pdb", chains=["B"])


def test_partial_chain_mismatch():
    with pytest.raises(PDBValidationError, match="not found"):
        validate_pdb(TEST_PDBS_DIR / "1UBQ.pdb", chains=["A", "X"])


# --- Backbone / CA validation ---

def test_too_few_ca_atoms(tmp_path):
    lines = []
    for i in range(1, 4):
        lines.append(
            f"ATOM  {i:5d}  CA  ALA A{i:4d}    "
            f"{float(i):8.3f}{float(i):8.3f}{float(i):8.3f}"
            f"  1.00  0.00           C  "
        )
    lines.append("END")
    f = tmp_path / "tiny.pdb"
    f.write_text("\n".join(lines) + "\n")
    with pytest.raises(PDBValidationError, match="CA atoms"):
        validate_pdb(f, chains=["A"])


def test_custom_size_limit():
    with pytest.raises(PDBValidationError, match="exceeds"):
        validate_pdb(TEST_PDBS_DIR / "1UBQ.pdb", chains=["A"], max_size_mb=0.001)
