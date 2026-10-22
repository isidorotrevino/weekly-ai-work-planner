# D5 I19 — contrato propuesto de resolución local aislada

Fecha: 2026-10-22. **Diseño para revisión; sin implementación ni SQL nuevo.**
Base publicada: `dd9b4f6`, [resolución I14](D5-I14-LOCAL-EDIT-LAB.md),
[adopción I16](D5-I16-ADOPTION-LAB.md) y
[reaparición local I18](D5-I18-LOCAL-REAPPEARANCE-LAB.md).
[Matriz de aceptación y siguiente decisión](D5-I19-ISOLATED-LOCAL-EDIT-REVIEW.md).
D5 abierto; D1–D4 cerrados y D6 pendiente.

English: proposed reviewed resolution of an isolated local title/description edit
against a selected, present source row identical to the applied semantic basis.
No fabricated comparison or I5 decision. Preserve the source basis, advance the
mapping version, and keep applied absence/reappearance gates intact. Design only.

## Decisiones expresas

| ID | Decisión del usuario | Consecuencia |
|---|---|---|
| D5-A45 | Priorizar resolución local aislada, con contrato/matriz antes de SQL | Sin comparación I5 ficticia ni implementación en este corte |
| D5-A46 | Fila presente seleccionada por referencia/version y base semántica íntegra igual a cabeza | Ausencia y cualquier diferencia semántica de origen quedan fuera; no basta Item/Objective |
| D5-A47 | Avanzar cabeza una vez, conservando base/proyección del origen | Elección, snapshot y recibo propios; paquetes preparados sobre versión anterior quedan obsoletos |
| D5-A48 | Bloquear si último efecto aplicado es ausencia, aunque se seleccione snapshot presente anterior | Resolver primero reaparición por I12/I18; acreditar efecto por versión, nunca por fecha |

Se conserva A31/A33: elegir origen completo o local completo, con revisión propia,
sin campos sueltos, texto manual o excepción permanente. Las secciones siguientes
concretan la propuesta completa para revisión; A45–A48 no autorizan implementarla.
Se conservan V1–V38, funciones, parsers/perfiles, adaptadores, runners, manifiestos
y evidencias anteriores. No se reserva número de migración ni se publica sin
aprobar el commit concreto.

## Problema y valores visibles

I14 exige CHANGED presente→presente con ACCEPT I5. I18 exige ADDED con prueba de
ausencia aplicada y declaración de identidad. Ninguno resuelve por sí solo una
edición local si la fuente seleccionada no cambió. Crear una comparación de una
observación consigo misma, un CHANGED artificial o una decisión I5 ficticia no
es una entrada válida. La variante propuesta tiene artefactos y revisión propios.

| Valor | Fuente | Significado |
|---|---|---|
| B | Cabeza D5 vigente | Última proyección del origen registrada |
| L | Snapshot completo actual de tarea | Pareja local title/description sometida a revisión |
| S | Fila presente del snapshot seleccionado | Proyección de origen reconstruida; aquí debe ser igual a B |

Se exige L distinto de B al preparar y aplicar; si coinciden no hay resolución
local aislada que autorizar. A46 exige igualdad de **toda** la base semántica de la
fila con `head.source_basis`: fields completos, source_struck y annotation_text,
según `d5.source-basis.v1`. Su digest y la proyección S=B deben ser coherentes.
Cambiar Status, Verified, bloqueos o anotación también queda fuera, aunque no cambien
Item/Objective. I14 u otro contrato aplicable conserva su revisión independiente.

La divergencia puede proceder de una edición directa actual, adopción I16 o
KEEP_LOCAL I14/I18/esta variante. No se infiere autor o fecha de edición. El origen
puede tener bytes/posición distintos si la fila semántica íntegra coincide: se fija
su observación, fila y localizador reales; nunca se sustituyen identidades de
observación por hashes iguales.

## Identidad y elegibilidad

