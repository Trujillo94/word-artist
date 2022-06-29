import logging
import traceback

from botocore.exceptions import ClientError
from slack_sdk.errors import SlackClientError
from src.utils.exception import GenericException, error_handling

logger = logging.getLogger("wrappers.slack.exception")


class SlackException(GenericException):

    @classmethod
    @error_handling
    def error_handling(cls, function):
        """
        Expands the error_handing found in utils/exception.py to handle ClientError
        and log them as an error with the Boto3 session.
        """

        def wrapper(*args, **kwargs):

            try:
                return function(*args, **kwargs)
            except ClientError as e:
                msg = f"'{function.__name__}' - Slack error: '{e}'"
                stack_trace = traceback.format_exc()
                logger.error(f"{msg} - Stack trace: '{stack_trace}'")
                raise SlackClientError(msg) from e

        wrapper.__name__ = function.__name__
        return wrapper
