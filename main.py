import logging

from src.word_artist.slack_word_artist import SlackWordArtist

logger = logging.getLogger("main")


def handler(event: dict, context: dict) -> dict | None:
    # print(event)
    print(f'event: {event}')
    print(f'context: {context}')
    response = SlackWordArtist().run(event)
    print("Successful execution")
    return response


if __name__ == "__main__":
    event = {
        "text": "Hello World"
    }
    response = handler(event, {})
    print(response)
