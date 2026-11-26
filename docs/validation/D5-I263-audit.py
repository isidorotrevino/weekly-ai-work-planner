#!/usr/bin/env python3
"""I263 A06/RQ06 documentary preparation; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '05cbbb320557c5f2b3df07fd5216f1a97e82b531'
DATE = '2026-11-26'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
W09 = P+'D5-I223-W09-E01-E05-INTEGRATION-CANDIDATE.json'
A05 = P+'D5-I251-A05-RQ05-REQUALIFICATION-COMPLETE-BOUNDS-CANDIDATE.json'
PRIOR_RECON = P+'D5-I262-I261-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I262-I261-documentary-review.json'
PRIOR_AUDIT = P+'D5-I262-audit.py'
PRIOR_SEAL = P+'D5-I262-integrity.json'
PRIOR_DOC = 'docs/design/D5-I262-I261-A05-RQ05-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I251-A06-RQ06-INDEPENDENT-RESOURCE-JOIN-CANDIDATE.json'
PREP = P+'D5-I263-preparation-review.json'
AUDIT = P+'D5-I263-audit.py'
SEAL = P+'D5-I263-integrity.json'
DOC = 'docs/design/D5-I263-A06-RQ06-INDEPENDENT-RESOURCE-JOIN.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_A06_RQ06_PREPARED_PREDECESSORS_AND_GENUINE_INDEPENDENT_JOIN_DECISIONS_MISSING_NOT_ADMITTED'


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


RETURNS = [
    ('RJ01','Antecedentes, autores y autoridad independientes',
     ['dependency_gate','role_scope_matrix','role_and_identity_boundary','phase_handoff'],
     'Aportar A02-A05/W02-W08 genuinamente aceptados con A01 conservado y mismo source/runtime/image/caller/platform/resource/epoch/policy scope. Identificar/enrolar/autenticar bajo autoridad previa genuina todos los autores/providers/preparadores conocidos y revisores R03/R06/R08 con competencia/appointments/independencia/exclusiones reales. No se realiza enrollment o nominación aquí. I262 documental no acepta A05; W10 o futuras firmas CE10 no pueden ser su única autenticación retrospectiva.'),
    ('RJ02','Cinco obligaciones y veinte disposiciones de criterio',
     ['resource_obligation_ledger','criterion_revalidation_ledger','resource_premise_handoff'],
     'Entregar dictamen genuino por E01-E05 y por sus cuatro criterios I131 revalidados sobre el sucesor efectivo: aplicabilidad,mismo scope,cuerpos/bytes/digests/autores/providers/custodia,derivaciones/unidades/todos supuestos/validez y reviews/decisión con motivo. No transferir resultados históricos,ni presentar criterio/obligación parcial positivo como cierre conjunto. Cada premisa de fuentes/W04-capacidad-servicio/W05-W08 completos debe estar disponible y compatible.'),
    ('RJ03','BASIS,índice y siete tipos de pruebas previas',
     ['prior_proof_boundary','profile_proof_requirements','contract_rule_requirements'],
     'Aportar cuerpos auténticos BASIS/resource index/registry/contract y bindings exactos a seis fuentes/runtime/scope y sus bytes/hashes/provenance. Siete tipos del índice E01-E05 con reviewer R03_RESOURCES y CP03/ATOMICITY con R06_ADMISSION_REVIEWER; BASIS tiene revisión propia R06, no es octava prueba del índice. review_record_id debe identificar review genuino aceptado de rol/scope exacto. Derivaciones autocontenidas completas bajo32768 o rechazar/revisar grafo, sin truncar/esconder futuras lecturas o usar strings/flags/firmas como prueba.'),
    ('RJ04','Compatibilidad conjunta de scope,unidades y premisas',
     ['resource_premise_handoff','resource_and_reserve_boundary','profile_proof_requirements'],
     'Entregar derivación global que reconcilie fuente/imagen/runtime/loader/crypto/caller/platform/ledger y procesos/hilos/hijos; once owners/vidas/native/allocator/GC/requested-committed/capacidad; all30 trabajo/CPU/IO/unidades/servicio o WCET; clock/cache/load/memory/windows/backlog/readiness/concurrencia/delays; fases t0/tR/exactTrue tW/tF con pre-tR worker,exit observation y finally/dual writes/éxito-liveness. No CPU sum como wall,unknown=0,resta overlap sin prueba,budget/watchdog como900 ni subbound histórico como fit/inviabilidad. Reservas y cuotas conservadas.'),
    ('RJ05','Reviews R03/R06 y decisión separada R08',
     ['role_and_identity_boundary','exit_predicate_dispositions','authority_boundary'],
     'Aportar reviews genuinas competentes R03/R06 y decisión separada R08 con autores/eligibilidad/authority/scope/cuerpos/validez y motivo por criterio/obligación/binding/derivación. Reconciliar todos los supuestos y pruebas previas aceptadas antes de considerar aceptación conjunta. Mismo asistente/preparador no aporta independencia; ningún autor/provider se autoasigna review o aceptación. Falta de material/autoridad/independencia conserva SD08 y no admisión.'),
    ('RJ06','Inventario completo y coste de referencias',
     ['evidence_package_requirements','resource_premise_handoff','final_binding_boundary','authority_boundary'],
     'Entregar inventario real completo por instancia faltante/aportada/rechazada/aceptada,con cuerpos disponibles/locators inmutables/bytes/digests/autores/providers/custodia/provenance/validez/invalidation. Las69 plantillas históricas y siete tipos de prueba no son conteos de cuerpos únicos. Ambos Readers y join global incluyen lookup/freshness/identity/crypto/native/IO/copias/registry/ledger/frames/recibo/dual outputs/fallos/cleanup. No nuevo runtime schema/Reader member/output/archivo oculto o coste offline gratuito. Los bindings finales B01-B04 siguen sin producirse o ejecutarse.'),
    ('RJ07','Gaps,dictamen negativo y trabajo separado',
     ['resource_obligation_ledger','prior_proof_boundary','phase_handoff','authority_boundary'],
     'Si falta cuerpo/autor/provider/custodia/scope/premisa/review o independencia, registrar requisito/instancia/dependientes y motivo negativo/pending; conservar SD08 y no admisión sin parcial positivo como cierre. Indicar trabajo/autoridad exactos separados necesarios, sin ejecutarlos,nominar/contactar,provisionar,firmar/verificar crypto,configurar/probar o cambiar cuotas/reservas. No reportar gap como aceptación o inviabilidad global.')]
CRITERIA = [
    ('AC01','A02-A05/W02-W08 genuinos con A01 conservado,mismo scope; revisiones documentales no aceptan antecedentes ni autorizan envío.',['RJ01']),
    ('AC02','Todos los autores/providers/preparadores y actores de review auténticos/enrolled/competentes/appointed antes W09,exclusiones reales sin asistente/Git/strings como personas.',['RJ01','RJ05']),
    ('AC03','Cinco obligaciones completas y veinte criterios con aplicabilidad revalidada,motivos,cuerpos/unidades/todos supuestos,sin transferencia I131/histórica.',['RJ02']),
    ('AC04','E01 entorno/clausura y plataforma compatibles; E02 once owners/vidas/allocator y fit/capacidad; E03 trabajo/WCET exacto completo.',['RJ02','RJ04']),
    ('AC05','E04 servicio/unidades/clock/demoras genuinos; E05 fases/éxito-liveness con E03/E04 completos,no watchdog/budget/elapsed como900.',['RJ02','RJ04']),
    ('AC06','BASIS/index/registry/contract y seis fuentes enlazan bytes/hashes/scope efectivos completos,sin bindings futuros o placeholders.',['RJ03']),
    ('AC07','Siete tipos E01-E05 R03 y CP03/ATOMICITY R06; BASIS review propio R06,review_record_ids genuinos de rol/scope exacto,aceptación separada R08.',['RJ03','RJ05']),
    ('AC08','Pruebas autocontenidas completas caben32768 o se rechaza/revisa grafo,sin truncar o futura lectura oculta,caps no prueba de recursos.',['RJ03','RJ06']),
    ('AC09','Join mismo source/runtime/image/caller/platform/resource/epoch/policy y procesos,memory/cache/load/units/windows/delays/validez reconciliados.',['RJ04']),
    ('AC10','Heap/requested/committed/capacidad,all30 trabajo/CPU/espera/servicio y fases completos,unknown no cero y overlap no restado sin prueba.',['RJ04']),
    ('AC11','Autores/baseline previos auténticos; W10 finaliza mismos hechos,sin backward dependency o CE10/root como única autenticación.',['RJ01','RJ05']),
    ('AC12','Reviews R03/R06 y R08 genuino separado sobre cuerpos/scope exactos con motivos; ningún parcial positivo o documento/hash/flag como aceptación conjunta.',['RJ02','RJ05']),
    ('AC13','Inventario real completo de instancias/cuerpos/provenance,69templates/7tipos no cuerpos únicos; costes ambos Readers/join íntegros sin gratis offline.',['RJ06']),
    ('AC14','Cambio de autor/body/source/runtime/platform/capacity/service/unit/load/epoch/key/policy invalida afectados; no transferencia automática o rebind activo.',['RJ01','RJ04','RJ06']),
    ('AC15','Gap/falta de autoridad/independencia mantiene SD08/no admisión,trabajo separado sin ejecución/probe/contacto/crypto/configuración/cuota/reserva.',['RJ07']),
    ('AC16','Sólo A06 genuino permite considerar A07 con A02/A04;W10/W11/W12/W13/CE12 no creados/aceptados ni cierre D5/ejecución automáticos.',['RJ05','RJ07'])]


def build_candidate():
    plan,acq,w=rd(PLAN),rd(ACQUISITION),rd(W09);lot,req=acq['acquisition_lots'][5],plan['work_packages'][8]
    assert lot['depends_on_lots']==['A02','A03','A04','A05'] and req['depends_on']==['W%02d'%i for i in range(2,9)]
    pins={**rd(PRIOR_RECON)['input_pins'],**{path:sha(path) for path in sorted(PRIOR_FILES)}}
    assert len(pins)==1112
    return dict(schema='d5.i263-a06-rq06-documentary-preparation.v1',increment='I263',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        dossier_id='PGE251-A06-RQ06-CANDIDATE-01',lot_id='A06',request_id='RQ06',work_package='W09',planned_deliverable_id=req['deliverable_id'],
        kind='CONDITIONAL_LOCAL_UNSENT_REQUEST_FOR_GENUINE_INDEPENDENT_JOIN_DECISIONS_NOT_ACTUAL_REVIEW_PROOF_RESOURCE_ACCEPTANCE_OR_RUNTIME_RECORD',
        status='A06_RQ06_DOCUMENTARY_PREPARED_PREDECESSORS_UNACCEPTED_SD01_ACTIVE_NOT_ACCEPTED_NOT_ADMITTED',input_pins=pins,
        acquisition_lot_binding=pin(ACQUISITION,'/acquisition_lots/5'),exact_acquisition_lot=lot,W09_requirement_binding=pin(PLAN,'/work_packages/8'),
        exact_W09_requirement=req,W09_documentary_checklist=pin(W09),prior_A05_review=pin(PRIOR_REVIEW),
        dependency_gate=dict(required_lot_ids=lot['depends_on_lots'],required_work_package_ids=req['depends_on'],source=pin(W09,'/dependency_gate'),
            exact_requirement=w['dependency_gate'],A05_state_source=pin(A05,'/current_effect'),exact_prior_effect=rd(A05)['current_effect'],
            A01_accepted=False,A02_accepted=False,A03_accepted=False,A04_accepted=False,A05_accepted=False,SD01_stop_active=True,
            actual_genuine_antecedent_acceptance_bodies=None,no_documentary_PASS_as_genuine_antecedent=True,
            no_send_contact_nomination_positive_intake_or_real_joint_decision_from_this_preparation=True),
        unsent_request=dict(original_draft=lot['unsent_request_draft'],subject='RQ06 — Decisión independiente E01-E05/BASIS/índices / W09 / PGO181 candidato02',
            recipient_role_only=lot['intended_recipient_role_kind'],
            reviewable_request_text='Borrador condicionado a A02-A05 genuinamente aceptados. Aportar RJ01-RJ06: todos los autores/providers/preparadores y baseline previamente autenticados,cinco obligaciones y veinte criterios revalidados con todos los cuerpos/supuestos,compatibilidad conjunta y BASIS/index/registry/contract/siete tipos de prueba efectivos. R03 revisa E01-E05,R06 CP03/ATOMICITY/BASIS,con review_record_ids auténticos y R08 elegible separado que decide por criterio/obligación y sobre join completo. No usar W10 o firmas futuras CE10 como única autenticación retrospectiva. Pruebas completas autocontenidas bajo32768 o rechazar/revisar grafo,sin truncar/coste offline gratis/lecturas ocultas. Si falta evidencia o independencia,RJ07/SD08 y no admisión;no parcial positivo como cierre. No se solicita ejecutar,cualificar,medir,probar,contactar,nominar,firmar/verificar crypto o configurar nada,ni cambiar cuotas/reservas. Antecedentes siguen sin aceptar y RQ06 no se envía.',
            required_return_ids=[r[0] for r in RETURNS],is_draft_only=True,sent=False,contact_authorized=False,
            actual_recipient_persons=None,actual_addresses_or_channels=None,actual_contact_authority=None,actual_delivery_or_receipt=None),
        requested_returns=[dict(id=rid,title=title,requirements=text,W09_requirement_sources=[pin(W09,'/'+key) for key in sections],
            universal_delivery_source=pin(ACQUISITION,'/evidence_delivery_contract'),actual_body_inventory=None,actual_received=False,
            actual_primary_reviews=None,actual_separate_acceptance=None,accepted=False) for rid,title,sections,text in RETURNS],
        role_evidence_requests=[dict(id=row['id'],source=pin(W09,'/role_scope_matrix/'+str(i)),exact_role_requirement=row,
            required_return_ids=['RJ01','RJ05'],actual_canonical_human_authority_competence_appointment_or_independence=None,
            actual_genuine_review_or_separate_decision=None,accepted=False) for i,row in enumerate(w['role_scope_matrix'])],
        obligation_decision_requests=[dict(id=row['id'],source=pin(W09,'/resource_obligation_ledger/'+str(i)),
            exact_plan_requirement=row['exact_plan_requirement'],criterion_ids=row['criterion_ids'],required_return_ids=['RJ02','RJ04','RJ05'],
            actual_complete_same_scope_bound_bodies_units_all_assumptions_or_provenance=None,
            actual_R03_R06_primary_reviews=None,actual_R08_separate_decision=None,accepted=False,closed=False)
            for i,row in enumerate(w['resource_obligation_ledger'])],
        resource_criterion_requests=[dict(id=row['id'],obligation=row['obligation'],source=pin(W09,'/criterion_revalidation_ledger/'+str(i)),
            exact_plan_requirement=row['exact_plan_requirement'],required_disposition=row['required_disposition'],required_return_ids=['RJ02','RJ05'],
            actual_applicability_derivation_units_bodies_scope_author_provider_custody_or_validity=None,
            actual_R03_R06_primary_reviews=None,actual_R08_separate_decision=None,
            current_disposition='PENDING_REVALIDATION_GENUINE_MATERIAL_AND_COMPETENT_DECISION',accepted=False,closes_resource_obligation=False)
            for i,row in enumerate(w['criterion_revalidation_ledger'])],
        proof_kind_requests=[dict(kind=row['kind'],source=pin(W09,'/prior_proof_boundary/required_proof_kind_ledger/'+str(i)),
            required_reviewer_role=row['required_reviewer_role'],required_return_ids=['RJ03','RJ05'],
            actual_complete_self_contained_derivation_body_bytes_digest_scope_or_assumptions=None,
            actual_author_provider_custody_currentness_or_genuine_review_record_id=None,accepted=False)
            for i,row in enumerate(w['prior_proof_boundary']['required_proof_kind_ledger'])],
        basis_index_request=dict(source=pin(W09,'/prior_proof_boundary'),exact_requirement=w['prior_proof_boundary'],
            basis_reviewer_role=w['prior_proof_boundary']['basis_reviewer_role'],
            BASIS_is_separate_review_not_eighth_index_proof=True,seven_types_not_actual_or_unique_body_count=True,
            actual_BASIS_resource_index_registry_contract_bodies_bytes_digests_or_cross_bindings=None,
            actual_BASIS_R06_review_or_prior_proof_acceptances=None,accepted=False),
        inherited_policies={key:dict(source=pin(W09,'/'+key),exact_requirement=w[key]) for key in
            ['role_and_identity_boundary','evidence_package_requirements','contract_rule_requirements','profile_proof_requirements',
             'resource_premise_handoff','resource_and_reserve_boundary','phase_handoff','final_binding_boundary','authority_boundary','preserved_scope_and_gates']},
        critical_boundaries=dict(
            every_actual_author_provider_preparer_and_baseline_authentic_before_W09_not_future_W10_CE10=True,
            actual_R03_R06_competence_appointments_and_R08_separation_required_not_assistant_Git_labels=True,
            all5_obligations_all20_criteria_revalidated_same_scope_with_all_bodies_units_assumptions=True,
            no_partial_positive_test_flag_signature_hash_or_documentary_PASS_as_joint_closure=True,
            E01_E05_index_reviews_R03_CP03_ATOMICITY_and_BASIS_R06_genuine_review_record_ids=True,
            seven_index_proof_types_plus_separate_BASIS_not_eight_index_records_or_unique_body_count=True,
            exact_registry_contract_index_basis_six_sources_runtime_bindings_no_future_payload_root_claim=True,
            full_self_contained_derivations_fit32768_or_reject_review_graph_never_truncate_hide_reads_or_raise_quota=True,
            all11_heap_lives_allocator_capacity_and_all30_work_units_service_WCET_and_ordered_success_phases_required=True,
            CPU_sum_not_wall_unknown_not_zero_overlap_not_subtracted_without_proof_no_budget_watchdog_as900=True,
            worker_pre_tR_exit_to_exact_True_tW_finally_to_tF_and_liveness_required_not_all_failures900=True,
            both_Readers_and_all_lookup_freshness_identity_crypto_native_IO_copies_ledger_receipt_outputs_failures_in_join=True,
            W10_final_freeze_same_facts_not_reverse_dependency_or_retroactive_authentication=True,
            W11_C_W12_bundle_mapping_W13_gates_and_CE12_not_accepted_or_created_by_A06=True,
            no_new_runtime_schema_Reader_member_hidden_file_helper_channel_output_or_free_offline_work=True,
            no_contact_nomination_enrollment_crypto_verification_signing_probe_component_execution_or_configuration=True),
        decision_workflow_requirements=dict(
            ordered_steps=['Check genuine prerequisites,complete bodies/refs and prior actor/baseline authentication with eligible roles.',
                'Revalidate applicability and exact successor derivations for every20 criteria and5 obligations;record traceable missing/rejected/provided dispositions.',
                'R03/R06 review resources/compatibility and exact prior proof/BASIS role bindings under their own genuine authority.',
                'R08 eligible separate decides per criterion/obligation/proof and complete joint scope with real reasons/bodies;no assistant-made decision.',
                'Only with every requirement and all assumptions genuinely satisfied may competent joint acceptance be considered;otherwise preserve negative/pending SD08.',
                'Reconcile currentness,changes and downstream impact;W10 later finalizes same facts under its own genuine requirements.'],
            primary_review_roles=req['primary_review_roles'],separate_acceptor_role=req['separate_acceptor_role'],
            incomplete_body_author_provider_scope_assumption_or_independence_keeps_SD08=True,
            actual_criterion_decisions=None,actual_obligation_decisions=None,actual_aggregate_decision=None,
            actual_independent_joint_review_or_acceptance_performed=False,obligations_closed=0),
        material_routes=dict(existing_material=dict(required_returns=['RJ%02d'%i for i in range(1,7)],actual_delivery_inventory=None,actual_route_accepted=False),
            missing_material=dict(required_return_id='RJ07',SD08_stop_if_body_author_provider_scope_assumption_or_independence_missing=True,
                gap_not_acceptance_no_partial_positive_as_complete_join=True,
                separately_scoped_work_authority_required_no_operational_action_from_plan=True,
                no_infeasibility_or_global_absence_inferred_from_missing_material=True,
                actual_gap_report=None,actual_new_action_authority=None,actual_work_performed=False)),
        W09_deliverable_coverage=[dict(id='WD%02d'%(i+1),source=pin(PLAN,'/work_packages/8/deliverables/'+str(i)),exact_requirement=text,
            required_return_ids=[['RJ02','RJ04','RJ05'],['RJ03','RJ05','RJ06'],['RJ01','RJ05']][i],
            actual_complete_delivery=None,accepted=False) for i,text in enumerate(req['deliverables'])],
        intake_acceptance_checklist=[dict(id=cid,criterion=text,required_return_ids=ids,actual_evidence_inventory=None,
            actual_R03_R06_primary_reviews=None,actual_R08_separate_decision=None,
            disposition='PENDING_PREDECESSORS_GENUINE_COMPLETE_PROOFS_AND_INDEPENDENT_DECISIONS',accepted=False)
            for cid,text,ids in CRITERIA],
        W09_exit_coverage=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/8/exit_predicates/'+str(i)),exact_predicate=text,
            required_intake_criteria=[c[0] for c in CRITERIA],required_resource_criterion_ids=[r['id'] for r in w['criterion_revalidation_ledger']],
            actual_genuine_disposition=None,accepted=False) for i,text in enumerate(req['exit_predicates'])],
        actual_material_state=dict(actual_received_inventory=None,provided_real_bodies=[],rejected_real_bodies=[],actual_evaluations=0,
            actual_provider_or_schedule=None,actual_independent_people_appointments_or_review_records=None,
            actual_positive_BASIS_index_proof_body_or_resource_decision_created=False,
            actual_operational_verification_execution_or_probe_performed=False),
        preserved_resource_rules=dict(source=pin(ACQUISITION,'/preserved_resource_and_cost_rules'),exact_requirement=acq['preserved_resource_and_cost_rules'],
            all_scope_assumptions_bounds_capacity_service_and_reference_costs_must_reconcile=True,
            no_quota_budget_reserve_transfer_or_resource_reservation_applied=True),
        handoff=dict(exact_A06_completion_predicate=lot['completion_predicate'],exact_A06_missing_stop=lot['missing_or_failure_stop'],
            next_lot='A07',required_genuine_prior_lots=['A02','A04','A06'],A07_or_RQ07_started_sent_or_accepted=False,
            actual_A06_completion_or_independent_acceptance=None,actual_W10_W13_C_bundle_mapping_or_final_route_created=False,
            final_route_source=pin(PLAN,'/prelaunch_handoff_and_CE12'),exact_final_route_boundary=plan['prelaunch_handoff_and_CE12'],
            no_final_E06_payload_Q_root_admission_claim_receipt_as_new_prelaunch_condition=True,
            no_automatic_certificate_PJC115_R2_execution_or_D5_release=True),
        change_control=dict(source=pin(W09,'/phase_handoff'),exact_requirement=w['phase_handoff'],
            changed_author_body_source_runtime_caller_platform_resource_units_service_load_epoch_key_policy_invalidates_affected_reviews=True,
            no_automatic_old_proof_approval_or_acceptance_transfer=True,actual_refresh_or_active_rebind=False),
        current_effect={**rd(A05)['current_effect'],'A06_RQ06_documentary_prepared':True,'A06_accepted':False,'RQ06_sent':False,
            'actual_independent_joint_E01_E05_BASIS_index_acceptance_created':False,'actual_A06_intake_progress_or_review_records_created':False},
        producer=dict(identity='Same Codex assistant/chat as I261/I262',documentary_preparer_only=True,actor_independent=False,
            competent_R03_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_independent_decision_prior_proof_resource_acceptance_authority_execution_or_D5_closure=True))


NEGATIVE_CASES = [
    ('A05_promoted',('dependency_gate','A05_accepted'),False,True),('SD01_bypassed',('dependency_gate','SD01_stop_active'),True,False),
    ('PASS_as_antecedent',('dependency_gate','no_documentary_PASS_as_genuine_antecedent'),True,False),
    ('request_sent',('unsent_request','sent'),False,True),('contact_granted',('unsent_request','contact_authorized'),False,True),
    ('reviewers_invented',('unsent_request','actual_recipient_persons'),None,['UNVERIFIED_TEST_LABEL']),
    ('material_received',('requested_returns',1,'actual_received'),False,True),
    ('actor_invented',('role_evidence_requests',0,'actual_canonical_human_authority_competence_appointment_or_independence'),None,{}),
    ('obligation_closed',('obligation_decision_requests',0,'closed'),False,True),
    ('criterion_accepted',('resource_criterion_requests',19,'accepted'),False,True),
    ('proof_created',('proof_kind_requests',0,'actual_complete_self_contained_derivation_body_bytes_digest_scope_or_assumptions'),None,{}),
    ('BASIS_accepted',('basis_index_request','accepted'),False,True),
    ('BASIS_as_eighth_proof',('basis_index_request','BASIS_is_separate_review_not_eighth_index_proof'),True,False),
    ('late_authentication',('critical_boundaries','every_actual_author_provider_preparer_and_baseline_authentic_before_W09_not_future_W10_CE10'),True,False),
    ('assistant_as_reviewer',('critical_boundaries','actual_R03_R06_competence_appointments_and_R08_separation_required_not_assistant_Git_labels'),True,False),
    ('partial_positive_as_join',('critical_boundaries','no_partial_positive_test_flag_signature_hash_or_documentary_PASS_as_joint_closure'),True,False),
    ('proof_role_waived',('critical_boundaries','E01_E05_index_reviews_R03_CP03_ATOMICITY_and_BASIS_R06_genuine_review_record_ids'),True,False),
    ('future_binding_allowed',('critical_boundaries','exact_registry_contract_index_basis_six_sources_runtime_bindings_no_future_payload_root_claim'),True,False),
    ('truncation_allowed',('critical_boundaries','full_self_contained_derivations_fit32768_or_reject_review_graph_never_truncate_hide_reads_or_raise_quota'),True,False),
    ('unknown_zero',('critical_boundaries','CPU_sum_not_wall_unknown_not_zero_overlap_not_subtracted_without_proof_no_budget_watchdog_as900'),True,False),
    ('exit_as_tW',('critical_boundaries','worker_pre_tR_exit_to_exact_True_tW_finally_to_tF_and_liveness_required_not_all_failures900'),True,False),
    ('offline_costs_free',('critical_boundaries','both_Readers_and_all_lookup_freshness_identity_crypto_native_IO_copies_ledger_receipt_outputs_failures_in_join'),True,False),
    ('W10_as_prior_authentication',('critical_boundaries','W10_final_freeze_same_facts_not_reverse_dependency_or_retroactive_authentication'),True,False),
    ('operational_verification_authorized',('critical_boundaries','no_contact_nomination_enrollment_crypto_verification_signing_probe_component_execution_or_configuration'),True,False),
    ('actual_aggregate_decision',('decision_workflow_requirements','actual_aggregate_decision'),None,'UNVERIFIED_TEST_LABEL'),
    ('joint_review_performed',('decision_workflow_requirements','actual_independent_joint_review_or_acceptance_performed'),False,True),
    ('SD08_waived',('material_routes','missing_material','SD08_stop_if_body_author_provider_scope_assumption_or_independence_missing'),True,False),
    ('gap_as_authority',('material_routes','missing_material','actual_new_action_authority'),None,'UNVERIFIED_TEST_LABEL'),
    ('existing_material_accepted',('material_routes','existing_material','actual_route_accepted'),False,True),
    ('intake_criterion_accepted',('intake_acceptance_checklist',11,'accepted'),False,True),('exit_accepted',('W09_exit_coverage',0,'accepted'),False,True),
    ('inventory_fabricated',('actual_material_state','actual_received_inventory'),None,[]),
    ('positive_prior_proofs_created',('actual_material_state','actual_positive_BASIS_index_proof_body_or_resource_decision_created'),False,True),
    ('quota_changed',('preserved_resource_rules','no_quota_budget_reserve_transfer_or_resource_reservation_applied'),True,False),
    ('A07_started',('handoff','A07_or_RQ07_started_sent_or_accepted'),False,True),
    ('final_route_as_prelaunch_condition',('handoff','no_final_E06_payload_Q_root_admission_claim_receipt_as_new_prelaunch_condition'),True,False),
    ('old_acceptance_transferred',('change_control','no_automatic_old_proof_approval_or_acceptance_transfer'),True,False),
    ('A06_accepted',('current_effect','A06_accepted'),False,True),('D5_closed',('current_effect','D5_closed'),False,True),
    ('assistant_independent',('producer','actor_independent'),False,True)]


def validate(d):
    for name,path,expected,_ in NEGATIVE_CASES:
        node=d
        for key in path:
            node=node[key]
        assert type(node) is type(expected) and node==expected,name
    assert d==build_candidate(),'A06/RQ06 differs from exact documentary reconstruction'
    pointers(d)


def rejection_checks(d):
    results=[]
    for name,path,_,value in NEGATIVE_CASES:
        mutant=copy.deepcopy(d);node=mutant
        for key in path[:-1]:
            node=node[key]
        node[path[-1]]=value
        try:
            validate(mutant)
        except AssertionError as error:
            assert str(error)==name,(name,str(error))
            results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return results


def build_review():
    d=rd(SUBJECT);validate(d);verify_blobs(d['input_pins'])
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));exists=Path.exists
    rec=previous['reconstruct']()
    assert rec==rd(PRIOR_RECON) and previous['build_review'](rec)==rd(PRIOR_REVIEW)
    assert Path.exists is exists
    w=rd(W09);req=rd(PLAN)['work_packages'][8]
    assert [r['id'] for r in d['role_evidence_requests']]==['R03','R06','R08']
    assert [r['id'] for r in d['obligation_decision_requests']]==['E%02d'%i for i in range(1,6)]
    assert len(d['resource_criterion_requests'])==20
    for obligation in d['obligation_decision_requests']:
        expected=[r['id'] for r in d['resource_criterion_requests'] if r['obligation']==obligation['id']]
        assert len(expected)==4 and obligation['criterion_ids']==expected
        assert obligation['exact_plan_requirement']==fragment(obligation['source'])['exact_plan_requirement']
    kinds=d['proof_kind_requests']
    assert [r['kind'] for r in kinds]==['E01','E02','E03','E04','E05','CP03','ATOMICITY']
    assert [r['required_reviewer_role'] for r in kinds]==['R03_RESOURCES']*5+['R06_ADMISSION_REVIEWER']*2
    assert d['basis_index_request']['basis_reviewer_role']=='R06_ADMISSION_REVIEWER'
    assert len(d['requested_returns'])==7 and len(d['intake_acceptance_checklist'])==16
    assert len(d['W09_deliverable_coverage'])==len(d['W09_exit_coverage'])==3
    assert d['decision_workflow_requirements']['primary_review_roles']==req['primary_review_roles']==['R03','R06']
    assert d['decision_workflow_requirements']['separate_acceptor_role']==req['separate_acceptor_role']=='R08'
    assert len(d['inherited_policies']['role_and_identity_boundary']['exact_requirement']['separation_matrix'])==14
    assert d['handoff']['required_genuine_prior_lots']==rd(ACQUISITION)['acquisition_lots'][6]['depends_on_lots']
    sources=rd(P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json')['$defs']['source_bindings']['required']
    assert all(not (ROOT/path).exists() for path in sources)
    bindings=rd(P+'D5-I193-CE11-PRELAUNCH-EVIDENCE-CLOSURE-REVIEW-CANDIDATE.json')['pending_I177_final_bindings']
    assert all(not (ROOT/r['path']).exists() for r in bindings)
    return dict(schema='d5.i263-preparation-review.v1',increment='I263',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,candidate=pin(SUBJECT),
        counts=dict(input_pins=1112,required_predecessor_lots=4,required_predecessor_work_packages=7,review_roles=3,separation_requirements=14,
            resource_obligations=5,resource_criteria=20,index_proof_kinds=7,separate_BASIS_review_requirements=1,requested_returns=7,intake_criteria=16,
            W09_deliverables=3,W09_exits=3,actual_received_bodies=0,actual_independent_decisions=0,actual_lots_accepted=0,resource_obligations_closed=0),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        source_reconstruction=dict(I262_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        limitations=['A02-A05 and inherited A01 remain unaccepted,SD01 active. Conditional unsent request only; no actual independent review or joint resource decision.',
            'Five obligations/twenty criteria and seven index proof kinds plus BASIS require complete exact bodies,units,assumptions,custody and genuine R03/R06/R08 records. All actual material remains missing.',
            'Prior author/baseline authentication cannot be deferred to W10 or future CE10 approvals. Incomplete evidence/independence keeps SD08; no partial positive closure or automatic certificate change.',
            'No product/component execution,operational verification,probe,contact,crypto,enrollment,configuration,claim,receipt,quota,reserve,binding or D5 change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I263-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/obligation/criterion/role checks and in-memory documentary mutations only. No target import/compile/discovery/tests/execution/build/profiling/benchmark/crypto/signing/keygen/enrollment/provisioning/contacts/platform/clock/CPU/IO/ledger/process/endpoint/replay/crash probes or configuration.',
            over400_lines=True,reason='Single conditional A06/RQ06 request with exact joint decision/prior proof requirements,pins,rejection checks and preservation; overage declared,no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_independent_decision_resource_acceptance_authority_or_execution=True))


def main():
    review=build_review();assert review==rd(PREP)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published799'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==804
    seal=rd(SEAL)
    assert seal['schema']=='d5.i263-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published804']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==review['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I263',input_pins=1112,preserved_published_files=804,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],SD01_stop_active=True,
        prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
