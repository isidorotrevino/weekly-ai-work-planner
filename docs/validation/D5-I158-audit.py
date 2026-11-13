#!/usr/bin/env python3
"""I158 H10 review: documentary Git/JSON/AST only; no target execution/probes."""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '076794c4fbaf9a42ea6d7b7fbab7b09e551d431e'
OUT = P + 'D5-PFC126-03-E02-H10.json'
REVIEW = P + 'D5-I157-P04-H10-preparation-review.json'
SEAL = P + 'D5-I157-integrity.json'
AUDIT = P + 'D5-I157-audit.py'
DESIGN = 'docs/design/D5-I157-P04-H10-TEE-STRINGIO-RAW-HEAP.md'
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
H09 = P + 'D5-PFC126-03-E02-H09.json'
H07 = P + 'D5-PFC126-03-E02-H07.json'
WORKER = 'testing/prospective_capture_joint_i122/worker.py'
PROJECTIONS = [
    (CONTRACT, '/heap/owner_budgets/9'),
    (P + 'D5-I125-complete-heap-review.json', '/required_terms/9'),
    (CONTRACT, '/product_numeric_candidates'),
    (P + 'D5-I125-complete-heap-review.json', '/scope'),
    (I124, '/lifetime_envelope'), (I124, '/scope'),
    (RUNTIME, '/acceptance'), (PLATFORM, '/acceptance'),
    (P + 'D5-I156-P04-H09-documentary-review.json', '/acceptance'),
    (H09, '/overlap_alias_original_and_rejected_prefix_treatment'),
    (SCOPE, '/worker_heap_vs_other_process_scope'), (H07, '/source_ABI_allocator_dependencies'),
]
SPECS = [
    (WORKER,'Tee.__init__'), (WORKER,'Tee.write'), (WORKER,'Tee.flush'),
    (WORKER,'exercise'), (WORKER,'main'),
    (CAPTURE,'BoundedOutput.__init__'), (CAPTURE,'BoundedOutput.encoding'),
    (CAPTURE,'BoundedOutput.write'), (CAPTURE,'BoundedOutput.flush'),
    (CAPTURE,'strict_json'), (CAPTURE,'strict_json.pairs'), (CAPTURE,'strict_json.check'),
    (CAPTURE,'scenario_metadata'), (CAPTURE,'aggregate_capture'),
    (ATOMIC,'build.Recorder._typed_finish'), (ATOMIC,'build.Recorder.finish'),
    (ATOMIC,'build.Recorder._drain'), (JOINT,'SideWriter.write'),
    (JOINT,'read_sidecar'), (JOINT,'BaseRecorder.finish'), (TYPED,'encode'),
]
CENSUS = ['Call','List','Tuple','Dict','Set','ListComp','SetComp',
          'DictComp','GeneratorExp','ExceptHandler']
# Order witnesses retain preguards/counter/forwarding, without allocation/copy counts.
ORDERS = [
    (CAPTURE,'BoundedOutput.write',"b = value.encode('utf8')",'require(self.count + len(b)'),
    (CAPTURE,'BoundedOutput.write','require(self.count + len(b)','out = self.target.write(value)'),
    (CAPTURE,'BoundedOutput.write','out = self.target.write(value)','self.count += len(b)'),
    (WORKER,'Tee.write','n = self.stream.write(s)','super().write(s)'),
    (WORKER,'exercise','rec.restore()','raw = c.strict_json(stdout.getvalue().encode())'),
    (WORKER,'exercise','raw = c.strict_json(stdout.getvalue().encode())','side = rec.finish(raw)'),
    (WORKER,'exercise','side = rec.finish(raw)','c.aggregate_capture(side, c.scenario_metadata(raw, entry), raw, entry)'),
    (ATOMIC,'build.Recorder._typed_finish','out = dict(',"len(encode(out)) > self.limits['index_sidecar_bytes']"),
]
FACTS = [
    (WORKER,'Tee.__init__','super().__init__()'),
    (WORKER,'Tee.write','self.stream.write(s)'),
    (WORKER,'Tee.write','super().write(s)'),
    (WORKER,'exercise','stdout.getvalue()'),
    (WORKER,'exercise','raw = c.strict_json(stdout.getvalue().encode())'),
    (WORKER,'main','Tee(sys.stdout)'),
    (CAPTURE,'BoundedOutput.__init__','self.hash = hashlib.sha256()'),
    (CAPTURE,'BoundedOutput.flush','return self.target.flush()'),
    (WORKER,'Tee.flush','self.stream.flush()'),
    (CAPTURE,'strict_json','out = json.loads(data, object_pairs_hook=pairs, parse_constant=reject)'),
    (ATOMIC,'build.Recorder.finish','out = self._typed_finish(raw)'),
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
                    generations_including_initial_upper=1+f+s, not_StringIO_capacity_or_raw_tree_live_counts=True),
                candidate_numeric_limits=json.loads(blobs[CONTRACT])['product_numeric_candidates'],
                no_target_import_execution_compilation_introspection_or_sampling=True)


