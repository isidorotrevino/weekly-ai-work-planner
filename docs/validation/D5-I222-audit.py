#!/usr/bin/env python3
"""I222 static deferred CE12 review; no product, claim, process, positive codec or crypto execution."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'd73176516f3cde2ea36ffd9b3a597eb68b0daa37'
DOS = P+'D5-I193-CE12-CONDITIONAL-ACTUAL-CLAIM-RECEIPT-CANDIDATE.json'
PLAN = P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
PROFILE = P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE06 = P+'D5-I193-CE06-PLATFORM-CLOCK-GLOBAL-LEDGER-CANDIDATE.json'
CE11 = P+'D5-I193-CE11-PRELAUNCH-EVIDENCE-CLOSURE-REVIEW-CANDIDATE.json'
BOUND = P+'D5-I192-I191-source-reconstruction.json'
PRIOR_AUDIT = P+'D5-I221-audit.py'
PRIOR_PREP = P+'D5-I221-preparation-review.json'
PRIOR_SEAL = P+'D5-I221-integrity.json'
PRIOR_DOC = 'docs/design/D5-I221-CE12-CONDITIONAL-CLAIM-RECEIPT.md'
PRIOR_FILES = {DOS,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I222-I221-source-reconstruction.json'
REVIEW = P+'D5-I222-I221-documentary-review.json'
AUDIT = P+'D5-I222-audit.py'
SEAL = P+'D5-I222-integrity.json'
DOC = 'docs/design/D5-I222-I221-CE12-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_CE12_DEFERRED_NOT_AUTHORIZED'
DATE = '2026-11-24'


def rd(p):
    return json.loads((ROOT/p).read_text())


def sha(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def pin(p,pointer=''):
    return dict(path=p,sha256=sha(p),json_pointer=pointer)


def fragment(source):
    assert source['sha256'] == sha(source['path'])
    value = rd(source['path'])
    for token in source.get('json_pointer','').split('/')[1:]:
        key = token.replace('~1','/').replace('~0','~')
        value = value[int(key)] if isinstance(value,list) else value[key]
    return value


def verify_blobs(pins):
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()))
    for p,h in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', p
        body = stream.read(int(header[2]))
        assert stream.read(1) == b'\n' and hashlib.sha256(body).hexdigest() == h == sha(p), p
    assert stream.read() == b''


def ancestors(graph):
    done = {}
    active = set()
    def visit(n):
        assert n in graph and n not in active, n
        if n in done:
            return done[n]
        active.add(n)
        found = set()
        for parent in graph[n]:
            found.add(parent)
            found.update(visit(parent))
        active.remove(n)
        assert n not in found
        done[n] = found
        return found
    for n in graph:
        visit(n)
    return done


def schema_literal_bytes(value):
    # Schema labels/constants only; never serialize a proposed positive receipt.
    return len(json.dumps(value,ensure_ascii=True,separators=(',',':')).encode('ascii'))


def receipt_envelope(node,defs):
    """Static I192 ASCII/safe-integer model for the receipt's restricted schema tree."""
    if '$ref' in node:
        assert node['$ref'].startswith('#/$defs/')
        return receipt_envelope(defs[node['$ref'][8:]],defs)
    if 'const' in node:
        return schema_literal_bytes(node['const'])
    kind = node['type']
    if kind == 'string':
        return 2+2*node['maxLength']
    if kind == 'integer':
        assert 0 <= node['minimum'] <= node['maximum'] <= 9007199254740991
        return len(str(node['maximum']))
    assert kind == 'object' and node['additionalProperties'] is False
    assert set(node['required']) == set(node['properties'])
    terms = [schema_literal_bytes(k)+1+receipt_envelope(v,defs) for k,v in node['properties'].items()]
    return 2+sum(terms)+max(len(terms)-1,0)


