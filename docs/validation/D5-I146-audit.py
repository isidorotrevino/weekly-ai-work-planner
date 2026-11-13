#!/usr/bin/env python3
"""I146 H04 review: documentary consistency and fresh Git/AST/integer reconstruction.
No product/component import, clone execution, allocator probe or quota change.
"""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'f245a595125891774cf58c1aa9ecc05e99ea6ecb'
OUT = P + 'D5-PFC126-03-E02-H04.json'
REVIEW = P + 'D5-I145-P04-H04-preparation-review.json'
PLAN = P + 'D5-I132-E01-E05-evidence-plan.json'
CONTRACT = P + 'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
SCOPE = P + 'D5-PFC126-03-RESOURCE-SCOPE.json'
RUNTIME = P + 'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
PLATFORM = P + 'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
H03 = P + 'D5-PFC126-03-E02-H03.json'
I123 = P + 'D5-I123-transient-resource-envelope.json'
I124 = P + 'D5-I124-global-batch-lifetime-proof.json'
MODEL = P + 'D5-I124-resource-admission-review.json'
ATOMIC = 'testing/prospective_capture_joint_i122/atomic.py'
PROJECTIONS = [
    (CONTRACT, '/heap/owner_budgets/3'), (I123, '/structural_per_clone'), (I123, '/memory'),
    (I124, '/global_F_upper'), (I124, '/global_S_upper'), (I124, '/lifetime_envelope'),
    (I124, '/lifetime_routes'), (MODEL, '/builtin_storage_model'),
    (P + 'D5-I125-complete-heap-review.json', '/required_terms/3'),
    (RUNTIME, '/acceptance'), (PLATFORM, '/acceptance'),
    (SCOPE, '/worker_heap_vs_other_process_scope'),
    (P + 'D5-I144-P04-H03-documentary-review.json', '/acceptance'),
]

def rd(path):
    return json.loads((ROOT / path).read_text())

def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()

def digest(value):
    body = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':'), sort_keys=True)
    return hashlib.sha256(body.encode()).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

def pointer(value, path):
    for key in path.strip('/').split('/'):
        key = key.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value

