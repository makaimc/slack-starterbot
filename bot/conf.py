from os import environ


class Conf:
    params = {'slack_bot_token': 'SLACK_BOT_TOKEN',
              'match_pattern': 'MATCH_PATTERN',
              'link_url': 'LINK_URL'}

    def load(self):
        """loading configuration from environment variables"""
        self.slack_bot_token = environ.get(self.params['slack_bot_token'])
        self.match_pattern = environ.get(self.params['match_pattern'])
        self.link_url = environ.get(self.params['link_url'])

        if self.slack_bot_token and self.match_pattern \
           and self.link_url:
            return True

        print("Missing mandatory configuration as env variable.")
        print("\n".join([self.params[k] for k in self.params.keys()]))


if __name__ == "__main__":
    pass