Intención materializada propia, mismo `(project_id, document_id, source_key)`,
perfil/política fijos y UUID/task_key/proyecto actuales exactos. Se admite propiedad
establecida por I8/I10/I16 y efectos posteriores I12/I14/I18; no se crea, adopta,
transfiere, reabre o reactiva tarea. Una intención v0 o sin destino materializado
bloquea. task_sources anteriores se conservan; esta variante no exige vaciarlos.

La tarea debe seguir BACKLOG, sin operaciones ni planificación, incluidas
históricas/canceladas. No se borran hechos o cambian estados para admitirla.
Título local y de origen válidos no vacíos ni solo blancos Unicode; descripción
local SQL NULL permitida, Objective string, vacío/guion literales. Fuente inválida
bloquea incluso KEEP_LOCAL. Se conserva texto literal sin normalizar Unicode,
renderizar Markdown, desescapar pipes o resolver URLs. Claims, tachado, bloqueos y
anotaciones son evidencia sin efectos de workflow o dependencias.

## Fuente seleccionada y prueba de cabeza presente

Observación exacta del documento/proyecto/perfil seleccionada como referencia con
versión esperada. El operador la selecciona antes; preparar/revisar/aplicar no la
eligen ni avanzan. La selección acredita esa referencia local, no que sea el último
contenido externo o la captura de fecha mayor. Ninguna lectura gana por fecha.

El adaptador reconstruye bytes y preview, verifica hashes fuente/preview/fila
canónica y exige una única fila presente. Un diagnóstico bloqueante en cualquier
fila bloquea el snapshot completo. Se permiten avisos del perfil compatible.
Ausencia, ID duplicado o cualquier diferencia semántica respecto a cabeza bloquean.
No se exige ni se produce comparación, review_item, ADDED/UNCHANGED o ACCEPT I5.

A48 añade un control distinto de la igualdad semántica. I8
KEEP_EXISTING_NO_DELETE avanza versión conservando B y source_basis. Por eso
ninguna de ellas, ni una referencia presente antigua, demuestra presencia aplicada.
Hace falta una prueba histórica del efecto confirmado que **produjo exactamente
la versión vigente** de la cabeza de esa intención/destino.

La propuesta de prueba `d5.isolated-local-head-proof.v1` fija variante, comando de
aplicación OK, paquete, propuesta/hash, pin de revisión histórico y recibo/efecto,
identidad de intención/tarea, versión producida y evidencia de fila presente/base
resultante. Se valida la cadena inmutable commands → paquete/pin → propuesta →
aplicación/efecto/recibo, no solo audit_events o un campo proporcionado por caller.
Hash y ámbito deben coincidir con los artefactos reales. No se infiere el ganador
por prepared_at/applied_at ni se inventan recibos o columnas en artefactos antiguos.

Efectos presentes de I8/I10/I12/I14/I16/I18 son candidatos; la prueba debe mostrar
su resultado real y base/proyección compatibles con cabeza. I16 inicializa v1:
no se fabrica una fila de cabeza previa v0. Una futura resolución aislada confirmada
también puede acreditar su versión producida y snapshot presente verificado, con
base conservada; así KEEP_LOCAL permite otra resolución propia sin perder trazabilidad.
Un tipo de efecto desconocido, cadena incoherente, prueba ausente/ajena o versión
sin acreditación bloquean, sin asumir presencia por defecto.

Si el efecto exacto vigente es una ausencia I8 aplicada, se bloquea incluso con
referencia presente seleccionada y S=B. No se avanza su cabeza ni se reversiona,
consume o fabrica prueba de ausencia. I12/I18 deben resolver la reaparición con
sus requisitos propios. Una ausencia antigua ya superada por reaparición válida
no bloquea para siempre; se acredita el efecto de la versión actual. Un REJECT
posterior de la revisión histórica no deshace un efecto confirmado, como en I12;
la resolución aislada sigue necesitando su propia revisión vigente.

## Preparación y revisión propias

El manifiesto propuesto `d5.isolated-local-edit-task-manifest.v1`, modo
ISOLATED_LOCAL_EDIT, incluye:

- Intención/destino y ámbito completos, perfil/política, versión de cabeza y prueba
  histórica de efecto presente para esa versión.
- Base semántica/digest y B anteriores, observación/revisión de origen, hashes de
  bytes/preview/fila, fila presente íntegra con localizador/posición y referencia/version.
- S reconstruida igual a B; no hay nueva base semántica de origen ni before/after
  de comparación. El snapshot actual se distingue de evidencia histórica de cabeza.
- Snapshot íntegro de tarea en UTC, row_version y digest `d5.task-target.v1`, L y
  hashes de B/L/S/resultado por dominios explícitos.
- USE_SOURCE o KEEP_LOCAL, razón, resultado completo derivado, acción/columnas a
  escribir, avance esperado de cabeza conservando base/proyección y
  `activation_allowed=false`. Metadatos de preparación sin autoridad temporal.

El preparador aporta razón explícita de 1–1.024 caracteres, sin controles ni solo
blancos Unicode. No aporta texto de resultado, máscara de campos o force. El
revisor acepta/rechaza todo el manifiesto: fuente/base y prueba, tarea actual,
elección, pérdida eventual de texto local, razón y efecto. No se reutiliza ACCEPT
I5/I8/I10/I12/I14/I16/I18. Esta revisión propia incluye la autorización del snapshot
de origen sin fabricar una revisión I5. Etiquetas/razones son afirmaciones sintéticas.

Cambiar fuente, prueba, tarea, elección o razón requiere otra preparación/revisión.
Revocar/reaceptar incrementa versión e invalida pins anteriores. Preparar registra
solo propuesta/recibo y cabeza de revisión v0, sin tarea, procedencia o avance de
correspondencia. No se toman locks de escritura D2 al preparar/revisar.

Los nombres siguientes son interfaces de diseño, todavía no disponibles:

| Paso | Contrato propuesto |
|---|---|
| PREPARE_ISOLATED_LOCAL_EDIT_TASK | Intención, observación/hashes fuente/preview/fila, versiones esperadas de referencia/cabeza, prueba de aplicación/propuesta que produjo cabeza, elección/razón; reconstruye fila y prepara sin escribir tarea |
| REVIEW_ISOLATED_LOCAL_EDIT_TASK | proposal_id/hash, versión propia esperada, ACCEPT/REJECT, etiqueta/razón; revisión completa |
| PACKAGE_ISOLATED_LOCAL_EDIT_TASKS | Lista explícita ordenada de proposal_id/hash y review_command_id/version; una por intención, misma observación/perfil |
| APPLY_ISOLATED_LOCAL_EDIT_TASKS | command_id global D5, ámbito y hash del paquete inmutable; sin texto libre ni force |

Paquetes de 1–2.000 propuestas ordenadas, de un documento/proyecto, sin duplicados
ni mezcla con variantes anteriores. No se eligen todas las aceptadas ni las de
fecha mayor. Se conservan límites de bytes y roles writer/reviewer/applier/reader.
El adaptador confiable verifica snapshots, prueba y manifiesto antes de preparar,
revisar, empaquetar y aplicar; SQL privilegiado por sí solo no acredita el parser.

## Efectos y continuidad

| Elección | Condición de entrada | Acción propuesta | Tarea |
|---|---|---|---|
| USE_SOURCE | L distinto de B y S=B | PATCH_ISOLATED_LOCAL_USE_SOURCE | Title/description completos a B; row_version +1 una vez |
| KEEP_LOCAL | L distinto de B y S=B | KEEP_ISOLATED_LOCAL | Conservar exactamente toda la fila sin UPDATE ni incremento de row_version |

No hay rama USE_SOURCE sin cambios en este corte: S=B y L distinto de B implican
PATCH. Una convergencia posterior a preparar invalida la propuesta; no se la
convierte automáticamente en confirmación sin efecto.

