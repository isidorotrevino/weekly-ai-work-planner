# Contributing / Cómo contribuir

## English

This repository is currently a design and database-validation project. Start with the [documentation index](docs/README.md), the approved D1 baseline, and the consolidated D2 draft.

- Discuss architectural changes in an issue before expanding scope. D1 changes need a recorded decision and maintainer approval; D2 remains a draft until explicitly approved.
- Keep historical V1–V4 migrations unchanged. Put new SQL proposals in `migrations-proposed/` and describe compatibility and backfill behavior.
- Add meaningful validation for changes to persistence contracts. Run `bash testing/D2/run-docker-audit.sh` when changing SQL, the harness, or documentation consumed by tests.
- Explain the problem, resulting behavior, validation performed, and relevant limitations in your pull request.
- Keep synthetic fixtures separate from real project data. Never include credentials, raw database clusters, private attachments, session transcripts, or unreviewed logs.
- Run `python3 scripts/check-publication.py` and inspect the staged diff. Keep documentation links and English/Spanish introductions consistent.

For a security concern, follow [SECURITY.md](SECURITY.md) rather than posting sensitive details publicly. Contributions intended for inclusion must be available under **GPL-3.0-only**, the project license. Contributors retain their copyright; submitting a contribution does not assign ownership to the maintainer. Preserve third-party notices and identify dependencies or copied material for license-compatibility review. See [LICENSE](LICENSE) and [LICENSING.md](LICENSING.md).

## Español

Este repositorio está en fase de diseño y validación de base de datos. Empieza por el [índice](docs/README.md), D1 aprobado y el borrador consolidado de D2.

- Comenta cambios de arquitectura en un issue antes de ampliar el alcance. Modificar D1 requiere una decisión registrada y aprobación del mantenedor; D2 sigue en borrador hasta su aprobación expresa.
- Conserva V1–V4 sin cambios. Añade SQL propuesto en `migrations-proposed/` y explica compatibilidad y backfill.
- Verifica los cambios de contratos con pruebas significativas. Ejecuta `bash testing/D2/run-docker-audit.sh` si modificas SQL, la batería o documentación que consumen las pruebas.
- Describe en el pull request el problema, el comportamiento resultante, las comprobaciones y sus límites.
- Usa fixtures sintéticas. No incluyas credenciales, clusters reales, adjuntos privados, conversaciones ni logs sin revisar.
- Ejecuta `python3 scripts/check-publication.py`, revisa el diff preparado y mantén coherentes los enlaces y las introducciones bilingües.

Para problemas de seguridad, sigue [SECURITY.md](SECURITY.md). Las contribuciones destinadas a incorporarse deben estar disponibles bajo **GPL-3.0-only**, la licencia del proyecto. Cada contribuidor conserva sus derechos de autor; contribuir no transfiere su titularidad al mantenedor. Conserva avisos de terceros e identifica dependencias o material copiado para revisar compatibilidad. Consulta [LICENSE](LICENSE) y [LICENSING.md](LICENSING.md).
