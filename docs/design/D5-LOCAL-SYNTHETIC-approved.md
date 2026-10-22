# D5 — hito local sintético aceptado

Fecha: **2026-10-22**, Europe/Madrid. Versión: **1.0**.
Estado: **ACEPTADO exclusivamente el hito `D5-LOCAL-SYNTHETIC-I1-I20`**.
**D5 global permanece abierto con G01–G07.**
[Registro verificable de aceptación](../validation/D5-LOCAL-SYNTHETIC-ACCEPTANCE.json) ·
[Propuesta aceptada I22](D5-I22-LOCAL-MILESTONE-ACCEPTANCE.md) ·
[Auditoría I21](D5-I21-SCOPE-AUDIT.md).

English: the user explicitly accepted the bounded local synthetic source/BACKLOG
lab milestone, not the complete D5 integration deliverable. Global D5 remains
open. This records an acceptance decision; it adds no SQL, runtime campaign,
provider access, activation, promotion, deployment or D6 scope.

## Decisión y referencias

**D5-A52**, respuesta expresa del usuario:

> A: aceptar exclusivamente el hito local descrito y registrar esta decisión,
> manteniendo D5 global abierto (recomendada).

La pregunta aceptada fija el hito `D5-LOCAL-SYNTHETIC-I1-I20` sobre base ejecutable
`d20f375`, criterios H01–H12, evidencias y exclusiones de I22. Precisa que D5 global
sigue abierto con G01–G07 y que esta aceptación no autoriza funciones nuevas,
activación, proveedores reales, promoción, despliegue ni D6.

| Referencia | Base exacta |
|---|---|
| Implementación aceptada I1–I20 | `d20f375f3eb45213d0d759f0530c056dd5ac251b` |
| Clasificación I21, aceptada por A51 | `2b18d6c40ee19217a3a95136a2cf0a7203b509a4` |
| Propuesta I22, aceptada por A52 | `b556193d52484cf88cbd1ca2bb9bf96f9d94afd7` |
| Evidencia ejecutada de referencia | [Informe I20](../validation/D5-I20-results.md) y [JSON I20](../validation/D5-I20-results.json) |

El documento presente y su registro reflejan la aceptación vigente del hito local.
I21/I22 e informes anteriores conservan sus estados históricos al emitirse:
«pendiente», «propuesta» o «D5 abierto» no revocan A52 ni se reescriben para atribuir
la aceptación a una fecha anterior. La publicación autorizada de I22 se verificó
en `main`; la autorización de publicar aquel commit no se extiende al registro nuevo.

## Alcance aceptado

Se aceptan H01–H12 de I22 con sus límites: captura local de bytes/hash/procedencia;
perfiles explícitos I1/I2/I3; almacenamiento de observaciones y referencia CAS;
comparación y revisión íntegra; simulación y aplicación revisada a tareas BACKLOG;
bootstrap explícito; reaparición con prueba de ausencia aplicada e identidad;
resolución de texto completo origen/local, incluida la aislada; adopción elegible
sin alterar la tarea; recibos, replay, atomicidad y recuperación; separación de
roles/laboratorios y ausencia de activación.

La unidad es un laboratorio Linux/Python/CLI y PostgreSQL desechable sintético
V30 + propuestas V31–V39, separado de dev/D4. Proyección Item→title y
Objective→description únicamente; estados, verificaciones y anotaciones del origen
siguen siendo evidencia inerte. Una ausencia no borra ni cierra tareas. Las
condiciones exactas de cada variante y las exclusiones E01–E07 permanecen en I22;
no se acepta una generalización a cualquier fuente, tarea o integración.

La última campaña I20 registra 264 pruebas SQL, 51 locales y 157 D2 independientes
sin fallos/errores. Los targets y campañas solapadas no se suman como ejecuciones
nuevas. El estado final registrado contiene 259 tareas BACKLOG sintéticas y cero
operaciones, intentos, outbox, entregas y reservas, con limpieza propia completada.
La fixture negativa A18 sigue limitada a transacción revertida, sin ejecución.

Esta aceptación es documental: no se ha reejecutado Docker, SQL, parser, D2 ni D4.
El registro verifica hashes actuales y de los commits de referencia; no acredita
un entorno nuevo, ausencia total de defectos, seguridad productiva o exactly-once
externo. D1–D4 conservan sus contratos, cierres y evidencias.

## D5 global y exclusiones vigentes

| Brecha | Continuidad D5 todavía abierta |
|---|---|
| G01 | Contrato completo Gentle-AI/routing y muestras representativas |
| G02 | Ingesta incremental/revisiones remotas de Drive |
| G03 | Sincronización Plane con conflictos, idempotencia y conciliación |
| G04 | Validación real de adaptadores/CLI y cuotas comerciales |
| G05 | Contratos de requisitos, épicas y grooming más allá de BACKLOG |
| G06 | Decisión integrada de perímetro y aceptación de D5 global |
| G07 | Evidencia de validación integrada de los contratos globales |

Estas brechas siguen en D5; no se trasladan a D6 ni se dan por satisfechas con
pruebas locales. IDs reutilizados/transferencias, adopción avanzada, conversiones
de perfil, fusión y dev/UI/servicio son extensiones fuera de este hito. Sheets/Monday
sigue opcional según D1.

Proveedores y credenciales reales, activación, promoción, despliegue y ampliación
D6 siguen fuera de autorización. A52 no inicia trabajo sobre G01–G07 ni E01–E07:
el siguiente incremento material requiere elegir alcance y contrato propios.
No existe por esta decisión un cierre global D5 ni se crea un manifiesto D5-CLOSURE.
