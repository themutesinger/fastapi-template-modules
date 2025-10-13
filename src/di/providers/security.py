from __future__ import annotations

import hashlib
import hmac
import os
from typing import Protocol


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str:  # pragma: no cover - protocol
        ...

    def verify(self, password: str, password_hash: str) -> bool:  # pragma: no cover - protocol
        ...


class PBKDF2PasswordHasher:
    """Lightweight password hasher using PBKDF2-HMAC-SHA256.

    Note: For production-grade security prefer using passlib[bcrypt] or argon2.
    """

    def __init__(self, secret_salt: str, iterations: int = 390000) -> None:
        self.secret_salt = secret_salt.encode("utf-8")
        self.iterations = iterations

    def hash(self, password: str) -> str:
        salt = os.urandom(16)
        dk = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt + self.secret_salt, self.iterations
        )
        return f"pbkdf2_sha256${self.iterations}${salt.hex()}${dk.hex()}"

    def verify(self, password: str, password_hash: str) -> bool:
        try:
            _, iters_str, salt_hex, digest_hex = password_hash.split("$")
            iterations = int(iters_str)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(digest_hex)
        except Exception:
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt + self.secret_salt, iterations
        )
        return hmac.compare_digest(actual, expected)


