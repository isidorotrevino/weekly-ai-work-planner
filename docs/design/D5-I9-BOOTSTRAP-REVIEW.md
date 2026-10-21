# D5 I9 — revisión del bootstrap y matriz de aceptación

Fecha: 2026-10-21. **Preparado para revisión; matriz todavía no ejecutada.**
[Contrato propuesto](D5-I9-BOOTSTRAP-DESIGN.md). Base: `81d54db`.
D5 abierto; D1–D4 cerrados y D6 pendiente.

A20 autoriza diseño antes de SQL; A21 selecciona IDs explícitos con intención
registrada, sin destino materializado y versión cero; A22 fija revisión propia del
manifiesto íntegro de bootstrap, sin inventar comparación o ACCEPT I5.

La propuesta conserva la selección explícita de referencia y su versión, los
perfiles/parsers y la proyección I8. Añade una variante de creación inicial desde
una sola observación real. Los nombres de entradas y schemas son propuestos;
no están implementados ni se reserva un número de migración.

## Matriz futura — B01–B28

| Caso | Situación | Resultado exigido |
|---|---|---|
| B01 | Snapshot real, referencia seleccionada y lista explícita con intención válida v0 | Preparar artefactos sin crear tarea; ámbito/perfil/UUID/clave inequívocos |
| B02 | Falta intención, pertenece a otro ámbito/perfil o destino/clave ya ocupados | Conflicto sin adopción o generación implícita de identidad |
| B03 | Intención materializada o versión >0, incluso ausencia previa sin tarea | No bootstrap ni reset para volver a cero |
| B04 | ID largo, Unicode/Markdown/pipe, fila tachada, localizador y anotación | Identidad completa, proyección literal y evidencia íntegra sin ejecutar texto |
| B05 | IDs duplicados, fila ambigua o diagnóstico bloqueante fuera de la selección | Bloquear observación completa; no importar una selección parcial de fuente inválida |
| B06 | Título inválido seleccionado; descripción vacía/guion; avisos compatibles | Título bloquea; descripción literal; avisos conservados sin workflow inferido |
| B07 | Falta ID seleccionado, selección repetida/vacía, límites o pin desconocido | Rechazo sin paquete implícito ni efectos parciales |
| B08 | Otras filas válidas sin intención, no seleccionadas o con título vacío | Solo procesar seleccionadas; no crear/actualizar/borrar ni dar por importado el documento entero |
| B09 | Comparación vacía, UNCHANGED, ACCEPT I5/I8 o manifiesto de otra variante | No sustituyen la revisión propia de bootstrap; no fabricar before/comparison/decisión |
| B10 | Bytes, preview, fila, hash o procedencia inconsistentes; manipulación del artefacto | Adaptador reconstruye y rechaza; SQL valida ámbito/hashes; no éxito reconocido |
| B11 | Manifiesto aceptado, después se cambia snapshot, fila, intención, UUID, clave o política | No modificarlo ni trasladar su aceptación; exigir preparación/revisión nueva |
| B12 | Revisión ausente/REJECT, versión obsoleta o ACCEPT→REJECT→ACCEPT | Paquete/aplicación bloqueados; versión monotónica, no reutilizar pins viejos |
| B13 | Sin referencia, referencia distinta o A→B→A; otra observación con mismos bytes | Exigir identidad de observación y versión exactas; no ganar por fecha ni hash solamente |
| B14 | Lista ordenada de manifiestos aceptados; duplicados, otra intención o mezcla I8 | Fijar paquete/hash exactos, una fila por intención; rechazar duplicados y mezcla de variantes |
| B15 | CREATE inicial con Status=DONE/Verified=approved/anotación afirmativa | Una tarea BACKLOG v0 con defaults I8, sin operaciones/aprobaciones/transiciones inferidas |
| B16 | Procedencia SourceRevision/documento/proyecto/localizador | FK y coherencia exactas; tarea/vínculo/correspondencia/base/auditoría/recibo atómicos |
| B17 | Estado inicial confirmado y comparación real posterior válida I8 | Misma identidad/tarea; base semántica permite PATCH, enlace de evidencia o ausencia sin borrado con revisiones I5/I8 |
| B18 | PATCH I8 posterior con edición local, antes semántico distinto o CAS obsoleto | Conflictos I8 conservados; bootstrap no añade force/merge ni excepciones |
| B19 | Aplicar no cambia referencia D5, puntero público ni cursors/bindings | Conservarlos; inicializar solo cabeza de correspondencia v1 y evidencia pertinente |
| B20 | Replay exacto, command_id global con otro contenido y otro comando del mismo paquete | Recibo histórico, conflicto de contenido o ALREADY_APPLIED; nunca restaurar tareas/heads |
| B21 | Otro paquete sobre intención ya aplicada o nueva fila aparece después de preparar | Conflicto de versión para intención aplicada; ninguna selección implícita de filas nuevas |
| B22 | Dos bootstraps concurrentes y bootstrap frente a CREATE I8 sobre la misma intención | Sesiones reales: un efecto ganador y conflicto/replay del otro; sin doble tarea ni adopción |
| B23 | Clave ocupada entre preparación y commit; paquete con una fila inválida | Cero filas aplicadas del paquete; conservar tarea preexistente y dejar recibo de conflicto |
| B24 | Terminación del backend antes de commit y fallo estructural tras comenzar efectos | Rollback íntegro, incluidos tarea, vínculo, base, auditoría y recibo de éxito |
| B25 | Commit confirmado, respuesta perdida y reinicio | Recuperar recibo original sin duplicación; datos persistidos coherentes |
| B26 | Sesiones cruzadas D3/D5 y roles source/reviewer/reader/applier | Orden 742001→742002→relaciones→742005; helper de administrador, mínimo privilegio y sin DML/autoridad D3/D4 generales |
| B27 | Captura D3 anterior y snapshot publicado de fixture | CREATE vuelve obsoleta la base anterior; no reescribir snapshot publicado ni publicar/despachar |
| B28 | BACKLOG eligible y regresiones anteriores | Cero operaciones/entregas/outbox/reservas nuevas; campañas y manifiestos anteriores intactos |

