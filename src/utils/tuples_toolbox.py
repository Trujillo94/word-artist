def transform_tuple(t, f):
	return tuple(map(f, t))


def filter_tuple(t, f):
	return tuple(filter(f, t))
