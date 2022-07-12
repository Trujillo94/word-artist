import json
from time import sleep

import boto3
import botocore
from botocore.config import Config
from botocore.exceptions import ClientError
from src.utils.json_toolbox import load_if_json
from src.utils.logging_toolbox import log_warning
from src.wrappers.aws.connect import boto3_session
from src.wrappers.aws.exception import AWSException


def invoke_lambda(function_name: str, payload: dict, read_timeout: int = 60, connect_timeout: int = 60, max_attempts=3, max_idle_attempts=30, wait_time=3, synchronously: bool = True) -> dict | None:
    try:
        return execute_lambda_invocation(function_name, payload, read_timeout=read_timeout, connect_timeout=connect_timeout, max_attempts=max_attempts, synchronously=synchronously)
    except ClientError as e:
        code = e.response['Error']['Code']
        message = e.response['Error']['Message']
        if code == 'CodeArtifactUserPendingException':
            log_warning(
                f'AWS Lambda failed with ClientError and will be retried (max. retries: {max_idle_attempts}). {code} - {message}')
            for i in range(1, max_idle_attempts):
                sleep(wait_time)
                try:
                    return execute_lambda_invocation(function_name, payload, read_timeout=read_timeout, connect_timeout=connect_timeout, max_attempts=max_attempts, synchronously=synchronously)
                except ClientError as e:
                    code = e.response['Error']['Code']
                    message = e.response['Error']['Message']
                    if i >= max_idle_attempts - 1:
                        operation_name = 'invoke_lambda'
                        raise ClientError(
                            f'AWS Lambda Error - Exceeded maximum number of retries for CodeArtifactUserPendingException ({max_idle_attempts}) with errors: {code} - {message}.', operation_name) from e
                    elif code == 'CodeArtifactUserPendingException':
                        log_warning(
                            f'({i}/{max_idle_attempts}) - AWS Lambda failed. {code} - {message}')
                    else:
                        raise e
                except Exception as e:
                    raise e
        else:
            raise e
    except Exception as e:
        raise e


def execute_lambda_invocation(function_name: str, payload: dict, read_timeout: int = 60, connect_timeout=60, max_attempts: int = 3, synchronously: bool = True) -> dict:
    client_config = Config(
        read_timeout=read_timeout,
        connect_timeout=connect_timeout,
        retries={"max_attempts": max_attempts}
    )
    client = boto3_session.client('lambda', config=client_config)
    invocation_type = 'RequestResponse' if synchronously else 'Event'
    response = client.invoke(FunctionName=function_name,
                             InvocationType=invocation_type,
                             Payload=json.dumps(payload))
    if synchronously:
        content_string = response['Payload'].read().decode()
        content = json.loads(content_string)
        return content
    else:
        return response


def run_task(cluster_name, task_definition, container_name, commands=[], environment_vars=[], environment_files=[], launch_type='FARGATE', group_name='', propagate_tags='TASK_DEFINITION', tags=[], network_config=None, subnets_ids=None):
    if launch_type.upper() == 'FARGATE' and network_config is None and subnets_ids is not None:
        network_config = get_fargate_task_network_config(subnets_ids)
    client = boto3_session.client('ecs')
    response = client.run_task(
        #     capacityProviderStrategy=[
        #     {
        #         'capacityProvider': 'string',
        #         'weight': 123,
        #         'base': 123
        #     },
        # ],
        cluster=cluster_name,
        # count=123,
        # enableECSManagedTags=True | False,
        # enableExecuteCommand=True | False,
        group=group_name,
        launchType=launch_type,
        networkConfiguration=network_config,
        overrides={
            'containerOverrides': [
                {
                    'name': container_name,
                    'command': commands,
                    'environment': environment_vars,
                    'environmentFiles': environment_files,
                    # 'cpu': 123,
                    # 'memory': 123,
                    # 'memoryReservation': 123,
                    # 'resourceRequirements': [
                    #     {
                    #         'value': 'string',
                    #         'type': 'GPU' | 'InferenceAccelerator'
                    #     },
                    # ]
                },
            ],
            #     'cpu': 'string',
            #     'inferenceAcceleratorOverrides': [
            #         {
            #             'deviceName': 'string',
            #             'deviceType': 'string'
            #         },
            #     ],
            #     'executionRoleArn': 'string',
            #     'memory': 'string',
            #     'taskRoleArn': 'string',
            #     'ephemeralStorage': {
            #         'sizeInGiB': 123
            #     }
        },
        #     placementConstraints=[
        #     {
        #         'type': 'distinctInstance' | 'memberOf',
        #         'expression': 'string'
        #     },
        # ],
        #     placementStrategy=[
        #     {
        #         'type': 'random' | 'spread' | 'binpack',
        #         'field': 'string'
        #     },
        # ],
        #     platformVersion='string',
        propagateTags=propagate_tags,
        # referenceId='string',
        # startedBy='string',
        tags=tags,
        taskDefinition=task_definition
    )
    if 'failures' in response:
        failures = response['failures']
        if len(failures) > 0:
            raise Exception(f'Run new task failed. Message: <{failures[0]}>')
    return response


def stop_task(cluster_name, task_id, reason=None):
    client = boto3_session.client('ecs')
    response = client.stop_task(
        cluster=cluster_name,
        task=task_id,
        reason=reason
    )
    return response


def get_task_state(cluster_name, task_id):
    response = describe_task(cluster_name, task_id)
    tasks = response['tasks']
    if len(tasks) > 0:
        state = tasks[0]
        return state
    else:
        raise Exception(
            f'Task not found. DescribeTasks response: <{response}>.')


def describe_task(cluster_name, task_id):
    client = boto3_session.client('ecs')
    response = client.describe_tasks(
        cluster=cluster_name,
        tasks=[
            task_id,
        ]
    )
    return response


def get_fargate_task_network_config(subnets_ids):
    network_config = {
        'awsvpcConfiguration': {
            'subnets': subnets_ids,

            'assignPublicIp': 'ENABLED'
        }
    }
    return network_config


def check_async_lambda_response(response) -> None:
    try:
        if 'ResponseMetadata' in response:
            if 'HTTPStatusCode' in response['ResponseMetadata']:
                status_code = response['ResponseMetadata']['HTTPStatusCode']
                if not str(status_code).startswith('2'):
                    raise Exception(
                        f'AWS Lambda invocation failed. Response: <{response}>.')
    except KeyError as e:
        raise Exception(
            f'AWS Lambda invocation failed. Invalid response structure. Exception: {e}. Response: <{response}>.')
