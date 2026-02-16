"""Integration tests for the POST /design endpoint"""

import json
import subprocess
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.config import TEST_PDBS_DIR
from app.main import app

client = TestClient(app)

UBQ_PATH = TEST_PDBS_DIR / "1UBQ.pdb"


def _post_design(pdb_path, chains=None, num_sequences=3):
    """Helper to POST /design with a real PDB file."""
    with open(pdb_path, "rb") as f:
        return client.post(
            "/design",
            files={"pdb_file": ("test.pdb", f, "chemical/x-pdb")},
            data={
                "chains": json.dumps(chains or ["A"]),
                "num_sequences": str(num_sequences),
            },
        )


class TestDesignEndpoint:
    """Tests for POST /design using mocked ProteinMPNN."""

    @patch("app.main.design_sequences")
    def test_success(self, mock_design):
        mock_design.return_value = ["AAAA", "BBBB", "CCCC"]
        resp = _post_design(UBQ_PATH, chains=["A"], num_sequences=3)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["metadata"]["chains"] == ["A"]
        assert data["metadata"]["num_sequences"] == 3
        assert data["metadata"]["num_residues"] == 76
        assert len(data["sequences"]) == 3

    @patch("app.main.design_sequences")
    def test_multichain(self, mock_design):
        mock_design.return_value = ["SEQ1"]
        pdb_path = TEST_PDBS_DIR / "1A3N.pdb"
        resp = _post_design(pdb_path, chains=["A", "B"], num_sequences=1)
        assert resp.status_code == 200
        data = resp.json()
        assert set(data["metadata"]["chains"]) == {"A", "B"}

    def test_invalid_chains_json(self):
        with open(UBQ_PATH, "rb") as f:
            resp = client.post(
                "/design",
                files={"pdb_file": ("test.pdb", f, "chemical/x-pdb")},
                data={"chains": "not-json", "num_sequences": "3"},
            )
        assert resp.status_code == 400

    def test_chain_not_in_pdb(self):
        resp = _post_design(UBQ_PATH, chains=["Z"])
        assert resp.status_code == 400
        assert "not found" in resp.json()["detail"]

    def test_num_sequences_exceeds_max(self):
        resp = _post_design(UBQ_PATH, num_sequences=999)
        assert resp.status_code == 400

    @patch(
        "app.main.design_sequences",
        side_effect=subprocess.TimeoutExpired(cmd="mpnn", timeout=300),
    )
    def test_timeout_returns_504(self, mock_design):
        resp = _post_design(UBQ_PATH)
        assert resp.status_code == 504

    @patch(
        "app.main.design_sequences",
        side_effect=RuntimeError("model crashed"),
    )
    def test_model_error_returns_500(self, mock_design):
        resp = _post_design(UBQ_PATH)
        assert resp.status_code == 500
        assert resp.json()["detail"] == "Internal server error"