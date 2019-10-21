# big text

BIG TEXT is a Slack command (`/big`) that you can use to generate images with large
text and send them to your coworkers.

_example_

```
/big BIG TEXT  is a Slack command (`/big`) that you can use to generate images with large text and send them to your coworkers.
```
might make 

![big text example](https://big.dougie.tech/content/066563d5-9723-4961-beab-ddeda58bcae6.png)

## Installation

To install to your Slack visit the [website for the app](https://big.dougie.tech)

## Developers

This project uses Serverless framework and is split across the following Lambda functions:
- the `/generate` handler
- the `big` Lambda
- the `oauth2 callback` Lambda
- the `/events` handler

### Generate
This function services an HTTP endpoint that Slack calls
when slash commands are invoked. Its jobs are to (a) verify that it is indeed Slack
who is making the request, (b) dispatch the request to the appropriate handler
for it (asynchronously) and (c) return a 200 to Slack as soon as it can.

### big
This function creates the big text image based on the text provided in the original
slash command. It then checks the database to see if we have an access token for the
caller.

If we do have an access token, the function sends the image on their behalf to the channel
where `/big` was originally invoked. If we don't, we use the `response_url` from the original
invocation to ask the caller to authorize us to send messages on their behalf.

#### Adding New Scripts

The `/big` Slack command randomly chooses from a library of hand-crafted, chef's kiss
worthy ImageMagick scripts for creating large text on backgrounds. To add one, add a shell
script to the `scripts` directory. 

Image scripts will be called with these arguments:
- `$1` text file containing the big text argument
- `$2` path of directory containing bundled fonts
- `$3` path to where image should be written

Then, in the `commands.py` file, add the name of your script (sans `.sh` file extension) to the
`IMAGE_SCRIPTS` list.

If your script needs custom fonts or other resources, they will need to be placed in the (`.gitignore`d)
`fonts/` directory prior to deploying.

### oauth2 callback
This is a very boring function that's only used during the initial installation
of the app or when a user needs to authorize the app to post its images as them.
It receives a `code` from Slack and exchanges it for user or bot tokens which it
then persists.

# deploying

Deploying this requires a `variables.yml` file with the following:
```yaml
ACM_CERTIFICATE_ID: ""
ROUTE_53_HOSTED_ZONE_ID: ""
S3_BUCKET_NAME: ""
WEB_APP_URL: ""
API_BASE_URL: ""
EDGE_LAMBDA_ARN: ""
CERTIFICATE_NAME: ""
```


