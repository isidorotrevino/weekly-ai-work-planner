# D5 I64 — intercalados finitos GI39

Fecha: **2026-10-25**, Europe/Madrid. Base local I63 `3934e51621883e737b9fe3de26763ca6bdc9b39d`. **IMPLEMENTATION_VALIDATED_WITH_OPEN_CRITERIA**.
[Laboratorio](../design/D5-I64-GI39-INTERLEAVINGS-LAB.md) · [Contrato I63](../design/D5-I63-GI39-INTERLEAVINGS-DESIGN.md) · [GX90](../design/D5-I63-GI39-INTERLEAVINGS-REVIEW.md) · [Resultados y punteros](D5-I64-results.json) · [Raw GX90](D5-I64-raw.json) · [Integridad](D5-I64-integrity.json).

La selección A posterior a I63 autoriza GX90 y nueve regresiones separadas. No autoriza publicación o cierre semántico/global. Los flags de preparación de I63 permanecen como historia.

## Resultado propio

**90/90 PASS: 86 casos de dominio sobre 22 mutaciones y cuatro controles.** UI26.2=30, UI27.2=23 y UI34.3=33. Familias: 24 LOCAL_APPLY,10 BEFORE_ISSUE,44 INFLIGHT y8 INFLIGHT_LOST_RESPONSE. **Cero SIGKILL positivos nuevos**; dos kills de timeout negativos separados. 134 raíces y 764 hijos registrados, cero raíces/hijos/hilos propios pendientes. Raw completo de 9755830 bytes, 317 entradas pre/post idénticas, 193.418s; dentro de12MiB, sin truncado.

86 gates primarios READY,12 PREPARED/probes de lock y98 liberaciones correlacionadas conservan el orden causal, no sólo timestamps o PASS. Hay176 parejas de lectores pasivos: dos por caso de dominio y una por control. Cada pareja separa lector de archivos independiente de APIs públicas CLIENT/REMOTE spawn con execute=lookup=0. Los actores que compiten terminan con salida0; esta campaña no se presenta como nueva prueba crash/H02 o recuperación integrada por sumar PASS aislados.

## Efecto local e invalidación previa a ISSUE

MUTATION_FIRST confirma la mutación completa mientras APPLY/APPLY_BATCH espera dentro de before_lock. La invocación con E vieja produce CONFLICT_HEAD sin recibo/efecto; una nueva invocación negativa explícita, HEAD fresca/cid nuevo y argumentos viejos acredita STALE_SOURCE, REVIEW_REQUIRED, STALE_PROFILE o STALE_EVALUATION según fila. CONFLICT_HEAD por sí solo no se cuenta como rechazo de dominio.

COMMIT_FIRST retiene CLIENT en before_object; contender PREPARED observa EAGAIN/EWOULDBLOCK mediante probe, sin afirmar entrada previa en flock bloqueante. APPLY/APPLY_BATCH confirma una vez; contender con E vieja pierde. Una mutación nueva explícita con HEAD/generations frescas confirma después, preservando efecto y recibo históricos. La preparación posterior con pins/revisiones viejos falla sin emitir send; T puede publicar BIND auxiliar explícito antes del rechazo de PREPARE_PROJECTION, sin aceptar PROJECTION. R intenta SELECT_TASKS por el recibo BATCH original sin reselección implícita. No rollback de un efecto local que ganó antes del cambio.

Las diez variantes relacionales previas a entrega tienen BATCH ya aplicado. ISSUE en before_lock pierde HEAD tras mutación; una nueva invocación negativa con HEAD fresca produce STALE_SELECTION y cero nuevo send/ticket/efecto. Se conserva el cambio relacional observado; no se exige que data permanezca igual cuando precisamente es el dato mutado.

## Mutación durante ejecución remota real

Cada una de las22 mutaciones se ejecuta dentro de una llamada Remote.execute real: CREATE/before_object y UPDATE/after_head. ISSUE real ya conservó UNKNOWN/ledger1/queries0 y el ticket único del caso. El hijo identifica run/Stores/operación/modo/M/send/ticket/cid UUIDv5/request/expected=None, dentro de la llamada, con execute1/lookup0 y sin P devuelta aún. El actor CLIENT confirma la mutación sin tocar REMOTE retenido; tras ACK de liberación el efecto histórico puede concluir.

RESULT conserva P exacta, EFFECT_CONFIRMED/ledger2/queries0 y validity=STALE, sin pending ni intento nuevo. CREATE produce una entidad v1; UPDATE preserva remote_id/key y foreign GX_KEEP, cambia payload y avanza v2→v3 exactamente una vez. CREATE v1 y edición pública de foreign a v2 son preparación separada. SOURCE/cuenta/perfil/política/revisiones/data_hash/relaciones mutados no se rebobinan al publicar RESULT. Nuevo dispatch del paquete viejo y retry del mismo send se rechazan con el error semántico específico, sin mover HEAD/recibos/REMOTE. EFFECT_REVOKE T distingue REVIEW_REQUIRED en APPLY de STALE_REVIEW en ISSUE.

