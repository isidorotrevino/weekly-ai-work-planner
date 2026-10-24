# D5 I55 — ambigüedad durable nativa

Fecha: **2026-10-24**, Europe/Madrid. Base local I54 `33440d3cf760d7d38ceaa6ab11b2f0823a599f8a`. **IMPLEMENTATION_VALIDATED_WITH_OPEN_CRITERIA**.
[Laboratorio y decisiones](../design/D5-I55-NATIVE-AMBIGUITY-LAB.md) · [Contrato aprobado](../design/D5-I54-NATIVE-AMBIGUITY-DESIGN.md) · [Matriz NA01–NA36](../design/D5-I54-NATIVE-AMBIGUITY-REVIEW.md) · [Resultados, fuentes y correspondencia](D5-I55-results.json) · [Raw NA36](D5-I55-raw.json).

El usuario aprobó **A**: implementar la extensión sintética I55, validar NA01–NA36 y Python321/HC24/HF40/IC30/UQ24/RV20 por separado. El sello histórico I54 sigue describiendo su preparación; no se reescriben sus booleans. Sin push nuevo. `origin/main` permanece en I52 `ce44158`; I53/I54 y este trabajo posterior son locales.

## Resultado y evidencia concreta

**36/36 tests PASS**: 32 de dominio y cuatro controles, **48 subescenarios**, cuatro secuencias positivas de SIGKILL y cero skips. No se suman subvariantes/donantes o controles internos como tests. Raw propio de 2581588 bytes, 138 entradas pre/post idénticas, 77 raíces y 347 hijos registrados; cero raíces/hijos/hilos propios pendientes. Duración 71.407s. Las ejecuciones previas de desarrollo/sellado sustituidas no se incluyen en este conteo.

- NA07–NA10: colecciones nativas de dos coincidencias (IDs distintos y repetidos) producen conflicto persistente; P exacta o vista limpia posterior no borran el conflicto ni el historial. El catálogo externo conserva su recibo separado; no son dos efectos CREATE autorizados.
- NA15–NA20: el protocolo sintético representa 429 antes y después del efecto real. AFTER conserva P/entidad v1 reales mientras CLIENT queda UNKNOWN/2/0 sin pending send; un CLIENT fresco lee sin llamadas y una consulta explícita confirma ese mismo ticket en /3/1 sin execute. BEFORE sigue UNKNOWN tras consulta vacía. No son respuestas HTTP reales.
- NA21–NA24: un tick elegible no autoriza retry de UNKNOWN, tampoco un send/cid/manifiesto revisado nuevo del mismo binding. Sólo el control NO_EFFECT/RATE_LIMIT correlacionado permite retry explícito tras CLOCK: nuevo ticket, dos intentos y un efecto. La guarda de ambigüedad no depende de pending vacío.
- NA25–NA28: estructura inválida no publica OBSERVE; combinación válida incompatible registra conflicto. Se comprueban 64KiB exactos/+1, ocho matches/+1, proof_bytes reducido, replay de recibo sin rebobinar y ledger CAS vieja rechazada. Son negativos identificados, sin adjudicarles semántica nativa positiva.
- NA29–NA32: cada secuencia enlaza ISSUE, efecto real, QUERY, OBSERVE y reapertura con run/stores/send/ticket/M/cid exactos. Before_observe deja ledger1/queries1 y send+query pending; nueva consulta explícita confirma /2/2 sin ejecutar. After_head deja /2/1 con un recibo alcanzable y replay idéntico. No se infiere recuperación sumando PASS aislados ni se completa todo F1–F7.

La composición reutiliza reducers T/R sin modificarlos. Se persiste sólo una cadena exterior; recibos core se materializan desde esa autoridad. T conserva captura I26 y revisiones SOURCE/EVALUATION/EFFECT. R conserva su lote, recibo y selección TASK, sin elevarlo a I32. El nuevo módulo es fixture sintética, sin cambio de producto ni de fixtures/runners anteriores. Core.RESULT no sustituye OBSERVE nativo.

## Regresiones separadas

