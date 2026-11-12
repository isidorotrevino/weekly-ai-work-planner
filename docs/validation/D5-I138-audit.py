#!/usr/bin/env python3
"""I138 P03 review audit: historical consistency plus fresh lexical/Git reconstruction.

Never import/build/launch product or components, collect platform data, allocate
resources or apply quotas. PASS validates an explicitly insufficient dossier.
"""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
BASE='8566fb37220722879f3ec98de296787b6224b162'
OUT=P+'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
REVIEW=P+'D5-I137-P03-preparation-review.json'
PLAN=P+'D5-I132-E01-E05-evidence-plan.json'
CONTRACT=P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
SCOPE=P+'D5-PFC126-03-RESOURCE-SCOPE.json'
RUNTIME=P+'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
RUNTIME_REVIEW=P+'D5-I136-P02-documentary-review.json'
OLD_TIME=P+'D5-I125-900-second-review.json'
UNKNOWN_FIELDS={
'platform_runtime_pin_set_and_validity':['platform_identity','target_runtime_pin_set','kernel_configuration_pin_set','process_service_domain_identity','attested_validity_interval'],
'available_worker_requested_and_committed_heap':['available_requested_heap_bytes','available_committed_heap_bytes','availability_validity_interval','allocator_backend_metric_correspondence'],
'coordinator_child_resource_and_interference_scope':['complete_process_resource_mapping','coordinator_memory_upper_bytes','child_memory_upper_bytes','joint_host_capacity_bytes','isolation_and_interference_guarantees'],
'compatible_CPU_service_unit_rate_latency_or_WCET_assumptions':['selected_proof_route','compatible_work_unit','guaranteed_service_rate_unit','guaranteed_service_rate_lower_bound','service_latency_upper_seconds','service_window_and_process_domain','exact_platform_WCET_environment','justified_WCET_upper_seconds'],
'bounded_scheduler_locks_IO_child_completion_observation_delays':['aggregate_delay_upper_seconds','complete_delay_coverage_evidence'],
'admissible_signal_retry_interference_and_load_assumptions':['signal_model_and_bound','retry_count_and_backoff_bounds','competing_workload_envelope','process_concurrency_and_arrival_limits','IO_filesystem_device_load_envelope','assumption_enforcement_and_validity'],
'clock_monotonicity_domain_and_latency_accounting':['actual_clock_implementation','actual_clock_domain_identity','monotonicity_units_rate_resolution_evidence','cross_process_service_domain_mapping','latency_accounting_compatibility_evidence']}
PROJECTIONS=[(CONTRACT,'/runtime/platform_attestation'),(CONTRACT,'/time/minimum_service_curve'),(CONTRACT,'/heap/host_total_capacity_bytes'),(CONTRACT,'/heap/capacity_attested'),(CONTRACT,'/time/worker_service_partition'),(CONTRACT,'/time/current_source_watchdog'),(RUNTIME,'/acceptance'),(RUNTIME_REVIEW,'/acceptance'),(OLD_TIME,'/missing_platform_evidence'),(OLD_TIME,'/user_platform_contract_reply'),(SCOPE,'/worker_heap_vs_other_process_scope')]
def rd(path):return json.loads((ROOT/path).read_text())
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pointer(document,path):
    v=document
    for part in path.strip('/').split('/'):
        key=part.replace('~1','/').replace('~0','~');v=v[int(key)] if isinstance(v,list) else v[key]
    return v

def bound_inputs(pins):
    paths=sorted(pins);stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=''.join(BASE+':'+p+'\n' for p in paths).encode()));data={};checks=[]
    for path in paths:
        h=stream.readline().decode().split();assert len(h)==3 and h[1]=='blob',path
        size=int(h[2]);body=stream.read(size);assert len(body)==size and stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==pins[path]==sha(path),path
        data[path]=body;checks.append(dict(path=path,git_blob_oid=h[0],bytes=size,sha256=pins[path]))
    assert not stream.read()
    projections=[]
    for path,ptr in PROJECTIONS:
        value=pointer(json.loads(data[path]),ptr);projections.append(dict(path=path,sha256=pins[path],json_pointer=ptr,observed_value=value,canonical_sha256=digest(value),resource_obligation_closed=False))
    return data,dict(commit=BASE,pin_count=len(checks),blob_checks=checks,projections=projections,reference_only_no_platform_attestation=True)

