# Contributing / Cómo contribuir

## English

This repository is currently a design and database-validation project. Start with the [documentation index](docs/README.md), the approved D1 baseline, and the approved D2 design.

- Discuss architectural changes in an issue before expanding scope. D1 changes need a recorded decision and maintainer approval; D2 is approved; changes to approved design decisions require maintainer approval.
- Keep historical V1–V4 migrations unchanged. Put new SQL proposals in `migrations-proposed/` and describe compatibility and backfill behavior.
- D3 additive SQL lives in `migrations-d3-proposed/` so the historical D2 V10→V11 audit keeps its target. Its dedicated harness explicitly adds that location; see [D3 I2](docs/design/D3-I2-PERSISTENCE.md).
- Add meaningful validation for changes to persistence contracts. Run `bash testing/D2/run-docker-audit.sh` when changing SQL, the harness, or documentation consumed by tests.
- Explain the problem, resulting behavior, validation performed, and relevant limitations in your pull request.
- Keep synthetic fixtures separate from real project data. Never include credentials, raw database clusters, private attachments, session transcripts, or unreviewed logs.
- Run `python3 scripts/check-publication.py` and inspect the staged diff. Keep documentation links and English/Spanish introductions consistent.

For a security concern, follow [SECURITY.md](SECURITY.md) rather than posting sensitive details publicly. Contributions intended for inclusion must be available under **GPL-3.0-only**, the project license. Contributors retain their copyright; submitting a contribution does not assign ownership to the maintainer. Preserve third-party notices and identify dependencies or copied material for license-compatibility review. See [LICENSE](LICENSE) and [LICENSING.md](LICENSING.md).

## Español

Este repositorio está en fase de diseño y validación de base de datos. Empieza por el [índice](docs/README.md), D1 aprobado y el diseño aprobado de D2.

- Comenta cambios de arquitectura en un issue antes de ampliar el alcance. Modificar D1 requiere una decisión registrada y aprobación del mantenedor; D2 está aprobado; cambiar decisiones aprobadas requiere aprobación del mantenedor.
- Conserva V1–V4 sin cambios. Añade SQL propuesto en `migrations-proposed/` y explica compatibilidad y backfill.
- El SQL aditivo D3 se aísla en `migrations-d3-proposed/` para conservar el target de la auditoría D2 V10→V11. Su harness propio añade esa ubicación explícitamente; consulta [D3 I2](docs/design/D3-I2-PERSISTENCE.md).
- Verifica los cambios de contratos con pruebas significativas. Ejecuta `bash testing/D2/run-docker-audit.sh` si modificas SQL, la batería o documentación que consumen las pruebas.
- Describe en el pull request el problema, el comportamiento resultante, las comprobaciones y sus límites.
- Usa fixtures sintéticas. No incluyas credenciales, clusters reales, adjuntos privados, conversaciones ni logs sin revisar.
- Ejecuta `python3 scripts/check-publication.py`, revisa el diff preparado y mantén coherentes los enlaces y las introducciones bilingües.

Para problemas de seguridad, sigue [SECURITY.md](SECURITY.md). Las contribuciones destinadas a incorporarse deben estar disponibles bajo **GPL-3.0-only**, la licencia del proyecto. Cada contribuidor conserva sus derechos de autor; contribuir no transfiere su titularidad al mantenedor. Conserva avisos de terceros e identifica dependencias o material copiado para revisar compatibilidad. Consulta [LICENSE](LICENSE) y [LICENSING.md](LICENSING.md).

D3 I3 keeps V13 separately in `migrations-d3-dispatch-proposed/`. The I3 harness supplies that fourth location explicitly; I2 still targets V12 and the unchanged D2 harness V11. See [I3](docs/design/D3-I3-DISPATCH.md).

The D3 coordinator adds V14 in `migrations-d3-coordinator-proposed/` as a fifth explicit test location. Earlier audit templates remain V11/V12/V13; the callable coordinator is tested separately on V14.

The integrated D3 review adds V15 in `migrations-d3-review-proposed/` as a sixth explicit location. It corrects critical incident reopening and appends a correction fact for affected open inbox requests; it preserves V1–V14. Historical templates stay unchanged, with V15 acceptance in its own template.
