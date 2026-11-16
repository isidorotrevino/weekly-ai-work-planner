#!/usr/bin/env python3
"""I197: documentary CE01 revision only; no product/components or runtime work."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='0885ea863a46c66b12b473ba63ee0f8389effdd4'
OLD=P+'D5-I193-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE.json'
DOS=P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
PRIOR_REVIEW=P+'D5-I196-I195-documentary-review.json'
PRIOR_RECON=P+'D5-I196-I195-source-reconstruction.json'
PRIOR_AUDIT=P+'D5-I196-audit.py';PRIOR_SEAL=P+'D5-I196-integrity.json'
PRIOR_DOC='docs/design/D5-I196-I195-CE01-REVIEW.md'
PRIOR_FILES={PRIOR_REVIEW,PRIOR_RECON,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
AUDIT=P+'D5-I197-audit.py';PREP=P+'D5-I197-preparation-review.json'
SEAL=P+'D5-I197-integrity.json';DOC='docs/design/D5-I197-CE01-SCOPE-DECISION-BOUNDARY-02.md'
FILES={DOS,AUDIT,PREP,SEAL,DOC}
HANDOFF='X09-PRELAUNCH-HANDOFF';FINAL='X09-FINAL-PREREQUISITES'


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pin(p,q=''):return dict(path=p,sha256=sha(p),json_pointer=q)


def check_git_pins(pins):
    request=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=request))
    for p,h in sorted(pins.items()):
        header=stream.readline().decode().split();assert len(header)==3 and header[1]=='blob',p
        body=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    assert stream.read()==b''


def check_step_obligations(rows,boundary,plan,finding):
    """Check what each step requires, rather than accept aggregate step coverage."""
    by_id={r['id']:r for r in rows};assert len(by_id)==len(rows)==11 and 'X09' not in by_id
    handoff=by_id[HANDOFF];final=by_id[FINAL];receipt=by_id['X10']
    proposals=finding['repair_proposal_not_applied']
    assert handoff['downstream_steps']==['CE11'] and final['downstream_steps']==['CE12']
    assert receipt['downstream_steps']==['CE12']
    assert handoff['requirement_kind']=='DOCUMENTARY_HANDOFF_OF_PENDING_FINAL_ROUTE'
    assert 'required_actual_evidence' not in handoff
    assert handoff['required_documentary_handoff']==proposals[0]['requirement']
    assert handoff['responsible_review_roles']==['R06','R08']
    assert handoff['requires_actual_final_route_completion'] is False
    assert handoff['requires_CE12_receipt_claim_or_spawn'] is False
    assert handoff['preserves_actual_CE01_CE10_custody_evidence'] is True
    assert final['requirement_kind']=='ACTUAL_FINAL_EVIDENCE_BEFORE_AUTHORIZED_CLAIM'
    assert 'required_documentary_handoff' not in final
    assert final['required_actual_evidence']==proposals[1]['requirement']
    assert final['responsible_review_roles']==['R04','R05','R07','R08']
    prerequisites=plan['closure_boundaries']['external_prerequisites_for_receipt']
    assert len(prerequisites)==5 and final['external_prerequisites']==prerequisites
    assert final['preclaim_external_prerequisites']==prerequisites[:4]
    assert final['receipt_only_external_prerequisites']==prerequisites[4:]==['ACTUAL_ATOMIC_ONE_USE_CLAIM_AND_PROTECTED_CONSTRUCTION']
    assert final['handoff_performs_or_satisfies_prerequisites'] is False
    assert final['current_execution_or_issuance_authorized'] is False
    a=boundary['CE11'];b=boundary['CE12']
    assert a['plan_source']==pin(PLAN,'/steps/10') and a['handoff_row']==HANDOFF
    assert a['required_actual_custody_step_ids']==plan['steps'][10]['depends_on']==['CE%02d'%i for i in range(1,11)]
    assert a['final_route_obligations_to_handoff']==prerequisites
    for k in ['actual_final_route_completion_required','CE12_receipt_claim_or_spawn_required','accepted']:assert a[k] is False
    assert a['no_execution_gate_release'] is True
    assert b['plan_source']==pin(PLAN,'/closure_boundaries') and b['final_prerequisite_row']==FINAL and b['actual_receipt_row']=='X10'
    assert b['external_prerequisites']==prerequisites
    assert b['preclaim_external_prerequisites']==prerequisites[:4] and b['receipt_only_external_prerequisites']==prerequisites[4:]
    for k in ['preclaim_prerequisites_must_be_genuinely_satisfied_before_claim','all_external_prerequisites_must_be_genuinely_satisfied_before_receipt','claim_is_not_its_own_precondition']:assert b[k] is True
    for k in ['documentary_handoff_satisfies_prerequisites','currently_authorized','accepted']:assert b[k] is False
    assert plan['closure_boundaries']['prelaunch_depends_on_receipt'] is False
    for r in rows:
        for k in ['actual_provider_identity','actual_provider_locator','actual_body_sha256','actual_body_bytes','actual_appointment']:assert r[k] is None
        assert r['availability']=='NOT_SUPPLIED_IN_THIS_SCOPE' and r['accepted'] is False and r['contact_authorized_now'] is False
    return dict(CE11_handoff_only=True,actual_CE01_CE10_prerequisites_preserved=True,
        CE11_requires_no_actual_final_route_or_CE12_receipt_claim_spawn=True,
        CE12_receipt_external_prerequisites_preserved=5,CE12_preclaim_external_prerequisites=4,
        claim_is_not_its_own_precondition=True,CE12_receipt_deferred_and_unauthorized=True,
        handoff_is_not_actual_evidence_or_admission=True)


def rejection_checks(rows,boundary,plan,finding):
    """In-memory counterexamples to documentary validation, never runtime components."""
    results=[]
    for case in ['FINAL_ROW_ASSIGNED_TO_CE11','HANDOFF_REQUIRES_ACTUAL_FINAL_EVIDENCE',
                 'FINAL_PREREQUISITE_DROPPED','CE01_CE10_PREREQUISITE_DROPPED','CE12_AUTHORIZED_BY_HANDOFF',
                 'CLAIM_AS_OWN_PRECONDITION']:
        altered=copy.deepcopy(rows);scope=copy.deepcopy(boundary)
        if case=='FINAL_ROW_ASSIGNED_TO_CE11':altered[9]['downstream_steps']=['CE11','CE12']
        elif case=='HANDOFF_REQUIRES_ACTUAL_FINAL_EVIDENCE':altered[8]['required_actual_evidence']='Actual final route complete'
        elif case=='FINAL_PREREQUISITE_DROPPED':altered[9]['external_prerequisites'].pop()
        elif case=='CE01_CE10_PREREQUISITE_DROPPED':scope['CE11']['required_actual_custody_step_ids'].pop()
        elif case=='CE12_AUTHORIZED_BY_HANDOFF':scope['CE12']['currently_authorized']=True
        else:scope['CE12']['preclaim_external_prerequisites'].append('ACTUAL_ATOMIC_ONE_USE_CLAIM_AND_PROTECTED_CONSTRUCTION')
        try:check_step_obligations(altered,scope,plan,finding)
        except AssertionError:results.append(dict(case=case,result='REJECTED_DOCUMENTARY_SCOPE_MUTATION'))
        else:raise AssertionError(case+' unexpectedly accepted')
    return results


def build_review():
    d=rd(DOS);old=rd(OLD);plan=rd(PLAN);prior_review=rd(PRIOR_REVIEW);finding=prior_review['findings'][0]
    pins={**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==782 and d['input_pins']==pins;check_git_pins(pins)
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));rec=previous['reconstruct']()
    assert rec==rd(PRIOR_RECON) and previous['build_review'](rec)==prior_review
    assert finding['id']=='F195-01' and finding['status']=='OPEN_DOCUMENTARY_REVISION_REQUIRED'
    assert d['schema']=='d5.i197-ce01-scope-decision-boundary-candidate-02.v1' and d['base_commit']==BASE
    assert d['increment']=='I197' and d['candidate_id']=='CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02'
    assert d['status']=='CE01_DOCUMENTARY_CANDIDATE_02_PREPARED_NOT_ADOPTED_NOT_ACCEPTED_NOT_ADMITTED'
    allowed_changes={'schema','increment','base_commit','candidate_id','status','input_pins','revision_binding',
        'external_evidence_requirements','step_obligation_boundary','finding_response','historical_scope',
        'work_unit','permission_matrix','current_effect','missing_facts_and_readiness'}
    actual_changes={k for k in set(old)|set(d) if old.get(k)!=d.get(k)}
    assert actual_changes==allowed_changes,actual_changes
    for k in set(old)-allowed_changes:assert d[k]==old[k],k
    assert d['revision_binding']==dict(supersedes_documentary_candidate=pin(OLD),source_review=pin(PRIOR_REVIEW,'/findings/0'),
        finding_id='F195-01',historical_I193_planned_path=OLD,current_candidate_path=DOS,active_binding_changed=False)
    rows=d['external_evidence_requirements'];oldrows=old['external_evidence_requirements']
    assert rows[:8]==oldrows[:8] and rows[10:]==oldrows[9:] and len(oldrows)==10
    scope=check_step_obligations(rows,d['step_obligation_boundary'],plan,finding)
    negative=rejection_checks(rows,d['step_obligation_boundary'],plan,finding)
    response=d['finding_response']
    assert response==dict(finding=pin(PRIOR_REVIEW,'/findings/0'),finding_id='F195-01',
        status='REPAIR_PREPARED_PENDING_DOCUMENTARY_REVIEW',historical_I196_finding_record_unchanged=True,
        revised_row_ids=[HANDOFF,FINAL],table_revision_path=DOC,source_checks_per_step=True,independent_review_or_accepted_closure=False)
    assert len(d['permission_matrix'])==len(old['permission_matrix'])==18
    for r,s in zip(d['permission_matrix'],old['permission_matrix']):
        assert {k:v for k,v in r.items() if k!='basis'}=={k:v for k,v in s.items() if k!='basis'}
        if r['authorized_now']:assert r['basis']=='Current explicit I197 request; prepare, audit and publish this documentary revision only.'
        else:assert r['basis']==s['basis']
    effect={**old['current_effect'], 'CE01_candidate_02_prepared':True,'F195_01_documentary_repair_prepared':True,
        'F195_01_accepted_closure':False,'CE01_documentary_confirmation':False}
    assert d['current_effect']==effect
    ready=copy.deepcopy(old['missing_facts_and_readiness'])
    ready['missing'][1]='Actual external provider/authority identities and authentic evidence locations/bodies for X01-X08, X09-FINAL-PREREQUISITES and X10; the separately required CE11 handoff packet is also not supplied.'
    ready['revised_requirement_inventory']=dict(actual_external_requirement_rows=10,documentary_handoff_rows=1,total_unaccepted_rows=11,actual_CE11_handoff_packet_created=False)
    assert d['missing_facts_and_readiness']==ready
    assert d['historical_scope']==dict(plan_and_review_records_preserved=True,I193_plan_saved_candidate_dossier_created_value=False,
        I193_plan_state_is_historical_and_unchanged=True,original_CE01_dossier_remains_published=True,
        current_candidate_revision_path=DOS,other11_dossiers_created=False,no_accepted_step_or_live_binding_transition=True,
        replay_method='Reproduce the immutable I196 reconstruction and I195 preparation against their original sources. I195 alone projects the original CE01 historical presence query to its Git-proven absent base, then restores it. This candidate02 is checked at its real new path; no predecessor body or historical finding is rewritten.')
    assert (ROOT/OLD).exists() and (ROOT/DOS).exists() and git('ls-tree','--name-only',BASE,'--',DOS)==''
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][1:])
    assert set(d['work_unit']['rollback_files'])==FILES and d['work_unit']['verification_command']=='python3 docs/validation/D5-I197-audit.py'
    assert d['work_unit']['expected_result']=='PASS_STATIC_SOURCE_ONLY_REPAIR_PREPARED_PENDING_REVIEW'
    return dict(schema='d5.i197-preparation-review.v1',increment='I197',date='2026-11-16',base_commit=BASE,
        dossier=pin(DOS),input_pins=pins,status='CE01_CANDIDATE_02_REPAIR_PREPARED_PENDING_REVIEW',
        provenance=dict(preparer='Same Codex assistant/chat',actor_independent=False,organizationally_independent=False,
            independent_acceptance=False,competent_R06_or_R08_acceptance=False),
        historical_reconstruction=dict(I196_source_reconstruction_and_review_reproduced=True,
            I195_original_dossier_preserved=True,I196_open_finding_preserved=True,
            prior_publication_mains_run=False,current_revision_checked_at_real_path=True,other_dossiers_absent=11),
        revision_coverage=dict(changed_top_level_fields=sorted(actual_changes),unchanged_external_rows=9,
            requirement_rows=11,actual_external_requirement_rows=10,documentary_handoff_rows=1,
            all_rows_unaccepted=True,step_obligation_checks=scope,documentary_negative_checks=negative,
            S01_exclusions_preserved=8,extra_custody_separations_preserved=4,full_CP07_conditions_preserved=9,
            role_matrix_caps_numeric_candidates_and_negative_gates_unchanged=True),
        finding_disposition=dict(id='F195-01',repair_prepared=True,documentary_confirmation=False,accepted_closure=False,
            next_scope='Review exact candidate02 before documentary confirmation; genuine competent R06/R08 adoption still absent.'),
        limitations=['Documentary obligation split only; no actual provider, actor appointment, evidence, final-route completion, runtime or resource proof.',
            'Six negative checks mutate only in-memory documentary data, not product/components or active schemas.',
            'No contact, enrollment, keys, crypto, image/build/probe, product/components, claim/worker, quota, active binding or authority action.'],
        current_effect=effect,decision=d['decision'],E06=d['E06'])


def main():
    assert rd(PREP)==build_review()
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published469'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==474
    seal=rd(SEAL);assert seal['schema']=='d5.i197-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published474']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['F195_01_repair_prepared'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['F195_01_accepted_closure','CE01_accepted','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY_REPAIR_PREPARED_PENDING_REVIEW',increment='I197',
        F195_01_repair_prepared=True,F195_01_accepted_closure=False,CE01_accepted=False,historical_pins=782,
        prior_published_files_preserved=474,new_files=5,requirement_rows=11,documentary_rejection_checks=6,
        actual_evidence_accepted=0,independent_acceptance=False,product_or_components_executed=0,quotas_changed=False,
        rebind_applied=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
