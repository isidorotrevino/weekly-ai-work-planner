#!/usr/bin/env python3
"""Documentary I135 audit. Read JSON/Git/source AST only; never import target modules.

PASS verifies an explicitly insufficient P02 dossier, not runtime provenance,
platform capacity, E01 closure, independent acceptance or permission to execute.
"""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
BASE='6a9469ac2366b06651cd4a7b2f653d36cd07476c'
OUT=P+'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
PLAN=P+'D5-I132-E01-E05-evidence-plan.json'
SCOPE=P+'D5-PFC126-03-RESOURCE-SCOPE.json'
CONTRACT=P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
REFERENCE=P+'D5-I127-runtime-reference-manifest.json'
def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def blobs(commit,paths):
    paths=list(paths)
    raw=subprocess.check_output(['git','cat-file','--batch'],input=''.join(commit+':'+p+'\n' for p in paths).encode(),cwd=ROOT)
    stream=io.BytesIO(raw);result={}
    for p in paths:
        header=stream.readline().decode().split();assert len(header)==3 and header[1]=='blob',p
        body=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        result[p]=(header[0],body)
    assert stream.read()==b''
    return result

def source_surface(s):
    sources={**s['I122_and_original_source_pin_set']['runner_registered_input_pins'],**s['I122_and_original_source_pin_set']['observer_static_repo_import_superset']['file_pins']}
    sources={p:h for p,h in sources.items() if p.endswith('.py')}
    data=blobs(BASE,sorted(sources));rows=[];dynamic=[];blob_checks=[]
    for path in sorted(sources):
        oid,body=data[path];assert hashlib.sha256(body).hexdigest()==sources[path]==sha(path),path
        blob_checks.append(dict(path=path,sha256=sources[path],git_blob_oid=oid,bytes=len(body)))
        for n in ast.walk(ast.parse(body.decode())):
            if isinstance(n,ast.Import):
                rows.extend(dict(path=path,line=n.lineno,kind='import',module=a.name,level=0) for a in n.names)
            elif isinstance(n,ast.ImportFrom):rows.append(dict(path=path,line=n.lineno,kind='from',module=n.module,level=n.level))
            elif isinstance(n,ast.Call):
                name=ast.unparse(n.func)
                if name=='__import__' or name.endswith('.import_module'):
                    arg=n.args[0] if n.args else None
                    literal=arg.value if isinstance(arg,ast.Constant) and isinstance(arg.value,str) else None
                    dynamic.append(dict(path=path,line=n.lineno,call=name,literal_module=literal,argument_AST=ast.dump(arg,include_attributes=False) if arg is not None else None))
    rows.sort(key=lambda x:(x['path'],x['line'],str(x['module']),x['kind']))
    dynamic.sort(key=lambda x:(x['path'],x['line'],x['call']))
    return dict(source_pins=sources,file_count=len(sources),Git_blob_checks=blob_checks,import_syntax_count=len(rows),import_syntax_vector_sha256=digest(rows),named_modules=sorted({r['module'] for r in rows if r['module']}),dynamic_import_sites=dynamic,all_syntax_including_nested_and_unreachable=True,recursive_stdlib_or_native_closure_computed=False,actual_loaded_manifest=False,transitive_completeness_claimed=False)

def source_anchors():
    specs=[('worker_command','testing/prospective_capture_joint_i122/capture.py','Assign',119),('worker_Popen_environment','testing/prospective_capture_joint_i122/capture.py','Assign',120),('normalized_joint_invocation','testing/prospective_capture_joint_i122/capture.py','FunctionDef',100),('normalized_base_invocation','testing/prospective_capture/capture.py','FunctionDef',210),('relational_spawn_context','testing/D5/relational_support.py','Assign',61),('durable_spawn_context','testing/D5/durable_support.py','Assign',145)]
    out=[]
    for id,path,kind,line in specs:
        matches=[n for n in ast.walk(ast.parse((ROOT/path).read_text())) if type(n).__name__==kind and n.lineno==line];assert len(matches)==1,(id,line)
        n=matches[0];out.append(dict(id=id,path=path,sha256=sha(path),kind=kind,line=line,end_line=n.end_lineno,AST_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()))
    return out

