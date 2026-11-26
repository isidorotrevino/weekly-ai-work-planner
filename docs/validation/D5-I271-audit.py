#!/usr/bin/env python3
"""I271 focused RQ01/RT01 documentary request; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'ade424fedbb34b4c73e5ae51e7d699624633bb1a'
DATE = '2026-11-26'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
A01 = P+'D5-I251-A01-RQ01-ENTRY-AUTHORITY-SCOPE-CANDIDATE.json'
HANDOFF = P+'D5-I269-A01-A08-CONSOLIDATED-HANDOFF-CANDIDATE.json'
PRIOR_RECON = P+'D5-I270-I269-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I270-I269-documentary-review.json'
PRIOR_AUDIT = P+'D5-I270-audit.py'
PRIOR_SEAL = P+'D5-I270-integrity.json'
PRIOR_DOC = 'docs/design/D5-I270-I269-CONSOLIDATED-HANDOFF-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I271-RQ01-RT01-ENTRY-AUTHORITY-REQUEST-CANDIDATE.json'
PREP = P+'D5-I271-preparation-review.json'
AUDIT = P+'D5-I271-audit.py'
SEAL = P+'D5-I271-integrity.json'
DOC = 'docs/design/D5-I271-RQ01-RT01-ENTRY-AUTHORITY-REQUEST.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_RQ01_RT01_REQUEST_PREPARED_PREEXISTING_AUTHORITY_AND_GENUINE_ELIGIBILITY_MISSING_SD01_ACTIVE_NOT_ADMITTED'


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


BOUNDARIES = 'entry_gate eligibility_boundary known_vs_missing authority_by_action intake_sequence missing_or_rejected_material preserved_cost_scope_and_limits handoff change_control'.split()
SECTIONS = [
('availability','Cuerpos y disponibilidad',
 'Por EA01/EA02/EA03 identificar cada cuerpo genuino completo ya disponible,locator inmutable/bytes/digest/autor/provider/custodia y referencias dependientes. No entregar sólo plantillas,links sin cuerpo,hashes o flags como prueba de autoridad;lo ausente queda declarado,no generado.'),
('authority_chain','Autoridad preexistente e independiente',
 'Aportar emisor,organización/competencia y cadena de delegación/provenance auténtica con alcance/vigencia que permita a EA01 decidir este scope lógico y a R06/R08 revisar/aceptar bajo autoridad propia. Debe existir independientemente de esta solicitud/asistente/Git y de futuros appointments W02/bundle/root;autoatestación o claves/firmas incluidas solas no fundan autoridad.'),
('identity_eligibility','Humanos canónicos y elegibilidad',
 'Identificar humanos canónicos/aliases completos,competencia y appointments de EA01/R06/R08,claves/purpose/custodia cuando aplicables y evidencia genuina de exclusiones/independencia. Mantener14 reglas y todos los preparadores del scope evaluado,no sólo source authors;no inferir personas distintas de strings/keys. W02 aporta criterios,no dependencia de W02 aceptado ni roster final futuro/CE10 como requisito previo. No prohibición general R01/R02 ni preaprobación de futuros autores.'),
('scope_and_currentness','Ámbito,acciones y vigencia',
 'Precisar target lógico PGO181 candidato02/PFC126-CANDIDATE-03/I122,facultades de scope/documentación/review/aceptación y acciones denegadas;vigencia/currentness/revocación y dependientes de cada autoridad/cuerpo. Hechos efectivos desconocidos siguen null,no hashes predictivos/freezes W03 o medidas nuevas. Aprobar scope no autoriza implementación/build/cualificación/medición/firma/contacto/provisión/configuración/ejecución/cuotas.'),
('review_provenance','Provenance y decisiones propias',
 'Aportar evidencia preexistente de elegibilidad/autoridad primaria R06 y separada R08 y,si ya existen válidamente,los cuerpos propios de reviews/decisiones con locator/bytes/digest/scope/validez y razones. La preparación no nomina ni produce esas decisiones;RT05 conserva la review/decisión genuina de todo A01. Un RT01 recibido/aceptado sólo cubre su ámbito,no acepta A01 ni habilita RQ02.'),
('gaps','Faltantes,cambios y autoridad separada',
 'Declarar por sujeto/referencia todo faltante/rechazado/incompatible,scope/dependientes y trabajo/autoridad exactos separados necesarios. Mantener SD01/no admisión y unknown no cero,sin inventar humano/proveedor/plazo/hash/documento positivo o inviabilidad global. Cambios invalidan afectados antes de avanzar,sin transferir aceptaciones;no contactar/fetch/servicios de verificación,emitir/fabricar autoridad,firmar/keygen/crypto/enrolar/configurar/probar/ejecutar para completar esta solicitud.')]
CRITERIA = [
('scope','RQ01/RT01 conserva requisito exacto y contrato universal,A01 completo no reemplazado.'),
('entry_authority','EA01/EA02/EA03 y autoridad previa propia auténtica,independiente de solicitud/Git/asistente/futuros W02/bundle/root.'),
('bodies','Cuerpos disponibles completos y cierre real de referencias,locator/bytes/digest/autor/provider/custodia,sin plantilla/hash/flag como verdad.'),
('canonical_people','Humanos canónicos/aliases,competencia y appointments genuinos,keys/purpose/custodia aplicables,sin nominalismo o persona inventada.'),
('independence','14 exclusiones/preparadores completos conservados y aplicabilidad auténtica,no auto-review R06/R08 o asistente como independiente.'),
('no_reverse_dependency','Criterios W02 no W02 aceptado/roster final futuro/CE10 como nueva dependencia de A01,no blanket R01/R02.'),
('logical_scope','Scope lógico/acciones exactos y límites vigentes,no freeze efectivo o hashes W03 inventados ni autoridad operativa implícita.'),
('validity','Emisor/delegación/scope/vigencia/currentness/revocación/dependencias con evidencia propia,no host date o firma sola.'),
('delivery','Ocho campos universales y siete grupos por sujeto íntegros,todas las referencias/supuestos visibles,unknown no cero.'),
('real_reviews','Autoridad/eligibilidad R06/R08 genuinas y decisiones propias trazables cuando existan,no JSON/commit/asistente como review real.'),
('partial_not_complete','RT01 no RT02-RT05;doce criterios,tres entregables/tres salidas y aceptación completa A01 necesarios antes de considerar RQ02.'),
('gaps','Gaps con scope/dependientes/autoridad separada mantienen SD01,no inferencia de inexistencia global,inviabilidad o duración.'),
('invalidation','Cambio autor/body/source/runtime/scope/epoch/key/policy invalida afectados,sin proof/approval/acceptance transfer o rebind activo.'),
('no_send','Borrador sin personas/canales/autoridad contacto/delivery,sin envío/nominación/fetch/servicios de verificación.'),
('no_operations','Sin producto/componentes/crypto/signing/keygen/enrollment/snapshots/provision/config/probes/cuotas/reservas o cambio activo.'),
('no_release','No autoridad genuina/aceptación creada;30 gates/E01-E05/D5 abiertos,CE12 diferido sin nuevo prerrequisito final prelaunch.')]


def build_candidate():
    a,acq,h=rd(A01),rd(ACQUISITION),rd(HANDOFF)
    pins={**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in PRIOR_FILES}};assert len(pins)==1152
    return dict(schema='d5.i271-rq01-rt01-request.v1',increment='I271',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        request_document_id='PGE251-RQ01-RT01-REQUEST-CANDIDATE-01',lot_id='A01',request_id='RQ01',return_id='RT01',
        kind='LOCAL_UNSENT_FOCUSED_REQUEST_FOR_PREEXISTING_AUTHORITY_NOT_AUTHORITY_ISSUANCE_ENROLLMENT_INTAKE_OR_ACCEPTANCE',
        status='RQ01_RT01_DRAFT_PREPARED_EA01_R06_R08_GENUINE_AUTHORITY_AND_ELIGIBILITY_MISSING_SD01_ACTIVE_NOT_ADMITTED',input_pins=pins,
        original_A01=pin(A01),original_RQ01_source=pin(A01,'/unsent_request'),exact_original_RQ01=a['unsent_request'],
        original_RT01_source=pin(A01,'/requested_returns/0'),exact_original_RT01=a['requested_returns'][0],
        handoff_entry_source=pin(HANDOFF,'/first_material_request'),exact_handoff_entry=h['first_material_request'],latest_review=pin(PRIOR_REVIEW),
        unsent_request=dict(subject='RQ01/RT01 — Aportación de autoridad preexistente y elegibilidad genuina EA01/R06/R08',
            recipient_role_only=a['unsent_request']['recipient_role_only'],
            text='Borrador local sin envío. Aportar exclusivamente material genuino ya disponible con autoridad propia para RT01 de RQ01/A01:EA01 autoridad accountable del scope lógico,EA02 R06 primario y EA03 R08 separado. Para cada sujeto adjuntar cuerpos completos y referencias disponibles con locator/bytes/digest/autor/provider/custodia;humano canónico/aliases,emisor y cadena preexistente de delegación/provenance,competencia/appointment,scope/acciones permitidas-denegadas,vigencia/currentness/revocación e independencia genuinos. No apoyar autoridad sólo en esta solicitud,asistente/Git,autoatestación o futuros W02/bundle/root. W02 aporta criterios,no aceptación previa/roster final/CE10 como condición de A01. Señalar todo faltante/rechazo/incompatibilidad y dependientes sin fabricar autoridad,personas,hashes o cuerpos. No emitir/firmar/keygen/verificar crypto,enrolar/contactar/fetch/provisionar/configurar/probar/ejecutar o cambiar cuotas/reservas. RT01 no completa RT02-RT05/A01 ni habilita RQ02;SD01/no admisión siguen activos. Este borrador no solicita una actuación operacional.',
            is_draft_only=True,sent=False,contact_authorized=False,actual_recipient_persons=None,actual_address_or_channel=None,
            actual_contact_authority=None,actual_sending_or_delivery_or_receipt=None),
        subject_evidence_requests=[dict(id=row['id'],required_role=row['exact_existing_requirement']['required_role'],subject=row['exact_existing_requirement']['subject'],
            source=pin(A01,'/authority_evidence_requests/'+str(i)),exact_original_requirement=row,
            mandatory_material_fields=row['required_independent_material_fields'],requested_return_sections=[s[0] for s in SECTIONS],
            actual_canonical_human_aliases_competence_or_appointment=None,actual_preexisting_authority_chain_scope_validity_or_independence_proof=None,
            actual_body_inventory_or_provenance=None,actual_primary_review_or_separate_decision=None,accepted=False)
            for i,row in enumerate(a['authority_evidence_requests'])],
        requested_information_sections=[dict(name=name,title=title,requirements=text,applies_to=['EA01','EA02','EA03'],
            original_RT01_requirement=pin(A01,'/requested_returns/0'),universal_contract_source=pin(ACQUISITION,'/evidence_delivery_contract'),
            actual_available_material_or_review=None,accepted=False) for name,title,text in SECTIONS],
        universal_delivery_requirement=dict(source=pin(ACQUISITION,'/evidence_delivery_contract'),exact_requirement=acq['evidence_delivery_contract'],
            mandatory_fields=acq['evidence_delivery_contract']['mandatory_return_fields'],known_logical_target_not_effective_freeze=True,
            unavailable_effective_identifiers_or_hashes_remain_null_no_predictive_values=True,no_actual_positive_runtime_or_authority_record_defined=True),
        inherited_A01_boundaries=[dict(section=s,source=pin(A01,'/'+s),exact_requirement=a[s]) for s in BOUNDARIES],
        RT01_intake_checklist=[dict(id='RC%02d'%(i+1),topic=topic,criterion=text,actual_genuine_evidence_or_eligible_decision=None,
            disposition='PENDING_GENUINE_PREEXISTING_AUTHORITY_AND_ELIGIBILITY',accepted=False) for i,(topic,text) in enumerate(CRITERIA)],
        complete_A01_followthrough=dict(remaining_return_sources=[pin(A01,'/requested_returns/'+str(i)) for i in range(1,5)],remaining_return_ids=['RT02','RT03','RT04','RT05'],
            A01_intake_source=pin(A01,'/acceptance_checklist'),A01_deliverable_source=pin(A01,'/W01_deliverable_coverage'),A01_exit_source=pin(A01,'/W01_exit_coverage'),
            RT01_intake_not_complete_A01_or_RQ02_authority=True,all_A01_criteria_and_reviews_before_downstream_consideration=True,
            RQ02_or_other_lot_enabled=False,actual_RT01_or_A01_acceptance=None),
        material_routes=dict(existing_material=dict(only_genuinely_supplied_existing_material_with_own_authorized_provenance=True,
                actual_received_inventory=None,provided_real_bodies=[],rejected_real_bodies=[],actual_evaluations=0,actual_primary_or_separate_decisions=None),
            missing_material=dict(SD01_stop_active=True,missing_authority_or_body_keeps_RT01_and_A01_unaccepted=True,
                no_fabricated_authority_body_human_hash_provider_or_calendar=True,no_global_absence_or_infeasibility_from_missing_evidence=True,
                separate_exact_authority_for_any_new_contact_operational_action_or_material_generation=True,actual_gap_or_separate_action_authority=None,actual_work_performed=False)),
        critical_boundaries=dict(
            EA01_scope_EA02_R06_EA03_R08_genuine_preexisting_own_authority_not_user_docs_request_self_or_forecast=True,
            RQ01_RT01_focused_request_not_nomination_enrollment_authority_issuance_or_sent_message=True,
            W02_eligibility_criteria_not_reverse_W02_acceptance_full_future_roster_or_CE10_precondition=True,
            canonical_people_aliases_competence_appointments_14_exclusions_all_preparers_no_Git_assistant_keys_alone=True,
            qualified_R01_R02_overlap_not_blanket_separation_or_preapproval_of_future_authors=True,
            complete_bodies_immutable_locators_bytes_digests_authors_providers_custody_and_reference_closure_required=True,
            preexisting_issuer_delegation_scope_validity_currentness_revocation_not_self_signature_or_host_date_alone=True,
            logical_scope_document_hash_not_effective_source_runtime_image_adoption_or_operational_authority=True,
            unknown_not_zero_no_predictive_hash_false_complete_inventory_or_schema_flag_as_truth=True,
            RT01_only_does_not_accept_A01_RT02_RT05_twelve_criteria_three_deliverables_three_exits_and_genuine_reviews_still_needed=True,
            no_RQ02_downstream_positive_intake_or_automatic_handoff=True,
            genuine_R06_primary_R08_separate_decisions_not_same_assistant_documentary_PASS_commit_push=True,
            missing_or_changed_material_keeps_SD01_and_invalidates_affected_A01_A08_no_automatic_transfer=True,
            no_contact_fetch_verification_service_implementation_build_qualification_clock_ledger_process_probe_execution=True,
            no_positive_crypto_codec_signing_keygen_enrollment_snapshot_record_C_Q_root_bundle_mapping_claim_receipt_configuration=True,
            both_Readers_reference_global_costs_limits_quotas_reserves_guards_outputs_unchanged_no_free_runtime_input=True,
            CE12_private_deferred_no_final_E06_Q_root_claim_spawn_receipt_as_new_prelaunch_condition=True,
            no_certificate_PJC115_R2_or_D5_release_no_genuine_authority_or_acceptance_from_preparation=True),
        final_route_boundary=dict(source=pin(ACQUISITION,'/final_route_boundary'),exact_requirement=acq['final_route_boundary'],
            current_run_command=None,actual_final_route_or_receipt_authorized=False),
        current_effect={**h['current_effect'],'RQ01_RT01_focused_documentary_request_prepared':True,'RQ01_RT01_request_sent':False,
            'actual_RT01_authority_eligibility_intake_or_acceptance_created':False},
        producer=dict(identity='Same Codex assistant/chat as I269/I270/A01',documentary_preparer_only=True,actor_independent=False,
            competent_primary_role_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_delivery_genuine_authority_eligibility_review_acceptance_execution_or_D5_closure=True))


def validate(d):
    assert d==build_candidate(),'Focused request differs from exact documentary reconstruction'
    a,acq=rd(A01),rd(ACQUISITION)
    assert (d['lot_id'],d['request_id'],d['return_id'])==('A01','RQ01','RT01')
    assert d['exact_original_RT01']==fragment(d['original_RT01_source'])==a['requested_returns'][0]
    assert d['exact_original_RQ01']==fragment(d['original_RQ01_source'])==a['unsent_request']
    assert d['exact_handoff_entry']==fragment(d['handoff_entry_source'])==rd(HANDOFF)['first_material_request']
    rows=d['subject_evidence_requests'];assert [r['id'] for r in rows]==['EA01','EA02','EA03']
    assert [r['required_role'] for r in rows]==['SCOPE_AUTHORITY','R06','R08']
    for i,row in enumerate(rows):
        assert row['exact_original_requirement']==fragment(row['source'])==a['authority_evidence_requests'][i]
        assert row['mandatory_material_fields']==a['authority_evidence_requests'][i]['required_independent_material_fields'] and len(row['mandatory_material_fields'])==7
    assert len(d['universal_delivery_requirement']['mandatory_fields'])==8
    assert d['universal_delivery_requirement']['exact_requirement']==fragment(d['universal_delivery_requirement']['source'])==acq['evidence_delivery_contract']
    eligibility=a['eligibility_boundary'];assert len(eligibility['exact_separation_matrix'])==14
    assert eligibility['no_blanket_R01_R02_separation_or_future_full_roster_required_for_A01'] is True
    assert len(d['requested_information_sections'])==6 and len(d['RT01_intake_checklist'])==16
    follow=d['complete_A01_followthrough'];assert [fragment(r)['id'] for r in follow['remaining_return_sources']]==['RT02','RT03','RT04','RT05']
    assert len(fragment(follow['A01_intake_source']))==12 and len(fragment(follow['A01_deliverable_source']))==len(fragment(follow['A01_exit_source']))==3
    assert len(d['critical_boundaries'])==18 and all(v is True for v in d['critical_boundaries'].values())
    pointers(d)


NEGATIVE_CASES = [
('sent',('unsent_request','sent'),True),('contact',('unsent_request','contact_authorized'),True),('recipient',('unsent_request','actual_recipient_persons'),'UNVERIFIED_TEST_LABEL'),
('entry_missing',('subject_evidence_requests',),[]),('R06_replaced',('subject_evidence_requests',1,'required_role'),'R01'),
('EA01_human_fabricated',('subject_evidence_requests',0,'actual_canonical_human_aliases_competence_or_appointment'),'UNVERIFIED_TEST_LABEL'),
('authority_fabricated',('subject_evidence_requests',0,'actual_preexisting_authority_chain_scope_validity_or_independence_proof'),{}),
('review_fabricated',('subject_evidence_requests',1,'actual_primary_review_or_separate_decision'),{}),('EA03_accepted',('subject_evidence_requests',2,'accepted'),True),
('subject_fields_omitted',('subject_evidence_requests',0,'mandatory_material_fields'),[]),('section_missing',('requested_information_sections',),[]),
('universal_fields_omitted',('universal_delivery_requirement','mandatory_fields'),[]),
('effective_hash_required',('universal_delivery_requirement','unavailable_effective_identifiers_or_hashes_remain_null_no_predictive_values'),False),
('boundary_omitted',('inherited_A01_boundaries',),[]),('criterion_accepted',('RT01_intake_checklist',0,'accepted'),True),
('remaining_returns_omitted',('complete_A01_followthrough','remaining_return_ids'),[]),('RT01_completes_A01',('complete_A01_followthrough','RT01_intake_not_complete_A01_or_RQ02_authority'),False),
('RQ02_enabled',('complete_A01_followthrough','RQ02_or_other_lot_enabled'),True),('inventory_fabricated',('material_routes','existing_material','actual_received_inventory'),[]),
('SD01_bypassed',('material_routes','missing_material','SD01_stop_active'),False),('work_done',('material_routes','missing_material','actual_work_performed'),True),
('forecast_authority',('critical_boundaries','EA01_scope_EA02_R06_EA03_R08_genuine_preexisting_own_authority_not_user_docs_request_self_or_forecast'),False),
('W02_backward_precondition',('critical_boundaries','W02_eligibility_criteria_not_reverse_W02_acceptance_full_future_roster_or_CE10_precondition'),False),
('independence_waived',('critical_boundaries','canonical_people_aliases_competence_appointments_14_exclusions_all_preparers_no_Git_assistant_keys_alone'),False),
('R01_R02_blanket',('critical_boundaries','qualified_R01_R02_overlap_not_blanket_separation_or_preapproval_of_future_authors'),False),
('partial_body_as_proof',('critical_boundaries','complete_bodies_immutable_locators_bytes_digests_authors_providers_custody_and_reference_closure_required'),False),
('host_date_as_authority',('critical_boundaries','preexisting_issuer_delegation_scope_validity_currentness_revocation_not_self_signature_or_host_date_alone'),False),
('scope_as_execution',('critical_boundaries','logical_scope_document_hash_not_effective_source_runtime_image_adoption_or_operational_authority'),False),
('unknown_zero',('critical_boundaries','unknown_not_zero_no_predictive_hash_false_complete_inventory_or_schema_flag_as_truth'),False),
('assistant_as_review',('critical_boundaries','genuine_R06_primary_R08_separate_decisions_not_same_assistant_documentary_PASS_commit_push'),False),
('acceptance_transfer',('critical_boundaries','missing_or_changed_material_keeps_SD01_and_invalidates_affected_A01_A08_no_automatic_transfer'),False),
('operational_action',('critical_boundaries','no_contact_fetch_verification_service_implementation_build_qualification_clock_ledger_process_probe_execution'),False),
('signing_config',('critical_boundaries','no_positive_crypto_codec_signing_keygen_enrollment_snapshot_record_C_Q_root_bundle_mapping_claim_receipt_configuration'),False),
('free_inputs_or_quotas',('critical_boundaries','both_Readers_reference_global_costs_limits_quotas_reserves_guards_outputs_unchanged_no_free_runtime_input'),False),
('receipt_precondition',('critical_boundaries','CE12_private_deferred_no_final_E06_Q_root_claim_spawn_receipt_as_new_prelaunch_condition'),False),
('run_command',('final_route_boundary','current_run_command'),'UNVERIFIED_TEST_LABEL'),('receipt_authorized',('final_route_boundary','actual_final_route_or_receipt_authorized'),True),
('A01_accepted',('current_effect','A01_accepted'),True),('D5_closed',('current_effect','D5_closed'),True),('assistant_independent',('producer','actor_independent'),True)]


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
    return dict(schema='d5.i271-preparation-review.v1',increment='I271',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,subject=pin(SUBJECT),findings=[],
        counts=dict(input_pins=1152,entry_subjects=3,subject_material_field_groups=7,universal_return_fields=8,information_sections=6,RT01_intake_criteria=16,
            inherited_A01_boundaries=9,separation_requirements=14,remaining_A01_returns=4,complete_A01_intake_criteria=12,A01_deliverables=3,A01_exits=3,
            critical_boundaries=18,documentary_rejections=len(NEGATIVE_CASES),preserved_published_files=844,new_files=5,actual_received_bodies=0,actual_genuine_authorities_or_acceptances_created=0,
            prelaunch_gates_closed=0,resource_obligations_closed=0),rejection_checks=rejections(d),
        source_reconstruction=dict(A01_RT01_original_requirements_and_I269_entry_exact=True,I270_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        current_effect=d['current_effect'],limitations=['Focused local RQ01/RT01 draft is no outbound message,nomination,enrollment,preexisting authority body or genuine eligibility/acceptance decision. EA01/R06/R08 remain unspecified and all material missing.',
            'W02 supplies eligibility criteria,not backward W02 acceptance/future full roster/CE10 prerequisite. A01 logical scope is not effective W03 source/runtime freeze or operational authority.',
            'RT01 is one return of RQ01. RT02-RT05,12 A01 criteria,3 deliverables/3 exits and own genuine reviews remain required;RQ02 not enabled,SD01 active,no admission.',
            'Thirty gates,E01-E05/PJC115-R2/D5 remain open;CE12/final route separately deferred. No execution,crypto/signing/keygen/enrollment,contact/provision/configuration/probe,quota/reserve or active authority/binding/destination/certificate change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I271-audit.py',expected_result=STATUS,over400_lines=True,
            reason='One focused RQ01/RT01 documentary request with exact authority/eligibility sources,pins,rejection checks and preservation; overage declared,no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage/graph checks and in-memory mutations only; no target import,compile,discovery,tests,execution,build,benchmark,codec,crypto,signing,keygen,enrollment,contacts,provision,configuration or platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes.'),
        provenance=d['producer'],publication=d['publication'])


def main():
    d=rd(SUBJECT);validate(d);verify_blobs(d['input_pins'])
    review=build_review();assert review==rd(PREP)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published839'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)};assert len(preserved)==844
    seal=rd(SEAL);assert seal['schema']=='d5.i271-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published844']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==d['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,**review['counts'],D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