| Campaña | Resultado | Inputs efectivos estables | Contexto/raw nuevos |
|---|---|---|---|
| Python321 | 321/321 PASS | 79 | [contexto](D5-I55-Python-regression-context.json) · [raw](D5-I55-Python-regression-raw.json) |
| HC24 | 24/24 PASS | 90 | [contexto](D5-I55-HC-regression-context.json) · [raw](D5-I55-HC-regression-raw.json) |
| HF40 | 40/40 PASS | 99 | [contexto](D5-I55-HF-regression-context.json) · [raw](D5-I55-HF-regression-raw.json) |
| IC30 | 30/30 PASS | 108 | [contexto](D5-I55-IC-regression-context.json) · [raw](D5-I55-IC-regression-raw.json) |
| UQ24 | 24/24 PASS | 119 | [contexto](D5-I55-UQ-regression-context.json) · [raw](D5-I55-UQ-regression-raw.json) |
| RV20 | 20/20 PASS | 129 | [contexto](D5-I55-RV-regression-context.json) · [raw](D5-I55-RV-regression-raw.json) |

Las repeticiones no son tests nuevos ni evidencia transferida por suma. Python321 usa el runner JSON histórico que hace el mismo discovery unittest de testing/D5 indicado en I54 y añade inventarios; no se modificaron comandos internos/tests. Las seis campañas conservan sus propios comandos, versiones, inputs efectivos pre/post, raws y recursos. La nueva fuente entra en los glob de fuentes de las regresiones; no se presenta como un test antiguo ni se omite del inventario.

## Integridad y revisión del archivo grande

El validador independiente resolvió 36 filas/48 subescenarios, 270 comprobaciones de hash de observaciones, 38 anclas de fuente y 20 enlaces locales, más inputs y los 13 artifacts raw/contexto. El control estándar de publicación señala únicamente que el raw de 2.6MB supera su umbral de 1MB. Se revisó expresamente su contenido sintético completo aplicando los mismos patrones a los 637 archivos con umbral temporal de 12MiB, sin modificar el checker ni su configuración persistida; no hubo coincidencias. Se conserva el aviso estándar de tamaño y el SHA revisado. Esto no autoriza publicar.

## Estado semántico y límites

MG01 y MG02: **IMPLEMENTED_BOUNDED_REVIEW_PENDING** para esta extensión sintética CREATE T/R. MG02 no certifica HTTP/API Plane. MG03 sigue fuera: conservar un conjunto observado no implementa selección/adopción humana. Los MODEL_GAP históricos de I49/I50 no cambian retrospectivamente. La capacidad pertenece al nuevo namespace NATIVE_T/NATIVE_R; no se atribuye automáticamente a las APIs T/R v1 ni al registro fijo I38. Su aplicabilidad debe revisarse expresamente.

UI20.3 continúa **PARTIAL** y H07 abierto; se mantiene el agregado I53 **76 con soporte acotado / ocho parciales**, pendiente de revisión dirigida de fuentes/oráculos/raw de esta nueva capacidad. D5 global, G01–G07 y los cinco GI siguen abiertos, closure=false. No hay promoción 30/35→35/35 ni cierre de un requisito real/humano por este PASS. GI06/GI12/GI18/GI24/GI30/GI36/GI42 conservan su puerta propia.

No cubre UPDATE, CLOSE, adopción/resolución, todas las fronteras F1–F7, carreras de origen/perfil/política o entrega relacional, host/energía/disco/NFS/Windows ni capacidades reales. D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. Sin SQL/Java/Docker, auditor I38, proveedor/credenciales/corpus real, consumo/reservas, activación, promoción, despliegue o D6. Sólo limpieza de raíces propias; no inspección operativa dev/run_data/D4.

Siguiente trabajo propuesto: revisión documental dirigida UI20.3/H07 contra contrato, código y evidencia I55, conservando el límite de protocolo sintético; cualquier revisión o siguiente corte se concreta por separado antes de nuevos cambios de modelo/campañas. Publicar Git tampoco equivale a aceptar D5 global.
