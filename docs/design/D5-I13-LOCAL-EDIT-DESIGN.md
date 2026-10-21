# D5 I13 — contrato propuesto de resolución de ediciones locales

Fecha: 2026-10-21. **Diseño para revisión; sin implementación ni SQL nuevo.**
Base publicada: `01eb985`, [mapeo I8](D5-I8-SYNTHETIC-TASK-LAB.md),
[bootstrap I10](D5-I10-BOOTSTRAP-LAB.md) y
[reaparición I12](D5-I12-REAPPEARANCE-LAB.md).
[Matriz de aceptación y siguiente decisión](D5-I13-LOCAL-EDIT-REVIEW.md).
D5 abierto; D1–D4 cerrados y D6 pendiente.

English: proposed explicit resolution of local title/description edits on owned,
present-row BACKLOG tasks. Review the complete source or local projection; no
field merge, permanent override, SQL implementation or operational activation.

## Decisiones y alcance

| ID | Decisión del usuario | Consecuencia |
|---|---|---|
| D5-A30 | Seguir con resolución local, preparando contrato/matriz antes de SQL | Este corte es documental; no crear migraciones, roles, tareas ni laboratorio |
| D5-A31 | Elegir la proyección completa del origen o conservar la local completa, ambas con revisión explícita | No combinar campos, redactar texto nuevo ni autorizar force genérico |
| D5-A32 | Solo cambios ordinarios sobre una fila presente | Reaparición con edición local, bootstrap y ausencia no entran en esta variante |
| D5-A33 | Mientras el texto local difiera de la proyección del origen registrada, exigir otra resolución explícita ante el siguiente cambio | Conservarlo ahora no concede una excepción permanente ni una preferencia automática |

Las secciones siguientes concretan una propuesta para aprobación. A30–A33 no
aprueban todavía su implementación. Se mantienen V1–V35, funciones, parsers,
perfiles, adaptadores, runners, manifiestos y evidencias históricas.
No se reserva un número de migración ni se publica este diseño sin autorización
para su commit concreto.

## Problema y tres valores visibles

I8 e I12 comparan title/description actuales con la proyección de origen guardada
en `d5.task_mapping_heads.projection`. Si difieren, bloquean con LOCAL_EDIT_CONFLICT,
incluso al preparar de nuevo o si la edición no incrementó row_version. Este
contrato propone una entrada propia y limitada para resolver ese conflicto.
No elimina ese control de las entradas existentes.

El manifiesto presenta tres proyecciones completas, sin normalizar sus strings:

| Valor | Fuente de autoridad | Uso |
|---|---|---|
| B: proyección del origen registrada | Cabeza D5 de la última aplicación confirmada | Detectar diferencia local; no reconstruirla desde la tarea actual |
| L: proyección local actual | Snapshot completo de la tarea, capturado al preparar | Evidencia exacta del texto local que se conservaría o sustituiría |
| S: proyección del origen entrante | Item/Objective de la fila después, reconstruida desde bytes | Texto del origen aceptado en I5; no convertirlo en texto manual |

La resolución exige L distinto de B. Si coinciden, se usa el flujo I8 ordinario;
esta variante no es una vía alternativa para eludir sus controles. S puede
coincidir con B o con L: una modificación de otros campos de la fila también
produce un cambio de origen revisable. No se infiere un merge aunque los cambios
locales y remotos afecten campos diferentes.

Se conserva exactamente `(project_id, document_id, source_key)`, intención,
perfil fijo, política `d5.task-projection.v1`, UUID y task_key. Debe existir una
tarea materializada propiedad de esa intención, creada por I8/I10 o conservada
tras I12. No hay búsqueda por nombre, adopción, cambio de identidad ni tarea nueva.

## Cambio de origen y condiciones de entrada

Hace falta una comparación I5 PREVIEW_ONLY reconstruida, del mismo ámbito/perfil,
con fila CHANGED, antes y después presentes para ese ID y sin diagnósticos
bloqueantes en ninguna captura. La base semántica íntegra de antes debe coincidir
con `task_mapping_heads.source_basis`, no solo su título. Se permite una observación
antes distinta si la fila semántica coincide; cambios de posiciones son procedencia.

La referencia seleccionada debe seguir siendo esa observación antes, con versión
esperada exacta. Se exige ACCEPT I5 vigente por comando/versión y hashes de fila y
reporte. Ese ACCEPT no autoriza descartar texto local: hace falta la revisión
propia del manifiesto de resolución. Ingerir, leer, preparar y revisar no avanzan
referencias, cursores ni punteros públicos.

