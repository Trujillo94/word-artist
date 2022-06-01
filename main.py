import logging

from src.word_artist import WordArtist

logger = logging.getLogger("main")


def handler(event, context):
	text = event['text']
	style = event['style']
	WordArtist().compute(text, style=style)
	logger.info("Successful execution")


if __name__ == "__main__":
	handler({}, {})
