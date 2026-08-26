import hashlib
from collections.abc import AsyncIterator

import aioboto3
from botocore.exceptions import ClientError

from app.config import Settings, get_settings

# S3 multipart parts must be >= 5 MiB each, except the last one.
PART_SIZE = 5 * 1024 * 1024


class StorageService:
    """Chunked, async, streaming access to the object store (MinIO/S3).

    Bytes are never fully buffered in memory: uploads are read chunk by
    chunk from the incoming request and pushed to storage as S3 multipart
    parts as soon as enough has accumulated; downloads are streamed back the
    same way. The content hash is computed incrementally as chunks pass
    through, so no separate full-file read is needed to get it.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _client(self):
        session = aioboto3.Session()
        return session.client(
            "s3",
            endpoint_url=self._settings.minio_endpoint,
            aws_access_key_id=self._settings.minio_access_key,
            aws_secret_access_key=self._settings.minio_secret_key,
        )

    async def ensure_bucket(self) -> None:
        async with self._client() as client:
            try:
                await client.head_bucket(Bucket=self._settings.minio_bucket)
            except ClientError:
                await client.create_bucket(Bucket=self._settings.minio_bucket)

    async def upload_stream(self, key: str, chunks: AsyncIterator[bytes]) -> tuple[int, str]:
        """Uploads an async byte stream under `key`. Returns (size_bytes, sha256_hex)."""
        hasher = hashlib.sha256()
        total_size = 0
        parts: list[dict] = []
        buffer = bytearray()

        async with self._client() as client:
            multipart = await client.create_multipart_upload(Bucket=self._settings.minio_bucket, Key=key)
            upload_id = multipart["UploadId"]

            try:

                async def flush_part() -> None:
                    part_number = len(parts) + 1
                    result = await client.upload_part(
                        Bucket=self._settings.minio_bucket,
                        Key=key,
                        PartNumber=part_number,
                        UploadId=upload_id,
                        Body=bytes(buffer),
                    )
                    parts.append({"PartNumber": part_number, "ETag": result["ETag"]})
                    buffer.clear()

                async for chunk in chunks:
                    hasher.update(chunk)
                    total_size += len(chunk)
                    buffer.extend(chunk)
                    if len(buffer) >= PART_SIZE:
                        await flush_part()

                # The last part has no minimum size, but multipart upload
                # requires at least one part even for an empty file.
                if buffer or not parts:
                    await flush_part()

                await client.complete_multipart_upload(
                    Bucket=self._settings.minio_bucket,
                    Key=key,
                    UploadId=upload_id,
                    MultipartUpload={"Parts": parts},
                )
            except Exception:
                await client.abort_multipart_upload(
                    Bucket=self._settings.minio_bucket, Key=key, UploadId=upload_id
                )
                raise

        return total_size, hasher.hexdigest()

    async def download_stream(self, key: str, chunk_size: int = PART_SIZE) -> AsyncIterator[bytes]:
        async with self._client() as client:
            response = await client.get_object(Bucket=self._settings.minio_bucket, Key=key)
            async for chunk in response["Body"].iter_chunks(chunk_size):
                yield chunk

    async def delete(self, key: str) -> None:
        async with self._client() as client:
            await client.delete_object(Bucket=self._settings.minio_bucket, Key=key)

    async def delete_many(self, keys: list[str]) -> None:
        if not keys:
            return
        async with self._client() as client:
            await client.delete_objects(
                Bucket=self._settings.minio_bucket,
                Delete={"Objects": [{"Key": key} for key in keys]},
            )


def get_storage_service() -> StorageService:
    return StorageService(get_settings())
