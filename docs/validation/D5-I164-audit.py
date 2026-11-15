#!/usr/bin/env python3
"""I164: self-contained documentary review; JSON/Git/AST only, no target execution."""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'e3efaa2a620e192150b6fb674885e38ccc2785d0'
OUT = P + 'D5-PFC126-03-E03-WORK-GROUPS.json'
REVIEW = P + 'D5-I163-P06-preparation-review.json'
SEAL = P + 'D5-I163-integrity.json'
AUDIT = P + 'D5-I163-audit.py'
DESIGN = 'docs/design/D5-I163-P06-WORK-GROUPS.md'
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
LEDGER = P + 'D5-I129-cost-coverage-ledger.json'
RESOURCE124 = P + 'D5-I124-resource-admission-review.json'
WORKER = 'testing/prospective_capture_joint_i122/worker.py'
PROJECTIONS = [
    (CONTRACT,'/cost_coverage/activities'), (CONTRACT,'/time/normative_markers'),
    (CONTRACT,'/time/ordered_interval_rule'), (CONTRACT,'/time/success_path_qualification'),
    (CONTRACT,'/time/worker_service_partition'), (CONTRACT,'/time/minimum_service_curve'),
    (LEDGER,'/coverage_rule'), (I124,'/kernel_work'), (I124,'/scope'),
    (RESOURCE124,'/collision_work_model'), (RUNTIME,'/acceptance'), (PLATFORM,'/acceptance'),
]
SPECS = [
    (JOINT,'launch'), (WORKER,'main'), (WORKER,'exercise'), (TYPED,'wait_worker'),
    (ATOMIC,'clone_metadata'), (ATOMIC,'build.Recorder._fork'), (ATOMIC,'build.Recorder._atomic'),
    (ATOMIC,'build.Recorder._drain'), (ATOMIC,'build.Recorder._typed_finish'),
    (CAPTURE,'Reader.read'), (CAPTURE,'Reader.finish'), (CAPTURE,'strict_json'),
    (CAPTURE,'digest_value'), (CAPTURE,'stop_owned'), (CAPTURE,'receive_line'),
    (JOINT,'InputPlan.before'), (JOINT,'InputPlan.after'), (JOINT,'InputPlan.finish'),
    (JOINT,'SideWriter.write'), (TYPED,'PageSink.append'),
]
CENSUS = ['Call','List','Tuple','Dict','Set','ListComp','SetComp',
          'DictComp','GeneratorExp','ExceptHandler']
# These bind source order, not observed times, work amounts or success durations.
ORDERS = [
    (JOINT,'launch',"c.write_json_fd(release_write, dict(event='RELEASE', lease=owner.nonce), 4096)",'os.close(release_write)'),
    (JOINT,'launch','os.close(release_write)','wait_worker(process)'),
    (JOINT,'launch','wait_worker(process)','inputs.joint_plan.after()'),
    (JOINT,'launch','packet.finish()','write_all(launchfd, b)'),
    (WORKER,'main',"p.verify_release(c.receive_line(releasefd, p.LIMITS['wait_seconds']), lease)","importlib.import_module(entry['runner_module'])"),
    (WORKER,'main','inputs.joint_plan.finish()',"writer.write(side, p.LIMITS['index_sidecar_bytes'])"),
    (ATOMIC,'build.Recorder._atomic','self._publish(draft)','p.write_all(fd, body)'),
    (ATOMIC,'build.Recorder._typed_finish','self._atomic(lambda draft: draft.events.close(), seal=True)','out = dict('),
]
FACTS = [
    (TYPED,'wait_worker','process.wait(timeout=limit)'), (TYPED,'wait_worker','return True'),
    (TYPED,'wait_worker','return False'), (JOINT,'launch','packet.finish()'),
    (JOINT,'launch','write_all(launchfd, b)'), (JOINT,'launch',"owner.create('context.json')"),
    (ATOMIC,'clone_metadata','memo[key] = out'), (ATOMIC,'build.Recorder._atomic','p.write_all(fd, body)'),
    (ATOMIC,'build.Recorder._drain','self._idle.wait(remaining)'),
    (CAPTURE,'Reader.read',"return b''.join(chunks)"), (WORKER,'exercise','exitcode = entrypoint()'),
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
                    generations_including_initial_upper=1+f+s, not_whole_CPU_WCET_or_phase_service_counts=True),
                candidate_numeric_limits=json.loads(blobs[CONTRACT])['product_numeric_candidates'],
                no_target_import_execution_compilation_introspection_or_sampling=True)


