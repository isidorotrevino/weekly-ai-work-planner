#!/usr/bin/env python3
"""I150 H06 review: documentary Git/JSON/AST reconstruction only.
No product/component imports, execution, compilation, introspection or sampling.
"""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'dd2db0ca8a4e168f148a91734656e397c503b159'
OUT = P + 'D5-PFC126-03-E02-H06.json'
REVIEW = P + 'D5-I149-P04-H06-preparation-review.json'
SEAL = P + 'D5-I149-integrity.json'
AUDIT = P + 'D5-I149-audit.py'
DESIGN = 'docs/design/D5-I149-P04-H06-PROJECTION-DIGEST-METADATA-TEMPORARIES.md'
PLAN = P + 'D5-I132-E01-E05-evidence-plan.json'
CONTRACT = P + 'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
SCOPE = P + 'D5-PFC126-03-RESOURCE-SCOPE.json'
RUNTIME = P + 'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
PLATFORM = P + 'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
H05 = P + 'D5-PFC126-03-E02-H05.json'
I124 = P + 'D5-I124-global-batch-lifetime-proof.json'
ATOMIC = 'testing/prospective_capture_joint_i122/atomic.py'
JOINT = 'testing/prospective_capture_joint_i122/capture.py'
TYPED = 'testing/prospective_capture_typed/capture.py'
CAPTURE = 'testing/prospective_capture/capture.py'
PROJECTIONS = [
    (CONTRACT, '/heap/owner_budgets/5'),
    (P + 'D5-I125-complete-heap-review.json', '/required_terms/5'),
    (P + 'D5-I123-transient-resource-envelope.json', '/memory'),
    (I124, '/scope'), (I124, '/lifetime_envelope'),
    (RUNTIME, '/acceptance'), (PLATFORM, '/acceptance'),
    (P + 'D5-I148-P04-H05-documentary-review.json', '/acceptance'),
    (H05, '/overlap_alias_original_and_rejected_prefix_treatment'),
    (SCOPE, '/worker_heap_vs_other_process_scope'),
    (CONTRACT, '/product_numeric_candidates'),
    (P + 'D5-I124-resource-admission-review.json', '/remaining_for_actual_admission'),
]
SPECS = [
    (CAPTURE, 'digest_value'), (CAPTURE, 'digest_value.add'),
    (CAPTURE, 'digest_value.charge'), (CAPTURE, 'digest_value.visit'),
    (TYPED, 'encode'), (TYPED, 'canonical'), (TYPED, 'Projector.observe'),
    (TYPED, 'Projector.observe.charge'), (TYPED, 'Projector.observe.leaf'),
    (TYPED, 'Projector.observe.visit'), (TYPED, 'PageSink.append'),
    (JOINT, 'bounded_builtin'), (JOINT, 'canonical_hash'),
    (JOINT, 'store_request'), (JOINT, 'drive_request'), (JOINT, 'store_receipt'),
    (JOINT, 'legacy_selectors'), (JOINT, 'scoped_selectors'),
    (JOINT, 'CausalState.row_budget'), (JOINT, 'CausalState.open_call'),
    (JOINT, 'CausalState.close_call'), (JOINT, 'DomainState.declaration'),
    (JOINT, 'DomainState.link'), (ATOMIC, 'build.Bindings.check'),
    (ATOMIC, 'build.Recorder._fork'), (ATOMIC, 'build.Recorder._atomic'),
    (ATOMIC, 'build.Recorder._typed_finish'), (ATOMIC, 'build.Pages.flush'),
]
CENSUS = ['Call', 'List', 'Tuple', 'Dict', 'Set', 'ListComp', 'SetComp',
          'DictComp', 'GeneratorExp', 'ExceptHandler']
