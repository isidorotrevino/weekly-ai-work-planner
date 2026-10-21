# D5 I10 — laboratorio de carga inicial explícita

Fecha: 2026-10-21. Implementa el [contrato I9](D5-I9-BOOTSTRAP-DESIGN.md)
y su [matriz B01–B28](D5-I9-BOOTSTRAP-REVIEW.md).
[Evidencia de esta campaña](../validation/D5-I10-results.md).
D5 abierto; D1–D4 cerrados y D6 pendiente.

## Autorización y alcance

D5-A23: el usuario aprueba I9 y autoriza implementar y validar B01–B28 en otro
laboratorio V30 desechable, con tareas BACKLOG sintéticas; sin promoción,
despliegue ni activación. Se mantienen A21 (IDs explícitos, intención v0 sin
destino) y A22 (revisión propia del manifiesto completo, sin ACCEPT I5 ficticio).

V34 es una propuesta adicional en `migrations-d5-proposed/`. No modifica V1–V33,
parsers, adaptadores, entrypoints o runners anteriores. Su esquema usa artefactos
bootstrap propios; las cabezas y destinos de correspondencia siguen siendo los I8.
No hace falta cambiar las tablas D2 o ampliar la proyección Item/Objective.

## Ejecutar la campaña nueva

Con Linux, Python 3 estándar, Docker e imagen local `postgres:16-bookworm`:

```bash
python3 -m testing.D5.run_bootstrap_lab
```

Crea una base nueva V1–V30 seguida de V31–V34, sin red ni puertos publicados.
Usa contenedor D5 etiquetado y volumen anónimo propios, con eliminación en finally.
Los diagnósticos privados quedan en `work/d5/postgres/d5-pg-*/bootstrap-results.json`.
Retorno 0 significa PASS de la campaña; otro retorno conserva diagnóstico privado.
No inicia Compose dev/D4, workers, heartbeat o ejecución de operaciones.

El orden es I4 (21), I5 (15), I6 (5), I8 (27) y B01–B28 (28): 96 casos ejecutados.
La fixture negativa de operación de M12 mantiene A18: solo dentro de una transacción
revertida, nunca ejecutada. Los planes publicados de M26/B27 son fixtures del
propietario, sin llamar a d3.publish, emitir outbox o despachar trabajo.

## Cuatro comandos propios

El adaptador nuevo es `source_ingest/bootstrap.py`. Recibe un archivo JSON cerrado
con `schema: d5.source-command.v1`, command_id, action, project_id, document_id y
los campos adicionales siguientes. Los UUID y las versiones deben ser explícitos.

| action | Campos adicionales |
|---|---|
| PREPARE_BOOTSTRAP_TASK | intent_id, source_key, observation_id, content_sha256, preview_sha256, snapshot_row_sha256, expected_reference_version |
| REVIEW_BOOTSTRAP_TASK | proposal_id, manifest_sha256, expected_version, decision, reviewer_label, reason |
| PACKAGE_BOOTSTRAP_TASKS | items: pins ordenados por proposal_id, sin repetidos |
| APPLY_BOOTSTRAP_TASKS | package_sha256 |

Cada pin contiene exactamente proposal_id, manifest_sha256, review_command_id y
review_version. Un paquete admite 1–2.000 manifiestos de intenciones distintas.
No se mezclan con manifiestos de comparación I8. La revisión propia acepta o
rechaza el manifiesto entero; su versión monotónica invalida pins antiguos por ABA.

```bash
python3 -m source_ingest.bootstrap --container d5-pg-IDENTIFICADOR --request command.json
```

El CLI no crea contenedores o intenciones, ni selecciona una referencia. Primero
se usan los pasos I4/I8 de registro, ingesta de una observación real, selección de
referencia con CAS y registro de intención. No se ingiere una captura vacía para
simular ADDED. El helper Python `BootstrapClient.prepare_request` construye el
comando cerrado y los bytes de fila desde una observación verificada:

```python
from source_ingest.bootstrap import BootstrapClient

client = BootstrapClient(container, 'd5_writer')
request, rowbytes = client.prepare_request(
    command_id, project_id, document_id, intent_id,
    observation_id, source_key, expected_reference_version,
)
proposal = client.submit_bootstrap(request, rowbytes)
```

Los nombres anteriores son variables que debe aportar el operador; el adaptador
no genera identidades ni elige la observación más reciente. `submit_bootstrap`
reconstruye de nuevo el snapshot. El CLI reconstruye los bytes de fila al recibir
el comando; no admite una fila suministrada que difiera de la almacenada.

