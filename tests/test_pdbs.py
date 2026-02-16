from app.validation.pdb import count_hetatm, validate_pdb
from app.config import TEST_PDBS_DIR

from Bio.PDB.Structure import Structure


def _count_residues(structure: Structure, chain_id: str) -> int:
    chain = structure[0][chain_id]
    return len([r for r in chain if r.get_id()[0] == " "])


# --- 1UBQ: baseline single-chain monomer ---

def test_1ubq_validates():
    result = validate_pdb(TEST_PDBS_DIR / "1UBQ.pdb", ["A"])
    assert isinstance(result, Structure)
    assert _count_residues(result, "A") == 76


# --- 6MRR: incomplete structure, fewer residues than expected ---

def test_6mrr_incomplete():
    result = validate_pdb(TEST_PDBS_DIR / "6MRR.pdb", ["A"])
    assert isinstance(result, Structure)
    assert _count_residues(result, "A") == 68


# --- 1A3N: multi-chain, multi-model hemoglobin ---

def test_1a3n_multi_chain():
    result = validate_pdb(TEST_PDBS_DIR / "1A3N.pdb", ["A"])
    assert isinstance(result, Structure)
    n_res = _count_residues(result, "A")
    assert n_res == 141


# --- 2LZM: has HETATM records (ligands/water) ---

def test_2lzm_validates():
    result = validate_pdb(TEST_PDBS_DIR / "2LZM.pdb", ["A"])
    assert isinstance(result, Structure)
    assert _count_residues(result, "A") == 164


def test_2lzm_has_hetatm():
    hetatm_count = count_hetatm(str(TEST_PDBS_DIR / "2LZM.pdb"))
    assert hetatm_count > 0
