#!/usr/bin/env python3
"""I147 H05 documentary audit: JSON, Git objects and source AST only.
No target imports, frame/generator execution, introspection or allocation probes.
"""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'a79acf8cdee443af5321bfc2b204e2d63af2a4f1'
OUT = P + 'D5-PFC126-03-E02-H05.json'
REVIEW = P + 'D5-I147-P04-H05-preparation-review.json'
PLAN = P + 'D5-I132-E01-E05-evidence-plan.json'
CONTRACT = P + 'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
SCOPE = P + 'D5-PFC126-03-RESOURCE-SCOPE.json'
RUNTIME = P + 'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
PLATFORM = P + 'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
H04 = P + 'D5-PFC126-03-E02-H04.json'
I124 = P + 'D5-I124-global-batch-lifetime-proof.json'
ATOMIC = 'testing/prospective_capture_joint_i122/atomic.py'
BASE_SOURCE = 'testing/prospective_capture/capture.py'
WORKER = 'testing/prospective_capture_joint_i122/worker.py'
PROJECTIONS = [
    (CONTRACT, '/heap/owner_budgets/4'),
    (P + 'D5-I125-complete-heap-review.json', '/required_terms/4'),
    (P + 'D5-I123-transient-resource-envelope.json', '/memory/symbols/w'),
    (P + 'D5-I123-transient-resource-envelope.json', '/memory/ABI_allocation_coefficients_verified'),
    (I124, '/lifetime_envelope'), (I124, '/scope'), (RUNTIME, '/acceptance'), (PLATFORM, '/acceptance'),
    (P + 'D5-I146-P04-H04-documentary-review.json', '/acceptance'),
    (H04, '/cardinality_size_lifetime_derivations'),
    (SCOPE, '/worker_heap_vs_other_process_scope'), (CONTRACT, '/product_numeric_candidates'),
]
CENSUS_KINDS = ['FunctionDef', 'AsyncFunctionDef', 'GeneratorExp', 'Yield', 'YieldFrom',
                'ListComp', 'SetComp', 'DictComp', 'ExceptHandler', 'Raise']


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
    source_sets = scope['I122_and_original_source_pin_set']
    sources = {**source_sets['runner_registered_input_pins'], **source_sets['observer_static_repo_import_superset']['file_pins']}
    sources = {path: h for path, h in sources.items() if path.endswith('.py')}
    trees, indices, rows, summaries = {}, {}, [], []
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
        sites = []
        for node in ast.walk(tree):
            kind = type(node).__name__
            if kind in CENSUS_KINDS:
                sites.append(dict(kind=kind, line=node.lineno, column=node.col_offset, end_line=node.end_lineno,
                                  AST_sha256=hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()))
        sites.sort(key=lambda x: (x['line'], x['column'], x['kind']))
        summaries.append(dict(path=path, sha256=h, syntax_counts={kind:sum(x['kind']==kind for x in sites) for kind in CENSUS_KINDS},
                              syntax_site_vector_sha256=digest(sites)))
        rows.extend(dict(path=path, **site) for site in sites)
    specs = [
        (ATOMIC, 'clone_metadata'), (ATOMIC, 'build.CausalProxy.__getattr__'),
        (ATOMIC, 'build.Recorder._atomic'), (ATOMIC, 'build.Recorder._observe'),
        (ATOMIC, 'build.Recorder._typed_finish'), (ATOMIC, 'build.Recorder.wrap_boundary'),
        (BASE_SOURCE, 'strict_json'), (BASE_SOURCE, 'digest_value'), (BASE_SOURCE, 'digest_value.visit'),
        (BASE_SOURCE, 'Recorder.start'), (WORKER, 'exercise'), (WORKER, 'main'),
    ]
    anchors, nodes = [], {}
    for path, symbol in specs:
        assert len(indices[path][symbol]) == 1
        node = indices[path][symbol][0]
        nodes[(path, symbol)] = node
        anchors.append(dict(path=path, sha256=sources[path], symbol=symbol, line=node.lineno,
                            end_line=node.end_lineno, AST_sha256=hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()))
    clone = nodes[(ATOMIC, 'clone_metadata')]
    clone_generators = [n for n in ast.walk(clone) if isinstance(n, ast.GeneratorExp)]
    assert len(clone_generators) == 4
    atomic = nodes[(ATOMIC, 'build.Recorder._atomic')]
    expressions = {ast.unparse(n) for n in ast.walk(atomic)}
    assert {'error = ex', 'raise error', 'value = operation(draft)', 'writes = tuple(draft.events._writes)', 'return value'} <= expressions
    observe = nodes[(ATOMIC, 'build.Recorder._observe')]
    assert any(isinstance(n, ast.ExceptHandler) and ast.unparse(n.type) == 'BaseException' for n in ast.walk(observe))
    visit = nodes[(BASE_SOURCE, 'digest_value.visit')]
    assert any(isinstance(n, ast.Compare) and ast.unparse(n) == "depth <= lim['depth']" for n in ast.walk(visit))
    start = nodes[(BASE_SOURCE, 'Recorder.start')]
    assert any(isinstance(n, ast.Call) and ast.unparse(n) == 'self.frames.append(frame)' for n in ast.walk(start))
    prior = json.loads(data[I124])
    f, s = prior['global_F_upper'], prior['global_S_upper']
    assert (f, s, f+s, 1+f+s) == (52018, 1759, 53777, 53778)
    candidate = json.loads(data[CONTRACT])['product_numeric_candidates']
    return dict(commit=BASE, input_pin_count=len(checks), input_blob_checks=checks, projections=projections,
                source_file_count=len(sources), source_pins=sources, source_file_summaries=summaries,
                syntax_counts={kind:sum(row['kind']==kind for row in rows) for kind in CENSUS_KINDS},
                syntax_site_vector_sha256=digest(rows), source_anchors=anchors,
                clone_generator_expression_sites=[dict(line=n.lineno, column=n.col_offset, end_line=n.end_lineno,
                                                      AST_sha256=hashlib.sha256(ast.dump(n, include_attributes=False).encode()).hexdigest()) for n in clone_generators],
                source_semantics=dict(atomic_error_reraise_and_return_IO_locals_identified=True,
                                      observe_catch_not_complete_collection_proof=True,
                                      data_depth_guard_not_whole_call_stack_bound=True,
                                      metadata_frames_list_not_VM_frame_inventory=True,
                                      syntax_does_not_determine_heap_materialization=True),
                inherited_count_reference=dict(F_upper=f, S_upper=s, clone_batches_upper=f+s,
                                               generations_including_initial_upper=1+f+s,
                                               batch_counts_not_frame_size_or_live_frame_count=True),
                candidate_metadata_frames_limit=candidate['frames'], candidate_serialized_depth_limit=candidate['depth'],
                no_target_modules_executed=True, no_frame_introspection_compilation_or_allocation_sampling=True)

