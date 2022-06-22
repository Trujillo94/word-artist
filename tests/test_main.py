import sys

from main import handler

sys.path.append('./')


def test_main():
    event = {
        "text": "Is this working",
        "style": None
    }
    handler(event, {})


if __name__ == "__main__":
    test_main()
