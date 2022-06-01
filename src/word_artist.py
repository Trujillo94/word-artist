from src.crawlers.make_word_art_crawler import MakeArtWordCrawler
from src.utils.vartypes_toolbox import check_type


class WordArtist:

    # Public:
    def compute(self, text: str, style=None):
        check_type(text, str)
        check_type(style, [str, None])
        img_filepath = self.__download_word_art_by_makeartword(text, style)
        return img_filepath

    def __download_word_art_by_makeartword(self, text, style=None):
        return MakeArtWordCrawler().compute(text, style=style)
