# SPDX-License-Identifier: GPL-3.0-only
"""I55 owned spawn workers and file oracles; no old roots are converted."""
import hashlib
import json
from pathlib import Path
import signal
import time
import uuid
from types import SimpleNamespace

from source_ingest import durable_ambiguity_fixture as n
from source_ingest.incremental_fixture import FixtureStore
from source_ingest.durable_store import DurableError
from testing.D5 import durable_support as T,relational_support as R
from testing.durable_concurrency.support import independent,require,canonical,digest
from testing.durable_uncertainty import support as controls

WAIT_SECONDS,CASE_SECONDS,CAMPAIGN_SECONDS=20,120,900
MAX_EVENTS,MAX_EVENT_BYTES,MAX_RAW_BYTES=256,65536,12*1024*1024
RECORDS=[]
CHILDREN=controls.CHILDREN
EXTRA_ROOTS=[]
uid=controls.uid
start,finish,stop_owned,receive=controls.start,controls.finish,controls.stop_owned,controls.receive
expect_error,hash_inputs,validate_inventory,validate_report=controls.expect_error,controls.hash_inputs,controls.validate_inventory,controls.validate_report


def spec(lab):
    value=dict(client=str(lab.root/'client'),remote=str(lab.root/'remote'),run_id=lab.run_id,
        client_id=lab.client_id,remote_id=lab.remote_id,variant=lab.variant)
    if lab.capture:value.update(capture=str(lab.capture.root),capture_run=lab.capture.run_id,scope=lab.scope)
    return value


def open_client(v,hook=None):
    cap=FixtureStore(v['capture'],v['capture_run'],v['scope']) if 'capture' in v else None
    remote=n.Remote(v['remote'],v['run_id'],v['remote_id'])
    return n.Client(v['client'],v['run_id'],v['client_id'],remote,capture=cap,variant=v['variant'],hook=hook)


def files(v):return {role:independent(v[role]) for role in ('client','remote')}


def core(value):
    # File oracle materialization, no fixture function/reducer or Store replay.
    return dict(value['state']['core'],receipts=value['state']['receipts'])


def describe(v):
    s=v['state'];c=core(v)
    out=controls.describe(dict(head=v['head'],state=c))
    out.update(outer_sha256=digest(s),core_sha256=digest(s['core']),config_sha256=digest(s['config']),
        receipt_requests={k:r['request_sha256'] for k,r in c['receipts'].items()},manifests={k:digest(m) for k,m in c.get('manifests',{}).items()},
        extension=s['extension'])
    return out


def expected_ready(message,expected):
    require(type(message) is dict and message.get('event')=='READY','MISSING_READY')
    require(all(message.get(k)==v for k,v in expected.items()),'READY_IDENTITY')


def worker(v,job,conn):
    command=None;c=None
    def hook(point):
        if job.get('crash')=='after_head' and command is not None and point=='after_head':hold(point)
    def hold(point):
        conn.send(dict(event='READY',role='CLIENT',variant=v['variant'],operation='OBSERVE',point=point,
            run_id=v['run_id'],client_store_id=v['client_id'],remote_store_id=v['remote_id'],ticket=job['ticket'],
            send_id=job['sid'],manifest_id=job['mid'],cid=job['cid'],command=command))
        conn.recv()
        raise AssertionError('CRASH_NOT_KILLED')
    try:
        if job['action']=='files':out=files(v)
        else:
            c=open_client(v,hook);action=job['action'];args=job.get('args',{})
            if action=='passive':out=dict(snapshot=c.snapshot())
            elif action=='dispatch':out=c.dispatch(**args)
            elif action=='reconcile':out=c.reconcile(**args)
            elif action=='query':out=c.begin_query(**args)
            elif action=='observe':out=c.observe(**args)
            elif action=='execute':out=c.remote.execute_response(**args)
            elif action=='declare':out=c.remote.declare_view(**args)
            elif action=='core':out=c.core.perform(**args)
            elif action=='crash':
                q=c.begin_query(job['sid']);snap=c.snapshot()
                command=dict(sid=q['sid'],ledger=q['ledger'],envelope=q['envelope'],query_id=q['query_id'],cid=job['cid'],
                    expected={k:snap['head'][k] for k in ('seq','commit_sha256')})
                if job['crash']=='before_observe':hold('before_observe')
                out=c.observe(**command)
            else:raise AssertionError('UNKNOWN_ACTION')
        conn.send(dict(event='DONE',status='OK',value=out,calls=c.remote.calls if c else dict(execute=0,query=0)))
    except DurableError as ex:conn.send(dict(event='DONE',status='ERROR',code=str(ex),calls=c.remote.calls if c else dict(execute=0,query=0)))
    except Exception as ex:conn.send(dict(event='DONE',status='HARNESS_ERROR',code=type(ex).__name__))
    finally:conn.close()


