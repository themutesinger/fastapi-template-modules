from __future__ import annotations

from fastapi import status

from infra.errors import BaseError


class UserAlreadyExistsError(BaseError):
    code = "unique"
    message_key = "conflict"
    detail_key = "user_exists"


class UserNotFoundError(BaseError):
    code = "not_found"
    message_key = "resource_not_found"
    detail_key = "not_found"


