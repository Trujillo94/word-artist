from src.word_artist import WordArtist


class SlackWordArtist:

    # Public:
    def __init__(self):
        pass

    def compute(self, text: str, style: str | None = None):
        img_url = WordArtist().compute(text, style=style)
        return img_url
