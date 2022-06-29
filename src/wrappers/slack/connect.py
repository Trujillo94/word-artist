import logging

from slack_sdk import WebClient
from src.config.slack import SLACK_BOT_TOKEN
from src.wrappers.slack.exception import SlackException

logger = logging.getLogger("wrappers.slack.connect")


@SlackException.error_handling
def initialize_slack_client():
    return WebClient(token=SLACK_BOT_TOKEN)


slack_client = initialize_slack_client()
