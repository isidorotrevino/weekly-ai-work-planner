#!/usr/bin/env python3
"""I133 P01 preparation audit: hashes, JSON, source AST/import edges only.

No target/product/component imports or execution. Git subprocesses inspect
publication metadata. Independent scope acceptance and resource evidence remain pending.
"""
import ast
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
D='testing/prospective_capture_joint_i122/'
def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def function(path,symbol):
    root=ast.parse((ROOT/path).read_text())
    for part in symbol.split('.'):
        found=[]
        def visit(n):
            for x in ast.iter_child_nodes(n):
                if isinstance(x,(ast.ClassDef,ast.FunctionDef)):
                    if x.name==part:found.append(x)
                else:visit(x)
        visit(root);assert len(found)==1,(path,symbol,part);root=found[0]
    return root

def anchor(a):
    n=function(a['path'],a['symbol'])
    if a.get('kind')=='NORMAL_RETURN_AFTER_FINALLY':n=n.body[-1];assert isinstance(n,ast.Return)
    elif a.get('expression'):
        target=ast.dump(ast.parse(a['expression'],mode='eval').body,include_attributes=False)
        matches=sorted([x for x in ast.walk(n) if isinstance(x,ast.expr) and ast.dump(x,include_attributes=False)==target],key=lambda x:(x.lineno,x.col_offset));n=matches[a['occurrence']]
    assert (n.lineno,n.end_lineno)==(a['line'],a['end_line'])
    if 'column'in a:assert n.col_offset==a['column']
    assert hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==a['AST_sha256']

def source_import_superset(seeds):
    def resolve(name):
        parts=name.split('.');out=[]
        for i in range(1,len(parts)+1):
            path='/'.join(parts[:i])+'/__init__.py'
            if (ROOT/path).is_file():out.append(path)
        path='/'.join(parts)+'.py'
        if (ROOT/path).is_file():out.append(path)
        return sorted(set(out))
    pending=list(seeds);pins={};edges=set()
    while pending:
        path=pending.pop()
        if path in pins:continue
        pins[path]=sha(path);tree=ast.parse((ROOT/path).read_text());pkg=path[:-3].replace('/','.').rsplit('.',1)[0]
        for n in ast.walk(tree):
            names=[]
            if isinstance(n,ast.Import):names=[a.name for a in n.names]
            elif isinstance(n,ast.ImportFrom):
                parts=pkg.split('.')
                base='.'.join(parts[:len(parts)-n.level+1]+([n.module] if n.module else [])) if n.level else n.module or ''
                names=[base]+[base+'.'+a.name for a in n.names if a.name!='*']
            for name in names:
                if not name.startswith(('testing.','source_ingest.')):continue
                for dest in resolve(name):
                    edges.add((path,n.lineno,name,dest))
                    if dest not in pins:pending.append(dest)
    return pins,[dict(from_path=a,line=n,module=m,to_path=d) for a,n,m,d in sorted(edges)]

