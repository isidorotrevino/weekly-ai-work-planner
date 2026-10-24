# D5 I44 — resultados acotados de fronteras H02

Fecha: **2026-10-24**, Europe/Madrid. **PASS de campaña sintética acotada**.
Base autorizada: `d34538adb8ad9e6c04208cd26ed1072654beddc0`; selección A del usuario para implementar/validar I43.
[Laboratorio](../design/D5-I44-DURABLE-CRASH-BOUNDARIES-LAB.md) · [Contrato](../design/D5-I43-DURABLE-CRASH-BOUNDARIES-DESIGN.md) · [Matriz prevista](../design/D5-I43-DURABLE-CRASH-BOUNDARIES-REVIEW.md) · [Sello](D5-I44-results.json).

## Resultados y contabilidad

| Campaña independiente | Tests distintos | Resultado | Evidencia nueva |
|---|---:|---|---|
| HF propia | 40 | PASS | [Raw HF](D5-I44-raw.json) |
| Regresión HC de I42 | 24 | PASS | [Raw HC](D5-I44-HC-regression-raw.json), [contexto](D5-I44-HC-regression-context.json) |
| Regresión Python histórica | 321 | PASS | [Raw Python](D5-I44-Python-regression-raw.json), [contexto](D5-I44-Python-regression-context.json) |

Los 41 escenarios HF corresponden a HF39 en T y R; no son 41 tests. Se registran 32 fronteras positivas con SIGKILL y seis filas de falla I/O con doce eventos OSError. Los dos SIGKILL adicionales de timeout negativo HF39 no cuentan como fronteras de recuperación. Filas, escenarios, lectores, eventos y comprobaciones de desarrollo no se suman como tests. Los grupos tienen IDs distintos y se mantienen separados; no se presenta su suma como evidencia integrada global. Los “new_tests=40” del runner histórico pertenecen a DR de I36: en I44 los 321 son regresiones existentes.

## Observaciones y límites de la novedad

- HF01–HF24: seis operaciones/stages tempranos R por cuatro puntos. Antes de publicar HEAD se conserva estado/recibo anteriores, aunque haya objeto huérfano o HEAD temporal. After_head conserva un commit/recibo exactos. Lectura pasiva no cambia nada; replay explícito confirma una vez o devuelve historia sin duplicar.
- HF25–HF30: OSError en directory_fsync deja COMMIT_UNKNOWN y CLIENT no reutilizable; otro CLIENT con recovery_fsync fallido también bloquea. Nuevo CLIENT sin fault valida/fsync el commit visible. Son fallas sintéticas, sin caída física de disco/energía.
- HF31/HF32: APPLY/APPLY_BATCH ya confirmados sobreviven al SIGKILL antes de binding/proyección. Recibo/replay no fabrican fases o proyección; la continuación explícita produce proyección revisada de la TASK exacta sin ISSUE. T termina data_generation 2 por APPLY y BIND; R permanece 1. No es segunda aplicación.
- HF33–HF38: al gate y después de reapertura pasiva se acredita UNKNOWN, ledger 1 y proof=None. Se diferencia execute retornado, lookup retornado y QUERY previa a lookup. Solo reconcile nueva publica P exacta, ledger 2 y queries 1/2; vacía pendientes con lookup=1, execute=0, sin cambiar REMOTE.
- HF39/HF40: negativas reales de gate/identidad/EOF/salida normal/timeout, inodo/marker/sentinel/enlace, cambio/adición de inputs, raw faltante/incompatible/hash errado, salida/eventos y contabilidad. Fallos de control no se convierten en PASS de recuperación.

DF20/DR26 ya cubrían after_remote y DF21 before_result desde UNKNOWN en T: HF33–HF35 son controles con trazabilidad nueva. HF36 exige la primera reconcile R desde UNKNOWN, distinto de la segunda caída de DR26 después de confirmar. Los hooks APPLY after_head ya existían; HF31/32 amplían oráculo y continuación. No se presentan cuarenta lagunas históricas inéditas ni se reescribe I40/I42.

