import logging

from src.word_artist.slack_word_artist import SlackWordArtist

logger = logging.getLogger("main")


def handler(event, context):
    print(event)
    logger.info(f'event: {event}')
    logger.info(f'context: {context}')
    slack_msg = {}
    if 'text' in event:
        text = event['text']
        style = event.get('style', None)
        slack_msg = SlackWordArtist().run(text, style=style)
    elif 'payload' in event:
        print(event['payload'])
    else:
        pass
    logger.info("Successful execution")
    return slack_msg
    # return event


if __name__ == "__main__":
    event = {
        "text": "Hello World"
    }
    response = handler(event, {})
    print(response)
