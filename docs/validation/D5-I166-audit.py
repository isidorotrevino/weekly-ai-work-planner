#!/usr/bin/env python3
"""I166 static documentary review. No target imports, execution or measurements."""
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


def validate_preparation():
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
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)


REVIEW_BASE = '7850738bd50ca58d827ecdc5102e17c68e2577d7'
NEW_REVIEW = P+'D5-I166-P07-documentary-review.json'
RECON = P+'D5-I166-P07-source-reconstruction.json'
NEW_AUDIT = P+'D5-I166-audit.py'
NEW_SEAL = P+'D5-I166-integrity.json'
NEW_DESIGN = 'docs/design/D5-I166-P07-COMPATIBILITY-REVIEW.md'
NEW_FILES = {NEW_REVIEW,RECON,NEW_AUDIT,NEW_SEAL,NEW_DESIGN}


def published_blobs(pins):
    # One Git read, independently bound to the review base and current bytes.
    request=''.join(REVIEW_BASE+':'+p+'\n' for p in sorted(pins)).encode()
    import io
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=request))
    blobs={}
    for path,h in sorted(pins.items()):
        header=stream.readline().decode().split()
        assert len(header)==3 and header[1]=='blob',path
        body=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(path),path
        blobs[path]=body
    return blobs


def reconstruct():
    pins={**rd(OUT)['input_pins'],**{p:sha(p) for p in [OUT,REVIEW,AUDIT,SEAL]}}
    blobs=published_blobs(pins)
    o,w,c,r,p,plan=[json.loads(blobs[x]) for x in [OUT,WORK,CONTRACT,RUNTIME,PLATFORM,PLAN]]
    task=next(t for t in plan['tasks'] if t['id']=='P07')
    assert o['schema']==task['output_schema'] and task['planned_output']==OUT
    assert task['depends_on']==['P02','P03','P06']
    assert len(task['required_specific_fields'])==7
    # Rebuild the relation by (group, process, phase), not by the producer's IDs alone.
    wvectors=w['per_process_phase_work_vectors_and_units']['vectors']
    expected={(v['group_id'],v['process_set_id'],v['phase']):v for v in wvectors}
    actual=o['exact_runtime_platform_process_unit_match']['joins']
    assert len(actual)==len(expected)==20
    nullkeys=['work_upper','work_unit','WCET_upper_seconds','exact_runtime_id','exact_platform_id',
        'service_process_domain','rate_unit','rate_lower_bound','latency_upper_seconds','conversion_derivation']
    observed=[]
    for row in actual:
        key=(row['group'],row['process_set'],row['phase'])
        v=expected.pop(key)
        assert row['id']==v['id'] and not row['compatible']
        assert row['work_upper']==v['complete_work_upper'] and row['work_unit']==v['work_unit']
        assert row['WCET_upper_seconds']==v['static_WCET_upper_seconds']
        assert all(row[k] is None for k in nullkeys)
        observed.append(dict(id=row['id'],group=key[0],process=key[1],phase=key[2],unproved={k:row[k] for k in nullkeys}))
    assert not expected
    categories=o['CPU_IO_child_scheduler_and_native_delay_bounds']['per_phase_categories']
    category_map={(x['phase'],x['category']):x for x in categories}
    assert len(category_map)==len(categories)==9
    for phase in ['Tpre','Tworker','Tpost']:
        for cat,budget in [('CPU',600),('IO_child_wait',90),('scheduler_blocking_observation',60)]:
            x=category_map[(phase,cat)]
            assert x['candidate_upper_seconds']==(budget if phase=='Tworker' else None)
            assert x['verified_upper_seconds'] is None and x['derivation'] is None
            assert not x['complete_coverage'] and x['extra_reserve_seconds']==0
    owners=o['latency_owner_map_without_unproved_deductions']['owners']
    owner_expectations={
        'interpreter_import_native_startup':('Tpre','CPU'),
        'RELEASE_write_close_and_READY':('Tpre','mixed_must_split'),
        'post_receipt_before_parent_tR':('Tpre','mixed_must_split'),
        'original_native_codec_allocation_GC_destruction':('all_phases','CPU'),
        'IO_and_child_completion':('all_phases','IO_child_wait'),
        'locks_dispatch_denied_service':('all_phases','scheduler_blocking_observation'),
        'physical_exit_to_exact_True_wait_return':('Tworker','scheduler_blocking_observation'),
        'normal_cleanup_and_input_checks':('Tpost','mixed_must_split'),
        'evidence_read_parse_hash_pages_finish':('Tpost','mixed_must_split'),
        'success_finally_context_launch_writes_closes':('Tpost','mixed_must_split')}
    assert len(owners)==len(owner_expectations)==10
    for x in owners:
        assert (x['phase'],x['required_category'])==owner_expectations.pop(x['id'])
        assert x['upper_seconds'] is None and not x['verified'] and x['process_scope']
    assert not owner_expectations
    source_pins=w['source_evidence']['source_pins']
    trees={path:ast.parse(blobs[path].decode()) for path in source_pins}
    assert len(trees)==79
    indices={}
    for path,tree in trees.items():
        index={}
        for n in ast.walk(tree):
            if hasattr(n,'lineno'):index.setdefault((n.lineno,n.col_offset,n.end_lineno),[]).append(n)
        indices[path]=index
    def bind(a):
        nodes=indices[a['path']][(a['line'],a['column'],a['end_line'])]
        found=[n for n in nodes if hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==a['AST_sha256']]
        assert len(found)==1
        if a.get('expression') is not None:assert ast.unparse(found[0])==a['expression']
        return dict(path=a['path'],source_sha256=pins[a['path']],line=a['line'],column=a['column'],end_line=a['end_line'],
            AST_sha256=a['AST_sha256'],node_kind=type(found[0]).__name__)
    cost_bindings=[bind(a) for a in c['cost_coverage']['source_anchors']]
    markers=[dict(id=m['id'],binding=bind(m['source_anchor']),clock_value=None) for m in c['time']['normative_markers']]
    # Source statements confirm definitions only, never timings or global liveness.
    launch=next(n for n in trees['testing/prospective_capture_joint_i122/capture.py'].body if isinstance(n,ast.FunctionDef) and n.name=='launch')
    wait=next(n for n in trees['testing/prospective_capture_typed/capture.py'].body if isinstance(n,ast.FunctionDef) and n.name=='wait_worker')
    waits=[n for n in ast.walk(launch) if isinstance(n,ast.Call) and ast.unparse(n)=='wait_worker(process)']
    assert len(waits)==1
    wait_try=next(n for n in wait.body if isinstance(n,ast.Try))
    assert ast.unparse(wait_try.body[-1])=='return True'
    assert any(isinstance(n,ast.Return) and ast.unparse(n)=='return False' for h in wait_try.handlers for n in ast.walk(h))
    assert ast.unparse(launch.body[-1])=='return context'
    assert c['time']['normative_markers'][2]['source_anchor']['kind']=='CALL_RETURN_EXACT_TRUE'
    conv=o['work_to_service_conversion_or_WCET_derivation']
    assert conv['selected_route'] is None and not conv['verified']
    assert [x['id'] for x in conv['conditional_routes']]==['ATTESTED_SERVICE','EXACT_PLATFORM_WCET']
    assert all(not x['selected'] and x['requirements'] for x in conv['conditional_routes'])
    assert all(conv[k] is None for k in ['whole_window_work_upper','compatible_work_unit','rate_lower_bound','rate_unit','service_latency_upper_seconds','static_WCET_upper_seconds','complete_conversion_derivation'])
    assert not r['acceptance']['accepted_as_runtime_identity'] and not p['acceptance']['accepted_as_platform_evidence']
    vector=o['worker_category_upper_vector_and_coverage_inequality']
    assert vector['candidate_vector_seconds']==dict(CPU=600,IO_child_wait=90,scheduler_blocking_observation=60)
    assert vector['verified_vector_seconds']==dict(CPU=None,IO_child_wait=None,scheduler_blocking_observation=None)
    assert vector['candidate_sum_seconds']==sum(vector['candidate_vector_seconds'].values())==750
    assert vector['verified_sum_seconds'] is None and not vector['inequality_proved']
    fields=[]
    for key in task['required_specific_fields']:
        fields.append(dict(field=key,canonical_sha256=digest(o[key]),
            assessment='INSUFFICIENT_FOR_ACCEPTANCE',resource_obligation_closed=False))
    return dict(schema='d5.i166-p07-source-reconstruction.v1',increment='I166',date='2026-11-15',base_commit=REVIEW_BASE,
        input_pins=pins,method='Fresh published Git blobs, relation-key joins, explicit category/owner maps and separate AST location index.',
        methodologically_separate=True,actor_independent=False,organizationally_independent=False,
        joins=observed,phase_categories=categories,latency_owners=owners,
        source_pins=source_pins,cost_anchor_bindings=cost_bindings,marker_bindings=markers,
        source_structure_checks=dict(unique_coordinator_wait_call=True,normal_wait_return_exact_True=True,
            timeout_return_False=True,final_normal_launch_return_bound=True,definitions_not_execution_timestamps=True),
        conditional_route_disposition=[dict(id=x['id'],selected=False,requirements_sha256=digest(x['requirements']),
            accepted_as_derivation=False) for x in conv['conditional_routes']],
        symbolic_service_expression_is_conditional_requirement_not_theorem=True,
        latency_map_is_required_coverage_not_exclusive_measured_partition=True,
        field_dispositions=fields,
        counts=dict(input_pins=len(pins),required_fields=7,insufficient_fields=7,process_phase_joins=20,
            selected_null_join_values=200,phase_categories=9,latency_owners=10,source_files=79,cost_anchors=20,markers=4),
        whole_CPU_seconds_upper=None,whole_wall_seconds_upper=None,resource_obligations_closed=0,execution_count=0)


