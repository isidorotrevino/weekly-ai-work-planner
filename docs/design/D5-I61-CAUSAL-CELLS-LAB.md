# D5 I61 — laboratorio de las 39 celdas calificadas

Fecha: **2026-10-25**, Europe/Madrid. Base de implementación: I60 `65fa390`.
[Contrato I60](D5-I60-CAUSAL-CELLS-DESIGN.md) · [Matriz CE43](D5-I60-CAUSAL-CELLS-REVIEW.md) · [Harness](../../testing/causal_frontier_cells/README.md).

La selección A posterior a I60 aprueba implementar/validar CE43 y ocho regresiones separadas, sin cambiar producto/fixtures/hooks/registro I38. Los flags de preparación de I60 permanecen como historia. No autoriza push o cierre de criterios.

## Ajuste concreto aprobado de preparación T UPDATE

En una selección de desarrollo, EDIT_TASK público modifica TASK pero no base. PREPARE_PROJECTION devuelve LOCAL_DIVERGENCE; no es una caída objetivo ni evidencia de recuperación fallida. Se detuvo esa preparación de CE12–CE15 y se presentó al usuario la sustitución concreta. Su selección **A** autoriza segunda captura I26, nuevas revisiones EVALUATION/EFFECT y APPLY públicos, que actualizan TASK y base conjuntamente. I60 permanece intacto; este ajuste no cambia las cuatro celdas, el oráculo UPDATE v2→v3, presupuesto o producto.

T captura los bytes del nuevo título en la misma fixture I26, importa el commit, acepta SOURCE, prepara/acepta EVALUATION y EFFECT y aplica con recibo exacto. Se registra el commit I26 y el cid/request APPLY. R conserva su preparación de segundo SOURCE/BATCH y selección por recibo aprobada en I60. Las dos rutas preparan/revisan después UPDATE con remote_base v2 exacta; ninguna escribe estado/Store directamente para evitar validaciones.

CREATE previo v1 y Remote.edit público de foreign a v2 son preparación registrada. El efecto objetivo conserva remote_id y creation_key, aplica payload nuevo, versión3 y foreign sentinel. Antes de HEAD conserva v2; la recuperación explícita cierra el ticket sin volver a aplicar. Después de HEAD consulta P y mantiene v3. CLOSE es kind/mode CLOSE sobre manifiesto CREATE, sin entidad.

## Observación y continuación

El hijo deriva el modo desde la operación efectiva y el manifiesto leído de CLIENT durable. READY conserva identidad de ambos Stores, rol/punto/operación real, manifiesto/creación/binding/target, send/ticket/qid/ledger y hashes de args/petición/base/capacidades. REMOTE usa el cid UUIDv5 y expected=None de su API pública. RESULT_DISPATCH obtiene P por lookup dentro del hijo y arma el hook después; no recibe P del padre.

Lector independiente y CLIENT/REMOTE públicos spawn se ejecutan por separado antes de continuar y al final, sin execute/lookup durante lectura pasiva. Los objetos físicos huérfanos/temporales no sustituyen HEAD alcanzable. Los oráculos distinguen la rama anterior a HEAD, el recibo tras after_head y la continuación expresamente llamada.

Después de un crash REMOTE anterior a HEAD, reconcile(close=True) publica tombstone sobre el ticket emitido. Repetir después EXECUTE original puede añadir un recibo de operación distinta que devuelve el tombstone existente; se registra esa diferencia, preservando entidades/keys/tickets. Repetir CLOSE exacto, o cualquier llamada objetivo tras after_head, es histórico y conserva HEAD. No se etiqueta la operación distinta como replay histórico.

## Entregables y límites

El raw CE43 y los ocho pares de regresión/contexto registran ejecuciones independientes e inputs efectivos pre/post. Una selección de desarrollo no se suma como pruebas nuevas. Los resultados definitivos documentan counts, recursos, deltas de 39 celdas, hashes y punteros por caso; TEST_PASS queda pendiente de suficiencia semántica posterior.

Sin nuevos OSError, casos nativos, carreras auxiliares, APIs o hooks; sin cambios en documentos/raws anteriores ni auditor/registro I38. D1–D4 cerrados y hito D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. UI22.2 PARTIAL, 77/7, H07 y D5 global/G01–G07/GI33/GI34/GI38/GI39/GI40 abiertos; sin promoción 30/35→35/35. Los siete requisitos reales/humanos conservan sus puertas propias. P0 vigente: sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue o D6; sin inspección/limpieza operativa dev/run_data/D4. Sin push.
