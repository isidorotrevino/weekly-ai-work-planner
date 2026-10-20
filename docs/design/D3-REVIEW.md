# D3 — revisión integrada para decidir el alcance de cierre

> Estado posterior: **D3 aprobado y cerrado el 2026-10-19** por «si, cierra D3», con el [MVP conservador 1.0](D3-approved.md). Las referencias a D3 abierto en este documento describen la entrega anterior a esa aprobación. No hay promoción ni despliegue aprobado.
Fecha: 2026-10-19. **D3 abierto. No se declara cierre, promoción ni despliegue.** La continuación autorizada revisa las bibliotecas/SQL entregados y añade una corrección contractual y validación acotada. La especificación v0.2 incluye objetivos cuya reducción al MVP conservador debe quedar explícita antes de aprobar cierre.

## Hallazgo corregido

C07 exigía observar reaperturas. V14 clasificaba STATE_CHANGED de INCIDENT como evento ordinario, incluida la transición RESOLVED→REOPENED con severidad SEV1/SEV2. D2 no emite siempre REPLAN_REQUIRED en esa transición: su trigger también depende de inserción/cambio de severidad. El resultado podía ser un retraso ordinario de 30 s y una bandera de protección incorrecta en el lote.

La propuesta [V15](../../migrations-d3-review-proposed/V15__critical_incident_reopening.sql) clasifica como inmediato el incidente reabierto que sigue abierto y es actualmente SEV1/SEV2. SEV3/SEV4 conservan el tratamiento ordinario. Si V14 ya había recibido una reapertura crítica en un lote abierto, la migración añade una corrección explícita, conserva el hecho anterior y aumenta la revisión causal; un cálculo viejo ya no puede confirmarse. No altera D2 ni V1–V14, no borra recibos y no reserva capacidad.

[AcceptanceTest](../../scheduler-postgres/src/test/java/io/github/isidorotrevino/planner/postgres/AcceptanceTest.java) prueba esa diferencia antes/después del upgrade y usa transiciones SQL D2 reales sobre datos sintéticos. También ejerce coordinación→plan→CLAIM→CALLBACK→aceptación→VERIFY→sucesor, camino P4→consumidor P0 con evidencia real de finalización, dos ventanas simultáneas y trabajo no interrumpible ante incidente.

## Contratos y evidencia

| Contrato | Evidencia concreta | Límite |
|---|---|---|
| C01: snapshot/CAS/mutex | PlanningStoreTest: dos publicadores; espera ante CLAIM/recalibración/invalidación; phantoms y rollback. CoordinatorTest: lease/revisión y confirmación conjunta | Mutex global y huella completa conservadores; no despliegue concurrente de DDL validado |
| C02: alternativas/calendario/mapping | CapacitySchedulerTest: alternativas y exclusiones. DispatchStoreTest: mapping+CLAIM, workspace y workers independientes. AcceptanceTest: flujo completo V15 | Roles de control plane sintéticos; sin autenticación HTTP |
| C03: TOP_UP/ventanas | Retry por delta, reserva estable, ventana insuficiente, intento/fencing conservados; integración con dos ventanas V15 | Cambio de cuenta/ventana tras reservar sigue bloqueado |
| C04: checkpoint/liquidación | CANCELLED devuelve RESUME_CONTRACT_REQUIRED; UNKNOWN/contradicciones conservan exclusión. V15 mantiene lease/compromiso no interrumpible ante SEV1, sin préstamo/preempción automática | No hay checkpoint real ni recuperación automática desde CANCELLED; D4 debe aportar el protocolo seguro |
| C05: dependencias/integración | HARD real hasta tarea DONE; P4 solo por camino bloqueante, hermano excluido; capability invalidada y MOCKABLE no completan indebidamente | No hay previsiones CONDITIONAL publicadas; bloqueo correcto no equivale a pronóstico de integración |
| C06: equidad persistente | Contadores de vías derivados de reservas, época sin borrar hechos, reloj de espera acotado, retry no cambia vía | Muestras de elegibilidad; no garantía temporal si no cabe una operación segura ni historia exacta de cambios no observados |
| C07: eventos/continuidad | Agrupación 30 s, barrido 60 s invocable, dos recálculos, reaperturas críticas V15, sucesor sin duplicar reservas y flujos completos | No hay daemon activo; el alojamiento debe invocar ticks y producir eventos administrativos que D2 no emite |

