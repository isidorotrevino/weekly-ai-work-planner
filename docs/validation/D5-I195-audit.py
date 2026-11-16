#!/usr/bin/env python3
"""CE01 documentary checks only. No product/component, crypto, image or protocol execution."""
import hashlib
import io
import json
import runpy
import subprocess
from contextlib import contextmanager
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='f0d6980aa8c5da04821e890dec4910783780b4b9'
DOS=P+'D5-I193-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE.json'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
CHECK=P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
OLD_AUDIT=P+'D5-I194-audit.py';OLD_SEAL=P+'D5-I194-integrity.json'
OLD_RECON=P+'D5-I194-I193-source-reconstruction.json'
OLD_REVIEW=P+'D5-I194-I193-documentary-review.json'
OLD_DOC='docs/design/D5-I194-I193-CUSTODY-EVIDENCE-PLAN-REVIEW.md'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK=P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
S01=P+'D5-I179-S01-ROLES-SCOPE-GATES.json'
CERT=P+'D5-I122-CAPACITY-CERTIFICATE.json'
AUDIT=P+'D5-I195-audit.py';PREP=P+'D5-I195-preparation-review.json'
SEAL=P+'D5-I195-integrity.json';DOC='docs/design/D5-I195-CE01-SCOPE-DECISION-BOUNDARY.md'
FILES={DOS,AUDIT,PREP,SEAL,DOC}
PRIOR_FILES={OLD_AUDIT,OLD_SEAL,OLD_RECON,OLD_REVIEW,OLD_DOC}
ALLOWED={'READ_REPOSITORY_DOCUMENTARY_SOURCE_AND_GIT_HASHES','PREPARE_THIS_CE01_DOCUMENTARY_DOSSIER',
         'RUN_THIS_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_REVIEWABLE_DOCUMENTARY_UNIT'}
DENIED={'COMPETENT_POLICY_OR_S01_ADOPTION','ACTOR_KEY_ANCHOR_CALLER_SERVICE_ENROLLMENT',
        'PRIVATE_KEY_GENERATION_OR_SIGNING','LIVE_CRYPTO_VERIFICATION_OR_RUNTIME_ATTESTATION',
        'IMAGE_BUILD_OR_SOURCE_IMPLEMENTATION_CHANGE','PLATFORM_PROBE_MEASUREMENT_OR_SERVICE_CONFIGURATION',
        'PRODUCT_OR_COMPONENT_EXECUTION','CLAIM_NONCE_CONSUMPTION_OR_REPLAY_TEST',
        'WORKER_OR_CONTROL_CHANNEL_CREATION','AUTHORITY_ROOT_C_Q_ISSUANCE_OR_CAPTURE_DESTINATION_CREATION',
        'PROVIDER_OR_REVIEWER_CONTACT','ACTIVE_SCHEMA_CONTRACT_GATE_OR_CAPTURE_INPUT_REBIND',
        'QUOTA_RESERVE_OR_BUDGET_CHANGE','RESOURCE_OR_D5_CLOSURE'}


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pin(p):return dict(path=p,sha256=sha(p))


@contextmanager
def predecessor_presence_as_of_base():
    """Only inherited absent-CE01 assertions see the proven historical presence state.

    No predecessor publication main runs. Current dossier, all other paths, bytes,
    hashes and authority checks remain separately checked against their real state.
    The override is synchronous, exact-path-only, and restored even on failure.
    """
    assert git('ls-tree','--name-only',BASE,'--',DOS)==''
    target=ROOT/DOS;real_exists=Path.exists;assert real_exists(target)
    def base_exists(path):
        return False if path==target else real_exists(path)
    Path.exists=base_exists
    try:yield
    finally:Path.exists=real_exists
    assert target.exists()


