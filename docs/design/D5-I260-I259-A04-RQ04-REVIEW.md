# I260 — revisión de A04/RQ04: caller, garantías, capacidad y servicio

**No se encuentran defectos documentales nuevos en A04/RQ04 de I259.** El dossier conserva los requisitos genuinos de caller, enforcement de plataforma, capacidad disponible y servicio compatible, sin confundirlos con presupuestos o cierre completo de recursos. A01/A02/A03/A04 siguen sin aceptar, SD01 está activo y se mantiene la **no admisión**. RQ04 no se envía.

Fecha: 2026-11-25, Europe/Madrid. Base: `528d7c52c498001e9a5e76e8b43940d7a1b493b1`.

Esta revisión metodológica del mismo asistente contrasta el [dossier I259](D5-I259-A04-RQ04-CALLER-PLATFORM-SERVICE.md) con [I251](D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.md), W04 y las fuentes normativas de caller/plataforma/servicio. No acredita operador, capacidad de construcción, attestation o garantía real, ni sustituye revisión competente R02/R03/R06 o aceptación separada R08.

## Dictamen por frontera

| Frontera | Resultado y evidencia genuina pendiente |
|---|---|
| Antecedentes | A02/W02 y A03/W03 siguen sin aceptar, con A01 pendiente. Preparar/revisar el borrador no permite envío, contacto, nominación, selección de backend o intake positivo. |
| Caller y constructor | Se exige principal software distinto del requester humano y mecanismo intrínseco existente de construcción/loader/aislamiento/custodia antes de código no confiable. UID/PID/fd/env/hash/appointment/READY no prueban capacidad. |
| Garantías de plataforma | Los ocho slots y sus fuentes/schema se conservan completos, con exigencia de mecanismo/enforcement, cuerpos disponibles, operador con autoridad real, scope/supuestos/validez y reviews. |
| Capacidad disponible | Debe atestarse realmente en métricas requested live heap y committed allocator heap, con native/GC/vidas/overlap y procesos pertinentes. Cuota, RSS, reserva virtual o presupuesto candidato no son disponibilidad. |
| Servicio y demoras | Unidades compatibles y curva inferior con condiciones/latencias o WCET justificado de plataforma exacta; CPU, wall y suma de procesos separados. Ocho clases de servicio y ocho demoras completas, sin incógnitas tratadas como cero. |
| Reloj y ledger | Currentness/revocación/epochs/reloj y mecanismo global atómico/durable/high-water/rollback/crash requieren evidencia genuina. No se prueban con fecha host ni mediante claim/replay/probe actual. |
| Fases posteriores | Demanda/join W05–W09, freeze W10, C W11, mapping W12 y claim/construcción/recibo CE12 conservan sus consumidores sin dependencia inversa. |

La ausencia de autoridad o garantías reales no constituye un defecto del borrador que las declara pendientes. Impide aceptar A04. PL07 exige registrar el gap y conservar SD03, sin suplirlo con un PASS documental o inventar una cota, proveedor, fecha o prueba de inviabilidad.

## Caller, canales y evidencia de enforcement

Se conservan las relaciones previas actor/imagen/caller/domain/constructor/loader y la separación humano/requester frente a principal software. Las firmas futuras del bundle no pueden ser su única autenticación prevista. El literal bootstrap-custody-only es política de schema, sin permiso emitido. Identidad de proceso, fd/fstat, nombre de módulo, clave, frame o appointment por sí solos tampoco autorizan import funcional/capture/claim/spawn.

La construcción protegida debe asegurar primera entrada inmutable y excluir loader shadowing, cwd/PYTHONPATH/sitecustomize no confiables, tracing/memory mutation y descriptor injection/duplication antes de código no confiable. Los dos pipes y seis operandos I189 conservan origen exclusivo, ownership y cierre de duplicados/extremos; los descriptores internos de runtime/spawn necesitan clausura/costes propios. No se crea helper/proceso/canal/fd/argv/input/file/env de confianza o constructor operativo.

Las ocho garantías son immutable_first_entry, no_loader_shadowing, no_descriptor_injection_or_duplication, no_hostile_tracing_or_memory_mutation, exclusive_parent_child_channel_origin, owned_paths_and_group_identity, no_unapproved_helper_or_input y exact_source_runtime_mapping. Se comprueban las ocho filas exactas, sin duplicado u omisión.

En el schema I191 cada slot es una **referencia tipada a evidencia**. Su presencia o digest no acredita el mecanismo o su verdad: hacen falta cuerpo completo disponible, operador competente con autoridad, scope source/runtime/image/caller/domain/process, supuestos/validez/provenance y decisión genuina. La comprobación del auditor propio fue corregida para contrastar ese `$ref` exacto; no se modifica el schema ni el dossier I259. Todos los slots reales siguen sin verificar/aceptar.

Los cuatro roles R02/R03/R06/R08 conservan sus ámbitos de competencia/appointment y separación. Los humanos, autoridad/custodia y cuerpos de review/decisión son desconocidos. El mismo asistente preparador y su auditor no aportan independencia o aceptaciones genuinas.

