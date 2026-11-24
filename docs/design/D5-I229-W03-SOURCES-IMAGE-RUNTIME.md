# I229 — W03 preparado; fuentes, imagen y runtime reales ausentes

Fecha: 2026-11-24 · Plan I223/W03 · PGO181 candidato 02 · PFC126-CANDIDATE-03/I122.

W03 queda preparado como dossier documental de baseline efectivo y evidencia faltante. **No se acepta W03: W01/W02 siguen sin aceptar y SD01 permanece activo.** No existen las seis fuentes sucesoras ni se aporta imagen/runtime, build, cierre de dependencias o mapping auténticos. Se mantiene la no admisión de PJC115-R2, D5 abierto e IR03 `NOT_READY`.

El [candidato W03](../validation/D5-I223-W03-SOURCES-IMAGE-RUNTIME-CANDIDATE.json) conserva literalmente los tres entregables, tres predicados de salida, rechazos y autoridad futura de `/work_packages/2` de [I223](../validation/D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json). Vincula [I228/N01](../validation/D5-I228-I227-documentary-review.json) como frontera de entrada: preparación documental no acepta las dependencias ni inicia avance positivo. `W03-REAL-EVIDENCE-PACKAGE` identifica el entregable previsto; este wrapper no crea ese paquete auténtico aceptado, código sucesor o un image_manifest positivo I191 rellenado con nulos.

## Tres entregables preparados

| Entregable W03 | Especificación documental | Material real pendiente |
|---|---|---|
| Seis fuentes y mapping | Rutas exactas de I191, semántica README/entradas cargadas y campos separados para source digest/bytes, miembro/representación/digest, mapping y observación de carga | Cuerpos fuente, hashes/tamaños, source-root real, miembros e inventario/mapeo auténticos |
| Imagen y runtime completos | Ocho categorías de cierre efectivo, procedencia de build/toolchain y compatibilidad exacta P02/P03 | Imagen externa final, identidad completa del runtime, dependencias y equivalencia/provenance aceptadas |
| Implementación de política | Siete políticas referenciadas, selección externa auténtica, cumplimiento por las seis fuentes y prohibición de own future digests/helpers fuera de scope | Selección independiente real, valores compilados y prueba de conformidad de las fuentes/imágenes reales |

Las rutas son `README.md`, `atomic.py`, `capture.py`, `run_joint_lab.py`, `test_joint_capture.py` y `worker.py` bajo `testing/prospective_capture_joint_prp181/`. Se comprueba sólo su ausencia, sin crear ni importar código. README conserva la obligación `DOCUMENT`; no se da por suministrada una representación real. Pertenecer a una imagen no prueba que tests o runner estén cargados, ejecutados o cualificados.

Los hashes I122 no se trasladan a rutas sucesoras. Los bytes desconocidos no se suman como cero y el source-root permanece nulo. El techo candidato de las seis fuentes sigue siendo 262.144 bytes; no se amplía scope ni se introduce helper, entrada o lectura runtime implícitos. Todo helper de repositorio debe pertenecer al histórico480 o a las seis fuentes, con binding y coste completos, o requerir revisión explícita de scope/grafo/costes.

## Cierre efectivo e identidad

El ledger distingue ocho categorías: intérprete/stdlib/frozen/native exactos; loader/primera entrada; nativo/allocator/GC/kernel; correspondencia fuente/binario/build; identidad del objetivo real; miembros/dependencias de imagen; pins plataforma/runtime; y dominios de reloj/proceso/servicio. Cada una identifica la referencia normativa/histórica y lo que deberá probarse, con inventario, hashes de cuerpos, provenance y derivación de equivalencia ausentes.

Las referencias P02/I135–I136 y P03/I137–I138 corresponden al scope histórico I122. Se fijan sus dossiers/revisiones para compatibilidad y requisitos, sin transferirlos como evidencia del sucesor. P02 histórico no verificó identidad real completa y P03 no atestó plataforma. El Python, OS y entorno actuales del auditor no se muestrean ni se adoptan como identidad objetivo.

`image_bytes_sha256` compromete bytes externos finales; no redefine ni sustituye `runtime_sha256`, el cierre completo interpreter/loader/stdlib/builtin/frozen/native/crypto o P02. Build recipe/toolchain, ABI/configuración relevante, dependencias transitivas, allocator/GC y equivalencia fuente→imagen/runtime necesitan cuerpos y procedencia auténticos. Un listado o hash aislado no demuestra completitud o equivalencia.

Los seis fragmentos I191 son image_manifest, image_member_binding, image_dependency, source_bindings, evidence_reference y validity. La lista candidata de dependencias 1–128 debe ser auténtica y completa, sin truncarse para caber. El cap de image_manifest sigue en 98.304 bytes: no se aplica al wrapper ni limita por sí solo todos los cuerpos de prueba. No se ejecuta codec/schema/crypto sobre un cuerpo real ni se afirma fit de imagen, heap o CPU.

## Políticas y semántica implementada

Se conservan los siete pins documentales de perfil02, protocolo, output I187, contrato/gramática I189 y pack/contrato I191. Sus hashes conocidos fijan documentos. Valores compilados reales, selección externa independiente y aceptación permanecen ausentes; conocer una constante o igualar un digest no demuestra que la imagen o las fuentes implementen sus reglas.

K04/K05/K07/K15/K16 se conservan íntegros. Las fuentes revisadas deberán implementar el contrato y schema I191 exactos seleccionados externamente. No se obtiene esa selección del propio bundle ni se considera que una firma posterior autentique retrospectivamente el baseline. No hay código sucesor que inspeccionar y no se afirma haber revisado su conformidad.