def timing_anchor_evidence():
    c = rd(CONTRACT)
    anchors = c['cost_coverage']['source_anchors']
    assert len(anchors)==20 and anchors==rd(LEDGER)['source_anchors']
    trees = {path:ast.parse((ROOT/path).read_text()) for path in {a['path'] for a in anchors}}
    def check(anchor):
        found = [n for n in ast.walk(trees[anchor['path']]) if hasattr(n,'lineno')
            and (n.lineno,n.col_offset,getattr(n,'end_lineno',None))==(anchor['line'],anchor['column'],anchor['end_line'])
            and hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==anchor['AST_sha256']]
        assert len(found)==1,anchor
        if anchor.get('expression') is not None:
            assert ast.unparse(found[0])==anchor['expression']
        return dict(anchor=anchor,source_sha256=sha(anchor['path']),node_kind=type(found[0]).__name__,verified_source_binding=True)
    costs = [check(a) for a in anchors]
    markers = [dict(id=m['id'],event=m['event'],clock_owner=m['clock_owner'],clock_value=None,
        source_check=check(m['source_anchor']),not_observed_execution_timestamp=True) for m in c['time']['normative_markers']]
    assert [m['id'] for m in markers]==['t0','tR','tW','tF']
    assert markers[2]['source_check']['anchor']['kind']=='CALL_RETURN_EXACT_TRUE'
    return dict(cost_anchor_checks=costs,marker_checks=markers,
        marker_definition_not_execution_or_clock_attestation=True)


GROUP_ANCHORS = [[0],[8],[1,2,3,11],[8,9,12,13,14,18,19],[8,9,12,13,14,18,19],
                 [4,10],[0,5],[0,6],[0,7,15,16,17],[0,9,18,19]]
PROCESS_PHASES = [
    [('COORDINATOR','Tpre')], [('WORKER_ALL_THREADS','Tpre')], [('COORDINATOR','Tpre')],
    [('WORKER_ALL_THREADS','Tpre'),('ORIGINAL_CHILDREN_SOURCE_SCOPE','Tpre')],
    [('WORKER_ALL_THREADS','Tworker'),('ORIGINAL_CHILDREN_SOURCE_SCOPE','Tworker')],
    [('COORDINATOR','Tworker')], [('COORDINATOR','Tpost')], [('COORDINATOR','Tpost')],
    [('COORDINATOR','Tpost')],
    [(p,phase) for p in ['COORDINATOR','WORKER_ALL_THREADS','ORIGINAL_CHILDREN_SOURCE_SCOPE']
     for phase in ['Tpre','Tworker','Tpost']],
]
TERMS = [
    ['registry/authority discovery, canonicalization and hashing','InputPlan bodies and fresh directory/source reads','native/runtime/scheduler startup within coordinator launch'],
    ['interpreter/import/native startup before worker.main and READY','registry/authority/channels and READY construction','pre-release block/dispatch and native service'],
    ['Popen/pipe/channel/native process service','READY receive and validation','RELEASE JSON/newline write and successful parent close'],
    ['all post-receipt imports/targets/suite/observers that may precede parent close','original children and finalization potentially before tR','interval split or justified whole-window conservative overcount'],
    ['all continuing original/child/observer work at or after tR','atomic copying plus noncopy projection/codec/native/GC/destruction','after/finish/source checks and sidecar write before worker exit'],
    ['coordinator wait dispatch/observe/reap/return','physical-exit-to-exact-True-return latency even if worker exited before tR','CPU/wait/scheduler attribution with no uncovered exit gap'],
    ['normal stop_owned cleanup and fresh after/finish checks','source/canonical authority/input comparison','native/file/signal/scheduler contributions after tW'],
    ['packet read/decode/hash/pages/aggregate/finish','evidence Reader and validation CPU separate from input-byte ledger','native parser, allocation, destruction and IO delays'],
    ['success finally fd closes and owner verify','context encode/package listing/size checks','context/launch create/write/close through final normal return'],
    ['transitive original/native/codec/hash/sort work in every relevant process/window','allocation/GC/destruction and callbacks/locks','cross-cutting attribution inside phases, not omitted noncopy0 or a free tail'],
]