def evidence(pins):
    paths = sorted(pins)
    request = ''.join(BASE + ':' + path + '\n' for path in paths).encode()
    stream = io.BytesIO(subprocess.check_output(['git', 'cat-file', '--batch'], cwd=ROOT, input=request))
    data, checks = {}, []
    for path in paths:
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', path
        size = int(header[2])
        body = stream.read(size)
        assert len(body) == size and stream.read(1) == b'\n'
        assert hashlib.sha256(body).hexdigest() == pins[path] == sha(path), path
        data[path] = body
        checks.append(dict(path=path, git_blob_oid=header[0], sha256=pins[path], bytes=size))
    assert not stream.read()
    projections = []
    for path, ptr in PROJECTIONS:
        value = pointer(json.loads(data[path]), ptr)
        projections.append(dict(path=path, sha256=pins[path], json_pointer=ptr, observed_value=value,
                                canonical_sha256=digest(value), resource_obligation_closed=False))
    scope = json.loads(data[SCOPE])
    sources = scope['I122_and_original_source_pin_set']['observer_static_repo_import_superset']['file_pins']
    trees, indices, clone_sites = {}, {}, []
    for path, h in sorted(sources.items()):
        assert hashlib.sha256(data[path]).hexdigest() == h
        tree = ast.parse(data[path].decode())
        trees[path] = tree
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
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and ast.unparse(node.func) == 'clone_metadata':
                clone_sites.append(dict(path=path, line=node.lineno, column=node.col_offset,
                                        AST_sha256=hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()))
    clone_sites.sort(key=lambda x: (x['path'], x['line'], x['column']))
    symbols = ['clone_metadata', 'opaque_originals', 'build.CausalProxy.__getattr__', 'build.CausalProxy.__setattr__',
               'build.Recorder._fork', 'build.Recorder._publish', 'build.Recorder._atomic',
               'build.Recorder._drain', 'build.Recorder._observe', 'build.Recorder._typed_finish', 'build.Pages.flush']
    anchors, nodes = [], {}
    for symbol in symbols:
        assert len(indices[ATOMIC][symbol]) == 1
        node = indices[ATOMIC][symbol][0]
        nodes[symbol] = node
        anchors.append(dict(path=ATOMIC, sha256=sources[ATOMIC], symbol=symbol, line=node.lineno,
                            end_line=node.end_lineno, AST_sha256=hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()))
    fields_node = next(n for n in trees[ATOMIC].body if isinstance(n, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == 'FIELDS' for t in n.targets))
    fields = list(ast.literal_eval(fields_node.value))
    expressions = {symbol: {ast.unparse(n) for n in ast.walk(node)} for symbol, node in nodes.items()}
    required = {
        'clone_metadata': ['key = id(value)', 'key in opaque', 'key in memo', 'return memo[key]', 'return value'],
        'build.Recorder._fork': ['memo = {}', 'opaque = opaque_originals(self)', 'draft._memo = memo', 'return draft'],
        'build.Recorder._atomic': ['draft = self._fork()', 'value = operation(draft)', 'writes = tuple(draft.events._writes)', 'self._publish(draft)', 'error = ex', 'raise error', 'return value'],
        'build.Recorder._drain': ['self._idle.wait(remaining)'],
    }
    for symbol, values in required.items():
        assert set(values) <= expressions[symbol]
    clones = [n for n in ast.walk(nodes['build.Recorder._fork']) if isinstance(n, ast.Call) and ast.unparse(n.func) == 'clone_metadata']
    assert len(clones) == 5 and all([ast.unparse(x) for x in n.args[-2:]] == ['memo', 'opaque'] for n in clones)
    proxy_clones = [n for n in ast.walk(nodes['build.CausalProxy.__getattr__']) if isinstance(n, ast.Call) and ast.unparse(n.func) == 'clone_metadata']
    assert len(proxy_clones) == 2 and all(ast.unparse(n.args[1]) == '{}' for n in proxy_clones)
    structural = json.loads(data[I123])['structural_per_clone']
    prior = json.loads(data[I124])
    storage = json.loads(data[MODEL])['builtin_storage_model']
    C, A, V, O = [structural[k] for k in ['containers_upper', 'child_occurrences_upper', 'clone_invocations_upper', 'opaque_insert_attempts_upper']]
    f, s = prior['global_F_upper'], prior['global_S_upper']
    batch = (storage['header_bytes_per_cloned_container'] * C + storage['bytes_per_child_occurrence'] * A
             + storage['memo_bytes_per_container'] * C + storage['id_temporary_bytes_per_visit'] * V
             + storage['opaque_fixed_bytes'] + storage['opaque_bytes_per_insert_attempt'] * O)
    generations = 1 + f + s
    assert f == 52018 and s == 1759 and f + s == prior['global_clone_batches_upper'] == 53777
    assert generations == prior['lifetime_envelope']['metadata_generations_including_initial_upper'] == 53778
    assert batch == storage['batch_requested_bytes_upper'] == 429494352768
    assert batch * (f + s) == storage['all_batches_requested_bytes_upper'] == 23096917808804736
    assert generations * C == prior['lifetime_envelope']['metadata_containers_upper']
    assert generations * (C + A) == prior['lifetime_envelope']['metadata_container_and_edge_units_upper']
    assert not storage['actual_interpreter_binary_layout_and_allocator_attested'] and not storage['total_heap_or_RSS_bound']
    ledger = dict(C=C, A=A, V=V, O=O, F=f, S=s, clone_batches=f+s, generations_including_initial=generations,
                  conditional_batch_bytes=batch, conditional_retain_all_bytes=batch*(f+s),
                  byte_subtotal_multiplier_is_clone_batches_not_generations=True,
                  initial_generation_storage_upper_bytes=None, initial_is_not_an_extra_cloned_memo_batch=True,
                  metadata_containers_including_initial_upper=generations*C,
                  metadata_container_and_edge_units_including_initial_upper=generations*(C+A),
                  candidate_budget_bytes=6442450944, conditional_model_upper_exceeds_budget=batch*(f+s) > 6442450944,
                  complete_verified_H04_upper_bytes=None, fits=None, slack_bytes=None,
                  old_upper_is_not_lower_bound_or_actual_infeasibility=True,
                  IO32_and_rejections_are_F_subsets_not_extra_batches=True,
                  no_33_generation_or_immediate_GC_refinement_proved=True)
    return dict(commit=BASE, input_pin_count=len(checks), input_blob_checks=checks, projections=projections,
                observer_source_files=len(sources), source_anchors=anchors, copied_FIELDS=fields,
                FIELDS_anchor=dict(path=ATOMIC, sha256=sources[ATOMIC], symbol='FIELDS', line=fields_node.lineno,
                                   end_line=fields_node.end_lineno, AST_sha256=hashlib.sha256(ast.dump(fields_node, include_attributes=False).encode()).hexdigest()),
                clone_call_syntax_sites=clone_sites, shared_fork_memo_source_verified=True,
                independent_proxy_memo_source_verified=True, escape_IO_error_retention_source_identified=True,
                source_syntax_is_not_live_generation_or_byte_measurement=True, inherited_arithmetic=ledger,
                inherited_structural_per_clone=structural, inherited_storage_model=storage,
                inherited_lifetime_routes=prior['lifetime_routes'], inherited_lifetime_envelope=prior['lifetime_envelope'],
                no_target_modules_executed=True)