def reconstruct():
    d = rd(DOS)
    plan = rd(PLAN)
    step = plan['steps'][11]
    spec = rd(SPEC)
    defs = rd(PACK)['$defs']
    profile = rd(PROFILE)
    receipt = defs['launch_receipt']
    pins = {**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 907
    verify_blobs(pins)
    assert d['step'] == step['id'] == 'CE12' and step['candidate_dossier_path'] == DOS
    assert d['status'] == step['status'] == 'DEFERRED_NOT_AUTHORIZED'
    assert d['plan_binding'] == pin(PLAN,'/steps/11')
    for a,b in [('required_evidence','required_evidence'),('planned_acceptance_checks','acceptance_checks'),
                ('contract_rules','contract_rules'),('authorization_boundary','authorization_boundary'),
                ('needs_fresh_snapshot_at_launch','needs_fresh_snapshot_at_launch')]:
        assert d[a] == step[b]
    assert len(d['required_evidence']) == len(d['planned_acceptance_checks']) == 3
    assert step['depends_on'] == ['CE11'] and step['record_families'] == ['launch_receipt']
    assert len(d['documentary_inventory']) == len({r['path'] for r in d['documentary_inventory']}) == 17
    for source in d['documentary_inventory']:
        assert pins[source['path']] == source['sha256'] == sha(source['path'])
    dep = d['dependency_gate']
    assert dep['latest_candidate'] == pin(CE11)
    assert fragment(dep['latest_documentary_review'])['current_effect']['CE11_accepted'] is False
    assert dep['documentary_baseline_confirmed'] and not dep['actual_prelaunch_checklist_closed']
    assert dep['competent_CE11_acceptance'] is False and dep['actual_dependency_satisfied'] is False
    prerequisites = plan['closure_boundaries']['external_prerequisites_for_receipt']
    assert len(prerequisites) == 5 and len(d['external_prerequisite_dispositions']) == 5
    for i,row in enumerate(d['external_prerequisite_dispositions']):
        assert row['id'] == 'XP%02d'%(i+1) and row['requirement'] == prerequisites[i]
        assert row['required_before'] == ('ACTUAL_CLAIM' if i < 4 else 'ACTUAL_RECEIPT')
        assert all(value is None for key,value in row.items() if key.startswith('actual_'))
        assert row['satisfied'] is False and row['current_action_authorized'] is False
    order = d['event_order_policy']
    phase1 = rd(CE01)['step_obligation_boundary']['CE12']
    assert fragment(order['source']) == phase1
    assert order['preclaim_external_prerequisites'] == prerequisites[:4] == phase1['preclaim_external_prerequisites']
    assert order['receipt_only_external_prerequisites'] == prerequisites[4:] == phase1['receipt_only_external_prerequisites']
    assert len(order['ordered_requirements']) == 4 and 'before paths/spawn' in order['ordered_requirements'][1]
    assert 'only after accepted claim' in order['ordered_requirements'][2]
    for key in ['claim_requires_its_own_receipt_or_claim_as_precondition',
                'claim_before_full_root_admission_or_paths_spawn_before_claim_allowed','CE11_requires_actual_CE12_claim_spawn_or_receipt']:
        assert order[key] is False
    for key in ['CE06_mechanism_or_CE10_mapping_policy_is_not_actual_claim',
                'receipt_does_not_authorize_its_own_claim_or_retroactive_trust_resources','no_execution_gate_release_from_documentary_or_custody_disposition']:
        assert order[key] is True
    assert order['current_run_command'] is None
    schemas = d['receipt_schema_obligations']
    assert fragment(schemas['source']) == schemas['schema_fragment'] == receipt
    assert receipt['additionalProperties'] is False
    assert len(receipt['required']) == len(receipt['properties']) == len(schemas['field_slots']) == 21
    assert [r['field'] for r in schemas['field_slots']] == receipt['required']
    assert all(r['actual_value'] is None and r['status'] == 'MISSING_NOT_POSITIVE_RECEIPT' for r in schemas['field_slots'])
    assert receipt['properties']['claim_status']['const'] == 'CLAIMED_FOR_ONE_CORRELATED_WORKER'
    assert receipt['properties']['role']['const'] == 'CALLER_PRIVATE_RECEIPT_NOT_NEW_FRAME_OR_AUTHORITY'
    assert schemas['candidate_body_cap_bytes'] == spec['record_caps_bytes']['launch_receipt'] == 8192
    envelope = receipt_envelope(receipt,defs)
    assert envelope == fragment(schemas['historical_schema_envelope_source'])['unrestricted_conservative_schema_upper_bytes']['launch_receipt'] == schemas['historical_ASCII_schema_upper_bytes'] == 2702
    assert schemas['actual_bytes_cap_encoding_schema_or_digest_verified'] is False
    for key in ['schema_claim_status_const_is_requirement_not_observed_event','schema_role_const_is_requirement_not_authority',
                'dossier_with_missing_fields_is_not_an_accepted_I191_record']:
        assert schemas[key] is True
    assert schemas['actual_positive_codec_schema_or_crypto_validation'] == 'NOT_RUN_NO_ACTUAL_BODY'
    ledger = d['global_one_use_policy']
    mechanism = fragment(ledger['source'])
    assert ledger['K14_rule'] == mechanism['rule'] == next(r['rule'] for r in spec['rules'] if r['id'] == 'K14')
    assert ledger['tuple_fields'] == mechanism['tuple_fields'] == ['trust_context_sha256','runtime_request_sha256','invocation_id']
    assert ledger['restart_policy_literal'] == mechanism['restart_policy_literal'] == 'NO_PRIOR_INVOCATION_REUSE_FRESH_CONTEXT_REQUIRED'
    assert ledger['anti_replay_rule'] == profile['bootstrap']['anti_replay']
    for key in ['one_authoritative_global_namespace_across_all_callers_domains_restarts','mapping_and_global_ledger_domain_must_agree',
                'durable_atomic_high_water_rollback_crash_double_spend_proof_required',
                'fresh_nonzero32_octet_unique_invocation_and_at_most_one_outstanding_request_per_context_required',
                'parent_child_is_one_correlated_invocation','uncertain_partial_failed_claim_spends_or_rejects']:
        assert ledger[key] is True
    for key in ['partitioned_per_caller_or_restart_local_claims_allowed','free_retry_or_prior_invocation_reuse_allowed',
                'actual_backend_ledger_or_namespace_selected','actual_claim_or_replay_crash_restart_test_performed']:
        assert ledger[key] is False
    assert all(value is None for value in d['actual_event_state'].values())
    assert d['actual_event_state']['actual_claim_status'] is None and d['actual_event_state']['actual_receipt_status'] is None
    assert len(d['genuine_event_evidence_requirements']) == len(d['failure_and_spent_state_obligations']) == 6
    for i,row in enumerate(d['genuine_event_evidence_requirements']):
        assert row['id'] == 'ER%02d'%(i+1)
        assert all(value is None for key,value in row.items() if key.startswith('actual_'))
        assert row['status'] == 'MISSING_NOT_EVALUATED' and row['accepted'] is False
    failure_topics = []
    for i,row in enumerate(d['failure_and_spent_state_obligations']):
        assert row['id'] == 'FE%02d'%(i+1)
        assert all(value is None for key,value in row.items() if key.startswith('actual_') and key != 'actual_state_evaluated')
        assert row['actual_state_evaluated'] is False and row['accepted'] is False
        failure_topics.append(dict(id=row['id'],condition=row['condition'],required_disposition=row['required_disposition'],
            actual_incident_or_spent_state_verified=False))
    privacy = d['privacy_and_resource_boundary']
    for key in ['receipt_caller_private_not_authority_or_permission','no_new_I187_context_launch_or_authority_field',
                'all_lookup_freshness_identity_crypto_measurement_copies_registry_receipt_native_IO_inside_launch_worker_finish_E01_E05',
                'both_process_Readers_and_global_heap_CPU_IO_service_clock_phase_join_required',
                'unknown_costs_not_zero_and_no_free_offline_verification',
                'cap8192_or_schema2702_not_complete_proof_body_heap_CPU_fit_or_admission']:
        assert privacy[key] is True
    assert privacy['receipt_as_new_C_Q_argv_frame_pipe_file_helper_input_or_capture_output_allowed'] is False
    assert privacy['actual_private_custody_body_or_backend_selected'] is False and privacy['actual_cost_capacity_service_or900_proof'] is None
    time = d['time_and_currentness_policy']
    assert time['profile_time_rule'] == profile['bootstrap']['time'] and time['profile_freshness_rule'] == profile['bootstrap']['freshness']
    assert time['max_validity_seconds'] == profile['bootstrap']['context_limits']['max_validity_seconds'] == 3600
    assert time['max_clock_error_seconds'] == profile['bootstrap']['context_limits']['max_clock_error_seconds'] == 5
    assert time['strict_not_before_lt_expires_at'] and time['client_date_host_clock_schema_or_plan_status_not_trusted_time']
    assert time['no_TOFU_stale_cache_hidden_lookup_or_instantaneous_revocation_claim']
    assert time['actual_clock_or_snapshot_sampled'] is False and time['actual_error_epoch_validity_or_currentness_verified'] is False
    graph = {s['id']:s['depends_on'] for s in plan['steps']}
    closure = ancestors(graph)
    record_order = ancestors(spec['record_order'])
    assert closure['CE12'] == {'CE%02d'%i for i in range(1,12)} and 'CE12' not in closure['CE11']
    assert {'EXTERNAL_CURRENT_MAPPING','Q_REQUEST','FINAL_ROOT'} <= record_order['ATOMIC_CLAIM']
    assert 'ATOMIC_CLAIM' in record_order['LAUNCH_RECEIPT'] and 'LAUNCH_RECEIPT' not in record_order['ATOMIC_CLAIM']
    assert d['inherited_scope_boundaries'] == rd(CE11)['inherited_scope_boundaries']
    assert d['preserved_negative_gates'] == rd(CE11)['preserved_negative_gates']
    assert len(d['inherited_scope_boundaries']['S01_exclusions']) == 8
    for gate in d['preserved_negative_gates']:
        assert fragment({**gate['source'],'json_pointer':gate['json_pointer']}) == gate['observed_value']
    assert d['permission_boundary']['denied_action_classes'] == rd(CE11)['permission_boundary']['denied_action_classes']
    assert [r['id'] for r in d['role_scope_matrix']] == step['provenance_and_role']['primary_review_roles'] == ['R01','R02','R06','R08']
    for row in d['role_scope_matrix']:
        assert row['assigned_person'] is None and row['accepted_appointment'] is False and row['current_actions_authorized'] == []
    for key in ['any_new_contributor_body_scope_source_runtime_image_domain_epoch_key_policy_or_currentness_change_requires_fresh_review',
                'revisit_affected_CE02_to_CE10_and_CE11_before_any_separately_authorized_event',
                'no_automatic_prior_hash_proof_approval_mapping_claim_or_receipt_transfer']:
        assert d['invalidation_policy'][key] is True
    assert d['invalidation_policy']['actual_rebind_snapshot_refresh_registry_or_service_change'] is False
    for key,value in d['current_effect'].items():
        if key == 'CE12_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_event_evidence_accepted','resource_obligations_closed']:
            assert value == 0 and type(value) is int
        else:
            assert value is False, key
    assert d['decision'] == plan['decision'] and d['E06'] == plan['E06']
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'])
    earlier_reviews = ['D5-I198-I197-documentary-review.json','D5-I202-I201-documentary-review.json',
        'D5-I204-I203-documentary-review.json','D5-I206-I205-documentary-review.json','D5-I208-I207-documentary-review.json',
        'D5-I210-I209-documentary-review.json','D5-I212-I211-documentary-review.json','D5-I214-I213-documentary-review.json',
        'D5-I216-I215-documentary-review.json','D5-I218-I217-documentary-review.json','D5-I220-I219-documentary-review.json']
    earlier_review_pins = []
    for name in earlier_reviews:
        review = rd(P+name)
        assert review['current_effect']['independent_acceptance'] is False
        earlier_review_pins.append(pin(P+name))
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    assert previous['build_review']() == rd(PRIOR_PREP)
    original = Path.exists
    assert git('ls-tree','--name-only',previous['BASE'],'--',DOS) == ''
    assert git('ls-tree','--name-only',BASE,'--',DOS) == DOS
    with previous['predecessor_CE12_presence_as_of_base']():
        assert not (ROOT/DOS).exists()
    assert Path.exists is original and (ROOT/DOS).exists()
    class DocumentaryProbe(Exception):
        pass
    try:
        with previous['predecessor_CE12_presence_as_of_base']():
            raise DocumentaryProbe()
    except DocumentaryProbe:
        pass
    assert Path.exists is original and (ROOT/DOS).exists()
    sections = {'K12':['event_order_policy','external_prerequisite_dispositions'],
        'K13':['time_and_currentness_policy','global_one_use_policy'],
        'K14':['global_one_use_policy','failure_and_spent_state_obligations','actual_event_state'],
        'K15':['privacy_and_resource_boundary'],
        'K16':['receipt_schema_obligations','permission_boundary','current_effect']}
    assert [r['id'] for r in d['contract_rule_requirements']] == list(sections) == step['contract_rules']
    rules = []
    for row in d['contract_rule_requirements']:
        assert fragment(row['source']) == dict(id=row['id'],rule=row['rule'])
        rules.append(dict(id=row['id'],source=row['source'],candidate_sections=[pin(DOS,'/'+s) for s in sections[row['id']]],
            documentary_requirement_preserved=True,actual_competent_acceptance=False))
    return dict(schema='d5.i222-i221-source-reconstruction.v1',increment='I222',date=DATE,base_commit=BASE,
        input_pins=pins,method='Fixed Git blobs and fresh receipt field/constant/envelope, four-before-claim/one-before-receipt, global namespace, failure-obligation and privacy/resource reconstruction. I221 documentary build reproduced without prior publication mains.',
        rule_review=rules,receipt_schema_review=dict(required_fields=receipt['required'],closed_type=True,top_level_field_count=21,
            positive_claim_status_const_not_actual_event=True,all_actual_values_hashes_and_statuses_unavailable=True,
            historical_ASCII_model_upper_bytes=envelope,candidate_cap_bytes=8192,actual_body_encoding_cap_fit_or_provenance_verified=False),
        event_order_review=dict(preclaim_external_prerequisites=prerequisites[:4],receipt_only_external_prerequisites=prerequisites[4:],
            actual_admission_before_claim_before_paths_spawn_required=True,actual_construction_before_receipt_required=True,
            claim_not_its_own_precondition=True,no_CE11_receipt_claim_spawn_dependency=True,
            receipt_is_not_capture_success_or_authority_or_retrospective_resource_proof=True),
        global_one_use_review=dict(tuple_fields=ledger['tuple_fields'],one_namespace_across_all_callers_domains_restarts=True,
            mapping_and_ledger_domain_consistency_required=True,atomic_durable_high_water_rollback_crash_double_spend_proof_missing=True,
            no_free_retry_or_prior_invocation_reuse=True,mechanism_policy_not_actual_claim=True,
            actual_backend_claim_worker_or_receipt_available=False),failure_obligation_review=failure_topics,
        documentary_route_review=dict(prepared_plan_slots_present=12,earlier_eleven_documentary_review_sources=earlier_review_pins,
            current_CE12_review_path=REVIEW,current_review_is_source_only=True,
            actual_plan_step_acceptances=0,actual_prelaunch_gates_still_pending=30,
            historical_plan_status_fields_not_rewritten=True,documentary_cycle_does_not_close_D5_or_authorize_execution=True),
        preservation=dict(documentary_inventory=17,unassigned_roles=4,competent_CE11_dependency_pending=True,
            eight_S01_exclusions_unchanged=True,I221_build_and_twelve_documentary_rejections_reproduced=True,
            historical_CE12_absence_and_current_presence_verified=True,guard_restored_after_success_and_exception=True,
            prior_publication_mains_run=False),
        verdict=dict(new_blocking_documentary_findings=0,CE12_documentary_baseline_confirmed=True,status='DEFERRED_NOT_AUTHORIZED',
            CE12_accepted=False,actual_claim_created=False,actual_protected_construction_or_worker_created=False,
            actual_receipt_created=False,actual_claim_or_receipt_status_available=False,actual_event_evidence_accepted=0,
            independent_acceptance=False,resource_obligations_closed=0,current_execution_authorized=False,product_or_components_executed=0))


