# SPDX-License-Identifier: GPL-3.0-only
"""Reviewed isolated local text resolution against an unchanged present source basis."""
import argparse
import hashlib
import json
from pathlib import Path

from .postgres import envelope, identity, sql_bytes, sql_text
from .preview import canonical
from .bootstrap import semantic
from .review import verified_record
from .task_mapping import MappingClient
from .adoption import AdoptionClient
from .bootstrap import BootstrapClient
from .reappearance import ReappearanceClient
from .local_edit import LocalEditClient
from .local_reappearance import LocalReappearanceClient

ENTRIES = {
    'PREPARE_ISOLATED_LOCAL_EDIT_TASK': ('prepare_isolated_local_edit_task', 'd5_writer'),
    'REVIEW_ISOLATED_LOCAL_EDIT_TASK': ('review_isolated_local_edit_task', 'd5_reviewer'),
    'PACKAGE_ISOLATED_LOCAL_EDIT_TASKS': ('package_isolated_local_edit_tasks', 'd5_writer'),
    'APPLY_ISOLATED_LOCAL_EDIT_TASKS': ('apply_isolated_local_edit_tasks', 'd5_applier'),
}


def isolated_local_edit_sql(request, rowbytes=None):
    name, _ = ENTRIES[request['action']]
    sql = 'SELECT d5.'+name+'('+sql_text(json.dumps(request, allow_nan=False))+'::json'
    if request['action'] == 'PREPARE_ISOLATED_LOCAL_EDIT_TASK':
        if not isinstance(rowbytes, bytes) or len(rowbytes) > 2097152:
            raise ValueError('Missing row or byte limit exceeded')
        sql += ','+sql_bytes(rowbytes)
    elif rowbytes is not None:
        raise ValueError('Unexpected row artifact')
    return sql+');'



