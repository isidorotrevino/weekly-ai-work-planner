# SPDX-License-Identifier: GPL-3.0-only
"""Reviewed whole source/local projection choice; synthetic owned BACKLOG tasks only."""
import argparse
import base64
import json
from pathlib import Path

from .bootstrap import semantic
from .postgres import identity, sql_text
from .task_mapping import MappingClient

ENTRIES = {
    'PREPARE_LOCAL_EDIT_TASK': ('prepare_local_edit_task', 'd5_writer'),
    'REVIEW_LOCAL_EDIT_TASK': ('review_local_edit_task', 'd5_reviewer'),
    'PACKAGE_LOCAL_EDIT_TASKS': ('package_local_edit_tasks', 'd5_writer'),
    'APPLY_LOCAL_EDIT_TASKS': ('apply_local_edit_tasks', 'd5_applier'),
}


def local_edit_sql(request):
    name, _ = ENTRIES[request['action']]
    return 'SELECT d5.'+name+'('+sql_text(json.dumps(request, allow_nan=False))+'::json);'


class LocalEditClient(MappingClient):
    def __init__(self, container, role='d5_reader'):
        super().__init__(container, role)

    def artifact(self, pid, doc, kind, key):
        if kind not in ('proposal', 'package'):
            raise ValueError('Unknown local_edit artifact')
        args = [sql_text(identity(pid))+'::uuid', sql_text(identity(doc))+'::uuid',
                sql_text(identity(key))+'::uuid' if kind == 'proposal' else sql_text(key)]
        return self.query('SELECT d5.read_local_edit_'+kind+'('+','.join(args)+');')

    def verify_manifest(self, pid, doc, proposal_id, digest):
        data = self.artifact(pid, doc, 'proposal', proposal_id)
        if not data or data['manifest_sha256'] != digest:
            raise ValueError('LocalEdit manifest scope/hash mismatch')
        m = data['manifest']
        report, report_hash = self.recover_comparison(pid, doc, m['comparison_id'])
        entry = next((r for r in report['review_items'] if r['source_key'] == m['intent']['source_key']), None)
        if not entry or report_hash != m['report_sha256'] or entry['row_sha256'] != m['row_sha256']:
            raise ValueError('LocalEdit source hash mismatch')
        row = json.loads(base64.b64decode(entry['row_base64'], validate=True))
        if row != m['source_change'] or row['change'] != 'CHANGED' or row['before']['row'] is None or row['after']['row'] is None:
            raise ValueError('Local resolution source differs from reconstruction')
        after = row['after']['row']
        projection = dict(title=after['fields']['item'], description=after['fields']['objective'])
        local = {k: m['target'][k] for k in ('title', 'description')}
        base = dict(title=m['last_applied_basis']['fields']['item'], description=m['last_applied_basis']['fields']['objective'])
        choice = m['choice']
        result = projection if choice == 'USE_SOURCE' else local
        action = 'KEEP_LOCAL_BACKLOG' if choice == 'KEEP_LOCAL' else ('LINK_LOCAL_RESOLUTION_EVIDENCE' if result == local else 'PATCH_LOCAL_USE_SOURCE')
        if m['schema'] != 'd5.local-edit-task-manifest.v1' or m['mode'] != 'LOCAL_EDIT' \
                or choice not in ('USE_SOURCE', 'KEEP_LOCAL') or m['action'] != action \
                or m['after_projection'] != projection or m['after_basis'] != semantic(after) \
                or m['last_applied_basis'] != semantic(row['before']['row']) \
                or m['local_projection'] != local or m['result_projection'] != result \
                or m['before_projection'] != base or m['before_projection'] == local or m['intent']['policy'] != 'd5.task-projection.v1':
            raise ValueError('Local resolution manifest/projection mismatch')
        return data

    def submit_local_edit(self, request):
        action = request['action']
        if self.role != ENTRIES[action][1]:
            raise ValueError('Dedicated role required')
        pid, doc = request['project_id'], request['document_id']
        if action == 'PREPARE_LOCAL_EDIT_TASK':
            _, digest = self.recover_comparison(pid, doc, request['comparison_id'])
            if digest != request['report_sha256']:
                raise ValueError('Comparison hash mismatch')
        elif action == 'REVIEW_LOCAL_EDIT_TASK':
            self.verify_manifest(pid, doc, request['proposal_id'], request['manifest_sha256'])
        elif action in ('PACKAGE_LOCAL_EDIT_TASKS', 'APPLY_LOCAL_EDIT_TASKS'):
            if action == 'PACKAGE_LOCAL_EDIT_TASKS':
                items = request['items']
            else:
                package = self.artifact(pid, doc, 'package', request['package_sha256'])
                if package is None:
                    raise ValueError('LocalEdit package not found')
                items = package['items']
            for pin in items:
                self.verify_manifest(pid, doc, pin['proposal_id'], pin['manifest_sha256'])
        return self.query(local_edit_sql(request))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container', required=True)
    parser.add_argument('--request', required=True, help='Closed JSON command file, explicit source/local choice and source/target pins')
    args = parser.parse_args()
    try:
        path = Path(args.request)
        if path.stat().st_size > 4194304:
            raise ValueError('Request limit exceeded')
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError('Duplicate JSON key')
                result[key] = value
            return result
        request = json.loads(path.read_text(), object_pairs_hook=unique)
        result = LocalEditClient(args.container, ENTRIES[request['action']][1]).submit_local_edit(request)
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        return 2 if result.get('status') == 'CONFLICT' else 0
    except (ValueError, KeyError, TypeError, RuntimeError, OSError, __import__('subprocess').SubprocessError):
        parser.exit(1, 'D5 local_edit failed; no success acknowledged\n')


if __name__ == '__main__':
    raise SystemExit(main())
