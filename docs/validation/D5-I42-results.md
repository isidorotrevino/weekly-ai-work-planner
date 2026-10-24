# D5 I42 — resultados acotados HC01–HC24

Fecha: **2026-10-24**, Europe/Madrid. **PASS de campaña sintética acotada**.
Base autorizada: `cd97028468236b78ffb5483f8e637a4075905687`; selección A del usuario para implementar/validar I41.
[Laboratorio](../design/D5-I42-DURABLE-CONCURRENCY-LAB.md) · [Contrato](../design/D5-I41-DURABLE-CONCURRENCY-DESIGN.md) · [Matriz prevista](../design/D5-I41-DURABLE-CONCURRENCY-REVIEW.md) · [Sello](D5-I42-results.json).

## Resultado y contabilidad

| Campaña | Tests distintos ejecutados | Resultado | Evidencia nueva |
|---|---:|---|---|
| Harness HC propio | 24 | PASS | [Raw propio](D5-I42-raw.json) |
| Regresión Python histórica separada | 321 | PASS | [Raw de regresión I42](D5-I42-regression-raw.json), [contexto](D5-I42-regression-context.json) |

Los 25 escenarios propios proceden de HC22 en T y R; no son 25 tests. Las 12 carreras tienen dos actores preparados, ganador bajo lock y probe del contendiente antes de liberar el commit. No se suman lectores, rondas, eventos o pruebas de desarrollo. El runner histórico llama “new_tests=40” a sus DR de I36; en I42 los 321 son regresiones existentes, separadas del harness nuevo. Ninguno equivale a evidencia de proveedor real.

## Observaciones comprobadas

- HC01–HC04: ambas ordenaciones respuesta/consulta en T/R. Un RESULT confirma y otro pierde CONFLICT_HEAD; un comando nuevo con HEAD fresca y ledger viejo falla CONFLICT_LEDGER sin recibo. Conciliación explícita posterior conserva P y llega a ledger 3 sin cambiar REMOTE.
- HC05–HC08: ambas ordenaciones RESULT/REVOKE. Se distingue el estado intermedio de la acción posterior; final EFFECT_CONFIRMED histórico + STALE y revisión REVOKE v2, sin ticket nuevo ni rollback remoto.
- HC09–HC12: EDIT primero deja UPDATE NO_EFFECT/REMOTE_PRECONDITION (HEAD +2, entidad +1); UPDATE primero confirma y EDIT viejo falla REMOTE_CAS (HEAD +1, entidad +1). Foreign permanece. El retry confirmado falla RETRY_FORBIDDEN; el no elegible por precondición falla RETRY_NOT_ELIGIBLE.
- HC13–HC20: CONFLICT persistente tras prueba incompatible; ABA de dos versiones y foreign invalidan base vieja; revocar antes de ISSUE impide send/ticket/efecto. ABA/foreign son secuencias controladas.
- HC21–HC24: controles negativos de protocolo, timeout reducido, inodo/marker/sentinel/enlace, inventario/eventos y contabilidad. Lectores independientes contrastan archivos y reapertura en proceso nuevo; no es una prueba de SIGKILL H02.

## Matriz ejecutada

Cada fila enlaza el ID de test exacto a los escenarios/oráculos/eventos del raw. UI son objetivos parciales de I41, sin dictamen automático de suficiencia.

