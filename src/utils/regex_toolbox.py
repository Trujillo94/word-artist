import re
import string
from difflib import SequenceMatcher

from src.utils.list_toolbox import (create_list_from_elements_count,
                                    get_elements_by_indices, remove_empty,
                                    remove_nones)
from src.utils.tuples_list_toolbox import filter_column, get_column_as_list
from src.utils.txt_toolbox import load_text
from text_to_num import alpha2digit


def get_first_element_from_list_matching_regexs(ls, regexs, ignore_case=False, whole_word=False):
    try:
        return next(s for s in ls if matches_any_regex(s, regexs, ignore_case=ignore_case, whole_word=whole_word))
    except StopIteration as e:
        return None
    except Exception as e:
        raise e


def remove_elements_from_list_matching_regexs(ls, regexs, ignore_case=False, whole_word=False):
    def f(s): return not matches_any_regex(
        s, regexs, ignore_case=ignore_case, whole_word=whole_word)
    return list(filter(f, ls))


def remove_elements_from_tuples_list_matching_regexs(ls, i, regexs, ignore_case=False, whole_word=False):
    def f(s): return not matches_any_regex(
        s, regexs, ignore_case=ignore_case, whole_word=whole_word)
    return filter_column(ls, i, f)


def remove_elements_from_list_not_matching_regexs(ls, regexs, ignore_case=False, whole_word=False):
    def f(s): return matches_any_regex(
        s, regexs, ignore_case=ignore_case, whole_word=whole_word)
    return list(filter(f, ls))


def remove_elements_from_tuples_list_not_matching_regexs(ls, i, regexs, ignore_case=False, whole_word=False):
    def f(s): return matches_any_regex(
        s, regexs, ignore_case=ignore_case, whole_word=whole_word)
    return filter_column(ls, i, f)


def remove_terms_not_in_text(text, terms, ignore_case=False):
    return list(filter(lambda term: contains_regex(text, make_literal(term.replace(' ', '\s')), ignore_case=ignore_case), terms))


def list_terms_matches(text, terms, ignore_case=False):
    terms_count = count_terms_matches(text, terms, ignore_case=ignore_case)
    ls = create_list_from_elements_count(terms_count)
    return ls


def count_terms_matches(text, terms, ignore_case=False):
    terms_count = []
    for term in terms:
        n = count_matches(text, make_literal(
            term.replace(' ', '\s')), ignore_case=ignore_case)
        terms_count.append((term, n))
    return terms_count


def count_matches(s, regexs, ignore_case=False):
    return len(get_all_matches(s, regexs, ignore_case=ignore_case))


def get_all_matches(s, regexs, ignore_case=False):
    if ignore_case:
        flags = re.MULTILINE | re.IGNORECASE
    else:
        flags = re.MULTILINE
    if type(regexs) is str:
        regexs = [regexs]
    matches = []
    for regex in regexs:
        matches += re.findall(regex, s, flags=flags)
    return matches


def get_lines_indices_containing_literal(s, literal, ignore_case=False, whole_word=False):
    matches = get_lines_containing_literal(
        s, literal, ignore_case=ignore_case, whole_word=whole_word, number_lines=True)
    return [t[0] for t in matches]


def get_lines_containing_literal(s, literal, ignore_case=False, whole_word=False, number_lines=False):
    literal = make_literal(literal)
    return get_lines_containing_regex(s, literal, ignore_case=ignore_case, whole_word=whole_word, number_lines=number_lines)


def get_lines_containing_regex(s, regexs, ignore_case=False, whole_word=False, number_lines=False):
    if ignore_case:
        flags = re.MULTILINE | re.IGNORECASE
    else:
        flags = re.MULTILINE
    if type(regexs) is str:
        regexs = [regexs]
    matches = []
    lines = s.splitlines()
    for i, line in enumerate(lines):
        if matches_any_regex(line, regexs, ignore_case=ignore_case, whole_word=whole_word):
            if number_lines:
                matches.append((i, line))
            else:
                matches.append(line)
    return matches


def get_lines_from_indices(s, indices):
    lines = s.splitlines()
    return get_elements_by_indices(lines, indices)


def get_all_lines_matching_regexs(s, regexs, ignore_case=False):
    if type(regexs) is str:
        regexs = [regexs]
    matches = []
    lines = s.splitlines()
    # matches = list(filter(lambda l: matches_any_regex(l, regexs, ignore_case=ignore_case), lines))
    for line in lines:
        if matches_any_regex(line, regexs, ignore_case=ignore_case):
            matches.append(line)
    return matches