def check_anchors(rows,data):
    trees={}
    for row in rows:
        path=row['path']
        if path not in trees:trees[path]=ast.parse(data[path].decode())
        matches=[n for n in ast.walk(trees[path]) if hasattr(n,'lineno') and n.lineno==row['line'] and n.end_lineno==row['end_line'] and ('column' not in row or n.col_offset==row['column']) and hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==row['AST_sha256']]
        assert len(matches)==1,(path,row.get('symbol'),row['line'])

def validate_preparation():
    o=rd(OUT);r=rd(REVIEW);seal=rd(P+'D5-I137-integrity.json');c=rd(CONTRACT);s=rd(SCOPE);p02=rd(RUNTIME);p02r=rd(RUNTIME_REVIEW);plan=rd(PLAN);task=plan['tasks'][2]
    assert o['base_commit']==r['base_commit']==seal['base_commit']==BASE
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    prior=rd(P+'D5-I136-integrity.json');preserved={**prior['preserved_published158'],**prior['artifacts'],P+'D5-I136-integrity.json':sha(P+'D5-I136-integrity.json')}
    assert len(preserved)==163 and seal['preserved_published163']==preserved
    for pins in [preserved,seal['artifacts'],o['input_pins'],r['input_pins'],rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for path,h in pins.items():assert sha(path)==h,path
    data,source_review=bound_inputs(o['input_pins']);assert o['source_evidence_review']==source_review and len(source_review['projections'])==11 and len(o['input_pins'])==130
    assert task['id']==o['package_id']=='P03' and task['planned_output']==OUT and task['output_schema']==o['schema']=='d5.pfc126-03.e04-platform-envelope.v1'
    assert o['plan_binding']==dict(path=PLAN,sha256=sha(PLAN),package_id='P03',task_record_canonical_sha256=digest(task))
    assert o['candidate_binding']==dict(path=CONTRACT,sha256=sha(CONTRACT),contract_id=c['contract_id'],subject=c['subject'],source_revision='I122-CANDIDATE-01')
    assert o['status']=='PREPARED_EXTERNAL_EVIDENCE_BLOCK_PLATFORM_NOT_ATTESTED_NOT_ADMITTED'
    assert list(UNKNOWN_FIELDS)==task['required_specific_fields'] and len(UNKNOWN_FIELDS)==7
    unknowns=[]
    for field,names in UNKNOWN_FIELDS.items():
        for name in names:assert o[field][name] is None,(field,name);unknowns.append('/'+field+'/'+name)
        assert o[field]['evidence_status']=='INSUFFICIENT_FOR_ACCEPTANCE' and not o[field]['verified']
    assert o['unknown_field_register']==unknowns and len(unknowns)==35
    assert o['platform_runtime_pin_set_and_validity']['inherited_reference']==c['runtime']
    heap=o['available_worker_requested_and_committed_heap']
    assert heap['metric']==c['heap']['metric'] and heap['worker_metric_definitions']==s['requested_committed_metrics']
    assert heap['candidate_requested_bytes']==11811160064==c['heap']['requested_heap_candidate_bytes']
    assert heap['candidate_committed_bytes']==12884901888==c['heap']['committed_heap_candidate_bytes']
    assert heap['fit_result']=='NOT_EVALUABLE_NO_DEMAND_OR_AVAILABILITY_PROOF' and not heap['budget_is_available_capacity']
    assert o['coordinator_child_resource_and_interference_scope']['declared_process_scope']==s['worker_heap_vs_other_process_scope']
    cpu=o['compatible_CPU_service_unit_rate_latency_or_WCET_assumptions']
    assert not cpu['rate_derived_from_budget_or_frequency'] and not cpu['service_from_ordinary_quota_or_watchdog']
    assert cpu['candidate_worker_partition']==c['time']['worker_service_partition'] and len(cpu['conditional_acceptance_requirements'])==5
    delay=o['bounded_scheduler_locks_IO_child_completion_observation_delays'];assert len(delay['delay_requirements'])==8
    for row in delay['delay_requirements']:
        assert set(row['candidate_activity_ids'])<=set(x['id'] for x in c['cost_coverage']['activities'])
        assert row['upper_seconds'] is None and row['evidence_pins']=={} and not row['verified'] and row['required_process_scope'] and row['candidate_activity_ids']
    clock=o['clock_monotonicity_domain_and_latency_accounting']
    assert clock['required_clock']==c['time']['clock'] and clock['markers']==c['time']['normative_markers'] and clock['ordered_interval_rule']==c['time']['ordered_interval_rule']
    assert clock['success_qualification']==c['time']['success_path_qualification'] and clock['failure_claim']==c['time']['failure_claim']
    assert clock['attribution_rules']=={k:c['cost_coverage'][k] for k in ['attribution_rule','pre_tR_worker_rule','finally_rule','observation_rule','CPU_wall_rule','noncopy_rule','input_byte_rule']}
    assert not clock['timestamps_collected'] and not clock['latency_coverage_verified']
    targets=o['unchanged_candidate_targets']
    assert targets['heap']==c['heap'] and targets['time']==c['time'] and targets['reserve_accounting']==c['reserve_accounting'] and targets['cost_activities']==c['cost_coverage']['activities']
    assert targets['numeric_candidates']==c['product_numeric_candidates'] and targets['source_watchdog_not_success_guarantee']==c['time']['current_source_watchdog']
    assert sum(x['candidate_budget_bytes'] for x in c['heap']['owner_budgets'][:10])+872415232==11811160064
    assert 11811160064+1073741824==12884901888 and sum(x['candidate_wall_seconds'] for x in c['time']['phase_budgets'])+30==900 and 600+90+60==750
    assert c['reserve_accounting']['heap']['allocated_total_bytes']==c['reserve_accounting']['time']['allocated_total_seconds']==0
    assert all(x['proof_upper_bytes'] is None for x in c['heap']['owner_budgets']) and all(x['verified_upper_seconds'] is None for x in c['time']['phase_budgets'])
    assert len(c['cost_coverage']['activities'])==10
    for row in c['cost_coverage']['activities']:
        for key in ['verified_work_upper','verified_CPU_seconds_upper','verified_wall_seconds_upper']:assert row[key] is None
    assert o['source_anchors']==c['source_anchors']+c['cost_coverage']['source_anchors']+rd(OLD_TIME)['anchors'];check_anchors(o['source_anchors'],data)
    assert not p02['acceptance']['accepted_as_runtime_identity'] and not p02r['acceptance']['accepted_as_runtime_identity']
    deps=o['dependencies'];assert [x['id'] for x in deps]==task['depends_on']==['P01','P02']
    for dep,path in zip(deps,[SCOPE,RUNTIME],strict=True):assert dep['path']==path and dep['sha256']==sha(path) and not dep['accepted_for_resource_closure']
    assert deps[0]['technical_source_scope_conformance'] and deps[0]['independent_acceptance_pending'] and deps[1]['runtime_evidence_insufficient']
    auth=o['producer_authority_signature_and_validity']
    assert auth['preparer_identity']=='Codex assistant preparing I137 in this chat' and auth['required_platform_authority_role']==task['responsible_role'] and auth['required_reviewer_role']==task['review_role']
    for key in ['platform_authority_identity','authority_record','signature','trust_anchor','signed_artifact_sha256','validity_interval','independent_reviewer_identity']:assert auth[key] is None,key
    assert not auth['preparer_is_platform_authority'] and not auth['independent_acceptance']
    assert len(o['field_assessment'])==7 and [x['field'] for x in o['field_assessment']]==task['required_specific_fields']
    for row in o['field_assessment']:assert row['result']=='INSUFFICIENT_FOR_ACCEPTANCE' and not row['resource_obligation_closed'] and row['reason'] and row['required_pre_existing_material']
    e=rd(P+'D5-I131-E01-E05-review.json')['obligations']
    assert o['criterion_disposition']==[dict(id=x['id'],inherited_result=x['result'],I137_result=x['result'],closed=False) for obligation in e if obligation['id'] in ['E01','E02','E04','E05'] for x in obligation['criteria']]
    assert o['acceptance']==dict(rule=task['acceptance'],rejection_rule=task['rejection'],preparation_complete=True,accepted_as_platform_evidence=False,resource_obligations_closed=0,E01_E05_closed=False,early_stop_applied=True,non_fit_proved=False)
    assert o['external_material_review']['authenticated_platform_materials_supplied']==[] and not o['external_material_review']['global_absence_claimed'] and not o['external_material_review']['external_contacts_made']
    assert o['early_stop']['rule']==plan['early_stop_rules'][1] and not o['early_stop']['later_closure_promised']
    assert o['early_stop']['external_evidence_block_recorded'] and o['early_stop']['insufficiency_does_not_prove_infeasibility'] and not o['early_stop']['P04_P05_P06_P07_P08_P09_P10_started']
    assert o['non_execution_and_zero_transfer_policy']==s['non_execution_and_zero_transfer_policy']
    assert r['output']==dict(path=OUT,sha256=sha(OUT),schema=o['schema'],produced=True,evidence_kind=o['evidence_kind']) and r['input_pins'][OUT]==sha(OUT)
    assert all(r['preparation_checks'].values()) and r['status']=='P03_PREPARATION_COMPLETE_INSUFFICIENT_PLATFORM_EVIDENCE_NO_ADMISSION'
    assert r['counts']==dict(required_fields=7,insufficient_fields=7,unknown_platform_service_fields=35,missing_delay_bounds=8,evidence_projections=11,preserved_criteria=16,other_unproduced_packages=17,source_anchors=len(o['source_anchors']),input_pins=len(o['input_pins']))
    assert r['independent_review']==dict(accepted=False,reviewer_identity=None,no_independent_review_fabricated=True)
    assert len(r['package_progress'])==len(plan['tasks'])==20
    for progress,planned in zip(r['package_progress'],plan['tasks'],strict=True):
        exists=planned['id'] in ['P01','P02','P03']
        assert progress['package_id']==planned['id'] and progress['path']==planned['planned_output'] and progress['output_created']==exists
        assert (ROOT/planned['planned_output']).exists()==exists and progress['sha256']==(sha(planned['planned_output']) if exists else None)
    for d in [o['decision'],r['decision']]:
        assert d['certificate_unchanged']==rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')['status']=='IMPLEMENTED_NOT_ADMITTED' and d['IR03']=='NOT_READY' and d['resource_obligations_closed']==0
        true_keys={'candidate_plan_P01_P02_and_source_bytes_preserved','numeric_candidates_unchanged','P0_D1_D4_I1_I20_A52_unchanged','global_gaps_and_real_obligations_pending','I86_I89_I92_not_resumed'}
        for key in true_keys:assert d[key] is True,key
        for key,value in d.items():
            if key not in true_keys|{'certificate_unchanged','IR03','resource_obligations_closed'}:assert value is False,key
    assert o['E06']==dict(status='SEPARATE_PENDING_NOT_RUN',components_executed=0,execution_authorized=False)==r['E06']
    for path in [P+'D5-JOINT-capture-authorization.json',P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:assert not (ROOT/path).exists(),path
    assert seal['source_only'] and not seal['proposal_enabled'] and r['git_publication']['commit_and_push_all_requested']

REVIEW_BASE='3b34ca56606cd759bbcd1398f5aa9d276a473365'
NEW_REVIEW=P+'D5-I138-P03-documentary-review.json'
RECON=P+'D5-I138-P03-source-reconstruction.json'
def read_blobs(commit,paths):
    paths=list(paths);stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=''.join(commit+':'+p+'\n' for p in paths).encode()));data={}
    for path in paths:
        header=stream.readline().decode().split();assert len(header)==3 and header[1]=='blob'
        size=int(header[2]);body=stream.read(size);assert len(body)==size and stream.read(1)==b'\n';data[path]=(header[0],body)
    assert not stream.read();return data

