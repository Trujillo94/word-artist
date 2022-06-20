import json


def load_json(filepath):
	with open(filepath) as f:
		data = json.load(f)
	return data


def load_if_json(filepath):
	if type(filepath) is str:
		if filepath.endswith('.json'):
			data = load_json(filepath)
			return data
	return filepath


def export_json(filepath, data):
	with open(filepath, 'w') as f:
		string = json.dumps(data, indent=4)
		f.write(string)