# These prove lexical construction/check order, not reachability, sizes or lifetimes.
ORDERS = [
    (JOINT, 'canonical_hash', 'body = ', "fault(len(body) + digest['bytes']"),
    (JOINT, 'store_request', 'body = ', "fault(args_digest['bytes']"),
    (JOINT, 'drive_request', 'body = ', "fault(decoded_digest['bytes']"),
    (JOINT, 'legacy_selectors', 'out[key] = val', 'fault(len(out)'),
    (JOINT, 'CausalState.row_budget', 'bounded_builtin(row', 'fault(len(encode(row))'),
    (JOINT, 'CausalState.open_call', 'row = dict(', 'stack.append(key)'),
    (JOINT, 'DomainState.declaration', "group = dict(schema='d5.domain-witness-group.v2'", 'self.row_budget(group)'),
    (JOINT, 'DomainState.declaration', 'self.row_budget(record)', 'self.charge(units)'),
    (TYPED, 'Projector.observe.visit', 'text = self.guard.lexical(v)', 'c.require(type(text) is str'),
    (TYPED, 'Projector.observe.visit', 'chunk = text[', 'charge(len(chunk))'),
    (TYPED, 'PageSink.append', 'b = encode(event)', 'c.require(len(b)'),
    (ATOMIC, 'build.Recorder._typed_finish', 'out = dict(', "len(encode(out)) > self.limits['index_sidecar_bytes']"),
    (ATOMIC, 'build.Pages.flush', 'body = ', 'p.fault(len(body) =='),
]
FACTS = [
    (CAPTURE, 'digest_value.visit', 'sorted(x)'),
    (CAPTURE, 'digest_value.visit', "sorted(parts, key=lambda v: v['sha256'])"),
    (CAPTURE, 'digest_value.visit', 'parts.append(p)'),
    (CAPTURE, 'digest_value.visit', 'add(chunk.encode())'),
    (TYPED, 'Projector.observe.leaf', 'emit(canonical(node))'),
    (JOINT, 'DomainState.link', "sorted(set(left + b['witness_refs']))"),
    (ATOMIC, 'build.Bindings.check', 'rows = dict(self.rows)'),
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
        orders.append(dict(path=path, symbol=symbol, construction_prefix=before,
                           later_check_or_publication_prefix=after, before=mark(a), after=mark(b),
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
                    generations_including_initial_upper=1+f+s, not_nonclone_operation_or_live_temporary_counts=True),
                candidate_numeric_limits=json.loads(blobs[CONTRACT])['product_numeric_candidates'],
                no_target_import_execution_compilation_introspection_or_sampling=True)


def validate_preparation():
    o, r, seal = rd(OUT), rd(REVIEW), rd(SEAL)
    task = next(t for t in rd(PLAN)['tasks'] if t['id'] == 'P04-H06')
    c, scope = rd(CONTRACT), rd(SCOPE)
    owner = c['heap']['owner_budgets'][5]
    expected = {OUT, REVIEW, SEAL, AUDIT, DESIGN}
    prior = rd(P + 'D5-I148-integrity.json')
    preserved = {**prior['preserved_published218'], **prior['artifacts'],
                 P + 'D5-I148-integrity.json': sha(P + 'D5-I148-integrity.json')}
    assert len(preserved) == 223 and seal['preserved_published223'] == preserved
    assert set(seal['artifacts']) | {SEAL} == expected
    for pins in [preserved, seal['artifacts'], o['input_pins'], r['input_pins'],
                 rd(P + 'D5-I119-integrity.json')['inherited_inputs477']]:
        for path, h in pins.items():
            assert sha(path) == h, path
    subprocess.check_call(['git', 'merge-base', '--is-ancestor', BASE, 'HEAD'], cwd=ROOT)
    assert o['base_commit'] == r['base_commit'] == seal['base_commit'] == BASE
    assert o['schema'] == task['output_schema'] and OUT == task['planned_output']
    assert o['package_id'] == 'P04-H06' and o['date'] == r['date'] == seal['date'] == '2026-11-13'
    assert r['schema'] == 'd5.i149-p04-h06-preparation-review.v1'
    assert seal['schema'] == 'd5.i149-integrity.v1'
    assert o['status'] == 'PREPARED_INSUFFICIENT_PROJECTION_DIGEST_METADATA_TEMPORARY_HEAP_H06_E02_OPEN_NOT_ADMITTED'
    assert r['status'] == 'P04_H06_PREPARATION_COMPLETE_NO_COMPLETE_BOUND_NO_ADMISSION'
    assert o['plan_binding'] == dict(path=PLAN, sha256=sha(PLAN), package_id='P04-H06', task_record_canonical_sha256=digest(task))
    assert o['candidate_binding'] == dict(path=CONTRACT, sha256=sha(CONTRACT),
        contract_id=c['contract_id'], subject=c['subject'], source_revision='I122-CANDIDATE-01')
    assert set(task['required_specific_fields']) <= set(o) and len(task['required_specific_fields']) == 9
    assert o['candidate_owner_record'] == owner and owner['id'] == 'H06'
    assert o['candidate_budget_bytes=268435456'] == o['candidate_budget_bytes'] == owner['candidate_budget_bytes'] == 256*1024**2
    assert o['owner_id_metric_and_exact_units']['metric'] == owner['metric'] == 'peak_requested_live_heap'
    identity = o['owner_id_metric_and_exact_units']
    assert identity['owner_id'] == 'H06' and identity['owner'] == owner['owner']
    assert identity['unit'] == 'exact_integer_bytes' and identity['candidate_budget_bytes'] == 268435456
    assert identity['scope_is_requirement_not_verified_bound'] and owner['proof_upper_bytes'] is None
    assert o['source_evidence'] == evidence(o['input_pins'])
    e = o['source_evidence']
    assert (e['input_pin_count'], e['source_file_count'], len(e['projections']), len(e['source_anchors'])) == (163, 79, 12, 28)
    assert len(e['lexical_order_witnesses']) == 13 and len(e['allocation_expression_witnesses']) == 7
    inventory = o['complete_live_allocation_inventory']
    assert not inventory['complete'] and len(inventory['required_classes']) == 12
    for i, row in enumerate(inventory['required_classes'], 1):
        assert row['id'] == 'R%02d' % i and row['required_coverage'] and row['runtime_dependency'] and not row['verified']
        assert all(row[k] is None for k in ['cardinality_upper', 'size_upper_bytes', 'maximum_live_upper_bytes', 'lifetime_derivation'])
    abi = o['source_ABI_allocator_dependencies']
    assert abi['historical_runtime_reference'] == c['runtime'] and not abi['exact_runtime_ABI_or_allocator_correspondence_verified']
    assert all(abi[k] is None for k in ['accepted_target_closure', 'builtin_growth_sort_scratch_model',
        'hash_crypto_native_workspace_model', 'projection_codec_allocation_mapping', 'requested_live_and_retention_model'])
    deriv = o['cardinality_size_lifetime_derivations']
    assert not deriv['complete'] and deriv['whole_owner_live_upper_bytes'] is None
    assert deriv['inherited_count_reference'] == e['inherited_count_reference']
    assert deriv['all_guards_after_construction_need_prefix_accounting'] and deriv['nonclone_operations_not_bounded_by_F_S_alone']
    assert deriv['temporary_name_or_return_not_lifetime_proof'] and deriv['metadata_lock_not_whole_worker_lifetime_serialization']
    overlap = o['overlap_alias_original_and_rejected_prefix_treatment']
    assert overlap['inherited_scope'] == scope['worker_heap_vs_other_process_scope']
    assert overlap['source_applicability'] == scope['321_root_12_group_applicability']['I124_applicability']
    assert [x['other_owner'] for x in overlap['boundary_requirements']] == ['H%02d' % i for i in range(1,12) if i != 6]
    assert all(not x['resolved'] for x in overlap['boundary_requirements']) and not overlap['complete_ownership_alias_lifetime_proof']
    assert overlap['nonclone_temporaries_not_inferred_paid_by_H04'] and overlap['codec_page_reader_carriers_not_implicitly_excluded']
    dep = o['explicit_assumptions_and_external_dependencies']
    assert not dep['assumptions_verified'] and not dep['P02_exact_runtime_identity_accepted'] and not dep['P03_capacity_service_accepted']
    assert dep['inherited_P01_preconditions'] == scope['321_root_12_group_applicability']['original_source_route_preconditions']
    assert all(dep[k] is None for k in ['complete_nonclone_operation_multiplicity_model',
        'complete_allocation_size_and_overlap_theorem', 'independent_runtime_memory_review'])
    bound, fit = o['verified_upper_bytes_and_derivation'], o['bound_fit_not_just_partial_payload']
    assert bound['verified_upper_bytes'] is None and bound['complete_derivation'] is None and not bound['verified'] and bound['unknown_not_zero']
    assert fit == dict(candidate_budget_bytes=268435456, verified_complete_upper_bytes=None,
        fit_result='NOT_EVALUABLE_NO_COMPLETE_H06_BOUND', fits=None, slack_bytes=None,
        overbudget_proved=False, actual_unboundedness_proved=False, partial_payload_not_accepted=True)
    assert [x['field'] for x in o['field_assessment']] == task['required_specific_fields']
    for row in o['field_assessment']:
        definition = row['field'] in ['owner_id_metric_and_exact_units', 'candidate_budget_bytes=268435456']
        assert row['result'] == ('DOCUMENTARY_DEFINITION_ONLY' if definition else 'INSUFFICIENT_FOR_ACCEPTANCE')
        assert row['basis'] and not row['resource_obligation_closed']
    assert o['acceptance'] == dict(rule=task['acceptance'], rejection_rule=task['rejection'],
        preparation_complete=True, accepted_as_complete_H06_proof=False, H06_verified=False,
        E02_closed=False, resource_obligations_closed=0, no_reserve_transfer=True)
    assert r['output'] == dict(path=OUT, sha256=sha(OUT), schema=o['schema'], evidence_kind=o['evidence_kind'], produced=True)
    assert r['counts'] == dict(required_fields=9, documentary_definition_fields=2, insufficient_fields=7,
        required_allocation_classes=12, unknown_inventory_values=48, owner_boundaries=10,
        source_files=79, source_anchors=28, evidence_projections=12, input_pins=163,
        lexical_order_witnesses=13, allocation_expression_witnesses=7, other_unproduced_packages=11)
    assert all(r['preparation_checks'].values())
    for progress, t in zip(r['package_progress'], rd(PLAN)['tasks'], strict=True):
        exists = t['id'] in ['P01','P02','P03'] + ['P04-H%02d' % i for i in range(1,7)]
        assert (ROOT/t['planned_output']).exists() == exists == progress['output_created']
        assert progress['package_id'] == t['id'] and progress['path'] == t['planned_output']
        assert progress['sha256'] == (sha(t['planned_output']) if exists else None)
    assert o['reserve_accounting'] == c['reserve_accounting']
    assert o['non_execution_and_zero_transfer_policy'] == rd(H05)['non_execution_and_zero_transfer_policy']
    assert not o['producer_and_review_provenance']['independent_acceptance']
    assert o['producer_and_review_provenance']['independent_reviewer_identity'] is None
    assert r['independent_review'] == dict(accepted=False, reviewer_identity=None, no_independent_review_fabricated=True)
    assert o['dependencies'] == rd(H05)['dependencies']
    assert [d['id'] for d in o['dependencies']] == task['depends_on'] == ['P01','P02']
    provenance = o['producer_and_review_provenance']
    assert provenance['producer_identity'] == 'Codex assistant preparing I149 in this chat'
    assert provenance['planned_author_role'] == task['responsible_role'] and provenance['planned_review_role'] == task['review_role']
    assert not provenance['runtime_custodian_authority_claimed']
    assert r['input_pins'] == {**o['input_pins'], OUT: sha(OUT)}
    assert not rd(RUNTIME)['acceptance']['accepted_as_runtime_identity']
    assert not rd(PLATFORM)['acceptance']['accepted_as_platform_evidence']
    assert not any(o['external_material_scope'][k] for k in ['global_absence_claimed','external_contacts_made','runtime_or_platform_sampled'])
    assert o['E02_criterion_disposition'] == r['E02_criterion_disposition']
    for row, old in zip(o['E02_criterion_disposition'], rd(H05)['E02_criterion_disposition'], strict=True):
        assert row == dict(id=old['id'], inherited_result=old['I147_result'], I149_result=old['I147_result'], closed=False)
    old_decision = rd(H05)['decision']
    negative = {('complete_H06_bound_verified' if k == 'complete_H05_bound_verified' else k): v for k,v in old_decision.items()}
    assert o['decision'] == r['decision'] == negative
    assert o['E06'] == r['E06'] == rd(H05)['E06']
    assert not seal['proposal_enabled'] and seal['source_only'] and not seal['product_or_components_executed']
    assert r['git_publication']['commit_and_push_all_requested']
    assert set(r['work_unit']['rollback_files']) == expected and r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command'] == 'python3 docs/validation/D5-I149-audit.py'
    assert r['work_unit']['expected_result'] == 'PASS_STATIC_SOURCE_ONLY' and r['work_unit']['diff_budget_note']
    for path in [P+'D5-JOINT-capture-authorization.json', P+'D5-JOINT-P01', P+'D5-JOINT-P01-launch.json']:
        assert not (ROOT/path).exists()


REVIEW_BASE = '89c341ff6e45c273fbcdfdf5b33952f0a0221f6a'
NEW_REVIEW = P + 'D5-I150-P04-H06-documentary-review.json'
RECON = P + 'D5-I150-P04-H06-source-reconstruction.json'
NEW_SEAL = P + 'D5-I150-integrity.json'
NEW_AUDIT = P + 'D5-I150-audit.py'
NEW_DESIGN = 'docs/design/D5-I150-P04-H06-TEMPORARY-HEAP-REVIEW.md'


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
    for i, row in enumerate(e['lexical_order_witnesses'], 1):
        before = locate(row['path'], row['symbol'], row['before'])
        after = locate(row['path'], row['symbol'], row['after'])
        assert ast.unparse(before).startswith(row['construction_prefix'])
        assert ast.unparse(after).startswith(row['later_check_or_publication_prefix'])
        assert (before.lineno, before.col_offset) < (after.lineno, after.col_offset)
        if i == 5:
            category = 'VALIDATION_TO_ENCODED_SIZE_GUARD'
        elif i == 6:
            category = 'CONSTRUCTION_TO_DRAFT_PUBLICATION'
        elif i == 8:
            category = 'ROW_VALIDATION_TO_REFERENCE_CHARGE'
        else:
            category = 'CONSTRUCTION_TO_LATER_GUARD_OR_VALIDATION'
        orders.append(dict(id='W%02d' % i, path=row['path'], symbol=row['symbol'],
                           published_record_sha256=digest(row), classification=category,
                           before_expression=ast.unparse(before), after_expression=ast.unparse(after),
                           not_first_guard_or_dynamic_allocation_proof=True))
    assert len(orders) == 13
    expressions = []
    for row in e['allocation_expression_witnesses']:
        for signature in row['sites']:
            assert ast.unparse(locate(row['path'], row['symbol'], signature)) == row['expression']
        expressions.append(dict(path=row['path'], symbol=row['symbol'], expression=row['expression'],
                                site_count=len(row['sites']), published_record_sha256=digest(row)))

    def function(path, symbol):
        assert len(indices[path][symbol]) == 1
        return indices[path][symbol][0]

    def one_expression(node, expression):
        found = [n for n in ast.walk(node) if not isinstance(n, ast.Expr) and ast.unparse(n) == expression]
        assert len(found) == 1, expression
        return found[0]

    def expression_record(node, expression):
        return dict(expression=expression, **mark(one_expression(node, expression)))

    add = function(CAPTURE, 'digest_value.add')
    leaf = function(TYPED, 'Projector.observe.leaf')
    emit = function(TYPED, 'Projector.observe.emit')
    charge = function(TYPED, 'Projector.observe.charge')
    chains = [dict(id='ARG01', path=CAPTURE, caller_symbol='digest_value.visit',
        argument_call=expression_record(nodes[(CAPTURE, 'digest_value.visit')], 'add(chunk.encode())'),
        local_callee_symbol='digest_value.add', local_callee_AST=mark(add),
        callee_guard=expression_record(add, "require(used <= lim['operand_bytes'], 'OPERAND_BUDGET')"),
        argument_evaluation_before_local_guard_conditional_on_pinned_binding=True),
        dict(id='ARG02', path=TYPED, caller_symbol='Projector.observe.leaf',
        argument_call=expression_record(leaf, 'emit(canonical(node))'),
        local_emit_symbol='Projector.observe.emit', local_emit_AST=mark(emit),
        emit_charge=expression_record(emit, 'charge(len(b))'),
        charge_guard=expression_record(charge, "c.require(used <= self.limits['operand_bytes'], 'OPERAND_BUDGET')"),
        argument_evaluation_before_local_guard_conditional_on_pinned_binding=True)]
    earlier = []
    for path, symbol, expression in [
        (JOINT, 'canonical_hash', 'digest = bounded_builtin(value, limits)'),
        (JOINT, 'store_request', 'args_digest = bounded_builtin(args, limits)'),
        (JOINT, 'store_request', 'op_digest = bounded_builtin(op, limits)'),
        (JOINT, 'drive_request', 'decoded_digest = bounded_builtin(req, lim)'),
        (TYPED, 'PageSink.append', "c.require(not self.closed, 'PAGES_CLOSED')"),
        (ATOMIC, 'build.Pages.flush', "p.fault(self._planning, 'CAUSAL_SCHEMA_INVALID')"),
    ]:
        earlier.append(dict(path=path, symbol=symbol, **expression_record(nodes[(path, symbol)], expression),
                            prior_guard_not_complete_allocation_upper=True))
    atomic = nodes[(ATOMIC, 'build.Recorder._atomic')]
    locks = [n for n in ast.walk(atomic) if isinstance(n, ast.With) and any(
        ast.unparse(item.context_expr) == 'self._state_lock' for item in n.items)]
    assert len(locks) == 1
    operation = one_expression(atomic, 'value = operation(draft)')
    write = one_expression(atomic, 'p.write_all(fd, body)')
    error = one_expression(atomic, 'error = ex')
    reraise = one_expression(atomic, 'raise error')
    assert locks[0].lineno < operation.lineno <= locks[0].end_lineno < write.lineno
    retention = dict(lock_AST=mark(locks[0]), operation_AST=mark(operation), write_AST=mark(write),
                     error_assignment_AST=mark(error), reraise_AST=mark(reraise),
                     source_only_lock_scope_not_worker_lifetime_serialization=True,
                     no_prompt_collection_or_permanent_retention_inferred=True)
    open_call = nodes[(JOINT, 'CausalState.open_call')]
    rows = [n for n in ast.walk(open_call) if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == 'row' for t in n.targets)]
    assert len(rows) == 1
    stack_append = one_expression(open_call, 'stack.append(key)')
    table_assignment = one_expression(open_call, 'self.calls[key] = row')
    assert (rows[0].lineno, rows[0].col_offset) < (stack_append.lineno, stack_append.col_offset)
    assert (stack_append.lineno, stack_append.col_offset) < (table_assignment.lineno, table_assignment.col_offset)
    draft_publication = dict(row_construction_AST=mark(rows[0]), stack_append_AST=mark(stack_append),
                             table_assignment_AST=mark(table_assignment),
                             source_only_no_external_publication_or_admission=True)
    counts = json.loads(data[I124][1])
    f, s = counts['global_F_upper'], counts['global_S_upper']
    assert e['inherited_count_reference'] == dict(F_upper=f, S_upper=s, clone_batches_upper=f+s,
        generations_including_initial_upper=1+f+s, not_nonclone_operation_or_live_temporary_counts=True)
    assert (f, s, f+s, 1+f+s) == (52018, 1759, 53777, 53778)
    unknowns, inventory = [], []
    for i, row in enumerate(o['complete_live_allocation_inventory']['required_classes']):
        for key in ['cardinality_upper', 'size_upper_bytes', 'maximum_live_upper_bytes', 'lifetime_derivation']:
            assert row[key] is None
            unknowns.append('/complete_live_allocation_inventory/required_classes/' + str(i) + '/' + key)
        assert not row['verified']
        inventory.append(dict(id=row['id'], record_sha256=digest(row), complete_count_size_peak_lifetime_unproved=True))
    boundaries = o['overlap_alias_original_and_rejected_prefix_treatment']['boundary_requirements']
    assert all(not row['resolved'] for row in boundaries)
    return dict(preparation_commit=o['base_commit'], published_commit=REVIEW_BASE,
        H06_published_blob_oid=oid, H06_sha256=sha(OUT), input_pin_checks=inputs,
        projection_checks=projections, source_file_count=len(sources), source_pin_vector_sha256=digest(sources),
        file_summary_vector_sha256=digest(summaries), syntax_counts=totals, syntax_site_vector_sha256=digest(vector),
        source_anchor_checks=anchors, classified_order_checks=orders, expression_checks=expressions,
        conditional_argument_evaluation_checks=chains, earlier_validation_checks=earlier,
        lock_and_retention_source_check=retention, draft_row_publication_source_check=draft_publication,
        inherited_count_reference=e['inherited_count_reference'],
        inventory_checks=inventory, unknown_inventory_pointers=unknowns,
        boundary_record_sha256={x['other_owner']: digest(x) for x in boundaries},
        field_record_sha256={x['field']: digest(o[x['field']]) for x in o['field_assessment']},
        no_dynamic_allocation_lifetime_runtime_binding_or_native_capacity_proof=True)


