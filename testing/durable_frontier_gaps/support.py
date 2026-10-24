# SPDX-License-Identifier: GPL-3.0-only
"""I58 first-publication frontiers; only public legacy T/R calls and existing hooks."""
import hashlib
import json
from pathlib import Path
import signal
import time

from source_ingest.durable_store import DurableError
from source_ingest import eligibility_fixture as q
from testing.D5 import durable_support as T,relational_support as R
from testing.durable_concurrency.support import independent,canonical,digest,require
from testing.durable_crash_boundaries import support as H
from testing.durable_native_ambiguity.support import raw_binding as strict_raw_binding

CHILDREN=H.CHILDREN
RECORDS=[]
EXTRA_ROOTS=[]
WAIT_SECONDS,CASE_SECONDS,CAMPAIGN_SECONDS=20,120,900
MAX_EVENTS,MAX_EVENT_BYTES,MAX_RAW_BYTES=256,16384,12*1024*1024
uid,spec,open_client,roots=H.uid,H.spec,H.open_client,H.roots
start,finish,stop_owned,receive=H.start,H.finish,H.stop_owned,H.receive
hash_inputs,validate_inventory,validate_report,expect_error=H.hash_inputs,H.validate_inventory,H.validate_report,H.expect_error


def plan():return json.loads(Path('docs/validation/D5-I57-design-review.json').read_text())


def worker(value,job,conn):
    transport=dict(lookup=0,execute=0,proof_sha256=None)
    armed=False;command=None
    def hook(point):
        if not armed or point!=job.get('point'):return
        conn.send(dict(event='READY',case=job['case'],path=value['path'],role='CLIENT',
            run_id=value['store']['run_id'],client_store_id=value['store']['client_id'],remote_store_id=value['store']['remote_id'],
            operation=command['kind'],logical_operation=job['logical_operation'],stage=job['stage'],mode=job['mode'],point=point,
            cid=command['cid'],args_sha256=digest(command['args']),expected=command['expected'],
            request_sha256=digest({k:command[k] for k in ('kind','args','expected')}),transport=dict(transport),
            manifest_id=job.get('mid'),send_id=job.get('sid'),ticket=job.get('ticket'),query_id=job.get('qid')))
        conn.recv();raise AssertionError('CRASH_NOT_KILLED')
    try:
        action=job['action']
        if action=='files':out=H.inspect_files(value)
        else:
            c=open_client(value,hook if action=='crash' else None)
            original_lookup,original_execute=c.remote.lookup,c.remote.execute
            def lookup(*args,**kw):
                transport['lookup']+=1;p=original_lookup(*args,**kw);transport['proof_sha256']=digest(p);return p
            def execute(*args,**kw):
                transport['execute']+=1;return original_execute(*args,**kw)
            c.remote.lookup,c.remote.execute=lookup,execute
            try:
                if action=='passive':
                    out=dict(snapshot=c.snapshot(),summary=c.summary(),reads=[])
                    for read in job.get('reads',[]):out['reads'].append(c.store.read_command(read['cid'],read['request_hash']))
                elif action in ('crash','replay'):
                    if job.get('result_spec'):
                        # No P crosses the spawn boundary. This child reads the emitted attempt and queries REMOTE itself.
                        r=job['result_spec'];s=c.snapshot()['state'];send=s['sends'][r['sid']];m=s['manifests'][r['mid']]
                        require(send['attempts'][-1]==r['ticket'],'RESULT_SETUP_IDENTITY')
                        if action=='crash':require(send['ledger_version']==r['ledger'],'RESULT_SETUP_LEDGER')
                        proof=c.remote.lookup(r['ticket'],m)
                        require(proof is not None,'RESULT_PROOF_MISSING')
                        command=dict(kind='RESULT',cid=r['cid'],expected=r['expected'],args=dict(send_id=r['sid'],ledger_version=r['ledger'],query_id=r['qid'],proof=proof))
                    else:command=job['command']
                    armed=action=='crash';out=c.perform(**command)
                elif action=='reconcile':out=c.reconcile(job['sid'])
                elif action=='clock':out=c.perform('CLOCK',dict(tick=job['tick']))
                else:raise AssertionError('UNKNOWN_ACTION')
            finally:c.remote.lookup,c.remote.execute=original_lookup,original_execute
        conn.send(dict(event='DONE',status='OK',value=out,transport=transport))
    except Exception as ex:
        code=str(ex) if isinstance(ex,(DurableError,AssertionError)) and str(ex).replace('_','').isalnum() else type(ex).__name__
        conn.send(dict(event='DONE',status='ERROR',code=code,transport=transport))
    finally:conn.close()


