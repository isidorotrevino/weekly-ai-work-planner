#!/usr/bin/env python3
"""I213 documentary CE08 freeze specification; no product/component execution."""
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
BASE = 'f4bbc9782182ab0fed83dc89ef2fa1869c9c4838'
PLAN = P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
CHECK = P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE02 = P+'D5-I201-CE02-ANCHOR-PROVENANCE-CANDIDATE-02.json'
DOS = P+'D5-I193-CE08-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json'
PRIOR_AUDIT = P+'D5-I212-audit.py'
PRIOR_RECON = P+'D5-I212-I211-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I212-I211-documentary-review.json'
PRIOR_SEAL = P+'D5-I212-integrity.json'
PRIOR_DOC = 'docs/design/D5-I212-I211-CE07-REVIEW.md'
PRIOR_FILES = {PRIOR_AUDIT,PRIOR_RECON,PRIOR_REVIEW,PRIOR_SEAL,PRIOR_DOC}
AUDIT = P+'D5-I213-audit.py'
PREP = P+'D5-I213-preparation-review.json'
SEAL = P+'D5-I213-integrity.json'
DOC = 'docs/design/D5-I213-CE08-FINAL-ANTECEDENT-FREEZE.md'
FILES = {DOS,AUDIT,PREP,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_FINAL_RECORDS_MISSING'
FAMILIES = ['actor_registry','image_manifest','caller_identity','platform_custody']


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
    assert len(pins) == 862
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
def predecessor_CE08_presence_as_of_base():
    """Project only this new dossier's existence during historical documentary replay."""
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


def missing_freeze():
    return dict(actual_record_id=None,actual_canonical_body=None,actual_canonical_body_sha256=None,
        actual_body_bytes=None,actual_provider=None,actual_custody_locator=None,
        actual_configuration_epoch=None,actual_validity=None,actual_prior_authentication=None,
        actual_complete_evidence_body_inventory=None,actual_reviewer=None,actual_acceptance=None,
        actual_frozen=False,accepted=False)


def build_candidate():
    plan = rd(PLAN)
    step = plan['steps'][7]
    spec = rd(SPEC)
    defs = rd(PACK)['$defs']
    ce7path = plan['steps'][6]['candidate_dossier_path']
    ce7 = rd(ce7path)
    paths = {PLAN,CHECK,SPEC,PACK,CE01,CE02,PRIOR_REVIEW,PRIOR_RECON,ce7path}
    paths.update(v['path'] for v in plan['bindings'].values())
    dependencies = []
    for number,review in [(2,'D5-I202-I201-documentary-review.json'),
                          (3,'D5-I204-I203-documentary-review.json'),
                          (4,'D5-I206-I205-documentary-review.json'),
                          (5,'D5-I208-I207-documentary-review.json'),
                          (6,'D5-I210-I209-documentary-review.json'),
                          (7,'D5-I212-I211-documentary-review.json')]:
        path = CE02 if number == 2 else plan['steps'][number-1]['candidate_dossier_path']
        paths.update([path,P+review])
        dependencies.append(dict(step='CE%02d'%number,latest_candidate=pin(path),latest_documentary_review=pin(P+review),
            historical_planned_path=plan['steps'][number-1]['candidate_dossier_path'],
            documentary_review_available=True,competent_acceptance=False,actual_dependency_satisfied=False))
    freeze = []
    for index,family in enumerate(FAMILIES):
        freeze.append(dict(family=family,order=index+1,schema_source=pin(PACK,'/$defs/'+family),
            schema_fragment=defs[family],candidate_body_cap_bytes=spec['record_caps_bytes'][family],
            cap_applied_as_quota=False,cap_is_not_heap_CPU_or_evidence_completeness_proof=True,
            field_slots=[dict(field=k,actual_value=None,status='MISSING_NOT_POSITIVE_RECORD') for k in defs[family]['required']],
            **missing_freeze()))
    definition_names = ['actor','preparation_record','anchor_key','image_member_binding','image_dependency',
        'evidence_reference','source_bindings','validity']
    roles = []
    for row in rd(CE01)['role_scope_matrix']:
        if row['id'] in step['provenance_and_role']['primary_review_roles']:
            role = {k:v for k,v in row.items() if k != 'CE01_responsibilities'}
            role['CE08_responsibility'] = 'Review genuine final contributor/evidence/scope and antecedent consistency only within appointed role; R08 acceptance is separate.'
            roles.append(role)
    mappings = [dict(logical_path=path,actual_source_sha256=None,actual_image_member_id=None,
        actual_image_member_sha256=None,actual_representation=None,actual_mapping_evidence=None,
        README_must_be_DOCUMENT=path.endswith('/README.md'),actual_source_exists=(ROOT/path).exists(),accepted=False)
        for path in defs['source_bindings']['required']]
    return dict(schema='d5.i213-ce08-final-antecedent-freeze-candidate.v1',increment='I213',date='2026-11-17',
        timezone='Europe/Madrid',base_commit=BASE,proposal_id=ce7['proposal_id'],profile_id=ce7['profile_id'],step='CE08',
        kind='MISSING_FINAL_ANTECEDENT_FREEZE_DOCUMENTARY_DOSSIER_NOT_POSITIVE_RECORDS',
        status='CE08_DOCUMENTARY_FREEZE_SPECIFICATION_PREPARED_RECORDS_MISSING_NOT_FROZEN_NOT_ACCEPTED_NOT_ADMITTED',
        input_pins=historical_pins(),plan_binding=pin(PLAN,'/steps/7'),
        required_evidence=step['required_evidence'],planned_acceptance_checks=step['acceptance_checks'],
        contract_rules=step['contract_rules'],authorization_boundary=step['authorization_boundary'],
        contract_rule_requirements=[dict(id=r['id'],rule=r['rule'],source=pin(SPEC,'/rules/'+str(i)))
            for i,r in enumerate(spec['rules']) if r['id'] in step['contract_rules']],
        needs_fresh_snapshot_at_launch=step['needs_fresh_snapshot_at_launch'],
        dependency_gates=dependencies,documentary_inventory=[pin(p) for p in sorted(paths)],
        producer=dict(identity='Same Codex assistant/chat as earlier candidates',documentary_preparer_only=True,
            actor_independent=False,organizationally_independent=False,competent_acceptance=False,external_contacts_made=False),
        role_scope_matrix=roles,freeze_inventory=freeze,
        schema_helpers=[dict(name=n,source=pin(PACK,'/$defs/'+n),schema_fragment=defs[n]) for n in definition_names],
        contributor_closure=dict(provisional_CE03=pin(plan['steps'][2]['candidate_dossier_path'],'/freeze_and_refresh'),
            latest_CE07_documentary_review=pin(PRIOR_REVIEW),
            required_subjects=['all documentary preparers in accepted contract/evidence scope including current and later contributions',
                'all actual proof/evidence authors including CE07',
                'role holders source author accountable requester custodians and authentic signature/key principals'],
            actual_complete_contributor_inventory=None,actual_canonical_human_alias_resolution=None,
            actual_competence_and_appointment_evidence=None,actual_preparation_records=None,
            actual_complete_anchor_key_inventory=None,actual_contributor_count=None,
            actual_preparer_count=None,actual_key_count=None,
            source_document_hashes_not_authorship_evidence=True,same_chat_not_independent_acceptance=True,
            actor_registry_first_after_all_actual_authors_known=True,CE03_provisional_not_final=True,
            no_unrecorded_CE07_or_later_authors=True,no_forecast_person_or_synthetic_preparation_record=True,
            preparation_record_must_not_pin_C_acceptance_bundle_Q_root_or_receipt=True,
            canonical_alias_collisions_ambiguity_or_missing_competence_reject=True,
            software_caller_not_alternate_human_identity=True,complete_scope_verified=False),
        identity_and_separation_policy=dict(
            all_role_preparer_requester_source_author_custody_identities_resolve_to_canonical_humans=True,
            distinct_strings_or_keys_not_distinct_people=True,
            key_binding_unique_by_purpose_and_key_id_with_one_canonical_actor=True,
            R08_human_and_key_distinct_from_R01_and_R02=True,
            R01_R02_same_genuinely_competent_human_allowed_with_distinct_role_domain_approvals=True,
            actual_alias_key_identity_or_separation_verified=False,
            actual_CE10_approvals_or_signatures_created=False),
        typed_array_limits=dict(source=pin(PACK),preparers_min=defs['actor_registry']['properties']['documentary_preparation_records']['minItems'],
            preparers_max=defs['actor_registry']['properties']['documentary_preparation_records']['maxItems'],
            actors_max=defs['actor_registry']['properties']['actors']['maxItems'],
            keys_max=defs['anchor_registry']['properties']['keys']['maxItems'],
            dependencies_max=defs['image_manifest']['properties']['dependencies']['maxItems'],
            actual_counts=None,complete_sorted_unique_canonical_arrays_required=True,
            truncation_or_quota_increase_allowed=False,typed_indices_do_not_bound_underlying_proof_costs=True),
        source_runtime_policy=dict(source_to_image_missing_inventory=mappings,
            actual_complete_runtime_loader_stdlib_frozen_native_crypto_closure=None,
            actual_image_bytes_sha256=None,actual_runtime_sha256=None,actual_source_root_sha256=None,
            image_digest_must_not_replace_runtime_identity=True,
            source_bindings_and_mapping_exact_six_actual_digests_equal=True,
            historical480_or_six_sources_only_no_unbound_helpers=True,
            document_membership_not_test_runner_loaded_evidence=True,
            no_image_self_manifest_bundle_future_digest_embedding=True,
            actual_build_or_measurement_performed=False),
        policy_constant_bindings=dict(expected_image_schema_constants={k:v['const'] for k,v in defs['image_manifest']['properties'].items() if 'const' in v},
            expected_preparation_schema_constants={k:v['const'] for k,v in defs['preparation_record']['properties'].items() if 'const' in v},
            selected_custody_contract=pin(SPEC),selected_custody_schema_pack=pin(PACK),
            actual_image_implements_selected_policies=None,actual_final_body_constants_verified=False),
        antecedent_and_hash_policy=dict(I191_record_order=spec['record_order'],
            CE08_record_order=FAMILIES,anchor_policy_and_prior_authentication_required_before_actor_registry=True,
            actual_accepted_prior_BASIS_index_resource_proofs=None,
            prior_proofs_same_final_source_image_runtime_resource_scope_required=True,
            all_evidence_reference_bodies_available_and_authentic_before_acceptance=True,
            actual_full_referenced_evidence_closure=None,
            canonical_body_hash_rule='SHA256(JCS(each complete actual record)); source_root SHA256(JCS(actual source_bindings)). No placeholder/zero hash, path hash or predicted final digest.',
            same_epoch_and_overlapping_current_validity_required=True,
            caller_actor_registry_image_and_platform_cross_record_hashes_must_agree=True,
            canonical_requester_caller_domain_constructor_and_resource_scope_must_agree=True,
            later_CE10_bundle_approvals_cannot_supply_sole_prior_authentication=True,
            later_C_Q_final_root_or_receipt_not_CE08_antecedent=True,
            actual_canonical_codec_crypto_or_positive_schema_validation='NOT_RUN_NO_ACTUAL_BODIES'),
        freshness_policy=dict(source=pin(SPEC,'/rules/'+str(next(i for i,r in enumerate(spec['rules']) if r['id']=='K13'))),
            strict_not_before_lt_expires_at=True,snapshot_lifetime_max_seconds=3600,clock_error_max_seconds=5,
            trusted_now_current_epoch_and_known_revocation_required_at_every_boundary=True,
            actual_clock_currentness_or_epoch_evidence=None,actual_snapshot_validity=None,
            client_date_or_host_clock_is_not_trusted_runtime_evidence=True,
            stale_TOFU_hidden_online_file_lookup_or_instantaneous_revocation_claim=False,
            fresh_snapshot_when_ready_not_expiry_extension_by_plan_or_cache=True,
            actual_fresh_snapshot_created=False),
        invalidation_policy=dict(source=pin(plan['steps'][2]['candidate_dossier_path'],'/freeze_and_refresh'),
            changed_inputs=['contributor_or_alias_or_competence','preparation_or_proof_body','source_or_image_or_runtime',
                'caller_constructor_or_domain','platform_guarantee_clock_ledger_or_resource_scope','epoch_key_policy_contract_or_schema'],
            anchor_or_key_change_revisit_CE02_before_dependent_freeze=True,
            invalidate_all_dependent_candidate_digests_reviews_and_scope_acceptances=True,
            rerun_documentary_scope_CE03_to_CE10_as_needed_and_fresh_CE11_before_handoff=True,
            any_automatic_prior_proof_acceptance_or_hash_reuse=False,
            actual_downstream_hashes_created_or_rebound=False),
        phase_boundary=dict(CE08_four_antecedent_records_only=True,CE09_actual_C_and_acceptance_deferred=True,
            CE10_bundle_role_domain_approvals_and_unique_mapping_deferred=True,
            CE11_no_CE12_receipt_dependency=True,
            CE12_actual_claim_then_receipt_after_full_admission_and_separate_authorization=True,
            external_prerequisites_for_receipt=plan['closure_boundaries']['external_prerequisites_for_receipt'],
            documentary_freeze_is_not_active_capture_inputs_rebind=True,
            actual_C_Q_bundle_mapping_root_claim_receipt_created=False),
        inherited_scope_boundaries=ce7['inherited_scope_boundaries'],preserved_negative_gates=ce7['preserved_negative_gates'],
        permission_boundary={**ce7['permission_boundary'],'authorized_documentary_actions':['READ_SOURCE_JSON_GIT_HASHES',
            'PREPARE_CE08_MISSING_FINAL_ANTECEDENT_FREEZE_DOSSIER','RUN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT']},
        current_effect=dict(CE08_documentary_prepared=True,CE08_accepted=False,actual_dependency_satisfied=False,
            actual_antecedent_records_created=0,actual_antecedent_records_frozen=0,actual_evidence_accepted=0,
            actual_contributor_completeness_verified=False,actual_full_evidence_closure_verified=False,
            actual_canonical_hashes_caps_or_currentness_verified=False,actual_prior_proofs_accepted=False,
            independent_acceptance=False,resource_obligations_closed=0,product_or_components_executed=False,
            quotas_changed=False,reserves_changed=False,rebind_applied=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),
        historical_replay_policy=dict(CE08_absent_at_BASE=True,exact_Path_exists_query_only_during_predecessor_replay=True,
            restore_after_success_and_exception=True,historical_blobs_unchanged=True,prior_publication_mains_run=False,
            CE09_to_CE12_dossiers_still_absent=True),decision=plan['decision'],E06=plan['E06'])


def validate(d):
    assert d['freeze_inventory'][0]['actual_frozen'] is False, 'premature_actor_freeze'
    assert d['contributor_closure']['actual_complete_contributor_inventory'] is None, 'invented_authors'
    assert d['contributor_closure']['no_unrecorded_CE07_or_later_authors'] is True, 'omit_proof_authors'
    assert d['typed_array_limits']['truncation_or_quota_increase_allowed'] is False, 'trim_to_cap'
    assert d['source_runtime_policy']['image_digest_must_not_replace_runtime_identity'] is True, 'image_as_runtime'
    assert d['antecedent_and_hash_policy']['later_CE10_bundle_approvals_cannot_supply_sole_prior_authentication'] is True, 'future_bundle_bootstrap'
    assert d['antecedent_and_hash_policy']['later_C_Q_final_root_or_receipt_not_CE08_antecedent'] is True, 'reverse_dependency'
    assert d['freshness_policy']['actual_fresh_snapshot_created'] is False, 'fake_fresh_snapshot'
    assert d['invalidation_policy']['any_automatic_prior_proof_acceptance_or_hash_reuse'] is False, 'stale_hash_transfer'
    assert d['current_effect']['actual_antecedent_records_created'] == 0, 'positive_record_fabrication'
    assert d['current_effect']['resource_obligations_closed'] == 0, 'document_closes_resources'
    assert d['phase_boundary']['documentary_freeze_is_not_active_capture_inputs_rebind'] is True, 'active_rebind'
    plan = rd(PLAN)
    assert [r['family'] for r in d['freeze_inventory']] == plan['steps'][7]['record_families'] == FAMILIES
    for row in d['freeze_inventory']:
        for k,v in missing_freeze().items():
            assert row[k] == v and type(row[k]) is type(v), (row['family'],k)
        assert all(s['actual_value'] is None for s in row['field_slots'])
    assert [r['step'] for r in d['dependency_gates']] == plan['steps'][7]['depends_on']
    assert [r['id'] for r in d['role_scope_matrix']] == plan['steps'][7]['provenance_and_role']['primary_review_roles']
    for row in d['role_scope_matrix']:
        assert row['assigned_person'] is None and not row['accepted_appointment'] and row['current_actions_authorized'] == []
    assert all(not (ROOT/r['logical_path']).exists() for r in d['source_runtime_policy']['source_to_image_missing_inventory'])
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][:8])
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][8:])
    assert d == build_candidate(), 'Dossier differs from source reconstruction'