def check_pins(pins):
    request=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=request))
    for p,h in sorted(pins.items()):
        head=stream.readline().decode().split();assert len(head)==3 and head[1]=='blob',p
        body=stream.read(int(head[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    assert stream.read()==b''


def build_review():
    d=rd(DOS);plan=rd(PLAN);step=plan['steps'][0];spec=rd(SPEC)
    pins={**rd(OLD_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==772 and d['input_pins']==pins;check_pins(pins)
    with predecessor_presence_as_of_base():
        previous=runpy.run_path(str(ROOT/OLD_AUDIT));rec=previous['reconstruct']()
        assert rec==rd(OLD_RECON) and previous['build_review'](rec)==rd(OLD_REVIEW)
    assert d['schema']=='d5.i195-ce01-scope-decision-boundary-candidate.v1'
    assert d['base_commit']==BASE and d['increment']=='I195' and d['step']=='CE01'
    assert d['kind']=='DOCUMENTARY_DOSSIER_NOT_I191_RECORD_NOT_AUTHORITY'
    assert d['status']=='CE01_DOCUMENTARY_CANDIDATE_PREPARED_NOT_ADOPTED_NOT_ACCEPTED_NOT_ADMITTED'
    assert d['proposal_id']==plan['proposal_id'] and d['profile_id']==plan['profile_id']
    assert step['id']=='CE01' and step['candidate_dossier_path']==DOS
    assert d['plan_binding']==dict(**pin(PLAN),json_pointer='/steps/0',step_id='CE01',planned_path=DOS)
    assert d['checklist_binding']==pin(CHECK) and d['last_plan_review']==pin(OLD_REVIEW)
    assert d['required_evidence']==step['required_evidence']
    assert d['planned_acceptance_checks']==step['acceptance_checks']
    assert d['contract_rules']==step['contract_rules']==['K01','K10','K12','K15','K16']
    refs={PLAN,CHECK,OLD_REVIEW,SPEC,PACK,S01,CERT,P+'D5-I192-I191-documentary-review.json',
          P+'D5-I193-preparation-review.json',*{b['path'] for b in spec['bindings'].values()}}
    expected=[dict(**pin(p),serialized_file_bytes=(ROOT/p).stat().st_size,
        availability='EXISTING_DOCUMENTARY_BYTES_PINNED_NOT_ACTUAL_EXTERNAL_EVIDENCE') for p in sorted(refs)]
    assert d['documentary_inventory']==expected and len(refs)==14
    for b in spec['bindings'].values():assert sha(b['path'])==b['sha256']
    roles=d['role_scope_matrix'];source_roles=rd(S01)['role_authority_validity_matrix']
    assert len(roles)==8 and [r['id'] for r in roles]==[r['id'] for r in source_roles]
    for r,s in zip(roles,source_roles):
        for k in ['id','role','required_decision_scopes','separation_required_from']:assert r[k]==s[k]
        for k in ['assigned_person','canonical_actor_id','appointment_or_authority_record','competence_evidence','key_or_trust_binding','validity']:assert r[k] is None
        assert r['CE01_responsibilities'] and not r['accepted_appointment'] and r['current_actions_authorized']==[]
    producer=d['producer'];assert producer['role']=='DOCUMENTARY_PREPARER' and producer['canonical_human_actor_id'] is None
    for k in ['accepted_external_identity','actor_independent','organizationally_independent','independent_acceptance']:assert producer[k] is False
    permissions=d['permission_matrix'];assert len(permissions)==18
    assert {r['action'] for r in permissions if r['authorized_now']}==ALLOWED
    assert {r['action'] for r in permissions if not r['authorized_now']}==DENIED
    for r in permissions:assert r['basis'] and r['grants_execution_or_custody'] is False
    proposals=d['decision_proposals'];assert [r['id'] for r in proposals]==['DCE01-%02d'%i for i in range(1,9)]
    for r in proposals:
        assert r['proposal'] and r['status']=='PROPOSED_NOT_ADOPTED' and not r['adopted']
        for k in ['adopting_person','authority_record','signature_or_trust_record']:assert r[k] is None
    external=d['external_evidence_requirements'];assert [r['id'] for r in external]==['X%02d'%i for i in range(1,11)]
    assert set().union(*(set(r['downstream_steps']) for r in external))=={'CE%02d'%i for i in range(1,13)}
    for r in external:
        for k in ['actual_provider_identity','actual_provider_locator','actual_body_sha256','actual_body_bytes','actual_appointment']:assert r[k] is None
        assert r['required_provider_kind'] and r['required_actual_evidence'] and r['responsible_review_roles']
        assert set(r['responsible_review_roles'])<={s['id'] for s in roles}
        assert r['availability']=='NOT_SUPPLIED_IN_THIS_SCOPE' and not r['accepted'] and not r['contact_authorized_now']
    availability=d['source_image_record_availability']
    slots=rd(P+'D5-I181-F179-01-GATE-ORDER-PROPOSAL.json')['successor_source_scope']['slots']
    assert len(slots)==6 and [r['path'] for r in availability['successor_sources']]==slots
    for r in availability['successor_sources']:
        assert not (ROOT/r['path']).exists() and r['availability']=='NOT_SUPPLIED_NOT_CREATED'
        assert r['actual_sha256'] is None and r['actual_bytes'] is None and not r['accepted']
    assert availability['six_source_design_cap_bytes']==262144
    for k in ['actual_image_id','actual_image_sha256','actual_runtime_identity_sha256']:assert availability[k] is None
    families=availability['I191_record_families'];assert [r['family'] for r in families]==spec['record_families'] and len(families)==8
    for r in families:assert not r['body_available'] and r['actual_sha256'] is None and r['actual_bytes'] is None and not r['accepted']
    assert availability['no_inference_from_existing_schema_or_I122_source_hashes']
    cert=rd(CERT);fields=['status','CP03_global_resolved','CP07_exact_admission_resolved','correlated_atomicity_verified','component_validation']
    gates=d['preserved_negative_gates'];assert [r['id'] for r in gates]==fields
    for r in gates:assert r['source']==pin(CERT) and r['json_pointer']=='/'+r['id'] and r['observed_value']==cert[r['id']]
    assert [cert[k] for k in fields]==['IMPLEMENTED_NOT_ADMITTED',True,False,False,'NOT_RUN']
    bounds=d['inherited_scope_boundaries']
    for new,old,n in [('S01_exclusions','S01_actor_exclusions',8),('extra_custody_separation','extra_custody_separation',4),('full_CP07_conditions','existing_full_CP07_conditions',9)]:
        assert bounds[new]==spec['inheritance'][old] and len(bounds[new])==n
    assert bounds['protocol_and_output_caps']==dict(C_body=8192,Q_body=2048,I_A_L_frame_with_LF=512,
        explicit_control_pipes=2,observed_worker_operands=6,payload_members=494,physical_input_paths=496,
        Reader_design_bytes_conditional=266693693,context_bytes=12582912,launch_bytes=12582912,
        bundle_cap=262144,bundle_upper_conditional_on_nested_caps=221644)
    assert bounds['numeric_candidates_unchanged']==rd(P+'D5-I122-CAPACITY-CONTRACT.json')['numeric_candidates']
    for k in ['current_successor_capacity_compatibility_or_service_verified','CE11_prelaunch_depends_on_CE12','receipt_authorized_now']:assert bounds[k] is False
    dispositions=d['review_dispositions']
    for k in ['primary_R06','separate_R08']:
        assert dispositions[k]==dict(person=None,appointment=None,authority=None,decision='PENDING_NOT_ACCEPTED')
    assert dispositions['no_signed_scope_or_role_acceptance_created']
    readiness=d['missing_facts_and_readiness'];assert readiness['candidate_documentary_ready_for_review']
    assert not readiness['competent_adoption_ready'] and not readiness['CE01_accepted'] and len(readiness['missing'])==4
    assert readiness['not_authorized_to_fill_by_execution_or_contact']
    historical=d['historical_scope'];assert historical['plan_and_review_records_preserved']
    assert historical['I193_plan_saved_candidate_dossier_created_value'] is False
    assert historical['I193_plan_state_is_historical_and_unchanged'] and historical['current_CE01_dossier_created']
    assert not historical['other11_dossiers_created'] and historical['no_accepted_step_or_live_binding_transition']
    assert not step['candidate_dossier_created'] and not step['accepted']
    others=[s['candidate_dossier_path'] for s in plan['steps'][1:]]
    assert len(others)==11 and all(not (ROOT/p).exists() for p in others) and (ROOT/DOS).exists()
    effect=d['current_effect']
    assert effect['CE01_documentary_candidate_prepared'] and effect['candidate_dossiers_prepared_this_increment']==1
    assert effect['actual_accepted_steps']==effect['actual_external_evidence_accepted']==effect['resource_obligations_closed']==0
    for k in ['CE01_accepted','adopted','implemented','S01_accepted','F179_01_resolved','independent_acceptance',
              'product_or_components_executed','active_schema_changed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert effect[k] is False
    assert effect['IR03']=='NOT_READY' and d['decision']==plan['decision'] and d['E06']==plan['E06']
    assert set(d['work_unit']['rollback_files'])==FILES
    assert d['work_unit']['verification_command']=='python3 docs/validation/D5-I195-audit.py'
    return dict(schema='d5.i195-preparation-review.v1',increment='I195',date='2026-11-16',base_commit=BASE,
        dossier=pin(DOS),input_pins=pins,status='DOCUMENTARY_CANDIDATE_PREPARED_ACTUAL_ACCEPTANCE_PENDING',
        provenance=dict(preparer='Same Codex assistant/chat',actor_independent=False,competent_R06_or_R08_acceptance=False),
        historical_replay=dict(base_CE01_path_absent_verified_with_git=True,only_exact_CE01_presence_query_projected=True,
            predecessor_bytes_unchanged=True,previous_reconstruction_and_review_reproduced=True,
            current_real_dossier_required_and_separately_checked=True,other_dossiers_absent=11),
        coverage=dict(required_evidence_items=len(step['required_evidence']),acceptance_checks=len(step['acceptance_checks']),
            contract_rules=step['contract_rules'],documentary_inputs=14,unassigned_roles=8,allowed_documentary_actions=4,
            denied_actions=14,unadopted_decision_proposals=8,missing_external_evidence_groups=10,
            missing_successor_sources=6,missing_actual_record_families=8,S01_exclusions=8,extra_custody_separations=4,
            CP03_only_inherited_I122_scope=True,CP07=False,correlated_atomicity=False,component_validation='NOT_RUN'),
        limitations=['Scope consistency and byte preservation only; no actual provider, appointment, authority, source/image/platform/resource evidence or acceptance.',
            'No product/component, image, crypto, claim, protocol or service execution. No contact, quota change or active rebind.',
            'Candidate readiness does not close CE01 or any later gate; competent separate R06/R08 adoption remains missing.'],
        current_effect=effect,decision=d['decision'],E06=d['E06'])


def main():
    assert rd(PREP)==build_review()
    prior=rd(OLD_SEAL);preserved={**prior['preserved_published459'],**prior['artifacts'],OLD_SEAL:sha(OLD_SEAL)}
    assert len(preserved)==464
    seal=rd(SEAL);assert seal['schema']=='d5.i195-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published464']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['CE01_accepted','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I195',CE01_candidate_prepared=True,
        CE01_accepted=False,historical_pins=772,prior_published_files_preserved=464,new_files=5,
        missing_external_evidence_groups=10,actual_evidence_accepted=0,independent_acceptance=False,
        product_or_components_executed=0,quotas_changed=False,rebind_applied=False,resource_obligations_closed=0,
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
