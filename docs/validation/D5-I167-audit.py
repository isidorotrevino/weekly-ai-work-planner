#!/usr/bin/env python3
"""I167 documentary Git/JSON/AST audit; no target execution, import or compilation."""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'b7ec299a4ae9be0d7b18fd6b1418e6bc8d5593fa'
OUT = P+'D5-PFC126-03-E05-PHASE-BOUNDS.json'
REVIEW = P+'D5-I167-P08-preparation-review.json'
AUDIT = P+'D5-I167-audit.py'
SEAL = P+'D5-I167-integrity.json'
DESIGN = 'docs/design/D5-I167-P08-PHASE-BOUNDS.md'
PLAN = P+'D5-I132-E01-E05-evidence-plan.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
SCOPE = P+'D5-PFC126-03-RESOURCE-SCOPE.json'
RUNTIME = P+'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
PLATFORM = P+'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
HEAP = P+'D5-PFC126-03-E02-HEAP-ROLLUP.json'
WORK = P+'D5-PFC126-03-E03-WORK-GROUPS.json'
COMPAT = P+'D5-PFC126-03-E03-E04-COMPATIBILITY.json'
OLD_SEAL = P+'D5-I166-integrity.json'
JOINT = 'testing/prospective_capture_joint_i122/capture.py'
TYPED = 'testing/prospective_capture_typed/capture.py'
WORKER = 'testing/prospective_capture_joint_i122/worker.py'
FILES = {OUT,REVIEW,AUDIT,SEAL,DESIGN}


def rd(path):
    return json.loads((ROOT/path).read_text())


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,allow_nan=False,
        sort_keys=True,separators=(',',':')).encode()).hexdigest()


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def pin(path):
    return dict(path=path,sha256=sha(path))


def inputs():
    extras=[COMPAT,P+'D5-I165-P07-preparation-review.json',P+'D5-I165-integrity.json',P+'D5-I165-audit.py',
        P+'D5-I166-P07-documentary-review.json',P+'D5-I166-P07-source-reconstruction.json',OLD_SEAL,P+'D5-I166-audit.py']
    return {**rd(COMPAT)['input_pins'],**{p:sha(p) for p in extras}}


def published_inputs():
    pins=inputs()
    request=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=request))
    for path,h in sorted(pins.items()):
        header=stream.readline().decode().split()
        assert len(header)==3 and header[1]=='blob',path
        body=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(path),path


def source_evidence():
    c=rd(CONTRACT);sources=rd(WORK)['source_evidence']['source_pins']
    trees={p:ast.parse((ROOT/p).read_text()) for p in sources}
    assert len(trees)==79 and all(sha(p)==h for p,h in sources.items())
    def bind(a):
        found=[n for n in ast.walk(trees[a['path']]) if hasattr(n,'lineno')
            and (n.lineno,n.col_offset,n.end_lineno)==(a['line'],a['column'],a['end_line'])
            and hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==a['AST_sha256']]
        assert len(found)==1,a
        if a.get('expression') is not None:assert ast.unparse(found[0])==a['expression']
        return dict(anchor=a,source_sha256=sha(a['path']),node_kind=type(found[0]).__name__,source_binding_verified=True)
    def symbol(path,name):
        return next(n for n in trees[path].body if isinstance(n,ast.FunctionDef) and n.name==name)
    def calls(node,expression):
        return [n for n in ast.walk(node) if isinstance(n,ast.Call) and ast.unparse(n)==expression]
    def location(node):
        return dict(kind=type(node).__name__,line=node.lineno,column=node.col_offset,end_line=node.end_lineno,
            AST_sha256=hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest())
    launch,wait,worker=symbol(JOINT,'launch'),symbol(TYPED,'wait_worker'),symbol(WORKER,'main')
    assert len(calls(launch,'wait_worker(process)'))==1
    wait_try=next(n for n in wait.body if isinstance(n,ast.Try))
    assert ast.unparse(wait_try.body[-1])=='return True'
    assert any(isinstance(n,ast.Return) and ast.unparse(n)=='return False' for h in wait_try.handlers for n in ast.walk(h))
    outer=next(n for n in launch.body if isinstance(n,ast.Try) and calls(n,'wait_worker(process)'))
    final=ast.Module(body=outer.finalbody,type_ignores=[])
    assert calls(final,"owner.create('context.json')") and calls(final,'write_all(launchfd, b)') and calls(final,'os.close(launchfd)')
    assert ast.unparse(launch.body[-1])=='return context'
    assert calls(launch,'packet.finish()')[0].lineno < min(n.lineno for n in outer.finalbody)
    order_specs=[(launch,"c.write_json_fd(release_write, dict(event='RELEASE', lease=owner.nonce), 4096)",'write_all(release_write, b\'\\n\')'),
        (launch,"write_all(release_write, b'\\n')",'os.close(release_write)'),
        (launch,'os.close(release_write)','wait_worker(process)'),
        (launch,'wait_worker(process)','inputs.joint_plan.after()'),
        (worker,"p.verify_release(c.receive_line(releasefd, p.LIMITS['wait_seconds']), lease)","importlib.import_module(entry['runner_module'])")]
    orders=[]
    for node,before,after in order_specs:
        a,b=calls(node,before),calls(node,after)
        assert len(a)==len(b)==1,(before,after)
        assert (a[0].lineno,a[0].col_offset)<(b[0].lineno,b[0].col_offset)
        orders.append(dict(before_expression=before,after_expression=after,before=location(a[0]),after=location(b[0]),lexical_order_only=True))
    return dict(source_pins=sources,source_file_count=79,
        cost_anchor_checks=[bind(a) for a in c['cost_coverage']['source_anchors']],
        marker_checks=[dict(id=m['id'],event=m['event'],clock_owner=m['clock_owner'],clock_value=None,
            source_check=bind(m['source_anchor'])) for m in c['time']['normative_markers']],
        lexical_order_witnesses=orders,
        success_finally_context_launch_writes_closes_and_normal_return_present=True,
        exact_True_and_timeout_False_source_returns_present=True,
        source_definitions_not_execution_clock_service_or_WCET_attestation=True)


