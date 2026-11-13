#!/usr/bin/env python3
"""I155: documentary JSON/Git/AST checks only; never import or run a target."""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'bb41c1185358ffe959adc6f80e136e899df2b746'
OUT = P + 'D5-PFC126-03-E02-H09.json'
REVIEW = P + 'D5-I155-P04-H09-preparation-review.json'
SEAL = P + 'D5-I155-integrity.json'
AUDIT = P + 'D5-I155-audit.py'
DESIGN = 'docs/design/D5-I155-P04-H09-EVENT-CHUNKS-PENDING-FLUSH-HEAP.md'
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
H08 = P + 'D5-PFC126-03-E02-H08.json'
WORKER = 'testing/prospective_capture_joint_i122/worker.py'
PROJECTIONS = [
    (CONTRACT, '/heap/owner_budgets/8'),
    (P + 'D5-I125-complete-heap-review.json', '/required_terms/8'),
    (P + 'D5-I123-transient-resource-envelope.json', '/memory'),
    (P + 'D5-I124-resource-admission-review.json', '/page_payload'),
    (I124, '/lifetime_envelope'), (I124, '/scope'),
    (RUNTIME, '/acceptance'), (PLATFORM, '/acceptance'),
    (P + 'D5-I154-P04-H08-documentary-review.json', '/acceptance'),
    (H08, '/overlap_alias_original_and_rejected_prefix_treatment'),
    (SCOPE, '/worker_heap_vs_other_process_scope'), (CONTRACT, '/product_numeric_candidates'),
]
SPECS = [
    (ATOMIC,'clone_metadata'), (ATOMIC,'build.Pages.append'),
    (ATOMIC,'build.Pages.flush'), (ATOMIC,'build.Pages.close'),
    (ATOMIC,'build.Recorder.__init__'), (ATOMIC,'build.Recorder._fork'),
    (ATOMIC,'build.Recorder._publish'), (ATOMIC,'build.Recorder._atomic'),
    (ATOMIC,'build.Recorder._drain'), (ATOMIC,'build.Recorder._observe'),
    (ATOMIC,'build.Recorder.reference'), (ATOMIC,'build.Recorder._typed_finish'),
    (TYPED,'PageSink.__init__'), (TYPED,'PageSink.header'), (TYPED,'PageSink.size'),
    (TYPED,'PageSink.append'), (TYPED,'PageSink.flush'), (TYPED,'PageSink.close'),
    (TYPED,'encode'), (TYPED,'Recorder.emit'), (WORKER,'exercise'),
]
CENSUS = ['Call','List','Tuple','Dict','Set','ListComp','SetComp',
          'DictComp','GeneratorExp','ExceptHandler']
# Source order only; relations include preguards/publication/reset/IO, not peak proofs.
ORDERS = [
    (TYPED,'PageSink.append','b = encode(event)','c.require(len(b)'),
    (TYPED,'PageSink.append','self.flush()','self.chunks.append(b)'),
    (ATOMIC,'build.Pages.flush',"p.fault(self._planning, 'CAUSAL_SCHEMA_INVALID')",'body = '),
    (ATOMIC,'build.Pages.flush','body = ','p.fault(len(body) =='),
    (ATOMIC,'build.Pages.flush','body = ','p.fault(self.total_bytes + len(body)'),
    (ATOMIC,'build.Pages.flush','self._reference()','self._writes.append((name, body))'),
    (ATOMIC,'build.Pages.flush','self._writes.append((name, body))','self.chunks = []'),
    (ATOMIC,'build.Recorder._atomic','writes = tuple(draft.events._writes)','self._publish(draft)'),
    (ATOMIC,'build.Recorder._atomic','self._publish(draft)','p.write_all(fd, body)'),
    (ATOMIC,'build.Recorder._publish','self.events = draft.events','self.events._writes = []'),
]
FACTS = [
    (ATOMIC,'build.Pages.flush',"b','.join(self.chunks)"),
    (ATOMIC,'build.Pages.flush','p.encode(header)'),
    (ATOMIC,'build.Pages.flush','self._writes.append((name, body))'),
    (ATOMIC,'build.Pages.flush','self.chunks = []'),
    (ATOMIC,'build.Recorder._fork','draft._memo = memo'),
    (ATOMIC,'clone_metadata','memo[key] = out'),
    (ATOMIC,'clone_metadata','return value'),
    (ATOMIC,'build.Recorder._atomic','writes = tuple(draft.events._writes)'),
    (ATOMIC,'build.Recorder._atomic','self._pending_io += 1'),
    (ATOMIC,'build.Recorder._atomic','self._pending_io -= 1'),
    (ATOMIC,'build.Recorder._typed_finish','self._drain()'),
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
                    generations_including_initial_upper=1+f+s, not_complete_page_storage_or_overlap_counts=True),
                candidate_numeric_limits=json.loads(blobs[CONTRACT])['product_numeric_candidates'],
                no_target_import_execution_compilation_introspection_or_sampling=True)


