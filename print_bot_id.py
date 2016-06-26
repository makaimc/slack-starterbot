import os
from slackclient import SlackClient


BOT_NAME = 'starterbot'

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


if __name__ == "__main__":
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    elif "error" in api_call:
        print("There was an error in the API call: {0}".format(api_call["error"]))
    else:
        print("could not find bot user with the name " + BOT_NAME)
