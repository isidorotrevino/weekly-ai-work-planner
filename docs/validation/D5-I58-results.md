# D5 I58 — corte FN64 de fronteras durables

Fecha: **2026-10-24**, Europe/Madrid. Base local I57 `183d55ab366524dc09655b6e0607aa15ccc6eb23`. **IMPLEMENTATION_VALIDATED_WITH_OPEN_CRITERIA**.
[Laboratorio](../design/D5-I58-FRONTIER-GAPS-LAB.md) · [Contrato aprobado](../design/D5-I57-FINITE-FRONTIERS-DESIGN.md) · [Matriz FL/FN](../design/D5-I57-FINITE-FRONTIERS-REVIEW.md) · [Resultados, deltas y fuentes](D5-I58-results.json) · [Raw FN64](D5-I58-raw.json).

La selección **A** posterior a I57 autorizó implementar FN01–FN64 y siete regresiones separadas, sin cambiar producto, fixtures o hooks. Los flags de preparación de I57 permanecen como historia. Este trabajo es local; no autoriza ni ejecuta push.

## Resultado propio

**64/64 tests PASS:** 52 primeras publicaciones, ocho RESULT de QUERY y cuatro controles. **60 SIGKILL positivos**, una caída objetivo por caso de dominio; los kills negativos de timeout quedan aparte. **64 escenarios**, 108 raíces y 482 hijos registrados; cero raíces/hijos/hilos propios pendientes. Raw de 3150627 bytes; 146 entradas pre/post idénticas; duración 56.194s. La selección previa de ocho métodos no se suma como tests adicionales.

FN01–FN36 ensaya las primeras salidas T IMPORT, SOURCE/EVALUATION/EFFECT/PROJECTION ACCEPT, preparación inicial y BIND; FN41–FN56 la primera selección/BIND/preparación/ACCEPT R desde recibo BATCH. FN37–FN40 y FN57–FN60 ensayan RESULT(query_id no nulo). FN61–FN64 son controles. Los IDs se enlazan a la celda FL y al punto exacto en el JSON; no se adjudica una fase por el total de caídas.

Antes de HEAD, los tres puntos conservan estado/HEAD/recibos alcanzables previos, sin salida inicial o ACCEPT; un huérfano/temporal no se adopta. After_head conserva un recibo nuevo y una salida/revisión1, aunque el hijo muere antes de devolverlo. Las aserciones limitan los cambios a los campos autorizados y el recibo; no hay revisión/fase posterior o send implícito. T verifica bytes/pin/grado de captura I26 real de fixture; R conserva lote, recibo, TASK participante y generaciones propios.

RESULT_QUERY exige un intento emitido y efecto REMOTE real superviviente. El hijo realiza lookup y construye la prueba del comando; READY correlaciona M/send/ticket/qid/stores/cid/request y hash de P, sin P enviada por el padre. Antes de HEAD queda UNKNOWN/ledger1/queries1 con send+query pendientes; tras lectura pasiva, una reconcile explícita concluye /2/2 sin execute/close. After_head queda EFFECT_CONFIRMED/2/1 con recibo y pending vacío; read_command/replay exactos históricos no duplican la observación. Un CLOCK posterior tampoco se rebobina al reproducir el recibo. REMOTE se mantiene idéntico durante consulta y continuación.

Cada caso conserva su identidad desde el estado inicial hasta la reapertura y continuación. Lector independiente de archivos y CLIENT público spawn comprueban por separado HEAD/cadena/recibos/estado, con cero llamadas de transporte durante lectura pasiva. No se deduce recuperación integrada sumando PASS de casos distintos.

## Regresiones separadas

