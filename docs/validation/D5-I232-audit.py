#!/usr/bin/env python3
"""I232 documentary review of W04 caller/platform/service. No product or trust operations."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '50bc209cba4f825aa5e9719ed9f6f10be0c7d1b2'
DATE = '2026-11-24'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
SUBJECT = P+'D5-I223-W04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE05 = P+'D5-I193-CE05-CALLER-CONSTRUCTOR-DOMAIN-CANDIDATE.json'
CE06 = P+'D5-I193-CE06-PLATFORM-CLOCK-GLOBAL-LEDGER-CANDIDATE.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
P03 = P+'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
ENTRY_REVIEW = P+'D5-I230-I229-documentary-review.json'
PRIOR_AUDIT = P+'D5-I231-audit.py'
PRIOR_PREP = P+'D5-I231-preparation-review.json'
PRIOR_SEAL = P+'D5-I231-integrity.json'
PRIOR_DOC = 'docs/design/D5-I231-W04-CALLER-PLATFORM-SERVICE.md'
PRIOR_FILES = {SUBJECT,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I232-I231-source-reconstruction.json'
REVIEW = P+'D5-I232-I231-documentary-review.json'
AUDIT = P+'D5-I232-audit.py'
SEAL = P+'D5-I232-integrity.json'
DOC = 'docs/design/D5-I232-I231-W04-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W04_REVIEW_CALLER_PLATFORM_SERVICE_MISSING_NOT_ADMITTED'


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
    assert d['dependency_gate']['future_bundle_or_freeze_not_sole_antecedent_authentication'], 'future_authority'
    assert d['caller_policy']['no_appointment_UID_PID_fd_env_hash_frame_READY_or_signature_alone_grants_functional_execution'], 'identifier_permission'
    assert d['caller_policy']['actual_caller_state']['actual_caller_or_backend_selected'] is False, 'selected_caller'
    assert all(r['actual_verified'] is False for r in d['platform_policy']['guarantee_evidence_inventory']), 'guarantee_flag'
    assert d['platform_policy']['clock_currentness']['actual_clock_error_or_sample'] is None, 'clock_zero'
    assert d['platform_policy']['clock_currentness']['host_clock_or_client_date_is_not_accepted_runtime_clock'], 'host_clock'
    assert d['platform_policy']['global_one_use']['global_across_all_approved_callers_domains_and_restarts'], 'partitioned_ledger'
    assert d['platform_policy']['global_one_use']['high_water_epoch_and_atomic_durable_rollback_crash_proof_required'], 'waived_durability'
    assert d['platform_policy']['global_one_use']['free_retry_or_invocation_reuse_permitted'] is False, 'free_retry'
    assert d['platform_policy']['global_one_use']['actual_claim_or_receipt_required_for_CE06_mechanism_evidence'] is False, 'premature_claim'
    assert d['platform_policy']['global_one_use']['actual_live_claim_replay_crash_restart_or_endpoint_test_performed'] is False, 'live_probe'
    assert d['platform_policy']['mechanism_evidence_not_actual_claim_or_runtime_backend'], 'mechanism_as_claim'
    assert d['actual_capacity_state']['available_requested_heap_lower_bytes'] is None, 'budget_as_capacity'
    assert d['actual_service_state']['guaranteed_rate_lower_bound'] is None, 'invented_rate'
    assert d['actual_service_state']['service_curve_latency_upper_seconds'] is None, 'unknown_delay_zero'
    assert d['actual_service_state']['justified_exact_platform_WCET_upper_seconds'] is None, 'invented_WCET'
    assert d['heap_metric_policy']['requested_and_committed_not_serialized_RSS_or_reserved_virtual_bytes'], 'RSS_as_heap'
    assert d['candidate_budgets']['not_service_from_frequency_budget_watchdog_or_deadline'], 'watchdog_as_service'
    assert d['candidate_budgets']['exact_True_wait_worker_tW_and_success_finally_tF_required'], 'wrong_tW'
    assert d['candidate_budgets']['reserve_transfers_applied'] == 0, 'reserve_transfer'
    assert d['schema_policy']['caps_not_actual_heap_CPU_or_service_guarantees'], 'cap_as_service'
    assert d['phase_boundary']['unique_mapping_policy']['actual_mapping'] is None, 'invented_mapping'
    assert d['phase_boundary']['genuine_actor_image_caller_platform_and_capacity_service_facts_before_W09_resource_acceptance_required'], 'late_authentication'
    assert d['phase_boundary']['W10_freeze_reconciles_same_genuine_facts_not_forecast_authentication'], 'forecast_freeze'
    assert d['phase_boundary']['final_resource_join_freeze_C_mapping_or_claim_not_new_reverse_W04_dependency'], 'reverse_dependency'
    assert d['phase_boundary']['resource_scope_identity_and_service_guarantee_not_full_program_work_heap_or_phase_fit'], 'service_as_program_fit'
    assert d['authority_and_costs']['no_new_helpers_channels_fds_argv_inputs_outputs_or_ambient_trust'], 'hidden_channel'
    assert d['authority_and_costs']['all_per_attempt_lookup_freshness_identity_crypto_measurement_copies_clock_ledger_registry_receipt_native_IO_inside_complete_phases_and_resource_join'], 'omitted_cost'
    assert d['authority_and_costs']['quotas_or_reserves_applied'] is False, 'quota_change'
    assert all(r['accepted'] is False for r in d['exit_predicate_dispositions']), 'exit_acceptance'
    assert d['current_effect']['W04_accepted'] is False and d['current_effect']['execution_authorized'] is False and d['current_effect']['D5_closed'] is False, 'positive_effect'


def inspect_scope(d):
    """Independent source comparisons, not I231 candidate-builder equality."""
    check_negative_boundaries(d)
    plan,caller,platform,contract,envelope,spec = rd(PLAN),rd(CE05),rd(CE06),rd(CONTRACT),rd(P03),rd(SPEC)
    work = plan['work_packages'][3]
    assert d['work_package'] == work['id'] == 'W04' and fragment(d['work_package_binding']) == work
    assert d['planned_deliverable_id'] == work['deliverable_id']
    for target,source in [('required_deliverables','deliverables'),('required_exit_predicates','exit_predicates'),('reject_if','reject_if'),('needs_separate_future_authority_for','needs_separate_future_authority_for')]:
        assert d[target] == work[source]
    dep = d['dependency_gate']
    assert dep['required_package_ids'] == work['depends_on'] == ['W02','W03']
    assert dep['W01_accepted'] is False and dep['W02_accepted'] is False and dep['W03_accepted'] is False
    assert dep['actual_entry_authority_or_accepted_baseline'] is None and dep['documentary_preparation_not_positive_dependency_progress']
    assert fragment(dep['source']) == rd(ENTRY_REVIEW)['documentary_clarifications'][0]
    assert d['role_scope_matrix'] == [r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R02','R03','R06','R08']]
    assert work['primary_review_roles'] == ['R02','R03','R06'] and work['separate_acceptor_role'] == 'R08'
    assert d['actual_provider_operator_identity_competence_authority_or_validity'] is None
    cp = d['caller_policy']
    for target,source in [('identity_and_capability','identity_and_capability_policy'),('actual_caller_state','actual_caller_state'),('cross_record_and_mapping','cross_record_and_mapping_policy'),('inherited_transport','inherited_transport_policy')]:
        assert cp[target] == caller[source]
    pp = d['platform_policy']
    for target,source in [('actual_platform_clock_ledger_state','actual_platform_clock_ledger_state'),('guarantee_evidence_inventory','guarantee_evidence_inventory'),('cross_record','cross_record_policy'),('clock_currentness','clock_currentness_policy'),('global_one_use','global_one_use_policy'),('inherited_transport','inherited_transport_policy')]:
        assert pp[target] == platform[source]
    for state in [cp['actual_caller_state'],pp['actual_platform_clock_ledger_state']]:
        assert all(v is None or v is False for v in state.values())
    assert cp['identity_and_capability']['human_requester_and_software_principal_namespaces_separate']
    assert cp['inherited_transport']['explicit_control_pipe_count'] == pp['inherited_transport']['explicit_control_pipe_count'] == 2
    assert cp['inherited_transport']['observed_worker_operand_count'] == pp['inherited_transport']['observed_worker_operand_count'] == 6
    assert cp['cross_record_and_mapping']['requester_projection_equality'] == 'C.runtime_requester_id == caller.accountable_requester_actor_id'
    assert cp['cross_record_and_mapping']['protection_domain_equality'] == 'platform.domain_id == caller.protection_domain_id'
    guarantees = pp['guarantee_evidence_inventory']
    assert len(guarantees) == 8 and {r['guarantee'] for r in guarantees} == set(rd(PACK)['$defs']['platform_custody']['properties']['guarantees']['required'])
    for row in guarantees:
        assert row['accepted'] is False and row['actual_verified'] is False
        assert all(v is None for k,v in row.items() if k.startswith('actual_') and k!='actual_verified')
    clock,ledger = pp['clock_currentness'],pp['global_one_use']
    assert clock['max_UTC_error_seconds'] == 5 and clock['max_snapshot_lifetime_seconds'] == 3600
    assert clock['actual_trusted_now'] is None and clock['instantaneous_all_revocation_discovery_claimed'] is False
    assert clock['no_TOFU_stale_cache_hidden_online_or_file_lookup']
    assert ledger['tuple_fields'] == ['trust_context_sha256','runtime_request_sha256','invocation_id']
    assert ledger['actual_tuple_or_claim'] is None and ledger['actual_ledger_domain_or_epoch'] is None
    assert ledger['uncertain_or_partial_claim_spends_or_rejects'] and ledger['parent_child_is_one_correlated_invocation'] and ledger['mapping_and_ledger_domain_must_agree']
    consumers = {'CE05':['W04'],'CE06':['W04'],'CE07':['W05','W06','W07','W08','W09'],'CE08':['W10'],'CE09':['W11'],'CE10':['W12'],'CE12':[]}
    expected = [(CE05,'caller_constructor_requirements',i,r) for i,r in enumerate(caller['caller_constructor_requirements'])]
    expected += [(CE06,'platform_requirements',i,r) for i,r in enumerate(platform['platform_requirements'])]
    rows = d['requirement_phase_ledger']
    assert len(rows) == len(expected) == 23
    for row,(path,group,i,original) in zip(rows,expected):
        assert row['source'] == pin(path,'/'+group+'/'+str(i)) and row['exact_requirement'] == original == fragment(row['source'])
        assert row['id'] == original['id'] and row['consumer_step'] == original['consumer_step']
        assert row['work_package_consumers'] == consumers[original['consumer_step']]
        assert row['deferred_from_W04'] is (original['consumer_step'] not in ['CE05','CE06'])
        assert row['final_route_outside_prelaunch_plan'] is (original['consumer_step']=='CE12')
        assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    assert sum(not r['deferred_from_W04'] for r in rows) == 13 and sum(r['final_route_outside_prelaunch_plan'] for r in rows) == 2
    service_keys = ['platform_runtime_pin_set_and_validity','available_worker_requested_and_committed_heap','coordinator_child_resource_and_interference_scope','compatible_CPU_service_unit_rate_latency_or_WCET_assumptions','bounded_scheduler_locks_IO_child_completion_observation_delays','admissible_signal_retry_interference_and_load_assumptions','clock_monotonicity_domain_and_latency_accounting','producer_authority_signature_and_validity']
    assert len(d['service_evidence_ledger']) == 8
    for row,key in zip(d['service_evidence_ledger'],service_keys):
        assert row['source'] == pin(P03,'/'+key) and row['required_material']
        assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    for state in [d['actual_capacity_state'],d['actual_service_state']]:
        assert state['accepted'] is False and all(v is None for k,v in state.items() if k!='accepted')
    metric = d['heap_metric_policy']
    assert metric['exact_metric_definitions'] == envelope['available_worker_requested_and_committed_heap']['worker_metric_definitions'] == fragment(metric['source'])
    assert metric['requested_reserve_or_product_limit_not_available_capacity'] and metric['unknown_availability_not_zero_or_infeasibility']
    delays = envelope['bounded_scheduler_locks_IO_child_completion_observation_delays']['delay_requirements']
    assert len(d['delay_requirements']) == len(delays) == 8
    for row,original in zip(d['delay_requirements'],delays):
        assert row['exact_requirement'] == original == fragment(row['source'])
        assert row['actual_evidence'] is None and row['accepted'] is False
    budgets = d['candidate_budgets']
    assert budgets['source'] == pin(CONTRACT)
    assert budgets['heap'] == {k:contract['heap'][k] for k in ['requested_heap_candidate_bytes','committed_heap_candidate_bytes','unassigned_requested_reserve_bytes','allocator_overhead_candidate_bytes']}
    for key in ['phase_budgets','normative_markers','ordered_interval_rule','success_path_qualification']:
        assert budgets[key] == contract['time'][key]
    assert budgets['worker_partition'] == contract['time']['worker_service_partition']
    assert budgets['success_seconds'] == 900 and budgets['unassigned_time_reserve_seconds'] == 30
    assert budgets['actual_capacity_service_heap_or900_proof'] is None and budgets['resources_reserved'] is False and budgets['product_quotas_changed'] is False
    schemas = d['schema_policy']
    assert [r['name'] for r in schemas['definitions']] == ['caller_identity','platform_custody','identity','evidence_reference','validity']
    for row in schemas['definitions']:
        assert row['schema_fragment'] == rd(PACK)['$defs'][row['name']] == fragment(row['source'])
    assert schemas['candidate_caller_body_cap_bytes'] == spec['record_caps_bytes']['caller_identity'] == 8192
    assert schemas['candidate_platform_body_cap_bytes'] == spec['record_caps_bytes']['platform_custody'] == 16384
    assert schemas['wrapper_not_positive_record_body'] and schemas['actual_body_sizes_or_fit_proof'] is None
    assert schemas['actual_schema_codec_or_crypto_validation'] == 'NOT_RUN_NO_ACTUAL_BODY'
    phase = d['phase_boundary']
    assert phase['exact_plan_order'] == plan['scope_authentication_and_freeze_order'] == fragment(phase['source'])
    assert phase['known_complete_proof_authors_and_bodies_before_W09_required']
    assert phase['final_record_order'] == ['actor_registry','image_manifest','caller_identity','platform_custody']
    assert phase['C_consumer'] == 'W11_CE09' and phase['unique_current_mapping_consumer'] == 'W12_CE10' and phase['actual_claim_construction_receipt_consumer'] == 'CE12_DEFERRED_NOT_AUTHORIZED'
    assert phase['unique_mapping_policy']['key'] == ['configuration_epoch','SHA256(JCS(C))']
    assert phase['unique_mapping_policy']['maps_to'] == ['bundle','caller','image','protection_domain','ledger']
    assert phase['preserved_CE12_boundary'] == plan['prelaunch_handoff_and_CE12']
    assert phase['actual_claim_or_replay_crash_restart_tests_required_or_performed'] is False
    assert phase['caller_and_platform_change_policy'] == caller['freeze_and_refresh'] and phase['actual_downstream_refresh_or_rebind'] is False
    cost = d['authority_and_costs']
    assert cost['inherited_boundary'] == plan['authorization_boundary'] == fragment(cost['source'])
    assert cost['inherited_boundary']['current_run_command'] is None and all(v is False for k,v in cost['inherited_boundary'].items() if k.endswith('_authorized'))
    assert len(cost['allowed_now']) == 4 and cost['no_selection_configuration_probes_measurement_clock_ledger_claim_endpoints_processes_or_contacts']
    assert cost['actual_external_material_or_provider'] is None and cost['actual_action_specific_authority'] is None
    assert cost['prior_enrollment_or_offline_not_free_work'] and cost['unknown_cost_delay_or_availability_not_zero']
    exits = d['exit_predicate_dispositions']
    assert len(exits) == 3 and [r['predicate'] for r in exits] == work['exit_predicates']
    for row in exits:
        assert row['documentary_policy_prepared'] is True and fragment(row['source']) == row['predicate']
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
    assert [row['exact_rule'] for row in d['contract_rules']] == [r for r in spec['rules'] if r['id'] in ['K02','K06','K07','K08','K09','K13','K14','K15','K16']]
    for row in d['contract_rules']:
        assert fragment(row['source']) == row['exact_rule']
    preserved = d['preserved_scope_and_gates']
    for key in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']:
        assert preserved[key] == plan[key]
    for row in preserved['preserved_negative_gates']:
        assert fragment({**row['source'],'json_pointer':row['json_pointer']}) == row['observed_value']
    assert preserved['existing_CE_dossiers_not_genuine_records_service_or_claim']
    for key,value in d['current_effect'].items():
        if key == 'W04_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False
    assert all(d['producer'][k] is False for k in ['actor_independent','competent_R02_attestation','competent_R03_resource_review','competent_R06_review','separate_R08_acceptance','external_contacts_made'])
    check_pointers(d)


def reconstruct():
    d = rd(SUBJECT)
    pins = {**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 957
    verify_blobs(pins)
    inspect_scope(d)
    criteria = [
        ('RC01','Three I223 W04 deliverables/exits and exact dependency/authority/rejection clauses','/work_package_binding'),
        ('RC02','W01-W03 unaccepted, SD01 active and no future authority bootstrap','/dependency_gate'),
        ('RC03','Human requester/software caller and four genuine review roles remain unassigned','/role_scope_matrix'),
        ('RC04','Caller custody and bootstrap-only policy do not grant functional permission','/caller_policy'),
        ('RC05','Eight exact platform guarantee slots remain without proof or verification','/platform_policy/guarantee_evidence_inventory'),
        ('RC06','Clock error/lifetime/currentness/revocation requirements retained without host/zero inference','/platform_policy/clock_currentness'),
        ('RC07','Global atomic/durable/high-water/rollback/crash one-use mechanism is not actual claim','/platform_policy/global_one_use'),
        ('RC08','23 exact requirements map to13 W04 and10 deferred rows; two CE12 references outside prelaunch','/requirement_phase_ledger'),
        ('RC09','Eight historical P03 reference categories do not attest successor service/capacity','/service_evidence_ledger'),
        ('RC10','Requested/committed/native/GC/process scope metrics distinct from RSS, reservation and quotas','/heap_metric_policy'),
        ('RC11','Compatible work/service units, service curve or justified WCET remain missing','/actual_service_state'),
        ('RC12','Eight exact delay requirements remain unproved; no unknown-zero or unproved overlap subtraction','/delay_requirements'),
        ('RC13','Candidate heap/time budgets preserve exact True wait return/finally without reserve transfer or900 proof','/candidate_budgets'),
        ('RC14','Five exact schemas and8192/16384 candidate body caps are not positive records or resource guarantees','/schema_policy'),
        ('RC15','Genuine antecedents before W09; later freeze/C/mapping/CE12 do not back-authenticate or add reverse dependency','/phase_boundary'),
        ('RC16','All per-attempt costs inside phases/resources; no helpers/probes/execution/quota authority','/authority_and_costs'),
        ('RC17','Three exits, actual evidence and separate competent decisions remain pending','/exit_predicate_dispositions'),
        ('RC18','Historical certificate, inherited constraints, deferred CE12 and no actual gate/resource/D5 promotion','/preserved_scope_and_gates')]
    return dict(schema='d5.i232-i231-source-reconstruction.v1',increment='I232',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        subject=pin(SUBJECT),plan=pin(PLAN,'/work_packages/3'),input_pins=pins,
        criteria=[dict(id=i,criterion=t,subject=pin(SUBJECT,p),result='DOCUMENTARY_CONSISTENCY_CONFIRMED_NOT_REAL_ACCEPTANCE') for i,t,p in criteria],
        requirement_phase_mapping=[dict(id=r['id'],source=r['source'],consumer_step=r['consumer_step'],work_package_consumers=r['work_package_consumers'],deferred=r['deferred_from_W04'],final_route=r['final_route_outside_prelaunch_plan'],actually_accepted=False) for r in d['requirement_phase_ledger']],
        counts=dict(input_pins=957,criteria=18,requirements=23,W04_rows=13,deferred_rows=10,CE12_rows=2,guarantees=8,service_categories=8,delay_requirements=8,schemas=5,unassigned_review_roles=4,pending_exits=3),
        current_effect={**d['current_effect'],'W04_documentary_reviewed':True},methodological_review_not_R02_attestation_independent_R03_R06_or_separate_R08=True)


def rejection_checks():
    cases = [
        ('SD01_bypass',('dependency_gate','SD01_stop_active'),False),
        ('future_authority',('dependency_gate','future_bundle_or_freeze_not_sole_antecedent_authentication'),False),
        ('identifier_permission',('caller_policy','no_appointment_UID_PID_fd_env_hash_frame_READY_or_signature_alone_grants_functional_execution'),False),
        ('selected_caller',('caller_policy','actual_caller_state','actual_caller_or_backend_selected'),True),
        ('guarantee_flag',('platform_policy','guarantee_evidence_inventory',0,'actual_verified'),True),
        ('clock_zero',('platform_policy','clock_currentness','actual_clock_error_or_sample'),0),
        ('host_clock',('platform_policy','clock_currentness','host_clock_or_client_date_is_not_accepted_runtime_clock'),False),
        ('partitioned_ledger',('platform_policy','global_one_use','global_across_all_approved_callers_domains_and_restarts'),False),
        ('waived_durability',('platform_policy','global_one_use','high_water_epoch_and_atomic_durable_rollback_crash_proof_required'),False),
        ('free_retry',('platform_policy','global_one_use','free_retry_or_invocation_reuse_permitted'),True),
        ('premature_claim',('platform_policy','global_one_use','actual_claim_or_receipt_required_for_CE06_mechanism_evidence'),True),
        ('live_probe',('platform_policy','global_one_use','actual_live_claim_replay_crash_restart_or_endpoint_test_performed'),True),
        ('mechanism_as_claim',('platform_policy','mechanism_evidence_not_actual_claim_or_runtime_backend'),False),
        ('budget_as_capacity',('actual_capacity_state','available_requested_heap_lower_bytes'),11811160064),
        ('invented_rate',('actual_service_state','guaranteed_rate_lower_bound'),1),
        ('unknown_delay_zero',('actual_service_state','service_curve_latency_upper_seconds'),0),
        ('invented_WCET',('actual_service_state','justified_exact_platform_WCET_upper_seconds'),900),
        ('RSS_as_heap',('heap_metric_policy','requested_and_committed_not_serialized_RSS_or_reserved_virtual_bytes'),False),
        ('watchdog_as_service',('candidate_budgets','not_service_from_frequency_budget_watchdog_or_deadline'),False),
        ('wrong_tW',('candidate_budgets','exact_True_wait_worker_tW_and_success_finally_tF_required'),False),
        ('reserve_transfer',('candidate_budgets','reserve_transfers_applied'),1),
        ('cap_as_service',('schema_policy','caps_not_actual_heap_CPU_or_service_guarantees'),False),
        ('invented_mapping',('phase_boundary','unique_mapping_policy','actual_mapping'),'UNAUTHENTICATED_TEST_LABEL_NOT_MAPPING'),
        ('late_authentication',('phase_boundary','genuine_actor_image_caller_platform_and_capacity_service_facts_before_W09_resource_acceptance_required'),False),
        ('forecast_freeze',('phase_boundary','W10_freeze_reconciles_same_genuine_facts_not_forecast_authentication'),False),
        ('reverse_dependency',('phase_boundary','final_resource_join_freeze_C_mapping_or_claim_not_new_reverse_W04_dependency'),False),
        ('service_as_program_fit',('phase_boundary','resource_scope_identity_and_service_guarantee_not_full_program_work_heap_or_phase_fit'),False),
        ('hidden_channel',('authority_and_costs','no_new_helpers_channels_fds_argv_inputs_outputs_or_ambient_trust'),False),
        ('omitted_cost',('authority_and_costs','all_per_attempt_lookup_freshness_identity_crypto_measurement_copies_clock_ledger_registry_receipt_native_IO_inside_complete_phases_and_resource_join'),False),
        ('quota_change',('authority_and_costs','quotas_or_reserves_applied'),True),
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
    return dict(schema='d5.i232-i231-documentary-review.v1',increment='I232',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,subject=pin(SUBJECT),reconstruction=pin(RECON),verdict='W04_DOCUMENTARY_CALLER_PLATFORM_SERVICE_BOUNDARIES_CONSISTENT_REAL_EVIDENCE_MISSING_NOT_ACCEPTED',
        findings=[],finding_count=0,criteria=rec['criteria'],counts=rec['counts'],
        documentary_clarifications=[
            dict(id='N01',subject='Authority and actual identities',disposition='W01-W04 remain unaccepted and SD01 active. Caller identities, appointments, fd/PID/UID/hash/frame/READY/signature or policy literals do not alone grant origin, capability or functional execution. Same assistant review is not competent R02 attestation, independent R03/R06 or separate R08 acceptance.'),
            dict(id='N02',subject='Availability/service versus candidate budgets',disposition='Requested/committed/native/allocator/GC/process metrics and actual lower availability bounds need genuine exact-platform authority/evidence. Budgets, reservations, RSS, quotas, frequency/watchdog/deadline and unknowns do not supply capacity, compatible service curve/WCET, bounded delays or successful900 proof. W04 service facts are not complete program work/heap/phase fit.'),
            dict(id='N03',subject='Global mechanism versus actual claim',disposition='Eight guarantees, accepted clock/epoch/currentness and globally shared durable/high-water/rollback/crash one-use mechanism remain genuine evidence requirements. No host-clock/zero-error, per-caller namespace, free retry or mechanism-as-claim is accepted. Actual claim/construction/receipt remains CE12, not a prerequisite to its own mechanism evidence.'),
            dict(id='N04',subject='Phase and antecedent boundaries',disposition='23 rows map to13 W04 and10 deferred rows including two CE12 references outside prelaunch. Genuine baseline actor/image/caller/platform/capacity/service and proof authors/bodies must precede W09 acceptance. W10 reconciles the same accepted facts; C/W11, mapping/W12 or later signatures cannot retroactively authenticate them or create a reverse baseline dependency.'),
            dict(id='N05',subject='Transport, costs and final route',disposition='I189 transport and full per-attempt lookup/freshness/identity/crypto/measurement/copies/clock/ledger/registry/receipt/native/IO costs remain bounded inside phases/resources. No new route/helper/authority/active quota or reserve is granted. CE11/prelaunch does not depend on a future CE12 receipt; final E06/Q/root/admission/claim/events remain separate and unperformed.')],
        source_replay=dict(I231_candidate_and_preparation_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(),current_effect=rec['current_effect'],
        provenance=dict(preparer_and_reviewer='Same Codex assistant/chat as I231',methodological_only=True,actor_independent=False,competent_R02_attestation=False,competent_R03_resource_review=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts=False),
        next_step='Documentary W04 review complete. Positive progress stays stopped at SD01 pending genuine authority, accepted dependencies and actual caller/platform/capacity/service/clock/global mechanism evidence; no operational work or provider contact initiated.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I232-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/role/policy/phase comparisons only; no product/components imports/build/compile/tests/benchmarks, codec/crypto positives, sampling/probes/measurement of platform/clock/ledger/services, endpoints/processes/claim/replay/crash/restart/signing/keygen/enrollment/provisioning/contact.',
            over400_lines=True,reason='One W04 review with exact input pins, independent semantic comparisons, phase mapping, negative checks and preservation; overage declared. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_platform_selection_capacity_attestation_claim_or_execution_authority=True))


def main():
    rec = reconstruct()
    assert rd(RECON) == rec
    review = build_review(rec)
    assert rd(REVIEW) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published644'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 649
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i232-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published649'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == rec['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I232',historical_pins=957,preserved_published_files=649,new_files=5,
        criteria=18,findings=0,documentary_rejections=len(review['rejection_checks']),current_effect=rec['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
