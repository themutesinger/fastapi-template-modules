FROM python:3.12-slim-bookworm AS builder

RUN pip install --no-cache-dir uv --user

COPY pyproject.toml uv.lock* ./

ENV UV_PROJECT_ENVIRONMENT=/usr/local
RUN /root/.local/bin/uv sync --no-dev --no-install-project --no-install-workspace --no-cache

FROM python:3.12-slim-bookworm AS runtime

ENV \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin

# App source and Alembic configuration
COPY src ./src
# Alembic configuration inside src/infra/db
COPY alembic.ini ./
COPY src/infra/db/alembic ./src/infra/db/alembic

# Ensure app files are writable by the non-root user (needed for Alembic revisions)
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Runtime-only extras
RUN pip install --no-cache-dir psycopg2-binary

# Optional: preinstall dev deps when tests profile is used (kept lightweight here)
# To speed up tests service, uncomment next line to bake pytest into the image
# RUN pip install --no-cache-dir pytest pytest-asyncio

CMD ["uvicorn", "presentations.api.app:app", "--host", "0.0.0.0", "--port", "8000"]


