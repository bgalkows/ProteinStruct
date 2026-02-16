"""Parse ProteinMPNN FASTA output."""

from pathlib import Path


def parse_fasta(fasta_path: Path) -> list[str]:
    """Extract designed sequences from a ProteinMPNN FASTA file.

    The first entry is the native sequence (skipped).
    Subsequent entries are designed sequences.
    """
    sequences: list[str] = []
    current_seq_lines: list[str] = []
    entry_index = -1

    with open(fasta_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if current_seq_lines and entry_index > 0:
                    sequences.append("".join(current_seq_lines))
                current_seq_lines = []
                entry_index += 1
            else:
                current_seq_lines.append(line)

    if current_seq_lines and entry_index > 0:
        sequences.append("".join(current_seq_lines))

    return sequences
