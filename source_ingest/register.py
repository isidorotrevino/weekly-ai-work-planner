# SPDX-License-Identifier: GPL-3.0-only
"""Explicit eight-column register profile. No workflow interpretation."""
import re
from .preview import MAX_ITEMS, structure

PROFILE = 'task-register.v1'
HEADERS = ('ID', 'Item', 'Component(s)', 'Objective', 'Blocked on', 'Status', 'Verified', 'Source')
FIELDS = ('id', 'item', 'components', 'objective', 'blocked_on', 'status', 'verified', 'source')
KEY = re.compile(r'[A-Z][A-Z0-9_]*-[0-9]+')


def cells(line):
    """Split only unescaped pipes; preserve raw markup and escape sequences."""
    line = line.strip()
    if not line.startswith('|'):
        return None
    values, start, slashes = [], 0, 0
    for index, char in enumerate(line):
        if char == '|' and slashes % 2 == 0:
            values.append(line[start:index])
            start = index + 1
        slashes = slashes + 1 if char == '\\' else 0
    values.append(line[start:])
    if values[0] or values[-1]:
        return None
    return [value.strip() for value in values[1:-1]]


def source_key(raw):
    struck = raw.startswith('~~') and raw.endswith('~~')
    key = raw[2:-2] if struck else raw
    return (key, struck) if KEY.fullmatch(key) else (None, struck)


def parse(content):
    sections, _, structural = structure(content)
    lines = content.decode('utf-8-sig').splitlines()
    proposals, diagnostics, seen = [], [], {}
    fence, active, expect_separator = None, False, False
    recognized, other_lines, row_count = 0, 0, 0
    heading_index, heading_path = 0, []

    def block(code, line, **details):
        diagnostics.append({'code': code, 'line': line, 'blocking': True, **details})

    for number, line in enumerate(lines, 1):
        while heading_index < len(sections) and sections[heading_index]['line'] <= number:
            heading = sections[heading_index]
            heading_path = [s for s in heading_path if s['level'] < heading['level']]
            heading_path.append(heading)
            heading_index += 1
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
            continue
        if marker:
            if expect_separator:
                block('REGISTER_SEPARATOR_REQUIRED', number)
            fence, active, expect_separator = (marker[1][0], len(marker[1])), False, False
            continue
        if line.lstrip().startswith('<'):
            block('HTML_BLOCK_UNSUPPORTED', number)
        if line.lstrip().startswith('|') and (len(line) - len(line.lstrip(' ')) > 3 or line.startswith('\t')):
            block('INDENTED_TABLE_UNSUPPORTED', number)
            active, expect_separator = False, False
            continue
        values = cells(line)
        if values is not None and tuple(values) == HEADERS:
            if expect_separator:
                block('REGISTER_SEPARATOR_REQUIRED', number)
            recognized += 1
            active, expect_separator = False, True
            continue
        if expect_separator:
            expect_separator = False
            if values is None or len(values) != len(HEADERS) or not all(re.fullmatch(r':?-{3,}:?', v) for v in values):
                block('REGISTER_SEPARATOR_REQUIRED', number)
                active = False
            else:
                active = True
                continue
        looks_like_row = line.lstrip().startswith('|')
        if not looks_like_row:
            active = False
            continue
        if not active:
            other_lines += 1
            first = values[0] if values else line.lstrip()[1:].split('|', 1)[0].strip()
            if source_key(first)[0] or first == 'ID':
                block('KEY_OUTSIDE_REGISTER_TABLE', number)
            elif values is not None and len(values) == len(HEADERS):
                block('UNRECOGNIZED_EIGHT_COLUMN_ROW', number)
            continue
        row_count += 1
        if row_count > MAX_ITEMS:
            raise ValueError('Register exceeds row limits')
        if values is None or len(values) != len(HEADERS):
            block('REGISTER_ROW_WIDTH', number)
            continue
        key, struck = source_key(values[0])
        if key is None:
            block('REGISTER_KEY_INVALID', number)
            continue
        if key in seen:
            block('REGISTER_KEY_DUPLICATE', number, first_line=seen[key], source_key=key)
        else:
            seen[key] = number
        proposals.append({'kind': 'REGISTER_ROW_CANDIDATE', 'source_key': key, 'source_struck': struck,
                          'fields': dict(zip(FIELDS, values)), 'line_start': number, 'line_end': number,
                          'heading_lines': [s['line'] for s in heading_path], 'activation_allowed': False})
    if expect_separator:
        block('REGISTER_SEPARATOR_REQUIRED', len(lines))
    if not recognized:
        block('NO_REGISTER_TABLE', 1)
    if any(d['code'] == 'UNCLOSED_FENCE' for d in structural):
        block('UNCLOSED_FENCE', len(lines))
    if other_lines:
        diagnostics.append({'code': 'OTHER_TABLE_LINES_UNINTERPRETED', 'line_count': other_lines, 'blocking': False})
    diagnostics.append({'code': 'REGISTER_PREVIEW_ONLY', 'blocking': False})
    return sections, proposals, diagnostics, {'recognized_tables': recognized, 'row_count': row_count,
                                              'comparison_eligible': not any(d.get('blocking') for d in diagnostics)}
