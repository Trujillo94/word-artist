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
    def send_message(self, channel_id, text, username=None, icon_url=None):
        self.__client.chat_postMessage(
            channel=channel_id, text=text, username=username, icon_url=icon_url)

    @SlackException.error_handling
    def get_user_info(self, user_id: str) -> dict:
        response = self.__client.users_info(user=user_id)
        user_info = response['user']
        if type(user_info) is dict:
            return user_info
        else:
            raise Exception(f'Invalid user info. User info: <{user_info}>')
