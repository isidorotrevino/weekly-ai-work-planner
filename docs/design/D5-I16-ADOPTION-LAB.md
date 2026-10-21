# D5 I16 — laboratorio de adopción explícita

Fecha: 2026-10-21. Implementa el [contrato I15](D5-I15-ADOPTION-DESIGN.md)
y su [matriz A01–A34](D5-I15-ADOPTION-REVIEW.md).
[Evidencia propia](../validation/D5-I16-results.md).
D5 abierto; D1–D4 cerrados y D6 pendiente.

English: a separate disposable PostgreSQL lab for reviewed adoption of existing
synthetic BACKLOG tasks. The task row is preserved; correspondence, first direct
provenance and receipt commit together. No activation, promotion or deployment.

## Autorización y ejecución separada

D5-A40: el usuario aprueba I15 y autoriza implementar/validar A01–A34 en otro
laboratorio V30 desechable con fixtures BACKLOG sintéticas existentes, sin activación,
promoción ni despliegue. Conserva A36–A39: tareas sin trabajo/plan ni correspondencia
o task_sources previos, tarea íntegra, snapshot seleccionado/revisión propia y
materialización solo al aplicar el paquete aprobado.

La propuesta V37 permanece en `migrations-d5-proposed/`; el runner nuevo aplica
V1–V30 y V31–V37 sobre una base nueva. No modifica funciones, parsers/perfiles,
contratos D2, runners o evidencias anteriores. No crea roles nuevos ni amplía
permisos sobre objetos anteriores. Se mantiene separado de Compose dev/D4.

```bash
python3 -m testing.D5.run_adoption_lab
```

Requiere Linux, Python 3 y Docker con `postgres:16-bookworm` ya disponible; el runner
no descarga imágenes. Contenedor D5 etiquetado, sin red ni puertos publicados,
volumen anónimo propio. No inicia workers, heartbeat, transporte ni ejecución.
Elimina solo su contenedor/volumen en finally, también ante fallo. Retorna 0 solo
si la campaña pasa. Evidencia bruta privada:
`work/d5/postgres/d5-pg-*/adoption-results.json`; no publicar logs o fuentes privadas.

## Identidad, fuente y revisión

Se eligen proyecto/documento/ID, perfil/política y UUID/task_key explícitos. La tarea
ya existe en el mismo proyecto y su clave debe coincidir; no se busca por título o
similitud. La clave mantiene límites I8: 1–256 caracteres, sin controles. El ID de
origen se conserva completo, incluidos IDs largos, con igualdad y unicidad exactas.

No puede haber intención D5 para ese origen —con cualquier perfil—, UUID o clave,
aunque solo reserve v0. La tarea debe estar BACKLOG, sin operaciones ni planificación
incluida histórica/cancelada, y sin ninguna fila task_sources, incluso idéntica.
No se eliminan hechos, transfieren correspondencias ni reinician cabezas.

La observación exacta debe ser la referencia seleccionada del documento/perfil con
versión esperada. El adaptador reconstruye bytes y preview, hashes y fila única
presente. Diagnósticos bloqueantes en cualquier fila invalidan el snapshot completo.
Los avisos compatibles y anotaciones son evidencia. No se fabrican comparación,
ADDED/UNCHANGED o ACCEPT I5; cada adopción tiene revisión propia del manifiesto.

S es la proyección Item/Objective del origen; L es title/description actuales de
la tarea. Se muestran ambos y el resultado=L. Títulos válidos, texto literal sin
normalización y Objective string; una descripción local SQL NULL se conserva.
Estado/verificación/bloqueos de origen no generan workflow o dependencias.

## Comandos explícitos

El adaptador es `source_ingest/adoption.py`:

```bash
python3 -m source_ingest.adoption --container d5-pg-IDENTIFICADOR --request command.json
```

Solo acepta contenedores D5 desechables etiquetados sin red, no dev/producción.
Archivo JSON cerrado, máximo 4 MiB; rechaza claves duplicadas. Campos comunes:
schema `d5.source-command.v1`, command_id UUID nuevo, action, project_id y document_id.
Roles sintéticos writer/reviewer/applier/reader separados según la acción:

| action | Campos adicionales |
|---|---|
| PREPARE_ADOPTION_TASK | source_key, profile, policy, task_id, task_key, observation_id, content_sha256, preview_sha256, snapshot_row_sha256, expected_reference_version, reason |
| REVIEW_ADOPTION_TASK | proposal_id, manifest_sha256, expected_version, decision, reviewer_label, reason |
| PACKAGE_ADOPTION_TASKS | items: lista explícita ordenada de pins de revisión |
| APPLY_ADOPTION_TASKS | package_sha256 |

