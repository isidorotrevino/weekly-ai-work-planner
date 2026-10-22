# SPDX-License-Identifier: GPL-3.0-only
"""I28 contract fixtures: actual in-process races, no HTTP or persisted domain."""
from copy import deepcopy
import json
import threading
import unittest
from unittest.mock import patch

from source_ingest import plane_fixture as pf

THREADS = []


def uid(n):
    return f'00000000-0000-4000-8000-{n:012d}'


class PlaneReconciliationTest(unittest.TestCase):
    def setUp(self):
        self.plane = pf.PlaneFixture(pf.capabilities())
        self.lab = pf.ReconciliationLab(self.plane)
        self.b = pf.binding(uid(1), uid(2), uid(3), uid(4), uid(5))
        self.t = pf.task(uid(2), uid(3))
        self.key = self.lab.bind(self.b, self.t)
        self.mid = self.prepare()
        self.cid = uid(20)

    def prepare(self, operation='CREATE'):
        mid = self.lab.prepare(uid(1), operation)
        old = self.lab._reviews[mid]['version']
        self.lab.review(mid, expected_version=old, decision='ACCEPT', reason='Explicit synthetic review')
        return mid

    def send(self, mid=None, cid=None, **kw):
        m = mid or self.mid
        return self.lab.dispatch(cid or self.cid, m, review_version=self.lab._reviews[m]['version'], **kw)

    def query(self, cid=None):
        cid = cid or self.cid
        return self.lab.reconcile(cid, expected_version=self.lab.command(cid)['version'])

    def unknown(self):
        self.plane.send_mode = 'LOSE_AFTER'
        value = self.send()
        self.assertEqual('UNKNOWN', value['result'])
        return value

    def created(self):
        value = self.send()
        self.assertEqual('EFFECT_CONFIRMED', value['result'])
        return value['effect_receipt']['remote_id']

    def local_edit(self, title='New local text'):
        self.t['row_version'] += 1
        self.t['title'] = title
        self.lab.edit_task(uid(1), self.t)

    def start(self, action):
        values = []
        def run():
            try:
                values.append(action())
            except Exception as exc:
                values.append(exc)
        child = threading.Thread(target=run)
        THREADS.append(child)
        child.start()
        return child, values

    def join(self, child):
        child.join(4)
        self.assertFalse(child.is_alive(), 'own fixture thread must finish')

    def test_PC01_stable_key_across_payload_package_and_command(self):
        original = self.key
        self.local_edit()
        newer = self.prepare()
        self.assertNotEqual(self.mid, newer)
        self.assertEqual(original, self.lab.manifest(newer)['key'])
        self.assertEqual(0, self.plane.write_calls)
        other = deepcopy(self.b); other['policy_version'] = 2
        self.assertEqual(original, pf.creation_key(other))

    def test_PC02_binding_uniqueness_and_remote_destination_uniqueness(self):
        other = deepcopy(self.b); other['binding_id'] = uid(50)
        with self.assertRaisesRegex(pf.PlaneError, 'BINDING_CONFLICT'):
            self.lab.bind(other, self.t)
        rid = self.created()
        b2 = pf.binding(uid(51), uid(2), uid(52), uid(4), uid(5))
        self.lab.bind(b2, pf.task(uid(2), uid(52)))
        mid = self.lab.prepare(uid(51))
        self.lab.review(mid, expected_version=0, decision='ACCEPT', reason='Synthetic')
        real_execute = self.plane.execute
        def wrong_destination(ticket, manifest):
            proof = real_execute(ticket, manifest)
            proof['remote_id'] = rid
            return proof
        with patch.object(self.plane, 'execute', side_effect=wrong_destination):
            value = self.send(mid, uid(53))
        self.assertEqual('DESTINATION_CONFLICT', value['conflict'])
        self.assertEqual('CONFLICT', value['result'])

    def test_PC03_reviewed_create_has_one_exact_effect_and_sanitized_receipt(self):
        value = self.send()
        self.assertEqual(1, self.plane.count())
        self.assertEqual('CURRENT', value['validity'][0])
        proof = value['effect_receipt']
        self.assertEqual(pf.digest(self.lab.manifest(self.mid)['payload']), proof['payload_sha256'])
        self.assertNotIn('Synthetic title', json.dumps(value))
        self.assertEqual(['fixture-preserved'], self.plane.read(proof['remote_id'])['foreign']['labels'])

    def test_PC04_lost_creation_response_blocks_another_package_and_command(self):
        self.unknown()
        self.local_edit()
        mid = self.prepare()
        with self.assertRaisesRegex(pf.PlaneError, 'BINDING_UNRESOLVED'):
            self.send(mid, uid(21))
        self.assertEqual(1, self.plane.write_calls)
        self.assertEqual(1, self.plane.count())

    def test_PC05_exact_query_recovers_creation_without_send(self):
        self.unknown()
        value = self.query()
        self.assertEqual('EFFECT_CONFIRMED', value['result'])
        self.assertEqual(1, self.plane.write_calls)
        self.assertEqual(1, self.plane.count())
        private = self.lab.inspect_command(self.cid)
        self.assertEqual(['DISPATCHED', 'SEND_RESULT', 'QUERY_RESULT'], [v['type'] for v in private['events']])
        private['events'].clear()
        self.assertEqual(3, len(self.lab.inspect_command(self.cid)['events']))

    def test_PC06_eventual_zero_never_authorizes_retry(self):
        self.unknown(); self.plane.query_mode = 'ZERO'
        for _ in range(3):
            self.assertEqual('UNKNOWN', self.query()['result'])
        with self.assertRaisesRegex(pf.PlaneError, 'RETRY_FORBIDDEN'):
            self.send(retry=True, expected_version=self.lab.command(self.cid)['version'])
        self.assertEqual(1, self.plane.write_calls)

    def test_PC07_strong_zero_with_inflight_ticket_stays_unknown(self):
        self.plane.send_mode = 'TIMEOUT_BEFORE'
        self.assertEqual('UNKNOWN', self.send()['result'])
        self.plane.query_mode = 'STRONG_ZERO'
        self.assertEqual('UNKNOWN', self.query()['result'])
        self.assertEqual(0, self.plane.count())
        self.assertEqual(1, self.plane.write_calls)

    def test_PC08_multiple_and_foreign_results_are_sticky_conflicts(self):
        for mode in ('DUPLICATES', 'FOREIGN'):
            with self.subTest(mode=mode):
                if mode != 'DUPLICATES': self.setUp()
                self.unknown(); self.plane.query_mode = mode
                value = self.query()
                self.assertEqual('CONFLICT', value['result'])
                self.plane.query_mode = 'EXACT'
                self.query()
                self.local_edit(); mid = self.prepare('UPDATE')
                with self.assertRaisesRegex(pf.PlaneError, 'BINDING_UNRESOLVED'):
                    self.send(mid, uid(21))
                self.assertEqual(1, self.plane.write_calls)

    def test_PC08_later_remote_edit_cannot_clear_prior_identity_conflict(self):
        self.unknown(); self.plane.query_mode = 'DUPLICATES'; self.query()
        self.plane.query_mode = 'EXACT'; value = self.query()
        rid = value['effect_receipt']['remote_id']
        self.plane.edit(rid, name='Subsequent remote edit')
        value = self.query()
        self.assertTrue(value['write_blocked_by_identity_conflict'])
        self.local_edit(); mid = self.prepare('UPDATE')
        with self.assertRaisesRegex(pf.PlaneError, 'BINDING_UNRESOLVED'):
            self.send(mid, uid(21))
        self.assertEqual(1, self.plane.write_calls)

    def test_PC09_fixture_unique_key_same_payload_recovers_other_payload_conflicts(self):
        manifest = self.lab.manifest(self.mid)
        first = self.plane.execute(uid(60), manifest)
        second = self.plane.execute(uid(61), manifest)
        self.assertEqual(first['remote_id'], second['remote_id'])
        other = deepcopy(manifest)
        other['task']['title'] = other['payload']['name'] = 'Different content'
        result = self.plane.execute(uid(62), other)
        self.assertEqual('CREATION_KEY_CONFLICT', result['code'])
        self.assertEqual(1, self.plane.count())

    def test_PC10_two_local_senders_and_two_query_publishers_compete(self):
        ready, release = threading.Event(), threading.Event()
        def pause():
            ready.set()
            if not release.wait(3): raise RuntimeError('fixture barrier timeout')
        self.plane.before_send = pause
        child, values = self.start(self.send)
        try:
            self.assertTrue(ready.wait(2))
            with self.assertRaisesRegex(pf.PlaneError, 'BINDING_UNRESOLVED'):
                self.send(cid=uid(21))
        finally:
            release.set(); self.join(child)
        self.assertIsInstance(values[0], dict)
        self.assertEqual(1, self.plane.count())
        self.plane.before_send = None
        barrier = threading.Barrier(2, timeout=3)
        self.plane.before_query = barrier.wait
        version = self.lab.command(self.cid)['version']
        a, av = self.start(lambda: self.lab.reconcile(self.cid, expected_version=version))
        b, bv = self.start(lambda: self.lab.reconcile(self.cid, expected_version=version))
        self.join(a); self.join(b)
        self.assertEqual(1, sum(type(v[0]) is dict for v in (av, bv)))
        self.assertEqual(['CONFLICT_LEDGER'], [str(v[0]) for v in (av, bv) if isinstance(v[0], Exception)])
        self.assertEqual(1, self.plane.write_calls)

    def test_PC10_fixture_creation_uniqueness_is_atomic_under_two_threads(self):
        barrier = threading.Barrier(2, timeout=3)
        self.plane.before_send = barrier.wait
        m = self.lab.manifest(self.mid)
        a, av = self.start(lambda: self.plane.execute(uid(70), m))
        b, bv = self.start(lambda: self.plane.execute(uid(71), m))
        self.join(a); self.join(b)
        self.assertEqual(av[0]['remote_id'], bv[0]['remote_id'])
        self.assertEqual(1, self.plane.count())

    def test_PC11_unproven_match_and_proven_historical_edit_differ(self):
        self.unknown(); self.plane.query_mode = 'UNPROVEN'
        self.assertEqual('UNKNOWN', self.query()['result'])
        rid = next(iter(self.plane._items))
        self.plane.edit(rid, name='Remote edit')
        self.plane.query_mode = 'EXACT'
        value = self.query()
        self.assertEqual('EFFECT_CONFIRMED', value['result'])
        self.assertEqual('REMOTE_EDIT', value['conflict'])
        self.assertEqual('Remote edit', self.plane.read(rid)['payload']['name'])
        self.assertEqual(1, self.plane.write_calls)

    def test_PC12_local_change_before_send_invalidates_approval(self):
        self.local_edit()
        with self.assertRaisesRegex(pf.PlaneError, 'STALE_PACKAGE'): self.send()
        self.assertEqual(0, self.plane.write_calls)

    def test_PC13_review_revocation_and_replacement_require_exact_version(self):
        for decision in ('REJECT', 'ACCEPT'):
            self.lab.review(self.mid, expected_version=self.lab._reviews[self.mid]['version'],
                            decision=decision, reason='New explicit decision')
            with self.assertRaisesRegex(pf.PlaneError, 'STALE_PACKAGE'):
                self.lab.dispatch(self.cid, self.mid, review_version=1)
        self.assertEqual(0, self.plane.write_calls)

    def test_PC14_binding_policy_and_capability_changes_invalidate_manifest(self):
        self.lab.change_policy(uid(1), 2)
        with self.assertRaisesRegex(pf.PlaneError, 'STALE_PACKAGE'): self.send()
        self.setUp()
        self.plane.change_card(pf.capabilities(release=2))
        with self.assertRaisesRegex(pf.PlaneError, 'STALE_PACKAGE'): self.send()
        self.assertEqual(0, self.plane.write_calls)

    def test_PC15_mutation_hash_and_command_request_conflict(self):
        raw = self.lab._manifests[self.mid]
        self.lab._manifests[self.mid] = raw + b' '
        with self.assertRaisesRegex(pf.PlaneError, 'MANIFEST_CORRUPT'): self.send()
        self.lab._manifests[self.mid] = raw
        self.created()
        self.local_edit(); mid = self.prepare('UPDATE')
        with self.assertRaisesRegex(pf.PlaneError, 'COMMAND_CONFLICT'): self.send(mid)
        self.assertEqual(1, self.plane.write_calls)

    def test_PC16_local_edit_during_send_preserves_actual_effect_as_stale(self):
        self.plane.before_send = self.local_edit
        value = self.send()
        self.assertEqual('EFFECT_CONFIRMED', value['result'])
        self.assertEqual(['STALE_LOCAL'], value['validity'])
        rid = value['effect_receipt']['remote_id']
        self.assertEqual('Synthetic title', self.plane.read(rid)['payload']['name'])
        self.assertEqual(1, self.plane.write_calls)

    def test_PC17_revocation_during_lost_response_allows_only_historical_read(self):
        self.plane.before_send = lambda: self.lab.review(self.mid, expected_version=1,
                                                        decision='REJECT', reason='Revoked in flight')
        value = self.unknown()
        self.assertEqual(['STALE_REVIEW'], value['validity'])
        self.assertEqual('EFFECT_CONFIRMED', self.query()['result'])
        self.assertEqual(1, self.plane.write_calls)

    def test_PC18_confirmed_historical_effect_does_not_become_current(self):
        self.unknown(); self.local_edit()
        self.lab.review(self.mid, expected_version=1, decision='REJECT', reason='Revoked')
        value = self.query()
        self.assertEqual(['STALE_LOCAL', 'STALE_REVIEW'], value['validity'])
        self.assertEqual('EFFECT_CONFIRMED', value['result'])
        receipt = value['effect_receipt']
        self.assertEqual(receipt, self.lab.command(self.cid)['effect_receipt'])
        self.assertEqual(1, self.plane.write_calls)

    def test_PC19_replay_never_restores_old_text(self):
        rid = self.created(); original = self.lab.command(self.cid)['effect_receipt']
        self.local_edit(); mid = self.prepare('UPDATE')
        self.send(mid, uid(21))
        self.plane.edit(rid, name='Later remote edit')
        replay = self.lab.dispatch(self.cid, self.mid, review_version=1)
        self.assertEqual(original, replay['effect_receipt'])
        self.assertEqual('Later remote edit', self.plane.read(rid)['payload']['name'])
        self.assertEqual(2, self.plane.write_calls)

    def test_PC20_domain_lock_is_released_during_provider_callback(self):
        def callback():
            child, values = self.start(self.local_edit)
            self.join(child)
            self.assertEqual([None], values)
        self.plane.before_send = callback
        value = self.send()
        self.assertEqual('EFFECT_CONFIRMED', value['result'])
        self.assertEqual(['STALE_LOCAL'], value['validity'])

    def test_PC21_new_reviewed_update_keeps_created_identity_and_foreign_fields(self):
        rid = self.created(); self.local_edit()
        mid = self.lab.prepare(uid(1), 'UPDATE')
        with self.assertRaisesRegex(pf.PlaneError, 'STALE_PACKAGE'):
            self.lab.dispatch(uid(21), mid, review_version=1)
        self.lab.review(mid, expected_version=0, decision='ACCEPT', reason='New update')
        value = self.send(mid, uid(21))
        self.assertEqual(rid, value['effect_receipt']['remote_id'])
        item = self.plane.read(rid)
        self.assertEqual('New local text', item['payload']['name'])
        self.assertEqual(['fixture-preserved'], item['foreign']['labels'])
        self.assertEqual(1, self.plane.count())

    def test_PC22_precondition_detects_before_during_and_ABA_remote_edits(self):
        for mode in ('BEFORE', 'DURING', 'ABA'):
            with self.subTest(mode=mode):
                if mode != 'BEFORE': self.setUp()
                rid = self.created(); self.local_edit(); mid = self.prepare('UPDATE')
                def edit():
                    self.plane.edit(rid, name='Remote edit')
                    if mode == 'ABA': self.plane.edit(rid, name='Synthetic title')
                if mode == 'DURING': self.plane.before_send = edit
                else: edit()
                value = self.send(mid, uid(21))
                self.assertEqual('REMOTE_PRECONDITION', value['conflict'])
                self.assertNotEqual('New local text', self.plane.read(rid)['payload']['name'])
                self.assertEqual(['fixture-preserved'], self.plane.read(rid)['foreign']['labels'])

    def test_PC23_timeout_malformed_and_local_ack_remain_unknown_and_sanitized(self):
        for mode in ('TIMEOUT_BEFORE', 'MALFORMED_AFTER', 'ACK_AFTER', 'AMBIGUOUS_429'):
            with self.subTest(mode=mode):
                if mode != 'TIMEOUT_BEFORE': self.setUp()
                self.plane.send_mode = mode
                value = self.send()
                self.assertEqual('UNKNOWN', value['result'])
                self.assertNotIn('fixture-private-body', json.dumps(value))
                self.assertNotIn('Synthetic title', json.dumps(value))
                self.assertEqual(1, self.plane.write_calls)

    def test_PC24_update_lost_response_then_remote_edit_recovers_without_patch(self):
        rid = self.created(); self.local_edit(); mid = self.prepare('UPDATE')
        self.plane.send_mode = 'LOSE_AFTER'
        value = self.send(mid, uid(21))
        self.assertEqual('UNKNOWN', value['result'])
        self.plane.edit(rid, name='Concurrent newer edit')
        value = self.query(uid(21))
        self.assertEqual('EFFECT_CONFIRMED', value['result'])
        self.assertEqual('REMOTE_EDIT', value['conflict'])
        self.assertEqual('Concurrent newer edit', self.plane.read(rid)['payload']['name'])
        self.assertEqual(2, self.plane.write_calls)

    def test_PC25_conclusive_rejection_is_not_an_effect_or_automatic_retry(self):
        self.plane.send_mode = 'REJECT'
        value = self.send()
        self.assertEqual('REJECTED_NO_EFFECT', value['result'])
        self.assertEqual(0, self.plane.count())
        self.assertEqual(1, self.plane.write_calls)
        self.assertEqual(value, self.send())

    def test_PC26_429_requires_no_effect_and_logical_retry_tick(self):
        self.plane.send_mode = 'RATE_LIMIT'
        value = self.send()
        with self.assertRaisesRegex(pf.PlaneError, 'RETRY_NOT_ELIGIBLE'):
            self.send(retry=True, expected_version=value['version'])
        self.lab.advance_clock(2)
        result = self.send(retry=True, expected_version=value['version'])
        self.assertEqual('EFFECT_CONFIRMED', result['result'])
        self.assertEqual(2, result['attempts'])
        self.setUp(); self.plane.send_mode = 'AMBIGUOUS_429'
        value = self.send(); self.lab.advance_clock(100)
        with self.assertRaisesRegex(pf.PlaneError, 'RETRY_FORBIDDEN'):
            self.send(retry=True, expected_version=value['version'])

    def test_PC27_invalid_retry_delay_budget_and_stale_state_block(self):
        for delay in (None, True, -1, '2'):
            self.setUp(); self.plane.send_mode = 'RATE_LIMIT'; self.plane.retry_after = delay
            value = self.send(); self.lab.advance_clock(100)
            with self.assertRaisesRegex(pf.PlaneError, 'RETRY_NOT_ELIGIBLE'):
                self.send(retry=True, expected_version=value['version'])
        self.setUp()
        for i in range(3):
            self.plane.send_mode = 'REJECT'
            value = self.send(**(dict(retry=True, expected_version=value['version']) if i else {}))
        with self.assertRaisesRegex(pf.PlaneError, 'ATTEMPT_BUDGET'):
            self.send(retry=True, expected_version=value['version'])
        with self.assertRaisesRegex(pf.PlaneError, 'PACKAGE_COMMAND_CONFLICT'):
            self.send(cid=uid(21))
        self.setUp(); self.plane.send_mode = 'REJECT'; value = self.send(); self.local_edit()
        with self.assertRaisesRegex(pf.PlaneError, 'STALE_PACKAGE'):
            self.send(retry=True, expected_version=value['version'])

    def test_PC28_explicit_retry_keeps_key_payload_and_history_new_attempt(self):
        self.plane.send_mode = 'REJECT'; value = self.send()
        value = self.send(retry=True, expected_version=value['version'])
        private = self.lab.inspect_command(self.cid)
        self.assertEqual(2, len(set(private['attempts'])))
        self.assertEqual(4, len(private['events']))
        self.assertEqual('EFFECT_CONFIRMED', value['result'])
        self.assertEqual(1, self.plane.count())

    def test_PC29_query_budget_and_missing_confirmed_destination_do_not_recreate(self):
        self.unknown(); self.plane.query_mode = 'ZERO'
        for _ in range(6): self.query()
        with self.assertRaisesRegex(pf.PlaneError, 'QUERY_BUDGET'): self.query()
        self.assertEqual('UNKNOWN', self.lab.command(self.cid)['result'])
        self.setUp(); rid = self.created(); self.plane.remove(rid)
        value = self.query()
        self.assertEqual('REMOTE_MISSING', value['conflict'])
        self.assertEqual('EFFECT_CONFIRMED', value['result'])
        with self.assertRaisesRegex(pf.PlaneError, 'ALREADY_CREATED'): self.prepare()
        self.assertEqual(1, self.plane.write_calls)

    def test_PC30_no_memory_restart_or_missing_capability_authority(self):
        self.unknown()
        with self.assertRaisesRegex(pf.PlaneError, 'LEDGER_RESTART_UNSUPPORTED'):
            pf.ReconciliationLab(self.plane)
        empty = pf.ReconciliationLab(pf.PlaneFixture())
        with self.assertRaisesRegex(pf.PlaneError, 'COMMAND_REQUIRED'): empty.command(self.cid)
        empty.bind(self.b, self.t)
        mid = empty.prepare(uid(1)); empty.review(mid, expected_version=0, decision='ACCEPT', reason='Synthetic')
        with self.assertRaisesRegex(pf.PlaneError, 'CAPABILITY_REQUIRED'):
            empty.dispatch(uid(21), mid, review_version=1)
        self.assertEqual(0, empty.plane.write_calls)

    def test_PC31_closed_schemas_types_text_and_manifest_limits(self):
        for change in ({'mode':'REAL'}, {'token':'forbidden'}, {'binding_id':'bad'}, {'policy_version':True}):
            b = dict(self.b, **change)
            with self.assertRaises(pf.PlaneError): self.lab.bind(b, self.t)
        bad = dict(self.t, title='x' * 8193)
        with self.assertRaisesRegex(pf.PlaneError, 'INVALID_TEXT'): self.lab.edit_task(uid(1), bad)
        with self.assertRaisesRegex(pf.PlaneError, 'MANIFEST_BUDGET'):
            with patch.object(pf, 'MAX_MANIFEST', 1): self.lab.prepare(uid(1))
        with self.assertRaisesRegex(pf.PlaneError, 'INVALID_ID'): self.lab.dispatch('not-id', self.mid, review_version=1)
        with self.assertRaisesRegex(pf.PlaneError, 'INVALID_INTEGER'): self.lab.dispatch(self.cid, self.mid, review_version=True)
        with self.assertRaisesRegex(pf.PlaneError, 'INVALID_MANIFEST_ID'): self.lab.manifest(['private-body'])
        with self.assertRaisesRegex(pf.PlaneError, 'BINDING_REQUIRED'): self.lab.edit_task(uid(999), self.t)
        with self.assertRaisesRegex(pf.PlaneError, 'BINDING_REQUIRED'): self.lab.change_policy(uid(999), 2)
        raw = self.lab.manifest(self.mid); raw['extra'] = 'forbidden'
        with self.assertRaisesRegex(pf.PlaneError, 'INVALID_SHAPE'): self.plane.execute(uid(90), raw)
        self.assertEqual(0, self.plane.write_calls)

    def test_PC31_binding_and_command_budget_are_not_truncated(self):
        for i in range(63):
            b = pf.binding(uid(1000+i), uid(2), uid(2000+i), uid(4), uid(5))
            self.lab.bind(b, pf.task(uid(2), uid(2000+i)))
        with self.assertRaisesRegex(pf.PlaneError, 'BINDING_BUDGET'):
            self.lab.bind(pf.binding(uid(90), uid(2), uid(91), uid(4), uid(5)), pf.task(uid(2), uid(91)))
        self.assertEqual(64, self.lab.summary()['bindings'])
        for i in range(128):
            if i:
                self.local_edit(f'Synthetic change {i}')
                self.mid = self.prepare()
            self.plane.send_mode = 'REJECT'
            self.send(cid=uid(3000+i))
        self.local_edit('Budget reached'); mid = self.prepare()
        with self.assertRaisesRegex(pf.PlaneError, 'COMMAND_BUDGET'): self.send(mid, uid(4000))
        self.assertEqual(128, self.lab.summary()['commands'])
        self.assertEqual(128, self.plane.write_calls)
        self.assertEqual(0, self.plane.count())
        self.assertEqual((64, 128, 3, 6, 65536, 8192), (pf.MAX_BINDINGS, pf.MAX_COMMANDS,
                         pf.MAX_ATTEMPTS, pf.MAX_QUERIES, pf.MAX_MANIFEST, pf.MAX_TEXT))

    def test_PC31_actual_utf8_manifest_byte_limit_blocks_without_truncation(self):
        self.t.update(title='😀' * 8192, description='😀' * 8192, row_version=2)
        self.lab.edit_task(uid(1), self.t)
        with self.assertRaisesRegex(pf.PlaneError, 'MANIFEST_BUDGET'): self.lab.prepare(uid(1))
        self.assertEqual(0, self.plane.write_calls)

    def test_PC15_invalid_query_proof_or_body_never_confirms(self):
        for mode in ('BAD_PROOF', 'MALFORMED', 'ERROR'):
            self.setUp(); self.unknown(); self.plane.query_mode = mode
            value = self.query()
            self.assertIn(value['result'], ('UNKNOWN', 'CONFLICT'))
            self.assertIsNone(value['effect_receipt'])
            self.assertNotIn('fixture-private-body', json.dumps(value))
            self.assertEqual(1, self.plane.write_calls)

    def test_PC15_contradictory_negative_cannot_replace_confirmed_effect(self):
        self.created()
        original = self.lab.command(self.cid)['effect_receipt']
        ticket = self.lab.inspect_command(self.cid)['attempts'][0]
        self.plane._proofs[ticket] = dict(status='REJECTED_NO_EFFECT', code='REJECT',
                                         ticket=ticket, manifest_sha256=self.mid)
        value = self.query()
        self.assertEqual('EFFECT_CONFIRMED', value['result'])
        self.assertEqual('PROOF_CONFLICT', value['conflict'])
        self.assertEqual(original, value['effect_receipt'])
        self.assertTrue(value['write_blocked_by_identity_conflict'])

    def test_PC20_query_callback_can_edit_domain_outside_lock(self):
        self.unknown()
        def callback():
            child, values = self.start(self.local_edit)
            self.join(child)
            self.assertEqual([None], values)
        self.plane.before_query = callback
        value = self.query()
        self.assertEqual('EFFECT_CONFIRMED', value['result'])
        self.assertEqual(['STALE_LOCAL'], value['validity'])

    def test_PC10_query_during_inflight_send_recovers_after_publish_CAS_conflict(self):
        ready, release = threading.Event(), threading.Event()
        def pause():
            ready.set()
            if not release.wait(3): raise RuntimeError('fixture barrier timeout')
        self.plane.before_send = pause
        child, values = self.start(self.send)
        try:
            self.assertTrue(ready.wait(2))
            self.assertEqual('UNKNOWN', self.query()['result'])
        finally:
            release.set(); self.join(child)
        self.assertIsInstance(values[0], pf.PlaneError)
        self.assertEqual('CONFLICT_LEDGER', str(values[0]))
        self.assertEqual('EFFECT_CONFIRMED', self.query()['result'])
        self.assertEqual(1, self.plane.count())
        self.assertEqual(1, self.plane.write_calls)

    def test_PC24_unknown_update_blocks_newer_reviewed_update(self):
        self.created(); self.local_edit(); mid = self.prepare('UPDATE')
        self.plane.send_mode = 'LOSE_AFTER'; self.send(mid, uid(21))
        self.local_edit('Another local change'); newer = self.prepare('UPDATE')
        with self.assertRaisesRegex(pf.PlaneError, 'BINDING_UNRESOLVED'):
            self.send(newer, uid(22))
        self.assertEqual(2, self.plane.write_calls)

    def test_PC32_summary_has_no_operational_authority_or_real_effects(self):
        self.created()
        summary = self.lab.summary()
        self.assertFalse(summary['D5_closed'])
        self.assertFalse(summary['operational_activation'])
        self.assertEqual(0, summary['real_remote_requests'])
        self.assertEqual(0, summary['persistent_D2_writes'])
        self.assertEqual('VOLATILE_MEMORY', summary['storage'])
        self.assertEqual([f'G{i:02}' for i in range(1,8)], summary['global_gaps_open'])
        self.assertFalse(any(t.is_alive() for t in THREADS))


if __name__ == '__main__':
    unittest.main()
