# SPDX-License-Identifier: GPL-3.0-only
"""I64 owned process interleavings; public T/R APIs and unchanged hooks."""
import copy
import hashlib
import json
from pathlib import Path
import time

from source_ingest.durable_store import DurableError
from source_ingest import eligibility_fixture as q
from testing.D5 import durable_support as T,relational_support as R
from testing.durable_concurrency.support import canonical,digest,require,probe_locked
from testing.durable_inflight_revocation import support as V
from testing.causal_frontier_cells import support as C
from testing.durable_crash_boundaries import support as H

CHILDREN=V.CHILDREN
RECORDS=[]
EXTRA_ROOTS=[]
WAIT_SECONDS,CASE_SECONDS,CAMPAIGN_SECONDS=20,120,900
MAX_EVENTS,MAX_EVENT_BYTES,MAX_RAW_BYTES=256,16384,12*1024*1024
uid,spec,roots=H.uid,H.spec,H.roots
start,finish,stop_owned,receive=V.start,V.finish,V.stop_owned,V.receive
hash_inputs,validate_inventory,validate_report,expect_error=H.hash_inputs,H.validate_inventory,H.validate_report,H.expect_error
bounded_raw,raw_binding=C.bounded_raw,C.raw_binding


def plan():return json.loads(Path('docs/validation/D5-I63-design-review.json').read_text())


def signature(state):
    return dict(profile=state.get('profile'),profile_generation=state.get('profile_generation'),policy_generation=state.get('policy_generation'),
        policy_sha256=digest(state.get('policy')),selected_source=state.get('selected_source'),source_generation=state.get('source_generation'),
        selection_generation=state.get('selection_generation'),data_generation=state.get('data_generation'),
        accounts={k:dict(generation=v['generation'],selected=v['selected'],revoked=v['revoked'],adapter_sha256=digest(v['adapter'])) for k,v in state.get('accounts',{}).items()},
        data_sha256=digest(state.get('data')),reviews=state.get('reviews',{}))


def validate_gate(event,expected):
    require(event.get('event')=='READY','MISSING_READY')
    for k,v in expected.items():require(event.get(k)==v,'GATE_'+k.upper())
    require(event.get('inside_real_call') is True,'NOT_IN_REAL_CALL')


def release(conn,identity):conn.send(dict(event='RELEASE',cid=identity['cid'],ticket=identity.get('ticket')))


def check_release(value,identity):require(value==dict(event='RELEASE',cid=identity['cid'],ticket=identity.get('ticket')),'CONTROL_RELEASE')


