from __future__ import annotations

from fastapi import FastAPI
from dishka import Container
from dishka.integrations.fastapi import setup_dishka


def build_container() -> Container:
    container = Container()
    return container


def setup_di(app: FastAPI) -> Container:
    """Build and attach DI container to FastAPI via Dishka integration."""
    container = build_container()
    setup_dishka(app, container)
    return container