def remove_all_lines_matching_regexs(s, regexs, ignore_case=False):
    if type(regexs) is str:
        regexs = [regexs]
    lines = s.splitlines()
    not_matching_lines = list(filter(lambda l: not matches_any_regex(
        l, regexs, ignore_case=ignore_case), lines))
    return '\n'.join(not_matching_lines)


def add_to_regexs(s, regexA, regexB, ignore_case=False):
    blocks = SequenceMatcher(None, regexA, regexB).get_matching_blocks()
    if len(blocks) > 1:
        a, b, _ = blocks[1]
        difference = make_literals_special_chars(regexB[a:b])
        match, i0, i1 = find_match_full(
            s, regexA, ignore_case=ignore_case)
        if match is not None:
            regexA0 = regexA[:a]
            regexA1 = regexA[a:]
            _, _, i = find_match_full(match, regexA0, ignore_case=ignore_case)
            # addition = find_match(match[i:], addition)
            replacement = match[:i] + difference + match[i:]
            s = s[:i0] + replacement + s[i1:]
    return s


def matches_any_regex(s, regexs, ignore_case=False, whole_word=False):
    if type(regexs) is str:
        regexs = [regexs]
    for regex in regexs:
        if contains_regex(s, regex, ignore_case=ignore_case, whole_word=whole_word):
            return True
    return False


def extract_fragment_full(s, regex0, regex1, include_opening_match=True, include_closing_match=False, ignore_case=False, whole_word=False):
    _, i0, match0 = get_from_match_full(s, regex0, ignore_case=ignore_case,
                                        whole_word=whole_word, include_match=include_opening_match)
    i = i0+len(match0)
    _, i1_, _ = get_until_match_full(s[i:], regex1, ignore_case=ignore_case,
                                     whole_word=whole_word, include_match=include_closing_match)
    if i0 != -1 and i1_ != -1:
        i1 = i+i1_
    else:
        i1 = -1
    return s[i0:i1], i0, i1


def get_from_match_full(s, regex, ignore_case=False, whole_word=False, include_match=True):
    _, i0, i1 = find_match_full(
        s, regex, ignore_case=ignore_case, whole_word=whole_word)
    if include_match:
        i = i0
    else:
        i = i1
    if i != -1:
        return s[i:], i, s[i0:i1]
    else:
        return '', -1, ''


def get_until_match_full(s, regex, ignore_case=False, whole_word=False, include_match=False):
    _, i0, i1 = find_match_full(
        s, regex, ignore_case=ignore_case, whole_word=whole_word)
    if include_match:
        i = i1
    else:
        i = i0
    if i != -1:
        return s[:i], i, s[i0:i1]
    else:
        return s, -1, ''


def extract_fragment(s, regex0, regex1, include_opening_match=True, include_closing_match=False, ignore_case=False, whole_word=False):
    s, _, _ = extract_fragment_full(s, regex0, regex1, include_opening_match=include_opening_match,
                                    include_closing_match=include_closing_match, ignore_case=ignore_case, whole_word=whole_word)
    return s


def get_from_match(s, regex, ignore_case=False, whole_word=False, include_match=True):
    s, _, _ = get_from_match_full(s, regex, ignore_case=ignore_case,
                                  whole_word=whole_word, include_match=include_match)
    return s


def get_until_match(s, regex, ignore_case=False, whole_word=False, include_match=True):
    s, _, _ = get_until_match_full(
        s, regex, ignore_case=ignore_case, whole_word=whole_word, include_match=include_match)
    return s


def contains_regex(s, regex, ignore_case=False, whole_word=False):
    match, _, _ = find_match_full(
        s, regex, ignore_case=ignore_case, whole_word=whole_word)
    if match is not None:
        return True
    else:
        return False


def find_match(s, regexs, ignore_case=False):
    if type(s) is not str:
        raise TypeError(
            f'Invalid type {type(s)} for input argument. Must be a string.')
    if type(regexs) is str:
        regexs = [regexs]
    if ignore_case:
        flags = re.MULTILINE | re.IGNORECASE
    else:
        flags = re.MULTILINE
    match = None
    for regex in regexs:
        matches = re.search(regex, s, flags=flags)
        if matches != None:
            match = matches.group()
            return match
    return match


