# Project Structure

High-level layout and key modules.

## Directories

- `src/` — application source code
  - `src/main.py:1` — FastAPI app factory and routes
  - `src/configs/` — configuration system
    - `src/configs/env.py:1` — typed accessors and repository chain
    - `src/configs/settings.py:1` — project-level settings
    - `src/configs/repository.py:1` — repositories (env, secrets, composite)
  - `src/core/di/` — dependency injection wiring (Dishka)

- `docs/` — documentation
  - `docs/README.md:1` — docs index
  - `docs/configuration.md:1` — config, secrets, helpers
  - `docs/development.md:1` — local dev, lint, tests, docker

## Key Technologies

- FastAPI for the web framework
- Dishka for DI
- decouplet-style config with repository chain (env + secrets)

