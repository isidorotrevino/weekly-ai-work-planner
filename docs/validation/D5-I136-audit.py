#!/usr/bin/env python3
"""I136: documentary P02 review using Git blobs, JSON and AST only.

No candidate/product/component import, discovery, build, launch or runtime probe.
The PASS concerns consistency of a negative evidence judgment, never E01 closure.
"""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
BASE='a0e4c540bea9120b9efb4f17ff8daa2f448252a8'
OUT=P+'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
RECON=P+'D5-I136-P02-source-reconstruction.json'
REVIEW=P+'D5-I136-P02-documentary-review.json'
PLAN=P+'D5-I132-E01-E05-evidence-plan.json'
SCOPE=P+'D5-PFC126-03-RESOURCE-SCOPE.json'
CONTRACT=P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
REFERENCE=P+'D5-I127-runtime-reference-manifest.json'
UNKNOWN_FIELDS={
'exact_interpreter_stdlib_frozen_builtin_extension_closure':['actual_target_interpreter','complete_stdlib_manifest','complete_frozen_manifest','complete_builtin_manifest','complete_extension_manifest','selected_import_resolution_manifest'],
'native_dependency_allocator_kernel_config_pins':['native_transitive_dependency_manifest','libc_binary_source_correspondence','allocator_backend_and_configuration','kernel_image_sha256','kernel_configuration_sha256','CPU_service_domain_identity'],
'source_binary_build_correspondence':['authenticated_build_record','source_tree_digest','toolchain_dependency_manifest','build_flags_and_configuration','binary_source_mapping','verification_and_trust_chain'],
'actual_target_not_just_observed_local_reference':['target_image_or_release_digest','deployment_selection_record','actual_target_pin_set','runtime_platform_validity_interval'],
'producer_authority_signature_and_validity':['custodian_identity','authority_record','signature','trust_anchor','signed_material_sha256','attestation_validity_interval','independent_reviewer_identity'],
'clock_and_process_service_domain_identity':['actual_clock_implementation','actual_clock_domain_id','resolution_rate_and_synchronization_guarantees','coordinator_worker_child_runtime_mapping','platform_service_domain_id','compatible_P03_attestation']}
def rd(path):return json.loads((ROOT/path).read_text())
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def blobs(commit,paths):
    paths=list(paths);stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=''.join(commit+':'+p+'\n' for p in paths).encode()));result={}
    for path in paths:
        header=stream.readline().decode().split();assert len(header)==3 and header[1]=='blob',path
        size=int(header[2]);body=stream.read(size);assert len(body)==size and stream.read(1)==b'\n'
        result[path]=(header[0],body)
    assert not stream.read()
    return result

