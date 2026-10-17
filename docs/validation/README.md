# Validation / Validación

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
