# D5 I26 — laboratorio de captura incremental sintética

Fecha: 2026-10-22. Implementa [I25](D5-I25-DRIVE-INCREMENTAL-DESIGN.md) y
[DI01–DI28](D5-I25-DRIVE-INCREMENTAL-REVIEW.md), solo para
GI07/GI08/GI09/GI11 sintéticos. [Resultados propios](../validation/D5-I26-results.md).
**D5 global abierto; sin validación Google real o ampliación del hito aceptado.**

English: owned temporary filesystem lab for synthetic inventory/feed pages,
page-atomic commits, process restart and fault recovery. No Google SDK/HTTP,
credentials, SQL, Docker, D2 application, reference selection, activation,
promotion, deployment or D6. Local process/fsync tests do not prove power-loss,
hardware, hostile-owner or real-provider guarantees.

## Autoridad y ejecución

D5-A63: el usuario aprueba I25 y autoriza implementar/validar DI01–DI28 en un
laboratorio temporal propio, con fixtures sintéticas, conservando A60–A62 y
G01–G07 abiertos. I25 publicado/verificado en `main`:
`e66a42c00d8953b77dd9a91d307da94ff4f9172a`.

Desde la raíz del repositorio, Linux/Python 3 con biblioteca estándar y filesystem
local que soporte rename atómico, fsync, flock y permisos Unix:

```bash
python3 -m testing.D5.run_incremental_lab
python3 -m unittest discover -s testing/D5 -p test_incremental_capture.py -v
```

El primer comando ejecuta la campaña completa Python y emite JSON saneado con IDs
de test, resultado y contadores de limpieza; no escribe un informe por sí mismo.
El segundo ejecuta únicamente los tests nuevos. El harness lee fixtures de Git,
crea carpetas privadas `d5-drive-*` bajo el temporal del sistema y las conserva
entre hijos de la prueba. Finalmente espera/termina solo sus hijos y elimina sus
propias raíces. No admite URL, credencial, PID externo, raíz de borrado o captura
privada como entrada. Los tests con SIGKILL actúan solo sobre hijos creados por él.

No usar como ingestión de una cuenta real. Las páginas normalizadas y estados de
fuente son datos de prueba; no un contrato exacto de respuesta API Google.

## Implementación y unidad de confirmación

[`incremental_fixture`](../../source_ingest/incremental_fixture.py) añade
`TemporaryFixtureLab`, `FixtureStore` y builders cerrados de scope/evento/página.
No cambia `offline.py`, parsers, fixtures ni entrypoints históricos.

| Operación | Frontera |
|---|---|
| Crear laboratorio | Raíz nueva, run_id, scope canónico y mapa explícito file→document/perfil; génesis fija ancla previa al inventario |
| `snapshot()` | Valida head y cadena completa; devuelve fase/token/versiones y conteos sin bytes fuente |
| `advance(command)` | Valida/prepara página completa, revalida bajo lock y CAS de cabeza, publica objeto inmutable y head atómico; no efectos parciales |
| `read_command(id, hash)` | Busca exclusivamente en cadena alcanzable; sincroniza directorios antes de devolver confirmación recuperada; otro hash da conflicto |
| `inspect()` | Devuelve cadena de fixtures completa y privada, incluidos bytes; no es salida saneada de publicación |
| Cerrar laboratorio | Solo la raíz creada por ese objeto, cuya identidad dev/inode retiene el creador; sin seguir symlinks hacia fuera |

Fases INVENTORY→CATCHUP→FOLLOWING y tokens opacos/versionados siguen I25. Una
página terminal vacía puede confirmar el mismo token; no hay polling/daemon sin
límite. Cada llamada es acotada y el presupuesto total de commits detiene progreso
adicional sin truncar. Un error de intento bloquea ese intento conservando el cursor
confirmado previo; no se escribe un avance para registrar el fallo.

El commit contiene request, versiones/hash de cabeza esperada, estado antes/después,
resultados de **todos** los eventos y recibo. Los bytes de página y captura pueden
repetirse físicamente; la vista lógica deduplica por scope/file/document/perfil,
revisión/metadatos/grado y hash de contenido, conservando ocurrencias. No se elige
una revisión «vigente» ni se produce una ausencia I8 aplicada.

