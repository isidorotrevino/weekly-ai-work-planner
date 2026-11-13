#!/usr/bin/env python3
"""I152 H07 review: Git/JSON/AST only, without target execution or probes."""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '187871af4e964711f9226952407cdb7414c838b6'
OUT = P + 'D5-PFC126-03-E02-H07.json'
REVIEW = P + 'D5-I151-P04-H07-preparation-review.json'
SEAL = P + 'D5-I151-integrity.json'
AUDIT = P + 'D5-I151-audit.py'
DESIGN = 'docs/design/D5-I151-P04-H07-JSON-UNICODE-CODEC-HEAP.md'
PLAN = P + 'D5-I132-E01-E05-evidence-plan.json'
CONTRACT = P + 'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
SCOPE = P + 'D5-PFC126-03-RESOURCE-SCOPE.json'
RUNTIME = P + 'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
PLATFORM = P + 'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
I124 = P + 'D5-I124-global-batch-lifetime-proof.json'
ATOMIC = 'testing/prospective_capture_joint_i122/atomic.py'
JOINT = 'testing/prospective_capture_joint_i122/capture.py'
TYPED = 'testing/prospective_capture_typed/capture.py'
CAPTURE = 'testing/prospective_capture/capture.py'
H06 = P + 'D5-PFC126-03-E02-H06.json'
WORKER = 'testing/prospective_capture_joint_i122/worker.py'
PROJECTIONS = [
    (CONTRACT, '/heap/owner_budgets/6'),
    (P + 'D5-I125-complete-heap-review.json', '/required_terms/6'),
    (P + 'D5-I123-transient-resource-envelope.json', '/memory'),
    (I124, '/scope'), (I124, '/lifetime_envelope'), (RUNTIME, '/acceptance'),
    (PLATFORM, '/acceptance'), (P + 'D5-I150-P04-H06-documentary-review.json', '/acceptance'),
    (H06, '/overlap_alias_original_and_rejected_prefix_treatment'),
    (SCOPE, '/worker_heap_vs_other_process_scope'), (CONTRACT, '/product_numeric_candidates'),
    (P + 'D5-I124-resource-admission-review.json', '/remaining_for_actual_admission'),
]
SPECS = [
    (CAPTURE, 'strict_json'), (CAPTURE, 'strict_json.pairs'),
    (CAPTURE, 'strict_json.check'), (CAPTURE, 'strict_json.reject'),
    (CAPTURE, 'digest_value.visit'), (CAPTURE, 'BoundedOutput.write'),
    (CAPTURE, 'write_json_fd'), (TYPED, 'encode'), (TYPED, 'canonical'),
    (TYPED, 'Projector.observe.visit'), (TYPED, 'PageSink.append'),
    (JOINT, 'bounded_builtin'), (JOINT, 'canonical_hash'), (JOINT, 'drive_request'),
    (JOINT, 'SideWriter.write'), (JOINT, 'read_sidecar'),
    (JOINT, 'scoped_projection_schemas'), (JOINT, 'canonical_metadata'),
    (ATOMIC, 'build.Recorder._typed_finish'), (ATOMIC, 'build.Pages.flush'),
    (WORKER, 'exercise'), (WORKER, 'main'),
]
CENSUS = ['Call', 'List', 'Tuple', 'Dict', 'Set', 'ListComp', 'SetComp',
          'DictComp', 'GeneratorExp', 'ExceptHandler']
# Lexical evidence only; the first relation deliberately records an earlier guard.
ORDERS = [
    (CAPTURE, 'strict_json', 'require(len(data)', "data.decode('utf8')"),
    (CAPTURE, 'strict_json', 'out = json.loads(', 'check(out)'),
    (CAPTURE, 'strict_json.pairs', 'd = {}', 'require(k not in d'),
    (JOINT, 'SideWriter.write', 'body = encode(value)', 'c.require(len(body)'),
    (CAPTURE, 'BoundedOutput.write', "b = value.encode('utf8')", 'require(self.count + len(b)'),
    (CAPTURE, 'write_json_fd', 'b = json.dumps(', 'require(len(b)'),
    (ATOMIC, 'build.Recorder._typed_finish', 'out = dict(', "len(encode(out)) > self.limits['index_sidecar_bytes']"),
    (JOINT, 'canonical_metadata', 'value = c.strict_json(body)', 'fault(body in'),
]
FACTS = [
    (TYPED, 'encode', "json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf8')"),
    (TYPED, 'canonical', "json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(',', ':')).encode('ascii')"),
    (JOINT, 'scoped_projection_schemas', 'out = json.loads(json.dumps(base))'),
    (WORKER, 'exercise', 'raw = c.strict_json(stdout.getvalue().encode())'),
    (JOINT, 'read_sidecar', "side = c.strict_json(body, dict(c.LIMITS, file_bytes=LIMITS['index_sidecar_bytes']))"),
    (CAPTURE, 'strict_json', "data.decode('utf8')"),
    (JOINT, 'canonical_metadata', 'encode(value)'),
    (CAPTURE, 'strict_json.pairs', 'd[k] = v'),
]


