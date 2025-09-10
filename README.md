## Configuration

This template uses `decouplet` to read environment variables and Docker/K8s secrets from a directory.

Basic usage in code:
```python
from config import env, get_bool

DATABASE_URL = env("DATABASE_URL", default="postgresql+asyncpg://user:pass@localhost:5432/app")
DEBUG = get_bool("DEBUG", default=False)
```

Secrets directory:
- By default, `/run/secrets/` is scanned; override with `SECRETS_PATH=/path/to/secrets`.
- A file named `db_password` becomes available as `env("DB_PASSWORD")`.


