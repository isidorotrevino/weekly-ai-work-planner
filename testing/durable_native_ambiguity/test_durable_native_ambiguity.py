# SPDX-License-Identifier: GPL-3.0-only
"""NA01–NA36: assertions use independent reachable file state, not PASS counters."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from source_ingest import durable_ambiguity_fixture as n
from source_ingest.durable_store import DurableError
from testing.durable_native_ambiguity import support as s


class NativeAmbiguityTest(unittest.TestCase):
    def state(self,v,status,ledger,queries,hard=False):
        values=v.observe('assert_'+status+'_'+str(ledger));c=s.core(values['client']);send=c['sends'][v.sid]
        self.assertEqual((send['status'],send['ledger_version'],send['queries'],send['hard_conflict']),(status,ledger,queries,hard))
        self.assertEqual(send['attempts'][0],v.ticket)
        self.assertNotIn('receipts',values['client']['state']['core'])
        self.assertEqual(len(values['client']['state']['extension']['observations']),ledger-len(send['attempts']))
        return values
    def effect(self,v,values,entities=1):
        remote=s.core(values['remote']);self.assertEqual(len(remote['entities']),entities)
        if entities:
            p=remote['tickets'][v.ticket];entity=remote['entities'][p['remote_id']]
            self.assertEqual(p['ticket'],v.ticket);self.assertEqual(p['manifest_hash'],s.digest(v.manifest))
            self.assertEqual(entity['version'],p['applied_version']);self.assertEqual(entity['payload'],v.manifest['payload'])
            self.assertEqual(s.digest(entity['payload']),p['payload_hash']);self.assertEqual(entity['foreign'],{})
            self.assertEqual(remote['keys'],{v.manifest['creation_key']:p['remote_id']})
    def blocked(self,v):
        before=v.observe('before_retry_rejected')
        v.call('dispatch',dict(mid=v.mid,review_version=1,send_id=v.sid,retry=True),error='BINDING_UNRESOLVED')
        self.assertEqual(v.observe('after_retry_rejected'),before)
    def readonly_reconcile(self,v):
        before=s.files(v.value)['remote'];e=v.reconcile()
        self.assertEqual(e['calls'],dict(execute=0,query=1));self.assertEqual(s.files(v.value)['remote'],before)
        return e
    def empty(self,case,path):
        with s.Scenario(case,path) as v:
            v.prepare();v.issue();self.readonly_reconcile(v)
            values=self.state(v,'UNKNOWN',2,1);self.effect(v,values,0)
            self.assertIn('send:'+v.ticket,s.core(values['client'])['pending']);self.blocked(v);v.passive()
    def single(self,case,path,proof):
        with s.Scenario(case,path) as v:
            v.prepare();v.issue()
            if proof:v.deliver()
            else:v.declare([v.match()])
            self.readonly_reconcile(v);values=self.state(v,'EFFECT_CONFIRMED' if proof else 'UNKNOWN',2,1)
            self.effect(v,values,int(proof))
            if proof:self.assertFalse(s.core(values['client'])['pending'])
            else:
                self.assertIsNone(s.core(values['client'])['sends'][v.sid]['proof']);self.blocked(v)
            v.passive()
    def multi(self,case,path,proof):
        for repeated in ((False,True) if not proof else (False,)):
            with s.Scenario(case,path) as v:
                v.record['subvariant']='REPEATED_ID' if repeated else 'DISTINCT_IDS'
                v.prepare();v.issue()
                if proof:
                    e=v.deliver();match=e['matches'][0]
                else:match=v.match()
                other=copy.deepcopy(match) if repeated else v.match()
                v.declare([match,other]);self.readonly_reconcile(v)
                values=self.state(v,'CONFLICT',2,1,True);self.effect(v,values,int(proof))
                observations=values['client']['state']['extension']['observations'];self.assertEqual(observations[-1]['classification'],'MULTIPLE_MATCHES')
                self.assertEqual(observations[-1]['envelope']['matches'],[match,other]);self.assertFalse(observations[-1]['adopted'])
                self.assertIsNone(s.core(values['client'])['sends'][v.sid]['proof']);self.assertFalse(s.core(values['client'])['pending'])
                if proof:
                    v.declare([match]);self.readonly_reconcile(v);after=self.state(v,'CONFLICT',3,2,True)
                    self.assertEqual(s.core(after['remote'])['entities'],s.core(values['remote'])['entities'])
                    self.assertIsNone(s.core(after['client'])['sends'][v.sid]['proof'])
                    self.assertEqual(after['client']['state']['extension']['observations'][0],observations[0])
                self.blocked(v);v.passive()
    def foreign_match(self,case,path):
        for field in ('creation_key','scope_hash'):
            with s.Scenario(case,path) as v:
                v.record['subvariant']=field;v.prepare();v.issue();v.declare([v.match(**{field:'0'*64})]);self.readonly_reconcile(v)
                values=self.state(v,'CONFLICT',2,1,True);self.effect(v,values,0);self.blocked(v);v.passive()
    def foreign_proof(self,case,path):
        with s.Scenario(case,path) as v,s.Scenario(case,'R' if path=='T' else 'T') as donor:
            donor.record['role']='FOREIGN_DONOR';donor.prepare();donor.issue();p=donor.deliver()['proof']
            v.prepare();v.issue();q=v.query();e=n.reseal(dict(q['envelope'],proof=p))
            v.event('FOREIGN_PROOF_INPUT',donor_run_id=donor.lab.run_id,donor_ticket=donor.ticket,proof=p)
            q['envelope']=e;v.observe_query(q);values=self.state(v,'CONFLICT',2,1,True)
            self.effect(v,values,0);self.assertIsNone(s.core(values['client'])['sends'][v.sid]['proof']);self.blocked(v);v.passive();donor.passive()
    def ambiguous(self,case,path,after):
        with s.Scenario(case,path) as v:
            v.prepare();mode='AMBIGUOUS_429_AFTER' if after else 'AMBIGUOUS_429_BEFORE';e=v.dispatch(mode)
            self.assertEqual(e['calls'],dict(execute=1,query=0));envelope=e['value']['envelope']
            self.assertEqual(envelope['http_status'],429);self.assertIsNone(envelope['proof']);self.assertEqual(envelope['matches'],[])
            self.assertNotIn('mode',envelope)
            values=self.state(v,'UNKNOWN',2,0);self.assertFalse(s.core(values['client'])['pending']);self.effect(v,values,int(after));v.passive();self.blocked(v)
            # Native replay and altered mode cannot create a second effect or move the original response HEAD.
            v.declare([],visible=False);before=v.observe('before_execute_replay')
            self.assertEqual(v.deliver(mode),envelope);self.assertEqual(v.observe('after_execute_replay'),before)
            v.call('execute',dict(ticket=v.ticket,m=v.manifest,mode='SUCCESS'),error='COMMAND_CONFLICT')
            self.assertEqual(v.observe('after_mode_conflict'),before)
            if after:
                match=dict(remote_id=s.core(values['remote'])['tickets'][v.ticket]['remote_id'],creation_key=v.manifest['creation_key'],
                    scope_hash=n.scope_hash(v.lab.config),version=1,payload_hash=s.digest(v.manifest['payload']))
                v.declare([match])
            self.readonly_reconcile(v);final=self.state(v,'EFFECT_CONFIRMED' if after else 'UNKNOWN',3,1);self.effect(v,final,int(after));v.passive()
    def query_429(self,case,path):
        with s.Scenario(case,path) as v:
            v.prepare();v.issue();e=v.deliver();v.declare(e['matches'],query_status=429,retry_after_tick=5)
            self.readonly_reconcile(v);values=self.state(v,'UNKNOWN',2,1);self.effect(v,values);v.passive()
            self.assertIn('send:'+v.ticket,s.core(values['client'])['pending']);self.blocked(v)
            v.declare(e['matches']);self.readonly_reconcile(v);self.state(v,'EFFECT_CONFIRMED',3,2);v.passive()
    def retry_ambiguous(self,case,path):
        with s.Scenario(case,path) as v:
            v.prepare();v.dispatch('AMBIGUOUS_429_BEFORE',5);v.call('core',dict(kind='CLOCK',args=dict(tick=5)))
            self.state(v,'UNKNOWN',2,0);self.blocked(v)
            before=v.observe('before_new_send');v.call('dispatch',dict(mid=v.mid,review_version=1),error='BINDING_UNRESOLVED')
            self.assertEqual(v.observe('after_new_send'),before)
            # New manifest and reviewed version, same unresolved binding. No budget reset.
            core=v.lab.client.core
            if path=='T':
                ef=v.call('core',dict(kind='PREPARE_EFFECT',args=dict(evaluation=v.ids['evaluation'],evaluation_review=1,
                    source_key='FIX-1',target_id=v.manifest['target_id'],target_key=v.manifest['task']['key'])))['value']['result']['manifest_id']
                core.review('EFFECT',ef);v.call('core',dict(kind='APPLY',args=dict(manifest_id=ef,review_version=1)))
            else:
                receipt=v.ids['apply'];v.call('core',dict(kind='SELECT_TASKS',args=dict(batch_command=receipt['command_id'],
                    batch_request=receipt['request_sha256'],task_ids=v.ids['task_ids'])))
            mid=core.prepare_projection(v.manifest['binding']['binding_id'])['result']['manifest_id'];core.review('PROJECTION',mid)
            self.assertNotEqual(mid,v.mid)
            v.event('NEW_PACKAGE_SAME_BINDING',old_manifest=v.mid,new_manifest=mid,binding_id=v.manifest['binding']['binding_id'])
            before=v.observe('before_new_package');v.call('dispatch',dict(mid=mid,review_version=1),error='BINDING_UNRESOLVED')
            self.assertEqual(v.observe('after_new_package'),before);self.effect(v,before,0);v.passive()
    def conclusive(self,case,path):
        with s.Scenario(case,path) as v:
            v.prepare();v.dispatch('CONCLUSIVE_RATE_LIMIT',5);values=self.state(v,'NO_EFFECT',2,0);self.effect(v,values,0)
            p=s.core(values['client'])['sends'][v.sid]['proof'];self.assertEqual((p['code'],p['retry_tick']),('RATE_LIMIT',5))
            before=v.observe('before_early_retry');v.call('dispatch',dict(mid=v.mid,review_version=1,send_id=v.sid,retry=True),error='RETRY_NOT_ELIGIBLE')
            self.assertEqual(v.observe('after_early_retry'),before);v.call('core',dict(kind='CLOCK',args=dict(tick=5)))
            out=v.call('dispatch',dict(mid=v.mid,review_version=1,send_id=v.sid,retry=True))['value'];final=self.state(v,'EFFECT_CONFIRMED',4,0)
            send=s.core(final['client'])['sends'][v.sid];self.assertEqual(send['attempts'],[v.ticket,out['ticket']]);self.assertNotEqual(out['ticket'],v.ticket)
            remote=s.core(final['remote']);self.assertEqual(len(remote['entities']),1);self.assertEqual(len(remote['tickets']),2)
            self.assertEqual(send['proof'],remote['tickets'][out['ticket']]);self.assertEqual(next(iter(remote['entities'].values()))['version'],1);v.passive()
    def invalid(self,case,path):
        with s.Scenario(case,path) as v:
            v.prepare();v.issue();q=v.query();original=q['envelope'];before=v.observe('before_invalid')
            bad=[]
            for key,value,code in [('schema','other','OBSERVATION_SCHEMA'),('http_status',True,'OBSERVATION_STATUS'),('http_status',503,'OBSERVATION_STATUS'),
                ('retry_after_tick',True,'INVALID_INTEGER'),('channel','OTHER','OBSERVATION_CHANNEL'),('matches',[v.match()]*9,'MATCH_BUDGET'),
                ('proof',[],'OBSERVATION_PROOF_TYPE')]:bad.append((n.reseal(dict(original,**{key:value})),code))
            bad.extend([(dict(original,response_id='0'*64),'RESPONSE_HASH'),(dict(original,extra=0),'INVALID_SHAPE')])
            # Exact 64KiB envelope remains structurally valid; +1 fails. Proof contents here are a deliberate negative.
            e=dict(original,proof=dict(padding=''));e=n.reseal(e);size=len(n.canonical(e));e['proof']['padding']='x'*(n.MAX_ENVELOPE-size);e=n.reseal(e)
            self.assertEqual(len(n.canonical(e)),n.MAX_ENVELOPE);n.envelope_shape(e)
            too=copy.deepcopy(e);too['proof']['padding']+='x';bad.append((n.reseal(too),'ENVELOPE_BUDGET'))
            for e,code in bad:
                q['envelope']=e;v.call('observe',dict(sid=q['sid'],ledger=q['ledger'],query_id=q['query_id'],envelope=e),error=code)
                self.assertEqual(v.observe('invalid_'+code),before)
            # Match limit is native, not a list used as malformed proof.
            matches=[v.match() for _ in range(8)];v.declare(matches);n.matches_shape(matches)
            v.call('declare',dict(key=v.manifest['creation_key'],matches=matches+[v.match()]),error='MATCH_BUDGET')
            q['envelope']=original;v.observe_query(q);self.state(v,'UNKNOWN',2,1);v.passive()
        for conflict in ('positive_429','tick_mismatch'):
            with s.Scenario(case,path) as v:
                v.record['subvariant']=conflict;v.prepare();v.issue()
                if conflict=='positive_429':v.deliver();q=v.query();e=n.reseal(dict(q['envelope'],http_status=429))
                else:
                    v.deliver('CONCLUSIVE_RATE_LIMIT',5);q=v.query();e=n.reseal(dict(q['envelope'],http_status=429,retry_after_tick=6))
                v.event('DELIBERATE_METADATA_NEGATIVE',subvariant=conflict,envelope=e)
                q['envelope']=e;v.observe_query(q);self.state(v,'CONFLICT',2,1,True);self.blocked(v);v.passive()
        with s.Scenario(case,path,proof_bytes=16) as v:
            v.record['subvariant']='REDUCED_PROOF_BUDGET';v.prepare();v.issue();v.deliver();q=v.query();before=v.observe('before_proof_budget')
            self.assertGreater(len(n.canonical(q['envelope']['proof'])),16)
            v.call('observe',dict(sid=q['sid'],ledger=q['ledger'],query_id=q['query_id'],envelope=q['envelope']),error='PROOF_BUDGET')
            self.assertEqual(v.observe('after_proof_budget'),before);self.state(v,'UNKNOWN',1,1);v.passive()
    def replay(self,case,path):
        with s.Scenario(case,path) as v:
            v.prepare();v.issue();v.deliver();q=v.query();snap=v.lab.client.snapshot();expected={k:snap['head'][k] for k in ('seq','commit_sha256')};cid=s.uid()
            args=dict(sid=q['sid'],ledger=q['ledger'],query_id=q['query_id'],envelope=q['envelope'],cid=cid,expected=expected)
            first=v.call('observe',args)['value'];values=self.state(v,'EFFECT_CONFIRMED',2,1)
            v.call('core',dict(kind='CLOCK',args=dict(tick=5)));before=v.observe('before_replay')
            repeat=v.call('observe',args)['value'];self.assertTrue(repeat['historical']);self.assertEqual({k:z for k,z in first.items() if k!='historical'},{k:z for k,z in repeat.items() if k!='historical'})
            self.assertEqual(v.observe('after_replay'),before)
            other=copy.deepcopy(args);other['envelope']=n.reseal(dict(args['envelope'],retry_after_tick=1));v.call('observe',other,error='COMMAND_CONFLICT')
            other=copy.deepcopy(args);other['cid']=s.uid();other.pop('expected');v.call('observe',other,error='CONFLICT_LEDGER')
            self.assertEqual(v.observe('after_replay_negatives'),before);self.effect(v,values);v.passive()
    def crash(self,case,path,point):
        with s.Scenario(case,path) as v:
            v.prepare();v.issue();v.deliver();before=v.observe('before_crash');command=v.crash(point)
            values=self.state(v,'UNKNOWN' if point=='before_observe' else 'EFFECT_CONFIRMED',1 if point=='before_observe' else 2,1)
            self.assertEqual(values['remote'],before['remote']);self.effect(v,values);v.passive()
            if point=='before_observe':
                self.assertEqual(len(s.core(values['client'])['pending']),2);self.readonly_reconcile(v);final=self.state(v,'EFFECT_CONFIRMED',2,2);self.assertFalse(s.core(final['client'])['pending'])
            else:
                old=v.observe('before_crash_replay');r=v.call('observe',command)['value'];self.assertTrue(r['historical']);self.assertEqual(v.observe('after_crash_replay'),old)
                self.assertIn(command['cid'],values['client']['state']['receipts'])
            v.passive()
    def ownership(self,case,path):
        with s.Scenario(case,path) as v:
            v.passive();saved=v.lab.home/'own_saved_run';v.lab.root.rename(saved);v.lab.root.mkdir()
            try:s.expect_error('CLEANUP_OWNERSHIP',v.lab.close)
            finally:v.lab.root.rmdir();saved.rename(v.lab.root)
            owner=v.lab.root/'owner.json';raw=owner.read_bytes();owner.write_bytes(b'{}')
            try:s.expect_error('CLEANUP_MARKER',v.lab.close)
            finally:owner.write_bytes(raw)
            sentinel=v.lab.sentinel.read_bytes();v.lab.sentinel.write_bytes(b'ALTERED')
            try:s.expect_error('SENTINEL_CHANGED',v.lab.close)
            finally:v.lab.sentinel.write_bytes(sentinel)
            link=v.lab.root/'client'/'own_link';link.symlink_to(v.lab.sentinel)
            try:s.expect_error('CLEANUP_SYMLINK',v.lab.close)
            finally:link.unlink()
            expected=dict(role='CLIENT',variant=v.lab.variant,operation='OBSERVE',point='before_observe',ticket=s.uid(),run_id=v.lab.run_id,
                client_store_id=v.lab.client_id,remote_store_id=v.lab.remote_id,send_id=s.uid(),manifest_id='0'*64,cid=s.uid())
            message=dict(event='READY',**expected);s.expected_ready(message,expected)
            for k in expected:
                with self.assertRaisesRegex(AssertionError,'READY_IDENTITY'):s.expected_ready(dict(message,**{k:'WRONG'}),expected)
            with self.assertRaisesRegex(AssertionError,'MISSING_READY'):s.expected_ready(dict(event='DONE'),expected)
            for target,code in ((s.controls.normal_child,'MISSING_READY'),(s.controls.empty_child,'CONTROL_EOF'),(s.controls.held_child,'CONTROL_TIMEOUT')):
                pair=s.start(target,(),dict(case=case,action='negative_protocol',path=path));v.children.append(pair)
                try:
                    if target is s.controls.held_child:
                        self.assertEqual(s.receive(pair[1])['event'],'READY')
                        with self.assertRaisesRegex(AssertionError,code):s.receive(pair[1],0.02)
                    elif target is s.controls.empty_child:
                        with self.assertRaisesRegex(AssertionError,code):s.receive(pair[1])
                    else:
                        with self.assertRaisesRegex(AssertionError,code):s.expected_ready(s.receive(pair[1]),expected)
                    if target is not s.controls.held_child:
                        s.finish(*pair);self.assertEqual(pair[0].exitcode,0)
                    v.event('PROTOCOL_NEGATIVE',kind=code,normal_exit_checked=target is not s.controls.held_child)
                finally:s.stop_owned([pair])
            v.event('PROTOCOL_OWNERSHIP_NEGATIVES',restored_before_cleanup=True,timeout_not_positive_crash=True)
    def inventory(self,case,path):
        with s.Scenario(case,path) as v:
            with tempfile.TemporaryDirectory(prefix='d5-i55-inventory-') as directory:
                s.EXTRA_ROOTS.append(directory);p=Path(directory)/'input';p.write_text('a');before=s.hash_inputs([p]);p.write_text('b')
                with self.assertRaisesRegex(AssertionError,'STALE_INPUTS'):s.validate_inventory(before,s.hash_inputs([p]))
                q=Path(directory)/'added';q.write_text('a')
                with self.assertRaisesRegex(AssertionError,'STALE_INPUTS'):s.validate_inventory(s.hash_inputs([p]),s.hash_inputs([p,q]))
                raw=Path(directory)/'raw'
                with self.assertRaisesRegex(AssertionError,'RAW_MISSING_OR_TYPE'):s.raw_binding(raw)
                for invalid in ('{','{"status":"PASS","status":"FAIL"}','{"x":NaN}'):
                    raw.write_text(invalid)
                    with self.assertRaisesRegex(AssertionError,'RAW_INCOMPATIBLE'):s.raw_binding(raw)
                raw.write_text(json.dumps(dict(status='PASS',tests_run=1,passed=['synthetic.test'])))
                self.assertEqual(s.raw_binding(raw)['tests_run'],1)
                with self.assertRaisesRegex(AssertionError,'RAW_HASH_MISMATCH'):s.raw_binding(raw,'0'*64)
                with self.assertRaisesRegex(AssertionError,'RAW_BUDGET'):s.raw_binding(raw,maximum=1)
                raw.write_text(json.dumps(dict(status='PASS',tests_run=2,passed=['synthetic.test']*2)))
                with self.assertRaisesRegex(AssertionError,'RAW_COUNTS'):s.raw_binding(raw)
            with self.assertRaisesRegex(AssertionError,'RAW_BUDGET'):s.bounded_raw(dict(x='x'*128),maximum=64)
            with self.assertRaisesRegex(AssertionError,'EVENT_SIZE_BUDGET'):v.event('OVERSIZE',x='x'*(s.MAX_EVENT_BYTES+1))
            maximum=s.MAX_EVENTS
            try:
                s.MAX_EVENTS=len(v.events)
                with self.assertRaisesRegex(AssertionError,'EVENT_BUDGET'):v.event('OVERCOUNT')
            finally:s.MAX_EVENTS=maximum
            design=json.loads(Path('docs/validation/D5-I54-design-review.json').read_text());methods=unittest.defaultTestLoader.getTestCaseNames(type(self));expected=['test_'+r['id'] for r in design['cases']]
            self.assertEqual(methods,expected);s.validate_report(methods,expected,[],0)
            for passed,skipped,left,code in [(methods+methods[:1],[],0,'DUPLICATE_TEST_IDS'),(methods[:-1],[],0,'INCOMPLETE_CAMPAIGN'),(methods,['skip'],0,'INCOMPLETE_CAMPAIGN'),(methods,[],1,'RESOURCES_REMAINING')]:
                with self.assertRaisesRegex(AssertionError,code):s.validate_report(passed,expected,skipped,left)
            # Config is closed in both directions. Opening a real new root with a legacy reducer also fails.
            base=v.lab.config['base_config'];m=n.module(v.lab.variant)
            with self.assertRaises(DurableError):(m.validate_config if path=='T' else m.valid_config)(v.lab.config)
            with self.assertRaises(DurableError):n.validate_config(base)
            legacy=n.T.Client(v.lab.root/'client',v.lab.run_id,v.lab.client_id,v.lab.capture,n.T.Remote(v.lab.root/'remote',v.lab.run_id,v.lab.remote_id)) if path=='T' else n.R.Client(v.lab.root/'client',v.lab.run_id,v.lab.client_id,n.R.Remote(v.lab.root/'remote',v.lab.run_id,v.lab.remote_id))
            before=v.observe('before_wrong_namespace')
            with self.assertRaises(DurableError):legacy.snapshot()
            wrong=n.Client(v.lab.root/'client',v.lab.run_id,v.lab.client_id,v.lab.remote,capture=v.lab.capture,variant='NATIVE_R' if path=='T' else 'NATIVE_T')
            s.expect_error('NATIVE_NAMESPACE_REQUIRED',wrong.snapshot);self.assertEqual(v.observe('after_wrong_namespace'),before)
            # Reverse direction: an owned legacy root cannot be silently opened as native.
            helper=s.T if path=='T' else s.R
            with helper.new_lab() as old:
                old_before={role:s.independent(old.root/role) for role in ('client','remote')}
                native_remote=n.Remote(old.root/'remote',old.run_id,old.remote_id)
                native=n.Client(old.root/'client',old.run_id,old.client_id,native_remote,variant=v.lab.variant)
                with self.assertRaises(DurableError):native.snapshot()
                with self.assertRaises(DurableError):native_remote.snapshot()
                self.assertEqual({role:s.independent(old.root/role) for role in ('client','remote')},old_before)
                v.event('LEGACY_ROOT_NATIVE_OPEN_REJECTED',run_id=old.run_id,head_hashes={role:z['head']['commit_sha256'] for role,z in old_before.items()})
            # Exact 64-view capacity remains below outer command budget; +1 hits the domain guard.
            for i in range(n.MAX_VIEWS):v.lab.remote.declare_view(f'{i:064x}',[])
            snap=v.lab.remote.snapshot();self.assertEqual(len(snap['state']['extension']['views']),n.MAX_VIEWS)
            s.expect_error('VIEW_BUDGET',v.lab.remote.declare_view,'f'*64,[]);self.assertEqual(v.lab.remote.snapshot(),snap)
            v.observe('view_capacity_rejected')
            v.event('INVENTORY_NEGATIVES',maps_inputs_raw_budgets_namespaces_verified=True,views_limit=n.MAX_VIEWS)

    def test_NA01(self):self.empty('NA01','T')

    def test_NA02(self):self.empty('NA02','R')

    def test_NA03(self):self.single('NA03','T',False)

    def test_NA04(self):self.single('NA04','R',False)

    def test_NA05(self):self.single('NA05','T',True)

    def test_NA06(self):self.single('NA06','R',True)

    def test_NA07(self):self.multi('NA07','T',False)

    def test_NA08(self):self.multi('NA08','R',False)

    def test_NA09(self):self.multi('NA09','T',True)

    def test_NA10(self):self.multi('NA10','R',True)

    def test_NA11(self):self.foreign_match('NA11','T')

    def test_NA12(self):self.foreign_match('NA12','R')

    def test_NA13(self):self.foreign_proof('NA13','T')

    def test_NA14(self):self.foreign_proof('NA14','R')

    def test_NA15(self):self.ambiguous('NA15','T',False)

    def test_NA16(self):self.ambiguous('NA16','R',False)

    def test_NA17(self):self.ambiguous('NA17','T',True)

    def test_NA18(self):self.ambiguous('NA18','R',True)

    def test_NA19(self):self.query_429('NA19','T')

    def test_NA20(self):self.query_429('NA20','R')

    def test_NA21(self):self.retry_ambiguous('NA21','T')

    def test_NA22(self):self.retry_ambiguous('NA22','R')

    def test_NA23(self):self.conclusive('NA23','T')

    def test_NA24(self):self.conclusive('NA24','R')

    def test_NA25(self):self.invalid('NA25','T')

    def test_NA26(self):self.invalid('NA26','R')

    def test_NA27(self):self.replay('NA27','T')

    def test_NA28(self):self.replay('NA28','R')

    def test_NA29(self):self.crash('NA29','T','before_observe')

    def test_NA30(self):self.crash('NA30','R','before_observe')

    def test_NA31(self):self.crash('NA31','T','after_head')

    def test_NA32(self):self.crash('NA32','R','after_head')

    def test_NA33(self):self.ownership('NA33','T')

    def test_NA34(self):self.ownership('NA34','R')

    def test_NA35(self):self.inventory('NA35','T')

    def test_NA36(self):self.inventory('NA36','R')
