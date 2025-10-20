
from typing import AsyncIterable

from dishka import Provider, Scope, provide

from configs import Settings
from infra.httpx.jsonplaceholder import JSONPlaceholderClient


class HttpClientsProvider(Provider):
    @provide(scope=Scope.APP)
    async def jsonplaceholder(self, settings: Settings) -> AsyncIterable[JSONPlaceholderClient]:
        client = JSONPlaceholderClient(base_url=settings.JSONPLACEHOLDER_BASE_URL)
        try:
            yield client
        finally:
            await client.close()