def work_fields():
    c = rd(CONTRACT)
    activities = c['cost_coverage']['activities']
    assert len(activities)==10 and [a['id'] for a in activities]==['C%02d'%i for i in range(1,11)]
    assert [a['id'] for a in rd(LEDGER)['activities']]==[a['id'] for a in activities]
    groups,vectors = [],[]
    for i,activity in enumerate(activities):
        assert all(activity[k] is None for k in ['verified_work_upper','verified_CPU_seconds_upper','verified_wall_seconds_upper'])
        groups.append(dict(id=activity['id'],candidate_requirement_record=activity,
            record_canonical_sha256=digest(activity),source_anchor_indices=GROUP_ANCHORS[i],required_cost_terms=TERMS[i],
            complete_transitive_cost_inventory=False,verified_work_upper=None,compatible_work_unit=None,
            justified_WCET_upper_seconds=None,verified=False))
        for process,phase in PROCESS_PHASES[i]:
            vectors.append(dict(id=activity['id']+':'+process+':'+phase,group_id=activity['id'],process_set_id=process,phase=phase,
                complete_work_upper=None,work_unit=None,static_WCET_upper_seconds=None,wait_upper_seconds=None,
                scheduler_observation_upper_seconds=None,complete_derivation=None,verified=False,
                required_categories=['CPU','IO_or_child_wait','scheduler_blocking_observation'],
                required_unit_rule='Pin exact process/runtime and compatible primitive-work/cycle/service units or justified exact-platform WCET seconds; no instruction/byte/clone-to-seconds shortcut.',
                actual_interval_split_not_proved=True,conservative_overcount_requires_complete_bound=True))
    assert len(vectors)==20
    proof = rd(I124)
    assert (proof['global_F_upper'],proof['global_S_upper'],proof['global_clone_batches_upper'])==(52018,1759,53777)
    return dict(
        all10_cost_group_inventory_and_source_anchors=dict(groups=groups,source_anchor_checks=timing_anchor_evidence()['cost_anchor_checks'],
            contract_cost_record_sha256=digest(c['cost_coverage']),complete_inventory=False,native_transitive_closure_verified=False),
        per_process_phase_work_vectors_and_units=dict(process_sets=[
            dict(id='COORDINATOR',scope='launch invocation t0..normal return tF',actual_identity_pin=None),
            dict(id='WORKER_ALL_THREADS',scope='selected worker including pre-main startup, all threads and pre-tR work',actual_identity_pin=None),
            dict(id='ORIGINAL_CHILDREN_SOURCE_SCOPE',scope='all relevant original children under P01 source routes, no instrumentation or per-child budget',actual_identity_pin=None)],
            vectors=vectors,complete_process_enumeration=False,compatible_service_unit_selected=None,
            whole_work_upper=None,whole_CPU_seconds_upper=None,whole_wall_seconds_upper=None,
            CPU_sum_not_wall_duration=True,no_parallel_overlap_subtraction=True,C10_is_cross_cutting_not_free_tail=True),
        transitive_original_native_codec_GC_destruction_costs=dict(required_terms=[
            'original suite/callback/import work and children across scoped routes',
            'native extensions/crypto/codecs/IO/syscalls and process/lock services',
            'projection/hash/sort/allocation, GC/destruction/finalizers and error-held references'],
            process_phase_coverage_required='All relevant contributors inside coordinator windows or justified additive overcount.',
            native_runtime_closure_verified=False,complete_original_work_bound=None,complete_native_codec_work_bound=None,
            complete_GC_destruction_work_bound=None,work_unit=None,compatible_WCET_or_service_conversion=None,
            heap_payload_or_file_bytes_not_CPU_work=True),
        worker_pre_READY_and_post_receipt_before_tR_coverage=dict(markers=timing_anchor_evidence()['marker_checks'],
            interval_rule=c['time']['ordered_interval_rule'],pre_tR_worker_rule=c['cost_coverage']['pre_tR_worker_rule'],
            affected_groups=['C02','C04','C05','C10'],worker_pre_main_startup_not_omitted=True,
            all_post_receipt_work_assigned_only_Tworker=False,actual_split_bound=None,conservative_overcount_bound=None,
            tR_parent_close_not_child_receipt=True,qualified_marker_values_observed=False),
        wait_return_observation_and_success_finally_coverage=dict(success_path_qualification=c['time']['success_path_qualification'],
            observation_latency_rule=c['time']['observation_latency_rule'],finally_rule=c['cost_coverage']['finally_rule'],
            affected_groups=['C06','C07','C08','C09','C10'],tW_exact_True_return_not_physical_exit=True,
            wait_True_not_capture_success=True,later_qualification_does_not_move_tW=True,
            packet_finish_not_tF=True,success_finally_closes_writes_through_normal_return_required=True,
            wait_observation_delay_upper_seconds=None,success_finally_work_upper=None,
            success_finally_wall_upper_seconds=None,verified=False),
        retries_signals_assumptions_and_liveness_requirements=dict(required_assumptions=[
            'selected admissible success paths, original source routes and bounded retry/signal behavior',
            'pipe/file/child completion, lock/scheduler/load/interference and wait-return service under attested process domain',
            'normal success finalization/cleanup progress; failure cleanup not automatically within900 seconds'],
            retry_count_upper=None,signal_interference_policy=None,IO_child_completion_upper_seconds=None,
            lock_scheduler_observation_delay_upper_seconds=None,complete_liveness_theorem=None,
            assumptions_verified=False,watchdog_is_failure_limit_not_success_duration_proof=True,
            timeouts_or_cleanup_not_replacements_for_qualified_tW=True),
        noncopy_and_runtime_cost_not_zero=dict(noncopy_rule=c['cost_coverage']['noncopy_rule'],CPU_wall_rule=c['cost_coverage']['CPU_wall_rule'],
            attribution_rule=c['cost_coverage']['attribution_rule'],input_byte_rule=c['cost_coverage']['input_byte_rule'],
            missing_costs_rejected_not_zero=True,complete_noncopy_upper=None,native_GC_destruction_not_zero=True,
            CPU_wait_scheduler_unknown_not_paid_by_candidate_budgets=True,
            no_additional_per_group_process_thread_or_category_reserve=True,not_measurement_or_verified_service=True),
        I124_count_transfer_or_refinement=dict(proof=dict(path=I124,sha256=sha(I124)),scope=proof['scope'],
            F_upper=52018,S_upper=1759,clone_batches_upper=53777,generations_including_initial_upper=53778,
            root_count=proof['root_count'],event_associated_F_upper=proof['event_associated_F_upper'],
            binding_slots_upper=proof['binding_slots_upper'],subtest_callbacks_upper=proof['subtest_callbacks_upper'],
            process_opportunities_upper=proof['process_opportunities_upper'],
            process_opportunities_not_actual_process_enumeration_or_service=True,
            kernel_work=proof['kernel_work'],lifetime_envelope=proof['lifetime_envelope'],
            collision_work_model=rd(RESOURCE124)['collision_work_model'],CPU_admission=rd(RESOURCE124)['CPU_admission'],
            status='CONDITIONAL_KERNEL_OPPORTUNITY_TRANSFER_NOT_TOTAL_CPU_OR_WCET',refinement_applied=False,
            abstract_units_not_instructions_or_seconds=True,not_all_noncopy_or_prepost_phase_work=True,
            no_division_by900_as_service_rate_or_actual_infeasibility=True,
            no_33_generation_or_immediate_GC_replacement=True))


