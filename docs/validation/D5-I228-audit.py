#!/usr/bin/env python3
"""I228 documentary review of W02; no product/components or positive trust operations."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '4a6f0613d583de09d4aca0c3f4e7ecc4b21a3410'
DATE = '2026-11-24'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
SUBJECT = P+'D5-I223-W02-PEOPLE-AND-ANCHORS-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE02 = P+'D5-I201-CE02-ANCHOR-PROVENANCE-CANDIDATE-02.json'
CE03 = P+'D5-I193-CE03-HUMAN-IDENTITY-ROSTER-CANDIDATE.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
ENTRY_REVIEW = P+'D5-I226-I225-documentary-review.json'
PRIOR_AUDIT = P+'D5-I227-audit.py'
PRIOR_PREP = P+'D5-I227-preparation-review.json'
PRIOR_SEAL = P+'D5-I227-integrity.json'
PRIOR_DOC = 'docs/design/D5-I227-W02-PEOPLE-AND-ANCHORS.md'
PRIOR_FILES = {SUBJECT,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I228-I227-source-reconstruction.json'
REVIEW = P+'D5-I228-I227-documentary-review.json'
AUDIT = P+'D5-I228-audit.py'
SEAL = P+'D5-I228-integrity.json'
DOC = 'docs/design/D5-I228-I227-W02-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W02_REVIEW_PEOPLE_ANCHORS_MISSING_NOT_ADMITTED'


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


def inspect_scope(d):
    """Compare source policies directly, separately from I227's generator."""
    plan,anchors,people,spec = rd(PLAN),rd(CE02),rd(CE03),rd(SPEC)
    w = plan['work_packages'][1]
    assert d['work_package'] == w['id'] == 'W02'
    assert fragment(d['work_package_binding']) == w and d['planned_deliverable_id'] == w['deliverable_id']
    for target,source in [('required_deliverables','deliverables'),('required_exit_predicates','exit_predicates'),('reject_if','reject_if'),('needs_separate_future_authority_for','needs_separate_future_authority_for')]:
        assert d[target] == w[source]
    assert len(d['required_deliverables']) == len(d['required_exit_predicates']) == 3
    dep = d['dependency_gate']
    assert dep['required_package_ids'] == w['depends_on'] == ['W01']
    assert dep['W01_accepted'] is False and dep['SD01_stop_active'] is True, 'W01_SD01_bypass'
    assert dep['actual_entry_authority'] is None and dep['actual_prior_scope_acceptance'] is None
    assert dep['W02_preparation_does_not_discharge_W01_or_start_positive_package_progress']
    assert dep['W02_or_future_bundle_cannot_be_sole_forecast_authority_for_W01'], 'future_entry_authority'
    assert fragment(dep['source']) == rd(ENTRY_REVIEW)['documentary_clarifications'][0]
    roles = d['role_scope_matrix']
    assert len(roles) == 8 and roles == rd(CE01)['role_scope_matrix'], 'invented_role_identity'
    assert [r['id'] for r in roles] == ['R%02d'%i for i in range(1,9)]
    for row in roles:
        assert row['accepted_appointment'] is False and row['current_actions_authorized'] == []
        assert all(row[k] is None for k in ['assigned_person','canonical_actor_id','appointment_or_authority_record','competence_evidence','key_or_trust_binding','validity'])
    subjects = d['subject_category_inventory']
    assert [r['category'] for r in subjects] == ['SOURCE_AUTHORS','DOCUMENTARY_PREPARERS','REQUESTER','PROOF_AUTHORS_AND_PROVIDERS','CUSTODY_SIGNATORIES']
    for row in subjects:
        assert row['complete'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    expected = [(CE02,'evidence_requirements',i,r,r.get('consumer_step','CE02')) for i,r in enumerate(anchors['evidence_requirements'])]
    expected += [(CE03,'identity_requirements',i,r,r['consumer_step']) for i,r in enumerate(people['identity_requirements'])]
    assert len(d['evidence_requirement_ledger']) == len(expected) == 19
    for row,(path,group,i,requirement,consumer) in zip(d['evidence_requirement_ledger'],expected):
        assert row['source'] == pin(path,'/'+group+'/'+str(i)) and fragment(row['source']) == row['exact_requirement'] == requirement
        assert row['id'] == requirement['id'] and row['consumer_step'] == consumer
        wp = {'CE10':'W12','CE08':'W10'}.get(consumer,'W02')
        assert row['work_package_consumer'] == wp and row['deferred_from_W02'] is (wp != 'W02'), 'wrong_phase_mapping'
        assert row['actual_evidence'] is None and row['actual_review'] is None and row['accepted'] is False
    ap = d['anchor_policy']
    assert ap['exact_policy'] == anchors['trust_and_currentness_contract'] == fragment(ap['source'])
    assert ap['actual_anchor_state'] == anchors['actual_anchor_state'], 'invented_anchor'
    assert all(v is None or v is False for v in ap['actual_anchor_state'].values())
    assert ap['prior_anchor_requirement_ids'] == anchors['step_obligation_boundary']['CE02']['required_requirement_ids']
    assert ap['genuine_external_prior_provisioning_acceptance_required'], 'prior_acceptance_waived'
    assert ap['CE10_future_approvals_required_to_accept_W02'] is False, 'premature_approval'
    assert ap['CE10_may_authenticate_own_anchors'] is False, 'anchor_self_bootstrap'
    assert ap['CE10_W12_actual_common_core_approvals_still_required_in_later_phase'], 'later_approval_waived'
    assert ap['actual_approval_core_C_or_signature'] is None and ap['actual_clock_or_revocation_check_performed'] is False
    assert ap['documentary_policy_hash_is_not_external_expected_registry_digest'] and ap['current_date_does_not_prove_currentness']
    trust = ap['exact_policy']
    assert trust['snapshot_max_lifetime_seconds'] == 3600 and trust['max_trusted_clock_error_seconds'] == 5
    assert trust['domain_separator_octets'] == [0] and len(trust['custody_domains']) == 3
    ip = d['identity_policy']
    assert ip['exact_policy'] == people['identity_resolution_policy'] == fragment(ip['source'])
    assert ip['actual_identity_state'] == people['actual_identity_state']
    assert all(v is None or v is False for v in ip['actual_identity_state'].values())
    assert ip['human_and_software_principals_distinct'] and ip['assistant_or_git_account_not_authenticated_human'], 'human_software_collapse'
    assert ip['provisionally_intake_known_people_only'] and ip['future_authors_preapproved'] is False, 'future_author_preapproval'
    assert ip['actual_authorship_or_identity_lookup_performed'] is False
    policy = people['identity_resolution_policy']
    sep = [(r['role']+' != '+r['excluded_subject'],pin(CE03,'/identity_resolution_policy/S01_exclusions/'+str(i))) for i,r in enumerate(policy['S01_exclusions'])]
    for key in ['profile_source_author_and_root_key_rules','extra_custody_separation']:
        sep += [(r,pin(CE03,'/identity_resolution_policy/'+key+'/'+str(i))) for i,r in enumerate(policy[key])]
    assert len(d['separation_matrix']) == len(sep) == 14, 'separation_omission'
    assert len(policy['S01_exclusions']) == 8 and len(policy['profile_source_author_and_root_key_rules']) == 2 and len(policy['extra_custody_separation']) == 4
    for row,(rule,source) in zip(d['separation_matrix'],sep):
        assert row['rule'] == rule and row['source'] == source
        assert row['actual_canonical_subjects_or_keys'] is None and row['actual_comparison_record'] is None and row['verified'] is False, 'invented_separation'
    overlap = d['overlap_policy']
    assert overlap['R01_R02_overlap_permitted_only_for_same_genuinely_qualified_human']
    assert overlap['separate_role_domain_approvals_required_in_CE10_W12']
    assert overlap['no_blanket_R01_R02_separation_added'], 'extra_overlap_ban'
    assert overlap['names_keys_role_strings_or_accepted_flags_alone_not_independence']
    defs = d['schema_policy']
    assert [r['name'] for r in defs['definitions']] == ['anchor_registry','anchor_key','actor_registry','actor','preparation_record','evidence_reference','validity']
    for row in defs['definitions']:
        assert row['schema_fragment'] == fragment(row['source']) == rd(PACK)['$defs'][row['name']]
    assert defs['candidate_anchor_registry_cap_bytes'] == spec['record_caps_bytes']['anchor_registry'] == 65536
    assert defs['candidate_actor_registry_cap_bytes'] == spec['record_caps_bytes']['actor_registry'] == 98304
    assert defs['limits_are_candidate_policy_not_active_quotas'] and defs['no_truncation_to_fit'] and defs['wrapper_is_not_registry_body'], 'cap_as_active_quota'
    assert defs['actual_registry_sizes'] is None and defs['actual_fit_proof'] is None
    assert defs['actual_schema_codec_or_crypto_validation'] == 'NOT_RUN_NO_ACTUAL_BODY'
    tracking = d['preparation_tracking']
    assert all(v is None for k,v in tracking.items() if k.startswith('actual_'))
    assert tracking['documentary_file_hashes_not_authorship_or_identity_proof'] and tracking['full_preparer_list_not_claimed']
    assert tracking['positive_record_must_bind_exact_profile_and_schema_and_genuine_contribution']
    assert tracking['no_preparation_record_backpins_C_acceptance_bundle_or_future_root'], 'preparation_cycle'
    phase = d['phase_boundary']
    assert phase['exact_plan_order'] == plan['scope_authentication_and_freeze_order'] == fragment(phase['source'])
    assert phase['historical_CE03_CE08_boundary'] == people['step_obligation_boundary']
    assert phase['freeze_and_refresh_policy'] == people['freeze_and_refresh']
    assert phase['real_W05_W08_authors_and_bodies_authenticated_before_W09_required'], 'late_authors'
    assert phase['W10_CE08_final_actor_freeze_does_not_retroactively_authenticate_W09'], 'forecast_freeze'
    assert phase['actor_then_image_then_caller_then_platform_before_C_required']
    assert phase['W10_freeze_or_final_registry_completeness_required_for_W02'] is False and phase['W02_intake_does_not_freeze_final_registry'], 'premature_freeze'
    assert phase['actual_final_actor_registry_or_digest'] is None and phase['actual_downstream_refresh_or_rebind_applied'] is False
    cost = d['costs_and_authority']
    assert cost['inherited_boundary'] == plan['authorization_boundary'] == fragment(cost['source'])
    assert cost['inherited_boundary']['current_run_command'] is None
    assert all(v is False for k,v in cost['inherited_boundary'].items() if k.endswith('_authorized'))
    assert len(cost['allowed_now']) == 4 and cost['no_contacts_nominations_enrollment_provisioning_keygen_signing_positive_verification_or_service_calls']
    assert cost['actual_external_material_or_provider'] is None and cost['actual_action_specific_authority'] is None
    assert cost['all_per_attempt_lookup_freshness_identity_crypto_copies_registry_receipt_native_IO_in_complete_resource_join'], 'omitted_cost'
    assert cost['offline_or_prior_human_work_not_permission_to_omit_required_launch_costs']
    assert cost['schemas_caps_and_document_hashes_not_heap_CPU_service_or900_proof']
    assert cost['actual_resource_or_capacity_evidence'] is None and cost['quotas_or_reserves_applied'] is False, 'quota_change'
    exits = d['exit_predicate_dispositions']
    assert len(exits) == 3 and [r['predicate'] for r in exits] == w['exit_predicates']
    for row in exits:
        assert fragment(row['source']) == row['predicate'] and row['documentary_policy_prepared'] is True
        assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_')), 'exit_acceptance'
    preserved = d['preserved_scope_and_gates']
    for key in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']:
        assert preserved[key] == plan[key]
    for row in preserved['preserved_negative_gates']:
        assert fragment({**row['source'],'json_pointer':row['json_pointer']}) == row['observed_value']
    assert preserved['existing_CE_dossiers_are_documents_not_actual_registry_approval_or_receipt']
    expected_rules = [r for r in spec['rules'] if r['id'] in ['K01','K02','K03','K10','K11','K13','K15','K16']]
    assert [r['exact_rule'] for r in d['contract_rules']] == expected_rules
    for row in d['contract_rules']:
        assert fragment(row['source']) == row['exact_rule']
    for key,value in d['current_effect'].items():
        if key == 'W02_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False, 'positive_effect'
    assert all(d['producer'][key] is False for key in ['actor_independent','competent_R06_review','separate_R08_acceptance','external_contacts_made'])
    check_pointers(d)


def reconstruct():
    d = rd(SUBJECT)
    pins = {**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 937
    verify_blobs(pins)
    inspect_scope(d)
    criteria = [
        ('RC01','Three deliverables/exits and exact I223 W02 contract retained','/work_package_binding'),
        ('RC02','W01 unaccepted and SD01 active; no future W02 authority bootstrap','/dependency_gate'),
        ('RC03','Eight role scopes and five additional subject categories unassigned; no person-count inference','/role_scope_matrix'),
        ('RC04','19 exact requirements mapped to17 W02, one W10 and one W12 obligations','/evidence_requirement_ledger'),
        ('RC05','Genuine prior independent anchor provisioning/acceptance remains required; no self trust','/anchor_policy'),
        ('RC06','CE10/W12 approvals deferred but not waived; no retrospective anchor authentication','/anchor_policy'),
        ('RC07','Canonical-human/alias/competence policy distinct from software caller; no future-author preapproval','/identity_policy'),
        ('RC08','All14 separation rules retained as unverified policy; qualified R01/R02 overlap allowed','/separation_matrix'),
        ('RC09','Seven exact schemas and two candidate registry caps; no active quota or fit proof','/schema_policy'),
        ('RC10','Assistant activity is not authenticated human/preparation record; no future-hash cycle','/preparation_tracking'),
        ('RC11','W02 provisional; genuine W05-W08 authors/bodies before W09; W10 only reconciles accepted facts','/phase_boundary'),
        ('RC12','Known costs remain in full resource composition; no offline zero-cost inference','/costs_and_authority'),
        ('RC13','No contact/enrollment/key/signing/probe/execution authority created','/costs_and_authority'),
        ('RC14','Three exit predicates remain unaccepted without genuine evidence/review','/exit_predicate_dispositions'),
        ('RC15','Historical certificate, inherited caps and deferred private CE12 preserved','/preserved_scope_and_gates'),
        ('RC16','No actual accepted package/registry/anchor/resource/gate/authority/D5 promotion','/current_effect')]
    return dict(schema='d5.i228-i227-source-reconstruction.v1',increment='I228',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        subject=pin(SUBJECT),plan=pin(PLAN,'/work_packages/1'),input_pins=pins,
        criteria=[dict(id=i,criterion=t,subject=pin(SUBJECT,p),result='DOCUMENTARY_CONSISTENCY_CONFIRMED_NOT_REAL_ACCEPTANCE') for i,t,p in criteria],
        requirement_phase_mapping=[dict(id=r['id'],source=r['source'],consumer_step=r['consumer_step'],work_package_consumer=r['work_package_consumer'],deferred=r['deferred_from_W02'],actually_accepted=False) for r in d['evidence_requirement_ledger']],
        counts=dict(input_pins=937,criteria=16,roles=8,additional_subject_categories=5,requirements=19,W02_requirements=17,W10_requirements=1,W12_requirements=1,separation_rules=14,schemas=7,pending_exits=3),
        current_effect={**d['current_effect'],'W02_documentary_reviewed':True},methodological_review_not_independent_R06_or_separate_R08=True)


def rejection_checks():
    cases = [
        ('W01_SD01_bypass',('dependency_gate','SD01_stop_active'),False),
        ('future_entry_authority',('dependency_gate','W02_or_future_bundle_cannot_be_sole_forecast_authority_for_W01'),False),
        ('invented_role_identity',('role_scope_matrix',0,'canonical_actor_id'),'UNAUTHENTICATED_TEST_LABEL_NOT_ACTOR'),
        ('wrong_phase_mapping',('evidence_requirement_ledger',8,'work_package_consumer'),'W02'),
        ('invented_anchor',('anchor_policy','actual_anchor_state','externally_expected_registry_sha256'),'INVENTED_NOT_REAL_DIGEST'),
        ('prior_acceptance_waived',('anchor_policy','genuine_external_prior_provisioning_acceptance_required'),False),
        ('premature_approval',('anchor_policy','CE10_future_approvals_required_to_accept_W02'),True),
        ('anchor_self_bootstrap',('anchor_policy','CE10_may_authenticate_own_anchors'),True),
        ('later_approval_waived',('anchor_policy','CE10_W12_actual_common_core_approvals_still_required_in_later_phase'),False),
        ('human_software_collapse',('identity_policy','human_and_software_principals_distinct'),False),
        ('future_author_preapproval',('identity_policy','future_authors_preapproved'),True),
        ('invented_separation',('separation_matrix',0,'verified'),True),
        ('extra_overlap_ban',('overlap_policy','no_blanket_R01_R02_separation_added'),False),
        ('cap_as_active_quota',('schema_policy','limits_are_candidate_policy_not_active_quotas'),False),
        ('preparation_cycle',('preparation_tracking','no_preparation_record_backpins_C_acceptance_bundle_or_future_root'),False),
        ('late_authors',('phase_boundary','real_W05_W08_authors_and_bodies_authenticated_before_W09_required'),False),
        ('forecast_freeze',('phase_boundary','W10_CE08_final_actor_freeze_does_not_retroactively_authenticate_W09'),False),
        ('premature_freeze',('phase_boundary','W10_freeze_or_final_registry_completeness_required_for_W02'),True),
        ('omitted_cost',('costs_and_authority','all_per_attempt_lookup_freshness_identity_crypto_copies_registry_receipt_native_IO_in_complete_resource_join'),False),
        ('quota_change',('costs_and_authority','quotas_or_reserves_applied'),True),
        ('exit_acceptance',('exit_predicate_dispositions',0,'accepted'),True),
        ('positive_effect',('current_effect','D5_closed'),True)]
    result = []
    for name,path,value in cases:
        mutant = copy.deepcopy(rd(SUBJECT))
        target = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            inspect_scope(mutant)
        except AssertionError as error:
            assert str(error) == name, (name,str(error))
            result.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return result


def build_review(rec):
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    exists = Path.exists
    assert previous['build_candidate']() == rd(SUBJECT)
    assert previous['build_review']() == rd(PRIOR_PREP)
    assert Path.exists is exists
    return dict(schema='d5.i228-i227-documentary-review.v1',increment='I228',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,subject=pin(SUBJECT),reconstruction=pin(RECON),
        verdict='W02_DOCUMENTARY_PEOPLE_ANCHORS_PHASE_BOUNDARIES_CONSISTENT_W01_BLOCKED_NOT_ACCEPTED',
        findings=[],finding_count=0,criteria=rec['criteria'],counts=rec['counts'],
        documentary_clarifications=[
            dict(id='N01',subject='Preparation versus genuine entry authority',disposition='W02 documentary preparation/review/publication does not accept W01/W02 or bypass SD01. Genuine entry scope authority and competent separate decisions remain missing; future W02 appointments/bundle cannot be their sole forecast authority.'),
            dict(id='N02',subject='Anchor policy versus later approvals',disposition='Prior external origin/provisioning/acceptance, independently expected digest/epoch, authenticated bindings and evidence remain W02 requirements. CE10/W12 actual common-core approvals remain required later and cannot bootstrap their own anchors. Their absence is not an extra premature W02 dependency.'),
            dict(id='N03',subject='Provisional intake versus final freeze',disposition='W02 does not require W10 final completeness. Every actual proof author/body and baseline fact must nevertheless be authenticated before W09 acceptance. W10 reconciles the same accepted facts; changed contributors/identities/bodies/epoch/key/policy/scope invalidate affected proofs and require renewed review.'),
            dict(id='N04',subject='Canonical humans and actual evidence',disposition='Eight roles/five subject categories are requirements, not thirteen people. All preparers, aliases and source-author/root-key/custody exclusions apply over authenticated humans/keys. Qualified R01/R02 overlap remains allowed. Assistant/Git labels, document hashes, caps, schemas and status flags do not supply human identity, independence, real registry evidence or capacity.'),
            dict(id='N05',subject='Costs and final route',disposition='Per-attempt custody work remains inside the complete resource/phase join. No new Reader/channel/helper/output or active quota/reserve is authorized. CE12 remains private/deferred and final E06/Q/root/admission/claim/receipt are separate from prelaunch evidence. Same assistant checks do not provide independent R06 or separate R08 acceptance.')],
        source_replay=dict(I227_candidate_and_preparation_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(),current_effect=rec['current_effect'],
        provenance=dict(preparer_and_reviewer='Same Codex assistant/chat as I227',methodological_only=True,actor_independent=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts=False),
        next_step='Documentary W02 review complete; positive progress remains stopped at SD01 pending genuine entry authority and accepted W01/W02 evidence. No contact, nomination, enrollment, provisioning, signing or operational work is initiated.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I228-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/role/policy/phase comparisons only; no product/components, imports/build/compile/tests/benchmarks, codec/crypto positives, probes/clock/ledger/claim/process/service/signing/keygen/enrollment/provisioning/contact.',
            over400_lines=True,reason='One review unit with immutable source pins, phase/identity/anchor comparisons, negative checks and preservation seal; overage declared. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_identity_enrollment_scope_adoption_or_execution_authority=True))


def main():
    rec = reconstruct()
    assert rd(RECON) == rec
    review = build_review(rec)
    assert rd(REVIEW) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published624'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 629
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i228-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published629'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == rec['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I228',historical_pins=937,preserved_published_files=629,new_files=5,
        criteria=16,findings=0,documentary_rejections=len(review['rejection_checks']),current_effect=rec['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
