# D5 I12 — laboratorio de reaparición revisada

Fecha: 2026-10-21. Implementa el [contrato I11](D5-I11-REAPPEARANCE-DESIGN.md)
y su [matriz R01–R30](D5-I11-REAPPEARANCE-REVIEW.md).
[Evidencia de esta campaña](../validation/D5-I12-results.md).
D5 abierto; D1–D4 cerrados y D6 pendiente.

## Autorización y alcance

D5-A29: el usuario aprueba I11 y autoriza implementar/validar R01–R30 en otro
laboratorio V30 desechable con fixtures BACKLOG sintéticas, sin activación,
promoción ni despliegue. Conserva A25–A28: declaración de misma entidad con razón,
PATCH/enlace bajo guards, ausencia I8 aplicada/versionada y posibilidad de otro
«antes» ausente reconstruido, fijando ambas observaciones.

La propuesta V35 es aditiva en `migrations-d5-proposed/`. Usa artefactos y entradas
propios, con cabeza/destino compartidos I8/I10. No modifica V1–V34, parsers,
perfiles, funciones, adaptadores o runners anteriores. I8 sigue devolviendo
REAPPEARANCE_REVIEW_REQUIRED y bootstrap exige intención inicial sin destino.

## Ejecutar la campaña nueva

Con Linux, Python 3 estándar, Docker e imagen local `postgres:16-bookworm`:

```bash
python3 -m testing.D5.run_reappearance_lab
```

Arranca una base V1–V30 seguida de V31–V35, sin red ni puertos publicados, con
contenedor D5 etiquetado y volumen anónimo propios. Se eliminan en finally, también
ante fallo. El resumen y diagnósticos privados quedan en
`work/d5/postgres/d5-pg-*/reappearance-results.json`. Retorno 0 significa PASS.
No inicia Compose dev/D4, workers, heartbeat, transporte o ejecución.

La campaña reúne I4 (21), I5 (15), I6 (5), I8 (27), I10 (28) y R01–R30 (30).
Los métodos `test_RP01`–`test_RP30` corresponden a R01–R30; el prefijo RP evita
confundirlos con los casos de revisión I5 heredados. Fixtures negativas de estado,
operación y planificación se revierten, nunca ejecutan trabajo. La autorización A18
se conserva para la operación negativa. Los planes publicados son fixtures del
propietario sin d3.publish, outbox o despliegue.

## Flujo explícito y comandos

Primero debe existir la tarea propia creada por I8 o I10 y un recibo I8 de
KEEP_EXISTING_NO_DELETE aplicado a esa correspondencia materializada. Se prepara
una comparación real I5 entre un «antes» sin ese ID y un «después» con su fila,
seleccionando la referencia explícita «antes» con CAS y aceptando la fila I5.
No se crea una captura vacía, otra tarea o una nueva intención para el mismo ID.

El adaptador nuevo `source_ingest/reappearance.py` recibe archivos JSON cerrados
con schema `d5.source-command.v1`, command_id, action, project_id y document_id,
más los siguientes campos. Todas las identidades, hashes y versiones son explícitos.

| action | Campos adicionales |
|---|---|
| PREPARE_REAPPEARANCE_TASK | intent_id, comparison_id, report_sha256, row_sha256, expected_reference_version, expected_mapping_version, absence_application_command_id, absence_proposal_id, identity_declaration, identity_reason |
| REVIEW_REAPPEARANCE_TASK | proposal_id, manifest_sha256, expected_version, decision, reviewer_label, reason |
| PACKAGE_REAPPEARANCE_TASKS | items: lista explícita ordenada por proposal_id |
| APPLY_REAPPEARANCE_TASKS | package_sha256 |

`identity_declaration` debe ser SAME_SOURCE_ENTITY, con razón no vacía/solo blancos,
acotada y sin controles. No es una atestación externa: quien revisa acepta esa
afirmación junto con toda la fuente, prueba, destino y efecto. Un ID reutilizado
para otra entidad o no confirmado se bloquea, sin liberar identidad ni adoptarla.

Cada pin de paquete contiene proposal_id, manifest_sha256, review_command_id y
review_version. Se admiten 1–2.000 manifiestos de intenciones distintas, sin mezclar
variantes I8/bootstrap, y se mantienen los límites de bytes existentes aplicables.
Una revisión I5 no sustituye la propia del manifiesto de reaparición.

```bash
python3 -m source_ingest.reappearance --container d5-pg-IDENTIFICADOR --request command.json
```

El CLI elige solo el rol sintético correspondiente al tipo de comando. Rechaza
claves JSON repetidas, tipos/formatos inválidos y contenedores sin la etiqueta D5
desechable o con red. Devuelve 2 ante conflicto de negocio, 1 ante fallo de
verificación/SQL y 0 ante resultado ordinario. No es un servicio persistente ni
una conexión a dev/producción; el runner destruye su base al terminar.

