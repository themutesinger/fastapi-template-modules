from fastapi import FastAPI

from core.di import setup_di
from configs.settings import APP_NAME


def create_app() -> FastAPI:
    app = FastAPI(title=APP_NAME)

    setup_di(app)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
