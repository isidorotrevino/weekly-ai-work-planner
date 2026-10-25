# D5 I61 — evidencia causal de las 39 celdas calificadas

Fecha: **2026-10-25**, Europe/Madrid. Base local I60 `65fa3907abf76561e9ebb0c6acc9d1c448c8b75f`. **IMPLEMENTATION_VALIDATED_WITH_OPEN_CRITERIA**.
[Laboratorio y ajuste aprobado](../design/D5-I61-CAUSAL-CELLS-LAB.md) · [Contrato I60](../design/D5-I60-CAUSAL-CELLS-DESIGN.md) · [Matriz CE43](../design/D5-I60-CAUSAL-CELLS-REVIEW.md) · [Resultados y deltas](D5-I61-results.json) · [Raw CE43](D5-I61-raw.json) · [Integridad](D5-I61-integrity.json).

## Resultado propio

**43/43 PASS: 39 casos de dominio (15 CLIENT T y 24 REMOTE T/R) y cuatro controles. 39 SIGKILL positivos**, una caída objetivo por celda. Dos kills de timeout negativos quedan separados. **74 raíces y 304 hijos registrados**, cero raíces/hijos/hilos propios pendientes. Raw de 2996172 bytes, 284 entradas efectivas pre/post idénticas y 65.41s. Las selecciones de desarrollo no se suman como pruebas nuevas.

CE01–CE03 captura primer APPLY T antes de HEAD. CE04–CE07 ISSUE, CE20–CE23 QUERY y CE24–CE27 RESULT_DISPATCH(query_id=None) dan detalle causal nuevo para las 15 celdas que sólo tenían metadata histórica T. CE08–CE19 y CE28–CE39 acreditan las 24 variantes físicas CREATE/UPDATE/CLOSE de T/R con modo registrado explícitamente; no se deduce desde el orden del bucle o tres registros indistintos.

Cada secuencia liga run/Stores/cid/request/operación real/manifiesto/modo/punto con READY, SIGKILL -9, HEAD/recibo, lector independiente y CLIENT/REMOTE públicos spawn pasivos, y continuación explícita. Las dos parejas de lecturas por caso de dominio usan execute=lookup=0. Los controles aportan otras cuatro parejas; no añaden celdas. Huérfanos y temporales se observan físicamente, sin adoptarlos como HEAD. No se deduce persistencia o recuperación integrada sumando PASS aislados.

## Ramas observadas

Antes de HEAD se conservan estado/HEAD/recibos previos de la autoridad objetivo. After_head conserva exactamente un commit y recibo objetivo alcanzables y hashes de la petición real. CLIENT/REMOTE no objetivo permanece intacto durante caída/reapertura; la continuación activa se registra aparte.

APPLY se reproduce explícitamente y materializa TASK/mapping/base/procedencia una vez, sin binding ni envío. ISSUE publica intento único UNKNOWN/1/0 y luego una reconcile(close=True) explícita termina CLOSED_NO_EFFECT/2/1 sin entidad. QUERY publica el qid original una vez y RESULT posterior con P obtenida por el hijo termina EFFECT_CONFIRMED/2/1. Los recibos históricos tras CLOCK no rebobinan HEAD.

RESULT_DISPATCH obtiene P dentro del hijo antes de armar el hook. Antes de HEAD queda UNKNOWN/1/0 con pending send; reconcile explícita por lookup confirma /2/1 sin crear recibo del cid RESULT interrumpido. After_head queda EFFECT_CONFIRMED/2/0; read_command y replay exactos son históricos, incluso tras CLOCK. El lookup de replay es explícito y distinto de la reapertura pasiva.

REMOTE CREATE after_head conserva entidad v1 y P exacta; UPDATE conserva el mismo remote_id y key, cambia payload y pasa v2→v3 con foreign sentinel intacto. CREATE previo v1 y edición pública de foreign a v2 son preparación separada. CLOSE registra Store kind/mode CLOSE sobre manifest.operation CREATE: tombstone CLOSED_NO_EFFECT sin entidad, con remote_id/applied_version/payload_hash nulos. El hijo deriva ese modo de la llamada y el manifiesto reales; las peticiones REMOTE usan cid UUIDv5 y expected=None de la API pública.

Antes de HEAD REMOTE, reconcile(close=True) cierra el ticket sin ejecutar el efecto pendiente; UPDATE conserva entidad v2. Después de HEAD sólo lookup recupera P. CLIENT termina /2/1 con el mismo intento y pending vacío. La repetición pública exacta tras after_head conserva HEAD; antes de HEAD, repetir EXECUTE después del CLOSE de recuperación añade un recibo EXECUTE distinto sin cambiar entidades/keys/tickets, y no se etiqueta como replay histórico del CLOSE. Repetir CLOSE exacto sí es histórico. Los controles comprueban campos de gate erróneos, EOF/salida normal/timeout, propiedad de raíz y límites/integridad del raw/inventario.

## Ajuste de preparación autorizado

