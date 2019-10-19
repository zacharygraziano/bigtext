import time
import requests


def big(event, context):
    """
    Come on, it makes big text
    """
    print(event)
    text = event['args']
    image_url = 'https://s3.amazonaws.com/big.dougie.tech/dougie.png'
    response_url = event['response_url']

    send_response_to_slack(response_url, text, image_url)


def send_response_to_slack(response_url, text, image_url):
    requests.post(
        response_url,
        json={
            'response_type': 'in_channel',
            'attachments': [
                {
                    'fallback': text,
                    'image_url': image_url
                }
            ]
        }
    )