def worker(value,job,conn):
    observed=dict(execute=0,lookup=0,proof_sha256=None,failure_phase=None)
    active=False;armed=True;identity=None;attempts=[]
    def hook(point):
        nonlocal armed
        if active and armed and point==job.get('point'):
            armed=False;conn.send(dict(event='READY',inside_real_call=True,**identity,transport=dict(observed)))
            check_release(receive(conn),identity)
    try:
        action=job['action']
        if action=='files':out=H.inspect_files(value)
        else:
            c=(T if value['path']=='T' else R).open_client(value['store'],hook if job.get('gate') and job['role']=='CLIENT' else None,hook if job.get('gate') and job['role']=='REMOTE' else None)
            execute,lookup=c.remote.execute,c.remote.lookup
            def seen_execute(ticket,m,**kw):
                nonlocal active,identity
                observed['execute']+=1;cmd=C.remote_command(value,ticket,m,kw.get('close',False))
                if job.get('gate'):
                    identity=dict(case=job['case'],path=value['path'],actor=job['actor'],role='REMOTE',operation=cmd['kind'],mode=m['operation'],stage='PROJECTION',point=job['point'],
                        run_id=value['store']['run_id'],client_store_id=value['store']['client_id'],remote_store_id=value['store']['remote_id'],
                        cid=cmd['cid'],request_sha256=digest({k:cmd[k] for k in ('kind','args','expected')}),args_sha256=digest(cmd['args']),expected=None,
                        manifest_id=job['mid'],manifest_sha256=digest(m),send_id=job['sid'],ticket=ticket)
                active=True
                try:p=execute(ticket,m,**kw)
                finally:active=False
                observed['proof_sha256']=digest(p)
                if job.get('lose_response'):observed['failure_phase']='LOSS_AFTER_REAL_COMMIT';raise OSError('SYNTHETIC_LOSS')
                return p
            def seen_lookup(*a,**kw):
                observed['lookup']+=1;p=lookup(*a,**kw);observed['proof_sha256']=digest(p);return p
            c.remote.execute,c.remote.lookup=seen_execute,seen_lookup
            try:
                if action=='passive':
                    out=dict(snapshot=c.snapshot(),remote=c.remote.snapshot(),summary=c.summary(),reads=[])
                    for r in job.get('reads',[]):out['reads'].append(c.store.read_command(r['cid'],r['request_sha256']))
                elif action=='summary':out=c.summary()
                elif action=='dispatch':out=c.dispatch(job['mid'],1,send_id=job['sid'],retry=job.get('retry',False))
                elif action=='reconcile':out=c.reconcile(job['sid'])
                elif action=='perform':
                    cmd=job['command'];identity=dict(case=job['case'],path=value['path'],actor=job['actor'],role='CLIENT',operation=cmd['kind'],mode='LOCAL',stage=job.get('stage'),point=job.get('point'),
                        run_id=value['store']['run_id'],client_store_id=value['store']['client_id'],remote_store_id=value['store']['remote_id'],
                        cid=cmd['cid'],request_sha256=digest({k:cmd[k] for k in ('kind','args','expected')}),args_sha256=digest(cmd['args']),expected=cmd['expected'],
                        manifest_id=cmd['args'].get('manifest_id'),manifest_sha256=cmd['args'].get('manifest_id'),send_id=cmd['args'].get('send_id'),ticket=cmd['args'].get('ticket'))
                    attempts.append(dict(cid=cmd['cid'],kind=cmd['kind'],args_sha256=digest(cmd['args']),expected=cmd['expected'],request_sha256=identity['request_sha256']))
                    active=job.get('gate',False);out=c.perform(**cmd);active=False
                elif action=='mutate':
                    first=job['steps'][0]
                    if job.get('contender'):
                        conn.send(dict(event='PREPARED',case=job['case'],actor=job['actor'],cid=first['cid'],expected=job['expected']))
                        conn.send(dict(event=probe_locked(roots(value)['client']),case=job['case'],actor=job['actor'],cid=first['cid']))
                        check_release(receive(conn),dict(cid=first['cid']))
                    out=[]
                    for i,step in enumerate(job['steps']):
                        before=c.snapshot();args=copy.deepcopy(step['args'])
                        if step.get('account'):args['generation']=before['state']['accounts'][step['account']]['generation']
                        expected=job.get('expected') if i==0 else None
                        if expected is None:expected={k:before['head'][k] for k in ('seq','commit_sha256')}
                        cmd=dict(kind=step['kind'],args=args,cid=step['cid'],expected=expected)
                        attempted=dict(cid=cmd['cid'],kind=cmd['kind'],args_sha256=digest(args),request_sha256=digest({k:cmd[k] for k in ('kind','args','expected')}),expected=expected)
                        attempts.append(attempted);receipt=c.perform(**cmd);after=c.snapshot()
                        out.append(dict(command=attempted,receipt=receipt,before=signature(before['state']),after=signature(after['state']),head=after['head']))
                elif action=='project_old':
                    if value['path']=='T':
                        c.perform('BIND',dict(binding_id=job['bid'],target_id=job['tid']))
                        out=c.prepare_projection(job['bid'])
                    else:
                        out=c.perform('SELECT_TASKS',dict(batch_command=job['batch_cid'],batch_request=job['batch_request'],task_ids=[job['tid']]))
                else:raise AssertionError('UNKNOWN_ACTION')
            finally:c.remote.execute,c.remote.lookup=execute,lookup
        conn.send(dict(event='DONE',status='OK',value=out,transport=observed,attempts=attempts,identity=identity))
    except Exception as ex:
        code=str(ex) if isinstance(ex,(DurableError,AssertionError)) and str(ex).replace('_','').isalnum() else type(ex).__name__
        conn.send(dict(event='DONE',status='ERROR',code=code,transport=observed,attempts=attempts,identity=identity))
    finally:conn.close()


