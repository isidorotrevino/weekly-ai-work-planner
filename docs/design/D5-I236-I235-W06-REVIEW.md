# I236 — W06 consistente documentalmente; heap y vidas sin aceptar

Fecha: 2026-11-24 · I223/W06 · PGO181 candidato 02 · PFC126-CANDIDATE-03/I122.

La revisión de [W06 de I235](D5-I235-W06-SUCCESSOR-HEAP-LIFETIMES.md) confirma la consistencia documental de sus cotas requeridas, vidas, rollup y fronteras de fase con I223. **Cero hallazgos de corrección documental. W01–W06 siguen sin aceptar y SD01 permanece activo.** Las cotas completas, picos/vidas, fits/slack y capacidad real siguen desconocidos. Se mantiene la no admisión de PJC115-R2, D5 abierto e IR03 `NOT_READY`.

El [dictamen estructurado](../validation/D5-I236-I235-documentary-review.json) registra cinco precisiones; la [reconstrucción](../validation/D5-I236-I235-source-reconstruction.json) fija 977 pins, 20 criterios y once assessments de owner sin bound/fit aceptados. El [candidato W06](../validation/D5-I223-W06-SUCCESSOR-HEAP-LIFETIMES-CANDIDATE.json) y todos los antecedentes permanecen intactos. El mismo asistente preparó I235 y realiza esta revisión metodológica: no acredita competencia/independencia R03 ni aceptación separada R08.

## Tres entregables de I223/W06

| Entregable | Resultado documental | Prueba real pendiente |
|---|---|---|
| Once derivaciones H01–H11 | Owner/task/metric/unit/budget y referencias históricas exactos | Inventarios efectivos, cardinalidad/tamaño, vidas/picos/transitorios, ABI/allocator/nativo/GC, cuerpos/autores/supuestos y decisiones |
| Cierre de native/allocator/GC y procesos/solapamientos | 132 clases, 55 parejas/110 direcciones, ocho familias nuevas y ocho de fases conservadas | Pertenencia/aliases/domino, retención/concurrencia y cobertura completa o sobreconteo conservador justificado |
| Requested/committed y capacidad W04 | Reglas condicionales y presupuestos intactos; sumas/fit/slack reales nulos | Derivación completa de backing/H11, rollup compatible y capacidad independiente realmente disponible con scope/validez concordantes |

Se conservan literalmente tres predicados de salida, rechazos y autoridad futura de `/work_packages/5`. La dependencia W03/W04/W05 sigue sin aceptar; preparar/revisar/publicar documentación no satisface esos gates. `W06-REAL-EVIDENCE-PACKAGE` identifica el entregable previsto, sin paquete auténtico aceptado, allocation trace o proof record positivo.

## Owners, clases y fronteras

Los once owners coinciden con I130/I223 y sus dossiers y últimas revisiones históricos. H01–H10 conservan peak_requested_live_heap; H11, allocator_overhead; todos en exact_integer_bytes. Ningún budget se aplica como cuota o se presenta como upper completo. Mapping efectivo, allocations, cardinalidad/tamaño/vida, upper, fit, slack, autores/custodia y revisión del sucesor permanecen nulos.

Las 132 clases coinciden fila por fila con los once expedientes históricos. Las 55 parejas son exactamente todas las combinaciones de dos owners entre H01–H11; cada una conserva ambas direcciones, 110 en total, y permanece sin resolver. Esta comprobación de cobertura del índice no demuestra que estén reconciliadas identidad física, dominio, pertenencia, retención o vida del sucesor.

El conjunto histórico de clases/parejas y las ocho familias nuevas no es inventario completo de allocations del nuevo código. P04/P05/I162 y las cotas parciales no transfieren aceptación. El modelo condicional H04 de unos 23 PB no es upper completo ni lower de demanda que pruebe inviabilidad; no se reemplaza por 33 generaciones o GC inmediato. Los payload submodels H08/H09/H10 no prueban heap total ni slack utilizable.

## Métricas, procesos y vidas

