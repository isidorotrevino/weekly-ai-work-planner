# D2 — registro de decisiones

Fecha: 2026-10-17. D1 permanece aprobado. **D2 cerrado y aprobado** tras validación satisfactoria y aprobación condicionada expresa del usuario. El cierre no promueve migraciones ni autoriza la implementación completa.

Este registro recoge las respuestas explícitas del usuario y las condiciones de aprobación. El contrato ejecutable se describe en [D2 aprobado](D2.9-approved.md); su evidencia y límites están en la [matriz de validación](../validation/D2-VALIDATION-MATRIX.md).

## Decisiones aprobadas

| ID | Decisión | Condiciones y alcance |
|---|---|---|
| D2-A01 | Cuentas físicas por recurso y ventana real, compartidas entre versiones del plan, con diario inmutable y saldos reconstruibles | Replanificar no crea cuota. Se separan compromiso y consumo, conservando 70/20/10 por recurso. No se exige partida doble formal. Respuesta del usuario: «Aprobar diario y cuentas físicas». |
| D2-A02 | BLOCKED_APPROVAL→RECONCILING ante evidencia nueva y concluyente | La transición no reintenta automáticamente el efecto externo. Una aprobación no sustituye la evidencia de reconciliación. Respuesta del usuario: «Aprobar la transición protegida». |
| D2-A03 | Tres intentos totales por defecto; máximo configurable de veinte | Son intentos totales, incluido el inicial. El reintento solo se permite si hay evidencia de que es seguro; los efectos ambiguos se bloquean. Respuesta del usuario: «3 intentos totales; máximo configurable de 20». |
| D2-A04 | Mantener inicialmente el bloqueo transaccional global conservador del MVP | Sin llamadas externas bajo locks. Refinar por cuenta/recurso cuando las mediciones lo justifiquen, conservando integridad y repitiendo pruebas de concurrencia. Respuesta del usuario: «Aprobar el enfoque conservador para el MVP». |
| D2-A05 | Exigir un intérprete SemVer completo antes de cerrar D2 | Se rechaza aceptar como suficiente el subconjunto actual. La gramática queda fijada en A06; la condición está cumplida por la validación V11 registrada abajo. Respuesta del usuario: «Exigir un intérprete SemVer completo antes de cerrar D2». |
| D2-A06 | SemVer 2.0.0 y rangos compatibles con npm/node-semver | Comparadores, AND/OR, guiones, comodines, caret y tilde; prereleases solo cuando el rango las admite expresamente. Respuesta del usuario: «SemVer 2.0.0 y rangos npm». |
| D2-A07 | Vocabularios MVP propuestos en V10 | Requisitos: DRAFT/READY/APPROVED/REJECTED/ARCHIVED. Épicas: BACKLOG/READY/IN_PROGRESS/BLOCKED/VERIFYING/DONE/CANCELLED/FAILED/DEFERRED. Intentos: LEASED/RUNNING/VERIFYING/COMPLETED/FAILED/CANCELLED/RECONCILING. Entradas del plan: PLANNED/DEFERRED/CANCELLED. Respuesta: «Aprobar los estados propuestos». |
| D2-A08 | Separar propietario/migrador, control plane, verificador y administrador de capacidad | Workers sin credenciales SQL; permisos concretos de despliegue por validar en D6. Respuesta del usuario: «Aprobar la separación de roles». |
| D2-A09 | Retención MVP sin borrado automático hasta aprobar la política de D6 | Conservar metadatos, revisiones, diario y evidencia referenciada; archivar agregados. La política de duración, acceso y recuperación se aprobará en D6 antes de habilitar borrado automático. Respuesta del usuario: «Aprobar la retención propuesta». |
| D2-A10 | Reparto de validación: persistencia y concurrencia sintéticas en D2; integraciones reales en D3–D6 | Cuotas comerciales, workers/CLI y APIs reales se validarán en D3–D6. SemVer completo sigue siendo obligatorio antes del cierre. Esta aceptación no aprueba cerrar D2. Respuesta del usuario: «Aceptar este reparto de validación». |

Las propuestas V8/V9 ya ejercitan A01–A04 con pruebas sintéticas. A05/A06 están validados por V11, 157 pruebas JUnit y 29.829 vectores SemVer sin discrepancias. V1–V10 conservan sus bytes; V11 añade el contrato SemVer validado. Los adaptadores reales conservan su validación posterior en D3–D6.

## Estado de las consultas

Todas las consultas de diseño presentadas hasta ahora tienen respuesta. P06 quedó aprobado como A09 y P07 como A10. No hay consultas de diseño pendientes de respuesta; la validación SemVer y la aprobación de cierre se completaron después, como se registra abajo.

## Validación y cierre

V11 amplía `d2.compatible` conforme a A05/A06. La auditoría completa ejecutada en Docker pasó **157 pruebas JUnit**, sin fallos, errores ni omisiones, incluyendo **29.829 vectores** contra npm/node-semver 7.7.2 y un upgrade V10→V11. El [informe SemVer](D2-SEMVER-VALIDATION.md) documenta límites y resultados; la [evidencia portable](../validation/semver-evidence.json) conserva hashes y conteos.

El usuario dio la autorización expresa condicionada: «validalo y si es exitoso apruebo el cierre de D2». La condición quedó satisfecha en la ejecución del 2026-10-17; **D2 queda cerrado y aprobado**. D1 permanece intacto. No se ha autorizado el despliegue, la promoción de migraciones ni la implementación completa.

Las validaciones reales de D3–D6 y la política operativa de retención siguen el reparto aprobado en A09/A10; son trabajo posterior, no comprobaciones ejecutadas por el prototipo D2.
