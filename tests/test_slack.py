import inspect

from src.utils.toolbox import load_env_var
from src.wrappers.slack.slack_wrapper import SlackWrapper


def test_slack_bot_connection():
    response = SlackWrapper().test_api()
    assert('ok' in response)
    assert response['ok'] is True


def test_send_message_as_bot():
    CHANNEL_ID = load_env_var('SLACK_TESTING_CHANNEL_ID') or ''
    function_name = inspect.currentframe().f_code.co_name
    text = f'Unit Testing: *{function_name}*'
    SlackWrapper().send_message(CHANNEL_ID, text)


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
    SlackWrapper().send_message(CHANNEL_ID, text, name=username, icon_url=icon_url)


def test_send_message_as_user_with_custom_name():
    CHANNEL_ID = load_env_var('SLACK_TESTING_CHANNEL_ID') or ''
    function_name = inspect.currentframe().f_code.co_name
    text = f'Unit Testing: *{function_name}*'
    user_id = load_env_var('SLACK_TESTING_USER_ID') or ''
    username = 'Custom Name'
    SlackWrapper().send_message(CHANNEL_ID, text, user_id=user_id, name=username)


if __name__ == "__main__":
    # test_slack_bot_connection()
    # test_send_message_as_bot()
    # test_send_message_as_user()
    test_get_user_name_and_icon_url_from_username()
    test_send_message_as_user_with_custom_name()
