# D4 — decisiones y alcance de preparación

Actualizado: 2026-10-20, Europe/Madrid. **D4 sintético aprobado y cerrado.** [Alcance vigente](D4-approved.md) y [manifiesto](../validation/D4-CLOSURE.json).

Autoridad: petición de iniciar diseño y preparar el primer corte del laboratorio,
tras leer [HANDOFF-D4](../../HANDOFF-D4.md). D1/D2/D3 siguen cerrados y aprobados.
D2 publicado: `69d71c3877e79bdfef088956b090d4eb6b447be9`; D3 conserva su
[referencia local](../validation/D3-CLOSURE.json), sin commit publicado atribuido.

## Respuestas expresas de esta sesión

| ID | Elección del usuario | Consecuencia y frontera |
|---|---|---|
| D4-A01 | «A: mTLS y catálogo autorizado» | CA efímera de laboratorio, certificado ligado a worker; el servidor autoriza asignación y capacidades. Anunciar capacidades no las concede |
| D4-A02 | «A: supervisor dentro de cada worker» | Vertical sintética Java 21/Spring Boot, dos workers y receptor durable; subprocesos de fixtures confiables, sin socket Docker. Primera campaña: éxito, competencia, callback perdido y proceso superviviente |
| D4-A03 | «A: diseñar continuidad explícita» | Diseñar transición aditiva para la misma operación con nuevo intento/generación y contabilidad conservada. Autoriza diseñarla; no aprueba aún su transición concreta ni implementar cambios de contratos D2/D3 |
| D4-A04 | «A: demostrar bloqueo; resolución posterior» | UNKNOWN y contradicciones mantienen compromiso y exclusión. Resolución concluyente aditiva fuera del primer corte |
| D4-A05 | «B: continuidad con efectos parciales» | Diseñar continuidad por pasos APPLIED verificados, liquidación parcial y sufijo pendiente; requiere revisar la transición concreta. Se descarta limitar el diseño a checkpoints sin efectos |
| D4-A06 | «A: grant acotado y cierre durable» | Grant ligado a identidad/lease D2, cierre durable serializado con aplicación y parada probada antes de retirar exclusión; sin consulta online adicional por cada efecto |
| D4-A07 | «A: TOP_UP conservador al vector original» | Continuación conserva el compromiso objetivo del vector congelado, aunque haya menor coste residual. No se añade una estimación residual que cambie TOP_UP |
| D4-A08 | «A: CANCELLED→READY solo con procedencia de checkpoint sellada y autorización explícita» | Contrato I5 aprobado para implementar en el laboratorio; cancelación ordinaria no continúa |
| D4-A09 | «A: checkpoint desde RUNNING con lease vigente; si vence antes del commit, conservar compromiso y exigir reconciliación» | Commit parcial solo en lease viva; ruta desde RECONCILING excluida del primer incremento |
| D4-A10 | «A: parar ante el primer ciclo fallido» | Ejecución prolongada: iniciar parada tras una renovación no confirmada después de un reintento acotado; watchdog independiente conserva el límite del último grant confirmado |
| D4-A11 | «A: solicitar cooperación por canal local ligado al intento» | Solicitud durante ejecución; si no coopera dentro del límite, parada y bloqueo sin checkpoint válido. La lease debe seguir vigente en COMMIT |
| D4-A12 | «A: pausar todo el bucle y exigir rearme explícito después del checkpoint» (2026-10-20) | CHECKPOINT_READY pausa todo polling; sellado y autorización de continuidad no rearman el bucle. Nuevo comando explícito después de retirar el estado local. Conserva operación, reserva, contador D2 y TOP_UP original |
| D4-A13 | «A: cadena lineal acotada» (2026-10-20) | Hasta 32 pasos/8 cuentas; primera campaña de tres pasos, dos cuentas y dos checkpoints. Sin ramas; cada continuación consume un intento D2 |
| D4-A14 | «A: vector exacto congelado» (2026-10-20) | Coste sintético exacto por paso/cuenta antes de CLAIM; liquidación incremental por APPLIED verificado; cero coste de reinicio explícito solo en fixture. TOP_UP original completo por cuenta |
| D4-A15 | «A: Git y restauración local» (2026-10-20) | Objetos y árbol completo en repositorio sintético del verificador; rollback solo de archivos. APPLIED y consumo no se deshacen; sin compensación externa |
| D4-A16 | «A: esquema cerrado (recomendada)» (2026-10-20) | V25 rechaza campos adicionales en manifiesto v2, paso y cuenta. Intenciones antiguas incompatibles se conservan, pero no admiten nuevos CLAIM, grants, pruebas ni continuidad; los hechos ya comprometidos no se transforman |
| D4-A17 | «A: resolución monotónica del receptor» (2026-10-20) | Cierre concluyente del mismo receptor/diario; no revocar APPLIED ni resolver hashes incompatibles o pérdida de diario |
| D4-A18 | «A: reutilizar continuidad sellada» (2026-10-20) | Recuperación parcial RECONCILING→CANCELLED sellada, autorización y rearme explícitos; BLOCKED_APPROVAL retorna primero a RECONCILING sin liberar en ese retorno |
| D4-A19 | «B: incluir v1 y recuperación terminal» (2026-10-20) | Incluir v1 y v2, continuación parcial y caso completamente APPLIED; aceptación final independiente, sin nuevo intento para recuperar resultados completos |
| D4-A20 | «A: sello de ausencia y retry explícito» (2026-10-20) | RECONCILING→RETRY_PENDING con parada y cierre independientes; autorización expresa a READY. Misma operación/reserva/contador y TOP_UP original, sin checkpoint ficticio |
| D4-A21 | «A: revisión verificada con delta cero» (2026-10-20) | Revisión append-only sin volver a CONSUME/RELEASE, invalida autorizaciones anteriores; no levanta cuarentena ni rearma por sí sola |
| D4-A22 | «A: caso separado y cuarentena» (2026-10-20) | Conserva CANCELLED/COMPLETED, PASS y consumo históricos; suspende aceptación efectiva, bloquea admisiones/consumidores afectados y exige contención física independiente antes del cierre explícito del caso |
| D4-A23 | «B: portar verificadores a Java» (2026-10-20) | Verificación dentro del servicio HTTPS; Git sintético del verificador, sin importar .git del worker ni compensar APPLIED |
| D4-A24 | «A: sesión y secuencia durable» (2026-10-20) | Incarnación autorizada y secuencia monotónica; vencimiento/reemplazo bloquea nuevas admisiones, no libera reservas/leases ni acredita parada; rearme explícito |

