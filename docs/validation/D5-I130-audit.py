#!/usr/bin/env python3
"""I130 documentary audit: candidate-rule deltas, AST, hashes and arithmetic.

No product/candidate/component execution, reserve transfer, schedule simulation
or resource probe. Git subprocesses inspect publication metadata only.
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
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

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

def check_anchor(a):
    n=function(a['path'],a['symbol'])
    if a.get('kind')=='NORMAL_RETURN_AFTER_FINALLY':n=n.body[-1];assert isinstance(n,ast.Return)
    elif a.get('expression'):
        wanted=ast.dump(ast.parse(a['expression'],mode='eval').body,include_attributes=False)
        nodes=sorted([x for x in ast.walk(n) if isinstance(x,ast.expr) and ast.dump(x,include_attributes=False)==wanted],key=lambda x:(x.lineno,x.col_offset))
        n=nodes[a['occurrence']]
    assert (n.lineno,n.end_lineno)==(a['line'],a['end_line'])
    if 'column' in a:assert n.col_offset==a['column']
    assert hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==a['AST_sha256']

def main():
    c=rd(P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json');r=rd(P+'D5-I130-cost-reserve-rule-incorporation.json');seal=rd(P+'D5-I130-integrity.json')
    base=c['base_commit'];assert base==r['base_commit']==seal['base_commit']=='e3f8dc292b6f8bda24ccf04bc3d54bdeede5058d'
    subprocess.check_call(['git','merge-base','--is-ancestor',base,'HEAD'],cwd=ROOT)
    assert len(seal['preserved_published128'])==128
    for pins in [seal['preserved_published128'],seal['artifacts'],c['input_pins'],r['input_pins']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert P+'D5-I130-integrity.json' not in seal['artifacts']
    expected=set(seal['artifacts'])|{P+'D5-I130-integrity.json'};assert len(expected)==5
    changed=set(git('diff',base,'--name-only').splitlines());untracked=set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed|untracked==expected,(changed,untracked,expected)
    if git('rev-parse','HEAD')!=base:assert not git('diff','HEAD','--name-only')
    for oldseal in ['D5-I129-integrity.json','D5-I128-integrity.json','D5-I127-integrity.json']:
        for p,h in rd(P+oldseal)['artifacts'].items():assert sha(p)==h,p
    for p,h in rd(P+'D5-I119-integrity.json')['inherited_inputs477'].items():assert sha(p)==h,p
    old=rd(P+'D5-I128-PLATFORM-CONTRACT-CANDIDATE.json');review=rd(P+'D5-I129-F127-02-cost-reserve-review.json');ledger=rd(P+'D5-I129-cost-coverage-ledger.json')
    assert sha(r['contract']['path'])==r['contract']['sha256']
    assert c['contract_id']==r['contract']['id']=='PFC126-CANDIDATE-03' and c['schema']=='d5.i130-platform-contract-candidate.v3'
    assert c['predecessor']==r['predecessor'] and c['predecessor']['contract_id']==old['contract_id']=='PFC126-CANDIDATE-02'
    assert c['predecessor']['sha256']==sha(c['predecessor']['path']) and c['predecessor']['revision']==3 and c['predecessor']['bytes_preserved']
    assert c['inherited_amendments']==[old['amendment']]
    changes={k for k in c.keys()|old.keys() if c.get(k)!=old.get(k)}
    assert changes=={'schema','contract_id','increment','base_commit','authority','input_pins','heap','time','required_evidence','predecessor','amendment','inherited_amendments','cost_coverage','reserve_accounting'},changes
    for k in r['unchanged_top_level_sections']:assert c[k]==old[k],k
    for p,h in old['input_pins'].items():assert c['input_pins'][p]==h,p
    added={P+'D5-I128-PLATFORM-CONTRACT-CANDIDATE.json',P+'D5-I128-F127-01-resolution.json',P+'D5-I128-integrity.json',P+'D5-I129-cost-coverage-ledger.json',P+'D5-I129-F127-02-cost-reserve-review.json',P+'D5-I129-integrity.json'}
    assert set(c['input_pins'])-set(old['input_pins'])==added
    a=c['amendment'];assert a['finding']=='F127-02' and a['status']=='COST_AND_RESERVE_RULES_INCORPORATED_EVIDENCE_OPEN'
    assert sha(a['review_path'])==a['review_sha256'] and sha(a['ledger_path'])==a['ledger_sha256']
    assert a['F127_01_resolution_preserved'] and a['does_not_close_E01_E05'] and a['does_not_change_product_or_quotas']
    h=c['heap'];oh=old['heap'];t=c['time'];ot=old['time']
    assert {k for k in h if h[k]!=oh[k]}=={'reserve_rule','proof_rule'}
    assert h.keys()==oh.keys()
    assert {k for k in t if t[k]!=ot[k]}=={'worker_service_partition','service_rule'} and t.keys()==ot.keys()
    assert {k:v for k,v in t['worker_service_partition'].items() if k!='attribution'}=={k:v for k,v in ot['worker_service_partition'].items() if k!='attribution'}
    assert t['worker_service_partition']['attribution'].startswith(ot['worker_service_partition']['attribution'])
    for marker in t['normative_markers']:check_anchor(marker['source_anchor'])
    assert t['normative_markers']==ot['normative_markers'] and t['ordered_interval_rule']==ot['ordered_interval_rule']
    assert t['success_path_qualification']==ot['success_path_qualification'] and t['observation_latency_rule']==ot['observation_latency_rule']
    assert t['success_path_qualification']['wait_worker_result_must_be_exact_True'] and t['success_path_qualification']['later_checks_never_move_tW']
    coverage=c['cost_coverage'];assert coverage['status']=='NORMATIVE_CANDIDATE_RULES_NOT_VERIFIED_COSTS'
    assert sha(coverage['basis']['path'])==coverage['basis']['sha256']
    assert coverage['source_anchors']==ledger['source_anchors'] and coverage['interval_rule']==ot['ordered_interval_rule']
    assert len(coverage['activities'])==10
    for row,prior in zip(coverage['activities'],ledger['activities'],strict=True):
        assert {k:v for k,v in row.items() if k not in ['requirement','candidate_rule_only']}==prior
        assert row['requirement']=='REQUIRED_COVERAGE_UNPROVED' and row['candidate_rule_only']
        assert row['verified_work_upper'] is None and row['verified_CPU_seconds_upper'] is None and row['verified_wall_seconds_upper'] is None
    assert coverage['activities'][3]['id']=='C04' and coverage['activities'][3]['phase']=='Tpre'
    assert coverage['activities'][8]['id']=='C09' and coverage['activities'][8]['phase']=='Tpost'
    for anchor in coverage['source_anchors']+c['source_anchors']:check_anchor(anchor)
    assert not coverage['all_activity_bounds_verified'] and not coverage['CPU_wall_coverage_verified'] and not coverage['executed_or_measured'] and coverage['proof_upper_seconds'] is None
    reserve=c['reserve_accounting'];rh=reserve['heap'];rt=reserve['time'];nested=reserve['worker_nested']
    assert reserve['status']=='NORMATIVE_CANDIDATE_RULES_NO_TRANSFER_APPLIED'
    assert rh['eligible_owner_ids']==[x['id'] for x in h['owner_budgets'][:10]]
    assert rh['owner_baseline_bytes']=={x['id']:x['candidate_budget_bytes'] for x in h['owner_budgets'][:10]}
    assert set(rh['allocation_bytes'])==set(rh['eligible_owner_ids']) and all(type(v) is int and v==0 for v in rh['allocation_bytes'].values())
    assert rh['allocated_total_bytes']==sum(rh['allocation_bytes'].values())==0
    assert rh['reserve_baseline_bytes']==rh['remaining_reserve_bytes']==h['unassigned_requested_reserve_bytes']==872415232
    assert sum(rh['owner_baseline_bytes'].values())+rh['remaining_reserve_bytes']==rh['requested_total_bytes']==h['requested_heap_candidate_bytes']==11*1024**3
    assert rh['allocator_H11_bytes']==h['allocator_overhead_candidate_bytes']==1073741824
    assert rh['requested_total_bytes']+rh['allocator_H11_bytes']==rh['committed_total_bytes']==h['committed_heap_candidate_bytes']==12*1024**3
    assert rh['rule']['conservation']=='sum(B_i_new)+R_heap_new=11811160064'
    assert rh['rule']['reserve_update']=='R_heap_new=872415232-sum(x_i)'
    assert rh['rule']['owner_update']=='B_i_new=B_i+x_i'
    assert rt['phase_ids']==[x['id'] for x in t['phase_budgets']]==['Tpre','Tworker','Tpost']
    assert rt['phase_baseline_seconds']=={x['id']:x['candidate_wall_seconds'] for x in t['phase_budgets']}
    assert set(rt['allocation_seconds'])==set(rt['phase_ids']) and all(type(v) is int and v==0 for v in rt['allocation_seconds'].values())
    assert rt['allocated_total_seconds']==sum(rt['allocation_seconds'].values())==0
    assert rt['reserve_baseline_seconds']==rt['remaining_reserve_seconds']==t['unassigned_wall_reserve_seconds']==30
    assert sum(rt['phase_baseline_seconds'].values())+rt['remaining_reserve_seconds']==rt['end_to_end_total_seconds']==t['success_end_to_end_candidate_seconds']==900
    assert rt['rule']['conservation']=='sum(phase_new)+R_time_new=900' and rt['rule']['reserve_update']=='R_time_new=30-sum(y)'
    assert nested['base_category_seconds']==dict(CPU=600,IO_child_wait=90,scheduler=60)
    assert nested['base_total_seconds']==sum(nested['base_category_seconds'].values())==rt['phase_baseline_seconds']['Tworker']==750
    assert all(type(v) is int and v==0 for v in nested['additional_category_allocation_seconds'].values())
    assert sum(nested['additional_category_allocation_seconds'].values())==nested['additional_phase_allocation_seconds']==nested['category_reserve_seconds']==0
    assert nested['allocation_constraint']=='z_CPU+z_IO+z_scheduler=y_worker'
    assert nested['updated_category_sum']=='750+sum(z)' and nested['updated_phase_budget']=='750+y_worker' and not nested['category_slack_verified']
    assert len(reserve['transition_requirements'])==4
    for k in ['resource_availability_verified','reserve_or_capacity_verified','transfers_applied','resources_reserved','product_quotas_changed']:assert reserve[k] is False,k
    # Symbolic conservation only: do not apply or simulate reserve allocations.
    def add(items):
        out={}
        for name,v in items:out[name]=out.get(name,0)+v
        return {k:v for k,v in out.items() if v}
    assert add([('sum_B',1),('sum_x',1),('R_h',1),('sum_x',-1)])=={'sum_B':1,'R_h':1}
    assert add([('sum_b',1),('sum_y',1),('R_t',1),('sum_y',-1)])=={'sum_b':1,'R_t':1}
    assert add([('base_worker',1),('sum_z',1),('base_worker',-1),('y_worker',-1)])=={'sum_z':1,'y_worker':-1}
    for i,(entry,prior) in enumerate(zip(c['required_evidence'],old['required_evidence'],strict=True)):
        assert entry['id']==prior['id'] and entry['status']==prior['status']=='MISSING'
        if i in [0,5]:assert entry==prior
        else:assert entry['description']!=prior['description']
    assert all(x['proof_upper_bytes'] is None for x in h['owner_budgets']) and not h['all_owner_bounds_verified'] and not h['capacity_attested']
    assert all(p['verified_upper_seconds'] is None for p in t['phase_budgets']) and not t['all_phase_bounds_verified'] and not t['successful_completion_within900_verified']
    assert not t['minimum_service_curve']['verified'] and t['minimum_service_curve']['rate_lower_bound'] is None
    for p,x in r['source_basis'].items():
        if p.endswith('_path'):assert sha(x)==r['source_basis'][p.replace('_path','_sha256')]
    assert r['source_basis']['actual_new_cost_measurements']==0 and r['source_basis']['activities_preserved']==10 and r['source_basis']['heap_owners_preserved']==11
    assert r['rule_disposition']['F127_02']=='RULES_INCORPORATED_COST_AND_SERVICE_EVIDENCE_OPEN'
    assert r['rule_disposition']['F127_01']=='RESOLVED_IN_CANDIDATE_CONTRACT_ONLY_PRESERVED'
    assert r['E01_E05_disposition']==review['E01_E05_disposition'] and all(not e['closed'] for e in r['E01_E05_disposition'])
    d=r['decision']
    for k in ['cost_evidence_closed','platform_attested','complete_heap_verified','full_work_service_or_WCET_verified','success_within900_verified','issue_SOURCE_CAPACITY_VERIFIED','product_quotas_changed','source_implementation_changed','product_or_components_executed','reserve_transfers_applied','resources_reserved','clock_or_schedule_measured','capture_inputs_rebound','authority_or_destination_created','proposal_enabled','capture_enabled','D5_closed','H07_closed']:assert d[k] is False,k
    assert d['predecessors_bytes_preserved'] and d['F127_01_markers_and_qualification_preserved'] and d['numeric_heap_time_budgets_preserved'] and d['rule_adopted_in_candidate_only']
    assert d['resource_obligations_closed']==0 and d['IR03']==c['normative_state']['IR03']=='NOT_READY'
    assert d['certificate_unchanged']==rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')['status']=='IMPLEMENTED_NOT_ADMITTED'
    assert c['product_numeric_candidates']==rd(P+'D5-I122-CAPACITY-CONTRACT.json')['numeric_candidates'] and not c['product_numeric_candidates_applied']
    assert r['E06']['components_executed']==0 and not r['E06']['execution_authorized'] and r['git_publication']['commit_and_push_all_requested']
    for p in ['docs/validation/D5-JOINT-capture-authorization.json','docs/validation/D5-JOINT-P01','docs/validation/D5-JOINT-P01-launch.json']:assert not (ROOT/p).exists(),p
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',contract=c['contract_id'],I129_rules_incorporated=True,F127_01_preserved=True,F127_02='RULES_INCORPORATED_EVIDENCE_OPEN',cost_rows=10,heap_owners=11,allocated_heap_bytes=0,allocated_time_seconds=0,numeric_budgets_unchanged=True,product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,proposal_enabled=False,prior_published_files_preserved=128,new_files=len(expected),D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))
if __name__=='__main__':main()
