import json
from availability import Availability
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# helper functions
def build_response(code, body):
    # headers for cors
    headers = {
        "Access-Control-Allow-Origin": "amazonaws.com",
        "Access-Control-Allow-Credentials": True
    }
    # lambda proxy integration
    response = {
        'isBase64Encoded': False,
        'statusCode': code,
        'headers': headers,
        'body': body
    }
    return response

# function: initialization
def initialization():
    patch_all()

# function: lambda invoker handler
def handler(event, context):
    av = Availability()
    av.pull_config()
    payload = []
    for user in av.get_users():
        payload.append(av.check_stores(user))
    return payload

initialization()