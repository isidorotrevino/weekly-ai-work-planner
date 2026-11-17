#!/usr/bin/env python3
"""I207 missing-caller documentary checks only; no backend/process/components."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from contextlib import contextmanager
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='49f7152be801d69a4c960567ba6f1a4d8b311d8b'
DOS=P+'D5-I193-CE05-CALLER-CONSTRUCTOR-DOMAIN-CANDIDATE.json'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json';CHECK=P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json';PACK=P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CE04=P+'D5-I193-CE04-IMAGE-SOURCE-BASELINE-CANDIDATE.json';CE03=P+'D5-I193-CE03-HUMAN-IDENTITY-ROSTER-CANDIDATE.json';CE01=P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
PRIOR_REVIEW=P+'D5-I206-I205-documentary-review.json';PRIOR_RECON=P+'D5-I206-I205-source-reconstruction.json'
PRIOR_AUDIT=P+'D5-I206-audit.py';PRIOR_SEAL=P+'D5-I206-integrity.json';PRIOR_DOC='docs/design/D5-I206-I205-CE04-REVIEW.md'
PRIOR_FILES={PRIOR_REVIEW,PRIOR_RECON,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
PREP=P+'D5-I207-preparation-review.json';AUDIT=P+'D5-I207-audit.py';SEAL=P+'D5-I207-integrity.json'
DOC='docs/design/D5-I207-CE05-CALLER-CONSTRUCTOR-DOMAIN.md';FILES={DOS,PREP,AUDIT,SEAL,DOC}


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pin(p,q=''):return dict(path=p,sha256=sha(p),json_pointer=q)


@contextmanager
def predecessor_CE05_presence_as_of_base():
    """Exact CE05 historical query only; no prior bytes/trust checks changed."""
    assert git('ls-tree','--name-only',BASE,'--',DOS)==''
    original=Path.exists;target=ROOT/DOS;assert original(target)
    def historical_exists(path):return False if path==target else original(path)
    Path.exists=historical_exists
    try:yield
    finally:Path.exists=original
    assert target.exists()


def verify_git_blobs(pins):
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()))
    for p,h in sorted(pins.items()):
        header=stream.readline().decode().split();assert len(header)==3 and header[1]=='blob',p
        body=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    assert stream.read()==b''


def check_caller_boundary(d,plan):
    rows=d['caller_constructor_requirements'];assert [r['id'] for r in rows]==['CC%02d'%i for i in range(1,13)]
    assert [r['consumer_step'] for r in rows]==['CE05']*6+['CE06','CE07','CE08','CE09','CE10','CE12']
    phases=d['step_obligation_boundary']
    for name,ids in [('CE05',['CC%02d'%i for i in range(1,7)]),('CE06',['CC07']),('CE07',['CC08']),('CE08',['CC09']),('CE09',['CC10']),('CE10',['CC11']),('CE12',['CC12'])]:
        s=next(s for s in plan['steps'] if s['id']==name)
        assert phases[name]['plan_source']==pin(PLAN,'/steps/'+str(plan['steps'].index(s)))
        assert phases[name]['required_step_ids']==s['depends_on'] and phases[name]['requirement_ids']==ids
        assert phases[name]['actual_acceptance'] is False and phases[name]['current_execution_authorized'] is False
        assert phases[name]['actual_dossier_created']==(name=='CE05')
    a=phases['CE05'];assert a['baseline_only_not_final_caller_record']
    assert not a['final_actor_image_caller_hash_or_C_mapping_required']
    assert a['later_platform_resources_C_mapping_or_construction_not_reverse_CE05_dependency']
    assert a['appointment_or_bootstrap_permission_is_not_execution']
    b=phases['CE08'];assert b['final_record_order']==plan['steps'][7]['record_families']
    for k in ['all_actual_authors_and_antecedents_required_before_freeze','final_caller_before_C_required','refresh_is_not_active_capture_inputs_rebind']:assert b[k] is True
    last=phases['CE12'];assert last['external_prerequisites_for_receipt']==plan['closure_boundaries']['external_prerequisites_for_receipt']
    assert last['no_claim_or_spawn_before_full_admission_and_separate_authorization'] and last['CE11_does_not_depend_on_CE12']
    policy=d['identity_and_capability_policy']
    for k in ['human_requester_and_software_principal_namespaces_separate','authentic_prior_actor_image_domain_constructor_provenance_required',
        'UID_PID_fd_env_module_cwd_key_hash_or_appointment_alone_is_not_capability','literal_is_schema_policy_not_issued_permission',
        'future_bundle_may_not_supply_sole_prior_authentication','no_extra_channel_fd_argv_helper_file_env_or_attestation_implicit',
        'expanded_real_backend_requires_rejection_or_separately_reviewed_versioned_scope_cost_work','no_C_or_bundle_hash_field_added_to_caller_schema_or_wire']:assert policy[k] is True
    assert not policy['actual_backend_or_principal_selected']
    assert policy['actual_C_projection_consumer']=='CE09' and policy['actual_unique_mapping_consumer']=='CE10' and policy['actual_protected_construction_consumer']=='CE12'
    t=d['inherited_transport_policy'];assert t['explicit_control_pipe_count']==2 and t['observed_worker_operand_count']==6
    assert t['actual_fd_PID_UID_domain_values'] is None and not t['actual_channel_origin_or_descriptor_ownership_verified'] and not t['actual_process_or_endpoint_probe_performed']
    assert t['worker_intrinsic_origin_is_not_received_as_new_mapping_or_receipt']
    state=d['actual_caller_state'];false_fields={'actual_caller_or_backend_selected','actual_caller_or_actor_enrolled',
        'actual_constructor_or_channel_created','actual_identity_or_custody_verified','actual_final_caller_record_frozen',
        'actual_mapping_or_claim_verified','actual_functional_execution_permitted'}
    assert len(state)==31
    for k,v in state.items():
        if k in false_fields:assert v is False
        else:assert v is None
    assert d['current_effect']['CE05_accepted'] is False and d['current_effect']['actual_claim_or_worker_created'] is False
    for r in rows:
        for k in ['actual_provider_identity','actual_provider_locator','actual_body_sha256','actual_body_bytes','actual_appointment','actual_acceptance_record']:assert r[k] is None
        assert r['status']=='MISSING_NOT_EVALUATED' and not r['accepted'] and not r['contact_authorized_now']
    return dict(CE05_baseline_rows=6,deferred_rows=6,human_and_software_namespaces_separate=True,
        no_self_asserted_endpoint_or_appointment_as_capability=True,bootstrap_policy_is_not_execution_permission=True,
        C_projection_mapping_construction_consumers=['CE09','CE10','CE12'],no_retrospective_trust_from_future_bundle=True,
        no_transport_expansion_or_new_worker_mapping_frame=True,all_actual_caller_backend_and_records_missing=True)


def rejection_checks(d,plan):
    cases=['LATER_MAPPING_ASSIGNED_TO_CE05','FINAL_C_MAPPING_REQUIRED_AT_BASELINE','FD_UID_ASSERTION_AS_CAPABILITY',
        'APPOINTMENT_OR_BOOTSTRAP_GRANTS_EXECUTION','EXTRA_CONTROL_PIPE','FINAL_CALLER_FREEZE_ASSIGNED_TO_CE05',
        'FUTURE_BUNDLE_SUPPLIES_SOLE_PRIOR_TRUST','CE05_ACCEPTED_FROM_DOCUMENTATION','HUMAN_SOFTWARE_NAMESPACES_COLLAPSED','FUNCTIONAL_EXECUTION_PERMITTED']
    result=[]
    for case in cases:
        x=copy.deepcopy(d)
        if case==cases[0]:x['caller_constructor_requirements'][10]['consumer_step']='CE05'
        elif case==cases[1]:x['step_obligation_boundary']['CE05']['final_actor_image_caller_hash_or_C_mapping_required']=True
        elif case==cases[2]:x['identity_and_capability_policy']['UID_PID_fd_env_module_cwd_key_hash_or_appointment_alone_is_not_capability']=False
        elif case==cases[3]:x['step_obligation_boundary']['CE05']['appointment_or_bootstrap_permission_is_not_execution']=False
        elif case==cases[4]:x['inherited_transport_policy']['explicit_control_pipe_count']=3
        elif case==cases[5]:x['caller_constructor_requirements'][8]['consumer_step']='CE05'
        elif case==cases[6]:x['identity_and_capability_policy']['future_bundle_may_not_supply_sole_prior_authentication']=False
        elif case==cases[7]:x['current_effect']['CE05_accepted']=True
        elif case==cases[8]:x['identity_and_capability_policy']['human_requester_and_software_principal_namespaces_separate']=False
        else:x['actual_caller_state']['actual_functional_execution_permitted']=True
        try:check_caller_boundary(x,plan)
        except AssertionError:result.append(dict(case=case,result='REJECTED_DOCUMENTARY_CALLER_MUTATION'))
        else:raise AssertionError(case+' unexpectedly accepted')
    return result


def build_review():
    d=rd(DOS);plan=rd(PLAN);step=plan['steps'][4];spec=rd(SPEC);defs=rd(PACK)['$defs'];ce04=rd(CE04);ce01=rd(CE01)
    pins={**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==832 and d['input_pins']==pins;verify_git_blobs(pins)
    original=Path.exists
    with predecessor_CE05_presence_as_of_base():
        previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));rec=previous['reconstruct']()
        assert rec==rd(PRIOR_RECON) and previous['build_review'](rec)==rd(PRIOR_REVIEW)
    assert Path.exists is original and (ROOT/DOS).exists()
    assert d['schema']=='d5.i207-ce05-caller-constructor-domain-candidate.v1' and d['increment']=='I207' and d['base_commit']==BASE
    assert d['kind']=='MISSING_CALLER_CONSTRUCTOR_DOMAIN_DOCUMENTARY_DOSSIER_NOT_CALLER_IDENTITY_NOT_CAPABILITY'
    assert d['status']=='CE05_DOCUMENTARY_BASELINE_PREPARED_CALLER_CONSTRUCTOR_DOMAIN_MISSING_NOT_FROZEN_NOT_ACCEPTED_NOT_ADMITTED'
    assert d['plan_binding']==dict(**pin(PLAN,'/steps/4'),step_id='CE05',planned_path=DOS) and step['candidate_dossier_path']==DOS
    for k,s in [('required_evidence','required_evidence'),('planned_acceptance_checks','acceptance_checks'),('authorization_boundary','authorization_boundary'),('contract_rules','contract_rules')]:assert d[k]==step[s]
    assert len(d['required_evidence'])==3 and len(d['planned_acceptance_checks'])==2 and d['contract_rules']==['K02','K06','K07','K08','K09','K15']
    gate=rd(CHECK)['family_gates'][3];assert gate['family']=='caller_identity' and gate['candidate_step_ids']==['CE05','CE08'] and gate['final_record_freeze_step']=='CE08'
    assert d['checklist_binding']==pin(CHECK,'/family_gates/3') and not gate['accepted']
    dep=d['dependency_gate'];assert dep['candidate']==pin(CE04) and dep['last_documentary_review']==pin(PRIOR_REVIEW)
    assert dep['CE04_documentary_baseline_confirmation'] and not dep['competent_CE04_acceptance'] and not dep['actual_dependency_satisfied']
    assert rd(PRIOR_REVIEW)['verdict']['CE04_documentary_baseline_confirmed'] and not rd(PRIOR_REVIEW)['verdict']['CE04_accepted']
    refs={PLAN,CHECK,SPEC,PACK,CE04,CE03,CE01,PRIOR_REVIEW,P+'D5-I122-CAPACITY-CERTIFICATE.json',*[b['path'] for b in plan['bindings'].values()]}
    assert len(refs)==15 and d['documentary_inventory']==[dict(**pin(p),serialized_file_bytes=(ROOT/p).stat().st_size,
        availability='DOCUMENTARY_SOURCE_NOT_REAL_CALLER_ENROLLMENT_CONSTRUCTOR_OR_CUSTODY_EVIDENCE') for p in sorted(refs)]
    boundary=check_caller_boundary(d,plan);negative=rejection_checks(d,plan)
    inverse={r:[] for r in d['contract_rules']}
    for row in d['caller_constructor_requirements']:
        for r in row['contract_rules']:inverse[r].append(row['id'])
    assert all(inverse.values())
    tp=plan['bindings']['bootstrap_contract']['path'];gp=plan['bindings']['bootstrap_grammar']['path'];transport=rd(tp);grammar=rd(gp);t=d['inherited_transport_policy']
    assert t['contract_binding']==pin(tp) and t['grammar_binding']==pin(gp)
    for new,old in [('endpoint_ownership_requirements','endpoint_ownership'),('argv_and_channel_checks_requirement','argv_and_channel_checks'),
        ('trust_boundary_requirements','trust_boundary'),('one_use_and_permissions_requirements','one_use_and_permissions')]:assert t[new]==transport[old]
    assert t['grammar_transport_limits']==grammar['transport_limits'] and t['grammar_permissions']==grammar['permissions']
    assert t['grammar_transport_limits']['additional_control_pipes']==t['grammar_transport_limits']['additional_processes']==t['grammar_transport_limits']['additional_repository_inputs']==0
    schema=d['schema_obligations'];names=['caller_identity','identity','evidence_reference','validity']
    assert schema['schema_binding']==pin(PACK,'/$defs/caller_identity') and schema['definitions']==[dict(name=n,source=pin(PACK,'/$defs/'+n),schema_fragment=defs[n]) for n in names]
    assert schema['final_caller_body_cap_bytes']==spec['record_caps_bytes']['caller_identity']==8192
    for k in ['dossier_is_not_positive_caller_identity','body_cap_not_applied_to_documentary_wrapper','limits_are_candidate_policy_not_active_quota']:assert schema[k] is True
    assert schema['actual_schema_codec_hash_or_crypto_validation']=='NOT_RUN_NO_ACTUAL_BODY' and schema['actual_final_body_validation_consumer_step']=='CE08'
    permission=defs['caller_identity']['properties']['permission']['const']
    assert d['identity_and_capability_policy']['original_caller_permission_literal']==permission=='BOOTSTRAP_CUSTODY_ONLY_FULL_ROOT_AND_SEPARATE_REQUEST_REQUIRED'
    cross=d['cross_record_and_mapping_policy'];assert cross['caller_projection']==spec['projection']
    assert cross['exact_C_rule']==next(r['rule'] for r in spec['rules'] if r['id']=='K08') and cross['unique_mapping_rule']==next(r['rule'] for r in spec['rules'] if r['id']=='K09')
    assert cross['requester_projection_equality']=='C.runtime_requester_id == caller.accountable_requester_actor_id'
    assert cross['protection_domain_equality']=='platform.domain_id == caller.protection_domain_id'
    assert not cross['actual_C_or_mapping_available'] and cross['no_retrospective_trust_from_future_bundle'] and cross['caller_record_has_no_C_Q_bundle_receipt_or_future_root_hash_field']
    for r in d['role_scope_matrix']:
        s=next(s for s in ce01['role_scope_matrix'] if s['id']==r['id'])
        assert {k:v for k,v in r.items() if k!='CE05_responsibility'}=={k:v for k,v in s.items() if k!='CE01_responsibilities'}
    assert [r['id'] for r in d['role_scope_matrix']]==step['provenance_and_role']['primary_review_roles']==['R01','R02','R06','R08']
    for k in ['accepted_external_identity','actor_independent','organizationally_independent','independent_acceptance']:assert d['producer'][k] is False
    assert d['permission_boundary']['denied_action_classes']==ce04['permission_boundary']['denied_action_classes'] and len(d['permission_boundary']['denied_action_classes'])==14
    assert d['permission_boundary']['authorized_documentary_actions']==['READ_SOURCE_JSON_GIT_HASHES','PREPARE_CE05_MISSING_CALLER_CONSTRUCTOR_DOMAIN_DOSSIER','RUN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT']
    for k in ['no_backend_selection_or_enrollment','no_constructor_channel_process_or_claim_creation','no_provider_contact_or_nomination','no_build_import_probe_measurement_product_components_crypto_or_codec_execution','no_active_state_or_quota_change']:assert d['permission_boundary'][k] is True
    assert d['inherited_scope_boundaries']==ce04['inherited_scope_boundaries'] and d['preserved_negative_gates']==ce04['preserved_negative_gates'] and d['freeze_and_refresh']==plan['freeze_and_refresh']
    for r in d['review_dispositions'].values():
        if isinstance(r,dict):assert r==dict(person=None,appointment=None,authority=None,decision='PENDING_NOT_ACCEPTED')
        else:assert r is True
    h=d['historical_scope'];assert not h['I193_saved_CE05_candidate_dossier_created'] and h['current_CE05_dossier_created']
    assert not step['candidate_dossier_created'] and not step['accepted'] and not h['other7_planned_dossiers_created'] and h['actual_accepted_steps']==0
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][:5]) and all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][5:])
    ready=d['missing_facts_and_readiness'];assert ready['candidate_documentary_ready_for_review'] and len(ready['missing'])==4
    for k in ['actual_caller_or_backend_provenance_available','actual_CE04_dependency_accepted','actual_CE05_acceptance_ready','actual_CE08_finalization_ready']:assert ready[k] is False
    assert ready['no_selection_enrollment_execution_probe_contact_or_fabrication_to_fill_missing_facts']
    effect=d['current_effect'];assert effect['CE05_documentary_baseline_prepared'] and effect['candidate_dossiers_prepared_this_increment']==1
    assert effect['actual_accepted_steps']==effect['actual_external_evidence_accepted']==effect['resource_obligations_closed']==0
    for k,v in effect.items():
        if k not in ['CE05_documentary_baseline_prepared','candidate_dossiers_prepared_this_increment','actual_accepted_steps','actual_external_evidence_accepted','resource_obligations_closed','IR03']:assert v is False
    assert effect['IR03']=='NOT_READY' and d['decision']==plan['decision'] and d['E06']==plan['E06']
    assert set(d['work_unit']['rollback_files'])==FILES and d['work_unit']['verification_command']=='python3 docs/validation/D5-I207-audit.py'
    return dict(schema='d5.i207-preparation-review.v1',increment='I207',date='2026-11-17',base_commit=BASE,
        dossier=pin(DOS),input_pins=pins,status='CE05_MISSING_CALLER_CONSTRUCTOR_DOMAIN_BASELINE_PREPARED_NOT_ACCEPTED',
        provenance=dict(preparer='Same Codex assistant/chat',actor_independent=False,organizationally_independent=False,competent_R01_R02_R06_R08_acceptance=False),
        historical_replay=dict(exact_CE05_absence_verified_in_BASE_git_tree=True,only_CE05_presence_projected_during_predecessor_reconstruction=True,
            original_nested_CE04_CE03_CE02_CE01_guards_preserved=True,prior_I206_reconstruction_and_review_reproduced=True,presence_method_restored=True,
            current_CE05_real_path_bytes_separately_required=True,other_planned_dossiers_absent=7,prior_publication_mains_run=False),
        coverage=dict(required_evidence_items=3,acceptance_checks=2,authorization_boundaries=1,contract_rules=step['contract_rules'],
            inverse_rule_to_requirement=inverse,documentary_sources=15,caller_boundary_checks=boundary,documentary_negative_checks=negative,
            schema_definitions=4,final_caller_candidate_cap=8192,actual_final_body_available=False,review_slots_unassigned=4,competent_CE04_dependency_satisfied=False),
        limitations=['Negative documentary wrapper only; no actual principal, requester, domain, constructor, endpoint, enrollment, evidence or accepted caller record.',
            'Transport/permission literals and schema/reference hashes are policy, not process capability or functional execution authority.',
            'Platform/resources/freeze/C/mapping/construction remain in CE06/CE07/CE08/CE09/CE10/CE12; future bundle cannot authenticate prior caller facts.'],
        current_effect=effect,decision=d['decision'],E06=d['E06'])


def main():
    assert rd(PREP)==build_review()
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published519'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==524
    seal=rd(SEAL);assert seal['schema']=='d5.i207-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published524']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['CE05_accepted','actual_caller_identity_record_created','actual_caller_record_finalized','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY_CALLER_CONSTRUCTOR_DOMAIN_MISSING',increment='I207',CE05_baseline_prepared=True,
        CE05_accepted=False,actual_caller_identity_record_created=False,actual_caller_record_finalized=False,actual_CE04_dependency_satisfied=False,
        historical_pins=832,prior_published_files_preserved=524,new_files=5,documentary_rejection_checks=10,actual_evidence_accepted=0,
        independent_acceptance=False,product_or_components_executed=0,quotas_changed=False,rebind_applied=False,
        resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
