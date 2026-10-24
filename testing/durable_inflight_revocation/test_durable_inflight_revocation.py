# SPDX-License-Identifier: GPL-3.0-only
"""Approved I51 intercalations inside real local Remote.execute calls."""
from copy import deepcopy
import json
from pathlib import Path
import signal
import tempfile
import unittest
import uuid

from testing.durable_inflight_revocation import support as s


def static_domain(state):
    return {k:v for k,v in state.items() if k not in ('receipts','reviews','review_count','sends','pending')}


class InflightRevocationTest(unittest.TestCase):
    def scenario(self,case,path,exercise):
        v=s.Scenario(case,path);success=False
        try:exercise(v);v.passive();success=True
        finally:v.close(success)

    def call(self,v,action,label=None,expected_error=None,**kwargs):
        return v.run_job(dict(action=action,role='CLIENT',operation=action,mode=v.record.get('mode','NONE'),stage='PROJECTION',**kwargs),label or action,expected_error=expected_error)

    def setup(self,v,mode):
        v.prepare_mode(mode);v.sid=s.uid()
        self.assertEqual(static_domain(v.before['client']['state']),static_domain(s.inspect_files(v.value)['client']['state']))

    def revoke(self,v):
        before=v.observe('before_revocation');head=before['client']['head']
        command=dict(kind='REVIEW',args=dict(stage='PROJECTION',manifest_id=v.mid,expected_version=1,decision='REVOKE',reason_code='SYNTHETIC_REVIEW'),cid=s.uid(),expected={k:head[k] for k in ('seq','commit_sha256')})
        rh=s.digest({k:command[k] for k in ('kind','args','expected')})
        event=self.call(v,'mutate','revoker_process',command=command);receipt=event['value']
        self.assertFalse(receipt['historical']);self.assertEqual(receipt['result'],dict(version=2))
        self.assertEqual((receipt['command_id'],receipt['request_sha256']),(command['cid'],rh))
        self.assertTrue(all(event['transport'][k]==0 for k in ('execute_real_calls','lookup_real_calls')))
        after=v.observe('revocation_committed');state=after['client']['state']
        self.assertEqual(state['reviews']['PROJECTION:'+v.mid],dict(version=2,decision='REVOKE',reason_code='SYNTHETIC_REVIEW'))
        self.assertEqual(after['client']['head']['seq'],before['client']['head']['seq']+1)
        self.assertEqual(after['remote'],before['remote']);self.assertEqual(state['sends'],before['client']['state']['sends'])
        self.assertEqual(state['pending'],before['client']['state']['pending'])
        self.assertEqual(static_domain(state),static_domain(v.before['client']['state']))
        v.record['revocation']=dict(cid=command['cid'],request_sha256=rh,manifest_id=v.mid,version=2,receipt_sha256=s.digest(receipt))
        v.event('REVOCATION_COMMITTED',role='CLIENT',operation='REVIEW',mode=v.record['mode'],stage='PROJECTION',cid=command['cid'],request_sha256=rh,review_version=2,receipt=receipt)
        replay=self.call(v,'mutate','exact_review_replay',command=command)['value']
        self.assertEqual(replay,dict(receipt,historical=True));self.assertEqual(v.observe('review_replay_unchanged'),after)
        current={k:after['client']['head'][k] for k in ('seq','commit_sha256')}
        incompatible=dict(command,cid=s.uid(),expected=current)
        self.call(v,'mutate','old_review_version',expected_error='CONFLICT_REVIEW',command=incompatible)
        self.assertEqual(v.observe('old_review_version_rejected'),after)
        return after

    def effect(self,v,remote,ticket,identity=None):
        baseline=v.before['remote'];proof=remote['state']['tickets'][ticket]
        self.assertEqual((proof['status'],proof['code'],proof['ticket']),('EFFECT_CONFIRMED','CONFIRMED',ticket))
        self.assertEqual((proof['run_id'],proof['store_id']),(v.lab.run_id,v.lab.remote_id))
        self.assertEqual(proof['schema'],'d5.durable-remote-proof.v1' if v.path=='T' else 'd5.relational-remote-proof.v1')
        self.assertEqual((proof['manifest_hash'],proof['request_hash'],proof['creation_key'],proof['payload_hash']),(s.digest(v.manifest),s.digest(v.manifest),v.manifest['creation_key'],s.digest(v.manifest['payload'])))
        rid=str(uuid.uuid5(uuid.UUID(v.lab.remote_id),v.manifest['creation_key']))
        base=v.manifest['remote_base'];version=base['version']+1 if base else 1
        foreign=base['foreign'] if base else {}
        self.assertEqual((proof['remote_id'],proof['applied_version']),(rid,version))
        expected=deepcopy(baseline['state']['entities']);expected[rid]=dict(id=rid,version=version,payload=v.manifest['payload'],foreign=foreign)
        self.assertEqual(remote['state']['entities'],expected)
        self.assertEqual(remote['state']['keys'],dict(baseline['state']['keys'],**{v.manifest['creation_key']:rid}))
        self.assertEqual(remote['head']['seq'],baseline['head']['seq']+1)
        self.assertEqual(set(remote['state']['tickets']),set(baseline['state']['tickets'])|{ticket})
        self.assertEqual(len(remote['state']['receipts']),len(baseline['state']['receipts'])+1)
        self.assertTrue(all(remote['state']['receipts'][k]==x for k,x in baseline['state']['receipts'].items()))
        if identity:
            receipt=remote['state']['receipts'][identity['cid']]
            self.assertEqual(receipt['request_sha256'],identity['request_sha256']);self.assertEqual(receipt['result'],proof)
        return proof

    def send_state(self,v,values,ticket,status,ledger,queries):
        state=values['client']['state'];send=state['sends'][v.sid]
        self.assertEqual((send['status'],send['ledger_version'],send['queries']),(status,ledger,queries))
        self.assertEqual(send['attempts'],[ticket]);self.assertFalse(send['hard_conflict'])
        self.assertEqual({k:x for k,x in state['sends'].items() if k!=v.sid},v.before['client']['state']['sends'])
        self.assertEqual(static_domain(state),static_domain(v.before['client']['state']))
        return send

    def rejected_dispatch(self,v):
        before=v.observe('before_revoked_retry')
        event=self.call(v,'dispatch','revoked_retry',expected_error='REVIEW_REQUIRED',mid=v.mid,sid=v.sid,retry=True)
        self.assertEqual(event['transport']['execute_real_calls'],0)
        self.assertEqual(v.observe('after_revoked_retry'),before)

    def summary_stale(self,v,status):
        event=self.call(v,'summary','public_summary_after_release')
        row=next(x for x in event['value']['sends'] if x['send_id']==v.sid)
        self.assertEqual((row['status'],row['validity'],row['attempts']),(status,'STALE',1))
        self.assertTrue(all(event['transport'][k]==0 for k in ('execute_real_calls','lookup_real_calls')))

    def before_issue(self,case,path,mode):
        def exercise(v):
            v.record['family']='BEFORE_ISSUE';self.setup(v,mode);after=self.revoke(v)
            event=self.call(v,'dispatch','revoked_before_issue',expected_error='REVIEW_REQUIRED',mid=v.mid,sid=v.sid)
            self.assertEqual(event['transport']['execute_real_calls'],0)
            self.assertEqual(v.observe('no_new_attempt'),after);self.assertNotIn(v.sid,after['client']['state']['sends'])
        self.scenario(case,path,exercise)

    def inflight(self,case,path,mode,point,lose=False):
        def exercise(v):
            v.record['family']='INFLIGHT_LOST_RESPONSE' if lose else 'INFLIGHT_BEFORE_PUBLISH' if point=='before_object' else 'INFLIGHT_AFTER_COMMIT'
            self.setup(v,mode)
            job=dict(action='dispatch',case=case,role='CLIENT',operation='dispatch',mode=mode,stage='PROJECTION',mid=v.mid,sid=v.sid,point=point,gate=True,lose_response=lose)
            pair=v.spawn(job,'dispatch_actor');p,conn=pair
            try:
                ready=s.receive(conn);self.assertTrue(p.is_alive());self.assertFalse(conn.poll(0))
                gate=v.observe('gate_'+point);send=gate['client']['state']['sends'][v.sid];ticket=send['attempts'][0]
                identity=s.execute_identity(v.value,job,ticket,v.manifest);s.validate_gate(ready,identity)
                self.assertEqual((ready['transport']['execute_wrapper_calls'],ready['transport']['execute_real_calls'],ready['transport']['lookup_real_calls']),(1,1,0))
                self.assertIsNone(ready['transport']['returned_proof_sha256'])
                self.send_state(v,gate,ticket,'UNKNOWN',1,0)
                self.assertEqual(gate['client']['state']['pending'],{'send:'+ticket:dict(send_id=v.sid)})
                self.assertEqual(gate['client']['head']['seq'],v.before['client']['head']['seq']+1)
                issue_commit=gate['client']['chain'][-1]
                self.assertEqual(issue_commit['operation']['kind'],'ISSUE')
                self.assertEqual(issue_commit['operation']['args']['ticket'],ticket)
                self.assertEqual(issue_commit['receipt']['request_sha256'],issue_commit['request_sha256'])
                v.record['issued_ticket']=dict(ticket=ticket,send_id=v.sid,cid=issue_commit['command_id'],request_sha256=issue_commit['request_sha256'],origin='ISSUED_BY_CLIENT')
                if point=='before_object':self.assertEqual(gate['remote'],v.before['remote'])
                else:self.effect(v,gate['remote'],ticket,identity)
                v.record['execute_identity']=identity
                v.event('READY',**{k:x for k,x in ready.items() if k not in ('event','case','path')})
                revoked=self.revoke(v)
                self.assertTrue(p.is_alive());self.assertFalse(conn.poll(0))
                self.assertEqual(revoked['remote'],gate['remote'])
                self.send_state(v,revoked,ticket,'UNKNOWN',1,0)
                release=dict(event='RELEASE',cid=identity['cid'],ticket=ticket)
                conn.send(release)
                v.event('RELEASE_ACK',actor='parent',role='REMOTE',operation='EXECUTE',mode=mode,stage='PROJECTION',point=point,cid=identity['cid'],ticket=ticket)
                done=s.receive(conn);self.assertEqual((done['event'],done['status']),('DONE','OK'));s.finish(*pair)
                self.assertEqual(done['execute_identity'],identity)
                self.assertEqual((done['transport']['execute_wrapper_calls'],done['transport']['execute_real_calls'],done['transport']['lookup_real_calls']),(1,1,0))
                self.assertEqual(done['transport']['failure_phase'],'LOSS_AFTER_REAL_COMMIT' if lose else None)
                self.assertEqual(done['value']['ticket'],ticket)
                v.event('DISPATCH_DONE',actor='dispatch_actor',role='CLIENT',operation='dispatch',mode=mode,stage='PROJECTION',point='after_result',result=done['value'],transport=done['transport'])
            finally:s.stop_owned([pair])
            values=v.observe('dispatch_complete');proof=self.effect(v,values['remote'],ticket,identity)
            self.assertEqual(done['transport']['returned_proof_sha256'],s.digest(proof))
            send=self.send_state(v,values,ticket,'UNKNOWN' if lose else 'EFFECT_CONFIRMED',2,0)
            self.assertEqual(send['proof'],None if lose else proof);self.assertFalse(values['client']['state']['pending'])
            self.summary_stale(v,'UNKNOWN' if lose else 'EFFECT_CONFIRMED');v.passive();self.rejected_dispatch(v)
            if lose:
                before=v.observe('before_explicit_reconcile')
                event=self.call(v,'reconcile','explicit_reconcile',sid=v.sid)
                self.assertEqual((event['transport']['lookup_real_calls'],event['transport']['execute_real_calls']),(1,0))
                after=v.observe('after_explicit_reconcile');self.assertEqual(after['remote'],before['remote'])
                send=self.send_state(v,after,ticket,'EFFECT_CONFIRMED',3,1);self.assertEqual(send['proof'],proof)
                self.assertFalse(after['client']['state']['pending']);self.summary_stale(v,'EFFECT_CONFIRMED');self.rejected_dispatch(v)
        self.scenario(case,path,exercise)

    def protocol(self,v):
        job=dict(case=v.case,mode='CREATE',point='before_object',mid='0'*64,sid=s.uid())
        manifest=dict(synthetic=True)
        expected=s.execute_identity(v.value,job,s.uid(),manifest)
        good=dict(event='READY',**expected,execute_in_progress=True)
        s.validate_gate(good,expected)
        for key in expected:
            bad=dict(good);bad[key]='synthetic-wrong'
            with self.assertRaisesRegex(AssertionError,'GATE_IDENTITY'):s.validate_gate(bad,expected)
        with self.assertRaisesRegex(AssertionError,'NOT_IN_REAL_EXECUTE'):s.validate_gate(dict(good,execute_in_progress=False),expected)
        for target,name in [(s.held_child,'TIMEOUT'),(s.normal_child,'NORMAL_EXIT'),(s.empty_child,'EOF')]:
            pair=s.start(target,(),dict(case=v.case,path=v.path,actor=name,action='negative_control'));v.children.append(pair)
            try:
                if name=='TIMEOUT':
                    self.assertEqual(s.receive(pair[1])['event'],'READY')
                    with self.assertRaisesRegex(AssertionError,'CONTROL_TIMEOUT'):s.receive(pair[1],timeout=0.02)
                elif name=='NORMAL_EXIT':
                    with self.assertRaisesRegex(AssertionError,'MISSING_READY'):s.validate_gate(s.receive(pair[1]),expected)
                    s.finish(*pair);self.assertEqual(pair[0].exitcode,0)
                else:
                    with self.assertRaisesRegex(AssertionError,'CONTROL_EOF'):s.receive(pair[1])
                    s.finish(*pair)
            finally:s.stop_owned([pair])
            v.event('NEGATIVE_PROTOCOL',point=name,reduced_timeout_seconds=0.02 if name=='TIMEOUT' else None,exitcode=pair[0].exitcode,counts_as_inflight=False,counts_as_recovery=False)

    def ownership(self,case,path):
        def exercise(v):
            self.protocol(v);v.passive()
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
            with tempfile.TemporaryDirectory(prefix='d5-i52-inventory-') as directory:
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
            design=json.loads(Path('docs/validation/D5-I51-design-review.json').read_text())
            methods=unittest.defaultTestLoader.getTestCaseNames(type(self));expected=['test_'+r['id'] for r in design['rows']]
            self.assertEqual(methods,expected);s.validate_report(methods,expected,[],0)
            for passed,skipped,left,code in [(methods+methods[:1],[],0,'DUPLICATE_TEST_IDS'),(methods[:-1],[],0,'INCOMPLETE_CAMPAIGN'),(methods,['skip'],0,'INCOMPLETE_CAMPAIGN'),(methods,[],1,'RESOURCES_REMAINING')]:
                with self.assertRaisesRegex(AssertionError,code):s.validate_report(passed,expected,skipped,left)
            self.assertFalse(design['D5_closed'])
            self.assertEqual(len(design['rows']),20)
            v.event('EVIDENCE_NEGATIVES',inputs_raw_counts_budgets_rejected=True,no_global_closure=True)
        self.scenario(case,path,exercise)

    def test_RV01(self):self.before_issue('RV01','T','CREATE')
    def test_RV02(self):self.before_issue('RV02','T','UPDATE')
    def test_RV03(self):self.before_issue('RV03','R','CREATE')
    def test_RV04(self):self.before_issue('RV04','R','UPDATE')
    def test_RV05(self):self.inflight('RV05','T','CREATE','before_object')
    def test_RV06(self):self.inflight('RV06','T','UPDATE','before_object')
    def test_RV07(self):self.inflight('RV07','R','CREATE','before_object')
    def test_RV08(self):self.inflight('RV08','R','UPDATE','before_object')
    def test_RV09(self):self.inflight('RV09','T','CREATE','after_head')
    def test_RV10(self):self.inflight('RV10','T','UPDATE','after_head')
    def test_RV11(self):self.inflight('RV11','R','CREATE','after_head')
    def test_RV12(self):self.inflight('RV12','R','UPDATE','after_head')
    def test_RV13(self):self.inflight('RV13','T','CREATE','after_head',True)
    def test_RV14(self):self.inflight('RV14','T','UPDATE','after_head',True)
    def test_RV15(self):self.inflight('RV15','R','CREATE','after_head',True)
    def test_RV16(self):self.inflight('RV16','R','UPDATE','after_head',True)
    def test_RV17(self):self.ownership('RV17','T')
    def test_RV18(self):self.ownership('RV18','R')
    def test_RV19(self):self.inventory('RV19','T')
    def test_RV20(self):self.inventory('RV20','R')
