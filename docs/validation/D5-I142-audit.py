#!/usr/bin/env python3
"""I142 H02 review audit. Historical consistency and fresh Git/AST reconstruction.

PASS is consistency of a negative original-heap dossier, not a verified bound.
"""
import ast
import hashlib
import io
import json
import subprocess
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
BASE='6f71d9a52376933c92340e64a6cdcca781a8610b'
OUT=P+'D5-PFC126-03-E02-H02.json'
REVIEW=P+'D5-I141-P04-H02-preparation-review.json'
PLAN=P+'D5-I132-E01-E05-evidence-plan.json'
CONTRACT=P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
SCOPE=P+'D5-PFC126-03-RESOURCE-SCOPE.json'
RUNTIME=P+'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
PLATFORM=P+'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
H01=P+'D5-PFC126-03-E02-H01.json'
PROJECTIONS=[(CONTRACT,'/heap/owner_budgets/1'),(CONTRACT,'/heap/complete_requested_upper_bytes'),(CONTRACT,'/runtime/required_identity_pins'),(P+'D5-I125-complete-heap-review.json','/required_terms/1'),(RUNTIME,'/acceptance'),(P+'D5-I136-P02-documentary-review.json','/acceptance'),(PLATFORM,'/acceptance'),(P+'D5-I138-P03-documentary-review.json','/acceptance'),(H01,'/acceptance'),(P+'D5-I140-P04-H01-documentary-review.json','/acceptance'),(SCOPE,'/worker_heap_vs_other_process_scope')]
def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pointer(v,p):
    for key in p.strip('/').split('/'):
        key=key.replace('~1','/').replace('~0','~');v=v[int(key)] if isinstance(v,list) else v[key]
    return v

def source_evidence(pins):
    paths=sorted(pins);stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=''.join(BASE+':'+p+'\n' for p in paths).encode()));data={};checks=[]
    for path in paths:
        h=stream.readline().decode().split();assert len(h)==3 and h[1]=='blob'
        size=int(h[2]);body=stream.read(size);assert len(body)==size and stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==pins[path]==sha(path),path;data[path]=body
        checks.append(dict(path=path,git_blob_oid=h[0],sha256=pins[path],bytes=size))
    assert not stream.read();s=json.loads(data[SCOPE]);originals=s['I122_and_original_source_pin_set']['runner_registered_input_pins'];python_pins={p:h for p,h in originals.items() if p.endswith('.py')}
    projections=[]
    for path,ptr in PROJECTIONS:
        v=pointer(json.loads(data[path]),ptr);projections.append(dict(path=path,sha256=pins[path],json_pointer=ptr,observed_value=v,canonical_sha256=digest(v),resource_obligation_closed=False))
    summaries=[];all_stores=[];trees={};indices={}
    paths_to_parse=set(python_pins)|{'testing/prospective_capture_joint_i122/atomic.py','testing/prospective_capture_joint_i122/capture.py'}
    for path in sorted(paths_to_parse):
        tree=ast.parse(data[path].decode());trees[path]=tree;index={}
        class Lexical(ast.NodeVisitor):
            def __init__(self):self.parts=[]
            def record(self,n):
                self.parts.append(n.name);index.setdefault('.'.join(self.parts),[]).append(n);self.generic_visit(n);self.parts.pop()
            visit_ClassDef=record
            visit_FunctionDef=record
            visit_AsyncFunctionDef=record
        Lexical().visit(tree);indices[path]=index
        if path not in python_pins:continue
        stores=sorted([dict(line=n.lineno,column=n.col_offset,end_line=n.end_lineno,attribute=n.attr,AST_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()) for n in ast.walk(tree) if isinstance(n,ast.Attribute) and isinstance(n.ctx,ast.Store) and isinstance(n.value,ast.Name) and n.value.id=='self'],key=lambda x:(x['line'],x['column'],x['attribute']))
        classes=[n for n in ast.walk(tree) if isinstance(n,ast.ClassDef)]
        summaries.append(dict(path=path,sha256=python_pins[path],class_declaration_count=len(classes),self_attribute_store_sites=len(stores),store_vector_sha256=digest(stores)));all_stores.extend(dict(path=path,**row) for row in stores)
    specs=[('clone_metadata','testing/prospective_capture_joint_i122/atomic.py','clone_metadata'),('opaque_originals','testing/prospective_capture_joint_i122/atomic.py','opaque_originals'),('atomic_fork','testing/prospective_capture_joint_i122/atomic.py','build.Recorder._fork'),('retained_record_values','testing/prospective_capture_joint_i122/atomic.py','build.Recorder._stop_fields'),('retained_oracle_values','testing/prospective_capture_joint_i122/capture.py','CausalState.retain'),('relational_fixture_constructor','source_ingest/durable_relational_fixture.py','RelationalLab.__init__'),('durable_fixture_constructor','source_ingest/durable_task_fixture.py','DurableLab.__init__'),('incremental_fixture_constructor','source_ingest/incremental_fixture.py','TemporaryFixtureLab.__init__'),('relational_parent_child_roots','testing/D5/relational_support.py','start'),('durable_parent_child_roots','testing/D5/durable_support.py','start')]
    anchors=[];nodes={}
    for id,path,symbol in specs:
        assert len(indices[path][symbol])==1;n=indices[path][symbol][0];nodes[id]=n
        anchors.append(dict(id=id,path=path,sha256=pins[path],symbol=symbol,line=n.lineno,end_line=n.end_lineno,AST_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()))
    clone=nodes['clone_metadata'];opaque_if=clone.body[2];assert isinstance(opaque_if,ast.If) and ast.unparse(opaque_if.test)=='key in opaque' and ast.unparse(opaque_if.body[0])=='return value'
    root_expressions=[ast.unparse(n.iter) for n in nodes['opaque_originals'].body if isinstance(n,ast.For)]
    assert root_expressions==['rec.record_refs','rec.record_baselines.values()','rec._causal_data.oracle_guards','rec.causal_sources.values()']
    assert any(isinstance(n,ast.Call) and ast.unparse(n)=='self.record_refs.append((binding, v))' for n in ast.walk(nodes['retained_record_values']))
    assert any(isinstance(n,ast.Call) and ast.unparse(n)=='self.oracle_guards.append((value, digest))' for n in ast.walk(nodes['retained_oracle_values']))
    return dict(commit=BASE,input_pin_count=len(checks),input_blob_checks=checks,projections=projections,registered_original_inputs=len(originals),original_python_files=len(python_pins),original_source_file_summaries=summaries,self_attribute_store_sites=len(all_stores),store_vector_sha256=digest(all_stores),source_anchors=anchors,opaque_root_expressions=root_expressions,opaque_clone_returns_original_identity=True,record_and_oracle_retention_sites_identified=True,source_index_is_not_complete_private_state_or_allocation_model=True,no_target_modules_executed=True)

