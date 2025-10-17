from __future__ import annotations

import logging
from typing import Optional

import aioboto3
from botocore.config import Config


logger = logging.getLogger(__name__)


class StorageClient:
    def __init__(
        self,
        *,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        region: str | None,
        use_ssl: bool,
        use_path_style: bool,
        bucket: str,
    ) -> None:
        self._endpoint_url = endpoint_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._region = region
        self._use_ssl = use_ssl
        self._use_path_style = use_path_style
        self._bucket = bucket
        self._session: Optional[aioboto3.Session] = None
        self._resource = None

    async def _get_resource(self):
        if self._resource is None:
            session = aioboto3.Session()
            config = Config(s3={"addressing_style": "path" if self._use_path_style else "auto"}, retries={"max_attempts": 3})
            self._resource = await session.resource(
                "s3",
                endpoint_url=self._endpoint_url,
                aws_access_key_id=self._access_key,
                aws_secret_access_key=self._secret_key,
                region_name=self._region,
                use_ssl=self._use_ssl,
                config=config,
            ).__aenter__()
        return self._resource

    async def close(self) -> None:
        if self._resource is not None:
            await self._resource.__aexit__(None, None, None)
            self._resource = None

    async def exists(self, key: str) -> bool:
        s3 = await self._get_resource()
        obj = await s3.Object(self._bucket, key)
        try:
            await obj.load()
            return True
        except Exception:
            return False

    async def put_bytes(self, key: str, data: bytes, content_type: str | None = None) -> None:
        s3 = await self._get_resource()
        args = {"Body": data}
        if content_type:
            args["ContentType"] = content_type
        await s3.Object(self._bucket, key).put(**args)

    async def get_bytes(self, key: str) -> bytes:
        s3 = await self._get_resource()
        obj = await s3.Object(self._bucket, key).get()
        body = await obj["Body"].read()
        return body

    async def delete(self, key: str) -> None:
        s3 = await self._get_resource()
        await s3.Object(self._bucket, key).delete()


