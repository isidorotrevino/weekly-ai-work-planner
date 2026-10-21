# D5 I7 — contrato propuesto de mapeo a tareas D2

Fecha: 2026-10-21. **Diseño para revisión; sin implementación ni SQL nuevo.**
Base publicada: `a76aa3c`, [I6 sobre V30](D5-I6-V30-COMPATIBILITY.md).
[Matriz de aceptación y decisión siguiente](D5-I7-TASK-MAPPING-REVIEW.md).
D5 abierto; cierres D1–D4 y D6 pendiente conservados.

## Decisiones expresas y alcance

| ID | Elección del usuario | Consecuencia |
|---|---|---|
| D5-A14 | A: contrato y matriz para revisión, sin SQL nuevo ni escrituras en tareas | Este corte no aplica propuestas ni crea roles, tareas o bases |
| D5-A15 | A: Item → título, Objective → descripción; resto como evidencia | Proyección mínima fija, sin workflow/dependencias inferidos |
| D5-A16 | A: correspondencia explícita con UUID y clave interna de tarea | Sin búsqueda/adopción por nombre o similitud |

Las reglas siguientes concretan una **propuesta de primer laboratorio futuro**.
A14–A16 no autorizan implementarlo, crear tareas, ampliar permisos o desplegarlo.
No se modifica V1–V32 ni los parsers/perfiles, adaptadores o runners existentes.

## Identidad de origen y destino

La identidad lógica es `(project_id, document_id, source_key)` exacta. El documento
ya debe estar registrado en D5 y pertenecer al proyecto. Ruta, título, hash de
contenido y UUID de candidato/perfil no sustituyen esa identidad. Los IDs largos
se conservan; un digest puede servir de índice, nunca truncar o reasignar el ID.

`REGISTER_TASK_INTENT` propuesto recibe esos tres campos, un perfil tabular
admitido, versión de política fija, task UUID explícito y task_key interna explícita.
El perfil puede ser estricto o compatible, pero queda fijado en el registro. La
unicidad de documento+ID ignora el perfil: cambiar de perfil no puede crear otra
tarea para el mismo origen. Cambiar perfil/política exige un contrato posterior;
no se reinterpreta automáticamente el UUID de identidad de los artefactos I2/I3.

La intención reserva identidad, **no materializa una tarea**. El primer laboratorio
futuro admitiría solo destinos nuevos, sin adopción de tareas preexistentes, incluso
por UUID explícito. UUID o clave ocupados, otra intención con ese destino o ámbito
incompatible producen conflicto. No se elige una clave por prefijo parecido ni se
reutiliza una tarea porque coincida el título. Adopción, fusión y múltiples orígenes
para una tarea quedan fuera de este primer contrato.

Registro y tarea deben compartir proyecto. La clave interna es independiente del
ID externo; no se copia implícitamente ni se genera desde texto de la fuente.
No se crean proyectos, requisitos o épicas artificiales. El vínculo directo
`d2.task_sources` aprobado en V10 permite que epic_id siga NULL.

## Proyección mínima versionada

Política propuesta: `d5.task-projection.v1`, sobre los campos ya reconstruidos del
perfil tabular. No se añade una gramática Gentle-AI ni interpretación de Markdown.

| Campo de origen | Destino/uso propuesto |
|---|---|
| fields.item | tasks.title exacto; vacío o solo blancos bloquea el paquete |
| fields.objective | tasks.description exacta, incluido vacío o guion literal |
| ID, componentes, bloqueos, Status, Verified, Source, tachado y anotaciones | Evidencia de origen; no crean estados, dependencias, recursos, aprobaciones o verificaciones |

Se usan los strings conservados por el parser: no se renderizan enlaces, resuelven
URLs, quitan backticks, desescapan pipes o normalizan Unicode. La captura original
sigue siendo la evidencia de bytes; la proyección solo es texto para una tarea.
La política es fija: no hay máscara de campos elegida por cada aplicación.

Una tarea nueva se propondría con status BACKLOG, row_version 0, epic_id NULL,
urgency 0, deadline_at NULL y deferred_count 0, independientemente del estado
que afirme la fuente. No se crea ninguna operación, reserva, lease, plan o entrega.
`d2.task_eligible` evalúa dependencias y puede ser true para una tarea BACKLOG:
no se usará ese booleano como prueba de activación o de ejecución. La ausencia de
operaciones y transiciones operativas deberá comprobarse separadamente.

