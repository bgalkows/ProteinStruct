""" Scratch script for checking out PDBs"""
from Bio.PDB import PDBParser

structure = PDBParser(QUIET=True).get_structure("test", "test_pdbs/1UBQ.pdb")

for model in structure:
    print(f"Model {model.get_id()}")
    for chain in model:
        residues = [r for r in chain if r.get_id()[0] == ' ']  # Skip this strange thing HETAM
        print(f"  Chain {chain.get_id()}: {len(residues)} residues")
        if residues:
            seq = "".join([r.get_resname() for r in residues[:5]])
            print(f"    First 5: {seq}")