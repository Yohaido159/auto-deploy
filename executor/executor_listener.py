import asyncio

from executor.files_functions import (
    handle_create_requirements,
    insert_packages_into_zip,
    exclude_packages_from_zip,
    build_react
)
from executor.zip_funtions import (
    handle_lambda_zip,
    handle_lambda_layer_zip
)
from executor.lambda_functions import (
    update_lambda_zip,
    update_lambda_layer_zip,
)
from executor.s3_functions import (upload_to_s3)
from executor.cf_functions import (handle_create_cf)

from event.event import subscribe


async def subscribe_lambda_preper():
    asyncio.gather(
        subscribe('handle_lambda_zip', handle_lambda_zip),
        subscribe('handle_create_requirements', handle_create_requirements),
        subscribe('handle_lambda_layer_zip', handle_lambda_layer_zip),
        subscribe('insert_packages_into_zip', insert_packages_into_zip),
        subscribe('exclude_packages_from_zip', exclude_packages_from_zip),
        subscribe('build_react', build_react),
    )


async def subscribe_aws_function():
    asyncio.gather(
        subscribe('upload_to_s3', upload_to_s3),
        subscribe('update_lambda_zip', update_lambda_zip),
        subscribe('update_lambda_layer_zip', update_lambda_layer_zip),
        subscribe('handle_create_cf', handle_create_cf),
    )