def reconstruct():
    published=blobs(BASE,[OUT])[OUT];o=json.loads(published[1]);prep=o['base_commit'];data=blobs(prep,sorted(o['input_pins']));pin_checks=[]
    for path,h in sorted(o['input_pins'].items()):
        oid,body=data[path];assert hashlib.sha256(body).hexdigest()==h==sha(path),path
        pin_checks.append(dict(path=path,preparation_blob_oid=oid,sha256=h,bytes=len(body)))
    assert hashlib.sha256(published[1]).hexdigest()==sha(OUT)
    s=json.loads(data[SCOPE][1]);source_pins={**s['I122_and_original_source_pin_set']['runner_registered_input_pins'],**s['I122_and_original_source_pin_set']['observer_static_repo_import_superset']['file_pins']}
    source_pins={path:h for path,h in source_pins.items() if path.endswith('.py')};trees={};syntax=[];dynamic=[];source_blobs=[]
    for path in sorted(source_pins):
        oid,body=data[path];assert hashlib.sha256(body).hexdigest()==source_pins[path]
        source_blobs.append(dict(path=path,sha256=source_pins[path],git_blob_oid=oid,bytes=len(body)))
        tree=ast.parse(body.decode());trees[path]=tree
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                for item in node.names:syntax.append(dict(path=path,line=node.lineno,kind='import',module=item.name,level=0))
            if isinstance(node,ast.ImportFrom):syntax.append(dict(path=path,line=node.lineno,kind='from',module=node.module,level=node.level))
            if isinstance(node,ast.Call):
                call=ast.unparse(node.func)
                if call=='__import__' or call.endswith('.import_module'):
                    arg=node.args[0] if node.args else None
                    literal=arg.value if isinstance(arg,ast.Constant) and isinstance(arg.value,str) else None
                    dynamic.append(dict(path=path,line=node.lineno,call=call,literal_module=literal,argument_AST=ast.dump(arg,include_attributes=False) if arg is not None else None))
    syntax.sort(key=lambda x:(x['path'],x['line'],str(x['module']),x['kind']));dynamic.sort(key=lambda x:(x['path'],x['line'],x['call']))
    surface=dict(source_pins=source_pins,file_count=len(source_pins),Git_blob_checks=source_blobs,import_syntax_count=len(syntax),import_syntax_vector_sha256=digest(syntax),named_modules=sorted({x['module'] for x in syntax if x['module']}),dynamic_import_sites=dynamic,all_syntax_including_nested_and_unreachable=True,recursive_stdlib_or_native_closure_computed=False,actual_loaded_manifest=False,transitive_completeness_claimed=False)
    assert surface==o['source_import_surface']
    anchored=[];nodes={}
    for row in o['source_anchors']:
        found=[n for n in ast.walk(trees[row['path']]) if type(n).__name__==row['kind'] and n.lineno==row['line'] and n.end_lineno==row['end_line']]
        assert len(found)==1,row['id'];node=found[0]
        assert hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()==row['AST_sha256'] and source_pins[row['path']]==row['sha256']
        nodes[row['id']]=node;anchored.append(row)
    # Inspect actual AST semantics as well as the hashes; no target call is run.
    cmd=nodes['worker_command'].value
    assert isinstance(cmd,ast.List) and ast.unparse(cmd.elts[0])=='sys.executable'
    assert [x.value for x in cmd.elts[1:5]]==['-B','-m','testing.prospective_capture_joint_i122.worker','P01']
    popen=nodes['worker_Popen_environment'].value;assert ast.unparse(popen.func)=='c.subprocess.Popen' and ast.unparse(popen.args[0])=='cmd'
    keys={x.arg:x.value for x in popen.keywords};env=keys['env']
    assert ast.unparse(env.func)=='dict' and {x.arg:ast.unparse(x.value) for x in env.keywords}=={'PATH':'os.defpath','LANG':"'C.UTF-8'",'LC_ALL':"'C.UTF-8'",'PYTHONNOUSERSITE':"'1'",'PYTHONDONTWRITEBYTECODE':"'1'",'PYTHONIOENCODING':"'utf-8'"}
    assert ast.literal_eval(keys['start_new_session']) is True
    base=nodes['normalized_base_invocation'];path_hash=[n.value for n in ast.walk(base) if isinstance(n,ast.keyword) and n.arg=='path_sha256']
    assert len(path_hash)==1 and ast.unparse(path_hash[0])=='sha(os.fsencode(sys.executable))'
    joint=nodes['normalized_joint_invocation'];command_assigns=[n for n in ast.walk(joint) if isinstance(n,ast.Assign) and any(ast.unparse(t)=="out['command']" for t in n.targets)]
    assert len(command_assigns)==1 and ast.literal_eval(command_assigns[0].value)==['python3','-B','-m','testing.prospective_capture_joint_i122.worker','P01']
    for name in ['relational_spawn_context','durable_spawn_context']:assert ast.unparse(nodes[name].value)=="multiprocessing.get_context('spawn')"
    envreg=json.loads(data[P+'D5-I122-CAPTURE-REGISTRY.json'][1]);assert hashlib.sha256(data[envreg['base_registry']][1]).hexdigest()==envreg['base_registry_sha256']
    profile=json.loads(data[envreg['base_registry']][1]);profile.update(envreg['overrides']);entry=profile['entry']
    literals=[row for row in dynamic if row['literal_module'] is not None];unresolved=[row for row in dynamic if row['literal_module'] is None]
    assert len(literals)==12 and len(unresolved)==1
    expression=unresolved[0];assert expression['path']=='testing/prospective_capture_joint_i122/worker.py' and expression['call']=='importlib.import_module'
    assert expression['argument_AST']==ast.dump(ast.parse("entry['runner_module']",mode='eval').body,include_attributes=False)
    assert entry['runner_module']=='testing.D5.run_relational_durable_lab' and entry['runner_path']=='testing/D5/run_relational_durable_lab.py'
    assert source_pins[entry['runner_path']]==entry['runner_sha256']
    unknowns=[];field_records=[]
    for field,names in UNKNOWN_FIELDS.items():
        for name in names:
            assert o[field][name] is None,(field,name);unknowns.append('/'+field+'/'+name)
        field_records.append(dict(field=field,record_canonical_sha256=digest(o[field]),unknown_pointers=['/'+field+'/'+name for name in names],result='INSUFFICIENT_FOR_ACCEPTANCE'))
    return dict(preparation_commit=prep,published_commit=BASE,P02_blob_oid=published[0],P02_sha256=sha(OUT),input_pin_checks=pin_checks,input_pin_count=len(pin_checks),source_files=surface['file_count'],source_pin_vector_sha256=digest(source_pins),import_syntax_count=len(syntax),import_syntax_vector_sha256=digest(syntax),named_modules=surface['named_modules'],dynamic_import_sites=dynamic,literal_dynamic_sites=len(literals),expression_dynamic_sites=len(unresolved),declared_runner_binding=dict(module=entry['runner_module'],path=entry['runner_path'],sha256=entry['runner_sha256'],registry_path=P+'D5-I122-CAPTURE-REGISTRY.json',registry_sha256=o['input_pins'][P+'D5-I122-CAPTURE-REGISTRY.json'],declaration_not_loaded_identity=True),source_anchors=anchored,source_anchor_semantics_checked=True,field_records=field_records,unknown_pointers=unknowns,unknown_count=len(unknowns),source_and_historical_reference_only=True,actor_independence_attested=False,actual_runtime_identity_verified=False,product_or_components_executed=False)

