# SPDX-License-Identifier: GPL-3.0-only
"""I41 HC01-HC24 obligations, implemented only in the new I42 harness."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from testing.durable_concurrency import support as s


def held_child(conn):
    conn.send(dict(event='READY'))
    conn.recv()


class DurableConcurrencyTest(unittest.TestCase):
    def run_scenario(self, case, path, exercise):
        value = s.Scenario(case, path)
        success = False
        try:
            exercise(value)
            value.reopen()
            success = True
        finally:
            value.close(success)

    def ledger(self, case, path, winner):
        def exercise(v):
            v.prepare()
            before_remote = s.independent(v.lab.root / 'remote')
            jobs = [dict(action='reconcile', role='CLIENT', operation='QUERY_RESULT', sid=v.send['send_id']),
                    dict(action='perform', role='CLIENT', operation='RESULT', args=v.result_args())]
            outcomes = v.race(jobs, winner)
            self.assertEqual(outcomes[winner]['status'], 'OK')
            self.assertEqual(outcomes[1-winner]['code'], 'CONFLICT_HEAD')
            observed = v.observe('ledger_round_1')['client']
            state = observed['state']; send = state['sends'][v.send['send_id']]
            self.assertEqual((send['ledger_version'], send['status'], send['proof']), (2, 'EFFECT_CONFIRMED', v.proof))
            self.assertFalse(state['pending'])
            fresh = s.open_client(v.value)
            s.expect_error('CONFLICT_LEDGER', fresh.perform, 'RESULT', v.result_args())
            self.assertEqual(s.independent(v.lab.root/'client'), observed)
            v.event('EXPECTED_REJECTION', role='CLIENT', operation='RESULT', mode='CREATE', round=2, code='CONFLICT_LEDGER', expected_ledger=1, current_ledger=2)
            s.open_client(v.value).reconcile(v.send['send_id'])
            state = v.observe('ledger_round_3')['client']['state']; send = state['sends'][v.send['send_id']]
            self.assertEqual((send['ledger_version'], send['proof'], send['status']), (3, v.proof, 'EFFECT_CONFIRMED'))
            self.assertEqual(s.independent(v.lab.root/'remote'), before_remote)
            self.assertEqual(len(before_remote['state']['entities']), 1)
            v.event('EXPLICIT_RECONCILE', role='CLIENT', operation='QUERY/RESULT', mode='CREATE', round=3, ledger=3, proof_sha256=s.digest(v.proof))
        self.run_scenario(case, path, exercise)

    def revoke(self, case, path, winner):
        def exercise(v):
            v.prepare()
            before_remote = s.independent(v.lab.root/'remote')
            args = dict(stage='PROJECTION', manifest_id=v.mid, expected_version=1, decision='REVOKE', reason_code='SYNTHETIC_REVIEW')
            jobs = [dict(action='perform', role='CLIENT', operation='RESULT', args=v.result_args()),
                    dict(action='perform', role='CLIENT', operation='REVIEW', args=args)]
            outcomes = v.race(jobs, winner)
            self.assertEqual(outcomes[winner]['status'], 'OK')
            self.assertEqual(outcomes[1-winner]['code'], 'CONFLICT_HEAD')
            row = v.lab.fresh().summary()['sends'][0]
            if winner == 0:
                self.assertEqual((row['status'], row['validity']), ('EFFECT_CONFIRMED', 'CURRENT'))
                v.lab.fresh().review('PROJECTION', v.mid, decision='REVOKE', version=1)
                operation = 'REVIEW'
            else:
                self.assertEqual((row['status'], row['validity']), ('UNKNOWN', 'STALE'))
                v.lab.fresh().reconcile(v.send['send_id'])
                operation = 'QUERY/RESULT'
            v.event('EXPLICIT_FOLLOWUP', role='CLIENT', operation=operation, mode='CREATE', round=2)
            final = v.observe('revoked_final')['client']['state']
            row = v.lab.fresh().summary()['sends'][0]
            self.assertEqual((row['status'], row['validity']), ('EFFECT_CONFIRMED', 'STALE'))
            review = final['reviews']['PROJECTION:'+v.mid]
            self.assertEqual((review['version'], review['decision']), (2, 'REVOKE'))
            self.assertEqual(len(final['sends']), 1)
            self.assertFalse(final['pending'])
            self.assertEqual(s.independent(v.lab.root/'remote'), before_remote)
        self.run_scenario(case, path, exercise)

    def update(self, case, path, winner):
        def exercise(v):
            v.update()
            jobs = [dict(action='edit', role='REMOTE', operation='EDIT', mode='UPDATE', cid=s.uid(), args=v.edit_args),
                    dict(action='execute', role='REMOTE', operation='EXECUTE', mode='UPDATE', ticket=v.send['ticket'], manifest=v.manifest)]
            outcomes = v.race(jobs, winner)
            self.assertEqual(outcomes[winner]['status'], 'OK')
            if winner == 1:
                self.assertEqual(outcomes[0]['code'], 'REMOTE_CAS')
            else:
                self.assertEqual(outcomes[1]['status'], 'OK')
            remote = s.independent(v.lab.root/'remote')
            proof = remote['state']['tickets'][v.send['ticket']]
            entity = remote['state']['entities'][v.base['id']]
            self.assertEqual(entity['version'], v.base['version']+1)
            self.assertEqual(entity['foreign'], dict(sentinel='keep'))
            self.assertEqual(len(remote['state']['entities']), 1)
            self.assertEqual(len(remote['state']['tickets']), 2)
            self.assertEqual(remote['head']['seq']-v.before_update['remote']['head']['seq'], 2 if winner == 0 else 1)
            self.assertEqual(len(remote['state']['receipts'])-len(v.before_update['remote']['state']['receipts']), 2 if winner == 0 else 1)
            if winner == 0:
                self.assertEqual((proof['status'], proof['code'], proof['retry_tick']), ('NO_EFFECT', 'REMOTE_PRECONDITION', None))
                self.assertEqual(entity['payload'], v.edit_args['payload'])
            else:
                self.assertEqual(proof['status'], 'EFFECT_CONFIRMED')
                self.assertEqual(entity['payload'], v.manifest['payload'])
            v.lab.fresh().perform('RESULT', v.result_args(proof))
            before_retry = s.independent(v.lab.root/'client')
            s.expect_error('RETRY_NOT_ELIGIBLE' if winner == 0 else 'RETRY_FORBIDDEN', v.lab.fresh().dispatch, v.mid, 1, send_id=v.send['send_id'], retry=True)
            self.assertEqual(s.independent(v.lab.root/'client'), before_retry)
            v.event('UPDATE_RESULT_PUBLISHED', role='CLIENT', operation='RESULT', mode='UPDATE', round=2, proof_sha256=s.digest(proof), code=proof['code'], applied_version=proof['applied_version'], remote_head_delta=remote['head']['seq']-v.before_update['remote']['head']['seq'])
        self.run_scenario(case, path, exercise)

    def conflict(self, case, path):
        def exercise(v):
            v.prepare()
            before_remote = s.independent(v.lab.root/'remote')
            bad = deepcopy(v.proof); bad['manifest_hash'] = '0'*64
            v.lab.client.perform('RESULT', v.result_args(bad))
            state = v.observe('incompatible_first')['client']['state']
            self.assertTrue(state['sends'][v.send['send_id']]['hard_conflict'])
            v.lab.fresh().reconcile(v.send['send_id'])
            state = v.observe('correct_later')['client']['state']
            send = state['sends'][v.send['send_id']]
            self.assertEqual((send['status'], send['hard_conflict'], send['ledger_version']), ('CONFLICT', True, 3))
            self.assertIsNone(send['proof'])
            s.expect_error('BINDING_UNRESOLVED', v.lab.fresh().dispatch, v.mid, 1)
            self.assertEqual(s.independent(v.lab.root/'remote'), before_remote)
            v.event('STICKY_CONFLICT', role='CLIENT', operation='RESULT/QUERY/RESULT', mode='CREATE', incompatible_sha256=s.digest(bad), correct_sha256=s.digest(v.proof))
        self.run_scenario(case, path, exercise)

    def edit_control(self, case, path, foreign=False):
        def exercise(v):
            v.update()
            if foreign:
                v.lab.remote.edit(v.base['id'], foreign=dict(sentinel='edited_foreign'))
                v.observe('foreign_edit_committed')
                edits = 1
            else:
                v.lab.remote.edit(v.base['id'], payload=v.edit_args['payload'])
                v.observe('aba_edit_one_committed')
                v.lab.remote.edit(v.base['id'], payload=v.base['payload'])
                v.observe('aba_edit_two_committed')
                edits = 2
            before_execute = s.independent(v.lab.root/'remote')
            entity = before_execute['state']['entities'][v.base['id']]
            self.assertEqual(entity['version'], v.base['version']+edits)
            self.assertEqual(entity['payload'], v.base['payload'])
            proof = v.lab.remote.execute(v.send['ticket'], v.manifest)
            self.assertEqual((proof['status'], proof['code'], proof['retry_tick']), ('NO_EFFECT', 'REMOTE_PRECONDITION', None))
            remote = s.independent(v.lab.root/'remote')
            self.assertEqual(remote['state']['entities'][v.base['id']], entity)
            self.assertEqual(remote['head']['seq'], before_execute['head']['seq']+1)
            self.assertEqual(entity['foreign'], dict(sentinel='edited_foreign' if foreign else 'keep'))
            v.lab.fresh().perform('RESULT', v.result_args(proof))
            s.expect_error('RETRY_NOT_ELIGIBLE', v.lab.fresh().dispatch, v.mid, 1, send_id=v.send['send_id'], retry=True)
            v.event('CONTROLLED_SEQUENCE', role='REMOTE', operation='EDIT/EXECUTE', mode='UPDATE', order='FOREIGN_FIRST' if foreign else 'ABA_FIRST', edit_commits=edits, version=entity['version'], proof_sha256=s.digest(proof))
        self.run_scenario(case, path, exercise)

    def revoked_before_issue(self, case, path):
        def exercise(v):
            v.prepare(issue=False)
            v.lab.client.review('PROJECTION', v.mid, decision='REVOKE', version=1)
            before = v.observe('before_blocked_issue')
            s.expect_error('REVIEW_REQUIRED', v.lab.fresh().dispatch, v.mid, 1)
            self.assertEqual(v.observe('after_blocked_issue'), before)
            self.assertFalse(before['client']['state']['sends'])
            self.assertFalse(before['remote']['state']['tickets'])
            self.assertFalse(before['remote']['state']['entities'])
            v.event('EXPECTED_REJECTION', role='CLIENT', operation='ISSUE', mode='CREATE', order='REVOKE_FIRST', code='REVIEW_REQUIRED')
        self.run_scenario(case, path, exercise)

    def test_HC01(self): self.ledger('HC01', 'T', 1)
    def test_HC02(self): self.ledger('HC02', 'T', 0)
    def test_HC03(self): self.ledger('HC03', 'R', 1)
    def test_HC04(self): self.ledger('HC04', 'R', 0)
    def test_HC05(self): self.revoke('HC05', 'T', 0)
    def test_HC06(self): self.revoke('HC06', 'T', 1)
    def test_HC07(self): self.revoke('HC07', 'R', 0)
    def test_HC08(self): self.revoke('HC08', 'R', 1)
    def test_HC09(self): self.update('HC09', 'T', 0)
    def test_HC10(self): self.update('HC10', 'T', 1)
    def test_HC11(self): self.update('HC11', 'R', 0)
    def test_HC12(self): self.update('HC12', 'R', 1)
    def test_HC13(self): self.conflict('HC13', 'T')
    def test_HC14(self): self.conflict('HC14', 'R')
    def test_HC15(self): self.edit_control('HC15', 'T')
    def test_HC16(self): self.edit_control('HC16', 'R')
    def test_HC17(self): self.edit_control('HC17', 'T', foreign=True)
    def test_HC18(self): self.edit_control('HC18', 'R', foreign=True)
    def test_HC19(self): self.revoked_before_issue('HC19', 'T')
    def test_HC20(self): self.revoked_before_issue('HC20', 'R')

    def test_HC21(self):
        def exercise(v):
            with self.assertRaisesRegex(AssertionError, 'PROBE_NOT_HELD'):
                s.probe_locked(v.lab.root/'client')
            pair = s.start(held_child, (), dict(case='HC21', actor='negative_timeout', path='T'))
            v.children.append(pair)
            try:
                self.assertEqual(s.receive(pair[1])['event'], 'READY')
                with self.assertRaisesRegex(AssertionError, 'CONTROL_TIMEOUT'):
                    s.receive(pair[1], timeout=0.02)
            finally:
                s.stop_owned([pair])
            # A missing/mislabelled READY is rejected, never inferred from elapsed time.
            with self.assertRaisesRegex(AssertionError, 'MISSING_READY'):
                s.expect_event(dict(event='DONE'), 'READY')
            v.event('NEGATIVE_CONTROLS', operation='CONTROL', free_probe_rejected=True, missing_ready_rejected=True, reduced_timeout_seconds=0.02, timeout_child_exitcode=pair[0].exitcode)
        self.run_scenario('HC21', 'T', exercise)

    def test_HC22(self):
        for path in ('T', 'R'):
            def exercise(v):
                saved = v.lab.home/'owned_run_saved'
                v.lab.root.rename(saved); v.lab.root.mkdir()
                try:
                    s.expect_error('CLEANUP_OWNERSHIP', v.lab.close)
                    self.assertTrue(v.lab.sentinel.exists())
                finally:
                    v.lab.root.rmdir(); saved.rename(v.lab.root)
                sentinel = v.lab.sentinel.read_bytes()
                v.lab.sentinel.write_bytes(b'SYNTHETIC_CONTROL_CHANGED')
                try:
                    s.expect_error('SENTINEL_CHANGED', v.lab.close)
                finally:
                    v.lab.sentinel.write_bytes(sentinel)
                owner = v.lab.root/'owner.json'; raw = owner.read_bytes()
                owner.write_bytes(b'{}')
                try:
                    s.expect_error('CLEANUP_MARKER', v.lab.close)
                    self.assertTrue(v.lab.sentinel.exists())
                finally:
                    owner.write_bytes(raw)
                link = v.lab.root/'client'/'own_control_link'
                link.symlink_to(v.lab.sentinel)
                try:
                    s.expect_error('CLEANUP_SYMLINK', v.lab.close)
                    self.assertEqual(v.lab.sentinel.read_bytes(), b'SYNTHETIC_SIBLING')
                finally:
                    link.unlink()
                v.event('OWNERSHIP_NEGATIVES', operation='CLEANUP', inode_rejected=True, changed_sentinel_rejected=True, marker_rejected=True, link_rejected=True, sentinel_preserved=True)
            self.run_scenario('HC22', path, exercise)

    def test_HC23(self):
        def exercise(v):
            with tempfile.TemporaryDirectory(prefix='d5-i42-inventory-') as directory:
                s.EXTRA_ROOTS.append(directory)
                path = Path(directory)/'synthetic-input.txt'; path.write_text('synthetic-a')
                before = s.hash_inputs([path]); s.validate_inventory(before, s.hash_inputs([path]))
                path.write_text('synthetic-b')
                with self.assertRaisesRegex(AssertionError, 'STALE_INPUTS'):
                    s.validate_inventory(before, s.hash_inputs([path]))
                extra = Path(directory)/'added-input.txt'; extra.write_text('synthetic-added')
                with self.assertRaisesRegex(AssertionError, 'STALE_INPUTS'):
                    s.validate_inventory(before, s.hash_inputs([path, extra]))
            with self.assertRaisesRegex(AssertionError, 'EVENT_SIZE_BUDGET'):
                v.event('OVERSIZED', synthetic='x'*(s.MAX_EVENT_BYTES+1))
            prior = s.MAX_EVENTS
            try:
                s.MAX_EVENTS = len(v.events)
                with self.assertRaisesRegex(AssertionError, 'EVENT_BUDGET'):
                    v.event('OVER_COUNT')
            finally:
                s.MAX_EVENTS = prior
            v.event('EVIDENCE_NEGATIVES', operation='INVENTORY', changed_input_rejected=True, added_input_rejected=True, oversized_event_rejected=True, event_count_rejected=True, explicit_reader_checks=True)
        self.run_scenario('HC23', 'R', exercise)

    def test_HC24(self):
        def exercise(v):
            design = json.loads(Path('docs/validation/D5-I41-design-review.json').read_text())
            planned = [r['id'] for r in design['cases']]
            self.assertEqual(planned, [f'HC{i:02}' for i in range(1, 25)])
            methods = unittest.defaultTestLoader.getTestCaseNames(type(self))
            self.assertEqual(methods, ['test_'+c for c in planned])
            s.validate_report(methods, methods, [], 0)
            for passed, skipped, remaining, code in [(methods+methods[:1], [], 0, 'DUPLICATE_TEST_IDS'), (methods[:-1], [], 0, 'INCOMPLETE_CAMPAIGN'), (methods, ['skip'], 0, 'INCOMPLETE_CAMPAIGN'), (methods, [], 1, 'RESOURCES_REMAINING')]:
                with self.assertRaisesRegex(AssertionError, code):
                    s.validate_report(passed, methods, skipped, remaining)
            self.assertFalse(design['D5_closed'] or design['publication_authorized'])
            self.assertEqual(len(design['global_gaps_open']), 7)
            v.event('REPORT_NEGATIVES', operation='REPORT', planned_rows=24, duplicate_incomplete_skip_resource_rejected=True, distinct_regression_campaign=True)
        self.run_scenario('HC24', 'R', exercise)