def validate_preparation():
    o=rd(OUT);r=rd(REVIEW);seal=rd(P+'D5-I141-integrity.json');c=rd(CONTRACT);s=rd(SCOPE);plan=rd(PLAN);task=plan['tasks'][4];owner=c['heap']['owner_budgets'][1]
    assert o['base_commit']==r['base_commit']==seal['base_commit']==BASE and o['date']==r['date']==seal['date']=='2026-11-13'
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    prior=rd(P+'D5-I140-integrity.json');preserved={**prior['preserved_published178'],**prior['artifacts'],P+'D5-I140-integrity.json':sha(P+'D5-I140-integrity.json')}
    assert seal['preserved_published183']==preserved and len(preserved)==183
    for pins in [preserved,seal['artifacts'],o['input_pins'],r['input_pins'],rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert o['source_evidence']==source_evidence(o['input_pins']) and o['source_evidence']['registered_original_inputs']==79 and o['source_evidence']['original_python_files']==71
    assert len(o['source_evidence']['source_anchors'])==10 and len(o['source_evidence']['projections'])==11 and len(o['input_pins'])==140 and o['source_evidence']['self_attribute_store_sites']==477
    assert o['package_id']==task['id']=='P04-H02' and OUT==task['planned_output'] and o['schema']==task['output_schema']=='d5.pfc126-03.e02-h02.v1'
    assert o['plan_binding']==dict(path=PLAN,sha256=sha(PLAN),package_id='P04-H02',task_record_canonical_sha256=digest(task))
    assert o['candidate_binding']==dict(path=CONTRACT,sha256=sha(CONTRACT),contract_id=c['contract_id'],subject=c['subject'],source_revision='I122-CANDIDATE-01')
    assert set(task['required_specific_fields'])<=set(o) and len(task['required_specific_fields'])==9
    assert o['status']=='PREPARED_INSUFFICIENT_COMPLETE_ORIGINAL_HEAP_H02_E02_OPEN_NOT_ADMITTED'
    assert o['owner_id_metric_and_exact_units']==dict(owner_id='H02',owner=owner['owner'],metric=owner['metric'],unit='exact_integer_bytes',process='Original suite parent process inside the I122 worker; not the coordinator',candidate_budget_bytes=2147483648,scope_is_requirement_not_verified_bound=True)
    assert o['candidate_budget_bytes=2147483648']==o['candidate_budget_bytes']==owner['candidate_budget_bytes']==2*1024**3 and o['candidate_owner_record']==owner and owner['proof_upper_bytes'] is None
    inventory=o['complete_live_allocation_inventory'];assert not inventory['complete'] and len(inventory['required_classes'])==12 and inventory['kind']=='TWELVE_REQUIRED_ORIGINAL_COVERAGE_CLASSES_NOT_COMPLETE_ALLOCATION_PROOF' and inventory['residual_private_native_state_not_proved_absent']
    assert [x['id'] for x in inventory['required_classes']]==['R%02d'%i for i in range(1,13)]
    for row in inventory['required_classes']:
        for key in ['cardinality_upper','size_upper_bytes','maximum_live_upper_bytes','lifetime_derivation']:assert row[key] is None
        assert not row['verified'] and row['required_coverage'] and row['runtime_dependency']
    abi=o['source_ABI_allocator_dependencies'];assert abi['historical_runtime_reference']==c['runtime'] and not abi['exact_runtime_ABI_or_allocator_correspondence_verified']
    for key in ['accepted_target_closure','complete_private_native_object_model','accepted_ABI_size_model','allocator_metric_correspondence']:assert abi[key] is None
    deriv=o['cardinality_size_lifetime_derivations'];assert not deriv['complete'] and deriv['whole_owner_live_upper_bytes'] is None and deriv['CP03_serialized_operand_bounds_not_whole_original_heap'] and deriv['syntax_sites_not_live_object_cardinalities'] and deriv['cleanup_or_close_not_proof_of_root_release']
    overlap=o['overlap_alias_original_and_rejected_prefix_treatment'];assert overlap['inherited_scope']==s['worker_heap_vs_other_process_scope'] and overlap['source_applicability']==s['321_root_12_group_applicability']['I124_applicability']
    assert [x['other_owner'] for x in overlap['boundary_requirements']]==['H01']+['H%02d'%i for i in range(3,12)]
    assert not overlap['complete_ownership_alias_lifetime_proof'] and overlap['originals_opaque_not_memory_free'] and overlap['observer_reference_storage_does_not_pay_for_original_referents']
    for row in overlap['boundary_requirements']:assert not row['resolved']
    dep=o['explicit_assumptions_and_external_dependencies'];assert not dep['assumptions_verified'] and not dep['P02_exact_runtime_identity_accepted'] and not dep['P03_capacity_service_accepted'] and dep['capacity_and_H01_proof_are_not_substitutes_for_H02_demand']
    for key in ['complete_original_private_native_state_derivation','exact_runtime_size_lifetime_material','independent_runtime_memory_review']:assert dep[key] is None
    assert dep['inherited_P01_preconditions']==s['321_root_12_group_applicability']['original_source_route_preconditions']
    assert o['verified_upper_bytes_and_derivation']==dict(verified_upper_bytes=None,complete_derivation=None,evidence_pins={},verified=False,unknown_not_zero=True,CP03_payload_and_file_sizes_not_heap_upper=True)
    assert o['bound_fit_not_just_partial_payload']==dict(candidate_budget_bytes=2147483648,verified_complete_upper_bytes=None,fit_result='NOT_EVALUABLE_NO_COMPLETE_H02_BOUND',fits=None,slack_bytes=None,overbudget_proved=False,actual_unboundedness_proved=False,partial_payload_not_accepted=True)
    assert [x['field'] for x in o['field_assessment']]==task['required_specific_fields']
    for row in o['field_assessment']:assert row['result']==('DOCUMENTARY_DEFINITION_ONLY' if row['field'] in ['owner_id_metric_and_exact_units','candidate_budget_bytes=2147483648'] else 'INSUFFICIENT_FOR_ACCEPTANCE') and not row['resource_obligation_closed'] and row['basis']
    assert o['acceptance']==dict(rule=task['acceptance'],rejection_rule=task['rejection'],preparation_complete=True,accepted_as_complete_H02_proof=False,H02_verified=False,E02_closed=False,resource_obligations_closed=0,no_reserve_transfer=True)
    for d,path in zip(o['dependencies'],[SCOPE,RUNTIME],strict=True):assert d['path']==path and d['sha256']==sha(path) and not d['accepted_for_resource_closure']
    assert [x['id'] for x in o['dependencies']]==task['depends_on']==['P01','P02']
    assert not rd(RUNTIME)['acceptance']['accepted_as_runtime_identity'] and not rd(PLATFORM)['acceptance']['accepted_as_platform_evidence']
    auth=o['producer_and_review_provenance'];assert auth['producer_identity']=='Codex assistant preparing I141 in this chat' and auth['planned_author_role']==task['responsible_role'] and auth['planned_review_role']==task['review_role'] and not auth['independent_acceptance'] and auth['independent_reviewer_identity'] is None and not auth['runtime_custodian_authority_claimed']
    assert o['non_execution_and_zero_transfer_policy']==s['non_execution_and_zero_transfer_policy'] and o['reserve_accounting']==c['reserve_accounting']
    criteria=rd(P+'D5-I131-E01-E05-review.json')['obligations'][1]['criteria']
    assert o['E02_criterion_disposition']==[dict(id=x['id'],inherited_result=x['result'],I141_result=x['result'],closed=False) for x in criteria]
    assert r['output']==dict(path=OUT,sha256=sha(OUT),schema=o['schema'],evidence_kind=o['evidence_kind'],produced=True) and r['input_pins'][OUT]==sha(OUT)
    assert r['status']=='P04_H02_PREPARATION_COMPLETE_NO_COMPLETE_BOUND_NO_ADMISSION' and all(r['preparation_checks'].values())
    assert r['counts']==dict(required_fields=9,documentary_definition_fields=2,insufficient_fields=7,required_allocation_classes=12,unknown_inventory_values=48,owner_boundaries=10,original_registered_inputs=79,original_Python_files=71,source_anchors=10,evidence_projections=11,input_pins=len(o['input_pins']),other_unproduced_packages=15)
    assert r['independent_review']==dict(accepted=False,reviewer_identity=None,no_independent_review_fabricated=True)
    assert not o['external_material_scope']['external_contacts_made'] and not o['external_material_scope']['global_absence_claimed'] and not o['external_material_scope']['runtime_or_platform_sampled']
    assert dep['negative_dossier_does_not_bypass_P01_P02'] and dep['later_resource_closure_not_started']
    assert len(r['package_progress'])==20
    for progress,t in zip(r['package_progress'],plan['tasks'],strict=True):
        exists=t['id'] in ['P01','P02','P03','P04-H01','P04-H02'];assert (ROOT/t['planned_output']).exists()==exists and progress['output_created']==exists and progress['package_id']==t['id'] and progress['path']==t['planned_output'] and progress['sha256']==(sha(t['planned_output']) if exists else None)
    for d in [o['decision'],r['decision']]:
        keys={'candidate_plan_prior_packages_and_source_bytes_preserved','numeric_candidates_unchanged','P0_D1_D4_I1_I20_A52_unchanged','global_gaps_and_real_obligations_pending','I86_I89_I92_not_resumed'}
        assert d['certificate_unchanged']==rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')['status']=='IMPLEMENTED_NOT_ADMITTED' and d['IR03']=='NOT_READY' and d['resource_obligations_closed']==0
        for k in keys:assert d[k] is True
        for k,v in d.items():
            if k not in keys|{'certificate_unchanged','IR03','resource_obligations_closed'}:assert v is False,k
    assert o['E06']==r['E06']==dict(status='SEPARATE_PENDING_NOT_RUN',components_executed=0,execution_authorized=False)
    for p in [P+'D5-JOINT-capture-authorization.json',P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:assert not (ROOT/p).exists()
    assert seal['source_only'] and not seal['proposal_enabled'] and r['git_publication']['commit_and_push_all_requested']

REVIEW_BASE='eb13a382f38e0c3cac5e85c28cf4715211e6017a'
NEW_REVIEW=P+'D5-I142-P04-H02-documentary-review.json'
RECON=P+'D5-I142-P04-H02-source-reconstruction.json'
def blobs(commit,paths):
    paths=list(paths);stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=''.join(commit+':'+p+'\n' for p in paths).encode()));out={}
    for path in paths:
        header=stream.readline().decode().split();assert len(header)==3 and header[1]=='blob',path
        size=int(header[2]);body=stream.read(size);assert len(body)==size and stream.read(1)==b'\n';out[path]=(header[0],body)
    assert not stream.read();return out

