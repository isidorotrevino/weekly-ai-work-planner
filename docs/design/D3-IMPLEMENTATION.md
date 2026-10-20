# D3 — estado de implementación

Actualizado: 2026-10-19. Diseño v0.2 aprobado e inicio I1–I3 autorizado por «si, adelante», después de la revisión exigida en 8B. **D3 aprobado y cerrado como MVP conservador 1.0 por «si, cierra D3». Sin promoción ni despliegue aprobado.** [Alcance de cierre](D3-approved.md). Las secciones por incremento conservan la secuencia histórica.

## Primer incremento I1 entregado

Módulo [scheduler-core](../../scheduler-core/README.md), Java 21, sin dependencias de producción. JUnit y Maven reutilizan versiones ya presentes en el harness D2. Se mantiene Java/Spring/PostgreSQL como arquitectura; este núcleo es una biblioteca independiente de transporte/persistencia.

| Área | Comportamiento ejecutable |
|---|---|
| Contratos | Records inmutables, versiones de esquema/algoritmo y Request con reloj fijo y límites explícitos; salida reviewOnly |
| Capacidad | Vector completo por cuentas físicas y pools, NULL/deficiencias preservados, admisión atómica virtual, sin préstamos automáticos ni gasto UNCERTAINTY |
| Reservas | CARRIED sin doble resta; retry por delta TOP_UP y consumo previo conservado; recurso/pool/mapping congelados; intento agotado o ventana vencida bloquean |
| Dependencias | DAG HARD activo importado, ciclos rechazados, herencia con ruta explicativa y excepción P4 limitada; consumidores no se desbloquean por previsiones |
| Elegibilidad | Diagnósticos D2 importados, políticas/contexto, aprobación en inicio previsto, confianza de cuenta/estimación ≥0,8, calibración, caducidad, capacidades y heartbeat ≤90 s |
| Reparto | Coste/servicio dominante con fracciones exactas, vía de edad 5%, urgente 20%, límites por cuenta y uso previo del snapshot, servicio al productor |
| Recursos | Calendarios [inicio,fin), una operación por worker, directorios/entornos exclusivos, operaciones de la misma tarea serializadas; tolerancia del 10% y protección válida de 15 min |
| Incidentes | Severidad/antigüedad, triaje SEV3/4, FOLLOW_UP en PLANNED; déficit INCIDENT visible sin tomar PLANNED |
| Explicación | Disposición de cada operación, razones, ruta de herencia, alternativas, puntuación exacta, deltas y antes/después virtuales; determinismo del resultado completo |
| Eventos | Política pura de agrupación 30 s, seguridad inmediata, deduplicación con conflicto de contenido, barrido 60 s y dos recálculos; unión de intervalos elegibles |
| Límites | Entrada inválida/ciclo/exceso de tamaño o cálculo devuelven resultado no ejecutable sin conservar un prefijo tentativo |

La [evidencia JUnit portable](../validation/D3-I1-results.json) registra el resultado ejecutado y hashes del código. Es independiente de las 44 comprobaciones aritméticas previas y de las 157 pruebas históricas D2; no sumar esos conteos como garantías de producción.

## Validación y límites de I1

Pruebas sobre snapshots sintéticos: varias ventanas/dimensiones, cuota desconocida y déficit, reservas/retries/cuentas vencidas, caminos de prioridad/P4, integración real requerida, confianza/caducidad, conflictos de worker/directorio, incidentes y vías, protección, presupuestos de cálculo y permutación de entradas con igualdad del resultado completo. También se comprueba el cambio de cuenta dominante durante TOP_UP para no volver a cobrar servicio ya comprometido, y la conservación de la vía original del retry para que cambiar su orden de selección no eluda el cupo 5%/20%.

No se ejecuta ningún CLAIM, publicación, worker o proveedor real. La confianza de las guardas D2 debe establecerla un adaptador del control plane, no una entrada no verificada. La exactitud del diario, la compatibilidad V11 y las aprobaciones no se reimplementan en Java.

Los saldos y reservas físicos permanecen inmutables durante el cálculo. Los acumuladores de servicio/vía son virtuales; persistirlos y reconstruirlos entre runs exige I2. Historia consumida sin atribución produce diagnóstico, no un reinicio silencioso con garantía de equidad. El historial de decisiones futuras debe conservar ese diagnóstico y su época.

No hay todavía pronóstico CONDITIONAL de consumidores HARD. Las fechas propagadas son cotas inferiores con las duraciones conocidas, no un calendario crítico global garantizado; sin duración relevante, el riesgo permanece UNKNOWN. El rendimiento no se presenta como cumplimiento de ≤2 s/≤250 ms: esas metas fueron aplazadas.

