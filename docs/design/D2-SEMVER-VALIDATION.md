# D2 — validación de SemVer completada

Estado: D2-A05/A06 validados el 2026-10-17. La auditoría Docker completa pasó con **157 pruebas JUnit**, cero fallos, errores u omisiones. Una de esas pruebas contrasta **29.829 vectores** con una referencia independiente; los vectores no se suman al conteo JUnit.

## Contrato y referencia

Versiones almacenadas conforme a [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html), con prereleases y metadatos de build. Los metadatos no afectan a la precedencia. La identidad persistida del artefacto y su evidencia siguen siendo exactas.

Rangos conforme a [npm/node-semver 7.7.2](https://github.com/npm/node-semver/tree/v7.7.2#ranges): comparadores, intersecciones, uniones, guiones, parciales, comodines, caret y tilde. Las prereleases requieren admisión expresa por las reglas del rango. No se habilitan `loose`, `coerce` ni `includePrerelease` global.

La referencia queda fijada en el commit `281055e7716ef0415a8826972471331989ede58c`. Se utiliza para generar resultados esperados; PostgreSQL ejecuta el código bajo prueba. Node no es una dependencia del prototipo en ejecución. La adaptación del algoritmo conserva el aviso ISC en [THIRD-PARTY-NOTICES.md](../../THIRD-PARTY-NOTICES.md).

## Corrección y diagnóstico

[V11 propuesta](../../migrations-proposed/V11__semver_contract_draft.sql) sustituye `d2.compatible` sin cambiar las migraciones V1–V10. CLAIM, elegibilidad HARD, integración MOCKABLE y VERIFY conservan las llamadas compartidas al mismo contrato. No se añade un segundo intérprete en otra capa.

`d2.compatibility_result` distingue `MATCH`, `NO_MATCH`, `INVALID_VERSION`, `INVALID_RANGE` y `LIMIT_EXCEEDED`. Solo MATCH permite compatibilidad. Un brazo OR inválido invalida el rango completo. Los helpers quedan revocados a PUBLIC; los entrypoints de ejecución conservan sus permisos restringidos.

Los límites operativos son explícitos:

| Entrada | Límite y comportamiento |
|---|---|
| Versión | 256 bytes; mayor tamaño produce LIMIT_EXCEEDED |
| Núcleo numérico | Componentes entre 0 y 9007199254740991, alineados con la referencia npm; fuera de ese dominio la versión produce INVALID_VERSION |
| Rango | 4096 bytes, hasta 32 brazos OR y 128 tokens por brazo; exceso produce LIMIT_EXCEEDED |
| Límites expandidos | Si la expansión requiere un núcleo fuera del dominio numérico, produce LIMIT_EXCEEDED |
| Identificadores prerelease numéricos | Comparación exacta por longitud y dígitos, sin redondeo de coma flotante, dentro del límite de versión |

Las versiones almacenadas son canónicas: se rechazan prefijos `v`/`=` y espacios alrededor de la versión. Los prefijos y espacios permitidos por la gramática npm sí se aceptan en rangos. No se afirma soporte ilimitado de enteros o tamaños de entrada.

## Evidencia ejecutada

- Corpus: 231 rangos por 129 versiones, más entradas inválidas; 29.829 resultados esperados contrastados, sin discrepancias. Incluye 175 filas oficiales aplicables de include/exclude y casos de análisis de rangos. Se excluyen 42 filas con otros modos, versiones almacenadas no canónicas o rangos inválidos; los errores de sintaxis se prueban por separado. [Metadatos](../../testing/D2/src/test/resources/semver/metadata.json).
- Orden: comparaciones por pares de la secuencia normativa de prereleases, builds con igual precedencia y números prerelease grandes sin redondeo.
- Integración: HARD bloquea CLAIM y VERIFY cuando corresponde; MOCKABLE puede desarrollar pero no completar una integración incompatible; una prerelease requiere rango explícito.
- Evidencia: builds de igual precedencia no comparten pruebas de versión, entorno, hash o generación. Las regresiones existentes de invalidación y concurrencia pasan.
- Upgrade: Flyway migra V10→V11, valida y no repite migraciones aplicadas. Las entradas previas inválidas se preservan y aparecen en el inventario `d2.semver_preflight`; no se normalizan ni sobrescriben a ciegas.
- Regresión completa: todas las clases históricas y de contratos pasan en PostgreSQL 16.15, Java 21 y Flyway 13.10.3.

La primera ejecución detectó el rango vacío y una expectativa antigua sobre `*`; ambos quedaron corregidos. Otra ejecución detectó un Context Pack ausente en los datos sintéticos del upgrade; se completó la fixture respetando la guarda existente. El informe vigente corresponde a la ejecución posterior satisfactoria.

## Reproducción y despliegue posterior

```bash
bash testing/D2/run-docker-audit.sh
```

Los fixtures están versionados; reproducir la auditoría no necesita descargar npm. Para regenerarlos, clonar el tag 7.7.2 en el directorio local ignorado indicado y ejecutar:

```bash
node testing/D2/generate-semver-fixtures.cjs work/semver-reference
```

El generador comprueba el commit de referencia. La [evidencia portable](../validation/semver-evidence.json) conserva hashes de entradas y conteos; los logs y XML originales permanecen locales.

Antes de promover V11 a una instalación con datos reales, el propietario/migrador deberá revisar `SELECT * FROM d2.semver_preflight WHERE status <> 'VALID'` y las resoluciones incompatibles. El upgrade sintético no sustituye esa revisión real. El cierre de diseño no aprueba despliegue ni inicia la aplicación completa; véanse el [registro de decisiones](D2-DECISIONS.md) y [D2 aprobado](D2.9-approved.md).
