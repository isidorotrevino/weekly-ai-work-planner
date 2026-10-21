# Validation / Validación

Estado vigente D4: **alcance sintético aprobado y cerrado** el 2026-10-20.
[Documento aprobado](../design/D4-approved.md) · [Manifiesto](D4-CLOSURE.json).
Los informes D4 siguientes conservan sus estados al emitirse, incluidos OPEN y
aprobación pendiente; la decisión posterior consta en el manifiesto, sin reescribir
resultados ni autorizar promoción o despliegue.

Estado vigente: [D3 aprobado y cerrado como MVP conservador 1.0](../design/D3-approved.md), con [manifiesto de cierre](D3-CLOSURE.json). Los informes y notas «D3 abierto» siguientes conservan el estado al emitirse; no implican falta de aprobación actual. No hay despliegue aprobado.
The recorded D2 audit completed **157 checks, zero failures, zero errors, and zero skipped checks** on October 17, 2026, with PostgreSQL 16.15, Java 21, and Flyway 13.10.3 in Docker.

La auditoría registrada de D2 completó **157 comprobaciones sin fallos, errores ni omisiones** el 17 de octubre de 2026, con PostgreSQL 16.15, Java 21 y Flyway 13.10.3 en Docker.

## What the result means / Qué significa

- 78 historical checks characterize V4/V5 gaps and validate the first V6 corrections. Historical `OPEN` cases pass when an old gap is reproduced.
- 79 contract checks exercise the proposed persistence contracts: capacity accounting, concurrent claims/reservations, transitions, fencing, recovery decisions, dependency cycles, immutable snapshots, approvals, and provenance.
- One SemVer contract test checks 29,829 vectors against pinned npm/node-semver 7.7.2. Separate checks cover ordering, limits, SQL guards and V10→V11 upgrade.
- External effects and checkpoints are simulated trusted receipts. No AI provider, Git operation, cloud API, or real worker was exercised.
- The validation kernel uses conservative global locking. Scalability and production deployment have not been validated. D2 is approved and closed under the user’s conditional approval after this successful validation.

Las 78 comprobaciones históricas incluyen reproducciones de defectos anteriores; las 79 de contratos ejercitan los contratos propuestos. Los recibos externos son simulaciones. Este resultado no acredita un sistema completo, servicios externos reales ni preparación para producción.

## Reproduce / Reproducir

From the repository root / Desde la raíz:

```bash
bash testing/D2/run-docker-audit.sh
```

See the [audit guide](../../testing/D2/README.md) for requirements and local PostgreSQL execution. The runner creates disposable databases and prints the evidence directory. Keep raw logs, database files, container metadata, and JUnit XML local; they may contain machine-specific information.

La batería crea bases desechables e indica la carpeta de evidencia. Los logs, archivos de base, metadatos de contenedores y XML JUnit se conservan localmente, excluidos de Git, porque pueden incluir datos del entorno.

## References / Referencias

- [Portable result summary](latest-results.json).
- [Detailed D2 validation matrix](D2-VALIDATION-MATRIX.md).
- [Approved D2 design](../design/D2.9-approved.md).

This summary is a recorded result, not a CI status badge. Re-run validation after changing executable inputs or the transition document consumed by tests.

Este resumen es un resultado registrado, no un indicador de CI. Repite la validación si cambian fuentes ejecutables o la especificación de transiciones que consumen las pruebas.

D2 está cerrado y aprobado como diseño. La implementación completa y el despliegue conservan aprobación separada. Los [hashes de entradas y conteos](semver-evidence.json) y el [informe SemVer](../design/D2-SEMVER-VALIDATION.md) completan la evidencia portable.

## D3 — coordinación invocable

La [evidencia del coordinador](D3-COORDINATOR-results.json) mantiene separados núcleo, I2, I3, coordinación y regresión histórica D2. [Contrato y límites](../design/D3-COORDINATOR.md). V14 se prueba en una plantilla propia; los grupos históricos no se presentan como si se hubieran ejecutado sobre V14. D3 sigue abierto, sin daemon, workers reales ni despliegue aprobado.

## Revisión integrada D3

La [evidencia de revisión](D3-REVIEW-results.json) añade aceptación V15 y cuatro mediciones de escala, manteniendo los grupos previos separados. LIMIT_EXCEEDED valida el aborto seguro, no rendimiento completado. [Alcance y decisiones pendientes](../design/D3-REVIEW.md). D3 sigue abierto.

## Optimización D3 autorizada por 2A

[Resultados de optimización](D3-OPTIMIZATION-results.json) y [alcance aprobado por 1A](../design/D3-OPTIMIZATION.md): fuente previa exacta, tres pruebas diferenciales/82 escenarios, cuatro mediciones idénticas y regresiones separadas. El núcleo cambió intencionadamente; los informes históricos y su código de referencia se conservan. Una medida no fija SLA ni cierra D3.

## D4 — integración sintética

[Resultados I4](D4-I4-results.json) separan campaña Compose, componentes D4, upgrade
V17→V18 y regresión D2. Los manifiestos D3 y sus 25 hashes de cierre se conservan.
[Alcance y límites](../design/D4-I4-LAB.md). D4 permanece abierto y sujeto a revisión.

