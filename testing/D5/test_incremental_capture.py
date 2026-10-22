# SPDX-License-Identifier: GPL-3.0-only
"""DI01-DI28 synthetic filesystem/process recovery, never Google conformance."""
from copy import deepcopy
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import uuid

from source_ingest.incremental_fixture import (FixtureStore, IncrementalError,
    MAX_COMMITS, MAX_EVENTS, MAX_OBJECT, TemporaryFixtureLab, digest, encode,
    file_event, page, request)

PROJECT = '00000000-0000-4000-8000-000000000001'
DOCUMENT = '00000000-0000-4000-8000-000000000002'
CONNECTOR = '00000000-0000-4000-8000-000000000003'
CHILDREN = []


def scope_fixture():
    return dict(schema='d5.fixture-drive-scope.v1', mode='SYNTHETIC_ONLY',
                project_id=PROJECT, connector_id=CONNECTOR, principal='fixture-principal',
                corpus='fixture-corpus', drive='fixture-drive', policy_version='fixture-policy.v1',
                export_mime='text/plain', allowlist=[dict(file_id='file-1', document_id=DOCUMENT,
                profile='task-register.v1')])


def child_advance(root, run_id, scope, req, connection, fault):
    try:
        store = FixtureStore(root, run_id, scope, test_fault=fault, test_ready=connection)
        connection.send(('OK', store.advance(req)))
    except IncrementalError as ex:
        connection.send(('ERROR', str(ex)))
    finally:
        connection.close()


def child_snapshot(root, run_id, scope, connection):
    try:
        connection.send(FixtureStore(root, run_id, scope).snapshot())
    finally:
        connection.close()


