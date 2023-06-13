import uuid
import boto3
import aioboto3
from fastapi import UploadFile, Request
from starlette.concurrency import run_in_threadpool
from streaming_form_data.targets import S3Target

from config import ACCESS_KEY_ID, SECRET_ACCESS_KEY, BUCKET_NAME

from streaming_form_data import StreamingFormDataParser

conf = {
    "service_name": 's3',
    "endpoint_url": "https://storage.yandexcloud.net",
    "aws_secret_access_key": SECRET_ACCESS_KEY,
    "aws_access_key_id": ACCESS_KEY_ID
}


async def upload_image(file: UploadFile) -> str:
    key = get_key(file.filename, "images/")
    async with aioboto3.Session().client(**conf) as s3:
        await s3.upload_fileobj(file, BUCKET_NAME, key)
        return get_url_to_obj(key)


def get_url_to_obj(key: str) -> str:
    return f" {conf['endpoint_url']}/{BUCKET_NAME}/{key}"


def get_key(filename, directory="") -> str:
    return f"{directory}{uuid.uuid4()}_{filename}"


async def upload_video(request: Request, filename: str) -> str:
    key = get_key(filename, "videos/")
    parser = StreamingFormDataParser(headers=request.headers)
    parser.register("file", S3Target(f"s3://{BUCKET_NAME}/{key}", "wb", {"client": boto3.Session().client(**conf)}))

    async for chunk in request.stream():
        await run_in_threadpool(parser.data_received, chunk)
    return get_url_to_obj(key)
