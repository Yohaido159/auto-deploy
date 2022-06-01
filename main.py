from pathlib import Path
from executor.executor_listener import subscribe_lambda_preper, subscribe_aws_function
from executor.s3_config import S3Config
from config.config import ConfigLoaderJson
import asyncio
#
from event.event import post_event

CONFIG_PATH = "./config_files/config.json"


async def main():

    config = ConfigLoaderJson(CONFIG_PATH).load_config()

    django_project_path = config.django_project_path
    bucket_name = config.bucket_name
    lambda_zip_path = config.lambda_zip_path
    lambda_layer_zip_path = config.lambda_layer_zip_path
    pip_path = config.pip_path
    generated_files = config.generated_files
    react_path = config.react_path
    utils_path = config.utils_path

    project_name = config.project_name

    await asyncio.gather(
        subscribe_lambda_preper(),
        subscribe_aws_function(),
    )

    upload_lambda_zip = S3Config(
        bucket_name=bucket_name,
        from_path=Path(lambda_zip_path),
        key=project_name + f"/django/{project_name}-lambda.zip",
        file_or_folder='file',
        acl="private"
    )
    upload_lambda_layer_zip = S3Config(
        bucket_name=bucket_name,
        from_path=Path(lambda_layer_zip_path),
        key=project_name +
        f"/layers/{project_name}-lambda-layer.zip",
        file_or_folder='file',
        acl="private"
    )
    upload_react_folder = S3Config(
        bucket_name=bucket_name,
        from_path=Path(generated_files) / 'react',
        key=project_name + "/react",
        file_or_folder='folder',
        acl="public-read"
    )
    # upload_react_admin_models_folder = S3Config(
    #     bucket_name=bucket_name,
    #     from_path=Path(generated_files) / 'admin-models',
    #     key=project_name + "/admin-models",
    #     file_or_folder='folder',
    #     acl="public-read"
    # )

    # post_event('handle_lambda_zip',
    #            django_project_path,
    #            lambda_zip_path)
    # post_event('upload_to_s3',
    #            upload_lambda_zip)
    # post_event('handle_create_requirements',
    #            pip_path, generated_files)
    # post_event('handle_lambda_layer_zip',
    #            lambda_layer_zip_path,
    #            generated_files,
    #            project_name)
    # # post_event('insert_packages_into_zip',
    # #            pip_path,
    # #            utils_path,
    # #            generated_files,
    # #            project_name)
    # TODO
    # # post_event('exclude_packages_from_zip',
    # #            pip_path,
    # #            utils_path,
    # #            generated_files,
    # #            project_name)
    # post_event('upload_to_s3',
    #            upload_lambda_layer_zip)
    # post_event('handle_create_cf',
    #            'lambda',
    #            project_name)
    # TODO deploy the api to template

    # post_event('update_lambda_zip',
    #            project_name)

    # post_event('update_lambda_layer_zip',
    #            project_name)

    # post_event('build_react',
    #            react_path, 'react')
    # post_event('upload_to_s3',
    #            upload_react_folder)
    # post_event('build_react',
    #            Path(utils_path) / 'admin-models',
    #            'admin-models')
    #    TODO
    # post_event('invalidate_cloudfront',
    #            upload_react_folder)
    # post_event('upload_to_s3',
    #            upload_react_admin_models_folder)
    # post_event('handle_create_cf',
    #            'cloudfront',
    #            project_name)
    # TODO
    # post_event('add_cnames_to_cf',
    #            upload_react_admin_models_folder)


if __name__ == '__main__':
    asyncio.run(main())
#     import json
#     a = {
#         "raw_command":
#         """import os
# for root, dirs , files in os.walk("./"):
#     for file in files:
#         print(file)
# """
#     }
#     b = json.dumps(a)
#     print("b", b)
