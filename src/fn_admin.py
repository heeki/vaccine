import base64
import boto3
import json
import os

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
    print(json.dumps(event))
    payload = event
    output = build_response(200, json.dumps(payload))
    print(output)
    return output
