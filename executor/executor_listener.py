from event.event import subscribe
from executor.django.django_listener import (lambda_perper_zip,
                                             upload_to_s3, handle_lambda_layer_zip,
                                             handle_create_requirements, insert_packages_into_zip,
                                             update_lambda_zip, update_lambda_layer_zip)


def subscribe_lambda_preper():
    subscribe('handle_lambda_zip', lambda_perper_zip)
    subscribe('update_lambda_zip', update_lambda_zip)
    subscribe('handle_create_requirements', handle_create_requirements)
    subscribe('handle_lambda_layer_zip', handle_lambda_layer_zip)
    subscribe('update_lambda_layer_zip', update_lambda_layer_zip)
    subscribe('insert_packages_into_zip', insert_packages_into_zip)


def subscribe_aws_function():
    subscribe('upload_to_s3', upload_to_s3)
