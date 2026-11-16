#!/usr/bin/env python3
"""I203 documentary provisional identity intake; no product/components/identity execution."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from contextlib import contextmanager
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='72ef842b5675c0c80aa56d3f0b7b4a9f07c05b47'
DOS=P+'D5-I193-CE03-HUMAN-IDENTITY-ROSTER-CANDIDATE.json'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json';CHECK=P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json';PACK=P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
S01=P+'D5-I179-S01-ROLES-SCOPE-GATES.json'
CE01=P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE02=P+'D5-I201-CE02-ANCHOR-PROVENANCE-CANDIDATE-02.json'
PRIOR_REVIEW=P+'D5-I202-I201-documentary-review.json';PRIOR_RECON=P+'D5-I202-I201-source-reconstruction.json'
PRIOR_AUDIT=P+'D5-I202-audit.py';PRIOR_SEAL=P+'D5-I202-integrity.json';PRIOR_DOC='docs/design/D5-I202-I201-CE02-02-REVIEW.md'
PRIOR_FILES={PRIOR_REVIEW,PRIOR_RECON,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
PREP=P+'D5-I203-preparation-review.json';AUDIT=P+'D5-I203-audit.py';SEAL=P+'D5-I203-integrity.json'
DOC='docs/design/D5-I203-CE03-HUMAN-IDENTITY-ROSTER.md';FILES={DOS,PREP,AUDIT,SEAL,DOC}


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pin(p,q=''):return dict(path=p,sha256=sha(p),json_pointer=q)


@contextmanager
def predecessor_CE03_presence_as_of_base():
    """Project only the new CE03 presence query during historical documentary replay.

    Original nested CE02/CE01 guards remain unchanged. Real current CE03 bytes,
    all other paths and authority checks are verified separately, never hidden.
    """
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


def check_intake_boundary(d,plan):
    rows=d['identity_requirements'];assert [r['id'] for r in rows]==['IR%02d'%i for i in range(1,10)]
    assert [r['consumer_step'] for r in rows]==['CE03']*8+['CE08']
    assert rows[8]['requirement_kind']=='DEFERRED_FINAL_ROSTER_FREEZE_BEFORE_C'
    a=d['step_obligation_boundary']['CE03'];b=d['step_obligation_boundary']['CE08']
    assert a['plan_source']==pin(PLAN,'/steps/2') and a['required_step_ids']==plan['steps'][2]['depends_on']==['CE02']
    assert a['requirement_ids']==['IR%02d'%i for i in range(1,9)] and a['provisional_intake_only'] is True
    for k in ['final_registry_completeness_or_hash_required','final_freeze_or_future_authors_preapproved','positive_preparation_record_may_pin_C_or_future_root','accepted']:assert a[k] is False
    assert a['no_execution_gate_release'] is True
    assert b['plan_source']==pin(PLAN,'/steps/7') and b['required_step_ids']==plan['steps'][7]['depends_on']
    assert b['deferred_requirement_ids']==['IR09'] and b['final_record_order']==plan['steps'][7]['record_families']
    for k in ['complete_actual_evidence_authors_and_preparers_required','final_actor_registry_before_C_required',
        'refresh_and_review_dependents_on_changed_identity_scope','refresh_is_not_active_capture_inputs_rebind']:assert b[k] is True
    for k in ['finalization_currently_performed','accepted']:assert b[k] is False
    actual=d['actual_identity_state'];false_keys={'actual_identity_resolution_performed','actual_separation_verified',
        'final_completeness_claimed','positive_I191_record_created','future_authors_preapproved'}
    assert len(actual)==24
    for k,v in actual.items():
        if k in false_keys:assert v is False
        else:assert v is None
    policy=d['identity_resolution_policy']
    for k in ['human_and_software_principal_namespaces_separate','aliases_resolve_to_one_canonical_human_under_accepted_authority',
        'strings_keys_or_appointments_alone_do_not_prove_distinct_people','all_documentary_preparers_not_just_source_authors_in_scope',
        'assistant_git_or_service_label_is_not_enrolled_human','complete_sorted_unique_actor_preparer_records_required_at_CE08',
        'R01_R02_qualified_overlap_permitted']:assert policy[k] is True
    assert policy['actual_bundle_approvals_consumer_step']=='CE10' and not policy['future_bundle_approval_required_for_CE03']
    tracking=d['documentary_preparation_tracking']
    assert tracking['canonical_human_actor_id'] is None and tracking['authorship_evidence'] is None and tracking['actual_contribution_scope_sha256'] is None
    for k in ['actual_positive_preparation_record_created','complete_preparer_scope_claimed','future_authors_preapproved']:assert tracking[k] is False
    assert tracking['source_observations_are_document_existence_not_human_authorship']
    assert tracking['no_preparation_record_may_pin_C_acceptance_bundle_or_future_root'] is True
    assert d['producer']['canonical_human_actor_id'] is None and d['producer']['organization_id'] is None
    assert d['current_effect']['CE03_accepted'] is False and d['current_effect']['actual_registry_finalized'] is False
    for r in rows:
        for k in ['actual_provider_identity','actual_provider_locator','actual_body_sha256','actual_body_bytes','actual_appointment','actual_acceptance_record']:assert r[k] is None
        assert r['status']=='MISSING_NOT_EVALUATED' and r['accepted'] is False and r['contact_authorized_now'] is False
    return dict(CE03_provisional_rows=8,CE08_deferred_rows=1,no_final_registry_completeness_or_hash_at_CE03=True,
        all_future_evidence_authors_required_before_CE08_freeze=True,human_and_software_namespaces_separate=True,
        all_actual_identities_and_registry_bodies_missing=True,no_future_author_preapproved=True,
        actual_bundle_approvals_not_required_at_CE03=True,preparation_records_cannot_pin_future_C_or_root=True)


def rejection_checks(d,plan):
    cases=['FINAL_FREEZE_ASSIGNED_TO_CE03','FINAL_COMPLETENESS_CLAIMED_NOW','HUMAN_AND_SOFTWARE_NAMESPACES_COLLAPSED',
        'FUTURE_AUTHOR_PREAPPROVED','FUTURE_C_ROOT_PIN_PERMITTED_IN_PREPARATION_RECORD','CE08_EVIDENCE_DEPENDENCY_DROPPED','CE03_ACCEPTED_FROM_DOCUMENTARY_PREPARATION']
    results=[]
    for case in cases:
        x=copy.deepcopy(d)
        if case==cases[0]:x['identity_requirements'][8]['consumer_step']='CE03'
        elif case==cases[1]:x['actual_identity_state']['final_completeness_claimed']=True
        elif case==cases[2]:x['identity_resolution_policy']['human_and_software_principal_namespaces_separate']=False
        elif case==cases[3]:x['documentary_preparation_tracking']['future_authors_preapproved']=True
        elif case==cases[4]:x['documentary_preparation_tracking']['no_preparation_record_may_pin_C_acceptance_bundle_or_future_root']=False
        elif case==cases[5]:x['step_obligation_boundary']['CE08']['required_step_ids'].remove('CE07')
        else:x['current_effect']['CE03_accepted']=True
        try:check_intake_boundary(x,plan)
        except AssertionError:results.append(dict(case=case,result='REJECTED_DOCUMENTARY_INTAKE_MUTATION'))
        else:raise AssertionError(case+' unexpectedly accepted')
    return results


def build_review():
    d=rd(DOS);plan=rd(PLAN);step=plan['steps'][2];spec=rd(SPEC);defs=rd(PACK)['$defs'];ce01=rd(CE01);ce02=rd(CE02)
    pins={**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==812 and d['input_pins']==pins;verify_git_blobs(pins)
    original=Path.exists
    with predecessor_CE03_presence_as_of_base():
        previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));rec=previous['reconstruct']()
        assert rec==rd(PRIOR_RECON) and previous['build_review'](rec)==rd(PRIOR_REVIEW)
    assert Path.exists is original and (ROOT/DOS).exists()
    assert d['schema']=='d5.i203-ce03-human-identity-roster-candidate.v1' and d['increment']=='I203' and d['base_commit']==BASE
    assert d['kind']=='PROVISIONAL_MISSING_IDENTITY_DOCUMENTARY_DOSSIER_NOT_ACTOR_REGISTRY_NOT_ENROLLMENT'
    assert d['status']=='CE03_PROVISIONAL_DOCUMENTARY_CANDIDATE_PREPARED_IDENTITIES_MISSING_NOT_FINALIZED_NOT_ACCEPTED_NOT_ADMITTED'
    assert d['plan_binding']==dict(**pin(PLAN,'/steps/2'),step_id='CE03',planned_path=DOS) and step['candidate_dossier_path']==DOS
    for k,s in [('required_evidence','required_evidence'),('planned_acceptance_checks','acceptance_checks'),('authorization_boundary','authorization_boundary'),('contract_rules','contract_rules')]:assert d[k]==step[s]
    assert len(d['required_evidence'])==len(d['planned_acceptance_checks'])==3 and d['contract_rules']==['K02','K03','K10','K16']
    gate=rd(CHECK)['family_gates'][1];assert gate['family']=='actor_registry' and gate['final_record_freeze_step']=='CE08'
    assert gate['candidate_step_ids']==['CE03','CE08'] and d['checklist_binding']==pin(CHECK,'/family_gates/1')
    dep=d['dependency_gate'];assert dep['candidate']==pin(CE02) and dep['last_documentary_review']==pin(PRIOR_REVIEW)
    assert dep['F199_01_documentary_repair_confirmed_for_exact_CE02_candidate_02']
    assert not dep['competent_CE02_acceptance'] and not dep['actual_dependency_satisfied']
    assert rd(PRIOR_REVIEW)['verdict']['F199_01_documentary_repair_confirmed_for_candidate_02'] and not rd(PRIOR_REVIEW)['verdict']['CE02_accepted']
    refs={PLAN,CHECK,SPEC,PACK,S01,CE01,CE02,PRIOR_REVIEW,P+'D5-I122-CAPACITY-CERTIFICATE.json',*[v['path'] for v in plan['bindings'].values()]}
    assert len(refs)==15 and d['documentary_inventory']==[dict(**pin(p),serialized_file_bytes=(ROOT/p).stat().st_size,
        availability='DOCUMENTARY_SOURCE_NOT_AUTHENTICATED_HUMAN_OR_ENROLLMENT_EVIDENCE') for p in sorted(refs)]
    scope=check_intake_boundary(d,plan);negative=rejection_checks(d,plan)
    inverse={r:[] for r in d['contract_rules']}
    for row in d['identity_requirements']:
        for r in row['contract_rules']:inverse[r].append(row['id'])
    assert all(inverse.values())
    policy=d['identity_resolution_policy'];profile=rd(plan['bindings']['profile02']['path'])
    assert policy['source_role_authority_matrix']==pin(S01,'/role_authority_validity_matrix')
    assert policy['required_role_ids']==[r['id'] for r in ce01['role_scope_matrix']]==['R%02d'%i for i in range(1,9)]
    assert policy['S01_exclusions']==spec['inheritance']['S01_actor_exclusions'] and len(policy['S01_exclusions'])==8
    assert policy['profile_source_author_and_root_key_rules']==profile['bootstrap']['separation'][8:]
    assert policy['extra_custody_separation']==spec['inheritance']['extra_custody_separation']
    assert policy['preparation_record_rule']==next(r['rule'] for r in spec['rules'] if r['id']=='K03')
    tracking=d['documentary_preparation_tracking'];assert set(tracking['current_unit_paths'])==FILES
    assert tracking['status']=='PARTIAL_DOCUMENTARY_ACTIVITY_TRACKING_NOT_AUTHENTICATED_PREPARER_ROSTER'
    assert tracking['known_source_observations']==[dict(source=pin(p),observed_increment=rd(p).get('increment'),
        accountable_human_actor_id=None,authorship_evidence=None,positive_preparation_record_created=False) for p in sorted(refs)]
    schema=d['schema_obligations'];names=['actor_registry','actor','preparation_record','evidence_reference','validity']
    assert schema['schema_binding']==pin(PACK,'/$defs/actor_registry')
    assert schema['definitions']==[dict(name=n,source=pin(PACK,'/$defs/'+n),schema_fragment=defs[n]) for n in names]
    assert schema['final_registry_body_cap_bytes']==spec['record_caps_bytes']['actor_registry']==98304
    assert schema['limits_are_candidate_policy_not_active_quota'] and schema['dossier_is_not_positive_registry'] and schema['body_cap_not_applied_to_documentary_wrapper']
    assert schema['actual_schema_codec_hash_or_crypto_validation']=='NOT_RUN_NO_ACTUAL_BODY' and schema['actual_final_body_validation_consumer_step']=='CE08'
    for r in d['role_scope_matrix']:
        source=next(s for s in ce01['role_scope_matrix'] if s['id']==r['id'])
        assert {k:v for k,v in r.items() if k!='CE03_responsibility'}=={k:v for k,v in source.items() if k!='CE01_responsibilities'}
    assert [r['id'] for r in d['role_scope_matrix']]==step['provenance_and_role']['primary_review_roles']==['R06','R08']
    for k in ['accepted_external_identity','actor_independent','organizationally_independent','independent_acceptance']:assert d['producer'][k] is False
    assert d['permission_boundary']['denied_action_classes']==ce02['permission_boundary']['denied_action_classes'] and len(d['permission_boundary']['denied_action_classes'])==14
    assert d['permission_boundary']['authorized_documentary_actions']==['READ_SOURCE_JSON_GIT_HASHES','PREPARE_CE03_PROVISIONAL_MISSING_IDENTITY_DOSSIER','RUN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT']
    for k in ['no_provider_contact_or_nomination','no_identity_actor_or_key_enrollment','no_software_label_as_human','no_product_components_crypto_or_registry_codec_execution','no_active_state_or_quota_change']:assert d['permission_boundary'][k] is True
    assert d['inherited_scope_boundaries']==ce02['inherited_scope_boundaries'] and d['preserved_negative_gates']==ce02['preserved_negative_gates']
    assert d['freeze_and_refresh']==plan['freeze_and_refresh']
    for r in d['review_dispositions'].values():
        if isinstance(r,dict):assert r==dict(person=None,appointment=None,authority=None,decision='PENDING_NOT_ACCEPTED')
        else:assert r is True
    h=d['historical_scope'];assert not h['I193_saved_CE03_candidate_dossier_created'] and h['current_CE03_dossier_created']
    assert not step['candidate_dossier_created'] and not step['accepted'] and not h['other9_planned_dossiers_created'] and h['actual_accepted_steps']==0
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][:3])
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][3:])
    ready=d['missing_facts_and_readiness'];assert ready['candidate_documentary_ready_for_review'] and len(ready['missing'])==4
    for k in ['actual_identity_authority_or_human_evidence_available','actual_CE02_dependency_accepted','actual_CE03_acceptance_ready','actual_CE08_finalization_ready']:assert ready[k] is False
    assert ready['no_execution_contact_enrollment_or_identity_fabrication_to_fill_missing_facts']
    effect=d['current_effect'];assert effect['CE03_provisional_documentary_candidate_prepared'] and effect['candidate_dossiers_prepared_this_increment']==1
    assert effect['actual_accepted_steps']==effect['actual_external_evidence_accepted']==effect['resource_obligations_closed']==0
    for k,v in effect.items():
        if k not in ['CE03_provisional_documentary_candidate_prepared','candidate_dossiers_prepared_this_increment','actual_accepted_steps','actual_external_evidence_accepted','resource_obligations_closed','IR03']:assert v is False
    assert effect['IR03']=='NOT_READY' and d['decision']==plan['decision'] and d['E06']==plan['E06']
    assert set(d['work_unit']['rollback_files'])==FILES and d['work_unit']['verification_command']=='python3 docs/validation/D5-I203-audit.py'
    return dict(schema='d5.i203-preparation-review.v1',increment='I203',date='2026-11-16',base_commit=BASE,
        dossier=pin(DOS),input_pins=pins,status='CE03_PROVISIONAL_MISSING_IDENTITY_CANDIDATE_PREPARED_NOT_FINALIZED_NOT_ACCEPTED',
        provenance=dict(preparer='Same Codex assistant/chat',actor_independent=False,organizationally_independent=False,competent_R06_R08_acceptance=False),
        historical_replay=dict(exact_CE03_absence_verified_in_BASE_git_tree=True,only_CE03_presence_projected_during_predecessor_reconstruction=True,
            original_nested_CE02_CE01_guards_preserved=True,prior_I202_reconstruction_and_review_reproduced=True,
            presence_method_restored=True,current_CE03_real_path_bytes_separately_required=True,other_planned_dossiers_absent=9,prior_publication_mains_run=False),
        coverage=dict(required_evidence_items=3,acceptance_checks=3,authorization_boundaries=1,contract_rules=step['contract_rules'],
            inverse_rule_to_requirement=inverse,documentary_sources=15,provisional_intake_checks=scope,
            documentary_negative_checks=negative,schema_definitions=5,final_actor_registry_candidate_cap=98304,
            actual_registry_body_available=False,primary_or_separate_review_slots_unassigned=2,
            source_observations_not_authenticated_humans=15,S01_exclusions=8,extra_custody_separations=4,
            competent_CE02_dependency_satisfied=False),
        limitations=['Provisional missing-identity wrapper only; no actual human, alias, organization, competence, appointment, actor-registry or accepted preparation record.',
            'Document existence/metadata/hashes and self-declared assistant activity are not genuine human authorship or complete preparer identity evidence.',
            'CE08 finalization and real bodies/codec/hash/cap/separation checks remain pending after all actual evidence authors; no future contributor is approved.'],
        current_effect=effect,decision=d['decision'],E06=d['E06'])


def main():
    assert rd(PREP)==build_review()
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published499'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==504
    seal=rd(SEAL);assert seal['schema']=='d5.i203-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published504']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['CE03_accepted','actual_actor_registry_created','actual_registry_finalized','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY_PROVISIONAL_IDENTITIES_MISSING',increment='I203',CE03_candidate_prepared=True,
        CE03_accepted=False,actual_actor_registry_created=False,actual_registry_finalized=False,actual_CE02_dependency_satisfied=False,
        historical_pins=812,prior_published_files_preserved=504,new_files=5,documentary_rejection_checks=7,actual_evidence_accepted=0,
        independent_acceptance=False,product_or_components_executed=0,quotas_changed=False,rebind_applied=False,
        resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
