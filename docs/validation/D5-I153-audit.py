#!/usr/bin/env python3
"""I153: documentary JSON/Git/AST checks only; never import or run a target."""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'f2290da117ed838ffc7944dce3cff47222f9b4eb'
OUT = P + 'D5-PFC126-03-E02-H08.json'
REVIEW = P + 'D5-I153-P04-H08-preparation-review.json'
SEAL = P + 'D5-I153-integrity.json'
AUDIT = P + 'D5-I153-audit.py'
DESIGN = 'docs/design/D5-I153-P04-H08-INPUT-READER-PHASE-HEAP.md'
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
H07 = P + 'D5-PFC126-03-E02-H07.json'
BINDING = P + 'D5-I122-binding-review.json'
WORKER = 'testing/prospective_capture_joint_i122/worker.py'
PROJECTIONS = [
    (CONTRACT, '/heap/owner_budgets/7'),
    (P + 'D5-I125-complete-heap-review.json', '/required_terms/7'),
    (BINDING, '/read_schedule'), (BINDING, '/future_metadata_width_sizes'),
    (P + 'D5-I123-transient-resource-envelope.json', '/physical_file_reads'),
    (P + 'D5-I124-resource-admission-review.json', '/physical_file_read_plan_unchanged'),
    (RUNTIME, '/acceptance'), (PLATFORM, '/acceptance'),
    (P + 'D5-I152-P04-H07-documentary-review.json', '/acceptance'),
    (H07, '/overlap_alias_original_and_rejected_prefix_treatment'),
    (SCOPE, '/worker_heap_vs_other_process_scope'), (CONTRACT, '/product_numeric_candidates'),
]
SPECS = [
    (CAPTURE, 'Reader.__init__'), (CAPTURE, 'Reader.directory'),
    (CAPTURE, 'Reader.read'), (CAPTURE, 'Reader.listing'), (CAPTURE, 'Reader.finish'),
    (JOINT, 'PhaseBytes.__init__'), (JOINT, 'PhaseBytes.read'), (JOINT, 'PhaseBytes.listing'),
    (JOINT, 'InputPlan.__init__'), (JOINT, 'InputPlan.before'),
    (JOINT, 'InputPlan.after'), (JOINT, 'InputPlan.finish'),
    (JOINT, 'MemberReader.__init__'), (JOINT, 'MemberReader.read'),
    (JOINT, 'canonical_metadata'), (JOINT, 'require_admission'),
    (ATOMIC, 'build.Bindings.check'), (ATOMIC, 'build.Bindings.prepare'),
    (WORKER, 'targets'), (WORKER, 'main'),
]
CENSUS = ['Call','List','Tuple','Dict','Set','ListComp','SetComp',
          'DictComp','GeneratorExp','ExceptHandler']
# Source order only: counter/phase/publication relations are not heap bounds.
ORDERS = [
    (CAPTURE, 'Reader.read', 'require(st.st_size <=', 'h = os.open('),
    (CAPTURE, 'Reader.read', 'self.total +=', 'require(self.total <='),
    (CAPTURE, 'Reader.read', 'b = os.read(h, min(left, 65536))', 'chunks.append(b)'),
    (CAPTURE, 'Reader.read', 'self.files[name] = value', "return b''.join(chunks)"),
    (CAPTURE, 'Reader.listing', 'names = tuple(sorted(os.listdir(fd)))', 'require(len(names)'),
    (JOINT, 'InputPlan.after', 'bodies[name] = self.reader.read(name)', 'self.view = PhaseBytes('),
    (JOINT, 'InputPlan.before', 'value = self.reader.read(name)', 'bodies[name] = value'),
    (JOINT, 'InputPlan.finish', 'self.reader.finish()', "self.phase = 'FINISHED'"),
]
FACTS = [
    (CAPTURE, 'Reader.read', "return b''.join(chunks)"),
    (CAPTURE, 'Reader.read', 'os.read(h, min(left, 65536))'),
    (CAPTURE, 'Reader.read', 'os.read(h, 1)'),
    (CAPTURE, 'Reader.finish', 'tuple(self.files)'),
    (CAPTURE, 'Reader.finish', 'tuple(self.dirs)'),
    (CAPTURE, 'Reader.listing', 'tuple(sorted(os.listdir(fd)))'),
    (JOINT, 'PhaseBytes.__init__', 'self.bodies = dict(bodies)'),
    (JOINT, 'PhaseBytes.read', 'return self.bodies[name]'),
    (JOINT, 'InputPlan.after', 'self.view = PhaseBytes(self.reader, bodies)'),
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
                    generations_including_initial_upper=1+f+s, not_reader_operation_or_live_body_counts=True),
                candidate_numeric_limits=json.loads(blobs[CONTRACT])['product_numeric_candidates'],
                no_target_import_execution_compilation_introspection_or_sampling=True)


