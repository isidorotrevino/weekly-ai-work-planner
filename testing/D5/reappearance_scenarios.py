# SPDX-License-Identifier: GPL-3.0-only
"""RP01-RP30 implement the I11 R01-R30 matrix without activating work."""
import concurrent.futures
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from .bootstrap_scenarios import Bootstrap
from .mapping_scenarios import body
from .postgres_scenarios import uid
from source_ingest.postgres import sql_text, submit_sql
from source_ingest.reappearance import ENTRIES, ReappearanceClient, reappearance_sql


class Reappearance(Bootstrap):
    def setUp(self):
        super().setUp()
        self.rwriter=ReappearanceClient(self.lab.container,'d5_writer')
        self.rreviewer=ReappearanceClient(self.lab.container,'d5_reviewer')
        self.rreader=ReappearanceClient(self.lab.container)
        self.rapplier=ReappearanceClient(self.lab.container,'d5_applier')
        self.key='PT-01'

    def rsend(self,req):
        return {'d5_writer':self.rwriter,'d5_reviewer':self.rreviewer,'d5_applier':self.rapplier}[ENTRIES[req['action']][1]].submit_reappearance(req)

    def absent(self,present=None,missing=None,key=None):
        self.key=key or self.key;self.missing=missing or body(key='PT-99')
        self.stage(present or body(),self.missing)
        _,p=self.propose(self.key);_,pkg=self.package(p);req,r=self.apply(pkg)
        self.assertEqual(r['status'],'OK')
        self.abs_p,self.abs_req,self.abs_result=p,req,r
        self.abs_aid,self.abs_pid=req['command_id'],p['proposal_id']
        return r

    def returned(self,data=None,before=None):
        self.stage(before or self.missing,data or body('Returned',key=self.key))

    def cycle(self,present=None,returning=None,key='PT-01',bootstrap=True,create=True,local_edit=False):
        self.key=key;present=present or body(key=key)
        if create:
            if bootstrap:
                self.initial(present,key=key);_,p=self.bpropose(key);_,pkg=self.bpackage(p);self.assertEqual(self.bapply(pkg)[1]['status'],'OK')
            else:
                self.stage(body('Old',key=key),present);self.intent(key)
                _,p=self.propose(key);_,pkg=self.package(p);self.assertEqual(self.apply(pkg)[1]['status'],'OK')
        if local_edit:self.lab.sql(f"UPDATE public.tasks SET title='Local' WHERE id='{self.tid}';")
        self.absent(present,key=key);self.returned(returning)

    def rrequest(self,**extra):
        version=int(self.scalar(f"SELECT version FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';"))
        req=self.command('PREPARE_REAPPEARANCE_TASK',intent_id=self.iid,comparison_id=self.cid,report_sha256=self.digest,
            row_sha256=self.items.get(self.key,{}).get('row_sha256','0'*64),expected_reference_version=self.refv,expected_mapping_version=version,
            absence_application_command_id=self.abs_aid,absence_proposal_id=self.abs_pid,
            identity_declaration='SAME_SOURCE_ENTITY',identity_reason='Synthetic continuity declaration for complete row and existing task')
        return dict(req,**extra)

    def rpropose(self,accept_source=True,**extra):
        if accept_source:self.decide(self.key)
        req=self.rrequest(**extra)
        return req,self.rsend(req)

    def raccept(self,p,version=0,decision='ACCEPT'):
        req=self.command('REVIEW_REAPPEARANCE_TASK',proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],
                         expected_version=version,decision=decision,reviewer_label='synthetic-reviewer',reason='Review source continuity, proof and whole effect')
        return req,self.rsend(req)

    def rpackage(self,*proposals,accept=True):
        pins=[]
        for p in proposals:
            if accept:
                _,r=self.raccept(p)
                pin=dict(proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],review_command_id=r['command_id'],review_version=r['version_at_commit'])
            else:
                data=self.rreader.artifact(self.pid,self.doc,'proposal',p['proposal_id'])
                pin={k:data[k] for k in ('proposal_id','manifest_sha256','review_command_id','review_version')}
                pin['review_command_id']=pin['review_command_id'] or uid()
            pins.append(pin)
        req=self.command('PACKAGE_REAPPEARANCE_TASKS',items=sorted(pins,key=lambda p:p['proposal_id']))
        return req,self.rsend(req)

    def rapply(self,pkg):
        req=self.command('APPLY_REAPPEARANCE_TASKS',package_sha256=pkg['package_sha256'])
        count=self.scalar('SELECT count(*) FROM public.tasks;');r=self.rsend(req)
        self.assertEqual(self.scalar('SELECT count(*) FROM public.tasks;'),count)
        return req,r

    def test_RP01_prepare_I8_and_bootstrap_destinations(self):
        for bootstrap in (True,False):
            if not bootstrap:
                self.tid,self.tkey=uid(),uid();self.key='PT-02'
            self.cycle(key=self.key,bootstrap=bootstrap)
            before=self.lab.protected_state();req,p=self.rpropose()
            self.assertEqual(p['status'],'OK');self.assertEqual(self.rsend(req),p);self.assertEqual(self.lab.protected_state(),before)
            self.assertEqual(p['manifest']['absence_proof']['application_command_id'],self.abs_aid)
            self.assertEqual(p['manifest']['mapping_version'],2)

    def test_RP02_identity_scope_and_target_key(self):
        self.cycle();self.decide();req=self.rrequest()
        for extra in (dict(intent_id=uid()),dict(project_id=uid()),dict(document_id=uid())):
            r=self.rwriter.query(reappearance_sql(dict(req,command_id=uid(),**extra)));self.assertEqual(r['code'],'INTENT_SCOPE_CONFLICT')
        self.lab.sql(f"UPDATE public.tasks SET task_key='locally-changed' WHERE id='{self.tid}';")
        self.assertEqual(self.rpropose(False)[1]['code'],'TARGET_IDENTITY_CONFLICT')

    def test_RP03_explicit_identity_and_reason(self):
        self.cycle();self.decide()
        for extra in (dict(identity_declaration='DIFFERENT_ENTITY'),dict(identity_declaration='UNCONFIRMED'),dict(identity_reason=''),dict(identity_reason=' \u00a0 ')):
            self.assertEqual(self.rpropose(False,**extra)[1]['code'],'IDENTITY_DECLARATION_REQUIRED')
        self.assertEqual(self.rpropose(False)[1]['status'],'OK')

    def test_RP04_absence_observation_accept_simulation_insufficient(self):
        self.bcreate();self.key='PT-01';self.missing=body(key='PT-99')
        self.stage(body(),self.missing);_,abs_p=self.propose();_,sim=self.decide(version=1)
        self.assertEqual(self.simulate([self.pin(self.key,sim)],self.refv)['status'],'OK')
        _,pkg=self.package(abs_p)  # accepted, deliberately not applied
        self.abs_aid,self.abs_pid=uid(),abs_p['proposal_id'];self.returned();self.decide()
        req=self.rrequest()
        with self.assertRaises(ValueError):self.rsend(req)
        self.assertEqual(self.rwriter.query(reappearance_sql(req))['code'],'APPLIED_ABSENCE_REQUIRED')
        # A confirmed absence without any materialized task is also insufficient.
        self.tid,self.tkey=uid(),uid();self.intent('PT-02');self.key='PT-02'
        self.absent(body(key=self.key),key=self.key);self.returned();self.decide(self.key)
        self.assertEqual(self.rwriter.query(reappearance_sql(self.rrequest()))['code'],'MAPPING_VERSION_CONFLICT')

    def test_RP05_proof_scope_and_incoherent_receipt(self):
        self.cycle();self.decide();req=self.rrequest()
        for extra in (dict(absence_application_command_id=uid()),dict(absence_proposal_id=uid()),dict(absence_application_command_id=self.abs_pid)):
            self.assertEqual(self.rwriter.query(reappearance_sql(dict(req,command_id=uid(),**extra)))['code'],'APPLIED_ABSENCE_REQUIRED')
        self.assertIsNone(self.rreader.query(f"SELECT d5.read_reappearance_absence('{uid()}','{self.doc}','{self.abs_aid}','{self.abs_pid}');"))
        # Owner-only inconsistent journal fixture is rolled back, never exposed as proof.
        fake=uid()
        sql=f"""BEGIN;
        WITH v AS (SELECT d5.task_hash('d5.task-package.v1',jsonb_build_object('project_id','{self.pid}','document_id','{self.doc}','items','[]'::jsonb)) sha)
        INSERT INTO d5.task_packages SELECT sha,'{self.pid}','{self.doc}','[]' FROM v;
        INSERT INTO d5.commands(command_id,request,request_sha256,response)
        SELECT '{fake}',q,encode(public.digest('d5.source-command.v1:'||q::text,'sha256'),'hex'),'{{"status":"CONFLICT"}}'
        FROM (SELECT request||jsonb_build_object('command_id','{fake}') q FROM d5.commands WHERE command_id='{self.abs_aid}') s;
        INSERT INTO d5.task_applications(package_sha256,command_id,result)
        SELECT d5.task_hash('d5.task-package.v1',jsonb_build_object('project_id','{self.pid}','document_id','{self.doc}','items','[]'::jsonb)),'{fake}','{{"status":"CONFLICT"}}';
        SELECT coalesce(d5.read_reappearance_absence('{self.pid}','{self.doc}','{fake}','{self.abs_pid}'),'null'::jsonb);ROLLBACK;"""
        self.assertIsNone(json.loads(self.lab.sql(sql).stdout.strip()))

    def test_RP06_absence_version_is_exact_not_latest_date(self):
        self.cycle();old_a,old_p=self.abs_aid,self.abs_pid
        self.absent();self.returned();self.decide()
        self.assertEqual(self.rpropose(False,absence_application_command_id=old_a,absence_proposal_id=old_p)[1]['code'],'ABSENCE_VERSION_CONFLICT')
        self.assertEqual(self.rpropose(False)[1]['status'],'OK')

    def test_RP07_historical_before_is_not_applied_basis(self):
        self.bcreate();self.absent(body('Historical unrelated title'));self.returned()
        _,p=self.rpropose();m=p['manifest']
        self.assertEqual(m['last_applied_basis']['fields']['item'],'Title')
        self.assertEqual(m['absence_proof']['absence_manifest']['before_basis']['fields']['item'],'Historical unrelated title')
        _,pkg=self.rpackage(p);self.assertEqual(self.rapply(pkg)[1]['status'],'OK');self.assertEqual(self.task()['title'],'Returned')

    def test_RP08_different_absent_before_observation(self):
        self.cycle();self.returned(before=b'\n\n'+body('Other row changed',key='PT-99'))
        _,p=self.rpropose();m=p['manifest']
        self.assertNotEqual(m['before_observation_id'],m['absence_proof']['absence_observation_id'])
        _,pkg=self.rpackage(p);self.assertEqual(self.rapply(pkg)[1]['status'],'OK')

    def test_RP09_only_unblocked_ADDED_absent_to_present(self):
        self.cycle()
        for b,a in [(body(),body('Changed')),(body(),body()),(self.missing,self.missing)]:
            self.stage(b,a);self.assertEqual(self.rpropose(False)[1]['code'],'REAPPEARANCE_ROW_REQUIRED')
        self.stage(self.missing,body('Returned')+b'| PT-01 | duplicate | x | x | - | OPEN | no | inert |\n')
        self.assertEqual(self.rpropose(False)[1]['code'],'COMPARISON_SCOPE_CONFLICT')

    def test_RP10_source_ACCEPT_and_ABA(self):
        self.cycle();self.assertEqual(self.rpropose(False)[1]['code'],'SOURCE_NOT_ACCEPTED')
        _,p=self.rpropose();_,pkg=self.rpackage(p)
        self.decide(decision='REJECT',version=1);self.decide(version=2)
        self.assertEqual(self.rapply(pkg)[1]['code'],'SOURCE_REVIEW_CONFLICT')
        _,fresh=self.rpropose(False);_,pkg=self.rpackage(fresh);self.assertEqual(self.rapply(pkg)[1]['status'],'OK')

    def test_RP11_reference_and_ABA(self):
        self.cycle();_,p=self.rpropose();_,pkg=self.rpackage(p)
        self.writer.submit(self.select(self.after,self.refv));self.assertEqual(self.rapply(pkg)[1]['code'],'REFERENCE_VERSION_CONFLICT')
        self.writer.submit(self.select(self.before,self.refv+1));self.assertEqual(self.rapply(pkg)[1]['code'],'REFERENCE_VERSION_CONFLICT')

    def test_RP12_long_ID_literal_unicode_and_annotation(self):
        key='LONG-'+'1'*5000;text='Árbol **raw** \\| `literal`'
        self.cycle(key=key,returning=body(text,'ñ [x](https://example.invalid)',annotation=' source claim',key=key,struck=True))
        _,p=self.rpropose();_,pkg=self.rpackage(p);self.assertEqual(self.rapply(pkg)[1]['status'],'OK')
        self.assertEqual(self.task()['title'],text);self.assertEqual(p['manifest']['intent']['source_key'],key)
        self.assertTrue(p['manifest']['source_change']['after']['row']['source_struck'])

    def test_RP13_projection_validation_and_inert_source_claims(self):
        self.cycle(returning=body('   '));self.assertEqual(self.rpropose()[1]['code'],'INVALID_PROJECTION')
        self.returned(body('Returned','-',status='DONE',annotation=' approved'));_,dash=self.rpropose()
        self.assertEqual(dash['manifest']['after_projection']['description'],'-')
        self.returned(body('Returned','',status='DONE',annotation=' approved'));_,p=self.rpropose();_,pkg=self.rpackage(p)
        self.assertEqual(self.rapply(pkg)[1]['status'],'OK');self.assertEqual(self.task()['description'],'');self.assertEqual(self.task()['status'],'BACKLOG')

    def test_RP14_PATCH_only_mapped_fields_and_one_version(self):
        self.cycle();self.lab.sql(f"UPDATE public.tasks SET urgency=3,deferred_count=2 WHERE id='{self.tid}';");old=self.task()
        _,p=self.rpropose();_,pkg=self.rpackage(p);self.assertEqual(self.rapply(pkg)[1]['status'],'OK');new=self.task()
        self.assertEqual(p['manifest']['action'],'PATCH_REAPPEARED_BACKLOG');self.assertEqual(new['row_version'],old['row_version']+1)
        self.assertEqual({k:v for k,v in old.items() if k not in ('title','description','row_version')},{k:v for k,v in new.items() if k not in ('title','description','row_version')})
        self.assertEqual(new['title'],'Returned')

    def test_RP15_evidence_only_preserves_whole_task(self):
        self.cycle(returning=body(status='DONE',annotation=' source claim'));old=self.task()
        _,p=self.rpropose();self.assertEqual(p['manifest']['action'],'LINK_REAPPEARANCE_EVIDENCE');_,pkg=self.rpackage(p)
        self.assertEqual(self.rapply(pkg)[1]['status'],'OK');self.assertEqual(self.task(),old)
        self.assertEqual(self.scalar(f"SELECT version FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';"),'3')

    def test_RP16_local_edit_during_absence_and_fresh_prepare(self):
        self.cycle(local_edit=True);self.assertEqual(self.rpropose()[1]['code'],'LOCAL_EDIT_CONFLICT')
        self.lab.sql(f"UPDATE public.tasks SET title='Title' WHERE id='{self.tid}';")
        _,p=self.rpropose(False);_,pkg=self.rpackage(p)
        for version in ('row_version','row_version+1'):
            self.lab.sql(f"UPDATE public.tasks SET title='Local',row_version={version} WHERE id='{self.tid}';")
            self.assertEqual(self.rapply(pkg)[1]['code'],'LOCAL_EDIT_CONFLICT')
            self.assertEqual(self.rpropose(False)[1]['code'],'LOCAL_EDIT_CONFLICT')

    def test_RP17_full_CAS_and_identity_change(self):
        self.cycle();_,p=self.rpropose();_,pkg=self.rpackage(p)
        self.lab.sql(f"UPDATE public.tasks SET urgency=4 WHERE id='{self.tid}';")
        self.assertEqual(self.rapply(pkg)[1]['code'],'TARGET_CAS_CONFLICT')
        _,fresh=self.rpropose(False);_,pkg=self.rpackage(fresh)
        self.lab.sql(f"UPDATE public.tasks SET task_key='local-key' WHERE id='{self.tid}';")
        self.assertEqual(self.rapply(pkg)[1]['code'],'TARGET_IDENTITY_CONFLICT')

    def test_RP18_state_operations_and_historical_schedule(self):
        self.cycle();_,p=self.rpropose();_,pkg=self.rpackage(p);req=self.command('APPLY_REAPPEARANCE_TASKS',package_sha256=pkg['package_sha256'])
        fixtures=[f"SELECT d2.transition('{uid()}','{json.dumps(dict(entity_type='TASK',entity_id=self.tid,expected_version=0,actor='fixture',reason='negative test',to='BLOCKED',**{'from':'BACKLOG'}))}');",
                  f"INSERT INTO public.operations(task_id,operation_type,idempotency_key) VALUES('{self.tid}','SYNTHETIC','{uid()}');"]
        plan=uid();fixtures.append(self.plan_fixture(plan)+f"INSERT INTO public.schedule_entries(planning_run_id,task_id,resource_id,pool,priority_snapshot,state) VALUES('{plan}','{self.tid}','{self.lab.resource}','PLANNED','{{}}','CANCELLED');")
        for fixture in fixtures:
            r=self.lab.sql('BEGIN;'+fixture+'SET LOCAL ROLE d5_applier;'+reappearance_sql(dict(req,command_id=uid()))+'ROLLBACK;',check=False)
            self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(json.loads(r.stdout.splitlines()[-1])['code'],'TARGET_HAS_WORK_OR_STATE')
        self.assertEqual(self.scalar('SELECT count(*) FROM public.operations;'),'0')

    def test_RP19_manifest_and_acceptance_not_transferable(self):
        self.cycle();_,p=self.rpropose();req,r=self.raccept(p)
        bad=dict(req,command_id=uid(),manifest_sha256='0'*64,expected_version=1)
        with self.assertRaises(ValueError):self.rsend(bad)
        self.assertEqual(self.rreviewer.query(reappearance_sql(bad))['code'],'MANIFEST_SCOPE_CONFLICT')
        for key in ('identity_reason','identity_declaration','absence_application_command_id','task_id','policy'):
            self.denied(reappearance_sql(dict(req,command_id=uid(),**{key:'changed'})),role='d5_reviewer')
        self.denied("UPDATE d5.reappearance_proposals SET manifest=manifest||'{\"mode\":\"CREATE\"}';",role='d5_lab_admin')

    def test_RP20_review_is_separate_and_versioned(self):
        self.cycle();_,p=self.rpropose();self.assertEqual(self.rpackage(p,accept=False)[1]['code'],'MANIFEST_NOT_ACCEPTED')
        _,pkg=self.rpackage(p);self.raccept(p,1,'REJECT');self.raccept(p,2,'ACCEPT')
        self.assertEqual(self.rapply(pkg)[1]['code'],'REAPPEARANCE_REVIEW_CONFLICT')
        _,new=self.rpackage(p,accept=False);self.assertEqual(self.rapply(new)[1]['status'],'OK')

    def test_RP21_package_explicit_limits_and_variant_isolation(self):
        self.cycle();_,p=self.rpropose();_,p2=self.rpropose(False);_,r2=self.raccept(p2);req,pkg=self.rpackage(p)
        self.assertEqual(self.rsend(dict(req,command_id=uid()))['package_sha256'],pkg['package_sha256'])
        for items in ([],req['items']*2,req['items']*2001):self.denied(reappearance_sql(dict(req,command_id=uid(),items=items)))
        pin=dict(proposal_id=p2['proposal_id'],manifest_sha256=p2['manifest_sha256'],review_command_id=r2['command_id'],review_version=1)
        self.denied(reappearance_sql(dict(req,command_id=uid(),items=sorted(req['items']+[pin],key=lambda x:x['proposal_id']))))
        from source_ingest.task_mapping import mapping_sql
        self.assertEqual(self.mapper.query(mapping_sql(dict(req,command_id=uid(),action='PACKAGE_TASK_PROPOSALS')))['code'],'MANIFEST_SCOPE_CONFLICT')

    def test_RP22_replay_and_global_commands(self):
        self.cycle();_,p=self.rpropose();_,pkg=self.rpackage(p);req,r=self.rapply(pkg)
        self.lab.sql(f"UPDATE public.tasks SET urgency=2 WHERE id='{self.tid}';")
        self.assertEqual(self.rsend(req),r);self.assertEqual(self.rsend(dict(req,command_id=uid()))['status'],'ALREADY_APPLIED')
        self.assertEqual(self.task()['urgency'],2)
        self.assertEqual(self.rapplier.query(reappearance_sql(dict(req,package_sha256='0'*64)))['code'],'COMMAND_CONTENT_CONFLICT')
        from source_ingest.bootstrap import bootstrap_sql
        self.assertEqual(self.bapplier.query(bootstrap_sql(dict(req,action='APPLY_BOOTSTRAP_TASKS')))['code'],'COMMAND_CONTENT_CONFLICT')

    def test_RP23_real_concurrent_packages_and_reference_update(self):
        self.cycle();_,p=self.rpropose();_,p2=self.rpropose(False);_,pkg=self.rpackage(p);_,pkg2=self.rpackage(p2)
        requests=[self.command('APPLY_REAPPEARANCE_TASKS',package_sha256=x['package_sha256']) for x in (pkg,pkg2)]
        result=self.lab.concurrent([reappearance_sql(r) for r in requests],role='d5_applier')
        self.assertEqual(sorted(r['status'] for r in result),['CONFLICT','OK']);self.assertEqual(self.task()['row_version'],1)
        self.cycle(present=body('Returned'),returning=body('Again'),create=False)
        _,p=self.rpropose();_,pkg=self.rpackage(p);req=self.command('APPLY_REAPPEARANCE_TASKS',package_sha256=pkg['package_sha256'])
        result=self.lab.concurrent([reappearance_sql(req),submit_sql(self.select(self.after,self.refv))],role='d5_lab_admin')
        self.assertEqual(result[1]['status'],'OK');self.assertIn(result[0]['status'],('OK','CONFLICT'))
        if result[0]['status']=='CONFLICT':self.assertEqual(result[0]['code'],'REFERENCE_VERSION_CONFLICT')

    def test_RP24_mixed_atomicity_abort_and_failure_after_mutations(self):
        present=body()+b'| PT-02 | Second | x | x | - | OPEN | no | inert |\n'
        after=body('Returned')+b'| PT-02 | Second new | x | x | - | OPEN | no | inert |\n'
        self.initial(present);i1=self.iid;other=uid();self.intent('PT-02',other,uid());i2=self.iid
        _,b1=self.bpropose(iid=i1);_,b2=self.bpropose('PT-02',i2);_,bpkg=self.bpackage(b1,b2);self.bapply(bpkg)
        self.iid=i1;self.key='PT-01';self.missing=body(key='PT-99');self.stage(present,self.missing)
        _,a1=self.propose(iid=i1);_,a2=self.propose('PT-02',iid=i2);_,apkg=self.package(a1,a2);areq,_=self.apply(apkg)
        self.returned(after);self.abs_aid=areq['command_id'];self.abs_pid=a1['proposal_id'];_,r1=self.rpropose()
        self.iid=i2;self.key='PT-02';self.abs_pid=a2['proposal_id'];_,r2=self.rpropose();_,pkg=self.rpackage(r1,r2)
        self.lab.sql(f"UPDATE public.tasks SET urgency=2 WHERE id='{other}';");before=self.lab.protected_state()
        self.assertEqual(self.rapply(pkg)[1]['code'],'TARGET_CAS_CONFLICT');self.assertEqual(self.lab.protected_state(),before)
        self.lab.sql(f"UPDATE public.tasks SET urgency=0 WHERE id='{other}';");before=self.lab.protected_state()
        req=self.command('APPLY_REAPPEARANCE_TASKS',package_sha256=pkg['package_sha256']);self.lab.abort_after(reappearance_sql(req))
        self.assertEqual(self.lab.protected_state(),before);self.assertIsNone(self.reader.read_command(req['command_id']))
        fault="""BEGIN;CREATE FUNCTION pg_temp.reappearance_fault() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic failure after reappearance mutations'; END $$;
        CREATE TRIGGER reappearance_fault BEFORE INSERT ON d5.reappearance_applications FOR EACH ROW EXECUTE FUNCTION pg_temp.reappearance_fault();"""
        error=self.denied(fault+reappearance_sql(req)+'COMMIT;',role='d5_lab_admin');self.assertIn('synthetic failure after reappearance mutations',error)
        self.assertEqual(self.lab.protected_state(),before);self.assertIsNone(self.reader.read_command(req['command_id']))
        self.assertEqual(self.scalar(f"SELECT bool_and(version=2) FROM d5.task_mapping_heads WHERE intent_id IN ('{i1}','{i2}');"),'t')

    def test_RP25_lost_response_restart_and_CLI_recovery(self):
        self.cycle();_,p=self.rpropose();_,pkg=self.rpackage(p);req=self.command('APPLY_REAPPEARANCE_TASKS',package_sha256=pkg['package_sha256'])
        self.lab.sql(reappearance_sql(req),role='d5_applier');self.lab.restart();r=self.reader.read_command(req['command_id']);self.assertEqual(self.rsend(req),r)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'request.json';path.write_text(json.dumps(req))
            run=subprocess.run([sys.executable,'-m','source_ingest.reappearance','--container',self.lab.container,'--request',str(path)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr);self.assertEqual(json.loads(run.stdout),r)
        self.assertEqual(self.task()['row_version'],1)

    def test_RP26_provenance_exact_append_only_and_identical_reuse(self):
        self.cycle(returning=body());old=self.task();before=self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}';")
        _,p=self.rpropose();_,pkg=self.rpackage(p);self.assertEqual(self.rapply(pkg)[1]['status'],'OK')
        self.assertEqual(self.task(),old);self.assertEqual(self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}';"),before)
        self.denied(f"UPDATE d2.task_sources SET source_locator='forged' WHERE task_id='{self.tid}';",role='d5_lab_admin')
        m=p['manifest'];self.assertEqual(self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}' AND revision_id='{m['after_revision_id']}' AND source_locator="+sql_text(m['source_change']['after']['row']['source_locator'])+';'),'1')

    def test_RP27_new_cycle_and_historical_review_revocation(self):
        self.cycle();old_a,old_p=self.abs_aid,self.abs_pid;m=self.abs_p['manifest']
        self.reviewer.decide(uid(),self.pid,self.doc,m['comparison_id'],self.key,m['row_sha256'],m['report_sha256'],1,'REJECT','fixture','Historical effect is not rolled back')
        self.accept(self.abs_p,1,'REJECT');_,p=self.rpropose();_,pkg=self.rpackage(p);first_req,first=self.rapply(pkg);self.assertEqual(first['status'],'OK')
        self.cycle(present=body('Returned'),returning=body('Again'),create=False);self.decide()
        self.assertEqual(self.rpropose(False,absence_application_command_id=old_a,absence_proposal_id=old_p)[1]['code'],'ABSENCE_VERSION_CONFLICT')
        _,p=self.rpropose(False);_,pkg=self.rpackage(p);self.assertEqual(self.rapply(pkg)[1]['status'],'OK')
        self.assertEqual(self.rsend(first_req),first);self.assertEqual(self.task()['title'],'Again');self.assertEqual(self.task()['row_version'],2)

    def test_RP28_I8_continuity_and_old_gates_preserved(self):
        self.cycle();_,p=self.rpropose();_,pkg=self.rpackage(p);self.rapply(pkg)
        self.stage(body('Returned'),body('Next'));_,p=self.propose();_,pkg=self.package(p);self.assertEqual(self.apply(pkg)[1]['status'],'OK')
        self.stage(body('Next'),body('Next',status='DONE'));_,p=self.propose();_,pkg=self.package(p);self.assertEqual(self.apply(pkg)[1]['status'],'OK')
        self.assertEqual(p['manifest']['action'],'LINK_SOURCE_EVIDENCE')
        self.absent(body('Next',status='DONE'));self.returned(body('Next'));self.assertEqual(self.propose()[1]['code'],'REAPPEARANCE_REVIEW_REQUIRED')
        self.initial(body('Next'),register=False);self.assertEqual(self.bpropose()[1]['code'],'INITIAL_INTENT_REQUIRED')

    def test_RP29_locks_roles_and_D3_stale_basis(self):
        self.cycle();_,p=self.rpropose();_,pkg=self.rpackage(p);req=self.command('APPLY_REAPPEARANCE_TASKS',package_sha256=pkg['package_sha256'])
        for role in ('d5_writer','d5_reviewer','d5_reader'):
            self.denied(reappearance_sql(req),role)
        for role in ('d5_writer','d5_reviewer','d5_reader','d5_applier'):
            self.denied('UPDATE public.tasks SET urgency=0;',role);self.denied('SELECT d5.task_lock_boundary();',role)
        self.denied('SELECT d3.lock_state();','d5_applier')
        self.denied('BEGIN ISOLATION LEVEL REPEATABLE READ;'+reappearance_sql(req),'d5_applier')
        blocker=self.lab.session('BEGIN;SELECT pg_advisory_xact_lock(742001);SELECT pg_sleep(60);ROLLBACK;','reappearance_boundary')
        self.lab.wait_for(lambda:self.lab.active('reappearance_boundary','PgSleep')==1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(self.lab.sql,reappearance_sql(req),'d5_applier')
                self.lab.wait_for(lambda:int(self.scalar("SELECT count(*) FROM pg_stat_activity WHERE usename='d5_applier' AND wait_event='advisory';"))==1)
                self.assertEqual(self.writer.submit(self.select(self.before,self.refv))['status'],'OK')
                self.lab.terminate('reappearance_boundary');self.assertEqual(json.loads(future.result(timeout=30).stdout)['code'],'REFERENCE_VERSION_CONFLICT')
        finally:self.lab.terminate('reappearance_boundary');blocker.communicate(timeout=5)
        blocker=self.lab.session('BEGIN;SELECT pg_advisory_xact_lock(742005);SELECT pg_sleep(60);ROLLBACK;','reappearance_boundary')
        self.lab.wait_for(lambda:self.lab.active('reappearance_boundary','PgSleep')==1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(self.lab.sql,reappearance_sql(dict(req,command_id=uid())),'d5_applier')
                self.lab.wait_for(lambda:int(self.scalar("SELECT count(*) FROM pg_stat_activity WHERE usename='d5_applier' AND wait_event='advisory';"))==1)
                self.assertEqual(self.scalar("SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a ON a.pid=l.pid WHERE a.usename='d5_applier' AND l.locktype='advisory' AND l.granted AND l.objid IN (742001,742002);"),'2')
                cid=uid();capture=self.lab.session(f"SELECT d3.capture('{cid}','{{\"action\":\"CAPTURE\"}}');",'reappearance_capture')
                self.lab.wait_for(lambda:self.lab.active('reappearance_capture','advisory')==1)
                self.lab.terminate('reappearance_boundary');future.result(timeout=30);out,error=capture.communicate(timeout=10)
                self.assertEqual(capture.returncode,0,error);self.assertEqual(json.loads(out)['capture_id'],cid)
        finally:self.lab.terminate('reappearance_boundary');blocker.communicate(timeout=5)
        self.refv=self.head()['version'];_,fresh=self.rpropose(False);_,pkg=self.rpackage(fresh)
        plan=uid();self.lab.sql(self.plan_fixture(plan,True));old=self.scalar(f"SELECT to_jsonb(p) FROM public.planning_runs p WHERE id='{plan}';")
        before=self.scalar("SELECT encode(public.digest(d3.state_body()::text,'sha256'),'hex');");self.assertEqual(self.rapply(pkg)[1]['status'],'OK')
        self.assertNotEqual(before,self.scalar("SELECT encode(public.digest(d3.state_body()::text,'sha256'),'hex');"))
        self.assertEqual(self.scalar(f"SELECT to_jsonb(p) FROM public.planning_runs p WHERE id='{plan}';"),old)
        self.denied(f"UPDATE public.planning_runs SET solver_version='changed' WHERE id='{plan}';",role='d5_lab_admin')

    def test_RP30_no_new_tasks_or_operational_activation(self):
        self.cycle();before=self.scalar(f"SELECT count(*) FROM public.tasks WHERE project_id='{self.pid}';")
        _,p=self.rpropose();_,pkg=self.rpackage(p);self.assertEqual(self.rapply(pkg)[1]['status'],'OK')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM public.tasks WHERE project_id='{self.pid}';"),before)
        self.assertEqual(self.scalar(f"SELECT d2.task_eligible('{self.tid}');"),'t');self.assertEqual(self.task()['status'],'BACKLOG')
        for table in ('public.operations','public.outbox_events','public.execution_attempts','d2.reservations','d2.plan_reservations','d4.deliveries'):
            self.assertEqual(self.scalar('SELECT count(*) FROM '+table+';'),'0')
        self.assertEqual(self.lab.catalog(),self.lab.v30_catalog);self.lab.assert_previous_functions()