def find_match_full(s, regexs, ignore_case=False, whole_word=False, i_start=0, i_end=-1):
    if type(s) is not str:
        raise TypeError(
            f'Invalid type {type(s)} for input argument. Must be a string.')
    if type(regexs) is str:
        regexs = [regexs]
    match = None
    i0 = -1
    i1 = -1
    for regex in regexs:
        match_, i0_, i1_ = find_full_regex_match(
            s, regex, ignore_case=ignore_case, whole_word=whole_word, i_start=i_start, i_end=i_end)
        if (i0_ < i0 or i0 == -1) and match_ is not None:
            match = match_
            i0 = i0_
            i1 = i1_
    return match, i0, i1


def find_full_regex_match(s, regex, ignore_case=False, whole_word=False, i_start=0, i_end=-1):
    if ignore_case:
        flags = re.MULTILINE | re.IGNORECASE
    else:
        flags = re.MULTILINE
    match = None
    i0 = -1
    i1 = -1
    if i_start != -1 and i_start < len(s) and len(regex) > 0:
        if i_end == -1:
            matches = re.search(regex, s[i_start:], flags=flags)
        else:
            matches = re.search(regex, s[i_start:i_end], flags=flags)
        if matches != None:
            match = matches.group()
            if len(matches.regs) > 0:
                i0_, i1_ = matches.regs[0]
                i0 = i_start+i0_
                i1 = i_start+i1_
            if whole_word:
                if i0 != 0:
                    if not is_separator(s[i0-1]):
                        match, i0, i1 = find_full_regex_match(
                            s, regex, ignore_case=ignore_case, whole_word=whole_word, i_start=i0+1)
                if i1 != len(s) and i1 != -1:
                    if not is_separator(s[i1]):
                        match, i0, i1 = find_full_regex_match(
                            s, regex, ignore_case=ignore_case, whole_word=whole_word, i_start=i1)
    return match, i0, i1


def get_first_match_index(s, regexs, ignore_case=False, i_start=0, i_end=-1):
    if type(regexs) is str:
        regexs = [regexs]
    index = -1
    for regex in regexs:
        _, i, _ = find_match_full(
            s, regex, ignore_case=ignore_case, i_start=i_start, i_end=i_end)
        if i != -1 and (index == -1 or i < index):
            index = i
    return index


def get_first_match_last_index(s, regexs, ignore_case=False, i_start=0, i_end=-1):
    if type(regexs) is str:
        regexs = [regexs]
    index = -1
    for regex in regexs:
        _, _, i = find_match_full(
            s, regex, ignore_case=ignore_case, i_start=i_start, i_end=i_end)
        if i != -1 and (index == -1 or i < index):
            index = i
    return index


def get_first_number(s):
    number = find_match(s, '\\d+')
    return number


def get_first_number_full(s):
    number, i0, i1 = find_match_full(s, '\\d+')
    return number, i0, i1


def get_first_roman_number_full(s):
    number, i0, i1 = find_match_full(s, ' (I|V|X|L|C|D|M)+(\s|\n|$)?')
    if number is not None:
        while not (number.startswith('I') or number.startswith('V') or number.startswith('X') or number.startswith('L') or number.startswith('C') or number.startswith('D') or number.startswith('M')):
            number = number[1:]
            i0 += 1
        while not (number.endswith('I') or number.endswith('V') or number.endswith('X') or number.endswith('L') or number.endswith('C') or number.endswith('D') or number.endswith('M')):
            number = number[:-1]
            i1 -= 1
    return number, i0, i1


def get_first_spanish_ordinal_full(s):
    numerals_filepath = 'src/config/tags/numerals/spanishOrdinalsShort.txt'
    regexs = load_text(numerals_filepath).splitlines()
    regex = merge_regexs(regexs)
    number, i0, i1 = find_match_full(s, regex, ignore_case=True)
    return number, i0, i1


def get_first_number_extended(s):
    number = None
    index = 1e10
    decimal = get_first_number_full(s)
    ordinal = get_first_spanish_ordinal_full(s)
    roman = get_first_roman_number_full(s)
    matches = [decimal, ordinal, roman]
    for match in matches:
        digit, i, _ = match
        if digit is not None and i < index:
            number = digit
            index = i
    return number


def has_numeral(s, language='en'):
    s = alpha2digit(s, language).replace('first', '1st').replace('second', '2nd').replace(
        'third', '3rd').replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
    s = remove_whitespaces(s)
    return has_number(s)


