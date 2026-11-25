#!/usr/bin/env python3
"""I248 W12 methodological review. Own documentary checks; no target execution."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '0030e67825766179278b1b5b43b5073262f591d8'
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
PRIOR_AUDIT = P+'D5-I247-audit.py'
PRIOR_PREP = P+'D5-I247-preparation-review.json'
PRIOR_SEAL = P+'D5-I247-integrity.json'
PRIOR_DOC = 'docs/design/D5-I247-W12-BUNDLE-APPROVALS-GLOBAL-MAPPING.md'
SUBJECT = P+'D5-I223-W12-BUNDLE-APPROVALS-GLOBAL-MAPPING-CANDIDATE.json'
PRIOR_FILES = {SUBJECT,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I248-I247-source-reconstruction.json'
REVIEW = P+'D5-I248-I247-documentary-review.json'
AUDIT = P+'D5-I248-audit.py'
SEAL = P+'D5-I248-integrity.json'
DOC = 'docs/design/D5-I248-I247-W12-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W12_REVIEW_BUNDLE_APPROVALS_GLOBAL_MAPPING_MISSING_NOT_ADMITTED'
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


def require_missing(row,false_fields=()):
    for key,value in row.items():
        if key.startswith('actual_'):
            assert value is False if key in false_fields else value is None,key
    if 'accepted' in row:
        assert row['accepted'] is False


def require_true(row,names):
    for key in names:
        assert row[key] is True,key


def inspect_size(model):
    # Read the published I192 bounds; do not encode any actual or synthetic body.
    reference=rd(SIZE)['serialized_bounds']
    upper,caps=reference['unrestricted_conservative_schema_upper_bytes'],rd(CUSTODY)['record_caps_bytes']
    terms={}
    for name in FAMILIES:
        terms[name]=upper[name] if upper[name]<=caps[name] else caps[name]
    raw_sum=sum(upper[name] for name in FAMILIES)
    overhead=upper['custody_bundle']-raw_sum
    bounded_sum=sum(terms.values())
    total=bounded_sum+overhead
    assert (raw_sum,overhead,bounded_sum,total)==(365064,3284,218360,221644)
    assert caps['custody_bundle']==reference['bundle_cap_bytes']==262144
    assert caps['custody_bundle']-total==reference['conditional_bundle_margin_bytes']==40500
    assert model['historical_reference']==reference==fragment(model['source'])
    assert model['effective_nested_model_terms_bytes']==terms
    assert model['nested_model_sum_bytes']==bounded_sum
    assert model['conditional_structure_and_approval_overhead_bytes']==overhead
    assert model['conditional_total_upper_bytes']==total
    assert model['candidate_bundle_cap_bytes']==caps['custody_bundle'] and model['conditional_arithmetic_margin_bytes']==40500
    assert model['exact_required_assumptions']==rd(CE10)['conditional_size_reference']['assumptions']
    require_true(model,['arithmetic_is_conditional_not_actual_encoding_fit_or_resource_proof',
        'all_nested_real_caps_and_ascii_safe_integer_escaping_assumptions_must_be_verified',
        'changed_encoding_requires_revised_bound_under_unchanged_limits_no_truncation',
        'unknown_body_or_proof_size_not_zero_margin_not_heap_CPU_reserve_or_service','unrestricted_schema_upper_not_actual_infeasibility'])
    require_missing(model,['actual_fit_verified'])
    return dict(effective_nested_model_terms_bytes=terms,nested_model_sum_bytes=bounded_sum,
        conditional_structure_and_approval_overhead_bytes=overhead,conditional_total_upper_bytes=total,
        candidate_bundle_cap_bytes=caps['custody_bundle'],conditional_arithmetic_margin_bytes=40500,
        actual_encoding_caps_fit_resources_or_infeasibility_proved=False)


def inspect(d):
    plan,ce10,custody,defs=rd(PLAN),rd(CE10),rd(CUSTODY),rd(PACK)['$defs']
    w=plan['work_packages'][11]
    assert d['work_package']=='W12' and d['planned_deliverable_id']==w['deliverable_id']
    assert fragment(d['work_package_binding'])==w
    for key,source in [('required_deliverables','deliverables'),('required_exit_predicates','exit_predicates'),('reject_if','reject_if'),('needs_separate_future_authority_for','needs_separate_future_authority_for')]:
        assert d[key]==w[source],key
    gate=d['dependency_gate']
    assert gate['required_package_ids']==fragment(gate['source'])==w['depends_on']==['W02','W04','W10','W11']
    assert gate['SD01_stop_active'] is True and gate['documentary_reviews_not_genuine_trust_acceptance_or_freeze'] is True
    assert all(gate['W%02d_accepted'%i] is False for i in range(1,12))
    require_missing(gate)
    assert d['role_scope_matrix']==[r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R01','R02','R06','R08']]
    trust=d['identity_and_trust_boundary']
    assert trust['exact_identity_policy']==rd(W02)['identity_policy']['exact_policy']
    assert trust['exact_separation_matrix']==rd(W02)['separation_matrix'] and len(trust['exact_separation_matrix'])==14
    assert trust['exact_overlap_policy']==rd(W02)['overlap_policy']
    assert fragment(trust['source'])==rd(W02)['identity_policy']
    assert fragment(trust['anchor_policy'])==rd(W02)['anchor_policy'] and fragment(trust['platform_policy'])==rd(W04)['platform_policy']
    assert trust['required_provider_kind']==w['provider_kind']
    assert trust['primary_review_roles']==w['primary_review_roles']==['R01','R02','R06']
    assert trust['separate_acceptor_role']==w['separate_acceptor_role']=='R08'
    require_true(trust,['preexisting_independently_accepted_anchors_registry_purpose_actor_key_epoch_currentness_and_revocation_evidence_required',
        'no_anchor_self_bootstrap_from_C_bundle_root_self_signed_registry_or_repository_key',
        'R08_human_and_key_distinct_from_both_R01_R02_all_S01_source_author_root_key_rules_preserved',
        'R01_R02_same_genuinely_qualified_human_key_only_under_role_purpose_bindings_and_distinct_domain_approvals',
        'selected_contract_schema_pins_must_match_external_authority_and_real_image_implemented_policies_not_bundle_self_selection'])
    require_missing(trust)
    assert [r['name'] for r in d['schema_requirement_ledger']]==['custody_bundle','custody_signed_core','custody_approval']
    for row in d['schema_requirement_ledger']:
        assert row['exact_schema']==fragment(row['source'])==defs[row['name']]
        assert row['exact_schema']['additionalProperties'] is False
    bundle,core,approval=defs['custody_bundle'],defs['custody_signed_core'],defs['custody_approval']
    assert bundle['required']==['schema','signed_core','approvals'] and len(core['required'])==8
    assert approval['required']==['actor_id','key_id','signature_hex']
    assert core['properties']['records']['required']==FAMILIES==core['properties']['record_hashes']['required']
    assert set(core['properties']['records']['properties'])==set(FAMILIES)==set(core['properties']['record_hashes']['properties'])
    assert core['properties']['records']['additionalProperties'] is False and core['properties']['record_hashes']['additionalProperties'] is False
    assert bundle['properties']['approvals']['required']==ROLES and bundle['properties']['approvals']['additionalProperties'] is False
    nested=d['nested_record_requirement_ledger']
    assert [r['family'] for r in nested]==FAMILIES
    assert [len(r['field_requirements']) for r in nested]==[8,26,13,14,27]
    for row in nested:
        assert row['exact_schema']==defs[row['family']]==fragment(row['source'])
        assert row['candidate_body_cap_bytes']==custody['record_caps_bytes'][row['family']]
        assert [s['field'] for s in row['field_requirements']]==defs[row['family']]['required']
        assert all(s['actual_value'] is None and s['status']=='MISSING_NOT_POSITIVE_RECORD' for s in row['field_requirements'])
        require_missing(row)
    complete=d['complete_core_and_bundle_requirement']
    assert complete['core_fields']==core['required'] and complete['bundle_fields']==bundle['required'] and complete['nested_families']==FAMILIES
    assert fragment(complete['selected_contract'])==custody and fragment(complete['selected_schema_pack'])==rd(PACK)
    require_true(complete,['all_five_record_hashes_equal_SHA256_JCS_complete_actual_nested_bodies_and_cross_records_must_agree',
        'same_complete_eight_field_core_for_all_roles_no_cut_fields_or_different_role_payloads',
        'excluded_signature_bundle_own_hash_Q_root_receipt_are_outside_core_not_permission_to_trim_core',
        'C_bound_indirectly_by_acceptance_trust_context_sha256_no_extra_C_body_or_bundle_hash_in_C',
        'acceptance_has_no_standalone_signature_bundle_has_no_own_validity_field',
        'custody_only_core_and_acceptance_decisions_not_runtime_resource_or_capture_admission'])
    require_missing(complete,['actual_bundle_accepted'])
    assert 'signature' not in defs['acceptance_record']['properties'] and 'validity' not in bundle['properties']
    approvals=d['approval_requirement_ledger']
    assert [r['role'] for r in approvals]==ROLES
    for row in approvals:
        assert fragment(row['source'])==approval
        assert row['required_domain_ASCII']==custody['custody_approval_domains'][row['role']]
        assert row['required_delimiter_hex']=='00' and type(row['required_delimiter_octets']) is int and row['required_delimiter_octets']==1
        assert row['required_payload']=='JCS(the same exact complete actual signed_core for all three roles)'
        assert row['verified'] is False
        require_missing(row)
    signature=d['signature_and_authentication_boundary']
    assert signature['exact_policy']==ce10['signature_policy']==fragment(signature['source'])
    assert signature['exact_domain_map']==custody['custody_approval_domains']
    assert signature['strict_crypto_profile']==ce10['signature_policy']['strict_profile_rules']
    require_true(signature,['three_genuine_approvals_required_same_core_exact_domain_plus_one_NUL',
        'two_existing_root_signatures_not_substitute_for_three_custody_approvals',
        'signatures_do_not_replace_full_provenance_evidence_resource_or_admission_decisions',
        'future_bundle_approvals_not_sole_prior_authentication_for_their_antecedents_or_W09_W10_W11'])
    assert signature['actual_signature_key_generation_crypto_codec_or_positive_schema_validation']=='NOT_RUN_NO_ACTUAL_BODIES'
    mapping=d['global_mapping_requirement']
    assert fragment(mapping['source'])==custody['rules'][8] and custody['rules'][8]['id']=='K09'
    assert fragment(mapping['historical_requirement'])==ce10['current_mapping_requirements']
    assert mapping['exact_key_fields']==ce10['current_mapping_requirements']['key_fields']==['configuration_epoch','SHA256(JCS(actual C))']
    assert mapping['required_unique_target_fields']==['bundle','caller','image','protection_domain','global_ledger_domain']
    require_true(mapping,['exactly_one_current_mapping_for_epoch_and_complete_C_digest_across_all_approved_callers_images_domains_and_restarts_required',
        'key_not_partitioned_or_extended_by_caller_image_domain_process_restart_or_local_registry',
        'one_observed_entry_or_local_signature_not_global_uniqueness_proof',
        'authenticated_resolution_before_P_ROOT_CHECK_then_freeze_same_C_Q_and_admitted_constructor_required',
        'conflicts_stale_epoch_rollback_unknown_revocation_or_uncertain_global_state_reject',
        'global_ledger_domain_matches_accepted_platform_one_use_domain'])
    require_missing(mapping,['actual_mapping_backend_endpoint_or_service_selected','actual_registry_or_mapping_configured','actual_mapping_accepted'])
    constructor=d['intrinsic_constructor_boundary']
    assert constructor['exact_rule']==fragment(constructor['source'])==custody['rules'][6] and custody['rules'][6]['id']=='K07'
    assert fragment(constructor['global_one_use_domain_rule'])==custody['rules'][13] and custody['rules'][13]['id']=='K14'
    assert fragment(constructor['platform_policy'])==rd(W04)['platform_policy']
    require_true(constructor,['accepted_immutable_first_entry_and_exact_image_runtime_constructor_custody_before_untrusted_repository_code_required',
        'worker_born_in_intrinsic_protected_domain_not_infer_mapping_from_bytes_or_new_I191_frame_receipt_or_channel',
        'no_extra_helper_process_pipe_fd_argv_env_trust_repository_key_schema_file_or_hidden_lookup_implicit',
        'incapable_backend_keeps_not_admitted_no_automatic_new_transport_attestation_or_contract_change',
        'global_mapping_not_actual_one_use_claim_and_durable_claim_domain_still_required'])
    require_missing(constructor,['actual_worker_or_claim_created'])
    assert set(d['inherited_bundle_policy_requirements'])==set(POLICIES)
    for key,row in d['inherited_bundle_policy_requirements'].items():
        assert row['exact_requirement']==ce10[key]==fragment(row['source'])
    selected=[r for r in custody['rules'] if r['id'] in ce10['contract_rules']]
    assert [r['id'] for r in d['contract_rule_requirements']]==ce10['contract_rules']==['K01','K03','K08','K09','K10','K11','K12','K13','K15','K16']
    assert [r['exact_rule'] for r in d['contract_rule_requirements']]==selected
    for row in d['contract_rule_requirements']:
        assert row['exact_rule']==fragment(row['source'])
    size=inspect_size(d['conditional_size_model'])
    facts=d['accepted_fact_and_validity_boundary']
    for key,path,field in [('W10_antecedents',W10,'freeze_record_ledger'),('W11_C_acceptance',W11,'schema_requirement_ledger'),
        ('W11_digest_and_signature_requirements',W11,'digest_and_signature_boundary'),('W11_deferred_PJ11_PJ12',W11,'projection_predicate_requirements')]:
        assert facts[key]['path']==path and fragment(facts[key])==rd(path)[field]
    require_true(facts,['all_real_nested_records_C_values_proof_bodies_and_prior_reviews_must_exist_and_same_scope_policies_authors_must_reconcile',
        'PJ11_three_approval_coverage_and_PJ12_effective_record_currentness_require_actual_W12_evidence_not_flags',
        'effective_bundle_validity_from_five_records_with_C_contained_not_new_bundle_interval_or_endpoint_equality',
        'same_epoch_strict_lifetime3600_conservative_clock_error5_trusted_now_known_revocation_and_no_conflicting_mapping_required',
        'host_client_date_or_stale_TOFU_cache_hidden_lookup_not_trusted_runtime_currentness'])
    require_missing(facts,['actual_fresh_snapshot_created'])
    resource=d['resource_and_invalidation_boundary']
    assert fragment(resource['source'])==plan['resource_and_scope_policy']
    assert resource['exact_candidate_reserve_rules']==rd(CONTRACT)['reserve_accounting']
    assert fragment(resource['W09_resource_join'])==rd(W09)['resource_premise_handoff']
    require_true(resource,['all_referenced_bodies_and_both_Readers_global_join_heap_work_CPU_IO_native_freshness_crypto_lookup_measurement_copies_registry_output_receipt_failure_cleanup_costs_required',
        'offline_enrollment_build_or_serialized_caps_not_free_work_capacity_service_phase_or_success900',
        'changed_mapping_lookup_constructor_operations_graph_authors_bodies_keys_epoch_policies_or_resource_assumptions_invalidate_dependents_and_requalify_join_before_progress',
        'no_automatic_hash_proof_approval_or_mapping_transfer_and_no_active_capture_inputs_rebind'])
    require_missing(resource,['actual_rebind_or_reconfiguration'])
    assert type(resource['reserve_transfers_applied']) is int and resource['reserve_transfers_applied']==0
    assert resource['resources_reserved'] is False and resource['quotas_or_budgets_changed'] is False
    phase=d['phase_handoff']
    assert fragment(phase['W13_consumer'])==plan['work_packages'][12]
    require_true(phase,['W12_requires_genuine_prior_W02_W04_W10_W11_not_future_root_E06_or_receipt',
        'mapping_follows_bundle_C_before_P_ROOT_CHECK_not_future_root_claim_or_receipt',
        'W13_gate_decision_and_CE11_handoff_then_separate_CE12_authorization_full_admission_claim_and_receipt_deferred',
        'CE11_does_not_depend_on_CE12_receipt'])
    assert phase['final_route_boundary']==plan['prelaunch_handoff_and_CE12']
    assert phase['actual_positive_bundle_approval_mapping_C_Q_root_request_claim_receipt_or_authority_created'] is False
    authority=d['authority_boundary']
    assert authority['inherited_boundary']==plan['authorization_boundary']==fragment(authority['source'])
    require_true(authority,['no_signing_key_generation_crypto_codec_or_positive_record_emission_build_import_compile_discovery_tests_product_or_components',
        'no_registry_mapping_backend_clock_ledger_key_identity_operator_service_selection_configuration_or_provider_contact',
        'no_claim_replay_crash_restart_endpoint_clock_CPU_IO_service_platform_process_benchmarks_or_probes',
        'no_new_helpers_channels_inputs_outputs_or_active_authority_destination_binding_or_quota_changes'])
    require_missing(authority)
    assert [r['predicate'] for r in d['exit_predicate_dispositions']]==w['exit_predicates']
    for row in d['exit_predicate_dispositions']:
        assert row['predicate']==fragment(row['source'])
        require_missing(row)
    assert d['preserved_scope_and_gates']=={k:plan[k] for k in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']}
    for key,value in d['current_effect'].items():
        if key=='W12_documentary_prepared':
            assert value is True
        elif key=='IR03':
            assert value=='NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value==0
        else:
            assert value is False,key
    check_pointers(d)
    return size


CRITERIA=[
    'Exact W12 deliverables, four dependencies, exits, rejections and operational restrictions match I223',
    'SD01 active and W01-W11 unaccepted; preparation/review does not supply genuine trust or freeze',
    'R01/R02/R06 reviews and separate R08 acceptance remain without appointed competent decisions',
    'Canonical identities,14 separation requirements and qualified R01/R02 overlap preserve W02',
    'Independent preexisting purpose-bound anchors/registry/policy selection cannot bootstrap from C/bundle/root',
    'Three exact closed schemas retain bundle3/core8/approval3 structure',
    'Five nested record bodies and five hashes retain exact schemas,88 missing field slots and separate caps',
    'Every role must cover the same complete eight-field core without field cropping',
    'Signature/bundle-own-hash/Q/root/receipt exclusions are external to core, not permission to trim it',
    'C is bound indirectly by acceptance digest; no extra C body, standalone acceptance signature or bundle validity',
    'Three R01/R02/R08 approvals retain exact role domains and one NUL before the same core',
    'Strict crypto profile is preserved as an unmet requirement; no keys/messages/signatures/verification issued',
    'Two root signatures and bare crypto success cannot substitute three custody approvals or provenance/resources',
    'Global mapping key is exactly epoch plus complete C digest, without caller/image/domain/restart partition',
    'One unique bundle/caller/image/protection/ledger target requires a global quantified proof, not a local entry',
    'Authenticated mapping resolution precedes P_ROOT_CHECK and freeze of same C/Q/admitted constructor',
    'Conflicts/stale epoch/rollback/uncertain revocation/global state reject and no backend/configuration selected',
    'K07 intrinsic protected first entry requires genuine origin evidence, not bytes or a new channel',
    'K14 global one-use claim domain remains separate from mapping and cannot be inferred from it',
    'Ten contract rules and seven CE10 policies retain exact primary text/pointers without stale history transfer',
    'Independent I192 arithmetic reconstructs218360+3284=221644 and margin40500 under nested caps',
    'ASCII/safe-integer/escaping/caps assumptions remain unverified; no actual encoding/fit proof',
    'Unrestricted368348 is not infeasibility and margin40500 is not resource reserve',
    'W10/W11 facts and PJ11/PJ12 evidence remain missing rather than supplied by future bundle signatures',
    'Effective validity comes from five current record intervals and C containment, not a new bundle interval',
    'Epoch/lifetime3600/error5/currentness/revocation require trusted evidence, not host date or hidden lookup',
    'Both Readers and complete evidence/provenance/freshness/crypto/native/output/failure costs remain in E01-E05',
    'Changed backend/lookup/constructor/graph/facts invalidate dependents and require reviewed resource join',
    'W13 gates, CE11 handoff and final authorization/root/claim/receipt remain separate without active rebind',
    'Three exits remain unaccepted, quotas/reserves unchanged and no positive bundle/mapping/D5 closure created']


def reconstruct():
    d=rd(SUBJECT)
    size=inspect(d)
    pins={**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==1037
    verify_blobs(pins)
    return dict(schema='d5.i248-source-reconstruction.v1',increment='I248',date=DATE,base_commit=BASE,subject=pin(SUBJECT),input_pins=pins,
        criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],
        counts=dict(input_pins=1037,schema_requirements=3,nested_records=5,nested_top_level_field_slots=88,core_fields=8,bundle_fields=3,
            role_approvals=3,approval_value_slots=9,inherited_policies=7,contract_rules=10,global_mapping_key_fields=2,
            unique_mapping_target_fields=5,unassigned_review_roles=4,pending_exits=3,review_criteria=len(CRITERIA)),
        independent_conditional_size_reconstruction=size,current_effect={**d['current_effect'],'W12_documentary_reviewed':True})


def own_rejections(d):
    cases=[
        ('core_field_omission',('complete_core_and_bundle_requirement','core_fields'),d['complete_core_and_bundle_requirement']['core_fields'][:-1]),
        ('extra_bundle_validity',('complete_core_and_bundle_requirement','bundle_fields'),d['complete_core_and_bundle_requirement']['bundle_fields']+['validity']),
        ('extra_C_schema_member',('schema_requirement_ledger',0,'exact_schema','properties','C'),{'type':'object'}),
        ('nested_family_substitution',('nested_record_requirement_ledger',0,'family'),'image_manifest'),
        ('nested_field_omission',('nested_record_requirement_ledger',0,'field_requirements'),d['nested_record_requirement_ledger'][0]['field_requirements'][:-1]),
        ('approval_role_duplicate',('approval_requirement_ledger',2,'role'),'R01_RUNTIME'),
        ('approval_domain_substitution',('approval_requirement_ledger',0,'required_domain_ASCII'),'D5/PGO181/CUSTODY/v1/R02'),
        ('double_NUL_hex',('approval_requirement_ledger',0,'required_delimiter_hex'),'0000'),
        ('different_role_payload',('approval_requirement_ledger',0,'required_payload'),'UNVERIFIED_PARTIAL_CORE_TEST_LABEL'),
        ('invented_message_bytes',('approval_requirement_ledger',0,'actual_message_bytes'),[]),
        ('crypto_algorithm_substitution',('signature_and_authentication_boundary','strict_crypto_profile','algorithm'),'Ed25519ph'),
        ('caller_extended_mapping_key',('global_mapping_requirement','exact_key_fields'),d['global_mapping_requirement']['exact_key_fields']+['caller']),
        ('ledger_target_omission',('global_mapping_requirement','required_unique_target_fields'),d['global_mapping_requirement']['required_unique_target_fields'][:-1]),
        ('invented_global_uniqueness_proof',('global_mapping_requirement','actual_global_quantified_uniqueness_authority_scope_currentness_conflict_and_rollback_proof'),'UNVERIFIED_TEST_LABEL'),
        ('new_mapping_schema_permission',('inherited_bundle_policy_requirements','current_mapping_requirements','exact_requirement','new_mapping_record_schema_or_registry_configuration_created'),True),
        ('constructor_rule_substitution',('intrinsic_constructor_boundary','exact_rule','rule'),'UNVERIFIED_TEST_RULE'),
        ('claim_rule_substitution',('intrinsic_constructor_boundary','global_one_use_domain_rule'),copy.deepcopy(d['global_mapping_requirement']['source'])),
        ('model_margin_change',('conditional_size_model','conditional_arithmetic_margin_bytes'),40501),
        ('model_assumption_omission',('conditional_size_model','exact_required_assumptions'),[]),
        ('model_nested_term_change',('conditional_size_model','effective_nested_model_terms_bytes','actor_registry'),98305),
        ('freshness_error_extension',('inherited_bundle_policy_requirements','freshness_policy','exact_requirement','max_clock_error_seconds'),6),
        ('anchor_self_bootstrap',('inherited_bundle_policy_requirements','anchor_and_policy_selection','exact_requirement','supplied_C_bundle_root_key_or_self_signed_registry_may_bootstrap'),True),
        ('wrong_W13_consumer',('phase_handoff','W13_consumer'),copy.deepcopy(d['accepted_fact_and_validity_boundary']['W10_antecedents'])),
        ('missing_resource_derivation_zero',('resource_and_invalidation_boundary','actual_complete_reference_inventory_and_resource_derivation_or_requalification'),0)]
    results=[]
    for name,path,value in cases:
        mutant=copy.deepcopy(d)
        node=mutant
        for key in path[:-1]:
            node=node[key]
        node[path[-1]]=value
        try:
            inspect(mutant)
        except AssertionError:
            results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return results


def build_review(rec):
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT))
    exists=Path.exists
    assert previous['build_candidate']()==rd(SUBJECT)
    prep=previous['build_review']()
    assert prep==rd(PRIOR_PREP) and Path.exists is exists
    additional=own_rejections(rd(SUBJECT))
    return dict(schema='d5.i248-documentary-review.v1',increment='I248',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,subject=pin(SUBJECT),reconstruction=pin(RECON),
        verdict='DOCUMENTARY_REQUIREMENTS_CONSISTENT_NO_NEW_DEFECT_FOUND_REAL_BUNDLE_APPROVALS_GLOBAL_MAPPING_MISSING_NOT_ADMITTED',findings=[],
        counts=rec['counts'],criteria=rec['criteria'],independent_conditional_size_reconstruction=rec['independent_conditional_size_reconstruction'],
        documentary_clarifications=[
            'Five nested bodies/88 slots, three approvals and the actual common core remain missing. Full closed core8/bundle3 are requirements, not accepted bodies or provenance.',
            'All roles require the same complete core under exact distinct role domains plus one NUL. Excluding signatures/hash-own/Q/root/receipt does not trim internal core fields; two root signatures do not replace three custody approvals.',
            'C remains bound indirectly by acceptance digest; no extra C body, standalone acceptance signature or independent bundle validity is introduced. Future approvals cannot supply sole prior authentication or independently selected anchors.',
            'Global mapping uniqueness is quantified across approved callers/images/domains/restarts for exactly(epoch,digest C), with one target bundle/caller/image/protection/ledger. No local entry proves it and no backend/configuration is selected.',
            'Authenticated resolution must precede P_ROOT_CHECK; protected constructor origin is intrinsic, not inferred from bytes/new frame. Mapping is not the actual global one-use claim and neither capability is proved here.',
            '221644/margin40500 are conditional I192 arithmetic requiring actual caps and encoding premises. No actual sizes, full evidence/resource fit, capacity/service/success900 or infeasibility is proved; costs/invalidations remain open.'],
        source_reconstruction=dict(primary_source_checks=True,I247_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        inherited_I247_rejection_checks=prep['rejection_checks'],additional_I248_rejection_checks=additional,current_effect=rec['current_effect'],
        provenance=dict(identity='Same Codex assistant/chat as I247',methodological_documentary_review_only=True,actor_independent=False,
            competent_R01_review=False,competent_R02_review=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['W02/W04/W10/W11 remain unaccepted. Actual records/approvals/keys/trust/global uniqueness/constructor/currentness/evidence and competent decisions remain missing; W12 exits unaccepted.',
            'SD01 active; zero accepted real packages, zero closed prelaunch gates and zero closed E01-E05 obligations. No actual resource/service/success900 or infeasibility proof.',
            'Same-assistant documentary checks do not satisfy competent independent reviews or R08 acceptance; publication grants no signing/crypto/configuration/product/component or quota authority.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I248-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/schema/domain/mapping-requirement/model-arithmetic checks and in-memory document mutations only. No target imports/compile/discovery/tests/runs/build, positive crypto/codec/signing/keygen/enrollment/provisioning, registry/mapping configuration, clock/CPU/IO/service/platform/ledger/claim/replay/process sampling/probes or contacts.',
            over400_lines=True,reason='One W12 review with primary-source reconstruction, pinned inputs, conditional arithmetic checks, rejection checks and integrity preservation. Overage declared; no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_bundle_approval_mapping_acceptance_resource_admission_or_execution_authority=True))


def main():
    rec=reconstruct()
    assert rec==rd(RECON)
    review=build_review(rec)
    assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL)
    preserved={**prior['preserved_published724'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==729
    seal=rd(SEAL)
    assert seal['schema']=='d5.i248-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published729']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I248',input_pins=1037,preserved_published_files=729,new_files=5,
        criteria=len(CRITERIA),inherited_documentary_rejections=len(review['inherited_I247_rejection_checks']),
        additional_documentary_rejections=len(review['additional_I248_rejection_checks']),findings=review['findings'],
        SD01_stop_active=True,prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
