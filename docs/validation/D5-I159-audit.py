#!/usr/bin/env python3
"""I159: documentary JSON/Git/AST checks only; never import or run a target."""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '8f919d08ec79ca6c8b51a9c04c4d997a4059ffb3'
OUT = P + 'D5-PFC126-03-E02-H11.json'
REVIEW = P + 'D5-I159-P04-H11-preparation-review.json'
SEAL = P + 'D5-I159-integrity.json'
AUDIT = P + 'D5-I159-audit.py'
DESIGN = 'docs/design/D5-I159-P04-H11-ALLOCATOR-OVERHEAD-HEAP.md'
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
H10 = P + 'D5-PFC126-03-E02-H10.json'
H07 = P + 'D5-PFC126-03-E02-H07.json'
WORKER = 'testing/prospective_capture_joint_i122/worker.py'
PROJECTIONS = [
    (CONTRACT, '/heap/owner_budgets/10'),
    (P + 'D5-I125-complete-heap-review.json', '/required_terms/10'),
    (SCOPE, '/requested_committed_metrics'),
    (SCOPE, '/worker_heap_vs_other_process_scope'),
    (RUNTIME, '/native_dependency_allocator_kernel_config_pins'),
    (RUNTIME, '/source_binary_build_correspondence'),
    (RUNTIME, '/actual_target_not_just_observed_local_reference'),
    (RUNTIME, '/acceptance'), (PLATFORM, '/acceptance'),
    (CONTRACT, '/reserve_accounting/heap'),
    (P + 'D5-I158-P04-H10-documentary-review.json', '/acceptance'),
    (H10, '/overlap_alias_original_and_rejected_prefix_treatment'),
]
SPECS = [
    (ATOMIC,'clone_metadata'), (ATOMIC,'build.Recorder._fork'),
    (ATOMIC,'build.Recorder._publish'), (ATOMIC,'build.Recorder._atomic'),
    (ATOMIC,'build.Recorder._drain'), (ATOMIC,'build.Recorder._typed_finish'),
    (ATOMIC,'build.Pages.flush'),
    (CAPTURE,'Reader.__init__'), (CAPTURE,'Reader.read'), (CAPTURE,'Reader.listing'),
    (CAPTURE,'strict_json'), (CAPTURE,'digest_value'), (CAPTURE,'BoundedOutput.write'),
    (TYPED,'Projector.observe'), (TYPED,'PageSink.append'), (TYPED,'PageSink.size'), (TYPED,'encode'),
    (WORKER,'Tee.write'), (WORKER,'exercise'), (WORKER,'main'),
    (JOINT,'InputPlan.after'), (JOINT,'PhaseBytes.__init__'),
    (JOINT,'SideWriter.write'), (JOINT,'MemberReader.read'),
]
CENSUS = ['Call','List','Tuple','Dict','Set','ListComp','SetComp',
          'DictComp','GeneratorExp','ExceptHandler']
# Workload order witnesses are not native allocator geometry or decommit evidence.
ORDERS = [
    (ATOMIC,'build.Recorder._fork','memo = {}','draft._memo = memo'),
    (ATOMIC,'build.Recorder._atomic','draft = self._fork()','self._publish(draft)'),
    (ATOMIC,'build.Recorder._atomic','self._publish(draft)','p.write_all(fd, body)'),
    (ATOMIC,'build.Pages.flush','body = ','self.chunks = []'),
    (CAPTURE,'Reader.read','chunks.append(b)',"return b''.join(chunks)"),
    (CAPTURE,'Reader.listing','names = tuple(sorted(os.listdir(fd)))','require(len(names)'),
    (JOINT,'InputPlan.after','bodies[name] = self.reader.read(name)','self.view = PhaseBytes('),
    (CAPTURE,'BoundedOutput.write',"b = value.encode('utf8')",'require(self.count + len(b)'),
]
FACTS = [
    (ATOMIC,'clone_metadata','memo[key] = out'),
    (ATOMIC,'build.Recorder._fork','draft._memo = memo'),
    (ATOMIC,'build.Recorder._publish','self.events._writes = []'),
    (ATOMIC,'build.Recorder._atomic','writes = tuple(draft.events._writes)'),
    (ATOMIC,'build.Recorder._drain','self._idle.wait(remaining)'),
    (ATOMIC,'build.Pages.flush',"b','.join(self.chunks)"),
    (CAPTURE,'Reader.read',"return b''.join(chunks)"),
    (JOINT,'PhaseBytes.__init__','self.bodies = dict(bodies)'),
    (CAPTURE,'strict_json','out = json.loads(data, object_pairs_hook=pairs, parse_constant=reject)'),
    (TYPED,'Projector.observe','refs = set()'),
    (WORKER,'exercise','raw = c.strict_json(stdout.getvalue().encode())'),
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
                    generations_including_initial_upper=1+f+s, not_allocator_geometry_or_backing_retention_counts=True),
                candidate_numeric_limits=json.loads(blobs[CONTRACT])['product_numeric_candidates'],
                no_target_import_execution_compilation_introspection_or_sampling=True)


