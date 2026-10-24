# D5 I51 — matriz de revocación en vuelo

Fecha: **2026-10-24**. **PREPARED_FOR_REVIEW**. [Contrato](D5-I51-INFLIGHT-REVOCATION-DESIGN.md) · [Plan de cierre](D5-I51-CLOSURE-PLAN.md) · [Sello](../validation/D5-I51-design-review.json).

RV01–RV20: todos **NOT_RUN / NOT_REVIEWED**. No son resultados; cada fila tiene path y modo propios. UPDATE conserva baseline histórico y compara únicamente la nueva tentativa.

| ID | Recorrido / modo | Familia | Punto real / pérdida de respuesta | Oráculo exigido |
|---|---|---|---|---|
| RV01 | T / CREATE | BEFORE_ISSUE | before_issue / False | REVIEW v2 confirmada antes de ISSUE; dispatch REVIEW_REQUIRED; no nuevo intento, recibo o efecto frente al baseline. |
| RV02 | T / UPDATE | BEFORE_ISSUE | before_issue / False | REVIEW v2 confirmada antes de ISSUE; dispatch REVIEW_REQUIRED; no nuevo intento, recibo o efecto frente al baseline. |
| RV03 | R / CREATE | BEFORE_ISSUE | before_issue / False | REVIEW v2 confirmada antes de ISSUE; dispatch REVIEW_REQUIRED; no nuevo intento, recibo o efecto frente al baseline. |
| RV04 | R / UPDATE | BEFORE_ISSUE | before_issue / False | REVIEW v2 confirmada antes de ISSUE; dispatch REVIEW_REQUIRED; no nuevo intento, recibo o efecto frente al baseline. |
| RV05 | T / CREATE | INFLIGHT_BEFORE_PUBLISH | before_object / False | ISSUE UNKNOWN/1; Remote.execute real pausado en before_object; REVIEW v2 confirma en CLIENT; liberación; RESULT P EFFECT_CONFIRMED/2 con vigencia STALE, un único efecto de este ticket y sin reenviar. |
| RV06 | T / UPDATE | INFLIGHT_BEFORE_PUBLISH | before_object / False | ISSUE UNKNOWN/1; Remote.execute real pausado en before_object; REVIEW v2 confirma en CLIENT; liberación; RESULT P EFFECT_CONFIRMED/2 con vigencia STALE, un único efecto de este ticket y sin reenviar. |
| RV07 | R / CREATE | INFLIGHT_BEFORE_PUBLISH | before_object / False | ISSUE UNKNOWN/1; Remote.execute real pausado en before_object; REVIEW v2 confirma en CLIENT; liberación; RESULT P EFFECT_CONFIRMED/2 con vigencia STALE, un único efecto de este ticket y sin reenviar. |
| RV08 | R / UPDATE | INFLIGHT_BEFORE_PUBLISH | before_object / False | ISSUE UNKNOWN/1; Remote.execute real pausado en before_object; REVIEW v2 confirma en CLIENT; liberación; RESULT P EFFECT_CONFIRMED/2 con vigencia STALE, un único efecto de este ticket y sin reenviar. |
| RV09 | T / CREATE | INFLIGHT_AFTER_COMMIT | after_head / False | ISSUE UNKNOWN/1; Remote.execute real pausado en after_head; REVIEW v2 confirma en CLIENT; liberación; RESULT P EFFECT_CONFIRMED/2 con vigencia STALE, un único efecto de este ticket y sin reenviar. |
| RV10 | T / UPDATE | INFLIGHT_AFTER_COMMIT | after_head / False | ISSUE UNKNOWN/1; Remote.execute real pausado en after_head; REVIEW v2 confirma en CLIENT; liberación; RESULT P EFFECT_CONFIRMED/2 con vigencia STALE, un único efecto de este ticket y sin reenviar. |
| RV11 | R / CREATE | INFLIGHT_AFTER_COMMIT | after_head / False | ISSUE UNKNOWN/1; Remote.execute real pausado en after_head; REVIEW v2 confirma en CLIENT; liberación; RESULT P EFFECT_CONFIRMED/2 con vigencia STALE, un único efecto de este ticket y sin reenviar. |
| RV12 | R / UPDATE | INFLIGHT_AFTER_COMMIT | after_head / False | ISSUE UNKNOWN/1; Remote.execute real pausado en after_head; REVIEW v2 confirma en CLIENT; liberación; RESULT P EFFECT_CONFIRMED/2 con vigencia STALE, un único efecto de este ticket y sin reenviar. |
| RV13 | T / CREATE | INFLIGHT_LOST_RESPONSE | after_head / True | ISSUE UNKNOWN/1; Remote.execute real pausado en after_head; REVIEW v2 confirma en CLIENT; liberación; RESULT(None) UNKNOWN/2 sin pending send; lector pasivo sin consulta; reconcile explícita ledger3/queries1 confirma P con vigencia STALE. |
| RV14 | T / UPDATE | INFLIGHT_LOST_RESPONSE | after_head / True | ISSUE UNKNOWN/1; Remote.execute real pausado en after_head; REVIEW v2 confirma en CLIENT; liberación; RESULT(None) UNKNOWN/2 sin pending send; lector pasivo sin consulta; reconcile explícita ledger3/queries1 confirma P con vigencia STALE. |
| RV15 | R / CREATE | INFLIGHT_LOST_RESPONSE | after_head / True | ISSUE UNKNOWN/1; Remote.execute real pausado en after_head; REVIEW v2 confirma en CLIENT; liberación; RESULT(None) UNKNOWN/2 sin pending send; lector pasivo sin consulta; reconcile explícita ledger3/queries1 confirma P con vigencia STALE. |
| RV16 | R / UPDATE | INFLIGHT_LOST_RESPONSE | after_head / True | ISSUE UNKNOWN/1; Remote.execute real pausado en after_head; REVIEW v2 confirma en CLIENT; liberación; RESULT(None) UNKNOWN/2 sin pending send; lector pasivo sin consulta; reconcile explícita ledger3/queries1 confirma P con vigencia STALE. |
| RV17 | T / NONE | PROTOCOL_OWNERSHIP | CONTROL / False | Negativos READY/rol/operación/modo/stage/punto/run/store/cid, EOF/salida normal/timeout reducido y ownership inode/marker/sentinel/link restaurados antes de limpieza propia. |
| RV18 | R / NONE | PROTOCOL_OWNERSHIP | CONTROL / False | Negativos READY/rol/operación/modo/stage/punto/run/store/cid, EOF/salida normal/timeout reducido y ownership inode/marker/sentinel/link restaurados antes de limpieza propia. |
| RV19 | T / NONE | INVENTORY_RAW | CONTROL / False | Inputs cambiados/añadidos, raw ausente/incompatible/hash, mapas duplicados/incompletos/skips/residuos y budgets negativos; regressiones separadas; no PASS heredado. |
| RV20 | R / NONE | INVENTORY_RAW | CONTROL / False | Inputs cambiados/añadidos, raw ausente/incompatible/hash, mapas duplicados/incompletos/skips/residuos y budgets negativos; regressiones separadas; no PASS heredado. |

## Alcance de la conclusión futura

UI30.2 podrá recibir valoración acotada después de fuente/oráculos/raw revisados. No implica cierre H03/GI39, revocación SOURCE/BATCH/EVALUATION, cambios de origen/cuenta/perfil, variaciones relacionales, cada frontera F1–F7 o dos tickets autorizados distintos. R conserva su propia autoridad.

Un hook before_object/after_head sólo sirve si está armado dentro de Remote.execute real del ticket activo. El checkpoint CLIENT after_remote y un wrapper pausado antes de invocar execute quedan excluidos como evidencia de durante-la-llamada.

Regresiones previstas separadas: Python321, HC24, HF40, IC30, UQ24. D1–D4 cerrados y A52 aceptado intactos; D5 global/G01–G07 abiertos. Publicación pendiente separada, sin proveedores/credenciales reales, consumo/reservas, activación, promoción, despliegue o D6.