def phase_fields():
    c,s,r,p,h,w,k=[rd(x) for x in [CONTRACT,SCOPE,RUNTIME,PLATFORM,HEAP,WORK,COMPAT]]
    vectors=w['per_process_phase_work_vectors_and_units']['vectors']
    joins=k['exact_runtime_platform_process_unit_match']['joins']
    phases=[]
    for row in c['time']['phase_budgets']:
        phase=row['id']
        phases.append(dict(id=phase,candidate_wall_seconds=row['candidate_wall_seconds'],verified_upper_seconds=None,
            complete_work_CPU_wait_scheduler_coverage=False,derivation=None,
            required_P06_vectors=[v['id'] for v in vectors if v['phase']==phase],
            required_P07_joins=[v['id'] for v in joins if v['phase']==phase],
            compatibility_accepted=False,unit_clock_process_domain_accepted=False,
            delay_bounds_verified=False,liveness_assumptions_satisfied=False))
    premises=[
        ('A01','Accepted exact scope/runtime/platform/process/monotonic clock identity','P01/P02/P03'),
        ('A02','Complete heap and capacity covering success and bounded observer-rejection prefixes','P05'),
        ('A03','Whole-window work/native/GC/destruction and compatible service or exact-platform WCET','P06/P07'),
        ('A04','Bounded IO/children/locks/dispatch/observation; enforced or justified load/retries/signals/liveness','P03/P07'),
        ('A05','Four qualified coordinator markers; independent successful-capture eligibility','source/P02/P03'),
        ('A06','Complete nonnegative ordered phase partition with no uncovered exit gap','source/P06/P07'),
        ('A07','Verified Tpre<=60, Tworker<=750, Tpost<=60 in the same compatible wall unit','P06/P07/P08')]
    return dict(
        t0_tR_tW_tF_exact_source_and_clock_domain=dict(markers=c['time']['normative_markers'],
            required_clock=c['time']['clock'],runtime_clock_domain=r['clock_and_process_service_domain_identity'],
            platform_clock_domain=p['clock_monotonicity_domain_and_latency_accounting'],
            actual_clock_domain_id=None,clock_guarantee_verified=False,timestamps_collected=False,
            marker_source_definitions_bound=True,marker_runtime_occurrence_attested=False),
        exact_True_wait_return_and_independent_success_qualification=dict(
            qualification=c['time']['success_path_qualification'],failure_claim=c['time']['failure_claim'],
            observation_latency_rule=c['time']['observation_latency_rule'],
            wait_return_exact_True_required=True,wait_True_not_capture_success=True,
            independent_exit0_authority_input_packet_page_functional_capture_and_finally_checks_required=True,
            later_checks_never_move_tW=True,False_or_exception_not_qualified_tW=True,
            source_success_gate_not_modified=True,successful_run_observed=False,
            successful_progress_or_existence_proved=False,no_vacuous_implication_as_admission=True),
        nonnegative_complete_phase_partition=dict(rule=c['time']['ordered_interval_rule'],
            symbolic_difference_coefficients=dict(Tpre=[-1,1,0,0],Tworker=[0,-1,1,0],Tpost=[0,0,-1,1]),
            coefficient_marker_order=['t0','tR','tW','tF'],telescoped_coefficients=[-1,0,0,1],
            conditional_algebra_identity='(tR-t0)+(tW-tR)+(tF-tW)=tF-t0',
            algebra_identity_verified=True,
            nonnegativity_requires_order_and_accepted_common_monotonic_domain=True,
            endpoint_convention='Ordered coordinator-clock intervals [t0,tR), [tR,tW), [tW,tF]; boundary events allocated by their completed-return definitions.',
            process_time_sum_not_phase_wall=True,physical_exit_not_boundary=True,worker_receipt_not_tR=True,
            pre_tR_worker_coverage_rule=c['cost_coverage']['pre_tR_worker_rule'],
            finally_through_tF_rule=c['cost_coverage']['finally_rule'],
            work_assignment_and_overlap_coverage_proved=False,actual_interval_order_and_nonnegativity_attested=False,
            complete_phase_partition_proved=False,no_unknown_marker_coerced_to_zero=True),
        verified_Tpre_Tworker_Tpost_upper_seconds=dict(phases=phases,
            conditional_theorem=dict(premises=[dict(id=i,required=q,source_package=src,satisfied=False) for i,q,src in premises],
                implication='If A01-A07 hold on a qualified success, tF-t0 = Tpre+Tworker+Tpost <= 60+750+60 = 870 <= 900.',
                conditional_numeric_sum_seconds=870,conditional_target_seconds=900,
                premises_satisfied=False,accepted_as_actual_success_bound=False),
            verified_phase_sum_seconds=None,verified_end_to_end_upper_seconds=None,
            all_three_phase_bounds_verified=False,successful_completion_within900_verified=False),
        heap_runtime_service_assumptions_satisfied=dict(
            scope_acceptance=s['acceptance_state'],runtime_acceptance=r['acceptance'],platform_acceptance=p['acceptance'],
            heap_acceptance=h['acceptance'],work_acceptance=w['acceptance'],compatibility_acceptance=k['acceptance'],
            P06_review=pin(P+'D5-I164-P06-documentary-review.json'),P07_review=pin(P+'D5-I166-P07-documentary-review.json'),
            dependency_preparation_or_documentary_review_not_resource_acceptance=True,
            exact_process_clock_work_service_units_match=False,heap_runtime_service_assumptions_satisfied=False,
            independent_and_custodian_acceptance_obtained=False,external_material_obtained=False,
            no_global_absence_or_actual_infeasibility_claim=True),
        **{'60_750_60_plus30_conserved_zero_transfer_account':dict(
            time_account=c['reserve_accounting']['time'],worker_nested_account=c['reserve_accounting']['worker_nested'],
            candidate_phase_seconds=[60,750,60],candidate_phase_sum_seconds=870,
            unassigned_reserve_seconds=30,conserved_total_seconds=900,
            arithmetic_conservation_verified=True,time_transferred_seconds=0,worker_category_transferred_seconds=0,
            reserve_is_not_automatic_phase_slack=True,reserve_not_service_or_runtime_measurement=True,
            no_extra_per_phase_process_thread_group_or_category_credit=True,
            heap_time_byte_second_or_H11_borrowing_applied=False,watchdog=c['time']['current_source_watchdog'],
            new_timer_installed=False)},
        failure_paths_excluded_from_success_claim_without_omitting_heap_rejection_scope=dict(
            excluded_from_qualified_success=[
                'wait False or exception, including timeout; no qualified tW',
                'worker nonzero exit or failure envelope',
                'authority/input/packet/page/functional/capture rejection',
                'exceptional or invalid success-finally/context/launch writes/closes or return'],
            all_failure_or_cleanup_within900_claimed=False,no_missing_time_or_marker_as_zero=True,
            no_rejection_or_timeout_as_success_timing_evidence=True,
            heap_scope=r['clock_and_process_service_domain_identity']['process_scope']['failure_scope'],
            scope_contract_reference=pin(SCOPE),heap_rollup_reference=pin(HEAP),
            bounded_observer_rejection_prefixes_and_retained_tracebacks_still_required=True,
            original_scope_and_preconditions_unchanged=True,heap_rejection_scope_closed=False,
            failure_cleanup_liveness_bound=None,all_failure_deadline_proved=False))