def fixed_read_graph_reference():
    binding = rd(BINDING)
    schedule = binding['read_schedule']
    known, future = binding['known_union_bytes'], binding['future_metadata_bytes_upper']
    assert (binding['known_files'],known,future)==(490,87104500,57277)
    assert sum(binding['future_metadata_width_sizes'].values())==future
    assert (binding['capture_inputs_with_future_components'],binding['union_with_authority'])==(493,494)
    read_upper = 3*(known+future)+4852460
    assert schedule['formula']=='3*(U_known+F_future4)+4852460'
    assert read_upper==schedule['worker_file_read_upper']==266337791
    assert schedule['launcher_file_read_upper']==3*(known+future)==261485331
    assert schedule['worker_file_read_limit']==268435456
    assert schedule['worker_file_read_margin']==268435456-read_upper==2097665
    owner = rd(CONTRACT)['heap']['owner_budgets'][7]
    payload = 2*read_upper
    assert payload==owner['known_partial_upper']==532675582
    assert owner['known_partial_unit']=='raw_input_byte_payload' and not owner['known_partial_is_complete_term']
    return dict(binding_review=dict(path=BINDING,sha256=sha(BINDING)),known_files=490,
        historical_known_union_bytes=known,future_four_metadata_bytes_upper=future,
        future_widths=binding['future_metadata_width_sizes'],capture_inputs_count=493,union_with_authority_count=494,
        formula=schedule['formula'],additional_fresh_check_read_bytes=4852460,
        worker_read_bytes_upper=read_upper,launcher_read_bytes_upper=schedule['launcher_file_read_upper'],
        worker_input_read_limit_bytes=268435456,physical_read_margin_bytes=2097665,
        successful_fixed_graph_chunk_plus_join_payload_upper_bytes=payload,
        candidate_owner_budget_bytes=536870912,
        arithmetic_budget_minus_payload_bytes=536870912-payload,
        arithmetic_distance_is_not_verified_heap_slack=True,
        complete_owner_upper_bytes=None,complete_owner_fits=None,
        successful_fixed_graph_not_all_rejected_prefixes_or_live_heap=True,
        future_input_or_protocol_change_requires_new_final_bytes_U_and_pin_review=True,
        I153_artifacts_added_to_capture_inputs=False,
        future_four_files_created=False,known_union_not_recomputed_as_current_repo_union=True)


