# D5 I41 — matriz de revisión HC01–HC24

Fecha: **2026-10-24**, Europe/Madrid. **PREPARED_FOR_REVIEW**.
Base: `900e837edfdd97d0b85f1b8c8b455f5797f24fa0`.
[Contrato](D5-I41-DURABLE-CONCURRENCY-DESIGN.md) ·
[Decisión A](D5-I41-NEXT-CUT-SCOPE.md) ·
[Sello documental](../validation/D5-I41-design-review.json).

Las 24 filas están **DESIGN_NOT_EXECUTED**: cero pruebas nuevas ejecutadas.
Son obligaciones de campaña propuesta, no 24 PASS ni necesariamente 24 tests.
La selección A autoriza este diseño; implementar/validar requiere la decisión
posterior sobre el contrato concreto. P0 sigue vigente.

## Lectura de estados y órdenes

L, V y U se definen íntegramente en el contrato. T conserva captura I26 y su
cadena de revisión; R conserva SOURCE/BATCH y selección de TASK desde lote.
No comparten autoridad por tener resultados parecidos. Las referencias UI son
objetivos parciales de trazabilidad; ninguna fila acredita la totalidad de una UI.

En HC01–HC12, dos procesos preparan entradas antes de competir y se fuerza cada
orden mediante los gates y probe del contrato. El lector independiente contrasta
HEAD/cadena/recibos/estado, P/base/versiones y conteos en puntos estables. Tras
terminar actores, un lector nuevo reabre desde disco; eso no prueba SIGKILL.

En L y V, perder por HEAD no acredita rechazo por ledger ni revocación confirmada.
Las rondas posteriores son comandos nuevos explícitos, nunca retry automático.
En U, EDIT usa Store.transact público con versión fijada; no se atribuye a la
fachada Remote.edit la elección de esa versión. UPDATE usa Remote.execute.

## Matriz propuesta

