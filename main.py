import logging

from src.word_artist.slack_word_artist import SlackWordArtist

logger = logging.getLogger("main")


def handler(event, context):
    text = event['text']
    style = event.get('style', None)
    print(text)
    img_url = SlackWordArtist().compute(text, style=style)
    logger.info("Successful execution")
    return img_url


if __name__ == "__main__":
    event = {
        "text": "Hello World"
    }
    handler(event, {})
