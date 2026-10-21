# D5 I8 — tareas BACKLOG sintéticas en laboratorio V30

Fecha: 2026-10-21. Implementa el [contrato I7](D5-I7-TASK-MAPPING-DESIGN.md)
y su [matriz M01–M27](D5-I7-TASK-MAPPING-REVIEW.md).
[Evidencia de esta campaña](../validation/D5-I8-results.md).
D5 sigue abierto; D1–D4 cerrados y D6 pendiente.

## Autorizaciones y ajuste del contrato

- A17: el usuario aprueba I7 y autoriza implementarlo y validar M01–M27 en una
  base V30 desechable, con tareas BACKLOG sintéticas, separada de dev/D4, sin
  promoción, despliegue ni operaciones de producto. Sustituye el gate de diseño
  solamente A14 para este laboratorio.
- A18: se permite una operación sintética exclusivamente dentro de una transacción
  negativa con rollback obligatorio, sin ejecutarla ni crear entregas o reservas.
- A19: V30 no tiene `tasks.updated_at`; tiene `created_at` y `deadline_at`.
  Se corrige la expectativa de I7/M09: PATCH cambia exclusivamente title,
  description y row_version; la fecha se guarda en `d5.task_applications.applied_at`.
  No se añade una columna ni se modifica el esquema D2 aprobado. Los documentos
  I7 se conservan como propuesta histórica; este ajuste expresa su resolución.

## Ejecución aislada

```bash
python3 -m testing.D5.run_mapping_lab
```

Requiere Docker local e imagen ya disponible `postgres:16-bookworm`, Linux y Python
3 con biblioteca estándar. El runner nuevo aplica V1–V30 y V31/V32/V33 a otro
contenedor etiquetado `wap.d5.disposable=true`, sin red ni puerto publicado, con
volumen anónimo propio. Ejecuta las regresiones I4/I5/I6 antes de crear tareas en
M01–M27. Elimina solo su contenedor y volumen al terminar, también ante fallo.
Retorna 0 al completar la campaña sin fallos. Resumen y diagnósticos privados:
`work/d5/postgres/d5-pg-*/mapping-results.json`.

V33 permanece en `migrations-d5-proposed/`; ningún runner anterior la descubre.
No se integra en Compose dev, en las baterías SQL históricas o en el laboratorio
D4. No inicia workers, heartbeat, transportes, planificación o ejecución.

## Flujo explícito

El adaptador nuevo es `source_ingest/task_mapping.py`. Usa archivos JSON cerrados;
no hay selección automática del último objeto o de todas las filas aceptadas.
Cada archivo incluye `schema: d5.source-command.v1`, command_id UUID nuevo,
action, project_id y document_id, además de estos campos:

| action | Campos adicionales |
|---|---|
| REGISTER_TASK_INTENT | source_key, profile, policy, task_id, task_key |
| PREPARE_TASK_PROPOSAL | intent_id, comparison_id, row_sha256, report_sha256, expected_reference_version |
| REVIEW_TASK_PROPOSAL | proposal_id, manifest_sha256, expected_version, decision, reviewer_label, reason |
| PACKAGE_TASK_PROPOSALS | items: lista explícita ordenada por proposal_id |
| APPLY_TASK_PROPOSALS | package_sha256 |

La preparación presupone como paso anterior la
comparación y revisión de origen I5. Cada pin de paquete contiene exactamente
proposal_id, manifest_sha256, review_command_id y review_version; no admite dos
propuestas de la misma intención. `policy` es `d5.task-projection.v1`; profile es
`task-register.v1` o `task-register-compat.v1`, fijo por documento+ID. Versiones
son enteros JSON no negativos. ACCEPT/REJECT del manifiesto usa revisión propia.
Etiquetas de revisión son afirmaciones sintéticas, no identidad autenticada.

```bash
python3 -m source_ingest.task_mapping --container d5-pg-IDENTIFICADOR --request command.json
```

El CLI solo acepta contenedores D5 desechables etiquetados sin red. No es una
conexión a dev/producción ni un servicio persistente. El runner destruye su base al
terminar; para revisar artefactos durante una investigación se usa la clase
`MappingLab` con limpieza en finally. Los métodos `artifact(..., 'proposal', UUID)`
y `artifact(..., 'package', hash)` exportan contenido para revisión explícita;
los recibos globales se consultan con `read_command`. No publicar esos archivos
si contienen fuentes privadas. El CLI devuelve 2 ante conflicto y 1 ante fallo
estructural/verificación. Un replay devuelve el resultado histórico, no estado
actual ni una restauración de la tarea.

