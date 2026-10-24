# SPDX-License-Identifier: GPL-3.0-only
"""I58 FN64: first publications and QUERY-associated RESULT, not parent PASS inference."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from testing.durable_frontier_gaps import support as s


class FrontierGapsTest(unittest.TestCase):
    def invariant_state(self,before,after,changed):
        self.assertEqual({k:v for k,v in before.items() if k not in changed},{k:v for k,v in after.items() if k not in changed})
    def initial(self,v):
        b=v.before['client']['state'];op=v.row['operation']
        self.assertNotIn(v.cmd['cid'],b['receipts'])
        if op=='IMPORT':
            self.assertEqual(b['sources'],{});self.assertIsNone(b['selected_source']);self.assertEqual(b['reviews'],{})
            self.assertEqual(v.record['capture']['grade'],'SYNTHETIC_OBSERVATION')
            cap=v.cmd['args']['capture'];self.assertEqual(base64.b64decode(cap['content_base64']),s.T.DATA)
            self.assertEqual(cap['content_sha256'],hashlib.sha256(s.T.DATA).hexdigest())
        elif op.startswith('REVIEW_'):
            a=v.cmd['args'];self.assertEqual((a['decision'],a['expected_version']),('ACCEPT',0));self.assertNotIn(a['stage']+':'+a['manifest_id'],b['reviews'])
            if a['stage']=='SOURCE':self.assertTrue(b['sources'])
            else:self.assertEqual(b['manifests'][a['manifest_id']]['stage'],a['stage'])
        elif op.startswith('PREPARE_'):
            self.assertFalse(any(m['stage']==v.row['stage'] for m in b['manifests'].values()))
            if op=='PREPARE_EFFECT':self.assertEqual(b['tasks'],{})
        elif op=='BIND':self.assertEqual(b['bindings'],{})
        elif op=='SELECT_TASKS':
            self.assertIsNone(b['selection']);self.assertEqual(b['selection_generation'],0)
        if op!='RESULT_QUERY':
            self.assertEqual(b['sends'],{});self.assertEqual(v.before['remote']['state']['entities'],{});self.assertEqual(v.before['remote']['state']['tickets'],{})
        if v.path=='T' and op!='IMPORT':
            src=b['sources'][v.ids['source']];self.assertEqual(src['pin'],v.record['capture']['pin']);self.assertFalse(src['blocked'])
        if v.path=='R':
            a=v.record['batch'];r=b['receipts'][a['command_id']]
            self.assertEqual(r['request_sha256'],a['request_sha256']);self.assertIn(a['task_id'],r['result']['participants'])
            self.assertEqual(b['data']['entities'][a['task_id']]['kind'],'TASK')
    def published(self,v,values):
        b=v.before['client']['state'];a=values['client']['state'];cmd=v.cmd;kind=cmd['kind'];op=v.row['operation'];r=a['receipts'][cmd['cid']]
        self.assertEqual(len(a['receipts']),len(b['receipts'])+1);self.assertEqual(r['request_sha256'],v.read['request_hash'])
        self.assertEqual(values['client']['head']['seq'],v.before['client']['head']['seq']+1)
        self.assertEqual(values['remote'],v.before['remote'])
        if kind=='IMPORT':
            self.assertEqual(len(a['sources']),1);sid=r['result']['source_id'];self.assertEqual(a['selected_source'],sid);self.assertEqual(a['sources'][sid]['pin'],cmd['args']['pin'])
            self.assertEqual(a['sources'][sid]['capture'],cmd['args']['capture']);self.assertEqual(a['selection_generation'],b['selection_generation']+1)
            self.assertEqual(a['sources'][sid]['profile_hash'],b['profile']);self.assertFalse(a['sources'][sid]['blocked']);self.assertFalse(a['reviews'])
            changed={'sources','selected_source','selection_generation','receipts'}
        elif kind=='REVIEW':
            x=cmd['args'];key=x['stage']+':'+x['manifest_id'];self.assertEqual(a['reviews'][key],dict(version=1,decision='ACCEPT',reason_code='SYNTHETIC_REVIEW'))
            self.assertEqual(a['review_count'],b['review_count']+1);self.assertEqual(len(a['reviews']),len(b['reviews'])+1);changed={'reviews','review_count','receipts'}
        elif kind.startswith('PREPARE_'):
            mid=r['result']['manifest_id'];m=a['manifests'][mid];self.assertNotIn(mid,b['manifests']);self.assertEqual(s.digest(m),mid)
            self.assertEqual(m['stage'],v.row['stage']);self.assertEqual(len(a['manifests']),len(b['manifests'])+1)
            if kind=='PREPARE_EVALUATION':
                self.assertEqual(m['pins']['source_id'],v.ids['source']);self.assertEqual(m['pins']['source_review'],1);self.assertEqual(m['account_id'],v.ids['account'])
            elif kind=='PREPARE_EFFECT':
                self.assertIsNone(m['before']);self.assertEqual(m['target_id'],s.T.uid(30));self.assertEqual(m['after']['title'],'Synthetic item');self.assertEqual(m['after']['row_version'],0)
                self.assertEqual(a['tasks'],{});self.assertEqual(m['evaluation'],v.ids['evaluation'])
            else:
                self.assertEqual(m['operation'],'CREATE');self.assertIsNone(m['remote_base']);self.assertEqual(m['remote_identity'],dict(run_id=v.lab.run_id,store_id=v.lab.remote_id))
                self.assertEqual(m['target_id'],v.tid);self.assertEqual(m['payload'],dict(name=m['task']['title'],description=m['task']['description']))
                if v.path=='R':self.assertEqual((m['batch_command'],m['batch_request']),(v.record['batch']['command_id'],v.record['batch']['request_sha256']))
            changed={'manifests','receipts'}
        elif kind=='BIND':
            self.assertEqual(a['bindings'],{v.bid:cmd['args']});changed={'bindings','receipts'}
            if v.path=='T':self.assertEqual(a['data_generation'],b['data_generation']+1);changed.add('data_generation')
        elif kind=='SELECT_TASKS':
            self.assertEqual(a['selection'],dict(**cmd['args'],data_generation=b['data_generation'],data_hash=s.digest(b['data'])))
            self.assertEqual(a['selection_generation'],1);self.assertFalse(a['bindings']);changed={'selection','selection_generation','receipts'}
        else:raise AssertionError('UNEXPECTED_FIRST_PUBLICATION')
        self.invariant_state(b,a,changed)
        self.assertEqual(a['sends'],{})
    def result_state(self,v,values,published,queries=1):
        a=values['client']['state'];send=a['sends'][v.sid]
        self.assertEqual((send['status'],send['ledger_version'],send['queries']),('EFFECT_CONFIRMED' if published else 'UNKNOWN',2 if published else 1,queries))
        self.assertEqual(send['attempts'],[v.ticket]);self.assertEqual(send['proof'],v.proof if published else None)
        self.assertEqual(len(send['events']),2 if published else 1)
        self.assertEqual(len(a['pending']),0 if published else 2)
        if not published:self.assertEqual(set(a['pending']),{'send:'+v.ticket,v.qid})
        self.assertEqual(values['remote'],v.before['remote'])
        remote=values['remote']['state'];self.assertEqual(len(remote['entities']),1);self.assertEqual(len(remote['tickets']),1)
        self.assertEqual(remote['tickets'][v.ticket],v.proof);entity=remote['entities'][v.proof['remote_id']]
        self.assertEqual((entity['version'],v.proof['applied_version']),(1,1));self.assertEqual(s.digest(entity['payload']),v.proof['payload_hash']);self.assertEqual(entity['foreign'],{})
        self.invariant_state(v.before['client']['state'],a,{'sends','pending','receipts'})
    def frontier(self,case):
        row=next(r for r in s.plan()['proposed_tests'] if r['id']==case)
        with s.Scenario(row) as v:
            v.prepare();self.initial(v);is_result=row['operation']=='RESULT_QUERY';yes=row['expected_published']
            if is_result:self.result_state(v,v.before,False)
            values=v.crash()
            self.assertEqual(values['remote'],v.before['remote'])
            if yes:
                if is_result:self.result_state(v,values,True)
                else:self.published(v,values)
            else:
                self.assertEqual(values['client'],v.before['client']);self.assertNotIn(v.cmd['cid'],values['client']['state']['receipts'])
            opened=v.passive();read=opened['reads'][0]
            if yes:
                self.assertTrue(read['historical']);self.assertEqual(read['request_sha256'],v.read['request_hash'])
            else:self.assertEqual(read['result'],'NOT_COMMITTED_AT_HEAD')
            if is_result and not yes:
                out=v.run(dict(action='reconcile',sid=v.sid));self.assertEqual(out['transport']['execute'],0);self.assertEqual(out['transport']['lookup'],1)
                final=v.observe('explicit_query_recovery');self.result_state(v,final,True,2)
                self.assertNotIn(v.cmd['cid'],final['client']['state']['receipts'])
                v.record['continuation_receipt']=dict(command_id=out['value']['command_id'],request_sha256=out['value']['request_sha256'])
            else:
                out=v.run(v.job('replay'));self.assertEqual(out['transport']['execute'],0)
                self.assertEqual(out['value']['historical'],yes)
                final=v.observe('explicit_replay')
                if yes:self.assertEqual(final,values)
                elif is_result:raise AssertionError('WRONG_RESULT_CONTINUATION')
                else:self.published(v,final)
                # A committed receipt stays historical after a newer CLOCK, without rewinding HEAD or business state.
                v.run(dict(action='clock',tick=1));later=v.observe('later_clock')
                repeated=v.run(v.job('replay'));self.assertTrue(repeated['value']['historical']);self.assertEqual(v.observe('historical_replay_no_rewind'),later)
            v.passive();v.record['first_publication_or_query_branch_verified']=True
    def protocol(self,case):
        row=next(r for r in s.plan()['proposed_tests'] if r['id']==case)
        with s.Scenario(row) as v:
            v.passive();saved=v.lab.home/'own_saved';v.lab.root.rename(saved);v.lab.root.mkdir()
            try:s.expect_error('CLEANUP_OWNERSHIP',v.lab.close)
            finally:v.lab.root.rmdir();saved.rename(v.lab.root)
            p=v.lab.root/'owner.json';old=p.read_bytes();p.write_bytes(b'{}')
            try:s.expect_error('CLEANUP_MARKER',v.lab.close)
            finally:p.write_bytes(old)
            old=v.lab.sentinel.read_bytes();v.lab.sentinel.write_bytes(b'ALTERED')
            try:s.expect_error('SENTINEL_CHANGED',v.lab.close)
            finally:v.lab.sentinel.write_bytes(old)
            p=v.lab.root/'client'/'own_link';p.symlink_to(v.lab.sentinel)
            try:s.expect_error('CLEANUP_SYMLINK',v.lab.close)
            finally:p.unlink()
            expected=dict(role='CLIENT',run_id=v.lab.run_id,client_store_id=v.lab.client_id,remote_store_id=v.lab.remote_id,operation='RESULT',logical_operation='RESULT_QUERY',stage='PROJECTION',mode='CREATE',point='after_head',cid=s.uid(),args_sha256='0'*64,request_sha256='1'*64,expected={'seq':0,'commit_sha256':'2'*64},manifest_id='3'*64,send_id=s.uid(),ticket=s.uid(),query_id=s.uid())
            job=dict(case=case);event=dict(event='READY',case=case,path=v.path,**expected);s.validate_gate(event,job,v.value,expected)
            for key in expected:
                with self.assertRaisesRegex(AssertionError,'GATE_'):s.validate_gate(dict(event,**{key:'WRONG'}),job,v.value,expected)
            for key in ('case','path'):
                with self.assertRaisesRegex(AssertionError,'GATE_CASE_PATH'):s.validate_gate(dict(event,**{key:'WRONG'}),job,v.value,expected)
            with self.assertRaisesRegex(AssertionError,'MISSING_READY'):s.validate_gate(dict(event='DONE'),job,v.value,expected)
            for target,code in ((s.H.normal_child,'MISSING_READY'),(s.H.empty_child,'CONTROL_EOF'),(s.H.held_child,'CONTROL_TIMEOUT')):
                pair=s.start(target,(),dict(case=case,path=v.path,action='protocol_negative'));v.children.append(pair)
                try:
                    if target is s.H.held_child:
                        self.assertEqual(s.receive(pair[1])['event'],'READY')
                        with self.assertRaisesRegex(AssertionError,code):s.receive(pair[1],0.02)
                    elif target is s.H.empty_child:
                        with self.assertRaisesRegex(AssertionError,code):s.receive(pair[1])
                    else:
                        with self.assertRaisesRegex(AssertionError,code):s.validate_gate(s.receive(pair[1]),job,v.value,expected)
                    if target is not s.H.held_child:s.finish(*pair);self.assertEqual(pair[0].exitcode,0)
                    v.event('PROTOCOL_NEGATIVE',code=code,normal_exit_checked=target is not s.H.held_child)
                finally:s.stop_owned([pair])
            v.event('OWNERSHIP_NEGATIVES',restored_before_cleanup=True,timeout_is_not_positive_crash=True)
    def inventory(self,case):
        row=next(r for r in s.plan()['proposed_tests'] if r['id']==case)
        with s.Scenario(row) as v:
            with tempfile.TemporaryDirectory(prefix='d5-i58-inventory-') as directory:
                s.EXTRA_ROOTS.append(directory);p=Path(directory)/'input';p.write_text('a');a=s.hash_inputs([p]);p.write_text('b')
                with self.assertRaisesRegex(AssertionError,'STALE_INPUTS'):s.validate_inventory(a,s.hash_inputs([p]))
                other=Path(directory)/'added';other.write_text('x')
                with self.assertRaisesRegex(AssertionError,'STALE_INPUTS'):s.validate_inventory(s.hash_inputs([p]),s.hash_inputs([p,other]))
                raw=Path(directory)/'raw'
                with self.assertRaisesRegex(AssertionError,'RAW_MISSING_OR_TYPE'):s.raw_binding(raw)
                for bad in ('{','{"status":"PASS","status":"FAIL"}','{"x":NaN}'):
                    raw.write_text(bad)
                    with self.assertRaisesRegex(AssertionError,'RAW_INCOMPATIBLE'):s.raw_binding(raw)
                raw.write_text(json.dumps(dict(status='PASS',tests_run=1,passed=['synthetic.test'])))
                self.assertEqual(s.raw_binding(raw)['tests_run'],1)
                with self.assertRaisesRegex(AssertionError,'RAW_HASH_MISMATCH'):s.raw_binding(raw,'0'*64)
                with self.assertRaisesRegex(AssertionError,'RAW_BUDGET'):s.raw_binding(raw,maximum=1)
                raw.write_text(json.dumps(dict(status='PASS',tests_run=2,passed=['synthetic.test']*2)))
                with self.assertRaisesRegex(AssertionError,'RAW_COUNTS'):s.raw_binding(raw)
            with self.assertRaisesRegex(AssertionError,'RAW_BUDGET'):s.bounded_raw(dict(x='x'*128),maximum=64)
            with self.assertRaisesRegex(AssertionError,'EVENT_SIZE_BUDGET'):v.event('OVERSIZE',x='x'*(s.MAX_EVENT_BYTES+1))
            limit=s.MAX_EVENTS
            try:
                s.MAX_EVENTS=len(v.events)
                with self.assertRaisesRegex(AssertionError,'EVENT_BUDGET'):v.event('OVERCOUNT')
            finally:s.MAX_EVENTS=limit
            methods=unittest.defaultTestLoader.getTestCaseNames(type(self));expected=['test_'+r['id'] for r in s.plan()['proposed_tests']]
            self.assertEqual(methods,expected);s.validate_report(methods,expected,[],0)
            for passed,skipped,left,code in ((methods+methods[:1],[],0,'DUPLICATE_TEST_IDS'),(methods[:-1],[],0,'INCOMPLETE_CAMPAIGN'),(methods,['skip'],0,'INCOMPLETE_CAMPAIGN'),(methods,[],1,'RESOURCES_REMAINING')):
                with self.assertRaisesRegex(AssertionError,code):s.validate_report(passed,expected,skipped,left)
            self.assertEqual(sum(r['frontier']!='CONTROL' for r in s.plan()['proposed_tests']),60)
            self.assertEqual(len(s.plan()['frontier_rows']),35)
            v.passive();v.event('INVENTORY_NEGATIVES',maps_raw_inputs_budgets_verified=True)

    def test_FN01(self):self.frontier('FN01')

    def test_FN02(self):self.frontier('FN02')

    def test_FN03(self):self.frontier('FN03')

    def test_FN04(self):self.frontier('FN04')

    def test_FN05(self):self.frontier('FN05')

    def test_FN06(self):self.frontier('FN06')

    def test_FN07(self):self.frontier('FN07')

    def test_FN08(self):self.frontier('FN08')

    def test_FN09(self):self.frontier('FN09')

    def test_FN10(self):self.frontier('FN10')

    def test_FN11(self):self.frontier('FN11')

    def test_FN12(self):self.frontier('FN12')

    def test_FN13(self):self.frontier('FN13')

    def test_FN14(self):self.frontier('FN14')

    def test_FN15(self):self.frontier('FN15')

    def test_FN16(self):self.frontier('FN16')

    def test_FN17(self):self.frontier('FN17')

    def test_FN18(self):self.frontier('FN18')

    def test_FN19(self):self.frontier('FN19')

    def test_FN20(self):self.frontier('FN20')

    def test_FN21(self):self.frontier('FN21')

    def test_FN22(self):self.frontier('FN22')

    def test_FN23(self):self.frontier('FN23')

    def test_FN24(self):self.frontier('FN24')

    def test_FN25(self):self.frontier('FN25')

    def test_FN26(self):self.frontier('FN26')

    def test_FN27(self):self.frontier('FN27')

    def test_FN28(self):self.frontier('FN28')

    def test_FN29(self):self.frontier('FN29')

    def test_FN30(self):self.frontier('FN30')

    def test_FN31(self):self.frontier('FN31')

    def test_FN32(self):self.frontier('FN32')

    def test_FN33(self):self.frontier('FN33')

    def test_FN34(self):self.frontier('FN34')

    def test_FN35(self):self.frontier('FN35')

    def test_FN36(self):self.frontier('FN36')

    def test_FN37(self):self.frontier('FN37')

    def test_FN38(self):self.frontier('FN38')

    def test_FN39(self):self.frontier('FN39')

    def test_FN40(self):self.frontier('FN40')

    def test_FN41(self):self.frontier('FN41')

    def test_FN42(self):self.frontier('FN42')

    def test_FN43(self):self.frontier('FN43')

    def test_FN44(self):self.frontier('FN44')

    def test_FN45(self):self.frontier('FN45')

    def test_FN46(self):self.frontier('FN46')

    def test_FN47(self):self.frontier('FN47')

    def test_FN48(self):self.frontier('FN48')

    def test_FN49(self):self.frontier('FN49')

    def test_FN50(self):self.frontier('FN50')

    def test_FN51(self):self.frontier('FN51')

    def test_FN52(self):self.frontier('FN52')

    def test_FN53(self):self.frontier('FN53')

    def test_FN54(self):self.frontier('FN54')

    def test_FN55(self):self.frontier('FN55')

    def test_FN56(self):self.frontier('FN56')

    def test_FN57(self):self.frontier('FN57')

    def test_FN58(self):self.frontier('FN58')

    def test_FN59(self):self.frontier('FN59')

    def test_FN60(self):self.frontier('FN60')

    def test_FN61(self):self.protocol('FN61')

    def test_FN62(self):self.protocol('FN62')

    def test_FN63(self):self.inventory('FN63')

    def test_FN64(self):self.inventory('FN64')
