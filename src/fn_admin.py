import json
import os
# from aws_xray_sdk.core import xray_recorder
# from aws_xray_sdk.core import patch_all
from lib.admin import Admin

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
    method = event["requestContext"]["http"]["method"]
    user = "heeki"

    if method == "GET":
        response = a.get_items()
        status = response["HTTPStatusCode"]
        body = json.dumps(response["ResponseBody"])
        output = build_response(status, body)

    elif method == "POST":
        response = a.put_user(user)
        status = response["HTTPStatusCode"]
        body = json.dumps(response["ResponseBody"])
        output = build_response(status, body)

    print(output)
    return output

# function: initialization
# patch_all()
table = os.environ["TABLE"]
a = Admin(table)
