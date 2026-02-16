"""Parse ProteinMPNN FASTA output."""

from pathlib import Path
from typing import NamedTuple


class ParsedFasta(NamedTuple):
    native_sequence: str
    designed_sequences: list[str]


def parse_fasta(fasta_path: Path) -> ParsedFasta:
    """Extract native and designed sequences from a ProteinMPNN FASTA file.

    The first entry is the native sequence.
    Subsequent entries are designed sequences.
    """
    native_sequence: str = ""
    designed: list[str] = []
    current_seq_lines: list[str] = []
    entry_index = -1

    with open(fasta_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if current_seq_lines:
                    seq = "".join(current_seq_lines)
                    if entry_index == 0:
                        native_sequence = seq
                    else:
                        designed.append(seq)
                current_seq_lines = []
                entry_index += 1
            else:
                current_seq_lines.append(line)

    if current_seq_lines:
        seq = "".join(current_seq_lines)
        if entry_index == 0:
            native_sequence = seq
        else:
            designed.append(seq)

    return ParsedFasta(native_sequence=native_sequence, designed_sequences=designed)
