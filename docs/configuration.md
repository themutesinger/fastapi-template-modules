# Configuration

This project resolves configuration from multiple sources using a repository chain:

- Priority: OS environment > secrets directory (`SECRETS_PATH`)
- Default secrets path: `/run/secrets/` (override via `SECRETS_PATH`)

See implementation in `src/configs/env.py:1` and repositories in `src/configs/repository.py:1`.

## Usage

Typed helpers are provided for convenience:

```python
from configs import env, get_bool, get_int, get_float, get_list

DATABASE_URL = env("DATABASE_URL", default="postgresql+asyncpg://user:pass@localhost:5432/app")
DEBUG = get_bool("DEBUG", default=False)
PORT = get_int("PORT", default=8000)
RATE = get_float("RATE", default=1.0)
ALLOWED_HOSTS = get_list("ALLOWED_HOSTS", default=["localhost"])  # comma-separated
```

Or import predefined settings:

```python
from configs.settings import APP_NAME, DEBUG, PORT, CORS_ORIGINS
```

## Secrets Directory

- Place files under the secrets directory (default `/run/secrets/`).
- A file `db_password` becomes available as `env("DB_PASSWORD")`.
- OS env wins: `export DB_PASSWORD=...` overrides the secret file.

Change secrets path at runtime:

```bash
export SECRETS_PATH=/path/to/secrets
```

## Boolean and List Parsing

- Booleans accept: `1/0`, `true/false`, `yes/no`, `y/n`, `on/off` (case-insensitive).
- Lists split by `,` and trim whitespace; empty items are ignored.

## Adding Project Settings

Put project-level constants in `src/configs/settings.py:1` and re-export in `src/configs/__init__.py:1` as needed.

