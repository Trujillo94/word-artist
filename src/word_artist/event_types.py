from enum import Enum, auto


class Event(Enum):
    TEXT_COMMAND = auto()
    ASYNC_GENERATION = auto()
    BUTTON_ACTION = auto()


def get_event_type(event: dict) -> Event:
    if 'text' in event:
        return Event.TEXT_COMMAND
    elif 'type' in event:
        match event['type']:
            case 'ASYNC_GENERATION':
                return Event.ASYNC_GENERATION
            case _:
                raise Exception(f'Invalid event. Event: <{event}>')
    elif 'payload' in event:
        return Event.BUTTON_ACTION
    else:
        raise Exception(f'Invalid event. Event: <{event}>')