def reconstruct():
    published=blobs(REVIEW_BASE,[OUT])[OUT];o=json.loads(published[1]);assert hashlib.sha256(published[1]).hexdigest()==sha(OUT)
    data=blobs(o['base_commit'],sorted(o['input_pins']));pinchecks=[]
    for path,h in sorted(o['input_pins'].items()):
        oid,body=data[path];assert hashlib.sha256(body).hexdigest()==h==sha(path)
        pinchecks.append(dict(path=path,preparation_git_blob_oid=oid,sha256=h,bytes=len(body)))
    projections=[];assert [(x['path'],x['json_pointer']) for x in o['source_evidence']['projections']]==PROJECTIONS
    for row in o['source_evidence']['projections']:
        value=pointer(json.loads(data[row['path']][1]),row['json_pointer'])
        assert row['observed_value']==value and row['canonical_sha256']==digest(value) and row['sha256']==o['input_pins'][row['path']]
        projections.append(dict(path=row['path'],sha256=row['sha256'],json_pointer=row['json_pointer'],recomputed_value_sha256=digest(value),matches_published_projection=True))
    scope=json.loads(data[SCOPE][1]);registered=scope['I122_and_original_source_pin_set']['runner_registered_input_pins'];sources={path:h for path,h in registered.items() if path.endswith('.py')}
    env=json.loads(data[P+'D5-I122-CAPTURE-REGISTRY.json'][1]);assert hashlib.sha256(data[env['base_registry']][1]).hexdigest()==env['base_registry_sha256']
    profile=json.loads(data[env['base_registry']][1]);profile.update(env['overrides']);assert profile['entry']['runner_effective_inputs']==registered
    rows=[];summaries=[];trees={};indices={}
    paths=set(sources)|{row['path'] for row in o['source_evidence']['source_anchors']}
    for path in sorted(paths):
        assert hashlib.sha256(data[path][1]).hexdigest()==o['input_pins'][path];tree=ast.parse(data[path][1].decode());trees[path]=tree;index={}
        class Lexical(ast.NodeVisitor):
            def __init__(self):self.parts=[]
            def record(self,n):
                self.parts.append(n.name);index.setdefault('.'.join(self.parts),[]).append(n);self.generic_visit(n);self.parts.pop()
            visit_ClassDef=record
            visit_FunctionDef=record
            visit_AsyncFunctionDef=record
        Lexical().visit(tree);indices[path]=index
        if path not in sources:continue
        found=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Attribute) and isinstance(node.ctx,ast.Store) and isinstance(node.value,ast.Name) and node.value.id=='self':found.append(dict(line=node.lineno,column=node.col_offset,end_line=node.end_lineno,attribute=node.attr,AST_sha256=hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()))
        found.sort(key=lambda x:(x['line'],x['column'],x['attribute']))
        summaries.append(dict(path=path,sha256=sources[path],class_declaration_count=sum(isinstance(n,ast.ClassDef) for n in ast.walk(tree)),self_attribute_store_sites=len(found),store_vector_sha256=digest(found)))
        rows.extend(dict(path=path,**row) for row in found)
    assert summaries==o['source_evidence']['original_source_file_summaries'] and len(rows)==o['source_evidence']['self_attribute_store_sites']==477
    assert digest(rows)==o['source_evidence']['store_vector_sha256']
    anchors=[];nodes={}
    for row in o['source_evidence']['source_anchors']:
        assert len(indices[row['path']][row['symbol']])==1
        node=indices[row['path']][row['symbol']][0];nodes[row['id']]=node
        assert (node.lineno,node.end_lineno)==(row['line'],row['end_line']) and hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()==row['AST_sha256']
        assert o['input_pins'][row['path']]==row['sha256']
        anchors.append(dict(id=row['id'],path=row['path'],symbol=row['symbol'],line=node.lineno,end_line=node.end_lineno,AST_sha256=row['AST_sha256'],lexical_binding_verified=True))
    clone=nodes['clone_metadata'];opaque_guards=[n for n in clone.body if isinstance(n,ast.If) and ast.unparse(n.test)=='key in opaque']
    assert len(opaque_guards)==1 and ast.unparse(opaque_guards[0].body[0])=='return value'
    assert ast.unparse(clone.body[1])=='key = id(value)' and clone.body.index(opaque_guards[0])==2
    loops=[n for n in nodes['opaque_originals'].body if isinstance(n,ast.For)];assert len(loops)==4
    selections=[]
    for loop in loops:
        assert len(loop.body)==1 and isinstance(loop.body[0],ast.Expr)
        call=loop.body[0].value;assert ast.unparse(call.func)=='result.add' and len(call.args)==1 and isinstance(call.args[0],ast.Call) and ast.unparse(call.args[0].func)=='id'
        selections.append(dict(iterable=ast.unparse(loop.iter),target=ast.unparse(loop.target),retained_value_expression=ast.unparse(call.args[0].args[0])))
    assert [x['iterable'] for x in selections]==o['source_evidence']['opaque_root_expressions']==['rec.record_refs','rec.record_baselines.values()','rec._causal_data.oracle_guards','rec.causal_sources.values()']
    assert [x['retained_value_expression'] for x in selections]==['value','values','value','values']
    assert any(isinstance(n,ast.Call) and ast.unparse(n)=='opaque_originals(self)' for n in ast.walk(nodes['atomic_fork']))
    assert any(isinstance(n,ast.Call) and ast.unparse(n)=='self.record_refs.append((binding, v))' for n in ast.walk(nodes['retained_record_values']))
    assert any(isinstance(n,ast.Call) and ast.unparse(n)=='self.oracle_guards.append((value, digest))' for n in ast.walk(nodes['retained_oracle_values']))
    parent_sites=[]
    for id in ['relational_parent_child_roots','durable_parent_child_roots']:
        fn=nodes[id]
        assert any(isinstance(n,ast.Call) and ast.unparse(n)=='CHILDREN.append(p)' for n in ast.walk(fn))
        assert isinstance(fn.body[-1],ast.Return) and ast.unparse(fn.body[-1].value)=='(p, parent)'
        parent_sites.append(dict(anchor=id,CHILDREN_retains_process_object=True,return_names=['p','parent'],close_is_not_complete_root_release_proof=True))
    unknowns=[];inventory=[]
    for i,row in enumerate(o['complete_live_allocation_inventory']['required_classes']):
        for key in ['cardinality_upper','size_upper_bytes','maximum_live_upper_bytes','lifetime_derivation']:
            assert row[key] is None;unknowns.append('/complete_live_allocation_inventory/required_classes/'+str(i)+'/'+key)
        assert not row['verified'];inventory.append(dict(id=row['id'],record_canonical_sha256=digest(row),unproved_cardinality_size_peak_and_lifetime=True))
    boundary=o['overlap_alias_original_and_rejected_prefix_treatment']['boundary_requirements']
    for row in boundary:assert not row['resolved']
    return dict(preparation_commit=o['base_commit'],published_commit=REVIEW_BASE,H02_published_blob_oid=published[0],H02_sha256=sha(OUT),input_pin_count=len(pinchecks),input_pin_checks=pinchecks,projection_checks=projections,registered_original_inputs=len(registered),original_Python_files=len(sources),original_pin_vector_sha256=digest(registered),self_attribute_store_sites=len(rows),store_vector_sha256=digest(rows),file_summary_vector_sha256=digest(summaries),source_anchor_checks=anchors,opaque_selections=selections,opaque_guard_returns_same_value_before_cloning=True,record_and_oracle_strong_reference_expressions_verified=True,parent_retention_source_sites=parent_sites,inventory_checks=inventory,unknown_inventory_pointers=unknowns,unknown_inventory_values=len(unknowns),boundary_record_sha256={x['other_owner']:digest(x) for x in boundary},field_record_sha256={x['field']:digest(o[x['field']]) for x in o['field_assessment']},source_only_not_lifetime_or_private_native_heap_proof=True)

