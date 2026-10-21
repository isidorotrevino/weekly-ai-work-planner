# SPDX-License-Identifier: GPL-3.0-only
"""A01-A34: explicit reviewed adoption; existing synthetic BACKLOG tasks only."""
import concurrent.futures
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from .local_edit_scenarios import LocalEdit
from .mapping_scenarios import body
from .postgres_scenarios import uid, PROFILE
from source_ingest.adoption import AdoptionClient, ENTRIES, adoption_sql
from source_ingest.bootstrap import bootstrap_sql
from source_ingest.postgres import sql_text, submit_sql
from source_ingest.preview import canonical
from source_ingest.task_mapping import mapping_sql


class Adoption(LocalEdit):
    def setUp(self):
        super().setUp()
        self.awriter=AdoptionClient(self.lab.container,'d5_writer')
        self.areviewer=AdoptionClient(self.lab.container,'d5_reviewer')
        self.areader=AdoptionClient(self.lab.container)
        self.aapplier=AdoptionClient(self.lab.container,'d5_applier')

    def asend(self,req,row=None):
        return {'d5_writer':self.awriter,'d5_reviewer':self.areviewer,'d5_applier':self.aapplier}[ENTRIES[req['action']][1]].submit_adoption(req,row)

    def existing(self,title='Title',description='Description'):
        self.lab.sql(f"INSERT INTO public.tasks(id,project_id,task_key,title,description) VALUES('{self.tid}','{self.pid}',{sql_text(self.tkey)},{sql_text(title)},"+('NULL' if description is None else sql_text(description))+');')

    def ainitial(self,data=None,key='PT-01',title='Title',description='Description',create=True,select=True,profile=PROFILE):
        self.key=key;self.source=body(key=key) if data is None else data
        self.initial(self.source,key,select=select,register=False,profile=profile)
        if create:self.existing(title,description)

    def arequest(self,**extra):
        row=next((r for r in self.snapshot['proposals'] if r['source_key']==self.key),None);payload=canonical(row)
        req=self.command('PREPARE_ADOPTION_TASK',source_key=self.key,profile=self.profile,policy='d5.task-projection.v1',task_id=self.tid,task_key=self.tkey,
            observation_id=self.oid,content_sha256=self.snapshot['content_sha256'],preview_sha256=self.ph,
            snapshot_row_sha256=hashlib.sha256(payload).hexdigest(),expected_reference_version=self.refv,reason='Synthetic explicit association of source ID and existing task')
        return dict(req,**extra),payload

    def apropose(self,**extra):
        req,row=self.arequest(**extra);return req,self.asend(req,row)

    def aaccept(self,p,version=0,decision='ACCEPT'):
        req=self.command('REVIEW_ADOPTION_TASK',proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],expected_version=version,
            decision=decision,reviewer_label='synthetic-reviewer',reason='Review full task association and unchanged local result')
        return req,self.asend(req)

    def apackage(self,*proposals,accept=True):
        pins=[]
        for p in proposals:
            if accept:
                _,r=self.aaccept(p)
                pin=dict(proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],review_command_id=r['command_id'],review_version=r['version_at_commit'])
            else:
                data=self.areader.artifact(self.pid,self.doc,'proposal',p['proposal_id'])
                pin={k:data[k] for k in ('proposal_id','manifest_sha256','review_command_id','review_version')};pin['review_command_id']=pin['review_command_id'] or uid()
            pins.append(pin)
        req=self.command('PACKAGE_ADOPTION_TASKS',items=sorted(pins,key=lambda x:x['proposal_id']));return req,self.asend(req)

    def aapply(self,pkg):
        req=self.command('APPLY_ADOPTION_TASKS',package_sha256=pkg['package_sha256']);count=self.scalar('SELECT count(*) FROM public.tasks;')
        r=self.asend(req);self.assertEqual(self.scalar('SELECT count(*) FROM public.tasks;'),count)
        if r['status']=='OK':self.iid=r['effects'][0]['intent_id']
        return req,r

    def source_insert(self,p,locator=None):
        m=p['manifest'];return f"INSERT INTO d2.task_sources VALUES('{m['intent']['task_id']}','{m['revision_id']}',{sql_text(locator or m['snapshot_row']['source_locator'])},'{self.doc}','{self.pid}');"

    def test_A01_prepare_without_reservation_or_task_write(self):
        self.ainitial();old=self.lab.protected_state();req,p=self.apropose()
        self.assertEqual(p['status'],'OK');self.assertEqual(self.asend(req),p);self.assertEqual(self.lab.protected_state(),old)
        for table in ('task_intents','task_mapping_heads','task_destinations'):
            self.assertEqual(self.scalar(f"SELECT count(*) FROM d5.{table} WHERE intent_id='{req['command_id']}';"),'0')
        self.assertEqual(p['manifest']['proposed_intent_id'],p['proposal_id'])

    def test_A02_prepare_accept_reject_never_reserve(self):
        self.ainitial();_,p=self.apropose();_,p2=self.apropose();self.aaccept(p);self.aaccept(p2);self.aaccept(p,1,'REJECT')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM d5.task_intents WHERE task_id='{self.tid}';"),'0')
        _,pkg=self.apackage(p2,accept=False);self.assertEqual(self.aapply(pkg)[1]['status'],'OK')

    def test_A03_explicit_scope_policy_and_task_identity(self):
        self.ainitial();req,row=self.arequest()
        for extra,code in [(dict(task_id=uid()),'TARGET_IDENTITY_CONFLICT'),(dict(task_key='wrong'),'TARGET_IDENTITY_CONFLICT'),
            (dict(project_id=uid()),'OBSERVATION_SCOPE_CONFLICT'),(dict(document_id=uid()),'OBSERVATION_SCOPE_CONFLICT'),
            (dict(profile='task-register.v1'),'OBSERVATION_SCOPE_CONFLICT'),(dict(policy='other'),'POLICY_PROFILE_CONFLICT')]:
            self.assertEqual(self.awriter.query(adoption_sql(dict(req,command_id=uid(),**extra),row))['code'],code)
        self.lab.sql(f"UPDATE public.tasks SET task_key='{'x'*257}' WHERE id='{self.tid}';");self.tkey='x'*257
        self.assertEqual(self.apropose()[1]['code'],'INVALID_TASK_KEY')

    def test_A04_existing_intents_even_version_zero_block(self):
        self.ainitial();other=uid();_,registered=self.intent(self.key,other,uid());self.assertEqual(registered['status'],'OK')
        self.assertEqual(self.apropose()[1]['code'],'CORRESPONDENCE_OCCUPIED')
        self.ainitial(key='PT-02',create=False);self.assertEqual(self.apropose()[1]['status'],'OK')
        _,p=self.apropose();_,pkg=self.apackage(p);self.assertEqual(self.aapply(pkg)[1]['status'],'OK')
        self.assertEqual(self.apropose()[1]['code'],'CORRESPONDENCE_OCCUPIED')
        self.ainitial(key='PT-03',create=False);self.assertEqual(self.apropose()[1]['code'],'CORRESPONDENCE_OCCUPIED')

    def test_A05_any_prior_source_including_identical_blocks(self):
        self.ainitial();_,p=self.apropose();_,pkg=self.apackage(p);self.lab.sql(self.source_insert(p))
        self.assertEqual(self.apropose()[1]['code'],'TARGET_HAS_SOURCE');self.assertEqual(self.aapply(pkg)[1]['code'],'TARGET_HAS_SOURCE')
        self.denied(f"DELETE FROM d2.task_sources WHERE task_id='{self.tid}';",role='d5_lab_admin')

    def test_A06_state_operation_and_historical_plan(self):
        self.ainitial();_,p=self.apropose();_,pkg=self.apackage(p)
        fixtures=[f"SELECT d2.transition('{uid()}','{json.dumps(dict(entity_type='TASK',entity_id=self.tid,expected_version=0,actor='fixture',reason='negative test',to='BLOCKED',**{'from':'BACKLOG'}))}');",
            f"INSERT INTO public.operations(task_id,operation_type,idempotency_key) VALUES('{self.tid}','SYNTHETIC','{uid()}');"]
        plan=uid();fixtures.append(self.plan_fixture(plan)+f"INSERT INTO public.schedule_entries(planning_run_id,task_id,resource_id,pool,priority_snapshot,state) VALUES('{plan}','{self.tid}','{self.lab.resource}','PLANNED','{{}}','CANCELLED');")
        for fixture in fixtures:
            prepare,row=self.arequest();apply=self.command('APPLY_ADOPTION_TASKS',package_sha256=pkg['package_sha256'])
            for statement in (adoption_sql(prepare,row),adoption_sql(apply)):
                r=self.lab.sql('BEGIN;'+fixture+statement+'ROLLBACK;');self.assertEqual(json.loads(r.stdout.splitlines()[-1])['code'],'TARGET_HAS_WORK_OR_STATE')
        self.assertEqual(self.scalar('SELECT count(*) FROM public.operations;'),'0')

    def test_A07_long_ID_literal_source_and_target(self):
        key='LONG-'+'1'*5000;text='Árbol **raw** \\| `literal`'
        self.ainitial(body(text,'ñ [x](https://example.invalid)',annotation=' source claim',key=key,struck=True),key,title='Local text')
        old=self.task();_,p=self.apropose();_,pkg=self.apackage(p);self.assertEqual(self.aapply(pkg)[1]['status'],'OK')
        self.assertEqual(self.task(),old);self.assertEqual(p['manifest']['intent']['source_key'],key);self.assertEqual(p['manifest']['projection']['title'],text)
        self.assertTrue(p['manifest']['snapshot_row']['source_struck'])

    def test_A08_absent_duplicate_and_unselected_ambiguity(self):
        self.ainitial(body(key='PT-99'));req,row=self.arequest()
        with self.assertRaises(ValueError):self.asend(req,row)
        self.assertEqual(self.awriter.query(adoption_sql(req,row))['code'],'SOURCE_ROW_NOT_UNIQUE')
        for data in (body()+b'| PT-99 | x | c | x | - | OPEN | no | inert |\n| PT-99 | y | c | y | - | OPEN | no | inert |\n',
                     body()+b'| PT-99 | ambiguous | row |\n'):
            self.ainitial(data,create=False);req,row=self.arequest()
            with self.assertRaises(ValueError):self.asend(req,row)
            self.assertEqual(self.awriter.query(adoption_sql(req,row))['code'],'OBSERVATION_BLOCKED')

    def test_A09_compatibility_selection_and_profile(self):
        data=body(annotation=' source annotation')+b'\n| PT-02 | Other | c | Other | - | OPEN | no | inert |\n'
        self.ainitial(data);_,p=self.apropose();_,pkg=self.apackage(p);self.assertEqual(self.aapply(pkg)[1]['status'],'OK')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM d5.task_intents WHERE document_id='{self.doc}';"),'1')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM public.tasks WHERE project_id='{self.pid}';"),'1')
        self.assertIn('source annotation',p['manifest']['source_basis']['annotation_text'])

    def test_A10_reference_required_and_ABA(self):
        self.ainitial(select=False);self.assertEqual(self.apropose()[1]['code'],'REFERENCE_VERSION_CONFLICT')
        self.refv=self.writer.submit(self.select(self.oid,self.refv))['version_at_commit'];_,p=self.apropose();_,pkg=self.apackage(p)
        _,other=self.ingest(self.capture(body('Other')));self.writer.submit(self.select(other['observation_id'],self.refv));self.writer.submit(self.select(self.oid,self.refv+1))
        self.assertEqual(self.aapply(pkg)[1]['code'],'REFERENCE_VERSION_CONFLICT')

    def test_A11_observation_and_hash_domains(self):
        self.ainitial();req,row=self.arequest()
        for k in ('content_sha256','preview_sha256','snapshot_row_sha256'):
            bad=dict(req,command_id=uid(),**{k:'0'*64})
            with self.assertRaises(ValueError):self.asend(bad,row)
        self.denied(adoption_sql(dict(req,command_id=uid()),b'{}'))
        _,p=self.apropose();_,pkg=self.apackage(p)
        _,other=self.ingest(self.capture(body(),label='same bytes, different observation'))
        self.assertNotEqual(other['observation_id'],self.oid);self.writer.submit(self.select(other['observation_id'],self.refv))
        self.assertEqual(self.aapply(pkg)[1]['code'],'REFERENCE_VERSION_CONFLICT')

    def test_A12_projection_validation_and_NULL(self):
        self.ainitial(body(' \u00a0 '));self.assertEqual(self.apropose()[1]['code'],'INVALID_PROJECTION')
        self.ainitial(body('Source','-'),create=False);self.local(' \u00a0 ');self.assertEqual(self.apropose()[1]['code'],'INVALID_PROJECTION')
        self.local(description=None);old=self.task();_,p=self.apropose();_,pkg=self.apackage(p);self.assertEqual(self.aapply(pkg)[1]['status'],'OK')
        self.assertEqual(self.task(),old);self.assertIsNone(p['manifest']['local_projection']['description']);self.assertEqual(p['manifest']['projection']['description'],'-')

    def test_A13_equal_and_divergent_text_never_written(self):
        for n,title in enumerate(('Title','Local'),1):
            self.tid,self.tkey=uid(),uid();self.ainitial(key=f'PT-{n:02}',title=title);old=self.task();_,p=self.apropose();_,pkg=self.apackage(p)
            trigger="BEGIN;CREATE FUNCTION pg_temp.no_adoption_write() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'unexpected task write'; END $$;CREATE TRIGGER no_adoption_write BEFORE INSERT OR UPDATE OR DELETE ON public.tasks FOR EACH ROW EXECUTE FUNCTION pg_temp.no_adoption_write();"
            req=self.command('APPLY_ADOPTION_TASKS',package_sha256=pkg['package_sha256']);r=self.lab.sql(trigger+adoption_sql(req)+'ROLLBACK;')
            self.assertEqual(json.loads(r.stdout.splitlines()[-1])['status'],'OK');self.assertEqual(self.aapply(pkg)[1]['status'],'OK');self.assertEqual(self.task(),old)
            self.assertEqual(p['manifest']['result_projection']['title'],title)

    def test_A14_preserve_epic_fields_and_dependencies(self):
        self.ainitial();eid,other=uid(),uid()
        self.lab.sql(f"INSERT INTO public.epics(id,project_id,epic_key,title) VALUES('{eid}','{self.pid}','fixture','Synthetic epic');INSERT INTO public.tasks(id,project_id,task_key,title) VALUES('{other}','{self.pid}','other','Other');UPDATE public.tasks SET epic_id='{eid}',urgency=3,deferred_count=2,deadline_at='2026-11-01' WHERE id='{self.tid}';INSERT INTO public.task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES('{other}','{self.tid}','SOFT');")
        before=self.task();deps=self.scalar(f"SELECT to_jsonb(d) FROM public.task_dependencies d WHERE successor_task_id='{self.tid}';")
        _,p=self.apropose();_,pkg=self.apackage(p);self.assertEqual(self.aapply(pkg)[1]['status'],'OK');self.assertEqual(self.task(),before)
        self.assertEqual(self.scalar(f"SELECT to_jsonb(d) FROM public.task_dependencies d WHERE successor_task_id='{self.tid}';"),deps)

    def test_A15_inert_source_claims(self):
        self.ainitial(body(status='DONE',annotation=' approved verified'))
        _,p=self.apropose();_,pkg=self.apackage(p);self.assertEqual(self.aapply(pkg)[1]['status'],'OK');self.assertEqual(self.task()['status'],'BACKLOG')
        self.assertIn('verified',p['manifest']['source_basis']['annotation_text'])

    def test_A16_reason_validation(self):
        self.ainitial()
        for reason in ('',' \u00a0 ','a\nb','x'*1025):self.assertEqual(self.apropose(reason=reason)[1]['code'],'ADOPTION_REASON_REQUIRED')
        req,row=self.arequest();self.denied(adoption_sql(dict(req,reason=None),row))

    def test_A17_manifest_closed_and_immutable(self):
        self.ainitial();_,p=self.apropose();req,_=self.aaccept(p)
        for k,v in [('task_id',uid()),('force',True),('result_projection',{'title':'new'})]:self.denied(adoption_sql(dict(req,command_id=uid(),**{k:v})),role='d5_reviewer')
        self.denied("UPDATE d5.adoption_proposals SET manifest=manifest||'{\"mode\":\"CREATE\"}';",role='d5_lab_admin')
        _,fresh=self.apropose(reason='Another complete adoption reason');self.assertNotEqual(p['manifest_sha256'],fresh['manifest_sha256'])
        self.assertEqual(self.apackage(fresh,accept=False)[1]['code'],'MANIFEST_NOT_ACCEPTED')
        original=self.areader.artifact
        for field in ('projection','source_basis','local_projection','proposed_intent_id','result_projection'):
            forged=copy.deepcopy(p);forged['manifest'][field]='forged';self.areader.artifact=lambda *args,data=forged:data
            with self.assertRaises(ValueError):self.areader.verify_manifest(self.pid,self.doc,p['proposal_id'],p['manifest_sha256'])
        self.areader.artifact=original

    def test_A18_no_fabricated_comparison_or_inherited_ACCEPT(self):
        self.ainitial();_,p=self.apropose()
        self.assertNotIn('comparison_id',p['manifest']);self.assertIsNone(p['manifest']['prior_applied_basis'])
        self.assertEqual(self.apackage(p,accept=False)[1]['code'],'MANIFEST_NOT_ACCEPTED')
        req,_=self.aaccept(p)
        for action,client,sql in [('REVIEW_TASK_PROPOSAL',self.mreviewer,mapping_sql),('REVIEW_BOOTSTRAP_TASK',self.breviewer,bootstrap_sql)]:
            self.assertEqual(client.query(sql(dict(req,command_id=uid(),action=action)))['code'],'MANIFEST_SCOPE_CONFLICT')

    def test_A19_own_review_version_and_ABA(self):
        self.ainitial();_,p=self.apropose();_,pkg=self.apackage(p);self.aaccept(p,1,'REJECT');self.aaccept(p,2,'ACCEPT')
        self.assertEqual(self.aapply(pkg)[1]['code'],'ADOPTION_REVIEW_CONFLICT')
        _,fresh=self.apackage(p,accept=False);self.assertEqual(self.aapply(fresh)[1]['status'],'OK')

    def test_A20_package_explicit_limits_and_single_snapshot(self):
        self.ainitial();_,p=self.apropose();req,pkg=self.apackage(p)
        for items in ([],req['items']*2,req['items']*2001):self.denied(adoption_sql(dict(req,command_id=uid(),items=items)))
        _,p2=self.apropose();req2,_=self.apackage(p2)
        self.denied(adoption_sql(dict(req,command_id=uid(),items=sorted(req['items']+req2['items'],key=lambda x:x['proposal_id']))))
        self.assertEqual(self.awriter.query(adoption_sql(dict(req,command_id=uid())))['package_sha256'],pkg['package_sha256'])
        self.assertEqual(self.mapper.query(mapping_sql(dict(req,command_id=uid(),action='PACKAGE_TASK_PROPOSALS')))['code'],'MANIFEST_SCOPE_CONFLICT')
        self.assertEqual(self.bwriter.query(bootstrap_sql(dict(req,command_id=uid(),action='PACKAGE_BOOTSTRAP_TASKS')))['code'],'MANIFEST_SCOPE_CONFLICT')
        # Another source row / task is valid alone, but belongs to another snapshot.
        self.tid,self.tkey=uid(),uid();self.ainitial(body(key='PT-02'),key='PT-02');_,other=self.apropose();req3,_=self.apackage(other)
        self.denied(adoption_sql(dict(req,command_id=uid(),items=sorted(req['items']+req3['items'],key=lambda x:x['proposal_id']))))

    def test_A21_whole_target_CAS_and_observable_ABA(self):
        self.ainitial();_,p=self.apropose();_,pkg=self.apackage(p);self.local('Edited without version')
        self.assertEqual(self.aapply(pkg)[1]['code'],'TARGET_CAS_CONFLICT')
        _,p=self.apropose();_,pkg=self.apackage(p);self.local('Other',bump=True);self.local('Edited without version',bump=True)
        self.assertEqual(self.aapply(pkg)[1]['code'],'TARGET_CAS_CONFLICT')
        _,p=self.apropose();_,pkg=self.apackage(p);self.lab.sql(f"UPDATE public.tasks SET urgency=4 WHERE id='{self.tid}';")
        self.assertEqual(self.aapply(pkg)[1]['code'],'TARGET_CAS_CONFLICT')

    def test_A22_real_competing_source_and_task_adoptions(self):
        self.ainitial();_,p=self.apropose();_,p2=self.apropose();_,pkg=self.apackage(p);_,pkg2=self.apackage(p2)
        requests=[self.command('APPLY_ADOPTION_TASKS',package_sha256=x['package_sha256']) for x in (pkg,pkg2)]
        results=self.lab.concurrent([adoption_sql(r) for r in requests],role='d5_applier')
        self.assertEqual(sorted(r['status'] for r in results),['CONFLICT','OK']);self.assertEqual(self.task()['row_version'],0)
        self.assertEqual(self.scalar(f"SELECT count(*) FROM d5.task_intents WHERE task_id='{self.tid}';"),'1')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}';"),'1')

    def test_A23_old_registration_reservation_and_gate(self):
        self.ainitial();_,p=self.apropose();_,pkg=self.apackage(p)
        self.assertEqual(self.intent(self.key)[1]['code'],'IDENTITY_CONFLICT')
        _,r=self.intent(self.key,uid(),uid());self.assertEqual(r['status'],'OK')
        self.assertEqual(self.aapply(pkg)[1]['code'],'CORRESPONDENCE_OCCUPIED')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}';"),'0')

    def test_A24_real_FK_races_both_orders(self):
        self.ainitial();_,p=self.apropose();_,pkg=self.apackage(p);apply=self.command('APPLY_ADOPTION_TASKS',package_sha256=pkg['package_sha256'])
        blocker=self.lab.session('BEGIN;SELECT pg_advisory_xact_lock(749024);SELECT pg_sleep(60);ROLLBACK;','adoption_fk_barrier')
        self.lab.wait_for(lambda:self.lab.active('adoption_fk_barrier','PgSleep')==1)
        writer=self.lab.session('BEGIN;'+self.source_insert(p)+'SELECT pg_advisory_xact_lock(749024);COMMIT;','adoption_fk_writer')
        self.lab.wait_for(lambda:self.lab.active('adoption_fk_writer','advisory')==1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(self.lab.sql,adoption_sql(apply),'d5_applier')
                self.lab.wait_for(lambda:int(self.scalar("SELECT count(*) FROM pg_stat_activity WHERE usename='d5_applier' AND wait_event IN ('transactionid','tuple');"))==1)
                self.lab.fk_wait_events.append('source_first: APPLY waits on task FK lock')
                self.lab.terminate('adoption_fk_barrier');out,error=writer.communicate(timeout=10);self.assertEqual(writer.returncode,0,error)
                self.assertEqual(json.loads(future.result(timeout=30).stdout)['code'],'TARGET_HAS_SOURCE')
        finally:
            self.lab.terminate('adoption_fk_barrier');self.lab.terminate('adoption_fk_writer');blocker.communicate(timeout=5)
        # Reverse order: adoption holds the target lock until commit. A later external
        # source insert waits; it may commit after adoption (no eternal write ban).
        self.tid,self.tkey=uid(),uid();self.ainitial(key='PT-02');_,p=self.apropose();_,pkg=self.apackage(p)
        apply=self.command('APPLY_ADOPTION_TASKS',package_sha256=pkg['package_sha256'])
        blocker=self.lab.session('BEGIN;SELECT pg_advisory_xact_lock(749025);SELECT pg_sleep(60);ROLLBACK;','adoption_fk_barrier')
        self.lab.wait_for(lambda:self.lab.active('adoption_fk_barrier','PgSleep')==1)
        applier=self.lab.session('BEGIN;'+adoption_sql(apply)+'SELECT pg_advisory_xact_lock(749025);COMMIT;','adoption_fk_apply')
        self.lab.wait_for(lambda:self.lab.active('adoption_fk_apply','advisory')==1)
        writer=self.lab.session('BEGIN;'+self.source_insert(p,'external-after-commit-fixture')+'COMMIT;','adoption_fk_writer')
        try:
            self.lab.wait_for(lambda:self.lab.active('adoption_fk_writer','transactionid')+self.lab.active('adoption_fk_writer','tuple')==1)
            self.lab.fk_wait_events.append('adoption_first: later source FK waits until commit')
            self.lab.terminate('adoption_fk_barrier');out,error=applier.communicate(timeout=10);self.assertEqual(applier.returncode,0,error)
            self.assertEqual(json.loads(out.splitlines()[0])['status'],'OK');out,error=writer.communicate(timeout=10);self.assertEqual(writer.returncode,0,error)
        finally:
            self.lab.terminate('adoption_fk_barrier');self.lab.terminate('adoption_fk_apply');self.lab.terminate('adoption_fk_writer');blocker.communicate(timeout=5)
        self.assertEqual(self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}';"),'2')

    def test_A25_reference_review_and_boundary_races(self):
        self.ainitial();_,p=self.apropose();_,pkg=self.apackage(p);req=self.command('APPLY_ADOPTION_TASKS',package_sha256=pkg['package_sha256'])
        review=self.command('REVIEW_ADOPTION_TASK',proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],expected_version=1,decision='REJECT',reviewer_label='fixture',reason='Concurrent revoke')
        result=self.lab.concurrent([adoption_sql(req),adoption_sql(review)],role='d5_lab_admin')
        self.assertEqual(result[1]['status'],'OK');self.assertIn(result[0]['status'],('OK','CONFLICT'))
        self.tid,self.tkey=uid(),uid();self.ainitial(key='PT-02');_,p=self.apropose();_,pkg=self.apackage(p)
        req=self.command('APPLY_ADOPTION_TASKS',package_sha256=pkg['package_sha256'])
        blocker=self.lab.session('BEGIN;SELECT pg_advisory_xact_lock(742001);SELECT pg_sleep(60);ROLLBACK;','adoption_boundary')
        self.lab.wait_for(lambda:self.lab.active('adoption_boundary','PgSleep')==1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(self.lab.sql,adoption_sql(req),'d5_applier')
                self.lab.wait_for(lambda:int(self.scalar("SELECT count(*) FROM pg_stat_activity WHERE usename='d5_applier' AND wait_event='advisory';"))==1)
                self.assertEqual(self.writer.submit(self.select(self.oid,self.refv))['status'],'OK')
                self.lab.terminate('adoption_boundary');self.assertEqual(json.loads(future.result(timeout=30).stdout)['code'],'REFERENCE_VERSION_CONFLICT')
        finally:self.lab.terminate('adoption_boundary');blocker.communicate(timeout=5)

    def test_A26_atomic_shared_identity_and_real_command_FK(self):
        self.ainitial(title='Local');_,p=self.apropose();_,pkg=self.apackage(p);_,r=self.aapply(pkg)
        self.assertEqual(r['status'],'OK');self.assertFalse(r['writes_task']);self.assertEqual(self.iid,p['proposal_id'])
        self.assertEqual(self.scalar(f"SELECT request->>'action' FROM d5.commands WHERE command_id='{self.iid}';"),'PREPARE_ADOPTION_TASK')
        actual=json.loads(self.scalar(f"SELECT to_jsonb(i) FROM d5.task_intents i WHERE intent_id='{self.iid}';"));self.assertEqual(actual,p['manifest']['intent'])
        head=json.loads(self.scalar(f"SELECT to_jsonb(h) FROM d5.task_mapping_heads h WHERE intent_id='{self.iid}';"))
        self.assertEqual(head['version'],1);self.assertEqual(head['projection']['title'],'Title');self.assertEqual(self.task()['title'],'Local')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM public.audit_events WHERE entity_id='{self.tid}' AND action='LINK_EXISTING_BACKLOG';"),'1')

    def test_A27_batch_rollback_abort_and_late_failure(self):
        data=body()+b'| PT-02 | Other | c | Other | - | OPEN | no | inert |\n'
        self.ainitial(data);first=self.tid;_,p1=self.apropose()
        self.tid,self.tkey=uid(),uid();self.existing('Second local');self.key='PT-02';_,p2=self.apropose();_,pkg=self.apackage(p1,p2)
        self.lab.sql(f"UPDATE public.tasks SET urgency=3 WHERE id='{self.tid}';");before=self.resolution_state()
        self.assertEqual(self.aapply(pkg)[1]['code'],'TARGET_CAS_CONFLICT');self.assertEqual(self.resolution_state(),before)
        self.lab.sql(f"UPDATE public.tasks SET urgency=0 WHERE id='{self.tid}';");before=self.resolution_state()
        req=self.command('APPLY_ADOPTION_TASKS',package_sha256=pkg['package_sha256']);self.lab.abort_after(adoption_sql(req))
        self.assertEqual(self.resolution_state(),before);self.assertIsNone(self.reader.read_command(req['command_id']))
        fault="""BEGIN;CREATE FUNCTION pg_temp.adoption_fault() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic failure after adoption effects'; END $$;
        CREATE TRIGGER adoption_fault BEFORE INSERT ON d5.adoption_applications FOR EACH ROW EXECUTE FUNCTION pg_temp.adoption_fault();"""
        error=self.denied(fault+adoption_sql(req)+'COMMIT;',role='d5_lab_admin');self.assertIn('synthetic failure after adoption effects',error)
        self.assertEqual(self.resolution_state(),before);self.assertIsNone(self.reader.read_command(req['command_id']))
        self.assertEqual(self.aapply(pkg)[1]['status'],'OK');self.assertEqual(self.task(first)['title'],'Title');self.assertEqual(self.task()['title'],'Second local')

    def test_A28_global_replay_and_no_restoration(self):
        self.ainitial();_,p=self.apropose();_,pkg=self.apackage(p);req,r=self.aapply(pkg);self.local('Later',bump=True)
        self.assertEqual(self.asend(req),r);self.assertEqual(self.asend(dict(req,command_id=uid()))['status'],'ALREADY_APPLIED');self.assertEqual(self.task()['title'],'Later')
        self.assertEqual(self.aapplier.query(adoption_sql(dict(req,package_sha256='0'*64)))['code'],'COMMAND_CONTENT_CONFLICT')
        self.assertEqual(self.applier.query(mapping_sql(dict(req,action='APPLY_TASK_PROPOSALS')))['code'],'COMMAND_CONTENT_CONFLICT')

    def test_A29_lost_response_restart_and_CLI(self):
        self.ainitial();_,p=self.apropose();_,pkg=self.apackage(p);req=self.command('APPLY_ADOPTION_TASKS',package_sha256=pkg['package_sha256'])
        self.lab.sql(adoption_sql(req),role='d5_applier');self.lab.restart();r=self.reader.read_command(req['command_id']);self.assertEqual(self.asend(req),r)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'request.json';path.write_text(json.dumps(req))
            run=subprocess.run([sys.executable,'-m','source_ingest.adoption','--container',self.lab.container,'--request',str(path)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr);self.assertEqual(json.loads(run.stdout),r)
            path.write_text('{"action":"x","action":"y"}')
            run=subprocess.run([sys.executable,'-m','source_ingest.adoption','--container',self.lab.container,'--request',str(path)],capture_output=True,text=True);self.assertEqual(run.returncode,1)
        self.assertEqual(self.task()['row_version'],0)

    def test_A30_equal_text_continues_through_existing_I8(self):
        self.ainitial();_,p=self.apropose();_,pkg=self.apackage(p);self.aapply(pkg)
        self.stage(self.source,body('Next'));_,p=self.propose();_,pkg=self.package(p);self.assertEqual(self.apply(pkg)[1]['status'],'OK')
        self.stage(body('Next'),body('Next',status='DONE'));_,p=self.propose();_,pkg=self.package(p);self.assertEqual(self.apply(pkg)[1]['status'],'OK')
        self.assertEqual(p['manifest']['action'],'LINK_SOURCE_EVIDENCE');self.assertEqual(self.task()['title'],'Next')
        self.absent(body('Next',status='DONE'));self.assertEqual(self.task()['title'],'Next')

    def test_A31_divergent_text_requires_existing_I14(self):
        self.ainitial(title='Local');_,p=self.apropose();_,pkg=self.apackage(p);self.aapply(pkg)
        self.stage(self.source,self.source);self.assertEqual(self.propose(accept_source=False)[1]['code'],'NO_CHANGED_ROW_NO_BOOTSTRAP')
        self.assertEqual(self.lpropose(False)[1]['code'],'PRESENT_CHANGED_ROW_REQUIRED')
        self.stage(self.source,body('Remote'));self.assertEqual(self.propose()[1]['code'],'LOCAL_EDIT_CONFLICT')
        _,p=self.lpropose(False,choice='KEEP_LOCAL');_,pkg=self.lpackage(p);self.assertEqual(self.lapply(pkg)[1]['status'],'OK')
        self.assertEqual(self.task()['title'],'Local');self.assertEqual(self.task()['row_version'],0)
        self.stage(body('Remote'),body('Again'));self.assertEqual(self.propose()[1]['code'],'LOCAL_EDIT_CONFLICT')
        _,p=self.lpropose(False);_,pkg=self.lpackage(p);self.assertEqual(self.lapply(pkg)[1]['status'],'OK');self.assertEqual(self.task()['title'],'Again')

    def test_A32_absence_and_reappearance_keep_old_guards(self):
        self.ainitial();_,p=self.apropose();_,pkg=self.apackage(p);self.aapply(pkg)
        self.absent(body());self.returned(body('Returned'));_,p=self.rpropose();_,pkg=self.rpackage(p);self.assertEqual(self.rapply(pkg)[1]['status'],'OK')
        self.absent(body('Returned'));self.returned(body('Again'));self.local('Local after absence')
        self.assertEqual(self.rpropose()[1]['code'],'LOCAL_EDIT_CONFLICT')
        self.initial(body('Again'),register=False);self.assertEqual(self.bpropose()[1]['code'],'INITIAL_INTENT_REQUIRED')

    def test_A33_roles_locks_readset_and_published_snapshot(self):
        self.ainitial();_,p=self.apropose();_,pkg=self.apackage(p);req=self.command('APPLY_ADOPTION_TASKS',package_sha256=pkg['package_sha256'])
        for role in ('d5_writer','d5_reader','d5_reviewer'):self.denied(adoption_sql(req),role)
        for role in ('d5_writer','d5_reader','d5_reviewer','d5_applier'):
            self.denied('UPDATE public.tasks SET urgency=0;',role);self.denied('SELECT d5.task_lock_boundary();',role)
        self.denied('SELECT d3.lock_state();','d5_applier');self.denied('BEGIN ISOLATION LEVEL REPEATABLE READ;'+adoption_sql(req),'d5_applier')
        plan=uid();self.lab.sql(self.plan_fixture(plan,True));old_plan=self.scalar(f"SELECT to_jsonb(p) FROM public.planning_runs p WHERE id='{plan}';")
        old_task=self.task();digest=self.scalar("SELECT encode(public.digest(d3.state_body()::text,'sha256'),'hex');")
        blocker=self.lab.session('BEGIN;SELECT pg_advisory_xact_lock(742005);SELECT pg_sleep(60);ROLLBACK;','adoption_boundary')
        self.lab.wait_for(lambda:self.lab.active('adoption_boundary','PgSleep')==1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(self.lab.sql,adoption_sql(req),'d5_applier')
                self.lab.wait_for(lambda:int(self.scalar("SELECT count(*) FROM pg_stat_activity WHERE usename='d5_applier' AND wait_event='advisory';"))==1)
                self.assertEqual(self.scalar("SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a ON a.pid=l.pid WHERE a.usename='d5_applier' AND l.locktype='advisory' AND l.granted AND l.objid IN (742001,742002);"),'2')
                cid=uid();capture=self.lab.session(f"SELECT d3.capture('{cid}','{{\"action\":\"CAPTURE\"}}');",'adoption_capture')
                self.lab.wait_for(lambda:self.lab.active('adoption_capture','advisory')==1)
                self.lab.terminate('adoption_boundary');self.assertEqual(json.loads(future.result(timeout=30).stdout)['status'],'OK')
                out,error=capture.communicate(timeout=10);self.assertEqual(capture.returncode,0,error);self.assertEqual(json.loads(out)['capture_id'],cid)
        finally:self.lab.terminate('adoption_boundary');blocker.communicate(timeout=5)
        self.assertEqual(self.task(),old_task);self.assertEqual(digest,self.scalar("SELECT encode(public.digest(d3.state_body()::text,'sha256'),'hex');"))
        self.assertEqual(self.scalar(f"SELECT to_jsonb(p) FROM public.planning_runs p WHERE id='{plan}';"),old_plan)
        self.denied(f"UPDATE public.planning_runs SET solver_version='changed' WHERE id='{plan}';",role='d5_lab_admin')

    def test_A34_no_new_tasks_activation_and_old_catalog(self):
        self.ainitial();count=self.scalar('SELECT count(*) FROM public.tasks;');_,p=self.apropose();_,pkg=self.apackage(p);self.assertEqual(self.aapply(pkg)[1]['status'],'OK')
        self.assertEqual(self.scalar('SELECT count(*) FROM public.tasks;'),count);self.assertEqual(self.scalar(f"SELECT d2.task_eligible('{self.tid}');"),'t')
        for table in ('public.operations','public.outbox_events','public.execution_attempts','d2.reservations','d2.plan_reservations','d4.deliveries'):
            self.assertEqual(self.scalar('SELECT count(*) FROM '+table+';'),'0')
        self.assertEqual(self.lab.catalog(),self.lab.v30_catalog);self.lab.assert_adoption_previous_functions()
