#!/usr/bin/env python3
"""I218 static CE10 review; no product, positive codec, crypto or service execution."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '0bcd5fc4a5d8c1a9a4cc336f50e16b7b514f2e81'
DOS = P+'D5-I193-CE10-BUNDLE-APPROVAL-AND-CURRENT-MAPPING-CANDIDATE.json'
PLAN = P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
PROFILE = P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
BOUND = P+'D5-I192-I191-source-reconstruction.json'
CE09 = P+'D5-I193-CE09-EXACT-C-PROJECTION-CANDIDATE.json'
PRIOR_AUDIT = P+'D5-I217-audit.py'
PRIOR_PREP = P+'D5-I217-preparation-review.json'
PRIOR_SEAL = P+'D5-I217-integrity.json'
PRIOR_DOC = 'docs/design/D5-I217-CE10-BUNDLE-APPROVAL-CURRENT-MAPPING.md'
PRIOR_FILES = {DOS,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I218-I217-source-reconstruction.json'
REVIEW = P+'D5-I218-I217-documentary-review.json'
AUDIT = P+'D5-I218-audit.py'
SEAL = P+'D5-I218-integrity.json'
DOC = 'docs/design/D5-I218-I217-CE10-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_BUNDLE_APPROVALS_MAPPING_MISSING'


def rd(p):
    return json.loads((ROOT/p).read_text())


def sha(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def pin(p,pointer=''):
    return dict(path=p,sha256=sha(p),json_pointer=pointer)


def fragment(source):
    assert source['sha256'] == sha(source['path'])
    value = rd(source['path'])
    for token in source.get('json_pointer','').split('/')[1:]:
        key = token.replace('~1','/').replace('~0','~')
        value = value[int(key)] if isinstance(value,list) else value[key]
    return value


def verify_blobs(pins):
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()))
    for p,h in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', p
        body = stream.read(int(header[2]))
        assert stream.read(1) == b'\n' and hashlib.sha256(body).hexdigest() == h == sha(p), p
    assert stream.read() == b''


def ancestors(graph):
    done = {}
    active = set()
    def visit(n):
        assert n in graph and n not in active, n
        if n in done:
            return done[n]
        active.add(n)
        found = set()
        for parent in graph[n]:
            found.add(parent)
            found.update(visit(parent))
        active.remove(n)
        assert n not in found
        done[n] = found
        return found
    for n in graph:
        visit(n)
    return done


def literal_bytes(value):
    # Schema names/constants only. Never serialize an actual custody instance.
    return len(json.dumps(value,ensure_ascii=True,separators=(',',':')).encode('ascii'))


def envelope(node,defs,caps):
    """Reconstruct I192's conditional encoding model, not a universal instance bound."""
    if '$ref' in node:
        name = node['$ref'].removeprefix('#/$defs/')
        assert node['$ref'] == '#/$defs/'+name
        upper = envelope(defs[name],defs,caps)
        return min(upper,caps.get(name,upper))
    if 'const' in node:
        return literal_bytes(node['const'])
    if 'enum' in node:
        return max(map(literal_bytes,node['enum']))
    for key in ['oneOf','anyOf']:
        if key in node:
            return max(envelope(child,defs,caps) for child in node[key])
    kind = node['type']
    if kind == 'string':
        return 2+node['maxLength']*2
    if kind == 'integer':
        assert 0 <= node['minimum'] <= node['maximum'] <= 9007199254740991
        return len(str(node['maximum']))
    if kind == 'array':
        count = node['maxItems']
        return 2+count*envelope(node['items'],defs,caps)+max(count-1,0)
    assert kind == 'object' and node['additionalProperties'] is False
    assert set(node['required']) == set(node['properties'])
    parts = [literal_bytes(k)+1+envelope(v,defs,caps) for k,v in node['properties'].items()]
    return 2+sum(parts)+max(len(parts)-1,0)


