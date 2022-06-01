def remove_elements_in_blocklist(ls, i, blocklist):
	return list(filter(lambda t: t[i] not in blocklist, ls))


def remove_elements_not_in_allowlist(ls, i, allowlist):
	return list(filter(lambda t: t[i] in allowlist, ls))


def filter_column(ls, i, f):
	return list(filter(lambda t: f(t[i]), ls))


def get_column_as_list(ls, i):
	return list(map(lambda t: t[i], ls))


def transform_column(ls, i, f):
	return list(map(lambda t: t[:i]+(f(t[i]),)+t[i+1:],ls))
