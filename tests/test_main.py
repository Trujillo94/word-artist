import inspect
import json

from main import handler
from slack_sdk.models.basic_objects import JsonObject
from src.utils.toolbox import load_env_var, load_json_file
from src.wrappers.slack.slack_wrapper import SlackWrapper

MOCK_RESPONSE_URL = 'https://github.com/Trujillo94/word-artist'


def test_text_command():
    function_name = inspect.currentframe().f_code.co_name
    event = {
        "text":  f'Unit Testing: *{function_name}*',
        "style": None
    }
    response = handler(event, {})
    assert_slack_message_format(response)


def test_error_reporting():
    raise NotImplementedError


def assert_slack_message_format(msg):
    JsonObject.validate_json(msg)


if __name__ == "__main__":
    test_error_reporting()
