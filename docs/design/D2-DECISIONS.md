# D2 — registro de decisiones

Fecha: 2026-10-17. D1 permanece aprobado. **D2 sigue abierto**: aprobar decisiones individuales no aprueba su cierre, una promoción de migraciones ni la implementación completa.

Este registro recoge respuestas explícitas del usuario y distingue propuestas pendientes. El contrato ejecutable se describe en [D2.8](D2.8-consolidated-review.md); su evidencia y límites están en la [matriz de validación](../validation/D2-VALIDATION-MATRIX.md).

## Decisiones aprobadas

| ID | Decisión | Condiciones y alcance |
|---|---|---|
| D2-A01 | Cuentas físicas por recurso y ventana real, compartidas entre versiones del plan, con diario inmutable y saldos reconstruibles | Replanificar no crea cuota. Se separan compromiso y consumo, conservando 70/20/10 por recurso. No se exige partida doble formal. Respuesta del usuario: «Aprobar diario y cuentas físicas». |
| D2-A02 | BLOCKED_APPROVAL→RECONCILING ante evidencia nueva y concluyente | La transición no reintenta automáticamente el efecto externo. Una aprobación no sustituye la evidencia de reconciliación. Respuesta del usuario: «Aprobar la transición protegida». |
| D2-A03 | Tres intentos totales por defecto; máximo configurable de veinte | Son intentos totales, incluido el inicial. El reintento solo se permite si hay evidencia de que es seguro; los efectos ambiguos se bloquean. Respuesta del usuario: «3 intentos totales; máximo configurable de 20». |
| D2-A04 | Mantener inicialmente el bloqueo transaccional global conservador del MVP | Sin llamadas externas bajo locks. Refinar por cuenta/recurso cuando las mediciones lo justifiquen, conservando integridad y repitiendo pruebas de concurrencia. Respuesta del usuario: «Aprobar el enfoque conservador para el MVP». |
| D2-A05 | Exigir un intérprete SemVer completo antes de cerrar D2 | Se rechaza aceptar como suficiente el subconjunto actual. La gramática queda fijada en A06; falta demostrar el contrato completo. Respuesta del usuario: «Exigir un intérprete SemVer completo antes de cerrar D2». |
| D2-A06 | SemVer 2.0.0 y rangos compatibles con npm/node-semver | Comparadores, AND/OR, guiones, comodines, caret y tilde; prereleases solo cuando el rango las admite expresamente. Respuesta del usuario: «SemVer 2.0.0 y rangos npm». |
| D2-A07 | Vocabularios MVP propuestos en V10 | Requisitos: DRAFT/READY/APPROVED/REJECTED/ARCHIVED. Épicas: BACKLOG/READY/IN_PROGRESS/BLOCKED/VERIFYING/DONE/CANCELLED/FAILED/DEFERRED. Intentos: LEASED/RUNNING/VERIFYING/COMPLETED/FAILED/CANCELLED/RECONCILING. Entradas del plan: PLANNED/DEFERRED/CANCELLED. Respuesta: «Aprobar los estados propuestos». |
| D2-A08 | Separar propietario/migrador, control plane, verificador y administrador de capacidad | Workers sin credenciales SQL; permisos concretos de despliegue por validar en D6. Respuesta del usuario: «Aprobar la separación de roles». |
| D2-A09 | Retención MVP sin borrado automático hasta aprobar la política de D6 | Conservar metadatos, revisiones, diario y evidencia referenciada; archivar agregados. La política de duración, acceso y recuperación se aprobará en D6 antes de habilitar borrado automático. Respuesta del usuario: «Aprobar la retención propuesta». |
| D2-A10 | Reparto de validación: persistencia y concurrencia sintéticas en D2; integraciones reales en D3–D6 | Cuotas comerciales, workers/CLI y APIs reales se validarán en D3–D6. SemVer completo sigue siendo obligatorio antes del cierre. Esta aceptación no aprueba cerrar D2. Respuesta del usuario: «Aceptar este reparto de validación». |

Las propuestas V8/V9 ya ejercitan A01–A04 con pruebas sintéticas. A05 es un requisito aprobado cuya validación sigue pendiente. Esta aprobación no cambia los bytes de las migraciones ni afirma que los adaptadores reales estén validados.

## Estado de las consultas

Todas las consultas de diseño presentadas hasta ahora tienen respuesta. P06 quedó aprobado como A09 y P07 como A10. No hay consultas de diseño pendientes de respuesta; sí trabajo técnico pendiente y una aprobación final de cierre todavía no solicitada.

## Trabajo técnico obligatorio antes del cierre

- Sustituir o ampliar el contrato acotado de `d2.compatible` y demostrar SemVer completo conforme a A05. Las 147 pruebas existentes no demuestran este requisito.
- Validar la gramática de rangos aprobada en A06. El [plan de validación SemVer](D2-SEMVER-VALIDATION.md) detalla el contrato aprobado y la evidencia todavía pendiente.

## Revisión restante

- Aprobación expresa del cierre de D2, en un paso separado al finalizar estas decisiones.
