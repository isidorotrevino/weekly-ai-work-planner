# Propuestas de persistencia D3

V12 es aditiva sobre V1–V11; solo se ha aplicado a bases desechables de auditoría. No promueve V5–V11 ni autoriza despliegue. D1/D2 y las migraciones anteriores se conservan byte por byte.

Esta ubicación separada evita que la batería histórica D2 descubra V12 automáticamente: su caso de upgrade V10→V11 comprueba expresamente una única migración. Es una excepción documental al directorio general `migrations-proposed/`; no altera el stack ni el contrato aprobado. El nuevo harness D3 proporciona las tres ubicaciones explícitamente y prueba instalación limpia y upgrade V11→V12 con reservas existentes.

La migración crea el esquema d3, catálogo versionado de estimaciones/calendarios, épocas/observaciones/atribuciones de equidad, captures inmutables y publicación con CAS. No crea cuentas de LOGIN ni concede permisos runtime. Los permisos usados por la batería se aplican únicamente a un rol NOLOGIN de prueba; la separación de identidades real corresponde a D6.

Consulta [I2: persistencia y publicación](../docs/design/D3-I2-PERSISTENCE.md) para contratos, locks, pruebas y límites. La adopción de planes PUBLISHED legados sin head D3 se rechaza y necesita revisión explícita; no se inventa un plan vigente.
