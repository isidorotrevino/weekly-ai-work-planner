# D5 I37 — contrato de auditoría de evidencia y aplicabilidad

Fecha: **2026-10-23**, Europe/Madrid. **PREPARED_FOR_REVIEW**.
Base: `af31fd7f4d70c23ad84ac5b8258c05aba029a58a`.
[Alcance y decisión A](D5-I37-NEXT-CUT-SCOPE.md) ·
[Matriz EA01–EA36](D5-I37-EVIDENCE-AUDIT-REVIEW.md) ·
[Criterios GI](D5-I23-GLOBAL-INTEGRATION-REVIEW.md).

English: proposed read-only local evidence auditor. Historical byte integrity,
current applicability, declared coverage and human sufficiency are separate.
No tests rerun, global acceptance, provider/API attestation or publication authority.

## Autoridad, problema y resultado propuesto

El usuario seleccionó A: preparar auditoría ejecutable de inventario/aplicabilidad
GI33/GI34. Este documento propone su contrato y su implementación futura; no la
autoriza. D1–D4 cerrados y A52/D5-LOCAL-SYNTHETIC-I1-I20 aceptado conservan alcance.
P0 mantiene I32, handoff y posteriores sin publicar. D5 global, G01–G07 y GI33/
GI34/GI38/GI39/GI40 siguen abiertos para revisión global. GI40 solo recibe
comprobaciones de no mutación de esta futura auditoría.

Hoy los runners I34/I36 registran hashes y tests, pero comparar solo archivos
enumerados no detecta una incorporación al namespace descubierto. Un informe
registrado también contiene campos documentales añadidos después de la salida
bruta. Un hash coincidente no acredita que los tests se ejecutaron, que el target
SQL era otro o que una API real cumple la capacidad declarada. La herramienta
propuesta hará explícitas esas diferencias sin reescribir informes históricos.

## Alcance de lectura fijo y referencias de confianza

Se propone `scripts/audit-d5-evidence.py`, biblioteca estándar Python, y pruebas
en `testing/evidence_audit/`, fuera del discovery `testing/D5`. Invocación desde
raíz: `python3 scripts/audit-d5-evidence.py`. Sin argumentos de raíz, URL, paths,
shell, perfiles de proveedor o reparación. Salida JSON saneada en stdout;
diagnóstico mínimo en stderr. No escribe informes, inventarios o caches.

Un registro versionado nuevo `docs/validation/D5-EVIDENCE-REGISTRY.json` fijará
referencias revisables, nunca generadas automáticamente desde el informe auditado:

| Entrada | Commit que conserva los bytes | Clasificación |
|---|---|---|
| I34, `docs/validation/D5-I34-results.json` | `6a9932acec47f422249c94bc55bf83dc9a38b80b` | Campaña T histórica; 281 tests declarados |
| I36, `docs/validation/D5-I36-results.json` | `af31fd7f4d70c23ad84ac5b8258c05aba029a58a` | Campaña R con regresiones; 321 tests declarados |
| I33, contratos integrado/durable y matrices | `41582827c3a91425bd143021435cadfa7ebbf5a1` | Obligaciones UI01–UI40/DF01–DF48, sin ejecución propia |
| I35, contrato y matriz DR | `aee8b212ab766cc89483013045ebb3bad8ebf168` | Obligaciones DR01–DR40, sin ejecución propia |
| D3/D4, cierres y sus referencias | Base I36 | Preservación histórica; sin reejecución |
| A52, aceptación local y sus referencias | Base I36 | Hito I1–I20 aceptado; targets históricos distintos |

El registro contendrá path, commit completo, SHA-256 del documento, schema, tipo,
campos de hashes admitidos, target declarado, IDs esperados y dependencias explícitas.
Los valores se obtendrán y revisarán desde esos commits al implementar. No se
añade ahora un registro operativo ni una atestación de confianza criptográfica.
Modificar registro/herramienta requiere diff/revisión; controlar ambos puede
falsificar la auditoría. No firma, host attestation ni defensa contra caller hostil.

Lecturas históricas mediante `git cat-file`/`git show` locales con argumentos
separados, OIDs completos y paths del registro, sin shell, fetch, checkout o hooks.
Validar commits y blobs regulares; un objeto ausente produce UNAVAILABLE, nunca
fallback a HEAD/parent/red. Un checkout sin historia suficiente puede auditar lo
disponible, pero no declarar íntegra la historia ausente.

D3: `verified_executable_input_sha256`, evidencia y documento canónico declarado.
D4: esos campos más `preserved_migrations_and_prior_reports_sha256`, hash canónico
y referencia de cierre D3. A52: `inputs`, canónico, `recorded_runtime_evidence` y
targets/grupos declarados. Cada adapter valida su schema real, sin buscar cualquier
clave que parezca hash. D1/D2 conservan su documentación/targets y referencias
transitivas existentes en estos documentos; no inventar D1-CLOSURE/D2-CLOSURE.
Referencia/target no declarado = NOT_RECORDED. El informe enumera el límite exacto
de preservación verificado; no proclama inventario exhaustivo de D1–D4.

