# I232 — W04 consistente documentalmente; garantías reales pendientes

Fecha: 2026-11-24 · I223/W04 · PGO181 candidato 02 · PFC126-CANDIDATE-03/I122.

La revisión de [W04 de I231](D5-I231-W04-CALLER-PLATFORM-SERVICE.md) confirma la consistencia documental de sus fronteras de caller, plataforma y servicio con I223 y las políticas referenciadas. **Cero hallazgos de corrección documental. W01–W04 siguen sin aceptar y SD01 permanece activo.** No se acreditan identidades, ocho garantías, capacidad/servicio, reloj o mecanismo global reales. Se mantiene la no admisión de PJC115-R2, D5 abierto e IR03 `NOT_READY`.

El [dictamen estructurado](../validation/D5-I232-I231-documentary-review.json) registra cinco precisiones; la [reconstrucción](../validation/D5-I232-I231-source-reconstruction.json) fija 957 pins, 18 criterios y el mapping de 23 requisitos. El [candidato W04](../validation/D5-I223-W04-CALLER-PLATFORM-SERVICE-CANDIDATE.json) y los antecedentes permanecen intactos. El mismo asistente preparó I231 y realiza esta revisión metodológica: no aporta atestación R02, independencia R03/R06 ni aceptación separada R08.

## Los tres entregables W04

| Entregable I223 | Resultado documental | Evidencia auténtica pendiente |
|---|---|---|
| Caller, constructor, dominio y ocho garantías | CE05/CE06 y transporte I189 conservados con identidades y cuerpos ausentes | Humano requester/principal software, enrollment/custodia, constructor/aislamiento, origen exclusivo de canales y ocho garantías completas |
| Memoria y CPU/IO/scheduler o WCET | Ocho categorías de evidencia, métricas, procesos/interferencia, unidades/latencias y condiciones de carga explícitas | Lower availability bounds y servicio/WCET atestados para plataforma/runtime/procesos/validez exactos, con autoridad genuina |
| Reloj/epoch/currentness y ledger global | Políticas de frescura y mecanismo atómico/durable/high-water/rollback/crash/doble gasto conservadas | Pruebas genuinas del reloj y mecanismo concordante con mapping; sin ejecutar claim para obtenerlas |

Los cuatro roles R02/R03/R06/R08 y el proveedor/operador continúan sin persona canónica, competencia, nombramiento, scope/vigencia o decisión auténticos. La petición de revisar/publicar permite trabajo documental, sin designar actores canónicos, aceptar dependencias ni obtener pruebas mediante contacto, selección de plataforma o ejecución.

## Caller y ocho garantías

Se confirma la separación entre humano accountable requester y principal software caller. El origen/custodia debe vincular actor registry, imagen/runtime, dominio protegido y constructor exactos mediante evidencia previa. UID/PID/fd/env/module/cwd, strings, hashes, claves o appointment por sí solos no establecen identidad, origen o permiso funcional. El literal bootstrap-custody-only, frame, READY o firma tampoco autorizan captura/import funcional/claim/spawn.

Los ocho slots exactos siguen sin proveedor/cuerpo/hash/scope/aceptación y con verificación falsa: immutable_first_entry; no_loader_shadowing; no_descriptor_injection_or_duplication; no_hostile_tracing_or_memory_mutation; exclusive_parent_child_channel_origin; owned_paths_and_group_identity; no_unapproved_helper_or_input; exact_source_runtime_mapping. Su presencia en un schema o como flag no implementa ni prueba los mecanismos.

Dos pipes, seis operandos, ownership/cierre de duplicados, checks de argv/origen, framing, permisos de one-use y gramática I189 permanecen exactos. Los fd internos de runtime/spawn conservan obligaciones de cierre/ownership/coste. No se seleccionan números reales, endpoints, backend o constructor. El worker debe nacer en el dominio protegido; no recibe confianza mediante mapping/recibo/frame/argv nuevos. Cualquier ampliación real exige rechazo de la ruta sin cambios o contratos/grafo/bounds/costes versionados y revisados bajo autoridad separada.

## Disponibilidad, servicio y latencias

Las ocho referencias P03 cubren plataforma/runtime/validez, heap disponible, coordinador/worker/hijos/interferencia, servicio CPU o WCET, retardos, señales/retry/carga, reloj/contabilización y autoridad del proveedor. P03/I138 es un dossier histórico insuficiente de I122: sus hashes y requisitos no atestan la plataforma sucesora ni seleccionan proveedor.

