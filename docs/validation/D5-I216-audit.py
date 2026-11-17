#!/usr/bin/env python3
"""I216 static CE09 projection review; never execute product or positive protocol codecs."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'b098d19c639e39be6e2ccacde1227cd405bfd311'
DOS = P+'D5-I193-CE09-EXACT-C-PROJECTION-CANDIDATE.json'
PLAN = P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
PROTO = P+'D5-I185-PGO181-SCHEMAS-CANDIDATE-02.json'
PROFILE = P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
CE08 = P+'D5-I193-CE08-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json'
PRIOR_AUDIT = P+'D5-I215-audit.py'
PRIOR_PREP = P+'D5-I215-preparation-review.json'
PRIOR_SEAL = P+'D5-I215-integrity.json'
PRIOR_DOC = 'docs/design/D5-I215-CE09-EXACT-C-PROJECTION.md'
PRIOR_FILES = {DOS,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I216-I215-source-reconstruction.json'
REVIEW = P+'D5-I216-I215-documentary-review.json'
AUDIT = P+'D5-I216-audit.py'
SEAL = P+'D5-I216-integrity.json'
DOC = 'docs/design/D5-I216-I215-CE09-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_C_AND_ACCEPTANCE_MISSING'


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


def references(value):
    found = set()
    pending = [value]
    while pending:
        current = pending.pop()
        if isinstance(current,dict):
            if '$ref' in current:
                assert current['$ref'].startswith('#/$defs/')
                found.add(current['$ref'][8:])
            pending.extend(current.values())
        elif isinstance(current,list):
            pending.extend(current)
    return found


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


def reconstruct():
    d = rd(DOS)
    plan = rd(PLAN)
    step = plan['steps'][8]
    spec = rd(SPEC)
    proto = rd(PROTO)['$defs']
    defs = rd(PACK)['$defs']
    C = proto['trust_context']
    A = defs['acceptance_record']
    pins = {**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 877
    verify_blobs(pins)
    assert step['id'] == d['step'] == 'CE09' and step['candidate_dossier_path'] == DOS
    assert d['plan_binding'] == pin(PLAN,'/steps/8')
    for a,b in [('required_evidence','required_evidence'),('planned_acceptance_checks','acceptance_checks'),
                ('contract_rules','contract_rules'),('authorization_boundary','authorization_boundary'),
                ('needs_fresh_snapshot_at_launch','needs_fresh_snapshot_at_launch')]:
        assert d[a] == step[b]
    assert len(d['required_evidence']) == len(d['planned_acceptance_checks']) == 3
    assert step['record_families'] == ['acceptance_record'] and step['depends_on'] == ['CE08']
    assert len(d['documentary_inventory']) == len({s['path'] for s in d['documentary_inventory']}) == 17
    for source in d['documentary_inventory']:
        assert pins[source['path']] == source['sha256'] == sha(source['path'])
    dep = d['dependency_gate']
    assert dep['latest_candidate'] == pin(CE08) and fragment(dep['latest_documentary_review'])['current_effect']['CE08_accepted'] is False
    assert dep['documentary_baseline_confirmed'] is True
    assert all(dep[k] is False for k in ['actual_four_antecedent_records_frozen','competent_CE08_acceptance','actual_dependency_satisfied'])
    common_names = set(C['properties']) & set(A['properties'])
    assert len(common_names) == 15 and C['properties']['schema'] != A['properties']['schema']
    equal_names = sorted(n for n in common_names if C['properties'][n] == A['properties'][n])
    assert len(equal_names) == 14 and set(equal_names) == common_names-{'schema'}
    assert [r['field'] for r in d['shared_type_projection']] == equal_names
    matrix = []
    for row in d['shared_type_projection']:
        name = row['field']
        assert fragment(row['C_schema_source']) == fragment(row['acceptance_schema_source']) == row['shared_schema_fragment']
        assert row['shared_schema_fragment'] == C['properties'][name] == A['properties'][name]
        expected = 'TYPE_IDENTICAL_C_INTERVAL_CONTAINED_IN_ACCEPTANCE_INTERVAL' if name == 'validity' else 'TYPE_IDENTICAL_EXACT_ACCEPTED_VALUE_PROJECTION'
        assert row['comparison'] == expected
        assert all(row[k] is None for k in ['actual_C_value','actual_acceptance_value','actual_source_evidence']) and not row['verified']
        matrix.append(dict(field=name,C_source=row['C_schema_source'],acceptance_source=row['acceptance_schema_source'],
            same_type=True,value_relation=expected,actual_value_projection_verified=False))
    ref_closure = set()
    queue = sorted(references([C['properties'][n] for n in equal_names]))
    while queue:
        name = queue.pop(0)
        if name in ref_closure:
            continue
        assert proto[name] == defs[name], name
        ref_closure.add(name)
        queue.extend(sorted(references(proto[name])-ref_closure))
    assert len(ref_closure) == 6
    assert [r['name'] for r in d['shared_transitive_definition_closure']] == sorted(ref_closure)
    for row in d['shared_transitive_definition_closure']:
        assert fragment(row['C_source']) == fragment(row['acceptance_source']) == row['schema_fragment'] == proto[row['name']]
    schemas = d['schema_obligations']
    assert fragment(schemas['C_schema_source']) == schemas['C_schema_fragment'] == C
    assert fragment(schemas['acceptance_schema_source']) == schemas['acceptance_schema_fragment'] == A
    assert C['additionalProperties'] is False and A['additionalProperties'] is False
    assert len(C['required']) == len(C['properties']) == len(schemas['C_field_slots']) == 19
    assert len(A['required']) == len(A['properties']) == len(schemas['acceptance_field_slots']) == 27
    for schema,slots in [(C,schemas['C_field_slots']),(A,schemas['acceptance_field_slots'])]:
        assert [r['field'] for r in slots] == schema['required'] and all(r['actual_value'] is None for r in slots)
    constants = {k:v['const'] for k,v in C['properties'].items() if 'const' in v}
    assert schemas['C_constants'] == constants and len(constants) == 4
    assert constants['schema'] == 'd5.prp181-trust-context.v3'
    assert constants['repository_id'] == 'github.com/isidorotrevino/weekly-ai-work-planner'
    assert constants['root_path'] == 'docs/validation/D5-PRP181-FINAL-ADMISSION-ROOT.json'
    assert constants['offline_key_status'] == 'BOTH_KEYS_APPROVED_NOT_REVOKED_AT_CONTEXT_ISSUANCE'
    assert schemas['acceptance_decision_constant'] == A['properties']['decision']['const'] == 'IDENTITY_IMAGE_CUSTODY_ONLY_NOT_RESOURCE_OR_CAPTURE_ADMISSION'
    assert not {'signature','signature_hex'} & set(A['properties']) and 'bundle_sha256' not in C['properties']
    ctx = rd(PROFILE)['bootstrap']['context_limits']
    assert schemas['C_candidate_body_cap_bytes'] == ctx['serialized_bytes'] == 8192
    assert schemas['acceptance_candidate_body_cap_bytes'] == spec['record_caps_bytes']['acceptance_record'] == 16384
    for k in ['caps_not_active_quotas_or_heap_CPU_proof','no_extra_bundle_hash_or_C_field','no_positive_C_or_acceptance_instantiated']:
        assert schemas[k] is True
    assert schemas['actual_canonical_codec_schema_crypto_validation'] == 'NOT_RUN_NO_ACTUAL_BODIES'
    evidence_fields = [n for n in A['required'] if n.endswith('_evidence')]
    assert len(evidence_fields) == 5 and [r['field'] for r in d['prior_acceptance_evidence_inventory']] == evidence_fields
    for row in d['prior_acceptance_evidence_inventory']:
        assert fragment(row['source']) == A['properties'][row['field']] == {'$ref':'#/$defs/evidence_reference'}
        assert all(value is None for key,value in row.items() if key.startswith('actual_')) and row['accepted'] is False
    predicates = d['projection_predicates']
    assert [r['id'] for r in predicates] == ['PJ%02d'%i for i in range(1,13)]
    assert [r['consumer_step'] for r in predicates] == ['CE09']*10+['CE10']*2
    for row in predicates:
        assert all(row[k] is None for k in ['actual_evidence','actual_provider','actual_reviewer','actual_acceptance'])
        assert row['status'] == 'MISSING_NOT_EVALUATED' and row['verified'] is False
    time = d['time_and_currentness_policy']
    assert time['profile_time_rule'] == rd(PROFILE)['bootstrap']['time']
    assert time['profile_freshness_rule'] == rd(PROFILE)['bootstrap']['freshness']
    assert time['max_validity_seconds'] == ctx['max_validity_seconds'] == 3600
    assert time['max_clock_error_seconds'] == ctx['max_clock_error_seconds'] == C['properties']['clock_error_seconds']['maximum'] == 5
    for k in ['C_validity_containment_not_forced_interval_equality','strict_not_before_lt_expires_at',
              'platform_error_lte_C_error_lte5','trusted_current_epoch_and_known_revocation_required',
              'host_or_client_date_not_trusted_runtime_time','no_TOFU_stale_cache_hidden_file_or_network_lookup','no_instantaneous_revocation_claim']:
        assert time[k] is True
    assert time['actual_clock_or_snapshot_selected'] is False
    assert all(value is None for value in d['actual_projection_state'].values())
    sig = d['signature_and_order_policy']
    assert sig['acceptance_has_standalone_signature'] is False
    assert sig['K12_signs_exact_digest_means_CE10_bundle_coverage_not_new_record_signature']
    assert sig['CE10_bundle_covers_actual_acceptance_and_C_in_signed_core']
    assert sig['prior_authentication_and_resource_acceptance_required_without_forecast_bundle']
    assert sig['no_C_or_bundle_key_automatically_trusted_as_anchor']
    assert sig['actual_signatures_keys_anchors_or_approvals_created'] is False
    assert sig['K11_approval_domains'] == spec['custody_approval_domains']
    assert sig['independent_selected_custody_contract'] == pin(SPEC) and sig['independent_selected_custody_schema_pack'] == pin(PACK)
    core = defs['custody_signed_core']
    bundle = defs['custody_bundle']
    record_names = ['actor_registry','image_manifest','caller_identity','platform_custody','acceptance_record']
    assert core['properties']['records']['required'] == core['properties']['record_hashes']['required'] == record_names
    assert len(core['required']) == len(core['properties']) == 8 and core['additionalProperties'] is False
    assert bundle['required'] == ['schema','signed_core','approvals'] and bundle['additionalProperties'] is False
    assert 'validity' not in bundle['properties'] and 'trust_context' not in core['properties'] and 'C' not in core['properties']
    assert A['properties']['trust_context_sha256'] == {'$ref':'#/$defs/sha256'}
    assert core['properties']['records']['properties']['acceptance_record'] == {'$ref':'#/$defs/acceptance_record'}
    assert bundle['properties']['approvals']['required'] == list(spec['custody_approval_domains'])
    assert all('validity' in defs[n]['required'] for n in record_names)
    graph = {s['id']:s['depends_on'] for s in plan['steps']}
    closure = ancestors(graph)
    order = ancestors(spec['record_order'])
    assert closure['CE09'] == {'CE%02d'%i for i in range(1,9)} and not {'CE10','CE11','CE12'} & closure['CE09']
    assert 'C_CONTEXT' in order['ACCEPTANCE'] and 'BUNDLE' not in order['ACCEPTANCE']
    assert 'ACCEPTANCE' in order['BUNDLE'] and 'CE12' not in closure['CE11']
    phases = d['phase_boundary']
    for k in ['CE09_actual_C_and_acceptance_still_missing','CE10_bundle_mapping_approvals_deferred',
              'CE11_no_CE12_receipt_dependency','CE12_separate_authorization_full_admission_actual_claim_before_receipt',
              'no_future_E06_bundle_final_root_receipt_as_sole_prior_acceptance_basis']:
        assert phases[k] is True
    assert not phases['C_wire_Q_runtime_request_root_bundle_mapping_claim_receipt_issued'] and not phases['active_capture_inputs_or_authority_rebind']
    assert phases['external_prerequisites_for_receipt'] == plan['closure_boundaries']['external_prerequisites_for_receipt']
    ce8 = rd(CE08)
    assert d['inherited_scope_boundaries'] == ce8['inherited_scope_boundaries']
    assert d['preserved_negative_gates'] == ce8['preserved_negative_gates']
    assert len(d['inherited_scope_boundaries']['S01_exclusions']) == 8
    assert d['permission_boundary']['denied_action_classes'] == ce8['permission_boundary']['denied_action_classes']
    assert [r['id'] for r in d['role_scope_matrix']] == step['provenance_and_role']['primary_review_roles'] == ['R01','R02','R03','R06','R08']
    for row in d['role_scope_matrix']:
        assert row['assigned_person'] is None and row['accepted_appointment'] is False and row['current_actions_authorized'] == []
    assert d['invalidation_policy']['no_automatic_prior_hash_proof_acceptance_transfer']
    assert d['invalidation_policy']['new_contributor_source_image_runtime_domain_resource_epoch_key_body_or_policy_requires_fresh_review']
    assert d['invalidation_policy']['revisit_CE02_for_anchor_key_and_CE03_to_CE10_as_affected_then_CE11']
    assert not d['invalidation_policy']['actual_downstream_hashes_recalculated_or_rebound']
    for gate in d['preserved_negative_gates']:
        assert fragment({**gate['source'],'json_pointer':gate['json_pointer']}) == gate['observed_value']
    for key,value in d['current_effect'].items():
        if key == 'CE09_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_prior_evidence_accepted','resource_obligations_closed']:
            assert value == 0 and type(value) is int
        else:
            assert value is False, key
    assert d['decision'] == plan['decision'] and d['E06'] == plan['E06']
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][:9])
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][9:])
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    assert previous['build_review']() == rd(PRIOR_PREP)
    original = Path.exists
    assert git('ls-tree','--name-only',previous['BASE'],'--',DOS) == ''
    assert git('ls-tree','--name-only',BASE,'--',DOS) == DOS
    with previous['predecessor_CE09_presence_as_of_base']():
        assert not (ROOT/DOS).exists()
    assert Path.exists is original and (ROOT/DOS).exists()
    class DocumentaryProbe(Exception):
        pass
    try:
        with previous['predecessor_CE09_presence_as_of_base']():
            raise DocumentaryProbe()
    except DocumentaryProbe:
        pass
    assert Path.exists is original and (ROOT/DOS).exists()
    sections = {
        'K08':['shared_type_projection','schema_obligations','projection_predicates','time_and_currentness_policy'],
        'K10':['role_scope_matrix','inherited_scope_boundaries','projection_predicates'],
        'K11':['signature_and_order_policy','projection_predicates'],
        'K12':['phase_boundary','signature_and_order_policy'],
        'K13':['time_and_currentness_policy'],
        'K16':['schema_obligations','permission_boundary','current_effect']}
    assert [r['id'] for r in d['contract_rule_requirements']] == list(sections) == step['contract_rules']
    rules = []
    for row in d['contract_rule_requirements']:
        assert fragment(row['source']) == dict(id=row['id'],rule=row['rule'])
        rules.append(dict(id=row['id'],source=row['source'],candidate_sections=[pin(DOS,'/'+s) for s in sections[row['id']]],
            documentary_requirement_preserved=True,actual_competent_acceptance=False))
    return dict(schema='d5.i216-i215-source-reconstruction.v1',increment='I216',date='2026-11-17',base_commit=BASE,
        input_pins=pins,method='Fixed Git blobs and fresh direct C/acceptance type/reference closure, constants, field/cap, validity, signed-core coverage and antecedent reconstruction. I215 documentary build reproduced without prior publication mains.',
        shared_type_review=matrix,shared_definition_names=sorted(ref_closure),rule_review=rules,
        shape_review=dict(C_top_level_fields=19,acceptance_top_level_fields=27,common_property_names=15,
            type_identical_fields=14,schema_constant_excluded=True,exact_value_projection_fields=13,validity_interval_containment_fields=1,
            evidence_reference_fields=evidence_fields,C_constants=constants,C_candidate_cap_bytes=8192,acceptance_candidate_cap_bytes=16384,
            no_positive_body_or_actual_field_values=True),
        coverage_interpretation=dict(acceptance_signature_field_absent=True,
            C_bound_indirectly_by_acceptance_trust_context_sha256=True,no_C_body_field_added_to_core_or_bundle=True,
            signed_core_records=record_names,bundle_top_level_fields=bundle['required'],
            effective_bundle_validity_from_five_record_intervals_not_new_bundle_field=True,
            CE10_approval_domains=spec['custody_approval_domains'],actual_signature_or_crypto_verification=False),
        phase_review=dict(step_graph=graph,CE09_ancestors=sorted(closure['CE09']),no_reverse_bundle_root_receipt_dependency=True,
            CE09_predicates=[r['id'] for r in predicates[:10]],deferred_CE10_predicates=[r['id'] for r in predicates[10:]],
            CE11_not_dependent_on_CE12=True,CE12_actual_claim_before_receipt_after_separate_authorization=True),
        preservation=dict(documentary_inventory=17,unassigned_review_slots=5,unaccepted_CE08_dependency=True,
            later_dossiers_absent=3,eight_S01_exclusions_unchanged=True,I215_documentary_build_and_twelve_rejections_reproduced=True,
            historical_CE09_absence_and_current_presence_verified=True,guard_restored_after_success_and_exception=True,
            prior_publication_mains_run=False),
        verdict=dict(new_blocking_documentary_findings=0,CE09_documentary_baseline_confirmed=True,CE09_accepted=False,
            actual_C_created=False,actual_C_emitted=False,actual_acceptance_record_created=False,actual_projection_verified=False,
            actual_prior_evidence_accepted=0,independent_acceptance=False,resource_obligations_closed=0,product_or_components_executed=0))


def build_review(rec):
    d = rd(DOS)
    checks = [
        ('E01','Exact unchanged roles/preparers/source/runtime/prior-scope projection','14_TYPES_AND_6_TRANSITIVE_DEFINITIONS_PRESERVED_VALUES_MISSING'),
        ('E02','Canonical C digest/constants/conservative clock/contained current validity','NO_ACTUAL_DIGEST_CLOCK_OR_INTERVAL_VERIFIED'),
        ('E03','Custody-only acceptance and five actual prior evidence references','REQUIREMENTS_PRESERVED_BODIES_AND_COMPETENT_DECISIONS_MISSING'),
        ('A01','14 types plus digest/constant/time/clock/cross-record predicates and no extra C bundle hash','PRESERVED_CLOSED_SCHEMAS_NO_POSITIVE_INSTANCE'),
        ('A02','No future bundle/root/E06 authentication or standalone acceptance signature','INDIRECT_C_DIGEST_COVERAGE_DEFERRED_TO_CE10'),
        ('A03','No C wire/root/request emission pending genuine facts/review','DOCUMENTARY_NEGATIVE_DOSSIER_ONLY')]
    return dict(schema='d5.i216-i215-documentary-review.v1',increment='I216',date='2026-11-17',timezone='Europe/Madrid',
        base_commit=BASE,proposal_id=d['proposal_id'],profile_id=d['profile_id'],step='CE09',
        status='CE09_DOCUMENTARY_BASELINE_CONFIRMED_C_ACCEPTANCE_MISSING_NOT_ACCEPTED_NOT_ADMITTED',
        candidate=pin(DOS),reconstruction=pin(RECON),findings=[],
        checks=[dict(id=i,scope=s,result=r) for i,s,r in checks],contract_rule_review=rec['rule_review'],
        documentary_clarifications=[
            dict(id='C01',subject='Shared type versus actual value',disposition='15 property names overlap; schema differs.14 types and six transitive definitions match.13 accepted value projections remain missing; validity uses containment, not mandatory equal endpoints.'),
            dict(id='C02',subject='C coverage in signed_core',disposition='Closed signed_core embeds five records, including acceptance and its trust_context_sha256. C is bound indirectly through that exact digest; no new C body/member or standalone signature is added.'),
            dict(id='C03',subject='Bundle validity wording',disposition='Effective bundle currentness/validity derives from its five current record intervals, including acceptance; bundle has only schema/signed_core/approvals, with no standalone validity property. No new interval field is introduced.'),
            dict(id='C04',subject='K12 digest signing wording',disposition='Read with explicit I193 CE09 and closed acceptance schema: CE10 role-domain bundle approvals cover the exact C digest through acceptance. They cannot supply sole prior authentication or close missing resource evidence.')],
        provenance=dict(reviewer='Same Codex assistant/chat that prepared I215',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,competent_R01_R02_R03_R06_review=False,
            separate_R08_acceptance=False,independent_acceptance=False),
        verdict=rec['verdict'],current_effect={**d['current_effect'],'CE09_documentary_review_completed':True,
            'CE09_documentary_confirmation':True,'CE09_documentary_revision_required':False},decision=d['decision'],E06=d['E06'],
        limitations=['No actual C/acceptance, final CE08 records or competent acceptance, prior basis/resource/R01/R02/R08 evidence, real identities/keys/clock/validity or projected actual values.',
            'Static type/field/signature coverage reconstruction is not positive schema/codec/crypto validation or a genuine independent review. No resource qualification, canonical positive digest,900-second proof, wire/request/root/bundle/claim issuance.',
            'Same assistant remains outside competent independent R01/R02/R03/R06 review and separate R08 acceptance. Existing negative gates and no-admission state stay unchanged.'],
        next_scope='CE09 can serve as a documentarily reviewed missing-evidence baseline for separately requested CE10 preparation. All actual antecedents, projections, evidence and acceptances remain pending.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I216-audit.py',expected_result=STATUS,
            runtime_harness='N/A: documentary JSON/Git/hash/type/schema-fragment and antecedent review only; no product/components or positive protocol/crypto execution.',
            over400_lines=True,reason='One CE09 review with independently reconstructed type/validity/digest coverage and immutable preservation; overage reported. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_is_not_C_emission_acceptance_or_admission=True))


def main():
    rec = reconstruct()
    assert rd(RECON) == rec and rd(REVIEW) == build_review(rec)
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published564'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 569
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i216-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published569'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():
            assert sha(p) == h, p
    assert seal['source_only'] and seal['current_effect'] == rd(REVIEW)['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I216',historical_pins=877,preserved_published_files=569,
        new_files=5,original_documentary_rejections_reproduced=12,verdict=rec['verdict'],
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
