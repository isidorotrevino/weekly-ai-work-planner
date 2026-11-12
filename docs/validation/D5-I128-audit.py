#!/usr/bin/env python3
"""I128 documentary audit: AST, JSON, hashes, source order and arithmetic.

Never import/execute the candidate, wait_worker, product, components or logical
cases. Git subprocesses only inspect repository metadata. No runtime time proof.
"""
import ast
import copy
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

def check_anchor(a):
    n=function(a['path'],a['symbol'])
    if a.get('kind')=='NORMAL_RETURN_AFTER_FINALLY':n=n.body[-1];assert isinstance(n,ast.Return)
    elif a.get('expression'):n=expressions(n,a['expression'])[a['occurrence']]
    assert (n.lineno,n.end_lineno)==(a['line'],a['end_line'])
    if 'column' in a:assert n.col_offset==a['column']
    assert hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==a['AST_sha256']
    return n

def main():
    c=rd(P+'D5-I128-PLATFORM-CONTRACT-CANDIDATE.json');r=rd(P+'D5-I128-F127-01-resolution.json');seal=rd(P+'D5-I128-integrity.json')
    base=c['base_commit'];assert base==r['base_commit']==seal['base_commit']=='918d40229d8b35f5af40feda6419754dcc0fba34'
    subprocess.check_call(['git','merge-base','--is-ancestor',base,'HEAD'],cwd=ROOT)
    assert len(seal['preserved_published118'])==118
    for pins in [seal['preserved_published118'],seal['artifacts'],c['input_pins'],r['input_pins']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert P+'D5-I128-integrity.json' not in seal['artifacts']
    expected=set(seal['artifacts'])|{P+'D5-I128-integrity.json'};assert len(expected)==5
    changed=set(git('diff',base,'--name-only').splitlines());untracked=set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed|untracked==expected,(changed,untracked,expected)
    if git('rev-parse','HEAD')!=base:assert not git('diff','HEAD','--name-only')
    for oldseal in ['D5-I127-integrity.json','D5-I126-integrity.json','D5-I125-integrity.json']:
        for p,h in rd(P+oldseal)['artifacts'].items():assert sha(p)==h,p
    for p,h in rd(P+'D5-I119-integrity.json')['inherited_inputs477'].items():assert sha(p)==h,p
    old=rd(P+'D5-I126-PLATFORM-CONTRACT-CANDIDATE.json');prior=rd(P+'D5-I127-E01-E05-review.json')
    assert c['contract_id']==r['contract']['id']=='PFC126-CANDIDATE-02'
    assert c['schema']=='d5.i128-platform-contract-candidate.v2' and c['increment']=='I128'
    assert r['contract']['sha256']==sha(r['contract']['path'])
    assert c['predecessor']==r['predecessor']
    assert c['predecessor']['contract_id']==old['contract_id']=='PFC126-CANDIDATE-01'
    assert c['predecessor']['sha256']==sha(c['predecessor']['path']) and c['predecessor']['bytes_preserved'] and c['predecessor']['revision']==2
    changed_keys={k for k in old.keys()|c.keys() if old.get(k)!=c.get(k)}
    assert changed_keys=={'schema','contract_id','increment','date','base_commit','authority','input_pins','time','required_evidence','predecessor','amendment'},changed_keys
    for k in r['unchanged_sections']:assert c[k]==old[k],k
    assert c['heap']==old['heap'] and c['normative_state']==old['normative_state']
    assert c['status']=='DRAFT_FOR_REVIEW_NOT_ATTESTED_NOT_ADMITTED'
    assert c['amendment']['finding']==r['finding']=='F127-01'
    assert c['amendment']['status']==r['findings']['F127_01']=='RESOLVED_IN_CANDIDATE_CONTRACT_ONLY'
    assert c['amendment']['does_not_close_E05'] and c['amendment']['does_not_change_product_or_quotas']
    assert c['amendment']['review_sha256']==sha(c['amendment']['review_path'])
    assert r['findings']['F127_02']=='OPEN_EVIDENCE_UNCHANGED'
    for p,h in old['input_pins'].items():assert c['input_pins'][p]==h,p
    assert set(c['input_pins'])-set(old['input_pins'])=={P+'D5-I126-PLATFORM-CONTRACT-CANDIDATE.json',P+'D5-I127-E01-E05-review.json',P+'D5-I127-integrity.json',P+'D5-I127-runtime-reference-manifest.json'}
    t=c['time'];ot=old['time'];changes={k for k in t.keys()|ot.keys() if t.get(k)!=ot.get(k)}
    assert changes=={'clock','phase_budgets','worker_service_partition','service_rule','normative_markers','ordered_interval_rule','success_path_qualification','observation_latency_rule','failure_claim','proof_collection_state','forbidden_marker_substitutions'},changes
    phases=copy.deepcopy(ot['phase_budgets'])
    phases[1]['end']='Coordinator wait_worker(process) call returned exact True (tW), not physical worker exit'
    phases[2]['start']='Coordinator exact-True wait_worker return (tW), not worker exit or later packet validation'
    assert t['phase_budgets']==phases
    assert [p['candidate_wall_seconds'] for p in phases]==[60,750,60]
    assert sum(p['candidate_wall_seconds'] for p in phases)+t['unassigned_wall_reserve_seconds']==t['success_end_to_end_candidate_seconds']==900
    assert all(p['verified_upper_seconds'] is None and not p['evidence_pins'] for p in phases)
    w=t['worker_service_partition'];ow=ot['worker_service_partition']
    assert {k:v for k,v in w.items() if k!='attribution'}=={k:v for k,v in ow.items() if k!='attribution'}
    assert w['attribution'].startswith(ow['attribution']) and 'observation service' in w['attribution']
    assert w['candidate_CPU_upper_seconds']+w['candidate_IO_child_wait_upper_seconds']+w['candidate_scheduler_and_blocking_upper_seconds']==750
    markers=t['normative_markers'];assert markers==r['marker_defs']
    assert [m['id'] for m in markers]==['t0','tR','tW','tF']
    assert all(m['clock_owner']=='coordinator' and m['clock_value'] is None for m in markers)
    marker_nodes=[check_anchor(m['source_anchor']) for m in markers]
    for a in c['source_anchors']+r['source_anchors']:check_anchor(a)
    assert pos(marker_nodes[0])<pos(marker_nodes[1])<pos(marker_nodes[2])<pos(marker_nodes[3])
    launch=function(D+'capture.py','launch')
    release=expressions(launch,"c.write_json_fd(release_write, dict(event='RELEASE', lease=owner.nonce), 4096)")[0]
    assert pos(release)<pos(marker_nodes[1])
    assert len(expressions(launch,'wait_worker(process)'))==1
    assert marker_nodes[3]==launch.body[-1] or ast.dump(marker_nodes[3])==ast.dump(launch.body[-1])
    wait=function('testing/prospective_capture_typed/capture.py','wait_worker');waittext=ast.unparse(wait)
    assert 'process.wait(timeout=limit)' in waittext
    assert isinstance(wait.body[1],ast.Try)
    trybody=wait.body[1].body;assert isinstance(trybody[-1],ast.Return) and isinstance(trybody[-1].value,ast.Constant) and trybody[-1].value.value is True
    assert 'TimeoutExpired' in waittext and 'return False' in waittext
    s=t['success_path_qualification']
    for k in ['wait_worker_result_must_be_exact_True','wait_True_is_not_capture_success','later_checks_never_move_tW','no_missing_marker_or_time_coerced_to_zero','claim_requires_all_four_markers','timeout_flag_or_later_cleanup_cannot_substitute_True','existing_source_checks_not_modified']:assert s[k] is True,k
    assert s['False_or_exception_defines_qualified_tW'] is False
    assert len(s['independent_later_checks'])==4
    assert all(v is False for k,v in t['proof_collection_state'].items() if k!='source_program_order_reviewed_only')
    assert t['proof_collection_state']['source_program_order_reviewed_only']
    assert not t['new_end_to_end_timer_installed'] and not t['all_phase_bounds_verified'] and not t['successful_completion_within900_verified']
    assert t['minimum_service_curve']==ot['minimum_service_curve'] and not t['minimum_service_curve']['verified']
    interval=t['ordered_interval_rule'];assert interval['required_order']==['t0','tR','tW','tF'] and interval['inequality']=='t0<=tR<=tW<=tF'
    assert interval['intervals']==dict(Tpre='tR-t0',Tworker='tW-tR',Tpost='tF-tW')
    assert interval['nonnegative_required'] and interval['no_uncovered_exit_observation_gap']
    # Symbolic documentary arithmetic; no event schedule or execution trace.
    terms=[{'tR':1,'t0':-1},{'tW':1,'tR':-1},{'tF':1,'tW':-1}];coeff={}
    for term in terms:
        for name,value in term.items():coeff[name]=coeff.get(name,0)+value
    assert {k:v for k,v in coeff.items() if v}=={'t0':-1,'tF':1}
    partition=r['formal_partition'];assert partition['ordered_nonnegative_definition_resolved']
    assert partition['verified_phase_upper_seconds']==[None,None,None] and not partition['proof_of_success_within900'] and not partition['clock_service_attested']
    assert partition['sum_seconds']==900 and partition['reserve_seconds']==30 and partition['phase_budgets_seconds']==[60,750,60]
    assert [case['id'] for case in r['logical_cases']]==['C01','C02','C03','C04','C05'] and all(not case['executed'] for case in r['logical_cases'])
    assert c['required_evidence'][:4]==old['required_evidence'][:4] and c['required_evidence'][5]==old['required_evidence'][5]
    assert c['required_evidence'][4]['id']=='E05' and c['required_evidence'][4]['status']=='MISSING' and 'tW' in c['required_evidence'][4]['description']
    assert [x['id'] for x in r['E01_E05_disposition']]==['E01','E02','E03','E04','E05'] and all(not x['closed'] for x in r['E01_E05_disposition'])
    assert [x['status'] for x in r['E01_E05_disposition'][:4]]==[x['status'] for x in prior['obligations'][:4]]
    d=r['decision']
    for k in ['platform_attested','complete_heap_verified','success_within900_verified','issue_SOURCE_CAPACITY_VERIFIED','product_numeric_quotas_changed','source_implementation_changed','product_or_components_executed','markers_instrumented','logical_cases_executed','resources_reserved','capture_inputs_rebound','authority_or_destination_created','proposal_enabled','capture_enabled','D5_closed','H07_closed']:assert d[k] is False,k
    assert d['resource_obligations_closed']==0 and d['heap_budgets_and_time_budgets_unchanged'] and d['PFC126_CANDIDATE_01_bytes_preserved']
    assert d['certificate_unchanged']==rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')['status']=='IMPLEMENTED_NOT_ADMITTED'
    assert c['product_numeric_candidates']==rd(P+'D5-I122-CAPACITY-CONTRACT.json')['numeric_candidates'] and not c['product_numeric_candidates_applied']
    assert d['IR03']==c['normative_state']['IR03']=='NOT_READY'
    assert r['E06']['components_executed']==0 and not r['E06']['execution_authorized']
    assert r['git_publication']['commit_and_push_all_requested']
    for p in ['docs/validation/D5-JOINT-capture-authorization.json','docs/validation/D5-JOINT-P01','docs/validation/D5-JOINT-P01-launch.json']:assert not (ROOT/p).exists(),p
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',contract=c['contract_id'],F127_01='RESOLVED_IN_CANDIDATE_CONTRACT_ONLY',logical_cases_executed=0,source_program_order_checked=True,E05_closed=False,resource_obligations_closed=0,platform_attested=False,proposal_enabled=False,prior_published_files_preserved=118,new_files=len(expected),product_or_components_executed=0,quotas_changed=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))
if __name__=='__main__':main()
