# SPDX-License-Identifier: GPL-3.0-only
"""I61 causal cells: public calls, owned spawn workers, unchanged Store hooks."""
import hashlib
import json
from pathlib import Path
import signal
import time
import uuid

from source_ingest.durable_store import DurableError
from testing.D5 import durable_support as T, relational_support as R
from testing.durable_crash_boundaries import support as H
from testing.durable_frontier_gaps import support as F
from testing.durable_concurrency.support import independent, canonical, digest, require

CHILDREN=H.CHILDREN
RECORDS=[]
EXTRA_ROOTS=[]
WAIT_SECONDS,CASE_SECONDS,CAMPAIGN_SECONDS=20,120,900
MAX_EVENTS,MAX_EVENT_BYTES,MAX_RAW_BYTES=256,16384,12*1024*1024
uid,spec,roots=H.uid,H.spec,H.roots
start,finish,stop_owned,receive=H.start,H.finish,H.stop_owned,H.receive
hash_inputs,validate_inventory,validate_report,expect_error=H.hash_inputs,H.validate_inventory,H.validate_report,H.expect_error
validate_gate=F.validate_gate
bounded_raw,raw_binding=F.bounded_raw,F.raw_binding


def plan():return json.loads(Path('docs/validation/D5-I60-design-review.json').read_text())


def remote_command(value,ticket,m,close):
    kind='CLOSE' if close else 'EXECUTE'
    args=dict(ticket=ticket,manifest=m,run_id=value['store']['run_id'],store_id=value['store']['remote_id'],reject=None,retry_tick=0)
    cid=str(uuid.uuid5(uuid.UUID(value['store']['remote_id']),kind+ticket+digest(m)))
    return dict(kind=kind,args=args,cid=cid,expected=None)


def worker(value,job,conn):
    transport=dict(lookup=0,execute=0,proof_sha256=None)
    armed=False;command=None;identity={}
    def hook(point):
        if not armed or point!=job.get('point'):return
        conn.send(dict(event='READY',case=job['case'],path=value['path'],role=job['role'],
            run_id=value['store']['run_id'],client_store_id=value['store']['client_id'],remote_store_id=value['store']['remote_id'],
            operation=command['kind'],logical_operation=job['logical_operation'],stage=job['stage'],point=point,
            cid=command['cid'],args_sha256=digest(command['args']),expected=command['expected'],
            request_sha256=digest({k:command[k] for k in ('kind','args','expected')}),transport=dict(transport),**identity))
        conn.recv();raise AssertionError('CRASH_NOT_KILLED')
    try:
        action=job['action']
        if action=='files':out=H.inspect_files(value)
        else:
            c=(T if value['path']=='T' else R).open_client(value['store'],
                hook if action=='crash' and job['role']=='CLIENT' else None,
                hook if action=='crash' and job['role']=='REMOTE' else None)
            original_lookup,original_execute=c.remote.lookup,c.remote.execute
            def lookup(*a,**kw):
                transport['lookup']+=1;p=original_lookup(*a,**kw);transport['proof_sha256']=digest(p);return p
            def execute(*a,**kw):
                transport['execute']+=1;return original_execute(*a,**kw)
            c.remote.lookup,c.remote.execute=lookup,execute
            try:
                if action=='passive':
                    out=dict(snapshot=c.snapshot(),remote=c.remote.snapshot(),summary=c.summary(),reads=[])
                    for r in job.get('reads',[]):out['reads'].append((c.remote.store if r['role']=='REMOTE' else c.store).read_command(r['cid'],r['request_hash']))
                elif action in ('crash','replay','remote_repeat'):
                    state=c.snapshot()['state'];mid=job.get('mid');m=state['manifests'][mid] if mid else None
                    sid,ticket,qid=job.get('sid'),job.get('ticket'),job.get('qid')
                    if sid and job['logical_operation']!='ISSUE':
                        send=state['sends'][sid];require(send['manifest_id']==mid and send['attempts'][-1]==ticket,'ATTEMPT_IDENTITY')
                    if job.get('remote_spec'):
                        close=job['remote_spec']['close'];command=remote_command(value,ticket,m,close)
                        mode='CLOSE' if close else m['operation']
                    elif job.get('result_spec'):
                        r=job['result_spec'];proof=c.remote.lookup(ticket,m);require(proof is not None,'PROOF_MISSING')
                        command=dict(kind='RESULT',cid=r['cid'],expected=r['expected'],args=dict(send_id=sid,ledger_version=r['ledger'],proof=proof,query_id=qid));mode=m['operation']
                    else:command=job['command'];mode=m.get('operation','LOCAL') if m else 'LOCAL'
                    identity=dict(mode=mode,manifest_operation=m.get('operation') if m else None,manifest_id=mid,
                        manifest_sha256=digest(m) if m else None,creation_key=m.get('creation_key') if m else None,
                        binding_id=m['binding']['binding_id'] if m and 'binding' in m else None,target_id=m['target_id'] if m else None,
                        remote_base_sha256=digest(m.get('remote_base')) if m else None,
                        send_id=sid,ticket=ticket,query_id=qid,ledger=state['sends'][sid]['ledger_version'] if sid and job['logical_operation']!='ISSUE' else None,
                        capabilities_sha256=digest(m['capabilities']) if m and 'capabilities' in m else None)
                    armed=action=='crash'
                    out=c.remote.execute(ticket,m,close=job['remote_spec']['close']) if job.get('remote_spec') else c.perform(**command)
                elif action=='reconcile':out=c.reconcile(job['sid'],close=job.get('close',False))
                elif action=='query_result':
                    v=c.snapshot()['state']['sends'][job['sid']];m=c.snapshot()['state']['manifests'][v['manifest_id']]
                    p=c.remote.lookup(v['attempts'][-1],m);require(p is not None,'PROOF_MISSING')
                    out=c.perform('RESULT',dict(send_id=job['sid'],ledger_version=v['ledger_version'],query_id=job['qid'],proof=p))
                elif action=='clock':out=c.perform('CLOCK',dict(tick=job['tick']))
                else:raise AssertionError('UNKNOWN_ACTION')
            finally:c.remote.lookup,c.remote.execute=original_lookup,original_execute
        conn.send(dict(event='DONE',status='OK',value=out,transport=transport))
    except Exception as ex:
        code=str(ex) if isinstance(ex,(DurableError,AssertionError)) and str(ex).replace('_','').isalnum() else type(ex).__name__
        conn.send(dict(event='DONE',status='ERROR',code=code,transport=transport))
    finally:conn.close()


