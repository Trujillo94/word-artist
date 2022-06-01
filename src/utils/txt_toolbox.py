def load_text(filepath):
	with open(filepath, 'r') as f:
		data = f.read()
	return data


def load_text_as_list(filepath, separator='\n'):
	raw_data = load_text(filepath)
	return raw_data.split(separator)


def save_file(filepath, content):
	with open(filepath, 'w') as f:
		f.write(content)
