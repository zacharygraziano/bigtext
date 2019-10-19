import json
import logging
import os
import requests
import uuid
import hmac
import boto3
from urllib.parse import parse_qs

import hashlib
logger = logging.getLogger()

LAMBDAS = {
    '/big': os.environ['BIG_LAMBDA_NAME']
}


def is_request_authorized(signature, timestamp, body):
    # from https://janikarhunen.fi/verify-slack-requests-in-aws-lambda-and-python
    slack_signing_secret = os.environ['SLACK_SIGNING_SECRET']
    ''' Form the basestring as stated in the Slack API docs. We need to make a bytestring. '''
    basestring = f"v0:{timestamp}:{body}".encode('utf-8')
    ''' Make the Signing Secret a bytestring too. '''
    slack_signing_secret = bytes(slack_signing_secret, 'utf-8')
    ''' Create a new HMAC "signature", and return the string presentation. '''
    my_signature = 'v0=' + \
        hmac.new(slack_signing_secret, basestring, hashlib.sha256).hexdigest()

    ''' Compare the the Slack provided signature to ours.
    If they are equal, the request should be verified successfully.
    Log the unsuccessful requests for further analysis
    (along with another relevant info about the request). '''
    if hmac.compare_digest(my_signature, signature):
        return True
    else:
        logger.warning(f"Verification failed. my_signature: {my_signature}")
        return False


def invoke_lambda(function_name, args):
    boto3.client('lambda').invoke(
        FunctionName=function_name,
        InvocationType='Event',
        Payload=json.dumps(args)
    )


def async_invoke_command(parsed):
    command = parsed['command']
    invocation_arguments = {
        'args': parsed['text'],
        'team_id': parsed['team_id'],
        'user_id': parsed['user_id'],
        'response_url': parsed['response_url'],
        'channel_id': parsed['channel_id'],
        'channel_name': parsed['channel_name'],
        'trigger_id': parsed['trigger_id']
    }

    lambda_name = LAMBDAS.get(command)
    if lambda_name:
        print("asynchronously invoking {}".format(lambda_name))
        invoke_lambda(lambda_name, invocation_arguments)
    else:
        # this should like, never happen becauseit means the app contains
        # a slash command that's not in the service
        raise Error("no such command {}".format(command))


def generate(event, context):
    """
    The /generate endpoint
    Verifies input from Slack slash command for this app has been signed and
    otherwise returns 403.

    Asynchronously invokes the Lambda associated with the Slack command if the
    request is authorized and immediately returns a 200.
    """
    body = event['body']
    parsed = {k: v[0] for k, v in parse_qs(event['body']).items()}
    request_time = event['headers']['X-Slack-Request-Timestamp']
    signature = event['headers']['X-Slack-Signature']
    immediate_response = None

    if not is_request_authorized(signature, request_time, body):
        return {
            "statusCode": 403,
            "body": json.dumps({"message": "Forbidden"})
        }

    if parsed.get('text'):
        async_invoke_command(parsed)
    else:
        immediate_response = json.dumps({
            'response_type': 'ephemeral',
            'text': "ya gotta put text after `/big`, try `/big you ARE fancy`"
        })

    return {
        "statusCode": 200,
        "body": immediate_response
    }
