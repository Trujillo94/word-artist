import pytest
from genericpath import exists
from src.word_artist.word_artist import WordArtist


@pytest.mark.skip(reason='Work in progress')
def test_no_style_word_art_generation() -> None:
    filepath, style = WordArtist().compute('WordArt generation test.', style=None)
    assert filepath is str
    assert style is str
    assert exists(filepath) is True


if __name__ == "__main__":
    test_no_style_word_art_generation()
