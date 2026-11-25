#!/usr/bin/env python3
"""I259 A04/RQ04 preparation: own documentary audit, no target execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '091586874bfc50990d4b2d66f99b548a4970281d'
DATE = '2026-11-25'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
W04 = P+'D5-I223-W04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
A03 = P+'D5-I251-A03-RQ03-SOURCES-IMAGE-RUNTIME-CANDIDATE.json'
PRIOR_RECON = P+'D5-I258-I257-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I258-I257-documentary-review.json'
PRIOR_AUDIT = P+'D5-I258-audit.py'
PRIOR_SEAL = P+'D5-I258-integrity.json'
PRIOR_DOC = 'docs/design/D5-I258-I257-A03-RQ03-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I251-A04-RQ04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
PREP = P+'D5-I259-preparation-review.json'
AUDIT = P+'D5-I259-audit.py'
SEAL = P+'D5-I259-integrity.json'
DOC = 'docs/design/D5-I259-A04-RQ04-CALLER-PLATFORM-SERVICE.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_A04_RQ04_PREPARED_PREDECESSORS_UNACCEPTED_CALLER_PLATFORM_SERVICE_MISSING_NOT_ADMITTED'


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
    ('PL01','Antecedentes y autoridad real de custodio/operador',
     ['dependency_gate','role_scope_matrix','authority_and_costs'],
     'Aportar aceptación genuina A02/W02 y A03/W03 con A01 de entrada conservado; identidad/competencia/appointment/provenance/scope/vigencia del custodio R02, operador con control real sobre garantías y revisores R03/R06/R08 elegibles. I258 documental no acepta A03. No seleccionar proveedor o iniciar contacto/intake positivo mientras falten antecedentes; una etiqueta de rol o firma sola no atesta facultad de garantizar servicio.'),
    ('PL02','Caller, constructor, dominio y origen de canales',
     ['caller_policy','requirement_phase_ledger'],
     'Aportar cuerpos genuinos existentes de requester humano y principal software distintos, caller/actor/image/domain/constructor/loader y provenance previa; mecanismo concreto de aislamiento/origen inmutable y custodia exclusiva de dos pipes/seis operandos I189. UID/PID/fd/fstat/env/module/cwd/hash/appointment o READY no constituyen capacidad. Excluir shadowing/tracing/memory/descriptor injection antes de código no confiable. No nuevo helper/canal/fd/argv/file/env, backend seleccionado o constructor invocado.'),
    ('PL03','Ocho garantías de plataforma exigibles',
     ['platform_policy'],
     'Por cada una de las ocho garantías, aportar prueba completa y disponible con mecanismo/enforcement, operador autorizado, alcance exacto source/runtime/image/caller/domain/processes, supuestos/validez/custodia y revisión. Booleanos, hashes o descripción de política no prueban garantías reales. Si no hay mecanismo intrínseco existente y evidencia propia genuina, registrar gap PL07 y mantener no admisión sin implementarlo/probarlo aquí.'),
    ('PL04','Capacidad real, servicio compatible o WCET y demoras',
     ['service_evidence_ledger','actual_capacity_state','actual_service_state','heap_metric_policy','delay_requirements','candidate_budgets'],
     'Aportar cotas inferiores atestadas de capacidad requested/committed allocator heap para runtime exacto y todos los procesos/interferencia/native/allocator/GC/vidas/overlap; no RSS/quota/reserva. Entregar unidades de trabajo/servicio compatibles, curva inferior con ventanas/backlog/readiness/concurrencia o WCET justificado de plataforma exacta, CPU frente wall y suma de procesos separados. Cubrir CPU/IO/scheduler/locks/hijos/reap/observación/retries y L01-L08, load/cache/memory/validez/supuestos y derivaciones. No MHz/benchmark/bytes/900 como servicio, ni unknown=0 o restar solapamientos sin prueba. Esto no sustituye demanda/heap/trabajo/fases completos W05-W09.'),
    ('PL05','Reloj/currentness y mecanismo global one-use durable',
     ['platform_policy','phase_boundary'],
     'Aportar dominio/reloj monotónico y UTC, error auténtico<=5, validez/currentness/epochs/revocación y cuerpos disponibles, no fecha host/TOFU/cache/fetch oculto. Probar mecanismo existente global para (trust_context_sha256,runtime_request_sha256,invocation_id) en todos callers/domains/restarts con atomicidad/high-water/durabilidad/rollback/crash/partial-claim y ledger concordante con mapping. Mecanismo no equivale a claim/mapping actuales: no probar replay/crash/claim para documentarlo. Conflicto/incertidumbre/partial gasta o rechaza sin free retry; padre/hijo son una invocación.'),
    ('PL06','Inventario íntegro y decisiones genuinas',
     ['role_scope_matrix','exit_predicate_dispositions','phase_boundary','authority_and_costs'],
     'Aportar todos los cuerpos/referencias/locators/bytes/digests/autores/providers/custodia/provenance/unidades/hipótesis y currentness bajo mismo scope. Revisiones genuinas R02/R03/R06 y decisión separada R08 con motivos por criterio/salida. Actor/image/caller/platform y capacidad/servicio auténticos antes W09; W10 no autentica retrospectivamente. Costes de ambos Readers y join global completos; no flags/caps/firmas/índices o PASS como verdad/fit.'),
    ('PL07','Gaps de garantía y alcance separado necesario',
     ['authority_and_costs','exit_predicate_dispositions','phase_boundary'],
     'Si falta autoridad, backend intrínseco, capacidad, unidad/servicio, demora, reloj o durabilidad, identificar requisito/cuerpo/scope/supuesto ausente y dependientes; conservar SD03/no admisión. Indicar trabajo y autoridad exactos separados necesarios sin ejecutarlos, seleccionar proveedor/fechas o cambiar cuotas. No probes/mediciones/configuración, operaciones de procesos/endpoints/reloj/ledger, claim o replay/crash/restart. Informe de gaps no acepta A04 ni demuestra ausencia global/inviabilidad.')]
CRITERIA = [
    ('AC01','A02/W02 y A03/W03 genuinamente aceptados, autoridad de entrada A01 conservada; revisiones documentales no antecedente positivo.',['PL01']),
    ('AC02','Custodio/operador con competencia/autoridad real sobre mecanismo/capacidad/servicio, scope/vigencia/provenance verificables; sin autodesignación.',['PL01']),
    ('AC03','Requester humano separado de software caller, identidad/actor/image/domain/constructor y provenance genuinos previos a recursos.',['PL02']),
    ('AC04','Constructor/loader/aislamiento/origen inmutable y custodia de dos pipes/seis operandos probados; UID/PID/fd/env/hash/READY/appointment solos no capacidad.',['PL02']),
    ('AC05','Las ocho garantías tienen cuerpos completos de mecanismo/enforcement/proveedor/scope/supuestos/validez; ningún booleano/hash sustituye prueba.',['PL03']),
    ('AC06','Capacidad disponible requested/committed allocator heap realmente atestada, native/GC/vidas/overlap y proceso conjunto; no RSS/quota/reserva como disponibilidad.',['PL04']),
    ('AC07','Unidad trabajo/servicio compatible y curva inferior/latencias o WCET exacto, con ventanas/load/cache/memoria/backlog/readiness/concurrencia y derivación.',['PL04']),
    ('AC08','CPU,wall y suma de procesos separados; coordinador/worker/hijos/interferencia/recursos compartidos no omitidos, no MHz/benchmark/budget como servicio.',['PL04']),
    ('AC09','L01-L08 completas, incluido exit físico→retorno exacto True de wait_worker y finally hasta tF; unknown no cero y overlap no resta sin prueba.',['PL04']),
    ('AC10','Reloj confiable monotónico/UTC/error<=5/currentness/epochs/revocación/validez, sin host date/TOFU/cache o lookup oculto.',['PL05']),
    ('AC11','Mecanismo global único C/Q/invocation entre callers/domains/restarts con atomicidad/high-water/durabilidad/rollback/crash/doble gasto y no retry incierto.',['PL05']),
    ('AC12','Mecanismo no claim actual; C W11,mapping W12,freeze W10 y claim/construcción/recibo CE12 diferidos sin dependencia inversa o permiso emitido.',['PL02','PL05']),
    ('AC13','Capacidad/servicio/scope no prueba demanda o join completo heap/trabajo/CPU/fases/900, diferido W05-W09; cuotas y reservas intactas.',['PL04','PL06']),
    ('AC14','Hechos de actor/image/caller/platform y autores/cuerpos auténticos antes W09, freeze W10 mismos hechos sin autoridad retrospectiva.',['PL01','PL06']),
    ('AC15','Cuerpos/referencias/provenance/unidades/todos supuestos y costes íntegros ambos Readers, sin caps como fit o trabajo offline gratuito.',['PL03','PL04','PL05','PL06']),
    ('AC16','Revisiones R02/R03/R06 y decisión separada R08 genuinas elegibles con motivos por requisito/salida, no este asistente como independiente.',['PL06']),
    ('AC17','Garantía/premisa no demostrada implica PL07 y SD03; no medir/probar/configurar/claim ni ampliar cuotas para rellenar expediente.',['PL07']),
    ('AC18','Cambios invalidan afectados antes de avanzar; sólo A04 genuino permite considerar A05 junto con A03, sin contacto/run ni cierre D5 automático.',['PL01','PL06','PL07'])]


def requirement_returns(row):
    if row['deferred_from_W04']:
        return []
    key=row['id']
    if key.startswith('CC'):
        return ['PL05'] if key=='CC07' else ['PL02']
    return {'PF01':['PL03'],'PF02':['PL03'],'PF03':['PL05'],'PF04':['PL05'],'PF05':['PL02','PL03'],'PF06':['PL05']}[key]


def build_candidate():
    plan,acq,w=rd(PLAN),rd(ACQUISITION),rd(W04)
    lot,req=acq['acquisition_lots'][3],plan['work_packages'][3]
    assert lot['depends_on_lots']==['A02','A03'] and req['depends_on']==['W02','W03']
    pins={**rd(PRIOR_RECON)['input_pins'],**{path:sha(path) for path in sorted(PRIOR_FILES)}}
    assert len(pins)==1092
    return dict(schema='d5.i259-a04-rq04-documentary-preparation.v1',increment='I259',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        dossier_id='PGE251-A04-RQ04-CANDIDATE-01',lot_id='A04',request_id='RQ04',work_package='W04',planned_deliverable_id=req['deliverable_id'],
        kind='CONDITIONAL_LOCAL_UNSENT_EVIDENCE_REQUEST_NOT_PLATFORM_CONTRACT_ATTESTATION_CALLER_CAPABILITY_OR_RUNTIME_RECORD',
        status='A04_RQ04_DOCUMENTARY_PREPARED_A02_A03_UNACCEPTED_SD01_ACTIVE_NOT_ACCEPTED_NOT_ADMITTED',input_pins=pins,
        acquisition_lot_binding=pin(ACQUISITION,'/acquisition_lots/3'),exact_acquisition_lot=lot,W04_requirement_binding=pin(PLAN,'/work_packages/3'),
        exact_W04_requirement=req,W04_documentary_checklist=pin(W04),prior_A03_review=pin(PRIOR_REVIEW),
        dependency_gate=dict(required_lot_ids=['A02','A03'],required_work_package_ids=['W02','W03'],
            source=pin(W04,'/dependency_gate'),exact_requirement=w['dependency_gate'],A03_state_source=pin(A03,'/current_effect'),exact_prior_effect=rd(A03)['current_effect'],
            A01_accepted=False,A02_accepted=False,A03_accepted=False,W02_accepted=False,W03_accepted=False,SD01_stop_active=True,
            actual_genuine_antecedent_acceptance_bodies=None,no_documentary_PASS_as_genuine_antecedent=True,
            no_send_contact_nomination_positive_intake_or_backend_selection_from_this_preparation=True),
        unsent_request=dict(original_draft=lot['unsent_request_draft'],subject='RQ04 — Caller y garantías exigibles de plataforma / W04 / PGO181 candidato02',
            recipient_role_only=lot['intended_recipient_role_kind'],
            reviewable_request_text='Borrador condicionado a A02/A03 genuinamente aceptados. Solicitar sólo material existente con autoridad/provenance propias PL01-PL06: caller/requester/constructor/dominio y origen intrínseco de canales; ocho garantías completas; capacidad real y servicio compatible o WCET con todas las condiciones y demoras; reloj/currentness y mecanismo global one-use/durable. Aportar cuerpos/locators/bytes/digests/autores/providers/custodia/validez, unidades y supuestos, revisiones R02/R03/R06 y decisión separada R08. Si falta garantía o backend intrínseco, PL07 y no admisión, sin suplirlo con cuota/benchmark/frecuencia/promesa. No se solicita seleccionar/implementar/probar/configurar backend, medir/probar plataforma/CPU/IO/reloj/ledger/procesos/endpoints, replay/crash/restart, claim, contacto, firma o ejecución. Recursos completos W05-W09,freeze W10,C W11,mapping W12 y claim/recibo CE12 siguen en sus fases. Los antecedentes siguen sin aceptar y RQ04 no se envía.',
            required_return_ids=[r[0] for r in RETURNS],is_draft_only=True,sent=False,contact_authorized=False,
            actual_recipient_person=None,actual_address_or_channel=None,actual_contact_authority=None,actual_delivery_or_receipt=None),
        requested_returns=[dict(id=rid,title=title,requirements=text,W04_requirement_sources=[pin(W04,'/'+key) for key in sections],
            universal_delivery_source=pin(ACQUISITION,'/evidence_delivery_contract'),actual_body_inventory=None,actual_received=False,
            actual_primary_reviews=None,actual_separate_acceptance=None,accepted=False) for rid,title,sections,text in RETURNS],
        role_evidence_requests=[dict(id=row['id'],source=pin(W04,'/role_scope_matrix/'+str(i)),exact_role_requirement=row,
            required_return_ids=['PL01','PL06'],actual_canonical_human_authority_appointment_competence_or_validity=None,
            actual_review_or_separate_acceptance=None,accepted=False) for i,row in enumerate(w['role_scope_matrix'])],
        platform_guarantee_requests=[dict(guarantee=row['guarantee'],source=pin(W04,'/platform_policy/guarantee_evidence_inventory/'+str(i)),
            schema_source=row['schema_source'],required_return_id='PL03',
            required_fields=['real mechanism/enforcement and complete proof bodies','provider competence/authority and provenance',
                'exact source/runtime/image/caller/domain/process scope','all assumptions,currentness,validity','primary reviews and separate acceptance'],
            actual_provider_mechanism_body_bytes_digest_scope_assumptions_or_validity=None,actual_verified=False,accepted=False)
            for i,row in enumerate(w['platform_policy']['guarantee_evidence_inventory'])],
        service_requests=[dict(id=row['id'],source=pin(W04,'/service_evidence_ledger/'+str(i)),normative_source=row['source'],required_material=row['required_material'],
            required_return_id='PL04',actual_provider_authority_attestation_or_bodies=None,actual_scope_unit_bound_conditions_or_derivation=None,accepted=False)
            for i,row in enumerate(w['service_evidence_ledger'])],
        delay_requests=[dict(id=row['exact_requirement']['id'],source=pin(W04,'/delay_requirements/'+str(i)),exact_requirement=row['exact_requirement'],
            required_return_id='PL04',actual_complete_delay_body_bound_scope_or_review=None,accepted=False) for i,row in enumerate(w['delay_requirements'])],
        phase_requirement_requests=[dict(id=row['id'],source=pin(W04,'/requirement_phase_ledger/'+str(i)),normative_source=row['source'],
            required_genuine_evidence=row['exact_requirement']['required_genuine_evidence'],consumer_step=row['consumer_step'],
            work_package_consumers=row['work_package_consumers'],deferred_from_A04=row['deferred_from_W04'],
            final_route_outside_prelaunch_plan=row['final_route_outside_prelaunch_plan'],required_return_ids=requirement_returns(row),
            actual_evidence_or_primary_review_or_separate_acceptance=None,accepted=False) for i,row in enumerate(w['requirement_phase_ledger'])],
        inherited_policies={key:dict(source=pin(W04,'/'+key),exact_requirement=w[key]) for key in
            ['caller_policy','platform_policy','heap_metric_policy','candidate_budgets','schema_policy','phase_boundary','authority_and_costs','preserved_scope_and_gates']},
        critical_boundaries=dict(
            caller_requester_principal_and_capability_not_UID_PID_fd_env_hash_READY_or_appointment=True,
            immutable_entry_and_exclusive_inherited_origin_before_untrusted_code_no_new_channels_helpers=True,
            all8_guarantees_require_genuine_complete_enforcement_bodies_not_boolean_or_hash=True,
            attested_available_requested_committed_heap_not_RSS_quota_virtual_reservation_or_candidate_reserve=True,
            CPU_work_service_compatible_units_or_exact_platform_WCET_not_MHz_benchmark_deadline_or_work_divided_by900=True,
            load_cache_memory_windows_backlog_readiness_concurrency_and_process_interference_explicit=True,
            all8_delay_classes_unknown_not_zero_overlap_not_subtracted_without_proof=True,
            exact_True_wait_return_tW_not_worker_physical_exit_finally_to_tF_and_pre_tR_worker_work_required=True,
            trusted_clock_error_currentness_epoch_revocation_not_host_clock_date_or_TOFU=True,
            global_ledger_across_callers_domains_restarts_atomic_durable_high_water_no_double_spend=True,
            mechanism_evidence_not_actual_claim_mapping_or_probe_parent_child_one_invocation_no_free_retry=True,
            capacity_service_premises_not_complete_program_demand_heap_work_phase_success900_or_resource_join=True,
            CC08_PF07_resources_CC09_PF08_freeze_CC10_PF09_C_CC11_PF10_mapping_CC12_PF11_claim_deferred_no_reverse_edges=True,
            genuine_actor_image_caller_platform_authors_and_bodies_before_W09_W10_not_retroactive=True,
            no_new_backend_operator_contact_crypto_provisioning_process_endpoint_clock_ledger_probe_or_configuration=True),
        material_routes=dict(existing_material=dict(required_returns=['PL01','PL02','PL03','PL04','PL05','PL06'],
            actual_delivery_inventory=None,actual_route_accepted=False),
            missing_material=dict(required_return_id='PL07',SD03_stop_if_guarantee_capacity_service_clock_durability_or_intrinsic_backend_unproved=True,
                exact_missing_body_scope_assumption_requirement_and_separate_work_authority_required=True,
                no_measurement_probe_configuration_claim_or_quota_change_to_fill_gap=True,
                gap_report_not_acceptance_or_global_infeasibility_proof=True,actual_provider_gap_report=None,
                actual_new_action_authority=None,actual_work_performed=False)),
        W04_deliverable_coverage=[dict(id='WD%02d'%(i+1),source=pin(PLAN,'/work_packages/3/deliverables/'+str(i)),exact_requirement=text,
            required_return_ids=[['PL02','PL03'],['PL04'],['PL05']][i],authority_return_id='PL01',review_return_id='PL06',
            actual_complete_delivery=None,accepted=False) for i,text in enumerate(req['deliverables'])],
        acceptance_checklist=[dict(id=cid,criterion=text,required_return_ids=ids,actual_evidence_inventory=None,
            actual_R02_R03_R06_primary_reviews=None,actual_R08_separate_decision=None,
            disposition='PENDING_A02_A03_GENUINE_GUARANTEES_AND_COMPETENT_DECISION',accepted=False) for cid,text,ids in CRITERIA],
        W04_exit_coverage=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/3/exit_predicates/'+str(i)),exact_predicate=text,
            required_acceptance_criteria=[c[0] for c in CRITERIA],actual_genuine_disposition=None,accepted=False) for i,text in enumerate(req['exit_predicates'])],
        actual_material_state=dict(actual_received_inventory=None,provided_real_bodies=[],rejected_real_bodies=[],actual_evaluations=0,
            actual_provider_operator_backend_or_service_selected=None,actual_schedule_or_duration_guarantee=None,
            actual_capacity_or_service_guarantee_verified=False,actual_clock_or_global_ledger_verified=False,
            actual_claim_mapping_replay_crash_restart_or_platform_probe_performed=False),
        preserved_resource_rules=dict(source=pin(ACQUISITION,'/preserved_resource_and_cost_rules'),exact_requirement=acq['preserved_resource_and_cost_rules'],
            all_reference_and_mechanism_costs_in_both_Readers_and_global_join_not_free_offline=True,
            no_caps_budgets_or_requested_reserve_as_actual_resource_fit_or_service_success900=True,
            no_quota_budget_reserve_transfer_or_resource_reservation_applied=True),
        handoff=dict(exact_A04_completion_predicate=lot['completion_predicate'],exact_A04_missing_stop=lot['missing_or_failure_stop'],
            next_lot='A05',required_genuine_prior_lots=['A03','A04'],A05_or_RQ05_started_sent_or_accepted=False,
            actual_A04_completion_or_independent_acceptance=None,actual_final_caller_platform_C_mapping_claim_or_receipt_created=False,
            final_route_source=pin(PLAN,'/prelaunch_handoff_and_CE12'),exact_final_route_boundary=plan['prelaunch_handoff_and_CE12'],
            prelaunch_not_conditioned_on_actual_final_E06_payload_Q_root_admission_claim_receipt=True,
            no_automatic_launch_certificate_PJC115_R2_or_D5_release=True),
        change_control=dict(source=pin(W04,'/phase_boundary'),exact_requirement=w['phase_boundary'],
            changed_operator_authority_source_runtime_caller_domain_service_load_clock_epoch_key_policy_or_body_invalidates_affected_reviews=True,
            no_automatic_old_guarantee_proof_approval_or_acceptance_transfer=True,actual_refresh_or_active_rebind=False),
        current_effect={**rd(A03)['current_effect'],'A04_RQ04_documentary_prepared':True,'A04_accepted':False,'RQ04_sent':False,
            'actual_caller_platform_capacity_service_clock_or_ledger_guarantees_accepted':False,
            'actual_backend_selected_or_platform_probed':False,'actual_A04_intake_progress_or_review_records_created':False},
        producer=dict(identity='Same Codex assistant/chat as I257/I258',documentary_preparer_only=True,actor_independent=False,
            competent_R02_R03_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_attestation_capability_authority_acceptance_execution_or_D5_closure=True))


NEGATIVE_CASES = [
    ('A02_promoted',('dependency_gate','A02_accepted'),False,True),('A03_promoted',('dependency_gate','A03_accepted'),False,True),
    ('SD01_bypassed',('dependency_gate','SD01_stop_active'),True,False),
    ('PASS_as_antecedent',('dependency_gate','no_documentary_PASS_as_genuine_antecedent'),True,False),
    ('request_sent',('unsent_request','sent'),False,True),('contact_granted',('unsent_request','contact_authorized'),False,True),
    ('operator_invented',('unsent_request','actual_recipient_person'),None,'UNVERIFIED_TEST_LABEL'),
    ('material_received',('requested_returns',3,'actual_received'),False,True),
    ('role_human_invented',('role_evidence_requests',0,'actual_canonical_human_authority_appointment_competence_or_validity'),None,{}),
    ('guarantee_verified',('platform_guarantee_requests',0,'actual_verified'),False,True),
    ('service_bound_invented',('service_requests',3,'actual_scope_unit_bound_conditions_or_derivation'),None,{}),
    ('delay_accepted',('delay_requests',4,'accepted'),False,True),
    ('fd_as_capability',('critical_boundaries','caller_requester_principal_and_capability_not_UID_PID_fd_env_hash_READY_or_appointment'),True,False),
    ('boolean_as_guarantee',('critical_boundaries','all8_guarantees_require_genuine_complete_enforcement_bodies_not_boolean_or_hash'),True,False),
    ('reserve_as_capacity',('critical_boundaries','attested_available_requested_committed_heap_not_RSS_quota_virtual_reservation_or_candidate_reserve'),True,False),
    ('MHz_as_service',('critical_boundaries','CPU_work_service_compatible_units_or_exact_platform_WCET_not_MHz_benchmark_deadline_or_work_divided_by900'),True,False),
    ('load_conditions_omitted',('critical_boundaries','load_cache_memory_windows_backlog_readiness_concurrency_and_process_interference_explicit'),True,False),
    ('delay_unknown_zero',('critical_boundaries','all8_delay_classes_unknown_not_zero_overlap_not_subtracted_without_proof'),True,False),
    ('physical_exit_as_tW',('critical_boundaries','exact_True_wait_return_tW_not_worker_physical_exit_finally_to_tF_and_pre_tR_worker_work_required'),True,False),
    ('host_clock_accepted',('critical_boundaries','trusted_clock_error_currentness_epoch_revocation_not_host_clock_date_or_TOFU'),True,False),
    ('ledger_local_only',('critical_boundaries','global_ledger_across_callers_domains_restarts_atomic_durable_high_water_no_double_spend'),True,False),
    ('mechanism_as_claim',('critical_boundaries','mechanism_evidence_not_actual_claim_mapping_or_probe_parent_child_one_invocation_no_free_retry'),True,False),
    ('service_as_full_resource_fit',('critical_boundaries','capacity_service_premises_not_complete_program_demand_heap_work_phase_success900_or_resource_join'),True,False),
    ('downstream_reverse_edge',('critical_boundaries','CC08_PF07_resources_CC09_PF08_freeze_CC10_PF09_C_CC11_PF10_mapping_CC12_PF11_claim_deferred_no_reverse_edges'),True,False),
    ('late_authentication',('critical_boundaries','genuine_actor_image_caller_platform_authors_and_bodies_before_W09_W10_not_retroactive'),True,False),
    ('platform_probe_authorized',('critical_boundaries','no_new_backend_operator_contact_crypto_provisioning_process_endpoint_clock_ledger_probe_or_configuration'),True,False),
    ('SD03_waived',('material_routes','missing_material','SD03_stop_if_guarantee_capacity_service_clock_durability_or_intrinsic_backend_unproved'),True,False),
    ('gap_as_authority',('material_routes','missing_material','actual_new_action_authority'),None,'UNVERIFIED_TEST_LABEL'),
    ('existing_material_accepted',('material_routes','existing_material','actual_route_accepted'),False,True),
    ('criterion_accepted',('acceptance_checklist',15,'accepted'),False,True),('exit_accepted',('W04_exit_coverage',0,'accepted'),False,True),
    ('inventory_fabricated',('actual_material_state','actual_received_inventory'),None,[]),
    ('backend_selected',('actual_material_state','actual_provider_operator_backend_or_service_selected'),None,'UNVERIFIED_TEST_LABEL'),
    ('claim_or_probe_done',('actual_material_state','actual_claim_mapping_replay_crash_restart_or_platform_probe_performed'),False,True),
    ('offline_costs_free',('preserved_resource_rules','all_reference_and_mechanism_costs_in_both_Readers_and_global_join_not_free_offline'),True,False),
    ('quota_changed',('preserved_resource_rules','no_quota_budget_reserve_transfer_or_resource_reservation_applied'),True,False),
    ('A05_started',('handoff','A05_or_RQ05_started_sent_or_accepted'),False,True),
    ('final_claim_created',('handoff','actual_final_caller_platform_C_mapping_claim_or_receipt_created'),False,True),
    ('final_route_as_prelaunch_condition',('handoff','prelaunch_not_conditioned_on_actual_final_E06_payload_Q_root_admission_claim_receipt'),True,False),
    ('guarantees_transferred',('change_control','no_automatic_old_guarantee_proof_approval_or_acceptance_transfer'),True,False),
    ('A04_accepted',('current_effect','A04_accepted'),False,True),('D5_closed',('current_effect','D5_closed'),False,True),
    ('assistant_independent',('producer','actor_independent'),False,True)]


def validate(d):
    for name,path,expected,_ in NEGATIVE_CASES:
        node=d
        for key in path:
            node=node[key]
        assert type(node) is type(expected) and node==expected,name
    assert d==build_candidate(),'A04/RQ04 differs from exact documentary reconstruction'
    pointers(d)


def rejection_checks(d):
    results=[]
    for name,path,_,value in NEGATIVE_CASES:
        mutant=copy.deepcopy(d); node=mutant
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
    assert [r['id'] for r in d['role_evidence_requests']]==['R02','R03','R06','R08']
    assert len(d['platform_guarantee_requests'])==8
    assert [r['id'] for r in d['service_requests']]==['SV%02d'%i for i in range(1,9)]
    assert [r['id'] for r in d['delay_requests']]==['L%02d'%i for i in range(1,9)]
    rows=d['phase_requirement_requests']; active=[r for r in rows if not r['deferred_from_A04']];deferred=[r for r in rows if r['deferred_from_A04']]
    assert len(rows)==23 and len(active)==13 and len(deferred)==10
    assert all(r['work_package_consumers']==['W04'] and r['required_return_ids'] for r in active)
    assert all(not r['required_return_ids'] for r in deferred)
    assert [r['id'] for r in rows if r['final_route_outside_prelaunch_plan']]==['CC12','PF11']
    assert len(d['requested_returns'])==7 and len(d['acceptance_checklist'])==18
    assert len(d['W04_deliverable_coverage'])==len(d['W04_exit_coverage'])==3
    assert d['handoff']['required_genuine_prior_lots']==rd(ACQUISITION)['acquisition_lots'][4]['depends_on_lots']
    sources=rd(P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json')['$defs']['source_bindings']['required']
    assert all(not (ROOT/path).exists() for path in sources)
    bindings=rd(P+'D5-I193-CE11-PRELAUNCH-EVIDENCE-CLOSURE-REVIEW-CANDIDATE.json')['pending_I177_final_bindings']
    assert all(not (ROOT/r['path']).exists() for r in bindings)
    return dict(schema='d5.i259-preparation-review.v1',increment='I259',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,candidate=pin(SUBJECT),
        counts=dict(input_pins=1092,roles=4,platform_guarantees=8,service_classes=8,delay_classes=8,phase_requirements=23,active_A04_requirements=13,
            deferred_requirements=10,final_route_requirements=2,requested_returns=7,acceptance_criteria=18,W04_deliverables=3,W04_exits=3,
            actual_guarantees_accepted=0,actual_received_bodies=0,actual_lots_accepted=0),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        source_reconstruction=dict(I258_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        limitations=['A02/A03 and inherited A01 remain unaccepted,SD01 active. Conditional unsent draft only; no positive A04 intake,caller capability,operator selection or attestation.',
            'Eight guarantees,eight service classes,eight delay classes and provider authority remain missing. Candidate budget/reserve/clock/ledger policy is not service,capacity or actual mechanism proof.',
            'Thirteen requirements apply to W04 and ten remain deferred,including two final-route requirements outside prelaunch. No reverse resource/freeze/C/mapping/claim dependency or actual claim/probe.',
            'No product/component execution,backend implementation,platform/CPU/IO/clock/ledger/process/endpoint/replay/crash probe,contact,signing,configuration,quota/reserve,binding or D5 change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I259-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage/phase checks and in-memory documentary mutations only; no target import/compile/discovery/tests/execution/build/benchmark/crypto/signing/keygen/enrollment/provisioning/contacts/platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes or configuration.',
            over400_lines=True,reason='Single conditional A04/RQ04 preparation with guarantees,service/delay and phase requirements,pins,rejection checks and preservation; overage declared,no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_attestation_authority_material_acceptance_or_execution=True))


def main():
    review=build_review();assert review==rd(PREP)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published779'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==784
    seal=rd(SEAL)
    assert seal['schema']=='d5.i259-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published784']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==review['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I259',input_pins=1092,preserved_published_files=784,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],SD01_stop_active=True,
        prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
