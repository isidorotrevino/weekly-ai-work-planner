# I231 — W04 preparado; caller, plataforma y servicio sin acreditar

Fecha: 2026-11-24 · Plan I223/W04 · PGO181 candidato 02 · PFC126-CANDIDATE-03/I122.

W04 queda preparado como dossier documental de evidencia faltante de caller, plataforma y capacidad/servicio. **W04 no está aceptado; W01–W03 tampoco y SD01 permanece activo.** No se selecciona proveedor, plataforma, constructor o backend ni se crean mecanismos de reloj/ledger. Se mantiene la no admisión de PJC115-R2, D5 abierto e IR03 `NOT_READY`.

El [candidato W04](../validation/D5-I223-W04-CALLER-PLATFORM-SERVICE-CANDIDATE.json) conserva los tres entregables, tres predicados de salida, rechazos y autoridad futura de `/work_packages/3` de [I223](../validation/D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json). Vincula [I230/N01](../validation/D5-I230-I229-documentary-review.json): preparar documentación no satisface las dependencias W02/W03 ni inicia progreso positivo. `W04-REAL-EVIDENCE-PACKAGE` identifica el entregable previsto; este wrapper no crea ese paquete auténtico aceptado, caller_identity/platform_custody positivos o una implementación de plataforma/ledger.

## Los tres entregables

| Entregable W04 | Preparación documental | Material real pendiente |
|---|---|---|
| Caller, constructor, dominio y ocho garantías | Políticas CE05/CE06 y transporte I189 conservados; slots de pruebas y relaciones exactas | Humano requester y principal software auténticos, enrollment/custodia, constructor/aislamiento/origen de canales y ocho proof bodies genuinos |
| Memoria y servicio CPU/IO/scheduler o WCET | Ocho categorías de evidencia, métricas requested/committed, proceso/interferencia, unidades/latencias y cargas admisibles | Capacidad realmente disponible y servicio/WCET atestados por proveedor competente para plataforma/runtime/procesos y validez exactos |
| Reloj/currentness y mecanismo one-use | Política de reloj/epoch/revocación y ledger global durable/high-water/rollback/crash/doble gasto | Pruebas auténticas de mecanismo, reloj y mapping concordantes; ningún claim real se ejecuta para obtenerlas |

R02/R03/R06 conservan la revisión primaria prevista y R08 la aceptación separada. Los cuatro slots, el proveedor/operador y su autoridad para prometer garantías siguen ausentes. El mismo asistente prepara el dossier, sin atestación competente R02, independencia R03/R06 o aceptación R08.

## Caller y garantías

La identidad humana del accountable requester es distinta del principal software/service/process. El caller deberá vincular actor registry, imagen/runtime, dominio protegido y constructor exactos mediante evidencia previa auténtica. UID/PID/fd/env/module/cwd, hashes, nombres, clave, appointment, frame, READY o firma por sí solos no prueban origen, capacidad o permiso funcional.

El literal bootstrap-custody-only es política de schema, no autorización emitida. C/Q/root, mapping y constructor admitido conservan sus relaciones posteriores; el bundle futuro no puede ser la única autenticación pronosticada de hechos caller/plataforma. El registro documental no implementa el mecanismo de constructor/loader/privilegios/aislamiento.

Las ocho garantías exactas I191 permanecen con proveedor/cuerpo/hash/scope/aceptación ausentes y verificación falsa:

| Garantía | Alcance exigido |
|---|---|
| immutable_first_entry | Primera entrada inmutable antes de código no confiable |
| no_loader_shadowing | Origen aceptado de loader/módulo/imagen sin sustitución |
| no_descriptor_injection_or_duplication | Controles reales contra inyección/duplicación de descriptores |
| no_hostile_tracing_or_memory_mutation | Exclusión acreditada de tracing hostil y mutación de memoria |
| exclusive_parent_child_channel_origin | Custodia y origen exclusivos de canales/construcción padre-hijo |
| owned_paths_and_group_identity | Ownership y sesión/grupo/identidad correlacionados |
| no_unapproved_helper_or_input | Scope efectivo sin helpers/inputs no aprobados |
| exact_source_runtime_mapping | Mapping auténtico fuente/runtime/imagen/caller del dominio |

Se conservan dos pipes, seis operandos, ownership, cierre de duplicados, checks de argv/origen, framing, permisos y límites I189. También se exige contabilizar descriptores internos de runtime/spawn. El worker debe nacer en el dominio aceptado; no recibe confianza nueva mediante mapping/recibo/frame/argv añadidos. Si el backend real necesita ampliar rutas/helpers/fd/canales/inputs/attestations, deberá rechazarse la ruta sin cambios o revisarse explícitamente contratos/grafo/costes bajo autoridad separada. No se construye ni prueba transporte aquí.

## Capacidad y servicio: ocho categorías de prueba

