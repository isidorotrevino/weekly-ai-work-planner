# SPDX-License-Identifier: GPL-3.0-only
"""Explicit I43 HF obligations; no product or historical-test modifications."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import signal
import tempfile
import unittest

from testing.durable_crash_boundaries import support as s


class CrashBoundariesTest(unittest.TestCase):
    def scenario(self, case, path, exercise):
        v = s.Scenario(case, path)
        success = False
        try:
            exercise(v)
            v.final_reader()
            success = True
        finally:
            v.close(success)

    def assert_empty_effects(self, v, values):
        state = values['client']['state']
        self.assertEqual(state['data_generation'], 0)
        self.assertTrue(all(not value for value in state['data'].values()))
        self.assertIsNone(state['selection'])
        self.assertFalse(state['bindings'] or state['sends'] or state['pending'])
        self.assertFalse(values['remote']['state']['entities'] or values['remote']['state']['tickets'])
        self.assertFalse(any(m['stage']=='PROJECTION' for m in state['manifests'].values()))
        self.assertEqual(values['remote'], v.before['remote'])

    def assert_early_transition(self, v, index, values):
        before, after = v.before['client'], values['client']
        state = after['state']; receipt = state['receipts'][v.cmd['cid']]
        self.assertEqual(after['head']['seq'], before['head']['seq']+1)
        self.assertEqual(len(state['receipts']), len(before['state']['receipts'])+1)
        self.assertEqual(receipt['request_sha256'], v.read['request_hash'])
        self.assertFalse(receipt['grants_execution_authority'] or receipt['activation_allowed'])
        self.assertEqual(receipt['quota_consumed'], 0)
        self.assertEqual(receipt['reservations_created'], 0)
        self.assertEqual(set(state['sources']), {v.sid})
        import base64
        self.assertEqual(base64.b64decode(state['sources'][v.sid]['content_base64']), v.raw)
        self.assertEqual(state['source_generation'], 0 if index == 0 else 1)
        self.assertEqual(state['selected_source'], None if index == 0 else v.sid)
        self.assertEqual(len(state['manifests']), [0,0,1,1,2,2][index])
        self.assertEqual(state['review_count'], [0,0,0,1,1,2][index])
        if index == 0:
            self.assertEqual(receipt['result']['source_id'], hashlib.sha256(v.raw).hexdigest())
        if index == 1:
            self.assertEqual(receipt['result']['source_generation'], 1)
        if index == 2:
            mid = receipt['result']['manifest_id']
            expected = dict(schema='d5.relational-manifest.v1', stage='SOURCE', context=dict(source_id=v.sid, source_generation=1))
            self.assertEqual(state['manifests'][mid], expected)
            self.assertEqual(mid, s.digest(expected))
        if index in (3,5):
            mid = v.sm if index == 3 else v.bm
            self.assertEqual(state['reviews'][v.stage+':'+mid], dict(version=1, decision='ACCEPT', reason_code='SYNTHETIC_REVIEW'))
            self.assertEqual(receipt['result']['version'], 1)
        if index == 4:
            mid = receipt['result']['manifest_id']; manifest = state['manifests'][mid]
            self.assertEqual(mid, s.digest(manifest))
            self.assertEqual((manifest['source_manifest'],manifest['source_review'],manifest['source_id']), (v.sm,1,v.sid))
            self.assertEqual(manifest['data_generation'], 0)
            self.assertEqual(manifest['data_hash'], s.digest(v.before['client']['state']['data']))
            self.assertEqual(manifest['targets'], v.targets)
            self.assertEqual(set(manifest['after']['entities']), {t['target_id'] for t in v.targets})
            self.assertEqual(len(manifest['after']['relations']), 2)
        self.assert_empty_effects(v, values)

    def read_and_replay(self, v, committed, index=None):
        before = v.observe('before_command_read')
        opened = v.passive([v.read])
        read = opened['commands'][v.cmd['cid']]
        if committed:
            self.assertEqual(read, dict(before['client']['state']['receipts'][v.cmd['cid']], historical=True))
        else:
            self.assertEqual(read, dict(result='NOT_COMMITTED_AT_HEAD', grants_execution_authority=False))
        event = v.run_job(dict(action='replay', operation=v.cmd['kind'], mode='LOCAL', stage=v.stage, command=v.cmd), 'explicit_replay')
        replay = event['value']
        self.assertEqual(replay['historical'], committed)
        after = v.observe('after_explicit_replay')
        if committed:
            self.assertEqual(after, before)
        if index is not None:
            self.assert_early_transition(v, index, after)
        v.event('REPLAY_VERIFIED', operation=v.cmd['kind'], mode='LOCAL', stage=v.stage, round=3, cid=v.cmd['cid'], request_sha256=v.read['request_hash'], historical=replay['historical'])
        return after

    def early(self, case, index, point):
        def exercise(v):
            job = v.early(index); job['point'] = point
            after = v.crash(job)
            committed = point == 'after_head'
            if committed:
                self.assert_early_transition(v,index,after)
            else:
                self.assertEqual(after, v.before)
            physical = v.oracles[-1]['client']
            self.assertEqual(physical['unreachable_objects'], int(point in ('after_object','before_replace')))
            self.assertEqual(physical['temporary_heads'], int(point == 'before_replace'))
            self.assertEqual(physical['temporary_objects'], 0)
            self.read_and_replay(v, committed, index)
        self.scenario(case,'R',exercise)

    def fsync(self, case, index):
        def exercise(v):
            job = v.early(index)
            job.update(action='io_fault', point='directory_fsync')
            event = v.run_job(job,'directory_fsync_fault')
            self.assertEqual(event['value']['error'], 'COMMIT_UNKNOWN')
            after = v.observe('visible_after_directory_fsync_fault')
            self.assert_early_transition(v,index,after)
            v.event('CONTROLLED_OSERROR', role='CLIENT', operation=job['operation'], mode='LOCAL', stage=v.stage, point='directory_fsync', code='COMMIT_UNKNOWN', old_client_poisoned=True)
            event = v.run_job(dict(job, point='recovery_fsync'), 'recovery_fsync_fault')
            self.assertEqual(event['value']['poisoned_error'], 'RECOVERY_REQUIRED')
            self.assertEqual(v.observe('after_failed_recovery'), after)
            v.event('CONTROLLED_OSERROR', role='CLIENT', operation=job['operation'], mode='LOCAL', stage=v.stage, point='recovery_fsync', code='COMMIT_UNKNOWN', round=2)
            self.read_and_replay(v, True, index)
        self.scenario(case,'R',exercise)

    def local_gap(self, case, path):
        def exercise(v):
            if path == 'T':
                ids = s.T.ready(v.lab,apply=False,projection=False)
                kind, mid, v.stage, tid, bid = 'APPLY', ids['effect'], 'EFFECT', s.T.uid(30), s.T.uid(40)
            else:
                raw, targets = s.R.source(tasks=1)
                ids = s.R.prepare(v.lab,raw,targets,apply=False)
                kind, mid, v.stage, tid, bid = 'APPLY_BATCH', ids['batch'], 'BATCH', s.R.uid(12), s.R.uid(100)
            v.cmd,v.read = v.command(kind,dict(manifest_id=mid,review_version=1))
            v.before = v.observe('before_local_apply')
            manifest = v.before['client']['state']['manifests'][mid]

            def local_oracle(values, gate=None):
                state = values['client']['state']
                self.assertEqual(state['data_generation'], v.before['client']['state']['data_generation']+1)
                self.assertIn(v.cmd['cid'], state['receipts'])
                self.assertFalse(state['bindings'] or state['sends'] or state['pending'])
                self.assertFalse(any(m['stage']=='PROJECTION' for m in state['manifests'].values()))
                self.assertEqual(values['remote'],v.before['remote'])
                if path == 'T':
                    self.assertEqual(set(state['tasks']), {tid})
                    self.assertEqual(state['tasks'][tid],manifest['after'])
                    self.assertEqual(state['bases'][tid],state['tasks'][tid])
                    self.assertEqual(state['mappings'][tid],manifest['identity'])
                    self.assertEqual(state['provenance'][tid], dict(source_id=manifest['source_id'],effect_manifest=mid,review_version=1))
                else:
                    data = state['data']; self.assertIsNone(state['selection'])
                    self.assertEqual(set(data['entities']),{s.R.uid(10),s.R.uid(11),s.R.uid(12)})
                    self.assertEqual({e['kind'] for e in data['entities'].values()},{'REQUIREMENT','EPIC','TASK'})
                    self.assertEqual({(r['type'],r['left'],r['right'],r['kind']) for r in data['relations'].values()},
                                     {('EPIC_REQUIREMENT',s.R.uid(11),s.R.uid(10),None),('TASK_EPIC',s.R.uid(12),s.R.uid(11),None)})
                    for key in ('entities','relations','mappings','bases'):
                        self.assertEqual(data[key],manifest['after'][key])
                    for key, planned in [('entity_provenance','entities'),('relation_provenance','relations')]:
                        self.assertEqual(set(data[key]),set(data[planned]))
                        for identifier, entries in data[key].items():
                            self.assertEqual(entries,[dict(source_sha256=manifest['source_id'],manifest_sha256=mid,source_review_version=1,batch_review_version=1,locators=manifest['plan'][planned][identifier])])
                self.assertFalse(values['remote']['state']['entities'] or values['remote']['state']['tickets'])
            after = v.crash(dict(operation=kind,mode='LOCAL',stage=v.stage,point='after_head',command=v.cmd), local_oracle)
            local_oracle(after)
            after_replay = self.read_and_replay(v,True)
            self.assertEqual(after_replay,after)
            event = v.run_job(dict(action='continue_gap',operation='BIND/PREPARE_PROJECTION/REVIEW',mode='LOCAL',stage='PROJECTION',cid=v.cmd['cid'],request_hash=v.read['request_hash'],tid=tid,bid=bid),'explicit_continuation')
            state = v.observe('projection_reviewed_without_issue')['client']['state']
            pm = event['value']['manifest_id']
            self.assertEqual(state['manifests'][pm]['target_id'],tid)
            self.assertEqual(state['reviews']['PROJECTION:'+pm]['version'],1)
            self.assertEqual(state['reviews']['PROJECTION:'+pm]['decision'],'ACCEPT')
            self.assertFalse(state['sends'] or state['pending'])
            self.assertEqual(len(state['bindings']),1)
            self.assertEqual(len([r for r in state['receipts'].values() if r['result'].get('outcome') in ('APPLIED','BATCH_APPLIED')]),1)
            self.assertEqual(state['data_generation'],2 if path=='T' else 1)
            if path=='T':
                self.assertEqual(state['tasks'],after['client']['state']['tasks'])
            else:
                self.assertEqual(state['data'],after['client']['state']['data'])
                self.assertEqual(state['selection']['batch_command'],v.cmd['cid'])
                self.assertEqual(state['selection']['batch_request'],v.read['request_hash'])
                self.assertEqual(state['selection']['task_ids'],[tid])
            self.assertEqual(v.observe('remote_still_empty')['remote'],v.before['remote'])
            v.event('EXPLICIT_GAP_CONTINUATION',role='CLIENT',operation=kind+'→PROJECTION',mode='LOCAL',stage='PROJECTION',round=3,target_id=tid,manifest_id=pm,data_generation=state['data_generation'],issue_count=0)
        self.scenario(case,path,exercise)

    def unknown(self, case, path, point):
        def exercise(v):
            if path=='T':
                ids=s.T.ready(v.lab); mid=ids['projection']
            else:
                raw,targets=s.R.source(tasks=1);ids=s.R.prepare(v.lab,raw,targets);mid=ids['projections'][0]
            sid=s.uid(); manifest=v.lab.client.snapshot()['state']['manifests'][mid]
            self.assertEqual(manifest['operation'],'CREATE')
            if point!='after_remote':
                out=v.lab.client.dispatch(mid,1,send_id=sid,deliver=False)
                v.lab.remote.execute(out['ticket'],manifest)
            before=v.observe('before_first_uncertain_operation')
            if point!='after_remote':
                self.assertEqual(before['client']['state']['sends'][sid]['queries'],0)
                self.assertEqual(before['client']['state']['sends'][sid]['status'],'UNKNOWN')
            captured={}

            def gate_oracle(values, gate):
                client,remote=values['client'],values['remote'];state=client['state'];send=state['sends'][sid]
                ticket=send['attempts'][0];proof=remote['state']['tickets'][ticket]
                self.assertEqual(len(send['attempts']),1)
                self.assertEqual((send['status'],send['ledger_version'],send['proof']),('UNKNOWN',1,None))
                self.assertEqual(send['queries'],0 if point=='after_remote' else 1)
                self.assertEqual(len(state['sends']),1)
                self.assertEqual(set(state['pending']),{'send:'+ticket} if point=='after_remote' else {'send:'+ticket,next(k for k in state['pending'] if not k.startswith('send:'))})
                self.assertTrue(all(p['send_id']==sid for p in state['pending'].values()))
                self.assertEqual((proof['status'],proof['manifest_hash'],proof['request_hash']),('EFFECT_CONFIRMED',s.digest(manifest),s.digest(manifest)))
                self.assertEqual((proof['run_id'],proof['store_id'],proof['creation_key']),(v.lab.run_id,v.lab.remote_id,manifest['creation_key']))
                self.assertEqual(len(remote['state']['entities']),1);self.assertEqual(len(remote['state']['tickets']),1)
                entity=remote['state']['entities'][proof['remote_id']]
                self.assertEqual(entity['version'],proof['applied_version']);self.assertEqual(entity['version'],1)
                self.assertEqual(entity['payload'],manifest['payload']);self.assertEqual(s.digest(entity['payload']),proof['payload_hash'])
                operations=[c['operation']['kind'] for c in client['chain']]
                self.assertEqual(operations.count('RESULT'),0)
                self.assertEqual(operations.count('QUERY'),0 if point=='after_remote' else 1)
                self.assertEqual(gate['transport']['lookup'],int(point=='before_result'))
                self.assertEqual(gate['transport']['execute'],int(point=='after_remote'))
                if point=='before_result':self.assertEqual(gate['transport']['proof_sha256'],s.digest(proof))
                if point=='after_remote':self.assertEqual(gate['transport']['execute_proof_sha256'],s.digest(proof))
                command=client['chain'][-1]
                captured.update(values=values,proof=proof,read=dict(cid=command['command_id'],request_hash=command['request_sha256']))
                v.record['uncertain_identity']=dict(send_id=sid,ticket=ticket,manifest_id=mid,target_id=manifest['target_id'],creation_key=proof['creation_key'],remote_id=proof['remote_id'],applied_version=1,proof_sha256=s.digest(proof),gate_ledger_version=1,gate_queries=send['queries'],proof_observed=point!='after_query')
            after=v.crash(dict(operation='dispatch' if point=='after_remote' else 'reconcile',mode='CREATE',stage='PROJECTION',point=point,mid=mid,sid=sid),gate_oracle)
            self.assertEqual(after,captured['values'])
            opened=v.passive([captured['read']])
            self.assertTrue(opened['commands'][captured['read']['cid']]['historical'])
            self.assertEqual(opened['summary']['sends'][0]['status'],'UNKNOWN')
            event=v.run_job(dict(action='reconcile',operation='QUERY/RESULT',mode='CREATE',stage='PROJECTION',sid=sid),'explicit_new_reconcile')
            self.assertEqual((event['transport']['lookup'],event['transport']['execute']),(1,0))
            values=v.observe('explicit_reconcile_complete');send=values['client']['state']['sends'][sid]
            self.assertEqual((send['status'],send['ledger_version'],send['queries']),('EFFECT_CONFIRMED',2,1 if point=='after_remote' else 2))
            self.assertEqual(send['proof'],captured['proof'])
            self.assertFalse(values['client']['state']['pending'])
            self.assertEqual(send['attempts'],[v.record['uncertain_identity']['ticket']])
            self.assertEqual(values['remote'],after['remote'])
            v.event('UNKNOWN_EXPLICITLY_RECONCILED',role='CLIENT',operation='QUERY/RESULT',mode='CREATE',stage='PROJECTION',round=3,ledger_version=2,queries=send['queries'],proof_sha256=s.digest(send['proof']),execute_calls=0)
        self.scenario(case,path,exercise)

    def test_HF31(self):self.local_gap('HF31','T')
    def test_HF32(self):self.local_gap('HF32','R')
    def test_HF33(self):self.unknown('HF33','T','after_remote')
    def test_HF34(self):self.unknown('HF34','R','after_remote')
    def test_HF35(self):self.unknown('HF35','T','before_result')
    def test_HF36(self):self.unknown('HF36','R','before_result')
    def test_HF37(self):self.unknown('HF37','T','after_query')
    def test_HF38(self):self.unknown('HF38','R','after_query')

    def test_HF39(self):
        for path in ('T','R'):
            def exercise(v):
                job=dict(operation='APPLY',mode='LOCAL',stage='EFFECT',point='after_head')
                event=dict(event='READY',role='CLIENT',run_id=v.lab.run_id,**job)
                s.validate_gate(event,job,v.value)
                with self.assertRaisesRegex(AssertionError,'WRONG_GATE'):s.validate_gate(dict(event,point='before_object'),job,v.value)
                with self.assertRaisesRegex(AssertionError,'GATE_IDENTITY'):s.validate_gate(dict(event,run_id=s.uid()),job,v.value)
                for target,negative in [(s.held_child,'TIMEOUT'),(s.normal_child,'NORMAL_EXIT'),(s.empty_child,'EOF')]:
                    pair=s.start(target,(),dict(case='HF39',path=path,actor=negative,action='negative_control'));v.children.append(pair)
                    try:
                        if negative=='TIMEOUT':
                            self.assertEqual(s.receive(pair[1])['event'],'READY')
                            with self.assertRaisesRegex(AssertionError,'CONTROL_TIMEOUT'):s.receive(pair[1],timeout=0.02)
                        elif negative=='NORMAL_EXIT':
                            message=s.receive(pair[1])
                            with self.assertRaisesRegex(AssertionError,'MISSING_READY'):s.validate_gate(message,job,v.value)
                            s.finish(*pair)
                            with self.assertRaisesRegex(AssertionError,'CHILD_EXIT'):s.require(pair[0].exitcode==-signal.SIGKILL,'CHILD_EXIT')
                        else:
                            with self.assertRaisesRegex(AssertionError,'CONTROL_EOF'):s.receive(pair[1])
                            s.finish(*pair)
                    finally:s.stop_owned([pair])
                    v.event('NEGATIVE_CONTROL',operation='CONTROL',point=negative,reduced_timeout_seconds=0.02 if negative=='TIMEOUT' else None,exitcode=pair[0].exitcode,counts_as_crash=False)
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
            self.scenario('HF39',path,exercise)

    def test_HF40(self):
        def exercise(v):
            with tempfile.TemporaryDirectory(prefix='d5-i44-inventory-') as directory:
                s.EXTRA_ROOTS.append(directory)
                path=Path(directory)/'synthetic-input';path.write_text('synthetic-a')
                before=s.hash_inputs([path]);s.validate_inventory(before,s.hash_inputs([path]))
                path.write_text('synthetic-b')
                with self.assertRaisesRegex(AssertionError,'STALE_INPUTS'):s.validate_inventory(before,s.hash_inputs([path]))
                rawpath=Path(directory)/'synthetic-raw.json'
                with self.assertRaisesRegex(AssertionError,'RAW_MISSING_OR_TYPE'):s.raw_binding(rawpath)
                rawpath.write_text('{')
                with self.assertRaisesRegex(AssertionError,'RAW_INCOMPATIBLE'):s.raw_binding(rawpath)
                rawpath.write_text(json.dumps(dict(status='PASS',passed=['synthetic.test'],tests_run=1)))
                binding=s.raw_binding(rawpath)
                self.assertEqual(binding['tests_run'],1)
                with self.assertRaisesRegex(AssertionError,'RAW_HASH_MISMATCH'):s.raw_binding(rawpath,'0'*64)
                with self.assertRaisesRegex(AssertionError,'RAW_BUDGET'):s.raw_binding(rawpath,maximum=1)
                rawpath.write_text(json.dumps(dict(status='PASS',passed=['synthetic.test']*2,tests_run=2)))
                with self.assertRaisesRegex(AssertionError,'RAW_COUNTS'):s.raw_binding(rawpath)
                extra=Path(directory)/'added-input';extra.write_text('synthetic-added')
                with self.assertRaisesRegex(AssertionError,'STALE_INPUTS'):s.validate_inventory(before,s.hash_inputs([path,extra]))
            with self.assertRaisesRegex(AssertionError,'RAW_BUDGET'):s.bounded_raw(dict(synthetic='x'*128),maximum=64)
            with self.assertRaisesRegex(AssertionError,'EVENT_SIZE_BUDGET'):v.event('OVERSIZE',synthetic='x'*(s.MAX_EVENT_BYTES+1))
            limit=s.MAX_EVENTS
            try:
                s.MAX_EVENTS=len(v.events)
                with self.assertRaisesRegex(AssertionError,'EVENT_BUDGET'):v.event('OVERCOUNT')
            finally:s.MAX_EVENTS=limit
            planned=json.loads(Path('docs/validation/D5-I43-design-review.json').read_text())
            expected=['test_'+r['id'] for r in planned['rows']]
            methods=unittest.defaultTestLoader.getTestCaseNames(type(self));self.assertEqual(methods,expected)
            s.validate_report(methods,expected,[],0)
            for passed,skipped,remaining,code in [(methods+methods[:1],[],0,'DUPLICATE_TEST_IDS'),(methods[:-1],[],0,'INCOMPLETE_CAMPAIGN'),(methods,['skip'],0,'INCOMPLETE_CAMPAIGN'),(methods,[],1,'RESOURCES_REMAINING')]:
                with self.assertRaisesRegex(AssertionError,code):s.validate_report(passed,expected,skipped,remaining)
            self.assertFalse(planned['D5_closed'] or planned['publication_authorized'])
            self.assertEqual(len(planned['global_gaps_open']),7)
            v.event('EVIDENCE_NEGATIVES',operation='INVENTORY/REPORT',changed_added_inputs_rejected=True,events_raw_bounded=True,missing_incompatible_hash_raw_rejected=True,duplicates_incomplete_skipped_residue_rejected=True,separate_campaigns=True)
        self.scenario('HF40','R',exercise)


def early_test(number,index,point):
    def test(self):self.early(f'HF{number:02}',index,point)
    test.__name__=f'test_HF{number:02}'
    return test


def fsync_test(number,index):
    def test(self):self.fsync(f'HF{number:02}',index)
    test.__name__=f'test_HF{number:02}'
    return test


for _index in range(6):
    for _offset,_point in enumerate(s.POINTS):
        _number=1+4*_index+_offset
        setattr(CrashBoundariesTest,f'test_HF{_number:02}',early_test(_number,_index,_point))
    _number=25+_index
    setattr(CrashBoundariesTest,f'test_HF{_number:02}',fsync_test(_number,_index))
