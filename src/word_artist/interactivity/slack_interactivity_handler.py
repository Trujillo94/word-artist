import json
import logging
from typing import Any

import requests
from src.word_artist.interactivity.event_types import Event, get_event_type
from src.word_artist.interactivity.slack_command_handler import \
    SlackCommandHandler
from src.word_artist.interactivity.slack_prompt_messages import \
    SlackWordArtistUserMessages
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
                    body = self.__compute_buttons_reply_message()
                case _:
                    raise Exception(f'Invalid event. Event: <{event}>')
            if type(body) is not dict:
                raise Exception(f'Error: body is not a dict. Event: <{body}>')
            body = self.__add_status_success(body)
            slack_response = self.__reply_to_slack(body)
            self.__check_response(slack_response)
        except Exception as e:
            body = self.__handle_interactivity_error(e)
            slack_response = self.__reply_to_slack(body)

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
        style = payload.get('style')
        body = SlackCommandHandler().generate_command_message(text, style=style)
        body['replace_original'] = True
        # body['delete_original'] = True
        body['response_type'] = 'ephimeral'
        return body

    def __compute_buttons_reply_message(self) -> dict:
        action = self.__payload['actions'][0]
        value = action.get('value')
        if not isinstance(value, str):
            raise Exception(
                f'Invalid event: missing or invalid <value> field in <action> event field. Event: <{action}>')
        value = value.replace("'", '"')
        value = json.loads(value)
        match action['action_id']:
            case 'send':
                img_url = value.get('img_url')
                text = value.get('text')
                image_blocks = SlackWrapper().get_image_blocks(img_url, text=text)
                body = {
                    'text': 'Your WordArt has been sent!',
                    'blocks': str(image_blocks),
                    "delete_original": True,
                    "response_type": "in_channel"
                }
            case 'cancel':
                body = {"delete_original": True}
            case 'again':
                style = value.get('style')
                if style is not None:
                    if 'used_styles' not in value:
                        value['used_styles'] = []
                    value['used_styles'].append(style)
                    value['used_styles'] = list(set(value['used_styles']))
                command_event = {**self.__event, **value}
                msg = SlackCommandHandler().run(command_event)
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
        body = SlackWordArtistUserMessages().generate_error_message(e)
        return body

    def __reply_to_slack(self, body: Any) -> requests.Response:
        response_url = self.__response_url
        response = requests.post(response_url, json=body)
        # print(f'Slack response: {response.text}')
        return response

    def __add_status_success(self, body: dict) -> dict:
        if type(body) is dict:
            if 'status' not in body:
                body['status'] = 'success'
        return body

    def __check_response(self, response: requests.Response) -> None:
        if not str(response.status_code).startswith('2'):
            raise Exception(
                f'Error: {response.status_code}. Details: {response.text}')
