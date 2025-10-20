
from typing import Any, Dict, List

from infra.httpx.jsonplaceholder import JSONPlaceholderClient
from infra.i18n import translate


class ListPostsUseCase:
    def __init__(self, client: JSONPlaceholderClient) -> None:
        self._client = client

    async def execute(self) -> List[Dict[str, Any]]:
        return await self._client.list_posts()


class GetPostUseCase:
    def __init__(self, client: JSONPlaceholderClient) -> None:
        self._client = client

    async def execute(self, post_id: int) -> Dict[str, Any]:
        return await self._client.get_post(post_id)


class CreatePostUseCase:
    def __init__(self, client: JSONPlaceholderClient) -> None:
        self._client = client

    async def execute(self, *, title: str, body: str, user_id: int) -> Dict[str, Any]:
        return await self._client.create_post(title=title, body=body, user_id=user_id)


class UpdatePostUseCase:
    def __init__(self, client: JSONPlaceholderClient) -> None:
        self._client = client

    async def execute(self, post_id: int, *, title: str, body: str, user_id: int) -> Dict[str, Any]:
        return await self._client.update_post(post_id, title=title, body=body, user_id=user_id)


class DeletePostUseCase:
    def __init__(self, client: JSONPlaceholderClient) -> None:
        self._client = client

    async def execute(self, post_id: int) -> None:
        await self._client.delete_post(post_id)


class TriggerErrorUseCase:
    async def execute(self) -> None:
        # Reuse an existing domain error to test i18n error responses
        from apps.users.exceptions import UserAlreadyExistsError

        raise UserAlreadyExistsError()


class LocalizedMessageUseCase:
    async def execute(self) -> dict:
        # Return a regular localized message using an existing key
        return {"message": translate("resource_not_found")}
