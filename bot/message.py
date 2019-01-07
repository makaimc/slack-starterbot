class Message:

    def __init__(self, channel, thread_ts, message, link_url=""):
        self.channel = channel
        self.thread_ts = thread_ts
        self.raw_message = message
        self.formatted_message = ""
        if message:
            self.formatted_message = "\n".join(["<{}|{}>".format(link_url.format(m), m) for m in message])

        # formatted_messages = ["<{}|{}>".format(self.LINK_URL.format(m), m) for m in matchs]
        # return "\n".join(formatted_messages)
