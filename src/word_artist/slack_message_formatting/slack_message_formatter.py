import os

from src.utils.dict_toolbox import apply_function_to_all_values_of_type
from src.utils.json_toolbox import format_json_template, load_if_json

BUCKET_FOLDER_ROUTE = os.getenv('BUCKET_FOLDER_ROUTE')
BUCKET_URL = os.getenv('BUCKET_URL')

severity_whitelist = ['unknown', 'low']


class SlackMessageFormatter:

    # Public:
    def __init__(self, template_filepath: str) -> None:
        self.template_filepath = template_filepath

    @property
    def template_filepath(self) -> str:
        return self.__template_filepath

    @template_filepath.setter
    def template_filepath(self, filepath: str) -> None:
        self.__template_filepath = filepath
        self.__load_message_template()

    def compute(self, values) -> dict:
        msg = None
        template = self.__template
        msg = apply_function_to_all_values_of_type(
            template, str, lambda s: format_json_template(s, values, ignore_missing_fields=False))
        return msg

    # Private:
    def __load_message_template(self) -> None:
        filepath = self.__template_filepath
        template = load_if_json(filepath)
        self.__template = template
