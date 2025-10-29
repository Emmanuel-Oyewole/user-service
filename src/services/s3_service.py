
import aioboto3
import mimetypes
from uuid import uuid4
from typing import Optional, Union, Any
from fastapi import UploadFile
from botocore.exceptions import ClientError

from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class S3Service:
    def __init__(self):
        self.bucket = settings.AWS_S3_BUCKET
        self.region = settings.AWS_REGION
        self.aws_key = settings.AWS_ACCESS_KEY_ID
        self.aws_secret = settings.AWS_SECRET_ACCESS_KEY

    async def upload_file(
        self,
        file: Union[UploadFile, bytes, bytearray, Any],
        key: Optional[str] = None,
    ) -> Optional[str]:
        """
        Simple async upload using aioboto3.
        - file: FastAPI UploadFile, bytes, or an object with async read().
        - key: optional S3 object key; generated if missing.
        Returns URL on success, None on failure.
        """

        filename = None
        content_type = None
        data: bytes

        if isinstance(file, UploadFile):
            filename = file.filename
            content_type = file.content_type or mimetypes.guess_type(filename or "")[0] or "application/octet-stream"
            data = await file.read()

        elif isinstance(file, (bytes, bytearray)):
            data = bytes(file)
            content_type = "application/octet-stream"

        else:
            read = getattr(file, "read", None)
            if read is None:
                raise TypeError("file must be UploadFile, bytes, or have a read() method")
            try:
                data = await read()
            except TypeError:
                import asyncio
                loop = asyncio.get_running_loop()
                data = await loop.run_in_executor(None, read)
            filename = getattr(file, "filename", None) or getattr(file, "name", None)
            content_type = getattr(file, "content_type", None) or mimetypes.guess_type(filename or "")[0] or "application/octet-stream"

        object_key = key or (f"{uuid4().hex}-{filename}" if filename else uuid4().hex)

        session = aioboto3.Session()
        extra_args = {"ContentType": content_type}
        try:
            async with session.client(
                "s3",
                region_name=self.region,
                aws_access_key_id=self.aws_key,
                aws_secret_access_key=self.aws_secret,
            ) as client:
                await client.put_object(Bucket=self.bucket, Key=object_key, Body=data, **extra_args)
                url = f"https://{self.bucket}.s3.amazonaws.com/{object_key}"
            logger.info("Uploaded %s to %s", object_key, self.bucket)
            return url

        except ClientError as err:
            logger.error("S3 upload failed for %s: %s", object_key, err)
            return None
        except Exception as exc:
            logger.exception("Unexpected error uploading to S3 for %s: %s", object_key, exc)
            return None
