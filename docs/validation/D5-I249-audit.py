#!/usr/bin/env python3
"""I249 W13 negative prelaunch gate disposition and deferred handoff. Own documentary checks only."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'ac3541a94de04edfb4745899679d588dd30c0a51'
DATE = '2026-11-25'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE07 = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
CE07_REVIEW = P+'D5-I212-I211-documentary-review.json'
W02 = P+'D5-I223-W02-PEOPLE-AND-ANCHORS-CANDIDATE.json'
W03 = P+'D5-I223-W03-SOURCES-IMAGE-RUNTIME-CANDIDATE.json'
W04 = P+'D5-I223-W04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
W05 = P+'D5-I223-W05-SUCCESSOR-REQUALIFICATION-CANDIDATE.json'
W06 = P+'D5-I223-W06-SUCCESSOR-HEAP-LIFETIMES-CANDIDATE.json'
W07 = P+'D5-I223-W07-SUCCESSOR-WORK-CPU-UNITS-CANDIDATE.json'
W08 = P+'D5-I223-W08-SUCCESSOR-PHASE-BOUNDS-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CUSTODY = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PROFILE = P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
W09 = P+'D5-I223-W09-E01-E05-INTEGRATION-CANDIDATE.json'
CE08 = P+'D5-I193-CE08-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json'
CE08_REVIEW = P+'D5-I214-I213-documentary-review.json'
W10 = P+'D5-I223-W10-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json'
CPACK = P+'D5-I185-PGO181-SCHEMAS-CANDIDATE-02.json'
CE09 = P+'D5-I193-CE09-EXACT-C-PROJECTION-CANDIDATE.json'
CE09_REVIEW = P+'D5-I216-I215-documentary-review.json'
W11 = P+'D5-I223-W11-EXACT-C-ACCEPTANCE-CANDIDATE.json'
CE10 = P+'D5-I193-CE10-BUNDLE-APPROVAL-AND-CURRENT-MAPPING-CANDIDATE.json'
CE10_REVIEW = P+'D5-I218-I217-documentary-review.json'
SIZE = P+'D5-I192-I191-source-reconstruction.json'
W01 = P+'D5-I223-W01-TARGET-SCOPE-AUTHORITY-CANDIDATE.json'
W12 = P+'D5-I223-W12-BUNDLE-APPROVALS-GLOBAL-MAPPING-CANDIDATE.json'
CE11 = P+'D5-I193-CE11-PRELAUNCH-EVIDENCE-CLOSURE-REVIEW-CANDIDATE.json'
CE11_REVIEW = P+'D5-I220-I219-documentary-review.json'
CHECKLIST = P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
PRIOR_RECON = P+'D5-I248-I247-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I248-I247-documentary-review.json'
PRIOR_AUDIT = P+'D5-I248-audit.py'
PRIOR_SEAL = P+'D5-I248-integrity.json'
PRIOR_DOC = 'docs/design/D5-I248-I247-W12-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I223-W13-PRELAUNCH-GATE-DECISION-CANDIDATE.json'
PREP = P+'D5-I249-preparation-review.json'
AUDIT = P+'D5-I249-audit.py'
SEAL = P+'D5-I249-integrity.json'
DOC = 'docs/design/D5-I249-W13-PRELAUNCH-GATE-DECISION.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W13_THIRTY_GATES_PENDING_NEGATIVE_DISPOSITION_NOT_ADMITTED'
WORK_PATHS = {'W01':W01,'W02':W02,'W03':W03,'W04':W04,'W05':W05,'W06':W06,'W07':W07,'W08':W08,'W09':W09,'W10':W10,'W11':W11,'W12':W12}


def rd(path):
    return json.loads((ROOT/path).read_text())


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def pin(path,pointer=''):
    return dict(path=path,sha256=sha(path),json_pointer=pointer)


def fragment(source):
    assert sha(source['path']) == source['sha256']
    value = rd(source['path'])
    for token in source.get('json_pointer','').split('/')[1:]:
        key = token.replace('~1','/').replace('~0','~')
        value = value[int(key)] if isinstance(value,list) else value[key]
    return value


def check_pointers(value):
    if isinstance(value,dict):
        if {'path','sha256','json_pointer'} <= set(value):
            fragment(value)
        for child in value.values():
            check_pointers(child)
    elif isinstance(value,list):
        for child in value:
            check_pointers(child)


def verify_blobs(pins):
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()))
    for path,digest in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', path
        data = stream.read(int(header[2]))
        assert stream.read(1) == b'\n' and hashlib.sha256(data).hexdigest() == digest == sha(path), path
    assert stream.read() == b''


def gate_requirement(plan,row,i):
    return dict(id=row['id'],category=row['category'],source=pin(PLAN,'/gate_closure_matrix/'+str(i)),exact_plan_gate=row,
        exact_checklist_gate_source=row['source'],
        producer_requirement_ledger=[dict(id=work,source=pin(PLAN,'/work_packages/'+str(int(work[1:])-1)),
            documentary_candidate=pin(WORK_PATHS[work]) if work in WORK_PATHS else None,
            W13_own_output_not_accepted_predecessor=work=='W13',
            actual_complete_accepted_package_and_reviews=None) for work in row['producer_work_package_ids']],
        current_documentary_disposition='PENDING_MISSING_GENUINE_EVIDENCE_AND_COMPETENT_DECISION',
        missing_reason='Producer packages are documentary requirements only; exact genuine evidence bodies, scope/authors/providers/custody and competent primary/separate decisions are absent.',
        actual_body_hash_bytes_locator_source_runtime_scope_author_provider_custody_and_validity=None,
        actual_complete_derivation_all_assumptions_caps_Reader_and_guard_compatibility=None,
        actual_primary_R06_review=None,actual_separate_R08_acceptance=None,
        actual_condition_verified=False,accepted=False,rejected=False,closed=False,execution_authorized=False)


def build_candidate():
    plan,ce11=rd(PLAN),rd(CE11)
    w=plan['work_packages'][12]
    pins={**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==1042
    inventory=sorted({PLAN,CONTRACT,CE01,CE11,CE11_REVIEW,CHECKLIST,PACK,CUSTODY,PROFILE,PRIOR_REVIEW,*WORK_PATHS.values()})
    assert all(p in pins and pins[p]==sha(p) for p in inventory)
    return dict(schema='d5.i249-w13-prelaunch-gate-decision-candidate.v1',increment='I249',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        work_package='W13',planned_deliverable_id=w['deliverable_id'],
        kind='NEGATIVE_DOCUMENTARY_PRELAUNCH_DISPOSITION_NOT_COMPETENT_GATE_ACCEPTANCE_NOT_ACCEPTED_HANDOFF_NOT_EXECUTION_RELEASE',
        status='W13_DOCUMENTARY_NEGATIVE_DISPOSITION_PREPARED_30_GATES_PENDING_CE12_DEFERRED_NOT_ADMITTED',
        input_pins=pins,work_package_binding=pin(PLAN,'/work_packages/12'),required_deliverables=w['deliverables'],required_exit_predicates=w['exit_predicates'],
        reject_if=w['reject_if'],needs_separate_future_authority_for=w['needs_separate_future_authority_for'],documentary_inventory=[pin(p) for p in inventory],
        dependency_gate=dict(source=pin(PLAN,'/work_packages/12/depends_on'),required_package_ids=w['depends_on'],
            **{'W%02d_accepted'%i:False for i in range(1,13)},SD01_stop_active=True,
            latest_W12_documentary_review=pin(PRIOR_REVIEW),actual_entry_authority_or_accepted_effective_baseline=None,
            documentary_preparations_and_reviews_not_actual_dependency_acceptance=True),
        package_dependency_requirements=[dict(id=key,plan_requirement=pin(PLAN,'/work_packages/'+str(int(key[1:])-1)),documentary_candidate=pin(path),
            actual_accepted_same_scope_package_complete_bodies_and_review_records=None,accepted=False) for key,path in WORK_PATHS.items()],
        role_scope_matrix=[r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R06','R08']],
        competent_decision_boundary=dict(source=pin(W02,'/identity_policy'),exact_identity_policy=rd(W02)['identity_policy']['exact_policy'],
            exact_separation_matrix=rd(W02)['separation_matrix'],exact_overlap_policy=rd(W02)['overlap_policy'],
            required_provider_kind=w['provider_kind'],primary_review_roles=w['primary_review_roles'],separate_acceptor_role=w['separate_acceptor_role'],
            genuine_canonical_humans_competence_appointments_independence_all_preparers_and_exclusions_required=True,
            same_assistant_documentary_review_not_actual_R06_or_R08_decision=True,
            W13_named_producer_means_review_output_not_own_accepted_predecessor_or_self_authorization=True,
            actual_primary_R06_identity_appointment_competence_and_review=None,
            actual_separate_R08_identity_appointment_competence_and_acceptance=None,
            actual_immutable_review_body_hash_bytes_custody_scope_or_validity=None,accepted=False),
        thirty_gate_disposition_ledger=[gate_requirement(plan,row,i) for i,row in enumerate(plan['gate_closure_matrix'])],
        deferred_receipt_gate=dict(source=pin(PLAN,'/deferred_gate'),exact_plan_disposition=plan['deferred_gate'],
            id='FAMILY-LAUNCH_RECEIPT',excluded_from30_prelaunch_targets=True,current_status='DEFERRED_NOT_AUTHORIZED',
            actual_body_or_competent_acceptance=None,accepted=False,execution_authorized=False),
        disposition_summary=dict(prelaunch_targets=30,family_targets=7,rule_targets=16,global_targets=7,
            pending=30,accepted=0,rejected_actual_evidence=0,closed=0,separately_deferred_receipt=1,total_checklist_dispositions=31,
            actual_competent_gate_decisions=0,documentary_aggregate='NOT_ADMITTED_INSUFFICIENT_GENUINE_EVIDENCE_AND_COMPETENT_ACCEPTANCE',
            no_gate_closed_by_document_presence_schema_type_signature_flag_or_candidate_budget=True,
            absence_of_actual_rejected_material_not_acceptance_or_evidence_of_fit=True,
            no_partial_positive_aggregate_or_real_checklist_closure=True,
            actual_competent_joint_decision_or_handoff=None),
        E01_E05_disposition_ledger=[dict(id=row['id'],source=pin(PLAN,'/resource_obligation_matrix/'+str(i)),exact_plan_requirement=row,
            W09_requirement=pin(W09,'/resource_obligation_ledger/'+str(i)),
            actual_complete_same_scope_bounds_body_derivations_units_all_assumptions_and_platform_capacity_service=None,
            actual_primary_R03_R06_review_and_separate_R08_acceptance=None,
            current_documentary_disposition='PENDING_INSUFFICIENT_COMPLETE_SUCCESSOR_EVIDENCE',accepted=False,closed=False)
            for i,row in enumerate(plan['resource_obligation_matrix'])],
        twenty_criterion_disposition_ledger=[dict(id=row['id'],obligation=row['obligation'],source=pin(PLAN,'/resource_criterion_matrix/'+str(i)),exact_plan_requirement=row,
            W09_requirement=pin(W09,'/criterion_revalidation_ledger/'+str(i)),
            actual_applicability_exact_scope_body_hash_bytes_author_provider_custody_derivation_and_review=None,
            current_documentary_disposition='PENDING_NOT_TRANSFERRED_FROM_HISTORICAL_RESULT',accepted=False,closes_resource_obligation=False)
            for i,row in enumerate(plan['resource_criterion_matrix'])],
        joint_resource_decision_boundary=dict(source=pin(W09,'/resource_premise_handoff'),
            all_five_obligations_and20_criteria_complete_authentic_compatible_same_final_scope_caps_Reader_outputs_and_guards_required=True,
            all_missing_original_native_heap_lifetime_work_CPU_IO_service_clock_phase_atomicity_BASIS_index_and900_premises_remain_visible=True,
            historical_CP03_179_cases_321_roots_12_groups_30_sites_and_tests_not_successor_or_resource_acceptance=True,
            all30_successor_work_correspondence_not_ten_activities_thirty_scalar_slots_or_twenty_vectors=True,
            conditional_size221644_margin40500_not_actual_encoding_fit_heap_CPU_IO_service_or900_proof=True,
            no_unknown_upper_as_zero_or_unproved_overlap_deduction_or_watchdog_as_success=True,
            actual_complete_joint_resource_scope_compatibility_derivation_or_acceptance=None,actual_E01_E05_closed=0),
        proof_reference_disposition=dict(source=pin(PLAN,'/reference_completeness_policy'),exact_plan_policy=plan['reference_completeness_policy'],
            typed_reference_requirements_source=pin(CE11,'/proof_reference_disposition/typed_reference_templates'),
            exact_typed_reference_requirements=ce11['proof_reference_disposition']['typed_reference_templates'],
            static_template_count=69,template_paths_arrays_and_repeated_nested_records_not_actual_unique_body_count=True,
            all_actual_missing_provided_rejected_references_require_immutable_locator_hash_bytes_authors_providers_custody_scope_review_and_disposition=True,
            provided_actual_proof_bodies=[],rejected_actual_proof_bodies=[],actual_proofs_evaluated=0,actual_full_reference_body_inventory=None,
            actual_reference_completeness_verified=False,absence_of_actual_rejection_not_acceptance=True,
            documentary_sources_and_hashes_not_actual_proof_truth_or_authorship=True),
        additional_proof_requirement_ledger=[dict(id=row['id'],source=pin(CE11,'/additional_proof_obligations/'+str(i)),exact_requirement=row,
            actual_complete_scope_body_provenance_and_genuine_decision=None,accepted=False) for i,row in enumerate(ce11['additional_proof_obligations'])],
        stop_requirement_ledger=[dict(id=row['id'],source=pin(PLAN,'/stop_and_decision_points/'+str(i)),exact_requirement=row,
            actual_provider_capability_or_competent_condition_decision=None,
            documentary_rule_preserved_not_global_absence_or_infeasibility_proof=True) for i,row in enumerate(plan['stop_and_decision_points'])],
        deferred_handoff=dict(source=pin(PLAN,'/prelaunch_handoff_and_CE12'),exact_plan_boundary=plan['prelaunch_handoff_and_CE12'],
            CE11_requirement=pin(CE11,'/prelaunch_handoff'),
            required_prelaunch_package_ids=w['depends_on'],pending_final_route_obligations=plan['prelaunch_handoff_and_CE12']['final_route_obligations'],
            handoff_of_pending_obligations_not_statement_that_final_prerequisites_satisfied=True,
            actual_final_E06_payload_Q_root_admission_claim_spawn_receipt_not_prerequisite_of_prelaunch_acceptance=True,
            no_actual_run_command_request_root_claim_or_destination_created=True,current_run_command=None,
            actual_accepted_prelaunch_facts_or_handoff=False,execution_or_component_qualification_authorized=False),
        CE12_boundary=dict(source=pin(CE11,'/CE12_boundary'),exact_historical_boundary=ce11['CE12_boundary'],
            preclaim_external_prerequisites=plan['prelaunch_handoff_and_CE12']['preclaim_external_prerequisites'],
            receipt_only_external_prerequisites=plan['prelaunch_handoff_and_CE12']['receipt_only_external_prerequisites'],
            all_four_preclaim_prerequisites_genuinely_satisfied_before_claim_and_fifth_actual_claim_construction_before_receipt_required=True,
            claim_not_own_precondition_and_after_full_root_admission_before_paths_spawn=True,
            uncertain_partial_expired_failed_claim_no_free_retry_or_invocation_reuse=True,
            receipt_private_not_capture_output_or_new_wire_field=True,
            actual_claim_spawn_receipt_or_final_route_completion_required_to_close_prelaunch=False,
            actual_execution_authorization_final_E06_payload_Q_root_full_admission_claim_construction_or_receipt=None,
            actual_CE12_authorized=False,actual_CE12_prerequisites_satisfied=False,actual_receipt_created=False),
        final_binding_requirement_ledger=[dict(id=row['id'],source=pin(CE11,'/pending_I177_final_bindings/'+str(i)),exact_historical_requirement=row,
            actual_body_sha256_bytes_custody_or_accepted_proof=None,current_status='DEFERRED_MISSING_NOT_EXECUTED_NOT_AUTHORIZED',accepted=False)
            for i,row in enumerate(ce11['pending_I177_final_bindings'])],
        source_resource_and_invalidation_boundary=dict(source=pin(PLAN,'/scope_authentication_and_freeze_order'),exact_plan_order=plan['scope_authentication_and_freeze_order'],
            inherited_CE11_policy=pin(CE11,'/freeze_and_invalidation_policy'),exact_CE11_policy=ce11['freeze_and_invalidation_policy'],
            scope_policy=pin(PLAN,'/resource_and_scope_policy'),exact_candidate_reserve_rules=rd(CONTRACT)['reserve_accounting'],
            genuine_same_effective_source_runtime_image_policy_body_epoch_author_scope_currentness_and_guard_compatibility_required=True,
            both_Readers_all_per_attempt_lookup_freshness_identity_crypto_native_IO_registry_copies_receipt_output_failure_cleanup_work_inside_global_E01_E05_and_phases=True,
            any_changed_author_body_source_runtime_domain_epoch_key_policy_mapping_graph_or_resource_fact_invalidates_affected_reviews_and_requires_requalification_before_progress=True,
            no_automatic_hash_proof_approval_mapping_or_scope_acceptance_transfer=True,
            actual_source_Reader_output_guard_resource_impact_or_requalification_review=None,
            actual_refresh_rebind_registry_clock_ledger_configuration=False,reserve_transfers_applied=0,resources_reserved=False,quotas_or_budgets_changed=False),
        non_admission_record=dict(I122_certificate='IMPLEMENTED_NOT_ADMITTED',CP07_verified=False,correlated_atomicity_verified=False,components_status='NOT_RUN',
            SOURCE_CAPACITY_VERIFIED_issued=False,PJC115_R2_enabled=False,prelaunch_real_gate_acceptances=0,E01_E05_closed=0,
            custody_or_resource_disposition_not_functional_execution_release_or_D5_closure=True,
            old_active_certificate_flags_not_automatically_promoted=True,
            actual_certificate_capture_inputs_quota_authority_destination_or_D5_change=False,IR03='NOT_READY'),
        authority_boundary=dict(source=pin(PLAN,'/authorization_boundary'),inherited_boundary=plan['authorization_boundary'],
            allowed_now=['READ_DOCUMENTS_GIT_HASHES_AND_EXACT_PATH_PRESENCE','PREPARE_NEGATIVE_30_GATE_DISPOSITION_AND_DEFERRED_HANDOFF','RUN_OWN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT'],
            no_product_components_E06_import_compile_discovery_tests_runs_build_crypto_codec_signing_keygen_enrollment_or_provisioning=True,
            no_C_Q_root_admission_authority_claim_spawn_receipt_capture_destination_registry_mapping_or_service_configuration=True,
            no_clock_CPU_IO_ledger_replay_crash_restart_endpoint_process_platform_benchmarks_probes_or_provider_contacts=True,
            actual_external_authority_material_or_operational_action=None),
        exit_predicate_dispositions=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/12/exit_predicates/'+str(i)),predicate=t,
            documentary_requirements_prepared=True,actual_evidence=None,actual_primary_R06_review=None,actual_separate_R08_acceptance=None,accepted=False) for i,t in enumerate(w['exit_predicates'])],
        preserved_scope_and_gates={key:plan[key] for key in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']},
        current_effect={**{key:value for key,value in rd(W12)['current_effect'].items() if key!='W12_documentary_prepared'},
            'W13_documentary_prepared':True,'W13_accepted':False,'actual_prelaunch_checklist_or_handoff_closed_or_execution_released':False},
        producer=dict(identity='Same Codex assistant/chat as I247/I248',documentary_preparer_only=True,actor_independent=False,
            competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_competent_gate_acceptance_handoff_execution_release_or_D5_closure=True))


NEGATIVE_CASES=[
    ('SD01_bypass',('dependency_gate','SD01_stop_active'),True,False),
    ('W13_acceptance',('current_effect','W13_accepted'),False,True),
    ('self_review_as_competent',('competent_decision_boundary','same_assistant_documentary_review_not_actual_R06_or_R08_decision'),True,False),
    ('self_accepted_predecessor',('competent_decision_boundary','W13_named_producer_means_review_output_not_own_accepted_predecessor_or_self_authorization'),True,False),
    ('gate_accepted',('thirty_gate_disposition_ledger',0,'accepted'),False,True),
    ('gate_closed',('thirty_gate_disposition_ledger',0,'closed'),False,True),
    ('gate_condition_verified',('thirty_gate_disposition_ledger',0,'actual_condition_verified'),False,True),
    ('invented_gate_body',('thirty_gate_disposition_ledger',0,'actual_body_hash_bytes_locator_source_runtime_scope_author_provider_custody_and_validity'),None,'UNVERIFIED_TEST_LABEL'),
    ('gate_execution_authorized',('thirty_gate_disposition_ledger',0,'execution_authorized'),False,True),
    ('receipt_as_prelaunch_gate',('deferred_receipt_gate','excluded_from30_prelaunch_targets'),True,False),
    ('receipt_accepted',('deferred_receipt_gate','accepted'),False,True),
    ('positive_aggregate_count',('disposition_summary','accepted'),0,1),
    ('closed_aggregate_count',('disposition_summary','closed'),0,1),
    ('documents_as_gate_truth',('disposition_summary','no_gate_closed_by_document_presence_schema_type_signature_flag_or_candidate_budget'),True,False),
    ('no_rejection_as_acceptance',('disposition_summary','absence_of_actual_rejected_material_not_acceptance_or_evidence_of_fit'),True,False),
    ('partial_positive_aggregate',('disposition_summary','no_partial_positive_aggregate_or_real_checklist_closure'),True,False),
    ('resource_obligation_closed',('E01_E05_disposition_ledger',0,'closed'),False,True),
    ('criterion_accepted',('twenty_criterion_disposition_ledger',0,'accepted'),False,True),
    ('criterion_as_closure',('twenty_criterion_disposition_ledger',0,'closes_resource_obligation'),False,True),
    ('missing_bound_zero',('E01_E05_disposition_ledger',1,'actual_complete_same_scope_bounds_body_derivations_units_all_assumptions_and_platform_capacity_service'),None,0),
    ('partial_resource_join',('joint_resource_decision_boundary','all_five_obligations_and20_criteria_complete_authentic_compatible_same_final_scope_caps_Reader_outputs_and_guards_required'),True,False),
    ('historical_CP03_as_successor_proof',('joint_resource_decision_boundary','historical_CP03_179_cases_321_roots_12_groups_30_sites_and_tests_not_successor_or_resource_acceptance'),True,False),
    ('ten_as_all30',('joint_resource_decision_boundary','all30_successor_work_correspondence_not_ten_activities_thirty_scalar_slots_or_twenty_vectors'),True,False),
    ('conditional_margin_as_resources',('joint_resource_decision_boundary','conditional_size221644_margin40500_not_actual_encoding_fit_heap_CPU_IO_service_or900_proof'),True,False),
    ('templates_as_real_bodies',('proof_reference_disposition','template_paths_arrays_and_repeated_nested_records_not_actual_unique_body_count'),True,False),
    ('reference_closure_verified',('proof_reference_disposition','actual_reference_completeness_verified'),False,True),
    ('document_hash_as_proof',('proof_reference_disposition','documentary_sources_and_hashes_not_actual_proof_truth_or_authorship'),True,False),
    ('handoff_as_final_prerequisites',('deferred_handoff','handoff_of_pending_obligations_not_statement_that_final_prerequisites_satisfied'),True,False),
    ('receipt_required_for_prelaunch',('deferred_handoff','actual_final_E06_payload_Q_root_admission_claim_spawn_receipt_not_prerequisite_of_prelaunch_acceptance'),True,False),
    ('current_run_command',('deferred_handoff','current_run_command'),None,'UNAUTHORIZED_TEST_COMMAND_LABEL'),
    ('handoff_accepted',('deferred_handoff','actual_accepted_prelaunch_facts_or_handoff'),False,True),
    ('claim_own_precondition',('CE12_boundary','claim_not_own_precondition_and_after_full_root_admission_before_paths_spawn'),True,False),
    ('claim_receipt_as_gate_prerequisite',('CE12_boundary','actual_claim_spawn_receipt_or_final_route_completion_required_to_close_prelaunch'),False,True),
    ('CE12_authorized',('CE12_boundary','actual_CE12_authorized'),False,True),
    ('CE12_prerequisites_satisfied',('CE12_boundary','actual_CE12_prerequisites_satisfied'),False,True),
    ('receipt_created',('CE12_boundary','actual_receipt_created'),False,True),
    ('receipt_new_output',('CE12_boundary','receipt_private_not_capture_output_or_new_wire_field'),True,False),
    ('free_claim_retry',('CE12_boundary','uncertain_partial_expired_failed_claim_no_free_retry_or_invocation_reuse'),True,False),
    ('binding_accepted',('final_binding_requirement_ledger',0,'accepted'),False,True),
    ('resource_cost_omission',('source_resource_and_invalidation_boundary','both_Readers_all_per_attempt_lookup_freshness_identity_crypto_native_IO_registry_copies_receipt_output_failure_cleanup_work_inside_global_E01_E05_and_phases'),True,False),
    ('automatic_scope_transfer',('source_resource_and_invalidation_boundary','no_automatic_hash_proof_approval_mapping_or_scope_acceptance_transfer'),True,False),
    ('active_rebind',('source_resource_and_invalidation_boundary','actual_refresh_rebind_registry_clock_ledger_configuration'),False,True),
    ('reserve_transfer',('source_resource_and_invalidation_boundary','reserve_transfers_applied'),0,1),
    ('quota_change',('source_resource_and_invalidation_boundary','quotas_or_budgets_changed'),False,True),
    ('custody_as_execution_release',('non_admission_record','custody_or_resource_disposition_not_functional_execution_release_or_D5_closure'),True,False),
    ('active_certificate_promoted',('non_admission_record','old_active_certificate_flags_not_automatically_promoted'),True,False),
    ('SOURCE_CAPACITY_VERIFIED',('non_admission_record','SOURCE_CAPACITY_VERIFIED_issued'),False,True),
    ('implicit_product_execution',('authority_boundary','no_product_components_E06_import_compile_discovery_tests_runs_build_crypto_codec_signing_keygen_enrollment_or_provisioning'),True,False),
    ('implicit_root_claim_issue',('authority_boundary','no_C_Q_root_admission_authority_claim_spawn_receipt_capture_destination_registry_mapping_or_service_configuration'),True,False),
    ('exit_accepted',('exit_predicate_dispositions',0,'accepted'),False,True),
    ('D5_closed',('current_effect','D5_closed'),False,True)]


def validate(d):
    for name,path,expected,_ in NEGATIVE_CASES:
        node=d
        for key in path:
            node=node[key]
        assert type(node) is type(expected) and node==expected,name
    assert d==build_candidate(),'Candidate differs from source reconstruction'
    check_pointers(d)


def rejection_checks(d):
    results=[]
    for name,path,_,value in NEGATIVE_CASES:
        mutant=copy.deepcopy(d)
        node=mutant
        for key in path[:-1]:
            node=node[key]
        node[path[-1]]=value
        try:
            validate(mutant)
        except AssertionError as error:
            assert str(error)==name,(name,str(error))
            results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return results


def build_review():
    d=rd(SUBJECT)
    verify_blobs(d['input_pins'])
    validate(d)
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT))
    exists=Path.exists
    rec=previous['reconstruct']()
    assert rec==rd(PRIOR_RECON) and previous['build_review'](rec)==rd(PRIOR_REVIEW)
    assert Path.exists is exists
    plan=rd(PLAN)
    assert d['dependency_gate']['required_package_ids']==['W%02d'%i for i in range(1,13)]
    gates=d['thirty_gate_disposition_ledger']
    assert len(gates)==len({r['id'] for r in gates})==30
    assert {kind:sum(r['category']==kind for r in gates) for kind in ['FAMILY','RULE','GLOBAL']}=={'FAMILY':7,'RULE':16,'GLOBAL':7}
    for i,row in enumerate(gates):
        assert row['exact_plan_gate']==fragment(row['source'])==plan['gate_closure_matrix'][i]
        assert fragment(row['exact_checklist_gate_source'])==row['exact_plan_gate']['source_gate']
        assert [r['id'] for r in row['producer_requirement_ledger']]==row['exact_plan_gate']['producer_work_package_ids']
        assert row['accepted'] is False and row['rejected'] is False and row['closed'] is False and row['actual_condition_verified'] is False
        assert all(v is None for k,v in row.items() if k.startswith('actual_') and k!='actual_condition_verified')
        for producer in row['producer_requirement_ledger']:
            assert fragment(producer['source'])['id']==producer['id']
            assert producer['W13_own_output_not_accepted_predecessor']==(producer['id']=='W13')
            if producer['id']=='W13':
                assert producer['documentary_candidate'] is None
            else:
                assert producer['documentary_candidate']['path']==WORK_PATHS[producer['id']]
    assert d['deferred_receipt_gate']['id'] not in {r['id'] for r in gates}
    assert len(d['E01_E05_disposition_ledger'])==5 and len(d['twenty_criterion_disposition_ledger'])==20
    for rows in [d['E01_E05_disposition_ledger'],d['twenty_criterion_disposition_ledger']]:
        for row in rows:
            assert row['exact_plan_requirement']==fragment(row['source'])
            assert fragment(row['W09_requirement'])['id']==row['id']
            assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    references=d['proof_reference_disposition']
    assert references['exact_typed_reference_requirements']==fragment(references['typed_reference_requirements_source'])
    assert len(references['exact_typed_reference_requirements'])==references['static_template_count']==69
    assert len(d['additional_proof_requirement_ledger'])==8 and len(d['stop_requirement_ledger'])==8
    for row in d['additional_proof_requirement_ledger']+d['stop_requirement_ledger']:
        assert row['exact_requirement']==fragment(row['source'])
    boundary=plan['prelaunch_handoff_and_CE12']
    assert d['deferred_handoff']['pending_final_route_obligations']==boundary['final_route_obligations']
    assert d['CE12_boundary']['preclaim_external_prerequisites']==boundary['preclaim_external_prerequisites']
    assert d['CE12_boundary']['receipt_only_external_prerequisites']==boundary['receipt_only_external_prerequisites']
    assert len(d['CE12_boundary']['preclaim_external_prerequisites'])==4 and len(d['CE12_boundary']['receipt_only_external_prerequisites'])==1
    assert [r['id'] for r in d['role_scope_matrix']]==['R06','R08']
    assert all(r['canonical_actor_id'] is None and r['accepted_appointment'] is False for r in d['role_scope_matrix'])
    for path in rd(PACK)['$defs']['source_bindings']['required']:
        assert not (ROOT/path).exists()
    for row in rd(CE11)['pending_I177_final_bindings']:
        assert not (ROOT/row['path']).exists()
    for key,value in d['current_effect'].items():
        if key=='W13_documentary_prepared':
            assert value is True
        elif key=='IR03':
            assert value=='NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value==0
        else:
            assert value is False,key
    return dict(schema='d5.i249-preparation-review.v1',increment='I249',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,candidate=pin(SUBJECT),work_package=pin(PLAN,'/work_packages/12'),
        counts=dict(input_pins=1042,prerequisite_packages=12,prelaunch_gates=30,family_gates=7,rule_gates=16,global_gates=7,
            pending_gates=30,accepted_gates=0,separately_deferred_receipt=1,resource_obligations=5,criteria=20,
            typed_reference_templates=69,additional_proof_topics=8,stop_requirements=8,preclaim_external_prerequisites=4,
            receipt_only_external_prerequisites=1,final_bindings=4,unassigned_review_roles=2,pending_exits=3),
        source_reconstruction=dict(I248_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        limitations=['W01-W12 remain unaccepted and SD01 active. Thirty gates are pending, CE12 receipt deferred. This is a truthful negative documentary disposition, not competent R06/R08 acceptance or closed checklist/handoff.',
            'Five obligations/twenty criteria, real proof/body/scope/provider/author/custody/review materials and full source-Reader-guard/resource compatibility remain missing.69 typed templates are not actual/unique body count; zero rejected bodies is not acceptance.',
            'Final execution authorization/E06/payload/Q/root/admission and actual claim/construction/receipt remain separate unfulfilled and unauthorized. They are not new preconditions for accepting prelaunch facts; claim is not its own precondition.',
            'Same-assistant preparation is not independent competent R06 review or R08 acceptance. No product/components/E06/crypto/codec/probes/contacts, quotas/reserves/flags/capture_inputs/authority/destination or D5 changes.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I249-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/gate/criterion/reference/role/handoff checks and in-memory document mutations only. No target imports/compile/discovery/tests/runs/build/E06, positive crypto/codec/signing/keygen/enrollment/provisioning, registry/mapping configuration, clock/CPU/IO/service/platform/ledger/claim/replay/process sampling/probes or contacts.',
            over400_lines=True,reason='One W13 negative30-gate disposition with exact upstream requirements, resource/reference/handoff boundaries, pins, rejection checks and preservation. Overage declared; no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_competent_gate_acceptance_handoff_execution_release_or_D5_closure=True))


def main():
    review=build_review()
    assert rd(PREP)==review
    prior=rd(PRIOR_SEAL)
    preserved={**prior['preserved_published729'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==734
    seal=rd(SEAL)
    assert seal['schema']=='d5.i249-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published734']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==review['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I249',input_pins=1042,preserved_published_files=734,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],SD01_stop_active=True,
        prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
