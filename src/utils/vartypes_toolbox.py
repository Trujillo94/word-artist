def check_type(value, expected_type):
	if type(expected_type) is list:
		expected_type = list(map(lambda t: t if t is not None else type(None), expected_type))
		if type(value) not in expected_type:
			raise TypeError(f"Expected {expected_type}, got {type(value)}")
	else:
		if not isinstance(value, expected_type):
			raise TypeError(f"Expected {expected_type}, got {type(value)}")