## Aprobar una fila no aprueba su destino D2

ACCEPT I5 revisa un cambio de origen. No identifica todavía una tarea, su versión,
la política de campos ni su efecto D2; tampoco lo hace un recibo de simulación.
Se propone una fase explícita adicional:

1. `PREPARE_TASK_PROPOSAL`: reconstruir comparación/fila; resolver una intención
   registrada y preparar un manifiesto inmutable. No escribir la tarea.
2. `REVIEW_TASK_PROPOSAL`: aceptar/rechazar el **manifiesto completo**, con versión
   esperada propia. Esta decisión es distinta del ACCEPT de origen I5.
3. `APPLY_TASK_PROPOSALS`: aplicar únicamente el paquete explícito aceptado, si
   siguen coincidiendo todas sus precondiciones. Todavía no implementado/autorizado.

El manifiesto fija proyecto/documento/ID/perfil, intención y versión, UUID/clave
interna, política, comparación/hash, fila/hash, observaciones y revisión D2 de
procedencia, ACCEPT I5 y versión, referencia «antes» y versión, acción solicitada,
proyección antes/después y expectativa del destino. El paquete fija la lista
ordenada completa de manifiestos seleccionados; su hash forma parte del recibo.
No se seleccionan automáticamente todos los ACCEPT ni el resultado de fecha mayor.

La expectativa de una tarea existente incluye row_version y snapshot completo
versionado de la fila D2. Se contrasta el valor guardado y su digest, no solo hash.
El snapshot del destino se normaliza en SQL con zona UTC y dominio de hash
versionado propio; no se usa como si fuera el hash canónico de una captura fuente.
Para CREATE se fija ausencia del UUID y de `(project_id, task_key)`.

## Acciones propuestas y conservación de ediciones locales

| Situación | Acción propuesta | Restricción |
|---|---|---|
| ADDED o CHANGED con intención no materializada y destino ausente | CREATE_BACKLOG explícito | No asumir que CHANGED implica una tarea existente |
| CHANGED con tarea ya creada por esta correspondencia | PATCH_BACKLOG | Solo title/description, con controles de origen y destino |
| CHANGED solo en campos no mapeados | LINK_SOURCE_EVIDENCE | Conservar tarea; añadir procedencia cuando corresponda |
| ABSENT_IN_OBSERVATION | KEEP_EXISTING_NO_DELETE | Sin borrar/cerrar tarea, liberar identidad o inventar una fila «después» |
| UNCHANGED | Sin propuesta nueva | Un movimiento de posición no importa ni reescribe tareas |

PATCH y enlace de evidencia requieren tarea propia de esta correspondencia,
BACKLOG, sin operaciones ni entradas de planificación asociadas. Las mutaciones
posteriores de workflow quedan en los entrypoints D2 aprobados; este contrato no
los redefine. Otros estados o trabajo asociado bloquean el paquete para revisión.

Se guarda la última proyección aplicada a title/description. Si los campos actuales
difieren de esa base, hay LOCAL_EDIT_CONFLICT aunque el preparador ya haya visto
la edición o row_version no se haya incrementado. No hay sobrescritura forzada,
mezcla automática ni resolución por fecha. Otros campos locales se preservan;
la expectativa completa detecta cualquier cambio ocurrido después de preparar.

Un PATCH real incrementaría row_version una vez, conservaría created_at y fijaría
updated_at de manera explícita. Un enlace de evidencia sin cambio de campos no
reescribe esa fila ni incrementa su row_version. El journal de correspondencia
avanza su propia versión para dejar trazabilidad del efecto confirmado.

La base de origen por fila se define con todos los campos, tachado y texto de
anotación; excluye ubicaciones, IDs de candidato y metadatos de recepción. Su
esquema/hash son propios y versionados, sin sustituir hashes I1–I5. Esa base debe
coincidir con la fila «antes» para actualizar un destino ya materializado. Permite
una captura «antes» distinta si la fila semántica no cambió, evitando bloquear
una fila solo porque hubo otras actualizaciones o desplazamientos en el documento.

La reaparición ADDED de un ID ya materializado no se trata como otra tarea nueva:
queda REAPPEARANCE_REVIEW_REQUIRED en este primer perfil. Una ausencia conserva la
última base presente, proyección y vínculos. Su recibo puede reconocer la ausencia,
pero no añade task_sources que afirme que había una fila ausente en esa revisión.
La carga inicial de un registro íntegro sigue requiriendo un contrato específico;
no se inventa una captura vacía para fabricar cambios ADDED.

