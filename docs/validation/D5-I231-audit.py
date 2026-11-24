#!/usr/bin/env python3
"""I231 W04 negative caller/platform/service dossier. Documentary JSON/Git only."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'b845f94da77cc353275424d84fba146f3bd415c6'
DATE = '2026-11-24'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE05 = P+'D5-I193-CE05-CALLER-CONSTRUCTOR-DOMAIN-CANDIDATE.json'
CE06 = P+'D5-I193-CE06-PLATFORM-CLOCK-GLOBAL-LEDGER-CANDIDATE.json'
CE05_REVIEW = P+'D5-I208-I207-documentary-review.json'
CE06_REVIEW = P+'D5-I210-I209-documentary-review.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
P03 = P+'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
P03_REVIEW = P+'D5-I138-P03-documentary-review.json'
PRIOR_RECON = P+'D5-I230-I229-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I230-I229-documentary-review.json'
PRIOR_AUDIT = P+'D5-I230-audit.py'
PRIOR_SEAL = P+'D5-I230-integrity.json'
PRIOR_DOC = 'docs/design/D5-I230-I229-W03-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I223-W04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
PREP = P+'D5-I231-preparation-review.json'
AUDIT = P+'D5-I231-audit.py'
SEAL = P+'D5-I231-integrity.json'
DOC = 'docs/design/D5-I231-W04-CALLER-PLATFORM-SERVICE.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W04_CALLER_PLATFORM_SERVICE_MISSING_SD01_ACTIVE_NOT_ADMITTED'


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
    plan,caller,platform,spec,contract,envelope = rd(PLAN),rd(CE05),rd(CE06),rd(SPEC),rd(CONTRACT),rd(P03)
    work = plan['work_packages'][3]
    pins = {**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 952
    inventory = sorted({PLAN,PRIOR_REVIEW,CE01,CE05,CE06,CE05_REVIEW,CE06_REVIEW,SPEC,PACK,CONTRACT,P03,P03_REVIEW})
    consumers = {'CE05':['W04'],'CE06':['W04'],'CE07':['W05','W06','W07','W08','W09'],'CE08':['W10'],'CE09':['W11'],'CE10':['W12'],'CE12':[]}
    requirements = []
    for path,group in [(CE05,'caller_constructor_requirements'),(CE06,'platform_requirements')]:
        for i,row in enumerate(rd(path)[group]):
            step = row['consumer_step']
            requirements.append(dict(id=row['id'],source=pin(path,'/'+group+'/'+str(i)),exact_requirement=row,
                consumer_step=step,work_package_consumers=consumers[step],
                deferred_from_W04=step not in ['CE05','CE06'],final_route_outside_prelaunch_plan=step=='CE12',
                actual_evidence=None,actual_primary_review=None,actual_separate_acceptance=None,accepted=False))
    service_groups = [
        ('SV01','platform_runtime_pin_set_and_validity','Exact platform/runtime/image/loader/domain/configuration and valid accepted scope; historical P03 is not successor evidence'),
        ('SV02','available_worker_requested_and_committed_heap','Real lower availability bounds for peak live requested and committed allocator heap under exact native/allocator/GC/lifetime/overlap model, not RSS/quota/reservation'),
        ('SV03','coordinator_child_resource_and_interference_scope','Complete coordinator/worker/children process scope and interference/shared resources; worker-only budgets cannot omit relevant contributors'),
        ('SV04','compatible_CPU_service_unit_rate_latency_or_WCET_assumptions','Authenticated compatible work/service unit, lower service curve and bounded delays, or justified exact-platform WCET; distinguish CPU time, wall time and process sums'),
        ('SV05','bounded_scheduler_locks_IO_child_completion_observation_delays','Complete scheduling/denied service/locks/IO/children/reap/exit-to-wait-return/startup/finalization delays with no unknown zero or unproved overlap subtraction'),
        ('SV06','admissible_signal_retry_interference_and_load_assumptions','Explicit admissible signal/retry/backoff/interference/load and validity assumptions, without free retry or hidden service'),
        ('SV07','clock_monotonicity_domain_and_latency_accounting','Accepted monotonic coordinator domain and error/observation/latency rules for exact True wait return and finally through tF; no host-clock adoption'),
        ('SV08','producer_authority_signature_and_validity','Genuine provider competence and authority for promised capacity/service, complete proof bodies, signature/provenance and current valid scope; not self-attestation by role label')]
    return dict(schema='d5.i231-w04-caller-platform-service-candidate.v1',increment='I231',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        work_package='W04',planned_deliverable_id=work['deliverable_id'],
        kind='NEGATIVE_CALLER_PLATFORM_CAPACITY_SERVICE_DOSSIER_NOT_I191_RECORD_NOT_PLATFORM_OR_LEDGER_IMPLEMENTATION_NOT_ACCEPTED_REAL_EVIDENCE_PACKAGE',
        status='W04_DOCUMENTARY_PREPARED_CALLER_PLATFORM_CAPACITY_SERVICE_MISSING_W02_W03_UNACCEPTED_SD01_ACTIVE_NOT_ADMITTED',
        input_pins=pins,work_package_binding=pin(PLAN,'/work_packages/3'),required_deliverables=work['deliverables'],required_exit_predicates=work['exit_predicates'],reject_if=work['reject_if'],needs_separate_future_authority_for=work['needs_separate_future_authority_for'],documentary_inventory=[pin(p) for p in inventory],
        dependency_gate=dict(source=pin(PRIOR_REVIEW,'/documentary_clarifications/0'),required_package_ids=work['depends_on'],W01_accepted=False,W02_accepted=False,W03_accepted=False,SD01_stop_active=True,
            actual_entry_authority_or_accepted_baseline=None,documentary_preparation_not_positive_dependency_progress=True,
            future_bundle_or_freeze_not_sole_antecedent_authentication=True),
        role_scope_matrix=[r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R02','R03','R06','R08']],
        actual_provider_operator_identity_competence_authority_or_validity=None,
        caller_policy=dict(source=pin(CE05),identity_and_capability=caller['identity_and_capability_policy'],
            actual_caller_state=caller['actual_caller_state'],cross_record_and_mapping=caller['cross_record_and_mapping_policy'],
            inherited_transport=caller['inherited_transport_policy'],
            no_appointment_UID_PID_fd_env_hash_frame_READY_or_signature_alone_grants_functional_execution=True),
        platform_policy=dict(source=pin(CE06),actual_platform_clock_ledger_state=platform['actual_platform_clock_ledger_state'],
            guarantee_evidence_inventory=platform['guarantee_evidence_inventory'],cross_record=platform['cross_record_policy'],
            clock_currentness=platform['clock_currentness_policy'],global_one_use=platform['global_one_use_policy'],
            inherited_transport=platform['inherited_transport_policy'],
            mechanism_evidence_not_actual_claim_or_runtime_backend=True),
        requirement_phase_ledger=requirements,
        service_evidence_ledger=[dict(id=i,source=pin(P03,'/'+key),required_material=text,
            actual_provider_or_attestation=None,actual_complete_proof_bodies=None,actual_runtime_platform_process_scope=None,actual_unit_or_metric=None,
            actual_lower_or_upper_bound=None,actual_validity_and_load_conditions=None,actual_compatibility_derivation=None,accepted=False)
            for i,key,text in service_groups],
        actual_capacity_state=dict(available_requested_heap_lower_bytes=None,available_committed_allocator_heap_lower_bytes=None,
            native_allocator_GC_and_metric_correspondence=None,coordinator_children_interference_or_overlap_proof=None,
            provider_and_authority=None,scope_and_validity=None,accepted=False),
        actual_service_state=dict(selected_service_or_WCET_route=None,work_unit=None,guaranteed_rate_unit=None,guaranteed_rate_lower_bound=None,
            service_curve_latency_upper_seconds=None,justified_exact_platform_WCET_upper_seconds=None,
            denied_service_wait_IO_scheduler_locks_child_observation_bounds=None,CPU_to_wall_process_window_derivation=None,
            provider_and_authority=None,scope_load_and_validity=None,accepted=False),
        heap_metric_policy=dict(source=pin(P03,'/available_worker_requested_and_committed_heap/worker_metric_definitions'),
            exact_metric_definitions=envelope['available_worker_requested_and_committed_heap']['worker_metric_definitions'],
            requested_and_committed_not_serialized_RSS_or_reserved_virtual_bytes=True,
            requested_reserve_or_product_limit_not_available_capacity=True,unknown_availability_not_zero_or_infeasibility=True),
        delay_requirements=[dict(source=pin(P03,'/bounded_scheduler_locks_IO_child_completion_observation_delays/delay_requirements/'+str(i)),exact_requirement=r,actual_evidence=None,accepted=False) for i,r in enumerate(envelope['bounded_scheduler_locks_IO_child_completion_observation_delays']['delay_requirements'])],
        candidate_budgets=dict(source=pin(CONTRACT),heap={k:contract['heap'][k] for k in ['requested_heap_candidate_bytes','committed_heap_candidate_bytes','unassigned_requested_reserve_bytes','allocator_overhead_candidate_bytes']},
            phase_budgets=contract['time']['phase_budgets'],worker_partition=contract['time']['worker_service_partition'],
            normative_markers=contract['time']['normative_markers'],ordered_interval_rule=contract['time']['ordered_interval_rule'],success_path_qualification=contract['time']['success_path_qualification'],
            success_seconds=900,unassigned_time_reserve_seconds=30,
            actual_capacity_service_heap_or900_proof=None,not_service_from_frequency_budget_watchdog_or_deadline=True,
            exact_True_wait_worker_tW_and_success_finally_tF_required=True,reserve_transfers_applied=0,resources_reserved=False,product_quotas_changed=False),
        schema_policy=dict(source=pin(PACK),definitions=[dict(name=n,source=pin(PACK,'/$defs/'+n),schema_fragment=rd(PACK)['$defs'][n]) for n in ['caller_identity','platform_custody','identity','evidence_reference','validity']],
            candidate_caller_body_cap_bytes=spec['record_caps_bytes']['caller_identity'],candidate_platform_body_cap_bytes=spec['record_caps_bytes']['platform_custody'],
            wrapper_not_positive_record_body=True,caps_not_actual_heap_CPU_or_service_guarantees=True,
            actual_body_sizes_or_fit_proof=None,actual_schema_codec_or_crypto_validation='NOT_RUN_NO_ACTUAL_BODY'),
        contract_rules=[dict(source=pin(SPEC,'/rules/'+str(i)),exact_rule=r) for i,r in enumerate(spec['rules']) if r['id'] in ['K02','K06','K07','K08','K09','K13','K14','K15','K16']],
        phase_boundary=dict(source=pin(PLAN,'/scope_authentication_and_freeze_order'),exact_plan_order=plan['scope_authentication_and_freeze_order'],
            genuine_actor_image_caller_platform_and_capacity_service_facts_before_W09_resource_acceptance_required=True,
            known_complete_proof_authors_and_bodies_before_W09_required=True,
            resource_scope_identity_and_service_guarantee_not_full_program_work_heap_or_phase_fit=True,
            final_resource_join_freeze_C_mapping_or_claim_not_new_reverse_W04_dependency=True,
            W10_freeze_reconciles_same_genuine_facts_not_forecast_authentication=True,
            final_record_order=['actor_registry','image_manifest','caller_identity','platform_custody'],
            C_consumer='W11_CE09',unique_current_mapping_consumer='W12_CE10',actual_claim_construction_receipt_consumer='CE12_DEFERRED_NOT_AUTHORIZED',
            unique_mapping_policy=dict(key=['configuration_epoch','SHA256(JCS(C))'],maps_to=['bundle','caller','image','protection_domain','ledger'],actual_mapping=None),
            preserved_CE12_boundary=plan['prelaunch_handoff_and_CE12'],actual_claim_or_replay_crash_restart_tests_required_or_performed=False,
            caller_and_platform_change_policy=caller['freeze_and_refresh'],actual_downstream_refresh_or_rebind=False),
        authority_and_costs=dict(source=pin(PLAN,'/authorization_boundary'),inherited_boundary=plan['authorization_boundary'],
            allowed_now=['READ_DOCUMENTS_GIT_HASHES','PREPARE_THIS_NEGATIVE_DOSSIER','RUN_OWN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT'],
            no_selection_configuration_probes_measurement_clock_ledger_claim_endpoints_processes_or_contacts=True,
            no_new_helpers_channels_fds_argv_inputs_outputs_or_ambient_trust=True,actual_external_material_or_provider=None,actual_action_specific_authority=None,
            all_per_attempt_lookup_freshness_identity_crypto_measurement_copies_clock_ledger_registry_receipt_native_IO_inside_complete_phases_and_resource_join=True,
            prior_enrollment_or_offline_not_free_work=True,unknown_cost_delay_or_availability_not_zero=True,quotas_or_reserves_applied=False),
        exit_predicate_dispositions=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/3/exit_predicates/'+str(i)),predicate=t,documentary_policy_prepared=True,actual_evidence=None,actual_primary_R02_R03_R06_review=None,actual_separate_R08_acceptance=None,accepted=False) for i,t in enumerate(work['exit_predicates'])],
        preserved_scope_and_gates=dict(inherited_scope_boundaries=plan['inherited_scope_boundaries'],preserved_negative_gates=plan['preserved_negative_gates'],prelaunch_handoff_and_CE12=plan['prelaunch_handoff_and_CE12'],existing_CE_dossiers_not_genuine_records_service_or_claim=True),
        current_effect=dict(W04_documentary_prepared=True,W01_accepted=False,W02_accepted=False,W03_accepted=False,W04_accepted=False,actual_entry_authority_verified=False,
            actual_caller_platform_capacity_service_clock_or_global_ledger_verified=False,actual_real_evidence_package_created=False,positive_I191_record_created=False,
            actual_evidence_accepted=0,work_packages_accepted=0,prelaunch_gates_closed=0,resource_obligations_closed=0,
            independent_acceptance=False,source_implementation_changed=False,product_or_components_executed=False,quotas_changed=False,reserves_changed=False,resource_reservations_created=False,rebind_applied=False,
            authority_or_destination_created=False,actual_claim_worker_or_receipt_created=False,execution_authorized=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),
        producer=dict(identity='Same Codex assistant/chat as I229/I230',documentary_preparer_only=True,actor_independent=False,competent_R02_attestation=False,competent_R03_resource_review=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_platform_selection_capacity_attestation_claim_or_execution_authority=True))


def validate(d):
    assert d['dependency_gate']['SD01_stop_active'] is True and d['dependency_gate']['W02_accepted'] is False and d['dependency_gate']['W03_accepted'] is False, 'dependency_bypass'
    assert d['current_effect']['W04_accepted'] is False, 'W04_accepted'
    assert d['caller_policy']['no_appointment_UID_PID_fd_env_hash_frame_READY_or_signature_alone_grants_functional_execution'], 'identifier_as_permission'
    assert d['caller_policy']['actual_caller_state']['actual_caller_or_backend_selected'] is False, 'selected_caller'
    assert all(r['actual_verified'] is False for r in d['platform_policy']['guarantee_evidence_inventory']), 'guarantee_by_flag'
    assert d['platform_policy']['clock_currentness']['actual_clock_error_or_sample'] is None, 'zero_clock_error'
    assert d['platform_policy']['clock_currentness']['host_clock_or_client_date_is_not_accepted_runtime_clock'], 'host_clock_as_trusted'
    assert d['platform_policy']['global_one_use']['global_across_all_approved_callers_domains_and_restarts'], 'per_caller_ledger'
    assert d['platform_policy']['global_one_use']['free_retry_or_invocation_reuse_permitted'] is False, 'free_retry'
    assert d['platform_policy']['global_one_use']['actual_claim_or_receipt_required_for_CE06_mechanism_evidence'] is False, 'premature_claim'
    assert d['platform_policy']['global_one_use']['actual_live_claim_replay_crash_restart_or_endpoint_test_performed'] is False, 'live_probe'
    assert d['platform_policy']['mechanism_evidence_not_actual_claim_or_runtime_backend'], 'mechanism_as_claim'
    assert d['actual_capacity_state']['available_requested_heap_lower_bytes'] is None, 'budget_as_capacity'
    assert d['actual_service_state']['guaranteed_rate_lower_bound'] is None, 'invented_rate'
    assert d['actual_service_state']['service_curve_latency_upper_seconds'] is None, 'unknown_delay_zero'
    assert d['candidate_budgets']['not_service_from_frequency_budget_watchdog_or_deadline'], 'watchdog_as_service'
    assert d['candidate_budgets']['exact_True_wait_worker_tW_and_success_finally_tF_required'], 'wrong_tW'
    assert d['candidate_budgets']['reserve_transfers_applied'] == 0, 'reserve_transfer'
    assert d['schema_policy']['caps_not_actual_heap_CPU_or_service_guarantees'], 'cap_as_service'
    assert d['phase_boundary']['unique_mapping_policy']['actual_mapping'] is None, 'invented_mapping'
    assert d['phase_boundary']['genuine_actor_image_caller_platform_and_capacity_service_facts_before_W09_resource_acceptance_required'], 'late_authentication'
    assert d['phase_boundary']['W10_freeze_reconciles_same_genuine_facts_not_forecast_authentication'], 'forecast_freeze'
    assert d['phase_boundary']['final_resource_join_freeze_C_mapping_or_claim_not_new_reverse_W04_dependency'], 'reverse_dependency'
    assert d['authority_and_costs']['no_new_helpers_channels_fds_argv_inputs_outputs_or_ambient_trust'], 'hidden_channel'
    assert d['authority_and_costs']['all_per_attempt_lookup_freshness_identity_crypto_measurement_copies_clock_ledger_registry_receipt_native_IO_inside_complete_phases_and_resource_join'], 'omitted_cost'
    assert d['authority_and_costs']['quotas_or_reserves_applied'] is False, 'quota_change'
    assert d['current_effect']['execution_authorized'] is False, 'execution_authorized'
    assert d['current_effect']['D5_closed'] is False, 'D5_closed'
    assert d == build_candidate(), 'Candidate differs from source reconstruction'
    check_pointers(d)


def rejection_checks(d):
    cases = [
        ('dependency_bypass',('dependency_gate','SD01_stop_active'),False),
        ('W04_accepted',('current_effect','W04_accepted'),True),
        ('identifier_as_permission',('caller_policy','no_appointment_UID_PID_fd_env_hash_frame_READY_or_signature_alone_grants_functional_execution'),False),
        ('selected_caller',('caller_policy','actual_caller_state','actual_caller_or_backend_selected'),True),
        ('guarantee_by_flag',('platform_policy','guarantee_evidence_inventory',0,'actual_verified'),True),
        ('zero_clock_error',('platform_policy','clock_currentness','actual_clock_error_or_sample'),0),
        ('host_clock_as_trusted',('platform_policy','clock_currentness','host_clock_or_client_date_is_not_accepted_runtime_clock'),False),
        ('per_caller_ledger',('platform_policy','global_one_use','global_across_all_approved_callers_domains_and_restarts'),False),
        ('free_retry',('platform_policy','global_one_use','free_retry_or_invocation_reuse_permitted'),True),
        ('premature_claim',('platform_policy','global_one_use','actual_claim_or_receipt_required_for_CE06_mechanism_evidence'),True),
        ('live_probe',('platform_policy','global_one_use','actual_live_claim_replay_crash_restart_or_endpoint_test_performed'),True),
        ('mechanism_as_claim',('platform_policy','mechanism_evidence_not_actual_claim_or_runtime_backend'),False),
        ('budget_as_capacity',('actual_capacity_state','available_requested_heap_lower_bytes'),11811160064),
        ('invented_rate',('actual_service_state','guaranteed_rate_lower_bound'),1),
        ('unknown_delay_zero',('actual_service_state','service_curve_latency_upper_seconds'),0),
        ('watchdog_as_service',('candidate_budgets','not_service_from_frequency_budget_watchdog_or_deadline'),False),
        ('wrong_tW',('candidate_budgets','exact_True_wait_worker_tW_and_success_finally_tF_required'),False),
        ('reserve_transfer',('candidate_budgets','reserve_transfers_applied'),1),
        ('cap_as_service',('schema_policy','caps_not_actual_heap_CPU_or_service_guarantees'),False),
        ('invented_mapping',('phase_boundary','unique_mapping_policy','actual_mapping'),'UNAUTHENTICATED_TEST_LABEL_NOT_MAPPING'),
        ('late_authentication',('phase_boundary','genuine_actor_image_caller_platform_and_capacity_service_facts_before_W09_resource_acceptance_required'),False),
        ('forecast_freeze',('phase_boundary','W10_freeze_reconciles_same_genuine_facts_not_forecast_authentication'),False),
        ('reverse_dependency',('phase_boundary','final_resource_join_freeze_C_mapping_or_claim_not_new_reverse_W04_dependency'),False),
        ('hidden_channel',('authority_and_costs','no_new_helpers_channels_fds_argv_inputs_outputs_or_ambient_trust'),False),
        ('omitted_cost',('authority_and_costs','all_per_attempt_lookup_freshness_identity_crypto_measurement_copies_clock_ledger_registry_receipt_native_IO_inside_complete_phases_and_resource_join'),False),
        ('quota_change',('authority_and_costs','quotas_or_reserves_applied'),True),
        ('execution_authorized',('current_effect','execution_authorized'),True),
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
    assert len(d['requirement_phase_ledger']) == 23 and sum(not r['deferred_from_W04'] for r in d['requirement_phase_ledger']) == 13
    assert sum(r['final_route_outside_prelaunch_plan'] for r in d['requirement_phase_ledger']) == 2
    for row in d['requirement_phase_ledger']:
        assert row['exact_requirement'] == fragment(row['source'])
        assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    assert len(d['platform_policy']['guarantee_evidence_inventory']) == 8
    assert {r['guarantee'] for r in d['platform_policy']['guarantee_evidence_inventory']} == set(rd(PACK)['$defs']['platform_custody']['properties']['guarantees']['required'])
    for row in d['platform_policy']['guarantee_evidence_inventory']:
        assert row['actual_verified'] is False and row['accepted'] is False
        assert all(v is None for k,v in row.items() if k.startswith('actual_') and k!='actual_verified')
    for state in [d['caller_policy']['actual_caller_state'],d['platform_policy']['actual_platform_clock_ledger_state']]:
        assert all(v is None or v is False for v in state.values())
    for state in [d['actual_capacity_state'],d['actual_service_state']]:
        assert state['accepted'] is False and all(v is None for k,v in state.items() if k!='accepted')
    assert len(d['service_evidence_ledger']) == 8 and len(d['delay_requirements']) == 8 and len(d['schema_policy']['definitions']) == 5
    assert [r['id'] for r in d['role_scope_matrix']] == ['R02','R03','R06','R08']
    assert all(r['canonical_actor_id'] is None and r['accepted_appointment'] is False for r in d['role_scope_matrix'])
    for key,value in d['current_effect'].items():
        if key == 'W04_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False, key
    return dict(schema='d5.i231-preparation-review.v1',increment='I231',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,candidate=pin(SUBJECT),work_package=pin(PLAN,'/work_packages/3'),
        counts=dict(input_pins=952,requirement_rows=23,W04_rows=13,deferred_rows=10,final_route_CE12_rows=2,platform_guarantees=8,service_evidence_categories=8,delay_requirements=8,schema_fragments=5,unassigned_review_roles=4,pending_exits=3),
        source_reconstruction=dict(I230_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        limitations=['W01-W03 remain unaccepted and SD01 active. W04 is negative documentary preparation only; no accepted real evidence package or actual caller/platform/service/ledger record.',
            'Provider authority, caller/constructor/domain/origin, eight guarantees, actual available memory, CPU/IO/service/WCET, compatible units/latencies, clock/epoch/revocation, durable atomic global mechanism and mappings remain missing.',
            'Mechanism evidence is not an actual claim. Final resource join, W10 freeze, C/W11, mapping/W12 and CE12 events remain separate; actual antecedents must be authenticated before W09, not borrowed from later signatures.',
            'Same assistant checks are not competent R02 attestation, independent R03/R06 review or separate R08 acceptance. No service/backend/provider is selected, contacted, configured or probed.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I231-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/policy/role checks only; no product/components imports/build/compile/tests/benchmarks, codec/crypto positives, platform/clock/ledger/service sampling or probes, endpoints/processes/claim/replay/crash/restart/signing/keygen/enrollment/provisioning/contact.',
            over400_lines=True,reason='One negative W04 dossier with exact pins, caller/guarantee/service/delay/phase matrices, checks and preservation; overage declared. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_platform_selection_attestation_claim_or_execution_authority=True))


def main():
    review = build_review()
    assert rd(PREP) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published639'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 644
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i231-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published644'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == review['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I231',historical_pins=952,preserved_published_files=644,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],current_effect=review['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
