#!/usr/bin/env python3
"""Read-only documentary hash/AST/JSON/arithmetic audit. No product imports/calls.

Run from repository root. Does not execute proposed components, campaigns or
original tests; those stay NOT_RUN. A pass never enables PJC115/R2 or closes D5.
"""
import ast
import copy
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREFIX = 'docs/validation/D5-I117-'

def read(path):
    return json.loads((ROOT / path).read_text())

def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()

def encoded(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False,
                      separators=(',', ':')).encode()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

def symbolic(value):
    return type(value) is dict and set(value) == {'$ascii_length'}

def json_size(value):
    if symbolic(value):
        return value['$ascii_length'] + 2
    if value is None:
        return 4
    if type(value) in (str, int):
        return len(encoded(value))
    if type(value) is dict:
        return 2 + sum(json_size(k) + 1 + json_size(v) for k, v in value.items()) + max(0, len(value)-1)
    if type(value) in (tuple, list):
        return 2 + sum(map(json_size, value)) + max(0, len(value)-1)
    raise AssertionError(type(value))

def digest_size(value):
    # I70 markers: s = 4 bytes + ascii-escaped JSON; int likewise;
    # tuple/list/dict type-name delimiters plus recursively encoded members.
    if symbolic(value):
        return value['$ascii_length'] + 6
    if type(value) is str:
        return 4 + len(json.dumps(value, ensure_ascii=True).encode())
    if type(value) is int:
        return 4 + len(str(value))
    if value is None:
        return 13
    if type(value) is dict:
        return 6 + sum(digest_size(k) + digest_size(v) for k, v in value.items())
    if type(value) in (tuple, list):
        return len(type(value).__name__) + 2 + sum(map(digest_size, value))
    raise AssertionError(type(value))

