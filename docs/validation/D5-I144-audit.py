#!/usr/bin/env python3
"""Audit the I144 H03 review using documentary consistency and fresh Git/AST reconstruction.
No target imports, components, allocation probes, quota changes or resource proof.
"""
import ast
import hashlib
import io
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '89725ddaa0e5d056362fa106a40036bf251b0234'
OUT = P + 'D5-PFC126-03-E02-H03.json'
REVIEW = P + 'D5-I143-P04-H03-preparation-review.json'
PLAN = P + 'D5-I132-E01-E05-evidence-plan.json'
CONTRACT = P + 'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
SCOPE = P + 'D5-PFC126-03-RESOURCE-SCOPE.json'
RUNTIME = P + 'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
PLATFORM = P + 'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
H01 = P + 'D5-PFC126-03-E02-H01.json'
H02 = P + 'D5-PFC126-03-E02-H02.json'
ATOMIC = 'testing/prospective_capture_joint_i122/atomic.py'
BASE_SOURCE = 'testing/prospective_capture/capture.py'
PROJECTIONS = [
    (CONTRACT, '/heap/owner_budgets/2'),
    (CONTRACT, '/runtime/required_identity_pins'),
    (P + 'D5-I125-complete-heap-review.json', '/required_terms/2'),
    (RUNTIME, '/acceptance'),
    (P + 'D5-I136-P02-documentary-review.json', '/acceptance'),
    (PLATFORM, '/acceptance'),
    (P + 'D5-I138-P03-documentary-review.json', '/acceptance'),
    (H02, '/acceptance'),
    (P + 'D5-I142-P04-H02-documentary-review.json', '/acceptance'),
    (SCOPE, '/worker_heap_vs_other_process_scope'),
    (H01, '/acceptance'),
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
    for part in path.strip('/').split('/'):
        key = part.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value

def source_evidence(pins):
    paths = sorted(pins)
    requests = ''.join(BASE + ':' + path + '\n' for path in paths).encode()
    stream = io.BytesIO(subprocess.check_output(['git', 'cat-file', '--batch'], cwd=ROOT, input=requests))
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
        projections.append(dict(path=path, sha256=pins[path], json_pointer=ptr,
                                observed_value=value, canonical_sha256=digest(value), resource_obligation_closed=False))
    scope = json.loads(data[SCOPE])
    sources = scope['I122_and_original_source_pin_set']['observer_static_repo_import_superset']['file_pins']
    trees, indices, summaries = {}, {}, []
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
        stores = sorted([
            dict(line=n.lineno, column=n.col_offset, attribute=n.attr,
                 AST_sha256=hashlib.sha256(ast.dump(n, include_attributes=False).encode()).hexdigest())
            for n in ast.walk(tree) if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store)
            and isinstance(n.value, ast.Name) and n.value.id == 'self'
        ], key=lambda x: (x['line'], x['column'], x['attribute']))
        summaries.append(dict(path=path, sha256=h, self_attribute_store_sites=len(stores),
                              literal_attributes=sorted({x['attribute'] for x in stores}), store_vector_sha256=digest(stores)))
    field_nodes = [n for n in trees[ATOMIC].body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'FIELDS' for t in n.targets)]
    assert len(field_nodes) == 1
    fields = ast.literal_eval(field_nodes[0].value)
    specs = [
        (ATOMIC, 'build.Recorder.__init__'), (ATOMIC, 'build.Recorder._fork'),
        (ATOMIC, 'build.Recorder._publish'), (ATOMIC, 'build.Bindings.__init__'),
        (BASE_SOURCE, 'Recorder.__init__'), (BASE_SOURCE, 'Recorder.owner'),
        (BASE_SOURCE, 'Recorder.patch'), (BASE_SOURCE, 'Recorder.restore'),
        ('testing/prospective_capture_typed/capture.py', 'Recorder.__init__'),
        ('testing/prospective_capture_late/capture.py', 'LateBindings.__init__'),
        ('testing/prospective_capture_joint_i122/capture.py', 'CausalState.__init__'),
        ('testing/prospective_capture_joint_i122/capture.py', 'ParentalState.__init__'),
        ('testing/prospective_capture_joint_i122/capture.py', 'DomainState.__init__'),
    ]
    anchors, constructors, nodes = [], [], {}
    for path, symbol in specs:
        assert len(indices[path][symbol]) == 1
        node = indices[path][symbol][0]
        nodes[(path, symbol)] = node
        anchors.append(dict(path=path, sha256=sources[path], symbol=symbol, line=node.lineno,
                            end_line=node.end_lineno, AST_sha256=hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()))
        if symbol.endswith('__init__'):
            names = sorted({n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)
                            and isinstance(n.ctx, ast.Store) and isinstance(n.value, ast.Name) and n.value.id == 'self'})
            constructors.append(dict(path=path, symbol=symbol, literal_self_attributes=names,
                                     attributes_outside_FIELDS=sorted(set(names) - set(fields)),
                                     source_candidates_not_complete_root_or_owner_assignment=True))
    field = field_nodes[0]
    field_anchor = dict(path=ATOMIC, sha256=sources[ATOMIC], symbol='FIELDS', line=field.lineno,
                        end_line=field.end_lineno, AST_sha256=hashlib.sha256(ast.dump(field, include_attributes=False).encode()).hexdigest())
    init = nodes[(ATOMIC, 'build.Recorder.__init__')]
    expressions = {ast.unparse(n) for n in ast.walk(init)}
    required = ['threading.RLock()', 'threading.Condition(self._state_lock)',
                'self._ref_lock = self._state_lock', 'self._emit_lock = self._state_lock',
                'bindings._owner = self', 'bindings.on_reference = self.reference']
    assert all(expr in expressions for expr in required)
    assert any(isinstance(n, ast.Call) and ast.unparse(n.func) == 'p.t.Recorder.__init__' for n in ast.walk(init))
    fork = nodes[(ATOMIC, 'build.Recorder._fork')]
    assert any(isinstance(n, ast.Call) and ast.unparse(n) == 'draft.__dict__.update(self.__dict__)' for n in ast.walk(fork))
    base_init = nodes[(BASE_SOURCE, 'Recorder.__init__')]
    assert any(isinstance(n, ast.Call) and ast.unparse(n.func) == 'threading.local' for n in ast.walk(base_init))
    owner = nodes[(BASE_SOURCE, 'Recorder.owner')]
    assert any(isinstance(n, ast.Call) and ast.unparse(n) == 'weakref.ref(obj)' for n in ast.walk(owner))
    patch = nodes[(BASE_SOURCE, 'Recorder.patch')]
    assert any(isinstance(n, ast.Call) and ast.unparse(n) == 'self.patches.append((cls, name, old, replacement))' for n in ast.walk(patch))
    restore = nodes[(BASE_SOURCE, 'Recorder.restore')]
    assert any(isinstance(n, ast.Call) and ast.unparse(n) == 'self.patches.clear()' for n in ast.walk(restore))
    return dict(commit=BASE, input_pin_count=len(checks), input_blob_checks=checks, projections=projections,
                observer_source_files=len(sources), observer_file_summaries=summaries, copied_FIELDS=list(fields),
                FIELDS_anchor=field_anchor, source_anchors=anchors, constructor_attribute_candidates=constructors,
                source_semantics=dict(shared_lock_and_condition_aliases_declared=True, owner_callback_backlinks_declared=True,
                                      typed_initializer_called_directly=True, draft_shallow_copies_root_dictionary=True,
                                      thread_local_and_weakref_and_patch_storage_identified=True,
                                      restore_clears_patch_list_not_complete_reachability_proof=True),
                source_candidates_not_complete_loaded_allocation_or_lifetime_model=True, no_target_modules_executed=True)