| Caso | Recorrido | Test distinto | Observaciones de archivos | Resultado |
|---|---|---|---:|---|
| HC01 | T | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC01` | 7 | PASS |
| HC02 | T | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC02` | 7 | PASS |
| HC03 | R | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC03` | 7 | PASS |
| HC04 | R | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC04` | 7 | PASS |
| HC05 | T | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC05` | 6 | PASS |
| HC06 | T | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC06` | 6 | PASS |
| HC07 | R | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC07` | 6 | PASS |
| HC08 | R | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC08` | 6 | PASS |
| HC09 | T | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC09` | 6 | PASS |
| HC10 | T | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC10` | 6 | PASS |
| HC11 | R | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC11` | 6 | PASS |
| HC12 | R | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC12` | 6 | PASS |
| HC13 | T | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC13` | 4 | PASS |
| HC14 | R | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC14` | 4 | PASS |
| HC15 | T | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC15` | 5 | PASS |
| HC16 | R | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC16` | 5 | PASS |
| HC17 | T | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC17` | 4 | PASS |
| HC18 | R | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC18` | 4 | PASS |
| HC19 | T | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC19` | 4 | PASS |
| HC20 | R | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC20` | 4 | PASS |
| HC21 | T | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC21` | 1 | PASS |
| HC22 | T, R | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC22` | 2 | PASS |
| HC23 | R | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC23` | 1 | PASS |
| HC24 | R | `testing.durable_concurrency.test_durable_concurrency.DurableConcurrencyTest.test_HC24` | 1 | PASS |

## Integridad, recursos y alcance de la evidencia

La campaña propia selló 89 inputs antes/después, idénticos y actuales. La regresión conserva sus 78 inputs de ejecución idénticos a los bytes actuales. El contexto externo de regresión capturó además 89 archivos antes/después; tres archivos del harness nuevo cambiaron después para reforzar oráculos y etiquetas. Esos tres no forman parte del discovery ni de los 78 inputs de las 321 regresiones. No se presenta el conjunto contextual completo como CURRENT; el sello enumera las diferencias. La validación propia final sí corresponde a los bytes finales. No se repitió la regresión inalterada por esos cambios ajenos a su ejecución.

Recursos propios: 38 raíces creadas (incluye el temporal del control de inventario), 50 hijos iniciados, cero raíces/hijos/hilos vivos restantes. 49 hijos terminan con 0 y uno con SIGKILL en la negativa de timeout HC21; no se cuenta como recuperación. Regresión separada: 141 raíces R, 310 T, 33 de captura; 86/149/7 hijos respectivamente y 13 hilos; cero restantes en todos los grupos. Son recursos propios de estas campañas, no una inspección del host operativo.

Los 42 inputs públicos y tres documentos sellados en I40, y los 20 inputs del diseño I41, permanecen idénticos. Producto, suites/runners históricos, registro fijo I38 y documentos anteriores no cambian. No se ejecutaron SQL/Java/Docker ni campañas T/R adicionales al runner de regresión autorizado.

## Desarrollo y límites

Las comprobaciones de desarrollo no se suman al resultado final. Se conserva el [raw fallido de desarrollo](D5-I42-development-raw.json): 24 ejecutados, 22 PASS y HC10/HC12 fallidos por esperar RETRY_NOT_ELIGIBLE cuando correspondía RETRY_FORBIDDEN. Se corrigió solo el oráculo del harness. Un [raw intermedio PASS](D5-I42-development-pass-raw.json) conserva la primera campaña corregida; después se reforzaron lecturas independientes, controles de ownership y etiquetas antes de la campaña final. Estos snapshots de desarrollo no tienen todos sus bytes de fuente antiguos versionados y no acreditan aplicabilidad actual. El raw final y sus hashes son la evidencia de este corte.

Permanecen pendientes doble ISSUE/CREATE simultáneo, otras revocaciones y cambios concurrentes de cuenta/perfil/origen/grooming de H03, además de H02/H07. Raw histórico I34/I36 sigue NOT_RECORDED y su contexto histórico parcial no se reconstruye. El probe acredita lock observado, no la entrada efectiva en flock bloqueante. Linux local/spawn/flock/fsync/rename no acredita durabilidad ante corte de energía, discos/NFS/Windows o caller hostil.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado permanecen intactos. D5 global, G01–G07 y revisión global de los cinco GI siguen abiertos; sin promoción automática 30/35→35/35. No se deduce persistencia o recuperación integrada de PASS aislados. Sin proveedores/credenciales reales, corpus privado, consumo/reservas, activación, promoción, despliegue o D6.

P0 vigente: no publicación de I32, handoff ni posteriores. Cualquier publicación requiere una decisión separada sobre SHA exacto y comprobación previa de remoto, ascendencia y diff. El commit local de I42 no concede esa autorización.
