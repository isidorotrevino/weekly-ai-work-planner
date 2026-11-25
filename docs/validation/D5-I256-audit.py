#!/usr/bin/env python3
"""I256: documentary review of A02/RQ02, without target execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'b01db76fdfaf658fc899c24b7f188f19757a03db'
DATE = '2026-11-25'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
W02 = P+'D5-I223-W02-PEOPLE-AND-ANCHORS-CANDIDATE.json'
A01 = P+'D5-I251-A01-RQ01-ENTRY-AUTHORITY-SCOPE-CANDIDATE.json'
SUBJECT = P+'D5-I251-A02-RQ02-PEOPLE-APPOINTMENTS-ANCHORS-CANDIDATE.json'
PRIOR_PREP = P+'D5-I255-preparation-review.json'
PRIOR_AUDIT = P+'D5-I255-audit.py'
PRIOR_SEAL = P+'D5-I255-integrity.json'
PRIOR_DOC = 'docs/design/D5-I255-A02-RQ02-PEOPLE-APPOINTMENTS-ANCHORS.md'
PRIOR_FILES = {SUBJECT,PRIOR_PREP,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I256-I255-source-reconstruction.json'
REVIEW = P+'D5-I256-I255-documentary-review.json'
AUDIT = P+'D5-I256-audit.py'
SEAL = P+'D5-I256-integrity.json'
DOC = 'docs/design/D5-I256-I255-A02-RQ02-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_A02_RQ02_REVIEW_A01_UNACCEPTED_PEOPLE_ANCHORS_AND_GENUINE_DECISIONS_PENDING_NOT_ADMITTED'


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


def missing(row, false_fields=()):
    for key,value in row.items():
        if key.startswith('actual_'):
            assert value is False if key in false_fields else value is None,key
    if 'accepted' in row:
        assert row['accepted'] is False


def truth(row, names):
    for name in names:
        assert row[name] is True,name


RETURN_SECTIONS = [
    ['dependency_gate','costs_and_authority'],['subject_category_inventory','identity_policy'],
    ['role_scope_matrix','identity_policy','overlap_policy'],['anchor_policy','schema_policy'],
    ['separation_matrix','overlap_policy','preparation_tracking','phase_boundary'],
    ['evidence_requirement_ledger','exit_predicate_dispositions','phase_boundary','costs_and_authority']]
REQUIREMENT_RETURNS = {
    'AP01':['IT01','IT04'],'AP02':['IT04'],'AP03':['IT02','IT03'],'AP04':['IT03','IT04'],
    'AP05':['IT06'],'AP06':['IT04'],'AP07':['IT04'],'AP08-ANCHOR-POLICY':['IT04'],'AP08-BUNDLE-APPROVAL':[],
    'AP09':['IT04','IT06'],'IR01':['IT02'],'IR02':['IT02'],'IR03':['IT03'],'IR04':['IT02'],'IR05':['IT02','IT03'],
    'IR06':['IT05'],'IR07':['IT05'],'IR08':['IT02','IT05'],'IR09':[]}
CRITERION_RETURNS = [['IT01'],['IT01','IT04'],['IT02'],['IT03'],['IT04'],['IT03','IT04'],['IT04'],['IT04'],
    ['IT03','IT05'],['IT02','IT05'],['IT02','IT05'],['IT04','IT06'],['IT06'],['IT01','IT05','IT06']]


def inspect(d):
    plan,acq,w=rd(PLAN),rd(ACQUISITION),rd(W02)
    lot,req=acq['acquisition_lots'][1],plan['work_packages'][1]
    assert (d['lot_id'],d['request_id'],d['work_package'],d['planned_deliverable_id'])==('A02','RQ02','W02',req['deliverable_id'])
    assert d['exact_acquisition_lot']==fragment(d['acquisition_lot_binding'])==lot
    assert d['exact_W02_requirement']==fragment(d['work_requirement_binding'])==req
    assert d['W02_documentary_checklist']['path']==W02
    gate=d['dependency_gate']
    assert gate['required_lot_ids']==['A01'] and gate['required_work_package_ids']==req['depends_on']==['W01']
    assert gate['exact_W02_dependency_requirement']==fragment(gate['W02_dependency_source'])==w['dependency_gate']
    assert gate['exact_current_A01_effect']==fragment(gate['A01_source'])==rd(A01)['current_effect']
    assert gate['A01_accepted'] is False and gate['W01_accepted'] is False
    truth(gate,['SD01_stop_active','no_documentary_I253_I254_PASS_as_A01_acceptance',
        'preparing_A02_draft_does_not_start_positive_intake_send_contact_nomination_or_discharge_A01'])
    missing(gate)
    draft=d['unsent_request']
    assert draft['original_draft']==lot['unsent_request_draft']
    assert draft['recipient_role_only']==lot['intended_recipient_role_kind']
    assert draft['required_return_ids']==['IT%02d'%i for i in range(1,7)]
    assert draft['is_draft_only'] is True and draft['sent'] is False and draft['contact_authorized'] is False
    missing(draft)
    returns=d['requested_returns']
    assert [r['id'] for r in returns]==draft['required_return_ids']
    for row,sections in zip(returns,RETURN_SECTIONS):
        assert row['requirements'] and row['title']
        assert row['W02_requirement_sources']==[pin(W02,'/'+section) for section in sections]
        assert fragment(row['universal_delivery_source'])==acq['evidence_delivery_contract']
        missing(row,['actual_received'])
    roles=d['role_evidence_requests']
    assert [r['id'] for r in roles]==['R%02d'%i for i in range(1,9)]
    for row,source in zip(roles,w['role_scope_matrix']):
        assert row['exact_role_requirement']==fragment(row['source'])==source
        assert row['required_return_id']=='IT03' and len(row['required_fields'])==5
        missing(row)
    subjects=d['subject_category_requests']
    assert len(subjects)==5 and [r['category'] for r in subjects]==[r['category'] for r in w['subject_category_inventory']]
    for row,source in zip(subjects,w['subject_category_inventory']):
        assert row['exact_category_requirement']==fragment(row['source'])==source
        assert row['required_return_ids']==['IT02','IT05'] and row['complete'] is False
        missing(row)
    ledger=d['evidence_requirement_requests']
    assert len(ledger)==19 and [r['id'] for r in ledger]==[r['id'] for r in w['evidence_requirement_ledger']]
    for row,source in zip(ledger,w['evidence_requirement_ledger']):
        assert fragment(row['source'])==source and row['normative_source']==source['source']
        normative=fragment(row['normative_source'])
        assert row['required_genuine_evidence']==source['exact_requirement']['required_genuine_evidence']==normative['required_genuine_evidence']
        for key in ['consumer_step','work_package_consumer']:
            assert row[key]==source[key]
        assert row['deferred_from_A02'] is source['deferred_from_W02']
        assert row['required_return_ids']==REQUIREMENT_RETURNS[row['id']]
        assert row['source_historical_metadata_not_reinterpreted_as_current_document_presence_or_actual_acceptance'] is True
        missing(row)
    active=[r for r in ledger if not r['deferred_from_A02']]
    deferred=[r for r in ledger if r['deferred_from_A02']]
    assert len(active)==17 and all(r['work_package_consumer']=='W02' for r in active)
    assert [(r['id'],r['consumer_step'],r['work_package_consumer']) for r in deferred]==[
        ('AP08-BUNDLE-APPROVAL','CE10','W12'),('IR09','CE08','W10')]
    expected_policies=['anchor_policy','identity_policy','separation_matrix','overlap_policy','schema_policy','phase_boundary','costs_and_authority','preserved_scope_and_gates']
    assert list(d['inherited_policies'])==expected_policies
    for key,row in d['inherited_policies'].items():
        assert row['exact_requirement']==fragment(row['source'])==w[key]
    anchor=d['inherited_policies']['anchor_policy']['exact_requirement']
    policy=anchor['exact_policy']
    assert anchor['CE10_future_approvals_required_to_accept_W02'] is False and anchor['CE10_may_authenticate_own_anchors'] is False
    assert policy['snapshot_max_lifetime_seconds']==3600 and policy['max_trusted_clock_error_seconds']==5
    assert policy['complete_sorted_unique_binding_key']==['purpose','key_id'] and policy['domain_separator_octets']==[0]
    assert policy['custody_domains']=={'R01_RUNTIME':'D5/PGO181/CUSTODY/v1/R01','R02_PLATFORM':'D5/PGO181/CUSTODY/v1/R02','R08_ACCEPTANCE':'D5/PGO181/CUSTODY/v1/R08'}
    assert len(d['inherited_policies']['separation_matrix']['exact_requirement'])==14
    assert w['phase_boundary']['W10_freeze_or_final_registry_completeness_required_for_W02'] is False
    assert all(value is True for value in d['authority_and_phase_rules'].values()) and len(d['authority_and_phase_rules'])==10
    track=d['documentary_contribution_tracking']
    assert fragment(track['W02_tracking_source'])==w['preparation_tracking']
    assert set(track['files'])=={SUBJECT,PRIOR_PREP,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
    truth(track,['git_hashes_or_assistant_label_not_canonical_human_provenance','no_backpin_C_acceptance_bundle_future_root'])
    assert track['full_preparer_list_or_final_completeness_claimed'] is False
    missing(track)
    delivers=d['W02_deliverable_coverage']
    assert [r['id'] for r in delivers]==['WD01','WD02','WD03']
    for i,row in enumerate(delivers):
        assert row['exact_requirement']==fragment(row['source'])==req['deliverables'][i]
        assert row['required_return_ids']==[['IT02','IT03','IT05'],['IT04'],['IT05']][i]
        assert row['authority_return_id']=='IT01' and row['review_return_id']=='IT06'
        missing(row)
    criteria=d['acceptance_checklist']
    ids=['AC%02d'%i for i in range(1,15)]
    assert [r['id'] for r in criteria]==ids
    for row,required in zip(criteria,CRITERION_RETURNS):
        assert row['criterion'] and row['required_return_ids']==required
        assert row['disposition']=='PENDING_A01_GENUINE_MATERIAL_AND_COMPETENT_DECISION'
        missing(row)
    exits=d['W02_exit_coverage']
    assert [r['id'] for r in exits]==['WX01','WX02','WX03']
    for i,row in enumerate(exits):
        assert row['exact_predicate']==fragment(row['source'])==req['exit_predicates'][i]
        assert row['required_acceptance_criteria']==ids
        missing(row)
    material=d['missing_material']
    assert material['actual_received_inventory'] is None and material['provided_real_bodies']==material['rejected_real_bodies']==[]
    assert type(material['actual_evaluations']) is int and material['actual_evaluations']==0
    assert material['actual_people_appointments_keys_or_anchors'] is None and material['actual_provider_or_schedule'] is None
    truth(material,['missing_or_ambiguous_authority_body_alias_eligibility_currentness_keeps_no_admission','no_global_absence_or_infeasibility_claim'])
    resource=d['preserved_resource_rules']
    assert resource['exact_requirement']==fragment(resource['source'])==acq['preserved_resource_and_cost_rules']
    truth(resource,['complete_bodies_and_all_costs_in_both_Readers_and_global_join_not_free_offline_work',
        'schemas_or_caps_not_actual_heap_CPU_capacity_service_or900_fit','no_truncation_or_new_Reader_member_output_helper_hidden_lookup_or_quota_reserve_change'])
    handoff=d['handoff']
    assert handoff['exact_A02_completion_predicate']==lot['completion_predicate'] and handoff['exact_A02_missing_stop']==lot['missing_or_failure_stop']
    assert handoff['next_lot']=='A03' and handoff['required_genuine_prior_lots']==['A01','A02']
    assert handoff['required_genuine_prior_lots']==acq['acquisition_lots'][2]['depends_on_lots']
    assert handoff['A03_or_RQ03_started_sent_or_accepted'] is False
    assert handoff['exact_final_route_boundary']==fragment(handoff['final_route_source'])==plan['prelaunch_handoff_and_CE12']
    truth(handoff,['prelaunch_not_conditioned_on_actual_final_E06_payload_Q_root_admission_claim_receipt','no_automatic_launch_certificate_PJC115_R2_or_D5_release'])
    missing(handoff,['actual_final_roster_registry_anchors_or_snapshots_created'])
    change=d['change_control']
    assert change['exact_requirement']==fragment(change['source'])==w['phase_boundary']
    truth(change,['changed_subject_alias_author_preparer_source_runtime_body_key_epoch_policy_revocation_invalidates_affected_reviews_before_progress',
        'no_automatic_old_approval_proof_or_appointment_transfer'])
    missing(change,['actual_refresh_or_active_rebind'])
    expected={**rd(A01)['current_effect'],'A02_RQ02_documentary_prepared':True,'A02_accepted':False,'RQ02_sent':False,
        'actual_people_anchors_appointments_or_key_bindings_accepted':False,'actor_registry_finalized':False,'anchor_registry_provisioned':False,'actual_A02_intake_progress_or_review_records_created':False}
    assert d['current_effect']==expected
    assert d['producer']['actor_independent'] is False and d['producer']['competent_R06_review'] is False
    assert d['producer']['separate_R08_acceptance'] is False and d['producer']['external_contacts_made'] is False
    pointers(d)
    return dict(role_decision_scopes={r['id']:r['exact_role_requirement']['required_decision_scopes'] for r in roles},
        subject_categories=[r['category'] for r in subjects],active_requirement_to_returns={r['id']:r['required_return_ids'] for r in active},
        deferred_consumers={r['id']:dict(step=r['consumer_step'],work=r['work_package_consumer']) for r in deferred},
        criterion_to_returns={r['id']:r['required_return_ids'] for r in criteria},
        all_W02_deliverables_and_exits_pending=True,A01_W01_unaccepted_SD01_active=True,actual_people_anchors_or_appointments_accepted=0,
        actual_received_bodies=0,actual_competent_primary_or_separate_decisions=0)


CRITERIA = [
    'A02/RQ02 preserves exact I251 lot,W02 requirements,A01 dependency and current negative predecessor state.',
    'Preparing documents is authorized without sending or starting positive intake; I253/I254 PASS does not accept A01.',
    'Eight roles preserve exact decision/competence scopes,appointments,purpose/key requirements and unknown actual people.',
    'Five subject categories cover source authors,all preparers,requester,proof authors/providers and custodians/signatories.',
    'Canonical humans/organizations/aliases/collisions require genuine authority; software principal,assistant or Git labels are not human identities.',
    'Competence and genuine appointment are scope/validity bound; authors/providers do not automatically become R03/R06/R08.',
    'Fourteen identity/key separation requirements remain exact; R01/R02 qualified overlap and separate role-domain approvals retain their proper phase.',
    'Independent anchor origin,provisioning,prior acceptance and external expected digest/epochs/policy preexist supplied registry bytes.',
    'Repo,C,bundle,root,supplied key,self-signature,TOFU,stale cache or hidden fetch cannot bootstrap trust.',
    'Purpose/key_id uniqueness and sorting,canonical actors,three domains and one NUL remain exact policy,not actual signatures.',
    'Closed schemas and proposed registry caps remain requirements with no trimming or cap-to-fit/resource proof inference.',
    'Trusted interval/currentness/epoch/revocation rules are preserved; host date is not freshness and offline status promises no instantaneous revocation.',
    'Nineteen requirements are traced directly to normative sources; seventeen apply now and two remain deferred.',
    'AP08 anchor policy/provisioning/acceptance is prior; AP08 actual same-core three-role bundle approvals belong to W12 and cannot authenticate own anchors.',
    'IR01-IR08 identity intake is provisional; IR09 complete final actors/preparers/registry belongs to W10,without future-author preapproval.',
    'Known authors/bodies and baseline authentication precede W09; W10 final freeze cannot authenticate resources retrospectively.',
    'Historical source metadata is frozen provenance,not current dossier absence or actual approval; existing CE dossiers supply no genuine material.',
    'Six returns and fourteen criteria cover all three W02 deliverables/exits with IT01 authority and IT06 genuine primary/separate decisions.',
    'Own documentary contribution tracking creates no enrolled human,authorship proof,positive preparation record or final preparer completeness.',
    'Preparation records retain genuine contribution/profile/schema requirements and no backpins to C/acceptance/bundle/future root.',
    'Complete evidence inventory,reference instances,bytes/digests/provenance/assumptions/currentness/reviews remain required; templates/hashes/flags are not truth.',
    'Zero actual supplied/rejected/evaluated material and null inventory do not establish acceptance or global absence/infeasibility.',
    'Both Readers and global resource joins retain all lookup/crypto/native/IO/registry/receipt/failure costs,unchanged quotas and reserves.',
    'Changed identity,alias,author,body,epoch/key/policy/revocation invalidates affected reviews without automatic appointment/proof transfer or active rebind.',
    'A03/RQ03 remains stopped,requiring genuine A01 and A02 first; no contact or downstream acceptance is authorized.',
    'CE12 remains deferred and final execution is not a new prelaunch condition; four preclaim prerequisites then actual claim/construction precede receipt.',
    'Same assistant review is not genuine competent R06 or separate R08 acceptance and creates no authority or operational action.',
    'I122/CP07/component/PJC115-R2/D5/IR03 negative state remains intact without product/component execution or quota change.'
]


def reconstruct():
    d=rd(SUBJECT)
    result=inspect(d)
    pins={**d['input_pins'],**{path:sha(path) for path in sorted(PRIOR_FILES)}}
    assert len(pins)==1077
    verify_blobs(pins)
    return dict(schema='d5.i256-source-reconstruction.v1',increment='I256',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        subject=pin(SUBJECT),input_pins=pins,independent_reconstruction=result,
        criteria=[dict(id='RV%02d'%(i+1),criterion=text,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,text in enumerate(CRITERIA)],
        current_effect={**d['current_effect'],'A02_RQ02_documentary_reviewed':True})


def own_rejections(d):
    cases=[
        ('A01_promoted',('dependency_gate','A01_accepted'),True),
        ('predecessor_omitted',('dependency_gate','required_lot_ids'),[]),
        ('contact_granted',('unsent_request','contact_authorized'),True),
        ('role_omitted',('role_evidence_requests',),d['role_evidence_requests'][:-1]),
        ('competence_scope_changed',('role_evidence_requests',5,'exact_role_requirement','required_decision_scopes'),['AUTHORITY_ISSUANCE']),
        ('human_fabricated',('role_evidence_requests',7,'actual_human_or_aliases'),'UNVERIFIED_TEST_LABEL'),
        ('category_omitted',('subject_category_requests',),d['subject_category_requests'][:-1]),
        ('category_finalized',('subject_category_requests',1,'complete'),True),
        ('normative_requirement_omitted',('evidence_requirement_requests',),d['evidence_requirement_requests'][:-1]),
        ('prior_anchor_waived',('evidence_requirement_requests',0,'required_genuine_evidence'),'UNVERIFIED_TEST_LABEL'),
        ('bundle_approval_required_early',('evidence_requirement_requests',8,'deferred_from_A02'),False),
        ('final_roster_required_early',('evidence_requirement_requests',18,'work_package_consumer'),'W02'),
        ('identity_requirement_return_removed',('evidence_requirement_requests',15,'required_return_ids'),[]),
        ('historical_metadata_as_current',('evidence_requirement_requests',8,'source_historical_metadata_not_reinterpreted_as_current_document_presence_or_actual_acceptance'),False),
        ('self_bootstrap_allowed',('inherited_policies','anchor_policy','exact_requirement','exact_policy','no_repo_C_bundle_or_self_signed_bootstrap'),False),
        ('expected_digest_self_selected',('inherited_policies','anchor_policy','exact_requirement','documentary_policy_hash_is_not_external_expected_registry_digest'),False),
        ('domain_separator_changed',('inherited_policies','anchor_policy','exact_requirement','exact_policy','domain_separator_octets'),[]),
        ('trusted_clock_error_expanded',('inherited_policies','anchor_policy','exact_requirement','exact_policy','max_trusted_clock_error_seconds'),6),
        ('separation_omitted',('inherited_policies','separation_matrix','exact_requirement'),d['inherited_policies']['separation_matrix']['exact_requirement'][:-1]),
        ('qualified_overlap_removed',('inherited_policies','overlap_policy','exact_requirement','no_blanket_R01_R02_separation_added'),False),
        ('late_authentication_allowed',('authority_and_phase_rules','real_W05_W08_authors_and_bodies_authenticated_before_W09_W10_not_retroactive'),False),
        ('preparer_identity_fabricated',('documentary_contribution_tracking','actual_accountable_canonical_human'),'UNVERIFIED_TEST_LABEL'),
        ('future_backpin_allowed',('documentary_contribution_tracking','no_backpin_C_acceptance_bundle_future_root'),False),
        ('return_group_omitted',('requested_returns',),d['requested_returns'][:-1]),
        ('deliverable_review_removed',('W02_deliverable_coverage',1,'review_return_id'),'IT04'),
        ('criterion_omitted',('acceptance_checklist',),d['acceptance_checklist'][:-1]),
        ('criterion_accepted',('acceptance_checklist',12,'accepted'),True),
        ('exit_coverage_reduced',('W02_exit_coverage',2,'required_acceptance_criteria'),['AC01']),
        ('reference_inventory_fabricated',('missing_material','actual_received_inventory'),[]),
        ('resource_costs_waived',('preserved_resource_rules','complete_bodies_and_all_costs_in_both_Readers_and_global_join_not_free_offline_work'),False),
        ('A03_dependency_removed',('handoff','required_genuine_prior_lots'),['A02']),
        ('claim_as_own_precondition',('handoff','exact_final_route_boundary','claim_not_its_own_precondition'),False),
        ('acceptance_transferred',('change_control','no_automatic_old_approval_proof_or_appointment_transfer'),False),
        ('A02_accepted',('current_effect','A02_accepted'),True)]
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
    return dict(schema='d5.i256-documentary-review.v1',increment='I256',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),reconstruction=pin(RECON),
        verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_CONDITIONAL_A02_RQ02_CONSISTENT_GENUINE_PEOPLE_ANCHORS_AND_ACCEPTANCE_MISSING',findings=[],
        criteria=rec['criteria'],independent_reconstruction=rec['independent_reconstruction'],
        counts=dict(input_pins=1077,roles=8,subject_categories=5,evidence_requirements=19,active_A02_requirements=17,deferred_requirements=2,
            separation_requirements=14,requested_returns=6,acceptance_criteria=14,W02_deliverables=3,W02_exits=3,review_criteria=len(CRITERIA),
            actual_people_or_anchors_accepted=0,actual_received_bodies=0,actual_lots_accepted=0,prelaunch_gates_closed=0,resource_obligations_closed=0),
        inherited_I255_rejection_checks=prep['rejection_checks'],additional_I256_rejection_checks=own_rejections(rd(SUBJECT)),
        clarifications=[
            'A01/W01 remains unaccepted and SD01 active. User requested documentary preparation/review of a conditional draft; this never sends RQ02 or starts positive A02 intake.',
            'External expected digest/epochs/policy and genuine prior anchor acceptance cannot be derived from supplied registry bytes,C,bundle,root or self-signature. Actual CE10/W12 approvals remain later consumers.',
            'Seventeen requirements apply to provisional A02: nine prior anchor/policy requirements and eight identity requirements. AP08-BUNDLE-APPROVAL is deferred W12; IR09 final completeness is deferred W10.',
            'Known authors/bodies and baseline facts must already be authentic before W09. W10 final freeze reconciles identical facts without retroactive authority or automatic transfer.',
            'Eight roles/five subject categories/fourteen separations are requirements for genuine humans,competence,appointments and purpose keys; this assistant,Git labels,distinct strings or hashes establish none of them.',
            'Historical source flags about dossier creation remain frozen provenance,not current absence. Existing CE dossiers are documentary and cannot substitute for real bodies,appointments,signatures or decisions.',
            'Final snapshots/C/bundle/currentness are checked at their own real boundaries under separate authority; date of review and offline status do not establish fresh trusted state or instantaneous revocation.',
            'A03/RQ03 only becomes a possible next consideration after genuine A01 and A02 acceptance under its own limits. This review provides no contact,crypto,enrollment,execution or D5 release authority.'],
        source_reconstruction=dict(primary_source_checks=True,I255_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,
            prior_Path_exists_restored=True,no_new_presence_projection=True),current_effect=rec['current_effect'],
        provenance=dict(identity='Same Codex assistant/chat as I255',documentary_review_only=True,actor_independent=False,
            competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['A01/W01 and A02/W02 remain unaccepted; SD01 active,RQ02 unsent,zero material/people/anchors/appointments accepted.',
            'No real independent R06/R08 review or canonical identity,authority,anchor provisioning,registry/snapshot/crypto validation is created. M01/M02 remain pending.',
            'Thirty gates,E01-E05 and D5 remain open. No product/component run,build,probe,contact,signing,configuration,claim,receipt,quota,reserve,binding or active authority/destination change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I256-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/role/requirement/phase checks and in-memory documentary mutations only. No target import/compile/discovery/tests/execution/build/benchmark/crypto/signing/keygen/enrollment/provisioning/contacts/platform/clock/CPU/IO/ledger/process/endpoint probes or configuration.',
            over400_lines=True,reason='One A02/RQ02 review with primary-source reconstruction,pins,rejection checks and preservation; overage declared,no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_evidence_people_anchor_authority_acceptance_execution_or_D5_closure=True))


def main():
    rec=reconstruct()
    assert rec==rd(RECON)
    review=build_review(rec)
    assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL)
    preserved={**prior['preserved_published764'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==769
    seal=rd(SEAL)
    assert seal['schema']=='d5.i256-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published769']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I256',input_pins=1077,preserved_published_files=769,new_files=5,review_criteria=len(CRITERIA),
        inherited_rejections=len(review['inherited_I255_rejection_checks']),additional_rejections=len(review['additional_I256_rejection_checks']),findings=review['findings'],
        SD01_stop_active=True,prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
