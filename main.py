import logging
from enum import Enum, auto

import requests

from src.config.aws import LAMBDA_NAME
from src.utils.aws_cli_toolbox import (check_async_lambda_response,
                                       invoke_lambda)
from src.word_artist.slack_word_artist import SlackWordArtist
from src.wrappers.slack.slack_wrapper import SlackWrapper

logger = logging.getLogger("main")


class Event(Enum):
    TEXT_COMMAND = auto()
    ASYNC_GENERATION = auto()
    BUTTON_ACTION = auto()


def type_of_event(event: dict) -> Event:
    if 'text' in event:
        return Event.TEXT_COMMAND
    elif 'type' in event:
        match event['type']:
            case 'ASYNC_GENERATION':
                return Event.ASYNC_GENERATION
            case _:
                raise Exception(f'Invalid event. Event: <{event}>')
    elif 'payload' in event:
        return Event.BUTTON_ACTION
    else:
        raise Exception(f'Invalid event. Event: <{event}>')


def call_async_generation(event: dict) -> None:
    if type(LAMBDA_NAME) is str:
        response = invoke_lambda(LAMBDA_NAME, event, synchronously=False)
        logger.info(f'Async generation response: {response}')
        check_async_lambda_response(response)
    else:
        raise Exception(f'Invalid lambda name: <{LAMBDA_NAME}>')


def handler(event: dict, context: dict) -> dict:
    # print(event)
    logger.info(f'event: {event}')
    logger.info(f'context: {context}')
    slack_msg = {}
    match type_of_event(event):
        case Event.TEXT_COMMAND:
            event = {
                "data": event,
                "type": "ASYNC_GENERATION"
            }
            response = call_async_generation(event)
            slack_msg = SlackWordArtist().compute_loading_message()
        case Event.ASYNC_GENERATION:
            data = event['data']
            text = data['text']
            response_url = data['response_url']
            style = data.get('style', None)
            body = SlackWordArtist().run(text, style=style)
            body['replace_original'] = True
            body['response_type'] = 'ephimeral'
            response = requests.post(response_url, json=body)
            logger.info(f'Slack response: {response}')
        case Event.BUTTON_ACTION:
            payload = event['payload']
            action = payload['actions'][0]
            value = action['value']
            response_url = payload['response_url']
            # channel_id = payload['channel']['id']
            # user_id = payload['user']['id']
            image_blocks = SlackWrapper().get_image_blocks(value)
            body = None
            match action['action_id']:
                case 'send':
                    # SlackWrapper().send_message(channel_id, text, user_id=user_id)
                    body = {
                        'text': str(image_blocks),
                        "delete_original": True,
                        "response_type": "in_channel"
                    }
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
