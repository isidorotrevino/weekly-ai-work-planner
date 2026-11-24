# I227 — W02 preparado; personas y anchors auténticos pendientes

Fecha: 2026-11-24 · Plan I223/W02 · PGO181 candidato 02 · PFC126-CANDIDATE-03/I122.

W02 queda preparado como dossier documental de requisitos de personas y anchors, con roles sin asignar, pruebas ausentes y separación de fases explícita. **W02 no está aceptado; W01 tampoco y SD01 continúa activo.** La preparación autorizada no descarga la dependencia W01 ni constituye avance positivo de paquetes. Se mantiene la no admisión de PJC115-R2, D5 abierto e IR03 `NOT_READY`.

El [candidato W02](../validation/D5-I223-W02-PEOPLE-AND-ANCHORS-CANDIDATE.json) vincula literalmente los tres entregables, tres predicados de salida, rechazos y autoridad futura de `/work_packages/1` del [plan I223](../validation/D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json). Referencia [I226/N01](../validation/D5-I226-I225-documentary-review.json): W02 o un bundle futuro no pueden ser la única autoridad pronosticada de W01. El identificador `W02-REAL-EVIDENCE-PACKAGE` identifica el entregable previsto; este dossier no crea su paquete auténtico aceptado ni un registro positivo I191 rellenado con nulos.

## Tres entregables preparados

| Entregable W02 | Contenido documental | Evidencia real pendiente |
|---|---|---|
| Personas y claves por propósito | Ocho roles R01–R08 con sus scopes y separaciones; cinco categorías adicionales: autores de fuentes, preparadores, requester humano, autores/proveedores de pruebas y firmantes/custodios | Humanos canónicos, organizaciones/alias completos, competencia, nombramientos, scope/vigencia, procedencia aceptada y bindings de propósito/clave |
| Política y anchors previos | Requisitos CE02 candidato 02, política de origen externo, expected digest/epochs, provisión/aceptación previa, cuerpos, vigencia/currentness/revocación | Autoridad externa auténtica, registry real y digest esperado seleccionado independientemente, claves públicas/procedencia, reloj confiable y decisiones previas genuinas |
| Matriz de separación | 14 reglas: ocho exclusiones S01, dos source-author/root-key y cuatro de custodia R08 frente a R01/R02 | Resolución canónica y comparaciones reales de humanos/keys; todas permanecen sin verificar |

Los roles y categorías no son un conteo de personas. Un humano sólo podrá ocupar scopes compatibles bajo competencia y autoridad genuinas. El principal software/service/process del caller permanece separado de la identidad humana responsable; nombres, cuentas Git, strings de rol, claves diferentes o flags aceptados no demuestran personas distintas ni independencia.

La preparación de este asistente se registra sólo como actividad documental sobre los cinco archivos de I227. Humano canónico responsable, organización, prueba de contribución y preparation_record positivo permanecen ausentes. No se infiere identidad del usuario Git ni se calcula un hash de contribución auténtica para suplirla. Todos los preparadores del scope aceptado deberán incluirse finalmente, sin limitar la lista a autores de código o a este chat.

## Evidencia por consumidor y fase

El ledger vincula 19 requisitos exactos de los dossiers revisados CE02/CE03. Nueve son previos de anchors, ocho son intake provisional de personas y dos describen fases diferidas. Cada fila conserva evidencia/proveedor/body/hash/tamaño/nombramiento/aceptación ausentes, sin contacto autorizado.

| Requisitos | Consumidor | Frontera conservada |
|---|---|---|
| AP01–AP07, AP08-ANCHOR-POLICY, AP09 | W02 / CE02 | Provisión y aceptación previa genuinas, origen/autoridad independientes, expectativa externa y bindings completos; no requiere firmas futuras del bundle |
| IR01–IR08 | W02 / CE03 provisional | Resolución humana/alias/organización, competencia/appointments, separación humano/software y seguimiento de contribuciones conocidas, sin afirmar completitud final |
| IR09 | W10 / CE08 | Freeze completo tras conocer autores/cuerpos reales; actor_registry, image_manifest, caller_identity y platform_custody en ese orden, antes de C |
| AP08-BUNDLE-APPROVAL | W12 / CE10 | Tres aprobaciones auténticas R01/R02/R08 sobre el mismo core, después de anchors, antecedentes y C aceptados; no autentican retrospectivamente sus propios anchors |

Se conserva la reparación F199-01 de CE02 candidato 02: política previa de dominios/core/profile/pack/contrato no equivale a firmas disponibles. La obligación posterior de aprobaciones reales sigue siendo exigible en CE10/W12, sin exigirla anticipadamente a W02 ni autorizar obtenerla ahora. Los dossiers documentales CE08/CE10 existentes no acreditan freeze, registry, core o aprobaciones reales.

La recepción CE03 es provisional. Los autores reales W05–W08 y los cuerpos completos deben existir y estar autenticados antes de aceptar sus pruebas en W09. El freeze posterior W10 reconcilia los mismos hechos aceptados; no puede ser su única autenticación pronosticada. Cambios de contribuyentes, alias, cuerpos, sources/runtime/imagen, dominio, epoch/key, política o scope invalidan hashes/revisiones afectados y exigen recualificación/reconciliación. No se aplica ningún refresh o rebind activo aquí.

