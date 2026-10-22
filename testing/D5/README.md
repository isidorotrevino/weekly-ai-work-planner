# D5 I1 — local preview / previsualización local

[Contrato y límites](../../docs/design/D5-LOCAL-PREVIEW.md) ·
[Resultados](../../docs/validation/D5-I1-results.md).
D5 abierto. Utilidad Linux/Python 3 de biblioteca estándar; no requiere Docker,
JDK, Maven, SQL, conectores ni credenciales. Ejecutar desde la raíz del repositorio.

```bash
python3 -m unittest discover -s testing/D5 -v
python3 -m source_ingest \
  --root testing/D5/fixtures --file plan.md \
  --project-id 00000000-0000-4000-8000-000000000001 \
  --document-id 00000000-0000-4000-8000-000000000002 \
  --revision fixture-v1
```

Los UUID del ejemplo son identidades sintéticas del llamante, sin vínculo a una
base existente. Para otra fuente, elegir una raíz explícita y una ruta relativa;
conservar los mismos UUID al observar otra revisión del mismo documento/proyecto.
`--revision` es una etiqueta de observación, no una atestación de Git ni del autor.
No ejecutar scripts ni seguir enlaces contenidos en el documento.

El comando imprime un resumen sin texto de la fuente: estado PREVIEW_ONLY, hashes,
conteos, diagnósticos y ruta al artefacto privado. Ese JSON **sí contiene todos los
bytes de la fuente**, codificados en base64, además de los candidatos y sus líneas.
No compartirlo ni copiarlo a Git. El destino predeterminado es
`work/d5/previews/HASH.json`, ignorado. `--store` permite otro directorio privado
seleccionado explícitamente por el operador; `.gitignore` solo protege las rutas
configuradas y no es un control de acceso.

Repetir exactamente el comando devuelve el mismo artefacto tras comprobar sus bytes.
Editar la fuente o cambiar etiqueta, identidad o perfil conserva otra observación.
No se mantiene un head ni se decide cuál es la revisión vigente. Un archivo
inexistente/inestable, traversal, symlink, hardlink, FIFO, UTF-8 inválido, NUL o
límite excedido da salida no cero sin generar un resultado parcial. Un artefacto
existente alterado se rechaza sin sobrescribirlo; conservarlo para diagnóstico y
revisarlo manualmente. Un temporal interrumpido puede quedar como `.preview-*`;
no es un resultado válido y no se promociona automáticamente.

El perfil extrae encabezados y checklists de una línea, no un AST Markdown completo.
Conserva los marcadores de origen sin deducir estados de workflow. Las tablas
producen un diagnóstico y ningún candidato derivado de sus celdas. Los resultados
son parciales y nunca habilitan ejecución. Las fuentes reales revisadas por el
usuario y sus snapshots se guardan solo localmente; `fixtures/plan.md` es sintético.

Estas pruebas son independientes de `testing/D2`, `testing/D3`, `testing/D4` y del
entorno `compose.dev.yaml`; no cambian targets, bootstrap ni evidencias anteriores.

## I2 — perfil tabular y comparación

[Contrato I2](../../docs/design/D5-REGISTER-COMPARISON.md) ·
[Resultados I2](../../docs/validation/D5-I2-results.md).
El perfil por defecto conserva el comportamiento I1. Para optar por las ocho
columnas del registro:

```bash
python3 -m source_ingest \
  --root testing/D5/fixtures --file register-before.md \
  --project-id 00000000-0000-4000-8000-000000000001 \
  --document-id 00000000-0000-4000-8000-000000000002 \
  --revision fixture-v1 --profile task-register.v1
```

Una demo sintética repetible crea las dos capturas y su comparación, e imprime
sus rutas privadas:

```bash
python3 -m testing.D5.demo_register
```

El resultado tiene un elemento añadido, uno cambiado, uno sin cambio desplazado
y una ausencia. Ninguno activa o elimina trabajo. Para usar el CLI comparador con
otras capturas, pasar las rutas JSON impresas por la ingesta:

```bash
python3 -m source_ingest.compare --before "$BEFORE_PREVIEW" --after "$AFTER_PREVIEW"
```

`BEFORE_PREVIEW` y `AFTER_PREVIEW` deben contener las rutas explícitas a las dos
capturas del mismo proyecto/documento/perfil. La herramienta no selecciona una
revisión vigente. Primero comprueba sus hashes y reconstruye el contenido. Las
etiquetas del llamante no prueban commits ni orden remoto.