## Identidad, efectos y evidencia

REGISTER reserva proyecto/documento/ID → UUID/clave proporcionados; no crea tarea ni
adopta tareas existentes. Los IDs largos se conservan completos con índice por
SHA; la igualdad incluye el valor, sin truncar. La FK de destino se materializa
solo al crear una tarea. No hay bootstrap UNCHANGED ni reaparición automática.

PREPARE fija un manifiesto inmutable con intención y versión de base, report/fila
completos, ACCEPT I5, referencia antes/version, revisión de procedencia, proyección,
acción y snapshot completo del destino. El adaptador reconstruye el reporte desde
los bytes fuente y previews antes de preparar, revisar, empaquetar y aplicar.
Como en I4/I5, la semántica del parser pertenece al adaptador confiable; una llamada
SQL directa por un escritor privilegiado no acredita esa reconstrucción.

CREATE usa BACKLOG v0, sin epic/deadline, urgencia y diferimientos cero, con
Item → title y Objective → description literales. Status, Verified, tachado,
bloqueos y anotaciones no alteran workflow. PATCH conserva campos locales ajenos a
la proyección y created_at; incrementa row_version exactamente una vez. Una edición
local de title/description bloquea incluso si se prepara después de verla.

La base semántica guarda todos los fields, source_struck y el texto de anotación,
con dominio de hash `d5.source-basis.v1`; excluye posiciones y metadatos de recepción.
El destino usa JSONB SQL en UTC y hash `d5.task-target.v1`; no se confunde con
la canonicalización de fuentes. Una revisión antes diferente puede servir si la
fila semántica sigue coincidiendo con la última aplicada.

LINK_SOURCE_EVIDENCE no escribe la fila de tarea. KEEP_EXISTING_NO_DELETE conserva
la última base presente, proyección, identidad y vínculos, sin inventar una fila
después. CREATE/PATCH/LINK añaden task_sources con SourceRevision, ámbito y
localizador exactos; reutilizan un vínculo idéntico y no modifican los anteriores.
No avanzan referencia D5, puntero público SourceDocument ni cursors de proveedores.

## Transacciones y separación de permisos

APPLY adquiere primero el helper fijo privilegiado que llama a d3.lock_state:
742001 → 742002 → relaciones D3 vigentes → mutex D5 742005. Después valida todas
las filas y bloquea correspondencias en orden de identidad. Exige READ COMMITTED.
No se toman locks de escritura D2 al preparar/revisar. Parsing y reconstrucción se
hacen fuera de la transacción de aplicación.

El helper pertenece al administrador de la base y solo es ejecutable por el
propietario nuevo d5_apply_owner NOLOGIN. Este tiene permisos limitados de
lectura/escritura de tareas, inserción de procedencia/auditoría y sus objetos D5;
no recibe USAGE D3/D4. d5_applier solo expone APPLY y lectores de artefactos;
writer prepara/empaqueta, reviewer acepta manifiestos y reader solo lee. Los roles,
funciones y ACL anteriores no se amplían. No hay DML directo para callers ni SQL
dinámico recibido por el helper.

Se comprueban referencia/version, revisiones vigentes de origen y manifiesto,
intención/base, snapshot y digest del destino, BACKLOG sin trabajo/plan para
PATCH/LINK y ausencia UUID/clave para CREATE. Un fallo de negocio deja recibo
CONFLICT sin aplicar ninguna fila. Un error estructural revierte tarea, vínculos,
base, auditoría y recibo de éxito. Un paquete tiene un único efecto; otro comando
sobre el mismo paquete obtiene ALREADY_APPLIED enlazado al original. No restaura
versiones ni referencias. La auditoría usa D5_TASK_IMPORT, sin STATE_CHANGED ni
outbox automático.

CREATE/PATCH cambian el readset D3: las capturas anteriores quedan obsoletas por
su digest. No se promete conservar el digest de I6 al aplicar tareas. Los planes
publicados de fixture y sus snapshots permanecen inmutables.

## Pendientes que conserva D5

Esta implementación no cierra D5. Siguen pendientes bootstrap inicial explícito,
reaparición, adopción, resolución de ediciones locales, cambios de perfil/política,
múltiples orígenes y validación de formatos Gentle-AI/routing con muestras adecuadas.
También siguen fuera proveedores/credenciales reales, requisitos/epics nuevos,
activación, promoción y despliegue. La autenticación real de revisores y la
distribución de credenciales siguen en D6; este corte no las amplía.
