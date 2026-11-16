#!/usr/bin/env python3
"""I196: source/JSON/Git documentary review; never run product or components."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
BASE='05876a14c9e3e614df9581a991b9c76140a96161'
DOS=P+'D5-I193-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE.json'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
CHECK=P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
S01=P+'D5-I179-S01-ROLES-SCOPE-GATES.json'
CERT=P+'D5-I122-CAPACITY-CERTIFICATE.json'
PRIOR_AUDIT=P+'D5-I195-audit.py'
PRIOR_PREP=P+'D5-I195-preparation-review.json'
PRIOR_SEAL=P+'D5-I195-integrity.json'
PRIOR_DOC='docs/design/D5-I195-CE01-SCOPE-DECISION-BOUNDARY.md'
PRIOR_FILES={DOS,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON=P+'D5-I196-I195-source-reconstruction.json'
REVIEW=P+'D5-I196-I195-documentary-review.json'
AUDIT=P+'D5-I196-audit.py'
SEAL=P+'D5-I196-integrity.json'
DOC='docs/design/D5-I196-I195-CE01-REVIEW.md'
FILES={RECON,REVIEW,AUDIT,SEAL,DOC}


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pin(p,q=''):return dict(path=p,sha256=sha(p),json_pointer=q)


def git_blob_pins(pins):
    request=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=request))
    for p,h in sorted(pins.items()):
        header=stream.readline().decode().split()
        assert len(header)==3 and header[1]=='blob',p
        body=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    assert stream.read()==b''


def replay_guard_review(previous,other):
    """Exercise only the documentary presence guard, including exception restoration."""
    old_base=previous['BASE'];target=ROOT/DOS;other_path=ROOT/other
    assert git('ls-tree','--name-only',old_base,'--',DOS)==''
    assert git('ls-tree','--name-only',BASE,'--',DOS)==DOS
    original=Path.exists
    assert target.exists() and not other_path.exists()
    with previous['predecessor_presence_as_of_base']():
        assert not target.exists() and not other_path.exists() and (ROOT/PLAN).exists()
    assert Path.exists is original and target.exists()
    class ExpectedDocumentaryProbe(Exception):pass
    try:
        with previous['predecessor_presence_as_of_base']():
            assert not target.exists()
            raise ExpectedDocumentaryProbe()
    except ExpectedDocumentaryProbe:pass
    else:raise AssertionError('Documentary failure probe was not raised')
    assert Path.exists is original and target.exists() and not other_path.exists()
    return dict(base_absence_verified=True,published_I195_presence_verified=True,
        exact_CE01_query_only=True,unrelated_existing_and_missing_paths_unchanged=True,
        restored_after_success=True,restored_after_exception=True,
        prior_publication_main_run=False,product_or_component_run=False)


def reconstruct():
    d=rd(DOS);plan=rd(PLAN);spec=rd(SPEC);steps={s['id']:s for s in plan['steps']}
    pins={**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==777;git_blob_pins(pins)
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT))
    assert previous['build_review']()==rd(PRIOR_PREP)
    guard=replay_guard_review(previous,steps['CE02']['candidate_dossier_path'])
    step=steps['CE01'];assert step['candidate_dossier_path']==DOS and not step['accepted']
    assert step['record_families']==[] and step['depends_on']==[]
    assert d['required_evidence']==step['required_evidence'] and len(d['required_evidence'])==3
    assert d['planned_acceptance_checks']==step['acceptance_checks'] and len(step['acceptance_checks'])==2
    assert d['contract_rules']==step['contract_rules']==['K01','K10','K12','K15','K16']
    inventory={r['path']:r for r in d['documentary_inventory']};assert len(inventory)==14
    for b in plan['bindings'].values():
        assert b['path'] in inventory and inventory[b['path']]['sha256']==b['sha256']==sha(b['path'])
    for r in inventory.values():
        assert r['sha256']==sha(r['path']) and r['serialized_file_bytes']==(ROOT/r['path']).stat().st_size
        assert r['availability']=='EXISTING_DOCUMENTARY_BYTES_PINNED_NOT_ACTUAL_EXTERNAL_EVIDENCE'
    source_roles=rd(S01)['role_authority_validity_matrix'];roles=d['role_scope_matrix']
    assert len(roles)==8 and [r['id'] for r in roles]==[r['id'] for r in source_roles]
    pairs=[]
    for r,s in zip(roles,source_roles):
        for k in ['role','required_decision_scopes','separation_required_from']:assert r[k]==s[k]
        pairs.extend((r['id'],x) for x in r['separation_required_from'])
        for k in ['assigned_person','canonical_actor_id','appointment_or_authority_record','competence_evidence','key_or_trust_binding','validity']:assert r[k] is None
        assert not r['accepted_appointment'] and r['current_actions_authorized']==[]
    inherited=d['inherited_scope_boundaries']
    exclusions=spec['inheritance']['S01_actor_exclusions']
    assert set(pairs)=={(r['role'],r['excluded_subject']) for r in exclusions} and len(pairs)==8
    assert inherited['S01_exclusions']==exclusions
    assert inherited['extra_custody_separation']==spec['inheritance']['extra_custody_separation']
    assert len(inherited['extra_custody_separation'])==4
    assert inherited['full_CP07_conditions']==spec['inheritance']['existing_full_CP07_conditions']
    assert len(inherited['full_CP07_conditions'])==9
    # Derive permitted actions separately rather than infer authority from an assigned role.
    permission={r['action']:r['authorized_now'] for r in d['permission_matrix']}
    assert len(permission)==18
    permitted={a for a,v in permission.items() if v}
    assert permitted=={'READ_REPOSITORY_DOCUMENTARY_SOURCE_AND_GIT_HASHES','PREPARE_THIS_CE01_DOCUMENTARY_DOSSIER',
        'RUN_THIS_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_REVIEWABLE_DOCUMENTARY_UNIT'}
    assert all(not r['grants_execution_or_custody'] for r in d['permission_matrix'])
    denied=sorted(set(permission)-permitted);assert len(denied)==14
    external=d['external_evidence_requirements'];assert len(external)==10
    for r in external:
        for k in ['actual_provider_identity','actual_provider_locator','actual_body_sha256','actual_body_bytes','actual_appointment']:assert r[k] is None
        assert not r['accepted'] and not r['contact_authorized_now']
    x09=external[8];assert x09['id']=='X09' and x09['downstream_steps']==['CE11','CE12']
    assert x09['required_actual_evidence']=='Future separately authorized real final E06/payload/Q/root/signatures and full admission; no run command or current issue.'
    ce11=steps['CE11']
    assert ce11['required_evidence'][2]=='Explicit handoff to existing final E06/payload/Q/root/admission work, with no current run command or authority; pending actual source/component/evidence work remains visible.'
    assert 'CE12' not in ce11['depends_on'] and plan['closure_boundaries']['prelaunch_depends_on_receipt'] is False
    assert external[9]['id']=='X10' and external[9]['downstream_steps']==['CE12']
    assert inherited['CE11_prelaunch_depends_on_CE12'] is False and inherited['receipt_authorized_now'] is False
    assert 'full admission' in x09['required_actual_evidence']
    # Detect an ambiguous step/obligation association, not an actual execution/cycle.
    ambiguity=dict(id='F195-01',row_id='X09',actual_downstream_steps=x09['downstream_steps'],
        unsplit_actual_evidence_requirement=x09['required_actual_evidence'],
        planned_CE11_handoff=ce11['required_evidence'][2],
        planned_CE11_boundary=ce11['authorization_boundary'],
        explicit_CE11_vs_CE12_requirement_split_present=False,
        documentary_row_ambiguous=True,actual_cycle_or_execution_observed=False)
    cert=rd(CERT)
    gates={r['id']:r['observed_value'] for r in d['preserved_negative_gates']}
    assert gates=={k:cert[k] for k in ['status','CP03_global_resolved','CP07_exact_admission_resolved','correlated_atomicity_verified','component_validation']}
    assert gates==dict(status='IMPLEMENTED_NOT_ADMITTED',CP03_global_resolved=True,
        CP07_exact_admission_resolved=False,correlated_atomicity_verified=False,component_validation='NOT_RUN')
    availability=d['source_image_record_availability']
    assert len(availability['successor_sources'])==6 and len(availability['I191_record_families'])==8
    for r in availability['successor_sources']:assert not (ROOT/r['path']).exists() and r['actual_sha256'] is None and not r['accepted']
    for r in availability['I191_record_families']:assert not r['body_available'] and not r['accepted']
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for i,s in steps.items() if i!='CE01')
    assert d['review_dispositions']['primary_R06']['decision']=='PENDING_NOT_ACCEPTED'
    assert d['review_dispositions']['separate_R08']['decision']=='PENDING_NOT_ACCEPTED'
    assert d['producer']['actor_independent'] is False and d['producer']['independent_acceptance'] is False
    assert all(not r['adopted'] for r in d['decision_proposals']) and len(d['decision_proposals'])==8
    assert d['current_effect']['CE01_accepted'] is False and d['decision']==plan['decision'] and d['E06']==plan['E06']
    return dict(schema='d5.i196-i195-source-reconstruction.v1',increment='I196',date='2026-11-16',base_commit=BASE,
        input_pins=pins,method='Fresh Git blobs and reverse source-to-CE01 coverage, independently reconstructed role exclusions and permission partition; predecessor documentary build reproduced without publication main.',
        historical_replay_guard=guard,
        coverage=dict(required_evidence_items=3,planned_acceptance_checks=2,authorization_boundaries=1,contract_rules=step['contract_rules'],
            documentary_inputs=14,unassigned_roles=8,S01_exclusions=8,extra_custody_separations=4,
            allowed_documentary_actions=sorted(permitted),denied_actions=denied,unadopted_decisions=8,
            missing_external_evidence_groups=10,missing_successor_sources=6,missing_record_families=8,
            other_dossiers_absent=11,actual_evidence_accepted=0),
        boundary_ambiguity=ambiguity,preserved_I122_gates=gates,
        authority_scope=dict(CP03_only_inherited_I122_scope=True,successor_resource_capacity_or_service_verified=False,
            no_competent_adoption_or_acceptance=True,no_contact_or_runtime_authorized=True),
        verdict=dict(new_blocking_documentary_findings=1,documentary_confirmation=False,revision_required=True,
            adopted=False,implemented=False,independent_acceptance=False,CE01_accepted=False,
            actual_evidence_accepted=0,resource_obligations_closed=0,product_or_components_executed=0))


def build_review(rec):
    d=rd(DOS);plan=rd(PLAN)
    finding=dict(id='F195-01',priority='P2',status='OPEN_DOCUMENTARY_REVISION_REQUIRED',blocks_documentary_confirmation=True,
        title='Separate CE11 documentary handoff from actual final evidence required before CE12',
        evidence=[pin(DOS,'/external_evidence_requirements/8'),pin(PRIOR_DOC),pin(PLAN,'/steps/10/required_evidence/2'),
                  pin(PLAN,'/steps/10/authorization_boundary'),pin(PLAN,'/closure_boundaries')],
        observed=rec['boundary_ambiguity'],
        impact='X09 associates one unsplit actual final E06/payload/Q/root/signatures/full-admission requirement with both CE11 and CE12. This leaves unclear whether actual final work must precede custody-only CE11, while I193 calls for an explicit handoff to that still-pending final route. No actual cycle, execution or admission is inferred.',
        requested_revision='Split X09 into a CE11 documentary handoff describing pending final prerequisites and a CE12 actual-final-evidence prerequisite. Update the I195 table and source-level audit of each step-specific obligation, preserving all gates and the no-receipt CE11 boundary.',
        repair_proposal_not_applied=[
            dict(proposed_id='X09-PRELAUNCH-HANDOFF',downstream_steps=['CE11'],kind='DOCUMENTARY_HANDOFF_OF_PENDING_FINAL_ROUTE',
                requirement='Enumerate pending final E06/payload/Q/root/admission obligations and responsible review scopes. Actual completion of that final route is not a new CE11 custody-only acceptance prerequisite; all genuine CE01-CE10 facts/reviews still required.',
                review_roles=['R06','R08'],current_execution_or_contact_authorized=False),
            dict(proposed_id='X09-FINAL-PREREQUISITES',downstream_steps=['CE12'],kind='ACTUAL_FINAL_EVIDENCE_BEFORE_AUTHORIZED_CLAIM',
                requirement='Actual final E06/payload/Q/trusted root/signatures and full root admission must exist before any separately authorized actual claim/construction/receipt. No current execution, issuance, evidence or acceptance is created.',
                review_roles=['R04','R05','R07','R08'],current_execution_or_contact_authorized=False)],
        completion_checks=['No X09 actual-final evidence requirement is assigned to CE11; its final-route handoff remains explicit.',
            'CE12 still requires every external prerequisite in I193 closure_boundaries; CE11 never requires CE12 receipt/claim/spawn.',
            'Check per-step obligation meanings, not just union coverage of CE01-CE12; keep all roles/providers/evidence missing and unaccepted.'],
        source_candidate_modified=False,competent_adoption=False)
    # Each requirement/rule is assessed at documentary scope; none is an actual evidence PASS.
    rows=[
        ('E01','I193 required_evidence[0]','Exact I191/I192/profile/protocol/output/transport inventory and inherited gates','CONSISTENT_PINNED_DOCUMENTARY_SOURCES'),
        ('E02','I193 required_evidence[1]','Producer, eight role scopes and permissions; no actual person/appointment','CONSISTENT_UNASSIGNED_ROLE_BOUNDARY'),
        ('E03','I193 required_evidence[2]','X01-X10 describe required providers/evidence honestly as missing','PARTIAL_X09_STEP_BOUNDARY_NEEDS_REVISION'),
        ('A01','I193 acceptance_checks[0]','Four documentary actions and14 denied classes; no execution/build/enrollment/signing/claim/contact','CONSISTENT_CURRENT_PERMISSION_SCOPE'),
        ('A02','I193 acceptance_checks[1]','S01/F183-01/eight exclusions and custody-only boundary retained','CONSISTENT_DECLARED_EXCLUSIONS_NOT_ACTUAL_INDEPENDENCE'),
        ('B01','I193 authorization_boundary','No signed policy/role acceptance; competent R06/R08 still absent','CONSISTENT_NO_COMPETENT_ADOPTION'),
        ('K01','I191 K01','External preaccepted anchors expected; no provider/key selected','CONSISTENT_REQUIREMENT_NOT_TRUST_PROOF'),
        ('K10','I191 K10','All eight exclusions and four additional actor/key separations','CONSISTENT_ROLE_POLICY_NOT_APPOINTMENTS'),
        ('K12','I191 K12 / I193 CE11-CE12','Antecedent custody/final route/claim order needs unambiguous X09 mapping','PARTIAL_F195_01_NO_ACTUAL_CYCLE_OBSERVED'),
        ('K15','I191 K15','Per-attempt/native/IO/verification work remains in full resources; no extra Reader inputs/free offline work','CONSISTENT_INHERITED_OBLIGATION_NOT_COST_PROOF'),
        ('K16','I191 K16','Caps/layouts/candidate numbers unchanged; no invented identity/body/authority','CONSISTENT_DESIGN_LIMITS_NOT_ACTUAL_FIT')]
    effect={**d['current_effect'], 'CE01_documentary_review_completed':True,
        'CE01_documentary_confirmation':False,'CE01_documentary_revision_required':True}
    return dict(schema='d5.i196-i195-documentary-review.v1',increment='I196',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        proposal=d['proposal_id'],profile_id=d['profile_id'],step='CE01',
        status='CE01_DOCUMENTARY_REVIEW_REVISION_REQUIRED_NOT_ADOPTED_NOT_ACCEPTED_NOT_ADMITTED',
        reconstruction=pin(RECON),
        provenance=dict(reviewer='Same Codex assistant/chat that prepared I195 and earlier candidates',
            methodological_reconstruction_separate=True,actor_independent=False,organizationally_independent=False,
            independent_acceptance=False,competent_R06_review=False,separate_R08_acceptance=False),
        findings=[finding],checks=[dict(id=i,source=s,scope=t,result=r) for i,s,t,r in rows],
        clarification=['The missing genuine providers/appointments/records/resources are disclosed external prerequisites, not invented new documentary defects.',
            'I195 candidate readiness is its historical self-disposition. I196 requires a documentary revision and does not mutate that source or accept CE01.',
            'K15 remains fully binding through pinned I191: actual launch lookup/freshness/verification/copies/native/IO/receipt work is not free or moved outside t0 by this review.',
            'The I195 historical exact-path presence projection is transparent, Git-proven and restored after success/failure; current CE01 presence and all bytes are verified normally.'],
        verdict=rec['verdict'],current_effect=effect,decision=plan['decision'],E06=plan['E06'],
        next_scope='Prepare a separately requested documentary revision separating X09 CE11 handoff from CE12 actual final prerequisites; review that exact revision before documentary confirmation. Genuine competent R06/R08 adoption remains independently missing.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I196-audit.py',
            expected_result='PASS_STATIC_SOURCE_ONLY_WITH_OPEN_FINDING_F195_01',
            runtime_harness='N/A: documentary source/preservation review; no product/components/crypto/image/claim/protocol run.',
            over400_lines=True,reason='One review unit with source reconstruction, precise finding, requirement coverage and preservation evidence; overage reported.'),
        publication=dict(commit_and_push_requested=True,publication_not_adoption_acceptance_or_authority=True))


def main():
    rec=reconstruct();assert rd(RECON)==rec and rd(REVIEW)==build_review(rec)
    prior=rd(PRIOR_SEAL)
    preserved={**prior['preserved_published464'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==469
    seal=rd(SEAL);assert seal['schema']=='d5.i196-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published469']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['open_documentary_findings']==['F195-01']
    assert seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['CE01_accepted','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY_WITH_OPEN_FINDING_F195_01',increment='I196',
        documentary_confirmation=False,new_blocking_documentary_findings=1,CE01_accepted=False,
        historical_pins=777,prior_published_files_preserved=469,new_files=5,actual_evidence_accepted=0,
        independent_acceptance=False,product_or_components_executed=0,quotas_changed=False,rebind_applied=False,
        resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
