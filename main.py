import logging

from src.word_artist.slack_word_artist import SlackWordArtist
from src.wrappers.slack.slack_wrapper import SlackWrapper

logger = logging.getLogger("main")


def handler(event: dict, context: dict) -> dict:
    # print(event)
    logger.info(f'event: {event}')
    logger.info(f'context: {context}')
    slack_msg = {}
    if 'text' in event:
        text = event['text']
        style = event.get('style', None)
        slack_msg = SlackWordArtist().run(text, style=style)
    elif 'payload' in event:
        payload = event['payload']
        channel_id = payload['channel']['id']
        text = payload['actions'][0]['value']
        text = text.split('send:')[-1]
        user_id = payload['user']['id']
        SlackWrapper().send_message(channel_id, text, user_id=user_id)
    else:
        raise Exception(f'Invalid event. Event: <{event}>')
    logger.info("Successful execution")
    return slack_msg


if __name__ == "__main__":
    event = {
        "text": "Hello World"
    }
    response = handler(event, {})
    print(response)
