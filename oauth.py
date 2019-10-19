import json


def callback(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({'message': "OK"})
    }
