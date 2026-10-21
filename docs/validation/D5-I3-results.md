# D5 I3 — resultados de compatibilidad y anotaciones

Fecha: 2026-10-21, Europe/Madrid. Base Git: `72c1a56` (I2 publicado).
**D5 abierto.** [Decisiones D5-A04/A05 y contrato](../design/D5-REGISTER-COMPATIBILITY.md) ·
[Uso](../../testing/D5/README.md). Sin SQL, activación, proveedores, credenciales
reales, promoción, despliegue ni inicio de D6.

## Pruebas y CLI

Linux, Python 3.14.4, biblioteca estándar; sin dependencias nuevas ni conexiones de
red. `python3 -m unittest discover -s testing/D5 -v`: **44 pruebas, cero fallos**,
con 33 regresiones I1/I2 y 11 pruebas nuevas I3. No se suman ejecuciones históricas.

Las pruebas nuevas cubren continuidad por blancos con cabecera vigente; interrupción
por narrativa, encabezado, fence u otra tabla; separador que no admite blancos;
texto/posiciones de anotación con Unicode, BOM y CRLF; introducción, cambio y retirada
de anotación; desplazamiento sin cambio de texto; columnas ambiguas, duplicados e
IDs inválidos que siguen bloqueando; pipes escapados en anotaciones; preservación
del perfil estricto y rechazo entre perfiles; manipulación de texto/posiciones/
contadores detectada por reconstrucción; afirmaciones y comandos inertes.

Se comprobaron el CLI de ingesta con `--profile task-register-compat.v1` y la demo
`python3 -m testing.D5.demo_register --profile task-register-compat.v1`.
La demo da un CHANGED por texto de anotación y un UNCHANGED desplazado. Capturas e
informes siguen siendo PREVIEW_ONLY y no permiten ejecución.

## Registro real autorizado

La fuente se leyó sin modificarla. Evidencia privada, snapshots e informes en
`work/d5/i3/`; no se publican contenido, nombres ni rutas privadas en Git.

| Dato | Resultado |
|---|---:|
| Cabeceras reconocidas | 15 |
| Filas y candidatos conservados | 627 |
| IDs tachados conservados | 295 |
| Continuaciones por blancos registradas | 2 |
| Anotaciones separadas conservadas | 5 |
| Comparación consigo mismo | 627 UNCHANGED |
| Salida CLI del comparador compatible | 0, PREVIEW_ONLY |

Se contrastaron las cinco posiciones con la subcadena exacta de cada línea de
origen. Las anotaciones no se mezclaron con las ocho celdas ni se interpretaron
como estado o aprobación. La repetición produjo la misma captura y hash. El hash
del original no cambió.

Para probar una diferencia en el corpus grande, se creó una **copia sintética local**
y se añadió un marcador a una sola anotación. El original permaneció intacto.
Resultado: 626 UNCHANGED y un CHANGED, exclusivamente en `source_annotation`.
No se presenta esa copia como una nueva revisión real del proyecto ni como historia
Git. Texto y posiciones permanecen ligados a los bytes de cada snapshot.

## Preservación y límites

Se reconstruyeron los tres artefactos I1 con sus hashes originales. La captura
estricta I2 y su informe BLOCKED se reconstruyeron y conservaron exactamente sus
hashes. El comparador rechazó cruzar estricto y compatible; no se renombraron ni
migraron identidades automáticamente. Los informes anteriores conservan sus conteos
y resultados, incluido el bloqueo original I2.

Las entradas de hashes D3/D4 permanecen intactas, sin cambios en migraciones,
componentes o targets históricos. Los cambios de este corte se limitan a la ingesta
local D5, pruebas y documentación; no necesitan repetir las baterías SQL/Compose.

PREVIEW_ONLY acredita extracción y comparación estructural reproducibles. No
acredita autor, frescura, commits, verdad de una anotación, completitud semántica,
verificación de trabajo ni autoridad para crear/cerrar tareas. El perfil sigue
siendo léxico y explícito; las ambigüedades adicionales y duplicados bloquean el
conjunto. No se aplica una interpretación tolerante al perfil estricto.

Chequeos de entrega: sintaxis Python, enlaces locales, revisión del diff,
`python3 scripts/check-publication.py` y `git diff --check`. Evidencia bruta en
`work/d5/i3/unittest.log`, `validation-summary.json`, `real-register-summary.json`,
`previews/`, `comparisons/` y la copia sintética `derived-register.md`, fuera de Git.
