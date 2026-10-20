# D3 — coordinación durable de solicitudes y eventos

> Estado posterior: **D3 aprobado y cerrado el 2026-10-19** por «si, cierra D3», con el [MVP conservador 1.0](D3-approved.md). Las referencias a D3 abierto en este documento describen la entrega anterior a esa aprobación. No hay promoción ni despliegue aprobado.
Fecha: 2026-10-19. Continuación autorizada por «sigue» tras entregar I3. **D3 permanece abierto, sin despliegue ni cierre aprobado.** Este complemento integra I1–I3 en un ciclo invocable; no inicia una aplicación, temporizador, worker ni llamada a proveedores.

## Entrada y salida

[PlanningCoordinator](../../scheduler-postgres/src/main/java/io/github/isidorotrevino/planner/postgres/PlanningCoordinator.java) ofrece:

| Método | Contrato |
|---|---|
| `enqueue` | Evento explícito del control plane: UUID, tipo ReplanPolicy, instante y contenido. Misma identidad/contenido conserva el lote original, incluso después de completarlo; contenido distinto da conflicto |
| `poll` | Recibe hasta 100 eventos del outbox, registra recibos propios y realiza el barrido si han pasado 60 s. Devuelve conteos y backlog visible |
| `take` / `prepare` | Adquiere el único lote abierto mediante lease con worker/generación, observa elegibilidad y persiste capture, IDs de plan/publicación y revisión causal del intento |
| `runOnce` | Toma un lote vencido, calcula sin locks y publica; ante STALE permite exactamente dos recálculos adicionales |
| `tick` | Un `poll` más un `runOnce`; el llamador proporciona IDs estables para reintentar las mismas invocaciones |
| `read` | Estado, eventos, intentos y transiciones de la solicitud, también si acaba STALE/BLOCKED |

La salida distingue IDLE, PUBLISHED, STALE y BLOCKED, con solicitud, plan confirmado si existe y número de recálculos. PUBLISHED confirma la intención del plan; no ejecuta CLAIM. Un resultado inválido del núcleo queda BLOCKED y conserva el plan anterior. Los errores SQL de publicación 40001 causan recálculo; 23514 quedan BLOCKED. Fencing, permisos, transporte y errores inesperados se propagan, sin declarar que una publicación falló cuando su resultado puede ser desconocido.

```java
var coordinator = new PlanningCoordinator();
// Conexión del control plane, autocommit READ COMMITTED.
var result = coordinator.tick(connection, pollCommandId, takeCommandId, coordinatorWorkerId);
// result puede ser IDLE. Un alojamiento posterior decide cuándo volver a invocar.
```

La [propuesta V14](../../migrations-d3-coordinator-proposed/V14__planning_coordinator.sql) es aditiva sobre V1–V13; tiene una quinta ubicación explícita. Sus tablas administrativas se excluyen del read_set físico I2 para evitar que registrar el propio cálculo lo invalide. Los hechos del lote se validan mediante revisión y fencing antes de publicar.

## Eventos, tiempo y equidad

Un único lote QUEUED/RUNNING acumula eventos persistentes. Los ordinarios vencen 30 s después de la primera recepción, sin aplazarse por tráfico continuo. Incidentes críticos, dependencia invalidada, déficit, worker perdido y aprobación inválida adelantan el lote a su recepción y rompen protección. Un cambio de prioridad rompe protección, pero conserva el plazo de agrupación. El cálculo recibe este valor en `Request.breakProtection`; se conserva la protección de 15 min para trabajo que sigue siendo válido en los demás casos.

Un evento recibido durante el cálculo incrementa la revisión: aquel intento no puede publicarse. El siguiente capture recoge el nuevo estado y las banderas acumuladas. Incluso con tráfico continuo solo se hacen cálculo inicial y dos recálculos; al agotarlos queda STALE con historia y eventos visibles. No se reinicia el presupuesto dentro de la misma solicitud. Un evento nuevo o barrido posterior puede abrir otra solicitud, dejando intacta la anterior.

El barrido se recuerda en PostgreSQL, no en memoria del proceso. Al primer `poll` o después de 60 s genera SWEEP, observa elegibilidad y permite revisar guardas sensibles al reloj. SWEEP está listo inmediatamente y no rompe protección por sí mismo; puede adelantar un lote ordinario si coincide con un barrido vencido. No sustituye los resets físicos de cuentas ni inventa tiempo de espera anterior a la observación.

