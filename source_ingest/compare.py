# SPDX-License-Identifier: GPL-3.0-only
"""Verify local snapshots and compare explicit source keys, without applying changes."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from .preview import MAX_BYTES, MAX_PREVIEW_BYTES, _directory, _identity, build_observation, canonical, save_preview
from .register import PROFILE


def _unique_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('Duplicate JSON key')
        value[key] = item
    return value


def load_preview(path):
    path = Path(path)
    if not re.fullmatch(r'[a-f0-9]{64}\.json', path.name):
        raise ValueError('Expected a content-addressed preview filename')
    parent = _directory(path.parent)
    fd = None
    try:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > MAX_PREVIEW_BYTES:
            raise ValueError('Invalid preview file or size')
        with os.fdopen(fd, 'rb') as stream:
            fd = None
            payload = stream.read(MAX_PREVIEW_BYTES + 1)
            if len(payload) > MAX_PREVIEW_BYTES or _identity(before) != _identity(os.fstat(stream.fileno())):
                raise ValueError('Preview changed during read or exceeds limits')
        if hashlib.sha256(payload).hexdigest() != path.stem:
            raise ValueError('Preview filename hash mismatch')
        try:
            value = json.loads(payload, object_pairs_hook=_unique_keys)
            if not isinstance(value, dict):
                raise ValueError('Preview must be an object')
            for key in ['project_id', 'document_id', 'source_path', 'observed_revision', 'profile', 'content_base64']:
                if not isinstance(value.get(key), str):
                    raise ValueError('Invalid preview metadata')
            if len(value['content_base64']) > 4 * ((MAX_BYTES + 2) // 3):
                raise ValueError('Snapshot exceeds limits')
            content = base64.b64decode(value['content_base64'], validate=True)
            expected = build_observation(content, value['source_path'], value['project_id'], value['document_id'], value['observed_revision'], value['profile'])
            if canonical(expected) != payload:
                raise ValueError('Preview differs from deterministic snapshot reconstruction')
            return expected, path.stem
        except (TypeError, KeyError, UnicodeError, RecursionError) as ex:
            raise ValueError('Invalid preview encoding or structure') from ex
    finally:
        if fd is not None:
            os.close(fd)
        os.close(parent)


def compare_previews(before_path, after_path):
    before, before_hash = load_preview(before_path)
    after, after_hash = load_preview(after_path)
    for field in ['project_id', 'document_id', 'profile']:
        if before[field] != after[field]:
            raise ValueError('Incompatible preview ' + field)
    if before['profile'] != PROFILE:
        raise ValueError('Comparison requires explicit task-register.v1 snapshots')
    report = {'schema': 'd5.local-comparison.v1', 'profile': PROFILE, 'state': 'PREVIEW_ONLY', 'activation_allowed': False,
              'project_id': before['project_id'], 'document_id': before['document_id'],
              'before_preview_sha256': before_hash, 'after_preview_sha256': after_hash,
              'before_content_sha256': before['content_sha256'], 'after_content_sha256': after['content_sha256'],
              'changes': [], 'diagnostics': []}
    for name, value in [('before', before), ('after', after)]:
        for diagnostic in value['diagnostics']:
            if diagnostic.get('blocking'):
                report['diagnostics'].append({'observation': name, **diagnostic})
    if report['diagnostics']:
        report['state'] = 'BLOCKED'
        return report
    if before['observed_revision'] == after['observed_revision'] and before['content_sha256'] != after['content_sha256']:
        report['diagnostics'].append({'code': 'CALLER_LABEL_REUSED_WITH_DIFFERENT_BYTES', 'blocking': False})
    old = {row['source_key']: row for row in before['proposals']}
    new = {row['source_key']: row for row in after['proposals']}
    for key in sorted(old.keys() | new.keys()):
        a, b = old.get(key), new.get(key)
        changed = [field for field in a['fields'] if a['fields'][field] != b['fields'][field]] if a and b else []
        status = 'ADDED' if a is None else 'ABSENT_IN_OBSERVATION' if b is None else 'CHANGED' if changed else 'UNCHANGED'
        entry = {'source_key': key, 'source_identity_id': (a or b)['source_identity_id'], 'change': status,
                 'changed_fields': changed, 'activation_allowed': False}
        for name, row in [('before', a), ('after', b)]:
            entry[name] = {'candidate_id': row['candidate_id'], 'source_locator': row['source_locator']} if row else None
        entry['location_changed'] = bool(a and b and a['line_start'] != b['line_start'])
        report['changes'].append(entry)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', required=True)
    parser.add_argument('--after', required=True)
    parser.add_argument('--store', default='work/d5/comparisons')
    args = parser.parse_args()
    try:
        report = compare_previews(args.before, args.after)
        path, digest = save_preview(args.store, report)
    except (OSError, ValueError) as ex:
        parser.exit(1, 'Comparison rejected: ' + str(ex) + '\n')
    counts = {}
    for item in report['changes']:
        counts[item['change']] = counts.get(item['change'], 0) + 1
    print(json.dumps({'state': report['state'], 'activation_allowed': False, 'comparison': str(path), 'comparison_sha256': digest,
                      'counts': counts, 'diagnostics': list(dict.fromkeys(d['code'] for d in report['diagnostics']))}))
    return 2 if report['state'] == 'BLOCKED' else 0


if __name__ == '__main__':
    raise SystemExit(main())
