#!/usr/bin/env python3
"""I148 H05 review: documentary consistency and fresh Git/AST reconstruction.
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

def validate_preparation():
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

REVIEW_BASE = 'f8003d33dd0786f0f2deb9aa1b998beebf57d193'
NEW_REVIEW = P + 'D5-I148-P04-H05-documentary-review.json'
RECON = P + 'D5-I148-P04-H05-source-reconstruction.json'

def blobs(commit, paths):
    paths = list(paths)
    request = ''.join(commit+':'+path+'\n' for path in paths).encode()
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=request))
    result = {}
    for path in paths:
        header = stream.readline().decode().split()
        assert len(header)==3 and header[1]=='blob',path
        size = int(header[2])
        body = stream.read(size)
        assert len(body)==size and stream.read(1)==b'\n'
        result[path]=(header[0],body)
    assert not stream.read()
    return result

def reconstruct():
    published = blobs(REVIEW_BASE,[OUT])[OUT]
    o = json.loads(published[1])
    assert hashlib.sha256(published[1]).hexdigest()==sha(OUT)
    data = blobs(o['base_commit'],sorted(o['input_pins']))
    checks = []
    for path,h in sorted(o['input_pins'].items()):
        oid,body = data[path]
        assert hashlib.sha256(body).hexdigest()==h==sha(path)
        checks.append(dict(path=path,preparation_git_blob_oid=oid,sha256=h,bytes=len(body)))
    evidence = o['source_evidence']
    projections = []
    assert [(x['path'],x['json_pointer']) for x in evidence['projections']]==PROJECTIONS
    for row in evidence['projections']:
        value = pointer(json.loads(data[row['path']][1]),row['json_pointer'])
        assert value==row['observed_value'] and digest(value)==row['canonical_sha256']
        assert o['input_pins'][row['path']]==row['sha256']
        projections.append(dict(path=row['path'],sha256=row['sha256'],json_pointer=row['json_pointer'],recomputed_value_sha256=digest(value),matches_published_projection=True))
    scope = json.loads(data[SCOPE][1])
    source_sets = scope['I122_and_original_source_pin_set']
    sources = {**source_sets['runner_registered_input_pins'],**source_sets['observer_static_repo_import_superset']['file_pins']}
    sources = {path:h for path,h in sources.items() if path.endswith('.py')}
    assert sources==evidence['source_pins']==json.loads(data[RUNTIME][1])['source_import_surface']['source_pins']
    trees,indices,summaries,all_sites = {},{ },[],[]
    for path,h in sorted(sources.items()):
        assert hashlib.sha256(data[path][1]).hexdigest()==h
        tree = ast.parse(data[path][1].decode())
        trees[path]=tree
        index = {}
        class Lexical(ast.NodeVisitor):
            def __init__(self):
                self.parts=[]
            def record(self,node):
                self.parts.append(node.name)
                index.setdefault('.'.join(self.parts),[]).append(node)
                self.generic_visit(node)
                self.parts.pop()
            visit_ClassDef=record
            visit_FunctionDef=record
            visit_AsyncFunctionDef=record
        Lexical().visit(tree)
        indices[path]=index
        sites=[]
        for node in ast.walk(tree):
            kind=type(node).__name__
            if kind in CENSUS_KINDS:
                sites.append(dict(kind=kind,line=node.lineno,column=node.col_offset,end_line=node.end_lineno,AST_sha256=hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()))
        sites.sort(key=lambda x:(x['line'],x['column'],x['kind']))
        summaries.append(dict(path=path,sha256=h,syntax_counts={kind:sum(x['kind']==kind for x in sites) for kind in CENSUS_KINDS},syntax_site_vector_sha256=digest(sites)))
        all_sites.extend(dict(path=path,**row) for row in sites)
    totals={kind:sum(row['kind']==kind for row in all_sites) for kind in CENSUS_KINDS}
    assert summaries==evidence['source_file_summaries'] and totals==evidence['syntax_counts']
    assert digest(all_sites)==evidence['syntax_site_vector_sha256']
    nodes,anchors = {},[]
    for row in evidence['source_anchors']:
        assert len(indices[row['path']][row['symbol']])==1
        node=indices[row['path']][row['symbol']][0]
        assert (node.lineno,node.end_lineno)==(row['line'],row['end_line'])
        assert hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()==row['AST_sha256']
        assert sources[row['path']]==row['sha256']
        nodes[(row['path'],row['symbol'])]=node
        anchors.append(dict(**row,lexical_binding_verified=True))
    clone = nodes[(ATOMIC,'clone_metadata')]
    generators=[n for n in ast.walk(clone) if isinstance(n,ast.GeneratorExp)]
    sites=[dict(line=n.lineno,column=n.col_offset,end_line=n.end_lineno,AST_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()) for n in generators]
    assert sites==evidence['clone_generator_expression_sites'] and len(sites)==4
    branches=[]
    for node in ast.walk(clone):
        if not isinstance(node,ast.If) or ast.unparse(node.test) not in ['kind is list','kind is tuple','kind is set','kind is frozenset']:
            continue
        owned=[x for statement in node.body for x in ast.walk(statement) if isinstance(x,ast.GeneratorExp)]
        assert len(owned)==1
        branches.append(dict(branch_test=ast.unparse(node.test),generator_line=owned[0].lineno,generator_AST_sha256=hashlib.sha256(ast.dump(owned[0],include_attributes=False).encode()).hexdigest(),syntax_not_live_allocation=True))
    assert len(branches)==4
    atomic=nodes[(ATOMIC,'build.Recorder._atomic')]
    handlers=[n for n in ast.walk(atomic) if isinstance(n,ast.ExceptHandler) and n.name=='ex' and ast.unparse(n.type)=='BaseException']
    assert len(handlers)==1
    assert any(isinstance(n,ast.Assign) and ast.unparse(n)=='error = ex' for n in handlers[0].body)
    assert any(isinstance(n,ast.Raise) and isinstance(n.exc,ast.Name) and n.exc.id=='error' for n in ast.walk(atomic))
    observe=nodes[(ATOMIC,'build.Recorder._observe')]
    assert any(isinstance(n,ast.ExceptHandler) and ast.unparse(n.type)=='BaseException' and any(isinstance(x,ast.Return) and isinstance(x.value,ast.Constant) and x.value.value is None for x in n.body) for n in ast.walk(observe))
    visit=nodes[(BASE_SOURCE,'digest_value.visit')]
    assert any(isinstance(n,ast.Compare) and ast.unparse(n)=="depth <= lim['depth']" for n in ast.walk(visit))
    start=nodes[(BASE_SOURCE,'Recorder.start')]
    frame_records=[n for n in ast.walk(start) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='frame' for t in n.targets) and isinstance(n.value,ast.Call) and ast.unparse(n.value.func)=='dict']
    assert len(frame_records)==1
    assert any(isinstance(n,ast.Call) and ast.unparse(n)=='self.frames.append(frame)' for n in ast.walk(start))
    exercise=nodes[(WORKER,'exercise')]
    assert any(isinstance(n,ast.Call) and ast.unparse(n)=='rec.restore()' for n in ast.walk(exercise))
    counts=json.loads(data[I124][1])
    f,s=counts['global_F_upper'],counts['global_S_upper']
    assert (f,s,f+s,1+f+s)==(52018,1759,53777,53778)
    assert evidence['inherited_count_reference']==dict(F_upper=f,S_upper=s,clone_batches_upper=f+s,generations_including_initial_upper=1+f+s,batch_counts_not_frame_size_or_live_frame_count=True)
    assert evidence['candidate_metadata_frames_limit']==4096 and evidence['candidate_serialized_depth_limit']==32
    inventory,unknowns=[],[]
    for i,row in enumerate(o['complete_live_allocation_inventory']['required_classes']):
        for key in ['cardinality_upper','size_upper_bytes','maximum_live_upper_bytes','lifetime_derivation']:
            assert row[key] is None
            unknowns.append('/complete_live_allocation_inventory/required_classes/'+str(i)+'/'+key)
        assert not row['verified']
        inventory.append(dict(id=row['id'],record_canonical_sha256=digest(row),unproved_complete_count_size_peak_and_lifetime=True))
    boundaries=o['overlap_alias_original_and_rejected_prefix_treatment']['boundary_requirements']
    assert all(not x['resolved'] for x in boundaries)
    return dict(preparation_commit=o['base_commit'],published_commit=REVIEW_BASE,H05_published_blob_oid=published[0],H05_sha256=sha(OUT),input_pin_count=len(checks),input_pin_checks=checks,
                projection_checks=projections,source_file_count=len(sources),source_pin_vector_sha256=digest(sources),file_summary_vector_sha256=digest(summaries),syntax_counts=totals,syntax_site_vector_sha256=digest(all_sites),
                source_anchor_checks=anchors,clone_generator_branch_checks=branches,
                source_semantics=dict(error_assignment_and_reraise_checked=True,observe_catch_None_checked=True,worker_restore_call_checked=True,data_depth_guard_checked=True,metadata_dict_frame_and_append_checked=True,
                                      metadata_frames4096_depth32_and_batch_counts_not_VM_frame_bound=True,source_not_actual_frame_materialization_or_release_proof=True),
                inherited_count_reference=evidence['inherited_count_reference'],inventory_checks=inventory,unknown_inventory_pointers=unknowns,unknown_inventory_values=len(unknowns),
                boundary_record_sha256={x['other_owner']:digest(x) for x in boundaries},field_record_sha256={x['field']:digest(o[x['field']]) for x in o['field_assessment']},
                no_target_frame_generator_execution_introspection_or_native_allocation_proof=True)

def main():
    validate_preparation()
    o,z,r=rd(OUT),rd(RECON),rd(NEW_REVIEW)
    seal=rd(P+'D5-I148-integrity.json')
    assert z['base_commit']==r['base_commit']==seal['base_commit']==REVIEW_BASE
    assert z['date']==r['date']==seal['date']=='2026-11-13'
    subprocess.check_call(['git','merge-base','--is-ancestor',REVIEW_BASE,'HEAD'],cwd=ROOT)
    prior=rd(P+'D5-I147-integrity.json')
    preserved={**prior['preserved_published213'],**prior['artifacts'],P+'D5-I147-integrity.json':sha(P+'D5-I147-integrity.json')}
    assert seal['preserved_published218']==preserved and len(preserved)==218
    for pins in [preserved,seal['artifacts'],z['input_pins'],r['input_pins']]:
        for path,h in pins.items():
            assert sha(path)==h,path
    expected={NEW_REVIEW,RECON,P+'D5-I148-audit.py',P+'D5-I148-integrity.json','docs/design/D5-I148-P04-H05-FRAMES-GENERATORS-TRACEBACKS-HEAP-REVIEW.md'}
    assert set(seal['artifacts'])|{P+'D5-I148-integrity.json'}==expected and len(seal['artifacts'])==4
    assert set(git('diff',REVIEW_BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())==expected
    if git('rev-parse','HEAD')!=REVIEW_BASE:
        assert not git('diff','HEAD','--name-only')
    assert z['reconstruction']==reconstruct() and z['reconstruction']['input_pin_count']==155
    assert z['reconstruction']['unknown_inventory_values']==48
    assert r['contract_id']==z['contract_id']==o['candidate_binding']['contract_id']=='PFC126-CANDIDATE-03'
    assert r['H05']==dict(path=OUT,sha256=sha(OUT),bytes_preserved=True) and r['plan_binding']==o['plan_binding']
    assert r['source_reconstruction']==dict(path=RECON,sha256=sha(RECON))
    assert r['status']=='REVIEW_COMPLETE_DOSSIER_CONFORMANT_H05_PROOF_REJECTED_NO_ADMISSION'
    assert r['field_disposition']==[dict(field=x['field'],I147_result=x['result'],I148_result='CONFIRMED_DOCUMENTARY_DEFINITION_ONLY' if x['result']=='DOCUMENTARY_DEFINITION_ONLY' else 'CONFIRMED_INSUFFICIENT_FOR_H05_ACCEPTANCE',record_canonical_sha256=digest(o[x['field']]),closed=False) for x in o['field_assessment']]
    assert len(r['checks'])==14 and [x['id'] for x in r['checks']]==['R%02d'%i for i in range(1,15)]
    for check in r['checks']:
        assert check['result']=='CONFORMANT_DOCUMENTARY_INSUFFICIENCY_JUDGMENT' and not check['resource_obligation_closed']
    assert r['blocking_dossier_defects']==[] and r['documentary_dossier_conformance'] and not r['H05_change_required']
    assert r['reviewer']['same_assistant_as_preparer'] and r['reviewer']['methodologically_separate_reconstruction']
    assert not r['reviewer']['actor_or_organizational_independence_attested'] and not r['reviewer']['runtime_custodian_authority_claimed']
    assert r['acceptance']==dict(review_completed=True,insufficiency_judgment_confirmed=True,accepted_as_complete_H05_proof=False,H05_verified=False,independent_documentary_acceptance=False,independent_reviewer_identity=None,E02_closed=False,E01_E05_closed=False,resource_obligations_closed=0,fit_or_overbudget_proved=False)
    assert r['E02_criterion_disposition']==[dict(id=x['id'],I148_result=x['inherited_result'],closed=False) for x in o['E02_criterion_disposition']]
    assert r['counts']==dict(H05_input_pins_checked=155,evidence_projections_checked=12,source_files_checked=79,symbol_anchors_checked=12,clone_generator_expressions=4,required_fields=9,documentary_definition_fields=2,insufficient_fields=7,required_allocation_classes=12,unknown_inventory_values=48,unresolved_owner_boundaries=10,E02_criteria_preserved=4,checks=14,other_unproduced_packages=12)
    assert r['decision']==o['decision'] and r['E06']==o['E06'] and r['other_packages_started']==0
    assert r['verified_complete_upper_bytes'] is None and r['fits'] is None and r['slack_bytes'] is None
    assert r['pending_independent_acceptance_and_P02_P03_not_bypassed']
    assert set(r['work_unit']['rollback_files'])==expected and r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command']=='python3 docs/validation/D5-I148-audit.py'
    assert r['work_unit']['expected_result']=='PASS_STATIC_SOURCE_ONLY' and r['work_unit']['diff_budget_note']
    assert seal['source_only'] and not seal['proposal_enabled'] and r['git_publication']['commit_and_push_all_requested']
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I148',package='P04-H05',documentary_dossier_conformance=True,accepted_as_complete_H05_proof=False,independent_acceptance=False,Git_input_pins_checked=155,source_files=79,evidence_projections=12,source_anchors=12,insufficient_fields=7,prior_published_files_preserved=218,new_files=5,product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':
    main()
