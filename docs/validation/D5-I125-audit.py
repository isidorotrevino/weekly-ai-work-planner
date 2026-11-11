#!/usr/bin/env python3
"""I125 documentary no-admission audit: AST, JSON, hashes and arithmetic only.

No candidate/product/component imports, code generation, benchmarks or scheduler
experiments. PASS means record consistency, never full heap/time admission.
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
def function(path,symbol):
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

def expression_calls(node,expression):
    want=ast.dump(ast.parse(expression,mode='eval').body,include_attributes=False)
    return sorted([n for n in ast.walk(node) if isinstance(n,ast.expr) and ast.dump(n,include_attributes=False)==want],key=lambda n:(n.lineno,n.col_offset))
def pos(node):return node.lineno,node.col_offset
def one(node,expression):
    found=expression_calls(node,expression);assert len(found)==1,(expression,len(found));return found[0]

def main():
    h=rd(P+'D5-I125-complete-heap-review.json');t=rd(P+'D5-I125-900-second-review.json');g=rd(P+'D5-I125-resource-admission-decision.json');seal=rd(P+'D5-I125-integrity.json')
    assert git('rev-parse','HEAD')==h['base_commit']==t['base_commit']==g['base_commit']==seal['base_commit']=='50c49678568bae2abeefbe5fec0285f26c628283'
    assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
    assert len(seal['prior_untracked102'])==102
    for pins in [seal['prior_untracked102'],seal['artifacts'],h['inputs'],t['inputs'],g['reviews']]:
        for p,value in pins.items():assert sha(p)==value,p
    assert P+'D5-I125-integrity.json' not in seal['artifacts']
    expected=set(seal['prior_untracked102'])|set(seal['artifacts'])|{P+'D5-I125-integrity.json'}
    assert set(git('ls-files','--others','--exclude-standard').splitlines())==expected
    for old in ['D5-I124-integrity.json','D5-I123-integrity.json','D5-I122-integrity.json']:
        for p,value in rd(P+old)['artifacts'].items():assert sha(p)==value,p
    for p,value in rd(P+'D5-I119-integrity.json')['inherited_inputs477'].items():assert sha(p)==value,p
    for a in h['anchors']+t['anchors']:
        node=function(a['path'],a['symbol'])
        assert (node.lineno,node.end_lineno)==(a['line'],a['end_line'])
        assert hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()==a['AST_sha256']
    terms=h['required_terms'];assert len(terms)==11
    assert [r['id'] for r in terms]==[f'H{i:02}' for i in range(1,12)]
    assert all(r['complete_term_upper_bytes'] is None for r in terms)
    assert not h['all_terms_have_verified_complete_bounds']
    for key in ['complete_peak_requested_heap_upper_bytes','complete_peak_committed_heap_upper_bytes','worker_heap_capacity_bytes']:assert h[key] is None
    assert not h['host_capacity_document_found']
    assert h['no_missing_term_coerced_to_zero'] and h['no_serialized_bytes_relabelled_as_heap']
    assert h['no_New_heap_quota_created'] and not h['claim_of_actual_unbounded_heap'] and not h['claim_of_actual_infeasibility']
    prior=rd(P+'D5-I124-resource-admission-review.json');proof=rd(P+'D5-I124-global-batch-lifetime-proof.json')
    contract=rd(P+'D5-I122-CAPACITY-CONTRACT.json');lim=contract['numeric_candidates']
    assert terms[3]['known_partial_upper']==prior['builtin_storage_model']['all_batches_requested_bytes_upper']==23096917808804736
    assert terms[7]['known_partial_upper']==2*prior['physical_file_read_plan_unchanged']['upper']==532675582
    assert terms[8]['known_partial_upper']==2*lim['event_pages_total_bytes']==134217728
    assert terms[9]['known_partial_upper']==5*lim['raw_bytes']==62914560
    assert len(lim)==24 and not any('heap' in k or 'CPU' in k or 'cpu' in k for k in lim)
    # Check allocation precedes quota rejection: these are output guards, not
    # a proof that all allocations before them fit the serialized quota.
    output=function('testing/prospective_capture/capture.py','BoundedOutput.write')
    assert pos(one(output,"value.encode('utf8')"))<pos(one(output,"require(self.count + len(b) <= self.limit, 'RAW_BUDGET')"))
    append=function('testing/prospective_capture_typed/capture.py','PageSink.append')
    assert one(append,'encode(event)').lineno<one(append,"c.require(len(b) <= self.limits['event_bytes'], 'EVENT_SIZE_BUDGET')").lineno
    encode=ast.unparse(function('testing/prospective_capture_typed/capture.py','encode'))
    assert 'json.dumps' in encode and ".encode('utf8')" in encode
    reader=ast.unparse(function('testing/prospective_capture/capture.py','Reader.read'))
    assert 'chunks.append(b)' in reader and "b''.join(chunks)" in reader and 'left -= len(b)' in reader
    phase=ast.unparse(function(D+'capture.py','PhaseBytes.__init__'))
    assert 'self.bodies = dict(bodies)' in phase
    tee=ast.unparse(function(D+'worker.py','Tee'))
    assert 'io.StringIO' in tee and 'super().write(s)' in tee
    exercise=ast.unparse(function(D+'worker.py','exercise'))
    assert 'stdout.getvalue().encode()' in exercise and 'c.strict_json' in exercise
    # Establish actual timer window by source position; execute no timeout,
    # subprocess, candidate or logical countermodel.
    launch=function(D+'capture.py','launch')
    wait=one(launch,'wait_worker(process)')
    cleanups=expression_calls(launch,"c.stop_owned(process, owner, dict(pid=process.pid, pgid=process.pid, lease=owner.nonce))")
    assert len(cleanups)==2  # normal cleanup and finally fallback, both outside wait
    cleanup=cleanups[0]
    release=one(launch,"c.write_json_fd(release_write, dict(event='RELEASE', lease=owner.nonce), 4096)")
    ready=one(launch,"verify_ready(c.receive_line(ready_read, LIMITS['wait_seconds']), owner.nonce, process.pid, rawfd, sidefd, directory)")
    after=one(launch,'inputs.joint_plan.after()')
    evidence_calls=expression_calls(launch,'evidence_reader(root)')
    assert len(evidence_calls)==3  # normal packet plus later failure/final paths
    evidence=evidence_calls[0]
    assert ready.lineno<release.lineno<wait.lineno<cleanup.lineno<after.lineno<evidence.lineno
    # Follow alias chain, rather than assuming same-named routines are active.
    assert 'wait_worker=late.wait_worker' in (ROOT/(D+'capture.py')).read_text()
    assert 'wait_worker=t.wait_worker' in (ROOT/'testing/prospective_capture_late/capture.py').read_text().replace(' ','')
    wait_source=ast.unparse(function('testing/prospective_capture_typed/capture.py','wait_worker'))
    assert 'process.wait(timeout=limit)' in wait_source and "LIMITS['campaign_seconds']" in wait_source
    assert 'TimeoutExpired' in wait_source and 'return False' in wait_source
    assert 'process_time' not in wait_source and 'getrusage' not in wait_source
    assert t['campaign_seconds_candidate']==lim['campaign_seconds']==900
    assert t['wait_seconds_candidate']==lim['wait_seconds']==20
    phases=t['ordered_coordinator_phases'];assert [p['inside_wait_worker_900'] for p in phases]==[False,True,False,False]
    assert all(p['verified_completion_seconds_upper'] is None for p in phases)
    assert phases[1]['timeout_argument_seconds']==900
    assert t['inherited_closed_counts']==dict(F=proof['global_F_upper'],S=proof['global_S_upper'],clone_visits_upper=proof['kernel_work']['clone_visits_upper'])
    assert t['whole_campaign_CPU_seconds_upper'] is None and t['whole_campaign_wall_seconds_upper'] is None
    assert not t['worker_success_within_900_verified'] and not t['end_to_end_success_within_900_verified']
    assert not t['logical_countermodel']['executed'] and t['logical_countermodel']['delay_seconds']==901>900
    assert t['no_rate_invented_from_work_divided_by_900'] and t['no_watchdog_relabelled_as_WCET']
    assert len(g['required_predicates'])==8 and all(v is False for v in g['required_predicates'].values())
    assert g['automatic_documentary_disposition']=='DO_NOT_ISSUE_SOURCE_CAPACITY_VERIFIED'
    for review in [h,t,g]:
        reply=review['user_platform_contract_reply']
        assert reply['answer']=='No; dejar dictamen de no admisión'
        assert reply['no_admission_confirmed'] and not reply['contract_provided']
        assert not reply['authorizes_execution_or_quota_changes']
    assert rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')['status']==g['current_certificate_status']=='IMPLEMENTED_NOT_ADMITTED'
    for key in ['certificate_modified','source_or_implementation_changed','quotas_changed','product_or_components_executed','synthetic_runtime_or_benchmark_executed','scheduler_countermodel_executed','authority_or_destination_created','commit_or_push','capture_enabled']:assert g[key] is False,key
    assert g['prior_files_preserved']==102 and g['F_S_lifetime_results_preserved'] and g['CP03_original_proof_preserved']
    for y in [h,t,g]:assert not y['proposal_enabled'] and not y['D5_closed'] and y['IR03']=='NOT_READY'
    for p in ['docs/validation/D5-JOINT-capture-authorization.json','docs/validation/D5-JOINT-P01','docs/validation/D5-JOINT-P01-launch.json']:assert not (ROOT/p).exists(),p
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',heap_ownership_terms=11,timer_window_verified=True,complete_heap_upper=None,whole_campaign_seconds_upper=None,resource_admission='NOT_ESTABLISHED',prior_files_preserved=102,new_artifacts=len(seal['artifacts'])+1,product_or_components_executed=0,certificate_unchanged='IMPLEMENTED_NOT_ADMITTED',proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),sort_keys=True))
if __name__=='__main__':main()
