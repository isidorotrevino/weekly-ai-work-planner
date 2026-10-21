# D5 I15 — contrato propuesto de adopción explícita

Fecha: 2026-10-21. **Diseño para revisión; sin implementación ni SQL nuevo.**
Base publicada: `b8ab72d`, [mapeo I8](D5-I8-SYNTHETIC-TASK-LAB.md),
[bootstrap I10](D5-I10-BOOTSTRAP-LAB.md),
[reaparición I12](D5-I12-REAPPEARANCE-LAB.md) y
[resolución local I14](D5-I14-LOCAL-EDIT-LAB.md).
[Matriz de aceptación y siguiente decisión](D5-I15-ADOPTION-REVIEW.md).
D5 abierto; D1–D4 cerrados y D6 pendiente.

English: proposed explicit adoption of an existing BACKLOG task from one selected
source snapshot. Review exact document/row and task identities; preserve the whole
task. Correspondence, provenance and receipt become durable together only at APPLY.
No similarity matching, SQL implementation, operational activation or deployment.

## Decisiones expresas

| ID | Decisión del usuario | Consecuencia |
|---|---|---|
| D5-A35 | Priorizar contrato/matriz de adopción explícita por documento+ID y UUID/clave de tarea | Diseño antes de SQL; no buscar por nombre o similitud |
| D5-A36 | BACKLOG del mismo proyecto, sin operaciones ni planificación históricas, sin correspondencia D5 ni task_sources previos | No adoptar tareas con trabajo o procedencia directa anterior, ni reutilizar reservas D5 |
| D5-A37 | Conservar íntegra la tarea; añadir correspondencia/procedencia | Sin PATCH inicial; divergencia con origen exige resolución explícita en cambios posteriores |
| D5-A38 | Fila presente de snapshot seleccionado por referencia/version y revisión propia del manifiesto completo | Sin comparación ficticia ni ACCEPT I5 fabricado |
| D5-A39 | Reservar/materializar solo al aplicar paquete aprobado, junto con procedencia y recibo | Preparar no reserva origen/tarea; una carrera posterior produce conflicto |

Las secciones siguientes concretan la propuesta completa para revisión. Estas
instrucciones no autorizan todavía implementar SQL, roles, tareas o un laboratorio.
Se conservan V1–V36, funciones, parsers/perfiles, adaptadores, runners y evidencias
históricas. No se reserva un número de migración. La publicación del diseño se
planteará sobre su commit concreto, separado de la aprobación de implementación.

## Identidad y elegibilidad

REGISTER_TASK_INTENT actual rechaza UUID/clave de tarea ya ocupados, aun si se
proporcionan explícitamente. Bootstrap exige destino ausente. La adopción propuesta
usa entradas propias y no relaja ninguno de esos rechazos de I8/I10.

La fuente es `(project_id, document_id, source_key)` exacta, con documento/proyecto
ya registrados. Perfil `task-register.v1` o `task-register-compat.v1` y política
`d5.task-projection.v1` fijos. El destino es una tarea existente con UUID, proyecto
y task_key proporcionados explícitamente y coincidentes con la fila actual.
Título, similitud, posición, fecha o ruta no sustituyen esas identidades. Se
conservan ID largo y strings completos; la igualdad no se decide solo por su hash.

No puede existir intención D5 para ese documento+ID —independientemente del
perfil—, UUID o clave interna del proyecto. También bloquea una intención v0 no
materializada, una reserva ordinaria I8 o cualquier historial materializado previo.
No se descarta, borra, transfiere o reinicia una correspondencia para admitir esta
variante. Si el índice por hash colisiona con otra identidad, se rechaza; nunca se
interpreta como coincidencia ni se trunca el ID para evitar el conflicto.

La tarea debe seguir en BACKLOG, sin ninguna operación ni entrada de planificación,
incluso histórica/cancelada, y con cero filas en `d2.task_sources` para su UUID.
Un vínculo anterior idéntico también bloquea una primera adopción: no demuestra
que esta adopción estuviera aprobada. No se borran vínculos o trabajo para admitirla.

