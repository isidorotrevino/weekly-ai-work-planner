# Validation / Validación

The recorded D2 audit completed **147 checks, zero failures, zero errors, and zero skipped checks** on October 17, 2026, with PostgreSQL 16.15, Java 21, and Flyway 13.10.3 in Docker.

La auditoría registrada de D2 completó **147 comprobaciones sin fallos, errores ni omisiones** el 17 de octubre de 2026, con PostgreSQL 16.15, Java 21 y Flyway 13.10.3 en Docker.

## What the result means / Qué significa

- 78 historical checks characterize V4/V5 gaps and validate the first V6 corrections. Historical `OPEN` cases pass when an old gap is reproduced.
- 69 additional checks exercise the proposed persistence contracts: capacity accounting, concurrent claims/reservations, transitions, fencing, recovery decisions, dependency cycles, immutable snapshots, approvals, and provenance.
- External effects and checkpoints are simulated trusted receipts. No AI provider, Git operation, cloud API, or real worker was exercised.
- The validation kernel uses conservative global locking. Scalability and production deployment have not been validated. D2 still requires review and approval.

Las 78 comprobaciones históricas incluyen reproducciones de defectos anteriores; las 69 nuevas ejercitan los contratos propuestos. Los recibos externos son simulaciones. Este resultado no acredita un sistema completo, servicios externos reales ni preparación para producción.

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
- [Consolidated D2 review](../design/D2.8-consolidated-review.md).

This summary is a recorded result, not a CI status badge. Re-run validation after changing executable inputs or the transition document consumed by tests.

Este resumen es un resultado registrado, no un indicador de CI. Repite la validación si cambian fuentes ejecutables o la especificación de transiciones que consumen las pruebas.