def main():
    s=rd(P+'D5-PFC126-03-RESOURCE-SCOPE.json');r=rd(P+'D5-I133-P01-preparation-review.json');seal=rd(P+'D5-I133-integrity.json')
    base=s['base_commit'];assert base==r['base_commit']==seal['base_commit']=='9268d2fd095be9437e44d45746579260b9df2b80'
    subprocess.check_call(['git','merge-base','--is-ancestor',base,'HEAD'],cwd=ROOT)
    assert len(seal['preserved_published143'])==143
    for pins in [seal['preserved_published143'],seal['artifacts'],s['input_pins'],r['input_pins']]:
        for path,h in pins.items():assert sha(path)==h,path
    assert P+'D5-I133-integrity.json' not in seal['artifacts']
    assert P+'D5-PFC126-03-RESOURCE-SCOPE.json' not in s['input_pins']
    expected=set(seal['artifacts'])|{P+'D5-I133-integrity.json'};assert len(expected)==5
    changed=set(git('diff',base,'--name-only').splitlines());untracked=set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed|untracked==expected,(changed,untracked,expected)
    if git('rev-parse','HEAD')!=base:assert not git('diff','HEAD','--name-only')
    for oldseal in ['D5-I132-integrity.json','D5-I131-integrity.json','D5-I130-integrity.json']:
        for path,h in rd(P+oldseal)['artifacts'].items():assert sha(path)==h,path
    for path,h in rd(P+'D5-I119-integrity.json')['inherited_inputs477'].items():assert sha(path)==h,path
    plan=rd(P+'D5-I132-E01-E05-evidence-plan.json');task=plan['tasks'][0]
    assert task['id']==s['package_id']=='P01' and task['planned_output']==r['output']['path']==P+'D5-PFC126-03-RESOURCE-SCOPE.json'
    assert task['output_schema']==s['schema']==r['output']['schema']=='d5.pfc126-03.resource-scope.v1'
    assert sha(r['output']['path'])==r['output']['sha256'] and r['output']['produced']
    assert sha(s['plan_binding']['path'])==s['plan_binding']['sha256'] and s['plan_binding']['task_record_canonical_sha256']==digest(task)
    assert set(task['required_specific_fields'])<=set(s) and len(task['required_specific_fields'])==8
    assert s['provenance']['producer']['identity']=='Codex assistant preparing I133 in this chat'
    assert s['provenance']['producer']['role']==task['responsible_role']
    assert s['provenance']['reviewer']==dict(identity=None,role=task['review_role'],state='INDEPENDENT_ACCEPTANCE_PENDING')
    assert not s['provenance']['resource_attestation'] and s['provenance']['platform_attestation_validity'] is None
    c=rd(P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json');cb=s['candidate_id_and_sha256']
    assert cb['contract_id']==r['contract_id']==c['contract_id']=='PFC126-CANDIDATE-03' and cb['sha256']==sha(cb['path'])
    assert cb['subject']==c['subject'] and cb['source_revision']=='I122-CANDIDATE-01'
    env=rd(P+'D5-I122-CAPTURE-REGISTRY.json');assert sha(env['base_registry'])==env['base_registry_sha256']
    profile=rd(env['base_registry']);profile.update(env['overrides']);entry=profile['entry']
    sp=s['I122_and_original_source_pin_set'];impl=rd(P+'D5-I122-atomicity-implementation.json')['source_hashes']
    assert sp['candidate_all_six_files']==impl and len(impl)==6
    assert sp['candidate_runtime_sources']=={p:impl[p] for p in [D+'capture.py',D+'atomic.py',D+'worker.py']}
    assert sp['candidate_components_NOT_RUN']=={p:h for p,h in impl.items() if p.endswith(('test_joint_capture.py','run_joint_lab.py'))}
    assert len(sp['candidate_components_NOT_RUN'])==2 and len(sp['candidate_documentation'])==1
    assert not set(sp['candidate_components_NOT_RUN'])&set(sp['observer_static_repo_import_superset']['file_pins'])
    graph=sp['observer_static_repo_import_superset'];pins,edges=source_import_superset(graph['seeds'])
    assert graph['seeds']==[D+'capture.py',D+'atomic.py',D+'worker.py']
    assert pins==graph['file_pins'] and len(pins)==8 and edges==graph['edges']
    assert not graph['is_actual_loaded_runtime_closure']
    assert sp['runner_registered_input_pins']==entry['runner_effective_inputs']
    assert sp['runner_registered_input_count']==len(entry['runner_effective_inputs'])==79
    assert sp['runner_registered_Python_source_count']==sum(p.endswith('.py') for p in entry['runner_effective_inputs'])==71
    ig=sp['original_import_graph'];assert sha(ig['path'])==ig['sha256']
    actual=rd(ig['path'])['outside_root_event_review']['discovery_import_graph']['modules']
    assert ig['module_records']==actual and ig['module_count']==len(actual)==33
    assert ig['unique_source_files']==len({row['path'] for row in actual.values()})==32 and not ig['is_runtime_loaded_manifest']
    for row in actual.values():assert entry['runner_effective_inputs'][row['path']]==row['sha256']
    a=s['321_root_12_group_applicability'];assert a['expected_test_ids']==entry['expected_test_ids']
    assert a['expected_root_count']==len(set(a['expected_test_ids']))==321
    assert a['expected_group_count']==len(a['expected_groups'])==12
    assert dict(Counter(id.split('.')[0] for id in a['expected_test_ids']))==a['expected_groups']==entry['expected_groups'] and sum(a['expected_groups'].values())==321
    ids_hash=hashlib.sha256(json.dumps(sorted(a['expected_test_ids']),separators=(',',':')).encode()).hexdigest()
    assert ids_hash==a['expected_passed_ids_sha256']==entry['expected_passed_ids_sha256']
    assert set(a['method_bindings'])==set(entry['method_bindings'])==set(a['expected_test_ids'])
    cache={}
    for id,row in a['method_bindings'].items():
        assert {k:v for k,v in row.items() if k!='source_AST_sha256'}==entry['method_bindings'][id]
        assert sha(row['path'])==row['sha256']
        if row['path'] not in cache:cache[row['path']]=ast.parse((ROOT/row['path']).read_text())
        nodes=[n for n in ast.walk(cache[row['path']]) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.lineno==row['line'] and n.end_lineno==row['end_line']]
        assert len(nodes)==1 and hashlib.sha256(ast.dump(nodes[0],include_attributes=False).encode()).hexdigest()==row['source_AST_sha256']
    assert a['factory_args_preserved'] and a['source_modes']==dict(Counter(row['mode'] for row in rd(P+'D5-I115-refined-reference-envelope.json')['root_rows']))=={'T_R':88,'DRIVE':30,'ASSERTION_CONTEXT_ONLY':203}
    assert a['causal_inventory_roots']==len(profile['inventory'])==118 and not a['runner']['entrypoint_executed']
    assert a['runner']['path']==entry['runner_path'] and sha(a['runner']['path'])==a['runner']['sha256']==entry['runner_sha256']
    assert a['record_sources']==entry['record_sources'] and a['discovery_patterns']==entry['runner_discovery_patterns']
    assert a['original_source_route_preconditions']==rd(P+'D5-I115-refined-reference-envelope.json')['preconditions']
    prior=rd(P+'D5-I124-global-batch-lifetime-proof.json');assert a['I124_applicability']==prior['scope']
    counts=a['I124_counts_reference'];assert counts['F']==prior['global_F_upper']==52018 and counts['S']==prior['global_S_upper']==1759 and counts['retained_generations']==53778 and counts['not_a_resource_fit_or_runtime_PASS']
    runtime=s['runtime_platform_target_reference'];assert runtime['reference']==c['runtime']
    assert runtime['runtime_target_acceptance_pending']=='P02' and runtime['platform_capacity_service_acceptance_pending']=='P03'
    assert not runtime['target_runtime_closure_attested'] and not runtime['platform_identity_and_service_attested'] and not runtime['new_runtime_probe_or_sampling']
    assert runtime['operator_identity'] is None and runtime['validity_interval'] is None
    heap=s['requested_committed_metrics'];assert heap['owner_budgets']==c['heap']['owner_budgets'] and heap['reserve_accounting']==c['reserve_accounting']
    assert heap['candidate_requested_total_bytes']==11*1024**3 and heap['candidate_committed_total_bytes']==12*1024**3
    assert heap['requested_reserve_bytes']==872415232 and heap['H11_overhead_budget_bytes']==1073741824
    for k in ['actual_complete_requested_upper_bytes','actual_complete_committed_upper_bytes','actual_available_capacity_bytes']:assert heap[k] is None,k
    assert heap['candidate_budget_is_not_proved_demand_or_capacity'] and not heap['committed_allocator_heap']['backend_allocation_correspondence_proven']
    t=s['t0_tR_tW_tF_and_qualified_success'];ct=c['time']
    for sk,ck in [('clock','clock'),('markers','normative_markers'),('ordered_interval_rule','ordered_interval_rule'),('success_qualification','success_path_qualification'),('failure_claim','failure_claim'),('observation_latency_rule','observation_latency_rule'),('forbidden_substitutions','forbidden_marker_substitutions'),('candidate_phase_budgets','phase_budgets'),('worker_partition','worker_service_partition'),('watchdog','current_source_watchdog')]:assert t[sk]==ct[ck],sk
    assert t['cost_coverage']==c['cost_coverage'] and t['candidate_end_to_end_seconds']==900 and t['unassigned_time_reserve_seconds']==30
    assert not t['timestamps_collected'] and not t['clock_or_service_verified'] and not t['success_within900_verified']
    assert s['source_anchors']==c['source_anchors']+c['cost_coverage']['source_anchors']
    for x in s['source_anchors']:anchor(x)
    for m in t['markers']:anchor(m['source_anchor'])
    policy=s['non_execution_and_zero_transfer_policy'];assert policy['numeric_candidates']==c['product_numeric_candidates']==rd(P+'D5-I122-CAPACITY-CONTRACT.json')['numeric_candidates']
    true_policy={'no_missing_resource_bound_coerced_to_zero','zero_allocation_is_documentary_not_runtime_usage'}
    numeric_policy={'numeric_candidates','heap_reserve_allocated_bytes','time_reserve_allocated_seconds','nested_time_allocated_seconds'}
    assert all(policy[k] is True for k in true_policy)
    assert all(policy[k]==0 for k in numeric_policy-{'numeric_candidates'})
    assert all(v is False for k,v in policy.items() if k not in true_policy|numeric_policy)
    accept=s['acceptance_state'];assert accept['P01_output_prepared'] and accept['source_hashes_and_321_binding_intervals_prepared'] and accept['scope_metrics_and_markers_defined']
    assert not accept['independent_review_accepted'] and not accept['P02_P03_evidence_obtained'] and accept['resource_obligations_closed']==0
    for k in ['complete_heap_verified','CPU_service_verified','success_within900_verified','issue_SOURCE_CAPACITY_VERIFIED','proposal_enabled','capture_enabled','D5_closed','H07_closed']:assert accept[k] is False,k
    assert r['independent_review']['accepted'] is False and r['independent_review']['reviewer_identity'] is None and r['independent_review']['no_independent_review_fabricated']
    assert all(r['preparation_checks'].values()) and r['counts']['observer_repo_import_files']==8 and r['counts']['source_bindings']==321
    assert len(r['package_progress'])==len(plan['tasks'])==20
    for progress,planned in zip(r['package_progress'],plan['tasks'],strict=True):
        assert progress['package_id']==planned['id'] and progress['planned_output']==planned['planned_output']
        if planned['id']=='P01':assert progress['output_created'] and progress['sha256']==sha(planned['planned_output']) and progress['status']=='P01_PREPARED_INDEPENDENT_ACCEPTANCE_PENDING'
        else:assert not progress['output_created'] and progress['sha256'] is None and progress['status']=='NOT_STARTED_NO_OUTPUT' and not (ROOT/planned['planned_output']).exists()
    assert not r['E01_E05_closed'] and r['E06']['components_executed']==0 and not r['E06']['execution_authorized']
    d=r['decision']
    for k in ['resource_evidence_or_platform_attestation_produced','product_or_components_executed','source_implementation_changed','product_quotas_changed','reserve_transfers_applied','resources_reserved','runtime_reference_recollected','capture_inputs_rebound','authority_or_destination_created','issue_SOURCE_CAPACITY_VERIFIED','proposal_enabled','capture_enabled','D5_closed','H07_closed']:assert d[k] is False,k
    assert d['resource_obligations_closed']==0 and d['candidate03_and_plan_bytes_preserved'] and d['prior_marker_cost_reserve_rules_preserved']
    assert d['certificate_unchanged']==accept['certificate_unchanged']==rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')['status']=='IMPLEMENTED_NOT_ADMITTED'
    assert d['IR03']==accept['IR03']=='NOT_READY' and r['git_publication']['commit_and_push_all_requested']
    for path in ['docs/validation/D5-JOINT-capture-authorization.json','docs/validation/D5-JOINT-P01','docs/validation/D5-JOINT-P01-launch.json']:assert not (ROOT/path).exists(),path
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',package='P01',output_prepared=True,independent_acceptance=False,roots=321,groups=12,method_AST_bindings=321,registered_runner_inputs=79,observer_static_import_files=8,other_packages_started=0,prior_published_files_preserved=143,new_files=len(expected),product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))
if __name__=='__main__':main()
