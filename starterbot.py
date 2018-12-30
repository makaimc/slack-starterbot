

import os
import time
from re import finditer, search
from slackclient import SlackClient
# from pprint import pprint
from bot.message import Message


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 2  # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
LINK_URL = "http://example.com/myValue={}"
LINK_PATTERN = "(INC000[0-9]{1})"

# list of channel the bot is member of
g_member_channel = []


def parse_direct_mention(message_text):
    """
    Finds a direct mention (a mention that is at the beginning) in message text
    and returns the user ID which was mentioned. If there is no direct mention,
    returns None
    """
    matches = search(MENTION_REGEX, message_text)
    # the first group contains the username,
    # the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def get_list_of_channels():
    """ print the list of available channels """
    channels = slack_client.api_call(
        "channels.list",
        exclude_archived=1
    )

    global g_member_channel
    g_member_channel = [channel for channel in channels['channels'] if channel['is_member']]

    # print("available channels:")
    # pprint(channels)

    print("menber of {} channels: {}"
          .format(len(g_member_channel),
                  ",".join([c['name'] for c in g_member_channel])))


def check_if_member(channel):
    """ checking if the bot is member of a given channel """
    return channel in [channel['id'] for channel in g_member_channel]


def parse_events_in_channel(events):
    """
    Selecting events of type message with no subtype
    which are posted in channel where the bot is
    """
    # print("DEBUG: my channels: {}".format(g_member_channel))
    for event in events:
        # pprint(event)
        # Parsing only messages in the channels where the bot is member
        if event["type"] != "message" or "subtype" in event or \
           not check_if_member(event["channel"]):
            # print("not for me: type:{}".format(event))
            continue

        # analyse message to see if we can suggest some links
        analysed_message = analyse_message(event['text'])

        thread_ts = event['ts']
        if 'thread_ts' in event.keys():
            thread_ts = event['thread_ts']
        return Message(event["channel"], thread_ts, analysed_message)
    return Message(None, None, None)


def analyse_message(message):
    """
    find matching sub string in the message and
    returns a list of formatted links
    """
    pattern = LINK_PATTERN
    matchs = []
    for i in finditer(pattern, message):
        value = i.group(1)
        if value not in matchs:
            matchs.append(value)

    if not len(matchs):
        return

    formatted_messages = ["<{}|{}>".format(LINK_URL.format(m), m) for m in matchs]
    return "\n".join(formatted_messages)


def respond_in_thread(bot_message):
    """Sends the response back to the channel
    în a thread
    """
    slack_client.api_call(
        "chat.postMessage",
        channel=bot_message.channel,
        thread_ts=bot_message.thread_ts,
        text=bot_message.message
    )


def bot_loop(slack_client):
    # Read bot's user ID by calling Web API method `auth.test`
    slack_client.api_call("auth.test")["user_id"]
    while True:
        bot_message = parse_events_in_channel(slack_client.rtm_read())
        if bot_message.channel:
            respond_in_thread(bot_message)
        time.sleep(RTM_READ_DELAY)


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        get_list_of_channels()
        bot_loop(slack_client)
    else:
        print("Connection failed. Exception traceback printed above.")
