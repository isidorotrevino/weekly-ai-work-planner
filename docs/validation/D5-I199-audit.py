#!/usr/bin/env python3
"""I199 documentary missing-anchor dossier checks; no product/components/crypto."""
import hashlib
import io
import json
import runpy
import subprocess
from contextlib import contextmanager
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='8d63df3249a99c68cdab50849618357742b61726'
DOS=P+'D5-I193-CE02-ANCHOR-PROVENANCE-CANDIDATE.json'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
CHECK=P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK=P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CE01=P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
PRIOR_REVIEW=P+'D5-I198-I197-documentary-review.json'
PRIOR_RECON=P+'D5-I198-I197-source-reconstruction.json'
PRIOR_AUDIT=P+'D5-I198-audit.py';PRIOR_SEAL=P+'D5-I198-integrity.json'
PRIOR_DOC='docs/design/D5-I198-I197-CE01-02-REVIEW.md'
PRIOR_FILES={PRIOR_REVIEW,PRIOR_RECON,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
PREP=P+'D5-I199-preparation-review.json';AUDIT=P+'D5-I199-audit.py';SEAL=P+'D5-I199-integrity.json'
DOC='docs/design/D5-I199-CE02-ANCHOR-PROVENANCE.md'
FILES={DOS,PREP,AUDIT,SEAL,DOC}


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pin(p,q=''):return dict(path=p,sha256=sha(p),json_pointer=q)


@contextmanager
def predecessor_CE02_presence_as_of_base():
    """Exact new CE02 query only; historical source/trust checks remain unchanged.

    I198 expects CE02 absent at its published base. I195's nested historical CE01
    guard remains original. Current CE02 bytes/presence are checked outside this
    synchronous projection; no old publication main runs.
    """
    assert git('ls-tree','--name-only',BASE,'--',DOS)==''
    original=Path.exists;target=ROOT/DOS;assert original(target)
    def historical_exists(path):return False if path==target else original(path)
    Path.exists=historical_exists
    try:yield
    finally:Path.exists=original
    assert target.exists()


def verify_git_blobs(pins):
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()))
    for p,h in sorted(pins.items()):
        header=stream.readline().decode().split();assert len(header)==3 and header[1]=='blob',p
        body=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    assert stream.read()==b''