def validate_preparation():
    o,r,seal = rd(OUT),rd(REVIEW),rd(SEAL)
    c,plan = rd(CONTRACT),rd(PLAN)
    task = next(t for t in plan['tasks'] if t['id']=='P06')
    prior = rd(P+'D5-I162-integrity.json')
    preserved = {**prior['preserved_published288'],**prior['artifacts'],P+'D5-I162-integrity.json':sha(P+'D5-I162-integrity.json')}
    expected = {OUT,REVIEW,AUDIT,SEAL,DESIGN}
    assert len(preserved)==293 and seal['preserved_published293']==preserved
    assert set(seal['artifacts'])|{SEAL}==expected
    for pins in [preserved,seal['artifacts'],o['input_pins'],r['input_pins'],rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for path,h in pins.items():
            assert sha(path)==h,path
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    assert o['base_commit']==r['base_commit']==seal['base_commit']==BASE
    assert o['date']==r['date']==seal['date']=='2026-11-15'
    assert o['schema']==task['output_schema'] and OUT==task['planned_output'] and o['package_id']=='P06'
    assert r['schema']=='d5.i163-p06-preparation-review.v1' and seal['schema']=='d5.i163-integrity.v1'
    assert o['status']=='PREPARED_INSUFFICIENT_WORK_GROUPS_E03_OPEN_NOT_ADMITTED'
    assert r['status']=='P06_PREPARATION_COMPLETE_WHOLE_WORK_AND_WCET_UNPROVED_NO_ADMISSION'
    assert o['plan_binding']==dict(path=PLAN,sha256=sha(PLAN),package_id='P06',task_record_canonical_sha256=digest(task))
    assert o['candidate_binding']==dict(path=CONTRACT,sha256=sha(CONTRACT),contract_id=c['contract_id'],subject=c['subject'],source_revision='I122-CANDIDATE-01')
    assert len(o['input_pins'])==220 and o['source_evidence']==evidence(o['input_pins'])
    assert o['source_evidence']['source_file_count']==79 and len(o['source_evidence']['source_anchors'])==20
    fields = work_fields()
    assert set(fields)==set(task['required_specific_fields']) and len(fields)==8
    for key,value in fields.items():
        assert o[key]==value,key
    assert o['timing_anchor_evidence']==timing_anchor_evidence()
    assert [row['field'] for row in o['field_assessment']]==task['required_specific_fields']
    documentary = {'all10_cost_group_inventory_and_source_anchors','noncopy_and_runtime_cost_not_zero','I124_count_transfer_or_refinement'}
    for row in o['field_assessment']:
        assert row['result']==('DOCUMENTARY_REQUIREMENT_OR_PARTIAL_TRANSFER_ONLY' if row['field'] in documentary else 'INSUFFICIENT_FOR_ACCEPTANCE')
        assert row['basis'] and not row['resource_obligation_closed']
    assert o['acceptance']==dict(rule=task['acceptance'],rejection_rule=task['rejection'],preparation_complete=True,
        accepted_as_complete_work_or_WCET_proof=False,all10_groups_bounded=False,compatible_units_verified=False,
        phase_work_and_delay_coverage_verified=False,E03_closed=False,resource_obligations_closed=0)
    assert [d['id'] for d in o['dependencies']]==task['depends_on']==['P01','P02','P03']
    for dep in o['dependencies']:
        assert dep['sha256']==sha(dep['path']) and not dep['accepted_for_resource_closure']
    assert not rd(RUNTIME)['acceptance']['accepted_as_runtime_identity'] and not rd(PLATFORM)['acceptance']['accepted_as_platform_evidence']
    assert o['reserve_accounting']==c['reserve_accounting'] and o['non_execution_and_zero_transfer_policy']==rd(SCOPE)['non_execution_and_zero_transfer_policy']
    criteria = next(x for x in rd(P+'D5-I131-E01-E05-review.json')['obligations'] if x['id']=='E03')['criteria']
    assert o['E03_criterion_disposition']==r['E03_criterion_disposition']==[dict(id=x['id'],inherited_result=x['result'],I163_result=x['result'],closed=False) for x in criteria]
    assert o['unchanged_time_candidate_reference']==dict(time=c['time'],cost_coverage_rules={k:v for k,v in c['cost_coverage'].items() if k not in ['source_anchors','activities']},
        budgets_not_verified_service_or_duration=True,work_to_service_route_unselected=True,P07_P08_not_started=True)
    provenance = o['producer_and_review_provenance']
    assert provenance['producer_identity']=='Codex assistant preparing I163 in this chat'
    assert provenance['planned_author_role']==task['responsible_role'] and provenance['planned_review_role']==task['review_role']
    assert provenance['independent_reviewer_identity'] is None and not provenance['independent_acceptance'] and not provenance['runtime_custodian_authority_claimed']
    assert r['input_pins']=={**o['input_pins'],OUT:sha(OUT)}
    assert r['output']==dict(path=OUT,sha256=sha(OUT),schema=o['schema'],evidence_kind=o['evidence_kind'],produced=True)
    assert all(r['preparation_checks'].values())
    assert r['counts']==dict(required_fields=8,documentary_requirement_or_partial_transfer_fields=3,insufficient_fields=5,
        cost_groups=10,unproved_group_work_CPU_wall_values=30,process_sets=3,process_phase_vectors=20,
        null_vector_work_unit_WCET_wait_scheduler_derivation_values=120,coordinator_markers=4,
        adopted_cost_source_anchors=20,source_files=79,selected_source_anchors=20,input_pins=220,other_unproduced_packages=4)
    for progress,t in zip(r['package_progress'],plan['tasks'],strict=True):
        exists = t['id'] in ['P01','P02','P03','P05','P06']+['P04-H%02d'%i for i in range(1,12)]
        assert (ROOT/t['planned_output']).exists()==progress['output_created']==exists
        assert progress['package_id']==t['id'] and progress['path']==t['planned_output'] and progress['sha256']==(sha(t['planned_output']) if exists else None)
    old = rd(P+'D5-PFC126-03-E02-HEAP-ROLLUP.json')
    negative = {('complete_work_groups_verified' if k=='complete_heap_rollup_verified' else k):v for k,v in old['decision'].items()}
    assert o['decision']==r['decision']==negative and o['E06']==r['E06']==old['E06']
    assert r['independent_review']==dict(accepted=False,reviewer_identity=None,no_independent_review_fabricated=True)
    assert not any(o['external_material_scope'][k] for k in ['global_absence_claimed','external_contacts_made','runtime_or_platform_sampled'])
    assert seal['source_only'] and not any(seal[k] for k in ['work_groups_verified','independent_acceptance','product_or_components_executed','quotas_changed','proposal_enabled','D5_closed'])
    assert seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    assert r['git_publication']['commit_and_push_all_requested']
    assert set(r['work_unit']['rollback_files'])==expected and r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command']=='python3 docs/validation/D5-I163-audit.py' and r['work_unit']['expected_result']=='PASS_STATIC_SOURCE_ONLY'
    for path in [P+'D5-JOINT-capture-authorization.json',P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:
        assert not (ROOT/path).exists()


REVIEW_BASE = 'cd7c55435465ed86cc0b2ceccdd45d6af14e966c'
NEW_REVIEW = P+'D5-I164-P06-documentary-review.json'
RECON = P+'D5-I164-P06-source-reconstruction.json'
NEW_AUDIT = P+'D5-I164-audit.py'
NEW_SEAL = P+'D5-I164-integrity.json'
NEW_DESIGN = 'docs/design/D5-I164-P06-WORK-GROUPS-REVIEW.md'
NEW_FILES = {NEW_REVIEW,RECON,NEW_AUDIT,NEW_SEAL,NEW_DESIGN}


def published(path, revision=REVIEW_BASE):
    data = subprocess.check_output(['git','show',revision+':'+path],cwd=ROOT)
    assert data==(ROOT/path).read_bytes(), path
    return data


def reconstruct():
    # Read the published package afresh, not the producer's calculated fields.
    o=json.loads(published(OUT))
    pins={**o['input_pins'],**{p:sha(p) for p in [OUT,REVIEW,AUDIT,SEAL]}}
    for path,h in pins.items():
        assert hashlib.sha256(published(path)).hexdigest()==h,path
    c=json.loads(published(CONTRACT))
    source_checks=[]
    for path,h in sorted(o['source_evidence']['source_pins'].items()):
        tree=ast.parse(published(path).decode())
        source_checks.append(dict(path=path,sha256=h,syntax_parsed=True,
            lexical_function_count=sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) for n in ast.walk(tree))))
    # Separate locator: index every AST location, then select by dump digest.
    trees={p:ast.parse(published(p).decode()) for p in {a['path'] for a in c['cost_coverage']['source_anchors']}}
    indices={}
    for path,tree in trees.items():
        index={}
        for n in ast.walk(tree):
            if hasattr(n,'lineno'):
                index.setdefault((n.lineno,n.col_offset,n.end_lineno),[]).append(n)
        indices[path]=index
    def locate(a):
        candidates=indices[a['path']][(a['line'],a['column'],a['end_line'])]
        selected=[n for n in candidates if hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==a['AST_sha256']]
        assert len(selected)==1
        n=selected[0]
        if a.get('expression') is not None:assert ast.unparse(n)==a['expression']
        return dict(path=a['path'],line=n.lineno,column=n.col_offset,end_line=n.end_lineno,
            node_kind=type(n).__name__,AST_sha256=a['AST_sha256'],source_sha256=sha(a['path']))
    anchors=[locate(a) for a in c['cost_coverage']['source_anchors']]
    markers=[dict(id=m['id'],source_binding=locate(m['source_anchor']),clock_value=None,
        execution_or_clock_attested=False) for m in c['time']['normative_markers']]
    launch=next(n for n in trees[JOINT].body if isinstance(n,ast.FunctionDef) and n.name=='launch')
    wait=next(n for n in trees[TYPED].body if isinstance(n,ast.FunctionDef) and n.name=='wait_worker')
    worker=next(n for n in trees[WORKER].body if isinstance(n,ast.FunctionDef) and n.name=='main')
    def calls(node,expr):
        return [n for n in ast.walk(node) if isinstance(n,ast.Call) and ast.unparse(n)==expr]
    assert len(calls(launch,'wait_worker(process)'))==1
    wait_try=next(n for n in wait.body if isinstance(n,ast.Try))
    assert isinstance(wait_try.body[-1],ast.Return) and wait_try.body[-1].value.value is True
    assert any(isinstance(n,ast.Return) and isinstance(n.value,ast.Constant) and n.value.value is False for h in wait_try.handlers for n in ast.walk(h))
    assert isinstance(launch.body[-1],ast.Return) and ast.unparse(launch.body[-1])=='return context'
    outer=next(n for n in launch.body if isinstance(n,ast.Try) and n.finalbody and calls(n,'wait_worker(process)'))
    final=ast.Module(body=outer.finalbody,type_ignores=[])
    assert calls(final,'write_all(launchfd, b)') and calls(final,"owner.create('context.json')") and calls(final,'os.close(launchfd)')
    assert calls(launch,'packet.finish()')[0].lineno < min(n.lineno for n in outer.finalbody)
    release=calls(launch,'os.close(release_write)')[0]
    assert release.lineno < calls(launch,'wait_worker(process)')[0].lineno
    assert calls(worker,"p.verify_release(c.receive_line(releasefd, p.LIMITS['wait_seconds']), lease)")[0].lineno < calls(worker,"importlib.import_module(entry['runner_module'])")[0].lineno
    group_rows=[]
    for i,a in enumerate(c['cost_coverage']['activities']):
        assert a['id']=='C%02d'%(i+1)
        missing={k:a[k] for k in ['verified_work_upper','verified_CPU_seconds_upper','verified_wall_seconds_upper']}
        assert all(v is None for v in missing.values())
        group_rows.append(dict(id=a['id'],requirement_record_sha256=digest(a),unproved_values=missing))
    expected_pairs={
        'C01':[('COORDINATOR','Tpre')], 'C02':[('WORKER_ALL_THREADS','Tpre')],
        'C03':[('COORDINATOR','Tpre')],
        'C04':[(x,'Tpre') for x in ['WORKER_ALL_THREADS','ORIGINAL_CHILDREN_SOURCE_SCOPE']],
        'C05':[(x,'Tworker') for x in ['WORKER_ALL_THREADS','ORIGINAL_CHILDREN_SOURCE_SCOPE']],
        'C06':[('COORDINATOR','Tworker')],
        **{'C%02d'%i:[('COORDINATOR','Tpost')] for i in [7,8,9]},
        'C10':[(p,t) for p in ['COORDINATOR','WORKER_ALL_THREADS','ORIGINAL_CHILDREN_SOURCE_SCOPE'] for t in ['Tpre','Tworker','Tpost']]}
    vfield=o['per_process_phase_work_vectors_and_units']
    actual=[(v['group_id'],v['process_set_id'],v['phase']) for v in vfield['vectors']]
    expected=[(g,p,t) for g,pts in expected_pairs.items() for p,t in pts]
    assert actual==expected and len(actual)==len(set(actual))==20
    nulls=['complete_work_upper','work_unit','static_WCET_upper_seconds','wait_upper_seconds','scheduler_observation_upper_seconds','complete_derivation']
    vector_rows=[]
    for v in vfield['vectors']:
        assert all(v[k] is None for k in nulls) and not v['verified']
        vector_rows.append(dict(id=v['id'],group=v['group_id'],process=v['process_set_id'],phase=v['phase'],unproved_fields={k:v[k] for k in nulls}))
    proof=json.loads(published(I124))
    counts={k:proof[k] for k in ['global_F_upper','global_S_upper','global_clone_batches_upper','root_count','process_opportunities_upper']}
    assert list(counts.values())==[52018,1759,53777,321,718]
    fields=o['field_assessment']
    assert len(fields)==8 and sum(x['result']=='INSUFFICIENT_FOR_ACCEPTANCE' for x in fields)==5
    return dict(schema='d5.i164-p06-source-reconstruction.v1',increment='I164',date='2026-11-15',base_commit=REVIEW_BASE,
        method='Fresh Git blob reads, separate AST location index and explicit group/process/phase Cartesian reconstruction; source syntax only.',
        actor_independent=False,organizationally_independent=False,input_pins=pins,
        source_file_count=len(source_checks),source_checks=source_checks,cost_anchor_bindings=anchors,marker_bindings=markers,
        structural_checks=dict(unique_wait_call=True,wait_normal_return_exact_True=True,timeout_return_False=True,
            parent_RELEASE_close_before_wait_lexically=True,worker_receipt_before_import_lexically=True,
            packet_finish_before_success_finally=True,finally_context_and_launch_writes_closes_present=True,normal_return_after_finally=True,
            lexical_structure_not_WCET_or_observed_schedule=True),
        groups=group_rows,vectors=vector_rows,counts=dict(cost_groups=10,process_sets=3,process_phase_vectors=20,
            missing_group_work_CPU_wall_values=30,missing_selected_vector_values=120,markers=4,adopted_anchors=20,source_files=79,input_pins=224),
        conditional_I124_counts=counts,kernel_work=proof['kernel_work'],
        transfer_not_complete_transitive_work_or_CPU_seconds=True,field_dispositions=fields,
        complete_process_enumeration=False,compatible_work_unit=None,whole_CPU_seconds_upper=None,whole_wall_seconds_upper=None,
        execution_count=0,resource_obligations_closed=0)


