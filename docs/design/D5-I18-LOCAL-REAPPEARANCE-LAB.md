# D5 I18 — laboratorio de resolución local de reaparición

Fecha: 2026-10-22. Implementa el [contrato I17](D5-I17-LOCAL-REAPPEARANCE-DESIGN.md)
y su [matriz LR01–LR36](D5-I17-LOCAL-REAPPEARANCE-REVIEW.md).
[Evidencia propia](../validation/D5-I18-results.md).
D5 abierto; D1–D4 cerrados y D6 pendiente.

English: a separate disposable PostgreSQL lab for jointly reviewed identity and
source/local text resolution when a source ID reappears. Confirmed I8 absence,
current task snapshot and source review remain mandatory. No activation,
promotion or deployment.

## Autorización y alcance

D5-A44: el usuario aprueba I17 y autoriza implementar/validar LR01–LR36 en otro
laboratorio V30 desechable con fixtures BACKLOG sintéticas. Conserva A42/A43:
cualquier divergencia actual al preparar, snapshot local completo y revisión
conjunta de prueba, identidad y elección/razón; ACCEPT I5 separado.

V38 queda en `migrations-d5-proposed/`, sin promoción. El runner nuevo aplica
V1–V30 y V31–V38 en una base nueva, preservando funciones, cuerpos/ACL/config,
funciones/triggers public/D2/D3/D4 y archivos anteriores. No inicia workers ni modifica dev/D4.

```bash
python3 -m testing.D5.run_local_reappearance_lab
```

Requiere Linux, Python 3, Docker y `postgres:16-bookworm` ya disponible. No descarga
imágenes. Contenedor D5 etiquetado, sin red ni puertos publicados, con volumen
anónimo propio; cleanup en finally elimina solo esos recursos incluso ante fallo.
Salida 0 únicamente si pasa la campaña. Logs y recibos brutos privados en
`work/d5/postgres/d5-pg-*/local-reappearance-results.json`.

## Fuente, identidad y texto

La tarea propia materializada puede proceder de I8/I10/I16 y efectos I12/I14.
UUID/clave/proyecto/documento/ID/perfil/política siguen fijos. BACKLOG y ninguna
operación o planificación, incluso histórica/cancelada. Se conservan vínculos
previos; no se exige task_sources vacío ni se adopta una tarea nueva.

B es la última proyección del origen en cabeza D5; L es title/description del
snapshot actual completo de la tarea; S es Item/Objective literal de la fila ADDED
reconstruida. Se exige L distinto de B. Si coinciden se usa I12 ordinario. La
variante admite divergencia anterior, durante o después de la ausencia, pero una
edición posterior a preparar exige nueva preparación/revisión.

La prueba histórica se obtiene con el lector I12 sin modificarlo: ausencia I8
KEEP_EXISTING_NO_DELETE realmente aplicada con recibo OK, cadena y revisión
histórica completas, versión producida igual a cabeza vigente. El target histórico
se conserva, aunque difiera de L. B y base semántica vienen de cabeza; no se
inventan desde before_basis histórico de la ausencia.

La comparación actual es PREVIEW_ONLY, ADDED ausente→presente, sin bloqueos en
ningún snapshot y con ACCEPT I5 vigente. Referencia exactamente al «antes» actual
y versión esperada. Puede diferir del snapshot ausente histórico, pero se
reconstruyen y fijan ambos. SAME_SOURCE_ENTITY con razón es obligatorio para ambas
elecciones; ID reutilizado para otra entidad queda bloqueado.

Título local/origen válido; descripción del origen string, descripción local SQL
NULL permitida. Se conserva Unicode/Markdown/pipes literalmente. Status, Verified,
tachados, bloqueos y anotaciones son evidencia; no activan tareas o dependencias.

## Comandos y revisión

```bash
python3 -m source_ingest.local_reappearance --container d5-pg-IDENTIFICADOR --request command.json
```

Solo contenedores desechables D5 etiquetados sin red; nunca dev/producción. Archivo
JSON cerrado, máximo 4 MiB, claves duplicadas rechazadas. Campos comunes: schema
`d5.source-command.v1`, command_id UUID, action, project_id y document_id.

