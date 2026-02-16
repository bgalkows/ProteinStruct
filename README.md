# ProteinMPNN Mini-Service

Web app for protein sequence design using [ProteinMPNN](https://github.com/dauparas/ProteinMPNN). Upload a PDB structure, pick chains, and get back designed sequences with mutations highlighted.

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green) ![Docker](https://img.shields.io/badge/docker-compose-blue)

## Quickstart

**Prerequisites:** Python 3, Docker, and Docker Compose.

```bash
# 1. Clone ProteinMPNN into vendor/ (not tracked in git)
### (git submodule)
git clone https://github.com/dauparas/ProteinMPNN vendor/ProteinMPNN

# 2. Download model weights (~6.4 MB, one-time, no pip install needed)
python3 scripts/download_weights.py

# 3. Start the service
docker compose up --build
```

Open `http://localhost:8000` in a browser. The service refuses to start if weights are missing. If `/design` returns a 500 error, the `vendor/ProteinMPNN` clone is likely missing.

## Usage

1. Drop a `.pdb` file onto the upload zone (or click to browse)
2. Enter chain IDs (e.g. `A` or `A, B`) and number of sequences (1-10)
3. Click **Design** and wait ~30-60s for CPU inference
4. Results show the native sequence and each design with mutations in red

## Architecture

```
app/
  main.py              FastAPI app, routes, static file mount
  schemas.py           Pydantic request/response models
  dependencies.py      Upload handling, param parsing
  config.py            Paths and constants
  proteinmpnn/
    wrapper.py         Runs ProteinMPNN as a subprocess
    parser.py          Parses FASTA output (native + designed sequences)
  validation/
    pdb.py             PDB structure validation (BioPython)
  static/
    index.html         Single-page UI (vanilla HTML/JS)
tests/                 pytest suite
scripts/               Weight download, debug utilities
test_pdbs/             Sample PDB files (1UBQ, 1A3N, 2LZM, 6MRR)
vendor/ProteinMPNN/    Vendored ProteinMPNN repo
```

## API

| Endpoint  | Method | Description                                |
|-----------|--------|--------------------------------------------|
| `/`       | GET    | Web UI                                     |
| `/health` | GET    | Liveness probe (`{"status": "ok", ...}`)   |
| `/design` | POST   | Run sequence design (multipart form data)  |
| `/docs`   | GET    | Interactive Swagger docs                   |

### POST /design

**Request** (multipart/form-data):
- `pdb_file` — PDB file upload
- `chains` — JSON array of chain IDs, e.g. `["A"]`
- `num_sequences` — integer, 1-10 (default 5)

**Response:**
```json
{
  "status": "success",
  "metadata": {
    "num_residues": 76,
    "chains": ["A"],
    "num_sequences": 5
  },
  "native_sequence": "MQIFVKTL...",
  "sequences": ["MQIFVKTL...", "..."]
}
```

**Errors:** 400 (bad PDB or params), 504 (timeout), 500 (internal).

## Development

```bash
# Run tests
pytest tests/

# Lint
ruff check .
```

## Constraints

- CPU-only inference (no GPU required is a plus!)
- Stateless — no database, no sessions
- Single-page vanilla HTML/JS frontend


## Followup Plans

If I circle back to the project, I'm excited about adding:

#### 1) Async worker queue with progress indicators
Long PDB job submissions with this only-CPU inference are going to really drag, and users of the app would have no visibility into what's going on.
To tackle this we could have background workers (coordinated with a combo like Redis + RedisQueue or Celery) that are polled for job status.

#### 2) More helpful validation & response confidences
Scientist users would appreciate feedback on the quality of their submission and the confidence the model has in its returned output.
We could pretty easily surface warnings for clashes in input sequences of incomplete residues above a certain percentage, and then work in
reporting the confidence ProteinMNPP has in the different returned regions of each sequence.

#### 3) Batch jobs
In a real world setting the value add of this app would be multified many times over with bulk batch jobs.
Scientists would likely submit massive amounts of PDBs and expect to return in some time for batched progress on them.
To enable this, we'd revisit the single subprocess decision and probably spread model invocations over many parallel processes in a batch.