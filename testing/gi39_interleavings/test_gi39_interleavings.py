# SPDX-License-Identifier: GPL-3.0-only
"""I64 causal actor orders, mutation-specific errors and historical remote effects."""
import copy
from copy import deepcopy
import uuid
import json
from pathlib import Path
import tempfile
import unittest
from testing.gi39_interleavings import support as s


class GI39InterleavingsTest(unittest.TestCase):
    def protocol(self,case):
        row=next(r for r in s.plan()['proposed_tests'] if r['id']==case)
        with s.Scenario(row) as v:
            expected=dict(case=v.case,path=v.path,actor='primary',role='REMOTE',operation='EXECUTE',mode='CREATE',stage='PROJECTION',point='before_object',run_id=v.lab.run_id,client_store_id=v.lab.client_id,remote_store_id=v.lab.remote_id,cid=s.uid(),ticket=s.uid(),request_sha256='1'*64,expected=None,manifest_id='2'*64,manifest_sha256='2'*64,send_id=s.uid(),args_sha256='3'*64)
            good=dict(event='READY',inside_real_call=True,**expected);s.validate_gate(good,expected)
            for key in expected:
                with self.assertRaisesRegex(AssertionError,'GATE_'):s.validate_gate(dict(good,**{key:'WRONG'}),expected)
            with self.assertRaisesRegex(AssertionError,'NOT_IN_REAL_CALL'):s.validate_gate(dict(good,inside_real_call=False),expected)
            with self.assertRaisesRegex(AssertionError,'MISSING_READY'):s.validate_gate(dict(event='DONE'),expected)
            with self.assertRaisesRegex(AssertionError,'CONTROL_RELEASE'):s.check_release(dict(event='RELEASE',cid=s.uid()),expected)
            with self.assertRaisesRegex(AssertionError,'PROBE_NOT_HELD'):s.probe_locked(v.lab.root/'client')
            for target,code in [(s.H.normal_child,'MISSING_READY'),(s.H.empty_child,'CONTROL_EOF'),(s.H.held_child,'CONTROL_TIMEOUT')]:
                pair=s.start(target,(),dict(case=case,path=v.path,action='protocol_negative'));v.children.append(pair)
                try:
                    if target is s.H.held_child:
                        self.assertEqual(s.receive(pair[1])['event'],'READY')
                        with self.assertRaisesRegex(AssertionError,code):s.receive(pair[1],0.02)
                    elif target is s.H.empty_child:
                        with self.assertRaisesRegex(AssertionError,code):s.receive(pair[1])
                    else:
                        with self.assertRaisesRegex(AssertionError,code):s.validate_gate(s.receive(pair[1]),expected)
                    if target is not s.H.held_child:s.finish(*pair);self.assertEqual(pair[0].exitcode,0)
                    v.event('PROTOCOL_NEGATIVE',code=code)
                finally:s.stop_owned([pair])
            saved=v.lab.home/'own_saved';v.lab.root.rename(saved);v.lab.root.mkdir()
            try:s.expect_error('CLEANUP_OWNERSHIP',v.lab.close)
            finally:v.lab.root.rmdir();saved.rename(v.lab.root)
            p=v.lab.root/'owner.json';old=p.read_bytes();p.write_text('{}')
            try:s.expect_error('CLEANUP_MARKER',v.lab.close)
            finally:p.write_bytes(old)
            old=v.lab.sentinel.read_bytes();v.lab.sentinel.write_text('ALTERED')
            try:s.expect_error('SENTINEL_CHANGED',v.lab.close)
            finally:v.lab.sentinel.write_bytes(old)
            link=v.lab.root/'client'/'own_link';link.symlink_to(v.lab.sentinel)
            try:s.expect_error('CLEANUP_SYMLINK',v.lab.close)
            finally:link.unlink()
            v.passive();v.event('OWNERSHIP_RESTORED',positive_crash=False)
    def head(self,values):return {k:values['client']['head'][k] for k in ('seq','commit_sha256')}
    def stable_domain(self,state):return {k:v for k,v in state.items() if k not in ('receipts','sends','pending')}
    def mutation(self,v,before,after,event):
        b=before['client']['state'];a=after['client']['state'];mid=v.row['mutation_id'];steps=event['value']
        self.assertEqual(len(steps),len(v.steps));self.assertEqual(after['client']['head']['seq'],before['client']['head']['seq']+len(steps));self.assertEqual(after['remote'],before['remote'])
        for step in steps:
            cmd=step['command'];r=step['receipt'];self.assertEqual(r['command_id'],cmd['cid']);self.assertEqual(r['request_sha256'],cmd['request_sha256']);self.assertEqual(a['receipts'][cmd['cid']],{k:x for k,x in r.items() if k!='historical'});self.assertFalse(r['historical'])
        allowed={'receipts'}
        if mid=='S01':
            allowed|={'sources','selected_source','selection_generation'};self.assertNotEqual(a['selected_source'],b['selected_source']);self.assertEqual(a['selection_generation'],b['selection_generation']+1)
            self.assertEqual(a['sources'][a['selected_source']]['pin'],v.steps[0]['args']['pin']);self.assertEqual(a['sources'][a['selected_source']]['capture'],v.steps[0]['args']['capture'])
            self.assertEqual({k:x for k,x in a['sources'].items() if k!=a['selected_source']},b['sources'])
        elif mid in ('S02','S03','S04','S06','S07'):
            allowed|={'reviews','review_count'};self.assertEqual(a['review_count'],b['review_count']+len(steps))
            args=v.steps[-1]['args'];r=a['reviews'][args['stage']+':'+args['manifest_id']];self.assertEqual((r['version'],r['decision']),(3,'ACCEPT') if mid=='S02' else (2,'REVOKE'))
        elif mid=='S05':allowed|={'selected_source','source_generation'};self.assertEqual(a['selected_source'],b['selected_source']);self.assertEqual(a['source_generation'],b['source_generation']+2)
        elif mid=='C01':allowed|={'profile','profile_generation'};self.assertEqual(a['profile'],b['profile']);self.assertEqual(a['profile_generation'],b['profile_generation']+2)
        elif mid=='C02':allowed|={'policy','policy_generation'};self.assertEqual(a['policy'],b['policy']);self.assertEqual(a['policy_generation'],b['policy_generation']+2)
        elif mid.startswith('C'):
            allowed.add('accounts');aid=v.ids['account'];aa=a['accounts'][aid];bb=b['accounts'][aid];self.assertEqual(aa['generation'],bb['generation']+len(steps));self.assertEqual(aa['observations'],bb['observations'])
            if mid=='C03':self.assertEqual(aa['selected'],bb['selected']);self.assertEqual(steps[0]['after']['accounts'][aid]['selected']!=steps[0]['before']['accounts'][aid]['selected'],True)
            elif mid=='C04':self.assertTrue(aa['revoked'])
            else:self.assertEqual(aa['adapter'],bb['adapter']);self.assertNotEqual(steps[0]['after']['accounts'][aid]['adapter_sha256'],steps[0]['before']['accounts'][aid]['adapter_sha256'])
            expected_account=copy.deepcopy(bb);expected_account['generation']+=len(steps)
            if mid=='C04':expected_account['revoked']=True
            self.assertEqual(a['accounts'],dict(b['accounts'],**{aid:expected_account}))
        else:
            allowed|={'data','data_generation'};expected=copy.deepcopy(b['data']);cmd=v.steps[0]
            if cmd['kind']=='EDIT_ENTITY':
                item=expected['entities'][cmd['args']['entity_id']];item.update(cmd['args']['changes']);item['row_version']+=1
            else:expected['relations'][s.digest(cmd['args']['relation'])]=cmd['args']['relation']
            self.assertEqual(a['data'],expected);self.assertNotEqual(s.digest(a['data']),s.digest(b['data']));self.assertEqual(a['data_generation'],b['data_generation']+1)
        self.assertEqual({k:v for k,v in a.items() if k not in allowed},{k:v for k,v in b.items() if k not in allowed})
        self.assertEqual(event['transport']['execute'],0);self.assertEqual(event['transport']['lookup'],0)
        v.record.setdefault('mutation_receipts',[]).extend(dict(cid=x['command']['cid'],request_sha256=x['command']['request_sha256'],seq=x['receipt']['seq']) for x in steps)
    def gate(self,v,pair,job,cmd=None):
        e=s.receive(pair[1]);self.assertTrue(pair[0].is_alive());self.assertFalse(pair[1].poll(0))
        at=v.observe('primary_gate');remote=job['role']=='REMOTE'
        if remote:
            send=at['client']['state']['sends'][v.sid];ticket=send['attempts'][-1];self.assertEqual((send['status'],send['ledger_version'],send['queries']),('UNKNOWN',1,0));v.ticket=ticket
            command=s.C.remote_command(v.value,ticket,v.manifest,False)
        else:command=cmd;ticket=cmd['args'].get('ticket')
        identity=dict(case=v.case,path=v.path,actor='primary',role=job['role'],operation=command['kind'],mode=v.manifest['operation'] if remote else 'LOCAL',stage='PROJECTION' if remote else job['stage'],point=job['point'],
            run_id=v.lab.run_id,client_store_id=v.lab.client_id,remote_store_id=v.lab.remote_id,cid=command['cid'],request_sha256=s.digest({k:command[k] for k in ('kind','args','expected')}),args_sha256=s.digest(command['args']),expected=command['expected'],
            manifest_id=v.mid if remote else cmd['args'].get('manifest_id'),manifest_sha256=s.digest(v.manifest) if remote else cmd['args'].get('manifest_id'),send_id=v.sid if remote else cmd['args'].get('send_id'),ticket=ticket)
        s.validate_gate(e,identity);self.assertEqual((e['transport']['execute'],e['transport']['lookup']),(int(remote),0));self.assertIsNone(e['transport']['proof_sha256'])
        v.event('READY',**{k:x for k,x in e.items() if k not in ('event','case','path')});v.record['primary_identity']=identity
        return at,identity
    def release(self,v,pair,identity):
        s.release(pair[1],identity);v.event('RELEASE_ACK',cid=identity['cid'],ticket=identity.get('ticket'))
    def fresh_negative(self,v,cmd,error):
        current=v.observe('before_fresh_negative');fresh=dict(cmd,cid=s.uid(),expected=self.head(current));e=v.run(dict(action='perform',actor='fresh_negative',command=fresh),error)
        self.assertEqual(v.observe('after_fresh_negative'),current);self.assertNotIn(fresh['cid'],current['client']['state']['receipts']);self.assertEqual(e['transport']['execute'],0)
    def local(self,v):
        row=v.row;issue=row['family']=='BEFORE_ISSUE'
        if issue:kind='ISSUE';args=dict(manifest_id=v.mid,review_version=1,send_id=v.sid,ticket=s.uid(),capabilities=v.manifest['capabilities'],retry=False)
        else:kind='APPLY' if v.path=='T' else 'APPLY_BATCH';args=dict(manifest_id=v.ids['effect' if v.path=='T' else 'batch'],review_version=1)
        cmd=dict(kind=kind,args=args,cid=s.uid(),expected=self.head(v.before));job=dict(action='perform',actor='primary',role='CLIENT',gate=True,point=row['point'],stage='PROJECTION' if issue else 'EFFECT' if v.path=='T' else 'BATCH',command=cmd)
        mutation_job=v.mutate_job(self.head(v.before),contender=row['order']=='COMMIT_FIRST');pair=v.spawn(job)
        try:
            at,identity=self.gate(v,pair,job,cmd)
            if row['order']=='COMMIT_FIRST':
                contender=v.spawn(mutation_job)
                try:
                    prepared=s.receive(contender[1]);self.assertEqual(prepared,dict(event='PREPARED',case=v.case,actor='mutator',cid=v.steps[0]['cid'],expected=self.head(v.before)));v.event('PREPARED',actor='mutator',cid=v.steps[0]['cid'],expected=prepared['expected'])
                    probe=s.receive(contender[1]);self.assertEqual(probe,dict(event='LOCK_HELD_OBSERVED',case=v.case,actor='mutator',cid=v.steps[0]['cid']));v.event('LOCK_HELD_OBSERVED',actor='mutator',cid=v.steps[0]['cid'])
                    self.release(v,pair,identity);done=v.done(pair,job);committed=v.observe('primary_committed');receipt=done['value'];self.assertEqual(committed['client']['state']['receipts'][cmd['cid']],{k:x for k,x in receipt.items() if k!='historical'})
                    self.assertEqual(committed['client']['head']['seq'],v.before['client']['head']['seq']+1)
                    self.release(v,contender,dict(cid=v.steps[0]['cid']));v.done(contender,mutation_job,'CONFLICT_HEAD');self.assertEqual(v.observe('contender_lost'),committed)
                finally:s.stop_owned([contender])
                mutation_job=v.mutate_job(self.head(committed));mutation_job['steps']=[dict(x,cid=s.uid()) for x in mutation_job['steps']]
                changed=v.run(mutation_job);after=v.observe('fresh_mutation_committed');self.mutation(v,committed,after,changed)
                self.assertEqual(after['client']['state']['receipts'][cmd['cid']],committed['client']['state']['receipts'][cmd['cid']])
                for key in ('tasks','bases','mappings','provenance') if v.path=='T' else ('data',):self.assertEqual(after['client']['state'][key],committed['client']['state'][key])
                pj=dict(action='project_old',actor='old_package_guard',bid=v.bid,tid=v.tid)
                if v.path=='R':pj.update(batch_cid=receipt['command_id'],batch_request=receipt['request_sha256'])
                v.run(pj,row['expected_semantic_error']);final=v.observe('old_preparation_blocked');self.assertEqual(final['client']['state']['sends'],{});self.assertEqual(final['remote'],v.before['remote'])
            else:
                changed=v.run(mutation_job);after=v.observe('mutation_committed');self.mutation(v,v.before,after,changed);self.assertTrue(pair[0].is_alive());self.assertFalse(pair[1].poll(0))
                self.release(v,pair,identity);v.done(pair,job,'CONFLICT_HEAD');self.assertEqual(v.observe('primary_lost_head'),after)
                self.fresh_negative(v,cmd,row['expected_semantic_error'])
                if not issue:self.assertEqual(after['client']['state'].get('tasks',after['client']['state'].get('data',{})),v.before['client']['state'].get('tasks',v.before['client']['state'].get('data',{})))
                self.assertEqual(after['client']['state']['sends'],{});self.assertEqual(after['remote'],v.before['remote'])
        finally:s.stop_owned([pair])
        v.passive();v.passive()
    def send(self,v,values,status,ledger,queries):
        a=values['client']['state'];send=a['sends'][v.sid];self.assertEqual((send['status'],send['ledger_version'],send['queries']),(status,ledger,queries));self.assertEqual(send['attempts'],[v.ticket]);self.assertFalse(send['hard_conflict']);return send
    def stale(self,v,status):
        out=v.run(dict(action='summary'))['value'];row=next(x for x in out['sends'] if x['send_id']==v.sid);self.assertEqual((row['status'],row['validity'],row['attempts']),(status,'STALE',1))
    def reject(self,v):
        for sid,retry in [(s.uid(),False),(v.sid,True)]:
            before=v.observe('before_old_dispatch');e=v.run(dict(action='dispatch',actor='old_dispatch',mid=v.mid,sid=sid,retry=retry),v.row['expected_package_error']);self.assertEqual(v.observe('after_old_dispatch'),before);self.assertEqual(e['transport']['execute'],0)
    def inflight(self,v):
        row=v.row;job=dict(action='dispatch',actor='primary',role='REMOTE',gate=True,point=row['point'],mid=v.mid,sid=v.sid,lose_response=row['lose_response']);pair=v.spawn(job)
        try:
            gate,identity=self.gate(v,pair,job);self.assertEqual(gate['client']['head']['seq'],v.before['client']['head']['seq']+1)
            if row['point']=='before_object':self.assertEqual(gate['remote'],v.before['remote'])
            else:self.effect(v,gate['remote'],v.ticket,identity)
            changed=v.run(v.mutate_job(self.head(gate)));after=v.observe('mutation_committed');self.mutation(v,gate,after,changed);self.send(v,after,'UNKNOWN',1,0)
            self.assertTrue(pair[0].is_alive());self.assertFalse(pair[1].poll(0));self.release(v,pair,identity);done=v.done(pair,job)
        finally:s.stop_owned([pair])
        values=v.observe('dispatch_complete');proof=self.effect(v,values['remote'],v.ticket,identity);self.assertEqual(done['transport']['proof_sha256'],s.digest(proof));self.assertEqual((done['transport']['execute'],done['transport']['lookup']),(1,0))
        lose=row['lose_response'];self.assertEqual(done['transport']['failure_phase'],'LOSS_AFTER_REAL_COMMIT' if lose else None)
        send=self.send(v,values,'UNKNOWN' if lose else 'EFFECT_CONFIRMED',2,0);self.assertEqual(send['proof'],None if lose else proof);self.assertEqual(values['client']['state']['pending'],{})
        self.assertEqual(self.stable_domain(values['client']['state']),self.stable_domain(after['client']['state']));self.stale(v,send['status']);v.passive();self.reject(v)
        if lose:
            e=v.run(dict(action='reconcile',actor='explicit_reconcile',sid=v.sid));self.assertEqual((e['transport']['execute'],e['transport']['lookup']),(0,1));final=v.observe('explicit_reconcile_complete');self.assertEqual(final['remote'],values['remote']);self.send(v,final,'EFFECT_CONFIRMED',3,1);self.stale(v,'EFFECT_CONFIRMED');self.reject(v)
        v.passive()
    def domain(self,case):
        row=next(r for r in s.plan()['proposed_tests'] if r['id']==case)
        with s.Scenario(row) as v:
            v.prepare()
            if row['family'] in ('LOCAL_APPLY','BEFORE_ISSUE'):self.local(v)
            else:self.inflight(v)
            v.record['causal_order_verified']=True

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
            self.assertEqual(sum(r['UI_part']!='CONTROL' for r in s.plan()['proposed_tests']),86)
            self.assertEqual(len(s.plan()['mutation_catalog']),22)
            v.passive();v.event('INVENTORY_NEGATIVES',maps_raw_inputs_budgets_verified=True)

    def test_GX01(self):self.domain('GX01')

    def test_GX02(self):self.domain('GX02')

    def test_GX03(self):self.domain('GX03')

    def test_GX04(self):self.domain('GX04')

    def test_GX05(self):self.domain('GX05')

    def test_GX06(self):self.domain('GX06')

    def test_GX07(self):self.domain('GX07')

    def test_GX08(self):self.domain('GX08')

    def test_GX09(self):self.domain('GX09')

    def test_GX10(self):self.domain('GX10')

    def test_GX11(self):self.domain('GX11')

    def test_GX12(self):self.domain('GX12')

    def test_GX13(self):self.domain('GX13')

    def test_GX14(self):self.domain('GX14')

    def test_GX15(self):self.domain('GX15')

    def test_GX16(self):self.domain('GX16')

    def test_GX17(self):self.domain('GX17')

    def test_GX18(self):self.domain('GX18')

    def test_GX19(self):self.domain('GX19')

    def test_GX20(self):self.domain('GX20')

    def test_GX21(self):self.domain('GX21')

    def test_GX22(self):self.domain('GX22')

    def test_GX23(self):self.domain('GX23')

    def test_GX24(self):self.domain('GX24')

    def test_GX25(self):self.domain('GX25')

    def test_GX26(self):self.domain('GX26')

    def test_GX27(self):self.domain('GX27')

    def test_GX28(self):self.domain('GX28')

    def test_GX29(self):self.domain('GX29')

    def test_GX30(self):self.domain('GX30')

    def test_GX31(self):self.domain('GX31')

    def test_GX32(self):self.domain('GX32')

    def test_GX33(self):self.domain('GX33')

    def test_GX34(self):self.domain('GX34')

    def test_GX35(self):self.domain('GX35')

    def test_GX36(self):self.domain('GX36')

    def test_GX37(self):self.domain('GX37')

    def test_GX38(self):self.domain('GX38')

    def test_GX39(self):self.domain('GX39')

    def test_GX40(self):self.domain('GX40')

    def test_GX41(self):self.domain('GX41')

    def test_GX42(self):self.domain('GX42')

    def test_GX43(self):self.domain('GX43')

    def test_GX44(self):self.domain('GX44')

    def test_GX45(self):self.domain('GX45')

    def test_GX46(self):self.domain('GX46')

    def test_GX47(self):self.domain('GX47')

    def test_GX48(self):self.domain('GX48')

    def test_GX49(self):self.domain('GX49')

    def test_GX50(self):self.domain('GX50')

    def test_GX51(self):self.domain('GX51')

    def test_GX52(self):self.domain('GX52')

    def test_GX53(self):self.domain('GX53')

    def test_GX54(self):self.domain('GX54')

    def test_GX55(self):self.domain('GX55')

    def test_GX56(self):self.domain('GX56')

    def test_GX57(self):self.domain('GX57')

    def test_GX58(self):self.domain('GX58')

    def test_GX59(self):self.domain('GX59')

    def test_GX60(self):self.domain('GX60')

    def test_GX61(self):self.domain('GX61')

    def test_GX62(self):self.domain('GX62')

    def test_GX63(self):self.domain('GX63')

    def test_GX64(self):self.domain('GX64')

    def test_GX65(self):self.domain('GX65')

    def test_GX66(self):self.domain('GX66')

    def test_GX67(self):self.domain('GX67')

    def test_GX68(self):self.domain('GX68')

    def test_GX69(self):self.domain('GX69')

    def test_GX70(self):self.domain('GX70')

    def test_GX71(self):self.domain('GX71')

    def test_GX72(self):self.domain('GX72')

    def test_GX73(self):self.domain('GX73')

    def test_GX74(self):self.domain('GX74')

    def test_GX75(self):self.domain('GX75')

    def test_GX76(self):self.domain('GX76')

    def test_GX77(self):self.domain('GX77')

    def test_GX78(self):self.domain('GX78')

    def test_GX79(self):self.domain('GX79')

    def test_GX80(self):self.domain('GX80')

    def test_GX81(self):self.domain('GX81')

    def test_GX82(self):self.domain('GX82')

    def test_GX83(self):self.domain('GX83')

    def test_GX84(self):self.domain('GX84')

    def test_GX85(self):self.domain('GX85')

    def test_GX86(self):self.domain('GX86')

    def test_GX87(self):self.protocol('GX87')

    def test_GX88(self):self.protocol('GX88')

    def test_GX89(self):self.inventory('GX89')

    def test_GX90(self):self.inventory('GX90')
