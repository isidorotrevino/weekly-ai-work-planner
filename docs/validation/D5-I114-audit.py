#!/usr/bin/env python3
"""Read-only I114 documentary audit; stdlib only, no product imports/execution.
Run from any directory with: python3 /absolute/path/to/D5-I114-audit.py
Hashes/AST/arithmetic are checked; source applicability reasoning remains reviewable
in the JSON/Markdown and is not promoted to a machine-proved semantic theorem.
"""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
verified = {}

def read(name):
    return json.loads((ROOT / name).read_text())

def check_hash(name, expected):
    path = Path(name)
    assert not path.is_absolute() and '..' not in path.parts, name
    assert not name.startswith('dev/run_data/'), name
    assert re.fullmatch('[0-9a-f]{64}', expected), name
    actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    assert actual == expected, name
    if name in verified:
        assert verified[name] == expected, name
    verified[name] = expected

def check_map(mapping):
    for name, digest in mapping.items():
        check_hash(name, digest)


def main():
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == '50c49678568bae2abeefbe5fec0285f26c628283'
    subprocess.run(['git', 'diff', '--exit-code', '--quiet'], cwd=ROOT, check=True)
    subprocess.run(['git', 'diff', '--cached', '--exit-code', '--quiet'], cwd=ROOT, check=True)
    h = read('docs/validation/D5-I113-handoff-integrity.json')
    for key in ('artifacts', 'preserved_local_artifacts', 'prior_integrity_seals'):
        check_map(h[key])
    for name in h['prior_integrity_seals']:
        check_map(read(name).get('artifacts', {}))
    r = read('docs/validation/D5-I114-reference-source-envelope.json')
    j = read('docs/validation/D5-I114-joint-resource-envelope.json')
    for doc in (r, j):
        check_map(doc['inputs'])
        for key in ('product_or_runner_imported', 'implementation_changed', 'quota_changed', 'functional_profile_created', 'future_capture_authority_or_destination_created', 'publication_authorized', 'D5_closed', 'H07_closed', 'closure'):
            assert doc[key] is False, key
        assert doc['new_tests_executed'] == doc['functional_campaigns_executed'] == 0
        assert doc['IR03'] == 'NOT_READY'
        assert doc['numeric_joint_capacity_certificate_created'] is False
    E, F = 30129, 321
    assert r['reused_global_event_upper'] == E and r['reused_root_frames'] == F
    assert r['event_bound_recomputed'] is False
    A, D, U = 5 * E + 7, 3 * E, 26 * E + F + 8
    assert sum(t['upper'] for t in r['context_origin_terms']) == U == r['context_entry_upper']
    expected = {
        'Q07': A, 'Q08': E, 'Q09': 2*E, 'Q10': E, 'Q11': E,
        'Q12': 2, 'Q13': 2, 'Q14': E, 'Q15': F+F*A, 'Q16': E,
        'Q17': 2, 'Q18': 1, 'Q19': 3*U+9*E+2, 'Q20': A,
        'Q23': 4*E+4, 'Q24': E, 'Q25': 1, 'Q26': 2*E,
        'Q27': 2, 'Q28': 1, 'Q29': 2, 'Q30': D, 'Q31': D,
        'Q32': 2*D, 'Q33': D, 'Q34': E*(1+D), 'Q35': 2*E,
        'Q36': E*(1+D), 'Q37': 6*E, 'Q38': 2*E*(1+D),
    }
    original = read('docs/validation/D5-I96-source-capacity-review.json')['charging_catalog']
    active = {q['id']: q for q in original if q['active']}
    assert set(expected) == set(active) and len(expected) == 30
    assert r['inactive_sites'] == [q['id'] for q in original if not q['active']]
    assert len(r['inactive_sites']) == 8
    assert len(r['active_sites']) == r['active_site_count'] == 30
    assert {q['site']: q['total_charge_upper'] for q in r['active_sites']} == expected
    assert sum(expected.values()) == r['source_global_reference_upper'] == 10945598127
    assert r['source_global_reference_lower'] == 19037 > r['current_reference_limit'] == 16384
    trees = {}
    for q in r['active_sites']:
        orig = active[q['site']]
        for key in ('path', 'sha256', 'owner', 'method', 'line', 'charge_expression'):
            assert q[key] == orig[key], (q['site'], key)
        check_hash(q['path'], q['sha256'])
        trees.setdefault(q['path'], ast.parse((ROOT / q['path']).read_text()))
        assert any(isinstance(n, ast.Call) and n.lineno == q['line'] and isinstance(n.func, ast.Attribute) and n.func.attr in ('reference', 'charge', 'on_reference') for n in ast.walk(trees[q['path']])), q['site']
    for a in r['source_anchors']:
        check_hash(a['path'], a['sha256'])
        if a['path'] not in trees:
            trees[a['path']] = ast.parse((ROOT / a['path']).read_text())
        assert any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and (n.name, n.lineno, n.end_lineno) == (a['method'], a['line'], a['end_line']) for n in ast.walk(trees[a['path']])), a
    # This audit must never acquire an import dependency on a product/runner module.
    audit_tree = ast.parse(Path(__file__).read_text())
    imports = [n for n in ast.walk(audit_tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
    allowed = {'ast', 'hashlib', 'json', 'pathlib', 're', 'subprocess'}
    for n in imports:
        names = [a.name for a in n.names] if isinstance(n, ast.Import) else [n.module]
        assert all(name in allowed for name in names), names
    pages = j['page_packing']
    B, L, H = 4096, 2097152, 256
    enc = lambda v: json.dumps(v, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode()
    header = dict(schema='d5.capture-event-page.v1', capture_run_id='0'*36, page_index=E, first_sequence=E, last_sequence=E, event_count=E)
    overhead = len(enc(header)) + len(b',"events":[]}') - 1
    assert overhead == pages['monotone_header_extreme_bytes'] == 189 <= H
    P = E*(B+1)//(L-H-(B+1)) + 1
    total = E*(B+1)+P*H
    assert P == pages['pages_upper'] == 59
    assert total == pages['page_bytes_sum_upper'] == 123453617
    assert E*2224//(L-H-2224)+1 == 32
    assert E*2224+32*H == pages['sufficient_refinement']['page_bytes_sum_upper'] == 67015088
    assert E*2225//(L-H-2225)+1 == 33
    inv = j['original_input_inventory']
    check_map(inv['pins'])
    assert len(inv['pins']) == inv['paths'] == 293
    assert sum((ROOT/p).stat().st_size for p in inv['pins']) == inv['unique_bytes'] == 63104330
    assert max(((ROOT/p).stat().st_size, p) for p in inv['pins']) == (9755833, inv['maximum_file']['path'])
    assert inv['maximum_file']['bytes'] == 9755833 < 16777216
    resources = {q['resource']: q for q in j['resource_rows']}
    previous = {q['resource']: q['current_limit'] for q in read('docs/validation/D5-I108-global-capacity-functional-readiness.json')['resource_rows']}
    assert len(resources) == j['resource_count'] == 24
    assert {k: v['current_limit'] for k, v in resources.items()} == previous
    assert resources['refs']['available_bound'] == r['source_global_reference_upper']
    assert resources['pages']['available_bound'] == P
    assert resources['event_pages_total_bytes']['available_bound'] == total
    assert resources['input_file_bytes']['available_bound'] == 9755833
    for key in ('event_bytes', 'page_bytes', 'operand_bytes', 'raw_bytes', 'index_sidecar_bytes', 'context_bytes', 'launch_bytes', 'depth', 'string'):
        assert resources[key]['available_bound'] is None, key
    assert 2*12582912+67108864+36 == resources['evidence_unique_bytes']['available_bound'] == 92274724
    assert 4*12582912+3*67108864+36 == resources['evidence_read_bytes']['available_bound'] == 251658276
    assert 64*1024**2+4*12*1024**2+36 == j['original_package_admission']['bytes_upper'] == 117440548
    assert 117444608 - 117440548 == j['original_package_admission']['headroom'] == 4060
    links = re.findall(r'\]\(([^)]+)\)', (ROOT/'docs/design/D5-I114-REFERENCES-AND-JOINT-BYTES.md').read_text())
    for link in links:
        assert (ROOT/'docs/design'/link).resolve().is_file(), link
    seal = read('docs/validation/D5-I114-integrity.json')
    check_map(seal['artifacts'])
    print(json.dumps(dict(status='DOCUMENTARY_HASH_AST_ARITHMETIC_CHECKS_PASS_NOT_FUNCTIONAL_TESTS', input_pins=len(r['inputs']), verified_unique_paths=len(verified), active_charge_sites=30, source_method_anchors=len(r['source_anchors']), resource_rows=24, product_imports=0, functional_campaigns=0, joint_capacity='NOT_ESTABLISHED', IR03='NOT_READY'), ensure_ascii=False))

if __name__ == '__main__':
    main()
