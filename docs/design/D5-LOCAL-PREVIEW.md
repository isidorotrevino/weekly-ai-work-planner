# D5 I1 — ingesta local y previsualización

Fecha: 2026-10-21. **D5 iniciado; I1 implementado. D5 abierto.**
Continuación actual: [I2 tabular y comparación, aprobado por D5-A03](D5-REGISTER-COMPARISON.md).
D1–D4 conservan sus aprobaciones, manifiestos y evidencias. D6 no se inicia.

## Decisiones y autoridad

| Decisión | Elección expresa | Consecuencia |
|---|---|---|
| D5-A01 | A: ingesta local y previsualización | Observar bytes/revisión/hash/procedencia y candidatos; no activar tareas |
| D5-A02 | Buscar ejemplos en el checkout local indicado por el usuario | Lectura del corpus existente; no modificarlo, ejecutarlo ni publicarlo |

La publicación del entorno de desarrollo anterior está confirmada en `origin/main`,
commit `c784082`. Esa entrega permanece separada de este incremento D5.

El corpus inspeccionado contiene un plan narrativo, un registro tabular de tareas
y checklists OpenSpec. Hay referencias a herramientas Gentle-AI; no se encontró en
esa inspección un contrato único de plan Gentle-AI ni su script de routing.
Las muestras justifican un perfil estructural acotado, no la aprobación de una
gramática completa ni la interpretación de todo el backlog. Los snapshots reales
permanecen fuera de Git en `work/d5/`; las pruebas versionadas usan contenido sintético.

## Flujo implementado

[`source_ingest`](../../source_ingest/preview.py) es una utilidad local Python de
biblioteca estándar, sin nuevo servicio ni dependencias externas. No sustituye el
control plane Java ni cambia la arquitectura D1. Su entrada es un archivo Markdown
explícito bajo una raíz autorizada y dos UUID de proyecto/documento elegidos por
el llamante. No consulta ni crea esos identificadores en PostgreSQL.

1. Abrir raíz, ancestros y archivo sin seguir symlinks; rechazar traversal,
   hardlinks y archivos no regulares. Lectura acotada, repetida y con contraste de
   metadatos para rechazar cambios observados durante la captura.
2. Calcular SHA-256 sobre los **bytes exactos**, conservados en base64. CRLF, BOM y
   cambios de codificación no se normalizan antes del hash. Solo se admite UTF-8
   (BOM opcional), sin NUL.
3. Extraer encabezados ATX y líneas de checklist, con números de línea/contexto.
   Los bloques delimitados por fences de backticks/tildes y las checklists citadas
   con `>` no producen candidatos. El perfil es léxico: no es un AST CommonMark
   completo; no resuelve HTML, indentación semántica, continuaciones ni anidamiento.
4. Conservar el marcador CHECKED/UNCHECKED como afirmación de la fuente; nunca
   convertirlo en DONE, aprobación, elegibilidad, dependencia o evidencia de ejecución.
   Los candidatos tienen `activation_allowed: false` y localizador hash+línea.
5. Guardar un artefacto JSON canónico, completo y direccionado por su propio hash,
   con permisos 0600 en el almacén local. Publicación local mediante enlace exclusivo
   desde un temporal completo, sin reemplazar otro artefacto. Una repetición exacta
   verifica el existente; contenido alterado o un symlink en destino se rechazan.

Límites: 2 MiB, 20.000 líneas, 65.536 caracteres por línea, 2.000 encabezados y
2.000 candidatos. Excederlos produce error; no se trunca silenciosamente. No se
promete captura atómica frente a un escritor hostil concurrente; usar archivos
estables o snapshots del propietario. La repetición detecta cambios observados,
no aporta atestación del filesystem ni identidad criptográfica del editor.

## Contrato local v1

`schema: d5.local-preview.v1`, `profile: markdown-structure.v1`, `state: PREVIEW_ONLY`.
El artefacto incluye proyecto/documento, ruta **relativa**, etiqueta de revisión,
bytes/base64/hash, encabezados, candidatos y diagnósticos. No almacena la ruta
absoluta de la raíz ni una credencial. El snapshot sí conserva todo el contenido
leído, por lo que debe mantenerse privado y fuera de Git.

`observed_revision` es una etiqueta opaca del llamante, con autoridad declarada
`CALLER_LABEL_ONLY`: no prueba un commit Git, una revisión Drive ni frescura remota.
El hash de contenido identifica los bytes. La misma revisión lógica con bytes
distintos produce otro artefacto; la misma captura con una etiqueta nueva también
se conserva separadamente. No hay head mutable, cursor, elección automática de
"última revisión", borrado, actualización in situ ni garantía de orden de revisiones.

Los IDs de candidato son UUIDv5 de documento, proyecto, hash, perfil y línea.
Sirven dentro de esa revisión; **no son IDs de tareas estables entre revisiones**.
Mover o editar contenido exige un diseño posterior de correspondencias explícitas.
`TABLE_SEMANTICS_NOT_PARSED` señala líneas tabulares sin interpretar. Toda captura
incluye `STRUCTURAL_PREVIEW_ONLY`; el resultado nunca se presenta como importación
semántica completa. Texto, enlaces y comandos de la fuente permanecen inertes;
no se resuelven enlaces ni se llama a modelos, shell, plugins o APIs.

## Relación con D2/D3/D4

D2 ya conserva `SourceDocument`, `SourceRevision`, `ExternalBinding`, vínculos de
requisitos y `d2.task_sources`. `d2.sync_source` compara revisión externa/hash local
esperados y conserva conflictos; `d2.ack_outbox` registra acuses de entrega. Estos
contratos se mantienen sin modificaciones. D5 I1 **no llama a esas funciones**,
no escribe SQL, no altera reservas, prioridades, estados ni aprovisiona operaciones
para D3/D4. Su almacén es solo evidencia local de previsualización.

Antes de una importación persistente hay que concretar mapeo de identidad/namespace,
procedencia, propiedad de campos, cambios/borrados y aprobación de propuestas.
V10 deduplica revisiones por documento+hash; no debe reinterpretarse una etiqueta
externa nueva con bytes idénticos como una historia de revisiones externas completa.
La observación local de I1 conserva por separado esas etiquetas sin ampliar SQL.
Una integración posterior requerirá diseñar su registro de observaciones/cursor,
CAS transaccional y backfill antes de cualquier propuesta de migración.

## Validación y siguiente corte

[Uso y pruebas](../../testing/D5/README.md) · [Resultados nuevos](../validation/D5-I1-results.md).
No se vuelven a contar pruebas históricas D4. No hay red, credenciales reales,
Drive/Plane, activación, promoción ni despliegue.

Decisión pendiente al emitir I1 (resuelta después por D5-A03 en I2): perfil tabular explícito para previsualizar
filas con identidad y procedencia frente a formalizar primero una muestra concreta
Gentle-AI. Cualquiera requiere definir campos, ambigüedades, versiones y cambios
entre revisiones antes de persistir o activar tareas. D5 no se declara terminado
por esta previsualización.
