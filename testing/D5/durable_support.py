# SPDX-License-Identifier: GPL-3.0-only
"""Trusted synthetic I33 test setup, spawn workers and independent file oracle."""
import base64
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import signal
import uuid

from source_ingest.durable_task_fixture import (DurableLab,Client,Remote,config,digest,copy)
from source_ingest import eligibility_fixture as q
from source_ingest.incremental_fixture import FixtureStore,file_event,page,request


def uid(n=None):
    return str(uuid.uuid4()) if n is None else f'00000000-0000-4000-8000-{n:012d}'


DATA=(b'| ID | Item | Component(s) | Objective | Blocked on | Status | Verified | Source |\n'
      b'|---|---|---|---|---|---|---|---|\n'
      b'| FIX-1 | Synthetic item | fixture | Review only | - | CLOSED | claim | inert |\n')


def new_lab(**kwargs):
    return DurableLab(config(uid(1),uid(2),uid(3),uid(4),**kwargs))


def capture(lab,data=DATA,**extra):
    snap=lab.capture.snapshot()
    tokens={} if snap['state']['phase']=='INVENTORY' else dict(new_start='fixture:'+uid())
    req=request(uid(),snap,page(lab.scope,snap['state'],[file_event('file-1',data,**extra)],**tokens))
    out=lab.capture.advance(req)
    return out['commit_sha256']


def ready(lab,*,apply=True,projection=True):
    c=lab.client
    ph=c.perform('REGISTER_PROFILE',dict(descriptor=q.descriptor()))['result']['profile_hash']
    c.perform('SELECT_PROFILE',dict(profile_hash=ph))
    source=c.import_event(capture(lab))['result']['source_id'];c.review('SOURCE',source)
    binding=q.account(uid(10),uid(11),uid(12),uid(1));card=q.adapter(uid(13));bid=binding['binding_id']
    c.perform('BIND_ACCOUNT',dict(binding=binding,adapter=card))
    rows=[q.constraint(cost=2),q.constraint('TOKENS','TOKEN','short',5)]
    c.perform('POLICY',dict(policy=q.policy(uid(14),rows,horizon=5)))
    generation=1
    for i,row in enumerate(rows):
        obs=q.observation(uid(20+i),binding,card,row)
        generation=c.perform('OBSERVE',dict(account_id=bid,observation=obs,generation=generation))['result']['generation']
        generation=c.perform('SELECT_OBSERVATION',dict(account_id=bid,observation_id=obs['observation_id'],generation=generation))['result']['generation']
    em=c.perform('PREPARE_EVALUATION',dict(source_id=source,source_review=1,account_id=bid))['result']['manifest_id']
    c.review('EVALUATION',em)
    ef=c.perform('PREPARE_EFFECT',dict(evaluation=em,evaluation_review=1,source_key='FIX-1',target_id=uid(30),target_key='FIXTURE-1'))['result']['manifest_id']
    c.review('EFFECT',ef)
    out=dict(source=source,evaluation=em,effect=ef,account=bid,profile=ph)
    if apply:
        out['apply']=c.perform('APPLY',dict(manifest_id=ef,review_version=1))
    if apply and projection:
        c.perform('BIND',dict(binding_id=uid(40),target_id=uid(30)))
        pm=c.prepare_projection(uid(40))['result']['manifest_id'];c.review('PROJECTION',pm);out['projection']=pm
    return out


