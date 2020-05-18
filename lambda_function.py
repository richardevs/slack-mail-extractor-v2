'''
Public version of slack-mail-extractor.
https://github.com/richardevs/slack-mail-extractor-v2
This script is intended for API Gateway + AWS Lambda
Last edit: 2020-05-18 18:00 JST

Basic function: Invite the Slack app into a channel,
this code will fetch any "filetype:email" and post full context to channel.
'''

'''
    Pre-load all templates
'''
import sys
sys.path.append('templates')
'''
    Append package to PATH to avoid Lambda dependency issue
'''
sys.path.append('package')

import re
import json
import secrets
import yaml
from slack import WebClient
from slack.errors import SlackApiError

'''
    When TEST_MODE is set to True, message will only be sent to SLACK_TEST_CHANNEL
    When SLACK_ON is set to True, message will be sent to Slack, else it will not

    For production:
TEST_MODE = False
SLACK_ON  = True
'''
TEST_MODE = False
SLACK_ON  = True

SLACK_BOT_TOKEN = secrets.get_slack_bot_token()
SLACK_VERIFICATION_TOKEN = secrets.get_slack_verification_token()
SLACK_TEST_CHANNEL = secrets.get_test_channel()

def lambda_handler(event, context):
    if 'event' in event:
        if 'files' in event['event']:
            if 'plain_text' in event['event']['files'][0]:
                if event['event']['files'][0]['filetype'] == 'email':
                    print('--- Raw Context Output Starts ---')
                    # print(event['event']['files'][0]['plain_text'])
                    print(event)
                    print('---- Raw Context Output Ends ----')

                    '''
                        Split email context into a list
                    '''
                    MAKELIST = re.split('\n|\r', event['event']['files'][0]['plain_text'])
                    REMOVE_NULL = list(filter(None, MAKELIST))
                    FINAL_LIST = []
                    for i in range(len(REMOVE_NULL)):
                        FINAL_LIST.append(REMOVE_NULL[i])

                    '''
                        Process route.yaml from templates
                    '''
                    CUSTOM_STRING = False # Pre-defined swtich
                    try:
                        with open(r'templates/route.yaml') as route:
                            route_yaml = yaml.full_load(route)
                            # print(route_yaml)
                            for k, v in route_yaml.items():
                                if any(k in s for s in FINAL_LIST):
                                    print('--- template for ' + k + ' exists, passing list to ' + v[0]["pyfilename"] + '.py ---')
                                    try:
                                        template_module = __import__(v[0]["pyfilename"])
                                        FINAL_STRING = template_module.main(FINAL_LIST)
                                        CUSTOM_STRING = True
                                    except Exception as e:
                                        print(e)
                                        print('--- pyfilename found, but ' + v[0]["pyfilename"] + ' does not exist ---')
                                        pass
                                    try:
                                        CHANNEL_TO_SENT = v[1]["slack_channel"]
                                        CUSTOM_SLACK_CHANNEL = True
                                    except IndexError:
                                        print('--- no slack channel found for this template ---')
                                        CUSTOM_SLACK_CHANNEL = False
                                        pass
                            '''
                                If no template matches (CUSTOM_STRING False), output original context
                            '''
                            if CUSTOM_STRING:
                                pass
                            else:
                                FINAL_STRING = event['event']['files'][0]['plain_text']
                            '''
                                Process Slack channel ID here, three possible situations:
                                1) TEST_MODE is ON, all to test channel
                                2) Custom channel is defined in route.yaml
                                3) Nothing is defined, sent back to origin channel
                            '''
                            if TEST_MODE:
                                print('--- TEST_MODE ON, All message will be sent to ' + SLACK_TEST_CHANNEL + ' ---')
                                CHANNEL_TO_SENT = SLACK_TEST_CHANNEL
                            if CUSTOM_SLACK_CHANNEL:
                                print('--- Custom slack channel is set to ' + CHANNEL_TO_SENT + ' ---')
                                pass
                            else:
                                CHANNEL_TO_SENT = event['event']['channel']
                            # print(CHANNEL_TO_SENT)

                    except Exception as e:
                        print(e)
                        print('--- templates/route.yaml might not exist, quitting... ---')

                    '''
                        Return process result to Slack
                    '''
                    # print(FINAL_STRING)
                    if SLACK_ON:
                        slack = WebClient(token=SLACK_BOT_TOKEN)
                        try:
                            response = slack.chat_postMessage(
                                channel = CHANNEL_TO_SENT,
                                text = FINAL_STRING,
                                username = event['event']['files'][0]['title'],
                                icon_emoji = ":mailbox_with_mail:"
                            )
                        except SlackApiError as e:
                            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
                    else:
                        print('--- SLACK_ON is False, no message will be sent ---')
    elif 'challenge' in event:
        '''
        Echo challenge string back to Slack server, only if token matches.
        '''
        if event['token'] == SLACK_VERIFICATION_TOKEN:
            return {
                'challenge': event['challenge']
            }
        else:
            print('--- Challenge failed, does not match SLACK_VERIFICATION_TOKEN ---')
            return
    else:
        print('--- Neither challenge nor email event detected ---')
        return {
            'error_msg': 'Neither challenge nor email event detected.'
        }

####### Local Debug #######
# f = open("PushEvents.json", "r")
# lambda_handler(json.load(f), 0)