def allocator_budget_reference():
    heap = rd(CONTRACT)['heap']
    owners = heap['owner_budgets']
    requested = sum(row['candidate_budget_bytes'] for row in owners[:10])
    reserve = heap['unassigned_requested_reserve_bytes']
    assert requested==heap['requested_owner_budget_bytes']==10938744832
    assert reserve==872415232 and requested+reserve==heap['requested_heap_candidate_bytes']==11811160064
    overhead = owners[10]['candidate_budget_bytes']
    assert overhead==heap['allocator_overhead_candidate_bytes']==1073741824
    assert heap['requested_heap_candidate_bytes']+overhead==heap['committed_heap_candidate_bytes']==12884901888
    assert owners[10]['metric']=='allocator_overhead' and owners[10]['known_partial_upper'] is None
    assert heap['complete_requested_upper_bytes'] is None and heap['complete_committed_upper_bytes'] is None
    assert not heap['all_owner_bounds_verified'] and not heap['capacity_attested']
    return dict(requested_owner_candidate_budget_sum_bytes=requested,
        unassigned_requested_reserve_candidate_bytes=reserve,
        requested_heap_candidate_bytes=11811160064,
        allocator_overhead_candidate_bytes=overhead,committed_heap_candidate_bytes=12884901888,
        nominal_committed_minus_requested_candidate_bytes=1073741824,
        candidate_arithmetic_not_overhead_demand_or_available_capacity_proof=True,
        H11_not_requested_reserve_or_RSS=True,reserve_transfer_applied=False,
        verified_overhead_upper_bytes=None,verified_overhead_fits=None,known_partial_overhead_upper_bytes=None,
        complete_requested_upper_bytes=None,complete_committed_upper_bytes=None,
        independent_peak_subtraction_not_valid_overhead_derivation=True)


def allocator_domain_requirements():
    runtime = rd(RUNTIME)
    native = runtime['native_dependency_allocator_kernel_config_pins']
    assert native['allocator_backend_and_configuration'] is None and not native['correspondence_verified']
    assert native['H11_backend_correspondence_pending']
    assert not runtime['source_binary_build_correspondence']['verified']
    assert not runtime['actual_target_not_just_observed_local_reference']['reference_promoted_to_target']
    requirements = [
        ('D01','Interpreter/object/container allocation domains','Exact target allocator APIs, redirects/build options, geometry, ownership and requested/backing correspondence.'),
        ('D02','Python raw/general backing allocator domains','Exact native backend/configuration and commitment model, including per-thread caches, retention and realloc.'),
        ('D03','Extension/crypto/codec/IO native allocation domains','Complete selected dependency closure, shared/custom allocators and mapping into worker requested/committed account.'),
        ('D04','Per-thread/cross-domain allocator support','All selected worker threads, metadata/caches/heaps and cross-domain transfers without extra per-thread budgets.'),
        ('D05','Commitment/mappings/process boundary','Prove which backing is allocator-owned committed worker heap; distinguish reserved virtual/RSS/stacks/kernel/coordinator/children.'),
    ]
    return dict(exact_backend_and_configuration=None,source_binary_correspondence_verified=False,
        target_attested=False,native_allocator_source_pins={},
        no_backend_geometry_or_allocator_selection_inferred_from_Python_AST=True,
        domains=[dict(id=i,domain_requirement=name,required_correspondence=description,
            selected_implementation=None,source_binary_config_pins={},requested_backing_mapping=None,
            commitment_retention_model=None,verified=False) for i,name,description in requirements],
        all_domains_exhaustively_identified=False,requirements_not_native_inventory_proof=True)


