#!/usr/bin/env python3
"""I221 documentary deferred claim/receipt slot; no product, ledger, process or positive record execution."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'f60c5562607916c5f1e30bf4d82770817cf48a12'
PLAN = P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
PROFILE = P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE06 = P+'D5-I193-CE06-PLATFORM-CLOCK-GLOBAL-LEDGER-CANDIDATE.json'
CE10 = P+'D5-I193-CE10-BUNDLE-APPROVAL-AND-CURRENT-MAPPING-CANDIDATE.json'
CE11 = P+'D5-I193-CE11-PRELAUNCH-EVIDENCE-CLOSURE-REVIEW-CANDIDATE.json'
BOUND = P+'D5-I192-I191-source-reconstruction.json'
DOS = P+'D5-I193-CE12-CONDITIONAL-ACTUAL-CLAIM-RECEIPT-CANDIDATE.json'
PRIOR_AUDIT = P+'D5-I220-audit.py'
PRIOR_RECON = P+'D5-I220-I219-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I220-I219-documentary-review.json'
PRIOR_SEAL = P+'D5-I220-integrity.json'
PRIOR_DOC = 'docs/design/D5-I220-I219-CE11-REVIEW.md'
PRIOR_FILES = {PRIOR_AUDIT,PRIOR_RECON,PRIOR_REVIEW,PRIOR_SEAL,PRIOR_DOC}
AUDIT = P+'D5-I221-audit.py'
PREP = P+'D5-I221-preparation-review.json'
SEAL = P+'D5-I221-integrity.json'
DOC = 'docs/design/D5-I221-CE12-CONDITIONAL-CLAIM-RECEIPT.md'
FILES = {DOS,AUDIT,PREP,SEAL,DOC}
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


def historical_pins():
    pins = {**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 902
    return pins


def verify_blobs(pins):
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()))
    for p,h in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', p
        body = stream.read(int(header[2]))
        assert stream.read(1) == b'\n' and hashlib.sha256(body).hexdigest() == h == sha(p), p
    assert stream.read() == b''


@contextmanager
def predecessor_CE12_presence_as_of_base():
    """Only this new dossier's existence is projected for historical documentary replay."""
    assert git('ls-tree','--name-only',BASE,'--',DOS) == ''
    target = ROOT/DOS
    original = Path.exists
    assert original(target)
    def historical_exists(path):
        return False if path == target else original(path)
    Path.exists = historical_exists
    try:
        yield
    finally:
        Path.exists = original
    assert target.exists()