def main():
    o,r,seal = rd(OUT),rd(REVIEW),rd(SEAL)
    c,scope,plan = rd(CONTRACT),rd(SCOPE),rd(PLAN)
    task = next(t for t in plan['tasks'] if t['id']=='P04-H08')
    owner = c['heap']['owner_budgets'][7]
    prior = rd(P+'D5-I152-integrity.json')
    preserved = {**prior['preserved_published238'],**prior['artifacts'],
                 P+'D5-I152-integrity.json':sha(P+'D5-I152-integrity.json')}
    expected = {OUT,REVIEW,AUDIT,SEAL,DESIGN}
    assert len(preserved)==243 and seal['preserved_published243']==preserved
    assert set(seal['artifacts'])|{SEAL}==expected
    for pins in [preserved,seal['artifacts'],o['input_pins'],r['input_pins'],
                 rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for path,h in pins.items():
            assert sha(path)==h,path
    assert set(git('diff',BASE,'--name-only').splitlines())|set(
        git('ls-files','--others','--exclude-standard').splitlines())==expected
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('diff','HEAD','--name-only')
    assert o['base_commit']==r['base_commit']==seal['base_commit']==BASE
    assert o['date']==r['date']==seal['date']=='2026-11-13'
    assert o['package_id']==task['id']=='P04-H08' and OUT==task['planned_output']
    assert o['schema']==task['output_schema'] and r['schema']=='d5.i153-p04-h08-preparation-review.v1'
    assert seal['schema']=='d5.i153-integrity.v1'
    assert o['status']=='PREPARED_INSUFFICIENT_INPUT_READER_PHASE_HEAP_H08_E02_OPEN_NOT_ADMITTED'
    assert r['status']=='P04_H08_PREPARATION_COMPLETE_NO_COMPLETE_BOUND_NO_ADMISSION'
    assert o['plan_binding']==dict(path=PLAN,sha256=sha(PLAN),package_id=task['id'],task_record_canonical_sha256=digest(task))
    assert o['candidate_binding']==dict(path=CONTRACT,sha256=sha(CONTRACT),contract_id=c['contract_id'],subject=c['subject'],source_revision='I122-CANDIDATE-01')
    assert len(task['required_specific_fields'])==9 and set(task['required_specific_fields'])<=set(o)
    assert o['candidate_owner_record']==owner and owner['id']=='H08' and owner['proof_upper_bytes'] is None
    assert o['candidate_budget_bytes']==o['candidate_budget_bytes=536870912']==owner['candidate_budget_bytes']==512*1024**2
    identity = o['owner_id_metric_and_exact_units']
    assert identity['owner_id']=='H08' and identity['owner']==owner['owner']
    assert identity['metric']==owner['metric']=='peak_requested_live_heap'
    assert identity['unit']=='exact_integer_bytes' and identity['candidate_budget_bytes']==536870912
    assert identity['scope_is_requirement_not_verified_bound']
    assert o['source_evidence']==evidence(o['input_pins'])
    assert o['fixed_read_graph_and_partial_payload_reference']==fixed_read_graph_reference()
    e = o['source_evidence']
    assert (e['input_pin_count'],e['source_file_count'],len(e['projections']),len(e['source_anchors']))==(180,79,12,20)
    assert len(e['lexical_order_witnesses'])==8 and len(e['allocation_expression_witnesses'])==9
    abi = o['source_ABI_allocator_dependencies']
    assert abi['historical_runtime_reference']==c['runtime'] and not abi['exact_runtime_ABI_or_allocator_correspondence_verified']
    assert all(abi[k] is None for k in ['accepted_target_closure','bytes_list_dict_tuple_growth_and_header_model',
        'directory_path_stat_hash_native_allocation_model','phase_map_sharing_and_retained_body_lifetime_model',
        'requested_live_overlap_and_allocator_mapping'])
    inventory = o['complete_live_allocation_inventory']
    assert not inventory['complete'] and len(inventory['required_classes'])==12
    assert inventory['residual_runtime_native_terms_not_proved_absent']
    for i,row in enumerate(inventory['required_classes'],1):
        assert row['id']=='R%02d'%i and row['required_coverage'] and row['runtime_dependency'] and not row['verified']
        assert all(row[k] is None for k in ['cardinality_upper','size_upper_bytes','maximum_live_upper_bytes','lifetime_derivation'])
    d = o['cardinality_size_lifetime_derivations']
    assert not d['complete'] and d['whole_owner_live_upper_bytes'] is None
    assert d['inherited_count_reference']==e['inherited_count_reference']
    assert all(d[k] for k in ['payload_not_complete_owner_heap','directory_listing_pre_guard_allocation_requires_prefix_proof',
        'phase_shallow_copy_not_fresh_read_or_deep_immutability_proof',
        'old_new_phase_views_and_error_retention_need_overlap_proof',
        'input_reader_not_member_reader_or_parent_heap_equated','future_input_rebind_not_applied'])
    overlap = o['overlap_alias_original_and_rejected_prefix_treatment']
    assert overlap['inherited_scope']==scope['worker_heap_vs_other_process_scope']
    assert overlap['source_applicability']==scope['321_root_12_group_applicability']['I124_applicability']
    assert [x['other_owner'] for x in overlap['boundary_requirements']]==['H%02d'%i for i in range(1,12) if i!=8]
    assert all(not x['resolved'] for x in overlap['boundary_requirements']) and not overlap['complete_ownership_alias_lifetime_proof']
    dep = o['explicit_assumptions_and_external_dependencies']
    assert not dep['assumptions_verified'] and not dep['P02_exact_runtime_identity_accepted'] and not dep['P03_capacity_service_accepted']
    assert dep['inherited_P01_preconditions']==scope['321_root_12_group_applicability']['original_source_route_preconditions']
    assert all(dep[k] is None for k in ['complete_reader_listing_phase_allocation_inventory',
        'complete_requested_allocation_and_lifetime_theorem','independent_runtime_memory_review'])
    b = o['verified_upper_bytes_and_derivation']
    assert b['verified_upper_bytes'] is None and b['complete_derivation'] is None and not b['verified'] and b['unknown_not_zero']
    assert o['bound_fit_not_just_partial_payload']==dict(candidate_budget_bytes=536870912,
        verified_complete_upper_bytes=None,fit_result='NOT_EVALUABLE_NO_COMPLETE_H08_BOUND',fits=None,
        slack_bytes=None,overbudget_proved=False,actual_unboundedness_proved=False,partial_payload_not_accepted=True)
    assert [x['field'] for x in o['field_assessment']]==task['required_specific_fields']
    for row in o['field_assessment']:
        definition = row['field'] in ['owner_id_metric_and_exact_units','candidate_budget_bytes=536870912']
        assert row['result']==('DOCUMENTARY_DEFINITION_ONLY' if definition else 'INSUFFICIENT_FOR_ACCEPTANCE')
        assert row['basis'] and not row['resource_obligation_closed']
    assert o['acceptance']==dict(rule=task['acceptance'],rejection_rule=task['rejection'],preparation_complete=True,
        accepted_as_complete_H08_proof=False,H08_verified=False,E02_closed=False,resource_obligations_closed=0,no_reserve_transfer=True)
    assert o['dependencies']==rd(H07)['dependencies']
    assert [x['id'] for x in o['dependencies']]==task['depends_on']==['P01','P02']
    provenance = o['producer_and_review_provenance']
    assert provenance['producer_identity']=='Codex assistant preparing I153 in this chat'
    assert provenance['planned_author_role']==task['responsible_role'] and provenance['planned_review_role']==task['review_role']
    assert provenance['independent_reviewer_identity'] is None and not provenance['independent_acceptance'] and not provenance['runtime_custodian_authority_claimed']
    assert not rd(RUNTIME)['acceptance']['accepted_as_runtime_identity'] and not rd(PLATFORM)['acceptance']['accepted_as_platform_evidence']
    assert o['reserve_accounting']==c['reserve_accounting'] and o['non_execution_and_zero_transfer_policy']==scope['non_execution_and_zero_transfer_policy']
    for row,old in zip(o['E02_criterion_disposition'],rd(H07)['E02_criterion_disposition'],strict=True):
        assert row==dict(id=old['id'],inherited_result=old['I151_result'],I153_result=old['I151_result'],closed=False)
    assert r['E02_criterion_disposition']==o['E02_criterion_disposition']
    assert r['input_pins']=={**o['input_pins'],OUT:sha(OUT)}
    assert r['output']==dict(path=OUT,sha256=sha(OUT),schema=o['schema'],evidence_kind=o['evidence_kind'],produced=True)
    assert all(r['preparation_checks'].values())
    assert r['counts']==dict(required_fields=9,documentary_definition_fields=2,insufficient_fields=7,
        required_allocation_classes=12,unknown_inventory_values=48,owner_boundaries=10,source_files=79,
        source_anchors=20,evidence_projections=12,input_pins=180,lexical_order_witnesses=8,
        allocation_expression_witnesses=9,other_unproduced_packages=9)
    for progress,t in zip(r['package_progress'],plan['tasks'],strict=True):
        exists = t['id'] in ['P01','P02','P03']+['P04-H%02d'%i for i in range(1,9)]
        assert (ROOT/t['planned_output']).exists()==progress['output_created']==exists
        assert progress['package_id']==t['id'] and progress['path']==t['planned_output']
        assert progress['sha256']==(sha(t['planned_output']) if exists else None)
    assert r['independent_review']==dict(accepted=False,reviewer_identity=None,no_independent_review_fabricated=True)
    assert not any(o['external_material_scope'][k] for k in ['global_absence_claimed','external_contacts_made','runtime_or_platform_sampled'])
    negative = {('complete_H08_bound_verified' if k=='complete_H07_bound_verified' else k):v for k,v in rd(H07)['decision'].items()}
    assert o['decision']==r['decision']==negative and o['E06']==r['E06']==rd(H07)['E06']
    assert seal['source_only'] and not any(seal[k] for k in ['H08_verified','independent_acceptance',
        'proposal_enabled','product_or_components_executed','quotas_changed','D5_closed'])
    assert seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    assert r['git_publication']['commit_and_push_all_requested']
    assert set(r['work_unit']['rollback_files'])==expected and r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command']=='python3 docs/validation/D5-I153-audit.py'
    assert r['work_unit']['expected_result']=='PASS_STATIC_SOURCE_ONLY' and r['work_unit']['diff_budget_note']
    for path in rd(BINDING)['future_metadata_width_sizes']:
        assert not (ROOT/path).exists()
    assert not (ROOT/(P+'D5-JOINT-P01')).exists() and not (ROOT/(P+'D5-JOINT-P01-launch.json')).exists()
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I153',package='P04-H08',
        preparation_complete=True,accepted_as_complete_H08_proof=False,candidate_budget_bytes=536870912,
        successful_fixed_graph_payload_subbound_bytes=532675582,insufficient_fields=7,source_files=79,
        source_anchors=20,prior_published_files_preserved=243,new_files=5,product_or_components_executed=0,
        quotas_changed=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,
        IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
