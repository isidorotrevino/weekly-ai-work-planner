# D5 I20 — laboratorio de resolución local aislada

Fecha: 2026-10-22. Implementa el [contrato I19](D5-I19-ISOLATED-LOCAL-EDIT-DESIGN.md)
y su [matriz IL01–IL36](D5-I19-ISOLATED-LOCAL-EDIT-REVIEW.md).
[Evidencia propia](../validation/D5-I20-results.md).
D5 abierto; D1–D4 cerrados y D6 pendiente.

English: a separate disposable PostgreSQL lab for reviewed isolated local edits.
The selected source row must match the entire applied source basis. Resolve the
whole source/local pair, preserve that basis and advance one mapping version;
no fabricated comparison, activation, promotion or deployment.

## Autorización y ejecución

D5-A49: el usuario aprueba I19 y autoriza implementar/validar IL01–IL36 en otro
laboratorio V30 desechable con fixtures BACKLOG sintéticas. Conserva A45–A48:
snapshot presente seleccionado, igualdad semántica íntegra, versión nueva con base
intacta y bloqueo si el efecto exacto vigente es ausencia aplicada.

V39 permanece en `migrations-d5-proposed/`, sin promoción. El runner nuevo aplica
V1–V30 y V31–V39 sobre base nueva. Preserva funciones, cuerpos/propietarios/ACL/config
y archivos anteriores; no modifica parsers/perfiles ni el catálogo de funciones y
triggers public/D2/D3/D4. No inicia workers ni modifica dev/D4.

```bash
python3 -m testing.D5.run_isolated_local_edit_lab
```

Linux, Python 3, Docker y `postgres:16-bookworm` ya disponible; el runner no descarga
imágenes. Contenedor etiquetado D5, sin red ni puertos, volumen anónimo propio;
finally elimina solo esos recursos incluso ante fallo. Salida 0 solo si pasa la
campaña. Brutos privados en
`work/d5/postgres/d5-pg-*/isolated-local-edit-results.json`; no publicar logs o corpus.

## Fuente, tarea y prueba histórica

Intención propia materializada con identidad exacta de proyecto/documento/ID,
perfil/política, UUID/task_key. BACKLOG sin operaciones ni planificación, incluso
histórica/cancelada. Mantiene task_sources previos; no crea, adopta o transfiere
tarea. B es proyección de origen aplicada, L texto local actual y S proyección del
snapshot seleccionado: exige L distinto de B y S=B.

El snapshot debe ser la referencia local exacta/versionada, tener fila única
presente sin diagnósticos bloqueantes y coincidir con toda source_basis: fields,
source_struck y annotation_text. Igual Item/Objective no basta. Cambios de bytes o
posición son admisibles si la semántica íntegra coincide; se fija procedencia real.
La selección no prueba ser el contenido externo más reciente ni el de mayor fecha.
No crea comparación, review_item, row_decision o ACCEPT I5.

La igualdad de base no acredita presencia: una ausencia I8 conserva esa base.
`read_isolated_local_head_proof(pid, doc, intent, application, proposal)` recupera
una prueba histórica por IDs explícitos. Solo reconoce tablas y acciones fijas de
I8/I10/I12/I14/I16/I18/esta variante. Valida ámbito/intención, hashes de manifiesto
y paquete, recibos de preparación y aplicación OK, efecto de tarea y pin histórico
ACCEPT. Produce versión confirmada y evidencia de presencia/base. No se basa en
fechas, audit_events sueltos o un campo de presencia proporcionado por caller.
Su SQL dinámico usa únicamente ese catálogo fijo, sin identificadores del llamante.

I16 produce v1 sin inventar una cabeza previa v0. Las demás versiones proceden
del mapping_version real del manifiesto +1. La prueba puede leerse después de
avanzar cabeza para recuperar recibos históricos; preparar/aplicar exigen que la
versión producida sea exactamente la cabeza vigente y que base/proyección coincidan.
Una prueba antigua no gana por conservar B. Ausencia vigente bloquea ambas elecciones,
aunque se seleccione una observación presente anterior: I12/I18 conservan la
reaparición, sin reversionar o consumir su prueba de ausencia.

El adaptador reconstruye fuente actual e histórica con los verificadores existentes.
Las resoluciones aisladas sucesivas se verifican mediante una cadena iterativa,
con detección de ciclos, sin recurrencia de llamadas Python entre esas resoluciones.
No se modifican recibos antiguos. Revocar después una revisión histórica no deshace
su efecto confirmado; la nueva resolución exige su propia revisión vigente.

## Comandos y revisión

```bash
python3 -m source_ingest.isolated_local_edit --container d5-pg-IDENTIFICADOR --request command.json
```

Solo contenedores D5 desechables etiquetados sin red, no dev/producción. JSON cerrado,
máximo 4 MiB, duplicados rechazados. Campos comunes: schema `d5.source-command.v1`,
command_id UUID, action, project_id y document_id. Roles writer/reviewer/applier/reader.