def reconstruct():
    d = rd(DOS)
    plan = rd(PLAN)
    step = plan['steps'][9]
    spec = rd(SPEC)
    defs = rd(PACK)['$defs']
    profile = rd(PROFILE)
    pins = {**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 887
    verify_blobs(pins)
    assert d['step'] == step['id'] == 'CE10' and step['candidate_dossier_path'] == DOS
    assert d['plan_binding'] == pin(PLAN,'/steps/9')
    for a,b in [('required_evidence','required_evidence'),('planned_acceptance_checks','acceptance_checks'),
                ('contract_rules','contract_rules'),('authorization_boundary','authorization_boundary'),
                ('needs_fresh_snapshot_at_launch','needs_fresh_snapshot_at_launch')]:
        assert d[a] == step[b]
    assert len(d['required_evidence']) == 4 and len(d['planned_acceptance_checks']) == 3
    assert step['record_families'] == ['custody_bundle']
    assert len(d['documentary_inventory']) == len({s['path'] for s in d['documentary_inventory']}) == 18
    for source in d['documentary_inventory']:
        assert source['sha256'] == pins[source['path']] == sha(source['path'])
    assert [r['step'] for r in d['dependency_gates']] == step['depends_on'] == ['CE02','CE08','CE09']
    for row in d['dependency_gates']:
        s = next(s for s in plan['steps'] if s['id'] == row['step'])
        path = P+'D5-I201-CE02-ANCHOR-PROVENANCE-CANDIDATE-02.json' if row['step'] == 'CE02' else s['candidate_dossier_path']
        assert row['latest_candidate'] == pin(path) and row['historical_planned_path'] == s['candidate_dossier_path']
        assert fragment(row['latest_documentary_review'])['current_effect']['independent_acceptance'] is False
        assert row['documentary_review_available'] and not row['competent_acceptance'] and not row['actual_dependency_satisfied']
    assert [r['name'] for r in d['schema_obligations']] == ['custody_bundle','custody_signed_core','custody_approval']
    for row in d['schema_obligations']:
        assert fragment(row['source']) == row['schema_fragment'] == defs[row['name']]
        assert defs[row['name']]['additionalProperties'] is False
    core = defs['custody_signed_core']
    bundle = defs['custody_bundle']
    families = core['properties']['records']['required']
    assert families == ['actor_registry','image_manifest','caller_identity','platform_custody','acceptance_record']
    assert core['properties']['record_hashes']['required'] == families
    assert len(core['required']) == 8 and bundle['required'] == ['schema','signed_core','approvals']
    assert 'validity' not in bundle['properties'] and 'C' not in core['properties'] and 'trust_context' not in core['properties']
    assert defs['acceptance_record']['properties']['trust_context_sha256'] == {'$ref':'#/$defs/sha256'}
    assert not {'signature','signature_hex'} & set(defs['acceptance_record']['properties'])
    records = d['nested_record_inventory']
    assert [r['family'] for r in records] == families
    caps = {}
    effective = {}
    for row in records:
        name = row['family']
        assert fragment(row['schema_source']) == row['schema_fragment'] == defs[name]
        assert row['required_top_level_fields'] == defs[name]['required']
        assert row['candidate_body_cap_bytes'] == spec['record_caps_bytes'][name]
        caps[name] = row['candidate_body_cap_bytes']
        effective[name] = min(envelope(defs[name],defs,{}),caps[name])
        for key,value in row.items():
            if key.startswith('actual_'):
                assert value is (False if key == 'actual_cap_fit_verified' else None), (name,key)
        assert row['accepted'] is False
    assert sum(len(r['required_top_level_fields']) for r in records) == 88
    domains = spec['custody_approval_domains']
    assert list(domains) == bundle['properties']['approvals']['required'] == [r['role'] for r in d['approval_inventory']]
    approval_review = []
    for row in d['approval_inventory']:
        recipe = row['message_recipe']
        assert fragment(row['schema_source']) == defs['custody_approval']
        assert recipe['domain_ASCII'] == domains[row['role']] and recipe['domain_ASCII'].isascii()
        assert recipe['delimiter_hex'] == '00' and recipe['delimiter_octets'] == 1
        assert recipe['payload'] == 'JCS(the same complete actual signed_core for all three roles)'
        assert recipe['actual_message_bytes'] is None
        assert all(value is None for key,value in row.items() if key.startswith('actual_'))
        assert row['verified'] is False and row['accepted'] is False
        approval_review.append(dict(role=row['role'],domain=domains[row['role']],one_NUL_octet_required=True,
            same_complete_eight_field_core_required=True,actual_message_signature_or_verification_available=False))
    anchor = d['anchor_and_policy_selection']
    assert anchor['independent_selected_contract'] == pin(SPEC) and anchor['independent_selected_schema_pack'] == pin(PACK)
    assert anchor['preexisting_independently_accepted_registry_required']
    assert not anchor['supplied_C_bundle_root_key_or_self_signed_registry_may_bootstrap']
    assert anchor['actual_core_policy_pins_must_equal_external_selection_and_image_policy']
    assert anchor['actual_registry_provisioned_or_selected'] is False
    assert all(v is None for k,v in anchor.items() if k.startswith('actual_') and k not in ['actual_core_policy_pins_must_equal_external_selection_and_image_policy','actual_registry_provisioned_or_selected'])
    sig = d['signature_policy']
    assert sig['domains'] == domains and sig['domain_delimiter_hex'] == '00' and sig['domain_delimiter_octets'] == 1
    for key in ['three_role_approvals_required','all_three_must_cover_same_exact_core',
                'existing_root_two_signatures_do_not_replace_three_custody_approvals','R08_human_and_key_distinct_from_R01_and_R02',
                'R01_R02_same_qualified_human_key_allowed_with_separate_role_domain_approvals',
                'all_S01_source_author_root_key_and_purpose_restrictions_preserved',
                'C_bound_indirectly_via_acceptance_trust_context_sha256_no_new_C_body','acceptance_has_no_standalone_signature',
                'signatures_do_not_replace_provenance_completeness_resources_or_admission']:
        assert sig[key] is True
    assert sig['strict_profile_rules'] == {k:profile['cryptography'][k] for k in ['algorithm','public_key','signature','verification','implementation']}
    assert sig['excluded_from_signed_message'] == ['signature_fields','bundle_own_hash','launch_receipt','Q','final_root']
    assert sig['actual_signing_key_generation_crypto_or_verification_authorized'] is False
    assert sig['actual_signature_crypto_codec_or_positive_schema_validation'] == 'NOT_RUN_NO_ACTUAL_BODIES'
    mapping = d['current_mapping_requirements']
    assert fragment(mapping['source'])['id'] == 'K09'
    assert mapping['key_fields'] == ['configuration_epoch','SHA256(JCS(actual C))']
    assert mapping['required_unique_target_fields'] == ['bundle','caller','image','protection_domain','global_ledger_domain']
    for key in ['one_current_mapping_across_all_approved_callers_images_and_domains',
                'conflicts_stale_epoch_rollback_or_unknown_revocation_reject',
                'authenticated_resolution_before_P_ROOT_CHECK_and_freeze_C_Q_constructor',
                'worker_intrinsic_protected_custody_required','worker_does_not_infer_mapping_from_bytes_or_receive_new_I191_frame']:
        assert mapping[key] is True
    assert mapping['partitioned_per_caller_uniqueness_allowed'] is False and mapping['accepted'] is False
    mapping_flags = {'actual_C_Q_or_constructor_frozen','actual_backend_or_service_selected','actual_mapping_created'}
    for key,value in mapping.items():
        if key.startswith('actual_'):
            assert value is (False if key in mapping_flags else None), key
    assert mapping['new_mapping_record_schema_or_registry_configuration_created'] is False
    size = d['conditional_size_reference']
    historical = fragment(size['source'])
    raw = envelope(defs['custody_bundle'],defs,{})
    upper = envelope(defs['custody_bundle'],defs,caps)
    assert raw == historical['unrestricted_conservative_schema_upper_bytes']['custody_bundle'] == size['historical_unrestricted_bundle_schema_upper_bytes'] == 368348
    assert upper == historical['conditional_bundle_upper_bytes'] == size['historical_conditional_bundle_upper_bytes'] == 221644
    assert size['whole_bundle_candidate_cap_bytes'] == spec['record_caps_bytes']['custody_bundle'] == 262144
    assert 262144-upper == historical['conditional_bundle_margin_bytes'] == size['historical_conditional_margin_bytes'] == 40500
    assert effective == dict(actor_registry=98304,image_manifest=98304,caller_identity=1933,platform_custody=5940,acceptance_record=13879)
    assert sum(effective.values()) == 218360 and upper-sum(effective.values()) == 3284
    assert len(size['assumptions']) == 4 and 'two-bytes-per-character' in size['assumptions'][1]
    for key in ['actual_encoding_assumptions_verified','actual_nested_caps_verified','actual_bundle_fit_verified','unknown_evidence_costs_coerced_to_zero','trimming_or_quota_increase_allowed']:
        assert size[key] is False
    assert size['actual_whole_bundle_bytes'] is None and size['indices_not_complete_evidence_size_heap_CPU_IO_or_service_proof']
    resources = d['evidence_and_resource_boundary']
    assert resources['all_referenced_proof_bodies_must_exist_be_available_and_genuinely_reviewed']
    assert resources['per_attempt_lookup_freshness_identity_crypto_measurement_copies_registry_receipt_native_IO_charged_inside_phases']
    assert resources['both_process_Reader_ledgers_and_global_E01_E05_join_required']
    assert resources['offline_enrollment_or_build_does_not_make_verification_free'] and resources['no_free_external_evidence_work']
    assert resources['resource_obligations_closed'] == 0
    assert all(v is None for k,v in resources.items() if k.startswith('actual_'))
    fresh = d['freshness_policy']
    assert fresh['effective_bundle_validity_from_five_record_intervals_not_own_bundle_field']
    assert fresh['C_validity_contained_in_all_relevant_current_records'] and fresh['strict_not_before_lt_expires_at']
    assert fresh['max_validity_seconds'] == profile['bootstrap']['context_limits']['max_validity_seconds'] == 3600
    assert fresh['max_clock_error_seconds'] == profile['bootstrap']['context_limits']['max_clock_error_seconds'] == 5
    assert fresh['actual_clock_snapshot_epoch_or_error_evidence'] is None and fresh['actual_fresh_snapshot_created'] is False
    assert fresh['trusted_now_current_epoch_known_revocation_and_no_conflicting_mapping_required']
    assert fresh['no_TOFU_stale_cache_hidden_online_or_file_lookup'] and fresh['no_instantaneous_revocation_claim']
    graph = {s['id']:s['depends_on'] for s in plan['steps']}
    closure = ancestors(graph)
    order = ancestors(spec['record_order'])
    assert closure['CE10'] == {'CE%02d'%i for i in range(1,10)} and not {'CE11','CE12'} & closure['CE10']
    assert {'BUNDLE','C_CONTEXT'} <= order['EXTERNAL_CURRENT_MAPPING']
    assert not {'FINAL_ROOT','ATOMIC_CLAIM','LAUNCH_RECEIPT'} & order['EXTERNAL_CURRENT_MAPPING']
    assert 'CE12' not in closure['CE11'] and 'ATOMIC_CLAIM' in order['LAUNCH_RECEIPT']
    phases = d['phase_boundary']
    for key in ['CE10_bundle_approvals_mapping_require_accepted_CE02_CE08_CE09',
                'prior_authentication_not_supplied_solely_by_future_bundle','no_future_E06_root_receipt_as_antecedent',
                'CE11_review_before_handoff','CE11_no_CE12_receipt_dependency',
                'CE12_claim_before_receipt_after_full_admission_separate_authorization']:
        assert phases[key] is True
    for key in ['new_C_Q_field_file_pipe_helper_input_receipt_channel_allowed',
                'actual_C_Q_request_root_receipt_claim_constructor_issued_or_created','any_tool_contact_with_providers_authorized']:
        assert phases[key] is False
    assert phases['external_prerequisites_for_receipt'] == plan['closure_boundaries']['external_prerequisites_for_receipt']
    ce9 = rd(CE09)
    assert d['inherited_scope_boundaries'] == ce9['inherited_scope_boundaries']
    assert d['preserved_negative_gates'] == ce9['preserved_negative_gates']
    assert len(d['inherited_scope_boundaries']['S01_exclusions']) == 8
    assert d['permission_boundary']['denied_action_classes'] == ce9['permission_boundary']['denied_action_classes']
    assert [r['id'] for r in d['role_scope_matrix']] == step['provenance_and_role']['primary_review_roles'] == ['R01','R02','R06','R08']
    for row in d['role_scope_matrix']:
        assert row['assigned_person'] is None and row['accepted_appointment'] is False and row['current_actions_authorized'] == []
    for gate in d['preserved_negative_gates']:
        assert fragment({**gate['source'],'json_pointer':gate['json_pointer']}) == gate['observed_value']
    assert d['invalidation_policy']['no_automatic_prior_hash_proof_approval_or_mapping_transfer']
    assert d['invalidation_policy']['anchor_key_actor_author_body_scope_image_runtime_domain_resource_epoch_or_policy_change_requires_fresh_review']
    assert d['invalidation_policy']['revisit_CE02_and_CE03_to_CE10_as_affected_then_CE11']
    assert not d['invalidation_policy']['actual_rebind_or_reconfiguration']
    for key,value in d['current_effect'].items():
        if key == 'CE10_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_approvals_created','actual_evidence_accepted','resource_obligations_closed']:
            assert value == 0 and type(value) is int
        else:
            assert value is False, key
    assert d['decision'] == plan['decision'] and d['E06'] == plan['E06']
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][:10])
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][10:])
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    assert previous['build_review']() == rd(PRIOR_PREP)
    original = Path.exists
    assert git('ls-tree','--name-only',previous['BASE'],'--',DOS) == ''
    assert git('ls-tree','--name-only',BASE,'--',DOS) == DOS
    with previous['predecessor_CE10_presence_as_of_base']():
        assert not (ROOT/DOS).exists()
    assert Path.exists is original and (ROOT/DOS).exists()
    class DocumentaryProbe(Exception):
        pass
    try:
        with previous['predecessor_CE10_presence_as_of_base']():
            raise DocumentaryProbe()
    except DocumentaryProbe:
        pass
    assert Path.exists is original and (ROOT/DOS).exists()
    sections = {
        'K01':['anchor_and_policy_selection','dependency_gates'],
        'K03':['nested_record_inventory','evidence_and_resource_boundary','inherited_scope_boundaries'],
        'K08':['nested_record_inventory','freshness_policy','schema_obligations'],
        'K09':['current_mapping_requirements'],
        'K10':['signature_policy','role_scope_matrix'],
        'K11':['signature_policy','approval_inventory','anchor_and_policy_selection'],
        'K12':['phase_boundary','signature_policy'],
        'K13':['freshness_policy','current_mapping_requirements'],
        'K15':['evidence_and_resource_boundary','phase_boundary'],
        'K16':['conditional_size_reference','permission_boundary','current_effect']}
    assert [r['id'] for r in d['contract_rule_requirements']] == list(sections) == step['contract_rules']
    rules = []
    for row in d['contract_rule_requirements']:
        assert fragment(row['source']) == dict(id=row['id'],rule=row['rule'])
        rules.append(dict(id=row['id'],source=row['source'],candidate_sections=[pin(DOS,'/'+s) for s in sections[row['id']]],
            documentary_requirement_preserved=True,actual_competent_acceptance=False))
    return dict(schema='d5.i218-i217-source-reconstruction.v1',increment='I218',date='2026-11-17',base_commit=BASE,
        input_pins=pins,method='Fixed Git blobs and direct five-record/core/domain/purpose/global-mapping/cap/encoding/phase reconstruction. I217 documentary build reproduced without prior publication mains.',
        rule_review=rules,approval_review=approval_review,
        schema_review=dict(nested_families=families,nested_top_level_fields=88,bundle_top_level_fields=bundle['required'],
            signed_core_fields=core['required'],no_standalone_acceptance_signature=True,
            C_bound_only_by_exact_digest_in_acceptance_no_new_C_body=True,
            effective_validity_from_record_intervals_no_bundle_validity_field=True),
        conditional_size_review=dict(source=pin(BOUND,'/serialized_bounds'),model='I192 ASCII/safe-integer/two-byte escaping envelope; all actual encoding and per-record caps unverified',
            raw_model_upper_bytes=raw,assumed_caps=caps,effective_nested_model_terms=effective,
            effective_nested_sum_bytes=218360,remaining_model_structure_and_approvals_bytes=3284,
            conditional_upper_bytes=upper,whole_bundle_cap_bytes=262144,conditional_margin_bytes=40500,
            actual_bundle_bytes_or_fit_verified=False,complete_evidence_heap_CPU_IO_service_or900_proof=False),
        mapping_review=dict(key_fields=mapping['key_fields'],unique_target_fields=mapping['required_unique_target_fields'],
            uniqueness_global_across_all_callers_images_domains=True,no_partitioned_uniqueness=True,
            resolve_before_P_ROOT_CHECK_and_freeze_C_Q_constructor_required=True,
            no_worker_extra_frame_or_inferred_custody=True,actual_registry_backend_snapshot_or_mapping_available=False),
        phase_review=dict(step_graph=graph,CE10_ancestors=sorted(closure['CE10']),no_reverse_root_claim_receipt_dependency=True,
            CE11_not_dependent_on_CE12=True,CE12_claim_before_receipt_after_full_admission_and_separate_authorization=True),
        preservation=dict(documentary_inventory=18,unassigned_roles=4,unaccepted_dependencies=3,later_dossiers_absent=2,
            eight_S01_exclusions_unchanged=True,I217_build_and_twelve_documentary_rejections_reproduced=True,
            historical_CE10_absence_and_current_presence_verified=True,guard_restored_after_success_and_exception=True,
            prior_publication_mains_run=False),
        verdict=dict(new_blocking_documentary_findings=0,CE10_documentary_baseline_confirmed=True,CE10_accepted=False,
            actual_bundle_created=False,actual_approvals_created=0,actual_mapping_created=False,actual_mapping_uniqueness_verified=False,
            actual_signature_or_provenance_verified=False,actual_bundle_fit_verified=False,
            actual_evidence_accepted=0,independent_acceptance=False,resource_obligations_closed=0,product_or_components_executed=0))