def build_review(rec):
    d = rd(DOS)
    checks = [
        ('E01','Actual receipt only after separate authority/full final Q/root/admission and real claim/construction','FOUR_PRECLAIM_PLUS_ONE_PRERECEIPT_SPLIT_PRESERVED_ALL_MISSING'),
        ('E02','Real applicable failure/partial/spent-state evidence; no planned CLAIMED assertion','SIX_OBLIGATIONS_NOT_OBSERVED_INCIDENTS_OR_SIMULATED_TRANSITIONS'),
        ('E03','Private receipt, no new channel/output/authority, block replay/expiry/unknown','PRESERVED_GLOBAL_USE_AND_NO_FREE_RETRY'),
        ('A01','Genuine final E06/payload/Q/root/admission and separate execution authority','NONE_CREATED_OR_GRANTED'),
        ('A02','No CE11 dependency on CE12; no retrospective trust/resources or self-authorizing claim','ACYCLIC_CONDITIONAL_ORDER_NOT_RUNTIME_EVENT'),
        ('A03','Keep DEFERRED_NOT_AUTHORIZED with unavailable actual hashes/statuses','NO_POSITIVE_RECEIPT_OR_CLAIM_PROCESS_EXECUTION')]
    return dict(schema='d5.i222-i221-documentary-review.v1',increment='I222',date=DATE,timezone='Europe/Madrid',
        base_commit=BASE,proposal_id=d['proposal_id'],profile_id=d['profile_id'],step='CE12',
        status='CE12_DOCUMENTARY_BASELINE_CONFIRMED_DEFERRED_NOT_AUTHORIZED_NO_ACTUAL_CLAIM_OR_RECEIPT',
        candidate=pin(DOS),reconstruction=pin(RECON),findings=[],
        checks=[dict(id=i,scope=s,result=r) for i,s,r in checks],contract_rule_review=rec['rule_review'],
        documentary_clarifications=[
            dict(id='C01',subject='Schema const and actual event',disposition='Positive claim_status belongs to the schema requirement only. Every actual receipt/claim body, tuple, ID, hash, epoch and status remains missing. No accepted positive I191 receipt is instantiated.'),
            dict(id='C02',subject='Failure coverage where applicable',disposition='Six failure/spent-state topics describe required mechanism/outcome evidence, not six incidents that must be provoked. No real transition evaluated; local absence does not prove global unspent state or permit retry.'),
            dict(id='C03',subject='Receipt meaning',disposition='A future genuine receipt records actual accepted claim/protected construction for one correlated invocation. It does not prove successful capture, replace resource/provenance proof, grant authority or authorize its own claim.'),
            dict(id='C04',subject='Documentary cycle versus actual closure',disposition='The12 I193 slots now have prepared dossiers and this review completes their documentary review cycle. Actual plan acceptances remain0,30 prelaunch gates remain pending, E01-E05 remain open and D5/IR03/admission are unchanged.')],
        provenance=dict(reviewer='Same Codex assistant/chat that prepared I221',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,competent_R01_R02_R06_review=False,
            separate_R08_acceptance=False,independent_acceptance=False),
        verdict=rec['verdict'],current_effect={**d['current_effect'],'CE12_documentary_review_completed':True,
            'CE12_documentary_confirmation':True,'CE12_documentary_revision_required':False},decision=d['decision'],E06=d['E06'],
        limitations=['No actual CE11 acceptance, functional authorization, final E06/payload/Q/root/admission, global backend/claim, protected construction, worker, applicable failure evidence or private receipt.',
            'Static schemas/21-field/envelope2702/cap8192/policy and order checks are not positive codec/crypto, actual state transitions, record fit, real independent provenance review, complete resources or900-second proof.',
            'Same assistant is not competent independent review or separate R08 acceptance. No execution, provider contact, quota/reserve/binding/authority/destination or active platform/service change.'],
        next_scope='I193 documentary preparation/review cycle is recorded through CE12. Actual closure requires genuine external facts/independent acceptances, complete resource/source evidence and separately authorized final-route/event work; no authority or new paper iteration is automatically created.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I222-audit.py',expected_result=STATUS,
            runtime_harness='N/A: documentary JSON/Git/hash/schema-envelope/order/global-use and failure-policy checks only; no product/components, actual claim/replay/crash/restart/process/codec/crypto execution.',
            over400_lines=True,reason='One CE12 review with independent schema/order/global-spent-state reconstruction and immutable preservation; overage reported. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_is_not_actual_claim_receipt_or_execution_authority=True))


def main():
    rec = reconstruct()
    assert rd(RECON) == rec and rd(REVIEW) == build_review(rec)
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published594'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 599
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i222-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published599'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():
            assert sha(p) == h, p
    assert seal['source_only'] and seal['current_effect'] == rd(REVIEW)['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I222',historical_pins=907,preserved_published_files=599,
        new_files=5,original_documentary_rejections_reproduced=12,verdict=rec['verdict'],
        documentary_plan_slots_prepared_and_reviewed=12,actual_plan_steps_accepted=0,
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
