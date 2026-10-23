# SPDX-License-Identifier: GPL-3.0-only
"""I33-F independent state, crash and cross-process race oracles."""
import base64
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import signal
import unittest
from unittest.mock import patch

from source_ingest.durable_store import DurableError,canonical,decode,digest,LIMITS
from source_ingest.durable_task_fixture import (Remote,Client,CAPS,BOUNDS,client_reduce,client_genesis,
                                               remote_reduce,proof_ok)
from source_ingest import eligibility_fixture as q
from source_ingest.offline import MemoryLab
from source_ingest.plane_fixture import PlaneFixture,ReconciliationLab,binding,task,capabilities
from testing.D5.durable_support import (new_lab,ready,capture,uid,DATA,independent,kill_at,
                                       start,receive,finish,CONTEXT,open_client,reopen_spec,CHILDREN)


class DurableIntegrationTest(unittest.TestCase):
    def setUp(self):
        from testing.D5 import durable_support
        durable_support.CURRENT_CASE=self._testMethodName.removeprefix('test_')
        self._owned_labs=[]

    def lab(self,**kwargs):
        for old in self._owned_labs:old.close()
        lab=new_lab(**kwargs);self._owned_labs.append(lab);self.addCleanup(lab.close);return lab

    def error(self,code,fn,*args,**kwargs):
        with self.assertRaisesRegex(DurableError,code):fn(*args,**kwargs)

    def state(self,lab):return independent(lab.root/'client')['state']
    def entities(self,lab):return independent(lab.root/'remote')['state']['entities']

    def fresh_process(self,lab):
        p,c=start(lab,'snapshot',{})
        try:r=receive(p,c)
        finally:code=finish(p,c)
        self.assertEqual(code,0);self.assertEqual(r[0],'OK');return r[1]

    def df01(self):
        paths=[Path('source_ingest/durable_store.py'),Path('source_ingest/durable_task_fixture.py'),
               Path('source_ingest/preview.py'),Path('testing/D5/test_durable_integration.py')]
        inventory={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        self.assertEqual(len(inventory),4)
        changed=dict(inventory);changed[str(paths[0])]='0'*64
        self.assertNotEqual(inventory,changed)
        from testing.D5.run_durable_lab import applicability
        self.assertEqual(applicability(inventory),'CURRENT')
        self.assertEqual(applicability(changed),'STALE_INPUTS')

    def df02(self):
        for name in ('D3','D4'):
            report=json.loads(Path(f'docs/validation/{name}-CLOSURE.json').read_bytes())
            for path,h in report['verified_executable_input_sha256'].items():
                self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(),h)
        a=json.loads(Path('docs/validation/D5-LOCAL-SYNTHETIC-ACCEPTANCE.json').read_bytes())
        self.assertFalse(a['D5_closed']);self.assertEqual(a['milestone_id'],'D5-LOCAL-SYNTHETIC-I1-I20')

    def df03(self):
        lab=self.lab();h=capture(lab);c=lab.client
        ph=c.perform('REGISTER_PROFILE',dict(descriptor=q.descriptor()))['result']['profile_hash']
        c.perform('SELECT_PROFILE',dict(profile_hash=ph));self.fresh_process(lab)
        out=lab.fresh().import_event(h)['result'];s=self.state(lab)
        self.assertFalse(out['blocked']);self.assertEqual(s['reviews'],{});self.assertEqual(s['tasks'],{})
        src=s['sources'][out['source_id']];self.assertEqual(base64.b64decode(src['capture']['content_base64']),DATA)
        self.assertEqual(src['pin']['commit_sha256'],h)

    def df04(self):
        lab=self.lab();h=capture(lab)
        self.error('PIN_UNREACHABLE',lab.client.import_event,'0'*64)
        self.error('PIN_EVENT',lab.client.import_event,h,99)
        ids=ready(lab);s=self.state(lab);pin=deepcopy(s['sources'][ids['source']]['pin'])
        for key,value in [('scope_sha256','0'*64),('capture_sha256','0'*64),('run_id',uid())]:
            bad=deepcopy(pin);bad[key]=value
            self.error('PIN_',lab.client._pin,bad)
        self.assertEqual(len(self.state(lab)['tasks']),1)

    def df05(self):
        for decoder,mime,data in [('markdown-structure.v1','text/markdown',DATA),
                                  ('task-register.v1','application/vnd.google-apps.document',DATA),
                                  ('task-register.v1','text/markdown',b'- [ ] Narrative only\n')]:
            with self.subTest(decoder=decoder,mime=mime):
                lab=self.lab();c=lab.client
                ph=c.perform('REGISTER_PROFILE',dict(descriptor=q.descriptor(decoder_id=decoder)))['result']['profile_hash']
                c.perform('SELECT_PROFILE',dict(profile_hash=ph))
                src=c.import_event(capture(lab,data,mime=mime))['result']
                self.assertTrue(src['blocked']);self.assertEqual(self.state(lab)['tasks'],{})

    def df06(self):
        lab=self.lab();ids=ready(lab,apply=False,projection=False);c=lab.client
        c.review('EVALUATION',ids['evaluation'],'REVOKE',1)
        self.error('REVIEW_REQUIRED',c.perform,'APPLY',dict(manifest_id=ids['effect'],review_version=1))
        c.review('EVALUATION',ids['evaluation'],'ACCEPT',2)
        self.error('REVIEW_REQUIRED',c.perform,'APPLY',dict(manifest_id=ids['effect'],review_version=1))
        self.assertFalse(self.state(lab)['tasks'])
        self.error('MANIFEST_REQUIRED',c.review,'PROJECTION',ids['effect'])

    def df07(self):
        lab=self.lab();store_id=uid();p,c=start(lab,'initialize',dict(store_id=store_id,config=lab.config),point='before_object')
        try:self.assertEqual(receive(p,c),('READY','before_object'))
        finally:
            if p.is_alive():p.kill()
            self.assertEqual(finish(p,c),-signal.SIGKILL)
        from source_ingest.durable_store import Store
        path=lab.root/'initializing'
        st=Store(path,lab.run_id,store_id,'CLIENT',client_reduce,client_genesis)
        self.error('CORRUPT_OR_INCOMPLETE_HEAD',st.snapshot)
        self.error('ALREADY_EXISTS',st.create,lab.config)
        self.assertFalse((path/'head.json').exists());self.assertTrue((path/'marker.json').exists())

    def phase_args(self,lab,phase):
        ids=ready(lab);c=lab.client
        if phase=='IMPORT':
            src=self.state(lab)['sources'][ids['source']]
            return dict(kind='IMPORT',args=dict(pin=src['pin'],capture=src['capture']))
        if phase.startswith('REVIEW'):
            stage='SOURCE' if phase=='REVIEW' else phase.split('_',1)[1]
            mid=ids[{'SOURCE':'source','EVALUATION':'evaluation','EFFECT':'effect','PROJECTION':'projection'}[stage]]
            return dict(kind='REVIEW',args=dict(stage=stage,manifest_id=mid,expected_version=1,decision='REVOKE',reason_code='TEST'))
        if phase=='PREPARE_EVALUATION':return dict(kind=phase,args=dict(source_id=ids['source'],source_review=1,account_id=ids['account']))
        if phase=='VALIDATE_EVALUATION':return dict(kind=phase,args=dict(manifest_id=ids['evaluation'],review_version=1))
        if phase=='PREPARE_EFFECT':return dict(kind=phase,args=dict(evaluation=ids['evaluation'],evaluation_review=1,source_key='FIX-1',target_id=uid(30),target_key='FIXTURE-1'))
        if phase=='PREPARE_PROJECTION':
            pm=self.state(lab)['manifests'][ids['projection']]
            return dict(kind=phase,args={k:pm[k] for k in ('capabilities','remote_base','remote_identity')}|dict(binding_id=uid(40)))
        if phase=='ISSUE':return dict(kind=phase,args=dict(manifest_id=ids['projection'],review_version=1,send_id=uid(),ticket=uid(),capabilities=CAPS,retry=False))
        out=c.dispatch(ids['projection'],1,deliver=False);v=self.state(lab)['sends'][out['send_id']]
        if phase=='QUERY':return dict(kind=phase,args=dict(send_id=out['send_id'],query_id=uid(),ledger_version=v['ledger_version']))
        proof=lab.remote.execute(out['ticket'],self.state(lab)['manifests'][ids['projection']])
        return dict(kind='RESULT',args=dict(send_id=out['send_id'],ledger_version=v['ledger_version'],proof=proof,query_id=None))

    def commit_crashes(self,point,published):
        phases=('IMPORT','REVIEW','REVIEW_EVALUATION','REVIEW_EFFECT','REVIEW_PROJECTION','PREPARE_EVALUATION','VALIDATE_EVALUATION','PREPARE_EFFECT','PREPARE_PROJECTION','ISSUE','QUERY','RESULT')
        for phase in phases:
            with self.subTest(phase=phase,point=point):
                lab=self.lab();args=self.phase_args(lab,phase);cid=uid();args['cid']=cid
                before=independent(lab.root/'client');expected={k:before['head'][k] for k in ('seq','commit_sha256')};args['expected']=expected
                kill_at(lab,'mutate',args,point)
                after=independent(lab.root/'client')
                self.assertEqual(after['head']['seq'],before['head']['seq']+int(published))
                self.assertEqual(cid in after['state']['receipts'],published)
                self.fresh_process(lab)
                if published:
                    r=lab.fresh().perform(**args);self.assertTrue(r['historical'])
                else:self.assertEqual(after['state'],before['state'])

    def df08(self):self.commit_crashes('before_object',False)
    def df09(self):self.commit_crashes('after_object',False)
    def df10(self):self.commit_crashes('before_replace',False)

    def df11(self):
        for phase in ('IMPORT','REVIEW','REVIEW_EVALUATION','REVIEW_EFFECT','REVIEW_PROJECTION','PREPARE_EVALUATION','VALIDATE_EVALUATION','PREPARE_EFFECT','PREPARE_PROJECTION','ISSUE','QUERY','RESULT'):
            with self.subTest(phase=phase):
                lab=self.lab();args=self.phase_args(lab,phase);cid=uid();args['cid']=cid
                def fault(point):
                    if point=='directory_fsync':raise OSError('controlled')
                c=lab.fresh(client_hook=fault)
                self.error('COMMIT_UNKNOWN',c.perform,**args)
                self.error('RECOVERY_REQUIRED',c.snapshot)
                self.assertIn(cid,independent(lab.root/'client')['state']['receipts'])
                self.fresh_process(lab)
                def recovery_fault(point):
                    if point=='recovery_fsync':raise OSError('controlled')
                self.error('COMMIT_UNKNOWN',lab.fresh(client_hook=recovery_fault).snapshot)
                self.assertEqual(len(self.entities(lab)),int(phase=='RESULT'))

    def df12(self):self.commit_crashes('after_head',True)

    def df13(self):
        for point in ('before_object','after_object','before_replace','after_head'):
            lab=self.lab();ids=ready(lab,apply=False,projection=False)
            kill_at(lab,'mutate',dict(kind='APPLY',args=dict(manifest_id=ids['effect'],review_version=1)),point)
            s=self.state(lab);yes=point=='after_head'
            self.assertEqual(bool(s['tasks']),yes);self.assertEqual(bool(s['mappings']),yes)
            self.assertEqual(bool(s['bases']),yes);self.assertEqual(bool(s['provenance']),yes)
            if yes:self.assertEqual(s['bases'][uid(30)],s['tasks'][uid(30)])
            self.fresh_process(lab)

    def df14(self):
        lab=self.lab();ids=ready(lab,projection=False);self.fresh_process(lab)
        self.assertEqual(len(self.state(lab)['tasks']),1);self.assertFalse(self.entities(lab));self.assertFalse(self.state(lab)['sends'])

    def df15(self):
        for point in ('after_object','before_replace'):
            lab=self.lab();ids=ready(lab)
            kill_at(lab,'dispatch',dict(mid=ids['projection'],review_version=1),point)
            self.assertFalse(self.entities(lab));self.assertFalse(self.state(lab)['sends'])

    def df16(self):
        lab=self.lab();ids=ready(lab);sid=uid()
        kill_at(lab,'dispatch',dict(mid=ids['projection'],review_version=1,send_id=sid),'after_issue')
        self.assertEqual(self.fresh_process(lab)['sends'][0]['status'],'UNKNOWN');self.assertFalse(self.entities(lab))
        lab.fresh().reconcile(sid);self.assertEqual(self.state(lab)['sends'][sid]['status'],'UNKNOWN')

    def remote_crashes(self,point,published):
        for mode in ('CREATE','UPDATE','CLOSE'):
            with self.subTest(mode=mode,point=point):
                lab=self.lab();ids=ready(lab)
                if mode=='UPDATE':
                    lab.client.dispatch(ids['projection'],1)
                    pm=lab.client.prepare_projection(uid(40))['result']['manifest_id'];lab.client.review('PROJECTION',pm);ids['projection']=pm
                sid=uid();out=lab.client.dispatch(ids['projection'],1,send_id=sid,deliver=False)
                m=self.state(lab)['manifests'][ids['projection']]
                before=independent(lab.root/'remote')
                kill_at(lab,'remote',dict(ticket=out['ticket'],m=m,close=mode=='CLOSE'),point,role='REMOTE')
                after=independent(lab.root/'remote')
                self.assertEqual(after['head']['seq'],before['head']['seq']+int(published))
                proof=lab.fresh().remote.lookup(out['ticket'],m)
                self.assertEqual(proof is not None,published)
                if published:
                    self.assertEqual(proof['status'],'CLOSED_NO_EFFECT' if mode=='CLOSE' else 'EFFECT_CONFIRMED')
                    lab.fresh().reconcile(sid)
                else:
                    self.assertEqual(before['state'],after['state']);lab.fresh().reconcile(sid,close=True)
                self.assertNotEqual(self.state(lab)['sends'][sid]['status'],'UNKNOWN')

    def df17(self):self.remote_crashes('before_object',False)
    def df18(self):self.remote_crashes('after_object',False)

    def df19(self):
        for mode in ('CREATE','UPDATE','CLOSE'):
            lab=self.lab();ids=ready(lab)
            if mode=='UPDATE':
                lab.client.dispatch(ids['projection'],1)
                pm=lab.client.prepare_projection(uid(40))['result']['manifest_id'];lab.client.review('PROJECTION',pm);ids['projection']=pm
            out=lab.client.dispatch(ids['projection'],1,deliver=False);m=self.state(lab)['manifests'][ids['projection']]
            def fault(point):
                if point=='directory_fsync':raise OSError('controlled')
            r=Remote(lab.root/'remote',lab.run_id,lab.remote_id,hook=fault)
            self.error('COMMIT_UNKNOWN',r.execute,out['ticket'],m,close=mode=='CLOSE')
            self.assertEqual(self.state(lab)['sends'][out['send_id']]['status'],'UNKNOWN')
            lab.fresh().reconcile(out['send_id']);self.assertIsNotNone(self.state(lab)['sends'][out['send_id']]['proof'])

    def df20(self):
        self.remote_crashes('before_replace',False)
        self.remote_crashes('after_head',True)
        lab=self.lab();ids=ready(lab);sid=uid()
        kill_at(lab,'dispatch',dict(mid=ids['projection'],review_version=1,send_id=sid),'after_remote')
        self.assertEqual(len(self.entities(lab)),1);self.assertEqual(self.fresh_process(lab)['sends'][0]['status'],'UNKNOWN')
        lab.fresh().reconcile(sid);self.assertEqual(self.state(lab)['sends'][sid]['status'],'EFFECT_CONFIRMED')
        self.assertEqual(len(self.entities(lab)),1)

    def df21(self):
        lab=self.lab();ids=ready(lab);out=lab.client.dispatch(ids['projection'],1,deliver=False)
        lab.remote.execute(out['ticket'],self.state(lab)['manifests'][ids['projection']])
        kill_at(lab,'reconcile',dict(sid=out['send_id']),'before_result')
        self.assertEqual(self.state(lab)['sends'][out['send_id']]['status'],'UNKNOWN')
        lab.fresh().reconcile(out['send_id']);self.assertEqual(len(self.entities(lab)),1)
        self.assertEqual(self.state(lab)['pending'],{})

    def df22(self):
        lab=self.lab();ids=ready(lab);args=self.phase_args_result(lab,ids);cid=uid();args['cid']=cid
        before=lab.client.snapshot()['head'];args['expected']={k:before[k] for k in ('seq','commit_sha256')}
        kill_at(lab,'mutate',args,'after_head')
        rid=next(iter(self.entities(lab)));lab.remote.edit(rid,payload=dict(name='Later remote',description='Later'))
        r=lab.fresh().perform(**args);self.assertTrue(r['historical']);self.assertEqual(self.entities(lab)[rid]['payload']['name'],'Later remote')
        bad=deepcopy(args);bad['args']['proof']=None
        self.error('COMMAND_CONFLICT',lab.fresh().perform,**bad)

    def phase_args_result(self,lab,ids):
        out=lab.client.dispatch(ids['projection'],1,deliver=False)
        p=lab.remote.execute(out['ticket'],self.state(lab)['manifests'][ids['projection']])
        return dict(kind='RESULT',args=dict(send_id=out['send_id'],ledger_version=1,proof=p,query_id=None))

    def df23(self):
        lab=self.lab();ids=ready(lab);out=lab.client.dispatch(ids['projection'],1,deliver=False)
        for _ in range(2):lab.fresh().reconcile(out['send_id'])
        self.assertEqual(self.state(lab)['sends'][out['send_id']]['status'],'UNKNOWN');self.assertFalse(self.entities(lab))

    def df24(self):
        lab=self.lab();ids=ready(lab);out=lab.client.dispatch(ids['projection'],1,deliver=False);m=self.state(lab)['manifests'][ids['projection']]
        lab.fresh().reconcile(out['send_id'],close=True)
        p=lab.fresh().remote.execute(out['ticket'],m);self.assertEqual(p['status'],'CLOSED_NO_EFFECT');self.assertFalse(self.entities(lab))

    def df25(self):
        lab=self.lab();ids=ready(lab);out=lab.client.dispatch(ids['projection'],1,deliver=False);m=self.state(lab)['manifests'][ids['projection']]
        barrier=CONTEXT.Barrier(2);workers=[start(lab,'remote',dict(ticket=out['ticket'],m=m,close=close),barrier=barrier) for close in (False,True)]
        answers=[]
        for p,c in workers:
            answers.append(receive(p,c));self.assertEqual(finish(p,c),0)
        self.assertTrue(all(a[0]=='OK' for a in answers));self.assertEqual(answers[0][1],answers[1][1])
        self.assertIn(answers[0][1]['status'],('EFFECT_CONFIRMED','CLOSED_NO_EFFECT'))
        self.assertEqual(len(self.entities(lab)),int(answers[0][1]['status']=='EFFECT_CONFIRMED'))

    def df26(self):
        for field in ('store_id','run_id','ticket','request_hash','creation_key','manifest_hash','payload_hash'):
            lab=self.lab();ids=ready(lab);out=lab.client.dispatch(ids['projection'],1,deliver=False)
            lab.remote.execute(out['ticket'],self.state(lab)['manifests'][ids['projection']])
            def bad(p):
                p[field]='0'*64 if field.endswith('hash') or field=='creation_key' else uid();return p
            lab.client.reconcile(out['send_id'],proof_hook=bad)
            self.assertEqual(self.state(lab)['sends'][out['send_id']]['status'],'CONFLICT')
            lab.client.reconcile(out['send_id']);self.assertEqual(self.state(lab)['sends'][out['send_id']]['status'],'CONFLICT')

    def df27(self):
        lab=self.lab();ids=ready(lab);out=lab.client.dispatch(ids['projection'],1,reject='RATE_LIMIT',retry_tick=5)
        self.error('RETRY_NOT_ELIGIBLE',lab.client.dispatch,ids['projection'],1,send_id=out['send_id'],retry=True)
        lab.client.perform('CLOCK',dict(tick=5))
        for _ in range(2):lab.client.dispatch(ids['projection'],1,send_id=out['send_id'],retry=True,reject='REJECTED')
        self.error('ATTEMPT_BUDGET',lab.client.dispatch,ids['projection'],1,send_id=out['send_id'],retry=True)
        self.assertFalse(self.entities(lab));self.assertEqual(len(self.state(lab)['sends'][out['send_id']]['attempts']),3)

    def df28(self):
        lab=self.lab();ids=ready(lab);out=lab.client.dispatch(ids['projection'],1,deliver=False)
        for sid,retry in ((out['send_id'],True),(uid(),False)):
            self.error('BINDING_UNRESOLVED',lab.client.dispatch,ids['projection'],1,send_id=sid,retry=retry)
        pm=lab.client.prepare_projection(uid(40))['result']['manifest_id'];lab.client.review('PROJECTION',pm,'ACCEPT',1)
        self.error('BINDING_UNRESOLVED',lab.client.dispatch,pm,2)

    def df29(self):
        for mode in ('head','missing','hash'):
            lab=self.lab();ready(lab);head=json.loads((lab.root/'client/head.json').read_bytes())
            obj=lab.root/'client/objects'/(head['commit_sha256']+'.json')
            if mode=='head':(lab.root/'client/head.json').write_bytes(b'{}')
            elif mode=='missing':obj.unlink()
            else:obj.write_bytes(b'{}')
            self.error('INVALID_SHAPE|STORE_UNAVAILABLE|CORRUPT',lab.fresh().snapshot)

    def df30(self):
        for mode in ('marker','symlink','extra','duplicate'):
            lab=self.lab();ready(lab);p=lab.root/'client/marker.json';raw=p.read_bytes()
            if mode=='marker':
                bad=json.loads(raw);bad['role']='REMOTE';p.write_bytes(canonical(bad))
            elif mode=='symlink':p.unlink();p.symlink_to(lab.sentinel)
            elif mode=='extra':p.write_bytes(canonical(json.loads(raw)|dict(extra=True)))
            else:p.write_bytes(b'{"a":1,"a":2}')
            try:self.error('STORE_|DUPLICATE_KEY',lab.fresh().snapshot)
            finally:
                if p.is_symlink():p.unlink()
                p.write_bytes(raw)
        self.error('INVALID_JSON',canonical,dict(x=1.1))

    def df31(self):
        lab=self.lab();ids=ready(lab,apply=False,projection=False);lab.client.perform('CLOCK',dict(tick=95))
        self.assertEqual(self.fresh_process(lab)['clock_tick'],95)
        lab.client.perform('VALIDATE_EVALUATION',dict(manifest_id=ids['evaluation'],review_version=1))
        lab.client.perform('CLOCK',dict(tick=96));self.error('BLOCKED_EVALUATION',lab.client.perform,'APPLY',dict(manifest_id=ids['effect'],review_version=1))
        self.error('CLOCK_BACKWARDS',lab.client.perform,'CLOCK',dict(tick=0))

    def df32(self):
        for mode in ('profile','policy','source','review'):
            lab=self.lab();ids=ready(lab)
            if mode=='profile':
                lab.client.perform('SELECT_PROFILE',dict(profile_hash=None));lab.client.perform('SELECT_PROFILE',dict(profile_hash=ids['profile']))
            elif mode=='policy':
                p=self.state(lab)['policy'];lab.client.perform('POLICY',dict(policy=p));lab.client.perform('POLICY',dict(policy=p))
            elif mode=='source':lab.client.import_event(capture(lab))
            else:lab.client.review('SOURCE',ids['source'],'REVOKE',1);lab.client.review('SOURCE',ids['source'],'ACCEPT',2)
            self.error('STALE_|REVIEW_REQUIRED|BLOCKED_SOURCE',lab.client.dispatch,ids['projection'],1)
            self.assertEqual(self.state(lab)['mappings'][uid(30)][-1],'FIX-1');self.assertFalse(self.entities(lab))

    def df33(self):
        for change in ('new_fact','revocation','adapter','expired'):
            lab=self.lab();ids=ready(lab);a=self.state(lab)['accounts'][ids['account']]
            if change=='new_fact':
                obs=deepcopy(next(iter(a['observations'].values())));obs['observation_id']=uid()
                lab.client.perform('OBSERVE',dict(account_id=ids['account'],observation=obs,generation=a['generation']))
            elif change=='revocation':lab.client.perform('REVOKE_OBSERVATION',dict(account_id=ids['account'],observation_id=next(iter(a['observations'])),generation=a['generation']))
            elif change=='adapter':lab.client.perform('ADAPTER',dict(account_id=ids['account'],adapter=q.adapter(uid(13),permission='REVOKED'),generation=a['generation']))
            else:lab.client.perform('CLOCK',dict(tick=100))
            self.error('STALE_|BLOCKED_EVALUATION',lab.client.dispatch,ids['projection'],1)
        lab=self.lab();ids=ready(lab);s=self.state(lab);a=s['accounts'][ids['account']]
        from source_ingest.durable_task_fixture import eligible
        self.assertTrue(eligible(s,a))
        for field,value in [('remaining',0),('state','UNKNOWN'),('observed_at',1)]:
            bad=deepcopy(a);next(iter(bad['observations'].values()))[field]=value;self.assertFalse(eligible(s,bad))
        self.assertEqual(lab.client.summary()['reservations_created'],0)

    def df34(self):
        lab=self.lab();ids=ready(lab)
        lab.client.perform('EDIT_TASK',dict(target_id=uid(30),changes=dict(foreign=dict(note='local'))))
        self.error('STALE_LOCAL',lab.client.dispatch,ids['projection'],1);self.assertFalse(self.entities(lab))
        self.assertEqual(self.state(lab)['tasks'][uid(30)]['foreign'],dict(note='local'))

    def df35(self):
        lab=self.lab();ids=ready(lab);lab.client.review('PROJECTION',ids['projection'],'REVOKE',1)
        self.error('REVIEW_REQUIRED',lab.client.dispatch,ids['projection'],1)
        lab=self.lab();ids=ready(lab);out=lab.client.dispatch(ids['projection'],1,deliver=False)
        lab.client.review('PROJECTION',ids['projection'],'REVOKE',1)
        lab.remote.execute(out['ticket'],self.state(lab)['manifests'][ids['projection']]);lab.client.reconcile(out['send_id'])
        view=lab.client.summary()['sends'][0];self.assertEqual((view['status'],view['validity']),('EFFECT_CONFIRMED','STALE'))

    def df36(self):
        lab=self.lab();ids=ready(lab);lab.client.dispatch(ids['projection'],1)
        rid=next(iter(self.entities(lab)));lab.remote.edit(rid,foreign=dict(sentinel='keep'))
        pm=lab.client.prepare_projection(uid(40))['result']['manifest_id'];lab.client.review('PROJECTION',pm)
        original=deepcopy(self.entities(lab)[rid]['payload'])
        lab.remote.edit(rid,payload=dict(name='B',description='B'));lab.remote.edit(rid,payload=original)
        out=lab.client.dispatch(pm,1);self.assertEqual(out['receipt']['result']['outcome'],'NO_EFFECT')
        self.assertEqual(self.entities(lab)[rid]['foreign'],dict(sentinel='keep'))
        self.error('RETRY_NOT_ELIGIBLE',lab.client.dispatch,pm,1,send_id=out['send_id'],retry=True)
        fresh=lab.client.prepare_projection(uid(40))['result']['manifest_id'];self.assertNotEqual(pm,fresh)

    def df37(self):
        lab=self.lab();ids=ready(lab);m=self.state(lab)['manifests'][ids['projection']];ticket=uid()
        first=lab.remote.execute(ticket,m);again=lab.fresh().remote.execute(ticket,m);self.assertEqual(first,again)
        second=lab.remote.execute(uid(),m);self.assertEqual(second['status'],'NO_EFFECT');self.assertEqual(len(self.entities(lab)),1)
        bad=deepcopy(m);bad['payload']['name']='Different';bad['task']['title']='Different'
        self.error('TICKET_CONFLICT',lab.remote.execute,ticket,bad)

    def df38(self):
        lab=self.lab();ids=ready(lab,apply=False,projection=False);head=lab.client.snapshot()['head'];exp={k:head[k] for k in ('seq','commit_sha256')}
        args=[dict(kind='APPLY',args=dict(manifest_id=ids['effect'],review_version=1),expected=exp),
              dict(kind='REVIEW',args=dict(stage='SOURCE',manifest_id=ids['source'],expected_version=1,decision='REVOKE',reason_code='TEST'),expected=exp)]
        barrier=CONTEXT.Barrier(2);ws=[start(lab,'mutate',a,barrier=barrier) for a in args];ans=[]
        for p,c in ws:ans.append(receive(p,c));self.assertEqual(finish(p,c),0)
        self.assertEqual(sorted(x[0] for x in ans),['ERROR','OK']);self.assertIn('CONFLICT_HEAD',[x[1] for x in ans if x[0]=='ERROR'])
        self.assertEqual(independent(lab.root/'client')['head']['seq'],head['seq']+1)

    def df39(self):
        lab=self.lab();ids=ready(lab);out=lab.client.dispatch(ids['projection'],1,deliver=False);sid=out['send_id']
        m=self.state(lab)['manifests'][ids['projection']];proof=lab.remote.execute(out['ticket'],m)
        qid=uid();lab.client.perform('QUERY',dict(send_id=sid,query_id=qid,ledger_version=1))
        lab.client.reconcile(sid)
        self.error('CONFLICT_LEDGER',lab.client.perform,'RESULT',dict(send_id=sid,ledger_version=1,proof=proof,query_id=qid))
        self.assertEqual(self.state(lab)['sends'][sid]['status'],'EFFECT_CONFIRMED')

    def df40(self):
        lab=self.lab();ready(lab);before=lab.client.snapshot()['head'];exp={k:before[k] for k in ('seq','commit_sha256')}
        owner,oc=start(lab,'mutate',dict(kind='CLOCK',args=dict(tick=1),expected=exp),point='before_object')
        waiter=wc=None
        try:
            self.assertEqual(receive(owner,oc),('READY','before_object'))
            barrier=CONTEXT.Barrier(2)
            waiter,wc=start(lab,'raw_mutate',dict(cid=uid(),kind='CLOCK',args=dict(tick=2),expected=exp),point='before_lock',barrier=barrier)
            self.assertEqual(receive(waiter,wc),('READY','before_lock'));barrier.wait(timeout=15)
            owner.kill();self.assertEqual(finish(owner,oc),-signal.SIGKILL)
            result=receive(waiter,wc);self.assertEqual(result[0],'OK');self.assertEqual(finish(waiter,wc),0)
        finally:
            for p,c in ((owner,oc),(waiter,wc)):
                if p is not None and p.is_alive():p.kill();finish(p,c)
        self.assertEqual(self.fresh_process(lab)['clock_tick'],2)

    def df41(self):
        lab=self.lab()
        with patch('socket.socket',side_effect=AssertionError('NETWORK_FORBIDDEN')),patch('subprocess.Popen',side_effect=AssertionError('PROCESS_FORBIDDEN')):
            ids=ready(lab);lab.client.dispatch(ids['projection'],1)
        s=lab.client.summary()
        for k in ('remote_requests','persistent_D2_writes','operations','operational_attempts','quota_consumed','reservations_created'):self.assertEqual(s[k],0)
        self.assertFalse(s['activation_allowed']);self.assertEqual(len(self.entities(lab)),1)

    def df42(self):
        lab=self.lab();ids=ready(lab);self.fresh_process(lab);home=lab.home;cap=lab.capture.root
        lab.close();self.assertFalse(home.exists());self.assertFalse(cap.exists());self.assertTrue(all(not p.is_alive() for p in CHILDREN))

    def df43(self):
        lab=self.lab();p=lab.root/'client/marker.json';raw=p.read_bytes();p.write_bytes(b'{}')
        try:self.error('CLEANUP_MARKER',lab.close);self.assertTrue(lab.sentinel.exists())
        finally:p.write_bytes(raw)
        link=lab.root/'client'/'external';link.symlink_to(lab.sentinel)
        try:self.error('CLEANUP_SYMLINK',lab.close);self.assertEqual(lab.sentinel.read_bytes(),b'SYNTHETIC_SIBLING')
        finally:link.unlink()

    def df44(self):
        for limits,code in [(dict(LIMITS,commands=2),'COMMAND_BUDGET'),(dict(LIMITS,commits=3),'HISTORY_HEADROOM')]:
            lab=self.lab(limits=limits);lab.client.perform('CLOCK',dict(tick=1));lab.client.perform('CLOCK',dict(tick=2))
            before=independent(lab.root/'client');self.error(code,lab.client.perform,'CLOCK',dict(tick=3))
            self.assertEqual(independent(lab.root/'client'),before)
        lab=self.lab(bounds=dict(BOUNDS,profiles=1))
        lab.client.perform('REGISTER_PROFILE',dict(descriptor=q.descriptor()))
        self.error('PROFILE_BUDGET',lab.client.perform,'REGISTER_PROFILE',dict(descriptor=q.descriptor(2)))
        lab=self.lab();ids=ready(lab);src=deepcopy(self.state(lab)['sources'][ids['source']]);src['capture']['content_base64']=base64.b64encode(b'x'*(2097152+1)).decode();src['pin']['capture_sha256']=digest(src['capture'])
        self.error('SOURCE_BUDGET',client_reduce,deepcopy(self.state(lab)),'IMPORT',dict(pin=src['pin'],capture=src['capture']))


        # All new catalog budgets are explicit; reduced budgets exercise rejection branches.
        for category in ('accounts','observations','manifests','reviews','tasks','tickets'):
            with self.subTest(budget=category):
                lab=self.lab();ids=ready(lab);original=self.state(lab)
                if category=='tickets':
                    pm=original['manifests'][ids['projection']]
                    one=lab.remote.execute(uid(),pm)
                    rs=independent(lab.root/'remote')['state'];rs['config']['bounds']['tickets']=1
                    self.error('TICKET_BUDGET',remote_reduce,rs,'EXECUTE',dict(ticket=uid(),manifest=pm,run_id=lab.run_id,store_id=lab.remote_id,reject=None,retry_tick=0))
                    continue
                state=deepcopy(original);state['config']['bounds'][category]=1
                if category=='accounts':
                    op='BIND_ACCOUNT';args=dict(binding=q.account(uid(),uid(),uid(),uid(1)),adapter=q.adapter(uid()))
                elif category=='observations':
                    a=state['accounts'][ids['account']];obs=deepcopy(next(iter(a['observations'].values())));obs['observation_id']=uid()
                    op='OBSERVE';args=dict(account_id=ids['account'],observation=obs,generation=a['generation'])
                elif category=='manifests':
                    state['tick']=1;op='PREPARE_EVALUATION';args=dict(source_id=ids['source'],source_review=1,account_id=ids['account'])
                elif category=='reviews':
                    op='REVIEW';args=dict(stage='SOURCE',manifest_id=ids['source'],expected_version=1,decision='REVOKE',reason_code='TEST')
                else:
                    op='PREPARE_EFFECT';args=dict(evaluation=ids['evaluation'],evaluation_review=1,source_key='FIX-1',target_id=uid(),target_key='OTHER')
                    # A different key is deliberately selected from the same source: first guard is uniqueness.
                    state['mappings'][uid(30)][-1]='OTHER-KEY'
                self.error('BUDGET',client_reduce,state,op,args)
                self.assertEqual(self.state(lab),original)
        for category in ('manifest_bytes','text_characters','constraints'):
            lab=self.lab();ids=ready(lab);state=self.state(lab);state['config']['bounds'][category]=1
            if category=='constraints':
                self.error('CONSTRAINT_BUDGET',client_reduce,state,'POLICY',dict(policy=state['policy']))
            else:
                self.error('MANIFEST_BUDGET|INVALID_LABEL',client_reduce,state,'PREPARE_EFFECT',dict(evaluation=ids['evaluation'],evaluation_review=1,source_key='FIX-1',target_id=uid(30),target_key='FIXTURE-1'))
        lab=self.lab();ids=ready(lab);out=lab.client.dispatch(ids['projection'],1,deliver=False)
        for _ in range(6):lab.client.reconcile(out['send_id'])
        self.error('QUERY_BUDGET',lab.client.reconcile,out['send_id'])

        for field,value,code in [('commit_bytes',4096,'COMMIT_BUDGET'),('store_bytes',16384,'STORE_HEADROOM')]:
            lab=self.lab(limits=dict(LIMITS,**{field:value}))
            for tick in range(1,20):
                before=independent(lab.root/'client')
                try:lab.client.perform('CLOCK',dict(tick=tick))
                except DurableError as ex:
                    self.assertEqual(str(ex),code);self.assertEqual(independent(lab.root/'client'),before);break
            else:self.fail('Budget boundary was not reached')
        for limits,code in [(dict(LIMITS,store_bytes=2*1024*1024),'STORE_HEADROOM'),(dict(LIMITS,commit_bytes=65536),'COMMIT_BUDGET')]:
            lab=self.lab(limits=limits);ids=ready(lab);before=independent(lab.root/'client')
            self.error(code,lab.client.dispatch,ids['projection'],1)
            self.assertEqual(independent(lab.root/'client'),before);self.assertFalse(self.entities(lab))

    def df45(self):
        limits=dict(LIMITS,commits=25);lab=self.lab(limits=limits);ids=ready(lab)
        before=lab.client.snapshot()['head'];self.assertLess(before['seq'],24)
        out=lab.client.dispatch(ids['projection'],1,deliver=False)
        while lab.client.snapshot()['head']['seq']<23:lab.client.perform('CLOCK',dict(tick=0))
        self.error('HISTORY_HEADROOM',lab.client.perform,'CLOCK',dict(tick=0))
        m=self.state(lab)['manifests'][ids['projection']];p=lab.remote.execute(out['ticket'],m)
        lab.client.perform('RESULT',dict(send_id=out['send_id'],ledger_version=1,proof=p,query_id=None))
        self.assertEqual(lab.client.snapshot()['head']['seq'],24)
        self.assertEqual(self.state(lab)['pending'],{})

    def df46(self):
        lab=self.lab();ids=ready(lab,projection=False);state=self.state(lab)
        mem=MemoryLab();cap=mem.capture(DATA,uid(1),uid(2),profile='task-register.v1');mem.review('SOURCE',cap,expected_version=0,decision='ACCEPT')
        ef=mem.prepare_effect(cap,'FIX-1',uid(30),'FIXTURE-1',source_review_version=1);mem.review('EFFECT',ef,expected_version=0,decision='ACCEPT');mem.apply_effect(uid(),ef,review_version=1)
        self.assertEqual(mem.entity(uid(30))['title'],state['tasks'][uid(30)]['title'])
        ref=q.EligibilityLab();ph=ref.register_profile(q.descriptor());ref.select_profile(uid(1),uid(2),ph,expected_generation=0)
        rc=ref.capture(DATA,uid(1),uid(2),'fixture-1');ref.review('SOURCE',rc,expected_version=0,decision='ACCEPT',reason='fixture')
        acct=state['accounts'][ids['account']];ref.bind_account(acct['binding'],acct['adapter']);ref.select_policy(uid(1),state['policy'],expected_generation=0);gen=1
        for obs in acct['observations'].values():
            gen=ref.publish_observation(ids['account'],obs,expected_generation=gen);gen=ref.select_observation(ids['account'],obs['observation_id'],expected_generation=gen)
        em=ref.prepare_evaluation(rc,ids['account'],source_review_version=1);ref.review('EVALUATION',em,expected_version=0,decision='ACCEPT',reason='fixture')
        r=ref.validate_evaluation(uid(),em,evaluation_review_version=1)
        actual=lab.client.perform('VALIDATE_EVALUATION',dict(manifest_id=ids['evaluation'],review_version=1))
        self.assertEqual(r['result'],actual['result']['outcome'])
        plane=PlaneFixture(capabilities());old=ReconciliationLab(plane);old.bind(binding(uid(40),uid(1),uid(30),uid(3),uid(4)),task(uid(1),uid(30),title='Synthetic item',description='Review only'))
        pm=old.prepare(uid(40));old.review(pm,expected_version=0,decision='ACCEPT',reason='fixture');v=old.dispatch(uid(),pm,review_version=1)
        self.assertEqual(v['result'],'EFFECT_CONFIRMED')
        lab.client.perform('BIND',dict(binding_id=uid(40),target_id=uid(30)));mid=lab.client.prepare_projection(uid(40))['result']['manifest_id'];lab.client.review('PROJECTION',mid)
        now=lab.client.dispatch(mid,1);self.assertEqual(now['receipt']['result']['outcome'],v['result'])
        ref.advance_clock(100);lab.client.perform('CLOCK',dict(tick=100))
        self.error('BLOCKED_EVALUATION',lab.client.perform,'VALIDATE_EVALUATION',dict(manifest_id=ids['evaluation'],review_version=1))
        self.assertEqual(ref.validate_evaluation(uid(),em,evaluation_review_version=1)['result'],'BLOCKED')

        # Lost response / reconciliation / replay are compared with the I28 public API.
        lab=self.lab();ids=ready(lab)
        plane=PlaneFixture(capabilities());old=ReconciliationLab(plane)
        old.bind(binding(uid(40),uid(1),uid(30),uid(3),uid(4)),task(uid(1),uid(30),title='Synthetic item',description='Review only'))
        pm=old.prepare(uid(40));old.review(pm,expected_version=0,decision='ACCEPT',reason='fixture')
        plane.send_mode='LOSE_AFTER';cid=uid();historical=old.dispatch(cid,pm,review_version=1)
        new=lab.client.dispatch(ids['projection'],1,deliver=False)
        m=self.state(lab)['manifests'][ids['projection']];lab.remote.execute(new['ticket'],m)
        self.assertEqual(historical['result'],self.state(lab)['sends'][new['send_id']]['status'])
        old.reconcile(cid,expected_version=old.command(cid)['version']);lab.client.reconcile(new['send_id'])
        self.assertEqual(old.command(cid)['result'],self.state(lab)['sends'][new['send_id']]['status'])
        before=plane.count();old.dispatch(cid,pm,review_version=1);self.assertEqual(plane.count(),before)
        # Both models reject an obsolete remote base conclusively and forbid retry.
        plane.send_mode='SUCCESS';up=old.prepare(uid(40),'UPDATE');old.review(up,expected_version=0,decision='ACCEPT',reason='fixture')
        remote_id=old.command(cid)['effect_receipt']['remote_id'];plane.edit(remote_id,name='Concurrent')
        rejected=old.dispatch(uid(),up,review_version=1)
        self.assertEqual(rejected['result'],'REJECTED_NO_EFFECT');self.assertEqual(rejected['conflict'],'REMOTE_PRECONDITION')
        upnew=lab.client.prepare_projection(uid(40))['result']['manifest_id'];lab.client.review('PROJECTION',upnew)
        rid=next(iter(self.entities(lab)));lab.remote.edit(rid,payload=dict(name='Concurrent',description='Review only'))
        blocked=lab.client.dispatch(upnew,1);v=self.state(lab)['sends'][blocked['send_id']]
        self.assertEqual(v['status'],'NO_EFFECT');self.assertEqual(v['proof']['code'],rejected['conflict']);self.assertIsNone(v['retry_tick'])

    def df47(self):
        lab=self.lab();ids=ready(lab);lab.client.dispatch(ids['projection'],1,deliver=False)
        before=independent(lab.root/'remote');out=self.fresh_process(lab)
        self.assertEqual(independent(lab.root/'remote'),before)
        public=json.dumps(out);self.assertNotIn('Synthetic item',public);self.assertNotIn(str(lab.home),public);self.assertNotIn('content_base64',public)
        self.assertEqual(out['sends'][0]['status'],'UNKNOWN')

    def df48(self):
        from testing.D5.run_durable_lab import coverage,distinct_groups
        groups=distinct_groups(['test_durable_integration.A.x','test_profiles_quotas.A.x','test_durable_integration.A.x'])
        self.assertEqual(sum(len(v) for v in groups.values()),2)
        mapping=coverage();self.assertEqual(len(mapping),48);self.assertTrue(all(v for v in mapping.values()))
        self.assertNotIn('UI25',json.dumps(mapping));self.assertNotIn('UI34',json.dumps(mapping))


# Fixed IDs retain readable matrix/test mapping without manufacturing passing tests.
for _n in range(1,49):
    setattr(DurableIntegrationTest,f'test_DF{_n:02}',getattr(DurableIntegrationTest,f'df{_n:02}'))
