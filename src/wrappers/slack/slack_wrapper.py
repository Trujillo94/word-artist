import logging

from src.config.slack import SLACK_BOT_TOKEN
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
    def send_message(self, payload):
        raise NotImplementedError
        # self.__client.chat_postMessage(**payload)
