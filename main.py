import logging
import sys

sys.path.append('.')
sys.path.append('./')

logger = logging.getLogger("main")


def handler(event, context):
    from src.slack_word_artist import SlackWordArtist
    print(sys.path)
    text = event['text']
    style = event['style']
    response = SlackWordArtist().compute(text, style=style)
    logger.info("Successful execution")
    return response


if __name__ == "__main__":
    event = {
        "text": "Hello World",
        "style": None
    }
    handler(event, {})
