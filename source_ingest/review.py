# SPDX-License-Identifier: GPL-3.0-only
"""Compare stored observations, review whole source rows and simulate D5-only effects."""
import argparse
import base64
import hashlib
import json
import tempfile

from .compare import compare_previews
from .postgres import LabClient, envelope, identity, sql_bytes, sql_text, verify_payload
from .preview import MAX_PREVIEW_BYTES, canonical, save_preview


def verified_record(record, project_id, document_id, observation_id):
    if not record or record['observation_id'] != observation_id:
        raise ValueError('Observation not found in requested scope')
    source, artifact = bytes.fromhex(record['source_hex']), bytes.fromhex(record['preview_hex'])
    if hashlib.sha256(source).hexdigest() != record['content_sha256'] or hashlib.sha256(artifact).hexdigest() != record['preview_sha256']:
        raise ValueError('Stored bytes failed hash validation')
    value = verify_payload(source, artifact)
    if value['project_id'] != project_id or value['document_id'] != document_id:
        raise ValueError('Observation scope mismatch')
    return value


def build_report(project_id, document_id, before_id, after_id, pair):
    """Reuse the unchanged I2/I3 comparator on fully reconstructed private captures."""
    before = verified_record(pair['before'], project_id, document_id, before_id)
    after = verified_record(pair['after'], project_id, document_id, after_id)
    with tempfile.TemporaryDirectory(prefix='d5-compare-') as directory:
        a, _ = save_preview(directory, before)
        b, _ = save_preview(directory, after)
        comparison = compare_previews(a, b)
    refs = {name: {'observation_id': oid, 'preview_sha256': pair[name]['preview_sha256'],
                   'content_sha256': pair[name]['content_sha256']}
            for name, oid in [('before', before_id), ('after', after_id)]}
    report = {'schema': 'd5.persisted-comparison.v1', 'project_id': project_id, 'document_id': document_id,
              'profile': before['profile'], 'state': comparison['state'], 'activation_allowed': False,
              'observations': refs, 'comparison': comparison, 'review_items': []}
    old = {row['source_key']: row for row in before['proposals']}
    new = {row['source_key']: row for row in after['proposals']}
    for change in comparison['changes']:
        if change['change'] == 'UNCHANGED':
            continue
        key = change['source_key']
        row = {'schema': 'd5.source-change.v1', 'project_id': project_id, 'document_id': document_id,
               'profile': before['profile'], 'source_key': key, 'change': change['change'],
               'changed_fields': change['changed_fields'], 'source_identity_id': change['source_identity_id'],
               'before': dict(refs['before'], row=old.get(key)), 'after': dict(refs['after'], row=new.get(key)),
               'activation_allowed': False}
        payload = canonical(row)
        report['review_items'].append({'source_key': key, 'change': change['change'],
                                      'row_sha256': hashlib.sha256(payload).hexdigest(),
                                      'row_base64': base64.b64encode(payload).decode('ascii')})
    if len(canonical(report)) > MAX_PREVIEW_BYTES:
        raise ValueError('Comparison report exceeds 32 MiB')
    return report


def review_sql(function, request, artifact=None):
    if function not in ('save_comparison', 'decide_row', 'simulate_application'):
        raise ValueError('Unknown review entry')
    sql = 'SELECT d5.' + function + '(' + sql_text(json.dumps(request, allow_nan=False)) + '::json'
    if function == 'save_comparison':
        if not isinstance(artifact, bytes) or len(artifact) > MAX_PREVIEW_BYTES:
            raise ValueError('Missing report or size exceeded')
        sql += ',' + sql_bytes(artifact)
    return sql + ');'