def validate_preparation():
    o, r = rd(OUT), rd(REVIEW)
    seal, c, s = rd(P + 'D5-I143-integrity.json'), rd(CONTRACT), rd(SCOPE)
    plan = rd(PLAN)
    task, owner = plan['tasks'][5], c['heap']['owner_budgets'][2]
    assert o['base_commit'] == r['base_commit'] == seal['base_commit'] == BASE
    assert o['date'] == r['date'] == seal['date'] == '2026-11-13'
    subprocess.check_call(['git', 'merge-base', '--is-ancestor', BASE, 'HEAD'], cwd=ROOT)
    prior = rd(P + 'D5-I142-integrity.json')
    preserved = {**prior['preserved_published188'], **prior['artifacts'], P + 'D5-I142-integrity.json': sha(P + 'D5-I142-integrity.json')}
    assert seal['preserved_published193'] == preserved and len(preserved) == 193
    for pins in [preserved, seal['artifacts'], o['input_pins'], r['input_pins'], rd(P + 'D5-I119-integrity.json')['inherited_inputs477']]:
        for path, h in pins.items():
            assert sha(path) == h, path
    expected = {OUT, REVIEW, P + 'D5-I143-audit.py', P + 'D5-I143-integrity.json', 'docs/design/D5-I143-P04-H03-PERSISTENT-OBSERVER-HEAP.md'}
    assert set(seal['artifacts']) | {P + 'D5-I143-integrity.json'} == expected and len(seal['artifacts']) == 4
    assert o['source_evidence'] == source_evidence(o['input_pins'])
    assert o['source_evidence']['observer_source_files'] == 8 and len(o['source_evidence']['source_anchors']) == 13
    assert len(o['source_evidence']['projections']) == 11 and len(o['input_pins']) == 145
    assert o['package_id'] == task['id'] == 'P04-H03' and OUT == task['planned_output'] and o['schema'] == task['output_schema']
    assert o['plan_binding'] == dict(path=PLAN, sha256=sha(PLAN), package_id='P04-H03', task_record_canonical_sha256=digest(task))
    assert o['candidate_binding'] == dict(path=CONTRACT, sha256=sha(CONTRACT), contract_id=c['contract_id'], subject=c['subject'], source_revision='I122-CANDIDATE-01')
    assert set(task['required_specific_fields']) <= set(o) and len(task['required_specific_fields']) == 9
    assert o['candidate_budget_bytes=536870912'] == o['candidate_budget_bytes'] == owner['candidate_budget_bytes'] == 512 * 1024**2
    assert o['candidate_owner_record'] == owner and owner['proof_upper_bytes'] is None
    assert o['status'] == 'PREPARED_INSUFFICIENT_PERSISTENT_OBSERVER_HEAP_H03_E02_OPEN_NOT_ADMITTED'
    assert o['owner_id_metric_and_exact_units'] == dict(owner_id='H03', owner=owner['owner'], metric=owner['metric'], unit='exact_integer_bytes', process='I122 worker observer', candidate_budget_bytes=536870912, scope_is_requirement_not_verified_bound=True)
    inventory = o['complete_live_allocation_inventory']
    assert not inventory['complete'] and len(inventory['required_classes']) == 12
    assert inventory['kind'] == 'TWELVE_REQUIRED_OBSERVER_COVERAGE_CLASSES_NOT_COMPLETE_ALLOCATION_PROOF' and inventory['residual_transitive_roots_not_proved_absent']
    for i, row in enumerate(inventory['required_classes'], 1):
        assert row['id'] == 'R%02d' % i and not row['verified'] and row['required_coverage'] and row['runtime_dependency']
        assert all(row[k] is None for k in ['cardinality_upper', 'size_upper_bytes', 'maximum_live_upper_bytes', 'lifetime_derivation'])
    abi = o['source_ABI_allocator_dependencies']
    assert abi['historical_runtime_reference'] == c['runtime'] and not abi['exact_runtime_ABI_or_allocator_correspondence_verified']
    assert all(abi[k] is None for k in ['accepted_target_closure', 'accepted_ABI_size_model', 'complete_observer_native_size_model', 'allocator_metric_correspondence'])
    deriv = o['cardinality_size_lifetime_derivations']
    assert not deriv['complete'] and deriv['whole_owner_live_upper_bytes'] is None
    assert deriv['FIELDS_and_logical_quotas_not_complete_heap_inventory'] and deriv['no_interning_or_alias_slack_inferred'] and deriv['restore_clear_not_complete_root_release']
    overlap = o['overlap_alias_original_and_rejected_prefix_treatment']
    assert overlap['inherited_scope'] == s['worker_heap_vs_other_process_scope'] and overlap['source_applicability'] == s['321_root_12_group_applicability']['I124_applicability']
    assert [x['other_owner'] for x in overlap['boundary_requirements']] == ['H01', 'H02'] + ['H%02d' % i for i in range(4, 12)]
    assert all(not x['resolved'] for x in overlap['boundary_requirements']) and not overlap['complete_ownership_alias_lifetime_proof']
    assert overlap['weakrefs_not_strong_referent_charge_or_zero_structure_cost'] and overlap['original_referents_not_paid_by_observer_containers']
    dep = o['explicit_assumptions_and_external_dependencies']
    assert not dep['assumptions_verified'] and not dep['P02_exact_runtime_identity_accepted'] and not dep['P03_capacity_service_accepted']
    assert all(dep[k] is None for k in ['complete_observer_root_native_model', 'exact_runtime_size_lifetime_material', 'independent_runtime_memory_review'])
    assert dep['negative_dossier_does_not_bypass_P01_P02'] and dep['other_owner_or_capacity_not_substitute_for_H03_demand'] and dep['later_resource_closure_not_started']
    assert dep['inherited_P01_preconditions'] == s['321_root_12_group_applicability']['original_source_route_preconditions']
    assert o['verified_upper_bytes_and_derivation'] == dict(verified_upper_bytes=None, complete_derivation=None, evidence_pins={}, verified=False, unknown_not_zero=True, logical_counts_payload_and_file_sizes_not_heap_upper=True)
    assert o['bound_fit_not_just_partial_payload'] == dict(candidate_budget_bytes=536870912, verified_complete_upper_bytes=None, fit_result='NOT_EVALUABLE_NO_COMPLETE_H03_BOUND', fits=None, slack_bytes=None, overbudget_proved=False, actual_unboundedness_proved=False, partial_payload_not_accepted=True)
    assert [x['field'] for x in o['field_assessment']] == task['required_specific_fields']
    for row in o['field_assessment']:
        expected_result = 'DOCUMENTARY_DEFINITION_ONLY' if row['field'] in ['owner_id_metric_and_exact_units', 'candidate_budget_bytes=536870912'] else 'INSUFFICIENT_FOR_ACCEPTANCE'
        assert row['result'] == expected_result and not row['resource_obligation_closed'] and row['basis']
    assert o['acceptance'] == dict(rule=task['acceptance'], rejection_rule=task['rejection'], preparation_complete=True, accepted_as_complete_H03_proof=False, H03_verified=False, E02_closed=False, resource_obligations_closed=0, no_reserve_transfer=True)
    for d, path in zip(o['dependencies'], [SCOPE, RUNTIME], strict=True):
        assert d['path'] == path and d['sha256'] == sha(path) and not d['accepted_for_resource_closure']
    assert [x['id'] for x in o['dependencies']] == task['depends_on'] == ['P01', 'P02']
    assert not rd(RUNTIME)['acceptance']['accepted_as_runtime_identity'] and not rd(PLATFORM)['acceptance']['accepted_as_platform_evidence']
    provenance = o['producer_and_review_provenance']
    assert provenance['producer_identity'] == 'Codex assistant preparing I143 in this chat'
    assert provenance['planned_author_role'] == task['responsible_role'] and provenance['planned_review_role'] == task['review_role']
    assert provenance['independent_reviewer_identity'] is None and not provenance['independent_acceptance'] and not provenance['runtime_custodian_authority_claimed']
    assert o['reserve_accounting'] == c['reserve_accounting'] and o['non_execution_and_zero_transfer_policy'] == s['non_execution_and_zero_transfer_policy']
    criteria = rd(P + 'D5-I131-E01-E05-review.json')['obligations'][1]['criteria']
    assert o['E02_criterion_disposition'] == [dict(id=x['id'], inherited_result=x['result'], I143_result=x['result'], closed=False) for x in criteria]
    assert r['output'] == dict(path=OUT, sha256=sha(OUT), schema=o['schema'], evidence_kind=o['evidence_kind'], produced=True)
    assert r['input_pins'][OUT] == sha(OUT) and all(r['preparation_checks'].values())
    assert r['status'] == 'P04_H03_PREPARATION_COMPLETE_NO_COMPLETE_BOUND_NO_ADMISSION'
    assert not o['external_material_scope']['external_contacts_made'] and not o['external_material_scope']['global_absence_claimed'] and not o['external_material_scope']['runtime_or_platform_sampled']
    assert set(r['work_unit']['rollback_files']) == expected
    assert r['work_unit']['verification_command'] == 'python3 docs/validation/D5-I143-audit.py' and r['work_unit']['expected_result'] == 'PASS_STATIC_SOURCE_ONLY'
    assert r['work_unit']['runtime_harness'].startswith('N/A:') and r['work_unit']['diff_budget_note']
    assert r['counts'] == dict(required_fields=9, documentary_definition_fields=2, insufficient_fields=7, required_allocation_classes=12, unknown_inventory_values=48, owner_boundaries=10, observer_source_files=8, source_anchors=14, evidence_projections=11, input_pins=145, other_unproduced_packages=14)
    assert r['independent_review'] == dict(accepted=False, reviewer_identity=None, no_independent_review_fabricated=True)
    assert len(r['package_progress']) == 20
    for progress, t in zip(r['package_progress'], plan['tasks'], strict=True):
        exists = t['id'] in ['P01', 'P02', 'P03', 'P04-H01', 'P04-H02', 'P04-H03']
        assert (ROOT / t['planned_output']).exists() == exists and progress['output_created'] == exists
        assert progress['package_id'] == t['id'] and progress['path'] == t['planned_output'] and progress['sha256'] == (sha(t['planned_output']) if exists else None)
    for d in [o['decision'], r['decision']]:
        true_keys = {'candidate_plan_prior_packages_and_source_bytes_preserved', 'numeric_candidates_unchanged', 'P0_D1_D4_I1_I20_A52_unchanged', 'global_gaps_and_real_obligations_pending', 'I86_I89_I92_not_resumed'}
        assert d['certificate_unchanged'] == rd(P + 'D5-I122-CAPACITY-CERTIFICATE.json')['status'] == 'IMPLEMENTED_NOT_ADMITTED'
        assert d['IR03'] == 'NOT_READY' and d['resource_obligations_closed'] == 0
        for key in true_keys:
            assert d[key] is True
        for key, value in d.items():
            if key not in true_keys | {'certificate_unchanged', 'IR03', 'resource_obligations_closed'}:
                assert value is False, key
    assert o['E06'] == r['E06'] == dict(status='SEPARATE_PENDING_NOT_RUN', components_executed=0, execution_authorized=False)
    for path in [P + 'D5-JOINT-capture-authorization.json', P + 'D5-JOINT-P01', P + 'D5-JOINT-P01-launch.json']:
        assert not (ROOT / path).exists()
    assert seal['source_only'] and not seal['proposal_enabled'] and r['git_publication']['commit_and_push_all_requested']