## Capacidad, servicio y temporalidad

Las ocho clases SV01–SV08 preservan plataforma/runtime/imagen/loader/domain/configuración; disponibilidad requested/committed heap; coordinador/worker/hijos e interferencia; CPU/servicio/WCET; demoras; señales/retry/load; reloj/observación; y autoridad/provenance/validez del proveedor. Cada fila conserva el enlace a su fuente P03 y la exigencia material completa, sin convertir el dossier histórico en prueba del sucesor.

La capacidad se acepta sólo con cotas inferiores reales para el scope y métricas exactos. Requested/committed no son bytes serializados, RSS, reserva virtual o límites configurados. Debe justificarse native/allocator/GC, vidas y solapamientos, incluidos procesos/interferencias compartidas. Los candidatos 11GiB requested/12GiB committed, 832MiB sin asignar y H11 separado no atestan memoria ni reservan recursos; subbounds históricos/modelos parciales no acreditan ajuste o inviabilidad.

El servicio necesita unidad compatible con el trabajo, curva inferior y latencia/ventanas/backlog/readiness/concurrencia o WCET justificado bajo la plataforma exacta. Carga/cache/memoria/configuración y validez son premisas explícitas. CPU time, wall time y sumas de procesos son magnitudes distintas; MHz, benchmark, deadline, cuotas o dividir trabajo por900 no proporcionan garantía de servicio. Una premisa de servicio no prueba toda la demanda del programa ni permite cerrar el join de recursos.

L01–L08 mantienen scheduler/servicio denegado, locks, filesystem/pipe/stream IO, terminación/reap de hijos, exit físico→retorno exacto True de wait_worker, startup/READY/RELEASE, cleanup/finalización/validación/publicación y señales/retry/backoff/interferencia. La fuente completa de cada demora se contrasta directamente con P03. Se incluye trabajo worker anterior a tR del padre, tW como retorno exacto True y finally/salidas hasta tF. No se resta overlap sin prueba o convierte demora desconocida en cero.

Los presupuestos 60/750/60+30=900 y worker600/90/60 siguen sin verificar. No se confunde el watchdog con liveness/éxito ni se añade crédito por categoría o se convierte presupuesto en servicio. Las reservas/cuotas permanecen intactas. Requested/committed/capacidad/servicio requieren correspondencia antes del futuro fit de heap y fases; esa obligación no se dispensa por diferir la prueba completa W05–W09.

## Reloj, currentness y mecanismo global

Se conservan las reglas exactas de dominio monotónico/UTC, error≤5, lifetime≤3600, `not_before<expires_at`, intervalos/contención en cada frontera aplicable y epoch/revocación/currentness auténticos. La fecha de revisión o un reloj del host no es el reloj aceptado del runtime. TOFU, cache obsoleta, NTP supuesto o lookup online/file/env oculto no reemplazan evidencia. El estado offline limitado por vigencia no promete descubrir toda revocación instantáneamente. No se muestrea/configura reloj o emite snapshot.

El namespace único global conserva la tupla `(trust_context_sha256,runtime_request_sha256,invocation_id)` en todos los callers/dominios/restarts. Se exigen atomicidad, high-water epoch, durabilidad/rollback/crash/doble gasto y ledger concordante con el mapping. Padre/hijo constituyen una invocación correlacionada, no dos consumos. Incertidumbre/claim parcial gasta o rechaza sin free retry o reutilización.

La evidencia de mecanismo existente no equivale a claim real, mapping emitido, recibo, backend operativo o replay/crash test. No se exige un claim para acreditar el mecanismo CE06 ni se ejecuta para obtener evidencia. C real sigue en W11 y mapping actual en W12; el worker conserva origen intrínseco protegido y sus comprobaciones C/Q/root independientes, sin nuevo mapping/receipt/frame/helper recibido.

## Cobertura y fronteras de fase

| Requisitos | Consumidor conservado |
|---|---|
| CC01–CC07, PF01–PF06 | Trece obligaciones de A04/W04 |
| CC08 / PF07 | W05–W09/CE07: demanda/join completo de recursos |
| CC09 / PF08 | W10/CE08: freeze final de antecedentes |
| CC10 / PF09 | W11/CE09: C exacto |
| CC11 / PF10 | W12/CE10: bundle/mapping actual único |
| CC12 / PF11 | CE12: claim/construcción/recibo, fuera del cierre prelaunch |

Se contrastan directamente los 23 requisitos y sus fuentes normativas. Trece se aplican a W04 y diez quedan diferidos; «aplicable» no significa satisfecho. Las dos obligaciones CE12 conservan su marca fuera de prelaunch. No se fuerza aceptación downstream de recursos/freeze/C/mapping/claim para aceptar las premisas propias de W04.

