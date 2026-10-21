# D5 I1 — resultados de ingesta local y previsualización

Fecha: 2026-10-21, Europe/Madrid. Base: `c784082` (entorno local publicado en
`origin/main`). D5 iniciado por petición expresa y opción A de ingesta local;
**D5 sigue abierto**. [Contrato](../design/D5-LOCAL-PREVIEW.md) ·
[Uso y pruebas](../../testing/D5/README.md).

## Validación propia

Linux, Python 3.14.4, biblioteca estándar; sin red, Docker, JDK/Maven ni base de
datos en esta campaña. No se modificaron los componentes de D1–D4, sus SQL,
manifiestos o evidencias. No se contactaron proveedores ni se activaron tareas.

`python3 -m unittest discover -s testing/D5 -v`: **17 pruebas, cero fallos**.
Cubren bytes exactos/CRLF, hash y localizadores; fences y citas; tablas sin
interpretar; fence incompleto; repetición del artefacto y permisos; cambios de
bytes, etiqueta de revisión y proyecto; traversal; symlinks en archivo/ancestros/
raíz; hardlinks y FIFO; UTF-8, NUL, tamaños y conteos; identidad y etiqueta inválidas;
artefacto alterado o symlink; comandos inertes; rechazo de mutación observada durante
lectura. Las pruebas usan fixtures sintéticas, no copias del corpus privado.

CLI ejecutada con `testing/D5/fixtures/plan.md`: dos encabezados, dos candidatos,
PREVIEW_ONLY, activación denegada y diagnóstico de tabla. Repetir el mismo comando
devuelve el mismo artefacto. Entrada inexistente: salida 1 sin previsualización.

## Contraste con el corpus real autorizado

Se revisaron tres archivos explícitos del checkout indicado por el usuario, sin
modificarlo ni ejecutar su código. Se conservan privadamente snapshots, hashes,
rutas relativas y artefactos en `work/d5/real-corpus.json` y `work/d5/previews/`.
No se publican nombres privados, instrucciones, comandos, contenido ni copias de
esas fuentes en este repositorio.

| Muestra | Bytes | Encabezados | Candidatos checklist | Diagnóstico |
|---|---:|---:|---:|---|
| Plan narrativo | 55.891 | 54 | 0 | Tablas no interpretadas; solo estructura |
| Registro tabular | 1.209.457 | 21 | 0 | Tablas no interpretadas; solo estructura |
| Checklist OpenSpec | 9.130 | 9 | 16 | Tablas no interpretadas; solo estructura |

Cada observación se repitió con el código final: mismo artefacto/hash y archivos
fuente intactos. Los 16 candidatos son marcadores de la fuente, no 16 tareas
creadas, elegibles, aprobadas o completadas. Los planes narrativos y registros
quedan capturados, pero no se fuerza una extracción semántica donde no hay perfil.

## Límites y controles

No hay parser Gentle-AI completo, correspondencia entre revisiones, importación
PostgreSQL, cursor, sincronización, decisión de revisión vigente, resolución de
dependencias ni activación D3/D4. `observed_revision` es una etiqueta del llamante,
no una prueba de commit. La repetición de lectura detecta cambios observados; no
promete atomicidad ante un escritor concurrente hostil. Se conservan los límites
de captura y el carácter parcial descritos en el contrato.

Las 17 pruebas y tres observaciones son nuevas evidencias D5, sin sumarse a los
resultados históricos D2/D3/D4. Los manifests anteriores se comprueban sin
reescribirlos. No se requieren regresiones SQL al no modificarse esos contratos.
El chequeo de publicación, enlaces locales, sintaxis Python y `git diff --check`
se ejecutan antes de la entrega. No hay promoción, despliegue ni inicio de D6.
