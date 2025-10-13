from fastapi import FastAPI, APIRouter

from di.container import setup_di


def create_app() -> FastAPI:
    app = FastAPI()
    setup_di(app)

    from apps.users.views.router import router as users_router

    api_v1 = APIRouter(prefix="/api/v1")
    api_v1.include_router(users_router)
    app.include_router(api_v1)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
