# I259 — A04/RQ04: caller y garantías exigibles de plataforma

**A04/RQ04 queda preparado como borrador documental condicionado a A02 y A03 genuinamente aceptados.** Ambos siguen sin aceptar, al igual que A01; SD01 está activo. No se envía RQ04, selecciona operador/backend o inicia intake positivo. Se mantiene la **no admisión**, con treinta gates pendientes, E01–E05 abiertas y D5 sin cerrar.

Fecha: 2026-11-25, Europe/Madrid. Base: `091586874bfc50990d4b2d66f99b548a4970281d`.

El [dossier estructurado](../validation/D5-I251-A04-RQ04-CALLER-PLATFORM-SERVICE-CANDIDATE.json), `PGE251-A04-RQ04-CANDIDATE-01`, desarrolla A04 del [plan I251](D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.md) y conserva W04 y la [revisión I258](D5-I258-I257-A03-RQ03-REVIEW.md). Esa revisión no aceptó A03. Se prepara una solicitud y checklist de evidencia, sin emitir contrato atestado, capacidad de construcción, registry/record runtime, nueva autoridad o permiso funcional.

## RQ04 lista para revisión

**Destinatario por función:** custodio R02 y operador con autoridad real sobre caller/plataforma/capacidad/servicio. Persona, dirección, canal y autorización de contacto desconocidos. El original RQ04 de I251 queda vinculado literalmente, con esta ampliación:

> Borrador condicionado a A02/A03 genuinamente aceptados. Solicitar sólo material existente con autoridad/provenance propias PL01–PL06: caller/requester/constructor/dominio y origen intrínseco de canales; ocho garantías completas; capacidad real y servicio compatible o WCET con todas las condiciones y demoras; reloj/currentness y mecanismo global one-use/durable. Aportar cuerpos/locators/bytes/digests/autores/providers/custodia/validez, unidades y supuestos, revisiones R02/R03/R06 y decisión separada R08. Si falta garantía o backend intrínseco, PL07 y no admisión, sin suplirlo con cuota/benchmark/frecuencia/promesa. No se solicita seleccionar/implementar/probar/configurar backend, medir/probar plataforma/CPU/IO/reloj/ledger/procesos/endpoints, replay/crash/restart, claim, contacto, firma o ejecución. Recursos completos W05–W09, freeze W10, C W11, mapping W12 y claim/recibo CE12 siguen en sus fases. Los antecedentes siguen sin aceptar y RQ04 no se envía.

Los identificadores PL/AC son documentales, sin schema wire, nuevo archivo de captura, input/output Reader, helper, canal, fd/argv o configuración activos. La petición actual autoriza preparación/auditoría/publicación documental, sin adoptar un scope operativo o nombrar sujetos.

## Siete grupos de retorno

| Retorno | Evidencia genuina exigida |
|---|---|
| PL01 — Antecedentes y autoridad | A02/W02 y A03/W03 aceptados con autoridad A01 conservada; humanos/competencia/appointments/provenance/scope/vigencia de R02, operador y revisores R03/R06/R08 |
| PL02 — Caller y construcción | Requester humano y principal software separados; caller/actor/image/domain/constructor/loader, aislamiento y origen inmutable antes de código no confiable, custodia exclusiva de transporte I189 |
| PL03 — Ocho garantías | Cuerpos completos de mecanismo/enforcement de cada garantía, operador con autoridad real, scope exacto, supuestos/validez/provenance y revisiones |
| PL04 — Capacidad y servicio | Cotas inferiores reales de memoria disponible, métricas requested/committed, servicio compatible o WCET, todos los procesos/interferencias/condiciones y ocho demoras |
| PL05 — Reloj y ledger | Monotónico/UTC/currentness/epoch/revocación y mecanismo global one-use atómico/durable/high-water/rollback/crash/doble gasto, concordante con mapping |
| PL06 — Inventario y decisiones | Todos los cuerpos/referencias/bytes/digests/locators/autores/providers/custodia/unidades/supuestos, reviews R02/R03/R06 y decisión separada R08 con motivos |
| PL07 — Gaps y parada | Requisito/cuerpo/scope/supuesto ausente y dependientes, trabajo/autoridad separados necesarios; SD03/no admisión sin probar/configurar/ejecutar o cambiar cuotas |

