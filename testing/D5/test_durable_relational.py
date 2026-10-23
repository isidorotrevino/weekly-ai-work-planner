# SPDX-License-Identifier: GPL-3.0-only
"""I36 DR01-DR40: relational union, independent disk and spawned process oracles."""
import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import signal
import unittest
from unittest.mock import patch

from source_ingest.durable_store import DurableError,LIMITS,canonical,digest,Store
from source_ingest.durable_relational_fixture import (BOUNDS,Client,Remote,client_reduce,client_genesis,
    remote_reduce,projection_current,PROJECTION_SCHEMA)
from source_ingest.relational_planner import plan_batch
from source_ingest.batch_fixture import BatchLab,BatchError,validate_source,element,declaration,reference,envelope
from testing.D5 import relational_support as support
from testing.D5.relational_support import uid,source,new_lab,prepare,independent,start,receive,finish,kill_at,CONTEXT


class DurableRelationalTest(unittest.TestCase):
    def setUp(self):support.CURRENT_CASE=self._testMethodName.removeprefix('test_');self.labs=[]
    def lab(self,**kwargs):
        for old in self.labs:old.close()
        lab=new_lab(**kwargs);self.labs.append(lab);self.addCleanup(lab.close);return lab
    def error(self,pattern,fn,*args,**kwargs):
        with self.assertRaisesRegex((DurableError,BatchError),pattern):fn(*args,**kwargs)
    def state(self,lab):return independent(lab.root/'client')['state']
    def entities(self,lab):return independent(lab.root/'remote')['state']['entities']
    def reprocess(self,lab):
        p,c=start(lab,'snapshot',{})
        try:r=receive(p,c)
        finally:code=finish(p,c)
        self.assertEqual(code,0);self.assertEqual(r[0],'OK');return r[1]
    def plan(self,lab,raw,targets,*,review=True):
        c=lab.client;sid=c.capture(raw)['result']['source_id'];c.select_source(sid)
        sm=c.perform('PREPARE_SOURCE',{})['result']['manifest_id'];c.review('SOURCE',sm)
        bm=c.perform('PREPARE_BATCH',dict(source_manifest=sm,source_review=1,targets=targets))['result']['manifest_id']
        if review:c.review('BATCH',bm)
        return sm,bm
    def dr01(self):
        from testing.D5.run_relational_durable_lab import inputs,applicability
        data=inputs();self.assertIn('source_ingest/durable_store.py',data)
        self.assertIn('source_ingest/relational_planner.py',data);self.assertEqual(applicability(data),'CURRENT')
        bad=dict(data);bad['source_ingest/durable_store.py']='0'*64;self.assertEqual(applicability(bad),'STALE_INPUTS')
    def dr02(self):
        r=json.loads(Path('docs/validation/D5-I34-results.json').read_bytes())
        for p,h in r['inputs'].items():self.assertEqual(hashlib.sha256(Path(p).read_bytes()).hexdigest(),h)
        for stage in ('D3','D4'):
            r=json.loads(Path(f'docs/validation/{stage}-CLOSURE.json').read_bytes())
            for p,h in r['verified_executable_input_sha256'].items():self.assertEqual(hashlib.sha256(Path(p).read_bytes()).hexdigest(),h)
        a=json.loads(Path('docs/validation/D5-LOCAL-SYNTHETIC-ACCEPTANCE.json').read_bytes());self.assertFalse(a['D5_closed'])
    def dr03(self):
        lab=self.lab();raw,t=source();pretty=json.dumps(json.loads(raw),indent=2).encode()
        sid=lab.client.capture(pretty)['result']['source_id'];s=self.state(lab)
        self.assertEqual(sid,hashlib.sha256(pretty).hexdigest());self.assertNotEqual(sid,hashlib.sha256(raw).hexdigest())
        self.assertEqual(base64.b64decode(s['sources'][sid]['content_base64']),pretty)
        self.assertIsNone(s['selected_source']);self.assertEqual(s['reviews'],{});self.assertFalse(s['data']['entities'])
    def dr04(self):
        raw,targets=source();src=json.loads(raw)
        cases=[src|dict(extra=True),src|dict(project_id=uid(999)),src|dict(schema='unknown'),src|dict(elements=[src['elements'][0]]*2)]
        for value in cases:
            lab=self.lab();before=self.state(lab)
            self.error('SHAPE|SCOPE|SYNTHETIC|DUPLICATE',lab.client.capture,canonical(value));self.assertEqual(self.state(lab),before)
        lab=self.lab();self.error('INVALID_JSON',lab.client.capture,b'{"schema":1,"schema":2}')
        bad=json.loads(raw);bad['elements'][0]['kind']='UNKNOWN';self.error('INVALID_KIND',lab.client.capture,canonical(bad))
    def dr05(self):
        lab=self.lab();ids=prepare(lab,apply=False)
        lab.client.select_source(None);lab.client.select_source(ids['source'])
        self.error('STALE_SOURCE',lab.client.perform,'APPLY_BATCH',dict(manifest_id=ids['batch'],review_version=1))
        fresh=lab.client.perform('PREPARE_SOURCE',{})['result']['manifest_id'];self.assertNotEqual(fresh,ids['source_manifest'])
        raw,t=source(revision='captured-only');lab.client.capture(raw)
        self.assertEqual(self.state(lab)['selected_source'],ids['source'])
    def dr06(self):
        lab=self.lab();ids=prepare(lab,project=False);raw,t=source(revision='again')
        for mode in ('adopt','rename','alias'):
            changed=deepcopy(t)
            if mode=='adopt':changed[2]['target_id']=uid(999)
            if mode=='rename':changed[2]['target_key']='Renamed'
            if mode=='alias':changed[3]['target_id']=changed[2]['target_id']
            before=self.state(lab)['data'];self.error('CONFLICT',self.plan,lab,raw,changed)
            self.assertEqual(self.state(lab)['data'],before)
    def dr07(self):
        for desc in (None,''):
            lab=self.lab();raw,t=source(description=desc);ids=prepare(lab,raw,t)
            data=self.state(lab)['data'];self.assertEqual(data['entities'][uid(10)]['status'],'DRAFT')
            self.assertNotIn('description',data['entities'][uid(11)])
            self.assertEqual(data['mappings'][uid(11)]['source_base']['description'],'Unprojected epic text')
            self.assertEqual(data['entities'][uid(12)]['description'],desc)
            out=lab.client.dispatch(ids['projections'][0],1);self.assertEqual(out['receipt']['result']['outcome'],'EFFECT_CONFIRMED')
            self.assertEqual(next(iter(self.entities(lab).values()))['payload']['description'],desc)
            self.assertEqual(set(next(iter(self.entities(lab).values()))['payload']),{'name','description'})
    def dr08(self):
        raw,t=source();v=json.loads(raw)
        for field,value in [('project_id',uid(999)),('source_key','ABSENT'),('kind','REQUIREMENT')]:
            lab=self.lab();bad=deepcopy(v);bad['relations'][-1]['right'][field]=value
            self.error('CROSS_PROJECT|REFERENCE_NOT|TYPE',self.plan,lab,canonical(bad),t);self.assertFalse(self.state(lab)['data']['entities'])
        lab=self.lab();bad=deepcopy(v);bad['relations'][0]['type']='CAPABILITY';self.error('UNSUPPORTED_RELATION',lab.client.capture,canonical(bad))
    def dr09(self):
        lab=self.lab();ids=prepare(lab,project=False);before=self.state(lab)['data'];raw,t=source(revision='repeat')
        sm,bm=self.plan(lab,raw,t);lab.client.perform('APPLY_BATCH',dict(manifest_id=bm,review_version=1));after=self.state(lab)['data']
        self.assertEqual(len(before['relations']),len(after['relations']))
        self.assertEqual(before['entities'][uid(12)]['row_version'],after['entities'][uid(12)]['row_version'])
        value=json.loads(raw);value['relations'][-1]['kind']='SOFT';self.error('KIND_CONFLICT',self.plan,lab,canonical(value),t)
        # A source with no relations does not remove previously applied links.
        value=json.loads(raw);value['revision']='absence';value['relations']=[]
        sm,bm=self.plan(lab,canonical(value),t);lab.client.perform('APPLY_BATCH',dict(manifest_id=bm,review_version=1))
        self.assertEqual(len(self.state(lab)['data']['relations']),4)
    def dr10(self):
        for kind in ('HARD','SOFT','MOCKABLE','OPTIONAL'):
            lab=self.lab();raw,t=source();v=json.loads(raw);v['relations'][-1]['kind']=kind
            v['relations'].append(declaration('BACK','TASK_DEPENDENCY',reference(uid(1),uid(2),'T1','TASK'),reference(uid(1),uid(2),'T0','TASK'),kind=kind))
            if kind=='HARD':self.error('HARD_CYCLE',self.plan,lab,canonical(v),t)
            else:
                sm,bm=self.plan(lab,canonical(v),t);lab.client.perform('APPLY_BATCH',dict(manifest_id=bm,review_version=1))
                self.assertEqual(len(self.state(lab)['data']['relations']),5)
        lab=self.lab();raw,t=source();v=json.loads(raw);v['relations'][-1]['right']=v['relations'][-1]['left']
        self.error('SELF_LOOP',self.plan,lab,canonical(v),t)
    def dr11(self):
        for mode in ('entity','relation','endpoint'):
            lab=self.lab();prepare(lab,project=False)
            if mode=='entity':lab.client.perform('EDIT_ENTITY',dict(entity_id=uid(12),changes=dict(foreign=dict(note='local'))))
            else:lab.client.perform('ADD_RELATION',dict(relation=dict(type='TASK_DEPENDENCY',left=uid(13),right=uid(12),kind='SOFT')))
            raw,t=source(revision='next')
            if mode=='endpoint':v=json.loads(raw);v['elements']=v['elements'][:2];raw=canonical(v);t=t[:2]
            before=self.state(lab)['data'];self.error('LOCAL_DIVERGENCE',self.plan,lab,raw,t)
            self.assertEqual(self.state(lab)['data'],before)
    def dr12(self):
        for entity in (uid(10),uid(11),uid(12)):
            lab=self.lab();prepare(lab,project=False);lab.client.perform('EDIT_ENTITY',dict(entity_id=entity,changes=dict(has_work=True)))
            raw,t=source(revision='next');self.error('WORK_OR_STATE_GUARD',self.plan,lab,raw,t)
        lab=self.lab();prepare(lab,project=False);lab.client.perform('EDIT_ENTITY',dict(entity_id=uid(12),changes=dict(status='ACTIVE')))
        raw,t=source(revision='next');self.error('WORK_OR_STATE_GUARD',self.plan,lab,raw,t)
    def dr13(self):
        lab=self.lab();ids=prepare(lab,apply=False);c=lab.client
        c.review('SOURCE',ids['source_manifest'],decision='REVOKE',version=1)
        self.error('REVIEW_REQUIRED',c.perform,'APPLY_BATCH',dict(manifest_id=ids['batch'],review_version=1))
        c.review('SOURCE',ids['source_manifest'],decision='ACCEPT',version=2)
        self.error('REVIEW_REQUIRED',c.perform,'APPLY_BATCH',dict(manifest_id=ids['batch'],review_version=1))
        lab=self.lab();ids=prepare(lab,apply=False)
        c=lab.client;args=self.state(lab)['manifests'][ids['batch']]
        other=c.perform('PREPARE_BATCH',dict(source_manifest=ids['source_manifest'],source_review=1,targets=list(reversed(args['targets']))))['result']['manifest_id'];c.review('BATCH',other)
        c.perform('APPLY_BATCH',dict(manifest_id=ids['batch'],review_version=1));self.assertEqual(self.state(lab)['data_generation'],1)
    def dr14(self):
        for point in ('before_object','after_object','before_replace','after_head'):
            lab=self.lab();ids=prepare(lab,apply=False)
            kill_at(lab,'mutate',dict(kind='APPLY_BATCH',args=dict(manifest_id=ids['batch'],review_version=1)),point)
            s=self.state(lab);published=point=='after_head'
            for key in ('entities','relations','mappings','bases','entity_provenance','relation_provenance'):self.assertEqual(bool(s['data'][key]),published)
            self.assertEqual(s['data_generation'],int(published));self.reprocess(lab)
    def dr15(self):
        lab=self.lab();ids=prepare(lab,project=False);before=self.state(lab)['data'];raw,t=source(revision='no-op')
        sm,bm=self.plan(lab,raw,t);lab.client.perform('APPLY_BATCH',dict(manifest_id=bm,review_version=1));after=self.state(lab)['data']
        self.assertEqual(after['entities'],before['entities'])
        for tid in before['mappings']:self.assertEqual(after['mappings'][tid]['version'],before['mappings'][tid]['version']+1)
        for tid in after['entity_provenance']:self.assertEqual(len(after['entity_provenance'][tid]),2)
        # Endpoint-only relation evidence advances provenance, not its previous source base.
        v=json.loads(raw);v['elements']=v['elements'][:2];v['revision']='endpoints';oldbase=after['mappings'][uid(12)]['source_base']
        sm,bm=self.plan(lab,canonical(v),t[:2]);lab.client.perform('APPLY_BATCH',dict(manifest_id=bm,review_version=1))
        self.assertEqual(self.state(lab)['data']['mappings'][uid(12)]['source_base'],oldbase)
    def dr16(self):
        lab=self.lab();ids=prepare(lab,apply=False);cid=uid();head=lab.client.snapshot()['head'];expected={k:head[k] for k in ('seq','commit_sha256')}
        args=dict(manifest_id=ids['batch'],review_version=1);first=lab.client.perform('APPLY_BATCH',args,cid=cid,expected=expected)
        lab.client.perform('EDIT_ENTITY',dict(entity_id=uid(12),changes=dict(title='Later local')))
        r=lab.fresh().perform('APPLY_BATCH',args,cid=cid,expected=expected);self.assertTrue(r['historical']);self.assertEqual(r['result'],first['result'])
        self.assertEqual(self.state(lab)['data']['entities'][uid(12)]['title'],'Later local')
        self.error('COMMAND_CONFLICT',lab.client.perform,'APPLY_BATCH',dict(manifest_id=ids['batch'],review_version=2),cid=cid,expected=expected)
    def dr17(self):
        lab=self.lab();ids=prepare(lab,select=False);c=lab.client;r=ids['apply']
        for tid in (uid(10),uid(11),uid(999)):
            self.error('TASK_PARTICIPANT_REQUIRED',c.perform,'SELECT_TASKS',dict(batch_command=r['command_id'],batch_request=r['request_sha256'],task_ids=[tid]))
        self.error('BATCH_RECEIPT_REQUIRED',c.perform,'SELECT_TASKS',dict(batch_command=uid(),batch_request=r['request_sha256'],task_ids=[uid(12)]))
        self.assertFalse(self.entities(lab));self.assertIsNone(self.state(lab)['selection'])
    def dr18(self):
        lab=self.lab();ids=prepare(lab);c=lab.client;mid=ids['projections'][1];c.review('PROJECTION',mid,decision='REVOKE',version=1)
        c.dispatch(ids['projections'][0],1);self.error('REVIEW_REQUIRED',c.dispatch,mid,1)
        self.assertEqual(len(self.entities(lab)),1)
        m=self.state(lab)['manifests'][ids['projections'][0]];self.assertNotIn('evaluation',m)
        self.assertEqual(m['batch_command'],ids['apply']['command_id']);self.assertEqual(m['data_hash'],self.state(lab)['selection']['data_hash'])
    def dr19(self):
        for mode in ('relation','entity','no-op'):
            lab=self.lab();ids=prepare(lab)
            if mode=='relation':lab.client.perform('ADD_RELATION',dict(relation=dict(type='TASK_DEPENDENCY',left=uid(13),right=uid(12),kind='SOFT')))
            elif mode=='entity':lab.client.perform('EDIT_ENTITY',dict(entity_id=uid(10),changes=dict(title='Other local')))
            else:
                raw,t=source(revision='again');sm,bm=self.plan(lab,raw,t);lab.client.perform('APPLY_BATCH',dict(manifest_id=bm,review_version=1))
            self.error('STALE_',lab.client.dispatch,ids['projections'][0],1);self.assertFalse(self.entities(lab))
    def dr20(self):
        for mode in ('selection','source_review','batch_review'):
            lab=self.lab();ids=prepare(lab)
            if mode=='selection':lab.client.select_source(None);lab.client.select_source(ids['source'])
            else:
                stage='SOURCE' if mode=='source_review' else 'BATCH';mid=ids['source_manifest'] if stage=='SOURCE' else ids['batch']
                lab.client.review(stage,mid,decision='REVOKE',version=1)
            self.error('STALE_|REVIEW_REQUIRED',lab.client.dispatch,ids['projections'][0],1)
        lab=self.lab();ids=prepare(lab);out=lab.client.dispatch(ids['projections'][0],1,deliver=False)
        lab.client.review('BATCH',ids['batch'],decision='REVOKE',version=1)
        lab.remote.execute(out['ticket'],self.state(lab)['manifests'][ids['projections'][0]]);lab.client.reconcile(out['send_id'])
        v=lab.client.summary()['sends'][0];self.assertEqual((v['status'],v['validity']),('EFFECT_CONFIRMED','STALE'))
    def dr21(self):
        lab=self.lab();ids=prepare(lab);a=lab.client.dispatch(ids['projections'][0],1);b=lab.client.dispatch(ids['projections'][1],1,deliver=False)
        view=lab.client.summary();by_task={v['target_id']:v['status'] for v in view['sends']}
        self.assertEqual(by_task,{ids['task_ids'][0]:'EFFECT_CONFIRMED',ids['task_ids'][1]:'UNKNOWN'})
        self.assertEqual((view['entities'],view['relations'],view['data_generation']),(4,4,1));self.assertEqual(len(self.entities(lab)),1)
        self.assertEqual(len(self.state(lab)['sends']),2)
    def dr22(self):
        from source_ingest.durable_task_fixture import remote_manifest as t_manifest
        lab=self.lab();ids=prepare(lab);m=self.state(lab)['manifests'][ids['projections'][0]]
        self.error('INVALID_SHAPE',t_manifest,m);self.assertEqual(m['schema'],PROJECTION_SCHEMA)
        key=m['creation_key'];self.assertEqual(set(m['payload']),{'name','description'});self.assertNotIn('epic_id',m['payload'])
        out=lab.client.dispatch(ids['projections'][0],1);rid=next(iter(self.entities(lab)));lab.remote.edit(rid,foreign=dict(sentinel='keep'))
        mid=lab.client.prepare_projection(ids['bindings'][0])['result']['manifest_id'];lab.client.review('PROJECTION',mid)
        self.assertEqual(self.state(lab)['manifests'][mid]['creation_key'],key);lab.client.dispatch(mid,1)
        self.assertEqual(self.entities(lab)[rid]['foreign'],dict(sentinel='keep'))
    def phase(self,lab,kind):
        ids=prepare(lab,apply=kind!='APPLY_BATCH')
        if kind=='APPLY_BATCH':return dict(kind=kind,args=dict(manifest_id=ids['batch'],review_version=1))
        r=ids['apply']
        if kind=='SELECT_TASKS':return dict(kind=kind,args=dict(batch_command=r['command_id'],batch_request=r['request_sha256'],task_ids=list(reversed(ids['task_ids']))))
        if kind=='PREPARE_PROJECTION':
            m=self.state(lab)['manifests'][ids['projections'][0]];return dict(kind=kind,args=dict(binding_id=ids['bindings'][0],remote_identity=m['remote_identity'],capabilities=m['capabilities'],remote_base=None))
        if kind=='ISSUE':
            m=self.state(lab)['manifests'][ids['projections'][0]];return dict(kind=kind,args=dict(manifest_id=ids['projections'][0],review_version=1,send_id=uid(),ticket=uid(),capabilities=m['capabilities'],retry=False))
        out=lab.client.dispatch(ids['projections'][0],1,deliver=False)
        if kind=='QUERY':return dict(kind=kind,args=dict(send_id=out['send_id'],query_id=uid(),ledger_version=1))
        proof=lab.remote.execute(out['ticket'],self.state(lab)['manifests'][ids['projections'][0]])
        return dict(kind='RESULT',args=dict(send_id=out['send_id'],ledger_version=1,proof=proof,query_id=None))
    def dr23(self):
        for kind in ('APPLY_BATCH','SELECT_TASKS','PREPARE_PROJECTION','ISSUE','QUERY','RESULT'):
            for point in ('before_object','after_object','before_replace','after_head'):
                with self.subTest(kind=kind,point=point):
                    lab=self.lab();args=self.phase(lab,kind);args['cid']=uid();before=independent(lab.root/'client');args['expected']={k:before['head'][k] for k in ('seq','commit_sha256')}
                    kill_at(lab,'mutate',args,point);after=independent(lab.root/'client');yes=point=='after_head'
                    self.assertEqual(after['head']['seq'],before['head']['seq']+int(yes));self.assertEqual(args['cid'] in after['state']['receipts'],yes)
                    self.reprocess(lab)
                    if yes:self.assertTrue(lab.fresh().perform(**args)['historical'])
                    else:self.assertEqual(before['state'],after['state'])
    def dr24(self):
        for kind in ('APPLY_BATCH','SELECT_TASKS','PREPARE_PROJECTION','ISSUE','QUERY','RESULT'):
            lab=self.lab();args=self.phase(lab,kind)
            def fault(point):
                if point=='directory_fsync':raise OSError('controlled')
            c=lab.fresh(client_hook=fault);self.error('COMMIT_UNKNOWN',c.perform,**args);self.error('RECOVERY_REQUIRED',c.snapshot)
            self.reprocess(lab)
            def recovery(point):
                if point=='recovery_fsync':raise OSError('controlled')
            self.error('COMMIT_UNKNOWN',lab.fresh(client_hook=recovery).snapshot)
    def dr25(self):
        lab=self.lab();ids=prepare(lab);sid=uid();kill_at(lab,'dispatch',dict(mid=ids['projections'][0],review_version=1,send_id=sid),'after_issue')
        self.assertEqual(self.reprocess(lab)['sends'][0]['status'],'UNKNOWN');self.assertFalse(self.entities(lab))
        lab.fresh().reconcile(sid);self.assertEqual(self.state(lab)['sends'][sid]['status'],'UNKNOWN')
    def dr26(self):
        lab=self.lab();ids=prepare(lab);sid=uid();kill_at(lab,'dispatch',dict(mid=ids['projections'][0],review_version=1,send_id=sid),'after_remote')
        self.assertEqual(len(self.entities(lab)),1);self.assertEqual(self.reprocess(lab)['sends'][0]['status'],'UNKNOWN')
        lab.fresh().reconcile(sid);self.assertEqual(self.state(lab)['sends'][sid]['status'],'EFFECT_CONFIRMED');self.assertEqual(len(self.entities(lab)),1)
        # Crash between the query response and publication also leaves the exact proof recoverable.
        kill_at(lab,'reconcile',dict(sid=sid),'before_result');lab.fresh().reconcile(sid);self.assertEqual(self.state(lab)['pending'],{})
    def dr27(self):
        for mode in ('CREATE','UPDATE','CLOSE'):
            for point in ('before_object','after_object','before_replace','after_head','fsync'):
                with self.subTest(mode=mode,point=point):
                    lab=self.lab();ids=prepare(lab);mid=ids['projections'][0]
                    if mode=='UPDATE':
                        lab.client.dispatch(mid,1);mid=lab.client.prepare_projection(ids['bindings'][0])['result']['manifest_id'];lab.client.review('PROJECTION',mid)
                    out=lab.client.dispatch(mid,1,deliver=False);m=self.state(lab)['manifests'][mid];before=independent(lab.root/'remote')
                    if point=='fsync':
                        def fault(p):
                            if p=='directory_fsync':raise OSError('controlled')
                        self.error('COMMIT_UNKNOWN',lab.fresh(remote_hook=fault).remote.execute,out['ticket'],m,close=mode=='CLOSE')
                        yes=True
                    else:kill_at(lab,'remote',dict(ticket=out['ticket'],m=m,close=mode=='CLOSE'),point,role='REMOTE');yes=point=='after_head'
                    after=independent(lab.root/'remote');self.assertEqual(after['head']['seq'],before['head']['seq']+int(yes))
                    proof=lab.fresh().remote.lookup(out['ticket'],m);self.assertEqual(proof is not None,yes)
                    lab.fresh().reconcile(out['send_id'],close=not yes)
                    self.assertNotEqual(self.state(lab)['sends'][out['send_id']]['status'],'UNKNOWN')
    def dr28(self):
        lab=self.lab();ids=prepare(lab);out=lab.client.dispatch(ids['projections'][0],1,deliver=False);m=self.state(lab)['manifests'][ids['projections'][0]]
        barrier=CONTEXT.Barrier(2);ws=[start(lab,'remote',dict(ticket=out['ticket'],m=m,close=close),barrier=barrier) for close in (True,False)];ans=[]
        for p,c in ws:ans.append(receive(p,c));self.assertEqual(finish(p,c),0)
        self.assertTrue(all(x[0]=='OK' for x in ans));self.assertEqual(ans[0][1],ans[1][1])
        self.assertEqual(len(self.entities(lab)),int(ans[0][1]['status']=='EFFECT_CONFIRMED'))
        lab=self.lab();ids=prepare(lab);out=lab.client.dispatch(ids['projections'][0],1,deliver=False);m=self.state(lab)['manifests'][ids['projections'][0]]
        lab.client.reconcile(out['send_id'],close=True);p=lab.fresh().remote.execute(out['ticket'],m)
        self.assertEqual(p['status'],'CLOSED_NO_EFFECT');self.assertFalse(self.entities(lab))
    def dr29(self):
        for key in ('store_id','run_id','ticket','creation_key','request_hash','manifest_hash','payload_hash'):
            lab=self.lab();ids=prepare(lab);out=lab.client.dispatch(ids['projections'][0],1,deliver=False);m=self.state(lab)['manifests'][ids['projections'][0]];lab.remote.execute(out['ticket'],m)
            def bad(p):p[key]='0'*64 if key.endswith('hash') or key=='creation_key' else uid();return p
            lab.client.reconcile(out['send_id'],proof_hook=bad);self.assertEqual(self.state(lab)['sends'][out['send_id']]['status'],'CONFLICT')
            lab.client.reconcile(out['send_id']);self.assertEqual(self.state(lab)['sends'][out['send_id']]['status'],'CONFLICT')
    def dr30(self):
        lab=self.lab();ids=prepare(lab);mid=ids['projections'][0];out=lab.client.dispatch(mid,1,reject='RATE_LIMIT',retry_tick=5)
        self.error('RETRY_NOT_ELIGIBLE',lab.client.dispatch,mid,1,send_id=out['send_id'],retry=True)
        lab.client.perform('CLOCK',dict(tick=5))
        for _ in range(2):lab.client.dispatch(mid,1,send_id=out['send_id'],retry=True,reject='REJECTED')
        self.error('ATTEMPT_BUDGET',lab.client.dispatch,mid,1,send_id=out['send_id'],retry=True)
        lab=self.lab();ids=prepare(lab);out=lab.client.dispatch(ids['projections'][0],1,deliver=False)
        for _ in range(6):lab.client.reconcile(out['send_id'])
        self.error('QUERY_BUDGET',lab.client.reconcile,out['send_id']);self.error('BINDING_UNRESOLVED',lab.client.dispatch,ids['projections'][0],1)
    def dr31(self):
        lab=self.lab();ids=prepare(lab,apply=False);m=self.state(lab)['manifests'][ids['batch']]
        alt=lab.client.perform('PREPARE_BATCH',dict(source_manifest=ids['source_manifest'],source_review=1,targets=list(reversed(m['targets']))))['result']['manifest_id'];lab.client.review('BATCH',alt)
        h=lab.client.snapshot()['head'];expected={k:h[k] for k in ('seq','commit_sha256')};barrier=CONTEXT.Barrier(2)
        ws=[start(lab,'mutate',dict(kind='APPLY_BATCH',args=dict(manifest_id=mid,review_version=1),expected=expected),barrier=barrier) for mid in (ids['batch'],alt)];ans=[]
        for p,c in ws:ans.append(receive(p,c));self.assertEqual(finish(p,c),0)
        self.assertEqual(sorted(x[0] for x in ans),['ERROR','OK']);self.assertIn('CONFLICT_HEAD',[x[1] for x in ans if x[0]=='ERROR'])
        self.assertEqual(self.state(lab)['data_generation'],1);self.assertEqual(len(self.state(lab)['data']['entities']),4)
    def dr32(self):
        lab=self.lab();ids=prepare(lab);out=lab.client.dispatch(ids['projections'][0],1,deliver=False);sid=out['send_id'];m=self.state(lab)['manifests'][ids['projections'][0]];proof=lab.remote.execute(out['ticket'],m)
        qid=uid();lab.client.perform('QUERY',dict(send_id=sid,query_id=qid,ledger_version=1))
        lab.client.review('PROJECTION',ids['projections'][0],decision='REVOKE',version=1);lab.client.reconcile(sid)
        self.error('CONFLICT_LEDGER',lab.client.perform,'RESULT',dict(send_id=sid,ledger_version=1,proof=proof,query_id=qid))
        v=lab.client.summary()['sends'][0];self.assertEqual((v['status'],v['validity']),('EFFECT_CONFIRMED','STALE'))
    def dr33(self):
        lab=self.lab();ids=prepare(lab);lab.client.dispatch(ids['projections'][0],1);rid=next(iter(self.entities(lab)))
        lab.remote.edit(rid,foreign=dict(sentinel='keep'));mid=lab.client.prepare_projection(ids['bindings'][0])['result']['manifest_id'];lab.client.review('PROJECTION',mid)
        before=deepcopy(self.entities(lab)[rid]['payload']);lab.remote.edit(rid,payload=dict(name='B',description=None));lab.remote.edit(rid,payload=before)
        out=lab.client.dispatch(mid,1);v=self.state(lab)['sends'][out['send_id']]
        self.assertEqual(v['status'],'NO_EFFECT');self.assertEqual(v['proof']['code'],'REMOTE_PRECONDITION');self.assertIsNone(v['retry_tick'])
        self.error('RETRY_NOT_ELIGIBLE',lab.client.dispatch,mid,1,send_id=out['send_id'],retry=True)
        self.assertEqual(self.entities(lab)[rid]['foreign'],dict(sentinel='keep'))
    def dr34(self):
        lab=self.lab();ids=prepare(lab);out=lab.client.dispatch(ids['projections'][0],1,deliver=False)
        raw,t=source(revision='next');v=json.loads(raw);v['elements'][2]['title']='Next TASK';sm,bm=self.plan(lab,canonical(v),t)
        r=lab.client.perform('APPLY_BATCH',dict(manifest_id=bm,review_version=1))
        lab.client.perform('SELECT_TASKS',dict(batch_command=r['command_id'],batch_request=r['request_sha256'],task_ids=[uid(12)]))
        waiting=lab.client.prepare_projection(ids['bindings'][0])['result']['manifest_id'];lab.client.review('PROJECTION',waiting)
        self.error('BINDING_UNRESOLVED',lab.client.dispatch,waiting,1)
        lab.remote.execute(out['ticket'],self.state(lab)['manifests'][ids['projections'][0]]);lab.client.reconcile(out['send_id'])
        self.assertEqual(lab.client.summary()['sends'][0]['validity'],'STALE')
        self.error('STALE_DESTINATION',lab.client.dispatch,waiting,1)
        self.assertEqual(self.state(lab)['data']['entities'][uid(12)]['title'],'Next TASK')
        lab.client.perform('SELECT_TASKS',dict(batch_command=r['command_id'],batch_request=r['request_sha256'],task_ids=[uid(12)]))
        pm=lab.client.prepare_projection(ids['bindings'][0])['result']['manifest_id'];lab.client.review('PROJECTION',pm)
        lab.client.dispatch(pm,1);self.assertEqual(next(iter(self.entities(lab).values()))['payload']['name'],'Next TASK')
    def dr35(self):
        from source_ingest.durable_task_fixture import Client as TClient,Remote as TRemote
        for mode in ('head','object','marker','symlink'):
            lab=self.lab();prepare(lab);path=lab.root/'client';h=json.loads((path/'head.json').read_bytes());marker=(path/'marker.json').read_bytes()
            if mode=='head':(path/'head.json').write_bytes(b'{}')
            elif mode=='object':(path/'objects'/(h['commit_sha256']+'.json')).unlink()
            elif mode=='marker':(path/'marker.json').write_bytes(b'{}')
            else:(path/'head.json').unlink();(path/'head.json').symlink_to(lab.sentinel)
            try:self.error('SHAPE|STORE_|CORRUPT',lab.fresh().snapshot)
            finally:
                (path/'marker.json').write_bytes(marker)
                if (path/'head.json').is_symlink():(path/'head.json').unlink()
        lab=self.lab();prepare(lab);t=TClient(lab.root/'client',lab.run_id,lab.client_id,None,TRemote(lab.root/'remote',lab.run_id,lab.remote_id))
        self.error('INVALID_SHAPE',t.snapshot)
    def assert_relational_equivalence(self,old,lab):
        left=old.inspect()['data'];right=self.state(lab)['data']
        for group in ('entity_provenance','relation_provenance'):
            for values in left[group].values():
                for row in values:
                    self.assertEqual(old.manifest(row['manifest_sha256'])['source_id'],row['source_sha256'])
                    row['manifest_sha256']='OWN_SCHEMA_MANIFEST'
            for values in right[group].values():
                for row in values:
                    self.assertEqual(self.state(lab)['manifests'][row['manifest_sha256']]['source_id'],row['source_sha256'])
                    row['manifest_sha256']='OWN_SCHEMA_MANIFEST'
        self.assertEqual(left,right)

    def dr36(self):
        # Same positive/negative inputs, only public I30 methods and inspect results.
        for scenario in ('normal','no-op','cycle','mapping','local'):
            lab=self.lab();raw,t=source();old=BatchLab(uid(1));sid=old.capture(raw);old.review('SOURCE',sid,expected_version=0,decision='ACCEPT',reason='fixture')
            mid=old.prepare(sid,t,source_review_version=1);old.review('BATCH',mid,expected_version=0,decision='ACCEPT',reason='fixture');old.apply(uid(),mid,batch_review_version=1,data_generation=0)
            ids=prepare(lab,raw,t,project=False)
            self.assert_relational_equivalence(old,lab)
            if scenario in ('normal','no-op'):
                raw2,t2=source(revision='again');sm,bm=self.plan(lab,raw2,t2)
                ss=old.capture(raw2);old.review('SOURCE',ss,expected_version=0,decision='ACCEPT',reason='fixture');mm=old.prepare(ss,t2,source_review_version=1);old.review('BATCH',mm,expected_version=0,decision='ACCEPT',reason='fixture')
                old.apply(uid(),mm,batch_review_version=1,data_generation=1);lab.client.perform('APPLY_BATCH',dict(manifest_id=bm,review_version=1))
                self.assert_relational_equivalence(old,lab)
            else:
                value=json.loads(raw);value['revision']='negative'
                if scenario=='cycle':value['relations'].append(declaration('BACK','TASK_DEPENDENCY',reference(uid(1),uid(2),'T1','TASK'),reference(uid(1),uid(2),'T0','TASK'),kind='HARD'))
                if scenario=='mapping':t[2]['target_id']=uid(999)
                if scenario=='local':old.fixture_edit_entity(uid(12),dict(title='Local'));lab.client.perform('EDIT_ENTITY',dict(entity_id=uid(12),changes=dict(title='Local')))
                rr=canonical(value);ss=old.capture(rr);old.review('SOURCE',ss,expected_version=0,decision='ACCEPT',reason='fixture')
                with self.assertRaises((BatchError,DurableError)) as a:old.prepare(ss,t,source_review_version=1)
                with self.assertRaises((BatchError,DurableError)) as b:self.plan(lab,rr,t)
                self.assertEqual(str(a.exception),str(b.exception))
    def dr37(self):
        for limits,code in [(dict(LIMITS,commands=2),'COMMAND_BUDGET'),(dict(LIMITS,commits=3),'HISTORY_HEADROOM'),(dict(LIMITS,commit_bytes=4096),'COMMIT_BUDGET'),(dict(LIMITS,store_bytes=16384),'STORE_HEADROOM')]:
            lab=self.lab(limits=limits)
            for tick in range(1,20):
                before=self.state(lab)
                try:lab.client.perform('CLOCK',dict(tick=tick))
                except DurableError as ex:self.assertEqual(str(ex),code);self.assertEqual(self.state(lab),before);break
            else:self.fail('Boundary not reached')
        for key in ('elements','declarations','sources','manifests','reviews','selected','bindings','entities','relations','remote_tasks','tickets','batch_bytes','projection_bytes'):
            lab=self.lab();ids=prepare(lab);s=deepcopy(self.state(lab));s['config']['bounds'][key]=1
            if key=='bindings':s['bindings'].pop(ids['bindings'][0])
            if key in ('elements','declarations'):self.error('BUDGET',client_reduce,s,'CAPTURE',dict(content_base64=base64.b64encode(ids['raw']).decode()))
            elif key=='sources':
                raw,t=source(revision='extra');self.error('BUDGET',client_reduce,s,'CAPTURE',dict(content_base64=base64.b64encode(raw).decode()))
            elif key=='reviews':self.error('BUDGET',client_reduce,s,'REVIEW',dict(stage='SOURCE',manifest_id=ids['source_manifest'],expected_version=1,decision='REVOKE',reason_code='fixture'))
            elif key=='selected':r=ids['apply'];self.error('INVALID_TASK_SELECTION',client_reduce,s,'SELECT_TASKS',dict(batch_command=r['command_id'],batch_request=r['request_sha256'],task_ids=ids['task_ids']))
            elif key=='bindings':self.error('BINDING_BUDGET',client_reduce,s,'BIND',dict(binding_id=uid(),target_id=ids['task_ids'][0]))
            elif key in ('entities','relations'):self.error('STATE_BUDGET',plan_batch,s['data'],validate_source(ids['raw']),ids['targets'],bounds=s['config']['bounds'])
            elif key in ('batch_bytes','manifests'):
                self.error('MANIFEST_BUDGET',client_reduce,s,'PREPARE_BATCH',dict(source_manifest=ids['source_manifest'],source_review=1,targets=ids['targets']))
            elif key=='projection_bytes':
                m=s['manifests'][ids['projections'][0]];self.error('MANIFEST_BUDGET',client_reduce,s,'PREPARE_PROJECTION',dict(binding_id=ids['bindings'][0],remote_identity=m['remote_identity'],capabilities=m['capabilities'],remote_base=None))
            elif key=='remote_tasks':
                for mid in ids['projections']:lab.client.dispatch(mid,1)
                rs=independent(lab.root/'remote')['state'];rs['config']['bounds']['remote_tasks']=1
                # Budget branch on a new explicit creation identity, no existing destination adoption.
                m=deepcopy(self.state(lab)['manifests'][ids['projections'][0]]);m['target_id']=uid(999);m['task']['id']=uid(999);m['binding']['target_id']=uid(999)
                from source_ingest.durable_relational_fixture import creation_key
                m['creation_key']=creation_key(lab.config,uid(999));m['selection']['task_ids']=[uid(999)]
                self.error('REMOTE_TASK_BUDGET',remote_reduce,rs,'EXECUTE',dict(ticket=uid(),manifest=m,run_id=lab.run_id,store_id=lab.remote_id,reject=None,retry_tick=0))
            else:
                lab.client.dispatch(ids['projections'][0],1);rs=independent(lab.root/'remote')['state'];rs['config']['bounds']['tickets']=1
                self.error('TICKET_BUDGET',remote_reduce,rs,'EXECUTE',dict(ticket=uid(),manifest=self.state(lab)['manifests'][ids['projections'][0]],run_id=lab.run_id,store_id=lab.remote_id,reject=None,retry_tick=0))
        for limits,code in [(dict(LIMITS,commit_bytes=65536),'COMMIT_BUDGET'),(dict(LIMITS,store_bytes=2097152),'STORE_HEADROOM')]:
            lab=self.lab(limits=limits);ids=prepare(lab);before=self.state(lab);self.error(code,lab.client.dispatch,ids['projections'][0],1);self.assertEqual(self.state(lab),before)
        lab=self.lab();self.error('SOURCE_BUDGET',lab.client.capture,b'x'*(2097152+1))
    def dr38(self):
        lab=self.lab();ids=prepare(lab);head=lab.client.snapshot()['head'];expected={k:head[k] for k in ('seq','commit_sha256')}
        owner,oc=start(lab,'mutate',dict(kind='CLOCK',args=dict(tick=1),expected=expected),point='before_object');waiter=wc=None
        try:
            self.assertEqual(receive(owner,oc),('READY','before_object'));barrier=CONTEXT.Barrier(2)
            waiter,wc=start(lab,'raw_mutate',dict(cid=uid(),kind='CLOCK',args=dict(tick=2),expected=expected),point='before_lock',barrier=barrier)
            self.assertEqual(receive(waiter,wc),('READY','before_lock'));barrier.wait(timeout=15);owner.kill();self.assertEqual(finish(owner,oc),-signal.SIGKILL)
            self.assertEqual(receive(waiter,wc)[0],'OK');self.assertEqual(finish(waiter,wc),0)
        finally:
            for p,c in ((owner,oc),(waiter,wc)):
                if p is not None and p.is_alive():p.kill();finish(p,c)
        self.assertEqual(self.reprocess(lab)['clock_tick'],2)
        marker=lab.root/'client/marker.json';original=marker.read_bytes();marker.write_bytes(b'{}')
        try:self.error('CLEANUP_MARKER',lab.close)
        finally:marker.write_bytes(original)
        link=lab.root/'client/link';link.symlink_to(lab.sentinel)
        try:self.error('CLEANUP_SYMLINK',lab.close)
        finally:link.unlink()
        root=lab.home;lab.close();self.assertFalse(root.exists());self.assertTrue(all(not p.is_alive() for p in support.CHILDREN))
    def dr39(self):
        lab=self.lab()
        with patch('socket.socket',side_effect=AssertionError('NO_NETWORK')),patch('subprocess.Popen',side_effect=AssertionError('NO_PROVIDER_CLI')):
            ids=prepare(lab);lab.client.dispatch(ids['projections'][0],1)
        out=lab.client.summary()
        for k in ('remote_requests','persistent_D2_writes','operations','operational_attempts','quota_consumed','reservations_created'):self.assertEqual(out[k],0)
        self.assertFalse(out['activation_allowed']);self.assertFalse(out['grants_execution_authority'])
        text=json.dumps(out);self.assertNotIn('Synthetic task',text);self.assertNotIn('content_base64',text);self.assertNotIn(str(lab.home),text)
    def dr40(self):
        from testing.D5.run_relational_durable_lab import coverage,distinct_groups
        self.assertEqual(len(coverage()),40)
        grouped=distinct_groups(['test_durable_relational.A.x','test_durable_integration.B.y','test_durable_relational.A.x'])
        self.assertEqual(sum(len(v) for v in grouped.values()),2)
        lab=self.lab();ids=prepare(lab);self.assertFalse(lab.client.summary()['D5_closed']);self.assertEqual(len(lab.client.summary()['global_gaps_open']),7)


for _n in range(1,41):setattr(DurableRelationalTest,f'test_DR{_n:02}',getattr(DurableRelationalTest,f'dr{_n:02}'))
