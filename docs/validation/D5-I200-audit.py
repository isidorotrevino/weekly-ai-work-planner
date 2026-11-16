#!/usr/bin/env python3
"""I200: documentary anchor provenance review; no product/components/crypto run."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='186c3f90722ad9c22220938da877fe9ea121be78'
DOS=P+'D5-I193-CE02-ANCHOR-PROVENANCE-CANDIDATE.json'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
CHECK=P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK=P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CE01=P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
PRIOR_AUDIT=P+'D5-I199-audit.py';PRIOR_PREP=P+'D5-I199-preparation-review.json'
PRIOR_SEAL=P+'D5-I199-integrity.json';PRIOR_DOC='docs/design/D5-I199-CE02-ANCHOR-PROVENANCE.md'
PRIOR_FILES={DOS,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON=P+'D5-I200-I199-source-reconstruction.json'
REVIEW=P+'D5-I200-I199-documentary-review.json'
AUDIT=P+'D5-I200-audit.py';SEAL=P+'D5-I200-integrity.json'
DOC='docs/design/D5-I200-I199-CE02-REVIEW.md'
FILES={RECON,REVIEW,AUDIT,SEAL,DOC}


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


def dependency_cycle(graph):
    """Return a documentary label cycle or None; never execute a protocol."""
    done=set();active=[]
    def visit(node):
        assert node in graph
        if node in active:return active[active.index(node):]+[node]
        if node in done:return None
        active.append(node)
        for parent in graph[node]:
            cycle=visit(parent)
            if cycle:return cycle
        active.pop();done.add(node);return None
    for node in sorted(graph):
        cycle=visit(node)
        if cycle:return cycle
    return None


def review_presence_guard(previous,plan):
    target=ROOT/DOS;other_present=ROOT/plan['steps'][0]['candidate_dossier_path']
    other_missing=ROOT/plan['steps'][2]['candidate_dossier_path'];original=Path.exists
    assert git('ls-tree','--name-only',previous['BASE'],'--',DOS)==''
    assert git('ls-tree','--name-only',BASE,'--',DOS)==DOS
    assert target.exists() and other_present.exists() and not other_missing.exists()
    with previous['predecessor_CE02_presence_as_of_base']():
        assert not target.exists() and other_present.exists() and not other_missing.exists()
    assert Path.exists is original and target.exists()
    class DocumentaryProbe(Exception):pass
    try:
        with previous['predecessor_CE02_presence_as_of_base']():
            assert not target.exists()
            raise DocumentaryProbe()
    except DocumentaryProbe:pass
    else:raise AssertionError('Expected documentary exception not raised')
    assert Path.exists is original and target.exists() and other_present.exists() and not other_missing.exists()
    return dict(CE02_absent_in_original_base_verified=True,CE02_present_in_review_base_verified=True,
        only_exact_CE02_query_projected=True,other_existing_and_missing_paths_preserved=True,
        restored_after_success=True,restored_after_exception=True,prior_publication_mains_run=False)


def reconstruct():
    d=rd(DOS);plan=rd(PLAN);spec=rd(SPEC);defs=rd(PACK)['$defs'];ce01=rd(CE01)
    pins={**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==797;verify_git_pins(pins)
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));assert previous['build_review']()==rd(PRIOR_PREP)
    guard=review_presence_guard(previous,plan)
    step=plan['steps'][1];assert step['id']=='CE02' and step['depends_on']==['CE01']
    assert d['required_evidence']==step['required_evidence'] and len(d['required_evidence'])==3
    assert d['planned_acceptance_checks']==step['acceptance_checks'] and len(d['planned_acceptance_checks'])==2
    assert d['authorization_boundary']==step['authorization_boundary']
    assert d['contract_rules']==step['contract_rules']==['K01','K03','K11','K13','K16']
    requirements={r['id']:r for r in d['evidence_requirements']};assert len(requirements)==9
    rule_rows=[]
    for rule in d['contract_rules']:
        definition=next(r for r in spec['rules'] if r['id']==rule)
        ids=[r['id'] for r in requirements.values() if rule in r['contract_rules']]
        assert ids
        rule_rows.append(dict(rule_id=rule,source=pin(SPEC,'/rules/'+str(spec['rules'].index(definition))),
            requirement_ids=ids,actual_evidence_accepted=False))
    ap08=requirements['AP08']
    assert ap08['subject']=='External key selection and three custody role domains'
    assert ap08['required_genuine_evidence']=='Genuine R01/R02/R08 approvals over the same signed core, exact independently selected profile/pack/contract/key-purpose bindings. No supplied C/bundle key bootstraps trust; no crypto here.'
    ce10=next(s for s in plan['steps'] if s['id']=='CE10')
    assert 'CE02' in ce10['depends_on']
    assert ce10['required_evidence'][1]=='Real three-role approval evidence over the common core with exact R01/R02/R08 domains/NUL; no signature or new key generation authorized by this plan.'
    graph={s['id']:list(s['depends_on']) for s in plan['steps']}
    assert dependency_cycle(graph) is None
    hypothetical={k:list(v) for k,v in graph.items()};hypothetical['CE02'].append('CE10')
    cycle=dependency_cycle(hypothetical);assert cycle==['CE02','CE10','CE02']
    order=spec['record_order'];assert order['ANCHOR']==[] and 'ANCHOR' in order['BUNDLE']
    assert dependency_cycle(order) is None
    ambiguity=dict(id='F199-01',row_id='AP08',source_step='CE02',
        unsplit_requirement=ap08['required_genuine_evidence'],
        actual_bundle_approval_step='CE10',CE10_depends_on_CE02=True,
        explicit_anchor_policy_vs_later_bundle_approval_split_present=False,
        cycle_only_if_AP08_is_read_as_CE02_actual_bundle_approval_gate=cycle,
        published_I193_dependency_graph_acyclic=True,actual_cycle_or_execution_observed=False)
    for r in requirements.values():
        for k in ['actual_provider_identity','actual_provider_locator','actual_body_sha256','actual_body_bytes','actual_appointment','actual_acceptance_record']:assert r[k] is None
        assert r['status']=='MISSING_NOT_EVALUATED' and not r['accepted'] and not r['contact_authorized_now']
    actual=d['actual_anchor_state'];false_keys={'complete_referenced_evidence_bodies_supplied','any_private_key_included_or_requested',
        'documentary_hash_used_as_external_expected_registry_digest','actual_positive_I191_record_created'}
    for k,v in actual.items():
        if k in false_keys:assert v is False
        else:assert v is None
    schema=d['schema_obligations'];fragments={r['name']:r for r in schema['definitions']}
    assert set(fragments)=={'anchor_registry','anchor_key','evidence_reference','validity'}
    for name,row in fragments.items():assert row['schema_fragment']==defs[name] and row['source']==pin(PACK,'/$defs/'+name)
    assert len(defs['anchor_registry']['required'])==9 and len(defs['anchor_key']['required'])==5
    assert defs['anchor_registry']['properties']['keys']['minItems']==3 and defs['anchor_registry']['properties']['keys']['maxItems']==64
    assert schema['body_cap_bytes']==spec['record_caps_bytes']['anchor_registry']==65536
    assert schema['dossier_is_not_registry_body'] and schema['body_cap_not_applied_to_documentary_wrapper']
    assert schema['actual_schema_codec_or_crypto_validation']=='NOT_RUN_NO_ACTUAL_BODY'
    contract=d['trust_and_currentness_contract'];profile=rd(plan['bindings']['profile02']['path'])
    assert contract['external_expected_values_must_preexist_supplied_registry'] and contract['no_repo_C_bundle_or_self_signed_bootstrap']
    assert contract['purpose_enum']==defs['anchor_key']['properties']['purpose']['enum']
    assert contract['custody_domains']==spec['custody_approval_domains'] and contract['domain_separator_octets']==[0]
    assert contract['snapshot_max_lifetime_seconds']==profile['bootstrap']['context_limits']['max_validity_seconds']==3600
    assert contract['max_trusted_clock_error_seconds']==profile['bootstrap']['context_limits']['max_clock_error_seconds']==5
    assert contract['time_rule']==profile['bootstrap']['time'] and contract['freshness_rule']==profile['bootstrap']['freshness']
    assert not contract['actual_currentness_verified'] and not contract['instantaneous_revocation_discovery_claimed']
    assert all(r['actual_evaluation']=='NOT_EVALUATED' for r in contract['rejection_conditions'])
    assert d['dependency_gate']['actual_dependency_satisfied'] is False and d['dependency_gate']['competent_CE01_acceptance'] is False
    assert d['inherited_scope_boundaries']==ce01['inherited_scope_boundaries'] and d['preserved_negative_gates']==ce01['preserved_negative_gates']
    assert [r['id'] for r in d['role_scope_matrix']]==['R01','R02','R08']
    for r in d['role_scope_matrix']:assert r['assigned_person'] is None and r['current_actions_authorized']==[] and not r['accepted_appointment']
    for r in d['review_dispositions'].values():
        if isinstance(r,dict):assert r==dict(person=None,appointment=None,authority=None,decision='PENDING_NOT_ACCEPTED')
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][2:])
    assert d['decision']==plan['decision'] and d['E06']==plan['E06']
    return dict(schema='d5.i200-i199-source-reconstruction.v1',increment='I200',date='2026-11-16',base_commit=BASE,
        input_pins=pins,method='Fresh Git blobs, reverse rule-to-requirement and schema coverage, independent I193/I191 dependency review and conditional AP08 counterexample, historical presence guard checked on success and exception. Predecessor documentary build reproduced without publication main.',
        historical_presence_guard=guard,reverse_rule_coverage=rule_rows,
        boundary_ambiguity=ambiguity,
        schema_review=dict(definitions=4,required_registry_fields=defs['anchor_registry']['required'],required_key_fields=defs['anchor_key']['required'],
            minimum_anchor_keys=3,maximum_anchor_keys=64,registry_candidate_cap_bytes=65536,
            documentary_wrapper_is_not_registry=True,actual_registry_body_available=False,actual_schema_codec_or_crypto_validation=False),
        preserved_scope=dict(documentary_sources=14,missing_provenance_requirements=9,pending_rejection_conditions=10,
            unassigned_primary_or_separate_review_slots=3,actual_CE01_dependency_satisfied=False,
            S01_exclusions_preserved=8,extra_custody_separations_preserved=4,full_CP07_conditions_preserved=9,
            caps_numeric_candidates_and_negative_gates_unchanged=True,other_planned_dossiers_absent=10),
        verdict=dict(new_blocking_documentary_findings=1,CE02_documentary_confirmation=False,revision_required=True,
            CE02_accepted=False,actual_anchor_registry_created=False,adopted=False,implemented=False,
            independent_acceptance=False,actual_evidence_accepted=0,resource_obligations_closed=0,product_or_components_executed=0))


def build_review(rec):
    d=rd(DOS);plan=rd(PLAN)
    finding=dict(id='F199-01',priority='P2',status='OPEN_DOCUMENTARY_REVISION_REQUIRED',blocks_documentary_confirmation=True,
        title='Separate prior anchor policy/provisioning from later CE10 signed-core approvals',
        evidence=[pin(DOS,'/evidence_requirements/7'),pin(DOS,'/actual_anchor_state/actual_signature_or_custody_approvals'),
            pin(PRIOR_DOC),pin(PLAN,'/steps/1'),pin(PLAN,'/steps/9'),pin(SPEC,'/rules/0'),pin(SPEC,'/rules/10'),pin(SPEC,'/record_order')],
        observed=rec['boundary_ambiguity'],
        impact='AP08 places genuine R01/R02/R08 signed-core approvals among CE02 missing evidence requirements without a later-stage qualifier. I193 assigns those actual bundle approvals to CE10, which depends on CE02; I191 requires externally accepted anchors before the bundle. Reading AP08 as a CE02 closure requirement would reverse that dependency. This is an ambiguous documentary requirement, not an observed live cycle or execution.',
        requested_revision='Keep authentic preexisting anchor provisioning, identity authority, externally expected digest/epochs and genuine competent prior acceptance at CE02. Separate the K11 purpose/domain/key/policy constraints needed now from actual bundle signed-core approval evidence due at CE10. Update AP08/table, the ambiguous approvals availability slot and per-step documentary audit. Do not remove genuine prior anchor acceptance or create a CE10 dossier/approval.',
        repair_proposal_not_applied=[
            dict(proposed_id='AP08-ANCHOR-POLICY',consumer_step='CE02',kind='PRIOR_EXTERNAL_ANCHOR_PROVISIONING_AND_APPROVAL_POLICY',
                requirement='Require genuine independent anchor/identity-authority provisioning and prior acceptance, external expected digest/epochs and purpose/actor/key bindings; pin the exact role-domain/core/profile/pack/contract selection policy. No actual future CE10 bundle signature or approval is required to accept CE02 provenance.',
                actual_evidence_supplied=False,accepted=False,current_execution_or_contact_authorized=False),
            dict(proposed_id='AP08-BUNDLE-APPROVAL',consumer_step='CE10',kind='DEFERRED_ACTUAL_BUNDLE_APPROVAL_EVIDENCE',
                requirement='After authentic antecedents and exact C/core exist, require the real three R01/R02/R08 role-domain approvals over that same core, using independently accepted CE02 purpose/actor/key and exact policy pins. Neither these signatures nor their bundle may bootstrap CE02 trust.',
                actual_evidence_supplied=False,accepted=False,current_execution_or_contact_authorized=False)],
        completion_checks=['CE02 retains all genuine prior provisioning/identity/acceptance evidence, without requiring a future CE10 signed-core approval.',
            'Actual bundle approvals are explicitly deferred to CE10; the declared CE02/CE10 order remains acyclic and no supplied signature/hash/key becomes its own authority.',
            'Separate prior acceptance availability from future bundle approvals; update the candidate table and check requirements by phase, not merely nonempty K-rule coverage.',
            'All actual evidence/appointments/acceptance remain missing; no registry, key, signature, codec/crypto run, provider contact or active binding is created.'],
        source_candidate_modified=False,competent_adoption=False)
    checks=[
        ('E01','Independent origin, expected digest/epoch and identity authority','PASS_DECLARED_MISSING_EXTERNAL_EVIDENCE'),
        ('E02','Purpose/actor/key/currentness and prior provisioning versus future approvals','PARTIAL_AP08_PHASE_AMBIGUITY'),
        ('E03','Complete actual referenced bodies, no private keys/generation','PASS_MISSING_BODIES_NOT_PLACEHOLDER_RECORD'),
        ('A01','No self-signed/supplied-key/unknown-authority/currentness fallback','PASS_DECLARED_REJECTION_POLICY_NOT_LIVE_VERIFICATION'),
        ('A02','Canonical schema/codec/cap65536 and prior acceptance/hash requirements','PASS_NO_ACTUAL_BODY_OR_ACCEPTANCE_CLAIMED'),
        ('B01','I193 missing-evidence-only boundary and unsatisfied competent CE01 dependency','PASS_NO_DEPENDENCY_OR_AUTHORITY_BYPASS'),
        ('K01','External accepted anchor/identity authority before registry/C/bundle','PASS_TRUST_ORIGIN_BOUNDARY_NOT_AUTHORITY_PROOF'),
        ('K03','Complete sorted unique purpose/key/actor scope and all underlying proof bodies/costs','PASS_DECLARED_COMPLETENESS_NOT_REAL_IDENTITY_OR_RESOURCE_PROOF'),
        ('K11','Prior anchor policy versus real common-core approvals belonging to CE10','PARTIAL_F199_01_NO_ACTUAL_CYCLE_OBSERVED'),
        ('K13','3600 lifetime/5 clock error/known revocation/currentness','PASS_DECLARED_TIME_RULE_NOT_FRESHNESS_PROOF'),
        ('K16','Registry cap differs from documentary wrapper; other caps/quotas unchanged','PASS_DESIGN_LIMITS_NOT_ACTUAL_FIT')]
    effect={**d['current_effect'],'CE02_documentary_review_completed':True,
        'CE02_documentary_confirmation':False,'CE02_documentary_revision_required':True}
    return dict(schema='d5.i200-i199-documentary-review.v1',increment='I200',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        proposal=d['proposal_id'],profile_id=d['profile_id'],step='CE02',
        status='CE02_DOCUMENTARY_REVIEW_REVISION_REQUIRED_EVIDENCE_MISSING_NOT_ADOPTED_NOT_ACCEPTED_NOT_ADMITTED',
        reconstruction=pin(RECON),provenance=dict(reviewer='Same Codex assistant/chat that prepared I199 and earlier candidates',
            methodological_reconstruction_separate=True,actor_independent=False,organizationally_independent=False,
            competent_R01_R02_review=False,separate_R08_acceptance=False,independent_acceptance=False),
        findings=[finding],checks=[dict(id=i,scope=s,result=r) for i,s,r in checks],verdict=rec['verdict'],
        current_effect=effect,decision=plan['decision'],E06=plan['E06'],
        limitations=['The absence of actual anchors/providers/keys/authority/acceptance is correctly disclosed and remains an external prerequisite, not itself a new documentary defect.',
            'The conditional cycle is a documentary counterexample only if AP08 is interpreted as an actual CE02 closure requirement. The published I193 graph is acyclic and no real action or live cycle was observed.',
            'Registry codec/schema/crypto/provenance/currentness/resource verification were not run. Same assistant preparation/review is not competent or independent R01/R02/R08 acceptance.'],
        next_scope='Prepare a separately requested CE02 revision separating prior anchor policy/provisioning from deferred CE10 bundle approvals, then review that exact revision. Genuine external evidence and competent CE01/CE02 acceptance remain independently pending.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I200-audit.py',
            expected_result='PASS_STATIC_SOURCE_ONLY_WITH_OPEN_FINDING_F199_01',
            runtime_harness='N/A: documentary JSON/Git/schema-fragment/dependency review; no product/components/crypto/registry codec/image/claim/protocol execution.',
            over400_lines=True,reason='One pinned review unit with reverse coverage, precise phase finding, conditional dependency evidence and preservation checks; overage reported.'),
        publication=dict(commit_and_push_requested=True,publication_not_adoption_acceptance_or_authority=True))


def main():
    rec=reconstruct();assert rd(RECON)==rec and rd(REVIEW)==build_review(rec)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published484'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==489
    seal=rd(SEAL);assert seal['schema']=='d5.i200-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published489']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['open_documentary_findings']==['F199-01']
    assert seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['CE02_accepted','actual_anchor_registry_created','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY_WITH_OPEN_FINDING_F199_01',increment='I200',
        new_blocking_documentary_findings=1,CE02_documentary_confirmation=False,CE02_accepted=False,
        actual_anchor_registry_created=False,historical_pins=797,prior_published_files_preserved=489,new_files=5,
        actual_evidence_accepted=0,independent_acceptance=False,product_or_components_executed=0,quotas_changed=False,
        rebind_applied=False,resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