def validate_preparation():
    o, r, seal = rd(OUT), rd(REVIEW), rd(P + 'D5-I145-integrity.json')
    c, s, plan = rd(CONTRACT), rd(SCOPE), rd(PLAN)
    task, owner = plan['tasks'][6], c['heap']['owner_budgets'][3]
    assert o['base_commit'] == r['base_commit'] == seal['base_commit'] == BASE
    assert o['date'] == r['date'] == seal['date'] == '2026-11-13'
    subprocess.check_call(['git', 'merge-base', '--is-ancestor', BASE, 'HEAD'], cwd=ROOT)
    prior = rd(P + 'D5-I144-integrity.json')
    preserved = {**prior['preserved_published198'], **prior['artifacts'], P + 'D5-I144-integrity.json': sha(P + 'D5-I144-integrity.json')}
    assert seal['preserved_published203'] == preserved and len(preserved) == 203
    for pins in [preserved, seal['artifacts'], o['input_pins'], r['input_pins'], rd(P + 'D5-I119-integrity.json')['inherited_inputs477']]:
        for path, h in pins.items():
            assert sha(path) == h, path
    expected = {OUT, REVIEW, P + 'D5-I145-audit.py', P + 'D5-I145-integrity.json', 'docs/design/D5-I145-P04-H04-CLONES-MEMO-HEAP.md'}
    assert set(seal['artifacts']) | {P + 'D5-I145-integrity.json'} == expected and len(seal['artifacts']) == 4
    assert o['source_evidence'] == evidence(o['input_pins']) and len(o['input_pins']) == 150
    assert len(o['source_evidence']['projections']) == 13 and len(o['source_evidence']['source_anchors']) == 11
    assert len(o['source_evidence']['clone_call_syntax_sites']) == 13 and len(o['source_evidence']['copied_FIELDS']) == 22
    assert o['package_id'] == task['id'] == 'P04-H04' and OUT == task['planned_output'] and o['schema'] == task['output_schema']
    assert o['plan_binding'] == dict(path=PLAN, sha256=sha(PLAN), package_id='P04-H04', task_record_canonical_sha256=digest(task))
    assert o['candidate_binding'] == dict(path=CONTRACT, sha256=sha(CONTRACT), contract_id=c['contract_id'], subject=c['subject'], source_revision='I122-CANDIDATE-01')
    assert set(task['required_specific_fields']) <= set(o) and len(task['required_specific_fields']) == 9
    assert o['candidate_budget_bytes=6442450944'] == o['candidate_budget_bytes'] == owner['candidate_budget_bytes'] == 6 * 1024**3
    assert o['candidate_owner_record'] == owner and owner['proof_upper_bytes'] is None
    assert o['status'] == 'PREPARED_INSUFFICIENT_COMPLETE_CLONE_MEMO_HEAP_H04_E02_OPEN_NOT_ADMITTED'
    assert o['owner_id_metric_and_exact_units'] == dict(owner_id='H04', owner=owner['owner'], metric=owner['metric'], unit='exact_integer_bytes', process='I122 worker clone/memo/opaque storage', candidate_budget_bytes=6442450944, scope_is_requirement_not_verified_bound=True)
    inventory = o['complete_live_allocation_inventory']
    assert not inventory['complete'] and len(inventory['required_classes']) == 12 and inventory['residual_native_or_growth_terms_not_proved_absent']
    for i, row in enumerate(inventory['required_classes'], 1):
        assert row['id'] == 'R%02d' % i and not row['verified'] and row['required_coverage'] and row['runtime_dependency']
        assert all(row[k] is None for k in ['cardinality_upper', 'size_upper_bytes', 'maximum_live_upper_bytes', 'lifetime_derivation'])
    abi = o['source_ABI_allocator_dependencies']
    assert abi['historical_runtime_reference'] == c['runtime'] and not abi['exact_runtime_ABI_or_allocator_correspondence_verified']
    assert all(abi[k] is None for k in ['accepted_target_closure', 'accepted_container_memo_id_growth_model', 'accepted_native_size_lifetime_model', 'allocator_metric_correspondence'])
    deriv = o['cardinality_size_lifetime_derivations']
    assert deriv['inherited_arithmetic'] == o['source_evidence']['inherited_arithmetic'] and not deriv['complete'] and deriv['whole_owner_live_upper_bytes'] is None
    assert deriv['closed_source_F_S_and_retain_all_scope_preserved'] and deriv['byte_subtotal_F_plus_S_distinct_from_initial_graph_count']
    assert deriv['conditional_retain_all_upper_not_complete_H04_proof'] and deriv['no_33_generation_or_GC_refinement_assumed'] and deriv['no_F_IO_or_rejection_double_count']
    overlap = o['overlap_alias_original_and_rejected_prefix_treatment']
    assert overlap['inherited_scope'] == s['worker_heap_vs_other_process_scope'] and overlap['source_applicability'] == s['321_root_12_group_applicability']['I124_applicability']
    assert [x['other_owner'] for x in overlap['boundary_requirements']] == ['H01', 'H02', 'H03'] + ['H%02d' % i for i in range(5, 12)]
    assert all(not x['resolved'] for x in overlap['boundary_requirements']) and not overlap['complete_ownership_alias_lifetime_proof']
    dep = o['explicit_assumptions_and_external_dependencies']
    assert not dep['assumptions_verified'] and not dep['P02_exact_runtime_identity_accepted'] and not dep['P03_capacity_service_accepted']
    assert all(dep[k] is None for k in ['complete_clone_memo_native_lifetime_model', 'justified_compatible_tighter_peak_theorem', 'independent_runtime_memory_review'])
    assert dep['inherited_P01_preconditions'] == s['321_root_12_group_applicability']['original_source_route_preconditions']
    assert dep['negative_dossier_does_not_bypass_P01_P02'] and dep['no_implementation_change_to_fit_budget']
    assert dep['later_resource_closure_not_started'] and dep['other_owner_or_capacity_not_substitute_for_H04_demand']
    assert not rd(RUNTIME)['acceptance']['accepted_as_runtime_identity'] and not rd(PLATFORM)['acceptance']['accepted_as_platform_evidence']
    assert o['verified_upper_bytes_and_derivation'] == dict(verified_upper_bytes=None, complete_derivation=None, evidence_pins={}, verified=False, unknown_not_zero=True, old_conditional_upper_not_complete_proof=True)
    assert o['bound_fit_not_just_partial_payload'] == dict(candidate_budget_bytes=6442450944, verified_complete_upper_bytes=None, fit_result='NOT_EVALUABLE_NO_COMPLETE_H04_BOUND', fits=None, slack_bytes=None, overbudget_proved=False, actual_unboundedness_proved=False, partial_payload_not_accepted=True)
    assert [x['field'] for x in o['field_assessment']] == task['required_specific_fields']
    for row in o['field_assessment']:
        result = 'DOCUMENTARY_DEFINITION_ONLY' if row['field'] in ['owner_id_metric_and_exact_units', 'candidate_budget_bytes=6442450944'] else 'INSUFFICIENT_FOR_ACCEPTANCE'
        assert row['result'] == result and not row['resource_obligation_closed'] and row['basis']
    assert o['acceptance'] == dict(rule=task['acceptance'], rejection_rule=task['rejection'], preparation_complete=True, accepted_as_complete_H04_proof=False, H04_verified=False, E02_closed=False, resource_obligations_closed=0, no_reserve_transfer=True)
    for d, path in zip(o['dependencies'], [SCOPE, RUNTIME], strict=True):
        assert d['path'] == path and d['sha256'] == sha(path) and not d['accepted_for_resource_closure']
    assert [x['id'] for x in o['dependencies']] == task['depends_on'] == ['P01', 'P02']
    provenance = o['producer_and_review_provenance']
    assert provenance['producer_identity'] == 'Codex assistant preparing I145 in this chat' and provenance['planned_author_role'] == task['responsible_role'] and provenance['planned_review_role'] == task['review_role']
    assert provenance['independent_reviewer_identity'] is None and not provenance['independent_acceptance'] and not provenance['runtime_custodian_authority_claimed']
    assert o['reserve_accounting'] == c['reserve_accounting'] and o['non_execution_and_zero_transfer_policy'] == s['non_execution_and_zero_transfer_policy']
    criteria = rd(P + 'D5-I131-E01-E05-review.json')['obligations'][1]['criteria']
    assert o['E02_criterion_disposition'] == [dict(id=x['id'], inherited_result=x['result'], I145_result=x['result'], closed=False) for x in criteria]
    assert r['output'] == dict(path=OUT, sha256=sha(OUT), schema=o['schema'], evidence_kind=o['evidence_kind'], produced=True) and r['input_pins'][OUT] == sha(OUT)
    assert all(r['preparation_checks'].values()) and r['status'] == 'P04_H04_PREPARATION_COMPLETE_NO_COMPLETE_BOUND_NO_ADMISSION'
    assert r['counts'] == dict(required_fields=9, documentary_definition_fields=2, insufficient_fields=7, required_allocation_classes=12, unknown_inventory_values=48, owner_boundaries=10, observer_source_files=8, source_anchors=12, evidence_projections=13, input_pins=150, other_unproduced_packages=13)
    assert not o['external_material_scope']['external_contacts_made'] and not o['external_material_scope']['global_absence_claimed'] and not o['external_material_scope']['runtime_or_platform_sampled']
    assert r['work_unit']['diff_budget_note']
    assert r['independent_review'] == dict(accepted=False, reviewer_identity=None, no_independent_review_fabricated=True)
    assert len(r['package_progress']) == 20
    for progress, t in zip(r['package_progress'], plan['tasks'], strict=True):
        exists = t['id'] in ['P01', 'P02', 'P03', 'P04-H01', 'P04-H02', 'P04-H03', 'P04-H04']
        assert (ROOT / t['planned_output']).exists() == exists and progress['output_created'] == exists and progress['package_id'] == t['id'] and progress['path'] == t['planned_output'] and progress['sha256'] == (sha(t['planned_output']) if exists else None)
    for d in [o['decision'], r['decision']]:
        true_keys = {'candidate_plan_prior_packages_and_source_bytes_preserved', 'numeric_candidates_unchanged', 'P0_D1_D4_I1_I20_A52_unchanged', 'global_gaps_and_real_obligations_pending', 'I86_I89_I92_not_resumed'}
        assert d['certificate_unchanged'] == rd(P + 'D5-I122-CAPACITY-CERTIFICATE.json')['status'] == 'IMPLEMENTED_NOT_ADMITTED' and d['IR03'] == 'NOT_READY' and d['resource_obligations_closed'] == 0
        for k in true_keys:
            assert d[k] is True
        for k, v in d.items():
            if k not in true_keys | {'certificate_unchanged', 'IR03', 'resource_obligations_closed'}:
                assert v is False, k
    assert o['E06'] == r['E06'] == dict(status='SEPARATE_PENDING_NOT_RUN', components_executed=0, execution_authorized=False)
    for path in [P + 'D5-JOINT-capture-authorization.json', P + 'D5-JOINT-P01', P + 'D5-JOINT-P01-launch.json']:
        assert not (ROOT / path).exists()
    assert set(r['work_unit']['rollback_files']) == expected and r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command'] == 'python3 docs/validation/D5-I145-audit.py' and r['work_unit']['expected_result'] == 'PASS_STATIC_SOURCE_ONLY'
    assert seal['source_only'] and not seal['proposal_enabled'] and r['git_publication']['commit_and_push_all_requested']