El resumen de ingesta incluye `comparison_eligible`; un perfil tabular con errores
puede capturarse para diagnóstico, pero no comparar cambios. La comparación guarda
un informe privado en `work/d5/comparisons/` y devuelve 0 para PREVIEW_ONLY, 2 para
BLOCKED (sin cambios parciales) y 1 para entradas inválidas/incompatibles. El retorno
0 nunca es permiso de importar o ejecutar. Los artefactos están limitados a 32 MiB.

El perfil conserva filas tachadas y estados de origen sin deducir DONE. Un ID
duplicado o una fila ambigua bloquea toda la comparación. Una tabla fragmentada
por líneas vacías no se recompone automáticamente; tampoco se recuperan filas
fuera de cabeceras reconocidas. Las variaciones del registro real se mantienen
bloqueadas hasta una decisión explícita sobre formato o normalización.

## I3 — compatibilidad optativa y anotaciones

[Decisiones y contrato I3](../../docs/design/D5-REGISTER-COMPATIBILITY.md) ·
[Resultados I3](../../docs/validation/D5-I3-results.md).
Conserva los perfiles I1/I2. Para probar blancos entre filas bajo una cabecera y
anotaciones separadas después de las ocho celdas:

```bash
python3 -m testing.D5.demo_register --profile task-register-compat.v1
python3 -m source_ingest \
  --root testing/D5/fixtures --file register-compat-before.md \
  --project-id 00000000-0000-4000-8000-000000000001 \
  --document-id 00000000-0000-4000-8000-000000000002 \
  --revision fixture-v1 --profile task-register-compat.v1
```

La demo conserva dos filas y detecta una anotación cambiada y una fila sin cambio
que se desplazó. Usa el comparador I2 con las rutas impresas para repetir la
comparación. Los dos extremos deben tener el mismo perfil; estricto y compatible
no se mezclan automáticamente. El sufijo se guarda como `source_annotation`, con
texto y posiciones Unicode de origen; no se incorpora a Status/Verified/Source ni
se interpreta como permiso o evidencia.

Solo se toleran blancos dentro de una tabla ya reconocida. Narrativa, encabezados
y fences terminan su continuidad; duplicados, columnas ambiguas u otras guardas
siguen bloqueando el informe completo. Un pipe adicional sin escapar en una
anotación también bloquea. El original nunca se modifica. La captura compatible
del registro real puede compararse estructuralmente, pero sus afirmaciones de
estado o verificación continúan siendo datos no acreditados.

## I4 — laboratorio PostgreSQL desechable

[Contrato aprobado e implementación](../../docs/design/D5-I4-PERSISTENCE-LAB.md)
· [Resultados propios](../../docs/validation/D5-I4-results.md).
Este laboratorio es opcional e independiente de las 47 pruebas locales de parser,
comparación y adaptador. Requiere Linux, Python 3 y Docker Engine accesible por el
usuario. No requiere psql en el host, JDK o Maven para D5.

Desde la raíz del repositorio:

```bash
# Preparar esta dependencia solo si falta; el runner no descarga imágenes.
docker pull postgres:16-bookworm
python3 -m testing.D5.run_postgres_lab
```

El runner arranca un contenedor único sin red, sin puertos y con socket SQL solo
interno. Crea la base y roles sintéticos, aplica V1–V11 y la propuesta D5 V31,
ejecuta P01–P10 y elimina su contenedor y volumen anónimo, también si fallan las
pruebas. Durante la campaña reinicia esa base para comprobar recuperación. No usa
Compose, `run_data`, el bootstrap D4 ni proyectos o datos existentes. No ejecuta
V12–V30 ni promociona V31. El retorno 0 indica que las pruebas pasaron; un fallo
devuelve no cero y conserva diagnóstico privado bajo `work/d5/postgres/d5-pg-*/`.
La limpieza no borra esos diagnósticos ni ejecuta podas globales de Docker.

El flujo comprobado registra una fuente, ingiere una previsualización sintética,
lee la referencia vacía, selecciona con versión esperada y recupera el recibo.
Las pruebas incluyen comandos concurrentes, conflictos, replay, bytes exactos,
aborto antes del commit, respuesta descartada y recuperación tras reinicio.

El adaptador ofrece `python3 -m source_ingest.postgres --help` con comandos
`register`, `ingest`, `select`, `reference` y `receipt`. Solo acepta un contenedor
D5 etiquetado y aislado, nunca una URL SQL arbitraria ni credenciales. Estos
comandos se ejercitan dentro de la campaña; al terminar ya no existe su base.
No son instrucciones para apuntar a desarrollo o producción. Las lecturas de
bytes están disponibles en la API Python `LabClient.recover`; el CLI solo imprime
metadatos/recibos, sin contenido fuente. Un conflicto confirmado devuelve código 2;
un fallo de verificación o SQL, código 1. Consultar un recibo inexistente devuelve
`null`, sin inferir éxito.

