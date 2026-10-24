# SPDX-License-Identifier: GPL-3.0-only
"""I50 owned serial uncertainty controls; no previous harness or product is changed."""
import hashlib
import json
import multiprocessing
from pathlib import Path
import time
import uuid

from source_ingest.durable_store import DurableError
from testing.D5 import durable_support as T, relational_support as R
from testing.durable_concurrency.support import independent, canonical, digest, require, spec, open_client

CTX=multiprocessing.get_context('spawn')
CHILDREN=[]
RECORDS=[]
EXTRA_ROOTS=[]
WAIT_SECONDS,CASE_SECONDS,CAMPAIGN_SECONDS=20,120,900
MAX_EVENTS,MAX_EVENT_BYTES,MAX_RAW_BYTES=256,16*1024,8*1024*1024


def uid():return str(uuid.uuid4())


def inspect_files(value):
    root=value['store']
    client=root['client_path'] if value['path']=='T' else root['client']
    remote=root['remote_path'] if value['path']=='T' else root['remote']
    return dict(client=independent(client),remote=independent(remote))


def describe(value):
    state=value['state']
    return dict(head=value['head'],state_sha256=digest(state),receipts=len(state['receipts']),
                data_generation=state.get('data_generation'),pending=list(state.get('pending',{})),
                reviews={k:dict(version=v['version'],decision=v['decision']) for k,v in state.get('reviews',{}).items()},
                sends={sid:dict(status=v['status'],ledger_version=v['ledger_version'],attempts=v['attempts'],queries=v['queries'],proof_sha256=digest(v['proof']),hard_conflict=v['hard_conflict'],retry_tick=v['retry_tick']) for sid,v in state.get('sends',{}).items()},
                tickets={ticket:dict(status=p['status'],code=p['code'],proof_sha256=digest(p),remote_id=p['remote_id'],applied_version=p['applied_version']) for ticket,p in state.get('tickets',{}).items()},
                entities={eid:dict(version=v['version'],payload_sha256=digest(v['payload']),foreign_sha256=digest(v['foreign'])) for eid,v in state.get('entities',{}).items()},
                keys=state.get('keys',{}),
                local_tasks={tid:dict(row_version=v['row_version'],task_sha256=digest(v)) for tid,v in state.get('tasks',state.get('data',{}).get('entities',{})).items() if 'kind' not in v or v['kind']=='TASK'})


def receive(conn,timeout=WAIT_SECONDS):
    require(conn.poll(timeout),'CONTROL_TIMEOUT')
    try:return conn.recv()
    except EOFError:raise AssertionError('CONTROL_EOF') from None