def build_output():
    task=next(t for t in rd(PLAN)['tasks'] if t['id']=='P08')
    fields=phase_fields();assert list(fields)==task['required_specific_fields']
    contributions=['Source anchors only; actual common clock/domain unverified.',
        'Exact-True and independent success requirements, not observed success or liveness.',
        'Conditional telescoping algebra, not actual ordered complete work/latency coverage.',
        'Three null upper bounds and explicitly unsatisfied conditional theorem premises.',
        'Six dependency dispositions retained without resource acceptance.',
        'Candidate arithmetic and zero allocations, not available service or phase slack.',
        'Failure exclusion rule and preserved heap rejection scope, not verified failure heap or cleanup bounds.']
    paths={t['id']:t['planned_output'] for t in rd(PLAN)['tasks']}
    criteria=next(o['criteria'] for o in rd(P+'D5-I131-E01-E05-review.json')['obligations'] if o['id']=='E05')
    decision=dict(rd(COMPAT)['decision']);decision['complete_phase_bounds_verified']=False
    return dict(schema=task['output_schema'],package_id='P08',increment='I167',date='2026-11-15',timezone='Europe/Madrid',base_commit=BASE,
        status='PREPARED_CONDITIONAL_PHASE_THEOREM_INSUFFICIENT_E05_OPEN_NOT_ADMITTED',
        evidence_kind='STATIC_SOURCE_DEFINITIONS_CONDITIONAL_ALGEBRA_AND_MISSING_PHASE_BOUNDS_NOT_TIMING_PROOF',
        plan_binding=dict(**pin(PLAN),task_record_canonical_sha256=digest(task)),candidate_binding=rd(COMPAT)['candidate_binding'],
        input_pins=inputs(),dependencies=[dict(id=i,**pin(paths[i]),accepted_for_resource_closure=False) for i in task['depends_on']],
        source_evidence=source_evidence(),**fields,
        field_assessment=[dict(field=f,result='INSUFFICIENT_FOR_ACCEPTANCE',documentary_contribution=b,
            resource_obligation_closed=False) for f,b in zip(fields,contributions,strict=True)],
        E05_criterion_disposition=[dict(id=x['id'],inherited_result=x['result'],I167_result=x['result'],closed=False) for x in criteria],
        acceptance=dict(rule=task['acceptance'],rejection_rule=task['rejection'],preparation_complete=True,
            accepted_as_verified_phase_or_success900_proof=False,E05_closed=False,resource_obligations_closed=0),
        early_stop=dict(external_evidence_block=True,dependency_nonacceptance_preserved=True,
            runtime_or_platform_probing_authorized=False,actual_infeasibility_proved=False),
        provenance=dict(producer='Codex assistant preparing I167 in same chat as preceding packages',
            planned_author_role=task['responsible_role'],planned_review_role=task['review_role'],
            independent_reviewer_identity=None,independent_acceptance=False,custodian_acceptance=False),
        reserve_accounting=rd(CONTRACT)['reserve_accounting'],
        non_execution_and_zero_transfer_policy=rd(SCOPE)['non_execution_and_zero_transfer_policy'],
        E06=rd(COMPAT)['E06'],decision=decision)


