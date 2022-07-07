from random import choice

from src.crawlers.make_word_art_crawler import MakeArtWordCrawler
from src.utils.string_toolbox import convert_to_kebab_case
from src.utils.vartypes_toolbox import check_type


class WordArtist:

    __styles = ['blues', 'rainbow', 'superhero', 'outline', 'arc', 'sunset', 'horizon', 'purple',
                'green-marble', 'marble-slab', 'gray-block', 'up', 'red-blue', 'aqua', 'italic-outline']

    # Public:
    def compute(self, text: str, style: str | None = None) -> tuple[str, str]:
        check_type(text, str)
        check_type(style, [str, None])
        if style is None:
            style = self.__get_random_style()
        elif type(style) is str:
            style = convert_to_kebab_case(style)
        else:
            raise TypeError(
                'Keyworded argument <style> cannot be of type <{type(style)}>. Valid types are <None> and <str>.')
        img_filepath = self.__download_word_art_by_makeartword(text, style)
        return img_filepath, style

        # Private:
    def __download_word_art_by_makeartword(self, text: str, style: str) -> str:
        return MakeArtWordCrawler().compute(text, style)

    def __get_random_style(self) -> str:
        styles = self.__styles
        style = choice(styles)
        return style
