
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

import aioboto3
from aioboto3.resources.base import AIOBoto3ServiceResource
from aioboto3.session import ResourceCreatorContext
from botocore.config import Config
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


class StorageClient:
    """Thin async wrapper around an S3-compatible bucket (e.g. MinIO)."""

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
        connect_timeout: float | None = None,
        read_timeout: float | None = None,
    ) -> None:
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.use_ssl = use_ssl
        self.use_path_style = use_path_style
        self.bucket = bucket
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self._resource_cm: ResourceCreatorContext | None = None
        self._resource: AIOBoto3ServiceResource | None = None

    def _build_config(self) -> Config:
        addressing = "path" if self.use_path_style else "auto"
        kwargs: dict[str, float] = {}
        if self.connect_timeout is not None:
            kwargs["connect_timeout"] = self.connect_timeout
        if self.read_timeout is not None:
            kwargs["read_timeout"] = self.read_timeout
        return Config(s3={"addressing_style": addressing}, retries={"max_attempts": 3}, **kwargs)

    def _create_resource_cm(self) -> ResourceCreatorContext:
        session = aioboto3.Session()
        return session.resource(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            use_ssl=self.use_ssl,
            config=self._build_config(),
        )

    async def _get_resource(self) -> AIOBoto3ServiceResource:
        """Lazily acquire a shared aioboto3 resource for the configured bucket."""
        if self._resource is None:
            self._resource_cm = self._create_resource_cm()
            self._resource = await self._resource_cm.__aenter__()
        return self._resource

    @asynccontextmanager
    async def get_resource(self) -> AsyncIterator[AIOBoto3ServiceResource]:
        """Provide a one-off resource context that closes reliably."""
        resource_cm = self._create_resource_cm()
        resource = await resource_cm.__aenter__()
        try:
            yield resource
        finally:
            await resource_cm.__aexit__(None, None, None)

    async def close(self) -> None:
        if self._resource_cm is not None:
            await self._resource_cm.__aexit__(None, None, None)
            self._resource_cm = None
            self._resource = None

    async def exists(self, key: str) -> bool:
        s3 = await self._get_resource()
        obj = s3.Object(self.bucket, key)
        try:
            await obj.load()
            return True
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code")
            if error_code in {"404", "NoSuchKey", "NotFound"}:
                return False
            logger.debug("Unexpected error checking key %s in bucket %s: %s", key, self.bucket, exc, exc_info=True)
            raise

    async def put_bytes(self, key: str, data: bytes, content_type: str | None = None) -> None:
        s3 = await self._get_resource()
        obj = s3.Object(self.bucket, key)
        args = {"Body": data}
        if content_type:
            args["ContentType"] = content_type
        await obj.put(**args)

    async def upload_file(self, key: str, file_path: str | Path, content_type: str | None = None) -> None:
        s3 = await self._get_resource()
        bucket = s3.Bucket(self.bucket)
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type
        await bucket.upload_file(str(file_path), key, ExtraArgs=extra_args or None)

    async def get_bytes(self, key: str) -> bytes:
        s3 = await self._get_resource()
        obj = s3.Object(self.bucket, key)
        result = await obj.get()
        body = await result["Body"].read()
        return body

    async def list_keys(self, prefix: str = "") -> list[str]:
        s3 = await self._get_resource()
        bucket = s3.Bucket(self.bucket)
        keys: list[str] = []
        async for obj in bucket.objects.filter(Prefix=prefix):
            keys.append(obj.key)
        return keys

    async def delete(self, key: str) -> None:
        s3 = await self._get_resource()
        obj = s3.Object(self.bucket, key)
        await obj.delete()

    async def bucket_exists(self) -> bool:
        """Return True when the configured bucket is reachable."""
        session = aioboto3.Session()
        async with session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            use_ssl=self.use_ssl,
            config=self._build_config(),
        ) as client:
            try:
                await client.head_bucket(Bucket=self.bucket)
                return True
            except ClientError as exc:
                error_code = exc.response.get("Error", {}).get("Code")
                if error_code in {"404", "NoSuchBucket"}:
                    return False
                logger.debug("Unexpected error checking bucket %s: %s", self.bucket, exc, exc_info=True)
                raise
