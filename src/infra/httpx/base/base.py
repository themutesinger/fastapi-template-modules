from __future__ import annotations
import asyncio
import logging
import httpx
from typing import Any, Dict, Optional, Iterable

from infra.httpx.base.exceptions import ApiNetworkError, ApiHTTPError
from infra.security.redaction import Redactor, RedactionLevel
from infra.logging import get_trace_id


class BaseApiClient:
    """Simple httpx client with retries and protection against a dead client."""

    timeout = httpx.Timeout(10.0, read=10.0)
    max_retries = 3
    retry_initial_delay = 0.5
    retry_max_delay = 4.0
    # Body logging controls
    log_bodies_debug: bool = False            # log request/response bodies on DEBUG
    log_error_bodies: bool = True             # log error response bodies on HTTP errors
    body_max_bytes: int = 4096                # truncate large bodies
    redact_keys: Iterable[str] = (
        "password", "token", "authorization", "access_token", "refresh_token", "secret", "api_key"
    )

    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        self._logger = logging.getLogger(self.__class__.__name__)

    async def close(self) -> None:
        await self.client.aclose()

    def _redact_dict(self, data: Any) -> Any:
        if isinstance(data, dict):
            redacted: Dict[str, Any] = {}
            for k, v in data.items():
                if isinstance(k, str) and k.lower() in self.redact_keys:
                    redacted[k] = "***"
                else:
                    redacted[k] = self._redact_dict(v)
            return redacted
        if isinstance(data, list):
            return [self._redact_dict(v) for v in data]
        return data

    def _shorten(self, text: str) -> str:
        limit = max(0, int(self.body_max_bytes))
        if limit and len(text.encode("utf-8", errors="ignore")) > limit:
            # naive truncation by characters; acceptable for logging
            return text[: limit] + "… (truncated)"
        return text

    def _should_log_body(self, content_type: str | None) -> bool:
        if not content_type:
            return False
        ct = content_type.lower()
        return ct.startswith("application/json") or ct.startswith("text/")

    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}{endpoint}"
        req_headers = {**self.headers, **(headers or {})}
        # propagate trace id into outbound request
        trace_id = get_trace_id()
        req_headers.setdefault("X-Request-ID", trace_id)
        delay = self.retry_initial_delay

        for attempt in range(1, self.max_retries + 1):
            client = self.client
            if attempt == self.max_retries:
                client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

            try:
                self._logger.info("HTTP %s %s", method, url, extra={"trace": trace_id})
                if self.log_bodies_debug and self._logger.isEnabledFor(logging.DEBUG) and json is not None:
                    try:
                        redacted = Redactor.redact(json, level=RedactionLevel.INTERNAL, extra_deny=self.redact_keys)
                        self._logger.debug("HTTP %s %s body -> %s", method, url, redacted, extra={"trace": trace_id})
                    except Exception:
                        # best-effort logging only
                        pass
                resp = await client.request(
                    method, url, params=params, json=json, headers=req_headers
                )
                self._logger.info("HTTP %s %s -> %s", method, url, resp.status_code, extra={"trace": trace_id})
                resp.raise_for_status()
                content_type = resp.headers.get("Content-Type", "")
                if self.log_bodies_debug and self._logger.isEnabledFor(logging.DEBUG) and self._should_log_body(content_type):
                    try:
                        body_text = resp.text
                        self._logger.debug(
                            "HTTP %s %s response body <- %s",
                            method,
                            url,
                            Redactor.shorten(body_text, self.body_max_bytes),
                            extra={"trace": trace_id},
                        )
                    except Exception:
                        pass
                if "application/json" in content_type:
                    return resp.json()
                return resp.text

            except httpx.RequestError as exc:
                if attempt == self.max_retries:
                    raise ApiNetworkError(str(exc)) from exc
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if self.log_error_bodies and self._should_log_body(exc.response.headers.get("Content-Type", "")):
                    try:
                        body_text = exc.response.text
                        self._logger.error(
                            "HTTP %s %s error %s body <- %s",
                            method,
                            url,
                            status,
                            Redactor.shorten(body_text, self.body_max_bytes),
                            extra={"trace": trace_id},
                        )
                    except Exception:
                        pass
                if not (500 <= status < 600) or attempt == self.max_retries:
                    raise ApiHTTPError(status, exc.response.text, exc.response)
            finally:
                if attempt == self.max_retries and client is not self.client:
                    await client.aclose()

            await asyncio.sleep(delay)
            delay = min(delay * 2, self.retry_max_delay)



