#!/usr/bin/env python3
"""I235 W06 negative successor heap/lifetime dossier. Documentary JSON/Git only."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '78e5eac02d31c97fd611f66d050938825073bae9'
DATE = '2026-11-24'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE07 = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
ROLLUP = P+'D5-PFC126-03-E02-HEAP-ROLLUP.json'
ROLLUP_REVIEW = P+'D5-I162-P05-documentary-review.json'
P03 = P+'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
W03 = P+'D5-I223-W03-SOURCES-IMAGE-RUNTIME-CANDIDATE.json'
W04 = P+'D5-I223-W04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
W05 = P+'D5-I223-W05-SUCCESSOR-REQUALIFICATION-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
PROFILE = P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
PROTO = P+'D5-I185-PGO181-SCHEMAS-CANDIDATE-02.json'
OUTPUT = P+'D5-I187-CONTEXT-LAUNCH-SCHEMAS-CANDIDATE.json'
TRANSPORT = P+'D5-I189-BOOTSTRAP-TRANSPORT-CONTRACT-CANDIDATE.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PRIOR_RECON = P+'D5-I234-I233-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I234-I233-documentary-review.json'
PRIOR_AUDIT = P+'D5-I234-audit.py'
PRIOR_SEAL = P+'D5-I234-integrity.json'
PRIOR_DOC = 'docs/design/D5-I234-I233-W05-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I223-W06-SUCCESSOR-HEAP-LIFETIMES-CANDIDATE.json'
PREP = P+'D5-I235-preparation-review.json'
AUDIT = P+'D5-I235-audit.py'
SEAL = P+'D5-I235-integrity.json'
DOC = 'docs/design/D5-I235-W06-SUCCESSOR-HEAP-LIFETIMES.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
OWNERS = [P+'D5-PFC126-03-E02-H%02d.json'%i for i in range(1,12)]
STATUS = 'PASS_STATIC_SOURCE_ONLY_W06_HEAP_LIFETIMES_MISSING_SD01_ACTIVE_NOT_ADMITTED'


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
    plan,contract,old,join = rd(PLAN),rd(CONTRACT),rd(ROLLUP),rd(CE07)
    work = plan['work_packages'][5]
    pins = {**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 972
    reviews = [r['latest_review']['path'] for r in old['complete_owner_fit_vector']]
    inventory = sorted({PLAN,PRIOR_REVIEW,CE01,CE07,CONTRACT,ROLLUP,ROLLUP_REVIEW,P03,W03,W04,W05,PACK,PROFILE,PROTO,OUTPUT,TRANSPORT,SPEC,*OWNERS,*reviews})
    owners,classes = [],[]
    for i,(task,path) in enumerate(zip(plan['heap_owner_proof_tasks'],OWNERS)):
        prior = rd(path)
        owners.append(dict(id=task['id'],owner=task['owner'],plan_task=pin(PLAN,'/heap_owner_proof_tasks/'+str(i)),contract_owner=task['source'],
            historical_dossier=pin(path),historical_status=prior['status'],historical_review=pin(reviews[i]),
            candidate_budget_bytes=task['candidate_budget_bytes'],candidate_budget_applied=False,
            required_metric='allocator_overhead' if i==10 else 'peak_requested_live_heap',required_unit='exact_integer_bytes',
            actual_effective_scope_runtime_ABI_allocator_and_process_mapping=None,actual_complete_allocation_inventory=None,
            actual_cardinality_size_and_same_state_lifetime_derivation=None,actual_complete_upper_bytes=None,actual_committed_coverage_derivation=None,
            actual_proof_body_hash_author_provider_custody_or_assumptions=None,actual_primary_R03_review=None,actual_separate_R08_acceptance=None,
            actual_fits_budget=None,actual_slack_bytes=None,accepted=False))
        for j,row in enumerate(prior['complete_live_allocation_inventory']['required_classes']):
            classes.append(dict(owner_id=task['id'],source=pin(path,'/complete_live_allocation_inventory/required_classes/'+str(j)),historical_requirement=row,
                actual_successor_allocation_class_or_source_mapping=None,actual_cardinality_upper=None,actual_size_upper_bytes=None,
                actual_maximum_live_upper_bytes=None,actual_lifetime_derivation=None,actual_proof_body_or_review=None,accepted=False))
    pairs = [dict(owners=row['owners'],source=pin(ROLLUP,'/overlap_metric_process_review/owner_pairs/'+str(i)),historical_directions=row['directions'],
        actual_successor_allocation_identity_alias_domain_or_ownership_mapping=None,actual_same_state_lifetime_overlap_or_conservative_overcount_proof=None,
        actual_complete_no_omission_no_double_credit_review=None,resolved=False,accepted=False) for i,row in enumerate(old['overlap_metric_process_review']['owner_pairs'])]
    new_memory = [
        ('NM01','Accepted custody records, actor/anchor/image/caller/platform snapshots and registry state',SPEC,'/rules/14'),
        ('NM02','JCS/parse/hash/strict crypto and measurement copies/native workspaces on every attempt',PROFILE,'/cryptography'),
        ('NM03','Identity/preparer/alias/key resolution, freshness/revocation/clock snapshots and rejection prefixes',PROFILE,'/bootstrap'),
        ('NM04','Global ledger lookup/locking/durable/partial-failure/receipt and backend-native/IO allocations',SPEC,'/rules/13'),
        ('NM05','Both physical Input Readers, phase snapshots/fresh reads/listings/maps/copies and496 stable paths',PROFILE,'/semantic_contracts/10'),
        ('NM06','Two-pipe framing/EOF/attempt/error buffers and constructor/bootstrap/READY/RELEASE state',TRANSPORT,'/framing'),
        ('NM07','Dual complete context/launch documents, codecs/trees/copies, validation and all diagnostic/fallback paths',OUTPUT,'/$defs'),
        ('NM08','Atomic drafts/clones/memo/frames/originals/rejected phases plus threads/children/native/GC/allocator overlap',W05,'/coverage_completeness')]
    lifetime_phases = ['image_entry_startup_and_imports','worker_before_parent_RELEASE_tR','original_and_observer_execution','postreturn_exception_and_retained_aliases','page_flush_and_IO','validation_and_dual_output','success_finally_through_tF','rejection_timeout_cleanup_child_retention']
    heap = contract['heap']
    return dict(schema='d5.i235-w06-successor-heap-lifetimes-candidate.v1',increment='I235',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        work_package='W06',planned_deliverable_id=work['deliverable_id'],kind='NEGATIVE_HEAP_LIFETIME_REQUIREMENT_DOSSIER_NOT_ALLOCATION_TRACE_NOT_COMPLETE_BOUND_NOT_ACCEPTED_REAL_EVIDENCE_PACKAGE',
        status='W06_DOCUMENTARY_PREPARED_COMPLETE_OWNER_LIFETIME_ROLLUP_CAPACITY_PROOFS_MISSING_SD01_ACTIVE_NOT_ADMITTED',
        input_pins=pins,work_package_binding=pin(PLAN,'/work_packages/5'),required_deliverables=work['deliverables'],required_exit_predicates=work['exit_predicates'],reject_if=work['reject_if'],needs_separate_future_authority_for=work['needs_separate_future_authority_for'],documentary_inventory=[pin(p) for p in inventory],
        dependency_gate=dict(source=pin(PRIOR_REVIEW,'/documentary_clarifications/4'),required_package_ids=work['depends_on'],W01_accepted=False,W02_accepted=False,W03_accepted=False,W04_accepted=False,W05_accepted=False,SD01_stop_active=True,
            actual_entry_authority_or_accepted_effective_baseline=None,documentary_preparation_not_positive_dependency_progress=True),
        role_scope_matrix=[r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R03','R08']],actual_owner_proof_authors_memory_integrator_or_provider_authority=None,
        owner_derivation_ledger=owners,historical_allocation_class_obligations=classes,owner_overlap_obligations=pairs,
        inherited_reference_boundary=dict(rollup=pin(ROLLUP),rollup_review=pin(ROLLUP_REVIEW),join=pin(CE07,'/heap_join'),
            eleven_owner_dossiers_and_historical_partials_not_successor_proof=True,partial_H04_model_not_whole_bound_or_minimum_demand_or_infeasibility_proof=True,
            no_33_generation_or_immediate_GC_shortcut=True,historical_H08_H09_H10_payload_terms_not_full_heap_or_verified_slack=True,
            actual_successor_finite_complete_bound=None,actual_unboundedness_or_infeasibility_proof=None),
        heap_metric_policy=dict(source=pin(P03,'/available_worker_requested_and_committed_heap/worker_metric_definitions'),
            exact_metric_definitions=rd(P03)['available_worker_requested_and_committed_heap']['worker_metric_definitions'],
            requested_committed_overhead_RSS_stack_and_other_mappings_have_explicit_distinct_domains=True,
            serialized_JSON_caps_getsizeof_partial_clone_counts_or_RSS_not_whole_heap=True,
            H02_original_suite_parent_is_inside_worker_not_coordinator=True,
            every_relevant_coordinator_thread_child_native_private_heap_requires_separate_scope_and_capacity_composition=True,
            actual_complete_process_domain_mapping=None,actual_native_stack_or_other_mapping_evidence=None,actual_joint_host_capacity_claim=False),
        lifetime_and_peak_contract=dict(required_phase_families=lifetime_phases,
            actual_allocation_id_birth_retention_release_or_peak_timeline=None,actual_complete_same_state_peak_derivation=None,
            originals_and_children_private_retained_state_not_just_clone_payload=True,
            success_and_every_applicable_rejected_prefix_exception_timeout_cleanup_and_transitive_route_required=True,
            no_immediate_GC_destruction_cache_release_allocator_reuse_or_nonoverlap_assumed=True,
            aliases_require_actual_identity_lifetime_and_domain_proof_without_omission_or_physical_witness_merge=True,
            complete_ownership_or_explicit_conservative_overcount_without_duplicate_budget_credit_required=True),
        new_successor_memory_requirements=[dict(id=i,required_scope=t,source=pin(p,ptr),actual_source_allocation_owner_process_phase_mapping=None,actual_count_size_native_lifetime_overlap_derivation=None,actual_complete_upper_or_review=None,accepted=False) for i,t,p,ptr in new_memory],
        successor_coverage_boundary=dict(source=pin(W05,'/coverage_completeness'),exact_W05_requirements=rd(W05)['coverage_completeness'],
            historical132_classes_55_pairs_and_eight_new_families_not_complete_successor_allocation_inventory=True,
            all_new_source_runtime_loader_crypto_caller_constructor_platform_ledger_output_failure_transitives_need_allocation_coverage=True,
            actual_complete_successor_allocation_membership_and_no_omission_review=None),
        requested_rollup=dict(source=pin(ROLLUP,'/requested_sum_plus_832MiB_reserve'),owner_ids=['H%02d'%i for i in range(1,11)],
            conditional_rule='Only complete same-scope per-owner requested upper bounds may be summed; sum(U_H01..U_H10)+documented remaining reserve<=candidate requested envelope. This reserve term is budget accounting, not measured allocation.',
            actual_requested_owner_sum_bytes=None,actual_remaining_reserve_comparison_sum_bytes=None,actual_whole_requested_peak_upper_bytes=None,
            actual_fit=None,actual_slack_bytes=None,missing_term_as_zero_or_budget_substitution=False),
        committed_rollup=dict(source=pin(ROLLUP,'/H11_overhead_and_committed_sum'),
            conditional_rule='Derive requested/backing/overhead correspondence in the same worker/domain/state with complete coverage; complete upper bounds may conservatively add. Independent peak subtraction does not derive H11.',
            actual_complete_H11_overhead_upper_bytes=None,actual_same_state_requested_backing_overhead_derivation=None,actual_whole_committed_upper_bytes=None,
            actual_fit=None,actual_slack_bytes=None,no_independent_peak_subtraction_or_borrowed_H11_reserve=True),
        candidate_budget_ledger=dict(source=pin(CONTRACT,'/heap'),owner_requested_sum_bytes=heap['requested_owner_budget_bytes'],unassigned_requested_reserve_bytes=heap['unassigned_requested_reserve_bytes'],
            requested_heap_candidate_bytes=heap['requested_heap_candidate_bytes'],allocator_overhead_candidate_bytes=heap['allocator_overhead_candidate_bytes'],committed_heap_candidate_bytes=heap['committed_heap_candidate_bytes'],
            exact_proof_rule=heap['proof_rule'],exact_reserve_rule=heap['reserve_rule'],reserve_accounting=contract['reserve_accounting'],
            arithmetic_is_only_candidate_budget_identity_not_runtime_demand_or_capacity=True,
            reserve_transfers_applied=0,resources_reserved=False,quotas_or_budgets_changed=False),
        availability_and_fit=dict(source=pin(W04,'/actual_capacity_state'),preserved_missing_W04_capacity=rd(W04)['actual_capacity_state'],
            actual_requested_available_lower_bytes=None,actual_committed_available_lower_bytes=None,actual_scope_unit_validity_provider_and_process_match=None,
            actual_whole_requested_fit=None,actual_whole_committed_fit=None,
            actual_independent_capacity_attestation=None,requested_reserve_ordinary_limit_or_host_total_not_verified_capacity=True,
            unknown_availability_not_zero_or_infeasibility=True,missing_or_overbudget_complete_proof_keeps_no_admission_no_quota_increase=True),
        phase_handoff=dict(source=pin(PLAN,'/scope_authentication_and_freeze_order'),exact_plan_order=plan['scope_authentication_and_freeze_order'],
            W05_memory_handoff=pin(W05,'/resource_handoff/0'),W08_consumer=pin(PLAN,'/work_packages/7'),W09_joint_acceptance=pin(PLAN,'/work_packages/8'),
            W06_prepares_complete_memory_derivations_not_W07_CPU_or_W08_success900_or_W09_E01_E05_acceptance=True,
            no_reverse_W06_dependency_on_final_resource_acceptance_freeze_C_mapping_E06_root_claim_or_receipt=True,
            genuine_effective_baseline_all_proof_authors_bodies_and_assumptions_before_W09_required=True,
            W10_reconciles_same_facts_and_changes_invalidate_affected_bounds=True,
            actual_heap_to_work_service_phase_or_joint_resource_derivation=None,actual_positive_heap_proof_BASIS_or_index_record_created=False,
            final_route_boundary=plan['prelaunch_handoff_and_CE12'],actual_refresh_or_active_rebind=False),
        authority_and_costs=dict(source=pin(PLAN,'/authorization_boundary'),inherited_boundary=plan['authorization_boundary'],
            allowed_now=['READ_DOCUMENTS_GIT_HASHES_AND_EXACT_PATH_PRESENCE','PREPARE_THIS_NEGATIVE_DOSSIER','RUN_OWN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT'],
            no_heap_sampling_profiling_benchmarks_introspection_product_components_build_import_compile_or_test_discovery=True,
            no_clock_ledger_process_claim_probes_crypto_signing_enrollment_provider_contact_or_new_helpers_inputs_channels=True,
            exact_per_attempt_cost_requirements=join['per_attempt_cost_coverage'],offline_or_caps_not_permission_to_omit_allocation_native_or_lifetime_terms=True,
            actual_external_material_provider_authority_or_measurement=None),
        exit_predicate_dispositions=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/5/exit_predicates/'+str(i)),predicate=t,documentary_requirements_prepared=True,actual_evidence=None,actual_primary_R03_review=None,actual_separate_R08_acceptance=None,accepted=False) for i,t in enumerate(work['exit_predicates'])],
        preserved_scope_and_gates=dict(inherited_scope_boundaries=plan['inherited_scope_boundaries'],preserved_negative_gates=plan['preserved_negative_gates'],prelaunch_handoff_and_CE12=plan['prelaunch_handoff_and_CE12']),
        current_effect=dict(W06_documentary_prepared=True,W01_accepted=False,W02_accepted=False,W03_accepted=False,W04_accepted=False,W05_accepted=False,W06_accepted=False,actual_entry_authority_verified=False,
            actual_complete_owner_heap_lifetime_rollup_capacity_or_fit_verified=False,actual_real_evidence_package_created=False,positive_I191_or_BASIS_index_heap_proof_record_created=False,
            actual_evidence_accepted=0,work_packages_accepted=0,prelaunch_gates_closed=0,resource_obligations_closed=0,
            independent_acceptance=False,source_implementation_changed=False,product_or_components_executed=False,quotas_changed=False,reserves_changed=False,resource_reservations_created=False,rebind_applied=False,authority_or_destination_created=False,actual_claim_worker_or_receipt_created=False,
            execution_authorized=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),
        producer=dict(identity='Same Codex assistant/chat as I233/I234',documentary_preparer_only=True,actor_independent=False,competent_R03_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_heap_capacity_attestation_or_execution_authority=True))


def validate(d):
    assert d['dependency_gate']['SD01_stop_active'] is True and all(d['dependency_gate'][k] is False for k in ['W03_accepted','W04_accepted','W05_accepted']), 'dependency_bypass'
    assert d['current_effect']['W06_accepted'] is False, 'W06_accepted'
    assert all(r['actual_complete_upper_bytes'] is None for r in d['owner_derivation_ledger']), 'budget_as_bound'
    assert all(r['actual_size_upper_bytes'] is None for r in d['historical_allocation_class_obligations']), 'invented_object_size'
    assert all(r['resolved'] is False for r in d['owner_overlap_obligations']), 'invented_pair_resolution'
    assert d['inherited_reference_boundary']['eleven_owner_dossiers_and_historical_partials_not_successor_proof'], 'historical_transfer'
    assert d['inherited_reference_boundary']['partial_H04_model_not_whole_bound_or_minimum_demand_or_infeasibility_proof'], 'partial_as_infeasibility'
    assert d['inherited_reference_boundary']['no_33_generation_or_immediate_GC_shortcut'], 'generational_shortcut'
    assert d['heap_metric_policy']['serialized_JSON_caps_getsizeof_partial_clone_counts_or_RSS_not_whole_heap'], 'RSS_or_payload_as_heap'
    assert d['heap_metric_policy']['H02_original_suite_parent_is_inside_worker_not_coordinator'], 'H02_as_coordinator'
    assert d['heap_metric_policy']['actual_joint_host_capacity_claim'] is False, 'unproved_joint_host_claim'
    assert d['lifetime_and_peak_contract']['no_immediate_GC_destruction_cache_release_allocator_reuse_or_nonoverlap_assumed'], 'immediate_release'
    assert d['lifetime_and_peak_contract']['originals_and_children_private_retained_state_not_just_clone_payload'], 'omitted_original_child'
    assert d['lifetime_and_peak_contract']['complete_ownership_or_explicit_conservative_overcount_without_duplicate_budget_credit_required'], 'alias_discount'
    assert d['successor_coverage_boundary']['historical132_classes_55_pairs_and_eight_new_families_not_complete_successor_allocation_inventory'], 'historical_as_complete_inventory'
    assert d['requested_rollup']['actual_requested_owner_sum_bytes'] is None, 'unknown_sum_zero'
    assert d['requested_rollup']['actual_fit'] is None, 'invented_requested_fit'
    assert d['committed_rollup']['actual_whole_committed_upper_bytes'] is None, 'invented_committed_bound'
    assert d['committed_rollup']['no_independent_peak_subtraction_or_borrowed_H11_reserve'], 'peak_subtraction'
    assert d['candidate_budget_ledger']['reserve_transfers_applied'] == 0, 'reserve_transfer'
    assert d['availability_and_fit']['actual_requested_available_lower_bytes'] is None, 'reserve_as_capacity'
    assert d['availability_and_fit']['unknown_availability_not_zero_or_infeasibility'], 'unknown_capacity_zero'
    assert d['availability_and_fit']['missing_or_overbudget_complete_proof_keeps_no_admission_no_quota_increase'], 'quota_to_force_fit'
    assert d['phase_handoff']['W06_prepares_complete_memory_derivations_not_W07_CPU_or_W08_success900_or_W09_E01_E05_acceptance'], 'heap_as_all_resources'
    assert d['phase_handoff']['no_reverse_W06_dependency_on_final_resource_acceptance_freeze_C_mapping_E06_root_claim_or_receipt'], 'reverse_dependency'
    assert d['phase_handoff']['genuine_effective_baseline_all_proof_authors_bodies_and_assumptions_before_W09_required'], 'late_authentication'
    assert d['authority_and_costs']['no_heap_sampling_profiling_benchmarks_introspection_product_components_build_import_compile_or_test_discovery'], 'implicit_profiling'
    assert d['candidate_budget_ledger']['quotas_or_budgets_changed'] is False, 'quota_change'
    assert all(r['accepted'] is False for r in d['exit_predicate_dispositions']), 'exit_acceptance'
    assert d['current_effect']['D5_closed'] is False, 'D5_closed'
    assert d == build_candidate(), 'Candidate differs from source reconstruction'
    check_pointers(d)


def rejection_checks(d):
    cases = [
        ('dependency_bypass',('dependency_gate','SD01_stop_active'),False),
        ('W06_accepted',('current_effect','W06_accepted'),True),
        ('budget_as_bound',('owner_derivation_ledger',0,'actual_complete_upper_bytes'),268435456),
        ('invented_object_size',('historical_allocation_class_obligations',0,'actual_size_upper_bytes'),0),
        ('invented_pair_resolution',('owner_overlap_obligations',0,'resolved'),True),
        ('historical_transfer',('inherited_reference_boundary','eleven_owner_dossiers_and_historical_partials_not_successor_proof'),False),
        ('partial_as_infeasibility',('inherited_reference_boundary','partial_H04_model_not_whole_bound_or_minimum_demand_or_infeasibility_proof'),False),
        ('generational_shortcut',('inherited_reference_boundary','no_33_generation_or_immediate_GC_shortcut'),False),
        ('RSS_or_payload_as_heap',('heap_metric_policy','serialized_JSON_caps_getsizeof_partial_clone_counts_or_RSS_not_whole_heap'),False),
        ('H02_as_coordinator',('heap_metric_policy','H02_original_suite_parent_is_inside_worker_not_coordinator'),False),
        ('unproved_joint_host_claim',('heap_metric_policy','actual_joint_host_capacity_claim'),True),
        ('immediate_release',('lifetime_and_peak_contract','no_immediate_GC_destruction_cache_release_allocator_reuse_or_nonoverlap_assumed'),False),
        ('omitted_original_child',('lifetime_and_peak_contract','originals_and_children_private_retained_state_not_just_clone_payload'),False),
        ('alias_discount',('lifetime_and_peak_contract','complete_ownership_or_explicit_conservative_overcount_without_duplicate_budget_credit_required'),False),
        ('historical_as_complete_inventory',('successor_coverage_boundary','historical132_classes_55_pairs_and_eight_new_families_not_complete_successor_allocation_inventory'),False),
        ('unknown_sum_zero',('requested_rollup','actual_requested_owner_sum_bytes'),0),
        ('invented_requested_fit',('requested_rollup','actual_fit'),True),
        ('invented_committed_bound',('committed_rollup','actual_whole_committed_upper_bytes'),12884901888),
        ('peak_subtraction',('committed_rollup','no_independent_peak_subtraction_or_borrowed_H11_reserve'),False),
        ('reserve_transfer',('candidate_budget_ledger','reserve_transfers_applied'),1),
        ('reserve_as_capacity',('availability_and_fit','actual_requested_available_lower_bytes'),11811160064),
        ('unknown_capacity_zero',('availability_and_fit','unknown_availability_not_zero_or_infeasibility'),False),
        ('quota_to_force_fit',('availability_and_fit','missing_or_overbudget_complete_proof_keeps_no_admission_no_quota_increase'),False),
        ('heap_as_all_resources',('phase_handoff','W06_prepares_complete_memory_derivations_not_W07_CPU_or_W08_success900_or_W09_E01_E05_acceptance'),False),
        ('reverse_dependency',('phase_handoff','no_reverse_W06_dependency_on_final_resource_acceptance_freeze_C_mapping_E06_root_claim_or_receipt'),False),
        ('late_authentication',('phase_handoff','genuine_effective_baseline_all_proof_authors_bodies_and_assumptions_before_W09_required'),False),
        ('implicit_profiling',('authority_and_costs','no_heap_sampling_profiling_benchmarks_introspection_product_components_build_import_compile_or_test_discovery'),False),
        ('quota_change',('candidate_budget_ledger','quotas_or_budgets_changed'),True),
        ('exit_acceptance',('exit_predicate_dispositions',0,'accepted'),True),
        ('D5_closed',('current_effect','D5_closed'),True)]
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
    owners = d['owner_derivation_ledger']
    assert len(owners) == 11 and [r['id'] for r in owners] == ['H%02d'%i for i in range(1,12)]
    assert sum(r['candidate_budget_bytes'] for r in owners[:10]) == d['candidate_budget_ledger']['owner_requested_sum_bytes'] == 10938744832
    for row in owners:
        assert fragment(row['plan_task'])['id'] == fragment(row['contract_owner'])['id'] == row['id']
        assert row['candidate_budget_applied'] is False and row['accepted'] is False
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
    assert len(d['historical_allocation_class_obligations']) == 132
    for row in d['historical_allocation_class_obligations']:
        assert row['historical_requirement'] == fragment(row['source'])
        assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    pairs = d['owner_overlap_obligations']
    assert len(pairs) == 55 and sum(len(r['historical_directions']) for r in pairs) == 110
    assert len({tuple(r['owners']) for r in pairs}) == 55
    for row in pairs:
        original = fragment(row['source'])
        assert row['owners'] == original['owners'] and row['historical_directions'] == original['directions']
        assert row['resolved'] is False and row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    budget = d['candidate_budget_ledger']
    assert budget['owner_requested_sum_bytes']+budget['unassigned_requested_reserve_bytes'] == budget['requested_heap_candidate_bytes'] == 11811160064
    assert budget['requested_heap_candidate_bytes']+budget['allocator_overhead_candidate_bytes'] == budget['committed_heap_candidate_bytes'] == 12884901888
    assert budget['unassigned_requested_reserve_bytes'] == 872415232 and budget['allocator_overhead_candidate_bytes'] == 1073741824
    assert len(d['new_successor_memory_requirements']) == 8 and len(d['lifetime_and_peak_contract']['required_phase_families']) == 8
    assert [r['id'] for r in d['role_scope_matrix']] == ['R03','R08']
    assert all(r['canonical_actor_id'] is None and r['accepted_appointment'] is False for r in d['role_scope_matrix'])
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
            assert value is False, key
    return dict(schema='d5.i235-preparation-review.v1',increment='I235',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,candidate=pin(SUBJECT),work_package=pin(PLAN,'/work_packages/5'),
        counts=dict(input_pins=972,owner_requirements=11,historical_allocation_classes=132,owner_pairs=55,historical_directed_boundaries=110,new_memory_families=8,lifetime_phase_families=8,unassigned_review_roles=2,pending_exits=3),
        source_reconstruction=dict(I234_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        limitations=['W01-W05 remain unaccepted and SD01 active. W06 is a negative memory requirement dossier, not actual allocation traces/complete owner bounds or an accepted package.',
            'Eleven historical owners,132 classes and55 pairs/110 directed references are coverage obligations, not a complete successor inventory. Exact allocations, object sizes/cardinality/lifetimes/native/GC/allocator mapping, joint process scope and all proof bodies/authors remain absent.',
            'Requested/committed sums, fits/slack and W04 actual availability stay unknown. Candidate11/12GiB and832MiB/1GiB reserves/overhead are not measured demand/capacity; no reserve transfer. H04 partial model proves neither whole upper nor minimum demand/infeasibility.',
            'W06 feeds memory evidence to W08/W09 without CPU/service/900/E01-E05 closure or a reverse dependency. Same assistant checks do not provide independent R03 review or separate R08 acceptance.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I235-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/owner/class/pair/budget checks only; no product/components imports/build/compile/test discovery/tests/benchmarks, heap sampling/profiling/introspection, codec/crypto positives, clock/ledger/claim/process/probe/signing/keygen/enrollment/provisioning/services/contact.',
            over400_lines=True,reason='One W06 negative heap/lifetime dossier with exact owner/class/pair obligations, successor families, rollup rules, pins/checks and preservation; overage declared. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_heap_capacity_attestation_or_execution_authority=True))


def main():
    review = build_review()
    assert rd(PREP) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published659'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 664
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i235-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published664'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == review['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I235',historical_pins=972,preserved_published_files=664,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],current_effect=review['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