| action | Campos adicionales |
|---|---|
| PREPARE_LOCAL_REAPPEARANCE_TASK | intent_id, comparison_id, report_sha256, row_sha256, expected_reference_version, expected_mapping_version, absence_application_command_id, absence_proposal_id, identity_declaration, identity_reason, choice, reason |
| REVIEW_LOCAL_REAPPEARANCE_TASK | proposal_id, manifest_sha256, expected_version, decision, reviewer_label, reason |
| PACKAGE_LOCAL_REAPPEARANCE_TASKS | items: pins explícitos ordenados de proposal_id, manifest_sha256, review_command_id, review_version |
| APPLY_LOCAL_REAPPEARANCE_TASKS | package_sha256 |

Roles writer/reviewer/applier/reader separados. Preparar no escribe tarea/cabeza.
Razón de identidad y resolución separadas, 1–1.024 caracteres, sin controles ni
solo blancos Unicode. El manifiesto propio muestra prueba completa, declaración,
B/L/S, snapshot/digest íntegro actual, elección, razones y resultado derivado.
Una sola revisión propia ACCEPT/REJECT abarca el conjunto. ACCEPT I5 sigue siendo
requisito separado; no se reutilizan revisiones I12/I14 ni se mezclan manifiestos.

Paquete de 1–2.000 propuestas ordenadas por proposal_id, una por intención, sin
mezcla con variantes previas. No hay selección implícita por fecha o «todas las
aceptadas». El adaptador reconstruye fuente actual y ausencia histórica antes de
preparar/revisar/empaquetar/aplicar. SQL privilegiado solo no acredita el parser.
`artifact(pid, doc, 'proposal', UUID)` y `'package', hash` recuperan el ámbito;
`read_command` recupera recibos. CLI: 2 ante CONFLICT, 1 ante fallo, 0 ordinario.

## Efecto, concurrencia y recuperación

| Elección | Condición | Efecto sobre la tarea |
|---|---|---|
| USE_SOURCE | S distinto de L | PATCH_LOCAL_REAPPEARANCE_USE_SOURCE: title/description a S y row_version +1 |
| USE_SOURCE | S igual a L | LINK_LOCAL_REAPPEARANCE_EVIDENCE: ningún UPDATE |
| KEEP_LOCAL | Cualquier S, L distinto de B | KEEP_LOCAL_REAPPEARANCE: fila íntegra sin UPDATE |

En los tres casos cabeza +1 con base reaparecida y projection=S; el resultado
local se guarda por separado. Procedencia después exacta append-only o reutilizada,
hecho/recibo inmutables con identidad/razones/prueba, fecha en D5 y auditoría
D5_TASK_IMPORT. No añadir tasks.updated_at ni cambiar otros campos locales;
ninguna tarea nueva, activación, referencia/puntero/cursor avanzado o outbox.

APPLY exige READ COMMITTED y frontera heredada fija: 742001 → 742002 → relaciones
D3 → mutex 742005 → intenciones/cabezas en orden. La frontera D3 protege las tareas
y el trabajo mientras se valida el paquete completo antes del primer efecto.
CAS íntegro bloquea cambios tras preparar incluso sin row_version; versiones de
cabeza, referencia y revisiones detectan ABA observable. No se promete detectar
restauraciones externas de todos los valores sin ninguna huella.

Conflicto de negocio no deja efectos parciales. Aborto/error revierte tarea,
procedencia, cabeza, hecho/auditoría y recibo de éxito. command_id global: replay
histórico; otro contenido, conflicto; mismo paquete con comando nuevo,
ALREADY_APPLIED sin restaurar estado posterior. Paquetes competidores tienen un
ganador y conflicto del otro. Recuperación tras respuesta perdida y reinicio.

USE_SOURCE/convergencia permiten continuidad I8 sobre base nueva. KEEP_LOCAL
divergente exige nueva resolución I14 ante siguiente cambio presente, sin excepción
permanente. Otro ciclo requiere otra ausencia aplicada/versionada y nueva revisión.
I12 sigue rechazando divergencia; I14 sigue limitado a CHANGED presente→presente.

## Límites

Etiquetas/razones son afirmaciones sintéticas, sin autenticación D6. No se declara
cierre D5, escalabilidad o autorización frente a DDL arbitrario del administrador.
D5 mantiene pendientes resolución local aislada sin cambio revisable del origen,
IDs reutilizados/transferencias, adopción con trabajo o procedencia previa,
perfil/política, múltiples orígenes y Gentle-AI/routing completo. Sin proveedores o
credenciales reales, promoción, despliegue ni ampliación D6.
