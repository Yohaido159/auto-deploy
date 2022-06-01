import boto3
from moto import mock_lambda

from event.event_logger import event_logger


# @mock_lambda
@event_logger
def update_lambda_zip(project_name):
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    lambda_client.update_function_code(
        FunctionName=f'websites-{project_name}-lambda',
        S3Bucket='websites-yohai',
        S3Key=f'{project_name}/django/{project_name}-lambda.zip',
        Publish=True
    )


@event_logger
# @mock_lambda
def update_lambda_layer_zip(project_name):
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    res = lambda_client.publish_layer_version(
        LayerName=f'{project_name}-lambda-layer',
        Content={
            'S3Bucket': 'websites-yohai',
            'S3Key': f'{project_name}/layers/{project_name}-lambda-layer.zip'
        }
    )
    layer_arn = res['LayerVersionArn']
    lambda_client.update_function_configuration(
        FunctionName=f'websites-{project_name}-lambda',
        Layers=[
            layer_arn,
            # 'arn:aws:lambda:us-east-1:634832404426:layer:pg38:1	'
        ]
    )