El preparador recibe snapshot/procedencia recuperables y resultado completo, no
una propuesta de PATCH. La razón de adopción tiene 1–1.024 caracteres, sin controles
ni solo blancos Unicode. ACCEPT/REJECT propios revisan identidad, fuente, tarea,
divergencia y efecto juntos. Las etiquetas siguen siendo afirmaciones sintéticas.

`AdoptionClient.prepare_request(command_id, pid, doc, observation_id, key,
reference_version, task_id, task_key, profile, policy, reason)` reconstruye la fila y
devuelve request y bytes canónicos para revisión local. El CLI reconstruye esos
bytes y exige que coincidan con los hashes explícitos. Se verifica de nuevo el
manifiesto antes de revisar, empaquetar y aplicar; SQL privilegiado por sí solo no
acredita la semántica del parser o la identidad de la asociación declarada.

Cada pin fija proposal_id/hash, review_command_id y review_version. Paquetes de
1–2.000 propuestas ordenadas por proposal_id, sin repetir origen, tarea o clave,
con una observación/perfil por paquete. No mezcla I8/I10/I12/I14. No se eligen todas
las aceptadas ni se sustituye una referencia por la de fecha más reciente.

`artifact(pid, doc, 'proposal', UUID)` y `'package', hash` recuperan objetos del
ámbito. Los recibos globales se consultan con `read_command`. El CLI retorna 2 ante
CONFLICT, 1 ante fallo y 0 ante resultado ordinario/replay. No publicar exportaciones
que contengan fuentes privadas.

## Correspondencia, atomicidad y carreras

Preparar registra solo propuesta/recibo y cabeza de revisión v0, sin reservar origen
o tarea. `proposed_intent_id=proposal_id` queda visible al revisor. Solo APPLY crea
la intención compartida con ese ID, referenciando el comando real de preparación;
no se fabrica un REGISTER_TASK_INTENT histórico ni se regenera el UUID de la tarea.

APPLY exige READ COMMITTED y helper de administrador vigente:
742001 → 742002 → relaciones D3 → mutex 742005 → tareas ordenadas por UUID con
FOR UPDATE. Ese lock no escribe datos y serializa la inserción de procedencia por
FK. Tras una espera se valida el estado vigente. No se toman locks de escritura D2
al preparar/revisar. Una inserción externa posterior al commit no queda prohibida
para siempre; el contrato garantiza el punto de aplicación bajo sus controles.

Se verifica todo el paquete antes del primer efecto: identidad, ausencia de reserva,
BACKLOG/trabajo/plan/procedencia, referencia y revisión, snapshot/digest completo
de tarea. La aplicación crea intención, destino, cabeza v1 con base de origen y
`projection=S`, primera procedencia, hecho inmutable, auditoría y recibo juntos.
El resultado conserva L y distingue `writes_task=false` de escrituras de evidencia D2.

Cero INSERT/UPDATE/DELETE en public.tasks: no se cambia título, descripción,
row_version, created_at, epic_id, urgencia, fechas o dependencias. Fecha de aplicación
en D5; no añadir tasks.updated_at. No se avanza referencia, puntero público o cursor.
Una fila inválida deja CONFLICT sin efectos parciales. Aborto/error estructural
revierte intención/destino/cabeza/vínculos/auditoría y recibo de éxito, sin reserva v0.

command_id es global D5. Replay devuelve recibo histórico; otro contenido entra
en conflicto. Otro comando del mismo paquete confirmado solo ALREADY_APPLIED,
sin restaurar texto, cabeza o identidad. Un paquete nuevo obsoleto pierde la carrera;
no se apropia de una correspondencia que ganó otra propuesta.

## Continuidad y límites

Si L=S, I5/I8 continúan desde la base adoptada con comparaciones y revisiones reales.
Si L difiere, I8 sigue bloqueando edición local y un cambio presente posterior
requiere I14, sin excepción permanente. Sin cambio revisable no se fuerza I14.
Ausencia/reaparición mantienen I8/I12 y su prueba aplicada/versionada, identidad
declarada y bloqueo de divergencia local. I10 sigue rechazando reinicialización.

Roles mínimos y propietario NOLOGIN sin autoridad general D3/D4; callers sin DML
directo. Se conservan cuerpo/propietario/ACL/config de funciones D5 anteriores y
catálogo public/D2/D3/D4. Se mide digest de tarea/readset D3 por separado de evidencia,
sin prometer invariancia global; snapshots publicados permanecen inmutables.
BACKLOG eligible no es activación. ABA externo sin huella observable no se presenta
como detectable; no se promete escalabilidad o protección frente a DDL arbitrario.

D5 sigue abierto: procedencia/trabajo anteriores, transferencias de correspondencia,
IDs reutilizados para otra entidad, resolución local de reaparición o sin cambio
presente, perfil/política, múltiples orígenes y Gentle-AI/routing completo conservan
pendientes. Sin proveedores/credenciales reales, activación, promoción, despliegue
ni ampliación D6. D1–D4 y sus evidencias se conservan.