CHECKS=[
    ('R01','P07 schema, seven fields and P02/P03/P06 dependencies','PASS_DOCUMENTARY_BINDING'),
    ('R02','Twenty group/process/phase joins reconstructed without loss or duplication','PASS_RELATION_ONLY'),
    ('R03','Exact runtime/platform/process/service/unit correspondence','INSUFFICIENT_FOR_ACCEPTANCE'),
    ('R04','Two unselected routes; service expression needs arrival/backlog/readiness theorem','PASS_CONDITIONAL_REQUIREMENT_ONLY'),
    ('R05','Full work/native/runtime or exact-platform WCET derivation','INSUFFICIENT_FOR_ACCEPTANCE'),
    ('R06','CPU-time versus wall-time rates, denied service and latency composition','PASS_REQUIREMENT_ONLY'),
    ('R07','Ten owner requirements; mixed terms split or justified additive overcount','PASS_REQUIREMENT_MAP_ONLY'),
    ('R08','Nine phase/category records with no verified upper or extra reserve','PASS_UNKNOWN_BOUND_RECORDS_ONLY'),
    ('R09','Provider validity, load, retries, signals, interference and liveness','INSUFFICIENT_FOR_ACCEPTANCE'),
    ('R10','Pre-main and post-receipt/pre-parent-tR work required','PASS_REQUIREMENT_ONLY'),
    ('R11','Physical exit not tW; exact True and independent later success qualification','PASS_SOURCE_DEFINITION_ONLY'),
    ('R12','Success finally through normal tF; packet.finish not final return','PASS_REQUIREMENT_ONLY'),
    ('R13','600/90/60 arithmetic versus unproved wall-coverage inequality','PASS_CANDIDATE_ARITHMETIC_ONLY'),
    ('R14','Separate pre/post bounds and 60/750/60+30 zero-transfer account','PASS_CANDIDATE_PRESERVATION_ONLY'),
    ('R15','P02/P03/P06 nonacceptance, P05 negative and P08-P10 absent','PASS_DEPENDENCY_STATE_ONLY'),
    ('R16','Same actor; no independent or custodian acceptance claimed','PASS_PROVENANCE_DISCLOSURE'),
    ('R17','Prior bytes, no execution, no quota changes and no admission','PASS_PRESERVATION_ONLY')]


