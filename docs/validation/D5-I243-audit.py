#!/usr/bin/env python3
"""I243 W10 negative final antecedent freeze dossier. Own documentary checks only."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'e9a8c2e3f77b866e15c88bbf7aefae5239a199eb'
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
PRIOR_RECON = P+'D5-I242-I241-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I242-I241-documentary-review.json'
PRIOR_AUDIT = P+'D5-I242-audit.py'
PRIOR_SEAL = P+'D5-I242-integrity.json'
PRIOR_DOC = 'docs/design/D5-I242-I241-W09-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I223-W10-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json'
PREP = P+'D5-I243-preparation-review.json'
AUDIT = P+'D5-I243-audit.py'
SEAL = P+'D5-I243-integrity.json'
DOC = 'docs/design/D5-I243-W10-FINAL-ANTECEDENT-FREEZE.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W10_FINAL_ANTECEDENTS_MISSING_NOT_FROZEN_NOT_ADMITTED'
FAMILIES = ['actor_registry','image_manifest','caller_identity','platform_custody']
HELPERS = ['actor','preparation_record','anchor_key','image_member_binding','image_dependency','evidence_reference','source_bindings','validity']
POLICIES = ['typed_array_limits','source_runtime_policy','policy_constant_bindings','antecedent_and_hash_policy','freshness_policy','invalidation_policy']
RECONCILIATIONS = [
    ('AUTHORS_PREPARERS_ALIASES_KEYS',W02,'identity_policy'),
    ('SIX_SOURCES_IMAGE_RUNTIME_CLOSURE',W03,'actual_image_runtime_state'),
    ('CALLER_PRINCIPAL_CONSTRUCTOR_DOMAIN',W04,'caller_policy'),
    ('PLATFORM_SERVICE_CLOCK_LEDGER_SCOPE',W04,'platform_policy'),
    ('OPERAND_ATOMICITY_COMPLETE_SCOPE',W05,'coverage_completeness'),
    ('HEAP_LIFETIMES_FIT_CAPACITY',W06,'availability_and_fit'),
    ('WORK_CPU_UNITS_SERVICE_AND_COSTS',W07,'actual_whole_work_and_time'),
    ('PHASE_SUCCESS_AND_RESERVES',W08,'time_and_reserve_account'),
    ('BASIS_INDEX_E01_E05_PRIOR_PROOFS',W09,'prior_proof_boundary'),
    ('AUTHENTIC_BASELINE_BEFORE_W09',W09,'phase_handoff')]


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


def documentary_DAG():
    graph = rd(CUSTODY)['record_order']
    order = []
    pending = set(graph)
    while pending:
        ready = sorted(n for n in pending if all(parent in order for parent in graph[n]))
        assert ready, 'Cyclic documentary record dependency graph'
        order.extend(ready)
        pending.difference_update(ready)
    assert [n for n in order if n in [f.upper() for f in FAMILIES]] == [f.upper() for f in FAMILIES]
    descendants = {}
    for root in ['ANCHOR']+[f.upper() for f in FAMILIES]:
        affected = {root}
        while True:
            expanded = affected | {node for node,parents in graph.items() if set(parents)&affected}
            if expanded == affected:
                break
            affected = expanded
        descendants[root] = sorted(affected-{root})
    return dict(source=pin(CUSTODY,'/record_order'),exact_record_order=graph,topological_order=order,
        invalidation_descendants=descendants,documentary_acyclicity_verified=True,
        actual_records_authentic_current_accepted_or_frozen=False)


def build_candidate():
    plan, old, custody, schemas = rd(PLAN),rd(CE08),rd(CUSTODY),rd(PACK)['$defs']
    w = plan['work_packages'][9]
    pins = {**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 1012
    inventory = [PLAN,CONTRACT,CE01,CE08,CE08_REVIEW,W02,W03,W04,W05,W06,W07,W08,W09,PACK,CUSTODY,PROFILE,PRIOR_REVIEW]
    assert all(p in pins and pins[p] == sha(p) for p in inventory)
    return dict(schema='d5.i243-w10-final-antecedent-freeze-candidate.v1',increment='I243',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        work_package='W10',planned_deliverable_id=w['deliverable_id'],kind='NEGATIVE_FINAL_ANTECEDENT_FREEZE_REQUIREMENT_DOSSIER_NOT_FROZEN_RECORDS_NOT_ACCEPTED_REAL_EVIDENCE_PACKAGE',
        status='W10_DOCUMENTARY_PREPARED_REAL_BODIES_IDENTITIES_AUTHENTICATION_RECONCILIATION_AND_ACCEPTANCE_MISSING_NOT_FROZEN_NOT_ADMITTED',
        input_pins=pins,work_package_binding=pin(PLAN,'/work_packages/9'),required_deliverables=w['deliverables'],required_exit_predicates=w['exit_predicates'],
        reject_if=w['reject_if'],needs_separate_future_authority_for=w['needs_separate_future_authority_for'],documentary_inventory=[pin(p) for p in sorted(inventory)],
        dependency_gate=dict(source=pin(PLAN,'/work_packages/9/depends_on'),required_package_ids=w['depends_on'],
            **{k+'_accepted':False for k in ['W01','W02','W03','W04','W05','W06','W07','W08','W09']},SD01_stop_active=True,
            actual_entry_authority_or_accepted_effective_baseline=None,documentary_preparation_and_reviews_not_actual_dependency_acceptance=True),
        role_scope_matrix=[r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R01','R02','R03','R06','R08']],
        role_and_contributor_boundary=dict(source=pin(W02,'/identity_policy'),exact_identity_policy=rd(W02)['identity_policy']['exact_policy'],
            exact_separation_matrix=rd(W02)['separation_matrix'],exact_overlap_policy=rd(W02)['overlap_policy'],required_provider_kind=w['provider_kind'],
            primary_review_roles=w['primary_review_roles'],separate_acceptor_role=w['separate_acceptor_role'],
            historical_contributor_requirements=pin(CE08,'/contributor_closure'),
            required_subjects=old['contributor_closure']['required_subjects'],actual_W05_W09_authors_providers_and_all_documentary_preparers_must_be_known_authenticated_and_in_complete_final_registry=True,
            W02_CE03_remain_provisional_not_prior_final_completeness_or_future_author_approval=True,
            actor_registry_first_after_actual_authors_known_and_prior_identity_authority_verified=True,
            complete_sorted_unique_canonical_human_alias_role_preparer_key_scope_no_truncation_required=True,
            software_principal_not_alias_to_evade_human_exclusions=True,document_hashes_git_assistant_labels_not_authorship_or_independence=True,
            no_synthetic_person_preparation_record_or_forecast_hash=True,
            actual_complete_contributor_preparer_alias_author_provider_and_key_inventory=None,
            actual_identity_competence_enrollment_appointments_custody_and_exclusion_comparisons=None,
            actual_counts=None,actual_independent_primary_reviews=None,actual_separate_R08_acceptance=None,accepted=False),
        freeze_record_ledger=[dict(family=f,order=i+1,schema_source=pin(PACK,'/$defs/'+f),exact_schema=schemas[f],
            candidate_body_cap_bytes=custody['record_caps_bytes'][f],cap_applied_as_quota=False,
            field_requirements=[dict(field=field,actual_value=None,status='MISSING_NOT_POSITIVE_RECORD') for field in schemas[f]['required']],
            actual_record_id=None,actual_complete_canonical_body=None,actual_body_sha256=None,actual_body_bytes=None,
            actual_actor_author_provider_custody_and_availability=None,actual_configuration_epoch=None,actual_validity=None,
            actual_prior_authentication=None,actual_complete_referenced_evidence_closure=None,
            actual_primary_review=None,actual_separate_R08_acceptance=None,actual_frozen=False,accepted=False) for i,f in enumerate(FAMILIES)],
        nested_schema_obligations=[dict(name=name,source=pin(PACK,'/$defs/'+name),exact_schema=schemas[name]) for name in HELPERS],
        contract_rule_requirements=[dict(id=r['id'],source=pin(CUSTODY,'/rules/'+str(i)),exact_rule=r) for i,r in enumerate(custody['rules']) if r['id'] in old['contract_rules']],
        inherited_freeze_policy_requirements={key:dict(source=pin(CE08,'/'+key),exact_requirement=old[key]) for key in POLICIES},
        schema_and_body_boundary=dict(source=pin(PLAN,'/evidence_package_contract'),exact_package_contract=plan['evidence_package_contract'],
            top_level_slots_and_serialized_caps_not_nested_completeness_heap_CPU_or_full_evidence_proof=True,
            actual_counts_or_body_sizes_unknown_not_zero_and_caps_not_measured_fit=True,
            every_reference_body_complete_available_authentic_with_bytes_digest_author_provider_custody_units_assumptions_and_validity_required=True,
            positive_records_require_complete_values_not_null_or_placeholder=True,
            no_new_positive_schema_Reader_member_input_output_or_free_offline_proof=True,
            complete_preparers_1_to16_actors_keys_at_most64_dependencies_at_most128_without_trimming=True,
            actual_full_body_evidence_scope_closure_or_cap_fit_derivation=None,actual_positive_record_or_snapshot_created=False),
        record_DAG=documentary_DAG(),
        hash_scope_and_validity_boundary=dict(source=pin(CUSTODY,'/record_order'),
            actual_complete_canonical_bodies_before_SHA256_JCS_record_hashes_or_source_root=True,
            actor_then_image_then_caller_then_platform_and_authentic_antecedent_scope_required=True,
            final_image_digest_not_runtime_identity_and_no_image_self_manifest_bundle_digest=True,
            exact_six_source_mapping_and_complete_interpreter_loader_stdlib_frozen_native_crypto_closure_required=True,
            README_DOCUMENT_and_no_test_runner_loaded_by_membership=True,
            exact_selected_profile_schema_output_transport_grammar_and_custody_policies_must_be_implemented_not_just_named=True,
            record_hashes_epoch_validity_and_caller_registry_image_platform_domain_constructor_resource_cross_bindings_must_agree=True,
            same_epoch_current_overlapping_validity_strict_not_before_expires_lifetime3600_clock_error5_required=True,
            trusted_clock_known_revocation_every_boundary_not_host_date_stale_cache_TOFU_or_hidden_lookup=True,
            fresh_snapshots_only_when_real_evidence_ready_no_documentary_expiry_extension=True,
            actual_final_hash_cross_binding_epoch_currentness_or_policy_implementation_evidence=None,
            actual_clock_sample_or_fresh_snapshot_created=False),
        W09_reconciliation_ledger=[dict(id=name,source=pin(path,'/'+field),
            actual_authenticated_baseline_and_W09_fact=None,actual_proposed_final_freeze_fact=None,
            actual_exact_same_scope_fact_hash_author_assumption_and_validity_comparison=None,
            actual_affected_dependents_invalidation_requalification_and_review=None,
            accepted=False,same_facts_verified=False) for name,path,field in RECONCILIATIONS],
        reconciliation_and_invalidation_boundary=dict(source=pin(PLAN,'/scope_authentication_and_freeze_order'),exact_plan_order=plan['scope_authentication_and_freeze_order'],
            W09_requirement=pin(W09,'/phase_handoff'),latest_W09_documentary_review=pin(PRIOR_REVIEW),
            genuine_baseline_actor_image_caller_platform_authentication_and_real_authors_bodies_required_before_W09_not_created_retroactively_by_W10=True,
            W10_follows_W09_without_supplying_its_sole_authentication_or_backward_acceptance_dependency=True,
            same_effective_source_runtime_image_caller_domain_resources_actors_authors_policies_assumptions_and_hashes_must_reconcile=True,
            changed_author_alias_body_source_runtime_image_caller_domain_platform_resource_epoch_key_policy_or_schema_stops_progress_and_invalidates_dependents=True,
            anchor_or_key_change_revisits_anchor_policy_before_dependent_freeze=True,
            affected_W02_W09_and_later_records_requalified_and_competently_reviewed_before_progress_no_automatic_proof_or_hash_transfer=True,
            recomputation_or_documentary_refresh_not_active_capture_inputs_rebind=True,
            actual_same_facts_reconciliation_or_affected_package_requalification=None,actual_refresh_or_active_rebind=False),
        resource_and_cost_boundary=dict(source=pin(W09,'/resource_premise_handoff'),
            actual_prior_BASIS_index_E01_E05_acceptance_and_same_scope_complete_derivations_required=True,
            new_authorship_custody_proof_body_memory_registry_freshness_crypto_lookup_native_IO_and_output_work_not_free=True,
            both_Reader_ledgers_global_join_all_original_native_children_failure_cleanup_and_traceback_heap_scope_preserved=True,
            changed_costs_assumptions_or_graph_require_reviewed_full_heap_work_service_phase_and_Reader_bounds=True,
            source_policy=pin(PLAN,'/resource_and_scope_policy'),exact_candidate_reserve_rules=rd(CONTRACT)['reserve_accounting'],
            budgets_not_available_capacity_service_or_success900=True,actual_resource_or_full_Reader_fit_derivation=None,
            quotas_or_budgets_changed=False,reserve_transfers_applied=0,resources_reserved=False),
        phase_handoff=dict(W11_consumer=pin(PLAN,'/work_packages/10'),
            four_antecedent_records_only_W11_C_projection_and_acceptance_W12_bundle_mapping_W13_gates_deferred=True,
            future_C_acceptance_bundle_Q_root_claim_receipt_not_antecedent_of_current_freeze=True,
            CE11_handoff_does_not_depend_on_CE12_receipt=True,
            final_route_boundary=plan['prelaunch_handoff_and_CE12'],
            actual_C_acceptance_bundle_mapping_Q_root_claim_receipt_or_authority_created=False),
        authority_boundary=dict(source=pin(PLAN,'/authorization_boundary'),inherited_boundary=plan['authorization_boundary'],
            allowed_now=['READ_DOCUMENTS_GIT_HASHES_AND_EXACT_PATH_PRESENCE','PREPARE_NEGATIVE_FINAL_ANTECEDENT_FREEZE_DOSSIER','RUN_OWN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT'],
            no_product_components_import_compile_discovery_tests_runs_builds_crypto_codec_signing_keygen_enrollment_or_provisioning=True,
            no_clock_CPU_IO_schedule_service_platform_ledger_claim_replay_crash_restart_endpoint_process_sampling_benchmarks_or_probes=True,
            no_identity_key_policy_operator_service_selection_configuration_provider_contacts_or_new_helpers_channels_inputs_outputs=True,
            actual_external_authority_material_or_operational_action=None),
        exit_predicate_dispositions=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/9/exit_predicates/'+str(i)),predicate=t,
            documentary_requirements_prepared=True,actual_evidence=None,actual_primary_reviews=None,actual_separate_R08_acceptance=None,accepted=False) for i,t in enumerate(w['exit_predicates'])],
        preserved_scope_and_gates={k:plan[k] for k in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']},
        current_effect={**{k:v for k,v in rd(W09)['current_effect'].items() if k!='W09_documentary_prepared'},
            'W10_documentary_prepared':True,'W10_accepted':False,'actual_final_antecedents_created_authenticated_or_frozen':False},
        producer=dict(identity='Same Codex assistant/chat as I241/I242',documentary_preparer_only=True,actor_independent=False,
            competent_R01_review=False,competent_R02_review=False,competent_R03_review=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_actual_freeze_identity_attestation_acceptance_or_execution_authority=True))


NEGATIVE_CASES = [
    ('SD01_bypass',('dependency_gate','SD01_stop_active'),True,False),
    ('W10_acceptance',('current_effect','W10_accepted'),False,True),
    ('unknown_authors',('role_and_contributor_boundary','actual_W05_W09_authors_providers_and_all_documentary_preparers_must_be_known_authenticated_and_in_complete_final_registry'),True,False),
    ('premature_intake_completeness',('role_and_contributor_boundary','W02_CE03_remain_provisional_not_prior_final_completeness_or_future_author_approval'),True,False),
    ('truncated_arrays',('role_and_contributor_boundary','complete_sorted_unique_canonical_human_alias_role_preparer_key_scope_no_truncation_required'),True,False),
    ('software_as_human',('role_and_contributor_boundary','software_principal_not_alias_to_evade_human_exclusions'),True,False),
    ('synthetic_preparer',('role_and_contributor_boundary','no_synthetic_person_preparation_record_or_forecast_hash'),True,False),
    ('invented_record_hash',('freeze_record_ledger',0,'actual_body_sha256'),None,'UNVERIFIED_TEST_LABEL'),
    ('unknown_body_size_zero',('freeze_record_ledger',0,'actual_body_bytes'),None,0),
    ('slot_as_positive_record',('freeze_record_ledger',0,'field_requirements',0,'actual_value'),None,'UNVERIFIED_TEST_LABEL'),
    ('actual_freeze',('freeze_record_ledger',0,'actual_frozen'),False,True),
    ('record_accepted',('freeze_record_ledger',0,'accepted'),False,True),
    ('record_cap_as_quota',('freeze_record_ledger',0,'cap_applied_as_quota'),False,True),
    ('cap_as_completeness',('schema_and_body_boundary','top_level_slots_and_serialized_caps_not_nested_completeness_heap_CPU_or_full_evidence_proof'),True,False),
    ('unknown_count_as_zero',('schema_and_body_boundary','actual_counts_or_body_sizes_unknown_not_zero_and_caps_not_measured_fit'),True,False),
    ('unavailable_body',('schema_and_body_boundary','every_reference_body_complete_available_authentic_with_bytes_digest_author_provider_custody_units_assumptions_and_validity_required'),True,False),
    ('positive_snapshot',('schema_and_body_boundary','actual_positive_record_or_snapshot_created'),False,True),
    ('DAG_as_actual_acceptance',('record_DAG','actual_records_authentic_current_accepted_or_frozen'),False,True),
    ('predicted_hash',('hash_scope_and_validity_boundary','actual_complete_canonical_bodies_before_SHA256_JCS_record_hashes_or_source_root'),True,False),
    ('image_as_runtime',('hash_scope_and_validity_boundary','final_image_digest_not_runtime_identity_and_no_image_self_manifest_bundle_digest'),True,False),
    ('omitted_source_closure',('hash_scope_and_validity_boundary','exact_six_source_mapping_and_complete_interpreter_loader_stdlib_frozen_native_crypto_closure_required'),True,False),
    ('membership_as_loaded',('hash_scope_and_validity_boundary','README_DOCUMENT_and_no_test_runner_loaded_by_membership'),True,False),
    ('named_policy_as_implemented',('hash_scope_and_validity_boundary','exact_selected_profile_schema_output_transport_grammar_and_custody_policies_must_be_implemented_not_just_named'),True,False),
    ('cross_hash_mismatch_allowed',('hash_scope_and_validity_boundary','record_hashes_epoch_validity_and_caller_registry_image_platform_domain_constructor_resource_cross_bindings_must_agree'),True,False),
    ('host_date_as_runtime',('hash_scope_and_validity_boundary','trusted_clock_known_revocation_every_boundary_not_host_date_stale_cache_TOFU_or_hidden_lookup'),True,False),
    ('plan_extends_expiry',('hash_scope_and_validity_boundary','fresh_snapshots_only_when_real_evidence_ready_no_documentary_expiry_extension'),True,False),
    ('clock_snapshot_creation',('hash_scope_and_validity_boundary','actual_clock_sample_or_fresh_snapshot_created'),False,True),
    ('unchecked_reconciliation',('W09_reconciliation_ledger',0,'same_facts_verified'),False,True),
    ('retroactive_authentication',('reconciliation_and_invalidation_boundary','genuine_baseline_actor_image_caller_platform_authentication_and_real_authors_bodies_required_before_W09_not_created_retroactively_by_W10'),True,False),
    ('backward_acceptance_dependency',('reconciliation_and_invalidation_boundary','W10_follows_W09_without_supplying_its_sole_authentication_or_backward_acceptance_dependency'),True,False),
    ('silent_hash_transfer',('reconciliation_and_invalidation_boundary','affected_W02_W09_and_later_records_requalified_and_competently_reviewed_before_progress_no_automatic_proof_or_hash_transfer'),True,False),
    ('actual_rebind',('reconciliation_and_invalidation_boundary','actual_refresh_or_active_rebind'),False,True),
    ('free_new_costs',('resource_and_cost_boundary','new_authorship_custody_proof_body_memory_registry_freshness_crypto_lookup_native_IO_and_output_work_not_free'),True,False),
    ('Reader_heap_scope_omission',('resource_and_cost_boundary','both_Reader_ledgers_global_join_all_original_native_children_failure_cleanup_and_traceback_heap_scope_preserved'),True,False),
    ('reserve_transfer',('resource_and_cost_boundary','reserve_transfers_applied'),0,1),
    ('quota_change',('resource_and_cost_boundary','quotas_or_budgets_changed'),False,True),
    ('future_root_as_antecedent',('phase_handoff','future_C_acceptance_bundle_Q_root_claim_receipt_not_antecedent_of_current_freeze'),True,False),
    ('actual_C_or_claim',('phase_handoff','actual_C_acceptance_bundle_mapping_Q_root_claim_receipt_or_authority_created'),False,True),
    ('implicit_build_execution',('authority_boundary','no_product_components_import_compile_discovery_tests_runs_builds_crypto_codec_signing_keygen_enrollment_or_provisioning'),True,False),
    ('implicit_sampling',('authority_boundary','no_clock_CPU_IO_schedule_service_platform_ledger_claim_replay_crash_restart_endpoint_process_sampling_benchmarks_or_probes'),True,False),
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
    assert d['dependency_gate']['required_package_ids'] == ['W02','W03','W04','W05','W06','W07','W08','W09']
    assert [r['family'] for r in d['freeze_record_ledger']] == FAMILIES
    assert [r['candidate_body_cap_bytes'] for r in d['freeze_record_ledger']] == [98304,98304,8192,16384]
    assert [len(r['field_requirements']) for r in d['freeze_record_ledger']] == [8,26,13,14]
    for row in d['freeze_record_ledger']:
        assert row['exact_schema'] == fragment(row['schema_source']) == rd(PACK)['$defs'][row['family']]
        assert [r['field'] for r in row['field_requirements']] == row['exact_schema']['required']
        assert all(r['actual_value'] is None for r in row['field_requirements'])
        assert row['actual_frozen'] is False and row['accepted'] is False
        assert all(v is None for k,v in row.items() if k.startswith('actual_') and k!='actual_frozen')
    assert [r['name'] for r in d['nested_schema_obligations']] == HELPERS
    for row in d['nested_schema_obligations']:
        assert row['exact_schema'] == fragment(row['source'])
    assert len(d['contract_rule_requirements']) == 10
    for row in d['contract_rule_requirements']:
        assert row['exact_rule'] == fragment(row['source'])
    for key,row in d['inherited_freeze_policy_requirements'].items():
        assert row['exact_requirement'] == fragment(row['source']) == rd(CE08)[key]
    assert len(d['W09_reconciliation_ledger']) == 10
    for row in d['W09_reconciliation_ledger']:
        assert row['accepted'] is False and row['same_facts_verified'] is False
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
    assert [r['id'] for r in d['role_scope_matrix']] == ['R01','R02','R03','R06','R08']
    assert all(r['canonical_actor_id'] is None and r['accepted_appointment'] is False for r in d['role_scope_matrix'])
    assert len(d['role_and_contributor_boundary']['exact_separation_matrix']) == 14
    for path in rd(PACK)['$defs']['source_bindings']['required']:
        assert not (ROOT/path).exists()
    for row in rd(CE07)['I177_binding_reference']:
        assert not (ROOT/row['path']).exists()
    for key,value in d['current_effect'].items():
        if key == 'W10_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False, key
    return dict(schema='d5.i243-preparation-review.v1',increment='I243',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,candidate=pin(SUBJECT),work_package=pin(PLAN,'/work_packages/9'),
        counts=dict(input_pins=1012,antecedent_record_requirements=4,required_top_level_field_slots=61,nested_schema_requirements=8,
            contract_rules=10,inherited_freeze_policies=6,W09_reconciliation_requirements=10,separation_requirements=14,
            unassigned_review_roles=5,pending_exits=3),
        source_reconstruction=dict(I242_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        limitations=['W02-W09 remain unaccepted; SD01 active. W10 is a negative documentary specification, not actual final records, immutable snapshots, authentic identities or accepted freeze.',
            'All four bodies,61 fields, nested evidence closures, real authors, bytes/hashes/caps/epoch/validity/custody/reviews and10 reconciliations remain missing. Serialized caps and documentary DAG prove no resource or currentness guarantee.',
            'W10 may not retroactively authenticate W09 or transfer proofs after changed facts. Later C/bundle/mapping/gates/E06/root/claim/receipt remain separate; no refresh or active rebind applied.',
            'Same-assistant preparation is not competent R01/R02/R03/R06 review or separate R08 acceptance. No build/enrollment/signing/product/components/crypto/codec/probes or measurements; no quotas/reserves/bindings change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I243-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/schema/field/DAG/role/scope checks and in-memory document mutations only. No target import/compile/discovery/tests/runs/build, positive crypto/codec, signing/keygen/enrollment/provisioning, clock/CPU/IO/service/platform/ledger/claim/replay/process sampling/probes or contacts.',
            over400_lines=True,reason='One W10 negative freeze dossier with exact record/schema/policy requirements, reconciliation, pins, rejection checks and preservation. Overage declared; no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_actual_freeze_identity_attestation_acceptance_or_execution_authority=True))


def main():
    review = build_review()
    assert rd(PREP) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published699'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 704
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i243-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published704'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == review['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I243',input_pins=1012,preserved_published_files=704,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],SD01_stop_active=True,
        prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
