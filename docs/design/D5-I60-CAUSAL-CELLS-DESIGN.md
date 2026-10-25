# D5 I60 — contrato de evidencia causal de las 39 celdas calificadas

Fecha: **2026-10-25**, Europe/Madrid. **PREPARED_FOR_REVIEW**. Base I59 `47f4cb2050dce6d871abf430c63b25543a83d43b`.
[Matriz CE01–CE43](D5-I60-CAUSAL-CELLS-REVIEW.md) · [Sellos y trazabilidad](../validation/D5-I60-design-review.json) · [Integridad](../validation/D5-I60-integrity.json) · [Dictamen I59](../validation/D5-I59-results.md).

## Autoridad y objetivo

La selección A posterior a I59 autoriza diseñar evidencia causal para las **15 celdas T con metadata histórica y 24 puntos/modos REMOTE T/R sin etiqueta**. I60 prepara contrato y matriz; no implementa ni ejecuta campañas, auditor, SQL o push. El posible siguiente incremento I61 requiere aprobación de este alcance concreto.

Se propone un harness nuevo CE43, **39 casos de dominio con un SIGKILL objetivo cada uno y cuatro controles**. Se preservan las otras 101 celdas I59 con soporte acotado y todos los documentos/raws históricos: no se reconstruye stdout I34/I36, no se modifica su clasificación histórica ni se adjudica mode desde el orden del bucle. El nuevo raw acreditaría sus propias secuencias si se autoriza y valida. Ningún PASS convierte automáticamente UI22.2 o GI38 en completos.

## Partición y precondiciones

| Familia | Celdas | Preparación pública previa a armar el hook |
|---|---|---|
| T APPLY FL07 | 3, antes de HEAD | I26 importado, SOURCE/EVALUATION/EFFECT ACCEPT; ninguna TASK aplicada, mapping/base/procedencia; sin binding/PROJECTION/send |
| T ISSUE FL11 | 4 | TASK aplicada, BIND y primera PROJECTION CREATE ACCEPT; ningún send/ticket/QUERY/RESULT; REMOTE vacío |
| T QUERY FL15 | 4 | ISSUE durable con un ticket, ejecución CREATE confirmada en REMOTE; CLIENT UNKNOWN/ledger1/queries0, pending send, ningún QUERY o RESULT |
| T RESULT_DISPATCH FL16 | 4 | Igual que QUERY, pero el comando objetivo RESULT tiene query_id=None y P obtenida por el hijo; ninguna QUERY anterior |
| T/R EXECUTE CREATE FL12/FL30 | 8 | PROJECTION CREATE ACCEPT e ISSUE durable; ticket objetivo sin efecto/recibo REMOTE, CLIENT UNKNOWN/1/0 |
| T/R EXECUTE UPDATE FL13/FL31 | 8 | CREATE previo confirmado v1; Remote.edit(foreign=sentinel) público produce v2; misma identidad y payload previo. Preparar/revisar por API una PROJECTION UPDATE con remote_base exacta y nuevo ISSUE/ticket; CLIENT UNKNOWN/1/0 para ese send |
| T/R CLOSE FL14/FL32 | 8 | PROJECTION CREATE ACCEPT e ISSUE durable sin efecto; llamada Remote.execute(close=True), que publica operación CLOSE y tombstone sin entidad |

R parte de SOURCE/BATCH y TASK participante del recibo APPLY_BATCH exacto (cid/request), selección y generaciones propias; no se convierte a I32. T conserva perfil y pin/bytes/grado de captura I26. La preparación UPDATE registra separado el CREATE previo v1 y la edición pública de foreign a v2, sus recibos y el send/ticket CREATE. T usa EDIT_TASK público para cambiar el título; R captura/revisa/prepara/aplica un segundo SOURCE/BATCH con título distinto y vuelve a seleccionar la misma TASK por el nuevo recibo exacto, conservando el binding. Se prepara/revisa UPDATE sólo tras esos pasos, con remote_base v2 exacta y payload distinto. No se suma ese efecto previo como efecto objetivo ni se exige cero tickets globales en UPDATE. El payload UPDATE debe cambiar realmente respecto a v1 usando APIs públicas; si esa preparación no fuese posible, detener y explicar el límite, sin editar Store, estados o fixtures.

## Identidad y gate causal

Un caso usa raíz propia y spawn nuevo. El hijo lee el manifiesto y send/intento emitidos desde CLIENT durable; no acepta P del padre como autoridad. Para RESULT_DISPATCH obtiene P mediante Remote.lookup y arma el hook sólo después de ese lookup, antes de perform(RESULT). Para REMOTE usa execute(ticket,M,close=...) público con remote_hook; no realiza un transact sustituto ni cambia reducer/hook.

