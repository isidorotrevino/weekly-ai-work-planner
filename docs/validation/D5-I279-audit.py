#!/usr/bin/env python3
"""I279 focused documentary DB01 gap record; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'dc4516893e2315c7c56f9fbf54e509cf98fc8b17'
DATE = '2026-11-27'
REQUEST = P+'D5-I277-RQ01-RT01-DELIVERY-AUTHORIZATION-REQUEST-CANDIDATE.json'
PRIOR_RECON = P+'D5-I278-I277-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I278-I277-documentary-review.json'
PRIOR_AUDIT = P+'D5-I278-audit.py'
PRIOR_SEAL = P+'D5-I278-integrity.json'
PRIOR_DOC = 'docs/design/D5-I278-I277-DELIVERY-AUTHORIZATION-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I279-DB01-ISSUER-UNIDENTIFIED-GAP.json'
PREP = P+'D5-I279-documentary-check.json'
AUDIT = P+'D5-I279-audit.py'
SEAL = P+'D5-I279-integrity.json'
DOC = 'docs/design/D5-I279-DB01-ISSUER-UNIDENTIFIED-GAP.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_DB01_ISSUER_UNIDENTIFIED_USER_REPORTED_NO_AUTHORITY_EVIDENCE_NO_POSITIVE_PROGRESS_NOT_GRANTED_NOT_SENT_NOT_ADMITTED'


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


QUESTION = '¿Quién es la autoridad humana preexistente que puede autorizar esta entrega documental RQ01/RT01, y qué documento o referencia disponible acredita su facultad, ámbito y vigencia? Si todavía no está identificada, indícalo.'
ANSWER = 'todavía no está identificada'


def build_record():
    q,review=rd(REQUEST),rd(PRIOR_REVIEW)
    pins={**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in PRIOR_FILES}};assert len(pins)==1193
    assert review['findings']==[] and review['provenance']['actor_independent'] is False
    return dict(schema='d5.i279-db01-user-reported-gap.v1',increment='I279',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        record_id='PGE251-RQ01-RT01-DB01-UNIDENTIFIED-ISSUER-GAP-01',kind='DOCUMENTARY_USER_REPORTED_GAP_NOT_CANONICAL_AUTHORITY_EVIDENCE_OR_GENUINE_DECISION',status=STATUS,
        input_pins=pins,request=pin(REQUEST),latest_documentary_review=pin(PRIOR_REVIEW),
        user_report=dict(question=QUESTION,answer_verbatim=ANSWER,recorded_date=DATE,
            provenance='User reply in this chat; conversational report only, not enrolled canonical issuer/provider or verified authority evidence',
            actual_canonical_reporter_or_authority_identity=None,actual_immutable_external_body_locator_or_authority_digest=None,
            actual_trusted_event_timestamp=None,no_issuer_nomination_contact_permission_or_decision_inferred=True),
        DB01_disposition=dict(source=pin(REQUEST,'/authorization_binding_requirements/0'),exact_original_requirement=q['authorization_binding_requirements'][0],
            reported_gap='ISSUER_NOT_IDENTIFIED',local_conversation_note_key='user_report',
            actual_issuer_delegation_body_scope_validity_or_competence=None,satisfied=False,authorized=False,
            no_global_nonexistence_or_infeasibility_claim=True,no_genuine_rejection_decision_created=True),
        binding_dispositions=[dict(id=r['id'],topic=r['topic'],source=pin(REQUEST,'/authorization_binding_requirements/'+str(i)),
            disposition=('MISSING_ISSUER_UNIDENTIFIED_USER_REPORTED_NOT_AUTHORITY_EVIDENCE' if i==0 else r['disposition']),
            actual_genuine_binding_or_review_decision=None,satisfied=False,authorized=False) for i,r in enumerate(q['authorization_binding_requirements'])],
        reentry_requirement=dict(first_material='Identify the genuine preexisting issuer and provide available authority/delegation body or immutable reference establishing own faculty, exact documentary-contact scope, competence and validity/currentness/revocation.',
            required_information=['canonical human issuer and complete aliases','available complete independently authentic authority/delegation body or reference with locator/bytes/digest/author/provider/custody',
                'faculty to authorize this exact documentary contact, allowed/denied actions and scope','validity/currentness/revocation and own provenance','competent own-scope review of genuine material; no assistant or generic chat approval substitution'],
            actual_genuine_issuer_or_body_received=None,actual_competent_authority_review=None,
            DB01_resolution_not_all_DB02_DB12_or_positive_grant=True,all_other_exact_bindings_before_any_positive_authorization=True,
            further_documentary_PASS_or_template_not_substitute_for_genuine_material=True,no_new_lot_request_phase_or_auto_contact_route=True),
        preserved_payload=dict(message_source=pin(REQUEST,'/exact_proposed_message'),exact_message_requirement=q['exact_proposed_message'],
            attachments_source=pin(REQUEST,'/exact_proposed_attachments'),exact_attachment_requirements=q['exact_proposed_attachments'],
            no_payload_actor_channel_or_validity_change_made=True),
        preserved_decision_boundary=dict(source=pin(REQUEST,'/future_decision_boundary'),exact_requirement=q['future_decision_boundary'],
            no_generic_continue_yes_or_gap_report_as_own_contact_authority_or_canonical_EA_authority=True),
        current_negative_state=dict(source=pin(REQUEST,'/missing_state'),exact_previous_state=q['missing_state'],
            actual_issuer_or_operator_or_canonical_people_channel_validity=None,actual_genuine_authorization_body_or_decision=None,
            actual_authorizations_granted=0,actual_messages_sent=0,actual_genuine_authority_evidence_received=0,actual_genuine_acceptances_created=0,
            SD01_stop_active=True,RQ01_sent=False,RQ02_or_downstream_enabled=False,
            user_conversation_gap_note_not_received_authority_proof_or_positive_intake=True),
        critical_boundaries=dict(
            unidentified_issuer_not_proven_nonexistent_authority_or_global_infeasibility=True,
            conversational_report_not_canonical_identity_authority_body_eligibility_or_decision=True,
            no_fake_issuer_operator_recipient_endpoint_channel_provider_validity_or_schedule=True,
            DB01_stays_missing_all_other_bindings_pending_no_blanket_or_conditional_grant=True,
            exact_message6_documentary_attachments_extract_and_single_attempt_limits_unchanged=True,
            permission_to_prepare_audit_commit_push_not_contact_delivery_EA_role_scope_adoption_or_acceptance=True,
            no_contact_fetch_services_enrollment_positive_codec_crypto_signing_keygen_provision_configuration_probes_or_product_execution=True,
            no_RQ02_or_downstream_enablement_RT01_not_RT02_RT05_full_A01_genuine_reviews=True,
            all14_exclusions_preexisting_own_authority_genuine_R06_R08_still_required_no_future_W02_reverse_dependency=True,
            raw_integrity_claims_authority_acceptance_separate_no_backend_or_ledger_guarantee=True,
            changed_material_invalidates_affected_bindings_no_proof_approval_acceptance_transfer=True,
            both_Readers_global_reference_costs_caps_guards_outputs_quotas_reserves_unchanged=True,
            CE12_private_deferred_no_final_event_as_new_entry_prelaunch_condition_no_claim_self_precondition_or_free_retry=True,
            no_certificate_SOURCE_CAPACITY_VERIFIED_PJC115_R2_or_D5_release_from_note_PASS_or_publication=True),
        final_route_boundary=dict(source=pin(REQUEST,'/final_route_boundary'),exact_requirement=q['final_route_boundary'],current_run_command=None,actual_final_route_or_receipt_authorized=False),
        current_effect={**review['current_effect'],'DB01_issuer_unidentified_conversation_gap_recorded':True,
            'actual_positive_authorization_contact_delivery_intake_or_acceptance_progress':False},
        producer=dict(identity='Same Codex assistant/chat as I277/I278; recorder of user-reported gap, not canonical authority',documentary_recorder_only=True,
            actor_independent=False,competent_authorizing_or_primary_role_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested_by_continuation=True,publication_not_issuer_nomination_genuine_authority_grant_contact_dispatch_or_D5_closure=True))


def validate(d):
    assert d==build_record(),'Gap record differs from exact request bindings and quoted user response'
    assert d['user_report']['answer_verbatim']==ANSWER and d['DB01_disposition']['exact_original_requirement']==fragment(d['DB01_disposition']['source'])
    assert [x['id'] for x in d['binding_dispositions']]==['DB%02d'%i for i in range(1,13)]
    for x in d['binding_dispositions']:assert fragment(x['source'])['id']==x['id'] and x['satisfied'] is False and x['authorized'] is False
    message=fragment(d['preserved_payload']['message_source']);assert message==d['preserved_payload']['exact_message_requirement']
    assert hashlib.sha256(message['text'].encode('utf-8')).hexdigest()==message['raw_sha256']
    attachments=fragment(d['preserved_payload']['attachments_source']);assert attachments==d['preserved_payload']['exact_attachment_requirements']
    for row in attachments:assert sha(row['delivery_file'])==row['raw_sha256'] and len((ROOT/row['delivery_file']).read_bytes())==row['raw_byte_count']
    assert len(d['critical_boundaries'])==14 and all(v is True for v in d['critical_boundaries'].values())
    state=d['current_negative_state']
    for k in ['actual_authorizations_granted','actual_messages_sent','actual_genuine_authority_evidence_received','actual_genuine_acceptances_created']:assert type(state[k]) is int and state[k]==0
    pointers(d)


NEGATIVE_CASES = [
('user_quote_changed',('user_report','answer_verbatim'),'AUTHORITY_ACCEPTED'),('canonical_reporter_invented',('user_report','actual_canonical_reporter_or_authority_identity'),'UNVERIFIED_TEST_LABEL'),
('issuer_fabricated',('DB01_disposition','actual_issuer_delegation_body_scope_validity_or_competence'),{}),('issuer_satisfied',('DB01_disposition','satisfied'),True),
('gap_as_rejection',('DB01_disposition','no_genuine_rejection_decision_created'),False),('global_absence',('DB01_disposition','no_global_nonexistence_or_infeasibility_claim'),False),
('binding_missing',('binding_dispositions',),[]),('binding_granted',('binding_dispositions',1,'authorized'),True),
('new_issuer_body',('reentry_requirement','actual_genuine_issuer_or_body_received'),{}),('DB01_as_full_grant',('reentry_requirement','DB01_resolution_not_all_DB02_DB12_or_positive_grant'),False),
('paper_as_evidence',('reentry_requirement','further_documentary_PASS_or_template_not_substitute_for_genuine_material'),False),
('generic_yes_as_grant',('preserved_decision_boundary','no_generic_continue_yes_or_gap_report_as_own_contact_authority_or_canonical_EA_authority'),False),
('grant_count',('current_negative_state','actual_authorizations_granted'),1),('message_count',('current_negative_state','actual_messages_sent'),1),
('proof_count',('current_negative_state','actual_genuine_authority_evidence_received'),1),('SD01_bypass',('current_negative_state','SD01_stop_active'),False),
('RQ02_enabled',('current_negative_state','RQ02_or_downstream_enabled'),True),('run_command',('final_route_boundary','current_run_command'),'UNVERIFIED_TEST_LABEL'),
('authority_progress',('current_effect','actual_positive_authorization_contact_delivery_intake_or_acceptance_progress'),True),('D5_closed',('current_effect','D5_closed'),True)]


def rejection_checks(d):
    results=[]
    for name,path,value in NEGATIVE_CASES:
        mutant=copy.deepcopy(d);node=mutant
        for key in path[:-1]:node=node[key]
        node[path[-1]]=value
        try:validate(mutant)
        except AssertionError:results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:raise AssertionError(name)
    return results


def build_check():
    d=rd(SUBJECT);validate(d);review=rd(PRIOR_REVIEW)
    assert review['status']=='PASS_STATIC_SOURCE_ONLY_DELIVERY_AUTHORIZATION_REQUEST_REVIEW_EXACT_BINDINGS_MISSING_NOT_GRANTED_NOT_SENT_NOT_ADMITTED'
    return dict(schema='d5.i279-documentary-check.v1',increment='I279',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,subject=pin(SUBJECT),findings=[],
        counts=dict(input_pins=1193,user_conversation_gap_notes=1,issuer_binding='DB01',all_bindings_pending=12,unchanged_documentary_attachments=6,
            reentry_information_groups=5,documentary_rejections=len(NEGATIVE_CASES),preserved_published_files=885,new_files=5,
            actual_authorizations_granted=0,actual_messages_sent=0,actual_genuine_authority_evidence_received=0,actual_genuine_acceptances=0),
        rejection_checks=rejection_checks(d),method=dict(focused_documentary_request_and_user_quote_reconciliation=True,published_I278_status_and_integrity_verified=True,
            immutable_base_blob_hashes_verified_by_main=True,historical_audits_rerun=False,product_or_component_execution=False,
            historical_review_not_new_genuine_authority_or_acceptance=True),current_effect=d['current_effect'],
        limitations=['User says issuer is not yet identified. This is a conversational gap report,not a canonical-person statement,authority/delegation proof,provider evidence,positive intake or genuine approval/rejection.',
            'No positive progress until actual issuer identification and genuine available own-authority material can be considered. DB02-DB12 remain pending; resolving DB01 would not itself grant delivery.',
            'Exact I277 message/files/limits preserved. SD01 active,request/handoff unsent,all A01-A08/30 gates/E01-E05/PJC115-R2/D5 open. No product execution,quota/reserve/active binding/authority/destination change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I279-audit.py',expected_result=STATUS,over400_lines=True,
            reason='Single negative DB01 gap record and precise reentry condition with quote provenance,request pins,focused checks and preservation; overage declared,no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/byte-preservation checks and in-memory mutations only. No target import,compile,discovery,tests,execution,build,benchmark,positive protocol codec,crypto,signing,keygen,enrollment,contacts,provision,configuration or platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes.'),
        provenance=d['producer'],publication=d['publication'])


def main():
    d=rd(SUBJECT);validate(d);verify_blobs(d['input_pins'])
    check=build_check();assert check==rd(PREP)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published880'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)};assert len(preserved)==885
    seal=rd(SEAL);assert seal['schema']=='d5.i279-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published885']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==d['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,**check['counts'],D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