def build_review(rec):
    d = rd(DOS)
    checks = [
        ('E01','Five final records/canonical hashes and independent policy/schema/anchors','REQUIREMENTS_PRESERVED_ACTUAL_RECORDS_REGISTRY_AND_ACCEPTANCE_MISSING'),
        ('E02','Three exact role-domain/NUL approvals over one complete core','PRESERVED_NO_SIGNING_KEY_GENERATION_OR_CRYPTO_EXECUTION'),
        ('E03','One authoritative current epoch/C mapping across caller/image/domain/ledger','GLOBAL_REQUIREMENT_NOT_PARTITIONED_OR_ACTUAL_SERVICE_PROOF'),
        ('E04','Nested caps/whole cap/evidence completeness/competent verification records','CONDITIONAL221644_ONLY_NOT_ACTUAL_FIT_OR_COMPLETE_RESOURCE_PROOF'),
        ('A01','Purpose/canonical actors/keys/S01/additional R08 exclusions/no self-bootstrap','PRESERVED_FOUR_UNASSIGNED_REVIEW_ROLES'),
        ('A02','Mandatory caps and I192 assumptions/margin','MODEL_REPRODUCED_ALL_ACTUAL_ENCODING_CAPS_AND_SIZES_UNKNOWN'),
        ('A03','No new C/Q/file/pipe/helper/input/receipt channel; separate authority/costs','NO_SERVICE_OR_CRYPTO_OR_PRODUCT_ACTION_AUTHORIZED')]
    return dict(schema='d5.i218-i217-documentary-review.v1',increment='I218',date='2026-11-17',timezone='Europe/Madrid',
        base_commit=BASE,proposal_id=d['proposal_id'],profile_id=d['profile_id'],step='CE10',
        status='CE10_DOCUMENTARY_BASELINE_CONFIRMED_BUNDLE_APPROVALS_MAPPING_MISSING_NOT_ACCEPTED_NOT_ADMITTED',
        candidate=pin(DOS),reconstruction=pin(RECON),findings=[],
        checks=[dict(id=i,scope=s,result=r) for i,s,r in checks],contract_rule_review=rec['rule_review'],
        documentary_clarifications=[
            dict(id='C01',subject='Three custody approvals versus root signatures',disposition='R01/R02/R08 all approve one complete core under distinct role domains plus one NUL. Root two-signature policy remains separate. R01/R02 sharing is conditional; R08 remains distinct.'),
            dict(id='C02',subject='Complete core and message exclusions',disposition='No field is stripped from the closed eight-field signed_core. Excluded outer approvals/signatures, bundle own hash, Q/root/receipt are outside it. C remains bound indirectly by acceptance digest, not a new member.'),
            dict(id='C03',subject='Conditional221644 and escaping',disposition='Static I192 model only: nested terms218360 plus structure/approvals3284. Mandatory real caps and encoding/escaping assumptions remain unverified; neither raw368348 nor margin40500 is actual size, infeasibility or resource evidence.'),
            dict(id='C04',subject='Global mapping',disposition='Exactly one current mapping for each epoch/C digest across every approved caller/image/protection domain, tied to one global ledger domain. Per-caller uniqueness is insufficient; no backend, positive mapping schema, endpoint or configuration is selected.')],
        provenance=dict(reviewer='Same Codex assistant/chat that prepared I217',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,competent_R01_R02_R06_review=False,
            separate_R08_acceptance=False,independent_acceptance=False),
        verdict=rec['verdict'],current_effect={**d['current_effect'],'CE10_documentary_review_completed':True,
            'CE10_documentary_confirmation':True,'CE10_documentary_revision_required':False},decision=d['decision'],E06=d['E06'],
        limitations=['No accepted CE02/CE08/CE09 prerequisites, five real nested records/C, actual approvals, external registry/keys/purposes, canonical bundle/bytes, verification records or globally unique current mapping.',
            'Conditional serialization and source-only schema/domain/mapping review are not positive codec/crypto/provenance checks, actual fit, complete evidence/resource proof,900-second evidence or admission.',
            'Same assistant is not competent independent review/separate R08 acceptance. No signing/key generation, crypto verification, registry/service/contact, product/component, quota/reserve/binding/authority/destination changes.'],
        next_scope='CE10 can serve as a documentarily reviewed missing-evidence baseline for separately requested CE11 preparation. No actual prelaunch gate, custody acceptance or execution authorization is supplied.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I218-audit.py',expected_result=STATUS,
            runtime_harness='N/A: documentary JSON/Git/hash/schema-envelope/domain and phase review only; no product/components, positive crypto/codec or service execution.',
            over400_lines=True,reason='One CE10 review with independent approval/global-mapping/conditional-cap reconstruction and immutable preservation; overage reported. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_is_not_bundle_mapping_acceptance_or_admission=True))


def main():
    rec = reconstruct()
    assert rd(RECON) == rec and rd(REVIEW) == build_review(rec)
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published574'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 579
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i218-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published579'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():
            assert sha(p) == h, p
    assert seal['source_only'] and seal['current_effect'] == rd(REVIEW)['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I218',historical_pins=887,preserved_published_files=579,
        new_files=5,original_documentary_rejections_reproduced=12,verdict=rec['verdict'],
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