READY registra case/path/run_id/client_store_id/remote_store_id/role, operación Store real, operación del manifiesto, modo observado, stage, punto, cid, args_sha256, request_sha256 y expected. CLIENT usa expected HEAD exacto; REMOTE usa expected=None. Para REMOTE, cid es el UUIDv5 público derivado de store_id, operación EXECUTE/CLOSE, ticket y digest(M); request_sha256 se calcula sobre kind/args/expected incluyendo reject=None y retry_tick=0. El gate y el commit alcanzable, cuando existe, deben coincidir en esa identidad y hash.

Guardar además manifest_id/hash, creation_key, binding/target, send_id, ticket, query_id (None donde procede), ledger, capacidades y hash de remote_base. Mode se deriva en el hijo de close y m.operation, se contrasta con la fila esperada y vuelve a comprobarse en el objeto/recibo alcanzable. **CLOSE: mode=CLOSE, Store kind=CLOSE, manifest.operation=CREATE**; UPDATE: kind=EXECUTE, manifest.operation=UPDATE. No basta copiar la etiqueta enviada por el padre. Antes de HEAD, cuando no hay commit objetivo alcanzable, se conserva READY, hashes de los argumentos reales y precondición, sin fingir un recibo publicado.

Un único READY válido habilita al padre a matar y exigir exitcode=-9. El lector de archivos durante el gate no adquiere el lock del Store retenido por el hijo. Falta de READY, EOF, DONE normal, identidad/modo/hash/rol/punto erróneo o timeout falla el caso; no se interpreta como recuperación exitosa. El hook sólo se arma para la operación objetivo, tras toda preparación.

## HEAD, reapertura y continuación

before_object, after_object y before_replace conservan HEAD, estado alcanzable y recibos previos de la autoridad objetivo. Objetos huérfanos o temporales se registran físicamente, pero no se adoptan. after_head ocurre tras fsync del directorio y antes de devolver el resultado; exige exactamente un commit y recibo objetivo alcanzables, no una nueva prueba de pérdida de energía.

Registrar oráculos independientes antes, gate, después de SIGKILL, antes/después de lecturas pasivas y después de continuación. Incluir cadena/hash/HEAD/recibo/request/estado, entidades y versiones, keys/tickets/foreign, reviews/generaciones, selección/BATCH y send/ledger/queries/pending. Comparar sólo cambios permitidos por la operación y el recibo. Para un crash CLIENT, REMOTE completo no cambia durante caída/reapertura; para uno REMOTE, CLIENT completo conserva UNKNOWN/1/0 y el mismo intento hasta la reconcile explícita.

Antes de continuar, dos observadores spawn separados: lector de archivos independiente y APIs públicas de CLIENT y REMOTE (snapshot/summary/read_command del Store objetivo). Ambos deben concordar con HEAD/cadena/estado alcanzable. Envolver transporte y exigir **execute=lookup=0** durante reapertura pasiva; obtener P para preparar o continuar es una acción explícita distinta. Una segunda pareja de lecturas confirma el estado final sin nuevos efectos.

APPLY: replay expreso del mismo cid/args/expected confirma una vez, materializa TASK/mapping/base/procedencia y no enlaza ni envía. ISSUE: replay expreso confirma una única emisión UNKNOWN/1/0; el replay histórico no llama transporte. Tras comprobar CLOCK+replay sin rebobinar, reconcile(close=True) explícita cierra el ticket sin entidad y termina CLOSED_NO_EFFECT/2/1.

QUERY: replay expreso publica el qid original una vez o devuelve recibo histórico. Tras CLOCK+replay estable, un hijo obtiene P por lookup y publica RESULT con ese mismo qid: EFFECT_CONFIRMED/2/1 y pending vacío, execute=0. RESULT_DISPATCH: antes de HEAD, nueva reconcile explícita concluye /2/1 y deja ausente el cid RESULT interrumpido; después de HEAD, /2/0 y recibo histórico exacto, incluso tras CLOCK; replay obtiene P mediante lookup explícito sin duplicar observación. No se confunde con RESULT_QUERY I58 ni con before_result lógico.

REMOTE antes de HEAD: ticket objetivo y recibo ausentes, estado remoto previo intacto. La continuación autorizada del ensayo es reconcile(close=True) sobre el ticket ya emitido: no reintenta EXECUTE y publica tombstone, QUERY+RESULT, CLOSED_NO_EFFECT/ledger2/queries1. En UPDATE conserva entidad v2, foreign sentinel y efecto CREATE previo. Después de HEAD: CREATE una entidad v1, UPDATE la misma entidad v3 desde remote_base v2, con payload exacto/foreign intacto, CLOSE ninguna entidad y tombstone; CLIENT sigue UNKNOWN hasta reconcile(close=False), que sólo lookup y termina con P exacta en /2/1.

