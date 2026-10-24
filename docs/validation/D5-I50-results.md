# D5 I50 — resultados de incertidumbre durable

Fecha: **2026-10-24**, Europe/Madrid. **PASS de campaña sintética acotada**. Base autorizada: `1ef0bdf47c0c5cd4f68925c3ef6bec664e632748`. Selección A: implementar/validar I49 sin cambiar producto/API/modelo.

[Laboratorio](../design/D5-I50-DURABLE-UNCERTAINTY-LAB.md) · [Contrato](../design/D5-I49-DURABLE-UNCERTAINTY-DESIGN.md) · [Matriz](../design/D5-I49-DURABLE-UNCERTAINTY-REVIEW.md) · [Sello y punteros](D5-I50-results.json).

## Campañas separadas

| Campaña | Tests distintos | Resultado | Evidencia |
|---|---:|---|---|
| UQ | 24 | PASS acotado | [Raw](D5-I50-raw.json) |
| HC | 24 | PASS acotado | [Raw](D5-I50-HC-regression-raw.json), [contexto](D5-I50-HC-regression-context.json) |
| HF | 40 | PASS acotado | [Raw](D5-I50-HF-regression-raw.json), [contexto](D5-I50-HF-regression-context.json) |
| IC | 30 | PASS acotado | [Raw](D5-I50-IC-regression-raw.json), [contexto](D5-I50-IC-regression-context.json) |
| Python | 321 | PASS acotado | [Raw](D5-I50-Python-regression-raw.json), [contexto](D5-I50-Python-regression-context.json) |

Los 26 escenarios UQ corresponden a 24 tests: UQ17/UQ18 tienen un segundo contraste UNKNOWN/CLOCK en otra raíz. No se suman escenarios, lectores, actores, pruebas negativas ni regresiones históricas como tests nuevos. Los cinco grupos tienen IDs separados; no constituyen por suma evidencia integrada global. Los new_tests del runner Python histórico son DR de I36, regresión en I50.

## Hechos observados y límites

- UQ01–UQ06: ausencia o excepción antes de llamada real conserva UNKNOWN y un intento; conocer el desenlace del fixture no autoriza reenvío desde CLIENT.
- UQ07/UQ08: execute real confirma una entidad versión1 y el wrapper pierde respuesta. RESULT(None) deja UNKNOWN/ledger2/queries0 **sin pending send**. La reapertura no consulta; reconcile explícita confirma ledger3/queries1 mediante lookup, sin execute adicional.
- UQ09/UQ10: existe prueba REMOTE del ticket emitido pero la primera consulta falla antes de lookup real. UNKNOWN/2/queries1 conserva send pending; segunda consulta explícita confirma ledger3/queries2 sin escribir REMOTE.
- UQ11–UQ16: listas/envelopes inválidos y ticket incompatible fijan CONFLICT/hard_conflict. La prueba correcta posterior incrementa ledger a 3/queries a 2 pero no limpia conflicto ni se adopta en sends.proof. **No son colecciones de múltiples resultados válidas.**
- UQ17/UQ18: NO_EFFECT/RATE_LIMIT correlacionado con retry_tick=5 bloquea antes del tick y admite un retry explícito tras CLOCK5. El ticket nuevo produce un efecto; el contraste UNKNOWN continúa BINDING_UNRESOLVED tras el mismo reloj.
- UQ19/UQ20: prueba NO_EFFECT con retry_tick=None mantiene RETRY_NOT_ELIGIBLE después de CLOCK5.
- UQ21–UQ24: lectores pasivos con cero llamadas de transporte, ownership restaurado antes de limpieza, inventario/raw/metadatos/budgets/conteos con negativos explícitos.

## Matriz ejecutada