| action | Campos adicionales |
|---|---|
| PREPARE_ISOLATED_LOCAL_EDIT_TASK | intent_id, source_key, observation_id, content_sha256, preview_sha256, snapshot_row_sha256, expected_reference_version, expected_mapping_version, head_application_command_id, head_proposal_id, choice, reason |
| REVIEW_ISOLATED_LOCAL_EDIT_TASK | proposal_id, manifest_sha256, expected_version, decision, reviewer_label, reason |
| PACKAGE_ISOLATED_LOCAL_EDIT_TASKS | items: lista ordenada de proposal_id, manifest_sha256, review_command_id y review_version |
| APPLY_ISOLATED_LOCAL_EDIT_TASKS | package_sha256 |

`IsolatedLocalEditClient.prepare_request` deriva request y bytes canónicos de la fila
para revisar; CLI reconstruye y compara los hashes explícitos. Vuelve a verificar
fuente/manifiesto/prueba antes de revisar, empaquetar y aplicar. SQL privilegiado
solo no acredita parsing ni identidad autenticada D6.

Manifiesto propio completo: prueba, base/digest, B/L/S, snapshot íntegro de tarea
UTC y digest `d5.task-target.v1`, elección, razón y resultado. Razón de 1–1.024
caracteres, sin controles ni solo blancos Unicode. USE_SOURCE/KEEP_LOCAL completos;
sin texto manual, máscara o force. ACCEPT/REJECT propios revisan todo el conjunto,
sin reutilizar aprobaciones anteriores o fabricar I5. Etiquetas/razones sintéticas.

Paquetes explícitos ordenados de 1–2.000, una propuesta por intención y una misma
observación/perfil; sin mezcla con otras variantes o elección por fecha. Cambiar
snapshot, fuente, prueba, elección o razón exige nueva preparación/revisión;
revocar/reaceptar invalida pins anteriores. `artifact(pid, doc, 'proposal', UUID)` y
`'package', hash` recuperan el ámbito, `read_command` los recibos. CLI devuelve 2
ante CONFLICT, 1 ante fallo y 0 ordinario/replay.

## Efecto y continuidad

| Elección | Tarea | Cabeza D5 |
|---|---|---|
| USE_SOURCE | PATCH_ISOLATED_LOCAL_USE_SOURCE: title/description completos a B=S y row_version +1 | Versión +1, base/digest/projection intactos |
| KEEP_LOCAL | KEEP_ISOLATED_LOCAL: fila íntegra sin UPDATE ni incremento de row_version | Versión +1, base/digest/projection intactos |

No hay rama USE_SOURCE sin cambios: L distinto de B=S es requisito; convergencia
tras preparar bloquea la propuesta. Descripción local NULL puede conservarse y
Objective vacío/guion es literal. Fuente inválida bloquea incluso KEEP_LOCAL.
No se normaliza Unicode, renderiza Markdown o infiere workflow de Status/Verified.

Procedencia seleccionada exacta append-only/reutilizada, hecho/recibo inmutables con
versión antes/después, resultado, elección/razón y prueba, y auditoría D5_TASK_IMPORT
se confirman juntos. No guarda texto local como origen ni crea una revisión de
origen desde esa edición. Fecha en D5, sin tasks.updated_at ni cambios de otros
campos de tarea. Ninguna tarea nueva, activación, puntero/referencia/cursor avanzado,
STATE_CHANGED u outbox. writes_task distingue texto de escrituras de evidencia D2.

READ COMMITTED y frontera fija: 742001 → 742002 → relaciones D3 → mutex 742005 →
intenciones/cabezas ordenadas. Se valida todo el paquete antes de efectos y de nuevo
tras esperar; CAS completo detecta cambios sin row_version y ABA observable.
Conflicto sin efectos parciales; aborto/error revierte también éxito. Replay global
histórico, contenido distinto en conflicto y ALREADY_APPLIED no restauran estado.
No se promete detectar restauración externa de todos los valores sin huella.

KEEP_LOCAL invalida paquetes sobre cabeza anterior aunque no cambie tarea ni base;
no rebasa paquetes ni concede override permanente. Puede revisarse otra resolución
con prueba de cabeza nueva; ante cambio real posterior, I14 sigue requerido si
persiste divergencia. USE_SOURCE permite continuidad I8; ausencia/reaparición futura
conserva I8/I12/I18 y nueva prueba de ausencia aplicada/versionada. PATCH cambia digest
de tarea D3, sin alterar planes publicados o prometer invariancia global del readset.

D5 sigue abierto: IDs reutilizados/transferencias, adopción con trabajo/procedencia
previos, perfil/política, múltiples orígenes y Gentle-AI/routing completo conservan
pendientes. Sin proveedores/credenciales reales, promoción, despliegue o ampliación D6.