No se fabrican cambios o comparaciones para resolver una edición local aislada:
UNCHANGED sin fila revisable, ADDED, ausencia y reaparición quedan fuera. Tampoco
se resuelve una base de origen divergente, perfil/política distinta o identidad
reutilizada mediante esta entrada. Un rechazo no libera la identidad ni modifica
la tarea. La procedencia exacta y los límites de bytes anteriores se mantienen.

La tarea debe seguir en BACKLOG, sin ninguna operación ni entrada de planificación,
incluso histórica o cancelada. No se borran operaciones/planes ni se cambia el
estado para admitirla. Campos locales ajenos a title/description se conservan y
forman parte del CAS completo; no son objetivos de reconciliación.

## Elección explícita y manifiesto completo

El preparador elige exactamente USE_SOURCE o KEEP_LOCAL y aporta una razón
explícita no vacía ni solo blancos Unicode, máximo 1.024 caracteres y sin controles.
No se acepta un resultado proporcionado libremente: el servidor lo deriva de S
o L. El revisor acepta/rechaza el manifiesto íntegro, con elección, razón, pérdida
de texto local si existe, destino, procedencia y efecto visibles juntos.
La razón y la etiqueta del revisor son afirmaciones sintéticas, no autenticación D6.

El manifiesto propuesto `d5.local-edit-task-manifest.v1` fija:

- Intención completa, ámbito/ID/perfil/política, UUID/task_key y versión de cabeza.
- Base semántica actual y hashes, B, L y S diferenciados y con hashes por dominio;
  nueva base de origen íntegra, incluidos campos, tachado y texto de anotaciones.
- Comparación y fila completas, hashes, observaciones antes/después, SourceRevision
  y localizador exactos; comando/versión ACCEPT I5 y referencia/version esperados.
- Snapshot completo en UTC de la tarea, row_version, dominio/digest
  `d5.task-target.v1`; no basta con un CAS de title/description o de row_version.
- Elección, razón, proyección de resultado derivada, acción, campos que cambiarían,
  `activation_allowed=false` y metadatos de preparación no autoritativos.

Una elección, razón, snapshot o fuente diferentes requieren nueva preparación y
revisión. No se reutiliza una aceptación I8, I10 o I12 para autorizar esta variante.
La revisión propia es versionada, admite ACCEPT/REJECT y no es transferible entre
manifiestos. Revocar/reaceptar con el mismo contenido invalida los pins antiguos.

Los nombres de interfaz siguientes son de diseño, todavía no ejecutables:

| Comando propuesto | Entrada específica y efecto |
|---|---|
| PREPARE_LOCAL_EDIT_TASK | Intención, comparación/hash de reporte/fila, versiones esperadas de referencia/cabeza, elección y razón; deriva manifiesto sin escribir tarea |
| REVIEW_LOCAL_EDIT_TASK | proposal_id/hash, versión esperada propia, ACCEPT/REJECT, etiqueta/razón; revisa el manifiesto completo |
| PACKAGE_LOCAL_EDIT_TASKS | Lista explícita ordenada de proposal_id/hash, review_command_id y review_version; no selección por fecha ni todos los ACCEPT |
| APPLY_LOCAL_EDIT_TASKS | command_id global D5, ámbito y hash del paquete inmutable; no acepta texto, máscara de campos o force |

El paquete tiene dominio `d5.local-edit-task-package.v1`, de 1 a 2.000 propuestas,
una por intención. Puede contener elecciones distintas de esta misma variante;
no se mezcla con paquetes I8/bootstrap/reaparición. Parsing, reconstrucción y
verificación del adaptador confiable se repiten antes de preparar, revisar,
empaquetar y aplicar. SQL privilegiado por sí solo no acredita ese parsing.

## Efectos y continuidad de A33

| Elección | Condición | Efecto en la tarea |
|---|---|---|
| USE_SOURCE | S distinto de L | PATCH solo title/description a S y row_version +1 una vez |
| USE_SOURCE | S igual a L | Enlace/confirmación de evidencia, sin reescribir tarea ni aumentar row_version |
| KEEP_LOCAL | L distinto de B, cualquiera que sea S | Conservar exactamente toda la fila de tarea, sin incremento de row_version |

S exige Item string no vacío/solo blancos Unicode y Objective string, como la
proyección I8. L debe tener título válido; su descripción puede ser SQL NULL,
porque D2 lo admite: KEEP_LOCAL conserva ese null, sin convertirlo en string vacío.
S inválida bloquea incluso si se elige KEEP_LOCAL: no se registra como proyección
válida del origen una fila que el contrato no podría proyectar.