class Scenario:
    def __init__(self,case,path,*,proof_bytes=None):
        self.case,self.path=case,path;self.started=time.monotonic();self.events=[];self.oracles=[];self.children=[]
        helper=T if path=='T' else R;base=(n.T if path=='T' else n.R).config(*[helper.uid(i) for i in range(1,5)])
        if proof_bytes is not None:base['limits']['proof_bytes']=proof_bytes
        self.lab=n.NativeLab(n.config('NATIVE_'+path,base));self.value=spec(self.lab)
        self.record=dict(case=case,path=path,variant=self.lab.variant,run_id=self.lab.run_id,
            client_store_id=self.lab.client_id,remote_store_id=self.lab.remote_id,status='RUNNING',events=self.events,oracles=self.oracles)
        RECORDS.append(self.record)
    def __enter__(self):return self
    def __exit__(self,typ,*_):self.close(typ is None)
    def event(self,event,**fields):
        require(time.monotonic()-self.started<CASE_SECONDS,'CASE_TIMEOUT')
        value=dict(event=event,case=self.case,path=self.path,variant=self.lab.variant,**fields)
        require(len(self.events)<MAX_EVENTS,'EVENT_BUDGET');require(len(canonical(value))<=MAX_EVENT_BYTES,'EVENT_SIZE_BUDGET');self.events.append(value)
    def observe(self,label):
        values=files(self.value);self.oracles.append(dict(label=label,**{k:describe(v) for k,v in values.items()}))
        self.event('ORACLE',point=label,state_hashes={k:digest(v['state']) for k,v in values.items()});return values
    def prepare(self):
        proxy=SimpleNamespace(client=self.lab.client.core,capture=self.lab.capture,scope=getattr(self.lab,'scope',None))
        if self.path=='T':self.ids=T.ready(proxy);self.mid=self.ids['projection']
        else:
            raw,targets=R.source(tasks=1);self.ids=R.prepare(proxy,raw,targets);self.mid=self.ids['projections'][0]
        values=self.observe('projection_reviewed');c=core(values['client']);self.manifest=c['manifests'][self.mid]
        require(self.manifest['operation']=='CREATE','SETUP_CREATE')
        require(c['reviews']['PROJECTION:'+self.mid]==dict(version=1,decision='ACCEPT',reason_code='SYNTHETIC_REVIEW'),'SETUP_REVIEW')
        tid=self.manifest['target_id'];task=c['tasks'][tid] if self.path=='T' else c['data']['entities'][tid]
        require(task==self.manifest['task'],'SETUP_TASK')
        require(self.manifest['remote_identity']==dict(run_id=self.lab.run_id,store_id=self.lab.remote_id),'SETUP_IDENTITY')
        require(self.manifest['capabilities']==core(values['remote'])['capabilities'],'SETUP_CAPABILITIES')
        if self.path=='T':
            require(all(self.ids[k] in c['manifests'] for k in ('evaluation','effect','projection')),'SETUP_T_AUTHORITY')
            require(c['sources'][self.ids['source']]['pin']['run_id']==self.lab.capture.run_id,'SETUP_CAPTURE_PIN')
        else:
            r=c['receipts'][self.manifest['batch_command']]
            require(r['request_sha256']==self.manifest['batch_request'] and tid in r['result']['participants'],'SETUP_BATCH_RECEIPT')
            require(tid in c['selection']['task_ids'],'SETUP_SELECTION')
        require(not c['sends'] and not core(values['remote'])['entities'],'SETUP_EMPTY')
        self.record['manifest']=dict(manifest_id=self.mid,manifest_sha256=digest(self.manifest),creation_key=self.manifest['creation_key'],
            payload_sha256=digest(self.manifest['payload']),target_id=tid,binding_id=self.manifest['binding']['binding_id'],review_version=1)
    def call(self,action,args=None,error=None,**extra):
        job=dict(action=action,args=args or {},**extra);pair=start(worker,(self.value,job),dict(case=self.case,action=action,path=self.path));self.children.append(pair)
        try:
            e=receive(pair[1]);require(e.get('event')=='DONE','MISSING_DONE')
            require(e.get('status')==('ERROR' if error else 'OK'),'WORKER_FAILURE_'+str(e.get('code')))
            if error:require(e['code']==error,'WRONG_PRODUCT_ERROR_'+str(e['code']))
            finish(*pair)
            self.event('DONE',operation=action,status=e['status'],code=e.get('code'),calls=e['calls'],
                result=e.get('value') if action not in ('files','passive') else None,output_sha256=digest(e.get('value')))
            return e
        finally:stop_owned([pair])
    def issue(self):
        out=self.call('dispatch',dict(mid=self.mid,review_version=1,deliver=False))['value'];self.sid,self.ticket=out['send_id'],out['ticket']
        self.record['send_id'],self.record['ticket']=self.sid,self.ticket
        return out
    def deliver(self,mode='SUCCESS',tick=None):return self.call('execute',dict(ticket=self.ticket,m=self.manifest,mode=mode,retry_after_tick=tick))['value']
    def dispatch(self,mode,tick=None):
        e=self.call('dispatch',dict(mid=self.mid,review_version=1,mode=mode,retry_after_tick=tick));out=e['value'];self.sid,self.ticket=out['send_id'],out['ticket']
        self.record['send_id'],self.record['ticket']=self.sid,self.ticket;return e
    def declare(self,matches,**extra):return self.call('declare',dict(key=self.manifest['creation_key'],matches=matches,**extra))
    def match(self,**changes):
        return dict(remote_id=uid(),creation_key=self.manifest['creation_key'],scope_hash=n.scope_hash(self.lab.config),
            version=1,payload_hash=digest(self.manifest['payload']),**changes) if not changes else dict(self.match(),**changes)
    def query(self):return self.call('query',dict(sid=self.sid))['value']
    def observe_query(self,q,**extra):return self.call('observe',dict(sid=q['sid'],ledger=q['ledger'],envelope=q['envelope'],query_id=q['query_id'],**extra))
    def reconcile(self):return self.call('reconcile',dict(sid=self.sid))
    def passive(self):
        before=self.observe('before_passive')
        require(self.call('files')['value']==before,'FILE_REOPEN_CHANGED')
        out=self.call('passive');require(out['calls']==dict(execute=0,query=0),'PASSIVE_TRANSPORT')
        require(out['value']['snapshot']==dict(head=before['client']['head'],state=before['client']['state']),'PUBLIC_REOPEN_CHANGED')
        require(self.observe('after_passive')==before,'PASSIVE_MUTATION');self.event('PASSIVE_UNCHANGED')
    def crash(self,point):
        job=dict(action='crash',crash=point,sid=self.sid,ticket=self.ticket,mid=self.mid,cid=uid())
        pair=start(worker,(self.value,job),dict(case=self.case,action='crash',point=point,path=self.path));self.children.append(pair)
        try:
            e=receive(pair[1]);expected=dict(role='CLIENT',variant=self.lab.variant,operation='OBSERVE',point=point,run_id=self.lab.run_id,
                client_store_id=self.lab.client_id,remote_store_id=self.lab.remote_id,ticket=self.ticket,send_id=self.sid,manifest_id=self.mid,cid=job['cid'])
            expected_ready(e,expected);self.event('READY',**{k:v for k,v in e.items() if k not in ('event','variant')})
            pair[0].kill();pair[0].join(WAIT_SECONDS);require(pair[0].exitcode==-signal.SIGKILL,'NOT_SIGKILL')
            self.event('KILLED',point=point,exitcode=pair[0].exitcode);return e['command']
        finally:stop_owned([pair])
    def close(self,success):
        try:
            stop_owned(self.children);self.lab.close();require(not self.lab.home.exists(),'OWN_ROOT_REMAINS')
            if self.lab.capture:require(not self.lab.capture.root.exists(),'OWN_CAPTURE_REMAINS')
            self.record['cleanup_verified']=True
        finally:
            self.record['status']='PASS' if success and self.record.get('cleanup_verified') else 'FAIL'
            self.record['elapsed_seconds']=round(time.monotonic()-self.started,3)


