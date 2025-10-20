
from infra.errors import BaseError


class UserAlreadyExistsError(BaseError):
    code = "unique"
    message_key = "conflict"
    detail_key = "user_exists"
    status_code = 409


class UserNotFoundError(BaseError):
    code = "not_found"
    message_key = "resource_not_found"
    detail_key = "not_found"
    status_code = 404

