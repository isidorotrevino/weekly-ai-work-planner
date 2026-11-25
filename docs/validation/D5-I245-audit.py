#!/usr/bin/env python3
"""I245 W11 negative exact C/acceptance dossier. Own documentary checks only."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'cb96bff2667d476f19b1ddf8c2b24883b12cadbf'
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
PRIOR_RECON = P+'D5-I244-I243-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I244-I243-documentary-review.json'
PRIOR_AUDIT = P+'D5-I244-audit.py'
PRIOR_SEAL = P+'D5-I244-integrity.json'
PRIOR_DOC = 'docs/design/D5-I244-I243-W10-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I223-W11-EXACT-C-ACCEPTANCE-CANDIDATE.json'
PREP = P+'D5-I245-preparation-review.json'
AUDIT = P+'D5-I245-audit.py'
SEAL = P+'D5-I245-integrity.json'
DOC = 'docs/design/D5-I245-W11-EXACT-C-ACCEPTANCE.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W11_C_ACCEPTANCE_AND_ACCEPTED_FACTS_MISSING_NOT_ADMITTED'
EVIDENCE_FIELDS = ['prior_basis_acceptance_evidence','prior_resource_acceptance_evidence','R01_runtime_acceptance_evidence','R02_platform_acceptance_evidence','R08_separate_acceptance_evidence']
ANTECEDENTS = [('actor_registry_sha256','actor_registry'),('image_manifest_sha256','image_manifest'),('caller_record_sha256','caller_identity'),('platform_record_sha256','platform_custody')]


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


def local_refs(value):
    result = set()
    if isinstance(value,dict):
        if '$ref' in value:
            ref = value['$ref']
            assert ref.startswith('#/$defs/')
            result.add(ref.rsplit('/',1)[1])
        for child in value.values():
            result.update(local_refs(child))
    elif isinstance(value,list):
        for child in value:
            result.update(local_refs(child))
    return result


def shared_contract():
    cdefs,adefs = rd(CPACK)['$defs'],rd(PACK)['$defs']
    c,a = cdefs['trust_context']['properties'],adefs['acceptance_record']['properties']
    common = sorted(set(c)&set(a))
    fields = [k for k in common if c[k]==a[k]]
    assert len(common)==15 and len(fields)==14 and set(common)-set(fields)=={'schema'}
    names = set()
    frontier = set().union(*(local_refs(c[k]) for k in fields))
    while frontier:
        name = sorted(frontier)[0]
        frontier.remove(name)
        if name in names:
            continue
        assert cdefs[name] == adefs[name]
        names.add(name)
        frontier.update(local_refs(cdefs[name])-names)
    assert names == {'identity','proposal_scope','sha256','trusted_key','validity','verifier_profile'}
    return fields,sorted(names)


def build_candidate():
    plan, ce09, cdefs, adefs = rd(PLAN),rd(CE09),rd(CPACK)['$defs'],rd(PACK)['$defs']
    w = plan['work_packages'][10]
    fields,closure = shared_contract()
    pins = {**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==1022
    inventory = [PLAN,CONTRACT,CE01,CE09,CE09_REVIEW,W02,W03,W04,W05,W06,W07,W08,W09,W10,PACK,CUSTODY,PROFILE,CPACK,PRIOR_REVIEW]
    assert all(p in pins and pins[p]==sha(p) for p in inventory)
    return dict(schema='d5.i245-w11-exact-C-acceptance-candidate.v1',increment='I245',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        work_package='W11',planned_deliverable_id=w['deliverable_id'],kind='NEGATIVE_EXACT_C_AND_CUSTODY_ACCEPTANCE_REQUIREMENT_DOSSIER_NOT_POSITIVE_C_OR_ACCEPTANCE_NOT_ACCEPTED_REAL_EVIDENCE_PACKAGE',
        status='W11_DOCUMENTARY_PREPARED_ACCEPTED_FACTS_EXACT_VALUES_BODIES_DIGESTS_VALIDITY_AND_DECISIONS_MISSING_NOT_ADMITTED',
        input_pins=pins,work_package_binding=pin(PLAN,'/work_packages/10'),required_deliverables=w['deliverables'],required_exit_predicates=w['exit_predicates'],
        reject_if=w['reject_if'],needs_separate_future_authority_for=w['needs_separate_future_authority_for'],documentary_inventory=[pin(p) for p in sorted(inventory)],
        dependency_gate=dict(source=pin(PLAN,'/work_packages/10/depends_on'),required_package_ids=w['depends_on'],
            **{'W%02d_accepted'%i:False for i in range(1,11)},SD01_stop_active=True,actual_entry_authority_or_accepted_effective_baseline=None,
            actual_W09_resources_prior_proofs_or_W10_frozen_antecedents=None,
            latest_W10_documentary_review=pin(PRIOR_REVIEW),documentary_reviews_not_genuine_acceptance_or_freeze=True),
        role_scope_matrix=[r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R01','R02','R03','R06','R08']],
        identity_and_decision_boundary=dict(source=pin(W02,'/identity_policy'),exact_identity_policy=rd(W02)['identity_policy']['exact_policy'],
            exact_separation_matrix=rd(W02)['separation_matrix'],exact_overlap_policy=rd(W02)['overlap_policy'],required_provider_kind=w['provider_kind'],
            primary_review_roles=w['primary_review_roles'],separate_acceptor_role=w['separate_acceptor_role'],
            all_roles_preparers_authors_requester_issuer_acceptor_and_keys_from_genuine_canonical_registry_competence_appointments_and_prior_acceptance=True,
            complete_preparer_records_actor_record_ids_and_SHA256_JCS_contribution_evidence_must_match_without_truncation=True,
            software_principal_not_alternate_human_and_no_git_assistant_or_role_string_as_independence=True,
            actual_accepted_identity_role_preparer_author_requester_key_inventory=None,actual_primary_reviews=None,actual_separate_R08_acceptance=None,accepted=False),
        schema_requirement_ledger=[dict(kind=kind,source=pin(path,'/$defs/'+definition),exact_schema=defs[definition],
            candidate_body_cap_bytes=cap,cap_applied_as_quota=False,
            field_requirements=[dict(field=f,actual_value=None,status='MISSING_NOT_POSITIVE_BODY') for f in defs[definition]['required']],
            actual_complete_body=None,actual_canonical_bytes=None,actual_body_sha256=None,actual_body_bytes=None,
            actual_authentic_scope_provider_custody_and_review=None,accepted=False)
            for kind,path,definition,defs,cap in [('C',CPACK,'trust_context',cdefs,8192),('ACCEPTANCE',PACK,'acceptance_record',adefs,rd(CUSTODY)['record_caps_bytes']['acceptance_record'])]],
        shared_type_requirement_ledger=[dict(field=f,C_source=pin(CPACK,'/$defs/trust_context/properties/'+f),acceptance_source=pin(PACK,'/$defs/acceptance_record/properties/'+f),
            exact_shared_schema=cdefs['trust_context']['properties'][f],type_identity_documentarily_verified=True,
            actual_C_value=None,actual_acceptance_value=None,actual_accepted_value_provenance=None,actual_value_projection_verified=False) for f in fields],
        shared_definition_closure=[dict(name=name,C_source=pin(CPACK,'/$defs/'+name),acceptance_source=pin(PACK,'/$defs/'+name),exact_shared_schema=cdefs[name]) for name in closure],
        value_projection_requirement_ledger=[dict(field=f,source=pin(CE09,'/shared_type_projection/'+str(next(i for i,r in enumerate(ce09['shared_type_projection']) if r['field']==f))),
            required_relation='EXACT_ACCEPTED_VALUE_EQUALITY',actual_accepted_source_fact=None,actual_C_value=None,actual_acceptance_value=None,verified=False) for f in fields if f!='validity'],
        validity_containment_requirement=dict(source=pin(CE09,'/time_and_currentness_policy'),
            type_shared_but_value_relation_is_containment_not_forced_interval_equality=True,
            C_validity_must_be_contained_in_each_current_relevant_antecedent_and_acceptance_interval=True,
            strict_not_before_lt_expires_at_lifetime_at_most3600_and_same_current_epoch=True,
            platform_clock_error_lte_C_clock_error_lte5_and_trusted_now_error_both_sides_required=True,
            actual_C_interval=None,actual_antecedent_acceptance_intervals=None,actual_platform_error_C_error_and_trusted_now=None,
            actual_containment_currentness_revocation_or_review=None,verified=False),
        exact_constant_requirements=dict(C_constants={k:v['const'] for k,v in cdefs['trust_context']['properties'].items() if 'const' in v},
            acceptance_decision_constant=adefs['acceptance_record']['properties']['decision']['const'],
            known_schema_constants_are_requirements_not_evidence_of_real_values=True,
            C_closed_unchanged_no_bundle_hash_new_field_or_root_backpin=True,acceptance_custody_only_not_resource_or_capture_admission=True,
            actual_constants_in_genuine_C_and_acceptance_verified=False),
        antecedent_hash_requirement_ledger=[dict(acceptance_field=field,family=family,source=pin(W10,'/freeze_record_ledger/'+str(i)),
            actual_accepted_canonical_body=None,actual_complete_body_hash=None,actual_matching_acceptance_hash=None,verified=False) for i,(field,family) in enumerate(ANTECEDENTS)],
        prior_acceptance_evidence_requirement_ledger=[dict(field=f,source=pin(PACK,'/$defs/acceptance_record/properties/'+f),
            actual_complete_proof_body_record_id_bytes_digest_author_provider_custody_and_availability=None,
            actual_scope_units_assumptions_validity_and_genuine_accepted_review=None,accepted=False) for f in EVIDENCE_FIELDS],
        projection_predicate_requirements=[dict(id=r['id'],source=pin(CE09,'/projection_predicates/'+str(i)),exact_historical_requirement=r,
            required_consumer_work_package='W11' if r['consumer_step']=='CE09' else 'W12',
            actual_same_scope_body_proof_provider_custody_review_or_acceptance=None,verified=False) for i,r in enumerate(ce09['projection_predicates'])],
        contract_rule_requirements=[dict(id=r['id'],source=pin(CUSTODY,'/rules/'+str(i)),exact_rule=r) for i,r in enumerate(rd(CUSTODY)['rules']) if r['id'] in ce09['contract_rules']],
        inherited_projection_policy_requirements={key:dict(source=pin(CE09,'/'+key),exact_requirement=ce09[key]) for key in ['time_and_currentness_policy','signature_and_order_policy','invalidation_policy']},
        digest_and_signature_boundary=dict(source=pin(CUSTODY,'/projection'),exact_projection_contract=rd(CUSTODY)['projection'],
            SHA256_JCS_exact_genuine_complete_C_required_not_path_placeholder_or_partial_digest=True,
            acceptance_has_no_standalone_signature=True,
            future_CE10_approvals_cover_acceptance_with_C_digest_indirectly_not_extra_C_in_signed_core=True,
            bundle_has_no_independent_validity_field_effective_validity_is_of_its_five_records=True,
            future_CE10_coverage_not_sole_prior_authentication_for_W09_W10_or_five_acceptance_evidences=True,
            custody_contract_schema_anchors_selected_independently_not_C_or_bundle_self_trust=True,
            actual_complete_C_digest_or_crypto_approval_evidence=None,actual_C_or_acceptance_codec_crypto_or_schema_validation='NOT_RUN_NO_ACTUAL_BODIES'),
        scope_and_reconciliation_boundary=dict(W09_prior_proofs=pin(W09,'/prior_proof_boundary'),W10_final_records=pin(W10,'/freeze_record_ledger'),
            W10_reconciliation=pin(W10,'/reconciliation_and_invalidation_boundary'),
            exact_requester_caller_domain_constructor_registry_and_platform_linkage_required=True,
            exact_sources_runtime_image_profile_BASIS_index_resource_suite_epoch_role_key_scope_must_match_genuine_accepted_antecedents=True,
            image_digest_not_runtime_identity_and_schema_type_equality_not_actual_value_acceptance=True,
            preparer_records_complete_sorted_unique_actor_record_hash_and_current_authorship_binding_required=True,
            same_baseline_facts_authors_bodies_policies_and_resource_assumptions_no_automatic_prior_proof_transfer=True,
            changes_in_contributor_body_source_runtime_image_domain_resource_epoch_key_or_policy_invalidate_affected_CE02_CE11_and_W02_W12_require_review=True,
            actual_same_scope_reconciliation_and_all_accepted_proof_closure=None,actual_refresh_or_active_rebind=False),
        resource_and_cost_boundary=dict(source=pin(PLAN,'/resource_and_scope_policy'),exact_candidate_reserve_rules=rd(CONTRACT)['reserve_accounting'],
            full_evidence_bodies_registry_C_acceptance_memory_copy_hash_JCS_lookup_freshness_identity_crypto_and_output_costs_not_free=True,
            both_Reader_ledgers_global_heap_work_service_phase_failure_and_cleanup_composition_and_extra_graph_review_required=True,
            C8192_acceptance16384_are_candidate_serialized_limits_not_heap_CPU_or_measured_fit=True,
            actual_complete_body_fit_and_full_resource_derivation=None,reserve_transfers_applied=0,resources_reserved=False,quotas_or_budgets_changed=False),
        phase_handoff=dict(W12_consumer=pin(PLAN,'/work_packages/11'),
            W11_C_and_acceptance_require_prior_W09_W10_facts_not_future_bundle_E06_root_or_receipt=True,
            PJ01_PJ10_require_W11_evidence_PJ11_PJ12_deferred_to_W12_without_backward_dependency=True,
            W12_bundle_approvals_unique_mapping_W13_gates_and_final_E06_payload_Q_root_claim_receipt_not_created_or_accepted_here=True,
            CE11_does_not_depend_on_CE12_receipt=True,final_route_boundary=plan['prelaunch_handoff_and_CE12'],
            actual_positive_C_acceptance_bundle_mapping_Q_request_root_claim_receipt_or_authority_created=False),
        authority_boundary=dict(source=pin(PLAN,'/authorization_boundary'),inherited_boundary=plan['authorization_boundary'],
            allowed_now=['READ_DOCUMENTS_GIT_HASHES_AND_EXACT_PATH_PRESENCE','PREPARE_NEGATIVE_EXACT_C_ACCEPTANCE_DOSSIER','RUN_OWN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT'],
            no_positive_C_emission_configuration_codec_crypto_signing_keygen_enrollment_build_import_compile_discovery_tests_product_or_components=True,
            no_clock_CPU_IO_service_platform_ledger_claim_replay_crash_restart_endpoint_process_benchmarks_or_probes=True,
            no_identity_key_anchor_operator_service_selection_configuration_contacts_or_new_helpers_channels_inputs_outputs=True,
            actual_external_authority_material_or_operational_action=None),
        exit_predicate_dispositions=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/10/exit_predicates/'+str(i)),predicate=t,
            documentary_requirements_prepared=True,actual_evidence=None,actual_primary_reviews=None,actual_separate_R08_acceptance=None,accepted=False) for i,t in enumerate(w['exit_predicates'])],
        preserved_scope_and_gates={k:plan[k] for k in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']},
        current_effect={**{k:v for k,v in rd(W10)['current_effect'].items() if k!='W10_documentary_prepared'},
            'W11_documentary_prepared':True,'W11_accepted':False,'actual_exact_C_or_custody_acceptance_projected_created_or_issued':False},
        producer=dict(identity='Same Codex assistant/chat as I243/I244',documentary_preparer_only=True,actor_independent=False,
            competent_R01_review=False,competent_R02_review=False,competent_R03_review=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_C_issuance_custody_acceptance_resource_admission_or_execution_authority=True))


NEGATIVE_CASES = [
    ('SD01_bypass',('dependency_gate','SD01_stop_active'),True,False),
    ('W11_acceptance',('current_effect','W11_accepted'),False,True),
    ('reviews_as_freeze',('dependency_gate','documentary_reviews_not_genuine_acceptance_or_freeze'),True,False),
    ('invented_identity_roster',('identity_and_decision_boundary','actual_accepted_identity_role_preparer_author_requester_key_inventory'),None,'UNVERIFIED_TEST_LABEL'),
    ('truncated_preparers',('identity_and_decision_boundary','complete_preparer_records_actor_record_ids_and_SHA256_JCS_contribution_evidence_must_match_without_truncation'),True,False),
    ('positive_C_body',('schema_requirement_ledger',0,'actual_complete_body'),None,{}),
    ('unknown_C_size_zero',('schema_requirement_ledger',0,'actual_body_bytes'),None,0),
    ('C_cap_as_quota',('schema_requirement_ledger',0,'cap_applied_as_quota'),False,True),
    ('schema_constant_as_C_fact',('schema_requirement_ledger',0,'field_requirements',0,'actual_value'),None,'d5.prp181-trust-context.v3'),
    ('type_match_as_value_acceptance',('shared_type_requirement_ledger',0,'actual_value_projection_verified'),False,True),
    ('invented_projection',('value_projection_requirement_ledger',0,'actual_C_value'),None,'UNVERIFIED_TEST_LABEL'),
    ('validity_forced_equal',('validity_containment_requirement','type_shared_but_value_relation_is_containment_not_forced_interval_equality'),True,False),
    ('missing_containment',('validity_containment_requirement','C_validity_must_be_contained_in_each_current_relevant_antecedent_and_acceptance_interval'),True,False),
    ('nonconservative_clock',('validity_containment_requirement','platform_clock_error_lte_C_clock_error_lte5_and_trusted_now_error_both_sides_required'),True,False),
    ('constants_as_evidence',('exact_constant_requirements','known_schema_constants_are_requirements_not_evidence_of_real_values'),True,False),
    ('extra_bundle_hash_in_C',('exact_constant_requirements','C_closed_unchanged_no_bundle_hash_new_field_or_root_backpin'),True,False),
    ('custody_as_resource_admission',('exact_constant_requirements','acceptance_custody_only_not_resource_or_capture_admission'),True,False),
    ('predicted_antecedent_hash',('antecedent_hash_requirement_ledger',0,'actual_complete_body_hash'),None,'UNVERIFIED_TEST_LABEL'),
    ('prior_evidence_accepted',('prior_acceptance_evidence_requirement_ledger',0,'accepted'),False,True),
    ('predicate_verified',('projection_predicate_requirements',0,'verified'),False,True),
    ('partial_C_digest',('digest_and_signature_boundary','SHA256_JCS_exact_genuine_complete_C_required_not_path_placeholder_or_partial_digest'),True,False),
    ('standalone_acceptance_signature',('digest_and_signature_boundary','acceptance_has_no_standalone_signature'),True,False),
    ('extra_C_in_signed_core',('digest_and_signature_boundary','future_CE10_approvals_cover_acceptance_with_C_digest_indirectly_not_extra_C_in_signed_core'),True,False),
    ('invented_bundle_validity',('digest_and_signature_boundary','bundle_has_no_independent_validity_field_effective_validity_is_of_its_five_records'),True,False),
    ('future_bundle_as_prior_authentication',('digest_and_signature_boundary','future_CE10_coverage_not_sole_prior_authentication_for_W09_W10_or_five_acceptance_evidences'),True,False),
    ('self_selected_anchor',('digest_and_signature_boundary','custody_contract_schema_anchors_selected_independently_not_C_or_bundle_self_trust'),True,False),
    ('requester_domain_mismatch',('scope_and_reconciliation_boundary','exact_requester_caller_domain_constructor_registry_and_platform_linkage_required'),True,False),
    ('runtime_scope_substitution',('scope_and_reconciliation_boundary','exact_sources_runtime_image_profile_BASIS_index_resource_suite_epoch_role_key_scope_must_match_genuine_accepted_antecedents'),True,False),
    ('unchecked_value_provenance',('scope_and_reconciliation_boundary','image_digest_not_runtime_identity_and_schema_type_equality_not_actual_value_acceptance'),True,False),
    ('automatic_proof_transfer',('scope_and_reconciliation_boundary','same_baseline_facts_authors_bodies_policies_and_resource_assumptions_no_automatic_prior_proof_transfer'),True,False),
    ('actual_rebind',('scope_and_reconciliation_boundary','actual_refresh_or_active_rebind'),False,True),
    ('free_projection_costs',('resource_and_cost_boundary','full_evidence_bodies_registry_C_acceptance_memory_copy_hash_JCS_lookup_freshness_identity_crypto_and_output_costs_not_free'),True,False),
    ('serialized_cap_as_resource_fit',('resource_and_cost_boundary','C8192_acceptance16384_are_candidate_serialized_limits_not_heap_CPU_or_measured_fit'),True,False),
    ('reserve_transfer',('resource_and_cost_boundary','reserve_transfers_applied'),0,1),
    ('quota_change',('resource_and_cost_boundary','quotas_or_budgets_changed'),False,True),
    ('future_root_as_antecedent',('phase_handoff','W11_C_and_acceptance_require_prior_W09_W10_facts_not_future_bundle_E06_root_or_receipt'),True,False),
    ('backward_W12_dependency',('phase_handoff','PJ01_PJ10_require_W11_evidence_PJ11_PJ12_deferred_to_W12_without_backward_dependency'),True,False),
    ('actual_wire_C_or_root',('phase_handoff','actual_positive_C_acceptance_bundle_mapping_Q_request_root_claim_receipt_or_authority_created'),False,True),
    ('implicit_codec_or_product_execution',('authority_boundary','no_positive_C_emission_configuration_codec_crypto_signing_keygen_enrollment_build_import_compile_discovery_tests_product_or_components'),True,False),
    ('implicit_clock_probe',('authority_boundary','no_clock_CPU_IO_service_platform_ledger_claim_replay_crash_restart_endpoint_process_benchmarks_or_probes'),True,False),
    ('exit_accepted',('exit_predicate_dispositions',0,'accepted'),False,True),
    ('D5_closed',('current_effect','D5_closed'),False,True)]


def validate(d):
    for name,path,expected,_ in NEGATIVE_CASES:
        node = d
        for key in path:
            node = node[key]
        assert type(node) is type(expected) and node == expected, name
    assert d==build_candidate(), 'Candidate differs from source reconstruction'
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
            assert str(error)==name, (name,str(error))
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
    fields,closure=shared_contract()
    assert d['dependency_gate']['required_package_ids']==['W09','W10']
    assert [r['field'] for r in d['shared_type_requirement_ledger']]==fields and len(fields)==14
    assert [r['field'] for r in d['value_projection_requirement_ledger']]==[f for f in fields if f!='validity']
    assert len(d['value_projection_requirement_ledger'])==13 and len(closure)==6
    for row in d['shared_type_requirement_ledger']:
        assert row['exact_shared_schema']==fragment(row['C_source'])==fragment(row['acceptance_source'])
        assert row['actual_value_projection_verified'] is False
        assert all(v is None for k,v in row.items() if k.startswith('actual_') and k!='actual_value_projection_verified')
    for row in d['shared_definition_closure']:
        assert row['exact_shared_schema']==fragment(row['C_source'])==fragment(row['acceptance_source'])
    assert [len(r['field_requirements']) for r in d['schema_requirement_ledger']]==[19,27]
    for row in d['schema_requirement_ledger']:
        assert row['exact_schema']==fragment(row['source']) and row['exact_schema']['additionalProperties'] is False
        assert [r['field'] for r in row['field_requirements']]==row['exact_schema']['required']
        assert all(r['actual_value'] is None for r in row['field_requirements'])
        assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    assert len(d['antecedent_hash_requirement_ledger'])==4 and len(d['prior_acceptance_evidence_requirement_ledger'])==5
    assert [r['field'] for r in d['prior_acceptance_evidence_requirement_ledger']]==EVIDENCE_FIELDS
    assert len(d['projection_predicate_requirements'])==12
    assert [r['required_consumer_work_package'] for r in d['projection_predicate_requirements']]==['W11']*10+['W12']*2
    for row in d['projection_predicate_requirements']:
        assert row['exact_historical_requirement']==fragment(row['source']) and row['verified'] is False
    assert [r['id'] for r in d['contract_rule_requirements']]==['K08','K10','K11','K12','K13','K16']
    for row in d['contract_rule_requirements']:
        assert row['exact_rule']==fragment(row['source'])
    for key,row in d['inherited_projection_policy_requirements'].items():
        assert row['exact_requirement']==fragment(row['source'])==rd(CE09)[key]
    assert 'signature' not in rd(PACK)['$defs']['acceptance_record']['properties']
    assert 'trust_context' not in rd(PACK)['$defs']['custody_signed_core']['properties']
    assert 'validity' not in rd(PACK)['$defs']['custody_bundle']['properties']
    assert [r['id'] for r in d['role_scope_matrix']]==['R01','R02','R03','R06','R08']
    assert all(r['canonical_actor_id'] is None and r['accepted_appointment'] is False for r in d['role_scope_matrix'])
    for path in rd(PACK)['$defs']['source_bindings']['required']:
        assert not (ROOT/path).exists()
    for row in rd(CE07)['I177_binding_reference']:
        assert not (ROOT/row['path']).exists()
    for key,value in d['current_effect'].items():
        if key=='W11_documentary_prepared':
            assert value is True
        elif key=='IR03':
            assert value=='NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value==0
        else:
            assert value is False, key
    return dict(schema='d5.i245-preparation-review.v1',increment='I245',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,candidate=pin(SUBJECT),work_package=pin(PLAN,'/work_packages/10'),
        counts=dict(input_pins=1022,C_field_requirements=19,acceptance_field_requirements=27,shared_types=14,exact_value_projections=13,
            validity_containment_requirements=1,shared_transitive_definitions=6,antecedent_hash_requirements=4,prior_acceptance_evidences=5,
            predicate_requirements=12,W11_predicates=10,W12_deferred_predicates=2,contract_rules=6,unassigned_review_roles=5,pending_exits=3),
        source_reconstruction=dict(I244_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        limitations=['W09/W10 remain unaccepted, actual prior proofs and final frozen records missing, SD01 active. No positive C or custody acceptance is instantiated, issued or accepted.',
            'Fourteen type equalities and six transitive definitions are static requirements only. Thirteen exact value projections, validity containment,46 body fields, four antecedent hashes and five prior evidences lack actual complete bodies and competent decisions.',
            'Acceptance has no standalone signature; future CE10 covers its exact C digest indirectly and cannot supply sole prior authentication. No extra C/bundle-validity field is defined. Host/client time is not trusted runtime evidence.',
            'Same-assistant preparation is not independent competent review or R08 acceptance. No positive codec/crypto/C issuance, product/components/build/probes or clock/platform/service selection, quota/reserve/binding changes.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I245-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/schema/type-reference/projection/scope and in-memory document checks only. No target import/compile/discovery/tests/runs/build, positive codec/crypto, signing/keygen/enrollment/provisioning, clock/CPU/IO/service/platform/ledger/claim/replay/process sampling/probes or contacts.',
            over400_lines=True,reason='One W11 negative C/acceptance dossier with exact schemas/type/value/proof/predicate requirements, pins, rejection checks and preservation. Overage declared; no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_C_issuance_custody_acceptance_resource_admission_or_execution_authority=True))


def main():
    review=build_review()
    assert rd(PREP)==review
    prior=rd(PRIOR_SEAL)
    preserved={**prior['preserved_published709'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==714
    seal=rd(SEAL)
    assert seal['schema']=='d5.i245-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published714']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path)==digest, path
    assert seal['source_only'] is True and seal['current_effect']==review['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I245',input_pins=1022,preserved_published_files=714,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],SD01_stop_active=True,
        prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
