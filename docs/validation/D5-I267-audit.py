#!/usr/bin/env python3
"""I267 A08/RQ08 documentary preparation; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '72304662b891e59b77370a78b3f6cbc536ab3eff'
DATE = '2026-11-26'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
A07 = P+'D5-I251-A07-RQ07-FINAL-CUSTODY-MAPPING-CANDIDATE.json'
PRIOR_RECON = P+'D5-I266-I265-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I266-I265-documentary-review.json'
PRIOR_AUDIT = P+'D5-I266-audit.py'
PRIOR_SEAL = P+'D5-I266-integrity.json'
PRIOR_DOC = 'docs/design/D5-I266-I265-A07-RQ07-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I251-A08-RQ08-GENUINE-PRELAUNCH-GATE-DECISION-CANDIDATE.json'
PREP = P+'D5-I267-preparation-review.json'
AUDIT = P+'D5-I267-audit.py'
SEAL = P+'D5-I267-integrity.json'
DOC = 'docs/design/D5-I267-A08-RQ08-GENUINE-PRELAUNCH-GATE-DECISION.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
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


W13 = P+'D5-I223-W13-PRELAUNCH-GATE-DECISION-CANDIDATE.json'
STATUS = 'PASS_STATIC_SOURCE_ONLY_A08_RQ08_PREPARED_ALL_PREDECESSORS_GENUINE_GATE_AND_RESOURCE_DECISIONS_MISSING_NOT_ADMITTED'

SECTIONS = 'dependency_gate package_dependency_requirements role_scope_matrix competent_decision_boundary thirty_gate_disposition_ledger deferred_receipt_gate disposition_summary E01_E05_disposition_ledger twenty_criterion_disposition_ledger joint_resource_decision_boundary proof_reference_disposition additional_proof_requirement_ledger stop_requirement_ledger deferred_handoff CE12_boundary final_binding_requirement_ledger source_resource_and_invalidation_boundary non_admission_record authority_boundary exit_predicate_dispositions preserved_scope_and_gates'.split()
RETURNS = [
('GD01','Antecedentes y autoridad genuinos',
 'Aportar A01-A07 genuinamente aceptados con W01-W12 completos y mismo scope; autoridad de entrada,identidades humanas canónicas/aliases/competencia/appointments/custodia/anchors y todas las contribuciones reales auténticas. R06 y R08 separados bajo14 exclusiones/keys heredadas;el asistente/Git/strings no aportan independencia. W09 ya aceptado sobre hechos auténticos,W10 finaliza los mismos hechos,no retroautenticación o forecast CE10/root. I266 documental no acepta A07.',
 ['dependency_gate','package_dependency_requirements','role_scope_matrix','competent_decision_boundary']),
('GD02','Treinta decisiones por gate con trazabilidad completa',
 'Entregar siete familias,16 reglas y siete globales,una disposición aceptada/rechazada/pendiente por cada ID exacto con evidencia suficiente/cuerpos canónicos completos bytes/hash/locator/source/runtime/scope/autor/provider/custodia/validez/currentness/revocación y todos los supuestos/derivaciones/caps/Reader/guards. Probar cada requisito exacto y close_only_if y disponer revisiones primarias R06 y aceptación separada R08 genuinas. Retener producers/collection lots;W13 es salida de decisión,no su propio antecedente aceptado. Ningún cierre por presencia/schema/firma/flag/presupuesto o PASS documental.',
 ['thirty_gate_disposition_ledger','disposition_summary','competent_decision_boundary']),
('GD03','Join auténtico E01-E05 y veinte criterios',
 'Aportar cinco obligaciones completas y sus cuatro criterios cada una,revalidados en el mismo sucesor/fuentes/runtime/image/caller/platform/epoch/policy y todos los supuestos/unidades/capacidad/servicio/caps/Reader/guards compatibles. W09 conserva R03/R06 y R08;W13 no sustituye esas decisiones. Heap completo H01-H11 y vidas/allocator/native,30 trabajos,WCET/CPU/IO/delays/clock/fases/atomicidad/BASIS/index/900 segundos requieren evidencia real,no presupuestos,reservas,watchdog,CPU sum=wall o unknown=0. Legado CP03 179/321/12 y30 sitios no aceptación del sucesor.221644/40500 sólo modelo condicionado,no fit/recursos. No transferencia de resultados históricos.',
 ['E01_E05_disposition_ledger','twenty_criterion_disposition_ledger','joint_resource_decision_boundary','source_resource_and_invalidation_boundary']),
('GD04','Inventario completo y pruebas adicionales',
 'Entregar inventario real completo de referencias faltantes/aportadas/rechazadas,instancias y cuerpos disponibles inmutables con bytes/hash/locator/provenance/autores/providers/custodia/scope/unidades/supuestos/review/validez.69 plantillas con arrays y registros repetidos no cuenta real/única de cuerpos o closure;ausencia de rechazo no aceptación. Ocho pruebas adicionales completas y cuatro bindings finales con fase exacta,sin fabricarlos o exigir eventos CE12 finales como prueba prelaunch. Ambos Readers/global lookup/freshness/identity/crypto/native/IO/copies/registry/ledger/frames/receipt/output/failures/cleanup conservan costes;no lecturas ocultas o offline gratis. Derivaciones completas deben caber límites o rechazar/revisar grafo,no truncar/subir cuota.',
 ['proof_reference_disposition','additional_proof_requirement_ledger','final_binding_requirement_ledger','source_resource_and_invalidation_boundary']),
('GD05','Dictamen primario y aceptación separada auténticos',
 'Entregar cuerpos inmutables propios de decisiones R06 y R08 por gate y agregado con autoridad/competencia/appointments/independencia/canonical humans reales,motivos y referencias completas en mismo scope/epoch/validez. Respetar todas14 exclusiones y preparadores,R08 humano/key separado de R01/R02;solapamiento R01/R02 sólo mismo humano cualificado y dominios separados. Decisión aceptada sólo con30 gates probados y join E01-E05/20 completo;incompletitud/rechazo/incompatibilidad conserva dictamen negativo/no admisión. No firmas/accepted flags/JSON sintéticos como reviews genuinas ni publicación como aceptación.',
 ['role_scope_matrix','competent_decision_boundary','disposition_summary','joint_resource_decision_boundary','non_admission_record']),
('GD06','Handoff limitado X09 y CE12 diferido',
 'Entregar únicamente obligaciones finales pendientes,sin comando actual ni afirmar satisfechos prerrequisitos. Separar cuatro externos antes del claim:autorización explícita de ejecución,E06/payload reales,Q/root confiable reales y admisión completa;claim atómico one-use/construcción protegida reales después de admisión y antes de paths/spawn como quinto antes de recibo. Claim no su propia precondición;uncertain/partial/expired/failed no free retry o reuse. Recibo privado,no output/campo wire,31a fila FAMILY-LAUNCH_RECEIPT excluida de30 y DEFERRED_NOT_AUTHORIZED. Ningún E06/Q/root/admisión/claim/spawn/recibo o finalización de ruta final nueva condición CE11/prelaunch. Aceptación recursos/custodia no ejecución/certificado/PJC115-R2/cierre D5.',
 ['deferred_receipt_gate','deferred_handoff','CE12_boundary','non_admission_record','authority_boundary']),
('GD07','Gaps,paradas e invalidación',
 'Identificar cada cuerpo/autor/provider/review/autoridad/scope/fit/supuesto/binding faltante o incompatible y dependientes;mantener SD01-SD08/no admisión y disposición pendiente/rechazada según decisión genuina. Cambios author/body/source/runtime/image/caller/domain/resource/epoch/key/policy/mapping/grafo invalidan afectados A01-A08 y exigen recualificación/review antes de avanzar,sin transferencia automática hashes/pruebas/aprobaciones/aceptaciones. Indicar trabajo y autoridad separados,sin contacto/ejecución/componentes/crypto/signing/keygen/enrollment/snapshots/emisión registros/C/bundle/Q/root/claim/recibo/provision/config/probes/cuotas/reservas. No inventar proveedores/plazos/hash o inviabilidad global por material ausente.',
 ['stop_requirement_ledger','source_resource_and_invalidation_boundary','authority_boundary','preserved_scope_and_gates'])]
CRITERIA = [
('Antecedentes A01-A07 y W01-W12 genuinos,sin PASS documental como aceptación o envío.',['GD01']),
('R06/R08 canónicos competentes/appointments/14 exclusiones y preparadores completos,no asistente.',['GD01','GD05']),
('Mismos hechos previamente auténticos W09 reconciliados W10-W12,sin retroautenticación/transferencia.',['GD01','GD03']),
('Treinta IDs exactos:7 familias16 reglas7 globales,productores y lotes conservados.',['GD02']),
('Por gate exact requisito/close_only_if y cuerpos bytes/hash/locator/scope/provenance/currentness completos.',['GD02','GD04']),
('Disposición aceptada/rechazada/pendiente real y motivos R06/R08;W13 salida,no antecedente propio.',['GD02','GD05']),
('Cinco obligaciones y20 criterios sucesor completos compatibles,sin resultados históricos transferidos.',['GD03']),
('R03/R06 y R08 genuinos W09 conservados,no reemplazo por dictamen W13.',['GD03','GD05']),
('Heap11 propietarios/vidas/native/allocator,30 trabajos/WCET/CPU/IO/servicio/reloj/900 completos.',['GD03']),
('Unknown no cero,reserva no capacidad,CPU sum no wall/watchdog no éxito,fit condicionado no real.',['GD03','GD04']),
('Inventario real faltante/aportado/rechazado completo;69 plantillas no cuerpos únicos/cierre.',['GD04']),
('Ocho pruebas adicionales y cuatro bindings con fase exacta,sin crear finales o invertir dependencias.',['GD04','GD06']),
('Referencias y ambos Readers/global joins costes/units/supuestos íntegros,sin truncar/cuota mayor.',['GD03','GD04']),
('Agregado aceptable sólo con30 gates y join completo,decisiones independientes reales.',['GD02','GD03','GD05']),
('FAMILY-LAUNCH_RECEIPT separado31a fila excluida30,privado,diferido,no autorizado.',['GD06']),
('Cuatro prerrequisitos antes claim,claim/construcción quinto antes recibo,no self-condition/retry gratis.',['GD06']),
('No E06/Q/root/claim/spawn/receipt/finalroute como nueva condición prelaunch,ni comando actual.',['GD06']),
('Gaps SD01-SD08 mantienen negativo/no admisión,sin nueva autoridad o inviabilidad inferida.',['GD07']),
('Cambio invalida afectados A01-A08 con nueva review,sin transferir pruebas/aceptaciones/rebind.',['GD01','GD07']),
('Recursos/custodia no ejecución/certificado activo/PJC115-R2/D5,cuotas o autoridad/destinos.',['GD05','GD06','GD07'])]


def build_candidate():
    acq,plan,w=rd(ACQUISITION),rd(PLAN),rd(W13);lot=acq['acquisition_lots'][7];req=plan['work_packages'][12]
    pins={**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in PRIOR_FILES}};assert len(pins)==1132
    return dict(schema='d5.i267-a08-rq08-documentary-preparation.v1',increment='I267',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        dossier_id='PGE251-A08-RQ08-CANDIDATE-01',lot_id='A08',request_id='RQ08',work_package='W13',planned_deliverable_id=req['deliverable_id'],
        kind='CONDITIONAL_LOCAL_UNSENT_REQUEST_FOR_GENUINE_PRELAUNCH_GATE_DECISIONS_NOT_ACTUAL_ACCEPTANCE_OR_EXECUTION_RELEASE',
        status='A08_RQ08_DOCUMENTARY_PREPARED_ALL_PREDECESSORS_UNACCEPTED_SD01_ACTIVE_NOT_ACCEPTED_NOT_ADMITTED',input_pins=pins,
        acquisition_lot_binding=pin(ACQUISITION,'/acquisition_lots/7'),exact_acquisition_lot=lot,
        W13_requirement_binding=pin(PLAN,'/work_packages/12'),exact_W13_requirement=req,W13_documentary_checklist=pin(W13),prior_A07_review=pin(PRIOR_REVIEW),
        dependency_gate=dict(required_lot_ids=lot['depends_on_lots'],required_external_work_package_ids=req['depends_on'],
            A07_state_source=pin(A07,'/current_effect'),exact_prior_effect=rd(A07)['current_effect'],
            actual_lot_acceptances={x:False for x in lot['depends_on_lots']},actual_genuine_antecedent_acceptance_bodies=None,
            SD01_stop_active=True,no_documentary_PASS_as_genuine_antecedent=True,no_send_contact_positive_intake_or_gate_resource_decision_from_preparation=True),
        unsent_request=dict(original_draft=lot['unsent_request_draft'],recipient_role_only=lot['intended_recipient_role_kind'],
            subject='RQ08 — Decisión genuina de30 gates de prelaunch / W13 / PGO181 candidato02',
            reviewable_request_text='Sólo con A01-A07/W01-W12 genuinos completos y aceptados,aportar GD01-GD06 bajo autoridad propia:decisión trazable R06 y R08 por cada uno de30 gates(7familias/16reglas/7globales),join E01-E05/20 criterios e inventario íntegro de cuerpos/refs/costes/supuestos/reviews;handoff limitado sin comando o liberación. W13 decide,no su propio antecedente. Si falta/cambia evidencia o independencia,GD07/SD01-SD08/no admisión. CE12/recibo31 separado diferido,ningún evento final como nueva condición prelaunch. No crear cuerpos/firmas/autoridad,mapping/claim/worker/recibo,contactar/configurar/probar/ejecutar o cambiar cuotas/reservas. Antecedentes siguen sin aceptar;RQ08 no se envía.',
            required_return_ids=[x[0] for x in RETURNS],is_draft_only=True,sent=False,contact_authorized=False,
            actual_recipient_persons=None,actual_addresses_or_channels=None,actual_contact_authority=None,actual_delivery_or_receipt=None),
        requested_returns=[dict(id=i,title=title,requirements=text,W13_requirement_sources=[pin(W13,'/'+s) for s in sections],
            universal_delivery_source=pin(ACQUISITION,'/evidence_delivery_contract'),actual_body_inventory=None,actual_received=False,
            actual_primary_reviews=None,actual_separate_acceptance=None,accepted=False) for i,title,text,sections in RETURNS],
        inherited_W13_requirements=[dict(section=s,source=pin(W13,'/'+s),documentary_container_dimension=len(w[s]),
            dimension_not_actual_bodies_proofs_fit_or_acceptance=True,actual_complete_same_scope_evidence_or_decision=None,accepted=False) for s in SECTIONS],
        gate_decision_requests=[dict(id=row['id'],category=row['category'],W13_gate_source=pin(W13,'/thirty_gate_disposition_ledger/'+str(i)),
            plan_gate_source=row['source'],exact_requirement=row['exact_plan_gate']['exact_requirement'],close_only_if=row['exact_plan_gate']['close_only_if'],
            collection_source=pin(ACQUISITION,'/gate_to_collection_matrix/'+str(i)),required_collection_lots=acq['gate_to_collection_matrix'][i]['required_collection_lots'],
            producer_work_package_ids=row['exact_plan_gate']['producer_work_package_ids'],
            genuine_accepted_external_work_package_ids=[x for x in row['exact_plan_gate']['producer_work_package_ids'] if x!='W13'],
            W13_producer_is_decision_output_not_accepted_self_predecessor=('W13' in row['exact_plan_gate']['producer_work_package_ids']),
            primary_review_roles=['R06'],separate_acceptor_role='R08',required_return_ids=['GD02','GD04','GD05'],
            allowed_future_dispositions=['ACCEPTED','REJECTED','PENDING'],current_disposition='PENDING_GENUINE_ANTECEDENTS_EVIDENCE_AND_INDEPENDENT_DECISIONS',
            actual_complete_body_bytes_hash_locator_scope_author_provider_custody_validity_or_derivation=None,
            actual_primary_R06_review=None,actual_separate_R08_acceptance=None,actual_condition_verified=False,accepted=False,rejected=False,closed=False,execution_authorized=False)
            for i,row in enumerate(w['thirty_gate_disposition_ledger'])],
        resource_decision_requests=[dict(id=row['id'],source=pin(W13,'/E01_E05_disposition_ledger/'+str(i)),exact_plan_requirement=row['exact_plan_requirement'],
            criterion_ids=[row['id']+'-R%d'%j for j in range(1,5)],primary_review_roles=['R03','R06'],separate_acceptor_role='R08',required_return_ids=['GD03','GD05'],
            actual_complete_same_scope_bound_or_platform_service_proof=None,actual_primary_and_separate_decisions=None,accepted=False,closed=False)
            for i,row in enumerate(w['E01_E05_disposition_ledger'])],
        resource_criterion_requests=[dict(id=row['id'],obligation=row['obligation'],source=pin(W13,'/twenty_criterion_disposition_ledger/'+str(i)),
            exact_plan_requirement=row['exact_plan_requirement'],required_return_ids=['GD03','GD05'],actual_complete_revalidation_evidence_and_decisions=None,
            current_disposition='PENDING_NOT_TRANSFERRED_FROM_HISTORICAL_RESULT',accepted=False,closes_resource_obligation=False)
            for i,row in enumerate(w['twenty_criterion_disposition_ledger'])],
        role_evidence_requests=[dict(id=row['id'],source=pin(W13,'/role_scope_matrix/'+str(i)),exact_requirement=row,required_return_ids=['GD01','GD05'],
            actual_canonical_human_appointment_competence_independence_or_review=None,accepted=False) for i,row in enumerate(w['role_scope_matrix'])],
        critical_boundaries=dict(
            all_A01_A07_W01_W12_genuinely_accepted_SD01_active_no_PASS_as_antecedent=True,
            exact30_gates_7_families16_rules7_globals_no_receipt_in_prelaunch=True,
            W13_is_review_output_not_own_accepted_predecessor=True,
            each_gate_requires_complete_genuine_bodies_scope_authorship_custody_currentness_and_R06_R08=True,
            all14_identity_key_exclusions_and_complete_preparers_no_assistant_as_independent_reviewer=True,
            E01_E05_all20_criteria_same_scope_complete_W09_R03_R06_R08_not_replaced=True,
            heap_lifetimes_all30_work_WCET_CPU_IO_service_clock_phases900_unknown_not_zero=True,
            full_actual_reference_inventory_69_templates_not_unique_bodies_no_absence_of_rejection_as_acceptance=True,
            both_Readers_all_global_reference_native_crypto_IO_copy_registry_ledger_output_failure_costs_retained=True,
            conditional221644_40500_not_actual_fit_capacity_service_or_reserve=True,
            no_partial_positive_aggregate_no_document_signature_flag_or_budget_as_truth=True,
            CE12_receipt31_private_deferred_not_authorized_not_new_prelaunch_condition=True,
            four_prerequisites_before_claim_fifth_claim_construction_before_receipt_claim_not_own_condition=True,
            uncertain_partial_expired_failed_claim_no_free_retry_or_reuse=True,
            W09_authentic_facts_before_W10_freeze_no_forecast_CE10_root_or_automatic_transfer=True,
            changed_author_body_scope_source_runtime_mapping_epoch_policy_invalidates_any_affected_A01_A08=True,
            no_operational_record_crypto_contact_config_probe_execution_or_quota_authority_from_request=True,
            custody_resource_acceptance_not_execution_certificate_PJC115_R2_or_D5_release=True),
        material_routes=dict(existing_material=dict(required_returns=['GD%02d'%i for i in range(1,7)],actual_delivery_inventory=None,actual_route_accepted=False),
            missing_material=dict(required_return_id='GD07',SD01_SD08_stop_rules_preserved=True,gap_not_acceptance_or_global_infeasibility=True,
                separate_exact_work_authority_required=True,actual_gap_report=None,actual_new_action_authority=None,actual_work_performed=False)),
        deliverable_coverage=[dict(id='WD%02d'%(i+1),source=pin(PLAN,'/work_packages/12/deliverables/'+str(i)),exact_requirement=text,
            required_return_ids=[['GD02','GD04','GD05'],['GD03','GD05'],['GD06'],['GD05','GD06','GD07']][i],actual_complete_delivery=None,accepted=False)
            for i,text in enumerate(req['deliverables'])],
        acceptance_checklist=[dict(id='AC%02d'%(i+1),criterion=text,required_return_ids=ids,actual_complete_evidence_and_competent_reviews=None,
            disposition='PENDING_ALL_PREDECESSORS_GENUINE_GATE_RESOURCE_AND_INDEPENDENT_DECISIONS',accepted=False) for i,(text,ids) in enumerate(CRITERIA)],
        exit_coverage=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/12/exit_predicates/'+str(i)),exact_predicate=text,
            required_intake_criteria=['AC%02d'%j for j in range(1,21)],actual_genuine_disposition=None,accepted=False) for i,text in enumerate(req['exit_predicates'])],
        actual_material_state=dict(actual_received_inventory=None,provided_real_bodies=[],rejected_real_bodies=[],actual_evaluations=0,
            actual_provider_schedule_or_duration_guarantee=None,actual_gate_resource_or_aggregate_decision=None,actual_positive_review_or_acceptance_records_created=False,
            actual_operational_verification_execution_signing_configuration_or_probe_performed=False),
        preserved_resource_rules=dict(source=pin(ACQUISITION,'/preserved_resource_and_cost_rules'),exact_requirement=acq['preserved_resource_and_cost_rules'],
            no_quota_budget_reserve_transfer_or_resource_reservation_applied=True),
        handoff=dict(source=pin(W13,'/deferred_handoff'),exact_requirement=w['deferred_handoff'],CE12_source=pin(W13,'/CE12_boundary'),exact_CE12_requirement=w['CE12_boundary'],
            receipt_source=pin(W13,'/deferred_receipt_gate'),exact_receipt_requirement=w['deferred_receipt_gate'],
            exact_A08_completion_predicate=lot['completion_predicate'],exact_A08_missing_stop=lot['missing_or_failure_stop'],
            current_run_command=None,actual_accepted_prelaunch_handoff=None,actual_final_route_Q_root_claim_spawn_receipt_created=False,
            no_new_lot_or_automatic_release_created=True,final_route_requires_separate_exact_authority=True),
        change_control=dict(source=pin(W13,'/source_resource_and_invalidation_boundary'),exact_requirement=w['source_resource_and_invalidation_boundary'],
            changed_material_invalidates_affected_A01_A08_before_progress=True,no_automatic_prior_hash_proof_approval_mapping_or_acceptance_transfer=True,actual_refresh_or_active_rebind=False),
        current_effect={**rd(A07)['current_effect'],'A08_RQ08_documentary_prepared':True,'A08_accepted':False,'RQ08_sent':False,
            'actual_genuine_prelaunch_gate_resource_or_aggregate_decisions_created':False,'actual_A08_intake_progress_or_review_records_created':False},
        producer=dict(identity='Same Codex assistant/chat as I265/I266',documentary_preparer_only=True,actor_independent=False,competent_R03_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_genuine_decision_acceptance_authority_execution_or_D5_closure=True))


NEGATIVE_CASES = [
('antecedent_promoted',('dependency_gate','actual_lot_acceptances','A07'),False,True),('SD01_bypassed',('dependency_gate','SD01_stop_active'),True,False),
('PASS_as_antecedent',('dependency_gate','no_documentary_PASS_as_genuine_antecedent'),True,False),('request_sent',('unsent_request','sent'),False,True),
('contact',('unsent_request','contact_authorized'),False,True),('person_invented',('unsent_request','actual_recipient_persons'),None,['UNVERIFIED_TEST_LABEL']),
('gate_accepted',('gate_decision_requests',0,'accepted'),False,True),('gate_closed',('gate_decision_requests',29,'closed'),False,True),
('gate_rejected_without_material',('gate_decision_requests',1,'rejected'),False,True),('gate_verified',('gate_decision_requests',0,'actual_condition_verified'),False,True),
('gate_executed',('gate_decision_requests',0,'execution_authorized'),False,True),('review_invented',('gate_decision_requests',0,'actual_primary_R06_review'),None,{}),
('gate_missing',('gate_decision_requests',),None,None),
('resource_closed',('resource_decision_requests',4,'closed'),False,True),('criterion_accepted',('resource_criterion_requests',19,'accepted'),False,True),
('criterion_as_closure',('resource_criterion_requests',0,'closes_resource_obligation'),False,True),('role_accepted',('role_evidence_requests',0,'accepted'),False,True),
('W13_self_predecessor',('critical_boundaries','W13_is_review_output_not_own_accepted_predecessor'),True,False),
('resource_review_replaced',('critical_boundaries','E01_E05_all20_criteria_same_scope_complete_W09_R03_R06_R08_not_replaced'),True,False),
('unknown_zero',('critical_boundaries','heap_lifetimes_all30_work_WCET_CPU_IO_service_clock_phases900_unknown_not_zero'),True,False),
('templates_as_inventory',('critical_boundaries','full_actual_reference_inventory_69_templates_not_unique_bodies_no_absence_of_rejection_as_acceptance'),True,False),
('offline_free',('critical_boundaries','both_Readers_all_global_reference_native_crypto_IO_copy_registry_ledger_output_failure_costs_retained'),True,False),
('conditional_fit',('critical_boundaries','conditional221644_40500_not_actual_fit_capacity_service_or_reserve'),True,False),
('partial_positive',('critical_boundaries','no_partial_positive_aggregate_no_document_signature_flag_or_budget_as_truth'),True,False),
('receipt_precondition',('critical_boundaries','CE12_receipt31_private_deferred_not_authorized_not_new_prelaunch_condition'),True,False),
('claim_self_condition',('critical_boundaries','four_prerequisites_before_claim_fifth_claim_construction_before_receipt_claim_not_own_condition'),True,False),
('free_retry',('critical_boundaries','uncertain_partial_expired_failed_claim_no_free_retry_or_reuse'),True,False),
('retroauth',('critical_boundaries','W09_authentic_facts_before_W10_freeze_no_forecast_CE10_root_or_automatic_transfer'),True,False),
('release',('critical_boundaries','custody_resource_acceptance_not_execution_certificate_PJC115_R2_or_D5_release'),True,False),
('gap_as_authority',('material_routes','missing_material','actual_new_action_authority'),None,'UNVERIFIED_TEST_LABEL'),
('exit_accepted',('exit_coverage',0,'accepted'),False,True),('intake_accepted',('acceptance_checklist',0,'accepted'),False,True),
('inventory_fabricated',('actual_material_state','actual_received_inventory'),None,[]),('positive_review',('actual_material_state','actual_positive_review_or_acceptance_records_created'),False,True),
('quota',('preserved_resource_rules','no_quota_budget_reserve_transfer_or_resource_reservation_applied'),True,False),
('run_command',('handoff','current_run_command'),None,'UNVERIFIED_TEST_LABEL'),('receipt_created',('handoff','actual_final_route_Q_root_claim_spawn_receipt_created'),False,True),
('old_transfer',('change_control','no_automatic_prior_hash_proof_approval_mapping_or_acceptance_transfer'),True,False),
('A08_accepted',('current_effect','A08_accepted'),False,True),('D5_closed',('current_effect','D5_closed'),False,True),('assistant_independent',('producer','actor_independent'),False,True)]


def validate(d):
    assert d==build_candidate(),'A08/RQ08 differs from exact documentary reconstruction'
    assert len(d['gate_decision_requests'])==30 and len(d['resource_criterion_requests'])==20
    assert {c:sum(r['category']==c for r in d['gate_decision_requests']) for c in ['FAMILY','RULE','GLOBAL']}==dict(FAMILY=7,RULE=16,GLOBAL=7)
    assert len({r['id'] for r in d['gate_decision_requests']})==30
    w=rd(W13);plan=rd(PLAN)
    for row in d['gate_decision_requests']:
        source=fragment(row['W13_gate_source']);exact=fragment(row['plan_gate_source']);collection=fragment(row['collection_source'])
        assert source['id']==exact['id']==collection['id']==row['id'] and source['exact_plan_gate']==exact
        assert collection['required_work_package_ids']==row['producer_work_package_ids']
        assert row['exact_requirement']==exact['exact_requirement'] and row['close_only_if']==exact['close_only_if']
        assert 'W13' not in row['genuine_accepted_external_work_package_ids']
    for i,row in enumerate(d['resource_decision_requests']):
        assert fragment(row['source'])['exact_plan_requirement']==row['exact_plan_requirement']==plan['resource_obligation_matrix'][i]
    for i,row in enumerate(d['resource_criterion_requests']):
        assert fragment(row['source'])['exact_plan_requirement']==row['exact_plan_requirement']==plan['resource_criterion_matrix'][i]
    assert len(w['competent_decision_boundary']['exact_separation_matrix'])==14
    assert w['proof_reference_disposition']['static_template_count']==69
    assert w['deferred_receipt_gate']['excluded_from30_prelaunch_targets'] is True
    assert w['CE12_boundary']['actual_claim_spawn_receipt_or_final_route_completion_required_to_close_prelaunch'] is False
    pointers(d)


def rejections(d):
    results=[]
    for name,path,expected,value in NEGATIVE_CASES:
        mutant=copy.deepcopy(d);node=mutant
        for key in path[:-1]:node=node[key]
        if name=='gate_missing':node[path[-1]]=node[path[-1]][:-1]
        else:
            assert node[path[-1]]==expected,name
            node[path[-1]]=value
        try:validate(mutant)
        except AssertionError:results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:raise AssertionError(name)
    return results


def build_review():
    d=rd(SUBJECT);validate(d)
    prior=runpy.run_path(str(ROOT/PRIOR_AUDIT));exists=Path.exists
    rec=prior['reconstruct']();assert rec==rd(PRIOR_RECON)
    review=prior['build_review'](rec);assert review==rd(PRIOR_REVIEW) and Path.exists is exists
    return dict(schema='d5.i267-preparation-review.v1',increment='I267',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),counts=dict(input_pins=1132,required_lots=7,required_external_work_packages=12,gate_requests=30,families=7,rules=16,global_conditions=7,
            resource_obligations=5,resource_criteria=20,review_roles=2,separation_requirements=14,reference_templates=69,additional_proof_requirements=8,
            final_binding_requirements=4,inherited_sections=len(SECTIONS),requested_returns=7,intake_criteria=20,deliverables=4,exits=3,actual_evaluations=0,
            actual_received_bodies=0,actual_lots_accepted=0,prelaunch_gates_closed=0,resource_obligations_closed=0,documentary_rejections=len(NEGATIVE_CASES),preserved_published_files=824,new_files=5),
        findings=[],rejection_checks=rejections(d),current_effect=d['current_effect'],
        source_reconstruction=dict(I266_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True,
            I223_I251_W13_gate_and_resource_sources_reconciled=True),
        limitations=['All A01-A07 and W01-W12 remain unaccepted; SD01 active,RQ08 unsent. Preparation creates no genuine material,gate/resource/review/acceptance decision or independent identity.',
            'Thirty gates and E01-E05/twenty criteria remain pending. Sixty-nine templates are not actual unique proof-body counts; complete inventory,provenance,costs and sufficient genuine evidence still required.',
            'CE12 receipt separate deferred not authorized,no final route as new prelaunch condition; custody/resource acceptance not execution,certificate,PJC115-R2 or D5 release.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I267-audit.py',expected_result=STATUS,over400_lines=True,
            reason='One A08/RQ08 documentary request with30 gates,resource criteria,exact source pins,negative checks and preservation; overage declared,no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage/graph checks and in-memory mutations only. No target import,compile,discovery,tests,execution,build,benchmark,crypto,codec,signing,keygen,enrollment,contacts,provision,configuration or platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes.'),
        provenance=d['producer'],publication=d['publication'])


def main():
    d=rd(SUBJECT);validate(d);verify_blobs(d['input_pins'])
    review=build_review();assert review==rd(PREP)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published819'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)};assert len(preserved)==824
    seal=rd(SEAL);assert seal['schema']=='d5.i267-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published824']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==d['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,**review['counts'],D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