def main():
    o=rd(OUT);r=rd(P+'D5-I135-P02-preparation-review.json');seal=rd(P+'D5-I135-integrity.json');s=rd(SCOPE);c=rd(CONTRACT);ref=rd(REFERENCE);plan=rd(PLAN);task=plan['tasks'][1]
    assert o['base_commit']==r['base_commit']==seal['base_commit']==BASE
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    prior=rd(P+'D5-I134-integrity.json')
    preserved={**prior['preserved_published148'],**prior['artifacts'],P+'D5-I134-integrity.json':sha(P+'D5-I134-integrity.json')}
    assert seal['preserved_published153']==preserved and len(preserved)==153
    for pinset in [preserved,seal['artifacts'],o['input_pins'],r['input_pins'],s['input_pins'],rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for p,h in pinset.items():assert sha(p)==h,p
    expected=set(seal['artifacts'])|{P+'D5-I135-integrity.json'}
    assert expected=={OUT,P+'D5-I135-P02-preparation-review.json',P+'D5-I135-audit.py',P+'D5-I135-integrity.json','docs/design/D5-I135-P02-RUNTIME-IDENTITY.md'}
    assert len(expected)==5 and len(seal['artifacts'])==4
    changed=set(git('diff',BASE,'--name-only').splitlines());untracked=set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed|untracked==expected,(changed,untracked,expected)
    if git('rev-parse','HEAD')!=BASE:assert not git('diff','HEAD','--name-only')
    historical=blobs(BASE,o['input_pins'])
    for p,h in o['input_pins'].items():assert hashlib.sha256(historical[p][1]).hexdigest()==h,p
    assert o['schema']==task['output_schema']=='d5.pfc126-03.e01-runtime-identity.v1' and OUT==task['planned_output']
    assert o['package_id']==task['id']=='P02' and len(task['required_specific_fields'])==6
    assert set(task['required_specific_fields'])<=set(o)
    assert o['plan_binding']==dict(path=PLAN,sha256=sha(PLAN),package_id='P02',task_record_canonical_sha256=digest(task))
    assert o['candidate_binding']==dict(path=CONTRACT,sha256=sha(CONTRACT),contract_id=c['contract_id'],subject=c['subject'],source_revision='I122-CANDIDATE-01')
    assert o['P01_dependency']['path']==SCOPE and o['P01_dependency']['sha256']==sha(SCOPE)
    assert o['P01_dependency']['technical_scope_conformance'] and not o['P01_dependency']['independent_acceptance_obtained']
    assert o['P01_dependency']['review_path']==P+'D5-I134-P01-documentary-review.json' and o['P01_dependency']['review_sha256']==sha(o['P01_dependency']['review_path'])
    assert o['status']=='PREPARED_INSUFFICIENT_RUNTIME_EVIDENCE_E01_OPEN_NOT_ADMITTED'
    assert o['historical_reference']==dict(path=REFERENCE,sha256=sha(REFERENCE),record=ref,new_collection=False,actual_target_identity_proved=False)
    assert ref['interpreter']['sha256']==c['runtime']['required_identity_pins']['interpreter']==c['runtime']['observed_reference']['interpreter_binary']['sha256']
    assert len(ref['stdlib_file_references'])==12 and len(ref['extension_references'])==5
    assert not ref['operator_attested'] and not ref['loaded_module_closure_complete']
    assert o['candidate_runtime_reference']==c['runtime']==s['runtime_platform_target_reference']['reference']
    assert o['source_import_surface']==source_surface(s) and o['source_anchors']==source_anchors()
    closure=o['exact_interpreter_stdlib_frozen_builtin_extension_closure']
    assert closure['status']=='INCOMPLETE_HISTORICAL_REFERENCE_ONLY' and closure['complete'] is False
    for k in ['actual_target_interpreter','complete_stdlib_manifest','complete_frozen_manifest','complete_builtin_manifest','complete_extension_manifest','selected_import_resolution_manifest']:assert closure[k] is None,k
    native=o['native_dependency_allocator_kernel_config_pins']
    for k in ['native_transitive_dependency_manifest','libc_binary_source_correspondence','allocator_backend_and_configuration','kernel_image_sha256','kernel_configuration_sha256','CPU_service_domain_identity']:assert native[k] is None,k
    assert native['historical_kernel_label']==ref['kernel_label'] and not native['correspondence_verified']
    corr=o['source_binary_build_correspondence']
    for k in ['authenticated_build_record','source_tree_digest','toolchain_dependency_manifest','build_flags_and_configuration','binary_source_mapping','verification_and_trust_chain']:assert corr[k] is None,k
    assert not corr['verified'] and corr['source_bytes_do_not_establish_binary_equivalence']
    target=o['actual_target_not_just_observed_local_reference']
    for k in ['target_image_or_release_digest','deployment_selection_record','actual_target_pin_set','runtime_platform_validity_interval']:assert target[k] is None,k
    assert not target['reference_promoted_to_target'] and not target['current_machine_sampled']
    provenance=o['producer_authority_signature_and_validity']
    assert provenance['preparer_identity']=='Codex assistant preparing I135 in this chat'
    assert provenance['required_custodian_role']==task['responsible_role'] and provenance['required_reviewer_role']==task['review_role']
    for k in ['custodian_identity','authority_record','signature','trust_anchor','signed_material_sha256','attestation_validity_interval','independent_reviewer_identity']:assert provenance[k] is None,k
    assert not provenance['preparer_is_attesting_custodian'] and not provenance['independent_acceptance']
    domain=o['clock_and_process_service_domain_identity']
    assert domain['required_clock']==c['time']['clock'] and domain['markers']==c['time']['normative_markers'] and domain['process_scope']==s['worker_heap_vs_other_process_scope']
    for k in ['actual_clock_implementation','actual_clock_domain_id','resolution_rate_and_synchronization_guarantees','coordinator_worker_child_runtime_mapping','platform_service_domain_id','compatible_P03_attestation']:assert domain[k] is None,k
    assert not domain['clock_or_service_verified'] and not domain['timestamps_collected']
    assert len(o['field_assessment'])==6
    assert [x['field'] for x in o['field_assessment']]==task['required_specific_fields']
    for row in o['field_assessment']:assert row['result']=='INSUFFICIENT_FOR_ACCEPTANCE' and not row['obligation_closed'] and row['required_pre_existing_material'] and row['reason']
    assert o['external_material_review']['authenticated_materials_supplied']==[] and not o['external_material_review']['global_absence_claimed'] and not o['external_material_review']['external_contacts_made']
    assert o['acceptance']['rule']==task['acceptance'] and o['acceptance']['rejection_rule']==task['rejection']
    assert o['acceptance']['preparation_complete'] and not o['acceptance']['accepted_as_runtime_identity'] and not o['acceptance']['E01_closed']
    assert o['acceptance']['remaining_P01_independent_acceptance'] and o['acceptance']['resource_obligations_closed']==0
    e=rd(P+'D5-I131-E01-E05-review.json')['obligations'][0]
    assert o['E01_criteria_disposition']==[dict(id=x['id'],inherited_result=x['result'],I135_result=x['result'],closed=False) for x in e['criteria']]
    assert r['output']==dict(path=OUT,sha256=sha(OUT),schema=o['schema'],evidence_kind=o['evidence_kind'],produced=True)
    assert r['input_pins'][OUT]==sha(OUT) and all(r['preparation_checks'].values())
    assert r['status']=='P02_PREPARATION_COMPLETE_INSUFFICIENT_EVIDENCE_NO_ADMISSION'
    assert not r['E01_E05_closed'] and r['E06']==o['E06']
    assert r['git_publication']['commit_and_push_all_requested']
    assert o['early_stop']['rule']==plan['early_stop_rules'][0] and o['early_stop']['affected_E01_E02_E03_E04_proofs_remain_open']
    assert not o['early_stop']['P03_P04_P06_or_later_evidence_produced'] and o['early_stop']['no_runtime_build_import_launch_or_probe_to_fill_gaps']
    assert r['counts']==dict(required_fields=6,insufficient_fields=6,historical_stdlib_file_references=12,historical_extension_records=5,source_files_parsed=o['source_import_surface']['file_count'],source_anchors=6,authenticated_runtime_materials=0,other_unproduced_packages=18)
    assert r['independent_review']==dict(accepted=False,reviewer_identity=None,no_independent_review_fabricated=True)
    for progress,planned in zip(r['package_progress'],plan['tasks'],strict=True):
        assert progress['package_id']==planned['id'] and progress['path']==planned['planned_output']
        exists=planned['id'] in ('P01','P02');assert progress['output_created']==exists and (ROOT/planned['planned_output']).exists()==exists
        assert progress['sha256']==(sha(planned['planned_output']) if exists else None)
    for state in [o['decision'],r['decision']]:
        assert state['certificate_unchanged']==rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')['status']=='IMPLEMENTED_NOT_ADMITTED'
        assert state['IR03']=='NOT_READY' and state['resource_obligations_closed']==0
        true_keys={'candidate_plan_P01_and_source_bytes_preserved','numeric_candidates_unchanged','P0_D1_D4_I1_I20_A52_unchanged','global_gaps_and_real_obligations_pending','I86_I89_I92_not_resumed'}
        for k in true_keys:assert state[k] is True,k
        for k,v in state.items():
            if k not in true_keys|{'certificate_unchanged','IR03','resource_obligations_closed'}:assert v is False,k
    assert o['non_execution_and_zero_transfer_policy']==s['non_execution_and_zero_transfer_policy']
    assert not o['E06']['execution_authorized'] and o['E06']['components_executed']==0 and o['E06']['status']=='SEPARATE_PENDING_NOT_RUN'
    for path in [P+'D5-JOINT-capture-authorization.json',P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:assert not (ROOT/path).exists(),path
    assert seal['source_only'] and not seal['proposal_enabled']
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I135',package='P02',preparation_complete=True,accepted_as_runtime_identity=False,insufficient_fields=6,source_files_parsed=o['source_import_surface']['file_count'],source_anchors=6,prior_published_files_preserved=153,new_files=5,product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))
if __name__=='__main__':main()
