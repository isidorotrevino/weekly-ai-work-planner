#!/usr/bin/env python3
"""I131 documentary E01-E05 review audit: hashes, AST, JSON pointers/arithmetic.

No candidate/product/component import, live reference probe, resource measurement
or benchmark. Git subprocesses inspect repository publication metadata only.
"""
import ast
import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pointer(value,path):
    for part in path.strip('/').split('/') if path else []:value=value[int(part)] if isinstance(value,list) else value[part.replace('~1','/').replace('~0','~')]
    return value

def function(path,symbol):
    root=ast.parse((ROOT/path).read_text())
    for part in symbol.split('.'):
        found=[]
        def walk(n):
            for c in ast.iter_child_nodes(n):
                if isinstance(c,(ast.ClassDef,ast.FunctionDef)):
                    if c.name==part:found.append(c)
                else:walk(c)
        walk(root);assert len(found)==1,(path,symbol,part);root=found[0]
    return root

def anchor(a):
    n=function(a['path'],a['symbol'])
    if a.get('kind')=='NORMAL_RETURN_AFTER_FINALLY':n=n.body[-1];assert isinstance(n,ast.Return)
    elif a.get('expression'):
        wanted=ast.dump(ast.parse(a['expression'],mode='eval').body,include_attributes=False)
        nodes=sorted([x for x in ast.walk(n) if isinstance(x,ast.expr) and ast.dump(x,include_attributes=False)==wanted],key=lambda x:(x.lineno,x.col_offset));n=nodes[a['occurrence']]
    assert (n.lineno,n.end_lineno)==(a['line'],a['end_line'])
    if 'column'in a:assert n.col_offset==a['column']
    assert hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==a['AST_sha256']