def page_source_relationships():
    indices = {}
    for path in [ATOMIC,TYPED]:
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

    clone = get(ATOMIC,'clone_metadata')
    kinds = [ast.unparse(n.test) for n in ast.walk(clone) if isinstance(n,ast.If)
             and ast.unparse(n.test).startswith('kind is ')]
    assert set(kinds)=={'kind is dict','kind is list','kind is tuple','kind is set','kind is frozenset'}
    last = [n for n in ast.walk(clone) if isinstance(n,ast.If) and ast.unparse(n.test)=='kind is frozenset']
    assert len(last)==1 and len(last[0].orelse)==1 and ast.unparse(last[0].orelse[0])=='return value'
    memo_sites = [mark(n) for n in ast.walk(clone) if isinstance(n,ast.Assign) and ast.unparse(n)=='memo[key] = out']
    assert len(memo_sites)==5
    flush = get(ATOMIC,'build.Pages.flush')
    bodies = [n for n in ast.walk(flush) if isinstance(n,ast.Assign)
              and any(isinstance(t,ast.Name) and t.id=='body' for t in n.targets)]
    assert len(bodies)==1
    append = one(flush,'self._writes.append((name, body))')
    clear = one(flush,'self.chunks = []')
    assert bodies[0].lineno<append.lineno<clear.lineno
    atomic = get(ATOMIC,'build.Recorder._atomic')
    locks = [n for n in ast.walk(atomic) if isinstance(n,ast.With)
        and any(ast.unparse(item.context_expr)=='self._state_lock' for item in n.items)]
    assert len(locks)==1
    writes = one(atomic,'writes = tuple(draft.events._writes)')
    publish = one(atomic,'self._publish(draft)')
    io_write = one(atomic,'p.write_all(fd, body)')
    decrement = one(atomic,'self._pending_io -= 1')
    returned = one(atomic,'return value')
    assert locks[0].lineno<writes.lineno<publish.lineno<=locks[0].end_lineno<io_write.lineno<decrement.lineno<returned.lineno
    return dict(clone_kind_branches=sorted(kinds),scalar_fallback_AST=mark(last[0].orelse[0]),
        memo_assignment_sites=sorted(memo_sites,key=lambda r:(r['line'],r['column'])),
        draft_memo_root_AST=mark(one(get(ATOMIC,'build.Recorder._fork'),'draft._memo = memo')),
        flush_body_AST=mark(bodies[0]),flush_queued_body_AST=mark(append),chunks_reset_AST=mark(clear),
        pending_writes_tuple_AST=mark(writes),publish_AST=mark(publish),metadata_lock_AST=mark(locks[0]),
        IO_write_AST=mark(io_write),pending_decrement_AST=mark(decrement),return_AST=mark(returned),
        publish_writes_reset_AST=mark(one(get(ATOMIC,'build.Recorder._publish'),'self.events._writes = []')),
        scalar_fallback_not_free_container_storage_or_alias_credit=True,
        memo_list_roots_and_local_pending_writes_not_dropped_by_chunks_reset=True,
        counter_drain_or_return_not_complete_collection_or_peak_proof=True,
        source_only_no_actual_layout_dispatch_or_lifetime_proof=True)


