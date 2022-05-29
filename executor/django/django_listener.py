import re
import os
from pprint import pprint
from pathlib import Path
import subprocess
from subprocess import check_output
import shutil

import boto3
from moto import mock_s3

from executor.s3.s3_config import S3Config


def lambda_perper_zip(django_project_path):
    abs_current_path = os.getcwd()
    os.chdir(django_project_path)
    subprocess.run([
        'rm',
        f'{abs_current_path}/generated_files/store-lambda.zip'])
    subprocess.run([
        'zip',
        '-r',
        f'{abs_current_path}./generated_files/store-lambda.zip',
        '.',
        '-x',
        './__pycache__/*',
        '-x',
        './.pytest_cache/*',
        '-x',
        './.vscode/*',
        '-x',
        './.git/*',
        '-x',
        './node_modules/*',
        '-x',
        './static/*',
        '-x',
        './htmlcov/*'])

    os.chdir(abs_current_path)


def update_lambda_zip():
    subprocess.run(
        ['aws', 'lambda', 'update-function-code', '--region', 'us-east-1', '--function-name',
         'websites-store-lambda', '--s3-bucket', 'websites-yohai', '--s3-key', 'store/django/store-lambda.zip']
    )


def update_lambda_layer_zip():
    subprocess.run(
        ['aws', 'lambda', 'update-function-configuration', '--region', 'us-east-1', '--function-name',
         'websites-store-lambda', '--layers', 'arn:aws:lambda:eu-central-1:634832404426:layer:store-lambda-layer:1']
    )


def handle_lambda_layer_zip(lambda_layer_zip_path, generated_files):
    subprocess.run(['rm', f'{lambda_layer_zip_path}'])
    subprocess.run(['docker', 'rm', 'deps-wrap'])
    subprocess.run(['docker', 'build', '-t', 'deps', generated_files])
    subprocess.run(['docker', 'run', '--name', 'deps-wrap', 'deps', ])
    subprocess.run(
        ['docker', 'cp', 'deps-wrap:app/store-lambda-layer.zip', f'{generated_files}'])


def handle_create_requirements(django_project_path, generated_files):
    pip_path = (Path(django_project_path).parent /
                'env2' / 'Scripts' / 'pip.exe')
    freeze_raw = check_output(
        [pip_path, 'freeze'], shell=True, universal_newlines=True)
    freeze_raw = re.sub('(boto.+|django-tenants.+|psycopg2.+)', '', freeze_raw)
    freeze_raw = freeze_raw.split('\n')

    with open(f'{generated_files}/requirements.txt', 'w') as f:
        f.write('\n'.join(sorted(freeze_raw)))


def insert_packages_into_zip(django_project_path, generated_files):
    pip_path = (Path(django_project_path).parent /
                'env2' / 'Scripts' / 'pip.exe')

    abs_current_path = os.getcwd()
    os.chdir(Path(django_project_path).parent.parent /
             'utils' / 'django-tenants')
    subprocess.run([
        pip_path,
        'install',
        '.',
        '-t',
        f'{abs_current_path}./generated_files/python/lib/python3.9/site-packages/',
        '--no-deps'])

    os.chdir(f'{abs_current_path}/generated_files')

    subprocess.run(
        ['zip', '-r', f'{abs_current_path}/generated_files/store-lambda-layer.zip', f'./python/lib/python3.9/site-packages/', ])
    os.chdir(abs_current_path)


def s3_upload_file(s3, bucket_name, from_path, key, acl):
    s3.upload_file(str(from_path), bucket_name, key, ExtraArgs={
        'ACL': acl,
    })


@ mock_s3
def upload_to_s3(s3_config: S3Config):
    s3 = boto3.client('s3')
    bucket_name = s3_config.bucket_name
    from_path = s3_config.from_path
    file_or_folder = s3_config.file_or_folder
    key = s3_config.key
    acl = s3_config.acl

    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={
        'LocationConstraint': 'eu-east-1'})

    if file_or_folder == 'file':
        s3_upload_file(s3, bucket_name, from_path, key, acl)

    elif file_or_folder == 'folder':
        for root, _, files in os.walk(from_path):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, from_path)
                s3_upload_file(s3=s3, bucket_name=bucket_name, from_path=full_path,
                               key=os.path.join(key, relative_path), acl=acl)

    res = s3.list_objects_v2(Bucket=bucket_name)
    pprint(res)
