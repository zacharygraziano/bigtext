import json
import requests
import os
import traceback

from api import tokens


SLACK_OAUTH2_APP_ID = os.environ['SLACK_OAUTH2_APP_ID']
WEB_APP_URL = os.environ['WEB_APP_URL']


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
        persist_installation_tokens(token_response)
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

    redirect_location = None

    if not code:
        redirect_location = "https://{}/404.html".format(WEB_APP_URL)
    else:
        try:
            token_response = slack_code_for_token_exchange(code)
            persist_auth_tokens(token_response)
            redirect_location = "https://slack.com/app_redirect?app={}".format(
                SLACK_OAUTH2_APP_ID)
        except:
            tb = traceback.format_exc()
            print("Received error: {} in oauth2 flow\n ".format(tb))
            redirect_location = "https://{}/oauth_error.html".format(
                WEB_APP_URL)

    return {
        "statusCode": 302,
        "headers": {
            "Location": redirect_location
        }
    }