## Matriz ejecutada

Cada fila se resuelve al ID exacto indicado por `case_test_map` del raw y a sus eventos/oráculos. UI son objetivos parciales del contrato.

| HF | Recorrido / operación / stage | Punto / modo | Oráculos de archivos | Resultado |
|---|---|---|---:|---|
| HF01 | R / CAPTURE / SOURCE | before_object / LOCAL | 8 | PASS acotado |
| HF02 | R / CAPTURE / SOURCE | after_object / LOCAL | 8 | PASS acotado |
| HF03 | R / CAPTURE / SOURCE | before_replace / LOCAL | 8 | PASS acotado |
| HF04 | R / CAPTURE / SOURCE | after_head / LOCAL | 8 | PASS acotado |
| HF05 | R / SELECT_SOURCE / SOURCE | before_object / LOCAL | 8 | PASS acotado |
| HF06 | R / SELECT_SOURCE / SOURCE | after_object / LOCAL | 8 | PASS acotado |
| HF07 | R / SELECT_SOURCE / SOURCE | before_replace / LOCAL | 8 | PASS acotado |
| HF08 | R / SELECT_SOURCE / SOURCE | after_head / LOCAL | 8 | PASS acotado |
| HF09 | R / PREPARE_SOURCE / SOURCE | before_object / LOCAL | 8 | PASS acotado |
| HF10 | R / PREPARE_SOURCE / SOURCE | after_object / LOCAL | 8 | PASS acotado |
| HF11 | R / PREPARE_SOURCE / SOURCE | before_replace / LOCAL | 8 | PASS acotado |
| HF12 | R / PREPARE_SOURCE / SOURCE | after_head / LOCAL | 8 | PASS acotado |
| HF13 | R / REVIEW / SOURCE | before_object / LOCAL | 8 | PASS acotado |
| HF14 | R / REVIEW / SOURCE | after_object / LOCAL | 8 | PASS acotado |
| HF15 | R / REVIEW / SOURCE | before_replace / LOCAL | 8 | PASS acotado |
| HF16 | R / REVIEW / SOURCE | after_head / LOCAL | 8 | PASS acotado |
| HF17 | R / PREPARE_BATCH / BATCH | before_object / LOCAL | 8 | PASS acotado |
| HF18 | R / PREPARE_BATCH / BATCH | after_object / LOCAL | 8 | PASS acotado |
| HF19 | R / PREPARE_BATCH / BATCH | before_replace / LOCAL | 8 | PASS acotado |
| HF20 | R / PREPARE_BATCH / BATCH | after_head / LOCAL | 8 | PASS acotado |
| HF21 | R / REVIEW / BATCH | before_object / LOCAL | 8 | PASS acotado |
| HF22 | R / REVIEW / BATCH | after_object / LOCAL | 8 | PASS acotado |
| HF23 | R / REVIEW / BATCH | before_replace / LOCAL | 8 | PASS acotado |
| HF24 | R / REVIEW / BATCH | after_head / LOCAL | 8 | PASS acotado |
| HF25 | R / CAPTURE / SOURCE | directory_fsync + recovery_fsync / LOCAL | 8 | PASS acotado |
| HF26 | R / SELECT_SOURCE / SOURCE | directory_fsync + recovery_fsync / LOCAL | 8 | PASS acotado |
| HF27 | R / PREPARE_SOURCE / SOURCE | directory_fsync + recovery_fsync / LOCAL | 8 | PASS acotado |
| HF28 | R / REVIEW / SOURCE | directory_fsync + recovery_fsync / LOCAL | 8 | PASS acotado |
| HF29 | R / PREPARE_BATCH / BATCH | directory_fsync + recovery_fsync / LOCAL | 8 | PASS acotado |
| HF30 | R / REVIEW / BATCH | directory_fsync + recovery_fsync / LOCAL | 8 | PASS acotado |
| HF31 | T / APPLY / EFFECT | after_head / LOCAL | 10 | PASS acotado |
| HF32 | R / APPLY_BATCH / BATCH | after_head / LOCAL | 10 | PASS acotado |
| HF33 | T / dispatch / PROJECTION | after_remote / CREATE | 7 | PASS acotado |
| HF34 | R / dispatch / PROJECTION | after_remote / CREATE | 7 | PASS acotado |
| HF35 | T / reconcile / PROJECTION | before_result / CREATE | 7 | PASS acotado |
| HF36 | R / reconcile / PROJECTION | before_result / CREATE | 7 | PASS acotado |
| HF37 | T / reconcile / PROJECTION | after_query / CREATE | 7 | PASS acotado |
| HF38 | R / reconcile / PROJECTION | after_query / CREATE | 7 | PASS acotado |
| HF39 | T, R / CONTROL / NONE | gate/exit/timeout / NONE | 2 | PASS acotado |
| HF40 | R / INVENTORY_REPORT / NONE | pre/post/raw/counts / NONE | 1 | PASS acotado |