def main():
    validate_preparation()
    o, z, r, seal = rd(OUT), rd(RECON), rd(NEW_REVIEW), rd(NEW_SEAL)
    prior = rd(SEAL)
    preserved = {**prior['preserved_published223'], **prior['artifacts'], SEAL: sha(SEAL)}
    assert len(preserved) == 228 and seal['preserved_published228'] == preserved
    expected = {NEW_REVIEW, RECON, NEW_SEAL, NEW_AUDIT, NEW_DESIGN}
    assert set(seal['artifacts']) | {NEW_SEAL} == expected
    for pins in [preserved, seal['artifacts'], z['input_pins'], r['input_pins']]:
        for path, h in pins.items():
            assert sha(path) == h, path
    assert set(git('diff', REVIEW_BASE, '--name-only').splitlines()) | set(
        git('ls-files', '--others', '--exclude-standard').splitlines()) == expected
    if git('rev-parse', 'HEAD') != REVIEW_BASE:
        assert not git('diff', 'HEAD', '--name-only')
    assert r['base_commit'] == z['base_commit'] == seal['base_commit'] == REVIEW_BASE
    assert r['date'] == z['date'] == seal['date'] == '2026-11-13'
    assert z['schema'] == 'd5.i150-p04-h06-source-reconstruction.v1'
    assert r['schema'] == 'd5.i150-p04-h06-documentary-review.v1'
    assert seal['schema'] == 'd5.i150-integrity.v1'
    assert z['reconstruction'] == reconstruct()
    pins = {**o['input_pins'], OUT: sha(OUT), REVIEW: sha(REVIEW), SEAL: sha(SEAL), AUDIT: sha(AUDIT)}
    assert z['input_pins'] == pins and r['input_pins'] == {**pins, RECON: sha(RECON)}
    assert r['H06'] == dict(path=OUT, sha256=sha(OUT), bytes_preserved=True)
    assert r['plan_binding'] == o['plan_binding']
    assert r['source_reconstruction'] == dict(path=RECON, sha256=sha(RECON))
    assert r['documentary_dossier_conformance'] and not r['H06_change_required']
    assert r['blocking_dossier_defects'] == []
    assert r['status'] == 'REVIEW_COMPLETE_DOSSIER_CONFORMANT_H06_PROOF_REJECTED_NO_ADMISSION'
    reviewer = r['reviewer']
    assert reviewer['same_assistant_as_preparer'] and reviewer['methodologically_separate_reconstruction']
    assert not reviewer['actor_independence'] and not reviewer['organizational_independence'] and not reviewer['runtime_custodian_authority']
    assert [x['id'] for x in r['checks']] == ['R%02d' % i for i in range(1,16)]
    for row in r['checks']:
        assert row['result'] == 'CONFORMANT_DOCUMENTARY_INSUFFICIENCY_JUDGMENT'
        assert row['basis'] and not row['resource_obligation_closed']
    assert r['field_disposition'] == [dict(field=x['field'], inherited_result=x['result'],
        I150_result=x['result'], field_record_sha256=digest(o[x['field']]), resource_obligation_closed=False)
        for x in o['field_assessment']]
    assert r['E02_criterion_disposition'] == [dict(id=x['id'], inherited_result=x['I149_result'],
        I150_result=x['I149_result'], closed=False) for x in o['E02_criterion_disposition']]
    assert r['counts'] == dict(input_pins_reconstructed=163, evidence_projections=12, source_files=79,
        source_anchors=28, order_relations=13, construction_to_later_check=10,
        construction_to_draft_publication=1, validation_to_guard_or_charge=2, expression_records=7,
        conditional_argument_chains=2, earlier_validation_checks=6, required_fields=9,
        documentary_definition_fields=2, insufficient_fields=7, required_allocation_classes=12,
        unknown_inventory_values=48, owner_boundaries=10, review_checks=15, other_unproduced_packages=11)
    assert r['acceptance'] == dict(review_completed=True, insufficiency_judgment_confirmed=True,
        accepted_as_complete_H06_proof=False, H06_verified=False, independent_acceptance=False,
        independent_reviewer_identity=None, E02_closed=False, E01_E05_closed=False,
        resource_obligations_closed=0, fit_or_overbudget_proof=False)
    assert all(r[k] is None for k in ['verified_complete_upper_bytes','fits','slack_bytes'])
    assert r['pending_independent_acceptance_and_P02_P03_not_bypassed'] and r['other_packages_started'] == 0
    assert len(r['limitations']) >= 10
    assert r['decision'] == o['decision'] and r['E06'] == o['E06']
    assert r['git_publication']['commit_and_push_all_requested']
    assert set(r['work_unit']['rollback_files']) == expected
    assert r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command'] == 'python3 docs/validation/D5-I150-audit.py'
    assert r['work_unit']['expected_result'] == 'PASS_STATIC_SOURCE_ONLY'
    assert seal['source_only'] and not seal['H06_verified'] and not seal['independent_acceptance']
    assert not seal['proposal_enabled'] and seal['resource_obligations_closed'] == 0
    assert not seal['product_or_components_executed'] and not seal['quotas_changed']
    assert not seal['D5_closed'] and seal['IR03'] == 'NOT_READY'
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY', increment='I150', package='P04-H06',
        documentary_dossier_conformance=True, accepted_as_complete_H06_proof=False,
        independent_acceptance=False, Git_input_pins_checked=163, evidence_projections=12,
        source_files=79, source_anchors=28, classified_order_relations=13,
        argument_evaluation_chains=2, insufficient_fields=7, prior_published_files_preserved=228,
        new_files=5, product_or_components_executed=0, quotas_changed=False,
        resource_obligations_closed=0, proposal_enabled=False, D5_closed=False,
        IR03='NOT_READY', git_head=git('rev-parse','HEAD')), sort_keys=True))


if __name__ == '__main__':
    main()
