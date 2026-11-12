#!/usr/bin/env python3
"""I137 P03 documentary audit: JSON, hashes, Git blobs, source AST and arithmetic.

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

def main():
    o=rd(OUT);r=rd(REVIEW);seal=rd(P+'D5-I137-integrity.json');c=rd(CONTRACT);s=rd(SCOPE);p02=rd(RUNTIME);p02r=rd(RUNTIME_REVIEW);plan=rd(PLAN);task=plan['tasks'][2]
    assert o['base_commit']==r['base_commit']==seal['base_commit']==BASE
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    prior=rd(P+'D5-I136-integrity.json');preserved={**prior['preserved_published158'],**prior['artifacts'],P+'D5-I136-integrity.json':sha(P+'D5-I136-integrity.json')}
    assert len(preserved)==163 and seal['preserved_published163']==preserved
    for pins in [preserved,seal['artifacts'],o['input_pins'],r['input_pins'],rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for path,h in pins.items():assert sha(path)==h,path
    expected={OUT,REVIEW,P+'D5-I137-audit.py',P+'D5-I137-integrity.json','docs/design/D5-I137-P03-PLATFORM-ENVELOPE.md'}
    assert set(seal['artifacts'])|{P+'D5-I137-integrity.json'}==expected and len(seal['artifacts'])==4
    assert set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())==expected
    if git('rev-parse','HEAD')!=BASE:assert not git('diff','HEAD','--name-only')
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
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I137',package='P03',preparation_complete=True,accepted_as_platform_evidence=False,insufficient_fields=7,missing_delay_bounds=8,unknown_platform_service_fields=35,prior_published_files_preserved=163,new_files=5,product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))
if __name__=='__main__':main()