## Integridad y recursos

Campaña propia: 98 inputs antes/después idénticos y actuales. HC: 89 inputs; Python histórica: 78; ambos grupos conservan sus propios inventarios pre/post idénticos y actuales. Los contextos no incluyen el código I44 como si fuera una dependencia ejecutada por las regresiones. Los 26 inputs de I43, 91 inputs y cinco artefactos I42, 20 inputs I41 y 42 inputs/tres documentos I40 permanecen idénticos. Producto, suites/runners históricos, I42, handoff y registro I38 no cambian.

Recursos HF: 47 raíces propias creadas y 207 hijos iniciados; 173 salidas normales y 34 por SIGKILL (32 fronteras, dos timeouts negativos). Cero hijos/hilos/raíces propios restantes. HC separado: 38 raíces y 50 hijos, cero restantes. Python separado: 141 raíces R, 310 T, 33 de captura; 86/149/7 hijos y 13 hilos; cero restantes. Estos conteos no inspeccionan ni certifican el host operativo.

El lector independiente se ejecuta en proceso nuevo, seguido de apertura pública pasiva en otro proceso y continuación explícita posterior. Las comprobaciones usan estados/recibos/pruebas/versiones y cadena desde disco; no restauran autoridad desde memoria ni toman un objeto huérfano como HEAD. Se conservan etiquetas de rol/operación/modo/stage/punto/ronda y conteos físicos separados de los alcanzables.

Seis pruebas focalizadas y una campaña preliminar HF de 40 tests pasaron durante desarrollo. Se ajustó únicamente la serialización stdout a JSON compacto para quedar bajo el umbral del chequeo de publicación; la campaña HF final revalida ese código y tiene el raw versionado enlazado. Los stdout preliminares no están versionados ni se suman o usan como autoridad de aplicabilidad actual. No se observaron fallos de pruebas en esas comprobaciones.

## Pendientes y política

La evidencia se limita a las filas del contrato. No acredita cada frontera F1–F7, todos los stages/modos, inicialización/corrupciones, pérdida de energía/disco, NFS/Windows/caller hostil o caída del REMOTE. La incertidumbre nueva solo usa CREATE; no se transfiere a UPDATE/CLOSE. Restantes H03/H07 y límites históricos H04/H05 siguen pendientes; raw I34/I36 original permanece NOT_RECORDED. H02 no se declara cerrado globalmente por sumar estos PASS.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado se conservan. D5 global, G01–G07 y revisión global de los cinco GI siguen abiertos; sin promoción 30/35→35/35 ni recuperación integrada inferida de PASS aislados. Sin proveedores/credenciales reales, corpus privado, consumo/reservas, activación, promoción, despliegue, SQL/Java/Docker o D6. Sin inspección/limpieza de dev/run_data/D4 operativo.

P0 vigente: no publicación de I32, handoff o posteriores. Un commit local de I44 no autoriza push. Una eventual publicación exige decisión separada sobre SHA exacto y comprobación de remoto, ascendencia y diff. No se ha consultado de nuevo el remoto en este corte.