Ocho casos pierden la respuesta en el wrapper después de volver Remote.execute real: S01,S05,C01,C02,C03,R03,R06,R07. REMOTE conserva P/efecto/recibo y CLIENT queda UNKNOWN/2/0 STALE con pending vacío. La lectura pasiva no consulta; sólo reconcile explícita posterior hace lookup1/execute0 y confirma EFFECT_CONFIRMED/3/1 STALE, REMOTE íntegro. La pérdida sintética de respuesta usa OSError de transporte después del commit, como estipula I63; no se confunde con inyección fsync ni SIGKILL.

## Autoridad de preparación y controles

T mantiene I26/pin/bytes y las revisiones propias. Observación B válida se registra antes de EVALUATION, de modo que C03 parte de un paquete vigente y acredita A→B→A con generation+2. PROFILE/POLICY/ADAPTER ABA conservan valor final A pero no la generación; REVOKE_OBSERVATION se registra como revocación irreversible. R mantiene lote de siete entidades, TASK0 por cid/request BATCH exactos y tres tipos de relación; cuatro clases de dependencia tienen aristas nuevas TASK0→TASK2, sin duplicados/ciclos. No campos T ficticios ni revisión I32 en R.

La vía UPDATE T reutiliza la preparación pública coherente aprobada en I61 (segunda captura, revisiones y APPLY), R segundo SOURCE/BATCH y selección por recibo nuevo. Nunca se escribe estado/Store directamente para construir autoridad. GX87–GX90 prueban protocolo, ownership y presupuestos/inventario/raw; no añaden carreras. En desarrollo se corrigieron imports del oráculo, una comparación indebida de data antes de ISSUE y nombres del inventario del runner nuevo. No hubo cambio de producto, presupuesto, contrato o helper anterior. La campaña completa capturada tras esas correcciones se adopta byte a byte como evidencia definitiva al verificar entradas pre/post aún idénticas; selecciones dirigidas no suman pruebas de aceptación.

## Nueve regresiones separadas

| Campaña | Resultado | Inputs pre/post | Raw y contexto I64 |
|---|---|---|---|
| Python321 | 321/321 PASS | 79 idénticos | [raw](D5-I64-Python-regression-raw.json) · [contexto](D5-I64-Python-regression-context.json) |
| HC24 | 24/24 PASS | 90 idénticos | [raw](D5-I64-HC-regression-raw.json) · [contexto](D5-I64-HC-regression-context.json) |
| HF40 | 40/40 PASS | 99 idénticos | [raw](D5-I64-HF-regression-raw.json) · [contexto](D5-I64-HF-regression-context.json) |
| IC30 | 30/30 PASS | 108 idénticos | [raw](D5-I64-IC-regression-raw.json) · [contexto](D5-I64-IC-regression-context.json) |
| UQ24 | 24/24 PASS | 119 idénticos | [raw](D5-I64-UQ-regression-raw.json) · [contexto](D5-I64-UQ-regression-context.json) |
| RV20 | 20/20 PASS | 129 idénticos | [raw](D5-I64-RV-regression-raw.json) · [contexto](D5-I64-RV-regression-context.json) |
| NA36 | 36/36 PASS | 138 idénticos | [raw](D5-I64-NA-regression-raw.json) · [contexto](D5-I64-NA-regression-context.json) |
| FN64 | 64/64 PASS | 146 idénticos | [raw](D5-I64-FN-regression-raw.json) · [contexto](D5-I64-FN-regression-context.json) |
| CE43 | 43/43 PASS | 284 idénticos | [raw](D5-I64-CE-regression-raw.json) · [contexto](D5-I64-CE-regression-context.json) |

Son nueve ejecuciones independientes, con sus runners históricos intactos e inventarios efectivos propios, aunque no descubran GX. El runner GX sí declara sus317 entradas efectivas y dependencias, incluidas las reutilizadas CE y el contrato/sello I63. No se suman repeticiones como tests nuevos ni aceptación global. No se ejecutó auditor I38 o SQL/Java/Docker.

## Integridad y pendientes

El validador documental independiente comprueba90 filas,86 órdenes/gates,12 probes,98 ACK,176 parejas pasivas, punteros JSON, anclas AST, comandos/recibos/generaciones y los19 artifacts raw/contexto de las diez campañas. Los archivos anteriores permanecen intactos. El checker estándar mantiene avisos >1MB; revisión íntegra con mismos patrones y umbral temporal12MiB registrada en integridad, sin modificar el checker ni truncar raw. Esta higiene no autoriza push.

Los86 casos nuevos quedan **TEST_PASS_PENDING_SUFFICIENCY_REVIEW** para las tres partes dirigidas. **UI26.2/UI27.2/UI34.3 siguen PARTIAL y agregado78/6 intacto**, pendiente de revisión documental de suficiencia dentro del perímetro finito, sin extender a combinaciones no seleccionadas. UI22.2/GI38 mantienen soporte acotado I62 T/R v1; sin ampliar fsync o fases nativas. H07 y todos los criterios globales siguen abiertos, sin promoción30/35→35/35.

Sin cambios de producto/Store/fixtures/schemas/hooks/helpers/tests/runners/documentos/raws anteriores, registro I38 o handoff. D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. D5 global/G01–G07/GI33/GI34/GI38/GI39/GI40 abiertos, closure=false. Los siete reales/humanos conservan sus puertas propias, sin traslado a D6. P0: sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue o D6; sin inspección/limpieza operativa dev/run_data/D4. Sólo limpieza propia. Publicado sólo hasta I52; I53–I64 locales. Sin push ni lectura nueva del remoto.
