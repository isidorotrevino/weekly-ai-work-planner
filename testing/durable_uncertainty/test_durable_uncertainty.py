# SPDX-License-Identifier: GPL-3.0-only
"""I49 UQ obligations: existing APIs, explicit transport-loss boundaries."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
import uuid

from testing.durable_uncertainty import support as s


def domain(state):
    return {k:v for k,v in state.items() if k not in ('receipts','sends','pending','tick')}


class UncertaintyTest(unittest.TestCase):
    def scenario(self,case,path,exercise,variant='primary'):
        v=s.Scenario(case,path);v.record['variant']=variant;success=False
        try:
            exercise(v);v.passive();success=True
        finally:v.close(success)

    def call(self,v,action,label=None,expected_error=None,**kwargs):
        return v.run_job(dict(action=action,role='CLIENT',operation=action,mode='CREATE',stage='PROJECTION',**kwargs),label or action,expected_error=expected_error)

    def setup(self,v):
        v.prepare();v.sid=s.uid()

    def issue(self,v):
        job=v.issue_job(s.uid(),v.sid,s.uid());out=v.run_job(job,'issue')['value']
        self.assertFalse(out['historical']);v.ticket=out['result']['ticket']
        v.record['issued_ticket']=dict(ticket=v.ticket,send_id=v.sid,cid=job['cid'],request_sha256=job['request_hash'],origin='ISSUED_BY_CLIENT')
        self.assert_unknown(v,1,0,True)

    def assert_unknown(self,v,ledger,queries,pending):
        values=v.observe('unknown_'+str(ledger)+'_'+str(queries));state=values['client']['state'];send=state['sends'][v.sid]
        self.assertEqual(set(state['sends']),{v.sid});self.assertEqual(send['attempts'],[v.ticket])
        self.assertEqual((send['status'],send['ledger_version'],send['queries'],send['proof']),('UNKNOWN',ledger,queries,None))
        self.assertFalse(send['hard_conflict'])
        self.assertEqual(state['pending'],{'send:'+v.ticket:dict(send_id=v.sid)} if pending else {})
        self.assertEqual(domain(state),domain(v.before['client']['state']))
        return values

    def effect(self,v,remote,ticket):
        proof=remote['state']['tickets'][ticket]
        self.assertEqual((proof['status'],proof['code'],proof['ticket']),('EFFECT_CONFIRMED','CONFIRMED',ticket))
        self.assertEqual((proof['request_hash'],proof['manifest_hash'],proof['creation_key']),(s.digest(v.manifest),s.digest(v.manifest),v.manifest['creation_key']))
        self.assertEqual((proof['run_id'],proof['store_id']),(v.lab.run_id,v.lab.remote_id))
        self.assertEqual(proof['schema'],'d5.durable-remote-proof.v1' if v.path=='T' else 'd5.relational-remote-proof.v1')
        rid=str(uuid.uuid5(uuid.UUID(v.lab.remote_id),v.manifest['creation_key']))
        self.assertEqual((proof['remote_id'],proof['applied_version'],proof['payload_hash']),(rid,1,s.digest(v.manifest['payload'])))
        self.assertEqual(remote['state']['entities'],{rid:dict(id=rid,version=1,payload=v.manifest['payload'],foreign={})})
        self.assertEqual(remote['state']['keys'],{v.manifest['creation_key']:rid})
        return proof

    def rejected_retry(self,v,code):
        before=v.observe('before_rejected_retry')
        self.call(v,'dispatch',expected_error=code,mid=v.mid,sid=v.sid,retry=True)
        self.assertEqual(v.observe('after_rejected_retry'),before)

    def reconcile_effect(self,v,ledger,queries):
        before=v.observe('before_explicit_reconcile');proof=self.effect(v,before['remote'],v.ticket)
        event=self.call(v,'reconcile','explicit_reconcile',sid=v.sid)
        self.assertEqual((event['transport']['lookup_real_calls'],event['transport']['execute_real_calls']),(1,0))
        after=v.observe('after_explicit_reconcile');send=after['client']['state']['sends'][v.sid]
        self.assertEqual((send['status'],send['ledger_version'],send['queries']),('EFFECT_CONFIRMED',ledger,queries))
        self.assertEqual(send['attempts'],[v.ticket]);self.assertEqual(send['proof'],proof)
        self.assertFalse(after['client']['state']['pending']);self.assertEqual(after['remote'],before['remote'])
        self.assertEqual(domain(after['client']['state']),domain(v.before['client']['state']))

    def empty(self,case,path,fault=False):
        def exercise(v):
            self.setup(v);self.issue(v);before=v.observe('before_empty_lookup')
            event=self.call(v,'reconcile',sid=v.sid,**(dict(fault='lookup_before') if fault else {}))
            self.assertEqual((event['transport']['lookup_wrapper_calls'],event['transport']['lookup_real_calls'],event['transport']['execute_real_calls']),(1,int(not fault),0))
            self.assertEqual(event['transport']['failure_phase'],'LOSS_BEFORE_REAL_CALL' if fault else None)
            after=self.assert_unknown(v,2,1,True);self.assertEqual(after['remote'],before['remote'])
            self.assertFalse(after['remote']['state']['entities'] or after['remote']['state']['tickets'])
            v.passive();self.rejected_retry(v,'BINDING_UNRESOLVED')
        self.scenario(case,path,exercise)

    def dispatch_loss(self,case,path,after_effect):
        def exercise(v):
            self.setup(v)
            event=self.call(v,'dispatch',mid=v.mid,sid=v.sid,fault='execute_after' if after_effect else 'execute_before')
            v.ticket=event['value']['ticket'];v.record['issued_ticket']=dict(ticket=v.ticket,send_id=v.sid,origin='ISSUED_BY_CLIENT')
            self.assertEqual((event['transport']['execute_wrapper_calls'],event['transport']['execute_real_calls'],event['transport']['lookup_real_calls']),(1,int(after_effect),0))
            self.assertEqual(event['transport']['failure_phase'],'LOSS_AFTER_REAL_COMMIT' if after_effect else 'LOSS_BEFORE_REAL_CALL')
            values=self.assert_unknown(v,2,0,False)
            if after_effect:
                p=self.effect(v,values['remote'],v.ticket)
                self.assertEqual(event['transport']['returned_proof_sha256'],s.digest(p))
            else:self.assertEqual(values['remote'],v.before['remote'])
            v.passive();self.rejected_retry(v,'BINDING_UNRESOLVED')
            if after_effect:self.reconcile_effect(v,3,1)
        self.scenario(case,path,exercise)

    def hidden_lookup(self,case,path):
        def exercise(v):
            self.setup(v);self.issue(v)
            event=v.run_job(v.execute_job(v.ticket),'execute_issued_ticket')
            self.assertEqual(event['transport']['execute_real_calls'],1)
            before=v.observe('remote_proof_not_yet_observed');self.effect(v,before['remote'],v.ticket)
            event=self.call(v,'reconcile',sid=v.sid,fault='lookup_before')
            self.assertEqual((event['transport']['lookup_wrapper_calls'],event['transport']['lookup_real_calls']),(1,0))
            self.assertIsNone(event['transport']['returned_proof_sha256'])
            values=self.assert_unknown(v,2,1,True);self.assertEqual(values['remote'],before['remote'])
            v.passive();self.rejected_retry(v,'BINDING_UNRESOLVED');self.reconcile_effect(v,3,2)
        self.scenario(case,path,exercise)

    def malformed(self,case,path,kind):
        def exercise(v):
            self.setup(v);self.issue(v);v.run_job(v.execute_job(v.ticket),'execute_issued_ticket')
            before=v.observe('before_malformed');proof=self.effect(v,before['remote'],v.ticket)
            event=self.call(v,'reconcile',sid=v.sid,invalid=kind,wrong_ticket=s.uid())
            self.assertEqual((event['transport']['lookup_real_calls'],event['transport']['execute_real_calls']),(1,0))
            self.assertEqual(event['transport']['proof_input_type'],'list' if kind=='list' else 'dict')
            self.assertEqual(event['transport']['proof_input_cardinality'],2 if kind in ('list','envelope') else None)
            for ledger,queries in [(2,1),(3,2)]:
                if ledger==3:self.call(v,'reconcile','correct_proof_after_conflict',sid=v.sid)
                values=v.observe('sticky_conflict_'+str(ledger));send=values['client']['state']['sends'][v.sid]
                self.assertEqual((send['status'],send['ledger_version'],send['queries'],send['proof']),('CONFLICT',ledger,queries,None))
                self.assertTrue(send['hard_conflict']);self.assertEqual(send['attempts'],[v.ticket])
                self.assertFalse(values['client']['state']['pending']);self.assertEqual(values['remote'],before['remote'])
                self.assertEqual(domain(values['client']['state']),domain(v.before['client']['state']))
                if ledger==3:self.assertEqual(send['events'][-1]['proof'],proof)
                v.passive();self.rejected_retry(v,'BINDING_UNRESOLVED')
            v.record['invalid_input_classification']='MALFORMED_PROOF_NOT_NATIVE_MULTIPLE_MATCHES'
        self.scenario(case,path,exercise)

    def rate_limit(self,case,path,delay):
        def exercise(v):
            self.setup(v)
            event=self.call(v,'dispatch',mid=v.mid,sid=v.sid,reject='RATE_LIMIT',retry_tick=delay)
            v.ticket=event['value']['ticket'];values=v.observe('rate_limit_no_effect');send=values['client']['state']['sends'][v.sid];proof=send['proof']
            self.assertEqual((send['status'],send['ledger_version'],send['queries']),('NO_EFFECT',2,0))
            self.assertEqual(proof['code'],'RATE_LIMIT');self.assertEqual(proof['retry_tick'],delay)
            self.assertEqual((proof['ticket'],proof['manifest_hash'],proof['request_hash'],proof['creation_key']),(v.ticket,s.digest(v.manifest),s.digest(v.manifest),v.manifest['creation_key']))
            self.assertEqual((proof['run_id'],proof['store_id']),(v.lab.run_id,v.lab.remote_id))
            self.assertTrue(all(proof[k] is None for k in ('remote_id','payload_hash','applied_version')))
            self.assertEqual(values['remote']['state']['tickets'],{v.ticket:proof});self.assertFalse(values['remote']['state']['entities'] or values['client']['state']['pending'])
            self.rejected_retry(v,'RETRY_NOT_ELIGIBLE');v.passive()
            self.call(v,'clock',tick=5)
            if delay is None:self.rejected_retry(v,'RETRY_NOT_ELIGIBLE')
            else:
                event=self.call(v,'dispatch','explicit_eligible_retry',mid=v.mid,sid=v.sid,retry=True)
                ticket=event['value']['ticket'];self.assertNotEqual(ticket,v.ticket)
                after=v.observe('explicit_retry_effect');self.effect(v,after['remote'],ticket)
                send=after['client']['state']['sends'][v.sid]
                self.assertEqual(send['attempts'],[v.ticket,ticket]);self.assertEqual((send['status'],send['ledger_version'],send['queries']),('EFFECT_CONFIRMED',4,0))
                self.assertEqual(send['proof'],after['remote']['state']['tickets'][ticket]);self.assertFalse(after['client']['state']['pending'])
                self.assertEqual(len(after['remote']['state']['tickets']),2)
            self.assertEqual(domain(v.observe('rate_limit_final')['client']['state']),domain(v.before['client']['state']))
        self.scenario(case,path,exercise)
        if delay is not None:
            def contrast(v):
                self.setup(v);self.issue(v);self.call(v,'clock',tick=5)
                self.assert_unknown(v,1,0,True);self.rejected_retry(v,'BINDING_UNRESOLVED')
            self.scenario(case,path,contrast,'unknown_clock_contrast')

    def ownership(self,case,path):
        def exercise(v):
            v.passive()
            saved=v.lab.home/'own_saved_run';v.lab.root.rename(saved);v.lab.root.mkdir()
            try:s.expect_error('CLEANUP_OWNERSHIP',v.lab.close)
            finally:v.lab.root.rmdir();saved.rename(v.lab.root)
            owner=v.lab.root/'owner.json';raw=owner.read_bytes();owner.write_bytes(b'{}')
            try:s.expect_error('CLEANUP_MARKER',v.lab.close)
            finally:owner.write_bytes(raw)
            sentinel=v.lab.sentinel.read_bytes();v.lab.sentinel.write_bytes(b'SYNTHETIC_ALTERED')
            try:s.expect_error('SENTINEL_CHANGED',v.lab.close)
            finally:v.lab.sentinel.write_bytes(sentinel)
            link=v.lab.root/'client'/'own_negative_link';link.symlink_to(v.lab.sentinel)
            try:s.expect_error('CLEANUP_SYMLINK',v.lab.close)
            finally:link.unlink()
            self.assertEqual(v.lab.sentinel.read_bytes(),sentinel)
            v.event('OWNERSHIP_NEGATIVES',inode_marker_sentinel_link_rejected=True,restored_before_cleanup=True)
        self.scenario(case,path,exercise)

    def inventory(self,case,path):
        def exercise(v):
            with tempfile.TemporaryDirectory(prefix='d5-i50-inventory-') as directory:
                s.EXTRA_ROOTS.append(directory);p=Path(directory)/'synthetic-input';p.write_text('synthetic-a')
                before=s.hash_inputs([p]);s.validate_inventory(before,s.hash_inputs([p]));p.write_text('synthetic-b')
                with self.assertRaisesRegex(AssertionError,'STALE_INPUTS'):s.validate_inventory(before,s.hash_inputs([p]))
                q=Path(directory)/'added-input';q.write_text('synthetic-added')
                with self.assertRaisesRegex(AssertionError,'STALE_INPUTS'):s.validate_inventory(before,s.hash_inputs([p,q]))
                raw=Path(directory)/'synthetic-raw.json'
                with self.assertRaisesRegex(AssertionError,'RAW_MISSING_OR_TYPE'):s.raw_binding(raw)
                raw.write_text('{')
                with self.assertRaisesRegex(AssertionError,'RAW_INCOMPATIBLE'):s.raw_binding(raw)
                raw.write_text(json.dumps(dict(status='PASS',tests_run=1,passed=['synthetic.test'])))
                self.assertEqual(s.raw_binding(raw)['tests_run'],1)
                with self.assertRaisesRegex(AssertionError,'RAW_HASH_MISMATCH'):s.raw_binding(raw,'0'*64)
                with self.assertRaisesRegex(AssertionError,'RAW_BUDGET'):s.raw_binding(raw,maximum=1)
                raw.write_text(json.dumps(dict(status='PASS',tests_run=2,passed=['synthetic.test']*2)))
                with self.assertRaisesRegex(AssertionError,'RAW_COUNTS'):s.raw_binding(raw)
            with self.assertRaisesRegex(AssertionError,'RAW_BUDGET'):s.bounded_raw(dict(synthetic='x'*128),maximum=64)
            with self.assertRaisesRegex(AssertionError,'EVENT_SIZE_BUDGET'):v.event('OVERSIZE',synthetic='x'*(s.MAX_EVENT_BYTES+1))
            limit=s.MAX_EVENTS
            try:
                s.MAX_EVENTS=len(v.events)
                with self.assertRaisesRegex(AssertionError,'EVENT_BUDGET'):v.event('OVERCOUNT')
            finally:s.MAX_EVENTS=limit
            design=json.loads(Path('docs/validation/D5-I49-design-review.json').read_text())
            methods=unittest.defaultTestLoader.getTestCaseNames(type(self));expected=['test_'+r['id'] for r in design['rows']]
            self.assertEqual(methods,expected);s.validate_report(methods,expected,[],0)
            for passed,skipped,left,code in [(methods+methods[:1],[],0,'DUPLICATE_TEST_IDS'),(methods[:-1],[],0,'INCOMPLETE_CAMPAIGN'),(methods,['skip'],0,'INCOMPLETE_CAMPAIGN'),(methods,[],1,'RESOURCES_REMAINING')]:
                with self.assertRaisesRegex(AssertionError,code):s.validate_report(passed,expected,skipped,left)
            self.assertFalse(design['H07_closed'] or design['D5_closed'] or design['publication_authorized'])
            self.assertEqual(len(design['model_gaps']),3)
            v.event('EVIDENCE_NEGATIVES',inputs_raw_counts_budgets_rejected=True,model_gaps_not_tests=True)
        self.scenario(case,path,exercise)

    def test_UQ01(self):self.empty('UQ01','T')
    def test_UQ02(self):self.empty('UQ02','R')
    def test_UQ03(self):self.empty('UQ03','T',True)
    def test_UQ04(self):self.empty('UQ04','R',True)
    def test_UQ05(self):self.dispatch_loss('UQ05','T',False)
    def test_UQ06(self):self.dispatch_loss('UQ06','R',False)
    def test_UQ07(self):self.dispatch_loss('UQ07','T',True)
    def test_UQ08(self):self.dispatch_loss('UQ08','R',True)
    def test_UQ09(self):self.hidden_lookup('UQ09','T')
    def test_UQ10(self):self.hidden_lookup('UQ10','R')
    def test_UQ11(self):self.malformed('UQ11','T','list')
    def test_UQ12(self):self.malformed('UQ12','R','list')
    def test_UQ13(self):self.malformed('UQ13','T','envelope')
    def test_UQ14(self):self.malformed('UQ14','R','envelope')
    def test_UQ15(self):self.malformed('UQ15','T','ticket')
    def test_UQ16(self):self.malformed('UQ16','R','ticket')
    def test_UQ17(self):self.rate_limit('UQ17','T',5)
    def test_UQ18(self):self.rate_limit('UQ18','R',5)
    def test_UQ19(self):self.rate_limit('UQ19','T',None)
    def test_UQ20(self):self.rate_limit('UQ20','R',None)
    def test_UQ21(self):self.ownership('UQ21','T')
    def test_UQ22(self):self.ownership('UQ22','R')
    def test_UQ23(self):self.inventory('UQ23','T')
    def test_UQ24(self):self.inventory('UQ24','R')