def raw_representation_reference():
    c = rd(CONTRACT)
    owner = c['heap']['owner_budgets'][9]
    term = rd(P+'D5-I125-complete-heap-review.json')['required_terms'][9]
    raw = c['product_numeric_candidates']['raw_bytes']
    assert raw==12582912 and 5*raw==owner['known_partial_upper']==term['known_partial_upper']==62914560
    assert owner['candidate_budget_bytes']==134217728 and not owner['known_partial_is_complete_term']
    assert owner['known_partial_unit']=='one_Unicode_representation_plus_one_UTF8_payload'
    return dict(raw_bytes_candidate=raw,historical_model_unicode_payload_bytes_per_codepoint=4,
        one_Unicode_scalar_payload_model_bytes=4*raw,one_UTF8_payload_bytes=raw,
        one_representation_pair_payload_subbound_bytes=5*raw,candidate_owner_budget_bytes=134217728,
        arithmetic_budget_minus_representation_pair_bytes=134217728-5*raw,
        arithmetic_distance_is_not_verified_heap_slack=True,
        conditional_accepted_UTF8_route_not_all_failed_or_concurrent_writes=True,
        aggregate_UTF8_bound_is_precondition_not_new_concurrency_theorem=True,
        factor4_is_historical_scalar_payload_model_not_verified_ABI_or_StringIO_capacity=True,
        StringIO_capacity_snapshots_growth_headers_native_and_raw_trees_not_included=True,
        getvalue_reuse_copy_count_and_release_not_proved=True,
        complete_owner_upper_bytes=None,complete_owner_fits=None)


def output_source_relationships():
    indices = {}
    for path in [WORKER,CAPTURE,ATOMIC]:
        index = {}
        pending = [(ast.parse((ROOT/path).read_text()),())]
        while pending:
            node,prefix = pending.pop()
            if isinstance(node,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):
                prefix = prefix+(node.name,)
                index.setdefault('.'.join(prefix),[]).append(node)
            pending.extend((child,prefix) for child in ast.iter_child_nodes(node))
        indices[path] = index

    def get(path,symbol):
        assert len(indices[path][symbol])==1
        return indices[path][symbol][0]

    def one(node,text):
        found = [n for n in ast.walk(node) if not isinstance(n,ast.Expr) and ast.unparse(n)==text]
        assert len(found)==1,text
        return found[0]

    tee = get(WORKER,'Tee')
    assert len(tee.bases)==1 and ast.unparse(tee.bases[0])=='io.StringIO'
    write = get(CAPTURE,'BoundedOutput.write')
    encode = one(write,"b = value.encode('utf8')")
    guard = one(write,"require(self.count + len(b) <= self.limit, 'RAW_BUDGET')")
    forwarded = one(write,'out = self.target.write(value)')
    counted = one(write,'self.count += len(b)')
    assert encode.col_offset<guard.col_offset<forwarded.col_offset<counted.col_offset
    assert encode.lineno==guard.lineno==forwarded.lineno==counted.lineno
    tee_write = get(WORKER,'Tee.write')
    stream = one(tee_write,'n = self.stream.write(s)')
    buffered = one(tee_write,'super().write(s)')
    assert stream.col_offset<buffered.col_offset and stream.lineno==buffered.lineno
    exercise = get(WORKER,'exercise')
    raw = one(exercise,'raw = c.strict_json(stdout.getvalue().encode())')
    finish = one(exercise,'side = rec.finish(raw)')
    aggregate = one(exercise,'c.aggregate_capture(side, c.scenario_metadata(raw, entry), raw, entry)')
    assert raw.lineno<finish.lineno<aggregate.lineno
    return dict(Tee_class_AST=mark(tee),Tee_base_spelling='io.StringIO',
        output_type_guard_AST=mark(one(write,"require(type(value) is str, 'INVALID_OUTPUT_TYPE')")),
        output_encode_AST=mark(encode),raw_budget_guard_AST=mark(guard),target_write_AST=mark(forwarded),
        counter_after_forward_AST=mark(counted),Tee_stream_write_AST=mark(stream),Tee_buffer_write_AST=mark(buffered),
        raw_getvalue_encode_parse_AST=mark(raw),finish_with_raw_AST=mark(finish),post_finish_raw_use_AST=mark(aggregate),
        typed_finish_bridge_AST=mark(one(get(ATOMIC,'build.Recorder.finish'),'out = self._typed_finish(raw)')),
        scalar_representation_bound_not_StringIO_or_parser_storage=True,
        pre_guard_encode_and_forward_error_prefixes_need_separate_bound=True,
        counter_check_forward_update_not_global_atomicity_or_serialization_proof=True,
        getvalue_copy_or_reuse_not_inferred_from_source=True,
        raw_finish_aggregate_order_not_full_lifetime_or_dispatch_proof=True,
        source_only_no_actual_StringIO_capacity_or_native_allocation_proof=True)


