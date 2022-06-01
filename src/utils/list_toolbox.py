from difflib import SequenceMatcher
import json


def intersect_lists(ls1, ls2):
	if not len(ls1) or not len(ls2):
		return ls1
	try:
		return list(set(ls1) & set(ls2))
	except Exception as e:
		msg = str(e)
		if 'unhashable type' in msg.lower() and type(ls1[0]) is dict and type(ls2[0]) is dict:
			ls1 = list(map(json.dumps, ls1))
			s1 = set(ls1)
			ls2 = list(map(json.dumps, ls2))
			s2 = set(ls2)
			s = s1 & s2
			ls = list(map(json.loads, s))
			return ls
		else:
			raise e


def diff_lists(ls1, ls2):
	common = intersect_lists(ls1, ls2)
	return list(filter(lambda e: e not in common, make_unique(ls1+ls2)))


def get_element_index(ls, element):
	index = [i for i, e in enumerate(ls) if element == e][0]
	return index


def get_element_indices(ls, element):
	return [i for i, e in enumerate(ls) if e == element]


def get_elements_by_indices(ls, indices):
	elements = []
	[elements.append(ls[i]) for i in indices]
	return elements


def get_elements_except_indices(ls, indices):
	elements = []
	for i, element in enumerate(ls):
		if i not in indices:
			elements.append(element)
	return elements


def get_element_by_type(ls, _type, index=0):
	matches = get_elements_by_type(ls, _type)
	if len(matches) > index or index == -1:
		return matches[index]
	else:
		return None


def get_elements_by_type(ls, _type):
	return list(filter(lambda e: type(e) is _type, ls))


def is_list_of_type(ls, _type):
	if type(ls) is list and len(ls) > 0:
		types = get_list_element_types(ls)
		return all(list(map(lambda t: t is _type, types)))


def get_list_element_types(ls):
	return list(map(type, ls))


def remove_nones(ls):
	return list(filter(lambda e: e is not None, ls))


def remove_empty(ls):
	ls = remove_nones(ls)
	return list(filter(lambda e: len(e) > 0 if (type(e) is str or type(e) is list or type(e) is dict or type(e) is tuple or type(e) is set) else True, ls))


def make_unique(ls):
	if len(ls) > 0:
		try:
			ls = list(set(ls))
		except Exception as e:
			msg = str(e)
			if 'unhashable type' in msg.lower() and type(ls[0]) is dict:
				ls = list(map(json.dumps, ls))
				ls = list(set(ls))
				ls = list(map(json.loads, ls))
				# ls = [dict(s) for s in set(frozenset(d.items()) for d in ls)]
			else:
				raise e
	return ls


def sort_list(ls):
	try:
		ls.sort()
	except Exception as e:
		msg = str(e)
		if 'not supported between instances of ' in msg.lower():
			pass
		else:
			raise e
	return ls


def get_most_repeated_element(ls):
	unique_elements = list(set(ls))
	repetions = list(map(lambda e: (e, ls.count(e)), unique_elements))
	_, counts = list(zip(*repetions))
	n = max(counts)
	t = list(filter(lambda t: t[1] == n, repetions))[0]
	return t[0]


def sort_strings_by_similarity(ls, string):
	def compute_similarity(ref):
		return SequenceMatcher(None, string, ref).ratio()
	sorted_values = sorted(ls, key=compute_similarity, reverse=True)
	return sorted_values


def find_most_similar_string(ls, string):
	if string in ls:
		match = string
	else:
		sorted_values = sort_strings_by_similarity(ls, string)
		match = sorted_values[0]
	return match


def get_string_in_list_by_substring(ls, substring):
	pass


def transform_list(ls, f):
	return list(map(f, ls))


def filter_list(ls, f):
	return list(filter(f, ls))


def get_first_element(ls):
	if len(ls) > 0:
		return ls[0]
	else:
		return None


def get_first_match(f, ls):
	matches = list(filter(f, ls))
	if len(matches) > 0:
		return matches[0]
	else:
		return None


def get_list_missing_elements(ls, reference):
	return [e for e in reference if e not in ls]


def find_duplicates_indices(ls):
	indices = []
	counted_elements = []
	for i, e in enumerate(ls):
		if e not in counted_elements:
			idxs = get_element_indices(ls, e)
			counted_elements.append(e)
			if len(idxs) > 1:
				indices.append(idxs)
	return indices


def find_uniques_indices(ls):
	return [i for i, e in enumerate(ls) if len(get_element_indices(ls, e)) == 1]


def unpack_list_of_lists(ls):
	new_ls = []
	list(map(lambda e: new_ls.extend(e) if type(
		e) is list else new_ls.append(e), ls))
	return new_ls


def get_list_missing_elements(ls, reference):
	return [e for e in reference if e not in ls]


def create_list_from_elements_count(elements_count):
	ls = []
	for element, n in elements_count:
		ls += create_list_of_duplicated_elements(element, n)
	return ls


def create_list_of_duplicated_elements(element, n):
	ls = []
	for i in range(0, n):
		ls.append(element)
	return ls
