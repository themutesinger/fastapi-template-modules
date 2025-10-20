
from fastapi import FastAPI

from presentations.api.build_app import build_app


def create_app(container=None) -> FastAPI:
    return build_app(container=container)


app = create_app()