def validate_preparation():
    o,r,seal = rd(OUT),rd(REVIEW),rd(SEAL)
    c,scope,plan = rd(CONTRACT),rd(SCOPE),rd(PLAN)
    task = next(t for t in plan['tasks'] if t['id']=='P04-H10')
    owner = c['heap']['owner_budgets'][9]
    prior = rd(P+'D5-I156-integrity.json')
    preserved = {**prior['preserved_published258'],**prior['artifacts'],
                 P+'D5-I156-integrity.json':sha(P+'D5-I156-integrity.json')}
    expected = {OUT,REVIEW,AUDIT,SEAL,DESIGN}
    assert len(preserved)==263 and seal['preserved_published263']==preserved
    assert set(seal['artifacts'])|{SEAL}==expected
    for pins in [preserved,seal['artifacts'],o['input_pins'],r['input_pins'],
                 rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for path,h in pins.items():
            assert sha(path)==h,path
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    assert o['base_commit']==r['base_commit']==seal['base_commit']==BASE
    assert o['date']==r['date']==seal['date']=='2026-11-13'
    assert o['package_id']==task['id']=='P04-H10' and OUT==task['planned_output']
    assert o['schema']==task['output_schema'] and r['schema']=='d5.i157-p04-h10-preparation-review.v1'
    assert seal['schema']=='d5.i157-integrity.v1'
    assert o['status']=='PREPARED_INSUFFICIENT_TEE_STRINGIO_RAW_HEAP_H10_E02_OPEN_NOT_ADMITTED'
    assert r['status']=='P04_H10_PREPARATION_COMPLETE_NO_COMPLETE_BOUND_NO_ADMISSION'
    assert o['plan_binding']==dict(path=PLAN,sha256=sha(PLAN),package_id=task['id'],task_record_canonical_sha256=digest(task))
    assert o['candidate_binding']==dict(path=CONTRACT,sha256=sha(CONTRACT),contract_id=c['contract_id'],subject=c['subject'],source_revision='I122-CANDIDATE-01')
    assert len(task['required_specific_fields'])==9 and set(task['required_specific_fields'])<=set(o)
    assert o['candidate_owner_record']==owner and owner['id']=='H10' and owner['proof_upper_bytes'] is None
    assert o['candidate_budget_bytes']==o['candidate_budget_bytes=134217728']==owner['candidate_budget_bytes']==128*1024**2
    identity = o['owner_id_metric_and_exact_units']
    assert identity['owner_id']=='H10' and identity['owner']==owner['owner']
    assert identity['metric']==owner['metric']=='peak_requested_live_heap'
    assert identity['unit']=='exact_integer_bytes' and identity['candidate_budget_bytes']==134217728
    assert identity['scope_is_requirement_not_verified_bound']
    assert o['source_evidence']==evidence(o['input_pins'])
    assert o['inherited_representation_payload_reference']==raw_representation_reference()
    assert o['output_source_relationships']==output_source_relationships()
    e = o['source_evidence']
    assert (e['input_pin_count'],e['source_file_count'],len(e['projections']),len(e['source_anchors']))==(196,79,12,21)
    assert len(e['lexical_order_witnesses'])==8 and len(e['allocation_expression_witnesses'])==11
    abi = o['source_ABI_allocator_dependencies']
    assert abi['historical_runtime_reference']==c['runtime'] and not abi['exact_runtime_ABI_or_allocator_correspondence_verified']
    assert all(abi[k] is None for k in ['accepted_target_closure','StringIO_capacity_growth_snapshot_and_layout_model',
        'text_UTF8_stream_codec_and_native_buffer_model','raw_tree_finish_and_error_retention_model',
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
    assert all(d[k] for k in ['one_representation_pair_not_complete_StringIO_or_raw_heap',
        'getvalue_copy_or_reuse_not_assumed','pre_guard_encode_and_partial_forward_error_prefixes_need_full_accounting',
        'raw_parse_finish_and_output_roots_need_explicit_overlap_proof',
        'restore_flush_return_not_complete_release_or_global_serialization',
        'factor4_not_accepted_ABI_or_capacity_proof'])
    overlap = o['overlap_alias_original_and_rejected_prefix_treatment']
    assert overlap['inherited_scope']==scope['worker_heap_vs_other_process_scope']
    assert overlap['source_applicability']==scope['321_root_12_group_applicability']['I124_applicability']
    assert [x['other_owner'] for x in overlap['boundary_requirements']]==['H%02d'%i for i in range(1,12) if i!=10]
    assert all(not x['resolved'] for x in overlap['boundary_requirements']) and not overlap['complete_ownership_alias_lifetime_proof']
    dep = o['explicit_assumptions_and_external_dependencies']
    assert not dep['assumptions_verified'] and not dep['P02_exact_runtime_identity_accepted'] and not dep['P03_capacity_service_accepted']
    assert dep['inherited_P01_preconditions']==scope['321_root_12_group_applicability']['original_source_route_preconditions']
    assert all(dep[k] is None for k in ['complete_Tee_StringIO_stream_raw_allocation_inventory',
        'complete_requested_allocation_and_lifetime_theorem','independent_runtime_memory_review'])
    b = o['verified_upper_bytes_and_derivation']
    assert b['verified_upper_bytes'] is None and b['complete_derivation'] is None and not b['verified'] and b['unknown_not_zero']
    assert o['bound_fit_not_just_partial_payload']==dict(candidate_budget_bytes=134217728,
        verified_complete_upper_bytes=None,fit_result='NOT_EVALUABLE_NO_COMPLETE_H10_BOUND',fits=None,
        slack_bytes=None,overbudget_proved=False,actual_unboundedness_proved=False,partial_payload_not_accepted=True)
    assert [x['field'] for x in o['field_assessment']]==task['required_specific_fields']
    for row in o['field_assessment']:
        definition = row['field'] in ['owner_id_metric_and_exact_units','candidate_budget_bytes=134217728']
        assert row['result']==('DOCUMENTARY_DEFINITION_ONLY' if definition else 'INSUFFICIENT_FOR_ACCEPTANCE')
        assert row['basis'] and not row['resource_obligation_closed']
    assert o['acceptance']==dict(rule=task['acceptance'],rejection_rule=task['rejection'],preparation_complete=True,
        accepted_as_complete_H10_proof=False,H10_verified=False,E02_closed=False,resource_obligations_closed=0,no_reserve_transfer=True)
    assert o['dependencies']==rd(H09)['dependencies']
    assert [x['id'] for x in o['dependencies']]==task['depends_on']==['P01','P02']
    provenance = o['producer_and_review_provenance']
    assert provenance['producer_identity']=='Codex assistant preparing I157 in this chat'
    assert provenance['planned_author_role']==task['responsible_role'] and provenance['planned_review_role']==task['review_role']
    assert provenance['independent_reviewer_identity'] is None and not provenance['independent_acceptance'] and not provenance['runtime_custodian_authority_claimed']
    assert not rd(RUNTIME)['acceptance']['accepted_as_runtime_identity'] and not rd(PLATFORM)['acceptance']['accepted_as_platform_evidence']
    assert o['reserve_accounting']==c['reserve_accounting'] and o['non_execution_and_zero_transfer_policy']==scope['non_execution_and_zero_transfer_policy']
    for row,old in zip(o['E02_criterion_disposition'],rd(H09)['E02_criterion_disposition'],strict=True):
        assert row==dict(id=old['id'],inherited_result=old['I155_result'],I157_result=old['I155_result'],closed=False)
    assert r['E02_criterion_disposition']==o['E02_criterion_disposition']
    assert r['input_pins']=={**o['input_pins'],OUT:sha(OUT)}
    assert r['output']==dict(path=OUT,sha256=sha(OUT),schema=o['schema'],evidence_kind=o['evidence_kind'],produced=True)
    assert all(r['preparation_checks'].values())
    assert r['counts']==dict(required_fields=9,documentary_definition_fields=2,insufficient_fields=7,
        required_allocation_classes=12,unknown_inventory_values=48,owner_boundaries=10,source_files=79,
        source_anchors=21,evidence_projections=12,input_pins=196,lexical_order_witnesses=8,
        allocation_expression_witnesses=11,other_unproduced_packages=7)
    for progress,t in zip(r['package_progress'],plan['tasks'],strict=True):
        exists = t['id'] in ['P01','P02','P03']+['P04-H%02d'%i for i in range(1,11)]
        assert (ROOT/t['planned_output']).exists()==progress['output_created']==exists
        assert progress['package_id']==t['id'] and progress['path']==t['planned_output']
        assert progress['sha256']==(sha(t['planned_output']) if exists else None)
    assert r['independent_review']==dict(accepted=False,reviewer_identity=None,no_independent_review_fabricated=True)
    assert not any(o['external_material_scope'][k] for k in ['global_absence_claimed','external_contacts_made','runtime_or_platform_sampled'])
    negative = {('complete_H10_bound_verified' if k=='complete_H09_bound_verified' else k):v for k,v in rd(H09)['decision'].items()}
    assert o['decision']==r['decision']==negative and o['E06']==r['E06']==rd(H09)['E06']
    assert seal['source_only'] and not any(seal[k] for k in ['H10_verified','independent_acceptance',
        'proposal_enabled','product_or_components_executed','quotas_changed','D5_closed'])
    assert seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    assert r['git_publication']['commit_and_push_all_requested']
    assert set(r['work_unit']['rollback_files'])==expected and r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command']=='python3 docs/validation/D5-I157-audit.py'
    assert r['work_unit']['expected_result']=='PASS_STATIC_SOURCE_ONLY' and r['work_unit']['diff_budget_note']
    for path in [P+'D5-JOINT-capture-authorization.json',P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:
        assert not (ROOT/path).exists()

REVIEW_BASE = 'c025f9e1aecd98066acae503e6aa6b6d545c1ad3'
NEW_REVIEW = P + 'D5-I158-P04-H10-documentary-review.json'
RECON = P + 'D5-I158-P04-H10-source-reconstruction.json'
NEW_SEAL = P + 'D5-I158-integrity.json'
NEW_AUDIT = P + 'D5-I158-audit.py'
NEW_DESIGN = 'docs/design/D5-I158-P04-H10-TEE-RAW-HEAP-REVIEW.md'

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

    categories = ['ENCODE_BEFORE_RAW_BYTE_CHECK','RAW_BYTE_CHECK_BEFORE_FORWARD',
        'FORWARD_BEFORE_COUNT_UPDATE','STREAM_FORWARD_BEFORE_STRINGIO_WRITE',
        'RESTORE_BEFORE_RAW_PARSE','RAW_PARSE_BEFORE_FINISH','FINISH_BEFORE_LATER_RAW_AGGREGATION',
        'FINISH_OUTPUT_CONSTRUCTION_BEFORE_SERIALIZED_SIZE_CHECK']
    orders = []
    for i,(row,category) in enumerate(zip(e['lexical_order_witnesses'],categories,strict=True),1):
        before = locate(row['path'],row['symbol'],row['before'])
        after = locate(row['path'],row['symbol'],row['after'])
        assert ast.unparse(before).startswith(row['earlier_expression_prefix'])
        assert ast.unparse(after).startswith(row['later_expression_prefix'])
        assert (before.lineno,before.col_offset)<(after.lineno,after.col_offset)
        orders.append(dict(id='W%02d'%i,path=row['path'],symbol=row['symbol'],classification=category,
            published_record_sha256=digest(row),before_expression=ast.unparse(before),after_expression=ast.unparse(after),
            source_order_not_allocation_copy_or_lifetime_proof=True))
    expressions = []
    for row in e['allocation_expression_witnesses']:
        for signature in row['sites']:
            assert ast.unparse(locate(row['path'],row['symbol'],signature))==row['expression']
        expressions.append(dict(path=row['path'],symbol=row['symbol'],expression=row['expression'],
            site_count=len(row['sites']),published_record_sha256=digest(row)))

    def one(node,text):
        found = [n for n in ast.walk(node) if not isinstance(n,ast.Expr) and ast.unparse(n)==text]
        assert len(found)==1,text
        return found[0]

    relationship = o['output_source_relationships']
    marker_specs = [
        ('output_type_guard_AST',CAPTURE,'BoundedOutput.write',"require(type(value) is str, 'INVALID_OUTPUT_TYPE')"),
        ('output_encode_AST',CAPTURE,'BoundedOutput.write',"b = value.encode('utf8')"),
        ('raw_budget_guard_AST',CAPTURE,'BoundedOutput.write',"require(self.count + len(b) <= self.limit, 'RAW_BUDGET')"),
        ('target_write_AST',CAPTURE,'BoundedOutput.write','out = self.target.write(value)'),
        ('counter_after_forward_AST',CAPTURE,'BoundedOutput.write','self.count += len(b)'),
        ('Tee_stream_write_AST',WORKER,'Tee.write','n = self.stream.write(s)'),
        ('Tee_buffer_write_AST',WORKER,'Tee.write','super().write(s)'),
        ('raw_getvalue_encode_parse_AST',WORKER,'exercise','raw = c.strict_json(stdout.getvalue().encode())'),
        ('finish_with_raw_AST',WORKER,'exercise','side = rec.finish(raw)'),
        ('post_finish_raw_use_AST',WORKER,'exercise','c.aggregate_capture(side, c.scenario_metadata(raw, entry), raw, entry)'),
        ('typed_finish_bridge_AST',ATOMIC,'build.Recorder.finish','out = self._typed_finish(raw)'),
    ]
    marker_checks = []
    for key,path,symbol,text in marker_specs:
        node = one(nodes[(path,symbol)],text)
        assert mark(node)==relationship[key]
        marker_checks.append(dict(key=key,path=path,symbol=symbol,expression=text,**mark(node)))
    assert len(indices[WORKER]['Tee'])==1
    tee = indices[WORKER]['Tee'][0]
    assert len(tee.bases)==1 and ast.unparse(tee.bases[0])=='io.StringIO'
    assert mark(tee)==relationship['Tee_class_AST'] and relationship['Tee_base_spelling']=='io.StringIO'
    write = nodes[(CAPTURE,'BoundedOutput.write')]
    typed = one(write,"require(type(value) is str, 'INVALID_OUTPUT_TYPE')")
    encoded = one(write,"b = value.encode('utf8')")
    guard = one(write,"require(self.count + len(b) <= self.limit, 'RAW_BUDGET')")
    forwarded = one(write,'out = self.target.write(value)')
    counted = one(write,'self.count += len(b)')
    assert typed.lineno==encoded.lineno==guard.lineno==forwarded.lineno==counted.lineno
    assert typed.col_offset<encoded.col_offset<guard.col_offset<forwarded.col_offset<counted.col_offset
    exercise = nodes[(WORKER,'exercise')]
    parsed = one(exercise,'raw = c.strict_json(stdout.getvalue().encode())')
    finish = one(exercise,'side = rec.finish(raw)')
    aggregate = one(exercise,'c.aggregate_capture(side, c.scenario_metadata(raw, entry), raw, entry)')
    assert parsed.lineno<finish.lineno<aggregate.lineno
    flushes = dict(BoundedOutput_flush_AST=mark(nodes[(CAPTURE,'BoundedOutput.flush')]),
        Tee_flush_AST=mark(nodes[(WORKER,'Tee.flush')]),
        restore_AST=mark(one(exercise,'rec.restore()')),flush_AST=mark(one(exercise,'sink.flush()')),
        no_close_shrink_or_all_root_release_theorem=True)
    relationships = dict(marker_checks=marker_checks,Tee_class_AST=mark(tee),base_spelling='io.StringIO',
        flush_restore_source_checks=flushes,published_relationship_record_sha256=digest(relationship),
        guard_forward_count_order_not_global_atomicity_or_serialization=True,
        getvalue_copy_or_reuse_not_established=True,raw_finish_use_not_complete_root_lifetime_proof=True)
    c = json.loads(data[CONTRACT][1])
    owner = c['heap']['owner_budgets'][9]
    old_term = json.loads(data[P+'D5-I125-complete-heap-review.json'][1])['required_terms'][9]
    b = c['product_numeric_candidates']['raw_bytes']
    assert b==12582912 and 5*b==owner['known_partial_upper']==old_term['known_partial_upper']==62914560
    assert not owner['known_partial_is_complete_term'] and owner['proof_upper_bytes'] is None
    assert owner['candidate_budget_bytes']==134217728 and 134217728-5*b==71303168
    partial = o['inherited_representation_payload_reference']
    assert partial['one_representation_pair_payload_subbound_bytes']==5*b
    assert partial['arithmetic_budget_minus_representation_pair_bytes']==71303168
    assert partial['aggregate_UTF8_bound_is_precondition_not_new_concurrency_theorem']
    arithmetic = dict(raw_bytes_candidate=b,historical_scalar_payload_factor=4,
        one_Unicode_scalar_payload_model_bytes=4*b,one_UTF8_payload_bytes=b,
        conditional_one_pair_payload_bytes=5*b,candidate_owner_budget_bytes=134217728,
        budget_minus_pair_arithmetic_only=71303168,
        aggregate_accepted_UTF8_bound_is_precondition_not_verified_all_writer_theorem=True,
        historical_factor_not_verified_StringIO_ABI_capacity_or_total_raw_memory=True,
        not_complete_owner_fit_or_verified_slack=True)
    counts = json.loads(data[I124][1])
    f,s = counts['global_F_upper'],counts['global_S_upper']
    assert (f,s,f+s,1+f+s)==(52018,1759,53777,53778)
    assert e['inherited_count_reference']==dict(F_upper=f,S_upper=s,clone_batches_upper=f+s,
        generations_including_initial_upper=1+f+s,not_StringIO_capacity_or_raw_tree_live_counts=True)
    inventory,unknowns = [],[]
    for i,row in enumerate(o['complete_live_allocation_inventory']['required_classes']):
        for key in ['cardinality_upper','size_upper_bytes','maximum_live_upper_bytes','lifetime_derivation']:
            assert row[key] is None
            unknowns.append('/complete_live_allocation_inventory/required_classes/'+str(i)+'/'+key)
        assert not row['verified']
        inventory.append(dict(id=row['id'],record_sha256=digest(row),complete_count_size_peak_lifetime_unproved=True))
    boundaries = o['overlap_alias_original_and_rejected_prefix_treatment']['boundary_requirements']
    assert all(not x['resolved'] for x in boundaries)
    return dict(preparation_commit=o['base_commit'],published_commit=REVIEW_BASE,
        H10_published_blob_oid=oid,H10_sha256=sha(OUT),input_pin_checks=inputs,projection_checks=projections,
        source_file_count=len(sources),source_pin_vector_sha256=digest(sources),
        file_summary_vector_sha256=digest(summaries),syntax_counts=totals,syntax_site_vector_sha256=digest(vector),
        source_anchor_checks=anchors,classified_order_checks=orders,expression_checks=expressions,
        output_StringIO_raw_source_checks=relationships,inherited_representation_arithmetic_check=arithmetic,
        inherited_count_reference=e['inherited_count_reference'],inventory_checks=inventory,unknown_inventory_pointers=unknowns,
        boundary_record_sha256={x['other_owner']:digest(x) for x in boundaries},
        field_record_sha256={x['field']:digest(o[x['field']]) for x in o['field_assessment']},
        no_runtime_StringIO_output_raw_allocation_lifetime_or_native_capacity_proof=True)


def main():
    validate_preparation()
    o,z,r,seal = rd(OUT),rd(RECON),rd(NEW_REVIEW),rd(NEW_SEAL)
    prior = rd(SEAL)
    preserved = {**prior['preserved_published263'],**prior['artifacts'],SEAL:sha(SEAL)}
    expected = {NEW_REVIEW,RECON,NEW_AUDIT,NEW_SEAL,NEW_DESIGN}
    assert len(preserved)==268 and seal['preserved_published268']==preserved
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
    assert r['schema']=='d5.i158-p04-h10-documentary-review.v1'
    assert z['schema']=='d5.i158-p04-h10-source-reconstruction.v1'
    assert seal['schema']=='d5.i158-integrity.v1'
    assert z['reconstruction']==reconstruct()
    pins = {**o['input_pins'],OUT:sha(OUT),REVIEW:sha(REVIEW),SEAL:sha(SEAL),AUDIT:sha(AUDIT)}
    assert z['input_pins']==pins and r['input_pins']=={**pins,RECON:sha(RECON)}
    assert r['H10']==dict(path=OUT,sha256=sha(OUT),bytes_preserved=True)
    assert r['plan_binding']==o['plan_binding'] and r['source_reconstruction']==dict(path=RECON,sha256=sha(RECON))
    assert r['status']=='REVIEW_COMPLETE_DOSSIER_CONFORMANT_H10_PROOF_REJECTED_NO_ADMISSION'
    assert r['documentary_dossier_conformance'] and not r['H10_change_required'] and r['blocking_dossier_defects']==[]
    reviewer = r['reviewer']
    assert reviewer['same_assistant_as_preparer'] and reviewer['methodologically_separate_reconstruction']
    assert not reviewer['actor_independence'] and not reviewer['organizational_independence'] and not reviewer['runtime_custodian_authority']
    assert [check['id'] for check in r['checks']]==['R%02d'%i for i in range(1,16)]
    for check in r['checks']:
        assert check['result']=='CONFORMANT_DOCUMENTARY_INSUFFICIENCY_JUDGMENT'
        assert check['basis'] and not check['resource_obligation_closed']
    assert r['field_disposition']==[dict(field=x['field'],inherited_result=x['result'],I158_result=x['result'],
        field_record_sha256=digest(o[x['field']]),resource_obligation_closed=False) for x in o['field_assessment']]
    assert r['E02_criterion_disposition']==[dict(id=x['id'],inherited_result=x['I157_result'],
        I158_result=x['I157_result'],closed=False) for x in o['E02_criterion_disposition']]
    assert r['acceptance']==dict(review_completed=True,insufficiency_judgment_confirmed=True,
        accepted_as_complete_H10_proof=False,H10_verified=False,independent_acceptance=False,
        independent_reviewer_identity=None,E02_closed=False,E01_E05_closed=False,resource_obligations_closed=0,fit_or_overbudget_proof=False)
    assert r['counts']==dict(input_pins_reconstructed=196,evidence_projections=12,source_files=79,
        source_anchors=21,order_relations=8,expression_records=11,output_lifetime_relationship_groups=1,
        inherited_representation_arithmetic_checks=1,required_fields=9,documentary_definition_fields=2,insufficient_fields=7,
        required_allocation_classes=12,unknown_inventory_values=48,owner_boundaries=10,review_checks=15,other_unproduced_packages=7)
    assert all(r[k] is None for k in ['verified_complete_upper_bytes','fits','slack_bytes'])
    assert r['pending_independent_acceptance_and_P02_P03_not_bypassed'] and r['other_packages_started']==0
    assert len(r['limitations'])>=10 and r['E06']==o['E06'] and r['decision']==o['decision']
    assert r['git_publication']['commit_and_push_all_requested']
    assert set(r['work_unit']['rollback_files'])==expected and r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command']=='python3 docs/validation/D5-I158-audit.py'
    assert r['work_unit']['expected_result']=='PASS_STATIC_SOURCE_ONLY' and r['work_unit']['diff_budget_note']
    assert seal['source_only'] and seal['documentary_dossier_conformance']
    assert not any(seal[k] for k in ['H10_verified','independent_acceptance','product_or_components_executed',
        'quotas_changed','proposal_enabled','D5_closed'])
    assert seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I158',package='P04-H10',
        documentary_dossier_conformance=True,accepted_as_complete_H10_proof=False,independent_acceptance=False,
        Git_input_pins_checked=196,evidence_projections=12,source_files=79,source_anchors=21,
        classified_order_relations=8,insufficient_fields=7,prior_published_files_preserved=268,new_files=5,
        inherited_representation_payload_subbound_bytes=62914560,payload_distance_not_heap_slack=True,
        product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
