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
        "style": None,
        # "response_url": MOCK_RESPONSE_URL
        "token": "I2qr45qIMQ9Hce8swoGrUbCc",
        "team_id": "T03HZL7AGSF",
        "team_domain": "slackappsdeve-kb84670",
        "channel_id": "C03HZLDDFPD",
        "channel_name": "development-of-slack-apps",
        "user_id": "U03HWRB6U5B",
        "user_name": "trujillo.oriol",
        "command": "/wordart",
        # "text": "RERERE",
        "api_app_id": "A03J268R2S0",
        "is_enterprise_install": "false",
        "response_url": "https://hooks.slack.com/commands/T03HZL7AGSF/3808600553315/mLlCSH6fhGMqhzoTDn3lhj3d",
        "trigger_id": "3811085827300.3611687356899.2ee650a93885190c16cd7bd729c284db"
    }
    response = handler(event, {})
    assert_slack_message_format(response)


def test_send_text_command_response():
    function_name = inspect.currentframe().f_code.co_name
    event = {
        "text":  f'Unit Testing: *{function_name}*',
        "style": None,
        "response_url": MOCK_RESPONSE_URL
    }
    response = handler(event, {})
    text = response.get('text')
    blocks = SlackWrapper().get_blocks_from_message(response)
    channel_id = load_env_var('SLACK_TESTING_CHANNEL_ID') or ''
    user_id = load_env_var('SLACK_TESTING_USER_ID') or ''
    SlackWrapper().send_message(channel_id, text=text, blocks=blocks, user_id=user_id)


def test_send_button():
    event = load_json_file("tests/data/send_payload.json")
    event['payload']['container']['channel_id'] = load_env_var(
        'SLACK_TESTING_CHANNEL_ID')
    response = handler(event, {})
    status = response.get('status')
    if status != 'success':
        raise Exception(f'Error: <{response}>')


def test_asynchronous_generation():
    event = {
        'payload': {
            'text': 'Unit Testing: *test_text_command*',
            'style': None,
                    'response_url': MOCK_RESPONSE_URL,
                    'token': 'I2qr45qIMQ9Hce8swoGrUbCc',
                    'team_id': 'T03HZL7AGSF',
                    'team_domain': 'slackappsdeve-kb84670',
                    'channel_id': 'C03HZLDDFPD',
                    'channel_name': 'development-of-slack-apps',
                    'user_id': 'U03HWRB6U5B',
                    'user_name': 'trujillo.oriol'
        },
        'type': 'ASYNC_GENERATION'
    }
    response = handler(event, {})
    assert type(response) is dict
    assert_slack_message_format(response)
    status = response.get('status')
    if status != 'success':
        raise Exception(f'Error: <{response}>')


def test_error_reporting():
    event = {
        "payload": {
            "response_url": MOCK_RESPONSE_URL,
            "error": "Unit Testing: *error_reporting*"
        },
        "type": "ASYNC_GENERATION"
    }
    response = handler(event, {})
    assert type(response) is dict
    assert_slack_message_format(response)
    status = response.get('status')
    if status != 'error':
        raise Exception(
            f'An Exception should be raised! Response: <{response}>')


def assert_slack_message_format(msg):
    JsonObject.validate_json(msg)


if __name__ == "__main__":
    # test_text_command()
    # test_send_text_command_response()
    test_send_button()
    # test_asynchronous_generation()
    # test_error_reporting()