def rejection_checks(d):
    cases = [
        ('premature_actor_freeze',('freeze_inventory',0,'actual_frozen'),True),
        ('invented_authors',('contributor_closure','actual_complete_contributor_inventory'),[]),
        ('omit_proof_authors',('contributor_closure','no_unrecorded_CE07_or_later_authors'),False),
        ('trim_to_cap',('typed_array_limits','truncation_or_quota_increase_allowed'),True),
        ('image_as_runtime',('source_runtime_policy','image_digest_must_not_replace_runtime_identity'),False),
        ('future_bundle_bootstrap',('antecedent_and_hash_policy','later_CE10_bundle_approvals_cannot_supply_sole_prior_authentication'),False),
        ('reverse_dependency',('antecedent_and_hash_policy','later_C_Q_final_root_or_receipt_not_CE08_antecedent'),False),
        ('fake_fresh_snapshot',('freshness_policy','actual_fresh_snapshot_created'),True),
        ('stale_hash_transfer',('invalidation_policy','any_automatic_prior_proof_acceptance_or_hash_reuse'),True),
        ('positive_record_fabrication',('current_effect','actual_antecedent_records_created'),1),
        ('document_closes_resources',('current_effect','resource_obligations_closed'),1),
        ('active_rebind',('phase_boundary','documentary_freeze_is_not_active_capture_inputs_rebind'),False)]
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
    with predecessor_CE08_presence_as_of_base():
        rec = previous['reconstruct']()
        assert rec == rd(PRIOR_RECON) and previous['build_review'](rec) == rd(PRIOR_REVIEW)
    assert Path.exists is original and (ROOT/DOS).exists()
    class DocumentaryProbe(Exception):
        pass
    try:
        with predecessor_CE08_presence_as_of_base():
            assert not (ROOT/DOS).exists()
            raise DocumentaryProbe()
    except DocumentaryProbe:
        pass
    assert Path.exists is original and (ROOT/DOS).exists()
    plan = rd(PLAN)
    graph = {s['id']:s['depends_on'] for s in plan['steps']}
    closure = previous['ancestor_sets'](graph)
    assert closure['CE08'] == {'CE01','CE02','CE03','CE04','CE05','CE06','CE07'}
    order = previous['ancestor_sets'](rd(SPEC)['record_order'])
    assert {'ANCHOR','ACTOR_REGISTRY','IMAGE_MANIFEST','CALLER_IDENTITY'} <= order['PLATFORM_CUSTODY']
    assert not {'C_CONTEXT','ACCEPTANCE','BUNDLE','Q_REQUEST','FINAL_ROOT','LAUNCH_RECEIPT'} & order['PLATFORM_CUSTODY']
    defs = rd(PACK)['$defs']
    assert d['typed_array_limits']['preparers_min'] == 1 and d['typed_array_limits']['preparers_max'] == 16
    assert d['typed_array_limits']['actors_max'] == d['typed_array_limits']['keys_max'] == 64
    assert d['typed_array_limits']['dependencies_max'] == 128
    assert [r['id'] for r in d['contract_rule_requirements']] == plan['steps'][7]['contract_rules']
    for family in FAMILIES:
        gate = next(g for g in rd(CHECK)['family_gates'] if g['family'] == family)
        assert gate['final_record_freeze_step'] == 'CE08' and gate['accepted'] is False
        assert defs[family]['additionalProperties'] is False
    profile = rd(plan['bindings']['profile02']['path'])
    assert d['freshness_policy']['snapshot_lifetime_max_seconds'] == profile['bootstrap']['context_limits']['max_validity_seconds'] == 3600
    assert d['freshness_policy']['clock_error_max_seconds'] == profile['bootstrap']['context_limits']['max_clock_error_seconds'] == 5
    for key,value in d['current_effect'].items():
        if key == 'CE08_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_antecedent_records_created','actual_antecedent_records_frozen','actual_evidence_accepted','resource_obligations_closed']:
            assert value == 0 and type(value) is int
        else:
            assert value is False, key
    fields = sum(len(defs[n]['required']) for n in FAMILIES)
    return dict(schema='d5.i213-preparation-review.v1',increment='I213',date='2026-11-17',base_commit=BASE,
        status=STATUS,candidate=pin(DOS),plan=pin(PLAN,'/steps/7'),
        counts=dict(input_pins=862,freeze_families=4,missing_required_field_slots=fields,
            helper_schema_definitions=8,missing_source_mappings=6,unaccepted_dependencies=6,
            unassigned_role_slots=5,later_dossiers_absent=4,resource_obligations_closed=0),
        provenance=d['producer'],source_reconstruction=dict(prior_I212_reconstruction_and_review_reproduced=True,
            prior_publication_mains_run=False,exact_CE08_historical_absence_guard=True,
            guard_restored_after_success_and_exception=True,antecedent_and_step_DAGs_acyclic=True,
            no_future_C_bundle_root_receipt_reverse_dependency=True,CE03_provisional_scope_not_automatically_final=True,
            latest_CE02_candidate02_used_without_rewriting_historical_plan=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],decision=d['decision'],E06=d['E06'],
        limitations=['No actual final actors/preparers/keys, image/runtime/source mapping, caller/domain/platform records or proof bodies; actual counts/bytes/record hashes remain missing.',
            'No accepted CE02-CE07 dependencies, complete author closure, prior BASIS/index/resource proof, canonical positive schema/crypto validation or trusted fresh snapshot.',
            'Same assistant is not independent competent R01/R02/R03/R06 review or separate R08 acceptance. Documentary freeze specification is not actual finalization or admission.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I213-audit.py',expected_result=STATUS,
            runtime_harness='N/A: documentary JSON/Git/hash/schema-fragment/DAG checks only; no runtime, component, crypto/codec, build, enrollment, clock/ledger or process execution.',
            over400_lines=True,reason='One negative final-freeze dossier with four typed record contracts, missing fields, provenance and immutable preservation. Machine-readable evidence exceeds400 lines; no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_is_not_freeze_acceptance_or_admission=True))


def main():
    review = build_review()
    assert rd(PREP) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published549'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 554
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i213-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published554'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():
            assert sha(p) == h, p
    assert seal['source_only'] and seal['current_effect'] == review['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I213',historical_pins=862,preserved_published_files=554,
        new_files=5,documentary_rejections=12,current_effect=review['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
