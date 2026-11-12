#!/usr/bin/env python3
"""I127 documentary audit: AST/JSON/hash/arithmetic, no target execution.

--check-local-reference additionally reads referenced local files; never loads
or executes them. Default verifies the portable historical reference record.
"""
import ast
import hashlib
import json
import subprocess
import sys
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
    assert sys.argv[1:] in [[],['--check-local-reference']]
    strict=bool(sys.argv[1:]);r=rd(P+'D5-I127-E01-E05-review.json');m=rd(P+'D5-I127-runtime-reference-manifest.json');seal=rd(P+'D5-I127-integrity.json')
    base=r['base_commit'];assert base==m['base_commit']==seal['base_commit']=='42d69b558b615aae95fd226596775c752f5143f9'
    subprocess.check_call(['git','merge-base','--is-ancestor',base,'HEAD'],cwd=ROOT)
    assert len(seal['preserved_published113'])==113
    for pins in [seal['preserved_published113'],seal['artifacts'],r['input_pins']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert P+'D5-I127-integrity.json' not in seal['artifacts']
    expected=set(seal['artifacts'])|{P+'D5-I127-integrity.json'};assert len(expected)==5
    changed=set(git('diff',base,'--name-only').splitlines());untracked=set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed|untracked==expected,(changed,untracked,expected)
    if git('rev-parse','HEAD')!=base:assert not git('diff','HEAD','--name-only')
    old=rd(P+'D5-I126-integrity.json')
    for p,h in {**old['preserved_prior_local108'],**old['artifacts']}.items():assert sha(p)==h,p
    for p,h in rd(P+'D5-I119-integrity.json')['inherited_inputs477'].items():assert sha(p)==h,p
    c=rd(P+'D5-I126-PLATFORM-CONTRACT-CANDIDATE.json');assert c['contract_id']==r['contract_id']=='PFC126-CANDIDATE-01'
    assert m['interpreter']['sha256']==c['runtime']['required_identity_pins']['interpreter'] and m['matches_I126_interpreter_pin']
    assert len(m['stdlib_file_references'])==12 and len(m['extension_references'])==5
    file_rows=[m['interpreter']]+m['stdlib_file_references']+[p for row in m['extension_references'] for p in row['external_file_candidates']]
    assert len(file_rows)==15
    for row in file_rows:
        assert isinstance(row['bytes'],int) and row['bytes']>0 and len(row['sha256'])==64 and all(x in '0123456789abcdef' for x in row['sha256'])
        if strict:
            path=Path(row['path']);assert path.stat().st_size==row['bytes'],path
            assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256'],path
    classification={x['name']:(x['declared_builtin'],len(x['external_file_candidates'])) for x in m['extension_references']}
    assert classification=={'_json':(True,0),'_hashlib':(False,1),'_multiprocessing':(False,1),'_struct':(True,0),'_posixsubprocess':(True,0)}
    assert all(not x['selection_or_loaded_module_proved'] and x['absence_of_file_is_not_absence_of_builtin'] for x in m['extension_references'])
    if strict:
        assert Path(sys.executable).resolve()==Path(m['interpreter']['path'])
        for row in m['extension_references']:assert row['declared_builtin']==(row['name'] in sys.builtin_module_names)
    for k in ['operator_attested','loaded_module_closure_complete','environment_manifest_verified','host_capacity_verified','product_or_components_executed','proposal_enabled','D5_closed']:assert m[k] is False,k
    assert not m['kernel_label']['is_kernel_binary_pin']
    for a in r['source_anchors']:
        n=function(a['path'],a['symbol'])
        if a['expression']:n=expressions(n,a['expression'])[a['occurrence']]
        assert (n.lineno,n.col_offset,n.end_lineno)==(a['line'],a['column'],a['end_line'])
        assert hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==a['AST_sha256']
    obligations=r['obligations'];assert [x['id'] for x in obligations]==['E01','E02','E03','E04','E05']
    assert all(not x['closed'] and x['still_required'] and x['acceptance'] for x in obligations)
    assert [x['status'] for x in obligations]==['PARTIAL_REFERENCE_ONLY_NOT_ATTESTED','COMPLETE_HEAP_FIT_NOT_DEMONSTRATED','KERNEL_WORK_ONLY_FULL_PHASE_WORK_MISSING','NO_ATTESTED_SERVICE_OR_LATENCY','ARITHMETIC_CHECKED_ENDPOINT_CLARIFICATION_REQUIRED_NO_TIME_PROOF']
    for row,oldrow in zip(r['heap_owner_review'],c['heap']['owner_budgets'],strict=True):
        assert row['id']==oldrow['id'] and row['owner']==oldrow['owner']
        assert row['candidate_budget_bytes']==oldrow['candidate_budget_bytes']
        assert row['complete_verified_upper_bytes'] is None and not row['complete_fit_verified'] and not row['capacity_attested']
        v=oldrow['known_partial_upper'];budget=oldrow['candidate_budget_bytes']
        assert row['known_partial_upper']==v and row['known_partial_unit']==oldrow['known_partial_unit']
        assert row['partial_minus_budget']==(None if v is None else v-budget)
        assert row['partial_remaining_budget_bytes']==(None if v is None else budget-v)
    rows={x['id']:x for x in r['heap_owner_review']}
    assert rows['H04']['known_partial_upper']>rows['H04']['candidate_budget_bytes']
    assert rows['H08']['partial_remaining_budget_bytes']==4195330
    assert rows['H09']['partial_remaining_budget_bytes']==67108864
    assert rows['H10']['partial_remaining_budget_bytes']==71303168
    a=r['arithmetic_verified'];h=c['heap'];t=c['time']
    assert a['requested_owner_bytes']==sum(x['candidate_budget_bytes'] for x in h['owner_budgets'][:10])==10938744832
    assert a['requested_owner_bytes']+a['requested_reserve_bytes']==a['requested_total_bytes']==11*1024**3
    assert a['requested_total_bytes']+a['allocator_overhead_bytes']==a['committed_total_bytes']==12*1024**3
    assert a['phase_seconds']==[60,750,60] and a['unassigned_wall_reserve_seconds']==30
    assert sum(a['phase_seconds'])+a['unassigned_wall_reserve_seconds']==a['total_wall_seconds']==900
    assert a['worker_partition_seconds']==[600,90,60] and sum(a['worker_partition_seconds'])==a['worker_total_seconds']==750 and a['arithmetic_only']
    assert all(x['proof_upper_bytes'] is None for x in h['owner_budgets'])
    assert all(x['verified_upper_seconds'] is None for x in t['phase_budgets'])
    assert t['minimum_service_curve']['rate_lower_bound'] is None and t['minimum_service_curve']['latency_upper_seconds'] is None
    assert not t['minimum_service_curve']['verified'] and not t['minimum_service_curve']['evidence_pins']
    assert all(x['CPU_and_wall_bound'] is None for x in r['phase_source_map'])
    proof=rd(P+'D5-I124-global-batch-lifetime-proof.json')
    assert r['inherited_results']==dict(F=proof['global_F_upper'],S=proof['global_S_upper'],retained_generations=proof['lifetime_envelope']['metadata_generations_including_initial_upper'],clone_visits=proof['kernel_work']['clone_visits_upper'],not_CPU_seconds=True)
    assert [f['id'] for f in r['findings']]==['F127-01','F127-02']
    f=r['findings'][0];assert not f['logical_model_executed'] and f['proposed_order']=='t0<=tR<=tW<=tF'
    assert f['proposed_intervals']==['Tpre=tR-t0','Tworker=tW-tR','Tpost=tF-tW']
    assert 'wait_worker returnedTrue' in f['proposed_markers']['tW']
    # Pin the program-order basis of the proposed ordered *observation* marker.
    launch=function(D+'capture.py','launch')
    release=expressions(launch,"c.write_json_fd(release_write, dict(event='RELEASE', lease=owner.nonce), 4096)")[0]
    close=expressions(launch,'os.close(release_write)')[0];wait=expressions(launch,'wait_worker(process)')[0]
    assert pos(release)<pos(close)<pos(wait)
    assert isinstance(launch.body[-1],ast.Return) and launch.body[-1].lineno>wait.lineno
    wait_source=ast.unparse(function('testing/prospective_capture_typed/capture.py','wait_worker'))
    assert 'process.wait(timeout=limit)' in wait_source and 'return True' in wait_source and 'return False' in wait_source
    assert r['E06']['reviewed_in_I127'] is False and r['E06']['component_tests_executed']==0 and r['E06']['no_implicit_execution_authorization']
    d=r['decision']
    for k in ['E01_E05_all_closed','platform_attested','complete_heap_verified','full_work_WCET_verified','CPU_service_verified','success_within900_verified','issue_SOURCE_CAPACITY_VERIFIED','product_quotas_changed','source_implementation_changed','product_or_components_executed','scheduler_model_executed','resources_reserved','proposal_enabled','capture_enabled','D5_closed','H07_closed']:assert d[k] is False,k
    assert d['PFC126_bytes_unchanged'] and d['CP03_and_30_source_sites_and_I124_preserved']
    assert d['certificate_unchanged']==rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')['status']=='IMPLEMENTED_NOT_ADMITTED'
    assert c['product_numeric_candidates']==rd(P+'D5-I122-CAPACITY-CONTRACT.json')['numeric_candidates']
    assert not c['product_numeric_candidates_applied'] and not c['time']['new_end_to_end_timer_installed']
    assert d['IR03']==m['IR03']=='NOT_READY'
    assert r['git_publication']['commit_and_push_all_requested']
    for p in ['docs/validation/D5-JOINT-capture-authorization.json','docs/validation/D5-JOINT-P01','docs/validation/D5-JOINT-P01-launch.json']:assert not (ROOT/p).exists(),p
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',obligations_reviewed=5,resource_obligations_closed=0,reference_files=15,local_reference_rechecked=strict,findings=2,contract_unchanged=True,platform_attested=False,product_or_components_executed=0,prior_published_files_preserved=113,new_files=len(expected),proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))
if __name__=='__main__':main()