Este control de procedencia es sobre task_sources directos, no una afirmación de
que no exista historia de proyecto, épica o requisitos. Se conservan epic_id,
dependencias, urgencia, fechas y demás datos locales; no se adoptan ni modifican
esas entidades, ni se crean requisitos/épicas o dependencias a partir del origen.
La ausencia de operaciones y planes se comprueba separadamente de task_eligible.

## Snapshot y referencia seleccionados

Se usa una observación exacta del documento/proyecto/perfil, seleccionada como
referencia vigente con versión esperada explícita. El operador la selecciona
antes si hace falta; preparar/revisar/aplicar no la eligen ni avanzan. Cambiar a
otra observación y volver a la primera invalida la versión antigua (ABA).

El adaptador reconstruye bytes de fuente y preview, verifica hashes y exige una
única fila presente para el ID. Un diagnóstico bloqueante en cualquier parte del
snapshot bloquea toda la selección, aunque afecte a otra fila. Los avisos compatibles,
blancos y anotaciones se conservan sin inferir aprobación o completitud.
El hash de fila canónica, el hash de bytes de fuente y el digest semántico SQL
son dominios diferentes y se verifican como tales.

La selección se expresa por propuestas individuales y un paquete de lista cerrada,
nunca todas las filas del documento ni todas las aceptadas. Cada paquete fija un
solo documento/proyecto, observación y perfil. Filas no seleccionadas no necesitan
correspondencia ni se adoptan. No se fabrica una captura vacía, un before ausente,
ADDED/UNCHANGED de comparación o decisiones I5 para usar entradas anteriores.

El origen exige Item válido, no vacío ni solo blancos Unicode, y Objective string;
vacío o guion son literales. El título local también debe ser válido y su descripción
puede ser SQL NULL, que se conserva exactamente. Un origen no proyectable bloquea
aunque no vaya a sobrescribir la tarea. Markdown/pipes/Unicode no se renderizan,
desescapan o normalizan. Status, Verified, tachado, bloqueos y anotaciones siguen
siendo evidencia sin efectos operativos.

## Preparación sin reserva y revisión propia

PREPARE registra solo propuesta/recibo D5 y cabeza de revisión propia v0, sin
decisión. No inserta intención, cabeza de correspondencia, destino ni task_sources
y no escribe public.tasks. Varias
propuestas pueden apuntar al mismo origen o tarea; ninguna tiene prioridad por
fecha, por ser la primera preparada o por estar aceptada. Un REJECT o abandono
no deja reservas que haya que liberar.

La propuesta fija `proposed_intent_id=proposal_id`, que es el command_id UUID de
PREPARE_ADOPTION_TASK. Este valor es visible al revisor y solo se convierte en
intent_id si gana APPLY. No se inventa un REGISTER_TASK_INTENT histórico: el FK
vigente de task_intents a commands enlazará el comando real de preparación,
conservando su action y recibo. Es la identidad de la correspondencia; UUID y clave
de la tarea siguen siendo los proporcionados, sin regenerarlos desde el texto.

La razón de adopción es explícita, de 1–1.024 caracteres, sin controles ni solo
blancos Unicode. Declara por qué se propone esa correspondencia; no es prueba
criptográfica de identidad externa. El manifiesto `d5.adoption-task-manifest.v1`
con modo ADOPTION_EXISTING y acción LINK_EXISTING_BACKLOG fija:

- Ámbito, documento+ID, perfil/política, proposed_intent_id y UUID/task_key del destino.
- Observación, SourceRevision, hashes fuente/preview/fila, versión de referencia,
  fila íntegra, posición/localizador, base `d5.source-basis.v1` y digest.
- S: proyección completa del origen y L: título/descripción locales, diferenciados;
  resultado=L y ninguna columna de tarea a escribir. No existe base aplicada previa.
