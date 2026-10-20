# D3 — planificador de capacidad, MVP conservador aprobado

Versión de cierre: **1.0**. Fecha: **2026-10-19**, Europe/Madrid. Estado: **D3 aprobado y cerrado**.

El usuario aprobó expresamente el cierre con **«si, cierra D3»**, después de aceptar el alcance conservador 1A, autorizar la optimización 2A y recibir sus resultados. Esta aprobación cierra D3 como diseño y prototipo validado de bibliotecas Java/SQL. **No aprueba despliegue, promoción de migraciones ni una plataforma de workers reales.** D1/D2 permanecen aprobados; la referencia publicada del cierre D2 sigue siendo `69d71c3877e79bdfef088956b090d4eb6b447be9`. No se atribuye a D3 un commit publicado.

Este documento y el [registro de decisiones](D3-DECISIONS.md) prevalecen para el estado de cierre. Los borradores, revisiones e informes anteriores conservan su estado histórico «D3 abierto» al ser emitidos; sus frases no reabren esta aprobación.

## Alcance aceptado

- Horizonte móvil de siete días civiles, Europe/Madrid y persistencia UTC. Deadlines blandos con explicación del riesgo; sin eludir `deferral_allowed=false` ni guardas de ejecución.
- Cuentas físicas por recurso/dimensión/ventana, reparto base 70% PLANNED / 20% INCIDENT / 10% UNCERTAINTY. No sumar unidades/proveedores ni crear capacidad al replanificar. Reservas compartidas entre planes, mappings congelados y retries por delta, sin reiniciar intentos.
- Reparto ponderado por recurso, servicio al proyecto ejecutor, vía de edad de hasta 5% de PLANNED tras siete días elegibles y vía urgente de hasta 20% con holgura ≤24 h. Persistencia de hechos/contadores, épocas explícitas e incertidumbre de historia visible.
- Dependencias y evidencia D2/SemVer reutilizadas. Prioridad heredada solo por camino bloqueante; excepción P4 limitada a trabajo activo de mayor prioridad. PAUSED/ARCHIVED excluidos.
- **1A conservador:** asignar únicamente trabajo actualmente elegible. Consumidores HARD bloqueados hasta evidencia real, con camino explicativo y cotas inferiores de riesgo. Sin slots CONDITIONAL ni calendario crítico completo; son ampliación separada.
- Confianza ≥0,8, estimaciones documentadas/calibradas con caducidad, heartbeat ≤90 s, una operación por worker y exclusión de tarea/directorio/entorno. Preservación de intención válida y tolerancia de recurso previamente aprobadas.
- Captures inmutables, publicación CAS con sucesor y validación final, dispatcher ligado al plan vigente y mapping+CLAIM atómicos. Fencing y conciliación D2 conservan compromisos ante UNKNOWN o contradicciones.
- Coordinador invocable durable: agrupación ordinaria 30 s, críticos inmediatos, barrido persistente 60 s, dos recálculos máximos y recuperación de lease. V15 corrige reapertura crítica nueva o previamente encolada por V14.
- **2A implementada:** optimización de slots mediante caché local por paso y unión exacta de ocupaciones, preservando decisiones/guardas y aborto sin prefijo tentativo.

Los contratos de algoritmo/DTO, [publicación I2](D3-I2-PERSISTENCE.md), [despacho I3](D3-I3-DISPATCH.md), [coordinación](D3-COORDINATOR.md) y [optimización](D3-OPTIMIZATION.md) detallan la implementación. Su secuencia y autorizaciones constan en [D3-DECISIONS](D3-DECISIONS.md).

## Evidencia de cierre

Se comprobó que los inputs ejecutables actuales coinciden con la [última evidencia de optimización](../validation/D3-OPTIMIZATION-results.json) y que las entradas históricas D2 siguen intactas. Este cierre solo cambia documentación; no atribuye nuevas ejecuciones de pruebas ni sobrescribe los informes previos.

| Grupo de la última ejecución | Pruebas | Alcance |
|---|---:|---|
| Núcleo original | 62 | Guardas, capacidad, equidad, prioridades, determinismo y presupuesto |
| Medición de escala | 4 | Fixtures sintéticas acotadas; un aborto seguro también es un resultado válido del test |
| Paridad de optimización | 3 | 82 escenarios comparados contra la fuente anterior exacta |
| I2 | 33 | PostgreSQL con V1–V12 |
| I3 | 39 | PostgreSQL con V1–V13 |
| Coordinador | 25 | PostgreSQL con V1–V14 |
| Aceptación integrada | 9 | PostgreSQL con V1–V15 y upgrade de reaperturas |
| Regresión histórica D2 | 157 | V1–V11; 29.829 vectores SemVer incluidos en una prueba |

Todos los grupos terminaron sin fallos, errores u omisiones. No son garantías de producción ni se presentan como si todos hubieran corrido sobre V15. Los hashes y el vínculo de aprobación se registran en el [manifiesto de cierre](../validation/D3-CLOSURE.json).

En la observación final, 1.000 operaciones independientes completaron en **6,575 s** con presupuesto de 30 s; antes agotaban 30 s. Con 5 s sigue habiendo aborto seguro. El caso de 200 completó en **0,252 s**. Una ejecución por fixture, con efectos de JIT/host no controlados: **no se establece SLA ni factor de aceleración garantizado**.

## Límites conservados y continuidad

| Destino | Trabajo posterior |
|---|---|
| D4 | Workers, transporte/autenticación, recuperación concluyente de efectos, checkpoints/preempción y pruebas reales de parada/fencing. No reanudar automáticamente CANCELLED ni retirar exclusión con evidencia contradictoria |
| D5 | Conectores/parsers, proveedores y cuotas comerciales reales; una cuota desconocida bloquea. Sin fallback automático de pago |
| D6 | Alojamiento y temporizadores activos, identidades/permisos reales, retención, promoción de migraciones y despliegue revisado |
| Ampliación de planificación | CONDITIONAL y calendario crítico completo, excluidos del MVP por 1A; nuevos objetivos de rendimiento solo mediante decisión explícita |

El coordinador requiere invocaciones de un alojamiento posterior; no hay daemon activo. La espera elegible se basa en muestras acotadas y no acredita cambios no observados. La renovación exige cobertura para los 60 s del lease D2 y puede bloquearse cerca de un reset. No se remapean reservas a ventanas nuevas ni se automatiza liquidación/préstamo sin contrato seguro. El déficit INCIDENT no toma PLANNED ni UNCERTAINTY.

V1–V15 permanecen en sus ubicaciones de originales/propuestas, sin promoción. El cierre no cambia D1/D2, no inicia D4 y no publica código ni servicios.
