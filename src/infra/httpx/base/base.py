from __future__ import annotations
import asyncio
import logging
import httpx
from typing import Any, Dict, Optional

from infra.httpx import ApiNetworkError, ApiHTTPError
from infra.logging import get_trace_id


class BaseApiClient:
    """Simple httpx client with retries and protection against a dead client."""

    timeout = httpx.Timeout(10.0, read=10.0)
    max_retries = 3
    retry_initial_delay = 0.5
    retry_max_delay = 4.0

    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        self._logger = logging.getLogger(self.__class__.__name__)

    async def close(self) -> None:
        await self.client.aclose()

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
                self._logger.info(
                    "HTTP %s %s", method, url,
                    extra={"trace": trace_id}
                )
                resp = await client.request(
                    method, url, params=params, json=json, headers=req_headers
                )
                self._logger.info(
                    "HTTP %s %s -> %s", method, url, resp.status_code,
                    extra={"trace": trace_id}
                )
                resp.raise_for_status()
                if "application/json" in resp.headers.get("Content-Type", ""):
                    return resp.json()
                return resp.text

            except httpx.RequestError as exc:
                if attempt == self.max_retries:
                    raise ApiNetworkError(str(exc)) from exc
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if not (500 <= status < 600) or attempt == self.max_retries:
                    raise ApiHTTPError(status, exc.response.text, exc.response)
            finally:
                if attempt == self.max_retries and client is not self.client:
                    await client.aclose()

            await asyncio.sleep(delay)
            delay = min(delay * 2, self.retry_max_delay)