`ReappearanceClient.absence(project_id, document_id, application_id, proposal_id)`
exporta y verifica la prueba explícita de ausencia. `artifact(..., 'proposal', id)`
y `artifact(..., 'package', hash)` permiten inspeccionar el contenido completo.
`submit_reappearance(request)` reconstruye las fuentes antes de enviar SQL.
Los recibos globales se consultan con read_command; representan resultados históricos,
no el estado actual. Mantener privados los comandos/exportaciones con datos fuente.

## Prueba de ausencia y base aplicada

La lectura SQL enlaza commands, task_applications, paquete, propuesta, revisión
histórica ACCEPT y efecto KEEP_EXISTING_NO_DELETE confirmado. Comprueba ámbito,
UUID, intención, hash de manifiesto y fila presente/ausente de aquella comparación.
Un CONFLICT, simulación, aceptación sin aplicación, recibo de otra tarea o paquete
sin ese efecto no acreditan ausencia. El verificador Python reconstruye también
esa comparación histórica desde sus snapshots y previews, además de la actual.

El manifiesto fija la prueba completa y la versión `mapping_version + 1` producida
por aquella ausencia. Debe coincidir exactamente con la cabeza vigente y la versión
esperada del preparador. No se busca por fecha, máximo ID o última lectura. Otra
aplicación o ciclo requiere otra prueba/version; ALREADY_APPLIED no avanza cabeza.

La base/proyección se toman de la cabeza realmente aplicada y se fijan con sus
hashes. No se confunden con before_basis de la comparación histórica de ausencia,
que I8 no exige igual a la base aplicada para KEEP_EXISTING. Se contrasta la
proyección conservada y la versión, sin sustituir el estado por una fila histórica.

El «antes» actual puede ser otra observación ausente del mismo ámbito/perfil.
La reconstrucción confirma ausencia del mismo ID y falta de diagnósticos bloqueantes;
el manifiesto fija ambas observaciones, su prueba y la comparación actual. El
ACCEPT I5 y la referencia/version corresponden a esta última, sin retroceder la
referencia o convertir ausencia en equivalencia por fecha/hash solamente.

Una revocación posterior de la revisión de la ausencia no deshace el hecho
confirmado. La prueba conserva sus pins históricos; las revisiones I5 de reaparición
y la propia del nuevo manifiesto sí deben seguir vigentes en APPLY.

## Aplicación, continuidad y límites

El manifiesto `d5.reappearance-task-manifest.v1` fija intención, cabeza/base aplicada,
comparación/fila, ACCEPT I5, referencia/version, prueba de ausencia, declaración/razón,
snapshot completo del destino en UTC con digest I8 y acción/proyección/base nuevas.
El paquete usa dominio `d5.reappearance-task-package.v1`. Ambos son inmutables.

APPLY usa el helper fijo de administrador y READ COMMITTED: 742001 → 742002 →
relaciones D3 vigentes → mutex D5 742005 → cabezas ordenadas. Verifica todo el
paquete antes de mutar. La tarea debe mantener UUID/proyecto/task_key de la intención,
ser BACKLOG sin ninguna operación/entrada de planificación, incluso histórica,
y coincidir en title/description con la última proyección aplicada. Una edición
local bloquea incluso si ocurrió durante la ausencia, sin aumento de row_version,
o antes de preparar de nuevo. Otros campos locales se conservan y el CAS completo
protege cualquier cambio posterior. No hay force, mezcla o reactivación.

PATCH_REAPPEARED_BACKLOG modifica solo title/description y aumenta row_version una
vez. LINK_REAPPEARANCE_EVIDENCE no reescribe la tarea. Los textos se conservan
literales y Status/Verified/tachado/anotaciones no alteran workflow. Ambas acciones
añaden/reutilizan procedencia exacta «después», avanzan la cabeza con la nueva base,
y confirman hecho/auditoría/recibo fechados en D5. No se crea otra tarea ni se añade
updated_at a D2; tampoco se modifica procedencia anterior, referencia, puntero o cursor.

Un conflicto confirma recibo sin aplicar parcialmente; un fallo estructural
revierte todos los efectos. command_id sigue siendo global D5. Replay devuelve el
recibo histórico; otro comando del mismo paquete aplicado solo ALREADY_APPLIED,
sin restaurar tarea/cabeza. Otro paquete sobre la cabeza obsoleta entra en conflicto.
Después se puede continuar por I5/I8 con la nueva base y otro ciclo de ausencia.

Los roles existentes reciben solo las entradas nuevas pertinentes; no DML directo
ni autoridad general D3/D4. Se conserva propietario NOLOGIN separado y helper de
administrador. Se comparan cuerpos/propietarios/ACL/config de funciones D5 previas y
catálogo public/D2/D3/D4, sin reescribir entradas selladas. PATCH cambia el digest
D3 y vuelve obsoleta una captura anterior, preservando snapshots publicados.
`task_eligible=true` en BACKLOG no activa trabajo.

Sigue siendo un laboratorio sintético y la semántica del parser depende del
adaptador confiable. D5 permanece abierto: adopción, reutilización de ID para otra
entidad, resolución local, cambio de perfil/política, múltiples orígenes y formato
Gentle-AI/routing completo conservan sus pendientes. D6 y proveedores/credenciales
reales, activación, promoción y despliegue permanecen fuera.
