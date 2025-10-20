
from dishka import Provider, Scope, provide

from infra.security import PasswordHasher


class SecurityProvider(Provider):
    @provide(scope=Scope.APP)
    def password_hasher(self) -> PasswordHasher:
        return PasswordHasher()