def independent(path):
    """Independent JSON/hash/chain/count reader; never calls Store or its reducer."""
    path=Path(path)
    raw=(path/'head.json').read_bytes();head=json.loads(raw)
    marker=json.loads((path/'marker.json').read_bytes())
    for key in ('run_id','store_id','role'):
        assert head[key]==marker[key]
    current=head['commit_sha256'];chain=[];seen=set()
    while current is not None:
        assert current not in seen;seen.add(current)
        raw=(path/'objects'/(current+'.json')).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==current
        value=json.loads(raw)
        assert value['run_id']==marker['run_id'] and value['store_id']==marker['store_id']
        chain.append(value);current=value['parent_sha256']
    chain.reverse()
    assert len(chain)==head['seq']+1
    for i,value in enumerate(chain):
        assert value['seq']==i
        if i:
            cid=value['command_id'];r=value['state']['receipts'][cid]
            assert r==value['receipt'] and r['request_sha256']==value['request_sha256']
            assert not r['grants_execution_authority'] and r['reservations_created']==0
    if CURRENT_CASE is not None:
        key=(CURRENT_CASE,marker['role'],marker['store_id'],head['commit_sha256'])
        if key not in ORACLE_KEYS:
            ORACLE_KEYS.add(key)
            ORACLES.append(dict(case=CURRENT_CASE,role=marker['role'],store_id=marker['store_id'],
                seq=head['seq'],commit_sha256=head['commit_sha256'],state_sha256=hashlib.sha256(
                    json.dumps(chain[-1]['state'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),
                receipts=len(chain[-1]['state']['receipts']),tasks=len(chain[-1]['state'].get('tasks',chain[-1]['state'].get('entities',{})))))
    return dict(head=head,state=chain[-1]['state'],chain=chain)


def reopen_spec(lab):
    return dict(client_path=str(lab.root/'client'),remote_path=str(lab.root/'remote'),run_id=lab.run_id,
                client_id=lab.client_id,remote_id=lab.remote_id,capture_path=str(lab.capture.root),
                capture_run=lab.capture.run_id,scope=lab.scope)


def open_client(spec,hook=None,remote_hook=None):
    cap=FixtureStore(spec['capture_path'],spec['capture_run'],spec['scope'])
    r=Remote(spec['remote_path'],spec['run_id'],spec['remote_id'],hook=remote_hook)
    return Client(spec['client_path'],spec['run_id'],spec['client_id'],cap,r,hook=hook)


def worker(spec,action,args,connection,point=None,role='CLIENT',barrier=None):
    def hook(stage):
        if stage==point:
            connection.send(('READY',stage))
            if barrier:
                barrier.wait(timeout=15)
            else:
                while True:signal.pause()
    try:
        c=open_client(spec,hook if role=='CLIENT' else None,hook if role=='REMOTE' else None)
        if barrier and point is None:barrier.wait(timeout=15)
        if action=='initialize':
            from source_ingest.durable_store import Store
            from source_ingest.durable_task_fixture import client_reduce,client_genesis
            store=Store(Path(spec['client_path']).parent/'initializing',spec['run_id'],args['store_id'],'CLIENT',client_reduce,client_genesis,hook=hook)
            out=store.create(args['config'])
        elif action=='snapshot':out=c.summary()
        elif action=='mutate':out=c.perform(**args)
        elif action=='raw_mutate':out=c.store.transact(**args)
        elif action=='dispatch':out=c.dispatch(**args)
        elif action=='reconcile':out=c.reconcile(**args)
        elif action=='remote':out=c.remote.execute(**args)
        else:raise ValueError('TEST_ACTION')
        connection.send(('OK',out))
    except Exception as ex:
        connection.send(('ERROR',str(ex)))
    finally:connection.close()


CURRENT_CASE=None
ORACLES=[]
ORACLE_KEYS=set()


CONTEXT=multiprocessing.get_context('spawn')
CHILDREN=[]
CRASHES=[]


def start(lab,action,args,*,point=None,role='CLIENT',barrier=None):
    parent,child=CONTEXT.Pipe()
    p=CONTEXT.Process(target=worker,args=(reopen_spec(lab),action,args,child,point,role,barrier))
    p.start();child.close();CHILDREN.append(p)
    return p,parent


def receive(p,conn,timeout=20):
    if not conn.poll(timeout):
        p.kill();p.join(5);raise AssertionError('CHILD_TIMEOUT')
    message=conn.recv();return message


def finish(p,conn):
    p.join(10)
    if p.is_alive():p.kill();p.join(5);raise AssertionError('CHILD_ALIVE')
    conn.close()
    return p.exitcode


def kill_at(lab,action,args,point,role='CLIENT'):
    before=independent(lab.root/('client' if role=='CLIENT' else 'remote'))['head']
    p,conn=start(lab,action,args,point=point,role=role)
    try:
        assert receive(p,conn)==('READY',point)
    finally:
        if p.is_alive():p.kill()
        code=finish(p,conn)
    assert code==-signal.SIGKILL
    after=independent(lab.root/('client' if role=='CLIENT' else 'remote'))['head']
    CRASHES.append(dict(case=CURRENT_CASE,role=role,action=action,operation=args.get('kind',action),stage=args.get('args',{}).get('stage'),
                       point=point,exitcode=code,before_seq=before['seq'],after_seq=after['seq'],
                       before_head_sha256=before['commit_sha256'],after_head_sha256=after['commit_sha256']))
    return code
