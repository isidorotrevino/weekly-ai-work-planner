#!/usr/bin/env python3
"""I206 documentary CE04 review: Git/JSON/phase math only, no components."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='240971a31dabb40d58fdc3c889583c3a6d6886ff'
DOS=P+'D5-I193-CE04-IMAGE-SOURCE-BASELINE-CANDIDATE.json'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json';CHECK=P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json';PACK=P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
SCOPE=P+'D5-I181-F179-01-GATE-ORDER-PROPOSAL.json';P02=P+'D5-I136-P02-documentary-review.json'
CE03=P+'D5-I193-CE03-HUMAN-IDENTITY-ROSTER-CANDIDATE.json'
PRIOR_AUDIT=P+'D5-I205-audit.py';PRIOR_PREP=P+'D5-I205-preparation-review.json';PRIOR_SEAL=P+'D5-I205-integrity.json'
PRIOR_DOC='docs/design/D5-I205-CE04-IMAGE-SOURCE-BASELINE.md';PRIOR_FILES={DOS,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON=P+'D5-I206-I205-source-reconstruction.json';REVIEW=P+'D5-I206-I205-documentary-review.json'
AUDIT=P+'D5-I206-audit.py';SEAL=P+'D5-I206-integrity.json';DOC='docs/design/D5-I206-I205-CE04-REVIEW.md'
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
    """Independent DFS of documentary prerequisites; no executable image/protocol."""
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
    target=ROOT/DOS;existing=[ROOT/s['candidate_dossier_path'] for s in plan['steps'][:3]]
    missing=ROOT/plan['steps'][4]['candidate_dossier_path'];original=Path.exists
    assert git('ls-tree','--name-only',previous['BASE'],'--',DOS)==''
    assert git('ls-tree','--name-only',BASE,'--',DOS)==DOS
    assert target.exists() and all(p.exists() for p in existing) and not missing.exists()
    with previous['predecessor_CE04_presence_as_of_base']():
        assert not target.exists() and all(p.exists() for p in existing) and not missing.exists()
    assert Path.exists is original and target.exists()
    class DocumentaryProbe(Exception):pass
    try:
        with previous['predecessor_CE04_presence_as_of_base']():
            assert not target.exists()
            raise DocumentaryProbe()
    except DocumentaryProbe:pass
    else:raise AssertionError('Expected documentary exception not raised')
    assert Path.exists is original and target.exists() and all(p.exists() for p in existing) and not missing.exists()
    return dict(CE04_absent_in_preparation_base_verified=True,CE04_present_in_review_base_verified=True,
        exact_CE04_query_only=True,CE01_CE02_CE03_existing_and_CE05_missing_preserved=True,
        restored_after_success=True,restored_after_exception=True,prior_publication_mains_run=False)


def reconstruct():
    d=rd(DOS);plan=rd(PLAN);spec=rd(SPEC);defs=rd(PACK)['$defs'];step=plan['steps'][3]
    pins={**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==827;verify_git_blobs(pins)
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));assert previous['build_review']()==rd(PRIOR_PREP)
    guard=review_presence_guard(previous,plan)
    assert step['id']=='CE04' and step['depends_on']==['CE03']
    assert d['required_evidence']==step['required_evidence'] and len(d['required_evidence'])==3
    assert d['planned_acceptance_checks']==step['acceptance_checks'] and len(d['planned_acceptance_checks'])==3
    assert d['authorization_boundary']==step['authorization_boundary']
    assert d['contract_rules']==step['contract_rules']==['K04','K05','K07','K15','K16']
    rows=d['image_source_requirements'];consumers={s:[] for s in ['CE04','CE05','CE06','CE07','CE08']}
    rules={r:{} for r in d['contract_rules']}
    for row in rows:
        consumer=row['consumer_step'];assert consumer in consumers;consumers[consumer].append(row['id'])
        for rule in row['contract_rules']:rules[rule].setdefault(consumer,[]).append(row['id'])
        for k in ['actual_provider_identity','actual_provider_locator','actual_body_sha256','actual_body_bytes','actual_appointment','actual_acceptance_record']:assert row[k] is None
        assert row['status']=='MISSING_NOT_EVALUATED' and not row['accepted'] and not row['contact_authorized_now']
    assert len(rows)==10 and consumers==dict(CE04=['IM%02d'%i for i in range(1,7)],CE05=['IM07'],CE06=['IM08'],CE07=['IM09'],CE08=['IM10'])
    phases=d['step_obligation_boundary'];graph={s['id']:s['depends_on'] for s in plan['steps']};closure=ancestors(graph)
    for name,ids in consumers.items():
        assert phases[name]['requirement_ids']==ids and phases[name]['required_step_ids']==graph[name]
        assert not phases[name]['actual_acceptance'] and not phases[name]['current_execution_authorized']
        assert phases[name]['actual_dossier_created']==(name=='CE04')
    assert closure['CE04']=={'CE01','CE02','CE03'}
    assert not {'CE05','CE06','CE07','CE08'}&closure['CE04']
    assert graph['CE05']==['CE04'] and graph['CE06']==['CE05'] and graph['CE07']==['CE04','CE05','CE06']
    assert graph['CE08']==['CE02','CE03','CE04','CE05','CE06','CE07'] and 'CE08' in closure['CE09']
    assert phases['CE04']['baseline_only_not_final_manifest'] and phases['CE04']['no_implicit_downstream_platform_resource_or_approval_acceptance']
    assert not phases['CE04']['downstream_proof_or_finalization_required_as_new_reverse_CE04_dependency']
    assert not phases['CE04']['final_registry_or_manifest_hash_required']
    order=['actor_registry','image_manifest','caller_identity','platform_custody']
    assert phases['CE08']['final_record_order']==plan['steps'][7]['record_families']==order
    assert phases['CE08']['actual_authors_and_complete_antecedents_before_freeze_required'] and phases['CE08']['final_manifest_before_C_required']
    source_ancestors=ancestors(spec['record_order'])
    assert 'ACTOR_REGISTRY' in source_ancestors['IMAGE_MANIFEST'] and 'IMAGE_MANIFEST' in source_ancestors['CALLER_IDENTITY']
    assert 'CALLER_IDENTITY' in source_ancestors['PLATFORM_CUSTODY'] and 'PLATFORM_CUSTODY' in source_ancestors['C_CONTEXT']
    gate=next(g for g in rd(CHECK)['family_gates'] if g['family']=='image_manifest')
    assert gate['candidate_step_ids']==['CE04','CE08'] and gate['final_record_freeze_step']=='CE08' and not gate['accepted']
    slots=rd(SCOPE)['successor_source_scope']['slots'];mapping=d['source_to_image_missing_inventory']
    assert len(slots)==len(mapping)==6 and [r['logical_path'] for r in mapping]==slots
    assert set(slots)==set(defs['source_bindings']['required'])==set(defs['image_manifest']['properties']['source_to_image']['required'])
    assert all(not (ROOT/p).exists() for p in slots)
    for row in mapping:
        for k in ['actual_source_sha256','actual_source_bytes','actual_image_member_id','actual_image_member_sha256','actual_image_representation','actual_mapping_evidence','actual_load_observation']:assert row[k] is None
        assert not row['loaded_by_membership_claimed'] and not row['accepted']
        if row['logical_path'].endswith('README.md'):assert row['required_representation']=='DOCUMENT' and row['allowed_representation_policy']==['DOCUMENT']
    scope=d['source_scope_policy'];assert scope['six_source_total_design_ceiling_bytes']==262144 and scope['actual_total_bytes'] is None
    assert scope['no_zero_sum_for_missing_sources'] and not scope['old_I122_proofs_transfer_to_successor']
    assert scope['no_silent_source_scope_enlargement'] and scope['no_unbound_repository_helper_outside_historical480_or_six_sources']
    runtime=d['runtime_identity_boundary'];assert runtime['image_bytes_digest_distinct_from_runtime_identity'] and runtime['image_bytes_digest_does_not_substitute_P02']
    assert runtime['P02_historical_review']==pin(P02) and runtime['historical_P02_subject']==rd(P02)['subject']
    assert runtime['historical_P02_runtime_verified']==rd(P02)['decision']['actual_runtime_identity_verified'] is False
    assert runtime['historical_P02_is_not_successor_runtime_evidence'] and runtime['existing_python_or_environment_not_target_runtime_evidence']
    assert not runtime['target_runtime_or_host_platform_sampled']
    policy_map={'profile_sha256':'profile02','protocol_schema_sha256':'protocol_schemas02','output_schema_sha256':'output_schemas',
        'transport_contract_sha256':'bootstrap_contract','transport_grammar_sha256':'bootstrap_grammar',
        'custody_schema_pack_sha256':'custody_schemas','custody_contract_sha256':'custody_contract'}
    assert len(d['compiled_policy_requirements'])==7
    for row in d['compiled_policy_requirements']:
        key=policy_map[row['image_field']];binding=plan['bindings'][key]
        assert row['documentary_binding']==pin(binding['path']) and row['required_candidate_policy_sha256']==binding['sha256']==sha(binding['path'])
        assert row['actual_compiled_policy_sha256'] is None and row['actual_independent_policy_selection_acceptance'] is None
        assert row['actual_compiled_value_verified'] is False
        prop=defs['image_manifest']['properties'][row['image_field']]
        if 'const' in prop:assert prop['const']==row['required_candidate_policy_sha256']
    noembed=d['no_self_embedding_policy'];assert noembed['own_future_image_manifest_bundle_digests_must_not_be_embedded']
    assert noembed['expected_image_identity_selected_by_external_accepted_custody'] and noembed['documentary_policy_pins_are_not_actual_compiled_or_image_evidence']
    assert noembed['actual_external_image_selection'] is None and not noembed['actual_source_or_image_no_self_embedding_verified']
    actual=d['actual_image_runtime_state'];false_fields={'actual_source_image_mapping_verified','actual_runtime_identity_verified',
        'actual_self_embedding_check_performed','actual_complete_dependency_closure_verified','actual_platform_enforcement_verified',
        'actual_resource_or_compatibility_join_verified','actual_final_manifest_frozen'}
    assert len(actual)==27
    for k,v in actual.items():
        if k in false_fields:assert v is False
        else:assert v is None
    schema=d['schema_obligations'];assert len(schema['definitions'])==6
    for row in schema['definitions']:assert row['schema_fragment']==defs[row['name']]
    assert schema['final_manifest_body_cap_bytes']==spec['record_caps_bytes']['image_manifest']==98304
    assert schema['dependency_min']==defs['image_manifest']['properties']['dependencies']['minItems']==1
    assert schema['dependency_max']==defs['image_manifest']['properties']['dependencies']['maxItems']==128
    assert schema['no_truncation_to_fit_cap'] and schema['dossier_is_not_positive_image_manifest'] and schema['body_cap_not_applied_to_documentary_wrapper']
    assert schema['actual_schema_codec_hash_or_crypto_validation']=='NOT_RUN_NO_ACTUAL_BODY' and schema['actual_final_body_validation_consumer_step']=='CE08'
    assert not d['dependency_gate']['actual_dependency_satisfied'] and not d['dependency_gate']['competent_CE03_acceptance']
    assert d['inherited_scope_boundaries']==rd(CE03)['inherited_scope_boundaries'] and d['preserved_negative_gates']==rd(CE03)['preserved_negative_gates']
    assert [r['id'] for r in d['role_scope_matrix']]==['R01','R06','R08']
    for r in d['role_scope_matrix']:assert r['assigned_person'] is None and not r['accepted_appointment'] and r['current_actions_authorized']==[]
    assert len(d['permission_boundary']['authorized_documentary_actions'])==4 and len(d['permission_boundary']['denied_action_classes'])==14
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][4:])
    assert d['decision']==plan['decision'] and d['E06']==plan['E06']
    return dict(schema='d5.i206-i205-source-reconstruction.v1',increment='I206',date='2026-11-17',base_commit=BASE,
        input_pins=pins,method='Fresh Git blobs, reverse requirement consumer/rule coverage, independent I193/I191 ancestor review, direct six-source/runtime/policy/schema distinctions and historical presence guard success/exception checks. Predecessor documentary preparation reproduced without publication main.',
        requirement_consumers=consumers,rule_consumers=rules,historical_presence_guard=guard,
        phase_review=dict(I193_dependency_graph_acyclic=True,CE04_ancestors=sorted(closure['CE04']),
            deferred_consumers={k:consumers[k] for k in ['CE05','CE06','CE07','CE08']},
            no_reverse_CE04_dependency_on_later_phases=True,CE08_final_record_order=order,CE09_requires_CE08=True,
            I191_antecedent_order_acyclic=True,baseline_does_not_discharge_caller_platform_resource_or_finalization=True),
        source_runtime_policy_review=dict(exact_missing_source_mapping_rows=6,README_document_constraint=True,no_load_claim_from_membership=True,
            actual_source_total_bytes=None,six_source_candidate_ceiling=262144,image_bytes_and_runtime_identity_distinct=True,
            historical_P02_runtime_verified=False,no_I122_P02_or_host_environment_proof_transfer=True,
            documentary_policy_requirements=7,actual_compiled_or_independently_selected_policy_values_available=False,
            own_future_image_manifest_bundle_embedding_forbidden=True,actual_no_self_embedding_verified=False,
            dependency_count_or_complete_closure_supplied=False,no_dependency_truncation=True),
        preserved_scope=dict(documentary_sources=17,schema_definitions=6,final_manifest_candidate_cap=98304,dependency_list_min=1,dependency_list_max=128,
            actual_final_body_or_codec_schema_crypto_validation=False,unassigned_review_slots=3,competent_CE03_dependency_satisfied=False,
            other_planned_dossiers_absent=8,prior_documentary_rejection_checks_reproduced=9,
            caps_numeric_permissions_role_policy_and_negative_gates_unchanged=True,original_I205_preparation_preserved=True,prior_publication_mains_run=False),
        verdict=dict(new_blocking_documentary_findings=0,CE04_documentary_baseline_confirmed=True,CE04_accepted=False,
            actual_image_manifest_created=False,actual_manifest_finalized=False,actual_runtime_identity_verified=False,
            actual_compiled_policy_verified=False,adopted=False,implemented=False,independent_acceptance=False,
            actual_evidence_accepted=0,resource_obligations_closed=0,product_or_components_executed=0))


def build_review(rec):
    d=rd(DOS);plan=rd(PLAN)
    checks=[
        ('E01','Actual six successor bodies/source root, external image digest and separate runtime/P02 evidence','PASS_DISTINCT_MISSING_FACTS_NOT_I122_TRANSFER'),
        ('E02','Six mappings, README DOCUMENT, full dependency/build/runtime/entry provenance','PASS_COMPLETE_REQUIREMENT_NOT_ACTUAL_MAPPING_OR_CLOSURE'),
        ('E03','Exact seven policy pins and no own future image/manifest/bundle digest embedding','PASS_DOCUMENTARY_POLICY_NOT_COMPILED_OR_EXTERNAL_IDENTITY_PROOF'),
        ('A01','Source-written/I122 not proof of changed successor;262144 ceiling not actual total','PASS_NO_PROOF_TRANSFER_OR_ZERO_SUM_FOR_MISSING_SOURCES'),
        ('A02','README/full bodies, no128-dependency truncation or hidden scope/helper expansion','PASS_REQUIRED_COMPLETENESS_NOT_MEMBERSHIP_OR_SIZE_PROOF'),
        ('A03','No build/import/measurement/code execution; provider facts must already genuinely exist','PASS_MISSING_EVIDENCE_WITH_NO_CURRENT_ACTION'),
        ('B01','Successor/image absent, dependent competent CE03 acceptance pending','PASS_NO_ARTIFACT_OR_DEPENDENCY_FABRICATION'),
        ('K04','Exact six rows and compiled policy/closure requirements','PASS_DECLARED_BASELINE_NOT_IMPLEMENTATION_OR_LOAD_PROOF'),
        ('K05','Image bytes versus full runtime identity, external expected identity/no self embedding','PASS_SEPARATE_COMMITMENTS_NOT_ACTUAL_IMAGE_OR_RUNTIME'),
        ('K07','Baseline entry versus deferred CE05 caller and CE06 complete enforcement','PASS_PHASE_BOUNDARIES_NOT_CONSTRUCTOR_OR_PLATFORM_PROOF'),
        ('K15','All per-attempt lookup/freshness/identity/crypto/copies/native/IO inside phases/global resource join','PASS_UNWAIVED_CE07_OBLIGATION_NOT_RESOURCE_OR_900_FIT'),
        ('K16','Caps98304/128 and other design limits unchanged; no active quota or positive manifest','PASS_CANDIDATE_LIMITS_NOT_ACTUAL_FIT')]
    effect={**d['current_effect'],'CE04_documentary_review_completed':True,'CE04_documentary_confirmation':True,
        'CE04_documentary_revision_required':False,'CE08_finalization_verified':False}
    return dict(schema='d5.i206-i205-documentary-review.v1',increment='I206',date='2026-11-17',timezone='Europe/Madrid',base_commit=BASE,
        proposal=d['proposal_id'],profile_id=d['profile_id'],step='CE04',
        status='CE04_DOCUMENTARY_BASELINE_CONFIRMED_SOURCE_IMAGE_RUNTIME_MISSING_NOT_FROZEN_NOT_ACCEPTED_NOT_ADMITTED',
        reconstruction=pin(RECON),provenance=dict(reviewer='Same Codex assistant/chat that prepared I205 and earlier candidates',
            methodological_reconstruction_separate=True,actor_independent=False,organizationally_independent=False,
            competent_R01_R06_review=False,separate_R08_acceptance=False,independent_acceptance=False),
        findings=[],checks=[dict(id=i,scope=s,result=r) for i,s,r in checks],
        evidence=[pin(DOS,'/source_to_image_missing_inventory'),pin(DOS,'/runtime_identity_boundary'),pin(DOS,'/compiled_policy_requirements'),
            pin(DOS,'/no_self_embedding_policy'),pin(DOS,'/step_obligation_boundary'),pin(DOS,'/actual_image_runtime_state'),
            pin(PLAN,'/steps/3'),pin(PLAN,'/steps/7'),pin(CHECK,'/family_gates/2'),pin(SPEC,'/record_order'),pin(P02,'/decision')],
        verdict=rec['verdict'],current_effect=effect,decision=plan['decision'],E06=plan['E06'],
        limitations=['Exact documentary baseline review only: no source/image/runtime/build/member mapping/compiled policy, accepted independent image selection, complete dependency body or final image manifest supplied.',
            'The seventeen documentary sources and their hashes are not actual successor or provider evidence. Historical I122/P02 and the auditor host runtime qualify no successor scope.',
            'Same assistant preparation/review is not competent independent R01/R06/R08 acceptance. Caller/platform/resources/final freeze and all actual CE01-CE04 prerequisites remain pending.',
            'Client date2026-11-17 is documentary metadata, not trusted runtime clock/currentness evidence. No execution/build/import/measurement, contact/enrollment, authority, quota, rebind or D5 release follows.'],
        next_scope='CE04 can proceed as a documentarily reviewed missing-evidence baseline. A separately requested CE05 documentary preparation is possible; no caller/backend/domain may be invented, selected or enrolled, and no constructor/build/process/component action is authorized. All genuine prerequisites remain pending.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I206-audit.py',
            expected_result='PASS_STATIC_SOURCE_ONLY',runtime_harness='N/A: documentary JSON/Git/mapping/policy/schema-fragment/graph review; no source creation/build/import/measurement/product/components/crypto/codec/claim/protocol execution.',
            over400_lines=True,reason='One pinned baseline/runtime-policy/phase review unit with precise no-proof-transfer scope, guard restoration and historical preservation; overage reported.'),
        publication=dict(commit_and_push_requested=True,publication_not_adoption_acceptance_or_authority=True))


def main():
    rec=reconstruct();assert rd(RECON)==rec and rd(REVIEW)==build_review(rec)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published514'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==519
    seal=rd(SEAL);assert seal['schema']=='d5.i206-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published519']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['CE04_accepted','actual_image_manifest_created','actual_manifest_finalized','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I206',new_blocking_documentary_findings=0,
        CE04_documentary_baseline_confirmed=True,CE04_accepted=False,actual_image_manifest_created=False,actual_manifest_finalized=False,
        historical_pins=827,prior_published_files_preserved=519,new_files=5,actual_evidence_accepted=0,independent_acceptance=False,
        product_or_components_executed=0,quotas_changed=False,rebind_applied=False,resource_obligations_closed=0,
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
