from src.utils.toolbox import load_env_var
from src.wrappers.slack.slack_wrapper import SlackWrapper


def test_slack_bot_connection():
    response = SlackWrapper().test_api()
    assert('ok' in response)
    assert response['ok'] is True


def test_send_message_as_bot():
    CHANNEL_ID = load_env_var('SLACK_TESTING_CHANNEL_ID')
    text = 'Unit Testing Slack.'
    SlackWrapper().send_message(CHANNEL_ID, text)


def test_get_user_name_and_icon_url_from_username():
    user_id = 'U03HWRB6U5B'
    ref_name = 'Oriol Trujillo'
    user_info = SlackWrapper().get_user_info(user_id)
    profile = user_info['profile']
    assert profile['real_name'] == ref_name
    assert type(profile['image_512']) is str


def test_send_message_as_user():
    CHANNEL_ID = load_env_var('SLACK_TESTING_CHANNEL_ID')
    text = 'Unit Testing Slack impersonating a user.'
    username = 'Oriol Trujillo'
    icon_url = 'https://ca.slack-edge.com/T03HZL7AGSF-U03HWRB6U5B-decfad7279ff-512'
    SlackWrapper().send_message(CHANNEL_ID, text, username=username, icon_url=icon_url)


if __name__ == "__main__":
    # test_slack_bot_connection()
    # test_send_message_as_bot()
    # test_send_message_as_user()
    test_get_user_name_and_icon_url_from_username()
