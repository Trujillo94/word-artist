import boto3
from src.config.aws import (ACCESS_KEY_ID, BUCKET_NAME, DEFAULT_REGION,
                            SECRET_ACCESS_KEY)
from src.utils.dict_toolbox import get_values_from_list_of_dicts_by_key
from src.utils.toolbox import load_env_var


def download(bucket_route: str, local_route: str):
    client = connect()
    try:
        client.download_file(BUCKET_NAME, bucket_route, local_route)
    except Exception as exception:
        msg = str(exception)
        if msg == 'An error occurred (404) when calling the HeadObject operation: Not Found':
            msg = "Error[404] - File not found in S3 bucket."
        raise Exception(msg) from exception


def upload(local_route: str, bucket_route: str, extra_args={}):
    client = connect()
    try:
        response = client.upload_file(
            local_route, BUCKET_NAME, bucket_route, ExtraArgs=extra_args)
    except Exception as e:
        msg = str(e)
        # !! Typifiy errors here !!
        raise Exception(msg) from e
    return response


def list_objects(prefix: str = '', exact_key: bool = False):
    client = connect()
    response = client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
    if 'Contents' in response:
        objs = response['Contents']
    else:
        objs = []
    if exact_key:
        objs = list(filter(lambda obj: obj['Key'] == prefix, objs))
    return objs


def get_object(route: str):
    client = connect()
    obj = client.get_object(Bucket=BUCKET_NAME, Key=route)
    return obj


def list_objects_routes(prefix: str = '', exclude_folders: bool = False, exact_key: bool = False):
    objects = list_objects(prefix=prefix, exact_key=exact_key)
    routes = get_values_from_list_of_dicts_by_key(objects, 'Key')
    if exclude_folders:
        routes = list(filter(lambda s: not s.endswith('/'), routes))
    return routes


def delete_objects(prefix: str = '', exact_key: bool = False):
    if prefix == '':
        raise Exception('THIS WOULD DELETE ALL OBJECTS!!')
    client = connect()
    routes = list_objects_routes(prefix=prefix, exact_key=exact_key)
    objs = [{'Key': route} for route in routes]
    if len(objs) > 0:
        response = client.delete_objects(
            Bucket=BUCKET_NAME, Delete={'Objects': objs})
        return response
    else:
        return None


def delete_object_by_route(route: str):
    return delete_objects(prefix=route, exact_key=True)


def delete_objects_by_routes(routes: list[str]):
    [delete_object_by_route(route) for route in routes]


def get_object_metadata(route: str):
    obj = get_object(route)
    if type(obj) is dict:
        return obj['Metadata']
    else:
        raise Exception(f'Object not found. Route: {route}')


def get_object_content_type(route: str):
    obj = get_object(route)
    if type(obj) is dict:
        return obj['ContentType']
    else:
        raise Exception(f'Object not found. Route: {route}')


def connect():
    client = boto3.client('s3', aws_access_key_id=ACCESS_KEY_ID,
                          aws_secret_access_key=SECRET_ACCESS_KEY, region_name=DEFAULT_REGION)
    return client