def build_candidate():
    plan = rd(PLAN)
    step = plan['steps'][11]
    spec = rd(SPEC)
    defs = rd(PACK)['$defs']
    receipt = defs['launch_receipt']
    ce11 = rd(CE11)
    prior_boundary = rd(CE01)['step_obligation_boundary']['CE12']
    ledger = rd(CE06)['global_one_use_policy']
    paths = {PLAN,SPEC,PACK,PROFILE,CE01,CE06,CE10,CE11,BOUND,PRIOR_RECON,PRIOR_REVIEW,
        P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'}
    paths.update(v['path'] for v in plan['bindings'].values())
    prerequisite_rows = [dict(id='XP%02d'%(i+1),requirement=value,
        required_before='ACTUAL_CLAIM' if i < 4 else 'ACTUAL_RECEIPT',
        actual_evidence_body=None,actual_body_sha256=None,actual_provider=None,actual_authority=None,
        actual_competent_review=None,satisfied=False,current_action_authorized=False)
        for i,value in enumerate(plan['closure_boundaries']['external_prerequisites_for_receipt'])]
    evidence_topics = [
        'Genuine C and Q canonical digests and fresh nonzero32-octet invocation; same authentic accepted request/context/one-use scope.',
        'Actual image bytes/runtime/source-root/manifest, caller principal/domain and accepted unique mapping match every receipt identity/hash.',
        'One global ledger domain across all approved callers/domains/restarts matches mapping; durable atomic claim/high-water/rollback and double-spend provenance.',
        'Actual accepted claim ID/epoch/outcome and actual exact protected constructor, one correlated child only, with provider/custody evidence.',
        'Actual current epoch/validity/trusted clock/error/currentness/revocation for every required boundary.',
        'Actual complete constructor_evidence body and independent competent receipt/claim provenance review, not a typed index alone.']
    failure_topics = [
        ('FE01','Missing preclaim authority/root/Q/admission/currentness','Reject; do not claim or construct. Do not infer any global unspent/reusable state from local absence.'),
        ('FE02','Conflicting, duplicate or rollback/stale global claim state','Reject invocation; no per-caller partition or fallback permits reuse.'),
        ('FE03','Uncertain, partial, failed or crash-interrupted claim','Treat as spent or reject under genuine durable mechanism; never free retry or invent successful claim.'),
        ('FE04','Restart, expired context/request or unknown revocation/currentness','Reject old invocation/context; fresh authentic context/request/root/authority needed for any separately authorized attempt.'),
        ('FE05','Failure after accepted claim or protected construction mismatch','No rollback to free/unclaimed invocation; preserve actual spent/failure evidence; no synthetic successful receipt.'),
        ('FE06','Receipt body/hash/schema/cap/provenance unavailable or unverifiable','No accepted receipt and no authority from its absence or proposed fields; no hidden output/channel workaround.')]
    return dict(schema='d5.i221-ce12-conditional-claim-receipt-candidate.v1',increment='I221',date=DATE,
        timezone='Europe/Madrid',base_commit=BASE,proposal_id=ce11['proposal_id'],profile_id=ce11['profile_id'],step='CE12',
        kind='DEFERRED_NEGATIVE_EVENT_EVIDENCE_SLOT_NOT_ACTUAL_CLAIM_OR_POSITIVE_RECEIPT',
        status='DEFERRED_NOT_AUTHORIZED',documentary_status='CE12_NEGATIVE_DOCUMENTARY_SLOT_PREPARED_NO_ACTUAL_EVENTS_OR_RECEIPT',
        input_pins=historical_pins(),plan_binding=pin(PLAN,'/steps/11'),required_evidence=step['required_evidence'],
        planned_acceptance_checks=step['acceptance_checks'],contract_rules=step['contract_rules'],
        authorization_boundary=step['authorization_boundary'],needs_fresh_snapshot_at_launch=step['needs_fresh_snapshot_at_launch'],
        contract_rule_requirements=[dict(id=r['id'],rule=r['rule'],source=pin(SPEC,'/rules/'+str(i))) for i,r in enumerate(spec['rules']) if r['id'] in step['contract_rules']],
        documentary_inventory=[pin(p) for p in sorted(paths)],
        dependency_gate=dict(step='CE11',latest_candidate=pin(CE11),latest_documentary_review=pin(PRIOR_REVIEW),
            documentary_baseline_confirmed=True,actual_prelaunch_checklist_closed=False,competent_CE11_acceptance=False,actual_dependency_satisfied=False),
        producer=dict(identity='Same Codex assistant/chat as earlier candidates',documentary_preparer_only=True,
            actor_independent=False,organizationally_independent=False,competent_acceptance=False,external_contacts_made=False),
        role_scope_matrix=[{**{k:v for k,v in row.items() if k != 'CE01_responsibilities'},
            'CE12_responsibility':'Review genuine authorized claim/constructor/private-receipt evidence within appointed competence only; R08 acceptance is separate.'}
            for row in rd(CE01)['role_scope_matrix'] if row['id'] in step['provenance_and_role']['primary_review_roles']],
        external_prerequisite_dispositions=prerequisite_rows,
        receipt_schema_obligations=dict(source=pin(PACK,'/$defs/launch_receipt'),schema_fragment=receipt,
            field_slots=[dict(field=k,actual_value=None,status='MISSING_NOT_POSITIVE_RECEIPT') for k in receipt['required']],
            candidate_body_cap_bytes=spec['record_caps_bytes']['launch_receipt'],
            historical_schema_envelope_source=pin(BOUND,'/serialized_bounds'),historical_ASCII_schema_upper_bytes=2702,
            actual_bytes_cap_encoding_schema_or_digest_verified=False,
            schema_claim_status_const_is_requirement_not_observed_event=True,
            schema_role_const_is_requirement_not_authority=True,
            dossier_with_missing_fields_is_not_an_accepted_I191_record=True,
            actual_positive_codec_schema_or_crypto_validation='NOT_RUN_NO_ACTUAL_BODY'),
        event_order_policy=dict(source=pin(CE01,'/step_obligation_boundary/CE12'),
            preclaim_external_prerequisites=prior_boundary['preclaim_external_prerequisites'],
            receipt_only_external_prerequisites=prior_boundary['receipt_only_external_prerequisites'],
            ordered_requirements=['Genuine accepted CE01-CE11 custody/proof facts and current authorized final request/root/admission prerequisites',
                'Actual atomic durable one-use claim after full root admission and before paths/spawn',
                'Actual protected construction for exactly one correlated worker only after accepted claim',
                'Actual private receipt only from genuine claim/construction facts, with competent scope/currentness/provenance/cap checks'],
            claim_requires_its_own_receipt_or_claim_as_precondition=False,
            claim_before_full_root_admission_or_paths_spawn_before_claim_allowed=False,
            CE11_requires_actual_CE12_claim_spawn_or_receipt=False,
            CE06_mechanism_or_CE10_mapping_policy_is_not_actual_claim=True,
            receipt_does_not_authorize_its_own_claim_or_retroactive_trust_resources=True,
            no_execution_gate_release_from_documentary_or_custody_disposition=True,
            current_run_command=None),
        global_one_use_policy=dict(source=pin(CE06,'/global_one_use_policy'),K14_rule=ledger['rule'],
            tuple_fields=ledger['tuple_fields'],one_authoritative_global_namespace_across_all_callers_domains_restarts=True,
            partitioned_per_caller_or_restart_local_claims_allowed=False,
            mapping_and_global_ledger_domain_must_agree=True,durable_atomic_high_water_rollback_crash_double_spend_proof_required=True,
            fresh_nonzero32_octet_unique_invocation_and_at_most_one_outstanding_request_per_context_required=True,
            anti_replay_rule=rd(PROFILE)['bootstrap']['anti_replay'],
            restart_policy_literal=ledger['restart_policy_literal'],parent_child_is_one_correlated_invocation=True,
            uncertain_partial_failed_claim_spends_or_rejects=True,free_retry_or_prior_invocation_reuse_allowed=False,
            actual_backend_ledger_or_namespace_selected=False,actual_claim_or_replay_crash_restart_test_performed=False),
        actual_event_state=dict(actual_tuple=None,actual_C_digest=None,actual_Q_digest=None,actual_invocation_id=None,
            actual_claim_id=None,actual_claim_epoch=None,actual_claim_status=None,actual_ledger_domain=None,
            actual_configuration_epoch=None,actual_registry_or_current_mapping=None,actual_C_Q_root_or_admission=None,
            actual_provider_or_authority=None,actual_caller_domain_or_constructor=None,actual_image_runtime_or_source_root=None,
            actual_construction_or_worker=None,actual_failure_partial_or_spent_state=None,
            actual_clock_error_epoch_validity_or_trusted_now=None,actual_receipt_body=None,actual_receipt_bytes=None,
            actual_receipt_sha256=None,actual_receipt_status=None,actual_provenance_or_competent_acceptance=None),
        genuine_event_evidence_requirements=[dict(id='ER%02d'%(i+1),requirement=topic,actual_complete_evidence_body=None,
            actual_body_sha256=None,actual_body_bytes=None,actual_provider=None,actual_custody=None,
            actual_reviewer=None,actual_acceptance=None,status='MISSING_NOT_EVALUATED',accepted=False) for i,topic in enumerate(evidence_topics)],
        failure_and_spent_state_obligations=[dict(id=i,condition=condition,required_disposition=rule,
            actual_event_or_transition=None,actual_state_proof=None,actual_provider_or_custody=None,
            actual_competent_review=None,actual_state_evaluated=False,accepted=False)
            for i,condition,rule in failure_topics],
        privacy_and_resource_boundary=dict(receipt_caller_private_not_authority_or_permission=True,
            receipt_as_new_C_Q_argv_frame_pipe_file_helper_input_or_capture_output_allowed=False,
            no_new_I187_context_launch_or_authority_field=True,
            actual_private_custody_body_or_backend_selected=False,
            all_lookup_freshness_identity_crypto_measurement_copies_registry_receipt_native_IO_inside_launch_worker_finish_E01_E05=True,
            both_process_Readers_and_global_heap_CPU_IO_service_clock_phase_join_required=True,
            actual_cost_capacity_service_or900_proof=None,unknown_costs_not_zero_and_no_free_offline_verification=True,
            cap8192_or_schema2702_not_complete_proof_body_heap_CPU_fit_or_admission=True),
        time_and_currentness_policy=dict(profile_time_rule=rd(PROFILE)['bootstrap']['time'],
            profile_freshness_rule=rd(PROFILE)['bootstrap']['freshness'],strict_not_before_lt_expires_at=True,
            max_validity_seconds=3600,max_clock_error_seconds=5,actual_clock_or_snapshot_sampled=False,
            actual_error_epoch_validity_or_currentness_verified=False,
            client_date_host_clock_schema_or_plan_status_not_trusted_time=True,
            no_TOFU_stale_cache_hidden_lookup_or_instantaneous_revocation_claim=True),
        inherited_scope_boundaries=ce11['inherited_scope_boundaries'],preserved_negative_gates=ce11['preserved_negative_gates'],
        permission_boundary={**ce11['permission_boundary'],'authorized_documentary_actions':['READ_SOURCE_JSON_GIT_HASHES',
            'PREPARE_CE12_DEFERRED_NEGATIVE_EVENT_RECEIPT_DOSSIER','RUN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT']},
        invalidation_policy=dict(any_new_contributor_body_scope_source_runtime_image_domain_epoch_key_policy_or_currentness_change_requires_fresh_review=True,
            revisit_affected_CE02_to_CE10_and_CE11_before_any_separately_authorized_event=True,
            no_automatic_prior_hash_proof_approval_mapping_claim_or_receipt_transfer=True,
            actual_rebind_snapshot_refresh_registry_or_service_change=False),
        historical_replay_policy=dict(CE12_absent_at_BASE=True,exact_Path_exists_query_only_during_predecessor_replay=True,
            restoration_after_success_and_exception_required=True,prior_publication_mains_run=False),
        current_effect=dict(CE12_documentary_prepared=True,CE12_accepted=False,actual_dependency_satisfied=False,
            current_execution_authorized=False,actual_claim_created=False,actual_protected_construction_or_worker_created=False,
            actual_receipt_created=False,actual_claim_status_available=False,actual_receipt_status_available=False,
            actual_event_evidence_accepted=0,actual_failures_or_spent_states_verified=False,independent_acceptance=False,
            resource_obligations_closed=0,product_or_components_executed=False,quotas_changed=False,reserves_changed=False,
            rebind_applied=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),decision=plan['decision'],E06=plan['E06'])


def validate(d):
    assert d['current_effect']['actual_receipt_created'] is False, 'invented_receipt'
    assert d['current_effect']['actual_claim_created'] is False, 'invented_claim'
    assert d['actual_event_state']['actual_claim_status'] is None, 'fabricated_claim_status'
    assert d['global_one_use_policy']['partitioned_per_caller_or_restart_local_claims_allowed'] is False, 'partitioned_claim_namespace'
    assert d['global_one_use_policy']['free_retry_or_prior_invocation_reuse_allowed'] is False, 'partial_claim_free_retry'
    assert d['event_order_policy']['claim_requires_its_own_receipt_or_claim_as_precondition'] is False, 'claim_receipt_cycle'
    assert d['event_order_policy']['claim_before_full_root_admission_or_paths_spawn_before_claim_allowed'] is False, 'claim_order_bypass'
    assert d['privacy_and_resource_boundary']['receipt_as_new_C_Q_argv_frame_pipe_file_helper_input_or_capture_output_allowed'] is False, 'public_receipt_channel'
    assert d['event_order_policy']['CE06_mechanism_or_CE10_mapping_policy_is_not_actual_claim'] is True, 'policy_as_actual_claim'
    assert d['current_effect']['current_execution_authorized'] is False, 'execution_authorized'
    assert d['current_effect']['quotas_changed'] is False, 'quota_change'
    assert d['current_effect']['D5_closed'] is False, 'D5_closed_by_receipt_slot'
    assert d['status'] == 'DEFERRED_NOT_AUTHORIZED'
    assert all(value is None for value in d['actual_event_state'].values())
    assert len(d['receipt_schema_obligations']['field_slots']) == 21
    assert all(row['actual_value'] is None for row in d['receipt_schema_obligations']['field_slots'])
    assert len(d['external_prerequisite_dispositions']) == 5
    assert all(row['satisfied'] is False and row['current_action_authorized'] is False for row in d['external_prerequisite_dispositions'])
    plan = rd(PLAN)
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'])
    assert d == build_candidate(), 'Dossier differs from source reconstruction'


def rejection_checks(d):
    cases = [
        ('invented_receipt',('current_effect','actual_receipt_created'),True),
        ('invented_claim',('current_effect','actual_claim_created'),True),
        ('fabricated_claim_status',('actual_event_state','actual_claim_status'),'INVENTED_EVENT_STATUS'),
        ('partitioned_claim_namespace',('global_one_use_policy','partitioned_per_caller_or_restart_local_claims_allowed'),True),
        ('partial_claim_free_retry',('global_one_use_policy','free_retry_or_prior_invocation_reuse_allowed'),True),
        ('claim_receipt_cycle',('event_order_policy','claim_requires_its_own_receipt_or_claim_as_precondition'),True),
        ('claim_order_bypass',('event_order_policy','claim_before_full_root_admission_or_paths_spawn_before_claim_allowed'),True),
        ('public_receipt_channel',('privacy_and_resource_boundary','receipt_as_new_C_Q_argv_frame_pipe_file_helper_input_or_capture_output_allowed'),True),
        ('policy_as_actual_claim',('event_order_policy','CE06_mechanism_or_CE10_mapping_policy_is_not_actual_claim'),False),
        ('execution_authorized',('current_effect','current_execution_authorized'),True),
        ('quota_change',('current_effect','quotas_changed'),True),
        ('D5_closed_by_receipt_slot',('current_effect','D5_closed'),True)]
    out = []
    for name,path,value in cases:
        mutant = copy.deepcopy(d)
        target = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            validate(mutant)
        except AssertionError as error:
            assert str(error) == name, (name,str(error))
            out.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return out


def build_review():
    d = rd(DOS)
    verify_blobs(d['input_pins'])
    validate(d)
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    original = Path.exists
    with predecessor_CE12_presence_as_of_base():
        rec = previous['reconstruct']()
        assert rec == rd(PRIOR_RECON) and previous['build_review'](rec) == rd(PRIOR_REVIEW)
    assert Path.exists is original and (ROOT/DOS).exists()
    class DocumentaryProbe(Exception):
        pass
    try:
        with predecessor_CE12_presence_as_of_base():
            assert not (ROOT/DOS).exists()
            raise DocumentaryProbe()
    except DocumentaryProbe:
        pass
    assert Path.exists is original and (ROOT/DOS).exists()
    plan = rd(PLAN)
    graph = {s['id']:s['depends_on'] for s in plan['steps']}
    closure = previous['ancestors'](graph)
    assert closure['CE12'] == {'CE%02d'%i for i in range(1,12)} and 'CE12' not in closure['CE11']
    assert [r['requirement'] for r in d['external_prerequisite_dispositions']] == plan['closure_boundaries']['external_prerequisites_for_receipt']
    assert [r['required_before'] for r in d['external_prerequisite_dispositions']] == ['ACTUAL_CLAIM']*4+['ACTUAL_RECEIPT']
    assert [r['id'] for r in d['role_scope_matrix']] == plan['steps'][11]['provenance_and_role']['primary_review_roles'] == ['R01','R02','R06','R08']
    for row in d['role_scope_matrix']:
        assert row['assigned_person'] is None and row['accepted_appointment'] is False and row['current_actions_authorized'] == []
    assert len(d['genuine_event_evidence_requirements']) == len(d['failure_and_spent_state_obligations']) == 6
    for row in d['genuine_event_evidence_requirements']:
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
        assert row['status'] == 'MISSING_NOT_EVALUATED' and row['accepted'] is False
    for row in d['failure_and_spent_state_obligations']:
        assert all(v is None for k,v in row.items() if k.startswith('actual_') and k != 'actual_state_evaluated')
        assert row['actual_state_evaluated'] is False and row['accepted'] is False
    for row in d['external_prerequisite_dispositions']:
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
    assert d['decision'] == plan['decision'] and d['E06'] == plan['E06']
    assert d['event_order_policy']['CE11_requires_actual_CE12_claim_spawn_or_receipt'] is False
    assert d['event_order_policy']['current_run_command'] is None
    receipt = rd(PACK)['$defs']['launch_receipt']
    assert receipt['additionalProperties'] is False
    assert [r['field'] for r in d['receipt_schema_obligations']['field_slots']] == receipt['required']
    assert d['receipt_schema_obligations']['candidate_body_cap_bytes'] == rd(SPEC)['record_caps_bytes']['launch_receipt'] == 8192
    assert d['receipt_schema_obligations']['historical_ASCII_schema_upper_bytes'] == rd(BOUND)['serialized_bounds']['unrestricted_conservative_schema_upper_bytes']['launch_receipt'] == 2702
    assert d['global_one_use_policy']['tuple_fields'] == ['trust_context_sha256','runtime_request_sha256','invocation_id']
    assert d['event_order_policy']['preclaim_external_prerequisites'] == plan['closure_boundaries']['external_prerequisites_for_receipt'][:4]
    assert d['event_order_policy']['receipt_only_external_prerequisites'] == plan['closure_boundaries']['external_prerequisites_for_receipt'][4:]
    assert [r['id'] for r in d['contract_rule_requirements']] == plan['steps'][11]['contract_rules']
    assert d['time_and_currentness_policy']['max_validity_seconds'] == rd(PROFILE)['bootstrap']['context_limits']['max_validity_seconds'] == 3600
    assert d['time_and_currentness_policy']['max_clock_error_seconds'] == rd(PROFILE)['bootstrap']['context_limits']['max_clock_error_seconds'] == 5
    for key,value in d['current_effect'].items():
        if key == 'CE12_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_event_evidence_accepted','resource_obligations_closed']:
            assert value == 0 and type(value) is int
        else:
            assert value is False, key
    return dict(schema='d5.i221-preparation-review.v1',increment='I221',date=DATE,base_commit=BASE,
        status=STATUS,candidate=pin(DOS),plan=pin(PLAN,'/steps/11'),
        counts=dict(input_pins=902,receipt_top_level_fields=21,external_prerequisites=5,preclaim_prerequisites=4,
            receipt_only_claim_construction_prerequisite=1,event_evidence_topics=6,failure_spent_state_topics=6,
            unassigned_role_slots=4,documentary_plan_slots_present=12,actual_steps_accepted=0,resource_obligations_closed=0),
        provenance=d['producer'],source_reconstruction=dict(prior_I220_reconstruction_and_review_reproduced=True,
            prior_publication_mains_run=False,exact_CE12_historical_absence_guard=True,guard_restored_success_and_exception=True,
            no_claim_receipt_cycle_or_claim_as_own_precondition=True,claim_after_full_admission_before_paths_spawn=True,
            global_ledger_mapping_domain_consistency_required=True,receipt_private_not_authority_or_channel=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],decision=d['decision'],E06=d['E06'],
        limitations=['No actual authorization, final E06/payload/Q/root/admission, CE11 acceptance, tuple/claim, protected construction, worker, failure/spent-state evidence or private receipt.',
            'Positive receipt schema const is a future required type value, never an observed claim status. All actual event hashes/statuses remain unavailable. Neither mechanism/mapping policy nor plan-slot presence is actual event evidence.',
            'Same assistant is not competent independent R01/R02/R06 review or separate R08 acceptance. Twelve documentary slots present does not close actual prelaunch gates, E01-E05, D5 or authorize any execution.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I221-audit.py',expected_result=STATUS,
            runtime_harness='N/A: documentary JSON/Git/hash/schema/phase and policy checks only; no product/components, claim/replay/crash/restart/process, crypto/codec or service execution.',
            over400_lines=True,reason='One deferred negative CE12 dossier with21-field schema, prerequisite/order/global-spent-state requirements and immutable preservation; overage reported. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_is_not_actual_claim_receipt_or_execution_authority=True))


def main():
    review = build_review()
    assert rd(PREP) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published589'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 594
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i221-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published594'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():
            assert sha(p) == h, p
    assert seal['source_only'] and seal['current_effect'] == review['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I221',historical_pins=902,preserved_published_files=594,
        new_files=5,documentary_rejections=12,counts=review['counts'],current_effect=review['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
