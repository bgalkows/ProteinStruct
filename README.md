# ProteinMPNN Mini-Service

Lightweight web app for protein sequence design using vanilla ProteinMPNN.

## Setup

### 0. Environment

The repo assumes an installation of Docker and Docker Compose.

### 1. Download model weights

Weights are not included in the repo. Download them before starting the service:

```bash
python scripts/download_weights.py
```

This places `v_48_020.pt` (~6.4 MB) into `app/proteinmpnn/vanilla_model_weights/`.
The script is idempotent and validates file size on download.

### 2. Run with Docker

```bash
docker compose up --build
```

The app starts at `http://localhost:8000`. The existing bind-mount in
`docker-compose.yml` maps `./app` into the container, so downloaded weights
are available automatically.

The service will **refuse to start** if weights are missing.

### 3. Run tests

```bash
pytest tests/
```

### 4. Lint

```bash
ruff check .
```

## API

| Endpoint       | Method | Description                     |
|----------------|--------|---------------------------------|
| `/health`      | GET    | Liveness probe + model status   |
| `/design`      | POST   | Run ProteinMPNN sequence design |
| `/docs`        | GET    | Interactive API docs (Swagger)  |
