#!/usr/bin/env python3
"""I215 negative CE09 documentary projection; no product or positive codec execution."""
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
BASE = '4d005e0470ada3d1af1654973e15d595d5bb24f2'
PLAN = P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
PROTO = P+'D5-I185-PGO181-SCHEMAS-CANDIDATE-02.json'
PROFILE = P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
CE08 = P+'D5-I193-CE08-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json'
DOS = P+'D5-I193-CE09-EXACT-C-PROJECTION-CANDIDATE.json'
PRIOR_AUDIT = P+'D5-I214-audit.py'
PRIOR_RECON = P+'D5-I214-I213-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I214-I213-documentary-review.json'
PRIOR_SEAL = P+'D5-I214-integrity.json'
PRIOR_DOC = 'docs/design/D5-I214-I213-CE08-REVIEW.md'
PRIOR_FILES = {PRIOR_AUDIT,PRIOR_RECON,PRIOR_REVIEW,PRIOR_SEAL,PRIOR_DOC}
AUDIT = P+'D5-I215-audit.py'
PREP = P+'D5-I215-preparation-review.json'
SEAL = P+'D5-I215-integrity.json'
DOC = 'docs/design/D5-I215-CE09-EXACT-C-PROJECTION.md'
FILES = {DOS,AUDIT,PREP,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_C_AND_ACCEPTANCE_MISSING'


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
    assert len(pins) == 872
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
def predecessor_CE09_presence_as_of_base():
    """Only the new CE09 existence query is projected during predecessor documentary replay."""
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


def referenced_defs(value):
    result = set()
    if isinstance(value,dict):
        if '$ref' in value:
            assert value['$ref'].startswith('#/$defs/')
            result.add(value['$ref'].split('/')[-1])
        for child in value.values():
            result.update(referenced_defs(child))
    elif isinstance(value,list):
        for child in value:
            result.update(referenced_defs(child))
    return result


def build_candidate():
    plan = rd(PLAN)
    step = plan['steps'][8]
    spec = rd(SPEC)
    proto = rd(PROTO)['$defs']
    defs = rd(PACK)['$defs']
    c = proto['trust_context']
    a = defs['acceptance_record']
    ce8 = rd(CE08)
    shared = sorted(k for k in c['properties'] if k in a['properties'] and c['properties'][k] == a['properties'][k])
    common_defs = set()
    pending = referenced_defs([c['properties'][k] for k in shared])
    while pending:
        name = pending.pop()
        if name in common_defs:
            continue
        assert proto[name] == defs[name], name
        common_defs.add(name)
        pending.update(referenced_defs(proto[name])-common_defs)
    paths = {PLAN,SPEC,PACK,PROTO,PROFILE,CE08,PRIOR_RECON,PRIOR_REVIEW}
    paths.update(v['path'] for v in plan['bindings'].values())
    paths.update(s['candidate_dossier_path'] for s in plan['steps'][2:8])
    evidence_fields = [k for k in a['required'] if k.endswith('_evidence')]
    predicate_specs = [
        ('PJ01','CE09','Canonical humans, appointments, S01/source-author/root-key and additional R08 separation; purpose-restricted genuine keys.'),
        ('PJ02','CE09','All preparers match actor_registry preparation actor_id/record_id and SHA256(JCS(complete preparation record)), with actual author contribution evidence and exact profile/schema.'),
        ('PJ03','CE09','C requester equals caller accountable_requester_actor_id; software principal, domain, constructor and platform linkage genuine and consistent.'),
        ('PJ04','CE09','Exact image source mapping and complete runtime identity match C proposal_scope and profile; image digest does not replace runtime digest.'),
        ('PJ05','CE09','Accepted prior basis/index/resource/suite bodies and competent acceptances cover the same final scope; no future E06/root/bundle substitutes.'),
        ('PJ06','CE09','All antecedent/acceptance epochs equal C epoch; C validity contained in every relevant current antecedent/acceptance interval.'),
        ('PJ07','CE09','Platform UTC error <= C.clock_error_seconds <=5, lifetime<=3600, trusted_now-error>=not_before and trusted_now+error<expires_at; no invented trusted clock.'),
        ('PJ08','CE09','Exact C schema/repository_id/root_path/offline_key_status constants and closed unchanged C; no bundle hash or new field.'),
        ('PJ09','CE09','trust_context_sha256 = SHA256(JCS(the exact genuine complete C)); all four record hashes and cross-record identity/domain/resource links agree.'),
        ('PJ10','CE09','Acceptance decision is custody-only; five actual prior basis/resource/R01/R02/R08 evidence references have genuine available complete bodies.'),
        ('PJ11','CE10','Acceptance has no standalone signature. Three purpose/role-domain approvals cover the same actual signed_core in bundle; external anchors selected independently, not keys borrowed from C/bundle.'),
        ('PJ12','CE10','Final bundle validity also contains exact C validity and its record_hashes/acceptance project that C; no actual CE10 bundle required as sole prior CE09 authentication.')]
    return dict(schema='d5.i215-ce09-exact-C-projection-candidate.v1',increment='I215',date='2026-11-17',
        timezone='Europe/Madrid',base_commit=BASE,proposal_id=ce8['proposal_id'],profile_id=ce8['profile_id'],step='CE09',
        kind='MISSING_EXACT_C_AND_ACCEPTANCE_DOCUMENTARY_DOSSIER_NOT_POSITIVE_RECORD_OR_WIRE_C',
        status='CE09_DOCUMENTARY_PROJECTION_PREPARED_C_ACCEPTANCE_MISSING_NOT_ACCEPTED_NOT_ADMITTED',
        input_pins=historical_pins(),plan_binding=pin(PLAN,'/steps/8'),
        required_evidence=step['required_evidence'],planned_acceptance_checks=step['acceptance_checks'],
        contract_rules=step['contract_rules'],authorization_boundary=step['authorization_boundary'],
        needs_fresh_snapshot_at_launch=step['needs_fresh_snapshot_at_launch'],
        contract_rule_requirements=[dict(id=r['id'],rule=r['rule'],source=pin(SPEC,'/rules/'+str(i))) for i,r in enumerate(spec['rules']) if r['id'] in step['contract_rules']],
        dependency_gate=dict(step='CE08',latest_candidate=pin(CE08),latest_documentary_review=pin(PRIOR_REVIEW),
            documentary_baseline_confirmed=True,actual_four_antecedent_records_frozen=False,
            competent_CE08_acceptance=False,actual_dependency_satisfied=False),
        documentary_inventory=[pin(p) for p in sorted(paths)],
        producer=dict(identity='Same Codex assistant/chat as prior candidates',documentary_preparer_only=True,
            actor_independent=False,organizationally_independent=False,competent_acceptance=False,external_contacts_made=False),
        role_scope_matrix=[{**{k:v for k,v in row.items() if k != 'CE08_responsibility'},
            'CE09_responsibility':'Review exact accepted C/record projections within genuine appointed competence; R08 acceptance stays separate.'}
            for row in ce8['role_scope_matrix']],
        shared_type_projection=[dict(field=k,C_schema_source=pin(PROTO,'/$defs/trust_context/properties/'+k),
            acceptance_schema_source=pin(PACK,'/$defs/acceptance_record/properties/'+k),shared_schema_fragment=c['properties'][k],
            comparison='TYPE_IDENTICAL_C_INTERVAL_CONTAINED_IN_ACCEPTANCE_INTERVAL' if k == 'validity' else 'TYPE_IDENTICAL_EXACT_ACCEPTED_VALUE_PROJECTION',
            actual_C_value=None,actual_acceptance_value=None,actual_source_evidence=None,verified=False) for k in shared],
        shared_transitive_definition_closure=[dict(name=n,C_source=pin(PROTO,'/$defs/'+n),acceptance_source=pin(PACK,'/$defs/'+n),schema_fragment=proto[n]) for n in sorted(common_defs)],
        schema_obligations=dict(C_schema_source=pin(PROTO,'/$defs/trust_context'),C_schema_fragment=c,
            acceptance_schema_source=pin(PACK,'/$defs/acceptance_record'),acceptance_schema_fragment=a,
            C_field_slots=[dict(field=k,actual_value=None) for k in c['required']],
            acceptance_field_slots=[dict(field=k,actual_value=None) for k in a['required']],
            C_constants={k:v['const'] for k,v in c['properties'].items() if 'const' in v},
            acceptance_decision_constant=a['properties']['decision']['const'],
            C_candidate_body_cap_bytes=8192,acceptance_candidate_body_cap_bytes=spec['record_caps_bytes']['acceptance_record'],
            caps_not_active_quotas_or_heap_CPU_proof=True,no_extra_bundle_hash_or_C_field=True,
            no_positive_C_or_acceptance_instantiated=True,actual_canonical_codec_schema_crypto_validation='NOT_RUN_NO_ACTUAL_BODIES'),
        projection_predicates=[dict(id=i,consumer_step=phase,requirement=text,actual_evidence=None,
            actual_provider=None,actual_reviewer=None,actual_acceptance=None,status='MISSING_NOT_EVALUATED',verified=False)
            for i,phase,text in predicate_specs],
        prior_acceptance_evidence_inventory=[dict(field=k,source=pin(PACK,'/$defs/acceptance_record/properties/'+k),
            actual_record_id=None,actual_proof_body=None,actual_body_sha256=None,actual_body_bytes=None,
            actual_provider=None,actual_custody=None,actual_acceptance=None,accepted=False) for k in evidence_fields],
        actual_projection_state=dict(actual_C_body=None,actual_C_canonical_bytes=None,actual_C_sha256=None,actual_C_bytes=None,
            actual_acceptance_body=None,actual_acceptance_canonical_bytes=None,actual_acceptance_sha256=None,actual_acceptance_bytes=None,
            actual_four_antecedent_hashes=None,actual_epoch=None,actual_validity_intersection=None,
            actual_platform_clock_error=None,actual_C_clock_error=None,actual_trusted_now=None,
            actual_roles_preparers_keys_or_source_runtime=None,actual_prior_basis_index_resource_suite=None),
        time_and_currentness_policy=dict(profile_time_rule=rd(PROFILE)['bootstrap']['time'],
            profile_freshness_rule=rd(PROFILE)['bootstrap']['freshness'],C_validity_containment_not_forced_interval_equality=True,
            strict_not_before_lt_expires_at=True,max_validity_seconds=3600,max_clock_error_seconds=5,
            platform_error_lte_C_error_lte5=True,trusted_current_epoch_and_known_revocation_required=True,
            actual_clock_or_snapshot_selected=False,host_or_client_date_not_trusted_runtime_time=True,
            no_TOFU_stale_cache_hidden_file_or_network_lookup=True,no_instantaneous_revocation_claim=True),
        signature_and_order_policy=dict(acceptance_has_standalone_signature=False,
            K12_signs_exact_digest_means_CE10_bundle_coverage_not_new_record_signature=True,
            CE10_bundle_covers_actual_acceptance_and_C_in_signed_core=True,
            prior_authentication_and_resource_acceptance_required_without_forecast_bundle=True,
            K11_approval_domains=spec['custody_approval_domains'],
            independent_selected_custody_contract=pin(SPEC),independent_selected_custody_schema_pack=pin(PACK),
            no_C_or_bundle_key_automatically_trusted_as_anchor=True,
            actual_signatures_keys_anchors_or_approvals_created=False),
        phase_boundary=dict(CE09_actual_C_and_acceptance_still_missing=True,CE10_bundle_mapping_approvals_deferred=True,
            CE11_no_CE12_receipt_dependency=True,CE12_separate_authorization_full_admission_actual_claim_before_receipt=True,
            no_future_E06_bundle_final_root_receipt_as_sole_prior_acceptance_basis=True,
            external_prerequisites_for_receipt=plan['closure_boundaries']['external_prerequisites_for_receipt'],
            C_wire_Q_runtime_request_root_bundle_mapping_claim_receipt_issued=False,
            active_capture_inputs_or_authority_rebind=False),
        invalidation_policy=dict(new_contributor_source_image_runtime_domain_resource_epoch_key_body_or_policy_requires_fresh_review=True,
            revisit_CE02_for_anchor_key_and_CE03_to_CE10_as_affected_then_CE11=True,
            no_automatic_prior_hash_proof_acceptance_transfer=True,actual_downstream_hashes_recalculated_or_rebound=False),
        inherited_scope_boundaries=ce8['inherited_scope_boundaries'],preserved_negative_gates=ce8['preserved_negative_gates'],
        permission_boundary={**ce8['permission_boundary'],'authorized_documentary_actions':['READ_SOURCE_JSON_GIT_HASHES',
            'PREPARE_CE09_NEGATIVE_EXACT_C_PROJECTION_DOSSIER','RUN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT']},
        historical_replay_policy=dict(CE09_absent_at_BASE=True,exact_Path_exists_query_only_during_predecessor_replay=True,
            restoration_after_success_and_exception_required=True,prior_publication_mains_run=False,CE10_to_CE12_dossiers_absent=True),
        current_effect=dict(CE09_documentary_prepared=True,CE09_accepted=False,actual_dependency_satisfied=False,
            actual_C_created=False,actual_C_emitted=False,actual_acceptance_record_created=False,
            actual_projection_verified=False,actual_canonical_digest_verified=False,actual_prior_evidence_accepted=0,
            independent_acceptance=False,resource_obligations_closed=0,product_or_components_executed=False,
            quotas_changed=False,reserves_changed=False,rebind_applied=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),
        decision=plan['decision'],E06=plan['E06'])


def validate(d):
    assert d['current_effect']['actual_C_created'] is False, 'positive_C_fabricated'
    assert d['current_effect']['actual_acceptance_record_created'] is False, 'positive_acceptance_fabricated'
    assert d['signature_and_order_policy']['acceptance_has_standalone_signature'] is False, 'standalone_acceptance_signature'
    assert d['schema_obligations']['no_extra_bundle_hash_or_C_field'] is True, 'extra_C_bundle_hash'
    assert d['time_and_currentness_policy']['C_validity_containment_not_forced_interval_equality'] is True, 'interval_equality_substitution'
    assert d['time_and_currentness_policy']['platform_error_lte_C_error_lte5'] is True, 'nonconservative_clock_error'
    assert d['signature_and_order_policy']['prior_authentication_and_resource_acceptance_required_without_forecast_bundle'] is True, 'future_bundle_bootstrap'
    assert d['phase_boundary']['no_future_E06_bundle_final_root_receipt_as_sole_prior_acceptance_basis'] is True, 'future_E06_root_bootstrap'
    assert d['schema_obligations']['caps_not_active_quotas_or_heap_CPU_proof'] is True, 'caps_as_resource_proof'
    assert d['current_effect']['resource_obligations_closed'] == 0, 'document_closes_resources'
    assert d['phase_boundary']['C_wire_Q_runtime_request_root_bundle_mapping_claim_receipt_issued'] is False, 'wire_or_root_issuance'
    assert d['phase_boundary']['active_capture_inputs_or_authority_rebind'] is False, 'active_rebind'
    assert len(d['shared_type_projection']) == 14 and len({r['field'] for r in d['shared_type_projection']}) == 14
    assert len(d['schema_obligations']['C_field_slots']) == 19
    assert len(d['schema_obligations']['acceptance_field_slots']) == 27
    assert len(d['prior_acceptance_evidence_inventory']) == 5
    assert len(d['projection_predicates']) == 12
    for row in d['shared_type_projection']:
        assert row['actual_C_value'] is None and row['actual_acceptance_value'] is None and row['actual_source_evidence'] is None
        assert row['verified'] is False
    assert all(value is None for value in d['actual_projection_state'].values())
    plan = rd(PLAN)
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][:9])
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][9:])
    assert d == build_candidate(), 'Dossier differs from source reconstruction'


