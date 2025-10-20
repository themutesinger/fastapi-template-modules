from __future__ import annotations

import asyncio
import logging
from contextlib import AsyncExitStack
from typing import Any, Dict, Optional

import httpx

from infra.httpx.base.exceptions import ApiHTTPError, ApiNetworkError, build_http_error

logger = logging.getLogger(__name__)


class BaseApiClient:
    """Minimal httpx wrapper with retries and optional body logging."""

    timeout = httpx.Timeout(10.0, read=10.0)
    max_retries = 3
    retry_initial_delay = 0.5
    retry_max_delay = 4.0

    log_bodies_debug: bool = False
    log_error_bodies: bool = True
    body_max_bytes: int = 4096

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        *,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.client = client or httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    async def close(self) -> None:
        await self.client.aclose()

    def _shorten(self, text: str) -> str:
        limit = max(0, int(self.body_max_bytes))
        if limit and len(text.encode("utf-8", errors="ignore")) > limit:
            return text[:limit] + "… (truncated)"
        return text

    def _should_log_body(self, content_type: Optional[str]) -> bool:
        if not content_type:
            return False
        ct = content_type.lower()
        return ct.startswith(("application/json", "text/"))

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
        delay = self.retry_initial_delay

        for attempt in range(1, self.max_retries + 1):
            async with AsyncExitStack() as stack:
                client = self._client_for_attempt(attempt, stack)

                try:
                    self._log_request(method, url, json)
                    response = await client.request(
                        method,
                        url,
                        params=params,
                        json=json,
                        headers=req_headers,
                    )
                    self._log_response(method, url, response)

                    response.raise_for_status()
                    return self._extract_payload(response)

                except httpx.RequestError as exc:
                    if attempt == self.max_retries:
                        raise ApiNetworkError(str(exc)) from exc
                except httpx.HTTPStatusError as exc:
                    self._log_error_response(method, url, exc)
                    status = exc.response.status_code
                    error = build_http_error(status, exc.response.text, exc.response)
                    if not (500 <= status < 600) or attempt == self.max_retries:
                        raise error

            await asyncio.sleep(delay)
            delay = min(delay * 2, self.retry_max_delay)

    def _client_for_attempt(self, attempt: int, stack: AsyncExitStack) -> httpx.AsyncClient:
        """
        Return the httpx client to use for a retry attempt.

        NOTE: On the final retry we create a fresh AsyncClient to avoid issues with a "dead"
        connection pool (e.g., half-open sockets, DNS glitches, or persistent keep-alive failures).
        The new client is registered with the exit stack so it is always closed.
        """
        if attempt < self.max_retries:
            return self.client
        client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        stack.push_async_callback(client.aclose)
        return client

    def _log_request(self, method: str, url: str, payload: Optional[Dict[str, Any]]) -> None:
        logger.info("HTTP %s %s", method, url)
        if self.log_bodies_debug and logger.isEnabledFor(logging.DEBUG) and payload is not None:
            logger.debug("HTTP %s %s body -> %s", method, url, payload)

    def _log_response(self, method: str, url: str, response: httpx.Response) -> None:
        logger.info("HTTP %s %s -> %s", method, url, response.status_code)
        content_type = response.headers.get("Content-Type", "")
        if self.log_bodies_debug and logger.isEnabledFor(logging.DEBUG) and self._should_log_body(content_type):
            logger.debug(
                "HTTP %s %s response body <- %s",
                method,
                url,
                self._shorten(response.text),
            )

    def _log_error_response(self, method: str, url: str, exc: httpx.HTTPStatusError) -> None:
        response = exc.response
        status = response.status_code
        if self.log_error_bodies and self._should_log_body(response.headers.get("Content-Type", "")):
            logger.error(
                "HTTP %s %s error %s body <- %s",
                method,
                url,
                status,
                self._shorten(response.text),
            )

    def _extract_payload(self, response: httpx.Response) -> Any:
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return response.json()
        return response.text
