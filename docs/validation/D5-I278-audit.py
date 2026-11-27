#!/usr/bin/env python3
"""I278 delivery authorization documentary review; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'd58533fc6c52e79df57bc1a9a6c18a8d06c6b58c'
DATE = '2026-11-27'
HANDOFF = P+'D5-I275-RQ01-RT01-RECEPTION-PACKAGE-HANDOFF-CANDIDATE.json'
CONSOLIDATED = P+'D5-I269-A01-A08-CONSOLIDATED-HANDOFF-CANDIDATE.json'
EXTRACT = P+'D5-I277-CONSOLIDATED-ENTRY-DELIVERY-EXTRACT.json'
SUBJECT = P+'D5-I277-RQ01-RT01-DELIVERY-AUTHORIZATION-REQUEST-CANDIDATE.json'
PRIOR_PREP = P+'D5-I277-preparation-review.json'
PRIOR_AUDIT = P+'D5-I277-audit.py'
PRIOR_SEAL = P+'D5-I277-integrity.json'
PRIOR_DOC = 'docs/design/D5-I277-RQ01-RT01-DELIVERY-AUTHORIZATION-REQUEST.md'
PRIOR_FILES = {SUBJECT,EXTRACT,PRIOR_PREP,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I278-I277-source-reconstruction.json'
REVIEW = P+'D5-I278-I277-documentary-review.json'
AUDIT = P+'D5-I278-audit.py'
SEAL = P+'D5-I278-integrity.json'
DOC = 'docs/design/D5-I278-I277-DELIVERY-AUTHORIZATION-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_DELIVERY_AUTHORIZATION_REQUEST_REVIEW_EXACT_BINDINGS_MISSING_NOT_GRANTED_NOT_SENT_NOT_ADMITTED'


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


TOPICS = 'issuer operator recipients channel payload action validity denied_actions own_decision change_control outcome_trace missing_bindings'.split()
INHERITED = 'three_boundaries future_return_routes integrity_and_trace missing_state complete_A01_boundary critical_boundaries final_route_boundary'.split()
SERIALIZER = 'Python stdlib json.dumps(indent=2, ensure_ascii=False) + LF; UTF-8; source insertion order retained; documentary JSON, not JCS'


def inspect(d):
    h=rd(HANDOFF)
    assert d['authorization_request_id']=='PGE251-RQ01-RT01-DELIVERY-AUTHORIZATION-CANDIDATE-01'
    assert (d['lot_id'],d['request_id'],d['return_id'])==('A01','RQ01','RT01') and d['handoff_source']==pin(HANDOFF)
    assert d['dispatch_boundary_source']==pin(HANDOFF,'/three_boundaries/dispatch_to_people') and d['exact_dispatch_boundary']==fragment(d['dispatch_boundary_source'])==h['three_boundaries']['dispatch_to_people']
    cover=d['request_cover'];assert cover['subject'] and cover['text'] and cover['intended_authorizer_role_only']
    assert cover['is_draft_only'] is True and cover['sent'] is False;missing(cover)
    message=d['exact_proposed_message'];raw=message['text'].encode('utf-8')
    assert (message['encoding'],message['line_endings'],message['normalization'])==('UTF-8','LF','NONE') and b'\r' not in raw and raw.endswith(b'\n')
    assert type(message['raw_byte_count']) is int and message['raw_byte_count']==len(raw)==1402
    assert message['raw_sha256']==hashlib.sha256(raw).hexdigest()=='ebaeb80a764baf83802ff32f8b0b54f6405036da17be2b79fd03882f1189ea1c'
    assert message['documentary_bytes_not_JCS_signature_or_genuine_authority'] is True;missing(message,['actual_sent'])
    attachments=d['exact_proposed_attachments'];manifest=h['documentary_attachment_manifest'];assert len(attachments)==len(manifest)==6
    assert [x['id'] for x in attachments]==[x['id'] for x in manifest] and len({x['id'] for x in attachments})==6
    for i,row in enumerate(attachments):
        src=manifest[i];assert row['original_handoff_requirement_source']==pin(HANDOFF,'/documentary_attachment_manifest/'+str(i)) and fragment(row['original_handoff_requirement_source'])==src
        assert row['original_source']==src['source'];fragment(row['original_source'])
        path=EXTRACT if row['id']=='CONSOLIDATED_ENTRY' else src['source']['path'];assert row['delivery_file']==path
        data=(ROOT/path).read_bytes();assert type(row['raw_byte_count']) is int and row['raw_byte_count']==len(data) and row['raw_sha256']==hashlib.sha256(data).hexdigest()
        assert row['documentary_content_not_actual_EA_authority_or_received_evidence'] is True;missing(row,['actual_dispatched'])
    export=d['extract_binding'];assert export['original_source']==pin(CONSOLIDATED,'/first_material_request') and export['delivery_file']==EXTRACT and export['serializer']==SERIALIZER
    fragment_object=fragment(export['original_source']);expected=(json.dumps(fragment_object,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
    assert (ROOT/EXTRACT).read_bytes()==expected and rd(EXTRACT)==fragment_object
    assert type(export['raw_byte_count']) is int and export['raw_byte_count']==len(expected)==6149 and export['raw_sha256']==sha(EXTRACT)
    truth(export,['exact_selected_fragment_only_no_whole_consolidated_dossier','metadata_export_not_positive_protocol_codec_crypto_or_actual_evidence'])
    roles=d['recipient_binding_requests'];assert [x['id'] for x in roles]==['EA01','EA02','EA03'] and [x['required_role'] for x in roles]==['SCOPE_AUTHORITY','R06','R08']
    for i,row in enumerate(roles):
        assert row['source']==pin(HANDOFF,'/role_handoff_cards/'+str(i)) and row['exact_role_requirement']==fragment(row['source'])==h['role_handoff_cards'][i]
        assert row['appointed'] is False and row['authorized_for_delivery'] is False;missing(row)
    requirements=d['authorization_binding_requirements'];assert [x['id'] for x in requirements]==['DB%02d'%i for i in range(1,13)] and [x['topic'] for x in requirements]==TOPICS
    for row in requirements:
        assert row['requirement'] and row['disposition']=='MISSING_NOT_REVIEWED_NOT_GRANTED' and row['satisfied'] is False;missing(row)
    limits=d['proposed_action_limits'];assert limits['action']=='DELIVER_EXACT_EMPTY_DOCUMENTARY_HANDOFF_ONLY'
    assert type(limits['max_attempts_per_exact_approved_unique_endpoint']) is int and limits['max_attempts_per_exact_approved_unique_endpoint']==1
    truth(limits,['approved_endpoint_list_must_be_finite_and_fully_bound','no_automatic_followup_retry_forwarding_additional_recipient_payload_channel_or_response_fetch',
        'uncertain_or_partial_transport_outcome_requires_separate_exact_decision_before_any_retry','contact_permission_not_enrollment_scope_adoption_EA_authority_operational_intake_verification_or_acceptance'])
    assert limits['authorized_now'] is False and limits['performed'] is False;missing(limits)
    decision=d['future_decision_boundary'];assert decision['allowed_reasoned_decision_kinds']==['AUTHORIZE_EXACT_FULLY_BOUND_DOCUMENTARY_DELIVERY','REJECT_WITH_TRACEABLE_REASON','DEFER_MISSING_BINDINGS']
    truth(decision,['genuine_preexisting_competent_authority_body_and_all_bindings_before_positive_decision','no_blanket_authorization_or_conditional_approval_of_unknown_people_channel_scope',
        'user_docs_commit_push_request_not_canonical_contact_or_EA_role_authority','description_not_grant_or_actual_request_to_others']);missing(decision,['actual_positive_authorization'])
    inherited=d['inherited_boundaries'];assert [x['section'] for x in inherited]==INHERITED
    for row,s in zip(inherited,INHERITED):assert row['source']==pin(HANDOFF,'/'+s) and row['exact_requirement']==fragment(row['source'])==h[s]
    state=d['missing_state'];counts=['actual_authorizations_granted','actual_messages_sent','actual_genuine_acceptances_created']
    assert all(type(state[k]) is int and state[k]==0 for k in counts);missing({k:v for k,v in state.items() if k not in counts})
    assert state['SD01_stop_active'] is True and state['RQ01_sent'] is False and state['RQ02_or_downstream_enabled'] is False
    assert len(d['critical_boundaries'])==22 and all(v is True for v in d['critical_boundaries'].values())
    final=d['final_route_boundary'];assert final['source']==pin(HANDOFF,'/final_route_boundary') and final['exact_requirement']==fragment(final['source'])==h['final_route_boundary']
    assert final['current_run_command'] is None;missing(final,['actual_final_route_or_receipt_authorized'])
    assert d['current_effect']=={**h['current_effect'],'RQ01_RT01_documentary_delivery_authorization_request_prepared':True,'actual_delivery_authority_request_sent_grant_dispatch_or_genuine_acceptance_created':False}
    assert all(d['producer'][k] is False for k in ['actor_independent','competent_authorizing_or_primary_role_review','separate_R08_acceptance','external_contacts_made'])
    assert d['publication']['only_empty_documentary_request_and_selected_existing_documentary_extract_published'] is True
    pointers(d)
    return dict(message_utf8_bytes=1402,message_raw_sha256=message['raw_sha256'],attachment_ids=[x['id'] for x in attachments],attachment_local_bytes=[x['raw_byte_count'] for x in attachments],
        extract_documentary_bytes=6149,extract_selected_parent_pointer='/first_material_request',recipient_role_bindings={x['id']:x['required_role'] for x in roles},
        authorization_topics=TOPICS,max_attempts_per_exact_approved_unique_endpoint=1,actual_endpoint_list=None,
        delivery_permission_not_canonical_EA_authority_or_evidence_acceptance=True,actual_authorizations_granted=0,actual_messages_sent=0,actual_genuine_acceptances=0)

CRITERIA = [
'I277 preserves I275 exact dispatch boundary and original RQ01/RT01 scope;request is local,unsent and not grant/nomination/acceptance.',
'Proposed message is new fixed communication text in I277,not asserted byte-identical to I275 cover;its1402 UTF8/LF bytes and rawSHA256 are exact.',
'Raw message hash is document integrity,not JCS,signature,authority or receipt;normalization NONE and final LF retained.',
'Six ordered attachment IDs preserve I275 original source path/hash/pointer and exact selected delivery file bytes/count/rawdigest.',
'First five attachments are complete original documentary files;CONSOLIDATED_ENTRY sends only selected I269 fragment export.',
'Extract6149 bytes equals parent first_material_request under declared ordinary JSON serializer/order/UTF8/LF;not JCS/protocol codec or evidence.',
'No whole consolidated dossier,extra attachments,hidden contents,runtime input or active binding included in exact proposed payload.',
'Local byte sizes exclude transport/channel envelopes and do not prove channel availability,resource fit,capacity,service or duration.',
'EA01 scope authority,EA02 R06,EA03 R08 preserve exact I275 role requirements;not three actual/distinct people or appointments.',
'Canonical recipient/aliases/eligibility,approved endpoint/channel and contact/delivery provenance remain missing per role.',
'Twelve DB IDs/topics cover issuer,operator,recipients,channel,payload,action,validity,denied actions,own decision,change control,outcome and gaps.',
'Every DB remains missing/not reviewed/not granted,with no genuine binding/authority/reasoned decision or satisfied flag.',
'Issuer needs authentic preexisting own delegation/scope/competence/validity and faculty to authorize exact documentary contact.',
'Operator must be accountable and eligible within that faculty,not appointed or authorized by template/user docs request.',
'Recipients/channel/endpoints/custodian/permission must be exact finite fully bound before positive decision,no discovery/contact/fetch to fill them now.',
'One proposed attempt per approved unique endpoint is strict integer1,not boolean/unbounded retry or durable/atomic delivery guarantee.',
'No automatic followups,retries,forwarding,additional recipient/payload/channel or response fetch;uncertain/partial outcome needs new exact decision.',
'Validity/currentness/revocation/scope require own authentic evidence,no host date,predictive values or invented calendar.',
'Allowed future decision kinds are exact authorize fully-bound scope,reject with reason or defer missing bindings;not actual decision or blanket approval.',
'No conditional positive authorization of unknown issuer/operator/people/channel/scope/validity and no generic reply promoted to grant.',
'Documentary delivery permission does not enroll/nominate,adopt scope,create canonical EA authority or authorize evidence intake/verification/acceptance.',
'Preexisting EA01/R06/R08 authority/competence/appointments/14 exclusions/preparers still required;user docs/Git/assistant/self/future W02/bundle/root not sole basis.',
'W02 eligibility not backward acceptance/full future roster/CE10,no blanket R01/R02;logical scope not effective W03 freeze/predictive hash.',
'Raw integrity/canonical/signature claims/genuine authority/acceptance distinct,no positive codec/crypto/signing/keygen or probes here.',
'Trace not backend/durability/global-ledger/intrinsic-custody proof,no new storage/path/service/input;no incoming bodies/data auto-published.',
'Seven I275 boundary sections complete;every change of payload/actor/channel/scope/validity invalidates affected grant before action,no automatic proof/approval/acceptance transfer.',
'RT01/handoff/receipt cannot replace RT02-RT05,12 A01 criteria,3 deliverables/3 exits and genuine R06/R08 decisions or enable RQ02.',
'All actual actors/authority/decision/dispatch/receipt/evidence missing,external inventory/count unknown;SD01 active,counters zero work only.',
'Both Readers/global reference costs,caps/guards/outputs/quotas/reserves unchanged,no hidden/free inputs or resource promise from hashes/budgets.',
'CE12 private deferred,4 external preclaim prerequisites then actual claim/construction before receipt;no claim self-condition/free retry or final events as new entry/prelaunch condition.',
'Gaps require exact separate work/authority,no fake actor/provider/calendar/hash/body or global infeasibility inferred from missing proof.',
'No actual contact/product/components/execution/configuration/quota/reserve/binding/authority/destination/certificate/PJC115-R2/D5 release from request/PASS/publication.'
]


def reconstruct():
    d=rd(SUBJECT);result=inspect(d);pins={**d['input_pins'],**{p:sha(p) for p in PRIOR_FILES}}
    assert len(pins)==1188;verify_blobs(pins)
    return dict(schema='d5.i278-source-reconstruction.v1',increment='I278',date=DATE,timezone='Europe/Madrid',base_commit=BASE,subject=pin(SUBJECT),input_pins=pins,
        independent_reconstruction=result,criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],
        current_effect={**d['current_effect'],'RQ01_RT01_documentary_delivery_authorization_request_reviewed':True})


def own_rejections(d):
    cases=[
('message_encoding',('exact_proposed_message','encoding'),'ASCII'),('message_byte_boolean',('exact_proposed_message','raw_byte_count'),True),
('attachment_order',('exact_proposed_attachments',),list(reversed(d['exact_proposed_attachments']))),('attachment_source_changed',('exact_proposed_attachments',0,'original_handoff_requirement_source','json_pointer'),'/documentary_attachment_manifest/1'),
('whole_parent_delivery',('exact_proposed_attachments',5,'delivery_file'),CONSOLIDATED),('attachment_byte_count_boolean',('exact_proposed_attachments',0,'raw_byte_count'),True),
('extract_serializer_claim',('extract_binding','serializer'),'JCS'),('extract_parent_pointer',('extract_binding','original_source','json_pointer'),'/cover_note'),
('extract_byte_count_changed',('extract_binding','raw_byte_count'),0),('recipient_duplicate',('recipient_binding_requests',2,'id'),'EA02'),
('scope_role_changed',('recipient_binding_requests',0,'required_role'),'R06'),('recipient_source',('recipient_binding_requests',0,'source','json_pointer'),'/role_handoff_cards/1'),
('binding_missing',('authorization_binding_requirements',),d['authorization_binding_requirements'][:-1]),('binding_topic',('authorization_binding_requirements',0,'topic'),'payload'),
('binding_promoted',('authorization_binding_requirements',0,'disposition'),'AUTHORIZED'),('attempts_boolean',('proposed_action_limits','max_attempts_per_exact_approved_unique_endpoint'),True),
('action_broadened',('proposed_action_limits','action'),'CONTACT_AND_ACCEPT_EVIDENCE'),('endpoint_list_fabricated',('proposed_action_limits','actual_unique_endpoint_list'),['UNVERIFIED_TEST_LABEL']),
('transport_retry',('proposed_action_limits','uncertain_or_partial_transport_outcome_requires_separate_exact_decision_before_any_retry'),False),
('decision_kind_missing',('future_decision_boundary','allowed_reasoned_decision_kinds'),['AUTHORIZE_EXACT_FULLY_BOUND_DOCUMENTARY_DELIVERY']),
('issuer_proof_waived',('future_decision_boundary','genuine_preexisting_competent_authority_body_and_all_bindings_before_positive_decision'),False),
('user_request_as_authority',('future_decision_boundary','user_docs_commit_push_request_not_canonical_contact_or_EA_role_authority'),False),
('boundary_missing',('inherited_boundaries',),d['inherited_boundaries'][:-1]),('dispatch_boundary_granted',('inherited_boundaries',0,'exact_requirement','dispatch_to_people','authorized_now'),True),
('operator_fabricated',('missing_state','actual_named_issuer_operator_recipients_channel_endpoints_or_validity'),{}),
('authority_body_fabricated',('missing_state','actual_genuine_authorization_body_or_contact_authority'),{}),('messages_boolean',('missing_state','actual_messages_sent'),False),
('receipt_fabricated',('missing_state','actual_request_dispatch_handoff_delivery_or_receipt'),{}),('unknown_as_zero',('missing_state','actual_external_body_inventory_or_count'),0),
('forged_primary_review',('missing_state','actual_received_evidence_or_primary_R06_separate_R08_decisions'),{}),
('claim_self_condition',('final_route_boundary','exact_requirement','exact_requirement','exact_requirement','exact_requirement','claim_not_own_precondition_no_free_retry_uncertain_partial_expired_states'),False),
('receipt_precondition',('final_route_boundary','exact_requirement','exact_requirement','exact_requirement','exact_requirement','no_final_route_execution_claim_spawn_receipt_as_new_precondition_of_prelaunch_acceptance'),False),
('changed_binding_transfer',('critical_boundaries','changed_payload_actor_channel_scope_validity_invalidates_affected_grant_no_proof_approval_acceptance_transfer'),False),
('grant_created',('current_effect','actual_delivery_authority_request_sent_grant_dispatch_or_genuine_acceptance_created'),True),
('assistant_authorizer',('producer','competent_authorizing_or_primary_role_review'),True),('incoming_data_published',('publication','only_empty_documentary_request_and_selected_existing_documentary_extract_published'),False)]
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
    return dict(schema='d5.i278-documentary-review.v1',increment='I278',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),reconstruction=pin(RECON),verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_EXACT_LOCAL_PAYLOAD_BOUND_AUTHORITY_AND_ACTOR_BINDINGS_MISSING_NOT_GRANTED',findings=[],
        criteria=rec['criteria'],independent_reconstruction=rec['independent_reconstruction'],
        counts=dict(input_pins=1188,preserved_published_files=880,proposed_messages=1,message_utf8_bytes=1402,exact_documentary_files=6,selected_extract_bytes=6149,
            recipient_role_bindings=3,authorization_requirements=12,inherited_boundaries=7,max_attempts_per_exact_approved_unique_endpoint=1,review_criteria=len(CRITERIA),
            actual_messages_sent=0,actual_authorizations_granted=0,actual_genuine_acceptances=0,prelaunch_gates_closed=0,resource_obligations_closed=0),
        inherited_I277_rejection_checks=prep['rejection_checks'],additional_I278_rejection_checks=own_rejections(rd(SUBJECT)),
        clarifications=['I277 fixes a new proposed communication text,not a byte copy of I275 cover. The1402 UTF8/LF bytes and6 documentary attachments are exact candidates for later scope-specific review,not sent content or granted authority.',
            'I269 selected first_material_request export is6149 bytes of ordinary documentary JSON under declared serializer,not JCS/protocol codec or evidence. Parent digest/pointer and exported raw bytes both bind the selected fragment,not the whole dossier.',
            'Local message/file byte counts exclude channel/envelope overhead and are no delivery/service/resource/quota guarantee. One attempt per approved unique endpoint is a proposed authorization limit,not durable atomic dispatch or global one-use claim.',
            'Issuer/delegation,operator,canonical people/aliases/endpoints/channel/custody/scope/validity and genuine reasoned decision all remain missing. No blanket or conditional positive approval of unknown bindings is sought or granted.',
            'Three role IDs do not nominate people or prove3 canonical/distinct humans. Delivery permission cannot create EA01/R06/R08 authority,adopt scope,enroll or authorize evidence intake/verification/acceptance.',
            'Changes of payload/actor/channel/scope/validity require fresh affected decision before action,no proof/approval/acceptance transfer. Uncertain/partial transport outcome grants no automatic retry/followup/forward/response fetch.',
            'RT01/delivery/receipt not full A01 or RQ02 enablement;preexisting genuine authority,14 exclusions,RT02-RT05 and own R06/R08 decisions remain required,SD01 active.',
            'CE12/private receipt remains deferred under separate exact authority,no final E06/Q/root/claim/spawn/receipt new entry/prelaunch condition or automatic certificate/PJC115-R2/D5 release.'],
        source_reconstruction=dict(primary_byte_source_and_binding_checks=True,I277_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        current_effect=rec['current_effect'],provenance=dict(identity='Same Codex assistant/chat as I277/I275/A01',documentary_review_only=True,actor_independent=False,competent_authorizing_or_primary_role_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['Request unsent,not granted,all genuine authority/actor/channel/validity/decision bindings missing,SD01 active. No contact/dispatch/receipt/intake or genuine acceptance created.',
            'All A01-A08,30 gates,E01-E05/20 criteria,PJC115-R2 and D5 remain unaccepted/open. Documentary JSON/hash/pointer/byte/mutation PASS proves no authentic authority,resource truth,capacity,service or900 fit.',
            'No product/component execution,positive protocol codec/crypto/signing/keygen/enrollment/contact/provision/configuration/probe,quota/reserve/binding/authority/destination/certificate change. CE12/final route separately deferred.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I278-audit.py',expected_result=STATUS,over400_lines=True,
            reason='One authorization-request review with independent message/file/extract/actor-binding reconstruction,pins,rejection checks and preservation; overage declared,no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/byte/metadata-export/coverage/graph checks and in-memory mutations only; no target import,compile,discovery,tests,execution,build,benchmark,positive protocol codec,crypto,signing,keygen,enrollment,contacts,provision,configuration or platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes.'),
        publication=dict(commit_and_push_requested=True,publication_not_delivery_authorization_contact_dispatch_receipt_genuine_EA_authority_acceptance_execution_or_D5_closure=True))


def main():
    rec=reconstruct();assert rec==rd(RECON)
    review=build_review(rec);assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published874'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)};assert len(preserved)==880
    seal=rd(SEAL);assert seal['schema']=='d5.i278-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published880']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for p,h in mapping.items():assert sha(p)==h,p
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,input_pins=1188,preserved_published_files=880,new_files=5,review_criteria=len(CRITERIA),inherited_rejections=len(review['inherited_I277_rejection_checks']),additional_rejections=len(review['additional_I278_rejection_checks']),findings=review['findings'],prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
