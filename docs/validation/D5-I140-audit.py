#!/usr/bin/env python3
"""I140 H01 review audit: documentary consistency and fresh Git/AST reconstruction.

No product/component import, build, discovery, allocation measurement or runtime
probe. PASS confirms a prepared insufficiency dossier, not an admitted H01 upper.
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
BASE='451a629c53a7d0040b82e1bfba45fa10451795e9'
OUT=P+'D5-PFC126-03-E02-H01.json'
REVIEW=P+'D5-I139-P04-H01-preparation-review.json'
PLAN=P+'D5-I132-E01-E05-evidence-plan.json'
CONTRACT=P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
SCOPE=P+'D5-PFC126-03-RESOURCE-SCOPE.json'
RUNTIME=P+'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
PLATFORM=P+'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
PROJECTIONS=[(CONTRACT,'/heap/owner_budgets/0'),(CONTRACT,'/heap/complete_requested_upper_bytes'),(CONTRACT,'/runtime/required_identity_pins'),(RUNTIME,'/acceptance'),(P+'D5-I136-P02-documentary-review.json','/acceptance'),(PLATFORM,'/acceptance'),(P+'D5-I138-P03-documentary-review.json','/acceptance'),(P+'D5-I125-complete-heap-review.json','/required_terms/0'),(SCOPE,'/worker_heap_vs_other_process_scope')]
def rd(path):return json.loads((ROOT/path).read_text())
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pointer(v,path):
    for key in path.strip('/').split('/'):
        key=key.replace('~1','/').replace('~0','~');v=v[int(key)] if isinstance(v,list) else v[key]
    return v

def source_evidence(pins):
    paths=sorted(pins);stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=''.join(BASE+':'+p+'\n' for p in paths).encode()));data={};checks=[]
    for path in paths:
        h=stream.readline().decode().split();assert len(h)==3 and h[1]=='blob',path
        size=int(h[2]);body=stream.read(size);assert len(body)==size and stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==pins[path]==sha(path),path
        data[path]=body;checks.append(dict(path=path,git_blob_oid=h[0],sha256=pins[path],bytes=size))
    assert not stream.read()
    projections=[]
    for path,ptr in PROJECTIONS:
        value=pointer(json.loads(data[path]),ptr);projections.append(dict(path=path,sha256=pins[path],json_pointer=ptr,observed_value=value,canonical_sha256=digest(value),resource_obligation_closed=False))
    p02=json.loads(data[RUNTIME]);sources=p02['source_import_surface']['source_pins'];trees={};file_summaries=[];module_vector=[]
    for path,h in sorted(sources.items()):
        assert hashlib.sha256(data[path]).hexdigest()==h;tree=ast.parse(data[path].decode());trees[path]=tree
        rows=[dict(kind=type(n).__name__,line=n.lineno,end_line=n.end_lineno,AST_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()) for n in tree.body]
        file_summaries.append(dict(path=path,sha256=h,module_body_statement_count=len(rows),module_body_kinds=dict(Counter(x['kind'] for x in rows)),module_body_vector_sha256=digest(rows)))
        module_vector.extend(dict(path=path,**row) for row in rows)
    specs=[('worker_capture_import','testing/prospective_capture_joint_i122/worker.py','ImportFrom',9),('atomic_build_import','testing/prospective_capture_joint_i122/capture.py','ImportFrom',1713),('atomic_build_at_module_scope','testing/prospective_capture_joint_i122/capture.py','Assign',1714),('atomic_build_definition','testing/prospective_capture_joint_i122/atomic.py','FunctionDef',51),('worker_main_definition','testing/prospective_capture_joint_i122/worker.py','FunctionDef',63),('runner_dynamic_import','testing/prospective_capture_joint_i122/worker.py','Call',76)]
    anchors=[];nodes={}
    for id,path,kind,line in specs:
        matches=[n for n in ast.walk(trees[path]) if type(n).__name__==kind and n.lineno==line]
        if id=='runner_dynamic_import':matches=[n for n in matches if ast.unparse(n.func)=='importlib.import_module']
        assert len(matches)==1,id;n=matches[0];nodes[id]=n
        anchors.append(dict(id=id,path=path,sha256=sources[path],kind=kind,line=n.lineno,column=n.col_offset,end_line=n.end_lineno,AST_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()))
    assert ast.unparse(nodes['atomic_build_at_module_scope'].value)=='_atomic_build(sys.modules[__name__])'
    assert ast.unparse(nodes['runner_dynamic_import'].args[0])=="entry['runner_module']"
    return dict(commit=BASE,input_pin_count=len(checks),input_blob_checks=checks,projections=projections,source_file_count=len(sources),source_pins=sources,module_body_file_summaries=file_summaries,module_body_statement_count=len(module_vector),module_body_vector_sha256=digest(module_vector),source_anchors=anchors,module_scope_build_call_identified=True,source_syntax_not_allocation_or_loaded_closure=True,no_target_modules_executed=True)

def validate_preparation():
    o=rd(OUT);r=rd(REVIEW);seal=rd(P+'D5-I139-integrity.json');c=rd(CONTRACT);s=rd(SCOPE);plan=rd(PLAN);task=plan['tasks'][3];owner=c['heap']['owner_budgets'][0]
    assert o['base_commit']==r['base_commit']==seal['base_commit']==BASE
    assert o['date']==r['date']==seal['date']=='2026-11-13'
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    prior=rd(P+'D5-I138-integrity.json');preserved={**prior['preserved_published168'],**prior['artifacts'],P+'D5-I138-integrity.json':sha(P+'D5-I138-integrity.json')}
    assert seal['preserved_published173']==preserved and len(preserved)==173
    for pins in [preserved,seal['artifacts'],o['input_pins'],r['input_pins'],rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for path,h in pins.items():assert sha(path)==h,path
    assert o['source_evidence']==source_evidence(o['input_pins']) and o['source_evidence']['source_file_count']==79 and len(o['source_evidence']['source_anchors'])==6
    assert len(o['source_evidence']['projections'])==9 and len(o['input_pins'])==135 and o['source_evidence']['module_body_statement_count']==1745
    assert task['id']==o['package_id']=='P04-H01' and task['planned_output']==OUT and task['output_schema']==o['schema']=='d5.pfc126-03.e02-h01.v1'
    assert o['plan_binding']==dict(path=PLAN,sha256=sha(PLAN),package_id='P04-H01',task_record_canonical_sha256=digest(task))
    assert o['candidate_binding']==dict(path=CONTRACT,sha256=sha(CONTRACT),contract_id=c['contract_id'],subject=c['subject'],source_revision='I122-CANDIDATE-01')
    assert set(task['required_specific_fields'])<=set(o) and len(task['required_specific_fields'])==9
    assert o['status']=='PREPARED_INSUFFICIENT_EXACT_RUNTIME_H01_BOUND_E02_OPEN_NOT_ADMITTED'
    assert o['owner_id_metric_and_exact_units']==dict(owner_id='H01',owner=owner['owner'],metric=owner['metric'],unit='exact_integer_bytes',process='I122 worker only',candidate_budget_bytes=268435456,scope_is_requirement_not_verified_bound=True)
    assert o['candidate_budget_bytes=268435456']==o['candidate_budget_bytes']==owner['candidate_budget_bytes']==256*1024**2
    assert o['candidate_owner_record']==owner and owner['proof_upper_bytes'] is None
    abi=o['source_ABI_allocator_dependencies'];assert abi['historical_runtime_reference']==c['runtime'] and not abi['exact_runtime_ABI_or_allocator_correspondence_verified']
    for key in ['accepted_target_closure','accepted_ABI_size_model','accepted_native_library_allocation_model','allocator_requested_committed_correspondence']:assert abi[key] is None
    inventory=o['complete_live_allocation_inventory'];assert not inventory['complete'] and inventory['kind']=='TWELVE_REQUIRED_COVERAGE_CLASSES_NOT_COMPLETE_ALLOCATION_PROOF'
    assert len(inventory['required_classes'])==12 and [x['id'] for x in inventory['required_classes']]==['R%02d'%i for i in range(1,13)]
    for row in inventory['required_classes']:
        for key in ['cardinality_upper','size_upper_bytes','maximum_live_upper_bytes','lifetime_derivation']:assert row[key] is None
        assert not row['verified'] and row['runtime_dependency'] and row['required_coverage']
    deriv=o['cardinality_size_lifetime_derivations'];assert not deriv['complete'] and deriv['whole_owner_live_upper_bytes'] is None
    assert deriv['source_statement_counts_are_not_allocation_counts'] and deriv['no_immediate_GC_or_cache_release_assumed'] and deriv['all_success_and_applicable_rejection_prefixes_need_coverage']
    overlap=o['overlap_alias_original_and_rejected_prefix_treatment']
    assert overlap['inherited_scope']==s['worker_heap_vs_other_process_scope'] and overlap['source_applicability']==s['321_root_12_group_applicability']['I124_applicability']
    assert len(overlap['boundary_requirements'])==10 and [x['other_owner'] for x in overlap['boundary_requirements']]==['H%02d'%i for i in range(2,12)]
    assert not overlap['complete_ownership_alias_lifetime_proof'] and overlap['no_alias_discount_or_omission_without_proof'] and overlap['opaque_originals_not_memory_free']
    dependencies=o['explicit_assumptions_and_external_dependencies'];assert not dependencies['assumptions_verified'] and not dependencies['P02_exact_runtime_identity_accepted'] and not dependencies['P03_capacity_service_accepted']
    assert dependencies['P03_capacity_is_separate_from_owner_derivation'] and dependencies['negative_dossier_does_not_bypass_P01_P02'] and dependencies['later_resource_closure_not_started']
    for key in ['exact_runtime_build_and_native_sources','complete_allocation_size_lifetime_material','independent_runtime_memory_review']:assert dependencies[key] is None
    upper=o['verified_upper_bytes_and_derivation'];assert upper==dict(verified_upper_bytes=None,complete_derivation=None,evidence_pins={},verified=False,unknown_not_zero=True,file_sizes_or_selected_type_sizes_not_heap_upper=True)
    fit=o['bound_fit_not_just_partial_payload'];assert fit==dict(candidate_budget_bytes=268435456,verified_complete_upper_bytes=None,fit_result='NOT_EVALUABLE_NO_COMPLETE_H01_BOUND',fits=None,slack_bytes=None,overbudget_proved=False,actual_unboundedness_proved=False,partial_payload_not_accepted=True)
    assert len(o['field_assessment'])==9 and [x['field'] for x in o['field_assessment']]==task['required_specific_fields']
    documentary={'owner_id_metric_and_exact_units','candidate_budget_bytes=268435456'}
    for row in o['field_assessment']:assert row['result']==('DOCUMENTARY_DEFINITION_ONLY' if row['field'] in documentary else 'INSUFFICIENT_FOR_ACCEPTANCE') and not row['resource_obligation_closed'] and row['basis']
    assert o['acceptance']==dict(rule=task['acceptance'],rejection_rule=task['rejection'],preparation_complete=True,accepted_as_complete_H01_proof=False,H01_verified=False,E02_closed=False,resource_obligations_closed=0,no_reserve_transfer=True)
    assert o['dependencies'][0]['id']=='P01' and o['dependencies'][1]['id']=='P02'
    for d,path in zip(o['dependencies'],[SCOPE,RUNTIME],strict=True):assert d['path']==path and d['sha256']==sha(path) and not d['accepted_for_resource_closure']
    assert not rd(RUNTIME)['acceptance']['accepted_as_runtime_identity'] and not rd(PLATFORM)['acceptance']['accepted_as_platform_evidence']
    auth=o['producer_and_review_provenance'];assert auth['producer_identity']=='Codex assistant preparing I139 in this chat' and auth['planned_author_role']==task['responsible_role'] and auth['planned_review_role']==task['review_role']
    assert not auth['independent_acceptance'] and auth['independent_reviewer_identity'] is None and not auth['runtime_custodian_authority_claimed']
    assert o['non_execution_and_zero_transfer_policy']==s['non_execution_and_zero_transfer_policy'] and o['reserve_accounting']==c['reserve_accounting']
    criteria=rd(P+'D5-I131-E01-E05-review.json')['obligations'][1]['criteria']
    assert o['E02_criterion_disposition']==[dict(id=x['id'],inherited_result=x['result'],I139_result=x['result'],closed=False) for x in criteria]
    assert r['output']==dict(path=OUT,sha256=sha(OUT),schema=o['schema'],evidence_kind=o['evidence_kind'],produced=True) and r['input_pins'][OUT]==sha(OUT)
    assert r['independent_review']==dict(accepted=False,reviewer_identity=None,no_independent_review_fabricated=True)
    assert o['external_material_scope']['authenticated_exact_runtime_allocation_materials_supplied']==[] and not o['external_material_scope']['global_absence_claimed'] and not o['external_material_scope']['external_contacts_made'] and not o['external_material_scope']['runtime_or_platform_sampled']
    assert r['status']=='P04_H01_PREPARATION_COMPLETE_NO_COMPLETE_BOUND_NO_ADMISSION' and all(r['preparation_checks'].values())
    assert r['counts']==dict(required_fields=9,documentary_definition_fields=2,insufficient_fields=7,required_allocation_classes=12,unknown_inventory_values=48,owner_boundaries=10,source_files=79,source_anchors=6,evidence_projections=9,input_pins=len(o['input_pins']),other_unproduced_packages=16)
    for t in plan['tasks']:assert (ROOT/t['planned_output']).exists()==(t['id'] in ['P01','P02','P03','P04-H01'])
    assert len(r['package_progress'])==20
    for progress,t in zip(r['package_progress'],plan['tasks'],strict=True):
        exists=t['id'] in ['P01','P02','P03','P04-H01'];assert progress['package_id']==t['id'] and progress['path']==t['planned_output'] and progress['output_created']==exists and progress['sha256']==(sha(t['planned_output']) if exists else None)
    for d in [o['decision'],r['decision']]:
        true_keys={'candidate_plan_P01_P02_P03_and_source_bytes_preserved','numeric_candidates_unchanged','P0_D1_D4_I1_I20_A52_unchanged','global_gaps_and_real_obligations_pending','I86_I89_I92_not_resumed'}
        assert d['certificate_unchanged']==rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')['status']=='IMPLEMENTED_NOT_ADMITTED' and d['IR03']=='NOT_READY' and d['resource_obligations_closed']==0
        for key in true_keys:assert d[key] is True
        for key,value in d.items():
            if key not in true_keys|{'certificate_unchanged','IR03','resource_obligations_closed'}:assert value is False,key
    assert o['E06']==r['E06']==dict(status='SEPARATE_PENDING_NOT_RUN',components_executed=0,execution_authorized=False)
    for path in [P+'D5-JOINT-capture-authorization.json',P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:assert not (ROOT/path).exists(),path
    assert seal['source_only'] and not seal['proposal_enabled'] and r['git_publication']['commit_and_push_all_requested']

REVIEW_BASE='e5cb55f8dcf30fbab217609538ed959764b2ac31'
NEW_REVIEW=P+'D5-I140-P04-H01-documentary-review.json'
RECON=P+'D5-I140-P04-H01-source-reconstruction.json'
def blobs(commit,paths):
    paths=list(paths);stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=''.join(commit+':'+path+'\n' for path in paths).encode()));out={}
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
    projections=[]
    assert [(x['path'],x['json_pointer']) for x in o['source_evidence']['projections']]==PROJECTIONS
    for row in o['source_evidence']['projections']:
        value=pointer(json.loads(data[row['path']][1]),row['json_pointer'])
        assert row['observed_value']==value and row['canonical_sha256']==digest(value) and row['sha256']==o['input_pins'][row['path']]
        projections.append(dict(path=row['path'],sha256=row['sha256'],json_pointer=row['json_pointer'],recomputed_value_sha256=digest(value),matches_published_projection=True))
    p02=json.loads(data[RUNTIME][1]);scope=json.loads(data[SCOPE][1]);sources={**scope['I122_and_original_source_pin_set']['runner_registered_input_pins'],**scope['I122_and_original_source_pin_set']['observer_static_repo_import_superset']['file_pins']}
    sources={path:h for path,h in sources.items() if path.endswith('.py')}
    assert sources==p02['source_import_surface']['source_pins']==o['source_evidence']['source_pins']
    summaries=[];vector=[];trees={};indices={}
    for path,h in sorted(sources.items()):
        assert hashlib.sha256(data[path][1]).hexdigest()==h;tree=ast.parse(data[path][1].decode());trees[path]=tree
        rows=[]
        for node in tree.body:rows.append(dict(kind=type(node).__name__,line=node.lineno,end_line=node.end_lineno,AST_sha256=hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()))
        summaries.append(dict(path=path,sha256=h,module_body_statement_count=len(rows),module_body_kinds=dict(Counter(x['kind'] for x in rows)),module_body_vector_sha256=digest(rows)))
        vector.extend(dict(path=path,**row) for row in rows)
        index={}
        class Index(ast.NodeVisitor):
            def __init__(self):self.parts=[]
            def record(self,n):
                self.parts.append(n.name);index.setdefault('.'.join(self.parts),[]).append(n);self.generic_visit(n);self.parts.pop()
            visit_ClassDef=record
            visit_FunctionDef=record
            visit_AsyncFunctionDef=record
        Index().visit(tree);indices[path]=index
    assert summaries==o['source_evidence']['module_body_file_summaries'] and len(vector)==o['source_evidence']['module_body_statement_count']==1745
    assert digest(vector)==o['source_evidence']['module_body_vector_sha256']
    anchors=[];nodes={}
    scopes={'worker_capture_import':'<module>','atomic_build_import':'<module>','atomic_build_at_module_scope':'<module>','atomic_build_definition':'build','worker_main_definition':'main','runner_dynamic_import':'main'}
    for row in o['source_evidence']['source_anchors']:
        path=row['path'];name=scopes[row['id']]
        if name=='<module>':candidates=trees[path].body
        elif row['kind']=='FunctionDef':candidates=indices[path][name]
        else:
            assert len(indices[path][name])==1;candidates=ast.walk(indices[path][name][0])
        found=[n for n in candidates if type(n).__name__==row['kind'] and (n.lineno,n.col_offset,n.end_lineno)==(row['line'],row['column'],row['end_line'])]
        assert len(found)==1,row['id'];node=found[0];nodes[row['id']]=node
        assert hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()==row['AST_sha256'] and sources[path]==row['sha256']
        anchors.append(dict(id=row['id'],path=path,lexical_scope=name,line=node.lineno,end_line=node.end_lineno,AST_sha256=row['AST_sha256'],module_or_lexical_binding_verified=True))
    worker_import=nodes['worker_capture_import'];assert worker_import.level==0 and worker_import.module=='testing.prospective_capture_joint_i122'
    assert [(x.name,x.asname) for x in worker_import.names]==[('capture','p')]
    imp=nodes['atomic_build_import'];assert imp.level==1 and imp.module=='atomic' and [(x.name,x.asname) for x in imp.names]==[('build','_atomic_build')]
    call=nodes['atomic_build_at_module_scope'];assert ast.unparse(call.value)=='_atomic_build(sys.modules[__name__])'
    assert len(call.targets)==1 and ast.unparse(call.targets[0])=='(Recorder, LateBindings)'
    build=nodes['atomic_build_definition'];assert build.name=='build' and [arg.arg for arg in build.args.args]==['p']
    classes=[dict(name=n.name,line=n.lineno,end_line=n.end_lineno,AST_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()) for n in build.body if isinstance(n,ast.ClassDef)]
    assert [x['name'] for x in classes]==['Pages','CausalProxy','Bindings','Recorder']
    assert isinstance(build.body[-1],ast.Return) and ast.unparse(build.body[-1].value)=='(Recorder, Bindings)'
    runner=nodes['runner_dynamic_import'];assert ast.unparse(runner.func)=='importlib.import_module' and ast.unparse(runner.args[0])=="entry['runner_module']"
    inventory_checks=[];unknowns=[]
    for i,row in enumerate(o['complete_live_allocation_inventory']['required_classes']):
        for key in ['cardinality_upper','size_upper_bytes','maximum_live_upper_bytes','lifetime_derivation']:
            assert row[key] is None;unknowns.append('/complete_live_allocation_inventory/required_classes/'+str(i)+'/'+key)
        assert not row['verified'];inventory_checks.append(dict(id=row['id'],record_canonical_sha256=digest(row),unproved_cardinality_size_peak_and_lifetime=True))
    boundaries=o['overlap_alias_original_and_rejected_prefix_treatment']['boundary_requirements']
    for row in boundaries:assert not row['resolved']
    return dict(preparation_commit=o['base_commit'],published_commit=REVIEW_BASE,H01_published_blob_oid=published[0],H01_sha256=sha(OUT),input_pin_count=len(pinchecks),input_pin_checks=pinchecks,projection_checks=projections,source_files=len(sources),source_pin_vector_sha256=digest(sources),module_body_statements=len(vector),module_body_vector_sha256=digest(vector),file_summary_vector_sha256=digest(summaries),source_anchor_checks=anchors,atomic_build_source_chain=dict(relative_import_maps_build_to_alias=True,module_scope_call_and_tuple_assignment=True,class_declarations=classes,return_names=['Recorder','Bindings'],module_assignment_names=['Recorder','LateBindings'],declarations_not_live_allocation_counts=True,source_chain_not_executed_or_runtime_attested=True),inventory_checks=inventory_checks,unknown_inventory_pointers=unknowns,unknown_inventory_values=len(unknowns),boundary_record_sha256={x['other_owner']:digest(x) for x in boundaries},field_record_sha256={x['field']:digest(o[x['field']]) for x in o['field_assessment']},source_only_no_identity_or_heap_upper_proved=True)

def main():
    validate_preparation()
    z=rd(RECON);r=rd(NEW_REVIEW);seal=rd(P+'D5-I140-integrity.json');o=rd(OUT)
    assert z['base_commit']==r['base_commit']==seal['base_commit']==REVIEW_BASE
    assert z['date']==r['date']==seal['date']=='2026-11-13'
    subprocess.check_call(['git','merge-base','--is-ancestor',REVIEW_BASE,'HEAD'],cwd=ROOT)
    prior=rd(P+'D5-I139-integrity.json');preserved={**prior['preserved_published173'],**prior['artifacts'],P+'D5-I139-integrity.json':sha(P+'D5-I139-integrity.json')}
    assert seal['preserved_published178']==preserved and len(preserved)==178
    for pins in [preserved,seal['artifacts'],z['input_pins'],r['input_pins']]:
        for path,h in pins.items():assert sha(path)==h,path
    expected={NEW_REVIEW,RECON,P+'D5-I140-audit.py',P+'D5-I140-integrity.json','docs/design/D5-I140-P04-H01-RUNTIME-IMPORTS-HEAP-REVIEW.md'}
    assert set(seal['artifacts'])|{P+'D5-I140-integrity.json'}==expected and len(seal['artifacts'])==4
    assert set(git('diff',REVIEW_BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())==expected
    if git('rev-parse','HEAD')!=REVIEW_BASE:assert not git('diff','HEAD','--name-only')
    assert z['reconstruction']==reconstruct()
    assert z['reconstruction']['input_pin_count']==135 and z['reconstruction']['source_files']==79 and z['reconstruction']['unknown_inventory_values']==48
    assert r['contract_id']==z['contract_id']==o['candidate_binding']['contract_id']=='PFC126-CANDIDATE-03'
    assert r['H01']==dict(path=OUT,sha256=sha(OUT),bytes_preserved=True) and r['plan_binding']==o['plan_binding']
    assert r['source_reconstruction']==dict(path=RECON,sha256=sha(RECON))
    assert r['status']=='REVIEW_COMPLETE_DOSSIER_CONFORMANT_H01_PROOF_REJECTED_NO_ADMISSION'
    assert r['field_disposition']==[dict(field=x['field'],I139_result=x['result'],I140_result='CONFIRMED_DOCUMENTARY_DEFINITION_ONLY' if x['result']=='DOCUMENTARY_DEFINITION_ONLY' else 'CONFIRMED_INSUFFICIENT_FOR_H01_ACCEPTANCE',record_canonical_sha256=digest(o[x['field']]),closed=False) for x in o['field_assessment']]
    assert len(r['checks'])==14 and [x['id'] for x in r['checks']]==['R%02d'%i for i in range(1,15)]
    for check in r['checks']:assert check['result']=='CONFORMANT_DOCUMENTARY_INSUFFICIENCY_JUDGMENT' and not check['resource_obligation_closed']
    assert r['blocking_dossier_defects']==[] and r['documentary_dossier_conformance'] and not r['H01_change_required']
    assert r['reviewer']['same_assistant_as_preparer'] and r['reviewer']['methodologically_separate_reconstruction'] and not r['reviewer']['actor_or_organizational_independence_attested'] and not r['reviewer']['runtime_custodian_authority_claimed']
    assert r['acceptance']==dict(review_completed=True,insufficiency_judgment_confirmed=True,accepted_as_complete_H01_proof=False,H01_verified=False,independent_documentary_acceptance=False,independent_reviewer_identity=None,E02_closed=False,E01_E05_closed=False,resource_obligations_closed=0,fit_or_overbudget_proved=False)
    assert r['E02_criterion_disposition']==[dict(id=x['id'],I140_result=x['inherited_result'],closed=False) for x in o['E02_criterion_disposition']]
    assert r['counts']==dict(H01_input_pins_checked=135,evidence_projections_checked=9,source_files_checked=79,module_body_statements=1745,source_anchors_checked=6,required_fields=9,documentary_definition_fields=2,insufficient_fields=7,required_allocation_classes=12,unknown_inventory_values=48,unresolved_owner_boundaries=10,build_class_declarations=4,E02_criteria_preserved=4,checks=14,other_unproduced_packages=16)
    assert r['E06']==o['E06'] and r['decision']==o['decision'] and r['other_packages_started']==0
    assert r['pending_independent_acceptance_and_P02_P03_not_bypassed'] and r['verified_complete_upper_bytes'] is None and r['fits'] is None and r['slack_bytes'] is None
    assert seal['source_only'] and not seal['proposal_enabled'] and r['git_publication']['commit_and_push_all_requested']
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I140',package='P04-H01',documentary_dossier_conformance=True,accepted_as_complete_H01_proof=False,independent_acceptance=False,Git_input_pins_checked=135,source_files_checked=79,evidence_projections=9,source_anchors=6,required_fields=9,insufficient_fields=7,prior_published_files_preserved=178,new_files=5,product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))
if __name__=='__main__':main()
