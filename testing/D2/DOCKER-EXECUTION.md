# Recorded Docker execution / Ejecución Docker registrada

The portable public record is maintained in [the validation overview](../../docs/validation/README.md) and [latest-results.json](../../docs/validation/latest-results.json).

**Recorded result, October 17, 2026:** PostgreSQL 16.15, Java 21, Flyway 13.10.3; 147 checks; zero failures, errors, or skipped checks. D2 remains a draft pending review.

Run from the repository root:

```bash
bash testing/D2/run-docker-audit.sh
```

The runner writes fresh reports directly to its own ignored `work/docker-audit/<run>/evidence/` directory. It records image digests, versions, Maven output, and cleanup results. Five databases compare the original schema, previous proposals, transactional upgrades, and the V1–V10 contract.

The kernel proposes an additional guarded reconciliation edge, bringing its transition matrix to 69 edges while the original matrix remains at 68. External effects and checkpoints use simulated receipts. The harness does not start Spring Boot, Testcontainers, workers, or external integrations. See the [validation matrix](../../docs/validation/D2-VALIDATION-MATRIX.md) for limits.

## Español

El resumen público portable está en los enlaces anteriores. La ejecución registrada completó 147 comprobaciones correctas. Para reproducirla, ejecuta el comando desde la raíz del repositorio. Los reportes brutos y metadatos quedan en una carpeta local excluida de Git; no se incluyen nombres de equipos ni rutas personales en este resumen.

La matriz del contrato propone 69 arcos, frente a los 68 originales. Los efectos externos y checkpoints son simulados. D2 permanece abierto; el resultado no autoriza su cierre ni un despliegue de producción.
