import os

from src.utils.dict_toolbox import apply_function_to_all_values_of_type
from src.utils.json_toolbox import load_if_json

BUCKET_FOLDER_ROUTE = os.getenv('BUCKET_FOLDER_ROUTE')
BUCKET_URL = os.getenv('BUCKET_URL')

severity_whitelist = ['unknown', 'low']


class SlackMessageFormatter:

    __template_filepath = 'src/word_artist/slack_message_formatting/message_template.json'

    # Public:

    def __init__(self):
        self.__load_message_template()

    def compute(self, img_url: str):
        msg = None
        template = self.__template
        img_name = 'Your Amazing WordArt.'
        msg = apply_function_to_all_values_of_type(
            template, str, lambda s: s.format(img_url=img_url, img_name=img_name))
        return msg

    # Private:
    def __load_message_template(self):
        filepath = self.__template_filepath
        template = load_if_json(filepath)
        self.__template = template