class ReviewClient(LabClient):
    def __init__(self, container, role='d5_writer'):
        if role not in ('d5_writer', 'd5_reader', 'd5_reviewer'):
            raise ValueError('Unknown D5 lab role')
        super().__init__(container, 'd5_reader' if role == 'd5_reviewer' else role)
        self.role = role

    def sources(self, project_id, document_id, before_id, after_id):
        ids = (project_id, document_id, before_id, after_id)
        pair = self.query('SELECT d5.read_comparison_sources(' + ','.join(sql_text(identity(x)) + '::uuid' for x in ids) + ');')
        if pair is None:
            raise ValueError('Incompatible or missing stored observations')
        return pair

    def compare(self, command_id, project_id, document_id, before_id, after_id):
        pair = self.sources(project_id, document_id, before_id, after_id)
        report = build_report(project_id, document_id, before_id, after_id, pair)
        payload = canonical(report)
        req = envelope(command_id, 'SAVE_COMPARISON', project_id, document_id,
                       before_observation_id=identity(before_id), after_observation_id=identity(after_id),
                       profile=report['profile'], report_sha256=hashlib.sha256(payload).hexdigest())
        return self.query(review_sql('save_comparison', req, payload))

    def recover_comparison(self, project_id, document_id, comparison_id):
        ids = (project_id, document_id, comparison_id)
        data = self.query('SELECT d5.read_comparison(' + ','.join(sql_text(identity(x)) + '::uuid' for x in ids) + ');')
        if data is None:
            raise ValueError('Comparison not found')
        payload = bytes.fromhex(data['report_hex'])
        if len(payload) > MAX_PREVIEW_BYTES or hashlib.sha256(payload).hexdigest() != data['report_sha256']:
            raise ValueError('Stored report hash mismatch')
        report = json.loads(payload)
        refs = report['observations']
        pair = self.sources(project_id, document_id, refs['before']['observation_id'], refs['after']['observation_id'])
        expected = build_report(project_id, document_id, refs['before']['observation_id'], refs['after']['observation_id'], pair)
        if canonical(expected) != payload:
            raise ValueError('Stored comparison differs from reconstruction')
        return expected, data['report_sha256']

    def review_state(self, project_id, document_id, comparison_id, source_key):
        return self.query('SELECT d5.read_row_review(' + ','.join(sql_text(identity(x)) + '::uuid' for x in
                          (project_id, document_id, comparison_id)) + ',' + sql_text(source_key) + ');')

    def decide(self, command_id, project_id, document_id, comparison_id, source_key, row_sha256,
               report_sha256, expected_version, decision, reviewer_label, reason):
        report, digest = self.recover_comparison(project_id, document_id, comparison_id)
        if digest != report_sha256 or not any(x['source_key'] == source_key and x['row_sha256'] == row_sha256 for x in report['review_items']):
            raise ValueError('Review must pin the complete verified source change')
        req = envelope(command_id, 'DECIDE_ROW', project_id, document_id, comparison_id=identity(comparison_id),
                       source_key=source_key, row_sha256=row_sha256, report_sha256=report_sha256,
                       expected_version=expected_version, decision=decision, reviewer_label=reviewer_label, reason=reason)
        return self.query(review_sql('decide_row', req))

    def simulate(self, command_id, project_id, document_id, comparison_id, report_sha256, expected_reference_version, items):
        _, digest = self.recover_comparison(project_id, document_id, comparison_id)
        if digest != report_sha256:
            raise ValueError('Comparison hash mismatch')
        req = envelope(command_id, 'SIMULATE_APPLICATION', project_id, document_id,
                       comparison_id=identity(comparison_id), report_sha256=report_sha256,
                       expected_reference_version=expected_reference_version, items=items)
        return self.query(review_sql('simulate_application', req))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container', required=True)
    actions = parser.add_subparsers(dest='action', required=True)
    for name in ('compare', 'export', 'row', 'decide', 'simulate'):
        p = actions.add_parser(name)
        for key in ('project-id', 'document-id'):
            p.add_argument('--'+key, required=True)
        if name in ('compare', 'decide', 'simulate'):
            p.add_argument('--command-id', required=True)
        if name == 'compare':
            p.add_argument('--before-observation-id', required=True)
            p.add_argument('--after-observation-id', required=True)
        else:
            p.add_argument('--comparison-id', required=True)
        if name == 'export':
            p.add_argument('--store', default='work/d5/reviews')
        if name in ('row', 'decide'):
            p.add_argument('--source-key', required=True)
        if name == 'decide':
            p.add_argument('--row-sha256', required=True)
            p.add_argument('--report-sha256', required=True)
            p.add_argument('--expected-version', type=int, required=True)
            p.add_argument('--decision', choices=('ACCEPT', 'REJECT'), required=True)
            p.add_argument('--reviewer-label', required=True)
            p.add_argument('--reason', required=True)
        if name == 'simulate':
            p.add_argument('--report-sha256', required=True)
            p.add_argument('--expected-reference-version', type=int, required=True)
            p.add_argument('--item', action='append', required=True,
                           help='SOURCE_KEY:ROW_SHA256:DECISION_COMMAND_UUID:DECISION_VERSION (repeatable)')
    args = parser.parse_args()
    try:
        client = ReviewClient(args.container, 'd5_reviewer' if args.action in ('decide', 'simulate') else
                              'd5_writer' if args.action == 'compare' else 'd5_reader')
        common = (args.project_id, args.document_id)
        if args.action == 'compare':
            result = client.compare(args.command_id, *common, args.before_observation_id, args.after_observation_id)
        elif args.action == 'decide':
            result = client.decide(args.command_id, *common, args.comparison_id, args.source_key, args.row_sha256,
                                   args.report_sha256, args.expected_version, args.decision, args.reviewer_label, args.reason)
        elif args.action == 'simulate':
            items = []
            for raw in args.item:
                key, digest, cid, version = raw.split(':')
                items.append(dict(source_key=key, row_sha256=digest, decision_command_id=identity(cid), expected_version=int(version)))
            result = client.simulate(args.command_id, *common, args.comparison_id, args.report_sha256,
                                     args.expected_reference_version, sorted(items, key=lambda x:x['source_key']))
        else:
            report, digest = client.recover_comparison(*common, args.comparison_id)
            if args.action == 'export':
                path, _ = save_preview(args.store, report)
                result = dict(report_sha256=digest, report=str(path), activation_allowed=False)
            else:
                item = next(x for x in report['review_items'] if x['source_key'] == args.source_key)
                result = dict(change=json.loads(base64.b64decode(item['row_base64'],validate=True)),
                              review=client.review_state(*common,args.comparison_id,args.source_key),report_sha256=digest)
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        return 2 if result and (result.get('status') == 'CONFLICT' or result.get('comparison_state') == 'BLOCKED') else 0
    except (ValueError, KeyError, TypeError, StopIteration, RuntimeError, OSError, __import__('subprocess').SubprocessError):
        parser.exit(1, 'D5 review failed; no success acknowledged\n')


if __name__ == '__main__':
    raise SystemExit(main())