def build_review():
    o=rd(OUT);progress=[]
    for t in rd(PLAN)['tasks']:
        exists=(ROOT/t['planned_output']).exists()
        progress.append(dict(package_id=t['id'],path=t['planned_output'],output_created=exists,
            sha256=sha(t['planned_output']) if exists else None,accepted_for_resource_closure=False))
    return dict(schema='d5.i167-p08-preparation-review.v1',increment='I167',date='2026-11-15',base_commit=BASE,
        status='P08_PREPARATION_COMPLETE_PHASE_BOUNDS_UNPROVED_NO_ADMISSION',
        input_pins={**inputs(),OUT:sha(OUT)},output=dict(**pin(OUT),schema=o['schema'],produced=True),
        counts=dict(required_fields=7,insufficient_fields=7,dependencies=6,phase_bounds=3,null_verified_phase_uppers=3,
            source_files=79,cost_anchors=20,markers=4,lexical_order_witnesses=5,unsatisfied_theorem_premises=7,
            P06_vector_requirements=20,P07_join_requirements=20,input_pins=len(inputs()),remaining_unproduced_packages=2),
        preparation_checks=dict(all_required_fields_present=True,exact_True_and_later_success_not_conflated=True,
            symbolic_telescoping_checked=True,all_phase_upper_bounds_null=True,no_premise_assumed_satisfied=True,
            no_automatic_reserve_or_byte_second_conversion=True,failure_heap_scope_preserved=True,
            no_independent_acceptance_fabricated=True),
        package_progress=progress,E05_criterion_disposition=o['E05_criterion_disposition'],acceptance=o['acceptance'],
        decision=o['decision'],E06=o['E06'],independent_review=dict(accepted=False,reviewer_identity=None),
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I167-audit.py',
            expected_result='PASS_STATIC_SOURCE_ONLY',runtime_harness='N/A: documentary phase-proof preparation; target execution prohibited.',
            over400_lines=True,reason='Pinned evidence, conditional proof records and self-contained audit; overage reported.'),
        git_publication=dict(commit_and_push_all_requested=True,publication_does_not_admit_candidate=True))


