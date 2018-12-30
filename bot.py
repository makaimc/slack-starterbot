
from sys import exit
from bot.conf import Conf
from bot.bot import Bot


if __name__ == "__main__":
    conf = Conf()
    if not conf.load():
        print("Missing conf, exiting")
        exit(1)

    bot = Bot(conf)
    bot.chat()
