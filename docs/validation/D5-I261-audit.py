#!/usr/bin/env python3
"""I261 A05/RQ05 documentary preparation; no product/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'e1e4a7881313449a102f73db6f2c810f06e27803'
DATE = '2026-11-26'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
A04 = P+'D5-I251-A04-RQ04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
PRIOR_RECON = P+'D5-I260-I259-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I260-I259-documentary-review.json'
PRIOR_AUDIT = P+'D5-I260-audit.py'
PRIOR_SEAL = P+'D5-I260-integrity.json'
PRIOR_DOC = 'docs/design/D5-I260-I259-A04-RQ04-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I251-A05-RQ05-REQUALIFICATION-COMPLETE-BOUNDS-CANDIDATE.json'
PREP = P+'D5-I261-preparation-review.json'
AUDIT = P+'D5-I261-audit.py'
SEAL = P+'D5-I261-integrity.json'
DOC = 'docs/design/D5-I261-A05-RQ05-REQUALIFICATION-COMPLETE-BOUNDS.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_A05_RQ05_PREPARED_PREDECESSORS_AND_COMPLETE_DERIVATIONS_MISSING_NOT_ADMITTED'
WORKS = {
    'W05':P+'D5-I223-W05-SUCCESSOR-REQUALIFICATION-CANDIDATE.json',
    'W06':P+'D5-I223-W06-SUCCESSOR-HEAP-LIFETIMES-CANDIDATE.json',
    'W07':P+'D5-I223-W07-SUCCESSOR-WORK-CPU-UNITS-CANDIDATE.json',
    'W08':P+'D5-I223-W08-SUCCESSOR-PHASE-BOUNDS-CANDIDATE.json'}


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


SECTIONS = {
    'W05':['inherited_scope_boundary','historical_operand_obligations','historical_root_obligations','historical_group_obligations',
        'historical_atomicity_obligations','atomicity_required_reasoning','policy_obligation_ledger','new_path_family_requirements',
        'coverage_completeness','qualification_boundary','basis_index_boundary','resource_handoff','cost_and_scope_boundary','phase_and_authority_boundary'],
    'W06':['owner_derivation_ledger','historical_allocation_class_obligations','owner_overlap_obligations','inherited_reference_boundary',
        'heap_metric_policy','lifetime_and_peak_contract','new_successor_memory_requirements','successor_coverage_boundary',
        'requested_rollup','committed_rollup','candidate_budget_ledger','availability_and_fit','phase_handoff','authority_and_costs'],
    'W07':['all30_successor_correspondence','historical_activity_obligations','historical_scalar_slot_obligations',
        'historical_process_phase_vector_obligations','historical_compatibility_join_obligations','latency_owner_obligations',
        'phase_category_obligations','work_service_or_WCET_boundary','scope_and_complete_work_boundary','per_attempt_cost_ledger',
        'per_attempt_cost_boundary','actual_whole_work_and_time','service_dependency','interval_and_budget_boundary','phase_handoff','authority_boundary'],
    'W08':['authorship_boundary','historical_reference_boundary','clock_and_marker_obligations','formal_phase_algebra','phase_derivation_ledger',
        'historical_conditional_premise_obligations','successor_premise_handoff','interval_coverage','qualified_success_boundary',
        'time_and_reserve_account','watchdog_boundary','phase_handoff','authority_boundary']}
RETURNS = [
    ('RB01','Antecedentes, scope efectivo y autores auténticos',[],
     'Aportar A03/W03 y A04/W04 genuinamente aceptados con A01/A02 conservados; cuerpos/source/runtime/image/caller/platform/resource/epoch/policy exactos y autoridad/competencia/appointments/provenance de autores/providers/revisores. I260 documental no acepta A04. Todos los autores y cuerpos deben ser auténticos antes de aceptar W09; W10 no puede autenticarlos retrospectivamente. Sin antecedentes, no envío/contacto/intake positivo.'),
    ('RB02','W05: recualificación completa de operandos, raíces, atomicidad y rutas',['W05'],
     'Entregar derivaciones existentes genuinas del sucesor para179 casos,321 raíces/12 grupos/30 sitios y todas las rutas nuevas de bootstrap/custodia/crypto/Reader/salida/fallo/transitivas/procesos/hilos/hijos. Mapping completo a bytes/runtime/plataforma efectivos y pruebas de correlación metadata/carga/páginas/alias/original/fallo/publicación/locks/draft/excepciones/finalización. CP03 heredado, código escrito, diez tests/índices o certificado no transfieren aceptación. Si hay cualificación previa, exigir autoridad exacta,scope,custodia R04/review R05/provenance R06; no obtener nuevos runs o discovery aquí.'),
    ('RB03','W06: once owners, vidas, picos y heap completo',['W06'],
     'Entregar H01-H11 completos para runtime/ABI/allocator/process set exactos: inventario/cardinalidades/tamaños/vidas/picos/transitorios y originales/observer/clones/memo/frames/generadores/tracebacks/codecs/Readers/output/native/GC/destrucción/fragmentación. Incorporar132 clases históricas y55 pares de overlap como obligaciones de recualificación, no prueba. Requested H01-H10 y committed/H11 con correspondencia del mismo estado; sobreconteo conservador explícito sin omisión/crédito doble o resta de picos independientes. Comparar cotas completas/presupuestos conservados y capacidad W04 genuina; no RSS/JSON/getsizeof parcial/reserva como heap o disponibilidad.'),
    ('RB04','W07: all30, trabajo/CPU/espera y unidades compatibles',['W07'],
     'Entregar inventario y correspondencia all30 del sucesor completos bajo I193, sin inventar IDs o reducir a10 actividades/30 escalares/20 vectores. Cada actividad/proceso/fase incluye todo trabajo/CPU/IO/locks/scheduler/hijos/observación/native/GC/destrucción/crypto y ambos Readers/registry/recibo/salidas/fallos. Derivar unidades compatibles con servicio W04 o WCET exacto, ventanas/arrivals/backlog/readiness/concurrencia/load/cache/memoria/validez y todas las demoras. CPU sum,wall y espera separados; no MHz/bytes/visitas/work-over900 como servicio, ni restar overlap/latencia sin prueba.'),
    ('RB05','W08: composición de fases, éxito y 900 segundos',['W08'],
     'Con W04-W07 completos y compatibles, aportar prueba de orden t0<=tR<=tW<=tF, cobertura y derivaciones de éxito/liveness de Tpre/Tworker/Tpost bajo60/750/60 más30 conservados. tW es retorno exacto True de wait_worker,no exit físico ni validación posterior; worker pre-tR pertenece a su ventana real y exit-to-wait-return se cubre. Finally/validación/dual writes/closes hasta tF, True necesario no suficiente. La identidad telescópica y sumar presupuestos no prueban servicio/éxito/liveness; no marcador ausente=0, watchdog como éxito o garantía de toda limpieza/fallo<=900.'),
    ('RB06','Revisiones/aceptaciones propias e inventario de referencias',list(WORKS),
     'Entregar todos los cuerpos/referencias/bytes/digests/locators/autores/providers/custodia/provenance/unidades/supuestos/currentness, con reviews exactos por W05 R03/R05/R06,W06 R03,W07/W08 R03/R06 y decisiones separadas R08 genuinas sobre mismo scope. Cumplir entregables/salidas/rechazos W y costes íntegros globales sin truncar evidencia, añadir lectura oculta o tratar hash/flag/firma/typed cap como verdad. Son paquetes previos para join independiente W09/A06, no cierre automático E01-E05/BASIS.'),
    ('RB07','Gaps exactos y alcance/autoridad separados',list(WORKS),
     'Si falta derivación completa finita,compatibilidad,premisa,capacidad,servicio,vida,demora,correlación,autor o review, registrar requisito/cuerpo/scope afectado y trabajo/autoridad separados necesarios. Conservar SD04/SD05 y no admisión; no runs/profiling/WCET experimental/benchmarks/probes/firma/configuración para rellenar expediente ni cambiar cuotas/reservas. No proveedor/fecha/hash inventado, unknown=0 o gap como aceptación/inviabilidad global.')]
CRITERIA = [
    ('AC01','A03/W03 y A04/W04 genuinos y antecedentes A01/A02 conservados,scope/autores/proveedores auténticos; PASS documental no antecedente positivo.',['RB01']),
    ('AC02','Orden exacto W05 primero,W06/W07 en paralelo,W08 después; dependencias internas conservadas sin ciclo/reversa.',['RB01','RB02','RB03','RB04','RB05']),
    ('AC03','179 casos/321 raíces/12 grupos/30 sitios del sucesor con mappings y cuerpos completos; CP03/atomicidad escrita/tests históricos no transfieren.',['RB02']),
    ('AC04','Todas las rutas nuevas/transitivas/procesos/hilos/hijos/guards/Reader/output/fallo y atomicidad correlacionada efectivas cubiertas.',['RB02']),
    ('AC05','Cualificación previa sólo genuina con autoridad/custodia/review/provenance exactas; ningún run/import/discovery/cualificación nueva autorizada.',['RB02','RB07']),
    ('AC06','Once owners con allocation/cardinalidad/tamaño/vida/pico/overlap/native/GC/allocator/fallo y proceso exactos, sin omisiones o unknown=0.',['RB03']),
    ('AC07','132 clases/55 overlaps son requisitos históricos; same-state alias/lifetime o sobreconteo conservador sin merge físico/crédito doble/resta de picos.',['RB03']),
    ('AC08','Requested/committed/H11 completos se ajustan a presupuestos y capacidad W04 independiente,con reserva conservada; no RSS/serialized/partialgetsizeof como heap.',['RB03']),
    ('AC09','Correspondencia all30 genuina sobre sucesor completo;10 actividades/30escalares/20vectores no equivalen automáticamente ni se inventan IDs.',['RB04']),
    ('AC10','Trabajo/CPU/wall/espera por actividad/proceso/fase íntegros con unidades compatibles/servicio o WCET y supuestos/ventanas/delays completos.',['RB04']),
    ('AC11','Ambos Readers/lookup/freshness/identity/crypto/measurement/copias/registry/recibo/native/GC/destrucción/output/fallo dentro del join,sin costes gratis offline.',['RB02','RB03','RB04','RB06']),
    ('AC12','CPU sum,wall y servicio distintos,no conversión bytes/visitas/MHz/work-over900 ni overlap/latencia restados sin prueba.',['RB04']),
    ('AC13','t0/tR/exactTrue tW/tF ordenados,cobertura pre-tR worker,exit-to-wait-return y finally/dual writes/closes reales; identidad formal no temporalidad probada.',['RB05']),
    ('AC14','Prueba éxito/liveness con W04/W06/W07 compatibles;True no suficiente,no watchdog/elapsed/timeout/missingmarker como éxito o cero.',['RB05']),
    ('AC15','60/750/60+30=900 y600/90/60 anidados sin crédito extra/reserva prestada; no presupuesto como servicio/900 ni toda falla/cleanup acotada.',['RB03','RB04','RB05']),
    ('AC16','Autores/bodies/baseline auténticos antes W09 y W10 posterior mismos hechos,no freeze futuro como única autoridad previa.',['RB01','RB06']),
    ('AC17','Roles de review exactos por W y R08 separado genuinos competentes,con motivos por requisito/salida; mismo asistente no independiente.',['RB06']),
    ('AC18','Cuerpos/referencias/unidades/todos supuestos/currentness/validez/provenance íntegros,sin caps/flags/firmas/hashes como verdad o truncamiento.',['RB01','RB06']),
    ('AC19','Gap/prueba incompleta/overbudget mantiene SD04/SD05/no admisión; no ejecución/profiling/probe o cambio de cuotas/reservas para suplirlo.',['RB07']),
    ('AC20','Sólo A05 genuino permite considerar A06 con sus demás antecedentes;W09 join independiente,E01-E05/CE12/D5 no cerrados ni ejecución autorizada.',['RB06','RB07'])]


def build_candidate():
    plan,acq=rd(PLAN),rd(ACQUISITION);lot=acq['acquisition_lots'][4]
    docs={key:rd(path) for key,path in WORKS.items()};reqs={r['id']:r for r in plan['work_packages'][4:8]}
    assert lot['depends_on_lots']==['A03','A04'] and list(reqs)==list(WORKS)
    pins={**rd(PRIOR_RECON)['input_pins'],**{path:sha(path) for path in sorted(PRIOR_FILES)}}
    assert len(pins)==1102
    return dict(schema='d5.i261-a05-rq05-documentary-preparation.v1',increment='I261',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        dossier_id='PGE251-A05-RQ05-CANDIDATE-01',lot_id='A05',request_id='RQ05',covers_work_packages=list(WORKS),
        kind='CONDITIONAL_LOCAL_UNSENT_REQUEST_FOR_COMPLETE_EXISTING_DERIVATIONS_NOT_QUALIFICATION_RUN_OR_RESOURCE_ACCEPTANCE',
        status='A05_RQ05_DOCUMENTARY_PREPARED_A03_A04_UNACCEPTED_SD01_ACTIVE_NOT_ACCEPTED_NOT_ADMITTED',input_pins=pins,
        acquisition_lot_binding=pin(ACQUISITION,'/acquisition_lots/4'),exact_acquisition_lot=lot,prior_A04_review=pin(PRIOR_REVIEW),
        dependency_gate=dict(required_lot_ids=['A03','A04'],required_external_work_package_ids=['W03','W04'],
            A04_state_source=pin(A04,'/current_effect'),exact_prior_effect=rd(A04)['current_effect'],
            A01_accepted=False,A02_accepted=False,A03_accepted=False,A04_accepted=False,SD01_stop_active=True,
            actual_genuine_antecedent_acceptance_bodies=None,no_documentary_PASS_as_genuine_antecedent=True,
            no_send_contact_positive_intake_or_qualification_from_this_preparation=True),
        internal_work_order=dict(exact_I223_dependencies={key:req['depends_on'] for key,req in reqs.items()},
            source=pin(ACQUISITION,'/acquisition_lots/4/internal_work_dependencies'),stages=[['W05'],['W06','W07'],['W08']],
            W06_and_W07_independent_after_W05=True,W08_after_complete_W04_W05_W06_W07=True,
            actual_work_packages_accepted=0,no_reverse_W09_or_W10_acceptance_dependency=True),
        unsent_request=dict(original_draft=lot['unsent_request_draft'],subject='RQ05 — Recualificación y cotas completas / W05-W08 / PGO181 candidato02',
            recipient_role_only=lot['intended_recipient_role_kind'],
            reviewable_request_text='Borrador condicionado a A03/A04 genuinamente aceptados. Entregar derivaciones completas existentes RB01-RB06 del mismo sucesor efectivo: W05 recualificación179/321/12/30 y todas las rutas nuevas;W06 once owners/vidas/picos/allocator/native/GC y requested/committed fit;W07 all30 trabajo/CPU/wall/espera/unidades compatibles con servicio/WCET;W08 orden t0/tR/exactTrue tW/tF,éxito/liveness y60/750/60+30 conservados. Seguir W05,después W06/W07 en paralelo,finalmente W08. Aportar cuerpos completos,provenance/autores/supuestos y reviews/aceptaciones genuinos por paquete para posterior join independiente W09;no cierre automático E01-E05. Si falta prueba/premisa, RB07 y no admisión. No se solicita nueva cualificación,run,import,compile,discovery,profiling,medición/WCET experimental,benchmark,probe,contacto,firma/configuración ni cambio de cuotas/reservas. Antecedentes siguen sin aceptar y RQ05 no se envía.',
            required_return_ids=[r[0] for r in RETURNS],is_draft_only=True,sent=False,contact_authorized=False,
            actual_recipient_persons=None,actual_addresses_or_channels=None,actual_contact_authority=None,actual_delivery_or_receipt=None),
        work_package_requests=[dict(id=key,source=pin(PLAN,'/work_packages/'+str(int(key[1:])-1)),exact_requirement=req,
            documentary_checklist=pin(WORKS[key]),planned_deliverable_id=req['deliverable_id'],
            primary_review_roles=req['primary_review_roles'],separate_acceptor_role=req['separate_acceptor_role'],
            required_material_return={'W05':'RB02','W06':'RB03','W07':'RB04','W08':'RB05'}[key],
            actual_complete_derivations_or_bodies=None,actual_scope_authors_assumptions_or_reviews=None,actual_separate_acceptance=None,accepted=False)
            for key,req in reqs.items()],
        requested_returns=[dict(id=rid,title=title,requirements=text,work_package_ids=works,
            W_requirement_sources=[pin(WORKS[key]) for key in works],universal_delivery_source=pin(ACQUISITION,'/evidence_delivery_contract'),
            actual_body_inventory=None,actual_received=False,actual_primary_reviews=None,actual_separate_acceptance=None,accepted=False)
            for rid,title,works,text in RETURNS],
        derivation_scope_requirements=[dict(work_package=key,section=section,source=pin(WORKS[key],'/'+section),
            documentary_container_dimension=len(docs[key][section]),container_dimension_not_proof_count_or_complete_bound=True,
            actual_complete_same_scope_derivation_or_review=None,accepted=False)
            for key,sections in SECTIONS.items() for section in sections],
        heap_owner_requests=[dict(id=row['id'],owner=row['owner'],source=pin(WORKS['W06'],'/owner_derivation_ledger/'+str(i)),
            required_return_id='RB03',candidate_budget_bytes=row['candidate_budget_bytes'],budget_not_demand_or_capacity=True,
            actual_complete_allocation_cardinality_size_lifetime_peak_process_proof=None,actual_requested_committed_upper_or_fit=None,
            actual_R03_review_or_R08_acceptance=None,accepted=False) for i,row in enumerate(docs['W06']['owner_derivation_ledger'])],
        W07_all30_boundary=dict(source=pin(WORKS['W07'],'/all30_successor_correspondence'),exact_requirement=docs['W07']['all30_successor_correspondence'],
            no_invented_group_IDs_or_ten_activities_as_thirty_successor_groups=True,actual_successor_group_inventory_or_mapping=None,accepted=False),
        W08_phase_requests=[dict(id=row['id'],source=pin(WORKS['W08'],'/phase_derivation_ledger/'+str(i)),candidate_wall_seconds=row['candidate_wall_seconds'],
            required_return_id='RB05',actual_complete_work_service_heap_delay_coverage_order_success_or_liveness_derivation=None,
            actual_finite_wall_upper_seconds=None,actual_reviews_or_acceptance=None,accepted=False)
            for i,row in enumerate(docs['W08']['phase_derivation_ledger'])],
        critical_boundaries=dict(
            historical_counts_and_CP03_written_atomicity_tests_or_certificate_not_successor_acceptance=True,
            all_new_paths_processes_threads_children_failures_and_transitives_need_own_correlated_source_proof=True,
            originals_observer_clones_memo_frames_tracebacks_codecs_Readers_outputs_native_allocator_GC_lives_all_required=True,
            same_state_peak_alias_ownership_or_conservative_overcount_no_omission_double_credit_or_physical_witness_merge=True,
            requested_committed_H11_and_attested_capacity_distinct_no_RSS_JSON_reserve_or_partial_getsizeof_substitute=True,
            all30_successor_requirement_not_10_activities_30_scalar_slots_20_vectors_or_predictive_IDs=True,
            compatible_work_service_units_or_exact_WCET_no_bytes_visits_MHz_budget_or_work_over900_conversion=True,
            CPU_sums_wall_wait_process_windows_service_backlog_readiness_load_memory_cache_and_delays_explicit=True,
            both_Readers_and_all_original_native_crypto_ledger_receipt_output_failure_cleanup_costs_in_global_join=True,
            exact_True_wait_return_not_physical_exit_or_later_validation_worker_pre_tR_and_finally_to_tF_covered=True,
            telescoping_identity_or_sum_budgets_not_order_coverage_service_liveness_or_success900=True,
            True_necessary_not_sufficient_watchdog_elapsed_timeout_missing_marker_not_success_or_zero=True,
            no_every_failure_cleanup_deadline_claim_no_failure_traceback_cost_omission=True,
            no_extra_600_per_activity_group_process_thread_window_or_category_no_double_nested_reserve=True,
            genuine_prior_qualification_only_with_own_authority_custody_review_no_new_component_run=True,
            all_authors_bodies_and_baseline_authentic_before_W09_W10_same_facts_not_retroactive=True,
            own_W05_W08_reviews_acceptances_not_W09_joint_E01_E05_BASIS_index_closure=True,
            no_contact_profiling_experimental_WCET_benchmark_probe_import_compile_or_target_execution=True),
        material_routes=dict(existing_derivations=dict(required_returns=['RB%02d'%i for i in range(1,7)],actual_delivery_inventory=None,actual_route_accepted=False),
            missing_derivations=dict(required_return_id='RB07',SD04_SD05_stop_if_any_incomplete_unbounded_or_incompatible_term=True,
                exact_missing_term_scope_requirement_dependency_and_separate_authority_required=True,
                gap_not_acceptance_no_unknown_as_zero_or_reserve_payment=True,
                no_execution_profiling_probe_or_quota_change_to_fill_gap=True,actual_gap_report=None,actual_new_action_authority=None,actual_work_performed=False)),
        deliverable_coverage=[dict(id=key+'-D%02d'%(i+1),work_package=key,source=pin(PLAN,'/work_packages/'+str(int(key[1:])-1)+'/deliverables/'+str(i)),
            exact_requirement=text,required_material_return={'W05':'RB02','W06':'RB03','W07':'RB04','W08':'RB05'}[key],
            authority_return_id='RB01',review_return_id='RB06',actual_complete_delivery=None,accepted=False)
            for key,req in reqs.items() for i,text in enumerate(req['deliverables'])],
        acceptance_checklist=[dict(id=cid,criterion=text,required_return_ids=ids,actual_evidence_inventory=None,
            actual_competent_primary_reviews=None,actual_R08_separate_decision=None,
            disposition='PENDING_A03_A04_COMPLETE_GENUINE_DERIVATIONS_AND_COMPETENT_DECISIONS',accepted=False) for cid,text,ids in CRITERIA],
        exit_coverage=[dict(id=key+'-X%02d'%(i+1),work_package=key,source=pin(PLAN,'/work_packages/'+str(int(key[1:])-1)+'/exit_predicates/'+str(i)),
            exact_predicate=text,required_acceptance_criteria=[c[0] for c in CRITERIA],actual_genuine_disposition=None,accepted=False)
            for key,req in reqs.items() for i,text in enumerate(req['exit_predicates'])],
        actual_material_state=dict(actual_received_inventory=None,provided_real_bodies=[],rejected_real_bodies=[],actual_evaluations=0,
            actual_derivations_or_bounds_or_qualification_evidence=None,actual_provider_schedule_or_duration_guarantee=None,
            actual_qualification_execution_profiling_WCET_probe_or_clock_sampling_performed=False,actual_global_resource_fit_or_success900_verified=False),
        preserved_resource_rules=dict(source=pin(ACQUISITION,'/preserved_resource_and_cost_rules'),exact_requirement=acq['preserved_resource_and_cost_rules'],
            requested_committed_availability_service_and_demand_need_complete_same_scope_derivations=True,
            no_quota_budget_reserve_transfer_or_resource_reservation_applied=True,
            no_cap_template_hash_flag_signature_or_documentary_PASS_as_truth=True),
        handoff=dict(exact_A05_completion_predicate=lot['completion_predicate'],exact_A05_missing_stop=lot['missing_or_failure_stop'],
            next_lot='A06',required_genuine_prior_lots=['A02','A03','A04','A05'],A06_or_RQ06_started_sent_or_accepted=False,
            W09_joint_review_not_reverse_predecessor_and_not_automatically_closed=True,
            actual_A05_completion_or_independent_acceptance=None,actual_E01_E05_BASIS_index_or_atomicity_joint_acceptance=False,
            final_route_source=pin(PLAN,'/prelaunch_handoff_and_CE12'),exact_final_route_boundary=plan['prelaunch_handoff_and_CE12'],
            no_final_E06_payload_Q_root_admission_claim_receipt_as_new_prelaunch_condition=True,
            no_automatic_certificate_PJC115_R2_execution_or_D5_release=True),
        change_control=dict(source=pin(PLAN,'/scope_authentication_and_freeze_order'),exact_requirement=plan['scope_authentication_and_freeze_order'],
            changed_author_body_source_runtime_image_platform_heap_life_work_unit_service_load_epoch_key_policy_invalidates_affected_reviews=True,
            no_automatic_old_derivation_proof_approval_or_acceptance_transfer=True,actual_refresh_or_active_rebind=False),
        current_effect={**rd(A04)['current_effect'],'A05_RQ05_documentary_prepared':True,'A05_accepted':False,'RQ05_sent':False,
            'actual_complete_W05_W08_derivations_or_independent_acceptance_created':False,'actual_A05_intake_progress_or_qualification_performed':False},
        producer=dict(identity='Same Codex assistant/chat as I259/I260',documentary_preparer_only=True,actor_independent=False,
            competent_R03_R05_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_derivation_qualification_authority_resource_acceptance_execution_or_D5_closure=True))


NEGATIVE_CASES = [
    ('A03_promoted',('dependency_gate','A03_accepted'),False,True),('A04_promoted',('dependency_gate','A04_accepted'),False,True),
    ('SD01_bypassed',('dependency_gate','SD01_stop_active'),True,False),
    ('PASS_as_antecedent',('dependency_gate','no_documentary_PASS_as_genuine_antecedent'),True,False),
    ('request_sent',('unsent_request','sent'),False,True),('contact_granted',('unsent_request','contact_authorized'),False,True),
    ('providers_invented',('unsent_request','actual_recipient_persons'),None,['UNVERIFIED_TEST_LABEL']),
    ('W_package_accepted',('work_package_requests',0,'accepted'),False,True),
    ('derivation_fabricated',('work_package_requests',1,'actual_complete_derivations_or_bodies'),None,{}),
    ('scope_as_proof_count',('derivation_scope_requirements',0,'container_dimension_not_proof_count_or_complete_bound'),True,False),
    ('owner_bound_fabricated',('heap_owner_requests',3,'actual_requested_committed_upper_or_fit'),None,0),
    ('all30_mapping_fabricated',('W07_all30_boundary','actual_successor_group_inventory_or_mapping'),None,[]),
    ('phase_bound_fabricated',('W08_phase_requests',1,'actual_finite_wall_upper_seconds'),None,750),
    ('history_transferred',('critical_boundaries','historical_counts_and_CP03_written_atomicity_tests_or_certificate_not_successor_acceptance'),True,False),
    ('path_coverage_waived',('critical_boundaries','all_new_paths_processes_threads_children_failures_and_transitives_need_own_correlated_source_proof'),True,False),
    ('overlap_credit',('critical_boundaries','same_state_peak_alias_ownership_or_conservative_overcount_no_omission_double_credit_or_physical_witness_merge'),True,False),
    ('RSS_as_heap',('critical_boundaries','requested_committed_H11_and_attested_capacity_distinct_no_RSS_JSON_reserve_or_partial_getsizeof_substitute'),True,False),
    ('ten_activities_as_all30',('critical_boundaries','all30_successor_requirement_not_10_activities_30_scalar_slots_20_vectors_or_predictive_IDs'),True,False),
    ('bytes_as_seconds',('critical_boundaries','compatible_work_service_units_or_exact_WCET_no_bytes_visits_MHz_budget_or_work_over900_conversion'),True,False),
    ('original_native_costs_waived',('critical_boundaries','both_Readers_and_all_original_native_crypto_ledger_receipt_output_failure_cleanup_costs_in_global_join'),True,False),
    ('physical_exit_as_tW',('critical_boundaries','exact_True_wait_return_not_physical_exit_or_later_validation_worker_pre_tR_and_finally_to_tF_covered'),True,False),
    ('formal_identity_as_liveness',('critical_boundaries','telescoping_identity_or_sum_budgets_not_order_coverage_service_liveness_or_success900'),True,False),
    ('True_as_success',('critical_boundaries','True_necessary_not_sufficient_watchdog_elapsed_timeout_missing_marker_not_success_or_zero'),True,False),
    ('all_failures_900',('critical_boundaries','no_every_failure_cleanup_deadline_claim_no_failure_traceback_cost_omission'),True,False),
    ('extra600',('critical_boundaries','no_extra_600_per_activity_group_process_thread_window_or_category_no_double_nested_reserve'),True,False),
    ('qualification_run_granted',('critical_boundaries','genuine_prior_qualification_only_with_own_authority_custody_review_no_new_component_run'),True,False),
    ('late_authentication',('critical_boundaries','all_authors_bodies_and_baseline_authentic_before_W09_W10_same_facts_not_retroactive'),True,False),
    ('W09_closed_early',('critical_boundaries','own_W05_W08_reviews_acceptances_not_W09_joint_E01_E05_BASIS_index_closure'),True,False),
    ('gap_as_authority',('material_routes','missing_derivations','actual_new_action_authority'),None,'UNVERIFIED_TEST_LABEL'),
    ('unknown_paid_by_reserve',('material_routes','missing_derivations','gap_not_acceptance_no_unknown_as_zero_or_reserve_payment'),True,False),
    ('criterion_accepted',('acceptance_checklist',16,'accepted'),False,True),('exit_accepted',('exit_coverage',0,'accepted'),False,True),
    ('inventory_fabricated',('actual_material_state','actual_received_inventory'),None,[]),
    ('success900_verified',('actual_material_state','actual_global_resource_fit_or_success900_verified'),False,True),
    ('quota_changed',('preserved_resource_rules','no_quota_budget_reserve_transfer_or_resource_reservation_applied'),True,False),
    ('A06_started',('handoff','A06_or_RQ06_started_sent_or_accepted'),False,True),
    ('joint_acceptance_created',('handoff','actual_E01_E05_BASIS_index_or_atomicity_joint_acceptance'),False,True),
    ('CE12_precondition_added',('handoff','no_final_E06_payload_Q_root_admission_claim_receipt_as_new_prelaunch_condition'),True,False),
    ('derivation_transferred',('change_control','no_automatic_old_derivation_proof_approval_or_acceptance_transfer'),True,False),
    ('A05_accepted',('current_effect','A05_accepted'),False,True),('D5_closed',('current_effect','D5_closed'),False,True),
    ('assistant_independent',('producer','actor_independent'),False,True)]


def validate(d):
    for name,path,expected,_ in NEGATIVE_CASES:
        node=d
        for key in path:
            node=node[key]
        assert type(node) is type(expected) and node==expected,name
    assert d==build_candidate(),'A05/RQ05 differs from exact documentary reconstruction'
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
    reqs={r['id']:r for r in rd(PLAN)['work_packages'][4:8]}
    assert d['internal_work_order']['exact_I223_dependencies']==fragment(d['internal_work_order']['source'])=={key:r['depends_on'] for key,r in reqs.items()}
    assert d['internal_work_order']['stages']==[['W05'],['W06','W07'],['W08']]
    assert [r['id'] for r in d['work_package_requests']]==list(WORKS)
    for row in d['work_package_requests']:
        assert row['exact_requirement']==fragment(row['source'])==reqs[row['id']]
        assert row['primary_review_roles']==reqs[row['id']]['primary_review_roles'] and row['separate_acceptor_role']=='R08'
    assert [r['id'] for r in d['heap_owner_requests']]==['H%02d'%i for i in range(1,12)]
    assert [r['id'] for r in d['W08_phase_requests']]==['Tpre','Tworker','Tpost']
    assert len(d['requested_returns'])==7 and len(d['acceptance_checklist'])==20
    assert len(d['deliverable_coverage'])==len(d['exit_coverage'])==12
    assert len(d['derivation_scope_requirements'])==sum(map(len,SECTIONS.values()))==57
    assert d['handoff']['required_genuine_prior_lots']==rd(ACQUISITION)['acquisition_lots'][5]['depends_on_lots']
    counts={key:len(rd(WORKS[work])[section]) for key,work,section in [
        ('operand_cases','W05','historical_operand_obligations'),('roots','W05','historical_root_obligations'),('root_groups','W05','historical_group_obligations'),
        ('atomic_sites','W05','historical_atomicity_obligations'),('new_path_families','W05','new_path_family_requirements'),
        ('allocation_classes','W06','historical_allocation_class_obligations'),('owner_overlap_pairs','W06','owner_overlap_obligations'),
        ('historical_activities','W07','historical_activity_obligations'),('scalar_slots','W07','historical_scalar_slot_obligations'),
        ('process_phase_vectors','W07','historical_process_phase_vector_obligations'),('compatibility_joins','W07','historical_compatibility_join_obligations'),
        ('conditional_phase_premises','W08','historical_conditional_premise_obligations')]}
    assert counts==dict(operand_cases=179,roots=321,root_groups=12,atomic_sites=30,new_path_families=12,allocation_classes=132,owner_overlap_pairs=55,
        historical_activities=10,scalar_slots=30,process_phase_vectors=20,compatibility_joins=20,conditional_phase_premises=7)
    sources=rd(P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json')['$defs']['source_bindings']['required']
    assert all(not (ROOT/path).exists() for path in sources)
    bindings=rd(P+'D5-I193-CE11-PRELAUNCH-EVIDENCE-CLOSURE-REVIEW-CANDIDATE.json')['pending_I177_final_bindings']
    assert all(not (ROOT/r['path']).exists() for r in bindings)
    return dict(schema='d5.i261-preparation-review.v1',increment='I261',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,candidate=pin(SUBJECT),
        counts=dict(input_pins=1102,work_packages=4,scope_sections=57,heap_owners=11,phase_requests=3,requested_returns=7,acceptance_criteria=20,
            deliverables=12,exits=12,actual_received_bodies=0,actual_complete_derivations_accepted=0,actual_lots_accepted=0),
        historical_requirement_dimensions_not_actual_proof_counts=counts,rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        source_reconstruction=dict(I260_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        limitations=['A03/A04 and inherited A01/A02 remain unaccepted,SD01 active. Conditional unsent draft only; no positive A05 intake,new proof,qualification or actual acceptance.',
            'Historical179/321/12/30,132 classes/55 overlaps and10/30/20/20 dimensions are source-bound requirements,not successor coverage/fit/service/900. All actual derivations remain missing.',
            'W05 then W06/W07 parallel then W08 preserve exact roles and own acceptance. A06/W09 independent E01-E05/BASIS join remains separate and unclosed.',
            'No product/component execution,profiling,experimental WCET,probe,contact,crypto,configuration,claim,receipt,quota,reserve,binding or D5 change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I261-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage/order checks and in-memory documentary mutations only. No target import/compile/discovery/tests/execution/build/profiling/benchmark/experimental WCET/crypto/signing/keygen/enrollment/provisioning/contacts/platform/clock/CPU/IO/ledger/process/endpoint/replay/crash probes or configuration.',
            over400_lines=True,reason='Single conditional A05/RQ05 request covering four inseparable W05-W08 handoffs with source-bound derivation sections,pins,rejection checks and preservation; overage declared,no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_derivation_qualification_resource_acceptance_authority_or_execution=True))


def main():
    review=build_review();assert review==rd(PREP)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published789'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==794
    seal=rd(SEAL)
    assert seal['schema']=='d5.i261-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published794']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==review['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I261',input_pins=1102,preserved_published_files=794,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],SD01_stop_active=True,
        prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