| Caso | Recorrido / familia | Escenarios | Resultado | Límite |
|---|---|---:|---|---|
| UQ01 | T / LOOKUP_EMPTY | 1 | PASS acotado | Ausencia por ticket, no colección de cero matches ni prueba de no efecto |
| UQ02 | R / LOOKUP_EMPTY | 1 | PASS acotado | Ausencia por ticket, no colección de cero matches ni prueba de no efecto |
| UQ03 | T / LOOKUP_ERROR_EMPTY | 1 | PASS acotado | Excepción de transporte sintética; no respuesta HTTP ni 429 |
| UQ04 | R / LOOKUP_ERROR_EMPTY | 1 | PASS acotado | Excepción de transporte sintética; no respuesta HTTP ni 429 |
| UQ05 | T / EXECUTE_ERROR_BEFORE | 1 | PASS acotado | Posible entrega desconocida desde CLIENT; saber que fixture no ejecutó no autoriza retry |
| UQ06 | R / EXECUTE_ERROR_BEFORE | 1 | PASS acotado | Posible entrega desconocida desde CLIENT; saber que fixture no ejecutó no autoriza retry |
| UQ07 | T / EXECUTE_ERROR_AFTER | 1 | PASS acotado | Pérdida de respuesta tras efecto demostrado, no semántica HTTP 429 |
| UQ08 | R / EXECUTE_ERROR_AFTER | 1 | PASS acotado | Pérdida de respuesta tras efecto demostrado, no semántica HTTP 429 |
| UQ09 | T / LOOKUP_ERROR_WITH_PROOF | 1 | PASS acotado | La prueba existe pero no se observó en la primera consulta |
| UQ10 | R / LOOKUP_ERROR_WITH_PROOF | 1 | PASS acotado | La prueba existe pero no se observó en la primera consulta |
| UQ11 | T / LIST_DUPLICATE_PROOFS | 1 | PASS acotado | Lista incompatible con proof_ok; NO acredita colección múltiple válida del dominio |
| UQ12 | R / LIST_DUPLICATE_PROOFS | 1 | PASS acotado | Lista incompatible con proof_ok; NO acredita colección múltiple válida del dominio |
| UQ13 | T / MATCH_ENVELOPE | 1 | PASS acotado | Envelope ajeno al schema durable, NO consulta nativa de múltiples resultados; match sintético sólo negativo |
| UQ14 | R / MATCH_ENVELOPE | 1 | PASS acotado | Envelope ajeno al schema durable, NO consulta nativa de múltiples resultados; match sintético sólo negativo |
| UQ15 | T / WRONG_TICKET | 1 | PASS acotado | Control de correlación existente repetido, no nuevo caso de múltiples coincidencias |
| UQ16 | R / WRONG_TICKET | 1 | PASS acotado | Control de correlación existente repetido, no nuevo caso de múltiples coincidencias |
| UQ17 | T / RATE_LIMIT_CONCLUSIVE | 2 | PASS acotado | RATE_LIMIT con prueba de no efecto; no ambigüedad HTTP. Nunca retry automático |
| UQ18 | R / RATE_LIMIT_CONCLUSIVE | 2 | PASS acotado | RATE_LIMIT con prueba de no efecto; no ambigüedad HTTP. Nunca retry automático |
| UQ19 | T / RATE_LIMIT_NO_DELAY | 1 | PASS acotado | Prueba no equivale a elegibilidad; None no concede espera cero |
| UQ20 | R / RATE_LIMIT_NO_DELAY | 1 | PASS acotado | Prueba no equivale a elegibilidad; None no concede espera cero |
| UQ21 | T / OWNERSHIP_PASSIVE | 1 | PASS acotado | Control repetido de propiedad/reapertura; no SIGKILL ni recuperación nueva |
| UQ22 | R / OWNERSHIP_PASSIVE | 1 | PASS acotado | Control repetido de propiedad/reapertura; no SIGKILL ni recuperación nueva |
| UQ23 | T / INVENTORY_RAW | 1 | PASS acotado | Metacontrol no suma escenarios/probes como tests ni completa UI20.3 |
| UQ24 | R / INVENTORY_RAW | 1 | PASS acotado | Metacontrol no suma escenarios/probes como tests ni completa UI20.3 |

## Integridad y recursos

UQ registra 118 inputs actuales, iguales antes/después; HC89/HF98/IC107/Python78 conservan sus conjuntos efectivos propios. Contextos registran Python/build/optimización/debug/comando. Producto y archivos históricos mantienen bytes; se verifican los sellos I49/I48/I46/I44/I42/I40 sin reescribirlos. Los catálogos nuevos incluyen fuente, símbolo/línea/hash, test ID, raw y cada escenario/evento/oráculo; los objetivos UI declarados no sustituyen suficiencia semántica.

UQ: 41 raíces propias, 198 hijos con salida0; cero raíces/hijos/hilos propios restantes. No SIGKILL positivos ni negativos. Recursos de cada regresión están separados en su raw y sello; observaciones de laboratorio no certifican host/dev/D4, energía, disco, NFS, Windows o caller hostil. Los límites de prueba reducidos no acreditan máximos completos.

La campaña UQ pasó en su primera ejecución completa y se conserva ese stdout exacto; no hubo pruebas UQ preliminares, fallos funcionales ni repetición para conseguir PASS. El lanzador externo de regresión falló inicialmente al importar testing desde /tmp antes de iniciar ninguna campaña; se corrigió su PYTHONPATH, sin alterar runner ni contar ese intento como test. Las regresiones finales tienen contexto y stdout propios.

## Pendientes y continuidad

**MG01–MG03: NO_NATIVE_MODEL, no tests ni PASS. UI20.3 sigue PARTIAL; H07 permanece abierto.** No se ensayó HTTP429 real ni una colección durable de múltiples coincidencias válidas. La pérdida OSError es falta de prueba; RATE_LIMIT con prueba concluyente es otra condición. MG03 no introduce una obligación de selección/adopción a UI20.3. No se añade API, formato persistido, migración o autoridad para resolver estos límites.

I48 conserva sus valoraciones históricas. Este corte añade evidencia acotada por secuencia/run/store/ticket; no deduce integración desde PASS aislados. Sin nuevas caídas, carreras, UPDATE/CLOSE, origen/cuenta/perfil, dos tickets autorizados UI33.2 ni variaciones relacionales UI34.3. Raw original I34/I36 sigue NOT_RECORDED.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. D5 global, G01–G07 y revisión global GI33/GI34/GI38/GI39/GI40 abiertos, closure=false; sin promoción del 30/35. Sin proveedores/credenciales reales, corpus privado, consumo/reservas, activación, promoción, despliegue, SQL/Java/Docker, auditor o D6.

P0: I32, handoff y posteriores sin publicar. Git se comprueba localmente; origin/main es tracking cacheado, sin consulta remota nueva. Un commit local I50 no autoriza publicación; una decisión separada debe especificar SHA/rama/destino y verificar remoto/ascendencia/diff.