Se conserva el contrato universal I251 para todas las entregas. Cada referencia real debe tener cuerpo completo disponible y provenance/autoridad propia, alcance/vigencia/currentness, unidades y todos los supuestos, sujetos elegibles y decisión trazable. Un hash, firma, booleano, plantilla, índice o PASS no prueba su verdad. El inventario recibido permanece null, listas aportadas/rechazadas vacías y evaluaciones reales cero; no se selecciona proveedor o calendario.

## Caller, constructor y ocho garantías

El caller debe ser un principal software existente bajo autoridad genuina, distinto del requester humano accountable. Su identidad y relaciones actor/imagen/dominio/constructor/loader requieren provenance previa, sin usar firmas futuras de bundle como única autenticación. UID/PID/fd/fstat/env/module/cwd/hash, appointment, C/I frame o READY por sí solos no son capacidad ni permiso de import/capture/claim/spawn. El literal bootstrap-custody-only sigue siendo política, sin permiso emitido.

Se exige mecanismo intrínseco existente de origen/aislamiento antes del primer código no confiable: no autenticar después de ejecutar desde cwd/PYTHONPATH/sitecustomize o con loader mutable. Los dos pipes y seis operandos I189 conservan origen, ownership, cierre de duplicados/extremos opuestos y dominios protegidos; los descriptores internos de spawn/runtime también necesitan clausura y costes propios. No se añade helper/proceso/canal/fd/argv/env/file de confianza ni se selecciona o invoca constructor para rellenar el expediente.

| Garantía | Respaldo exigido |
|---|---|
| immutable_first_entry | Origen de primera entrada inmutable |
| no_loader_shadowing | Resolución de loader sin sustitución |
| no_descriptor_injection_or_duplication | Exclusión de inyección/duplicación de descriptores |
| no_hostile_tracing_or_memory_mutation | Protección frente a tracing o mutación hostil |
| exclusive_parent_child_channel_origin | Origen exclusivo de canales padre/hijo |
| owned_paths_and_group_identity | Custodia de paths e identidad de grupo |
| no_unapproved_helper_or_input | Ausencia de helpers/inputs no aprobados |
| exact_source_runtime_mapping | Correspondencia fuente/runtime exacta |

Cada fila requiere mecanismo, cuerpo completo, bytes/digest/provenance/custodia, operador competente con facultad real, scope source/runtime/image/caller/domain/process y todos los supuestos/validez, más revisión/decisión genuinas. Se mantienen ocho slots sin verificar/aceptar. Una casilla true o descripción normativa no demuestra enforcement.

## Capacidad, servicio y demoras

Las ocho clases SV01–SV08 exigen plataforma/runtime/imagen/loader/dominio/configuración exactos; disponibilidad requested y committed allocator heap; procesos e interferencia compartida; unidades CPU/servicio compatibles o WCET; demoras completas; señales/retry/backoff/load; reloj/observación monotónicos; y autoridad/provenance/validez del proveedor. Las ocho peticiones están sin cuerpo, unidad, bound, attestation o derivación reales.

La memoria disponible se atesta separadamente de la demanda. Requested live heap y committed allocator heap no son bytes serializados, RSS, reserva virtual o cuota. Native/allocator/GC, vidas/overlap y contribuciones de coordinador/worker/hijos deben corresponder al modelo efectivo. Los candidatos 11GiB requested/12GiB committed, 832MiB sin asignar y H11 separado no acreditan disponibilidad ni reservan recursos. Los subbounds históricos/modelos incompletos tampoco prueban fit o inviabilidad.

El servicio debe dar unidades compatibles y curva inferior con latencia/ventanas/backlog/readiness/concurrencia, o WCET justificado para la plataforma exacta y sus condiciones. Carga/cache/memoria/configuración/validez e interferencia deben estar explícitas. CPU time, wall time y suma de procesos son magnitudes distintas; MHz, benchmark, deadline, cuota o trabajo dividido por900 no acreditan servicio. Una garantía de servicio y capacidad no sustituye las futuras derivaciones completas de demanda/heap/trabajo/fases de W05–W09.

