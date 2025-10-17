from __future__ import annotations

from typing import AsyncIterable

from dishka import Provider, Scope, provide

from configs import Settings
from infra.storage.client import StorageClient


class StorageProvider(Provider):
    @provide(scope=Scope.APP)
    async def storage(self, settings: Settings) -> AsyncIterable[StorageClient]:
        required = [
            settings.S3_ENDPOINT_URL,
            settings.S3_ACCESS_KEY,
            settings.S3_SECRET_KEY,
            settings.S3_BUCKET,
        ]
        if not all(required):
            raise RuntimeError("S3 storage is required but not fully configured")

        client = StorageClient(
            endpoint_url=settings.S3_ENDPOINT_URL,
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            region=settings.S3_REGION,
            use_ssl=bool(settings.S3_SECURE),
            use_path_style=bool(settings.S3_USE_PATH_STYLE),
            bucket=settings.S3_BUCKET,
        )
        try:
            yield client
        finally:
            await client.close()