El ledger referencia los requisitos de P03 histórico sobre pins plataforma/runtime/validez; memoria disponible; coordinador/worker/hijos/interferencia; servicio CPU o WCET; retardos; señales/retry/carga; reloj/contabilización; y autoridad/provenance del proveedor. P03/I138 siguen siendo un dossier histórico insuficiente de I122, sin atestación de la plataforma sucesora. Sus hashes documentales no aportan garantías reales.

La capacidad debe distinguir peak live requested heap de committed allocator heap bajo backend/nativo/GC y métricas exactos. H11, metadata/retención/desperdicio y solapamientos requieren correspondencia demostrada. RSS, bytes serializados, address space reservado, límites ordinarios y reservas solicitadas no son capacidad disponible; stacks y otros mappings no se incluyen silenciosamente en el heap. Coordinador, hijos, recursos compartidos e interferencia conservan su scope propio. Los dos lower bounds de disponibilidad y sus condiciones de validez siguen nulos; desconocido no significa cero ni prueba de inviabilidad.

La ruta de servicio o WCET sigue sin seleccionar. Unidad de trabajo, unidad/rate inferior garantizado, curva/latencia, ventana/procesos, WCET justificado, atribución de esperas y derivación CPU→wall permanecen nulos. Frecuencia nominal, ratio trabajo/presupuesto, quota, watchdog/deadline o una muestra empírica no sustituyen servicio atestado o WCET justificado. Sumar CPU de procesos concurrentes no produce elapsed wall; una tasa por CPU-time requiere límites separados de servicio denegado/espera/scheduling.

Las ocho obligaciones de latencia conservan scheduler/denied service, locks, filesystem/pipes/IO, finalización/reap de hijos, exit físico→retorno exacto True de wait_worker, startup/READY/RELEASE, cleanup/finalización/validación/publicación y señales/retry/backoff/interferencia. No son categorías medidas disjuntas. Sin prueba no se resta solapamiento ni se da doble crédito de presupuesto; unknown no se convierte en cero.

Los candidatos I130 se conservan: requested 11 GiB, committed 12 GiB, reserva requested 832 MiB y overhead H11 1 GiB. Siguen sin demostrar demanda completa, capacidad disponible o fit. Fases 60/750/60 más reserva 30 segundos y partición worker 600/90/60 son presupuestos candidatos, sin servicio verificado ni transferencias. `tW` es el retorno exacto True de wait_worker, no exit físico; se conserva todo finally y salidas hasta `tF`, y True no prueba éxito de captura. No se demuestra el claim de éxito en 900 segundos.

## Reloj y ledger: mecanismo antecedente, claim diferido

Se requieren clock domain aceptado, monotonicidad, frescura UTC/error conservador ≤5 s, epoch actual, revocación conocida y snapshots estrictos con vida ≤3.600 s. Se preservan las reglas temporales completas del perfil02, sin reloj/trusted-now/muestras o error reales suministrados. No se asume error cero ni se usa reloj del host/fecha del chat. No se introduce TOFU, cache obsoleta o lookup oculto online/archivo, ni garantía de descubrir instantáneamente toda revocación.

El ledger exige un namespace autoritativo global para `(trust_context_sha256, runtime_request_sha256, invocation_id)` a través de todos los callers/dominios aprobados y reinicios. Deben acreditarse atomicidad, durabilidad, high-water/epoch, rollback/crash/doble gasto y consumo parcial; su dominio debe concordar con el mapping único. Padre e hijo son una invocación correlacionada. Ante incertidumbre o claim parcial se gasta o rechaza, sin retry gratuito ni reutilización.

La prueba del mecanismo no es un claim, backend seleccionado o recibo real. No se ejecutan invocaciones, probes, replay/crash/restart, endpoints o procesos para preparar evidencia. El mapping posterior exige una única relación actual por `(configuration_epoch, SHA256(JCS(C)))` hacia bundle/caller/image/domain/ledger; sus cuerpos y estado siguen ausentes. Claim/construcción/recibo pertenecen a CE12 diferido/no autorizado, tras autorización separada, final E06/payload/Q/root y admisión completa. Claim no es precondición de sí mismo; su evento real precede al recibo. CE11 no adquiere dependencia de un recibo futuro.

## Requisitos y fronteras de fase

El ledger vincula 23 filas exactas de CE05/CE06. Trece se asignan a W04: CC01–CC07 y PF01–PF06; CC07 conserva su consumidor CE06 aunque fuera diferido respecto de CE05. Son obligaciones relacionadas, no trece garantías independientes. Diez se mantienen diferidas:

| Filas | Consumidor | Frontera |
|---|---|---|
| CC08 / PF07 | W05–W09 / CE07 | Recualificación, trabajo y composición completa de recursos/compatibilidad |
| CC09 / PF08 | W10 / CE08 | Freeze actor→image→caller→platform antes de C |
| CC10 / PF09 | W11 / CE09 | Proyección exacta C, requester/constantes/clock/validez/relaciones |
| CC11 / PF10 | W12 / CE10 | Mapping único actual y bindings/aprobaciones posteriores |
| CC12 / PF11 | CE12 fuera del prelaunch | Claim/construcción/recibo reales bajo autorización separada; no se inventa otro paquete W |

La identidad del resource scope y un contrato de disponibilidad/servicio no prueban el trabajo completo del programa, sus picos o el ajuste de fases. El join completo sigue en W09, sin convertirse en dependencia inversa del baseline W04. Hechos de actores/imagen/caller/plataforma y garantías auténticas de capacidad/servicio deben estar autenticados antes de aceptar recursos, con autores y cuerpos completos conocidos. W10 sólo reconcilia los mismos hechos, sin autenticación retrospectiva desde freeze/bundle. Cambios de contributors, cuerpos, imagen/runtime, dominio, epoch/key, política o scope invalidan dependientes y exigen nueva revisión; no se aplica rebind/refresh activo.

Los cinco fragmentos I191 caller_identity, platform_custody, identity, evidence_reference y validity permanecen exactos. Los caps candidatos caller 8.192 bytes y plataforma 16.384 bytes corresponden a cuerpos futuros, no al wrapper ni a todas sus pruebas. Codec/schema/crypto sobre cuerpos reales, tamaños y fit siguen sin ejecutar ni demostrar.

## Autoridad, costes y estado

Sólo se autoriza lectura documental/Git/hashes, preparación, auditoría propia y commit/push. No se selecciona/configura/mide plataforma o servicio, ni se realizan probes/reloj/ledger/claim/endpoints/procesos/contactos, firmas/keygen/enrollment/provisioning o ejecución de producto/componentes. No se incluyen comandos operativos. Cada acción futura requiere su autoridad exacta y cobertura de costes, sin inferirla de este dossier.

Lookup/frescura/identidad/crypto/medición/copias/reloj/ledger/registry/recibo/nativo/IO necesarios por intento siguen dentro de fases y composición global E01–E05. Enrollment previo u offline no hacen gratuito trabajo requerido durante launch. No cambian cuotas, reservas, presupuestos, sources, schemas, Reader/canales, capture_inputs/bindings, autoridad/root o destino.

Los tres predicados de salida siguen pendientes de evidencia, revisión R02/R03/R06 y aceptación R08 genuinas. Continúan cero paquetes aceptados, cero de los 30 gates cerrados y cero obligaciones E01–E05 cerradas. I122 conserva `IMPLEMENTED_NOT_ADMITTED`, CP03 sólo en scope heredado, CP07/atomicidad correlacionada sin verificar y componentes `NOT_RUN`; no se emite `SOURCE_CAPACITY_VERIFIED`. CE12 permanece privado/deferido, sin claim, worker, root o recibo reales creados por esta preparación.

## Verificación y publicación

Comando exclusivamente documental: `python3 docs/validation/D5-I231-audit.py`.

Resultado exigido: `PASS_STATIC_SOURCE_ONLY_W04_CALLER_PLATFORM_SERVICE_MISSING_SD01_ACTIVE_NOT_ADMITTED`. La [revisión de preparación](../validation/D5-I231-preparation-review.json) reconstruye el candidato, resuelve pointers y verifica 952 pins contra blobs de la base I230 `b845f94da77cc353275424d84fba146f3bd415c6`. Reproduce reconstrucción/revisión documental I230 sin llamar mains históricos de publicación ni añadir proyección de presencia, con método de consulta restaurado. Veintiocho mutaciones negativas en memoria deben rechazarse. El [sello](../validation/D5-I231-integrity.json) preserva 644 archivos publicados y fija los otros cuatro artefactos.

Runtime harness: **N/A**. Sólo JSON/Git/hashes/políticas/roles y comprobaciones documentales propias, sin ejecución/import/compile de producto o componentes, tests/benchmarks, builds, codec/crypto positivos, sampling/probes/medición de plataforma/reloj/ledger/servicio, endpoints/procesos/claim/replay/crash/restart, firma/keygen/enrollment/provisioning/servicios/contactos. El PASS documental no prueba garantía, capacidad, independencia o admisión.

Unidad documental única con commit/push solicitados, sin PR. Se declara el exceso de 400 líneas por pins, matrices de caller/garantías/servicio/latencias/fases, comprobaciones y preservación. Reversión exacta limitada a:

- `docs/design/D5-I231-W04-CALLER-PLATFORM-SERVICE.md`
- `docs/validation/D5-I223-W04-CALLER-PLATFORM-SERVICE-CANDIDATE.json`
- `docs/validation/D5-I231-preparation-review.json`
- `docs/validation/D5-I231-audit.py`
- `docs/validation/D5-I231-integrity.json`
