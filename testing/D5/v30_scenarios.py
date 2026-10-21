# SPDX-License-Identifier: GPL-3.0-only
"""Bounded D5/V30 SQL coexistence; no tasks, dispatch or worker processes."""
import concurrent.futures
import json

from .review_scenarios import Review
from .postgres_scenarios import uid
from source_ingest.postgres import envelope


class Compatibility(Review):
    def basis(self):
        return self.scalar("SELECT encode(public.digest(d3.state_body()::text,'sha256'),'hex');")

    def test_T01_V30_catalog_and_readset_preserved(self):
        self.assertEqual(self.lab.catalog(),self.lab.v30_catalog)
        relations=json.loads(self.scalar('SELECT to_jsonb(d3.state_relations());'))
        self.assertIn('d4.presence_heads',relations)
        self.assertNotIn('public.source_documents',relations)
        self.assertNotIn('public.source_revisions',relations)
        self.assertTrue(all(not r.startswith('d5.') for r in relations))
        self.assertEqual(self.scalar("SELECT count(*) FROM d4.worker_catalog WHERE enabled;"),'0')
        self.assertEqual(self.scalar("SELECT count(*) FROM public.workers WHERE state<>'OFFLINE';"),'0')

    def test_T02_D5_full_flow_preserves_populated_D2_D3_D4(self):
        before=self.lab.protected_state(include_sources=False);basis=self.basis()
        # Exercise new source registration within an already existing synthetic project.
        self.doc=uid()
        self.writer.submit(envelope(uid(),'REGISTER_SOURCE',self.pid,self.doc,namespace='synthetic',logical_key='coexistence'))
        self.prepare()
        pins=[]
        for key in sorted(self.items):
            _,result=self.decide(key);pins.append(self.pin(key,result))
        self.assertEqual(self.simulate(pins)['status'],'OK')
        self.assertEqual(self.lab.protected_state(include_sources=False),before)
        self.assertEqual(self.basis(),basis)
        self.assertEqual(self.scalar('SELECT count(*) FROM public.tasks;'),'0')
        self.assertEqual(self.scalar('SELECT count(*) FROM public.operations;'),'0')
        self.assertEqual(self.scalar(f"SELECT current_revision_id IS NULL FROM public.source_documents WHERE id='{self.doc}';"),'t')

    def test_T03_runtime_roles_have_no_D3_D4_authority(self):
        calls=['d3.capture(NULL,\'{"action":"CAPTURE"}\'::jsonb)',
               "d3.enqueue_planning(NULL,'{}'::jsonb)","d3.dispatch(NULL,'{}'::jsonb)",
               "d4.transport(NULL,NULL,'{}'::jsonb)","d4.worker_execution(NULL,NULL,'{}'::jsonb)",
               "d4.presence_open(NULL,NULL,NULL,NULL)","d4.tree_record(NULL,NULL,'{}'::jsonb)"]
        for role in ('d5_writer','d5_reader','d5_reviewer'):
            for call in calls:
                result=self.lab.sql('\\set VERBOSITY verbose\nSELECT '+call+';',role=role,check=False)
                self.assertNotEqual(result.returncode,0)
                self.assertIn('42501',result.stderr)
            self.assertEqual(self.scalar("SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname IN ('d3','d4') AND has_schema_privilege('"+role+"',n.oid,'USAGE') AND has_function_privilege('"+role+"',p.oid,'EXECUTE');"),'0')
        for schema in ('d2','d3','d4'):
            self.assertEqual(self.scalar("SELECT has_schema_privilege('d5_owner','"+schema+"','USAGE');"),'f')

    def test_T04_D5_finishes_while_D3_state_lock_is_held(self):
        blocker=self.lab.session('BEGIN; SELECT d3.lock_state(); SELECT pg_sleep(60); ROLLBACK;','d5_barrier')
        self.lab.wait_for(lambda:self.lab.active('d5_barrier','PgSleep')==1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                def flow():
                    self.prepare();_,r=self.decide()
                    return self.simulate([self.pin('PT-01',r)])
                future=pool.submit(flow)
                try:
                    result=future.result(timeout=12)
                    self.assertEqual(result['status'],'OK')
                    self.assertEqual(self.lab.active('d5_barrier','PgSleep'),1)
                finally:
                    self.lab.terminate('d5_barrier')
        finally:
            self.lab.terminate('d5_barrier');blocker.communicate(timeout=5)

    def test_T05_D3_capture_and_D4_read_finish_while_D5_lock_is_held(self):
        blocker=self.lab.session('BEGIN; SELECT pg_advisory_xact_lock(742005); SELECT pg_sleep(60); ROLLBACK;','d5_barrier')
        self.lab.wait_for(lambda:self.lab.active('d5_barrier','PgSleep')==1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                capture=uid()
                sql="SELECT d3.capture('"+capture+"','{\"action\":\"CAPTURE\"}'::jsonb); SELECT d4.presence_current('"+self.lab.worker+"');"
                future=pool.submit(self.lab.sql,sql)
                try:
                    result=future.result(timeout=12)
                    lines=result.stdout.splitlines()
                    self.assertEqual(json.loads(lines[0])['capture_id'],capture)
                    self.assertIsNone(json.loads(lines[1]))
                    self.assertEqual(self.lab.active('d5_barrier','PgSleep'),1)
                finally:
                    self.lab.terminate('d5_barrier')
        finally:
            self.lab.terminate('d5_barrier');blocker.communicate(timeout=5)
