#!/usr/bin/env python3
"""I198 documentary CE01 review: JSON/Git/partial-order math only, no components."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='21bee3e8629e5cd204603648419870feb14b7645'
DOS=P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
OLD=P+'D5-I193-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE.json'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
FINDING=P+'D5-I196-I195-documentary-review.json'
PRIOR_PREP=P+'D5-I197-preparation-review.json'
PRIOR_AUDIT=P+'D5-I197-audit.py';PRIOR_SEAL=P+'D5-I197-integrity.json'
PRIOR_DOC='docs/design/D5-I197-CE01-SCOPE-DECISION-BOUNDARY-02.md'
PRIOR_FILES={DOS,PRIOR_PREP,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON=P+'D5-I198-I197-source-reconstruction.json'
REVIEW=P+'D5-I198-I197-documentary-review.json'
AUDIT=P+'D5-I198-audit.py';SEAL=P+'D5-I198-integrity.json'
DOC='docs/design/D5-I198-I197-CE01-02-REVIEW.md'
FILES={RECON,REVIEW,AUDIT,SEAL,DOC}
HANDOFF='X09-PRELAUNCH-HANDOFF';FINAL='X09-FINAL-PREREQUISITES'


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


def ancestors_for(graph):
    """DFS over documentary dependency labels; not a protocol or runtime simulation."""
    completed=set();active=set();closures={}
    def visit(node):
        assert node in graph and node not in active,node
        if node in completed:return closures[node]
        active.add(node);found=set()
        for parent in graph[node]:found.add(parent);found.update(visit(parent))
        active.remove(node);completed.add(node);closures[node]=found
        assert node not in found
        return found
    for node in sorted(graph):visit(node)
    return closures


def reconstruct():
    d=rd(DOS);old=rd(OLD);plan=rd(PLAN);spec=rd(SPEC)
    pins={**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==787;verify_git_blobs(pins)
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT))
    prior=previous['build_review']();assert prior==rd(PRIOR_PREP)
    finding=rd(FINDING)['findings'][0];assert finding['id']=='F195-01'
    assert finding['status']=='OPEN_DOCUMENTARY_REVISION_REQUIRED'
    rows=d['external_evidence_requirements'];by_id={r['id']:r for r in rows}
    assert len(by_id)==len(rows)==11 and 'X09' not in by_id
    assert rows[:8]==old['external_evidence_requirements'][:8]
    assert rows[10:]==old['external_evidence_requirements'][9:]
    mapping={s['id']:[] for s in plan['steps']}
    for r in rows:
        for step in r['downstream_steps']:mapping[step].append(r['id'])
        field='required_documentary_handoff' if r['id']==HANDOFF else 'required_actual_evidence'
        assert r[field] and r['accepted'] is False and r['contact_authorized_now'] is False
        for k in ['actual_provider_identity','actual_provider_locator','actual_body_sha256','actual_body_bytes','actual_appointment']:assert r[k] is None
    assert mapping['CE11']==['X08',HANDOFF] and mapping['CE12']==['X06',FINAL,'X10']
    h=by_id[HANDOFF];f=by_id[FINAL];a=d['step_obligation_boundary']['CE11'];b=d['step_obligation_boundary']['CE12']
    assert h['downstream_steps']==['CE11'] and f['downstream_steps']==['CE12']
    assert h['requirement_kind']=='DOCUMENTARY_HANDOFF_OF_PENDING_FINAL_ROUTE' and 'required_actual_evidence' not in h
    assert f['requirement_kind']=='ACTUAL_FINAL_EVIDENCE_BEFORE_AUTHORIZED_CLAIM' and 'required_documentary_handoff' not in f
    assert h['required_documentary_handoff']==finding['repair_proposal_not_applied'][0]['requirement']
    assert f['required_actual_evidence']==finding['repair_proposal_not_applied'][1]['requirement']
    assert a['required_actual_custody_step_ids']==plan['steps'][10]['depends_on']==['CE%02d'%i for i in range(1,11)]
    assert h['preserves_actual_CE01_CE10_custody_evidence'] and a['no_execution_gate_release']
    for row,fields in [(h,['requires_actual_final_route_completion','requires_CE12_receipt_claim_or_spawn']),
                       (a,['actual_final_route_completion_required','CE12_receipt_claim_or_spawn_required','accepted'])]:
        for k in fields:assert row[k] is False
    prerequisites=plan['closure_boundaries']['external_prerequisites_for_receipt']
    claim_fact='ACTUAL_ATOMIC_ONE_USE_CLAIM_AND_PROTECTED_CONSTRUCTION'
    # Classify by meaning/identity, independently of the preparer's positional slicing.
    expected_preclaim={
        'SEPARATE_EXPLICIT_EXECUTION_AUTHORIZATION','ACTUAL_FINAL_E06_AND_PAYLOAD',
        'ACTUAL_Q_AND_TRUSTED_FINAL_ROOT','ACTUAL_FULL_ROOT_ADMISSION'}
    assert set(prerequisites)==expected_preclaim|{claim_fact} and len(prerequisites)==5
    for r in [f,b]:
        assert set(r['external_prerequisites'])==set(prerequisites) and len(r['external_prerequisites'])==5
        assert set(r['preclaim_external_prerequisites'])==expected_preclaim and len(r['preclaim_external_prerequisites'])==4
        assert r['receipt_only_external_prerequisites']==[claim_fact]
    assert set(a['final_route_obligations_to_handoff'])==set(prerequisites)
    assert not f['handoff_performs_or_satisfies_prerequisites'] and not f['current_execution_or_issuance_authorized']
    for k in ['documentary_handoff_satisfies_prerequisites','currently_authorized','accepted']:assert b[k] is False
    assert b['preclaim_prerequisites_must_be_genuinely_satisfied_before_claim']
    assert b['all_external_prerequisites_must_be_genuinely_satisfied_before_receipt'] and b['claim_is_not_its_own_precondition']
    # A projection of prerequisite phases only. No new active graph or full-I181 replacement.
    phases={p:[] for p in sorted(expected_preclaim)}
    phases.update(ATOMIC_CLAIM_ACTION=sorted(expected_preclaim),PROTECTED_CONSTRUCTION_ACTION=['ATOMIC_CLAIM_ACTION'])
    phases[claim_fact]=['ATOMIC_CLAIM_ACTION','PROTECTED_CONSTRUCTION_ACTION']
    phases['RECEIPT_ACTION']=prerequisites
    phase_ancestors=ancestors_for(phases)
    assert phase_ancestors['ATOMIC_CLAIM_ACTION']==expected_preclaim
    assert claim_fact not in phase_ancestors['ATOMIC_CLAIM_ACTION']
    assert expected_preclaim|{claim_fact,'ATOMIC_CLAIM_ACTION','PROTECTED_CONSTRUCTION_ACTION'}==phase_ancestors['RECEIPT_ACTION']
    source_order=spec['record_order'];source_ancestors=ancestors_for(source_order)
    assert len(source_order)==16
    assert {'C_CONTEXT','Q_REQUEST','FINAL_ROOT','FINAL_E06','FINAL_PAYLOAD'}<=source_ancestors['ATOMIC_CLAIM']
    assert {'ATOMIC_CLAIM','FINAL_ROOT'}<=source_ancestors['LAUNCH_RECEIPT']
    assert 'ATOMIC_CLAIM' not in source_ancestors['FINAL_ROOT']
    assert plan['closure_boundaries']['prelaunch_depends_on_receipt'] is False
    assert 'CE12' not in plan['steps'][10]['depends_on']
    assert d['role_scope_matrix']==old['role_scope_matrix'] and len(d['role_scope_matrix'])==8
    assert d['inherited_scope_boundaries']==old['inherited_scope_boundaries']
    assert len(d['inherited_scope_boundaries']['S01_exclusions'])==8
    assert len(d['inherited_scope_boundaries']['extra_custody_separation'])==4
    assert len(d['inherited_scope_boundaries']['full_CP07_conditions'])==9
    assert d['preserved_negative_gates']==old['preserved_negative_gates']
    gates={r['id']:r['observed_value'] for r in d['preserved_negative_gates']}
    assert gates==dict(status='IMPLEMENTED_NOT_ADMITTED',CP03_global_resolved=True,
        CP07_exact_admission_resolved=False,correlated_atomicity_verified=False,component_validation='NOT_RUN')
    assert d['current_effect']['CE01_accepted'] is False and not d['current_effect']['F195_01_accepted_closure']
    assert d['producer']['actor_independent'] is False and not d['producer']['independent_acceptance']
    for role in ['primary_R06','separate_R08']:assert d['review_dispositions'][role]['decision']=='PENDING_NOT_ACCEPTED'
    assert d['decision']==plan['decision'] and d['E06']==plan['E06']
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][1:])
    return dict(schema='d5.i198-i197-source-reconstruction.v1',increment='I198',date='2026-11-16',base_commit=BASE,
        input_pins=pins,method='Fresh Git blobs, reverse obligation-to-step incidence, semantic classification of preclaim versus prereceipt facts and independent DFS of phase projection and pinned I191 order; predecessor documentary build reproduced without publication mains.',
        requirement_mapping=mapping,
        repair_coverage=dict(total_rows=11,unchanged_external_rows=9,actual_external_requirement_rows=10,
            documentary_handoff_rows=1,all_rows_unaccepted=True,CE11_actual_CE01_CE10_requirements_retained=True,
            CE11_no_actual_final_completion_or_receipt_claim_spawn_required=True,
            CE12_preclaim_prerequisites=sorted(expected_preclaim),CE12_prereceipt_event_requirement=claim_fact,
            no_handoff_satisfies_actual_evidence=True,prior_documentary_rejection_checks_reproduced=6),
        order_review=dict(projection_only_not_full_I181_or_runtime_graph=True,phase_dependencies=phases,
            phase_ancestors={k:sorted(v) for k,v in sorted(phase_ancestors.items())},
            source_I191_nodes=16,source_order_acyclic=True,source_claim_ancestors=sorted(source_ancestors['ATOMIC_CLAIM']),
            source_receipt_ancestors=sorted(source_ancestors['LAUNCH_RECEIPT']),
            no_claim_as_own_precondition=True,no_prelaunch_receipt_dependency=True),
        preserved_scope=dict(unassigned_roles=8,S01_exclusions=8,additional_custody_separations=4,full_CP07_conditions=9,
            other_dossiers_absent=11,numeric_caps_permissions_and_negative_gates_unchanged=True,prior_I197_preparation_reproduced=True,
            original_dossier_and_open_historical_finding_preserved=True,prior_publication_mains_run=False),
        preserved_I122_gates=gates,
        verdict=dict(new_blocking_documentary_findings=0,CE01_candidate_02_documentarily_confirmed=True,
            F195_01_documentary_repair_confirmed_for_candidate_02=True,F195_01_accepted_closure=False,
            CE01_accepted=False,adopted=False,implemented=False,independent_acceptance=False,
            actual_evidence_accepted=0,resource_obligations_closed=0,product_or_components_executed=0))


def build_review(rec):
    d=rd(DOS);plan=rd(PLAN)
    evidence=[pin(DOS,'/external_evidence_requirements/8'),pin(DOS,'/external_evidence_requirements/9'),
        pin(DOS,'/step_obligation_boundary'),pin(PLAN,'/steps/10'),pin(PLAN,'/closure_boundaries'),
        pin(SPEC,'/rules/11'),pin(SPEC,'/record_order'),pin(FINDING,'/findings/0')]
    checks=[
        ('E01','Three CE01 evidence requirements and exact pinned I191/I192/profile02/output/transport inventory','PASS_DOCUMENTARY_PINS_NOT_ACTUAL_EXTERNAL_EVIDENCE'),
        ('E02','Eight unassigned role scopes and producer/reviewer boundary','PASS_DECLARED_POLICY_NOT_APPOINTMENTS'),
        ('E03','Ten actual-evidence requirements plus one documentary handoff; nine unrelated rows unchanged','PASS_TRUTHFUL_MISSING_EVIDENCE_AND_TYPED_SPLIT'),
        ('A01','Four documentary permissions and14 denied action classes','PASS_NO_EXECUTION_CONTACT_OR_QUOTA_AUTHORITY'),
        ('A02','Eight S01 exclusions, F183-01 and four custody actor/key separations','PASS_PRESERVED_SCOPE_NOT_ACTUAL_INDEPENDENCE'),
        ('B01','No signed policy/role acceptance or competent R06/R08 decision','PASS_NO_COMPETENT_ADOPTION'),
        ('K01','External preaccepted anchors required, no provider/actor/key selected','PASS_REQUIREMENT_NOT_TRUST_PROOF'),
        ('K10','Complete preparer scope and all inherited/additional separations','PASS_DECLARED_EXCLUSIONS_NOT_IDENTITY_PROOF'),
        ('K12','CE11 handoff separated from actual final work, claim and receipt phases; DFS agrees with I191','PASS_F195_01_DOCUMENTARY_REPAIR_FOR_CANDIDATE_02'),
        ('K15','Full per-attempt verification/lookup/copies/native/IO costs still required in phase/resource composition','PASS_INHERITED_OBLIGATION_NOT_RESOURCE_OR_900_PROOF'),
        ('K16','C/Q/I/A/L, pipes/operands, Reader/output/custody caps and numeric candidates unchanged','PASS_DESIGN_LIMITS_NOT_ACTUAL_FIT')]
    effect={**d['current_effect'], 'CE01_documentary_review_completed':True,'CE01_documentary_confirmation':True,
        'F195_01_documentary_repair_confirmed_for_candidate_02':True,'CE01_documentary_revision_required':False}
    return dict(schema='d5.i198-i197-documentary-review.v1',increment='I198',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        proposal=d['proposal_id'],profile_id=d['profile_id'],candidate_id=d['candidate_id'],step='CE01',
        status='CE01_CANDIDATE_02_DOCUMENTARILY_CONFIRMED_NOT_ADOPTED_NOT_ACCEPTED_NOT_ADMITTED',
        reconstruction=pin(RECON),provenance=dict(reviewer='Same Codex assistant/chat that prepared I197/I195 and earlier candidates',
            methodological_reconstruction_separate=True,actor_independent=False,organizationally_independent=False,
            competent_R06_review=False,separate_R08_acceptance=False,independent_acceptance=False),
        findings=[],finding_dispositions=[dict(id='F195-01',status='DOCUMENTARY_REPAIR_CONFIRMED_FOR_CANDIDATE_02_ONLY',
            source_finding=pin(FINDING,'/findings/0'),candidate=pin(DOS),
            historical_I196_open_finding_unchanged=True,historical_I197_pending_review_record_unchanged=True,
            documentary_resolution=True,competent_or_independent_accepted_closure=False,actual_CE01_acceptance=False,
            reason='CE11 now requires a typed pending-final-route handoff, not actual completion; CE12 retains all five genuine receipt prerequisites with four before claim and claim/construction before receipt. No prerequisite was waived and no current permission or evidence was supplied.',
            evidence=evidence)],checks=[dict(id=i,scope=s,result=r) for i,s,r in checks],
        verdict=rec['verdict'],current_effect=effect,decision=plan['decision'],E06=plan['E06'],
        limitations=['Documentary confirmation is limited to exact candidate02 and F195-01 repair; no actual appointment, provider, identity, image/runtime/platform/resource/atomicity/claim evidence or accepted custody.',
            'Phase DFS is a documentary partial-order check, not a full I181 replacement, executable protocol, service simulation or proof of actual operation.',
            'The same assistant prepared/reviewed candidates. Competent R06 and separate R08 adoption/acceptance remain absent; no quota, rebind, authority, execution or D5 release follows.'],
        next_scope='CE01 candidate02 can proceed as a documentarily reviewed scope candidate. A separately requested CE02-ANCHOR intake/preparation is a possible next documentary task; no real provider contact, actor/key enrollment, evidence fabrication, cryptography or execution is authorized. All actual competent CE01 adoption remains pending.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I198-audit.py',
            expected_result='PASS_STATIC_SOURCE_ONLY',runtime_harness='N/A: documentary review/JSON/Git/graph mathematics; no product/component/crypto/image/claim/protocol execution.',
            over400_lines=True,reason='One review unit: pinned reconstruction, reverse step coverage, phase/source DFS, precise finding disposition and preservation evidence; overage reported.'),
        publication=dict(commit_and_push_requested=True,publication_not_adoption_acceptance_or_authority=True))


def main():
    rec=reconstruct();assert rd(RECON)==rec and rd(REVIEW)==build_review(rec)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published474'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==479
    seal=rd(SEAL);assert seal['schema']=='d5.i198-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published479']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['F195_01_documentary_repair_confirmed_for_candidate_02']
    assert seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['F195_01_accepted_closure','CE01_accepted','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I198',new_blocking_documentary_findings=0,
        F195_01_documentary_repair_confirmed_for_candidate_02=True,F195_01_accepted_closure=False,CE01_accepted=False,
        historical_pins=787,prior_published_files_preserved=479,new_files=5,actual_evidence_accepted=0,
        independent_acceptance=False,product_or_components_executed=0,quotas_changed=False,rebind_applied=False,
        resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
