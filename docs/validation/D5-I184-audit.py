#!/usr/bin/env python3
"""I184 documentary review: JSON/Git/hash/schema/role relations only; no target/crypto execution."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'ecd63ca9b6eb716031e2e30957f2c909f89f99df'
PACK = P+'D5-I183-PGO181-SCHEMAS-CANDIDATE.json'
PROFILE = P+'D5-I183-PGO181-TRUST-PROFILE-CANDIDATE.json'
OLD_REVIEW = P+'D5-I183-preparation-review.json'
OLD_AUDIT = P+'D5-I183-audit.py'
OLD_SEAL = P+'D5-I183-integrity.json'
OLD_DOC = 'docs/design/D5-I183-PGO181-SCHEMAS-TRUST-CANDIDATE.md'
S01 = P+'D5-I179-S01-ROLES-SCOPE-GATES.json'
RECON = P+'D5-I184-I183-source-reconstruction.json'
REVIEW = P+'D5-I184-I183-documentary-review.json'
AUDIT = P+'D5-I184-audit.py'
SEAL = P+'D5-I184-integrity.json'
DOC = 'docs/design/D5-I184-I183-SCHEMAS-TRUST-REVIEW.md'
FILES = {RECON, REVIEW, AUDIT, SEAL, DOC}
PRIOR_FILES = {PACK, PROFILE, OLD_REVIEW, OLD_AUDIT, OLD_SEAL, OLD_DOC}

def rd(p):
    return json.loads((ROOT/p).read_text())

def sha(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

def pin(p, pointer):
    return dict(path=p, sha256=sha(p), json_pointer=pointer)

def edge(a, b):
    assert a != b
    return tuple(sorted((a, b)))

def resolve(s, defs):
    if '$ref' in s:
        assert set(s) == {'$ref'} and s['$ref'].startswith('#/$defs/')
        return resolve(defs[s['$ref'][8:]], defs)
    return s

def schema_children(s):
    for k in ['properties', '$defs']:
        yield from s.get(k, {}).values()
    for k in ['oneOf', 'anyOf']:
        yield from s.get(k, [])
    for k in ['items', 'propertyNames', 'additionalProperties']:
        if isinstance(s.get(k), dict):
            yield s[k]

def refs(s):
    if '$ref' in s:
        yield s['$ref'][8:]
    for sub in schema_children(s):
        yield from refs(sub)

def schema_nodes(s):
    yield s
    for sub in schema_children(s):
        yield from schema_nodes(sub)

def role_review(profile):
    matrix = rd(S01)['role_authority_validity_matrix']
    required = {edge(row['id'], other) for row in matrix for other in row['separation_required_from']}
    def normalize(term):
        if term.startswith('issuer.') or term.startswith('acceptor.'):
            return term
        if term == 'source_author_id':
            return 'SOURCE_AUTHOR'
        assert term.startswith('R') and term[1:3].isdigit()
        return term[:3]
    written = set()
    key_constraints = []
    for expression in profile['bootstrap']['separation']:
        left, right = (x.strip() for x in expression.split('!='))
        if '.' in left or '.' in right:
            key_constraints.append(expression)
        else:
            written.add(edge(normalize(left), normalize(right)))
    missing = required-written
    assert len(required) == 8 and len(written) == 4 and len(missing) == 5
    assert missing == {
        edge('R03','DOCUMENTARY_PREPARER'), edge('R06','DOCUMENTARY_PREPARER'),
        edge('R08','DOCUMENTARY_PREPARER'), edge('R08','R03'), edge('R08','R06')}
    # Symbolic equality partitions: no names, actual appointments, signatures or protocol run.
    examples = []
    for a,b in sorted(missing):
        def representative(x):
            return a if x == b else x
        assert all(representative(x) != representative(y) for x,y in written)
        assert representative(a) == representative(b)
        examples.append(dict(coalesced_symbols=[a,b],all_written_actor_disequalities_still_satisfiable=True,
                             inherited_disequality_violated=[a,b],symbolic_only=True))
    context = rd(PACK)['$defs']['trust_context']['properties']
    assert 'source_author_id' in context and 'documentary_preparer_id' not in context
    return dict(inherited_actor_disequalities=[list(x) for x in sorted(required)],
        written_actor_disequalities=[list(x) for x in sorted(written)],
        written_key_disequalities=key_constraints,
        missing_inherited_actor_disequalities=[list(x) for x in sorted(missing)],
        symbolic_countermodels=examples,
        source_author_not_defined_as_documentary_preparer=True,
        inherited_independence_only_partially_restated=True,
        broad_all_roles_accepted_clause_does_not_exactly_encode_missing_separation=True,
        no_actual_role_collision_or_runtime_bypass_claimed=True)

def git_blobs(pins):
    req = ''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'], cwd=ROOT, input=req))
    out = {}
    for p,h in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', p
        body = stream.read(int(header[2]))
        assert stream.read(1) == b'\n'
        assert hashlib.sha256(body).hexdigest() == h == sha(p), p
        out[p] = body
    return out

def reconstruct():
    profile = rd(PROFILE)
    pins = {**profile['input_pins'], **{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 712
    blobs = git_blobs(pins)
    pack = json.loads(blobs[PACK])
    defs = pack['$defs']
    top = [s['$ref'][8:] for s in pack['oneOf']]
    assert len(top) == 17 and len(defs) == 32 and len(set(top)) == 17
    assert profile['schema_pack']['sha256'] == pins[PACK]
    # Independent structural traversal and reference DAG. Const/enum data are not schemas.
    children = {name:set(refs(s)) for name,s in defs.items()}
    visited = set()
    active = set()
    def walk(name):
        assert name in defs and name not in active
        if name in visited:
            return
        active.add(name)
        for child in children[name]:
            walk(child)
        active.remove(name)
        visited.add(name)
    for name in defs:
        walk(name)
    closed = maps = 0
    for node in schema_nodes(pack):
        if node.get('type') == 'object':
            if 'properties' in node:
                assert node['additionalProperties'] is False
                assert set(node['required']) == set(node['properties'])
                closed += 1
            else:
                assert node['minProperties'] == node['maxProperties']
                assert node['additionalProperties'] == {'$ref':'#/$defs/sha256'}
                maps += 1
    headers = [defs[name]['properties']['schema']['const'] for name in top]
    assert len(set(headers)) == 17
    old = rd(P+'D5-I181-F179-01-GATE-ORDER-PROPOSAL.json')
    slots = {s['role']:s['path'] for s in old['logical_future_slots']}
    historical = set(defs['historical_bindings']['const'])
    assert len(historical) == 480 and set(defs['historical_path']['enum']) == historical
    for p,h in defs['historical_bindings']['const'].items():
        assert pins[p] == h
    sources = set(defs['source_bindings']['properties'])
    assert sources == set(old['successor_source_scope']['slots']) and len(sources) == 6
    def fixed_map(name, field):
        s = resolve(defs[name]['properties'][field], defs)
        if 'properties' in s:
            return set(s['properties'])
        branches = s['propertyNames']['anyOf']
        assert branches[0] == {'$ref':'#/$defs/historical_path'}
        result = historical|set(branches[1]['enum'])
        assert len(result) == s['minProperties'] == s['maxProperties']
        return result
    late = {slots[x] for x in ['COMPONENT_MANIFEST','FINAL_RAW','FINAL_REVIEW','FINAL_SEAL','AUTHORITY_PAYLOAD','FINAL_ROOT']}
    basis = fixed_map('source_basis','source_bindings')
    index = fixed_map('resource_index','source_bindings')
    manifest = fixed_map('component_manifest','source_bindings')
    payload = fixed_map('authority_payload','capture_inputs')
    assert basis == historical|sources|{slots[x] for x in ['REGISTRY','CAPACITY_CONTRACT','RESOURCE_INDEX']}
    assert index == sources|{slots['CAPACITY_CONTRACT']}
    assert manifest == sources|{slots[x] for x in ['REGISTRY','CAPACITY_CONTRACT','SOURCE_BASIS_CERT']}
    assert payload == historical|sources|{slots[x] for x in slots if x not in ['FINAL_ROOT','AUTHORITY_PAYLOAD']}
    assert not late.intersection(basis|index) and slots['FINAL_ROOT'] not in payload
    assert len(basis) == 489 and len(payload) == 494 and len(manifest) == 9
    assert 'CP07_exact_admission_resolved' not in json.dumps(defs)
    assert profile['final_CP07_conditions'] == old['stage_claims'][3]['required_conditions']
    core = set(defs['signed_core']['properties'])
    assert not core.intersection(profile['encoding']['signed_core_exclusions'])
    assert all(k in core for k in ['trust_context_sha256','runtime_request_sha256','invocation_id','trust_verifier_profile'])
    root_fields = set(defs['final_root']['properties'])
    assert root_fields == {'schema','signed_core','issuer_signature','acceptor_signature'}
    for name in ['worker_invocation','worker_ready','parent_release','capture_binding']:
        assert set(defs[name]['properties']) == {'schema','message','root_sha256','invocation_id','trust_context_sha256','runtime_request_sha256'}
    limits = rd(P+'D5-I122-CAPACITY-CONTRACT.json')['numeric_candidates']
    for name in ['registry','capacity_contract']:
        assert defs[name]['properties']['numeric_candidates']['const'] == limits
    budget = profile['budget']
    assert budget['physical_union_with_root'] == 496
    unique = sum(len(blobs[p]) for p in historical)+262144+253184
    assert unique == 87280411
    assert 3*unique+4852460 == budget['read_design_upper_bytes'] == 266693693
    assert not budget['successor_Reader_fit_verified']
    # Reproduce I183 documentary preparation, not its publication-boundary main.
    m = runpy.run_path(str(ROOT/OLD_AUDIT))
    assert m['build_review']() == rd(OLD_REVIEW)
    role_result = role_review(profile)
    assert not any((ROOT/s).exists() for s in slots.values())
    assert not (ROOT/'testing/prospective_capture_joint_prp181').exists()
    return dict(schema='d5.i184-i183-source-reconstruction.v1',increment='I184',date='2026-11-16',base_commit=BASE,
        input_pins=pins,method='Git blobs + separate schema/reference/key-set traversal, inherited role-disequality comparison and symbolic countermodels; documentary preparation independently rerun, never runtime/crypto.',
        schema_structure=dict(top_families=17,definitions=32,closed_object_definitions=closed,fixed_cardinality_maps=maps,
            reference_graph_acyclic=True,local_refs_only=True,unique_discriminators=True,
            historical_members=480,source_members=6,basis_members=489,manifest_members=9,payload_members=494,
            antecedents_exclude_future_bodies=True,full_CP07_conditions=9),
        role_separation=role_result,
        signature_and_trust_scope=dict(core_excludes_signatures_self_hash_future_result=True,two_role_signatures_same_core_required=True,
            external_authentic_context_required=True,strict_Ed25519_profile_is_local_choice=True,
            cryptographic_conformance_or_security_verified=False,keys_created=False,signatures_created=False,
            actual_custody_clock_epoch_revocation_or_replay_verified=False),
        budget=dict(physical_paths=496,unique_design_bytes=unique,read_design_bytes=266693693,
            actual_fit_verified=False,all_body_caps_and_new_fresh_bound_still_required=True,
            inherited_width_witnesses_not_universal_upper_bounds=True),
        remaining_implementation_scope=['Complete enclosing capture context/launch schemas (capture_binding alone is only a fragment).',
            'Concrete trusted caller/custody/clock/replay implementation, key/library conformance and all resource/source/output requalification.',
            'Actual named competent appointments, genuine antecedent acceptance, final E06 provenance and root/payload/request/signature evidence.'],
        documentary_blocking_findings=1,actual_runtime_exploits_claimed=False,
        provenance=dict(actor_independent=False,organizationally_independent=False,independent_acceptance=False),
        product_or_components_executed=0,resource_obligations_closed=0,F179_01_resolved=False)


def build_review(rec):
    profile = rd(PROFILE)
    return dict(schema='d5.i184-i183-documentary-review.v1',increment='I184',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        proposal='PGO181-SPLIT-ROOT-01',profile_id=profile['profile_id'],
        status='REQUIRES_REVISION_BLOCKING_DOCUMENTARY_SEPARATION_GAP_NOT_ADOPTED_NOT_IMPLEMENTED_NOT_ADMITTED',
        reconstruction=dict(path=RECON,sha256=sha(RECON)),
        provenance=dict(reviewer='Same Codex assistant/chat that prepared I183',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,independent_acceptance=False,custodian_acceptance=False),
        findings=[dict(id='F183-01',priority='P1',classification='BLOCKING_DOCUMENTARY_CONTRACT_GAP',
            title='Preserve the complete S01 independence matrix in the exact trust profile',
            evidence=[pin(S01,'/role_authority_validity_matrix'),pin(PROFILE,'/bootstrap/separation'),pin(PACK,'/$defs/trust_context/properties')],
            missing_disequalities=rec['role_separation']['missing_inherited_actor_disequalities'],
            problem='I183 states only part of the inherited separation matrix. It permits R08 to coincide with R03 or R06 under its explicit actor predicates and lacks a documentary-preparer identity distinct from source_author_id. The all8 roles accepted clause is not an exact import of the S01 exclusions. No current appointment or admission is asserted.',
            consequence='A future verifier following only I183 explicit relations could accept overlapping primary/final review or self-review forbidden by S01. This blocks documentary acceptance of the candidate profile, not a finding of an executed bypass or real role collision.',
            required_revision='Prepare a new versioned candidate preserving all8 inherited actor exclusions, or explicitly obtain competent versioned adjudication of a changed separation policy. Bind authentic documentary-preparer identity/provenance (not assumed equal to source author), include all predicates and negative symbolic cases, preserve key separation, and rebind the new pack/profile digests. Do not change old candidate/active flags or grant runtime permission.',
            closed=False,fix_applied=False)],
        checks=[dict(id=i,scope=s,result=r) for i,s,r in [
            ('R01','17 closed schema families/32 definitions and local acyclic refs','PASS_DOCUMENTARY_STRUCTURE'),
            ('R02','Exact480 historical/six source sets and489/9/494 joins','PASS_BINDING_SET_MODEL'),
            ('R03','BASIS/index exclude descendants; legacy CP07 absent;9 full predicates retained','PASS_CLAIM_BOUNDARY'),
            ('R04','Root binds preceding hashes/profile/context/request; no self/back pin','PASS_ROOT_CONTRACT_MODEL'),
            ('R05','Actual raw/review/seal and authentic separate component permission required','PASS_DECLARED_EVIDENCE_REQUIREMENT_NOT_RUN'),
            ('R06','JCS ASCII/safe integer subset plus schema/cap/semantic predicates','PASS_RESTRICTED_ENCODING_SPEC_NOT_GENERAL_CODEC_PROOF'),
            ('R07','Two pure Ed25519 role domains on same canonical core','PASS_PROPOSED_SIGNATURE_SPEC_NOT_CRYPTO_PROOF'),
            ('R08','External trusted caller and accepted key/time/epoch/replay premises','DECLARED_BUT_NOT_ESTABLISHED'),
            ('R09','Complete inherited S01 role independence','FAIL_F183_01_FIVE_MISSING_EXCLUSIONS'),
            ('R10','Signature primitive/profile restrictions distinguished from RFC requirements','PASS_DOCUMENTARY_ATTRIBUTION'),
            ('R11','Same496-path Reader; numeric limits/design arithmetic preserved','PASS_CONDITIONAL_MODEL_NOT_ACTUAL_FIT'),
            ('R12','Width witnesses cannot establish every valid body/resource bound','PASS_LIMITATION_DISCLOSED'),
            ('R13','New handshake fields and full enclosing context/launch format','FRAGMENT_DEFINED_ENCLOSING_SCHEMAS_PENDING'),
            ('R14','Original179/321/12/30 scope and new costs','FULL_REQUALIFICATION_PENDING'),
            ('R15','Same preparer/reviewer actor; no independent acceptance','PASS_PROVENANCE_DISCLOSURE'),
            ('R16','No active changes, fake evidence or execution/admission','PASS_PRESERVATION_ONLY')]],
        verdict=dict(schema_structure_documentarily_consistent=True,trust_separation_complete=False,
            documentary_acceptance=False,candidate_requires_revision=True,blocking_documentary_findings=1,
            adopted=False,implemented=False,implementation_ready=False,trust_anchor_established=False,
            successor_Reader_fit_verified=False,F179_01_resolved=False,S01_accepted=False,
            independent_acceptance=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False),
        remaining_work=rec['remaining_implementation_scope'],current_effect=profile['current_effect'],decision=profile['decision'],E06=profile['E06'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I184-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: documentary contract review; no runtime changes or product/component/crypto execution.',over400_lines=True,
            reason='Traceable Git/schema/role reconstruction, findings and preservation seal in one documentary review; overage reported.'),
        publication=dict(commit_and_push_requested=True,publication_is_not_adoption_or_authority=True))


def main():
    rec = reconstruct()
    assert rd(RECON) == rec
    assert rd(REVIEW) == build_review(rec)
    prior = rd(OLD_SEAL)
    preserved = {**prior['preserved_published398'],**prior['artifacts'],OLD_SEAL:sha(OLD_SEAL)}
    assert len(preserved) == 404
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i184-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published404'] == preserved
    assert set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():
            assert sha(p) == h, p
    assert seal['source_only'] and seal['resource_obligations_closed'] == 0 and seal['IR03'] == 'NOT_READY'
    for key in ['independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:
        assert seal[key] is False
    changes = set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changes == FILES, changes
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I184',historical_pins=712,
        schema_families=17,blocking_documentary_findings=1,missing_inherited_role_exclusions=5,
        documentary_acceptance=False,adopted=False,implemented=False,F179_01_resolved=False,
        prior_published_files_preserved=404,new_files=5,product_or_components_executed=0,
        quotas_changed=False,rebind_applied=False,resource_obligations_closed=0,proposal_enabled=False,
        D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__ == '__main__':
    main()
