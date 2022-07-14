import logging
from enum import Enum, auto
from typing import Any

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


def handler_logic(event: dict) -> dict | None:
    if type_of_event(event) == Event.TEXT_COMMAND:
        return handle_text_command(event)
    else:
        return handle_interactivity(event)


def handle_text_command(event: dict) -> dict:
    try:
        event = {
            "payload": event,
            "type": "ASYNC_GENERATION"
        }
        response = call_async_generation(event)
        logger.info(f'Async generation response: {response}')
        return SlackWordArtist().compute_loading_message()
    except Exception as e:
        logger.error(f'Error: {e}')
        return SlackWordArtist().compute_error_message(e)


def handle_interactivity(event: dict) -> dict:
    payload = event.get('payload')
    if payload is None:
        raise Exception(
            f'Invalid event: missing <payload> field. Event: <{event}>')
    response_url = payload.get('response_url')
    if response_url is None:
        raise Exception(
            f'Invalid event: missing <response_url> field. Event: <{event}>')
    body = None
    try:
        match type_of_event(event):
            case Event.ASYNC_GENERATION:
                text = payload['text']
                style = payload.get('style', None)
                body = SlackWordArtist().run(text, style=style)
                body['replace_original'] = True
                # body['delete_original'] = True
                body['response_type'] = 'ephimeral'
            case Event.BUTTON_ACTION:
                action = payload['actions'][0]
                body = get_button_action_response(action)
            case _:
                raise Exception(f'Invalid event. Event: <{event}>')
    except Exception as e:
        body = handle_interactivity_error(e)
    finally:
        if type(body) is not dict:
            e = Exception(f'Error: body is not a dict. Event: <{body}>')
            body = handle_interactivity_error(e)
        body = add_status_if_missing(body)
        reply_to_slack(response_url, body)
    return body


def handle_interactivity_error(e: Exception) -> dict:
    logger.error(f'Error: {e}')
    body = {
        'text': f'Error: {e}',
        'blocks': str(SlackWrapper().get_image_blocks('error')),
        "status": "error",
    }
    return body


def get_button_action_response(action: dict) -> dict:
    value = action.get('value')
    if value is None:
        raise Exception(
            f'Invalid event: missing <value> field in <action> event field. Event: <{action}>')
    match action['action_id']:
        case 'send':
            image_blocks = SlackWrapper().get_image_blocks(value)
            body = {
                'text': 'Your WordArt has been sent!',
                'blocks': str(image_blocks),
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
    return body


def reply_to_slack(response_url: str, body: Any) -> None:
    if response_url:
        response = requests.post(response_url, json=body)
        logger.info(f'Slack response: {response}')


def add_status_if_missing(body: dict) -> dict:
    if type(body) is dict:
        if 'status' not in body:
            body['status'] = 'success'
    return body


def handler(event: dict, context: dict) -> dict | None:
    # print(event)
    logger.info(f'event: {event}')
    logger.info(f'context: {context}')
    response = handler_logic(event)
    logger.info("Successful execution")
    return response


if __name__ == "__main__":
    event = {
        "text": "Hello World"
    }
    response = handler(event, {})
    print(response)