def main():
    assert rd(OUT)==build_output() and rd(REVIEW)==build_review()
    published_inputs()
    o,c=rd(OUT),rd(CONTRACT)
    assert sha(CONTRACT)=='e7a873a2aea8648d225f2272854e0b15c3f21de5826df06f16dfb6e45aa54576'
    prior=rd(OLD_SEAL)
    preserved={**prior['preserved_published308'],**prior['artifacts'],OLD_SEAL:sha(OLD_SEAL)}
    seal=rd(SEAL)
    assert len(preserved)==313 and seal['preserved_published313']==preserved
    assert seal['schema']=='d5.i167-integrity.v1' and seal['base_commit']==BASE and seal['date']=='2026-11-15'
    assert set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts'],rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for path,h in pins.items():assert sha(path)==h,path
    task=next(t for t in rd(PLAN)['tasks'] if t['id']=='P08')
    assert task['depends_on']==['P01','P02','P03','P05','P06','P07'] and len(o['dependencies'])==6
    coeff=o['nonnegative_complete_phase_partition']['symbolic_difference_coefficients']
    assert [sum(v[i] for v in coeff.values()) for i in range(4)]==[-1,0,0,1]
    phases=o['verified_Tpre_Tworker_Tpost_upper_seconds']['phases']
    assert [x['id'] for x in phases]==['Tpre','Tworker','Tpost']
    assert [x['candidate_wall_seconds'] for x in phases]==[60,750,60]
    assert all(x['verified_upper_seconds'] is None and x['derivation'] is None for x in phases)
    assert [v for x in phases for v in x['required_P06_vectors']]==[v['id'] for phase in ['Tpre','Tworker','Tpost'] for v in rd(WORK)['per_process_phase_work_vectors_and_units']['vectors'] if v['phase']==phase]
    assert sum(len(x['required_P06_vectors']) for x in phases)==20
    assert all(x['required_P06_vectors']==x['required_P07_joins'] for x in phases)
    assert all(not x['satisfied'] for x in o['verified_Tpre_Tworker_Tpost_upper_seconds']['conditional_theorem']['premises'])
    assert c['reserve_accounting']['time']['allocation_seconds']==dict(Tpre=0,Tworker=0,Tpost=0)
    assert sum(c['reserve_accounting']['worker_nested']['additional_category_allocation_seconds'].values())==0
    assert 60+750+60==870 and 870+30==900
    assert [m['id'] for m in o['source_evidence']['marker_checks']]==['t0','tR','tW','tF']
    assert o['source_evidence']['marker_checks'][2]['source_check']['anchor']['kind']=='CALL_RETURN_EXACT_TRUE'
    for t in rd(PLAN)['tasks']:
        if t['id'] in ['P09','P10']:assert not (ROOT/t['planned_output']).exists()
    for p in [P+'D5-JOINT-capture-authorization.json',P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:assert not (ROOT/p).exists()
    for k in ['phase_bounds_verified','independent_acceptance','product_or_components_executed','quotas_changed','proposal_enabled','D5_closed']:assert seal[k] is False
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    changes=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changes==FILES,changes
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I167',package='P08',preparation_complete=True,
        accepted_as_phase_or_success900_proof=False,required_fields=7,insufficient_fields=7,null_verified_phase_uppers=3,
        prior_published_files_preserved=313,new_files=5,product_or_components_executed=0,quotas_changed=False,
        resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
