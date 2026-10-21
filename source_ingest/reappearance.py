# SPDX-License-Identifier: GPL-3.0-only
"""Reviewed source ID reappearance; existing synthetic BACKLOG tasks only."""
import argparse
import base64
import json
from pathlib import Path

from .bootstrap import semantic
from .postgres import identity, sql_text
from .task_mapping import MappingClient

ENTRIES = {
    'PREPARE_REAPPEARANCE_TASK': ('prepare_reappearance_task', 'd5_writer'),
    'REVIEW_REAPPEARANCE_TASK': ('review_reappearance_task', 'd5_reviewer'),
    'PACKAGE_REAPPEARANCE_TASKS': ('package_reappearance_tasks', 'd5_writer'),
    'APPLY_REAPPEARANCE_TASKS': ('apply_reappearance_tasks', 'd5_applier'),
}


def reappearance_sql(request):
    name, _ = ENTRIES[request['action']]
    return 'SELECT d5.'+name+'('+sql_text(json.dumps(request, allow_nan=False))+'::json);'


class ReappearanceClient(MappingClient):
    def __init__(self, container, role='d5_reader'):
        super().__init__(container, role)
        self.history = MappingClient(container, role)

    def absence(self, pid, doc, application_id, proposal_id):
        args = ','.join(sql_text(identity(x))+'::uuid' for x in (pid, doc, application_id, proposal_id))
        data = self.query('SELECT d5.read_reappearance_absence('+args+');')
        if data is None:
            raise ValueError('Confirmed scoped I8 absence application required')
        original = self.history.verify_manifest(pid, doc, proposal_id, data['absence_manifest_sha256'])
        if original['manifest'] != data['absence_manifest']:
            raise ValueError('Absence proof differs from original manifest')
        return data

    def artifact(self, pid, doc, kind, key):
        if kind not in ('proposal', 'package'):
            raise ValueError('Unknown reappearance artifact')
        args = [sql_text(identity(pid))+'::uuid', sql_text(identity(doc))+'::uuid',
                sql_text(identity(key))+'::uuid' if kind == 'proposal' else sql_text(key)]
        return self.query('SELECT d5.read_reappearance_'+kind+'('+','.join(args)+');')

    def verify_manifest(self, pid, doc, proposal_id, digest):
        data = self.artifact(pid, doc, 'proposal', proposal_id)
        if not data or data['manifest_sha256'] != digest:
            raise ValueError('Reappearance manifest scope/hash mismatch')
        m = data['manifest']
        report, report_hash = self.recover_comparison(pid, doc, m['comparison_id'])
        entry = next((r for r in report['review_items'] if r['source_key'] == m['intent']['source_key']), None)
        if not entry or report_hash != m['report_sha256'] or entry['row_sha256'] != m['row_sha256']:
            raise ValueError('Reappearance source hash mismatch')
        row = json.loads(base64.b64decode(entry['row_base64'], validate=True))
        if row != m['source_change'] or row['change'] != 'ADDED' or row['before']['row'] is not None or row['after']['row'] is None:
            raise ValueError('Reappearance source differs from reconstruction')
        after = row['after']['row']
        projection = dict(title=after['fields']['item'], description=after['fields']['objective'])
        proof = self.absence(pid, doc, m['absence_proof']['application_command_id'], m['absence_proof']['absence_proposal_id'])
        if m['schema'] != 'd5.reappearance-task-manifest.v1' or m['mode'] != 'REAPPEARANCE' \
                or m['action'] not in ('PATCH_REAPPEARED_BACKLOG', 'LINK_REAPPEARANCE_EVIDENCE') \
                or m['after_projection'] != projection or m['after_basis'] != semantic(after) \
                or m['absence_proof'] != proof or m['identity_declaration'] != 'SAME_SOURCE_ENTITY' \
                or m['intent']['policy'] != 'd5.task-projection.v1':
            raise ValueError('Reappearance manifest/proof/projection mismatch')
        return data

    def submit_reappearance(self, request):
        action = request['action']
        if self.role != ENTRIES[action][1]:
            raise ValueError('Dedicated role required')
        pid, doc = request['project_id'], request['document_id']
        if action == 'PREPARE_REAPPEARANCE_TASK':
            _, digest = self.recover_comparison(pid, doc, request['comparison_id'])
            if digest != request['report_sha256']:
                raise ValueError('Comparison hash mismatch')
            self.absence(pid, doc, request['absence_application_command_id'], request['absence_proposal_id'])
        elif action == 'REVIEW_REAPPEARANCE_TASK':
            self.verify_manifest(pid, doc, request['proposal_id'], request['manifest_sha256'])
        elif action in ('PACKAGE_REAPPEARANCE_TASKS', 'APPLY_REAPPEARANCE_TASKS'):
            if action == 'PACKAGE_REAPPEARANCE_TASKS':
                items = request['items']
            else:
                package = self.artifact(pid, doc, 'package', request['package_sha256'])
                if package is None:
                    raise ValueError('Reappearance package not found')
                items = package['items']
            for pin in items:
                self.verify_manifest(pid, doc, pin['proposal_id'], pin['manifest_sha256'])
        return self.query(reappearance_sql(request))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container', required=True)
    parser.add_argument('--request', required=True, help='Closed JSON command file, explicit absence proof and source/target pins')
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
        result = ReappearanceClient(args.container, ENTRIES[request['action']][1]).submit_reappearance(request)
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        return 2 if result.get('status') == 'CONFLICT' else 0
    except (ValueError, KeyError, TypeError, RuntimeError, OSError, __import__('subprocess').SubprocessError):
        parser.exit(1, 'D5 reappearance failed; no success acknowledged\n')


if __name__ == '__main__':
    raise SystemExit(main())
