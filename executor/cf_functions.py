import random
import boto3
from moto import mock_s3, mock_cloudformation

from config.parse_file_variables import parse_file_and_return_str
from event.event_logger import event_logger


# @mock_cloudformation
# @mock_s3
@event_logger
def handle_create_cf(type_, project_name):
    # s3 = boto3.client('s3', region_name='us-east-1')
    # s3.create_bucket(Bucket='websites-yohai')
    rand_int = random.randint(1, 10000)

    cf = boto3.client('cloudformation', region_name='us-east-1')
    res = cf.create_stack(
        StackName=f'websites-{project_name}-cf-{rand_int}',
        TemplateBody=parse_file_and_return_str(
            f'generated_files/template_{type_}.yml', {'project_name': project_name}),
        Capabilities=['CAPABILITY_IAM'],
    )
    stack_id = res['StackId']
    # res = cf.get_waiter('stack_create_complete').wait(StackName=stack_id)
    # print("res", res)