def build_review():
    d=rd(DOS);plan=rd(PLAN);step=plan['steps'][1];spec=rd(SPEC);defs=rd(PACK)['$defs'];ce01=rd(CE01)
    pins={**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==792 and d['input_pins']==pins;verify_git_blobs(pins)
    original_exists=Path.exists
    with predecessor_CE02_presence_as_of_base():
        previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));rec=previous['reconstruct']()
        assert rec==rd(PRIOR_RECON) and previous['build_review'](rec)==rd(PRIOR_REVIEW)
    assert Path.exists is original_exists and (ROOT/DOS).exists()
    assert d['schema']=='d5.i199-ce02-anchor-provenance-candidate.v1'
    assert d['increment']=='I199' and d['base_commit']==BASE and d['step']=='CE02'
    assert d['kind']=='MISSING_EVIDENCE_DOCUMENTARY_DOSSIER_NOT_ANCHOR_REGISTRY_NOT_TRUST_AUTHORITY'
    assert d['status']=='CE02_DOCUMENTARY_CANDIDATE_PREPARED_EVIDENCE_MISSING_NOT_ADOPTED_NOT_ACCEPTED_NOT_ADMITTED'
    assert d['plan_binding']==dict(**pin(PLAN,'/steps/1'),step_id='CE02',planned_path=DOS)
    assert step['id']=='CE02' and step['candidate_dossier_path']==DOS
    assert step['depends_on']==['CE01'] and step['record_families']==['anchor_registry']
    for k,s in [('required_evidence','required_evidence'),('planned_acceptance_checks','acceptance_checks'),
                ('authorization_boundary','authorization_boundary'),('contract_rules','contract_rules')]:assert d[k]==step[s]
    assert d['contract_rules']==['K01','K03','K11','K13','K16']
    gate=rd(CHECK)['family_gates'][0]
    assert gate['family']=='anchor_registry' and gate['body_cap_bytes']==65536 and gate['final_record_freeze_step']=='CE02'
    assert d['checklist_binding']==pin(CHECK,'/family_gates/0') and not gate['accepted']
    dep=d['dependency_gate'];assert dep['required_step']=='CE01' and dep['candidate']==pin(CE01)
    assert dep['last_documentary_review']==pin(PRIOR_REVIEW) and dep['F195_01_documentary_repair_confirmed_for_exact_CE01_candidate_02']
    assert dep['competent_CE01_acceptance'] is False and dep['actual_dependency_satisfied'] is False
    assert rd(PRIOR_REVIEW)['verdict']['F195_01_documentary_repair_confirmed_for_candidate_02'] is True
    assert rd(PRIOR_REVIEW)['verdict']['CE01_accepted'] is False
    refs={PLAN,CHECK,SPEC,PACK,CE01,PRIOR_REVIEW,P+'D5-I122-CAPACITY-CERTIFICATE.json',
        P+'D5-I179-S01-ROLES-SCOPE-GATES.json',*[v['path'] for v in plan['bindings'].values()]}
    assert len(refs)==14
    assert d['documentary_inventory']==[dict(**pin(p),serialized_file_bytes=(ROOT/p).stat().st_size,
        availability='DOCUMENTARY_SOURCE_NOT_EXTERNAL_ANCHOR_EVIDENCE') for p in sorted(refs)]
    roles=d['role_scope_matrix'];assert [r['id'] for r in roles]==step['provenance_and_role']['primary_review_roles']==['R01','R02','R08']
    for r in roles:
        source=next(s for s in ce01['role_scope_matrix'] if s['id']==r['id'])
        assert {k:v for k,v in r.items() if k!='CE02_responsibility'}=={k:v for k,v in source.items() if k!='CE01_responsibilities'}
        assert r['CE02_responsibility'] and r['assigned_person'] is None and not r['accepted_appointment']
    producer=d['producer'];assert producer['role']=='DOCUMENTARY_PREPARER' and producer['canonical_human_actor_id'] is None
    for k in ['accepted_external_identity','actor_independent','organizationally_independent','independent_acceptance']:assert producer[k] is False
    permissions=d['permission_boundary']
    assert permissions['authorized_documentary_actions']==['READ_SOURCE_JSON_GIT_HASHES','PREPARE_CE02_MISSING_EVIDENCE_DOSSIER','RUN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT']
    assert permissions['denied_action_classes']==[r['action'] for r in ce01['permission_matrix'] if not r['authorized_now']]
    assert len(permissions['denied_action_classes'])==14
    for k in ['no_provider_contact_or_nomination','no_keys_generation_or_crypto_execution','no_product_or_component_execution','no_active_state_or_quota_change']:assert permissions[k] is True
    rows=d['evidence_requirements'];assert [r['id'] for r in rows]==['AP%02d'%i for i in range(1,10)]
    inverse={rule:[] for rule in d['contract_rules']}
    for r in rows:
        assert r['subject'] and r['required_genuine_evidence'] and r['status']=='MISSING_NOT_EVALUATED'
        for k in ['actual_provider_identity','actual_provider_locator','actual_body_sha256','actual_body_bytes','actual_appointment','actual_acceptance_record']:assert r[k] is None
        assert r['accepted'] is False and r['contact_authorized_now'] is False
        for rule in r['contract_rules']:inverse[rule].append(r['id'])
    assert all(inverse.values())
    actual=d['actual_anchor_state']
    bool_fields={'complete_referenced_evidence_bodies_supplied','any_private_key_included_or_requested',
        'documentary_hash_used_as_external_expected_registry_digest','actual_positive_I191_record_created'}
    assert len(actual)==19
    for k,v in actual.items():assert v is False if k in bool_fields else v is None
    schema=d['schema_obligations'];assert schema['schema_binding']==pin(PACK,'/$defs/anchor_registry')
    assert schema['definitions']==[dict(name=n,source=pin(PACK,'/$defs/'+n),schema_fragment=defs[n])
        for n in ['anchor_registry','anchor_key','evidence_reference','validity']]
    assert schema['body_cap_bytes']==spec['record_caps_bytes']['anchor_registry']==65536
    assert schema['actual_schema_codec_or_crypto_validation']=='NOT_RUN_NO_ACTUAL_BODY'
    for k in ['cap_is_candidate_evidence_limit_not_active_quota','dossier_is_not_registry_body','body_cap_not_applied_to_documentary_wrapper','body_hash_must_be_actual_not_placeholder']:assert schema[k] is True
    contract=d['trust_and_currentness_contract'];profile=rd(plan['bindings']['profile02']['path'])
    assert contract['purpose_enum']==defs['anchor_key']['properties']['purpose']['enum']
    assert contract['custody_domains']==spec['custody_approval_domains'] and contract['domain_separator_octets']==[0]
    assert contract['complete_sorted_unique_binding_key']==['purpose','key_id']
    assert contract['snapshot_max_lifetime_seconds']==profile['bootstrap']['context_limits']['max_validity_seconds']==3600
    assert contract['max_trusted_clock_error_seconds']==profile['bootstrap']['context_limits']['max_clock_error_seconds']==5
    assert contract['time_rule']==profile['bootstrap']['time'] and contract['freshness_rule']==profile['bootstrap']['freshness']
    for k in ['external_expected_values_must_preexist_supplied_registry','no_repo_C_bundle_or_self_signed_bootstrap',
              'no_hidden_online_file_lookup_or_stale_cache_TOFU','canonical_actor_per_binding',
              'R01_R02_may_share_only_same_qualified_human_with_separate_role_domain_approvals']:assert contract[k] is True
    assert not contract['actual_currentness_verified'] and not contract['instantaneous_revocation_discovery_claimed']
    rejects=contract['rejection_conditions'];assert len(rejects)==10 and len({r['id'] for r in rejects})==10
    for r in rejects:assert r['disposition']=='REJECT_IF_OBSERVED_OR_REQUIRED_FACT_MISSING' and r['actual_evaluation']=='NOT_EVALUATED'
    assert d['inherited_scope_boundaries']==ce01['inherited_scope_boundaries'] and d['preserved_negative_gates']==ce01['preserved_negative_gates']
    for r in d['review_dispositions'].values():
        if isinstance(r,dict):assert r==dict(person=None,appointment=None,authority=None,decision='PENDING_NOT_ACCEPTED')
        else:assert r is True
    historical=d['historical_scope'];assert not historical['I193_saved_CE02_candidate_dossier_created'] and historical['current_CE02_dossier_created']
    assert not step['candidate_dossier_created'] and not step['accepted'] and historical['actual_accepted_steps']==0
    assert not historical['other10_planned_dossiers_created']
    assert (ROOT/plan['steps'][0]['candidate_dossier_path']).exists() and (ROOT/CE01).exists()
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][2:])
    ready=d['missing_facts_and_readiness'];assert ready['candidate_documentary_ready_for_review'] and len(ready['missing'])==4
    for k in ['actual_anchor_evidence_available','actual_CE01_dependency_accepted','actual_CE02_acceptance_ready']:assert ready[k] is False
    assert ready['no_execution_contact_or_key_generation_to_fill_missing_facts'] is True
    effect=d['current_effect'];assert effect['CE02_documentary_candidate_prepared'] and effect['candidate_dossiers_prepared_this_increment']==1
    assert effect['actual_accepted_steps']==effect['actual_external_evidence_accepted']==effect['resource_obligations_closed']==0
    for k,v in effect.items():
        if k not in ['CE02_documentary_candidate_prepared','candidate_dossiers_prepared_this_increment','actual_accepted_steps','actual_external_evidence_accepted','resource_obligations_closed','IR03']:assert v is False
    assert effect['IR03']=='NOT_READY' and d['decision']==plan['decision'] and d['E06']==plan['E06']
    assert set(d['work_unit']['rollback_files'])==FILES and d['work_unit']['verification_command']=='python3 docs/validation/D5-I199-audit.py'
    return dict(schema='d5.i199-preparation-review.v1',increment='I199',date='2026-11-16',base_commit=BASE,
        dossier=pin(DOS),input_pins=pins,status='CE02_MISSING_EVIDENCE_DOCUMENTARY_CANDIDATE_PREPARED_NOT_ACCEPTED',
        provenance=dict(preparer='Same Codex assistant/chat',actor_independent=False,organizationally_independent=False,
            competent_R01_R02_R08_acceptance=False,independent_acceptance=False),
        historical_replay=dict(exact_CE02_absence_verified_in_BASE_git_tree=True,
            only_CE02_presence_projected_during_I198_inherited_documentary_reconstruction=True,
            I195_original_CE01_guard_preserved=True,prior_I198_reconstruction_and_review_reproduced=True,
            presence_method_restored=True,current_CE02_real_path_bytes_separately_required=True,
            other_planned_dossiers_absent=10,prior_publication_mains_run=False),
        coverage=dict(required_evidence_items=3,acceptance_checks=2,authorization_boundaries=1,contract_rules=step['contract_rules'],
            inverse_rule_to_requirement=inverse,documentary_sources=14,missing_provenance_requirements=9,
            schema_definitions=4,required_anchor_registry_fields=defs['anchor_registry']['required'],
            proposed_registry_body_cap=65536,actual_registry_bytes=None,actual_schema_codec_or_crypto_validation='NOT_RUN',
            role_review_slots_unassigned=3,rejection_conditions_pending=10,competent_CE01_dependency_satisfied=False),
        limitations=['This is a negative documentary wrapper, not an actual anchor_registry or proof of trust/provenance/freshness/identity/keys.',
            'Schema fragments/caps and declared rejection rules are documentary requirements only; no registry body, canonical codec or signature verification is run.',
            'Genuine external authority/expected values/evidence and appointed R01/R02/R08 acceptance, including competent CE01 adoption, remain missing.'],
        current_effect=effect,decision=d['decision'],E06=d['E06'])


def main():
    assert rd(PREP)==build_review()
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published479'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==484
    seal=rd(SEAL);assert seal['schema']=='d5.i199-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published484']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['CE02_accepted','actual_anchor_registry_created','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY_EVIDENCE_MISSING',increment='I199',CE02_candidate_prepared=True,
        CE02_accepted=False,actual_anchor_registry_created=False,actual_CE01_dependency_satisfied=False,historical_pins=792,
        prior_published_files_preserved=484,new_files=5,actual_evidence_accepted=0,independent_acceptance=False,
        product_or_components_executed=0,quotas_changed=False,rebind_applied=False,resource_obligations_closed=0,
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
