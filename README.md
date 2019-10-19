# BIG TEXT

BIG TEXT is an image macro Slack app. It makes slash commands that you can install
into a workspace and send goofy images from a bot user.

## Developers

This project uses Serverless framework and is split across the following Lambda functions:
- the `/generate` handler
- the `/send` handler
- the `big` Lambda
- the `oauth2 callback` Lambda

### Generate
Located in `handler.py`, this function services an HTTP endpoint that Slack calls
when slash commands are invoked. Its jobs are to (a) verify that it is indeed Slack
who is making the request and (b) dispatch the request to the appropriate handler
for it.

Why does it work this way? Slack requires you to respond to a slash command rather
quickly (within 3s) and suggests that longer running operations form messages using
response bodies, but rather by making requests to the `response_url` paramter in
the request. However, since this is Lambda, we can't return a `200` and keep doing
stuff. So we quickly glance at the command, use the Lambda API to invoke the correct
function asynchronously, and return a 200 OK ASAP.

### big
This function creates the big text image based on the text provided in the original
slash command. It then uses the `response_url` to send back a message to the channel
including the big text image.

### oauth2 callback
This is a very boring function that's only used during the initial installation
of the app or when a user needs to authorize the app to post its images as them.
It receives a `code` from Slack and exchanges it for user or bot tokens which it
then persists.


