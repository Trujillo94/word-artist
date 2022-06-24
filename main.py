import logging

from src.word_artist.slack_word_artist import SlackWordArtist

logger = logging.getLogger("main")


def handler(event, context):
    logger.info(f'event: {event}')
    logger.info(f'context: {context}')
    text = event['text']
    style = event.get('style', None)
    slack_msg = SlackWordArtist().compute(text, style=style)
    logger.info("Successful execution")
    return slack_msg
    # return event


if __name__ == "__main__":
    event = {
        "text": "Hello World"
    }
    response = handler(event, {})
    print(response)
