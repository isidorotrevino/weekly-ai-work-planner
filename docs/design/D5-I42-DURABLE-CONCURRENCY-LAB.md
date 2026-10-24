# D5 I42 — laboratorio de carreras T/R

Fecha: **2026-10-24**, Europe/Madrid. Alcance aprobado tras el commit de diseño
`cd97028468236b78ffb5483f8e637a4075905687`, mediante selección **A** del usuario:
implementar/validar harness HC01–HC24, evidencia propia y regresiones Python
separadas. [Contrato I41](D5-I41-DURABLE-CONCURRENCY-DESIGN.md) ·
[Matriz I41](D5-I41-DURABLE-CONCURRENCY-REVIEW.md) ·
[Harness](../../testing/durable_concurrency/README.md).

Se incorporan únicamente archivos nuevos en `testing/durable_concurrency` y
documentos/evidencia I42. No se modifica el kernel, reducers, parsers, fachadas,
pruebas/runners históricos, registro fijo I38, handoff o informes anteriores.
La autorización de implementación no autoriza publicación: P0 sigue vigente.

## Competencias y oráculos

Dos procesos spawn abren clientes nuevos. En respuesta/consulta, reconcile público
confirma QUERY y observa mediante lookup real la prueba P, retenida como mensaje;
su RESULT y la respuesta directa se preparan desde la misma HEAD. El ganador
queda pausado dentro de before_object bajo lock. El contendiente observa ese
lock mediante flock no bloqueante sobre descriptor propio, después sigue su
llamada real; el padre libera el ganador solo tras el evento de observación.
Se conservan ambas ordenaciones deliberadas. El probe no acredita que el flock
bloqueante del producto ya se ejecutara.

HEAD común y ledger obsoleto tienen rondas y oráculos distintos. RESULT ganador
consume pendientes y publica P; el perdedor falla por HEAD. Después se presenta
ledger viejo con HEAD fresca y se exige CONFLICT_LEDGER sin nuevo recibo. Una
conciliación nueva acredita el mismo hecho remoto sin reenviar el ticket.

Revocar tras ISSUE no deshace el efecto posible: la carrera y la acción posterior
explícita quedan separadas. Final histórico EFFECT_CONFIRMED + STALE, revisión
revocada v2. El control anterior a ISSUE exige cero send/ticket/efecto.

EDIT usa Store.transact público con expected_version fijada; UPDATE usa execute
con base aprobada. EDIT primero provoca NO_EFFECT/REMOTE_PRECONDITION sin retry;
UPDATE primero confirma el efecto y EDIT viejo falla REMOTE_CAS sin recibo.
El reintento de UPDATE ya confirmado falla RETRY_FORBIDDEN, distinto de
RETRY_NOT_ELIGIBLE del paquete rechazado por precondición. Los controles ABA y
foreign son secuencias explícitas; no se anuncian como carreras simultáneas.

El lector propio comprueba bytes/hash/marker/HEAD/cadena/recibos sin Store ni
reducer y con comprobaciones explícitas independientes de `assert`. Reapertura
final en proceso nuevo contrasta el mismo estado desde disco; no acredita H02.
La campaña exige optimize=0 y registra Python/build/plataforma, IDs, hashes,
gates, rol/operación/modo/orden/ronda y oráculos, sin payload o paths privados.

## Ejecución y conservación

Comando propio: `python3 -B -m testing.durable_concurrency.run_concurrency_lab`.
Regresión separada sin modificar runner:
`python3 -B -m testing.D5.run_relational_durable_lab`.
Los resultados y raws nuevos se enlazan desde el [informe I42](../validation/D5-I42-results.md).
Los hashes anteriores/posteriores y los IDs distintos gobiernan la aplicabilidad;
filas, rondas, eventos y lectores no se suman como tests adicionales.

Las negativas de control incluyen probe libre, READY ausente, espera reducida
expirada, ownership/enlace, cambio/adición de input, eventos fuera de presupuesto
y contabilidad incompleta/duplicada/skip/residuo. Un timeout mata/espera solo su
hijo propio y no se contabiliza como recuperación de producto. Se mantienen los
límites del contrato y limpieza de temporales propios con sentinels.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado permanecen intactos.
D5 global, G01–G07 y revisión global de los cinco GI siguen abiertos. Pendientes
H03 excluidos, H02/H07 y límites históricos H04/H05 no se eliminan. I34/I36 raw
original sigue NOT_RECORDED. Sin proveedores/credenciales reales, consumo/reservas,
activación, promoción, despliegue ni D6. No se deduce recuperación integrada de
PASS aislados ni se transforma 30/35 en 35/35.
