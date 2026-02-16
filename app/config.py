"""Storing hard-coded vals and paths"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
APP_DIR = Path(__file__).parent
TEST_PDBS_DIR = PROJECT_ROOT / "test_pdbs"

PROTEINMPNN_DIR = APP_DIR / "proteinmpnn"
PROTEINMPNN_REPO = PROJECT_ROOT / "vendor" / "ProteinMPNN"
MODEL_WEIGHTS_DIR = PROTEINMPNN_DIR / "vanilla_model_weights"
MODEL_WEIGHTS_FILE = MODEL_WEIGHTS_DIR / "v_48_020.pt"
MODEL_WEIGHTS_URL = "https://huggingface.co/spaces/simonduerr/ProteinMPNN/resolve/main/ProteinMPNN/vanilla_model_weights/v_48_020.pt"
MODEL_WEIGHTS_EXPECTED_SIZE = 6681301

# Runtime defaults
DEFAULT_NUM_SEQUENCES = 5
MAX_SEQUENCES = 10
MAX_PDB_SIZE_MB = 10
REQUEST_TIMEOUT_SECONDS = 120