## What it does

Invite the Slack app into a channel, when slack notified a new message,
it will fetch all messages with `filetype:email` and process them with any specified template.

## Process Logic

1) Get email content when they are posted in Slack channel
2) Check templates/route.yaml for pre-defined action to specific keywords inside email content
3) If there is no match template, output raw email content back to the same channel
4) If there is a match, raw email content will be passed to that python file to process

## How does templates/route.yaml works

Format:

```
"Keyword": 
  - "pyfilename": 
  - "slack_channel": (Optional)
```

Search the "keyword" in raw email content, if it exists, pass to templates/`pyfilename`.py to process,
and if slack_channel is defined, the return result will be sent to `slack_channel`.

## How to

1) Create a new app at https://api.slack.com/apps
2) Rename secrets.py.sample to secrets.py
3) Fill in all information needed by secrets.py
    - Slack Incoming Webhook URL
    - Slack Bot User OAuth Access Token
    - Slack Verification Token
    - Test Channel ID (Optional)
4) Use build.sh (For Mac or Linux) or build.ps1 (For Windows PowerShell) to build the AWS Lambda Python function
5) Upload to your Lambda function, and create an AWS API Gateway to receive all json `POST` requests and pass it to Lambda
6) Test your deployment by entering your API Gateway URL to Lambda in Slack Event Subscriptions page
7) If Slack returns `Verified`, your deployment should be working
8) Subscribe to these bot events:
    - message.channels  
    
   And assign these Bot Token Scopes:
    - chat:write
    - chat:write.public
    - chat:write.customize
    - incoming-webhook
9) Send some test emails, check Cloudwatch for logs and verify if it is working as intended
10) HF!