| Demora | Evidencia temporal exigida |
|---|---|
| L01 | Scheduler/dispatch/servicio denegado |
| L02 | Contención/bloqueo de locks |
| L03 | Filesystem/pipe/stream IO |
| L04 | Terminación de hijos y reap |
| L05 | Exit físico hasta retorno exacto True de wait_worker |
| L06 | Startup/READY/RELEASE, incluido trabajo worker anterior a tR del padre |
| L07 | Cleanup/finalización/validación/publicación de éxito hasta tF |
| L08 | Señales/interrupciones/retry/backoff/interferencia |

No se trata demora desconocida como cero ni se resta solapamiento sin prueba. `tW` es retorno exacto True, no exit físico; `tF` incluye finally/salidas finales. Presupuestos 60/750/60+30=900 y worker600/90/60 no acreditan esas cotas o liveness, y no se reasignan reservas o servicio por afirmación.

## Reloj y mecanismo global one-use

La evidencia debe sustentar dominio monotónico/UTC, error real≤5, strict `not_before<expires_at`, lifetime≤3600 y reglas exactas de contención/comprobación de intervalos en sus fronteras aplicables. Epoch/revocación/currentness se aceptan bajo autoridad genuina, sin fecha/reloj host, TOFU, cache obsoleta o lookup oculto. Status offline limitado por vigencia no promete descubrimiento instantáneo de revocación. No se toma una muestra de reloj ni se emite snapshot.

El mecanismo existente debe demostrar un único namespace global para `(trust_context_sha256,runtime_request_sha256,invocation_id)` entre todos los callers/dominios/restarts, con atomicidad, high-water epoch, durabilidad/rollback/crash/doble gasto y tratamiento de claims inciertos/parciales. Padre/hijo son una sola invocación correlacionada, sin doble consumo; incertidumbre gasta o rechaza, sin retry gratuito. El ledger debe concordar con el dominio del mapping único previsto.

Probar el mecanismo mediante cuerpos existentes no equivale a efectuar un claim, crear mapping/ledger, ejecutar replay/crash/restart o emitir recibo. Mapping real epoch/digest C sigue en W12, C en W11 y claim/construcción/recibo en CE12. El worker tiene origen intrínseco protegido y validación independiente C/Q/root; no recibe un nuevo mapping/receipt/frame/helper como fuente de confianza.

## Veintitrés requisitos y orden de fases

| Requisitos | Consumidor conservado |
|---|---|
| CC01–CC07 y PF01–PF06 | Trece requisitos de caller/plataforma/reloj/ledger para A04/W04 |
| CC08 / PF07 | W05–W09/CE07: join completo de recursos |
| CC09 / PF08 | W10/CE08: freeze final actor→imagen→caller→plataforma |
| CC10 / PF09 | W11/CE09: C exacto |
| CC11 / PF10 | W12/CE10: bundle/mapping único actual |
| CC12 / PF11 | CE12: claim/construcción/recibo, fuera del cierre prelaunch |

Los 23 requisitos conservan sus fuentes, textos normativos y consumidores: trece aplicables a W04 y diez diferidos, incluidos los dos de ruta final. «Aplicable» expresa una obligación pendiente; no implica aceptación o progreso real. Las obligaciones posteriores no se eliminan ni se convierten en nueva dependencia inversa de W04.

Actor/imagen/caller/plataforma, capacidad/servicio, autores y cuerpos deben estar auténticamente sustentados antes de aceptar W09. W10 reconcilia/finaliza esos mismos hechos, sin autenticación retrospectiva ni bundle como única autoridad previa. Cambios de operador/autoridad/cuerpo/source/runtime/caller/domain/service/load/clock/epoch/key/policy invalidan afectados y exigen revisión genuina antes de avanzar. No se transfiere automáticamente garantía, prueba, aprobación o aceptación ni se aplica refresh/rebind activo.

## Aceptación, parada y handoff

Los tres entregables/salidas W04 se conservan literalmente y quedan cubiertos por caller/garantías PL02/PL03, capacidad/servicio PL04 y reloj/ledger PL05, con autoridad PL01 y reviews/decisión PL06. Los dieciocho criterios AC01–AC18 permanecen pendientes de antecedentes, garantías y decisión competente. R02/R03/R06 deben revisar bajo sus competencias y R08 aceptar/rechazar separadamente sobre el mismo scope/cuerpos, con motivos por requisito/salida. El mismo asistente y su auditor no realizan esas funciones genuinas.