def main():
    z=rd(RECON);r=rd(REVIEW);seal=rd(P+'D5-I136-integrity.json');o=rd(OUT);s=rd(SCOPE);plan=rd(PLAN);task=plan['tasks'][1];c=rd(CONTRACT);ref=rd(REFERENCE)
    assert z['base_commit']==r['base_commit']==seal['base_commit']==BASE
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    prior=rd(P+'D5-I135-integrity.json');preserved={**prior['preserved_published153'],**prior['artifacts'],P+'D5-I135-integrity.json':sha(P+'D5-I135-integrity.json')}
    assert seal['preserved_published158']==preserved and len(preserved)==158
    for pinset in [preserved,seal['artifacts'],z['input_pins'],r['input_pins'],o['input_pins'],rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for path,h in pinset.items():assert sha(path)==h,path
    expected={RECON,REVIEW,P+'D5-I136-audit.py',P+'D5-I136-integrity.json','docs/design/D5-I136-P02-RUNTIME-IDENTITY-REVIEW.md'}
    assert set(seal['artifacts'])|{P+'D5-I136-integrity.json'}==expected and len(seal['artifacts'])==4
    assert set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())==expected
    if git('rev-parse','HEAD')!=BASE:assert not git('diff','HEAD','--name-only')
    assert z['reconstruction']==reconstruct()
    assert z['reconstruction']['input_pin_count']==125 and z['reconstruction']['unknown_count']==35 and z['reconstruction']['source_files']==79
    assert z['reconstruction']['import_syntax_count']==770 and len(z['reconstruction']['dynamic_import_sites'])==13 and len(z['reconstruction']['source_anchors'])==6
    assert OUT==task['planned_output'] and o['schema']==task['output_schema'] and o['package_id']=='P02'
    assert o['plan_binding']==dict(path=PLAN,sha256=sha(PLAN),package_id='P02',task_record_canonical_sha256=digest(task))
    assert o['candidate_binding']==dict(path=CONTRACT,sha256=sha(CONTRACT),contract_id=c['contract_id'],subject=c['subject'],source_revision='I122-CANDIDATE-01')
    assert r['contract_id']==z['contract_id']==c['contract_id']=='PFC126-CANDIDATE-03'
    assert r['P02']==dict(path=OUT,sha256=sha(OUT),bytes_preserved=True)
    assert r['source_reconstruction']==dict(path=RECON,sha256=sha(RECON))
    assert r['plan_binding']==o['plan_binding']
    assert list(UNKNOWN_FIELDS)==task['required_specific_fields'] and len(task['required_specific_fields'])==6
    assert o['historical_reference']==dict(path=REFERENCE,sha256=sha(REFERENCE),record=ref,new_collection=False,actual_target_identity_proved=False)
    assert o['candidate_runtime_reference']==c['runtime']==s['runtime_platform_target_reference']['reference']
    assert ref['interpreter']['sha256']==c['runtime']['required_identity_pins']['interpreter']
    assert len(ref['stdlib_file_references'])==12 and len(ref['extension_references'])==5
    assert {x['name'] for x in ref['extension_references'] if x['declared_builtin']}=={'_json','_struct','_posixsubprocess'}
    assert {x['name'] for x in ref['extension_references'] if x['external_file_candidates']}=={'_hashlib','_multiprocessing'}
    assert not ref['operator_attested'] and not ref['loaded_module_closure_complete'] and not ref['kernel_label']['is_kernel_binary_pin']
    assert o['exact_interpreter_stdlib_frozen_builtin_extension_closure']['historical_interpreter_pin']==ref['interpreter']
    assert not o['exact_interpreter_stdlib_frozen_builtin_extension_closure']['complete'] and not o['native_dependency_allocator_kernel_config_pins']['correspondence_verified'] and not o['source_binary_build_correspondence']['verified']
    assert not o['actual_target_not_just_observed_local_reference']['reference_promoted_to_target'] and not o['actual_target_not_just_observed_local_reference']['current_machine_sampled']
    domain=o['clock_and_process_service_domain_identity'];assert domain['required_clock']==c['time']['clock'] and domain['markers']==c['time']['normative_markers'] and domain['process_scope']==s['worker_heap_vs_other_process_scope']
    assert not domain['clock_or_service_verified'] and not domain['timestamps_collected']
    p=o['producer_authority_signature_and_validity'];assert p['preparer_identity']=='Codex assistant preparing I135 in this chat' and not p['preparer_is_attesting_custodian'] and not p['independent_acceptance']
    assert p['required_custodian_role']==task['responsible_role'] and p['required_reviewer_role']==task['review_role']
    assert o['P01_dependency']['path']==SCOPE and o['P01_dependency']['sha256']==sha(SCOPE)
    oldreview=rd(P+'D5-I134-P01-documentary-review.json')
    assert o['P01_dependency']['technical_scope_conformance']==oldreview['technical_scope_conformance'] and not o['P01_dependency']['independent_acceptance_obtained'] and not oldreview['acceptance']['independent_documentary_acceptance']
    assert len(o['field_assessment'])==6 and [x['field'] for x in o['field_assessment']]==task['required_specific_fields']
    for x in o['field_assessment']:assert x['result']=='INSUFFICIENT_FOR_ACCEPTANCE' and not x['obligation_closed'] and x['reason'] and x['required_pre_existing_material']
    assert r['field_disposition']==[dict(field=x['field'],I135_result=x['result'],I136_result='CONFIRMED_INSUFFICIENT_FOR_RUNTIME_ACCEPTANCE',evidence_record_canonical_sha256=digest(o[x['field']]),closed=False) for x in o['field_assessment']]
    assert o['acceptance']['rule']==task['acceptance'] and o['acceptance']['rejection_rule']==task['rejection'] and o['acceptance']['preparation_complete'] and not o['acceptance']['accepted_as_runtime_identity'] and not o['acceptance']['E01_closed']
    assert o['acceptance']['resource_obligations_closed']==0 and o['acceptance']['remaining_P01_independent_acceptance']
    assert o['external_material_review']['authenticated_materials_supplied']==[] and not o['external_material_review']['global_absence_claimed'] and not o['external_material_review']['external_contacts_made']
    criteria=rd(P+'D5-I131-E01-E05-review.json')['obligations'][0]['criteria']
    assert o['E01_criteria_disposition']==[dict(id=x['id'],inherited_result=x['result'],I135_result=x['result'],closed=False) for x in criteria]
    assert r['E01_criteria_disposition']==[dict(id=x['id'],I136_result=x['result'],closed=False) for x in criteria]
    assert o['early_stop']['rule']==plan['early_stop_rules'][0] and o['early_stop']['affected_E01_E02_E03_E04_proofs_remain_open'] and not o['early_stop']['P03_P04_P06_or_later_evidence_produced']
    assert o['non_execution_and_zero_transfer_policy']==s['non_execution_and_zero_transfer_policy']
    assert o['E06']==dict(status='SEPARATE_PENDING_NOT_RUN',components_executed=0,execution_authorized=False)
    for t in plan['tasks']:assert (ROOT/t['planned_output']).exists()==(t['id'] in ('P01','P02'))
    assert len(r['checks'])==12 and [x['id'] for x in r['checks']]==['R%02d'%i for i in range(1,13)]
    for check in r['checks']:assert check['result']=='CONFORMANT_DOCUMENTARY_INSUFFICIENCY_JUDGMENT' and not check['resource_obligation_closed']
    assert r['blocking_dossier_defects']==[] and r['documentary_dossier_conformance'] and not r['P02_change_required']
    assert r['reviewer']['same_assistant_as_preparer'] and r['reviewer']['methodologically_separate_reconstruction'] and not r['reviewer']['actor_or_organizational_independence_attested'] and not r['reviewer']['custodian_authority_claimed']
    assert r['status']=='REVIEW_COMPLETE_DOSSIER_CONFORMANT_RUNTIME_IDENTITY_REJECTED_E01_OPEN'
    assert r['acceptance']==dict(review_completed=True,insufficiency_judgment_confirmed=True,accepted_as_runtime_identity=False,independent_documentary_acceptance=False,independent_reviewer_identity=None,E01_closed=False,E01_E05_closed=False,resource_obligations_closed=0)
    assert r['other_packages_started']==0 and r['other_unproduced_packages']==18
    assert r['counts']==dict(P02_input_pins_checked=125,source_files_checked=79,import_syntax=770,dynamic_import_sites=13,literal_dynamic_sites=12,expression_dynamic_sites=1,source_anchors=6,required_fields=6,unknown_identity_provenance_fields=35,criteria_preserved=4,checks=12)
    for d in [r['decision'],o['decision']]:
        assert d['certificate_unchanged']==rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')['status']=='IMPLEMENTED_NOT_ADMITTED' and d['IR03']=='NOT_READY' and d['resource_obligations_closed']==0
        true_keys={'candidate_plan_P01_and_source_bytes_preserved','numeric_candidates_unchanged','P0_D1_D4_I1_I20_A52_unchanged','global_gaps_and_real_obligations_pending','I86_I89_I92_not_resumed'}
        for key in true_keys:assert d[key] is True,key
        for key,value in d.items():
            if key not in true_keys|{'certificate_unchanged','IR03','resource_obligations_closed'}:assert value is False,key
    for path in [P+'D5-JOINT-capture-authorization.json',P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:assert not (ROOT/path).exists(),path
    assert seal['source_only'] and not seal['proposal_enabled'] and r['git_publication']['commit_and_push_all_requested']
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I136',package='P02',documentary_dossier_conformance=True,accepted_as_runtime_identity=False,independent_acceptance=False,Git_input_pins_checked=125,source_files_checked=79,source_anchors=6,insufficient_fields=6,unknown_identity_provenance_fields=35,prior_published_files_preserved=158,new_files=5,product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))
if __name__=='__main__':main()