Ingerir no mueve ninguna referencia. Seleccionar no activa trabajo y una captura
BLOCKED conserva su bloqueo. El recibo identifica el resultado histórico; la
referencia actual requiere otra lectura. Los artefactos originales I1–I3 y las
etiquetas del llamante conservan sus límites de autoridad.

## I5 — comparación persistida, revisión y simulación

[Decisiones A10–A12 y contrato](../../docs/design/D5-I5-REVIEW-SIMULATION.md)
· [Evidencia I5](../../docs/validation/D5-I5-results.md).
Con los mismos requisitos Docker/Python del laboratorio I4:

```bash
python3 -m testing.D5.run_review_lab
```

Este runner propio aplica V1–V11, V31 y V32 solo en su contenedor desechable sin red
ni puertos. Ejecuta la regresión I4 y el flujo nuevo, comprueba la recuperación y
elimina su contenedor/volumen. Conserva diagnóstico privado en
`work/d5/postgres/d5-pg-*/review-results.json`. No modifica el runner I4 ni el entorno
de desarrollo. El retorno no cero indica fallo de la campaña, sin promoción.

El caso R15 prueba el CLI `python3 -m source_ingest.review --help` dentro del
laboratorio, con este flujo completo:

1. `compare`: dos IDs explícitos de observación SQL; guarda informe y hashes.
2. `export`: recupera, reconstruye y exporta el informe a un archivo privado
   direccionado por hash; destino por defecto `work/d5/reviews/`.
3. `row`: muestra el cambio completo de una fila y su revisión actual. Este comando
   **imprime contenido de origen** por solicitud expresa; no compartirlo como log.
4. `decide`: ACCEPT/REJECT con ID/hash de comparación, ID/hash de fila, versión
   esperada, etiqueta del revisor y motivo; conserva decisión y recibo.
5. `simulate`: filas elegidas mediante `--item ID:HASH:DECISION_UUID:VERSION`,
   repetible, y `--expected-reference-version`. El CLI ordena los pins por ID.

Los subcomandos exigen proyecto/documento y contenedor D5 etiquetado sin red.
`compare`, `decide` y `simulate` exigen command_id explícito. Usar `--help` en cada
subcomando para ver todos sus parámetros. La referencia debe seleccionarse antes
con el `select` I4, apuntando al ID «antes»; no se mueve al comparar, aceptar o
simular. Al terminar la campaña su base deja de existir; estos comandos no se
ofrecen como conexión a dev/producción ni como un servicio persistente nuevo.

Un conflicto o comparación BLOCKED devuelve 2; fallo de verificación/SQL devuelve 1.
Las respuestas ordinarias muestran metadatos y recibos. `export` y `row` dan acceso
explícito a datos privados; el informe incluye las filas completas codificadas en
base64 y `row` las decodifica para revisión. El recibo se consulta con `receipt`
del CLI I4 y siempre representa un resultado histórico.

Aceptar no importa una tarea. Simular no escribe requisitos/tareas D2 ni selecciona
el «después». Una ausencia aceptada produce KEEP_EXISTING_NO_DELETE. Si cambian la
referencia o las versiones de decisión esperadas, hay conflicto sin simulación
parcial; repetir un recibo antiguo no revierte esos cambios.

## I6 — coexistencia SQL sobre V30

[Alcance A13 y matriz](../../docs/design/D5-I6-V30-COMPATIBILITY.md) ·
[Evidencia propia](../../docs/validation/D5-I6-results.md).
Con los mismos requisitos Linux/Python/Docker e imagen PostgreSQL local:

```bash
python3 -m testing.D5.run_v30_lab
```

El runner crea una base nueva, aplica V1–V30 y después V31/V32, ejecuta 36 pruebas
D5 anteriores y cinco casos de coexistencia. Su configuración, contenedor y volumen
son exclusivos y se eliminan al terminar; el resumen privado queda en
`work/d5/postgres/d5-pg-*/v30-results.json`. Retorno 0 significa PASS de esa campaña;
un fallo devuelve no cero y conserva diagnóstico privado. No se cambia ningún
runner anterior ni se arranca el laboratorio HTTPS D4 o el entorno persistente.

Los controles de estado tienen un worker OFFLINE y recursos/catálogo deshabilitados,
sin heartbeat, tareas ni operaciones. Se comprueban conservación del estado
D2/D3/D4, límites de permisos y coexistencia de sus locks con el flujo D5. La
captura D3 del caso T05 es un artefacto de test, sin publicación de planes.
Este runner no ofrece aplicación operativa D2, proveedores, promoción o despliegue.

