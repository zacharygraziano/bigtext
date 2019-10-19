"""
access functions for Slack tokens
"""
import boto3

Tokens = boto3.resource('dynamodb').Table('BigTextSlackStorage')


def get_slack_token(team, user):
    item = Tokens.get_item(
        Key={
            'team': team,
            'user': user
        },
        ProjectionExpression='token'
    ).get('Item')
    return r['token']['S'] if item else None


def store_slack_token(team, user, token):
    """
    Upsert token for team/user.
    Returns None
    """
    Tokens.put_item(
        Item={
            'team': team,
            'user': user,
            'token': token
        }
    )


def store_bot_token(team, token):
    store_slack_token(team, "GLOBAL", token)
