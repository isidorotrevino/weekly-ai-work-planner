# D3 — alcance 1A y optimización 2A

> Estado posterior: **D3 aprobado y cerrado el 2026-10-19** por «si, cierra D3», con el [MVP conservador 1.0](D3-approved.md). Las referencias a D3 abierto en este documento describen la entrega anterior a esa aprobación. No hay promoción ni despliegue aprobado.
Fecha: 2026-10-19. El usuario aceptó **1A: MVP conservador sin previsiones CONDITIONAL ni calendario crítico completo**, y **2A: optimizar el caso independiente y repetir la medición preservando guardas**. Son las opciones de la revisión integrada posterior, distintas de las ocho elecciones iniciales. **D3 sigue abierto; no hay cierre, promoción ni despliegue aprobado.**

## Cambio implementado

[CapacityScheduler](../../scheduler-core/src/main/java/io/github/isidorotrevino/planner/scheduler/CapacityScheduler.java) mantiene la selección greedy, puntuación racional exacta, orden de vías, desempates y contratos de entrada/salida. El coste repetido estaba en buscar huecos de calendario/ocupación para cada alternativa de cada operación en cada paso.

1. **Caché local de slots.** Durante un paso, comparte búsquedas equivalentes por recurso, duración, cuentas físicas, claves exclusivas, intención protegida y tarea cuando hay varias operaciones de esa tarea. Una tarea con una sola operación en el snapshot no puede tener otra decisión de esa misma tarea: permite compartir el hueco con otras tareas independientes. También se conserva el resultado sin slot. Cada asignación vacía la caché; nunca se comparte entre cálculos.
2. **Unión exacta de ocupaciones.** Cada búsqueda sin caché construye una sola unión ordenada de intervalos del worker, claves compartidas y decisiones de la misma tarea. Busca conflictos por binaria y salta al final de un intervalo ocupado, en vez de volver a recorrer todas las decisiones desde cada instante candidato. Intervalos adyacentes se pueden unir: una operación de duración positiva no cabe en un hueco de longitud cero.

Se conservan los candidatos de inicio anteriores, el intervalo semiabierto y la prioridad de la intención protegida. Un salto solo omite inicios imposibles: si un intervalo ocupado intersecta `[inicio,inicio+duración)`, ningún inicio posterior anterior al final ocupado puede evitar ese conflicto. La unión tampoco inventa disponibilidad ni combina intervalos de calendario que por separado no cubran una operación.

La caché no guarda elegibilidad, saldos, reparto, confianza ni deltas. Esos filtros se vuelven a evaluar para cada alternativa/operación. Los importes de una estimación no son parte de la clave temporal porque no cambian el slot; siguen interviniendo en la admisión física posterior. Aprobación, caducidad, mapping congelado, capacidad de cada cuenta y topes de vía se comprueban después de obtener el slot igual que antes.

No se cambian SQL V1–V15, el schema `d3.snapshot.v1`, el identificador de algoritmo `d3.greedy.v1` ni los DTO. La optimización preserva el comportamiento de decisión cuando hay presupuesto suficiente; puede completar cálculos que antes agotaban su tiempo. Conserva el aborto completo si el presupuesto se agota.

## Referencia y comprobaciones

La [fuente previa exacta](../../scheduler-core/src/test/resources/d3-baseline/CapacityScheduler.java) se conserva como recurso **solo de pruebas**. Su SHA coincide con el núcleo registrado en los informes históricos. [OptimizationParityTest](../../scheduler-core/src/test/java/io/github/isidorotrevino/planner/scheduler/OptimizationParityTest.java) la compila con el JDK 21 en un classloader aislado, compartiendo los DTO para poder comparar el `Result` completo con igualdad estructural.

Tres pruebas ejercen **82 escenarios**: 60 variantes heterogéneas con tareas compartidas, workers, calendarios, ocupación/exclusividad, recursos previos e importes/duraciones; 20 variantes de claves homogéneas con cuotas y caducidad de aprobación distintas; dos casos de calendario con huecos/ocupación y ausencia de slot. Se usa reloj monotónico constante únicamente en esta comparación para evitar que un timeout distinto oculte la igualdad de decisiones, razones, alternativas, scores, slots, saldos y prioridades. Las pruebas separadas de presupuesto siguen usando la guarda temporal.

También se ejecutaron las 62 pruebas originales del núcleo, las cuatro fixtures de escala **sin modificar su fuente**, 33 pruebas I2, 39 I3, 25 de coordinación, nueve de aceptación V15 y 157 de regresión D2. La [evidencia nueva](../validation/D3-OPTIMIZATION-results.json) separa los grupos. El núcleo de producción sí cambió deliberadamente por 2A; no se afirma que su hash siga siendo el antiguo. El exportador identifica esa diferencia autorizada y verifica la referencia y los demás inputs históricos.

## Mediciones observadas

Se repitieron las mismas cuatro fixtures y presupuestos. Una observación por fixture/auditoría, en Docker/Java 21. JIT, orden de pruebas y carga del host no están controlados: no es un benchmark estadístico ni permite afirmar un factor de aceleración garantizado.

| Fixture | Presupuesto | Antes: salida / tiempo | Ahora: salida / tiempo | Tentativas ahora |
|---|---:|---|---|---:|
| dag | 5 s | PARTIAL / 0.039 s | PARTIAL / 0.035 s | 1 |
| independent-1000-30s | 30 s | LIMIT_EXCEEDED / 30.000 s | COMPLETE / 6.575 s | 1000 |
| independent-1000-5s | 5 s | LIMIT_EXCEEDED / 5.005 s | LIMIT_EXCEEDED / 5.002 s | 0 |
| independent-200-5s | 5 s | COMPLETE / 1.948 s | COMPLETE / 0.252 s | 200 |

COMPLETE/1.000 demuestra que esa ejecución terminó con todas las operaciones tentativas, no que se ejecutaran workers o proveedores. El DAG conserva un solo productor elegible y consumidores bloqueados; su tiempo no demuestra admisión simultánea de mil operaciones. El caso de 5 s que devuelve LIMIT_EXCEEDED sigue sin prefijo tentativo. No se cambia ningún límite de seguridad para hacer pasar una carga ni se crea un SLA nuevo.

## Estado para revisión

El alcance conservador queda aceptado por 1A: consumidores HARD bloqueados hasta evidencia real, con camino explicativo y cotas de riesgo, sin slots CONDITIONAL ni calendario crítico completo. Esas previsiones pasan a ampliación separada y no constituyen un pendiente oculto de este MVP.

2A queda implementada y medida: el caso independiente de 1.000 completa con el presupuesto de 30 s; la frontera de 5 s se sigue mostrando explícitamente. Permanecen los límites ya aceptados de reservas/checkpoints/integración y la ausencia de alojamiento/temporizadores activos, workers reales, conectores y despliegue. Esta entrega permite revisar el cierre del MVP conservador, pero **no lo declara cerrado**.