Las alternativas B de identidad y aislamiento quedan descartadas para este corte.
No se vuelven a consultar proveedores reales ni máquinas físicas: están excluidos
por la petición. Sin credenciales reales, promoción, despliegue o cierre automático.

## Revisión todavía necesaria

La propuesta concreta de continuidad está en [diseño técnico](D4-workers-draft.md).
La aceptación de la ruta concreta A/A quedó registrada en A08/A09; se conservan
las precondiciones, liquidación parcial y pruebas de upgrade allí aprobadas.
No se habilita por HTTP una llamada directa a `d2.preempt`: I5 usa sus entradas
D4 de solicitud, prueba independiente y commit, ligadas a la identidad exacta.
I6 añade la señal cooperativa bajo A10/A11. No se modifica V1–V15.

La [propuesta de continuidad con efectos parciales](D4-CHECKPOINT-CONTINUATION.md)
concreta prueba por paso, cierre, consumo y arco candidato. A07 resuelve TOP_UP:
se conserva el vector original. La revisión concreta [I5](D4-I5-REVIEW.md) recibió aprobación A/A (A08/A09).
Su [implementación acotada](D4-I5-CHECKPOINT-LAB.md) no autoriza ampliar a
RECONCILING, resolver contradicciones ni cerrar D4.