Actor/imagen/caller/plataforma/capacidad/servicio y autores/cuerpos deben ser auténticos antes de aceptar W09. W10 reconcilia/finaliza esos mismos hechos, sin autenticación retrospectiva o bundle como única autoridad previa. Cambios de operador/autoridad/body/source/runtime/caller/domain/service/load/clock/epoch/key/policy invalidan afectados y requieren revisión genuina, sin transferir garantía/approval/prueba/aceptación ni aplicar refresh/rebind activo.

Los siete retornos y dieciocho criterios cubren los tres entregables y tres salidas W04 con sus textos originales. PL01 aporta autoridad; PL02/PL03 caller/garantías; PL04 capacidad/servicio; PL05 reloj/ledger; PL06 inventario/reviews/decisión; PL07 gaps/parada. Todo sigue pendiente sobre el mismo scope/cuerpos y sujetos genuinos; no hay attestation o contrato de servicio emitido.

Los cuerpos/referencias/locators/bytes/digests/autores/providers/custodia/provenance, unidades y todos los supuestos, validez/currentness y motivos de review/decisión deben ser completos y disponibles. Inventario null y cero cuerpos aportados/rechazados/evaluados no prueban verdad o ausencia global. Ambos Readers y join global pagan todos los costes de lookup/freshness/identidad/crypto/native/IO/copias/registry/ledger/recibo/salidas/fallos/cleanup y nuevos mecanismos; no costes gratuitos offline, lecturas ocultas o caps tomados como fit/servicio/900.

## No admisión y handoff

Cuando falta garantía, mecanismo intrínseco, capacidad, unidad/servicio, demora, reloj o durabilidad, PL07 registra el requisito/cuerpo/scope/supuesto exacto y dependientes, manteniendo SD03/no admisión. No se contacta, mide, prueba/configura backend/plataforma/reloj/ledger/proceso/endpoint ni se ejecuta claim/replay/crash/restart para rellenarlo. El trabajo y autoridad separados necesarios no se conceden por este dictamen.

A05/RQ05 permanece detenido; requeriría A03/A04 genuinamente aceptados y sus límites propios. CE12 sigue privado, diferido y no autorizado; E06/payload/Q/root/admisión/claim/recibo finales no se añaden como nueva condición prelaunch. Se conservan cuatro prerrequisitos externos antes del claim y claim/construcción protegida antes del recibo; claim no es su propia precondición y estados inciertos/parciales/expirados/fallidos no habilitan retry gratuito.

Se mantiene I122 IMPLEMENTED_NOT_ADMITTED, CP07 falso, atomicidad correlacionada sin verificar, componentes/E06 NOT_RUN, PJC115-R2 sin habilitar, D5/H07 abiertos e IR03 NOT_READY. Cero lotes/gates/obligaciones cerrados; treinta gates pendientes y E01–E05 abiertas. No se crean fuentes/runtime records, C/Q/root/bindings, autoridad/destino, mapping/claim/worker/recibo o recursos reservados.

## Verificación y publicación

La [reconstrucción](../validation/D5-I260-I259-source-reconstruction.json) fija 1097 entradas contra blobs del commit base y registra 28 criterios. El [dictamen](../validation/D5-I260-I259-documentary-review.json) reproduce candidato/preparación I259 sin llamar mains de publicación históricos, conserva sus 43 rechazos documentales y añade 38 mutaciones en memoria sobre antecedentes, caller/roles, garantías/servicio/demoras, fases, capacidad/currentness/ledger, gaps/autoridad, cobertura, costes y aceptación. El [sello](../validation/D5-I260-integrity.json) preserva 789 archivos publicados y cuatro artefactos propios distintos del sello.

```text
python3 docs/validation/D5-I260-audit.py
PASS_STATIC_SOURCE_ONLY_A04_RQ04_REVIEW_PREDECESSORS_CALLER_PLATFORM_CAPACITY_SERVICE_PENDING_NOT_ADMITTED
```

Harness de runtime: **N/A**. Sólo JSON/Git/hashes/pointers/garantías/servicio/demoras/fases y comprobaciones documentales propias. Sin importar/compilar/ejecutar producto/componentes, discovery/tests/E06, build, medición, benchmarks, crypto/codec positivos, firma/keygen/enrollment/provisión/contactos/configuración registry/mapping/reloj/ledger/servicio o probes CPU/IO/procesos/endpoints/replay/crash/restart. Sin cuotas/reservas/capture_inputs o nuevos inputs/outputs/helpers/canales. No se inspecciona/limpia dev/run_data/D4 ni se reanudan I86/I89/I92.

Unidad documental con exceso de 400 líneas declarado por reconstrucción, pins y preservación; sin PR solicitado. Rollback limitado a retirar exactamente:

- `docs/design/D5-I260-I259-A04-RQ04-REVIEW.md`
- `docs/validation/D5-I260-I259-source-reconstruction.json`
- `docs/validation/D5-I260-I259-documentary-review.json`
- `docs/validation/D5-I260-audit.py`
- `docs/validation/D5-I260-integrity.json`

I260 termina esta revisión documental. La autoridad/aceptación genuina de los antecedentes y las garantías/cuerpos/decisiones de A04 siguen pendientes; publicar no los acredita ni habilita A05 o D5.