def rd(path):
    return json.loads((ROOT / path).read_text())


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def digest(value):
    body = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(body.encode()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def pointer(value, ptr):
    for key in ptr.strip('/').split('/'):
        key = key.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def mark(node):
    return dict(kind=type(node).__name__, line=node.lineno, column=node.col_offset,
                end_line=node.end_lineno, AST_sha256=hashlib.sha256(
                    ast.dump(node, include_attributes=False).encode()).hexdigest())


def evidence(pins):
    paths = sorted(pins)
    request = ''.join(BASE + ':' + path + '\n' for path in paths).encode()
    stream = io.BytesIO(subprocess.check_output(['git', 'cat-file', '--batch'], cwd=ROOT, input=request))
    blobs, checks = {}, []
    for path in paths:
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', path
        body = stream.read(int(header[2]))
        assert len(body) == int(header[2]) and stream.read(1) == b'\n'
        assert hashlib.sha256(body).hexdigest() == pins[path] == sha(path), path
        blobs[path] = body
        checks.append(dict(path=path, git_blob_oid=header[0], bytes=len(body), sha256=pins[path]))
    assert not stream.read()
    scope = json.loads(blobs[SCOPE])['I122_and_original_source_pin_set']
    sources = {**scope['runner_registered_input_pins'],
               **scope['observer_static_repo_import_superset']['file_pins']}
    sources = {p: h for p, h in sources.items() if p.endswith('.py')}
    indices, summaries, vector = {}, [], []
    for path, h in sorted(sources.items()):
        assert pins[path] == h
        tree = ast.parse(blobs[path].decode())
        index = {}

        class Lexical(ast.NodeVisitor):
            def __init__(self):
                self.parts = []

            def record(self, node):
                self.parts.append(node.name)
                index.setdefault('.'.join(self.parts), []).append(node)
                self.generic_visit(node)
                self.parts.pop()

            visit_ClassDef = record
            visit_FunctionDef = record
            visit_AsyncFunctionDef = record

        Lexical().visit(tree)
        indices[path] = index
        rows = [mark(n) for n in ast.walk(tree) if type(n).__name__ in CENSUS]
        rows.sort(key=lambda r: (r['line'], r['column'], r['kind']))
        summaries.append(dict(path=path, sha256=h, syntax_counts={
            k: sum(r['kind'] == k for r in rows) for k in CENSUS}, site_vector_sha256=digest(rows)))
        vector.extend(dict(path=path, **r) for r in rows)
    nodes, anchors = {}, []
    for path, symbol in SPECS:
        assert len(indices[path][symbol]) == 1, (path, symbol)
        node = indices[path][symbol][0]
        nodes[(path, symbol)] = node
        anchors.append(dict(path=path, sha256=sources[path], symbol=symbol, **mark(node)))

    def matches(path, symbol, text, exact=False):
        return [n for n in ast.walk(nodes[(path, symbol)]) if not isinstance(n, ast.Expr)
                if (ast.unparse(n) == text if exact else ast.unparse(n).startswith(text))]

    orders = []
    for path, symbol, before, after in ORDERS:
        first, second = matches(path, symbol, before), matches(path, symbol, after)
        assert len(first) == len(second) == 1, (symbol, before, after, len(first), len(second))
        a, b = first[0], second[0]
        assert (a.lineno, a.col_offset) < (b.lineno, b.col_offset)
        orders.append(dict(path=path, symbol=symbol, earlier_expression_prefix=before,
                           later_expression_prefix=after, before=mark(a), after=mark(b),
                           lexical_order_only_not_allocation_upper=True))
    facts = []
    for path, symbol, text in FACTS:
        found = matches(path, symbol, text, exact=True)
        assert found, (symbol, text)
        facts.append(dict(path=path, symbol=symbol, expression=text,
                          sites=sorted([mark(n) for n in found], key=lambda r: (r['line'], r['column'])),
                          not_dynamic_invocations_or_bytes=True))
    projections = []
    for path, ptr in PROJECTIONS:
        value = pointer(json.loads(blobs[path]), ptr)
        projections.append(dict(path=path, sha256=pins[path], json_pointer=ptr,
                                observed_value=value, canonical_sha256=digest(value), resource_obligation_closed=False))
    counts = json.loads(blobs[I124])
    f, s = counts['global_F_upper'], counts['global_S_upper']
    assert (f, s, f+s, 1+f+s) == (52018, 1759, 53777, 53778)
    return dict(commit=BASE, input_pin_count=len(pins), input_blob_checks=checks,
                projections=projections, source_file_count=len(sources), source_pins=sources,
                source_file_summaries=summaries, syntax_counts={
                    k: sum(r['kind'] == k for r in vector) for k in CENSUS},
                site_vector_sha256=digest(vector), source_anchors=anchors,
                lexical_order_witnesses=orders, allocation_expression_witnesses=facts,
                inherited_count_reference=dict(F_upper=f, S_upper=s, clone_batches_upper=f+s,
                    generations_including_initial_upper=1+f+s, not_codec_operation_or_live_tree_counts=True),
                candidate_numeric_limits=json.loads(blobs[CONTRACT])['product_numeric_candidates'],
                no_target_import_execution_compilation_introspection_or_sampling=True)


def codec_spelling_evidence(pins):
    """A spelling index, deliberately not resolved codec dispatch or closure."""
    scope = rd(SCOPE)['I122_and_original_source_pin_set']
    sources = {**scope['runner_registered_input_pins'],
               **scope['observer_static_repo_import_superset']['file_pins']}
    spellings = ['json.dumps', 'json.loads', 'json.dump', 'json.load',
                 'attribute.encode', 'attribute.decode', 'attribute.iterencode']
    summaries, all_sites = [], []
    for path, h in sorted(sources.items()):
        if not path.endswith('.py'):
            continue
        assert sha(path) == pins[path] == h
        rows = []
        for node in ast.walk(ast.parse((ROOT/path).read_text())):
            if not isinstance(node, ast.Call):
                continue
            name = ast.unparse(node.func)
            spelling = name if name in spellings[:4] else (
                'attribute.' + node.func.attr if isinstance(node.func, ast.Attribute)
                and node.func.attr in ['encode','decode','iterencode'] else None)
            if spelling is not None:
                rows.append(dict(spelling=spelling, expression=ast.unparse(node), **mark(node)))
        rows.sort(key=lambda r: (r['line'], r['column'], r['spelling']))
        summaries.append(dict(path=path, sha256=h, counts={k:sum(r['spelling']==k for r in rows)
                              for k in spellings}, site_vector_sha256=digest(rows)))
        all_sites.extend(dict(path=path, **r) for r in rows)
    return dict(source_file_count=len(summaries), file_summaries=summaries,
        counts={k:sum(r['spelling']==k for r in all_sites) for k in spellings},
        site_vector_sha256=digest(all_sites),
        attribute_spelling_not_runtime_codec_resolution_or_complete_inventory=True)


def validate_preparation():
    o, r, seal = rd(OUT), rd(REVIEW), rd(SEAL)
    c, scope, plan = rd(CONTRACT), rd(SCOPE), rd(PLAN)
    task = next(t for t in plan['tasks'] if t['id'] == 'P04-H07')
    owner = c['heap']['owner_budgets'][6]
    expected = {OUT, REVIEW, AUDIT, SEAL, DESIGN}
    prior = rd(P+'D5-I150-integrity.json')
    preserved = {**prior['preserved_published228'], **prior['artifacts'],
                 P+'D5-I150-integrity.json': sha(P+'D5-I150-integrity.json')}
    assert len(preserved) == 233 and seal['preserved_published233'] == preserved
    assert set(seal['artifacts']) | {SEAL} == expected
    for pins in [preserved, seal['artifacts'], o['input_pins'], r['input_pins'],
                 rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for path, h in pins.items():
            assert sha(path) == h, path
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    assert o['base_commit'] == r['base_commit'] == seal['base_commit'] == BASE
    assert o['date'] == r['date'] == seal['date'] == '2026-11-13'
    assert o['package_id'] == task['id'] == 'P04-H07'
    assert o['schema'] == task['output_schema'] and OUT == task['planned_output']
    assert r['schema'] == 'd5.i151-p04-h07-preparation-review.v1'
    assert seal['schema'] == 'd5.i151-integrity.v1'
    assert o['status'] == 'PREPARED_INSUFFICIENT_JSON_UNICODE_CODEC_HEAP_H07_E02_OPEN_NOT_ADMITTED'
    assert r['status'] == 'P04_H07_PREPARATION_COMPLETE_NO_COMPLETE_BOUND_NO_ADMISSION'
    assert o['plan_binding'] == dict(path=PLAN,sha256=sha(PLAN),package_id=task['id'],task_record_canonical_sha256=digest(task))
    assert o['candidate_binding'] == dict(path=CONTRACT,sha256=sha(CONTRACT),contract_id=c['contract_id'],subject=c['subject'],source_revision='I122-CANDIDATE-01')
    assert len(task['required_specific_fields']) == 9 and set(task['required_specific_fields']) <= set(o)
    assert o['candidate_owner_record'] == owner and owner['id'] == 'H07' and owner['proof_upper_bytes'] is None
    assert o['candidate_budget_bytes'] == o['candidate_budget_bytes=268435456'] == owner['candidate_budget_bytes'] == 256*1024**2
    identity = o['owner_id_metric_and_exact_units']
    assert identity['owner_id'] == 'H07' and identity['owner'] == owner['owner']
    assert identity['metric'] == owner['metric'] == 'peak_requested_live_heap'
    assert identity['unit'] == 'exact_integer_bytes' and identity['candidate_budget_bytes'] == 268435456
    assert identity['scope_is_requirement_not_verified_bound']
    assert o['source_evidence'] == evidence(o['input_pins'])
    assert o['codec_call_spelling_evidence'] == codec_spelling_evidence(o['input_pins'])
    e = o['source_evidence']
    assert (e['input_pin_count'],e['source_file_count'],len(e['projections']),len(e['source_anchors'])) == (171,79,12,22)
    assert len(e['lexical_order_witnesses']) == 8 and len(e['allocation_expression_witnesses']) == 8
    abi = o['source_ABI_allocator_dependencies']
    assert abi['historical_runtime_reference'] == c['runtime']
    assert not abi['exact_runtime_ABI_or_allocator_correspondence_verified']
    assert all(abi[k] is None for k in ['accepted_target_closure','unicode_bytes_representation_and_growth_model',
        'json_encoder_decoder_native_workspace_model','pairs_hooks_tree_allocation_model','requested_live_overlap_and_allocator_mapping'])
    inventory = o['complete_live_allocation_inventory']
    assert not inventory['complete'] and len(inventory['required_classes']) == 12
    assert inventory['residual_runtime_native_terms_not_proved_absent']
    for i,row in enumerate(inventory['required_classes'],1):
        assert row['id'] == 'R%02d'%i and row['required_coverage'] and row['runtime_dependency'] and not row['verified']
        assert all(row[k] is None for k in ['cardinality_upper','size_upper_bytes','maximum_live_upper_bytes','lifetime_derivation'])
    d = o['cardinality_size_lifetime_derivations']
    assert not d['complete'] and d['whole_owner_live_upper_bytes'] is None
    assert d['inherited_count_reference'] == e['inherited_count_reference']
    assert all(d[k] for k in ['serialized_bytes_not_complete_codec_heap','post_parse_validation_not_preallocation_cap',
        'earlier_byte_and_depth_guards_preserved','no_fixed_unicode_factor_or_buffer_reuse_assumed',
        'scan_decode_and_parse_overlap_not_assumed_without_lifetime_proof','worker_and_parent_codec_calls_not_implicitly_summed'])
    overlap = o['overlap_alias_original_and_rejected_prefix_treatment']
    assert overlap['inherited_scope'] == scope['worker_heap_vs_other_process_scope']
    assert overlap['source_applicability'] == scope['321_root_12_group_applicability']['I124_applicability']
    assert [x['other_owner'] for x in overlap['boundary_requirements']] == ['H%02d'%i for i in range(1,12) if i != 7]
    assert all(not x['resolved'] for x in overlap['boundary_requirements']) and not overlap['complete_ownership_alias_lifetime_proof']
    dep = o['explicit_assumptions_and_external_dependencies']
    assert not dep['assumptions_verified'] and not dep['P02_exact_runtime_identity_accepted'] and not dep['P03_capacity_service_accepted']
    assert dep['inherited_P01_preconditions'] == scope['321_root_12_group_applicability']['original_source_route_preconditions']
    assert all(dep[k] is None for k in ['complete_codec_operation_and_tree_multiplicity_model',
        'complete_requested_allocation_and_lifetime_theorem','independent_runtime_memory_review'])
    b = o['verified_upper_bytes_and_derivation']
    assert b['verified_upper_bytes'] is None and b['complete_derivation'] is None and not b['verified'] and b['unknown_not_zero']
    assert o['bound_fit_not_just_partial_payload'] == dict(candidate_budget_bytes=268435456,
        verified_complete_upper_bytes=None,fit_result='NOT_EVALUABLE_NO_COMPLETE_H07_BOUND',fits=None,
        slack_bytes=None,overbudget_proved=False,actual_unboundedness_proved=False,partial_payload_not_accepted=True)
    assert [x['field'] for x in o['field_assessment']] == task['required_specific_fields']
    for row in o['field_assessment']:
        definition = row['field'] in ['owner_id_metric_and_exact_units','candidate_budget_bytes=268435456']
        assert row['result'] == ('DOCUMENTARY_DEFINITION_ONLY' if definition else 'INSUFFICIENT_FOR_ACCEPTANCE')
        assert row['basis'] and not row['resource_obligation_closed']
    assert o['acceptance'] == dict(rule=task['acceptance'],rejection_rule=task['rejection'],preparation_complete=True,
        accepted_as_complete_H07_proof=False,H07_verified=False,E02_closed=False,resource_obligations_closed=0,no_reserve_transfer=True)
    assert o['dependencies'] == rd(H06)['dependencies']
    assert [x['id'] for x in o['dependencies']] == task['depends_on'] == ['P01','P02']
    provenance = o['producer_and_review_provenance']
    assert provenance['producer_identity'] == 'Codex assistant preparing I151 in this chat'
    assert provenance['planned_author_role'] == task['responsible_role'] and provenance['planned_review_role'] == task['review_role']
    assert provenance['independent_reviewer_identity'] is None and not provenance['independent_acceptance'] and not provenance['runtime_custodian_authority_claimed']
    assert not rd(RUNTIME)['acceptance']['accepted_as_runtime_identity'] and not rd(PLATFORM)['acceptance']['accepted_as_platform_evidence']
    assert o['reserve_accounting'] == c['reserve_accounting']
    assert o['non_execution_and_zero_transfer_policy'] == scope['non_execution_and_zero_transfer_policy']
    for row,old in zip(o['E02_criterion_disposition'],rd(H06)['E02_criterion_disposition'],strict=True):
        assert row == dict(id=old['id'],inherited_result=old['I149_result'],I151_result=old['I149_result'],closed=False)
    assert r['E02_criterion_disposition'] == o['E02_criterion_disposition']
    assert r['input_pins'] == {**o['input_pins'],OUT:sha(OUT)}
    assert r['output'] == dict(path=OUT,sha256=sha(OUT),schema=o['schema'],evidence_kind=o['evidence_kind'],produced=True)
    assert all(r['preparation_checks'].values())
    assert r['counts'] == dict(required_fields=9,documentary_definition_fields=2,insufficient_fields=7,
        required_allocation_classes=12,unknown_inventory_values=48,owner_boundaries=10,source_files=79,
        source_anchors=22,evidence_projections=12,input_pins=171,lexical_order_witnesses=8,
        allocation_expression_witnesses=8,other_unproduced_packages=10)
    for progress,t in zip(r['package_progress'],plan['tasks'],strict=True):
        exists = t['id'] in ['P01','P02','P03'] + ['P04-H%02d'%i for i in range(1,8)]
        assert (ROOT/t['planned_output']).exists() == progress['output_created'] == exists
        assert progress['package_id'] == t['id'] and progress['path'] == t['planned_output']
        assert progress['sha256'] == (sha(t['planned_output']) if exists else None)
    assert r['independent_review'] == dict(accepted=False,reviewer_identity=None,no_independent_review_fabricated=True)
    assert not any(o['external_material_scope'][k] for k in ['global_absence_claimed','external_contacts_made','runtime_or_platform_sampled'])
    negative = {('complete_H07_bound_verified' if k=='complete_H06_bound_verified' else k):v for k,v in rd(H06)['decision'].items()}
    assert o['decision'] == r['decision'] == negative and o['E06'] == r['E06'] == rd(H06)['E06']
    assert seal['source_only'] and not seal['H07_verified'] and not seal['proposal_enabled'] and not seal['quotas_changed']
    assert not seal['product_or_components_executed'] and not seal['independent_acceptance']
    assert seal['resource_obligations_closed'] == 0 and not seal['D5_closed'] and seal['IR03'] == 'NOT_READY'
    assert r['git_publication']['commit_and_push_all_requested']
    assert set(r['work_unit']['rollback_files']) == expected and r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command'] == 'python3 docs/validation/D5-I151-audit.py'
    assert r['work_unit']['expected_result'] == 'PASS_STATIC_SOURCE_ONLY' and r['work_unit']['diff_budget_note']
    for path in [P+'D5-JOINT-capture-authorization.json',P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:
        assert not (ROOT/path).exists()

REVIEW_BASE = 'd8acb2bf24a2a70240f0bd9cf3fc9a30f1c007a8'
NEW_REVIEW = P + 'D5-I152-P04-H07-documentary-review.json'
RECON = P + 'D5-I152-P04-H07-source-reconstruction.json'
NEW_SEAL = P + 'D5-I152-integrity.json'
NEW_AUDIT = P + 'D5-I152-audit.py'
NEW_DESIGN = 'docs/design/D5-I152-P04-H07-CODEC-HEAP-REVIEW.md'

def read_blobs(commit, paths):
    paths = list(paths)
    request = ''.join(commit + ':' + path + '\n' for path in paths).encode()
    stream = io.BytesIO(subprocess.check_output(['git', 'cat-file', '--batch'], cwd=ROOT, input=request))
    result = {}
    for path in paths:
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', path
        size = int(header[2])
        body = stream.read(size)
        assert len(body) == size and stream.read(1) == b'\n'
        result[path] = (header[0], body)
    assert not stream.read()
    return result


def reconstruct():
    oid, body = read_blobs(REVIEW_BASE, [OUT])[OUT]
    o = json.loads(body)
    assert hashlib.sha256(body).hexdigest() == sha(OUT)
    data = read_blobs(o['base_commit'], sorted(o['input_pins']))
    inputs = []
    for path, h in sorted(o['input_pins'].items()):
        blob_oid, content = data[path]
        assert hashlib.sha256(content).hexdigest() == h == sha(path), path
        inputs.append(dict(path=path, preparation_blob_oid=blob_oid, sha256=h, bytes=len(content)))
    e = o['source_evidence']
    assert [(r['path'], r['json_pointer']) for r in e['projections']] == PROJECTIONS
    projections = []
    for row in e['projections']:
        value = pointer(json.loads(data[row['path']][1]), row['json_pointer'])
        assert value == row['observed_value'] and digest(value) == row['canonical_sha256']
        assert row['sha256'] == o['input_pins'][row['path']]
        projections.append(dict(path=row['path'], json_pointer=row['json_pointer'],
                                recomputed_value_sha256=digest(value), agrees_with_H06=True))
    scope = json.loads(data[SCOPE][1])['I122_and_original_source_pin_set']
    sources = {**scope['runner_registered_input_pins'],
               **scope['observer_static_repo_import_superset']['file_pins']}
    sources = {p: h for p, h in sources.items() if p.endswith('.py')}
    assert sources == e['source_pins'] == json.loads(data[RUNTIME][1])['source_import_surface']['source_pins']
    indices, summaries, vector = {}, [], []
    for path, h in sorted(sources.items()):
        tree = ast.parse(data[path][1].decode())
        index = {}
        pending = [(tree, ())]
        while pending:
            node, prefix = pending.pop()
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                prefix = prefix + (node.name,)
                index.setdefault('.'.join(prefix), []).append(node)
            pending.extend((child, prefix) for child in ast.iter_child_nodes(node))
        indices[path] = index
        sites = sorted([mark(n) for n in ast.walk(tree) if type(n).__name__ in CENSUS],
                       key=lambda x: (x['line'], x['column'], x['kind']))
        summaries.append(dict(path=path, sha256=h, syntax_counts={
            k: sum(r['kind'] == k for r in sites) for k in CENSUS}, site_vector_sha256=digest(sites)))
        vector.extend(dict(path=path, **r) for r in sites)
    totals = {k: sum(r['kind'] == k for r in vector) for k in CENSUS}
    assert summaries == e['source_file_summaries'] and totals == e['syntax_counts']
    assert digest(vector) == e['site_vector_sha256']
    anchors, nodes = [], {}
    for row in e['source_anchors']:
        assert len(indices[row['path']][row['symbol']]) == 1
        node = indices[row['path']][row['symbol']][0]
        assert row == dict(path=row['path'], sha256=sources[row['path']], symbol=row['symbol'], **mark(node))
        nodes[(row['path'], row['symbol'])] = node
        anchors.append(dict(**row, lexical_binding_verified=True))
    assert list(nodes) == SPECS

    def locate(path, symbol, signature):
        found = [n for n in ast.walk(nodes[(path, symbol)])
                 if hasattr(n, 'lineno') and mark(n) == signature]
        assert len(found) == 1, (path, symbol, signature)
        return found[0]

    orders = []
    categories = ['BYTE_GUARD_BEFORE_SCAN_DECODE', 'PARSE_BEFORE_TREE_VALIDATION',
        'HOOK_DICT_BEFORE_DUPLICATE_GUARD', 'ENCODE_BEFORE_BODY_BYTE_GUARD',
        'ENCODE_BEFORE_RAW_BYTE_GUARD', 'ENCODE_BEFORE_OUTPUT_BYTE_GUARD',
        'OUTPUT_DICT_BEFORE_SERIALIZED_SIZE_CHECK', 'PARSE_BEFORE_CANONICAL_FORM_CHECK']
    for i, (row, category) in enumerate(zip(e['lexical_order_witnesses'], categories, strict=True), 1):
        before = locate(row['path'], row['symbol'], row['before'])
        after = locate(row['path'], row['symbol'], row['after'])
        assert ast.unparse(before).startswith(row['earlier_expression_prefix'])
        assert ast.unparse(after).startswith(row['later_expression_prefix'])
        assert (before.lineno, before.col_offset) < (after.lineno, after.col_offset)
        orders.append(dict(id='W%02d'%i, path=row['path'], symbol=row['symbol'], classification=category,
            published_record_sha256=digest(row), before_expression=ast.unparse(before),
            after_expression=ast.unparse(after), source_order_not_allocation_or_lifetime_proof=True))
    expressions = []
    for row in e['allocation_expression_witnesses']:
        for signature in row['sites']:
            assert ast.unparse(locate(row['path'], row['symbol'], signature)) == row['expression']
        expressions.append(dict(path=row['path'], symbol=row['symbol'], expression=row['expression'],
            site_count=len(row['sites']), published_record_sha256=digest(row)))
    codec = o['codec_call_spelling_evidence']
    spellings = ['json.dumps','json.loads','json.dump','json.load',
                 'attribute.encode','attribute.decode','attribute.iterencode']
    codec_files, codec_vector = [], []
    for path,h in sorted(sources.items()):
        rows = []
        for node in ast.walk(ast.parse(data[path][1].decode())):
            if not isinstance(node,ast.Call) or not isinstance(node.func,ast.Attribute):
                continue
            func = node.func
            if isinstance(func.value,ast.Name) and func.value.id=='json' and func.attr in ['dumps','loads','dump','load']:
                spelling = 'json.'+func.attr
            elif func.attr in ['encode','decode','iterencode']:
                spelling = 'attribute.'+func.attr
            else:
                continue
            rows.append(dict(spelling=spelling,expression=ast.unparse(node),**mark(node)))
        rows.sort(key=lambda r:(r['line'],r['column'],r['spelling']))
        codec_files.append(dict(path=path,sha256=h,counts={k:sum(r['spelling']==k for r in rows)
            for k in spellings},site_vector_sha256=digest(rows)))
        codec_vector.extend(dict(path=path,**r) for r in rows)
    codec_counts = {k:sum(r['spelling']==k for r in codec_vector) for k in spellings}
    assert codec_files == codec['file_summaries'] and codec_counts == codec['counts']
    assert len(codec_files) == codec['source_file_count'] == 79
    assert digest(codec_vector) == codec['site_vector_sha256']

    def one(node, expression):
        found = [n for n in ast.walk(node) if not isinstance(n,ast.Expr) and ast.unparse(n)==expression]
        assert len(found)==1,expression
        return found[0]

    def record(node, expression):
        return dict(expression=expression,**mark(one(node,expression)))

    strict = nodes[(CAPTURE,'strict_json')]
    scan = [n for n in ast.walk(strict) if isinstance(n,ast.For) and ast.unparse(n.iter)=="data.decode('utf8')"]
    assert len(scan)==1
    parse = one(strict,'out = json.loads(data, object_pairs_hook=pairs, parse_constant=reject)')
    check = one(strict,'check(out)')
    assert scan[0].end_lineno < parse.lineno < check.lineno
    string_guard = record(nodes[(CAPTURE,'strict_json.check')],"require(len(x) <= lim['string'], 'STRING_BUDGET')")
    pairs = nodes[(CAPTURE,'strict_json.pairs')]
    duplicate_guard = one(pairs,"require(k not in d, 'DUPLICATE_KEY')")
    insertion = one(pairs,'d[k] = v')
    assert (duplicate_guard.lineno,duplicate_guard.col_offset)<(insertion.lineno,insertion.col_offset)
    parser = dict(byte_guard=record(strict,"require(len(data) <= lim['file_bytes'], 'FILE_BUDGET')"),
        scan_loop_AST=mark(scan[0]), depth_guard=record(strict,"require(depth <= lim['depth'], 'JSON_DEPTH')"),
        parse_AST=mark(parse), check_call_AST=mark(check), string_guard=string_guard,
        duplicate_guard_AST=mark(duplicate_guard), hook_insertion_AST=mark(insertion),
        nonfinite_reject=record(nodes[(CAPTURE,'strict_json.reject')],"raise CaptureFault('NONFINITE_JSON')"),
        scan_parse_buffer_reuse_or_simultaneity_unproved=True,
        hook_signature_not_concrete_argument_storage_proof=True)
    writer = nodes[(JOINT,'SideWriter.write')]
    writer_body = one(writer,'body = encode(value)')
    writer_guard = one(writer,"c.require(len(body) <= limit, 'SIDECAR_BUDGET')")
    writer_parse = one(writer,'read_sidecar(body, self.lease, self.pid)')
    writer_write = one(writer,'write_all(self.fd, body)')
    assert writer_body.col_offset < writer_guard.col_offset < writer_parse.col_offset < writer_write.col_offset
    assert writer_body.lineno == writer_guard.lineno == writer_parse.lineno == writer_write.lineno
    worker_main = nodes[(WORKER,'main')]
    worker_write = record(worker_main,"writer.write(side, p.LIMITS['index_sidecar_bytes'])")
    launch_candidates = indices[JOINT]['launch']
    assert len(launch_candidates)==1
    launch_reads = [n for n in ast.walk(launch_candidates[0]) if isinstance(n,ast.Call)
                    and ast.unparse(n.func)=='read_sidecar']
    assert len(launch_reads)==2
    raw = record(nodes[(WORKER,'exercise')],'raw = c.strict_json(stdout.getvalue().encode())')
    finish = record(nodes[(WORKER,'exercise')],'side = rec.finish(raw)')
    assert raw['line'] < finish['line']
    pipelines = dict(worker_raw_parse=raw, worker_finish=finish, worker_side_writer_call=worker_write,
        side_writer_encode_AST=mark(writer_body), side_writer_byte_guard_AST=mark(writer_guard),
        side_writer_parse_AST=mark(writer_parse), side_writer_write_AST=mark(writer_write),
        launcher_read_sidecar_sites=sorted([mark(n) for n in launch_reads],key=lambda r:(r['line'],r['column'])),
        source_context_only_not_complete_process_attribution_or_dispatch_proof=True,
        validation_result_discard_not_prompt_release_or_retained_tree_peak_proof=True)
    counts = json.loads(data[I124][1])
    f,s = counts['global_F_upper'],counts['global_S_upper']
    assert (f,s,f+s,1+f+s)==(52018,1759,53777,53778)
    assert e['inherited_count_reference']==dict(F_upper=f,S_upper=s,clone_batches_upper=f+s,
        generations_including_initial_upper=1+f+s,not_codec_operation_or_live_tree_counts=True)
    unknowns, inventory = [], []
    for i,row in enumerate(o['complete_live_allocation_inventory']['required_classes']):
        for key in ['cardinality_upper','size_upper_bytes','maximum_live_upper_bytes','lifetime_derivation']:
            assert row[key] is None
            unknowns.append('/complete_live_allocation_inventory/required_classes/'+str(i)+'/'+key)
        assert not row['verified']
        inventory.append(dict(id=row['id'],record_sha256=digest(row),complete_count_size_peak_lifetime_unproved=True))
    boundaries = o['overlap_alias_original_and_rejected_prefix_treatment']['boundary_requirements']
    assert all(not r['resolved'] for r in boundaries)
    return dict(preparation_commit=o['base_commit'],published_commit=REVIEW_BASE,
        H07_published_blob_oid=oid,H07_sha256=sha(OUT),input_pin_checks=inputs,
        projection_checks=projections,source_file_count=len(sources),source_pin_vector_sha256=digest(sources),
        file_summary_vector_sha256=digest(summaries),syntax_counts=totals,syntax_site_vector_sha256=digest(vector),
        source_anchor_checks=anchors,classified_order_checks=orders,expression_checks=expressions,
        codec_spelling_counts=codec_counts,codec_file_summary_sha256=digest(codec_files),
        codec_site_vector_sha256=digest(codec_vector),strict_json_source_check=parser,
        worker_and_launcher_source_context_checks=pipelines,inherited_count_reference=e['inherited_count_reference'],
        inventory_checks=inventory,unknown_inventory_pointers=unknowns,
        boundary_record_sha256={r['other_owner']:digest(r) for r in boundaries},
        field_record_sha256={r['field']:digest(o[r['field']]) for r in o['field_assessment']},
        no_runtime_codec_resolution_native_allocation_or_lifetime_proof=True)


def main():
    validate_preparation()
    o,z,r,seal = rd(OUT),rd(RECON),rd(NEW_REVIEW),rd(NEW_SEAL)
    prior = rd(SEAL)
    preserved = {**prior['preserved_published233'],**prior['artifacts'],SEAL:sha(SEAL)}
    expected = {NEW_REVIEW,RECON,NEW_AUDIT,NEW_SEAL,NEW_DESIGN}
    assert len(preserved)==238 and seal['preserved_published238']==preserved
    assert set(seal['artifacts'])|{NEW_SEAL}==expected
    for pins in [preserved,seal['artifacts'],z['input_pins'],r['input_pins']]:
        for path,h in pins.items():
            assert sha(path)==h,path
    assert set(git('diff',REVIEW_BASE,'--name-only').splitlines())|set(
        git('ls-files','--others','--exclude-standard').splitlines())==expected
    if git('rev-parse','HEAD')!=REVIEW_BASE:
        assert not git('diff','HEAD','--name-only')
    assert r['base_commit']==z['base_commit']==seal['base_commit']==REVIEW_BASE
    assert r['date']==z['date']==seal['date']=='2026-11-13'
    assert r['schema']=='d5.i152-p04-h07-documentary-review.v1'
    assert z['schema']=='d5.i152-p04-h07-source-reconstruction.v1'
    assert seal['schema']=='d5.i152-integrity.v1'
    assert z['reconstruction']==reconstruct()
    pins = {**o['input_pins'],OUT:sha(OUT),REVIEW:sha(REVIEW),SEAL:sha(SEAL),AUDIT:sha(AUDIT)}
    assert z['input_pins']==pins and r['input_pins']=={**pins,RECON:sha(RECON)}
    assert r['H07']==dict(path=OUT,sha256=sha(OUT),bytes_preserved=True)
    assert r['plan_binding']==o['plan_binding']
    assert r['source_reconstruction']==dict(path=RECON,sha256=sha(RECON))
    assert r['status']=='REVIEW_COMPLETE_DOSSIER_CONFORMANT_H07_PROOF_REJECTED_NO_ADMISSION'
    assert r['documentary_dossier_conformance'] and not r['H07_change_required']
    assert r['blocking_dossier_defects']==[]
    reviewer = r['reviewer']
    assert reviewer['same_assistant_as_preparer'] and reviewer['methodologically_separate_reconstruction']
    assert not reviewer['actor_independence'] and not reviewer['organizational_independence'] and not reviewer['runtime_custodian_authority']
    assert [check['id'] for check in r['checks']]==['R%02d'%i for i in range(1,16)]
    for check in r['checks']:
        assert check['result']=='CONFORMANT_DOCUMENTARY_INSUFFICIENCY_JUDGMENT'
        assert check['basis'] and not check['resource_obligation_closed']
    assert r['field_disposition']==[dict(field=x['field'],inherited_result=x['result'],
        I152_result=x['result'],field_record_sha256=digest(o[x['field']]),resource_obligation_closed=False) for x in o['field_assessment']]
    assert r['E02_criterion_disposition']==[dict(id=x['id'],inherited_result=x['I151_result'],
        I152_result=x['I151_result'],closed=False) for x in o['E02_criterion_disposition']]
    assert r['acceptance']==dict(review_completed=True,insufficiency_judgment_confirmed=True,
        accepted_as_complete_H07_proof=False,H07_verified=False,independent_acceptance=False,
        independent_reviewer_identity=None,E02_closed=False,E01_E05_closed=False,
        resource_obligations_closed=0,fit_or_overbudget_proof=False)
    assert r['counts']==dict(input_pins_reconstructed=171,evidence_projections=12,source_files=79,
        source_anchors=22,order_relations=8,earlier_byte_guard_relations=1,expression_records=8,
        strict_json_source_checks=1,worker_launcher_context_checks=1,required_fields=9,
        documentary_definition_fields=2,insufficient_fields=7,required_allocation_classes=12,
        unknown_inventory_values=48,owner_boundaries=10,review_checks=15,other_unproduced_packages=10)
    assert all(r[k] is None for k in ['verified_complete_upper_bytes','fits','slack_bytes'])
    assert r['pending_independent_acceptance_and_P02_P03_not_bypassed'] and r['other_packages_started']==0
    assert len(r['limitations'])>=10 and r['E06']==o['E06'] and r['decision']==o['decision']
    assert r['git_publication']['commit_and_push_all_requested']
    assert set(r['work_unit']['rollback_files'])==expected and r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command']=='python3 docs/validation/D5-I152-audit.py'
    assert r['work_unit']['expected_result']=='PASS_STATIC_SOURCE_ONLY' and r['work_unit']['diff_budget_note']
    assert seal['source_only'] and seal['documentary_dossier_conformance']
    assert not any(seal[k] for k in ['H07_verified','independent_acceptance','product_or_components_executed',
        'quotas_changed','proposal_enabled','D5_closed'])
    assert seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I152',package='P04-H07',
        documentary_dossier_conformance=True,accepted_as_complete_H07_proof=False,independent_acceptance=False,
        Git_input_pins_checked=171,evidence_projections=12,source_files=79,source_anchors=22,
        classified_order_relations=8,insufficient_fields=7,prior_published_files_preserved=238,new_files=5,
        product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
