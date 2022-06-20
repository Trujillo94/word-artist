from random import choice

from selenium.webdriver.common.keys import Keys
from src.utils.files_management_toolbox import get_extension
from src.utils.selenium_toolbox import AbstractSeleniumCrawler
from src.utils.string_toolbox import convert_to_kebab_case
from src.utils.vartypes_toolbox import check_type


class MakeArtWordCrawler(AbstractSeleniumCrawler):

    _url = 'https://www.makewordart.com/'

    # Public:
    def compute(self, text: str, style: str):
        check_type(text, str)
        check_type(style, [str, None])
        self.__text = text
        self.__style = style
        self.__click_style()
        self.__type_text()
        self.__download_image()
        filepath = self.move_last_downloaded_file()
        return filepath

    # Protected:
    def _get_new_filename(self, old_filepath: str):
        ext = get_extension(old_filepath).replace('.', '')
        text = self.__text
        style = self.__style
        new_filename = f'{convert_to_kebab_case(text)}_{convert_to_kebab_case(style)}.{ext}'
        return new_filename

    # Private:
    def __click_style(self):
        style = self.__style
        styles_div = self.get_element_by_class_name(style)
        style_element = styles_div.find_element_by_xpath(
            f'//div[contains(@class, "sprite {style}")]')
        style_element.click()

    def __type_text(self):
        text = self.__text
        text_input = self.get_element_by_id('text-input')
        text_input.send_keys(text)
        text_input.send_keys(Keys.ENTER)

    def __download_image(self):
        xpath = f'//button [contains(text(), "Download")]'
        download_button = self.get_element_by_xpath(xpath)
        download_button.click()