def is_numeral(s, language='en'):
    if type(s) is int or type(s) is float:
        return True
    elif type(s) is str:
        s = alpha2digit(s, language).replace('first', '1st').replace('second', '2nd').replace(
            'third', '3rd').replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
        s = remove_whitespaces(s)
        return is_number(s)
    else:
        raise TypeError(
            f'Invalid type <{type(s)}> for input argument <s>. Valid types are: <str>, <int> and <float>.')


def just_numerals(s, language='en'):
    if type(s) is int or type(s) is float:
        return True
    elif type(s) is str:
        parts = split_by_separators(s, additional_separators=['and', '&'])
        parts = remove_empty(parts)
        return all(list(map(is_numeral, parts)))
    else:
        raise TypeError(
            f'Invalid type <{type(s)}> for input argument <s>. Valid types are: <str>, <int> and <float>.')


def has_number(s):
    return find_match(s, r'\d') is not None


def is_number(s):
    return s.isnumeric()


def get_first_word(s):
    word = find_match(s, '\\w+')
    return word


def get_first_date(s):
    regexs = [
        '\\d+ de (enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)( (de|del|del año) \\d{4})?',
        '\\d+(\\.|/|-)\\d+(\\.|/|-)\\d{4}'
    ]
    date = find_match(s, regexs)
    return date


def find_all_matches(s, regexs, ignore_case=False, whole_word=False):
    matches_full = find_all_matches_full(
        s, regexs, ignore_case=ignore_case, whole_word=whole_word)
    matches = get_column_as_list(matches_full, 0)
    return matches


def find_all_matches_full(s, regexs, ignore_case=False, whole_word=False):
    if type(regexs) is str:
        regexs = [regexs]
    matches_full = []
    i_ = 0
    while len(s) > 0:
        match, i0_, i1_ = find_match_full(
            s, regexs, ignore_case=ignore_case, whole_word=whole_word)
        if match is not None:
            if len(match) > 0:
                i0 = i_ + i0_
                i1 = i_ + i1_
                matches_full.append((match, i0, i1))
                i_ += i1_
                s = s[i1_:]
                continue
        break
        # matches += re.findall(regex, s, flags=flags)
    return matches_full


def find_all_unique_matches(s, regexs, ignore_case=False):
    matches = find_all_matches(s, regexs, ignore_case=ignore_case)
    matches = list(set(matches))
    return matches


def find_last_match_full_forward_strategy(s, regexs, ignore_case=True, whole_word=False):
    match_full = (None, -1, -1)
    matches_full = find_all_matches_full(
        s, regexs, ignore_case=ignore_case, whole_word=whole_word)
    if len(matches_full) > 0:
        match_full = matches_full[-1]
    return match_full


def find_last_match_full_backwards_strategy(s, regexs, step_size=1, ignore_case=True, whole_word=False):
    match, i0, i1 = None, -1, -1
    i = len(s)
    while i > 0:
        match, i0_, i1_ = find_last_match_full_forward_strategy(
            s[i:], regexs, ignore_case=ignore_case, whole_word=whole_word)
        if match is not None:
            i0 = i + i0_
            i1 = i + i1_
            break
        else:
            i -= step_size
    return match, i0, i1


def find_last_match_full(s, regexs, ignore_case=True, whole_word=False, step_size=20, strategy='backwards'):
    if strategy == 'forward':
        return find_last_match_full_forward_strategy(
            s, regexs, ignore_case=ignore_case, whole_word=whole_word)
    elif strategy == 'backwards':
        return find_last_match_full_backwards_strategy(
            s, regexs, step_size=step_size, ignore_case=ignore_case, whole_word=whole_word)
    else:
        raise NotImplementedError(
            'Invalid strategy <{strategy}>. Valid values are <forward> and <backwards>.')


def find_last_separator_index(s, strategy='backwards', step_size=20):
    regexs = ['(\s|\\.|,|;|:)']
    _, i0, _ = find_last_match_full(
        s, regexs, strategy=strategy, step_size=step_size, ignore_case=True, whole_word=False)
    return i0


def find_last_whitespace_index(s, strategy='backwards', step_size=20):
    regexs = ['\s']
    _, i0, _ = find_last_match_full(
        s, regexs, strategy=strategy, step_size=step_size, ignore_case=True, whole_word=False)
    return i0


