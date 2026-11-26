#!/usr/bin/env python3
"""I275 local empty-package handoff preparation; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '4ae838c3c3a9908d2e7822c5db7594ee8ea59738'
DATE = '2026-11-26'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
A01 = P+'D5-I251-A01-RQ01-ENTRY-AUTHORITY-SCOPE-CANDIDATE.json'
REQUEST = P+'D5-I271-RQ01-RT01-ENTRY-AUTHORITY-REQUEST-CANDIDATE.json'
PACKET = P+'D5-I273-RQ01-RT01-EVIDENCE-RECEPTION-PACKAGE-CANDIDATE.json'
CONSOLIDATED = P+'D5-I269-A01-A08-CONSOLIDATED-HANDOFF-CANDIDATE.json'
REQUEST_REVIEW = P+'D5-I272-I271-documentary-review.json'
PRIOR_RECON = P+'D5-I274-I273-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I274-I273-documentary-review.json'
PRIOR_AUDIT = P+'D5-I274-audit.py'
PRIOR_SEAL = P+'D5-I274-integrity.json'
PRIOR_DOC = 'docs/design/D5-I274-I273-RECEPTION-PACKAGE-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I275-RQ01-RT01-RECEPTION-PACKAGE-HANDOFF-CANDIDATE.json'
PREP = P+'D5-I275-preparation-review.json'
AUDIT = P+'D5-I275-audit.py'
SEAL = P+'D5-I275-integrity.json'
DOC = 'docs/design/D5-I275-RQ01-RT01-RECEPTION-PACKAGE-HANDOFF.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_RECEPTION_PACKAGE_HANDOFF_PREPARED_NOT_SENT_NO_GENUINE_EVIDENCE_OR_ACCEPTANCE_SD01_ACTIVE_NOT_ADMITTED'


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


ATTACHMENTS = [
('A01_ORIGINAL',A01,''),('RQ01_RT01_REQUEST',REQUEST,''),('REQUEST_DOCUMENTARY_REVIEW',REQUEST_REVIEW,''),
('EMPTY_RECEPTION_PACKAGE',PACKET,''),('PACKET_DOCUMENTARY_REVIEW',PRIOR_REVIEW,''),('CONSOLIDATED_ENTRY',CONSOLIDATED,'/first_material_request')]
SECTIONS = 'preparation_boundary worksheet_descriptions reception_sequence material_disposition_policy documentary_integrity_policy documentary_trace_policy subject_reconciliation_requests information_section_routes universal_delivery_requirement eligibility_boundary separation_reconciliation_requests RC_reconciliation_requests inherited_A01_boundaries empty_actual_material_state missing_material_route complete_A01_followthrough critical_boundaries final_route_boundary'.split()
CONDITIONS = [
('recipients','Humanos canónicos y roles EA01/R06/R08 elegibles con autoridad preexistente propia;funciones e IDs no son nombramientos o tres personas probadas.'),
('delivery_authority','Destinatario/canal/custodio y autoridad exacta de contacto/entrega propios antes de un envío real;publicar documentos no concede ni ejecuta esa entrega.'),
('document_manifest','Manifiesto exacto de seis fuentes/versiones/digests/pointers,integridad documental sólo,sin hash canónico de prueba o garantía de autenticidad.'),
('empty_packet','Entregar sólo el kit vacío y requisitos:cinco grupos/38 descripciones,siete pasos futuros,sin cuerpos positivos/backend/registro real o datos entrantes auto-publicados.'),
('available_material','Retorno sólo de cuerpos genuinos disponibles con propia provenance/custodia/scope/validez y referencias completas;PROVIDED_NOT_ACCEPTED no acepta autoridad ni levanta SD01.'),
('integrity_claims','Bytes originales y digest bruto suministrado/recalculado separados de claim canónico/firma/verificación competente;sin codec/crypto/probes aquí y hash no autoridad.'),
('trace_scope','Trace/cambios/supersession documental no backend/durabilidad/ledger global;sin path/servicio/input Reader/canal/helper nuevo o coste oculto.'),
('eligibility_phase','14 exclusiones y preparadores del scope actual;W02 criterios no aceptación previa/roster final/CE10,no blanket R01/R02;scope lógico no W03 freeze/hash predictivo.'),
('genuine_reviews','16 RC preservadas y decisiones genuinas R06/R08 con cuerpos/razones en mismo scope;asistente/flags/revisión documental no decisión competente.'),
('gaps_changes','Toda ausencia/rechazo/incompatibilidad/cambio visible con dependientes A01-A08 e invalidación/review nueva,sin transferir pruebas o generar sustitutos.'),
('complete_A01','RT01 parcial/recibo/integridad no RT02-RT05,12 criterios,3 entregables/3 salidas y reviews propias A01,no habilita RQ02.'),
('limited_final_route','SD01/no admisión;CE12 privado/diferido,no evento final como condición entrada/prelaunch,claim no propia precondición/free retry;sin certificado/PJC115-R2/D5 release.')]


def build_candidate():
    p,r,a=rd(PACKET),rd(REQUEST),rd(A01)
    pins={**rd(PRIOR_RECON)['input_pins'],**{s:sha(s) for s in PRIOR_FILES}};assert len(pins)==1172
    return dict(schema='d5.i275-empty-reception-package-handoff.v1',increment='I275',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        handoff_id='PGE251-RQ01-RT01-RECEPTION-HANDOFF-CANDIDATE-01',lot_id='A01',request_id='RQ01',return_id='RT01',
        kind='LOCAL_UNSENT_EMPTY_PACKET_HANDOFF_NOT_ACTUAL_DELIVERY_RECEIPT_EVIDENCE_INTAKE_AUTHORITY_OR_ACCEPTANCE',
        status='HANDOFF_DRAFT_PREPARED_NOT_SENT_CANONICAL_RECIPIENTS_AUTHORITY_AND_GENUINE_EVIDENCE_MISSING_SD01_ACTIVE_NOT_ADMITTED',input_pins=pins,
        packet_source=pin(PACKET),latest_review=pin(PRIOR_REVIEW),
        cover_note=dict(subject='RQ01/RT01 — Handoff para revisión del paquete vacío de recepción EA01/R06/R08',
            recipient_roles_only=['EA01/SCOPE_AUTHORITY','EA02/R06','EA03/R08'],
            text='Borrador local sin envío. Para revisión bajo autoridad propia de EA01 scope authority,EA02 R06 y EA03 R08:se prepara para revisión local un índice del kit vacío I273 revisado en I274,con RQ01/RT01 y requisitos A01 originales. El manifiesto fija seis fuentes;no adjunta cuerpos de autoridad/identidad o reviews genuinas. Devolver sólo material genuino ya disponible con propia provenance:cadena preexistente de autoridad,humano canónico/aliases/competencia/appointments/scope/vigencia/independencia y cuerpos completos/locators/bytes/digests/custodia,por sujeto. Usar cinco grupos de formularios como guía documental,no como prueba positiva. Registrar disponibilidad futura no significa aceptación;separar integridad bruta de claims canónicos/firma y autoridad genuina. Declarar gaps sin generar autoridad,personas,hashes o cuerpos. No contactar/fetch/verificar servicios,firmar/keygen/crypto/enrolar/configurar/probar/ejecutar o cambiar cuotas/reservas. RT01 no acepta A01/RT02-RT05 ni habilita RQ02;SD01/no admisión siguen activos,CE12 aparte sin comando o liberación. Esta publicación no envía el handoff a personas ni autoriza recepción operacional.',
            is_draft_only=True,sent=False,contact_or_delivery_authorized=False,
            actual_coordinator_or_recipient_people=None,actual_channel_custodian_or_contact_authority=None,actual_outbound_delivery_or_receipt=None),
        documentary_attachment_manifest=[dict(id=i,source=pin(path,pointer),documentary_source_only_not_genuine_authority_or_received_evidence=True,
            no_self_hash_runtime_input_or_active_binding_created=True) for i,path,pointer in ATTACHMENTS],
        role_handoff_cards=[dict(id=x['id'],required_role=x['required_role'],subject_source=pin(REQUEST,'/subject_evidence_requests/'+str(i)),
            exact_subject_requirement=x,packet_reconciliation_source=pin(PACKET,'/subject_reconciliation_requests/'+str(i)),
            mandatory_material_fields=x['mandatory_material_fields'],return_information_section_names=[s['name'] for s in r['requested_information_sections']],
            actual_canonical_recipient_appointment_or_own_authority=None,actual_material_or_review_references=None,
            dispatched=False,received=False,accepted=False) for i,x in enumerate(r['subject_evidence_requests'])],
        worksheet_manifest=[dict(name=x['name'],source=pin(PACKET,'/worksheet_descriptions/'+str(i)),field_description_count=len(x['field_descriptions']),
            descriptions_not_positive_record_or_genuine_body_count=True) for i,x in enumerate(p['worksheet_descriptions'])],
        packet_requirement_routes=[dict(section=s,source=pin(PACKET,'/'+s),requirements_retained_complete_by_immutable_reference=True,
            actual_received_material_or_eligible_decision=None,accepted=False) for s in SECTIONS],
        delivery_and_acceptance_checklist=[dict(id='HC%02d'%(i+1),topic=topic,requirement=text,
            actual_own_authority_material_or_primary_separate_decision=None,
            disposition='PENDING_GENUINE_RECIPIENTS_OWN_DELIVERY_AUTHORITY_MATERIAL_AND_DECISIONS',accepted=False)
            for i,(topic,text) in enumerate(CONDITIONS)],
        three_boundaries=dict(
            documentary_publication=dict(current_scope='PREPARE_AUDIT_COMMIT_PUSH_EMPTY_DOCUMENTS_ONLY',not_canonical_authority_or_scope_adoption=True),
            dispatch_to_people=dict(requires_separate_exact_own_contact_delivery_authority_canonical_recipient_channel_and_scope=True,
                actual_authority_recipient_channel_or_delivery=None,authorized_now=False,performed=False),
            reception_review_acceptance=dict(source=pin(PACKET,'/preparation_boundary'),exact_requirement=p['preparation_boundary'],
                no_receipt_or_publication_or_hash_as_genuine_authority_or_acceptance=True,
                actual_intake_body_or_eligible_review_decision=None,authorized_now=False,performed=False)),
        future_return_routes=dict(available_material=dict(source=pin(PACKET,'/material_disposition_policy'),exact_requirement=p['material_disposition_policy'],
                only_genuinely_supplied_available_bodies_with_own_authorized_provenance=True,
                actual_received_inventory=None,provided_real_bodies=[],rejected_real_bodies=[],actual_evaluations=0),
            missing_or_changed_material=dict(source=pin(PACKET,'/missing_material_route'),exact_requirement=p['missing_material_route'],
                keep_SD01_and_negative_pending_no_global_absence_or_infeasibility_or_calendar_claim=True,
                actual_gap_or_new_work_authority=None,actual_work_performed=False)),
        integrity_and_trace=dict(integrity_source=pin(PACKET,'/documentary_integrity_policy'),exact_integrity_requirement=p['documentary_integrity_policy'],
            trace_source=pin(PACKET,'/documentary_trace_policy'),exact_trace_requirement=p['documentary_trace_policy'],
            no_incoming_evidence_personal_data_or_claim_automatically_committed_pushed_published=True,
            actual_raw_or_canonical_evidence_digest_or_signature=None,actual_codec_crypto_probe_or_storage_backend_created=False),
        missing_state=dict(actual_named_recipients_or_provider=None,actual_delivery_id_timestamp_or_acknowledgment=None,
            actual_incoming_body_or_full_reference_inventory=None,actual_primary_R06_or_separate_R08_decisions=None,
            actual_external_reference_body_count=None,actual_delivery_records=[],actual_receipts_or_acceptances_created=0,
            SD01_stop_active=True,RQ01_sent=False,RQ02_or_downstream_enabled=False),
        complete_A01_boundary=dict(source=pin(PACKET,'/complete_A01_followthrough'),exact_requirement=p['complete_A01_followthrough'],
            handoff_or_delivery_not_complete_RT01_or_A01_acceptance=True,actual_RT01_or_A01_acceptance=None),
        critical_boundaries=dict(
            local_empty_handoff_not_dispatch_receipt_intake_evidence_authority_or_acceptance=True,
            EA01_scope_EA02_R06_EA03_R08_roles_not_actual_people_or_nomination=True,
            genuine_preexisting_own_authority_not_user_docs_request_self_Git_assistant_or_future_W02_bundle_root=True,
            exact_6_sources_and_empty_5_worksheet38_descriptions_not_genuine_body_count=True,
            four_material_states_provided_not_accepted_no_SD01_lift_or_gate_decision=True,
            raw_integrity_canonical_signature_claims_and_genuine_authority_acceptance_separate_no_codec_crypto_here=True,
            trace_not_backend_durability_global_ledger_or_intrinsic_custody_no_new_input_path_service=True,
            canonical_people_aliases_competence_appointments14_exclusions_all_preparers_genuine_no_label_keys_alone=True,
            W02_eligibility_not_reverse_acceptance_future_full_roster_CE10_no_blanket_R01_R02=True,
            logical_scope_not_effective_W03_freeze_unknown_not_zero_no_predictive_hash=True,
            complete_reference_bodies_availability_provenance_custody_scope_validity_and_all_assumptions_required=True,
            no_fake_recipient_provider_body_review_gap_hash_calendar_or_global_infeasibility_from_missing_evidence=True,
            genuine_R06_primary_R08_separate_decisions_not_same_assistant_PASS_flags_or_publication=True,
            sixteen_RC_not12_A01_criteria_RT01_not_RT02_RT05_three_deliverables_three_exits_or_RQ02_enablement=True,
            changed_material_invalidates_affected_A01_A08_no_automatic_proof_approval_mapping_acceptance_transfer_or_rebind=True,
            no_contact_fetch_verification_service_enrollment_build_qualification_probe_configuration_or_product_component_execution=True,
            no_positive_crypto_signing_keygen_C_Q_root_bundle_mapping_claim_worker_receipt_or_active_authority=True,
            both_Readers_global_reference_costs_limits_guards_outputs_quotas_reserves_unchanged_no_free_input=True,
            CE12_private_deferred_no_final_E06_Q_root_claim_spawn_receipt_as_new_entry_prelaunch_condition=True,
            four_external_preclaim_then_actual_claim_construction_before_receipt_no_self_condition_or_free_retry=True,
            no_actual_intake_store_backend_or_automatic_publication_of_incoming_evidence=True,
            no_certificate_SOURCE_CAPACITY_VERIFIED_PJC115_R2_or_D5_release_from_empty_handoff=True),
        final_route_boundary=dict(source=pin(PACKET,'/final_route_boundary'),exact_requirement=p['final_route_boundary'],
            current_run_command=None,actual_final_route_or_receipt_authorized=False),
        current_effect={**p['current_effect'],'RQ01_RT01_empty_reception_package_documentary_handoff_prepared':True,
            'actual_RQ01_RT01_handoff_dispatch_delivery_or_genuine_acceptance_created':False},
        producer=dict(identity='Same Codex assistant/chat as I273/I274/A01',documentary_preparer_only=True,actor_independent=False,
            competent_primary_role_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,only_empty_documentary_handoff_published=True,
            publication_not_dispatch_receipt_genuine_authority_review_acceptance_execution_or_D5_closure=True))


def validate(d):
    assert d==build_candidate(),'Empty-package handoff differs from exact documentary reconstruction'
    p,r,a=rd(PACKET),rd(REQUEST),rd(A01)
    assert (d['lot_id'],d['request_id'],d['return_id'])==('A01','RQ01','RT01')
    assert len(d['documentary_attachment_manifest'])==6
    for row,(i,path,ptr) in zip(d['documentary_attachment_manifest'],ATTACHMENTS):assert row['id']==i and row['source']==pin(path,ptr)
    assert [x['id'] for x in d['role_handoff_cards']]==['EA01','EA02','EA03']
    assert [x['required_role'] for x in d['role_handoff_cards']]==['SCOPE_AUTHORITY','R06','R08']
    for i,row in enumerate(d['role_handoff_cards']):
        assert row['exact_subject_requirement']==fragment(row['subject_source'])==r['subject_evidence_requests'][i]
        assert fragment(row['packet_reconciliation_source'])==p['subject_reconciliation_requests'][i]
        assert len(row['mandatory_material_fields'])==7
    assert [x['name'] for x in d['worksheet_manifest']]==[x['name'] for x in p['worksheet_descriptions']]
    assert sum(x['field_description_count'] for x in d['worksheet_manifest'])==38
    assert [x['section'] for x in d['packet_requirement_routes']]==SECTIONS
    assert len(d['delivery_and_acceptance_checklist'])==12
    assert d['three_boundaries']['dispatch_to_people']['authorized_now'] is False and d['three_boundaries']['reception_review_acceptance']['authorized_now'] is False
    assert d['integrity_and_trace']['exact_integrity_requirement']==fragment(d['integrity_and_trace']['integrity_source'])==p['documentary_integrity_policy']
    assert d['integrity_and_trace']['exact_trace_requirement']==fragment(d['integrity_and_trace']['trace_source'])==p['documentary_trace_policy']
    state=d['missing_state'];assert state['actual_incoming_body_or_full_reference_inventory'] is None and state['actual_external_reference_body_count'] is None
    assert state['actual_delivery_records']==[] and type(state['actual_receipts_or_acceptances_created']) is int and state['actual_receipts_or_acceptances_created']==0
    assert state['SD01_stop_active'] is True and state['RQ01_sent'] is False and state['RQ02_or_downstream_enabled'] is False
    assert len(d['critical_boundaries'])==22 and all(v is True for v in d['critical_boundaries'].values())
    assert d['complete_A01_boundary']['exact_requirement']==fragment(d['complete_A01_boundary']['source'])==p['complete_A01_followthrough']
    pointers(d)


NEGATIVE_CASES = [
('cover_sent',('cover_note','sent'),True),('delivery_authorized',('cover_note','contact_or_delivery_authorized'),True),('recipient_invented',('cover_note','actual_coordinator_or_recipient_people'),'UNVERIFIED_TEST_LABEL'),
('outbound_receipt_created',('cover_note','actual_outbound_delivery_or_receipt'),{}),('manifest_missing',('documentary_attachment_manifest',),[]),
('manifest_as_evidence',('documentary_attachment_manifest',0,'documentary_source_only_not_genuine_authority_or_received_evidence'),False),
('role_missing',('role_handoff_cards',),[]),('R06_reassigned',('role_handoff_cards',1,'required_role'),'R01'),
('role_dispatched',('role_handoff_cards',0,'dispatched'),True),('role_received',('role_handoff_cards',0,'received'),True),('role_accepted',('role_handoff_cards',2,'accepted'),True),
('worksheet_as_body',('worksheet_manifest',0,'descriptions_not_positive_record_or_genuine_body_count'),False),('route_missing',('packet_requirement_routes',),[]),
('check_accepted',('delivery_and_acceptance_checklist',0,'accepted'),True),('check_decision_fabricated',('delivery_and_acceptance_checklist',0,'actual_own_authority_material_or_primary_separate_decision'),{}),
('publication_as_authority',('three_boundaries','documentary_publication','not_canonical_authority_or_scope_adoption'),False),
('dispatch_performed',('three_boundaries','dispatch_to_people','performed'),True),('intake_authorized',('three_boundaries','reception_review_acceptance','authorized_now'),True),
('inventory_fabricated',('future_return_routes','available_material','actual_received_inventory'),[]),('gap_as_authority',('future_return_routes','missing_or_changed_material','actual_gap_or_new_work_authority'),{}),
('digest_fabricated',('integrity_and_trace','actual_raw_or_canonical_evidence_digest_or_signature'),'UNVERIFIED_TEST_LABEL'),
('auto_publish',('integrity_and_trace','no_incoming_evidence_personal_data_or_claim_automatically_committed_pushed_published'),False),
('body_count_zero',('missing_state','actual_external_reference_body_count'),0),('delivery_created',('missing_state','actual_delivery_records'),[{}]),
('SD01_bypass',('missing_state','SD01_stop_active'),False),('RQ02_enabled',('missing_state','RQ02_or_downstream_enabled'),True),
('RT01_as_A01',('complete_A01_boundary','handoff_or_delivery_not_complete_RT01_or_A01_acceptance'),False),
('forecast_authority',('critical_boundaries','genuine_preexisting_own_authority_not_user_docs_request_self_Git_assistant_or_future_W02_bundle_root'),False),
('W02_backward',('critical_boundaries','W02_eligibility_not_reverse_acceptance_future_full_roster_CE10_no_blanket_R01_R02'),False),
('integrity_as_authority',('critical_boundaries','raw_integrity_canonical_signature_claims_and_genuine_authority_acceptance_separate_no_codec_crypto_here'),False),
('trace_as_ledger',('critical_boundaries','trace_not_backend_durability_global_ledger_or_intrinsic_custody_no_new_input_path_service'),False),
('scope_as_freeze',('critical_boundaries','logical_scope_not_effective_W03_freeze_unknown_not_zero_no_predictive_hash'),False),
('scope_transfer',('critical_boundaries','changed_material_invalidates_affected_A01_A08_no_automatic_proof_approval_mapping_acceptance_transfer_or_rebind'),False),
('free_cost_or_quota',('critical_boundaries','both_Readers_global_reference_costs_limits_guards_outputs_quotas_reserves_unchanged_no_free_input'),False),
('receipt_precondition',('critical_boundaries','CE12_private_deferred_no_final_E06_Q_root_claim_spawn_receipt_as_new_entry_prelaunch_condition'),False),
('claim_self_condition',('critical_boundaries','four_external_preclaim_then_actual_claim_construction_before_receipt_no_self_condition_or_free_retry'),False),
('run_command',('final_route_boundary','current_run_command'),'UNVERIFIED_TEST_LABEL'),('final_authorized',('final_route_boundary','actual_final_route_or_receipt_authorized'),True),
('A01_accepted',('current_effect','A01_accepted'),True),('D5_closed',('current_effect','D5_closed'),True),('assistant_independent',('producer','actor_independent'),True),
('publication_as_dispatch',('publication','publication_not_dispatch_receipt_genuine_authority_review_acceptance_execution_or_D5_closure'),False)]


def rejections(d):
    results=[]
    for name,path,value in NEGATIVE_CASES:
        mutant=copy.deepcopy(d);node=mutant
        for key in path[:-1]:node=node[key]
        node[path[-1]]=value
        try:validate(mutant)
        except AssertionError:results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:raise AssertionError(name)
    return results


def build_review():
    d=rd(SUBJECT);validate(d)
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));exists=Path.exists
    rec=previous['reconstruct']();assert rec==rd(PRIOR_RECON)
    review=previous['build_review'](rec);assert review==rd(PRIOR_REVIEW) and Path.exists is exists
    return dict(schema='d5.i275-preparation-review.v1',increment='I275',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,subject=pin(SUBJECT),findings=[],
        counts=dict(input_pins=1172,documentary_attachments=6,role_cards=3,subject_material_groups=7,worksheet_groups=5,worksheet_field_descriptions=38,
            packet_section_routes=len(SECTIONS),handoff_conditions=12,material_states=4,separation_requirements=14,RC_rows=16,full_A01_criteria=12,A01_deliverables=3,A01_exits=3,
            remaining_A01_returns=4,critical_boundaries=22,documentary_rejections=len(NEGATIVE_CASES),preserved_published_files=864,new_files=5,
            actual_dispatches_or_receipts_or_acceptances_created=0,actual_received_bodies=0,prelaunch_gates_closed=0,resource_obligations_closed=0),rejection_checks=rejections(d),
        source_reconstruction=dict(I273_packet_I271_request_A01_requirements_exact=True,I274_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        current_effect=d['current_effect'],limitations=['Local handoff draft and six documentary attachments are not actual dispatch,receipt,incoming evidence,nomination,authority or acceptance. Canonical people/channel/contact/delivery authority remain unspecified,SD01 active,RQ01 unsent.',
            'Publishing empty documents is authorized separately from any future dispatch to people and genuine reception/review/acceptance. No future actor or action is authorized by this index.',
            'Packet remains empty,external reference/body inventory unknown. Byte integrity is not authority,canonical/signature claims not verification,and trace policy not backend/durable/global-ledger proof.',
            'RT01/handoff/receipt cannot complete RT02-RT05/A01 or enable RQ02.30 gates,E01-E05/PJC115-R2/D5 remain open;CE12/final route deferred,no execution,quotas/reserves/active binding/authority/destination/certificate change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I275-audit.py',expected_result=STATUS,over400_lines=True,
            reason='One local empty-packet handoff with role cards,source manifest,conditions,pins,rejection checks and preservation; overage declared,no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage/graph checks and in-memory mutations only; no target import,compile,discovery,tests,execution,build,benchmark,codec,crypto,signing,keygen,enrollment,contacts,provision,configuration or platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes.'),
        provenance=d['producer'],publication=d['publication'])


def main():
    d=rd(SUBJECT);validate(d);verify_blobs(d['input_pins'])
    review=build_review();assert review==rd(PREP)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published859'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)};assert len(preserved)==864
    seal=rd(SEAL);assert seal['schema']=='d5.i275-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published864']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==d['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,**review['counts'],D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