class IncrementalCaptureTest(unittest.TestCase):
    def setUp(self):
        self.data = Path('testing/D5/fixtures/register-before.md').read_bytes()
        self.scope = scope_fixture()
        self.lab = TemporaryFixtureLab(self.scope, 'opaque:anchor')
        self.addCleanup(self.lab.close)
        self.store = self.lab.store

    def command(self, events=(), *, nxt=None, terminal=None, snapshot=None, cid=None):
        snap = snapshot or self.store.snapshot()
        return request(cid or str(uuid.uuid4()), snap,
                       page(self.scope, snap['state'], list(events), next_token=nxt, new_start=terminal))

    def advance(self, events=(), **kwargs):
        return self.store.advance(self.command(events, **kwargs))

    def capture(self, content=None, **extra):
        return file_event('file-1', self.data if content is None else content, **extra)

    def spawn(self, req, fault=None):
        ctx = mp.get_context('spawn')
        parent, child = ctx.Pipe()
        process = ctx.Process(target=child_advance,
            args=(str(self.lab.root), self.lab.run_id, self.scope, req, child, fault))
        process.start(); child.close(); CHILDREN.append(process)
        def cleanup():
            if process.is_alive(): process.kill()
            process.join(10); parent.close()
            if process.is_alive(): raise AssertionError('Fixture child failed to exit')
        self.addCleanup(cleanup)
        return process, parent

    def message(self, connection):
        self.assertTrue(connection.poll(10), 'Fixture child did not reach checkpoint')
        return connection.recv()

    def kill_at(self, req, point):
        process, connection = self.spawn(req, point)
        self.assertEqual(point, self.message(connection))
        process.kill(); process.join(10)
        self.assertFalse(process.is_alive())
        self.assertLess(process.exitcode, 0)

    def test_DI01_scope_genesis_identity_and_no_reference(self):
        snap = self.store.snapshot()
        self.assertEqual(0, snap['version'])
        self.assertEqual(dict(phase='INVENTORY', anchor='opaque:anchor', token=None, continuations=[]), snap['state'])
        self.assertFalse(snap['reference_selected'])
        self.assertEqual(0, snap['persistent_D2_writes'])
        with self.assertRaises(IncrementalError):
            FixtureStore(self.lab.root, str(uuid.uuid4()), self.scope).snapshot()

    def test_DI02_anchor_before_inventory_and_observed_new_revision(self):
        self.advance([self.capture()])
        self.assertEqual('opaque:anchor', self.store.snapshot()['state']['token'])
        self.advance([self.capture(self.data.replace(b'Review only', b'Newly observed'), version='fixture-2')], terminal='opaque:poll')
        snap = self.store.snapshot()
        self.assertEqual('FOLLOWING', snap['state']['phase'])
        self.assertEqual(2, snap['logical_observations'])
        self.assertEqual('opaque:anchor', snap['state']['anchor'])

    def test_DI03_inventory_pages_preserve_anchor_until_explicit_end(self):
        self.advance([self.capture()], nxt='inventory-next')
        snap = self.store.snapshot()
        self.assertEqual('INVENTORY', snap['state']['phase'])
        self.assertEqual('inventory-next', snap['state']['token'])
        self.advance([])
        self.assertEqual('CATCHUP', self.store.snapshot()['state']['phase'])
        self.assertEqual('opaque:anchor', self.store.snapshot()['state']['token'])

    def test_DI04_feed_continuation_and_terminal_are_separate(self):
        self.advance([])
        self.advance([], nxt='feed-next')
        snap = self.store.snapshot()
        self.assertEqual('CATCHUP', snap['state']['phase'])
        self.assertEqual('feed-next', snap['state']['token'])
        invalid = self.command([], nxt='x', terminal='y')
        with self.assertRaises(IncrementalError): self.store.advance(invalid)
        self.assertEqual(snap, self.store.snapshot())
        self.advance([], terminal='future-token')
        self.assertEqual('FOLLOWING', self.store.snapshot()['state']['phase'])

    def test_DI05_duplicate_observations_keep_occurrences_not_duplicate_identity(self):
        self.advance([self.capture()])
        self.advance([self.capture()], terminal='future')
        snap = self.store.snapshot()
        self.assertEqual(2, snap['occurrences']); self.assertEqual(1, snap['logical_observations'])
        self.advance([self.capture(version='different-label')], terminal='new-future')
        self.assertEqual(2, self.store.snapshot()['logical_observations'])

    def test_DI06_empty_pages_and_empty_poll_with_same_terminal_token(self):
        self.advance([])
        self.advance([], terminal='opaque:anchor')
        before = self.store.snapshot()
        self.advance([], terminal='opaque:anchor')
        after = self.store.snapshot()
        self.assertEqual(before['version'] + 1, after['version'])
        self.assertEqual(before['state'], after['state'])
        self.assertEqual(0, after['occurrences'])

    def test_DI07_fresh_process_recovers_state_from_disk(self):
        self.advance([self.capture()], nxt='next-inventory')
        expected = self.store.snapshot()
        ctx = mp.get_context('spawn'); parent, child = ctx.Pipe()
        process = ctx.Process(target=child_snapshot, args=(str(self.lab.root), self.lab.run_id, self.scope, child))
        process.start(); child.close(); CHILDREN.append(process)
        try:
            self.assertEqual(expected, self.message(parent))
        finally:
            if process.is_alive(): process.join(10)
            if process.is_alive(): process.kill(); process.join(10)
            parent.close()
        self.assertEqual(0, process.exitcode)

    def test_DI08_bytes_diagnostics_receipt_and_cursor_share_one_commit(self):
        req = self.command([self.capture(), file_event('not-allowed', b'ignored')])
        result = self.store.advance(req)
        sha, commit = self.store.inspect()[-1]
        self.assertEqual(sha, result['commit_sha256'])
        self.assertEqual(2, len(commit['results']))
        self.assertEqual('OUTSIDE_ALLOWLIST', commit['results'][1]['code'])
        self.assertEqual('CATCHUP', commit['state_after']['phase'])
        self.assertEqual(digest(req), commit['request_sha256'])
        self.assertEqual(1, commit['receipt']['version'])
        self.assertIn('content_base64', commit['results'][0]['capture'])

    def test_DI08_docs_export_grade_survives_filesystem_recovery_without_reference(self):
        self.advance([self.capture(mime='application/vnd.google-apps.document')])
        fresh=FixtureStore(self.lab.root,self.lab.run_id,self.scope)
        capture=fresh.inspect()[-1][1]['results'][0]['capture']
        self.assertEqual('OBSERVED_EXPORT',capture['provenance_grade'])
        self.assertEqual('text/plain',capture['export_mime'])
        self.assertEqual('fixture-exporter.v1',capture['exporter'])
        self.assertFalse(fresh.snapshot()['reference_selected'])

    def test_DI09_transient_late_event_never_commits_a_prefix(self):
        before = self.store.snapshot()
        req = self.command([self.capture(), file_event('file-1', outcome='TIMEOUT')])
        with self.assertRaisesRegex(IncrementalError, 'TRANSIENT_PAGE'): self.store.advance(req)
        self.assertEqual(before, self.store.snapshot())
        self.assertEqual(1, len(list((self.lab.root / 'objects').glob('*.json'))))

    def test_DI10_kill_before_object_does_not_authorize_partial_temporary(self):
        before = self.store.snapshot(); req = self.command([self.capture()])
        self.kill_at(req, 'before_object')
        (self.lab.root / 'objects/.partial-fixture').write_bytes(b'{')
        self.assertEqual(before, self.store.snapshot())
        self.store.advance(req)
        self.assertEqual(1, self.store.snapshot()['logical_observations'])

    def test_DI11_kill_after_object_preserves_old_head_and_ignores_orphan(self):
        before = self.store.snapshot(); req = self.command([self.capture()])
        self.kill_at(req, 'after_object')
        self.assertEqual(2, len(list((self.lab.root / 'objects').glob('*.json'))))
        self.assertEqual(before, self.store.snapshot())
        self.store.advance(req)
        self.assertEqual(1, self.store.snapshot()['committed_pages'])
        self.assertEqual(1, self.store.snapshot()['logical_observations'])

    def test_DI12_kill_after_head_recovers_receipt_without_reapplying(self):
        req = self.command([self.capture()])
        self.kill_at(req, 'after_head')
        snap = self.store.snapshot()
        recovered = self.store.read_command(req['command_id'], digest(req))
        self.assertEqual('SYNTHETIC_CAPTURE_CONFIRMED', recovered['result'])
        self.assertEqual(recovered, self.store.advance(req))
        self.advance([], terminal='new-poll')
        newer = self.store.snapshot()
        self.assertEqual(recovered, self.store.advance(req))
        self.assertEqual(newer, self.store.snapshot())
        self.assertEqual(snap['version'] + 1, newer['version'])

    def test_DI13_before_replace_or_uncertain_fsync_recovers_whole_state(self):
        req = self.command([self.capture()]); before = self.store.snapshot()
        self.kill_at(req, 'before_replace')
        self.assertEqual(before, self.store.snapshot())
        faulty = FixtureStore(self.lab.root, self.lab.run_id, self.scope, test_fault='fsync_failure')
        with self.assertRaisesRegex(IncrementalError, 'UNKNOWN_COMMIT'): faulty.advance(req)
        self.assertEqual(1, self.store.snapshot()['version'])
        self.assertEqual(1, self.store.snapshot()['logical_observations'])
        self.assertEqual(self.store.read_command(req['command_id'], digest(req)), self.store.advance(req))

    def test_DI13_recovery_must_sync_visible_head_before_confirming_receipt(self):
        req=self.command([self.capture()])
        faulty=FixtureStore(self.lab.root,self.lab.run_id,self.scope,test_fault='fsync_failure')
        with self.assertRaisesRegex(IncrementalError,'UNKNOWN_COMMIT'):faulty.advance(req)
        with patch('source_ingest.incremental_fixture.os.fsync',side_effect=OSError('fixture fsync failure')):
            with self.assertRaisesRegex(IncrementalError,'UNKNOWN_COMMIT'):
                self.store.read_command(req['command_id'],digest(req))
            with self.assertRaisesRegex(IncrementalError,'UNKNOWN_COMMIT'):
                self.store.advance(req)
        self.assertEqual('SYNTHETIC_CAPTURE_CONFIRMED',self.store.read_command(req['command_id'],digest(req))['result'])

    def test_DI14_two_writers_cas_and_command_content_conflict(self):
        snap = self.store.snapshot()
        a = self.command([self.capture()], snapshot=snap)
        b = self.command([], snapshot=snap)
        pa, ca = self.spawn(a,'prepared'); pb, cb = self.spawn(b,'prepared')
        self.assertEqual('prepared',self.message(ca)); self.assertEqual('prepared',self.message(cb))
        ca.send('CONTINUE'); cb.send('CONTINUE')
        responses = [self.message(ca), self.message(cb)]
        pa.join(10); pb.join(10)
        self.assertEqual(['ERROR', 'OK'], sorted(x[0] for x in responses))
        self.assertEqual('CONFLICT_HEAD', next(x[1] for x in responses if x[0]=='ERROR'))
        winner = a if responses[0][0]=='OK' else b
        changed = deepcopy(winner); changed['page']['events'] = [self.capture(version='changed')]
        with self.assertRaisesRegex(IncrementalError, 'CONFLICT_COMMAND'): self.store.advance(changed)
        self.assertEqual(1, self.store.snapshot()['version'])

    def test_DI15_outside_allowlist_keeps_terminal_diagnostic_only(self):
        self.advance([file_event('../external-file', b'not read')])
        item = self.store.inspect()[-1][1]['results'][0]
        self.assertEqual('OUTSIDE_ALLOWLIST', item['code'])
        self.assertIsNone(item['capture'])
        self.assertFalse(self.store.snapshot()['reference_selected'])
        drive=file_event('placeholder');drive.update(change_type='drive',file_id=None)
        self.advance([drive],terminal='poll-after-non-file')
        self.assertEqual('NON_FILE_CHANGE',self.store.inspect()[-1][1]['results'][0]['code'])
        self.assertEqual(0,self.store.snapshot()['logical_observations'])

    def test_DI16_unsupported_formats_and_size_limit_not_silent_truncation(self):
        events=[self.capture(mime='application/pdf'), self.capture(mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
                self.capture(b'x' * (2*1024*1024+1))]
        self.advance(events)
        results=self.store.inspect()[-1][1]['results']
        self.assertEqual(['UNSUPPORTED_MIME','UNSUPPORTED_MIME','SOURCE_SIZE_LIMIT'],[r['code'] for r in results])
        self.assertTrue(all(r['capture'] is None for r in results))
        self.assertEqual(0,self.store.snapshot()['logical_observations'])

    def test_DI17_removal_and_file_access_loss_are_not_D2_absence_application(self):
        self.advance([file_event('file-1', outcome=o) for o in ['REMOVED','ACCESS_DENIED','NOT_FOUND']])
        snapshot=self.store.snapshot()
        self.assertEqual(3,snapshot['terminal_diagnostics'])
        self.assertEqual(0,snapshot['persistent_D2_writes'])
        self.assertFalse(snapshot['reference_selected'])

    def test_DI18_global_auth_error_cannot_be_diagnosed_as_file_skip(self):
        before=self.store.snapshot()
        for outcome in ['AUTH_FAILURE','SCOPE_INVALID','RATE_LIMIT']:
            with self.subTest(outcome=outcome),self.assertRaises(IncrementalError):
                self.advance([file_event('file-1',outcome=outcome)])
            self.assertEqual(before,self.store.snapshot())
        self.advance([file_event('file-1',outcome='ACCESS_DENIED')])
        self.assertEqual(1,self.store.snapshot()['terminal_diagnostics'])

    def test_DI19_later_accessible_file_does_not_erase_terminal_history(self):
        self.advance([file_event('file-1',outcome='NOT_FOUND')])
        self.advance([self.capture()],terminal='poll')
        snapshot=self.store.snapshot()
        self.assertEqual(1,snapshot['terminal_diagnostics'])
        self.assertEqual(1,snapshot['logical_observations'])
        self.assertEqual(2,snapshot['occurrences'])

    def test_DI20_ambiguous_or_invalid_encoding_bytes_are_captured_blocked(self):
        events=[self.capture(self.data+self.data.splitlines(keepends=True)[4]),self.capture(b'\xff')]
        self.advance(events)
        results=self.store.inspect()[-1][1]['results']
        self.assertEqual(['CAPTURED_BLOCKED']*2,[r['status'] for r in results])
        self.assertEqual('CATCHUP',self.store.snapshot()['state']['phase'])
        self.assertFalse(self.store.snapshot()['reference_selected'])

    def test_DI21_changed_source_scope_error_and_caller_terminal_override_block(self):
        before=self.store.snapshot()
        for event in [self.capture(changed=True),file_event('file-1',outcome='SCOPE_INVALID')]:
            with self.assertRaises(IncrementalError):self.advance([event])
            self.assertEqual(before,self.store.snapshot())
        event=file_event('file-1',outcome='TIMEOUT');event['terminal']=True
        with self.assertRaisesRegex(IncrementalError,'INVALID_FIELDS'):self.advance([event])
        self.assertEqual(before,self.store.snapshot())
        drive=file_event('placeholder',outcome='SCOPE_INVALID');drive.update(change_type='drive',file_id=None)
        with self.assertRaisesRegex(IncrementalError,'BLOCKED_CONNECTOR'):self.advance([drive])
        self.assertEqual(before,self.store.snapshot())

    def test_DI22_scope_changes_need_a_new_root(self):
        before=self.store.snapshot()
        alternatives=[]
        for key in ['principal','corpus','drive','policy_version']:
            changed=deepcopy(self.scope);changed[key]='other';alternatives.append(changed)
        for key in ['project_id','connector_id']:
            changed=deepcopy(self.scope);changed[key]=str(uuid.uuid4());alternatives.append(changed)
        changed=deepcopy(self.scope);changed['allowlist'][0]['document_id']=str(uuid.uuid4());alternatives.append(changed)
        changed=deepcopy(self.scope);changed['allowlist'][0]['profile']='markdown-structure.v1';alternatives.append(changed)
        for changed in alternatives:
            with self.assertRaises(IncrementalError):FixtureStore(self.lab.root,self.lab.run_id,changed).snapshot()
        self.assertEqual(before,self.store.snapshot())
        with TemporaryFixtureLab(alternatives[0]) as other:self.assertEqual(0,other.store.snapshot()['version'])

    def test_DI23_malformed_pages_and_json_duplicate_keys_never_advance(self):
        original=self.command([]);before=self.store.snapshot()
        bads=[]
        for delta in [dict(phase='FOLLOWING'),dict(request_token='wrong'),dict(extra=True),dict(new_start_page_token='bad-inventory')]:
            bad=deepcopy(original);bad['page'].update(delta);bads.append(bad)
        for bad in bads:
            with self.assertRaises(IncrementalError):self.store.advance(bad)
        with self.assertRaises(IncrementalError):self.store.advance(b'{"schema":"x","schema":"y"}')
        with self.assertRaises(IncrementalError):self.store.advance(b'{"x":NaN}')
        self.assertEqual(before,self.store.snapshot())

    def test_DI24_limits_reject_whole_page_and_history_without_truncation(self):
        self.assertEqual(16,MAX_EVENTS);self.assertEqual(32*1024*1024,MAX_OBJECT);self.assertEqual(1024,MAX_COMMITS)
        before=self.store.snapshot()
        with self.assertRaisesRegex(IncrementalError,'PAGE_EVENT_LIMIT'):self.advance([self.capture()]*17)
        with self.assertRaisesRegex(IncrementalError,'OBJECT_LIMIT'):self.store.advance(b' '*(MAX_OBJECT+1))
        self.assertEqual(before,self.store.snapshot())
        # Exercise exactly the same boundary with a small synthetic ledger budget.
        with patch('source_ingest.incremental_fixture.MAX_COMMITS',4):
            self.advance([]);self.advance([],terminal='poll');self.advance([],terminal='poll')
            bounded=self.store.snapshot()
            with self.assertRaisesRegex(IncrementalError,'HISTORY_LIMIT'):self.advance([],terminal='poll')
            self.assertEqual(bounded,self.store.snapshot())

    def test_DI25_opaque_tokens_and_continuation_cycles(self):
        self.advance([],nxt='not-a-number:β')
        before=self.store.snapshot()
        with self.assertRaisesRegex(IncrementalError,'CONTINUATION_CYCLE'):self.advance([],nxt='not-a-number:β')
        self.assertEqual(before,self.store.snapshot())
        self.advance([],nxt='another-token')
        before=self.store.snapshot()
        with self.assertRaisesRegex(IncrementalError,'CONTINUATION_CYCLE'):self.advance([],nxt='not-a-number:β')
        self.assertEqual(before,self.store.snapshot())

    def test_DI26_corruption_blocks_without_selecting_orphans_or_repairing(self):
        self.advance([self.capture()])
        head_path=self.lab.root/'head.json';original_head=head_path.read_bytes()
        for body in [b'{',b'{}']:
            head_path.write_bytes(body)
            with self.assertRaises(IncrementalError):self.store.snapshot()
            self.assertEqual(body,head_path.read_bytes())
        head_path.write_bytes(original_head)
        head=json.loads(original_head);obj=self.lab.root/'objects'/(head['commit_sha256']+'.json');original_obj=obj.read_bytes()
        obj.write_bytes(original_obj+b' ')
        with self.assertRaisesRegex(IncrementalError,'CORRUPT_OBJECT'):self.store.snapshot()
        obj.write_bytes(original_obj)
        value=json.loads(original_obj);value['results'][0]['capture']['content_sha256']='0'*64
        forged=encode(value);sha=hashlib.sha256(forged).hexdigest();fake=self.lab.root/'objects'/(sha+'.json')
        fake.write_bytes(forged);fake.chmod(0o600)
        head['commit_sha256']=sha;head_path.write_bytes(encode(head))
        with self.assertRaisesRegex(IncrementalError,'CORRUPT_COMMIT'):self.store.snapshot()
        head_path.write_bytes(original_head)
        for field,bad in [('parent','0'*64),('parent',[]),('scope_sha256','0'*64)]:
            value=json.loads(original_obj);value[field]=bad
            blob=encode(value);key=hashlib.sha256(blob).hexdigest();forged_path=self.lab.root/'objects'/(key+'.json')
            forged_path.write_bytes(blob);forged_path.chmod(0o600)
            damaged_head=json.loads(original_head);damaged_head['commit_sha256']=key;head_path.write_bytes(encode(damaged_head))
            with self.assertRaises(IncrementalError):self.store.snapshot()
        head_path.write_bytes(original_head)
        obj.unlink()
        with self.assertRaises(IncrementalError):self.store.snapshot()
        self.assertEqual(original_head,head_path.read_bytes())

    def test_DI27_root_and_file_links_wrong_marks_and_other_roots_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix='d5-drive-sentinel-') as directory:
            sibling=Path(directory);sentinel=sibling/'sentinel';sentinel.write_bytes(b'SYNTHETIC_UNTOUCHED')
            alias=sibling/'alias';alias.symlink_to(self.lab.root,target_is_directory=True)
            with self.assertRaises(IncrementalError):FixtureStore(alias,self.lab.run_id,self.scope).snapshot()
            head=self.lab.root/'head.json';backup=head.read_bytes();head.unlink();head.symlink_to(sentinel)
            with self.assertRaises(IncrementalError):self.store.snapshot()
            self.assertEqual(b'SYNTHETIC_UNTOUCHED',sentinel.read_bytes())
            head.unlink();head.write_bytes(backup);head.chmod(0o600)
            os.link(head,sibling/'head-hardlink')
            with self.assertRaises(IncrementalError):self.store.snapshot()
            (sibling/'head-hardlink').unlink()
            owner=self.lab.root/'owner.json';data=json.loads(owner.read_bytes());data['run_id']=str(uuid.uuid4());owner.write_bytes(encode(data))
            with self.assertRaisesRegex(IncrementalError,'WRONG_OWNER'):self.store.snapshot()
            with TemporaryFixtureLab(self.scope) as other:
                with self.assertRaises(IncrementalError):FixtureStore(other.root,self.lab.run_id,self.scope).snapshot()
                self.assertEqual(0,other.store.snapshot()['version'])

    def test_DI28_cleanup_finally_owns_only_created_root_and_preserves_sentinels(self):
        with tempfile.TemporaryDirectory(prefix='d5-drive-sentinels-') as directory:
            sibling=Path(directory);sentinel=sibling/'keep';sentinel.write_bytes(b'KEEP_SYNTHETIC')
            root=None
            with self.assertRaisesRegex(RuntimeError,'fixture failure'):
                with TemporaryFixtureLab(self.scope) as owned:
                    root=owned.root
                    (root/'outside-link').symlink_to(sibling,target_is_directory=True)
                    raise RuntimeError('fixture failure')
            self.assertFalse(root.exists());self.assertEqual(b'KEEP_SYNTHETIC',sentinel.read_bytes())
            saved=self.lab.root;self.lab.root=sibling
            with self.assertRaisesRegex(IncrementalError,'CLEANUP_OWNERSHIP_CHANGED'):self.lab.close()
            self.lab.root=saved
            self.assertEqual(b'KEEP_SYNTHETIC',sentinel.read_bytes())


if __name__=='__main__':unittest.main()
