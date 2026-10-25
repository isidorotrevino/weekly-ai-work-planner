# SPDX-License-Identifier: GPL-3.0-only
"""CE01–CE43: each domain case keeps its own crash/reopen/continuation identity."""
import json
import tempfile
from pathlib import Path
import unittest
from testing.causal_frontier_cells import support as s


class CausalCellsTest(unittest.TestCase):
    def unchanged(self,b,a,allowed):
        self.assertEqual(set(b),set(a))
        for k in b:
            if k not in allowed:self.assertEqual(b[k],a[k],k)
    def send(self,v,values,status,ledger,queries,pending):
        a=values['client']['state'];send=a['sends'][v.sid]
        self.assertEqual((send['status'],send['ledger_version'],send['queries'],len(a['pending'])),(status,ledger,queries,pending))
        self.assertEqual(send['attempts'],[v.ticket]);return send
    def local_published(self,v,values):
        b=v.before['client']['state'];a=values['client']['state'];op=v.row['operation'];r=a['receipts'][v.cmd['cid']]
        self.assertEqual(r['request_sha256'],v.read['request_hash']);self.assertEqual(len(a['receipts']),len(b['receipts'])+1)
        if op=='APPLY':
            tid=s.T.uid(30);m=b['manifests'][v.ids['effect']]
            self.assertEqual(a['tasks'],{tid:m['after']});self.assertEqual(a['bases'],{tid:m['after']});self.assertEqual(a['mappings'],{tid:m['identity']})
            self.assertEqual(a['provenance'][tid],dict(source_id=m['source_id'],effect_manifest=v.ids['effect'],review_version=1));self.assertEqual(a['data_generation'],b['data_generation']+1)
            self.assertEqual((a['bindings'],a['sends']),({},{}));allowed={'tasks','bases','mappings','provenance','data_generation','receipts'}
        elif op=='ISSUE':
            self.send(v,values,'UNKNOWN',1,0,1);self.assertEqual(a['sends'][v.sid]['manifest_id'],v.mid);self.assertIn('send:'+v.ticket,a['pending']);allowed={'sends','pending','receipts'}
        elif op=='QUERY':
            self.send(v,values,'UNKNOWN',1,1,2);self.assertEqual(set(a['pending']),{'send:'+v.ticket,v.qid});allowed={'sends','pending','receipts'}
        else:
            send=self.send(v,values,'EFFECT_CONFIRMED',2,0,0);self.assertEqual(send['proof'],v.proof);allowed={'sends','pending','receipts'}
        self.unchanged(b,a,allowed);self.assertEqual(values['remote'],v.before['remote'])
    def remote_published(self,v,values):
        b=v.before['remote']['state'];a=values['remote']['state'];r=a['receipts'][v.cmd['cid']];m=v.cmd['args']['manifest'];mode=v.row['mode']
        self.assertEqual(r['request_sha256'],v.read['request_hash']);self.assertEqual(len(a['receipts']),len(b['receipts'])+1)
        p=a['tickets'][v.ticket];self.assertEqual(r['result'],p);self.assertEqual(p['manifest_hash'],s.digest(m));self.assertEqual(p['request_hash'],s.digest(m));self.assertEqual(p['ticket'],v.ticket)
        self.assertEqual(len(a['tickets']),len(b['tickets'])+1)
        if mode=='CLOSE':
            self.assertEqual((p['status'],p['remote_id'],p['applied_version'],p['payload_hash']),('CLOSED_NO_EFFECT',None,None,None));self.assertEqual(a['entities'],b['entities']);self.assertEqual(a['keys'],b['keys'])
        else:
            self.assertEqual(p['status'],'EFFECT_CONFIRMED');rid=p['remote_id'];entity=a['entities'][rid];self.assertEqual(entity['payload'],m['payload']);self.assertEqual(s.digest(entity['payload']),p['payload_hash'])
            self.assertEqual(len(a['entities']),1);self.assertEqual(a['keys'][m['creation_key']],rid)
            if mode=='CREATE':self.assertEqual((entity['version'],p['applied_version'],entity['foreign']),(1,1,{}));self.assertFalse(b['entities'])
            else:
                self.assertEqual((b['entities'][rid]['version'],entity['version'],p['applied_version']),(2,3,3));self.assertEqual(entity['foreign'],{'sentinel':'CE_KEEP'})
                self.assertEqual(m['remote_base'],b['entities'][rid]);self.assertNotEqual(entity['payload'],b['entities'][rid]['payload']);self.assertEqual(a['keys'],b['keys'])
        self.unchanged(b,a,{'entities','keys','tickets','receipts'})
        self.assertEqual(values['client'],v.before['client'])
    def initial(self,v):
        b=v.before['client']['state'];op=v.row['operation'];r=v.before['remote']['state']
        self.assertNotIn(v.cmd['cid'],v.before['remote' if v.row['role']=='REMOTE' else 'client']['state']['receipts'])
        if op=='APPLY':
            for k in ('tasks','bases','mappings','provenance','bindings','sends'):self.assertEqual(b[k],{})
            self.assertEqual(b['reviews']['EFFECT:'+v.ids['effect']]['decision'],'ACCEPT')
        elif op=='ISSUE':self.assertEqual(b['sends'],{});self.assertEqual(r['tickets'],{});self.assertEqual(r['entities'],{})
        else:
            self.send(v,v.before,'UNKNOWN',1,0,1)
            if op in ('QUERY','RESULT_DISPATCH'):self.assertEqual(r['tickets'][v.ticket],v.proof);self.assertEqual(len(r['entities']),1)
            else:
                self.assertNotIn(v.ticket,r['tickets'])
                if v.row['mode']=='UPDATE':
                    self.assertEqual(len(r['entities']),1);entity=next(iter(r['entities'].values()));self.assertEqual((entity['version'],entity['foreign']),(2,{'sentinel':'CE_KEEP'}))
                    self.assertEqual(v.record['update_setup']['create_entity']['version'],1)
                else:self.assertEqual(r['entities'],{})
        if v.path=='T':
            src=b['sources'][v.ids['source']];self.assertEqual(src['pin'],v.record['capture']['pin']);self.assertEqual(src['capture']['content_sha256'],v.record['capture']['source_bytes_sha256'])
        else:
            batch=v.record['batch'];receipt=b['receipts'][batch['command_id']];self.assertEqual(receipt['request_sha256'],batch['request_sha256']);self.assertIn(v.tid,receipt['result']['participants'])
            self.assertEqual(b['selection']['batch_command'],batch['command_id']);self.assertEqual(b['selection']['batch_request'],batch['request_sha256']);self.assertIn(v.tid,b['selection']['task_ids'])
    def historical_clock(self,v):
        v.run(dict(action='clock',tick=1));later=v.observe('later_clock');out=v.run(v.job('replay'))
        self.assertTrue(out['value']['historical']);self.assertEqual(out['transport']['execute'],0);self.assertEqual(v.observe('historical_replay_no_rewind'),later)
    def domain(self,case):
        row=next(r for r in s.plan()['proposed_tests'] if r['id']==case)
        with s.Scenario(row) as v:
            v.prepare();self.initial(v);remote=row['role']=='REMOTE';role='remote' if remote else 'client';yes=row['expected_published'];op=row['operation']
            values=v.crash();self.assertEqual(values[role]['head']['seq'],v.before[role]['head']['seq']+int(yes))
            if yes:
                (self.remote_published if remote else self.local_published)(v,values)
                obj=values[role]['chain'][-1];self.assertEqual(obj['command_id'],v.cmd['cid']);self.assertEqual(obj['operation'],{k:v.cmd[k] for k in ('kind','args','expected')})
            else:self.assertEqual(values[role],v.before[role])
            if remote:self.assertEqual(values['client'],v.before['client'])
            else:self.assertEqual(values['remote'],v.before['remote'])
            reads=v.passive()['reads'];self.assertEqual(reads[0].get('historical',False),yes)
            if yes:self.assertEqual(reads[0]['request_sha256'],v.read['request_hash'])
            else:self.assertEqual(reads[0]['result'],'NOT_COMMITTED_AT_HEAD')
            if remote:
                out=v.run(dict(action='reconcile',sid=v.sid,close=not yes));self.assertEqual((out['transport']['execute'],out['transport']['lookup']),(int(not yes),int(yes)))
                settled=v.observe('explicit_reconcile');status=('CLOSED_NO_EFFECT' if not yes or row['mode']=='CLOSE' else 'EFFECT_CONFIRMED')
                send=self.send(v,settled,status,2,1,0);self.assertEqual(send['proof'],settled['remote']['state']['tickets'][v.ticket])
                if yes:self.assertEqual(settled['remote'],values['remote'])
                else:self.assertEqual(settled['remote']['state']['entities'],v.before['remote']['state']['entities']);self.assertEqual(settled['remote']['state']['keys'],v.before['remote']['state']['keys'])
                # Public repetition after settlement: immutable business state; a different EXECUTE may add a receipt after CLOSE.
                out=v.run(v.job('remote_repeat'));self.assertEqual(out['value'],send['proof']);repeated=v.observe('explicit_remote_repeat')
                for k in ('entities','keys','tickets'):self.assertEqual(repeated['remote']['state'][k],settled['remote']['state'][k])
                self.assertEqual(repeated['client'],settled['client'])
                if yes or row['mode']=='CLOSE':self.assertEqual(repeated['remote'],settled['remote'])
                else:self.assertEqual(repeated['remote']['head']['seq'],settled['remote']['head']['seq']+1)
                finalread=v.passive()['reads'][0];self.assertTrue(finalread['historical']);self.assertEqual(finalread['request_sha256'],v.read['request_hash'])
            elif op=='RESULT_DISPATCH' and not yes:
                out=v.run(dict(action='reconcile',sid=v.sid));self.assertEqual((out['transport']['execute'],out['transport']['lookup']),(0,1));settled=v.observe('explicit_query_recovery')
                self.send(v,settled,'EFFECT_CONFIRMED',2,1,0);self.assertNotIn(v.cmd['cid'],settled['client']['state']['receipts']);self.assertEqual(settled['remote'],v.before['remote']);v.passive()
            else:
                out=v.run(v.job('replay'));self.assertEqual(out['value']['historical'],yes);self.assertEqual(out['transport']['execute'],0)
                replayed=v.observe('explicit_replay')
                if yes:self.assertEqual(replayed,values)
                else:self.local_published(v,replayed)
                self.historical_clock(v)
                if op=='QUERY':
                    out=v.run(dict(action='query_result',sid=v.sid,qid=v.qid));self.assertEqual((out['transport']['execute'],out['transport']['lookup']),(0,1));settled=v.observe('explicit_original_query_result');self.send(v,settled,'EFFECT_CONFIRMED',2,1,0);self.assertEqual(settled['remote'],v.before['remote'])
                elif op=='ISSUE':
                    out=v.run(dict(action='reconcile',sid=v.sid,close=True));self.assertEqual((out['transport']['execute'],out['transport']['lookup']),(1,0));settled=v.observe('explicit_close');self.send(v,settled,'CLOSED_NO_EFFECT',2,1,0);self.assertEqual(settled['remote']['state']['entities'],{})
                v.passive()
            v.record['same_sequence_verified']=True

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
            expected.update(manifest_operation='CREATE',manifest_sha256='4'*64,creation_key='5'*64,binding_id=s.uid(),target_id=s.uid(),remote_base_sha256='6'*64,capabilities_sha256='7'*64,ledger=1)
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
            self.assertEqual(sum(r['role']!='CONTROL' for r in s.plan()['proposed_tests']),39)
            self.assertEqual(s.plan()['counts']['baseline_cells'],140)
            v.passive();v.event('INVENTORY_NEGATIVES',maps_raw_inputs_budgets_verified=True)

    def test_CE01(self):self.domain('CE01')

    def test_CE02(self):self.domain('CE02')

    def test_CE03(self):self.domain('CE03')

    def test_CE04(self):self.domain('CE04')

    def test_CE05(self):self.domain('CE05')

    def test_CE06(self):self.domain('CE06')

    def test_CE07(self):self.domain('CE07')

    def test_CE08(self):self.domain('CE08')

    def test_CE09(self):self.domain('CE09')

    def test_CE10(self):self.domain('CE10')

    def test_CE11(self):self.domain('CE11')

    def test_CE12(self):self.domain('CE12')

    def test_CE13(self):self.domain('CE13')

    def test_CE14(self):self.domain('CE14')

    def test_CE15(self):self.domain('CE15')

    def test_CE16(self):self.domain('CE16')

    def test_CE17(self):self.domain('CE17')

    def test_CE18(self):self.domain('CE18')

    def test_CE19(self):self.domain('CE19')

    def test_CE20(self):self.domain('CE20')

    def test_CE21(self):self.domain('CE21')

    def test_CE22(self):self.domain('CE22')

    def test_CE23(self):self.domain('CE23')

    def test_CE24(self):self.domain('CE24')

    def test_CE25(self):self.domain('CE25')

    def test_CE26(self):self.domain('CE26')

    def test_CE27(self):self.domain('CE27')

    def test_CE28(self):self.domain('CE28')

    def test_CE29(self):self.domain('CE29')

    def test_CE30(self):self.domain('CE30')

    def test_CE31(self):self.domain('CE31')

    def test_CE32(self):self.domain('CE32')

    def test_CE33(self):self.domain('CE33')

    def test_CE34(self):self.domain('CE34')

    def test_CE35(self):self.domain('CE35')

    def test_CE36(self):self.domain('CE36')

    def test_CE37(self):self.domain('CE37')

    def test_CE38(self):self.domain('CE38')

    def test_CE39(self):self.domain('CE39')

    def test_CE40(self):self.protocol('CE40')

    def test_CE41(self):self.protocol('CE41')

    def test_CE42(self):self.inventory('CE42')

    def test_CE43(self):self.inventory('CE43')
