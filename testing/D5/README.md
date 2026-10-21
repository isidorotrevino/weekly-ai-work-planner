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