def page_payload_reference():
    old = rd(P+'D5-I124-resource-admission-review.json')['page_payload']
    memory = rd(P+'D5-I123-transient-resource-envelope.json')['memory']
    owner = rd(CONTRACT)['heap']['owner_budgets'][8]
    limits = rd(CONTRACT)['product_numeric_candidates']
    assert limits['pages']==32 and limits['page_bytes']==2097152
    assert 32*2097152==limits['event_pages_total_bytes']==67108864
    assert old['pending_bodies_upper']==old['all_unique_historical_chunks_upper']==67108864
    assert old['bodies_plus_chunks_upper']==owner['known_partial_upper']==134217728
    assert old['old_memo_chunks_included'] and not old['encoding_and_object_storage_included'] and old['not_a_RAM_quota']
    assert memory['all_historical_unique_chunk_payload_upper']==67108864
    assert memory['bodies_plus_unique_chunks_payload_upper']==134217728
    assert not memory['global_byte_upper_verified'] and memory['payload_bound_is_not_heap_or_RSS_bound']
    assert owner['candidate_budget_bytes']==201326592 and owner['known_partial_unit']=='pending_bodies_plus_unique_chunk_payload'
    assert not owner['known_partial_is_complete_term']
    return dict(pages_candidate=32,page_bytes_candidate=2097152,event_pages_total_bytes_candidate=67108864,
        inherited_pending_body_payload_upper_bytes=67108864,
        inherited_all_unique_historical_chunk_payload_upper_bytes=67108864,
        inherited_bodies_plus_distinct_chunks_payload_upper_bytes=134217728,
        historical_memo_chunks_included=True,encoding_headers_lists_native_overhead_included=False,
        candidate_owner_budget_bytes=201326592,arithmetic_budget_minus_payload_bytes=67108864,
        arithmetic_distance_is_not_verified_heap_slack=True,
        complete_owner_upper_bytes=None,complete_owner_fits=None,
        conditional_successful_path_payload_not_all_rejected_prefixes_or_global_observer=True,
        distinct_payload_not_allocation_headers_capacity_or_retained_pointer_occurrences=True,
        no_alias_discount_or_N_times_duplicate_payload_charge_inferred=True,
        future_input_or_protocol_change_requires_separate_review=True)


