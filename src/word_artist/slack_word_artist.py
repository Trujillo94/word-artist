from src.utils.files_management_toolbox import get_extension
from src.utils.s3_toolbox import upload
from src.utils.string_toolbox import convert_to_kebab_case
from src.word_artist.word_artist import WordArtist


class SlackWordArtist:

    # Public:
    def __init__(self):
        pass

    def compute(self, text: str, style: str | None = None):
        # img_filepath, style = WordArtist().compute(text, style=style)
        img_filepath = 'media/wordartist_scheme.png'
        style = 'mock'
        bucket_route = self.__compute_bucket_route(text, style, img_filepath)
        img_url = upload(img_filepath, bucket_route,
                         extra_args={'ACL': 'public-read'})
        return img_url

    def __compute_bucket_route(self, text: str, style: str, filepath: str):
        ext = get_extension(filepath)
        bucket_route = convert_to_kebab_case(f'{text}-{style}{ext}')
        return bucket_route