class Scenario(C.Scenario):
    def __init__(self,row):
        self.row=row;self.case=row['id'];self.path=row['path'];self.started=time.monotonic();self.events,self.oracles,self.children=[],[],[];self.ids={}
        self.lab=(T if self.path=='T' else R).new_lab();self.value=spec(self.lab,self.path)
        self.record=dict(case=self.case,path=self.path,family=row['family'],mutation_id=row.get('mutation_id'),mode=row.get('mode','CONTROL'),point=row.get('point','CONTROL'),
            order=row.get('order','CONTROL'),UI_part=row['UI_part'],run_id=self.lab.run_id,client_store_id=self.lab.client_id,remote_store_id=self.lab.remote_id,events=self.events,oracles=self.oracles,status='RUNNING')
        RECORDS.append(self.record)
    def event(self,event,**fields):
        require(time.monotonic()-self.started<CASE_SECONDS,'CASE_TIMEOUT');v=dict(event=event,case=self.case,path=self.path,**fields)
        require(len(self.events)<MAX_EVENTS,'EVENT_BUDGET');require(len(canonical(v))<=MAX_EVENT_BYTES,'EVENT_SIZE_BUDGET');self.events.append(v)
    def observe(self,label):
        values=super().observe(label);self.oracles[-1]['client']['signature']=signature(values['client']['state']);return values
    def t_prepare(self,apply=True,project=True,data=T.DATA):
        c=self.lab.client
        if not self.ids:
            ph=c.perform('REGISTER_PROFILE',dict(descriptor=q.descriptor()))['result']['profile_hash'];c.perform('SELECT_PROFILE',dict(profile_hash=ph));self.ids['profile']=ph
            binding=q.account(T.uid(10),T.uid(11),T.uid(12),T.uid(1));card=q.adapter(T.uid(13));self.ids['account']=binding['binding_id']
            c.perform('BIND_ACCOUNT',dict(binding=binding,adapter=card));rows=[q.constraint(cost=2),q.constraint('TOKENS','TOKEN','short',5)]
            c.perform('POLICY',dict(policy=q.policy(T.uid(14),rows,horizon=5)));gen=1
            for i,r in enumerate(rows):
                obs=q.observation(T.uid(20+i),binding,card,r);gen=c.perform('OBSERVE',dict(account_id=binding['binding_id'],observation=obs,generation=gen))['result']['generation']
                gen=c.perform('SELECT_OBSERVATION',dict(account_id=binding['binding_id'],observation_id=obs['observation_id'],generation=gen))['result']['generation']
            if self.row.get('mutation_id')=='C03':
                obs=q.observation(T.uid(22),binding,card,rows[0],remaining=11);c.perform('OBSERVE',dict(account_id=binding['binding_id'],observation=obs,generation=gen));self.ids['observation_b']=obs['observation_id']
        commit=T.capture(self.lab,data=data);sid=c.import_event(commit)['result']['source_id'];c.review('SOURCE',sid)
        em=c.perform('PREPARE_EVALUATION',dict(source_id=sid,source_review=1,account_id=self.ids['account']))['result']['manifest_id'];c.review('EVALUATION',em)
        ef=c.perform('PREPARE_EFFECT',dict(evaluation=em,evaluation_review=1,source_key='FIX-1',target_id=T.uid(30),target_key='FIXTURE-1'))['result']['manifest_id'];c.review('EFFECT',ef)
        self.ids.update(source=sid,evaluation=em,effect=ef);self.tid,self.bid=T.uid(30),T.uid(40)
        if apply:self.ids['apply']=c.perform('APPLY',dict(manifest_id=ef,review_version=1))
        if project:
            if self.bid not in c.snapshot()['state']['bindings']:c.perform('BIND',dict(binding_id=self.bid,target_id=self.tid))
            self.mid=c.prepare_projection(self.bid)['result']['manifest_id'];c.review('PROJECTION',self.mid)
    def r_source(self,title=None,revision='gx-baseline'):
        raw,targets=R.source(tasks=3,revision=revision);data=json.loads(raw)
        data['elements'] += [R.element('REQ2','REQUIREMENT','Aux requirement','Synthetic'),R.element('EP2','EPIC','Aux epic','Synthetic')]
        targets += [dict(source_key='REQ2',target_id=R.uid(50),target_key='AUX-REQ'),dict(source_key='EP2',target_id=R.uid(51),target_key='AUX-EP')]
        if title:data['elements'][2]['title']=title
        return canonical(data),targets
    def r_prepare(self,apply=True,project=True,title=None):
        raw,targets=self.r_source(title,revision='gx-update' if title else 'gx-baseline');self.ids.update(R.prepare(self.lab,raw,targets,apply=apply,select=False,project=False))
        self.raw=raw;self.targets=targets;self.tid,self.bid=R.uid(12),R.uid(100);c=self.lab.client
        if project:
            receipt=self.ids['apply'];c.perform('SELECT_TASKS',dict(batch_command=receipt['command_id'],batch_request=receipt['request_sha256'],task_ids=[self.tid]))
            if self.bid not in c.snapshot()['state']['bindings']:c.perform('BIND',dict(binding_id=self.bid,target_id=self.tid))
            self.mid=c.prepare_projection(self.bid)['result']['manifest_id'];c.review('PROJECTION',self.mid)
    def prepare(self):
        local=self.row['family']=='LOCAL_APPLY';self.mid=None
        (self.t_prepare if self.path=='T' else self.r_prepare)(apply=not local,project=not local)
        c=self.lab.client
        if self.row['mode']=='UPDATE':
            old=c.dispatch(self.mid,1);before=self.lab.remote.snapshot();rid=next(iter(before['state']['entities']));edit=self.lab.remote.edit(rid,foreign=dict(sentinel='GX_KEEP'))
            self.record['update_setup']=dict(create=old,create_entity=before['state']['entities'][rid],foreign_edit_receipt=edit)
            if self.path=='T':self.t_prepare(data=T.DATA.replace(b'Synthetic item',b'GX UPDATE payload'))
            else:self.r_prepare(title='GX UPDATE payload')
        self.sid=uid();self.steps=[];mid=self.row['mutation_id'];state=c.snapshot()['state']
        def step(kind,args,account=None):self.steps.append(dict(kind=kind,args=args,cid=uid(),account=account))
        if mid=='S01':
            commit=T.capture(self.lab,data=T.DATA.replace(b'Synthetic item',b'GX observed source B'));cap=next(v['results'][0]['capture'] for h,v in self.lab.capture.inspect() if h==commit)
            pin=dict(run_id=self.lab.capture.run_id,scope_sha256=self.lab.capture.scope_hash,commit_sha256=commit,event_index=0,capture_sha256=digest(cap));step('IMPORT',dict(pin=pin,capture=cap));self.record['mutation_capture_pin']=pin
        elif mid in ('S02','S03','S04','S06','S07'):
            stage={'S02':'SOURCE','S03':'EVALUATION','S04':'EFFECT','S06':'SOURCE','S07':'BATCH'}[mid]
            target=self.ids['source_manifest' if self.path=='R' and stage=='SOURCE' else stage.lower()]
            step('REVIEW',dict(stage=stage,manifest_id=target,expected_version=1,decision='REVOKE',reason_code='GX_MUTATION'))
            if mid=='S02':step('REVIEW',dict(stage=stage,manifest_id=target,expected_version=2,decision='ACCEPT',reason_code='GX_ABA'))
        elif mid=='S05':
            raw,_=self.r_source(revision='gx-source-b');b=c.capture(raw)['result']['source_id'];step('SELECT_SOURCE',dict(source_id=b));step('SELECT_SOURCE',dict(source_id=state['selected_source']))
        elif mid=='C01':step('SELECT_PROFILE',dict(profile_hash=None));step('SELECT_PROFILE',dict(profile_hash=state['profile']))
        elif mid=='C02':
            a=state['policy'];b=copy.deepcopy(a);b['required_horizon']=4;step('POLICY',dict(policy=b));step('POLICY',dict(policy=a))
        elif mid in ('C03','C04','C05'):
            aid=self.ids['account'];account=state['accounts'][aid]
            if mid=='C03':
                step('SELECT_OBSERVATION',dict(account_id=aid,observation_id=self.ids['observation_b']),aid);step('SELECT_OBSERVATION',dict(account_id=aid,observation_id=T.uid(20)),aid)
            elif mid=='C04':step('REVOKE_OBSERVATION',dict(account_id=aid,observation_id=T.uid(20)),aid)
            else:
                a=account['adapter'];b=copy.deepcopy(a);b['release']='gx-adapter-b';step('ADAPTER',dict(account_id=aid,adapter=b),aid);step('ADAPTER',dict(account_id=aid,adapter=a),aid)
        elif mid.startswith('R'):
            if mid in ('R01','R02','R03','R04'):
                target={'R01':self.tid,'R02':R.uid(11),'R03':R.uid(10),'R04':self.tid}[mid]
                changes={'R01':dict(title='GX changed TASK'),'R02':dict(title='GX changed EPIC'),'R03':dict(has_work=True),'R04':dict(epic_id=R.uid(51))}[mid]
                step('EDIT_ENTITY',dict(entity_id=target,changes=changes))
            else:
                typ='EPIC_REQUIREMENT' if mid=='R05' else 'TASK_EPIC' if mid=='R06' else 'TASK_DEPENDENCY'
                left=R.uid(11) if mid=='R05' else self.tid;right=R.uid(50) if mid=='R05' else R.uid(51) if mid=='R06' else R.uid(14)
                kind={'R07':'HARD','R08':'SOFT','R09':'MOCKABLE','R10':'OPTIONAL'}.get(mid);rel=dict(type=typ,left=left,right=right,kind=kind)
                require(digest(rel) not in state['data']['relations'],'RELATION_ALREADY_PRESENT');step('ADD_RELATION',dict(relation=rel))
        self.before=self.observe('baseline');self.record['baseline_signature']=signature(self.before['client']['state']);self.record['mutation_steps']=[dict(kind=v['kind'],args_sha256=digest(v['args']),cid=v['cid']) for v in self.steps]
        if self.path=='T':
            src=self.before['client']['state']['sources'][self.ids['source']];self.record['authority']=dict(source_id=self.ids['source'],pin=src['pin'],source_bytes_sha256=src['capture']['content_sha256'],evaluation=self.ids['evaluation'],effect=self.ids['effect'])
        else:
            self.record['authority']=dict(source_manifest=self.ids['source_manifest'],batch_manifest=self.ids['batch'],batch_receipt=self.ids.get('apply'),task_id=self.tid)
        if not local:self.manifest=self.before['client']['state']['manifests'][self.mid];self.record['manifest']=dict(id=self.mid,sha256=digest(self.manifest),mode=self.manifest['operation'],target_id=self.tid,binding_id=self.bid)
        return self.before
    def command(self,kind,args):
        h=self.observe('command_head')['client']['head'];return dict(kind=kind,args=args,cid=uid(),expected={k:h[k] for k in ('seq','commit_sha256')})
    def spawn(self,job):
        job=dict(job,case=self.case);pair=start(worker,(self.value,job),dict(case=self.case,path=self.path,action=job['action'],actor=job.get('actor','reader')));self.children.append(pair);return pair
    def done(self,pair,job,error=None):
        try:
            e=receive(pair[1]);require(e.get('event')=='DONE' and e.get('status')==('ERROR' if error else 'OK'),'WORKER_FAILURE')
            if error:require(e['code']==error,'WRONG_PRODUCT_ERROR')
            finish(*pair);self.event('DONE',actor=job.get('actor','reader'),operation=job['action'],code=e.get('code'),transport=e['transport'],attempts=e['attempts'],result=e.get('value') if job['action'] not in ('passive','files') else None,output_sha256=digest(e.get('value')));return e
        finally:stop_owned([pair])
    def run(self,job,error=None):return self.done(self.spawn(job),job,error)
    def mutate_job(self,expected,contender=False):return dict(action='mutate',actor='mutator',steps=copy.deepcopy(self.steps),expected=expected,contender=contender)
    def passive(self):
        before=self.observe('before_passive');require(self.run(dict(action='files'))['value']==before,'FILE_REOPEN_CHANGED')
        e=self.run(dict(action='passive'));require(e['transport']['execute']==e['transport']['lookup']==0,'PASSIVE_TRANSPORT')
        for role,key in [('client','snapshot'),('remote','remote')]:require(e['value'][key]==dict(head=before[role]['head'],state=before[role]['state']),'PUBLIC_REOPEN_CHANGED')
        require(self.observe('after_passive')==before,'PASSIVE_MUTATION');self.event('PASSIVE_UNCHANGED');return e['value']
