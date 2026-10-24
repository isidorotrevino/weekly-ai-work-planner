# SPDX-License-Identifier: GPL-3.0-only
"""I45 IC obligations, with issued provenance separate from REMOTE negatives."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
import uuid

from testing.durable_issue_create import support as s


def static_domain(state):
    return {k:v for k,v in state.items() if k not in ('receipts','sends','pending')}


class IssueCreateTest(unittest.TestCase):
    def scenario(self,case,path,exercise):
        v=s.Scenario(case,path);success=False
        try:
            exercise(v);v.passive();success=True
        finally:v.close(success)

    def assert_unknown(self,state,sid,ticket):
        self.assertEqual(set(state['sends']),{sid});send=state['sends'][sid]
        self.assertEqual((send['status'],send['ledger_version'],send['proof'],send['queries']),('UNKNOWN',1,None,0))
        self.assertEqual(send['attempts'],[ticket]);self.assertFalse(send['hard_conflict'])
        self.assertEqual(state['pending'],{'send:'+ticket:dict(send_id=sid)})
        self.assertEqual(send['events'],[dict(type='ISSUED',ticket=ticket)])

    def assert_effect(self,v,remote,ticket,proof):
        self.assertEqual(proof['status'],'EFFECT_CONFIRMED');self.assertEqual(proof['code'],'CONFIRMED')
        self.assertEqual(proof['schema'],'d5.durable-remote-proof.v1' if v.path=='T' else 'd5.relational-remote-proof.v1')
        self.assertEqual((proof['run_id'],proof['store_id'],proof['ticket']),(v.lab.run_id,v.lab.remote_id,ticket))
        self.assertEqual(proof['request_hash'],s.digest(v.manifest));self.assertEqual(proof['manifest_hash'],s.digest(v.manifest))
        self.assertEqual(proof['creation_key'],v.manifest['creation_key'])
        self.assertEqual(proof,remote['state']['tickets'][ticket])
        rid=str(uuid.uuid5(uuid.UUID(v.lab.remote_id),v.manifest['creation_key']))
        self.assertEqual(proof['remote_id'],rid)
        self.assertEqual(set(remote['state']['entities']),{rid})
        entity=remote['state']['entities'][rid]
        self.assertEqual(entity,dict(id=rid,version=1,payload=v.manifest['payload'],foreign={}))
        self.assertEqual(proof['applied_version'],1);self.assertEqual(proof['payload_hash'],s.digest(entity['payload']))
        self.assertEqual(remote['state']['keys'],{v.manifest['creation_key']:rid})

    def explicit_reconcile(self,v,sid,proof):
        before=v.observe('before_explicit_reconcile')
        event=v.run_job(dict(action='reconcile',role='CLIENT',operation='QUERY/RESULT',mode='CREATE',stage='PROJECTION',sid=sid),'explicit_reconcile',round=3)
        self.assertEqual(event['transport'],dict(lookup=1,execute=0))
        values=v.observe('after_explicit_reconcile');state=values['client']['state'];send=state['sends'][sid]
        self.assertEqual((send['status'],send['ledger_version'],send['queries']),('EFFECT_CONFIRMED',2,1))
        self.assertEqual(send['proof'],proof);self.assertFalse(state['pending'])
        self.assertEqual(static_domain(state),static_domain(before['client']['state']))
        self.assertEqual(values['remote'],before['remote'])
        v.event('EXPLICIT_RECONCILE',role='CLIENT',operation='QUERY/RESULT',mode='CREATE',stage='PROJECTION',round=3,ledger_version=2,proof_sha256=s.digest(proof),execute_calls=0)
        return values

    def client_competition(self,case,path,family,winner):
        def exercise(v):
            v.prepare();cid,sid,ticket=s.uid(),s.uid(),s.uid()
            a=v.issue_job(cid,sid,ticket)
            if family=='C1':b=deepcopy(a)
            elif family=='C2':b=v.issue_job(s.uid(),s.uid(),s.uid())
            elif family=='C3':b=v.issue_job(s.uid(),sid,ticket)
            else:b=v.issue_job(cid,sid,s.uid())
            jobs=[a,b];out=v.race(jobs,winner)
            self.assertEqual(out[winner]['status'],'OK');self.assertFalse(out[winner]['value']['historical'])
            loser=1-winner
            if family=='C1':
                self.assertEqual(out[loser]['status'],'OK');self.assertTrue(out[loser]['value']['historical'])
                self.assertEqual({k:x for k,x in out[winner]['value'].items() if k!='historical'},{k:x for k,x in out[loser]['value'].items() if k!='historical'})
            else:self.assertEqual(out[loser]['code'],'COMMAND_CONFLICT' if family=='C4' else 'CONFLICT_HEAD')
            values=v.observe('issue_round_1');state=values['client']['state'];win=jobs[winner];args=win['command']['args']
            self.assertEqual(values['client']['head']['seq'],v.before['client']['head']['seq']+1)
            self.assertEqual(len(state['receipts']),len(v.before['client']['state']['receipts'])+1)
            self.assertEqual(state['receipts'][win['cid']]['request_sha256'],win['request_hash'])
            self.assertEqual(static_domain(state),static_domain(v.before['client']['state']))
            self.assert_unknown(state,args['send_id'],args['ticket']);self.assertEqual(values['remote'],v.before['remote'])
            v.record['issued_ticket']=dict(ticket=args['ticket'],send_id=args['send_id'],cid=win['cid'],request_sha256=win['request_hash'],origin='ISSUED_BY_CLIENT')
            if family in ('C2','C3'):
                fresh={k:values['client']['head'][k] for k in ('seq','commit_sha256')};old=jobs[loser];oa=old['command']['args']
                updated=v.issue_job(old['cid'],oa['send_id'],oa['ticket'],fresh)
                self.assertNotEqual(updated['request_hash'],old['request_hash'])
                v.run_job(updated,'fresh_head_loser',expected_error='BINDING_UNRESOLVED')
                self.assertEqual(v.observe('binding_rejection'),values)
                v.event('FRESH_HEAD_REJECTION',role='CLIENT',operation='ISSUE',mode='CREATE',stage='PROJECTION',round=2,code='BINDING_UNRESOLVED',old_request_sha256=old['request_hash'],new_request_sha256=updated['request_hash'])
            elif family=='C4':
                v.run_job(jobs[loser],'incompatible_same_cid',expected_error='COMMAND_CONFLICT')
                self.assertEqual(v.observe('command_collision_repeated'),values)
            executed=v.run_job(v.execute_job(args['ticket']),'execute_issued_winner',round=3)
            self.assertEqual(executed['transport'],dict(lookup=0,execute=1));proof=executed['value']
            remote=v.observe('issued_effect')['remote'];self.assert_effect(v,remote,args['ticket'],proof)
            self.assertEqual(len(remote['state']['tickets']),1);self.assertEqual(remote['head']['seq'],1)
            reconciled=self.explicit_reconcile(v,args['send_id'],proof)
            replay=v.run_job(win,'old_issue_receipt_only',round=4)['value']
            self.assertTrue(replay['historical']);self.assertEqual(replay['result']['outcome'],'UNKNOWN')
            self.assertEqual(replay,dict(state['receipts'][win['cid']],historical=True))
            self.assertEqual(v.observe('after_old_issue_history'),reconciled)
            self.assertFalse(replay['grants_execution_authority']);self.assertEqual(replay['reservations_created'],0)
            v.event('OLD_RECEIPT_NO_REWIND',role='CLIENT',operation='ISSUE',mode='CREATE',stage='PROJECTION',round=4,receipt_outcome='UNKNOWN',current_status='EFFECT_CONFIRMED',current_ledger=2,cid=win['cid'])
        self.scenario(case,path,exercise)

    def issued_setup(self,v):
        v.prepare();job=v.issue_job(s.uid(),s.uid(),s.uid())
        event=v.run_job(job,'setup_issue');self.assertFalse(event['value']['historical'])
        args=job['command']['args'];v.issued=job;v.sid=args['send_id'];v.ticket=args['ticket']
        v.record['issued_ticket']=dict(ticket=v.ticket,send_id=v.sid,cid=job['cid'],request_sha256=job['request_hash'],origin='ISSUED_BY_CLIENT')
        baseline=v.observe('one_issue_no_remote')
        self.assert_unknown(baseline['client']['state'],v.sid,v.ticket)
        self.assertFalse(baseline['remote']['state']['tickets'] or baseline['remote']['state']['entities'])
        return baseline

    def remote_competition(self,case,path,extra,winner):
        def exercise(v):
            baseline=self.issued_setup(v);other=s.uid() if extra else v.ticket
            jobs=[v.execute_job(v.ticket),v.execute_job(other)]
            v.record['ticket_provenance']={v.ticket:'ISSUED_BY_CLIENT'}
            if extra:v.record['ticket_provenance'][other]='NOT_ISSUED_BY_CLIENT'
            v.record['integrated_claim_allowed']=not extra;v.record['reconcile_performed']=False
            out=v.race(jobs,winner,second_commit=extra)
            self.assertTrue(all(e['status']=='OK' for e in out));self.assertTrue(all(e['transport']==dict(lookup=0,execute=1) for e in out))
            values=v.observe('remote_round_1');remote=values['remote'];loser=1-winner;count=2 if extra else 1
            self.assertEqual(values['client'],baseline['client'])
            self.assertEqual(remote['head']['seq'],baseline['remote']['head']['seq']+count)
            self.assertEqual(len(remote['state']['receipts']),len(baseline['remote']['state']['receipts'])+count)
            self.assertEqual(len(remote['state']['tickets']),count)
            self.assert_effect(v,remote,jobs[winner]['ticket'],out[winner]['value'])
            for job,event in zip(jobs,out):
                self.assertEqual(remote['state']['tickets'][job['ticket']],event['value'])
                self.assertEqual(remote['state']['receipts'][job['cid']]['request_sha256'],job['request_hash'])
            if extra:
                proof=out[loser]['value']
                self.assertEqual((proof['status'],proof['code'],proof['retry_tick']),('NO_EFFECT','CREATION_KEY_CONFLICT',None))
                self.assertEqual(proof['ticket'],jobs[loser]['ticket']);self.assertEqual(proof['request_hash'],s.digest(v.manifest))
                self.assertEqual(proof['schema'],'d5.durable-remote-proof.v1' if path=='T' else 'd5.relational-remote-proof.v1')
                self.assertEqual((proof['run_id'],proof['store_id'],proof['creation_key'],proof['manifest_hash']),(v.lab.run_id,v.lab.remote_id,v.manifest['creation_key'],s.digest(v.manifest)))
                self.assertTrue(all(proof[k] is None for k in ('remote_id','applied_version','payload_hash')))
                self.assert_unknown(values['client']['state'],v.sid,v.ticket)
                v.record['winning_ticket_origin']=v.record['ticket_provenance'][jobs[winner]['ticket']]
                v.event('REMOTE_ONLY_NO_RECONCILE',role='REMOTE',operation='EXECUTE',mode='CREATE',stage='PROJECTION',ticket_origin=v.record['winning_ticket_origin'],client_ledger=1,client_status='UNKNOWN',integrated_claim_allowed=False)
            else:
                self.assertEqual(out[0]['value'],out[1]['value'])
                read=dict(role='REMOTE',cid=jobs[0]['cid'],request_hash=jobs[0]['request_hash'])
                public=v.passive([read]);self.assertEqual(public['reads'][0],dict(remote['state']['receipts'][jobs[0]['cid']],historical=True))
                self.explicit_reconcile(v,v.sid,out[0]['value']);v.record['reconcile_performed']=True
        self.scenario(case,path,exercise)

    def mutated_manifest(self,case,path):
        def exercise(v):
            self.issued_setup(v)
            proof=v.run_job(v.execute_job(v.ticket),'valid_create_first')['value']
            before=v.observe('valid_create_committed');self.assert_effect(v,before['remote'],v.ticket,proof)
            bad=deepcopy(v.manifest);bad['task']['title']='Synthetic altered request';bad['payload']['name']=bad['task']['title']
            self.assertNotEqual(s.digest(bad),s.digest(v.manifest))
            job=v.execute_job(v.ticket,bad)
            event=v.run_job(job,'unreviewed_mutation_negative',expected_error='TICKET_CONFLICT')
            self.assertEqual(event['transport'],dict(lookup=0,execute=1))
            self.assertEqual(v.observe('ticket_conflict_no_change'),before)
            v.event('SERIAL_MUTATION_REJECTED',role='REMOTE',operation='EXECUTE',mode='CREATE',stage='PROJECTION',code='TICKET_CONFLICT',mutant_reviewed=False,original_manifest_sha256=s.digest(v.manifest),mutant_manifest_sha256=s.digest(bad))
        self.scenario(case,path,exercise)

    def wrong_identity(self,case,path):
        def exercise(v):
            before=self.issued_setup(v);bad=deepcopy(v.manifest);bad['creation_key']='0'*64
            self.assertNotEqual(bad['creation_key'],v.manifest['creation_key'])
            v.run_job(v.execute_job(v.ticket,bad),'bad_key_negative',expected_error='REMOTE_SCOPE')
            self.assertEqual(v.observe('scope_error_no_effect'),before)
            read=dict(action='read_command',role='CLIENT',operation='READ_COMMAND',mode='CREATE',stage='PROJECTION',cid=v.issued['cid'],request_hash='0'*64)
            self.assertNotEqual(read['request_hash'],v.issued['request_hash'])
            v.run_job(read,'bad_request_hash',expected_error='COMMAND_CONFLICT')
            good=v.run_job(dict(read,request_hash=v.issued['request_hash']),'exact_request_hash')['value']
            self.assertTrue(good['historical']);self.assertEqual(good['result']['outcome'],'UNKNOWN');self.assertFalse(good['grants_execution_authority'])
            self.assertEqual(v.observe('read_no_mutation'),before)
            v.event('IDENTITY_NEGATIVES',role='REMOTE',operation='EXECUTE/READ_COMMAND',mode='CREATE',stage='PROJECTION',scope_and_request_rejected=True)
        self.scenario(case,path,exercise)

    def test_IC25(self):self.mutated_manifest('IC25','T')
    def test_IC26(self):self.mutated_manifest('IC26','R')
    def test_IC27(self):self.wrong_identity('IC27','T')
    def test_IC28(self):self.wrong_identity('IC28','R')

    def test_IC29(self):
        for path in ('T','R'):
            def exercise(v):
                v.prepare();job=v.issue_job(s.uid(),s.uid(),s.uid());event=dict(event='READY',**{k:job[k] for k in ('role','operation','mode','stage','cid','request_hash')})
                s.validate_gate(event,job,'READY')
                with self.assertRaisesRegex(AssertionError,'WRONG_GATE'):s.validate_gate(dict(event,event='DONE'),job,'READY')
                with self.assertRaisesRegex(AssertionError,'GATE_IDENTITY'):s.validate_gate(dict(event,cid=s.uid()),job,'READY')
                with self.assertRaisesRegex(AssertionError,'PROBE_NOT_HELD'):s.probe_locked(v.lab.root/'client')
                for target,label in [(s.held_child,'REDUCED_TIMEOUT'),(s.normal_child,'NORMAL_EXIT'),(s.empty_child,'EOF')]:
                    pair=s.start(target,(),dict(case='IC29',path=path,actor=label,action='negative_control'));v.children.append(pair)
                    try:
                        if label=='REDUCED_TIMEOUT':
                            self.assertEqual(s.receive(pair[1])['event'],'READY')
                            with self.assertRaisesRegex(AssertionError,'CONTROL_TIMEOUT'):s.receive(pair[1],timeout=0.02)
                        elif label=='NORMAL_EXIT':
                            message=s.receive(pair[1])
                            with self.assertRaisesRegex(AssertionError,'WRONG_GATE'):s.validate_gate(message,job,'READY')
                            s.finish(*pair)
                        else:
                            with self.assertRaisesRegex(AssertionError,'CONTROL_EOF'):s.receive(pair[1])
                            s.finish(*pair)
                    finally:s.stop_owned([pair])
                    v.event('NEGATIVE_PROTOCOL',point=label,reduced_timeout_seconds=0.02 if label=='REDUCED_TIMEOUT' else None,exitcode=pair[0].exitcode,counts_as_recovery=False)
                saved=v.lab.home/'own_saved_run';v.lab.root.rename(saved);v.lab.root.mkdir()
                try:s.expect_error('CLEANUP_OWNERSHIP',v.lab.close)
                finally:v.lab.root.rmdir();saved.rename(v.lab.root)
                owner=v.lab.root/'owner.json';raw=owner.read_bytes();owner.write_bytes(b'{}')
                try:s.expect_error('CLEANUP_MARKER',v.lab.close)
                finally:owner.write_bytes(raw)
                sentinel=v.lab.sentinel.read_bytes();v.lab.sentinel.write_bytes(b'SYNTHETIC_ALTERED')
                try:s.expect_error('SENTINEL_CHANGED',v.lab.close)
                finally:v.lab.sentinel.write_bytes(sentinel)
                link=v.lab.root/'client'/'own_control_link';link.symlink_to(v.lab.sentinel)
                try:s.expect_error('CLEANUP_SYMLINK',v.lab.close)
                finally:link.unlink()
                self.assertEqual(v.lab.sentinel.read_bytes(),sentinel)
                v.event('OWNERSHIP_NEGATIVES',operation='CLEANUP',inode_marker_sentinel_link_rejected=True)
            self.scenario('IC29',path,exercise)

    def test_IC30(self):
        def exercise(v):
            with tempfile.TemporaryDirectory(prefix='d5-i46-inventory-') as directory:
                s.EXTRA_ROOTS.append(directory);path=Path(directory)/'synthetic-input';path.write_text('synthetic-a')
                before=s.hash_inputs([path]);s.validate_inventory(before,s.hash_inputs([path]));path.write_text('synthetic-b')
                with self.assertRaisesRegex(AssertionError,'STALE_INPUTS'):s.validate_inventory(before,s.hash_inputs([path]))
                extra=Path(directory)/'added-input';extra.write_text('synthetic-added')
                with self.assertRaisesRegex(AssertionError,'STALE_INPUTS'):s.validate_inventory(before,s.hash_inputs([path,extra]))
                raw=Path(directory)/'synthetic-raw.json'
                with self.assertRaisesRegex(AssertionError,'RAW_MISSING_OR_TYPE'):s.raw_binding(raw)
                raw.write_text('{')
                with self.assertRaisesRegex(AssertionError,'RAW_INCOMPATIBLE'):s.raw_binding(raw)
                raw.write_text(json.dumps(dict(status='PASS',passed=['synthetic.test'],tests_run=1)));self.assertEqual(s.raw_binding(raw)['tests_run'],1)
                with self.assertRaisesRegex(AssertionError,'RAW_HASH_MISMATCH'):s.raw_binding(raw,'0'*64)
                raw.write_text(json.dumps(dict(status='PASS',passed=['synthetic.test']*2,tests_run=2)))
                with self.assertRaisesRegex(AssertionError,'RAW_COUNTS'):s.raw_binding(raw)
                with self.assertRaisesRegex(AssertionError,'RAW_BUDGET'):s.raw_binding(raw,maximum=1)
            with self.assertRaisesRegex(AssertionError,'EVENT_SIZE_BUDGET'):v.event('OVERSIZED',synthetic='x'*(s.MAX_EVENT_BYTES+1))
            limit=s.MAX_EVENTS
            try:
                s.MAX_EVENTS=len(v.events)
                with self.assertRaisesRegex(AssertionError,'EVENT_BUDGET'):v.event('OVER_COUNT')
            finally:s.MAX_EVENTS=limit
            with self.assertRaisesRegex(AssertionError,'RAW_BUDGET'):s.bounded_raw(dict(synthetic='x'*128),maximum=64)
            design=json.loads(Path('docs/validation/D5-I45-design-review.json').read_text())
            methods=unittest.defaultTestLoader.getTestCaseNames(type(self));expected=['test_'+r['id'] for r in design['rows']]
            self.assertEqual(methods,expected);s.validate_report(methods,expected,[],0)
            for passed,skipped,remaining,code in [(methods+methods[:1],[],0,'DUPLICATE_TEST_IDS'),(methods[:-1],[],0,'INCOMPLETE_CAMPAIGN'),(methods,['skip'],0,'INCOMPLETE_CAMPAIGN'),(methods,[],1,'RESOURCES_REMAINING')]:
                with self.assertRaisesRegex(AssertionError,code):s.validate_report(passed,expected,skipped,remaining)
            self.assertFalse(design['D5_closed'] or design['publication_authorized']);self.assertEqual(len(design['global_gaps_open']),7)
            self.assertFalse(design['remote_negative_extra_ticket']['integrated_claim_allowed'])
            v.event('EVIDENCE_NEGATIVES',operation='INVENTORY/REPORT',inputs_raw_counts_limits_rejected=True,remote_extra_ticket_isolated=True)
        self.scenario('IC30','R',exercise)


def client_test(number,path,family,winner):
    def test(self):self.client_competition(f'IC{number:02}',path,family,winner)
    test.__name__=f'test_IC{number:02}';return test


def remote_test(number,path,extra,winner):
    def test(self):self.remote_competition(f'IC{number:02}',path,extra,winner)
    test.__name__=f'test_IC{number:02}';return test


_number=0
for _family in ('C1','C2','C3','C4'):
    for _path in ('T','R'):
        for _winner in (0,1):
            _number+=1;setattr(IssueCreateTest,f'test_IC{_number:02}',client_test(_number,_path,_family,_winner))
for _extra in (False,True):
    for _path in ('T','R'):
        for _winner in (0,1):
            _number+=1;setattr(IssueCreateTest,f'test_IC{_number:02}',remote_test(_number,_path,_extra,_winner))
