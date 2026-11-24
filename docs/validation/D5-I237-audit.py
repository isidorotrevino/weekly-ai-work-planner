#!/usr/bin/env python3
"""I237 W07 negative successor work/CPU/unit dossier. Documentary JSON/Git only."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'ca16f4a34a839e2fe16692508f53fee0e0835f74'
DATE = '2026-11-24'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE07 = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
P06 = P+'D5-PFC126-03-E03-WORK-GROUPS.json'
P06_REVIEW = P+'D5-I164-P06-documentary-review.json'
P07 = P+'D5-PFC126-03-E03-E04-COMPATIBILITY.json'
P07_REVIEW = P+'D5-I166-P07-documentary-review.json'
W04 = P+'D5-I223-W04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
W05 = P+'D5-I223-W05-SUCCESSOR-REQUALIFICATION-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
PRIOR_RECON = P+'D5-I236-I235-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I236-I235-documentary-review.json'
PRIOR_AUDIT = P+'D5-I236-audit.py'
PRIOR_SEAL = P+'D5-I236-integrity.json'
PRIOR_DOC = 'docs/design/D5-I236-I235-W06-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I223-W07-SUCCESSOR-WORK-CPU-UNITS-CANDIDATE.json'
PREP = P+'D5-I237-preparation-review.json'
AUDIT = P+'D5-I237-audit.py'
SEAL = P+'D5-I237-integrity.json'
DOC = 'docs/design/D5-I237-W07-SUCCESSOR-WORK-CPU-UNITS.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W07_WORK_CPU_UNITS_MISSING_SD01_ACTIVE_NOT_ADMITTED'


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


def build_candidate():
    plan,contract,p06,p07,join = rd(PLAN),rd(CONTRACT),rd(P06),rd(P07),rd(CE07)
    work = plan['work_packages'][6]
    pins = {**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 982
    inventory = sorted({PLAN,PRIOR_REVIEW,CE01,CE07,CONTRACT,P06,P06_REVIEW,P07,P07_REVIEW,W04,W05,PACK})
    activities = contract['cost_coverage']['activities']
    return dict(schema='d5.i237-w07-successor-work-cpu-units-candidate.v1',increment='I237',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        work_package='W07',planned_deliverable_id=work['deliverable_id'],kind='NEGATIVE_WORK_CPU_UNITS_REQUIREMENT_DOSSIER_NOT_SUCCESSOR_WORK_CENSUS_NOT_WCET_OR_SERVICE_PROOF_NOT_ACCEPTED_REAL_EVIDENCE_PACKAGE',
        status='W07_DOCUMENTARY_PREPARED_COMPLETE_SUCCESSOR_WORK_CPU_WAIT_COMPATIBLE_UNITS_AND_SERVICE_PROOFS_MISSING_SD01_ACTIVE_NOT_ADMITTED',
        input_pins=pins,work_package_binding=pin(PLAN,'/work_packages/6'),required_deliverables=work['deliverables'],required_exit_predicates=work['exit_predicates'],reject_if=work['reject_if'],needs_separate_future_authority_for=work['needs_separate_future_authority_for'],documentary_inventory=[pin(p) for p in inventory],
        dependency_gate=dict(source=pin(PRIOR_REVIEW,'/documentary_clarifications/3'),required_package_ids=work['depends_on'],W01_accepted=False,W02_accepted=False,W03_accepted=False,W04_accepted=False,W05_accepted=False,W06_accepted=False,SD01_stop_active=True,
            actual_entry_authority_or_accepted_effective_baseline=None,documentary_preparation_not_positive_dependency_progress=True),
        role_scope_matrix=[r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R03','R06','R08']],actual_work_WCET_authors_provider_or_review_authority=None,
        all30_successor_correspondence=dict(source=pin(CE07,'/work_join'),exact_requirement='all30 work groups of I193 over the complete effective successor, or a complete genuinely reviewed correspondence preserving that requirement',
            historical_ten_activities_thirty_scalar_slots_twenty_vectors_not_thirty_successor_groups=True,
            no_predictive_group_IDs_or_scope_reduction=True,actual_complete_successor_activity_and_group_inventory=None,actual_all30_group_mapping_and_completeness_derivation=None,
            actual_effective_source_runtime_loader_crypto_caller_platform_ledger_process_scope=None,actual_authors_assumptions_or_review=None,accepted=False),
        historical_activity_obligations=[dict(id=r['id'],source=pin(CONTRACT,'/cost_coverage/activities/'+str(i)),historical_activity=r,
            plan_task=pin(PLAN,'/work_activity_proof_tasks/'+str(i)),actual_successor_source_process_phase_mapping=None,actual_complete_work_upper=None,
            actual_CPU_seconds_upper=None,actual_wall_seconds_upper=None,actual_compatible_work_unit_and_domain=None,actual_full_derivation_body_hash_author_or_review=None,accepted=False) for i,r in enumerate(activities)],
        historical_scalar_slot_obligations=[dict(historical_activity_id=r['id'],source=pin(CONTRACT,'/cost_coverage/activities/'+str(i)+'/'+field),required_kind=kind,
            actual_successor_upper=None,actual_compatible_unit_process_window_or_derivation=None,accepted=False)
            for i,r in enumerate(activities) for field,kind in [('verified_work_upper','WORK'),('verified_CPU_seconds_upper','CPU_SECONDS'),('verified_wall_seconds_upper','WALL_SECONDS')]],
        historical_process_phase_vector_obligations=[dict(id=r['id'],source=pin(P06,'/per_process_phase_work_vectors_and_units/vectors/'+str(i)),historical_requirement=r,
            actual_successor_source_process_thread_child_phase_mapping=None,actual_complete_work_upper=None,actual_compatible_unit=None,actual_WCET_upper_seconds=None,
            actual_wait_upper_seconds=None,actual_scheduler_observation_upper_seconds=None,actual_complete_derivation_or_review=None,accepted=False)
            for i,r in enumerate(p06['per_process_phase_work_vectors_and_units']['vectors'])],
        historical_compatibility_join_obligations=[dict(id=r['id'],source=pin(P07,'/exact_runtime_platform_process_unit_match/joins/'+str(i)),historical_requirement=r,
            actual_exact_runtime_platform_process_domain_and_validity=None,actual_work_unit_rate_latency_or_WCET_match=None,
            actual_conversion_theorem_derivation_body_author_or_review=None,compatible=False,accepted=False)
            for i,r in enumerate(p07['exact_runtime_platform_process_unit_match']['joins'])],
        latency_owner_obligations=[dict(id=r['id'],source=pin(P07,'/latency_owner_map_without_unproved_deductions/owners/'+str(i)),historical_requirement=r,
            actual_successor_latency_owner_process_window_mapping=None,actual_complete_upper_seconds=None,actual_disjoint_or_conservative_overcount_derivation=None,accepted=False)
            for i,r in enumerate(p07['latency_owner_map_without_unproved_deductions']['owners'])],
        phase_category_obligations=[dict(source=pin(P07,'/CPU_IO_child_scheduler_and_native_delay_bounds/per_phase_categories/'+str(i)),historical_requirement=r,
            actual_complete_CPU_wait_scheduler_native_upper_seconds=None,actual_derivation_or_review=None,accepted=False)
            for i,r in enumerate(p07['CPU_IO_child_scheduler_and_native_delay_bounds']['per_phase_categories'])],
        work_service_or_WCET_boundary=dict(source=pin(P07,'/work_to_service_conversion_or_WCET_derivation'),
            required_conditional_routes=p07['work_to_service_conversion_or_WCET_derivation']['conditional_routes'],
            forbidden_shortcuts=p07['work_to_service_conversion_or_WCET_derivation']['forbidden_shortcuts'],
            actual_selected_route=None,actual_complete_whole_window_work=None,actual_work_unit=None,actual_rate_lower_bound=None,actual_rate_unit=None,
            actual_service_latency_upper_seconds=None,actual_static_WCET_upper_seconds=None,actual_full_conversion_theorem_and_assumptions=None,
            workload_arrivals_backlog_readiness_concurrency_service_windows_and_validity_require_justification=True,
            L_plus_W_over_r_only_if_applicable_theorem_complete_work_and_service_premises_proved=True,
            CPU_rate_gives_CPU_execution_not_automatic_wall=True,CPU_sum_wait_and_wall_are_distinct=True,
            no_MHz_cores_quota_frequency_budget_watchdog_or_work_over900_as_service=True,
            no_unproved_parallel_overlap_subtraction_or_double_latency_credit=True),
        scope_and_complete_work_boundary=dict(source=pin(W05,'/coverage_completeness'),exact_W05_closure_requirements=rd(W05)['coverage_completeness'],
            all_original_import_native_crypto_codec_allocation_GC_destruction_locks_IO_children_threads_transitives_and_rejected_routes_required=True,
            function_labels_or_source_counts_not_complete_cost_inventory=True,
            actual_complete_successor_operation_process_phase_inventory_or_no_omission_review=None,
            historical_P06_P07_and_I124_kernel_counts_not_successor_work_WCET_or_infeasibility_proof=True,
            conditional_I124_reference=pin(P06,'/I124_count_transfer_or_refinement'),
            bytes_clones_visits_generations_process_opportunities_not_instructions_or_seconds=True,
            no_33_generation_immediate_GC_or_free_noncopy_tail=True),
        per_attempt_cost_ledger=[dict(source=pin(CE07,'/per_attempt_cost_coverage/required_terms/'+str(i)),required_scope=t,
            actual_successor_operations_units_counts_process_phase_or_derivation=None,actual_complete_upper_or_review=None,accepted=False)
            for i,t in enumerate(join['per_attempt_cost_coverage']['required_terms'])],
        per_attempt_cost_boundary=dict(source=pin(CE07,'/per_attempt_cost_coverage'),exact_required_coverage=join['per_attempt_cost_coverage'],
            both_coordinator_and_worker_Reader_ledgers_and_global_join_required=True,
            input_file_byte_envelopes_not_all_IO_or_CPU_and_snapshots_not_fresh_reads=True,
            every_added_custody_bootstrap_frame_output_ledger_failure_and_cleanup_operation_charged=True,
            offline_enrollment_build_prior_facts_not_free_required_verification=True,
            unknown_work_wait_native_IO_scheduling_or_latency_not_zero=True,actual_complete_global_cost_composition=None),
        actual_whole_work_and_time=dict(whole_work_upper=None,compatible_work_unit=None,whole_CPU_seconds_upper=None,whole_wait_IO_child_upper_seconds=None,
            whole_scheduler_blocking_observation_upper_seconds=None,whole_wall_seconds_upper=None,complete_source_process_window_coverage_derivation=None,verified=False),
        service_dependency=dict(source=pin(W04,'/actual_service_state'),preserved_missing_W04_service=rd(W04)['actual_service_state'],
            actual_same_scope_runtime_platform_service_memory_cache_load_and_unit_compatibility=None,
            W04_service_guarantees_not_selected_or_qualified_here=True),
        interval_and_budget_boundary=dict(source=pin(CONTRACT,'/cost_coverage'),required_interval_rule=contract['cost_coverage']['interval_rule'],
            exact_cost_rules={k:contract['cost_coverage'][k] for k in ['attribution_rule','pre_tR_worker_rule','finally_rule','observation_rule','CPU_wall_rule','noncopy_rule','input_byte_rule']},
            normative_markers=contract['time']['normative_markers'],ordered_interval_rule=contract['time']['ordered_interval_rule'],success_path_qualification=contract['time']['success_path_qualification'],
            worker_pre_main_and_post_RELEASE_receipt_before_parent_tR_must_be_covered=True,
            physical_exit_to_exact_True_wait_return_tW_observation_remains_inside_Tworker=True,
            success_finally_validation_and_dual_writes_to_tF_required=True,
            C10_is_crosscutting_inside_phases_not_free_tail_or_extra_budget=True,
            candidate_phase_budgets=contract['time']['phase_budgets'],candidate_worker_partition=contract['time']['worker_service_partition'],
            required_worker_inequality=p07['worker_category_upper_vector_and_coverage_inequality']['required_inequality'],
            actual_worker_CPU_IO_scheduler_vector=None,actual_worker_verified_sum_seconds=None,actual_worker_inequality_proved=False,
            actual_all_success_phase_uppers_or900_derivation=None,
            candidate_end_to_end_seconds=900,candidate_unassigned_reserve_seconds=30,
            no_extra_600_for_C04_Tpre_or_per_group_process_thread_window_category=True,
            reserve_accounting=contract['reserve_accounting'],reserve_transfers_applied=0,resources_reserved=False,quotas_or_budgets_changed=False),
        phase_handoff=dict(source=pin(PLAN,'/scope_authentication_and_freeze_order'),exact_plan_order=plan['scope_authentication_and_freeze_order'],
            W05_work_handoff=pin(W05,'/resource_handoff/1'),W08_consumer=pin(PLAN,'/work_packages/7'),W09_joint_acceptance=pin(PLAN,'/work_packages/8'),
            W06_memory_and_W07_work_are_parallel_inputs_to_W08_without_reverse_baseline_dependency=True,
            memory_cache_allocator_interference_assumptions_must_be_reconciled_and_justified_not_automatically_borrowed=True,
            W07_does_not_prove_W06_heap_or_W08_success900_or_W09_E01_E05_acceptance=True,
            genuine_effective_baseline_known_authors_bodies_assumptions_before_W09_required=True,
            W10_freeze_reconciles_same_facts_and_changes_invalidate_affected_bounds=True,
            final_freeze_C_mapping_E06_payload_Q_root_claim_receipt_not_sole_antecedent_proof=True,
            final_route_boundary=plan['prelaunch_handoff_and_CE12'],actual_positive_work_service_BASIS_index_proof_record_created=False,actual_refresh_or_active_rebind=False),
        authority_boundary=dict(source=pin(PLAN,'/authorization_boundary'),inherited_boundary=plan['authorization_boundary'],
            allowed_now=['READ_DOCUMENTS_GIT_HASHES_AND_EXACT_PATH_PRESENCE','PREPARE_THIS_NEGATIVE_DOSSIER','RUN_OWN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT'],
            no_product_components_import_compile_test_discovery_WCET_experiment_benchmarks_probes_schedule_or_service_sampling=True,
            no_new_helpers_Reader_members_inputs_outputs_channels_clock_ledger_claim_signing_keygen_enrollment_provider_contacts=True,
            actual_external_material_provider_authority_or_measurement=None),
        exit_predicate_dispositions=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/6/exit_predicates/'+str(i)),predicate=t,documentary_requirements_prepared=True,actual_evidence=None,actual_primary_R03_R06_review=None,actual_separate_R08_acceptance=None,accepted=False) for i,t in enumerate(work['exit_predicates'])],
        preserved_scope_and_gates=dict(inherited_scope_boundaries=plan['inherited_scope_boundaries'],preserved_negative_gates=plan['preserved_negative_gates'],prelaunch_handoff_and_CE12=plan['prelaunch_handoff_and_CE12']),
        current_effect=dict(W07_documentary_prepared=True,W01_accepted=False,W02_accepted=False,W03_accepted=False,W04_accepted=False,W05_accepted=False,W06_accepted=False,W07_accepted=False,actual_entry_authority_verified=False,
            actual_complete_successor_work_CPU_wait_units_service_WCET_or_phase_fit_verified=False,actual_real_evidence_package_created=False,positive_I191_or_BASIS_index_work_proof_record_created=False,
            actual_evidence_accepted=0,work_packages_accepted=0,prelaunch_gates_closed=0,resource_obligations_closed=0,
            independent_acceptance=False,source_implementation_changed=False,product_or_components_executed=False,quotas_changed=False,reserves_changed=False,resource_reservations_created=False,rebind_applied=False,authority_or_destination_created=False,actual_claim_worker_or_receipt_created=False,
            execution_authorized=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),
        producer=dict(identity='Same Codex assistant/chat as I235/I236',documentary_preparer_only=True,actor_independent=False,competent_R03_review=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_work_WCET_service_attestation_or_execution_authority=True))


def validate(d):
    assert d['dependency_gate']['SD01_stop_active'] is True and all(d['dependency_gate'][k] is False for k in ['W03_accepted','W04_accepted','W05_accepted']), 'dependency_bypass'
    assert d['current_effect']['W07_accepted'] is False, 'W07_accepted'
    assert d['all30_successor_correspondence']['historical_ten_activities_thirty_scalar_slots_twenty_vectors_not_thirty_successor_groups'], 'count_equivalence'
    assert d['all30_successor_correspondence']['actual_all30_group_mapping_and_completeness_derivation'] is None, 'invented_group_mapping'
    assert all(r['actual_successor_upper'] is None for r in d['historical_scalar_slot_obligations']), 'unknown_upper_zero'
    assert all(r['compatible'] is False for r in d['historical_compatibility_join_obligations']), 'invented_compatibility'
    assert d['work_service_or_WCET_boundary']['actual_selected_route'] is None, 'invented_route'
    assert d['work_service_or_WCET_boundary']['actual_rate_lower_bound'] is None, 'invented_rate'
    assert d['work_service_or_WCET_boundary']['actual_service_latency_upper_seconds'] is None, 'unknown_latency_zero'
    assert d['work_service_or_WCET_boundary']['L_plus_W_over_r_only_if_applicable_theorem_complete_work_and_service_premises_proved'], 'naive_division'
    assert d['work_service_or_WCET_boundary']['CPU_rate_gives_CPU_execution_not_automatic_wall'], 'CPU_rate_as_wall'
    assert d['work_service_or_WCET_boundary']['CPU_sum_wait_and_wall_are_distinct'], 'CPU_sum_as_wall'
    assert d['work_service_or_WCET_boundary']['no_MHz_cores_quota_frequency_budget_watchdog_or_work_over900_as_service'], 'budget_as_service'
    assert d['work_service_or_WCET_boundary']['no_unproved_parallel_overlap_subtraction_or_double_latency_credit'], 'unproved_overlap'
    assert d['scope_and_complete_work_boundary']['bytes_clones_visits_generations_process_opportunities_not_instructions_or_seconds'], 'abstract_count_as_seconds'
    assert d['scope_and_complete_work_boundary']['no_33_generation_immediate_GC_or_free_noncopy_tail'], 'free_noncopy_tail'
    assert d['per_attempt_cost_boundary']['both_coordinator_and_worker_Reader_ledgers_and_global_join_required'], 'omitted_Reader'
    assert d['per_attempt_cost_boundary']['every_added_custody_bootstrap_frame_output_ledger_failure_and_cleanup_operation_charged'], 'omitted_new_path'
    assert d['per_attempt_cost_boundary']['offline_enrollment_build_prior_facts_not_free_required_verification'], 'offline_free'
    assert d['interval_and_budget_boundary']['worker_pre_main_and_post_RELEASE_receipt_before_parent_tR_must_be_covered'], 'worker_all_Tworker'
    assert d['interval_and_budget_boundary']['physical_exit_to_exact_True_wait_return_tW_observation_remains_inside_Tworker'], 'physical_exit_as_tW'
    assert d['interval_and_budget_boundary']['success_finally_validation_and_dual_writes_to_tF_required'], 'finish_as_tF'
    assert d['interval_and_budget_boundary']['no_extra_600_for_C04_Tpre_or_per_group_process_thread_window_category'], 'extra_CPU_budget'
    assert d['interval_and_budget_boundary']['actual_worker_inequality_proved'] is False, 'candidate_as_proved_inequality'
    assert d['interval_and_budget_boundary']['reserve_transfers_applied'] == 0, 'reserve_transfer'
    assert d['phase_handoff']['W06_memory_and_W07_work_are_parallel_inputs_to_W08_without_reverse_baseline_dependency'], 'reverse_dependency'
    assert d['phase_handoff']['W07_does_not_prove_W06_heap_or_W08_success900_or_W09_E01_E05_acceptance'], 'premature_resources'
    assert d['phase_handoff']['genuine_effective_baseline_known_authors_bodies_assumptions_before_W09_required'], 'late_authentication'
    assert d['phase_handoff']['final_freeze_C_mapping_E06_payload_Q_root_claim_receipt_not_sole_antecedent_proof'], 'future_final_as_proof'
    assert d['authority_boundary']['no_product_components_import_compile_test_discovery_WCET_experiment_benchmarks_probes_schedule_or_service_sampling'], 'implicit_benchmark'
    assert d['interval_and_budget_boundary']['quotas_or_budgets_changed'] is False, 'quota_change'
    assert all(r['accepted'] is False for r in d['exit_predicate_dispositions']), 'exit_acceptance'
    assert d['current_effect']['D5_closed'] is False, 'D5_closed'
    assert d == build_candidate(), 'Candidate differs from source reconstruction'
    check_pointers(d)


def rejection_checks(d):
    cases = [
        ('dependency_bypass',('dependency_gate','SD01_stop_active'),False),('W07_accepted',('current_effect','W07_accepted'),True),
        ('count_equivalence',('all30_successor_correspondence','historical_ten_activities_thirty_scalar_slots_twenty_vectors_not_thirty_successor_groups'),False),
        ('invented_group_mapping',('all30_successor_correspondence','actual_all30_group_mapping_and_completeness_derivation'),'UNVERIFIED_TEST_LABEL_NOT_GROUP_MAPPING'),
        ('unknown_upper_zero',('historical_scalar_slot_obligations',0,'actual_successor_upper'),0),
        ('invented_compatibility',('historical_compatibility_join_obligations',0,'compatible'),True),
        ('invented_route',('work_service_or_WCET_boundary','actual_selected_route'),'UNSELECTED_TEST_LABEL_NOT_ROUTE'),
        ('invented_rate',('work_service_or_WCET_boundary','actual_rate_lower_bound'),1),
        ('unknown_latency_zero',('work_service_or_WCET_boundary','actual_service_latency_upper_seconds'),0),
        ('naive_division',('work_service_or_WCET_boundary','L_plus_W_over_r_only_if_applicable_theorem_complete_work_and_service_premises_proved'),False),
        ('CPU_rate_as_wall',('work_service_or_WCET_boundary','CPU_rate_gives_CPU_execution_not_automatic_wall'),False),
        ('CPU_sum_as_wall',('work_service_or_WCET_boundary','CPU_sum_wait_and_wall_are_distinct'),False),
        ('budget_as_service',('work_service_or_WCET_boundary','no_MHz_cores_quota_frequency_budget_watchdog_or_work_over900_as_service'),False),
        ('unproved_overlap',('work_service_or_WCET_boundary','no_unproved_parallel_overlap_subtraction_or_double_latency_credit'),False),
        ('abstract_count_as_seconds',('scope_and_complete_work_boundary','bytes_clones_visits_generations_process_opportunities_not_instructions_or_seconds'),False),
        ('free_noncopy_tail',('scope_and_complete_work_boundary','no_33_generation_immediate_GC_or_free_noncopy_tail'),False),
        ('omitted_Reader',('per_attempt_cost_boundary','both_coordinator_and_worker_Reader_ledgers_and_global_join_required'),False),
        ('omitted_new_path',('per_attempt_cost_boundary','every_added_custody_bootstrap_frame_output_ledger_failure_and_cleanup_operation_charged'),False),
        ('offline_free',('per_attempt_cost_boundary','offline_enrollment_build_prior_facts_not_free_required_verification'),False),
        ('worker_all_Tworker',('interval_and_budget_boundary','worker_pre_main_and_post_RELEASE_receipt_before_parent_tR_must_be_covered'),False),
        ('physical_exit_as_tW',('interval_and_budget_boundary','physical_exit_to_exact_True_wait_return_tW_observation_remains_inside_Tworker'),False),
        ('finish_as_tF',('interval_and_budget_boundary','success_finally_validation_and_dual_writes_to_tF_required'),False),
        ('extra_CPU_budget',('interval_and_budget_boundary','no_extra_600_for_C04_Tpre_or_per_group_process_thread_window_category'),False),
        ('candidate_as_proved_inequality',('interval_and_budget_boundary','actual_worker_inequality_proved'),True),
        ('reserve_transfer',('interval_and_budget_boundary','reserve_transfers_applied'),1),
        ('reverse_dependency',('phase_handoff','W06_memory_and_W07_work_are_parallel_inputs_to_W08_without_reverse_baseline_dependency'),False),
        ('premature_resources',('phase_handoff','W07_does_not_prove_W06_heap_or_W08_success900_or_W09_E01_E05_acceptance'),False),
        ('late_authentication',('phase_handoff','genuine_effective_baseline_known_authors_bodies_assumptions_before_W09_required'),False),
        ('future_final_as_proof',('phase_handoff','final_freeze_C_mapping_E06_payload_Q_root_claim_receipt_not_sole_antecedent_proof'),False),
        ('implicit_benchmark',('authority_boundary','no_product_components_import_compile_test_discovery_WCET_experiment_benchmarks_probes_schedule_or_service_sampling'),False),
        ('quota_change',('interval_and_budget_boundary','quotas_or_budgets_changed'),True),
        ('exit_acceptance',('exit_predicate_dispositions',0,'accepted'),True),('D5_closed',('current_effect','D5_closed'),True)]
    result = []
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
            result.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return result


def build_review():
    d = rd(SUBJECT)
    verify_blobs(d['input_pins'])
    validate(d)
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    exists = Path.exists
    rec = previous['reconstruct']()
    assert rec == rd(PRIOR_RECON) and previous['build_review'](rec) == rd(PRIOR_REVIEW)
    assert Path.exists is exists
    assert len(d['historical_activity_obligations']) == 10 and len(d['historical_scalar_slot_obligations']) == 30
    assert len({(r['historical_activity_id'],r['required_kind']) for r in d['historical_scalar_slot_obligations']}) == 30
    for row in d['historical_activity_obligations']:
        assert row['historical_activity'] == fragment(row['source'])
        assert fragment(row['plan_task'])['id'] == row['id']
    for row in d['historical_scalar_slot_obligations']:
        assert fragment(row['source']) is None
    assert len(d['historical_process_phase_vector_obligations']) == 20 and len(d['historical_compatibility_join_obligations']) == 20
    assert [r['id'] for r in d['historical_process_phase_vector_obligations']] == [r['id'] for r in d['historical_compatibility_join_obligations']]
    assert len(d['latency_owner_obligations']) == 10 and len(d['phase_category_obligations']) == 9 and len(d['per_attempt_cost_ledger']) == 7
    for key in ['historical_activity_obligations','historical_scalar_slot_obligations','historical_process_phase_vector_obligations','historical_compatibility_join_obligations','latency_owner_obligations','phase_category_obligations','per_attempt_cost_ledger']:
        for row in d[key]:
            assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
            if 'historical_requirement' in row:
                assert row['historical_requirement'] == fragment(row['source'])
    assert all(v is None or v is False for v in d['actual_whole_work_and_time'].values())
    assert d['all30_successor_correspondence']['accepted'] is False
    assert [r['id'] for r in d['role_scope_matrix']] == ['R03','R06','R08']
    assert all(r['canonical_actor_id'] is None and r['accepted_appointment'] is False for r in d['role_scope_matrix'])
    for path in rd(PACK)['$defs']['source_bindings']['required']:
        assert not (ROOT/path).exists()
    for key,value in d['current_effect'].items():
        if key == 'W07_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False, key
    return dict(schema='d5.i237-preparation-review.v1',increment='I237',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,candidate=pin(SUBJECT),work_package=pin(PLAN,'/work_packages/6'),
        counts=dict(input_pins=982,historical_activities=10,historical_scalar_slots=30,historical_process_phase_vectors=20,historical_compatibility_joins=20,latency_owner_requirements=10,phase_category_requirements=9,per_attempt_cost_families=7,unassigned_review_roles=3,pending_exits=3),
        source_reconstruction=dict(I236_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        limitations=['W01-W06 remain unaccepted and SD01 active. W07 is negative documentary preparation, not a successor work inventory, full bound, unit-compatibility/service/WCET proof or actual accepted package.',
            'Ten historical activities/thirty scalar upper slots/twenty process-phase vectors do not establish all30 successor groups. Actual complete mapping, work/CPU/wait/wall/native/transitive cost, compatible units/rates/windows/backlog and derivations remain absent.',
            'W04 service is not attested; no service/WCET route is selected. W06 memory and W07 work feed W08/W09 without extra budgets, quota/reserve transfers, success900 or E01-E05 acceptance. Final route and CE12 stay separate.',
            'Same assistant checks do not satisfy independent R03/R06 review or separate R08 acceptance. No product/component execution, import/compile/test discovery, experimental WCET, benchmarks, schedule/service/platform sampling or probes occur.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I237-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/activity/vector/unit/phase checks only; no product/components imports/build/compile/test discovery/tests/benchmarks, experimental WCET/CPU/IO/service/platform/clock/schedule sampling/probes, codec/crypto positives, ledger/claim/process/signing/keygen/enrollment/provisioning/services/contact.',
            over400_lines=True,reason='One W07 negative work/CPU/unit dossier with exact activity/scalar/vector/join/latency requirements, conversion/phase/handoff rules, pins/checks and preservation; overage declared. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_work_WCET_service_attestation_or_execution_authority=True))


def main():
    review = build_review()
    assert rd(PREP) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published669'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 674
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i237-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published674'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == review['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I237',historical_pins=982,preserved_published_files=674,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],current_effect=review['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
