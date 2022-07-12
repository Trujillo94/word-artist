import logging

from src.utils.dict_toolbox import get_values_from_dict_by_keys
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
    def send_message(self, channel_id: str, text: str, user_id: str | None = None, name: str | None = None, icon_url: str | None = None) -> None:
        if user_id is not None:
            real_name, image = self.get_profile_fields(
                user_id, fields=['real_name', 'image_512'])
            name = real_name if name is None else name
            icon_url = image if icon_url is None else icon_url
        self.__client.chat_postMessage(
            channel=channel_id, text=text, username=name, icon_url=icon_url)

    @SlackException.error_handling
    def get_user_info(self, user_id: str) -> dict:
        response = self.__client.users_info(user=user_id)
        user_info = response['user']
        if type(user_info) is dict:
            return user_info
        else:
            raise Exception(f'Invalid user info. User info: <{user_info}>')

    @SlackException.error_handling
    def get_profile_info(self, user_id: str) -> dict:
        user_info = self.get_user_info(user_id)
        profile = user_info['profile']
        return profile

    @SlackException.error_handling
    def get_profile_fields(self, user_id: str, fields: list[str] = list()) -> tuple:
        profile = self.get_profile_info(user_id)
        if len(fields):
            data = get_values_from_dict_by_keys(profile, fields)
        else:
            data = list(profile.values())
        return tuple(data)

    @SlackException.error_handling
    def get_image_block(self, image_url: str, text: str = "A wonderful piece of WordArt.") -> dict:
        msg = {
            "blocks": [
                {
                    "type": "image",
                    "image_url": f"{image_url}",
                    "alt_text": f"{text}"
                }
            ]
        }
        return msg
