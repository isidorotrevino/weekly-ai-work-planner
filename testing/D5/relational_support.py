# SPDX-License-Identifier: GPL-3.0-only
"""New R-only fixture setup and independent spawn/file oracles; no legacy state restoration."""
import hashlib
import json
import multiprocessing
from pathlib import Path
import signal
import uuid

from source_ingest.durable_relational_fixture import RelationalLab,Client,Remote,config
from source_ingest.batch_fixture import element,declaration,reference,envelope


def uid(n=None):return str(uuid.uuid4()) if n is None else f'10000000-0000-4000-8000-{n:012d}'


def new_lab(**kwargs):return RelationalLab(config(uid(1),uid(2),uid(3),uid(4),**kwargs))


def source(*,revision='fixture-1',tasks=2,description=None,relations=True):
    items=[element('REQ','REQUIREMENT','Explicit requirement','Requirement evidence'),element('EP','EPIC','Explicit epic','Unprojected epic text')]
    items += [element(f'T{i}','TASK',f'Synthetic task {i}',description) for i in range(tasks)]
    ref=lambda key,kind:reference(uid(1),uid(2),key,kind)
    links=[]
    if relations:
        links=[declaration('ER','EPIC_REQUIREMENT',ref('EP','EPIC'),ref('REQ','REQUIREMENT'))]
        links += [declaration(f'TE{i}','TASK_EPIC',ref(f'T{i}','TASK'),ref('EP','EPIC')) for i in range(tasks)]
        if tasks>1:links.append(declaration('DEP','TASK_DEPENDENCY',ref('T0','TASK'),ref('T1','TASK'),kind='HARD'))
    raw=envelope(uid(1),uid(2),revision,items,links)
    targets=[dict(source_key=row['source_key'],target_id=uid(10+i),target_key=f'KEY-{i}') for i,row in enumerate(items)]
    return raw,targets


def prepare(lab,raw=None,targets=None,*,apply=True,select=True,project=True):
    if raw is None:raw,targets=source()
    c=lab.client
    sid=c.capture(raw)['result']['source_id'];c.select_source(sid)
    sm=c.perform('PREPARE_SOURCE',{})['result']['manifest_id'];c.review('SOURCE',sm)
    bm=c.perform('PREPARE_BATCH',dict(source_manifest=sm,source_review=1,targets=targets))['result']['manifest_id'];c.review('BATCH',bm)
    ids=dict(source=sid,source_manifest=sm,batch=bm,targets=targets,raw=raw)
    if apply:
        receipt=c.perform('APPLY_BATCH',dict(manifest_id=bm,review_version=1));ids['apply']=receipt
        state=c.snapshot()['state'];task_ids=[t['target_id'] for t in targets if state['data']['entities'][t['target_id']]['kind']=='TASK']
        if select:
            c.perform('SELECT_TASKS',dict(batch_command=receipt['command_id'],batch_request=receipt['request_sha256'],task_ids=task_ids));ids['task_ids']=task_ids
            if project:
                mids=[];bindings=[]
                for i,tid in enumerate(task_ids):
                    bid=uid(100+i);c.perform('BIND',dict(binding_id=bid,target_id=tid))
                    mid=c.prepare_projection(bid)['result']['manifest_id'];c.review('PROJECTION',mid)
                    mids.append(mid);bindings.append(bid)
                ids['projections']=mids;ids['bindings']=bindings
    return ids


CURRENT_CASE=None
ORACLES=[]
ORACLE_KEYS=set()
CHILDREN=[]
CRASHES=[]
CONTEXT=multiprocessing.get_context('spawn')


