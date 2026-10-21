# SPDX-License-Identifier: GPL-3.0-only
"""Reviewed adoption of an existing BACKLOG task; never writes its row."""
import argparse
import hashlib
import json
from pathlib import Path

from .postgres import envelope, identity, sql_bytes, sql_text
from .preview import canonical
from .bootstrap import semantic
from .review import verified_record
from .task_mapping import MappingClient

ENTRIES = {
    'PREPARE_ADOPTION_TASK': ('prepare_adoption_task', 'd5_writer'),
    'REVIEW_ADOPTION_TASK': ('review_adoption_task', 'd5_reviewer'),
    'PACKAGE_ADOPTION_TASKS': ('package_adoption_tasks', 'd5_writer'),
    'APPLY_ADOPTION_TASKS': ('apply_adoption_tasks', 'd5_applier'),
}


def adoption_sql(request, rowbytes=None):
    name, _ = ENTRIES[request['action']]
    sql = 'SELECT d5.'+name+'('+sql_text(json.dumps(request, allow_nan=False))+'::json'
    if request['action'] == 'PREPARE_ADOPTION_TASK':
        if not isinstance(rowbytes, bytes) or len(rowbytes) > 2097152:
            raise ValueError('Missing row or byte limit exceeded')
        sql += ','+sql_bytes(rowbytes)
    elif rowbytes is not None:
        raise ValueError('Unexpected row artifact')
    return sql+');'



class AdoptionClient(MappingClient):
    def snapshot(self, pid, doc, oid):
        pair = self.sources(pid, doc, oid, oid)
        record = pair['before']
        value = verified_record(record, pid, doc, oid)
        if value['profile'] not in ('task-register.v1', 'task-register-compat.v1') or any(d.get('blocking') for d in value['diagnostics']):
            raise ValueError('Adoption requires an unblocked tabular observation')
        return value, record

    def prepare_request(self, command_id, pid, doc, observation_id, key, reference_version, task_id, task_key, profile, policy, reason):
        value, record = self.snapshot(pid, doc, observation_id)
        if value['profile'] != profile:
            raise ValueError('Adoption profile mismatch')
        rows = [r for r in value['proposals'] if r['source_key'] == key]
        if len(rows) != 1:
            raise ValueError('Selected ID must exist exactly once')
        payload = canonical(rows[0])
        return envelope(command_id, 'PREPARE_ADOPTION_TASK', pid, doc, source_key=key,
                        profile=profile, policy=policy, task_id=identity(task_id), task_key=task_key, reason=reason,
                        observation_id=identity(observation_id), content_sha256=record['content_sha256'],
                        preview_sha256=record['preview_sha256'], snapshot_row_sha256=hashlib.sha256(payload).hexdigest(),
                        expected_reference_version=reference_version), payload

    def artifact(self, pid, doc, kind, key):
        if kind not in ('proposal', 'package'):
            raise ValueError('Unknown adoption artifact')
        args = [sql_text(identity(pid))+'::uuid', sql_text(identity(doc))+'::uuid',
                sql_text(identity(key))+'::uuid' if kind == 'proposal' else sql_text(key)]
        return self.query('SELECT d5.read_adoption_'+kind+'('+','.join(args)+');')

    def verify_manifest(self, pid, doc, proposal_id, digest):
        data = self.artifact(pid, doc, 'proposal', proposal_id)
        if not data or data['manifest_sha256'] != digest:
            raise ValueError('Adoption manifest scope/hash mismatch')
        m = data['manifest']
        i = m['intent']
        req, payload = self.prepare_request(proposal_id, pid, doc, m['observation_id'], i['source_key'],
            m['reference_version'], i['task_id'], i['task_key'], i['profile'], i['policy'], m['reason'])
        row = json.loads(payload)
        projection = dict(title=row['fields']['item'], description=row['fields']['objective'])
        local = {k: m['target'][k] for k in ('title', 'description')}
        expected_intent = dict(intent_id=proposal_id, project_id=pid, document_id=doc, source_key=i['source_key'],
            source_key_sha256=hashlib.sha256(i['source_key'].encode()).hexdigest(),profile=i['profile'],policy='d5.task-projection.v1',
            task_id=i['task_id'],task_key=i['task_key'])
        if m['schema'] != 'd5.adoption-task-manifest.v1' or m['mode'] != 'ADOPTION_EXISTING' or m['action'] != 'LINK_EXISTING_BACKLOG' \
                or m['proposal_id'] != proposal_id or m['proposed_intent_id'] != proposal_id or i != expected_intent \
                or m['snapshot_row'] != row or m['snapshot_row_sha256'] != req['snapshot_row_sha256'] \
                or m['content_sha256'] != req['content_sha256'] or m['preview_sha256'] != req['preview_sha256'] \
                or m['projection'] != projection or m['source_basis'] != semantic(row) \
                or m['local_projection'] != local or m['result_projection'] != local or m['task_fields_to_write'] != [] \
                or m['target']['id'] != i['task_id'] or m['target']['project_id'] != pid or m['target']['task_key'] != i['task_key'] \
                or m['prior_applied_basis'] is not None:
            raise ValueError('Adoption manifest differs from reconstruction')
        return data

    def submit_adoption(self, request, rowbytes=None):
        action = request['action']
        if self.role != ENTRIES[action][1]:
            raise ValueError('Dedicated role required')
        pid, doc = request['project_id'], request['document_id']
        if action == 'PREPARE_ADOPTION_TASK':
            expected, payload = self.prepare_request(request['command_id'], pid, doc, request['observation_id'],
                request['source_key'], request['expected_reference_version'], request['task_id'], request['task_key'],
                request['profile'], request['policy'], request['reason'])
            if request != expected or (rowbytes is not None and rowbytes != payload):
                raise ValueError('Adoption request differs from verified snapshot')
            rowbytes = payload
        elif action == 'REVIEW_ADOPTION_TASK':
            self.verify_manifest(pid, doc, request['proposal_id'], request['manifest_sha256'])
        elif action in ('PACKAGE_ADOPTION_TASKS', 'APPLY_ADOPTION_TASKS'):
            if action == 'PACKAGE_ADOPTION_TASKS':
                items = request['items']
            else:
                package = self.artifact(pid, doc, 'package', request['package_sha256'])
                if package is None:
                    raise ValueError('Adoption package not found')
                items = package['items']
            for pin in items:
                self.verify_manifest(pid, doc, pin['proposal_id'], pin['manifest_sha256'])
        return self.query(adoption_sql(request, rowbytes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container', required=True)
    parser.add_argument('--request', required=True, help='Closed JSON command; explicit IDs and hashes, no latest selection')
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
        result = AdoptionClient(args.container, ENTRIES[request['action']][1]).submit_adoption(request)
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        return 2 if result.get('status') == 'CONFLICT' else 0
    except (ValueError, KeyError, TypeError, RuntimeError, OSError, __import__('subprocess').SubprocessError):
        parser.exit(1, 'D5 adoption failed; no success acknowledged\n')


if __name__ == '__main__':
    raise SystemExit(main())