La elegibilidad se muestrea al recibir eventos nuevos, en los barridos y al preparar un capture. Se reutilizan los intervalos acotados I2: heartbeat, aprobación, estimación y ventanas limitan la espera reconocida; las muestras superpuestas no duplican tiempo. Un corte de servicio deja huecos de historia, no crédito ilimitado. La cadencia de 60 s requiere que un alojamiento posterior invoque `tick`; no hay daemon activo ni garantía de entrega en tiempo real.

El adaptador de outbox reconoce REPLAN_REQUIRED crítico, invalidaciones, transiciones de tarea/capability/incidente/operación, cambios de capacidad y solicitudes de replanificación I3. Un déficit vigente por recalibración, consumo u otra operación de capacidad se clasifica como inmediato, conservando consumo y deuda. Algunas mutaciones administrativas no generan eventos D2: su integración debe enviar `enqueue`; el barrido revisa el estado vigente aunque falte ese evento. No se promete observación exacta de transiciones que nunca se entregaron.

## Durabilidad y concurrencia

La ingesta usa recibos independientes por outbox UUID y contenido inmutable; no modifica `delivered_at` ni el recibo global D2 de otros consumidores. No usa un máximo de UUID ni de timestamp: una inserción tardía con fecha antigua se recibe igualmente. Ordena primero los críticos conocidos, recibe como máximo 100 filas y expone backlog. PLAN_PUBLISHED y tipos no reconocidos quedan registrados como IGNORED, sin producir un bucle de planes. El límite de filas no es una garantía de coste de consulta: clasificar y buscar pendientes puede recorrer historia.

El lease de cómputo dura 60 s, con generación propia e independiente del lease de ejecución D2. `take` no roba uno vigente; tras caducar, otro proceso incrementa la generación y recupera los mismos IDs del intento preparado. El proceso anterior ya no puede publicar ni marcar fallos. No se añade un renovador durante cálculo: un cálculo que excede el lease queda cercado y necesita recuperación. Este timeout interno no constituye un SLA del scheduler.

Preparar el capture y registrar sus IDs es una transacción corta. Después el adaptador lee el cuerpo inmutable y ejecuta el núcleo sin transacción SQL abierta. Publicar adquiere primero el mutex de publicación y después el global D2, comprueba lease/revisión/intento, llama al publicador I2 y confirma plan, outbox y solicitud juntos. Si el lease caduca durante esa transacción, se revierte todo. Un rollback tampoco deja el lote como publicado.

Tras perder una respuesta se reutiliza el comando TAKE y el intento persistido. Una publicación confirmada devuelve el mismo resultado, incluso si el lease ya caducó, sin calcular ni publicar de nuevo. STALE/BLOCKED también se pueden consultar o repetir sin recomenzar su presupuesto. Los fallos ambiguos de conexión no crean artificialmente un nuevo plan o contador de recálculos.

El rol sintético del coordinador solo puede usar estas entradas y leer captures; no recibe publicación directa, dispatcher, contabilidad, configuración ni DML. Se prueban roles NOLOGIN; identidades y permisos de despliegue siguen pendientes en D6.

## Validación y alcance restante

[Resultados portables](../validation/D3-COORDINATOR-results.json): 25 pruebas del coordinador, 62 del núcleo, 33 de I2, 39 de I3 y 157 históricas D2, todas sin fallos, errores u omisiones y en grupos separados. La suite nueva usa V1–V14, además de probar upgrade V13→V14 con plan publicado, reserva, diario y lease activo. I2 sigue probándose en V12, I3 en V13 y la regresión histórica D2 en V11; no se atribuyen esos grupos retrospectivamente a V14.

Los escenarios cubren agrupación/aceleración, prioridad/protección, deduplicación tras completar, evento futuro/inválido, backlog, llegada tardía, recibos por consumidor, barrido persistente, observación idempotente, dos procesos, recuperación de lease, cálculo sin locks, eventos durante cálculo, conflicto físico, agotamiento y replay de STALE, bloqueo sin sustituir el plan anterior, rollback, respuesta perdida, error ambiguo y déficit por consumo real sintético.

V1–V13 y las entradas ejecutables originales I1–I3 permanecen intactas. Los informes anteriores son históricos y no se sobrescriben. D3 sigue siendo un prototipo de bibliotecas/SQL: faltan alojamiento HTTP/Spring y temporizadores, autenticación, workers/checkpoints/preempción reales, conectores/proveedores, retención/permisos y despliegue. No se ha autorizado cierre de D3.
