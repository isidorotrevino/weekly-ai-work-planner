# I237 — W07 preparado; trabajo, CPU y unidades compatibles sin probar

Fecha: 2026-11-24 · Plan I223/W07 · PGO181 candidato 02 · PFC126-CANDIDATE-03/I122.

W07 queda preparado como dossier documental de trabajo/CPU/esperas, compatibilidad de unidades y servicio del sucesor. **W07 no está aceptado; W01–W06 tampoco y SD01 permanece activo.** Faltan inventario completo, correspondencia all30, cotas transitivas, unidades/dominios/servicio compatibles o WCET justificado. Se mantiene la no admisión de PJC115-R2, D5 abierto e IR03 `NOT_READY`.

El [candidato W07](../validation/D5-I223-W07-SUCCESSOR-WORK-CPU-UNITS-CANDIDATE.json) conserva literalmente los tres entregables, tres predicados de salida, rechazos y autoridad futura de `/work_packages/6` de [I223](../validation/D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json). Vincula [I236/N04](../validation/D5-I236-I235-documentary-review.json): W03/W04/W05 siguen sin aceptar y trabajo/memoria alimentan las fases y el join sin adelantar decisiones. `W07-REAL-EVIDENCE-PACKAGE` identifica el entregable previsto; este wrapper no crea paquete auténtico aceptado, censo del sucesor, prueba WCET/servicio o record positivo BASIS/índice/I191.

## Tres entregables preparados

| Entregable W07 | Preparación documental | Prueba real pendiente |
|---|---|---|
| Inventario completo y correspondencia all30 | Diez actividades, treinta slots work/CPU/wall, veinte vectores y veinte cruces históricos fijados por fuente | Inventario efectivo del sucesor o correspondencia genuinamente revisada que cumpla all30 sin reducirlo ni inventar IDs |
| Cotas y unidades compatibles o WCET | Dos rutas condicionales de prueba, diez obligaciones de latencia y nueve registros fase/categoría | Trabajo transitivo/CPU/IO/espera/scheduler/hijos/observación completos, unidades/servicio/runtime/plataforma, supuestos y derivación auténticos |
| Ledger por intento y composición | Siete familias de costes, ambos Reader y toda la clausura W05, sin restar overlap no probado | Operaciones/conteos/unidades/procesos/fases reales, cobertura completa y revisión competente |

## Referencias históricas, sin equivalencia automática

| Referencia | Contenido preservado | Límite |
|---|---|---|
| C01–C10 I130 / I223 | Diez actividades y sus ventanas/procesos/categorías históricos | No son inventario completo del código sucesor |
| Treinta slots | Diez actividades × work/CPU/wall, con upper real nulo | No son treinta actividades o grupos distintos |
| Veinte vectores P06 | Proceso/fase/work/unidad/WCET/espera/observación/derivación | No enumeran todos los procesos/threads/hijos reales |
| Veinte cruces P07 | Runtime/plataforma/dominio/unidad/tasa/latencia o WCET | Compatibilidad no verificada; ningún servicio aceptado |
| Diez latencias / nueve fase-categoría | Atribución y composición requeridas | No son cotas medidas, categorías disjuntas o presupuesto extra |

El requisito «all30 work groups» de I193 se conserva íntegro. No se llena con G01–G30 predictivos, los treinta slots escalares, los 12 grupos de raíces o los 30 sitios atómicos de W05. La correspondencia e inventario reales permanecen nulos, sin autores, supuestos o aceptación. Nuevas rutas/transitivos del sucesor deben incluirse aunque no tengan fila histórica.

P06/I163–I164 y P07/I165–I166 son dossiers históricos insuficientes de I122. Sus hashes/documentos, referencias de source y cotas parciales no cualifican al sucesor. Las oportunidades abstractas I124, clones/visitas/generaciones/bytes o oportunidades de procesos no son instrucciones, CPU-seconds, PIDs o servicio. Se preservan sus precondiciones; no se transfieren automáticamente a la clausura cambiada ni se prueba inviabilidad o éxito desde un upper abstracto laxo. No se sustituye retain-all por 33 generaciones/GC inmediato ni se omite noncopy como cero.

## Actividades y cobertura temporal

| Actividad histórica | Cobertura requerida |
|---|---|
| C01 | Registry/autoridad/discovery/inputs iniciales del coordinador |
| C02 | Startup/import/nativo/canales del worker y threads antes de main/READY/RELEASE |
| C03 | Constructor, READY, RELEASE/newline/close del coordinador hasta tR |
| C04 | Trabajo post-recepción RELEASE del worker/hijos que puede preceder al close tR del coordinador |
| C05 | Trabajo que continúa a partir de tR hasta salida física del worker |
| C06 | Dispatch/observación/reap y retorno exacto True de wait_worker en tW |
| C07 | Cleanup normal y comprobaciones frescas after/finish |
| C08 | Evidencia read/parse/hash/pages/aggregate/finish |
| C09 | Finally, closes, listing/sizes/context encode y escrituras context/launch hasta retorno tF |
| C10 | Originales/proyección/JSON/Unicode/hash/sort/nativo/GC/destrucción/allocations/locks por proceso y ventana |