La implementación avanza por incrementos separados: [I1 entrega](D4-I1-DELIVERY.md),
[I2 HTTPS/mTLS](D4-I2-HTTPS.md), [I3 supervisor/receptor](D4-I3-PROCESS-EFFECTS.md)
y [I4 integración Compose/verificador](D4-I4-LAB.md). La petición expresa de conectar
los componentes, construir Compose y ejecutar los cuatro escenarios autoriza I4
sintético. No aprueba el cierre de D4. A08/A09 posteriores autorizan la continuidad
acotada del laboratorio, documentada en I5.
A10/A11 autorizan la [ejecución prolongada y cooperación I6](D4-I6-LONG-RUNNING-LAB.md)
con las alternativas conservadas en su [revisión](D4-I6-LONG-RUNNING-REVIEW.md).

I7 [implementa y valida](D4-I7-POLLING-LAB.md) el polling normal y la retirada verificada, conservando los contratos
anteriores. La [decisión A12](D4-I7-POLLING-REVIEW.md) aprueba la opción A:
pausa del bucle completo y rearme explícito tras checkpoint. El informe I7 original
conserva el estado pendiente que tenía al ejecutarse; S13 valida la decisión posterior
en una campaña separada, sin ampliar los contratos SQL ni cerrar D4.

A13–A15 aprueban las opciones A de la [revisión I8](D4-I8-GENERALIZATION-REVIEW.md).
El diseño y los componentes deben distinguirse de la integración SQL/HTTPS y Compose
efectivamente ejecutada; no se infiere cierre de D4.

A13/A14 se concretan en la [integración SQL/HTTPS y Compose I8.2](D4-I8-INTEGRATION.md),
con rutas v2 separadas. A15 conserva su alcance local; no implica compensación
de efectos ni importación Git desde workers. No se añade aprobación de cierre.

La [revisión de fronteras de V24](D4-V24-BOUNDARY-REVIEW.md) corrige tipos y plazo
con V25 propuesta. A16 aprueba el esquema cerrado de campos adicionales; se conserva
la historia sin admitir nuevas acciones sobre intenciones incompatibles.

A17–A19 amplían A04/A09 mediante la [ruta I9](D4-I9-RECONCILIATION-LAB.md): resolución concluyente y checkpoint desde reconciliación, incluyendo v1 y recuperación terminal. Los entrypoints anteriores conservan sus guardas.

A20–A22 registran las opciones A de [I10](D4-I10-REOPENING-REVIEW.md).
[I10.1](D4-I10-ABSENCE-LAB.md) concreta la implementación de ausencia sin progreso;
En ese corte A21/A22 seguían pendientes de integración y validación; I11 recoge
la ampliación posterior.

A21/A22 se concretan en [I11: revisiones y cuarentena](D4-I11-REVIEW-QUARANTINE-LAB.md),
con V28 propuesta y campañas separadas. A20/I10.1 e informes anteriores mantienen
su alcance histórico. D4 no queda cerrado por esta ampliación.

A23=B y A24=A se implementan en [I12](D4-I12-INTEGRATED-VERIFIERS-PRESENCE.md):
port Java integrado con aceptación SQL/HTTPS, sesiones durables, matriz sobre V30
y polling/reinicio con revisiones. La aprobación de estas opciones no cierra D4.

## D4-CLOSE-01 — aprobación expresa del cierre sintético

El 2026-10-20 el usuario respondió **«A: aprobar cierre de D4 sintético»** a la
revisión final I12 (638 pruebas, 1.085 comprobaciones, 30 escenarios V30 y limpieza
confirmada). Cierra únicamente el [alcance sintético documentado](D4-approved.md),
sin promoción ni despliegue. Esta decisión posterior satisface la condición de
cierre pendiente en los cortes históricos; A01–A24 conservan sus límites.

Ratificación y publicación, 2026-10-21: el usuario solicita «publica en git, y se
aprueba el cierre de D4». Ratifica D4-CLOSE-01 sin ampliar su alcance y autoriza
publicar los cambios pendientes y preparar el [handoff de desarrollo](../../HANDOFF-DEV-ENV.md).
