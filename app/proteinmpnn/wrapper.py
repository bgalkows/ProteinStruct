"""Subprocess wrapper for ProteinMPNN sequence design."""

import subprocess
import sys
import tempfile
from pathlib import Path

from app.config import MODEL_WEIGHTS_DIR, PROTEINMPNN_REPO
from app.proteinmpnn.parser import parse_fasta

MPNN_SCRIPT = PROTEINMPNN_REPO / "protein_mpnn_run.py"


def design_sequences(
    pdb_path: str,
    chains: list[str],
    num_sequences: int = 3,
    sampling_temp: float = 0.1,
) -> list[str]:
    """Run ProteinMPNN on a PDB file and return designed sequences.

    Args:
        pdb_path: Path to the input PDB file.
        chains: Chain IDs to redesign (e.g. ["A"]).
        num_sequences: Number of sequences to generate.
        sampling_temp: Sampling temperature.

    Returns:
        List of designed amino acid sequences.

    Raises:
        FileNotFoundError: If PDB or ProteinMPNN script is missing.
        RuntimeError: If ProteinMPNN subprocess fails.
    """
    pdb = Path(pdb_path).resolve()
    if not pdb.exists():
        raise FileNotFoundError(f"PDB file not found: {pdb}")
    if not MPNN_SCRIPT.exists():
        raise FileNotFoundError(
            f"ProteinMPNN not found at {MPNN_SCRIPT}. "
            "Clone it: git clone https://github.com/dauparas/ProteinMPNN vendor/ProteinMPNN"
        )

    with tempfile.TemporaryDirectory(prefix="mpnn_") as tmpdir:
        out_dir = Path(tmpdir)

        cmd = [
            sys.executable,
            str(MPNN_SCRIPT),
            "--pdb_path", str(pdb),
            "--pdb_path_chains", " ".join(chains),
            "--out_folder", str(out_dir),
            "--num_seq_per_target", str(num_sequences),
            "--sampling_temp", str(sampling_temp),
            "--path_to_model_weights", str(MODEL_WEIGHTS_DIR),
            "--seed", "42",
            "--batch_size", "1",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(PROTEINMPNN_REPO),
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"ProteinMPNN failed (exit {result.returncode}):\n{result.stderr}"
            )

        pdb_stem = pdb.stem
        fasta_path = out_dir / "seqs" / f"{pdb_stem}.fa"
        if not fasta_path.exists():
            seqs_dir = out_dir / "seqs"
            available = list(seqs_dir.glob("*.fa")) if seqs_dir.exists() else []
            raise RuntimeError(
                f"Expected FASTA at {fasta_path} but not found. "
                f"Available: {available}\nstdout: {result.stdout}"
            )

        return parse_fasta(fasta_path)