En las dos elecciones se avanza la cabeza una vez, registrando la nueva base
semántica **de origen** y `projection=S`. KEEP_LOCAL nunca guarda L en projection:
ese campo mantiene el significado histórico de I8/I12. Un hecho nuevo e inmutable
D5 fija elección, B/L/S, resultado real, razones y recibo de aplicación. La
proyección resultante de la tarea y la proyección del origen son conceptos distintos;
el lector debe presentar ambos, sin afirmar que la tarea reproduce el origen.

Se añade o reutiliza el vínculo task_sources exacto a la fila después, sin modificar
vínculos anteriores. Ese vínculo acredita procedencia, no igualdad del texto de la
tarea; el manifiesto/recibo revela si se conservó texto local. No hay vínculo a una
fila ausente. Hecho, cabeza, vínculo, auditoría y recibo se confirman juntos.
Fecha de aplicación en D5; no añadir tasks.updated_at ni tocar created_at.

Tras KEEP_LOCAL con L distinto de S, I8 ordinario sigue devolviendo
LOCAL_EDIT_CONFLICT en el siguiente cambio: la proyección registrada es S y la
tarea conserva L. Una nueva comparación real, ACCEPT I5 y resolución completa
serán necesarios; la revisión anterior no autoriza un cambio posterior.
No se introduce flag persistente de override ni se relajan funciones antiguas.

Si el resultado coincide con S —por USE_SOURCE o por convergencia L=S—, I8 puede
continuar desde la nueva base bajo sus controles habituales. Una edición local
posterior vuelve a bloquear. Una vuelta del texto a la proyección registrada no
restaura versiones ni recibos históricos; siempre se comprueba el estado actual.
Una secuencia de ediciones A→B→A con aumento de row_version invalida el snapshot;
el sistema no promete detectar una edición externa que restaure todos los valores
sin dejar ningún cambio de versión o evidencia observable.

La ausencia I8 conserva su semántica y puede conservar una divergencia local.
La reaparición I12 sigue bloqueada mientras L difiera de la proyección registrada;
una resolución anterior no sustituye su prueba de ausencia aplicada/versionada ni
su declaración de identidad. La extensión a reaparición requiere otro contrato.

## Transacción, permisos y preservación

APPLY futuro exige READ COMMITTED y el helper de administrador vigente:
742001 → 742002 → relaciones D3 → mutex D5 742005, seguido de intenciones/cabezas y
destinos ordenados. No se toman locks de escritura D2 en preparación/revisión.
Se valida el paquete entero antes del primer efecto: ámbito/propiedad, bases y
versiones, revisiones, referencia, comparación, B/L/S, elección derivada, snapshot
completo, BACKLOG y ausencia de trabajo/planificación. Se comprueba otra vez que
L difiere de B; no se aplica una resolución obsoleta tras convergencia externa.

Una fila inválida invalida todo el paquete, con recibo de negocio CONFLICT sin
efectos parciales. Un error estructural o aborto revierte todos los efectos y el
recibo de éxito. command_id es global D5: replay exacto devuelve el recibo histórico,
contenido distinto entra en conflicto y otro comando del mismo paquete confirmado
solo devuelve ALREADY_APPLIED enlazado al original. Nunca restaura texto o cabeza.

Las entradas y artefactos nuevos serían aditivos, con cabeza/destino compartidos.
Se mantiene separación writer/reviewer/applier/reader, propietario NOLOGIN y helper
fijo sin SQL arbitrario. Sin DML directo para callers, autoridad general D3/D4,
relajación de LOCAL_EDIT_CONFLICT antiguo o cambios en contratos D2 aprobados.
La auditoría distingue elección y acción bajo D5_TASK_IMPORT; no STATE_CHANGED,
no outbox ni llamadas a ejecución. El recibo distingue escritura de tarea de
escrituras de evidencia D2: KEEP_LOCAL no escribe tasks aunque añada task_sources.

PATCH cambia el digest de tarea D3 y vuelve obsoleta una captura anterior. Los
snapshots publicados permanecen inmutables; no se promete readset global constante.
KEEP_LOCAL/enlace no reescriben tarea; los efectos de evidencia se verifican por
separado. `task_eligible=true` en BACKLOG no equivale a activación.

## Siguiente decisión y límites

El siguiente paso exige aprobar este contrato completo y autorizar expresamente
implementación y matriz en otro laboratorio V30 desechable, con fixtures sintéticas,
separado de dev/D4. Este diseño no ejecuta esa matriz ni inicia servicios.

Siguen fuera adopción, reutilización de IDs para otra entidad, resolución local de
reaparición/ausencia sin cambio presente, texto manual/mezcla de campos, cambios de
perfil/política, múltiples orígenes y formato Gentle-AI/routing completo. D5 sigue
abierto. Proveedores/credenciales reales, activación, promoción, despliegue y D6
conservan sus exclusiones; los cierres y evidencias D1–D4 se preservan.
