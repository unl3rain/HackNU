import os
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings
from typing import Optional

_s3_client = None

def _get_s3_client():
    global _s3_client
    if _s3_client is not None:
        return _s3_client
    try:
        import boto3  # type: ignore
    except Exception as e:
        raise RuntimeError("boto3 is required for S3 storage but not installed") from e
    _s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    return _s3_client


def ensure_upload_dir() -> None:
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


async def save_upload(file: UploadFile, filename: str | None = None) -> str:
    name = filename or file.filename or "file"
    content = await file.read()

    if (settings.STORAGE_PROVIDER or "local").lower() == "s3":
        if not settings.AWS_S3_BUCKET:
            raise RuntimeError("AWS_S3_BUCKET is not configured")
        key = name
        s3 = _get_s3_client()
        base_stem = Path(name).stem
        suffix = Path(name).suffix
        attempt = 0
        final_key = key
        while True:
            try:
                s3.head_object(Bucket=settings.AWS_S3_BUCKET, Key=final_key)
                attempt += 1
                final_key = f"{base_stem}_{attempt}{suffix}"
            except Exception:
                break
        s3.put_object(Bucket=settings.AWS_S3_BUCKET, Key=final_key, Body=content, ContentType=file.content_type or "application/octet-stream")
        return f"s3://{settings.AWS_S3_BUCKET}/{final_key}"

    ensure_upload_dir()
    dest = Path(settings.UPLOAD_DIR) / name
    i = 1
    stem = dest.stem
    suffix = dest.suffix
    while dest.exists():
        dest = Path(settings.UPLOAD_DIR) / f"{stem}_{i}{suffix}"
        i += 1
    Path(dest).write_bytes(content)
    return str(dest)
