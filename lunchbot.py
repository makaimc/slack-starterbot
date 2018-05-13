import os
import time
import re
from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
CHAT_POST_MESSAGE = 'chat.postMessage'

ORDER_COMMAND_REGEX = '^order\s*(.*)from\s(\S*)'

orders_dict = {}

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"], event["user"]
    return None, None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(channel, from_user, command):
    """
        Executes bot command if the command is known
    """

    matches = re.search(ORDER_COMMAND_REGEX, command)
    if matches:
        handle_order(channel, from_user, matches.group(1).strip(), matches.group(2).strip())
        return

    command_arr = command.split()
    command = command_arr[0]
    if len(command_arr) == 2 and command == 'summarize':
        summarize_restaurant(channel, command_arr[1])
        return

    if len(command_arr) == 2 and command == 'clear' and command_arr[1] == 'all':
        clear_all_restaurants(channel)
        return
    
    if len(command_arr) == 2 and command == 'clear':
        clear_restaurant(channel, command_arr[1])
        return

    # Sends the response back to the channel
    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text='Not sure what you mean'
    )



#Custom defined commands

def handle_order(channel, from_user, meal, restaurant):
    add_order(from_user, meal, restaurant)

    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text='<@{0}> Order added :white_check_mark:'.format(from_user, meal, restaurant)
    )

def summarize_restaurant(channel, restaurant):
    if restaurant.lower() not in orders_dict:
        summarized = 'There are no orders from *{0}*'.format(restaurant)
    else :
        rest_dict = orders_dict[restaurant.lower()]
        summarized = '*{0}:*\n'.format(restaurant)
        for meal, users in rest_dict.items():
            summarized += '_{0}_, x{1}'.format(meal, len(users))
            summarized += ' ('
            for i in range(len(users)):
                u = users[i]
                summarized += '<@{0}>'.format(u)
                if not i == len(users) - 1:
                    summarized += ', '
            summarized += ')'
    
    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text=summarized
    )

def clear_restaurant(channel, restaurant):
    rest_lower = restaurant.lower()
    if rest_lower not in orders_dict:
        message = 'There are no orders from *{0}*'.format(restaurant)
    else:
        del orders_dict[rest_lower]
        message = 'All orders from *{0}* cleared!'.format(restaurant)

    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text=message
    )

def clear_all_restaurants(channel):
    orders_dict.clear()

    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text='All orders cleared'
    )

#Orders

def add_order(from_user, meal, restaurant):
    rest_lower = restaurant.lower()
    if rest_lower not in orders_dict:
        orders_dict[rest_lower] = {}

    rest_dict = orders_dict[rest_lower]

    if meal not in rest_dict:
        rest_dict[meal] = []

    meals_arr = rest_dict[meal]
    meals_arr.append(from_user)

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel, from_user = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(channel, from_user, command)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
