# D5 I62 — suficiencia de la matriz finita T/R v1

Fecha: **2026-10-25**. [Dictamen](D5-I62-results.md) · [Fuentes y punteros por celda](D5-I62-results.json).

B=SUPPORTS_BOUNDED dentro del contrato I57 y los estados/variantes declarados. **140 B** no significa 140 tests nuevos ni aceptación global. Las 101 celdas I59 conservan su soporte; las otras 39 se contrastan contra I61.

| FL / path / frontera | Operación / modo | before_object | after_object | before_replace | after_head | Evidencia nueva / conservada |
|---|---|---|---|---|---|---|
| FL01 / T / F1 | IMPORT / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL02 / T / F2 | REVIEW_SOURCE_ACCEPT / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL03 / T / F2 | PREPARE_EVALUATION / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL04 / T / F2 | REVIEW_EVALUATION_ACCEPT / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL05 / T / F2 | PREPARE_EFFECT / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL06 / T / F2 | REVIEW_EFFECT_ACCEPT / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL07 / T / F3 | APPLY / LOCAL | B | B | B | B | CE01, CE02, CE03 |
| FL08 / T / F4 | BIND / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL09 / T / F4 | PREPARE_PROJECTION / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL10 / T / F4 | REVIEW_PROJECTION_ACCEPT / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL11 / T / F5 | ISSUE / CREATE | B | B | B | B | CE04, CE05, CE06, CE07 |
| FL12 / T / F6 | EXECUTE / CREATE | B | B | B | B | CE08, CE09, CE10, CE11 |
| FL13 / T / F6 | EXECUTE / UPDATE | B | B | B | B | CE12, CE13, CE14, CE15 |
| FL14 / T / F6 | CLOSE / CLOSE | B | B | B | B | CE16, CE17, CE18, CE19 |
| FL15 / T / F7 | QUERY / CREATE | B | B | B | B | CE20, CE21, CE22, CE23 |
| FL16 / T / F7 | RESULT_DISPATCH / CREATE | B | B | B | B | CE24, CE25, CE26, CE27 |
| FL17 / T / F7 | RESULT_QUERY / CREATE | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL18 / R / F1 | CAPTURE / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL19 / R / F1 | SELECT_SOURCE / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL20 / R / F2 | PREPARE_SOURCE / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL21 / R / F2 | REVIEW_SOURCE_ACCEPT / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL22 / R / F2 | PREPARE_BATCH / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL23 / R / F2 | REVIEW_BATCH_ACCEPT / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL24 / R / F3 | APPLY_BATCH / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL25 / R / F4 | SELECT_TASKS / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL26 / R / F4 | BIND / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL27 / R / F4 | PREPARE_PROJECTION / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL28 / R / F4 | REVIEW_PROJECTION_ACCEPT / LOCAL | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL29 / R / F5 | ISSUE / CREATE | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL30 / R / F6 | EXECUTE / CREATE | B | B | B | B | CE28, CE29, CE30, CE31 |
| FL31 / R / F6 | EXECUTE / UPDATE | B | B | B | B | CE32, CE33, CE34, CE35 |
| FL32 / R / F6 | CLOSE / CLOSE | B | B | B | B | CE36, CE37, CE38, CE39 |
| FL33 / R / F7 | QUERY / CREATE | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL34 / R / F7 | RESULT_DISPATCH / CREATE | B | B | B | B | I59 conservada; hash/puntero verificado |
| FL35 / R / F7 | RESULT_QUERY / CREATE | B | B | B | B | I59 conservada; hash/puntero verificado |

FL07 conserva after_head HF31 y añade CE01–CE03. FL11/FL15/FL16 sustituyen la carencia de raw causal mediante CE propios, sin reescribir metadata I34. FL12–FL14/FL30–FL32 añaden modo y operación de manifiesto explícitos, sin reetiquetar registros históricos.

Cortes lógicos (12) y exclusiones tipadas (6) conservados por referencia. OSError y fases CORE nativas fuera de la matriz no se declaran acreditados por B. Las 83 partes no dirigidas heredan I59; sólo UI22.2 se reevalúa. GI global y G01–G07 siguen abiertos.
