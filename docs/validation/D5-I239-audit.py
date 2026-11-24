#!/usr/bin/env python3
"""I239 W08 negative phase-bound dossier. Own documentary JSON/Git/algebra only."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '7722e3ed2b5965ff0043583efbbe3b05ffe7719f'
DATE = '2026-11-24'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE07 = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
P08 = P+'D5-PFC126-03-E05-PHASE-BOUNDS.json'
P08_REVIEW = P+'D5-I168-P08-documentary-review.json'
W04 = P+'D5-I223-W04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
W05 = P+'D5-I223-W05-SUCCESSOR-REQUALIFICATION-CANDIDATE.json'
W06 = P+'D5-I223-W06-SUCCESSOR-HEAP-LIFETIMES-CANDIDATE.json'
W07 = P+'D5-I223-W07-SUCCESSOR-WORK-CPU-UNITS-CANDIDATE.json'
W06_REVIEW = P+'D5-I236-I235-documentary-review.json'
PRIOR_RECON = P+'D5-I238-I237-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I238-I237-documentary-review.json'
PRIOR_AUDIT = P+'D5-I238-audit.py'
PRIOR_SEAL = P+'D5-I238-integrity.json'
PRIOR_DOC = 'docs/design/D5-I238-I237-W07-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
SUBJECT = P+'D5-I223-W08-SUCCESSOR-PHASE-BOUNDS-CANDIDATE.json'
PREP = P+'D5-I239-preparation-review.json'
AUDIT = P+'D5-I239-audit.py'
SEAL = P+'D5-I239-integrity.json'
DOC = 'docs/design/D5-I239-W08-SUCCESSOR-PHASE-BOUNDS.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W08_PHASE_BOUNDS_MISSING_SD01_ACTIVE_NOT_ADMITTED'


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


def phase_algebra():
    # Coefficients are formal endpoint differences, not measured timestamps.
    endpoints = ['t0','tR','tW','tF']
    vectors = []
    for i in range(3):
        row = [0]*4
        row[i], row[i+1] = -1, 1
        vectors.append(row)
    total = [sum(v[i] for v in vectors) for i in range(4)]
    assert total == [-1,0,0,1]
    return dict(marker_order=endpoints,phase_difference_coefficients=vectors,telescoped_coefficients=total,
        symbolic_identity='(tR-t0)+(tW-tR)+(tF-tW)=tF-t0',formal_identity_verified=True,
        actual_marker_order_or_nonnegativity_verified=False,actual_complete_temporal_coverage_verified=False,
        actual_successful_execution_existence_or_liveness_verified=False)


def build_candidate():
    plan, contract, historical, work = rd(PLAN), rd(CONTRACT), rd(P08), rd(W07)
    w, time = plan['work_packages'][7], contract['time']
    pins = {**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 992
    inventory = [PLAN,CONTRACT,CE01,CE07,P08,P08_REVIEW,W04,W05,W06,W07,W06_REVIEW,PRIOR_REVIEW,PACK]
    assert all(p in pins and pins[p] == sha(p) for p in inventory)
    return dict(schema='d5.i239-w08-successor-phase-bounds-candidate.v1',increment='I239',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        work_package='W08',planned_deliverable_id=w['deliverable_id'],
        kind='NEGATIVE_PHASE_BOUND_REQUIREMENT_DOSSIER_NOT_SUCCESS900_PROOF_NOT_ACCEPTED_REAL_EVIDENCE_PACKAGE',
        status='W08_DOCUMENTARY_PREPARED_COMPLETE_SUCCESSOR_PHASE_BOUNDS_AND_LIVENESS_MISSING_SD01_ACTIVE_NOT_ADMITTED',
        input_pins=pins,work_package_binding=pin(PLAN,'/work_packages/7'),required_deliverables=w['deliverables'],
        required_exit_predicates=w['exit_predicates'],reject_if=w['reject_if'],needs_separate_future_authority_for=w['needs_separate_future_authority_for'],
        documentary_inventory=[pin(p) for p in sorted(inventory)],
        dependency_gate=dict(source=pin(PLAN,'/work_packages/7/depends_on'),required_package_ids=w['depends_on'],
            W01_accepted=False,W02_accepted=False,W03_accepted=False,W04_accepted=False,W05_accepted=False,W06_accepted=False,W07_accepted=False,
            SD01_stop_active=True,actual_entry_authority_or_accepted_effective_baseline=None,
            documentary_preparation_and_review_not_actual_dependency_acceptance=True),
        role_scope_matrix=[r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R03','R06','R08']],
        authorship_boundary=dict(required_provider_kind=w['provider_kind'],required_primary_roles=w['primary_review_roles'],required_separate_acceptor_role=w['separate_acceptor_role'],
            actual_temporal_proof_author_or_service_guarantor=None,actual_appointments_competence_or_authority=None,
            actual_R03_R06_review=None,actual_separate_R08_acceptance=None,accepted=False),
        historical_reference_boundary=dict(source=pin(P08),review=pin(P08_REVIEW),
            historical_P08_is_conditional_dossier_not_successor_timing_proof=True,
            old_I122_source_anchors_do_not_bind_effective_successor=True,
            historical_process_vector_labels_not_actual_PIDs_or_all30_successor_inventory=True,
            no_historical_counts_or_old_acceptance_as_successor_bound=True,
            actual_successor_source_runtime_loader_crypto_caller_platform_ledger_process_binding=None),
        clock_and_marker_obligations=dict(source=pin(CONTRACT,'/time'),required_clock_domain=time['clock'],
            marker_ledger=[dict(id=r['id'],source=pin(CONTRACT,'/time/normative_markers/'+str(i)),historical_definition=r,
                actual_successor_event_and_source_binding=None,actual_clock_identity_domain_unit_resolution_and_guarantees=None,
                actual_marker_value=None,actual_derivation_or_review=None,accepted=False) for i,r in enumerate(time['normative_markers'])],
            ordered_interval_rule=time['ordered_interval_rule'],observation_latency_rule=time['observation_latency_rule'],
            forbidden_marker_substitutions=time['forbidden_marker_substitutions'],
            no_worker_receipt_or_physical_exit_or_later_validation_as_coordinator_marker=True,
            actual_common_monotonic_clock_or_order_proof=None,clock_sampled=False,markers_instrumented=False),
        formal_phase_algebra=phase_algebra(),
        phase_derivation_ledger=[dict(id=r['id'],source=pin(CONTRACT,'/time/phase_budgets/'+str(i)),historical_phase_requirement=r,
            candidate_wall_seconds=r['candidate_wall_seconds'],
            historical_W07_vector_requirements=[pin(W07,'/historical_process_phase_vector_obligations/'+str(j)) for j,v in enumerate(work['historical_process_phase_vector_obligations']) if v['historical_requirement']['phase']==r['id']],
            historical_W07_compatibility_requirements=[pin(W07,'/historical_compatibility_join_obligations/'+str(j)) for j,v in enumerate(work['historical_compatibility_join_obligations']) if v['historical_requirement']['phase']==r['id']],
            actual_complete_successor_operations_processes_and_phase_mapping=None,
            actual_complete_work_CPU_wait_IO_children_locks_dispatch_observation_native_GC_destruction_bound=None,
            actual_same_scope_heap_memory_cache_load_units_clock_service_or_WCET_and_liveness_proof=None,
            actual_finite_wall_upper_seconds=None,actual_derivation_body_hash_author_and_review=None,
            complete_coverage_verified=False,accepted=False) for i,r in enumerate(time['phase_budgets'])],
        historical_conditional_premise_obligations=[dict(id=r['id'],source=pin(P08,'/verified_Tpre_Tworker_Tpost_upper_seconds/conditional_theorem/premises/'+str(i)),historical_requirement=r,
            actual_complete_successor_premise_proof_and_authors=None,satisfied=False)
            for i,r in enumerate(historical['verified_Tpre_Tworker_Tpost_upper_seconds']['conditional_theorem']['premises'])],
        successor_premise_handoff=dict(W04_service_and_clock=pin(W04,'/actual_service_state'),W05_complete_scope=pin(W05,'/coverage_completeness'),
            W06_heap_fit=pin(W06,'/availability_and_fit'),W07_complete_work=pin(W07,'/actual_whole_work_and_time'),
            W07_compatible_service_or_WCET=pin(W07,'/work_service_or_WCET_boundary'),W07_per_attempt_costs=pin(W07,'/per_attempt_cost_boundary'),
            all30_successor_work_correspondence_required_without_ten_activity_shortcut=True,
            both_Reader_ledgers_global_join_and_every_added_identity_crypto_frame_custody_output_failure_cleanup_cost_required=True,
            genuine_same_scope_memory_allocator_cache_load_service_units_and_validity_must_be_justified_and_reconciled=True,
            complete_original_native_children_threads_transitives_rejection_prefix_and_traceback_heap_scope_preserved=True,
            actual_compatible_complete_premise_join=None,actual_independent_premise_acceptance=None),
        interval_coverage=dict(source=pin(CONTRACT,'/cost_coverage'),exact_interval_rule=contract['cost_coverage']['interval_rule'],
            exact_cost_rules={k:contract['cost_coverage'][k] for k in ['attribution_rule','pre_tR_worker_rule','finally_rule','observation_rule','CPU_wall_rule','noncopy_rule','input_byte_rule']},
            worker_startup_before_main_and_post_RELEASE_receipt_before_parent_close_tR_must_be_covered_in_Tpre=True,
            physical_exit_to_exact_True_wait_return_tW_stays_in_Tworker_even_if_already_exited=True,
            cleanup_fresh_after_finish_validation_finally_dual_writes_and_closes_through_normal_tF_required=True,
            C10_crosscutting_inside_phases_not_free_tail_or_extra_budget=True,
            no_unproved_parallel_overlap_subtraction_or_CPU_sum_as_wall=True,
            actual_complete_no_gap_attribution_and_latency_derivation=None),
        qualified_success_boundary=dict(source=pin(CONTRACT,'/time/success_path_qualification'),exact_qualification=time['success_path_qualification'],
            failure_claim=time['failure_claim'],
            True_is_necessary_not_sufficient_for_success=True,later_checks_do_not_move_tW=True,
            False_exception_timeout_nonzero_exit_rejection_invalid_finalization_not_qualified_success=True,
            all_four_actual_markers_and_independent_success_checks_required=True,
            no_missing_marker_or_unknown_upper_coerced_to_zero=True,
            conditional_implication_not_existence_or_liveness_proof=True,
            termination_progress_IO_lock_scheduler_retry_signal_and_environment_assumptions_require_justification=True,
            no_every_failure_or_cleanup_within900_claim=True,
            success_only_timing_does_not_omit_failure_costs_or_rejection_traceback_heap_requirements=True,
            actual_success_eligibility_and_liveness_derivation=None,actual_all_failure_cleanup_deadline=None),
        time_and_reserve_account=dict(source=pin(CONTRACT,'/reserve_accounting'),exact_candidate_rules=contract['reserve_accounting'],
            candidate_phase_seconds=[r['candidate_wall_seconds'] for r in time['phase_budgets']],candidate_phase_sum_seconds=870,
            candidate_unassigned_reserve_seconds=time['unassigned_wall_reserve_seconds'],candidate_total_seconds=time['success_end_to_end_candidate_seconds'],
            candidate_worker_partition=time['worker_service_partition'],
            required_worker_inequality=work['interval_and_budget_boundary']['required_worker_inequality'],
            conditional_conclusion='If compatible complete premises and qualified normal success with verified phase bounds hold, tF-t0<=60+750+60=870<=900; unassigned30 is not proof or automatic spending permission.',
            no_extra_600_per_C04_group_process_thread_window_or_category=True,no_null_paid_by_reserve_or_double_outer_nested_credit=True,
            candidate_arithmetic_not_verified_service_capacity_or_success_bound=True,
            actual_phase_uppers=None,actual_worker_category_vector_or_verified_sum=None,actual_end_to_end_upper_seconds=None,
            actual_success900_proved=False,actual_infeasibility_proved=False,
            time_reserve_transfers_applied=0,nested_category_transfers_applied=0,heap_reserve_transfers_applied=0,
            resources_reserved=False,quotas_or_budgets_changed=False),
        watchdog_boundary=dict(source=pin(CONTRACT,'/time/current_source_watchdog'),historical_watchdog=time['current_source_watchdog'],
            process_wait900_not_end_to_end_deadline_or_success_liveness_guarantee=True,new_timer_or_clock_rule_installed=False),
        phase_handoff=dict(source=pin(PLAN,'/scope_authentication_and_freeze_order'),exact_plan_order=plan['scope_authentication_and_freeze_order'],
            W06_and_W07_parallel_inputs_to_W08_not_reverse_dependencies=True,
            W08_does_not_qualify_missing_W04_W05_W06_W07_or_accept_W09_E01_E05=True,
            W09_joint_acceptance=pin(PLAN,'/work_packages/8'),genuine_baseline_authors_proof_bodies_assumptions_required_before_W09=True,
            W10_freeze_reconciles_same_facts_changes_invalidate_affected_proofs=True,
            final_C_mapping_E06_payload_Q_root_claim_receipt_not_sole_antecedent_proof=True,
            final_route_boundary=plan['prelaunch_handoff_and_CE12'],actual_positive_phase_BASIS_index_record_created=False,actual_refresh_or_rebind=False),
        authority_boundary=dict(source=pin(PLAN,'/authorization_boundary'),inherited_boundary=plan['authorization_boundary'],
            allowed_now=['READ_DOCUMENTS_GIT_HASHES_AND_EXACT_PATH_PRESENCE','PREPARE_NEGATIVE_PHASE_DOSSIER','RUN_OWN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT'],
            no_product_components_import_compile_discovery_tests_experimental_WCET_benchmarks_probes_clock_CPU_IO_schedule_service_or_platform_sampling=True,
            no_helpers_Reader_members_channels_inputs_outputs_ledger_claim_signing_keygen_enrollment_provisioning_or_contacts=True,
            actual_external_authority_material_measurement_or_contact=None),
        exit_predicate_dispositions=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/7/exit_predicates/'+str(i)),predicate=t,
            documentary_requirements_prepared=True,actual_evidence=None,actual_R03_R06_review=None,actual_separate_R08_acceptance=None,accepted=False) for i,t in enumerate(w['exit_predicates'])],
        preserved_scope_and_gates={k:plan[k] for k in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']},
        current_effect={**{k:v for k,v in work['current_effect'].items() if k!='W07_documentary_prepared'},
            'W08_documentary_prepared':True,'W08_accepted':False,'actual_complete_phase_bounds_or_success900_verified':False},
        producer=dict(identity='Same Codex assistant/chat as I237/I238',documentary_preparer_only=True,actor_independent=False,
            competent_R03_review=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_temporal_service_attestation_acceptance_or_execution_authority=True))


# Expected values are requirements of this negative dossier, not runtime bounds.
NEGATIVE_CASES = [
    ('SD01_bypass',('dependency_gate','SD01_stop_active'),True,False),
    ('W08_acceptance',('current_effect','W08_accepted'),False,True),
    ('historical_proof_transfer',('historical_reference_boundary','historical_P08_is_conditional_dossier_not_successor_timing_proof'),True,False),
    ('old_anchor_successor_binding',('historical_reference_boundary','old_I122_source_anchors_do_not_bind_effective_successor'),True,False),
    ('invented_timestamp',('clock_and_marker_obligations','marker_ledger',0,'actual_marker_value'),None,0),
    ('invented_clock',('clock_and_marker_obligations','actual_common_monotonic_clock_or_order_proof'),None,'UNVERIFIED_TEST_LABEL'),
    ('clock_sampling',('clock_and_marker_obligations','clock_sampled'),False,True),
    ('formal_algebra_as_order',('formal_phase_algebra','actual_marker_order_or_nonnegativity_verified'),False,True),
    ('unknown_phase_zero',('phase_derivation_ledger',0,'actual_finite_wall_upper_seconds'),None,0),
    ('invented_premise',('historical_conditional_premise_obligations',0,'satisfied'),False,True),
    ('ten_as_all30',('successor_premise_handoff','all30_successor_work_correspondence_required_without_ten_activity_shortcut'),True,False),
    ('omitted_Reader_costs',('successor_premise_handoff','both_Reader_ledgers_global_join_and_every_added_identity_crypto_frame_custody_output_failure_cleanup_cost_required'),True,False),
    ('borrowed_memory_premises',('successor_premise_handoff','genuine_same_scope_memory_allocator_cache_load_service_units_and_validity_must_be_justified_and_reconciled'),True,False),
    ('pre_tR_worker_gap',('interval_coverage','worker_startup_before_main_and_post_RELEASE_receipt_before_parent_close_tR_must_be_covered_in_Tpre'),True,False),
    ('exit_to_wait_gap',('interval_coverage','physical_exit_to_exact_True_wait_return_tW_stays_in_Tworker_even_if_already_exited'),True,False),
    ('finally_omitted',('interval_coverage','cleanup_fresh_after_finish_validation_finally_dual_writes_and_closes_through_normal_tF_required'),True,False),
    ('free_C10',('interval_coverage','C10_crosscutting_inside_phases_not_free_tail_or_extra_budget'),True,False),
    ('CPU_as_wall',('interval_coverage','no_unproved_parallel_overlap_subtraction_or_CPU_sum_as_wall'),True,False),
    ('True_as_success',('qualified_success_boundary','True_is_necessary_not_sufficient_for_success'),True,False),
    ('later_validation_tW',('qualified_success_boundary','later_checks_do_not_move_tW'),True,False),
    ('timeout_as_success',('qualified_success_boundary','False_exception_timeout_nonzero_exit_rejection_invalid_finalization_not_qualified_success'),True,False),
    ('missing_marker_zero',('qualified_success_boundary','no_missing_marker_or_unknown_upper_coerced_to_zero'),True,False),
    ('vacuous_liveness',('qualified_success_boundary','conditional_implication_not_existence_or_liveness_proof'),True,False),
    ('failure_deadline',('qualified_success_boundary','no_every_failure_or_cleanup_within900_claim'),True,False),
    ('failure_heap_omitted',('qualified_success_boundary','success_only_timing_does_not_omit_failure_costs_or_rejection_traceback_heap_requirements'),True,False),
    ('extra_CPU600',('time_and_reserve_account','no_extra_600_per_C04_group_process_thread_window_or_category'),True,False),
    ('reserve_payment_unknown',('time_and_reserve_account','no_null_paid_by_reserve_or_double_outer_nested_credit'),True,False),
    ('budget_sum_as_proof',('time_and_reserve_account','candidate_arithmetic_not_verified_service_capacity_or_success_bound'),True,False),
    ('invented_success900',('time_and_reserve_account','actual_success900_proved'),False,True),
    ('reserve_transfer',('time_and_reserve_account','time_reserve_transfers_applied'),0,1),
    ('nested_transfer',('time_and_reserve_account','nested_category_transfers_applied'),0,1),
    ('quota_change',('time_and_reserve_account','quotas_or_budgets_changed'),False,True),
    ('watchdog_guarantee',('watchdog_boundary','process_wait900_not_end_to_end_deadline_or_success_liveness_guarantee'),True,False),
    ('premature_W09',('phase_handoff','W08_does_not_qualify_missing_W04_W05_W06_W07_or_accept_W09_E01_E05'),True,False),
    ('late_authentication',('phase_handoff','genuine_baseline_authors_proof_bodies_assumptions_required_before_W09'),True,False),
    ('future_final_as_proof',('phase_handoff','final_C_mapping_E06_payload_Q_root_claim_receipt_not_sole_antecedent_proof'),True,False),
    ('implicit_execution',('authority_boundary','no_product_components_import_compile_discovery_tests_experimental_WCET_benchmarks_probes_clock_CPU_IO_schedule_service_or_platform_sampling'),True,False),
    ('exit_accepted',('exit_predicate_dispositions',0,'accepted'),False,True),
    ('D5_closed',('current_effect','D5_closed'),False,True)]


def validate(d):
    for name,path,expected,_ in NEGATIVE_CASES:
        node = d
        for key in path:
            node = node[key]
        assert type(node) is type(expected) and node == expected, name
    assert d == build_candidate(), 'Candidate differs from source reconstruction'
    check_pointers(d)


def rejection_checks(d):
    results = []
    for name,path,_,value in NEGATIVE_CASES:
        mutant = copy.deepcopy(d)
        node = mutant
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        try:
            validate(mutant)
        except AssertionError as error:
            assert str(error) == name, (name,str(error))
            results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return results


def build_review():
    d = rd(SUBJECT)
    verify_blobs(d['input_pins'])
    validate(d)
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    exists = Path.exists
    rec = previous['reconstruct']()
    assert rec == rd(PRIOR_RECON) and previous['build_review'](rec) == rd(PRIOR_REVIEW)
    assert Path.exists is exists
    assert d['dependency_gate']['required_package_ids'] == ['W04','W05','W06','W07']
    markers = d['clock_and_marker_obligations']['marker_ledger']
    assert [r['id'] for r in markers] == ['t0','tR','tW','tF']
    for row in markers:
        assert row['historical_definition'] == fragment(row['source'])
        assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    phases = d['phase_derivation_ledger']
    assert [r['id'] for r in phases] == ['Tpre','Tworker','Tpost']
    assert [r['candidate_wall_seconds'] for r in phases] == [60,750,60]
    assert [len(r['historical_W07_vector_requirements']) for r in phases] == [8,6,6]
    assert [len(r['historical_W07_compatibility_requirements']) for r in phases] == [8,6,6]
    for row in phases:
        assert row['historical_phase_requirement'] == fragment(row['source'])
        assert row['accepted'] is False and row['complete_coverage_verified'] is False
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
        for vector,join in zip(row['historical_W07_vector_requirements'],row['historical_W07_compatibility_requirements']):
            v,j = fragment(vector)['historical_requirement'],fragment(join)['historical_requirement']
            assert v['phase'] == j['phase'] == row['id'] and v['id'] == j['id']
    assert len(d['historical_conditional_premise_obligations']) == 7
    assert all(r['satisfied'] is False and r['actual_complete_successor_premise_proof_and_authors'] is None for r in d['historical_conditional_premise_obligations'])
    account = d['time_and_reserve_account']
    assert sum(account['candidate_phase_seconds']) == account['candidate_phase_sum_seconds'] == 870
    assert 870+account['candidate_unassigned_reserve_seconds'] == account['candidate_total_seconds'] == 900
    assert sum([600,90,60]) == 750
    assert [r['id'] for r in d['role_scope_matrix']] == ['R03','R06','R08']
    assert all(r['canonical_actor_id'] is None and r['accepted_appointment'] is False for r in d['role_scope_matrix'])
    for path in rd(PACK)['$defs']['source_bindings']['required']:
        assert not (ROOT/path).exists()
    for key,value in d['current_effect'].items():
        if key == 'W08_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False, key
    return dict(schema='d5.i239-preparation-review.v1',increment='I239',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,candidate=pin(SUBJECT),work_package=pin(PLAN,'/work_packages/7'),
        counts=dict(input_pins=992,marker_requirements=4,phase_requirements=3,historical_vector_references=20,
            historical_compatibility_references=20,unsatisfied_conditional_premises=7,unassigned_review_roles=3,pending_exits=3),
        source_reconstruction=dict(I238_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        formal_algebra=phase_algebra(),rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        limitations=['W04/W05/W06/W07 remain unaccepted; SD01 active. W08 is a negative documentary dossier, not complete successor phase bounds or actual evidence package.',
            'Historical I130 markers/P08 algebra and W07 vectors are requirements only. No genuine source/runtime/clock/service/unit/heap/work/latency/liveness premise or phase bound is supplied.',
            '870+30=900 conserves candidate arithmetic only. No missing upper paid by reserve, budget change, extra CPU600, success guarantee or infeasibility conclusion.',
            'Same-assistant preparation is not independent R03/R06 review or separate R08 acceptance. No product/components run, imports, compile/tests, clock/probe/benchmark or platform/service sampling.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I239-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/marker/phase/unit/algebra and in-memory document checks only. No target imports/compile/discovery/tests/runs, experimental WCET, clock/CPU/IO/service/schedule/platform sampling/probes or external services/contact.',
            over400_lines=True,reason='One W08 negative phase-bound dossier with exact requirements, pins, conditional algebra, rejection cases and preservation. Overage declared; no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_temporal_service_attestation_acceptance_or_execution_authority=True))


def main():
    review = build_review()
    assert rd(PREP) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published679'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 684
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i239-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published684'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == review['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I239',input_pins=992,preserved_published_files=684,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],SD01_stop_active=True,
        prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
