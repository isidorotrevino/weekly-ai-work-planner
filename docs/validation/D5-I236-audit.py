#!/usr/bin/env python3
"""I236 documentary W06 heap/lifetime review. No product or memory introspection."""
import copy
import hashlib
import io
import itertools
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '47f5708a62ce4b9c43ce5cfa38aa6c660e26aac9'
DATE = '2026-11-24'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
SUBJECT = P+'D5-I223-W06-SUCCESSOR-HEAP-LIFETIMES-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE07 = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
ROLLUP = P+'D5-PFC126-03-E02-HEAP-ROLLUP.json'
P03 = P+'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
W04 = P+'D5-I223-W04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
W05 = P+'D5-I223-W05-SUCCESSOR-REQUALIFICATION-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
PROFILE = P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
OUTPUT = P+'D5-I187-CONTEXT-LAUNCH-SCHEMAS-CANDIDATE.json'
TRANSPORT = P+'D5-I189-BOOTSTRAP-TRANSPORT-CONTRACT-CANDIDATE.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
ENTRY_REVIEW = P+'D5-I234-I233-documentary-review.json'
PRIOR_AUDIT = P+'D5-I235-audit.py'
PRIOR_PREP = P+'D5-I235-preparation-review.json'
PRIOR_SEAL = P+'D5-I235-integrity.json'
PRIOR_DOC = 'docs/design/D5-I235-W06-SUCCESSOR-HEAP-LIFETIMES.md'
PRIOR_FILES = {SUBJECT,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I236-I235-source-reconstruction.json'
REVIEW = P+'D5-I236-I235-documentary-review.json'
AUDIT = P+'D5-I236-audit.py'
SEAL = P+'D5-I236-integrity.json'
DOC = 'docs/design/D5-I236-I235-W06-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
OWNERS = [P+'D5-PFC126-03-E02-H%02d.json'%i for i in range(1,12)]
STATUS = 'PASS_STATIC_SOURCE_ONLY_W06_REVIEW_HEAP_LIFETIMES_MISSING_NOT_ADMITTED'


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


def check_negative_boundaries(d):
    assert d['dependency_gate']['SD01_stop_active'] is True, 'SD01_bypass'
    assert d['current_effect']['W06_accepted'] is False, 'W06_accepted'
    assert all(r['actual_complete_upper_bytes'] is None for r in d['owner_derivation_ledger']), 'budget_as_bound'
    assert all(r['actual_size_upper_bytes'] is None for r in d['historical_allocation_class_obligations']), 'invented_size'
    assert all(r['resolved'] is False for r in d['owner_overlap_obligations']), 'invented_pair_resolution'
    assert d['inherited_reference_boundary']['eleven_owner_dossiers_and_historical_partials_not_successor_proof'], 'historical_transfer'
    assert d['inherited_reference_boundary']['partial_H04_model_not_whole_bound_or_minimum_demand_or_infeasibility_proof'], 'partial_as_infeasibility'
    assert d['inherited_reference_boundary']['no_33_generation_or_immediate_GC_shortcut'], 'generational_shortcut'
    assert d['heap_metric_policy']['serialized_JSON_caps_getsizeof_partial_clone_counts_or_RSS_not_whole_heap'], 'RSS_payload_as_heap'
    assert d['heap_metric_policy']['H02_original_suite_parent_is_inside_worker_not_coordinator'], 'H02_reclassification'
    assert d['heap_metric_policy']['actual_joint_host_capacity_claim'] is False, 'joint_host_claim'
    assert d['lifetime_and_peak_contract']['no_immediate_GC_destruction_cache_release_allocator_reuse_or_nonoverlap_assumed'], 'immediate_release'
    assert d['lifetime_and_peak_contract']['originals_and_children_private_retained_state_not_just_clone_payload'], 'omitted_original_child'
    assert d['lifetime_and_peak_contract']['complete_ownership_or_explicit_conservative_overcount_without_duplicate_budget_credit_required'], 'alias_discount'
    assert d['successor_coverage_boundary']['historical132_classes_55_pairs_and_eight_new_families_not_complete_successor_allocation_inventory'], 'historical_as_complete_inventory'
    assert d['requested_rollup']['actual_requested_owner_sum_bytes'] is None, 'unknown_sum_zero'
    assert d['requested_rollup']['actual_fit'] is None, 'invented_requested_fit'
    assert d['requested_rollup']['actual_slack_bytes'] is None, 'invented_slack'
    assert d['committed_rollup']['actual_whole_committed_upper_bytes'] is None, 'invented_committed_bound'
    assert d['committed_rollup']['no_independent_peak_subtraction_or_borrowed_H11_reserve'], 'peak_subtraction'
    assert d['candidate_budget_ledger']['reserve_transfers_applied'] == 0, 'reserve_transfer'
    assert d['availability_and_fit']['actual_requested_available_lower_bytes'] is None, 'reserve_as_capacity'
    assert d['availability_and_fit']['unknown_availability_not_zero_or_infeasibility'], 'unknown_capacity_zero'
    assert d['availability_and_fit']['missing_or_overbudget_complete_proof_keeps_no_admission_no_quota_increase'], 'quota_to_force_fit'
    assert d['phase_handoff']['W06_prepares_complete_memory_derivations_not_W07_CPU_or_W08_success900_or_W09_E01_E05_acceptance'], 'heap_as_all_resources'
    assert d['phase_handoff']['no_reverse_W06_dependency_on_final_resource_acceptance_freeze_C_mapping_E06_root_claim_or_receipt'], 'reverse_dependency'
    assert d['phase_handoff']['genuine_effective_baseline_all_proof_authors_bodies_and_assumptions_before_W09_required'], 'late_authentication'
    assert d['phase_handoff']['W10_reconciles_same_facts_and_changes_invalidate_affected_bounds'], 'forecast_freeze'
    assert d['authority_and_costs']['no_heap_sampling_profiling_benchmarks_introspection_product_components_build_import_compile_or_test_discovery'], 'implicit_profiling'
    assert d['candidate_budget_ledger']['quotas_or_budgets_changed'] is False, 'quota_change'
    assert all(r['accepted'] is False for r in d['exit_predicate_dispositions']), 'exit_acceptance'
    assert d['current_effect']['D5_closed'] is False and d['current_effect']['execution_authorized'] is False, 'positive_effect'


def inspect_scope(d):
    """Independent plan/owner/pair/metric comparisons, not I235-builder equality."""
    check_negative_boundaries(d)
    plan,contract,old = rd(PLAN),rd(CONTRACT),rd(ROLLUP)
    work = plan['work_packages'][5]
    assert d['work_package'] == work['id'] == 'W06' and fragment(d['work_package_binding']) == work
    assert d['planned_deliverable_id'] == work['deliverable_id']
    for target,source in [('required_deliverables','deliverables'),('required_exit_predicates','exit_predicates'),('reject_if','reject_if'),('needs_separate_future_authority_for','needs_separate_future_authority_for')]:
        assert d[target] == work[source]
    assert len(d['required_deliverables']) == len(d['required_exit_predicates']) == 3
    dep = d['dependency_gate']
    assert dep['required_package_ids'] == work['depends_on'] == ['W03','W04','W05']
    assert all(dep[k] is False for k in ['W01_accepted','W02_accepted','W03_accepted','W04_accepted','W05_accepted'])
    assert dep['actual_entry_authority_or_accepted_effective_baseline'] is None and dep['documentary_preparation_not_positive_dependency_progress']
    assert fragment(dep['source']) == rd(ENTRY_REVIEW)['documentary_clarifications'][4]
    assert d['role_scope_matrix'] == [r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R03','R08']]
    assert work['primary_review_roles'] == ['R03'] and work['separate_acceptor_role'] == 'R08'
    assert d['actual_owner_proof_authors_memory_integrator_or_provider_authority'] is None
    owners = d['owner_derivation_ledger']
    ids = ['H%02d'%i for i in range(1,12)]
    assert [r['id'] for r in owners] == ids
    for i,(row,path,task,owner) in enumerate(zip(owners,OWNERS,plan['heap_owner_proof_tasks'],contract['heap']['owner_budgets'])):
        assert row['plan_task'] == pin(PLAN,'/heap_owner_proof_tasks/'+str(i)) and fragment(row['plan_task']) == task
        assert row['contract_owner'] == task['source'] and fragment(row['contract_owner']) == owner
        assert row['id'] == task['id'] == owner['id'] and row['owner'] == task['owner'] == owner['owner']
        assert row['historical_dossier'] == pin(path) and row['historical_status'] == rd(path)['status']
        assert row['historical_review'] == pin(old['complete_owner_fit_vector'][i]['latest_review']['path'])
        assert row['candidate_budget_bytes'] == task['candidate_budget_bytes'] == owner['candidate_budget_bytes']
        assert row['candidate_budget_applied'] is False and row['accepted'] is False
        assert row['required_metric'] == ('allocator_overhead' if row['id']=='H11' else 'peak_requested_live_heap')
        assert row['required_unit'] == 'exact_integer_bytes'
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
    classes = d['historical_allocation_class_obligations']
    expected_classes = [(ids[i],path,j,row) for i,path in enumerate(OWNERS) for j,row in enumerate(rd(path)['complete_live_allocation_inventory']['required_classes'])]
    assert len(classes) == len(expected_classes) == 132
    for row,(owner,path,i,requirement) in zip(classes,expected_classes):
        assert row['owner_id'] == owner and row['source'] == pin(path,'/complete_live_allocation_inventory/required_classes/'+str(i))
        assert row['historical_requirement'] == requirement == fragment(row['source'])
        assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    pairs = d['owner_overlap_obligations']
    historical_pairs = old['overlap_metric_process_review']['owner_pairs']
    assert len(pairs) == len(historical_pairs) == 55
    assert {tuple(r['owners']) for r in pairs} == set(itertools.combinations(ids,2))
    assert sum(len(r['historical_directions']) for r in pairs) == 110
    for i,(row,original) in enumerate(zip(pairs,historical_pairs)):
        assert row['source'] == pin(ROLLUP,'/overlap_metric_process_review/owner_pairs/'+str(i))
        assert row['owners'] == original['owners'] and row['historical_directions'] == original['directions'] and fragment(row['source']) == original
        assert {(r['owner_id'],r['other_owner']) for r in row['historical_directions']} == {tuple(row['owners']),tuple(reversed(row['owners']))}
        assert row['resolved'] is False and row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    reference = d['inherited_reference_boundary']
    assert reference['rollup'] == pin(ROLLUP) and reference['join'] == pin(CE07,'/heap_join')
    assert reference['historical_H08_H09_H10_payload_terms_not_full_heap_or_verified_slack']
    assert reference['actual_successor_finite_complete_bound'] is None and reference['actual_unboundedness_or_infeasibility_proof'] is None
    metric = d['heap_metric_policy']
    assert metric['exact_metric_definitions'] == rd(P03)['available_worker_requested_and_committed_heap']['worker_metric_definitions'] == fragment(metric['source'])
    assert metric['requested_committed_overhead_RSS_stack_and_other_mappings_have_explicit_distinct_domains']
    assert metric['every_relevant_coordinator_thread_child_native_private_heap_requires_separate_scope_and_capacity_composition']
    assert metric['actual_complete_process_domain_mapping'] is None and metric['actual_native_stack_or_other_mapping_evidence'] is None
    life = d['lifetime_and_peak_contract']
    assert life['required_phase_families'] == ['image_entry_startup_and_imports','worker_before_parent_RELEASE_tR','original_and_observer_execution','postreturn_exception_and_retained_aliases','page_flush_and_IO','validation_and_dual_output','success_finally_through_tF','rejection_timeout_cleanup_child_retention']
    assert life['actual_allocation_id_birth_retention_release_or_peak_timeline'] is None and life['actual_complete_same_state_peak_derivation'] is None
    assert life['success_and_every_applicable_rejected_prefix_exception_timeout_cleanup_and_transitive_route_required']
    assert life['aliases_require_actual_identity_lifetime_and_domain_proof_without_omission_or_physical_witness_merge']
    memory = d['new_successor_memory_requirements']
    assert [r['id'] for r in memory] == ['NM%02d'%i for i in range(1,9)]
    assert [(r['source']['path'],r['source']['json_pointer']) for r in memory] == [(SPEC,'/rules/14'),(PROFILE,'/cryptography'),(PROFILE,'/bootstrap'),(SPEC,'/rules/13'),(PROFILE,'/semantic_contracts/10'),(TRANSPORT,'/framing'),(OUTPUT,'/$defs'),(W05,'/coverage_completeness')]
    for row in memory:
        assert row['required_scope'] and row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    coverage = d['successor_coverage_boundary']
    assert coverage['exact_W05_requirements'] == rd(W05)['coverage_completeness'] == fragment(coverage['source'])
    assert coverage['all_new_source_runtime_loader_crypto_caller_constructor_platform_ledger_output_failure_transitives_need_allocation_coverage']
    assert coverage['actual_complete_successor_allocation_membership_and_no_omission_review'] is None
    requested,committed = d['requested_rollup'],d['committed_rollup']
    assert requested['source'] == pin(ROLLUP,'/requested_sum_plus_832MiB_reserve') and requested['owner_ids'] == ids[:10]
    assert requested['conditional_rule'] and requested['missing_term_as_zero_or_budget_substitution'] is False
    assert all(v is None for k,v in requested.items() if k.startswith('actual_'))
    assert committed['source'] == pin(ROLLUP,'/H11_overhead_and_committed_sum') and committed['conditional_rule']
    assert all(v is None for k,v in committed.items() if k.startswith('actual_'))
    budget,heap = d['candidate_budget_ledger'],contract['heap']
    assert fragment(budget['source']) == heap
    for key,source in [('owner_requested_sum_bytes','requested_owner_budget_bytes'),('unassigned_requested_reserve_bytes','unassigned_requested_reserve_bytes'),('requested_heap_candidate_bytes','requested_heap_candidate_bytes'),('allocator_overhead_candidate_bytes','allocator_overhead_candidate_bytes'),('committed_heap_candidate_bytes','committed_heap_candidate_bytes')]:
        assert budget[key] == heap[source]
    assert sum(r['candidate_budget_bytes'] for r in owners[:10]) == budget['owner_requested_sum_bytes'] == 10938744832
    assert budget['owner_requested_sum_bytes']+budget['unassigned_requested_reserve_bytes'] == budget['requested_heap_candidate_bytes'] == 11811160064
    assert budget['requested_heap_candidate_bytes']+budget['allocator_overhead_candidate_bytes'] == budget['committed_heap_candidate_bytes'] == 12884901888
    assert budget['exact_proof_rule'] == heap['proof_rule'] and budget['exact_reserve_rule'] == heap['reserve_rule']
    assert budget['reserve_accounting'] == contract['reserve_accounting']
    assert budget['arithmetic_is_only_candidate_budget_identity_not_runtime_demand_or_capacity'] and budget['resources_reserved'] is False
    available = d['availability_and_fit']
    assert available['preserved_missing_W04_capacity'] == rd(W04)['actual_capacity_state'] == fragment(available['source'])
    assert all(v is None for k,v in available.items() if k.startswith('actual_'))
    assert available['requested_reserve_ordinary_limit_or_host_total_not_verified_capacity']
    phase = d['phase_handoff']
    assert phase['exact_plan_order'] == plan['scope_authentication_and_freeze_order'] == fragment(phase['source'])
    assert phase['W05_memory_handoff'] == pin(W05,'/resource_handoff/0')
    assert phase['W08_consumer'] == pin(PLAN,'/work_packages/7') and phase['W09_joint_acceptance'] == pin(PLAN,'/work_packages/8')
    assert phase['actual_heap_to_work_service_phase_or_joint_resource_derivation'] is None and phase['actual_positive_heap_proof_BASIS_or_index_record_created'] is False
    assert phase['final_route_boundary'] == plan['prelaunch_handoff_and_CE12'] and phase['actual_refresh_or_active_rebind'] is False
    auth = d['authority_and_costs']
    assert auth['inherited_boundary'] == plan['authorization_boundary'] == fragment(auth['source'])
    assert auth['inherited_boundary']['current_run_command'] is None and all(v is False for k,v in auth['inherited_boundary'].items() if k.endswith('_authorized'))
    assert len(auth['allowed_now']) == 4 and auth['no_clock_ledger_process_claim_probes_crypto_signing_enrollment_provider_contact_or_new_helpers_inputs_channels']
    assert auth['exact_per_attempt_cost_requirements'] == rd(CE07)['per_attempt_cost_coverage']
    assert auth['offline_or_caps_not_permission_to_omit_allocation_native_or_lifetime_terms'] and auth['actual_external_material_provider_authority_or_measurement'] is None
    exits = d['exit_predicate_dispositions']
    assert len(exits) == 3 and [r['predicate'] for r in exits] == work['exit_predicates']
    for row in exits:
        assert row['documentary_requirements_prepared'] is True and fragment(row['source']) == row['predicate']
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
    for key in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']:
        assert d['preserved_scope_and_gates'][key] == plan[key]
    for row in d['preserved_scope_and_gates']['preserved_negative_gates']:
        assert fragment({**row['source'],'json_pointer':row['json_pointer']}) == row['observed_value']
    for path in rd(PACK)['$defs']['source_bindings']['required']:
        assert not (ROOT/path).exists()
    for key,value in d['current_effect'].items():
        if key == 'W06_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False
    assert all(d['producer'][k] is False for k in ['actor_independent','competent_R03_review','separate_R08_acceptance','external_contacts_made'])
    check_pointers(d)


def reconstruct():
    d = rd(SUBJECT)
    pins = {**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 977
    verify_blobs(pins)
    inspect_scope(d)
    criteria = [
        ('RC01','Exact three W06 deliverables/exits and authority/rejection clauses','/work_package_binding'),
        ('RC02','W03-W05 unaccepted and SD01 active; no authority or independent roles supplied','/dependency_gate'),
        ('RC03','Eleven exact owners/tasks/metrics/units and candidate budgets with unknown successor bounds','/owner_derivation_ledger'),
        ('RC04','132 exact historical classes retained as coverage requirements, not successor allocations','/historical_allocation_class_obligations'),
        ('RC05','All55 unordered owner pairs and110 historical directions retained, none resolved','/owner_overlap_obligations'),
        ('RC06','Historical partial H04/H08/H09/H10 models do not prove whole bound, slack or infeasibility','/inherited_reference_boundary'),
        ('RC07','Requested/committed/overhead versus RSS/stacks/other mappings kept in distinct domains','/heap_metric_policy'),
        ('RC08','H02 parent remains inside worker; coordinator/children/native/process composition not silently omitted','/heap_metric_policy'),
        ('RC09','Eight lifetime families require complete rejected/success/retained paths without GC/reuse shortcut','/lifetime_and_peak_contract'),
        ('RC10','Eight new memory families and full W05 closure require real allocation mapping','/new_successor_memory_requirements'),
        ('RC11','Aliases require identity/lifetime/domain evidence; only complete ownership or explicit conservative overcount','/lifetime_and_peak_contract'),
        ('RC12','Requested rollup terms unknown; reserve comparison is budget accounting, not allocation','/requested_rollup'),
        ('RC13','Committed/H11 needs same-domain/state correspondence; no independent peak subtraction or borrowing','/committed_rollup'),
        ('RC14','11/12GiB candidate identities and full reserve rules preserved without transfers or capacity claims','/candidate_budget_ledger'),
        ('RC15','W04 lower availability and matching remain unknown; no quota increase or zero-capacity inference','/availability_and_fit'),
        ('RC16','W06 memory feeds W08/W09 without W07 CPU/900/full E01-E05 closure or reverse dependency','/phase_handoff'),
        ('RC17','Genuine baseline/authors/bodies before W09; W10 only reconciles accepted facts and invalidates changes','/phase_handoff'),
        ('RC18','No profiling/sampling/execution authority; every required allocation/native/lifetime cost remains included','/authority_and_costs'),
        ('RC19','Three exits and actual R03/R08 decisions remain unaccepted','/exit_predicate_dispositions'),
        ('RC20','No positive heap/record/resource/gate/D5 promotion; inherited certificate and CE12 preserved','/preserved_scope_and_gates')]
    return dict(schema='d5.i236-i235-source-reconstruction.v1',increment='I236',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        subject=pin(SUBJECT),plan=pin(PLAN,'/work_packages/5'),input_pins=pins,
        criteria=[dict(id=i,criterion=t,subject=pin(SUBJECT,p),result='DOCUMENTARY_CONSISTENCY_CONFIRMED_NOT_REAL_ACCEPTANCE') for i,t,p in criteria],
        owner_assessment=[dict(id=r['id'],metric=r['required_metric'],candidate_budget_bytes=r['candidate_budget_bytes'],historical_dossier=r['historical_dossier'],actual_complete_bound=None,actual_fit=None,accepted=False) for r in d['owner_derivation_ledger']],
        pair_set_equals_all11_choose2=True,
        counts=dict(input_pins=977,criteria=20,owners=11,historical_classes=132,pairs=55,directions=110,new_memory_families=8,lifetime_phase_families=8,unassigned_review_roles=2,pending_exits=3),
        current_effect={**d['current_effect'],'W06_documentary_reviewed':True},methodological_review_not_independent_R03_or_separate_R08=True)


def rejection_checks():
    cases = [
        ('SD01_bypass',('dependency_gate','SD01_stop_active'),False),
        ('W06_accepted',('current_effect','W06_accepted'),True),
        ('budget_as_bound',('owner_derivation_ledger',0,'actual_complete_upper_bytes'),268435456),
        ('invented_size',('historical_allocation_class_obligations',0,'actual_size_upper_bytes'),0),
        ('invented_pair_resolution',('owner_overlap_obligations',0,'resolved'),True),
        ('historical_transfer',('inherited_reference_boundary','eleven_owner_dossiers_and_historical_partials_not_successor_proof'),False),
        ('partial_as_infeasibility',('inherited_reference_boundary','partial_H04_model_not_whole_bound_or_minimum_demand_or_infeasibility_proof'),False),
        ('generational_shortcut',('inherited_reference_boundary','no_33_generation_or_immediate_GC_shortcut'),False),
        ('RSS_payload_as_heap',('heap_metric_policy','serialized_JSON_caps_getsizeof_partial_clone_counts_or_RSS_not_whole_heap'),False),
        ('H02_reclassification',('heap_metric_policy','H02_original_suite_parent_is_inside_worker_not_coordinator'),False),
        ('joint_host_claim',('heap_metric_policy','actual_joint_host_capacity_claim'),True),
        ('immediate_release',('lifetime_and_peak_contract','no_immediate_GC_destruction_cache_release_allocator_reuse_or_nonoverlap_assumed'),False),
        ('omitted_original_child',('lifetime_and_peak_contract','originals_and_children_private_retained_state_not_just_clone_payload'),False),
        ('alias_discount',('lifetime_and_peak_contract','complete_ownership_or_explicit_conservative_overcount_without_duplicate_budget_credit_required'),False),
        ('historical_as_complete_inventory',('successor_coverage_boundary','historical132_classes_55_pairs_and_eight_new_families_not_complete_successor_allocation_inventory'),False),
        ('unknown_sum_zero',('requested_rollup','actual_requested_owner_sum_bytes'),0),
        ('invented_requested_fit',('requested_rollup','actual_fit'),True),
        ('invented_slack',('requested_rollup','actual_slack_bytes'),0),
        ('invented_committed_bound',('committed_rollup','actual_whole_committed_upper_bytes'),12884901888),
        ('peak_subtraction',('committed_rollup','no_independent_peak_subtraction_or_borrowed_H11_reserve'),False),
        ('reserve_transfer',('candidate_budget_ledger','reserve_transfers_applied'),1),
        ('reserve_as_capacity',('availability_and_fit','actual_requested_available_lower_bytes'),11811160064),
        ('unknown_capacity_zero',('availability_and_fit','unknown_availability_not_zero_or_infeasibility'),False),
        ('quota_to_force_fit',('availability_and_fit','missing_or_overbudget_complete_proof_keeps_no_admission_no_quota_increase'),False),
        ('heap_as_all_resources',('phase_handoff','W06_prepares_complete_memory_derivations_not_W07_CPU_or_W08_success900_or_W09_E01_E05_acceptance'),False),
        ('reverse_dependency',('phase_handoff','no_reverse_W06_dependency_on_final_resource_acceptance_freeze_C_mapping_E06_root_claim_or_receipt'),False),
        ('late_authentication',('phase_handoff','genuine_effective_baseline_all_proof_authors_bodies_and_assumptions_before_W09_required'),False),
        ('forecast_freeze',('phase_handoff','W10_reconciles_same_facts_and_changes_invalidate_affected_bounds'),False),
        ('implicit_profiling',('authority_and_costs','no_heap_sampling_profiling_benchmarks_introspection_product_components_build_import_compile_or_test_discovery'),False),
        ('quota_change',('candidate_budget_ledger','quotas_or_budgets_changed'),True),
        ('exit_acceptance',('exit_predicate_dispositions',0,'accepted'),True),
        ('positive_effect',('current_effect','D5_closed'),True)]
    out = []
    for name,path,value in cases:
        mutant = copy.deepcopy(rd(SUBJECT))
        target = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            inspect_scope(mutant)
        except AssertionError as error:
            assert str(error) == name, (name,str(error))
            out.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return out


def build_review(rec):
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    exists = Path.exists
    assert previous['build_candidate']() == rd(SUBJECT)
    assert previous['build_review']() == rd(PRIOR_PREP)
    assert Path.exists is exists
    return dict(schema='d5.i236-i235-documentary-review.v1',increment='I236',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,subject=pin(SUBJECT),reconstruction=pin(RECON),verdict='W06_DOCUMENTARY_HEAP_LIFETIME_ROLLUP_PHASE_BOUNDARIES_CONSISTENT_COMPLETE_SUCCESSOR_MEMORY_PROOF_MISSING_NOT_ACCEPTED',
        findings=[],finding_count=0,criteria=rec['criteria'],counts=rec['counts'],
        documentary_clarifications=[
            dict(id='N01',subject='Historical coverage versus actual memory proof',disposition='Eleven owners,132 classes,55 pairs/110 directions and eight new families remain requirements, not complete successor allocation inventory or accepted bounds. H04 partial model is neither complete upper nor minimum demand/infeasibility proof; H08/H09/H10 payload terms and historical dossiers do not transfer as complete heap/slack.'),
            dict(id='N02',subject='Metrics, process scope and lifetime coverage',disposition='Requested live heap, committed allocator backing and H11 overhead require exact same-domain/state coverage, distinct from RSS/stacks/other mappings. H02 suite parent remains inside worker; coordinator/children/native/private/process overlaps need separate composition. No GC/reuse/nonoverlap shortcut, alias discount, witness merge or omitted rejected-prefix cost is justified.'),
            dict(id='N03',subject='Budget arithmetic versus rollup and availability',disposition='Known owner budgets plus832MiB reserve give11GiB requested, then1GiB H11 gives12GiB committed as candidate identities only. All real sums, fits/slack and independent W04 availability remain unknown. Remaining reserve is budget accounting, not physical usage/capacity. No peak subtraction, H11 borrowing, quota increase or zero-capacity/infeasibility inference is permitted.'),
            dict(id='N04',subject='Handoffs and antecedent authentication',disposition='W03-W05/SD01 remain blocking. W06 supplies memory derivations to W08/W09, not W07 CPU, successful900 or whole E01-E05 acceptance. No reverse baseline dependency on later acceptance/freeze/C/mapping/E06/root/claim is added. Genuine authors/bodies/scope precede W09; W10 reconciles the same accepted facts and changes invalidate affected bounds.'),
            dict(id='N05',subject='Authority and independent acceptance',disposition='No profiling/sampling/introspection, product/component execution, helpers/inputs/channels, crypto/probes/services/contact or quota/reserve change is authorized. All required per-attempt allocation/native/lifetime work stays in full composition. Same assistant checks do not provide competent independent R03 review or separate R08 acceptance; CE12 and final route remain deferred.')],
        source_replay=dict(I235_candidate_and_preparation_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(),current_effect=rec['current_effect'],
        provenance=dict(preparer_and_reviewer='Same Codex assistant/chat as I235',methodological_only=True,actor_independent=False,competent_R03_review=False,separate_R08_acceptance=False,external_contacts=False),
        next_step='Documentary W06 review complete. Positive progress stays stopped at SD01 pending genuine authority, accepted dependencies and complete exact-scope owner/lifetime/overlap/rollup/capacity evidence; no measurement or operational work initiated.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I236-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/owner/class/pair/budget/phase comparisons only; no product/components imports/build/compile/test discovery/tests/benchmarks, heap sampling/profiling/getsizeof/introspection, codec/crypto positives, clock/ledger/claim/process/probes/signing/keygen/enrollment/provisioning/services/contact.',
            over400_lines=True,reason='One W06 review with exact pins, independently checked owners/classes/all55 pairs, metric/lifetime/rollup/capacity comparisons, negative checks and preservation; overage declared. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_heap_capacity_attestation_or_execution_authority=True))


def main():
    rec = reconstruct()
    assert rd(RECON) == rec
    review = build_review(rec)
    assert rd(REVIEW) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published664'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 669
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i236-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published669'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == rec['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I236',historical_pins=977,preserved_published_files=669,new_files=5,
        criteria=20,findings=0,documentary_rejections=len(review['rejection_checks']),current_effect=rec['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