Cada futuro preparation_record deberá vincular actor autenticado, perfil02/schema exactos y contribución real. Sus datos deberán coincidir con la proyección C conforme a K03, pero el propio registro no puede pinchar C, acceptance, bundle o root futuro. No se preaprueban autores todavía desconocidos.

## Separación y confianza

Las ocho exclusiones S01 se aplican sobre todos los humanos canónicos/preparadores pertinentes. Se conservan R08/source-author y la separación de claves issuer/acceptor del root, junto con R08 humano/key distinto de ambos R01 y R02 en custodia. R01/R02 pueden coincidir sólo para el mismo humano genuinamente competente en ambos scopes, con aprobaciones de dominio de rol separadas en su fase. No se añade una prohibición general de solapamiento R01/R02.

Los anchors deben proceder de configuración externa preexistente y aceptación independiente de repo/C/bundle/root. Un registry autofirmado, key_id, clave suministrada, hash documental o firma futura no crea su propia confianza. Se requieren cuerpos completos de prueba, bindings ordenados/únicos por propósito y clave, epoch y vigencia auténticos; los cuerpos subyacentes no pueden ocultarse o truncarse para ajustar un índice.

Se preservan los dominios R01/R02/R08 y terminador 0x00 como política, vida máxima 3.600 segundos y error confiable máximo 5 segundos. No se usan la fecha del chat o mtime como evidencia de currentness. No se ejecutan comprobaciones de reloj, revocación, registry codec o crypto. Sin garantía de frescura se rechaza; no se añade TOFU, cache obsoleta, consulta online/archivo oculta ni promesa de descubrir instantáneamente toda revocación.

## Caps, costes y autoridad

Se fijan siete fragmentos de schema I191: anchor_registry, anchor_key, actor_registry, actor, preparation_record, evidence_reference y validity. Son política documental exacta, sin instancias positivas. Los caps candidatos de registry son 65.536 bytes para anchors y 98.304 para actores; no son cuotas activas ni límites de tamaño de este wrapper. No prueban fit de un cuerpo real desconocido, de sus pruebas referenciadas, heap, CPU/IO, servicio o 900 segundos.

Lookup, frescura, resolución de identidad, verificaciones necesarias, copias/estado del registry, recibo y trabajo nativo/IO por intento siguen dentro de la composición completa de recursos y fases. Llamar offline a la evidencia o tener enrollment humano previo no permite omitir trabajo exigido durante el lanzamiento. No se asignan o transfieren reservas.

Las acciones actuales se limitan a lectura documental/Git/hashes, preparación, auditoría documental propia y commit/push. La matriz conserva las ocho clases operativas sin autorizar del plan: ejecución; implementación/build; probes de plataforma/reloj/ledger; firma/keygen/crypto positiva; contactos; provisioning/enrollment/servicios; cambios activos de capture_inputs/root/autoridad/destino; cuotas/reservas. No hay comando de ejecución ni permiso implícito para nominar personas, crear claves o buscar proveedores.

Los tres predicados de salida están reproducidos y pendientes de evidencia, revisión R06 y aceptación R08 genuinas. El mismo asistente preparador no satisface esas decisiones independientes. Continúan cero paquetes aceptados, cero de los 30 gates cerrados y cero obligaciones E01–E05 cerradas. I122 sigue `IMPLEMENTED_NOT_ADMITTED`, CP03 sólo en scope heredado, CP07/atomicidad correlacionada sin verificar y componentes `NOT_RUN`. No se emite `SOURCE_CAPACITY_VERIFIED`. CE12 sigue privado/deferido, sin claim, worker, root o recibo reales creados por esta preparación.

## Verificación y publicación

Comando exclusivamente documental: `python3 docs/validation/D5-I227-audit.py`.

Resultado exigido: `PASS_STATIC_SOURCE_ONLY_W02_PEOPLE_ANCHORS_MISSING_W01_BLOCKED_NOT_ADMITTED`. La [revisión de preparación](../validation/D5-I227-preparation-review.json) verifica el candidato reproducido, 932 pins contra blobs de la base I226 `a715fb2310ce12f9bc3f29719e59f90b4917e20e`, pointers, roles, separaciones, requisitos y fases. Reproduce las funciones documentales I226 sin llamar mains históricos de publicación ni añadir proyección de presencia; el método de consulta queda restaurado. Dieciocho mutaciones negativas en memoria deben rechazarse. El [sello](../validation/D5-I227-integrity.json) preserva 624 archivos publicados y fija los cuatro artefactos restantes de esta unidad.

Runtime harness: **N/A**. Sólo se usan JSON/Git/hashes y comprobaciones documentales propias; no se ejecutan/importan/compilan producto o componentes, tests/benchmarks, builds, codecs/crypto positivos, probes/muestras de reloj/ledger/claim/procesos, firma/keygen, enrollment/provisioning/servicios ni contactos. No se cambian cuotas, reservas, schemas o configuración activa.

Unidad documental única, sin PR. Se declara el exceso de 400 líneas por los pins, matrices, requisitos completos, comprobaciones y preservación, sin comprimir evidencia. Commit/push publica sólo para revisión; la reversión exacta retira:

- `docs/design/D5-I227-W02-PEOPLE-AND-ANCHORS.md`
- `docs/validation/D5-I223-W02-PEOPLE-AND-ANCHORS-CANDIDATE.json`
- `docs/validation/D5-I227-preparation-review.json`
- `docs/validation/D5-I227-audit.py`
- `docs/validation/D5-I227-integrity.json`