REVIEW_BASE = '9db9e526959579d43fe6fe3351de46b20f037c8b'
NEW_REVIEW = P + 'D5-I144-P04-H03-documentary-review.json'
RECON = P + 'D5-I144-P04-H03-source-reconstruction.json'

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
    projections = []
    evidence = o['source_evidence']
    assert [(x['path'], x['json_pointer']) for x in evidence['projections']] == PROJECTIONS
    for row in evidence['projections']:
        value = pointer(json.loads(data[row['path']][1]), row['json_pointer'])
        assert value == row['observed_value'] and digest(value) == row['canonical_sha256']
        assert o['input_pins'][row['path']] == row['sha256']
        projections.append(dict(path=row['path'], sha256=row['sha256'], json_pointer=row['json_pointer'],
                                recomputed_value_sha256=digest(value), matches_published_projection=True))
    scope = json.loads(data[SCOPE][1])
    sources = scope['I122_and_original_source_pin_set']['observer_static_repo_import_superset']['file_pins']
    summaries, trees, indices = [], {}, {}
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
        Lexical().visit(tree)
        indices[path] = index
        stores = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store) and isinstance(n.value, ast.Name) and n.value.id == 'self':
                stores.append(dict(line=n.lineno, column=n.col_offset, attribute=n.attr,
                                   AST_sha256=hashlib.sha256(ast.dump(n, include_attributes=False).encode()).hexdigest()))
        stores.sort(key=lambda x: (x['line'], x['column'], x['attribute']))
        summaries.append(dict(path=path, sha256=h, self_attribute_store_sites=len(stores),
                              literal_attributes=sorted({x['attribute'] for x in stores}), store_vector_sha256=digest(stores)))
    assert summaries == evidence['observer_file_summaries']
    anchors, constructors, nodes = [], [], {}
    for row in evidence['source_anchors']:
        candidates = indices[row['path']][row['symbol']]
        assert len(candidates) == 1
        node = candidates[0]
        assert (node.lineno, node.end_lineno) == (row['line'], row['end_line'])
        assert hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest() == row['AST_sha256']
        assert sources[row['path']] == row['sha256']
        nodes[(row['path'], row['symbol'])] = node
        anchors.append(dict(**row, lexical_binding_verified=True))
    field_row = evidence['FIELDS_anchor']
    candidates = [n for n in trees[ATOMIC].body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'FIELDS' for t in n.targets)]
    assert len(candidates) == 1
    field_node = candidates[0]
    assert (field_node.lineno, field_node.end_lineno) == (field_row['line'], field_row['end_line'])
    assert hashlib.sha256(ast.dump(field_node, include_attributes=False).encode()).hexdigest() == field_row['AST_sha256']
    fields = list(ast.literal_eval(field_node.value))
    assert fields == evidence['copied_FIELDS'] and len(fields) == 22
    for row in evidence['source_anchors']:
        if not row['symbol'].endswith('__init__'):
            continue
        node = nodes[(row['path'], row['symbol'])]
        names = sorted({n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)
                        and isinstance(n.ctx, ast.Store) and isinstance(n.value, ast.Name) and n.value.id == 'self'})
        constructors.append(dict(path=row['path'], symbol=row['symbol'], literal_self_attributes=names,
                                 attributes_outside_FIELDS=sorted(set(names) - set(fields)),
                                 source_candidates_not_complete_root_or_owner_assignment=True))
    assert constructors == evidence['constructor_attribute_candidates'] and len(constructors) == 8
    init = nodes[(ATOMIC, 'build.Recorder.__init__')]
    required = ['threading.RLock()', 'threading.Condition(self._state_lock)',
                'self._ref_lock = self._state_lock', 'self._emit_lock = self._state_lock',
                'bindings._owner = self', 'bindings.on_reference = self.reference']
    assert set(required) <= {ast.unparse(n) for n in ast.walk(init)}
    direct_calls = [n for n in ast.walk(init) if isinstance(n, ast.Call) and ast.unparse(n.func) == 'p.t.Recorder.__init__']
    assert len(direct_calls) == 1
    semantics = [dict(topic='lock_condition_and_callback_aliases', source_expressions=required,
                      declaration_not_identity_or_native_size_proof=True)]
    for symbol, expected in [
        ((ATOMIC, 'build.Recorder._fork'), 'draft.__dict__.update(self.__dict__)'),
        ((ATOMIC, 'build.Recorder._publish'), 'causal.charge = self.reference'),
        ((BASE_SOURCE, 'Recorder.__init__'), 'threading.local()'),
        ((BASE_SOURCE, 'Recorder.owner'), 'weakref.ref(obj)'),
        ((BASE_SOURCE, 'Recorder.patch'), 'self.patches.append((cls, name, old, replacement))'),
        ((BASE_SOURCE, 'Recorder.restore'), 'self.patches.clear()'),
    ]:
        assert expected in {ast.unparse(n) for n in ast.walk(nodes[symbol])}
        semantics.append(dict(path=symbol[0], symbol=symbol[1], expression=expected,
                              source_match=True, no_runtime_or_lifetime_proof=True))
    inventory_checks, unknowns = [], []
    for i, row in enumerate(o['complete_live_allocation_inventory']['required_classes']):
        for key in ['cardinality_upper', 'size_upper_bytes', 'maximum_live_upper_bytes', 'lifetime_derivation']:
            assert row[key] is None
            unknowns.append('/complete_live_allocation_inventory/required_classes/' + str(i) + '/' + key)
        assert not row['verified']
        inventory_checks.append(dict(id=row['id'], record_canonical_sha256=digest(row), unproved_size_count_peak_and_lifetime=True))
    boundaries = o['overlap_alias_original_and_rejected_prefix_treatment']['boundary_requirements']
    assert all(not row['resolved'] for row in boundaries)
    return dict(preparation_commit=o['base_commit'], published_commit=REVIEW_BASE,
                H03_published_blob_oid=published[0], H03_sha256=sha(OUT), input_pin_count=len(checks),
                input_pin_checks=checks, projection_checks=projections, observer_source_files=len(sources),
                observer_summary_vector_sha256=digest(summaries), source_anchor_checks=anchors,
                FIELDS_anchor_check=dict(**field_row, module_assignment_verified=True), copied_FIELDS=fields,
                constructor_attribute_candidates=constructors, source_semantics_checks=semantics,
                inventory_checks=inventory_checks, unknown_inventory_pointers=unknowns,
                unknown_inventory_values=len(unknowns),
                boundary_record_sha256={x['other_owner']: digest(x) for x in boundaries},
                field_record_sha256={x['field']: digest(o[x['field']]) for x in o['field_assessment']},
                source_only_not_MRO_loaded_identity_native_sizes_or_lifetime_proof=True)

