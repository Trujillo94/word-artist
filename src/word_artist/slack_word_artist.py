from src.config.aws import BUCKET_NAME
from src.utils.files_management_toolbox import get_extension
from src.utils.string_toolbox import convert_to_kebab_case
from src.word_artist.slack_message_formatting.slack_message_formatter import \
    SlackMessageFormatter
from src.word_artist.word_artist import WordArtist
from src.wrappers.aws.s3 import S3Wrapper


class SlackWordArtist:

    # Public:
    def __init__(self):
        pass

    def run(self, text: str, style: str | None = None):
        self.__generate_image(text, style=style)
        self.__upload_image()
        slack_msg = self.__generate_slack_message()
        return slack_msg

    # Private:
    def __generate_image(self, text: str, style: str | None):
        # img_filepath, style = WordArtist().compute(text, style=style)
        img_filepath = 'media/wordartist_scheme.png'
        style = 'hehe'
        self.__img_filepath = img_filepath
        self.__text = text
        self.__style = style

    def __upload_image(self):
        img_filepath = self.__img_filepath
        style = self.__style
        text = self.__text
        bucket_route = self.__compute_bucket_route(text, style, img_filepath)
        img_url = S3Wrapper().upload_file(BUCKET_NAME, img_filepath,
                                          bucket_route, extra_args={'ACL': 'public-read'})
        self.__img_url = img_url

    def __generate_slack_message(self):
        img_url = self.__img_url
        text = self.__text
        msg = SlackMessageFormatter().compute(img_url, text=text)
        return msg

    def __compute_bucket_route(self, text: str, style: str, filepath: str):
        ext = get_extension(filepath)
        bucket_route = convert_to_kebab_case(f'{text}-{style}{ext}')
        return bucket_route
