# Security / Seguridad

## Reporting a concern

Do not include credentials, private source documents, database dumps, or sensitive reproduction details in public issues or pull requests. Arrange a private reporting channel with the maintainer before sharing those details. No dedicated security email or response-time commitment is configured for this prototype.

If a credential has been exposed, revoke or rotate it with its provider. Deleting a file or adding an ignore rule does not invalidate a credential or remove it from Git history.

## Publication boundaries

- `.gitignore` excludes local agent/cloud state, secrets, attachments, raw audit evidence, PostgreSQL data, logs, caches, and build outputs.
- `scripts/check-publication.py` checks tracked and unignored files for a limited set of sensitive patterns. It prints locations and finding categories, never matched credential values.
- Keep examples synthetic and use environment-based configuration for future integrations. Allowed `.example` files must contain placeholders only.
- Review staged changes before pushing. Ignore rules do not apply retroactively to tracked files; the local check also examines those files.
- The database audit uses temporary containers and synthetic data. It is not a production deployment procedure.

The project has no released production application or supported release series yet. Database migration-owner privileges are for isolated validation; the future application must use restricted roles. See the [D2 review draft](docs/design/D2.8-consolidated-review.md) for the proposed trust boundaries.

## Comunicación de problemas

No publiques credenciales, documentos privados, dumps ni detalles sensibles en issues o pull requests. Acuerda primero un canal privado con el mantenedor. Este prototipo todavía no dispone de correo de seguridad dedicado ni compromiso de tiempo de respuesta.

Si se expone una credencial, revócala o rótala con su proveedor. Borrar un archivo o añadirlo a `.gitignore` no invalida la credencial ni la elimina del historial de Git.

Los archivos de ejemplo deben usar datos ficticios. Revisa el diff antes del push y ejecuta la comprobación local; sus patrones son limitados y no sustituyen una revisión de secretos. La auditoría PostgreSQL utiliza bases temporales y fixtures sintéticas, no un procedimiento de despliegue de producción.
