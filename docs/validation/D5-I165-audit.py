#!/usr/bin/env python3
"""I165 documentary Git/JSON/AST audit. Never imports or executes target sources."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'ddee9044329da00965c80f95d3a3c3087304c6f0'
OUT = P+'D5-PFC126-03-E03-E04-COMPATIBILITY.json'
REVIEW = P+'D5-I165-P07-preparation-review.json'
AUDIT = P+'D5-I165-audit.py'
SEAL = P+'D5-I165-integrity.json'
DESIGN = 'docs/design/D5-I165-P07-COMPATIBILITY.md'
PLAN = P+'D5-I132-E01-E05-evidence-plan.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
RUNTIME = P+'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
PLATFORM = P+'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
WORK = P+'D5-PFC126-03-E03-WORK-GROUPS.json'
SCOPE = P+'D5-PFC126-03-RESOURCE-SCOPE.json'
OLD_REVIEW = P+'D5-I164-P06-documentary-review.json'
OLD_SEAL = P+'D5-I164-integrity.json'
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
    paths = [WORK,OLD_REVIEW,OLD_SEAL,P+'D5-I164-P06-source-reconstruction.json',
        P+'D5-I164-audit.py',P+'D5-I163-P06-preparation-review.json',
        P+'D5-I163-integrity.json',P+'D5-I163-audit.py']
    return {**rd(WORK)['input_pins'],**{p:sha(p) for p in paths}}


def source_evidence():
    w,c=rd(WORK),rd(CONTRACT)
    sources=w['source_evidence']['source_pins']
    summaries=[]
    trees={}
    for path,h in sorted(sources.items()):
        assert sha(path)==h
        tree=ast.parse((ROOT/path).read_text())
        trees[path]=tree
        summaries.append(dict(path=path,sha256=h,parsed_as_syntax_only=True))
    def locate(anchor):
        nodes=[n for n in ast.walk(trees[anchor['path']]) if hasattr(n,'lineno')
            and (n.lineno,n.col_offset,n.end_lineno)==(anchor['line'],anchor['column'],anchor['end_line'])
            and hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==anchor['AST_sha256']]
        assert len(nodes)==1,anchor
        if anchor.get('expression') is not None:assert ast.unparse(nodes[0])==anchor['expression']
        return dict(anchor=anchor,source_sha256=sha(anchor['path']),node_kind=type(nodes[0]).__name__,source_binding_verified=True)
    return dict(source_files=summaries,source_file_count=len(summaries),
        cost_anchors=[locate(a) for a in c['cost_coverage']['source_anchors']],
        markers=[dict(id=m['id'],event=m['event'],clock_owner=m['clock_owner'],clock_value=None,
            source_check=locate(m['source_anchor'])) for m in c['time']['normative_markers']],
        lexical_binding_not_clock_service_or_WCET_attestation=True)


def compatibility_fields():
    c,w,r,p=rd(CONTRACT),rd(WORK),rd(RUNTIME),rd(PLATFORM)
    vectors=w['per_process_phase_work_vectors_and_units']['vectors']
    joins=[]
    for v in vectors:
        joins.append(dict(id=v['id'],group=v['group_id'],process_set=v['process_set_id'],phase=v['phase'],
            work_upper=v['complete_work_upper'],work_unit=v['work_unit'],WCET_upper_seconds=v['static_WCET_upper_seconds'],
            exact_runtime_id=None,exact_platform_id=None,service_process_domain=None,
            rate_unit=None,rate_lower_bound=None,latency_upper_seconds=None,conversion_derivation=None,
            compatible=False,status='BLOCKED_MISSING_WORK_RUNTIME_PLATFORM_UNIT_SERVICE_OR_WCET'))
    categories=[]
    for phase in ['Tpre','Tworker','Tpost']:
        for category,budget in [('CPU',600),('IO_child_wait',90),('scheduler_blocking_observation',60)]:
            categories.append(dict(phase=phase,category=category,
                candidate_upper_seconds=budget if phase=='Tworker' else None,
                verified_upper_seconds=None,complete_coverage=False,derivation=None,
                extra_reserve_seconds=0,all_relevant_processes_required=True))
    latency_specs=[
        ('interpreter_import_native_startup','Tpre',['C02','C10'],'CPU','worker all threads; pre-main plus original/native startup'),
        ('RELEASE_write_close_and_READY','Tpre',['C01','C02','C03','C04','C10'],'mixed_must_split','coordinator and concurrent worker/children'),
        ('post_receipt_before_parent_tR','Tpre',['C04','C10'],'mixed_must_split','worker all threads and original children'),
        ('original_native_codec_allocation_GC_destruction','all_phases',['C01','C02','C03','C04','C05','C06','C07','C08','C09','C10'],'CPU','all relevant coordinator/worker/child contributors'),
        ('IO_and_child_completion','all_phases',['C01','C02','C03','C04','C05','C06','C07','C08','C09','C10'],'IO_child_wait','all relevant processes and transitive original children'),
        ('locks_dispatch_denied_service','all_phases',['C01','C02','C03','C04','C05','C06','C07','C08','C09','C10'],'scheduler_blocking_observation','all relevant process/window contributors'),
        ('physical_exit_to_exact_True_wait_return','Tworker',['C06','C10'],'scheduler_blocking_observation','coordinator dispatch/reap/observation/return, even worker already exited'),
        ('normal_cleanup_and_input_checks','Tpost',['C07','C10'],'mixed_must_split','coordinator including native IO and cleanup progress'),
        ('evidence_read_parse_hash_pages_finish','Tpost',['C08','C10'],'mixed_must_split','coordinator evidence validation, not input-byte ledger alone'),
        ('success_finally_context_launch_writes_closes','Tpost',['C09','C10'],'mixed_must_split','coordinator through final normal launch return')]
    owners=[dict(id=i,phase=phase,groups=groups,required_category=cat,process_scope=scope,
        upper_seconds=None,verified=False,accounting='Requirement only; split mixed terms or use justified additive overcount. No overlap deduction or zero for missing terms.')
        for i,phase,groups,cat,scope in latency_specs]
    return dict(
        exact_runtime_platform_process_unit_match=dict(
            runtime_evidence=pin(RUNTIME),platform_evidence=pin(PLATFORM),work_evidence=pin(WORK),
            runtime_acceptance=r['acceptance'],platform_acceptance=p['acceptance'],
            runtime_clock_process_domain=r['clock_and_process_service_domain_identity'],
            platform_service=p['compatible_CPU_service_unit_rate_latency_or_WCET_assumptions'],
            platform_process_scope=p['coordinator_child_resource_and_interference_scope'],
            exact_target_runtime_platform_mapping=None,complete_process_enumeration=False,
            joins=joins,all20_joins_compatible=False),
        work_to_service_conversion_or_WCET_derivation=dict(
            candidate_route=c['time']['CPU_proof_route'],selected_route=None,
            whole_window_work_upper=None,compatible_work_unit=None,rate_lower_bound=None,rate_unit=None,
            service_latency_upper_seconds=None,static_WCET_upper_seconds=None,complete_conversion_derivation=None,
            service_curve_reference=c['time']['minimum_service_curve'],
            conditional_routes=[dict(id='ATTESTED_SERVICE',selected=False,requirements=[
                'Complete transitive whole-window work plus compatible units, exact process domain and valid attested lower service.',
                'Justify workload arrivals, initial backlog, concurrency and busy-period/window applicability; no automatic W/r from total clones.',
                'For beta(dt)=r*max(0,dt-L), r>0: L+W/r only after a theorem proves full admitted work W is served within that bound under stated arrival/backlog/readiness assumptions.',
                'CPU-time rate yields CPU execution time only; bound all denied service, IO/child waits and observation separately before wall-time use.',
                'Wall-time service latency must be owned explicitly; repeated per-window/per-process latency charges require a justified composition.']),
                dict(id='EXACT_PLATFORM_WCET',selected=False,requirements=[
                    'Full exact accepted runtime/platform, original/native/codec/GC/destruction and bounded paths; justified WCET for all contributors.',
                    'Declare whether bound is CPU execution or full wall; include uncovered IO/children/locks/dispatch/observation exactly or conservatively.',
                    'Composition and memory/cache/allocator/interference assumptions must hold for all required processes/phases.'])],
            forbidden_shortcuts=['W/budget as guaranteed rate','MHz/core count as guaranteed service','bytes/clones as CPU seconds',
                'CPU sum as wall time','watchdog or quota as service proof','missing work or latency as zero'],verified=False),
        latency_owner_map_without_unproved_deductions=dict(owners=owners,
            disjoint_or_justified_additive_overcount_required=True,overlap_subtracted_seconds=0,
            owner_map_requirement_not_complete_bound=True,unowned_latency_assumed_zero=False,
            service_latency_and_denied_service_double_credit_forbidden=True,composition_proved=False),
        CPU_IO_child_scheduler_and_native_delay_bounds=dict(per_phase_categories=categories,
            complete_transitive_native_original_GC_destruction_bound=None,
            all_phase_CPU_wait_scheduler_uppers_verified=False,
            worker_CPU_budget_not_reused_for_Tpre=True,C10_crosscutting_not_extra_budget=True,
            candidate_worker_partition=c['time']['worker_service_partition']),
        provider_load_interference_assumptions_satisfied=dict(
            admissible_assumptions=p['admissible_signal_retry_interference_and_load_assumptions'],
            bounded_delay_requirements=p['bounded_scheduler_locks_IO_child_completion_observation_delays'],
            attesting_authority=None,validity_interval=None,provider_material_obtained=False,
            assumption_enforcement_evidence=None,satisfied=False,external_contacts_made=False,
            no_global_absence_claim=True,no_local_machine_sampling=True),
        pre_tR_overlap_and_exit_to_tW_latency_accounted=dict(
            normative_markers=c['time']['normative_markers'],interval_rule=c['time']['ordered_interval_rule'],
            success_qualification=c['time']['success_path_qualification'],
            observation_latency_rule=c['time']['observation_latency_rule'],
            pre_tR_rule=c['cost_coverage']['pre_tR_worker_rule'],finally_rule=c['cost_coverage']['finally_rule'],
            affected_pre_tR_vectors=[v['id'] for v in vectors if v['group_id'] in ['C02','C04'] or (v['group_id']=='C10' and v['phase']=='Tpre')],
            pre_tR_complete_work_or_conservative_overcount_upper=None,exit_to_wait_True_latency_upper_seconds=None,
            success_finally_through_tF_upper_seconds=None,coverage_required=True,coverage_proved=False,
            worker_receipt_not_parent_tR=True,physical_exit_not_tW=True,wait_True_not_capture_success=True,
            later_qualification_never_moves_tW=True,False_or_exception_not_qualified_tW=True,packet_finish_not_tF=True),
        worker_category_upper_vector_and_coverage_inequality=dict(
            candidate_vector_seconds=dict(CPU=600,IO_child_wait=90,scheduler_blocking_observation=60),
            verified_vector_seconds=dict(CPU=None,IO_child_wait=None,scheduler_blocking_observation=None),
            candidate_sum_seconds=750,verified_sum_seconds=None,
            required_inequality='Tworker <= U_CPU + U_IO_child_wait + U_scheduler_observation <= 600+90+60 = 750',
            inequality_proved=False,candidate_arithmetic_only=True,
            conditions=['Every contributor in tR..exact-True tW covered under compatible process/domain/unit assumptions.',
                'Disjoint attribution or justified conservative additive overcount; CPU is not automatically wall.',
                'No omitted initial backlog, native/GC/destruction or exit-to-wait-return delay; no reserve credit.'],
            separate_phase_requirements=[dict(phase=x['id'],candidate_upper_seconds=x['candidate_wall_seconds'],verified_upper_seconds=None,
                complete_CPU_wait_scheduler_coverage=False) for x in c['time']['phase_budgets'] if x['id']!='Tworker'],
            end_to_end_candidate_seconds=900,unassigned_reserve_seconds=30,reserve_transferred_seconds=0,
            end_to_end_success_proved=False,P08_phase_theorem_not_produced=True))


def build_output():
    plan,c,w=rd(PLAN),rd(CONTRACT),rd(WORK)
    task=next(t for t in plan['tasks'] if t['id']=='P07')
    fields=compatibility_fields()
    assert list(fields)==task['required_specific_fields']
    paths={t['id']:t['planned_output'] for t in plan['tasks']}
    old_criteria=[dict(obligation=o['id'],id=x['id'],inherited_result=x['result'],I165_result=x['result'],closed=False)
        for o in rd(P+'D5-I131-E01-E05-review.json')['obligations'] if o['id'] in ['E03','E04'] for x in o['criteria']]
    decision=dict(w['decision']);decision['complete_compatibility_verified']=False
    return dict(schema=task['output_schema'],package_id='P07',increment='I165',date='2026-11-15',timezone='Europe/Madrid',base_commit=BASE,
        status='PREPARED_INSUFFICIENT_COMPATIBILITY_E03_E04_OPEN_NOT_ADMITTED',
        evidence_kind='STATIC_REQUIREMENTS_JOIN_AND_NEGATIVE_EVIDENCE_ASSESSMENT_NOT_CAPACITY_SERVICE_OR_WCET_PROOF',
        plan_binding=dict(**pin(PLAN),task_record_canonical_sha256=digest(task)),candidate_binding=w['candidate_binding'],
        input_pins=inputs(),dependencies=[dict(id=i,**pin(paths[i]),accepted_for_resource_closure=False) for i in task['depends_on']],
        source_evidence=source_evidence(),**fields,
        field_assessment=[dict(field=f,result='INSUFFICIENT_FOR_ACCEPTANCE',resource_obligation_closed=False,
            basis='Required compatibility record present; accepted exact target/work/service/latency evidence and derivation absent.') for f in fields],
        E03_E04_criterion_disposition=old_criteria,
        unchanged_candidate_reference=dict(time=c['time'],reserve_accounting=c['reserve_accounting'],numeric_candidates=c['product_numeric_candidates']),
        acceptance=dict(rule=task['acceptance'],rejection_rule=task['rejection'],preparation_complete=True,
            accepted_as_compatible_work_service_or_WCET_proof=False,E03_closed=False,E04_closed=False,resource_obligations_closed=0),
        early_stop=dict(external_evidence_block=True,dependency_nonacceptance_preserved=True,
            further_runtime_or_platform_probing_authorized=False,actual_infeasibility_proved=False),
        provenance=dict(producer='Codex assistant preparing I165 in same chat as I163/I164',
            planned_author_role=task['responsible_role'],planned_review_role=task['review_role'],
            independent_reviewer_identity=None,independent_acceptance=False,custodian_acceptance=False),
        non_execution_and_zero_transfer_policy=rd(SCOPE)['non_execution_and_zero_transfer_policy'],E06=w['E06'],decision=decision)


def build_review():
    o=rd(OUT);plan=rd(PLAN)
    progress=[]
    for t in plan['tasks']:
        exists=(ROOT/t['planned_output']).exists()
        progress.append(dict(package_id=t['id'],path=t['planned_output'],output_created=exists,
            sha256=sha(t['planned_output']) if exists else None,accepted_for_resource_closure=False))
    return dict(schema='d5.i165-p07-preparation-review.v1',increment='I165',date='2026-11-15',base_commit=BASE,
        status='P07_PREPARATION_COMPLETE_COMPATIBILITY_UNPROVED_NO_ADMISSION',
        input_pins={**inputs(),OUT:sha(OUT)},output=dict(**pin(OUT),schema=o['schema'],produced=True),
        counts=dict(required_fields=7,insufficient_fields=7,process_phase_joins=20,phase_category_records=9,
            required_latency_owner_records=10,source_files=79,cost_source_anchors=20,markers=4,
            inherited_missing_group_values=30,inherited_missing_selected_vector_values=120,
            input_pins=len(inputs()),remaining_unproduced_packages=3),
        preparation_checks=dict(exact_plan_fields_present=True,all20_P06_vectors_joined=True,
            no_unattested_conversion_applied=True,all_verified_category_bounds_null=True,
            pre_tR_exit_observation_finally_requirements_present=True,budgets_and_reserves_preserved=True,
            dependency_rejection_preserved=True,no_independent_review_fabricated=True),
        package_progress=progress,E03_E04_criterion_disposition=o['E03_E04_criterion_disposition'],
        acceptance=o['acceptance'],decision=o['decision'],E06=o['E06'],
        independent_review=dict(accepted=False,reviewer_identity=None),
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I165-audit.py',
            expected_result='PASS_STATIC_SOURCE_ONLY',runtime_harness='N/A: documentary preparation only; product/component execution prohibited.',
            over400_lines=True,reason='Traceable compatibility records, input pins and self-contained documentary audit; overage reported.'),
        git_publication=dict(commit_and_push_all_requested=True,publication_does_not_enable_admission=True))


def main():
    assert rd(OUT)==build_output()
    assert rd(REVIEW)==build_review()
    o=rd(OUT);c=rd(CONTRACT)
    assert sha(CONTRACT)=='e7a873a2aea8648d225f2272854e0b15c3f21de5826df06f16dfb6e45aa54576'
    prior=rd(OLD_SEAL)
    preserved={**prior['preserved_published298'],**prior['artifacts'],OLD_SEAL:sha(OLD_SEAL)}
    seal=rd(SEAL)
    assert len(preserved)==303 and seal['preserved_published303']==preserved
    assert seal['schema']=='d5.i165-integrity.v1' and seal['base_commit']==BASE and seal['date']=='2026-11-15'
    assert set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts'],inputs(),rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for path,h in pins.items():assert sha(path)==h,path
    # Exact input snapshots from Git, including source corpus and resource evidence.
    for path,h in inputs().items():
        blob=subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
        assert hashlib.sha256(blob).hexdigest()==h,path
    assert len(o['source_evidence']['cost_anchors'])==20 and o['source_evidence']['source_file_count']==79
    assert [m['id'] for m in o['source_evidence']['markers']]==['t0','tR','tW','tF']
    assert o['source_evidence']['markers'][2]['source_check']['anchor']['kind']=='CALL_RETURN_EXACT_TRUE'
    joins=o['exact_runtime_platform_process_unit_match']['joins']
    v=rd(WORK)['per_process_phase_work_vectors_and_units']['vectors']
    assert [x['id'] for x in joins]==[x['id'] for x in v] and len(joins)==20
    for x in joins:
        assert not x['compatible'] and all(x[k] is None for k in ['work_upper','work_unit','WCET_upper_seconds','rate_unit','rate_lower_bound','latency_upper_seconds','conversion_derivation'])
    assert not rd(RUNTIME)['acceptance']['accepted_as_runtime_identity']
    assert not rd(PLATFORM)['acceptance']['accepted_as_platform_evidence']
    part=c['time']['worker_service_partition']
    assert [part[k] for k in ['candidate_CPU_upper_seconds','candidate_IO_child_wait_upper_seconds','candidate_scheduler_and_blocking_upper_seconds']]==[600,90,60]
    assert [x['candidate_wall_seconds'] for x in c['time']['phase_budgets']]==[60,750,60]
    assert c['time']['unassigned_wall_reserve_seconds']==30 and 60+750+60+30==900
    assert all(x['verified_upper_seconds'] is None for x in o['CPU_IO_child_scheduler_and_native_delay_bounds']['per_phase_categories'])
    assert all(x['upper_seconds'] is None for x in o['latency_owner_map_without_unproved_deductions']['owners'])
    for t in rd(PLAN)['tasks']:
        if t['id'] in ['P08','P09','P10']:assert not (ROOT/t['planned_output']).exists()
    for path in [P+'D5-JOINT-capture-authorization.json',P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:assert not (ROOT/path).exists()
    for k in ['compatibility_verified','independent_acceptance','product_or_components_executed','quotas_changed','proposal_enabled','D5_closed']:assert seal[k] is False
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    changes=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changes==FILES,changes
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I165',package='P07',preparation_complete=True,
        accepted_as_compatible_proof=False,required_fields=7,insufficient_fields=7,process_phase_joins=20,
        source_files=79,prior_published_files_preserved=303,new_files=5,product_or_components_executed=0,
        quotas_changed=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',
        git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
