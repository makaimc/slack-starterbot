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

ORDER_COMMAND_REGEX = 'order\s+([^0-9]*)\s+([0-9]*(?:,|.)?[0-9]*)\s*(?:kn)*\s*from\s+(\S*)'
MEAL_DICT_KEY_USERS = 'users'
MEAL_DICT_KEY_PRICE = 'price'

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
        meal = matches.group(1).strip()
        restaurant = matches.group(3).strip()
        try:
            price = float(matches.group(2).strip().replace(',', '.'))
        except:
            price = 0.0

        print('Order received:\nRestaurant: {0}\nMeal: {1}\nPrice: {2}\n'.format(restaurant, meal, price))

        handle_order(channel, from_user, meal, price, restaurant)
        return

    command_arr = command.split()
    command_arr_len = len(command_arr)
    command = command_arr[0]

    if (command_arr_len == 1 or command_arr_len == 2) and command == 'summarize':
        restaurant = command_arr[1] if command_arr_len > 1 else None
        summarize_restaurant(channel, restaurant)
        return

    if command_arr_len == 2 and command == 'clear' and command_arr[1] == 'all':
        clear_all_restaurants(channel)
        return
    
    if command_arr_len == 2 and command == 'clear':
        clear_restaurant(channel, command_arr[1])
        return

    if command_arr_len == 2 and command == 'orders' and command_arr[1] == 'cancel':
        cancel_orders(channel, from_user)
        return
    
    if command_arr_len == 1 and command == 'help':
        print_usage(channel)
        return

    # Sends the response back to the channel
    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text='<@{0}> not sure what you mean. Try typing *help* to get the list of supported commands!'.format(from_user)
    )

#Helpers

def usage_description():
    return ''.join([
        '*Commands* and _arguments_ :fork_and_knife:\n\n',
        '*order* _meal_ *from* _restaurant_\n',
        '\t• Order meal from restaurant\n',
        '*summarize* _restaurant_\n',
        '\t• Summarize all orders from restaurant\n',
        '*orders cancel*\n',
        '\t • Cancel orders from user\n',
        '*clear* _restaurant_\n',
        '\t• Clear all orders from restaurant\n',
        '*clear all*\n',
        '\t• Clear all orders',
    ])

#Custom defined commands

def handle_order(channel, from_user, meal, price, restaurant):
    add_order(from_user, meal, price, restaurant)

    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text='<@{0}> Order added :white_check_mark:'.format(from_user)
    )

def summarize_restaurant(channel, restaurant):
    if restaurant == None:
        summarized = 'Please specify restaurant name'
    elif restaurant.lower() not in orders_dict or len(orders_dict[restaurant.lower()]) == 0:
        summarized = 'There are no orders from *{0}*'.format(restaurant)
    else :
        rest_dict = orders_dict[restaurant.lower()]
        totalPrice = 0

        summarized = '*{0}:*\n'.format(restaurant)
        for meal, meal_dict in rest_dict.items():
            users = meal_dict[MEAL_DICT_KEY_USERS]
            price = meal_dict[MEAL_DICT_KEY_PRICE]
            num_orders = len(users)
            totalPrice += price * num_orders

            summarized += '_{0}_, *{1}kn* x{2}'.format(meal, price, num_orders)
            summarized += ' ('
            for i in range(len(users)):
                u = users[i]
                summarized += '<@{0}>'.format(u)
                if not i == len(users) - 1:
                    summarized += ', '
            summarized += ')\n'
        
        summarized += '\n_Total:_ *{0}kn*'.format(totalPrice)
    
    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text=summarized
    )

def cancel_orders(channel, from_user):
    for rest_dict in orders_dict.values():
        delete_meals = []
        for meal_name, meal_dict in rest_dict.items():
            users = meal_dict[MEAL_DICT_KEY_USERS]
            if from_user in users:
                users.remove(from_user)
            if len(users) == 0:
                delete_meals.append(meal_name)
        
        if len(delete_meals) > 0:
            for meal in delete_meals:
                del rest_dict[meal]
    
    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text='<@{0}> All orders canceled!'.format(from_user)
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

def print_usage(channel):

    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text=usage_description()
    )

#Orders

def add_order(from_user, meal, price, restaurant):
    rest_lower = restaurant.lower()
    if rest_lower not in orders_dict:
        orders_dict[rest_lower] = {}

    rest_dict = orders_dict[rest_lower]

    if meal not in rest_dict:
        rest_dict[meal] = { MEAL_DICT_KEY_PRICE : 0.0,
                            MEAL_DICT_KEY_USERS : [] }

    meals_dict = rest_dict[meal]
    meals_dict[MEAL_DICT_KEY_USERS].append(from_user)
    if not price == 0:
        meals_dict[MEAL_DICT_KEY_PRICE] = price

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
