# D5 I25 — contrato de captura incremental Drive sintética

Fecha: 2026-10-22. **PREPARADO PARA REVISIÓN; sin implementación nueva.**
Cobertura propuesta: GI07/GI08/GI09/GI11 de
[I23](D5-I23-GLOBAL-INTEGRATION-DESIGN.md), conservando
[I24 offline](D5-I24-OFFLINE-INTEGRATION-LAB.md) y el
[hito aceptado I1–I20](D5-LOCAL-SYNTHETIC-approved.md).
[Matriz DI01–DI28](D5-I25-DRIVE-INCREMENTAL-REVIEW.md) ·
[Comprobaciones documentales](../validation/D5-I25-design-review.json).

English: proposed synthetic incremental ingestion with inventory/feed fixtures,
page-atomic filesystem commits and process-restart recovery in an owned temporary
lab. No Google client, real data/credentials, SQL, Docker, D2 application, automatic
reference selection, activation, migration promotion, deployment or D6 scope.

## Decisiones expresas y perímetro

| ID | Decisión | Consecuencia |
|---|---|---|
| A60 | Priorizar diseño de Drive incremental/recuperación GI07/GI08/GI09/GI11 | Contrato y matriz antes de implementar |
| A61 | Carpeta temporal propia y marcada del harness, conservada durante reinicios y eliminada selectivamente al finalizar | Sin almacenamiento en dev/run_data ni conservación entre sesiones |
| A62 | Diagnóstico terminal explícito/recuperable permite confirmar un evento no capturable; transitorios impiden confirmar la página | Cursor de captura separado de referencia D5 y efecto D2; ausencia nunca borra/cierra |

Se propone un módulo/harness nuevo de biblioteca estándar Python sobre Linux y
filesystem local con rename atómico, fsync y flock. Solo fixtures públicas
sintéticas; los parsers, dobles y contratos existentes permanecen intactos.
No reutilizar snapshots privados ni configuración/env de un servicio real.
A60–A62 fijan decisiones; no aprueban todavía el contrato completo ni su implementación.

## Identidad, ámbito y límites

Crear una raíz nueva con run_id UUID aleatorio, marca de propiedad y configuración
canónica. Scope hash fija proyecto, conector sintético, identidad/corpus/drive
**de fixture**, allowlist explícita file_id→document_id/perfil, MIME/exportación y
versión de política. No elegir documentos por nombre/ruta/similitud.
Cambiar cualquier parte de ese ámbito exige otra ejecución/raíz y reconciliación
explícita; nunca reinterpretar el cursor ni reescribir el historial anterior.

Tokens de proveedor son cadenas opacas, acotadas y ligadas a ámbito/fase; no se
ordenan numéricamente ni por fecha. Un evento se localiza por respuesta/página e
índice, no por un supuesto ID de evento nativo que no se haya acreditado. La
identidad lógica de observación combina scope/file/document/perfil, metadatos de
revisión, grado/exportación y hash de bytes. Repetirla conserva ocurrencias y una
vista lógica deduplicada; otro contenido o revisión no se pierde por compartir file_id.
No se exige deduplicación física de bytes dentro de los commits.

Límites propuestos del laboratorio: 16 eventos por página, 32 MiB por objeto JSON
canónico completo, 1.024 commits alcanzables por ejecución y tokens de hasta 256
caracteres. Mantener límites I1/I24 de fuente (2 MiB, líneas/objetos) sin truncar.
Exceder límites de página/historia o no poder validar el envelope bloquea la página;
no se recortan eventos para fabricar progreso. Estos límites no describen cuotas
o máximos del servicio Google.

## Máquina de estados

| Fase | Cursor/entrada esperada | Transición confirmada |
|---|---|---|
| INIT | Scope explícito y ancla de feed obtenida del doble **antes** del inventario | Génesis v0 fija ancla y fase INVENTORY |
| INVENTORY | inventory_token, null solo para primera página; cada respuesta tiene next_page_token o fin | Página siguiente o CATCHUP desde el ancla original; sin elegir referencia D5 |
| CATCHUP | Token de cambios anclado; next_page_token continúa el lote | Al fin, new_start_page_token establece FOLLOWING |
| FOLLOWING | Token confirmado para cambios futuros | Continuar páginas o confirmar el nuevo token terminal para la próxima consulta |
| BLOCKED | Error de protocolo, ámbito, corrupción o presupuesto sin resolver | Sin avance automático, reset o adopción de archivos huérfanos |

