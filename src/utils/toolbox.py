import json
import logging
import os
from time import sleep
from typing import Any, Callable

from src.utils.logging_toolbox import log_warning

logger = logging.getLogger("Toolbox")


def load_env_var(key: str) -> str | None:
    """
    Returns the value of the environment variable or None if not found.

    :param key: Environment variable key
    :return: The environment variable value, or None
    """
    value = os.environ.get(key)

    if value is None:
        logger.warning(f"Environment variable '{key}' not found.")
    return value


def load_json_file(json_file_path):
    """
    Loads a JSON file content into a dict object.
    :param json_file_path: path to the JSON file
    :return: The dict object with the JSON content
    """

    with open(json_file_path, "r") as json_file:
        content = json.load(json_file)

    return content


def retry_function(f: Callable, *args, max_attempts: int = 20, wait_time: int = 3, ignored_exceptions: list[Exception] = list(), **kwargs) -> Any:
    for i in range(0, max_attempts):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            for ignored_exception in ignored_exceptions:
                if type(e) is ignored_exception:
                    raise e
            log_warning(
                f'Failed execution of {f.__qualname__}. Attempt: {i+1}/{max_attempts}. DETAILS: <{str(e)}>')
            if i+1 < max_attempts:
                sleep(wait_time)
            else:
                raise e
    raise Exception(
        f"Failed to execute {f.__qualname__} after {max_attempts} attempts.")