def reconstruct():
    published=read_blobs(REVIEW_BASE,[OUT])[OUT];o=json.loads(published[1]);assert hashlib.sha256(published[1]).hexdigest()==sha(OUT)
    inputs=read_blobs(o['base_commit'],sorted(o['input_pins']));checks=[]
    for path,h in sorted(o['input_pins'].items()):
        oid,body=inputs[path];assert hashlib.sha256(body).hexdigest()==h==sha(path)
        checks.append(dict(path=path,preparation_git_blob_oid=oid,sha256=h,bytes=len(body)))
    projections=[]
    assert [(x['path'],x['json_pointer']) for x in o['source_evidence_review']['projections']]==PROJECTIONS
    for row in o['source_evidence_review']['projections']:
        value=pointer(json.loads(inputs[row['path']][1]),row['json_pointer'])
        assert row['observed_value']==value and row['canonical_sha256']==digest(value) and row['sha256']==o['input_pins'][row['path']]
        projections.append(dict(path=row['path'],json_pointer=row['json_pointer'],sha256=row['sha256'],recomputed_canonical_sha256=digest(value),matches_published_projection=True))
    indices={};trees={}
    def anchor(row):
        path=row['path']
        if path not in trees:
            tree=ast.parse(inputs[path][1].decode());trees[path]=tree;index={}
            class Lexical(ast.NodeVisitor):
                def __init__(self):self.names=[]
                def record(self,n):
                    self.names.append(n.name);index.setdefault('.'.join(self.names),[]).append(n);self.generic_visit(n);self.names.pop()
                visit_ClassDef=record
                visit_FunctionDef=record
                visit_AsyncFunctionDef=record
            Lexical().visit(tree);indices[path]=index
        definitions=indices[path][row['symbol']];assert len(definitions)==1,(path,row['symbol']);node=definitions[0]
        if row.get('expression'):
            expected=ast.dump(ast.parse(row['expression'],mode='eval').body,include_attributes=False)
            matches=sorted([n for n in ast.walk(node) if isinstance(n,ast.expr) and ast.dump(n,include_attributes=False)==expected],key=lambda n:(n.lineno,n.col_offset))
            node=matches[row.get('occurrence',0)]
        elif row.get('kind')=='NORMAL_RETURN_AFTER_FINALLY':node=node.body[-1];assert isinstance(node,ast.Return)
        assert (node.lineno,node.end_lineno)==(row['line'],row['end_line']) and ('column' not in row or node.col_offset==row['column'])
        h=hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest();assert h==row['AST_sha256']
        return dict(path=path,symbol=row['symbol'],line=node.lineno,column=node.col_offset,end_line=node.end_lineno,node_type=type(node).__name__,AST_sha256=h,lexical_symbol_and_expression_match=True)
    annotations=[anchor(row) for row in o['source_anchors']]
    marker_checks=[dict(marker=m['id'],anchor=anchor(m['source_anchor']),clock_value=m['clock_value']) for m in o['clock_monotonicity_domain_and_latency_accounting']['markers']]
    wait=indices['testing/prospective_capture_typed/capture.py']['wait_worker'][0]
    calls=[n for n in ast.walk(wait) if isinstance(n,ast.Call) and ast.unparse(n.func)=='process.wait'];assert len(calls)==1
    assert {k.arg:ast.unparse(k.value) for k in calls[0].keywords}=={'timeout':'limit'}
    true_returns=[n for n in ast.walk(wait) if isinstance(n,ast.Return) and isinstance(n.value,ast.Constant) and n.value.value is True]
    false_returns=[n for n in ast.walk(wait) if isinstance(n,ast.Return) and isinstance(n.value,ast.Constant) and n.value.value is False]
    assert len(true_returns)==len(false_returns)==1
    timeouts=[n for n in ast.walk(wait) if isinstance(n,ast.ExceptHandler) and ast.unparse(n.type)=='c.subprocess.TimeoutExpired'];assert len(timeouts)==1
    launch=indices['testing/prospective_capture_joint_i122/capture.py']['launch'][0]
    assert len([n for n in ast.walk(launch) if isinstance(n,ast.Call) and ast.unparse(n.func)=='wait_worker'])==1
    assert isinstance(launch.body[-1],ast.Return) and ast.unparse(launch.body[-1].value)=='context'
    # All evidence remains source-only: the contract, rather than execution,
    # qualifies exact True and later success checks and covers denied service.
    gaps=[]
    for field,names in UNKNOWN_FIELDS.items():
        for name in names:
            assert o[field][name] is None;gaps.append('/'+field+'/'+name)
    for i,row in enumerate(o['bounded_scheduler_locks_IO_child_completion_observation_delays']['delay_requirements']):
        assert row['upper_seconds'] is None;gaps.append('/bounded_scheduler_locks_IO_child_completion_observation_delays/delay_requirements/'+str(i)+'/upper_seconds')
    for key in ['platform_authority_identity','authority_record','signature','trust_anchor','signed_artifact_sha256','validity_interval','independent_reviewer_identity']:
        assert o['producer_authority_signature_and_validity'][key] is None;gaps.append('/producer_authority_signature_and_validity/'+key)
    assert len(gaps)==len(set(gaps))==50
    c=json.loads(inputs[CONTRACT][1]);h=c['heap'];t=c['time']
    arithmetic=dict(requested_owner_sum_bytes=sum(x['candidate_budget_bytes'] for x in h['owner_budgets'] if x['id']!='H11'),unassigned_requested_reserve_bytes=h['unassigned_requested_reserve_bytes'],requested_total_bytes=h['requested_heap_candidate_bytes'],H11_bytes=h['allocator_overhead_candidate_bytes'],committed_total_bytes=h['committed_heap_candidate_bytes'],phase_sum_seconds=sum(x['candidate_wall_seconds'] for x in t['phase_budgets']),unassigned_wall_reserve_seconds=t['unassigned_wall_reserve_seconds'],end_to_end_candidate_seconds=t['success_end_to_end_candidate_seconds'],worker_category_sum_seconds=sum(t['worker_service_partition'][k] for k in ['candidate_CPU_upper_seconds','candidate_IO_child_wait_upper_seconds','candidate_scheduler_and_blocking_upper_seconds']),arithmetic_only_not_capacity_or_service=True)
    assert arithmetic['requested_owner_sum_bytes']+arithmetic['unassigned_requested_reserve_bytes']==arithmetic['requested_total_bytes']
    assert arithmetic['requested_total_bytes']+arithmetic['H11_bytes']==arithmetic['committed_total_bytes']
    assert arithmetic['phase_sum_seconds']+arithmetic['unassigned_wall_reserve_seconds']==arithmetic['end_to_end_candidate_seconds']==900
    assert arithmetic['worker_category_sum_seconds']==750
    delay_rows=[]
    for row in o['bounded_scheduler_locks_IO_child_completion_observation_delays']['delay_requirements']:
        assert row['unit']=='wall_seconds' and not row['verified'] and row['evidence_pins']=={}
        activity=[x for x in c['cost_coverage']['activities'] if x['id'] in row['candidate_activity_ids']]
        assert len(activity)==len(set(row['candidate_activity_ids']))
        delay_rows.append(dict(id=row['id'],record_canonical_sha256=digest(row),candidate_activity_phases={x['id']:x['phase'] for x in activity},requirement_not_bounded_service=True))
    return dict(preparation_commit=o['base_commit'],published_commit=REVIEW_BASE,P03_published_blob_oid=published[0],P03_sha256=sha(OUT),input_pin_count=len(checks),input_pin_checks=checks,projection_count=len(projections),projection_checks=projections,source_anchor_records=len(annotations),source_anchor_checks=annotations,marker_checks=marker_checks,all_anchor_lexical_symbols_match=True,wait_source_has_timeout_True_and_TimeoutExpired_False=True,launch_unique_wait_and_final_normal_return=True,documented_unknown_pointers=gaps,documented_unknown_count=len(gaps),main_field_unknown_count=35,delay_unknown_count=8,authority_unknown_count=7,unknown_list_is_not_exhaustive_missing_platform_inventory=True,arithmetic=arithmetic,delay_requirement_checks=delay_rows,field_record_sha256={field:digest(o[field]) for field in UNKNOWN_FIELDS},source_only_not_execution_or_actor_independence=True,platform_capacity_service_or_time_verified=False)

