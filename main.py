import logging

from src.slack_word_artist import SlackWordArtist

logger = logging.getLogger("main")


def handler(event, context):
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
