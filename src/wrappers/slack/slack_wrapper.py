import logging

from src.wrappers.slack.connect import slack_client
from src.wrappers.slack.exception import SlackException

logger = logging.getLogger("wrappers.slack.slack_wrapper")


class SlackWrapper:

    @SlackException.error_handling
    def __init__(self):
        self.__client = slack_client

    @SlackException.error_handling
    def test_api(self):
        return self.__client.api_test()

    @SlackException.error_handling
    def send_message(self, channel_id, text, as_user=False):
        self.__client.chat_postMessage(channel=channel_id, text=text)