def worker(value,job,conn):
    transport=dict(execute_wrapper_calls=0,execute_real_calls=0,lookup_wrapper_calls=0,lookup_real_calls=0,
                   failure_phase=None,returned_proof_sha256=None,proof_input_type=None,proof_input_cardinality=None)
    try:
        if job['action']=='file_reader':
            out=inspect_files(value)
        else:
            c=open_client(value)
            execute,lookup=c.remote.execute,c.remote.lookup
            def wrapped_execute(*args,**kwargs):
                transport['execute_wrapper_calls']+=1
                if job.get('fault')=='execute_before':
                    transport['failure_phase']='LOSS_BEFORE_REAL_CALL';raise OSError('SYNTHETIC_LOSS')
                transport['execute_real_calls']+=1;result=execute(*args,**kwargs)
                transport['returned_proof_sha256']=digest(result)
                if job.get('fault')=='execute_after':
                    transport['failure_phase']='LOSS_AFTER_REAL_COMMIT';raise OSError('SYNTHETIC_LOSS')
                return result
            def wrapped_lookup(*args,**kwargs):
                transport['lookup_wrapper_calls']+=1
                if job.get('fault')=='lookup_before':
                    transport['failure_phase']='LOSS_BEFORE_REAL_CALL';raise OSError('SYNTHETIC_LOSS')
                transport['lookup_real_calls']+=1;result=lookup(*args,**kwargs)
                transport['returned_proof_sha256']=digest(result);return result
            def invalid_proof(proof):
                require(type(proof) is dict,'PROOF_SETUP_REQUIRED')
                if job['invalid']=='list':result=[proof,proof]
                elif job['invalid']=='envelope':
                    match=dict(remote_id=proof['remote_id'],creation_key=proof['creation_key'])
                    result=dict(matches=[match,match],proof=proof)
                else:
                    result=dict(proof,ticket=job['wrong_ticket'])
                transport['proof_input_type']=type(result).__name__
                transport['proof_input_cardinality']=2 if job['invalid'] in ('list','envelope') else None
                return result
            c.remote.execute,c.remote.lookup=wrapped_execute,wrapped_lookup
            try:
                if job['action']=='dispatch':out=c.dispatch(job['mid'],1,send_id=job['sid'],retry=job.get('retry',False),reject=job.get('reject'),retry_tick=job.get('retry_tick',0))
                elif job['action']=='reconcile':out=c.reconcile(job['sid'],proof_hook=invalid_proof if job.get('invalid') else None)
                elif job['action']=='issue':out=c.perform(**job['command'])
                elif job['action']=='execute':out=c.remote.execute(job['ticket'],job['manifest'])
                elif job['action']=='passive':
                    out=dict(snapshot=c.snapshot(),summary=c.summary(),reads=[])
                    for read in job.get('reads',[]):
                        store=c.store if read['role']=='CLIENT' else c.remote.store
                        out['reads'].append(store.read_command(read['cid'],read['request_hash']))
                elif job['action']=='clock':out=c.perform('CLOCK',dict(tick=job['tick']))
                else:raise AssertionError('UNKNOWN_ACTION')
            finally:c.remote.execute,c.remote.lookup=execute,lookup
        conn.send(dict(event='DONE',status='OK',value=out,transport=transport))
    except DurableError as ex:conn.send(dict(event='DONE',status='ERROR',code=str(ex),transport=transport))
    except Exception as ex:conn.send(dict(event='DONE',status='HARNESS_ERROR',code=type(ex).__name__))
    finally:conn.close()


def held_child(conn):
    conn.send(dict(event='READY'));conn.recv()


def normal_child(conn):
    conn.send(dict(event='DONE'));conn.close()


def empty_child(conn):conn.close()


def start(target,args,label):
    require(sum(p.is_alive() for p,_ in CHILDREN)<4,'CHILD_BUDGET')
    parent,child=CTX.Pipe();p=CTX.Process(target=target,args=(*args,child));p.start();child.close()
    CHILDREN.append((p,label));return p,parent


def stop_owned(pairs):
    for p,conn in pairs:
        if p.is_alive():p.kill()
        p.join(WAIT_SECONDS);conn.close()
    require(all(not p.is_alive() for p,_ in pairs),'CHILD_REMAINING')


def finish(p,conn):
    p.join(WAIT_SECONDS)
    if p.is_alive():stop_owned([(p,conn)]);raise AssertionError('CHILD_JOIN_TIMEOUT')
    conn.close();require(p.exitcode==0,'CHILD_EXIT')