## Incremento I2 entregado

[Persistencia/publicación I2](D3-I2-PERSISTENCE.md): adaptador JDBC, propuesta aditiva V12, snapshot inmutable con huella completa, catálogo de estimaciones/calendarios, observaciones/épocas/atribuciones de equidad y publicación CAS con validación final, supersesión y outbox atómicos. La [evidencia I2](../validation/D3-I2-results.json) separa integración, núcleo y regresión histórica D2.

Las afirmaciones de ausencia de SQL/publicación de la sección anterior describen exclusivamente I1. I2 sí ejecuta publicación y D2 CLAIM sobre datos sintéticos en PostgreSQL desechable; no ejecuta workers ni proveedores reales. Los datos de equidad ya tienen persistencia, mientras el consumo automático de eventos y sus temporizadores siguen pendientes.

V12 está en `migrations-d3-proposed/` para preservar el caso histórico de upgrade D2 V10→V11. No se promueve a producción. Los roles de prueba son NOLOGIN y no constituyen una identidad de despliegue.

## Incremento I3 entregado

[Despacho protegido I3](D3-I3-DISPATCH.md): adaptador JDBC y propuesta V13 aditiva; plan vigente, mapping+CLAIM atómicos, trazabilidad inmutable plan/intento/reserva, vías persistentes, reintentos por delta, guardas actuales de ventanas/aprobación/integración y ciclo de ejecución D2 con fencing. La [evidencia I3](../validation/D3-I3-results.json) mantiene grupos separados y verifica las entradas históricas D2/I2 intactas.

I1–I3 se han implementado como bibliotecas y SQL sintéticos; no son una plataforma desplegada. El coordinador de solicitudes/eventos se añade en el complemento siguiente. Pendientes: alojamiento/temporizadores, transporte/autenticación, workers/checkpoints/proveedores, conectores, permisos/retención y despliegue D4–D6. No hay servicio ni temporizadores activos. El detalle de límites figura en I3.

V1–V12 y D1/D2 se preservan. V12/V13 permanecen propuestas aisladas sin promoción. **D3 sigue abierto: cierre y despliegue requieren aprobación expresa.**

## Complemento de coordinación entregado

[Coordinador durable](D3-COORDINATOR.md): ingesta con recibos propios, agrupación 30 s, críticos inmediatos, barrido persistente 60 s, observaciones, leases con fencing, recálculos limitados a dos y publicación/confirmación atómicas. SQL V14 y Java invocables, sin proceso residente. [Evidencia separada](../validation/D3-COORDINATOR-results.json); V1–V13 y los ejecutables originales I1–I3 se conservan. La continuación «sigue» autoriza este trabajo; no implica cierre ni despliegue de D3.

## Revisión integrada para decidir el cierre

[Revisión D3](D3-REVIEW.md): corrección V15 de reapertura crítica, incluso si V14 ya había encolado el evento como ordinario, y nueve pruebas integradas sobre V15. Se añaden cuatro fixtures medidos de escala; un aborto seguro no equivale a completar la carga. [Evidencia separada](../validation/D3-REVIEW-results.json), sin alterar V1–V14 ni los ejecutables originales. Faltan decisiones explícitas sobre la ausencia de previsiones CONDITIONAL y el siguiente paso de rendimiento; no se recomienda declarar cumplimiento completo de v0.2 ni cerrar D3 mientras sigan pendientes.

## Alcance aceptado y optimización entregada

El usuario respondió 1A/2A a la revisión integrada: acepta el MVP conservador sin previsiones y autoriza optimizar. [Optimización y evidencia](D3-OPTIMIZATION.md): tres pruebas diferenciales/82 escenarios y las mismas cuatro fixtures de escala; 1.000 operaciones independientes completan en la ejecución con presupuesto de 30 s. SQL V1–V15 y adaptadores permanecen intactos; cambia deliberadamente el núcleo, con fuente previa exacta conservada para comparar. Las decisiones de aquella revisión están respondidas. **D3 continúa abierto, pendiente de aprobación expresa de cierre.**

## Cierre aprobado

El usuario aprobó expresamente el cierre el 2026-10-19 con «si, cierra D3». Prevalece [D3 aprobado 1.0](D3-approved.md); el [manifiesto](../validation/D3-CLOSURE.json) vincula aprobación, evidencia y hashes verificados. D3 está cerrado; despliegue y promoción siguen fuera de esta aprobación.
