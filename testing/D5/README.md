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
