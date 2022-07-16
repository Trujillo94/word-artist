import logging

from src.word_artist.slack_word_artist import SlackWordArtist

logger = logging.getLogger("main")


def handler(event: dict, context: dict) -> dict | None:
    # print(event)
    logger.info(f'event: {event}')
    logger.info(f'context: {context}')
    response = SlackWordArtist().run(event)
    logger.info("Successful execution")
    return response


if __name__ == "__main__":
    event = {
        "text": "Hello World"
    }
    response = handler(event, {})
    print(response)