Las etiquetas de función o source-order no prueban el calendario entre procesos. Recibir RELEASE en el worker no es tR: imports, suite, observers, hijos o finish post-recepción pueden ejecutarse antes de que el coordinador cierre el extremo. Tpre debe cubrir ese trabajo o un sobreconteo conservador completo justificado, sin asignarlo todo automáticamente a Tworker. C02 incluye startup previo a main.

La salida física no es tW, incluso si precede a tR o a la invocación wait. La observación/dispatch/reap/retorno del coordinador permanece en Tworker. True no demuestra captura exitosa ni las validaciones posteriores mueven tW. False/excepción/timeout/cleanup no sustituyen el marcador calificado. packet.finish no es tF: C09 incluye finally, validaciones y dos salidas/closes hasta retorno normal, con elegibilidad de éxito independiente.

C10 es transversal dentro de fases, no un tail gratuito, noncopy cero o presupuesto adicional. Todos los originales, imports, native/crypto/codecs, allocations/GC/destrucción, IO/locks, hijos/threads y transitivos de éxito/rechazo/timeout/fallo/cleanup conservan obligación de cobertura. Inventario efectivo de operaciones/procesos/fases y prueba de no omisión siguen ausentes.

## Conversión trabajo/servicio o WCET

La ruta sigue sin seleccionar; trabajo total W, unidad, tasa inferior r, unidad de tasa, latencia L, WCET y teorema/derivación completos permanecen nulos. La curva de servicio o WCET no se mide ni se cualifica aquí.

Para una ruta de servicio se requieren trabajo transitivo completo, garantía inferior atestada y dominio/unidades/runtime/plataforma/procesos/validez compatibles. Llegadas, backlog inicial, readiness, concurrencia y ventanas de aplicación deben estar justificados. Para beta(dt)=r·max(0,dt−L), r>0, **L+W/r sólo es utilizable bajo un teorema aplicable que pruebe servicio de todo W con esas premisas**; no se calcula dividiendo clones o bytes por un objetivo de tiempo.

Una tasa por CPU-time sólo permite concluir tiempo de ejecución CPU bajo sus hipótesis; wall necesita además límites de servicio denegado, IO/hijos, scheduling y observación. Una tasa por wall debe declarar qué delays incluye. CPU sumada entre procesos concurrentes no equivale a elapsed del coordinador. Latencias por proceso/ventana necesitan composición justificada, sin double credit o restas de overlap no demostrado.

La alternativa WCET requiere prueba para runtime/plataforma exactos, originales/native/codecs/GC/destrucción completos y supuestos de memoria/cache/allocator/carga/interferencia válidos. Debe declarar si acota CPU o wall y cubrir delays restantes. MHz, core count, frecuencia, cuotas ordinarias, watchdog/deadline, W/budget o W/900 no constituyen garantía de servicio. Ninguna ruta puede tratar trabajo/latencia desconocidos como cero.

W04 conserva servicio sin atestar, sin ruta, unidad, tasa/curva/latencia/WCET/proveedor válidos o matching real de plataforma/runtime/procesos. Esos campos se referencian sin rellenarlos con políticas, nombres o hashes. La prueba estática/servicio futuros sólo serán admisibles con cuerpos, autores/authority/provenance, supuestos y revisión competentes reales.

## Ledger de costes y presupuestos

Las siete familias CE07 conservan ambos Reader físicos y lecturas repetidas; lookup/registry/canonicalización/parse/hash/identidad/keys/crypto; freshness/revocación/reloj/ledger/locks/claim durable/recibo; frames/attempts/prefijos rechazados/dos pipes; copias/sort/Unicode/codecs/nativo/allocator/GC/destrucción/frames/tracebacks; doble output/validación/fallo/cleanup; y startup/originales/hijos/threads/scheduler/IO/observación/finally.

Su inventario operativo, conteos/unidades/cotas y asignación proceso/fase están pendientes, sin aceptar ninguna familia. Captura/custodia/bootstrap/ledger/output añaden trabajo real que no se descarga con los conteos heredados. Los envelopes de input file-bytes no son CPU, todo el IO o un split automático de fases; snapshots no son lecturas frescas. Offline/enrollment/build previos no hacen gratuito el trabajo requerido por intento.

La desigualdad requerida sigue sin demostrar:
`Tworker <= U_CPU + U_IO_child_wait + U_scheduler_observation <= 600+90+60 = 750`.

Vector real, suma verificada y prueba de la desigualdad permanecen nulos/falsos. Los 600/90/60 son presupuestos candidatos, sin garantías ni asignación adicional por grupo, proceso, thread, ventana o categoría. C04/Tpre no recibe otro CPU600. Las fases 60/750/60 más reserva 30 conservan el objetivo 900; no se transfiere reserva ni se reservan recursos. Un watchdog de wait no prueba éxito end-to-end o cleanup dentro de 900 segundos.

