import asyncio
from event.event import subscribe
from executor.files_functions import (
    upload_to_s3, handle_lambda_layer_zip,
    handle_create_requirements, insert_packages_into_zip,
    update_lambda_zip, update_lambda_layer_zip, handle_create_cf, build_react)
from executor.zip_funtions import handle_lambda_zip


async def subscribe_lambda_preper():
    asyncio.gather(
        subscribe('handle_lambda_zip', handle_lambda_zip),
        subscribe('handle_create_requirements', handle_create_requirements),
        subscribe('handle_lambda_layer_zip', handle_lambda_layer_zip),
        subscribe('insert_packages_into_zip', insert_packages_into_zip),
        subscribe('build_react', build_react),
    )


async def subscribe_aws_function():
    asyncio.gather(
        subscribe('upload_to_s3', upload_to_s3),
        subscribe('update_lambda_zip', update_lambda_zip),
        subscribe('update_lambda_layer_zip', update_lambda_layer_zip),
        subscribe('handle_create_cf', handle_create_cf),
    )