class Scenario:
    def __init__(self,case,path):
        self.case,self.path=case,path;self.started=time.monotonic()
        self.events,self.oracles,self.children=[],[],[]
        self.lab=(T if path=='T' else R).new_lab();self.value=spec(self.lab,path)
        self.record=dict(case=case,path=path,run_id=self.lab.run_id,client_store_id=self.lab.client_id,remote_store_id=self.lab.remote_id,
                         status='RUNNING',events=self.events,oracles=self.oracles)
        RECORDS.append(self.record)

    def event(self,name,*,actor='parent',role='HARNESS',operation='CONTROL',mode='NONE',stage='NONE',point=None,order='NONE',round=1,**fields):
        require(time.monotonic()-self.started<CASE_SECONDS,'CASE_TIMEOUT')
        value=dict(event=name,case=self.case,path=self.path,actor=actor,role=role,operation=operation,mode=mode,stage=stage,
                   point=point or name,order=order,round=round,**fields)
        require(len(self.events)<MAX_EVENTS,'EVENT_BUDGET')
        require(len(canonical(value))<=MAX_EVENT_BYTES,'EVENT_SIZE_BUDGET');self.events.append(value)

    def observe(self,label):
        values=inspect_files(self.value)
        self.oracles.append(dict(label=label,**{k:describe(v) for k,v in values.items()}))
        self.event('ORACLE',operation='READ_FILES',point=label,hashes={k:digest(v['state']) for k,v in values.items()})
        return values

    def prepare(self):
        if self.path=='T':
            self.ids=T.ready(self.lab);self.mid=self.ids['projection']
        else:
            raw,targets=R.source(tasks=1);self.ids=R.prepare(self.lab,raw,targets);self.mid=self.ids['projections'][0]
        values=self.observe('projection_reviewed');self.before=values
        self.manifest=values['client']['state']['manifests'][self.mid]
        require(self.manifest['operation']=='CREATE','SETUP_NOT_CREATE')
        state=values['client']['state'];tid=self.manifest['target_id']
        require(state['reviews']['PROJECTION:'+self.mid]['version']==1 and state['reviews']['PROJECTION:'+self.mid]['decision']=='ACCEPT','SETUP_REVIEW')
        local=state['tasks'][tid] if self.path=='T' else state['data']['entities'][tid]
        require(local==self.manifest['task'],'SETUP_TASK_SNAPSHOT')
        require(self.manifest['remote_identity']==dict(run_id=self.lab.run_id,store_id=self.lab.remote_id),'SETUP_REMOTE_IDENTITY')
        require(self.manifest['capabilities']==values['remote']['state']['capabilities'],'SETUP_CAPABILITIES')
        if self.path=='R':
            receipt=state['receipts'][self.manifest['batch_command']]
            require(receipt['request_sha256']==self.manifest['batch_request'] and tid in receipt['result']['participants'],'SETUP_BATCH_RECEIPT')
        require(not values['client']['state']['sends'] and not values['remote']['state']['tickets'] and not values['remote']['state']['entities'],'SETUP_NOT_EMPTY')
        self.record['manifest']=dict(manifest_id=self.mid,manifest_sha256=digest(self.manifest),payload_sha256=digest(self.manifest['payload']),
                                     creation_key=self.manifest['creation_key'],target_id=self.manifest['target_id'],binding_id=self.manifest['binding']['binding_id'],review_version=1)

    def issue_job(self,cid,sid,ticket,expected=None):
        if expected is None:
            head=self.before['client']['head'];expected={k:head[k] for k in ('seq','commit_sha256')}
        args=dict(manifest_id=self.mid,review_version=1,send_id=sid,ticket=ticket,capabilities=self.manifest['capabilities'],retry=False)
        command=dict(kind='ISSUE',args=args,cid=cid,expected=expected)
        request=digest(dict(kind='ISSUE',args=args,expected=expected))
        return dict(action='issue',role='CLIENT',operation='ISSUE',mode='CREATE',stage='PROJECTION',command=command,cid=cid,request_hash=request)

    def execute_job(self,ticket,manifest=None):
        manifest=self.manifest if manifest is None else manifest
        cid=str(uuid.uuid5(uuid.UUID(self.lab.remote_id),'EXECUTE'+ticket+digest(manifest)))
        args=dict(ticket=ticket,manifest=manifest,run_id=self.lab.run_id,store_id=self.lab.remote_id,reject=None,retry_tick=0)
        return dict(action='execute',role='REMOTE',operation='EXECUTE',mode='CREATE',stage='PROJECTION',ticket=ticket,manifest=manifest,
                    cid=cid,request_hash=digest(dict(kind='EXECUTE',args=args,expected=None)))

    def spawn(self,job,label):
        pair=start(worker,(self.value,job),dict(case=self.case,path=self.path,actor=label,action=job['action']))
        self.children.append(pair)
        self.event('SPAWN',actor=label,role=job.get('role','HARNESS'),operation=job.get('operation',job['action']),mode=job.get('mode','NONE'),stage=job.get('stage','NONE'),
                   cid=job.get('cid'),request_sha256=job.get('request_hash'))
        return pair

    def run_job(self,job,label,expected_error=None,round=2):
        pair=self.spawn(job,label)
        try:
            event=receive(pair[1]);require(event.get('event')=='DONE','MISSING_DONE')
            require(event.get('status')==('ERROR' if expected_error else 'OK'),'WORKER_FAILURE')
            if expected_error:require(event['code']==expected_error,'WRONG_PRODUCT_ERROR')
            finish(*pair)
            self.event('DONE',actor=label,role=job.get('role','HARNESS'),operation=job.get('operation',job['action']),mode=job.get('mode','NONE'),stage=job.get('stage','NONE'),
                       round=round,status=event['status'],code=event.get('code'),output_sha256=digest(event.get('value')),transport=event['transport'],result=event.get('value') if job['action'] in ('dispatch','reconcile','issue','execute','clock') else None)
            return event
        finally:stop_owned([pair])

    def passive(self,reads=()):
        before=self.observe('before_passive')
        require(self.run_job(dict(action='file_reader'),'new_file_reader')['value']==before,'FILE_REOPEN_CHANGED')
        event=self.run_job(dict(action='passive',reads=list(reads)),'new_public_passive')
        require(all(event['transport'][key]==0 for key in ('execute_wrapper_calls','execute_real_calls','lookup_wrapper_calls','lookup_real_calls')),'PASSIVE_TRANSPORT_CALL')
        public=event['value']
        require(public['snapshot']==dict(head=before['client']['head'],state=before['client']['state']),'PUBLIC_REOPEN_CHANGED')
        require(self.observe('after_passive')==before,'PASSIVE_MUTATION')
        self.event('PASSIVE_UNCHANGED',operation='SNAPSHOT/READ_COMMAND',round=4,receipt_reads=[digest(r) for r in public['reads']])
        return public

    def close(self,successful):
        try:
            stop_owned(self.children);self.lab.close();require(not self.lab.home.exists(),'OWN_ROOT_REMAINS')
            if self.path=='T':require(not self.lab.capture.root.exists(),'OWN_CAPTURE_REMAINS')
            self.record['cleanup_verified']=True
        except Exception:self.record['cleanup_verified']=False;raise
        finally:
            self.record['status']='PASS' if successful and self.record.get('cleanup_verified') else 'FAIL'
            self.record['elapsed_seconds']=round(time.monotonic()-self.started,3)


