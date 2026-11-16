#!/usr/bin/env python3
"""I202: documentary CE02 revision review, JSON/Git/graph math; no components."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='8ff09022193b488d1d58d487d6abdf7aef96040c'
DOS=P+'D5-I201-CE02-ANCHOR-PROVENANCE-CANDIDATE-02.json'
OLD=P+'D5-I193-CE02-ANCHOR-PROVENANCE-CANDIDATE.json'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK=P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
FINDING=P+'D5-I200-I199-documentary-review.json'
PRIOR_PREP=P+'D5-I201-preparation-review.json';PRIOR_AUDIT=P+'D5-I201-audit.py'
PRIOR_SEAL=P+'D5-I201-integrity.json';PRIOR_DOC='docs/design/D5-I201-CE02-ANCHOR-PROVENANCE-02.md'
PRIOR_FILES={DOS,PRIOR_PREP,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON=P+'D5-I202-I201-source-reconstruction.json';REVIEW=P+'D5-I202-I201-documentary-review.json'
AUDIT=P+'D5-I202-audit.py';SEAL=P+'D5-I202-integrity.json';DOC='docs/design/D5-I202-I201-CE02-02-REVIEW.md'
FILES={RECON,REVIEW,AUDIT,SEAL,DOC}
POLICY='AP08-ANCHOR-POLICY';APPROVAL='AP08-BUNDLE-APPROVAL'


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
    """Independent DFS of documentary prerequisites only, no service/protocol model."""
    active=set();done={}
    def visit(n):
        assert n in graph and n not in active,n
        if n in done:return done[n]
        active.add(n);result=set()
        for p in graph[n]:result.add(p);result.update(visit(p))
        active.remove(n);assert n not in result;done[n]=result;return result
    for n in sorted(graph):visit(n)
    return done


def reconstruct():
    d=rd(DOS);old=rd(OLD);plan=rd(PLAN);spec=rd(SPEC);defs=rd(PACK)['$defs']
    pins={**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==807;verify_git_blobs(pins)
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));prior=previous['build_review']()
    assert prior==rd(PRIOR_PREP)
    finding=rd(FINDING)['findings'][0];assert finding['id']=='F199-01' and finding['status']=='OPEN_DOCUMENTARY_REVISION_REQUIRED'
    rows=d['evidence_requirements'];by_id={r['id']:r for r in rows};assert len(rows)==len(by_id)==10 and 'AP08' not in by_id
    assert rows[:7]==old['evidence_requirements'][:7] and rows[9:]==old['evidence_requirements'][8:]
    consumers={'CE02':[],'CE10':[]};rule_consumers={r:{} for r in d['contract_rules']}
    for row in rows:
        step=row.get('consumer_step',d['step']);assert step in consumers
        consumers[step].append(row['id'])
        for rule in row['contract_rules']:rule_consumers[rule].setdefault(step,[]).append(row['id'])
        for k in ['actual_provider_identity','actual_provider_locator','actual_body_sha256','actual_body_bytes','actual_appointment','actual_acceptance_record']:assert row[k] is None
        assert row['status']=='MISSING_NOT_EVALUATED' and not row['accepted'] and not row['contact_authorized_now']
    expected_prior=['AP%02d'%i for i in range(1,8)]+[POLICY,'AP09']
    assert consumers==dict(CE02=expected_prior,CE10=[APPROVAL])
    assert rule_consumers['K11']==dict(CE02=['AP04',POLICY],CE10=[APPROVAL])
    p=by_id[POLICY];a=by_id[APPROVAL];bound=d['step_obligation_boundary']
    assert p['requirement_kind']=='PRIOR_EXTERNAL_ANCHOR_PROVISIONING_AND_APPROVAL_POLICY'
    assert a['requirement_kind']=='DEFERRED_ACTUAL_BUNDLE_APPROVAL_EVIDENCE'
    for row,proposal in zip([p,a],finding['repair_proposal_not_applied']):assert row['required_genuine_evidence']==proposal['requirement']
    assert p['genuine_prior_provisioning_and_acceptance_required'] and not p['future_CE10_bundle_approval_required']
    assert bound['CE02']['genuine_prior_anchor_provisioning_and_acceptance_required']
    assert bound['CE02']['authentic_identity_authority_external_expected_digest_epochs_and_bindings_required']
    assert bound['CE02']['approval_policy_is_not_actual_bundle_approval'] and bound['CE02']['no_execution_gate_release']
    for k in ['actual_future_CE10_bundle_approvals_required','future_C_or_bundle_may_bootstrap_anchors','accepted']:assert bound['CE02'][k] is False
    assert a['authentic_antecedents_and_exact_C_before_approvals'] and a['independently_accepted_CE02_anchors_required']
    assert not a['bundle_approvals_may_authenticate_their_own_anchors'] and not a['current_action_authorized'] and not a['CE10_dossier_created']
    for k in ['bundle_approvals_may_discharge_CE02_prior_acceptance','currently_authorized','actual_dossier_created','accepted']:assert bound['CE10'][k] is False
    assert bound['CE10']['actual_common_core_approvals_required'] and bound['CE10']['accepted_anchors_and_exact_C_before_actual_approvals']
    assert bound['CE02']['required_requirement_ids']==consumers['CE02'] and bound['CE10']['deferred_requirement_ids']==consumers['CE10']
    graph={s['id']:s['depends_on'] for s in plan['steps']};closure=ancestors(graph)
    assert len(graph)==12 and graph['CE02']==bound['CE02']['required_step_ids']==['CE01']
    assert graph['CE10']==bound['CE10']['required_step_ids']==['CE02','CE08','CE09']
    assert closure['CE02']=={'CE01'} and 'CE10' not in closure['CE02']
    assert {'CE02','CE08','CE09'}<=closure['CE10']
    source=ancestors(spec['record_order']);assert len(source)==16
    assert source['ANCHOR']==set() and {'ANCHOR','C_CONTEXT','ACCEPTANCE'}<=source['BUNDLE']
    assert 'BUNDLE' not in source['ANCHOR']
    actual=d['actual_anchor_state'];assert 'actual_signature_or_custody_approvals' not in actual
    assert actual['genuine_prior_acceptance_record'] is None and actual['genuine_prior_anchor_provisioning_acceptance_evidence'] is None
    assert actual['externally_expected_registry_sha256'] is None and actual['actual_anchor_registry_record'] is None
    assert actual['actual_anchor_registry_sha256'] is None and actual['actual_public_key_bindings'] is None
    assert not actual['documentary_hash_used_as_external_expected_registry_digest'] and not actual['actual_positive_I191_record_created']
    future=d['future_CE10_bundle_approval_availability'];assert future['consumer_step']=='CE10' and future['requirement_id']==APPROVAL
    for k in ['actual_bundle_approvals','actual_signed_core_sha256','actual_C_sha256']:assert future[k] is None
    for k in ['actual_evidence_supplied','accepted','current_action_authorized','actual_CE10_dossier_created']:assert future[k] is False
    assert future['actual_schema_codec_or_crypto_validation']=='NOT_RUN'
    schema=d['schema_obligations'];assert schema==old['schema_obligations']
    for r in schema['definitions']:assert r['schema_fragment']==defs[r['name']]
    assert schema['body_cap_bytes']==65536 and schema['dossier_is_not_registry_body'] and schema['body_cap_not_applied_to_documentary_wrapper']
    assert schema['actual_schema_codec_or_crypto_validation']=='NOT_RUN_NO_ACTUAL_BODY'
    assert d['inherited_scope_boundaries']==old['inherited_scope_boundaries'] and d['preserved_negative_gates']==old['preserved_negative_gates']
    assert d['role_scope_matrix']==old['role_scope_matrix'] and [r['id'] for r in d['role_scope_matrix']]==['R01','R02','R08']
    assert d['permission_boundary']==old['permission_boundary']
    assert len(d['permission_boundary']['authorized_documentary_actions'])==4 and len(d['permission_boundary']['denied_action_classes'])==14
    assert not d['dependency_gate']['actual_dependency_satisfied'] and not d['dependency_gate']['competent_CE01_acceptance']
    assert not d['current_effect']['CE02_accepted'] and not d['current_effect']['F199_01_accepted_closure']
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][2:])
    assert d['decision']==plan['decision'] and d['E06']==plan['E06']
    return dict(schema='d5.i202-i201-source-reconstruction.v1',increment='I202',date='2026-11-16',base_commit=BASE,
        input_pins=pins,method='Fresh Git blobs, independently reconstructed requirement consumer/rule incidence and DFS of pinned I193/I191 orders; direct check of genuine prior acceptance and separated missing-approval slots. Predecessor documentary preparation reproduced without publication mains.',
        requirement_consumers=consumers,rule_consumers=rule_consumers,
        repair_coverage=dict(requirement_rows=10,unchanged_rows=8,CE02_prior_rows=9,CE10_deferred_rows=1,
            genuine_prior_anchor_acceptance_still_required=True,no_actual_future_approval_needed_for_CE02=True,
            K11_policy_before_actual_approvals=True,availability_prior_and_future_separate=True,
            no_future_bundle_bootstraps_anchor_trust=True,actual_CE10_dossier_created=False,
            prior_documentary_rejection_checks_reproduced=7),
        order_review=dict(I193_dependency_graph_acyclic=True,CE02_ancestors=sorted(closure['CE02']),
            CE10_ancestors=sorted(closure['CE10']),no_CE02_to_CE10_reverse_dependency=True,
            I191_record_order_acyclic=True,ANCHOR_ancestors=sorted(source['ANCHOR']),BUNDLE_ancestors=sorted(source['BUNDLE']),
            graph_is_documentary_not_actual_enrollment_or_execution=True),
        preserved_scope=dict(documentary_sources=14,unassigned_review_slots=3,pending_rejection_conditions=10,
            actual_CE01_dependency_satisfied=False,other_planned_dossiers_absent=10,
            registry_candidate_cap_bytes=65536,actual_registry_body_available=False,actual_codec_schema_or_crypto_validation=False,
            S01_exclusions=8,extra_custody_separations=4,full_CP07_conditions=9,
            schemas_caps_role_permissions_numeric_candidates_and_negative_gates_unchanged=True,
            I199_original_and_I200_open_finding_preserved=True,I201_preparation_reproduced=True,prior_publication_mains_run=False),
        verdict=dict(new_blocking_documentary_findings=0,CE02_candidate_02_documentarily_confirmed=True,
            F199_01_documentary_repair_confirmed_for_candidate_02=True,F199_01_accepted_closure=False,CE02_accepted=False,
            actual_anchor_registry_created=False,adopted=False,implemented=False,independent_acceptance=False,
            actual_evidence_accepted=0,resource_obligations_closed=0,product_or_components_executed=0))


def build_review(rec):
    d=rd(DOS);plan=rd(PLAN)
    evidence=[pin(DOS,'/evidence_requirements/7'),pin(DOS,'/evidence_requirements/8'),pin(DOS,'/step_obligation_boundary'),
        pin(DOS,'/actual_anchor_state'),pin(DOS,'/future_CE10_bundle_approval_availability'),
        pin(PLAN,'/steps/1'),pin(PLAN,'/steps/9'),pin(SPEC,'/rules/0'),pin(SPEC,'/rules/10'),pin(SPEC,'/record_order'),pin(FINDING,'/findings/0')]
    checks=[
        ('E01','Independent existing origin, expected digest/epochs and identity authority','PASS_MISSING_EXTERNAL_PROVENANCE_TRUTHFULLY_DECLARED'),
        ('E02','Prior provisioning/key policy distinguished from later bundle approvals','PASS_PHASE_SPECIFIC_REQUIREMENTS_WITH_PRIOR_ACCEPTANCE_RETAINED'),
        ('E03','Complete underlying bodies required, no private keys or fabricated registry','PASS_MISSING_BODIES_NOT_POSITIVE_EVIDENCE'),
        ('A01','No self-signed/supplied-key/unknown-authority/currentness fallback','PASS_DECLARED_REJECTION_POLICY_NOT_REAL_CHECKS'),
        ('A02','Exact schema/codec/cap65536 and genuine prior acceptance/hash obligations','PASS_NO_ACTUAL_REGISTRY_OR_VALIDATION_CLAIM'),
        ('B01','Missing-only boundary and competent CE01 dependency not bypassed','PASS_NO_AUTHORITY_OR_DEPENDENCY_RELEASE'),
        ('K01','Expected trust selected independently before C/bundle; no future signature bootstraps anchors','PASS_EXTERNAL_TRUST_REQUIREMENT_NOT_AUTHORITY_PROOF'),
        ('K03','Complete sorted unique canonical identity/purpose/key/evidence scope, costs not bounded by indices','PASS_DECLARED_COMPLETENESS_NOT_RESOURCE_OR_IDENTITY_PROOF'),
        ('K11','CE02 policy/prior acceptance; CE10 three real core approvals after antecedents/C','PASS_F199_01_DOCUMENTARY_REPAIR_FOR_EXACT_CANDIDATE_02'),
        ('K13','3600 lifetime/5 clock error/currentness/revocation rules preserved','PASS_DECLARED_TIME_RULE_NOT_ACTUAL_FRESHNESS'),
        ('K16','Registry cap is future body limit, not wrapper/active quota; other caps unchanged','PASS_DESIGN_LIMITS_NOT_ACTUAL_FIT')]
    effect={**d['current_effect'],'CE02_documentary_review_completed':True,'CE02_documentary_confirmation':True,
        'F199_01_documentary_repair_confirmed_for_candidate_02':True,'CE02_documentary_revision_required':False}
    return dict(schema='d5.i202-i201-documentary-review.v1',increment='I202',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        proposal=d['proposal_id'],profile_id=d['profile_id'],candidate_id=d['candidate_id'],step='CE02',
        status='CE02_CANDIDATE_02_DOCUMENTARILY_CONFIRMED_EVIDENCE_MISSING_NOT_ADOPTED_NOT_ACCEPTED_NOT_ADMITTED',
        reconstruction=pin(RECON),provenance=dict(reviewer='Same Codex assistant/chat that prepared I201/I199 and earlier candidates',
            methodological_reconstruction_separate=True,actor_independent=False,organizationally_independent=False,
            competent_R01_R02_review=False,separate_R08_acceptance=False,independent_acceptance=False),
        findings=[],finding_dispositions=[dict(id='F199-01',status='DOCUMENTARY_REPAIR_CONFIRMED_FOR_CANDIDATE_02_ONLY',
            source_finding=pin(FINDING,'/findings/0'),candidate=pin(DOS),historical_I200_open_finding_unchanged=True,
            historical_I201_pending_review_record_unchanged=True,documentary_resolution=True,
            competent_or_independent_accepted_closure=False,actual_CE02_acceptance=False,
            reason='CE02 retains genuine independent prior provisioning/identity/expected values/bindings/acceptance and K11 selection policy. Actual same-core approvals explicitly belong to CE10 after accepted anchors/C; separated availability and phase checks prevent reverse bootstrap. No prior acceptance was waived and no actual evidence or authorization supplied.',evidence=evidence)],
        checks=[dict(id=i,scope=s,result=r) for i,s,r in checks],verdict=rec['verdict'],current_effect=effect,
        decision=plan['decision'],E06=plan['E06'],
        limitations=['Confirmation applies only to exact candidate02 documentary repair; no actual anchor, authority, expected digest/epoch, actor/key/proof body, clock/revocation, registry, C/core or approval accepted.',
            'Dependency DFS and seven predecessor rejection checks are documentary checks only; no product/component, schema/codec/crypto, enrollment, provider contact, image/runtime/probe or claim execution.',
            'The same assistant prepared/reviewed. Genuine competent CE01/CE02 adoption and R01/R02/R08 decisions remain absent; all resource/atomicity/final evidence/admission gates stay pending.'],
        next_scope='CE02 candidate02 is documentarily reviewed with actual evidence missing. A separately requested CE03 documentary preparation is a possible next scope; do not invent identities/appointments, contact providers, enroll actors/keys or infer any actual CE01/CE02 acceptance.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I202-audit.py',
            expected_result='PASS_STATIC_SOURCE_ONLY',runtime_harness='N/A: documentary JSON/Git/consumer/graph review; no product/components/registry codec/crypto/image/claim/protocol execution.',
            over400_lines=True,reason='One pinned review unit with precise finding disposition, reverse consumer/rule coverage, independent dependency review and historical preservation; overage reported.'),
        publication=dict(commit_and_push_requested=True,publication_not_adoption_acceptance_or_authority=True))


def main():
    rec=reconstruct();assert rd(RECON)==rec and rd(REVIEW)==build_review(rec)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published494'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==499
    seal=rd(SEAL);assert seal['schema']=='d5.i202-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published499']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['F199_01_documentary_repair_confirmed_for_candidate_02']
    assert seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['F199_01_accepted_closure','CE02_accepted','actual_anchor_registry_created','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I202',new_blocking_documentary_findings=0,
        F199_01_documentary_repair_confirmed_for_candidate_02=True,F199_01_accepted_closure=False,CE02_accepted=False,
        actual_anchor_registry_created=False,historical_pins=807,prior_published_files_preserved=499,new_files=5,
        actual_evidence_accepted=0,independent_acceptance=False,product_or_components_executed=0,quotas_changed=False,
        rebind_applied=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