def main():
    o, r, seal = rd(OUT), rd(REVIEW), rd(P + 'D5-I147-integrity.json')
    c, s, plan = rd(CONTRACT), rd(SCOPE), rd(PLAN)
    task, owner = plan['tasks'][7], c['heap']['owner_budgets'][4]
    assert o['base_commit'] == r['base_commit'] == seal['base_commit'] == BASE
    assert o['date'] == r['date'] == seal['date'] == '2026-11-13'
    subprocess.check_call(['git', 'merge-base', '--is-ancestor', BASE, 'HEAD'], cwd=ROOT)
    prior = rd(P + 'D5-I146-integrity.json')
    preserved = {**prior['preserved_published208'], **prior['artifacts'], P + 'D5-I146-integrity.json': sha(P + 'D5-I146-integrity.json')}
    assert seal['preserved_published213'] == preserved and len(preserved) == 213
    for pins in [preserved, seal['artifacts'], o['input_pins'], r['input_pins'], rd(P + 'D5-I119-integrity.json')['inherited_inputs477']]:
        for path, h in pins.items():
            assert sha(path) == h, path
    expected = {OUT, REVIEW, P + 'D5-I147-audit.py', P + 'D5-I147-integrity.json', 'docs/design/D5-I147-P04-H05-FRAMES-GENERATORS-TRACEBACKS-HEAP.md'}
    assert set(seal['artifacts']) | {P + 'D5-I147-integrity.json'} == expected and len(seal['artifacts']) == 4
    assert set(git('diff', BASE, '--name-only').splitlines()) | set(git('ls-files', '--others', '--exclude-standard').splitlines()) == expected
    if git('rev-parse', 'HEAD') != BASE:
        assert not git('diff', 'HEAD', '--name-only')
    assert o['source_evidence'] == evidence(o['input_pins']) and len(o['input_pins']) == 155
    source = o['source_evidence']
    assert source['source_file_count'] == 79 and len(source['source_anchors']) == 12 and len(source['projections']) == 12
    assert source['candidate_metadata_frames_limit'] == 4096 and source['candidate_serialized_depth_limit'] == 32
    assert o['package_id'] == task['id'] == 'P04-H05' and OUT == task['planned_output'] and o['schema'] == task['output_schema']
    assert o['plan_binding'] == dict(path=PLAN, sha256=sha(PLAN), package_id='P04-H05', task_record_canonical_sha256=digest(task))
    assert o['candidate_binding'] == dict(path=CONTRACT, sha256=sha(CONTRACT), contract_id=c['contract_id'], subject=c['subject'], source_revision='I122-CANDIDATE-01')
    assert set(task['required_specific_fields']) <= set(o) and len(task['required_specific_fields']) == 9
    assert o['candidate_budget_bytes=134217728'] == o['candidate_budget_bytes'] == owner['candidate_budget_bytes'] == 128*1024**2
    assert o['candidate_owner_record'] == owner and owner['proof_upper_bytes'] is None
    assert o['status'] == 'PREPARED_INSUFFICIENT_DYNAMIC_FRAME_GENERATOR_TRACEBACK_HEAP_H05_E02_OPEN_NOT_ADMITTED'
    assert o['owner_id_metric_and_exact_units'] == dict(owner_id='H05', owner=owner['owner'], metric=owner['metric'], unit='exact_integer_bytes', process='I122 worker dynamic heap activation/support objects; native stack/RSS separate', candidate_budget_bytes=134217728, scope_is_requirement_not_verified_bound=True)
    inventory = o['complete_live_allocation_inventory']
    assert not inventory['complete'] and len(inventory['required_classes']) == 12 and inventory['residual_runtime_native_terms_not_proved_absent']
    assert inventory['kind'] == 'TWELVE_REQUIRED_ACTIVATION_GENERATOR_TRACEBACK_CLASSES_NOT_COMPLETE_HEAP_PROOF'
    for i, row in enumerate(inventory['required_classes'], 1):
        assert row['id'] == 'R%02d'%i and not row['verified'] and row['required_coverage'] and row['runtime_dependency']
        assert all(row[k] is None for k in ['cardinality_upper', 'size_upper_bytes', 'maximum_live_upper_bytes', 'lifetime_derivation'])
    abi = o['source_ABI_allocator_dependencies']
    assert abi['historical_runtime_reference'] == c['runtime'] and not abi['exact_runtime_ABI_or_allocator_correspondence_verified']
    assert all(abi[k] is None for k in ['accepted_target_closure', 'heap_frame_materialization_and_backing_model', 'generator_iterator_native_size_model', 'traceback_exception_allocation_model', 'native_stack_heap_allocator_mapping'])
    deriv = o['cardinality_size_lifetime_derivations']
    assert not deriv['complete'] and deriv['whole_owner_live_upper_bytes'] is None
    assert deriv['inherited_count_reference'] == source['inherited_count_reference']
    assert deriv['metadata_frames_and_serialized_depth_not_VM_frame_bound'] and deriv['batch_retention_not_per_frame_size_or_multiplicity']
    assert deriv['native_stack_RSS_not_relabelled_as_heap'] and deriv['return_except_cleanup_not_immediate_release']
    overlap = o['overlap_alias_original_and_rejected_prefix_treatment']
    assert overlap['inherited_scope'] == s['worker_heap_vs_other_process_scope'] and overlap['source_applicability'] == s['321_root_12_group_applicability']['I124_applicability']
    assert [x['other_owner'] for x in overlap['boundary_requirements']] == ['H01','H02','H03','H04'] + ['H%02d'%i for i in range(6,12)]
    assert all(not x['resolved'] for x in overlap['boundary_requirements']) and not overlap['complete_ownership_alias_lifetime_proof']
    assert overlap['frame_carrier_does_not_pay_for_retained_referents'] and overlap['no_implicit_stack_exclusion_or_double_count']
    dep = o['explicit_assumptions_and_external_dependencies']
    assert not dep['assumptions_verified'] and not dep['P02_exact_runtime_identity_accepted'] and not dep['P03_capacity_service_accepted']
    assert all(dep[k] is None for k in ['complete_activation_native_size_multiplicity_model', 'complete_retained_traceback_generator_lifetime_theorem', 'independent_runtime_memory_review'])
    assert dep['inherited_P01_preconditions'] == s['321_root_12_group_applicability']['original_source_route_preconditions']
    assert dep['no_new_hooks_instrumentation_recursion_limit_or_source_changes']
    assert deriv['no_one_call_or_definition_or_comprehension_one_heap_frame_assumed']
    assert dep['negative_dossier_does_not_bypass_P01_P02'] and dep['other_owner_or_capacity_not_substitute_for_H05_demand'] and dep['later_resource_closure_not_started']
    assert o['verified_upper_bytes_and_derivation'] == dict(verified_upper_bytes=None, complete_derivation=None, evidence_pins={}, verified=False, unknown_not_zero=True, depth_batch_counts_and_file_sizes_not_heap_upper=True)
    assert o['bound_fit_not_just_partial_payload'] == dict(candidate_budget_bytes=134217728, verified_complete_upper_bytes=None, fit_result='NOT_EVALUABLE_NO_COMPLETE_H05_BOUND', fits=None, slack_bytes=None, overbudget_proved=False, actual_unboundedness_proved=False, partial_payload_not_accepted=True)
    assert [x['field'] for x in o['field_assessment']] == task['required_specific_fields']
    for row in o['field_assessment']:
        result = 'DOCUMENTARY_DEFINITION_ONLY' if row['field'] in ['owner_id_metric_and_exact_units','candidate_budget_bytes=134217728'] else 'INSUFFICIENT_FOR_ACCEPTANCE'
        assert row['result'] == result and not row['resource_obligation_closed'] and row['basis']
    assert o['acceptance'] == dict(rule=task['acceptance'], rejection_rule=task['rejection'], preparation_complete=True, accepted_as_complete_H05_proof=False, H05_verified=False, E02_closed=False, resource_obligations_closed=0, no_reserve_transfer=True)
    for d, path in zip(o['dependencies'], [SCOPE,RUNTIME], strict=True):
        assert d['path'] == path and d['sha256'] == sha(path) and not d['accepted_for_resource_closure']
    assert [x['id'] for x in o['dependencies']] == task['depends_on'] == ['P01','P02']
    provenance = o['producer_and_review_provenance']
    assert provenance['producer_identity'] == 'Codex assistant preparing I147 in this chat' and provenance['planned_author_role'] == task['responsible_role'] and provenance['planned_review_role'] == task['review_role']
    assert provenance['independent_reviewer_identity'] is None and not provenance['independent_acceptance'] and not provenance['runtime_custodian_authority_claimed']
    assert not rd(RUNTIME)['acceptance']['accepted_as_runtime_identity'] and not rd(PLATFORM)['acceptance']['accepted_as_platform_evidence']
    assert o['reserve_accounting'] == c['reserve_accounting'] and o['non_execution_and_zero_transfer_policy'] == s['non_execution_and_zero_transfer_policy']
    criteria = rd(P+'D5-I131-E01-E05-review.json')['obligations'][1]['criteria']
    assert o['E02_criterion_disposition'] == [dict(id=x['id'], inherited_result=x['result'], I147_result=x['result'], closed=False) for x in criteria]
    assert r['output'] == dict(path=OUT, sha256=sha(OUT), schema=o['schema'], evidence_kind=o['evidence_kind'], produced=True) and r['input_pins'][OUT] == sha(OUT)
    assert all(r['preparation_checks'].values()) and r['status'] == 'P04_H05_PREPARATION_COMPLETE_NO_COMPLETE_BOUND_NO_ADMISSION'
    assert r['counts'] == dict(required_fields=9, documentary_definition_fields=2, insufficient_fields=7, required_allocation_classes=12, unknown_inventory_values=48, owner_boundaries=10, source_files=79, source_anchors=12, evidence_projections=12, input_pins=155, other_unproduced_packages=12)
    assert r['independent_review'] == dict(accepted=False, reviewer_identity=None, no_independent_review_fabricated=True)
    assert not o['external_material_scope']['external_contacts_made'] and not o['external_material_scope']['global_absence_claimed'] and not o['external_material_scope']['runtime_or_platform_sampled']
    assert len(r['package_progress']) == 20
    for progress, t in zip(r['package_progress'],plan['tasks'],strict=True):
        exists = t['id'] in ['P01','P02','P03','P04-H01','P04-H02','P04-H03','P04-H04','P04-H05']
        assert (ROOT/t['planned_output']).exists() == exists and progress['output_created'] == exists and progress['package_id'] == t['id'] and progress['path'] == t['planned_output'] and progress['sha256'] == (sha(t['planned_output']) if exists else None)
    for d in [o['decision'],r['decision']]:
        true_keys = {'candidate_plan_prior_packages_and_source_bytes_preserved','numeric_candidates_unchanged','P0_D1_D4_I1_I20_A52_unchanged','global_gaps_and_real_obligations_pending','I86_I89_I92_not_resumed'}
        assert d['certificate_unchanged'] == rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')['status'] == 'IMPLEMENTED_NOT_ADMITTED' and d['IR03'] == 'NOT_READY' and d['resource_obligations_closed'] == 0
        for key in true_keys:
            assert d[key] is True
        for key,value in d.items():
            if key not in true_keys | {'certificate_unchanged','IR03','resource_obligations_closed'}:
                assert value is False,key
    assert o['E06'] == r['E06'] == dict(status='SEPARATE_PENDING_NOT_RUN',components_executed=0,execution_authorized=False)
    for path in [P+'D5-JOINT-capture-authorization.json',P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:
        assert not (ROOT/path).exists()
    assert set(r['work_unit']['rollback_files']) == expected and r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command'] == 'python3 docs/validation/D5-I147-audit.py' and r['work_unit']['expected_result'] == 'PASS_STATIC_SOURCE_ONLY' and r['work_unit']['diff_budget_note']
    assert seal['source_only'] and not seal['proposal_enabled'] and r['git_publication']['commit_and_push_all_requested']
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I147',package='P04-H05',preparation_complete=True,accepted_as_complete_H05_proof=False,candidate_budget_bytes=134217728,insufficient_fields=7,source_files=79,prior_published_files_preserved=213,new_files=5,product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__ == '__main__':
    main()