## Procedencia, auditoría y referencias

CREATE/PATCH/enlace de evidencia insertan `d2.task_sources` con task UUID,
SourceRevision de la observación «después», documento/proyecto y localizador exacto
hash+línea de esa fila. Sus FKs existentes deben cumplir ámbito y revisión/documento.
Se conserva toda procedencia anterior: no UPDATE/DELETE de vínculos inmutables.
Un vínculo idéntico se reutiliza solo tras comprobar sus campos, sin duplicarlo.

Se proponen hechos D5 de intención, manifiesto, revisión de manifiesto y aplicación;
cabezas versionadas separadas para identidad/base aplicada. Una relación de destino
materializado con FK tarea/proyecto aparece solo al crear la tarea: la intención
previa no simula un FK a una tarea que aún no existe.

La tarea, vínculos, bases aplicadas, auditoría y recibo se confirmarían juntos.
No se mueve la referencia D5 al «después», ni los punteros públicos D2, bindings o
cursors de proveedores. Un CREATE/PATCH cambia el estado que captura D3: ya no debe
prometerse la conservación del digest de I6. La futura prueba exigirá que D3 detecte
la base anterior como obsoleta y que ningún snapshot publicado sea reescrito.

Se propone auditoría explícita de importación, sin fabricar STATE_CHANGED ni llamar
a publicación, despacho o ejecución. La notificación/planificación automática no
forma parte de este primer contrato de tareas BACKLOG sin operaciones.

## Atomicidad, concurrencia y permisos propuestos

El futuro APPLY comprobaría bajo locks: ámbito, hashes/reconstrucción, decisiones
vigentes de origen y destino, perfil/política, intención/base y versiones, referencia
actual igual al «antes» con versión exacta y expectativas del destino. Fallar una
fila revierte todo el paquete. Un conflicto de negocio confirmado tiene recibo;
fallos estructurales hacen rollback sin presentar éxito. No hay aplicación parcial.

Los IDs de comando siguen siendo globales D5. Replay exacto devuelve recibo histórico,
sin restaurar tareas o heads viejos. El paquete inmutable tiene un único hecho de
aplicación: otro command_id sobre el mismo paquete ya aplicado solo obtendría un
acuse ALREADY_APPLIED enlazado al original, sin incrementar versiones. Otro paquete
sobre bases/versiones obsoletas produce conflicto. Un recibo no acredita estado actual.

El orden deberá respetar D3/D2: frontera d3.lock_state (742001 → 742002 → relaciones
vigentes), después mutex D5 742005 y filas/correspondencias ordenadas. No llamar a
D3 después de adquirir primero el mutex D5. Preparar/revisar solo lee snapshots del
destino; no toma locks de escritura D2 antes de esa frontera. READ COMMITTED;
reconstrucción y I/O fuera de locks. El primer laboratorio priorizará corrección,
sin afirmar escalabilidad ni protección frente al propietario que cambie DDL.

`d3.lock_state` es invoker y bloquea muchas relaciones: un aplicador con permisos
mínimos no puede invocarlo suponiendo que basta EXECUTE. Se propone un helper fijo
SECURITY DEFINER del propietario confiable que adquiera exclusivamente esa frontera
y el mutex D5, sin SQL dinámico recibido ni mutación de estado. Solo un propietario
nuevo y separado de aplicación podría llamarlo; los roles actuales y d5_owner
conservarían sus permisos I6. Este diseño de privilegios deberá probarse, no asumirse.

El futuro rol de aplicación expondría solo el entrypoint APPLY; sin DML directo ni
funciones D3/D4 generales. Un propietario NOLOGIN separado tendría los permisos
mínimos de tareas/procedencia/auditoría requeridos. Etiquetas de revisor no son
identidad autenticada; autenticación y distribución real de credenciales siguen
en D6. No se reutiliza ACCEPT I5 como autorización de ejecución.

## Fuera de este corte y gate siguiente

No hay migración nueva, función SQL, helper privilegiado, cambio de rol, tarea,
vínculo operativo o prueba de aplicación ejecutada. No se reserva número V33.
Los proveedores y credenciales reales, promoción, despliegue y cierre D5 siguen
fuera. La siguiente decisión será revisar este contrato y, si se aprueba, autorizar
por separado un laboratorio sintético que lo implemente y pruebe su matriz.
