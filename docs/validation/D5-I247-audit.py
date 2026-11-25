#!/usr/bin/env python3
"""I247 W12 negative bundle/approval/global mapping dossier. Own documentary checks only."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'e68ed6276e9ea1018a9942e4d3599550e859f9cc'
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
PRIOR_RECON = P+'D5-I246-I245-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I246-I245-documentary-review.json'
PRIOR_AUDIT = P+'D5-I246-audit.py'
PRIOR_SEAL = P+'D5-I246-integrity.json'
PRIOR_DOC = 'docs/design/D5-I246-I245-W11-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I223-W12-BUNDLE-APPROVALS-GLOBAL-MAPPING-CANDIDATE.json'
PREP = P+'D5-I247-preparation-review.json'
AUDIT = P+'D5-I247-audit.py'
SEAL = P+'D5-I247-integrity.json'
DOC = 'docs/design/D5-I247-W12-BUNDLE-APPROVALS-GLOBAL-MAPPING.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W12_BUNDLE_APPROVALS_GLOBAL_MAPPING_MISSING_NOT_ADMITTED'
FAMILIES = ['actor_registry','image_manifest','caller_identity','platform_custody','acceptance_record']
ROLES = ['R01_RUNTIME','R02_PLATFORM','R08_ACCEPTANCE']
POLICIES = ['anchor_and_policy_selection','signature_policy','current_mapping_requirements','conditional_size_reference','evidence_and_resource_boundary','freshness_policy','invalidation_policy']


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


def conditional_size_arithmetic():
    # Arithmetic on the published conditional model only; no body encoding occurs.
    reference=rd(SIZE)['serialized_bounds']
    upper=reference['unrestricted_conservative_schema_upper_bytes']
    caps=rd(CUSTODY)['record_caps_bytes']
    effective={name:min(upper[name],caps[name]) for name in FAMILIES}
    overhead=upper['custody_bundle']-sum(upper[name] for name in FAMILIES)
    total=sum(effective.values())+overhead
    assert overhead==3284 and sum(effective.values())==218360 and total==221644
    assert total==reference['conditional_bundle_upper_bytes'] and caps['custody_bundle']-total==40500
    return dict(source=pin(SIZE,'/serialized_bounds'),historical_reference=reference,
        effective_nested_model_terms_bytes=effective,nested_model_sum_bytes=sum(effective.values()),
        conditional_structure_and_approval_overhead_bytes=overhead,conditional_total_upper_bytes=total,
        candidate_bundle_cap_bytes=caps['custody_bundle'],conditional_arithmetic_margin_bytes=caps['custody_bundle']-total,
        exact_required_assumptions=rd(CE10)['conditional_size_reference']['assumptions'],
        arithmetic_is_conditional_not_actual_encoding_fit_or_resource_proof=True,
        all_nested_real_caps_and_ascii_safe_integer_escaping_assumptions_must_be_verified=True,
        changed_encoding_requires_revised_bound_under_unchanged_limits_no_truncation=True,
        unknown_body_or_proof_size_not_zero_margin_not_heap_CPU_reserve_or_service=True,
        unrestricted_schema_upper_not_actual_infeasibility=True,
        actual_encoding_assumptions_nested_caps_complete_bundle_bytes_or_fit=None,actual_fit_verified=False)


def build_candidate():
    plan,ce10,custody,defs=rd(PLAN),rd(CE10),rd(CUSTODY),rd(PACK)['$defs']
    w=plan['work_packages'][11]
    pins={**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==1032
    inventory=[PLAN,CONTRACT,CE01,CE10,CE10_REVIEW,SIZE,W02,W04,W09,W10,W11,PACK,CUSTODY,PROFILE,CPACK,PRIOR_REVIEW]
    assert all(p in pins and pins[p]==sha(p) for p in inventory)
    return dict(schema='d5.i247-w12-bundle-approvals-global-mapping-candidate.v1',increment='I247',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        work_package='W12',planned_deliverable_id=w['deliverable_id'],kind='NEGATIVE_BUNDLE_APPROVALS_AND_GLOBAL_MAPPING_REQUIREMENT_DOSSIER_NOT_REAL_BUNDLE_SIGNATURE_OR_MAPPING_NOT_ACCEPTED_EVIDENCE_PACKAGE',
        status='W12_DOCUMENTARY_PREPARED_REAL_BODIES_APPROVALS_TRUST_GLOBAL_UNIQUENESS_AND_ACCEPTANCE_MISSING_NOT_ADMITTED',
        input_pins=pins,work_package_binding=pin(PLAN,'/work_packages/11'),required_deliverables=w['deliverables'],required_exit_predicates=w['exit_predicates'],
        reject_if=w['reject_if'],needs_separate_future_authority_for=w['needs_separate_future_authority_for'],documentary_inventory=[pin(p) for p in sorted(inventory)],
        dependency_gate=dict(source=pin(PLAN,'/work_packages/11/depends_on'),required_package_ids=w['depends_on'],
            **{'W%02d_accepted'%i:False for i in range(1,12)},SD01_stop_active=True,actual_entry_authority_or_accepted_effective_baseline=None,
            actual_W02_anchors_W04_platform_W10_freeze_W11_C_and_acceptance=None,
            latest_W11_documentary_review=pin(PRIOR_REVIEW),documentary_reviews_not_genuine_trust_acceptance_or_freeze=True),
        role_scope_matrix=[r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R01','R02','R06','R08']],
        identity_and_trust_boundary=dict(source=pin(W02,'/identity_policy'),exact_identity_policy=rd(W02)['identity_policy']['exact_policy'],
            exact_separation_matrix=rd(W02)['separation_matrix'],exact_overlap_policy=rd(W02)['overlap_policy'],
            anchor_policy=pin(W02,'/anchor_policy'),platform_policy=pin(W04,'/platform_policy'),
            required_provider_kind=w['provider_kind'],primary_review_roles=w['primary_review_roles'],separate_acceptor_role=w['separate_acceptor_role'],
            preexisting_independently_accepted_anchors_registry_purpose_actor_key_epoch_currentness_and_revocation_evidence_required=True,
            no_anchor_self_bootstrap_from_C_bundle_root_self_signed_registry_or_repository_key=True,
            R08_human_and_key_distinct_from_both_R01_R02_all_S01_source_author_root_key_rules_preserved=True,
            R01_R02_same_genuinely_qualified_human_key_only_under_role_purpose_bindings_and_distinct_domain_approvals=True,
            selected_contract_schema_pins_must_match_external_authority_and_real_image_implemented_policies_not_bundle_self_selection=True,
            actual_canonical_actors_competence_appointments_keys_purpose_bindings_or_separation_proofs=None,
            actual_external_anchor_registry_epoch_digest_validity_and_revocation=None,
            actual_primary_reviews_or_separate_R08_acceptance=None,accepted=False),
        schema_requirement_ledger=[dict(name=name,source=pin(PACK,'/$defs/'+name),exact_schema=defs[name]) for name in ['custody_bundle','custody_signed_core','custody_approval']],
        nested_record_requirement_ledger=[dict(family=name,source=pin(PACK,'/$defs/'+name),exact_schema=defs[name],candidate_body_cap_bytes=custody['record_caps_bytes'][name],
            field_requirements=[dict(field=field,actual_value=None,status='MISSING_NOT_POSITIVE_RECORD') for field in defs[name]['required']],
            actual_complete_canonical_body=None,actual_body_sha256=None,actual_body_bytes=None,
            actual_provider_custody_referenced_evidence_closure_and_prior_authentication=None,
            actual_epoch_validity_scope_cross_hashes_and_competent_acceptance=None,accepted=False) for name in FAMILIES],
        complete_core_and_bundle_requirement=dict(core_fields=defs['custody_signed_core']['required'],bundle_fields=defs['custody_bundle']['required'],nested_families=FAMILIES,
            selected_contract=pin(CUSTODY),selected_schema_pack=pin(PACK),
            all_five_record_hashes_equal_SHA256_JCS_complete_actual_nested_bodies_and_cross_records_must_agree=True,
            same_complete_eight_field_core_for_all_roles_no_cut_fields_or_different_role_payloads=True,
            excluded_signature_bundle_own_hash_Q_root_receipt_are_outside_core_not_permission_to_trim_core=True,
            C_bound_indirectly_by_acceptance_trust_context_sha256_no_extra_C_body_or_bundle_hash_in_C=True,
            acceptance_has_no_standalone_signature_bundle_has_no_own_validity_field=True,
            custody_only_core_and_acceptance_decisions_not_runtime_resource_or_capture_admission=True,
            actual_complete_core_bytes_digest_bundle_body_hash_or_byte_size=None,actual_bundle_accepted=False),
        approval_requirement_ledger=[dict(role=role,source=pin(PACK,'/$defs/custody_approval'),
            required_domain_ASCII=custody['custody_approval_domains'][role],required_delimiter_hex='00',required_delimiter_octets=1,
            required_payload='JCS(the same exact complete actual signed_core for all three roles)',
            actual_canonical_actor_key_purpose_external_anchor_and_currentness=None,actual_common_core_bytes_and_digest=None,
            actual_message_bytes=None,actual_signature=None,actual_provenance_and_competent_verification_record=None,
            actual_independent_reviewer_or_R08_acceptance=None,verified=False,accepted=False) for role in ROLES],
        signature_and_authentication_boundary=dict(source=pin(CE10,'/signature_policy'),exact_policy=ce10['signature_policy'],
            exact_domain_map=custody['custody_approval_domains'],strict_crypto_profile=ce10['signature_policy']['strict_profile_rules'],
            three_genuine_approvals_required_same_core_exact_domain_plus_one_NUL=True,
            two_existing_root_signatures_not_substitute_for_three_custody_approvals=True,
            signatures_do_not_replace_full_provenance_evidence_resource_or_admission_decisions=True,
            future_bundle_approvals_not_sole_prior_authentication_for_their_antecedents_or_W09_W10_W11=True,
            actual_signature_key_generation_crypto_codec_or_positive_schema_validation='NOT_RUN_NO_ACTUAL_BODIES'),
        global_mapping_requirement=dict(source=pin(CUSTODY,'/rules/8'),historical_requirement=pin(CE10,'/current_mapping_requirements'),
            exact_key_fields=ce10['current_mapping_requirements']['key_fields'],required_unique_target_fields=ce10['current_mapping_requirements']['required_unique_target_fields'],
            exactly_one_current_mapping_for_epoch_and_complete_C_digest_across_all_approved_callers_images_domains_and_restarts_required=True,
            key_not_partitioned_or_extended_by_caller_image_domain_process_restart_or_local_registry=True,
            one_observed_entry_or_local_signature_not_global_uniqueness_proof=True,
            authenticated_resolution_before_P_ROOT_CHECK_then_freeze_same_C_Q_and_admitted_constructor_required=True,
            conflicts_stale_epoch_rollback_unknown_revocation_or_uncertain_global_state_reject=True,
            global_ledger_domain_matches_accepted_platform_one_use_domain=True,
            actual_key_epoch_and_C_digest=None,actual_unique_bundle_caller_image_protection_domain_and_ledger_target=None,
            actual_global_quantified_uniqueness_authority_scope_currentness_conflict_and_rollback_proof=None,
            actual_registry_provider_custody_and_competent_review=None,
            actual_mapping_backend_endpoint_or_service_selected=False,actual_registry_or_mapping_configured=False,actual_mapping_accepted=False),
        intrinsic_constructor_boundary=dict(source=pin(CUSTODY,'/rules/6'),exact_rule=custody['rules'][6],
            global_one_use_domain_rule=pin(CUSTODY,'/rules/13'),platform_policy=pin(W04,'/platform_policy'),
            accepted_immutable_first_entry_and_exact_image_runtime_constructor_custody_before_untrusted_repository_code_required=True,
            worker_born_in_intrinsic_protected_domain_not_infer_mapping_from_bytes_or_new_I191_frame_receipt_or_channel=True,
            no_extra_helper_process_pipe_fd_argv_env_trust_repository_key_schema_file_or_hidden_lookup_implicit=True,
            incapable_backend_keeps_not_admitted_no_automatic_new_transport_attestation_or_contract_change=True,
            global_mapping_not_actual_one_use_claim_and_durable_claim_domain_still_required=True,
            actual_backend_enforcement_origin_evidence_or_accepted_constructor=None,actual_worker_or_claim_created=False),
        inherited_bundle_policy_requirements={key:dict(source=pin(CE10,'/'+key),exact_requirement=ce10[key]) for key in POLICIES},
        contract_rule_requirements=[dict(id=r['id'],source=pin(CUSTODY,'/rules/'+str(i)),exact_rule=r) for i,r in enumerate(custody['rules']) if r['id'] in ce10['contract_rules']],
        conditional_size_model=conditional_size_arithmetic(),
        accepted_fact_and_validity_boundary=dict(W10_antecedents=pin(W10,'/freeze_record_ledger'),W11_C_acceptance=pin(W11,'/schema_requirement_ledger'),
            W11_digest_and_signature_requirements=pin(W11,'/digest_and_signature_boundary'),
            W11_deferred_PJ11_PJ12=pin(W11,'/projection_predicate_requirements'),
            all_real_nested_records_C_values_proof_bodies_and_prior_reviews_must_exist_and_same_scope_policies_authors_must_reconcile=True,
            PJ11_three_approval_coverage_and_PJ12_effective_record_currentness_require_actual_W12_evidence_not_flags=True,
            effective_bundle_validity_from_five_records_with_C_contained_not_new_bundle_interval_or_endpoint_equality=True,
            same_epoch_strict_lifetime3600_conservative_clock_error5_trusted_now_known_revocation_and_no_conflicting_mapping_required=True,
            host_client_date_or_stale_TOFU_cache_hidden_lookup_not_trusted_runtime_currentness=True,
            actual_complete_accepted_fact_join_or_validity_currentness_clock_revocation_proof=None,
            actual_fresh_snapshot_created=False),
        resource_and_invalidation_boundary=dict(source=pin(PLAN,'/resource_and_scope_policy'),exact_candidate_reserve_rules=rd(CONTRACT)['reserve_accounting'],
            W09_resource_join=pin(W09,'/resource_premise_handoff'),
            all_referenced_bodies_and_both_Readers_global_join_heap_work_CPU_IO_native_freshness_crypto_lookup_measurement_copies_registry_output_receipt_failure_cleanup_costs_required=True,
            offline_enrollment_build_or_serialized_caps_not_free_work_capacity_service_phase_or_success900=True,
            changed_mapping_lookup_constructor_operations_graph_authors_bodies_keys_epoch_policies_or_resource_assumptions_invalidate_dependents_and_requalify_join_before_progress=True,
            no_automatic_hash_proof_approval_or_mapping_transfer_and_no_active_capture_inputs_rebind=True,
            actual_complete_reference_inventory_and_resource_derivation_or_requalification=None,
            actual_rebind_or_reconfiguration=False,reserve_transfers_applied=0,resources_reserved=False,quotas_or_budgets_changed=False),
        phase_handoff=dict(W13_consumer=pin(PLAN,'/work_packages/12'),
            W12_requires_genuine_prior_W02_W04_W10_W11_not_future_root_E06_or_receipt=True,
            mapping_follows_bundle_C_before_P_ROOT_CHECK_not_future_root_claim_or_receipt=True,
            W13_gate_decision_and_CE11_handoff_then_separate_CE12_authorization_full_admission_claim_and_receipt_deferred=True,
            CE11_does_not_depend_on_CE12_receipt=True,final_route_boundary=plan['prelaunch_handoff_and_CE12'],
            actual_positive_bundle_approval_mapping_C_Q_root_request_claim_receipt_or_authority_created=False),
        authority_boundary=dict(source=pin(PLAN,'/authorization_boundary'),inherited_boundary=plan['authorization_boundary'],
            allowed_now=['READ_DOCUMENTS_GIT_HASHES_AND_EXACT_PATH_PRESENCE','PREPARE_NEGATIVE_BUNDLE_APPROVAL_GLOBAL_MAPPING_DOSSIER','RUN_OWN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT'],
            no_signing_key_generation_crypto_codec_or_positive_record_emission_build_import_compile_discovery_tests_product_or_components=True,
            no_registry_mapping_backend_clock_ledger_key_identity_operator_service_selection_configuration_or_provider_contact=True,
            no_claim_replay_crash_restart_endpoint_clock_CPU_IO_service_platform_process_benchmarks_or_probes=True,
            no_new_helpers_channels_inputs_outputs_or_active_authority_destination_binding_or_quota_changes=True,
            actual_external_authority_material_or_operational_action=None),
        exit_predicate_dispositions=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/11/exit_predicates/'+str(i)),predicate=t,
            documentary_requirements_prepared=True,actual_evidence=None,actual_primary_reviews=None,actual_separate_R08_acceptance=None,accepted=False) for i,t in enumerate(w['exit_predicates'])],
        preserved_scope_and_gates={k:plan[k] for k in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']},
        current_effect={**{k:v for k,v in rd(W11)['current_effect'].items() if k!='W11_documentary_prepared'},
            'W12_documentary_prepared':True,'W12_accepted':False,'actual_bundle_approvals_global_mapping_or_intrinsic_constructor_verified_or_created':False},
        producer=dict(identity='Same Codex assistant/chat as I245/I246',documentary_preparer_only=True,actor_independent=False,
            competent_R01_review=False,competent_R02_review=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_bundle_approval_mapping_acceptance_resource_admission_or_execution_authority=True))


NEGATIVE_CASES=[
    ('SD01_bypass',('dependency_gate','SD01_stop_active'),True,False),
    ('W12_acceptance',('current_effect','W12_accepted'),False,True),
    ('self_bootstrap_anchor',('identity_and_trust_boundary','no_anchor_self_bootstrap_from_C_bundle_root_self_signed_registry_or_repository_key'),True,False),
    ('missing_external_policy_selection',('identity_and_trust_boundary','selected_contract_schema_pins_must_match_external_authority_and_real_image_implemented_policies_not_bundle_self_selection'),True,False),
    ('R08_separation_waiver',('identity_and_trust_boundary','R08_human_and_key_distinct_from_both_R01_R02_all_S01_source_author_root_key_rules_preserved'),True,False),
    ('positive_nested_body',('nested_record_requirement_ledger',0,'actual_complete_canonical_body'),None,{}),
    ('unknown_nested_size_zero',('nested_record_requirement_ledger',0,'actual_body_bytes'),None,0),
    ('predicted_nested_hash',('nested_record_requirement_ledger',0,'actual_body_sha256'),None,'UNVERIFIED_TEST_LABEL'),
    ('unchecked_cross_hashes',('complete_core_and_bundle_requirement','all_five_record_hashes_equal_SHA256_JCS_complete_actual_nested_bodies_and_cross_records_must_agree'),True,False),
    ('cut_core_for_role',('complete_core_and_bundle_requirement','same_complete_eight_field_core_for_all_roles_no_cut_fields_or_different_role_payloads'),True,False),
    ('exclusions_trim_internal_core',('complete_core_and_bundle_requirement','excluded_signature_bundle_own_hash_Q_root_receipt_are_outside_core_not_permission_to_trim_core'),True,False),
    ('extra_C_body',('complete_core_and_bundle_requirement','C_bound_indirectly_by_acceptance_trust_context_sha256_no_extra_C_body_or_bundle_hash_in_C'),True,False),
    ('new_acceptance_signature_or_bundle_validity',('complete_core_and_bundle_requirement','acceptance_has_no_standalone_signature_bundle_has_no_own_validity_field'),True,False),
    ('bundle_accepted',('complete_core_and_bundle_requirement','actual_bundle_accepted'),False,True),
    ('wrong_delimiter',('approval_requirement_ledger',0,'required_delimiter_octets'),1,2),
    ('positive_signature',('approval_requirement_ledger',0,'actual_signature'),None,'UNVERIFIED_TEST_LABEL'),
    ('approval_verified',('approval_requirement_ledger',0,'verified'),False,True),
    ('two_root_signatures_as_three_approvals',('signature_and_authentication_boundary','two_existing_root_signatures_not_substitute_for_three_custody_approvals'),True,False),
    ('signatures_as_resources',('signature_and_authentication_boundary','signatures_do_not_replace_full_provenance_evidence_resource_or_admission_decisions'),True,False),
    ('future_bundle_as_prior_authentication',('signature_and_authentication_boundary','future_bundle_approvals_not_sole_prior_authentication_for_their_antecedents_or_W09_W10_W11'),True,False),
    ('local_uniqueness_as_global',('global_mapping_requirement','exactly_one_current_mapping_for_epoch_and_complete_C_digest_across_all_approved_callers_images_domains_and_restarts_required'),True,False),
    ('caller_partitioned_mapping_key',('global_mapping_requirement','key_not_partitioned_or_extended_by_caller_image_domain_process_restart_or_local_registry'),True,False),
    ('one_entry_as_proof',('global_mapping_requirement','one_observed_entry_or_local_signature_not_global_uniqueness_proof'),True,False),
    ('late_mapping_resolution',('global_mapping_requirement','authenticated_resolution_before_P_ROOT_CHECK_then_freeze_same_C_Q_and_admitted_constructor_required'),True,False),
    ('mapping_backend_selected',('global_mapping_requirement','actual_mapping_backend_endpoint_or_service_selected'),False,True),
    ('mapping_configured',('global_mapping_requirement','actual_registry_or_mapping_configured'),False,True),
    ('mapping_accepted',('global_mapping_requirement','actual_mapping_accepted'),False,True),
    ('worker_infers_custody',('intrinsic_constructor_boundary','worker_born_in_intrinsic_protected_domain_not_infer_mapping_from_bytes_or_new_I191_frame_receipt_or_channel'),True,False),
    ('implicit_helper_channel',('intrinsic_constructor_boundary','no_extra_helper_process_pipe_fd_argv_env_trust_repository_key_schema_file_or_hidden_lookup_implicit'),True,False),
    ('incapable_backend_accepted',('intrinsic_constructor_boundary','incapable_backend_keeps_not_admitted_no_automatic_new_transport_attestation_or_contract_change'),True,False),
    ('conditional_size_as_actual_fit',('conditional_size_model','arithmetic_is_conditional_not_actual_encoding_fit_or_resource_proof'),True,False),
    ('encoding_assumptions_waived',('conditional_size_model','all_nested_real_caps_and_ascii_safe_integer_escaping_assumptions_must_be_verified'),True,False),
    ('margin_as_resource_reserve',('conditional_size_model','unknown_body_or_proof_size_not_zero_margin_not_heap_CPU_reserve_or_service'),True,False),
    ('actual_size_fit',('conditional_size_model','actual_fit_verified'),False,True),
    ('new_bundle_validity',('accepted_fact_and_validity_boundary','effective_bundle_validity_from_five_records_with_C_contained_not_new_bundle_interval_or_endpoint_equality'),True,False),
    ('host_time_as_currentness',('accepted_fact_and_validity_boundary','host_client_date_or_stale_TOFU_cache_hidden_lookup_not_trusted_runtime_currentness'),True,False),
    ('unchecked_PJ11_PJ12',('accepted_fact_and_validity_boundary','PJ11_three_approval_coverage_and_PJ12_effective_record_currentness_require_actual_W12_evidence_not_flags'),True,False),
    ('free_offline_costs',('resource_and_invalidation_boundary','offline_enrollment_build_or_serialized_caps_not_free_work_capacity_service_phase_or_success900'),True,False),
    ('unreviewed_mapping_cost_change',('resource_and_invalidation_boundary','changed_mapping_lookup_constructor_operations_graph_authors_bodies_keys_epoch_policies_or_resource_assumptions_invalidate_dependents_and_requalify_join_before_progress'),True,False),
    ('reserve_transfer',('resource_and_invalidation_boundary','reserve_transfers_applied'),0,1),
    ('quota_change',('resource_and_invalidation_boundary','quotas_or_budgets_changed'),False,True),
    ('actual_rebind',('resource_and_invalidation_boundary','actual_rebind_or_reconfiguration'),False,True),
    ('future_root_as_mapping_antecedent',('phase_handoff','mapping_follows_bundle_C_before_P_ROOT_CHECK_not_future_root_claim_or_receipt'),True,False),
    ('implicit_crypto_execution',('authority_boundary','no_signing_key_generation_crypto_codec_or_positive_record_emission_build_import_compile_discovery_tests_product_or_components'),True,False),
    ('implicit_registry_configuration',('authority_boundary','no_registry_mapping_backend_clock_ledger_key_identity_operator_service_selection_configuration_or_provider_contact'),True,False),
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
    assert d['dependency_gate']['required_package_ids']==['W02','W04','W10','W11']
    defs=rd(PACK)['$defs']
    assert [r['name'] for r in d['schema_requirement_ledger']]==['custody_bundle','custody_signed_core','custody_approval']
    for row in d['schema_requirement_ledger']:
        assert row['exact_schema']==fragment(row['source']) and row['exact_schema']['additionalProperties'] is False
    assert defs['custody_bundle']['required']==['schema','signed_core','approvals'] and len(defs['custody_signed_core']['required'])==8
    assert [r['family'] for r in d['nested_record_requirement_ledger']]==FAMILIES
    assert [len(r['field_requirements']) for r in d['nested_record_requirement_ledger']]==[8,26,13,14,27]
    for row in d['nested_record_requirement_ledger']:
        assert row['exact_schema']==fragment(row['source'])==defs[row['family']]
        assert [r['field'] for r in row['field_requirements']]==row['exact_schema']['required']
        assert all(r['actual_value'] is None for r in row['field_requirements'])
        assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    approvals=d['approval_requirement_ledger']
    assert [r['role'] for r in approvals]==ROLES
    for row in approvals:
        assert fragment(row['source'])==defs['custody_approval']
        assert row['required_domain_ASCII']==rd(CUSTODY)['custody_approval_domains'][row['role']]
        assert row['required_delimiter_hex']=='00' and row['required_delimiter_octets']==1
        assert row['verified'] is False and row['accepted'] is False
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
    assert len(d['contract_rule_requirements'])==10
    for row in d['contract_rule_requirements']:
        assert row['exact_rule']==fragment(row['source'])
    for key,row in d['inherited_bundle_policy_requirements'].items():
        assert row['exact_requirement']==fragment(row['source'])==rd(CE10)[key]
    mapping=d['global_mapping_requirement']
    assert mapping['exact_key_fields']==['configuration_epoch','SHA256(JCS(actual C))']
    assert mapping['required_unique_target_fields']==['bundle','caller','image','protection_domain','global_ledger_domain']
    assert d['conditional_size_model']==conditional_size_arithmetic()
    assert [r['id'] for r in d['role_scope_matrix']]==['R01','R02','R06','R08']
    assert all(r['canonical_actor_id'] is None and r['accepted_appointment'] is False for r in d['role_scope_matrix'])
    for path in defs['source_bindings']['required']:
        assert not (ROOT/path).exists()
    for row in rd(CE07)['I177_binding_reference']:
        assert not (ROOT/row['path']).exists()
    for key,value in d['current_effect'].items():
        if key=='W12_documentary_prepared':
            assert value is True
        elif key=='IR03':
            assert value=='NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value==0
        else:
            assert value is False,key
    return dict(schema='d5.i247-preparation-review.v1',increment='I247',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,candidate=pin(SUBJECT),work_package=pin(PLAN,'/work_packages/11'),
        counts=dict(input_pins=1032,schema_requirements=3,nested_records=5,nested_top_level_field_slots=88,core_fields=8,bundle_fields=3,
            role_approvals=3,approval_value_slots=9,inherited_policies=7,contract_rules=10,global_mapping_key_fields=2,
            unique_mapping_target_fields=5,unassigned_review_roles=4,pending_exits=3),
        source_reconstruction=dict(I246_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        limitations=['W02/W04/W10/W11 remain unaccepted, SD01 active. No real bundle, approval/signature, independent trust or global mapping proof is supplied or accepted.',
            'Five bodies/88 fields, actual common core, actor/key/purpose/currentness/crypto/provenance records and unique global registry/backend/intrinsic constructor evidence remain missing.',
            '221644 and40500 are conditional I192-model arithmetic under real nested caps and encoding hypotheses; no actual body bytes, fit, resource/capacity/service/phase/success900 or infeasibility proof.',
            'Same-assistant preparation is not competent independent R01/R02/R06 review or R08 acceptance. No signing/crypto/codec/configuration/product/components/probes/contacts or quota/reserve/rebind changes.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I247-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/schema/domain/mapping-requirement/model-arithmetic checks and in-memory document mutations only. No target imports/compile/discovery/tests/runs/build, positive crypto/codec/signing/keygen/enrollment/provisioning, registry/mapping configuration, clock/CPU/IO/service/platform/ledger/claim/replay/process sampling/probes or contacts.',
            over400_lines=True,reason='One W12 negative bundle/approval/global mapping dossier with exact rules, schemas, conditional size model, pins, rejection checks and preservation. Overage declared; no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_bundle_approval_mapping_acceptance_resource_admission_or_execution_authority=True))


def main():
    review=build_review()
    assert rd(PREP)==review
    prior=rd(PRIOR_SEAL)
    preserved={**prior['preserved_published719'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==724
    seal=rd(SEAL)
    assert seal['schema']=='d5.i247-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published724']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==review['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I247',input_pins=1032,preserved_published_files=724,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],SD01_stop_active=True,
        prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
