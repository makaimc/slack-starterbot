import os
from slackclient import SlackClient


BOT_NAME = 'starterbot' #define the name of the bot #TODO migrate to Config file


def get_BotID(BOT_TOKEN):
    """
        Returns the BOT_ID for the given SLACK_BOT_TOKEN
    """
    slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
                BOT_ID=user.get('id')
    else:
        print("could not find bot user with the name " + BOT_NAME)
    return BOT_ID

