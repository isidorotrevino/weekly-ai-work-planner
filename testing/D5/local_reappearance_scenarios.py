# SPDX-License-Identifier: GPL-3.0-only
"""LR01-LR36: approved I17; joint identity and whole text resolution on reappearance."""
import concurrent.futures
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from .adoption_scenarios import Adoption
from .mapping_scenarios import body
from .postgres_scenarios import uid
from source_ingest.local_reappearance import ENTRIES, LocalReappearanceClient, local_reappearance_sql
from source_ingest.postgres import sql_text, submit_sql
from source_ingest.task_mapping import mapping_sql


class LocalReappearance(Adoption):
    def setUp(self):
        super().setUp()
        self.xwriter=LocalReappearanceClient(self.lab.container,'d5_writer')
        self.xreviewer=LocalReappearanceClient(self.lab.container,'d5_reviewer')
        self.xreader=LocalReappearanceClient(self.lab.container)
        self.xapplier=LocalReappearanceClient(self.lab.container,'d5_applier')

    def xsend(self,req):
        return {'d5_writer':self.xwriter,'d5_reviewer':self.xreviewer,'d5_applier':self.xapplier}[ENTRIES[req['action']][1]].submit_local_reappearance(req)

    def setup_return(self,present=None,after=None,key='PT-01',origin='bootstrap',when='after',edit=True):
        self.key=key;present=present or body(key=key)
        if origin=='adoption':
            self.ainitial(present,key,title='Local' if edit and when=='before' else 'Title');_,p=self.apropose();_,pkg=self.apackage(p);self.assertEqual(self.aapply(pkg)[1]['status'],'OK')
        elif origin=='mapping':
            self.stage(body('Old',key=key),present);self.intent(key);_,p=self.propose(key);_,pkg=self.package(p);self.assertEqual(self.apply(pkg)[1]['status'],'OK')
        else:
            self.initial(present,key);_,p=self.bpropose(key);_,pkg=self.bpackage(p);self.assertEqual(self.bapply(pkg)[1]['status'],'OK')
        if edit and when=='before':self.local()
        self.absent(present,key=key)
        if edit and when=='during':self.local()
        self.returned(after or body('Remote',key=key))
        if edit and when=='after':self.local()

    def xrequest(self,**extra):
        version=int(self.scalar(f"SELECT version FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';"))
        req=self.command('PREPARE_LOCAL_REAPPEARANCE_TASK',intent_id=self.iid,comparison_id=self.cid,report_sha256=self.digest,
            row_sha256=self.items.get(self.key,{}).get('row_sha256','0'*64),expected_reference_version=self.refv,
            expected_mapping_version=version,absence_application_command_id=self.abs_aid,absence_proposal_id=self.abs_pid,
            identity_declaration='SAME_SOURCE_ENTITY',identity_reason='Synthetic explicit continuity of source entity',choice='USE_SOURCE',reason='Synthetic review of complete source versus local result')
        return dict(req,**extra)

    def xpropose(self,accept_source=True,**extra):
        if accept_source:self.decide(self.key)
        req=self.xrequest(**extra);return req,self.xsend(req)

    def xaccept(self,p,version=0,decision='ACCEPT'):
        req=self.command('REVIEW_LOCAL_REAPPEARANCE_TASK',proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],
            expected_version=version,decision=decision,reviewer_label='synthetic-reviewer',reason='Review whole projection choice and source evidence')
        return req,self.xsend(req)

    def xpackage(self,*proposals,accept=True):
        pins=[]
        for p in proposals:
            if accept:
                _,r=self.xaccept(p)
                pin=dict(proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],review_command_id=r['command_id'],review_version=r['version_at_commit'])
            else:
                data=self.xreader.artifact(self.pid,self.doc,'proposal',p['proposal_id'])
                pin={k:data[k] for k in ('proposal_id','manifest_sha256','review_command_id','review_version')}
                pin['review_command_id']=pin['review_command_id'] or uid()
            pins.append(pin)
        req=self.command('PACKAGE_LOCAL_REAPPEARANCE_TASKS',items=sorted(pins,key=lambda p:p['proposal_id']))
        return req,self.xsend(req)

    def xapply(self,pkg):
        req=self.command('APPLY_LOCAL_REAPPEARANCE_TASKS',package_sha256=pkg['package_sha256'])
        count=self.scalar('SELECT count(*) FROM public.tasks;');r=self.xsend(req)
        self.assertEqual(self.scalar('SELECT count(*) FROM public.tasks;'),count)
        return req,r

    def test_LR01_owned_origins_prepare_no_writes(self):
        for n,origin in enumerate(('bootstrap','mapping','adoption'),1):
            self.tid,self.tkey=uid(),uid();self.setup_return(origin=origin,key=f'PT-{n:02}',when='before')
            old=self.lab.protected_state();req,p=self.xpropose()
            self.assertEqual(p['status'],'OK');self.assertEqual(self.xsend(req),p);self.assertEqual(self.lab.protected_state(),old)
            self.assertEqual(p['manifest']['before_projection']['title'],'Title');self.assertEqual(p['manifest']['local_projection']['title'],'Local')
        # A previously reviewed I14 KEEP_LOCAL effect remains a genuine divergent source basis.
        self.tid,self.tkey=uid(),uid();self.setup_change(key='PT-04');_,p=self.lpropose(choice='KEEP_LOCAL');_,pkg=self.lpackage(p);self.lapply(pkg)
        self.absent(body('Remote',key='PT-04'));self.returned(body('Reappeared',key='PT-04'))
        _,p=self.xpropose();self.assertEqual(p['manifest']['before_projection']['title'],'Remote')

    def test_LR02_scope_and_materialized_identity(self):
        self.setup_return();self.decide();req=self.xrequest()
        for extra in (dict(intent_id=uid()),dict(project_id=uid()),dict(document_id=uid())):
            self.assertEqual(self.xwriter.query(local_reappearance_sql(dict(req,command_id=uid(),**extra)))['code'],'INTENT_SCOPE_CONFLICT')
        self.lab.sql(f"UPDATE public.tasks SET task_key='changed' WHERE id='{self.tid}';")
        self.assertEqual(self.xpropose(False)[1]['code'],'TARGET_IDENTITY_CONFLICT')
        for field in ('profile','policy'):
            self.denied(f"UPDATE d5.task_intents SET {field}='other' WHERE intent_id='{self.iid}';",'d5_lab_admin')
        self.tid,self.tkey=uid(),uid();self.intent('PT-02');self.key='PT-02';self.absent(body(key=self.key));self.returned()
        self.decide(self.key);req=self.xrequest()
        with self.assertRaises(ValueError):self.xsend(req)
        self.assertEqual(self.xwriter.query(local_reappearance_sql(req))['code'],'MAPPING_VERSION_CONFLICT')

    def test_LR03_no_divergence_uses_I12(self):
        self.setup_return(edit=False);self.assertEqual(self.xpropose()[1]['code'],'NO_LOCAL_EDIT')
        _,p=self.rpropose(False);_,pkg=self.rpackage(p);self.assertEqual(self.rapply(pkg)[1]['status'],'OK')

    def test_LR04_divergence_any_time_snapshot_current(self):
        for n,(when,origin) in enumerate([('before','adoption'),('before','bootstrap'),('during','bootstrap'),('after','bootstrap')],1):
            self.tid,self.tkey=uid(),uid();self.setup_return(key=f'PT-{n:02}',when=when,origin=origin)
            for bump in (False,True):
                self.local('Current reviewed',bump=bump);_,p=self.xpropose(accept_source=not bump)
                self.assertEqual(p['manifest']['target'],self.task())
                self.assertEqual(p['manifest']['absence_proof']['absence_manifest']['target'],self.abs_p['manifest']['target'])
                if when!='before':self.assertNotEqual(p['manifest']['target']['title'],self.abs_p['manifest']['target']['title'])

    def test_LR05_applied_proof_required(self):
        self.setup_return();self.decide();req=self.xrequest()
        for extra in (dict(absence_application_command_id=uid()),dict(absence_proposal_id=uid()),dict(absence_application_command_id=self.abs_pid)):
            bad=dict(req,command_id=uid(),**extra)
            with self.assertRaises(ValueError):self.xsend(bad)
            self.assertEqual(self.xwriter.query(local_reappearance_sql(bad))['code'],'APPLIED_ABSENCE_REQUIRED')
        # Exercise original historical chain validation, including accepted but unapplied and CONFLICT receipts.
        self.setUp();self.test_RP04_absence_observation_accept_simulation_insufficient()
        self.setUp();self.test_RP05_proof_scope_and_incoherent_receipt()

    def test_LR06_absence_head_version_exact(self):
        self.setup_return();old_a,old_p=self.abs_aid,self.abs_pid
        self.absent();self.returned();self.decide()
        self.assertEqual(self.xpropose(False,absence_application_command_id=old_a,absence_proposal_id=old_p)[1]['code'],'ABSENCE_VERSION_CONFLICT')
        self.assertEqual(self.xpropose(False)[1]['status'],'OK')

    def test_LR07_historical_before_not_head_basis(self):
        self.bcreate();self.local();self.absent(body('Unapplied historical text'));self.returned(body('Remote'))
        _,p=self.xpropose();m=p['manifest']
        self.assertEqual(m['before_projection']['title'],'Title');self.assertEqual(m['last_applied_basis']['fields']['item'],'Title')
        self.assertEqual(m['absence_proof']['absence_manifest']['before_basis']['fields']['item'],'Unapplied historical text')
        _,pkg=self.xpackage(p);self.assertEqual(self.xapply(pkg)[1]['status'],'OK')

    def test_LR08_different_current_absent_snapshot(self):
        self.setup_return();self.returned(body('Remote'),before=b'\n\n'+body('Other changed',key='PT-99'))
        _,p=self.xpropose();m=p['manifest']
        self.assertNotEqual(m['before_observation_id'],m['absence_proof']['absence_observation_id'])
        _,pkg=self.xpackage(p);self.assertEqual(self.xapply(pkg)[1]['status'],'OK')

    def test_LR09_only_nonblocked_ADDED(self):
        self.setup_return()
        for before,after in [(body(),body('Changed')),(body(),body()),(self.missing,self.missing),(body(),self.missing)]:
            self.stage(before,after);self.assertEqual(self.xpropose(False)[1]['code'],'REAPPEARANCE_ROW_REQUIRED')
        for before,after in [(self.missing,body('Remote')+b'| PT-01 | dup | x | x | - | OPEN | no | inert |\n'),
                             (self.missing+b'| PT-99 | dup | x | x | - | OPEN | no | inert |\n',body('Remote'))]:
            self.stage(before,after);self.assertEqual(self.xpropose(False)[1]['code'],'COMPARISON_SCOPE_CONFLICT')

    def test_LR10_identity_both_choices(self):
        self.setup_return();self.decide()
        for choice in ('USE_SOURCE','KEEP_LOCAL'):
            for declaration in ('DIFFERENT_ENTITY','UNCONFIRMED',''):
                self.assertEqual(self.xpropose(False,choice=choice,identity_declaration=declaration)[1]['code'],'IDENTITY_DECLARATION_REQUIRED')
            self.assertEqual(self.xpropose(False,choice=choice)[1]['status'],'OK')

    def test_LR11_separate_reason_validation(self):
        self.setup_return();self.decide()
        for choice in ('USE_SOURCE','KEEP_LOCAL'):
            for field in ('identity_reason','reason'):
                for value in ('',' \u00a0 ','x\n','x'*1025):
                    r=self.xpropose(False,choice=choice,**{field:value})[1]
                    self.assertEqual(r['status'],'CONFLICT')
                for value in (None,{},1):
                    self.denied(local_reappearance_sql(self.xrequest(choice=choice,**{field:value})))
        self.assertEqual(self.xpropose(False,identity_reason='á'*1024,reason='Reason  ✓')[1]['status'],'OK')

    def test_LR12_I5_ACCEPT_separate_current(self):
        self.setup_return();self.assertEqual(self.xpropose(False)[1]['code'],'SOURCE_NOT_ACCEPTED')
        _,p=self.xpropose();_,pkg=self.xpackage(p)
        self.decide(decision='REJECT',version=1);self.decide(version=2)
        self.assertEqual(self.xapply(pkg)[1]['code'],'SOURCE_REVIEW_CONFLICT')

    def test_LR13_reference_CAS_ABA(self):
        self.setup_return();self.assertEqual(self.xpropose(expected_reference_version=self.refv+1)[1]['code'],'REFERENCE_VERSION_CONFLICT')
        _,p=self.xpropose(False);_,pkg=self.xpackage(p)
        self.writer.submit(self.select(self.after,self.refv));self.writer.submit(self.select(self.before,self.refv+1))
        self.assertEqual(self.xapply(pkg)[1]['code'],'REFERENCE_VERSION_CONFLICT')

    def test_LR14_own_complete_review_only(self):
        self.setup_return();_,p=self.xpropose();self.assertEqual(self.xpackage(p,accept=False)[1]['code'],'MANIFEST_NOT_ACCEPTED')
        req=self.command('REVIEW_REAPPEARANCE_TASK',proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],expected_version=0,decision='ACCEPT',reviewer_label='fixture',reason='wrong domain')
        from source_ingest.reappearance import reappearance_sql
        from source_ingest.local_edit import local_edit_sql
        self.assertEqual(self.rreviewer.query(reappearance_sql(req))['code'],'MANIFEST_SCOPE_CONFLICT')
        self.assertEqual(self.lreviewer.query(local_edit_sql(dict(req,command_id=uid(),action='REVIEW_LOCAL_EDIT_TASK')))['code'],'MANIFEST_SCOPE_CONFLICT')
        _,different=self.xpropose(False,choice='KEEP_LOCAL');self.xaccept(different)
        self.assertEqual(self.xpackage(p,accept=False)[1]['code'],'MANIFEST_NOT_ACCEPTED')
        _,pkg=self.xpackage(p);self.assertEqual(self.xapply(pkg)[1]['status'],'OK')

    def test_LR15_manifest_immutability_and_reconstruction(self):
        self.setup_return();_,p=self.xpropose();_,pkg=self.xpackage(p)
        self.denied(f"UPDATE d5.local_reappearance_proposals SET manifest=manifest||'{{\"choice\":\"KEEP_LOCAL\"}}' WHERE proposal_id='{p['proposal_id']}';",'d5_lab_admin')
        original=self.xreader.artifact;data=original(self.pid,self.doc,'proposal',p['proposal_id'])
        for field,value in [('choice','KEEP_LOCAL'),('identity_declaration','DIFFERENT_ENTITY'),('after_projection',{}),('absence_proof',{}),('target',{})]:
            altered=copy.deepcopy(data);altered['manifest'][field]=value
            self.xreader.artifact=lambda *args:altered
            with self.assertRaises((ValueError,KeyError)):self.xreader.verify_manifest(self.pid,self.doc,p['proposal_id'],p['manifest_sha256'])
        self.xreader.artifact=original
        req=self.xrequest();self.denied(local_reappearance_sql(dict(req,force=True)))
        self.denied(local_reappearance_sql(dict(req,result_projection={'title':'manual'})))
        self.assertEqual(self.xapply(pkg)[1]['status'],'OK')

    def test_LR16_own_review_version_reject_ABA(self):
        self.setup_return();_,p=self.xpropose();self.xaccept(p,decision='REJECT')
        self.assertEqual(self.xpackage(p,accept=False)[1]['code'],'MANIFEST_NOT_ACCEPTED')
        self.xaccept(p,1);_,pkg=self.xpackage(p,accept=False);self.xaccept(p,2,'REJECT');self.xaccept(p,3)
        self.assertEqual(self.xapply(pkg)[1]['code'],'LOCAL_REAPPEARANCE_REVIEW_CONFLICT')
        _,fresh=self.xpackage(p,accept=False);self.assertEqual(self.xapply(fresh)[1]['status'],'OK')

    def test_LR17_literal_ID_and_evidence(self):
        key='LONG-'+'1'*5000;text='Árbol **raw** \\| `literal`'
        self.setup_return(key=key,after=body(text,'ñ [x](https://example.invalid)',annotation=' source claim',key=key,struck=True))
        _,p=self.xpropose();_,pkg=self.xpackage(p);self.assertEqual(self.xapply(pkg)[1]['status'],'OK')
        self.assertEqual(self.task()['title'],text);self.assertEqual(p['manifest']['intent']['source_key'],key)
        self.assertTrue(p['manifest']['source_change']['after']['row']['source_struck'])

    def test_LR18_projection_validity_NULL_and_inert_claims(self):
        self.setup_return(after=body(' \u00a0 '));self.assertEqual(self.xpropose(choice='KEEP_LOCAL')[1]['code'],'INVALID_PROJECTION')
        self.returned(body('Remote'));self.local(' \u00a0 ');self.assertEqual(self.xpropose()[1]['code'],'INVALID_PROJECTION')
        self.local(description=None);old=self.task();_,p=self.xpropose(False,choice='KEEP_LOCAL');_,pkg=self.xpackage(p)
        self.assertIsNone(p['manifest']['result_projection']['description']);self.assertEqual(self.xapply(pkg)[1]['status'],'OK');self.assertEqual(self.task(),old)
        for n,description in enumerate(('','-'),2):
            self.tid,self.tkey=uid(),uid();self.setup_return(key=f'PT-{n:02}',after=body('Remote',description,key=f'PT-{n:02}',status='DONE',annotation=' verified approved'))
            _,p=self.xpropose();_,pkg=self.xpackage(p);self.assertEqual(self.xapply(pkg)[1]['status'],'OK')
            self.assertEqual(self.task()['description'],description);self.assertEqual(self.task()['status'],'BACKLOG')

    def test_LR19_USE_SOURCE_PATCH_fields_once(self):
        self.setup_return();self.lab.sql(f"UPDATE public.tasks SET urgency=3,deferred_count=2 WHERE id='{self.tid}';");old=self.task()
        _,p=self.xpropose();_,pkg=self.xpackage(p);_,r=self.xapply(pkg);new=self.task()
        self.assertEqual(p['manifest']['action'],'PATCH_LOCAL_REAPPEARANCE_USE_SOURCE');self.assertTrue(r['effects'][0]['writes_task'])
        self.assertEqual(new['row_version'],old['row_version']+1);self.assertEqual(new['title'],'Remote')
        self.assertEqual({k:v for k,v in old.items() if k not in ('title','description','row_version')},{k:v for k,v in new.items() if k not in ('title','description','row_version')})
        self.assertEqual(r['effects'][0]['absence_proof'],p['manifest']['absence_proof'])

    def no_update(self,pkg):
        req=self.command('APPLY_LOCAL_REAPPEARANCE_TASKS',package_sha256=pkg['package_sha256']);old=self.task()
        sql="""BEGIN;CREATE FUNCTION pg_temp.no_local_reappearance_update() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'unexpected task UPDATE'; END $$;
        CREATE TRIGGER no_local_reappearance_update BEFORE UPDATE ON public.tasks FOR EACH ROW EXECUTE FUNCTION pg_temp.no_local_reappearance_update();"""
        r=json.loads(self.lab.sql(sql+local_reappearance_sql(req)+'ROLLBACK;').stdout.strip())
        self.assertEqual(self.task(),old)
        self.assertEqual(self.xsend(req)['status'],'OK')
        self.assertEqual(r['status'],'OK');self.assertFalse(r['effects'][0]['writes_task']);self.assertEqual(self.task(),old)
        return r

    def test_LR20_USE_SOURCE_convergence_no_UPDATE(self):
        self.setup_return(after=body('Local'));_,p=self.xpropose();_,pkg=self.xpackage(p);self.no_update(pkg)
        self.assertEqual(p['manifest']['action'],'LINK_LOCAL_REAPPEARANCE_EVIDENCE')

    def test_LR21_KEEP_LOCAL_all_source_relations_no_UPDATE(self):
        for n,title in enumerate(('Remote','Local','Title'),1):
            self.tid,self.tkey=uid(),uid();self.setup_return(key=f'PT-{n:02}',after=body(title,key=f'PT-{n:02}'))
            _,p=self.xpropose(choice='KEEP_LOCAL');_,pkg=self.xpackage(p);self.no_update(pkg)
            self.assertEqual(p['manifest']['action'],'KEEP_LOCAL_REAPPEARANCE')
            self.assertEqual(self.scalar(f"SELECT projection->>'title' FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';"),title)
            self.assertEqual(self.scalar(f"SELECT version FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';"),'3')

    def test_LR22_source_equals_base_both_choices(self):
        for n,choice in enumerate(('USE_SOURCE','KEEP_LOCAL'),1):
            self.tid,self.tkey=uid(),uid();self.setup_return(key=f'PT-{n:02}',after=body(key=f'PT-{n:02}'))
            _,p=self.xpropose(choice=choice);_,pkg=self.xpackage(p);self.assertEqual(self.xapply(pkg)[1]['status'],'OK')
            self.assertEqual(self.task()['title'],'Title' if choice=='USE_SOURCE' else 'Local')

    def test_LR23_target_CAS_late_edits_and_ABA(self):
        self.setup_return();_,p=self.xpropose();_,pkg=self.xpackage(p);self.local('Unreviewed')
        self.assertEqual(self.xapply(pkg)[1]['code'],'RESOLUTION_CONTENT_CONFLICT')
        self.local();self.lab.sql(f"UPDATE public.tasks SET urgency=4 WHERE id='{self.tid}';")
        self.assertEqual(self.xapply(pkg)[1]['code'],'TARGET_CAS_CONFLICT')
        _,p=self.xpropose(False);_,pkg=self.xpackage(p);self.local('Other',bump=True);self.local(bump=True)
        self.assertEqual(self.xapply(pkg)[1]['code'],'TARGET_CAS_CONFLICT')
        self.local('Title');self.assertEqual(self.xapply(pkg)[1]['code'],'NO_LOCAL_EDIT')

    def test_LR24_state_and_historical_work_block_all_choices(self):
        self.setup_return();self.decide()
        fixtures=[f"SELECT d2.transition('{uid()}','{json.dumps(dict(entity_type='TASK',entity_id=self.tid,expected_version=0,actor='fixture',reason='negative test',to='BLOCKED',**{'from':'BACKLOG'}))}');",
                  f"INSERT INTO public.operations(task_id,operation_type,idempotency_key) VALUES('{self.tid}','SYNTHETIC','{uid()}');"]
        plan=uid();fixtures.append(self.plan_fixture(plan)+f"INSERT INTO public.schedule_entries(planning_run_id,task_id,resource_id,pool,priority_snapshot,state) VALUES('{plan}','{self.tid}','{self.lab.resource}','PLANNED','{{}}','CANCELLED');")
        for choice in ('USE_SOURCE','KEEP_LOCAL'):
            _,p=self.xpropose(False,choice=choice);_,pkg=self.xpackage(p)
            for fixture in fixtures:
                for statement in (local_reappearance_sql(self.xrequest(choice=choice)),local_reappearance_sql(self.command('APPLY_LOCAL_REAPPEARANCE_TASKS',package_sha256=pkg['package_sha256']))):
                    r=self.lab.sql('BEGIN;'+fixture+statement+'ROLLBACK;');self.assertEqual(json.loads(r.stdout.splitlines()[-1])['code'],'TARGET_HAS_WORK_OR_STATE')
        self.assertEqual(self.scalar('SELECT count(*) FROM public.operations;'),'0')

    def test_LR25_explicit_package_limits_and_variant_isolation(self):
        self.setup_return();_,p=self.xpropose();_,p2=self.xpropose(False,choice='KEEP_LOCAL');_,r2=self.xaccept(p2);req,pkg=self.xpackage(p)
        self.assertEqual(self.xsend(dict(req,command_id=uid()))['package_sha256'],pkg['package_sha256'])
        for items in ([],req['items']*2,req['items']*2001):self.denied(local_reappearance_sql(dict(req,command_id=uid(),items=items)))
        pin=dict(proposal_id=p2['proposal_id'],manifest_sha256=p2['manifest_sha256'],review_command_id=r2['command_id'],review_version=1)
        self.denied(local_reappearance_sql(dict(req,command_id=uid(),items=sorted(req['items']+[pin],key=lambda x:x['proposal_id']))))
        from source_ingest.bootstrap import bootstrap_sql
        from source_ingest.reappearance import reappearance_sql
        from source_ingest.local_edit import local_edit_sql
        from source_ingest.adoption import adoption_sql
        for client,sql,action in [(self.mapper,mapping_sql,'PACKAGE_TASK_PROPOSALS'),(self.bwriter,bootstrap_sql,'PACKAGE_BOOTSTRAP_TASKS'),(self.rwriter,reappearance_sql,'PACKAGE_REAPPEARANCE_TASKS'),(self.lwriter,local_edit_sql,'PACKAGE_LOCAL_EDIT_TASKS'),(self.awriter,adoption_sql,'PACKAGE_ADOPTION_TASKS')]:
            self.assertEqual(client.query(sql(dict(req,command_id=uid(),action=action)))['code'],'MANIFEST_SCOPE_CONFLICT')
    def test_LR26_concurrent_packages_and_new_absence(self):
        self.setup_return();_,p=self.xpropose();_,p2=self.xpropose(False,choice='KEEP_LOCAL');_,pkg=self.xpackage(p);_,pkg2=self.xpackage(p2)
        requests=[self.command('APPLY_LOCAL_REAPPEARANCE_TASKS',package_sha256=x['package_sha256']) for x in (pkg,pkg2)]
        results=self.lab.concurrent([local_reappearance_sql(r) for r in requests],role='d5_applier')
        self.assertEqual(sorted(r['status'] for r in results),['CONFLICT','OK'])
        self.assertEqual(self.scalar(f"SELECT version FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';"),'3')
        self.tid,self.tkey=uid(),uid();self.setup_return(key='PT-02');_,p=self.xpropose();_,pkg=self.xpackage(p)
        apply=self.command('APPLY_LOCAL_REAPPEARANCE_TASKS',package_sha256=pkg['package_sha256'])
        self.absent(body('Remote',key=self.key));self.assertEqual(self.xapplier.query(local_reappearance_sql(apply))['code'],'MAPPING_VERSION_CONFLICT')

    def test_LR27_review_and_reference_change_while_waiting(self):
        self.setup_return();_,p=self.xpropose();_,pkg=self.xpackage(p);req=self.command('APPLY_LOCAL_REAPPEARANCE_TASKS',package_sha256=pkg['package_sha256'])
        results=self.lab.concurrent([local_reappearance_sql(req),submit_sql(self.select(self.after,self.refv))],role='d5_lab_admin')
        self.assertEqual(results[1]['status'],'OK');self.assertIn(results[0]['status'],('OK','CONFLICT'))
        if results[0]['status']=='CONFLICT':self.assertEqual(results[0]['code'],'REFERENCE_VERSION_CONFLICT')
        self.tid,self.tkey=uid(),uid();self.setup_return(key='PT-02');_,p=self.xpropose();_,pkg=self.xpackage(p)
        req=self.command('APPLY_LOCAL_REAPPEARANCE_TASKS',package_sha256=pkg['package_sha256'])
        review=self.command('REVIEW_LOCAL_REAPPEARANCE_TASK',proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],expected_version=1,decision='REJECT',reviewer_label='fixture',reason='Concurrent revoke')
        results=self.lab.concurrent([local_reappearance_sql(req),local_reappearance_sql(review)],role='d5_lab_admin')
        self.assertEqual(results[1]['status'],'OK');self.assertIn(results[0]['status'],('OK','CONFLICT'))
        if results[0]['status']=='CONFLICT':self.assertEqual(results[0]['code'],'LOCAL_REAPPEARANCE_REVIEW_CONFLICT')

    def test_LR28_batch_atomicity_abort_and_late_failure(self):
        present=body()+b'| PT-02 | Second | x | x | - | OPEN | no | inert |\n'
        after=body('Remote')+b'| PT-02 | Second new | x | x | - | OPEN | no | inert |\n'
        self.initial(present);i1=self.iid;t1=self.tid;other=uid();self.intent('PT-02',other,uid());i2=self.iid
        _,b1=self.bpropose(iid=i1);_,b2=self.bpropose('PT-02',i2);_,bpkg=self.bpackage(b1,b2);self.bapply(bpkg)
        self.stage(present,body(key='PT-99'));_,a1=self.propose('PT-01',i1);_,a2=self.propose('PT-02',i2);_,apkg=self.package(a1,a2);a_req,r=self.apply(apkg);self.assertEqual(r['status'],'OK')
        self.stage(body(key='PT-99'),after);self.abs_aid=a_req['command_id'];self.iid=i1;self.tid=t1;self.key='PT-01';self.abs_pid=a1['proposal_id'];self.local();_,p1=self.xpropose()
        self.iid=i2;self.tid=other;self.key='PT-02';self.abs_pid=a2['proposal_id'];self.local('Local second');_,p2=self.xpropose(choice='KEEP_LOCAL');_,pkg=self.xpackage(p1,p2)
        self.lab.sql(f"UPDATE public.tasks SET urgency=2 WHERE id='{other}';");before=self.resolution_state()
        self.assertEqual(self.xapply(pkg)[1]['code'],'TARGET_CAS_CONFLICT');self.assertEqual(self.resolution_state(),before)
        self.lab.sql(f"UPDATE public.tasks SET urgency=0 WHERE id='{other}';");before=self.resolution_state()
        req=self.command('APPLY_LOCAL_REAPPEARANCE_TASKS',package_sha256=pkg['package_sha256']);self.lab.abort_after(local_reappearance_sql(req))
        self.assertEqual(self.resolution_state(),before);self.assertIsNone(self.reader.read_command(req['command_id']))
        fault="""BEGIN;CREATE FUNCTION pg_temp.local_reappearance_fault() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic failure after local reappearance effects'; END $$;
        CREATE TRIGGER local_reappearance_fault BEFORE INSERT ON d5.local_reappearance_applications FOR EACH ROW EXECUTE FUNCTION pg_temp.local_reappearance_fault();"""
        error=self.denied(fault+local_reappearance_sql(req)+'COMMIT;',role='d5_lab_admin');self.assertIn('synthetic failure after local reappearance effects',error)
        self.assertEqual(self.resolution_state(),before);self.assertIsNone(self.reader.read_command(req['command_id']))
        self.assertEqual(self.scalar(f"SELECT bool_and(version=2) FROM d5.task_mapping_heads WHERE intent_id IN ('{i1}','{i2}');"),'t')
        old=self.task();self.assertEqual(self.xapply(pkg)[1]['status'],'OK');self.assertEqual(self.task(),old);self.assertEqual(self.task(t1)['title'],'Remote')

    def test_LR29_replay_global_command_and_ALREADY_APPLIED(self):
        self.setup_return();_,p=self.xpropose();_,pkg=self.xpackage(p);req,r=self.xapply(pkg);self.local('Later',bump=True)
        self.assertEqual(self.xsend(req),r);self.assertEqual(self.xsend(dict(req,command_id=uid()))['status'],'ALREADY_APPLIED');self.assertEqual(self.task()['title'],'Later')
        self.assertEqual(self.xapplier.query(local_reappearance_sql(dict(req,package_sha256='0'*64)))['code'],'COMMAND_CONTENT_CONFLICT')
        self.assertEqual(self.applier.query(mapping_sql(dict(req,action='APPLY_TASK_PROPOSALS')))['code'],'COMMAND_CONTENT_CONFLICT')

    def test_LR30_lost_response_restart_CLI(self):
        self.setup_return();_,p=self.xpropose();_,pkg=self.xpackage(p);req=self.command('APPLY_LOCAL_REAPPEARANCE_TASKS',package_sha256=pkg['package_sha256'])
        self.lab.sql(local_reappearance_sql(req),role='d5_applier');self.lab.restart();r=self.reader.read_command(req['command_id']);self.assertEqual(self.xsend(req),r)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'request.json';path.write_text(json.dumps(req))
            run=subprocess.run([sys.executable,'-m','source_ingest.local_reappearance','--container',self.lab.container,'--request',str(path)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr);self.assertEqual(json.loads(run.stdout),r)
            path.write_text('{"action":"x","action":"y"}')
            run=subprocess.run([sys.executable,'-m','source_ingest.local_reappearance','--container',self.lab.container,'--request',str(path)],capture_output=True,text=True)
            self.assertEqual(run.returncode,1)
        self.assertEqual(self.task()['row_version'],1)

    def test_LR31_provenance_reuse_append_only_and_scope(self):
        self.setup_return();_,p=self.xpropose(choice='KEEP_LOCAL');m=p['manifest'];locator=m['source_change']['after']['row']['source_locator']
        self.lab.sql(f"INSERT INTO d2.task_sources VALUES('{self.tid}','{m['after_revision_id']}',{sql_text(locator)},'{self.doc}','{self.pid}');")
        before=self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}';")
        _,pkg=self.xpackage(p);self.assertEqual(self.xapply(pkg)[1]['status'],'OK');self.assertEqual(self.task()['title'],'Local')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}';"),before)
        self.denied(f"UPDATE d2.task_sources SET source_locator='forged' WHERE task_id='{self.tid}';",'d5_lab_admin')
        self.assertIsNone(self.xreader.artifact(uid(),self.doc,'proposal',p['proposal_id']))
        self.assertIsNone(self.xreader.artifact(self.pid,uid(),'package',pkg['package_sha256']))
        self.assertEqual(self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}' AND revision_id='{m['after_revision_id']}' AND source_locator={sql_text(locator)};"),'1')

    def test_LR32_future_I8_and_I14_continuity(self):
        for n,(choice,title) in enumerate([('USE_SOURCE','Remote'),('KEEP_LOCAL','Local'),('KEEP_LOCAL','Remote')],1):
            self.tid,self.tkey=uid(),uid();self.setup_return(key=f'PT-{n:02}',after=body(title,key=f'PT-{n:02}'));_,p=self.xpropose(choice=choice);_,pkg=self.xpackage(p);self.xapply(pkg)
            self.stage(body(title,key=self.key),body('Next',key=self.key))
            if choice=='KEEP_LOCAL' and title!='Local':
                self.assertEqual(self.propose(self.key)[1]['code'],'LOCAL_EDIT_CONFLICT')
                _,p=self.lpropose(False,choice='KEEP_LOCAL');_,pkg=self.lpackage(p);self.assertEqual(self.lapply(pkg)[1]['status'],'OK');self.assertEqual(self.task()['title'],'Local')
            else:
                _,p=self.propose(self.key);_,pkg=self.package(p);self.assertEqual(self.apply(pkg)[1]['status'],'OK');self.assertEqual(self.task()['title'],'Next')

    def test_LR33_new_cycle_new_proof_and_historical_review(self):
        self.setup_return();_,p=self.xpropose(choice='KEEP_LOCAL');_,pkg=self.xpackage(p)
        # Revoking the old absence review does not revoke a confirmed historical application.
        self.accept(self.abs_p,version=1,decision='REJECT');req,r=self.xapply(pkg);self.assertEqual(r['status'],'OK')
        old_a,old_p=self.abs_aid,self.abs_pid;self.absent(body('Remote'));self.returned(body('Again'))
        self.assertEqual(self.xpropose(absence_application_command_id=old_a,absence_proposal_id=old_p)[1]['code'],'ABSENCE_VERSION_CONFLICT')
        _,p=self.xpropose(False,choice='KEEP_LOCAL');self.assertEqual(self.xpackage(p,accept=False)[1]['code'],'MANIFEST_NOT_ACCEPTED')
        _,pkg=self.xpackage(p);self.assertEqual(self.xapply(pkg)[1]['status'],'OK');self.assertEqual(self.task()['title'],'Local');self.assertEqual(self.xsend(req),r)

    def test_LR34_old_routes_remain_closed(self):
        self.setup_return();self.assertEqual(self.rpropose()[1]['code'],'LOCAL_EDIT_CONFLICT')
        self.assertEqual(self.lpropose(False)[1]['code'],'PRESENT_CHANGED_ROW_REQUIRED')
        self.assertEqual(self.propose()[1]['code'],'REAPPEARANCE_REVIEW_REQUIRED')
        _,p=self.xpropose(False);_,pkg=self.xpackage(p);self.assertEqual(self.xapply(pkg)[1]['status'],'OK')
        self.lab.assert_previous_functions();self.lab.assert_local_previous_functions();self.lab.assert_adoption_previous_functions();self.lab.assert_local_reappearance_previous_functions()

    def test_LR35_locks_roles_D3_capture_and_snapshot(self):
        self.setup_return();_,p=self.xpropose();_,pkg=self.xpackage(p);req=self.command('APPLY_LOCAL_REAPPEARANCE_TASKS',package_sha256=pkg['package_sha256'])
        for role in ('d5_writer','d5_reviewer','d5_reader'):self.denied(local_reappearance_sql(req),role)
        for role in ('d5_writer','d5_reviewer','d5_reader','d5_applier'):
            self.denied('UPDATE public.tasks SET urgency=0;',role);self.denied('SELECT d5.task_lock_boundary();',role)
            self.denied('SELECT * FROM d5.local_reappearance_proposals;',role)
        self.denied('SELECT d3.lock_state();','d5_applier');self.denied('BEGIN ISOLATION LEVEL REPEATABLE READ;'+local_reappearance_sql(req),'d5_applier')
        blocker=self.lab.session('BEGIN;SELECT pg_advisory_xact_lock(742001);SELECT pg_sleep(60);ROLLBACK;','local_reappearance_boundary')
        self.lab.wait_for(lambda:self.lab.active('local_reappearance_boundary','PgSleep')==1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(self.lab.sql,local_reappearance_sql(req),'d5_applier')
                self.lab.wait_for(lambda:int(self.scalar("SELECT count(*) FROM pg_stat_activity WHERE usename='d5_applier' AND wait_event='advisory';"))==1)
                self.assertEqual(self.writer.submit(self.select(self.before,self.refv))['status'],'OK')
                self.lab.terminate('local_reappearance_boundary');self.assertEqual(json.loads(future.result(timeout=30).stdout)['code'],'REFERENCE_VERSION_CONFLICT')
        finally:self.lab.terminate('local_reappearance_boundary');blocker.communicate(timeout=5)
        blocker=self.lab.session('BEGIN;SELECT pg_advisory_xact_lock(742005);SELECT pg_sleep(60);ROLLBACK;','local_reappearance_boundary')
        self.lab.wait_for(lambda:self.lab.active('local_reappearance_boundary','PgSleep')==1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(self.lab.sql,local_reappearance_sql(dict(req,command_id=uid())),'d5_applier')
                self.lab.wait_for(lambda:int(self.scalar("SELECT count(*) FROM pg_stat_activity WHERE usename='d5_applier' AND wait_event='advisory';"))==1)
                self.assertEqual(self.scalar("SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a ON a.pid=l.pid WHERE a.usename='d5_applier' AND l.locktype='advisory' AND l.granted AND l.objid IN (742001,742002);"),'2')
                cid=uid();capture=self.lab.session(f"SELECT d3.capture('{cid}','{{\"action\":\"CAPTURE\"}}');",'local_reappearance_capture')
                self.lab.wait_for(lambda:self.lab.active('local_reappearance_capture','advisory')==1)
                self.lab.terminate('local_reappearance_boundary');future.result(timeout=30);out,error=capture.communicate(timeout=10)
                self.assertEqual(capture.returncode,0,error);self.assertEqual(json.loads(out)['capture_id'],cid)
        finally:self.lab.terminate('local_reappearance_boundary');blocker.communicate(timeout=5)
        self.refv=self.head()['version'];_,p=self.xpropose(False);_,pkg=self.xpackage(p)
        plan=uid();self.lab.sql(self.plan_fixture(plan,True));old=self.scalar(f"SELECT to_jsonb(p) FROM public.planning_runs p WHERE id='{plan}';")
        before=self.scalar("SELECT encode(public.digest(d3.state_body()::text,'sha256'),'hex');");self.assertEqual(self.xapply(pkg)[1]['status'],'OK')
        self.assertNotEqual(before,self.scalar("SELECT encode(public.digest(d3.state_body()::text,'sha256'),'hex');"));self.assertEqual(self.scalar(f"SELECT to_jsonb(p) FROM public.planning_runs p WHERE id='{plan}';"),old)
        self.denied(f"UPDATE public.planning_runs SET solver_version='changed' WHERE id='{plan}';",'d5_lab_admin')
        # Evidence-only variants leave tasks byte-for-byte unchanged (LR20/LR21).

    def test_LR36_final_no_activation_and_catalog(self):
        self.setup_return();before=self.scalar('SELECT count(*) FROM public.tasks;');_,p=self.xpropose();_,pkg=self.xpackage(p);self.assertEqual(self.xapply(pkg)[1]['status'],'OK')
        self.assertEqual(self.scalar('SELECT count(*) FROM public.tasks;'),before);self.assertEqual(self.task()['status'],'BACKLOG')
        for table in ('public.operations','public.outbox_events','public.execution_attempts','d2.reservations','d2.plan_reservations','d4.deliveries'):
            self.assertEqual(self.scalar('SELECT count(*) FROM '+table+';'),'0')
        self.assertEqual(self.lab.catalog(),self.lab.v30_catalog);self.lab.assert_local_reappearance_previous_functions()
