#!/usr/bin/env python3
"""I129 read-only documentary audit: AST, JSON, hashes and budget arithmetic.

No candidate/product/component execution, timing/memory measurement, transfer,
resource reservation or schedule simulation. Git inspects publication metadata.
"""
import ast
import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
D='testing/prospective_capture_joint_i122/'
def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pos(n):return n.lineno,n.col_offset

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

def expressions(n,expr):
    want=ast.dump(ast.parse(expr,mode='eval').body,include_attributes=False)
    return sorted([x for x in ast.walk(n) if isinstance(x,ast.expr) and ast.dump(x,include_attributes=False)==want],key=pos)

def main():
    l=rd(P+'D5-I129-cost-coverage-ledger.json');r=rd(P+'D5-I129-F127-02-cost-reserve-review.json');seal=rd(P+'D5-I129-integrity.json')
    base=l['base_commit'];assert base==r['base_commit']==seal['base_commit']=='33dec048f58879b25de13e80f44f9934495c9fc6'
    subprocess.check_call(['git','merge-base','--is-ancestor',base,'HEAD'],cwd=ROOT)
    assert len(seal['preserved_published123'])==123
    for pins in [seal['preserved_published123'],seal['artifacts'],l['input_pins'],r['input_pins']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert P+'D5-I129-integrity.json' not in seal['artifacts']
    expected=set(seal['artifacts'])|{P+'D5-I129-integrity.json'};assert len(expected)==5
    changed=set(git('diff',base,'--name-only').splitlines());untracked=set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed|untracked==expected,(changed,untracked,expected)
    if git('rev-parse','HEAD')!=base:assert not git('diff','HEAD','--name-only')
    for oldseal in ['D5-I128-integrity.json','D5-I127-integrity.json','D5-I126-integrity.json']:
        for p,h in rd(P+oldseal)['artifacts'].items():assert sha(p)==h,p
    for p,h in rd(P+'D5-I119-integrity.json')['inherited_inputs477'].items():assert sha(p)==h,p
    assert sha(r['ledger']['path'])==r['ledger']['sha256']
    c=rd(P+'D5-I128-PLATFORM-CONTRACT-CANDIDATE.json');h=c['heap'];t=c['time']
    assert l['contract_id']==r['contract_id']==c['contract_id']=='PFC126-CANDIDATE-02'
    assert l['markers']==t['normative_markers'] and l['interval_rule']==t['ordered_interval_rule']
    for a in l['source_anchors']:
        n=function(a['path'],a['symbol'])
        if a.get('expression'):n=expressions(n,a['expression'])[a['occurrence']]
        assert (n.lineno,n.col_offset,n.end_lineno)==(a['line'],a['column'],a['end_line'])
        assert hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==a['AST_sha256']
    acts=l['activities'];assert [x['id'] for x in acts]==[f'C{i:02}' for i in range(1,11)]
    assert [x['phase'] for x in acts]==['Tpre','Tpre','Tpre','Tpre','Tworker','Tworker','Tpost','Tpost','Tpost','CROSS_PHASE_ATTRIBUTE_BY_ACTUAL_INTERVAL']
    for row in acts:
        assert row['verified_work_upper'] is None and row['verified_CPU_seconds_upper'] is None and row['verified_wall_seconds_upper'] is None
        assert row['evidence_status']=='SOURCE_COVERAGE_ONLY_NOT_WCET'
    launch=function(D+'capture.py','launch');worker=function(D+'worker.py','main')
    newline=expressions(launch,"write_all(release_write, b'\\n')")[0]
    close=expressions(launch,'os.close(release_write)')[0];wait=expressions(launch,'wait_worker(process)')[0]
    assert pos(newline)<pos(close)<pos(wait)
    release=expressions(worker,"p.verify_release(c.receive_line(releasefd, p.LIMITS['wait_seconds']), lease)")[0]
    load=expressions(worker,"importlib.import_module(entry['runner_module'])")[0]
    assert pos(release)<pos(load)
    # Source-line protocol returns on newline, not on EOF/parent close. This
    # verifies source facts only; no receive/select/write/interleaving is run.
    receiver=ast.unparse(function('testing/prospective_capture/capture.py','receive_line'))
    assert "while b'\\n' not in data" in receiver and 'return strict_json(data)' in receiver
    finalwrite=expressions(launch,'write_all(launchfd, b)')[0]
    packetfinish=expressions(launch,'packet.finish()')[0]
    assert pos(wait)<pos(packetfinish)<pos(finalwrite)<pos(launch.body[-1])
    maintry=next(x for x in launch.body if isinstance(x,ast.Try) and any(isinstance(n,ast.expr) and ast.dump(n,include_attributes=False)==ast.dump(wait,include_attributes=False) for n in ast.walk(ast.Module(body=x.body,type_ignores=[]))))
    assert any(n is finalwrite for stmt in maintry.finalbody for n in ast.walk(stmt))
    wp=l['worker_partition'];assert wp['candidate_CPU']+wp['candidate_IO_child_wait']+wp['candidate_scheduler']==wp['total']==750
    assert not wp['CPU_process_domain_verified'] and not wp['wall_coverage_inequality_verified'] and not wp['CPU_and_delay_bounds_verified']
    assert wp['observation_latency_included_as_obligation']
    read=rd(P+'D5-I122-binding-review.json')['read_schedule'];file=l['file_byte_envelopes']
    assert file['worker_input_bytes']==read['worker_file_read_upper']==266337791
    assert file['coordinator_input_bytes']==read['launcher_file_read_upper']==261485331
    assert file['diagnostic_sum_separate_input_ledgers']==file['worker_input_bytes']+file['coordinator_input_bytes']==527823122
    assert not file['one_shared_budget_or_ledger'] and not file['CPU_seconds_derived'] and not file['phase_split_derived']
    assert len(l['heap_owner_costs'])==11
    for row,old in zip(l['heap_owner_costs'],h['owner_budgets'],strict=True):
        assert row['id']==old['id'] and row['metric']==old['metric'] and row['budget_bytes']==old['candidate_budget_bytes']
        assert row['complete_bound'] is None and row['known_partial_upper']==old['known_partial_upper']
        v=old['known_partial_upper'];assert row['candidate_difference_budget_minus_partial']==(None if v is None else old['candidate_budget_bytes']-v)
        assert row['verified_spare_capacity_bytes'] is None and not row['slack_is_proved']
    reserve=r['reserve_review'];rh=reserve['heap'];rt=reserve['time'];MiB=1048576
    assert rh['owner_baselines']==[x['candidate_budget_bytes'] for x in h['owner_budgets'][:10]]
    assert rh['baseline_sum']==sum(rh['owner_baselines'])==10432*MiB
    assert rh['unassigned_candidate_reserve']==rh['remaining_candidate_reserve']==h['unassigned_requested_reserve_bytes']==832*MiB
    assert rh['allocated_in_I129']==0 and not rh['resource_availability_proved']
    assert rh['baseline_sum']+rh['unassigned_candidate_reserve']==rh['requested_total']==11*1024**3
    assert rh['allocator_H11_budget']==h['owner_budgets'][10]['candidate_budget_bytes']==1024*MiB
    assert rh['requested_total']+rh['allocator_H11_budget']==rh['committed_total']==12*1024**3
    assert rh['H11_not_free_reserve'] and rh['unknown_costs_cannot_consume_reserve_without_bound']
    diagnostic=rh['diagnostic_H04'];assert diagnostic['known_conditional_upper']==h['owner_budgets'][3]['known_partial_upper']
    assert diagnostic['current_owner_budget']==h['owner_budgets'][3]['candidate_budget_bytes']==6442450944
    assert diagnostic['owner_plus_entire_candidate_reserve']==diagnostic['current_owner_budget']+rh['unassigned_candidate_reserve']==7314866176
    assert diagnostic['known_conditional_upper']>diagnostic['owner_plus_entire_candidate_reserve']
    assert not diagnostic['known_model_establishes_fit_even_with_reserve'] and not diagnostic['actual_infeasibility_claimed'] and not diagnostic['allocation_applied']
    assert rt['phase_baselines']==[p['candidate_wall_seconds'] for p in t['phase_budgets']]==[60,750,60]
    assert rt['baseline_sum']==sum(rt['phase_baselines'])==870
    assert rt['allocated_in_I129']==0 and rt['remaining_candidate_reserve']==rt['unassigned_candidate_reserve']==30
    assert rt['baseline_sum']+rt['unassigned_candidate_reserve']==rt['end_to_end_total']==900
    assert not rt['service_availability_proved'] and rt['unknown_or_unbounded_phase_cannot_be_filled_with_reserve']
    nested=rt['nested_worker_rule'];assert nested['base_categories']==[600,90,60] and sum(nested['base_categories'])==nested['base_sum']==750
    assert nested['per_category_reserve']==0 and nested['outer_and_inner_reserve_not_two_credits'] and not nested['existing_category_slack_verified']
    assert all(reserve['cross_domain'].values()) and not reserve['transfers_executed_or_applied'] and not reserve['candidate_contract_modified']
    # Symbolic conservation arithmetic, not numerical allocation experiments.
    def combine(terms):
        out={}
        for name,value in terms:out[name]=out.get(name,0)+value
        return {name:value for name,value in out.items() if value}
    assert combine([('sum_B',1),('sum_x',1),('R_h',1),('sum_x',-1)])=={'sum_B':1,'R_h':1}
    assert combine([('sum_b',1),('sum_y',1),('R_t',1),('sum_y',-1)])=={'sum_b':1,'R_t':1}
    assert combine([('y_worker',-1),('z_CPU',1),('z_IO',1),('z_sched',1)])=={'y_worker':-1,'z_CPU':1,'z_IO':1,'z_sched':1}
    f=r['finding_review'];assert f['id']=='F127-02' and f['review_complete'] and f['source_coverage_clarified']
    assert f['status']=='OPEN_COST_AND_SERVICE_EVIDENCE_RESERVE_RULES_PROPOSED'
    assert not f['cost_upper_bounds_closed'] and not f['reserve_rules_adopted_in_contract'] and not f['phase_success_proved']
    assert f['F127_01_resolution_preserved']==rd(P+'D5-I128-F127-01-resolution.json')['findings']['F127_01']=='RESOLVED_IN_CANDIDATE_CONTRACT_ONLY'
    assert [x['id'] for x in r['findings']]==['F129-01','F129-02'] and all(not x['executed'] for x in r['findings'])
    assert not r['findings'][0]['reopens_F127_01']
    assert all(not x['closed'] for x in r['E01_E05_disposition']) and len(r['E01_E05_disposition'])==5
    for key in ['all_phase_work_and_time_upper_verified','full_heap_upper_verified','source_runtime_or_components_executed','logical_schedule_executed','proposal_enabled','D5_closed']:assert l[key] is False,key
    assert l['unknown_bounds_not_zero'] and l['IR03']=='NOT_READY'
    d=r['decision']
    for key in ['platform_attested','heap_capacity_verified','work_or_CPU_seconds_verified','success_within900_verified','issue_SOURCE_CAPACITY_VERIFIED','product_quotas_changed','source_implementation_changed','product_or_components_executed','logical_schedule_executed','reserve_transfers_applied','resources_reserved','capture_inputs_rebound','authority_or_destination_created','proposal_enabled','capture_enabled','D5_closed','H07_closed']:assert d[key] is False,key
    assert d['PFC126_CANDIDATE_02_bytes_preserved'] and d['markers_tW_exact_True_unchanged'] and d['heap_and_time_budgets_unchanged']
    assert d['resource_obligations_closed']==0 and d['IR03']=='NOT_READY'
    assert d['certificate_unchanged']==rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')['status']=='IMPLEMENTED_NOT_ADMITTED'
    assert c['product_numeric_candidates']==rd(P+'D5-I122-CAPACITY-CONTRACT.json')['numeric_candidates'] and not c['product_numeric_candidates_applied']
    assert r['E06']['components_executed']==0 and not r['E06']['execution_authorized']
    assert r['git_publication']['commit_and_push_all_requested']
    for p in ['docs/validation/D5-JOINT-capture-authorization.json','docs/validation/D5-JOINT-P01','docs/validation/D5-JOINT-P01-launch.json']:assert not (ROOT/p).exists(),p
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',contract=c['contract_id'],F127_02='REVIEWED_OPEN_COST_AND_SERVICE_EVIDENCE',F127_01_preserved=True,cost_rows=10,heap_owners=11,heap_reserve_bytes=rh['remaining_candidate_reserve'],time_reserve_seconds=rt['remaining_candidate_reserve'],reserve_transfers_applied=False,contract_unchanged=True,resource_obligations_closed=0,prior_published_files_preserved=123,new_files=len(expected),product_or_components_executed=0,quotas_changed=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))
if __name__=='__main__':main()
