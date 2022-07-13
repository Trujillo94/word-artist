import inspect
import json

from src.utils.toolbox import load_env_var, load_json_file
from src.word_artist.slack_message_formatting.slack_message_formatter import \
    SlackMessageFormatter
from src.wrappers.slack.slack_wrapper import SlackWrapper

ATTACHMENTS_TEMPLATE_FILEPATH = 'tests/data/attachments_template.json'
BLOCKS_TEMPLATE_FILEPATH = 'tests/data/blocks_template.json'


def test_slack_bot_connection():
    response = SlackWrapper().test_api()
    assert('ok' in response)
    assert response['ok'] is True


def test_send_message_as_bot():
    CHANNEL_ID = load_env_var('SLACK_TESTING_CHANNEL_ID') or ''
    function_name = inspect.currentframe().f_code.co_name
    text = f'Unit Testing: *{function_name}*'
    SlackWrapper().send_message(CHANNEL_ID, text=text)


def test_get_user_name_and_icon_url_from_username():
    user_id = load_env_var('SLACK_TESTING_USER_ID') or ''
    ref_name = 'Oriol Trujillo'
    name, icon_url = SlackWrapper().get_profile_fields(
        user_id, fields=['real_name', 'image_512'])
    assert name == ref_name
    assert type(icon_url) is str and len(icon_url) > 0


def test_send_message_as_user():
    CHANNEL_ID = load_env_var('SLACK_TESTING_CHANNEL_ID') or ''
    function_name = inspect.currentframe().f_code.co_name
    text = f'Unit Testing: *{function_name}*'
    username = 'Oriol Trujillo'
    icon_url = 'https://ca.slack-edge.com/T03HZL7AGSF-U03HWRB6U5B-decfad7279ff-512'
    SlackWrapper().send_message(CHANNEL_ID, text=text, name=username, icon_url=icon_url)


def test_send_message_as_user_with_custom_name():
    CHANNEL_ID = load_env_var('SLACK_TESTING_CHANNEL_ID') or ''
    function_name = inspect.currentframe().f_code.co_name
    text = f'Unit Testing: *{function_name}*'
    user_id = load_env_var('SLACK_TESTING_USER_ID') or ''
    username = 'Custom Name'
    SlackWrapper().send_message(CHANNEL_ID, text=text, user_id=user_id, name=username)


def test_template_message_formatting():
    function_name = inspect.currentframe().f_code.co_name
    fields = {
        "text": f'Unit Testing: *{function_name}*',
        "img_url": "https://giphy.com/gifs/pokemon-venusaur-pokemoncard-Y4kZokSLJov84J421T"
    }
    msg = SlackMessageFormatter(ATTACHMENTS_TEMPLATE_FILEPATH).compute(fields)
    assert type(msg) is dict
    json_msg = json.dumps(msg)
    dict_msg = json.loads(json_msg)
    assert msg == dict_msg


def test_send_blocks_message():
    CHANNEL_ID = load_env_var('SLACK_TESTING_CHANNEL_ID') or ''
    function_name = inspect.currentframe().f_code.co_name
    text = f'Unit Testing: {function_name}'
    img_url = "https://media0.giphy.com/media/l0JMrPWRQkTeg3jjO/giphy.gif?cid=790b761118dcdd45484a085423b92468d1a9b8e2283561b6&rid=giphy.gif&ct=g"
    blocks = SlackWrapper().get_image_blocks(img_url)
    SlackWrapper().send_message(CHANNEL_ID, text=text, blocks=blocks)


if __name__ == "__main__":
    # test_slack_bot_connection()
    # test_send_message_as_bot()
    # test_send_message_as_user()
    # test_get_user_name_and_icon_url_from_username()
    # test_send_message_as_user_with_custom_name()
    test_send_blocks_message()
    # test_template_message_formatting()