Si falta respaldo de garantía, backend intrínseco, capacidad, unidad/servicio, demora, reloj o durabilidad, PL07 identifica el gap exacto y mantiene SD03/no admisión. No se ejecuta un probe, medición, configuración o claim ni se cambia cuota/reserva para llenar el expediente. Se registra el alcance y autoridad separados necesarios, sin inventar cota, proveedor, garantía o plazo. La ausencia de evidencia no acredita inviabilidad global.

A05/RQ05 sólo podría considerarse con A03 y A04 genuinamente aceptados y sus límites propios. Nada se envía, inicia o acepta. Ambos Readers y el join global conservan todos los costes por intento de lookup/freshness/identidad/crypto/native/IO/copias/registry/ledger/recibo/salidas/fallos/cleanup y nuevos mecanismos; no trabajo offline gratuito, inputs ocultos o caps tomados como fit/servicio/900.

CE12 permanece privado, diferido y no autorizado. No se añade la ejecución final E06/payload/Q/root/admisión/claim/recibo como nueva condición de aceptación prelaunch. Se conservan cuatro prerrequisitos externos antes del claim y claim/construcción protegida antes del recibo; claim no es su propia precondición y estados inciertos/parciales/expirados/fallidos no autorizan retry gratuito.

Se conserva I122 IMPLEMENTED_NOT_ADMITTED, CP07 falso, atomicidad correlacionada sin verificar, componentes/E06 NOT_RUN, PJC115-R2 sin habilitar, D5/H07 abiertos e IR03 NOT_READY. Cero lotes/gates/obligaciones cerrados. No se crean fuentes/runtime records, C/Q/root/bindings, authority/destination, mapping/claim/worker/recibo o recursos reservados.

## Verificación y publicación

La [preparación](../validation/D5-I259-preparation-review.json) fija 1092 entradas contra blobs del commit base, reproduce reconstrucción/revisión I258 sin invocar mains históricos y comprueba cuatro roles, ocho garantías, ocho clases de servicio/demora, veintitrés requisitos, siete retornos, dieciocho criterios y tres entregables/salidas. El [sello](../validation/D5-I259-integrity.json) preserva 784 archivos publicados y cuatro artefactos propios distintos del sello.

```text
python3 docs/validation/D5-I259-audit.py
PASS_STATIC_SOURCE_ONLY_A04_RQ04_PREPARED_PREDECESSORS_UNACCEPTED_CALLER_PLATFORM_SERVICE_MISSING_NOT_ADMITTED
```

El auditor rechaza 43 mutaciones documentales en memoria sobre antecedentes, envío/contacto, garantías inventadas, capacidad/servicio/unidades/demoras, reloj/ledger, fases, gaps/autoridad, costes y aceptación. Su PASS es metodológico; no es una attestation o contrato de servicio auténtico.

Harness de runtime: **N/A**. Sólo JSON/Git/hashes/pointers/cobertura/fases y comprobaciones documentales propias. Sin importar/compilar/ejecutar producto/componentes, discovery/tests/E06, build, medición, benchmark, crypto/codec positivos, firma/keygen/enrollment/provisión/contactos/configuración registry/mapping/reloj/ledger/servicio o probes CPU/IO/procesos/endpoints/replay/crash/restart. Sin cuotas/reservas/capture_inputs o nuevos inputs/outputs/helpers/canales. No se inspecciona/limpia dev/run_data/D4 ni se reanudan I86/I89/I92.

Una unidad documental con exceso de 400 líneas declarado por requisitos, pins y preservación; sin PR solicitado. Rollback limitado a retirar exactamente:

- `docs/design/D5-I259-A04-RQ04-CALLER-PLATFORM-SERVICE.md`
- `docs/validation/D5-I251-A04-RQ04-CALLER-PLATFORM-SERVICE-CANDIDATE.json`
- `docs/validation/D5-I259-preparation-review.json`
- `docs/validation/D5-I259-audit.py`
- `docs/validation/D5-I259-integrity.json`

I259 prepara el borrador RQ04. A02/A03 y las garantías/aceptación genuinas A04 siguen pendientes; publicar no acepta el lote ni autoriza obtenerlas mediante operaciones fuera del alcance actual.
