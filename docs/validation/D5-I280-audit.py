#!/usr/bin/env python3
"""I280 focused DB01 gap and reentry documentary review; no target execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'fc6dfb6f88ce8bb3e67fb4d157f5d6465b1d1c27'
DATE = '2026-11-27'
REQUEST = P+'D5-I277-RQ01-RT01-DELIVERY-AUTHORIZATION-REQUEST-CANDIDATE.json'
SOURCE_REVIEW = P+'D5-I278-I277-documentary-review.json'
SUBJECT = P+'D5-I279-DB01-ISSUER-UNIDENTIFIED-GAP.json'
PRIOR_CHECK = P+'D5-I279-documentary-check.json'
PRIOR_AUDIT = P+'D5-I279-audit.py'
PRIOR_SEAL = P+'D5-I279-integrity.json'
PRIOR_DOC = 'docs/design/D5-I279-DB01-ISSUER-UNIDENTIFIED-GAP.md'
PRIOR_FILES = {SUBJECT,PRIOR_CHECK,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I280-I279-source-reconstruction.json'
REVIEW = P+'D5-I280-I279-documentary-review.json'
AUDIT = P+'D5-I280-audit.py'
SEAL = P+'D5-I280-integrity.json'
DOC = 'docs/design/D5-I280-I279-DB01-GAP-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_DB01_GAP_REVIEW_ISSUER_UNIDENTIFIED_REENTRY_REQUIRES_GENUINE_MATERIAL_NOT_GRANTED_NOT_SENT_NOT_ADMITTED'


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


QUESTION = '¿Quién es la autoridad humana preexistente que puede autorizar esta entrega documental RQ01/RT01, y qué documento o referencia disponible acredita su facultad, ámbito y vigencia? Si todavía no está identificada, indícalo.'
ANSWER = 'todavía no está identificada'
REENTRY_FIELDS = ['canonical human issuer and complete aliases','available complete independently authentic authority/delegation body or reference with locator/bytes/digest/author/provider/custody',
'faculty to authorize this exact documentary contact, allowed/denied actions and scope','validity/currentness/revocation and own provenance','competent own-scope review of genuine material; no assistant or generic chat approval substitution']


def inspect(d):
    q,source_review=rd(REQUEST),rd(SOURCE_REVIEW)
    assert d['record_id']=='PGE251-RQ01-RT01-DB01-UNIDENTIFIED-ISSUER-GAP-01' and d['kind']=='DOCUMENTARY_USER_REPORTED_GAP_NOT_CANONICAL_AUTHORITY_EVIDENCE_OR_GENUINE_DECISION'
    assert d['request']==pin(REQUEST) and d['latest_documentary_review']==pin(SOURCE_REVIEW)
    report=d['user_report'];assert report['question']==QUESTION and report['answer_verbatim']==ANSWER and report['recorded_date']=='2026-11-27'
    assert report['provenance']=='User reply in this chat; conversational report only, not enrolled canonical issuer/provider or verified authority evidence'
    assert report['no_issuer_nomination_contact_permission_or_decision_inferred'] is True;missing(report)
    gap=d['DB01_disposition'];assert gap['source']==pin(REQUEST,'/authorization_binding_requirements/0') and gap['exact_original_requirement']==fragment(gap['source'])==q['authorization_binding_requirements'][0]
    assert gap['exact_original_requirement']['id']=='DB01' and gap['exact_original_requirement']['topic']=='issuer'
    assert gap['reported_gap']=='ISSUER_NOT_IDENTIFIED' and gap['local_conversation_note_key']=='user_report'
    assert gap['satisfied'] is False and gap['authorized'] is False
    truth(gap,['no_global_nonexistence_or_infeasibility_claim','no_genuine_rejection_decision_created']);missing(gap)
    bindings=d['binding_dispositions'];assert [x['id'] for x in bindings]==['DB%02d'%i for i in range(1,13)]
    for i,row in enumerate(bindings):
        src=q['authorization_binding_requirements'][i];assert row['source']==pin(REQUEST,'/authorization_binding_requirements/'+str(i)) and fragment(row['source'])==src
        assert row['id']==src['id'] and row['topic']==src['topic']
        assert row['disposition']==('MISSING_ISSUER_UNIDENTIFIED_USER_REPORTED_NOT_AUTHORITY_EVIDENCE' if i==0 else src['disposition'])
        assert row['satisfied'] is False and row['authorized'] is False;missing(row)
    reentry=d['reentry_requirement'];assert reentry['first_material']=='Identify the genuine preexisting issuer and provide available authority/delegation body or immutable reference establishing own faculty, exact documentary-contact scope, competence and validity/currentness/revocation.'
    assert reentry['required_information']==REENTRY_FIELDS
    truth(reentry,['DB01_resolution_not_all_DB02_DB12_or_positive_grant','all_other_exact_bindings_before_any_positive_authorization',
        'further_documentary_PASS_or_template_not_substitute_for_genuine_material','no_new_lot_request_phase_or_auto_contact_route']);missing(reentry)
    payload=d['preserved_payload'];assert payload['message_source']==pin(REQUEST,'/exact_proposed_message') and payload['exact_message_requirement']==fragment(payload['message_source'])==q['exact_proposed_message']
    message=payload['exact_message_requirement'];raw=message['text'].encode('utf-8');assert len(raw)==message['raw_byte_count']==1402 and hashlib.sha256(raw).hexdigest()==message['raw_sha256']
    assert payload['attachments_source']==pin(REQUEST,'/exact_proposed_attachments') and payload['exact_attachment_requirements']==fragment(payload['attachments_source'])==q['exact_proposed_attachments']
    assert len(payload['exact_attachment_requirements'])==6
    for row in payload['exact_attachment_requirements']:
        data=(ROOT/row['delivery_file']).read_bytes();assert len(data)==row['raw_byte_count'] and hashlib.sha256(data).hexdigest()==row['raw_sha256']
    assert payload['no_payload_actor_channel_or_validity_change_made'] is True
    decision=d['preserved_decision_boundary'];assert decision['source']==pin(REQUEST,'/future_decision_boundary') and decision['exact_requirement']==fragment(decision['source'])==q['future_decision_boundary']
    assert decision['no_generic_continue_yes_or_gap_report_as_own_contact_authority_or_canonical_EA_authority'] is True
    state=d['current_negative_state'];assert state['source']==pin(REQUEST,'/missing_state') and state['exact_previous_state']==fragment(state['source'])==q['missing_state']
    counters=['actual_authorizations_granted','actual_messages_sent','actual_genuine_authority_evidence_received','actual_genuine_acceptances_created']
    assert all(type(state[k]) is int and state[k]==0 for k in counters);missing({k:v for k,v in state.items() if k not in counters})
    truth(state,['SD01_stop_active','user_conversation_gap_note_not_received_authority_proof_or_positive_intake'])
    assert state['RQ01_sent'] is False and state['RQ02_or_downstream_enabled'] is False
    assert len(d['critical_boundaries'])==14 and all(v is True for v in d['critical_boundaries'].values())
    final=d['final_route_boundary'];assert final['source']==pin(REQUEST,'/final_route_boundary') and final['exact_requirement']==fragment(final['source'])==q['final_route_boundary']
    assert final['current_run_command'] is None;missing(final,['actual_final_route_or_receipt_authorized'])
    assert d['current_effect']=={**source_review['current_effect'],'DB01_issuer_unidentified_conversation_gap_recorded':True,'actual_positive_authorization_contact_delivery_intake_or_acceptance_progress':False}
    assert all(d['producer'][k] is False for k in ['actor_independent','competent_authorizing_or_primary_role_review','separate_R08_acceptance','external_contacts_made'])
    assert d['publication']['publication_not_issuer_nomination_genuine_authority_grant_contact_dispatch_or_D5_closure'] is True
    pointers(d)
    return dict(conversation_answer=ANSWER,report_is_canonical_authority_evidence=False,DB01_identified=False,DB01_genuine_rejection_created=False,
        all_12_binding_ids=[x['id'] for x in bindings],reentry_information_groups=REENTRY_FIELDS,DB01_resolution_not_full_grant=True,
        unchanged_message_bytes=1402,unchanged_documentary_attachment_count=6,actual_authorizations_granted=0,actual_messages_sent=0,actual_genuine_authority_evidence_received=0)

CRITERIA = [
'I279 records exact user question/answer as ordinary conversation with documentary date,not verified canonical-person/provider/authority evidence.',
'No invented canonical reporter,external body locator/authority digest or trusted event timestamp and no nomination/contact/decision inferred.',
'DB01 retains exact I277 issuer requirement and source,not a new authority or different binding.',
'Unidentified issuer does not prove authority globally nonexistent,infeasibility or genuine rejection decision.',
'All12 DB IDs/topics/source pointers preserved;DB01 user-reported gap and DB02-DB12 original pending states,none satisfied/authorized.',
'Reentry requires genuine issuer identity/aliases,available authentic preexisting delegation body/reference,faculty/scope,validity/revocation and own competent review.',
'Nominal identification alone not authority proof;authority must cover this exact documentary contact with traceable available complete material.',
'Resolving DB01 does not satisfy DB02-DB12 or issue grant;all other exact actors/channel/payload/action/validity/decision bindings still required.',
'Further documentary PASS/template/publication never substitutes genuine material,no new lot/phase/request or auto-contact path.',
'I2771402-byte message and six files/extract/raw digests unchanged,no payload/actor/channel/validity change from gap record.',
'Future decision boundary exact,no generic continue/yes/chat-gap report as own contact or canonical EA authority.',
'All real issuer/operator/people/channel/validity/authority/decision fields remain null,zero grants/messages/genuine proofs/acceptances.',
'SD01 active,RQ01 unsent,RQ02/downstream disabled;conversation note no positive intake,provider-gap artifact or proof of eligibility.',
'Preexisting own EA01/R06/R08 authority,14 exclusions/preparers and genuine decisions still needed;no future W02 reverse dependency.',
'RT01/delivery/receipt not RT02-RT05/full A01 own criteria/deliverables/exits or RQ02 enablement.',
'Raw integrity/canonical/signature claims/authentic authority/acceptance distinct,no backend/durable/global-ledger guarantee.',
'Changes invalidate affected bindings/reviews before progress,no proof/approval/acceptance transfer or active rebind.',
'Both Readers/global reference costs,caps/guards/outputs/quotas/reserves unchanged,no hidden/free inputs.',
'CE12 private deferred,no final E06/Q/root/claim/spawn/receipt new entry/prelaunch condition,no claim self-condition/free retry.',
'Published I278 remains frozen documentary baseline,not fresh genuine authority/eligibility/acceptance proof.',
'Focused I279 check can be reproduced without running older audit mains or product/components;hash/version preservation distinct from historical re-audit.',
'Same assistant records/reviews documentation,not independent authorizer/primary role or separate R08;no external contact performed.',
'I122/CP07/atomicity/components/E06/IR03 negative state and30 gates/E01-E05/PJC115-R2/D5 open state retained.',
'Publishing negative gap/review is not issuer nomination,grant,dispatch,scope adoption,active authority/destination/certificate/quota change.'
]


def reconstruct():
    d=rd(SUBJECT);result=inspect(d);pins={**d['input_pins'],**{p:sha(p) for p in PRIOR_FILES}}
    assert len(pins)==1198;verify_blobs(pins)
    return dict(schema='d5.i280-source-reconstruction.v1',increment='I280',date=DATE,timezone='Europe/Madrid',base_commit=BASE,subject=pin(SUBJECT),input_pins=pins,
        independent_reconstruction=result,criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],
        current_effect={**d['current_effect'],'DB01_user_reported_gap_and_reentry_documentary_reviewed':True})


def own_rejections(d):
    cases=[
('question_rewritten',('user_report','question'),'AUTHORIZE_DELIVERY'),('report_as_canonical',('user_report','provenance'),'CANONICAL_AUTHORITY_PROOF'),
('trusted_timestamp_invented',('user_report','actual_trusted_event_timestamp'),'UNVERIFIED_TEST_LABEL'),('nomination_inferred',('user_report','no_issuer_nomination_contact_permission_or_decision_inferred'),False),
('DB01_source_changed',('DB01_disposition','source','json_pointer'),'/authorization_binding_requirements/1'),('issuer_gap_recast',('DB01_disposition','reported_gap'),'ISSUER_DOES_NOT_EXIST'),
('binding_topic_reassigned',('binding_dispositions',0,'topic'),'operator'),('binding_removed',('binding_dispositions',),d['binding_dispositions'][:-1]),
('binding_promoted',('binding_dispositions',1,'disposition'),'ACCEPTED'),('reentry_fields_omitted',('reentry_requirement','required_information'),[]),
('first_material_recast',('reentry_requirement','first_material'),'PREPARE_ANOTHER_DOCUMENTARY_PASS'),('other_bindings_waived',('reentry_requirement','all_other_exact_bindings_before_any_positive_authorization'),False),
('auto_contact_route',('reentry_requirement','no_new_lot_request_phase_or_auto_contact_route'),False),('message_source_changed',('preserved_payload','message_source','json_pointer'),'/missing_state'),
('attachment_removed',('preserved_payload','exact_attachment_requirements'),d['preserved_payload']['exact_attachment_requirements'][:-1]),
('payload_change_allowed',('preserved_payload','no_payload_actor_channel_or_validity_change_made'),False),('conversation_as_authority',('current_negative_state','user_conversation_gap_note_not_received_authority_proof_or_positive_intake'),False),
('grant_boolean',('current_negative_state','actual_authorizations_granted'),False),('new_authority_body',('current_negative_state','actual_genuine_authorization_body_or_decision'),{}),
('authority_body_count',('current_negative_state','actual_genuine_authority_evidence_received'),1),('nomination_allowed',('critical_boundaries','conversational_report_not_canonical_identity_authority_body_eligibility_or_decision'),False),
('claim_self_condition',('final_route_boundary','exact_requirement','exact_requirement','exact_requirement','exact_requirement','exact_requirement','claim_not_own_precondition_no_free_retry_uncertain_partial_expired_states'),False),
('assistant_authorizes',('producer','competent_authorizing_or_primary_role_review'),True),('publication_as_grant',('publication','publication_not_issuer_nomination_genuine_authority_grant_contact_dispatch_or_D5_closure'),False)]
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
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT))
    assert previous['build_record']()==rd(SUBJECT)
    check=previous['build_check']();assert check==rd(PRIOR_CHECK) and check['method']['historical_audits_rerun'] is False
    return dict(schema='d5.i280-documentary-review.v1',increment='I280',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),reconstruction=pin(RECON),verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_DB01_USER_REPORTED_UNIDENTIFIED_NOT_NONEXISTENCE_REJECTION_OR_GRANT',findings=[],
        criteria=rec['criteria'],independent_reconstruction=rec['independent_reconstruction'],
        counts=dict(input_pins=1198,preserved_published_files=890,user_conversation_gap_notes=1,pending_binding_count=12,reentry_information_groups=5,
            unchanged_documentary_attachments=6,review_criteria=len(CRITERIA),actual_authorizations_granted=0,actual_messages_sent=0,actual_genuine_authority_evidence_received=0,
            actual_genuine_acceptances=0,prelaunch_gates_closed=0,resource_obligations_closed=0),
        inherited_I279_rejection_checks=check['rejection_checks'],additional_I280_rejection_checks=own_rejections(rd(SUBJECT)),
        clarifications=['The exact conversational answer says issuer is not yet identified. It does not verify canonical reporter/provider identity,prove no authority exists globally,or create a genuine approval/rejection.',
            'DB01 retains its original issuer/delegation requirement. Identifying a name alone is insufficient;available genuine own-authority material and competent scope review remain necessary before considering DB01 resolution.',
            'DB02-DB12 stay pending. DB01 resolution alone never grants exact delivery,appoints EA01/R06/R08,adopts scope,accepts RT01/A01 or enables RQ02.',
            'Reentry requires five material information groups,not another template/PASS/publication. No new lot,request phase,nomination,contact/fetch or operational verification route is authorized.',
            'I277 message and6 files/extract/limits remain exact. Ordinary gap note is not incoming genuine authority evidence,provider gap artifact,positive intake or decision.',
            'I279 focused check and20 rejections are reproduced. Frozen I278 baseline hashes/versions are checked without rerunning earlier historical audit chains or manufacturing fresh authority evidence.',
            'SD01/no admission remains;CE12/private receipt deferred,no final E06/Q/root/claim/spawn/receipt new entry/prelaunch prerequisite or automatic PJC115-R2/D5 release.'],
        method=dict(primary_gap_and_reentry_source_checks=True,I279_record_and_focused_check_reproduced=True,earlier_historical_audits_rerun=False,prior_publication_mains_called=False),
        current_effect=rec['current_effect'],provenance=dict(identity='Same Codex assistant/chat as I279/I277',documentary_review_only=True,actor_independent=False,competent_authorizing_or_primary_role_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['No issuer identified or genuine authority/delegation body/reference supplied. Positive delivery progress remains stopped,all12 bindings pending,SD01 active,RQ01 unsent.',
            'All A01-A08,30 gates,E01-E05/20 criteria,PJC115-R2/D5 remain unaccepted/open. Documentary quote/hash/JSON/byte/mutation PASS gives no canonical authority,eligibility,capacity,service or900 fit.',
            'No product/component execution,positive protocol codec/crypto/signing/keygen/enrollment/contact/provision/configuration/probe,quota/reserve/binding/authority/destination/certificate change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I280-audit.py',expected_result=STATUS,over400_lines=True,
            reason='One focused gap/reentry review with exact conversational/source reconstruction,pins,rejection checks and preservation; overage declared,no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/byte-preservation checks and in-memory mutations only; no target import,compile,discovery,tests,execution,build,benchmark,positive protocol codec,crypto,signing,keygen,enrollment,contacts,provision,configuration or platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes.'),
        publication=dict(commit_and_push_requested=True,publication_not_nomination_genuine_authority_grant_contact_dispatch_receipt_acceptance_execution_or_D5_closure=True))


def main():
    rec=reconstruct();assert rec==rd(RECON)
    review=build_review(rec);assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published885'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)};assert len(preserved)==890
    seal=rd(SEAL);assert seal['schema']=='d5.i280-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published890']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,input_pins=1198,preserved_published_files=890,new_files=5,review_criteria=len(CRITERIA),inherited_rejections=len(review['inherited_I279_rejection_checks']),additional_rejections=len(review['additional_I280_rejection_checks']),findings=review['findings'],prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