La idempotencia remota se verifica por read_command y llamada explícita con el mismo ticket/M/close. Después de HEAD, recibo exacto histórico y HEAD completo inmutable. Antes de HEAD, tras cerrar, una llamada EXECUTE original puede añadir un recibo EXECUTE diferente que devuelve el tombstone ya existente; esto no es replay histórico del CLOSE ni nuevo efecto, y se registra separado. Para el modo CLOSE la continuación ya publica el mismo cid original; su repetición sí debe ser histórica. Nunca sustituir CLOSE por EXECUTE al afirmar replay exacto. Si se añade CLOCK CLIENT, verificar que reproducir recibos CLIENT no rebobina su HEAD; CLOCK no prueba idempotencia del Store REMOTE.

## Controles y ejecución propuesta

CE40/41: controles T/R de protocolo/propiedad (gate mal correlacionado en cada campo, EOF, salida normal, timeout; inode/owner/sentinel/symlink restaurados antes de limpiar). Un kill de timeout negativo no cuenta como SIGKILL positivo. CE42/43: inventario/raw T/R (entrada cambiada/añadida, raw ausente/hash/JSON duplicado/NaN, IDs duplicados o ausentes, skip, recursos y presupuestos). Cuatro controles no añaden celdas.

El futuro I61 sólo crearía testing/causal_frontier_cells/{support.py,test_causal_frontier_cells.py,run_causal_cells_lab.py,README.md}, su documento de laboratorio, raw/results propios y **ocho** pares raw/contexto de regresión separados: Python321, HC24, HF40, IC30, UQ24, RV20, NA36 y FN64. Los helpers/runners/tests históricos, producto, Store, schemas y fixtures siguen intactos. Su reutilización debe quedar pinneada; no se mezclan RECORDS o hijos de campañas distintas.

Cada regresión conserva su inventario efectivo aunque no descubra el directorio nuevo; el runner CE incluye todos sus módulos/reutilizados, producto, contrato/matriz/sello I60 y dependencias anteriores con hashes pre/post exactos. No incluir results/raw generados en su propio inventario circular. Raw CE: mapa unívoco CE/celda/método/ancla/escenario/eventos/oráculos, stdout realmente capturado, exitcode/stderr/argv/plataforma y recursos. CE43 PASS no se deduce de tests_run sin mapa completo, ni se suma a regresiones como pruebas nuevas.

Límites propuestos: 4 hijos vivos, 20s por espera, 120s por caso, 900s campaña, 256 eventos por escenario, 16KiB/evento y 12MiB raw propio; cada regresión mantiene su presupuesto histórico. Limpieza sólo de raíces propias, cero hijos/hilos/raíces pendientes; no cambiar límites kernel ni inspeccionar/limpiar dev/run_data/D4. Si el raw excede un presupuesto, fallar y presentar cambio de contrato; no truncar ni aumentar silenciosamente.

## Aceptación y límites

Tras autorización, I61 debe entregar 39 secuencias positivas inequívocas y cuatro controles, ocho regresiones separadas, sellos estables y validación documental independiente. Los deltas quedarían TEST_PASS_PENDING_SUFFICIENCY_REVIEW; sólo una revisión posterior podría reevaluar UI22.2 dentro del perímetro explícito. Ni siquiera 140 celdas acreditadas cerrarían automáticamente GI38 o D5 global.

No se añade OSError directory_fsync/recovery_fsync ni se traslada la evidencia antigua a primeras ACCEPT/BIND/RESULT_QUERY. Sin casos nativos nuevos: UI20.3 CREATE NATIVE_T/NATIVE_R y NA29–NA32 F7 conservan su alcance, otras fases CORE NOT_ASSESSED sin producto cartesiano obligatorio nuevo. Sin carreras auxiliares ni host/energía/NFS/Windows. El auditor/registro fijo I38 permanece intacto y no se ejecuta. Histórico 30/35 sin promoción.

D1–D4 cerrados; D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intacto. UI22.2 PARTIAL, agregado I56/I59 77/7, H07 y D5 global/G01–G07/GI33/GI34/GI38/GI39/GI40 abiertos, closure=false. GI06/GI12/GI18/GI24/GI30/GI36/GI42 reales/humanos pendientes de sus puertas propias, sin traslado a D6. P0 vigente: sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue ni D6. Publicado sólo hasta I52; I53–I60 locales, sin push ni nueva lectura de red.
