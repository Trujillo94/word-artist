import pytest
from genericpath import exists
from src.word_artist.word_art_generation.word_art_generator import \
    WordArtGenerator


@pytest.mark.skip(reason='Work in progress')
def test_no_style_word_art_generation() -> None:
    filepath = WordArtGenerator().compute(
        'WordArt generation test.', style=None)
    assert type(filepath) is str
    assert exists(filepath) is True


if __name__ == "__main__":
    test_no_style_word_art_generation()
