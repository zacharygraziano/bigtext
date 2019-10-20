import json
import requests
import os

from api import tokens


def forbidden():
    return {
        "statusCode": 403,
        "body": json.dumps({'error': "Forbidden"})
    }


def slack_code_for_token_exchange(code):
    client_id = os.environ['SLACK_OAUTH2_CLIENT_ID']
    client_secret = os.environ['SLACK_OAUTH2_CLIENT_SECRET']
    response = requests.post("https://slack.com/api/oauth.access",
                             data={'code': code},
                             auth=(client_id, client_secret))
    if response.status_code == 200:
        body = response.json()
        return body
    else:
        print(response)


def persist_auth_tokens(token_response):
    """
    Based on the scopes the response contains, we can determine whether this is
    a user authorizing us to post on their behalf, or somebody initially installing
    us to their Slack team. The app is not currently setup to allow both at the same
    time.
    """
    scopes = token_response['scope'].split(",")
    if token_response.get('bot'):
        pass
    if token_response.get('user_id') and token_response.get('access_token'):
        persist_user_authorization_tokens(token_response)


def persist_installation_tokens(token_response):
    bot_user = token_response['bot']['bot_user_id']
    bot_token = token_response['bot']['bot_access_token']
    team = token_response['team_id']
    tokens.store_bot_token(team, bot_token)


def persist_user_authorization_tokens(token_response):
    """
    Stores a user token under the (team_id, user_id)
    """
    user = token_response['user_id']
    team = token_response['team_id']
    access_token = token_response['access_token']
    tokens.store_slack_token(team, user, access_token)


def callback(event, context):
    querystring = event['queryStringParameters']
    code = querystring.get('code') if querystring else None

    # TODO figure out whether people are in a browser doing this
    # and give them HTML or send them back to slack, also handle errors
    if not code:
        return forbidden()

    token_response = slack_code_for_token_exchange(code)
    persist_auth_tokens(token_response)

    return {
        "statusCode": 200,
        "body": json.dumps({'message': "OK"})
    }
