"""Storing hard-coded vals and paths"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
APP_DIR = Path(__file__).parent
TEST_PDBS_DIR = PROJECT_ROOT / "test_pdbs"

# Runtime defaults
DEFAULT_NUM_SEQUENCES = 5
MAX_SEQUENCES = 10
MAX_PDB_SIZE_MB = 10
REQUEST_TIMEOUT_SECONDS = 120