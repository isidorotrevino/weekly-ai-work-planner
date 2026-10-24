# D5 I56 — revisión dirigida UI20.3/H07 y aplicabilidad I55

Fecha: **2026-10-24**, Europe/Madrid. Base local I55 `675173606c61ccc1f82174e07a1bf15b3f88690e`. **DOCUMENTARY_REVIEW_COMPLETE_WITH_OPEN_CRITERIA**.
[Matriz y ámbito](D5-I56-matrix.md) · [Fuentes, casos y punteros](D5-I56-results.json) · [Integridad](D5-I56-integrity.json) · [Evidencia I55](D5-I55-results.md) · [Contrato aprobado I54](../design/D5-I54-NATIVE-AMBIGUITY-DESIGN.md).

## Dictamen

**UI20.3: PARTIAL → SUPPORTS_BOUNDED, exclusivamente para la extensión sintética CREATE NATIVE_T/NATIVE_R aprobada en I54 e implementada en I55.** H07 obtiene soporte acotado en ese namespace; su cierre global sigue false. La revisión contrasta obligación original UI20/DF26–DF28, contrato, fuente, oráculos y raw por identidad; no deriva el dictamen de NA36 PASS ni de sumar regresiones.

El agregado con la ampliación aprobada resulta **77 partes con soporte acotado y siete parciales**. Sólo se reevalúa UI20.3; las otras **83** se heredan de I53. I53 conserva históricamente su 76/8. Este agregado de evidencia no acepta criterios globales ni cambia 30/35 a 35/35. GI38 sigue PARTIAL por UI22.2, y los cinco GI permanecen globalmente OPEN.

## Motivo y trazabilidad

NA07–NA10 devuelve colecciones válidas persistidas por DECLARE_VIEW, no listas malformadas en proof. Incluye dos IDs distintos y un ID repetido. OBSERVE conserva el envelope completo y el conflicto; NA09/10 recibe después una vista limpia con P exacta y continúa CONFLICT/ledger3/queries2, sin adoptar P ni perder la observación original. Catálogo externo no es una segunda entidad creada por un ticket autorizado.

NA15–NA18 diferencia 429 sintético antes y después del efecto. En AFTER, el mismo caso conserva P y entidad v1 REMOTE mientras CLIENT queda UNKNOWN/2/0 sin pending send. Tras lector independiente y CLIENT spawn pasivo, la consulta explícita confirma la P del mismo ticket en /3/1 sin execute ni mutar entities/tickets. BEFORE sigue UNKNOWN tras vacío. NA19/20 acredita además consulta 429 con P oculta y posterior observación explícita; son status nativos de una fixture, sin HTTP/API real.

NA21/22 conserva UNKNOWN tras CLOCK y rechaza retry, nuevo send y manifiesto revisado distinto del mismo binding. Cada rechazo conserva HEAD, recibos e intentos. T prepara/aplica otro EFFECT compatible; R vuelve a seleccionar TASK desde su recibo exacto. NA23/24 es un control distinto: NO_EFFECT/RATE_LIMIT correlacionado habilita retry expreso sólo tras tick; segundo ticket, dos intentos y un efecto. No se confunde ese ticket nuevo con el ticket inicial de la secuencia ni con retry de UNKNOWN.

NA29–NA32 no se usan como un total de SIGKILL: cada fila liga run/stores/send/ticket/M/cid, READY y oráculos de la misma secuencia. Before_observe conserva QUERY y send pendientes; continuación explícita consulta sin ejecutar. After_head conserva un recibo OBSERVE alcanzable, cuyo request_hash se verifica contra el comando de READY; replay no mueve HEAD. Aportan continuidad acotada, sin certificar todas las fronteras F1–F7 o la supervivencia a pérdida de energía.

## Aplicabilidad y límites

NATIVE_T compone el reducer T, captura I26 y revisiones SOURCE/EVALUATION/EFFECT/PROJECTION. NATIVE_R conserva SOURCE/BATCH, recibo APPLY_BATCH y selección TASK propios. Los recibos core se materializan desde la única cadena exterior, también al preparar proyecciones; no hay un segundo Store CLIENT. OBSERVE nativo es distinto de la observación de elegibilidad T. Esta correspondencia sostiene los recorridos de la extensión aprobada, sin convertir R a I32.

Las APIs **T/R v1** siguen devolviendo prueba única/None y no adquieren colecciones o metadatos 429 por esta revisión. MG01/MG02 reciben REVIEWED_BOUNDED en la extensión nueva; su MODEL_GAP histórico en I49/I50 y en las APIs v1 permanece visible. MG03 selección/adopción humana sigue excluido. Un envelope observado no concede autoridad para elegir una coincidencia.

El registro fijo **I38 no incluye I55/NA36**; conserva sus once entradas históricas. Este expediente añade una tabla documental de aplicabilidad, sin modificar ni ejecutar el auditor o presentar EA36 como auditoría del nuevo namespace. La tabla de aplicabilidad conserva el alcance fijo del registro y enlaza la evidencia nueva por separado. Una futura actualización tendría contrato y matriz propios.

No se atribuye soporte a UPDATE/CLOSE, todas las variantes de frontera, carreras de origen/perfil/política/entrega relacional, HTTP real, host/energía/disco/NFS/Windows. H07 global sigue abierto y la capacidad se etiqueta por namespace. No se inventa selección/adopción como nueva obligación pendiente de UI20.3.

## Verificación documental y continuidad

Se verifican los hashes de I53/I54/I55, los 13 artifacts raw/contexto I55 y las entradas efectivas de sus seis regresiones. NA36/48 subescenarios y seis campañas son **ejecuciones históricas de I55**, no tests nuevos ni reejecutados en I56. La revisión sólo lee JSON, AST, fuentes, hashes y Git: cero imports de producto/harness/auditor, cero discovery o campañas nuevas. Los punteros y comprobaciones semánticas están enumerados en el JSON.

El raw I55 conserva su revisión explícita de archivo grande al SHA registrado; el checker estándar mantiene el aviso >1MB. I56 no reduce el raw ni modifica el checker para ocultarlo. No hay push: `origin/main` local sigue en I52 `ce44158`, y HEAD en I55 antes de este registro; son verificaciones locales, sin nueva lectura de red.

Las siete partes PARTIAL son **UI01.2, UI04.1, UI09.2, UI22.2, UI26.2, UI27.2, UI34.3**. La siguiente brecha de GI38 es CP03/UI22.2: matriz finita F1–F7 por autoridad/operación/punto, distinguiendo evidencia existente y cortes faltantes antes de implementar.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. D5 global/G01–G07 y GI33/GI34/GI38/GI39/GI40 abiertos, closure=false. GI06/GI12/GI18/GI24/GI30/GI36/GI42 reales/humanos siguen pendientes de sus puertas propias; ninguno se traslada a D6. Sin proveedores/credenciales/corpus real, consumo/reservas, activación, promoción, despliegue, SQL/Java/Docker ni D6. Sin inspección/limpieza operativa dev/run_data/D4.