def main():
    c = read(PREFIX+'CP02-source-counterexample.json')
    d = read(PREFIX+'PJC115-R2-design.json')
    o = read(PREFIX+'operand-envelope-progress.json')
    r = read(PREFIX+'reader-capacity-design.json')
    seal = read(PREFIX+'integrity.json')
    assert git('rev-parse', 'HEAD') == c['base_commit'] == '50c49678568bae2abeefbe5fec0285f26c628283'
    assert not git('diff', '--name-only') and not git('diff', '--cached', '--name-only')
    for doc in (c, d, o, r):
        assert doc['inputs'] == c['inputs'] and len(doc['inputs']) == 464
        assert doc['increment'] == 'I117' and doc['IR03'] == 'NOT_READY'
        for field in ('product_or_runner_imported','implementation_changed','quota_changed',
                      'functional_profile_created','future_capture_authority_or_destination_created',
                      'D5_closed','H07_closed','closure','publication_authorized','real_providers',
                      'credentials','consumption','reservations','activation','promotion','deployment','D6'):
            assert doc[field] is False, field
        assert doc['new_tests_executed'] == doc['functional_campaigns_executed'] == 0
        assert doc['semantic_baseline'] == 'P0;83 SUPPORTS_BOUNDED/1 PARTIAL'
        assert doc['remaining_partial_parts'] == ['UI04.1']
    checked = set()
    for mapping in (c['inputs'], seal['prior_local_files'], seal['artifacts']):
        for path, sha in mapping.items():
            assert not Path(path).is_absolute() and '..' not in Path(path).parts
            assert not path.startswith('dev/run_data/'), path
            assert digest(path) == sha, path
            checked.add(path)
    assert len(seal['prior_local_files']) == 32
    assert len(seal['artifacts']) == 6
    expected = set(r['manifest_design']['dossier_names'])
    assert expected == set(seal['artifacts']) | {PREFIX+'integrity.json'}
    assert set(git('ls-files','--others','--exclude-standard').splitlines()) == set(seal['prior_local_files']) | expected

    # Source tree only: the method is selected by its reviewed existing binding.
    tree = ast.parse((ROOT/'testing/D5/test_durable_relational.py').read_text())
    method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'dr37')
    loops = [n for n in method.body if isinstance(n, ast.For)]
    counts = [len(n.iter.elts) for n in loops]
    assert counts == [4,13,2], counts
    assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'subTest' for n in ast.walk(method))
    last = method.body[-1]
    expected_call = ast.parse("self.error('SOURCE_BUDGET',lab.client.capture,b'x'*(2097152+1))").body[0]
    assert ast.dump(last, include_attributes=False) == ast.dump(expected_call, include_attributes=False)
    assert sum(counts)+1 == 20
    shape = read('docs/validation/D5-I116-projection-row-envelopes.json')
    assert c['source_binding'] == shape['role_method_bindings'][c['source_case']]
    assert shape['maximum_group_witnesses'] == 40
    uuid_source = Path(importlib.util.find_spec('uuid').origin)
    assert hashlib.sha256(uuid_source.read_bytes()).hexdigest() == c['stdlib_uuid_source']['sha256']
    uuid_tree = ast.parse(uuid_source.read_text())
    uuid4 = next(n for n in uuid_tree.body if isinstance(n, ast.FunctionDef) and n.name == 'uuid4')
    assert any(isinstance(n,ast.Attribute) and n.attr == 'urandom' for n in ast.walk(uuid4))

    group = c['minimal_distinct_ref_shape']
    witnesses = group['witnesses']
    assert len(witnesses) == len({x['object_ref'] for x in witnesses}) == 40
    assert [x['object_ref'] for x in witnesses] == sorted('O'+str(i) for i in range(1,41))
    assert sorted(len(x['authorities']) for x in witnesses) == [1]*20+[2]*20
    assert len(encoded(group)) == c['encoded_lower_bound'] == 4123 > c['row_limit'] == 4096
    assert c['excess_lower_bound'] == 27 and not c['actual_P01_excess_measured']
    assert not c['UUID_uniqueness_assumed'] and not c['normal_unique_ID_path_proven_to_overflow']
    # Minimum width proof: empty row, 20 two-authority + 20 one-authority
    # witnesses with O1, delimiters, and 31 additional digits for O10..O40.
    empty = copy.deepcopy(group);empty['witnesses'] = []
    one = dict(object_ref='O1',authorities=witnesses[0]['authorities'])
    other = dict(object_ref='O1',authorities=witnesses[-1]['authorities'])
    assert len(one['authorities']) == 2
    # O9 is a Store, so select the facade authority explicitly.
    other['authorities'] = ['OBSERVED_PARENT_RETURN']
    assert len(encoded(empty)) + 20*len(encoded(one)) + 20*len(encoded(other)) + 39 + 31 == 4123

    records = d['example_records']; new = d['example_new_group']
    assert len(records) == len(new['witness_record_refs']) == 40
    rebuilt = copy.deepcopy(new);rebuilt['schema'] = 'd5.domain-witness-group.v1'
    refs = rebuilt.pop('witness_record_refs')
    assert len(set(refs)) == len(refs) and set(refs) == set(records)
    for key in refs:
        assert records[key]['witness_ref'] == key
        assert records[key]['group_ref'] == new['group_ref']
        assert records[key]['schema'] == 'd5.domain-witness-record.v1'
    rebuilt['witnesses'] = [dict(object_ref=records[k]['object_ref'],authorities=records[k]['authorities']) for k in refs]
    assert encoded(rebuilt) == encoded(group) == encoded(d['example_old_group'])
    assert d['example_roundtrip_bytes_equal']
    assert len(encoded(d['group_row_majorant'])) == d['group_row_bytes_upper'] == 714
    assert len(encoded(d['record_row_majorant'])) == d['record_row_bytes_upper'] == 212
    prior = read('docs/validation/D5-I115-refined-reference-envelope.json')
    saving = sum(4*x['primitives']['I']*max(0,x['primitives']['W']-40) for x in prior['root_rows'])
    charge = d['charging']
    assert len(prior['root_rows']) == 321
    assert saving == charge['copy_weight_refinement_saving'] == 146336
    assert prior['witness_memberships_upper'] == 9285
    assert charge['extra_upper'] == 4*9285 == 37140
    assert charge['source_R2_upper'] == 442305-saving+4*9285 == 333109
    assert charge['headroom'] == 442305-333109 == 109196
    assert charge['causal_key_upper'] == 37651+9285 == 46936
    assert len('Y'+str(charge['causal_key_upper'])) == charge['causal_key_chars'] == 6
    assert d['numeric_candidates'] == read('docs/validation/D5-I115-joint-capacity-proposal.json')['candidate_limits']
    assert len(d['numeric_candidates']) == 24 and not d['quota_values_changed']
    assert len(d['synthetic_matrix']) == 10 and all(x['status']=='NOT_RUN' for x in d['synthetic_matrix'])
    assert not d['implementation_authorized'] and not d['capture_authorized']
    assert not d['numeric_joint_capacity_certificate_created'] and d['components_executed']==0

    for key, model in d['component_width_majorants'].items():
        assert len(encoded(model['value'])) + model['container_overhead'] == model['encoded_with_container_overhead'], key
        assert model['encoded_with_container_overhead'] <= model['allowance'], key
    cells = d['sidecar_components']
    assert len(cells) == 13
    assert cells['groups']['upper'] == 6615*600 + 9285*(10+300)
    assert cells['protocols']['upper'] == 718*2048 + 934*2304 + 1438*128
    assert cells['fixture_declarations']['upper'] == 2*256
    unchanged = read('docs/validation/D5-I115-structural-byte-plan.json')['sidecar_components']
    for name in cells.keys()-{'groups','protocols','fixture_declarations'}:
        assert cells[name]['upper'] == unchanged[name]['upper'], name
    assert sum(x['upper'] for x in cells.values()) == d['conditional_structural_sidecar_upper'] == 30996862
    assert d['sidecar_candidate_limit'] == 35651584
    assert d['sidecar_plan_headroom'] == 35651584-30996862 == 4654722
    assert len(encoded(d['protocol_closed_source_majorant']['value'])) == d['protocol_closed_source_majorant']['encoded_bytes'] == 3672 < 4096
    top = d['component_width_majorants']['top_metadata']['value']
    assert len(top['pages']) == 32 and len(top['groups']) == 12
    assert top['capture_inputs_before'] == top['capture_inputs_after'] and len(top['capture_inputs_before']) == 484
    assert top['domain_witness_records'] == {} and top['domain_witness_groups'] == {}
    event = d['I117_event_padding']
    assert len(encoded(event['value'])) == event['encoded_bytes'] == 3546
    page = event['refined_page_envelope']
    n = sum(page['category_counts'][k]*(size+1) for k,size in page['category_bytes'].items())
    pages = n//(2097152-256-3547)+1
    assert n == page['chunks_and_commas_upper'] == 58862755
    assert pages == page['pages_upper'] == 29
    assert n+256*pages == page['total_page_bytes_upper'] == 58870179 < 67108864
    assert sum(page['category_counts'].values()) == 30129

    # Bind arithmetic to the original expression and the observer's own grammar.
    product_tree = ast.parse((ROOT/'source_ingest/durable_relational_fixture.py').read_text())
    client = next(n for n in product_tree.body if isinstance(n,ast.ClassDef) and n.name=='Client')
    capture = next(n for n in client.body if isinstance(n,ast.FunctionDef) and n.name=='capture')
    expected_return = ast.parse("return self.perform('CAPTURE',dict(content_base64=base64.b64encode(raw).decode()))").body[0]
    assert ast.dump(capture.body[-1],include_attributes=False)==ast.dump(expected_return,include_attributes=False)
    selectors = ast.parse((ROOT/'testing/prospective_capture_selectors/capture.py').read_text())
    token = next(n for n in selectors.body if isinstance(n,ast.FunctionDef) and n.name=='token')
    grammar = next(n.value for n in ast.walk(token) if isinstance(n,ast.Constant) and isinstance(n.value,str) and '{1,128}' in n.value)
    assert grammar == r'[A-Za-z0-9_.:/+\-]{1,128}'
    reg = read('docs/validation/D5-SELECTOR-CAPTURE-REGISTRY.json')
    actions = [x['action'] for x in reg['parental_contract']['child_action_policies']] + ['Drive.advance']
    assert max(map(len,actions)) <= 16 and all(re.fullmatch(grammar,x) for x in actions)
    request = next(n for n in selectors.body if isinstance(n,ast.FunctionDef) and n.name=='store_request')
    expected_budget = ast.parse("args_digest['bytes'] + op_digest['bytes'] + len(body) <= dict(LIMITS, **(limits or {}))['operand_bytes']", mode='eval').body
    assert any(isinstance(n,ast.Compare) and ast.dump(n,include_attributes=False)==ast.dump(expected_budget,include_attributes=False) for n in ast.walk(request))
    assert o['input_bytes'] == 2097152+1
    assert o['base64_ascii_chars'] == 4*((o['input_bytes']+2)//3) == 2796204
    args = o['abstract_args'];op=o['abstract_op']
    assert digest_size((('CAPTURE',args),{})) == o['wrapper_digest_upper'] == 2796269
    assert digest_size(args) == o['args_digest_upper'] == 2796236
    assert digest_size(op) == o['op_digest_upper'] == 2796401
    assert json_size(op) == o['canonical_op_upper'] == 2796358
    assert digest_size(args)+digest_size(op)+json_size(op) == o['store_request_combined_upper'] == 8388995 < o['operand_limit'] == 16777216
    assert not o['global_CP03_resolved'] and not o['larger_universal_bound_claimed']

    union = sum((ROOT/p).stat().st_size for p in c['inputs'])
    assert union == r['existing_documentary_union']['unique_bytes'] == 84080766
    assert max((ROOT/p).stat().st_size for p in c['inputs']) == r['existing_documentary_union']['maximum_file_bytes'] == 9755833
    naive = 160864585+2*(union-63104330)+union
    assert naive == r['naive_inheritance']['upper'] == 286898223
    assert not r['naive_inheritance']['actual_excess_proven']
    assert r['existing_recheck_upper'] == 160864585-156012125 == 4852460
    base = 3*union+r['existing_recheck_upper']
    assert base == r['base_worker_three_phase_upper'] == 257094758
    assert r['remaining_weighted_bytes'] == 268435456-base == 11340698
    assert r['conditional_S_max_if_X_proven_zero'] == 11340698//3 == 3780232
    assert not r['zero_extras_proven'] and not r['CP07_exact_binding_resolved']
    assert r['unknowns']['S_new_unique_file_bytes'] is None and r['unknowns']['X_new_extra_read_bytes'] is None
    assert r['unknowns']['new_source_hashes'] is None
    manifest = d['fixed_manifest_plan']
    assert manifest == r['manifest_design']
    assert len(manifest['dossier_names']) == 7 and len(manifest['future_fixed_names']) == 12
    assert manifest['authority_path'] is None and manifest['future_hashes'] is None
    assert manifest['total_paths_upper'] == 464+7+12+1 == 484
    assert not any((ROOT/p).exists() for p in manifest['future_fixed_names'])
    assert not r['actual_reader_or_profile_changed']
    for link in re.findall(r'\]\(([^)]+)\)', (ROOT/'docs/design/D5-I117-PJC115-R2-CAPACITY-REVIEW.md').read_text()):
        assert (ROOT/'docs/design'/link).resolve().is_file(), link
    dossier_bytes = sum((ROOT/p).stat().st_size for p in expected)
    print(json.dumps(dict(status='DOCUMENTARY_HASH_AST_JSON_ARITHMETIC_PASS_NOT_PRODUCT_EXECUTION',
        input_pins=464,prior_local_files=32,I117_files=7,verified_paths=len(checked),
        old_group_lower=4123,R2_group_upper=714,R2_record_upper=212,
        R2_ref_upper=333109,R2_sidecar_upper=30996862,projected_page_bytes=58870179,
        reader_base=257094758,reader_weighted_margin=11340698,
        I117_dossier_bytes=dossier_bytes,future_S_and_X='UNKNOWN',
        CP03='GLOBAL_OPEN',CP07='EXACT_OPEN',PJC115_enabled=False,R2_enabled=False,
        IR03='NOT_READY',D5_closed=False)))

if __name__ == '__main__':
    main()
