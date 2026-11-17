#!/usr/bin/env python3
"""I217 negative documentary bundle/mapping plan; no signing, verification or product execution."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'bdb7f82f13dffc92a90b75d10efea8ca80a92177'
PLAN = P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
PROFILE = P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
BOUND = P+'D5-I192-I191-source-reconstruction.json'
CE02 = P+'D5-I201-CE02-ANCHOR-PROVENANCE-CANDIDATE-02.json'
CE08 = P+'D5-I193-CE08-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json'
CE09 = P+'D5-I193-CE09-EXACT-C-PROJECTION-CANDIDATE.json'
DOS = P+'D5-I193-CE10-BUNDLE-APPROVAL-AND-CURRENT-MAPPING-CANDIDATE.json'
PRIOR_AUDIT = P+'D5-I216-audit.py'
PRIOR_RECON = P+'D5-I216-I215-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I216-I215-documentary-review.json'
PRIOR_SEAL = P+'D5-I216-integrity.json'
PRIOR_DOC = 'docs/design/D5-I216-I215-CE09-REVIEW.md'
PRIOR_FILES = {PRIOR_AUDIT,PRIOR_RECON,PRIOR_REVIEW,PRIOR_SEAL,PRIOR_DOC}
AUDIT = P+'D5-I217-audit.py'
PREP = P+'D5-I217-preparation-review.json'
SEAL = P+'D5-I217-integrity.json'
DOC = 'docs/design/D5-I217-CE10-BUNDLE-APPROVAL-CURRENT-MAPPING.md'
FILES = {DOS,AUDIT,PREP,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_BUNDLE_APPROVALS_MAPPING_MISSING'


def rd(p):
    return json.loads((ROOT/p).read_text())


def sha(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def pin(p,pointer=''):
    return dict(path=p,sha256=sha(p),json_pointer=pointer)


def historical_pins():
    pins = {**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 882
    return pins


def verify_blobs(pins):
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()))
    for p,h in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', p
        body = stream.read(int(header[2]))
        assert stream.read(1) == b'\n' and hashlib.sha256(body).hexdigest() == h == sha(p), p
    assert stream.read() == b''


@contextmanager
def predecessor_CE10_presence_as_of_base():
    """Project only new CE10 existence during predecessor documentary replay; no blob bypass."""
    assert git('ls-tree','--name-only',BASE,'--',DOS) == ''
    target = ROOT/DOS
    original = Path.exists
    assert original(target)
    def historical_exists(path):
        return False if path == target else original(path)
    Path.exists = historical_exists
    try:
        yield
    finally:
        Path.exists = original
    assert target.exists()


def schema_literal_length(value):
    # Constants and property names from schema documents only, never an actual custody body.
    return len(json.dumps(value,ensure_ascii=True,separators=(',',':')).encode('ascii'))


def conditional_schema_bound(node,defs,assumed_caps=None):
    """Static I192 ASCII/safe-integer envelope; no instance or positive codec run."""
    assumed_caps = assumed_caps or {}
    if '$ref' in node:
        assert node['$ref'].startswith('#/$defs/')
        name = node['$ref'][8:]
        raw = conditional_schema_bound(defs[name],defs,assumed_caps)
        return min(raw,assumed_caps.get(name,raw))
    if 'const' in node:
        return schema_literal_length(node['const'])
    if 'enum' in node:
        return max(schema_literal_length(x) for x in node['enum'])
    for name in ['anyOf','oneOf']:
        if name in node:
            return max(conditional_schema_bound(x,defs,assumed_caps) for x in node[name])
    kind = node['type']
    if kind == 'integer':
        assert 0 <= node['minimum'] <= node['maximum'] <= 9007199254740991
        return len(str(node['maximum']))
    if kind == 'string':
        return 2+2*node['maxLength']
    if kind == 'array':
        count = node['maxItems']
        return 2+count*conditional_schema_bound(node['items'],defs,assumed_caps)+max(0,count-1)
    assert kind == 'object' and node['additionalProperties'] is False
    props = node['properties']
    assert set(node['required']) == set(props)
    return 2+sum(schema_literal_length(k)+1+conditional_schema_bound(v,defs,assumed_caps) for k,v in props.items())+max(0,len(props)-1)


def build_candidate():
    plan = rd(PLAN)
    step = plan['steps'][9]
    spec = rd(SPEC)
    defs = rd(PACK)['$defs']
    ce9 = rd(CE09)
    families = defs['custody_signed_core']['properties']['records']['required']
    paths = {PLAN,SPEC,PACK,PROFILE,BOUND,CE02,CE08,CE09,PRIOR_RECON,PRIOR_REVIEW,
        P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'}
    paths.update(v['path'] for v in plan['bindings'].values())
    dependencies = []
    for number,path,review in [(2,CE02,'D5-I202-I201-documentary-review.json'),
                              (8,CE08,'D5-I214-I213-documentary-review.json'),
                              (9,CE09,'D5-I216-I215-documentary-review.json')]:
        paths.add(P+review)
        dependencies.append(dict(step='CE%02d'%number,latest_candidate=pin(path),latest_documentary_review=pin(P+review),
            historical_planned_path=plan['steps'][number-1]['candidate_dossier_path'],
            documentary_review_available=True,competent_acceptance=False,actual_dependency_satisfied=False))
    records = [dict(family=n,schema_source=pin(PACK,'/$defs/'+n),schema_fragment=defs[n],
        candidate_body_cap_bytes=spec['record_caps_bytes'][n],required_top_level_fields=defs[n]['required'],
        actual_complete_body=None,actual_canonical_bytes=None,actual_body_sha256=None,actual_body_bytes=None,
        actual_provider=None,actual_custody=None,actual_proof_body_inventory=None,actual_competent_review=None,
        actual_cap_fit_verified=False,accepted=False) for n in families]
    approvals = [dict(role=role,schema_source=pin(PACK,'/$defs/custody_approval'),
        message_recipe=dict(domain_ASCII=domain,delimiter_hex='00',delimiter_octets=1,
            payload='JCS(the same complete actual signed_core for all three roles)',actual_message_bytes=None),
        actual_canonical_actor=None,actual_key_id=None,actual_external_purpose_binding=None,actual_public_key=None,
        actual_signature=None,actual_signed_core_sha256=None,actual_provenance=None,actual_provider=None,
        actual_verification_record=None,actual_independent_reviewer=None,verified=False,accepted=False)
        for role,domain in spec['custody_approval_domains'].items()]
    return dict(schema='d5.i217-ce10-bundle-approval-current-mapping-candidate.v1',increment='I217',date='2026-11-17',
        timezone='Europe/Madrid',base_commit=BASE,proposal_id=ce9['proposal_id'],profile_id=ce9['profile_id'],step='CE10',
        kind='MISSING_BUNDLE_APPROVALS_CURRENT_MAPPING_DOCUMENTARY_DOSSIER_NOT_POSITIVE_RECORD_OR_CONFIGURATION',
        status='CE10_DOCUMENTARY_BUNDLE_MAPPING_SPECIFICATION_PREPARED_EVIDENCE_MISSING_NOT_ACCEPTED_NOT_ADMITTED',
        input_pins=historical_pins(),plan_binding=pin(PLAN,'/steps/9'),required_evidence=step['required_evidence'],
        planned_acceptance_checks=step['acceptance_checks'],contract_rules=step['contract_rules'],
        authorization_boundary=step['authorization_boundary'],needs_fresh_snapshot_at_launch=step['needs_fresh_snapshot_at_launch'],
        contract_rule_requirements=[dict(id=r['id'],rule=r['rule'],source=pin(SPEC,'/rules/'+str(i))) for i,r in enumerate(spec['rules']) if r['id'] in step['contract_rules']],
        documentary_inventory=[pin(p) for p in sorted(paths)],dependency_gates=dependencies,
        producer=dict(identity='Same Codex assistant/chat as prior candidates',documentary_preparer_only=True,
            actor_independent=False,organizationally_independent=False,competent_acceptance=False,external_contacts_made=False),
        role_scope_matrix=[{**{k:v for k,v in r.items() if k != 'CE09_responsibility'},
            'CE10_responsibility':'Review genuine appointed custody/purpose/epoch/provenance and same-core/mapping facts; R08 acceptance is separate.'}
            for r in ce9['role_scope_matrix'] if r['id'] in step['provenance_and_role']['primary_review_roles']],
        schema_obligations=[dict(name=n,source=pin(PACK,'/$defs/'+n),schema_fragment=defs[n])
            for n in ['custody_bundle','custody_signed_core','custody_approval']],
        nested_record_inventory=records,approval_inventory=approvals,
        anchor_and_policy_selection=dict(latest_CE02=pin(CE02),independent_selected_contract=pin(SPEC),
            independent_selected_schema_pack=pin(PACK),actual_external_anchor_registry=None,actual_registry_digest=None,
            actual_authority_registry_epoch=None,actual_identity_authority_and_purpose_key_bindings=None,
            actual_validity_currentness_revocation_proofs=None,
            preexisting_independently_accepted_registry_required=True,
            supplied_C_bundle_root_key_or_self_signed_registry_may_bootstrap=False,
            actual_core_policy_pins_must_equal_external_selection_and_image_policy=True,
            actual_image_policy_implementation_proof=None,actual_registry_provisioned_or_selected=False),
        signature_policy=dict(domains=spec['custody_approval_domains'],domain_delimiter_hex='00',domain_delimiter_octets=1,
            three_role_approvals_required=True,all_three_must_cover_same_exact_core=True,
            strict_profile_rules={k:rd(PROFILE)['cryptography'][k] for k in ['algorithm','public_key','signature','verification','implementation']},
            existing_root_two_signatures_do_not_replace_three_custody_approvals=True,
            R08_human_and_key_distinct_from_R01_and_R02=True,
            R01_R02_same_qualified_human_key_allowed_with_separate_role_domain_approvals=True,
            all_S01_source_author_root_key_and_purpose_restrictions_preserved=True,
            excluded_from_signed_message=['signature_fields','bundle_own_hash','launch_receipt','Q','final_root'],
            C_bound_indirectly_via_acceptance_trust_context_sha256_no_new_C_body=True,
            acceptance_has_no_standalone_signature=True,
            signatures_do_not_replace_provenance_completeness_resources_or_admission=True,
            actual_signing_key_generation_crypto_or_verification_authorized=False,
            actual_signature_crypto_codec_or_positive_schema_validation='NOT_RUN_NO_ACTUAL_BODIES'),
        current_mapping_requirements=dict(source=pin(SPEC,'/rules/'+str(next(i for i,r in enumerate(spec['rules']) if r['id']=='K09'))),
            key_fields=['configuration_epoch','SHA256(JCS(actual C))'],
            required_unique_target_fields=['bundle','caller','image','protection_domain','global_ledger_domain'],
            one_current_mapping_across_all_approved_callers_images_and_domains=True,
            partitioned_per_caller_uniqueness_allowed=False,actual_global_unique_mapping_proof=None,
            actual_configuration_epoch=None,actual_C_digest=None,actual_bundle_digest=None,actual_caller=None,
            actual_image=None,actual_protection_domain=None,actual_global_ledger_domain=None,actual_registry_snapshot=None,
            actual_provider_custody_and_competent_review=None,actual_conflict_rollback_or_currentness_evidence=None,
            conflicts_stale_epoch_rollback_or_unknown_revocation_reject=True,
            authenticated_resolution_before_P_ROOT_CHECK_and_freeze_C_Q_constructor=True,
            actual_C_Q_or_constructor_frozen=False,worker_intrinsic_protected_custody_required=True,
            worker_does_not_infer_mapping_from_bytes_or_receive_new_I191_frame=True,
            actual_backend_or_service_selected=False,new_mapping_record_schema_or_registry_configuration_created=False,
            actual_mapping_created=False,accepted=False),
        conditional_size_reference=dict(source=pin(BOUND,'/serialized_bounds'),
            historical_unrestricted_bundle_schema_upper_bytes=368348,
            historical_conditional_bundle_upper_bytes=221644,historical_conditional_margin_bytes=40500,
            whole_bundle_candidate_cap_bytes=spec['record_caps_bytes']['custody_bundle'],
            assumptions=['I192 ASCII/safe-integer JCS envelope applies to actual bodies',
                'actual string escaping satisfies the I192 two-bytes-per-character envelope; otherwise require a revised bound under unchanged caps',
                'every one of five nested actual bodies independently satisfies its mandatory byte cap',
                'closed unchanged typed schemas and three approval shapes; no extra member'],
            actual_encoding_assumptions_verified=False,actual_nested_caps_verified=False,
            actual_whole_bundle_bytes=None,actual_bundle_fit_verified=False,
            indices_not_complete_evidence_size_heap_CPU_IO_or_service_proof=True,
            unknown_evidence_costs_coerced_to_zero=False,trimming_or_quota_increase_allowed=False),
        evidence_and_resource_boundary=dict(all_referenced_proof_bodies_must_exist_be_available_and_genuinely_reviewed=True,
            actual_complete_reference_body_inventory=None,actual_provider_and_custody_proofs=None,
            actual_separate_competent_signature_and_provenance_verification_records=None,
            per_attempt_lookup_freshness_identity_crypto_measurement_copies_registry_receipt_native_IO_charged_inside_phases=True,
            both_process_Reader_ledgers_and_global_E01_E05_join_required=True,
            offline_enrollment_or_build_does_not_make_verification_free=True,
            actual_heap_CPU_IO_clock_service_phase_and900_proofs=None,resource_obligations_closed=0,
            no_free_external_evidence_work=True),
        freshness_policy=dict(effective_bundle_validity_from_five_record_intervals_not_own_bundle_field=True,
            C_validity_contained_in_all_relevant_current_records=True,
            strict_not_before_lt_expires_at=True,max_validity_seconds=3600,max_clock_error_seconds=5,
            trusted_now_current_epoch_known_revocation_and_no_conflicting_mapping_required=True,
            actual_clock_snapshot_epoch_or_error_evidence=None,no_TOFU_stale_cache_hidden_online_or_file_lookup=True,
            no_instantaneous_revocation_claim=True,actual_fresh_snapshot_created=False),
        phase_boundary=dict(CE10_bundle_approvals_mapping_require_accepted_CE02_CE08_CE09=True,
            prior_authentication_not_supplied_solely_by_future_bundle=True,
            no_future_E06_root_receipt_as_antecedent=True,CE11_review_before_handoff=True,
            CE11_no_CE12_receipt_dependency=True,CE12_claim_before_receipt_after_full_admission_separate_authorization=True,
            external_prerequisites_for_receipt=plan['closure_boundaries']['external_prerequisites_for_receipt'],
            new_C_Q_field_file_pipe_helper_input_receipt_channel_allowed=False,
            actual_C_Q_request_root_receipt_claim_constructor_issued_or_created=False,
            any_tool_contact_with_providers_authorized=False),
        invalidation_policy=dict(anchor_key_actor_author_body_scope_image_runtime_domain_resource_epoch_or_policy_change_requires_fresh_review=True,
            revisit_CE02_and_CE03_to_CE10_as_affected_then_CE11=True,
            no_automatic_prior_hash_proof_approval_or_mapping_transfer=True,actual_rebind_or_reconfiguration=False),
        inherited_scope_boundaries=ce9['inherited_scope_boundaries'],preserved_negative_gates=ce9['preserved_negative_gates'],
        permission_boundary={**ce9['permission_boundary'],'authorized_documentary_actions':['READ_SOURCE_JSON_GIT_HASHES',
            'PREPARE_CE10_NEGATIVE_BUNDLE_APPROVAL_MAPPING_DOSSIER','RUN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT']},
        historical_replay_policy=dict(CE10_absent_at_BASE=True,exact_Path_exists_query_only_during_predecessor_replay=True,
            restoration_after_success_and_exception_required=True,prior_publication_mains_run=False,CE11_CE12_dossiers_absent=True),
        current_effect=dict(CE10_documentary_prepared=True,CE10_accepted=False,actual_dependencies_satisfied=False,
            actual_bundle_created=False,actual_bundle_fit_verified=False,actual_approvals_created=0,
            actual_signature_or_provenance_verified=False,actual_mapping_created=False,actual_mapping_uniqueness_verified=False,
            actual_anchor_registry_provisioned=False,actual_evidence_accepted=0,independent_acceptance=False,
            resource_obligations_closed=0,product_or_components_executed=False,quotas_changed=False,reserves_changed=False,
            rebind_applied=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),decision=plan['decision'],E06=plan['E06'])


def validate(d):
    assert d['anchor_and_policy_selection']['supplied_C_bundle_root_key_or_self_signed_registry_may_bootstrap'] is False, 'self_bootstrap_key'
    assert len(d['approval_inventory']) == 3, 'missing_third_approval'
    assert d['signature_policy']['domain_delimiter_hex'] == '00' and d['signature_policy']['domain_delimiter_octets'] == 1, 'missing_NUL'
    assert d['signature_policy']['all_three_must_cover_same_exact_core'] is True, 'mixed_signed_cores'
    assert d['signature_policy']['R08_human_and_key_distinct_from_R01_and_R02'] is True, 'waived_R08_separation'
    assert d['current_mapping_requirements']['partitioned_per_caller_uniqueness_allowed'] is False, 'partitioned_mapping'
    assert d['conditional_size_reference']['actual_bundle_fit_verified'] is False, 'conditional_bound_as_actual_fit'
    assert d['evidence_and_resource_boundary']['no_free_external_evidence_work'] is True, 'free_proof_costs'
    assert d['phase_boundary']['new_C_Q_field_file_pipe_helper_input_receipt_channel_allowed'] is False, 'hidden_channel'
    assert d['signature_policy']['actual_signing_key_generation_crypto_or_verification_authorized'] is False, 'active_crypto_authorized'
    assert d['current_mapping_requirements']['actual_mapping_created'] is False, 'invented_mapping'
    assert d['current_effect']['CE10_accepted'] is False, 'documentary_acceptance'
    plan = rd(PLAN)
    assert [r['step'] for r in d['dependency_gates']] == plan['steps'][9]['depends_on'] == ['CE02','CE08','CE09']
    assert [r['id'] for r in d['role_scope_matrix']] == plan['steps'][9]['provenance_and_role']['primary_review_roles']
    for row in d['nested_record_inventory']:
        assert all(value is None for key,value in row.items() if key.startswith('actual_') and key != 'actual_cap_fit_verified')
        assert row['actual_cap_fit_verified'] is False and row['accepted'] is False
    for row in d['approval_inventory']:
        assert all(value is None for key,value in row.items() if key.startswith('actual_'))
        assert row['message_recipe']['actual_message_bytes'] is None and row['verified'] is False and row['accepted'] is False
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][:10])
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][10:])
    assert d == build_candidate(), 'Dossier differs from source reconstruction'


def rejection_checks(d):
    cases = [
        ('self_bootstrap_key',('anchor_and_policy_selection','supplied_C_bundle_root_key_or_self_signed_registry_may_bootstrap'),True),
        ('missing_third_approval',('approval_inventory',),d['approval_inventory'][:2]),
        ('missing_NUL',('signature_policy','domain_delimiter_octets'),0),
        ('mixed_signed_cores',('signature_policy','all_three_must_cover_same_exact_core'),False),
        ('waived_R08_separation',('signature_policy','R08_human_and_key_distinct_from_R01_and_R02'),False),
        ('partitioned_mapping',('current_mapping_requirements','partitioned_per_caller_uniqueness_allowed'),True),
        ('conditional_bound_as_actual_fit',('conditional_size_reference','actual_bundle_fit_verified'),True),
        ('free_proof_costs',('evidence_and_resource_boundary','no_free_external_evidence_work'),False),
        ('hidden_channel',('phase_boundary','new_C_Q_field_file_pipe_helper_input_receipt_channel_allowed'),True),
        ('active_crypto_authorized',('signature_policy','actual_signing_key_generation_crypto_or_verification_authorized'),True),
        ('invented_mapping',('current_mapping_requirements','actual_mapping_created'),True),
        ('documentary_acceptance',('current_effect','CE10_accepted'),True)]
    out = []
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
            out.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return out


def build_review():
    d = rd(DOS)
    verify_blobs(d['input_pins'])
    validate(d)
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    original = Path.exists
    with predecessor_CE10_presence_as_of_base():
        rec = previous['reconstruct']()
        assert rec == rd(PRIOR_RECON) and previous['build_review'](rec) == rd(PRIOR_REVIEW)
    assert Path.exists is original and (ROOT/DOS).exists()
    class DocumentaryProbe(Exception):
        pass
    try:
        with predecessor_CE10_presence_as_of_base():
            assert not (ROOT/DOS).exists()
            raise DocumentaryProbe()
    except DocumentaryProbe:
        pass
    assert Path.exists is original and (ROOT/DOS).exists()
    spec = rd(SPEC)
    defs = rd(PACK)['$defs']
    families = defs['custody_signed_core']['properties']['records']['required']
    caps = {n:spec['record_caps_bytes'][n] for n in families}
    raw = conditional_schema_bound(defs['custody_bundle'],defs)
    upper = conditional_schema_bound(defs['custody_bundle'],defs,caps)
    historical = rd(BOUND)['serialized_bounds']
    assert raw == historical['unrestricted_conservative_schema_upper_bytes']['custody_bundle'] == 368348
    assert upper == historical['conditional_bundle_upper_bytes'] == 221644
    assert spec['record_caps_bytes']['custody_bundle']-upper == historical['conditional_bundle_margin_bytes'] == 40500
    assert d['conditional_size_reference']['whole_bundle_candidate_cap_bytes'] == 262144
    assert len(d['nested_record_inventory']) == 5 and sum(len(defs[n]['required']) for n in families) == 88
    assert [r['family'] for r in d['nested_record_inventory']] == families
    assert [r['role'] for r in d['approval_inventory']] == list(spec['custody_approval_domains']) == defs['custody_bundle']['properties']['approvals']['required']
    for row in d['approval_inventory']:
        recipe = row['message_recipe']
        assert recipe['domain_ASCII'] == spec['custody_approval_domains'][row['role']]
        assert recipe['domain_ASCII'].isascii() and recipe['delimiter_hex'] == '00' and recipe['delimiter_octets'] == 1
    assert defs['custody_signed_core']['properties']['record_hashes']['required'] == families
    for name in ['custody_bundle','custody_signed_core','custody_approval']:
        assert defs[name]['additionalProperties'] is False
    assert d['current_mapping_requirements']['key_fields'] == ['configuration_epoch','SHA256(JCS(actual C))']
    assert d['current_mapping_requirements']['one_current_mapping_across_all_approved_callers_images_and_domains']
    assert d['current_mapping_requirements']['required_unique_target_fields'] == ['bundle','caller','image','protection_domain','global_ledger_domain']
    assert d['decision'] == rd(PLAN)['decision'] and d['E06'] == rd(PLAN)['E06']
    plan = rd(PLAN)
    graph = {s['id']:s['depends_on'] for s in plan['steps']}
    order = previous['ancestors'](graph)
    assert order['CE10'] == {'CE%02d'%i for i in range(1,10)} and 'CE12' not in order['CE11']
    assert [r['id'] for r in d['contract_rule_requirements']] == plan['steps'][9]['contract_rules']
    assert len(defs['custody_bundle']['required']) == 3 and len(defs['custody_signed_core']['required']) == 8
    assert 'validity' not in defs['custody_bundle']['properties']
    assert d['freshness_policy']['max_validity_seconds'] == rd(PROFILE)['bootstrap']['context_limits']['max_validity_seconds'] == 3600
    assert d['freshness_policy']['max_clock_error_seconds'] == rd(PROFILE)['bootstrap']['context_limits']['max_clock_error_seconds'] == 5
    for row in d['role_scope_matrix']:
        assert row['assigned_person'] is None and row['accepted_appointment'] is False and row['current_actions_authorized'] == []
    for key,value in d['current_effect'].items():
        if key == 'CE10_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_approvals_created','actual_evidence_accepted','resource_obligations_closed']:
            assert value == 0 and type(value) is int
        else:
            assert value is False, key
    return dict(schema='d5.i217-preparation-review.v1',increment='I217',date='2026-11-17',base_commit=BASE,
        status=STATUS,candidate=pin(DOS),plan=pin(PLAN,'/steps/9'),
        counts=dict(input_pins=882,nested_record_families=5,nested_top_level_fields=88,bundle_fields=3,signed_core_fields=8,
            missing_role_approvals=3,unaccepted_dependencies=3,unassigned_role_slots=4,later_dossiers_absent=2,resource_obligations_closed=0),
        conditional_serialization_review=dict(source=pin(BOUND,'/serialized_bounds'),raw_ASCII_schema_upper=raw,
            assumed_nested_caps=caps,conditional_ASCII_upper=upper,conditional_margin=262144-upper,
            actual_bodies_caps_encoding_or_fit_verified=False,complete_evidence_heap_CPU_IO_or_service_bound=False),
        provenance=d['producer'],source_reconstruction=dict(prior_I216_reconstruction_and_review_reproduced=True,
            prior_publication_mains_run=False,exact_CE10_historical_absence_guard=True,guard_restored_success_and_exception=True,
            no_reverse_root_receipt_dependency=True,global_mapping_not_partitioned_per_caller=True,
            I216_indirect_C_digest_and_no_standalone_bundle_validity_preserved=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],decision=d['decision'],E06=d['E06'],
        limitations=['No actual nested records, C, approvals, signature verification records, authentic external registry or global unique mapping. All competent dependencies and real evidence remain missing.',
            'Conditional221644/margin40500 requires I192 encoding assumptions and mandatory nested caps; no actual size/fit, complete-evidence cost, resource or900-second proof is supplied.',
            'Same assistant is not competent independent R01/R02/R06 review or separate R08 acceptance. No contact, enrollment, provisioning, signing/key generation, crypto verification or mapping service action is authorized.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I217-audit.py',expected_result=STATUS,
            runtime_harness='N/A: documentary JSON/Git/hash/schema-bound/phase checks only; no product/components, positive codec/crypto, service, clock/ledger or process execution.',
            over400_lines=True,reason='One negative bundle/approval/mapping dossier with exact caps, provenance and immutable preservation; overage reported. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_is_not_bundle_mapping_acceptance_or_admission=True))


def main():
    review = build_review()
    assert rd(PREP) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published569'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 574
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i217-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published574'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():
            assert sha(p) == h, p
    assert seal['source_only'] and seal['current_effect'] == review['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I217',historical_pins=882,preserved_published_files=574,
        new_files=5,documentary_rejections=12,current_effect=review['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
