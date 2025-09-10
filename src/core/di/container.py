from __future__ import annotations

from dishka import Container, make_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI


def build_container() -> Container:
    container = make_container()
    return container


def setup_di(app: FastAPI) -> Container:
    container = build_container()
    setup_dishka(container, app)  # type: ignore[arg-type]
    return container
