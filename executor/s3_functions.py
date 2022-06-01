import os
import mimetypes
import pathlib
from pathlib import Path
from pprint import pprint

import boto3
from event.event_logger import event_logger

from executor.s3_config import S3Config
from moto import mock_s3


@event_logger
def s3_upload_file(s3, bucket_name, from_path, key, acl):
    s3.Object(bucket_name, key).put(Body=open(from_path, 'rb'),
                                    ACL=acl, ContentType=(mimetypes.guess_type(from_path)[0] or 'octet-stream/application'))


# @ mock_s3
@event_logger
def upload_to_s3(s3_config: S3Config):

    # s3 = boto3.client('s3', region_name='us-east-1')
    s3 = boto3.resource('s3')
    bucket_name = s3_config.bucket_name
    from_path = s3_config.from_path
    file_or_folder = s3_config.file_or_folder
    key = s3_config.key
    acl = s3_config.acl

    # TODO is only in test
    # s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={
    #     'LocationConstraint': 'eu-east-1'})

    if file_or_folder == 'file':
        s3_upload_file(s3, bucket_name, from_path, key, acl)

    elif file_or_folder == 'folder':
        for root, _, files in os.walk(from_path):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, from_path)
                full_key = os.path.join(key, relative_path)
                full_key = Path(full_key)
                full_key = full_key.as_posix()

                s3_upload_file(s3=s3, bucket_name=bucket_name, from_path=full_path,
                               key=full_key, acl=acl)
    # TODO is only in test
    # res = s3.list_objects_v2(Bucket=bucket_name)
    # pprint(res)
