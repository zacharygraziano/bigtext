import requests
import subprocess
import uuid
import boto3
import os
import traceback
import random

from api import tokens

SLACK_OAUTH2_CLIENT_ID = os.environ['SLACK_OAUTH2_CLIENT_ID']
S3_CONTENT_BUCKET = os.environ['S3_CONTENT_BUCKET']
WEB_APP_URL = os.environ['WEB_APP_URL']

IMAGE_SCRIPTS = [
    # ("comicsans", "png"),
    # ("silly", "png"),
    # ("strong", "png")
    ("rotating", "gif"),
    ("waving", "gif")
]


def make_big_text_image(text, response_url):
    """
    Uses one of our scripts to make an image. Returns the path
    to that image on the local filesystem.
    """
    image_id = str(uuid.uuid4())
    fonts_dir = os.getcwd() + "/fonts"
    # Pick one from our library of illustrious image scripts
    (script, file_ext) = random.choice(IMAGE_SCRIPTS)

    filename = '/tmp/{}.{}'.format(image_id, file_ext)

    print("generating image {} with text {} using `{}`".format(
        image_id, text, script))

    if file_ext == "gif":
        send_might_take_a_while_message(response_url)

    text_filename = '/tmp/{}.txt'.format(image_id)
    with open(text_filename, 'w') as txtfile:
        txtfile.write(text)

    cmd = [
        "bash",
        "scripts/{}.sh".format(script),
        text_filename,
        fonts_dir,
        filename
    ]

    if subprocess.call(cmd) == 0:
        return filename


def upload_image_file(full_path):
    obj_key = "content/" + full_path.split('/')[-1]
    bucket = boto3.resource('s3').Bucket(S3_CONTENT_BUCKET)
    bucket.upload_file(full_path, obj_key, ExtraArgs={
        'ContentType': "image/{}".format(full_path.split(".")[-1])
    })
    return 'https://{}/{}'.format(WEB_APP_URL, obj_key)


def send_might_take_a_while_message(response_url):
    requests.post(
        response_url,
        json={
            'response_type': "ephemeral",
            'text': ":hourglass_flowing_sand: i'm workin', this one might take a little bit"
        }
    )


def send_error_message(response_url):
    requests.post(
        response_url,
        json={
            'response_type': "ephemeral",
            'text': "_uh oh_ looks like something went wrong. try again in a bit"
        }
    )


def big(event, context):
    """
    Come on, it makes big text
    """
    text = event['args']
    response_url = event['response_url']
    try:
        image_file = make_big_text_image(text, response_url)
        image_url = upload_image_file(image_file)
        access_token = tokens.get_slack_token(
            event['team_id'], event['user_id'])

        if access_token:
            send_image_to_channel(
                access_token, event['channel_id'], text, image_url, response_url)
        else:
            request_authorization_from_user(response_url, text, image_url)
    except:
        # TODO: insert Sentry reporting here
        # it's VERY important that the invocation has SUCCEEDED in Lambda's eyes
        # because Lambda will retry an asynchronously invoked function up to 2 times,
        # which will result in several error messages being sent to Slack for the same /big invocation
        tb = traceback.format_exc()
        print("Received error: {}\n Sending message to slack".format(tb))
        send_error_message(response_url)


def send_image_to_channel(access_token, channel_id, text, image_url, response_url):
    """
    Sends a message on behalf of the caller of /big in the channel where it was invoked.
    If the token has expired, request authorization from the caller.
    If any other error occurs, we'll send an ephemeral message saying something went wrong.
    """
    resp = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={
            "Authorization": "Bearer {}".format(access_token)
        },
        json={
            "as_user": True,
            "channel": channel_id,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*<{}|{}>*".format(image_url, text)
                    }
                },
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": "sent using /big"
                    },
                    "image_url": image_url,
                    "alt_text": text
                }
            ]
        }
    )

    if resp.status_code == 401:
        print("Slack reports unauthorized, requesting auth from user.")
        request_authorization_from_user(response_url, text, image_url)
    elif resp.status_code != 200:
        print("Slack API error with status code {}: {}").format(
            resp.status_code, resp.text)
        send_error_message(response_url)
    elif resp.status_code == 200 and not resp.json()['ok']:
        print("Slack says we're NOT good {}".format(resp.text))
        send_error_message(response_url)


def request_authorization_from_user(response_url, text, image_url):
    """
    Sends a message that only the caller of /big can see, requesting
    them to authorize us to post messages on their behalf.
    """
    r = requests.post(
        response_url,
        json={
            "response_type": "ephemeral",
            "text": "_psst!_ you need to authorize big text",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "_psst!_ I want to send this baby out but you haven't authorized me to send messages yet. Click the button to get started."
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ":key: Authorize Big Text",
                            "emoji": True
                        },
                        "url": "https://slack.com/oauth/authorize?client_id={}&scope=chat:write:user".format(SLACK_OAUTH2_CLIENT_ID)
                    }
                },
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": text,
                        "emoji": True
                    },
                    "image_url": image_url,
                    "alt_text": text
                }
            ]
        }
    )
    if r.status_code != 200:
        print("slack error requesting auth: {}".format(r.text))
        send_error_message(response_url)
