#!/usr/bin/env python3
"""I209 documentary missing-platform checks; no platform/clock/ledger execution."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from contextlib import contextmanager
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='adc364bff918e3564268777a12d22dd1485e511d'
DOS=P+'D5-I193-CE06-PLATFORM-CLOCK-GLOBAL-LEDGER-CANDIDATE.json'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json';CHECK=P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json';PACK=P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CE05=P+'D5-I193-CE05-CALLER-CONSTRUCTOR-DOMAIN-CANDIDATE.json';CE04=P+'D5-I193-CE04-IMAGE-SOURCE-BASELINE-CANDIDATE.json'
CE03=P+'D5-I193-CE03-HUMAN-IDENTITY-ROSTER-CANDIDATE.json';CE01=P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
PRIOR_REVIEW=P+'D5-I208-I207-documentary-review.json';PRIOR_RECON=P+'D5-I208-I207-source-reconstruction.json'
PRIOR_AUDIT=P+'D5-I208-audit.py';PRIOR_SEAL=P+'D5-I208-integrity.json';PRIOR_DOC='docs/design/D5-I208-I207-CE05-REVIEW.md'
PRIOR_FILES={PRIOR_REVIEW,PRIOR_RECON,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
PREP=P+'D5-I209-preparation-review.json';AUDIT=P+'D5-I209-audit.py';SEAL=P+'D5-I209-integrity.json'
DOC='docs/design/D5-I209-CE06-PLATFORM-CLOCK-GLOBAL-LEDGER.md';FILES={DOS,PREP,AUDIT,SEAL,DOC}


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pin(p,q=''):return dict(path=p,sha256=sha(p),json_pointer=q)


@contextmanager
def predecessor_CE06_presence_as_of_base():
    """Only exact CE06 historical presence query; current bytes checked separately."""
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


def check_platform_boundary(d,plan):
    rows=d['platform_requirements'];assert [r['id'] for r in rows]==['PF%02d'%i for i in range(1,12)]
    assert [r['consumer_step'] for r in rows]==['CE06']*6+['CE07','CE08','CE09','CE10','CE12']
    phases=d['step_obligation_boundary']
    for name,ids in [('CE06',['PF%02d'%i for i in range(1,7)]),('CE07',['PF07']),('CE08',['PF08']),('CE09',['PF09']),('CE10',['PF10']),('CE12',['PF11'])]:
        s=next(s for s in plan['steps'] if s['id']==name)
        assert phases[name]['plan_source']==pin(PLAN,'/steps/'+str(plan['steps'].index(s)))
        assert phases[name]['required_step_ids']==s['depends_on'] and phases[name]['requirement_ids']==ids
        assert not phases[name]['actual_acceptance'] and not phases[name]['current_execution_authorized']
        assert phases[name]['actual_dossier_created']==(name=='CE06')
    a=phases['CE06'];assert a['baseline_mechanism_proof_not_actual_invocation'] and a['guarantee_policy_or_hash_is_not_proof'] and a['no_current_qualification_or_execution']
    for k in ['actual_invocation_claim_or_receipt_required','actual_C_or_mapping_or_final_platform_hash_required','accepted_complete_resource_join_required_as_reverse_dependency']:assert a[k] is False
    b=phases['CE08'];assert b['final_record_order']==plan['steps'][7]['record_families']
    for k in ['actual_authors_and_resource_scope_before_freeze_required','final_platform_before_C_required','refresh_is_not_active_capture_inputs_rebind']:assert b[k] is True
    last=phases['CE12'];assert last['external_prerequisites_for_receipt']==plan['closure_boundaries']['external_prerequisites_for_receipt']
    assert last['separate_authorization_full_admission_before_claim_required'] and last['claim_is_prereceipt_event_not_own_precondition'] and last['CE11_does_not_depend_on_CE12']
    for g in d['guarantee_evidence_inventory']:
        for k in ['actual_provider_identity','actual_record_id','actual_evidence_sha256','actual_proof_body','actual_proof_bytes','actual_scope_binding','actual_acceptance_record']:assert g[k] is None
        assert g['status']=='MISSING_NOT_EVALUATED' and g['actual_verified'] is False and g['accepted'] is False
    c=d['clock_currentness_policy'];assert c['host_clock_or_client_date_is_not_accepted_runtime_clock']
    assert c['actual_clock_error_or_sample'] is None and c['actual_trusted_now'] is None
    for k in ['accepted_clock_and_monotonic_UTC_evidence_required','no_TOFU_stale_cache_hidden_online_or_file_lookup','missing_clock_currentness_durability_assurance_stays_pending','deadline_counter_limits_not_service_or_900_proof']:assert c[k] is True
    assert not c['instantaneous_all_revocation_discovery_claimed']
    ledger=d['global_one_use_policy']
    assert ledger['tuple_fields']==['trust_context_sha256','runtime_request_sha256','invocation_id']
    for k in ['one_authoritative_global_namespace_required','global_across_all_approved_callers_domains_and_restarts',
        'high_water_epoch_and_atomic_durable_rollback_crash_proof_required','literal_is_requirement_not_running_backend_or_new_authorization',
        'uncertain_or_partial_claim_spends_or_rejects','parent_child_is_one_correlated_invocation','mapping_and_ledger_domain_must_agree']:assert ledger[k] is True
    for k in ['free_retry_or_invocation_reuse_permitted','actual_claim_or_receipt_required_for_CE06_mechanism_evidence','actual_live_claim_replay_crash_restart_or_endpoint_test_performed']:assert ledger[k] is False
    assert ledger['actual_tuple_or_claim'] is None and ledger['actual_ledger_domain_or_epoch'] is None
    assert ledger['actual_claim_construction_consumer']=='CE12' and ledger['actual_unique_mapping_consumer']=='CE10'
    t=d['inherited_transport_policy'];assert t['explicit_control_pipe_count']==2 and t['observed_worker_operand_count']==6
    assert not t['actual_backend_constructor_or_endpoint_selected'] and not t['actual_probe_or_process_creation']
    state=d['actual_platform_clock_ledger_state'];false_fields={'actual_platform_or_clock_or_ledger_selected','actual_guarantees_verified',
        'actual_clock_or_currentness_verified','actual_global_atomicity_or_durability_verified','actual_target_platform_or_clock_sampled',
        'actual_ledger_or_claim_created','actual_final_platform_frozen'}
    assert len(state)==33
    for k,v in state.items():
        if k in false_fields:assert v is False
        else:assert v is None
    assert d['current_effect']['CE06_accepted'] is False
    for r in rows:
        for k in ['actual_provider_identity','actual_provider_locator','actual_body_sha256','actual_body_bytes','actual_appointment','actual_acceptance_record']:assert r[k] is None
        assert r['status']=='MISSING_NOT_EVALUATED' and not r['accepted'] and not r['contact_authorized_now']
    return dict(CE06_baseline_rows=6,deferred_rows=5,eight_guarantees_require_real_bodies_not_flags=True,
        clock_and_revocation_not_derived_from_host_or_chat_date=True,one_global_namespace_across_callers_domains_restarts=True,
        mechanism_evidence_not_actual_CE12_invocation=True,no_uncertain_or_partial_claim_retry=True,
        resources_freeze_C_mapping_claim_stay_in_later_phases=True,all_actual_platform_clock_ledger_facts_missing=True)


def rejection_checks(d,plan):
    cases=['GUARANTEE_BOOL_AS_PROOF','HOST_CLOCK_AS_TRUSTED','PER_CALLER_LEDGER_INSTEAD_OF_GLOBAL','PARTIAL_CLAIM_FREE_RETRY',
        'ACTUAL_CLAIM_REQUIRED_AT_CE06','RESOURCE_JOIN_REQUIRED_AT_CE06','FINAL_PLATFORM_FREEZE_ASSIGNED_TO_CE06',
        'DEADLINE_AS_900_PROOF','EXTRA_CONTROL_PIPE','CE06_ACCEPTED_FROM_DOCUMENTATION']
    results=[]
    for case in cases:
        x=copy.deepcopy(d)
        if case==cases[0]:x['guarantee_evidence_inventory'][0]['actual_verified']=True
        elif case==cases[1]:x['clock_currentness_policy']['host_clock_or_client_date_is_not_accepted_runtime_clock']=False
        elif case==cases[2]:x['global_one_use_policy']['global_across_all_approved_callers_domains_and_restarts']=False
        elif case==cases[3]:x['global_one_use_policy']['free_retry_or_invocation_reuse_permitted']=True
        elif case==cases[4]:x['step_obligation_boundary']['CE06']['actual_invocation_claim_or_receipt_required']=True
        elif case==cases[5]:x['step_obligation_boundary']['CE06']['accepted_complete_resource_join_required_as_reverse_dependency']=True
        elif case==cases[6]:x['platform_requirements'][7]['consumer_step']='CE06'
        elif case==cases[7]:x['clock_currentness_policy']['deadline_counter_limits_not_service_or_900_proof']=False
        elif case==cases[8]:x['inherited_transport_policy']['explicit_control_pipe_count']=3
        else:x['current_effect']['CE06_accepted']=True
        try:check_platform_boundary(x,plan)
        except AssertionError:results.append(dict(case=case,result='REJECTED_DOCUMENTARY_PLATFORM_MUTATION'))
        else:raise AssertionError(case+' unexpectedly accepted')
    return results


def build_review():
    d=rd(DOS);plan=rd(PLAN);step=plan['steps'][5];spec=rd(SPEC);defs=rd(PACK)['$defs'];ce05=rd(CE05);ce01=rd(CE01)
    pins={**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==842 and d['input_pins']==pins;verify_git_blobs(pins)
    original=Path.exists
    with predecessor_CE06_presence_as_of_base():
        previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));rec=previous['reconstruct']()
        assert rec==rd(PRIOR_RECON) and previous['build_review'](rec)==rd(PRIOR_REVIEW)
    assert Path.exists is original and (ROOT/DOS).exists()
    assert d['schema']=='d5.i209-ce06-platform-clock-global-ledger-candidate.v1' and d['increment']=='I209' and d['base_commit']==BASE
    assert d['kind']=='MISSING_PLATFORM_CLOCK_LEDGER_DOCUMENTARY_DOSSIER_NOT_PLATFORM_RECORD_NOT_SERVICE'
    assert d['status']=='CE06_DOCUMENTARY_BASELINE_PREPARED_PLATFORM_CLOCK_LEDGER_MISSING_NOT_FROZEN_NOT_ACCEPTED_NOT_ADMITTED'
    assert d['plan_binding']==dict(**pin(PLAN,'/steps/5'),step_id='CE06',planned_path=DOS) and step['candidate_dossier_path']==DOS
    for k,s in [('required_evidence','required_evidence'),('planned_acceptance_checks','acceptance_checks'),('authorization_boundary','authorization_boundary'),('contract_rules','contract_rules')]:assert d[k]==step[s]
    assert len(d['required_evidence'])==len(d['planned_acceptance_checks'])==3 and d['contract_rules']==['K06','K07','K08','K13','K14','K15','K16']
    gate=rd(CHECK)['family_gates'][4];assert gate['family']=='platform_custody' and gate['candidate_step_ids']==['CE06','CE08'] and gate['final_record_freeze_step']=='CE08'
    assert d['checklist_binding']==pin(CHECK,'/family_gates/4') and not gate['accepted']
    dep=d['dependency_gate'];assert dep['candidate']==pin(CE05) and dep['last_documentary_review']==pin(PRIOR_REVIEW)
    assert dep['CE05_documentary_baseline_confirmation'] and not dep['competent_CE05_acceptance'] and not dep['actual_dependency_satisfied']
    assert rd(PRIOR_REVIEW)['verdict']['CE05_documentary_baseline_confirmed'] and not rd(PRIOR_REVIEW)['verdict']['CE05_accepted']
    refs={PLAN,CHECK,SPEC,PACK,CE05,CE04,CE03,CE01,PRIOR_REVIEW,P+'D5-I122-CAPACITY-CERTIFICATE.json',*[b['path'] for b in plan['bindings'].values()]}
    assert len(refs)==16 and d['documentary_inventory']==[dict(**pin(p),serialized_file_bytes=(ROOT/p).stat().st_size,
        availability='DOCUMENTARY_SOURCE_NOT_ACTUAL_PLATFORM_CLOCK_OR_LEDGER_PROOF') for p in sorted(refs)]
    props=defs['platform_custody']['properties'];guarantees=props['guarantees']['required']
    assert len(guarantees)==8 and [g['guarantee'] for g in d['guarantee_evidence_inventory']]==guarantees
    for g in d['guarantee_evidence_inventory']:assert g['schema_source']==pin(PACK,'/$defs/platform_custody/properties/guarantees/properties/'+g['guarantee'])
    boundary=check_platform_boundary(d,plan);negative=rejection_checks(d,plan)
    inverse={r:[] for r in d['contract_rules']}
    for row in d['platform_requirements']:
        for r in row['contract_rules']:inverse[r].append(row['id'])
    assert all(inverse.values())
    profile=rd(plan['bindings']['profile02']['path']);clock=d['clock_currentness_policy']
    assert clock['profile_binding']==pin(plan['bindings']['profile02']['path'],'/bootstrap')
    assert clock['max_UTC_error_seconds']==props['clock']['properties']['UTC_error_upper_seconds']['maximum']==profile['bootstrap']['context_limits']['max_clock_error_seconds']==5
    assert clock['max_snapshot_lifetime_seconds']==profile['bootstrap']['context_limits']['max_validity_seconds']==3600
    assert clock['time_rule']==profile['bootstrap']['time'] and clock['freshness_rule']==profile['bootstrap']['freshness']
    ledger=d['global_one_use_policy'];assert ledger['rule_source']==pin(SPEC,'/rules/13') and ledger['rule']==next(r['rule'] for r in spec['rules'] if r['id']=='K14')
    assert ledger['restart_policy_literal']==props['one_use']['properties']['restart_policy']['const']=='NO_PRIOR_INVOCATION_REUSE_FRESH_CONTEXT_REQUIRED'
    cross=d['cross_record_policy'];assert cross['same_actor_image_caller_domain_resource_scope_required'] and cross['genuine_prior_platform_authentication_required'] and cross['future_bundle_may_not_supply_sole_prior_authentication']
    assert cross['exact_C_rule']==next(r['rule'] for r in spec['rules'] if r['id']=='K08') and not cross['actual_C_or_mapping_available']
    assert [cross['actual_resource_join_consumer'],cross['actual_final_platform_freeze_consumer'],cross['actual_C_projection_consumer'],cross['actual_current_mapping_consumer']]==['CE07','CE08','CE09','CE10']
    tp=plan['bindings']['bootstrap_contract']['path'];gp=plan['bindings']['bootstrap_grammar']['path'];transport=rd(tp);grammar=rd(gp);t=d['inherited_transport_policy']
    assert t['contract_binding']==pin(tp) and t['grammar_binding']==pin(gp)
    for new,old in [('endpoint_ownership_requirements','endpoint_ownership'),('argv_and_channel_checks_requirement','argv_and_channel_checks'),('trust_boundary_requirements','trust_boundary'),('one_use_and_permissions_requirements','one_use_and_permissions')]:assert t[new]==transport[old]
    assert t['grammar_transport_limits']==grammar['transport_limits'] and t['grammar_permissions']==grammar['permissions'] and t['no_implicit_helper_input_file_network_fd_argv_attestation_or_environment_trust']
    schema=d['schema_obligations'];names=['platform_custody','identity','evidence_reference','validity']
    assert schema['schema_binding']==pin(PACK,'/$defs/platform_custody') and schema['definitions']==[dict(name=n,source=pin(PACK,'/$defs/'+n),schema_fragment=defs[n]) for n in names]
    assert schema['final_platform_body_cap_bytes']==spec['record_caps_bytes']['platform_custody']==16384
    for k in ['dossier_is_not_positive_platform_record','body_cap_not_applied_to_documentary_wrapper','limits_are_candidate_policy_not_active_quota']:assert schema[k] is True
    assert schema['actual_schema_codec_hash_or_crypto_validation']=='NOT_RUN_NO_ACTUAL_BODY' and schema['actual_final_body_validation_consumer_step']=='CE08'
    for r in d['role_scope_matrix']:
        s=next(s for s in ce01['role_scope_matrix'] if s['id']==r['id'])
        assert {k:v for k,v in r.items() if k!='CE06_responsibility'}=={k:v for k,v in s.items() if k!='CE01_responsibilities'}
    assert [r['id'] for r in d['role_scope_matrix']]==step['provenance_and_role']['primary_review_roles']==['R02','R03','R06','R08']
    for k in ['accepted_external_identity','actor_independent','organizationally_independent','independent_acceptance']:assert d['producer'][k] is False
    assert d['permission_boundary']['denied_action_classes']==ce05['permission_boundary']['denied_action_classes'] and len(d['permission_boundary']['denied_action_classes'])==14
    assert d['permission_boundary']['authorized_documentary_actions']==['READ_SOURCE_JSON_GIT_HASHES','PREPARE_CE06_MISSING_PLATFORM_CLOCK_LEDGER_DOSSIER','RUN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT']
    for k in ['no_platform_clock_or_ledger_selection_or_configuration','no_claim_replay_crash_restart_endpoint_clock_or_process_probe','no_provider_contact_or_nomination','no_build_import_product_components_crypto_or_codec_execution','no_active_state_or_quota_change']:assert d['permission_boundary'][k] is True
    assert d['inherited_scope_boundaries']==ce05['inherited_scope_boundaries'] and d['preserved_negative_gates']==ce05['preserved_negative_gates'] and d['freeze_and_refresh']==plan['freeze_and_refresh']
    for r in d['review_dispositions'].values():
        if isinstance(r,dict):assert r==dict(person=None,appointment=None,authority=None,decision='PENDING_NOT_ACCEPTED')
        else:assert r is True
    h=d['historical_scope'];assert not h['I193_saved_CE06_candidate_dossier_created'] and h['current_CE06_dossier_created']
    assert not step['candidate_dossier_created'] and not step['accepted'] and not h['other6_planned_dossiers_created'] and h['actual_accepted_steps']==0
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][:6]) and all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][6:])
    ready=d['missing_facts_and_readiness'];assert ready['candidate_documentary_ready_for_review'] and len(ready['missing'])==4
    for k in ['actual_platform_clock_or_ledger_proof_available','actual_CE05_dependency_accepted','actual_CE06_acceptance_ready','actual_CE08_finalization_ready']:assert ready[k] is False
    assert ready['no_qualification_sampling_claim_probe_contact_or_fabrication_to_fill_missing_facts']
    effect=d['current_effect'];assert effect['CE06_documentary_baseline_prepared'] and effect['candidate_dossiers_prepared_this_increment']==1
    assert effect['actual_accepted_steps']==effect['actual_external_evidence_accepted']==effect['resource_obligations_closed']==0
    for k,v in effect.items():
        if k not in ['CE06_documentary_baseline_prepared','candidate_dossiers_prepared_this_increment','actual_accepted_steps','actual_external_evidence_accepted','resource_obligations_closed','IR03']:assert v is False
    assert effect['IR03']=='NOT_READY' and d['decision']==plan['decision'] and d['E06']==plan['E06']
    assert set(d['work_unit']['rollback_files'])==FILES and d['work_unit']['verification_command']=='python3 docs/validation/D5-I209-audit.py'
    return dict(schema='d5.i209-preparation-review.v1',increment='I209',date='2026-11-17',base_commit=BASE,
        dossier=pin(DOS),input_pins=pins,status='CE06_MISSING_PLATFORM_CLOCK_LEDGER_BASELINE_PREPARED_NOT_ACCEPTED',
        provenance=dict(preparer='Same Codex assistant/chat',actor_independent=False,organizationally_independent=False,competent_R02_R03_R06_R08_acceptance=False),
        historical_replay=dict(exact_CE06_absence_verified_in_BASE_git_tree=True,only_CE06_presence_projected_during_predecessor_reconstruction=True,
            original_nested_CE05_to_CE01_guards_preserved=True,prior_I208_reconstruction_and_review_reproduced=True,presence_method_restored=True,
            current_CE06_real_path_bytes_separately_required=True,other_planned_dossiers_absent=6,prior_publication_mains_run=False),
        coverage=dict(required_evidence_items=3,acceptance_checks=3,authorization_boundaries=1,contract_rules=step['contract_rules'],
            inverse_rule_to_requirement=inverse,documentary_sources=16,guarantee_slots=8,platform_boundary_checks=boundary,documentary_negative_checks=negative,
            schema_definitions=4,final_platform_candidate_cap=16384,actual_final_body_available=False,review_slots_unassigned=4,competent_CE05_dependency_satisfied=False),
        limitations=['Negative documentary wrapper only: no actual platform/domain/clock/ledger, enforcement bodies, accepted proof, snapshot, epoch or claim.',
            'Mechanism provenance/guarantee/reference fields are not evidence by themselves; client/host date and deadline/counter policies prove no currentness, service or900 seconds.',
            'Resources/freeze/C/mapping/actual claim remain CE07/CE08/CE09/CE10/CE12. No reverse dependency or actual invocation is required to prepare CE06.'],
        current_effect=effect,decision=d['decision'],E06=d['E06'])


def main():
    assert rd(PREP)==build_review()
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published529'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==534
    seal=rd(SEAL);assert seal['schema']=='d5.i209-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published534']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['CE06_accepted','actual_platform_record_created','actual_platform_record_finalized','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY_PLATFORM_CLOCK_LEDGER_MISSING',increment='I209',CE06_baseline_prepared=True,
        CE06_accepted=False,actual_platform_record_created=False,actual_platform_record_finalized=False,actual_CE05_dependency_satisfied=False,
        historical_pins=842,prior_published_files_preserved=534,new_files=5,documentary_rejection_checks=10,actual_evidence_accepted=0,
        independent_acceptance=False,product_or_components_executed=0,quotas_changed=False,rebind_applied=False,
        resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
