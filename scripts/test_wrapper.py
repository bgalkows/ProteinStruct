"""Standalone test: call ProteinMPNN wrapper outside FastAPI."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.proteinmpnn.wrapper import design_sequences


def main():
    pdb_path = str(project_root / "test_pdbs" / "6MRR.pdb")
    chains = ["A"]
    num_sequences = 3

    print(f"Input: {pdb_path}")
    print(f"Chains: {chains}")
    print(f"Num sequences: {num_sequences}")
    print("-" * 60)

    sequences = design_sequences(pdb_path, chains, num_sequences)

    print(f"Got {len(sequences)} designed sequences:\n")
    for i, seq in enumerate(sequences, 1):
        print(f"  Seq {i} ({len(seq)} aa): {seq[:80]}...")
        print()

    assert len(sequences) == num_sequences, (
        f"Expected {num_sequences} sequences, got {len(sequences)}"
    )
    print("PASS")


if __name__ == "__main__":
    main()
