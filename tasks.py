from __future__ import annotations

import subprocess
import os
from pathlib import Path

from invoke import task

PROJECT_ROOT = Path(__file__).resolve().parent
# Honour external runner, e.g. PYTHON="uv run python"
PYTHON = os.environ.get("PYTHON", "python3")
# Ensure application sources are importable by scripts (infra.*, apps.*, etc.)
BASE_ENV = {
    **os.environ,
    "PYTHONPATH": f"{PROJECT_ROOT / 'src'}" + (
        os.pathsep + os.environ.get("PYTHONPATH", "") if os.environ.get("PYTHONPATH") else ""
    ),
}


@task(name="i18n_register")
def i18n_register(c):
    """Collect BaseError localization keys into locales/.i18n_keys.json"""
    subprocess.run([*PYTHON.split(), "scripts/i18n_register.py"], check=True, cwd=PROJECT_ROOT, env=BASE_ENV)


@task(name="i18n_refresh")
def i18n_refresh(c):
    """Refresh Babel catalogs using registered keys."""
    i18n_register(c)
    subprocess.run([*PYTHON.split(), "scripts/gen_i18n_stubs.py"], check=True, cwd=PROJECT_ROOT, env=BASE_ENV)
    # Use project-local locales inside src/infra/i18n/locales
    locales_dir = str(PROJECT_ROOT / "src/infra/i18n/locales")
    subprocess.run([
        "pybabel",
        "extract",
        "-F",
        "babel.cfg",
        "-o",
        f"{locales_dir}/messages.pot",
        ".",
    ], check=True, cwd=PROJECT_ROOT, env=BASE_ENV)
    subprocess.run([
        "pybabel",
        "update",
        "-i",
        f"{locales_dir}/messages.pot",
        "-d",
        locales_dir,
    ], check=True, cwd=PROJECT_ROOT, env=BASE_ENV)
    subprocess.run(["pybabel", "compile", "-d", locales_dir], check=True, cwd=PROJECT_ROOT, env=BASE_ENV)


@task(name="i18n_verify")
def i18n_verify(c):
    """Fail if any .po entries are missing translations."""
    subprocess.run([*PYTHON.split(), "scripts/i18n_verify.py"], check=True, cwd=PROJECT_ROOT, env=BASE_ENV)
