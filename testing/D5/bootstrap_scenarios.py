# SPDX-License-Identifier: GPL-3.0-only
"""B01-B28: initial import and continuity, with only synthetic BACKLOG effects."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from .mapping_scenarios import Mapping, body
from .postgres_scenarios import uid, PROFILE
from source_ingest.bootstrap import BootstrapClient, ENTRIES, bootstrap_sql
from source_ingest.postgres import sql_text
from source_ingest.preview import canonical
from source_ingest.task_mapping import mapping_sql


class Bootstrap(Mapping):
    def setUp(self):
        super().setUp()
        self.bwriter=BootstrapClient(self.lab.container,'d5_writer')
        self.breviewer=BootstrapClient(self.lab.container,'d5_reviewer')
        self.breader=BootstrapClient(self.lab.container)
        self.bapplier=BootstrapClient(self.lab.container,'d5_applier')

    def bsend(self,req,artifact=None):
        client={'d5_writer':self.bwriter,'d5_reviewer':self.breviewer,'d5_applier':self.bapplier}[ENTRIES[req['action']][1]]
        return client.submit_bootstrap(req,artifact)

    def initial(self,data=None,key='PT-01',select=True,register=True,profile=PROFILE):
        self.snapshot=self.capture(body() if data is None else data,profile=profile)
        _,r=self.ingest(self.snapshot);self.oid=r['observation_id'];self.ph=r['preview_sha256'];self.profile=profile
        if register:self.intent(key,profile=profile)
        self.refv=self.head(profile)['version']
        if select:
            self.refv=self.writer.submit(self.select(self.oid,self.refv,profile=profile))['version_at_commit']
        return r

    def brequest(self,key='PT-01',iid=None):
        row=next((r for r in self.snapshot['proposals'] if r['source_key']==key),None);payload=canonical(row)
        return self.command('PREPARE_BOOTSTRAP_TASK',intent_id=iid or self.iid,source_key=key,observation_id=self.oid,
                            content_sha256=self.snapshot['content_sha256'],preview_sha256=self.ph,
                            snapshot_row_sha256=hashlib.sha256(payload).hexdigest(),expected_reference_version=self.refv),payload

    def bpropose(self,key='PT-01',iid=None):
        req,payload=self.brequest(key,iid)
        return req,self.bsend(req,payload)

    def baccept(self,p,version=0,decision='ACCEPT'):
        req=self.command('REVIEW_BOOTSTRAP_TASK',proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],
                         expected_version=version,decision=decision,reviewer_label='synthetic-reviewer',reason='Review initial row and complete target manifest')
        return req,self.bsend(req)

    def bpackage(self,*proposals,accept=True):
        pins=[]
        for p in proposals:
            if accept:
                _,r=self.baccept(p)
                pin=dict(proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],review_command_id=r['command_id'],review_version=r['version_at_commit'])
            else:
                h=self.breader.artifact(self.pid,self.doc,'proposal',p['proposal_id'])
                pin={k:h[k] for k in ('proposal_id','manifest_sha256','review_command_id','review_version')}
                pin['review_command_id']=pin['review_command_id'] or uid()
            pins.append(pin)
        req=self.command('PACKAGE_BOOTSTRAP_TASKS',items=sorted(pins,key=lambda x:x['proposal_id']))
        return req,self.bsend(req)

    def bapply(self,pkg):
        req=self.command('APPLY_BOOTSTRAP_TASKS',package_sha256=pkg['package_sha256'])
        return req,self.bsend(req)

    def bcreate(self,data=None):
        self.initial(data);_,p=self.bpropose();self.assertEqual(p['status'],'OK');_,pkg=self.bpackage(p)
        req,r=self.bapply(pkg);self.assertEqual(r['status'],'OK')
        return req,r

    def test_B01_prepare_without_task(self):
        self.initial();before=self.lab.protected_state();req,p=self.bpropose()
        self.assertEqual(p['status'],'OK');self.assertEqual(self.bsend(req),p)
        self.assertEqual(p['manifest']['mode'],'BOOTSTRAP_INITIAL');self.assertEqual(self.lab.protected_state(),before)
        self.assertEqual(p['manifest']['snapshot_row'],self.snapshot['proposals'][0])
        self.assertEqual(self.scalar(f"SELECT version FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';"),'0')

    def test_B02_identity_scope_profile_and_occupied_target(self):
        self.initial();req,payload=self.brequest()
        for extra in (dict(intent_id=uid()),dict(project_id=uid()),dict(document_id=uid()),dict(source_key='PT-02')):
            r=self.bwriter.query(bootstrap_sql(dict(req,command_id=uid(),**extra),payload));self.assertEqual(r['code'],'INTENT_SCOPE_CONFLICT')
        self.lab.sql(f"INSERT INTO public.tasks(project_id,task_key,title) VALUES('{self.pid}','{self.tkey}','Occupied');")
        self.assertEqual(self.bpropose()[1]['code'],'TARGET_OCCUPIED')
        self.tid,self.tkey=uid(),uid();self.intent('PT-02',profile='task-register.v1')
        self.assertEqual(self.bwriter.query(bootstrap_sql(dict(req,command_id=uid(),intent_id=self.iid,source_key='PT-02'),payload))['code'],'OBSERVATION_SCOPE_CONFLICT')

    def test_B03_noninitial_and_absence_history_rejected(self):
        self.bcreate();self.assertEqual(self.bpropose()[1]['code'],'INITIAL_INTENT_REQUIRED')
        self.tid,self.tkey=uid(),uid();self.intent('PT-02');self.stage(body(key='PT-02'),body(key='PT-99'))
        _,p=self.propose('PT-02');_,pkg=self.package(p);self.apply(pkg)
        self.initial(body(key='PT-02'),key='PT-02',register=False)
        self.assertEqual(self.bpropose('PT-02')[1]['code'],'INITIAL_INTENT_REQUIRED')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM public.tasks WHERE id='{self.tid}';"),'0')

    def test_B04_long_ID_literal_text_and_annotation(self):
        key='LONG-'+'1'*5000;text='Árbol **raw** \\| `literal`'
        self.initial(body(text,'ñ [x](https://example.invalid)',annotation=' verified claim',key=key,struck=True),key)
        _,p=self.bpropose(key);_,pkg=self.bpackage(p);self.assertEqual(self.bapply(pkg)[1]['status'],'OK')
        self.assertEqual(self.task()['title'],text);self.assertTrue(p['manifest']['snapshot_row']['source_struck'])
        self.assertIn('verified claim',p['manifest']['snapshot_row']['source_annotation']['text'])
        self.assertEqual(p['manifest']['intent']['source_key'],key)

    def test_B05_blocking_diagnostics_outside_selection(self):
        for data in (body()+b'| PT-99 | x | c | x | - | OPEN | no | inert |\n| PT-99 | y | c | y | - | OPEN | no | inert |\n',
                     body()+b'| PT-99 | ambiguous | row |\n'):
            self.initial(data,register=not hasattr(self,'iid'));req,payload=self.brequest()
            with self.assertRaises(ValueError):self.bsend(req)
            self.assertEqual(self.bwriter.query(bootstrap_sql(req,payload))['code'],'OBSERVATION_BLOCKED')

    def test_B06_projection_and_nonblocking_compatibility(self):
        self.initial(body('   '));self.assertEqual(self.bpropose()[1]['code'],'INVALID_PROJECTION')
        for description in ('','-'):
            self.initial(body(objective=description,annotation=' source claim'),register=False)
            _,p=self.bpropose();self.assertEqual(p['manifest']['projection']['description'],description)
        _,pkg=self.bpackage(p);self.assertEqual(self.bapply(pkg)[1]['status'],'OK');self.assertEqual(self.task()['description'],'-')

    def test_B07_selection_missing_duplicates_empty_and_limits(self):
        self.initial();req,payload=self.brequest();missing=dict(req,command_id=uid(),source_key='PT-02')
        with self.assertRaises(ValueError):self.bsend(missing)
        _,p=self.bpropose();preq,pkg=self.bpackage(p)
        for items in ([],preq['items']*2,preq['items']*2001):
            self.denied(bootstrap_sql(dict(preq,command_id=uid(),items=items)))
        with self.assertRaises(ValueError):bootstrap_sql(req,b'x'*2097153)
        bad=dict(preq,command_id=uid(),items=[dict(preq['items'][0],proposal_id=uid())])
        self.assertEqual(self.bwriter.query(bootstrap_sql(bad))['code'],'MANIFEST_SCOPE_CONFLICT')

    def test_B08_only_explicit_rows_materialize(self):
        self.bcreate(body()+b'| PT-02 | | x | Not selected | - | DONE | approved | inert |\n')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM public.tasks WHERE project_id='{self.pid}';"),'1')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM d5.task_intents WHERE document_id='{self.doc}';"),'1')

    def test_B09_comparison_and_I8_ACCEPT_do_not_authorize(self):
        self.stage();self.intent();_,p=self.propose();self.accept(p)
        self.snapshot=self.capture(body('Old'),label='before');self.oid=self.before
        self.ph=self.report['observations']['before']['preview_sha256']
        _,b=self.bpropose();_,pkg=self.bpackage(b,accept=False);self.assertEqual(pkg['code'],'MANIFEST_NOT_ACCEPTED')
        self.assertNotIn('comparison_id',b['manifest']);self.assertNotIn('source_decision_command_id',b['manifest'])
        self.denied(bootstrap_sql(dict(self.brequest()[0],comparison_id=self.cid),self.brequest()[1]))

    def test_B10_reconstruction_and_SQL_binding(self):
        self.initial();req,payload=self.brequest()
        for extra in (dict(content_sha256='0'*64),dict(preview_sha256='0'*64),dict(snapshot_row_sha256='0'*64)):
            with self.assertRaises(ValueError):self.bsend(dict(req,**extra))
        forged=json.loads(payload);forged['fields']['status']='FORGED';raw=canonical(forged)
        bad=dict(req,command_id=uid(),snapshot_row_sha256=hashlib.sha256(raw).hexdigest())
        self.assertEqual(self.bwriter.query(bootstrap_sql(bad,raw))['code'],'SNAPSHOT_ROW_CONFLICT')
        self.denied(bootstrap_sql(dict(req,command_id=uid()),b'{}'))
        self.assertIsNone(self.reader.read_command(req['command_id']))

    def test_B11_manifest_and_acceptance_cannot_be_transferred(self):
        self.initial();_,p=self.bpropose();req,r=self.baccept(p)
        bad=dict(req,command_id=uid(),manifest_sha256='0'*64,expected_version=1)
        with self.assertRaises(ValueError):self.bsend(bad)
        self.assertEqual(self.breviewer.query(bootstrap_sql(bad))['code'],'MANIFEST_SCOPE_CONFLICT')
        for field in ('task_id','task_key','policy','observation_id','projection'):
            self.denied(bootstrap_sql(dict(req,command_id=uid(),**{field:'changed'})),role='d5_reviewer')
        self.denied("UPDATE d5.bootstrap_proposals SET manifest=manifest||'{\"mode\":\"ADDED\"}';",role='d5_lab_admin')

    def test_B12_review_versions_and_ABA(self):
        self.initial();_,p=self.bpropose();self.assertEqual(self.bpackage(p,accept=False)[1]['code'],'MANIFEST_NOT_ACCEPTED')
        _,pkg=self.bpackage(p);self.baccept(p,1,'REJECT');self.baccept(p,2,'ACCEPT')
        self.assertEqual(self.bapply(pkg)[1]['code'],'BOOTSTRAP_REVIEW_CONFLICT')
        self.assertEqual(self.baccept(p,0)[1]['code'],'REVIEW_VERSION_CONFLICT')
        _,fresh=self.bpackage(p,accept=False);self.assertEqual(self.bapply(fresh)[1]['status'],'OK')

    def test_B13_reference_version_identity_and_ABA(self):
        self.initial(select=False);self.assertEqual(self.bpropose()[1]['code'],'REFERENCE_VERSION_CONFLICT')
        self.refv=self.writer.submit(self.select(self.oid,0))['version_at_commit'];_,p=self.bpropose();_,pkg=self.bpackage(p)
        _,same=self.ingest(self.capture(body(),label='another-label'))
        self.writer.submit(self.select(same['observation_id'],1));self.assertEqual(self.bapply(pkg)[1]['code'],'REFERENCE_VERSION_CONFLICT')
        self.writer.submit(self.select(self.oid,2));self.assertEqual(self.bapply(pkg)[1]['code'],'REFERENCE_VERSION_CONFLICT')

    def test_B14_package_exact_list_and_no_variant_mixing(self):
        self.initial();_,p=self.bpropose();_,p2=self.bpropose();_,r=self.baccept(p2)
        req,pkg=self.bpackage(p)
        self.assertEqual(self.bsend(dict(req,command_id=uid()))['package_sha256'],pkg['package_sha256'])
        pin2=dict(proposal_id=p2['proposal_id'],manifest_sha256=p2['manifest_sha256'],review_command_id=r['command_id'],review_version=1)
        self.denied(bootstrap_sql(dict(req,command_id=uid(),items=sorted(req['items']+[pin2],key=lambda p:p['proposal_id']))))
        # The old I8 package API rejects bootstrap proposals rather than accepting null comparison pins.
        mixed=dict(req,command_id=uid(),action='PACKAGE_TASK_PROPOSALS')
        self.assertEqual(self.mapper.query(mapping_sql(mixed))['code'],'MANIFEST_SCOPE_CONFLICT')

    def test_B15_source_claims_create_only_BACKLOG_defaults(self):
        self.bcreate(body(status='DONE',annotation=' approved and closed',struck=True));t=self.task()
        self.assertEqual((t['status'],t['row_version'],t['urgency'],t['deferred_count']),('BACKLOG',0,0,0))
        self.assertIsNone(t['deadline_at']);self.assertIsNone(t['epic_id'])

    def test_B16_atomic_scoped_provenance_and_initial_base(self):
        self.bcreate();link=json.loads(self.scalar(f"SELECT to_jsonb(s) FROM d2.task_sources s WHERE task_id='{self.tid}';"))
        self.assertEqual(link['source_locator'],self.snapshot['proposals'][0]['source_locator']);self.assertEqual(link['document_id'],self.doc)
        self.assertEqual(link['project_id'],self.pid)
        self.assertEqual(self.scalar(f"SELECT version FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';"),'1')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM public.audit_events WHERE entity_id='{self.tid}' AND action='CREATE_INITIAL_BACKLOG';"),'1')
        self.denied(f"INSERT INTO d2.task_sources VALUES('{self.tid}','{link['revision_id']}','forged','{self.doc}','{uid()}');",role='d5_lab_admin')
        self.denied(f"DELETE FROM d2.task_sources WHERE task_id='{self.tid}';",role='d5_lab_admin')

    def test_B17_continuity_PATCH_evidence_and_absence_through_I8(self):
        self.bcreate();_,p=self.next_proposal();_,pkg=self.package(p);self.assertEqual(self.apply(pkg)[1]['status'],'OK')
        self.assertEqual(self.task()['title'],'New');self.assertEqual(self.task()['row_version'],1)
        self.stage(body('New'),body('New',status='DONE'));_,p=self.propose();_,pkg=self.package(p);self.apply(pkg)
        self.assertEqual(p['manifest']['action'],'LINK_SOURCE_EVIDENCE');old=self.task()
        self.stage(body('New',status='DONE'),body(key='PT-99'));_,p=self.propose();_,pkg=self.package(p);self.apply(pkg)
        self.assertEqual(self.task(),old);self.assertEqual(p['manifest']['action'],'KEEP_EXISTING_NO_DELETE')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}';"),'3')

    def test_B18_continuity_preserves_conflict_guards(self):
        self.bcreate();self.stage(body(status='DONE'),body('New'));self.assertEqual(self.propose()[1]['code'],'SOURCE_BASE_CONFLICT')
        _,p=self.next_proposal();_,pkg=self.package(p);self.lab.sql(f"UPDATE public.tasks SET urgency=2 WHERE id='{self.tid}';")
        self.assertEqual(self.apply(pkg)[1]['code'],'TARGET_CAS_CONFLICT')
        _,p=self.propose(accept_source=False);_,pkg=self.package(p);self.lab.sql(f"UPDATE public.tasks SET title='Local' WHERE id='{self.tid}';")
        self.assertEqual(self.apply(pkg)[1]['code'],'LOCAL_EDIT_CONFLICT');self.assertEqual(self.propose(accept_source=False)[1]['code'],'LOCAL_EDIT_CONFLICT')

    def test_B19_no_head_cursor_or_unrelated_table_changes(self):
        self.initial();head=self.head();before=self.lab.protected_state();_,p=self.bpropose();_,pkg=self.bpackage(p);self.bapply(pkg)
        after=self.lab.protected_state();allowed={'public.tasks','d2.task_sources','public.audit_events'}
        self.assertEqual({k:v for k,v in before.items() if k not in allowed},{k:v for k,v in after.items() if k not in allowed})
        self.assertEqual(self.head(),head)

    def test_B20_replay_global_commands_and_single_effect(self):
        req,r=self.bcreate();self.lab.sql(f"UPDATE public.tasks SET urgency=2 WHERE id='{self.tid}';")
        self.assertEqual(self.bsend(req),r);self.assertEqual(self.bsend(dict(req,command_id=uid()))['status'],'ALREADY_APPLIED')
        self.assertEqual(self.task()['urgency'],2)
        bad=dict(req,package_sha256='0'*64);self.assertEqual(self.bapplier.query(bootstrap_sql(bad))['code'],'COMMAND_CONTENT_CONFLICT')
        cross=self.command('APPLY_TASK_PROPOSALS',package_sha256='0'*64);cross['command_id']=req['command_id']
        self.assertEqual(self.applier.query(mapping_sql(cross))['code'],'COMMAND_CONTENT_CONFLICT')

    def test_B21_other_package_and_new_rows_do_not_reimport(self):
        self.initial();_,p1=self.bpropose();_,p2=self.bpropose();_,pkg1=self.bpackage(p1);_,pkg2=self.bpackage(p2)
        self.ingest(self.capture(body()+b'| PT-02 | New row | x | x | - | OPEN | no | inert |\n',label='later'))
        self.assertEqual(self.bapply(pkg1)[1]['status'],'OK');self.assertEqual(self.bapply(pkg2)[1]['code'],'INITIAL_INTENT_REQUIRED')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM public.tasks WHERE project_id='{self.pid}';"),'1')

    def test_B22_real_concurrency_bootstrap_and_I8(self):
        self.initial();_,p1=self.bpropose();_,p2=self.bpropose();_,pkg1=self.bpackage(p1);_,pkg2=self.bpackage(p2)
        commands=[self.command('APPLY_BOOTSTRAP_TASKS',package_sha256=p['package_sha256']) for p in (pkg1,pkg2)]
        result=self.lab.concurrent([bootstrap_sql(r) for r in commands],role='d5_applier')
        self.assertEqual(sorted(r['status'] for r in result),['CONFLICT','OK'])
        self.tid,self.tkey=uid(),uid();self.initial(body(key='PT-02'),key='PT-02');_,bp=self.bpropose('PT-02');_,bpkg=self.bpackage(bp)
        _,ar=self.ingest(self.capture(body('New',key='PT-02'),label='after'))
        self.before,self.after=self.oid,ar['observation_id'];self.cid=uid();self.client.compare(self.cid,self.pid,self.doc,self.before,self.after)
        self.report,self.digest=self.reader.recover_comparison(self.pid,self.doc,self.cid);self.items={i['source_key']:i for i in self.report['review_items']}
        _,p=self.propose('PT-02');_,pkg=self.package(p)
        b=self.command('APPLY_BOOTSTRAP_TASKS',package_sha256=bpkg['package_sha256']);m=self.command('APPLY_TASK_PROPOSALS',package_sha256=pkg['package_sha256'])
        result=self.lab.concurrent([bootstrap_sql(b),mapping_sql(m)],role='d5_applier')
        self.assertEqual(sorted(r['status'] for r in result),['CONFLICT','OK'])
        self.assertEqual(self.scalar(f"SELECT count(*) FROM public.tasks WHERE project_id='{self.pid}';"),'2')

    def test_B23_key_race_mixed_package_atomic_conflict(self):
        self.initial(body()+b'| PT-02 | Second | x | x | - | OPEN | no | inert |\n');first=self.iid
        self.intent('PT-02',uid(),'occupied-later');second=self.iid
        _,p1=self.bpropose(iid=first);_,p2=self.bpropose('PT-02',second);_,pkg=self.bpackage(p1,p2)
        self.lab.sql(f"INSERT INTO public.tasks(project_id,task_key,title) VALUES('{self.pid}','occupied-later','Preexisting');")
        before=self.lab.protected_state();req,r=self.bapply(pkg);self.assertEqual(r['code'],'TARGET_OCCUPIED')
        self.assertEqual(self.lab.protected_state(),before);self.assertEqual(self.reader.read_command(req['command_id']),r)

    def test_B24_backend_abort_and_structural_failure_after_insert(self):
        self.initial();_,p=self.bpropose();_,pkg=self.bpackage(p);req=self.command('APPLY_BOOTSTRAP_TASKS',package_sha256=pkg['package_sha256'])
        before=self.lab.protected_state();self.lab.abort_after(bootstrap_sql(req));self.assertEqual(self.lab.protected_state(),before)
        self.assertIsNone(self.reader.read_command(req['command_id']))
        fault="""BEGIN;CREATE FUNCTION pg_temp.bootstrap_fault() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic failure after task insert'; END $$;
        CREATE TRIGGER bootstrap_fault BEFORE INSERT ON d5.task_destinations FOR EACH ROW EXECUTE FUNCTION pg_temp.bootstrap_fault();"""
        error=self.denied(fault+bootstrap_sql(req)+'COMMIT;',role='d5_lab_admin');self.assertIn('synthetic failure after task insert',error)
        self.assertEqual(self.lab.protected_state(),before);self.assertIsNone(self.reader.read_command(req['command_id']))
        self.assertEqual(self.scalar(f"SELECT version FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';"),'0')
        self.assertEqual(self.bsend(req)['status'],'OK')

    def test_B25_lost_response_restart_and_CLI_recovery(self):
        self.initial();_,p=self.bpropose();_,pkg=self.bpackage(p);req=self.command('APPLY_BOOTSTRAP_TASKS',package_sha256=pkg['package_sha256'])
        self.lab.sql(bootstrap_sql(req),role='d5_applier');self.lab.restart();receipt=self.reader.read_command(req['command_id'])
        self.assertEqual(self.bsend(req),receipt)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'request.json';path.write_text(json.dumps(req))
            cli=subprocess.run([sys.executable,'-m','source_ingest.bootstrap','--container',self.lab.container,'--request',str(path)],capture_output=True,text=True)
            self.assertEqual(cli.returncode,0,cli.stderr);self.assertEqual(json.loads(cli.stdout),receipt)
        self.assertEqual(self.task()['row_version'],0)

    def test_B26_cross_sessions_lock_order_and_permissions(self):
        self.initial();_,p=self.bpropose();_,pkg=self.bpackage(p);req=self.command('APPLY_BOOTSTRAP_TASKS',package_sha256=pkg['package_sha256'])
        for role in ('d5_writer','d5_reviewer','d5_reader'):
            self.denied(bootstrap_sql(req),role);self.denied('SELECT d5.task_lock_boundary();',role)
        for role in ('d5_writer','d5_reviewer','d5_reader','d5_applier'):
            self.denied('UPDATE public.tasks SET urgency=0;',role);self.denied('DELETE FROM d5.bootstrap_review_heads;',role)
        self.denied('SELECT d3.lock_state();','d5_applier')
        blocker=self.lab.session('BEGIN;SELECT pg_advisory_xact_lock(742001);SELECT pg_sleep(60);ROLLBACK;','bootstrap_boundary')
        self.lab.wait_for(lambda:self.lab.active('bootstrap_boundary','PgSleep')==1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(self.lab.sql,bootstrap_sql(req),'d5_applier')
                self.lab.wait_for(lambda:int(self.scalar("SELECT count(*) FROM pg_stat_activity WHERE usename='d5_applier' AND wait_event='advisory';"))==1)
                self.assertEqual(self.writer.submit(self.select(self.oid,self.refv))['status'],'OK')
                self.lab.terminate('bootstrap_boundary');self.assertEqual(json.loads(future.result(timeout=30).stdout)['code'],'REFERENCE_VERSION_CONFLICT')
        finally:self.lab.terminate('bootstrap_boundary');blocker.communicate(timeout=5)
        blocker=self.lab.session('BEGIN;SELECT pg_advisory_xact_lock(742005);SELECT pg_sleep(60);ROLLBACK;','bootstrap_boundary')
        self.lab.wait_for(lambda:self.lab.active('bootstrap_boundary','PgSleep')==1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(self.lab.sql,bootstrap_sql(dict(req,command_id=uid())),'d5_applier')
                self.lab.wait_for(lambda:int(self.scalar("SELECT count(*) FROM pg_stat_activity WHERE usename='d5_applier' AND wait_event='advisory';"))==1)
                self.assertEqual(self.scalar("SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a ON a.pid=l.pid WHERE a.usename='d5_applier' AND l.locktype='advisory' AND l.granted AND l.objid IN (742001,742002);"),'2')
                cid=uid();capture=self.lab.session(f"SELECT d3.capture('{cid}','{{\"action\":\"CAPTURE\"}}');",'bootstrap_capture')
                self.lab.wait_for(lambda:self.lab.active('bootstrap_capture','advisory')==1)
                self.lab.terminate('bootstrap_boundary');future.result(timeout=30);out,error=capture.communicate(timeout=10)
                self.assertEqual(capture.returncode,0,error);self.assertEqual(json.loads(out)['capture_id'],cid)
        finally:self.lab.terminate('bootstrap_boundary');blocker.communicate(timeout=5)

    def test_B27_D3_stale_basis_and_published_fixture_immutable(self):
        plan=uid();self.lab.sql(self.plan_fixture(plan,True));old=self.scalar(f"SELECT to_jsonb(p) FROM public.planning_runs p WHERE id='{plan}';")
        cid=uid();self.lab.sql(f"SELECT d3.capture('{cid}','{{\"action\":\"CAPTURE\"}}');")
        before=self.scalar("SELECT encode(public.digest(d3.state_body()::text,'sha256'),'hex');");self.bcreate()
        self.assertNotEqual(before,self.scalar("SELECT encode(public.digest(d3.state_body()::text,'sha256'),'hex');"))
        self.assertEqual(self.scalar(f"SELECT to_jsonb(p) FROM public.planning_runs p WHERE id='{plan}';"),old)
        self.denied(f"UPDATE public.planning_runs SET solver_version='changed' WHERE id='{plan}';",role='d5_lab_admin')

    def test_B28_eligible_BACKLOG_no_activation_and_old_contracts_preserved(self):
        self.bcreate();self.assertEqual(self.scalar(f"SELECT d2.task_eligible('{self.tid}');"),'t')
        for table in ('public.operations','public.outbox_events','public.execution_attempts','d2.reservations','d2.plan_reservations','d4.deliveries'):
            self.assertEqual(self.scalar('SELECT count(*) FROM '+table+';'),'0')
        self.assertEqual(self.task()['status'],'BACKLOG');self.assertEqual(self.lab.catalog(),self.lab.v30_catalog)
        self.lab.assert_i8_functions()
