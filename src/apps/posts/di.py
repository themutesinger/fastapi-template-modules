from __future__ import annotations

from dishka import Provider, Scope, provide

from infra.httpx.jsonplaceholder import JSONPlaceholderClient
from .service import ListPostsUseCase, GetPostUseCase, CreatePostUseCase, UpdatePostUseCase, DeletePostUseCase


class PostsProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def list_posts_usecase(self, client: JSONPlaceholderClient) -> ListPostsUseCase:
        return ListPostsUseCase(client)

    @provide(scope=Scope.REQUEST)
    def get_post_usecase(self, client: JSONPlaceholderClient) -> GetPostUseCase:
        return GetPostUseCase(client)

    @provide(scope=Scope.REQUEST)
    def create_post_usecase(self, client: JSONPlaceholderClient) -> CreatePostUseCase:
        return CreatePostUseCase(client)

    @provide(scope=Scope.REQUEST)
    def update_post_usecase(self, client: JSONPlaceholderClient) -> UpdatePostUseCase:
        return UpdatePostUseCase(client)

    @provide(scope=Scope.REQUEST)
    def delete_post_usecase(self, client: JSONPlaceholderClient) -> DeletePostUseCase:
        return DeletePostUseCase(client)


di = PostsProvider()


