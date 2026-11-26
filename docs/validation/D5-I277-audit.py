#!/usr/bin/env python3
"""I277 documentary dispatch-authorization request; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '2b670b8155f378962ec55721d5000388c7b47956'
DATE = '2026-11-26'
A01 = P+'D5-I251-A01-RQ01-ENTRY-AUTHORITY-SCOPE-CANDIDATE.json'
REQUEST = P+'D5-I271-RQ01-RT01-ENTRY-AUTHORITY-REQUEST-CANDIDATE.json'
PACKET = P+'D5-I273-RQ01-RT01-EVIDENCE-RECEPTION-PACKAGE-CANDIDATE.json'
HANDOFF = P+'D5-I275-RQ01-RT01-RECEPTION-PACKAGE-HANDOFF-CANDIDATE.json'
CONSOLIDATED = P+'D5-I269-A01-A08-CONSOLIDATED-HANDOFF-CANDIDATE.json'
PRIOR_RECON = P+'D5-I276-I275-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I276-I275-documentary-review.json'
PRIOR_AUDIT = P+'D5-I276-audit.py'
PRIOR_SEAL = P+'D5-I276-integrity.json'
PRIOR_DOC = 'docs/design/D5-I276-I275-RECEPTION-HANDOFF-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I277-RQ01-RT01-DELIVERY-AUTHORIZATION-REQUEST-CANDIDATE.json'
EXTRACT = P+'D5-I277-CONSOLIDATED-ENTRY-DELIVERY-EXTRACT.json'
PREP = P+'D5-I277-preparation-review.json'
AUDIT = P+'D5-I277-audit.py'
SEAL = P+'D5-I277-integrity.json'
DOC = 'docs/design/D5-I277-RQ01-RT01-DELIVERY-AUTHORIZATION-REQUEST.md'
FILES = {SUBJECT,EXTRACT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_DELIVERY_AUTHORIZATION_REQUEST_PREPARED_EXACT_DOCUMENTS_BOUND_RECIPIENTS_AUTHORITY_MISSING_NOT_GRANTED_NOT_SENT_NOT_ADMITTED'


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


MESSAGE = ('RQ01/RT01 — Paquete documental vacío para revisión EA01/R06/R08\n\n'
'Esta es una propuesta de comunicación documental, sin designación de personas o emisión de autoridad. '
'El kit I273 y el handoff I275 permanecen vacíos y sin aceptación. Se adjuntan seis fuentes documentales exactas. '
'Para RT01 se solicita únicamente material genuino ya disponible con autoridad propia sobre EA01 scope authority, EA02/R06 y EA03/R08: '
'humano canónico y aliases, emisor/delegación preexistente independiente, competencia/appointment, scope/acciones permitidas-denegadas, '
'vigencia/currentness/revocación/independencia, cuerpos completos y referencias disponibles con locator/bytes/digest/autor/provider/custodia. '
'Declarar faltantes y dependientes sin generar sustitutos. Hash/documento/recibo no prueba autoridad o aceptación; separar integridad bruta de claims canónicos/firma. '
'No se solicita implementación, build, cualificación, medición, firma/keygen/crypto, enrollment, contacto a terceros, configuración o ejecución. '
'W02 aporta criterios de elegibilidad, sin aceptación previa/roster final/CE10 como condición de A01. '
'RT01 no reemplaza RT02–RT05 y decisiones propias de A01 ni habilita RQ02. SD01/no admisión se mantienen y CE12/ruta final siguen aparte. '
'Este contenido sólo podrá enviarse si una autoridad genuina identifica destinatarios/canal/operador y autoriza exactamente este alcance.\n')
BINDINGS = [
('issuer','Humano/emisor y cuerpo de autoridad/delegación preexistente auténtica,scope/competencia/vigencia y facultad propia de autorizar contacto documental.'),
('operator','Operador accountable identificado y elegible bajo esa facultad,con ámbito de entrega documental exclusivamente.'),
('recipients','Mapping exacto EA01/EA02-R06/EA03-R08 a destinatarios canónicos/aliases y evidencia de legitimidad;sin crear appointment o inferir tres humanos distintos.'),
('channel','Canal y endpoints únicos exactos aprobados,custodio,provenance y facultad de usarlos;sin discovery/contacto/fetch para completarlos desde esta solicitud.'),
('payload','Texto UTF8 y seis archivos documentales por ID/locator/bytes/rawSHA256;extracto I269 exacto,serializador documental declarado,sin claims JCS/firma o adjuntos adicionales.'),
('action','Una única tentativa de entrega documental por endpoint único explícitamente aprobado,lista finita aprobada;sin followups/reintentos/reenvío automático ni autoridad para otros destinatarios.'),
('validity','Ventana de autorización,currentness/revocación y límites de scope identificados por autoridad propia,sin inventar fecha/plazo o usar host date como prueba.'),
('denied_actions','Excluir nominación/enrollment,adopción scope/autoridad EA,recepción operacional/verificación/aceptación,producto/componentes/crypto/probes/configuración/cuotas y publicación automática de respuestas.'),
('own_decision','Cuerpo genuino de decisión aceptar alcance exacto/rechazar/aplazar con motivo,locators/bytes/digest/provenance/autoridad,sin booleano o PASS del asistente como sustituto.'),
('change_control','Cambio de mensaje,archivo,extracto,destinatario,canal,operador,emisor,scope/validez invalida la autorización afectada y exige decisión propia nueva antes de actuar.'),
('outcome_trace','Si una entrega futura se autoriza y realiza,anotar sólo outcome real bajo autoridad propia;acuse/transporte no autoridad EA,autenticidad,recepción operacional o aceptación RT01/A01.'),
('missing_bindings','Cualquier binding/autoridad/cuerpo desconocido mantiene aplazado/no concedido/no enviado,SD01/no admisión;no aprobar huecos,proporcionar facultad genérica o inventar persona/canal/plazo.')]


def extract_bytes():
    return (json.dumps(rd(CONSOLIDATED)['first_material_request'],indent=2,ensure_ascii=False)+'\n').encode('utf-8')


def build_candidate():
    h,r,p=rd(HANDOFF),rd(REQUEST),rd(PACKET)
    pins={**rd(PRIOR_RECON)['input_pins'],**{s:sha(s) for s in PRIOR_FILES}};assert len(pins)==1182
    assert (ROOT/EXTRACT).read_bytes()==extract_bytes()
    return dict(schema='d5.i277-dispatch-authorization-request.v1',increment='I277',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        authorization_request_id='PGE251-RQ01-RT01-DELIVERY-AUTHORIZATION-CANDIDATE-01',lot_id='A01',request_id='RQ01',return_id='RT01',
        kind='LOCAL_UNSENT_REQUEST_FOR_EXACT_FUTURE_DOCUMENTARY_DELIVERY_AUTHORITY_NOT_A_GRANT_DISPATCH_NOMINATION_OR_ACCEPTANCE',
        status='REQUEST_PREPARED_EXACT_PAYLOAD_BOUND_CANONICAL_PEOPLE_CHANNEL_ISSUER_OPERATOR_AUTHORITY_MISSING_NOT_GRANTED_NOT_SENT_NOT_ADMITTED',input_pins=pins,
        handoff_source=pin(HANDOFF),latest_review=pin(PRIOR_REVIEW),dispatch_boundary_source=pin(HANDOFF,'/three_boundaries/dispatch_to_people'),
        exact_dispatch_boundary=h['three_boundaries']['dispatch_to_people'],
        request_cover=dict(subject='Solicitud de autorización limitada de entrega — handoff RQ01/RT01 EA01/R06/R08',
            intended_authorizer_role_only='Autoridad humana preexistente con facultad propia de autorizar esta entrega documental exacta;sin designar',
            text='Se prepara para revisión local una solicitud de decisión sobre una futura entrega documental exacta,con texto y seis adjuntos fijados abajo. No se pide aprobar identidades/canales/operador/emisor/validez todavía desconocidos:deben aportarse y vincularse genuinamente antes de una decisión positiva. La autoridad propia de contacto/entrega debe ser preexistente e independiente de esta petición/Git/asistente. No confundir permiso limitado de comunicación con autoridad canónica EA01/R06/R08,adopción de scope o aceptación de evidencia. Hoy sólo se preparan/auditan/publican documentos vacíos:la solicitud no se envía,autoriza o ejecuta. Si falta cualquier binding o cuerpo,aplazar/rechazar con gap sin fabricar sustitutos,SD01/no admisión.',
            is_draft_only=True,sent=False,actual_authorizer_person_or_delegation_body=None,actual_recipient_or_contact_channel=None,actual_request_delivery_or_acknowledgment=None),
        exact_proposed_message=dict(text=MESSAGE,encoding='UTF-8',line_endings='LF',normalization='NONE',raw_byte_count=len(MESSAGE.encode('utf-8')),
            raw_sha256=hashlib.sha256(MESSAGE.encode('utf-8')).hexdigest(),documentary_bytes_not_JCS_signature_or_genuine_authority=True,actual_sent=False),
        exact_proposed_attachments=[dict(id=x['id'],original_handoff_requirement_source=pin(HANDOFF,'/documentary_attachment_manifest/'+str(i)),
            original_source=x['source'],delivery_file=(EXTRACT if x['id']=='CONSOLIDATED_ENTRY' else x['source']['path']),
            raw_byte_count=(ROOT/(EXTRACT if x['id']=='CONSOLIDATED_ENTRY' else x['source']['path'])).stat().st_size,
            raw_sha256=sha(EXTRACT if x['id']=='CONSOLIDATED_ENTRY' else x['source']['path']),
            documentary_content_not_actual_EA_authority_or_received_evidence=True,actual_dispatched=False)
            for i,x in enumerate(h['documentary_attachment_manifest'])],
        extract_binding=dict(original_source=pin(CONSOLIDATED,'/first_material_request'),delivery_file=EXTRACT,
            serializer='Python stdlib json.dumps(indent=2, ensure_ascii=False) + LF; UTF-8; source insertion order retained; documentary JSON, not JCS',
            exact_selected_fragment_only_no_whole_consolidated_dossier=True,raw_byte_count=len(extract_bytes()),raw_sha256=sha(EXTRACT),
            metadata_export_not_positive_protocol_codec_crypto_or_actual_evidence=True),
        recipient_binding_requests=[dict(id=x['id'],required_role=x['required_role'],source=pin(HANDOFF,'/role_handoff_cards/'+str(i)),
            exact_role_requirement=x,actual_canonical_person_aliases_or_eligibility_body=None,actual_approved_endpoint_or_channel=None,
            actual_own_contact_delivery_scope_or_provenance=None,appointed=False,authorized_for_delivery=False)
            for i,x in enumerate(h['role_handoff_cards'])],
        authorization_binding_requirements=[dict(id='DB%02d'%(i+1),topic=topic,requirement=text,
            actual_binding_or_preexisting_own_authority_or_reasoned_decision=None,
            disposition='MISSING_NOT_REVIEWED_NOT_GRANTED',satisfied=False) for i,(topic,text) in enumerate(BINDINGS)],
        proposed_action_limits=dict(action='DELIVER_EXACT_EMPTY_DOCUMENTARY_HANDOFF_ONLY',max_attempts_per_exact_approved_unique_endpoint=1,
            approved_endpoint_list_must_be_finite_and_fully_bound=True,actual_unique_endpoint_list=None,actual_issuer_operator_scope_validity_or_contact_authority=None,
            no_automatic_followup_retry_forwarding_additional_recipient_payload_channel_or_response_fetch=True,
            uncertain_or_partial_transport_outcome_requires_separate_exact_decision_before_any_retry=True,
            contact_permission_not_enrollment_scope_adoption_EA_authority_operational_intake_verification_or_acceptance=True,
            authorized_now=False,performed=False),
        future_decision_boundary=dict(allowed_reasoned_decision_kinds=['AUTHORIZE_EXACT_FULLY_BOUND_DOCUMENTARY_DELIVERY','REJECT_WITH_TRACEABLE_REASON','DEFER_MISSING_BINDINGS'],
            genuine_preexisting_competent_authority_body_and_all_bindings_before_positive_decision=True,
            no_blanket_authorization_or_conditional_approval_of_unknown_people_channel_scope=True,
            user_docs_commit_push_request_not_canonical_contact_or_EA_role_authority=True,
            description_not_grant_or_actual_request_to_others=True,actual_issuer_or_decision_body=None,actual_positive_authorization=False),
        inherited_boundaries=[dict(section=s,source=pin(HANDOFF,'/'+s),exact_requirement=h[s]) for s in [
            'three_boundaries','future_return_routes','integrity_and_trace','missing_state','complete_A01_boundary','critical_boundaries','final_route_boundary']],
        missing_state=dict(actual_named_issuer_operator_recipients_channel_endpoints_or_validity=None,actual_genuine_authorization_body_or_contact_authority=None,
            actual_request_dispatch_handoff_delivery_or_receipt=None,actual_received_evidence_or_primary_R06_separate_R08_decisions=None,
            actual_external_body_inventory_or_count=None,actual_authorizations_granted=0,actual_messages_sent=0,actual_genuine_acceptances_created=0,
            SD01_stop_active=True,RQ01_sent=False,RQ02_or_downstream_enabled=False),
        critical_boundaries=dict(
            exact_local_request_not_grant_dispatch_nomination_receipt_or_acceptance=True,
            genuine_preexisting_own_delivery_authority_independent_user_docs_permission_Git_assistant_self_or_forecast=True,
            unknown_issuer_operator_canonical_recipients_channel_endpoints_validity_not_approved_or_fabricated=True,
            exact_UTF8_message_and6_documentary_files_raw_bytes_hashes_not_authority_evidence_or_signature=True,
            selected_I269_fragment_export_ordinary_documentary_JSON_not_JCS_no_whole_dossier_or_hidden_extra=True,
            finite_exact_approved_unique_endpoints_single_attempt_each_no_automatic_followup_retry_forward_or_fetch=True,
            delivery_permission_not_EA_authority_scope_adoption_enrollment_operational_intake_verification_or_acceptance=True,
            EA01_scope_EA02_R06_EA03_R08_own_genuine_authority_eligibility14_exclusions_all_preparers_still_required=True,
            W02_eligibility_not_reverse_acceptance_future_roster_CE10_no_blanket_R01_R02=True,
            raw_integrity_canonical_signature_claims_and_authentic_authority_acceptance_separate_no_codec_crypto_here=True,
            trace_not_backend_durability_global_ledger_or_intrinsic_custody_no_new_runtime_input_path_service=True,
            no_incoming_evidence_personal_data_or_claim_auto_published_no_unknown_zero_or_predictive_hash=True,
            complete_reference_bodies_availability_provenance_scope_validity_assumptions_and_real_R06_R08_decisions_required=True,
            RT01_delivery_not_RT02_RT05_12_A01_criteria_three_deliverables_three_exits_or_RQ02_enablement=True,
            changed_payload_actor_channel_scope_validity_invalidates_affected_grant_no_proof_approval_acceptance_transfer=True,
            gaps_no_fake_authority_person_provider_calendar_hash_or_global_infeasibility_from_missing_evidence=True,
            no_actual_contact_fetch_enrollment_build_qualification_probe_configuration_product_component_execution=True,
            no_positive_crypto_signing_keygen_C_Q_root_bundle_mapping_claim_worker_receipt_or_active_authority=True,
            both_Readers_global_reference_costs_limits_guards_outputs_quotas_reserves_unchanged_no_free_input=True,
            CE12_private_deferred_no_final_E06_Q_root_claim_spawn_receipt_as_new_entry_prelaunch_condition=True,
            four_external_preclaim_then_actual_claim_construction_before_receipt_no_self_condition_or_free_retry=True,
            no_certificate_SOURCE_CAPACITY_VERIFIED_PJC115_R2_or_D5_release_from_request_PASS_publication_or_future_delivery=True),
        final_route_boundary=dict(source=pin(HANDOFF,'/final_route_boundary'),exact_requirement=h['final_route_boundary'],current_run_command=None,actual_final_route_or_receipt_authorized=False),
        current_effect={**h['current_effect'],'RQ01_RT01_documentary_delivery_authorization_request_prepared':True,
            'actual_delivery_authority_request_sent_grant_dispatch_or_genuine_acceptance_created':False},
        producer=dict(identity='Same Codex assistant/chat as I275/I276/A01',documentary_preparer_only=True,actor_independent=False,
            competent_authorizing_or_primary_role_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,only_empty_documentary_request_and_selected_existing_documentary_extract_published=True,
            publication_not_delivery_authorization_contact_dispatch_receipt_genuine_EA_authority_acceptance_execution_or_D5_closure=True))


def validate(d):
    assert d==build_candidate(),'Dispatch authorization request differs from exact documentary reconstruction'
    h=rd(HANDOFF)
    assert (d['lot_id'],d['request_id'],d['return_id'])==('A01','RQ01','RT01')
    assert d['exact_dispatch_boundary']==fragment(d['dispatch_boundary_source'])==h['three_boundaries']['dispatch_to_people']
    message=d['exact_proposed_message'];assert message['text'].encode('utf-8')==MESSAGE.encode('utf-8')
    assert message['raw_byte_count']==len(MESSAGE.encode('utf-8')) and message['raw_sha256']==hashlib.sha256(MESSAGE.encode('utf-8')).hexdigest()
    rows=d['exact_proposed_attachments'];assert [x['id'] for x in rows]==[x['id'] for x in h['documentary_attachment_manifest']] and len(rows)==6
    for i,row in enumerate(rows):
        src=h['documentary_attachment_manifest'][i];assert fragment(row['original_handoff_requirement_source'])==src and row['original_source']==src['source']
        assert row['raw_sha256']==sha(row['delivery_file']) and row['raw_byte_count']==(ROOT/row['delivery_file']).stat().st_size
    assert (ROOT/EXTRACT).read_bytes()==extract_bytes() and rd(EXTRACT)==fragment(d['extract_binding']['original_source'])
    assert len(d['recipient_binding_requests'])==3 and [r['required_role'] for r in d['recipient_binding_requests']]==['SCOPE_AUTHORITY','R06','R08']
    for i,row in enumerate(d['recipient_binding_requests']):assert row['exact_role_requirement']==fragment(row['source'])==h['role_handoff_cards'][i]
    assert len(d['authorization_binding_requirements'])==12 and [r['topic'] for r in d['authorization_binding_requirements']]==[x[0] for x in BINDINGS]
    assert d['proposed_action_limits']['max_attempts_per_exact_approved_unique_endpoint']==1 and d['proposed_action_limits']['authorized_now'] is False
    assert len(d['inherited_boundaries'])==7 and len(d['critical_boundaries'])==22 and all(v is True for v in d['critical_boundaries'].values())
    state=d['missing_state'];assert state['actual_external_body_inventory_or_count'] is None and all(type(state[k]) is int and state[k]==0 for k in ['actual_authorizations_granted','actual_messages_sent','actual_genuine_acceptances_created'])
    pointers(d)


NEGATIVE_CASES = [
('request_sent',('request_cover','sent'),True),('authorizer_fabricated',('request_cover','actual_authorizer_person_or_delegation_body'),'UNVERIFIED_TEST_LABEL'),
('message_changed',('exact_proposed_message','text'),'UNVERIFIED_TEST_LABEL'),('message_hash_changed',('exact_proposed_message','raw_sha256'),'0'*64),
('attachment_missing',('exact_proposed_attachments',),[]),('attachment_hash_changed',('exact_proposed_attachments',0,'raw_sha256'),'0'*64),
('whole_dossier_allowed',('extract_binding','exact_selected_fragment_only_no_whole_consolidated_dossier'),False),('extract_as_JCS',('extract_binding','metadata_export_not_positive_protocol_codec_crypto_or_actual_evidence'),False),
('recipient_missing',('recipient_binding_requests',),[]),('recipient_fabricated',('recipient_binding_requests',0,'actual_canonical_person_aliases_or_eligibility_body'),'UNVERIFIED_TEST_LABEL'),
('endpoint_fabricated',('recipient_binding_requests',0,'actual_approved_endpoint_or_channel'),'UNVERIFIED_TEST_LABEL'),('nomination',('recipient_binding_requests',0,'appointed'),True),
('delivery_authorized',('recipient_binding_requests',1,'authorized_for_delivery'),True),('binding_missing',('authorization_binding_requirements',),[]),
('binding_satisfied',('authorization_binding_requirements',0,'satisfied'),True),('authority_decision_fabricated',('authorization_binding_requirements',0,'actual_binding_or_preexisting_own_authority_or_reasoned_decision'),{}),
('attempts_increased',('proposed_action_limits','max_attempts_per_exact_approved_unique_endpoint'),2),('unbounded_endpoints',('proposed_action_limits','approved_endpoint_list_must_be_finite_and_fully_bound'),False),
('auto_retry',('proposed_action_limits','no_automatic_followup_retry_forwarding_additional_recipient_payload_channel_or_response_fetch'),False),
('contact_as_EA_authority',('proposed_action_limits','contact_permission_not_enrollment_scope_adoption_EA_authority_operational_intake_verification_or_acceptance'),False),
('dispatch_performed',('proposed_action_limits','performed'),True),('blanket_grant',('future_decision_boundary','no_blanket_authorization_or_conditional_approval_of_unknown_people_channel_scope'),False),
('positive_grant',('future_decision_boundary','actual_positive_authorization'),True),('issuer_decision_created',('future_decision_boundary','actual_issuer_or_decision_body'),{}),
('boundary_missing',('inherited_boundaries',),[]),('authorization_count',('missing_state','actual_authorizations_granted'),1),('message_count',('missing_state','actual_messages_sent'),1),
('external_count_zero',('missing_state','actual_external_body_inventory_or_count'),0),('SD01_bypass',('missing_state','SD01_stop_active'),False),('RQ02_enabled',('missing_state','RQ02_or_downstream_enabled'),True),
('forecast_authority',('critical_boundaries','genuine_preexisting_own_delivery_authority_independent_user_docs_permission_Git_assistant_self_or_forecast'),False),
('W02_backward',('critical_boundaries','W02_eligibility_not_reverse_acceptance_future_roster_CE10_no_blanket_R01_R02'),False),
('integrity_as_acceptance',('critical_boundaries','raw_integrity_canonical_signature_claims_and_authentic_authority_acceptance_separate_no_codec_crypto_here'),False),
('auto_publish_evidence',('critical_boundaries','no_incoming_evidence_personal_data_or_claim_auto_published_no_unknown_zero_or_predictive_hash'),False),
('RT01_as_A01',('critical_boundaries','RT01_delivery_not_RT02_RT05_12_A01_criteria_three_deliverables_three_exits_or_RQ02_enablement'),False),
('scope_transfer',('critical_boundaries','changed_payload_actor_channel_scope_validity_invalidates_affected_grant_no_proof_approval_acceptance_transfer'),False),
('free_cost_quota',('critical_boundaries','both_Readers_global_reference_costs_limits_guards_outputs_quotas_reserves_unchanged_no_free_input'),False),
('receipt_precondition',('critical_boundaries','CE12_private_deferred_no_final_E06_Q_root_claim_spawn_receipt_as_new_entry_prelaunch_condition'),False),
('claim_self_condition',('critical_boundaries','four_external_preclaim_then_actual_claim_construction_before_receipt_no_self_condition_or_free_retry'),False),
('run_command',('final_route_boundary','current_run_command'),'UNVERIFIED_TEST_LABEL'),('final_authorized',('final_route_boundary','actual_final_route_or_receipt_authorized'),True),
('A01_accepted',('current_effect','A01_accepted'),True),('D5_closed',('current_effect','D5_closed'),True),('assistant_authorizes',('producer','competent_authorizing_or_primary_role_review'),True),
('publication_as_grant',('publication','publication_not_delivery_authorization_contact_dispatch_receipt_genuine_EA_authority_acceptance_execution_or_D5_closure'),False)]


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
    return dict(schema='d5.i277-preparation-review.v1',increment='I277',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,subject=pin(SUBJECT),findings=[],
        counts=dict(input_pins=1182,proposed_messages=1,exact_documentary_attachments=6,selected_fragment_exports=1,recipient_role_bindings=3,authorization_binding_requirements=12,
            max_attempts_per_exact_approved_unique_endpoint=1,inherited_boundaries=7,critical_boundaries=22,documentary_rejections=len(NEGATIVE_CASES),
            preserved_published_files=874,new_files=6,actual_messages_sent=0,actual_authorizations_granted=0,actual_genuine_acceptances=0,prelaunch_gates_closed=0,resource_obligations_closed=0),
        rejection_checks=rejections(d),source_reconstruction=dict(I275_handoff_exact_bytes_and_selected_fragment_bound=True,I276_reconstruction_and_review_reproduced=True,
            prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),current_effect=d['current_effect'],
        limitations=['Request is local and unsent,not a grant. Issuer/delegation,operator,canonical people/channel/endpoints/validity and genuine decision remain missing;unknown bindings cannot receive blanket or conditional approval.',
            'Exact UTF8 text and6 document files are bound by raw bytes/hash;I269 selected fragment exported as ordinary documentary JSON,not JCS,signature,authority proof or positive protocol record.',
            'Future exact delivery permission cannot create EA01/R06/R08 canonical authority,nominate/enroll,adopt scope,receive/verify/accept evidence or authorize product. No sending,contacts or messages to others done.',
            'SD01/no admission remains;RT01 not full A01 or RQ02 enablement.30 gates,E01-E05/PJC115-R2/D5 open,CE12/final route separate,deferred. No quota/reserve/binding/authority/destination/certificate change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I277-audit.py',expected_result=STATUS,over400_lines=True,
            reason='One concrete delivery-authorization request with fixed proposed message,6 attachment byte bindings,one exact documentary fragment export,pins/rejections/preservation; overage declared,no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/byte-export/coverage/graph checks and in-memory mutations only; no target import,compile,discovery,tests,execution,build,benchmark,positive protocol codec,crypto,signing,keygen,enrollment,contacts,provision,configuration or platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes.'),
        provenance=d['producer'],publication=d['publication'])


def main():
    d=rd(SUBJECT);validate(d);verify_blobs(d['input_pins'])
    review=build_review();assert review==rd(PREP)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published869'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)};assert len(preserved)==874
    seal=rd(SEAL);assert seal['schema']=='d5.i277-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published874']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==d['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,**review['counts'],D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
