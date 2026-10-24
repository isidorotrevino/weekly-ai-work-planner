# D5 I46 — resultados acotados de doble ISSUE/CREATE

Fecha: **2026-10-24**, Europe/Madrid. **PASS de campaña sintética acotada**.
Base autorizada: `7af5362f2aad0513ccd2a655aa212a5e731eae54`; selección A del usuario para implementar/validar I45.
[Laboratorio](../design/D5-I46-DURABLE-ISSUE-CREATE-LAB.md) · [Contrato](../design/D5-I45-DURABLE-ISSUE-CREATE-DESIGN.md) · [Matriz prevista](../design/D5-I45-DURABLE-ISSUE-CREATE-REVIEW.md) · [Sello](D5-I46-results.json).

## Resultados y contabilidad

| Campaña independiente | Tests distintos | Resultado | Evidencia nueva |
|---|---:|---|---|
| IC propia | 30 | PASS | [Raw IC](D5-I46-raw.json) |
| Regresión HC de I42 | 24 | PASS | [Raw HC](D5-I46-HC-regression-raw.json), [contexto](D5-I46-HC-regression-context.json) |
| Regresión HF de I44 | 40 | PASS | [Raw HF](D5-I46-HF-regression-raw.json), [contexto](D5-I46-HF-regression-context.json) |
| Regresión Python histórica | 321 | PASS | [Raw Python](D5-I46-Python-regression-raw.json), [contexto](D5-I46-Python-regression-context.json) |

Los 31 escenarios IC proceden de IC29 en T y R. Son 24 carreras con orden forzado (doce pares de familia/recorrido, ambas ordenaciones), cuatro negativas seriales y dos tests transversales. Actores, retornos, probes, lecturas y comprobaciones de desarrollo no se cuentan como tests adicionales. Los cuatro grupos tienen IDs distintos y se conservan separados; su suma no constituye evidencia integrada global. Los “new_tests=40” del runner histórico son DR de I36, regresiones en I46.

## Resultados por autoridad

- IC01–IC04: mismo cid/request devuelve un único recibo nuevo y otro histórico idéntico; no son dos emisiones.
- IC05–IC12: cid distintos compiten con HEAD común; el perdedor falla CONFLICT_HEAD. Su petición posterior con HEAD fresca falla BINDING_UNRESOLVED sin recibo/ticket nuevo.
- IC13–IC16: mismo cid con tickets/request distintos produce COMMAND_CONFLICT antes de CAS. No se confunde con conflicto de HEAD.
- En las dieciséis filas CLIENT, solo el ticket ganador emitido se ejecuta una vez. Reconcile nueva observa P con lookup=1/execute=0 y ledger 2. Replay del ISSUE original devuelve recibo UNKNOWN histórico sin rebobinar HEAD, revisión, TASK o ledger EFFECT_CONFIRMED/2.
- IC17–IC20: dos execute del mismo ticket emitido devuelven P idéntica con un único commit/recibo/ticket/entidad REMOTE versión 1. Read_command contrasta el recibo; no se inventa flag historical en el retorno de execute. Reconcile posterior conserva REMOTE.
- IC21–IC24: T0 emitido y T1 extra no emitido compiten solo en REMOTE. El primero confirma, el segundo NO_EFFECT/CREATION_KEY_CONFLICT/retry_tick=None; dos recibos/tickets y una entidad versión 1. **No hay reconcile ni adopción en CLIENT**: permanece UNKNOWN/ledger 1, única tentativa T0. Si gana T1, su efecto nunca se presenta como éxito de T0. Estas cuatro filas no acreditan dos envíos autorizados, autenticación de tickets o recuperación integrada.
- IC25–IC28: paquete mutado serial produce TICKET_CONFLICT, K falsa produce REMOTE_SCOPE y read_command con hash falso COMMAND_CONFLICT, sin efectos adicionales. Paquetes negativos no reciben revisión o autoridad.
- IC29/IC30: controles de protocolo/probe/EOF/salida/timeout, inodo/marker/sentinel/enlace, inputs/raw/límites y contabilidad. Los dos SIGKILL de timeout negativo no son fronteras positivas de recuperación.

## Matriz ejecutada

Los IDs exactos están en `case_test_map` del raw y en el sello. Las UI del contrato son objetivos parciales, sin dictamen automático de suficiencia.

