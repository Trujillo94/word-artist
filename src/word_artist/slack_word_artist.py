import logging

from src.word_artist.event_types import Event, get_event_type
from src.word_artist.interactivity.slack_command_handler import \
    SlackCommandHandler
from src.word_artist.interactivity.slack_interactivity_handler import \
    SlackInteractivityHandler

logger = logging.getLogger("src.word_artist")


class SlackWordArtist:

    # Public:
    def run(self, event: dict) -> dict | None:
        self.__event_type = get_event_type(event)
        if self.__event_type == Event.TEXT_COMMAND:
            return SlackCommandHandler().run(event)
        else:
            return SlackInteractivityHandler().run(event)

    # Private:
