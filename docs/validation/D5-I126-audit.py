#!/usr/bin/env python3
"""I126 source-only documentary audit, usable before/staged/after Git commit.

No product/candidate/component imports or execution. Checks candidate budget
arithmetic and no-admission flags, not runtime resource fit or execution PASS.
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
def node(path,symbol):
    root=ast.parse((ROOT/path).read_text())
    for part in symbol.split('.'):
        found=[]
        def visit(n):
            for c in ast.iter_child_nodes(n):
                if isinstance(c,(ast.ClassDef,ast.FunctionDef)):
                    if c.name==part:found.append(c)
                else:visit(c)
        visit(root);assert len(found)==1,(symbol,part);root=found[0]
    return root

def main():
    c=rd(P+'D5-I126-PLATFORM-CONTRACT-CANDIDATE.json');r=rd(P+'D5-I126-platform-candidate-review.json');seal=rd(P+'D5-I126-integrity.json')
    base=c['base_commit'];assert base==r['base_commit']==seal['base_commit']=='50c49678568bae2abeefbe5fec0285f26c628283'
    subprocess.check_call(['git','merge-base','--is-ancestor',base,'HEAD'],cwd=ROOT)
    assert len(seal['preserved_prior_local108'])==108
    for pins in [seal['preserved_prior_local108'],seal['artifacts'],c['input_pins']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert sha(r['contract']['path'])==r['contract']['sha256']
    assert P+'D5-I126-integrity.json' not in seal['artifacts']
    expected=set(seal['preserved_prior_local108'])|set(seal['artifacts'])|{P+'D5-I126-integrity.json'}
    # Base diff includes committed AND staged additions. Before staging, files
    # are untracked instead. No historical HEAD/untracked assumption is edited.
    changed=set(git('diff',base,'--name-only').splitlines())
    untracked=set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed|untracked==expected,(len(changed),len(untracked),len(expected))
    assert len(expected)==113
    if git('rev-parse','HEAD')!=base:
        assert not git('diff','HEAD','--name-only'),'publication audit requires clean committed bytes'
    for old in ['D5-I125-integrity.json','D5-I124-integrity.json','D5-I123-integrity.json','D5-I122-integrity.json']:
        for p,h in rd(P+old)['artifacts'].items():assert sha(p)==h,p
    for p,h in rd(P+'D5-I119-integrity.json')['inherited_inputs477'].items():assert sha(p)==h,p
    for a in c['source_anchors']:
        n=node(a['path'],a['symbol'])
        assert (n.lineno,n.end_lineno)==(a['line'],a['end_line'])
        assert hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==a['AST_sha256']
    assert c['status']=='DRAFT_FOR_REVIEW_NOT_ATTESTED_NOT_ADMITTED'
    n=c['normative_state'];assert n['candidate_review_only']
    for k in ['operator_attested','accepted','enforced','resources_reserved','active_limits_changed','implementation_modified','execution_authorized','component_execution_authorized','capture_authorized','proposal_enabled','D5_closed']:assert n[k] is False,k
    assert n['IR03']=='NOT_READY'
    h=c['heap'];MiB=1048576;terms=h['owner_budgets']
    assert [x['id'] for x in terms]==[f'H{i:02}' for i in range(1,12)]
    assert [x['candidate_budget_bytes']//MiB for x in terms]==[256,2048,512,6144,128,256,256,512,192,128,1024]
    assert all(x['candidate_budget_bytes']%MiB==0 for x in terms)
    old=rd(P+'D5-I125-complete-heap-review.json')['required_terms']
    for x,y in zip(terms,old,strict=True):
        assert x['owner']==y['owner'] and x['proof_upper_bytes'] is None
        assert x['status']=='UNPROVED' and x['budget_kind']=='PROPOSED_NOT_APPLIED_NOT_ATTESTED'
        assert not x['evidence_pins'] and not x['known_partial_is_complete_term']
        assert x['known_partial_upper']==y['known_partial_upper'] and x['known_partial_unit']==y['known_partial_unit']
    requested=sum(x['candidate_budget_bytes'] for x in terms[:10]);reserve=h['unassigned_requested_reserve_bytes']
    assert requested==h['requested_owner_budget_bytes']==10938744832
    assert reserve==832*MiB and requested+reserve==h['requested_heap_candidate_bytes']==11*1024**3
    assert terms[10]['candidate_budget_bytes']==h['allocator_overhead_candidate_bytes']==1024*MiB
    assert h['requested_heap_candidate_bytes']+h['allocator_overhead_candidate_bytes']==h['committed_heap_candidate_bytes']==12*1024**3
    assert h['complete_requested_upper_bytes'] is None and h['complete_committed_upper_bytes'] is None and h['host_total_capacity_bytes'] is None
    assert not h['all_owner_bounds_verified'] and not h['capacity_attested']
    assert terms[3]['known_partial_upper']>terms[3]['candidate_budget_bytes']
    assert not r['H04_model_establishes_candidate_fit'] and not r['H04_actual_infeasibility_claimed']
    t=c['time'];phases=t['phase_budgets']
    assert [x['id'] for x in phases]==['Tpre','Tworker','Tpost']
    assert [x['candidate_wall_seconds'] for x in phases]==[60,750,60]
    assert all(x['verified_upper_seconds'] is None and not x['evidence_pins'] for x in phases)
    assert sum(x['candidate_wall_seconds'] for x in phases)+t['unassigned_wall_reserve_seconds']==t['success_end_to_end_candidate_seconds']==900
    assert t['unassigned_wall_reserve_seconds']==30
    w=t['worker_service_partition']
    assert [w[k] for k in ['candidate_CPU_upper_seconds','candidate_IO_child_wait_upper_seconds','candidate_scheduler_and_blocking_upper_seconds']]==[600,90,60]
    assert 600+90+60==phases[1]['candidate_wall_seconds']
    for k in ['CPU_upper_verified','IO_child_wait_upper_verified','scheduler_upper_verified']:assert w[k] is False,k
    curve=t['minimum_service_curve'];assert curve['rate_lower_bound'] is None and curve['latency_upper_seconds'] is None and not curve['verified'] and not curve['evidence_pins']
    assert t['noncopy_work_upper'] is None
    for k in ['new_end_to_end_timer_installed','all_phase_bounds_verified','successful_completion_within900_verified']:assert t[k] is False,k
    watchdog=t['current_source_watchdog'];assert watchdog['seconds']==900 and watchdog['unchanged'] and not watchdog['proves_successful_completion']
    actual=rd(P+'D5-I122-CAPACITY-CONTRACT.json')['numeric_candidates']
    assert c['product_numeric_candidates']==actual and not c['product_numeric_candidates_applied']
    assert actual['campaign_seconds']==900 and len(actual)==24
    runtime=c['runtime'];assert runtime['observed_reference']==rd(P+'D5-I124-resource-admission-review.json')['runtime_metadata_observed_without_candidate']
    assert runtime['required_identity_pins']['interpreter']==runtime['observed_reference']['interpreter_binary']['sha256']
    assert all(v is None for k,v in runtime['required_identity_pins'].items() if k!='interpreter')
    assert all(v is None for v in runtime['platform_attestation'].values())
    assert not runtime['source_binary_equivalence_verified'] and not runtime['environment_manifest_verified']
    assert [x['id'] for x in c['required_evidence']]==[f'E{i:02}' for i in range(1,7)]
    assert all(x['status']=='MISSING' for x in c['required_evidence'])
    assert c['historical_I125_no_contract_reply_preserved'] and c['contract_candidate_is_not_retroactive_I125_attestation']
    assert rd(P+'D5-I125-resource-admission-decision.json')['user_platform_contract_reply']['answer']=='No; dejar dictamen de no admisión'
    assert rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')['status']==r['current_certificate']=='IMPLEMENTED_NOT_ADMITTED'
    assert r['prior_local_files_preserved']==108 and r['git_commit_push_requested']
    assert r['git_execution_status']=='VERIFY_FROM_GIT_AFTER_OPERATION_NOT_SELF_ATTESTED'
    for k in ['resource_proof_complete','platform_attested','source_implementation_changed','product_quotas_changed','product_or_components_executed','certificate_modified','proposal_enabled','capture_enabled','D5_closed','H07_closed']:assert r[k] is False,k
    assert r['components_executed']==0 and r['IR03']=='NOT_READY' and r['I125_no_admission_preserved']
    assert c['git_publication']['commit_and_push_all_changes_requested']
    for p in ['docs/validation/D5-JOINT-capture-authorization.json','docs/validation/D5-JOINT-P01','docs/validation/D5-JOINT-P01-launch.json']:assert not (ROOT/p).exists(),p
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',contract=c['contract_id'],requested_heap_candidate_bytes=h['requested_heap_candidate_bytes'],committed_heap_candidate_bytes=h['committed_heap_candidate_bytes'],end_to_end_candidate_seconds=900,budgets_applied=False,platform_attested=False,proposal_enabled=False,prior_files_preserved=108,publication_file_count=len(expected),product_or_components_executed=0,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))
if __name__=='__main__':main()
