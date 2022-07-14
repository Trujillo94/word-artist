import inspect
import json

from main import handler
from slack_sdk.models.basic_objects import JsonObject
from src.utils.toolbox import load_env_var, load_json_file
from src.wrappers.slack.slack_wrapper import SlackWrapper


def test_text_command():
    function_name = inspect.currentframe().f_code.co_name
    event = {
        "text":  f'Unit Testing: *{function_name}*',
        "style": None
    }
    response = handler(event, {})
    assert_slack_message_format(response)


def test_send_text_command_response():
    function_name = inspect.currentframe().f_code.co_name
    event = {
        "text":  f'Unit Testing: *{function_name}*',
        "style": None
    }
    response = handler(event, {})
    blocks = SlackWrapper().get_blocks_from_message(response)
    channel_id = load_env_var('SLACK_TESTING_CHANNEL_ID') or ''
    user_id = load_env_var('SLACK_TESTING_USER_ID') or ''
    SlackWrapper().send_message(channel_id, blocks=blocks, user_id=user_id)


def test_send_button():
    event = load_json_file("tests/data/send_payload.json")
    event['payload']['container']['channel_id'] = load_env_var(
        'SLACK_TESTING_CHANNEL_ID')
    response = handler(event, {})


def test_asynchronous_generation():
    event = {
        "data": {
            "text": "Unit Testing: *asynchronous_generation*",
            "style": None
        },
        "type": "ASYNC_GENERATION"
    }
    response = handler(event, {})
    assert type(response) is dict
    assert_slack_message_format(response)
    status = response.get('status')
    assert status == 'success'


def test_error_reporting():
    event = {
        "type": "HEHEHEHEHHEE"
    }
    response = handler(event, {})
    assert type(response) is dict
    assert_slack_message_format(response)
    status = response.get('status')
    assert status == 'error'


def assert_slack_message_format(msg):
    JsonObject.validate_json(msg)


if __name__ == "__main__":
    # test_text_command()
    # test_send_text_command_response()
    # test_send_button()
    test_asynchronous_generation()
