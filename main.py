import logging
from enum import Enum, auto

import requests

from src.word_artist.slack_word_artist import SlackWordArtist
from src.wrappers.slack.slack_wrapper import SlackWrapper

logger = logging.getLogger("main")


class Event(Enum):
    TEXT_COMMAND = auto()
    BUTTON_ACTION = auto()


def type_of_event(event: dict) -> Event:
    if 'text' in event:
        return Event.TEXT_COMMAND
    elif 'payload' in event:
        return Event.BUTTON_ACTION
    else:
        raise Exception(f'Invalid event. Event: <{event}>')


def handler(event: dict, context: dict) -> dict:
    # print(event)
    logger.info(f'event: {event}')
    logger.info(f'context: {context}')
    slack_msg = {}
    match type_of_event(event):
        case Event.TEXT_COMMAND:
            value = event['text']
            style = event.get('style', None)
            slack_msg = SlackWordArtist().run(value, style=style)
        case Event.BUTTON_ACTION:
            payload = event['payload']
            action = payload['actions'][0]
            value = action['value']
            response_url = payload['response_url']
            channel_id = payload['channel']['id']
            user_id = payload['user']['id']
            body = None
            match action['action_id']:
                case 'send':
                    # SlackWrapper().send_message(channel_id, text, user_id=user_id)
                    body = {'text': value}
                case 'cancel':
                    body = {"delete_original": True}
                case 'again':
                    style = None
                    msg = SlackWordArtist().run(value, style=style)
                    body = {
                        "text": msg,
                        "replace_original": True,
                        "response_type": "ephemeral",
                    }
                case 'donate':
                    raise NotImplementedError
                case _:
                    raise NotImplementedError
            response = requests.post(response_url, json=body)
            logger.info(f'Slack response: {response}')
        case _:
            raise Exception(f'Invalid event. Event: <{event}>')
    logger.info("Successful execution")
    return slack_msg


if __name__ == "__main__":
    event = {
        "text": "Hello World"
    }
    response = handler(event, {})
    print(response)
