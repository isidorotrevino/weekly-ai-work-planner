#!/usr/bin/env python3
"""I183 documentary contracts only. Never load target code or run a protocol/crypto."""
import copy
import hashlib
import io
import json
import re
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '6b5de0b9b72f69fa97580a5fcc0ba35aca2c6018'
PACK = P+'D5-I183-PGO181-SCHEMAS-CANDIDATE.json'
PROFILE = P+'D5-I183-PGO181-TRUST-PROFILE-CANDIDATE.json'
PREP = P+'D5-I183-preparation-review.json'
AUDIT = P+'D5-I183-audit.py'
SEAL = P+'D5-I183-integrity.json'
DOC = 'docs/design/D5-I183-PGO181-SCHEMAS-TRUST-CANDIDATE.md'
FILES = {PACK, PROFILE, PREP, AUDIT, SEAL, DOC}
PRIOR_SEAL = P+'D5-I182-integrity.json'
PID = 'PGO181-TRUST-ED25519-JCS-CANDIDATE-01'

def rd(p):
    return json.loads((ROOT/p).read_text())

def sha(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

def canonical(value):
    """Only our restricted ASCII/safe-integer documentary witnesses, not general JCS."""
    return json.dumps(value, ensure_ascii=False, allow_nan=False,
                      sort_keys=True, separators=(',', ':')).encode('ascii')

def domain(value):
    if type(value) is dict:
        for key, item in value.items():
            domain(key)
            domain(item)
    elif type(value) is list:
        for item in value:
            domain(item)
    elif type(value) is str:
        assert all(32 <= ord(c) <= 126 for c in value)
    elif type(value) is int:
        assert 0 <= value <= 9007199254740991
    else:
        assert type(value) is bool

def strict_body(body):
    def pairs(items):
        out = {}
        for key, value in items:
            assert key not in out
            out[key] = value
        return out
    def no_float(value):
        raise AssertionError('float/non-finite token forbidden')
    value = json.loads(body.decode('utf-8'), object_pairs_hook=pairs,
                       parse_float=no_float, parse_constant=no_float)
    domain(value)
    assert body == canonical(value)
    return value

def validate(s, value, defs):
    """Documentary evaluator of exactly the pack's keyword subset, not a runtime validator."""
    if '$ref' in s:
        validate(defs[s['$ref'].removeprefix('#/$defs/')], value, defs)
    if 'const' in s:
        assert canonical(value) == canonical(s['const'])
    if 'enum' in s:
        assert any(canonical(value) == canonical(x) for x in s['enum'])
    for keyword in ['oneOf', 'anyOf']:
        if keyword in s:
            matches = sum(accepts(x, value, defs) for x in s[keyword])
            assert matches == 1 if keyword == 'oneOf' else matches >= 1
    if 'type' not in s:
        return
    t = s['type']
    expected = {'object':dict, 'array':list, 'string':str, 'integer':int}
    assert type(value) is expected[t]
    if t == 'object':
        assert s.get('minProperties', 0) <= len(value) <= s.get('maxProperties', 10000)
        assert set(s.get('required', [])) <= set(value)
        props = s.get('properties', {})
        for key, item in value.items():
            if 'propertyNames' in s:
                validate(s['propertyNames'], key, defs)
            if key in props:
                validate(props[key], item, defs)
            else:
                assert s.get('additionalProperties') is not False
                validate(s['additionalProperties'], item, defs)
    elif t == 'array':
        assert s['minItems'] <= len(value) <= s['maxItems']
        for item in value:
            validate(s['items'], item, defs)
    elif t == 'string':
        assert s['minLength'] <= len(value) <= s['maxLength']
        assert re.fullmatch(s['pattern'], value)
    elif t == 'integer':
        assert s['minimum'] <= value <= s['maximum']

def accepts(s, value, defs):
    try:
        validate(s, value, defs)
        return True
    except AssertionError:
        return False

def rejected(action):
    try:
        action()
    except (AssertionError, ValueError, UnicodeError):
        return
    raise AssertionError('Documentary negative case unexpectedly accepted')

def schema_shape(s, defs):
    allowed = {'$schema','$id','title','$defs','$ref','oneOf','anyOf','type','properties',
               'required','additionalProperties','const','enum','minLength','maxLength',
               'pattern','minimum','maximum','items','minItems','maxItems','propertyNames',
               'minProperties','maxProperties'}
    assert type(s) is dict and not set(s)-allowed
    if '$ref' in s:
        assert set(s) == {'$ref'} and s['$ref'].startswith('#/$defs/')
        assert s['$ref'][8:] in defs
    if 'type' in s:
        assert s['type'] in {'object','array','string','integer'}
        if s['type'] == 'object':
            if 'properties' in s:
                assert s['additionalProperties'] is False
                assert set(s['required']) == set(s['properties'])
                assert len(s['required']) == len(set(s['required']))
            else:
                assert s['minProperties'] == s['maxProperties']
                assert 'propertyNames' in s
        if s['type'] == 'integer':
            assert 0 <= s['minimum'] <= s['maximum'] <= 9007199254740991
        if s['type'] == 'string':
            re.compile(s['pattern'])
            assert 0 < s['minLength'] <= s['maxLength']
    for key in ['properties','$defs']:
        for sub in s.get(key, {}).values():
            schema_shape(sub, defs)
    for key in ['oneOf','anyOf']:
        for sub in s.get(key, []):
            schema_shape(sub, defs)
    for key in ['items','propertyNames','additionalProperties']:
        if isinstance(s.get(key), dict):
            schema_shape(s[key], defs)


def witness(s, defs):
    """In-memory shape data only: zero digests/strings are not evidence, keys or signatures."""
    if '$ref' in s:
        return witness(defs[s['$ref'][8:]], defs)
    if 'const' in s:
        return copy.deepcopy(s['const'])
    if 'enum' in s:
        return s['enum'][0]
    if s['type'] == 'object':
        if 'properties' in s:
            return {k:witness(v, defs) for k,v in s['properties'].items()}
        names = defs['historical_path']['enum']+s['propertyNames']['anyOf'][1]['enum']
        assert len(names) == s['minProperties']
        return {p:'0'*64 for p in names}
    if s['type'] == 'array':
        return [witness(s['items'], defs) for _ in range(s['minItems'])]
    if s['type'] == 'integer':
        return s['maximum']
    if s['pattern'] == '^[ -~]+$':
        return 'documentary-placeholder'
    return '0'*s['maxLength']


def check_history(profile):
    pins = profile['input_pins']
    assert len(pins) == 706
    requests = ''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'], cwd=ROOT, input=requests))
    for p,h in sorted(pins.items()):
        head = stream.readline().decode().split()
        assert len(head) == 3 and head[1] == 'blob', p
        body = stream.read(int(head[2]))
        assert stream.read(1) == b'\n'
        assert hashlib.sha256(body).hexdigest() == h == sha(p), p
    # Run only the predecessor's documentary functions, never its publication boundary/main.
    m = runpy.run_path(str(ROOT/(P+'D5-I182-audit.py')))
    m['validate_preparation']()
    rec = m['reconstruct']()
    assert m['rd'](m['RECON']) == rec
    assert m['rd'](m['NEW_REVIEW']) == m['review_record'](rec)
    oldseal = rd(PRIOR_SEAL)
    preserved = {**oldseal['preserved_published393'],**oldseal['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 398
    for p,h in preserved.items():
        assert sha(p) == h, p
    return preserved


def build_review():
    profile = rd(PROFILE)
    preserved = check_history(profile)
    pack = rd(PACK)
    defs = pack['$defs']
    assert pack['$schema'] == 'https://json-schema.org/draft/2020-12/schema'
    assert pack['$id'] == profile['schema_pack']['id']
    assert sha(PACK) == profile['schema_pack']['sha256']
    schema_shape(pack, defs)
    top = profile['schema_pack']['top_level_definitions']
    assert len(top) == 17 and len(defs) == 32
    assert pack['oneOf'] == [{'$ref':'#/$defs/'+n} for n in top]
    headers = [defs[n]['properties']['schema']['const'] for n in top]
    assert len(set(headers)) == 17
    old = rd(P+'D5-I181-F179-01-GATE-ORDER-PROPOSAL.json')
    slots = {s['role']:s for s in old['logical_future_slots']}
    assert profile['scope']['future_slots'] == old['logical_future_slots']
    assert profile['scope']['successor_sources'] == old['successor_source_scope']['slots']
    for slot in slots.values():
        assert not (ROOT/slot['path']).exists()
    assert not (ROOT/'testing/prospective_capture_joint_prp181').exists()
    assert profile['final_CP07_conditions'] == old['stage_claims'][3]['required_conditions']
    assert len(profile['final_CP07_conditions']) == 9
    assert [r['id'] for r in profile['semantic_contracts']] == ['C%02d'%i for i in range(1,15)]
    numeric = rd(P+'D5-I122-CAPACITY-CONTRACT.json')['numeric_candidates']
    for name in ['registry','capacity_contract']:
        assert defs[name]['properties']['numeric_candidates']['const'] == numeric
    assert defs['source_basis']['properties']['status']['const'] == 'ANTECEDENT_BASIS_ONLY_NOT_ADMISSION'
    assert 'CP07_exact_admission_resolved' not in json.dumps(defs)
    assert defs['authority_payload']['properties']['phase']['const'] == 'BINDING_PAYLOAD_ONLY_NO_RUNTIME_PERMISSION'
    assert defs['source_basis']['properties']['source_bindings']['minProperties'] == 489
    assert defs['authority_payload']['properties']['capture_inputs']['minProperties'] == 494
    assert len(defs['component_manifest']['properties']['source_bindings']['properties']) == 9
    # No late references can be introduced by the explicit antecedent schemas.
    late = {slots[n]['path'] for n in ['COMPONENT_MANIFEST','FINAL_RAW','FINAL_REVIEW','FINAL_SEAL','AUTHORITY_PAYLOAD','FINAL_ROOT']}
    basis_extra = defs['source_basis']['properties']['source_bindings']['propertyNames']['anyOf'][1]['enum']
    assert not late.intersection(basis_extra)
    index_map = defs['resource_index']['properties']['source_bindings']['properties']
    assert not late.intersection(index_map)
    assert profile['budget']['unchanged_ten_body_caps'] == {k:v['max_serialized_bytes'] for k,v in slots.items()}
    assert profile['budget']['read_design_upper_bytes'] == 266693693
    assert not profile['budget']['successor_Reader_fit_verified']
    assert profile['cryptography']['algorithm'] == 'Ed25519 (pure, RFC8032 section5.1; not Ed25519ph or Ed25519ctx)'
    assert defs['signature']['minLength'] == defs['signature']['maxLength'] == 128
    assert defs['sha256']['minLength'] == defs['sha256']['maxLength'] == 64
    assert defs['verifier_profile']['properties']['id']['const'] == profile['profile_id'] == PID
    assert profile['encoding']['signed_core_exclusions'] == ['issuer_signature','acceptor_signature','root_file_sha256','future_execution_outcome']
    assert not set(profile['encoding']['signed_core_exclusions']).intersection(defs['signed_core']['properties'])
    assert profile['bootstrap']['assigned_persons'] is None
    assert profile['bootstrap']['actual_key_material'] is None
    assert profile['bootstrap']['actual_context'] is None and profile['bootstrap']['actual_request'] is None
    assert not profile['bootstrap']['independent_acceptance']
    assert profile['current_effect']['exact_schemas_prepared'] and profile['current_effect']['trust_profile_prepared']
    for k,v in old['current_effect'].items():
        assert profile['current_effect'][k] == v
    assert profile['decision'] == old['decision'] and profile['E06'] == old['E06']
    assert set(profile['work_unit']['rollback_files']) == FILES
    checks = []
    widths = {}
    for name in top:
        s = defs[name]
        w = witness(s, defs)
        domain(w)
        validate(s, w, defs)
        assert sum(accepts(defs[n], w, defs) for n in top) == 1
        assert strict_body(canonical(w)) == w
        widths[name] = len(canonical(w))
        for key in s['required']:
            bad = copy.deepcopy(w)
            del bad[key]
            rejected(lambda:validate(s, bad, defs))
        bad = copy.deepcopy(w)
        bad['unrecognized_field'] = True
        rejected(lambda:validate(s, bad, defs))
        rejected(lambda:validate(s, None, defs))
        checks.append({'schema':name,'required_keys_checked':len(s['required']),
                       'unknown_and_missing_keys_rejected':True,'unique_family_discriminator':True})
    # Width witnesses establish only encodability of documentary shapes, never runtime evidence/fit.
    role_names = dict(REGISTRY='registry',CAPACITY_CONTRACT='capacity_contract',RESOURCE_INDEX='resource_index',
        SOURCE_BASIS_CERT='source_basis',COMPONENT_MANIFEST='component_manifest',FINAL_RAW='component_raw',
        FINAL_REVIEW='component_review',FINAL_SEAL='component_seal',AUTHORITY_PAYLOAD='authority_payload',FINAL_ROOT='final_root')
    for role,name in role_names.items():
        assert widths[name] <= slots[role]['max_serialized_bytes'], (role,widths[name])
    assert widths['trust_context'] <= profile['bootstrap']['context_limits']['serialized_bytes']
    for n in ['worker_invocation','worker_ready','parent_release','capture_binding']:
        assert widths[n]+1 <= 512
    for n in ['runtime_request','component_request']:
        assert widths[n] <= 2048
    parser_bad = [b'{"a":1,"a":2}',b'{"x":{"a":1,"a":2}}',b'{"a":1.0}',b'{"a":1e0}',
        b'{"a":-0}',b'{"a":NaN}',b'{"a":null}',b'{"a":9007199254740992}',b'{"a":1}\n',
        b'{ "a":1}',b'{"a":"\\u0000"}',b'{"a":"\\ud800"}',b'{"a":"\\u00e9"}',b'\xef\xbb\xbf{}']
    for body in parser_bad:
        rejected(lambda:strict_body(body))
    for value in [True,False,1.0,-1,9007199254740992,None]:
        rejected(lambda:validate(defs['resource_bounds']['properties']['whole_heap_upper_bytes'],value,defs))
    bad_map = witness(defs['authority_payload'],defs)
    mapping = bad_map['capture_inputs']
    mapping[slots['FINAL_ROOT']['path']] = mapping.pop(next(iter(mapping)))
    rejected(lambda:validate(defs['authority_payload'],bad_map,defs))
    return dict(schema='d5.i183-preparation-review.v1',increment='I183',date='2026-11-16',base_commit=BASE,
        status='EXACT_SCHEMA_TRUST_CANDIDATE_PREPARED_NOT_ADOPTED_NOT_IMPLEMENTED_NOT_ADMITTED',
        proposal='PGO181-SPLIT-ROOT-01',profile_id=PID,
        schema_pack={'path':PACK,'sha256':sha(PACK)},profile={'path':PROFILE,'sha256':sha(PROFILE)},
        checks=checks,top_schemas=17,definitions=32,semantic_contracts=14,input_pins=706,preserved_published_files=len(preserved),
        documentary_encoding_widths=widths,
        witness_scope='Only ephemeral shape placeholders. No evidence/keys/signatures/PASS bodies emitted. Widths are neither all-valid-instance upper bounds nor resource/Reader fit proof; effective validity also requires per-body byte caps and semantic truth.',
        lexical_negative_cases=len(parser_bad),schema_evaluator='Small auditable interpreter for exact used keyword subset; not complete JSON Schema conformance or runtime/crypto implementation.',
        provenance={'preparer':'Same Codex assistant in same chat','actor_independent':False,'organizationally_independent':False,'independent_acceptance':False},
        current_effect=profile['current_effect'],decision=profile['decision'],E06=profile['E06'],
        remaining_work=profile['remaining_work'],work_unit=profile['work_unit'])


def main():
    review = build_review()
    assert rd(PREP) == review
    seal = rd(SEAL)
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published393'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert seal['preserved_published398'] == preserved
    assert seal['base_commit'] == BASE and seal['schema'] == 'd5.i183-integrity.v1'
    assert set(seal['artifacts']) == FILES-{SEAL}
    for p,h in seal['artifacts'].items():
        assert sha(p) == h, p
    assert seal['source_only'] and seal['resource_obligations_closed'] == 0
    for key in ['independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:
        assert seal[key] is False
    assert seal['IR03'] == 'NOT_READY'
    changes = set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changes == FILES, changes
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I183',candidate_schema_families=17,
        semantic_contracts=14,historical_pins=706,prior_published_files_preserved=398,new_files=6,
        adopted=False,implemented=False,trust_anchor_established=False,F179_01_resolved=False,
        successor_Reader_fit_verified=False,product_or_components_executed=0,quotas_changed=False,
        rebind_applied=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,
        IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__ == '__main__':
    main()
