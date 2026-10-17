# D2 — matriz de validación y límites

Estado: D2 cerrado y aprobado tras validación satisfactoria y aprobación condicionada del usuario. Fecha: 2026-10-17.

Documento consolidado: [D2 aprobado](../design/D2.9-approved.md). Resultado cuantitativo y alcance de la última ejecución: [guía de validación](README.md) y [resultados portables](latest-results.json). Las filas siguientes describen el contrato nuevo; la batería histórica mantiene casos OPEN en V4/V5 para demostrar los huecos anteriores.

## Plan original D2.4

| Escenario | Evidencia disponible | Límite de la conclusión |
|---|---|---|
| 1. Flyway/PostgreSQL | V1–V11, upgrade V10→V11, validate y migrate repetido; todas las FKs del contrato validadas; índices operativos principales presentes | No auditoría de rendimiento ni upgrade de una base de producción |
| 2. Transiciones y eventos | Estado/versión esperados, rechazo de arco inválido, replay, historia y outbox únicos por comando/versionado | El propietario puede cambiar DDL; la garantía de acceso usa rol runtime restringido |
| 3. 20 claims y fencing | Un claim completo confirmado, lease/intento/reserva/historia; rechazo de generación obsoleta y tuple incorrecto | Mutex global conservador; no prueba throughput de cuatro workers reales |
| 4. Crash tras efecto externo | Recibo APPLIED confirmado en otra conexión antes de perder callback; recuperación y verificación sin segunda aplicación | Adaptador simulado; no se ejecutó un commit Git ni API externa |
| 5. Duplicados | Callback repetido no duplica consumo; mismo command_id con otro contenido falla; ack outbox repetido produce un recibo | Un ack SQL no garantiza efecto único en una API; la integración necesita idempotencia/reconciliación |
| 6. Reservas concurrentes | Dos reservas de 60 contra pool 70: una admitida; cuentas físicas compartidas entre planes | La reserva opera por el entrypoint; SQL de propietario queda fuera del modelo de aplicación |
| 7. Cuota desconocida | NULL bloquea; una recalibración con evidencia permite admisión; reducción conserva consumo y déficit | Solo unidades sintéticas; no medición ni estimación real de cuotas comerciales |
| 8. BORROW/RETURN | Conservación del límite, deuda, no devolución de capacidad comprometida y bloqueo de préstamo no checkpointable | La verdad del checkpoint y de la demanda del proveedor depende de adaptadores confiables |
| 9. Planes y snapshots | Padre/hijos congelados; sucesor explícito; misma reserva ligada a dos planes sin duplicación; publicación contra mutación concurrente | No solver D3 ni política real de selección de plan vigente |
| 10. Capabilities | PASS exacto y fresco; invalidación cambia epoch, bloquea HARD y reconcilia activos; MOCKABLE no completa sin integración compatible | Productores, resoluciones y evidencia son fixtures; verificadores reales son D4/D5 |
| 11. DAG/prioridad | Ciclos de tareas, capabilities y proyectos HARD rechazados; dos escritores opuestos no confirman ambos; SOFT permitido; herencia solo por camino bloqueante | El grafo necesita productores/resoluciones explícitos; rangos de versiones no soportados bloquean |
| 12. SEV1/checkpoint | REPLAN_REQUIRED transaccional; no interrumpible se aplaza; cancelación/liberación exige recibo seguro de la generación actual | No se detuvieron procesos reales ni se midió latencia de replanning |
| 13. Aprobaciones | Ausencia/caducidad/contexto modificado bloquean ejecución; snapshots de intento inmutables; consumo observado no se pierde por caducidad posterior | Interfaz de aprobación, identidad humana y almacenamiento de secretos son posteriores |
| 14. Fuentes/conflictos | CAS de revisión externa conocida/hash local, conflicto sin sobrescritura, revisiones preservadas y replay | Ingestión simulada; una escritura real debe usar condicionamiento y scopes de la API D5 |
| 15. SemVer/npm | 29.829 vectores, orden, límites, guardas CLAIM/VERIFY, builds con evidencia independiente y preflight de upgrade | Versiones canónicas y tamaños/números acotados explícitamente; sin modos loose/coerce |