REVIEW_BASE = 'abb4a05e140fb188a2a51a8976b99c8f8aedeeb2'
NEW_REVIEW = P + 'D5-I146-P04-H04-documentary-review.json'
RECON = P + 'D5-I146-P04-H04-source-reconstruction.json'

def blobs(commit, paths):
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
    published = blobs(REVIEW_BASE, [OUT])[OUT]
    o = json.loads(published[1])
    assert hashlib.sha256(published[1]).hexdigest() == sha(OUT)
    data = blobs(o['base_commit'], sorted(o['input_pins']))
    checks = []
    for path, h in sorted(o['input_pins'].items()):
        oid, body = data[path]
        assert hashlib.sha256(body).hexdigest() == h == sha(path)
        checks.append(dict(path=path, preparation_git_blob_oid=oid, sha256=h, bytes=len(body)))
    evidence = o['source_evidence']
    projections = []
    assert [(x['path'], x['json_pointer']) for x in evidence['projections']] == PROJECTIONS
    for row in evidence['projections']:
        value = pointer(json.loads(data[row['path']][1]), row['json_pointer'])
        assert value == row['observed_value'] and digest(value) == row['canonical_sha256']
        assert o['input_pins'][row['path']] == row['sha256']
        projections.append(dict(path=row['path'], sha256=row['sha256'], json_pointer=row['json_pointer'],
                                recomputed_value_sha256=digest(value), matches_published_projection=True))
    scope = json.loads(data[SCOPE][1])
    sources = scope['I122_and_original_source_pin_set']['observer_static_repo_import_superset']['file_pins']
    trees, indices, clone_sites, scoped_sites = {}, {}, [], []
    for path, h in sorted(sources.items()):
        assert hashlib.sha256(data[path][1]).hexdigest() == h
        tree = ast.parse(data[path][1].decode())
        trees[path] = tree
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
            def visit_Call(self, node):
                if ast.unparse(node.func) == 'clone_metadata':
                    row = dict(path=path, line=node.lineno, column=node.col_offset,
                               AST_sha256=hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest())
                    clone_sites.append(row)
                    scoped_sites.append(dict(**row, lexical_scope='.'.join(self.parts)))
                self.generic_visit(node)
        Lexical().visit(tree)
        indices[path] = index
    clone_sites.sort(key=lambda x: (x['path'], x['line'], x['column']))
    scoped_sites.sort(key=lambda x: (x['path'], x['line'], x['column']))
    assert clone_sites == evidence['clone_call_syntax_sites'] and len(clone_sites) == 13
    assert sum(x['lexical_scope'] == 'clone_metadata' for x in scoped_sites) == 6
    assert sum(x['lexical_scope'] == 'build.Recorder._fork' for x in scoped_sites) == 5
    assert sum(x['lexical_scope'].startswith('build.CausalProxy.__getattr__') for x in scoped_sites) == 2
    nodes, anchors = {}, []
    for row in evidence['source_anchors']:
        candidates = indices[row['path']][row['symbol']]
        assert len(candidates) == 1
        node = candidates[0]
        assert (node.lineno, node.end_lineno) == (row['line'], row['end_line'])
        assert hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest() == row['AST_sha256']
        assert row['sha256'] == sources[row['path']]
        nodes[row['symbol']] = node
        anchors.append(dict(**row, lexical_binding_verified=True))
    field_row = evidence['FIELDS_anchor']
    field_nodes = [n for n in trees[ATOMIC].body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'FIELDS' for t in n.targets)]
    assert len(field_nodes) == 1
    field = field_nodes[0]
    assert (field.lineno, field.end_lineno) == (field_row['line'], field_row['end_line'])
    assert hashlib.sha256(ast.dump(field, include_attributes=False).encode()).hexdigest() == field_row['AST_sha256']
    assert list(ast.literal_eval(field.value)) == evidence['copied_FIELDS'] and len(evidence['copied_FIELDS']) == 22
    fork_calls = [n for n in ast.walk(nodes['build.Recorder._fork']) if isinstance(n, ast.Call) and ast.unparse(n.func) == 'clone_metadata']
    assert len(fork_calls) == 5 and all([ast.unparse(a) for a in n.args[-2:]] == ['memo', 'opaque'] for n in fork_calls)
    proxy_calls = [n for n in ast.walk(nodes['build.CausalProxy.__getattr__']) if isinstance(n, ast.Call) and ast.unparse(n.func) == 'clone_metadata']
    assert len(proxy_calls) == 2 and all(ast.unparse(n.args[1]) == '{}' for n in proxy_calls)
    atomic = nodes['build.Recorder._atomic']
    assert isinstance(atomic.body[0], ast.If) and ast.unparse(atomic.body[0].test) == 'self._draft'
    assert ast.unparse(atomic.body[0].body[0]) == 'return operation(self)'
    expr = {symbol: {ast.unparse(n) for n in ast.walk(node)} for symbol, node in nodes.items()}
    for symbol, required in {
        'build.Recorder._fork': ['draft._memo = memo', 'return draft'],
        'build.Recorder._atomic': ['value = operation(draft)', 'writes = tuple(draft.events._writes)', 'self._publish(draft)', 'error = ex', 'raise error', 'return value'],
        'clone_metadata': ['key = id(value)', 'return memo[key]', 'return value'],
    }.items():
        assert set(required) <= expr[symbol]
    structural = json.loads(data[I123][1])['structural_per_clone']
    counts = json.loads(data[I124][1])
    model = json.loads(data[MODEL][1])['builtin_storage_model']
    assert evidence['inherited_structural_per_clone'] == structural
    assert evidence['inherited_storage_model'] == model
    assert evidence['inherited_lifetime_routes'] == counts['lifetime_routes']
    assert evidence['inherited_lifetime_envelope'] == counts['lifetime_envelope']
    C, A, V, O = [structural[k] for k in ['containers_upper', 'child_occurrences_upper', 'clone_invocations_upper', 'opaque_insert_attempts_upper']]
    terms = dict(container_headers=model['header_bytes_per_cloned_container']*C,
                 child_occurrences=model['bytes_per_child_occurrence']*A,
                 memo_entries=model['memo_bytes_per_container']*C,
                 id_temporaries=model['id_temporary_bytes_per_visit']*V,
                 opaque_fixed=model['opaque_fixed_bytes'], opaque_insert_attempts=model['opaque_bytes_per_insert_attempt']*O)
    B = sum(terms.values())
    F, S = counts['global_F_upper'], counts['global_S_upper']
    N, G = F+S, 1+F+S
    assert (F, S, N, G, B, N*B) == (52018, 1759, 53777, 53778, 429494352768, 23096917808804736)
    ledger = evidence['inherited_arithmetic']
    assert ledger == o['cardinality_size_lifetime_derivations']['inherited_arithmetic']
    assert ledger['F'] == F and ledger['S'] == S and ledger['clone_batches'] == N and ledger['generations_including_initial'] == G
    assert ledger['conditional_batch_bytes'] == B == model['batch_requested_bytes_upper']
    assert ledger['conditional_retain_all_bytes'] == N*B == model['all_batches_requested_bytes_upper']
    assert ledger['metadata_containers_including_initial_upper'] == G*C == counts['lifetime_envelope']['metadata_containers_upper']
    assert ledger['metadata_container_and_edge_units_including_initial_upper'] == G*(C+A) == counts['lifetime_envelope']['metadata_container_and_edge_units_upper']
    assert ledger['initial_generation_storage_upper_bytes'] is None and ledger['complete_verified_H04_upper_bytes'] is None
    assert ledger['fits'] is None and ledger['slack_bytes'] is None and ledger['byte_subtotal_multiplier_is_clone_batches_not_generations']
    assert not model['actual_interpreter_binary_layout_and_allocator_attested'] and not model['total_heap_or_RSS_bound']
    routes = {row['route']: row for row in counts['lifetime_routes']}
    assert routes['page_IO_phase']['batches_upper'] == 32
    assert routes['rejected_or_partial_fork']['batches_upper'] == F and routes['proxy_read_snapshot']['batches_upper'] == S
    assert routes['initial_live_generation']['batches_upper'] == 1
    inventory, unknowns = [], []
    for i, row in enumerate(o['complete_live_allocation_inventory']['required_classes']):
        for key in ['cardinality_upper', 'size_upper_bytes', 'maximum_live_upper_bytes', 'lifetime_derivation']:
            assert row[key] is None
            unknowns.append('/complete_live_allocation_inventory/required_classes/' + str(i) + '/' + key)
        assert not row['verified']
        inventory.append(dict(id=row['id'], record_canonical_sha256=digest(row), unproved_complete_count_size_peak_and_lifetime=True))
    boundaries = o['overlap_alias_original_and_rejected_prefix_treatment']['boundary_requirements']
    assert all(not row['resolved'] for row in boundaries)
    return dict(preparation_commit=o['base_commit'], published_commit=REVIEW_BASE,
                H04_published_blob_oid=published[0], H04_sha256=sha(OUT), input_pin_count=len(checks), input_pin_checks=checks,
                projection_checks=projections, observer_source_files=len(sources), source_anchor_checks=anchors,
                FIELDS_anchor_check=dict(**field_row, module_assignment_verified=True), clone_call_scoped_sites=scoped_sites,
                source_semantics=dict(shared_fork_memo_sites=5, fresh_proxy_memo_sites=2, draft_fast_path_has_no_new_fork=True,
                                      return_IO_and_error_retention_obligations_preserved=True, source_only_not_live_peak_or_execution=True),
                arithmetic_check=dict(weighted_conditional_batch_terms=terms, conditional_batch_bytes=B,
                                      F_upper=F, S_upper=S, clone_batches_upper=N, generations_including_initial_upper=G,
                                      conditional_clone_subtotal_bytes=N*B, initial_generation_bytes=None,
                                      structural_containers_including_initial_upper=G*C,
                                      structural_container_and_edge_units_including_initial_upper=G*(C+A),
                                      no_extra_IO32_or_rejection_F_added=True, conditional_upper_not_actual_lower_bound=True,
                                      no_33_generation_or_immediate_GC_peak_proved=True),
                inventory_checks=inventory, unknown_inventory_pointers=unknowns, unknown_inventory_values=len(unknowns),
                boundary_record_sha256={x['other_owner']: digest(x) for x in boundaries},
                field_record_sha256={x['field']: digest(o[x['field']]) for x in o['field_assessment']},
                source_arithmetic_not_exact_runtime_or_complete_H04_byte_proof=True)