Requested live heap, committed allocator backing y overhead H11 requieren dominios exactos y correspondencia de allocations. RSS, stacks, otros mappings, bytes serializados/typed caps, getsizeof parcial o número de clones no son la misma métrica ni prueban heap completo. H11 cubre backing/metadata/retención/desperdicio/fragmentación bajo modelo exacto, sin derivarlo de restar picos independientes.

Se preserva el parent de la suite H02 dentro del worker histórico: no se reclasifica como coordinador para retirar coste. Coordinador, threads, hijos y estado nativo/privado, recursos compartidos e interferencia requieren scope y composición de capacidad propios. No se reclama capacidad conjunta del host desde el rollup worker ni se usa suma de heaps/RSS ajenos como disponibilidad del worker.

Las ocho familias de vida cubren entrada/startup/imports; trabajo previo a RELEASE tR; originales/observer; postreturn/excepción/aliases retenidos; flush/IO; validación/doble salida; finally de éxito hasta tF; y rechazo/timeout/cleanup/retención de hijos. Son obligaciones, no timestamps o traces observados. Nacimiento/retención/liberación, count/size y derivaciones de pico/estado reales siguen ausentes.

No se asumen GC/destrucción/cache release/reuse inmediatos o no solapamiento. Deben incluirse originales/private state, hijos y todas las rutas aplicables de éxito, prefijos rechazados, excepción, timeout, cleanup y transitivos. Aliases exigen identidad física/lifetime/dominio demostrados; no se fusionan witnesses ni se descuenta memoria por nombres iguales. Se admite sólo pertenencia completa o sobreconteo conservador explícito sin omisiones o doble crédito de presupuesto.

Las ocho familias de memoria nueva conservan custodia/registries/snapshots, JCS/crypto/measurement, identidad/freshness, ledger/recibo/backend, ambos Reader/496 paths/copias, framing/pipes/bootstrap, doble output/codec/diagnóstico y drafts/clones/originales/native/GC. Sus mappings fuente/owner/proceso/fase y upper/prueba siguen nulos. La clausura completa W05 se conserva y requiere cubrir todo transitivo nuevo; no se incorporan helpers/inputs/canales implícitos.

## Rollup y capacidad: identidades de presupuesto, no pruebas

| Identidad candidata conservada | Bytes |
|---|---:|
| H01–H10 | 10938744832 |
| Reserva requested no asignada | 872415232 |
| Requested candidato (11 GiB) | 11811160064 |
| Overhead H11 candidato (1 GiB) | 1073741824 |
| Committed candidato (12 GiB) | 12884901888 |

La suma de budgets y reserva es correcta como contabilidad candidata. No suma cotas reales, no mide demanda y no aporta capacidad. El rollup requested exige upper bounds completos compatibles por owner; su suma, peak y comparación con reserva restante, fit y slack continúan nulos. Un owner faltante no se iguala a cero o a su budget. La reserva restante en la comprobación contractual no representa allocation física observada.

Committed exige correspondencia requested/backing/overhead del mismo worker/dominio/estado y cobertura completa. Upper bounds completos pueden sumarse conservadoramente bajo esas condiciones; faltan las derivaciones y H11 completo. Committed, fit y slack siguen nulos. No se deriva overhead restando peaks independientes ni se toma H11 como otra reserva requested disponible.

La capacidad W04 preservada sigue sin atestación, lower availability bounds, matching de scope/procesos/métricas/runtime/ABI/allocator, proveedor o validez reales. Reserva, límite ordinario, quota o host total no sustituyen capacidad independiente. Desconocido no significa cero ni prueba de inviabilidad. Falta de prueba finita completa o falta de ajuste mantiene la no admisión, sin ampliar cuotas o financiar carencias implícitamente con reservas/H11.

Se preservan las reglas completas I130 de heap/tiempo/nested, sin transferencias o recursos reservados. Los ceros de asignación son documentales; no miden uso real, slack o capacidad sobrante.

## Fronteras de fase y aceptación

