import logging

from src.slack_error_bot import SlackErrorBot

logger = logging.getLogger("main")


def handler(event: dict, context: dict) -> dict | None:
    logger.info(f'event: {event}')
    logger.info(f'context: {context}')
    response = SlackErrorBot().run(event)
    logger.info("Successful execution")
    return response


if __name__ == "__main__":
    event = {}
    response = handler(event, {})
    print(response)
