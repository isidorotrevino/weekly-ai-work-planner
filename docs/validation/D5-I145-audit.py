#!/usr/bin/env python3
"""Documentary H04 audit: Git blobs, JSON, AST and inherited integer arithmetic.
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

def main():
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
    assert set(git('diff', BASE, '--name-only').splitlines()) | set(git('ls-files', '--others', '--exclude-standard').splitlines()) == expected
    if git('rev-parse', 'HEAD') != BASE:
        assert not git('diff', 'HEAD', '--name-only')
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
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY', increment='I145', package='P04-H04', preparation_complete=True, accepted_as_complete_H04_proof=False, candidate_budget_bytes=6442450944, insufficient_fields=7, generations_including_initial=53778, prior_published_files_preserved=203, new_files=5, product_or_components_executed=0, quotas_changed=False, resource_obligations_closed=0, proposal_enabled=False, D5_closed=False, IR03='NOT_READY', git_head=git('rev-parse', 'HEAD')), sort_keys=True))

if __name__ == '__main__':
    main()