La memoria distingue requested live heap, committed allocator heap y su correspondencia nativa/allocator/GC/H11, con scope/lifetime/solapamientos y procesos pertinentes. RSS, bytes serializados, address space reservado, límites ordinarios o reserva solicitada no son lower bounds de disponibilidad. Stacks y otros mappings no se incluyen silenciosamente en el heap. La ausencia de disponibilidad no se interpreta como cero o prueba automática de inviabilidad.

Ruta servicio/WCET, unidades de trabajo/tasa, lower rate garantizado, curva/latencia, WCET exact-platform, ventanas/procesos, condiciones de carga y derivación CPU→wall siguen nulos. Presupuesto, frecuencia nominal, ratio trabajo/budget, quota, watchdog/deadline o una muestra no suministran servicio atestado ni WCET justificado. CPU-time, wall-time y suma de CPU de procesos concurrentes no son intercambiables; servicio denegado y esperas requieren límites propios.

Las ocho obligaciones de retardo permanecen exactas: scheduler/denied service, locks, IO, hijos/reap, exit físico→retorno exacto True de wait_worker, startup/READY/RELEASE, cleanup/finalización/validación/publicación y señales/retry/backoff/interferencia. Son requisitos, no categorías medidas disjuntas. No se convierten desconocidos en cero ni se resta solapamiento sin prueba o duplica crédito de presupuesto.

Los candidatos I130 se conservan sin aplicarlos: requested 11 GiB, committed 12 GiB, reserva requested 832 MiB y overhead H11 1 GiB; fases 60/750/60 más 30 segundos de reserva y partición worker 600/90/60. No prueban demanda completa, capacidad realmente disponible o ajuste del programa. `tW` sigue siendo retorno exacto True de wait_worker, no exit físico; finalmente se incluyen validación/salidas/finally hasta `tF`. True no demuestra captura exitosa ni el watchdog prueba éxito dentro de 900 segundos. Cero transferencias o reservas reales.

Los cinco fragmentos I191 son exactos; caps caller 8.192 bytes y plataforma 16.384 son candidatos para cuerpos finales, no el wrapper, sus pruebas subyacentes o garantías de heap/CPU/servicio. Tamaños y fit de cuerpos reales siguen ausentes; codec/schema/crypto positivo no se ejecuta.

## Reloj y mecanismo global frente a claim real

El clock domain, monotonicidad, trusted-now, epoch/revocación y cuerpos de frescura permanecen ausentes. Se conserva error UTC máximo 5 segundos y vida de snapshots máxima 3.600 segundos con reglas estrictas y comprobaciones de vigencia en cada frontera. No se asume error cero, reloj local o fecha documental como evidencia confiable. No hay TOFU, cache obsoleta, lookup oculto online/archivo ni promesa de descubrir instantáneamente toda revocación.

El mecanismo one-use exige un único namespace global autoritativo para `(trust_context_sha256, runtime_request_sha256, invocation_id)` entre todos los callers/dominios aprobados y reinicios. Atomicidad/durabilidad, high-water/epoch, rollback/crash/doble gasto y tratamiento parcial siguen requiriendo prueba genuina. No basta particionar por caller/proceso. La invocación incierta/parcial se gasta o rechaza, sin retry gratuito; padre/hijo son una invocación correlacionada.

Prueba del mecanismo no equivale a claim/construcción/recibo reales ni requiere ejecutar esos eventos para aceptarse. El ledger debe concordar con el mapping único actual por `(configuration_epoch, SHA256(JCS(C)))` hacia bundle/caller/image/domain/ledger. Ese mapping posterior sigue ausente. Claim/construcción/recibo son CE12 diferido/no autorizado: autorización separada, final E06/payload/Q/root y admisión completa preceden a claim, y su evento real precede al recibo. Claim no es precondición de sí mismo y CE11 no depende de un recibo CE12 futuro.

## Requisitos y orden de aceptación

El mapping conserva 23 filas: 13 se asignan a W04 y 10 son referencias diferidas. CC07 mantiene CE06 como consumidor y, al estar CE05/CE06 dentro de W04, no se difiere fuera de W04. Las filas relacionadas no son trece garantías independientes.