def review_record(rec):
    o=rd(OUT);task=next(t for t in rd(PLAN)['tasks'] if t['id']=='P07')
    return dict(schema='d5.i166-p07-documentary-review.v1',increment='I166',date='2026-11-15',base_commit=REVIEW_BASE,
        package_id='P07',status='DOCUMENTARY_CONFORMANT_COMPATIBILITY_UNPROVED_E03_E04_OPEN_NOT_ADMITTED',
        subject=o['candidate_binding'],plan_task_sha256=digest(task),input_pins={**rec['input_pins'],RECON:sha(RECON)},
        reconstruction=pin(RECON),
        provenance=dict(reviewer='Codex assistant in same chat; also prepared I165',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,planned_review_role=task['review_role'],
            independent_reviewer_identity=None,independent_acceptance=False,custodian_acceptance=False),
        checks=[dict(id=i,scope=s,result=r,resource_obligation_closed=False) for i,s,r in CHECKS],
        findings=dict(blocking_documentary_defects=[],acceptance_gaps=[
            'No accepted exact runtime/platform/process/clock/service correspondence or compatible units.',
            'No complete transitive whole-window work or justified exact-platform WCET; conversion route unselected.',
            'No bounded IO/children/locks/scheduling/observation or satisfied provider/load/retry/signal/liveness assumptions.',
            'No proved attribution/composition or 600/90/60 worker and separate pre/post coverage bounds.',
            'No independent scheduling/IO/WCET review or competent custodian acceptance.']),
        counts=rec['counts'],field_dispositions=rec['field_dispositions'],
        E03_E04_criterion_disposition=[dict(id=x['id'],obligation=x['obligation'],inherited_result=x['I165_result'],
            I166_result=x['I165_result'],closed=False) for x in o['E03_E04_criterion_disposition']],
        acceptance=dict(documentary_conformance=True,accepted_as_compatible_work_service_or_WCET_proof=False,
            independent_acceptance=False,E03_closed=False,E04_closed=False,resource_obligations_closed=0),
        decision=o['decision'],E06=o['E06'],
        next_evidence_required='Under I132, supply complete work/WCET, exact accepted runtime/platform/unit/service/domain and bounded delays/assumptions with independent/custodian acceptance. No execution authorized; P08 not prepared.',
        work_unit=dict(rollback_files=sorted(NEW_FILES),verification_command='python3 docs/validation/D5-I166-audit.py',
            expected_result='PASS_STATIC_SOURCE_ONLY',runtime_harness='N/A: documentary review only; product and component execution prohibited.',
            over400_lines=True,reason='Self-contained prior semantic validator, fresh reconstruction and pinned review evidence; overage reported.'),
        git_publication=dict(commit_and_push_all_requested=True,publication_does_not_enable_admission=True))


