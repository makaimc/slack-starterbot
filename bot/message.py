class Message:

    def __init__(self, channel, thread_ts, message):
        self.channel = channel
        self.thread_ts = thread_ts
        self.message = message
