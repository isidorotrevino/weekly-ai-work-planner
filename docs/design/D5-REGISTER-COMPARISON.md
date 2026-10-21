# D5 I2 — registro tabular y comparación entre observaciones

Fecha: 2026-10-21. **Implementado y validado localmente; D5 abierto.**
[I1 y fronteras](D5-LOCAL-PREVIEW.md) · [Uso](../../testing/D5/README.md) ·
[Evidencia I2](../validation/D5-I2-results.md).

## D5-A03 — decisión expresa

El usuario eligió A: perfil tabular estricto; conservar filas y estados como datos;
corresponder por documento+ID; bloquear toda comparación ante duplicados o filas
ambiguas; ausencia sin borrado ni cierre. No autoriza modificar las fuentes,
interpretar sus aprobaciones, conectar proveedores ni persistir tareas en SQL.
D1–D4 y sus evidencias se conservan. D6 no se inicia.

## Perfil optativo

El perfil existente `markdown-structure.v1` y sus artefactos I1 siguen iguales.
`--profile task-register.v1` produce `schema: d5.local-preview.v2` y exige esta
cabecera exacta, en este orden:

```text
ID | Item | Component(s) | Objective | Blocked on | Status | Verified | Source
```

Se exige pipe de apertura/cierre, ocho celdas y una línea separadora con al menos
tres guiones por celda (alineación `:` opcional). Cada tabla repetida vuelve a
exigir su cabecera. Una línea vacía, narrativa o fence termina la tabla reconocida;
las filas con ID fuera de ella se diagnostican y bloquean la comparación.
No se reconstruye silenciosamente una tabla fragmentada. Una tabla reconocida
vacía es una observación explícita; un documento sin tabla reconocida se bloquea.

Los pipes precedidos por un número impar de backslashes no separan celdas. Se
conservan los escapes y el Markdown en sus valores; se recorta solo el espacio
exterior de cada celda. Un pipe sin escapar, incluso dentro de backticks, sigue
siendo separador. No se interpreta un ancho incorrecto como una columna extra de
comentarios. No se concatenan líneas ni se sigue un enlace de `Source`.

El ID admite `[A-Z][A-Z0-9_]*-[0-9]+`, plano o envuelto exactamente en `~~…~~`.
Se conservan su forma original y `source_struck`; quitar ese envoltorio identifica
la clave de origen sin inferir cierre. No hay conversión de mayúsculas, números o
ceros iniciales. `PT-1` y `PT-01` son claves distintas. Otras decoraciones de ID no
se normalizan implícitamente. `Status`, `Blocked on`, `Verified` y `Source` son
texto de origen, sin estados de workflow, dependencias o evidencia inferidos.

Cada fila válida conserva sus ocho campos, línea, encabezados, clave, localizador
hash+línea y candidato de revisión. La identidad estable de origen es UUIDv5 de
proyecto+documento+perfil+clave; **no es un UUID de tarea SQL**. El ID del candidato
sigue incluyendo hash/línea, por lo que cambia entre revisiones. Duplicados, incluso
entre tablas o con tachados distintos, se conservan como candidatos separados y
bloquean el conjunto. Las filas no interpretables permanecen en los bytes del
snapshot y en diagnósticos con línea; no se inventan celdas para ellas.

Tablas ajenas permanecen sin interpretar. Una fila con clave fuera de tabla, una
cabecera `ID` no reconocida o una fila ajena de ocho columnas impide declarar la
comparación segura. La indentación tabular mayor de tres espacios, un fence
incompleto y líneas de bloque que comienzan con `<` también bloquean. Sigue siendo
un perfil léxico acotado, no un parser CommonMark/GFM/HTML completo. Dentro de las
celdas se conserva el marcado como texto inerte.

## Verificación y comparación

`python3 -m source_ingest.compare` recibe explícitamente dos artefactos locales.
No elige un head ni ordena etiquetas de revisión. Antes de comparar:

1. Abre archivos regulares sin symlinks/hardlinks, hasta 32 MiB, contrastando sus
   metadatos durante la lectura. El nombre debe ser su SHA-256 y el JSON canónico.
2. Rechaza claves JSON duplicadas y reconstruye toda la observación desde sus bytes
   base64 con el perfil declarado. Exige igualdad canónica exacta: editar filas,
   hashes, IDs, diagnósticos o elegibilidad y recalcular solo el nombre no basta.
3. Exige el mismo proyecto, documento y perfil tabular en ambas observaciones.
   Las capturas I1 se pueden verificar, pero no comparar como registros tabulares.
4. Si cualquiera tiene diagnósticos bloqueantes, conserva un informe `BLOCKED`, sin
   lista parcial de cambios, y devuelve código 2. Datos inválidos/incompatibles dan
   código 1. Una comparación válida devuelve 0 y sigue siendo `PREVIEW_ONLY`.

La reconstrucción detecta alteraciones inconsistentes, pero **no autentica al autor**:
el llamante puede crear otra captura coherente de otros bytes. Las identidades y
etiquetas son del operador, sin atestación de Git/proveedor. Una etiqueta reutilizada
con bytes distintos produce un aviso; no se inventa un conflicto remoto ni un orden.

Los campos recortados de las ocho celdas se comparan por igualdad exacta para cada
clave. No hay coincidencia difusa ni correspondencia por título, línea o similitud.
El contexto de encabezados queda en las capturas; no se interpreta como estado.
Un desplazamiento de línea se informa aparte con `location_changed`.

| Resultado | Significado de la observación |
|---|---|
| `ADDED` | Clave presente solo en la captura indicada como posterior |
| `CHANGED` | Misma clave, campos distintos; enumera los nombres de los campos |
| `UNCHANGED` | Mismos campos; puede haber desplazamiento de línea |
| `ABSENT_IN_OBSERVATION` | Clave no vista en esa captura, sin inferir borrado/cierre |

El informe referencia hashes de ambas capturas, candidatos y localizadores. Se
conserva como otro JSON privado, inmutable para la herramienta y direccionado por
contenido (`d5.local-comparison.v1`). No cambia capturas, archivos fuente, heads,
cursores, reservas, dependencias ni tareas. No genera SQL ni comandos de ejecución.

## Corpus real y siguiente frontera

El registro autorizado demuestra un caso de bloqueo útil: las tablas fragmentadas
y ciertas filas no conformes al perfil no se reparan para obtener un resultado
verde. Las filas válidas son previsualizaciones parciales; el informe completo
permanece bloqueado. [Conteos y pruebas](../validation/D5-I2-results.md).

Siguiente decisión material: aprobar un perfil versionado de compatibilidad para
esas variaciones concretas, o mantener el contrato estricto y preparar una copia
normalizada revisada por el propietario. La fuente original permanece intacta.
La gramática Gentle-AI completa y cualquier aplicación persistente de propuestas
requieren contratos posteriores; I2 no aprueba esas ampliaciones.
