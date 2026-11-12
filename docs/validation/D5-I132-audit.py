#!/usr/bin/env python3
"""I132 evidence-plan audit: DAG, acceptance mapping, hashes, AST, arithmetic.

No future evidence generated or product/component/benchmark executed. Git
subprocesses inspect publication metadata; all planned outputs must be absent.
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
        def visit(n):
            for x in ast.iter_child_nodes(n):
                if isinstance(x,(ast.ClassDef,ast.FunctionDef)):
                    if x.name==part:found.append(x)
                else:visit(x)
        visit(root);assert len(found)==1,(path,symbol,part);root=found[0]
    return root

def check_anchor(a):
    n=function(a['path'],a['symbol'])
    if a.get('kind')=='NORMAL_RETURN_AFTER_FINALLY':n=n.body[-1];assert isinstance(n,ast.Return)
    elif a.get('expression'):
        wanted=ast.dump(ast.parse(a['expression'],mode='eval').body,include_attributes=False)
        nodes=sorted([x for x in ast.walk(n) if isinstance(x,ast.expr) and ast.dump(x,include_attributes=False)==wanted],key=lambda x:(x.lineno,x.col_offset));n=nodes[a['occurrence']]
    assert (n.lineno,n.end_lineno)==(a['line'],a['end_line'])
    if 'column'in a:assert n.col_offset==a['column']
    assert hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==a['AST_sha256']

def main():
    p=rd(P+'D5-I132-E01-E05-evidence-plan.json');q=rd(P+'D5-I132-closure-checklist.json');seal=rd(P+'D5-I132-integrity.json')
    base=p['base_commit'];assert base==q['base_commit']==seal['base_commit']=='fa91f107c56535b850ee3d86e16882756924e5eb'
    subprocess.check_call(['git','merge-base','--is-ancestor',base,'HEAD'],cwd=ROOT)
    assert len(seal['preserved_published138'])==138
    for pins in [seal['preserved_published138'],seal['artifacts'],p['input_pins'],q['input_pins']]:
        for path,h in pins.items():assert sha(path)==h,path
    assert P+'D5-I132-integrity.json' not in seal['artifacts']
    expected=set(seal['artifacts'])|{P+'D5-I132-integrity.json'};assert len(expected)==5
    changed=set(git('diff',base,'--name-only').splitlines());untracked=set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed|untracked==expected,(changed,untracked,expected)
    if git('rev-parse','HEAD')!=base:assert not git('diff','HEAD','--name-only')
    for oldseal in ['D5-I131-integrity.json','D5-I130-integrity.json','D5-I129-integrity.json']:
        for path,h in rd(P+oldseal)['artifacts'].items():assert sha(path)==h,path
    for path,h in rd(P+'D5-I119-integrity.json')['inherited_inputs477'].items():assert sha(path)==h,path
    assert sha(q['plan']['path'])==q['plan']['sha256']
    c=rd(P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json');old=rd(P+'D5-I131-E01-E05-review.json')
    assert p['contract_id']==q['contract_id']==c['contract_id']=='PFC126-CANDIDATE-03'
    assert p['route_is_plan_not_contract_or_execution_change']
    assert p['selected_planning_route']=='STATIC_SOURCE_AND_ALLOCATION_WORK_PROOFS_PLUS_PRE_EXISTING_ATTESTED_RUNTIME_PLATFORM_SERVICE_OR_JUSTIFIED_STATIC_WCET'
    tasks=p['tasks'];owners=['P04-'+h['id'] for h in c['heap']['owner_budgets']]
    ids=['P01','P02','P03']+owners+['P05','P06','P07','P08','P09','P10']
    assert [t['id'] for t in tasks]==ids and len(ids)==len(set(ids))==20
    outputs=[t['planned_output'] for t in tasks];assert len(set(outputs))==20 and outputs==q['planned_future_artifact_paths']
    assert len({t['output_schema'] for t in tasks})==20
    byid={t['id']:t for t in tasks};order={id:i for i,id in enumerate(ids)}
    for task in tasks:
        assert task['state']=='PLANNED_NOT_PRODUCED' and not task['output_created'] and not task['external_evidence_obtained']
        assert task['assigned_person'] is None and task['responsible_role'] and task['review_role']
        assert task['method'] and task['required_specific_fields'] and task['acceptance'] and task['rejection']
        assert not task['product_component_or_benchmark_execution_allowed'] and not task['quota_or_budget_change_allowed']
        assert task['obligations'] and set(task['obligations'])<=set(['E01','E02','E03','E04','E05'])
        assert len(task['depends_on'])==len(set(task['depends_on']))
        assert all(id in byid and order[id]<order[task['id']] for id in task['depends_on'])
        assert all(path in p['input_pins'] for path in task['current_inputs'])
        path=Path(task['planned_output']);assert str(path).startswith(P+'D5-PFC126-03-') and path.suffix=='.json' and '..' not in path.parts and not path.is_absolute()
        assert not (ROOT/path).exists(),path
    # Explicit ordering, dependency coverage and acyclicity of the proposed DAG.
    assert byid['P01']['depends_on']==[]
    assert byid['P02']['depends_on']==['P01'] and byid['P03']['depends_on']==['P01','P02']
    assert all(byid[id]['depends_on']==['P01','P02'] for id in owners)
    assert set(byid['P05']['depends_on'])==set(['P01','P02','P03']+owners)
    assert byid['P06']['depends_on']==['P01','P02','P03']
    assert byid['P07']['depends_on']==['P02','P03','P06']
    assert byid['P08']['depends_on']==['P01','P02','P03','P05','P06','P07']
    assert byid['P09']['depends_on']==['P02','P03','P05','P06','P07','P08']
    assert 'P09' in byid['P10']['depends_on']
    stages=p['execution_order'];assert [s['stage'] for s in stages]==['S0','S1','S2','S3','S4','S5']
    staged=[id for stage in stages for id in stage['task_ids']]
    assert len(staged)==20 and set(staged)==set(ids)
    staged_order={id:i for i,id in enumerate(staged)}
    assert all(staged_order[dep]<staged_order[t['id']] for t in tasks for dep in t['depends_on'])
    assert staged.index('P03')<staged.index('P06') and all(staged.index('P03')<staged.index(id) for id in owners)
    assert len(p['early_stop_rules'])==4 and len(p['common_artifact_envelope'])==6
    for h in c['heap']['owner_budgets']:
        t=byid['P04-'+h['id']]
        assert t['planned_output']==P+'D5-PFC126-03-E02-'+h['id']+'.json'
        assert 'candidate_budget_bytes='+str(h['candidate_budget_bytes']) in t['required_specific_fields']
        assert t['obligations']==['E02']
    assert 'No reserve transfer' in byid['P04-H04']['acceptance']
    assert '33 generations' in byid['P04-H04']['rejection']
    assert byid['P09']['planned_output'].endswith('RESOURCE-BUNDLE-BINDING-REVIEW.json')
    assert byid['P10']['planned_output'].endswith('E01-E05-CLOSURE-REVIEW.json')
    closures=q['obligations'];assert [x['id'] for x in closures]==['E01','E02','E03','E04','E05']
    expected_criteria={row['id'] for ob in old['obligations'] for row in ob['criteria']}
    assigned=[]
    for entry,ob in zip(closures,old['obligations'],strict=True):
        assert entry['id']==ob['id'] and not entry['complete_evidence_present'] and not entry['closed']
        assert entry['criterion_ids']==[r['id'] for r in ob['criteria']]
        assert set(entry['required_tasks'])<=set(ids) and len(entry['required_tasks'])==len(set(entry['required_tasks']))
        assert 'P10' in entry['required_tasks'] and 'P09' in entry['required_tasks']
        assert entry['acceptance'] and entry['not_sufficient'];assigned+=entry['criterion_ids']
    assert len(assigned)==len(set(assigned))==20 and set(assigned)==expected_criteria and q['criterion_ids_fully_covered']
    assert set(owners)<=set(closures[1]['required_tasks'])
    assert all(id in closures[4]['required_tasks'] for id in ['P05','P06','P07','P08','P09','P10'])
    for a in q['source_anchors']:check_anchor(a)
    assert q['source_anchors']==c['source_anchors']+c['cost_coverage']['source_anchors']
    policy=p['source_and_budget_policy'];assert policy['candidate03_unchanged'] and policy['implementation_fixed']=='I122-CANDIDATE-01'
    assert policy['numeric_candidates_unchanged'] and policy['proof_failure_does_not_authorize_code_budget_or_quota_change']
    assert policy['reserve_allocation_heap_bytes']==policy['reserve_allocation_time_seconds']==0
    ext=p['external_evidence_inputs'];assert ext['runtime_custodian_material']==ext['platform_capacity_service_material']=='NOT_PROVIDED'
    assert not ext['named_responsible_persons_assigned'] and not ext['external_contacts_made'] and not ext['resources_reserved']
    assert p['no_time_or_capacity_guarantee_for_plan_completion']
    for k in ['planned_output_files_created','product_or_components_executed','benchmark_or_scheduling_probe_authorized','contracts_or_quotas_changed','E06_execution_authorized','issue_SOURCE_CAPACITY_VERIFIED','proposal_enabled','D5_closed']:assert p[k] is False,k
    assert p['resource_obligations_closed']==q['resource_obligations_closed']==0 and not q['planned_artifacts_are_existing_evidence']
    d=q['decision']
    for k in ['complete_resource_evidence_produced','external_contacts_made','product_or_components_executed','source_implementation_changed','product_quotas_changed','reserve_transfers_applied','resources_reserved','capture_inputs_rebound','authority_or_destination_created','platform_attested','issue_SOURCE_CAPACITY_VERIFIED','proposal_enabled','capture_enabled','D5_closed','H07_closed']:assert d[k] is False,k
    assert d['candidate03_bytes_unchanged'] and d['prior_marker_cost_reserve_rules_preserved'] and d['numeric_budgets_and_quotas_unchanged']
    assert d['certificate_unchanged']==rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')['status']=='IMPLEMENTED_NOT_ADMITTED'
    assert d['IR03']==p['IR03']=='NOT_READY'
    assert c['product_numeric_candidates']==rd(P+'D5-I122-CAPACITY-CONTRACT.json')['numeric_candidates'] and not c['product_numeric_candidates_applied']
    assert all(h['proof_upper_bytes'] is None for h in c['heap']['owner_budgets']) and all(row['verified_upper_seconds'] is None for row in c['time']['phase_budgets'])
    assert c['reserve_accounting']['heap']['allocated_total_bytes']==c['reserve_accounting']['time']['allocated_total_seconds']==0
    assert not c['normative_state']['execution_authorized'] and not c['normative_state']['component_execution_authorized']
    assert q['E06']['components_executed']==0 and not q['E06']['execution_authorized']
    assert p['git_publication']['commit_and_push_all_requested'] and q['git_publication']['commit_and_push_all_requested']
    for path in ['docs/validation/D5-JOINT-capture-authorization.json','docs/validation/D5-JOINT-P01','docs/validation/D5-JOINT-P01-launch.json']:assert not (ROOT/path).exists(),path
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',contract=c['contract_id'],work_packages=20,planned_outputs=20,future_outputs_created=0,heap_proof_packages=11,E01_E05_criteria_mapped=20,DAG_checked=True,external_evidence_obtained=False,resource_obligations_closed=0,product_or_components_executed=0,quotas_changed=False,reserve_transfers_applied=False,proposal_enabled=False,prior_published_files_preserved=138,new_files=len(expected),D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))
if __name__=='__main__':main()
