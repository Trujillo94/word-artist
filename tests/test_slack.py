from src.wrappers.slack.slack_wrapper import SlackWrapper


def test_slack_bot_connection():
    response = SlackWrapper().test_api()
    assert('ok' in response)
    assert response['ok'] is True


if __name__ == "__main__":
    test_slack_bot_connection()