CHECKS = [
    ('R01','Plan/schema/dependencies/8 fields and exact candidate bytes','PASS_DOCUMENTARY_CONFORMANCE'),
    ('R02','Ten requirement groups bound to twenty adopted source anchors','PASS_REQUIREMENT_BINDING_ONLY'),
    ('R03','Three process sets and twenty required process/phase vectors','PASS_REQUIREMENT_VECTOR_ONLY'),
    ('R04','C02 covers pre-main startup; C04 covers worker/children before parent tR','PASS_REQUIREMENT_ONLY'),
    ('R05','tW unique wait exact True; physical exit and later eligibility do not replace it','PASS_SOURCE_DEFINITION_ONLY'),
    ('R06','C09 success finally through normal launch return; packet.finish is not tF','PASS_SOURCE_DEFINITION_ONLY'),
    ('R07','Original/native/codec/GC/destruction transitive closure','INSUFFICIENT_FOR_ACCEPTANCE'),
    ('R08','Complete compatible work/WCET and process-domain/unit correspondence','INSUFFICIENT_FOR_ACCEPTANCE'),
    ('R09','Retries/signals/IO/children/locks/scheduler/observation and liveness','INSUFFICIENT_FOR_ACCEPTANCE'),
    ('R10','I124 conditional count transfer without byte/clone-to-seconds conversion','PASS_PARTIAL_TRANSFER_ONLY'),
    ('R11','No overlap subtraction, noncopy zero or reserve multiplication','PASS_DOCUMENTARY_RULE_ONLY'),
    ('R12','900 watchdog and candidate budgets not successful-duration evidence','PASS_DOCUMENTARY_RULE_ONLY'),
    ('R13','P02/P03/P05 insufficiency retained; P07-P10 not produced','PASS_DEPENDENCY_STATE_ONLY'),
    ('R14','No independent actor/custodian/resource acceptance fabricated','PASS_PROVENANCE_DISCLOSURE'),
    ('R15','Prior bytes/no admission/no execution/no quota or source changes','PASS_PRESERVATION_ONLY')]