def rejection_checks(d):
    cases = [
        ('positive_C_fabricated',('current_effect','actual_C_created'),True),
        ('positive_acceptance_fabricated',('current_effect','actual_acceptance_record_created'),True),
        ('standalone_acceptance_signature',('signature_and_order_policy','acceptance_has_standalone_signature'),True),
        ('extra_C_bundle_hash',('schema_obligations','no_extra_bundle_hash_or_C_field'),False),
        ('interval_equality_substitution',('time_and_currentness_policy','C_validity_containment_not_forced_interval_equality'),False),
        ('nonconservative_clock_error',('time_and_currentness_policy','platform_error_lte_C_error_lte5'),False),
        ('future_bundle_bootstrap',('signature_and_order_policy','prior_authentication_and_resource_acceptance_required_without_forecast_bundle'),False),
        ('future_E06_root_bootstrap',('phase_boundary','no_future_E06_bundle_final_root_receipt_as_sole_prior_acceptance_basis'),False),
        ('caps_as_resource_proof',('schema_obligations','caps_not_active_quotas_or_heap_CPU_proof'),False),
        ('document_closes_resources',('current_effect','resource_obligations_closed'),1),
        ('wire_or_root_issuance',('phase_boundary','C_wire_Q_runtime_request_root_bundle_mapping_claim_receipt_issued'),True),
        ('active_rebind',('phase_boundary','active_capture_inputs_or_authority_rebind'),True)]
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
    with predecessor_CE09_presence_as_of_base():
        rec = previous['reconstruct']()
        assert rec == rd(PRIOR_RECON) and previous['build_review'](rec) == rd(PRIOR_REVIEW)
    assert Path.exists is original and (ROOT/DOS).exists()
    class DocumentaryProbe(Exception):
        pass
    try:
        with predecessor_CE09_presence_as_of_base():
            assert not (ROOT/DOS).exists()
            raise DocumentaryProbe()
    except DocumentaryProbe:
        pass
    assert Path.exists is original and (ROOT/DOS).exists()
    plan = rd(PLAN)
    graph = {s['id']:s['depends_on'] for s in plan['steps']}
    closure = previous['ancestors'](graph)
    assert closure['CE09'] == {'CE%02d'%i for i in range(1,9)}
    assert not {'CE10','CE11','CE12'} & closure['CE09'] and 'CE12' not in closure['CE11']
    assert [r['id'] for r in d['contract_rule_requirements']] == plan['steps'][8]['contract_rules']
    assert [r['consumer_step'] for r in d['projection_predicates']] == ['CE09']*10+['CE10']*2
    for row in d['projection_predicates']:
        assert all(row[k] is None for k in ['actual_evidence','actual_provider','actual_reviewer','actual_acceptance'])
        assert row['verified'] is False and row['status'] == 'MISSING_NOT_EVALUATED'
    for row in d['prior_acceptance_evidence_inventory']:
        assert all(value is None for key,value in row.items() if key.startswith('actual_'))
        assert row['accepted'] is False
    assert [r['id'] for r in d['role_scope_matrix']] == plan['steps'][8]['provenance_and_role']['primary_review_roles']
    for row in d['role_scope_matrix']:
        assert row['assigned_person'] is None and row['accepted_appointment'] is False and row['current_actions_authorized'] == []
    for key,value in d['current_effect'].items():
        if key == 'CE09_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_prior_evidence_accepted','resource_obligations_closed']:
            assert value == 0 and type(value) is int
        else:
            assert value is False, key
    assert d['schema_obligations']['C_candidate_body_cap_bytes'] == rd(PROFILE)['bootstrap']['context_limits']['serialized_bytes'] == 8192
    assert d['schema_obligations']['acceptance_candidate_body_cap_bytes'] == rd(SPEC)['record_caps_bytes']['acceptance_record'] == 16384
    C = rd(PROTO)['$defs']['trust_context']
    A = rd(PACK)['$defs']['acceptance_record']
    assert C['additionalProperties'] is A['additionalProperties'] is False
    assert 'signature_hex' not in A['properties'] and 'signature' not in A['properties']
    assert 'bundle_sha256' not in C['properties'] and C['properties']['schema'] != A['properties']['schema']
    return dict(schema='d5.i215-preparation-review.v1',increment='I215',date='2026-11-17',base_commit=BASE,
        status=STATUS,candidate=pin(DOS),plan=pin(PLAN,'/steps/8'),
        counts=dict(input_pins=872,shared_type_fields=14,shared_transitive_definitions=len(d['shared_transitive_definition_closure']),
            C_top_level_fields=19,acceptance_top_level_fields=27,prior_acceptance_evidence_slots=5,
            CE09_predicates=10,deferred_CE10_predicates=2,unassigned_role_slots=5,later_dossiers_absent=3,resource_obligations_closed=0),
        provenance=d['producer'],source_reconstruction=dict(prior_I214_reconstruction_and_review_reproduced=True,
            prior_publication_mains_run=False,exact_CE09_historical_absence_guard=True,
            guard_restored_success_and_exception=True,no_reverse_future_bundle_root_receipt_dependency=True,
            shared_types_and_transitive_definitions_equal=True,validity_is_containment_not_forced_interval_equality=True,
            standalone_signature_not_added=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],decision=d['decision'],E06=d['E06'],
        limitations=['Negative dossier only: no actual C/acceptance, final antecedent record freeze, competent dependency acceptance, genuine prior proof bodies, actors/keys, clock or validity.',
            'Same assistant is not competent independent review or separate R08 acceptance. No actual canonical positive body/digest/schema/crypto verification, wire emission, request, bundle or final root.',
            'Type equality is static schema evidence, not equality or acceptance of unknown actual values. C validity must be contained; acceptance is custody-only and has no standalone signature.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I215-audit.py',expected_result=STATUS,
            runtime_harness='N/A: documentary JSON/Git/hash/schema-fragment/type/phase checks; no product/components or positive codec/crypto execution.',
            over400_lines=True,reason='One negative exact-C projection dossier with shared types, prior-evidence/predicate matrix and immutable preservation; overage reported. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_is_not_C_issuance_acceptance_or_admission=True))


def main():
    review = build_review()
    assert rd(PREP) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published559'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 564
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i215-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published564'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():
            assert sha(p) == h, p
    assert seal['source_only'] and seal['current_effect'] == review['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I215',historical_pins=872,preserved_published_files=564,
        new_files=5,documentary_rejections=12,current_effect=review['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
