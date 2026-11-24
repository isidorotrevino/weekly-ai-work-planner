# I235 — W06 preparado; heap y vidas completos siguen sin probar

Fecha: 2026-11-24 · Plan I223/W06 · PGO181 candidato 02 · PFC126-CANDIDATE-03/I122.

W06 queda preparado como dossier documental de once propietarios de heap, vidas/picos y rollup del sucesor. **W06 no está aceptado; W01–W05 tampoco y SD01 permanece activo.** Faltan allocations, cotas completas, correspondencia allocator/nativo/GC, composición de procesos y capacidad genuina. Se mantiene la no admisión de PJC115-R2, D5 abierto e IR03 `NOT_READY`.

El [candidato W06](../validation/D5-I223-W06-SUCCESSOR-HEAP-LIFETIMES-CANDIDATE.json) conserva literalmente los tres entregables, tres predicados de salida, rechazos y autoridad futura de `/work_packages/5` de [I223](../validation/D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json). Vincula [I234/N05](../validation/D5-I234-I233-documentary-review.json): las dependencias W03/W04/W05 siguen sin aceptar y una revisión metodológica no aporta prueba real. `W06-REAL-EVIDENCE-PACKAGE` identifica el entregable previsto; este wrapper no crea ese paquete auténtico aceptado, allocation trace, prueba de heap o record positivo BASIS/índice/I191.

## Tres entregables preparados

| Entregable W06 | Preparación documental | Evidencia real pendiente |
|---|---|---|
| Once derivaciones H01–H11 | Ledger por owner con unidad/métrica/presupuesto candidato, referencias históricas y campos de prueba separados | Inventario completo, cardinalidad/tamaño, vidas/picos, ABI/allocator/nativo/GC y cuerpos/autores/supuestos/decisiones |
| Cierre de procesos, allocations y solapamientos | 132 clases históricas, 55 parejas/110 direcciones de frontera, ocho familias nuevas y ocho familias de fases de vida | Mapping efectivo de pertenencia/aliases/domino, retención/concurrencia y cobertura completa o sobreconteo conservador justificado |
| Rollup requested/committed y capacidad W04 | Reglas condicionales y aritmética de presupuestos intactas; sumas/fit/slack reales nulos | Cotas completas compatibles, derivación H11/backing del mismo dominio/estado y capacidad disponible independiente con scope/validez concordantes |

## Once propietarios, sin cotas heredadas transferidas

| Owner | Obligación | Presupuesto candidato, bytes |
|---|---|---:|
| H01 | Runtime/startup/imports y extensiones nativas | 268435456 |
| H02 | Fixtures/private heap y originales retenidos del parent de la suite dentro del worker | 2147483648 |
| H03 | Raíces persistentes del observador y escalares fuera de clones | 536870912 |
| H04 | Clones, memo/id keys y opaque sets | 6442450944 |
| H05 | Frames/generadores/tracebacks y retención dinámica | 134217728 |
| H06 | Temporales de proyección/digest/metadata | 268435456 |
| H07 | JSON/Unicode, árboles y buffers/codecs | 268435456 |
| H08 | Reader chunks/datos inmutables de fase | 536870912 |
| H09 | Event chunks, pending bodies y flush | 201326592 |
| H10 | Tee/StringIO, texto de salida y raw parse | 134217728 |
| H11 | Allocation domain/backing/overhead/retención/fragmentación | 1073741824 |

H01–H10 conservan peak_requested_live_heap; H11, allocator_overhead. Son objetivos de diseño, sin aplicación como cuotas ni cotas completas verificadas. Cada fila fija su task I223, owner I130, dossier y última revisión históricos; scope, mapping, derivación, upper, fit, slack y aceptación del sucesor permanecen ausentes.

Los once expedientes P04 históricos y P05/I162 son declaraciones de insuficiencia de I122, sin transferencia al sucesor. Sus 132 clases y las 55 parejas no son un inventario completo de allocations del nuevo código. El modelo condicional H04 de unos 23 PB no es cota completa ni demanda mínima que pruebe inviabilidad; tampoco se sustituye por 33 generaciones o GC inmediato. Los submodelos payload H08/H09/H10 no se suman como heap completo ni se convierten en slack.

## Métricas, pertenencia y vidas

Requested live heap, committed allocator backing, overhead H11, RSS, stacks y otros mappings necesitan dominios/métricas explícitos. Bytes de JSON, typed caps, getsizeof parcial, cantidad de clones o RSS no prueban todo el heap. H11 debe justificar metadata/retención/desperdicio/fragmentación y correspondencia de backing con solicitudes del mismo dominio/estado; no deriva de restar picos independientes o presupuestos.