[D4 I5](D4-I5-results.json) registra checkpoint parcial, S01–S05 y regresiones D3/D2
en copia, con targets históricos separados de V21. D4 permanece abierto.

[D4 I6](D4-I6-results.json) registra S01–S09 (283 comprobaciones), 84 pruebas D4,
175 D3 y 157 D2, con targets históricos separados de V22. Incluye una reproducción
del bloqueo con un carrier antes de la corrección y validación posterior de la
parada. Solo las ejecuciones finales verdes acreditan PASS; D4 permanece abierto.

[D4 I7](D4-I7-results.json) registra S01–S12 (367 comprobaciones), 92 pruebas D4,
175 D3 y 157 D2, con sus targets históricos separados de V23. La política del bucle
tras checkpoint estaba pendiente en esa campaña; no se acredita allí una nueva campaña automática
de checkpoint. D4 permanece abierto.

[A12 / S13](D4-I7-A12-results.json) registra la decisión posterior de pausar todo
el bucle tras CHECKPOINT_READY y exigir rearme explícito. Es una campaña acotada
separada; no sobrescribe I7 ni convierte sus doce escenarios en una repetición
actual. Incluye regresión de checkpoint/retirada y de las baterías históricas.
D4 sigue abierto, sin promoción ni despliegue.

[I8.1: componentes](D4-I8-COMPONENTS-results.json) registra cálculo multidimensional
y verificadores locales de archivos/Git/restauración. No acredita liquidación SQL
multicuentas, importación de objetos candidatos ni nueva campaña Compose.

[I8.2: integración multicuentas](D4-I8-INTEGRATION-results.json) registra por
separado V24, SQL/HTTPS y Compose S14 con regresiones v1 S05/S13. No sobrescribe
los informes de componentes ni los resultados históricos. D4 abierto.

[Revisión de fronteras V24](D4-V24-BOUNDARY-results.json) separa reproducciones
de dos defectos en target 24 de la validación positiva de la corrección propuesta
V25 y de la campaña S15/S14/S13. D4 continúa abierto.

[Esquema cerrado V25, A16](D4-V25-CLOSED-SCHEMA-results.json) registra la
validación posterior a la elección expresa del usuario, sin sobrescribir el informe
provisional de fronteras. D4 abierto.

[I9: resolución concluyente y recuperación v1/v2](D4-I9-RECONCILIATION-results.json)
conserva los recibos históricos, separa checkpoint parcial y aceptación terminal,
y mantiene D4 abierto bajo A17–A19.

[I10.1: ausencia sin progreso y retry explícito](D4-I10-ABSENCE-results.json)
registra A20: 201 pruebas D4, 25 verificadores locales y 169 comprobaciones
Compose S20/S21/S16/S19, con limpieza de sus cuatro proyectos. A21/A22 continúan
aprobadas y pendientes de integración; D4 permanece abierto.

## D4 I11 — A21/A22

[Resultados independientes](D4-I11-REVIEW-QUARANTINE-results.json) de revisiones sin
nueva liquidación, cuarentena separada, contención y cierre explícito.
[Contrato y límites](../design/D4-I11-REVIEW-QUARANTINE-LAB.md). Los informes previos
conservan sus resultados y targets históricos; D4 sigue abierto.

## D4 I12 — verificadores Java, presencia y aceptación final

[Informe I12](D4-I12-INTEGRATED-results.json), con pruebas D4 y regresión D2/D3
separadas, matriz actual V30, pilotos excluidos y cleanup selectivo.
[Revisión final del alcance](../design/D4-I12-ACCEPTANCE-REVIEW.md).
El informe prepara la decisión del usuario; no constituye cierre D4 ni promoción.

## D5 — local source persistence / persistencia local de fuentes

[D5 I4](D5-I4-results.md) records a separate synthetic PostgreSQL campaign and D2
regression. [Implementation and limits](../design/D5-I4-PERSISTENCE-LAB.md).
D5 remains open; no task activation, migration promotion or deployment.

[D5 I4](D5-I4-results.md) registra una campaña PostgreSQL sintética independiente
y regresión D2. [Implementación y límites](../design/D5-I4-PERSISTENCE-LAB.md).
D5 sigue abierto; sin activación de tareas, promoción ni despliegue.

[D5 I5](D5-I5-results.md) adds stored comparisons, per-row review and application
simulation, with separate evidence. No operational application to D2 tasks.

[D5 I5](D5-I5-results.md) añade comparaciones persistidas, revisión por fila y
simulación de aplicación, con evidencia propia. Sin aplicación operativa a tareas D2.

[D5 I6](D5-I6-results.md) records fresh V30 → V31/V32 SQL coexistence, with D5
regressions and five new compatibility cases. D4 process/HTTPS evidence stays historical.

[D5 I6](D5-I6-results.md) registra coexistencia SQL V30 → V31/V32 en una base nueva,
con regresiones D5 y cinco casos nuevos. La evidencia de procesos/HTTPS D4 se conserva.
