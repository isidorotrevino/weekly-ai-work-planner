#!/usr/bin/env python3
"""I251 genuine-evidence acquisition plan. Own documentary checks only."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '5dedb15e24656b0525af5f2921558312b55ea4a3'
DATE = '2026-11-25'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE07 = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
CE07_REVIEW = P+'D5-I212-I211-documentary-review.json'
W02 = P+'D5-I223-W02-PEOPLE-AND-ANCHORS-CANDIDATE.json'
W03 = P+'D5-I223-W03-SOURCES-IMAGE-RUNTIME-CANDIDATE.json'
W04 = P+'D5-I223-W04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
W05 = P+'D5-I223-W05-SUCCESSOR-REQUALIFICATION-CANDIDATE.json'
W06 = P+'D5-I223-W06-SUCCESSOR-HEAP-LIFETIMES-CANDIDATE.json'
W07 = P+'D5-I223-W07-SUCCESSOR-WORK-CPU-UNITS-CANDIDATE.json'
W08 = P+'D5-I223-W08-SUCCESSOR-PHASE-BOUNDS-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CUSTODY = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PROFILE = P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
W09 = P+'D5-I223-W09-E01-E05-INTEGRATION-CANDIDATE.json'
CE08 = P+'D5-I193-CE08-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json'
CE08_REVIEW = P+'D5-I214-I213-documentary-review.json'
W10 = P+'D5-I223-W10-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json'
CPACK = P+'D5-I185-PGO181-SCHEMAS-CANDIDATE-02.json'
CE09 = P+'D5-I193-CE09-EXACT-C-PROJECTION-CANDIDATE.json'
CE09_REVIEW = P+'D5-I216-I215-documentary-review.json'
W11 = P+'D5-I223-W11-EXACT-C-ACCEPTANCE-CANDIDATE.json'
CE10 = P+'D5-I193-CE10-BUNDLE-APPROVAL-AND-CURRENT-MAPPING-CANDIDATE.json'
CE10_REVIEW = P+'D5-I218-I217-documentary-review.json'
SIZE = P+'D5-I192-I191-source-reconstruction.json'
W01 = P+'D5-I223-W01-TARGET-SCOPE-AUTHORITY-CANDIDATE.json'
W12 = P+'D5-I223-W12-BUNDLE-APPROVALS-GLOBAL-MAPPING-CANDIDATE.json'
CE11 = P+'D5-I193-CE11-PRELAUNCH-EVIDENCE-CLOSURE-REVIEW-CANDIDATE.json'
CE11_REVIEW = P+'D5-I220-I219-documentary-review.json'
CHECKLIST = P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
W13 = P+'D5-I223-W13-PRELAUNCH-GATE-DECISION-CANDIDATE.json'
PRIOR_RECON = P+'D5-I250-I249-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I250-I249-documentary-review.json'
PRIOR_AUDIT = P+'D5-I250-audit.py'
PRIOR_SEAL = P+'D5-I250-integrity.json'
PRIOR_DOC = 'docs/design/D5-I250-I249-W13-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
PREP = P+'D5-I251-preparation-review.json'
AUDIT = P+'D5-I251-audit.py'
SEAL = P+'D5-I251-integrity.json'
DOC = 'docs/design/D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_I223_GENUINE_EVIDENCE_ACQUISITION_PLAN_NO_MATERIAL_OR_ACCEPTANCE_NOT_ADMITTED'
WORK_PATHS = {'W01':W01,'W02':W02,'W03':W03,'W04':W04,'W05':W05,'W06':W06,'W07':W07,'W08':W08,'W09':W09,'W10':W10,'W11':W11,'W12':W12}

WORK_PATHS['W13'] = W13


def rd(path):
    return json.loads((ROOT/path).read_text())


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def pin(path,pointer=''):
    return dict(path=path,sha256=sha(path),json_pointer=pointer)


def fragment(source):
    assert sha(source['path']) == source['sha256']
    value = rd(source['path'])
    for token in source.get('json_pointer','').split('/')[1:]:
        key = token.replace('~1','/').replace('~0','~')
        value = value[int(key)] if isinstance(value,list) else value[key]
    return value


def check_pointers(value):
    if isinstance(value,dict):
        if {'path','sha256','json_pointer'} <= set(value):
            fragment(value)
        for child in value.values():
            check_pointers(child)
    elif isinstance(value,list):
        for child in value:
            check_pointers(child)


def verify_blobs(pins):
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()))
    for path,digest in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', path
        data = stream.read(int(header[2]))
        assert stream.read(1) == b'\n' and hashlib.sha256(data).hexdigest() == digest == sha(path), path
    assert stream.read() == b''


# These are finite delivery lots and unsent requests, not new runtime records.
LOTS=[
    dict(id='A01',title='Autoridad de entrada y scope objetivo',works=['W01'],depends=[],recipient='Autoridad humana preexistente del proyecto y maintainer del scope; persona sin designar',
        request='Aportar la autoridad auténtica preexistente del scope y de sus revisores/aceptante de entrada, el target exacto PGO181 candidato02 y los límites que permanecen sin cambiar. Separar autoridad documental de cualquier facultad operativa; no apoyarse en appointments futuros o en un bundle no emitido.',
        returns=['Registro de autoridad de entrada con identidad/custodia, competencia, vigencia y ámbito exacto, revisado por R06 y R08 bajo autoridad preexistente.',
            'Scope source/runtime/image/caller/platform/epoch/policy conocido, con los identificadores reales disponibles y ausencias explícitas; constantes y cuotas I223 sin cambiar.',
            'Matriz de acciones permitidas/denegadas y de quién puede decidirlas; ninguna facultad funcional inferida de esta petición.'],
        completion='W01 aceptado genuinamente y autoridad de entrada trazable; ningún appointment futuro A02 es su única justificación.',
        stop='Sin autoridad de entrada o scope aceptado, SD01: no contactar, nominar, provisionar o aceptar paquetes posteriores.'),
    dict(id='A02',title='Humanos canónicos, competencia, appointments y anchors',works=['W02'],depends=['A01'],recipient='Autoridad externa de identidad/anchors y titulares competentes R01-R08; sin nombres seleccionados',
        request='Entregar evidencia genuina de sujetos/aliases/competencia/appointments y anchors preexistentes independientes, con claves de propósito, epoch, vigencias y revocación. Identificar autores y preparadores conocidos sin afirmar completitud final ni preaprobar futuros autores.',
        returns=['Roster humano canónico y relación de aliases con evidencia de autoridad, competencia y appointments por rol y scope; principal software separado.',
            'Comparaciones reales de ocho exclusiones S01, source-author/root-key y cuatro separaciones de custodia; R08 separado de R01/R02, coincidencia R01/R02 sólo bajo condiciones exactas.',
            'Registry/anchor/actor/key/purpose/epoch/currentness/revocación auténticos bajo selección independiente; registros previos de revisiones genuinas, no strings o hashes documentales.'],
        completion='W02 intake aceptado bajo sus roles reales, con revisores/aceptante elegibles y anchors auténticos; completitud final diferida a W10.',
        stop='Faltan autoridad, independencia o anchors: no usar identidades Git/asistente o claves autofundadas; contacto/enrollment/firma/provisión requieren autoridad propia separada.'),
    dict(id='A03',title='Baseline genuino de fuentes, imagen y runtime',works=['W03'],depends=['A01','A02'],recipient='Autor real de las seis fuentes y custodio R01 de build/imagen/runtime; sin persona designada',
        request='Aportar, si existen y están autorizados por su provenance, los seis fuentes efectivos ya calificados, la imagen externa y la clausura exacta de runtime y sus correspondencias. Si no existen, declarar el gap y el trabajo de implementación/build/cualificación pendiente, sin ejecutarlo por este plan.',
        returns=['Seis cuerpos reales completos en los logical paths exactos con bytes/digests/source root, versión, autores y provenance de cualificación; no predictive hashes.',
            'Imagen externa auténtica y mapping source-to-image con README DOCUMENT, entradas inmutables, política/schema/perfil/salidas/transporte exactos realmente implementados.',
            'Clausura completa interpreter/loader/stdlib/frozen/native/crypto, build/toolchain y correspondencia source/binario/runtime con identidad y revisión R01/R06 más R08.'],
        completion='W03 aceptado con todos los cuerpos y correspondencias disponibles, mismo scope real; repo-hashes o una imagen declarada no bastan.',
        stop='SD02: las seis fuentes faltan en el repo. Si tampoco se entregan artefactos genuinos calificados, detener: hace falta alcance y autoridad separados de implementación/build/cualificación; ningún run queda autorizado aquí.'),
    dict(id='A04',title='Caller y garantías exigibles de plataforma',works=['W04'],depends=['A02','A03'],recipient='Custodio R02 y operador con autoridad real sobre caller/plataforma/capacidad/servicio; sin selección',
        request='Aportar cuerpos ya existentes con garantías exigibles para el runtime y process set exactos: caller/constructor/dominio, capacidad, CPU/IO/scheduler/observación, reloj y ledger global. Explicar mecanismo, hipótesis, validez y autoridad de cada garantía, sin sustituirla por cuota, benchmark, frecuencia o promesa.',
        returns=['Identidad/principal requester-caller, constructor existente, dominio protegido y enforcement de origen/primer entry/canales heredados antes de código no confiable.',
            'Capacidad disponible realmente atestada para el rollup solicitado/committed y garantías compatibles de servicio o condiciones de WCET: unidades, procesos, carga/cache/memoria, ventanas, backlog/readiness/concurrencia, delays y vigencia.',
            'Ocho garantías de plataforma completas, reloj/error/currentness/revocación y dominio global atomic one-use/durabilidad/restarts/rollback con provenance; revisiones R02/R03/R06 y R08.'],
        completion='W04 aceptado y cada premisa de capacidad/servicio/custodia sustentada; decisión de disponibilidad antes de invertir en pruebas derivadas incompletas.',
        stop='SD03: garantía o backend intrínseco no demostrados, mantener no admisión. No probar/medir/configurar reloj, ledger, procesos, endpoints o servicio para llenar el expediente sin autoridad separada.'),
    dict(id='A05',title='Cuerpos de recualificación y cotas completas',works=['W05','W06','W07','W08'],depends=['A03','A04'],recipient='Autores competentes de pruebas de fuente/atomicidad, allocation/lifetime, trabajo/WCET y temporalidad; revisores separados',
        request='Entregar derivaciones completas disponibles para el sucesor efectivo, con autores autenticados y todas las hipótesis/provenance. Seguir W05, después W06 y W07 en paralelo y finalmente W08. Una nueva medición/cualificación o run no se obtiene por esta solicitud documental.',
        returns=['W05: inventarios/requalificación de179 casos,321 raíces,12 grupos y30 sitios más rutas de bootstrap/custodia/crypto/Reader/salida/fallo y closure completa; CP03 heredado y atomicidad escrita no transfieren aceptación.',
            'W06: once owners con bytes, vidas, overlap/allocator/native/GC/tracebacks/rechazos, requested/committed y fit frente a capacidad realmente disponible, sin null=0 ni préstamos de reserva.',
            'W07: inventario/correspondencia all30 completa, costes por actividad/proceso/fase, ambos Readers y join global, unidades compatibles/servicio o WCET con supuestos y delays, no bytes/visitas a segundos.',
            'W08: prueba ordenada t0/tR/tW/tF, trabajo worker pre-tR, exit-to-exact-True tW, finally/dual writes hasta tF, éxito/liveness y cotas60/750/60+30 con reserva conservada.'],
        completion='Cuerpos W05-W08 completos y reviews/aceptaciones propios genuinos bajo roles exactos; se entregan para el join independiente W09 sin declarar E01-E05 cerradas.',
        stop='SD04/SD05: bound, premisa o900 incompleto, parar admisión de recursos. No probes/profiling/WCET experimental/benchmarks/runs o cambios de cuotas/reservas; si la ruta los necesita, queda pendiente de alcance/autoridad separados.'),
    dict(id='A06',title='Decisión independiente del join E01-E05/BASIS/índices',works=['W09'],depends=['A02','A03','A04','A05'],recipient='R03/R06 genuinos y R08 separado de autores/providers/preparadores; sin personas designadas',
        request='Revisar los veinte criterios y cinco obligaciones con cuerpos completos exactos y todos los supuestos, más BASIS/index/CP03/ATOMICITY. Identificar y autenticar todos los autores y hechos baseline antes de aceptar; no pedir al futuro freeze o CE10 que los autentique retrospectivamente.',
        returns=['Disposición por cada E01-E05 y sus cuatro criterios sobre el mismo source/runtime/image/caller/platform/resource/epoch scope, con fuentes, unidades, hipótesis, reviewers y motivos reales.',
            'BASIS/resource index y siete pruebas autocontenidas auténticas: E01-E05 reviewer R03; CP03/ATOMICITY/BASIS reviewer R06; bytes/hashes/roles/review_record_ids genuinos y R08 separado.',
            'Inventario completo de autores/providers/preparadores conocidos y baseline previamente autenticado; toda referencia faltante/rechazada visible; evidencia que no quepa bajo límites exige rechazar/revisar grafo, nunca truncar.'],
        completion='W09 sólo aceptable con todas las obligaciones/criterios y supuestos compatibles, pruebas previas aceptadas y decisiones independientes trazables.',
        stop='SD08 y rechazos W09: si falta cuerpo/autor/provider/scope o independencia, dictamen negativo; no se presenta un parcial positivo como cierre conjunto ni se espera CE10 como única autoridad.'),
    dict(id='A07',title='Finalización auténtica de custodia y mapping',works=['W10','W11','W12'],depends=['A02','A04','A06'],recipient='Autoridad identidad/anchors, custodios R01/R02, compilador de evidencia y revisores/aceptante genuinos; sin designación',
        request='Cuando las premisas previas estén genuinamente aceptadas, aportar los registros finales de los mismos hechos, C/acceptance exactos, bundle/aprobaciones y prueba global de mapping bajo autoridad propia. No generar, firmar, configurar o verificar crypto por este plan.',
        returns=['W10: roster final de todos los autores W05-W09 y preparadores; actor registry→imagen→caller→plataforma, cuerpos/bytes/digests/caps/epoch/vigencias exactos, reconciliados con W09 antes aceptado.',
            'W11: C19/acceptance27,14 tipos/13 valores+contención, constantes y digest completo, cuatro hashes y cinco evidencias previas; sin firma propia de acceptance o bundle hash en C.',
            'W12: core8/bundle3 y cinco registros, tres aprobaciones R01/R02/R08 sobre mismo core con dominios+un NUL; anchors y políticas seleccionados independientemente.',
            'Prueba global de exactamente un mapping por(epoch,digest C) hacia bundle/caller/image/domain/ledger entre todos los callers/imágenes/dominios/restarts antes de P_ROOT_CHECK y constructor intrínseco, con caps reales y costes revalidados.'],
        completion='W10→W11→W12 genuinamente aceptados sobre los mismos hechos; C contenido en vigencias actuales, error conservador≤5/lifetime≤3600, fuentes/proof/caps/Reader/guards compatibles.',
        stop='SD06/SD07: cualquier autor/cuerpo/fuente/runtime/epoch/política cambia, invalidar afectados y volver a revisar antes de progresar. Snapshots/signing/keygen/crypto/enrollment/registry/mapping/provisión/configuración necesitan autoridad separada; no se simulan.'),
    dict(id='A08',title='Decisión real de los30 gates y handoff limitado',works=['W13'],depends=['A01','A02','A03','A04','A05','A06','A07'],recipient='R06 competente y R08 separado con autoridad limitada al dictamen; sin nombramiento',
        request='Sólo con paquetes genuinos y completos, decidir cada una de las treinta filas prelaunch y el join de recursos. Mantener recibo CE12 diferido y entregar las obligaciones finales sin ejecutar, crear autoridad o promover flags/certificado.',
        returns=['Checklist30 con siete familias,16 reglas y siete globales; cada disposición aceptada/rechazada/pendiente con body bytes/hash/locator/scope/autor/provider/custodia y decisión primaria/separada auténticas.',
            'Join E01-E05/20 criterios aceptable únicamente con clausura exacta; inventario real completo de referencias faltantes/aportadas/rechazadas,69 plantillas nunca sustituyen cuerpos reales.',
            'Handoff X09 sin comando actual: autorización separada/E06/payload/Q/root/admisión antes de claim, claim/construcción reales antes del recibo privado; no CE12 como precondición nueva de CE11.'],
        completion='W13 sólo aceptable con30 gates probados y R06/R08 genuinos. Aceptación prelaunch sigue separada de ejecución funcional, certificado activo y cierre D5.',
        stop='Cualquier gate/obligación incompleto o decisión no independiente conserva disposición negativa y no admisión; no claim/spawn/recibo/E06/Q/root/runs para hacer cerrar el checklist.')]


def acquisition_graph():
    graph={r['id']:r['depends'] for r in LOTS}
    pending=set(graph)
    order=[]
    while pending:
        ready=sorted(node for node in pending if set(graph[node])<=set(order))
        assert ready,'Cyclic acquisition-lot graph'
        order.extend(ready)
        pending.difference_update(ready)
    return dict(graph=graph,topological_order=order,acyclic_documentarily_verified=True,actual_lots_accepted=0)


def build_candidate():
    plan=rd(PLAN)
    pins={**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==1052
    inventory=sorted({PLAN,CONTRACT,CE01,W01,W02,W09,W10,W11,W12,W13,PACK,CUSTODY,PROFILE,PRIOR_REVIEW,*WORK_PATHS.values()})
    assert all(p in pins and pins[p]==sha(p) for p in inventory)
    owner={work:lot['id'] for lot in LOTS for work in lot['works']}
    return dict(schema='d5.i251-genuine-evidence-acquisition-plan.v1',increment='I251',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        plan_id='PGE251-CANDIDATE-01',subject='I223 / PGO181 candidate02 / PJC115-R2; no active policy,quota or certificate change',
        kind='UNSENT_GENUINE_MATERIAL_DELIVERY_AND_COMPETENT_ACCEPTANCE_PLAN_NOT_NEW_RUNTIME_SCHEMA_OR_ACTUAL_EVIDENCE',
        status='DOCUMENTARY_ACQUISITION_PLAN_READY_NO_CONTACT_MATERIAL_OR_COMPETENT_ACCEPTANCE_SD01_ACTIVE_NOT_ADMITTED',
        input_pins=pins,plan_binding=pin(PLAN),latest_negative_review=pin(PRIOR_REVIEW),documentary_inventory=[pin(p) for p in inventory],
        objective='Obtain genuinely supplied complete same-scope bodies and independent decisions for existing W01-W13; reuse their checklists as requirements, never manufacture proof or substitute more documentary passes for external material.',
        current_blockers=plan['current_blockers'],current_no_admission=rd(W13)['non_admission_record'],
        existing_material_boundary=dict(source=pin(W01,'/existing_external_material_intake'),exact_existing_material_rule=rd(W01)['existing_external_material_intake'],
            entry_authority_source=pin(W01,'/entry_authority_boundary'),exact_entry_rule=rd(W01)['entry_authority_boundary'],
            genuine_preexisting_entry_authority_not_future_A02_appointments_or_A07_bundle_as_sole_forecast_basis=True,
            only_existing_material_with_own_authorized_provenance_no_contact_fetch_or_verification_service_authorized=True,
            six_successor_sources_currently_absent_no_local_implementation_build_or_qualification_created=True,
            no_external_material_received_or_accepted_by_plan=True,actual_material_provider_body_or_own_authority=None),
        evidence_delivery_contract=dict(source=pin(PLAN,'/evidence_package_contract'),exact_contract=plan['evidence_package_contract'],
            mandatory_return_fields=['lot and W deliverable IDs','exact effective source/runtime/image/caller/domain/policy/epoch scope',
                'immutable body locator and available complete bytes/canonical digest','author/provider/custody/own provenance and validity/currentness/revocation',
                'complete derivations compatible units and all capacity/service/load/memory/cache/delay assumptions',
                'canonical actors/aliases/keys/purpose/competence/appointments/independence evidence',
                'genuine primary review and separate acceptance body IDs,hashes,bytes and reason per criterion',
                'all dependency/change/invalidation relations and missing/provided/rejected disposition'],
            no_document_hash_template_boolean_signature_test_or_budget_as_truth=True,
            unknown_values_remain_null_not_zero_or_predictive_hash=True,
            no_new_positive_wire_record_runtime_schema_Reader_member_hidden_file_or_output_defined=True),
        acquisition_lots=[dict(id=r['id'],title=r['title'],covers_work_packages=r['works'],depends_on_lots=r['depends'],
            intended_recipient_role_kind=r['recipient'],required_material_returns=r['returns'],completion_predicate=r['completion'],missing_or_failure_stop=r['stop'],
            W_requirements=[pin(PLAN,'/work_packages/'+str(int(work[1:])-1)) for work in r['works']],
            W_documentary_checklists=[pin(WORK_PATHS[work]) for work in r['works']],
            internal_work_dependencies={work:plan['work_packages'][int(work[1:])-1]['depends_on'] for work in r['works']},
            required_primary_review_roles={work:plan['work_packages'][int(work[1:])-1]['primary_review_roles'] for work in r['works']},
            separate_acceptor_role='R08',
            unsent_request_draft=dict(id='RQ'+r['id'][1:],recipient=r['recipient'],text=r['request'],
                required_return_contract='All evidence_delivery_contract fields plus each existing W requirement, no fabricated records.',
                is_draft_only=True,sent=False,contact_authorized=False),
            route_if_material_exists='Consider only genuinely supplied available material with its own authorized provenance and exact scope; this plan does not fetch/contact or run verification services.',
            route_if_material_missing='Keep missing/negative disposition. Identify exact unavailable body and separately scoped work/authority needed; do not execute,sign,provision,configure or create a synthetic substitute.',
            actual_coordinator_person=None,actual_provider_persons=None,actual_reviewers=None,actual_separate_acceptor=None,
            actual_delivery_location_bodies_bytes_digests_or_custody=None,actual_competence_appointments_and_entry_authority=None,
            actual_primary_reviews_or_separate_acceptance=None,actual_date_or_duration_guarantee=None,
            current_state='REQUEST_DRAFT_READY_NOT_SENT_GENUINE_MATERIAL_AND_AUTHORITY_MISSING',accepted=False)
            for r in LOTS],
        lot_order=acquisition_graph(),
        work_package_coverage=[dict(id=r['id'],source=pin(PLAN,'/work_packages/'+str(i)),exact_work_requirement=r,collection_lot=owner[r['id']],
            actual_accepted_delivery_package=None,accepted=False) for i,r in enumerate(plan['work_packages'])],
        exact_I223_work_dependency_graph={r['id']:r['depends_on'] for r in plan['work_packages']},
        critical_order_rules=dict(source=pin(PLAN,'/scope_authentication_and_freeze_order'),exact_order=plan['scope_authentication_and_freeze_order'],
            A01_preexisting_scope_reviewer_authority_cannot_be_backfilled_from_future_A02_or_bundle=True,
            early_A03_real_sources_and_A04_enforceable_capacity_service_before_costly_derivations=True,
            W05_first_then_W06_W07_parallel_then_W08_not_reverse_heap_work_dependency=True,
            actual_all_authors_and_complete_bodies_baseline_actor_image_caller_platform_authentic_before_A06_W09_acceptance=True,
            A07_final_freeze_same_facts_not_sole_retroactive_authentication_or_backward_A06_dependency=True,
            changed_contributors_scope_bodies_epoch_key_policy_service_or_graph_invalidates_affected_A01_A08_and_requires_review=True,
            W13_in_gate_producers_is_current_review_output_not_own_accepted_predecessor=True),
        real_milestones=[
            dict(id='M01',lots=['A01'],evidence_of_completion='Genuine accepted W01 scope and preexisting entry/reviewer authority.'),
            dict(id='M02',lots=['A02'],evidence_of_completion='Genuine canonical people/appointments/anchors and independent review eligibility, provisional intake not final author completeness.'),
            dict(id='M03',lots=['A03','A04'],evidence_of_completion='Available qualified exact sources/image/runtime and enforceable caller/platform/capacity/service/clock/global-ledger proof, with real acceptance.'),
            dict(id='M04',lots=['A05'],evidence_of_completion='Complete W05-W08 derivations and own required reviews for exact scope, no global E01-E05 closure inferred.'),
            dict(id='M05',lots=['A06'],evidence_of_completion='Actual independent joint W09 review of5 obligations/20 criteria and BASIS/index/atomicity, known authenticated authors/bodies/assumptions.'),
            dict(id='M06',lots=['A07'],evidence_of_completion='Actual accepted final W10/W11/W12 records,C,three approvals and global mapping under own authority and unchanged reviewed scope/caps.'),
            dict(id='M07',lots=['A08'],evidence_of_completion='Genuine R06/R08 decisions on30 gates and limited handoff. No automatic product release,certificate promotion or D5 closure.')],
        first_handoff=dict(next_request_draft_ids=['RQ01'],after_genuine_A01_acceptance_request_draft_ids=['RQ02'],required_first_material='Preexisting project/scope/reviewer entry authority and genuine identity/competence/appointment/anchor evidence; none supplied.',
            next_early_feasibility_request_draft_ids=['RQ03','RQ04'],no_real_handoff_contact_or_nomination_done=True,
            all_recipient_persons_addresses_channels_and_contact_authority=None,
            existing_reviewed_dossiers_are_requirements_not_new_external_proof=True),
        future_authority_resolution_ledger=[dict(work_id=r['id'],collection_lot=owner[r['id']],source=pin(PLAN,'/work_packages/'+str(i)+'/needs_separate_future_authority_for'),
            exact_separate_action_classes=r['needs_separate_future_authority_for'],
            if_required_for_missing_material='BLOCK_ACTION_KEEP_NOT_ADMITTED; prepare exact scope/actor/artifact/cost/authority request separately, never auto-approve or execute from this plan.',
            actual_operational_authority=None,authorized_now=False) for i,r in enumerate(plan['work_packages'])],
        intake_and_review_workflow=dict(ordered_steps=[
            'Check independently genuine entry authority and recipient/reviewer eligibility before considering acceptance; no automatic nomination.',
            'Record genuinely supplied body availability/locator/bytes/digest,author/provider/custody/own authority,exact scope and validity; unknown material stays missing.',
            'Identify every actual reference instance and all assumptions;69 typed templates are not actual or unique body count.',
            'Competent authorized primary actors review applicability,derivation,scope/units/capacity/service/guards and provenance; unavailable or incompatible evidence cannot advance.',
            'Separate eligible R08 accepts or rejects only in exact own scope with a real immutable reason/body; assistant audit never manufactures that decision.',
            'Reconcile accepted package dependencies/currentness and invalidations before downstream lot; changed facts require affected work/review again.',
            'Only when all30 gates and5 obligations/20 criteria have genuine compatible accepted evidence may competent prelaunch handoff be considered; final execution route stays separate.'],
            allowed_future_dispositions=['MISSING','PROVIDED_NOT_ACCEPTED','REJECTED_WITH_TRACEABLE_REASON','ACCEPTED_ONLY_BY_GENUINE_AUTHORIZED_ROLES'],
            no_actual_disposition_decision_or_proof_created=True,
            actual_received_inventory=None,provided_real_bodies=[],rejected_real_bodies=[],actual_primary_decisions=0,actual_separate_acceptances=0,
            actual_reference_completeness_verified=False),
        gate_to_collection_matrix=[dict(id=g['id'],category=g['category'],source=pin(PLAN,'/gate_closure_matrix/'+str(i)),
            required_work_package_ids=g['producer_work_package_ids'],required_collection_lots=sorted({owner[work] for work in g['producer_work_package_ids']}),
            exact_close_only_if=g['close_only_if'],actual_evidence_and_competent_decisions=None,accepted=False)
            for i,g in enumerate(plan['gate_closure_matrix'])],
        resource_acceptance_matrix=[dict(id=r['id'],source=pin(PLAN,'/resource_obligation_matrix/'+str(i)),exact_requirement=r,
            producer_lots=sorted({owner[work] for work in r['producer_work_package_ids']}),
            actual_complete_bound_same_scope_assumptions_primary_review_and_R08_acceptance=None,closed=False,accepted=False)
            for i,r in enumerate(plan['resource_obligation_matrix'])],
        stop_rules=dict(source=pin(PLAN,'/stop_and_decision_points'),exact_stop_points=plan['stop_and_decision_points'],
            current_SD01_active=True,any_missing_body_unknown_provider_unqualified_actor_incompatible_scope_or_unproved_service_keeps_no_admission=True,
            no_more_documentary_passes_substitute_for_genuine_material_or_external_decisions=True,
            lack_of_evidence_not_global_absence_or_actual_infeasibility=True,
            no_calendar_or_completion_duration_guarantee=True,actual_schedule_provider_or_service_selected=None),
        preserved_resource_and_cost_rules=dict(source=pin(PLAN,'/resource_and_scope_policy'),exact_policy=plan['resource_and_scope_policy'],
            exact_candidate_reserve_rules=rd(CONTRACT)['reserve_accounting'],
            all_referenced_evidence_lookup_freshness_identity_crypto_native_IO_copies_registry_receipt_output_failure_cleanup_inside_both_Readers_and_global_heap_work_service_phase_join=True,
            proposed_delivery_docs_or_offline_enrollment_not_new_Reader_inputs_free_costs_capacity_or_success900=True,
            actual_bound_capacity_service_or_resource_requalification=None,reserve_transfers_applied=0,resources_reserved=False,quotas_or_budgets_changed=False),
        final_route_boundary=dict(source=pin(PLAN,'/prelaunch_handoff_and_CE12'),exact_boundary=plan['prelaunch_handoff_and_CE12'],
            receipt_gate=plan['deferred_gate'],four_external_preclaim_prerequisites_then_actual_claim_construction_before_private_receipt=True,
            no_final_route_execution_claim_spawn_receipt_as_new_precondition_of_prelaunch_acceptance=True,
            claim_not_own_precondition_no_free_retry_uncertain_partial_expired_states=True,
            actual_execution_authorization_E06_payload_Q_root_admission_claim_receipt=None,actual_route_or_receipt_authorized=False),
        authority_boundary=dict(source=pin(PLAN,'/authorization_boundary'),exact_inherited_boundary=plan['authorization_boundary'],
            allowed_now=['READ_DOCUMENTS_GIT_HASHES_AND_EXACT_PATH_PRESENCE','PREPARE_PLAN_AND_UNSENT_REQUEST_DRAFTS','RUN_OWN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT'],
            all_requests_are_local_drafts_not_messages_or_provider_contact=True,
            no_contact_nomination_enrollment_fetch_verification_service_signing_keygen_crypto_or_provisioning=True,
            no_product_components_E06_import_compile_discovery_tests_builds_benchmarks_platform_clock_ledger_claim_process_or_endpoint_probes=True,
            no_new_sources_runtime_records_C_Q_root_mapping_registry_authority_destination_helpers_channels_inputs_outputs_or_active_configuration=True,
            no_quota_budget_reserve_or_capture_inputs_change=True,
            actual_external_action_authority_or_provider_selection=None),
        preserved_scope_and_gates={key:plan[key] for key in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']},
        current_effect={**{key:value for key,value in rd(W13)['current_effect'].items() if key!='W13_documentary_prepared'},
            'I251_acquisition_plan_and_unsent_drafts_prepared':True,'actual_material_obtained_or_independent_acceptance_or_lot_completion':False,
            'provider_contact_or_nomination_done':False,'actual_sources_implementation_or_build_created':False,'actual_acquisition_lots_accepted':0},
        producer=dict(identity='Same Codex assistant/chat as I249/I250',documentary_preparer_only=True,actor_independent=False,
            competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_contact_authority_material_acquisition_canonical_appointment_acceptance_execution_release_or_D5_closure=True))


NEGATIVE_CASES=[
    ('SD01_bypass',('stop_rules','current_SD01_active'),True,False),
    ('material_as_obtained',('current_effect','actual_material_obtained_or_independent_acceptance_or_lot_completion'),False,True),
    ('draft_sent',('acquisition_lots',0,'unsent_request_draft','sent'),False,True),
    ('contact_authorized',('acquisition_lots',0,'unsent_request_draft','contact_authorized'),False,True),
    ('draft_not_draft',('acquisition_lots',0,'unsent_request_draft','is_draft_only'),True,False),
    ('invented_provider',('acquisition_lots',0,'actual_provider_persons'),None,['UNVERIFIED_TEST_LABEL']),
    ('invented_acceptor',('acquisition_lots',0,'actual_separate_acceptor'),None,'UNVERIFIED_TEST_LABEL'),
    ('invented_delivery',('acquisition_lots',0,'actual_delivery_location_bodies_bytes_digests_or_custody'),None,{}),
    ('completion_guarantee',('acquisition_lots',0,'actual_date_or_duration_guarantee'),None,'UNVERIFIED_TEST_DATE'),
    ('lot_accepted',('acquisition_lots',0,'accepted'),False,True),
    ('future_A02_as_entry_authority',('critical_order_rules','A01_preexisting_scope_reviewer_authority_cannot_be_backfilled_from_future_A02_or_bundle'),True,False),
    ('source_service_premises_skipped',('critical_order_rules','early_A03_real_sources_and_A04_enforceable_capacity_service_before_costly_derivations'),True,False),
    ('reverse_heap_work_dependency',('critical_order_rules','W05_first_then_W06_W07_parallel_then_W08_not_reverse_heap_work_dependency'),True,False),
    ('late_author_authentication',('critical_order_rules','actual_all_authors_and_complete_bodies_baseline_actor_image_caller_platform_authentic_before_A06_W09_acceptance'),True,False),
    ('freeze_as_prior_authentication',('critical_order_rules','A07_final_freeze_same_facts_not_sole_retroactive_authentication_or_backward_A06_dependency'),True,False),
    ('silent_proof_transfer',('critical_order_rules','changed_contributors_scope_bodies_epoch_key_policy_service_or_graph_invalidates_affected_A01_A08_and_requires_review'),True,False),
    ('self_accepted_predecessor',('critical_order_rules','W13_in_gate_producers_is_current_review_output_not_own_accepted_predecessor'),True,False),
    ('entry_self_authorized',('existing_material_boundary','genuine_preexisting_entry_authority_not_future_A02_appointments_or_A07_bundle_as_sole_forecast_basis'),True,False),
    ('implicit_material_fetch',('existing_material_boundary','only_existing_material_with_own_authorized_provenance_no_contact_fetch_or_verification_service_authorized'),True,False),
    ('synthetic_source_substitute',('existing_material_boundary','six_successor_sources_currently_absent_no_local_implementation_build_or_qualification_created'),True,False),
    ('document_template_as_proof',('evidence_delivery_contract','no_document_hash_template_boolean_signature_test_or_budget_as_truth'),True,False),
    ('missing_value_zero',('evidence_delivery_contract','unknown_values_remain_null_not_zero_or_predictive_hash'),True,False),
    ('new_runtime_schema',('evidence_delivery_contract','no_new_positive_wire_record_runtime_schema_Reader_member_hidden_file_or_output_defined'),True,False),
    ('actual_contact_handoff',('first_handoff','no_real_handoff_contact_or_nomination_done'),True,False),
    ('future_operation_authorized',('future_authority_resolution_ledger',0,'authorized_now'),False,True),
    ('reference_closure_verified',('intake_and_review_workflow','actual_reference_completeness_verified'),False,True),
    ('workflow_as_actual_decision',('intake_and_review_workflow','no_actual_disposition_decision_or_proof_created'),True,False),
    ('gate_accepted',('gate_to_collection_matrix',0,'accepted'),False,True),
    ('resource_closed',('resource_acceptance_matrix',0,'closed'),False,True),
    ('more_documentary_passes_as_material',('stop_rules','no_more_documentary_passes_substitute_for_genuine_material_or_external_decisions'),True,False),
    ('calendar_guarantee',('stop_rules','no_calendar_or_completion_duration_guarantee'),True,False),
    ('global_infeasibility_from_missing',('stop_rules','lack_of_evidence_not_global_absence_or_actual_infeasibility'),True,False),
    ('free_external_evidence_costs',('preserved_resource_and_cost_rules','all_referenced_evidence_lookup_freshness_identity_crypto_native_IO_copies_registry_receipt_output_failure_cleanup_inside_both_Readers_and_global_heap_work_service_phase_join'),True,False),
    ('reserve_transfer',('preserved_resource_and_cost_rules','reserve_transfers_applied'),0,1),
    ('quota_change',('preserved_resource_and_cost_rules','quotas_or_budgets_changed'),False,True),
    ('final_route_as_prelaunch_precondition',('final_route_boundary','no_final_route_execution_claim_spawn_receipt_as_new_precondition_of_prelaunch_acceptance'),True,False),
    ('final_route_authorized',('final_route_boundary','actual_route_or_receipt_authorized'),False,True),
    ('implicit_contact',('authority_boundary','all_requests_are_local_drafts_not_messages_or_provider_contact'),True,False),
    ('implicit_provisioning_crypto',('authority_boundary','no_contact_nomination_enrollment_fetch_verification_service_signing_keygen_crypto_or_provisioning'),True,False),
    ('implicit_product_run',('authority_boundary','no_product_components_E06_import_compile_discovery_tests_builds_benchmarks_platform_clock_ledger_claim_process_or_endpoint_probes'),True,False),
    ('implicit_active_configuration',('authority_boundary','no_new_sources_runtime_records_C_Q_root_mapping_registry_authority_destination_helpers_channels_inputs_outputs_or_active_configuration'),True,False),
    ('D5_closed',('current_effect','D5_closed'),False,True)]


def validate(d):
    for name,path,expected,_ in NEGATIVE_CASES:
        node=d
        for key in path:
            node=node[key]
        assert type(node) is type(expected) and node==expected,name
    assert d==build_candidate(),'Plan differs from source reconstruction'
    check_pointers(d)


def rejection_checks(d):
    results=[]
    for name,path,_,value in NEGATIVE_CASES:
        mutant=copy.deepcopy(d)
        node=mutant
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
    d=rd(SUBJECT)
    verify_blobs(d['input_pins'])
    validate(d)
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT))
    exists=Path.exists
    rec=previous['reconstruct']()
    assert rec==rd(PRIOR_RECON) and previous['build_review'](rec)==rd(PRIOR_REVIEW)
    assert Path.exists is exists
    plan=rd(PLAN)
    lots=d['acquisition_lots']
    assert [r['id'] for r in lots]==['A%02d'%i for i in range(1,9)]
    coverage=[work for lot in lots for work in lot['covers_work_packages']]
    assert coverage==['W%02d'%i for i in range(1,14)] and len(coverage)==len(set(coverage))
    assert [r['unsent_request_draft']['id'] for r in lots]==['RQ%02d'%i for i in range(1,9)]
    for lot in lots:
        assert lot['unsent_request_draft']['sent'] is False and lot['unsent_request_draft']['contact_authorized'] is False
        assert lot['accepted'] is False and all(v is None for k,v in lot.items() if k.startswith('actual_'))
        for work,source,checklist in zip(lot['covers_work_packages'],lot['W_requirements'],lot['W_documentary_checklists']):
            requirement=plan['work_packages'][int(work[1:])-1]
            assert fragment(source)==requirement and checklist['path']==WORK_PATHS[work]
            assert lot['internal_work_dependencies'][work]==requirement['depends_on']
            assert lot['required_primary_review_roles'][work]==requirement['primary_review_roles']
    assert d['exact_I223_work_dependency_graph']=={r['id']:r['depends_on'] for r in plan['work_packages']}
    assert d['lot_order']==acquisition_graph()
    lot_of={work:lot['id'] for lot in lots for work in lot['covers_work_packages']}
    graph=d['lot_order']['graph']
    def ancestors(node):
        seen=set()
        pending=list(graph[node])
        while pending:
            parent=pending.pop()
            if parent not in seen:
                seen.add(parent)
                pending.extend(graph[parent])
        return seen
    for requirement in plan['work_packages']:
        current=lot_of[requirement['id']]
        for parent in requirement['depends_on']:
            assert lot_of[parent]==current or lot_of[parent] in ancestors(current), (requirement['id'],parent)
    assert len(d['real_milestones'])==7 and len(d['future_authority_resolution_ledger'])==13
    assert len(d['gate_to_collection_matrix'])==30 and len(d['resource_acceptance_matrix'])==5
    assert len({r['id'] for r in d['gate_to_collection_matrix']})==30
    for row in d['gate_to_collection_matrix']:
        requirement=fragment(row['source'])
        assert row['id']==requirement['id'] and row['exact_close_only_if']==requirement['close_only_if']
        assert row['accepted'] is False and row['actual_evidence_and_competent_decisions'] is None
    for row in d['resource_acceptance_matrix']:
        assert row['exact_requirement']==fragment(row['source']) and row['closed'] is False and row['accepted'] is False
    assert d['current_no_admission']==rd(W13)['non_admission_record']
    for path in rd(PACK)['$defs']['source_bindings']['required']:
        assert not (ROOT/path).exists()
    for row in rd(CE11)['pending_I177_final_bindings']:
        assert not (ROOT/row['path']).exists()
    for key,value in d['current_effect'].items():
        if key=='I251_acquisition_plan_and_unsent_drafts_prepared':
            assert value is True
        elif key=='IR03':
            assert value=='NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed','actual_acquisition_lots_accepted']:
            assert type(value) is int and value==0
        else:
            assert value is False,key
    return dict(schema='d5.i251-preparation-review.v1',increment='I251',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,candidate=pin(SUBJECT),
        counts=dict(input_pins=1052,acquisition_lots=8,unsent_request_drafts=8,covered_I223_packages=13,real_evidence_milestones=7,
            mapped_prelaunch_gates=30,resource_obligations=5,future_authority_requirements=13,actual_material_packages=0,actual_lots_accepted=0),
        source_reconstruction=dict(I250_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        limitations=['This is a concrete finite acquisition/request plan, not material delivery,contact,provider nomination,canonical appointment or genuine independent acceptance. SD01 active and all current I223 gates/resources still pending.',
            'A01/A02 need independently genuine entry/identity authority. Six sources are absent; A03 existing qualified artifacts or separately authorized implementation/build/qualification scope is a real material branch, not another documentary PASS.',
            'Source/platform/service premises precede complete derivations; known authentic baseline/authors/bodies precede W09 and W10/CE10 cannot authenticate them retrospectively. Changed facts invalidate affected lots.',
            'Actual signing/crypto/enrollment/configuration/runs/probes/provider contacts require their own separate exact authority and remain unperformed; no calendar/provider/duration guarantee,quota/reserve/binding or D5 change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I251-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/lot-order/dependency/coverage/request-draft checks and in-memory document mutations only. No target imports/compile/discovery/tests/runs/build/E06, positive crypto/codec/signing/keygen/enrollment/provisioning, contacts/registry/mapping configuration, clock/CPU/IO/service/platform/ledger/claim/replay/process sampling/probes.',
            over400_lines=True,reason='One finite eight-lot acquisition plan with unsent reviewable requests, exact I223 coverage/dependencies, pins, rejection checks and preservation. Overage declared; no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_contact_authority_material_acquisition_canonical_appointment_acceptance_execution_release_or_D5_closure=True))


def main():
    review=build_review()
    assert rd(PREP)==review
    prior=rd(PRIOR_SEAL)
    preserved={**prior['preserved_published739'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==744
    seal=rd(SEAL)
    assert seal['schema']=='d5.i251-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published744']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==review['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I251',input_pins=1052,preserved_published_files=744,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],SD01_stop_active=True,
        prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
