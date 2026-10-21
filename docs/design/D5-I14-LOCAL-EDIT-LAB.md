# D5 I14 — laboratorio de resolución de ediciones locales

Fecha: 2026-10-21. Implementa el [contrato I13](D5-I13-LOCAL-EDIT-DESIGN.md)
y su [matriz L01–L32](D5-I13-LOCAL-EDIT-REVIEW.md).
[Evidencia propia](../validation/D5-I14-results.md).
D5 abierto; D1–D4 cerrados y D6 pendiente.

English: a separate synthetic PostgreSQL lab for reviewed whole source/local
projection choices. Existing tasks only; no permanent override, activation or
migration promotion. Prior labs and their evidence remain unchanged.

## Autorización y separación

D5-A34: el usuario aprueba el contrato I13 y autoriza implementar/validar L01–L32
en otro laboratorio V30 desechable con fixtures BACKLOG sintéticas, sin activación,
promoción ni despliegue. A31–A33 se mantienen: origen o local completos, cambios
presentes solamente, sin excepción permanente para importaciones posteriores.

La propuesta V36 vive en `migrations-d5-proposed/`. Se aplica exclusivamente desde
el runner nuevo, después de V1–V30 y V31–V35, en base recién creada. No modifica
funciones anteriores, parsers/perfiles, contratos D2, campañas
selladas, manifiestos o evidencias anteriores. No crea roles nuevos ni amplía
permisos sobre objetos anteriores. No entra en Compose dev ni D4.

```bash
python3 -m testing.D5.run_local_edit_lab
```

Requiere Docker local con `postgres:16-bookworm` ya disponible, Linux y Python 3.
Contenedor etiquetado D5, sin red ni puertos, volumen anónimo propio. No hay
proveedores, credenciales reales, workers, heartbeat ni ejecución. El runner
elimina solo su contenedor/volumen en finally, también ante fallo; retorna 0
únicamente si la campaña pasa. Evidencia privada en
`work/d5/postgres/d5-pg-*/local-edit-results.json`; no publicar logs privados.

## Preparación y revisión

Se exige tarea materializada de la misma intención/UUID/clave/proyecto, BACKLOG,
sin operaciones ni planificación, incluso históricas. La fila debe ser CHANGED,
antes y después presentes, bajo comparación I5 PREVIEW_ONLY reconstruida y sin
bloqueos. Su base antes coincide semánticamente con la última cabeza aplicada.
Se fijan ACCEPT I5 y referencia antes/version, sin seleccionarlos por fecha.
Reaparición, ausencia, UNCHANGED sin fila revisable y tareas no materializadas
quedan fuera de esta variante.

El manifiesto muestra B (proyección de origen registrada), L (texto local actual)
y S (proyección de origen entrante), con bases/hashes, snapshot completo de tarea,
procedencia, versiones, elección y razón. L debe diferir de B; si coincide,
corresponde usar I8 ordinario. No se deduce un merge de cambios disjuntos.

El adaptador es `source_ingest/local_edit.py`:

```bash
python3 -m source_ingest.local_edit --container d5-pg-IDENTIFICADOR --request command.json
```

Solo acepta contenedores D5 desechables etiquetados, sin red; no conecta con dev o
producción. Archivo JSON cerrado, máximo 4 MiB, claves duplicadas rechazadas.
Campos comunes: schema `d5.source-command.v1`, command_id UUID nuevo, action,
project_id y document_id. Cada acción usa el rol sintético dedicado:

| action | Campos adicionales |
|---|---|
| PREPARE_LOCAL_EDIT_TASK | intent_id, comparison_id, report_sha256, row_sha256, expected_reference_version, expected_mapping_version, choice, reason |
| REVIEW_LOCAL_EDIT_TASK | proposal_id, manifest_sha256, expected_version, decision, reviewer_label, reason |
| PACKAGE_LOCAL_EDIT_TASKS | items: lista explícita ordenada de pins de revisión |
| APPLY_LOCAL_EDIT_TASKS | package_sha256 |

choice es USE_SOURCE o KEEP_LOCAL. La razón es explícita, hasta 1.024 caracteres,
sin controles ni solo blancos Unicode. No se aceptan force, texto libre de resultado
ni máscara de campos. El revisor ACCEPT/REJECT revisa el manifiesto completo,
separadamente del ACCEPT I5. Las etiquetas son afirmaciones sintéticas, no D6.

