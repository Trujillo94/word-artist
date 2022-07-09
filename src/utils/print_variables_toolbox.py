from src.utils.objects_toolbox import remove_non_serializable_elements


def make_variables_list_printable(ls):
	new_ls = []
	for obj in ls:
		new_obj = make_variable_printable(obj)
		new_ls.append(new_obj)
	return new_ls


def make_variables_dict_printable(d):
	new_dict = {}
	for key, value in d.items():
		new_value = make_variable_printable(value)
		new_dict[key] = new_value
	return new_dict


def make_variable_printable(var):
	# var = remove_non_serializable_elements(var, recursive=True)
	if type(var) is list or type(var) is tuple or type(var) is set:
		var = make_variables_list_printable(var)
	elif type(var) is dict:
		var = make_variables_dict_printable(var)
	else:
		try:
			var = vars(var)
		except:
			pass
	return var
