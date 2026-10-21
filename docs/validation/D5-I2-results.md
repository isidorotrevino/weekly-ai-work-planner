# D5 I2 — resultados del registro tabular y comparación

Fecha: 2026-10-21, Europe/Madrid. Base Git: `6aac999` (I1 publicado).
**D5 abierto.** [Decisión D5-A03 y contrato](../design/D5-REGISTER-COMPARISON.md) ·
[Uso](../../testing/D5/README.md). Sin activación de tareas, SQL, proveedores,
credenciales reales, promoción, despliegue o inicio de D6.

## Suite y CLI

Linux, Python 3.14.4, biblioteca estándar. Ejecución:
`python3 -m unittest discover -s testing/D5 -v`.
**33 pruebas, cero fallos:** 17 regresiones I1 y 16 pruebas nuevas I2.

Las pruebas I2 cubren campos escapados y tachados; duplicados entre tablas;
pipes sin escapar incluso en código; cabeceras, separadores, cierres e IDs no
conformes; tablas desconocidas, indentación y HTML; fences; cambios, movimientos,
altas y ausencias; etiquetas nuevas con los mismos bytes; tabla vacía frente a
ausencia de tabla; compatibilidad proyecto/documento/perfil; manipulación de campos,
activación, hashes, metadatos y elegibilidad; JSON con claves duplicadas, atributos
extra, hash de nombre incorrecto y symlinks; reutilización de etiquetas; límite de
filas sin truncado; códigos de salida del comparador y guardado de informes.

La demo `python3 -m testing.D5.demo_register` y los CLI de ingesta/comparación se
comprobaron con dos fixtures sintéticas. Resultado PREVIEW_ONLY: un ADDED, un
CHANGED, un UNCHANGED desplazado y un ABSENT_IN_OBSERVATION. El cambio de tachado
se conserva como diferencia de campo de origen, sin traducirlo a DONE. Todos los
resultados conservan `activation_allowed: false`. Una comparación bloqueada guarda
un informe sin cambios y devuelve código 2; entradas inválidas dan código 1.

## Corpus real: bloqueo esperado, no aceptación forzada

Se volvió a observar el registro autorizado en el checkout local indicado por el
usuario. Solo lectura, sin modificarlo ni ejecutar su código. Snapshot completo,
rutas, diagnósticos por línea e informes quedan privados en `work/d5/i2/`.
Ningún contenido ni nombre privado se añade a Git.

Un conteo independiente local identifica 627 filas con ID, 15 cabeceras, 332 IDs
planos y 295 tachados. La prueba del perfil estricto obtuvo:

| Dato observado | Resultado |
|---|---:|
| Cabeceras reconocidas | 15 |
| Filas dentro de tablas reconocidas | 535 |
| Candidatos de esas filas con ocho campos válidos | 530 |
| Candidatos válidos tachados | 272 |
| Filas no conformes al ancho/cierre del perfil | 5 |
| Filas con clave fuera de tabla reconocida | 92 |
| Diagnóstico de líneas de otras tablas | 1 |

Las cinco filas no conformes permanecen en el snapshot y en el diagnóstico
REGISTER_ROW_WIDTH. Las 92 filas fuera de cabecera reconocida producen
KEY_OUTSIDE_REGISTER_TABLE, sin recomponer tablas fragmentadas tras interrupciones.
Los pipes escapados se separaron correctamente; no se confundieron con columnas.
El conteo inicial por delimitadores no bastaba para comprobar cierres y continuidad
de tablas; la prueba completa del perfil sí detecta esos casos.

**La comparación del registro consigo mismo devuelve BLOCKED y cero cambios**, con
código de salida CLI 2. Se comprobó como resultado conservador esperado: no es un
fallo oculto de pruebas ni una declaración de que el registro entero se haya
interpretado. Los 530 candidatos son una previsualización parcial, no tareas
importadas. El artefacto conserva los bytes de las 627 filas y del resto del archivo.

Repetir la captura produjo el mismo artefacto/hash. El hash de la fuente se conservó
antes/después. No se corrigió el registro para obtener un resultado verde. Aprobar
un perfil compatible o una copia normalizada es una decisión posterior explícita.

## Preservación y límites

Los tres artefactos reales I1 se reconstruyeron íntegramente desde sus bytes y
metadatos; conservan sus hashes y el perfil original. El informe I1 no se reescribe.
Las entradas de hashes D3/D4 siguen coincidiendo con sus manifiestos; no cambian SQL,
workers, baterías históricas ni targets D1–D4. La comparación es local y no requiere
repetir la matriz SQL/Compose.

Los snapshots no autentican al autor ni el orden de revisiones. La reconstrucción
rechaza campos derivados inconsistentes; no impide crear una observación coherente
de otros bytes bajo identidades del llamante. El perfil no es un parser Markdown
completo y no interpreta estados, dependencias ni evidencia externa. Ausencias y
altas son datos entre dos capturas elegidas explícitamente, sin aplicación automática.

Validación de entrega: sintaxis Python, enlaces locales, chequeo de publicación y
`git diff --check`. Evidencia bruta en `work/d5/i2/unittest.log`,
`real-register-summary.json`, `previews/`, `comparisons/` y `demo/`, excluida de Git.