En ambos casos cabeza +1, conservando **exactamente** source_basis, su digest y
projection=B; no se guarda L como origen ni se crea una revisión de origen a
partir de la edición local. El hecho/recibo inmutable fija versión antes/después, B/L/S, resultado real,
prueba y elección/razón. No hay override permanente, cursor/puntero/referencia
avanzado o revisión I5 inventada. Fecha de aplicación en D5, sin tasks.updated_at,
cambios de created_at u otros campos ajenos a title/description/row_version.

Se añade o reutiliza task_sources exacto del snapshot presente seleccionado, con
SourceRevision/FK/localizador coherentes, sin editar o borrar vínculos previos.
Acredita procedencia y selección revisada, no igualdad de la tarea con el origen.
Una misma revisión/vínculo no se duplica. No se crean tareas, intenciones, destinos,
requisitos, épicas, dependencias u operaciones. Auditoría D5_TASK_IMPORT propia,
no STATE_CHANGED ni outbox; distinguir writes_task de escritura de evidencia D2.

USE_SOURCE restablece L=B y permite continuidad I8 con cambio real/revisión propios.
KEEP_LOCAL mantiene L distinto de B: ante siguiente cambio presente exige I14;
si la fuente sigue igual puede prepararse otra resolución aislada con nueva prueba,
versión y revisión, nunca una autorización permanente. Una ausencia futura sigue
por I8 y su reaparición por I12/I18 con nueva prueba aplicada/versionada.

A47 invalida paquetes anteriores aunque B sea idéntica y KEEP_LOCAL no escriba
tarea. No se rebasa un paquete I8/I14/I18 automáticamente: otra preparación con
cabeza actual y revisión propia. Lecturas, replay y ALREADY_APPLIED no avanzan
versiones ni restauran texto, y nunca revalidan pins antiguos por igualdad de hash.

## Atomicidad, permisos y siguiente decisión

APPLY futuro exige READ COMMITTED y helper fijo vigente: 742001 → 742002 →
relaciones D3 → mutex D5 742005 → intenciones/cabezas y destinos ordenados.
Se valida todo el paquete antes del primer efecto: identidad/propiedad, prueba de
cabeza presente/version, referencia y revisión vigentes, base/proyección intactas,
fila reconstruida, B/L/S/resultado, snapshot/digest íntegro, BACKLOG y ausencia de
trabajo/plan. Ediciones posteriores incluso sin row_version invalidan el CAS;
ABA observable invalida pins, sin prometer detectar restauración externa de todos
los valores sin huella de versión/evidencia.

Conflicto de negocio sin efectos parciales; aborto/error estructural revierte tarea,
vínculo, cabeza, hecho/auditoría y recibo de éxito. command_id global: replay exacto
histórico, contenido distinto en conflicto, otro comando del mismo paquete solo
ALREADY_APPLIED. Carreras entre variantes con un avance ganador y conflicto del
otro; tras una espera se verifica el estado vigente, sin snapshot obsoleto.

Implementación futura aditiva, propietario NOLOGIN y roles separados sin DML directo
para callers ni autoridad general D3/D4. Funciones/rechazos antiguos intactos, sin
relajar I14 CHANGED, I12/I18 ausencia/identidad ni I16 adopción. PATCH cambia digest
de tarea D3 y vuelve obsoleta una captura; planes publicados permanecen inmutables.
KEEP_LOCAL no escribe tarea; no se promete invariancia global de todos los efectos
de evidencia o cambios concurrentes. BACKLOG elegible no significa activación.

El siguiente paso exige aprobar este contrato completo y autorizar implementación
y matriz en otro laboratorio V30 desechable con fixtures BACKLOG sintéticas,
separado de dev/D4. Este corte no ejecuta la matriz ni inicia servicios.
D5 sigue abierto: IDs reutilizados/transferencias, adopción con trabajo/procedencia
previos, perfil/política, múltiples orígenes y Gentle-AI/routing completo conservan
pendientes. Sin proveedores/credenciales reales, activación, promoción, despliegue
ni ampliación D6; D1–D4 y sus evidencias se conservan.