def validate_gate(e,job,value,expected):
    require(type(e) is dict and e.get('event')=='READY','MISSING_READY')
    for key,v in expected.items():require(e.get(key)==v,'GATE_'+key.upper())
    require(e.get('case')==job['case'] and e.get('path')==value['path'],'GATE_CASE_PATH')


class Prepared(Exception):pass


class Scenario:
    def __init__(self,row):
        self.row=row;self.case=row['id'];self.path=row['path'];self.started=time.monotonic()
        self.events,self.oracles,self.children=[],[],[]
        self.lab=(T if self.path=='T' else R).new_lab();self.value=spec(self.lab,self.path)
        self.record=dict(case=self.case,path=self.path,frontier_row=row.get('frontier_row'),frontier=row['frontier'],
            logical_operation=row['operation'],stage=row['stage'],mode=row['mode'],point=row['point'],
            run_id=self.lab.run_id,client_store_id=self.lab.client_id,remote_store_id=self.lab.remote_id,
            events=self.events,oracles=self.oracles,status='RUNNING')
        self.ids={};RECORDS.append(self.record)
    def __enter__(self):return self
    def __exit__(self,kind,*_):self.close(kind is None)
    def event(self,event,**fields):
        require(time.monotonic()-self.started<CASE_SECONDS,'CASE_TIMEOUT')
        value=dict(event=event,case=self.case,path=self.path,**fields)
        require(len(self.events)<MAX_EVENTS,'EVENT_BUDGET');require(len(canonical(value))<=MAX_EVENT_BYTES,'EVENT_SIZE_BUDGET');self.events.append(value)
    def observe(self,label):
        values=H.inspect_files(self.value);out=dict(label=label)
        for role,v in values.items():
            s=v['state'];d=H.describe(v,roots(self.value)[role])
            d.update(receipt_requests={cid:r['request_sha256'] for cid,r in s['receipts'].items()},
                manifest_ids={mid:m['stage'] for mid,m in s.get('manifests',{}).items()},
                source_ids=list(s.get('sources',{})),selected_source=s.get('selected_source'),profile=s.get('profile'),
                profile_generation=s.get('profile_generation'),selection_generation=s.get('selection_generation'),selection=s.get('selection'),
                mappings_sha256=digest(s.get('mappings',s.get('data',{}).get('mappings'))),bases_sha256=digest(s.get('bases',s.get('data',{}).get('bases'))),
                provenance_sha256=digest(s.get('provenance',s.get('data',{}).get('entity_provenance'))),
                bindings_sha256=digest(s.get('bindings')),pending_entries=s.get('pending',{}))
            out[role]=d
        self.oracles.append(out);self.event('ORACLE',label=label,state_hashes={r:digest(v['state']) for r,v in values.items()});return values
    def set_command(self,kind,args):
        head=independent(self.lab.root/'client')['head'];self.cmd=dict(kind=kind,args=args,cid=uid(),expected={k:head[k] for k in ('seq','commit_sha256')})
        self.read=dict(cid=self.cmd['cid'],request_hash=digest({k:self.cmd[k] for k in ('kind','args','expected')}))
        self.record['command']=dict(cid=self.cmd['cid'],kind=kind,args_sha256=digest(args),expected=self.cmd['expected'],request_sha256=self.read['request_hash'])
    def step(self,label,kind,args):
        if label==self.row['operation']:
            self.set_command(kind,args);raise Prepared()
        return self.lab.client.perform(kind,args)['result']
    def review(self,stage,mid):
        return self.step('REVIEW_'+stage+'_ACCEPT','REVIEW',dict(stage=stage,manifest_id=mid,expected_version=0,decision='ACCEPT',reason_code='SYNTHETIC_REVIEW'))
    def projection(self,bid):
        return self.step('PREPARE_PROJECTION','PREPARE_PROJECTION',dict(binding_id=bid,remote_identity=dict(run_id=self.lab.run_id,store_id=self.lab.remote_id),
            capabilities=self.lab.remote.snapshot()['state']['capabilities'],remote_base=None))
    def setup_t(self):
        c=self.lab.client
        ph=c.perform('REGISTER_PROFILE',dict(descriptor=q.descriptor()))['result']['profile_hash'];c.perform('SELECT_PROFILE',dict(profile_hash=ph));self.ids['profile']=ph
        commit=T.capture(self.lab);cap=next(v['results'][0]['capture'] for h,v in self.lab.capture.inspect() if h==commit)
        pin=dict(run_id=self.lab.capture.run_id,scope_sha256=self.lab.capture.scope_hash,commit_sha256=commit,event_index=0,capture_sha256=digest(cap))
        self.record['capture']=dict(pin=pin,source_bytes_sha256=cap['content_sha256'],grade=cap['provenance_grade'],profile='task-register.v1')
        source=self.step('IMPORT','IMPORT',dict(pin=pin,capture=cap))['source_id'];self.ids['source']=source;self.review('SOURCE',source)
        binding=q.account(T.uid(10),T.uid(11),T.uid(12),T.uid(1));card=q.adapter(T.uid(13));bid=binding['binding_id'];self.ids['account']=bid
        c.perform('BIND_ACCOUNT',dict(binding=binding,adapter=card));rows=[q.constraint(cost=2),q.constraint('TOKENS','TOKEN','short',5)]
        c.perform('POLICY',dict(policy=q.policy(T.uid(14),rows,horizon=5)));generation=1
        for i,r in enumerate(rows):
            obs=q.observation(T.uid(20+i),binding,card,r)
            generation=c.perform('OBSERVE',dict(account_id=bid,observation=obs,generation=generation))['result']['generation']
            generation=c.perform('SELECT_OBSERVATION',dict(account_id=bid,observation_id=obs['observation_id'],generation=generation))['result']['generation']
        em=self.step('PREPARE_EVALUATION','PREPARE_EVALUATION',dict(source_id=source,source_review=1,account_id=bid))['manifest_id'];self.ids['evaluation']=em;self.review('EVALUATION',em)
        ef=self.step('PREPARE_EFFECT','PREPARE_EFFECT',dict(evaluation=em,evaluation_review=1,source_key='FIX-1',target_id=T.uid(30),target_key='FIXTURE-1'))['manifest_id'];self.ids['effect']=ef;self.review('EFFECT',ef)
        c.perform('APPLY',dict(manifest_id=ef,review_version=1));self.tid,self.bid=T.uid(30),T.uid(40)
        self.step('BIND','BIND',dict(binding_id=self.bid,target_id=self.tid))
        pm=self.projection(self.bid)['manifest_id'];self.ids['projection']=pm;self.review('PROJECTION',pm)
    def setup_r(self):
        raw,targets=R.source(tasks=1);self.ids=R.prepare(self.lab,raw,targets,select=False,project=False)
        c=self.lab.client;state=c.snapshot()['state'];self.tid=next(t['target_id'] for t in targets if state['data']['entities'][t['target_id']]['kind']=='TASK');self.bid=R.uid(100)
        receipt=self.ids['apply'];self.record['batch']=dict(command_id=receipt['command_id'],request_sha256=receipt['request_sha256'],source_sha256=hashlib.sha256(raw).hexdigest(),task_id=self.tid)
        self.step('SELECT_TASKS','SELECT_TASKS',dict(batch_command=receipt['command_id'],batch_request=receipt['request_sha256'],task_ids=[self.tid]))
        self.step('BIND','BIND',dict(binding_id=self.bid,target_id=self.tid));pm=self.projection(self.bid)['manifest_id'];self.ids['projection']=pm;self.review('PROJECTION',pm)
    def setup_result(self):
        if self.path=='T':self.ids=T.ready(self.lab);self.mid=self.ids['projection']
        else:
            raw,targets=R.source(tasks=1);self.ids=R.prepare(self.lab,raw,targets);self.mid=self.ids['projections'][0]
            receipt=self.ids['apply'];self.record['batch']=dict(command_id=receipt['command_id'],request_sha256=receipt['request_sha256'],source_sha256=hashlib.sha256(raw).hexdigest(),task_id=self.ids['task_ids'][0])
        c=self.lab.client;out=c.dispatch(self.mid,1,deliver=False);self.sid,self.ticket=out['send_id'],out['ticket'];self.qid=uid()
        m=c.snapshot()['state']['manifests'][self.mid];self.proof=self.lab.remote.execute(self.ticket,m)
        c.perform('QUERY',dict(send_id=self.sid,query_id=self.qid,ledger_version=1))
        self.set_command('RESULT',dict(send_id=self.sid,ledger_version=1,query_id=self.qid,proof=self.proof))
        self.record['attempt']=dict(manifest_id=self.mid,manifest_sha256=digest(m),send_id=self.sid,ticket=self.ticket,query_id=self.qid,
            proof_sha256=digest(self.proof),creation_key=m['creation_key'],remote_id=self.proof['remote_id'],payload_sha256=digest(m['payload']))
        if self.path=='T':
            src=c.snapshot()['state']['sources'][self.ids['source']];self.record['capture']=dict(pin=src['pin'],source_bytes_sha256=src['capture']['content_sha256'],grade=src['capture']['provenance_grade'],profile='task-register.v1')
    def prepare(self):
        if self.row['operation']=='RESULT_QUERY':self.setup_result()
        else:
            try:(self.setup_t if self.path=='T' else self.setup_r)()
            except Prepared:pass
            else:raise AssertionError('TARGET_NOT_REACHED')
        self.record['ids']={k:v for k,v in self.ids.items() if k not in ('raw','targets','apply')}
        self.before=self.observe('precondition');return self.before
    def job(self,action='crash'):
        job=dict(action=action,case=self.case,logical_operation=self.row['operation'],stage=self.row['stage'],mode=self.row['mode'],point=self.row['point'])
        if self.row['operation']=='RESULT_QUERY':
            job.update(mid=self.mid,sid=self.sid,ticket=self.ticket,qid=self.qid,result_spec=dict(sid=self.sid,ticket=self.ticket,mid=self.mid,qid=self.qid,
                ledger=1,cid=self.cmd['cid'],expected=self.cmd['expected']))
            require('command' not in job and 'proof' not in job['result_spec'],'PARENT_PROOF_AUTHORITY')
        else:job['command']=self.cmd
        return job
    def run(self,job):
        pair=start(worker,(self.value,job),dict(case=self.case,path=self.path,action=job['action']));self.children.append(pair)
        try:
            e=receive(pair[1]);require(e.get('event')=='DONE' and e.get('status')=='OK',e.get('code','WORKER_FAILURE'));finish(*pair)
            self.event('DONE',operation=job['action'],transport=e['transport'],output_sha256=digest(e['value']),result=e['value'] if job['action'] not in ('passive','files') else None)
            return e
        finally:stop_owned([pair])
    def crash(self):
        job=self.job();pair=start(worker,(self.value,job),dict(case=self.case,path=self.path,action='crash'));self.children.append(pair)
        expected=dict(role='CLIENT',run_id=self.lab.run_id,client_store_id=self.lab.client_id,remote_store_id=self.lab.remote_id,
            operation=self.cmd['kind'],logical_operation=self.row['operation'],stage=self.row['stage'],mode=self.row['mode'],point=self.row['point'],
            cid=self.cmd['cid'],args_sha256=digest(self.cmd['args']),expected=self.cmd['expected'],request_sha256=self.read['request_hash'],
            manifest_id=getattr(self,'mid',None),send_id=getattr(self,'sid',None),ticket=getattr(self,'ticket',None),query_id=getattr(self,'qid',None))
        try:
            e=receive(pair[1]);validate_gate(e,job,self.value,expected)
            require(e['transport']['execute']==0 and e['transport']['lookup']==int(self.row['operation']=='RESULT_QUERY'),'WRONG_TRANSPORT_AT_GATE')
            if self.row['operation']=='RESULT_QUERY':require(e['transport']['proof_sha256']==digest(self.proof),'WRONG_REAL_PROOF')
            self.event('READY',**{k:v for k,v in e.items() if k not in ('event','case','path')});self.observe('gate')
            pair[0].kill();finish(*pair,expected=-signal.SIGKILL);self.event('SIGKILL',exitcode=pair[0].exitcode,point=self.row['point'])
        finally:stop_owned([pair])
        return self.observe('after_sigkill')
    def passive(self):
        before=self.observe('before_passive');require(self.run(dict(action='files'))['value']==before,'FRESH_FILE_READER_CHANGED')
        e=self.run(dict(action='passive',reads=[self.read] if hasattr(self,'read') else []));require(e['transport']['lookup']==e['transport']['execute']==0,'PASSIVE_TRANSPORT')
        require(e['value']['snapshot']==dict(head=before['client']['head'],state=before['client']['state']),'PUBLIC_REOPEN_CHANGED')
        require(self.observe('after_passive')==before,'PASSIVE_MUTATION');self.event('PASSIVE_UNCHANGED',read_receipt_hashes=[digest(r) for r in e['value']['reads']]);return e['value']
    def close(self,success):
        try:
            stop_owned(self.children);self.lab.close();require(not self.lab.home.exists(),'OWN_ROOT_REMAINS')
            if self.path=='T':require(not self.lab.capture.root.exists(),'OWN_CAPTURE_REMAINS')
            self.record['cleanup_verified']=True
        finally:
            self.record['status']='PASS' if success and self.record.get('cleanup_verified') else 'FAIL';self.record['elapsed_seconds']=round(time.monotonic()-self.started,3)


def bounded_raw(value,maximum=MAX_RAW_BYTES):
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'));require(len(raw.encode())<=maximum,'RAW_BUDGET');return raw


def raw_binding(path,expected_sha256=None,maximum=MAX_RAW_BYTES):return strict_raw_binding(path,expected_sha256,maximum)