## Estados independientes y agregación

Cada entrada devuelve dimensiones y hallazgos con código estable y path público:

| Dimensión | Estados | Significado |
|---|---|---|
| `historical_integrity` | MATCH / MISMATCH / UNAVAILABLE / INVALID | Bytes del commit y hashes referenciados; sin inferir ejecución |
| `recorded_files_now` | MATCH / CHANGED / MISSING / INVALID | Archivos actuales enumerados, ejecutables y documentales separados |
| `discovery_now` | SAME / ADDED / REMOVED / INVALID / NOT_RECORDED | Conjunto de inputs seleccionables frente a conjunto histórico |
| `runtime_context` | MATCH_DECLARED / DIFFERENT / NOT_RECORDED | Python/plataforma actuales frente a declaraciones; sin equivalencia automática |
| `declarations` | CONSISTENT / INCONSISTENT / NOT_RECORDED | Schema, cuentas, grupos, mapas y exclusiones |
| `raw_binding` | MATCH / MISMATCH / NOT_RECORDED / UNAVAILABLE | Salida bruta anclada independientemente y comparación permitida |
| `sufficiency` | REVIEW_PENDING | Ningún cómputo convierte cobertura declarada en aceptación |

`applicability` será CURRENT_RECORDED_SCOPE solo si integridad histórica, bytes
ejecutables/config/contratos, conjunto descubierto y contexto declarado coinciden
y las declaraciones son consistentes. Se mantendrá el sufijo RECORDED_SCOPE y el
estado raw_binding: no equivale a nueva ejecución o prueba independiente de ella.
Cambio de un input pertinente o contexto = STALE; información necesaria ausente =
UNDETERMINED; contradicción o formato inseguro = INVALID. Precedencia INVALID,
STALE, UNDETERMINED, CURRENT_RECORDED_SCOPE. Cambio exclusivamente documental se
reporta por separado, sin invalidar automáticamente el runtime ni ocultarlo.

`audit_status` describe comprobaciones, nunca PASS funcional: CONSISTENT,
FINDINGS o INVALID. Exit 0 = sin contradicciones/cambios detectados en alcance
registrado; 1 = hallazgos, STALE/UNDETERMINED o evidencia ausente; 2 = entrada
inválida/error de lectura/verificación. NOT_RECORDED de salida bruta es una
limitación esperada explícita de los informes legados y no cambia solo el exit,
si no se exige como condición de una afirmación. Incluir contadores por dimensión
para que exit 0 no oculte esa ausencia. No emitir `D5_closed=true`, aceptación
global o permiso de publicar/activar, incluso ante un informe que lo solicite.

## Inventario, contexto y vigencia

Reconstruir en cada commit el conjunto exacto de reglas del runner: `.py` directos
de `source_ingest` y `testing/D5`, `.md` directos de `testing/D5/fixtures` y contratos
`docs/design/D5-I33-*.md` para I34 o `D5-I35-*.md` para I36. Comparar conjunto y
hash por separado; un archivo nuevo invalida igualdad aunque todos los anteriores
coincidan. Incluir no tracked que coincida con esas reglas. No importar módulos,
descubrir tests ejecutándolos ni leer otros directorios recursivamente.

La herramienta/registro/tests nuevos se inventarían por hashes en su propia
campaña de auditoría futura, sin insertarse retrospectivamente en I34/I36. Sus
paths concretos fuera del discovery no son una exclusión genérica para archivos
nuevos. Un cambio al runner o a sus reglas exige registro/adapter nuevo revisado;
no aprender un inventario nuevo para hacer que la campaña vieja aparezca vigente.

Versiones de schema/perfil/capacidades/config embebidas quedan ligadas a bytes del
código/contrato y a las declaraciones realmente presentes. No extraer ejecución
de un import. Config externa, API, CLI, proveedor, dependencia o versión sin
registro = NOT_RECORDED y fuera de cualquier afirmación de aplicabilidad completa.
Linux/Python declarados no identifican kernel/mount/energía ni garantizan fsync
real. Targets Python, SQL V30/propuestas, D1–D4 y dev no se equiparan por nombres.

## Declaraciones, mapas y contabilidad

Adaptadores explícitos I34/I36 validan `tests_run`, `passed`, `groups`,
`new_tests`, `regression_tests`, `failures/errors/skipped`, `case_test_map` y
mapas UI propios. IDs no vacíos, únicos en `passed`; grupos partición exacta,
cuentas enteras no booleanas y coherentes con grupos y resultado declarado.
Resultados no PASS se conservan como hechos, sin derivar tests exitosos ausentes.

