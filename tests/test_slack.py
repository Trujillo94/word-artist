from src.utils.toolbox import load_env_var
from src.wrappers.slack.slack_wrapper import SlackWrapper


def test_slack_bot_connection():
    response = SlackWrapper().test_api()
    assert('ok' in response)
    assert response['ok'] is True


def test_slack_send_message():
    CHANNEL_ID = load_env_var('SLACK_TESTING_CHANNEL_ID')
    text = 'Unit Testing Slack.'
    SlackWrapper().send_message(CHANNEL_ID, text, as_user=False)


if __name__ == "__main__":
    test_slack_bot_connection()
    test_slack_send_message()
