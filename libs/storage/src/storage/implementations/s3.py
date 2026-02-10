"""Amazon S3 storage implementation."""
import os
from datetime import datetime, timezone
from typing import BinaryIO

from storage.interfaces.base import FileMetadata, StorageBackend

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None  # type: ignore
    ClientError = Exception  # type: ignore


class S3StorageBackend(StorageBackend):
    """Store files in Amazon S3."""

    def __init__(
        self,
        bucket: str,
        region: str | None = None,
        prefix: str = "",
    ) -> None:
        if boto3 is None:
            raise RuntimeError("boto3 is required for S3 storage. Install with: pip install boto3")
        self.bucket = bucket
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.prefix = prefix.strip("/")
        self._client = boto3.client("s3", region_name=self.region)

    def _key(self, key: str) -> str:
        if self.prefix:
            return f"{self.prefix}/{key}"
        return key

    def upload(
        self,
        file_obj: BinaryIO,
        *,
        key: str,
        content_type: str,
        original_filename: str,
    ) -> FileMetadata:
        s3_key = self._key(key)
        data = file_obj.read()
        self._client.put_object(
            Bucket=self.bucket,
            Key=s3_key,
            Body=data,
            ContentType=content_type,
        )
        return FileMetadata(
            storage_key=key,
            original_filename=original_filename,
            size=len(data),
            content_type=content_type,
            uploaded_at=datetime.now(timezone.utc).isoformat(),
        )

    def download(self, key: str) -> bytes:
        s3_key = self._key(key)
        try:
            resp = self._client.get_object(Bucket=self.bucket, Key=s3_key)
            return resp["Body"].read()
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "NoSuchKey":
                raise FileNotFoundError(key) from e
            raise

    def delete(self, key: str) -> None:
        s3_key = self._key(key)
        self._client.delete_object(Bucket=self.bucket, Key=s3_key)

    def get_metadata(self, key: str) -> FileMetadata | None:
        s3_key = self._key(key)
        try:
            resp = self._client.head_object(Bucket=self.bucket, Key=s3_key)
            return FileMetadata(
                storage_key=key,
                original_filename=key.split("/")[-1],
                size=resp["ContentLength"],
                content_type=resp.get("ContentType", "application/octet-stream"),
                uploaded_at=resp["LastModified"].isoformat(),
            )
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "404":
                return None
            raise

    def get_url(self, key: str) -> str:
        s3_key = self._key(key)
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": s3_key},
            ExpiresIn=3600,
        )
