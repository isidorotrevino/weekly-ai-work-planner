# D5 I62 — revisión de suficiencia UI22.2/GI38

Fecha: **2026-10-25**, Europe/Madrid. Base local I61 `64ee83c3ab023af13d379ca676e64830ae29f25f`. **DOCUMENTARY_REVIEW_COMPLETE_WITH_OPEN_CRITERIA**.
[Matriz de 140 celdas](D5-I62-matrix.md) · [Trazabilidad y dictamen estructurado](D5-I62-results.json) · [Integridad](D5-I62-integrity.json) · [Contrato finito I57](../design/D5-I57-FINITE-FRONTIERS-DESIGN.md) · [Evidencia I61](D5-I61-results.md).

## Dictamen y perímetro

**UI22.2: PARTIAL → SUPPORTS_BOUNDED para la matriz finita F1–F7 T/R v1 aprobada en I57.** Las 140 celdas tienen soporte acotado: 101 conservan su evaluación I59 y las 39 calificadas reciben evidencia causal propia I61 contrastada. Este inventario no es una suma de PASS ni una declaración universal de recuperación. Ninguna celda queda global_accepted=true.

La obligación original UI22 pide caída/reinicio antes y después de F1–F7, con estado/recibos/conflictos y doble remoto superviviente; I33 exige oráculo previo/posterior y respuesta perdida donde corresponde. I57 concreta 35 salidas/variantes y cuatro puntos físicos, distingue cortes lógicos y seis exclusiones justificadas. El dictamen se limita a ese contrato: estado inicial y autoridad propios de cada fila, tres puntos previos a HEAD y after_head tras fsync con respuesta local perdida. No redefine «cada frontera» como toda mutación imaginable ni certifica una transacción distribuida.

El agregado pasa de **77/7 a 78 SUPPORTS_BOUNDED / 6 PARTIAL**. Sólo se reevalúa UI22.2; las otras 83 partes se heredan de I59. GI38 obtiene evaluación de evidencia SUPPORTS_BOUNDED dentro de los ámbitos de sus UI, manteniendo **global_review=OPEN y closure=false**, igual que GI40. GI33/GI34/GI39 siguen parciales; todos los GI y D5 global/G01–G07 siguen abiertos. No se promueve el histórico30/35 a35/35.

## Cómo se resuelven las 39 celdas calificadas

Las 15 celdas CLIENT T añaden detalle por caso para primer APPLY antes de HEAD, ISSUE, QUERY y RESULT_DISPATCH(query_id=None). Se cotejan comando real, gate, cid/request/expected, manifiesto, HEAD/cadena/recibo y continuidad. El stdout I34 original continúa NOT_RECORDED; el nuevo raw I61 no lo reconstruye. FL07 after_head conserva su evidencia HF31 previa.

Las 24 celdas REMOTE T/R registran mode desde close y manifest.operation en el hijo y lo contrastan con petición y commit objetivo. CLOSE significa Store kind=CLOSE sobre manifiesto CREATE y tombstone sin entidad; UPDATE significa EXECUTE/UPDATE con base v2 y la misma entidad v3, payload distinto y foreign intacto. CREATE previo v1 y edición pública de foreign a v2 son preparación identificada, sin confundirlos con el efecto objetivo. La repetición de un pool histórico sin mode no se cuenta como tres observaciones distintas.

El ajuste T de CE12–CE15 fue autorizado explícitamente tras detectar LOCAL_DIVERGENCE con EDIT_TASK. Segunda captura I26, revisiones SOURCE/EVALUATION/EFFECT y APPLY públicos actualizan TASK y base conjuntamente antes de preparar UPDATE. La prueba conserva pin/bytes/recibo y el mismo oráculo v2→v3; no evita validaciones por escritura directa. R conserva SOURCE/BATCH y selección por su nuevo APPLY_BATCH exacto. El contraste usa la fuente y raw definitivos, no la ejecución CE43 anterior supersedida.

Cada una de las 39 secuencias mantiene run/Stores/cid/request/M/send/ticket/qid, READY y SIGKILL -9 hasta su reapertura y continuación. Los observadores spawn independientes (archivos y APIs públicas CLIENT/REMOTE) conservan HEAD/estado alcanzable y transporte pasivo execute=lookup=0. Antes de HEAD no hay recibo objetivo; después de HEAD existe exactamente el recibo esperado. Objetos huérfanos/temporales no se adoptan. Los cuatro controles y los kills de timeout negativos no añaden celdas de dominio.

