# D5 I3 — compatibilidad optativa y anotaciones de origen

Fecha: 2026-10-21. **Implementado y validado; D5 abierto.**
[Contrato estricto I2](D5-REGISTER-COMPARISON.md) ·
[Uso](../../testing/D5/README.md) · [Resultados I3](../validation/D5-I3-results.md).

## Decisiones expresas

| ID | Elección del usuario | Consecuencia |
|---|---|---|
| D5-A04 | A: nuevo perfil de compatibilidad optativo | Admitir blancos entre filas bajo la misma cabecera; narrativa, encabezados Markdown o fences terminan la tabla. Conservar el original y el perfil estricto |
| D5-A05 | A: anotación de origen separada | Conservar texto y posición después de las ocho celdas, comparar sus cambios y no inferir aprobación, cierre ni verificación |

La nueva selección es `--profile task-register-compat.v1`. Sigue usando
`d5.local-preview.v2` con un perfil propio; no cambia el comportamiento ni los
artefactos `markdown-structure.v1` o `task-register.v1`. No normaliza ni reescribe
la fuente. No añade SQL, tareas, fuentes de red, credenciales reales ni D6.

## Continuación de filas

Una vez reconocidas la cabecera exacta de ocho campos y su separador, las líneas
vacías o con solo espacios pueden separar filas sin perder esa cabecera. Al
retomar una fila se registra `REGISTER_BLANK_CONTINUATION`, sus líneas vacías y la
línea retomada. Un blanco entre cabecera y separador sigue siendo inválido.

Una línea narrativa, un encabezado Markdown o un fence cierra la continuidad:
una fila posterior necesita otra cabecera. Otras tablas, HTML, indentaciones no
soportadas, IDs inválidos, filas de ancho ambiguo y duplicados conservan las guardas
I2 y bloquean la comparación completa. No se buscan cabeceras antiguas a través de
otras secciones ni se relaja el perfil estricto silenciosamente.

## Anotación posterior al cierre

Además de una fila normal de ocho celdas, el perfil admite exactamente nueve pipes
**no escapados**: apertura, siete divisiones y cierre. Si después del cierre queda
texto no blanco, ese sufijo se conserva aparte. Otro pipe sin escapar en el sufijo
hace ambiguo el ancho y bloquea la fila. Los pipes escapados se conservan como texto.
Esta regla es una convención explícita del perfil, no una afirmación de conformidad
CommonMark/GFM ni una prueba de lo que quiso expresar el autor.

Cada candidato incluye `source_annotation: null` o un objeto con:

- `text`: sufijo exacto después del cierre, incluidos espacios iniciales/finales;
- `line`: línea de origen, comenzando en 1;
- `column_start`, `column_end`: posiciones inclusivas, comenzando en 1, en caracteres
  Unicode de la línea decodificada con UTF-8/BOM opcional, sin terminador CR/LF.
  Son posiciones de caracteres, no bytes ni anchuras visuales de tabulación.

El snapshot conserva los bytes originales, incluido BOM/CRLF. Una cola de solo
espacios no se interpreta como anotación; sigue presente en esos bytes. El marcado,
enlaces, afirmaciones de estado y comandos del sufijo permanecen inertes.
`Status`, `Verified` y `Source` retienen sus celdas; no se les incorpora el sufijo.
Las anotaciones se señalan con `REGISTER_SOURCE_ANNOTATION`, sin verificación factual.

La reconstrucción de artefactos vuelve a obtener texto, posiciones, diagnósticos y
contadores del snapshot. Editarlos y cambiar el nombre/hash del JSON no permite
fabricar una observación coherente distinta de esos bytes. Esto no autentica al
editor: las identidades y etiquetas siguen perteneciendo al llamante, como en I2.

## Comparación

Ambas observaciones deben usar el mismo perfil, proyecto y documento. No se permite
comparar estricto contra compatible. La identidad de origen sigue incluyendo el
perfil; no se hace una migración ni alias automático de identidades entre perfiles.
Los resultados anteriores y su bloqueo conservan su significado original.

Además de las ocho celdas, se compara el texto exacto de `source_annotation`:
introducirlo, cambiarlo o retirarlo da `CHANGED` con ese nombre en `changed_fields`.
Cambiar solo su posición conserva `UNCHANGED` y marca `annotation_location_changed`.
El informe incluye la posición de cada anotación en su referencia de captura; el
texto completo permanece en los snapshots referenciados. La comparación de campos
no deduce significado de encabezados ni de expresiones como "aprobado" o "verificado".

Una anotación añadida o retirada es un cambio de contenido, no un movimiento. Para
anotaciones presentes en ambas capturas, la bandera de ubicación contrasta línea e
intervalo de columnas; puede cambiar también si un texto cambia de longitud. Los
resultados siguen siendo PREVIEW_ONLY y `activation_allowed: false`.

## Resultado y frontera siguiente

En el corpus autorizado se capturan las 627 filas, los 295 IDs tachados, dos
continuaciones y cinco anotaciones. La comparación consigo mismo devuelve 627
UNCHANGED; acredita reproducibilidad estructural, no una nueva revisión real ni
verificación de sus afirmaciones. La fuente, los artefactos I1 y el informe estricto
BLOCKED I2 se conservan intactos. [Evidencia detallada](../validation/D5-I3-results.md).

Quedan pendientes un contrato de revisión/aplicación de propuestas o el diseño de
persistencia de fuentes, observaciones y correspondencias. D5 I3 no autoriza
importación SQL, activación de tareas, nuevos contratos de ejecución, promoción,
conexiones reales ni despliegue. D1–D4 y D6 conservan sus fronteras.