Cada pin contiene proposal_id, manifest_sha256, review_command_id y review_version.
Paquetes de 1–2.000 propuestas, una por intención, ordenadas por proposal_id.
Pueden combinar elecciones de esta variante, nunca propuestas I8/I10/I12. Cambios
de fuente, elección, razón o destino requieren preparar y revisar otra propuesta.

`LocalEditClient.artifact(pid, doc, 'proposal', UUID)` o `'package', hash` permiten
leer los artefactos del ámbito. `verify_manifest` reconstruye los bytes de origen,
comparación, fila y proyecciones; se ejecuta antes de revisión, paquete y aplicación.
Los recibos globales se consultan con `read_command`. El CLI devuelve 2 ante
CONFLICT, 1 ante fallo y 0 para resultado ordinario/replay. No elegir el último
artefacto ni publicar exportaciones con datos privados.

## Resultados y continuidad

| Elección | Resultado |
|---|---|
| USE_SOURCE, S distinto de L | PATCH solo title/description y row_version +1 |
| USE_SOURCE, S igual a L | Confirmar evidencia sin UPDATE tasks |
| KEEP_LOCAL | Conservar la fila completa de tarea sin UPDATE ni incremento de row_version |

El origen exige título válido y descripción string. El título local también debe
ser válido; KEEP_LOCAL conserva una descripción local NULL permitida por D2 sin
convertirla en string vacío. Strings Unicode/Markdown/pipes y Objective vacío/guion
se conservan literalmente. Claims de estado/verificación son evidencia sin efectos
operativos. No se añade tasks.updated_at; fecha de aplicación en D5.

En todos los casos, cabeza +1 con base de origen nueva y `projection=S`. El recibo
inmutable conserva por separado elección, resultado real y proyección de origen;
cada efecto distingue `writes_task`. KEEP_LOCAL puede escribir procedencia D2 sin
escribir tasks, por lo que `writes_d2` no implica UPDATE de tarea.
Los vínculos exactos task_sources se añaden o reutilizan, sin editar los anteriores.
Acreditan procedencia, no igualdad textual. No se mueven referencia ni punteros.

Si KEEP_LOCAL deja L distinto de S, el siguiente cambio sigue bloqueado por I8
existente y requiere otra resolución/ACCEPT/manifiesto. No hay override persistente.
Si L=S o se eligió USE_SOURCE, I8 puede continuar desde la nueva base bajo sus
controles. Edición local posterior vuelve a bloquear. Una ausencia posterior
conserva su semántica; I12 no admite reaparición con divergencia local por haber
existido esta resolución. No sustituye prueba de ausencia ni identidad declarada.

## Transacción y límites

APPLY exige READ COMMITTED y el helper fijo del administrador, orden
742001 → 742002 → relaciones D3 → mutex 742005 → correspondencias ordenadas.
Se comprueba el paquete completo antes de modificar: identidad, versiones/bases,
revisiones, referencia, elección/resultado, snapshot/digest completo, BACKLOG y
trabajo/plan. Una edición sin incremento de row_version también invalida el
snapshot. ABA observable por versión invalida el pin; ABA externo sin ninguna
huella observable no se presenta como detectable.

Una fila inválida deja CONFLICT sin efectos parciales. Error estructural o aborto
revierte tareas, vínculos, cabeza, auditoría y recibo. command_id es global D5;
replay recupera resultado histórico y otro comando del mismo paquete confirmado
solo ALREADY_APPLIED. No restaura texto ni versiones. La misma cabeza serializa
las rutas I8/I10/I12/nueva bajo sus controles existentes.

Roles writer/reviewer/applier/reader separados, propietario NOLOGIN, sin nuevos
grants generales D3/D4 ni DML directo para callers. Los objetos nuevos son D5 y las
funciones anteriores conservan cuerpo, propietario, ACL y configuración. PATCH
cambia el digest D3 y vuelve obsoleta una captura previa; snapshots publicados
permanecen inmutables. BACKLOG eligible no significa activación.

El adaptador sigue siendo confiable para la semántica del parser; SQL privilegiado
no autentica fuentes ni revisores. Las pruebas acotan concurrencia y recuperación,
no escalabilidad o DDL arbitrario de un administrador. D5 sigue abierto: adopción,
IDs reutilizados para otra entidad, resolución local de reaparición, cambios de
perfil/política, múltiples orígenes y Gentle-AI/routing completo conservan pendientes.
Sin proveedores/credenciales reales, activación, promoción, despliegue o D6.
