import logging
from typing import Any

import requests
from src.word_artist.event_types import Event, get_event_type
from src.word_artist.interactivity.slack_command_handler import \
    SlackCommandHandler
from src.wrappers.slack.slack_wrapper import SlackWrapper

logger = logging.getLogger(
    "src.word_artist.interactivity.slack_interactivity_handler")


class SlackInteractivityHandler:

    # Public:
    def run(self, event: dict) -> dict:
        self.__event = event
        self.__get_payload()
        self.__get_response_url()
        body = None
        try:
            match get_event_type(event):
                case Event.ASYNC_GENERATION:
                    body = self.__compute_wordart_preview_message()
                case Event.BUTTON_ACTION:
                    action = self.__payload['actions'][0]
                    body = self.__compute_buttons_reply_message(action)
                case _:
                    raise Exception(f'Invalid event. Event: <{event}>')
        except Exception as e:
            body = self.__handle_interactivity_error(e)
        finally:
            if type(body) is not dict:
                e = Exception(f'Error: body is not a dict. Event: <{body}>')
                body = self.__handle_interactivity_error(e)
            body = self.__add_status_if_missing(body)
            self.__reply_to_slack(body)
        print(f'Response body: {body}')
        return body

    # Private:
    def __get_payload(self) -> None:
        event = self.__event
        payload = event.get('payload')
        if payload is None:
            raise Exception(
                f'Invalid event: missing <payload> field. Event: <{event}>')
        self.__payload = payload

    def __get_response_url(self) -> None:
        event = self.__event
        payload = self.__payload
        response_url = payload.get('response_url')
        if response_url is None:
            raise Exception(
                f'Invalid event: missing <response_url> field. Event: <{event}>')
        self.__response_url = response_url

    def __compute_wordart_preview_message(self) -> dict:
        payload = self.__payload
        text = payload['text']
        style = payload.get('style', None)
        body = SlackCommandHandler().generate_command_message(text, style=style)
        body['replace_original'] = True
        # body['delete_original'] = True
        body['response_type'] = 'ephimeral'
        return body

    def __compute_buttons_reply_message(self, action: dict) -> dict:
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
                msg = SlackCommandHandler().generate_command_message(value, style=style)
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

    def __handle_interactivity_error(self, e: Exception) -> dict:
        logger.error(f'Error: {e}')
        body = {
            'text': f'Error: {e}',
            'blocks': str(SlackWrapper().get_image_blocks('error')),
            "status": "error",
        }
        return body

    def __reply_to_slack(self, body: Any) -> None:
        response_url = self.__response_url
        response = requests.post(response_url, json=body)
        # check_response(response)
        print(f'Slack response: {response}')

    def __add_status_if_missing(self, body: dict) -> dict:
        if type(body) is dict:
            if 'status' not in body:
                body['status'] = 'success'
        return body
