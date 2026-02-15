#!/usr/bin/env python3
"""Download ProteinMPNN weights."""
import urllib.request
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import (
    MODEL_WEIGHTS_DIR,
    MODEL_WEIGHTS_FILE,
    MODEL_WEIGHTS_URL,
    MODEL_WEIGHTS_EXPECTED_SIZE,
)


def download() -> None:
    MODEL_WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)

    if MODEL_WEIGHTS_FILE.exists():
        actual = MODEL_WEIGHTS_FILE.stat().st_size
        if actual == MODEL_WEIGHTS_EXPECTED_SIZE:
            print(f"Model already exists: {MODEL_WEIGHTS_FILE}")
            return
        print(f"Corrupt weights ({actual} bytes, expected {MODEL_WEIGHTS_EXPECTED_SIZE}). Re-downloading.")
        MODEL_WEIGHTS_FILE.unlink()

    print(f"Downloading {MODEL_WEIGHTS_URL}...")
    print(f"Target: {MODEL_WEIGHTS_FILE}")

    urllib.request.urlretrieve(MODEL_WEIGHTS_URL, MODEL_WEIGHTS_FILE)

    actual = MODEL_WEIGHTS_FILE.stat().st_size
    if actual != MODEL_WEIGHTS_EXPECTED_SIZE:
        MODEL_WEIGHTS_FILE.unlink()
        raise RuntimeError(
            f"Download failed: got {actual} bytes, expected {MODEL_WEIGHTS_EXPECTED_SIZE}"
        )

    size_mb = actual / (1024 * 1024)  # bytes to megabytes
    print(f"Downloaded: {size_mb:.1f} MB")


if __name__ == "__main__":
    download()