# Validación reproducible de D2

Este módulo contiene prototipos SQL y pruebas de persistencia, integridad, concurrencia y recuperación. No es la aplicación completa. D1 permanece aprobado y D2 cerrado y aprobado como diseño. Consultar el [índice público](../../docs/README.md) y la [matriz D2](../../docs/validation/D2-VALIDATION-MATRIX.md).

## Docker

Desde la raíz:

```bash
bash testing/D2/run-docker-audit.sh
```

Requiere acceso al daemon Docker, al registro de imágenes y a Maven Central. El proyecto debe ser visible al daemon para el bind mount. El usuario que ejecute la batería debe tener acceso al daemon.

Se levantan PostgreSQL 16 y Maven/Java 21 en una red exclusiva sin puertos publicados. La base usa almacenamiento temporal y trust exclusivamente para fixtures. El runner elimina únicamente sus dos contenedores y su red al terminar. AUDIT_PG_IMAGE/AUDIT_MAVEN_IMAGE permiten fijar digests o probar otras versiones.

Se crean seis bases: baseline V4, proposed V5, hardened V6, upgrade V5 para pruebas transaccionales de V6, contract V1–V11, y semver_upgrade para la actualización V10→V11. El target histórico queda fijado para no cambiar los casos OPEN cuando aparecen propuestas nuevas.

La última ejecución terminó con PostgreSQL 16.15 y **157 comprobaciones, sin fallos, errores ni omisiones**. Logs, versiones, hashes y reportes están en el directorio anunciado dentro de work/docker-audit/. Maven escribe los reportes directamente en su carpeta evidence/, también en ejecuciones fallidas, sin copiar resultados viejos desde target/.

Los 78 casos históricos y 79 de contratos no equivalen a 157 garantías de producción. Algunos caracterizan huecos V4/V5; los nuevos validan el contrato propuesto y usan adaptadores simulados. No se ejecuta Spring Boot ni Testcontainers. [DOCKER-EXECUTION.md](DOCKER-EXECUTION.md) documenta alcance y evidencia.

## Ejecución local alternativa

```bash
PG_BIN=/ruta/postgresql/bin MAVEN_BIN=/ruta/mvn bash testing/D2/run-audit.sh
```

Requiere Java 21, Maven, PostgreSQL 16+ con servidor, pgcrypto y btree_gist, y psql. El script crea un cluster nuevo bajo work/d2-runtime, escucha solo en localhost y lo detiene al terminar. AUDIT_PORT cambia el puerto 55439 y AUDIT_M2 fija caché Maven. Nunca apuntar el harness a bases existentes: inserta fixtures y algunas pruebas conservan datos para concurrencia. No usa Flyway clean.

La ejecución local histórica de 53 comprobaciones utilizó PostgreSQL 18.6; sus logs/reportes originales se conservan en testing/D2/evidence/ y work/d2-runtime/. Las ampliaciones actuales se han ejecutado con Docker, no se atribuyen a aquella ejecución local.

## SemVer

La batería incluye 29.829 vectores con resultados esperados generados por npm/node-semver 7.7.2, dentro de una prueba JUnit, más pruebas de límites, orden, CLAIM/VERIFY, evidencia y upgrade V10→V11. Los fixtures están versionados; Node no es necesario para ejecutar la batería. Véase el [informe SemVer](../../docs/design/D2-SEMVER-VALIDATION.md) para regeneración, límites e inventario previo a despliegue.
