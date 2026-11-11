#!/usr/bin/env python3
"""Read-only I124 source arithmetic/pin audit; never run candidate or components.

PASS checks documentary consistency, not the runtime truth of source-model
premises, whole-heap capacity or whole-campaign CPU/time.
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

class Census(ast.NodeVisitor):
    def __init__(self,path):self.path=path;self.scope=[];self.rows=[]
    def visit_ClassDef(self,n):self.scope.append(n.name);self.generic_visit(n);self.scope.pop()
    def visit_FunctionDef(self,n):self.scope.append(n.name);self.generic_visit(n);self.scope.pop()
    def visit_Attribute(self,n):
        s=ast.unparse(n)
        if '.causal.' in s and isinstance(n.ctx,(ast.Load,ast.Store)):
            self.rows.append(dict(path=self.path,symbol='.'.join(self.scope),line=n.lineno,expression=s,mode=type(n.ctx).__name__))
        self.generic_visit(n)
    def visit_Call(self,n):
        if isinstance(n.func,ast.Attribute) and n.func.attr in ['_atomic','_observe','prepare']:
            self.rows.append(dict(path=self.path,symbol='.'.join(self.scope),line=n.lineno,expression=ast.unparse(n.func),mode='Call'))
        self.generic_visit(n)

def function(tree,path):
    root=tree
    for part in path.split('.'):
        options=[]
        def visit(n):
            for c in ast.iter_child_nodes(n):
                if isinstance(c,(ast.ClassDef,ast.FunctionDef)):
                    if c.name==part:options.append(c)
                else:visit(c)
        visit(root);assert len(options)==1,(path,part);root=options[0]
    return root

def main():
    x=rd(P+'D5-I124-global-batch-lifetime-proof.json');r=rd(P+'D5-I124-resource-admission-review.json');seal=rd(P+'D5-I124-integrity.json')
    assert git('rev-parse','HEAD')==x['base_commit']==r['base_commit']==seal['base_commit']=='50c49678568bae2abeefbe5fec0285f26c628283'
    assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
    assert len(seal['prior_untracked97'])==97
    for pins in [seal['prior_untracked97'],seal['artifacts'],x['inputs']]:
        for path,h in pins.items():assert sha(path)==h,path
    assert sha(r['proof']['path'])==r['proof']['sha256']
    assert P+'D5-I124-integrity.json' not in seal['artifacts']
    expected=set(seal['prior_untracked97'])|set(seal['artifacts'])|{P+'D5-I124-integrity.json'}
    assert set(git('ls-files','--others','--exclude-standard').splitlines())==expected
    for old in ['D5-I123-integrity.json','D5-I122-integrity.json']:
        for p,h in rd(P+old)['artifacts'].items():assert sha(p)==h,p
    for p,h in rd(P+'D5-I119-integrity.json')['inherited_inputs477'].items():assert sha(p)==h,p
    # Parse and census only; no importlib, compile, exec, evaluator or subprocess
    # invocation of any candidate, test, runner or original program.
    sources=[D+'atomic.py',D+'capture.py',D+'worker.py','testing/prospective_capture_late/capture.py','testing/prospective_capture_typed/capture.py','testing/prospective_capture/capture.py']
    census=[];trees={}
    for p in sources:
        t=ast.parse((ROOT/p).read_text());trees[p]=t;c=Census(p);c.visit(t);census.extend(c.rows)
    assert census==x['dispatch_census'] and len(census)==115
    kernel=trees[D+'atomic.py'];raw=trees[D+'capture.py'];typed=trees['testing/prospective_capture_typed/capture.py']
    live=function(kernel,'build.Recorder');methods={n.name for n in live.body if isinstance(n,ast.FunctionDef)}
    assert {'__init__','start','stop','finish','wrap_boundary','wrap_return','constructor','emit','owner','reference','outcome'}<=methods
    core=ast.unparse(function(kernel,'build.Recorder._atomic'))
    assert 'if self._draft:' in core and 'return operation(self)' in core
    assert core.count('self._fork()')==1
    assert core.index('self._publish(draft)')<core.index('self.events.owner.create(name)')
    # Direct wrappers really call started for preview=None; return/failure are
    # alternatives. Pure selected incurs a snapshot on false results too.
    parent=ast.unparse(function(raw,'Recorder.install_direct.start'))
    assert 'if rec.causal.selected() else None' in parent
    assert parent.count('rec.causal.started')==2 and 'except BaseException' in parent
    pipe=ast.unparse(function(raw,'Recorder.install_direct.pipe'))
    assert 'if rec.causal.selected()' in pipe and 'rec.causal.pipe_return' in pipe
    proxy=ast.unparse(function(kernel,'build.CausalProxy.__getattr__'))
    assert "('selected', 'check_retained', 'protocol_for', 'witnesses')" in proxy
    assert 'clone_metadata(value, {}, opaque_originals(rec))' in proxy
    finish=ast.unparse(function(kernel,'build.Recorder.finish'))
    assert finish.count('self.causal.check_retained')==1 and finish.count('self.causal.tables')==1
    install=ast.unparse(function(typed,'Recorder.install'))
    assert "name not in ('assertRaises', 'assertRaisesRegex')" in install and "if depth == 0" in install
    assert 'capture.operand' in install
    modules=rd(P+'D5-I113-drive-global-event-bounds.json')['outside_root_event_review']['discovery_import_graph']['modules']
    assert len(modules)==33
    for m in modules.values():assert sha(m['path'])==m['sha256']==x['inputs'][m['path']]
    ref=rd(P+'D5-I115-refined-reference-envelope.json');assert len(x['root_rows'])==x['root_count']==321
    assert len({q['test_id'] for q in x['root_rows']})==321
    F=2;S=2
    for row,old in zip(x['root_rows'],ref['root_rows'],strict=True):
        assert (row['test_id'],row['evidence'],row['mode'])==(old['test_id'],old['evidence'],old['mode'])
        v=old['event_vector'];p=old['primitives'];d=int('.test_DI07_' in old['test_id'])
        terms=dict(event_committing_phases=old['event_upper'],companion_PRECALL=p['C'],binding_prepare_opportunities=2*v['A'],addSubTest=v['L']-3,raw_recv=p['M'],raw_join=p['X'],parent_started=p['P'],direct_pipe=d,direct_preview=d,direct_bind=d)
        assert terms==row['terms'] and min(terms.values())>=0
        assert row['F_upper']==sum(terms.values())
        assert row['S_terms']==dict(start_selected=1,Pipe_selected=p['P'],BaseProcess_start_selected=p['P'])
        assert row['S_upper']==1+2*p['P'];F+=row['F_upper'];S+=row['S_upper']
    assert F==x['global_F_upper']==52018 and S==x['global_S_upper']==1759
    N=F+S;assert N==x['global_clone_batches_upper']==53777
    assert x['event_associated_F_upper']==42074 and x['process_opportunities_upper']==718
    assert x['subtest_callbacks_upper']==197 and x['binding_slots_upper']==2
    assert x['global_fixed_F']==dict(initial_binding_phase=1,seal_page_close=1)
    assert x['global_fixed_S']==dict(finish_check_retained=1,finish_tables=1)
    old=rd(P+'D5-I123-transient-resource-envelope.json')['structural_per_clone'];C=old['containers_upper'];A=old['child_occurrences_upper'];V=old['clone_invocations_upper'];O=old['opaque_insert_attempts_upper']
    life=x['lifetime_envelope'];assert life['metadata_generations_including_initial_upper']==N+1==53778
    assert life['metadata_containers_upper']==(N+1)*C==8600477034570
    assert life['metadata_container_and_edge_units_upper']==(N+1)*(C+A)==25765336923450
    assert not life['GC_latency_assumed'] and not life['immediate_release_assumed'] and not life['peak_live_DAG_batches_claimed_as_33']
    work=x['kernel_work'];assert work['clone_visits_upper']==N*V==17164544043094
    assert work['logical_memo_operations_upper']==N*old['logical_memo_operations_upper']==42929405195193
    assert work['opaque_insert_attempts_upper']==N*O==107446446
    binary=r['runtime_metadata_observed_without_candidate']['interpreter_binary']
    assert str(Path(sys.executable).resolve())==binary['path']
    assert hashlib.sha256(Path(binary['path']).read_bytes()).hexdigest()==binary['sha256']
    assert Path(binary['path']).stat().st_size==binary['bytes']
    m=r['builtin_storage_model'];assert m['header_bytes_per_cloned_container']==1024
    assert m['bytes_per_child_occurrence']==m['memo_bytes_per_container']==m['opaque_bytes_per_insert_attempt']==512
    assert m['id_temporary_bytes_per_visit']==64 and m['opaque_fixed_bytes']==1024
    H=1024*C+512*A+512*C+64*V+1024+512*O
    assert m['batch_requested_bytes_upper']==H==429494352768
    assert m['all_batches_requested_bytes_upper']==N*H==23096917808804736
    assert not m['actual_interpreter_binary_layout_and_allocator_attested']
    assert not m['total_heap_or_RSS_bound'] and not m['complete_memory_capacity_verified']
    h=r['collision_work_model'];slots=8*(C+A+O+1);ops=3*V+C+A+O;probes=10*(slots+13)
    assert (h['table_slots_upper'],h['hash_operations_per_batch_upper'],h['probe_steps_per_hash_operation_upper'])==(slots,ops,probes)
    assert h['rehash_multiplier']==65
    W=N*65*ops*probes
    assert h['probe_inspections_upper']==W==192478912238762047131262250
    assert h['key_compare_byte_units_per_probe_upper']==524288
    assert h['probe_compare_byte_units_upper']==W*524288
    assert h['not_a_machine_instruction_or_CPU_seconds_bound']
    assert r['page_payload']['bodies_plus_chunks_upper']==134217728
    cpu=r['CPU_admission'];assert cpu['clone_counts_fully_numeric']
    assert not cpu['whole_campaign_CPU_seconds_verified'] and not cpu['wall_seconds_verified']
    assert cpu['campaign_seconds_unchanged']==rd(P+'D5-I122-CAPACITY-CONTRACT.json')['numeric_candidates']['campaign_seconds']==900
    assert rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')['status']=='IMPLEMENTED_NOT_ADMITTED'
    assert x['non_execution']==dict(product=False,candidate_import_or_compile=False,components=False,benchmark=False)
    for y in [x,r]:assert not y['proposal_enabled'] and not y['D5_closed'] and y['IR03']=='NOT_READY'
    assert not r['source_files_changed'] and not r['quotas_changed'] and not r['product_or_components_executed'] and not r['commit_or_push']
    assert not r['capture_enabled'] and not r['CP07_actual_admission'] and r['components_executed']==0
    assert r['prior_files_preserved']==97
    for p in ['docs/validation/D5-JOINT-capture-authorization.json','docs/validation/D5-JOINT-P01','docs/validation/D5-JOINT-P01-launch.json']:
        assert not (ROOT/p).exists(),p
    # Hypothetical bytes only; no rebind or modification of I122's input set.
    new=set(seal['artifacts'])|{P+'D5-I124-integrity.json'}
    added=sum((ROOT/p).stat().st_size for p in new)
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',roots=321,F_upper=F,S_upper=S,total_batches=N,retained_generations_upper=N+1,clone_visits_upper=N*V,prior_files_preserved=97,new_artifacts=len(new),candidate_or_components_executed=0,whole_heap_verified=False,whole_campaign_seconds_verified=False,I124_bytes_if_later_added=added,hypothetical_three_pass_additional_bytes=3*added,hypothetical_I122_read_headroom_after_I124_only=2097665-3*added,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),sort_keys=True))
if __name__=='__main__':main()
