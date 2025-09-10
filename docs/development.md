# Development

## Quick Start

1) Install dependencies (with a tool of your choice):

```bash
uv sync  # or: pip install -e .[dev]
```

2) Run the app (reload for local dev):

```bash
uvicorn src.main:app --reload --port 8000
```

3) Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Docker

Bring up the stack:

```bash
docker compose up --build
```

Ports:
- API: `8001 -> 8000` (container)
- Postgres: `5440 -> 5432`
- Redis: `6380 -> 6379`
- MinIO API/Console: `9002/9003`

## Lint and Tests

```bash
ruff check src
black --check src
mypy src
pytest -q
```

## Configuration in Dev

- Use OS env or a secrets folder. By default, secrets are read from `/run/secrets/`.
- Override secrets path: `export SECRETS_PATH=$(pwd)/.secrets`
- Create a secret: `echo "value" > .secrets/db_password`

See `docs/configuration.md:1` for details.

