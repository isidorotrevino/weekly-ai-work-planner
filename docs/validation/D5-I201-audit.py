#!/usr/bin/env python3
"""I201: documentary CE02 phase revision; no product/components/crypto execution."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='473507bacda8146813970011ec35acb24e941fd1'
OLD=P+'D5-I193-CE02-ANCHOR-PROVENANCE-CANDIDATE.json'
DOS=P+'D5-I201-CE02-ANCHOR-PROVENANCE-CANDIDATE-02.json'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PRIOR_REVIEW=P+'D5-I200-I199-documentary-review.json'
PRIOR_RECON=P+'D5-I200-I199-source-reconstruction.json'
PRIOR_AUDIT=P+'D5-I200-audit.py';PRIOR_SEAL=P+'D5-I200-integrity.json'
PRIOR_DOC='docs/design/D5-I200-I199-CE02-REVIEW.md'
PRIOR_FILES={PRIOR_REVIEW,PRIOR_RECON,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
PREP=P+'D5-I201-preparation-review.json';AUDIT=P+'D5-I201-audit.py';SEAL=P+'D5-I201-integrity.json'
DOC='docs/design/D5-I201-CE02-ANCHOR-PROVENANCE-02.md'
FILES={DOS,PREP,AUDIT,SEAL,DOC}
POLICY='AP08-ANCHOR-POLICY';APPROVAL='AP08-BUNDLE-APPROVAL'


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pin(p,q=''):return dict(path=p,sha256=sha(p),json_pointer=q)


def verify_git_pins(pins):
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()))
    for p,h in sorted(pins.items()):
        header=stream.readline().decode().split();assert len(header)==3 and header[1]=='blob',p
        body=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    assert stream.read()==b''


def check_phase_boundaries(d,plan,finding):
    """Check consumer/phase and authentic prior acceptance, not only K-rule coverage."""
    rows=d['evidence_requirements'];by_id={r['id']:r for r in rows}
    assert len(by_id)==len(rows)==10 and 'AP08' not in by_id
    p=by_id[POLICY];f=by_id[APPROVAL]
    assert p['consumer_step']=='CE02' and f['consumer_step']=='CE10'
    assert p['contract_rules']==['K01','K03','K11'] and f['contract_rules']==['K11']
    assert p['requirement_kind']=='PRIOR_EXTERNAL_ANCHOR_PROVISIONING_AND_APPROVAL_POLICY'
    assert f['requirement_kind']=='DEFERRED_ACTUAL_BUNDLE_APPROVAL_EVIDENCE'
    for row,proposal in zip([p,f],finding['repair_proposal_not_applied']):assert row['required_genuine_evidence']==proposal['requirement']
    assert p['genuine_prior_provisioning_and_acceptance_required'] is True
    assert p['future_CE10_bundle_approval_required'] is False and p['selection_policy_source']==pin(SPEC,'/rules/10')
    assert f['authentic_antecedents_and_exact_C_before_approvals'] is True and f['independently_accepted_CE02_anchors_required'] is True
    for k in ['bundle_approvals_may_authenticate_their_own_anchors','current_action_authorized','CE10_dossier_created']:assert f[k] is False
    a=d['step_obligation_boundary']['CE02'];b=d['step_obligation_boundary']['CE10']
    assert a['plan_source']==pin(PLAN,'/steps/1') and b['plan_source']==pin(PLAN,'/steps/9')
    assert a['required_step_ids']==plan['steps'][1]['depends_on']==['CE01']
    assert b['required_step_ids']==plan['steps'][9]['depends_on']==['CE02','CE08','CE09']
    assert a['required_requirement_ids']==['AP%02d'%i for i in range(1,8)]+[POLICY,'AP09']
    assert b['deferred_requirement_ids']==[APPROVAL] and APPROVAL not in a['required_requirement_ids']
    for k in ['genuine_prior_anchor_provisioning_and_acceptance_required','authentic_identity_authority_external_expected_digest_epochs_and_bindings_required',
              'approval_policy_is_not_actual_bundle_approval','no_execution_gate_release']:assert a[k] is True
    for k in ['actual_future_CE10_bundle_approvals_required','future_C_or_bundle_may_bootstrap_anchors','accepted']:assert a[k] is False
    for k in ['actual_common_core_approvals_required','accepted_anchors_and_exact_C_before_actual_approvals']:assert b[k] is True
    for k in ['bundle_approvals_may_discharge_CE02_prior_acceptance','currently_authorized','actual_dossier_created','accepted']:assert b[k] is False
    actual=d['actual_anchor_state'];assert 'actual_signature_or_custody_approvals' not in actual
    assert actual['genuine_prior_acceptance_record'] is None and actual['genuine_prior_anchor_provisioning_acceptance_evidence'] is None
    availability=d['future_CE10_bundle_approval_availability']
    assert availability==dict(consumer_step='CE10',requirement_id=APPROVAL,actual_bundle_approvals=None,
        actual_signed_core_sha256=None,actual_C_sha256=None,status='DEFERRED_EVIDENCE_MISSING_NOT_EVALUATED',
        actual_evidence_supplied=False,accepted=False,actual_schema_codec_or_crypto_validation='NOT_RUN',
        current_action_authorized=False,actual_CE10_dossier_created=False)
    c=d['trust_and_currentness_contract']
    assert c['custody_domains_are_selection_policy_not_actual_approvals'] and c['actual_bundle_approvals_consumer_step']=='CE10'
    assert c['no_future_bundle_approval_needed_for_CE02_provenance'] and c['genuine_prior_anchor_acceptance_still_required']
    for row in rows:
        for k in ['actual_provider_identity','actual_provider_locator','actual_body_sha256','actual_body_bytes','actual_appointment','actual_acceptance_record']:assert row[k] is None
        assert row['status']=='MISSING_NOT_EVALUATED' and not row['accepted'] and not row['contact_authorized_now']
    return dict(CE02_prior_genuine_acceptance_required=True,CE02_no_future_bundle_approval_required=True,
        actual_three_role_approvals_deferred_to_CE10=True,CE10_depends_on_accepted_CE02_and_exact_antecedents=True,
        prior_acceptance_and_future_approval_availability_separate=True,no_trust_bootstrap_from_future_C_or_bundle=True,
        actual_CE10_dossier_created=False,current_execution_contact_or_crypto_authorized=False)


def rejection_checks(d,plan,finding):
    """In-memory documentary counterexamples only; no product/runtime data is run."""
    cases=['FUTURE_APPROVAL_ASSIGNED_TO_CE02','FUTURE_APPROVAL_REQUIRED_FOR_CE02',
        'GENUINE_PRIOR_ACCEPTANCE_WAIVED','BUNDLE_BOOTSTRAPS_OWN_ANCHORS','CE10_AUTHORIZED_BY_REVISION',
        'CE10_DROPS_CE02_PREREQUISITE','PRIOR_AND_FUTURE_AVAILABILITY_RECOMBINED']
    results=[]
    for case in cases:
        x=copy.deepcopy(d)
        if case==cases[0]:x['evidence_requirements'][8]['consumer_step']='CE02'
        elif case==cases[1]:x['step_obligation_boundary']['CE02']['actual_future_CE10_bundle_approvals_required']=True
        elif case==cases[2]:x['step_obligation_boundary']['CE02']['genuine_prior_anchor_provisioning_and_acceptance_required']=False
        elif case==cases[3]:x['evidence_requirements'][8]['bundle_approvals_may_authenticate_their_own_anchors']=True
        elif case==cases[4]:x['step_obligation_boundary']['CE10']['currently_authorized']=True
        elif case==cases[5]:x['step_obligation_boundary']['CE10']['required_step_ids'].remove('CE02')
        else:x['actual_anchor_state']['actual_signature_or_custody_approvals']=None
        try:check_phase_boundaries(x,plan,finding)
        except AssertionError:results.append(dict(case=case,result='REJECTED_DOCUMENTARY_PHASE_MUTATION'))
        else:raise AssertionError(case+' unexpectedly accepted')
    return results


def build_review():
    d=rd(DOS);old=rd(OLD);plan=rd(PLAN);prior_review=rd(PRIOR_REVIEW);finding=prior_review['findings'][0]
    pins={**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==802 and d['input_pins']==pins;verify_git_pins(pins)
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));rec=previous['reconstruct']()
    assert rec==rd(PRIOR_RECON) and previous['build_review'](rec)==prior_review
    assert finding['id']=='F199-01' and finding['status']=='OPEN_DOCUMENTARY_REVISION_REQUIRED'
    assert d['schema']=='d5.i201-ce02-anchor-provenance-candidate-02.v1' and d['increment']=='I201' and d['base_commit']==BASE
    assert d['candidate_id']=='CE02-ANCHOR-PROVENANCE-CANDIDATE-02'
    assert d['status']=='CE02_DOCUMENTARY_CANDIDATE_02_REPAIR_PREPARED_EVIDENCE_MISSING_NOT_ADOPTED_NOT_ACCEPTED_NOT_ADMITTED'
    allowed={'schema','increment','base_commit','candidate_id','status','input_pins','revision_binding','evidence_requirements',
        'future_CE10_bundle_approval_availability','step_obligation_boundary','finding_response','historical_scope','work_unit',
        'actual_anchor_state','trust_and_currentness_contract','missing_facts_and_readiness','current_effect'}
    changed={k for k in set(old)|set(d) if old.get(k)!=d.get(k)};assert changed==allowed,changed
    for k in set(old)-allowed:assert d[k]==old[k],k
    assert d['revision_binding']==dict(supersedes_documentary_candidate=pin(OLD),source_review=pin(PRIOR_REVIEW,'/findings/0'),
        finding_id='F199-01',historical_I193_planned_path=OLD,current_candidate_path=DOS,active_binding_changed=False)
    assert d['evidence_requirements'][:7]==old['evidence_requirements'][:7] and d['evidence_requirements'][9:]==old['evidence_requirements'][8:]
    scope=check_phase_boundaries(d,plan,finding);negative=rejection_checks(d,plan,finding)
    actual=copy.deepcopy(old['actual_anchor_state']);actual.pop('actual_signature_or_custody_approvals')
    actual['genuine_prior_anchor_provisioning_acceptance_evidence']=None;assert d['actual_anchor_state']==actual
    contract={**old['trust_and_currentness_contract'], 'custody_domains_are_selection_policy_not_actual_approvals':True,
        'actual_bundle_approvals_consumer_step':'CE10','no_future_bundle_approval_needed_for_CE02_provenance':True,
        'genuine_prior_anchor_acceptance_still_required':True}
    assert d['trust_and_currentness_contract']==contract
    response=d['finding_response'];assert response==dict(finding=pin(PRIOR_REVIEW,'/findings/0'),finding_id='F199-01',
        status='REPAIR_PREPARED_PENDING_DOCUMENTARY_REVIEW',historical_I200_finding_record_unchanged=True,
        revised_row_ids=[POLICY,APPROVAL],table_revision_path=DOC,source_checks_per_phase=True,independent_review_or_accepted_closure=False)
    ready=copy.deepcopy(old['missing_facts_and_readiness'])
    ready['revised_requirement_inventory']=dict(prior_CE02_requirement_rows=9,deferred_CE10_requirement_rows=1,
        total_unaccepted_rows=10,missing_future_bundle_approval_is_not_CE02_gate=True,genuine_prior_anchor_acceptance_remains_missing=True,
        actual_CE10_dossier_created=False)
    assert d['missing_facts_and_readiness']==ready
    assert d['historical_scope']==dict(plan_and_prior_bytes_preserved=True,I193_saved_CE02_candidate_dossier_created=False,
        original_CE02_dossier_remains_published=True,current_candidate_revision_path=DOS,original_CE01_and_candidate_02_preserved=True,
        other10_planned_dossiers_created=False,actual_accepted_steps=0,no_accepted_step_or_live_binding_transition=True,
        predecessor_replay='Reproduce immutable I200 reconstruction/review and I199 preparation against original sources. I199 alone projects original CE02 presence to its Git-proven absent base; its nested CE01 guard stays original. This candidate02 is checked at its real new path. No predecessor or historical finding is rewritten.')
    effect={**old['current_effect'],'CE02_candidate_02_prepared':True,'F199_01_documentary_repair_prepared':True,
        'F199_01_accepted_closure':False,'CE02_documentary_confirmation':False}
    assert d['current_effect']==effect and not d['dependency_gate']['actual_dependency_satisfied']
    graph={s['id']:s['depends_on'] for s in plan['steps']};assert previous['dependency_cycle'](graph) is None
    assert rd(SPEC)['record_order']['ANCHOR']==[] and 'ANCHOR' in rd(SPEC)['record_order']['BUNDLE']
    assert (ROOT/OLD).exists() and (ROOT/DOS).exists() and git('ls-tree','--name-only',BASE,'--',DOS)==''
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][2:])
    assert set(d['work_unit']['rollback_files'])==FILES and d['work_unit']['verification_command']=='python3 docs/validation/D5-I201-audit.py'
    assert d['work_unit']['expected_result']=='PASS_STATIC_SOURCE_ONLY_REPAIR_PREPARED_EVIDENCE_MISSING'
    return dict(schema='d5.i201-preparation-review.v1',increment='I201',date='2026-11-16',base_commit=BASE,
        dossier=pin(DOS),input_pins=pins,status='CE02_CANDIDATE_02_REPAIR_PREPARED_PENDING_REVIEW_EVIDENCE_MISSING',
        provenance=dict(preparer='Same Codex assistant/chat',actor_independent=False,organizationally_independent=False,
            independent_acceptance=False,competent_R01_R02_R08_acceptance=False),
        historical_reconstruction=dict(I200_reconstruction_and_review_reproduced=True,I199_original_dossier_preserved=True,
            I200_open_finding_preserved=True,prior_publication_mains_run=False,current_revision_checked_at_real_path=True,
            other_planned_dossiers_absent=10),
        revision_coverage=dict(changed_top_level_fields=sorted(changed),unchanged_requirement_rows=8,requirement_rows=10,
            CE02_prior_requirement_rows=9,CE10_deferred_requirement_rows=1,all_rows_missing_and_unaccepted=True,
            phase_checks=scope,documentary_rejection_checks=negative,I193_dependency_graph_acyclic=True,
            source_ANCHOR_precedes_BUNDLE=True,schema_caps_role_policy_and_negative_gates_unchanged=True),
        finding_disposition=dict(id='F199-01',repair_prepared=True,documentary_confirmation=False,accepted_closure=False,
            next_scope='Review exact CE02 candidate02; genuine external authority/evidence and competent CE01/CE02 acceptance remain absent.'),
        limitations=['Documentary phase split and separated missing-value slots only; no actual anchor, body, key, signature, core/C or acceptance.',
            'Seven rejection checks mutate in-memory documentary data only, not product/components or active schemas.',
            'No provider contact, keys/enrollment, crypto/codec, image/runtime/probe, product/components, claim/worker, quota, active binding or authority action.'],
        current_effect=effect,decision=d['decision'],E06=d['E06'])


def main():
    assert rd(PREP)==build_review()
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published489'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==494
    seal=rd(SEAL);assert seal['schema']=='d5.i201-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published494']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['F199_01_repair_prepared'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['F199_01_accepted_closure','CE02_accepted','actual_anchor_registry_created','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY_REPAIR_PREPARED_EVIDENCE_MISSING',increment='I201',
        F199_01_repair_prepared=True,F199_01_accepted_closure=False,CE02_accepted=False,actual_anchor_registry_created=False,
        historical_pins=802,prior_published_files_preserved=494,new_files=5,documentary_rejection_checks=7,
        actual_evidence_accepted=0,independent_acceptance=False,product_or_components_executed=0,quotas_changed=False,
        rebind_applied=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