## I8 — synthetic BACKLOG mapping / mapeo BACKLOG sintético

Run the new disposable campaign / Ejecuta la campaña desechable nueva:

```bash
python3 -m testing.D5.run_mapping_lab
```

[Contract, command files and boundaries / Contrato, archivos de comando y límites](../../docs/design/D5-I8-SYNTHETIC-TASK-LAB.md) ·
[Evidence / Evidencia](../../docs/validation/D5-I8-results.md).
Creates synthetic BACKLOG tasks only; no worker execution or deployment.
Crea solo tareas BACKLOG sintéticas; no ejecuta workers ni despliega.
The previous runners keep their original targets. Los runners anteriores conservan
sus targets originales; Compose dev y D4 permanecen separados.

## I10 — initial import / carga inicial

Run the separate bootstrap campaign / Ejecuta la campaña separada de bootstrap:

```bash
python3 -m testing.D5.run_bootstrap_lab
```

[Guide and explicit commands / Guía y comandos explícitos](../../docs/design/D5-I10-BOOTSTRAP-LAB.md) ·
[Evidence / Evidencia](../../docs/validation/D5-I10-results.md).
Imports selected rows from one real snapshot into synthetic BACKLOG tasks, with
a separate manifest review. Importa filas seleccionadas de un único snapshot real
a tareas BACKLOG sintéticas, con revisión propia del manifiesto.
No activation or deployment. Sin activación ni despliegue; dev/D4 y campañas
anteriores permanecen separados.

## I12 — reviewed reappearance / reaparición revisada

Run the separate campaign / Ejecuta la campaña separada:

```bash
python3 -m testing.D5.run_reappearance_lab
```

[Guide and explicit commands / Guía y comandos explícitos](../../docs/design/D5-I12-REAPPEARANCE-LAB.md) ·
[Evidence / Evidencia](../../docs/validation/D5-I12-results.md).
Reuses existing synthetic BACKLOG tasks after a confirmed absence and explicit
review. Reutiliza tareas BACKLOG sintéticas tras ausencia confirmada y revisión
expresa, sin crear otra tarea o activar trabajo. Dev/D4 and previous campaigns
remain separate. Dev/D4 y campañas anteriores permanecen separados.

## I14 — local edit resolution / resolución de ediciones locales

Run the separate campaign / Ejecuta la campaña separada:

```bash
python3 -m testing.D5.run_local_edit_lab
```

[Guide and explicit commands / Guía y comandos explícitos](../../docs/design/D5-I14-LOCAL-EDIT-LAB.md) ·
[Evidence / Evidencia](../../docs/validation/D5-I14-results.md).
Reviews the full source or local text for existing synthetic BACKLOG tasks.
Revisa texto completo del origen o local para tareas BACKLOG sintéticas existentes,
sin excepción permanente ni extensión a reaparición con edición local.
No activation or deployment; dev/D4 and prior campaigns remain separate.
Sin activación ni despliegue; dev/D4 y campañas anteriores permanecen separados.

## I16 — existing task adoption / adopción de tareas existentes

Run the separate campaign / Ejecuta la campaña separada:

```bash
python3 -m testing.D5.run_adoption_lab
```

[Guide and explicit commands / Guía y comandos explícitos](../../docs/design/D5-I16-ADOPTION-LAB.md) ·
[Evidence / Evidencia](../../docs/validation/D5-I16-results.md).
Adopts existing synthetic BACKLOG tasks after explicit source/task review, preserving
the whole task row. Adopta tareas BACKLOG sintéticas existentes tras revisión
expresa de origen y destino, conservando íntegra la tarea. No activation or
deployment; dev/D4 and previous campaigns remain separate. Sin activación ni
despliegue; dev/D4 y campañas anteriores permanecen separados.

## I18 — local reappearance / Reaparición con divergencia local

```bash
python3 -m testing.D5.run_local_reappearance_lab
```

[Guide and explicit commands / Guía y comandos explícitos](../../docs/design/D5-I18-LOCAL-REAPPEARANCE-LAB.md) ·
[Evidence / Evidencia](../../docs/validation/D5-I18-results.md).
Joint identity and source/local review on a reappeared ID with confirmed I8 absence.
Revisión conjunta de identidad y texto origen/local ante un ID reaparecido con
ausencia I8 aplicada. Own V30 + V31–V38 disposable lab, synthetic BACKLOG fixtures;
separate from dev/D4. Laboratorio desechable propio V30 + V31–V38, fixtures BACKLOG
sintéticas; separado de dev/D4, sin activación, promoción ni despliegue.