El cuerpo de página normalizado de fixture se propone cerrado/versionado:
schema, scope_sha256, phase, request_token, events, next_page_token y
new_start_page_token. Inventario no utiliza new_start_page_token. Feed exige
exactamente continuación o token terminal. Página vacía es válida cuando su
protocolo es válido. Token terminal igual al consultado puede representar un poll
vacío; no autoriza bucle ilimitado: cada invocación es acotada y no hay daemon.
Continuaciones que se repiten o forman ciclo bloquean antes de confirmar.

Obtener el ancla primero, enumerar y después reproducir el feed permite volver a
observar cambios durante inventario. No demuestra snapshot global consistente,
revisiones intermedias completas o atomicidad de Google Docs exportado. El doble
simula casos acotados; la propiedad no se extrapola a un proveedor real.

## Resultado de cada evento y confirmación de página

| Resultado | Qué se conserva | ¿Permite confirmar la página? |
|---|---|---|
| CAPTURED | Bytes exactos/base64/hash, metadatos antes/después, perfil/exportación/grado y localizador | Sí, después de completar todos los eventos |
| CAPTURED_BLOCKED | Bytes acotados y diagnóstico de parser/perfil/encoding, sin candidata elegible | Sí; guardar no equivale a revisar/seleccionar |
| TERMINAL_DIAGNOSTIC | Código controlado, file_id/ámbito y metadatos disponibles; sin inventar bytes/revisión capturados | Sí, explícito por A62 |
| TRANSIENT_OR_UNCERTAIN | Timeout, rate limit, cambio durante captura o resultado no concluyente | No: toda la página conserva su cursor previo |
| INVALID_PAGE_OR_SCOPE | Página incoherente, campo/tipo desconocido, token/ámbito incorrecto, error global de autorización | No: bloquear, no convertir en un diagnóstico terminal por archivo |

Registro terminal acotado: OUTSIDE_ALLOWLIST, UNSUPPORTED_MIME, REMOVED_OR_ACCESS_LOST,
UNAVAILABLE_CONFIRMED y SOURCE_SIZE_LIMIT. Cada código exige la condición prevista
en la fixture/validador; un booleano arbitrario del llamante no puede declarar
terminal un timeout o error global. Removal/404/acceso perdido no prueban borrado
real y no escriben D2. Un cambio de drive que invalida el ámbito bloquea el conector;
un evento no-file irrelevante puede conservar NON_FILE_CHANGE sin inventar documento.

Diagnósticos terminales no excluyen un archivo para siempre: una observación
posterior recuperable conserva otra ocurrencia/captura. Un conjunto de bytes
ambiguo puede capturarse bloqueado; una fuente cambiante es transitoria y no se
etiqueta definitiva para saltarla. Todo fallo transitorio descarta la preparación
completa de esa página: no hay prefijo de eventos aplicado o cursor adelantado.

Mantener la distinción blob/exportación y OBSERVED_EXPORT de I23/I24. Comprobación
de metadatos antes/después no eleva esa procedencia a revisión inmutable. Ni
capturar ni confirmar una página llama a review, SELECT_REFERENCE o apply_effect.

## Persistencia desechable propuesta

La raíz contiene owner.json, scope.json, un lock propio, objects/<sha256>.json y
head.json. No aceptar rutas de archivo procedentes de eventos ni nombres libres.
Crear directorios/archivos privados, rechazar symlinks/hardlinks y validar ancestros,
marca/run_id y tipos de objeto antes de abrir. No es almacenamiento cifrado ni
protección contra un dueño hostil: solo se autorizan fixtures sin secretos.

Cada objeto de commit incluye schema, run/scope, versión, parent_commit_sha256,
command_id/request_hash, cursores antes/después, fase y todos los resultados de la
página con sus bytes/diagnósticos y recibo. Génesis fija el ancla. head.json solo
señala el commit autorizado/versionado; el cursor efectivo vive dentro de ese
commit y se recupera recorriendo esa cadena, nunca desde un checkpoint independiente.

Protocolo propuesto de confirmación:

1. Preparar/validar la página y capturas de fixture fuera del lock, sin avanzar estado.
2. Tomar flock exclusivo de la raíz; revalidar marca, scope, head esperado y cadena.
   Si el command_id ya existe alcanzable con el mismo request_hash, devolver su
   recibo histórico antes de exigir una cabeza nueva; con otro hash, conflicto.
3. Comprobar CAS de versión/hash de cabeza, fase y token consultado; revalidar la
   página completa y todos sus resultados. Contendientes con la misma versión
   no pueden confirmar ambos. Un conflicto no vuelve a preparar silenciosamente.