La escritura usa temporales privados y objeto direccionado por SHA-256 sin
reemplazarlo, fsync de archivo/directorio, temporal de head, reemplazo atómico y
fsync de raíz. El cursor está dentro del commit señalado por head, no en otro
checkpoint. Un objeto huérfano no es un comando aplicado y nunca gana por fecha.
Head, objetos, schema, parents, scope y resultados se reconstruyen/validan antes
de aceptar la cadena; corrupción bloquea sin reparación automática.

## Fuentes bloqueadas y recuperación

A62 permite diagnósticos terminales explícitos por archivo sin referencia D5 ni
escritura D2. Fuera de allowlist, MIME no admitido, removal/acceso perdido, archivo
no disponible concluyente o tamaño fuera de límite conservan diagnósticos, no bytes
ficticios. Una fuente accesible posterior puede capturarse sin borrar su diagnóstico.

Parser ambiguo/perfil desconocido o encoding no admitido conservan bytes acotados
como CAPTURED_BLOCKED. Cambio durante captura, timeout/rate limit o fallo global de
autorización/ámbito bloquea la página completa. La entrada no admite un flag
`terminal` del llamante para saltar fallos. Google Docs exportado conserva
OBSERVED_EXPORT, formato y exportador de fixture, sin elevarse a revisión inmutable.

Una respuesta perdida después de head se recupera por ID/hash sin reversionar la
cabeza actual. Error de fsync tras reemplazo da UNKNOWN_COMMIT: no se devuelve
éxito hasta observar una cadena válida y sincronizar sus directorios. Si la
sincronización de recuperación sigue fallando, también queda UNKNOWN_COMMIT.
Los fallos antes de head dejan su estado previo; no se adoptan temporales/huérfanos.
No se promete reparación automática si un archivo alcanzable presenta hardlinks,
symlinks, corrupción o identidad incompatible.

Los hooks de fallo/barrera de preparación son parámetros explícitos del constructor
para el harness confiable; los eventos/commands no pueden activarlos ni aportar
señales/PIDs. Los dos escritores de DI14 se detienen tras preparar la misma cabeza
y se liberan juntos para ejercitar revalidación y exclusión entre procesos.

## Límites y evidencia

16 eventos/página, objeto JSON completo ≤32 MiB, fuente ≤2 MiB con límites I1/I24,
tokens ≤256 caracteres y ≤1.024 commits alcanzables, incluido génesis. Los límites
no son cuotas/máximos Google. Las pruebas de historia usan además un presupuesto
pequeño controlado para ejercitar exactamente el límite sin una campaña de tamaño.

La campaña registra 30 tests nuevos sobre 28 casos y 86 regresiones Python,
116 distintos sin fallos/errores/omisiones. Se crean 33 raíces propias; las siete
instancias de hijo terminan y las 33 raíces se comprueban eliminadas. Cuatro hijos
se matan mediante SIGKILL en puntos del protocolo. Los sentinels hermanos se crean
como fixtures de prueba; no se inspeccionan dev/run_data/D4 ni corpus privado.
Los counts/digests están en el informe propio, no en manifiestos históricos.

Este PASS es de filesystem/procesos locales con fixtures confiables. No prueba
pérdida de energía, disco defectuoso, NFS/Windows, restauración hostil o identidad
criptográfica. La marca no es autenticación: la API Python no aísla a un llamante
que modifique sus atributos o el filesystem como propietario. Capturas/inspect
contienen bytes completos y son privados; recibos/snapshot/runner los evitan.

GI07/GI08/GI09/GI11 tienen evidencia sintética propia; los 18 criterios I24 conservan
su evidencia de modelo/regresión. Quedan 13 criterios sintéticos y siete de
evidencia real fuera de este corte. No se declara completo GI38/GI39/GI40 ni
ninguna brecha global G01–G07 por cubrir solo la frontera de captura. Sin SQL,
conectores reales, elección de referencia, efectos D2, activación, promoción,
despliegue ni D6.