- Snapshot completo de la tarea en UTC, row_version y dominio/digest
  `d5.task-target.v1`; expectativas de ausencia de intención/cabeza/destino y de
  task_sources, BACKLOG y ausencia de operaciones/planificación.
- Razón de adopción, metadatos de preparación no autoritativos y
  `activation_allowed=false`. No se afirma igualdad textual si L difiere de S.

No se introduce versión cero ficticia de una cabeza que aún no existe. La
expectativa es ausencia de correspondencia bajo identidades únicas. El FK y los
campos finales de la intención se derivan de los valores explícitos del manifiesto;
no se añade una columna o marca D2 para declarar la tarea adoptada.

El revisor ACCEPT/REJECT revisa el manifiesto completo con versión esperada propia:
identidad, snapshot de origen, tarea y divergencia, razón y efecto juntos. No se
reutilizan ACCEPT I5/I8/I10/I12/I14 para aprobar adopción. Etiquetas y razones de
revisión son afirmaciones sintéticas; no se introduce autenticación D6.
Una nueva fuente, destino, razón o snapshot de tarea exige otra preparación y
revisión. Revocar/reaceptar deja obsoletos los pins de revisión anteriores.

Los nombres siguientes son interfaces de diseño, todavía no implementadas:

| Paso | Contrato propuesto |
|---|---|
| PREPARE_ADOPTION_TASK | Ámbito, source_key, perfil/política, UUID/task_key, observación y hashes fuente/preview/fila, versión de referencia y razón; deriva manifiesto sin reservar identidades |
| REVIEW_ADOPTION_TASK | proposal_id/hash, versión esperada propia, ACCEPT/REJECT, etiqueta/razón; revisa el manifiesto íntegro |
| PACKAGE_ADOPTION_TASKS | Lista explícita ordenada de proposal_id/hash, review_command_id y review_version; una observación/perfil por paquete |
| APPLY_ADOPTION_TASKS | command_id global D5, ámbito y hash del paquete inmutable; sin texto de resultado ni force |

La lista tiene 1–2.000 propuestas y dominio `d5.adoption-task-package.v1`. Rechaza
orígenes, UUID de tarea y claves internas duplicados, incluso en propuestas
distintas; una tarea no puede ganar dos orígenes. No mezcla variantes I8/I10/I12/I14.
Se mantienen límites de bytes anteriores y separación writer/reviewer/applier/reader.
Reconstrucción e I/O ocurren fuera de locks de escritura D2; se verifica de nuevo
el artefacto antes de revisar, empaquetar y aplicar mediante el adaptador confiable.

## Aplicación atómica y carreras

APPLY futuro exige READ COMMITTED y helper fijo del administrador vigente:
742001 → 742002 → relaciones D3 → mutex D5 742005. Después bloquea destinos
existentes por UUID en orden determinista con FOR UPDATE, sin UPDATE de datos.
No se adquieren esos locks de escritura D2 al preparar/revisar.

El bloqueo de la fila destino también debe cerrar la carrera con inserciones que
referencien la tarea mediante FK, como task_sources: no basta comprobar que está
vacía y luego insertar sin serializar. Tras cualquier espera se comprueba estado
vigente bajo READ COMMITTED. Se prueban sesiones reales y ambos órdenes de llegada;
no se promete impedir DDL arbitrario ni escrituras externas posteriores al commit.

Bajo esa frontera se verifica todo el paquete antes del primer efecto: revisiones
y hashes vigentes, referencia/version, snapshot/digest íntegro de tarea, elegibilidad,
procedencia vacía y ausencia de correspondencias para todas las identidades.
Una intención I8 que reserve antes el mismo origen para otro destino, aunque
solo tenga v0, invalida la adopción.
Si gana adopción, REGISTER_TASK_INTENT antiguo sigue rechazando el destino ocupado.
No se reutiliza automáticamente la correspondencia ganadora de otra propuesta.

Para cada propuesta válida, los efectos indivisibles son:

1. Insertar intención compartida con el proposed_intent_id revisado, ámbito, clave,
   perfil/política y UUID/task_key exactos; FK al comando real de preparación.
