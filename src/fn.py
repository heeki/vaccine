import json
from availability import Availability

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
    a = Availability(event)
    payload = []
    payload.append(a.notify(a.check_cvs()))
    payload.append(a.notify(a.check_riteaid()))
    return payload
