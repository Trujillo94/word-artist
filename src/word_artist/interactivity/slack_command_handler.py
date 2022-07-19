import logging
from dataclasses import dataclass

from src.config.aws import LAMBDA_NAME
from src.utils.aws_cli_toolbox import (check_async_lambda_response,
                                       invoke_lambda)
from src.word_artist.interactivity.slack_prompt_messages import \
    SlackWordArtistUserMessages
from src.word_artist.slack_message_formatting.slack_message_formatter import \
    SlackMessageFormatter
from src.word_artist.word_art_generation.word_art_generator import \
    WordArtGenerator

logger = logging.getLogger(
    "src.word_artist.interactivity.slack_command_handler")


@dataclass
class SlackCommandHandler:

    message_template_filepath: str = 'src/word_artist/slack_message_formatting/message_template.json'

    # Public:
    def run(self, event: dict) -> dict | None:
        try:
            response = self.__call_async_generation(event)
            print(f'Async generation response: {response}')
            return SlackWordArtistUserMessages().generate_loading_message()
        except Exception as e:
            logger.error(f'Error: {e}')
            return SlackWordArtistUserMessages().generate_error_message(e)

    def generate_command_message(self, text: str, style: str | None = None) -> dict:
        self.__text = text
        self.__style = style
        self.__generate_image()
        slack_msg = self.__generate_slack_message()
        return slack_msg

    # Private:
    def __call_async_generation(self, event: dict) -> dict:
        event = {
            "payload": event,
            "type": "ASYNC_GENERATION"
        }
        if type(LAMBDA_NAME) is str:
            response = invoke_lambda(LAMBDA_NAME, event, synchronously=False)
            print(f'Async generation response: {response}')
            check_async_lambda_response(response)
            return response
        else:
            raise Exception(f'Invalid lambda name: <{LAMBDA_NAME}>')

    def __generate_image(self) -> None:
        text = self.__text
        style = self.__style
        word_art_generator = WordArtGenerator()
        img_filepath = word_art_generator.compute(text, style=style)
        style = word_art_generator.style
        # img_filepath = 'media/wordartist_scheme.png'
        self.__img_url = img_filepath
        self.__style = style

    def __generate_slack_message(self) -> dict:
        img_url = self.__img_url
        text = self.__text
        style = self.__style
        event_str = str({
            'text': text,
            'style': style,
            'img_url': img_url
        }).replace('"', "'")
        template_filepath = self.message_template_filepath
        fields = {
            'img_url': img_url,
            'text': text,
            'style': style,
            'event': event_str
        }
        msg = SlackMessageFormatter(template_filepath).compute(fields)
        return msg
