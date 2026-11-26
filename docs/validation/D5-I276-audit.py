#!/usr/bin/env python3
"""I276 reception handoff documentary review; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '9bf17da129ef6c52cb84de25fd3facdc57479382'
DATE = '2026-11-26'
A01 = P+'D5-I251-A01-RQ01-ENTRY-AUTHORITY-SCOPE-CANDIDATE.json'
REQUEST = P+'D5-I271-RQ01-RT01-ENTRY-AUTHORITY-REQUEST-CANDIDATE.json'
PACKET = P+'D5-I273-RQ01-RT01-EVIDENCE-RECEPTION-PACKAGE-CANDIDATE.json'
CONSOLIDATED = P+'D5-I269-A01-A08-CONSOLIDATED-HANDOFF-CANDIDATE.json'
REQUEST_REVIEW = P+'D5-I272-I271-documentary-review.json'
PACKET_REVIEW = P+'D5-I274-I273-documentary-review.json'
SUBJECT = P+'D5-I275-RQ01-RT01-RECEPTION-PACKAGE-HANDOFF-CANDIDATE.json'
PRIOR_PREP = P+'D5-I275-preparation-review.json'
PRIOR_AUDIT = P+'D5-I275-audit.py'
PRIOR_SEAL = P+'D5-I275-integrity.json'
PRIOR_DOC = 'docs/design/D5-I275-RQ01-RT01-RECEPTION-PACKAGE-HANDOFF.md'
PRIOR_FILES = {SUBJECT,PRIOR_PREP,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I276-I275-source-reconstruction.json'
REVIEW = P+'D5-I276-I275-documentary-review.json'
AUDIT = P+'D5-I276-audit.py'
SEAL = P+'D5-I276-integrity.json'
DOC = 'docs/design/D5-I276-I275-RECEPTION-HANDOFF-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_RECEPTION_HANDOFF_REVIEW_PUBLICATION_NOT_DISPATCH_OR_ACCEPTANCE_SD01_ACTIVE_NOT_ADMITTED'


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


ATTACHMENTS = [('A01_ORIGINAL',A01,''),('RQ01_RT01_REQUEST',REQUEST,''),('REQUEST_DOCUMENTARY_REVIEW',REQUEST_REVIEW,''),
('EMPTY_RECEPTION_PACKAGE',PACKET,''),('PACKET_DOCUMENTARY_REVIEW',PACKET_REVIEW,''),('CONSOLIDATED_ENTRY',CONSOLIDATED,'/first_material_request')]
SECTIONS = 'preparation_boundary worksheet_descriptions reception_sequence material_disposition_policy documentary_integrity_policy documentary_trace_policy subject_reconciliation_requests information_section_routes universal_delivery_requirement eligibility_boundary separation_reconciliation_requests RC_reconciliation_requests inherited_A01_boundaries empty_actual_material_state missing_material_route complete_A01_followthrough critical_boundaries final_route_boundary'.split()
TOPICS = 'recipients delivery_authority document_manifest empty_packet available_material integrity_claims trace_scope eligibility_phase genuine_reviews gaps_changes complete_A01 limited_final_route'.split()


def inspect(d):
    p,r=rd(PACKET),rd(REQUEST)
    assert d['handoff_id']=='PGE251-RQ01-RT01-RECEPTION-HANDOFF-CANDIDATE-01' and (d['lot_id'],d['request_id'],d['return_id'])==('A01','RQ01','RT01')
    assert d['packet_source']==pin(PACKET) and d['latest_review']==pin(PACKET_REVIEW)
    cover=d['cover_note'];assert cover['subject'] and cover['text'] and cover['recipient_roles_only']==['EA01/SCOPE_AUTHORITY','EA02/R06','EA03/R08']
    assert cover['is_draft_only'] is True and cover['sent'] is False and cover['contact_or_delivery_authorized'] is False;missing(cover)
    manifest=d['documentary_attachment_manifest'];assert len(manifest)==6
    for row,(i,path,ptr) in zip(manifest,ATTACHMENTS):
        assert row['id']==i and row['source']==pin(path,ptr);fragment(row['source'])
        truth(row,['documentary_source_only_not_genuine_authority_or_received_evidence','no_self_hash_runtime_input_or_active_binding_created'])
    for path in [REQUEST_REVIEW,PACKET_REVIEW]:assert rd(path)['findings']==[] and rd(path)['provenance']['actor_independent'] is False
    roles=d['role_handoff_cards'];assert [x['id'] for x in roles]==['EA01','EA02','EA03'] and [x['required_role'] for x in roles]==['SCOPE_AUTHORITY','R06','R08']
    for i,row in enumerate(roles):
        src=r['subject_evidence_requests'][i]
        assert row['subject_source']==pin(REQUEST,'/subject_evidence_requests/'+str(i)) and row['exact_subject_requirement']==fragment(row['subject_source'])==src
        assert row['packet_reconciliation_source']==pin(PACKET,'/subject_reconciliation_requests/'+str(i)) and fragment(row['packet_reconciliation_source'])==p['subject_reconciliation_requests'][i]
        assert row['mandatory_material_fields']==src['mandatory_material_fields'] and len(row['mandatory_material_fields'])==7
        assert row['return_information_section_names']==[s['name'] for s in r['requested_information_sections']]
        assert row['dispatched'] is False and row['received'] is False;missing(row)
    worksheets=d['worksheet_manifest'];assert [x['name'] for x in worksheets]==['delivery','body_reference','person_authority','review_decision','gap_change']
    for i,row in enumerate(worksheets):
        assert row['source']==pin(PACKET,'/worksheet_descriptions/'+str(i)) and fragment(row['source'])==p['worksheet_descriptions'][i]
        assert row['field_description_count']==len(p['worksheet_descriptions'][i]['field_descriptions']) and row['descriptions_not_positive_record_or_genuine_body_count'] is True
    assert [x['field_description_count'] for x in worksheets]==[8,10,7,7,6] and sum(x['field_description_count'] for x in worksheets)==38
    routes=d['packet_requirement_routes'];assert [x['section'] for x in routes]==SECTIONS
    for row,s in zip(routes,SECTIONS):
        assert row['source']==pin(PACKET,'/'+s) and fragment(row['source'])==p[s] and row['requirements_retained_complete_by_immutable_reference'] is True;missing(row)
    checklist=d['delivery_and_acceptance_checklist'];assert [x['id'] for x in checklist]==['HC%02d'%i for i in range(1,13)] and [x['topic'] for x in checklist]==TOPICS
    for row in checklist:
        assert row['requirement'] and row['disposition']=='PENDING_GENUINE_RECIPIENTS_OWN_DELIVERY_AUTHORITY_MATERIAL_AND_DECISIONS';missing(row)
    boundaries=d['three_boundaries'];assert set(boundaries)=={'documentary_publication','dispatch_to_people','reception_review_acceptance'}
    pub=boundaries['documentary_publication'];assert pub['current_scope']=='PREPARE_AUDIT_COMMIT_PUSH_EMPTY_DOCUMENTS_ONLY' and pub['not_canonical_authority_or_scope_adoption'] is True
    dispatch=boundaries['dispatch_to_people'];assert dispatch['requires_separate_exact_own_contact_delivery_authority_canonical_recipient_channel_and_scope'] is True
    assert dispatch['authorized_now'] is False and dispatch['performed'] is False;missing(dispatch)
    intake=boundaries['reception_review_acceptance'];assert intake['source']==pin(PACKET,'/preparation_boundary') and intake['exact_requirement']==fragment(intake['source'])==p['preparation_boundary']
    assert intake['no_receipt_or_publication_or_hash_as_genuine_authority_or_acceptance'] is True and intake['authorized_now'] is False and intake['performed'] is False;missing(intake)
    available=d['future_return_routes']['available_material'];assert available['source']==pin(PACKET,'/material_disposition_policy') and available['exact_requirement']==fragment(available['source'])==p['material_disposition_policy']
    assert available['only_genuinely_supplied_available_bodies_with_own_authorized_provenance'] is True and available['provided_real_bodies']==available['rejected_real_bodies']==[]
    assert type(available['actual_evaluations']) is int and available['actual_evaluations']==0;missing({k:v for k,v in available.items() if k!='actual_evaluations'})
    gap=d['future_return_routes']['missing_or_changed_material'];assert gap['source']==pin(PACKET,'/missing_material_route') and gap['exact_requirement']==fragment(gap['source'])==p['missing_material_route']
    assert gap['keep_SD01_and_negative_pending_no_global_absence_or_infeasibility_or_calendar_claim'] is True;missing(gap,['actual_work_performed'])
    integrity=d['integrity_and_trace']
    for ref,value,section in [('integrity_source','exact_integrity_requirement','documentary_integrity_policy'),('trace_source','exact_trace_requirement','documentary_trace_policy')]:
        assert integrity[ref]==pin(PACKET,'/'+section) and integrity[value]==fragment(integrity[ref])==p[section]
    assert integrity['no_incoming_evidence_personal_data_or_claim_automatically_committed_pushed_published'] is True;missing(integrity,['actual_codec_crypto_probe_or_storage_backend_created'])
    state=d['missing_state'];assert state['actual_delivery_records']==[] and type(state['actual_receipts_or_acceptances_created']) is int and state['actual_receipts_or_acceptances_created']==0
    missing({k:v for k,v in state.items() if k not in ['actual_delivery_records','actual_receipts_or_acceptances_created']})
    assert state['SD01_stop_active'] is True and state['RQ01_sent'] is False and state['RQ02_or_downstream_enabled'] is False
    complete=d['complete_A01_boundary'];assert complete['source']==pin(PACKET,'/complete_A01_followthrough') and complete['exact_requirement']==fragment(complete['source'])==p['complete_A01_followthrough']
    assert complete['handoff_or_delivery_not_complete_RT01_or_A01_acceptance'] is True;missing(complete)
    assert len(d['critical_boundaries'])==22 and all(v is True for v in d['critical_boundaries'].values())
    final=d['final_route_boundary'];assert final['source']==pin(PACKET,'/final_route_boundary') and final['exact_requirement']==fragment(final['source'])==p['final_route_boundary']
    assert final['current_run_command'] is None;missing(final,['actual_final_route_or_receipt_authorized'])
    assert d['current_effect']=={**p['current_effect'],'RQ01_RT01_empty_reception_package_documentary_handoff_prepared':True,'actual_RQ01_RT01_handoff_dispatch_delivery_or_genuine_acceptance_created':False}
    assert all(d['producer'][k] is False for k in ['actor_independent','competent_primary_role_review','separate_R08_acceptance','external_contacts_made'])
    assert d['publication']['only_empty_documentary_handoff_published'] is True
    pointers(d)
    return dict(manifest_ids=[x['id'] for x in manifest],subject_roles={x['id']:x['required_role'] for x in roles},worksheet_field_counts=[8,10,7,7,6],
        full_packet_sections=SECTIONS,handoff_condition_topics=TOPICS,publication_dispatch_reception_acceptance_distinct=True,actual_external_body_count=None,
        actual_dispatches=0,actual_receipts=0,actual_genuine_authorities_or_acceptances=0)

CRITERIA = [
'Local handoff preserves I273/I271/A01 exact sources,no actual dispatch,receipt,evidence intake,authority or new protocol/backend.',
'Cover note has only EA01/R06/R08 role recipients,no actual people,channel,custodian,contact authority or acknowledgment;draft unsent.',
'Six attachment IDs/digests/pointers exact,including I269 entry and I272/I274 reviews,documentary integrity not genuine proof.',
'Same-assistant review sources preserve provenance,not independent actor authority or acceptance.',
'Three role cards preserve EA01 scope authority,EA02 R06,EA03 R08,without proving three actual/distinct people or nomination.',
'All seven material groups and six information sections per subject retain original complete requirement/reconciliation sources.',
'Five worksheet sources preserve8/10/7/7/6 field counts,38 descriptions,not positive records or actual body count.',
'Eighteen complete packet requirement routes retain source hashes/pointers with no accepted material or weakened requirement.',
'Twelve HC conditions preserve distinct topics,all pending with no own-authority evidence or real primary/separate decision.',
'Authorized documentary preparation/audit/commit/push differs from canonical scope adoption/authority,dispatch or acceptance.',
'Dispatch to people requires exact own contact/delivery authority,canonical recipient/channel/custodian/scope;not authorized or performed now.',
'Reception/review/acceptance likewise requires own authority and genuine material/actors,no receipt/publication/hash as acceptance.',
'Only genuinely supplied available bodies with own authorized provenance may be considered later;no contact/fetch/services now.',
'Four material states retained;PROVIDED_NOT_ACCEPTED no authority/truth/admission or SD01 lift,not a gate decision.',
'Raw supplied/recomputed digests separate from canonical/JCS/signature claims and competent authorized verification,no codec/crypto/probe here.',
'Bytes/hash agreement no authorship,authority,currentness,competence,independence or truth proof.',
'Documentary trace no backend/durability/global-ledger/intrinsic-custody guarantee;no storage path/service/runtime input selected.',
'No future incoming evidence/personal data/claim automatically committed/pushed/published from empty handoff.',
'Preexisting EA01/R06/R08 own authority independent of user docs request/Git/assistant/self/future W02/bundle/root sole basis.',
'Fourteen exclusions and all actual preparers require canonical identity/competence/appointments and genuine independence,no label/key inference.',
'W02 eligibility not backward acceptance/full future roster/CE10 prerequisite,no blanket R01/R02 separation or future-author preapproval.',
'Logical scope distinct from effective W03 freeze,unknown null not zero or predictive hash.',
'Sixteen RC requirements not twelve full A01 criteria,no same-assistant PASS/flag/publication as genuine R06/R08 decision.',
'RT01/receipt/kit delivery does not replace RT02-RT05,three A01 deliverables/three exits/own reviews or enable RQ02.',
'Actual external reference inventory/body count unknown;zero dispatch/delivery/evaluation records not zero external proof universe.',
'Every missing/provided/rejected/incompatible body/scope/assumption/dependent visible,no acceptance from no rejection or global infeasibility/calendar inferred.',
'Changed material invalidates any affected A01-A08 with fresh review,no automatic proof/approval/mapping/acceptance transfer or active rebind.',
'Both Readers/global reference/native/IO/crypto/copy/ledger/output/failure costs,caps/guards/quotas/reserves unchanged,no hidden/free inputs.',
'CE12 private receipt31 separately deferred,with four preclaim external prerequisites then actual claim/construction before receipt.',
'Claim not own precondition,no free retry/reuse;final E06/Q/root/claim/spawn/receipt not new entry/prelaunch condition.',
'No canonical authority,eligibility,receipt,review,acceptance,resource truth or900 fit from source manifest/PASS/publication.',
'I122/CP07/atomicity/components/E06/IR03 negative state preserved,no SOURCE_CAPACITY_VERIFIED/certificate/PJC115-R2/D5 release or active quota/authority/destination change.'
]


def reconstruct():
    d=rd(SUBJECT);result=inspect(d);pins={**d['input_pins'],**{p:sha(p) for p in PRIOR_FILES}}
    assert len(pins)==1177;verify_blobs(pins)
    return dict(schema='d5.i276-source-reconstruction.v1',increment='I276',date=DATE,timezone='Europe/Madrid',base_commit=BASE,subject=pin(SUBJECT),input_pins=pins,
        independent_reconstruction=result,criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],
        current_effect={**d['current_effect'],'RQ01_RT01_empty_reception_package_documentary_handoff_reviewed':True})


def own_rejections(d):
    cases=[
('role_recipient_changed',('cover_note','recipient_roles_only'),['EA01/SCOPE_AUTHORITY']),('manifest_missing',('documentary_attachment_manifest',),d['documentary_attachment_manifest'][:-1]),
('manifest_id_reassigned',('documentary_attachment_manifest',0,'id'),'EMPTY_RECEPTION_PACKAGE'),('manifest_pointer',('documentary_attachment_manifest',5,'source','json_pointer'),'/cover_note'),
('role_subject_reassigned',('role_handoff_cards',0,'required_role'),'R06'),('role_source_changed',('role_handoff_cards',0,'subject_source','json_pointer'),'/subject_evidence_requests/1'),
('material_fields_removed',('role_handoff_cards',1,'mandatory_material_fields'),[]),('section_names_removed',('role_handoff_cards',1,'return_information_section_names'),[]),
('worksheet_missing',('worksheet_manifest',),d['worksheet_manifest'][:-1]),('worksheet_count_wrong',('worksheet_manifest',1,'field_description_count'),9),
('route_pointer_changed',('packet_requirement_routes',0,'source','json_pointer'),'/worksheet_descriptions'),('route_requirements_weakened',('packet_requirement_routes',0,'requirements_retained_complete_by_immutable_reference'),False),
('condition_missing',('delivery_and_acceptance_checklist',),d['delivery_and_acceptance_checklist'][:-1]),('condition_topic_changed',('delivery_and_acceptance_checklist',0,'topic'),'document_manifest'),
('condition_promoted',('delivery_and_acceptance_checklist',0,'disposition'),'ACCEPTED'),('canonical_scope_from_publication',('three_boundaries','documentary_publication','not_canonical_authority_or_scope_adoption'),False),
('delivery_authority_waived',('three_boundaries','dispatch_to_people','requires_separate_exact_own_contact_delivery_authority_canonical_recipient_channel_and_scope'),False),
('intake_source_changed',('three_boundaries','reception_review_acceptance','source','json_pointer'),'/empty_actual_material_state'),
('hash_as_acceptance',('three_boundaries','reception_review_acceptance','no_receipt_or_publication_or_hash_as_genuine_authority_or_acceptance'),False),
('foreign_provenance',('future_return_routes','available_material','only_genuinely_supplied_available_bodies_with_own_authorized_provenance'),False),
('new_body',('future_return_routes','available_material','provided_real_bodies'),[{}]),('evaluation_created',('future_return_routes','available_material','actual_evaluations'),1),
('gap_as_infeasibility',('future_return_routes','missing_or_changed_material','keep_SD01_and_negative_pending_no_global_absence_or_infeasibility_or_calendar_claim'),False),
('raw_digest_proves_authority',('integrity_and_trace','exact_integrity_requirement','raw_hash_or_byte_match_not_authorship_authority_validity_competence_or_independence'),False),
('trace_as_durability',('integrity_and_trace','exact_trace_requirement','documentary_append_trace_policy_not_enforced_backend_durability_global_ledger_or_custody_proof'),False),
('provider_fabricated',('missing_state','actual_named_recipients_or_provider'),'UNVERIFIED_TEST_LABEL'),('body_inventory_fabricated',('missing_state','actual_incoming_body_or_full_reference_inventory'),[]),
('acceptance_created',('missing_state','actual_receipts_or_acceptances_created'),1),('RT05_removed',('complete_A01_boundary','exact_requirement','exact_requirement','remaining_return_ids'),['RT02','RT03','RT04']),
('receipt_precondition',('final_route_boundary','exact_requirement','exact_requirement','exact_requirement','no_final_route_execution_claim_spawn_receipt_as_new_precondition_of_prelaunch_acceptance'),False),
('claim_self_condition',('final_route_boundary','exact_requirement','exact_requirement','exact_requirement','claim_not_own_precondition_no_free_retry_uncertain_partial_expired_states'),False),
('scope_transfer',('critical_boundaries','changed_material_invalidates_affected_A01_A08_no_automatic_proof_approval_mapping_acceptance_transfer_or_rebind'),False),
('dispatch_created',('current_effect','actual_RQ01_RT01_handoff_dispatch_delivery_or_genuine_acceptance_created'),True),('assistant_primary',('producer','competent_primary_role_review'),True),
('incoming_evidence_published',('publication','only_empty_documentary_handoff_published'),False)]
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
    return dict(schema='d5.i276-documentary-review.v1',increment='I276',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),reconstruction=pin(RECON),verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_LOCAL_HANDOFF_NOT_DISPATCH_GENUINE_AUTHORITY_OR_ACCEPTANCE',findings=[],criteria=rec['criteria'],independent_reconstruction=rec['independent_reconstruction'],
        counts=dict(input_pins=1177,preserved_published_files=869,documentary_sources=6,role_cards=3,material_groups=7,worksheet_groups=5,worksheet_field_descriptions=38,
            full_packet_sections=18,handoff_conditions=12,material_states=4,separation_rules=14,RC_rows=16,full_A01_criteria=12,A01_deliverables=3,A01_exits=3,review_criteria=len(CRITERIA),
            actual_dispatches_or_receipts_or_acceptances=0,actual_received_bodies=0,prelaunch_gates_closed=0,resource_obligations_closed=0),
        inherited_I275_rejection_checks=prep['rejection_checks'],additional_I276_rejection_checks=own_rejections(rd(SUBJECT)),
        clarifications=['Publication of empty local documents is authorized; dispatch to canonical people and genuine reception/review/acceptance remain separate acts with their own exact authority,not performed or enabled by the handoff.',
            'Six source references are documentary attachments only,not actual transmitted evidence. Role cards are requirements,not nomination or proof of3 canonical/distinct humans. All people/channels/authority/provider/receipt remain unknown.',
            'Manifest hashes establish document integrity only. Raw digests/canonical or signature claims/competent verification/authentic authority/acceptance remain distinct; trace is no selected backend or durable/global-ledger proof.',
            'Zero delivery/evaluation records describes work performed; actual external body/reference count remains unknown. No provider gap report,positive authority body or genuine decision is manufactured.',
            'W02 eligibility is not a backward acceptance/future full-roster/CE10 condition and logical scope not predictive W03 freeze. All14 exclusions and preparers remain genuine requirements.',
            '16 RC rows do not replace12 full A01 criteria,RT02-RT05,three deliverables/three exits or genuine R06/R08 decisions. RT01/handoff/receipt never automatically enables RQ02.',
            'All gaps/changes stay visible and invalidate affected A01-A08 before progress,no proof/approval/mapping/acceptance transfer. Further same-assistant PASS or publication cannot supply missing genuine evidence.',
            'CE12/private receipt31 remains deferred under separate exact authority,no final E06/Q/root/claim/spawn/receipt new entry/prelaunch condition or automatic certificate/PJC115-R2/D5 release.'],
        source_reconstruction=dict(primary_source_checks=True,I275_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        current_effect=rec['current_effect'],provenance=dict(identity='Same Codex assistant/chat as I275/I273/A01',documentary_review_only=True,actor_independent=False,competent_primary_role_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['Local handoff unsent,packet empty,preexisting EA01/R06/R08 authority/eligibility and competent independent decisions missing,SD01 active,RQ01 unsent. No actual delivery/intake/authority/acceptance created.',
            'All A01-A08,30 gates,E01-E05/20 criteria,PJC115-R2 and D5 remain unaccepted/open. Documentary JSON/hash/pointer/graph/mutation PASS proves no canonical human authority,resource truth,capacity,service or900 fit.',
            'No product/component execution,codec/crypto/signing/keygen/enrollment/contact/provision/configuration/probe,quota/reserve/binding/authority/destination/certificate change. CE12/final route separately deferred.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I276-audit.py',expected_result=STATUS,over400_lines=True,
            reason='One local reception-handoff review with independent manifest/role/boundary/source reconstruction,pins,rejection checks and preservation; overage declared,no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage/graph checks and in-memory mutations only; no target import,compile,discovery,tests,execution,build,benchmark,codec,crypto,signing,keygen,enrollment,contacts,provision,configuration or platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes.'),
        publication=dict(commit_and_push_requested=True,publication_not_dispatch_receipt_genuine_authority_review_acceptance_execution_or_D5_closure=True))


def main():
    rec=reconstruct();assert rec==rd(RECON)
    review=build_review(rec);assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published864'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)};assert len(preserved)==869
    seal=rd(SEAL);assert seal['schema']=='d5.i276-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published869']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for p,h in mapping.items():assert sha(p)==h,p
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,input_pins=1177,preserved_published_files=869,new_files=5,review_criteria=len(CRITERIA),inherited_rejections=len(review['inherited_I275_rejection_checks']),additional_rejections=len(review['additional_I276_rejection_checks']),findings=review['findings'],prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
