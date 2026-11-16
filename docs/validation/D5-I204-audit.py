#!/usr/bin/env python3
"""I204 documentary CE03/CE08 review: Git/JSON/graphs only, no components."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='cf293f90cac9ac510df59b7b3233f0e32aad1b59'
DOS=P+'D5-I193-CE03-HUMAN-IDENTITY-ROSTER-CANDIDATE.json'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json';CHECK=P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json';PACK=P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CE02=P+'D5-I201-CE02-ANCHOR-PROVENANCE-CANDIDATE-02.json'
PRIOR_AUDIT=P+'D5-I203-audit.py';PRIOR_PREP=P+'D5-I203-preparation-review.json';PRIOR_SEAL=P+'D5-I203-integrity.json'
PRIOR_DOC='docs/design/D5-I203-CE03-HUMAN-IDENTITY-ROSTER.md';PRIOR_FILES={DOS,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON=P+'D5-I204-I203-source-reconstruction.json';REVIEW=P+'D5-I204-I203-documentary-review.json'
AUDIT=P+'D5-I204-audit.py';SEAL=P+'D5-I204-integrity.json';DOC='docs/design/D5-I204-I203-CE03-REVIEW.md'
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
    """Independent label dependency DFS, not a protocol, identity or service model."""
    active=set();done={}
    def visit(n):
        assert n in graph and n not in active,n
        if n in done:return done[n]
        active.add(n);result=set()
        for p in graph[n]:result.add(p);result.update(visit(p))
        active.remove(n);assert n not in result;done[n]=result;return result
    for n in sorted(graph):visit(n)
    return done


def review_presence_guard(previous,plan):
    target=ROOT/DOS;existing=[ROOT/s['candidate_dossier_path'] for s in plan['steps'][:2]]
    missing=ROOT/plan['steps'][3]['candidate_dossier_path'];original=Path.exists
    assert git('ls-tree','--name-only',previous['BASE'],'--',DOS)==''
    assert git('ls-tree','--name-only',BASE,'--',DOS)==DOS
    assert target.exists() and all(p.exists() for p in existing) and not missing.exists()
    with previous['predecessor_CE03_presence_as_of_base']():
        assert not target.exists() and all(p.exists() for p in existing) and not missing.exists()
    assert Path.exists is original and target.exists()
    class DocumentaryProbe(Exception):pass
    try:
        with previous['predecessor_CE03_presence_as_of_base']():
            assert not target.exists()
            raise DocumentaryProbe()
    except DocumentaryProbe:pass
    else:raise AssertionError('Expected documentary exception not raised')
    assert Path.exists is original and target.exists() and all(p.exists() for p in existing) and not missing.exists()
    return dict(CE03_absent_in_preparation_base_verified=True,CE03_present_in_review_base_verified=True,
        exact_CE03_query_only=True,CE01_CE02_existing_and_CE04_missing_preserved=True,
        restored_after_success=True,restored_after_exception=True,prior_publication_mains_run=False)


def reconstruct():
    d=rd(DOS);plan=rd(PLAN);spec=rd(SPEC);defs=rd(PACK)['$defs'];step=plan['steps'][2]
    pins={**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==817;verify_git_blobs(pins)
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));prep=previous['build_review']();assert prep==rd(PRIOR_PREP)
    guard=review_presence_guard(previous,plan)
    assert step['id']=='CE03' and step['depends_on']==['CE02']
    assert d['required_evidence']==step['required_evidence'] and len(d['required_evidence'])==3
    assert d['planned_acceptance_checks']==step['acceptance_checks'] and len(d['planned_acceptance_checks'])==3
    assert d['authorization_boundary']==step['authorization_boundary']
    assert d['contract_rules']==step['contract_rules']==['K02','K03','K10','K16']
    rows=d['identity_requirements'];assert len(rows)==9
    consumers={'CE03':[],'CE08':[]};rules={r:{} for r in d['contract_rules']}
    for row in rows:
        consumer=row['consumer_step'];assert consumer in consumers;consumers[consumer].append(row['id'])
        for rule in row['contract_rules']:rules[rule].setdefault(consumer,[]).append(row['id'])
        for k in ['actual_provider_identity','actual_provider_locator','actual_body_sha256','actual_body_bytes','actual_appointment','actual_acceptance_record']:assert row[k] is None
        assert row['status']=='MISSING_NOT_EVALUATED' and not row['accepted'] and not row['contact_authorized_now']
    assert consumers==dict(CE03=['IR%02d'%i for i in range(1,9)],CE08=['IR09'])
    assert rows[8]['requirement_kind']=='DEFERRED_FINAL_ROSTER_FREEZE_BEFORE_C'
    boundary=d['step_obligation_boundary'];intake=boundary['CE03'];freeze=boundary['CE08']
    assert intake['requirement_ids']==consumers['CE03'] and freeze['deferred_requirement_ids']==consumers['CE08']
    assert intake['provisional_intake_only'] and intake['no_execution_gate_release']
    for k in ['final_registry_completeness_or_hash_required','final_freeze_or_future_authors_preapproved','positive_preparation_record_may_pin_C_or_future_root','accepted']:assert intake[k] is False
    assert freeze['complete_actual_evidence_authors_and_preparers_required'] and freeze['final_actor_registry_before_C_required']
    assert freeze['refresh_and_review_dependents_on_changed_identity_scope'] and freeze['refresh_is_not_active_capture_inputs_rebind']
    assert not freeze['finalization_currently_performed'] and not freeze['accepted']
    graph={s['id']:s['depends_on'] for s in plan['steps']};closure=ancestors(graph)
    assert intake['required_step_ids']==graph['CE03']==['CE02'] and closure['CE03']=={'CE01','CE02'}
    assert freeze['required_step_ids']==graph['CE08']==['CE02','CE03','CE04','CE05','CE06','CE07']
    assert set(graph['CE08'])<=closure['CE08'] and 'CE08' in closure['CE09']
    assert 'CE08' not in closure['CE03'] and 'CE10' not in closure['CE03']
    final_order=['actor_registry','image_manifest','caller_identity','platform_custody']
    assert freeze['final_record_order']==plan['steps'][7]['record_families']==final_order
    source=ancestors(spec['record_order'])
    assert 'ACTOR_REGISTRY' in source['IMAGE_MANIFEST'] and 'IMAGE_MANIFEST' in source['CALLER_IDENTITY']
    assert 'CALLER_IDENTITY' in source['PLATFORM_CUSTODY'] and 'PLATFORM_CUSTODY' in source['C_CONTEXT']
    gate=next(g for g in rd(CHECK)['family_gates'] if g['family']=='actor_registry')
    assert gate['candidate_step_ids']==['CE03','CE08'] and gate['final_record_freeze_step']=='CE08'
    assert not gate['accepted'] and gate['actual_body_sha256'] is None
    policy=d['identity_resolution_policy'];profile=rd(plan['bindings']['profile02']['path'])
    assert policy['required_role_ids']==['R%02d'%i for i in range(1,9)]
    assert policy['human_and_software_principal_namespaces_separate'] and policy['assistant_git_or_service_label_is_not_enrolled_human']
    assert policy['aliases_resolve_to_one_canonical_human_under_accepted_authority'] and policy['strings_keys_or_appointments_alone_do_not_prove_distinct_people']
    assert policy['all_documentary_preparers_not_just_source_authors_in_scope'] and policy['complete_sorted_unique_actor_preparer_records_required_at_CE08']
    assert policy['S01_exclusions']==spec['inheritance']['S01_actor_exclusions'] and len(policy['S01_exclusions'])==8
    assert policy['profile_source_author_and_root_key_rules']==profile['bootstrap']['separation'][8:] and len(policy['profile_source_author_and_root_key_rules'])==2
    assert policy['extra_custody_separation']==spec['inheritance']['extra_custody_separation'] and len(policy['extra_custody_separation'])==4
    assert policy['R01_R02_qualified_overlap_permitted'] and policy['actual_bundle_approvals_consumer_step']=='CE10'
    assert policy['future_bundle_approval_required_for_CE03'] is False
    tracking=d['documentary_preparation_tracking'];observations=tracking['known_source_observations']
    assert len(observations)==len(d['documentary_inventory'])==15
    for r in observations:
        assert r['source']['sha256']==sha(r['source']['path'])
        assert r['accountable_human_actor_id'] is None and r['authorship_evidence'] is None and not r['positive_preparation_record_created']
    assert tracking['source_observations_are_document_existence_not_human_authorship']
    assert not tracking['complete_preparer_scope_claimed'] and not tracking['future_authors_preapproved'] and not tracking['actual_positive_preparation_record_created']
    assert tracking['canonical_human_actor_id'] is None and tracking['authorship_evidence'] is None and tracking['actual_contribution_scope_sha256'] is None
    assert tracking['no_preparation_record_may_pin_C_acceptance_bundle_or_future_root']
    actual=d['actual_identity_state'];false_fields={'actual_identity_resolution_performed','actual_separation_verified','final_completeness_claimed','positive_I191_record_created','future_authors_preapproved'}
    assert len(actual)==24
    for k,v in actual.items():
        if k in false_fields:assert v is False
        else:assert v is None
    schema=d['schema_obligations'];assert len(schema['definitions'])==5
    for r in schema['definitions']:assert r['schema_fragment']==defs[r['name']]
    assert schema['final_registry_body_cap_bytes']==spec['record_caps_bytes']['actor_registry']==98304
    assert schema['dossier_is_not_positive_registry'] and schema['body_cap_not_applied_to_documentary_wrapper']
    assert schema['actual_schema_codec_hash_or_crypto_validation']=='NOT_RUN_NO_ACTUAL_BODY' and schema['actual_final_body_validation_consumer_step']=='CE08'
    registry=defs['actor_registry']['properties'];actor=defs['actor']['properties'];record=defs['preparation_record']
    assert registry['actors']['minItems']==1 and registry['actors']['maxItems']==64
    assert registry['documentary_preparation_records']['minItems']==1 and registry['documentary_preparation_records']['maxItems']==16
    assert actor['aliases']['minItems']==0 and actor['aliases']['maxItems']==16
    assert actor['competence_scopes']['minItems']==1 and actor['competence_scopes']['maxItems']==8
    assert record['additionalProperties'] is False and record['required']==['actor_id','record_id','profile_sha256','protocol_schema_sha256','contribution_scope_sha256','authorship_evidence']
    assert record['properties']['profile_sha256']['const']==plan['bindings']['profile02']['sha256']
    assert record['properties']['protocol_schema_sha256']['const']==plan['bindings']['protocol_schemas02']['sha256']
    assert d['freeze_and_refresh']==plan['freeze_and_refresh'] and not d['dependency_gate']['actual_dependency_satisfied']
    assert not d['dependency_gate']['competent_CE02_acceptance']
    assert d['inherited_scope_boundaries']==rd(CE02)['inherited_scope_boundaries'] and d['preserved_negative_gates']==rd(CE02)['preserved_negative_gates']
    assert [r['id'] for r in d['role_scope_matrix']]==['R06','R08']
    for r in d['role_scope_matrix']:assert r['assigned_person'] is None and not r['accepted_appointment'] and r['current_actions_authorized']==[]
    assert len(d['permission_boundary']['authorized_documentary_actions'])==4 and len(d['permission_boundary']['denied_action_classes'])==14
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][3:])
    assert d['decision']==plan['decision'] and d['E06']==plan['E06']
    return dict(schema='d5.i204-i203-source-reconstruction.v1',increment='I204',date='2026-11-16',base_commit=BASE,
        input_pins=pins,method='Fresh Git blobs, reverse consumer/rule incidence, independent I193/I191 ancestor reconstruction, source schema/preparation-binding and non-authorship review; predecessor documentary build reproduced without publication main.',
        requirement_consumers=consumers,rule_consumers=rules,historical_presence_guard=guard,
        phase_review=dict(I193_graph_acyclic=True,CE03_ancestors=sorted(closure['CE03']),CE08_ancestors=sorted(closure['CE08']),
            CE09_requires_CE08=True,no_CE03_dependency_on_CE08_or_CE10=True,final_record_order=final_order,
            I191_antecedent_order_acyclic=True,registry_final_freeze_step='CE08',CE03_is_provisional_only=True,
            no_current_final_registry_or_completeness_claim=True,no_future_authors_preapproved=True),
        identity_and_tracking=dict(canonical_humans_not_software_labels=True,all8_role_scopes_required=True,
            S01_exclusions=8,source_author_root_key_rules=2,extra_custody_separations=4,qualified_R01_R02_overlap_permitted=True,
            source_observations_not_human_authorship=15,authenticated_humans_or_preparation_records_supplied=False,
            complete_preparer_scope_claimed=False,preparation_record_closed_fields=record['required'],
            no_C_acceptance_bundle_or_future_root_hash_in_preparation_record=True,exact_profile_protocol_schema_constants=True),
        preserved_scope=dict(schema_definitions=5,final_registry_candidate_cap=98304,actual_schema_codec_hash_or_crypto_validation=False,
            actual_CE02_dependency_satisfied=False,unassigned_review_slots=2,other_planned_dossiers_absent=9,
            prior_documentary_rejection_checks_reproduced=7,caps_numeric_permissions_and_negative_gates_unchanged=True,
            original_CE03_preparation_preserved=True,prior_publication_mains_run=False),
        verdict=dict(new_blocking_documentary_findings=0,CE03_provisional_candidate_documentarily_confirmed=True,
            CE03_accepted=False,actual_registry_finalized=False,actual_actor_registry_created=False,
            actual_identity_or_separation_verified=False,adopted=False,implemented=False,independent_acceptance=False,
            actual_evidence_accepted=0,resource_obligations_closed=0,product_or_components_executed=0))


def build_review(rec):
    d=rd(DOS);plan=rd(PLAN)
    checks=[
        ('E01','Canonical human/organization/alias/competence/appointment intake','PASS_REQUIREMENT_DECLARED_IDENTITIES_MISSING'),
        ('E02','Human versus software namespace and requester/source-author/all-preparer scope','PASS_NO_SOFTWARE_OR_NAME_AS_AUTHENTICATED_HUMAN'),
        ('E03','Known documentary activity tracked provisionally; final authors/completeness deferred','PASS_DOCUMENT_OBSERVATIONS_NOT_HUMAN_AUTHORSHIP'),
        ('A01','All8 S01 exclusions plus R08/source-author and root-key rules','PASS_DECLARED_UNIVERSAL_POLICY_NOT_ACTUAL_IDENTITY_COMPARISON'),
        ('A02','Extra R08/R01/R02 human/key separation without blanket qualified R01/R02 prohibition','PASS_SEPARATION_POLICY_NOT_REAL_INDEPENDENCE'),
        ('A03','No final registry hash/completeness while preparers/aliases/scope unknown','PASS_CE03_PROVISIONAL_CE08_FINALIZATION'),
        ('B01','CE08 complete freeze/refresh before C, no future-author preapproval','PASS_PHASE_BOUNDARY_NOT_ACTUAL_FREEZE_OR_REBIND'),
        ('K02','One canonical human under accepted authority, software separate and ambiguity rejected','PASS_POLICY_NOT_IDENTITY_ENROLLMENT'),
        ('K03','Complete future preparation record bindings and bodies, no future C/root; partial current tracking honest','PASS_ANTECEDENT_PREPARATION_POLICY_NOT_POSITIVE_RECORD'),
        ('K10','All role/preparer/author/key exclusions and phase-correct CE10 approvals retained','PASS_SCOPE_PRESERVED_NOT_COMPETENT_ACCEPTANCE'),
        ('K16','Candidate schema/cap98304, no truncation or active quotas, future full-body checks at CE08','PASS_DESIGN_LIMITS_NOT_REAL_FIT')]
    effect={**d['current_effect'],'CE03_documentary_review_completed':True,'CE03_documentary_confirmation':True,
        'CE03_documentary_revision_required':False,'CE08_finalization_verified':False}
    return dict(schema='d5.i204-i203-documentary-review.v1',increment='I204',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        proposal=d['proposal_id'],profile_id=d['profile_id'],step='CE03',
        status='CE03_PROVISIONAL_DOCUMENTARILY_CONFIRMED_IDENTITIES_MISSING_NOT_FINALIZED_NOT_ACCEPTED_NOT_ADMITTED',
        reconstruction=pin(RECON),provenance=dict(reviewer='Same Codex assistant/chat that prepared I203 and earlier candidates',
            methodological_reconstruction_separate=True,actor_independent=False,organizationally_independent=False,
            competent_R06_review=False,separate_R08_acceptance=False,independent_acceptance=False),
        findings=[],checks=[dict(id=i,scope=s,result=r) for i,s,r in checks],
        evidence=[pin(DOS,'/identity_requirements'),pin(DOS,'/step_obligation_boundary'),pin(DOS,'/documentary_preparation_tracking'),
            pin(DOS,'/actual_identity_state'),pin(PLAN,'/steps/2'),pin(PLAN,'/steps/7'),pin(PLAN,'/freeze_and_refresh'),
            pin(CHECK,'/family_gates/1'),pin(PACK,'/$defs/preparation_record'),pin(SPEC,'/record_order')],
        verdict=rec['verdict'],current_effect=effect,decision=plan['decision'],E06=plan['E06'],
        limitations=['Exact CE03 documentary scope only: no actual human/organization/alias/role/appointment, authenticated authorship, positive registry/preparation record or competent acceptance.',
            'Document hashes/metadata and self-declared assistant activity prove neither human identity nor complete preparer scope; CE08 must include actual later proof authors and refresh dependent reviews before C.',
            'Same assistant preparation/review is not independent competent R06/R08 acceptance. Graph/schema-fragment checks are documentary; no product/component, registry codec, identity, crypto, image, claim or protocol execution.',
            'CE01/CE02 competent adoption and all resource/atomicity/final-evidence/admission gates remain pending. No authority, enrollment, contact, quota or rebind follows.'],
        next_scope='CE03 can proceed as a documentarily reviewed provisional missing-identity dossier. A separately requested CE04 documentary preparation is possible; no source-to-image fact, runtime, author identity or build/enrollment/execution may be fabricated or inferred. CE08 finalization and actual competent prerequisites remain pending.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I204-audit.py',
            expected_result='PASS_STATIC_SOURCE_ONLY',runtime_harness='N/A: documentary JSON/Git/consumer/schema-fragment/dependency review; no product/components/identity/registry codec/crypto/image/claim/protocol execution.',
            over400_lines=True,reason='One pinned review unit with provisional/final phase reconstruction, non-authorship and schema/separation checks, guard restoration and preservation evidence; overage reported.'),
        publication=dict(commit_and_push_requested=True,publication_not_adoption_acceptance_or_authority=True))


def main():
    rec=reconstruct();assert rd(RECON)==rec and rd(REVIEW)==build_review(rec)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published504'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==509
    seal=rd(SEAL);assert seal['schema']=='d5.i204-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published509']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['CE03_accepted','actual_actor_registry_created','actual_registry_finalized','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I204',new_blocking_documentary_findings=0,
        CE03_provisional_documentarily_confirmed=True,CE03_accepted=False,actual_actor_registry_created=False,actual_registry_finalized=False,
        historical_pins=817,prior_published_files_preserved=509,new_files=5,actual_evidence_accepted=0,independent_acceptance=False,
        product_or_components_executed=0,quotas_changed=False,rebind_applied=False,resource_obligations_closed=0,
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