La [evidencia de revisión](../validation/D3-REVIEW-results.json) mantiene grupos separados: núcleo original, medición de escala, I2/V12, I3/V13, coordinador/V14, aceptación/V15 y regresión D2/V11. Los grupos antiguos no se presentan como si se hubieran ejecutado íntegros sobre V15. Se verifican hashes de las entradas originales D2, I2, I3 y coordinación; sus informes anteriores se conservan.

## Primera medición de escala, sin SLA

[ScaleReviewTest](../../scheduler-core/src/test/java/io/github/isidorotrevino/planner/scheduler/ScaleReviewTest.java) realiza una ejecución medida por fixture en el contenedor Java 21, con reloj fijo de planificación, cuatro recursos y presupuestos locales de seguridad de 5 s y 30 s. No es una prueba estadística ni una medida de proveedores. Los valores observados se registran en el informe portable; no se extrapolan a producción. El caso independiente de 1.000 se contrasta con ambos presupuestos, sin convertirlos en objetivos de latencia aprobados.

Hay tres formas de carga, medidas en cuatro fixtures: 200 operaciones independientes/800 alternativas; 1.000 independientes/4.000 alternativas; y 1.000 operaciones/4.000 alternativas/5.000 aristas HARD activas con solo el productor inicial elegible. El DAG no demuestra que se puedan programar mil operaciones a la vez. Un test que comprueba LIMIT_EXCEEDED es una validación del aborto seguro, no una prueba de rendimiento completada.

| Fixture | Presupuesto de cómputo | Tiempo observado | Salida | Operaciones tentativas |
|---|---:|---:|---|---:|
| dag | 5 s | 0.039 s | PARTIAL | 1 |
| independent-1000-30s | 30 s | 30.000 s | LIMIT_EXCEEDED | 0 |
| independent-1000-5s | 5 s | 5.005 s | LIMIT_EXCEEDED | 0 |
| independent-200-5s | 5 s | 1.948 s | COMPLETE | 200 |

La política P08/6B aplazó metas numéricas; ahora existe una primera medida para decidir el siguiente paso. No se inventa una latencia objetivo aprobada. Completar el fixture pequeño y abortar con seguridad el grande no demuestra la escala operativa de 1.000 operaciones inicialmente considerada.

## Decisiones presentadas y respondidas después de esta revisión

1. **Previsiones:** propongo documentar el MVP actual como planificación solo de trabajo elegible, con consumidores HARD bloqueados, camino explicativo y cotas inferiores de riesgo. No incluye slots CONDITIONAL ni un calendario crítico completo por recursos. Alternativa: implementar y validar esas previsiones antes de plantear cierre. El cierre de la especificación v0.2 completa no puede darse por cumplido silenciosamente mientras falten.
2. **Rendimiento:** propongo mantener D3 abierto y optimizar el caso independiente antes de repetir la medición, manteniendo intactas las guardas y sin fijar un SLA todavía. Alternativa: aceptar expresamente el límite medido como frontera de este MVP, conservar el aborto seguro y aplazar la mejora de escala. Un cierre bajo esa alternativa sería de alcance acotado, no una demostración de rendimiento a 1.000 operaciones.

Las restricciones ya aprobadas por 7A —sin rollover de reservas, checkpoint inseguro ni completitud MOCKABLE sin guarda real— se conservan; no se pide aprobarlas de nuevo. Tampoco se pide autorización para desplegar, promover migraciones o iniciar workers reales. Resolver estas dos decisiones no cierra D3 automáticamente: su cierre requiere aprobación expresa posterior sobre el resultado revisado.

## Resultado posterior de la consulta

El usuario eligió **1A y 2A**: acepta el MVP conservador y autoriza optimizar el caso independiente. Se completó la [optimización y repetición de mediciones](D3-OPTIMIZATION.md), con [evidencia nueva separada](../validation/D3-OPTIMIZATION-results.json). Este documento y su informe conservan la medición anterior; las dos decisiones ya están respondidas. D3 permanece abierto y su cierre exige aprobación expresa.