La primera selección de desarrollo encontró LOCAL_DIVERGENCE al usar EDIT_TASK T antes de PREPARE_PROJECTION y un fallo del control de presupuesto del harness nuevo. Se detuvo la preparación T UPDATE y se presentó el cambio concreto: segunda captura I26, nuevas revisiones SOURCE/EVALUATION/EFFECT y APPLY públicos. La selección A del usuario lo autorizó para CE12–CE15. El ajuste mantiene TASK y base coherentes, conserva las cuatro celdas y el oráculo v2→v3. Se corrigió el control para usar el presupuesto del módulo CE, sin modificar helpers anteriores ni límites del contrato. La reparación dirigida pasó. Una primera campaña CE43 también pasó; durante la revisión se añadió al gate APPLY el ID/hash explícito del manifiesto EFFECT y se repitió CE43 con esa fuente definitiva. Los intentos anteriores quedan supersedidos y no cuentan como pruebas adicionales de aceptación.

R conserva segundo SOURCE/BATCH y selección por el cid/request de su nuevo APPLY_BATCH, con la misma TASK participante y binding. T registra pin/bytes/grado de captura y el recibo del nuevo APPLY. Nunca se escribe estado/Store directamente para evitar validaciones. I60 permanece intacto como contrato histórico, y la ampliación autorizada se registra en el laboratorio y el JSON I61.

## Ocho regresiones separadas

| Campaña | Resultado | Inputs pre/post | Raw y contexto I61 |
|---|---|---|---|
| Python321 | 321/321 PASS | 79 idénticos | [raw](D5-I61-Python-regression-raw.json) · [contexto](D5-I61-Python-regression-context.json) |
| HC24 | 24/24 PASS | 90 idénticos | [raw](D5-I61-HC-regression-raw.json) · [contexto](D5-I61-HC-regression-context.json) |
| HF40 | 40/40 PASS | 99 idénticos | [raw](D5-I61-HF-regression-raw.json) · [contexto](D5-I61-HF-regression-context.json) |
| IC30 | 30/30 PASS | 108 idénticos | [raw](D5-I61-IC-regression-raw.json) · [contexto](D5-I61-IC-regression-context.json) |
| UQ24 | 24/24 PASS | 119 idénticos | [raw](D5-I61-UQ-regression-raw.json) · [contexto](D5-I61-UQ-regression-context.json) |
| RV20 | 20/20 PASS | 129 idénticos | [raw](D5-I61-RV-regression-raw.json) · [contexto](D5-I61-RV-regression-context.json) |
| NA36 | 36/36 PASS | 138 idénticos | [raw](D5-I61-NA-regression-raw.json) · [contexto](D5-I61-NA-regression-context.json) |
| FN64 | 64/64 PASS | 146 idénticos | [raw](D5-I61-FN-regression-raw.json) · [contexto](D5-I61-FN-regression-context.json) |

Cada runner histórico permanece intacto y conserva su descubrimiento efectivo, aunque no incluya CE. El runner CE sí incluye sus módulos, reutilizados, contrato y dependencias completas; sus 284 entradas se sellan por separado. Las regresiones son repeticiones independientes, sin sumarlas como tests nuevos o aceptación semántica. No se ejecutó auditor I38, SQL/Java/Docker o evidencia real.

## Integridad y pendientes

El validador documental independiente comprueba 43 filas, 39 gates/caídas, 39 deltas exactos I59, punteros raw, hashes pre/post y artifacts/contextos, anclas AST y continuidad de ramas/recibos/lecturas. Los archivos anteriores permanecen intactos. El checker estándar mantiene avisos de tamaño >1MB; su revisión íntegra con los mismos patrones y umbral temporal12MiB se registra en integridad, sin modificar el checker ni truncar evidencia. La revisión no autoriza push.

Las 39 celdas nuevas quedan **TEST_PASS_PENDING_SUFFICIENCY_REVIEW**. Las otras 101 celdas I59 conservan su evaluación; I61 no las reevalúa. **UI22.2 sigue PARTIAL, agregado 77/7; GI38 sigue parcial.** No se promociona a 140 celdas aceptadas ni se reconstruye stdout original I34/I36. Una revisión documental posterior deberá valorar suficiencia, incertidumbre fsync y perímetro nativo por separado; CE43 no amplía esos ámbitos automáticamente.

Sin cambios de producto, Store, fixtures T/R/nativas, schemas, hooks, helpers/tests/runners anteriores, registro I38 o handoff. D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. H07, D5 global/G01–G07/GI33/GI34/GI38/GI39/GI40 abiertos, closure=false; sin promoción30/35→35/35. GI06/GI12/GI18/GI24/GI30/GI36/GI42 reales/humanos pendientes de sus propias puertas, sin traslado a D6. P0: sin proveedor/credenciales/corpus real, consumo/reservas, activación, promoción, despliegue o D6; sin inspección/limpieza operativa dev/run_data/D4. Sólo publicado hasta I52; I53–I61 locales, sin push ni lectura nueva de remoto.
