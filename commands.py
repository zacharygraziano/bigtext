import requests
import subprocess
import uuid
import boto3
import os


def make_big_textimage(text):
    """
    use image magic to make big text image, returns the path where it's stored
    if successful and None otherwise
    """
    filename = '/tmp/{}.png'.format(str(uuid.uuid4()))
    cmd = [
        "convert",
        "-size",
        "500x400",
        "-background",
        "white",
        "-font",
        "./fonts/csmb.ttf",
        "-gravity",
        "Center",
        'caption:{}'.format(text),
        "-flatten",
        "-bordercolor",
        "white",
        "-border",
        "50x50",
        filename
    ]
    if subprocess.call(cmd) == 0:
        return filename


def upload_image_file(full_path):
    obj_key = full_path.split('/')[-1]
    bucket = boto3.resource('s3').Bucket('big.dougie.tech')
    bucket.upload_file(full_path, obj_key)
    return 'https://s3.amazonaws.com/big.dougie.tech/{}'.format(obj_key)


def big(event, context):
    """
    Come on, it makes big text
    """
    text = event['args']
    image_file = make_big_textimage(text)
    image_url = upload_image_file(image_file)
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