def bounded_raw(value,maximum=MAX_RAW_BYTES):
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    require(len(raw.encode())<=maximum,'RAW_BUDGET');return raw


def raw_binding(path,expected_sha256=None,maximum=MAX_RAW_BYTES):
    path=Path(path);require(path.is_file() and not path.is_symlink(),'RAW_MISSING_OR_TYPE')
    require(path.stat().st_size<=maximum,'RAW_BUDGET');raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None:require(sha==expected_sha256,'RAW_HASH_MISMATCH')
    def pairs(items):
        out={}
        for key,value in items:
            if key in out:raise ValueError('DUPLICATE_KEY')
            out[key]=value
        return out
    def invalid_constant(value):raise ValueError('INVALID_CONSTANT')
    try:report=json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid_constant)
    except (ValueError,UnicodeError):raise AssertionError('RAW_INCOMPATIBLE') from None
    require(type(report) is dict and report.get('status')=='PASS' and type(report.get('passed')) is list and type(report.get('tests_run')) is int,'RAW_INCOMPATIBLE')
    require(all(type(v) is str for v in report['passed']),'RAW_INCOMPATIBLE')
    require(report['tests_run']==len(report['passed'])==len(set(report['passed'])),'RAW_COUNTS')
    return dict(sha256=sha,bytes=len(raw),tests_run=report['tests_run'],schema=report.get('schema'))