4. Escribir un objeto inmutable completo en un temporal propio, fsync del archivo,
   publicarlo bajo su hash sin reemplazar y fsync de objects/. Ningún objeto a
   medio escribir se presenta como commit válido.
5. Preparar head temporal completo, fsync, reemplazar atómicamente head.json y
   fsync de la raíz. Solo después devolver el recibo confirmado. Bytes, diagnóstico,
   recibo y cursor pertenecen así al mismo commit alcanzable.

El lock no sale de la raíz ni se comparte con dev/D4. No hay llamadas de proveedor,
SQL o red dentro/fuera del lock. Lectores toman lock compatible y validan el mismo
head/cadena, sin aceptar JSON truncado como resultado parcial.

## Caída, respuesta perdida y corrupción

| Punto de fallo | Recuperación exigida |
|---|---|
| Antes de publicar objeto | Head previo; temporal no es evidencia y ningún evento se considera confirmado |
| Objeto durable, antes de head | Objeto huérfano no autorizado; no se elige por fecha o número mayor |
| Durante reemplazo de head | Abrir head completo anterior o nuevo y verificar la cadena; no mezclar cursores |
| Después de confirmar head, antes de respuesta | Recuperar comando/recibo por ID+hash; retry exacto no duplica commit ni regresa cursor |
| Error de fsync/resultado incierto tras reemplazo | UNKNOWN_COMMIT; inspeccionar la cadena antes de retry, sin presumir rollback o éxito |
| Head/objeto/parent/scope/bytes inconsistente o ausente | CORRUPT_OR_INCOMPATIBLE, sin avance, reparación automática o promoción de huérfanos |

Un retry no puede utilizar el mismo command_id con respuesta/página distinta si ya
existe un recibo confirmado. La identidad de request incluye página normalizada,
scope, pins de cabeza y hashes de capturas; los tokens no autorizan contenido nuevo
por sí solos. Recuperar un recibo antiguo nunca cambia la cabeza actual.

La validación propuesta mata/reinicia procesos del harness sobre la misma carpeta
propia y prueba límites de commit con fallos inyectados. No promete resistencia a
pérdida de energía, fallo de disco, NFS/Windows o restauración hostil de todo el
filesystem. Una copia antigua válida sin pin externo no aporta detección universal
de rollback. No se afirma autenticación o firma criptográfica del proveedor.

## Harness, limpieza y siguiente autorización

El harness crea una raíz con tempfile, conserva su identidad fuera de los procesos
hijos y la comparte solo para las pruebas de reinicio. Antes de limpiar termina
y espera a sus propios procesos hijos; no acepta PIDs o señales desde eventos ni
actúa sobre workers reales. Un finally elimina exclusivamente esa raíz creada por
él, validando propiedad y sin seguir enlaces
hacia fuera. No borra paths suministrados por eventos ni ejecuta prune/reset global.
Raíz ajena, marca equivocada o identidad incompatible se rechazan; los sentinels
externos de las pruebas deben sobrevivir: se crean como fixtures hermanas, sin
inspeccionar entornos reales. No leer run_data, dev, D4 o corpus privado.

El contrato propone implementar después un adaptador de fixtures y almacén nuevo,
con pruebas de páginas/reinicio/corrupción y evidencia propia DI01–DI28. Usar fsync,
rename/flock y procesos locales del harness amplía deliberadamente I24, que era
solo memoria: requiere aprobar este contrato y autorizar ese corte antes de código.
No habrá Google/HTTP, credenciales, Docker, SQL, cambios de parser, aplicación D2,
selección automática de referencia o activación.

Los cuatro criterios serán **sintéticos** incluso si pasan DI01–DI28. GI12 y la
validación integrada real siguen pendientes, igual que las demás brechas G01–G07.
No se adjudican los criterios generales GI38/GI39/GI40 como completos por probar
solo esta frontera de captura y limpieza.

## Referencias primarias consultadas el 2026-10-22

- [Drive: retrieve changes](https://developers.google.com/workspace/drive/api/guides/manage-changes): el feed usa ancla y páginas del estado disponible, no un historial completo de snapshots.
- [Drive: changes.list](https://developers.google.com/workspace/drive/api/reference/rest/v3/changes/list): distingue nextPageToken y newStartPageToken al final. La referencia indica que esos tokens no expiran; no se inventa una política de expiración por tiempo en este laboratorio. Rechazo o ámbito incompatible se mantienen como errores explícitos.
- [Drive: Change](https://developers.google.com/workspace/drive/api/reference/rest/v3/changes): removed puede ser borrado o pérdida de acceso; hay cambios de file o drive. El envelope de fixture no se presenta como copia exacta de ese JSON ni como prueba de su semántica real.
