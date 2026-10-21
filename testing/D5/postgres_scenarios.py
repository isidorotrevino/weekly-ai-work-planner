# SPDX-License-Identifier: GPL-3.0-only
"""Integration cases; invoked only by the disposable D5 runner."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

from source_ingest.postgres import LabClient, envelope, ingest_request, sql_text, submit_sql
from source_ingest.preview import MAX_BYTES, build_observation, canonical, save_preview

LAB = None
PROFILE = 'task-register-compat.v1'


def uid():
    return str(uuid.uuid4())


class Persistence(unittest.TestCase):
    def setUp(self):
        self.lab = LAB
        self.writer = LabClient(LAB.container)
        self.reader = LabClient(LAB.container, 'd5_reader')
        self.pid, self.doc = uid(), uid()
        self.lab.sql("INSERT INTO public.projects(id,code,name,workflow_type) VALUES('" + self.pid + "','" + self.pid + "','Synthetic D5','GENTLE_AI');")
        self.register = envelope(uid(), 'REGISTER_SOURCE', self.pid, self.doc, namespace='synthetic', logical_key='register')
        self.assertEqual(self.writer.submit(self.register)['status'], 'OK')

    def scalar(self, sql):
        return self.lab.sql(sql).stdout.strip()

    def capture(self, body=None, label='fixture-v1', profile=PROFILE, doc=None, pid=None):
        if body is None:
            body = Path('testing/D5/fixtures/register-compat-before.md').read_bytes()
        return build_observation(body, 'fixture.md', pid or self.pid, doc or self.doc, label, profile)

    def packet(self, observation=None, cid=None):
        with tempfile.TemporaryDirectory() as tmp:
            path, _ = save_preview(tmp, observation or self.capture())
            return ingest_request(cid or uid(), path)

    def ingest(self, observation=None):
        packet = self.packet(observation)
        return packet, self.writer.submit(*packet)

    def select(self, oid, version, cid=None, profile=PROFILE):
        return envelope(cid or uid(), 'SELECT_REFERENCE', self.pid, self.doc, profile=profile,
                        observation_id=oid, expected_version=version, reason='Synthetic diagnostic reference')

    def head(self, profile=PROFILE):
        return self.reader.read_reference(self.pid, self.doc, profile)

    def count(self, table, doc=None):
        return int(self.scalar(f"SELECT count(*) FROM {table} WHERE document_id='{doc or self.doc}';"))

    def denied(self, sql, role='d5_writer'):
        result = self.lab.sql(sql, role=role, check=False)
        self.assertNotEqual(result.returncode, 0)
        return result.stderr

    def test_P01_registration_replay_and_empty_heads(self):
        self.assertEqual(self.writer.submit(self.register), self.reader.read_command(self.register['command_id']))
        self.assertEqual(self.head()['version'], 0)
        self.assertIsNone(self.head()['observation_id'])
        self.assertEqual(self.count('d5.reference_heads'), 3)
        other = dict(self.register, command_id=uid())
        self.assertEqual(self.writer.submit(other)['status'], 'OK')
        other['command_id'], other['logical_key'] = uid(), 'other'
        self.assertEqual(self.writer.submit(other)['code'], 'IDENTITY_CONFLICT')
        collision = dict(self.register, command_id=uid(), document_id=uid())
        self.assertEqual(self.writer.submit(collision)['code'], 'IDENTITY_CONFLICT')
        self.assertEqual(self.count('d5.source_registrations'), 1)

    def test_P01_missing_project_and_legacy_adoption(self):
        req = dict(self.register, command_id=uid(), project_id=uid(), document_id=uid())
        with self.assertRaises(RuntimeError):
            self.writer.submit(req)
        self.assertIsNone(self.reader.read_command(req['command_id']))
        legacy = uid()
        self.lab.sql(f"INSERT INTO public.source_documents(id,project_id,source_type,source_uri) VALUES('{legacy}','{self.pid}','OTHER','legacy:{legacy}');")
        req = dict(self.register, command_id=uid(), document_id=legacy, logical_key='legacy')
        self.assertEqual(self.writer.submit(req)['code'], 'ADOPTION_REQUIRED')
        self.assertEqual(self.count('d5.source_registrations', legacy), 0)

    def test_P01_external_head_and_identity_changes_block(self):
        packet, result = self.ingest()
        rid = result['revision_id']
        for change in ["source_type='GENTLE_AI'", "source_uri='changed'", f"current_revision_id='{rid}'"]:
            self.lab.sql(f"UPDATE public.source_documents SET {change} WHERE id='{self.doc}';")
            p = (dict(packet[0], command_id=uid()), packet[1], packet[2])
            self.assertEqual(self.writer.submit(*p)['code'], 'IDENTITY_CONFLICT')
            self.lab.sql(f"UPDATE public.source_documents SET source_type='OTHER',source_uri='urn:weekly-ai-work-planner:d5:source:{self.doc}',current_revision_id=NULL WHERE id='{self.doc}';")
        self.assertEqual(self.count('d5.observations'), 1)
        self.assertEqual(self.head()['version'], 0)

    def test_P02_selection_and_ingest_scope(self):
        packet, result = self.ingest()
        req = self.select(result['observation_id'], 0, profile='task-register.v1')
        self.assertEqual(self.writer.submit(req)['code'], 'OBSERVATION_SCOPE_CONFLICT')
        req = self.select(result['observation_id'], 0)
        req['project_id'] = uid()
        self.assertEqual(self.writer.submit(req)['code'], 'IDENTITY_CONFLICT')
        bad = dict(packet[0], command_id=uid(), document_id=uid())
        with self.assertRaises(ValueError):
            self.writer.submit(bad, *packet[1:])
        self.denied(submit_sql(bad, *packet[1:]), role='d5_writer')
        self.assertEqual(self.head()['version'], 0)

    def test_P02_composite_foreign_keys(self):
        _, result = self.ingest()
        oid = result['observation_id']
        # Owner attempts cannot attach an observation to a head of another profile.
        self.denied(f"UPDATE d5.reference_heads SET observation_id='{oid}',version=1 WHERE document_id='{self.doc}' AND profile='task-register.v1';", role='d5_lab_admin')
        self.assertEqual(self.head('task-register.v1')['version'], 0)

    def test_P03_hash_embedded_bytes_and_parser_guards(self):
        packet = self.packet()
        self.denied(submit_sql(packet[0], b'other', packet[2]))
        value = json.loads(packet[2])
        for key, changed in [('content_base64', 'b3RoZXI='), ('project_id', uid()), ('activation_allowed', True), ('revision_authority', 'VERIFIED')]:
            modified = dict(value, **{key: changed})
            payload = canonical(modified)
            req = dict(packet[0], command_id=uid(), preview_sha256=hashlib.sha256(payload).hexdigest())
            self.denied(submit_sql(req, packet[1], payload))
        modified = dict(value)
        modified['proposals'] = []  # Semantically forged but structurally coherent SQL data.
        payload = canonical(modified)
        req = dict(packet[0], preview_sha256=hashlib.sha256(payload).hexdigest())
        with self.assertRaises(ValueError):
            self.writer.submit(req, packet[1], payload)
        self.assertEqual(self.count('d5.observations'), 0)

    def test_P03_closed_envelope_and_duplicate_keys(self):
        req = self.select(uid(), 0)
        for change in [dict(extra='x'), dict(expected_version='0'), dict(expected_version=True), dict(expected_version=-1), dict(expected_version=0.5), dict(reason=None), dict(profile='unknown')]:
            self.denied(submit_sql(dict(req, **change)))
        duplicate = json.dumps(self.register)[:-1] + ',"action":"REGISTER_SOURCE"}'
        self.denied('SELECT d5.submit(' + sql_text(duplicate) + '::json);')
        self.denied('BEGIN ISOLATION LEVEL REPEATABLE READ; ' + submit_sql(dict(self.register, command_id=uid())) + 'COMMIT;')
        for name in ['', ' x', 'x\t', 'x'*257, '\u00a0x', 'x\u2003']:
            self.denied(submit_sql(dict(self.register, command_id=uid(), namespace=name)))

    def test_P03_source_exact_limit_and_excess(self):
        body = (b'a'*65535+b'\n')*32
        self.assertEqual(len(body), MAX_BYTES)
        packet, result = self.ingest(self.capture(body, profile='markdown-structure.v1'))
        self.assertEqual(result['status'], 'OK')
        with self.assertRaises(ValueError):
            self.writer.submit(packet[0], body+b'a', packet[2])
        # Bypass adapter length guard to exercise SQL's independent limit.
        self.denied('SELECT d5.submit(' + sql_text(json.dumps(packet[0])) + "::json,decode('" + (body+b'a').hex() + "','hex'),decode('" + packet[2].hex() + "','hex'));")
        recovered = self.reader.recover(self.pid, self.doc, result['observation_id'])
        self.assertEqual(recovered, packet[1:])

    def test_P03_artifact_storage_boundary(self):
        _, result = self.ingest()
        # Storage constraint only: owner inserts synthetic padding inside rollback.
        # This does not claim canonical 32 MiB parser output is attainable.
        rid = result['revision_id']
        statement = f"INSERT INTO d5.preview_artifacts SELECT encode(public.digest(b,'sha256'),'hex'),'{self.doc}','{self.pid}','{rid}','{PROFILE}',b FROM (SELECT convert_to(repeat(' ',{{size}}),'UTF8') b) s;"
        self.lab.sql('BEGIN;'+statement.format(size=33554432)+'ROLLBACK;')
        self.denied('BEGIN;'+statement.format(size=33554433)+'ROLLBACK;', role='d5_lab_admin')
        self.assertEqual(self.count('d5.preview_artifacts'), 1)

    def test_P04_dedup_labels_profiles_commands_and_documents(self):
        first, result = self.ingest()
        self.writer.submit(dict(first[0], command_id=uid()), *first[1:])
        self.ingest(self.capture(label='fixture-v2'))
        self.ingest(self.capture(profile='task-register.v1'))
        self.assertEqual(self.count('d5.revision_content'), 1)
        self.assertEqual(self.count('d5.observations'), 4)
        self.assertEqual(self.count('d5.preview_artifacts'), 3)
        other = uid()
        self.writer.submit(dict(self.register, command_id=uid(), document_id=other, logical_key='second'))
        p = self.packet(self.capture(doc=other))
        self.writer.submit(*p)
        self.assertEqual(self.count('d5.revision_content', other), 1)
        self.assertEqual(self.scalar(f"SELECT external_revision IS NULL FROM public.source_revisions WHERE id='{result['revision_id']}';"), 't')
        self.assertEqual(self.head()['version'], 0)

    def test_P05_selection_same_observation_and_blocked_diagnostic(self):
        _, result = self.ingest()
        req = self.select(result['observation_id'], 0)
        self.assertEqual(self.writer.submit(req)['version_at_commit'], 1)
        self.assertEqual(self.writer.submit(self.select(result['observation_id'], 1))['version_at_commit'], 2)
        blocked = Path('testing/D5/fixtures/register-compat-before.md').read_bytes()
        # Strict profile with an annotation is blocked; selecting cannot repair it.
        value = self.capture(blocked, profile='task-register.v1')
        self.assertFalse(value['register']['comparison_eligible'])
        packet, r = self.ingest(value)
        self.assertEqual(self.writer.submit(self.select(r['observation_id'], 0, profile='task-register.v1'))['status'], 'OK')
        self.assertEqual(self.reader.recover(self.pid, self.doc, r['observation_id'])[1], packet[2])

    def test_P06_concurrent_ingest_and_CAS(self):
        packet = self.packet()
        packets = [packet, (dict(packet[0], command_id=uid()), *packet[1:])]
        results = self.lab.concurrent([submit_sql(*p) for p in packets])
        self.assertTrue(all(r['status']=='OK' for r in results))
        self.assertEqual(self.count('d5.revision_content'), 1)
        self.assertEqual(self.count('d5.observations'), 2)
        self.assertEqual(self.count('d5.preview_artifacts'), 1)
        choices = [self.select(r['observation_id'], 0) for r in results]
        selected = self.lab.concurrent([submit_sql(r) for r in choices])
        self.assertEqual(sorted(r['status'] for r in selected), ['CONFLICT','OK'])
        self.assertEqual(self.head()['version'], 1)
        self.assertEqual(self.count('d5.reference_selections'), 1)
        loser = next((req,r) for req,r in zip(choices,selected) if r['status']=='CONFLICT')
        self.assertEqual(self.writer.submit(loser[0]), loser[1])

    def test_P06_ABA_and_historical_replay(self):
        packet, a = self.ingest()
        _, b = self.ingest(self.capture(label='B'))
        first = self.select(a['observation_id'], 0)
        receipt = self.writer.submit(first)
        self.writer.submit(self.select(b['observation_id'], 1))
        self.writer.submit(self.select(a['observation_id'], 2))
        self.assertEqual(self.writer.submit(self.select(b['observation_id'], 1))['code'], 'VERSION_CONFLICT')
        self.assertEqual(self.writer.submit(first), receipt)
        self.assertEqual(self.head()['version'], 3)
        self.assertEqual(self.head()['observation_id'], a['observation_id'])
        self.assertEqual(self.writer.submit(dict(first, expected_version=3))['code'], 'COMMAND_CONTENT_CONFLICT')

    def test_P06_version_exhaustion_rolls_back(self):
        _, result = self.ingest()
        self.writer.submit(self.select(result['observation_id'], 0))
        maximum = 9223372036854775807
        self.lab.sql(f"UPDATE d5.reference_heads SET version={maximum} WHERE document_id='{self.doc}' AND profile='{PROFILE}';")
        req = self.select(result['observation_id'], maximum)
        with self.assertRaises(RuntimeError):
            self.writer.submit(req)
        self.assertEqual(self.head()['version'], maximum)
        self.assertIsNone(self.reader.read_command(req['command_id']))
        self.assertEqual(self.count('d5.reference_selections'), 1)

    def test_P07_replay_and_changed_request(self):
        packet, result = self.ingest()
        self.assertEqual(self.writer.submit(*packet), result)
        self.assertEqual(self.reader.read_command(packet[0]['command_id']), result)
        self.assertEqual(self.count('d5.observations'), 1)
        other = self.packet(self.capture(label='another'), cid=packet[0]['command_id'])
        self.assertEqual(self.writer.submit(*other)['code'], 'COMMAND_CONTENT_CONFLICT')
        cross = dict(self.register, command_id=packet[0]['command_id'])
        self.assertEqual(self.writer.submit(cross)['code'], 'COMMAND_CONTENT_CONFLICT')
        self.assertEqual(self.reader.read_command(packet[0]['command_id']), result)
        self.assertEqual(self.count('d5.observations'), 1)

    def test_P08_abort_before_commit_and_retry(self):
        packet = self.packet()
        # Terminate a real session after all writes but before its COMMIT.
        self.lab.abort_after(submit_sql(*packet))
        self.assertIsNone(self.reader.read_command(packet[0]['command_id']))
        for table in ('d5.observations','d5.preview_artifacts','d5.revision_content','public.source_revisions'):
            self.assertEqual(self.count(table), 0)
        self.assertEqual(self.writer.submit(*packet)['status'], 'OK')

    def test_P08_selection_abort_preserves_head(self):
        _, result = self.ingest()
        req = self.select(result['observation_id'], 0)
        self.lab.abort_after(submit_sql(req))
        self.assertIsNone(self.reader.read_command(req['command_id']))
        self.assertEqual(self.head()['version'], 0)
        self.assertEqual(self.count('d5.reference_selections'), 0)
        self.assertEqual(self.writer.submit(req)['version_at_commit'], 1)

    def test_P08_lost_response_restart_and_recovery(self):
        packet = self.packet()
        self.writer.submit(*packet)  # Deliberately discard the confirmed response.
        self.lab.restart()
        fresh = LabClient(self.lab.container)
        receipt = fresh.read_command(packet[0]['command_id'])
        self.assertEqual(fresh.submit(*packet), receipt)
        self.assertEqual(self.reader.recover(self.pid, self.doc, receipt['observation_id']), packet[1:])
        self.assertEqual(self.count('d5.observations'), 1)
        self.assertEqual(self.head()['version'], 0)

    def test_P09_role_permissions_and_fact_immutability(self):
        for role in ('d5_reader','d5_writer'):
            for sql in ['SELECT * FROM public.projects;', 'UPDATE public.source_documents SET current_revision_id=NULL;',
                        'SELECT * FROM d5.observations;', 'TRUNCATE d5.commands;', 'SELECT * FROM d2.commands;',
                        'SELECT d2.sync_source(gen_random_uuid(),\'{}\'::jsonb);']:
                self.denied(sql, role=role)
        self.denied(submit_sql(dict(self.register, command_id=uid())), role='d5_reader')
        for table in ('commands','source_registrations','revision_content','preview_artifacts','observations','reference_selections'):
            for statement in (f'DELETE FROM d5.{table};', f'TRUNCATE d5.{table};'):
                self.denied(statement, role='d5_lab_admin')
        self.denied('UPDATE d5.commands SET response=response;', role='d5_lab_admin')
        # Temporary shadow relations cannot redirect SECURITY DEFINER reads.
        self.lab.sql("CREATE TEMP TABLE commands(response jsonb,command_id uuid); SELECT d5.read_command('"+self.register['command_id']+"');", role='d5_reader')
        self.assertEqual(self.scalar("SELECT bool_and(NOT rolcanlogin AND NOT rolsuper) FROM pg_roles WHERE rolname='d5_owner';"),'t')
        self.assertEqual(self.scalar("SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace CROSS JOIN LATERAL aclexplode(coalesce(p.proacl,acldefault('f',p.proowner))) a WHERE n.nspname='d5' AND a.grantee=0 AND a.privilege_type='EXECUTE';"),'0')

    def test_P10_CLI_workflow(self):
        def cli(*args, code=0):
            result = subprocess.run([sys.executable,'-m','source_ingest.postgres','--container',self.lab.container,*args],capture_output=True,text=True)
            self.assertEqual(result.returncode,code,result.stderr)
            return json.loads(result.stdout)
        common = ['--project-id',self.pid,'--document-id',self.doc]
        registered = cli('register','--command-id',uid(),*common,'--namespace','synthetic','--logical-key','register')
        self.assertEqual(registered['status'],'OK')
        with tempfile.TemporaryDirectory() as directory:
            path,_ = save_preview(directory,self.capture())
            cid = uid()
            ingested = cli('ingest','--command-id',cid,'--preview',str(path))
        head = cli('reference',*common,'--profile',PROFILE)
        self.assertEqual(head['version'],0)
        self.assertEqual(cli('receipt','--command-id',cid),ingested)
        selected = cli('select','--command-id',uid(),*common,'--profile',PROFILE,
                       '--observation-id',cid,'--expected-version','0','--reason','Synthetic review')
        self.assertEqual(selected['version_at_commit'],1)
        conflict = cli('select','--command-id',uid(),*common,'--profile',PROFILE,
                       '--observation-id',cid,'--expected-version','0','--reason','Stale review',code=2)
        self.assertEqual(conflict['code'],'VERSION_CONFLICT')

    def test_P10_public_state_and_D2_pointers_preserved(self):
        before = self.lab.protected_state()
        packet, result = self.ingest()
        self.writer.submit(self.select(result['observation_id'],0))
        self.assertEqual(self.lab.protected_state(), before)
        self.assertEqual(self.scalar(f"SELECT current_revision_id IS NULL FROM public.source_documents WHERE id='{self.doc}';"),'t')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM public.external_bindings WHERE internal_id='{self.doc}';"),'0')
