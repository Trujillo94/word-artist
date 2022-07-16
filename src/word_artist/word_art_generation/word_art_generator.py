from enum import Enum
from random import choice

from src.config.aws import BUCKET_NAME
from src.crawlers.make_word_art_crawler import MakeArtWordCrawler
from src.utils.files_management_toolbox import get_extension
from src.utils.string_toolbox import convert_to_kebab_case
from src.utils.vartypes_toolbox import check_type
from src.word_artist.word_art_generation.word_art_generator_strategies import \
    WordArtGenerationStrategy
from src.wrappers.aws.s3 import S3Wrapper


class WordArtGenerator:

    __styles = ['blues', 'rainbow', 'superhero', 'outline', 'arc', 'sunset', 'horizon', 'purple',
                'green-marble', 'marble-slab', 'gray-block', 'up', 'red-blue', 'aqua', 'italic-outline']

    # Public:
    def __init__(self,
                 strategy: WordArtGenerationStrategy = WordArtGenerationStrategy.MOCK_WORD_ART):
        self.__strategy = strategy

    def compute(self, text: str, style: str | None = None) -> str:
        check_type(text, str)
        check_type(style, [str, None])
        self.__text = text
        self.__style = style
        self.__format_style()
        self.__generate_image()
        self.__upload_image()
        return self.__img_url

    # Private:
    def __generate_image(self) -> None:
        text = self.__text
        style = self.__style
        generator = self.__create_generator()
        img_filepath = generator(text, style)
        self.__img_filepath = img_filepath

    def __upload_image(self) -> None:
        img_filepath = self.__img_filepath
        style = self.__style
        text = self.__text
        bucket_route = self.__compute_bucket_route(text, style, img_filepath)
        img_url = S3Wrapper().upload_file(BUCKET_NAME, img_filepath,
                                          bucket_route, extra_args={'ACL': 'public-read'})
        self.__img_url = img_url

    def __compute_bucket_route(self, text: str, style: str, filepath: str) -> str:
        ext = get_extension(filepath)
        bucket_route = convert_to_kebab_case(f'{text}-{style}{ext}')
        return bucket_route

    def __download_word_art_by_makeartword(self, text: str, style: str) -> str:
        return MakeArtWordCrawler().compute(text, style)

    def __format_style(self) -> None:
        style = self.__style
        if style is None:
            style = self.__get_random_style()
        elif type(style) is str:
            style = convert_to_kebab_case(style)
        else:
            raise TypeError(
                'Keyworded argument <style> cannot be of type <{type(style)}>. Valid types are <None> and <str>.')

    def __get_random_style(self) -> str:
        styles = self.__styles
        style = choice(styles)
        return style

    def __create_generator(self):
        strategy = self.__strategy
        match strategy:
            case WordArtGenerationStrategy.MAKE_WORD_ART_DOWNLOAD:
                return self.__download_word_art_by_makeartword
            case WordArtGenerationStrategy.MOCK_WORD_ART:
                return lambda text, style: 'media/wordartist_scheme.png'
            case _:
                raise ValueError(f'Unknown strategy: {strategy}')