def main():
    validate_preparation()
    z=rd(RECON);r=rd(NEW_REVIEW);seal=rd(P+'D5-I138-integrity.json');o=rd(OUT);plan=rd(PLAN);task=plan['tasks'][2]
    assert z['base_commit']==r['base_commit']==seal['base_commit']==REVIEW_BASE
    subprocess.check_call(['git','merge-base','--is-ancestor',REVIEW_BASE,'HEAD'],cwd=ROOT)
    prior=rd(P+'D5-I137-integrity.json');preserved={**prior['preserved_published163'],**prior['artifacts'],P+'D5-I137-integrity.json':sha(P+'D5-I137-integrity.json')}
    assert seal['preserved_published168']==preserved and len(preserved)==168
    for pins in [preserved,seal['artifacts'],z['input_pins'],r['input_pins']]:
        for path,h in pins.items():assert sha(path)==h,path
    expected={NEW_REVIEW,RECON,P+'D5-I138-audit.py',P+'D5-I138-integrity.json','docs/design/D5-I138-P03-PLATFORM-ENVELOPE-REVIEW.md'}
    assert set(seal['artifacts'])|{P+'D5-I138-integrity.json'}==expected and len(seal['artifacts'])==4
    assert set(git('diff',REVIEW_BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())==expected
    if git('rev-parse','HEAD')!=REVIEW_BASE:assert not git('diff','HEAD','--name-only')
    assert z['reconstruction']==reconstruct()
    assert z['reconstruction']['input_pin_count']==130 and z['reconstruction']['source_anchor_records']==41
    assert r['contract_id']==z['contract_id']==o['candidate_binding']['contract_id']=='PFC126-CANDIDATE-03'
    assert r['P03']==dict(path=OUT,sha256=sha(OUT),bytes_preserved=True)
    assert r['plan_binding']==o['plan_binding'] and r['source_reconstruction']==dict(path=RECON,sha256=sha(RECON))
    assert r['status']=='REVIEW_COMPLETE_DOSSIER_CONFORMANT_PLATFORM_EVIDENCE_REJECTED_NO_ADMISSION'
    assert r['field_disposition']==[dict(field=x['field'],I137_result=x['result'],I138_result='CONFIRMED_INSUFFICIENT_FOR_PLATFORM_ACCEPTANCE',record_canonical_sha256=digest(o[x['field']]),closed=False) for x in o['field_assessment']]
    assert len(r['checks'])==14 and [x['id'] for x in r['checks']]==['R%02d'%i for i in range(1,15)]
    for check in r['checks']:assert check['result']=='CONFORMANT_DOCUMENTARY_INSUFFICIENCY_JUDGMENT' and not check['resource_obligation_closed']
    assert r['blocking_dossier_defects']==[] and r['documentary_dossier_conformance'] and not r['P03_change_required']
    assert r['reviewer']['same_assistant_as_preparer'] and r['reviewer']['methodologically_separate_reconstruction'] and not r['reviewer']['actor_or_organizational_independence_attested'] and not r['reviewer']['platform_authority_claimed']
    assert r['acceptance']==dict(review_completed=True,insufficiency_judgment_confirmed=True,accepted_as_platform_evidence=False,independent_documentary_acceptance=False,independent_reviewer_identity=None,E01_E05_closed=False,E04_E05_closed=False,resource_obligations_closed=0,non_fit_proved=False)
    assert r['criterion_disposition']==[dict(id=x['id'],I138_result=x['inherited_result'],closed=False) for x in o['criterion_disposition']]
    assert r['counts']==dict(P03_input_pins_checked=130,evidence_projections_checked=11,source_anchor_records_checked=41,marker_anchors_checked=4,required_fields=7,main_unknown_values=35,missing_delay_bounds=8,missing_authority_values=7,documented_unknown_values=50,criteria_preserved=16,checks=14,other_unproduced_packages=17)
    assert r['other_packages_started']==0 and r['E06']==o['E06'] and r['decision']==o['decision']
    assert r['independent_acceptance_of_P01_P02_P03_not_obtained']
    assert seal['source_only'] and not seal['proposal_enabled'] and r['git_publication']['commit_and_push_all_requested']
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I138',package='P03',documentary_dossier_conformance=True,accepted_as_platform_evidence=False,independent_acceptance=False,Git_input_pins_checked=130,evidence_projections=11,source_anchor_records=41,marker_anchors=4,insufficient_fields=7,missing_delay_bounds=8,prior_published_files_preserved=168,new_files=5,product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))
if __name__=='__main__':main()