def review_record(rec):
    o=rd(OUT)
    task=next(t for t in rd(PLAN)['tasks'] if t['id']=='P06')
    return dict(schema='d5.i164-p06-documentary-review.v1',increment='I164',date='2026-11-15',base_commit=REVIEW_BASE,
        package_id='P06',status='DOCUMENTARY_CONFORMANT_COMPLETE_WORK_WCET_UNPROVED_NOT_ADMITTED',
        subject=o['candidate_binding'],plan_task_sha256=digest(task),
        input_pins={**rec['input_pins'],RECON:sha(RECON)},
        reconstruction=dict(path=RECON,sha256=sha(RECON)),
        review_provenance=dict(reviewer='Codex assistant in same chat; also prepared I163',
            methodological_reconstruction_separate=True,actor_independent=False,organizationally_independent=False,
            planned_review_role=task['review_role'],independent_reviewer_identity=None,independent_acceptance=False,
            runtime_or_platform_custodian_acceptance=False),
        checks=[dict(id=i,scope=s,result=r,resource_obligation_closed=False) for i,s,r in CHECKS],
        findings=dict(blocking_documentary_defects=[],resource_acceptance_gaps=[
            'Complete original/native/runtime/codec/GC/destruction and process closure absent.',
            'Compatible work/unit/service route or exact-platform WCET unproved; all20 vector bounds remain null.',
            'IO/child/scheduler/observation, retry/signal assumptions and liveness unproved.',
            'P02 exact runtime and P03 platform/service not accepted; P05 heap remains unproved.',
            'Independent reviewer and competent custodian acceptance absent.']),
        counts=rec['counts'],field_dispositions=o['field_assessment'],
        E03_criterion_disposition=[dict(id=x['id'],inherited_result=x['I163_result'],I164_result=x['I163_result'],closed=False) for x in o['E03_criterion_disposition']],
        acceptance=dict(documentary_conformance=True,accepted_as_complete_work_or_WCET_proof=False,
            independent_acceptance=False,E03_closed=False,resource_obligations_closed=0),
        decision=o['decision'],E06=o['E06'],
        next_evidence_required='Supply reviewable full transitive work and compatible units/service or justified exact-runtime/platform WCET, delays/liveness and independent/custodian acceptance under I132; no execution authorized.',
        work_unit=dict(files=sorted(NEW_FILES),rollback_files=sorted(NEW_FILES),
            verification_command='python3 docs/validation/D5-I164-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: documentary JSON/Git/AST review only; target execution forbidden.',
            over400_lines=True,overage_reason='Self-contained historical validator, fresh reconstruction and pinned review evidence; no evidence removed to fit a line cap.'),
        git_publication=dict(commit_and_push_all_requested=True,publication_does_not_admit_candidate=True))


