# Documentation / Documentación

[Project introduction](../README.md) · [Presentación en español](../README.es.md)

## Current design / Diseño vigente

| Document | Purpose / Propósito |
|---|---|
| [D1 architecture baseline](design/D1-architecture-baseline.md) | Approved functional architecture / Arquitectura funcional aprobada |
| [D2 decision register](design/D2-DECISIONS.md) | Approved decisions and pending choices / Decisiones aprobadas y pendientes |
| [D2 consolidated review](design/D2.8-consolidated-review.md) | Current domain/PostgreSQL draft, in Spanish / Borrador vigente, pendiente de revisión |
| [Validation overview](validation/README.md) | How to interpret and reproduce the checks / Alcance y reproducción |
| [D2 validation matrix](validation/D2-VALIDATION-MATRIX.md) | Requirements, evidence, and limitations / Requisitos, evidencia y límites |
| [Portable results](validation/latest-results.json) | Recorded environment and counts, without machine-specific data / Resumen sin datos del equipo |

D1 is approved. D2 remains a draft. Older documents contain statements that were accurate when written; use the consolidated review and validation overview for the current status. Migration paths in the design documents are relative to the repository root.

D1 está aprobado y D2 sigue en borrador. Los documentos históricos reflejan su momento de redacción; consulta la consolidación y la validación para el estado vigente. Las rutas de migraciones indicadas en los documentos parten de la raíz del repositorio.

## Design history / Historial

- [Original domain model](design/history/D2-domain-model-draft.md).
- [D2.3 — state, capacity, recovery](design/history/D2.3-state-capacity-recovery.md).
- [D2.4 — transitions and test plan](design/history/D2.4-transitions-integrity-tests.md).
- [D2.5 — integrity proposal](design/history/D2.5-integrity-proposal.md).
- [D2.6 — physical capacity and transactions](design/history/D2.6-capacity-transaction-contract.md).
- [D2.7 — relational corrections](design/history/D2.7-relational-corrections.md).
- [Archived SQL mirrors](archive/sql-markdown/README.md).

The original D1, D2 v0.4 documents, V1–V4 SQL, and SQL mirrors retain their content after relocation. Original import manifests, handoffs, and raw evidence remain local in ignored directories. The test harness reads the relocated D2.4 transition specification directly.

El contenido de D1, los documentos originales de D2 v0.4, SQL V1–V4 y sus mirrors se conserva tras la reorganización. Los manifiestos de importación, handoffs y evidencia bruta permanecen locales, fuera de Git. Las pruebas leen directamente la especificación D2.4 reubicada.
