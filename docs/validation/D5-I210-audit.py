#!/usr/bin/env python3
"""I210 documentary platform/clock/global-ledger review; no component execution."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='95fe546adece2cc362cec262e5ee7e7515b276e0'
DOS=P+'D5-I193-CE06-PLATFORM-CLOCK-GLOBAL-LEDGER-CANDIDATE.json'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json';CHECK=P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json';PACK=P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CE05=P+'D5-I193-CE05-CALLER-CONSTRUCTOR-DOMAIN-CANDIDATE.json'
PRIOR_AUDIT=P+'D5-I209-audit.py';PRIOR_PREP=P+'D5-I209-preparation-review.json';PRIOR_SEAL=P+'D5-I209-integrity.json'
PRIOR_DOC='docs/design/D5-I209-CE06-PLATFORM-CLOCK-GLOBAL-LEDGER.md';PRIOR_FILES={DOS,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON=P+'D5-I210-I209-source-reconstruction.json';REVIEW=P+'D5-I210-I209-documentary-review.json'
AUDIT=P+'D5-I210-audit.py';SEAL=P+'D5-I210-integrity.json';DOC='docs/design/D5-I210-I209-CE06-REVIEW.md'
FILES={RECON,REVIEW,AUDIT,SEAL,DOC}


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pin(p,q=''):return dict(path=p,sha256=sha(p),json_pointer=q)


def verify_git_blobs(pins):
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()))
    for p,h in sorted(pins.items()):
        header=stream.readline().decode().split();assert len(header)==3 and header[1]=='blob',p
        body=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    assert stream.read()==b''


def ancestors(graph):
    active=set();done={}
    def visit(n):
        assert n in graph and n not in active,n
        if n in done:return done[n]
        active.add(n);found=set()
        for p in graph[n]:found.add(p);found.update(visit(p))
        active.remove(n);assert n not in found;done[n]=found;return found
    for n in sorted(graph):visit(n)
    return done


def review_presence_guard(previous,plan):
    target=ROOT/DOS;existing=[ROOT/s['candidate_dossier_path'] for s in plan['steps'][:5]]
    missing=ROOT/plan['steps'][6]['candidate_dossier_path'];original=Path.exists
    assert git('ls-tree','--name-only',previous['BASE'],'--',DOS)==''
    assert git('ls-tree','--name-only',BASE,'--',DOS)==DOS
    assert target.exists() and all(p.exists() for p in existing) and not missing.exists()
    with previous['predecessor_CE06_presence_as_of_base']():
        assert not target.exists() and all(p.exists() for p in existing) and not missing.exists()
    assert Path.exists is original and target.exists()
    class DocumentaryProbe(Exception):pass
    try:
        with previous['predecessor_CE06_presence_as_of_base']():
            assert not target.exists()
            raise DocumentaryProbe()
    except DocumentaryProbe:pass
    else:raise AssertionError('Expected documentary exception not raised')
    assert Path.exists is original and target.exists() and all(p.exists() for p in existing) and not missing.exists()
    return dict(CE06_absent_in_preparation_base_verified=True,CE06_present_in_review_base_verified=True,
        exact_CE06_query_only=True,CE01_to_CE05_existing_and_CE07_missing_preserved=True,
        restored_after_success=True,restored_after_exception=True,prior_publication_mains_run=False)


def reconstruct():
    d=rd(DOS);plan=rd(PLAN);spec=rd(SPEC);defs=rd(PACK)['$defs'];step=plan['steps'][5]
    pins={**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==847;verify_git_blobs(pins)
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));assert previous['build_review']()==rd(PRIOR_PREP)
    guard=review_presence_guard(previous,plan)
    assert step['id']=='CE06' and step['depends_on']==['CE05']
    assert d['required_evidence']==step['required_evidence'] and len(d['required_evidence'])==3
    assert d['planned_acceptance_checks']==step['acceptance_checks'] and len(d['planned_acceptance_checks'])==3
    assert d['authorization_boundary']==step['authorization_boundary']
    assert d['contract_rules']==step['contract_rules']==['K06','K07','K08','K13','K14','K15','K16']
    consumers={s:[] for s in ['CE06','CE07','CE08','CE09','CE10','CE12']};rules={r:{} for r in d['contract_rules']}
    for row in d['platform_requirements']:
        c=row['consumer_step'];assert c in consumers;consumers[c].append(row['id'])
        for k in row['contract_rules']:rules[k].setdefault(c,[]).append(row['id'])
        for k in ['actual_provider_identity','actual_provider_locator','actual_body_sha256','actual_body_bytes','actual_appointment','actual_acceptance_record']:assert row[k] is None
        assert row['status']=='MISSING_NOT_EVALUATED' and not row['accepted'] and not row['contact_authorized_now']
    assert consumers==dict(CE06=['PF%02d'%i for i in range(1,7)],CE07=['PF07'],CE08=['PF08'],CE09=['PF09'],CE10=['PF10'],CE12=['PF11'])
    phases=d['step_obligation_boundary'];graph={s['id']:s['depends_on'] for s in plan['steps']};closure=ancestors(graph)
    for name,ids in consumers.items():
        assert phases[name]['requirement_ids']==ids and phases[name]['required_step_ids']==graph[name]
        assert not phases[name]['actual_acceptance'] and not phases[name]['current_execution_authorized']
        assert phases[name]['actual_dossier_created']==(name=='CE06')
    assert closure['CE06']=={'CE01','CE02','CE03','CE04','CE05'} and not ((set(consumers)-{'CE06'}) & closure['CE06'])
    a=phases['CE06'];assert a['baseline_mechanism_proof_not_actual_invocation'] and a['guarantee_policy_or_hash_is_not_proof']
    for k in ['actual_invocation_claim_or_receipt_required','actual_C_or_mapping_or_final_platform_hash_required','accepted_complete_resource_join_required_as_reverse_dependency']:assert a[k] is False
    assert graph['CE07']==['CE04','CE05','CE06'] and graph['CE08']==['CE02','CE03','CE04','CE05','CE06','CE07']
    assert graph['CE09']==['CE08'] and graph['CE10']==['CE02','CE08','CE09'] and graph['CE12']==['CE11'] and 'CE12' not in closure['CE11']
    assert phases['CE08']['final_record_order']==plan['steps'][7]['record_families']
    assert phases['CE12']['external_prerequisites_for_receipt']==plan['closure_boundaries']['external_prerequisites_for_receipt']
    assert phases['CE12']['separate_authorization_full_admission_before_claim_required'] and phases['CE12']['claim_is_prereceipt_event_not_own_precondition'] and phases['CE12']['CE11_does_not_depend_on_CE12']
    order=ancestors(spec['record_order']);assert {'ACTOR_REGISTRY','IMAGE_MANIFEST','CALLER_IDENTITY'}<=order['PLATFORM_CUSTODY']
    assert 'PLATFORM_CUSTODY' in order['C_CONTEXT'] and {'EXTERNAL_CURRENT_MAPPING','FINAL_ROOT'}<=order['ATOMIC_CLAIM'] and 'ATOMIC_CLAIM' in order['LAUNCH_RECEIPT']
    props=defs['platform_custody']['properties'];names=props['guarantees']['required'];inventory=d['guarantee_evidence_inventory']
    assert len(names)==len(inventory)==8 and [g['guarantee'] for g in inventory]==names
    for g in inventory:
        assert g['schema_source']==pin(PACK,'/$defs/platform_custody/properties/guarantees/properties/'+g['guarantee'])
        for k in ['actual_provider_identity','actual_record_id','actual_evidence_sha256','actual_proof_body','actual_proof_bytes','actual_scope_binding','actual_acceptance_record']:assert g[k] is None
        assert g['status']=='MISSING_NOT_EVALUATED' and not g['actual_verified'] and not g['accepted']
    clock=d['clock_currentness_policy'];profile=rd(plan['bindings']['profile02']['path'])
    assert clock['max_UTC_error_seconds']==profile['bootstrap']['context_limits']['max_clock_error_seconds']==props['clock']['properties']['UTC_error_upper_seconds']['maximum']==5
    assert clock['max_snapshot_lifetime_seconds']==profile['bootstrap']['context_limits']['max_validity_seconds']==3600
    assert clock['time_rule']==profile['bootstrap']['time'] and clock['freshness_rule']==profile['bootstrap']['freshness']
    for k in ['accepted_clock_and_monotonic_UTC_evidence_required','host_clock_or_client_date_is_not_accepted_runtime_clock',
        'no_TOFU_stale_cache_hidden_online_or_file_lookup','missing_clock_currentness_durability_assurance_stays_pending','deadline_counter_limits_not_service_or_900_proof']:assert clock[k] is True
    assert clock['actual_clock_error_or_sample'] is None and clock['actual_trusted_now'] is None and not clock['instantaneous_all_revocation_discovery_claimed']
    ledger=d['global_one_use_policy'];assert ledger['rule']==next(r['rule'] for r in spec['rules'] if r['id']=='K14')
    assert ledger['tuple_fields']==['trust_context_sha256','runtime_request_sha256','invocation_id']
    for k in ['one_authoritative_global_namespace_required','global_across_all_approved_callers_domains_and_restarts',
        'high_water_epoch_and_atomic_durable_rollback_crash_proof_required','uncertain_or_partial_claim_spends_or_rejects',
        'parent_child_is_one_correlated_invocation','mapping_and_ledger_domain_must_agree','literal_is_requirement_not_running_backend_or_new_authorization']:assert ledger[k] is True
    for k in ['free_retry_or_invocation_reuse_permitted','actual_claim_or_receipt_required_for_CE06_mechanism_evidence','actual_live_claim_replay_crash_restart_or_endpoint_test_performed']:assert ledger[k] is False
    assert ledger['actual_tuple_or_claim'] is None and ledger['actual_ledger_domain_or_epoch'] is None
    assert ledger['restart_policy_literal']==props['one_use']['properties']['restart_policy']['const']=='NO_PRIOR_INVOCATION_REUSE_FRESH_CONTEXT_REQUIRED'
    assert ledger['actual_claim_construction_consumer']=='CE12' and ledger['actual_unique_mapping_consumer']=='CE10'
    cross=d['cross_record_policy'];assert cross['exact_C_rule']==next(r['rule'] for r in spec['rules'] if r['id']=='K08')
    assert cross['same_actor_image_caller_domain_resource_scope_required'] and cross['genuine_prior_platform_authentication_required'] and cross['future_bundle_may_not_supply_sole_prior_authentication'] and not cross['actual_C_or_mapping_available']
    assert [cross['actual_resource_join_consumer'],cross['actual_final_platform_freeze_consumer'],cross['actual_C_projection_consumer'],cross['actual_current_mapping_consumer']]==['CE07','CE08','CE09','CE10']
    t=d['inherited_transport_policy'];transport=rd(plan['bindings']['bootstrap_contract']['path']);grammar=rd(plan['bindings']['bootstrap_grammar']['path'])
    for new,old in [('endpoint_ownership_requirements','endpoint_ownership'),('argv_and_channel_checks_requirement','argv_and_channel_checks'),('trust_boundary_requirements','trust_boundary'),('one_use_and_permissions_requirements','one_use_and_permissions')]:assert t[new]==transport[old]
    assert t['grammar_transport_limits']==grammar['transport_limits'] and t['grammar_permissions']==grammar['permissions']
    assert t['explicit_control_pipe_count']==2 and t['observed_worker_operand_count']==6 and not t['actual_backend_constructor_or_endpoint_selected'] and not t['actual_probe_or_process_creation']
    state=d['actual_platform_clock_ledger_state'];false_fields={'actual_platform_or_clock_or_ledger_selected','actual_guarantees_verified',
        'actual_clock_or_currentness_verified','actual_global_atomicity_or_durability_verified','actual_target_platform_or_clock_sampled','actual_ledger_or_claim_created','actual_final_platform_frozen'}
    assert len(state)==33
    for k,v in state.items():
        if k in false_fields:assert v is False
        else:assert v is None
    schema=d['schema_obligations'];assert len(schema['definitions'])==4
    for row in schema['definitions']:assert row['schema_fragment']==defs[row['name']]
    assert schema['final_platform_body_cap_bytes']==spec['record_caps_bytes']['platform_custody']==16384
    assert schema['dossier_is_not_positive_platform_record'] and schema['body_cap_not_applied_to_documentary_wrapper']
    assert schema['actual_schema_codec_hash_or_crypto_validation']=='NOT_RUN_NO_ACTUAL_BODY' and schema['actual_final_body_validation_consumer_step']=='CE08'
    assert len(defs['platform_custody']['required'])==14 and len(props['clock']['required'])==4 and len(props['one_use']['required'])==5
    gate=next(g for g in rd(CHECK)['family_gates'] if g['family']=='platform_custody');assert gate['final_record_freeze_step']=='CE08' and not gate['accepted']
    assert d['inherited_scope_boundaries']==rd(CE05)['inherited_scope_boundaries'] and d['preserved_negative_gates']==rd(CE05)['preserved_negative_gates']
    assert not d['dependency_gate']['actual_dependency_satisfied'] and not d['dependency_gate']['competent_CE05_acceptance']
    assert [r['id'] for r in d['role_scope_matrix']]==['R02','R03','R06','R08']
    for r in d['role_scope_matrix']:assert r['assigned_person'] is None and not r['accepted_appointment'] and r['current_actions_authorized']==[]
    assert len(d['permission_boundary']['authorized_documentary_actions'])==4 and len(d['permission_boundary']['denied_action_classes'])==14
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][6:])
    assert d['decision']==plan['decision'] and d['E06']==plan['E06']
    return dict(schema='d5.i210-i209-source-reconstruction.v1',increment='I210',date='2026-11-17',base_commit=BASE,
        input_pins=pins,method='Fresh Git blobs, independent consumer/rule incidence and I193/I191 ancestor reconstruction; direct eight-proof/clock/global-mechanism review and historical guard checks. Predecessor documentary build reproduced without publication main.',
        requirement_consumers=consumers,rule_consumers=rules,historical_presence_guard=guard,
        phase_review=dict(I193_dependency_graph_acyclic=True,CE06_ancestors=sorted(closure['CE06']),no_reverse_dependency_on_later_phases=True,
            resource_join='CE07',final_platform_freeze='CE08',actual_C_projection='CE09',unique_mapping='CE10',actual_claim_construction_receipt='CE12',
            no_CE11_receipt_dependency=True,I191_antecedent_order_acyclic=True,platform_before_C_and_mapping_root_before_claim=True,
            claim_is_actual_prereceipt_event_not_own_precondition=True),
        guarantee_clock_ledger_review=dict(guarantee_slots=names,all_actual_guarantee_bodies_and_acceptances_missing=True,
            max_candidate_UTC_error_seconds=5,max_snapshot_lifetime_seconds=3600,actual_error_sample_trusted_now_or_epoch_available=False,
            host_or_client_time_not_trust_evidence=True,no_instantaneous_revocation_claim=True,no_deadline_as_service_or_900_proof=True,
            one_authoritative_global_namespace_across_callers_domains_restarts=True,tuple_fields=ledger['tuple_fields'],
            durable_atomic_high_water_rollback_crash_proof_required=True,uncertain_partial_claim_no_free_retry=True,
            mechanism_proof_distinct_from_actual_CE12_claim=True,no_ledger_clock_or_platform_instantiated_or_tested=True),
        preserved_scope=dict(documentary_sources=16,schema_definitions=4,final_platform_candidate_cap=16384,closed_platform_fields=14,
            actual_final_body_or_codec_schema_crypto_validation=False,unassigned_review_slots=4,competent_CE05_dependency_satisfied=False,
            other_planned_dossiers_absent=6,prior_documentary_rejection_checks_reproduced=10,
            caps_numeric_permissions_role_policy_and_negative_gates_unchanged=True,original_I209_preparation_preserved=True,prior_publication_mains_run=False),
        verdict=dict(new_blocking_documentary_findings=0,CE06_documentary_baseline_confirmed=True,CE06_accepted=False,
            actual_platform_record_created=False,actual_platform_record_finalized=False,actual_guarantees_clock_or_global_ledger_verified=False,
            actual_claim_or_process_created=False,adopted=False,implemented=False,independent_acceptance=False,
            actual_evidence_accepted=0,resource_obligations_closed=0,product_or_components_executed=0))


def build_review(rec):
    d=rd(DOS);plan=rd(PLAN)
    checks=[
        ('E01','Eight genuine same-scope platform guarantee bodies','PASS_EXACT_SLOTS_REQUIRED_NOT_FLAGS_OR_HASHES_AS_PROOF'),
        ('E02','Accepted clock/monotonic/UTC error/currentness/revocation/validity','PASS_MISSING_REAL_CLOCK_NOT_HOST_OR_CLIENT_DATE'),
        ('E03','One global atomic/durable namespace with high-water/rollback/crash/partial-state proof','PASS_MECHANISM_REQUIREMENT_NOT_ACTUAL_INVOCATION'),
        ('A01','Same actor/image/caller/domain/resource scope and genuine antecedent authentication','PASS_SCOPE_POLICY_NOT_PLATFORM_CUSTODY_ACCEPTANCE'),
        ('A02','No live claim/process/probe/replay/clock measurement in preparation','PASS_NO_ACTIVE_QUALIFICATION'),
        ('A03','Absent durability/clock/enforcement pending; deadlines/counters not service or900 proof','PASS_NO_POLICY_AS_PERFORMANCE_GUARANTEE'),
        ('B01','Only authentic available evidence; needed qualification separately authorized','PASS_NO_PLATFORM_OR_LEDGER_FABRICATION'),
        ('K06','Prior actor/image/caller/platform facts before C/resource acceptance, no future-bundle bootstrap','PASS_ANTECEDENTS_NOT_ACCEPTED_PLATFORM'),
        ('K07','Exact first-entry/domain/channel enforcement requirements and unchanged I189 scope','PASS_REQUIREMENTS_NOT_MECHANISM_OR_ENDPOINT_PROOF'),
        ('K08','Same records/resource scope and conservative C clock/validity, with later projection','PASS_CE08_CE09_BOUNDARIES_NOT_REAL_HASHES_OR_C'),
        ('K13','Strict<=3600 snapshots/<=5 error/current epoch/known revocation, no TOFU/stale fallback','PASS_FRESHNESS_POLICY_NOT_ACTUAL_CURRENTNESS'),
        ('K14','Global across callers/domains/restarts, no free retry, one correlated invocation','PASS_CE06_MECHANISM_VERSUS_DEFERRED_CE12_EVENT'),
        ('K15','All lookup/freshness/identity/crypto/copies/ledger/receipt/native/IO inside phases/global resources','PASS_UNWAIVED_CE07_OBLIGATION_NOT_RESOURCE_PROOF'),
        ('K16','Cap16384/evidence indices distinct from proof/heap/CPU; no active quotas changed','PASS_CANDIDATE_LIMITS_NOT_FIT_OR_ADMISSION')]
    effect={**d['current_effect'],'CE06_documentary_review_completed':True,'CE06_documentary_confirmation':True,
        'CE06_documentary_revision_required':False,'actual_guarantees_clock_or_global_ledger_verified':False}
    return dict(schema='d5.i210-i209-documentary-review.v1',increment='I210',date='2026-11-17',timezone='Europe/Madrid',base_commit=BASE,
        proposal=d['proposal_id'],profile_id=d['profile_id'],step='CE06',
        status='CE06_DOCUMENTARY_BASELINE_CONFIRMED_PLATFORM_CLOCK_LEDGER_MISSING_NOT_FROZEN_NOT_ACCEPTED_NOT_ADMITTED',
        reconstruction=pin(RECON),provenance=dict(reviewer='Same Codex assistant/chat that prepared I209 and earlier candidates',
            methodological_reconstruction_separate=True,actor_independent=False,organizationally_independent=False,
            competent_R02_R03_R06_review=False,separate_R08_acceptance=False,independent_acceptance=False),
        findings=[],checks=[dict(id=i,scope=s,result=r) for i,s,r in checks],
        evidence=[pin(DOS,'/guarantee_evidence_inventory'),pin(DOS,'/clock_currentness_policy'),pin(DOS,'/global_one_use_policy'),
            pin(DOS,'/cross_record_policy'),pin(DOS,'/step_obligation_boundary'),pin(DOS,'/actual_platform_clock_ledger_state'),
            pin(PLAN,'/steps/5'),pin(PLAN,'/closure_boundaries'),pin(CHECK,'/family_gates/4'),pin(PACK,'/$defs/platform_custody'),pin(SPEC,'/record_order')],
        verdict=rec['verdict'],current_effect=effect,decision=plan['decision'],E06=d['E06'],
        limitations=['Exact documentary baseline only: no genuine platform/domain/enforcement/clock/currentness/revocation/epoch/global ledger body or acceptance; all eight guarantees still missing.',
            'Global one-use, durable/high-water/restart/rollback rules describe required mechanism evidence, not an actual claim/receipt or proof that a service enforces them. No active qualification/probe run.',
            'Same assistant preparation/review is not independent competent R02/R03/R06/R08 acceptance. Actual CE01-CE06 prerequisites and resources/final records/C/mapping/root/admission remain pending.',
            'Client/host date and deadline/counter bounds are not trusted time, service or900-second evidence; no configuration, enrollment, execution, contact, authority/quota/rebind or D5 release follows.'],
        next_scope='CE06 can proceed as a documentarily reviewed missing-evidence baseline. A separately requested CE07 documentary preparation is possible, preserving every missing source/runtime/backend/resource premise and no actual qualification or PASS. All genuine competent decisions remain pending.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I210-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: documentary JSON/Git/guarantee-clock-ledger-policy/schema-fragment/phase review; no platform selection/clock sampling/claim/replay/crash/restart/process/probe/product/components/crypto/codec execution.',
            over400_lines=True,reason='One pinned eight-guarantee/clock/global-mechanism and phase review with independent antecedents, guard restoration and preservation evidence; overage reported.'),
        publication=dict(commit_and_push_requested=True,publication_not_adoption_acceptance_or_authority=True))


def main():
    rec=reconstruct();assert rd(RECON)==rec and rd(REVIEW)==build_review(rec)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published534'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==539
    seal=rd(SEAL);assert seal['schema']=='d5.i210-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published539']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['CE06_accepted','actual_platform_record_created','actual_platform_record_finalized','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I210',new_blocking_documentary_findings=0,
        CE06_documentary_baseline_confirmed=True,CE06_accepted=False,actual_platform_record_created=False,actual_platform_record_finalized=False,
        historical_pins=847,prior_published_files_preserved=539,new_files=5,actual_evidence_accepted=0,independent_acceptance=False,
        product_or_components_executed=0,quotas_changed=False,rebind_applied=False,resource_obligations_closed=0,
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