def main():
    validate_preparation()
    rec=reconstruct()
    assert rd(RECON)==rec and rd(NEW_REVIEW)==review_record(rec)
    prior=rd(SEAL)
    preserved={**prior['preserved_published303'],**prior['artifacts'],SEAL:sha(SEAL)}
    seal=rd(NEW_SEAL)
    assert len(preserved)==308 and seal['preserved_published308']==preserved
    assert seal['schema']=='d5.i166-integrity.v1' and seal['base_commit']==REVIEW_BASE and seal['date']=='2026-11-15'
    assert set(seal['artifacts'])==NEW_FILES-{NEW_SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,h in pins.items():assert sha(path)==h,path
    for k in ['compatibility_verified','independent_acceptance','product_or_components_executed','quotas_changed','proposal_enabled','D5_closed']:assert seal[k] is False
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    assert rec['counts']['input_pins']==232 and len(rec['field_dispositions'])==7
    changes=set(git('diff',REVIEW_BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changes==NEW_FILES,changes
    subprocess.check_call(['git','merge-base','--is-ancestor',REVIEW_BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=REVIEW_BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I166',package='P07',documentary_conformance=True,
        accepted_as_compatible_proof=False,insufficient_fields=7,process_phase_joins=20,selected_null_join_values=200,
        prior_published_files_preserved=308,new_files=5,product_or_components_executed=0,quotas_changed=False,
        resource_obligations_closed=0,independent_acceptance=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',
        git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