W03 conserva el baseline exacto pendiente; W04 deberá aportar capacidad independiente; W05 debe sustentar la clausura/rutas/allocations del sucesor. W06 prepara derivaciones de memoria para W08 y W09; no completa W07 trabajo/CPU/unidades, W08 servicio/éxito en 900 segundos o el join E01–E05/BASIS/índices de W09.

No se agrega dependencia inversa W06 hacia aceptar recursos finales, freeze, C, mapping, E06, root, claim o recibo. Baseline efectivo, autores/cuerpos completos y supuestos deben estar autenticados antes de W09. W10 reconcilia los mismos hechos; cambios de contributors/bytes/imagen/runtime/caller/plataforma/ledger/epoch/key/política/scope invalidan cotas/revisiones afectadas y exigen recualificación. No se aplica refresh/rebind activo.

Todas las allocations, lookup/freshness/identidad/crypto/medición/copias/registry/recibo/native/IO, ambos Reader y doble salida necesarios por intento siguen dentro de la composición de fases/recursos. Offline/build/enrollment previo o un cap serializado no los hace gratuitos. No se exige ejecutar un claim futuro para documentar memoria de su mecanismo; CE12 conserva su frontera privada/deferida y autorización separada, sin recibo futuro como dependencia de CE11.

R03/R08 y autores/integrador/proveedores siguen sin identidades canónicas, competencia, nombramientos, cuerpos o decisiones genuinos. Los tres predicados de salida permanecen sin aceptar. El mismo asistente no puede sustituir revisión competente independiente o aceptación separada con comprobaciones documentales.

## Estado y verificación

Continúan cero paquetes aceptados, cero de los 30 gates cerrados y cero obligaciones E01–E05 cerradas. I122 conserva `IMPLEMENTED_NOT_ADMITTED`, CP03 sólo en scope heredado, CP07/atomicidad correlacionada sin verificar y componentes `NOT_RUN`. No se emite `SOURCE_CAPACITY_VERIFIED`, no se habilita PJC115-R2 y D5 sigue abierto. No se crea un record positivo de heap/BASIS/índice/I191, autoridad/root, claim, worker o recibo.

Comando exclusivamente documental: `python3 docs/validation/D5-I236-audit.py`.

Resultado: `PASS_STATIC_SOURCE_ONLY_W06_REVIEW_HEAP_LIFETIMES_MISSING_NOT_ADMITTED`. La auditoría compara independientemente I223/CE01/CE07/I130/owners/P05/P03/W04/W05, resuelve JSON pointers y verifica 977 pins contra blobs de la base I235 `47f5708a62ce4b9c43ce5cfa38aa6c660e26aac9`. Preserva 669 archivos publicados y exige cinco nuevos. Reproduce candidato/revisión de preparación I235 sin mains históricos de publicación ni proyección de presencia nueva, con método de consulta restaurado. Treinta y dos mutaciones documentales negativas en memoria se rechazan. El PASS no acredita heap, vidas/picos, ajuste/capacidad, independencia o admisión.

Runtime harness: **N/A**. Sólo documentos/JSON/Git/hashes/políticas y comprobaciones propias, sin ejecución/import/compile/test discovery de producto/componentes, tests/benchmarks/builds, profiling/sampling/getsizeof/introspección de heap, codec/crypto positivos, reloj/ledger/claim/procesos/probes/signing/keygen/enrollment/provisioning/servicios/contactos. No cambian cuotas, presupuestos/reservas, fuentes, schemas, Reader/canales/inputs/salidas, capture_inputs/bindings, autoridades/destinos o configuración activa.

Unidad documental única con commit/push solicitados, sin PR. Se declara el exceso de 400 líneas por pins, comparaciones de owners/clases/parejas/métricas/vidas/rollup/capacidad/fases, comprobaciones y preservación. Reversión exacta limitada a:

- `docs/design/D5-I236-I235-W06-REVIEW.md`
- `docs/validation/D5-I236-I235-source-reconstruction.json`
- `docs/validation/D5-I236-I235-documentary-review.json`
- `docs/validation/D5-I236-audit.py`
- `docs/validation/D5-I236-integrity.json`