El parent de la suite H02 está dentro del worker histórico; no se reclasifica como coordinador para retirar su coste del heap. Coordinador, threads, hijos y sus heaps nativos/privados, interferencia, recursos compartidos y solapamientos requieren scope y composición de capacidad propios. El rollup worker no se presenta como prueba de capacidad conjunta del host ni se suman heaps/RSS ajenos como disponibilidad del worker.

Cada allocation futura deberá identificar clase/cuerpo/representación, owner, proceso/dominio, cardinalidad, tamaño solicitado/backing, raíces/aliases, nacimiento/retención/liberación y evidencia de vida/pico. Todos esos datos reales siguen ausentes. Las ocho familias de fases son requisitos: entrada/startup/imports; trabajo worker anterior a RELEASE tR; originales/observer; postreturn/excepción/aliases retenidos; flush/IO; validación/doble salida; finally de éxito hasta tF; y rechazo/timeout/cleanup/retención de hijos. No son timestamps, observaciones o un inventario exhaustivo del programa.

No se asumen liberación inmediata, GC/destrucción/caches oportunos, reuse del allocator o no solapamiento. Deben cubrirse todos los caminos aplicables de éxito, prefijos rechazados, excepciones, timeouts, cleanup y transitivos. Originales, private state e hijos no quedan cubiertos por medir clones. Aliases requieren prueba de identidad física, lifetime y dominio; no se fusionan witnesses distintos ni se obtiene descuento por nombres iguales.

Las 55 parejas conservan sus dos direcciones históricas, con resolución del sucesor falsa y mapping/prueba/revisión nulos. Se exige pertenencia completa o sobreconteo conservador explícito sin omisiones ni doble crédito de presupuesto. Reunir las 110 referencias no reconcilia sus fronteras.

## Memoria nueva del sucesor

Las ocho familias adicionales vinculan requisitos de I185/I187/I189/I191 y la clausura W05:

- Registros y snapshots de custodia/actores/anchors/imagen/caller/plataforma, registry y retención de memoria aceptada.
- JCS/parse/hash/crypto/measurement y copias/workspaces nativos por intento.
- Resolución de identidad/preparadores/aliases/keys, frescura/revocación/reloj y prefijos rechazados.
- Ledger global/locks/durabilidad/estados parciales/recibo y allocations de backend/native/IO.
- Ambos Reader físicos, snapshots/fresh reads/listings/maps/copias y 496 paths estables.
- Dos pipes/framing/EOF/attempts/errores, constructor/bootstrap/READY/RELEASE y estado retenido.
- Dos documentos context/launch completos, codecs/árboles/copias/validación/diagnósticos/fallback.
- Drafts/clones/memo/frames/originales y rutas atómicas rechazadas con threads/hijos/native/GC/allocator y solapamiento.

No se asignan allocations reales a owners mediante esas etiquetas. Los mappings de fuente/owner/proceso/fase, count/size/native/lifetime y prueba quedan nulos. Las familias amplían requisitos de cobertura; no afirman un censo completo del sucesor. Todo nuevo helper/transitivo efectivo debe estar ligado al scope aprobado y sus costes, sin lecturas/canales/inputs/salidas nuevos implícitos.

## Rollup condicional y capacidad independiente

| Aritmética de presupuestos conservados | Bytes |
|---|---:|
| H01–H10 | 10938744832 |
| Reserva requested no asignada, 832 MiB | 872415232 |
| Requested candidato, 11 GiB | 11811160064 |
| Overhead H11 candidato, 1 GiB | 1073741824 |
| Committed candidato, 12 GiB | 12884901888 |

Sólo se suman presupuestos conocidos en esta tabla. La suma de cotas solicitadas completas, su comparación con reserva restante y el peak requested real permanecen nulos; un owner desconocido no se toma como cero o como su budget. Añadir reserva restante en la comprobación contractual es contabilidad de presupuesto, no allocation o memoria observada.

Con cobertura y dominio/estado compatibles, upper bounds completos pueden sumarse conservadoramente para requested/backing/overhead. Falta la derivación de correspondencia y el upper completo H11; committed, fit y slack siguen nulos. No se resta un peak requested de otro peak committed independiente para afirmar overhead ni se toma H11 como otra reserva requested disponible.

W04 no aporta lower availability bounds reales de requested/committed ni matching de procesos/ABI/allocator/validez. Reserva solicitada, quota, límite ordinario o host total no sustituyen atestación independiente. Desconocido no significa capacidad cero ni demuestra inviabilidad. Si falta una prueba finita completa o no ajusta, continúa la no admisión; no se amplía cuota o se financia silenciosamente una carencia con H11/reserva.