def expect_error(code,call,*args,**kwargs):
    try:call(*args,**kwargs)
    except DurableError as ex:require(str(ex)==code,'WRONG_PRODUCT_ERROR');return
    raise AssertionError('EXPECTED_ERROR_ABSENT')


def hash_inputs(paths):return {str(p):hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sorted(paths)}


def validate_inventory(before,after):require(before==after,'STALE_INPUTS')


def validate_report(passed,expected,skipped,remaining):
    require(len(passed)==len(set(passed)),'DUPLICATE_TEST_IDS')
    require(set(passed)==set(expected) and not skipped,'INCOMPLETE_CAMPAIGN')
    require(remaining==0,'RESOURCES_REMAINING')


def bounded_raw(value,maximum=MAX_RAW_BYTES):
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    require(len(raw.encode())<=maximum,'RAW_BUDGET');return raw


def raw_binding(path,expected_sha256=None,maximum=MAX_RAW_BYTES):
    path=Path(path);require(path.is_file() and not path.is_symlink(),'RAW_MISSING_OR_TYPE')
    require(path.stat().st_size<=maximum,'RAW_BUDGET');raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None:require(sha==expected_sha256,'RAW_HASH_MISMATCH')
    try:report=json.loads(raw)
    except (ValueError,UnicodeError):raise AssertionError('RAW_INCOMPATIBLE') from None
    require(type(report) is dict and report.get('status')=='PASS' and type(report.get('passed')) is list and type(report.get('tests_run')) is int,'RAW_INCOMPATIBLE')
    require(report['tests_run']==len(report['passed'])==len(set(report['passed'])),'RAW_COUNTS')
    return dict(sha256=sha,bytes=len(raw),tests_run=report['tests_run'],schema=report.get('schema'))