## Handoff y fronteras

W03 mantiene pendiente el baseline efectivo; W04, garantías de servicio/capacidad; W05, clausura completa de rutas/operaciones. W06 memoria y W07 trabajo son inputs paralelos de W08, conforme al grafo I223. W07 no exige aceptar W06 como dependencia inversa, pero los supuestos de memoria/cache/allocator/interferencia deberán reconciliarse y justificarse: no se toman prestados de una prueba ausente.

W08 debe componer trabajo/servicio/delays, memoria y marcadores exactos para éxito; W09 acepta conjuntamente recursos/BASIS/índices con cuerpos y decisiones genuinos. W07 no demuestra heap W06, éxito900 W08 o E01–E05 W09. No se añade dependencia inversa del baseline hacia freeze, C, mapping, E06, root, claim o recibo.

Hechos efectivos, autores, cuerpos y supuestos completos deben autenticarse antes de W09. W10 reconcilia los mismos hechos; cambios de contribuyentes/fuentes/runtime/imagen/caller/plataforma/ledger/epoch/key/política/scope invalidan lo afectado y exigen nueva revisión. Ningún resultado final, bundle/root o freeze futuro puede ser la única autenticación previa. No se aplica refresh/rebind activo. CE12 sigue privado/deferido tras sus prerrequisitos reales, sin claim/worker/recibo y sin dependencia CE11 de un recibo futuro.

## Autoridad, estado y verificación

R03/R06 y R08, autores de análisis/WCET/proveedor y sus competencias/appointments/cuerpos permanecen ausentes. El mismo asistente prepara el dossier sin revisión independiente R03/R06 o aceptación separada R08. Los tres predicados de salida siguen pendientes de evidencia real.

Sólo se realizan lectura documental/Git/hashes/presencia exacta, preparación, auditoría propia y commit/push. No se ejecutan producto/componentes, import/compile/test discovery, tests/benchmarks/builds, WCET experimental, probes/schedule/CPU/IO/service/platform/reloj sampling, codec/crypto positivos, ledger/claim/procesos/signing/keygen/enrollment/provisioning/servicios/contactos. No se crean helpers/canales/Reader/inputs/salidas implícitos ni se cambian cuotas, presupuestos/reservas, fuentes, schemas, capture_inputs/bindings o autoridades/destinos.

Siguen cero paquetes aceptados, cero de los 30 gates cerrados y cero obligaciones E01–E05 cerradas. I122 conserva `IMPLEMENTED_NOT_ADMITTED`, CP03 sólo en scope heredado, CP07/atomicidad correlacionada sin verificar y componentes `NOT_RUN`. No se emite `SOURCE_CAPACITY_VERIFIED`, no se habilita PJC115-R2 y D5 sigue abierto.

Comando exclusivamente documental: `python3 docs/validation/D5-I237-audit.py`.

Resultado exigido: `PASS_STATIC_SOURCE_ONLY_W07_WORK_CPU_UNITS_MISSING_SD01_ACTIVE_NOT_ADMITTED`. La [revisión de preparación](../validation/D5-I237-preparation-review.json) reconstruye el candidato, resuelve pointers y verifica 982 pins contra blobs de la base I236 `ca16f4a34a839e2fe16692508f53fee0e0835f74`. Comprueba diez actividades/treinta slots/veinte vectores/veinte cruces/diez latencias/nueve categorías/siete familias y estados desconocidos. Reproduce reconstrucción/revisión documental I236 sin mains históricos de publicación ni nueva proyección de presencia, con método de consulta restaurado. Treinta y tres mutaciones negativas sólo en memoria deben rechazarse. El [sello](../validation/D5-I237-integrity.json) preserva 674 archivos publicados y fija los otros cuatro artefactos.

Runtime harness: **N/A**. Sólo documentos/JSON/Git/hashes/requisitos y comprobaciones propias, sin producto/componentes/schedule/CPU/IO/servicio/runtime/plataforma ejecutados o medidos. El PASS no acredita trabajo/tiempo, unidades compatibles, WCET/servicio, independencia o admisión.

Unidad documental única con commit/push solicitados, sin PR. Se declara el exceso de 400 líneas por actividades/slots/vectores/cruces/latencias, reglas de conversión/fases/handoffs, pins, comprobaciones y preservación. Reversión exacta limitada a:

- `docs/design/D5-I237-W07-SUCCESSOR-WORK-CPU-UNITS.md`
- `docs/validation/D5-I223-W07-SUCCESSOR-WORK-CPU-UNITS-CANDIDATE.json`
- `docs/validation/D5-I237-preparation-review.json`
- `docs/validation/D5-I237-audit.py`
- `docs/validation/D5-I237-integrity.json`
