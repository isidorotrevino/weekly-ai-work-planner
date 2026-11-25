#!/usr/bin/env python3
"""I246 W11 methodological review. Own documentary checks; no target execution."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '1eedb75402652a5e8d5d68d33a9a5a3fc3a64074'
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
PRIOR_AUDIT = P+'D5-I245-audit.py'
PRIOR_PREP = P+'D5-I245-preparation-review.json'
PRIOR_SEAL = P+'D5-I245-integrity.json'
PRIOR_DOC = 'docs/design/D5-I245-W11-EXACT-C-ACCEPTANCE.md'
SUBJECT = P+'D5-I223-W11-EXACT-C-ACCEPTANCE-CANDIDATE.json'
PRIOR_FILES = {SUBJECT,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I246-I245-source-reconstruction.json'
REVIEW = P+'D5-I246-I245-documentary-review.json'
AUDIT = P+'D5-I246-audit.py'
SEAL = P+'D5-I246-integrity.json'
DOC = 'docs/design/D5-I246-I245-W11-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W11_REVIEW_C_ACCEPTANCE_AND_ACCEPTED_FACTS_MISSING_NOT_ADMITTED'
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


def require_missing(row, false_fields=()):
    for key,value in row.items():
        if key.startswith('actual_'):
            assert value is False if key in false_fields else value is None, key
    if 'accepted' in row:
        assert row['accepted'] is False


def require_true(row, names):
    for key in names:
        assert row[key] is True, key


def reference_closure(shared_fragments, cdefs, adefs):
    # Iterative schema traversal independent of I245's recursive set collector.
    pending, seen = list(shared_fragments),set()
    while pending:
        value=pending.pop()
        if isinstance(value,list):
            pending.extend(value)
        elif isinstance(value,dict):
            if '$ref' in value:
                ref=value['$ref']
                assert ref.startswith('#/$defs/')
                name=ref[len('#/$defs/'):]
                if name not in seen:
                    assert cdefs[name]==adefs[name]
                    seen.add(name)
                    pending.append(cdefs[name])
            pending.extend(value.values())
    assert seen=={'identity','proposal_scope','sha256','trusted_key','validity','verifier_profile'}
    return sorted(seen)


def inspect(d):
    plan,ce09,cdefs,adefs=rd(PLAN),rd(CE09),rd(CPACK)['$defs'],rd(PACK)['$defs']
    w=plan['work_packages'][10]
    c,a=cdefs['trust_context'],adefs['acceptance_record']
    assert d['work_package']=='W11' and d['planned_deliverable_id']==w['deliverable_id']
    assert fragment(d['work_package_binding'])==w
    for key,source in [('required_deliverables','deliverables'),('required_exit_predicates','exit_predicates'),('reject_if','reject_if'),('needs_separate_future_authority_for','needs_separate_future_authority_for')]:
        assert d[key]==w[source],key
    gate=d['dependency_gate']
    assert gate['required_package_ids']==fragment(gate['source'])==w['depends_on']==['W09','W10']
    assert gate['SD01_stop_active'] is True and gate['documentary_reviews_not_genuine_acceptance_or_freeze'] is True
    assert all(gate['W%02d_accepted'%i] is False for i in range(1,11))
    require_missing(gate)
    assert d['role_scope_matrix']==[r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R01','R02','R03','R06','R08']]
    identity=d['identity_and_decision_boundary']
    assert fragment(identity['source'])==rd(W02)['identity_policy']
    assert identity['exact_identity_policy']==rd(W02)['identity_policy']['exact_policy']
    assert identity['exact_separation_matrix']==rd(W02)['separation_matrix'] and len(identity['exact_separation_matrix'])==14
    assert identity['exact_overlap_policy']==rd(W02)['overlap_policy']
    assert identity['required_provider_kind']==w['provider_kind']
    assert identity['primary_review_roles']==w['primary_review_roles']==['R01','R02','R03','R06']
    assert identity['separate_acceptor_role']==w['separate_acceptor_role']=='R08'
    require_true(identity,['all_roles_preparers_authors_requester_issuer_acceptor_and_keys_from_genuine_canonical_registry_competence_appointments_and_prior_acceptance',
        'complete_preparer_records_actor_record_ids_and_SHA256_JCS_contribution_evidence_must_match_without_truncation',
        'software_principal_not_alternate_human_and_no_git_assistant_or_role_string_as_independence'])
    require_missing(identity)
    ledger=d['schema_requirement_ledger']
    assert [r['kind'] for r in ledger]==['C','ACCEPTANCE']
    for row,path,definition,expected,cap in zip(ledger,[CPACK,PACK],['trust_context','acceptance_record'],[c,a],[8192,16384]):
        assert row['source']['path']==path and row['source']['json_pointer']=='/$defs/'+definition
        assert row['exact_schema']==fragment(row['source'])==expected
        assert expected['additionalProperties'] is False
        assert row['candidate_body_cap_bytes']==cap and row['cap_applied_as_quota'] is False
        assert [s['field'] for s in row['field_requirements']]==expected['required']
        assert all(s['actual_value'] is None and s['status']=='MISSING_NOT_POSITIVE_BODY' for s in row['field_requirements'])
        require_missing(row)
    assert [len(r['field_requirements']) for r in ledger]==[19,27]
    assert ledger[1]['candidate_body_cap_bytes']==rd(CUSTODY)['record_caps_bytes']['acceptance_record']
    common=sorted(set(c['properties'])&set(a['properties']))
    shared=[key for key in common if c['properties'][key]==a['properties'][key]]
    assert len(common)==15 and len(shared)==14 and set(common)-set(shared)=={'schema'}
    assert [r['field'] for r in d['shared_type_requirement_ledger']]==shared
    for row in d['shared_type_requirement_ledger']:
        field=row['field']
        assert row['exact_shared_schema']==fragment(row['C_source'])==fragment(row['acceptance_source'])==c['properties'][field]==a['properties'][field]
        assert row['type_identity_documentarily_verified'] is True
        require_missing(row,['actual_value_projection_verified'])
    closure=reference_closure([c['properties'][f] for f in shared],cdefs,adefs)
    assert [r['name'] for r in d['shared_definition_closure']]==closure
    for row in d['shared_definition_closure']:
        assert row['exact_shared_schema']==fragment(row['C_source'])==fragment(row['acceptance_source'])==cdefs[row['name']]==adefs[row['name']]
    values=d['value_projection_requirement_ledger']
    assert [r['field'] for r in values]==[f for f in shared if f!='validity'] and len(values)==13
    for row in values:
        assert fragment(row['source'])==next(r for r in ce09['shared_type_projection'] if r['field']==row['field'])
        assert row['required_relation']=='EXACT_ACCEPTED_VALUE_EQUALITY' and row['verified'] is False
        require_missing(row)
    validity=d['validity_containment_requirement']
    assert fragment(validity['source'])==ce09['time_and_currentness_policy']
    require_true(validity,['type_shared_but_value_relation_is_containment_not_forced_interval_equality',
        'C_validity_must_be_contained_in_each_current_relevant_antecedent_and_acceptance_interval',
        'strict_not_before_lt_expires_at_lifetime_at_most3600_and_same_current_epoch',
        'platform_clock_error_lte_C_clock_error_lte5_and_trusted_now_error_both_sides_required'])
    require_missing(validity)
    assert validity['verified'] is False
    constants=d['exact_constant_requirements']
    assert constants['C_constants']=={key:value['const'] for key,value in c['properties'].items() if 'const' in value}
    assert set(constants['C_constants'])=={'schema','repository_id','root_path','offline_key_status'}
    assert constants['acceptance_decision_constant']==a['properties']['decision']['const']=='IDENTITY_IMAGE_CUSTODY_ONLY_NOT_RESOURCE_OR_CAPTURE_ADMISSION'
    require_true(constants,['known_schema_constants_are_requirements_not_evidence_of_real_values',
        'C_closed_unchanged_no_bundle_hash_new_field_or_root_backpin','acceptance_custody_only_not_resource_or_capture_admission'])
    assert constants['actual_constants_in_genuine_C_and_acceptance_verified'] is False
    hashes=d['antecedent_hash_requirement_ledger']
    assert [(r['acceptance_field'],r['family']) for r in hashes]==ANTECEDENTS
    for i,row in enumerate(hashes):
        assert row['source']['path']==W10 and row['source']['json_pointer']=='/freeze_record_ledger/'+str(i)
        assert fragment(row['source'])==rd(W10)['freeze_record_ledger'][i]
        assert row['acceptance_field'] in a['required'] and row['verified'] is False
        require_missing(row)
    evidence=d['prior_acceptance_evidence_requirement_ledger']
    assert [r['field'] for r in evidence]==EVIDENCE_FIELDS
    for row in evidence:
        assert row['source']['path']==PACK and row['source']['json_pointer']=='/$defs/acceptance_record/properties/'+row['field']
        assert fragment(row['source'])==a['properties'][row['field']]
        require_missing(row)
    predicates=d['projection_predicate_requirements']
    assert [r['id'] for r in predicates]==['PJ%02d'%i for i in range(1,13)]
    assert [r['required_consumer_work_package'] for r in predicates]==['W11']*10+['W12']*2
    for i,row in enumerate(predicates):
        assert row['exact_historical_requirement']==ce09['projection_predicates'][i]==fragment(row['source'])
        assert row['verified'] is False
        require_missing(row)
    selected=[r for r in rd(CUSTODY)['rules'] if r['id'] in ce09['contract_rules']]
    assert [r['id'] for r in d['contract_rule_requirements']]==ce09['contract_rules']==['K08','K10','K11','K12','K13','K16']
    assert [r['exact_rule'] for r in d['contract_rule_requirements']]==selected
    for row in d['contract_rule_requirements']:
        assert row['exact_rule']==fragment(row['source'])
    policies=d['inherited_projection_policy_requirements']
    assert set(policies)=={'time_and_currentness_policy','signature_and_order_policy','invalidation_policy'}
    for key,row in policies.items():
        assert row['exact_requirement']==ce09[key]==fragment(row['source'])
    time=policies['time_and_currentness_policy']['exact_requirement']
    assert time['max_validity_seconds']==3600 and time['max_clock_error_seconds']==5
    assert time['platform_error_lte_C_error_lte5'] is True and time['host_or_client_date_not_trusted_runtime_time'] is True
    assert time['actual_clock_or_snapshot_selected'] is False
    signature=d['digest_and_signature_boundary']
    assert signature['exact_projection_contract']==rd(CUSTODY)['projection']==fragment(signature['source'])
    require_true(signature,['SHA256_JCS_exact_genuine_complete_C_required_not_path_placeholder_or_partial_digest',
        'acceptance_has_no_standalone_signature',
        'future_CE10_approvals_cover_acceptance_with_C_digest_indirectly_not_extra_C_in_signed_core',
        'bundle_has_no_independent_validity_field_effective_validity_is_of_its_five_records',
        'future_CE10_coverage_not_sole_prior_authentication_for_W09_W10_or_five_acceptance_evidences',
        'custody_contract_schema_anchors_selected_independently_not_C_or_bundle_self_trust'])
    assert signature['actual_complete_C_digest_or_crypto_approval_evidence'] is None
    assert signature['actual_C_or_acceptance_codec_crypto_or_schema_validation']=='NOT_RUN_NO_ACTUAL_BODIES'
    assert 'signature' not in a['properties']
    core,bundle=adefs['custody_signed_core'],adefs['custody_bundle']
    assert core['additionalProperties'] is False and bundle['additionalProperties'] is False
    assert len(core['required'])==8 and bundle['required']==['schema','signed_core','approvals']
    records=core['properties']['records']
    assert records['additionalProperties'] is False and set(records['properties'])=={'actor_registry','image_manifest','caller_identity','platform_custody','acceptance_record'}
    assert records['properties']['acceptance_record']=={'$ref':'#/$defs/acceptance_record'}
    assert 'trust_context_sha256' in a['required'] and 'C' not in core['properties'] and 'validity' not in bundle['properties']
    scope=d['scope_and_reconciliation_boundary']
    for key,path,field in [('W09_prior_proofs',W09,'prior_proof_boundary'),('W10_final_records',W10,'freeze_record_ledger'),('W10_reconciliation',W10,'reconciliation_and_invalidation_boundary')]:
        assert scope[key]['path']==path and fragment(scope[key])==rd(path)[field]
    require_true(scope,['exact_requester_caller_domain_constructor_registry_and_platform_linkage_required',
        'exact_sources_runtime_image_profile_BASIS_index_resource_suite_epoch_role_key_scope_must_match_genuine_accepted_antecedents',
        'image_digest_not_runtime_identity_and_schema_type_equality_not_actual_value_acceptance',
        'preparer_records_complete_sorted_unique_actor_record_hash_and_current_authorship_binding_required',
        'same_baseline_facts_authors_bodies_policies_and_resource_assumptions_no_automatic_prior_proof_transfer',
        'changes_in_contributor_body_source_runtime_image_domain_resource_epoch_key_or_policy_invalidate_affected_CE02_CE11_and_W02_W12_require_review'])
    require_missing(scope,['actual_refresh_or_active_rebind'])
    resource=d['resource_and_cost_boundary']
    assert fragment(resource['source'])==plan['resource_and_scope_policy']
    assert resource['exact_candidate_reserve_rules']==rd(CONTRACT)['reserve_accounting']
    require_true(resource,['full_evidence_bodies_registry_C_acceptance_memory_copy_hash_JCS_lookup_freshness_identity_crypto_and_output_costs_not_free',
        'both_Reader_ledgers_global_heap_work_service_phase_failure_and_cleanup_composition_and_extra_graph_review_required',
        'C8192_acceptance16384_are_candidate_serialized_limits_not_heap_CPU_or_measured_fit'])
    require_missing(resource)
    assert type(resource['reserve_transfers_applied']) is int and resource['reserve_transfers_applied']==0
    assert resource['resources_reserved'] is False and resource['quotas_or_budgets_changed'] is False
    phase=d['phase_handoff']
    assert fragment(phase['W12_consumer'])==plan['work_packages'][11]
    require_true(phase,['W11_C_and_acceptance_require_prior_W09_W10_facts_not_future_bundle_E06_root_or_receipt',
        'PJ01_PJ10_require_W11_evidence_PJ11_PJ12_deferred_to_W12_without_backward_dependency',
        'W12_bundle_approvals_unique_mapping_W13_gates_and_final_E06_payload_Q_root_claim_receipt_not_created_or_accepted_here',
        'CE11_does_not_depend_on_CE12_receipt'])
    assert phase['actual_positive_C_acceptance_bundle_mapping_Q_request_root_claim_receipt_or_authority_created'] is False
    assert phase['final_route_boundary']==plan['prelaunch_handoff_and_CE12']
    authority=d['authority_boundary']
    assert authority['inherited_boundary']==plan['authorization_boundary']==fragment(authority['source'])
    require_true(authority,['no_positive_C_emission_configuration_codec_crypto_signing_keygen_enrollment_build_import_compile_discovery_tests_product_or_components',
        'no_clock_CPU_IO_service_platform_ledger_claim_replay_crash_restart_endpoint_process_benchmarks_or_probes',
        'no_identity_key_anchor_operator_service_selection_configuration_contacts_or_new_helpers_channels_inputs_outputs'])
    require_missing(authority)
    assert [r['predicate'] for r in d['exit_predicate_dispositions']]==w['exit_predicates']
    for row in d['exit_predicate_dispositions']:
        assert row['predicate']==fragment(row['source'])
        require_missing(row)
    assert d['preserved_scope_and_gates']=={k:plan[k] for k in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']}
    for key,value in d['current_effect'].items():
        if key=='W11_documentary_prepared':
            assert value is True
        elif key=='IR03':
            assert value=='NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value==0
        else:
            assert value is False,key
    check_pointers(d)
    return dict(common_names=common,identical_type_fields=shared,exact_value_fields=[f for f in shared if f!='validity'],
        shared_transitive_definitions=closure,validity_relation='CONTAINMENT_NOT_FORCED_EQUALITY',
        C_coverage_route='signed_core.records.acceptance_record.trust_context_sha256 == SHA256(JCS(exact complete genuine C))',
        actual_values_bodies_digests_crypto_or_acceptance_verified=False)


CRITERIA=[
    'Exact W11 deliverables, W09/W10 dependencies, exits, rejections and positive-codec/issuance restriction match I223',
    'SD01 active and W01-W10 unaccepted; documentary review is not freeze or genuine acceptance',
    'R01/R02/R03/R06 and separate R08 remain without competent appointments/decisions',
    'W02 canonical identity,14 separation requirements and qualified R01/R02 overlap remain exact',
    'Complete role/preparer/author/requester/key provenance and no synthetic human/software substitution',
    'C19 and acceptance27 closed required fields retain unknown bodies/values/bytes/hashes',
    'C8192/acceptance16384 remain candidate serialized limits, not quotas or resource fit',
    'Fifteen common names yield fourteen identical field types; differing schema constants are excluded',
    'Independent iterative reference traversal reproduces six identical transitive definitions',
    'Thirteen exact accepted-value projections are distinct from static type equality',
    'Validity type equality requires interval containment rather than identical endpoints',
    'Strict lifetime3600/current epoch and conservative platform_error<=C_error<=5 remain unproved',
    'Host/client date and stale/TOFU/hidden lookup are not trusted runtime currentness',
    'Four exact C constants and custody-only acceptance decision cannot serve as genuine facts',
    'Four antecedent hash requirements retain exact W10 family/field correspondence',
    'Five prior basis/resource/R01/R02/R08 evidence references require real complete accepted bodies',
    'PJ01-PJ10 belong to W11; PJ11-PJ12 remain deferred W12 without backward acceptance dependency',
    'Six custody rules and three CE09 policies match exact source text and pointers',
    'Exact full-C JCS digest is required; acceptance has no standalone signature',
    'Closed eight-field signed_core contains five records and covers C indirectly by acceptance digest',
    'Closed three-field bundle has no independent validity or extra C field',
    'Future CE10 coverage cannot supply sole prior authentication or self-selected anchors',
    'Exact source/runtime/image/caller/domain/requester/BASIS/index/resource/suite/epoch scope remains missing',
    'New author/body/source/domain/resource/key/policy invalidates affected candidates without automatic transfer/rebind',
    'C/acceptance/evidence costs remain inside both Readers and full heap/work/service/phase composition',
    'Reserve/budget/resource rules remain unchanged and missing bounds are not replaced by serialized caps',
    'W12 bundle/mapping, W13 gates and final E06/Q/root/claim/receipt remain separate',
    'Inherited scope exclusions, negative gates, CE12 and no-product/no-codec/no-clock authority preserved',
    'Three exits remain unaccepted; no positive C, custody acceptance, evidence package or D5 closure is created']


def reconstruct():
    d=rd(SUBJECT)
    projection=inspect(d)
    pins={**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==1027
    verify_blobs(pins)
    return dict(schema='d5.i246-source-reconstruction.v1',increment='I246',date=DATE,base_commit=BASE,subject=pin(SUBJECT),input_pins=pins,
        criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],
        counts=dict(input_pins=1027,C_field_requirements=19,acceptance_field_requirements=27,shared_types=14,exact_value_projections=13,
            validity_containment_requirements=1,shared_transitive_definitions=6,antecedent_hash_requirements=4,prior_acceptance_evidences=5,
            predicate_requirements=12,W11_predicates=10,W12_deferred_predicates=2,contract_rules=6,unassigned_review_roles=5,pending_exits=3,review_criteria=len(CRITERIA)),
        independent_projection_reconstruction=projection,current_effect={**d['current_effect'],'W11_documentary_reviewed':True})


def own_rejections(d):
    cases=[
        ('C_field_omission',('schema_requirement_ledger',0,'field_requirements'),d['schema_requirement_ledger'][0]['field_requirements'][:-1]),
        ('extra_shared_schema_field',('shared_type_requirement_ledger',),d['shared_type_requirement_ledger']+[dict(field='schema')]),
        ('shared_type_substitution',('shared_type_requirement_ledger',0,'exact_shared_schema'),{'type':'integer'}),
        ('shared_definition_omission',('shared_definition_closure',),d['shared_definition_closure'][:-1]),
        ('transitive_sha_length_change',('shared_definition_closure',2,'exact_shared_schema','maxLength'),63),
        ('validity_as_exact_value',('value_projection_requirement_ledger',0,'field'),'validity'),
        ('projection_relation_substitution',('value_projection_requirement_ledger',0,'required_relation'),'INTERVAL_EQUALITY'),
        ('epoch_lifetime_waiver',('validity_containment_requirement','strict_not_before_lt_expires_at_lifetime_at_most3600_and_same_current_epoch'),False),
        ('repository_constant_alias',('exact_constant_requirements','C_constants','repository_id'),'UNVERIFIED_TEST_ALIAS'),
        ('C_cap_change',('schema_requirement_ledger',0,'candidate_body_cap_bytes'),8193),
        ('antecedent_family_substitution',('antecedent_hash_requirement_ledger',0,'family'),'image_manifest'),
        ('prior_evidence_omission',('prior_acceptance_evidence_requirement_ledger',),d['prior_acceptance_evidence_requirement_ledger'][:-1]),
        ('PJ11_premature_W11_consumer',('projection_predicate_requirements',10,'required_consumer_work_package'),'W11'),
        ('custody_decision_substitution',('exact_constant_requirements','acceptance_decision_constant'),'UNVERIFIED_TEST_ADMISSION'),
        ('clock_error_extension',('inherited_projection_policy_requirements','time_and_currentness_policy','exact_requirement','max_clock_error_seconds'),6),
        ('host_date_as_runtime',('inherited_projection_policy_requirements','time_and_currentness_policy','exact_requirement','host_or_client_date_not_trusted_runtime_time'),False),
        ('standalone_signature_inherited_policy',('inherited_projection_policy_requirements','signature_and_order_policy','exact_requirement','acceptance_has_standalone_signature'),True),
        ('projection_contract_substitution',('digest_and_signature_boundary','exact_projection_contract','C'),'UNVERIFIED_TEST_CONTRACT'),
        ('wrong_next_package',('phase_handoff','W12_consumer'),copy.deepcopy(d['scope_and_reconciliation_boundary']['W10_final_records'])),
        ('blanket_R01_R02_separation',('identity_and_decision_boundary','exact_overlap_policy','no_blanket_R01_R02_separation_added'),False),
        ('positive_codec_state',('digest_and_signature_boundary','actual_C_or_acceptance_codec_crypto_or_schema_validation'),'PASS'),
        ('missing_prior_body_zero',('prior_acceptance_evidence_requirement_ledger',0,'actual_complete_proof_body_record_id_bytes_digest_author_provider_custody_and_availability'),0)]
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
    return dict(schema='d5.i246-documentary-review.v1',increment='I246',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,subject=pin(SUBJECT),reconstruction=pin(RECON),
        verdict='DOCUMENTARY_REQUIREMENTS_CONSISTENT_NO_NEW_DEFECT_FOUND_REAL_C_AND_ACCEPTANCE_MISSING_NOT_ADMITTED',findings=[],
        counts=rec['counts'],criteria=rec['criteria'],independent_projection_reconstruction=rec['independent_projection_reconstruction'],
        documentary_clarifications=[
            'Fifteen common field names yield fourteen identical types; schema differs. Thirteen exact accepted-value projections exclude validity, whose required relation is containment without forced endpoint equality.',
            'Forty-six C/acceptance slots, four antecedent hashes and five prior evidences remain missing. Known constants and static type equality do not instantiate genuine C, custody records or trusted facts.',
            'Acceptance has no standalone signature. CE10 signed_core covers C indirectly through records.acceptance_record.trust_context_sha256; no extra C body or independent bundle validity field is added.',
            'Conservative platform_error<=C_error<=5, strict lifetime<=3600, current epoch/revocation and trusted-now checks remain unproved. Host/client date cannot supply trusted runtime time.',
            'Actual W09 acceptance and W10 frozen facts remain missing. Future CE10 approvals, E06/root/receipt or keys claimed in C/bundle cannot supply sole prior authentication or independently selected anchors.',
            'PJ01-PJ10 remain W11 requirements; PJ11-PJ12 deferred W12. Full same-scope identity/proof/resource costs and change invalidation remain required, with no actual rebind, quota/reserve change, wire C or execution.'],
        source_reconstruction=dict(primary_source_checks=True,I245_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        inherited_I245_rejection_checks=prep['rejection_checks'],additional_I246_rejection_checks=additional,current_effect=rec['current_effect'],
        provenance=dict(identity='Same Codex assistant/chat as I245',methodological_documentary_review_only=True,actor_independent=False,
            competent_R01_review=False,competent_R02_review=False,competent_R03_review=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['W09/W10 remain unaccepted; positive C and custody acceptance bodies, actual values/digests, complete evidence/currentness and competent independent decisions remain missing. W11 exits unaccepted.',
            'SD01 active; zero accepted real packages, zero closed prelaunch gates and zero closed E01-E05 obligations. No resource/capacity/service/success900 or infeasibility proof.',
            'Same-assistant documentary checks do not satisfy competent independent review or R08 acceptance; publication grants no C issuance, positive codec/crypto, product/component or quota authority.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I246-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/schema/type-reference/projection/scope checks and in-memory document mutations only. No target imports/compile/discovery/tests/runs/build, positive codec/crypto, signing/keygen/enrollment/provisioning, clock/CPU/IO/service/platform/ledger/claim/replay/process sampling/probes or contacts.',
            over400_lines=True,reason='One W11 review with primary-source reconstruction, pinned inputs, independent reference traversal, rejection checks and integrity preservation. Overage declared; no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_C_issuance_custody_acceptance_resource_admission_or_execution_authority=True))


def main():
    rec=reconstruct()
    assert rec==rd(RECON)
    review=build_review(rec)
    assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL)
    preserved={**prior['preserved_published714'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==719
    seal=rd(SEAL)
    assert seal['schema']=='d5.i246-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published719']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I246',input_pins=1027,preserved_published_files=719,new_files=5,
        criteria=len(CRITERIA),inherited_documentary_rejections=len(review['inherited_I245_rejection_checks']),
        additional_documentary_rejections=len(review['additional_I246_rejection_checks']),findings=review['findings'],
        SD01_stop_active=True,prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
