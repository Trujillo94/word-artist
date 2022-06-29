from main import handler
from src.utils.toolbox import load_json_file


def test_text_command():
    event = {
        "text": "Is this working",
        "style": None
    }
    response = handler(event, {})
    assert_slack_message_format(response)


def test_send_button():
    event = load_json_file("tests/data/send_payload.json")
    response = handler(event, {})


def assert_slack_message_format(msg):
    if type(msg) is dict:
        if 'attachments' in msg:
            return
    assert False


if __name__ == "__main__":
    test_text_command()
    test_send_button()
