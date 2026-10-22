# SPDX-License-Identifier: GPL-3.0-only
"""I32 profile/quota contract fixtures, never real provider authority."""
import base64
from copy import deepcopy
import json
from pathlib import Path
import threading
import unittest
from unittest.mock import patch
import uuid

from source_ingest import eligibility_fixture as ef

THREADS=[]
P='00000000-0000-4000-8000-000000000001'
D='00000000-0000-4000-8000-000000000002'


def uid(key):
    return str(uuid.uuid5(uuid.NAMESPACE_OID,'I32-synthetic-'+str(key)))


class ProfilesQuotasTest(unittest.TestCase):
    def setUp(self):
        self.lab=ef.EligibilityLab()
        self.content=Path('testing/D5/fixtures/register-before.md').read_bytes()
        self.dh=self.lab.register_profile(ef.descriptor())
        self.pg=self.lab.select_profile(P,D,self.dh,expected_generation=0)
        self.cap=self.lab.capture(self.content,P,D,'fixture-1')
        self.lab.review('SOURCE',self.cap,expected_version=0,decision='ACCEPT',reason='Explicit source review')
        self.binding=ef.account(uid('binding'),uid('account'),uid('resource'),P)
        self.card=ef.adapter(uid('adapter'))
        self.bid=self.lab.bind_account(self.binding,self.card)
        self.constraints=[ef.constraint(cost=2),ef.constraint('TOKENS','TOKEN','short',5),
                          ef.constraint(window_id='long',cost=2,end=200)]
        self.lab.select_policy(P,ef.policy(uid('policy'),self.constraints,horizon=5),expected_generation=0)
        self.counter=0
        self.oids=[]
        for row in self.constraints: self.oids.append(self.publish(row))
        self.lab.advance_clock(10)

    def publish(self, row=None, *, bid=None, select=True, card=None, oid=None, **extra):
        self.counter+=1; bid=bid or self.bid
        a=self.lab.account_snapshot(bid)
        row=self.constraints[0] if row is None else row
        oid=oid or uid('obs-'+str(self.counter))
        obs=ef.observation(oid,a['binding'],card or a['card'],row,**extra)
        gen=self.lab.publish_observation(bid,obs,expected_generation=a['generation'])
        if select: self.lab.select_observation(bid,oid,expected_generation=gen)
        return oid

    def prepare(self, capture=None, bid=None):
        return self.lab.prepare_evaluation(capture or self.cap,bid or self.bid,source_review_version=1)

    def approved(self):
        mid=self.prepare()
        v=self.lab._reviews['EVALUATION'][mid]['version']
        self.lab.review('EVALUATION',mid,expected_version=v,decision='ACCEPT',reason='Explicit evaluation review')
        return mid,v+1

    def validate(self, pair=None, cid=None):
        mid,version=pair or self.approved()
        return self.lab.validate_evaluation(cid or uid('command'),mid,evaluation_review_version=version)

    def select(self, descriptor):
        dh=self.lab.register_profile(descriptor)
        self.pg=self.lab.select_profile(P,D,dh,expected_generation=self.pg)
        return self.lab.capture(self.content,P,D,'fixture-1')

    def change_card(self, **changes):
        a=self.lab.account_snapshot(self.bid)
        self.lab.change_adapter(self.bid,dict(a['card'],**changes),expected_generation=a['generation'])

    def start(self, action):
        values=[]
        def run():
            try: values.append(action())
            except Exception as exc: values.append(exc)
        t=threading.Thread(target=run); THREADS.append(t); t.start()
        return t,values

    def join(self, t):
        t.join(5); self.assertFalse(t.is_alive())

    def test_PQ01_same_bytes_new_profile_have_distinct_capture_preview_and_manifest(self):
        old=self.lab.artifact(self.cap); mid=self.prepare()
        newcap=self.select(ef.descriptor(version=2)); new=self.lab.artifact(newcap)
        self.assertEqual(old['content_sha256'],new['content_sha256'])
        self.assertNotEqual(self.cap,newcap); self.assertNotEqual(old['preview_sha256'],new['preview_sha256'])
        self.assertEqual(old['preview'],new['preview'])
        with self.assertRaisesRegex(ef.EligibilityError,'SOURCE_REVIEW_REQUIRED'):
            self.lab.prepare_evaluation(newcap,self.bid,source_review_version=1)
        self.lab.review('SOURCE',newcap,expected_version=0,decision='ACCEPT',reason='New profile review')
        self.assertNotEqual(mid,self.prepare(newcap))
        self.assertEqual(self.content,base64.b64decode(new['content_base64']))

    def test_PQ02_extraction_policy_change_requires_new_review_even_if_text_equal(self):
        pair=self.approved(); newcap=self.select(ef.descriptor(policy_version=2))
        self.assertEqual(self.lab.artifact(self.cap)['preview'],self.lab.artifact(newcap)['preview'])
        with self.assertRaisesRegex(ef.EligibilityError,'STALE_PROFILE'): self.validate(pair)

    def test_PQ03_unknown_descriptor_or_decoder_retains_bytes_without_execution(self):
        cap=self.lab.capture(self.content,P,D,'fixture-1',profile_hash='0'*64)
        self.assertEqual('BLOCKED',self.lab.artifact(cap)['state'])
        self.assertEqual(self.content,base64.b64decode(self.lab.artifact(cap)['content_base64']))
        cap=self.select(ef.descriptor(version=2,decoder_id='/tmp/do-not-execute.py'))
        self.assertEqual(['BLOCKED_DECODER'],self.lab.artifact(cap)['diagnostics'])
        with self.assertRaisesRegex(ef.EligibilityError,'SOURCE_PREVIEW_ONLY'):
            self.lab.review('SOURCE',cap,expected_version=0,decision='ACCEPT',reason='Cannot authorize code')

    def test_PQ04_mapping_namespace_is_immutable_and_not_reused(self):
        self.lab.record_mapping_fixture(self.cap,'PT-01',uid('target'))
        before=self.lab.inspect_facts()['mappings']
        cap=self.select(ef.descriptor(version=2))
        self.assertEqual('BLOCKED_PROFILE_MAPPING_REUSE',self.lab.check_mapping_fixture(cap,'PT-01',uid('target')))
        with self.assertRaisesRegex(ef.EligibilityError,'MAPPING_FIXTURE_CONFLICT'):
            self.lab.record_mapping_fixture(cap,'PT-01',uid('target'))
        self.assertEqual(before,self.lab.inspect_facts()['mappings'])
        self.assertEqual('BLOCKED_MAPPING_IDENTITY',self.lab.check_mapping_fixture(cap,'PT-02',uid('target')))

    def test_PQ05_profile_revocation_and_ABA_never_restore_old_generation(self):
        pair=self.approved()
        self.pg=self.lab.select_profile(P,D,None,expected_generation=self.pg)
        self.pg=self.lab.select_profile(P,D,self.dh,expected_generation=self.pg)
        with self.assertRaisesRegex(ef.EligibilityError,'STALE_PROFILE'): self.validate(pair)
        self.assertGreater(self.pg,1)

    def test_PQ06_exact_source_review_and_unstable_checklist_remain_separate(self):
        pair=self.approved()
        self.lab.review('SOURCE',self.cap,expected_version=1,decision='ACCEPT',reason='Replaced review')
        with self.assertRaisesRegex(ef.EligibilityError,'SOURCE_REVIEW_REQUIRED'): self.validate(pair)
        dh=self.lab.register_profile(ef.descriptor(version=2,decoder_id='markdown-structure.v1'))
        self.pg=self.lab.select_profile(P,D,dh,expected_generation=self.pg)
        cap=self.lab.capture(b'# Plan\n- [ ] same title\n',P,D,'checklist')
        self.assertIsNotNone(self.lab.artifact(cap)['preview'])
        with self.assertRaisesRegex(ef.EligibilityError,'SOURCE_PREVIEW_ONLY'):
            self.lab.review('SOURCE',cap,expected_version=0,decision='ACCEPT',reason='No stable identity')

    def test_PQ07_historical_capture_replay_does_not_restore_profile(self):
        artifact=self.lab.artifact(self.cap); pair=self.approved(); receipt=self.validate(pair)
        self.select(ef.descriptor(version=2))
        before=self.lab.inspect_facts()
        self.assertEqual(artifact,self.lab.artifact(self.cap))
        replay=self.validate(pair)
        self.assertTrue(replay['historical']); self.assertEqual(receipt['tick'],replay['tick'])
        self.assertEqual(before,self.lab.inspect_facts())

    def test_PQ08_all_dimensions_and_windows_evaluated_without_summing(self):
        before=self.lab.inspect_facts(); receipt=self.validate()
        self.assertEqual('SIMULATED_ELIGIBLE',receipt['result'])
        self.assertEqual(before,self.lab.inspect_facts())
        mid=self.prepare(); m=self.lab.manifest(mid)
        self.assertEqual(3,len(m['policy_selection']['policy']['constraints']))
        self.assertEqual(set(self.oids),set(m['observation_sha256']))

    def test_PQ09_other_accounts_and_providers_cannot_supply_missing_constraints(self):
        other=ef.account(uid('b2'),uid('a2'),uid('r2'),P,'other-fixture-provider')
        otherbid=self.lab.bind_account(other,self.card)
        self.publish(self.constraints[0],remaining=100,bid=otherbid)
        self.publish(self.constraints[0],remaining=1)
        self.assertEqual('BLOCKED',self.validate()['result'])
        with self.assertRaisesRegex(ef.EligibilityError,'OBSERVATION_SCOPE'):
            self.lab.select_observation(self.bid,uid('obs-4'),expected_generation=self.lab.account_snapshot(self.bid)['generation'])

    def test_PQ10_duplicate_resource_or_physical_account_cannot_multiply_capacity(self):
        for changes in [dict(binding_id=uid('alias'),physical_account_id=uid('new-account')),
                        dict(binding_id=uid('alias'),resource_id=uid('new-resource'))]:
            with self.assertRaisesRegex(ef.EligibilityError,'BINDING_CONFLICT'):
                self.lab.bind_account(dict(self.binding,**changes),self.card)
        self.assertEqual(1,self.lab.summary()['accounts'])

    def test_PQ11_missing_required_window_blocks_and_no_caller_subset_is_accepted(self):
        extra=ef.constraint('MEMORY','BYTE','short',1)
        self.lab.select_policy(P,ef.policy(uid('policy'),self.constraints+[extra],version=2,horizon=5),expected_generation=1)
        self.assertIn('BLOCKED_MISSING_OBSERVATION',self.validate()['diagnostics'])
        with self.assertRaises(TypeError):
            self.lab.prepare_evaluation(self.cap,self.bid,source_review_version=1,constraints=self.constraints[:1])

    def test_PQ12_duplicate_constraints_units_and_invalid_costs_do_not_convert(self):
        for value in (0,-1,1.5,True):
            with self.assertRaises(ef.EligibilityError):
                self.lab.select_policy(P,ef.policy(uid('bad'),[ef.constraint(cost=value)]),expected_generation=1)
        with self.assertRaisesRegex(ef.EligibilityError,'DUPLICATE_CONSTRAINT'):
            self.lab.select_policy(P,ef.policy(uid('bad'),[self.constraints[0]]*2),expected_generation=1)
        wrong=dict(self.constraints[0],unit='OTHER_UNIT')
        self.lab.select_policy(P,ef.policy(uid('policy'),[wrong],version=2),expected_generation=1)
        self.assertIn('BLOCKED_MISSING_OBSERVATION',self.validate()['diagnostics'])

    def test_PQ13_zero_unknown_unlimited_and_revoked_have_distinct_blocking_reasons(self):
        for state in ('KNOWN','UNKNOWN','UNLIMITED_DECLARED','REVOKED'):
            self.setUp(); self.publish(state=state,remaining=0 if state=='KNOWN' else None)
            receipt=self.validate()
            self.assertEqual('BLOCKED',receipt['result'])
            self.assertIn('BLOCKED_QUOTA_EXHAUSTED' if state=='KNOWN' else 'BLOCKED_QUOTA_'+state,receipt['diagnostics'])

    def test_PQ14_future_observation_or_window_does_not_supply_current_capacity(self):
        self.publish(observed_at=20,expires_at=100)
        self.assertIn('BLOCKED_QUOTA_TIME',self.validate()['diagnostics'])
        self.setUp(); row=ef.constraint(start=20,end=100)
        self.lab.select_policy(P,ef.policy(uid('policy'),[row],version=2),expected_generation=1)
        self.publish(row)
        self.assertIn('BLOCKED_QUOTA_TIME',self.validate()['diagnostics'])

    def test_PQ15_half_open_bounds_and_required_horizon_are_revalidated(self):
        pair=self.approved(); self.lab.advance_clock(95)
        self.assertEqual('SIMULATED_ELIGIBLE',self.validate(pair,uid('boundary-95'))['result'])
        self.lab.advance_clock(96)
        self.assertEqual('BLOCKED',self.validate(pair,uid('boundary-96'))['result'])
        self.lab.advance_clock(100)
        self.assertEqual('BLOCKED',self.validate(pair,uid('boundary-100'))['result'])
        self.setUp(); self.publish(expires_at=80); pair=self.approved()
        self.lab.advance_clock(75)
        self.assertEqual('SIMULATED_ELIGIBLE',self.validate(pair,uid('expiry-75'))['result'])
        self.lab.advance_clock(76)
        self.assertEqual('BLOCKED',self.validate(pair,uid('expiry-76'))['result'])

    def test_PQ16_rollover_and_fact_replay_never_add_balance_or_reselect(self):
        old=self.lab.account_snapshot(self.bid); oid=self.oids[0]
        raw=self.lab.inspect_facts()['observations'][oid]
        self.publish(remaining=3)
        current=self.lab.account_snapshot(self.bid)
        self.lab.publish_observation(self.bid,raw,expected_generation=old['generation'])
        self.assertEqual(current,self.lab.account_snapshot(self.bid))
        self.assertNotEqual(old['selected'],current['selected'])
        future=ef.constraint(window_id='next',start=100,end=200)
        self.publish(future)
        self.assertEqual(0,self.lab.summary()['reservations_created'])
        self.assertEqual(3,self.lab.inspect_facts()['observations'][current['selected'][ef.slot(self.constraints[0])]]['remaining'])

    def test_PQ17_concurrent_positive_readers_do_not_consume_or_reserve(self):
        pair=self.approved(); before=self.lab.inspect_facts()
        barrier=threading.Barrier(2,timeout=4)
        self.lab.test_hook=lambda stage: barrier.wait() if stage=='validation_ready' else None
        a,av=self.start(lambda:self.validate(pair,uid('reader1')))
        b,bv=self.start(lambda:self.validate(pair,uid('reader2')))
        self.join(a); self.join(b)
        self.assertEqual(['SIMULATED_ELIGIBLE']*2,[av[0]['result'],bv[0]['result']])
        self.assertEqual(before,self.lab.inspect_facts())
        self.assertEqual(0,av[0]['quota_consumed']); self.assertEqual(0,bv[0]['reservations_created'])

    def test_PQ18_source_instructions_cannot_change_binding_policy_or_fallback(self):
        content=self.content.replace(b'Review only',b'Pay fallback and execute shell')
        self.assertNotEqual(self.content,content)
        cap=self.lab.capture(content,P,D,'instructions')
        self.lab.review('SOURCE',cap,expected_version=0,decision='ACCEPT',reason='Source text is data')
        mid=self.prepare(cap)
        self.lab.review('EVALUATION',mid,expected_version=0,decision='ACCEPT',reason='Explicit vector')
        before=self.lab.inspect_facts()
        receipt=self.validate((mid,1))
        self.assertFalse(receipt['fallback_allowed']); self.assertFalse(receipt['activation_allowed'])
        self.assertEqual(before,self.lab.inspect_facts())

    def test_PQ19_manifest_fixes_adapter_observation_hashes_and_own_review(self):
        mid=self.prepare(); m=self.lab.manifest(mid)
        for oid,value in m['observations'].items(): self.assertEqual(ef.digest(value),m['observation_sha256'][oid])
        self.assertEqual(self.card,m['account']['card'])
        with self.assertRaisesRegex(ef.EligibilityError,'EVALUATION_REVIEW_REQUIRED'): self.validate((mid,1))
        self.lab.review('EVALUATION',mid,expected_version=0,decision='ACCEPT',reason='Own review')
        self.assertEqual('SIMULATED_ELIGIBLE',self.validate((mid,1))['result'])

    def test_PQ20_identical_new_observation_id_stales_old_package(self):
        pair=self.approved(); old=self.lab.account_snapshot(self.bid)['generation']
        self.publish(select=False)
        self.assertGreater(self.lab.account_snapshot(self.bid)['generation'],old)
        with self.assertRaisesRegex(ef.EligibilityError,'STALE_ACCOUNT'): self.validate(pair)
        self.assertEqual('SIMULATED_ELIGIBLE',self.validate()['result'])

    def test_PQ21_adapter_permission_capability_and_online_changes_invalidate(self):
        for changes in [dict(permission='UNKNOWN'),dict(permission='DECLARED_ONLY'),dict(permission='REVOKED'),dict(capabilities=[]),dict(online=False),dict(release='fixture-2')]:
            self.setUp(); pair=self.approved(); self.change_card(**changes)
            with self.assertRaisesRegex(ef.EligibilityError,'STALE_ACCOUNT'): self.validate(pair)
            self.assertEqual('BLOCKED',self.validate()['result'])

    def test_PQ22_other_adapter_release_and_incomplete_observation_block(self):
        self.publish(card=ef.adapter(uid('adapter'),'other-release'))
        self.assertIn('BLOCKED_OBSERVATION_SCOPE',self.validate()['diagnostics'])
        obs=ef.observation(uid('malformed'),self.binding,self.card,self.constraints[0]); del obs['expires_at']
        with self.assertRaisesRegex(ef.EligibilityError,'INVALID_SHAPE'):
            self.lab.publish_observation(self.bid,obs,expected_generation=self.lab.account_snapshot(self.bid)['generation'])

    def test_PQ23_later_timestamp_does_not_win_without_selection(self):
        self.publish(remaining=1)
        self.publish(select=False,remaining=100,observed_at=5,expires_at=100)
        self.assertIn('BLOCKED_QUOTA_EXHAUSTED',self.validate()['diagnostics'])

    def test_PQ24_restore_old_values_after_revocation_does_not_revive_approval(self):
        pair=self.approved(); self.change_card(permission='REVOKED'); self.change_card(permission='SYNTHETIC_GRANTED')
        with self.assertRaisesRegex(ef.EligibilityError,'STALE_ACCOUNT'): self.validate(pair)
        gen=self.lab.account_snapshot(self.bid)['generation']
        self.lab.revoke_observation(self.bid,self.oids[0],expected_generation=gen)
        self.assertIn('BLOCKED_QUOTA_REVOKED',self.validate()['diagnostics'])
        old=self.lab.inspect_facts()['observations'][self.oids[0]]
        self.lab.publish_observation(self.bid,old,expected_generation=1)
        self.assertIn(self.oids[0],self.lab.account_snapshot(self.bid)['revoked'])

    def test_PQ25_review_and_receipt_do_not_modify_facts_or_manifest_hash(self):
        mid=self.prepare(); before=self.lab.inspect_facts(); m=self.lab.manifest(mid)
        self.lab.review('EVALUATION',mid,expected_version=0,decision='ACCEPT',reason='Explicit')
        self.validate((mid,1))
        self.assertEqual(before,self.lab.inspect_facts()); self.assertEqual(mid,ef.digest(m))
        self.assertEqual(m,self.lab.manifest(mid))

    def test_PQ26_fact_change_between_read_and_CAS_has_no_positive_receipt(self):
        pair=self.approved(); ready=threading.Event(); release=threading.Event()
        def hook(stage):
            if stage=='validation_ready':
                ready.set()
                if not release.wait(4): raise RuntimeError('fixture barrier timeout')
        self.lab.test_hook=hook
        child,values=self.start(lambda:self.validate(pair))
        try:
            self.assertTrue(ready.wait(2)); self.publish(remaining=0)
        finally:
            release.set(); self.join(child)
        self.assertIsInstance(values[0],ef.EligibilityError); self.assertEqual('STALE_ACCOUNT',str(values[0]))
        self.assertEqual(0,self.lab.summary()['receipts'])

    def test_PQ26_profile_or_policy_change_before_confirmation_is_stale(self):
        for change in ('PROFILE','POLICY'):
            self.setUp(); pair=self.approved()
            def hook(stage):
                if stage=='validation_ready':
                    if change=='PROFILE': self.select(ef.descriptor(version=2))
                    else: self.lab.select_policy(P,ef.policy(uid('policy'),self.constraints,version=2,horizon=6),expected_generation=1)
            self.lab.test_hook=hook
            with self.assertRaisesRegex(ef.EligibilityError,'STALE_PROFILE|STALE_POLICY'): self.validate(pair)
            self.assertEqual(0,self.lab.summary()['receipts'])

    def test_PQ27_review_revocation_during_validation_detected(self):
        pair=self.approved()
        def hook(stage):
            if stage=='validation_ready':
                self.lab.review('EVALUATION',pair[0],expected_version=1,decision='REJECT',reason='Concurrent revoke')
        self.lab.test_hook=hook
        with self.assertRaisesRegex(ef.EligibilityError,'EVALUATION_REVIEW_REQUIRED'): self.validate(pair)
        self.assertEqual(0,self.lab.summary()['receipts'])

    def test_PQ27_replacement_acceptance_is_not_the_old_review(self):
        pair=self.approved()
        def hook(stage):
            if stage=='validation_ready':
                self.lab.review('EVALUATION',pair[0],expected_version=1,decision='ACCEPT',reason='Replacement review')
        self.lab.test_hook=hook
        with self.assertRaisesRegex(ef.EligibilityError,'EVALUATION_REVIEW_REQUIRED'): self.validate(pair)
        self.assertEqual(0,self.lab.summary()['receipts'])

    def test_PQ28_time_change_without_fact_generation_blocks_at_confirmation(self):
        pair=self.approved(); before=self.lab.account_snapshot(self.bid)
        self.lab.test_hook=lambda stage:self.lab.advance_clock(100) if stage=='validation_ready' else None
        self.assertEqual('BLOCKED',self.validate(pair)['result'])
        self.assertEqual(before,self.lab.account_snapshot(self.bid))

    def test_PQ29_replay_is_historical_after_expiration_and_new_command_revalidates(self):
        pair=self.approved(); first=self.validate(pair); self.lab.advance_clock(100)
        replay=self.validate(pair)
        self.assertTrue(replay['historical']); self.assertEqual(first['tick'],replay['tick'])
        self.assertFalse(replay['grants_execution_authority'])
        self.assertEqual('BLOCKED',self.validate(pair,uid('new-command'))['result'])
        read=self.lab.read_command(first['command_id'],first['request_sha256'])
        self.assertEqual(replay,read)

    def test_PQ29_lost_response_recovers_only_a_historical_receipt(self):
        pair=self.approved(); before=self.lab.inspect_facts()
        def hook(stage):
            if stage=='after_confirm': raise ef.EligibilityError('RESPONSE_LOST')
        self.lab.test_hook=hook
        with self.assertRaisesRegex(ef.EligibilityError,'RESPONSE_LOST'): self.validate(pair)
        replay=self.validate(pair)
        self.assertTrue(replay['historical']); self.assertFalse(replay['grants_execution_authority'])
        self.assertEqual(1,self.lab.summary()['receipts']); self.assertEqual(before,self.lab.inspect_facts())

    def test_PQ30_command_reuse_with_new_request_conflicts(self):
        pair=self.approved(); first=self.validate(pair)
        with self.assertRaisesRegex(ef.EligibilityError,'COMMAND_CONFLICT'):
            self.lab.validate_evaluation(first['command_id'],pair[0],evaluation_review_version=2)
        self.assertEqual(first['request_sha256'],self.lab.read_command(first['command_id'],first['request_sha256'])['request_sha256'])

    def test_PQ31_closed_shapes_invalid_types_and_no_raw_text_in_public_receipt(self):
        for bad in [dict(self.card,api_key='SYNTHETIC_NOT_A_CREDENTIAL'),dict(self.card,online='true'),dict(self.card,adapter_id='bad')]:
            with self.assertRaises(ef.EligibilityError): self.lab.change_adapter(self.bid,bad,expected_generation=7)
        with self.assertRaisesRegex(ef.EligibilityError,'INVALID_SHAPE'): self.lab.register_profile(dict(ef.descriptor(2),command='DO_NOT_RUN'))
        with self.assertRaises(ef.EligibilityError): self.lab.advance_clock(True)
        receipt=self.validate(); encoded=json.dumps(receipt)
        self.assertNotIn('Review only',encoded); self.assertNotIn('SYNTHETIC_NOT_A_CREDENTIAL',encoded)
        self.assertNotIn('content_base64',encoded)

    def test_PQ32_full_count_limits_and_replay_at_receipt_limit(self):
        for i in range(2,17): self.lab.register_profile(ef.descriptor(i))
        with self.assertRaisesRegex(ef.EligibilityError,'PROFILE_BUDGET'): self.lab.register_profile(ef.descriptor(17))
        for i in range(2,17): self.lab.bind_account(ef.account(uid('b'+str(i)),uid('a'+str(i)),uid('r'+str(i)),P),self.card)
        with self.assertRaisesRegex(ef.EligibilityError,'ACCOUNT_BUDGET'):
            self.lab.bind_account(ef.account(uid('b17'),uid('a17'),uid('r17'),P),self.card)
        for i in range(125): self.publish(select=False)
        with self.assertRaisesRegex(ef.EligibilityError,'OBSERVATION_BUDGET'): self.publish(select=False)
        pair=self.approved(); first=None
        for i in range(128):
            value=self.validate(pair,uid('count-'+str(i)))
            if first is None: first=value
        with self.assertRaisesRegex(ef.EligibilityError,'RECEIPT_BUDGET'): self.validate(pair,uid('count-extra'))
        self.assertTrue(self.validate(pair,first['command_id'])['historical'])
        self.assertEqual((16,16,128,128),tuple(self.lab.summary()[k] for k in ('profiles','accounts','observations','receipts')))

    def test_PQ32_constraint_source_manifest_and_label_limits_without_truncation(self):
        rows=[ef.constraint(window_id='w'+str(i)) for i in range(16)]
        self.lab.select_policy(P,ef.policy(uid('policy'),rows,version=2),expected_generation=1)
        with self.assertRaisesRegex(ef.EligibilityError,'CONSTRAINT_BUDGET'):
            self.lab.select_policy(P,ef.policy(uid('policy'),rows+[ef.constraint(window_id='extra')],version=3),expected_generation=2)
        with self.assertRaisesRegex(ef.EligibilityError,'SOURCE_BUDGET'): self.lab.capture(b'x'*(ef.MAX_SOURCE+1),P,D,'oversize')
        with self.assertRaisesRegex(ef.EligibilityError,'INVALID_LABEL'):
            self.lab.register_profile(dict(ef.descriptor(2),profile_id='x'*257))
        with patch.object(ef,'MAX_MANIFEST',1):
            with self.assertRaisesRegex(ef.EligibilityError,'MANIFEST_BUDGET'): self.prepare()
        self.assertEqual(1048576,ef.MAX_MANIFEST)

    def test_PQ33_new_memory_has_no_prior_reviews_receipts_or_authority(self):
        receipt=self.validate(); new=ef.EligibilityLab()
        with self.assertRaisesRegex(ef.EligibilityError,'COMMAND_REQUIRED'):
            new.read_command(receipt['command_id'],receipt['request_sha256'])
        self.assertEqual(0,new.summary()['accounts']); self.assertEqual(0,new.summary()['receipts'])

    def test_PQ34_summary_and_owned_threads_have_no_operational_effects(self):
        self.validate(); value=self.lab.summary()
        for k in ('quota_consumed','reservations_created','persistent_D2_writes','remote_requests'):
            self.assertEqual(0,value[k])
        self.assertFalse(value['D5_closed']); self.assertFalse(value['operational_activation'])
        self.assertEqual([f'G{i:02}' for i in range(1,8)],value['global_gaps_open'])
        self.assertFalse(any(t.is_alive() for t in THREADS))


if __name__=='__main__':
    unittest.main()