DF01–DF48 y DR01–DR40 exigen fila exacta, lista no vacía de IDs realmente PASS;
UI01–UI40 se inventaría completa con obligación, mapa disponible por campaña,
modalidad y exclusión. I34 tiene mapas de base y expansión durable; I36 declara
solo UI25/UI34 como aportación R. Un ID repetido en varias filas es válido, pero
no incrementa tests distintos. UI sin mapa no recibe evidencia por proximidad;
Docs pendiente y GI reales no se convierten en PASS sintético. La asociación
UI→GI es declarada y revisable, nunca prueba automática de suficiencia.

I34 281 e I36 321 son campañas distintas; el informe muestra ambos y su intersección
de IDs, nunca 602 pruebas nuevas ni 48+40 como integración probada por aritmética.
Subcasos, procesos, SIGKILL, raíces y observaciones son métricas distintas. Validar
coherencia aritmética de limpieza/exitcodes cuando existen, sin probar por ello
que no quede un proceso externo. Ceros de actividad son declaraciones históricas,
no mediciones actuales de dev/proveedores. SQL/D1–D4 preservados por hash se muestran
como HISTORICAL_NOT_RERUN, conservando grupos/targets originales sin sumarlos a Python.

## Informe registrado frente a salida bruta

No hay salida bruta versionada y anclada independientemente para I34/I36 en este
alcance inicial. Deben resultar `raw_binding=NOT_RECORDED`. No buscarla en /tmp,
reconstruirla desde el JSON enriquecido o usar una reejecución como si fuera la
original. Para futuros paquetes, el registro fijará hash/identidad de salida
bruta y un adapter enumerará campos de runtime comunes, campos documentales
añadidos permitidos y normalizaciones exactas. Contradicción en un campo común
es MISMATCH; campo desconocido no se ignora. Orden de claves JSON no altera el
significado; listas PASS pueden compararse como conjuntos solo después de
rechazar duplicados. Las pruebas del comparador usan paquetes sintéticos propios,
sin crear retrospectivamente evidencia bruta histórica.

## Lecturas acotadas, salida y recursos

Paths relativos POSIX normalizados, sin absolutos, `..`, `.`, backslash, controles,
URLs o componentes privados. Lista cerrada de documentos/entradas de registro y
namespaces de discovery; rechazar duplicados JSON y floats no finitos. Nunca
resolver referencia documental arbitraria, enlaces Markdown, `.env`, dev/run_data,
.git como filesystem, D4 operativo, corpus privado o directorios externos.
Solo blobs públicos versionados D4/documentos/SQL y los inputs públicos enumerados
en cierres, con exclusiones privadas aplicadas antes de abrir contenido.

No seguir symlinks en ningún componente; rechazar FIFO/dispositivo/directorio en
lugar de archivo. Abrir archivos con comprobación de identidad/tamaño antes y
después, hash streaming; repetir conjuntos y comprobación de identidad final.
Cambio detectado durante lectura = UNSTABLE_SNAPSHOT y applicability UNDETERMINED,
sin reintento que mezcle snapshots. No prometer snapshot atómico ante escritor
hostil/ABA: auditoría exige checkout quieto y no confiere autoridad operacional.

Límites propuestos: 16 entradas de evidencia, 4096 paths únicos, 16 MiB por archivo,
128 MiB leídos por ejecución, 16384 IDs, 512 filas de mapa, 2 MiB de salida. JSON
profundidad máxima 32 y strings de metadatos 4096 caracteres. Validar límites antes
de asignaciones mayores; presupuestos reducidos de pruebas se etiquetan. Git:
máximo 256 invocaciones locales, 10 s por invocación, 60 s total; timeout sin éxito
parcial confirmado, terminar y esperar hijos propios. No procesos de laboratorio,
red, Docker/SQL/HTTP/SDK/CLI de proveedor, tests funcionales o comandos de limpieza.

Salida solo paths públicos, OIDs/hashes, códigos, versiones públicas y cuentas.
No imprimir bytes, texto fuente, claves desconocidas, valores inválidos, home,
path temporal, variables de entorno o stderr Git arbitrario. Errores saneados.
No side effects sobre archivos, Git/index/config, historiales o evidencia ajena.
Fixtures negativas en temporales propios; su harness limpia solo recursos creados
por él. No inspeccionar/parar/borrar dev/run_data/D4.

## Propuesta concreta para la siguiente autorización

Aprobar este contrato y EA01–EA36 autorizaría implementar únicamente script,
registro fijo, harness/pruebas de auditoría y documentación/resultados propios.
Conservar kernel durable, parsers, T/R, runners y reportes históricos intactos.
Ejecutar pruebas de auditoría con paquetes sintéticos y auditoría de lectura local;
no reejecutar las 321 pruebas ni SQL por este cambio aislado. Si hace falta cambiar
runtime/discovery/contrato, revisar alcance antes de hacerlo. P0 sigue vigente y
la publicación requiere después SHA concreto autorizado por separado.

Sin proveedores/credenciales reales, consumo/reservas, activación, promoción,
despliegue o D6. Aprobar solo diseño es una alternativa distinta de implementar.