def main():
    validate_preparation()
    z=rd(RECON);r=rd(NEW_REVIEW);seal=rd(P+'D5-I142-integrity.json');o=rd(OUT)
    assert z['base_commit']==r['base_commit']==seal['base_commit']==REVIEW_BASE and z['date']==r['date']==seal['date']=='2026-11-13'
    subprocess.check_call(['git','merge-base','--is-ancestor',REVIEW_BASE,'HEAD'],cwd=ROOT)
    prior=rd(P+'D5-I141-integrity.json');preserved={**prior['preserved_published183'],**prior['artifacts'],P+'D5-I141-integrity.json':sha(P+'D5-I141-integrity.json')}
    assert seal['preserved_published188']==preserved and len(preserved)==188
    for pins in [preserved,seal['artifacts'],z['input_pins'],r['input_pins']]:
        for path,h in pins.items():assert sha(path)==h,path
    expected={NEW_REVIEW,RECON,P+'D5-I142-audit.py',P+'D5-I142-integrity.json','docs/design/D5-I142-P04-H02-ORIGINALS-HEAP-REVIEW.md'}
    assert set(seal['artifacts'])|{P+'D5-I142-integrity.json'}==expected and len(seal['artifacts'])==4
    assert set(git('diff',REVIEW_BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())==expected
    if git('rev-parse','HEAD')!=REVIEW_BASE:assert not git('diff','HEAD','--name-only')
    assert z['reconstruction']==reconstruct() and z['reconstruction']['input_pin_count']==140 and z['reconstruction']['unknown_inventory_values']==48
    assert r['contract_id']==z['contract_id']==o['candidate_binding']['contract_id']=='PFC126-CANDIDATE-03'
    assert r['H02']==dict(path=OUT,sha256=sha(OUT),bytes_preserved=True) and r['plan_binding']==o['plan_binding'] and r['source_reconstruction']==dict(path=RECON,sha256=sha(RECON))
    assert r['status']=='REVIEW_COMPLETE_DOSSIER_CONFORMANT_H02_PROOF_REJECTED_NO_ADMISSION'
    assert r['field_disposition']==[dict(field=x['field'],I141_result=x['result'],I142_result='CONFIRMED_DOCUMENTARY_DEFINITION_ONLY' if x['result']=='DOCUMENTARY_DEFINITION_ONLY' else 'CONFIRMED_INSUFFICIENT_FOR_H02_ACCEPTANCE',record_canonical_sha256=digest(o[x['field']]),closed=False) for x in o['field_assessment']]
    assert len(r['checks'])==14 and [x['id'] for x in r['checks']]==['R%02d'%i for i in range(1,15)]
    for check in r['checks']:assert check['result']=='CONFORMANT_DOCUMENTARY_INSUFFICIENCY_JUDGMENT' and not check['resource_obligation_closed']
    assert r['blocking_dossier_defects']==[] and r['documentary_dossier_conformance'] and not r['H02_change_required']
    assert r['reviewer']['same_assistant_as_preparer'] and r['reviewer']['methodologically_separate_reconstruction'] and not r['reviewer']['actor_or_organizational_independence_attested'] and not r['reviewer']['runtime_custodian_authority_claimed']
    assert r['acceptance']==dict(review_completed=True,insufficiency_judgment_confirmed=True,accepted_as_complete_H02_proof=False,H02_verified=False,independent_documentary_acceptance=False,independent_reviewer_identity=None,E02_closed=False,E01_E05_closed=False,resource_obligations_closed=0,fit_or_overbudget_proved=False)
    assert r['E02_criterion_disposition']==[dict(id=x['id'],I142_result=x['inherited_result'],closed=False) for x in o['E02_criterion_disposition']]
    assert r['counts']==dict(H02_input_pins_checked=140,evidence_projections_checked=11,original_registered_inputs=79,original_Python_files_checked=71,self_attribute_store_sites=477,source_anchors_checked=10,explicit_opaque_root_selectors=4,parent_process_retention_sites=2,required_fields=9,documentary_definition_fields=2,insufficient_fields=7,required_allocation_classes=12,unknown_inventory_values=48,unresolved_owner_boundaries=10,E02_criteria_preserved=4,checks=14,other_unproduced_packages=15)
    assert r['E06']==o['E06'] and r['decision']==o['decision'] and r['other_packages_started']==0
    assert r['pending_independent_acceptance_and_P02_P03_not_bypassed'] and r['verified_complete_upper_bytes'] is None and r['fits'] is None and r['slack_bytes'] is None
    assert seal['source_only'] and not seal['proposal_enabled'] and r['git_publication']['commit_and_push_all_requested']
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I142',package='P04-H02',documentary_dossier_conformance=True,accepted_as_complete_H02_proof=False,independent_acceptance=False,Git_input_pins_checked=140,original_Python_files_checked=71,evidence_projections=11,source_anchors=10,required_fields=9,insufficient_fields=7,prior_published_files_preserved=188,new_files=5,product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))
if __name__=='__main__':main()
