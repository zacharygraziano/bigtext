from api.verify_message import is_request_authorized
import json


def events(event, context):
    """
    The /events endpoint
    Verifies input from Slack slash command for this app has been signed and
    otherwise returns 403.
    """
    body = event['body']
    parsed = json.loads(body)
    request_time = event['headers']['X-Slack-Request-Timestamp']
    signature = event['headers']['X-Slack-Signature']
    immediate_response = None

    if not is_request_authorized(signature, request_time, body):
        return {
            "statusCode": 403,
            "body": json.dumps({"message": "Forbidden"})
        }

    if parsed['type'] == "url_verification":
        return {
            "statusCode": 200,
            "body": parsed['challenge']
        }

    # TODO: at some point could use this to have the bot user respond to messages
    else:
        return {
            "statusCode": 200
        }
