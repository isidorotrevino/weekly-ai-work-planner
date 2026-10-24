# D5 I52 — resultados de revocación en vuelo

Fecha: **2026-10-24**, Europe/Madrid. **PASS de campaña sintética acotada**. Selección A sobre I51; base `21cbfe03342dfaf43b4707d87a7c4a0cd4ba0f98`.

[Laboratorio](../design/D5-I52-INFLIGHT-REVOCATION-LAB.md) · [Contrato](../design/D5-I51-INFLIGHT-REVOCATION-DESIGN.md) · [Matriz](../design/D5-I51-INFLIGHT-REVOCATION-REVIEW.md) · [Sello y punteros](D5-I52-results.json) · [Preparación CP01/CP05](D5-I52-CP01-CP05-preparation.md).

## Campañas separadas

| Campaña | Tests distintos | Resultado | Evidencia |
|---|---:|---|---|
| RV | 20 | PASS acotado | [Raw RV](D5-I52-raw.json) |
| Python | 321 | PASS acotado | [Raw](D5-I52-Python-regression-raw.json), [contexto](D5-I52-Python-regression-context.json) |
| HC | 24 | PASS acotado | [Raw](D5-I52-HC-regression-raw.json), [contexto](D5-I52-HC-regression-context.json) |
| HF | 40 | PASS acotado | [Raw](D5-I52-HF-regression-raw.json), [contexto](D5-I52-HF-regression-context.json) |
| IC | 30 | PASS acotado | [Raw](D5-I52-IC-regression-raw.json), [contexto](D5-I52-IC-regression-context.json) |
| UQ | 24 | PASS acotado | [Raw](D5-I52-UQ-regression-raw.json), [contexto](D5-I52-UQ-regression-context.json) |

RV contiene 20 escenarios para 20 métodos explícitos. Doce casos RV05–RV16 registran intercalación durante Remote.execute real; RV01–RV04 son controles previos a ISSUE y RV17–RV20 controles de laboratorio. No se suman actores, lectores, escenarios, assertions o campañas previas como tests nuevos. Las regresiones mantienen sus propios IDs/inputs/contextos y recursos. Los new_tests del runner Python histórico siguen siendo DR de I36 reejecutados, no novedades de I52.

## Secuencias observadas

- RV01–RV04: REVOKE v2 antes de ISSUE produce REVIEW_REQUIRED, sin nueva emisión, recibo o efecto frente al baseline. UPDATE conserva el CREATE histórico previo.
- RV05–RV08: READY en before_object se produce dentro de Remote.execute y con HEAD REMOTE aún en baseline. Otro proceso confirma REVIEW v2 en CLIENT; sólo después se libera EXECUTE. El ticket emitido confirma un efecto y RESULT registra EFFECT_CONFIRMED/ledger2/queries0 + STALE.
- RV09–RV12: READY en after_head observa efecto/prueba ya alcanzables mientras EXECUTE no ha retornado. La revocación confirma antes del ACK; la prueba posterior es un hecho histórico, no éxito vigente. No se equipara la lectura del padre a prueba ya recibida por CLIENT.
- RV13–RV16: la misma intercalación after_head pierde respuesta mediante OSError después del retorno real de EXECUTE. RESULT(None) deja UNKNOWN/ledger2/queries0 y sin pending send. La apertura pasiva no consulta; reconcile explícita usa lookup=1/execute=0, conserva REMOTE y confirma EFFECT_CONFIRMED/ledger3/queries1 + STALE.
- Todos los casos sustantivos comprueban revisión realmente confirmada, replay histórico de esa revocación sin rebobinado y CONFLICT_REVIEW por versión vieja. Retry bajo la proyección revocada falla REVIEW_REQUIRED sin nuevo ticket/efecto. CREATE produce versión1; UPDATE B.version+1 y conserva foreign/sentinels y recibos/sends históricos.
- RV17–RV20: controles de identidad/protocolo, EOF/salida normal/timeout reducido, ownership restaurado, inputs/raw/IDs/skips/residuos y budgets. Los dos SIGKILL de timeout negativo no acreditan caída/reinicio del producto.

## Matriz ejecutada

