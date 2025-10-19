from __future__ import annotations

from enum import Enum
from typing import Any, Iterable


class RedactionLevel(Enum):
    STRICT = "strict"      # external systems: Sentry, logs shipped outside
    INTERNAL = "internal"  # internal app logs
    OFF = "off"            # local debugging only


class Redactor:
    DEFAULT_DENYLIST = {
        "password", "passwd", "authorization", "authorization_header",
        "token", "access_token", "refresh_token",
        "api_key", "apikey", "secret", "secret_key",
        "credentials",
    }

    @classmethod
    def redact(cls, data: Any, *, level: RedactionLevel = RedactionLevel.INTERNAL, extra_deny: Iterable[str] | None = None) -> Any:
        deny = set(map(str.lower, (extra_deny or []))) | set(map(str.lower, cls.DEFAULT_DENYLIST))

        def _mask(value: Any) -> Any:
            if isinstance(value, dict):
                out: dict[str, Any] = {}
                for k, v in value.items():
                    key = str(k).lower()
                    if key in deny:
                        out[k] = "***"
                    else:
                        out[k] = _mask(v)
                return out
            if isinstance(value, list):
                return [_mask(v) for v in value]
            if isinstance(value, tuple):
                return tuple(_mask(v) for v in value)
            # Partial masking examples: emails in STRICT
            if level is RedactionLevel.STRICT and isinstance(value, str) and "@" in value:
                try:
                    name, domain = value.split("@", 1)
                    return (name[:1] + "***@" + domain) if name else ("***@" + domain)
                except Exception:
                    return value
            return value

        return _mask(data)

    @staticmethod
    def shorten(text: str, limit: int = 4096) -> str:
        try:
            enc = text.encode("utf-8", errors="ignore")
            if len(enc) > limit:
                return enc[:limit].decode("utf-8", errors="ignore") + "… (truncated)"
            return text
        except Exception:
            return text[:256] + "…"


