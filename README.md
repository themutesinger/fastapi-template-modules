## Overview

FastAPI application template with a clean configuration system, DI setup, and ready-to-use
local stack via Docker. The configuration layer uses a repository chain to merge OS
environment and a secrets directory for secure deployments.

## Features

- FastAPI app factory with health endpoint
- DI integration (Dishka)
- Config repository chain (env > secrets)
- Typed config helpers and project settings
- Docker Compose for local services (Postgres, Redis, MinIO, PgBouncer)

## Quick Start

Run locally:

```bash
uvicorn src.main:app --reload --port 8000
```

Run via Docker:

```bash
docker compose up --build
```

Health check: http://127.0.0.1:8000/health

## Documentation

- Docs Index: `docs/README.md`
- Configuration: `docs/configuration.md`
- Development: `docs/development.md`
- Project Structure: `docs/project-structure.md`

Preferred usage pattern for settings:

```python
from configs import settings

print(settings.APP_NAME)
```
