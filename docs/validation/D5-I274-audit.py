#!/usr/bin/env python3
"""I274 empty reception package documentary review; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '65dde986762f674f5287addc89e3431322047db9'
DATE = '2026-11-26'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
A01 = P+'D5-I251-A01-RQ01-ENTRY-AUTHORITY-SCOPE-CANDIDATE.json'
REQUEST = P+'D5-I271-RQ01-RT01-ENTRY-AUTHORITY-REQUEST-CANDIDATE.json'
SUBJECT = P+'D5-I273-RQ01-RT01-EVIDENCE-RECEPTION-PACKAGE-CANDIDATE.json'
PRIOR_PREP = P+'D5-I273-preparation-review.json'
PRIOR_AUDIT = P+'D5-I273-audit.py'
PRIOR_SEAL = P+'D5-I273-integrity.json'
PRIOR_DOC = 'docs/design/D5-I273-RQ01-RT01-EVIDENCE-RECEPTION-PACKAGE.md'
PRIOR_FILES = {SUBJECT,PRIOR_PREP,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I274-I273-source-reconstruction.json'
REVIEW = P+'D5-I274-I273-documentary-review.json'
AUDIT = P+'D5-I274-audit.py'
SEAL = P+'D5-I274-integrity.json'
DOC = 'docs/design/D5-I274-I273-RECEPTION-PACKAGE-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_EMPTY_RECEPTION_PACKAGE_REVIEW_INTEGRITY_NOT_AUTHORITY_OR_ACCEPTANCE_SD01_ACTIVE_NOT_ADMITTED'


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


WORKSHEET_COUNTS = dict(delivery=8,body_reference=10,person_authority=7,review_decision=7,gap_change=6)
STEP_NAMES = 'before_any_intake record_delivery_without_acceptance record_integrity_without_authenticity reconcile_scope_and_eligibility independent_review_and_separate_decision missing_changed_or_incompatible limited_followthrough'.split()


def inspect(d):
    r,a,acq=rd(REQUEST),rd(A01),rd(ACQUISITION)
    assert d['package_id']=='PGE251-RQ01-RT01-RECEPTION-CANDIDATE-01' and (d['lot_id'],d['request_id'],d['return_id'])==('A01','RQ01','RT01')
    assert d['request_source']==pin(REQUEST) and d['exact_RT01_requirement_source']==pin(A01,'/requested_returns/0') and d['exact_RT01_requirement']==fragment(d['exact_RT01_requirement_source'])==a['requested_returns'][0]
    boundary=d['preparation_boundary'];assert boundary['preparation_only'] is True and boundary['actual_operational_intake_or_verification_authorized_now'] is False
    truth(boundary,['SD01_stop_active','no_nomination_fetch_verification_service_or_material_generation'])
    assert boundary['RQ01_sent'] is False and boundary['external_contacts_made'] is False;missing(boundary,['actual_operational_intake_or_verification_authorized_now'])
    worksheets=d['worksheet_descriptions'];assert [x['name'] for x in worksheets]==list(WORKSHEET_COUNTS)
    for row in worksheets:
        fields=row['field_descriptions'];assert len(fields)==len(set(fields))==WORKSHEET_COUNTS[row['name']]
        assert all(isinstance(f,str) and f for f in fields) and row['documentary_description_not_instantiated_positive_record_or_runtime_schema'] is True
        missing(row,['actual_records_created'])
    fields=worksheets[1]['field_descriptions']
    assert {'complete_original_bytes_and_byte_count','provided_raw_digest_and_algorithm','documentary_recomputed_raw_digest_if_separately_permitted','provided_canonical_digest_and_encoding_claim','canonical_codec_or_crypto_verification_status_and_authority'}<=set(fields)
    assert sum(len(x['field_descriptions']) for x in worksheets)==38
    steps=d['reception_sequence'];assert [x['step'] for x in steps]==STEP_NAMES
    for row in steps:assert row['requirement'] and row['performed'] is False;missing(row)
    dispositions=d['material_disposition_policy'];assert dispositions['source']==pin(ACQUISITION,'/intake_and_review_workflow') and fragment(dispositions['source'])==acq['intake_and_review_workflow']
    assert dispositions['exact_material_states']==acq['intake_and_review_workflow']['allowed_future_dispositions']
    truth(dispositions,['provided_not_accepted_never_proves_authority_truth_or_admission','material_states_not_gate_decisions','missing_body_or_own_authority_keeps_SD01']);missing(dispositions,['actual_any_material_disposition_decision_created'])
    integrity=d['documentary_integrity_policy'];truth(integrity,[
        'original_bytes_and_provider_claims_retained_without_overwrite','supplied_raw_digest_separate_from_documentary_recomputed_raw_digest',
        'supplied_canonical_digest_codec_or_signature_claim_separate_from_actual_authorized_verification','raw_hash_or_byte_match_not_authorship_authority_validity_competence_or_independence',
        'no_positive_codec_crypto_signing_keygen_or_operational_integrity_probe_here']);missing(integrity,['actual_positive_verification_performed'])
    trace=d['documentary_trace_policy'];assert trace['source']==pin(A01,'/change_control') and trace['exact_requirement']==fragment(trace['source'])==a['change_control']
    truth(trace,['preserve_original_claims_and_trace_changes_supersession_and_affected_review','documentary_append_trace_policy_not_enforced_backend_durability_global_ledger_or_custody_proof',
        'no_backend_storage_path_service_or_runtime_Reader_member_selected','no_incoming_body_personal_data_or_claim_automatically_committed_pushed_or_published']);missing(trace,['actual_refresh_or_rebind'])
    subjects=d['subject_reconciliation_requests'];assert [x['id'] for x in subjects]==['EA01','EA02','EA03'] and [x['required_role'] for x in subjects]==['SCOPE_AUTHORITY','R06','R08']
    for i,row in enumerate(subjects):
        src=r['subject_evidence_requests'][i];assert row['source']==pin(REQUEST,'/subject_evidence_requests/'+str(i)) and row['exact_requirement']==fragment(row['source'])==src
        assert row['mandatory_material_fields']==src['mandatory_material_fields'] and len(row['mandatory_material_fields'])==7 and row['current_material_state']=='MISSING';missing(row)
    sections=d['information_section_routes'];assert [x['name'] for x in sections]==[x['name'] for x in r['requested_information_sections']]
    for i,row in enumerate(sections):
        src=r['requested_information_sections'][i];assert row['source']==pin(REQUEST,'/requested_information_sections/'+str(i)) and fragment(row['source'])==src
        assert row['applies_to']==src['applies_to']==['EA01','EA02','EA03'];missing(row)
    universal=d['universal_delivery_requirement'];assert universal['source']==pin(REQUEST,'/universal_delivery_requirement') and universal['exact_requirement']==fragment(universal['source'])==r['universal_delivery_requirement'];missing(universal)
    assert len(universal['exact_requirement']['mandatory_fields'])==8
    eligibility=d['eligibility_boundary'];assert eligibility['source']==pin(A01,'/eligibility_boundary') and eligibility['exact_requirement']==fragment(eligibility['source'])==a['eligibility_boundary']
    truth(eligibility,['all_actual_preparers_scope_no_future_author_preapproval','W02_criteria_not_backward_W02_acceptance_or_future_full_roster_CE10_requirement']);missing(eligibility,['actual_people_appointments_keys_or_independence_verified'])
    exclusions=d['separation_reconciliation_requests'];assert [x['id'] for x in exclusions]==['SP%02d'%i for i in range(1,15)]
    for i,row in enumerate(exclusions):
        src=a['eligibility_boundary']['exact_separation_matrix'][i]
        assert row['source']==pin(A01,'/eligibility_boundary/exact_separation_matrix/'+str(i)) and fragment(row['source'])==src
        assert row['rule']==src['rule'] and row['scope']==src['scope'] and row['verified'] is False;missing(row)
    checks=d['RC_reconciliation_requests'];assert [x['id'] for x in checks]==['RC%02d'%i for i in range(1,17)]
    for i,row in enumerate(checks):
        src=r['RT01_intake_checklist'][i];assert row['source']==pin(REQUEST,'/RT01_intake_checklist/'+str(i)) and fragment(row['source'])==src
        assert (row['id'],row['topic'],row['criterion'])==(src['id'],src['topic'],src['criterion'])
        assert row['current_disposition']=='PENDING_GENUINE_MATERIAL_AND_COMPETENT_PRIMARY_SEPARATE_DECISIONS';missing(row)
    inherited=d['inherited_A01_boundaries'];assert [x['section'] for x in inherited]==[x['section'] for x in r['inherited_A01_boundaries']] and len(inherited)==9
    for i,row in enumerate(inherited):assert row['source']==pin(REQUEST,'/inherited_A01_boundaries/'+str(i)) and row['exact_requirement']==fragment(row['source'])==r['inherited_A01_boundaries'][i]
    state=d['empty_actual_material_state'];record_keys=['delivery_records','body_reference_records','person_authority_records','review_decision_records','gap_change_records']
    assert all(state[k]==[] for k in record_keys)
    for key in ['actual_evaluations','actual_genuine_authorities_or_acceptances_created','actual_delivery_records_received']:assert type(state[key]) is int and state[key]==0
    assert all(state[k] is None for k in ['actual_full_reference_inventory','actual_available_original_bodies','actual_provider_custodian_or_own_receipt_authority'])
    truth(state,['original_document_pins_not_genuine_evidence_body_count','unknown_external_reference_count_not_zero'])
    gap=d['missing_material_route'];assert gap['current_state']=='MISSING_NOT_RECEIVED_NOT_EVALUATED'
    truth(gap,['SD01_stop_active','every_missing_rejected_incompatible_body_subject_scope_assumption_and_dependents_must_remain_visible',
        'no_accepted_material_from_absence_of_rejection_or_template_or_hash','gap_needs_separate_exact_work_authority_not_fabrication_contact_execution_or_global_infeasibility']);missing(gap,['actual_work_performed'])
    follow=d['complete_A01_followthrough'];assert follow['source']==pin(REQUEST,'/complete_A01_followthrough') and follow['exact_requirement']==fragment(follow['source'])==r['complete_A01_followthrough']
    truth(follow,['receipt_or_integrity_or_RT01_acceptance_not_complete_A01_or_RQ02_authority']);assert follow['RQ02_or_downstream_enabled'] is False;missing(follow)
    assert len(fragment(follow['exact_requirement']['A01_intake_source']))==12 and len(fragment(follow['exact_requirement']['A01_deliverable_source']))==len(fragment(follow['exact_requirement']['A01_exit_source']))==3
    assert len(d['critical_boundaries'])==24 and all(v is True for v in d['critical_boundaries'].values())
    final=d['final_route_boundary'];assert final['source']==pin(REQUEST,'/final_route_boundary') and final['exact_requirement']==fragment(final['source'])==r['final_route_boundary']
    assert final['current_run_command'] is None;missing(final,['actual_final_route_or_receipt_authorized'])
    assert d['current_effect']=={**r['current_effect'],'RQ01_RT01_empty_documentary_reception_package_prepared':True,'actual_RQ01_RT01_delivery_intake_evidence_store_or_genuine_acceptance_created':False}
    assert all(d['producer'][k] is False for k in ['actor_independent','competent_primary_role_review','separate_R08_acceptance','external_contacts_made'])
    assert d['publication']['only_empty_documentary_package_published_no_actual_incoming_evidence'] is True
    pointers(d)
    return dict(worksheet_field_counts=WORKSHEET_COUNTS,worksheet_descriptions=38,reception_steps=STEP_NAMES,material_states=dispositions['exact_material_states'],
        subject_roles={x['id']:x['required_role'] for x in subjects},separation_rows=14,RC_rows=16,full_A01_criteria=12,
        actual_record_lists_empty=record_keys,actual_reference_inventory=None,actual_external_body_count=None,actual_evaluations=0,
        byte_integrity_not_authority_or_acceptance=True,documentary_trace_not_global_ledger_or_backend_proof=True,actual_genuine_acceptances=0)

CRITERIA = [
'Package preserves exact A01/RT01 and I271 requirements; empty local worksheets are no delivery,evidence store or positive wire schema.',
'Preparation only,no operational intake/verification/contact authority,people/provider/schedule/delivery;SD01 active,RQ01 unsent.',
'Five worksheet groups retain38 field descriptions with no instantiated record or backend/runtime member.',
'Seven future steps remain descriptions,none performed; own authorized genuine material required before any intake.',
'Four I251 material states retained;PROVIDED_NOT_ACCEPTED never proves truth,authority or lifts SD01 and is not gate disposition.',
'Original complete bytes/locator/count and provider claims retained without overwriting or manufacturing evidence.',
'Supplied and documentary-recomputed raw digests remain distinct with own authority and no implied canonical encoding.',
'Canonical/JCS/signature claims stay separate from actual competent authorized verification; no positive codec/crypto/signing/keygen.',
'Byte/hash equality proves no authorship,authority,competence,independence,currentness or acceptance.',
'Documentary trace/supersession/invalidation is no enforced backend,durability,intrinsic custody or global-ledger proof.',
'No storage path/service/backend/runtime Reader input/helper/channel chosen and no incoming bodies/personal data auto-published.',
'EA01 scope authority,EA02 R06,EA03 R08 preserve original roles and seven material groups,without actual people or body refs.',
'Six information-section routes and eight universal delivery fields retain exact scope/requirements and availability/provenance assumptions.',
'Authority must preexist independently of user docs request/Git/assistant/self assertion/future W02/bundle/root as sole basis.',
'All14 human/key exclusions and all actual preparers retain exact source rules and no verified comparisons.',
'W02 eligibility is no reverse W02 acceptance/full future roster/CE10 prerequisite;no blanket R01/R02 prohibition or future-author preapproval.',
'Logical scope remains distinct from effective W03 source/runtime/image freeze;unknown facts null,no predictive hashes or unknown-as-zero.',
'16 RC reconciliation rows preserve exact topic/text/source with genuine R06 and separate R08 body/reason fields absent.',
'16 RC rows are distinct from12 original A01 criteria;worksheet flags never manufacture genuine competent decisions.',
'RT01 receipt/integrity/acceptance only its scope,not RT02-RT05/A01 three deliverables/three exits or RQ02 authority.',
'Nine A01 boundary sources remain complete and exact,including entry/authority/cost/handoff/change rules.',
'All five real record lists empty;no delivery/body/person/review/provider-gap claim instantiated or received.',
'Actual full reference inventory/original bodies/provider/custodian/receipt authority unknown,null;zero processed records not zero external proofs.',
'Document pins and69 typed templates are not actual unique bodies or real complete reference inventory.',
'Every missing/provided/rejected/incompatible body/subject/scope/assumption and dependents remains visible;no rejection is not acceptance.',
'Gaps require separately scoped work/authority,no fabricated person/provider/calendar/hash/positive body or inferred global infeasibility.',
'Changed author/body/source/runtime/scope/epoch/key/policy invalidates affected A01-A08 before progress,no proof/approval/acceptance transfer or rebind.',
'Both Readers/global lookup/freshness/identity/crypto/native/IO/copies/registry/ledger/receipt/output/failure costs,caps/guards/quotas/reserves unchanged.',
'CE12 private receipt31 stays deferred unauthorized;four external preclaim prerequisites plus actual claim/construction fifth before receipt distinct.',
'Claim not own precondition,no free retry/reuse;final E06/Q/root/claim/spawn/receipt not new entry/prelaunch antecedent.',
'No canonical authority,eligibility,primary/separate decision,resource truth,900 fit or certificate/PJC115-R2/D5 release from packet/PASS/publication.',
'I122/CP07/atomicity/components/E06/IR03 negative state remains,no product execution,quota/reserve/binding/authority/destination/certificate change.'
]


def reconstruct():
    d=rd(SUBJECT);result=inspect(d);pins={**d['input_pins'],**{p:sha(p) for p in PRIOR_FILES}}
    assert len(pins)==1167;verify_blobs(pins)
    return dict(schema='d5.i274-source-reconstruction.v1',increment='I274',date=DATE,timezone='Europe/Madrid',base_commit=BASE,subject=pin(SUBJECT),input_pins=pins,
        independent_reconstruction=result,criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],
        current_effect={**d['current_effect'],'RQ01_RT01_empty_documentary_reception_package_reviewed':True})


def own_rejections(d):
    cases=[
('worksheet_missing',('worksheet_descriptions',),d['worksheet_descriptions'][:-1]),('field_missing',('worksheet_descriptions',1,'field_descriptions'),d['worksheet_descriptions'][1]['field_descriptions'][:-1]),
('field_duplicate',('worksheet_descriptions',1,'field_descriptions',5),'provided_raw_digest_and_algorithm'),
('worksheet_as_schema',('worksheet_descriptions',0,'documentary_description_not_instantiated_positive_record_or_runtime_schema'),False),
('step_missing',('reception_sequence',),d['reception_sequence'][:-1]),('step_order',('reception_sequence',0,'step'),'record_delivery_without_acceptance'),
('material_states_weakened',('material_disposition_policy','exact_material_states'),['ACCEPTED']),('material_as_gate',('material_disposition_policy','material_states_not_gate_decisions'),False),
('raw_digest_conflated',('documentary_integrity_policy','supplied_raw_digest_separate_from_documentary_recomputed_raw_digest'),False),
('canonical_claim_conflated',('documentary_integrity_policy','supplied_canonical_digest_codec_or_signature_claim_separate_from_actual_authorized_verification'),False),
('overwrite_claims',('documentary_trace_policy','preserve_original_claims_and_trace_changes_supersession_and_affected_review'),False),
('EA_role_changed',('subject_reconciliation_requests',0,'required_role'),'R06'),('EA_fields_missing',('subject_reconciliation_requests',1,'mandatory_material_fields'),[]),
('EA_as_received',('subject_reconciliation_requests',0,'current_material_state'),'PROVIDED_NOT_ACCEPTED'),
('section_scope_changed',('information_section_routes',0,'applies_to'),['EA01']),('section_source_changed',('information_section_routes',0,'source','json_pointer'),'/requested_information_sections/1'),
('delivery_contract_source',('universal_delivery_requirement','source','json_pointer'),'/complete_A01_followthrough'),
('eligibility_waived',('eligibility_boundary','all_actual_preparers_scope_no_future_author_preapproval'),False),
('separation_missing',('separation_reconciliation_requests',),d['separation_reconciliation_requests'][:-1]),('separation_rule_changed',('separation_reconciliation_requests',0,'rule'),'NO_EXCLUSION'),
('RC_missing',('RC_reconciliation_requests',),d['RC_reconciliation_requests'][:-1]),('RC_text_changed',('RC_reconciliation_requests',0,'criterion'),'DOCUMENT_PRESENT'),
('RC_promoted',('RC_reconciliation_requests',0,'current_disposition'),'ACCEPTED'),('boundary_missing',('inherited_A01_boundaries',),d['inherited_A01_boundaries'][:-1]),
('body_count_known',('empty_actual_material_state','unknown_external_reference_count_not_zero'),False),('document_pins_as_proofs',('empty_actual_material_state','original_document_pins_not_genuine_evidence_body_count'),False),
('original_bodies_fabricated',('empty_actual_material_state','actual_available_original_bodies'),[]),('receipt_authority_fabricated',('empty_actual_material_state','actual_provider_custodian_or_own_receipt_authority'),{}),
('gaps_hidden',('missing_material_route','every_missing_rejected_incompatible_body_subject_scope_assumption_and_dependents_must_remain_visible'),False),
('absence_rejection_as_acceptance',('missing_material_route','no_accepted_material_from_absence_of_rejection_or_template_or_hash'),False),
('RT05_removed',('complete_A01_followthrough','exact_requirement','remaining_return_ids'),['RT02','RT03','RT04']),
('claim_self_condition',('final_route_boundary','exact_requirement','exact_requirement','claim_not_own_precondition_no_free_retry_uncertain_partial_expired_states'),False),
('receipt_precondition',('final_route_boundary','exact_requirement','exact_requirement','no_final_route_execution_claim_spawn_receipt_as_new_precondition_of_prelaunch_acceptance'),False),
('intake_progress_created',('current_effect','actual_RQ01_RT01_delivery_intake_evidence_store_or_genuine_acceptance_created'),True),
('assistant_R08',('producer','separate_R08_acceptance'),True)]
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
    return dict(schema='d5.i274-documentary-review.v1',increment='I274',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),reconstruction=pin(RECON),verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_EMPTY_PACKET_INTEGRITY_NOT_GENUINE_AUTHORITY_OR_ACCEPTANCE',findings=[],
        criteria=rec['criteria'],independent_reconstruction=rec['independent_reconstruction'],
        counts=dict(input_pins=1167,preserved_published_files=859,worksheet_groups=5,worksheet_field_descriptions=38,future_steps=7,material_states=4,entry_subjects=3,
            subject_material_groups=7,universal_fields=8,information_sections=6,separation_requirements=14,RC_rows=16,A01_criteria=12,A01_deliverables=3,A01_exits=3,
            inherited_boundaries=9,review_criteria=len(CRITERIA),actual_received_bodies=0,actual_genuine_authorities_or_acceptances=0,prelaunch_gates_closed=0,resource_obligations_closed=0),
        inherited_I273_rejection_checks=prep['rejection_checks'],additional_I274_rejection_checks=own_rejections(rd(SUBJECT)),
        clarifications=[
            'The packet is empty documentary field descriptions and pending reconciliation rows,not an actual receipt,instantiated evidence record,operational intake authority or selected storage/backend.',
            'Zero deliveries/evaluations records current work only. Actual external reference/body count and full inventory remain unknown/null; document pins and templates do not count genuine or unique proofs.',
            'PROVIDED_NOT_ACCEPTED records availability under own authorized provenance,not authority,truth or admission and never automatically lifts SD01. Material states are distinct from gate decisions.',
            'Raw supplied/recomputed digests and canonical/JCS/signature claims remain separate. Byte/hash agreement supplies no authorship,authority,competence,independence,currentness or acceptance; no positive codec/crypto or probes occur.',
            'Documentary change/supersession trace is not enforced durability,backend custody or global-ledger proof. No storage path/service/new Reader input is selected; future incoming data are not automatically published by this empty-packet commit.',
            'EA01/R06/R08 require genuine preexisting own authority and applicable14 exclusions. W02 supplies eligibility without backward W02 acceptance/full future roster/CE10; logical scope does not require predictive W03 freeze.',
            '16 RC reconciliation rows do not replace12 full A01 criteria,RT02-RT05 and genuine primary R06/separate R08 decisions. Receipt,integrity or RT01 partial acceptance cannot enable RQ02.',
            'CE12/private receipt remains deferred under separate exact authority,no final E06/Q/root/claim/spawn/receipt new entry/prelaunch condition or automatic certificate/PJC115-R2/D5 release.'],
        source_reconstruction=dict(primary_source_checks=True,I273_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        current_effect=rec['current_effect'],provenance=dict(identity='Same Codex assistant/chat as I273/I271/A01',documentary_review_only=True,actor_independent=False,competent_primary_role_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['No actual delivery,body,provider,person/authority,review/decision or gap report received/created. Preexisting authority/eligibility and independent decisions remain missing,SD01 active,RQ01 unsent.',
            'All A01-A08,30 gates,E01-E05/20 criteria,PJC115-R2 and D5 remain unaccepted/open. JSON/hash/pointer/graph/mutation PASS proves no authentic authority,capacity,service,900 fit or backend/global custody guarantee.',
            'No product/component execution,codec/crypto/signing/keygen/enrollment/contact/provision/configuration/probe,quota/reserve/binding/authority/destination/certificate change. CE12/final route separately deferred.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I274-audit.py',expected_result=STATUS,over400_lines=True,
            reason='One empty-reception-package review with independent integrity/authority/acceptance/source reconstruction,pins,rejection checks and preservation; overage declared,no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage/graph checks and in-memory mutations only; no target import,compile,discovery,tests,execution,build,benchmark,codec,crypto,signing,keygen,enrollment,contacts,provision,configuration or platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes.'),
        publication=dict(commit_and_push_requested=True,publication_not_receipt_genuine_authority_review_acceptance_execution_or_D5_closure=True))


def main():
    rec=reconstruct();assert rec==rd(RECON)
    review=build_review(rec);assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published854'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)};assert len(preserved)==859
    seal=rd(SEAL);assert seal['schema']=='d5.i274-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published859']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for p,h in mapping.items():assert sha(p)==h,p
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,input_pins=1167,preserved_published_files=859,new_files=5,review_criteria=len(CRITERIA),inherited_rejections=len(review['inherited_I273_rejection_checks']),additional_rejections=len(review['additional_I274_rejection_checks']),findings=review['findings'],prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