B22/B26 requieren sesiones simultáneas y observación del estado tras desbloquear.
B24/B25 requieren transacciones reales, aborto y recuperación; no solo mocks.
B17/B18 exigen usar los entrypoints I5/I8 existentes, sin reescribirlos para que
acepten contratos bootstrap. Se propone una campaña nueva con regresiones anteriores
y target V30 propio, no modificar los runners I4–I8 o atribuirles casos nuevos.

## Verificación documental de este corte

Se revisan las observaciones persistidas y su referencia I4, la reconstrucción de
comparaciones I5, el contrato I7, las correspondencias/efectos y la evidencia I8.
Se verifican enlaces locales, formato, publicación y hashes históricos, sin arrancar
servicios ni crear SQL, tareas, operaciones o laboratorio nuevo. Ningún caso B se
declara PASS por esta revisión documental.

Se comprueba la integridad de los cierres D3/D4 y del documento canónico D4, además
de las entradas de ejecución registradas I4/I5/I6/I8. Las pruebas originales no se
repiten porque este corte no cambia código, SQL, harness o documentación consumida
por esas pruebas. Las evidencias anteriores conservan su estado al emitirse.

Resultado documental: 92 enlaces locales válidos y formato correcto; comprobación
de publicación sobre 349 archivos de texto sin patrones configurados detectados.
Coinciden 245 entradas de hash de cierre D3/D4, el documento canónico D4 y las
20/27/47/51 entradas de ejecución registradas en I4/I5/I6/I8. Estas comprobaciones
no validan los casos B01–B28 ni acreditan una implementación del bootstrap.

## Decisión siguiente

Revisar este contrato y, si se aprueba, autorizar por separado implementación y
validación sintética de B01–B28. No asumir autorización por el diseño A20–A22.
La revisión no cierra D5 ni amplía D6. Quedan fuera activación, proveedores y
credenciales reales, promoción y despliegue, además de las extensiones enumeradas
en el contrato. La publicación Git del corte documental se propone sobre su
commit concreto una vez preparado y verificado.
