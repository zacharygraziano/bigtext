import logging
import os
import hmac
import hashlib
logger = logging.getLogger()


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
