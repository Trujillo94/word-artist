import string
import unicodedata

import validators
from src.utils.regex_toolbox import is_separator, replace_regex


def get_number_from_string(s):
	try:
		return int(''.join([c for c in s if c.isdigit()]))
	except Exception as e:
		print(f'Cannot get number from strin: {s}. Message: {e}')


def append_prefix_to_strings(ls, prefix):
	return [prefix + s for s in ls]


def remove_word(s, w):
	return s.replace(w, '', 1)


def remove_first_word(s, remove_initial_separators=True):
	w = get_first_word(s)
	s = remove_word(s, w)
	if remove_initial_separators:
		s = remove_starting_separators(s)
	return s


def remove_last_word(s, remove_final_separators=True):
	w = get_last_word(s)
	s = remove_word(s, w)
	if remove_final_separators:
		s = remove_ending_separators(s)
	return s


def remove_starting_separators(s):
	while starts_with_separator(s):
		s = s[1:]
	return s


def remove_ending_separators(s):
	while ends_with_separator(s):
		s = s[:-1]
	return s


def strip_separators(s):
	if len(s) > 0:
		s = remove_starting_separators(s)
	if len(s) > 0:
		s = remove_ending_separators(s)
		return s


def remove_starting_whitespaces(s):
	while s.startswith(' '):
		s = s[1:]
	return s


def remove_ending_whitespaces(s):
	while s.endswith(' '):
		s = s[:-1]
	return s


def remove_whitespaces(s):
	return s.replace(' ', '')


def remove_double_whitespaces(s):
	while '  ' in s:
		s = s.replace('  ', ' ')
	return s


def starts_with_separator(s):
	if len(s) > 0:
		return is_separator(s[0])
	else:
		return False


def ends_with_separator(s):
	if len(s) > 0:
		return is_separator(s[-1])
	else:
		return False


def is_url(s):
	return not not validators.url(s)


def make_single_whitespaces(s):
	return replace_regex(s, ['\s+'], ' ', whole_word=False, replace_all=True)


def make_single_line(s):
	s = s.replace('-\n', '')
	s = s.replace('\n', ' ')
	s = make_single_whitespaces(s)
	s = s.lstrip()
	s = s.rstrip()
	return s


def remove_ending_whitespaces(s):
	while s.endswith(' '):
		s = s[:-1]
	return s


def normalize(s, form='NFKC'):
	return unicodedata.normalize(form, s)


def remove_punctuation(s):
	return s.translate(str.maketrans('', '', string.punctuation))


def remove_whitespaces(s):
	return s.replace(' ', '')


def get_first_word(s):
	if type(s) is str:
		words = s.split()
		if len(words) > 0:
			return words[0]
	return s


def get_last_word(s):
	if type(s) is str:
		words = s.split()
		if len(words) > 0:
			return words[-1]
	return s


def count_words(s):
	return len(s.split())


def convert_to_snake_case(s):
	if len(s) > 1:
		s = s.replace(' ', '_')
		s = s[0].lower() + s[1:]
		s = ''.join([f'_{c.lower()}' if c.isupper() else c for c in s])
	else:
		s = s.lower()
	return s


def convert_to_normal_case(s):
	s = ''.join(map(lambda c: f' {c}' if c.isupper()
				or c == '-' or c == '_' else c, s))
	s = s.strip()
	s = remove_double_whitespaces(s)
	return s


def convert_to_kebab_case(s):
	s = convert_to_normal_case(s)
	return s.lower().replace(' ', '-')


def convert_to_screaming_kebab_case(s):
	s = convert_to_normal_case(s)
	return s.upper().replace(' ', '-')


def copy_case(s, ref):
	if type(s) is not str and type(ref) is not ref:
		raise TypeError('Both input arguments must be strings.')
	if len(s) > 0 and len(ref) > 0:
		if ref.isupper():
			return s.upper()
		elif ref.islower():
			return s.lower()
		elif ref[0].isupper():
			return s.capitalize()
	return s


def get_class_name(obj):
	name = str(obj.__class__)
	name = name.split("'>")[0]
	name = name.split('.')[-1]
	return name
