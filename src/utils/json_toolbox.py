import json

from src.utils.string_toolbox import get_substrings_between_curly_braces


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


def format_json_template(s: str, values: dict, ignore_missing_fields=False) -> str:
    try:
        return s.format(**values)
    except KeyError:
        if ignore_missing_fields:
            return s
        else:
            missing_fields = get_substrings_between_curly_braces(s)
            raise Exception(
                f'Missing field in message template: {missing_fields}')