Se mantiene la prohibición de incrustar los futuros digests propios de imagen, manifest o bundle. La identidad esperada de imagen debe seleccionarse por custodia externa aceptada. La obligación no acredita una inspección real de no autoembedding: imagen, selección y prueba siguen ausentes.

## Consumidores y orden de autenticación

| Requisitos CE04 | Consumidor en I223 | Frontera |
|---|---|---|
| IM01–IM06 | W03 | Baseline de fuentes, mapping, closure/build, runtime, políticas y primera entrada de imagen |
| IM07 | W04 / CE05 | Identidad caller, constructor/dominio/loader y origen de endpoints |
| IM08 | W04 / CE06 | Enforcement/garantías reales de plataforma contra shadowing, tracing, mutación e inyección |
| IM09 | W05–W09 / CE07 | Recualificación y composición completa E01–E05,179/321/12/30, heap/CPU/IO/Reader/900 segundos |
| IM10 | W10 / CE08 | Freeze final actor_registry → image_manifest → caller_identity → platform_custody, antes de C |

Las diez filas mantienen proveedor, cuerpo, hash/tamaño, nombramiento y aceptación ausentes; seis describen baseline y cuatro obligaciones diferidas. El baseline de primera entrada no sustituye el constructor/enforcement que deberá acreditar W04. No se añade una dependencia inversa de W03 hacia aceptar W04–W10 ni se aceptan sus hechos implícitamente.

Los hechos baseline de actores, imagen, caller y plataforma, así como autores y cuerpos completos de pruebas, deben estar autenticados antes de aceptar recursos en W09. W10 reconcilia los mismos hechos/scope; no puede ser su única autenticación pronosticada. El freeze final no se exige para preparar este dossier, ni se declara un manifest/source-root final aceptado. Cambios de autores, cuerpos, sources/imagen/runtime, epoch/key, política o scope invalidan dependientes y requieren nueva revisión/recualificación. No se aplica rebind o refresh activo.

## Autoridad, costes y estado

R01 y R06 conservan la revisión primaria prevista; R08 la aceptación separada. Los tres slots siguen sin persona, identidad canónica, competencia, nombramiento, clave/vigencia o aceptación. El mismo asistente/chat prepara I229 sin acreditar atestación competente R01, independencia R06 o aceptación R08.

Las acciones actuales son lectura documental/Git/hashes/presencia exacta de rutas, preparación, auditoría documental propia y commit/push. La ausencia de fuentes no concede autoridad para implementarlas, construir/medir imagen, importar/ejecutar o cualificar componentes. Tampoco se autorizan contactos, nombramientos/provisioning/enrollment, claves/firma/crypto positiva, probes/servicios, cambios activos de capture_inputs/root/autoridad/destino o cuotas/reservas. No se incluyen comandos operativos.

Las verificaciones de identidad/frescura/firma/medición necesarias por intento, lookup, copias/registry/recibo y nativo/IO siguen dentro de launch/worker/finish y composición completa E01–E05. Build/enrollment previos o llamar offline al material no hacen gratuito trabajo requerido durante launch. No hay nuevas rutas/helpers/fd/pipes/argv/entradas/salidas o confianza ambiental; si la plataforma real los necesita, corresponde rechazar la ruta sin cambios o revisar contratos/grafo/costes bajo autoridad separada.

Los tres predicados de salida permanecen pendientes. Continúan cero paquetes aceptados, cero de los 30 gates cerrados y cero obligaciones E01–E05 cerradas. I122 conserva `IMPLEMENTED_NOT_ADMITTED`, CP03 sólo en scope heredado, CP07/atomicidad correlacionada sin verificar y componentes `NOT_RUN`; no se emite `SOURCE_CAPACITY_VERIFIED`. CE12 sigue privado y deferido, sin C/Q/root/claim/worker/recibo reales creados por esta preparación.

## Verificación y publicación

Comando exclusivamente documental: `python3 docs/validation/D5-I229-audit.py`.

Resultado exigido: `PASS_STATIC_SOURCE_ONLY_W03_SOURCES_IMAGE_RUNTIME_MISSING_SD01_ACTIVE_NOT_ADMITTED`. La [revisión de preparación](../validation/D5-I229-preparation-review.json) reconstruye el candidato, resuelve pointers y verifica 942 pins contra blobs de la base I228 `dd241bbec9bedcc19349f04cd685187d150b08c8`. Reproduce reconstrucción/revisión documental I228 sin invocar mains históricos de publicación ni añadir proyección de presencia, con método de consulta restaurado. Veintidós mutaciones negativas en memoria deben rechazarse. El [sello](../validation/D5-I229-integrity.json) preserva 634 archivos publicados y fija los cuatro artefactos restantes.

Runtime harness: **N/A**. Sólo JSON/Git/hashes/políticas/presencia de rutas y comprobaciones documentales propias; no ejecución/import/compile de producto o componentes, tests/benchmarks, builds, codec/crypto positivos, medición de imagen/runtime/plataforma, probes/reloj/ledger/claim/procesos, firma/keygen, enrollment/provisioning/servicios o contactos. No cambian cuotas, reservas, fuentes, schemas, bindings, autoridades/destinos o configuración activa.

Unidad documental única, sin PR. Se declara el exceso de 400 líneas por pins, inventarios/closure, requisitos completos, fases, comprobaciones y preservación. Commit/push publica para revisión; reversión exacta limitada a:

- `docs/design/D5-I229-W03-SOURCES-IMAGE-RUNTIME.md`
- `docs/validation/D5-I223-W03-SOURCES-IMAGE-RUNTIME-CANDIDATE.json`
- `docs/validation/D5-I229-preparation-review.json`
- `docs/validation/D5-I229-audit.py`
- `docs/validation/D5-I229-integrity.json`