`BootstrapClient.artifact(project_id, document_id, 'proposal', proposal_id)` y la
variante `'package', package_sha256` permiten inspeccionar artefactos completos.
`verify_manifest` comprueba su fila, proyección y base contra la reconstrucción de
bytes. La revisión permite consultar la fuente completa mediante las lecturas I4/I5.
Los recibos se recuperan con `read_command`; son históricos, no estado actual.
Los archivos de comandos y exportaciones son privados si contienen datos de fuente.

El CLI devuelve 2 ante conflicto de negocio, 1 ante fallo de verificación/SQL y 0
ante resultado ordinario. Solo acepta contenedores D5 desechables sin red; no es
una conexión a dev/producción ni un nuevo servicio persistente. El runner destruye
su base al terminar; para inspección durante una investigación se usa BootstrapLab
con limpieza en finally.

## Qué se fija y qué se aplica

La observación debe ser la referencia actual del mismo documento/perfil, con su
versión exacta. Un diagnóstico bloqueante invalida el snapshot entero, aunque
la fila problemática no esté seleccionada. Los avisos compatibles se conservan.
Las filas no seleccionadas no requieren correspondencia ni se materializan.

PREPARE exige intención registrada con perfil/política fijos, cabeza v0 con base y
proyección nulas, sin destino o hecho previo de aplicación, y UUID/clave ausentes.
Una ausencia anterior con cabeza avanzada no vuelve a cero. Una fila debe existir
exactamente una vez; su título no puede ser vacío o solo blancos. El perfil se
reconstruye con los parsers existentes, conservando Unicode/Markdown/pipes literales,
tachado y anotaciones, sin interpretar Status o Verified como workflow.

El manifiesto propio `d5.bootstrap-task-manifest.v1` fija observación, revisión,
hashes de contenido/preview/fila, fila completa, intención/destino, referencia y
versión, proyección, base semántica, ausencia esperada y metadatos de preparación.
El modo es BOOTSTRAP_INITIAL y la acción CREATE_INITIAL_BACKLOG. No contiene
comparación, fila antes o decisión I5 inventadas. El snapshot completo se recupera
por sus hashes; no se duplica la fuente entera en cada manifiesto.

APPLY reutiliza el helper privilegiado I8: d3.lock_state, 742001 → 742002 →
relaciones vigentes → 742005 y correspondencias ordenadas, en READ COMMITTED.
Comprueba todas las filas antes de mutar la primera. Bajo locks exige referencia,
intención inicial, revisión ACCEPT vigente y ausencia de destino por UUID/clave.

Cada efecto confirma atómicamente tarea BACKLOG v0 con defaults I8, destino con FK,
task_sources de esa revisión/localizador, cabeza compartida inicializada a v1,
auditoría D5_TASK_IMPORT, hecho de aplicación fechado en D5 y recibo. Ningún paso
selecciona otra referencia, mueve el puntero público o genera STATE_CHANGED/outbox,
operaciones, entregas, reservas o planes. `task_eligible=true` no activa trabajo.

Un conflicto deja recibo sin efectos parciales. Un error estructural revierte todo.
Replay exacto devuelve el recibo histórico; otro command_id del mismo paquete ya
aplicado obtiene ALREADY_APPLIED. Otro paquete sobre esa intención avanzada falla.
Los command_id siguen siendo globales D5 incluso entre bootstrap y comparación.

## Continuidad, permisos y conservación

La base semántica inicial usa las reglas y el dominio I8. Después pueden ejecutarse
comparación y ACCEPT I5, preparación/revisión I8 y PATCH, enlace de evidencia o
reconocimiento de ausencia sobre la misma tarea. Siguen vigentes los conflictos
por edición local, base de origen distinta, CAS del destino y referencia/versión.
La carrera bootstrap/CREATE I8 se resuelve por la cabeza compartida, sin doble tarea.

Los callers existentes reciben solo los nuevos entrypoints pertinentes: writer
prepara/empaqueta, reviewer revisa, reader lee y applier aplica. No obtienen DML
directo ni autoridad D3/D4. El propietario NOLOGIN separado conserva la autoridad
mínima de aplicación I8 y añade lectura de previews para verificar la fila SQL;
el helper fijo sigue siendo del administrador. No se modifica ninguna función I8.
Las etiquetas de revisión siguen siendo afirmaciones sintéticas, no autenticación.

CREATE cambia el readset y digest D3: se detecta la obsolescencia de la base previa
y se conservan los snapshots publicados de fixture. La evidencia comprueba las
funciones previas D5 y el catálogo public/D2/D3/D4, además de los hashes históricos.

Bootstrap inicial queda acotado a este laboratorio. Siguen pendientes reaparición,
adopción, resolución de edición local, cambios de perfil/política, múltiples
orígenes y formato Gentle-AI/routing completo. D5 no se cierra; D6 no se amplía.
Proveedores/credenciales reales, promoción, despliegue y activación permanecen fuera.