| Filas | Consumidor | Dictamen |
|---|---|---|
| CC01–CC07 / PF01–PF06 | W04 | Caller y baseline de garantías/clock/mecanismo, sin aceptar sus pruebas por documentación |
| CC08 / PF07 | W05–W09 / CE07 | Trabajo, recualificación y composición completa recursos/compatibilidad |
| CC09 / PF08 | W10 / CE08 | Freeze actor→image→caller→platform antes de C |
| CC10 / PF09 | W11 / CE09 | Proyección C exacta y relaciones de requester/clock/validez |
| CC11 / PF10 | W12 / CE10 | Mapping único actual y bindings posteriores |
| CC12 / PF11 | CE12 fuera de prelaunch | Eventos reales bajo autorización separada, sin inventar otro paquete W |

La identidad del resource scope y un contrato de disponibilidad/servicio no prueban el trabajo, picos de heap o ajuste de fases del programa completo; el join permanece en W09. Los hechos auténticos de actores/imagen/caller/plataforma/capacidad/servicio, autores y cuerpos completos de pruebas deben estar autenticados antes de aceptar recursos. Freeze W10 y firmas futuras sólo reconcilian/fijan los mismos hechos; no pueden ser su única autenticación pronosticada. No se añade dependencia inversa del baseline hacia aceptar recursos/freeze/C/mapping/claim ni se aceptan esas fases implícitamente.

Cambios de contribuyentes, cuerpos, imagen/runtime, dominio, epoch/key, política o scope invalidan dependientes y exigen nueva revisión/recualificación. Ningún refresh/rebind activo se aplica en esta revisión. Todos los costes necesarios por intento de lookup/frescura/identidad/crypto/medición/copias/clock/ledger/registry/recibo/nativo/IO siguen dentro de fases y composición global E01–E05; build/enrollment previo u offline no los hace gratuitos.

## Estado y verificación

Los tres predicados de salida permanecen pendientes de evidencia real y decisiones competentes. `W04-REAL-EVIDENCE-PACKAGE` es el entregable previsto, sin paquete auténtico aceptado, record positivo, infraestructura o servicio creado. Siguen cero paquetes aceptados, cero de los 30 gates cerrados y cero obligaciones E01–E05 cerradas. I122 conserva `IMPLEMENTED_NOT_ADMITTED`, CP03 sólo en scope heredado, CP07/atomicidad correlacionada sin verificar y componentes `NOT_RUN`. No se emite `SOURCE_CAPACITY_VERIFIED` ni se cierra D5; CE12 sigue privado/deferido sin eventos reales emitidos aquí.

Comando exclusivamente documental: `python3 docs/validation/D5-I232-audit.py`.

Resultado: `PASS_STATIC_SOURCE_ONLY_W04_REVIEW_CALLER_PLATFORM_SERVICE_MISSING_NOT_ADMITTED`. La auditoría contrasta independientemente I223/CE01/CE05/CE06/P03/I130/I191, resuelve JSON pointers y verifica 957 pins contra blobs de la base I231 `50bc209cba4f825aa5e9719ed9f6f10be0c7d1b2`. Preserva 649 archivos publicados y exige cinco nuevos. Reproduce candidato/revisión de preparación I231 sin ejecutar mains históricos de publicación ni añadir proyección de presencia, con método de consulta restaurado. Treinta y dos mutaciones documentales negativas en memoria se rechazan. El PASS no aporta autenticidad, capacidad, independencia o admisión.

Runtime harness: **N/A**. Sólo documentos/JSON/Git/hashes/políticas y comprobaciones propias, sin ejecución/import/compile de producto/componentes, tests/benchmarks, builds, codec/crypto positivos, sampling/probes/medición de plataforma/reloj/ledger/servicios, endpoints/procesos/claim/replay/crash/restart, firma/keygen/enrollment/provisioning/contactos. No cambian cuotas, reservas, fuentes, schemas, Reader/canales, capture_inputs/bindings, autoridades/destinos o configuración activa.

Unidad documental única con commit/push solicitados, sin PR. Se declara el exceso de 400 líneas por pins, mapping, comparaciones independientes, comprobaciones y preservación. Reversión exacta limitada a:

- `docs/design/D5-I232-I231-W04-REVIEW.md`
- `docs/validation/D5-I232-I231-source-reconstruction.json`
- `docs/validation/D5-I232-I231-documentary-review.json`
- `docs/validation/D5-I232-audit.py`
- `docs/validation/D5-I232-integrity.json`