| Campaña | Resultado | Inputs efectivos pre/post | Raw y contexto I58 |
|---|---|---|---|
| Python321 | 321/321 PASS | 79 idénticos | [raw](D5-I58-Python-regression-raw.json) · [contexto](D5-I58-Python-regression-context.json) |
| HC24 | 24/24 PASS | 90 idénticos | [raw](D5-I58-HC-regression-raw.json) · [contexto](D5-I58-HC-regression-context.json) |
| HF40 | 40/40 PASS | 99 idénticos | [raw](D5-I58-HF-regression-raw.json) · [contexto](D5-I58-HF-regression-context.json) |
| IC30 | 30/30 PASS | 108 idénticos | [raw](D5-I58-IC-regression-raw.json) · [contexto](D5-I58-IC-regression-context.json) |
| UQ24 | 24/24 PASS | 119 idénticos | [raw](D5-I58-UQ-regression-raw.json) · [contexto](D5-I58-UQ-regression-context.json) |
| RV20 | 20/20 PASS | 129 idénticos | [raw](D5-I58-RV-regression-raw.json) · [contexto](D5-I58-RV-regression-context.json) |
| NA36 | 36/36 PASS | 138 idénticos | [raw](D5-I58-NA-regression-raw.json) · [contexto](D5-I58-NA-regression-context.json) |

Son siete ejecuciones independientes mediante runners históricos intactos. Python321 realiza el discovery unittest de testing/D5 y añade inventario JSON. NA36 es regresión nativa separada, sin trasladar sus casos a FN o ampliar implícitamente sus fases CORE. Los inventarios efectivos de cada runner se conservan, aunque no incluyan el nuevo directorio FN; el raw FN declara su propio descubrimiento completo. No se suman estas repeticiones como pruebas nuevas o aceptación global.

## Verificación documental y archivos grandes

El validador independiente comprobó las 64 filas, 60 gates positivos, 124 pares de lecturas pasivas, 1.862 punteros raw, 104 anclas de fuente, 22 enlaces, 164 entradas efectivas/documentales y 15 artifacts raw/contexto. Los archivos anteriores permanecen intactos. No se ejecutaron campañas adicionales para esta verificación documental.

El checker estándar conserva avisos >1MB para el raw I55, el raw FN64 I58 y la regresión NA36 I58. Se revisó su contenido íntegro con los mismos patrones y umbral temporal de 12MiB: 666 archivos de texto, sin coincidencias. Los SHA revisados constan en el JSON; no se modificó el checker persistido, no se redujo la evidencia para eludir el umbral y esta revisión no autoriza publicación.

## Deltas y pendientes

El expediente añade evidencia nueva a **60 celdas** seleccionadas de las 140 I57: 40 tenían evidencia de otro estado inicial y 20 carecían de caso correspondiente. Cada delta queda TEST_PASS_PENDING_SUFFICIENCY_REVIEW. I57 permanece intacto; no se promueve automáticamente el inventario a cobertura aceptada.

Las otras 80 celdas conservan su clasificación I57: 41 evidencia acotada, 15 metadata histórica y 24 modos remotos sin etiqueta. Permanecen también los límites de OSError, casos auxiliares y recuperación de fases CORE nativas no evaluadas. No se reconstruyen raws originales I34/I36, no se reetiqueta un modo desde la cantidad de registros y no se ejecuta o amplía el auditor/registro fijo I38.

**UI22.2 continúa PARTIAL y el agregado I56 77/7 se conserva**, pendiente de revisión dirigida de suficiencia de la matriz finita. UI20.3 conserva soporte acotado sólo en el namespace CREATE NATIVE_T/NATIVE_R. H07, D5 global/G01–G07 y los cinco GI siguen abiertos, closure=false; no hay promoción 30/35→35/35. GI06/GI12/GI18/GI24/GI30/GI36/GI42 reales/humanos conservan sus puertas propias.

Sin cambios de producto, Store, fixtures T/R/nativa, schemas, hooks, helpers/tests/runners anteriores, registro I38 o handoff. D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. Sin proveedor/credenciales/corpus real, consumo/reservas, activación, promoción, despliegue, SQL/Java/Docker o D6. Sólo limpieza de raíces creadas por los labs; ninguna inspección/limpieza operativa dev/run_data/D4. Publicado sólo hasta I52; I53–I58 locales, sin push nuevo.
