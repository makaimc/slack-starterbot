<!-- MarkdownTOC -->

- [Linker slackbot](#linker-slackbot)
	- [Installation](#installation)
	- [Env var setup](#env-var-setup)
- [Getting the bot running](#getting-the-bot-running)
- [Improvment list](#improvment-list)
- [References: slack-starterbot](#references-slack-starterbot)

<!-- /MarkdownTOC -->
# Linker slackbot 
Just a bot responding with links for given pattern

## Installation
```
# create a virtualenv from python3
virtualenv -p python3 botenv

# install the project requirments
source botenv/bin/activate
pip install -r requirements.txt
```


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

# Getting the bot running
```
$ ./bot.py

Starter Bot connected and running!
I am member of 2 channels: test,demo
...

```

# Improvment list
- run in a docker image (suitable for openshift)
- (/) avoid posting multiple time the same link in a given thread
- get link pattern from environment variable
- add test coverage
- add logging
- connect to externals system to get details related to the link provided



# References: slack-starterbot
A simple Python-powered starter Slack bot. Read 
[the tutorial](https://www.fullstackpython.com/blog/build-first-slack-bot-python.html) 
for a full overview.
