## Overview

FastAPI application template with a clean configuration system, DI setup, and ready-to-use
local stack via Docker. Configuration relies on Pydantic settings that merge secrets
and environment variables automatically.

## Features

- FastAPI app factory with health endpoint
- DI integration (Dishka)
- Pydantic-based settings (secrets dir > env > defaults)
- Settings exposed via `configs.settings` or DI
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

print(settings.app_name)
```