class IsolatedLocalEditClient(AdoptionClient):
    def head_proof(self, pid, doc, intent, application, proposal):
        def read(aid, prop):
            args=','.join(sql_text(identity(x))+'::uuid' for x in (pid,doc,intent,aid,prop))
            return self.query('SELECT d5.read_isolated_local_head_proof('+args+');')
        proof=read(application,proposal)
        current=proof;seen=set()
        classes={'task':MappingClient,'bootstrap':BootstrapClient,'adoption':AdoptionClient,
                 'reappearance':ReappearanceClient,'local_edit':LocalEditClient,'local_reappearance':LocalReappearanceClient}
        while current is not None:
            pair=(current['application_command_id'],current['proposal_id'])
            if pair in seen or current['schema']!='d5.isolated-local-head-proof.v1':
                raise ValueError('Invalid head proof chain')
            seen.add(pair)
            if current['kind']=='isolated_local_edit':
                data=self.verify_manifest(pid,doc,current['proposal_id'],current['manifest_sha256'],verify_head=False)
            else:
                data=classes[current['kind']](self.container,self.role).verify_manifest(pid,doc,current['proposal_id'],current['manifest_sha256'])
            if data['manifest']!=current['manifest'] or data['manifest']['intent']['intent_id']!=intent:
                raise ValueError('Historical head manifest mismatch')
            if current['kind']!='isolated_local_edit':break
            older=data['manifest']['head_proof']
            current=read(older['application_command_id'],older['proposal_id'])
            if current!=older:raise ValueError('Historical head chain differs')
        if proof is None:raise ValueError('Confirmed scoped head effect required')
        return proof

    def prepare_request(self,command_id,pid,doc,intent,key,oid,reference_version,mapping_version,application,proposal,choice,reason):
        value,record=self.snapshot(pid,doc,oid)
        rows=[r for r in value['proposals'] if r['source_key']==key]
        if len(rows)!=1:raise ValueError('Selected ID must exist exactly once')
        payload=canonical(rows[0])
        return envelope(command_id,'PREPARE_ISOLATED_LOCAL_EDIT_TASK',pid,doc,intent_id=identity(intent),source_key=key,
            observation_id=identity(oid),content_sha256=record['content_sha256'],preview_sha256=record['preview_sha256'],
            snapshot_row_sha256=hashlib.sha256(payload).hexdigest(),expected_reference_version=reference_version,
            expected_mapping_version=mapping_version,head_application_command_id=identity(application),head_proposal_id=identity(proposal),choice=choice,reason=reason),payload

    def artifact(self,pid,doc,kind,key):
        if kind not in ('proposal','package'):raise ValueError('Unknown isolated artifact')
        args=[sql_text(identity(pid))+'::uuid',sql_text(identity(doc))+'::uuid',sql_text(identity(key))+'::uuid' if kind=='proposal' else sql_text(key)]
        return self.query('SELECT d5.read_isolated_local_edit_'+kind+'('+','.join(args)+');')

    def verify_manifest(self,pid,doc,proposal_id,digest,verify_head=True):
        data=self.artifact(pid,doc,'proposal',proposal_id)
        if not data or data['manifest_sha256']!=digest:raise ValueError('Isolated manifest scope/hash mismatch')
        m=data['manifest'];i=m['intent'];hp=m['head_proof']
        req,payload=self.prepare_request(proposal_id,pid,doc,i['intent_id'],i['source_key'],m['observation_id'],m['reference_version'],m['mapping_version'],hp['application_command_id'],hp['proposal_id'],m['choice'],m['reason'])
        row=json.loads(payload);projection=dict(title=row['fields']['item'],description=row['fields']['objective'])
        local={k:m['target'][k] for k in ('title','description')};choice=m['choice']
        result=projection if choice=='USE_SOURCE' else local
        action='PATCH_ISOLATED_LOCAL_USE_SOURCE' if choice=='USE_SOURCE' else 'KEEP_ISOLATED_LOCAL'
        if m['schema']!='d5.isolated-local-edit-task-manifest.v1' or m['mode']!='ISOLATED_LOCAL_EDIT' or choice not in ('USE_SOURCE','KEEP_LOCAL') \
          or m['proposal_id']!=proposal_id or m['snapshot_row']!=row or m['snapshot_row_sha256']!=req['snapshot_row_sha256'] \
          or m['content_sha256']!=req['content_sha256'] or m['preview_sha256']!=req['preview_sha256'] \
          or m['last_applied_basis']!=semantic(row) or m['after_basis']!=semantic(row) \
          or m['before_projection']!=projection or m['after_projection']!=projection or local==projection \
          or m['local_projection']!=local or m['result_projection']!=result or m['action']!=action \
          or hp['mapping_version_after']!=m['mapping_version'] or hp['source_present'] is not True \
          or hp['source_basis']!=m['last_applied_basis'] or hp['projection']!=projection \
          or m['target']['id']!=i['task_id'] or m['target']['project_id']!=pid or m['target']['task_key']!=i['task_key'] \
          or i['policy']!='d5.task-projection.v1':raise ValueError('Isolated manifest differs from reconstruction')
        if verify_head and self.head_proof(pid,doc,i['intent_id'],hp['application_command_id'],hp['proposal_id'])!=hp:
            raise ValueError('Head proof differs from history')
        return data

    def submit_isolated_local_edit(self,request,rowbytes=None):
        action=request['action']
        if self.role!=ENTRIES[action][1]:raise ValueError('Dedicated role required')
        pid,doc=request['project_id'],request['document_id']
        if action=='PREPARE_ISOLATED_LOCAL_EDIT_TASK':
            expected,payload=self.prepare_request(request['command_id'],pid,doc,request['intent_id'],request['source_key'],request['observation_id'],request['expected_reference_version'],request['expected_mapping_version'],request['head_application_command_id'],request['head_proposal_id'],request['choice'],request['reason'])
            if request!=expected or (rowbytes is not None and rowbytes!=payload):raise ValueError('Request differs from verified snapshot')
            self.head_proof(pid,doc,request['intent_id'],request['head_application_command_id'],request['head_proposal_id']);rowbytes=payload
        elif action=='REVIEW_ISOLATED_LOCAL_EDIT_TASK':self.verify_manifest(pid,doc,request['proposal_id'],request['manifest_sha256'])
        else:
            package=None if action=='PACKAGE_ISOLATED_LOCAL_EDIT_TASKS' else self.artifact(pid,doc,'package',request['package_sha256'])
            if action=='APPLY_ISOLATED_LOCAL_EDIT_TASKS' and package is None:raise ValueError('Isolated package not found')
            for pin in request['items'] if action=='PACKAGE_ISOLATED_LOCAL_EDIT_TASKS' else package['items']:
                self.verify_manifest(pid,doc,pin['proposal_id'],pin['manifest_sha256'])
        return self.query(isolated_local_edit_sql(request,rowbytes))


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
        result = IsolatedLocalEditClient(args.container, ENTRIES[request['action']][1]).submit_isolated_local_edit(request)
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        return 2 if result.get('status') == 'CONFLICT' else 0
    except (ValueError, KeyError, TypeError, RuntimeError, OSError, __import__('subprocess').SubprocessError):
        parser.exit(1, 'D5 isolated local edit failed; no success acknowledged\n')


if __name__ == '__main__':
    raise SystemExit(main())