def main():
    validate_preparation()
    rec=reconstruct()
    assert rd(RECON)==rec
    assert rd(NEW_REVIEW)==review_record(rec)
    prior=rd(SEAL)
    preserved={**prior['preserved_published293'],**prior['artifacts'],SEAL:sha(SEAL)}
    seal=rd(NEW_SEAL)
    assert len(preserved)==298 and seal['preserved_published298']==preserved
    assert seal['schema']=='d5.i164-integrity.v1' and seal['base_commit']==REVIEW_BASE and seal['date']=='2026-11-15'
    assert set(seal['artifacts'])==NEW_FILES-{NEW_SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,h in pins.items():assert sha(path)==h,path
    assert seal['source_only'] and seal['IR03']=='NOT_READY' and seal['resource_obligations_closed']==0
    for k in ['work_groups_verified','independent_acceptance','product_or_components_executed','quotas_changed','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',REVIEW_BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==NEW_FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',REVIEW_BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=REVIEW_BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I164',package='P06',
        documentary_conformance=True,accepted_as_complete_work_or_WCET_proof=False,
        cost_groups=10,process_phase_vectors=20,missing_group_values=30,missing_selected_vector_values=120,
        prior_published_files_preserved=298,new_files=5,product_or_components_executed=0,quotas_changed=False,
        resource_obligations_closed=0,independent_acceptance=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',
        git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
