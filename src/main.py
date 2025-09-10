from fastapi import FastAPI
from di import setup_di


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI Template")

    setup_di(app)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()