class Scenario(F.Scenario):
    def __init__(self,row):
        self.row=row;self.case=row['id'];self.path=row['path'];self.started=time.monotonic()
        self.events,self.oracles,self.children=[],[],[];self.ids={}
        self.lab=(T if self.path=='T' else R).new_lab();self.value=spec(self.lab,self.path)
        self.record=dict(case=self.case,path=self.path,frontier_row=row.get('frontier_row'),frontier=row.get('frontier','CONTROL'),
            logical_operation=row.get('operation','CONTROL'),role=row['role'],stage=row.get('stage','CONTROL'),mode=row.get('mode','CONTROL'),point=row.get('point','CONTROL'),
            run_id=self.lab.run_id,client_store_id=self.lab.client_id,remote_store_id=self.lab.remote_id,events=self.events,oracles=self.oracles,status='RUNNING')
        RECORDS.append(self.record)
    def event(self,event,**fields):
        require(time.monotonic()-self.started<CASE_SECONDS,'CASE_TIMEOUT')
        value=dict(event=event,case=self.case,path=self.path,**fields)
        require(len(self.events)<MAX_EVENTS,'EVENT_BUDGET');require(len(canonical(value))<=MAX_EVENT_BYTES,'EVENT_SIZE_BUDGET');self.events.append(value)
    def observe(self,label):
        values=super().observe(label)
        for role,v in values.items():
            self.oracles[-1][role].update(keys_sha256=digest(v['state'].get('keys')),ticket_values=v['state'].get('tickets',{}),
                remote_entities=v['state'].get('entities',{}))
        return values
    def set_target(self,command):
        self.cmd=command;self.read=dict(role=self.row['role'],cid=command['cid'],request_hash=digest({k:command[k] for k in ('kind','args','expected')}))
        self.record['command']=dict(cid=command['cid'],kind=command['kind'],args_sha256=digest(command['args']),expected=command['expected'],request_sha256=self.read['request_hash'])
    def prepare(self):
        c=self.lab.client;op=self.row['operation'];self.mid=self.sid=self.ticket=self.qid=None
        if op=='APPLY':
            self.ids=T.ready(self.lab,apply=False,projection=False)
            self.mid=self.ids['effect'];self.set_command('APPLY',dict(manifest_id=self.mid,review_version=1));self.set_target(self.cmd)
            manifest=c.snapshot()['state']['manifests'][self.mid];self.record['local_manifest']=dict(manifest_id=self.mid,manifest_sha256=digest(manifest),stage=manifest['stage'],target_id=manifest['target_id'])
        else:
            if self.path=='T':self.ids=T.ready(self.lab);self.mid=self.ids['projection'];self.tid=T.uid(30);self.bid=T.uid(40)
            else:
                raw,targets=R.source(tasks=1);self.ids=R.prepare(self.lab,raw,targets);self.mid=self.ids['projections'][0];self.tid=self.ids['task_ids'][0];self.bid=self.ids['bindings'][0]
                self.record['batch']=dict(command_id=self.ids['apply']['command_id'],request_sha256=self.ids['apply']['request_sha256'],task_id=self.tid)
            if self.row['mode']=='UPDATE':
                old=c.dispatch(self.mid,1)
                state=self.lab.remote.snapshot()['state'];rid=next(iter(state['entities']))
                create_entity=state['entities'][rid];edit=self.lab.remote.edit(rid,foreign=dict(sentinel='CE_KEEP'))
                self.record['update_setup']=dict(create_send=old['send_id'],create_ticket=old['ticket'],create_receipt=old['receipt'],create_entity=create_entity,foreign_edit_receipt=edit)
                if self.path=='T':
                    # Explicitly approved I61 amendment: update source/base together, never bypass LOCAL_DIVERGENCE.
                    commit=T.capture(self.lab,data=T.DATA.replace(b'Synthetic item',b'Causal UPDATE payload'))
                    source=c.import_event(commit)['result']['source_id'];c.review('SOURCE',source)
                    em=c.perform('PREPARE_EVALUATION',dict(source_id=source,source_review=1,account_id=self.ids['account']))['result']['manifest_id'];c.review('EVALUATION',em)
                    ef=c.perform('PREPARE_EFFECT',dict(evaluation=em,evaluation_review=1,source_key='FIX-1',target_id=self.tid,target_key='FIXTURE-1'))['result']['manifest_id'];c.review('EFFECT',ef)
                    applied=c.perform('APPLY',dict(manifest_id=ef,review_version=1));self.ids.update(source=source,evaluation=em,effect=ef,apply=applied)
                    self.record['update_setup']['new_source_apply']=dict(command_id=applied['command_id'],request_sha256=applied['request_sha256'],capture_commit=commit)
                else:
                    raw,targets=R.source(tasks=1,revision='ce-update');data=json.loads(raw);data['elements'][2]['title']='Causal UPDATE payload'
                    self.ids.update(R.prepare(self.lab,canonical(data),targets,project=False))
                    self.record['batch']=dict(command_id=self.ids['apply']['command_id'],request_sha256=self.ids['apply']['request_sha256'],task_id=self.tid)
                self.mid=c.prepare_projection(self.bid)['result']['manifest_id'];c.review('PROJECTION',self.mid)
            m=c.snapshot()['state']['manifests'][self.mid]
            if op=='ISSUE':
                self.sid,self.ticket=uid(),uid()
                self.set_command('ISSUE',dict(manifest_id=self.mid,review_version=1,send_id=self.sid,ticket=self.ticket,capabilities=m['capabilities'],retry=False));self.set_target(self.cmd)
            else:
                out=c.dispatch(self.mid,1,deliver=False);self.sid,self.ticket=out['send_id'],out['ticket']
                if op in ('QUERY','RESULT_DISPATCH'):
                    self.proof=self.lab.remote.execute(self.ticket,m)
                    if op=='QUERY':
                        self.qid=uid();self.set_command('QUERY',dict(send_id=self.sid,query_id=self.qid,ledger_version=1))
                    else:self.set_command('RESULT',dict(send_id=self.sid,query_id=None,ledger_version=1,proof=self.proof))
                    self.set_target(self.cmd)
                else:self.set_target(remote_command(self.value,self.ticket,m,self.row['mode']=='CLOSE'))
            self.record['attempt']=dict(manifest_id=self.mid,manifest_sha256=digest(m),manifest_operation=m['operation'],creation_key=m['creation_key'],
                binding_id=self.bid,target_id=self.tid,send_id=self.sid,ticket=self.ticket,query_id=self.qid,remote_base_sha256=digest(m['remote_base']),capabilities_sha256=digest(m['capabilities']))
        if self.path=='T':
            src=c.snapshot()['state']['sources'][self.ids['source']]
            self.record['capture']=dict(pin=src['pin'],source_bytes_sha256=src['capture']['content_sha256'],grade=src['capture']['provenance_grade'])
        self.record['ids']={k:v for k,v in self.ids.items() if k not in ('raw','targets','apply')}
        self.before=self.observe('precondition');return self.before
    def job(self,action='crash'):
        job=dict(action=action,case=self.case,role=self.row['role'],logical_operation=self.row['operation'],stage=self.row['stage'],point=self.row['point'],mid=self.mid,sid=self.sid,ticket=self.ticket,qid=self.qid)
        if self.row['role']=='REMOTE':job['remote_spec']=dict(close=self.row['mode']=='CLOSE')
        elif self.row['operation']=='RESULT_DISPATCH':job['result_spec']=dict(cid=self.cmd['cid'],expected=self.cmd['expected'],ledger=1)
        else:job['command']=self.cmd
        require('proof' not in job.get('result_spec',{}),'PARENT_PROOF_AUTHORITY');return job
    def run(self,job):
        pair=start(worker,(self.value,job),dict(case=self.case,path=self.path,action=job['action']));self.children.append(pair)
        try:
            e=receive(pair[1]);require(e.get('event')=='DONE' and e.get('status')=='OK',e.get('code','WORKER_FAILURE'));finish(*pair)
            self.event('DONE',operation=job['action'],transport=e['transport'],output_sha256=digest(e['value']),result=e['value'] if job['action'] not in ('passive','files') else None);return e
        finally:stop_owned([pair])
    def crash(self):
        job=self.job();pair=start(worker,(self.value,job),dict(case=self.case,path=self.path,action='crash'));self.children.append(pair)
        m=self.before['client']['state']['manifests'][self.mid] if self.mid else None
        expected=dict(role=self.row['role'],run_id=self.lab.run_id,client_store_id=self.lab.client_id,remote_store_id=self.lab.remote_id,
            operation=self.cmd['kind'],logical_operation=self.row['operation'],stage=self.row['stage'],mode=self.row['mode'],point=self.row['point'],
            cid=self.cmd['cid'],args_sha256=digest(self.cmd['args']),expected=self.cmd['expected'],request_sha256=self.read['request_hash'],
            manifest_operation=m.get('operation') if m else None,manifest_id=self.mid,manifest_sha256=digest(m) if m else None,
            creation_key=m.get('creation_key') if m else None,binding_id=m['binding']['binding_id'] if m and 'binding' in m else None,
            target_id=m['target_id'] if m else None,remote_base_sha256=digest(m.get('remote_base')) if m else None,
            capabilities_sha256=digest(m['capabilities']) if m and 'capabilities' in m else None,
            send_id=self.sid,ticket=self.ticket,query_id=self.qid,ledger=self.before['client']['state']['sends'][self.sid]['ledger_version'] if self.sid and self.row['operation']!='ISSUE' else None)
        try:
            e=receive(pair[1]);validate_gate(e,job,self.value,expected)
            require(e['transport']['execute']==int(self.row['role']=='REMOTE') and e['transport']['lookup']==int(self.row['operation']=='RESULT_DISPATCH'),'GATE_TRANSPORT')
            if self.row['operation']=='RESULT_DISPATCH':require(e['transport']['proof_sha256']==digest(self.proof),'REAL_PROOF_MISMATCH')
            self.event('READY',**{k:v for k,v in e.items() if k not in ('event','case','path')});self.observe('gate')
            pair[0].kill();finish(*pair,expected=-signal.SIGKILL);self.event('SIGKILL',exitcode=pair[0].exitcode,point=self.row['point'])
        finally:stop_owned([pair])
        return self.observe('after_sigkill')
    def passive(self):
        before=self.observe('before_passive');require(self.run(dict(action='files'))['value']==before,'FRESH_FILE_READER_CHANGED')
        e=self.run(dict(action='passive',reads=[self.read] if hasattr(self,'read') else []));require(e['transport']['lookup']==e['transport']['execute']==0,'PASSIVE_TRANSPORT')
        for role,key in [('client','snapshot'),('remote','remote')]:require(e['value'][key]==dict(head=before[role]['head'],state=before[role]['state']),'PUBLIC_REOPEN_CHANGED')
        require(self.observe('after_passive')==before,'PASSIVE_MUTATION');self.event('PASSIVE_UNCHANGED',read_receipt_hashes=[digest(r) for r in e['value']['reads']]);return e['value']
