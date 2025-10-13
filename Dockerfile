FROM python:3.12-slim-bookworm AS builder

RUN pip install --no-cache-dir uv --user

COPY pyproject.toml uv.lock* ./

ENV UV_PROJECT_ENVIRONMENT=/usr/local
RUN if [ -f uv.lock ]; then \
      /root/.local/bin/uv sync --frozen --no-dev --no-install-project --no-install-workspace --no-cache; \
    else \
      /root/.local/bin/uv sync --no-dev --no-install-project --no-install-workspace --no-cache; \
    fi

FROM python:3.12-slim-bookworm AS runtime

ENV \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin

# App source and Alembic configuration
COPY src ./
# Alembic configuration inside src/infra/db
COPY alembic.ini ./
COPY src/infra/db/alembic ./src/infra/db/alembic

# Ensure app files are writable by the non-root user (needed for Alembic revisions)
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

RUN pip install --no-cache-dir psycopg2-binary

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


