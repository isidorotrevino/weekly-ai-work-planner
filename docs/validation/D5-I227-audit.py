#!/usr/bin/env python3
"""I227 W02 documentary missing-person/anchor dossier; no registry or runtime execution."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'a715fb2310ce12f9bc3f29719e59f90b4917e20e'
DATE = '2026-11-24'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
W01 = P+'D5-I223-W01-TARGET-SCOPE-AUTHORITY-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE02 = P+'D5-I201-CE02-ANCHOR-PROVENANCE-CANDIDATE-02.json'
CE03 = P+'D5-I193-CE03-HUMAN-IDENTITY-ROSTER-CANDIDATE.json'
CE02_REVIEW = P+'D5-I202-I201-documentary-review.json'
CE03_REVIEW = P+'D5-I204-I203-documentary-review.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
PROFILE = P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
PROTO = P+'D5-I185-PGO181-SCHEMAS-CANDIDATE-02.json'
PRIOR_RECON = P+'D5-I226-I225-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I226-I225-documentary-review.json'
PRIOR_AUDIT = P+'D5-I226-audit.py'
PRIOR_SEAL = P+'D5-I226-integrity.json'
PRIOR_DOC = 'docs/design/D5-I226-I225-W01-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I223-W02-PEOPLE-AND-ANCHORS-CANDIDATE.json'
PREP = P+'D5-I227-preparation-review.json'
AUDIT = P+'D5-I227-audit.py'
SEAL = P+'D5-I227-integrity.json'
DOC = 'docs/design/D5-I227-W02-PEOPLE-AND-ANCHORS.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W02_PEOPLE_ANCHORS_MISSING_W01_BLOCKED_NOT_ADMITTED'


def rd(path):
    return json.loads((ROOT/path).read_text())


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def pin(path,pointer=''):
    return dict(path=path,sha256=sha(path),json_pointer=pointer)


def fragment(source):
    assert sha(source['path']) == source['sha256']
    value = rd(source['path'])
    for token in source.get('json_pointer','').split('/')[1:]:
        key = token.replace('~1','/').replace('~0','~')
        value = value[int(key)] if isinstance(value,list) else value[key]
    return value


def check_pointers(value):
    if isinstance(value,dict):
        if {'path','sha256','json_pointer'} <= set(value):
            fragment(value)
        for child in value.values():
            check_pointers(child)
    elif isinstance(value,list):
        for child in value:
            check_pointers(child)


def verify_blobs(pins):
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()))
    for path,digest in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', path
        data = stream.read(int(header[2]))
        assert stream.read(1) == b'\n' and hashlib.sha256(data).hexdigest() == digest == sha(path), path
    assert stream.read() == b''


def build_candidate():
    plan = rd(PLAN)
    work = plan['work_packages'][1]
    anchors = rd(CE02)
    people = rd(CE03)
    spec = rd(SPEC)
    pins = {**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 932
    inventory = sorted({PLAN,W01,PRIOR_REVIEW,CE01,CE02,CE03,CE02_REVIEW,CE03_REVIEW,SPEC,PACK,PROFILE,PROTO})
    requirements = []
    for path,group in [(CE02,'evidence_requirements'),(CE03,'identity_requirements')]:
        for i,row in enumerate(rd(path)[group]):
            consumer = row.get('consumer_step','CE02')
            requirements.append(dict(id=row['id'],source=pin(path,'/'+group+'/'+str(i)),exact_requirement=row,
                consumer_step=consumer,work_package_consumer='W12' if consumer=='CE10' else 'W10' if consumer=='CE08' else 'W02',
                deferred_from_W02=consumer in ['CE08','CE10'],actual_evidence=None,actual_review=None,accepted=False))
    policy = people['identity_resolution_policy']
    separations = [(r['role']+' != '+r['excluded_subject'],'ALL_CANONICAL_PREPARERS' if r['excluded_subject']=='DOCUMENTARY_PREPARER' else 'CANONICAL_HUMANS',pin(CE03,'/identity_resolution_policy/S01_exclusions/'+str(i))) for i,r in enumerate(policy['S01_exclusions'])]
    for key in ['profile_source_author_and_root_key_rules','extra_custody_separation']:
        separations += [(r,'CANONICAL_HUMANS_OR_PURPOSE_RESTRICTED_KEYS',pin(CE03,'/identity_resolution_policy/'+key+'/'+str(i))) for i,r in enumerate(policy[key])]
    schemas = ['anchor_registry','anchor_key','actor_registry','actor','preparation_record','evidence_reference','validity']
    rules = [dict(source=pin(SPEC,'/rules/'+str(i)),exact_rule=r) for i,r in enumerate(spec['rules']) if r['id'] in ['K01','K02','K03','K10','K11','K13','K15','K16']]
    return dict(schema='d5.i227-w02-people-and-anchors-candidate.v1',increment='I227',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        work_package='W02',planned_deliverable_id=work['deliverable_id'],
        kind='NEGATIVE_PROVISIONAL_PEOPLE_ANCHOR_DOSSIER_NOT_I191_RECORD_NOT_ACCEPTED_REAL_EVIDENCE_PACKAGE',
        status='W02_DOCUMENTARY_PREPARED_W01_ENTRY_AUTHORITY_BLOCKED_PEOPLE_AND_ANCHORS_MISSING_NOT_ACCEPTED_NOT_ADMITTED',
        input_pins=pins,work_package_binding=pin(PLAN,'/work_packages/1'),required_deliverables=work['deliverables'],
        required_exit_predicates=work['exit_predicates'],reject_if=work['reject_if'],needs_separate_future_authority_for=work['needs_separate_future_authority_for'],
        documentary_inventory=[pin(p) for p in inventory],contract_rules=rules,
        dependency_gate=dict(source=pin(PRIOR_REVIEW,'/documentary_clarifications/0'),required_package_ids=work['depends_on'],
            W01_accepted=False,actual_entry_authority=None,actual_prior_scope_acceptance=None,SD01_stop_active=True,
            W02_preparation_does_not_discharge_W01_or_start_positive_package_progress=True,
            W02_or_future_bundle_cannot_be_sole_forecast_authority_for_W01=True),
        role_scope_matrix=rd(CE01)['role_scope_matrix'],
        subject_category_inventory=[dict(category=c,scope_description=s,actual_canonical_humans=None,actual_organization_alias_competence_appointments=None,actual_purpose_key_bindings=None,actual_accepted_provenance=None,complete=False)
            for c,s in [('SOURCE_AUTHORS','Every actual author of the exact source scope'),('DOCUMENTARY_PREPARERS','Every preparer of accepted contract/evidence, including this assistant activity without inferring its accountable human'),
                ('REQUESTER','Accountable requesting human; separate from software caller'),('PROOF_AUTHORS_AND_PROVIDERS','All actual proof authors/providers, including W05-W08 before W09 acceptance'),('CUSTODY_SIGNATORIES','Every actual custodian/signatory under authenticated role-purpose authority')]],
        evidence_requirement_ledger=requirements,
        anchor_policy=dict(source=pin(CE02,'/trust_and_currentness_contract'),exact_policy=anchors['trust_and_currentness_contract'],
            actual_anchor_state=anchors['actual_anchor_state'],
            prior_anchor_requirement_ids=anchors['step_obligation_boundary']['CE02']['required_requirement_ids'],
            genuine_external_prior_provisioning_acceptance_required=True,
            CE10_future_approvals_required_to_accept_W02=False,CE10_may_authenticate_own_anchors=False,
            CE10_W12_actual_common_core_approvals_still_required_in_later_phase=True,
            actual_approval_core_C_or_signature=None,actual_clock_or_revocation_check_performed=False,
            documentary_policy_hash_is_not_external_expected_registry_digest=True,
            current_date_does_not_prove_currentness=True),
        identity_policy=dict(source=pin(CE03,'/identity_resolution_policy'),exact_policy=policy,
            actual_identity_state=people['actual_identity_state'],
            human_and_software_principals_distinct=True,assistant_or_git_account_not_authenticated_human=True,
            provisionally_intake_known_people_only=True,future_authors_preapproved=False,
            actual_authorship_or_identity_lookup_performed=False),
        separation_matrix=[dict(id='SP%02d'%(i+1),rule=r,scope=s,source=src,actual_canonical_subjects_or_keys=None,actual_comparison_record=None,verified=False)
            for i,(r,s,src) in enumerate(separations)],
        overlap_policy=dict(R01_R02_overlap_permitted_only_for_same_genuinely_qualified_human=True,
            separate_role_domain_approvals_required_in_CE10_W12=True,no_blanket_R01_R02_separation_added=True,
            names_keys_role_strings_or_accepted_flags_alone_not_independence=True),
        schema_policy=dict(source=pin(PACK),definitions=[dict(name=n,source=pin(PACK,'/$defs/'+n),schema_fragment=rd(PACK)['$defs'][n]) for n in schemas],
            candidate_anchor_registry_cap_bytes=spec['record_caps_bytes']['anchor_registry'],candidate_actor_registry_cap_bytes=spec['record_caps_bytes']['actor_registry'],
            limits_are_candidate_policy_not_active_quotas=True,no_truncation_to_fit=True,wrapper_is_not_registry_body=True,
            actual_registry_sizes=None,actual_fit_proof=None,actual_schema_codec_or_crypto_validation='NOT_RUN_NO_ACTUAL_BODY'),
        preparation_tracking=dict(activity='Same Codex assistant/chat prepared documentary I227 files',files=sorted(FILES),
            actual_accountable_canonical_human=None,actual_organization=None,actual_authorship_evidence=None,
            actual_positive_preparation_record=None,actual_contribution_scope_hash=None,
            documentary_file_hashes_not_authorship_or_identity_proof=True,
            full_preparer_list_not_claimed=True,positive_record_must_bind_exact_profile_and_schema_and_genuine_contribution=True,
            no_preparation_record_backpins_C_acceptance_bundle_or_future_root=True),
        phase_boundary=dict(source=pin(PLAN,'/scope_authentication_and_freeze_order'),exact_plan_order=plan['scope_authentication_and_freeze_order'],
            historical_CE03_CE08_boundary=people['step_obligation_boundary'],
            freeze_and_refresh_policy=people['freeze_and_refresh'],
            real_W05_W08_authors_and_bodies_authenticated_before_W09_required=True,
            W10_CE08_final_actor_freeze_does_not_retroactively_authenticate_W09=True,
            actor_then_image_then_caller_then_platform_before_C_required=True,
            W10_freeze_or_final_registry_completeness_required_for_W02=False,
            W02_intake_does_not_freeze_final_registry=True,
            actual_final_actor_registry_or_digest=None,actual_downstream_refresh_or_rebind_applied=False),
        costs_and_authority=dict(source=pin(PLAN,'/authorization_boundary'),inherited_boundary=plan['authorization_boundary'],
            allowed_now=['READ_DOCUMENTS_GIT_HASHES','PREPARE_THIS_NEGATIVE_DOSSIER','RUN_OWN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT'],
            no_contacts_nominations_enrollment_provisioning_keygen_signing_positive_verification_or_service_calls=True,
            actual_external_material_or_provider=None,actual_action_specific_authority=None,
            all_per_attempt_lookup_freshness_identity_crypto_copies_registry_receipt_native_IO_in_complete_resource_join=True,
            offline_or_prior_human_work_not_permission_to_omit_required_launch_costs=True,
            schemas_caps_and_document_hashes_not_heap_CPU_service_or900_proof=True,
            actual_resource_or_capacity_evidence=None,quotas_or_reserves_applied=False),
        exit_predicate_dispositions=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/1/exit_predicates/'+str(i)),predicate=t,
            documentary_policy_prepared=True,actual_evidence=None,actual_primary_R06_review=None,actual_separate_R08_acceptance=None,accepted=False)
            for i,t in enumerate(work['exit_predicates'])],
        preserved_scope_and_gates=dict(inherited_scope_boundaries=plan['inherited_scope_boundaries'],preserved_negative_gates=plan['preserved_negative_gates'],
            prelaunch_handoff_and_CE12=plan['prelaunch_handoff_and_CE12'],
            existing_CE_dossiers_are_documents_not_actual_registry_approval_or_receipt=True),
        current_effect=dict(W02_documentary_prepared=True,W01_accepted=False,W02_accepted=False,actual_entry_authority_verified=False,
            actual_people_anchors_appointments_or_key_bindings_accepted=False,actual_real_evidence_package_created=False,
            actor_registry_finalized=False,anchor_registry_provisioned=False,positive_I191_record_created=False,
            actual_evidence_accepted=0,work_packages_accepted=0,prelaunch_gates_closed=0,resource_obligations_closed=0,
            independent_acceptance=False,source_implementation_changed=False,product_or_components_executed=False,
            quotas_changed=False,reserves_changed=False,resource_reservations_created=False,rebind_applied=False,
            authority_or_destination_created=False,actual_claim_worker_or_receipt_created=False,
            execution_authorized=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),
        producer=dict(identity='Same Codex assistant/chat as I225/I226',documentary_preparer_only=True,actor_independent=False,
            competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_identity_enrollment_scope_adoption_or_execution_authority=True))


def validate(d):
    assert d['dependency_gate']['W01_accepted'] is False and d['dependency_gate']['SD01_stop_active'] is True, 'W01_or_SD01_bypassed'
    assert d['dependency_gate']['W02_or_future_bundle_cannot_be_sole_forecast_authority_for_W01'], 'future_authority'
    assert d['current_effect']['W02_accepted'] is False, 'W02_accepted'
    assert d['role_scope_matrix'][0]['canonical_actor_id'] is None, 'invented_human'
    assert d['anchor_policy']['actual_anchor_state']['externally_expected_registry_sha256'] is None, 'invented_anchor_digest'
    assert d['anchor_policy']['CE10_future_approvals_required_to_accept_W02'] is False, 'premature_approvals'
    assert d['anchor_policy']['CE10_may_authenticate_own_anchors'] is False, 'self_bootstrap'
    assert d['anchor_policy']['genuine_external_prior_provisioning_acceptance_required'], 'prior_acceptance_waived'
    assert d['identity_policy']['human_and_software_principals_distinct'], 'human_software_collapsed'
    assert d['identity_policy']['future_authors_preapproved'] is False, 'future_author_preapproval'
    assert d['phase_boundary']['W10_freeze_or_final_registry_completeness_required_for_W02'] is False, 'premature_freeze'
    assert d['phase_boundary']['real_W05_W08_authors_and_bodies_authenticated_before_W09_required'], 'late_author_authentication'
    assert d['separation_matrix'][0]['verified'] is False, 'invented_separation'
    assert d['overlap_policy']['no_blanket_R01_R02_separation_added'], 'extra_overlap_ban'
    assert d['preparation_tracking']['no_preparation_record_backpins_C_acceptance_bundle_or_future_root'], 'preparation_cycle'
    assert d['costs_and_authority']['quotas_or_reserves_applied'] is False, 'quota_changed'
    assert d['current_effect']['execution_authorized'] is False, 'execution_authorized'
    assert d['current_effect']['D5_closed'] is False, 'D5_closed'
    assert d == build_candidate(), 'Source reconstruction differs'
    check_pointers(d)


def rejection_checks(d):
    cases = [
        ('W01_or_SD01_bypassed',('dependency_gate','SD01_stop_active'),False),
        ('future_authority',('dependency_gate','W02_or_future_bundle_cannot_be_sole_forecast_authority_for_W01'),False),
        ('W02_accepted',('current_effect','W02_accepted'),True),
        ('invented_human',('role_scope_matrix',0,'canonical_actor_id'),'UNAUTHENTICATED_TEST_LABEL_NOT_ACTOR'),
        ('invented_anchor_digest',('anchor_policy','actual_anchor_state','externally_expected_registry_sha256'),'INVENTED_NOT_REAL_DIGEST'),
        ('premature_approvals',('anchor_policy','CE10_future_approvals_required_to_accept_W02'),True),
        ('self_bootstrap',('anchor_policy','CE10_may_authenticate_own_anchors'),True),
        ('prior_acceptance_waived',('anchor_policy','genuine_external_prior_provisioning_acceptance_required'),False),
        ('human_software_collapsed',('identity_policy','human_and_software_principals_distinct'),False),
        ('future_author_preapproval',('identity_policy','future_authors_preapproved'),True),
        ('premature_freeze',('phase_boundary','W10_freeze_or_final_registry_completeness_required_for_W02'),True),
        ('late_author_authentication',('phase_boundary','real_W05_W08_authors_and_bodies_authenticated_before_W09_required'),False),
        ('invented_separation',('separation_matrix',0,'verified'),True),
        ('extra_overlap_ban',('overlap_policy','no_blanket_R01_R02_separation_added'),False),
        ('preparation_cycle',('preparation_tracking','no_preparation_record_backpins_C_acceptance_bundle_or_future_root'),False),
        ('quota_changed',('costs_and_authority','quotas_or_reserves_applied'),True),
        ('execution_authorized',('current_effect','execution_authorized'),True),
        ('D5_closed',('current_effect','D5_closed'),True)]
    result = []
    for name,path,value in cases:
        mutant = copy.deepcopy(d)
        target = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            validate(mutant)
        except AssertionError as error:
            assert str(error) == name, (name,str(error))
            result.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return result


def build_review():
    d = rd(SUBJECT)
    verify_blobs(d['input_pins'])
    validate(d)
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    exists = Path.exists
    rec = previous['reconstruct']()
    assert rec == rd(PRIOR_RECON) and previous['build_review'](rec) == rd(PRIOR_REVIEW)
    assert Path.exists is exists
    assert len(d['role_scope_matrix']) == 8 and all(r['accepted_appointment'] is False for r in d['role_scope_matrix'])
    for row in d['role_scope_matrix']:
        assert all(row[k] is None for k in ['assigned_person','canonical_actor_id','appointment_or_authority_record','competence_evidence','key_or_trust_binding','validity'])
        assert row['current_actions_authorized'] == []
    assert len(d['evidence_requirement_ledger']) == 19 and len(d['separation_matrix']) == 14
    assert sum(not r['deferred_from_W02'] for r in d['evidence_requirement_ledger']) == 17
    for row in d['evidence_requirement_ledger']:
        assert fragment(row['source']) == row['exact_requirement']
        assert row['actual_evidence'] is None and row['actual_review'] is None and row['accepted'] is False
    for row in d['separation_matrix']:
        assert row['actual_canonical_subjects_or_keys'] is None and row['actual_comparison_record'] is None and row['verified'] is False
    assert all(v is None or v is False for v in d['anchor_policy']['actual_anchor_state'].values())
    assert all(v is None or v is False for v in d['identity_policy']['actual_identity_state'].values())
    for key,value in d['current_effect'].items():
        if key == 'W02_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False, key
    return dict(schema='d5.i227-preparation-review.v1',increment='I227',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,candidate=pin(SUBJECT),work_package=pin(PLAN,'/work_packages/1'),
        counts=dict(input_pins=932,roles=8,additional_subject_categories=5,evidence_requirements=19,prior_or_provisional_requirements=17,deferred_CE10_W12_approval_requirements=1,deferred_CE08_W10_freeze_requirements=1,separation_rules=14,schema_fragments=7,pending_exit_predicates=3),
        source_reconstruction=dict(I226_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        limitations=['W01 remains unaccepted and SD01 active. W02 is negative documentary preparation only; no positive dependency progress or actual evidence package.',
            'No genuine humans/organizations/aliases/competence/appointments/anchors/keys/epochs/clock/revocation/proof bodies or independent decisions supplied. No real I191 record or registry is generated.',
            'CE03 intake is provisional; actual W05-W08 authors must be authenticated before W09 acceptance. W10 final freeze only reconciles genuine facts and cannot provide forecast prior authority. CE10/W12 actual approvals are deferred and cannot bootstrap anchors.',
            'Same assistant preparation and checks are not competent independent R06 review or separate R08 acceptance.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I227-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/role/policy checks only; no product/components, registry codec/crypto positives, execution/build/import/compile/tests/probes/clock/ledger/signing/keygen/enrollment/provisioning/services/contact.',
            over400_lines=True,reason='One W02 negative evidence dossier with source pins, role/separation/phase matrices, preservation and documentary checks; overage declared. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_actual_identity_or_scope_acceptance_or_execution_authority=True))


def main():
    review = build_review()
    assert review == rd(PREP)
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published619'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 624
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i227-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published624'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == review['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I227',historical_pins=932,preserved_published_files=624,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],current_effect=review['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
