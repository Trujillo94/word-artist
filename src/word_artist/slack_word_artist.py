from dataclasses import dataclass

from src.config.aws import BUCKET_NAME
from src.utils.files_management_toolbox import get_extension
from src.utils.string_toolbox import convert_to_kebab_case
from src.utils.toolbox import load_env_var
from src.word_artist.slack_message_formatting.slack_message_formatter import \
    SlackMessageFormatter
from src.wrappers.aws.s3 import S3Wrapper


@dataclass
class SlackWordArtist:

    loading_text: str = 'Generating a fabulous WordArt...'
    loading_img_url: str = 'https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif'
    error_text = 'Oops! Something went wrong.'
    error_img_url = 'https://media3.giphy.com/media/YDj8Ot6mIbJYs/giphy.gif?cid=ecf05e47fn4ptkyy52ocl3a3h305wyjawoa82snb48ad47br&rid=giphy.gif&ct=g'
    message_template_filepath: str = 'src/word_artist/slack_message_formatting/message_template.json'

    # Public:
    def run(self, text: str, style: str | None = None) -> dict:
        self.__generate_image(text, style=style)
        self.__upload_image()
        slack_msg = self.__generate_slack_message()
        return slack_msg

    def compute_loading_message(self) -> dict:
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

    def compute_error_message(self, e: Exception) -> dict:
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
    def __generate_image(self, text: str, style: str | None) -> None:
        # img_filepath, style = WordArtist().compute(text, style=style)
        img_filepath = 'media/wordartist_scheme.png'
        style = 'hehe'
        self.__img_filepath = img_filepath
        self.__text = text
        self.__style = style

    def __upload_image(self) -> None:
        img_filepath = self.__img_filepath
        style = self.__style
        text = self.__text
        bucket_route = self.__compute_bucket_route(text, style, img_filepath)
        img_url = S3Wrapper().upload_file(BUCKET_NAME, img_filepath,
                                          bucket_route, extra_args={'ACL': 'public-read'})
        self.__img_url = img_url

    def __generate_slack_message(self) -> dict:
        img_url = self.__img_url
        text = self.__text
        template_filepath = self.message_template_filepath
        fields = {
            'img_url': img_url,
            'text': text
        }
        msg = SlackMessageFormatter(template_filepath).compute(fields)
        return msg

    def __compute_bucket_route(self, text: str, style: str, filepath: str) -> str:
        ext = get_extension(filepath)
        bucket_route = convert_to_kebab_case(f'{text}-{style}{ext}')
        return bucket_route