def main():
    validate_preparation()
    o, z, r = rd(OUT), rd(RECON), rd(NEW_REVIEW)
    seal = rd(P + 'D5-I146-integrity.json')
    assert z['base_commit'] == r['base_commit'] == seal['base_commit'] == REVIEW_BASE
    assert z['date'] == r['date'] == seal['date'] == '2026-11-13'
    subprocess.check_call(['git', 'merge-base', '--is-ancestor', REVIEW_BASE, 'HEAD'], cwd=ROOT)
    prior = rd(P + 'D5-I145-integrity.json')
    preserved = {**prior['preserved_published203'], **prior['artifacts'], P + 'D5-I145-integrity.json': sha(P + 'D5-I145-integrity.json')}
    assert seal['preserved_published208'] == preserved and len(preserved) == 208
    for pins in [preserved, seal['artifacts'], z['input_pins'], r['input_pins']]:
        for path, h in pins.items():
            assert sha(path) == h, path
    expected = {NEW_REVIEW, RECON, P + 'D5-I146-audit.py', P + 'D5-I146-integrity.json', 'docs/design/D5-I146-P04-H04-CLONES-MEMO-HEAP-REVIEW.md'}
    assert set(seal['artifacts']) | {P + 'D5-I146-integrity.json'} == expected and len(seal['artifacts']) == 4
    assert set(git('diff', REVIEW_BASE, '--name-only').splitlines()) | set(git('ls-files', '--others', '--exclude-standard').splitlines()) == expected
    if git('rev-parse', 'HEAD') != REVIEW_BASE:
        assert not git('diff', 'HEAD', '--name-only')
    assert z['reconstruction'] == reconstruct() and z['reconstruction']['input_pin_count'] == 150
    assert z['reconstruction']['unknown_inventory_values'] == 48
    assert r['contract_id'] == z['contract_id'] == o['candidate_binding']['contract_id'] == 'PFC126-CANDIDATE-03'
    assert r['H04'] == dict(path=OUT, sha256=sha(OUT), bytes_preserved=True) and r['plan_binding'] == o['plan_binding']
    assert r['source_reconstruction'] == dict(path=RECON, sha256=sha(RECON))
    assert r['status'] == 'REVIEW_COMPLETE_DOSSIER_CONFORMANT_H04_PROOF_REJECTED_NO_ADMISSION'
    assert r['field_disposition'] == [dict(field=x['field'], I145_result=x['result'],
            I146_result='CONFIRMED_DOCUMENTARY_DEFINITION_ONLY' if x['result']=='DOCUMENTARY_DEFINITION_ONLY' else 'CONFIRMED_INSUFFICIENT_FOR_H04_ACCEPTANCE',
            record_canonical_sha256=digest(o[x['field']]), closed=False) for x in o['field_assessment']]
    assert len(r['checks']) == 14 and [x['id'] for x in r['checks']] == ['R%02d'%i for i in range(1,15)]
    for check in r['checks']:
        assert check['result'] == 'CONFORMANT_DOCUMENTARY_INSUFFICIENCY_JUDGMENT' and not check['resource_obligation_closed']
    assert r['blocking_dossier_defects'] == [] and r['documentary_dossier_conformance'] and not r['H04_change_required']
    assert r['reviewer']['same_assistant_as_preparer'] and r['reviewer']['methodologically_separate_reconstruction']
    assert not r['reviewer']['actor_or_organizational_independence_attested'] and not r['reviewer']['runtime_custodian_authority_claimed']
    assert r['acceptance'] == dict(review_completed=True, insufficiency_judgment_confirmed=True, accepted_as_complete_H04_proof=False,
                                 H04_verified=False, independent_documentary_acceptance=False, independent_reviewer_identity=None,
                                 E02_closed=False, E01_E05_closed=False, resource_obligations_closed=0, fit_or_overbudget_proved=False)
    assert r['E02_criterion_disposition'] == [dict(id=x['id'], I146_result=x['inherited_result'], closed=False) for x in o['E02_criterion_disposition']]
    assert r['counts'] == dict(H04_input_pins_checked=150, evidence_projections_checked=13, observer_source_files=8,
                              symbol_anchors_checked=11, FIELDS_anchors_checked=1, clone_call_syntax_sites=13,
                              required_fields=9, documentary_definition_fields=2, insufficient_fields=7, required_allocation_classes=12,
                              unknown_inventory_values=48, unresolved_owner_boundaries=10, E02_criteria_preserved=4, checks=14,
                              other_unproduced_packages=13)
    assert r['decision'] == o['decision'] and r['E06'] == o['E06'] and r['other_packages_started'] == 0
    assert r['verified_complete_upper_bytes'] is None and r['fits'] is None and r['slack_bytes'] is None
    assert r['pending_independent_acceptance_and_P02_P03_not_bypassed']
    assert set(r['work_unit']['rollback_files']) == expected and r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command'] == 'python3 docs/validation/D5-I146-audit.py'
    assert r['work_unit']['expected_result'] == 'PASS_STATIC_SOURCE_ONLY' and r['work_unit']['diff_budget_note']
    assert seal['source_only'] and not seal['proposal_enabled'] and r['git_publication']['commit_and_push_all_requested']
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY', increment='I146', package='P04-H04', documentary_dossier_conformance=True,
                         accepted_as_complete_H04_proof=False, independent_acceptance=False, Git_input_pins_checked=150,
                         observer_source_files=8, evidence_projections=13, source_anchors=12, insufficient_fields=7,
                         clone_batches_upper=53777, generations_including_initial_upper=53778,
                         prior_published_files_preserved=208, new_files=5, product_or_components_executed=0, quotas_changed=False,
                         resource_obligations_closed=0, proposal_enabled=False, D5_closed=False, IR03='NOT_READY', git_head=git('rev-parse','HEAD')), sort_keys=True))

if __name__ == '__main__':
    main()