| IC | Recorrido / familia | Orden / tipo | Oráculos de archivos | Resultado |
|---|---|---|---:|---|
| IC01 | T / C1_EXACT | A_FIRST / FORCED_PROCESS_ORDER | 11 | PASS acotado |
| IC02 | T / C1_EXACT | B_FIRST / FORCED_PROCESS_ORDER | 11 | PASS acotado |
| IC03 | R / C1_EXACT | A_FIRST / FORCED_PROCESS_ORDER | 11 | PASS acotado |
| IC04 | R / C1_EXACT | B_FIRST / FORCED_PROCESS_ORDER | 11 | PASS acotado |
| IC05 | T / C2_DISTINCT | A_FIRST / FORCED_PROCESS_ORDER | 12 | PASS acotado |
| IC06 | T / C2_DISTINCT | B_FIRST / FORCED_PROCESS_ORDER | 12 | PASS acotado |
| IC07 | R / C2_DISTINCT | A_FIRST / FORCED_PROCESS_ORDER | 12 | PASS acotado |
| IC08 | R / C2_DISTINCT | B_FIRST / FORCED_PROCESS_ORDER | 12 | PASS acotado |
| IC09 | T / C3_BUSINESS_REPEAT | A_FIRST / FORCED_PROCESS_ORDER | 12 | PASS acotado |
| IC10 | T / C3_BUSINESS_REPEAT | B_FIRST / FORCED_PROCESS_ORDER | 12 | PASS acotado |
| IC11 | R / C3_BUSINESS_REPEAT | A_FIRST / FORCED_PROCESS_ORDER | 12 | PASS acotado |
| IC12 | R / C3_BUSINESS_REPEAT | B_FIRST / FORCED_PROCESS_ORDER | 12 | PASS acotado |
| IC13 | T / C4_COMMAND_COLLISION | A_FIRST / FORCED_PROCESS_ORDER | 12 | PASS acotado |
| IC14 | T / C4_COMMAND_COLLISION | B_FIRST / FORCED_PROCESS_ORDER | 12 | PASS acotado |
| IC15 | R / C4_COMMAND_COLLISION | A_FIRST / FORCED_PROCESS_ORDER | 12 | PASS acotado |
| IC16 | R / C4_COMMAND_COLLISION | B_FIRST / FORCED_PROCESS_ORDER | 12 | PASS acotado |
| IC17 | T / R1_ISSUED_DELIVERY_REPEAT | A_FIRST / FORCED_PROCESS_ORDER | 12 | PASS acotado |
| IC18 | T / R1_ISSUED_DELIVERY_REPEAT | B_FIRST / FORCED_PROCESS_ORDER | 12 | PASS acotado |
| IC19 | R / R1_ISSUED_DELIVERY_REPEAT | A_FIRST / FORCED_PROCESS_ORDER | 12 | PASS acotado |
| IC20 | R / R1_ISSUED_DELIVERY_REPEAT | B_FIRST / FORCED_PROCESS_ORDER | 12 | PASS acotado |
| IC21 | T / R2_REMOTE_ONLY_EXTRA_UNISSUED_TICKET | A_FIRST / FORCED_PROCESS_ORDER_REMOTE_NEGATIVE | 8 | PASS acotado |
| IC22 | T / R2_REMOTE_ONLY_EXTRA_UNISSUED_TICKET | B_FIRST / FORCED_PROCESS_ORDER_REMOTE_NEGATIVE | 8 | PASS acotado |
| IC23 | R / R2_REMOTE_ONLY_EXTRA_UNISSUED_TICKET | A_FIRST / FORCED_PROCESS_ORDER_REMOTE_NEGATIVE | 8 | PASS acotado |
| IC24 | R / R2_REMOTE_ONLY_EXTRA_UNISSUED_TICKET | B_FIRST / FORCED_PROCESS_ORDER_REMOTE_NEGATIVE | 8 | PASS acotado |
| IC25 | T / MUTATED_REQUEST_AFTER_VALID_CREATE | VALID_CREATE_THEN_MUTATION / CONTROLLED_NEGATIVE_SEQUENCE | 6 | PASS acotado |
| IC26 | R / MUTATED_REQUEST_AFTER_VALID_CREATE | VALID_CREATE_THEN_MUTATION / CONTROLLED_NEGATIVE_SEQUENCE | 6 | PASS acotado |
| IC27 | T / BAD_KEY_AND_COMMAND_HASH | SERIAL_NEGATIVES / CONTROLLED_NEGATIVE_SEQUENCE | 6 | PASS acotado |
| IC28 | R / BAD_KEY_AND_COMMAND_HASH | SERIAL_NEGATIVES / CONTROLLED_NEGATIVE_SEQUENCE | 6 | PASS acotado |
| IC29 | T, R / PROTOCOL_OWNERSHIP | CONTROL_NEGATIVES / TRANSVERSE_CONTROL | 6 | PASS acotado |
| IC30 | R / EVIDENCE_COUNTS | PRE_POST_RAW_REPORT / TRANSVERSE_CONTROL | 2 | PASS acotado |