def main():
    o,r,seal = rd(OUT),rd(REVIEW),rd(SEAL)
    c,scope,plan = rd(CONTRACT),rd(SCOPE),rd(PLAN)
    task = next(t for t in plan['tasks'] if t['id']=='P04-H09')
    owner = c['heap']['owner_budgets'][8]
    prior = rd(P+'D5-I154-integrity.json')
    preserved = {**prior['preserved_published248'],**prior['artifacts'],
                 P+'D5-I154-integrity.json':sha(P+'D5-I154-integrity.json')}
    expected = {OUT,REVIEW,AUDIT,SEAL,DESIGN}
    assert len(preserved)==253 and seal['preserved_published253']==preserved
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
    assert o['package_id']==task['id']=='P04-H09' and OUT==task['planned_output']
    assert o['schema']==task['output_schema'] and r['schema']=='d5.i155-p04-h09-preparation-review.v1'
    assert seal['schema']=='d5.i155-integrity.v1'
    assert o['status']=='PREPARED_INSUFFICIENT_EVENT_CHUNKS_PENDING_FLUSH_HEAP_H09_E02_OPEN_NOT_ADMITTED'
    assert r['status']=='P04_H09_PREPARATION_COMPLETE_NO_COMPLETE_BOUND_NO_ADMISSION'
    assert o['plan_binding']==dict(path=PLAN,sha256=sha(PLAN),package_id=task['id'],task_record_canonical_sha256=digest(task))
    assert o['candidate_binding']==dict(path=CONTRACT,sha256=sha(CONTRACT),contract_id=c['contract_id'],subject=c['subject'],source_revision='I122-CANDIDATE-01')
    assert len(task['required_specific_fields'])==9 and set(task['required_specific_fields'])<=set(o)
    assert o['candidate_owner_record']==owner and owner['id']=='H09' and owner['proof_upper_bytes'] is None
    assert o['candidate_budget_bytes']==o['candidate_budget_bytes=201326592']==owner['candidate_budget_bytes']==192*1024**2
    identity = o['owner_id_metric_and_exact_units']
    assert identity['owner_id']=='H09' and identity['owner']==owner['owner']
    assert identity['metric']==owner['metric']=='peak_requested_live_heap'
    assert identity['unit']=='exact_integer_bytes' and identity['candidate_budget_bytes']==201326592
    assert identity['scope_is_requirement_not_verified_bound']
    assert o['source_evidence']==evidence(o['input_pins'])
    assert o['page_source_relationships']==page_source_relationships()
    assert o['inherited_page_payload_reference']==page_payload_reference()
    e = o['source_evidence']
    assert (e['input_pin_count'],e['source_file_count'],len(e['projections']),len(e['source_anchors']))==(188,79,12,21)
    assert len(e['lexical_order_witnesses'])==10 and len(e['allocation_expression_witnesses'])==11
    abi = o['source_ABI_allocator_dependencies']
    assert abi['historical_runtime_reference']==c['runtime'] and not abi['exact_runtime_ABI_or_allocator_correspondence_verified']
    assert all(abi[k] is None for k in ['accepted_target_closure','bytes_list_dict_tuple_growth_and_header_model',
        'join_concat_unicode_native_workspace_model','memo_pending_IO_and_rejected_prefix_lifetime_model',
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
    assert all(d[k] for k in ['distinct_payload_not_full_heap_or_global_observer_bound',
        'historical_memo_chunk_retention_not_dropped_at_reset',
        'pre_guard_encode_join_concat_and_failure_prefixes_need_full_accounting',
        'publication_reset_pending_counter_or_drain_not_prompt_release_proof',
        'no_extra_per_page_per_thread_or_allocator_reserve',
        'metadata_lock_not_pending_IO_lifetime_serialization'])
    overlap = o['overlap_alias_original_and_rejected_prefix_treatment']
    assert overlap['inherited_scope']==scope['worker_heap_vs_other_process_scope']
    assert overlap['source_applicability']==scope['321_root_12_group_applicability']['I124_applicability']
    assert [x['other_owner'] for x in overlap['boundary_requirements']]==['H%02d'%i for i in range(1,12) if i!=9]
    assert all(not x['resolved'] for x in overlap['boundary_requirements']) and not overlap['complete_ownership_alias_lifetime_proof']
    dep = o['explicit_assumptions_and_external_dependencies']
    assert not dep['assumptions_verified'] and not dep['P02_exact_runtime_identity_accepted'] and not dep['P03_capacity_service_accepted']
    assert dep['inherited_P01_preconditions']==scope['321_root_12_group_applicability']['original_source_route_preconditions']
    assert all(dep[k] is None for k in ['complete_chunk_page_list_memo_IO_allocation_inventory',
        'complete_requested_allocation_and_lifetime_theorem','independent_runtime_memory_review'])
    b = o['verified_upper_bytes_and_derivation']
    assert b['verified_upper_bytes'] is None and b['complete_derivation'] is None and not b['verified'] and b['unknown_not_zero']
    assert o['bound_fit_not_just_partial_payload']==dict(candidate_budget_bytes=201326592,
        verified_complete_upper_bytes=None,fit_result='NOT_EVALUABLE_NO_COMPLETE_H09_BOUND',fits=None,
        slack_bytes=None,overbudget_proved=False,actual_unboundedness_proved=False,partial_payload_not_accepted=True)
    assert [x['field'] for x in o['field_assessment']]==task['required_specific_fields']
    for row in o['field_assessment']:
        definition = row['field'] in ['owner_id_metric_and_exact_units','candidate_budget_bytes=201326592']
        assert row['result']==('DOCUMENTARY_DEFINITION_ONLY' if definition else 'INSUFFICIENT_FOR_ACCEPTANCE')
        assert row['basis'] and not row['resource_obligation_closed']
    assert o['acceptance']==dict(rule=task['acceptance'],rejection_rule=task['rejection'],preparation_complete=True,
        accepted_as_complete_H09_proof=False,H09_verified=False,E02_closed=False,resource_obligations_closed=0,no_reserve_transfer=True)
    assert o['dependencies']==rd(H08)['dependencies']
    assert [x['id'] for x in o['dependencies']]==task['depends_on']==['P01','P02']
    provenance = o['producer_and_review_provenance']
    assert provenance['producer_identity']=='Codex assistant preparing I155 in this chat'
    assert provenance['planned_author_role']==task['responsible_role'] and provenance['planned_review_role']==task['review_role']
    assert provenance['independent_reviewer_identity'] is None and not provenance['independent_acceptance'] and not provenance['runtime_custodian_authority_claimed']
    assert not rd(RUNTIME)['acceptance']['accepted_as_runtime_identity'] and not rd(PLATFORM)['acceptance']['accepted_as_platform_evidence']
    assert o['reserve_accounting']==c['reserve_accounting'] and o['non_execution_and_zero_transfer_policy']==scope['non_execution_and_zero_transfer_policy']
    for row,old in zip(o['E02_criterion_disposition'],rd(H08)['E02_criterion_disposition'],strict=True):
        assert row==dict(id=old['id'],inherited_result=old['I153_result'],I155_result=old['I153_result'],closed=False)
    assert r['E02_criterion_disposition']==o['E02_criterion_disposition']
    assert r['input_pins']=={**o['input_pins'],OUT:sha(OUT)}
    assert r['output']==dict(path=OUT,sha256=sha(OUT),schema=o['schema'],evidence_kind=o['evidence_kind'],produced=True)
    assert all(r['preparation_checks'].values())
    assert r['counts']==dict(required_fields=9,documentary_definition_fields=2,insufficient_fields=7,
        required_allocation_classes=12,unknown_inventory_values=48,owner_boundaries=10,source_files=79,
        source_anchors=21,evidence_projections=12,input_pins=188,lexical_order_witnesses=10,
        allocation_expression_witnesses=11,other_unproduced_packages=8)
    for progress,t in zip(r['package_progress'],plan['tasks'],strict=True):
        exists = t['id'] in ['P01','P02','P03']+['P04-H%02d'%i for i in range(1,10)]
        assert (ROOT/t['planned_output']).exists()==progress['output_created']==exists
        assert progress['package_id']==t['id'] and progress['path']==t['planned_output']
        assert progress['sha256']==(sha(t['planned_output']) if exists else None)
    assert r['independent_review']==dict(accepted=False,reviewer_identity=None,no_independent_review_fabricated=True)
    assert not any(o['external_material_scope'][k] for k in ['global_absence_claimed','external_contacts_made','runtime_or_platform_sampled'])
    negative = {('complete_H09_bound_verified' if k=='complete_H08_bound_verified' else k):v for k,v in rd(H08)['decision'].items()}
    assert o['decision']==r['decision']==negative and o['E06']==r['E06']==rd(H08)['E06']
    assert seal['source_only'] and not any(seal[k] for k in ['H09_verified','independent_acceptance',
        'proposal_enabled','product_or_components_executed','quotas_changed','D5_closed'])
    assert seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    assert r['git_publication']['commit_and_push_all_requested']
    assert set(r['work_unit']['rollback_files'])==expected and r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command']=='python3 docs/validation/D5-I155-audit.py'
    assert r['work_unit']['expected_result']=='PASS_STATIC_SOURCE_ONLY' and r['work_unit']['diff_budget_note']
    for path in [P+'D5-JOINT-capture-authorization.json',P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:
        assert not (ROOT/path).exists()
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I155',package='P04-H09',
        preparation_complete=True,accepted_as_complete_H09_proof=False,candidate_budget_bytes=201326592,
        inherited_distinct_payload_subbound_bytes=134217728,insufficient_fields=7,source_files=79,
        source_anchors=21,prior_published_files_preserved=253,new_files=5,product_or_components_executed=0,
        quotas_changed=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,
        IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