def main():
    validate_preparation()
    o, z, r = rd(OUT), rd(RECON), rd(NEW_REVIEW)
    seal = rd(P + 'D5-I144-integrity.json')
    assert z['base_commit'] == r['base_commit'] == seal['base_commit'] == REVIEW_BASE
    assert z['date'] == r['date'] == seal['date'] == '2026-11-13'
    subprocess.check_call(['git', 'merge-base', '--is-ancestor', REVIEW_BASE, 'HEAD'], cwd=ROOT)
    prior = rd(P + 'D5-I143-integrity.json')
    preserved = {**prior['preserved_published193'], **prior['artifacts'], P + 'D5-I143-integrity.json': sha(P + 'D5-I143-integrity.json')}
    assert seal['preserved_published198'] == preserved and len(preserved) == 198
    for pins in [preserved, seal['artifacts'], z['input_pins'], r['input_pins']]:
        for path, h in pins.items():
            assert sha(path) == h, path
    expected = {NEW_REVIEW, RECON, P + 'D5-I144-audit.py', P + 'D5-I144-integrity.json', 'docs/design/D5-I144-P04-H03-PERSISTENT-OBSERVER-HEAP-REVIEW.md'}
    assert set(seal['artifacts']) | {P + 'D5-I144-integrity.json'} == expected and len(seal['artifacts']) == 4
    assert set(git('diff', REVIEW_BASE, '--name-only').splitlines()) | set(git('ls-files', '--others', '--exclude-standard').splitlines()) == expected
    if git('rev-parse', 'HEAD') != REVIEW_BASE:
        assert not git('diff', 'HEAD', '--name-only')
    assert z['reconstruction'] == reconstruct() and z['reconstruction']['input_pin_count'] == 145
    assert z['reconstruction']['unknown_inventory_values'] == 48
    assert r['contract_id'] == z['contract_id'] == o['candidate_binding']['contract_id'] == 'PFC126-CANDIDATE-03'
    assert r['H03'] == dict(path=OUT, sha256=sha(OUT), bytes_preserved=True) and r['plan_binding'] == o['plan_binding']
    assert r['source_reconstruction'] == dict(path=RECON, sha256=sha(RECON))
    assert r['status'] == 'REVIEW_COMPLETE_DOSSIER_CONFORMANT_H03_PROOF_REJECTED_NO_ADMISSION'
    assert r['field_disposition'] == [dict(field=x['field'], I143_result=x['result'],
            I144_result='CONFIRMED_DOCUMENTARY_DEFINITION_ONLY' if x['result'] == 'DOCUMENTARY_DEFINITION_ONLY' else 'CONFIRMED_INSUFFICIENT_FOR_H03_ACCEPTANCE',
            record_canonical_sha256=digest(o[x['field']]), closed=False) for x in o['field_assessment']]
    assert len(r['checks']) == 14 and [x['id'] for x in r['checks']] == ['R%02d' % i for i in range(1, 15)]
    for check in r['checks']:
        assert check['result'] == 'CONFORMANT_DOCUMENTARY_INSUFFICIENCY_JUDGMENT' and not check['resource_obligation_closed']
    assert r['blocking_dossier_defects'] == [] and r['documentary_dossier_conformance'] and not r['H03_change_required']
    assert r['reviewer']['same_assistant_as_preparer'] and r['reviewer']['methodologically_separate_reconstruction']
    assert not r['reviewer']['actor_or_organizational_independence_attested'] and not r['reviewer']['runtime_custodian_authority_claimed']
    assert r['acceptance'] == dict(review_completed=True, insufficiency_judgment_confirmed=True, accepted_as_complete_H03_proof=False,
                                 H03_verified=False, independent_documentary_acceptance=False, independent_reviewer_identity=None,
                                 E02_closed=False, E01_E05_closed=False, resource_obligations_closed=0, fit_or_overbudget_proved=False)
    assert r['E02_criterion_disposition'] == [dict(id=x['id'], I144_result=x['inherited_result'], closed=False) for x in o['E02_criterion_disposition']]
    assert r['counts'] == dict(H03_input_pins_checked=145, evidence_projections_checked=11, observer_source_files=8,
                              symbol_anchors_checked=13, FIELDS_anchors_checked=1, copied_FIELDS=22, constructor_attribute_lists=8,
                              required_fields=9, documentary_definition_fields=2, insufficient_fields=7, required_allocation_classes=12,
                              unknown_inventory_values=48, unresolved_owner_boundaries=10, E02_criteria_preserved=4, checks=14,
                              other_unproduced_packages=14)
    assert r['decision'] == o['decision'] and r['E06'] == o['E06'] and r['other_packages_started'] == 0
    assert r['verified_complete_upper_bytes'] is None and r['fits'] is None and r['slack_bytes'] is None
    assert r['pending_independent_acceptance_and_P02_P03_not_bypassed']
    assert set(r['work_unit']['rollback_files']) == expected and r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command'] == 'python3 docs/validation/D5-I144-audit.py'
    assert r['work_unit']['expected_result'] == 'PASS_STATIC_SOURCE_ONLY' and r['work_unit']['diff_budget_note']
    assert seal['source_only'] and not seal['proposal_enabled'] and r['git_publication']['commit_and_push_all_requested']
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY', increment='I144', package='P04-H03', documentary_dossier_conformance=True,
                         accepted_as_complete_H03_proof=False, independent_acceptance=False, Git_input_pins_checked=145,
                         observer_source_files=8, evidence_projections=11, source_anchors=14, insufficient_fields=7,
                         prior_published_files_preserved=198, new_files=5, product_or_components_executed=0, quotas_changed=False,
                         resource_obligations_closed=0, proposal_enabled=False, D5_closed=False, IR03='NOT_READY', git_head=git('rev-parse', 'HEAD')), sort_keys=True))

if __name__ == '__main__':
    main()
