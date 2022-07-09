import logging
import os
from functools import wraps
from time import time

from src.utils.print_variables_toolbox import make_variable_printable

# logging.basicConfig(level=logging.INFO)
# create logger
logger = logging.getLogger('decorator')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s [%(levelname)s] | %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def log_function_smart(f):
	env = os.getenv('ENVIRONMENT') or 'local'
	if env == 'local':
		return log_function_quiet(f)
	else:
		return log_function_verbose(f)


def log_function_verbose(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		t0 = time()
		name = f.__qualname__
		input_msg = get_input_log_message(args, kwargs)
		started_msg = f'[{name}] | STARTED | {input_msg}'
		logger.info(started_msg)
		try:
			result = f(*args, **kwargs)
			output_msg = get_output_log_message(result)
			finished_msg = f'[{name}] | FINISHED | {output_msg}'
			logger.info(finished_msg)
			return result
		except Exception as e:
			finished_msg = f'[{name}] | FINISHED | EXCEPTION: <{e}>'
			logger.error(
				f'{finished_msg}')
			raise e
		finally:
			t1 = time()
			time_msg = f'[{name}] | PERFORMANCE | ELAPSED_TIME: {round(t1-t0,2)}s'
			logger.info(time_msg)
	return wrapper


def log_function_quiet(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		t0 = time()
		name = f.__qualname__
		started_msg = f'[{name}] | STARTED'
		logger.info(started_msg)
		try:
			result = f(*args, **kwargs)
			t1 = time()
			finished_msg = f'[{name}] | FINISHED | ELAPSED_TIME: {round(t1-t0,2)}s'
			logger.info(finished_msg)
			return result
		except Exception as e:
			finished_msg = f'[{name}] | FINISHED | EXCEPTION: <{e}>'
			logger.error(
				f'{finished_msg}')
			raise e
	return wrapper


def log_exception(name, msg):
	finished_msg = f'[{name}] | RAISED_EXCEPTION: <{msg}>'
	logger.warning(f'{finished_msg}')


def warn_and_continue(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		name = f.__qualname__
		try:
			return f(*args, **kwargs)
		except Exception as e:
			finished_msg = f'[{name}] | FINISHED | EXCEPTION: <{e}>'
			logger.warn(
				f'{finished_msg}')
	return wrapper


def warn_and_continue_verbose(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		t0 = time()
		name = f.__qualname__
		input_msg = get_input_log_message(args, kwargs)
		started_msg = f'[{name}] | STARTED | {input_msg}'
		logger.info(started_msg)
		try:
			result = f(*args, **kwargs)
			output_msg = get_output_log_message(result)
			finished_msg = f'[{name}] | FINISHED | {output_msg}'
			logger.info(finished_msg)
			return result
		except Exception as e:
			finished_msg = f'[{name}] | FINISHED | EXCEPTION: <{e}>'
			logger.warn(
				f'{finished_msg}')
		finally:
			t1 = time()
			time_msg = f'[{name}] | PERFORMANCE | ELAPSED_TIME: {round(t1-t0,2)}s'
			logger.info(time_msg)
	return wrapper


def log_exception(name, msg):
	finished_msg = f'[{name}] | RAISED_EXCEPTION: <{msg}>'
	logger.warning(f'{finished_msg}')


def log_warning(msg):
	logger.warning(f'{msg}')


def log_info(msg):
	logger.info(f'{msg}')


def log_error(msg):
	logger.error(f'{msg}')


def get_input_log_message(args, kwargs):
	printable_args = make_variable_printable(args)
	printable_kwargs = make_variable_printable(kwargs)
	return f'INPUT: ({printable_args}, {printable_kwargs})'


def get_output_log_message(output):
	printable_output = make_variable_printable(output)
	return f'OUTPUT: {printable_output}'
