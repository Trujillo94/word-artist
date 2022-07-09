from functools import wraps
from time import sleep, time

from src.utils.logging_toolbox import log_exception as real_log_exception
from src.utils.logging_toolbox import \
    log_function_quiet as real_log_function_quiet
from src.utils.logging_toolbox import \
    log_function_smart as real_log_function_smart
from src.utils.logging_toolbox import \
    log_function_verbose as real_log_function_verbose
from src.utils.logging_toolbox import log_warning
from src.utils.logging_toolbox import \
    warn_and_continue as real_warn_and_continue
from src.utils.logging_toolbox import \
    warn_and_continue_verbose as real_warn_and_continue_verbose


def timing(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        name = f.__qualname__
        t0 = time()
        result = f(*args, **kwargs)
        t1 = time()
        print(f'{name} - elapsed time: {round(t1-t0, 2)}s.')
        return result
    return wrapper


def log_function_smart(*args, **kwargs):
    return real_log_function_smart(*args, **kwargs)


def log_function_verbose(*args, **kwargs):
    return real_log_function_verbose(*args, **kwargs)


def log_function_quiet(*args, **kwargs):
    return real_log_function_quiet(*args, **kwargs)


def log_exception(*args, **kwargs):
    return real_log_exception(*args, **kwargs)


def warn_and_continue(*args, **kwargs):
    return real_warn_and_continue(*args, **kwargs)


def warn_and_continue_verbose(*args, **kwargs):
    return real_warn_and_continue_verbose(*args, **kwargs)


def retry(*args, n_attempts=3, wait_time=60, ignored_exceptions=[], **kwargs):
    def wrapper(f):
        def retry_function(*args, **kwargs):
            for i in range(0, n_attempts):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    for ignored_exception in ignored_exceptions:
                        if type(e) is ignored_exception:
                            raise e
                    log_warning(
                        f'Failed execution of {f.__qualname__}. Attempt: {i+1}/{n_attempts}. DETAILS: <{str(e)}>')
                    if i+1 < n_attempts:
                        sleep(wait_time)
                    else:
                        raise e
        return retry_function
    return wrapper


def print_function(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        name = f.__qualname__
        print(name)
        return f(*args, **kwargs)
    return wrapper