def independent(path):
    path=Path(path);head=json.loads((path/'head.json').read_bytes());owner=json.loads((path/'marker.json').read_bytes())
    assert all(head[k]==owner[k] for k in ('run_id','store_id','role'))
    h=head['commit_sha256'];chain=[];seen=set()
    while h is not None:
        assert h not in seen;seen.add(h)
        raw=(path/'objects'/(h+'.json')).read_bytes();assert hashlib.sha256(raw).hexdigest()==h
        value=json.loads(raw);assert all(value[k]==owner[k] for k in ('run_id','store_id','role'))
        chain.append(value);h=value['parent_sha256']
    chain.reverse();assert len(chain)==head['seq']+1
    for n,value in enumerate(chain):
        assert value['seq']==n
        if n:
            assert value['receipt']==value['state']['receipts'][value['command_id']]
            assert not value['receipt']['grants_execution_authority'] and value['receipt']['quota_consumed']==0
    s=chain[-1]['state'];key=(CURRENT_CASE,owner['store_id'],head['commit_sha256'])
    if CURRENT_CASE and key not in ORACLE_KEYS:
        ORACLE_KEYS.add(key)
        ORACLES.append(dict(case=CURRENT_CASE,role=owner['role'],store_id=owner['store_id'],seq=head['seq'],head_sha256=head['commit_sha256'],
             state_sha256=hashlib.sha256(json.dumps(s,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),
             entities=len(s.get('data',{}).get('entities',s.get('entities',{}))),relations=len(s.get('data',{}).get('relations',{})),receipts=len(s['receipts'])))
    return dict(head=head,state=s,chain=chain)


def spec(lab):return dict(client=str(lab.root/'client'),remote=str(lab.root/'remote'),run_id=lab.run_id,client_id=lab.client_id,remote_id=lab.remote_id)


def open_client(v,hook=None,remote_hook=None):
    r=Remote(v['remote'],v['run_id'],v['remote_id'],hook=remote_hook)
    return Client(v['client'],v['run_id'],v['client_id'],r,hook=hook)


def worker(v,action,args,conn,point=None,role='CLIENT',barrier=None):
    def hook(stage):
        if stage==point:
            conn.send(('READY',stage))
            if barrier:barrier.wait(timeout=15)
            else:
                while True:signal.pause()
    try:
        c=open_client(v,hook if role=='CLIENT' else None,hook if role=='REMOTE' else None)
        if barrier and point is None:barrier.wait(timeout=15)
        if action=='mutate':out=c.perform(**args)
        elif action=='raw_mutate':out=c.store.transact(**args)
        elif action=='snapshot':out=c.summary()
        elif action=='dispatch':out=c.dispatch(**args)
        elif action=='reconcile':out=c.reconcile(**args)
        elif action=='remote':out=c.remote.execute(**args)
        else:raise ValueError('TEST_ACTION')
        conn.send(('OK',out))
    except Exception as ex:conn.send(('ERROR',str(ex)))
    finally:conn.close()


def start(lab,action,args,*,point=None,role='CLIENT',barrier=None):
    parent,child=CONTEXT.Pipe();p=CONTEXT.Process(target=worker,args=(spec(lab),action,args,child,point,role,barrier));p.start();child.close();CHILDREN.append(p)
    return p,parent


def receive(p,c):
    if not c.poll(25):p.kill();p.join(5);raise AssertionError('CHILD_TIMEOUT')
    return c.recv()


def finish(p,c):
    p.join(10)
    if p.is_alive():p.kill();p.join(5);raise AssertionError('CHILD_ALIVE')
    c.close();return p.exitcode


def kill_at(lab,action,args,point,role='CLIENT'):
    path=lab.root/('client' if role=='CLIENT' else 'remote');before=independent(path)['head']
    p,c=start(lab,action,args,point=point,role=role)
    try:assert receive(p,c)==('READY',point)
    finally:
        if p.is_alive():p.kill()
        code=finish(p,c)
    assert code==-signal.SIGKILL
    after=independent(path)['head']
    CRASHES.append(dict(case=CURRENT_CASE,role=role,action=action,operation=args.get('kind',action),point=point,exitcode=code,
       before_seq=before['seq'],after_seq=after['seq'],before_head=before['commit_sha256'],after_head=after['commit_sha256']))
