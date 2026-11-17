#!/usr/bin/env python3
"""I214 documentary review of CE08; no product/component or positive codec execution."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '2184e26e22a5ea94cf9d158f4ca9e1917745a275'
DOS = P+'D5-I193-CE08-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json'
PLAN = P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
CHECK = P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE02 = P+'D5-I201-CE02-ANCHOR-PROVENANCE-CANDIDATE-02.json'
CE07 = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
PRIOR_AUDIT = P+'D5-I213-audit.py'
PRIOR_PREP = P+'D5-I213-preparation-review.json'
PRIOR_SEAL = P+'D5-I213-integrity.json'
PRIOR_DOC = 'docs/design/D5-I213-CE08-FINAL-ANTECEDENT-FREEZE.md'
PRIOR_FILES = {DOS,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I214-I213-source-reconstruction.json'
REVIEW = P+'D5-I214-I213-documentary-review.json'
AUDIT = P+'D5-I214-audit.py'
SEAL = P+'D5-I214-integrity.json'
DOC = 'docs/design/D5-I214-I213-CE08-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
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
    active = set()
    done = {}
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
    step = plan['steps'][7]
    spec = rd(SPEC)
    defs = rd(PACK)['$defs']
    pins = {**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 867
    verify_blobs(pins)
    assert d['step'] == step['id'] == 'CE08' and step['candidate_dossier_path'] == DOS
    assert d['plan_binding'] == pin(PLAN,'/steps/7')
    for a,b in [('required_evidence','required_evidence'),('planned_acceptance_checks','acceptance_checks'),
                ('contract_rules','contract_rules'),('authorization_boundary','authorization_boundary'),
                ('needs_fresh_snapshot_at_launch','needs_fresh_snapshot_at_launch')]:
        assert d[a] == step[b]
    assert len(d['required_evidence']) == 4 and len(d['planned_acceptance_checks']) == 3
    inventory = d['documentary_inventory']
    assert len(inventory) == len({r['path'] for r in inventory}) == 24
    for source in inventory:
        assert source['sha256'] == pins[source['path']] == sha(source['path'])
    assert [r['step'] for r in d['dependency_gates']] == step['depends_on'] == ['CE02','CE03','CE04','CE05','CE06','CE07']
    for row in d['dependency_gates']:
        s = next(s for s in plan['steps'] if s['id'] == row['step'])
        expected = CE02 if row['step'] == 'CE02' else s['candidate_dossier_path']
        assert row['latest_candidate'] == pin(expected)
        assert row['historical_planned_path'] == s['candidate_dossier_path']
        review = fragment(row['latest_documentary_review'])
        assert review['current_effect']['independent_acceptance'] is False
        assert row['documentary_review_available'] is True
        assert row['competent_acceptance'] is False and row['actual_dependency_satisfied'] is False
    missing_fields = ['actual_record_id','actual_canonical_body','actual_canonical_body_sha256','actual_body_bytes',
        'actual_provider','actual_custody_locator','actual_configuration_epoch','actual_validity',
        'actual_prior_authentication','actual_complete_evidence_body_inventory','actual_reviewer','actual_acceptance']
    shape = []
    assert [r['family'] for r in d['freeze_inventory']] == step['record_families'] == FAMILIES
    for i,row in enumerate(d['freeze_inventory']):
        family = row['family']
        assert row['order'] == i+1 and fragment(row['schema_source']) == row['schema_fragment'] == defs[family]
        assert defs[family]['additionalProperties'] is False
        assert [r['field'] for r in row['field_slots']] == defs[family]['required']
        assert all(r['actual_value'] is None and r['status'] == 'MISSING_NOT_POSITIVE_RECORD' for r in row['field_slots'])
        assert all(row[k] is None for k in missing_fields)
        assert row['actual_frozen'] is False and row['accepted'] is False and row['cap_applied_as_quota'] is False
        assert row['cap_is_not_heap_CPU_or_evidence_completeness_proof'] is True
        assert row['candidate_body_cap_bytes'] == spec['record_caps_bytes'][family]
        gate = next(g for g in rd(CHECK)['family_gates'] if g['family'] == family)
        assert gate['final_record_freeze_step'] == 'CE08' and gate['accepted'] is False
        shape.append(dict(family=family,top_level_field_names=defs[family]['required'],
            top_level_field_count=len(defs[family]['required']),candidate_body_cap_bytes=row['candidate_body_cap_bytes'],
            actual_record_body_or_hash_available=False,actual_accepted_or_frozen=False))
    assert [r['top_level_field_count'] for r in shape] == [8,26,13,14]
    assert sum(r['top_level_field_count'] for r in shape) == 61
    assert len(d['schema_helpers']) == 8
    for row in d['schema_helpers']:
        assert fragment(row['source']) == row['schema_fragment'] == defs[row['name']]
    contributors = d['contributor_closure']
    for k in ['actual_complete_contributor_inventory','actual_canonical_human_alias_resolution',
              'actual_competence_and_appointment_evidence','actual_preparation_records',
              'actual_complete_anchor_key_inventory','actual_contributor_count','actual_preparer_count','actual_key_count']:
        assert contributors[k] is None
    assert fragment(contributors['provisional_CE03']) == rd(plan['steps'][2]['candidate_dossier_path'])['freeze_and_refresh']
    assert fragment(contributors['latest_CE07_documentary_review'])['current_effect']['CE07_accepted'] is False
    for k in ['source_document_hashes_not_authorship_evidence','same_chat_not_independent_acceptance',
              'actor_registry_first_after_all_actual_authors_known','CE03_provisional_not_final',
              'no_unrecorded_CE07_or_later_authors','no_forecast_person_or_synthetic_preparation_record',
              'preparation_record_must_not_pin_C_acceptance_bundle_Q_root_or_receipt',
              'canonical_alias_collisions_ambiguity_or_missing_competence_reject','software_caller_not_alternate_human_identity']:
        assert contributors[k] is True
    assert contributors['complete_scope_verified'] is False
    limits = d['typed_array_limits']
    assert limits['preparers_min'] == defs['actor_registry']['properties']['documentary_preparation_records']['minItems'] == 1
    assert limits['preparers_max'] == defs['actor_registry']['properties']['documentary_preparation_records']['maxItems'] == 16
    assert limits['actors_max'] == defs['actor_registry']['properties']['actors']['maxItems'] == 64
    assert limits['keys_max'] == defs['anchor_registry']['properties']['keys']['maxItems'] == 64
    assert limits['dependencies_max'] == defs['image_manifest']['properties']['dependencies']['maxItems'] == 128
    assert limits['actual_counts'] is None and limits['truncation_or_quota_increase_allowed'] is False
    assert limits['complete_sorted_unique_canonical_arrays_required'] and limits['typed_indices_do_not_bound_underlying_proof_costs']
    separation = d['identity_and_separation_policy']
    assert separation['R08_human_and_key_distinct_from_R01_and_R02']
    assert separation['R01_R02_same_genuinely_competent_human_allowed_with_distinct_role_domain_approvals']
    assert separation['key_binding_unique_by_purpose_and_key_id_with_one_canonical_actor']
    assert separation['all_role_preparer_requester_source_author_custody_identities_resolve_to_canonical_humans']
    assert separation['distinct_strings_or_keys_not_distinct_people']
    assert separation['actual_alias_key_identity_or_separation_verified'] is False
    assert separation['actual_CE10_approvals_or_signatures_created'] is False
    policy = d['source_runtime_policy']
    mappings = policy['source_to_image_missing_inventory']
    assert [r['logical_path'] for r in mappings] == defs['source_bindings']['required']
    assert defs['image_manifest']['properties']['source_to_image']['required'] == defs['source_bindings']['required']
    assert len(mappings) == 6
    for row in mappings:
        assert not (ROOT/row['logical_path']).exists() and row['actual_source_exists'] is False
        for k in ['actual_source_sha256','actual_image_member_id','actual_image_member_sha256','actual_representation','actual_mapping_evidence']:
            assert row[k] is None
        assert row['README_must_be_DOCUMENT'] == row['logical_path'].endswith('/README.md') and not row['accepted']
    for k in ['actual_complete_runtime_loader_stdlib_frozen_native_crypto_closure','actual_image_bytes_sha256','actual_runtime_sha256','actual_source_root_sha256']:
        assert policy[k] is None
    for k in ['image_digest_must_not_replace_runtime_identity','source_bindings_and_mapping_exact_six_actual_digests_equal',
              'historical480_or_six_sources_only_no_unbound_helpers','document_membership_not_test_runner_loaded_evidence',
              'no_image_self_manifest_bundle_future_digest_embedding']:
        assert policy[k] is True
    assert policy['actual_build_or_measurement_performed'] is False
    constants = d['policy_constant_bindings']
    for kind,name in [('image','image_manifest'),('preparation','preparation_record')]:
        assert constants['expected_'+kind+'_schema_constants'] == {k:v['const'] for k,v in defs[name]['properties'].items() if 'const' in v}
    digest_fields = {'protocol_schema_sha256':'protocol_schemas02','profile_sha256':'profile02',
        'output_schema_sha256':'output_schemas','transport_contract_sha256':'bootstrap_contract','transport_grammar_sha256':'bootstrap_grammar'}
    for field,binding in digest_fields.items():
        assert constants['expected_image_schema_constants'][field] == sha(plan['bindings'][binding]['path']) == plan['bindings'][binding]['sha256']
    assert constants['selected_custody_contract'] == pin(SPEC) and constants['selected_custody_schema_pack'] == pin(PACK)
    assert constants['actual_image_implements_selected_policies'] is None and not constants['actual_final_body_constants_verified']
    hashes = d['antecedent_and_hash_policy']
    assert hashes['I191_record_order'] == spec['record_order'] and hashes['CE08_record_order'] == FAMILIES
    for k in ['actual_accepted_prior_BASIS_index_resource_proofs','actual_full_referenced_evidence_closure']:
        assert hashes[k] is None
    for k in ['anchor_policy_and_prior_authentication_required_before_actor_registry',
              'prior_proofs_same_final_source_image_runtime_resource_scope_required',
              'all_evidence_reference_bodies_available_and_authentic_before_acceptance',
              'same_epoch_and_overlapping_current_validity_required',
              'caller_actor_registry_image_and_platform_cross_record_hashes_must_agree',
              'canonical_requester_caller_domain_constructor_and_resource_scope_must_agree',
              'later_CE10_bundle_approvals_cannot_supply_sole_prior_authentication',
              'later_C_Q_final_root_or_receipt_not_CE08_antecedent']:
        assert hashes[k] is True
    assert hashes['actual_canonical_codec_crypto_or_positive_schema_validation'] == 'NOT_RUN_NO_ACTUAL_BODIES'
    freshness = d['freshness_policy']
    assert fragment(freshness['source'])['id'] == 'K13'
    ctx = rd(plan['bindings']['profile02']['path'])['bootstrap']['context_limits']
    assert freshness['snapshot_lifetime_max_seconds'] == ctx['max_validity_seconds'] == 3600
    assert freshness['clock_error_max_seconds'] == ctx['max_clock_error_seconds'] == 5
    assert freshness['actual_clock_currentness_or_epoch_evidence'] is None and freshness['actual_snapshot_validity'] is None
    assert freshness['actual_fresh_snapshot_created'] is False
    assert freshness['strict_not_before_lt_expires_at'] and freshness['trusted_now_current_epoch_and_known_revocation_required_at_every_boundary']
    assert freshness['client_date_or_host_clock_is_not_trusted_runtime_evidence']
    assert freshness['fresh_snapshot_when_ready_not_expiry_extension_by_plan_or_cache']
    assert freshness['stale_TOFU_hidden_online_file_lookup_or_instantaneous_revocation_claim'] is False
    invalidate = d['invalidation_policy']
    assert len(invalidate['changed_inputs']) == 6
    assert invalidate['anchor_or_key_change_revisit_CE02_before_dependent_freeze']
    assert invalidate['invalidate_all_dependent_candidate_digests_reviews_and_scope_acceptances']
    assert invalidate['rerun_documentary_scope_CE03_to_CE10_as_needed_and_fresh_CE11_before_handoff']
    assert not invalidate['any_automatic_prior_proof_acceptance_or_hash_reuse'] and not invalidate['actual_downstream_hashes_created_or_rebound']
    graph = {s['id']:s['depends_on'] for s in plan['steps']}
    step_ancestors = ancestors(graph)
    order = ancestors(spec['record_order'])
    assert step_ancestors['CE08'] == {'CE01','CE02','CE03','CE04','CE05','CE06','CE07'}
    assert not {'CE09','CE10','CE11','CE12'} & step_ancestors['CE08']
    node_names = [n.upper() for n in FAMILIES]
    for i,node in enumerate(node_names):
        assert set(node_names[:i]) <= order[node]
        assert not {'C_CONTEXT','ACCEPTANCE','BUNDLE','Q_REQUEST','FINAL_ROOT','ATOMIC_CLAIM','LAUNCH_RECEIPT'} & order[node]
    descendants = {n:sorted(k for k,a in order.items() if n in a) for n in ['ANCHOR',*node_names]}
    phases = d['phase_boundary']
    assert all(phases[k] is True for k in ['CE08_four_antecedent_records_only','CE09_actual_C_and_acceptance_deferred',
        'CE10_bundle_role_domain_approvals_and_unique_mapping_deferred','CE11_no_CE12_receipt_dependency',
        'CE12_actual_claim_then_receipt_after_full_admission_and_separate_authorization','documentary_freeze_is_not_active_capture_inputs_rebind'])
    assert phases['actual_C_Q_bundle_mapping_root_claim_receipt_created'] is False
    assert phases['external_prerequisites_for_receipt'] == plan['closure_boundaries']['external_prerequisites_for_receipt']
    assert 'CE12' not in step_ancestors['CE11'] and 'ATOMIC_CLAIM' in order['LAUNCH_RECEIPT']
    ce7 = rd(CE07)
    assert d['inherited_scope_boundaries'] == ce7['inherited_scope_boundaries']
    assert d['preserved_negative_gates'] == ce7['preserved_negative_gates']
    assert len(d['inherited_scope_boundaries']['S01_exclusions']) == 8
    assert d['permission_boundary']['denied_action_classes'] == ce7['permission_boundary']['denied_action_classes']
    assert [r['id'] for r in d['role_scope_matrix']] == step['provenance_and_role']['primary_review_roles'] == ['R01','R02','R03','R06','R08']
    for row in d['role_scope_matrix']:
        assert row['assigned_person'] is None and row['accepted_appointment'] is False and row['current_actions_authorized'] == []
        baseline = next(r for r in rd(CE01)['role_scope_matrix'] if r['id'] == row['id'])
        assert row['separation_required_from'] == baseline['separation_required_from']
    for gate in d['preserved_negative_gates']:
        assert fragment({**gate['source'],'json_pointer':gate['json_pointer']}) == gate['observed_value']
    for key,value in d['current_effect'].items():
        if key == 'CE08_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_antecedent_records_created','actual_antecedent_records_frozen','actual_evidence_accepted','resource_obligations_closed']:
            assert value == 0 and type(value) is int
        else:
            assert value is False, key
    assert d['decision'] == plan['decision'] and d['E06'] == plan['E06']
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][:8])
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][8:])
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    assert previous['build_review']() == rd(PRIOR_PREP)
    original = Path.exists
    assert git('ls-tree','--name-only',previous['BASE'],'--',DOS) == ''
    assert git('ls-tree','--name-only',BASE,'--',DOS) == DOS
    with previous['predecessor_CE08_presence_as_of_base']():
        assert not (ROOT/DOS).exists()
    assert Path.exists is original and (ROOT/DOS).exists()
    class DocumentaryProbe(Exception):
        pass
    try:
        with previous['predecessor_CE08_presence_as_of_base']():
            raise DocumentaryProbe()
    except DocumentaryProbe:
        pass
    assert Path.exists is original and (ROOT/DOS).exists()
    assert [r['id'] for r in d['contract_rule_requirements']] == step['contract_rules']
    rules = []
    sections = [['contributor_closure','identity_and_separation_policy'],['contributor_closure','typed_array_limits'],
        ['source_runtime_policy','policy_constant_bindings'],['source_runtime_policy'],
        ['dependency_gates','antecedent_and_hash_policy'],['antecedent_and_hash_policy','phase_boundary'],
        ['identity_and_separation_policy','inherited_scope_boundaries'],['phase_boundary','antecedent_and_hash_policy'],
        ['freshness_policy'],['freeze_inventory','typed_array_limits','permission_boundary']]
    for row,scope in zip(d['contract_rule_requirements'],sections):
        assert fragment(row['source']) == dict(id=row['id'],rule=row['rule'])
        rules.append(dict(id=row['id'],source=row['source'],candidate_sections=[pin(DOS,'/'+s) for s in scope],
            requirement_preserved=True,actual_competent_acceptance=False))
    return dict(schema='d5.i214-i213-source-reconstruction.v1',increment='I214',date='2026-11-17',base_commit=BASE,
        input_pins=pins,method='Fixed Git blob and direct I193/I191 schema, constant, contributor, field, cap, epoch and antecedent reconstruction. I213 documentary build reproduced without historical publication mains.',
        freeze_shapes=shape,rule_review=rules,
        contributor_review=dict(complete_human_and_proof_author_closure_missing=True,CE03_provisional_not_final=True,
            no_forecast_preparer_or_automatic_alias_competence=True,actual_counts_unknown_not_zero=True,
            schema_limits=dict(preparers_min=1,preparers_max=16,actors_max=64,keys_max=64,dependencies_max=128),
            eight_S01_exclusions_preserved=True,R08_distinct_human_and_key_from_R01_R02=True,
            R01_R02_same_qualified_human_and_role_domain_approvals_allowed=True),
        phase_review=dict(step_graph=graph,CE08_ancestors=sorted(step_ancestors['CE08']),record_graph=spec['record_order'],
            invalidation_descendants=descendants,graphs_acyclic=True,no_reverse_C_bundle_root_receipt_dependency=True,
            CE11_not_dependent_on_CE12=True,CE12_claim_before_receipt_after_separate_authorization=True),
        scope_review=dict(documentary_inventory=24,helper_definitions=8,missing_source_mappings=6,
            exact_policy_constants_match_pinned_sources=True,image_not_runtime_identity=True,
            actual_canonical_body_schema_codec_crypto_validation=False,actual_snapshot_created=False,
            host_or_client_date_not_freshness_evidence=True,actual_epoch_clock_and_validity_unknown=True,
            unaccepted_dependencies=6,unassigned_roles=5,later_dossiers_absent=4),
        historical_guard_review=dict(CE08_absent_in_I213_base_present_in_I214_base=True,
            exact_query_projection_only=True,restored_after_success_and_exception=True,
            prior_documentary_rejections_reproduced=12,prior_publication_mains_run=False),
        verdict=dict(new_blocking_documentary_findings=0,CE08_documentary_baseline_confirmed=True,CE08_accepted=False,
            actual_antecedent_records_created=0,actual_antecedent_records_frozen=0,actual_evidence_accepted=0,
            independent_acceptance=False,resource_obligations_closed=0,product_or_components_executed=0))


def build_review(rec):
    d = rd(DOS)
    checks = [
        ('E01','Full contributor/alias/competence scope including CE07 proof authors','PRESERVED_NOT_ACTUAL_AUTHOR_COMPLETENESS'),
        ('E02','Registry then image then caller then platform, actual antecedents before C','PRESERVED_NO_FUTURE_BUNDLE_AUTHENTICATION'),
        ('E03','Genuine complete bodies, canonical hashes, six-source/runtime mapping and policy constants','SCHEMAS_AND_REQUIREMENTS_PINNED_ACTUAL_BODIES_MISSING'),
        ('E04','Actual sha/size/provider/custody/reviewer freeze inventory','61_TOP_LEVEL_SLOTS_MISSING_NOT_POSITIVE_NULL_RECORDS'),
        ('A01','I191 antecedent DAG and prior authentication','ACYCLIC_REQUIREMENT_NOT_ACCEPTED_ENROLLMENT'),
        ('A02','CE03 provisional; authors/body/scope changes invalidate downstream hashes and reviews','PRESERVED_CE02_REFRESH_FOR_ANCHOR_OR_KEY_CHANGE'),
        ('A03','Complete sorted unique preparers/actors/keys/dependencies in typed caps','LIMITS_PRESERVED_ACTUAL_COUNTS_UNKNOWN_NO_TRIMMING')]
    return dict(schema='d5.i214-i213-documentary-review.v1',increment='I214',date='2026-11-17',timezone='Europe/Madrid',
        base_commit=BASE,proposal_id=d['proposal_id'],profile_id=d['profile_id'],step='CE08',
        status='CE08_DOCUMENTARY_BASELINE_CONFIRMED_FINAL_RECORDS_MISSING_NOT_FROZEN_NOT_ACCEPTED_NOT_ADMITTED',
        candidate=pin(DOS),reconstruction=pin(RECON),findings=[],
        checks=[dict(id=i,scope=s,result=r) for i,s,r in checks],contract_rule_review=rec['rule_review'],
        documentary_clarifications=[
            dict(id='C01',subject='61 slots',disposition='Counts top-level required fields only:8/26/13/14. Nested contracts and evidence bodies remain required; this is not a complete proof-body count or validation result.'),
            dict(id='C02',subject='Author closure and later contributors',disposition='CE03 provisional intake cannot finalize the actor scope before genuine CE07 authors are known. New contribution or changed accepted scope invalidates dependent candidates and requires fresh review; no future author is preapproved.'),
            dict(id='C03',subject='Conditional freeze order',disposition='Genuine prior authentication and same-scope accepted resource proofs are missing. Four-record order specifies antecedents; future C/bundle/root/receipt cannot be their sole forecast authentication.'),
            dict(id='C04',subject='Separation and key reuse',disposition='Preserve all S01/source-author/root-key exclusions and R08 separation from R01/R02. No blanket R01/R02 separation is added; shared identity/key is conditional on genuine competence, allowed purpose bindings and separate role-domain approvals.')],
        provenance=dict(reviewer='Same Codex assistant/chat that prepared I213',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,competent_R01_R02_R03_R06_review=False,
            separate_R08_acceptance=False,independent_acceptance=False),
        verdict=rec['verdict'],current_effect={**d['current_effect'],'CE08_documentary_review_completed':True,
            'CE08_documentary_confirmation':True,'CE08_documentary_revision_required':False},decision=d['decision'],E06=d['E06'],
        limitations=['No accepted CE02-CE07 dependencies or actual final four record bodies, contributor/preparer/key completeness, evidence-body closure, source/image/runtime, caller/platform identity or current snapshot.',
            'No actual freeze, positive schema/canonical/crypto validation, resource qualification, accepted prior BASIS/index proof or900-second evidence. Same assistant is not competent independent acceptance.',
            'No product/component, build/import/compile, probe/clock/ledger, claim/process, enrollment/signature/contact, quota/reserve/binding/authority/destination or active contract change.'],
        next_scope='CE08 is a documentarily reviewed missing-evidence baseline for a separately requested CE09 documentary preparation. All actual freeze and acceptance prerequisites remain pending.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I214-audit.py',expected_result=STATUS,
            runtime_harness='N/A: documentary JSON/Git/hash/schema-fragment/antecedent review; no product/components or positive codec/crypto execution.',
            over400_lines=True,reason='One CE08 review with source pins, independent field/constant/author/DAG reconstruction and immutable preservation; overage reported. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_is_not_freeze_acceptance_or_admission=True))


def main():
    rec = reconstruct()
    assert rd(RECON) == rec and rd(REVIEW) == build_review(rec)
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published554'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 559
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i214-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published559'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():
            assert sha(p) == h, p
    assert seal['source_only'] and seal['current_effect'] == rd(REVIEW)['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I214',historical_pins=867,preserved_published_files=559,
        new_files=5,original_documentary_rejections_reproduced=12,verdict=rec['verdict'],
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
