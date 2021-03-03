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

# function: lambda invoker handler
def handler(event, context):
    av.check_stores()
    output = av.check_users()
    for o in output:
        av.put_emf(context, o["user"], o["availability"])
    return output

# function: initialization
patch_all()
av = Availability()
av.logging = False
av.pull_config()