| Caso | Recorrido / modo | Familia / punto | Resultado |
|---|---|---|---|
| RV01 | T / CREATE | BEFORE_ISSUE / before_issue | PASS acotado |
| RV02 | T / UPDATE | BEFORE_ISSUE / before_issue | PASS acotado |
| RV03 | R / CREATE | BEFORE_ISSUE / before_issue | PASS acotado |
| RV04 | R / UPDATE | BEFORE_ISSUE / before_issue | PASS acotado |
| RV05 | T / CREATE | INFLIGHT_BEFORE_PUBLISH / before_object | PASS acotado |
| RV06 | T / UPDATE | INFLIGHT_BEFORE_PUBLISH / before_object | PASS acotado |
| RV07 | R / CREATE | INFLIGHT_BEFORE_PUBLISH / before_object | PASS acotado |
| RV08 | R / UPDATE | INFLIGHT_BEFORE_PUBLISH / before_object | PASS acotado |
| RV09 | T / CREATE | INFLIGHT_AFTER_COMMIT / after_head | PASS acotado |
| RV10 | T / UPDATE | INFLIGHT_AFTER_COMMIT / after_head | PASS acotado |
| RV11 | R / CREATE | INFLIGHT_AFTER_COMMIT / after_head | PASS acotado |
| RV12 | R / UPDATE | INFLIGHT_AFTER_COMMIT / after_head | PASS acotado |
| RV13 | T / CREATE | INFLIGHT_LOST_RESPONSE / after_head | PASS acotado |
| RV14 | T / UPDATE | INFLIGHT_LOST_RESPONSE / after_head | PASS acotado |
| RV15 | R / CREATE | INFLIGHT_LOST_RESPONSE / after_head | PASS acotado |
| RV16 | R / UPDATE | INFLIGHT_LOST_RESPONSE / after_head | PASS acotado |
| RV17 | T / NONE | PROTOCOL_OWNERSHIP / CONTROL | PASS acotado |
| RV18 | R / NONE | PROTOCOL_OWNERSHIP / CONTROL | PASS acotado |
| RV19 | T / NONE | INVENTORY_RAW / CONTROL | PASS acotado |
| RV20 | R / NONE | INVENTORY_RAW / CONTROL | PASS acotado |

## Integridad, desarrollo y recursos

RV registra 128 inputs actuales idénticos antes/después. Las regresiones conservan sus conjuntos efectivos: Python78, HC89, HF98, IC107 y UQ118. Los sellos I51/I50/I49/I48/I46/I44/I42/I40 mantienen sus hashes. Producto, APIs, harness históricos, handoff y registro I38 intactos. Fuente/símbolo/línea/hash, método, escenario, evento y oráculo se resuelven en el JSON; cada secuencia integra sus propias identidades, no se deduce integración desde la suma de PASS.

RV crea 32 raíces propias y 174 hijos: 172 salidas0 y dos SIGKILL de timeout negativo. Cero raíces/hijos/hilos propios restantes. Recursos de las cinco regresiones se conservan en cada raw/contexto/sello, sin mezclarlos con RV o certificación del host operativo. Lectores nuevos comparan HEAD/estado íntegro y comprueban cero llamadas de transporte en apertura pasiva.

La primera campaña completa RV20 pasó. La revisión de su evidencia motivó registrar explícitamente pins de autoridad I26/SOURCE/EVALUATION/EFFECT en T y SOURCE/BATCH/recibo/selección en R; RV20 se reejecutó con esos metadatos y pasó. Se conserva el stdout final exacto; el preliminar no se versiona ni suma. No se observaron fallos funcionales. Las regresiones no se repitieron porque sus entradas efectivas no incluyen el nuevo módulo RV y permanecieron iguales.

## Revisión preparada y pendientes

CP01/CP05 queda **PREPARED_FOR_SUFFICIENCY_REVIEW**, no aceptado automáticamente: se preservan 84 inputs históricos I32 frente a su commit y los dos índices cambiados se distinguen de pérdida de integridad. Se catalogan targets/grupos públicos D3/D4/A52 y carencias explícitas de inventario D1/D2; sin SQL/Java/Docker o reapertura de cierres.

Para UI33.2 se conservan UI33 original, DF37, la descomposición I40, el dictamen I48 y punteros de IC30 I52. Exigir dos tickets distintos efectivamente autorizados necesita contraste con el requisito normativo y la guarda de una emisión no resuelta; no se elimina DF37 ni se eleva el ticket extra no emitido de IC21–IC24. La preparación no cambia PARTIAL ni acepta suficiencia.

**UI30.2 dispone de evidencia nueva acotada; su revisión de suficiencia global sigue pendiente.** I48 y sus diez partes parciales permanecen como baseline histórico, sin promoción automática. Fuera de RV: revocaciones SOURCE/BATCH/EVALUATION, origen/cuenta/perfil/política, variantes relacionales UI34.3, nuevas caídas/F1–F7 y ambigüedad nativa H07.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado conservados. D5 global, G01–G07 y los cinco GI abiertos, sin promover 30/35. Los siete requisitos reales/humanos conservan su puerta de decisión; no se eliminan ni se trasladan a D6. Sin proveedores/credenciales/corpus real, consumo/reservas, activación, promoción, despliegue, auditor o D6.

La publicación continúa pendiente de confirmación inequívoca del destino/rango: los dos push previos fueron rechazados automáticamente antes de ejecutarse. A sobre I51 autoriza I52, no equivale al Sí de publicación solicitado. No se intentó otro push en I52 ni se eludió el bloqueo. El commit local resultante no se declara publicado.
