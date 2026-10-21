# SPDX-License-Identifier: GPL-3.0-only
"""M01-M27: synthetic effects only, no operational admission or execution."""
import concurrent.futures
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import sys

from .review_scenarios import Review
from .postgres_scenarios import uid, PROFILE
from source_ingest.postgres import envelope, sql_text
from source_ingest.task_mapping import ENTRIES, MappingClient, mapping_sql

HEADER = '| ID | Item | Component(s) | Objective | Blocked on | Status | Verified | Source |\n|---|---|---|---|---|---|---|---|\n'


def body(item='Title', objective='Description', status='OPEN', annotation='', key='PT-01', struck=False):
    return (HEADER + f'| {"~~"+key+"~~" if struck else key} | {item} | `example` | {objective} | - | {status} | approved | inert |{annotation}\n').encode()


class Mapping(Review):
    def setUp(self):
        super().setUp()
        self.mapper=MappingClient(self.lab.container,'d5_writer')
        self.mreviewer=MappingClient(self.lab.container,'d5_reviewer')
        self.applier=MappingClient(self.lab.container,'d5_applier')
        self.mreader=MappingClient(self.lab.container)
        self.tid,self.tkey=uid(),uid()

    def command(self,action,**fields):
        return envelope(uid(),action,self.pid,self.doc,**fields)

    def send(self,req):
        return {'d5_writer':self.mapper,'d5_reviewer':self.mreviewer,'d5_applier':self.applier}[
            ENTRIES[req['action']][1]].submit_mapping(req)

    def intent(self,key='PT-01',tid=None,tkey=None,profile=PROFILE):
        req=self.command('REGISTER_TASK_INTENT',source_key=key,profile=profile,policy='d5.task-projection.v1',task_id=tid or self.tid,task_key=tkey or self.tkey)
        res=self.send(req)
        if res['status']=='OK':self.iid=res['intent_id']
        return req,res

    def stage(self,b=None,a=None,ref_version=None):
        b=body('Old') if b is None else b;a=body() if a is None else a
        _,br=self.ingest(self.capture(b,label='before'));_,ar=self.ingest(self.capture(a,label='after'))
        self.before,self.after=br['observation_id'],ar['observation_id'];self.profile=PROFILE
        self.cid=uid();self.client.compare(self.cid,self.pid,self.doc,self.before,self.after)
        self.report,self.digest=self.reader.recover_comparison(self.pid,self.doc,self.cid)
        self.items={i['source_key']:i for i in self.report['review_items']}
        v=self.head()['version'] if ref_version is None else ref_version
        self.assertEqual(self.writer.submit(self.select(self.before,v))['status'],'OK')
        self.refv=v+1

    def propose(self,key='PT-01',iid=None,accept_source=True):
        if accept_source:self.decide(key)
        req=self.command('PREPARE_TASK_PROPOSAL',intent_id=iid or self.iid,comparison_id=self.cid,
                         row_sha256=self.items.get(key,{}).get('row_sha256','0'*64),report_sha256=self.digest,expected_reference_version=self.refv)
        return req,self.send(req)

    def accept(self,p,version=0,decision='ACCEPT'):
        req=self.command('REVIEW_TASK_PROPOSAL',proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],
                         expected_version=version,decision=decision,reviewer_label='synthetic-reviewer',reason='Explicit whole manifest review')
        return req,self.send(req)

    def package(self,*proposals,accept=True):
        pins=[]
        for p in proposals:
            if accept:
                _,r=self.accept(p)
                pin=dict(proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],review_command_id=r['command_id'],review_version=r['version_at_commit'])
            else:
                h=self.mreader.artifact(self.pid,self.doc,'proposal',p['proposal_id'])
                pin={k:h[k] for k in ('proposal_id','manifest_sha256','review_command_id','review_version')}
                pin['review_command_id']=pin['review_command_id'] or uid()
            pins.append(pin)
        req=self.command('PACKAGE_TASK_PROPOSALS',items=sorted(pins,key=lambda x:x['proposal_id']))
        return req,self.send(req)

    def apply(self,package,cid=None):
        req=self.command('APPLY_TASK_PROPOSALS',package_sha256=package['package_sha256'])
        if cid:req['command_id']=cid
        return req,self.send(req)

    def create(self,b=None,a=None):
        self.stage(b,a);self.intent();_,p=self.propose();self.assertEqual(p['status'],'OK')
        _,pkg=self.package(p);req,res=self.apply(pkg);self.assertEqual(res['status'],'OK')
        return req,res

    def next_proposal(self,b=None,a=None):
        self.stage(body() if b is None else b,body('New') if a is None else a)
        return self.propose()

    def task(self,tid=None):
        return json.loads(self.scalar("SELECT to_jsonb(t) FROM public.tasks t WHERE id='"+(tid or self.tid)+"';"))

    def plan_fixture(self,pid,published=False):
        return f"""INSERT INTO public.planning_runs(id,horizon_start,horizon_end,trigger_type,config_snapshot,config_sha256,solver_version)
        VALUES('{pid}','2026-10-19','2026-10-26','SYNTHETIC','{{}}',repeat('0',64),'fixture');"""+(f"UPDATE public.planning_runs SET status='PUBLISHED' WHERE id='{pid}';" if published else '')

    def test_M01_registration_reserves_only(self):
        req,r=self.intent();self.assertEqual(r['status'],'OK');self.assertEqual(self.send(req),r)
        self.assertEqual(self.scalar(f"SELECT count(*) FROM public.tasks WHERE project_id='{self.pid}';"),'0')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM d5.task_destinations WHERE intent_id='{self.iid}';"),'0')
        doc2=uid();self.writer.submit(envelope(uid(),'REGISTER_SOURCE',self.pid,doc2,namespace='synthetic',logical_key='other-document'))
        scoped=dict(req,command_id=uid(),document_id=doc2,task_id=uid(),task_key=uid())
        self.assertEqual(self.send(scoped)['status'],'OK')

    def test_M02_scoped_identity_no_adoption(self):
        self.intent()
        for key,tid,tkey,profile in [('PT-01',uid(),uid(),PROFILE),('PT-02',self.tid,uid(),PROFILE),('PT-02',uid(),self.tkey,PROFILE),('PT-01',uid(),uid(),'task-register.v1')]:
            self.assertEqual(self.intent(key,tid,tkey,profile)[1]['code'],'IDENTITY_CONFLICT')
        req=self.command('REGISTER_TASK_INTENT',source_key='PT-02',profile=PROFILE,policy='d5.task-projection.v1',task_id=uid(),task_key=uid())
        self.assertEqual(self.send(dict(req,document_id=uid()))['code'],'SOURCE_SCOPE_CONFLICT')
        self.assertEqual(self.send(dict(req,command_id=uid(),project_id=uid()))['code'],'SOURCE_SCOPE_CONFLICT')
        tid=uid();self.lab.sql(f"INSERT INTO public.tasks(id,project_id,task_key,title) VALUES('{tid}','{self.pid}','occupied','Existing');")
        self.assertEqual(self.intent('PT-02',tid,uid())[1]['code'],'IDENTITY_CONFLICT')
        self.assertEqual(self.intent('PT-02',uid(),'occupied')[1]['code'],'IDENTITY_CONFLICT')

    def test_M03_literal_long_ID_unicode_markdown(self):
        key='LONG-'+'1'*5000;item='Árbol **literal** \\| `code`';objective='ñ [link](https://example.invalid)'
        self.stage(body('Old',key=key),body(item,objective,key=key,struck=True));self.intent(key)
        _,p=self.propose(key);self.assertEqual(p['manifest']['intent']['source_key'],key)
        _,pkg=self.package(p);self.assertEqual(self.apply(pkg)[1]['status'],'OK')
        self.assertEqual((self.task()['title'],self.task()['description']),(item,objective))

    def test_M04_empty_title_and_literal_descriptions(self):
        self.stage(a=body('   '));self.intent();_,p=self.propose();self.assertEqual(p['code'],'INVALID_PROJECTION')
        for description in ('','-'):
            self.stage(body(objective='') if description=='-' else body('Old'),body(objective=description))
            _,p=self.propose();_,pkg=self.package(p)
            self.assertEqual(self.apply(pkg)[1]['status'],'OK');self.assertEqual(self.task()['description'],description)

    def test_M05_source_claims_never_workflow(self):
        self.create(a=body(status='DONE',annotation=' verified and closed',struck=True))
        t=self.task();self.assertEqual((t['status'],t['row_version'],t['urgency'],t['deferred_count']),('BACKLOG',0,0,0))
        self.assertIsNone(t['epic_id']);self.assertIsNone(t['deadline_at'])
        self.assertEqual(self.scalar(f"SELECT count(*) FROM public.operations WHERE task_id='{self.tid}';"),'0')

    def test_M06_source_ACCEPT_not_task_authorization(self):
        self.stage();self.intent();_,d=self.decide();self.assertEqual(self.simulate([self.pin('PT-01',d)],self.refv)['status'],'OK')
        _,p=self.propose(accept_source=False);_,pkg=self.package(p,accept=False)
        self.assertEqual(pkg['code'],'MANIFEST_NOT_ACCEPTED')
        req=self.command('APPLY_TASK_PROPOSALS',package_sha256='0'*64)
        self.assertEqual(self.applier.query(mapping_sql(req))['code'],'PACKAGE_SCOPE_CONFLICT')

    def test_M07_manifest_tamper_is_not_review(self):
        self.stage();self.intent();_,p=self.propose();req,r=self.accept(p)
        tampered=dict(req,command_id=uid(),manifest_sha256='0'*64,expected_version=1)
        with self.assertRaises(ValueError):self.send(tampered)
        self.assertEqual(self.mreviewer.query(mapping_sql(tampered))['code'],'MANIFEST_SCOPE_CONFLICT')
        for field in ('task_id','task_key','policy','after_projection'):
            self.denied(mapping_sql(dict(req,command_id=uid(),**{field:'tampered'})),role='d5_reviewer')
        self.denied("UPDATE d5.task_proposals SET manifest=manifest||'{\"action\":\"PATCH_BACKLOG\"}';",role='d5_lab_admin')

    def test_M08_create_from_added_and_changed_atomic(self):
        for added in (True,False):
            if added:self.create(body(key='PT-99'),body())
            else:
                self.tid,self.tkey=uid(),uid();self.intent('PT-02');self.stage(body('Old',key='PT-02'),body(key='PT-02'))
                _,p=self.propose('PT-02');_,pkg=self.package(p);self.assertEqual(self.apply(pkg)[1]['status'],'OK')
            self.assertEqual(self.task()['row_version'],0)
            self.assertEqual(self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}';"),'1')
            self.assertEqual(self.scalar(f"SELECT count(*) FROM public.audit_events WHERE entity_id='{self.tid}' AND action='CREATE_BACKLOG';"),'1')

    def test_M09_patch_preserves_other_fields(self):
        self.create();old=self.task();self.lab.sql(f"UPDATE public.tasks SET urgency=3,deferred_count=2 WHERE id='{self.tid}';")
        _,p=self.next_proposal();self.assertEqual(p['manifest']['action'],'PATCH_BACKLOG');_,pkg=self.package(p)
        self.assertEqual(self.apply(pkg)[1]['status'],'OK');t=self.task()
        self.assertEqual((t['title'],t['row_version'],t['urgency'],t['deferred_count']),('New',1,3,2))
        self.assertEqual(t['created_at'],old['created_at']);self.assertEqual(self.scalar(f"SELECT count(*) FROM d5.task_applications a JOIN d5.task_packages p USING(package_sha256) WHERE p.document_id='{self.doc}' AND a.applied_at IS NOT NULL;"),'2')

    def test_M10_local_edit_even_without_version_bump(self):
        self.create();_,p=self.next_proposal();_,pkg=self.package(p)
        for version in ('row_version','row_version+1'):
            self.lab.sql(f"UPDATE public.tasks SET title='Local',row_version={version} WHERE id='{self.tid}';")
            self.assertEqual(self.apply(pkg)[1]['code'],'LOCAL_EDIT_CONFLICT')
            self.assertEqual(self.propose(accept_source=False)[1]['code'],'LOCAL_EDIT_CONFLICT')
        self.assertEqual(self.task()['title'],'Local')

    def test_M11_complete_target_CAS(self):
        self.create();_,p=self.next_proposal();_,pkg=self.package(p)
        self.lab.sql(f"UPDATE public.tasks SET urgency=4 WHERE id='{self.tid}';")
        self.assertEqual(self.apply(pkg)[1]['code'],'TARGET_CAS_CONFLICT');self.assertEqual(self.task()['title'],'Title')
        # A fresh prepare pins the unrelated local value and preserves it on PATCH.
        _,fresh=self.propose(accept_source=False);_,newpkg=self.package(fresh)
        self.assertEqual(self.apply(newpkg)[1]['status'],'OK');self.assertEqual(self.task()['urgency'],4)

    def test_M12_state_work_and_schedule_blocked(self):
        self.create();_,p=self.next_proposal();_,pkg=self.package(p)
        req=self.command('APPLY_TASK_PROPOSALS',package_sha256=pkg['package_sha256'])
        # These owner-only negative fixtures always roll back. Explicitly authorized.
        fixtures=[f"SELECT d2.transition('{uid()}','{json.dumps(dict(entity_type="TASK",entity_id=self.tid,expected_version=0,actor="fixture",reason="negative test",to="BLOCKED",**{"from":"BACKLOG"}))}'::jsonb);",
                  f"INSERT INTO public.operations(task_id,operation_type,idempotency_key) VALUES('{self.tid}','SYNTHETIC','{uid()}');"]
        plan=uid();fixtures.append(self.plan_fixture(plan)+f"INSERT INTO public.schedule_entries(planning_run_id,task_id,resource_id,pool,priority_snapshot) VALUES('{plan}','{self.tid}','{self.lab.resource}','PLANNED','{{}}');")
        for fixture in fixtures:
            r=self.lab.sql('BEGIN;'+fixture+"SET LOCAL ROLE d5_applier;"+mapping_sql(dict(req,command_id=uid()))+'ROLLBACK;',check=False)
            self.assertEqual(r.returncode,0,r.stderr)
            value=json.loads(r.stdout.strip().splitlines()[-1]);self.assertEqual(value['code'],'TARGET_HAS_WORK_OR_STATE')
        self.assertEqual(self.scalar('SELECT count(*) FROM public.operations;'),'0');self.assertEqual(self.task()['status'],'BACKLOG')

    def test_M13_unmapped_changes_append_evidence_only(self):
        self.create();old=self.task();self.stage(body(),body(status='DONE',annotation=' source claim'))
        _,p=self.propose();self.assertEqual(p['manifest']['action'],'LINK_SOURCE_EVIDENCE')
        _,pkg=self.package(p);self.assertEqual(self.apply(pkg)[1]['status'],'OK');self.assertEqual(self.task(),old)
        self.assertEqual(self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}';"),'2')

    def test_M14_absence_preserves_identity_base_links(self):
        self.create();old=self.task();links=self.scalar(f"SELECT jsonb_agg(to_jsonb(s)) FROM d2.task_sources s WHERE task_id='{self.tid}';")
        self.stage(body(),body(key='PT-99'));_,p=self.propose();_,pkg=self.package(p)
        oldbase=self.scalar(f"SELECT source_basis FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';")
        self.assertEqual(self.apply(pkg)[1]['status'],'OK');self.assertEqual(self.task(),old)
        self.assertEqual(self.scalar(f"SELECT source_basis FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';"),oldbase)
        self.assertEqual(self.scalar(f"SELECT jsonb_agg(to_jsonb(s)) FROM d2.task_sources s WHERE task_id='{self.tid}';"),links)
        self.tid,self.tkey=uid(),uid();self.intent('PT-02');self.stage(body(key='PT-02'),body(key='PT-99'))
        _,p=self.propose('PT-02');_,pkg=self.package(p);self.assertEqual(self.apply(pkg)[1]['status'],'OK')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM public.tasks WHERE id='{self.tid}';"),'0')

    def test_M15_reappearance_and_unchanged_bootstrap_blocked(self):
        self.create();self.stage(body(key='PT-99'),body());self.assertEqual(self.propose()[1]['code'],'REAPPEARANCE_REVIEW_REQUIRED')
        self.stage(body(),body());self.assertEqual(self.propose(accept_source=False)[1]['code'],'NO_CHANGED_ROW_NO_BOOTSTRAP')

    def test_M16_new_before_observation_same_semantics(self):
        self.create();self.stage(b'\n\n'+body(),body('New'));_,p=self.propose();_,pkg=self.package(p)
        self.assertEqual(self.apply(pkg)[1]['status'],'OK');self.assertEqual(self.task()['title'],'New')

    def test_M17_semantic_base_not_title_only(self):
        self.create();self.stage(body(status='DONE'),body('New'))
        self.assertEqual(self.propose()[1]['code'],'SOURCE_BASE_CONFLICT');self.assertEqual(self.task()['title'],'Title')

    def test_M18_reference_review_and_mapping_ABA(self):
        self.stage();self.intent();_,p=self.propose();_,pkg=self.package(p)
        self.writer.submit(self.select(self.after,self.refv));self.writer.submit(self.select(self.before,self.refv+1))
        self.assertEqual(self.apply(pkg)[1]['code'],'REFERENCE_VERSION_CONFLICT')
        self.refv+=2;_,p2=self.propose(accept_source=False);_,pkg2=self.package(p2)
        self.accept(p2,1,'REJECT');self.accept(p2,2,'ACCEPT')
        self.assertEqual(self.apply(pkg2)[1]['code'],'MANIFEST_REVIEW_CONFLICT')
        _,pkg3=self.package(p2,accept=False)
        self.decide(decision='REJECT',version=1);self.decide(version=2)
        self.assertEqual(self.apply(pkg3)[1]['code'],'SOURCE_REVIEW_CONFLICT')
        _,fresh=self.propose(accept_source=False);_,ok=self.package(fresh);self.assertEqual(self.apply(ok)[1]['status'],'OK')
        self.assertEqual(self.apply(pkg3)[1]['code'],'INTENT_VERSION_CONFLICT')

    def test_M19_scoped_append_only_provenance(self):
        self.create();old=self.scalar(f"SELECT to_jsonb(s) FROM d2.task_sources s WHERE task_id='{self.tid}';")
        link=json.loads(old);self.assertTrue(link['source_locator'].startswith('sha256:'))
        self.denied(f"UPDATE d2.task_sources SET source_locator='forged' WHERE task_id='{self.tid}';",role='d5_lab_admin')
        self.denied(f"INSERT INTO d2.task_sources VALUES('{self.tid}','{link['revision_id']}','forged','{self.doc}','{uid()}');",role='d5_lab_admin')
        # Exact duplicate link already present: verified reuse, not another fact.
        self.stage(body(),body(status='DONE'));_,p=self.propose();m=p['manifest']
        self.lab.sql(f"INSERT INTO d2.task_sources VALUES('{self.tid}','{m['after_revision_id']}',"+sql_text(m['source_change']['after']['row']['source_locator'])+f",'{self.doc}','{self.pid}');")
        _,pkg=self.package(p);self.assertEqual(self.apply(pkg)[1]['status'],'OK')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}';"),'2')

    def test_M20_replay_and_single_package_effect(self):
        req,r=self.create();old=self.task();self.assertEqual(self.send(req),r)
        self.assertEqual(self.send(dict(req,command_id=uid()))['status'],'ALREADY_APPLIED');self.assertEqual(self.task(),old)
        self.lab.sql(f"UPDATE public.tasks SET urgency=2 WHERE id='{self.tid}';")
        self.assertEqual(self.send(req),r);self.assertEqual(self.task()['urgency'],2)

    def test_M21_real_concurrent_application_and_target_race(self):
        self.stage();self.intent();_,p=self.propose();_,pkg=self.package(p)
        req=self.command('APPLY_TASK_PROPOSALS',package_sha256=pkg['package_sha256'])
        results=self.lab.concurrent([mapping_sql(req),mapping_sql(dict(req,command_id=uid()))],role='d5_applier')
        self.assertEqual(sorted(r['status'] for r in results),['ALREADY_APPLIED','OK'])
        # Distinct immutable packages compete against the same mapped base.
        _,p1=self.next_proposal();_,p2=self.propose(accept_source=False)
        _,pack1=self.package(p1);_,pack2=self.package(p2)
        commands=[self.command('APPLY_TASK_PROPOSALS',package_sha256=x['package_sha256']) for x in (pack1,pack2)]
        results=self.lab.concurrent([mapping_sql(r) for r in commands],role='d5_applier')
        self.assertEqual(sorted(r['status'] for r in results),['CONFLICT','OK'])
        self.assertEqual(next(r for r in results if r['status']=='CONFLICT')['code'],'INTENT_VERSION_CONFLICT')
        self.tid,self.tkey=uid(),uid();self.intent('PT-02');self.stage(body('Old',key='PT-02'),body(key='PT-02'))
        _,p=self.propose('PT-02');_,pkg=self.package(p)
        self.lab.sql(f"INSERT INTO public.tasks(project_id,task_key,title) VALUES('{self.pid}','{self.tkey}','Occupied after prepare');")
        self.assertEqual(self.apply(pkg)[1]['code'],'TARGET_OCCUPIED')

    def test_M22_all_or_nothing_and_real_transaction_abort(self):
        self.stage(body('Old'),body());self.intent();_,p=self.propose();_,pkg=self.package(p)
        req=self.command('APPLY_TASK_PROPOSALS',package_sha256=pkg['package_sha256'])
        before=self.lab.protected_state();self.lab.abort_after(mapping_sql(req))
        self.assertEqual(self.lab.protected_state(),before);self.assertIsNone(self.reader.read_command(req['command_id']))
        self.assertEqual(self.scalar(f"SELECT version FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';"),'0')
        # Two explicit valid manifests, one revoked before APPLY => zero task effects.
        other=uid();otherkey=uid();_,i=self.intent('PT-02',other,otherkey)
        combined=body()+f'| PT-02 | Second | x | More | - | OPEN | no | inert |\n'.encode()
        self.stage(body('Old')+b'| PT-02 | Old second | x | Old | - | OPEN | no | inert |\n',combined)
        first_i=p['manifest']['intent']['intent_id'];_,p1=self.propose(iid=first_i);_,p2=self.propose('PT-02',iid=i['intent_id']);_,both=self.package(p1,p2)
        self.accept(p2,1,'REJECT');before=self.lab.protected_state()
        self.assertEqual(self.apply(both)[1]['code'],'MANIFEST_REVIEW_CONFLICT');self.assertEqual(self.lab.protected_state(),before)

    def test_M23_lost_response_restart_and_CLI_recovery(self):
        self.stage();self.intent();_,p=self.propose();_,pkg=self.package(p)
        req=self.command('APPLY_TASK_PROPOSALS',package_sha256=pkg['package_sha256'])
        # The first process commits; its stdout is intentionally discarded.
        self.lab.sql(mapping_sql(req),role='d5_applier');self.lab.restart()
        r=self.reader.read_command(req['command_id']);self.assertEqual(self.send(req),r)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'request.json';path.write_text(json.dumps(req))
            cli=subprocess.run([sys.executable,'-m','source_ingest.task_mapping','--container',self.lab.container,'--request',str(path)],capture_output=True,text=True)
            self.assertEqual(cli.returncode,0,cli.stderr);self.assertEqual(json.loads(cli.stdout),r)
        self.assertEqual(self.task()['row_version'],0)

    def test_M24_lock_order_cross_sessions(self):
        self.stage();self.intent();_,p=self.propose();_,pkg=self.package(p)
        req=self.command('APPLY_TASK_PROPOSALS',package_sha256=pkg['package_sha256'])
        blocker=self.lab.session('BEGIN;SELECT pg_advisory_xact_lock(742001);SELECT pg_sleep(60);ROLLBACK;','d5_boundary')
        self.lab.wait_for(lambda:self.lab.active('d5_boundary','PgSleep')==1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(self.lab.sql,mapping_sql(req),'d5_applier')
                self.lab.wait_for(lambda:int(self.scalar("SELECT count(*) FROM pg_stat_activity WHERE usename='d5_applier' AND wait_event='advisory';"))==1)
                # APPLY waiting at D3 has NOT taken the D5 mutex: source-only work finishes.
                self.assertEqual(self.writer.submit(self.select(self.before,self.refv))['status'],'OK')
                self.lab.terminate('d5_boundary');r=json.loads(future.result(timeout=30).stdout)
                self.assertEqual(r['code'],'REFERENCE_VERSION_CONFLICT')
        finally:self.lab.terminate('d5_boundary');blocker.communicate(timeout=5)
        blocker=self.lab.session('BEGIN;SELECT pg_advisory_xact_lock(742005);SELECT pg_sleep(60);ROLLBACK;','d5_boundary')
        self.lab.wait_for(lambda:self.lab.active('d5_boundary','PgSleep')==1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(self.lab.sql,mapping_sql(dict(req,command_id=uid())),'d5_applier')
                self.lab.wait_for(lambda:int(self.scalar("SELECT count(*) FROM pg_stat_activity WHERE usename='d5_applier' AND wait_event='advisory';"))==1)
                held=self.scalar("SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a ON a.pid=l.pid WHERE a.usename='d5_applier' AND l.locktype='advisory' AND l.granted AND l.objid IN (742001,742002);")
                self.assertEqual(held,'2')
                capture_id=uid()
                capture=self.lab.session(f"SELECT d3.capture('{capture_id}','{{\"action\":\"CAPTURE\"}}');",'d5_cross_capture')
                self.lab.wait_for(lambda:self.lab.active('d5_cross_capture','advisory')==1)
                self.lab.terminate('d5_boundary');future.result(timeout=30)
                output,error=capture.communicate(timeout=10)
                self.assertEqual(capture.returncode,0,error);self.assertEqual(json.loads(output)['capture_id'],capture_id)
        finally:self.lab.terminate('d5_boundary');blocker.communicate(timeout=5)

    def test_M25_roles_boundary_and_no_generic_authority(self):
        req=self.command('APPLY_TASK_PROPOSALS',package_sha256='0'*64)
        for role in ('d5_writer','d5_reviewer','d5_reader'):
            self.denied(mapping_sql(req),role);self.denied('SELECT d5.task_lock_boundary();',role)
            self.denied("INSERT INTO public.tasks(project_id,task_key,title) VALUES(NULL,'bad','bad');",role)
        self.denied('SELECT d5.task_lock_boundary();','d5_applier')
        self.denied('SELECT d3.lock_state();','d5_applier');self.denied('SET ROLE d5_apply_owner; SELECT d3.lock_state();','d5_lab_admin')
        self.denied('DELETE FROM d5.task_mapping_heads;','d5_applier')
        self.denied("INSERT INTO public.tasks(project_id,task_key,title) VALUES(NULL,'bad','bad');",'d5_applier')
        self.denied("UPDATE public.tasks SET title='bad';",'d5_applier')
        self.assertEqual(self.applier.query(mapping_sql(req))['code'],'PACKAGE_SCOPE_CONFLICT')
        self.assertEqual(self.scalar("SELECT has_schema_privilege('d5_apply_owner','d3','USAGE') OR has_schema_privilege('d5_apply_owner','d4','USAGE');"),'f')
        self.assertEqual(self.scalar("SELECT rolcanlogin FROM pg_roles WHERE rolname='d5_apply_owner';"),'f')
        self.assertEqual(self.scalar("SELECT pg_get_userbyid(proowner) FROM pg_proc WHERE oid='d5.task_lock_boundary()'::regprocedure;"),'d5_lab_admin')

    def test_M26_D3_basis_stale_published_snapshot_immutable(self):
        # Owner-only historical published fixture; no d3.publish, outbox or dispatch.
        plan=uid();self.lab.sql(self.plan_fixture(plan,True))
        snapshot=self.scalar(f"SELECT to_jsonb(p) FROM public.planning_runs p WHERE id='{plan}';")
        capture=uid();self.lab.sql(f"SELECT d3.capture('{capture}','{{\"action\":\"CAPTURE\"}}');")
        before=self.scalar("SELECT encode(public.digest(d3.state_body()::text,'sha256'),'hex');")
        self.create();after=self.scalar("SELECT encode(public.digest(d3.state_body()::text,'sha256'),'hex');");self.assertNotEqual(before,after)
        _,p=self.next_proposal();_,pkg=self.package(p);self.apply(pkg)
        self.assertNotEqual(after,self.scalar("SELECT encode(public.digest(d3.state_body()::text,'sha256'),'hex');"))
        self.assertEqual(self.scalar(f"SELECT to_jsonb(p) FROM public.planning_runs p WHERE id='{plan}';"),snapshot)
        self.denied(f"UPDATE public.planning_runs SET solver_version='modified' WHERE id='{plan}';",role='d5_lab_admin')

    def test_M27_eligibility_is_not_activation(self):
        self.create();self.assertEqual(self.scalar(f"SELECT d2.task_eligible('{self.tid}');"),'t')
        for table in ('public.operations','public.outbox_events','public.execution_attempts','d2.reservations','d2.plan_reservations'):
            self.assertEqual(self.scalar(f'SELECT count(*) FROM {table};'),'0')
        self.assertEqual(self.task()['status'],'BACKLOG')
