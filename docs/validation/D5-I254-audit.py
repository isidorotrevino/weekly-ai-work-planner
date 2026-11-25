#!/usr/bin/env python3
"""I254 source-only review of A01/RQ01; no product/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '1ebaea25f313a77cf5c49043bca3e43a19db9659'
DATE = '2026-11-25'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
W01 = P+'D5-I223-W01-TARGET-SCOPE-AUTHORITY-CANDIDATE.json'
W02 = P+'D5-I223-W02-PEOPLE-AND-ANCHORS-CANDIDATE.json'
SUBJECT = P+'D5-I251-A01-RQ01-ENTRY-AUTHORITY-SCOPE-CANDIDATE.json'
PRIOR_PREP = P+'D5-I253-preparation-review.json'
PRIOR_AUDIT = P+'D5-I253-audit.py'
PRIOR_SEAL = P+'D5-I253-integrity.json'
PRIOR_DOC = 'docs/design/D5-I253-A01-RQ01-ENTRY-AUTHORITY-SCOPE.md'
PRIOR_FILES = {SUBJECT,PRIOR_PREP,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I254-I253-source-reconstruction.json'
REVIEW = P+'D5-I254-I253-documentary-review.json'
AUDIT = P+'D5-I254-audit.py'
SEAL = P+'D5-I254-integrity.json'
DOC = 'docs/design/D5-I254-I253-A01-RQ01-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_A01_RQ01_REVIEW_ENTRY_AUTHORITY_AND_SCOPE_ACCEPTANCE_PENDING_NOT_ADMITTED'


def rd(path):
    return json.loads((ROOT/path).read_text())


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def pin(path, pointer=''):
    return dict(path=path, sha256=sha(path), json_pointer=pointer)


def fragment(ref):
    assert sha(ref['path']) == ref['sha256'], ref['path']
    value = rd(ref['path'])
    for token in ref.get('json_pointer','').split('/')[1:]:
        key = token.replace('~1','/').replace('~0','~')
        value = value[int(key)] if isinstance(value,list) else value[key]
    return value


def pointers(node):
    if isinstance(node,dict):
        if {'path','sha256','json_pointer'} <= set(node):
            fragment(node)
        for value in node.values():
            pointers(value)
    elif isinstance(node,list):
        for value in node:
            pointers(value)


def verify_blobs(pins):
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'], cwd=ROOT,
        input=''.join(BASE+':'+path+'\n' for path in sorted(pins)).encode()))
    for path,digest in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header)==3 and header[1]=='blob', path
        body = stream.read(int(header[2]))
        assert stream.read(1)==b'\n' and hashlib.sha256(body).hexdigest()==digest==sha(path), path
    assert not stream.read()


SCOPE_SECTIONS = ['logical_source_scope','effective_environment_scope','caller_platform_ledger_scope','policy_version_inventory',
    'numeric_candidate_ledger','protocol_output_ledger','custody_record_cap_ledger','heap_scope_ledger','phase_marker_ledger',
    'guard_obligation_ledger','transport_and_output_scope','source_requalification_boundary']
RETURN_SECTIONS = [
    ['entry_authority_inventory','entry_authority_boundary'],
    ['logical_source_scope','effective_environment_scope','caller_platform_ledger_scope','policy_version_inventory'],
    ['numeric_candidate_ledger','protocol_output_ledger','custody_record_cap_ledger','heap_scope_ledger','phase_marker_ledger','guard_obligation_ledger','transport_and_output_scope','source_requalification_boundary','inherited_scope_boundaries'],
    ['action_authority_ledger','existing_external_material_intake'],
    ['exit_predicate_dispositions','handoff_and_deferred_scope','change_control']]
CRITERION_RETURNS = [['RT01'],['RT01'],['RT01','RT05'],['RT02'],['RT02'],['RT03'],['RT04'],['RT01','RT02','RT03','RT04','RT05'],['RT05'],['RT05'],['RT01','RT02','RT03','RT04','RT05'],['RT05']]


def missing(row, false_fields=()):
    for key,value in row.items():
        if key.startswith('actual_'):
            assert value is False if key in false_fields else value is None,key
    if 'accepted' in row:
        assert row['accepted'] is False


def truth(row, names):
    for name in names:
        assert row[name] is True,name


def inspect(d):
    plan,acq,work,w02 = rd(PLAN),rd(ACQUISITION),rd(W01),rd(W02)
    lot=acq['acquisition_lots'][0]
    req=plan['work_packages'][0]
    assert (d['lot_id'],d['request_id'],d['work_package'],d['planned_deliverable_id'])==('A01','RQ01','W01',req['deliverable_id'])
    assert d['exact_acquisition_lot']==fragment(d['acquisition_lot_binding'])==lot
    assert d['exact_W01_requirement']==fragment(d['W01_requirement_binding'])==req
    assert d['W01_documentary_checklist']['path']==W01
    gate=d['entry_gate']
    assert gate['exact_boundary']==fragment(gate['source'])==work['entry_authority_boundary']
    truth(gate,['SD01_stop_active','no_future_W02_appointment_A07_bundle_or_root_as_sole_entry_authority',
        'no_A01_self_authorization_from_empty_predecessor_list_or_this_user_document_request',
        'W02_identity_requirements_used_as_eligibility_criteria_not_future_W02_acceptance_precondition'])
    missing(gate,['actual_authority_verified','actual_scope_accepted'])
    request=d['unsent_request']
    assert request['original_draft']==lot['unsent_request_draft']
    assert request['recipient_role_only']==lot['intended_recipient_role_kind']
    assert request['required_return_ids']==['RT%02d'%i for i in range(1,6)]
    assert request['is_draft_only'] is True and request['sent'] is False and request['contact_authorized'] is False
    missing(request)
    eas=d['authority_evidence_requests']
    assert [r['id'] for r in eas]==['EA01','EA02','EA03']
    for row,source in zip(eas,work['entry_authority_inventory']):
        assert row['exact_existing_requirement']==fragment(row['source'])==source
        assert row['required_return_id']=='RT01' and len(row['required_independent_material_fields'])==7
        missing(row)
    eligibility=d['eligibility_boundary']
    for child,source,expected in [('exact_identity_policy','identity_policy_source',w02['identity_policy']['exact_policy']),
        ('exact_separation_matrix','separation_source',w02['separation_matrix']),('exact_overlap_policy','overlap_source',w02['overlap_policy'])]:
        assert eligibility[child]==fragment(eligibility[source])==expected
    assert len(eligibility['exact_separation_matrix'])==14
    truth(eligibility,['all_preparers_and_source_authors_in_exclusion_scope',
        'no_assistant_git_account_role_label_key_or_signature_alone_as_canonical_human_or_independence',
        'no_blanket_R01_R02_separation_or_future_full_roster_required_for_A01'])
    missing(eligibility,['actual_separations_verified'])
    scope=d['scope_manifest_requirements']
    assert [r['section'] for r in scope]==SCOPE_SECTIONS
    for row in scope:
        assert fragment(row['source'])==work[row['section']]
        assert row['documentary_requirement_count']==len(work[row['section']])
        missing(row)
    sources=d['logical_sources']
    assert len(sources)==6
    for row,source in zip(sources,work['logical_source_scope']):
        assert row['logical_path']==source['logical_path'] and row['target_kind']==source['target_kind']
        assert row['effective_source_facts_deferred_to']=='W03'
        missing(row)
    known=d['known_vs_missing']
    assert known['policy_document_pins']==work['policy_version_inventory'] and len(known['policy_document_pins'])==8
    truth(known,['policy_hashes_are_document_integrity_not_effective_adoption_or_source_runtime_image_proof',
        'W01_logical_scope_does_not_require_actual_future_W03_hashes_or_freeze','no_material_or_effective_snapshot_invented'])
    missing(known)
    returns=d['requested_returns']
    assert [r['id'] for r in returns]==request['required_return_ids']
    for row,sections in zip(returns,RETURN_SECTIONS):
        assert row['title'] and row['requirements']
        assert row['W01_requirement_sources']==[pin(W01,'/'+section) for section in sections]
        assert fragment(row['universal_delivery_source'])==acq['evidence_delivery_contract']
        missing(row,['actual_received'])
    deliveries=d['W01_deliverable_coverage']
    assert len(deliveries)==3 and [r['id'] for r in deliveries]==['WD01','WD02','WD03']
    for i,row in enumerate(deliveries):
        assert row['exact_requirement']==fragment(row['source'])==req['deliverables'][i]
        assert row['required_return_ids']==[['RT02'],['RT03'],['RT04']][i]
        assert row['authority_return_id']=='RT01' and row['review_return_id']=='RT05'
        missing(row)
    criteria=d['acceptance_checklist']
    ids=['AC%02d'%i for i in range(1,13)]
    assert [r['id'] for r in criteria]==ids
    for row,returns_for_criterion in zip(criteria,CRITERION_RETURNS):
        assert row['criterion'] and row['required_return_ids']==returns_for_criterion
        assert row['disposition']=='PENDING_GENUINE_MATERIAL_AND_COMPETENT_DECISION'
        missing(row)
    exits=d['W01_exit_coverage']
    assert len(exits)==3 and [r['id'] for r in exits]==['WX01','WX02','WX03']
    for i,row in enumerate(exits):
        assert row['exact_predicate']==fragment(row['source'])==req['exit_predicates'][i]
        assert row['required_acceptance_criteria']==ids
        missing(row)
    material=d['missing_or_rejected_material']
    assert material['current_disposition']=='MISSING_NOT_RECEIVED_NOT_EVALUATED'
    assert material['actual_received_inventory'] is None and material['provided_real_bodies']==material['rejected_real_bodies']==[]
    assert type(material['actual_material_evaluations']) is int and material['actual_material_evaluations']==0
    truth(material,['missing_authority_or_unavailable_body_keeps_SD01_and_A01_unaccepted','no_global_absence_or_infeasibility_inferred'])
    actions=d['authority_by_action']
    assert actions['exact_existing_ledger']==fragment(actions['source'])==work['action_authority_ledger']
    assert len(actions['exact_existing_ledger'])==12
    truth(actions,['documentary_request_is_not_canonical_nomination_scope_adoption_or_operational_authority'])
    missing(actions,['actual_contact_or_operational_action_done'])
    costs=d['preserved_cost_scope_and_limits']
    assert costs['exact_resource_rules']==fragment(costs['resource_source'])==acq['preserved_resource_and_cost_rules']
    assert costs['exact_scope']==fragment(costs['scope_source'])==work['inherited_scope_boundaries']
    truth(costs,['same_caps_guards_no_extra_Reader_members_hidden_reads_free_costs_helpers_channels_or_outputs','quotas_budgets_reserves_unchanged'])
    missing(costs)
    handoff=d['handoff']
    assert handoff['exact_A01_completion_predicate']==lot['completion_predicate']
    assert handoff['exact_A01_missing_stop']==lot['missing_or_failure_stop']
    assert handoff['next_request_only_after_genuine_A01_acceptance']=='RQ02'
    assert handoff['RQ02_sent_or_enabled_now'] is False and handoff['A02_or_W02_started_or_accepted'] is False
    assert handoff['exact_final_route_boundary']==fragment(handoff['final_route_source'])==plan['prelaunch_handoff_and_CE12']
    truth(handoff,['prelaunch_acceptance_not_new_requirement_to_execute_final_E06_Q_root_claim_or_receipt','no_launch_certificate_promotion_or_D5_closure_from_A01_acceptance'])
    missing(handoff)
    change=d['change_control']
    assert change['exact_existing_policy']==fragment(change['source'])==work['change_control']
    truth(change,['affected_entry_authority_scope_or_body_change_requires_invalidation_and_fresh_genuine_review','no_active_rebind_or_snapshot_refresh'])
    expected={**acq['current_effect'],'A01_RQ01_documentary_prepared':True,'A01_accepted':False,'RQ01_sent':False,'actual_A01_authority_scope_or_review_records_created':False}
    assert d['current_effect']==expected
    assert d['producer']['actor_independent'] is False and d['producer']['competent_R06_review'] is False
    assert d['producer']['separate_R08_acceptance'] is False and d['producer']['external_contacts_made'] is False
    pointers(d)
    return dict(authority_roles={r['id']:r['exact_existing_requirement']['required_role'] for r in eas},
        scope_section_dimensions={r['section']:r['documentary_requirement_count'] for r in scope},
        scope_dimensions_are_documentary_container_lengths_not_proof_body_counts=True,
        deliverable_to_returns={r['id']:r['required_return_ids']+[r['authority_return_id'],r['review_return_id']] for r in deliveries},
        criterion_to_returns={r['id']:r['required_return_ids'] for r in criteria},
        exit_to_criteria={r['id']:r['required_acceptance_criteria'] for r in exits},
        separation_requirements=14,policy_document_versions=8,documentary_action_classes=4,unauthorized_operational_action_classes=8,
        missing_authority_slots=3,actual_authorities_verified=0,actual_received_bodies=0,actual_A01_acceptances=0)


CRITERIA = [
    'A01/RQ01 binds exact I251 first lot and W01 three deliverables/exits, without changing the target or planned real package.',
    'Unsent draft preserves original RQ01 and role-only recipient; no person,address,channel,contact authority or delivery is invented.',
    'EA01/EA02/EA03 preserve genuine preexisting scope,R06 and R08 authority requirements with provenance/competence/validity/custody.',
    'A01 empty predecessor list or current documentary request never creates entry authority or canonical appointment.',
    'Future W02 appointments or bundle/root cannot be sole forecast authority; W02 identity rules are criteria,not a backward acceptance edge.',
    'Fourteen separation rules and eight S01 exclusions remain exact for all preparers/source authors; no assistant independence inferred.',
    'Qualified R01/R02 overlap is retained with separate role-domain approvals at its phase,not blanket separation or premature bundle issuance.',
    'Twelve scope sections retain complete pinned W01 content; container dimensions are not evidence counts or verified runtime facts.',
    'Exactly six logical paths retain DOCUMENT/source distinctions and absent effective source hashes/mappings; W03 qualification is not anticipated.',
    'Eight policy hashes fix documents,not runtime/image identity,implementation or authoritative adoption.',
    'Scope logical acceptance does not require a future effective freeze,final roster or final custody record already issued.',
    'Five RT returns cover entry authority,logical scope,limits,action authority and genuine primary/separate decisions.',
    'Three W01 deliverables map to RT02/03/04 plus RT01 authority and RT05 review,without omitted requirements.',
    'Twelve AC criteria cover complete material/provenance,eligibility,scope,limits,reviews,currentness and limited handoff.',
    'AC12 expresses a transition rule,not actual A01 acceptance or completed RQ02 as its own prerequisite; all three exits remain pending.',
    'Reception requires full bodies/references/bytes/digests/providers/custody/assumptions and traceable missing/rejected dispositions.',
    'Unknown received inventory is null and actual supplied/rejected/evaluated material is zero,not global absence or infeasibility.',
    'Four documentary action classes and eight unauthorized operational classes remain separate; scope adoption grants no operational authority.',
    'Same-scope genuine R06 review and separate R08 decision remain absent; this assistant review cannot supply either.',
    'Full resource/cost rules,both Readers,caps/guards,new paths/failures and unchanged reserve rules remain binding without capacity/service/900 inference.',
    'Changed authority/body/scope/runtime/domain/epoch/key/policy/limits invalidate affected reviews before progression without implicit rebind.',
    'RQ02/A02 remain stopped; only genuine A01 acceptance permits considering RQ02 under its own limits,never automatic contact.',
    'CE12 remains separately deferred; final execution is not a new prelaunch prerequisite and claim is not its own prerequisite.',
    'I122/CP07/component/PJC115-R2/D5/IR03 negative state remains preserved with no new source,record,authority,destination,quota or execution.'
]


def reconstruct():
    d=rd(SUBJECT)
    result=inspect(d)
    pins={**d['input_pins'],**{path:sha(path) for path in sorted(PRIOR_FILES)}}
    assert len(pins)==1067
    verify_blobs(pins)
    return dict(schema='d5.i254-source-reconstruction.v1',increment='I254',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        subject=pin(SUBJECT),input_pins=pins,independent_reconstruction=result,
        criteria=[dict(id='RV%02d'%(i+1),criterion=text,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,text in enumerate(CRITERIA)],
        current_effect={**d['current_effect'],'A01_RQ01_documentary_reviewed':True})


def own_rejections(d):
    cases=[
        ('authority_slot_omitted',('authority_evidence_requests',),d['authority_evidence_requests'][:-1]),
        ('authority_role_substituted',('authority_evidence_requests',1,'exact_existing_requirement','required_role'),'R01'),
        ('authority_chain_fabricated',('authority_evidence_requests',2,'actual_preexisting_authority_chain_or_body'),{}),
        ('entry_stop_bypassed',('entry_gate','SD01_stop_active'),False),
        ('future_W02_edge_added',('entry_gate','W02_identity_requirements_used_as_eligibility_criteria_not_future_W02_acceptance_precondition'),False),
        ('request_return_omitted',('unsent_request','required_return_ids'),['RT01','RT02','RT03','RT04']),
        ('request_contact_granted',('unsent_request','contact_authorized'),True),
        ('scope_section_omitted',('scope_manifest_requirements',),d['scope_manifest_requirements'][:-1]),
        ('scope_dimension_fabricated',('scope_manifest_requirements',0,'documentary_requirement_count'),7),
        ('logical_source_omitted',('logical_sources',),d['logical_sources'][:-1]),
        ('source_hash_predicted',('logical_sources',5,'actual_body_digest_or_runtime_mapping'),'UNVERIFIED_TEST_LABEL'),
        ('policy_version_omitted',('known_vs_missing','policy_document_pins'),d['known_vs_missing']['policy_document_pins'][:-1]),
        ('future_freeze_required',('known_vs_missing','W01_logical_scope_does_not_require_actual_future_W03_hashes_or_freeze'),False),
        ('separation_rule_omitted',('eligibility_boundary','exact_separation_matrix'),d['eligibility_boundary']['exact_separation_matrix'][:-1]),
        ('R01_R02_overlap_removed',('eligibility_boundary','exact_overlap_policy','no_blanket_R01_R02_separation_added'),False),
        ('return_group_omitted',('requested_returns',),d['requested_returns'][:-1]),
        ('return_source_omitted',('requested_returns',2,'W01_requirement_sources'),d['requested_returns'][2]['W01_requirement_sources'][:-1]),
        ('deliverable_authority_missing',('W01_deliverable_coverage',0,'authority_return_id'),'RT05'),
        ('criterion_omitted',('acceptance_checklist',),d['acceptance_checklist'][:-1]),
        ('criterion_primary_review_fabricated',('acceptance_checklist',8,'actual_R06_primary_review'),'UNVERIFIED_TEST_LABEL'),
        ('criterion_status_promoted',('acceptance_checklist',11,'disposition'),'ACCEPTED_TEST_LABEL'),
        ('exit_criteria_dropped',('W01_exit_coverage',0,'required_acceptance_criteria'),['AC01']),
        ('material_evaluation_fabricated',('missing_or_rejected_material','actual_material_evaluations'),1),
        ('action_permission_fabricated',('authority_by_action','exact_existing_ledger',8,'authorized_now'),True),
        ('reserve_changed',('preserved_cost_scope_and_limits','exact_resource_rules','reserve_transfers_applied'),1),
        ('handoff_completed',('handoff','actual_A01_completion_or_handoff'),'UNVERIFIED_TEST_LABEL'),
        ('claim_as_own_prerequisite',('handoff','exact_final_route_boundary','claim_not_its_own_precondition'),False),
        ('scope_change_transferred',('change_control','affected_entry_authority_scope_or_body_change_requires_invalidation_and_fresh_genuine_review'),False),
        ('A01_accepted',('current_effect','A01_accepted'),True),
        ('assistant_R08',('producer','separate_R08_acceptance'),True)]
    results=[]
    for name,path,value in cases:
        mutant=copy.deepcopy(d)
        node=mutant
        for key in path[:-1]:
            node=node[key]
        node[path[-1]]=value
        try:
            inspect(mutant)
        except AssertionError:
            results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return results


def build_review(rec):
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT))
    exists=Path.exists
    assert previous['build_candidate']()==rd(SUBJECT)
    prep=previous['build_review']()
    assert prep==rd(PRIOR_PREP) and Path.exists is exists
    return dict(schema='d5.i254-documentary-review.v1',increment='I254',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),reconstruction=pin(RECON),
        verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_A01_RQ01_CONSISTENT_ENTRY_AUTHORITY_AND_GENUINE_SCOPE_ACCEPTANCE_MISSING',findings=[],
        criteria=rec['criteria'],independent_reconstruction=rec['independent_reconstruction'],
        counts=dict(input_pins=1067,authority_slots=3,scope_sections=12,logical_source_paths=6,policy_documents=8,separation_requirements=14,
            requested_returns=5,W01_deliverables=3,acceptance_criteria=12,W01_exits=3,review_criteria=len(CRITERIA),
            actual_authorities_verified=0,actual_received_bodies=0,actual_lots_accepted=0,prelaunch_gates_closed=0,resource_obligations_closed=0),
        inherited_I253_rejection_checks=prep['rejection_checks'],additional_I254_rejection_checks=own_rejections(rd(SUBJECT)),
        clarifications=[
            'EA01/EA02/EA03 need genuinely preexisting independently authentic authority/provenance and eligibility; future W02 appointments or bundle/root cannot be their sole forecast justification.',
            'W02 identity/separation rules are criteria for current entry eligibility, not a requirement that future W02 be accepted before A01. Final actor completeness remains in its own phase.',
            'Logical scope acceptance does not require future W03 effective hashes or freeze. Unknown source/runtime/image/caller/platform facts remain absent; document policy pins are not actual adoption.',
            'AC12 is a rule governing a possible future transition. It neither requires RQ02 already sent nor treats A01 as its own accepted predecessor; its three exits remain unaccepted.',
            'RT05 and AC09/AC10 require genuine competent R06 review and separate R08 decision. The same assistant documentary review is neither one and creates no canonical appointment or independent acceptance.',
            'W01 scope section counts measure JSON container dimensions only, not complete proof-body counts or verified runtime premises. Exact pinned content and complete material remain required.',
            'RQ01 remains unsent and no contact is authorized. RQ02 may only be considered after genuine A01 acceptance, under its own authority and limits; another documentary PASS supplies no material.'],
        source_reconstruction=dict(primary_source_checks=True,I253_candidate_and_preparation_reproduced=True,
            prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        current_effect=rec['current_effect'],provenance=dict(identity='Same Codex assistant/chat as I253',documentary_review_only=True,
            actor_independent=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['Entry authority and genuine same-scope primary/separate decisions remain missing. A01/W01 unaccepted,SD01 active,no RQ02/A02 progress.',
            'No authority,appointment,scope adoption,material receipt or real acceptance is created. Thirty gates and E01-E05 remain open; CE12 separately deferred.',
            'No product/component execution,source change,build,platform probe,signing,contact,provisioning,configuration,claim,receipt,quota,reserve,binding or D5 change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I254-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage/roles/authority checks and in-memory documentary mutations. No target import/compile/discovery/tests/execution/build/benchmark/crypto/signing/keygen/enrollment/provisioning/contacts/platform/CPU/IO/clock/ledger/process/endpoint probes or configuration.',
            over400_lines=True,reason='Single A01/RQ01 documentary review with primary reconstruction,pins,rejection checks and preservation; overage declared,no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_material_authority_scope_acceptance_execution_or_D5_closure=True))


def main():
    rec=reconstruct()
    assert rec==rd(RECON)
    review=build_review(rec)
    assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL)
    preserved={**prior['preserved_published754'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==759
    seal=rd(SEAL)
    assert seal['schema']=='d5.i254-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published759']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I254',input_pins=1067,preserved_published_files=759,new_files=5,review_criteria=len(CRITERIA),
        inherited_rejections=len(review['inherited_I253_rejection_checks']),additional_rejections=len(review['additional_I254_rejection_checks']),findings=review['findings'],
        SD01_stop_active=True,prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