## Continuaciones y evidencia conservada

APPLY y ISSUE se reproducen expresamente con el mismo cid/args/expected; QUERY conserva su qid original y el hijo obtiene P antes de publicar RESULT. RESULT_DISPATCH antes de HEAD termina por una reconcile explícita /2/1 y deja ausente el cid interrumpido; after_head conserva /2/0 y replay histórico. El CLOCK posterior no se rebobina. El lookup para construir un replay es explícito y no se atribuye a la reapertura pasiva.

REMOTE antes de HEAD conserva el estado previo; reconcile(close=True) publica tombstone sin reenviar el efecto pendiente. UPDATE conserva su entidad v2. Después de HEAD, reconcile por lookup recupera P exacta sin execute. Repetir EXECUTE después de un CLOSE de recuperación puede añadir un recibo distinto sin cambiar entidades/keys/tickets: se registra esa diferencia y no se llama replay histórico del CLOSE. La llamada exacta tras after_head y la repetición CLOSE exacta conservan HEAD. CLIENT termina /2/1, mismo intento y sin pending.

Las 60 celdas FN de primera publicación/ACCEPT/BIND y RESULT_QUERY conservan el soporte causal revisado en I59; las 41 restantes conservan evidencia HF/DR con su nivel de detalle original. Se comprueban hashes y punteros, sin afirmar que todas tengan el formato nuevo CE. Los doce cortes lógicos HF31–HF38/NA29–NA32 y seis exclusiones tipadas se mantienen separados. before_result no equivale a before_object de RESULT; después de APPLY no equivale a una caída dentro de BIND. CLOSE legacy sigue aplicable y F0 I26 sigue siendo prerrequisito.

## Límites de fsync, nativo y cierre

OSError directory_fsync/recovery_fsync conserva sólo el alcance observado DF11/DR24/HF25–HF30. I58/I61 no prueban esas variantes en primera ACCEPT, BIND o RESULT_QUERY; no se transfiere su soporte ni se confunde con SIGKILL o pérdida de energía. **La valoración de 140 celdas acredita los cuatro puntos físicos I57, no toda incertidumbre de I/O.** UI23 conserva su evaluación I59 sin reevaluación; ampliar la pretensión de recuperación incierta exige contrato/matriz y evidencia propios.

UI20.3 mantiene soporte acotado CREATE NATIVE_T/NATIVE_R según I56. NA29–NA32 aportan sólo sus cuatro casos F7; otras fases CORE nativas siguen NOT_ASSESSED. El soporte T/R v1 no se traslada a OBSERVE ni acredita una recuperación nativa integral. Tampoco se inventa un producto cartesiano obligatorio por admitir aquella extensión acotada. H07 global sigue abierto.

Las seis partes que permanecen parciales son **UI01.2, UI04.1, UI09.2, UI26.2, UI27.2 y UI34.3**. Sus pendientes son trazabilidad integral GI33/GI34 y carreras de origen/configuración/variación relacional con entrega GI39; CE43 no las resuelve por ejecutar regresiones. El registro fijo I38 permanece intacto y no se presenta como auditoría del nuevo expediente.

## Verificación documental

Se leen documentos, fuentes, AST, JSON, hashes y Git: **cero imports de producto/harness/auditor, discovery, campañas, SQL/Java/Docker o red**. Se verifican sellos I59/I60/I61, 39 secuencias nuevas, 140 celdas, doce cortes lógicos, seis exclusiones y los ocho pares raw/contexto I61 con entradas efectivas pre/post. Las ejecuciones siguen siendo históricas de I61 y sus antecedentes, no pruebas nuevas I62. El checker estándar conserva sus avisos de tamaño >1MB; revisión íntegra con los mismos patrones y umbral temporal12MiB registrada en integridad, sin modificar el checker ni truncar raws.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. D5 global/G01–G07 y GI33/GI34/GI38/GI39/GI40 abiertos, closure=false. GI06/GI12/GI18/GI24/GI30/GI36/GI42 reales/humanos conservan sus puertas propias, sin traslado a D6. P0: sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue ni D6; sin inspección/limpieza operativa dev/run_data/D4. Publicado sólo hasta I52; I53–I62 locales, sin push ni nueva lectura del remoto.
