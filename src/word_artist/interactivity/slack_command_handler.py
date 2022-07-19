import logging
from dataclasses import dataclass

from src.config.aws import LAMBDA_NAME
from src.utils.aws_cli_toolbox import (check_async_lambda_response,
                                       invoke_lambda)
from src.utils.toolbox import load_env_var
from src.word_artist.slack_message_formatting.slack_message_formatter import \
    SlackMessageFormatter
from src.word_artist.word_art_generation.word_art_generator import \
    WordArtGenerator

logger = logging.getLogger(
    "src.word_artist.interactivity.slack_command_handler")


@dataclass
class SlackCommandHandler:

    loading_text: str = 'Generating a fabulous WordArt...'
    loading_img_url: str = 'https://media0.giphy.com/media/XXH77SsudU3HW/giphy.gif?cid=790b76113f7e1b9f0e6117c95a1a3bbdde66fa6948828e6b&rid=giphy.gif&ct=g'
    error_text = 'Oops! Something went wrong.'
    error_img_url = 'https://media3.giphy.com/media/YDj8Ot6mIbJYs/giphy.gif?cid=ecf05e47fn4ptkyy52ocl3a3h305wyjawoa82snb48ad47br&rid=giphy.gif&ct=g'
    message_template_filepath: str = 'src/word_artist/slack_message_formatting/message_template.json'

    # Public:
    def run(self, event: dict) -> dict | None:
        try:
            response = self.__call_async_generation(event)
            print(f'Async generation response: {response}')
            return self.generate_loading_message()
        except Exception as e:
            logger.error(f'Error: {e}')
            return self.generate_error_message(e)

    def generate_command_message(self, text: str, style: str | None = None) -> dict:
        self.__text = text
        self.__style = style
        self.__generate_image()
        slack_msg = self.__generate_slack_message()
        return slack_msg

    def generate_loading_message(self) -> dict:
        text = self.loading_text
        img_url = self.loading_img_url
        msg = {
            "blocks": [
                {
                    "type": "image",
                    "alt_text": text,
                    "image_url": img_url
                }
            ]
        }
        return msg

    def generate_error_message(self, e: Exception) -> dict:
        msg = {
            "blocks": [
                {
                    "type": "image",
                    "alt_text": self.error_text,
                    "image_url": self.error_img_url
                }
            ]
        }
        if load_env_var('ENV') == 'dev':
            text = str(e)
            msg['blocks'].append({
                "type": "section",
                "text": {
                        "type": "mrkdwn",
                        "text": text
                }
            })
        return msg

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
        template_filepath = self.message_template_filepath
        fields = {
            'img_url': img_url,
            'text': text,
            'style': style
        }
        msg = SlackMessageFormatter(template_filepath).compute(fields)
        return msg
