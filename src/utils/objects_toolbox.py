from copy import deepcopy
import json

from src.utils.dict_toolbox import filter_dictionary, transform_dictionary
from src.utils.list_toolbox import filter_list, transform_list
from src.utils.tuples_toolbox import filter_tuple, transform_tuple


def get_state(obj, recursive=False, ignore_non_serializable=False):
	state = None
	try:
		state = deepcopy(obj.__dict__)
	except:
		if is_builtin_type(obj):
			state = obj
		else:
			props = dir(obj)
			state = {}
			for prop in props:
				value = getattr(obj, prop)
				if not recursive or is_builtin_type(value):
					state[prop] = value
				else:
					if ignore_non_serializable:
						try:
							state[prop] = deepcopy(value.__dict__)
						except:
							pass
					else:
						state[prop] = get_state(
							value, ignore_non_serializable=True)
	return state


def get_objects_from_list_by_attribute_values(ls, attribute, values):
	return list(filter(lambda o: getattr(o, attribute) in values, ls))


def is_builtin_type(a):
	return type(a) is int or type(a) is str or type(a) is float or type(a) is bytes or type(a) is list or type(a) is dict or type(a) is tuple or type(a) is set or type(a) is bool or a is None


def is_iterable(a):
	try:
		iter(a)
		return True
	except TypeError as te:
		return False


def is_array(a):
	return type(a) is list or type(a) is set or type(a) is tuple or type(a) is dict


def remove_non_serializable_elements(a, recursive=False):

	def is_serializable(e):
		try:
			json.dumps(e)
			return True
		except:
			return False
	return remove_data_structure(a, is_serializable, recursive=recursive)


def remove_elements_of_type(a, _type, recursive=False):

	def f(e): return type(e) is not _type
	return remove_data_structure(a, f, recursive=recursive)


def replace_objects_by_object_states(a):
	if type(a) is list:
		return transform_list(a, replace_objects_by_object_states)
	elif type(a) is tuple:
		return transform_tuple(a, replace_objects_by_object_states)
	elif type(a) is dict:
		return transform_dictionary(a, replace_objects_by_object_states)
	elif '<class ' in str(type(a)):
		return get_state(a)
	else:
		return a


def transform_data_structure(a, f, recursive=False):
	if recursive:
		def g(a): return transform_data_structure(a, f, recursive=True)
	else:
		g = f
	if type(a) is list:
		return transform_list(a, g)
	elif type(a) is tuple:
		return transform_tuple(a, g)
	elif type(a) is dict:
		return transform_dictionary(a, g)
	elif is_iterable(a) and type(a) is not str:
		# !! ASSUMING THAT WOULD BE ITERABLE AS A DICT !!
		return transform_dictionary(a, g)
	else:
		return f(a)


def remove_data_structure(a, f, recursive=False):
	if is_iterable(a):
		def g(a):
			if is_iterable(a):
				return True
			else:
				return f(a)
		b = filter_data_structure(a, g, recursive=False)
		def h(a): return remove_data_structure(a, f, recursive=recursive)
		c = transform_data_structure(b, h, recursive=False)
		return c
	else:
		return a


def filter_data_structure(a, f, recursive=False):
	if recursive:
		def g(a): return filter_data_structure(a, f, recursive=True)
	else:
		g = f
	if type(a) is list:
		return filter_list(a, g)
	elif type(a) is tuple:
		return filter_tuple(a, g)
	elif type(a) is dict:
		return filter_dictionary(a, g)
	elif is_iterable(a) and type(a) is not str:
		# !! ASSUMING THAT WOULD BE ITERABLE AS A DICT !!
		return filter_dictionary(a, g)
	else:
		return f(a)


def replace_objects_in_list_by_object_states(ls):
	a = []
	for e in ls:
		e = replace_objects_by_object_states(e)
		a.append(e)
	return a


def replace_objects_in_tuple_by_object_states(t):
	a = tuple()
	for e in t:
		e = replace_objects_by_object_states(e)
		a += (e,)
	return a


def replace_objects_in_dictionary_by_object_states(d):
	a = tuple()
	for key, value in d.items():
		value = replace_objects_by_object_states(value)
		a[key] = value
	return a
