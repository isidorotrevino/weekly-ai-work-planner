#!/usr/bin/env python3
"""I205 missing image/source baseline, documentary checks only; no components."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from contextlib import contextmanager
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='718387a5c0158931dac173ae75919befe482bb0a'
DOS=P+'D5-I193-CE04-IMAGE-SOURCE-BASELINE-CANDIDATE.json'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json';CHECK=P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json';PACK=P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CE03=P+'D5-I193-CE03-HUMAN-IDENTITY-ROSTER-CANDIDATE.json';CE01=P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
SCOPE=P+'D5-I181-F179-01-GATE-ORDER-PROPOSAL.json';P02=P+'D5-I136-P02-documentary-review.json';P02PREP=P+'D5-I135-P02-preparation-review.json'
PRIOR_REVIEW=P+'D5-I204-I203-documentary-review.json';PRIOR_RECON=P+'D5-I204-I203-source-reconstruction.json'
PRIOR_AUDIT=P+'D5-I204-audit.py';PRIOR_SEAL=P+'D5-I204-integrity.json';PRIOR_DOC='docs/design/D5-I204-I203-CE03-REVIEW.md'
PRIOR_FILES={PRIOR_REVIEW,PRIOR_RECON,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
PREP=P+'D5-I205-preparation-review.json';AUDIT=P+'D5-I205-audit.py';SEAL=P+'D5-I205-integrity.json'
DOC='docs/design/D5-I205-CE04-IMAGE-SOURCE-BASELINE.md';FILES={DOS,PREP,AUDIT,SEAL,DOC}


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pin(p,q=''):return dict(path=p,sha256=sha(p),json_pointer=q)


@contextmanager
def predecessor_CE04_presence_as_of_base():
    """Exact CE04 historical presence only; current bytes checked outside replay."""
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


def check_baseline_boundary(d,plan):
    rows=d['image_source_requirements'];assert [r['id'] for r in rows]==['IM%02d'%i for i in range(1,11)]
    assert [r['consumer_step'] for r in rows]==['CE04']*6+['CE05','CE06','CE07','CE08']
    phases=d['step_obligation_boundary']
    for name,ids in [('CE04',['IM%02d'%i for i in range(1,7)]),('CE05',['IM07']),('CE06',['IM08']),('CE07',['IM09']),('CE08',['IM10'])]:
        step=next(s for s in plan['steps'] if s['id']==name)
        assert phases[name]['plan_source']==pin(PLAN,'/steps/'+str(plan['steps'].index(step)))
        assert phases[name]['required_step_ids']==step['depends_on'] and phases[name]['requirement_ids']==ids
        assert phases[name]['actual_acceptance'] is False and phases[name]['current_execution_authorized'] is False
        assert phases[name]['actual_dossier_created']==(name=='CE04')
    a=phases['CE04'];assert a['baseline_only_not_final_manifest'] and a['no_implicit_downstream_platform_resource_or_approval_acceptance']
    assert a['downstream_proof_or_finalization_required_as_new_reverse_CE04_dependency'] is False and a['final_registry_or_manifest_hash_required'] is False
    b=phases['CE08'];assert b['final_record_order']==plan['steps'][7]['record_families']
    for k in ['actual_authors_and_complete_antecedents_before_freeze_required','final_manifest_before_C_required','freeze_is_not_active_capture_inputs_rebind']:assert b[k] is True
    source=d['source_scope_policy'];assert source['actual_total_bytes'] is None and source['no_zero_sum_for_missing_sources']
    assert not source['old_I122_proofs_transfer_to_successor']
    mapping=d['source_to_image_missing_inventory'];assert len(mapping)==6
    for row in mapping:
        for k in ['actual_source_sha256','actual_source_bytes','actual_image_member_id','actual_image_member_sha256','actual_image_representation','actual_mapping_evidence','actual_load_observation']:assert row[k] is None
        assert not row['loaded_by_membership_claimed'] and not row['accepted']
        if row['logical_path'].endswith('README.md'):assert row['required_representation']=='DOCUMENT' and row['allowed_representation_policy']==['DOCUMENT']
    runtime=d['runtime_identity_boundary'];assert runtime['image_bytes_digest_distinct_from_runtime_identity'] and runtime['image_bytes_digest_does_not_substitute_P02']
    assert runtime['historical_P02_is_not_successor_runtime_evidence'] and not runtime['historical_P02_runtime_verified'] and not runtime['target_runtime_or_host_platform_sampled']
    for row in d['compiled_policy_requirements']:
        assert row['actual_compiled_policy_sha256'] is None and row['actual_independent_policy_selection_acceptance'] is None
        assert row['actual_compiled_value_verified'] is False
    state=d['actual_image_runtime_state'];false_fields={'actual_source_image_mapping_verified','actual_runtime_identity_verified',
        'actual_self_embedding_check_performed','actual_complete_dependency_closure_verified','actual_platform_enforcement_verified',
        'actual_resource_or_compatibility_join_verified','actual_final_manifest_frozen'}
    assert len(state)==27
    for k,v in state.items():
        if k in false_fields:assert v is False
        else:assert v is None
    assert d['current_effect']['CE04_accepted'] is False
    for row in rows:
        for k in ['actual_provider_identity','actual_provider_locator','actual_body_sha256','actual_body_bytes','actual_appointment','actual_acceptance_record']:assert row[k] is None
        assert row['status']=='MISSING_NOT_EVALUATED' and not row['accepted'] and not row['contact_authorized_now']
    return dict(CE04_baseline_requirements=6,deferred_phase_requirements=4,source_mapping_rows=6,
        all_real_sources_mappings_and_images_missing=True,README_document_only=True,no_load_claim_from_membership=True,
        image_digest_distinct_from_runtime_identity=True,no_I122_or_P02_proof_transfer=True,no_actual_compiled_policy_verified=True,
        downstream_caller_platform_resources_and_finalization_not_discharged=True)


def rejection_checks(d,plan):
    cases=['FINAL_MANIFEST_FREEZE_ASSIGNED_TO_CE04','README_NOT_DOCUMENT','MEMBERSHIP_CLAIMS_TEST_RUNNER_LOADED',
        'IMAGE_DIGEST_SUBSTITUTES_RUNTIME','MISSING_SOURCES_SUMMED_AS_ZERO','I122_PROOF_TRANSFERRED',
        'DEPENDENCY_CLOSURE_CLAIMED_COMPLETE','DOCUMENTARY_PIN_CLAIMED_COMPILED','CE04_ACCEPTED_FROM_DOCUMENTATION']
    results=[]
    for case in cases:
        x=copy.deepcopy(d)
        if case==cases[0]:x['image_source_requirements'][9]['consumer_step']='CE04'
        elif case==cases[1]:next(r for r in x['source_to_image_missing_inventory'] if r['logical_path'].endswith('README.md'))['required_representation']='PYTHON_SOURCE'
        elif case==cases[2]:next(r for r in x['source_to_image_missing_inventory'] if r['logical_path'].endswith('test_joint_capture.py'))['loaded_by_membership_claimed']=True
        elif case==cases[3]:x['runtime_identity_boundary']['image_bytes_digest_does_not_substitute_P02']=False
        elif case==cases[4]:x['source_scope_policy']['actual_total_bytes']=0
        elif case==cases[5]:x['source_scope_policy']['old_I122_proofs_transfer_to_successor']=True
        elif case==cases[6]:x['actual_image_runtime_state']['actual_complete_dependency_closure_verified']=True
        elif case==cases[7]:x['compiled_policy_requirements'][0]['actual_compiled_value_verified']=True
        else:x['current_effect']['CE04_accepted']=True
        try:check_baseline_boundary(x,plan)
        except AssertionError:results.append(dict(case=case,result='REJECTED_DOCUMENTARY_BASELINE_MUTATION'))
        else:raise AssertionError(case+' unexpectedly accepted')
    return results


def build_review():
    d=rd(DOS);plan=rd(PLAN);step=plan['steps'][3];spec=rd(SPEC);defs=rd(PACK)['$defs'];ce03=rd(CE03);ce01=rd(CE01)
    pins={**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==822 and d['input_pins']==pins;verify_git_blobs(pins)
    original=Path.exists
    with predecessor_CE04_presence_as_of_base():
        previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));rec=previous['reconstruct']()
        assert rec==rd(PRIOR_RECON) and previous['build_review'](rec)==rd(PRIOR_REVIEW)
    assert Path.exists is original and (ROOT/DOS).exists()
    assert d['schema']=='d5.i205-ce04-image-source-baseline-candidate.v1' and d['increment']=='I205' and d['base_commit']==BASE
    assert d['kind']=='MISSING_IMAGE_SOURCE_DOCUMENTARY_BASELINE_NOT_IMAGE_MANIFEST_NOT_BUILD'
    assert d['status']=='CE04_DOCUMENTARY_BASELINE_PREPARED_SOURCES_IMAGE_RUNTIME_MISSING_NOT_FROZEN_NOT_ACCEPTED_NOT_ADMITTED'
    assert d['plan_binding']==dict(**pin(PLAN,'/steps/3'),step_id='CE04',planned_path=DOS) and step['candidate_dossier_path']==DOS
    for k,s in [('required_evidence','required_evidence'),('planned_acceptance_checks','acceptance_checks'),('authorization_boundary','authorization_boundary'),('contract_rules','contract_rules')]:assert d[k]==step[s]
    assert len(d['required_evidence'])==len(d['planned_acceptance_checks'])==3 and d['contract_rules']==['K04','K05','K07','K15','K16']
    gate=rd(CHECK)['family_gates'][2];assert gate['family']=='image_manifest' and gate['candidate_step_ids']==['CE04','CE08'] and gate['final_record_freeze_step']=='CE08'
    assert d['checklist_binding']==pin(CHECK,'/family_gates/2') and not gate['accepted']
    dep=d['dependency_gate'];assert dep['candidate']==pin(CE03) and dep['last_documentary_review']==pin(PRIOR_REVIEW)
    assert dep['CE03_provisional_documentary_confirmation'] and not dep['competent_CE03_acceptance'] and not dep['actual_dependency_satisfied']
    assert rd(PRIOR_REVIEW)['verdict']['CE03_provisional_candidate_documentarily_confirmed'] and not rd(PRIOR_REVIEW)['verdict']['CE03_accepted']
    refs={PLAN,CHECK,SPEC,PACK,CE03,CE01,PRIOR_REVIEW,SCOPE,P02,P02PREP,P+'D5-I122-CAPACITY-CERTIFICATE.json',*[b['path'] for b in plan['bindings'].values()]}
    assert len(refs)==17 and d['documentary_inventory']==[dict(**pin(p),serialized_file_bytes=(ROOT/p).stat().st_size,
        availability='DOCUMENTARY_SOURCE_NOT_ACTUAL_SUCCESSOR_IMAGE_RUNTIME_OR_BUILD_EVIDENCE') for p in sorted(refs)]
    scope=rd(SCOPE)['successor_source_scope'];mapping=d['source_to_image_missing_inventory'];slots=scope['slots']
    assert [r['logical_path'] for r in mapping]==slots and len(slots)==6 and all(not (ROOT/p).exists() for p in slots)
    assert set(slots)==set(defs['source_bindings']['required'])==set(defs['image_manifest']['properties']['source_to_image']['required'])
    for row in mapping:
        if not row['logical_path'].endswith('README.md'):assert row['required_representation'] is None and row['allowed_representation_policy']==defs['image_member_binding']['properties']['image_representation']['enum']
    source=d['source_scope_policy'];assert source['source']==pin(SCOPE,'/successor_source_scope') and source['exact_six_paths']==slots
    assert source['six_source_total_design_ceiling_bytes']==scope['total_six_source_bytes_design_upper']==262144
    for k in ['README_is_DOCUMENT','no_test_or_runner_loaded_from_membership','no_silent_source_scope_enlargement','no_unbound_repository_helper_outside_historical480_or_six_sources','no_old_I122_extra_runtime_reads_or_helpers_added']:assert source[k] is True
    boundary=check_baseline_boundary(d,plan);negative=rejection_checks(d,plan)
    inverse={r:[] for r in d['contract_rules']}
    for row in d['image_source_requirements']:
        for r in row['contract_rules']:inverse[r].append(row['id'])
    assert all(inverse.values())
    runtime=d['runtime_identity_boundary'];assert runtime['P02_historical_review']==pin(P02)
    assert runtime['historical_P02_subject']==rd(P02)['subject'] and runtime['historical_P02_status']==rd(P02)['status']
    assert runtime['historical_P02_runtime_verified']==rd(P02)['decision']['actual_runtime_identity_verified'] is False
    assert runtime['existing_python_or_environment_not_target_runtime_evidence']
    policy_map={'profile_sha256':'profile02','protocol_schema_sha256':'protocol_schemas02','output_schema_sha256':'output_schemas',
        'transport_contract_sha256':'bootstrap_contract','transport_grammar_sha256':'bootstrap_grammar','custody_schema_pack_sha256':'custody_schemas','custody_contract_sha256':'custody_contract'}
    expected=[dict(image_field=f,documentary_binding=pin(plan['bindings'][b]['path']),required_candidate_policy_sha256=sha(plan['bindings'][b]['path']),
        actual_compiled_policy_sha256=None,actual_compiled_value_verified=False,actual_independent_policy_selection_acceptance=None) for f,b in policy_map.items()]
    assert d['compiled_policy_requirements']==expected
    for row in expected:
        prop=defs['image_manifest']['properties'][row['image_field']]
        if 'const' in prop:assert prop['const']==row['required_candidate_policy_sha256']
    noembed=d['no_self_embedding_policy'];assert noembed['own_future_image_manifest_bundle_digests_must_not_be_embedded'] and noembed['expected_image_identity_selected_by_external_accepted_custody']
    assert noembed['actual_external_image_selection'] is None and not noembed['actual_source_or_image_no_self_embedding_verified']
    assert noembed['documentary_policy_pins_are_not_actual_compiled_or_image_evidence']
    schema=d['schema_obligations'];names=['image_manifest','image_member_binding','image_dependency','source_bindings','evidence_reference','validity']
    assert schema['definitions']==[dict(name=n,source=pin(PACK,'/$defs/'+n),schema_fragment=defs[n]) for n in names]
    assert schema['schema_binding']==pin(PACK,'/$defs/image_manifest') and schema['final_manifest_body_cap_bytes']==spec['record_caps_bytes']['image_manifest']==98304
    assert schema['dependency_min']==defs['image_manifest']['properties']['dependencies']['minItems']==1
    assert schema['dependency_max']==defs['image_manifest']['properties']['dependencies']['maxItems']==128
    for k in ['no_truncation_to_fit_cap','dossier_is_not_positive_image_manifest','body_cap_not_applied_to_documentary_wrapper','limits_are_candidate_policy_not_active_quota']:assert schema[k] is True
    assert schema['actual_schema_codec_hash_or_crypto_validation']=='NOT_RUN_NO_ACTUAL_BODY' and schema['actual_final_body_validation_consumer_step']=='CE08'
    for r in d['role_scope_matrix']:
        s=next(s for s in ce01['role_scope_matrix'] if s['id']==r['id'])
        assert {k:v for k,v in r.items() if k!='CE04_responsibility'}=={k:v for k,v in s.items() if k!='CE01_responsibilities'}
    assert [r['id'] for r in d['role_scope_matrix']]==step['provenance_and_role']['primary_review_roles']==['R01','R06','R08']
    for k in ['accepted_external_identity','actor_independent','organizationally_independent','independent_acceptance']:assert d['producer'][k] is False
    assert d['permission_boundary']['denied_action_classes']==ce03['permission_boundary']['denied_action_classes'] and len(d['permission_boundary']['denied_action_classes'])==14
    assert d['permission_boundary']['authorized_documentary_actions']==['READ_SOURCE_JSON_GIT_HASHES','PREPARE_CE04_MISSING_IMAGE_BASELINE_DOSSIER','RUN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT']
    for k in ['no_source_creation_or_build','no_import_measurement_or_target_runtime_sampling','no_provider_contact_or_nomination','no_product_components_crypto_or_registry_codec_execution','no_active_state_or_quota_change']:assert d['permission_boundary'][k] is True
    assert d['inherited_scope_boundaries']==ce03['inherited_scope_boundaries'] and d['preserved_negative_gates']==ce03['preserved_negative_gates'] and d['freeze_and_refresh']==plan['freeze_and_refresh']
    for r in d['review_dispositions'].values():
        if isinstance(r,dict):assert r==dict(person=None,appointment=None,authority=None,decision='PENDING_NOT_ACCEPTED')
        else:assert r is True
    h=d['historical_scope'];assert not h['I193_saved_CE04_candidate_dossier_created'] and h['current_CE04_dossier_created']
    assert not step['candidate_dossier_created'] and not step['accepted'] and not h['other8_planned_dossiers_created'] and h['actual_accepted_steps']==0
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][:4]) and all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][4:])
    ready=d['missing_facts_and_readiness'];assert ready['candidate_documentary_ready_for_review'] and len(ready['missing'])==4
    for k in ['actual_successor_source_or_image_available','actual_CE03_dependency_accepted','actual_CE04_acceptance_ready','actual_CE08_finalization_ready']:assert ready[k] is False
    assert ready['no_execution_build_import_measurement_contact_or_fabrication_to_fill_missing_facts']
    effect=d['current_effect'];assert effect['CE04_documentary_baseline_prepared'] and effect['candidate_dossiers_prepared_this_increment']==1
    assert effect['actual_accepted_steps']==effect['actual_external_evidence_accepted']==effect['resource_obligations_closed']==0
    for k,v in effect.items():
        if k not in ['CE04_documentary_baseline_prepared','candidate_dossiers_prepared_this_increment','actual_accepted_steps','actual_external_evidence_accepted','resource_obligations_closed','IR03']:assert v is False
    assert effect['IR03']=='NOT_READY' and d['decision']==plan['decision'] and d['E06']==plan['E06']
    assert set(d['work_unit']['rollback_files'])==FILES and d['work_unit']['verification_command']=='python3 docs/validation/D5-I205-audit.py'
    return dict(schema='d5.i205-preparation-review.v1',increment='I205',date='2026-11-16',base_commit=BASE,
        dossier=pin(DOS),input_pins=pins,status='CE04_MISSING_IMAGE_SOURCE_RUNTIME_BASELINE_PREPARED_NOT_ACCEPTED',
        provenance=dict(preparer='Same Codex assistant/chat',actor_independent=False,organizationally_independent=False,competent_R01_R06_R08_acceptance=False),
        historical_replay=dict(exact_CE04_absence_verified_in_BASE_git_tree=True,only_CE04_presence_projected_during_predecessor_reconstruction=True,
            original_nested_CE03_CE02_CE01_guards_preserved=True,prior_I204_reconstruction_and_review_reproduced=True,presence_method_restored=True,
            current_CE04_real_path_bytes_separately_required=True,other_planned_dossiers_absent=8,prior_publication_mains_run=False),
        coverage=dict(required_evidence_items=3,acceptance_checks=3,authorization_boundaries=1,contract_rules=step['contract_rules'],
            inverse_rule_to_requirement=inverse,documentary_sources=17,baseline_checks=boundary,documentary_negative_checks=negative,
            compiled_policy_requirements=7,schema_definitions=6,six_source_design_ceiling=262144,actual_source_total_bytes=None,
            final_image_manifest_candidate_cap=98304,actual_final_body_available=False,review_slots_unassigned=3,competent_CE03_dependency_satisfied=False),
        limitations=['Negative documentary wrapper only: no actual successor source/image/runtime/build/mapping, compiled policy, provider or accepted evidence.',
            'Image bytes and complete runtime/P02 identity stay distinct. Historical I122/P02 do not qualify successor scope; dependency/size caps cannot replace full proof.',
            'Caller/platform/resource/final-manifest work remains in CE05/CE06/CE07/CE08 respectively; no active rebind or current action authorized.'],
        current_effect=effect,decision=d['decision'],E06=d['E06'])


def main():
    assert rd(PREP)==build_review()
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published509'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==514
    seal=rd(SEAL);assert seal['schema']=='d5.i205-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published514']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['CE04_accepted','actual_image_manifest_created','actual_manifest_finalized','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY_IMAGE_SOURCE_RUNTIME_MISSING',increment='I205',CE04_baseline_prepared=True,
        CE04_accepted=False,actual_image_manifest_created=False,actual_manifest_finalized=False,actual_CE03_dependency_satisfied=False,
        historical_pins=822,prior_published_files_preserved=514,new_files=5,documentary_rejection_checks=9,actual_evidence_accepted=0,
        independent_acceptance=False,product_or_components_executed=0,quotas_changed=False,rebind_applied=False,
        resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