2. Insertar destino con sus FK e inicializar cabeza compartida directamente en
   versión 1, con base semántica de la fila real y `projection=S`, incluso si L difiere.
3. Insertar la primera procedencia task_sources con SourceRevision/documento/proyecto
   y localizador exactos. El vínculo acredita origen, no igualdad del texto local.
4. Añadir hecho inmutable de adopción, auditoría D5_TASK_IMPORT con acción propia y
   recibo; conservar S, L, resultado real, identidades y fecha de aplicación en D5.

**Cero INSERT/UPDATE/DELETE en public.tasks**, sin incrementar row_version ni cambiar
created_at u otros campos. No añadir tasks.updated_at. Registrar evidencia D2 no
significa escribir tarea: el recibo distingue `writes_task=false` y procedencia D2.
No se cambian referencias D5, punteros públicos de fuente o cursores de proveedores.

Una fila inválida deja CONFLICT sin correspondencias, vínculos o efectos parciales.
Un aborto/error estructural revierte intención, destino, cabeza, procedencia,
hecho, auditoría y recibo de éxito. No se deja una reserva v0 para reintentar una
adopción parcialmente aplicada. Las restricciones de unicidad/FK siguen vigentes;
una carrera no se resuelve mediante ON CONFLICT que silencie otra identidad.

command_id sigue siendo global D5. Replay exacto devuelve el resultado histórico;
contenido distinto entra en conflicto. Otro comando del mismo paquete confirmado
solo ALREADY_APPLIED enlazado al original. Esta recuperación se distingue de una
primera adopción con procedencia ya presente: no reevalúa el recibo como autorización
para otra tarea ni restaura cabeza o texto. Otro paquete obsoleto queda en conflicto.

## Continuidad y siguiente decisión

Si L=S, I8 puede continuar con una comparación real desde la base adoptada, ACCEPT
I5, referencia/version y revisión I8 propias. Si L difiere, I8 sigue bloqueando
LOCAL_EDIT_CONFLICT y un cambio posterior de fila presente exige I14, con resolución
completa USE_SOURCE/KEEP_LOCAL y sus versiones. La adopción no da override permanente.
Si no hay cambio de origen revisable, I14 no se fuerza fabricando una comparación;
la resolución de edición local aislada conserva su pendiente.

Ausencia I8 conserva su semántica; una reaparición posterior sigue exigiendo I12,
prueba de ausencia aplicada/versionada y declaración de identidad. Si persiste
edición local, la reaparición sigue bloqueada. I10 no puede volver a inicializar
una tarea adoptada ni I8 ordinario adoptar otra. La implementación futura debe
validar esta continuidad llamando a las entradas existentes, sin relajarlas.

Se preservan campos de tarea y snapshots D3 publicados. Se verifican por separado
el digest de tarea y los efectos de evidencia sobre el readset vigente, sin afirmar
invariancia global solo porque no hubo UPDATE tasks. BACKLOG eligible no significa
activación. No hay operaciones, transporte, outbox, entregas, intentos o reservas.

El siguiente paso exige aprobar este contrato y autorizar por separado implementar
y validar su matriz en otro laboratorio V30 desechable con fixtures BACKLOG
sintéticas existentes, separado de dev/D4. SQL privilegiado no demuestra por sí
solo reconstrucción del parser o autenticación de la asociación declarada. Un ABA de
edición externa que restaure todos los valores sin rastro de versión/evidencia
no se presenta como detectable.

Este corte verifica documentos e integridad histórica; no ejecuta la matriz ni
inicia servicios. D5 sigue abierto: adopción con procedencia previa/trabajo, cambio
de correspondencia, IDs reutilizados, resolución local de reaparición o sin cambio
presente, perfil/política, múltiples orígenes y Gentle-AI/routing completo conservan
pendientes. Sin proveedores/credenciales reales, activación, promoción, despliegue
ni ampliación D6. Los cierres D1–D4 y sus evidencias se conservan.