## I20 — isolated local edits / Ediciones locales aisladas

```bash
python3 -m testing.D5.run_isolated_local_edit_lab
```

[Guide and explicit commands / Guía y comandos explícitos](../../docs/design/D5-I20-ISOLATED-LOCAL-EDIT-LAB.md) ·
[Evidence / Evidencia](../../docs/validation/D5-I20-results.md).
Resolve a reviewed whole source/local choice against an unchanged selected source
row, with confirmed head provenance. Resolver la pareja origen/local revisada frente
a una fila seleccionada sin cambio semántico, con prueba de cabeza aplicada.
Own V30 + V31–V39 disposable lab; no fabricated I5 comparisons or activation.
Laboratorio desechable V30 + V31–V39 propio, separado de dev/D4; sin comparaciones
I5 ficticias, activación, promoción ni despliegue.

## I24 — offline integration contracts / contratos de integración offline

[I23 aprobado e implementación I24](../../docs/design/D5-I24-OFFLINE-INTEGRATION-LAB.md)
y [resultados propios](../../docs/validation/D5-I24-results.md). Dobles Python en
memoria para el primer corte de 18 criterios; sin HTTP, SQL, Docker ni proveedores.

```bash
python3 -m unittest discover -s testing/D5 -p test_offline_integration.py -v
python3 -m testing.D5.demo_offline_integration
```

The fixed synthetic demo reads a tracked fixture, writes no artifacts and loses all
state on exit. Its receipts are simulated, not remote acknowledgments. D5 global
remains open; 17 other synthetic criteria and seven real-evidence criteria remain
pending. La demo no recibe rutas/URLs/credenciales del operador y no modifica D2.

## I26 — incremental fixture capture / captura incremental sintética

[I25 aprobado e implementación I26](../../docs/design/D5-I26-DRIVE-INCREMENTAL-LAB.md)
y [resultados DI01–DI28](../../docs/validation/D5-I26-results.md): inventario/feed de
fixtures, commits por página, cursor y reinicio con filesystem temporal propio.

```bash
python3 -m testing.D5.run_incremental_lab
```

The runner uses only Python's standard library on Linux, emits sanitized JSON,
and removes its own temporary labs after waiting for its own child processes.
Fault tests kill only children created by this harness. No Google/HTTP, SQL,
Docker, reference selection, persistent D2 effects or real-provider conformance.
G01–G07 remain open. No usar estas fixtures como cliente de una cuenta real.

## I28 — Plane reconciliation model / modelo de conciliación Plane

[Contrato I27 aprobado e implementación I28](../../docs/design/D5-I28-PLANE-RECONCILIATION-LAB.md)
y [resultados PC01–PC32](../../docs/validation/D5-I28-results.md): clave estable de
creación, envíos inciertos, revisión propia y conciliación histórica en memoria.

```bash
python3 -m testing.D5.demo_plane_reconciliation
python3 -m unittest discover -s testing/D5 -p test_plane_reconciliation.py -v
python3 -m testing.D5.run_plane_lab
```

The new model/demo use volatile memory and owned threads, with no HTTP, provider
credentials, durable outbox or D2 writes. The complete runner also executes I26's
separate filesystem/process regressions and verifies their selective cleanup;
Linux/fsync/flock requirements still apply to that regression group. JSON output
labels evidence as synthetic; real Plane capabilities and global G01–G07 remain
open. La demo imprime estados/contadores y pierde su estado al salir; no es un
cliente Plane ni una autorización de activación, promoción o despliegue.

## I30 — relational batch model / modelo de relaciones y lotes

[I29 aprobado e implementación I30](../../docs/design/D5-I30-RELATIONAL-BATCH-LAB.md)
y [resultados RB01–RB34](../../docs/validation/D5-I30-results.md): entidades tipadas,
vínculos explícitos del mismo proyecto, guardas locales y un commit atómico de
fixture con datos, procedencia y recibo juntos.

```bash
python3 -m testing.D5.demo_relational_batch
python3 -m unittest discover -s testing/D5 -p test_relational_batch.py -v
python3 -m testing.D5.run_batch_lab
```

The new model uses volatile memory and owned threads. Source and whole-batch
reviews remain separate; lost-response replay does not repeat effects. No SQL,
HTTP, persistent D2 writes or real-provider conformance. The complete runner also
executes previous regressions: Linux/fsync/flock, temporary roots and child-process
cleanup belong to I26, not to durable batch recovery. G01–G07 remain open.
La demo no recibe rutas/URL/credenciales ni activa trabajo; sus snapshots completos
son privados, y la salida publicada contiene solo estados/contadores saneados.