I130 conserva sus reglas completas de contabilidad heap/tiempo/nested. Cero transferencias y recursos reservados falsos son estado documental, no medidas de uso o capacidad sobrante. No se aplica reasignación automática entre owners, reservas o fases.

## Fases, aceptación y autoridad

W03 aporta el objetivo exacto de fuentes/runtime/loader/imagen; W04 deberá atestar capacidad independiente; W05 deberá probar allocations/rutas/guards/Reader/output/atomicidad de la clausura. Esas dependencias siguen sin aceptar. W06 prepara derivaciones de memoria para el consumidor W08 y el join W09; no sustituye W07 CPU/unidades, W08 servicio/éxito en 900 segundos o aceptación conjunta E01–E05/BASIS/índices en W09.

No se introduce una dependencia inversa de W06 hacia aceptar recursos finales, freeze, C, mapping, E06, root, claim o recibo. Autores, cuerpos completos, supuestos y baseline efectivo deben autenticarse antes de W09. W10 reconcilia los mismos hechos; cambios de contributors/bytes/imagen/runtime/caller/plataforma/ledger/epoch/key/política/scope invalidan lo afectado y requieren nueva revisión. No se aplica refresh/rebind activo.

Las allocations, lookup/freshness/identidad/crypto/medición/copias/registry/recibo/nativo/IO requeridas por intento, ambos Reader y doble salida permanecen dentro de la composición completa de fases y recursos. Offline/build/enrollment previos o caps serializados no los hacen gratuitos. Prueba del mecanismo/retención de un claim futuro no requiere ejecutarlo ahora; CE12 conserva su frontera privada/deferida y autorización separada.

R03/R08 y los autores/integrador/proveedores siguen sin identidades canónicas, competencia, nombramientos, cuerpos o decisiones genuinos. El mismo asistente prepara este dossier sin revisión independiente R03 o aceptación separada R08. Los tres predicados de salida permanecen pendientes.

Sólo se realizan lectura documental/Git/hashes/presencia exacta, preparación, auditoría propia y commit/push. No se ejecutan producto/componentes, import/compile/test discovery, profiling/sampling/getsizeof/introspección/benchmarks/builds, codec/crypto positivos, reloj/ledger/claim/procesos/probes/signing/keygen/enrollment/provisioning/servicios/contactos. No se cambian fuentes, cuotas, presupuestos/reservas, schemas, Reader/canales/inputs/salidas, capture_inputs/bindings, autoridades/destinos o configuración activa.

Siguen cero paquetes aceptados, cero de los 30 gates cerrados y cero obligaciones E01–E05 cerradas. I122 conserva `IMPLEMENTED_NOT_ADMITTED`, CP03 sólo en scope heredado, CP07/atomicidad correlacionada sin verificar y componentes `NOT_RUN`. No se emite `SOURCE_CAPACITY_VERIFIED`, no se habilita PJC115-R2 y D5 continúa abierto.

## Verificación y publicación

Comando exclusivamente documental: `python3 docs/validation/D5-I235-audit.py`.

Resultado exigido: `PASS_STATIC_SOURCE_ONLY_W06_HEAP_LIFETIMES_MISSING_SD01_ACTIVE_NOT_ADMITTED`. La [revisión de preparación](../validation/D5-I235-preparation-review.json) reconstruye el candidato, resuelve pointers y verifica 972 pins contra blobs de la base I234 `78e5eac02d31c97fd611f66d050938825073bae9`. Comprueba once owners/132 clases/55 parejas y 110 direcciones, aritmética sólo de budgets, sumas desconocidas y fronteras. Reproduce reconstrucción/revisión documental I234 sin mains históricos de publicación ni nueva proyección de presencia, con método de consulta restaurado. Treinta mutaciones negativas documentales en memoria deben rechazarse. El [sello](../validation/D5-I235-integrity.json) preserva 664 archivos publicados y fija los otros cuatro artefactos.

Runtime harness: **N/A**. Sólo documentos/JSON/Git/hashes/requisitos y comprobaciones propias; sin producto/componentes/heap/allocator/plataforma o infraestructuras ejecutados/medidos. El PASS no prueba cotas de heap, fit/capacidad, independencia o admisión.

Unidad documental única con commit/push solicitados, sin PR. Se declara el exceso de 400 líneas por obligaciones de owners/clases/fronteras, familias nuevas, reglas de rollup, pins, comprobaciones y preservación. Reversión exacta limitada a:

- `docs/design/D5-I235-W06-SUCCESSOR-HEAP-LIFETIMES.md`
- `docs/validation/D5-I223-W06-SUCCESSOR-HEAP-LIFETIMES-CANDIDATE.json`
- `docs/validation/D5-I235-preparation-review.json`
- `docs/validation/D5-I235-audit.py`
- `docs/validation/D5-I235-integrity.json`