| Caso | Recorrido / objetivo UI parcial | Estado inicial | Orden / tipo | Oráculo obligatorio |
|---|---|---|---|---|
| HC01 | T; UI32, UI33 | L: UNKNOWN, ledger 1; QUERY confirmada, P remota, HEAD E común | RESULT directo primero; otro RESULT pierde HEAD; FORCED_PROCESS_ORDER | Ronda 1: ledger 2, P exacta, EFFECT_CONFIRMED, pendientes consumidos y un efecto. Ronda 2: HEAD fresca + ledger viejo → CONFLICT_LEDGER sin recibo/cambio. Ronda 3: reconcile nuevo → ledger 3, misma P y REMOTE intacto. |
| HC02 | T; UI32, UI33 | L: UNKNOWN, ledger 1; QUERY confirmada, P remota, HEAD E común | RESULT de reconcile primero; otro RESULT pierde HEAD; FORCED_PROCESS_ORDER | Ronda 1: ledger 2, P exacta, EFFECT_CONFIRMED, pendientes consumidos y un efecto. Ronda 2: HEAD fresca + ledger viejo → CONFLICT_LEDGER sin recibo/cambio. Ronda 3: reconcile nuevo → ledger 3, misma P y REMOTE intacto. |
| HC03 | R; UI32, UI33, UI34 | L: UNKNOWN, ledger 1; QUERY confirmada, P remota, HEAD E común | RESULT directo primero; otro RESULT pierde HEAD; FORCED_PROCESS_ORDER | Ronda 1: ledger 2, P exacta, EFFECT_CONFIRMED, pendientes consumidos y un efecto. Ronda 2: HEAD fresca + ledger viejo → CONFLICT_LEDGER sin recibo/cambio. Ronda 3: reconcile nuevo → ledger 3, misma P y REMOTE intacto. |
| HC04 | R; UI32, UI33, UI34 | L: UNKNOWN, ledger 1; QUERY confirmada, P remota, HEAD E común | RESULT de reconcile primero; otro RESULT pierde HEAD; FORCED_PROCESS_ORDER | Ronda 1: ledger 2, P exacta, EFFECT_CONFIRMED, pendientes consumidos y un efecto. Ronda 2: HEAD fresca + ledger viejo → CONFLICT_LEDGER sin recibo/cambio. Ronda 3: reconcile nuevo → ledger 3, misma P y REMOTE intacto. |
| HC05 | T; UI30, UI32, UI33 | V: UNKNOWN, P remota, PROJECTION ACCEPT v1, HEAD E común | RESULT primero; otro comando pierde HEAD; FORCED_PROCESS_ORDER | Separar ronda competida y acción posterior explícita: RESULT primero conserva CURRENT hasta REVOKE nuevo; REVOKE primero deja UNKNOWN/STALE hasta reconcile nuevo. Final histórico EFFECT_CONFIRMED + STALE, REVOKE v2, un efecto, ningún envío nuevo. |
| HC06 | T; UI30, UI32, UI33 | V: UNKNOWN, P remota, PROJECTION ACCEPT v1, HEAD E común | REVIEW REVOKE primero; otro comando pierde HEAD; FORCED_PROCESS_ORDER | Separar ronda competida y acción posterior explícita: RESULT primero conserva CURRENT hasta REVOKE nuevo; REVOKE primero deja UNKNOWN/STALE hasta reconcile nuevo. Final histórico EFFECT_CONFIRMED + STALE, REVOKE v2, un efecto, ningún envío nuevo. |
| HC07 | R; UI30, UI32, UI33, UI34 | V: UNKNOWN, P remota, PROJECTION ACCEPT v1, HEAD E común | RESULT primero; otro comando pierde HEAD; FORCED_PROCESS_ORDER | Separar ronda competida y acción posterior explícita: RESULT primero conserva CURRENT hasta REVOKE nuevo; REVOKE primero deja UNKNOWN/STALE hasta reconcile nuevo. Final histórico EFFECT_CONFIRMED + STALE, REVOKE v2, un efecto, ningún envío nuevo. |
| HC08 | R; UI30, UI32, UI33, UI34 | V: UNKNOWN, P remota, PROJECTION ACCEPT v1, HEAD E común | REVIEW REVOKE primero; otro comando pierde HEAD; FORCED_PROCESS_ORDER | Separar ronda competida y acción posterior explícita: RESULT primero conserva CURRENT hasta REVOKE nuevo; REVOKE primero deja UNKNOWN/STALE hasta reconcile nuevo. Final histórico EFFECT_CONFIRMED + STALE, REVOKE v2, un efecto, ningún envío nuevo. |
| HC09 | T; UI31, UI32, UI33 | U: entidad v/payload A/foreign sentinel; UPDATE aprobado base B; EDIT fijado a v | EDIT primero; versiones preparadas antes de competir; FORCED_PROCESS_ORDER | EDIT primero: UPDATE NO_EFFECT/REMOTE_PRECONDITION, retry_tick=None, HEAD +2 y entidad +1. UPDATE primero: EDIT REMOTE_CAS sin recibo, HEAD +1 y entidad +1. Publicar prueba UPDATE explícitamente; foreign preservado; paquete viejo no reintentable. |
| HC10 | T; UI31, UI32, UI33 | U: entidad v/payload A/foreign sentinel; UPDATE aprobado base B; EDIT fijado a v | UPDATE primero; versiones preparadas antes de competir; FORCED_PROCESS_ORDER | EDIT primero: UPDATE NO_EFFECT/REMOTE_PRECONDITION, retry_tick=None, HEAD +2 y entidad +1. UPDATE primero: EDIT REMOTE_CAS sin recibo, HEAD +1 y entidad +1. Publicar prueba UPDATE explícitamente; foreign preservado; paquete viejo no reintentable. |
| HC11 | R; UI31, UI32, UI33, UI34 | U: entidad v/payload A/foreign sentinel; UPDATE aprobado base B; EDIT fijado a v | EDIT primero; versiones preparadas antes de competir; FORCED_PROCESS_ORDER | EDIT primero: UPDATE NO_EFFECT/REMOTE_PRECONDITION, retry_tick=None, HEAD +2 y entidad +1. UPDATE primero: EDIT REMOTE_CAS sin recibo, HEAD +1 y entidad +1. Publicar prueba UPDATE explícitamente; foreign preservado; paquete viejo no reintentable. |
| HC12 | R; UI31, UI32, UI33, UI34 | U: entidad v/payload A/foreign sentinel; UPDATE aprobado base B; EDIT fijado a v | UPDATE primero; versiones preparadas antes de competir; FORCED_PROCESS_ORDER | EDIT primero: UPDATE NO_EFFECT/REMOTE_PRECONDITION, retry_tick=None, HEAD +2 y entidad +1. UPDATE primero: EDIT REMOTE_CAS sin recibo, HEAD +1 y entidad +1. Publicar prueba UPDATE explícitamente; foreign preservado; paquete viejo no reintentable. |
| HC13 | T; UI32 | L: efecto P remoto; CLIENT UNKNOWN | RESULT con prueba incompatible; después consulta pública con P correcta; CONTROLLED_SEQUENCE | CONFLICT/hard_conflict persiste, sin adoptar binding desde prueba incompatible ni habilitar envío nuevo; un efecto remoto histórico. Registrar entrada alterada sintética y posterior P real sin fabricar autoridad. |
| HC14 | R; UI32, UI34 | L: efecto P remoto; CLIENT UNKNOWN | RESULT con prueba incompatible; después consulta pública con P correcta; CONTROLLED_SEQUENCE | CONFLICT/hard_conflict persiste, sin adoptar binding desde prueba incompatible ni habilitar envío nuevo; un efecto remoto histórico. Registrar entrada alterada sintética y posterior P real sin fabricar autoridad. |
| HC15 | T; UI31 | U: base B contiene entidad v/payload A | EDIT A→B; EDIT B→A; después UPDATE con base vieja; CONTROLLED_SEQUENCE | Entidad v+2 antes del UPDATE; igualdad de payload no restaura base. NO_EFFECT/REMOTE_PRECONDITION, sin sobrescritura; dos EDIT y sus recibos/versiones explícitos. No se denomina carrera ABA simultánea. |
| HC16 | R; UI31, UI34 | U: base B contiene entidad v/payload A | EDIT A→B; EDIT B→A; después UPDATE con base vieja; CONTROLLED_SEQUENCE | Entidad v+2 antes del UPDATE; igualdad de payload no restaura base. NO_EFFECT/REMOTE_PRECONDITION, sin sobrescritura; dos EDIT y sus recibos/versiones explícitos. No se denomina carrera ABA simultánea. |
| HC17 | T; UI31 | U: base B incluye foreign inicial | EDIT solo foreign; después UPDATE con base B; CONTROLLED_SEQUENCE | Base completa obsoleta: UPDATE NO_EFFECT/REMOTE_PRECONDITION; payload y foreign editado conservados, entidad solo sube por EDIT. No equiparar a conflicto solo de payload. |
| HC18 | R; UI31, UI34 | U: base B incluye foreign inicial | EDIT solo foreign; después UPDATE con base B; CONTROLLED_SEQUENCE | Base completa obsoleta: UPDATE NO_EFFECT/REMOTE_PRECONDITION; payload y foreign editado conservados, entidad solo sube por EDIT. No equiparar a conflicto solo de payload. |
| HC19 | T; UI30 | PROJECTION preparada y ACCEPT, todavía sin ISSUE | REVOKE confirma antes de ISSUE; NEGATIVE_CONTROL | ISSUE bloqueado; cero nuevos sends/tickets/efectos y revisión revocada. Distinguir esta guarda del efecto ya posible tras ISSUE de HC05–HC08. |
| HC20 | R; UI30, UI34 | PROJECTION preparada y ACCEPT, todavía sin ISSUE | REVOKE confirma antes de ISSUE; NEGATIVE_CONTROL | ISSUE bloqueado; cero nuevos sends/tickets/efectos y revisión revocada. Distinguir esta guarda del efecto ya posible tras ISSUE de HC05–HC08. |
| HC21 | T/R harness; UI33, UI38 | Labs propios y hooks existentes | READY ambos → W before_object con lock → C probe EAGAIN/EWOULDBLOCK → liberar W; HARNESS_CONTROL | ACK causal completo, operaciones/gates identificados; negativas de evento ausente/timeout/probe inesperado fallan sin PASS parcial; hijos propios terminados/esperados. No afirma que C ya ejecutó flock bloqueante ni demuestra recuperación H02. |
| HC22 | T/R harness; UI12, UI35, UI36, UI37, UI38, UI39, UI40 | Ownership/marker/inodo y sentinels propios | Creación/terminación/limpieza propia; controles de ownership/enlace; RESOURCE_CONTROL | Máximo 4 hijos vivos/caso; 20 s/gate, 120 s/caso, 900 s campaña propia; 256 eventos/caso, raw 8 MiB, evento 16 KiB. Cero recursos propios restantes en éxito. Ownership inválido impide borrar y registra residuo/fallo. Sin inspección operativa. |
| HC23 | Campaña propia; UI01, UI02, UI04, UI06, UI07, UI39 | Inventario nuevo, históricos preservados | Hashes pre/post y raw nuevo anclado con contexto; EVIDENCE_CONTROL | Registrar Python/plataforma/optimize/__debug__, caso/path/actor/rol/operación/modo/punto/orden/ronda/oráculo. Hashes pertinentes coinciden o invalidan resultado; sin depender de assert deshabilitado. Raw I34/I36 sigue NOT_RECORDED; registro I38 intacto. |
| HC24 | Campaña y regresiones; UI08, UI09, UI10, UI11, UI12, UI40 | HC previstos, sin ejecuciones actuales | Runner propio; después runner histórico sin modificar, campaña separada; REPORT_CONTROL | IDs HC→tests/subcasos/órdenes/resultados reales; conteos sin inflar. 321 regresiones Python previstas con raw nuevo separado, sin llamarlo raw histórico; fallos/NOT_RUN explícitos. P0, D5/G01–G07 abiertos, exclusiones y pendientes H03 conservados. |

## Criterio de aceptación y pendientes

Cada fila deberá enlazar IDs realmente ejecutados, eventos causales, versión/base/
prueba y resultados del lector. HC21–HC24 son controles transversales con negativas
propias; no convierten cada evento/probe/assertion en otro test. Los fallos de
setup/control/oráculo y casos no ejecutados impiden un resultado completo PASS.
Regresiones nuevas e históricas se separan por campaña; SQL/Java/Docker no se ejecutan.

Siguen fuera doble ISSUE/CREATE simultáneo, revocación SOURCE/EVALUATION/BATCH,
cambios concurrentes de cuenta/perfil/origen, grooming, H02 y H07. ABA y foreign
HC15–HC18 son secuencias controladas específicas, no competencia simultánea.
El raw histórico ausente y los límites del contexto histórico se conservan.

Ninguna aprobación de este diseño publica commits, cierra D5 global/G01–G07,
amplía A52 ni deduce persistencia/recuperación integrada de PASS aislados.
Sin proveedores/credenciales reales, corpus privado, consumo/reservas, operaciones,
activación, promoción, despliegue o D6. Producto, suites/runners históricos y
registro fijo I38 permanecen fuera de modificación en el I42 propuesto.