## Hallazgos originales F01–F14

| Hallazgo | Tratamiento actual |
|---|---|
| F01 allocation/budget | V5 exige vínculo, valida coherencia y solo backfill inequívoco |
| F02 movimiento/propietario | V6/V7 enlazan recurso, operación, tarea, proyecto y pool; transferencias V3 no apuntan a una allocation |
| F03 capacidad/balances | V8 implementa contrato de cuentas físicas y diario con vistas; locks, ventanas simultáneas, desconocidos, deuda y correcciones |
| F04 duplicación/snapshots | V7/V8/V10 congelan snapshots y separan cuenta/reserva de planning run |
| F05 fencing | V5 tuple y unicidad; V9 generación vigente, vencimiento y comandos de recuperación |
| F06 aprobaciones | V5 metadatos; V9 comparación y caducidad en claim/START/renovación |
| F07 estados/evidencia | V9 API restringida, creación en estado inicial, CAS, verificación exacta y generación de invalidación |
| F08 ciclos | V7 tipa project_dependencies; V9 serializa y comprueba grafos HARD |
| F09 historia/idempotencia | V9 valida entidad por lookup, recibos únicos de versión y comando; historia/outbox transaccionales por API |
| F10 ownership/bindings | V6/V7/V10 completan vínculos locales y destinos externos tipados; d2.task_sources permite trazabilidad directa |
| F11 mediciones/ventanas | V5 límites de porcentaje, recurso de attempt y pares temporales completos |
| F12 inmutabilidad | V5/V8/V10 protegen hechos, artefactos, evidencia y payload del outbox; runtime sin permisos SQL de mutación |
| F13 incidentes | V5 timestamps/versión; V9 transición resuelve/reabre con historial, auditoría de severidad y replan |
| F14 discrepancias del modelo | D2.8 reconcilia nombres/campos, catálogos MVP y ampliación explícita 68→69 arcos |

Esto significa que hay una corrección o contrato ejecutable para los hallazgos dentro del entorno de validación. No significa que se haya desplegado, que el SQL legado sea seguro con permisos de propietario ni que los servicios definitivos estén implementados.

## Estado de las decisiones de revisión

- **Aprobado D2-A01:** diario append-only con vistas reconstruibles; cuentas físicas y diario legado separados.
- Mutex global de validación y mutex de publicación adquirido antes de locks de filas.
- **Aprobado D2-A02:** arco adicional BLOCKED_APPROVAL→RECONCILING ante evidencia nueva y concluyente.
- **Aprobado D2-A03:** reintentos por defecto 3, rango configurable 1–20. Vocabularios MVP aprobados (D2-A07); separación de roles aprobada (D2-A08). **Aprobado D2-A04:** bloqueo global conservador, sin llamadas externas bajo locks. **Requisito D2-A05:** SemVer completo antes del cierre; validado con rangos npm aprobados (D2-A06), V11, 29.829 vectores y la batería completa de 157 pruebas.
- Modelo de roles y permisos; política de conservación sin borrado automático hasta aprobar D6.
- Alcance de pruebas con recibos simulados y requisitos posteriores de workers/conectores reales.

El usuario aprobó cerrar D2 condicionado a la validación satisfactoria. Esa condición se cumplió. La promoción de migraciones y el comienzo de implementación completa conservan aprobación separada.

**Aprobado D2-A09:** retención MVP sin borrado automático hasta política D6. **Aprobado D2-A10:** alcance sintético de D2 e integraciones reales D3–D6, manteniendo SemVer completo como requisito de cierre. No quedan consultas de diseño sin respuesta; SemVer quedó validado y el cierre aprobado se hizo efectivo.

Las respuestas explícitas y el cierre están en el [registro de decisiones](../design/D2-DECISIONS.md).