def main():
    r=rd(P+'D5-I131-E01-E05-review.json');d=rd(P+'D5-I131-resource-evidence-delta.json');seal=rd(P+'D5-I131-integrity.json')
    base=r['base_commit'];assert base==d['base_commit']==seal['base_commit']=='51a997ef03d7101d84b75a26ff409c9dd52f0bac'
    subprocess.check_call(['git','merge-base','--is-ancestor',base,'HEAD'],cwd=ROOT)
    assert len(seal['preserved_published133'])==133
    for pins in [seal['preserved_published133'],seal['artifacts'],r['input_pins'],d['input_pins']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert P+'D5-I131-integrity.json' not in seal['artifacts']
    expected=set(seal['artifacts'])|{P+'D5-I131-integrity.json'};assert len(expected)==5
    changed=set(git('diff',base,'--name-only').splitlines());untracked=set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed|untracked==expected,(changed,untracked,expected)
    if git('rev-parse','HEAD')!=base:assert not git('diff','HEAD','--name-only')
    for oldseal in ['D5-I130-integrity.json','D5-I129-integrity.json','D5-I128-integrity.json']:
        for p,h in rd(P+oldseal)['artifacts'].items():assert sha(p)==h,p
    for p,h in rd(P+'D5-I119-integrity.json')['inherited_inputs477'].items():assert sha(p)==h,p
    assert sha(r['contract']['path'])==r['contract']['sha256'] and sha(r['evidence_delta']['path'])==r['evidence_delta']['sha256']
    c=rd(r['contract']['path']);old=rd(P+'D5-I128-PLATFORM-CONTRACT-CANDIDATE.json');ledger=rd(P+'D5-I129-cost-coverage-ledger.json');rules=rd(P+'D5-I130-cost-reserve-rule-incorporation.json')
    assert r['contract_id']==d['candidate_id']==c['contract_id']=='PFC126-CANDIDATE-03'
    def hp(x):return {k:v for k,v in x['heap'].items() if k not in ['reserve_rule','proof_rule']}
    expected_time_keys=['phase_budgets','unassigned_wall_reserve_seconds','success_end_to_end_candidate_seconds','minimum_service_curve','noncopy_work_upper','current_source_watchdog','new_end_to_end_timer_installed','all_phase_bounds_verified','successful_completion_within900_verified','normative_markers','ordered_interval_rule','success_path_qualification','observation_latency_rule','failure_claim','proof_collection_state','forbidden_marker_substitutions']
    assert d['time_projection_keys']==expected_time_keys
    def tp(x):
        out={k:x['time'][k] for k in d['time_projection_keys']};out['worker_service_numeric_and_verification']={k:v for k,v in x['time']['worker_service_partition'].items() if k!='attribution'};return out
    def sp(x):return {p:h for p,h in x['input_pins'].items() if p.startswith('testing/')}
    keys=['id','verified_work_upper','verified_CPU_seconds_upper','verified_wall_seconds_upper','evidence_status'];assert d['activity_projection_keys']==keys
    def ap(rows):return [{k:row[k] for k in keys} for row in rows]
    pairs=[('runtime_identity_reference_and_attestation',old['runtime'],c['runtime']),('heap_numeric_and_evidence',hp(old),hp(c)),('time_markers_numeric_and_evidence',tp(old),tp(c)),('normative_non_admission',old['normative_state'],c['normative_state']),('direct_testing_source_bindings',sp(old),sp(c)),('activity_cost_evidence',ap(ledger['activities']),ap(c['cost_coverage']['activities']))]
    assert len(d['comparisons'])==len(pairs)==6
    for row,(id,left,right) in zip(d['comparisons'],pairs,strict=True):
        assert row['id']==id and left==right and row['equal']
        assert row['left_projection_sha256']==digest(left)==row['right_projection_sha256']==digest(right)
        assert row['left_path'] in d['input_pins'] and row['right_path'] in d['input_pins']
    assert d['selected_projections_equal'] and d['new_rule_sections']==['cost_coverage','reserve_accounting'] and d['new_rule_sections_are_not_resource_proof']
    assert d['new_resource_measurements']==d['new_platform_attestations']==0 and not d['new_positive_resource_proof'] and not d['actual_infeasibility_claimed']
    h=c['heap'];t=c['time'];reserve=c['reserve_accounting'];coverage=c['cost_coverage']
    assert len(h['owner_budgets'])==11 and d['missing_complete_heap_owner_bounds']==sum(x['proof_upper_bytes'] is None for x in h['owner_budgets'])==11
    assert len(coverage['activities'])==10 and d['missing_activity_work_CPU_wall_values']==sum(row[k] is None for row in coverage['activities'] for k in ['verified_work_upper','verified_CPU_seconds_upper','verified_wall_seconds_upper'])==30
    assert d['missing_phase_upper_bounds']==sum(p['verified_upper_seconds'] is None for p in t['phase_budgets'])==3
    assert d['operator_attestation_values_all_null'] and all(v is None for v in c['runtime']['platform_attestation'].values())
    assert not c['runtime']['source_binary_equivalence_verified'] and not c['runtime']['environment_manifest_verified']
    reference=rd(P+'D5-I127-runtime-reference-manifest.json')
    assert reference['interpreter']['sha256']==c['runtime']['required_identity_pins']['interpreter'] and not reference['environment_manifest_verified']
    assert sum(row['candidate_budget_bytes'] for row in h['owner_budgets'][:10])+reserve['heap']['remaining_reserve_bytes']==h['requested_heap_candidate_bytes']==11*1024**3
    assert h['requested_heap_candidate_bytes']+h['allocator_overhead_candidate_bytes']==h['committed_heap_candidate_bytes']==12*1024**3
    assert reserve['heap']['remaining_reserve_bytes']==872415232 and reserve['heap']['allocated_total_bytes']==0
    assert [p['candidate_wall_seconds'] for p in t['phase_budgets']]==[60,750,60]
    assert sum(p['candidate_wall_seconds'] for p in t['phase_budgets'])+reserve['time']['remaining_reserve_seconds']==900
    assert reserve['time']['remaining_reserve_seconds']==30 and reserve['time']['allocated_total_seconds']==reserve['worker_nested']['additional_phase_allocation_seconds']==0
    assert sum(reserve['worker_nested']['base_category_seconds'].values())==750
    assert not reserve['transfers_applied'] and not reserve['resource_availability_verified'] and not reserve['reserve_or_capacity_verified']
    assert coverage['activities'][3]['phase']=='Tpre' and coverage['activities'][8]['phase']=='Tpost'
    assert not coverage['all_activity_bounds_verified'] and not coverage['CPU_wall_coverage_verified'] and coverage['proof_upper_seconds'] is None
    assert t['noncopy_work_upper'] is None and all(t['minimum_service_curve'][k] is None for k in ['rate_unit','rate_lower_bound','latency_upper_seconds'])
    assert not t['minimum_service_curve']['evidence_pins'] and not t['minimum_service_curve']['verified']
    assert t['success_path_qualification']['wait_worker_result_must_be_exact_True'] and t['success_path_qualification']['later_checks_never_move_tW']
    assert t['ordered_interval_rule']['required_order']==['t0','tR','tW','tF'] and not t['success_path_qualification']['False_or_exception_defines_qualified_tW']
    assert all(m['clock_value'] is None for m in t['normative_markers']) and not t['proof_collection_state']['clock_guarantee_verified']
    assert not t['all_phase_bounds_verified'] and not t['successful_completion_within900_verified']
    for a in r['source_anchors']:anchor(a)
    for m in t['normative_markers']:anchor(m['source_anchor'])
    assert r['source_anchors']==c['source_anchors']+coverage['source_anchors']
    obligations=r['obligations'];assert [row['id'] for row in obligations]==['E01','E02','E03','E04','E05']
    assert all(not row['closed'] and row['needed'] and len(row['criteria'])==4 for row in obligations)
    criteria=[row for ob in obligations for row in ob['criteria']];assert len(criteria)==r['criteria_total']==20
    counts={k:sum(row['kind']==k for row in criteria) for k in ['DOCUMENTARY','REFERENCE','RESOURCE']}
    assert counts==r['criterion_counts']==dict(DOCUMENTARY=9,REFERENCE=1,RESOURCE=10)
    assert len({row['id'] for row in criteria})==20
    for row in criteria:
        assert row['result']=={'DOCUMENTARY':'DOCUMENTARY_CONSISTENCY_ONLY','REFERENCE':'HISTORICAL_REFERENCE_ONLY','RESOURCE':'COMPLETE_EVIDENCE_NOT_SUPPLIED'}[row['kind']]
        assert not row['closes_resource_obligation'] and row['references']
        for ref in row['references']:
            assert ref['path'] in r['input_pins']
            assert sha(ref['path'])==ref['sha256']
            assert digest(pointer(rd(ref['path']),ref['json_pointer']))==ref['observed_canonical_sha256']
    assert r['documentary_checks_are_not_resource_closures'] and r['new_normative_inconsistencies_found']==[]
    assert r['finding_disposition']==rules['rule_disposition']
    assert r['finding_disposition']['F127_02']=='RULES_INCORPORATED_COST_AND_SERVICE_EVIDENCE_OPEN'
    assert r['current_reserve_state']==dict(heap_allocated_bytes=0,time_allocated_seconds=0,nested_additional_seconds=0,heap_remaining_candidate_bytes=872415232,time_remaining_candidate_seconds=30,actual_availability_or_service_verified=False)
    assert all(entry['status']=='MISSING' for entry in c['required_evidence'])
    assert not r['E06']['reviewed_in_I131'] and r['E06']['components_executed']==0 and not r['E06']['execution_authorized']
    dec=r['decision']
    for k in ['E01_E05_all_closed','platform_attested','complete_heap_verified','whole_work_WCET_or_service_verified','success_within900_verified','issue_SOURCE_CAPACITY_VERIFIED','product_or_components_executed','source_implementation_changed','product_quotas_changed','reserve_transfers_applied','resources_reserved','runtime_reference_recollected','capture_inputs_rebound','authority_or_destination_created','proposal_enabled','capture_enabled','D5_closed','H07_closed']:assert dec[k] is False,k
    assert dec['candidate03_bytes_unchanged'] and dec['prior_rules_and_F127_01_preserved'] and dec['numeric_budgets_and_quotas_unchanged']
    assert dec['resource_obligations_closed']==0 and dec['IR03']==d['IR03']=='NOT_READY'
    assert dec['certificate_unchanged']==rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')['status']=='IMPLEMENTED_NOT_ADMITTED'
    assert c['product_numeric_candidates']==rd(P+'D5-I122-CAPACITY-CONTRACT.json')['numeric_candidates'] and not c['product_numeric_candidates_applied']
    assert r['git_publication']['commit_and_push_all_requested']
    for p in ['docs/validation/D5-JOINT-capture-authorization.json','docs/validation/D5-JOINT-P01','docs/validation/D5-JOINT-P01-launch.json']:assert not (ROOT/p).exists(),p
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',contract=c['contract_id'],obligations_reviewed=5,criteria=20,documentary_checks=9,historical_reference_checks=1,missing_resource_criteria=10,resource_obligations_closed=0,unchanged_technical_projections=6,contract_unchanged=True,product_or_components_executed=0,quotas_changed=False,reserve_transfers_applied=False,proposal_enabled=False,prior_published_files_preserved=133,new_files=len(expected),D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))
if __name__=='__main__':main()
