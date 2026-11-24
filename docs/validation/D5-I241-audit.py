#!/usr/bin/env python3
"""I241 W09 negative E01-E05 integration dossier. Own documentary checks only."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'abe6ba72bfa694fe4a644594a818b90a8bc618cc'
DATE = '2026-11-24'
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
PRIOR_RECON = P+'D5-I240-I239-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I240-I239-documentary-review.json'
PRIOR_AUDIT = P+'D5-I240-audit.py'
PRIOR_SEAL = P+'D5-I240-integrity.json'
PRIOR_DOC = 'docs/design/D5-I240-I239-W08-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I223-W09-E01-E05-INTEGRATION-CANDIDATE.json'
PREP = P+'D5-I241-preparation-review.json'
AUDIT = P+'D5-I241-audit.py'
SEAL = P+'D5-I241-integrity.json'
DOC = 'docs/design/D5-I241-W09-E01-E05-INTEGRATION.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W09_INTEGRATION_EVIDENCE_MISSING_SD01_ACTIVE_NOT_ADMITTED'


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
    plan, ce07, people = rd(PLAN), rd(CE07), rd(W02)
    w = plan['work_packages'][8]
    pins = {**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 1002
    inventory = [PLAN,CONTRACT,CE01,CE07,CE07_REVIEW,W02,W03,W04,W05,W06,W07,W08,PACK,CUSTODY,PROFILE,PRIOR_REVIEW]
    assert all(p in pins and pins[p] == sha(p) for p in inventory)
    return dict(schema='d5.i241-w09-e01-e05-integration-candidate.v1',increment='I241',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        work_package='W09',planned_deliverable_id=w['deliverable_id'],
        kind='NEGATIVE_JOINT_RESOURCE_AND_PRIOR_PROOF_REQUIREMENT_DOSSIER_NOT_ACCEPTED_EVIDENCE_PACKAGE_NOT_POSITIVE_PROOF_RECORD',
        status='W09_DOCUMENTARY_PREPARED_E01_E05_BASIS_INDEX_AND_GENUINE_ACCEPTANCE_MISSING_SD01_ACTIVE_NOT_ADMITTED',
        input_pins=pins,work_package_binding=pin(PLAN,'/work_packages/8'),required_deliverables=w['deliverables'],
        required_exit_predicates=w['exit_predicates'],reject_if=w['reject_if'],needs_separate_future_authority_for=w['needs_separate_future_authority_for'],
        documentary_inventory=[pin(p) for p in sorted(inventory)],
        dependency_gate=dict(source=pin(PLAN,'/work_packages/8/depends_on'),required_package_ids=w['depends_on'],
            **{k+'_accepted':False for k in ['W01','W02','W03','W04','W05','W06','W07','W08']},SD01_stop_active=True,
            actual_entry_authority_or_accepted_effective_baseline=None,documentary_preparation_and_review_not_dependency_acceptance=True),
        role_scope_matrix=[r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R03','R06','R08']],
        role_and_identity_boundary=dict(source=pin(W02,'/identity_policy'),exact_identity_policy=people['identity_policy']['exact_policy'],
            required_provider_kind=w['provider_kind'],primary_roles=w['primary_review_roles'],separate_acceptor=w['separate_acceptor_role'],
            separation_matrix=people['separation_matrix'],overlap_policy=people['overlap_policy'],
            W02_intake_provisional_not_final_completeness_or_future_author_preapproval=True,
            all_actual_W05_W08_authors_providers_and_all_documentary_preparers_must_be_identified_enrolled_and_authenticated_before_acceptance=True,
            actor_strings_keys_git_or_assistant_labels_not_competence_appointment_or_independence=True,
            actual_complete_actor_author_provider_custody_inventory=None,actual_competence_appointment_independence_review=None,
            actual_R03_review=None,actual_R06_review=None,actual_separate_R08_decision=None,accepted=False),
        evidence_package_requirements=dict(source=pin(PLAN,'/evidence_package_contract'),exact_contract=plan['evidence_package_contract'],
            no_new_positive_record_schema_or_Runtime_Reader_member_defined=True,
            actual_complete_proof_body_inventory_locators_bytes_digests_authors_custody_availability=None,
            actual_scope_units_all_assumptions_provenance_validity_revocation_or_invalidation_join=None,
            document_hashes_templates_accepted_flags_or_typed_indices_not_real_proof=True,
            missing_body_actor_provider_or_assumption_blocks_acceptance=True),
        resource_obligation_ledger=[dict(id=r['id'],source=pin(PLAN,'/resource_obligation_matrix/'+str(i)),exact_plan_requirement=r,
            CE07_requirement=pin(CE07,'/E01_E05_join/'+str(i)),criterion_ids=[c['id'] for c in plan['resource_criterion_matrix'] if c['obligation']==r['id']],
            actual_complete_successor_scope_bound_body_derivation_and_assumptions=None,
            actual_platform_capacity_service_units_validity_and_custody=None,
            actual_primary_R03_R06_review=None,actual_separate_R08_acceptance=None,accepted=False,closed=False)
            for i,r in enumerate(plan['resource_obligation_matrix'])],
        criterion_revalidation_ledger=[dict(id=r['id'],obligation=r['obligation'],source=pin(PLAN,'/resource_criterion_matrix/'+str(i)),exact_plan_requirement=r,
            historical_I131_criterion=r['source'],CE07_requirement=pin(CE07,'/all20_criterion_join/'+str(i)),
            required_disposition='RECHECK_APPLICABILITY_AND_COMPLETE_EXACT_SUCCESSOR_EVIDENCE_NO_HISTORICAL_RESULT_TRANSFER',
            actual_applicability_assessment=None,actual_scope_body_bytes_hash_author_provider_custody=None,
            actual_derivation_units_assumptions_validity=None,actual_R03_R06_review=None,actual_R08_decision=None,
            accepted=False,closes_resource_obligation=False) for i,r in enumerate(plan['resource_criterion_matrix'])],
        contract_rule_requirements=[dict(id=r['id'],source=pin(CUSTODY,'/rules/'+str(i)),exact_rule=r)
            for i,r in enumerate(rd(CUSTODY)['rules']) if r['id'] in ce07['contract_rules']],
        profile_proof_requirements=[dict(id=r['id'],source=pin(PROFILE,'/semantic_contracts/'+str(i)),exact_rule=r)
            for i,r in enumerate(rd(PROFILE)['semantic_contracts']) if r['id'] in ['C02','C03','C04','C11']],
        prior_proof_boundary=dict(source=pin(CE07,'/accepted_prior_proof_join'),exact_negative_join=ce07['accepted_prior_proof_join'],
            W05_basis_index_requirements=pin(W05,'/basis_index_boundary'),
            required_proof_kind_ledger=[dict(kind=kind,source=pin(PROFILE,'/semantic_contracts/2'),required_reviewer_role='R03_RESOURCES' if kind.startswith('E0') else 'R06_ADMISSION_REVIEWER',
                actual_exact_source_runtime_resource_scope=None,actual_self_contained_derivation_body_hash_bytes_assumptions=None,
                actual_author_provider_custody_currentness=None,actual_review_record_id_and_genuine_accepted_review=None,accepted=False)
                for kind in ['E01','E02','E03','E04','E05','CP03','ATOMICITY']],
            basis_reviewer_role='R06_ADMISSION_REVIEWER',actual_BASIS_body_digest_bytes_or_review=None,
            actual_resource_index_body_digest_bytes_or_review=None,actual_source_registry_contract_index_basis_cross_binding=None,
            exact_source_image_runtime_policy_scope_and_current_antecedent_authentication_required=True,
            complete_self_contained_derivations_must_fit_reviewed_32768_limit_or_reject_and_review_graph_without_truncation=True,
            no_hidden_extra_files_future_proof_reads_or_cost_free_offline_evidence=True,
            seven_proof_requirements_not_seven_actual_records=True,
            CP03_historical_scope_and_written_atomicity_not_successor_acceptance=True,
            tests_flags_certificates_strings_or_placeholder_hashes_not_complete_proofs=True,
            antecedent_qualification_and_final_E06_separate_not_authorized=True,
            final_E06_payload_Q_root_claim_receipt_not_sole_antecedent_proof=True,
            actual_positive_BASIS_index_or_proof_record_created=False),
        resource_premise_handoff=dict(
            W03_exact_sources_image_runtime=pin(W03,'/actual_image_runtime_state'),W04_service=pin(W04,'/actual_service_state'),W04_capacity=pin(W04,'/actual_capacity_state'),
            W05_complete_scope=pin(W05,'/coverage_completeness'),W05_atomicity=pin(W05,'/atomicity_required_reasoning'),
            W06_heap_fit=pin(W06,'/availability_and_fit'),W06_requested_heap=pin(W06,'/requested_rollup'),W06_committed_heap=pin(W06,'/committed_rollup'),
            W07_complete_work=pin(W07,'/actual_whole_work_and_time'),W07_all30=pin(W07,'/all30_successor_correspondence'),
            W07_compatible_service_or_WCET=pin(W07,'/work_service_or_WCET_boundary'),W07_per_attempt_costs=pin(W07,'/per_attempt_cost_boundary'),
            W08_phase_bounds=pin(W08,'/phase_derivation_ledger'),W08_qualified_success=pin(W08,'/qualified_success_boundary'),W08_reserves=pin(W08,'/time_and_reserve_account'),
            same_effective_scope_memory_allocator_cache_load_clock_units_service_windows_and_validity_must_be_justified_and_reconciled=True,
            all11_heap_owners_lifetimes_allocator_complete_fit_and_separate_available_capacity_required=True,
            all30_work_group_correspondence_not_ten_activities_thirty_scalar_slots_or_twenty_vectors=True,
            all_original_native_children_threads_transitives_failure_paths_and_retained_traceback_scope_required=True,
            both_Readers_global_join_freshness_identity_crypto_ledger_frames_dual_outputs_and_cleanup_costs_required=True,
            no_CPU_sum_as_wall_unproved_overlap_subtraction_or_unknown_upper_as_zero=True,
            worker_pre_tR_work_exit_to_exact_True_tW_observation_and_successful_finally_to_tF_covered=True,
            complete_ordered_phase_bounds_and_nonvacuous_success_liveness_not_watchdog_elapsed_or_budget_sum=True,
            no_every_failure_cleanup_within900_claim_and_no_actual_infeasibility_conclusion=True,
            actual_joint_scope_assumptions_bound_compatibility_and_provenance_derivation=None,actual_complete_E01_E05_join_accepted=False),
        resource_and_reserve_boundary=dict(source=pin(PLAN,'/resource_and_scope_policy'),exact_plan_policy=plan['resource_and_scope_policy'],
            exact_candidate_reserve_rules=rd(CONTRACT)['reserve_accounting'],
            all_missing_heap_work_service_delay_phase_bounds_unknown_not_zero=True,
            budgets_not_capacity_service_or_success900_proof=True,
            no_partial_positive_or_documentary_PASS_as_joint_E01_E05_closure=True,
            actual_complete_heap_fit_capacity_work_service_phase_or900_proof=None,
            transfers_applied=0,resources_reserved=False,quotas_or_budgets_changed=False),
        phase_handoff=dict(source=pin(PLAN,'/scope_authentication_and_freeze_order'),exact_plan_order=plan['scope_authentication_and_freeze_order'],
            actual_baseline_actor_image_caller_platform_facts_previously_authenticated_before_resource_acceptance_required=True,
            actual_authors_providers_complete_bodies_and_assumptions_known_authenticated_before_W09_acceptance_required=True,
            W10_final_freeze_not_required_as_W09_sole_authentication_or_backward_dependency=True,
            W10_CE08_reconciles_same_facts_changed_inputs_invalidate_then_requalify_affected_packages=True,
            W11_C_W12_bundle_mapping_W13_gates_and_CE12_not_created_or_accepted_by_W09=True,
            no_future_CE10_approval_or_final_root_used_as_prior_authentication=True,
            W10_consumer=pin(PLAN,'/work_packages/9'),final_route_boundary=plan['prelaunch_handoff_and_CE12'],
            actual_final_actor_registry_C_bundle_root_claim_receipt_or_authority=None,actual_refresh_or_active_rebind=False),
        final_binding_boundary=dict(source=pin(CE07,'/I177_binding_reference'),exact_negative_binding_requirements=ce07['I177_binding_reference'],
            no_actual_B01_B04_artifact_or_body_produced=True,no_qualification_or_final_component_run_authorized=True),
        authority_boundary=dict(source=pin(PLAN,'/authorization_boundary'),inherited_boundary=plan['authorization_boundary'],
            allowed_now=['READ_DOCUMENTS_GIT_HASHES_AND_EXACT_PATH_PRESENCE','PREPARE_NEGATIVE_JOINT_INTEGRATION_DOSSIER','RUN_OWN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT'],
            no_product_components_import_compile_discovery_tests_runs_experimental_WCET_benchmarks_clock_CPU_IO_service_platform_sampling_or_probes=True,
            no_actual_crypto_codec_ledger_claim_provisioning_signing_keygen_enrollment_provider_contacts_or_new_helpers_channels_inputs_outputs=True,
            actual_external_authority_material_operational_verification_or_contact=None),
        exit_predicate_dispositions=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/8/exit_predicates/'+str(i)),predicate=t,
            documentary_requirements_prepared=True,actual_evidence=None,actual_primary_R03_R06_review=None,actual_separate_R08_acceptance=None,accepted=False)
            for i,t in enumerate(w['exit_predicates'])],
        preserved_scope_and_gates={k:plan[k] for k in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']},
        current_effect={**{k:v for k,v in rd(W08)['current_effect'].items() if k!='W08_documentary_prepared'},
            'W09_documentary_prepared':True,'W09_accepted':False,'actual_E01_E05_joint_BASIS_index_scope_and_atomicity_acceptance':False},
        producer=dict(identity='Same Codex assistant/chat as I239/I240',documentary_preparer_only=True,actor_independent=False,
            competent_R03_review=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_E01_E05_or_BASIS_index_acceptance_or_execution_authority=True))


NEGATIVE_CASES = [
    ('SD01_bypass',('dependency_gate','SD01_stop_active'),True,False),
    ('W09_acceptance',('current_effect','W09_accepted'),False,True),
    ('provisional_actor_freeze',('role_and_identity_boundary','W02_intake_provisional_not_final_completeness_or_future_author_preapproval'),True,False),
    ('missing_author_inventory',('role_and_identity_boundary','all_actual_W05_W08_authors_providers_and_all_documentary_preparers_must_be_identified_enrolled_and_authenticated_before_acceptance'),True,False),
    ('self_review_as_independence',('role_and_identity_boundary','actor_strings_keys_git_or_assistant_labels_not_competence_appointment_or_independence'),True,False),
    ('invented_R08_decision',('role_and_identity_boundary','actual_separate_R08_decision'),None,'UNVERIFIED_TEST_LABEL'),
    ('body_missing_bypass',('evidence_package_requirements','missing_body_actor_provider_or_assumption_blocks_acceptance'),True,False),
    ('template_as_proof',('evidence_package_requirements','document_hashes_templates_accepted_flags_or_typed_indices_not_real_proof'),True,False),
    ('obligation_accepted',('resource_obligation_ledger',0,'accepted'),False,True),
    ('obligation_closed',('resource_obligation_ledger',0,'closed'),False,True),
    ('criterion_accepted',('criterion_revalidation_ledger',0,'accepted'),False,True),
    ('criterion_as_closure',('criterion_revalidation_ledger',0,'closes_resource_obligation'),False,True),
    ('unknown_bound_zero',('resource_obligation_ledger',1,'actual_complete_successor_scope_bound_body_derivation_and_assumptions'),None,0),
    ('invented_proof_body',('prior_proof_boundary','required_proof_kind_ledger',0,'actual_self_contained_derivation_body_hash_bytes_assumptions'),None,'UNVERIFIED_TEST_LABEL'),
    ('proof_accepted',('prior_proof_boundary','required_proof_kind_ledger',0,'accepted'),False,True),
    ('proof_truncation',('prior_proof_boundary','complete_self_contained_derivations_must_fit_reviewed_32768_limit_or_reject_and_review_graph_without_truncation'),True,False),
    ('hidden_extra_reads',('prior_proof_boundary','no_hidden_extra_files_future_proof_reads_or_cost_free_offline_evidence'),True,False),
    ('legacy_CP03_transfer',('prior_proof_boundary','CP03_historical_scope_and_written_atomicity_not_successor_acceptance'),True,False),
    ('final_E06_as_prior_proof',('prior_proof_boundary','final_E06_payload_Q_root_claim_receipt_not_sole_antecedent_proof'),True,False),
    ('positive_index_record',('prior_proof_boundary','actual_positive_BASIS_index_or_proof_record_created'),False,True),
    ('unreconciled_premises',('resource_premise_handoff','same_effective_scope_memory_allocator_cache_load_clock_units_service_windows_and_validity_must_be_justified_and_reconciled'),True,False),
    ('heap_budget_as_fit',('resource_premise_handoff','all11_heap_owners_lifetimes_allocator_complete_fit_and_separate_available_capacity_required'),True,False),
    ('ten_as_all30',('resource_premise_handoff','all30_work_group_correspondence_not_ten_activities_thirty_scalar_slots_or_twenty_vectors'),True,False),
    ('omitted_failure_heap',('resource_premise_handoff','all_original_native_children_threads_transitives_failure_paths_and_retained_traceback_scope_required'),True,False),
    ('omitted_Reader_costs',('resource_premise_handoff','both_Readers_global_join_freshness_identity_crypto_ledger_frames_dual_outputs_and_cleanup_costs_required'),True,False),
    ('CPU_as_wall',('resource_premise_handoff','no_CPU_sum_as_wall_unproved_overlap_subtraction_or_unknown_upper_as_zero'),True,False),
    ('temporal_gap',('resource_premise_handoff','worker_pre_tR_work_exit_to_exact_True_tW_observation_and_successful_finally_to_tF_covered'),True,False),
    ('watchdog_as_success',('resource_premise_handoff','complete_ordered_phase_bounds_and_nonvacuous_success_liveness_not_watchdog_elapsed_or_budget_sum'),True,False),
    ('partial_positive_closure',('resource_and_reserve_boundary','no_partial_positive_or_documentary_PASS_as_joint_E01_E05_closure'),True,False),
    ('reserve_transfer',('resource_and_reserve_boundary','transfers_applied'),0,1),
    ('quota_change',('resource_and_reserve_boundary','quotas_or_budgets_changed'),False,True),
    ('late_baseline_authentication',('phase_handoff','actual_baseline_actor_image_caller_platform_facts_previously_authenticated_before_resource_acceptance_required'),True,False),
    ('late_proof_author_authentication',('phase_handoff','actual_authors_providers_complete_bodies_and_assumptions_known_authenticated_before_W09_acceptance_required'),True,False),
    ('backward_freeze_dependency',('phase_handoff','W10_final_freeze_not_required_as_W09_sole_authentication_or_backward_dependency'),True,False),
    ('future_bundle_as_authentication',('phase_handoff','no_future_CE10_approval_or_final_root_used_as_prior_authentication'),True,False),
    ('silent_proof_transfer',('phase_handoff','W10_CE08_reconciles_same_facts_changed_inputs_invalidate_then_requalify_affected_packages'),True,False),
    ('actual_rebind',('phase_handoff','actual_refresh_or_active_rebind'),False,True),
    ('final_artifact_created',('final_binding_boundary','no_actual_B01_B04_artifact_or_body_produced'),True,False),
    ('implicit_execution',('authority_boundary','no_product_components_import_compile_discovery_tests_runs_experimental_WCET_benchmarks_clock_CPU_IO_service_platform_sampling_or_probes'),True,False),
    ('exit_acceptance',('exit_predicate_dispositions',0,'accepted'),False,True),
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
    assert d['dependency_gate']['required_package_ids'] == ['W02','W03','W04','W05','W06','W07','W08']
    plan, ce07 = rd(PLAN), rd(CE07)
    obligations, criteria = d['resource_obligation_ledger'], d['criterion_revalidation_ledger']
    assert [r['id'] for r in obligations] == ['E01','E02','E03','E04','E05']
    assert len(criteria) == 20 and len({r['id'] for r in criteria}) == 20
    for i,row in enumerate(obligations):
        assert row['exact_plan_requirement'] == fragment(row['source']) == plan['resource_obligation_matrix'][i]
        assert fragment(row['CE07_requirement']) == ce07['E01_E05_join'][i]
        assert row['criterion_ids'] == [r['id'] for r in criteria if r['obligation']==row['id']]
        assert len(row['criterion_ids']) == 4 and row['closed'] is False
    for i,row in enumerate(criteria):
        assert row['exact_plan_requirement'] == fragment(row['source']) == plan['resource_criterion_matrix'][i]
        assert fragment(row['historical_I131_criterion']) == fragment(plan['resource_criterion_matrix'][i]['source'])
        assert fragment(row['CE07_requirement']) == ce07['all20_criterion_join'][i]
        assert row['closes_resource_obligation'] is False
    for row in obligations+criteria+d['prior_proof_boundary']['required_proof_kind_ledger']:
        assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    assert [r['id'] for r in d['contract_rule_requirements']] == ce07['contract_rules'] == ['K04','K05','K06','K08','K12','K15','K16']
    assert [r['id'] for r in d['profile_proof_requirements']] == ['C02','C03','C04','C11']
    for row in d['contract_rule_requirements']+d['profile_proof_requirements']:
        assert row['exact_rule'] == fragment(row['source'])
    proof = d['prior_proof_boundary']['required_proof_kind_ledger']
    assert [r['kind'] for r in proof] == ['E01','E02','E03','E04','E05','CP03','ATOMICITY']
    assert [r['required_reviewer_role'] for r in proof] == ['R03_RESOURCES']*5+['R06_ADMISSION_REVIEWER']*2
    assert d['prior_proof_boundary']['basis_reviewer_role'] == 'R06_ADMISSION_REVIEWER'
    assert len(d['role_and_identity_boundary']['separation_matrix']) == 14
    assert len(d['role_and_identity_boundary']['exact_identity_policy']['S01_exclusions']) == 8
    assert len(d['role_and_identity_boundary']['exact_identity_policy']['extra_custody_separation']) == 4
    assert d['role_and_identity_boundary']['overlap_policy']['no_blanket_R01_R02_separation_added'] is True
    assert [r['id'] for r in d['role_scope_matrix']] == ['R03','R06','R08']
    assert all(r['canonical_actor_id'] is None and r['accepted_appointment'] is False for r in d['role_scope_matrix'])
    for path in rd(PACK)['$defs']['source_bindings']['required']:
        assert not (ROOT/path).exists()
    for row in ce07['I177_binding_reference']:
        assert not (ROOT/row['path']).exists()
    for key,value in d['current_effect'].items():
        if key == 'W09_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False, key
    return dict(schema='d5.i241-preparation-review.v1',increment='I241',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,candidate=pin(SUBJECT),work_package=pin(PLAN,'/work_packages/8'),
        counts=dict(input_pins=1002,resource_obligations=5,criteria_to_revalidate=20,criteria_per_obligation=4,prior_proof_kind_requirements=7,
            custody_rules=7,profile_proof_rules=4,separation_requirements=14,S01_exclusions=8,extra_custody_separations=4,unassigned_review_roles=3,pending_exits=3),
        source_reconstruction=dict(I240_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        limitations=['W02-W08 remain unaccepted and SD01 active. This dossier is not the actual independent W09 decision, E01-E05 acceptance or an accepted proof record.',
            'Twenty historical criteria and five obligations require genuine complete same-scope successor evidence. BASIS/index bodies, seven self-contained proof derivations, authors/custody/currentness and actual R03/R06/R08 decisions remain missing.',
            'Baseline facts and actual authors/bodies must be authenticated before resource acceptance; W10 freeze and future CE10 approvals cannot supply sole prior authentication. No automatic proof transfer.',
            'Same-assistant preparation is not competent independent review or acceptance. No product/components, crypto/codec, runs/probes/benchmarks or clock/CPU/IO/service/platform sampling occur; no quotas/reserves/bindings change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I241-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/source-pointer/criterion/role/phase and in-memory document checks only. No target imports/compile/discovery/tests/runs, WCET experiments, clock/CPU/IO/service/platform/schedule sampling/probes, actual codec/crypto/ledger/claim, signing/keygen/enrollment/provisioning/services/contact.',
            over400_lines=True,reason='One W09 negative integration dossier with exact obligations/criteria/rules, proof requirements, pins, rejection checks and preservation. Overage declared; no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_E01_E05_or_BASIS_index_acceptance_or_execution_authority=True))


def main():
    review = build_review()
    assert rd(PREP) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published689'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 694
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i241-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published694'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == review['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I241',input_pins=1002,preserved_published_files=694,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],SD01_stop_active=True,
        prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
