# SPDX-License-Identifier: GPL-3.0-only
"""Synthetic BACKLOG mapping in an explicitly isolated D5 lab; never activation."""
import argparse
import base64
import json
from pathlib import Path

from .postgres import identity, sql_text
from .review import ReviewClient

ENTRIES = {
    'REGISTER_TASK_INTENT': ('register_task_intent', 'd5_writer'),
    'PREPARE_TASK_PROPOSAL': ('prepare_task_proposal', 'd5_writer'),
    'REVIEW_TASK_PROPOSAL': ('review_task_proposal', 'd5_reviewer'),
    'PACKAGE_TASK_PROPOSALS': ('package_task_proposals', 'd5_writer'),
    'APPLY_TASK_PROPOSALS': ('apply_task_proposals', 'd5_applier'),
}


def mapping_sql(request):
    function, _ = ENTRIES[request['action']]
    return 'SELECT d5.' + function + '(' + sql_text(json.dumps(request, allow_nan=False)) + '::json);'


class MappingClient(ReviewClient):
    def __init__(self, container, role='d5_reader'):
        super().__init__(container, 'd5_reader' if role == 'd5_applier' else role)
        if role not in ('d5_writer', 'd5_reviewer', 'd5_reader', 'd5_applier'):
            raise ValueError('Unknown mapping role')
        self.role = role

    def artifact(self, project_id, document_id, kind, key):
        if kind not in ('proposal', 'package'):
            raise ValueError('Unknown artifact')
        args = [sql_text(identity(project_id))+'::uuid', sql_text(identity(document_id))+'::uuid',
                sql_text(identity(key))+'::uuid' if kind == 'proposal' else sql_text(key)]
        return self.query('SELECT d5.read_task_' + kind + '(' + ','.join(args) + ');')

    def verify_manifest(self, project_id, document_id, proposal_id, digest):
        artifact = self.artifact(project_id, document_id, 'proposal', proposal_id)
        if not artifact or artifact['manifest_sha256'] != digest:
            raise ValueError('Manifest not found in requested scope/hash')
        manifest = artifact['manifest']
        report, report_hash = self.recover_comparison(project_id, document_id, manifest['comparison_id'])
        if report_hash != manifest['report_sha256']:
            raise ValueError('Manifest report hash mismatch')
        row = next((r for r in report['review_items'] if r['source_key'] == manifest['intent']['source_key']), None)
        if not row or row['row_sha256'] != manifest['row_sha256'] or json.loads(base64.b64decode(row['row_base64'], validate=True)) != manifest['source_change']:
            raise ValueError('Manifest source differs from reconstruction')
        candidate = manifest['source_change']['after']['row']
        expected = None if candidate is None else {'title': candidate['fields']['item'], 'description': candidate['fields']['objective']}
        if manifest['after_projection'] != expected or manifest['intent']['policy'] != 'd5.task-projection.v1':
            raise ValueError('Manifest projection mismatch')
        return artifact

    def submit_mapping(self, request):
        action = request['action']
        _, role = ENTRIES[action]
        if self.role != role:
            raise ValueError('Use the dedicated synthetic role for this action')
        pid, doc = request['project_id'], request['document_id']
        if action == 'PREPARE_TASK_PROPOSAL':
            _, digest = self.recover_comparison(pid, doc, request['comparison_id'])
            if digest != request['report_sha256']:
                raise ValueError('Comparison hash mismatch')
        elif action == 'REVIEW_TASK_PROPOSAL':
            self.verify_manifest(pid, doc, request['proposal_id'], request['manifest_sha256'])
        elif action in ('PACKAGE_TASK_PROPOSALS', 'APPLY_TASK_PROPOSALS'):
            if action == 'PACKAGE_TASK_PROPOSALS':
                items = request['items']
            else:
                package = self.artifact(pid, doc, 'package', request['package_sha256'])
                if package is None:
                    raise ValueError('Package not found')
                items = package['items']
            for pin in items:
                self.verify_manifest(pid, doc, pin['proposal_id'], pin['manifest_sha256'])
        return self.query(mapping_sql(request))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container', required=True)
    parser.add_argument('--request', required=True, help='Explicit closed JSON command file; no defaults or latest selection')
    args = parser.parse_args()
    try:
        path = Path(args.request)
        if path.stat().st_size > 4194304:
            raise ValueError('Request too large')
        def unique(pairs):
            obj = {}
            for key, value in pairs:
                if key in obj:
                    raise ValueError('Duplicate key')
                obj[key] = value
            return obj
        request = json.loads(path.read_text(), object_pairs_hook=unique)
        client = MappingClient(args.container, ENTRIES[request['action']][1])
        result = client.submit_mapping(request)
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        return 2 if result.get('status') == 'CONFLICT' else 0
    except (ValueError, KeyError, TypeError, RuntimeError, OSError, __import__('subprocess').SubprocessError):
        parser.exit(1, 'D5 mapping failed; no success acknowledged\n')


if __name__ == '__main__':
    raise SystemExit(main())
