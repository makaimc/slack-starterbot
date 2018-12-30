<!-- MarkdownTOC -->

- Linker slackbot
- Improvment list
- References: slack-starterbot

<!-- /MarkdownTOC -->
# Linker slackbot 
Just a bot responding with links for given pattern


## Env var setup 
to be able to interact with your slack workspace, the bot requires the following environmental
variables to be setup:

```
# The bot token
export SLACK_BOT_TOKEN='xoxb-<your-bot-token>'
# The pattern the bot is looking for
export MATCH_PATTERN="(INC000[0-9]{1})"
# The link the bot is responding for each match
export LINK_URL="http://example.com/myValue={}"
```


# Improvment list
- avoid posting multiple time the same link in a given thread
- get link pattern from environment variable
- add test coverage
- add logging
- connect to externals system to get details related to the link provided



# References: slack-starterbot
A simple Python-powered starter Slack bot. Read 
[the tutorial](https://www.fullstackpython.com/blog/build-first-slack-bot-python.html) 
for a full overview.