def main():
    o,r,seal = rd(OUT),rd(REVIEW),rd(SEAL)
    c,scope,plan = rd(CONTRACT),rd(SCOPE),rd(PLAN)
    task = next(t for t in plan['tasks'] if t['id']=='P04-H11')
    owner = c['heap']['owner_budgets'][10]
    prior = rd(P+'D5-I158-integrity.json')
    preserved = {**prior['preserved_published268'],**prior['artifacts'],
                 P+'D5-I158-integrity.json':sha(P+'D5-I158-integrity.json')}
    expected = {OUT,REVIEW,AUDIT,SEAL,DESIGN}
    assert len(preserved)==273 and seal['preserved_published273']==preserved
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
    assert o['package_id']==task['id']=='P04-H11' and OUT==task['planned_output']
    assert o['schema']==task['output_schema'] and r['schema']=='d5.i159-p04-h11-preparation-review.v1'
    assert seal['schema']=='d5.i159-integrity.v1'
    assert o['status']=='PREPARED_INSUFFICIENT_ALLOCATOR_OVERHEAD_H11_E02_OPEN_NOT_ADMITTED'
    assert r['status']=='P04_H11_PREPARATION_COMPLETE_NO_COMPLETE_BOUND_NO_ADMISSION'
    assert o['plan_binding']==dict(path=PLAN,sha256=sha(PLAN),package_id=task['id'],task_record_canonical_sha256=digest(task))
    assert o['candidate_binding']==dict(path=CONTRACT,sha256=sha(CONTRACT),contract_id=c['contract_id'],subject=c['subject'],source_revision='I122-CANDIDATE-01')
    assert len(task['required_specific_fields'])==9 and set(task['required_specific_fields'])<=set(o)
    assert o['candidate_owner_record']==owner and owner['id']=='H11' and owner['proof_upper_bytes'] is None
    assert o['candidate_budget_bytes']==o['candidate_budget_bytes=1073741824']==owner['candidate_budget_bytes']==1024**3
    identity = o['owner_id_metric_and_exact_units']
    assert identity['owner_id']=='H11' and identity['owner']==owner['owner']
    assert identity['metric']==owner['metric']=='allocator_overhead'
    assert identity['unit']=='exact_integer_bytes' and identity['candidate_budget_bytes']==1073741824
    assert identity['scope_is_requirement_not_verified_bound']
    assert o['source_evidence']==evidence(o['input_pins'])
    assert o['candidate_budget_arithmetic_reference']==allocator_budget_reference()
    assert o['allocator_domain_correspondence_requirements']==allocator_domain_requirements()
    e = o['source_evidence']
    assert (e['input_pin_count'],e['source_file_count'],len(e['projections']),len(e['source_anchors']))==(204,79,12,24)
    assert len(e['lexical_order_witnesses'])==8 and len(e['allocation_expression_witnesses'])==11
    assert o['metric_and_coverage_requirements']['P01_metric_record']==scope['requested_committed_metrics']
    metric = o['metric_and_coverage_requirements']
    assert metric['coverage_obligation']=='For the same worker state and proved allocator domains: C_worker(t) <= R_worker(t) + O_worker(t).'
    assert metric['safe_peak_upper_rule']=='If the pointwise coverage and both complete bounds are proved, sup C_worker <= sup R_worker + sup O_worker.'
    assert metric['R_actual_distinct_requested_mapping_not_conservative_overcount_subtracted']
    assert metric['independent_peak_or_budget_subtraction_not_overhead_proof']
    assert metric['worker_committed_not_reserved_virtual_RSS_stacks_or_other_process_heap']
    assert not metric['pointwise_coverage_proved'] and not metric['backend_correspondence_proved']
    abi = o['source_ABI_allocator_dependencies']
    assert abi['historical_runtime_reference']==c['runtime'] and not abi['exact_runtime_ABI_or_allocator_correspondence_verified']
    assert all(abi[k] is None for k in ['accepted_target_closure','exact_native_allocator_sources_binaries_build_configuration',
        'requested_backing_and_commitment_domain_mapping','sizeclass_arena_cache_realloc_retention_model',
        'whole_worker_interleaving_and_retained_overhead_theorem'])
    inventory = o['complete_live_allocation_inventory']
    assert not inventory['complete'] and len(inventory['required_classes'])==12
    assert inventory['residual_runtime_native_terms_not_proved_absent']
    for i,row in enumerate(inventory['required_classes'],1):
        assert row['id']=='R%02d'%i and row['required_coverage'] and row['runtime_dependency'] and not row['verified']
        assert all(row[k] is None for k in ['cardinality_upper','size_upper_bytes','maximum_live_upper_bytes','lifetime_derivation'])
    d = o['cardinality_size_lifetime_derivations']
    assert not d['complete'] and d['whole_owner_overhead_upper_bytes'] is None
    assert d['inherited_count_reference']==e['inherited_count_reference']
    assert all(d[k] for k in ['requested_liveness_not_allocator_backing_release',
        'no_fixed_fragmentation_percentage_or_unpinned_geometry_assumed',
        'all_worker_threads_and_selected_native_domains_need_coverage',
        'rejected_growth_and_retained_free_storage_need_full_accounting',
        'H11_not_additional_requested_reserve','no_zero_overhead_or_missing_term_zero'])
    overlap = o['overlap_alias_original_and_rejected_prefix_treatment']
    assert overlap['inherited_scope']==scope['worker_heap_vs_other_process_scope']
    assert overlap['source_applicability']==scope['321_root_12_group_applicability']['I124_applicability']
    assert [x['other_owner'] for x in overlap['boundary_requirements']]==['H%02d'%i for i in range(1,11)]
    assert all(not x['resolved'] for x in overlap['boundary_requirements']) and not overlap['complete_ownership_alias_lifetime_proof']
    dep = o['explicit_assumptions_and_external_dependencies']
    assert not dep['assumptions_verified'] and not dep['P02_exact_runtime_identity_accepted'] and not dep['P03_capacity_service_accepted']
    assert dep['inherited_P01_preconditions']==scope['321_root_12_group_applicability']['original_source_route_preconditions']
    assert all(dep[k] is None for k in ['complete_allocator_domain_overhead_inventory',
        'complete_committed_requested_coverage_and_retention_theorem','independent_runtime_memory_review'])
    b = o['verified_upper_bytes_and_derivation']
    assert b['verified_upper_bytes'] is None and b['complete_derivation'] is None and not b['verified'] and b['unknown_not_zero']
    assert o['bound_fit_not_just_partial_payload']==dict(candidate_budget_bytes=1073741824,
        verified_complete_upper_bytes=None,fit_result='NOT_EVALUABLE_NO_COMPLETE_H11_OVERHEAD_BOUND',fits=None,
        slack_bytes=None,overbudget_proved=False,actual_unboundedness_proved=False,partial_payload_not_accepted=True)
    assert [x['field'] for x in o['field_assessment']]==task['required_specific_fields']
    for row in o['field_assessment']:
        definition = row['field'] in ['owner_id_metric_and_exact_units','candidate_budget_bytes=1073741824']
        assert row['result']==('DOCUMENTARY_DEFINITION_ONLY' if definition else 'INSUFFICIENT_FOR_ACCEPTANCE')
        assert row['basis'] and not row['resource_obligation_closed']
    assert o['acceptance']==dict(rule=task['acceptance'],rejection_rule=task['rejection'],preparation_complete=True,
        accepted_as_complete_H11_proof=False,H11_verified=False,E02_closed=False,resource_obligations_closed=0,no_reserve_transfer=True)
    assert o['dependencies']==rd(H10)['dependencies']
    assert [x['id'] for x in o['dependencies']]==task['depends_on']==['P01','P02']
    provenance = o['producer_and_review_provenance']
    assert provenance['producer_identity']=='Codex assistant preparing I159 in this chat'
    assert provenance['planned_author_role']==task['responsible_role'] and provenance['planned_review_role']==task['review_role']
    assert provenance['independent_reviewer_identity'] is None and not provenance['independent_acceptance'] and not provenance['runtime_custodian_authority_claimed']
    assert not rd(RUNTIME)['acceptance']['accepted_as_runtime_identity'] and not rd(PLATFORM)['acceptance']['accepted_as_platform_evidence']
    assert o['reserve_accounting']==c['reserve_accounting'] and o['non_execution_and_zero_transfer_policy']==scope['non_execution_and_zero_transfer_policy']
    for row,old in zip(o['E02_criterion_disposition'],rd(H10)['E02_criterion_disposition'],strict=True):
        assert row==dict(id=old['id'],inherited_result=old['I157_result'],I159_result=old['I157_result'],closed=False)
    assert r['E02_criterion_disposition']==o['E02_criterion_disposition']
    assert r['input_pins']=={**o['input_pins'],OUT:sha(OUT)}
    assert r['output']==dict(path=OUT,sha256=sha(OUT),schema=o['schema'],evidence_kind=o['evidence_kind'],produced=True)
    assert all(r['preparation_checks'].values())
    assert r['counts']==dict(required_fields=9,documentary_definition_fields=2,insufficient_fields=7,
        required_allocation_classes=12,unknown_inventory_values=48,owner_boundaries=10,allocator_domain_requirement_groups=5,
        source_files=79,source_anchors=24,evidence_projections=12,input_pins=204,lexical_order_witnesses=8,
        allocation_expression_witnesses=11,other_unproduced_packages=6)
    for progress,t in zip(r['package_progress'],plan['tasks'],strict=True):
        exists = t['id'] in ['P01','P02','P03']+['P04-H%02d'%i for i in range(1,12)]
        assert (ROOT/t['planned_output']).exists()==progress['output_created']==exists
        assert progress['package_id']==t['id'] and progress['path']==t['planned_output']
        assert progress['sha256']==(sha(t['planned_output']) if exists else None)
    assert r['independent_review']==dict(accepted=False,reviewer_identity=None,no_independent_review_fabricated=True)
    assert not any(o['external_material_scope'][k] for k in ['global_absence_claimed','external_contacts_made','runtime_or_platform_sampled'])
    negative = {('complete_H11_bound_verified' if k=='complete_H10_bound_verified' else k):v for k,v in rd(H10)['decision'].items()}
    assert o['decision']==r['decision']==negative and o['E06']==r['E06']==rd(H10)['E06']
    assert seal['source_only'] and not any(seal[k] for k in ['H11_verified','independent_acceptance',
        'proposal_enabled','product_or_components_executed','quotas_changed','D5_closed'])
    assert seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    assert r['git_publication']['commit_and_push_all_requested']
    assert set(r['work_unit']['rollback_files'])==expected and r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command']=='python3 docs/validation/D5-I159-audit.py'
    assert r['work_unit']['expected_result']=='PASS_STATIC_SOURCE_ONLY' and r['work_unit']['diff_budget_note']
    for path in [P+'D5-JOINT-capture-authorization.json',P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:
        assert not (ROOT/path).exists()
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I159',package='P04-H11',
        preparation_complete=True,accepted_as_complete_H11_proof=False,candidate_budget_bytes=1073741824,
        metric='allocator_overhead',verified_overhead_upper_bytes=None,insufficient_fields=7,source_files=79,
        source_anchors=24,prior_published_files_preserved=273,new_files=5,product_or_components_executed=0,
        quotas_changed=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,
        IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
