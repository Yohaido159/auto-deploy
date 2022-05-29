from pathlib import Path
from executor.executor import Executor
from executor.executor_listener import subscribe_lambda_preper, subscribe_aws_function
from executor.s3.s3_config import S3Config
from config.config import ConfigLoaderJson

from event.event import post_event

CONFIG_PATH = "./config_files/config.json"


def main():
    executor = Executor(ConfigLoaderJson(CONFIG_PATH))

    subscribe_lambda_preper()
    subscribe_aws_function()

    upload_lambda_zip = S3Config(
        bucket_name=executor.config.bucket_name,
        from_path=Path(executor.config.lambda_zip_path),
        key=executor.config.project_name + "/django/store-lambda.zip",
        file_or_folder='file',
        acl="private"
    )
    upload_lambda_layer_zip = S3Config(
        bucket_name=executor.config.bucket_name,
        from_path=Path(executor.config.lambda_layer_zip_path),
        key=executor.config.project_name + "/layers/store-lambda-layer.zip",
        file_or_folder='file',
        acl="private"
    )
    upload_react_folder = S3Config(
        bucket_name=executor.config.bucket_name,
        from_path=Path(executor.config.react_path),
        key=executor.config.project_name + "/react",
        file_or_folder='folder',
        acl="public-read"
    )

    post_event('handle_lambda_zip', executor.config.django_project_path)
    # post_event('upload_to_s3', upload_lambda_zip)
    # post_event('update_lambda_zip', )
    # post_event('handle_create_requirements',
    #            executor.config.django_project_path, executor.config.generated_files,)
    # post_event('handle_lambda_layer_zip',
    #            executor.config.lambda_layer_zip_path, executor.config.generated_files)
    # post_event('insert_packages_into_zip',
    #            executor.config.django_project_path, executor.config.generated_files,)
    # post_event('upload_to_s3', upload_lambda_layer_zip)
    # post_event('update_lambda_zip', )


if __name__ == '__main__':
    main()
