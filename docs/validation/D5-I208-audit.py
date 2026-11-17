#!/usr/bin/env python3
"""I208 documentary caller/capability review; no product/backend/components."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='528f4ae4bae9ddcf5fe4ed55464962817610da68'
DOS=P+'D5-I193-CE05-CALLER-CONSTRUCTOR-DOMAIN-CANDIDATE.json'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json';CHECK=P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json';PACK=P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CE04=P+'D5-I193-CE04-IMAGE-SOURCE-BASELINE-CANDIDATE.json'
PRIOR_AUDIT=P+'D5-I207-audit.py';PRIOR_PREP=P+'D5-I207-preparation-review.json';PRIOR_SEAL=P+'D5-I207-integrity.json'
PRIOR_DOC='docs/design/D5-I207-CE05-CALLER-CONSTRUCTOR-DOMAIN.md';PRIOR_FILES={DOS,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON=P+'D5-I208-I207-source-reconstruction.json';REVIEW=P+'D5-I208-I207-documentary-review.json'
AUDIT=P+'D5-I208-audit.py';SEAL=P+'D5-I208-integrity.json';DOC='docs/design/D5-I208-I207-CE05-REVIEW.md'
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
    target=ROOT/DOS;existing=[ROOT/s['candidate_dossier_path'] for s in plan['steps'][:4]]
    missing=ROOT/plan['steps'][5]['candidate_dossier_path'];original=Path.exists
    assert git('ls-tree','--name-only',previous['BASE'],'--',DOS)==''
    assert git('ls-tree','--name-only',BASE,'--',DOS)==DOS
    assert target.exists() and all(p.exists() for p in existing) and not missing.exists()
    with previous['predecessor_CE05_presence_as_of_base']():
        assert not target.exists() and all(p.exists() for p in existing) and not missing.exists()
    assert Path.exists is original and target.exists()
    class DocumentaryProbe(Exception):pass
    try:
        with previous['predecessor_CE05_presence_as_of_base']():
            assert not target.exists()
            raise DocumentaryProbe()
    except DocumentaryProbe:pass
    else:raise AssertionError('Expected documentary exception not raised')
    assert Path.exists is original and target.exists() and all(p.exists() for p in existing) and not missing.exists()
    return dict(CE05_absent_in_preparation_base_verified=True,CE05_present_in_review_base_verified=True,
        exact_CE05_query_only=True,CE01_to_CE04_existing_and_CE06_missing_preserved=True,
        restored_after_success=True,restored_after_exception=True,prior_publication_mains_run=False)


def reconstruct():
    d=rd(DOS);plan=rd(PLAN);spec=rd(SPEC);defs=rd(PACK)['$defs'];step=plan['steps'][4]
    pins={**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==837;verify_git_blobs(pins)
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));assert previous['build_review']()==rd(PRIOR_PREP)
    guard=review_presence_guard(previous,plan)
    assert step['id']=='CE05' and step['depends_on']==['CE04']
    assert d['required_evidence']==step['required_evidence'] and len(d['required_evidence'])==3
    assert d['planned_acceptance_checks']==step['acceptance_checks'] and len(d['planned_acceptance_checks'])==2
    assert d['authorization_boundary']==step['authorization_boundary']
    assert d['contract_rules']==step['contract_rules']==['K02','K06','K07','K08','K09','K15']
    names=['CE05','CE06','CE07','CE08','CE09','CE10','CE12'];consumers={s:[] for s in names};rules={r:{} for r in d['contract_rules']}
    for r in d['caller_constructor_requirements']:
        c=r['consumer_step'];assert c in consumers;consumers[c].append(r['id'])
        for k in r['contract_rules']:rules[k].setdefault(c,[]).append(r['id'])
        for k in ['actual_provider_identity','actual_provider_locator','actual_body_sha256','actual_body_bytes','actual_appointment','actual_acceptance_record']:assert r[k] is None
        assert r['status']=='MISSING_NOT_EVALUATED' and not r['accepted'] and not r['contact_authorized_now']
    assert consumers==dict(CE05=['CC%02d'%i for i in range(1,7)],CE06=['CC07'],CE07=['CC08'],CE08=['CC09'],CE09=['CC10'],CE10=['CC11'],CE12=['CC12'])
    phases=d['step_obligation_boundary'];graph={s['id']:s['depends_on'] for s in plan['steps']};closure=ancestors(graph)
    for name,ids in consumers.items():
        assert phases[name]['requirement_ids']==ids and phases[name]['required_step_ids']==graph[name]
        assert not phases[name]['actual_acceptance'] and not phases[name]['current_execution_authorized']
        assert phases[name]['actual_dossier_created']==(name=='CE05')
    assert closure['CE05']=={'CE01','CE02','CE03','CE04'}
    assert not set(names[1:])&closure['CE05']
    assert graph['CE08']==['CE02','CE03','CE04','CE05','CE06','CE07'] and graph['CE09']==['CE08']
    assert graph['CE10']==['CE02','CE08','CE09'] and graph['CE12']==['CE11'] and 'CE12' not in closure['CE11']
    assert phases['CE08']['final_record_order']==plan['steps'][7]['record_families']
    assert phases['CE12']['external_prerequisites_for_receipt']==plan['closure_boundaries']['external_prerequisites_for_receipt']
    assert phases['CE12']['no_claim_or_spawn_before_full_admission_and_separate_authorization'] and phases['CE12']['CE11_does_not_depend_on_CE12']
    order=ancestors(spec['record_order'])
    assert {'ACTOR_REGISTRY','IMAGE_MANIFEST'}<=order['CALLER_IDENTITY'] and 'CALLER_IDENTITY' in order['PLATFORM_CUSTODY']
    assert 'PLATFORM_CUSTODY' in order['C_CONTEXT'] and {'C_CONTEXT','BUNDLE'}<=order['EXTERNAL_CURRENT_MAPPING']
    assert {'EXTERNAL_CURRENT_MAPPING','FINAL_ROOT'}<=order['ATOMIC_CLAIM'] and 'ATOMIC_CLAIM' in order['LAUNCH_RECEIPT']
    policy=d['identity_and_capability_policy']
    for k in ['human_requester_and_software_principal_namespaces_separate','authentic_prior_actor_image_domain_constructor_provenance_required',
        'UID_PID_fd_env_module_cwd_key_hash_or_appointment_alone_is_not_capability','literal_is_schema_policy_not_issued_permission',
        'future_bundle_may_not_supply_sole_prior_authentication','no_extra_channel_fd_argv_helper_file_env_or_attestation_implicit',
        'expanded_real_backend_requires_rejection_or_separately_reviewed_versioned_scope_cost_work','no_C_or_bundle_hash_field_added_to_caller_schema_or_wire']:assert policy[k] is True
    assert not policy['actual_backend_or_principal_selected']
    assert [policy['actual_C_projection_consumer'],policy['actual_unique_mapping_consumer'],policy['actual_protected_construction_consumer']]==['CE09','CE10','CE12']
    tp=plan['bindings']['bootstrap_contract']['path'];gp=plan['bindings']['bootstrap_grammar']['path'];transport=rd(tp);grammar=rd(gp);t=d['inherited_transport_policy']
    assert t['contract_binding']==pin(tp) and t['grammar_binding']==pin(gp)
    for new,old in [('endpoint_ownership_requirements','endpoint_ownership'),('argv_and_channel_checks_requirement','argv_and_channel_checks'),
        ('trust_boundary_requirements','trust_boundary'),('one_use_and_permissions_requirements','one_use_and_permissions')]:assert t[new]==transport[old]
    assert t['grammar_transport_limits']==grammar['transport_limits'] and t['grammar_permissions']==grammar['permissions']
    assert t['explicit_control_pipe_count']==2 and t['observed_worker_operand_count']==6 and t['actual_fd_PID_UID_domain_values'] is None
    assert not t['actual_channel_origin_or_descriptor_ownership_verified'] and not t['actual_process_or_endpoint_probe_performed']
    assert t['worker_intrinsic_origin_is_not_received_as_new_mapping_or_receipt']
    assert t['grammar_permissions']['worker_functional_import_after']=='W_RELEASED only'
    for k in ['additional_control_pipes','additional_processes','additional_repository_inputs']:assert t['grammar_transport_limits'][k]==0
    cross=d['cross_record_and_mapping_policy'];assert cross['caller_projection']==spec['projection']
    assert cross['exact_C_rule']==next(r['rule'] for r in spec['rules'] if r['id']=='K08')
    assert cross['unique_mapping_rule']==next(r['rule'] for r in spec['rules'] if r['id']=='K09')
    assert cross['requester_projection_equality']=='C.runtime_requester_id == caller.accountable_requester_actor_id'
    assert cross['protection_domain_equality']=='platform.domain_id == caller.protection_domain_id'
    assert not cross['actual_C_or_mapping_available'] and cross['no_retrospective_trust_from_future_bundle']
    actual=d['actual_caller_state'];false_fields={'actual_caller_or_backend_selected','actual_caller_or_actor_enrolled',
        'actual_constructor_or_channel_created','actual_identity_or_custody_verified','actual_final_caller_record_frozen',
        'actual_mapping_or_claim_verified','actual_functional_execution_permitted'}
    assert len(actual)==31
    for k,v in actual.items():
        if k in false_fields:assert v is False
        else:assert v is None
    schema=d['schema_obligations'];assert len(schema['definitions'])==4
    for row in schema['definitions']:assert row['schema_fragment']==defs[row['name']]
    fields=defs['caller_identity']['required'];assert len(fields)==13 and defs['caller_identity']['additionalProperties'] is False
    assert not {'C','Q','bundle_sha256','launch_receipt','future_root_sha256'}&set(fields)
    literal=defs['caller_identity']['properties']['permission']['const']
    assert literal==policy['original_caller_permission_literal']=='BOOTSTRAP_CUSTODY_ONLY_FULL_ROOT_AND_SEPARATE_REQUEST_REQUIRED'
    assert schema['final_caller_body_cap_bytes']==spec['record_caps_bytes']['caller_identity']==8192
    assert schema['dossier_is_not_positive_caller_identity'] and schema['body_cap_not_applied_to_documentary_wrapper']
    assert schema['actual_schema_codec_hash_or_crypto_validation']=='NOT_RUN_NO_ACTUAL_BODY' and schema['actual_final_body_validation_consumer_step']=='CE08'
    gate=next(g for g in rd(CHECK)['family_gates'] if g['family']=='caller_identity')
    assert gate['candidate_step_ids']==['CE05','CE08'] and gate['final_record_freeze_step']=='CE08' and not gate['accepted']
    assert d['inherited_scope_boundaries']==rd(CE04)['inherited_scope_boundaries'] and d['preserved_negative_gates']==rd(CE04)['preserved_negative_gates']
    assert not d['dependency_gate']['actual_dependency_satisfied'] and not d['dependency_gate']['competent_CE04_acceptance']
    assert [r['id'] for r in d['role_scope_matrix']]==['R01','R02','R06','R08']
    for r in d['role_scope_matrix']:assert r['assigned_person'] is None and not r['accepted_appointment'] and r['current_actions_authorized']==[]
    assert len(d['permission_boundary']['authorized_documentary_actions'])==4 and len(d['permission_boundary']['denied_action_classes'])==14
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][5:])
    assert d['decision']==plan['decision'] and d['E06']==plan['E06']
    return dict(schema='d5.i208-i207-source-reconstruction.v1',increment='I208',date='2026-11-17',base_commit=BASE,
        input_pins=pins,method='Fresh Git blobs, independent consumer/rule incidence and I193/I191 ancestor review, direct identity-versus-capability and I189 transport/permission comparison; predecessor documentary build reproduced without publication main.',
        requirement_consumers=consumers,rule_consumers=rules,historical_presence_guard=guard,
        phase_review=dict(I193_dependency_graph_acyclic=True,CE05_ancestors=sorted(closure['CE05']),
            no_reverse_CE05_dependency_on_later_phases=True,final_caller_freeze='CE08',actual_C_projection='CE09',
            actual_unique_mapping='CE10',actual_protected_construction='CE12',no_CE11_receipt_dependency=True,
            I191_antecedent_order_acyclic=True,caller_before_platform_before_C=True,external_mapping_and_root_before_claim=True),
        identity_capability_transport_review=dict(human_and_software_principal_distinct=True,self_assertions_or_appointments_not_capability=True,
            bootstrap_permission_is_schema_policy_not_issued_authority=True,actual_caller_backend_or_capability_supplied=False,
            existing_explicit_control_pipes=2,observed_worker_operands=6,additional_process_pipe_repository_input_limits=0,
            full_I189_custody_checks_preserved=True,worker_functional_gate='W_RELEASED',actual_endpoint_probe_or_origin_verification=False,
            no_new_mapping_receipt_wire_or_argv=True,no_retrospective_trust_from_future_bundle=True),
        preserved_scope=dict(documentary_sources=15,schema_definitions=4,closed_caller_required_fields=fields,
            final_caller_candidate_cap=8192,actual_final_body_or_codec_schema_crypto_validation=False,unassigned_review_slots=4,
            competent_CE04_dependency_satisfied=False,other_planned_dossiers_absent=7,prior_documentary_rejection_checks_reproduced=10,
            caps_numeric_permissions_role_policy_and_negative_gates_unchanged=True,original_I207_preparation_preserved=True,prior_publication_mains_run=False),
        verdict=dict(new_blocking_documentary_findings=0,CE05_documentary_baseline_confirmed=True,CE05_accepted=False,
            actual_caller_identity_record_created=False,actual_caller_record_finalized=False,actual_caller_or_backend_selected=False,
            actual_capability_or_functional_permission_issued=False,adopted=False,implemented=False,independent_acceptance=False,
            actual_evidence_accepted=0,resource_obligations_closed=0,product_or_components_executed=0))


def build_review(rec):
    d=rd(DOS);plan=rd(PLAN)
    checks=[
        ('E01','Software principal/accountable human and genuine actor/image/domain/constructor enrollment','PASS_REQUIRED_PROVENANCE_MISSING_NOT_IDENTITIES_OR_CAPABILITY'),
        ('E02','Concrete constructor/loader/privilege/isolation and exclusive I189 endpoint custody','PASS_REQUIREMENT_NOT_MECHANISM_OR_RUNTIME_PROOF'),
        ('E03','fd/PID/UID/env/module/cwd assertions cannot select caller/image','PASS_NO_SELF_ASSERTED_OR_MUTABLE_TRUST'),
        ('A01','Accountable requester and image/domain/constructor relations project to later exact C','PASS_DECLARED_CE09_RELATIONS_NOT_REAL_C_OR_MAPPING'),
        ('A02','Additional backend mechanisms reject unchanged route or require versioned scope/cost review','PASS_NO_IMPLICIT_CHANNEL_FD_ARGV_HELPER_OR_QUOTA_EXPANSION'),
        ('B01','No caller/backend selected/enrolled; CE04 competent dependency remains pending','PASS_NO_INFRASTRUCTURE_OR_APPOINTMENT_FABRICATION'),
        ('K02','Canonical humans separate from software principal; all identity evidence required','PASS_POLICY_NOT_ACTUAL_IDENTITY_RESOLUTION'),
        ('K06','Prior genuine caller/actor/image/domain/constructor facts not borrowed from future bundle','PASS_ANTECEDENT_POLICY_NOT_ACCEPTED_CALLER_OR_EXECUTION'),
        ('K07','First-entry/loader/channel capability before untrusted code, no hidden transport','PASS_CUSTODY_POLICY_NOT_PLATFORM_ENFORCEMENT_PROOF'),
        ('K08','Final record cross-relations/freeze/C projection remain CE08/CE09','PASS_PHASE_BOUNDARIES_NOT_ACTUAL_C_OR_RECORD_HASHES'),
        ('K09','Unique current external mapping CE10 and intrinsic protected construction later','PASS_NO_RETROSPECTIVE_TRUST_OR_WORKER_MAPPING_FRAME'),
        ('K15','Full lookup/freshness/identity/copies/crypto/native/IO/registry/receipt costs still inside phases/global join','PASS_UNWAIVED_RESOURCE_OBLIGATION_NOT_HEAP_CPU_OR_900_PROOF')]
    effect={**d['current_effect'],'CE05_documentary_review_completed':True,'CE05_documentary_confirmation':True,
        'CE05_documentary_revision_required':False,'actual_capability_or_functional_permission_issued':False}
    return dict(schema='d5.i208-i207-documentary-review.v1',increment='I208',date='2026-11-17',timezone='Europe/Madrid',base_commit=BASE,
        proposal=d['proposal_id'],profile_id=d['profile_id'],step='CE05',
        status='CE05_DOCUMENTARY_BASELINE_CONFIRMED_CALLER_CONSTRUCTOR_DOMAIN_MISSING_NOT_FROZEN_NOT_ACCEPTED_NOT_ADMITTED',
        reconstruction=pin(RECON),provenance=dict(reviewer='Same Codex assistant/chat that prepared I207 and earlier candidates',
            methodological_reconstruction_separate=True,actor_independent=False,organizationally_independent=False,
            competent_R01_R02_R06_review=False,separate_R08_acceptance=False,independent_acceptance=False),
        findings=[],checks=[dict(id=i,scope=s,result=r) for i,s,r in checks],
        evidence=[pin(DOS,'/identity_and_capability_policy'),pin(DOS,'/inherited_transport_policy'),pin(DOS,'/cross_record_and_mapping_policy'),
            pin(DOS,'/step_obligation_boundary'),pin(DOS,'/actual_caller_state'),pin(PLAN,'/steps/4'),pin(PLAN,'/closure_boundaries'),
            pin(CHECK,'/family_gates/3'),pin(PACK,'/$defs/caller_identity'),pin(SPEC,'/record_order')],
        verdict=rec['verdict'],current_effect=effect,decision=plan['decision'],E06=plan['E06'],
        limitations=['Exact documentary caller baseline only: no principal/requester/constructor/domain/endpoints/enrollment, capability, actual record, C/mapping, claim or worker supplied or accepted.',
            'I189/schema/permission literals, descriptor counts and document hashes are requirements, not process-origin evidence or functional execution authority. No probe or identity resolution performed.',
            'Same assistant preparation/review is not independent competent R01/R02/R06/R08 acceptance. All CE01-CE05 competent prerequisites, platform/resources/freeze/final evidence/admission remain pending.',
            'No selection/enrollment/contact, build/import/measurement/process/component/crypto/codec/claim execution, authority/quota/rebind or D5 release follows.'],
        next_scope='CE05 can proceed as a documentarily reviewed missing-caller baseline. A separately requested CE06 documentary preparation is possible; do not invent platform/clock/ledger guarantees or run probes/claim/replay/process work. All authentic evidence and competent acceptances remain pending.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I208-audit.py',
            expected_result='PASS_STATIC_SOURCE_ONLY',runtime_harness='N/A: documentary JSON/Git/capability-policy/transport/schema-fragment/phase review; no backend selection/enrollment/process/probe/product/components/crypto/codec/claim/protocol execution.',
            over400_lines=True,reason='One pinned identity/capability/transport/phase review unit with independent antecedent checks, restored historical guard and preservation evidence; overage reported.'),
        publication=dict(commit_and_push_requested=True,publication_not_adoption_acceptance_or_authority=True))


def main():
    rec=reconstruct();assert rd(RECON)==rec and rd(REVIEW)==build_review(rec)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published524'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==529
    seal=rd(SEAL);assert seal['schema']=='d5.i208-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published529']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['CE05_accepted','actual_caller_identity_record_created','actual_caller_record_finalized','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I208',new_blocking_documentary_findings=0,
        CE05_documentary_baseline_confirmed=True,CE05_accepted=False,actual_caller_identity_record_created=False,actual_caller_record_finalized=False,
        historical_pins=837,prior_published_files_preserved=529,new_files=5,actual_evidence_accepted=0,independent_acceptance=False,
        product_or_components_executed=0,quotas_changed=False,rebind_applied=False,resource_obligations_closed=0,
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
