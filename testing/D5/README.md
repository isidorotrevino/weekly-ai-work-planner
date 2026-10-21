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