def replace_whole_word(s, replacements):
    for word, replacement in replacements.items():
        s = re.sub(f'\\b{word}\\b', replacement, s)
    return s


def replace_ignoring_case(s, regex, replacement):
    matches = find_all_unique_matches(s, regex, ignore_case=True)
    for match in matches:
        s = s.replace(match, replacement)
    return s


def replace_mantaining_case(s, regex, replacement):
    matches = find_all_unique_matches(s, regex, ignore_case=True)
    for match in matches:
        if match.islower():
            replacement = replacement.lower()
        elif match.isupper():
            replacement = replacement.upper()
        elif match.istitle():
            replacement = replacement.title()
        s = s.replace(match, replacement)
    return s


def replace_pattern_in_regex(s, regexs, pattern_regex, replacement, replace_all=True, ignore_case=False, whole_word=False):
    matches = find_all_matches(
        s, regexs, ignore_case=ignore_case, whole_word=whole_word)
    for match in matches:
        pattern = find_match(match, pattern_regex)
        new_string = match.replace(pattern, replacement)
        s = s.replace(match, new_string, 1)
        if not replace_all:
            break
    return s


def replace_regex(s, regexs, replacement, replace_all=False, ignore_case=False, whole_word=False, i_start=0, i_end=-1):
    while True:
        match, i0, i1 = find_match_full(
            s, regexs, ignore_case=ignore_case, whole_word=whole_word, i_start=i_start, i_end=i_end)
        if match is None:
            return s
        else:
            i_start = i0+1
            if i0 == i1 and i0 != -1:
                i1 = i0+1
            s = s[:i0] + replacement + s[i1:]
            if not replace_all:
                return s


def merge_regexs(regexs):
    if type(regexs) is list:
        regex = f"({')|('.join(regexs)})"
        return regex
    else:
        raise TypeError('merge_regexs expected <regexs> var to be a <list>.')


def split_by_separators(s: str, additional_separators: list = []):
    separators = ['\s', ',', '\.', '\n', ';',
                  ':', '\(', '\)', '\[', '\]', '"', "'"] + additional_separators
    return re.split(r'|'.join(separators), s)


def split_by_regexs(string, regexs, ignore_case=False, whole_word=False):
    if type(regexs) is str:
        regexs = [regexs]
    if ignore_case:
        flags = re.MULTILINE | re.IGNORECASE
    else:
        flags = re.MULTILINE
    regex = merge_regexs(regexs)
    parts = re.split(regex, string, flags=flags)
    parts = remove_nones(parts)
    return parts


def remove_not_listed_characters(s, char_regexs, ignore_case=False):
    return ''.join(filter(lambda c: matches_any_regex(c, char_regexs, ignore_case=ignore_case, whole_word=False), s))


def is_separator(char):
    return char in string.punctuation+' '+'\n'


def make_literal(regex):
    regex = make_literals_special_chars(regex)
    regex = make_special_chars_literals(regex)
    return regex


def remove_whitespaces(s):
    return s.replace(' ', '')


def break_sql_syntax(s):
    s = replace_pattern_in_regex(
        s, '\s+and\s+(\w+|\d+)=', '=', ' ', replace_all=True)
    return s


def make_special_chars_literals(regex):
    regex = regex.replace('(', '\\(')
    regex = regex.replace(')', '\\)')
    regex = regex.replace('.', '\\.')
    regex = regex.replace('^', '\\^')
    regex = regex.replace('$', '\\$')
    regex = regex.replace('*', '\\*')
    regex = regex.replace('+', '\\+')
    regex = regex.replace('?', '\\?')
    regex = regex.replace('{', '\\{')
    regex = regex.replace('}', '\\}')
    regex = regex.replace('[', '\\[')
    regex = regex.replace(']', '\\]')
    regex = regex.replace('|', '\\|')
    return regex


def make_literals_special_chars(regex):
    regex = regex.replace('\\(', '(')
    regex = regex.replace('\\)', ')')
    regex = regex.replace('\\.', '.')
    regex = regex.replace('\\^', '^')
    regex = regex.replace('\\$', '$')
    regex = regex.replace('\\*', '*')
    regex = regex.replace('\\+', '+')
    regex = regex.replace('\\?', '?')
    regex = regex.replace('\\{', '{')
    regex = regex.replace('\\}', '}')
    regex = regex.replace('\\[', '[')
    regex = regex.replace('\\]', ']')
    regex = regex.replace('\\|', '|')
    return regex