## Integridad, recursos y desarrollo

IC conserva 107 inputs antes/después idénticos y actuales. Las regresiones conservan sus inventarios pertinentes, también idénticos antes/después y actuales: HC89, HF98 y Python78. No se incluyen los archivos I46 como dependencias ejecutadas por los runners anteriores. Los 25 inputs I45; 100 inputs/cinco artefactos I44; 26 inputs I43; 91 inputs/cinco artefactos I42; 42 inputs/tres documentos I40 siguen coincidiendo. Producto, suites/runners anteriores, I42/I44, registro I38 y handoff no cambian.

Recursos IC: 47 raíces propias y 210 hijos; 208 salidas normales y dos SIGKILL de timeout negativo. Cero raíces/hijos/hilos propios restantes. HC separado: 38 raíces/50 hijos; HF separado: 47 raíces/207 hijos; Python separado: 141 raíces R, 310 T, 33 captura, 86/149/7 hijos y 13 hilos. Todos los grupos declaran cero restantes. Estos conteos no inspeccionan ni certifican el host operativo.

El lector independiente I42 reutilizado comprueba archivos/cadena/hash/recibos; una lectura nueva y apertura pública pasiva final conservan HEAD/estado sin emitir/ejecutar/conciliar. El probe solo acredita lock observado; no prueba que el flock bloqueante ya empezó. Los hashes de retornos y oráculos se ligan a cid/request/manifest/ticket/procedencia/versión y al código sellado. No se restauró autoridad desde memoria ni se escribió HEAD/estado desde el harness.

Seis pruebas focalizadas y una campaña preliminar IC de 30 tests pasaron en desarrollo. Se consolidaron las lecturas pasivas duplicadas de R2 manteniendo la lectura independiente y apertura pública finales de cada caso; se reforzó el contraste de identidad de la prueba NO_EFFECT. La campaña IC final revalida esos cambios y conserva su stdout completo en JSON compacto, bajo el umbral del chequeo de publicación. Los stdout preliminares no están versionados, no se suman ni acreditan aplicabilidad actual. No se observaron fallos de pruebas en estas comprobaciones.

## Pendientes y política

DF37 y otros controles ya cubrían secuencias de ticket/identidad: no se presentan treinta lagunas inéditas. El alcance añade ordenaciones específicas y oráculos separados de autoridad. Fuera quedan paquetes aprobados distintos, targets válidos distintos, UPDATE/CLOSE, otras revocaciones/cuenta/perfil/origen/grooming, nuevas caídas H02, H07 y límites históricos H04/H05; energía/disco/NFS/Windows/caller hostil. El raw original I34/I36 permanece NOT_RECORDED. H03 no se cierra globalmente por estas cifras.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. D5 global, G01–G07 y revisión global GI33/GI34/GI38/GI39/GI40 abiertos; sin promoción 30/35→35/35 o persistencia/recuperación integrada inferida de PASS aislados. Sin proveedores/credenciales reales, corpus privado, consumo/reservas, activación, promoción, despliegue, SQL/Java/Docker o D6. Sin inspección/limpieza de dev/run_data/D4 operativo.

P0 vigente: I32, handoff y posteriores sin publicar. El commit local I46 no autoriza push. Una eventual publicación necesita decisión separada sobre SHA exacto y comprobación de remoto, ascendencia y diff. No se consultó de nuevo el remoto en este corte.
