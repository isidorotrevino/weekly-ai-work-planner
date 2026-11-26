#!/usr/bin/env python3
"""I272 RQ01/RT01 documentary review; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'dee12c930c03ee0ee54e036e4f793366a7b776e6'
DATE = '2026-11-26'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
A01 = P+'D5-I251-A01-RQ01-ENTRY-AUTHORITY-SCOPE-CANDIDATE.json'
HANDOFF = P+'D5-I269-A01-A08-CONSOLIDATED-HANDOFF-CANDIDATE.json'
SUBJECT = P+'D5-I271-RQ01-RT01-ENTRY-AUTHORITY-REQUEST-CANDIDATE.json'
PRIOR_PREP = P+'D5-I271-preparation-review.json'
PRIOR_AUDIT = P+'D5-I271-audit.py'
PRIOR_SEAL = P+'D5-I271-integrity.json'
PRIOR_DOC = 'docs/design/D5-I271-RQ01-RT01-ENTRY-AUTHORITY-REQUEST.md'
PRIOR_FILES = {SUBJECT,PRIOR_PREP,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I272-I271-source-reconstruction.json'
REVIEW = P+'D5-I272-I271-documentary-review.json'
AUDIT = P+'D5-I272-audit.py'
SEAL = P+'D5-I272-integrity.json'
DOC = 'docs/design/D5-I272-I271-RQ01-RT01-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_RQ01_RT01_REVIEW_PREEXISTING_AUTHORITY_AND_GENUINE_ELIGIBILITY_MISSING_SD01_ACTIVE_NOT_ADMITTED'


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


BOUNDARIES = 'entry_gate eligibility_boundary known_vs_missing authority_by_action intake_sequence missing_or_rejected_material preserved_cost_scope_and_limits handoff change_control'.split()
SECTION_NAMES = 'availability authority_chain identity_eligibility scope_and_currentness review_provenance gaps'.split()
TOPICS = 'scope entry_authority bodies canonical_people independence no_reverse_dependency logical_scope validity delivery real_reviews partial_not_complete gaps invalidation no_send no_operations no_release'.split()


def inspect(d):
    a,acq,h=rd(A01),rd(ACQUISITION),rd(HANDOFF)
    assert d['request_document_id']=='PGE251-RQ01-RT01-REQUEST-CANDIDATE-01'
    assert (d['lot_id'],d['request_id'],d['return_id'])==('A01','RQ01','RT01') and d['original_A01']==pin(A01)
    for refkey,valuekey,section in [('original_RQ01_source','exact_original_RQ01','unsent_request'),('original_RT01_source','exact_original_RT01','requested_returns/0')]:
        assert d[refkey]==pin(A01,'/'+section) and d[valuekey]==fragment(d[refkey])
    assert d['exact_original_RQ01']==a['unsent_request'] and d['exact_original_RT01']==a['requested_returns'][0]
    assert d['handoff_entry_source']==pin(HANDOFF,'/first_material_request') and d['exact_handoff_entry']==fragment(d['handoff_entry_source'])==h['first_material_request']
    draft=d['unsent_request'];assert draft['subject'] and draft['text'] and draft['recipient_role_only']==a['unsent_request']['recipient_role_only']
    assert draft['is_draft_only'] is True and draft['sent'] is False and draft['contact_authorized'] is False;missing(draft)
    rows=d['subject_evidence_requests'];assert [r['id'] for r in rows]==['EA01','EA02','EA03']
    assert [r['required_role'] for r in rows]==['SCOPE_AUTHORITY','R06','R08']
    for i,row in enumerate(rows):
        src=a['authority_evidence_requests'][i]
        assert row['source']==pin(A01,'/authority_evidence_requests/'+str(i)) and row['exact_original_requirement']==fragment(row['source'])==src
        assert row['subject']==src['exact_existing_requirement']['subject'] and row['required_role']==src['exact_existing_requirement']['required_role']
        assert row['mandatory_material_fields']==src['required_independent_material_fields'] and len(row['mandatory_material_fields'])==7
        assert row['requested_return_sections']==SECTION_NAMES;missing(row)
    sections=d['requested_information_sections'];assert [r['name'] for r in sections]==SECTION_NAMES
    for row in sections:
        assert row['title'] and row['requirements'] and row['applies_to']==['EA01','EA02','EA03']
        assert row['original_RT01_requirement']==pin(A01,'/requested_returns/0') and row['universal_contract_source']==pin(ACQUISITION,'/evidence_delivery_contract');missing(row)
    universal=d['universal_delivery_requirement'];assert universal['source']==pin(ACQUISITION,'/evidence_delivery_contract')
    assert universal['exact_requirement']==fragment(universal['source'])==acq['evidence_delivery_contract'] and universal['mandatory_fields']==acq['evidence_delivery_contract']['mandatory_return_fields']
    assert len(universal['mandatory_fields'])==8
    truth(universal,['known_logical_target_not_effective_freeze','unavailable_effective_identifiers_or_hashes_remain_null_no_predictive_values','no_actual_positive_runtime_or_authority_record_defined'])
    inherited=d['inherited_A01_boundaries'];assert [r['section'] for r in inherited]==BOUNDARIES
    for row,s in zip(inherited,BOUNDARIES):assert row['source']==pin(A01,'/'+s) and row['exact_requirement']==fragment(row['source'])==a[s]
    entry=a['entry_gate'];truth(entry,['SD01_stop_active','no_future_W02_appointment_A07_bundle_or_root_as_sole_entry_authority','no_A01_self_authorization_from_empty_predecessor_list_or_this_user_document_request','W02_identity_requirements_used_as_eligibility_criteria_not_future_W02_acceptance_precondition'])
    assert entry['actual_authority_verified'] is False and entry['actual_scope_accepted'] is False
    eligibility=a['eligibility_boundary'];assert len(eligibility['exact_separation_matrix'])==14
    assert [r['id'] for r in eligibility['exact_separation_matrix']]==['SP%02d'%i for i in range(1,15)]
    truth(eligibility,['all_preparers_and_source_authors_in_exclusion_scope','no_assistant_git_account_role_label_key_or_signature_alone_as_canonical_human_or_independence','no_blanket_R01_R02_separation_or_future_full_roster_required_for_A01'])
    checklist=d['RT01_intake_checklist'];assert [r['id'] for r in checklist]==['RC%02d'%i for i in range(1,17)] and [r['topic'] for r in checklist]==TOPICS
    for row in checklist:
        assert row['criterion'] and row['disposition']=='PENDING_GENUINE_PREEXISTING_AUTHORITY_AND_ELIGIBILITY';missing(row)
    follow=d['complete_A01_followthrough'];assert follow['remaining_return_ids']==['RT02','RT03','RT04','RT05']
    assert follow['remaining_return_sources']==[pin(A01,'/requested_returns/'+str(i)) for i in range(1,5)]
    for key,section,count in [('A01_intake_source','acceptance_checklist',12),('A01_deliverable_source','W01_deliverable_coverage',3),('A01_exit_source','W01_exit_coverage',3)]:
        assert follow[key]==pin(A01,'/'+section) and fragment(follow[key])==a[section] and len(a[section])==count
    truth(follow,['RT01_intake_not_complete_A01_or_RQ02_authority','all_A01_criteria_and_reviews_before_downstream_consideration'])
    assert follow['RQ02_or_other_lot_enabled'] is False;missing(follow)
    existing=d['material_routes']['existing_material'];truth(existing,['only_genuinely_supplied_existing_material_with_own_authorized_provenance'])
    assert existing['provided_real_bodies']==existing['rejected_real_bodies']==[] and type(existing['actual_evaluations']) is int and existing['actual_evaluations']==0
    missing({k:v for k,v in existing.items() if k!='actual_evaluations'})
    gap=d['material_routes']['missing_material'];truth(gap,['SD01_stop_active','missing_authority_or_body_keeps_RT01_and_A01_unaccepted','no_fabricated_authority_body_human_hash_provider_or_calendar','no_global_absence_or_infeasibility_from_missing_evidence','separate_exact_authority_for_any_new_contact_operational_action_or_material_generation']);missing(gap,['actual_work_performed'])
    assert len(d['critical_boundaries'])==18 and all(v is True for v in d['critical_boundaries'].values())
    final=d['final_route_boundary'];assert final['source']==pin(ACQUISITION,'/final_route_boundary') and final['exact_requirement']==fragment(final['source'])==acq['final_route_boundary']
    assert final['current_run_command'] is None;missing(final,['actual_final_route_or_receipt_authorized'])
    assert d['current_effect']=={**h['current_effect'],'RQ01_RT01_focused_documentary_request_prepared':True,'RQ01_RT01_request_sent':False,'actual_RT01_authority_eligibility_intake_or_acceptance_created':False}
    assert all(d['producer'][k] is False for k in ['actor_independent','competent_primary_role_review','separate_R08_acceptance','external_contacts_made'])
    pointers(d)
    return dict(entry_subject_roles={r['id']:r['required_role'] for r in rows},mandatory_material_field_groups_per_subject=7,universal_return_fields=8,
        information_sections=SECTION_NAMES,RT01_checklist_topics=TOPICS,complete_A01_remaining_returns=follow['remaining_return_ids'],A01_intake_criteria=12,A01_deliverables=3,A01_exits=3,
        separation_requirements=14,RT01_not_complete_A01=True,W02_eligibility_not_backward_acceptance_dependency=True,actual_received_bodies=0,actual_genuine_authorities_or_acceptances=0)

CRITERIA = [
'RQ01/RT01 exact original A01 request and return plus I269 entry boundary remain pinned and unchanged.',
'Focused local draft preserves recipient by role only,no actual people/channels/contact authority/delivery or sending.',
'EA01 scope authority,EA02 R06 and EA03 R08 exact subject/role mappings remain requirements,not three actual or necessarily distinct people.',
'All seven mandatory material groups per subject retain complete original authority/evidence requirements.',
'Six information sections cover bodies,authority chain,identity/eligibility,scope/currentness,review provenance and gaps.',
'Eight universal delivery fields retain complete contract with applicable scope/assumptions/provenance/decisions and unknown effective facts null.',
'Authority must genuinely preexist under own independent provenance,not this request,user docs permission,assistant/Git,self assertion or future W02/bundle/root as sole basis.',
'A01 empty predecessor list is not self-authorization and logical target documentation is not canonical scope adoption.',
'W02 supplies eligibility criteria,not backward W02 acceptance,full future roster or CE10 requirement before A01.',
'Canonical humans/aliases,competence/appointments and applicable purpose/key/custody need genuine complete bodies and current scope.',
'All14 human/key exclusions and all preparers/source authors retained; strings/keys/signatures/role labels alone prove no identity or independence.',
'R01/R02 qualified overlap remains permitted under own later rules,no blanket prohibition or preapproval of future contributors.',
'Body availability,immutable locator,bytes/digest,author/provider/custody and all actual reference instances remain genuine requirements.',
'Issuer/delegation/scope/allowed-denied actions/validity/currentness/revocation need own proof,no host date or self-signature as sole assurance.',
'Logical PGO181 candidate02/PFC126-03/I122 scope remains distinct from effective W03 source/runtime/image freeze and operational authority.',
'No invented effective identifier/predictive hash,unknown-as-zero,template/flag/document hash as truth or actual authority record.',
'Sixteen RC questions organize RT01 review and are distinct from twelve complete A01 acceptance criteria.',
'If genuine review bodies already exist they may be supplied under own provenance; conditional wording never waives missing evidence or manufactures decisions.',
'RT05 keeps genuine R06 primary/separate R08 review of all A01,not same-assistant documentary PASS or commit/push.',
'RT01 supplied or accepted alone does not complete A01;RT02-RT05,three deliverables/three exits/twelve criteria and genuine decisions remain required.',
'RQ02/downstream remains disabled,SD01 active,all subjects/checklist/material unaccepted and no evaluations.',
'Nine full A01 boundaries preserve entry,eligibility,known/missing,authority,intake,gaps,costs,handoff and invalidation.',
'Gaps preserve exact missing subject/body/authority/scope/dependents and separately scoped work/authority without invented provider/calendar/infeasibility.',
'Changed contributor/body/source/runtime/scope/epoch/key/policy invalidates any affected A01-A08 before progress,no automatic acceptance/proof transfer or rebind.',
'Only genuinely supplied existing material with authorized provenance;no contact/fetch/verification service or nomination/enrollment now.',
'No actual authority issuance,credential/preparation record,signature/keygen/crypto/snapshot/C/Q/root/bundle/mapping/claim/receipt/configuration.',
'Both Readers/global reference costs,guards/outputs/caps/quotas/reserves retained,no hidden runtime inputs or free offline work.',
'CE12/private receipt remains separately deferred,with four external preclaim requirements and fifth claim/protected construction before receipt.',
'Claim is not own precondition,no free retry/reuse;final E06/Q/root/claim/spawn/receipt not new entry/prelaunch antecedent.',
'All genuine authority/eligibility/review/acceptance bodies remain missing;documentary audit proves no human competence,truth,capacity,service or900 fit.',
'I122/CP07/atomicity/component/E06/IR03 negative state remains,no SOURCE_CAPACITY_VERIFIED/certificate/PJC115-R2/D5 release.',
'Publication is local documentary work only,no operational execution,quota/reserve/binding/authority/destination/certificate change.'
]


def reconstruct():
    d=rd(SUBJECT);result=inspect(d);pins={**d['input_pins'],**{p:sha(p) for p in PRIOR_FILES}}
    assert len(pins)==1157;verify_blobs(pins)
    return dict(schema='d5.i272-source-reconstruction.v1',increment='I272',date=DATE,timezone='Europe/Madrid',base_commit=BASE,subject=pin(SUBJECT),input_pins=pins,
        independent_reconstruction=result,criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],
        current_effect={**d['current_effect'],'RQ01_RT01_focused_documentary_request_reviewed':True})


def own_rejections(d):
    cases=[
('return_reassigned',('return_id',),'RT02'),('original_pointer',('original_RT01_source','json_pointer'),'/requested_returns/1'),
('handoff_entry_changed',('exact_handoff_entry','return_key'),'A08/GD01'),('subject_missing',('subject_evidence_requests',),d['subject_evidence_requests'][:-1]),
('subject_duplicate',('subject_evidence_requests',2,'id'),'EA02'),('scope_role_changed',('subject_evidence_requests',0,'required_role'),'R06'),
('subject_scope_changed',('subject_evidence_requests',0,'subject'),'UNVERIFIED_TEST_LABEL'),('field_group_missing',('subject_evidence_requests',1,'mandatory_material_fields'),[]),
('section_coverage_missing',('subject_evidence_requests',1,'requested_return_sections'),['availability']),('section_missing',('requested_information_sections',),d['requested_information_sections'][:-1]),
('section_scope_changed',('requested_information_sections',0,'applies_to'),['EA01']),('section_source_changed',('requested_information_sections',0,'original_RT01_requirement','json_pointer'),'/requested_returns/1'),
('universal_field_missing',('universal_delivery_requirement','mandatory_fields'),[]),('logical_as_freeze',('universal_delivery_requirement','known_logical_target_not_effective_freeze'),False),
('boundary_missing',('inherited_A01_boundaries',),d['inherited_A01_boundaries'][:-1]),('future_W02_authority',('inherited_A01_boundaries',0,'exact_requirement','no_future_W02_appointment_A07_bundle_or_root_as_sole_entry_authority'),False),
('separation_missing',('inherited_A01_boundaries',1,'exact_requirement','exact_separation_matrix'),[]),('future_roster_required',('inherited_A01_boundaries',1,'exact_requirement','no_blanket_R01_R02_separation_or_future_full_roster_required_for_A01'),False),
('RC_missing',('RT01_intake_checklist',),d['RT01_intake_checklist'][:-1]),('RC_topic_changed',('RT01_intake_checklist',0,'topic'),'no_release'),
('RC_disposition_promoted',('RT01_intake_checklist',0,'disposition'),'ACCEPTED'),('RT05_missing',('complete_A01_followthrough','remaining_return_ids'),['RT02','RT03','RT04']),
('A01_criteria_wrong_source',('complete_A01_followthrough','A01_intake_source','json_pointer'),'/authority_evidence_requests'),
('remaining_pointer_changed',('complete_A01_followthrough','remaining_return_sources',3,'json_pointer'),'/requested_returns/3'),
('all_reviews_waived',('complete_A01_followthrough','all_A01_criteria_and_reviews_before_downstream_consideration'),False),
('foreign_provenance',('material_routes','existing_material','only_genuinely_supplied_existing_material_with_own_authorized_provenance'),False),
('body_fabricated',('material_routes','existing_material','provided_real_bodies'),['UNVERIFIED_TEST_LABEL']),('evaluation_fabricated',('material_routes','existing_material','actual_evaluations'),1),
('gap_as_global_infeasibility',('material_routes','missing_material','no_global_absence_or_infeasibility_from_missing_evidence'),False),
('gap_as_permission',('material_routes','missing_material','separate_exact_authority_for_any_new_contact_operational_action_or_material_generation'),False),
('proof_transfer',('critical_boundaries','missing_or_changed_material_keeps_SD01_and_invalidates_affected_A01_A08_no_automatic_transfer'),False),
('receipt_as_precondition',('final_route_boundary','exact_requirement','no_final_route_execution_claim_spawn_receipt_as_new_precondition_of_prelaunch_acceptance'),False),
('claim_self_condition',('final_route_boundary','exact_requirement','claim_not_own_precondition_no_free_retry_uncertain_partial_expired_states'),False),
('intake_created',('current_effect','actual_RT01_authority_eligibility_intake_or_acceptance_created'),True),('assistant_R08',('producer','separate_R08_acceptance'),True)]
    results=[]
    for name,path,value in cases:
        mutant=copy.deepcopy(d);node=mutant
        for key in path[:-1]:node=node[key]
        node[path[-1]]=value
        try:inspect(mutant)
        except AssertionError:results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:raise AssertionError(name)
    return results


def build_review(rec):
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));exists=Path.exists
    assert previous['build_candidate']()==rd(SUBJECT)
    prep=previous['build_review']();assert prep==rd(PRIOR_PREP) and Path.exists is exists
    return dict(schema='d5.i272-documentary-review.v1',increment='I272',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),reconstruction=pin(RECON),verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_PREEXISTING_AUTHORITY_ELIGIBILITY_AND_GENUINE_DECISIONS_PENDING',findings=[],
        criteria=rec['criteria'],independent_reconstruction=rec['independent_reconstruction'],
        counts=dict(input_pins=1157,preserved_published_files=849,entry_subjects=3,subject_material_groups=7,universal_return_fields=8,information_sections=6,RT01_questions=16,
            full_A01_criteria=12,A01_deliverables=3,A01_exits=3,remaining_A01_returns=4,inherited_boundaries=9,separation_requirements=14,review_criteria=len(CRITERIA),
            actual_received_bodies=0,actual_genuine_authorities_or_acceptances=0,prelaunch_gates_closed=0,resource_obligations_closed=0),
        inherited_I271_rejection_checks=prep['rejection_checks'],additional_I272_rejection_checks=own_rejections(rd(SUBJECT)),
        clarifications=[
            'EA01/EA02/EA03 are requirements for scope authority,R06 and R08,not invented canonical people or a proof of3 distinct humans. All people/authority/eligibility/appointments remain genuinely missing.',
            'A01 has no lot predecessor but is not self-authorized. User request authorizes docs/audit/publication only,not canonical scope adoption,nomination or independent review authority. Future W02/bundle/root cannot be sole entry authority.',
            'W02 eligibility policy applies without requiring future W02 acceptance,complete future roster or CE10 approvals before A01. All14 human/key rules and preparers remain conserved; no blanket R01/R02 separation or future-author preapproval.',
            'Sixteen RC questions describe focused RT01 review and do not replace12 original A01 acceptance criteria. RT01 alone cannot replace RT02-RT05,three deliverables/three exits and genuine own R06/R08 decisions or enable RQ02.',
            'If genuine review bodies already exist wording limits this draft to existing available material under own authorized provenance. It never waives actual missing evidence or grants approval for generating authority/decisions. RT05 complete A01 reviews remain pending.',
            'Universal effective scope identifiers/derivations are declared where applicable; unknown effective W03 facts remain null,no predictive source/runtime/image hash or freeze required to complete logical A01 scope.',
            'Current inventory null,provided/rejected lists empty,evaluations0,SD01 active,RQ01 unsent. A further same-assistant PASS or commit/push supplies no genuine material or acceptance.',
            'CE12/private receipt remains deferred under separate exact authority; no final E06/Q/root/claim/spawn/receipt new entry/prelaunch prerequisite or automatic certificate/PJC115-R2/D5 release.'],
        source_reconstruction=dict(primary_source_checks=True,I271_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        current_effect=rec['current_effect'],provenance=dict(identity='Same Codex assistant/chat as I271/A01',documentary_review_only=True,actor_independent=False,competent_primary_role_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['Preexisting EA01 scope authority and R06/R08 genuine eligibility/competence/appointment/independence bodies remain missing,SD01 active,RQ01/RT01 unsent. No positive intake or acceptance created.',
            'All A01-A08,30 gates,E01-E05/20 resource criteria,PJC115-R2 and D5 remain unaccepted/open. Documentary pin/JSON/graph/mutation PASS proves no actual authority,truth,capacity,service or900-second fit.',
            'No product/component execution,positive crypto/signing/keygen/enrollment/contact/provision/configuration/probe,quota/reserve/binding/authority/destination/certificate change. CE12/final route remain separate and deferred.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I272-audit.py',expected_result=STATUS,over400_lines=True,
            reason='One focused RQ01/RT01 review with independent authority/eligibility/source reconstruction,pins,rejection checks and preservation; overage declared,no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage/graph checks and in-memory mutations only; no target import,compile,discovery,tests,execution,build,benchmark,codec,crypto,signing,keygen,enrollment,contacts,provision,configuration or platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes.'),
        publication=dict(commit_and_push_requested=True,publication_not_genuine_authority_eligibility_review_acceptance_delivery_execution_or_D5_closure=True))


def main():
    rec=reconstruct();assert rec==rd(RECON)
    review=build_review(rec);assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published844'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)};assert len(preserved)==849
    seal=rd(SEAL);assert seal['schema']=='d5.i272-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published849']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for p,h in mapping.items():assert sha(p)==h,p
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,input_pins=1157,preserved_published_files=849,new_files=5,review_criteria=len(CRITERIA),inherited_rejections=len(review['inherited_I271_rejection_checks']),additional_rejections=len(review['additional_I272_rejection_checks']),findings=review['findings'],prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
