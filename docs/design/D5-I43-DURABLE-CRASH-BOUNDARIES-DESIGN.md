# D5 I43 — contrato de fronteras de fallo H02 en T/R

Fecha: **2026-10-24**, Europe/Madrid. **PREPARED_FOR_REVIEW**.
Base: `98df91a05a43313e26c47dc8d80fd3c2f16018d5`.
[Selección A](D5-I43-NEXT-CUT-SCOPE.md) ·
[Matriz HF01–HF40](D5-I43-DURABLE-CRASH-BOUNDARIES-REVIEW.md) ·
[Sello](../validation/D5-I43-design-review.json).

La selección A autoriza preparar este contrato/matriz, no implementar o ejecutar.
Se propone I44 como harness y evidencia nuevos, manteniendo producto, suites y
runners históricos, I42 y registro fijo I38 intactos. Si falta un hook o aparece
un defecto de producto, documentar el impedimento y volver al alcance; no añadir
hooks ni corregir producto bajo esta propuesta.

## Objetivo y exclusiones

Atender las tres lagunas concretas H02 de I40: SIGKILL después del efecto local y
antes de binding/proyección; fronteras de fases R anteriores a APPLY_BATCH;
y pérdida de la prueba antes de RESULT partiendo realmente de UNKNOWN.
Objetivos parciales GI38/UI15–UI19/UI21–UI23/UI25 según recorrido; GI33/GI34/GI40 para
inventario, regresiones y recursos. Cada fila indica aplicabilidad parcial; no
acredita automáticamente una UI entera, recuperación integrada global o cierre H02.

P0 vigente: I32, handoff y posteriores no publicables sin decisión separada.
D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. D5 global,
G01–G07 y revisión global de los cinco GI abiertos. Sin promover 30/35→35/35.
Sin proveedores/credenciales reales, corpus privado, consumo/reservas, operaciones,
activación, promoción, despliegue o D6; sin inspección/limpieza de dev/run_data/D4.

Fuera: cambios de kernel/modelo/almacenamiento, ausencia de disco/energía,
NFS/Windows/caller hostil, inicialización corrupta/genesis, todas las combinaciones
imaginables de fase/modo/revisión, carreras H03 restantes y colección múltiple/429
ambiguo H07. Los límites de raw histórico H04/contexto H05 siguen declarados.
No se reconstruye raw I34/I36 ni se reescriben I40/I42.

## Archivos y APIs

Archivos nuevos previstos en `testing/durable_crash_boundaries/`: `support.py`,
`test_durable_crash_boundaries.py`, `run_crash_boundaries_lab.py` y README;
documentos y resultados I44 nuevos. Fuera de discovery `testing/D5` y
`testing/durable_concurrency`; no actualizar el registro I38 por implicación.

Labs nuevos T/R, setup público de `testing/D5/durable_support.py` y
`relational_support.py`. Puede reutilizarse sin modificar el lector de archivos
`testing/durable_concurrency/support.py:independent`, cuyas comprobaciones explícitas
no dependen de assert. El control de procesos/crashes será nuevo: no reutilizar
un helper que detenga la operación equivocada o registre fases genéricas sin modo.

Solo `Client.perform`, `Store.read_command`, snapshot/summary, dispatch/reconcile,
Remote.execute/lookup y hooks públicos existentes. No `_head`, `_candidate`,
pickle, restauración de autoridad en memoria, escritura de HEAD/objetos de estado,
reparación, rebase, GC o promoción de objetos huérfanos desde el harness.
Las escrituras de archivos auxiliares de control/ownership son propias del lab;
no alteran datos de negocio para simular una transición.

## Fronteras disponibles y significado exacto

| Hook existente | Lugar | Hecho al detenerse | Oráculo permitido |
|---|---|---|---|
| before_object | Store._publish bajo lock | Transición calculada, antes de escribir objeto | HEAD/estado/recibos anteriores |
| after_object | Objeto enlazado y directorio objects fsync | Objeto nuevo posible, HEAD anterior | No promover objeto no alcanzable |
| before_replace | Temporal de HEAD escrito/fsync, antes de rename | HEAD anterior; temporal posible | No adoptar temporal como commit |
| directory_fsync | Después de reemplazar HEAD y antes del fsync del directorio | HEAD puede ser visible; confirmación no retornada | OSError controlado → COMMIT_UNKNOWN, no prueba de energía |
| after_head | Después del fsync del directorio | Commit/recibo alcanzables, aún dentro de transact | SIGKILL antes de devolver recibo |
| recovery_fsync | Store._load tras validar cadena | Recuperación debe fsync objetos y raíz | OSError controlado → COMMIT_UNKNOWN |
| after_remote | dispatch tras execute y antes de RESULT | ISSUE durable; efecto remoto confirmado; CLIENT UNKNOWN | Prueba local del proceso se pierde al matar |
| after_query | reconcile tras QUERY y antes de lookup | QUERY durable, todavía no se observó P | No llamarlo pérdida de respuesta ya recibida |
| before_result | reconcile tras lookup y antes de RESULT | P observada, solo retenida en proceso | Exigir P real y CLIENT todavía UNKNOWN |

No existe hook dedicado «after_apply_before_bind». Para ese hueco se usará
**after_head del comando APPLY/APPLY_BATCH concreto**, filtrado por operación y
activado después del setup. Mata antes de que perform retorne; BIND/SELECT_TASKS/
PREPARE_PROJECTION no se han invocado. No afirmar que se mató dentro de BIND ni
inventar un indicador durable de fase pendiente que el modelo no almacena.

`directory_fsync`/`recovery_fsync` serán fallas OSError sintéticas, no SIGKILL y
no fallos físicos reales. Se registran aparte. No se ensaya el hueco de energía
entre rename y fsync ni se deduce durabilidad física a partir de HEAD visible.

## Identidad del comando y protocolo de proceso

Por escenario: lab/raíz propios, recorrido, run/store IDs, actor/rol, comando UUID,
operación, modo, stage de revisión, args/expected/request hashes, versiones y punto.
Para perform, el padre fija `cid`, argumentos y expected HEAD antes del hijo. Request hash debe
ser digest canónico de `{kind,args,expected}`. Capturar esos datos no concede
aprobaciones ni permite sustituirlas: las revisiones proceden de comandos públicos.
En dispatch/reconcile, los cid/ticket/query_id generados por las fachadas se
observan en recibos/pendientes al gate; no se sustituyen para controlar el test.
Dispatch permite fijar send_id, no ticket/cid internos. Read_command puede
consultar esos comandos observados por su request hash exacto; no repetir dispatch
como si fuera replay del ISSUE antiguo, porque crearía un ticket nuevo.

Linux local, spawn y Pipe/Event; reloj lógico no avanza por esperar/reabrir. El hijo
abre el CLIENT/REMOTE correspondiente desde disco, ejecuta la operación pública
y emite READY únicamente en el hook objetivo tras el setup. El padre comprueba
operación/rol/modo/punto e identidad, registra HEAD/estado y envía SIGKILL solo a
ese hijo. Exigir join y exitcode=-SIGKILL; timeout/EOF/salida normal o gate equivocado
son FAIL/NOT_RUN, nunca cobertura de caída. No sleeps/azar como prueba de frontera.

Para before_result, wrapper de observación de lookup delega a Remote.lookup real,
retorna P sin alteración y publica solo su hash/IDs. La señal del gate debe acreditar
que el hash observado coincide con el ticket durable. No fabricar P en proof_hook
ni devolver una prueba desde un pickle/objeto de autoridad del padre.

Tras la caída: (1) lector independiente de archivos en proceso nuevo; (2) apertura
pública en otro proceso nuevo para snapshot/read_command/summary pasivos;
(3) solo después, comandos explícitos de continuación/conciliación. Separar rondas.
La reapertura puede fsync los directorios por diseño; no QUERY, RESULT, ISSUE,
EXECUTE, revisión, incremento lógico de versión o replay implícito. Comparar HEAD,
estado/recibos, ledger/queries y REMOTE antes/después de la lectura pasiva.

Guardar huérfanos/temporales como observación física sin tratarlos como autoridad.
La igualdad exigida antes de commit es de HEAD y estado alcanzable; no de todo el
árbol físico. No limpiar huérfanos entre caída y oráculos. Limpieza final solo del
lab propio tras registrar evidencia.

## E — estados tempranos R

Fuente JSON sintética con un TASK y referencias válidas; misma identidad/bytes y
targets predefinidos por escenario, sin captura I26 o EVALUATION Markdown ficticias.
Precondiciones mínimas y transición esperada:

| Operación/stage | Estado inicial | Único cambio autorizado si confirma |
|---|---|---|
| CAPTURE | Genesis R, sin fuentes | source_id=SHA256 de bytes exactos; sources 0→1; selección nula |
| SELECT_SOURCE | Fuente capturada, sin seleccionar | source_id elegido y source_generation 0→1 |
| PREPARE_SOURCE | Fuente seleccionada | Manifiesto SOURCE hash/contexto exactos; sin revisión implícita |
| REVIEW SOURCE ACCEPT | Manifiesto SOURCE sin revisión | Review SOURCE versión 0→1 ACCEPT; sin manifiesto BATCH |
| PREPARE_BATCH | SOURCE aceptada v1; data vacía/generation 0 | Manifiesto BATCH con plan/after exactos; data sigue vacía, no efecto |
| REVIEW BATCH ACCEPT | Manifiesto BATCH sin revisión | Review BATCH versión 0→1 ACCEPT; no APPLY_BATCH |

HF01–HF24 prueban cada operación en cuatro puntos (before_object, after_object,
before_replace, after_head), cada combinación en lab nuevo. Los tres primeros
conservan HEAD/state anteriores y no tienen recibo del cid; after_head conserva
exactamente un nuevo commit/recibo con la transición específica de tabla. En
todos: data/selection TASK/bindings/proyección/sends/REMOTE siguen sin efecto.

Para cid no confirmado, Store.read_command con request hash exacto devuelve
NOT_COMMITTED_AT_HEAD y grants_execution_authority=False; para confirmado devuelve
el recibo histórico exacto. Luego replay **explícito** del mismo comando/args/cid/
expected: si confirmó, historical=True sin cambiar HEAD/estado; si no, confirma
una vez desde el estado anterior. No regenerar cid o expected para disimular retry.
Comprobar source/review/generation/manifest/receipts exactos sin duplicación.

HF25–HF30 repiten las seis operaciones con OSError en directory_fsync: el objeto
CLIENT usado queda poisoned (RECOVERY_REQUIRED en snapshot). Un CLIENT nuevo con
fault en recovery_fsync falla COMMIT_UNKNOWN. Apertura nueva sin fault termina
la validación/fsync y observa el commit/recibo visible de ese proceso local; replay
explícito conserva el recibo y no duplica nada. No contabilizar estas filas como
crashes ni elevarlas a garantía tras pérdida de energía.

## G — hueco efecto local → binding/proyección

HF31 T parte de `ready(apply=False, projection=False)` y mata APPLY en after_head.
Exigir un TASK, mapping/base/provenance exactos y data_generation +1, recibo APPLY
alcanzable, sin binding, manifiesto PROJECTION, send/ticket o efecto REMOTE.
HF32 R parte del batch aceptado sin aplicar/seleccionar/proyectar y mata
APPLY_BATCH en after_head. Exigir lote entero (entidades/relaciones/provenances),
data_generation +1 y recibo exacto, pero selection nula, bindings/proyección/sends
vacíos y REMOTE intacto. No confundir `manifest.after` previo con `data` aplicada.

Apertura pasiva no fabrica fases o proyecciones. Read_command/replay explícito del
APPLY confirma historia sin segunda aplicación/generation. Solo después T ejecuta
BIND, PREPARE_PROJECTION y REVIEW; R ejecuta SELECT_TASKS desde cid/request/recibo
APPLY_BATCH exactos, después BIND/PREPARE_PROJECTION/REVIEW para el TASK derivado.
Final: efecto local una vez y proyección revisada; cero ISSUE/efecto remoto. No
atribuir al recibo histórico autorización para ejecutar esos pasos automáticamente.

## U — prueba perdida desde UNKNOWN

Solo modo CREATE de un TASK, un send/ticket emitido, ledger 1, proof=None en CLIENT,
sin conciliación anterior. Configuración/identidad/revisión propias de T y R.

HF33/HF34 matan dispatch en after_remote: el hijo emitió ISSUE y Remote.execute
confirmó exactamente P; antes de matar CLIENT debe seguir UNKNOWN, queries=0,
pendiente send y un efecto REMOTE. No usar deliver=False como sustituto de esa
llamada pública dispatch en este par.

HF35/HF36 preparan ISSUE sin entrega y ejecutan explícitamente el ticket una vez
en REMOTE para crear P; CLIENT sigue UNKNOWN. Matan la **primera** reconcile en
before_result tras observar P. HF37/HF38 usan el mismo estado inicial en labs
separados, pero matan en after_query, antes de lookup. En ambos pares: ledger 1,
UNKNOWN, queries=1, pendientes send+query exactos, sin recibo RESULT. Distinguir
prueba observada y todavía no observada en los metadatos.

Para las seis filas, apertura pasiva conserva ese estado. Solo después, reconcile
nuevo explícito QUERY/RESULT confirma P exacta, ledger 2 y elimina pendientes de
ese send, incluidos queries abandonados. Queries finales: 1 en HF33/34 y 2 en
HF35–38. Igual ticket/creation_key/remote_id/version/payload hash y HEAD REMOTE
antes/después; un efecto y ninguna ejecución o cierre remoto durante reconcile.
No se prueba UPDATE/CLOSE aquí; no transferir cobertura CREATE a otros modos.

La novedad se declara por obligación, no por número de caídas: DF20/DR26 ya
incluyen after_remote; DF21 ya ensaya before_result desde UNKNOWN en T. HF33–35
son controles/repeticiones con evidencia propia y etiquetas reforzadas; HF36
exige en R el estado inicial que no acredita la segunda caída de DR26. Los
APPLY/APPLY_BATCH after_head tampoco son un hook nuevo: HF31/32 amplían el
oráculo del hueco y su continuación explícita. El informe futuro separará
frontera ya probada, nuevo estado/oráculo y pendiente, sin vender cada fila
como una laguna histórica inédita.

## Evidencia, recursos y aceptación futura

Nueva campaña con stdout raw anclado, pre/post hashes y descubrimiento completo de
inputs pertinentes (fuentes, setup, lector I42, harness, fixtures y contratos).
Registrar Python/build/plataforma/optimize/__debug__, exigir optimize=0; lector
con comprobaciones explícitas. Cada evento/oráculo: caso/path/actor/rol/operación/
modo/stage/punto/orden/ronda, cid/request/HEAD/proof hashes y versiones, conteos
alcanzables y físicos diferenciados. Salida sin payload íntegro/paths temporales/
credenciales/errores privados. Desarrollo fallido no se oculta ni cuenta como PASS.

Un lab/escenario, un hijo mutador y lectores/followup posteriores; máximo cuatro
hijos vivos/caso; 20 s/espera, 120 s/caso, 900 s/campaña propia, 256 eventos/caso,
16 KiB/evento, 8 MiB/raw. No ampliar límites kernel/T/R ni crear reservas D3.
Negativas reducidas de gate/timeout son fallos de control, no recuperación exitosa.
Ownership/inodos/marker/sentinels, rechazo de enlaces y limpieza solo propios;
cero hijos/hilos/raíces propios restantes en éxito. Un rechazo de ownership impide
borrar, registra residuo y hace fallar la campaña. No inspección del estado operativo.

Propuesta de aprobación posterior: implementar/validar HF01–HF40 con evidencia
propia; ejecutar por separado las 24 HC de I42 mediante su runner sin modificar
y las 321 regresiones Python mediante runner histórico intacto. Tres campañas,
raw/contexto/pre/post por separado; no reemplazar raws originales. HF son filas
previstas, no promesa de 40 tests ni suma automática con 24/321. Validar IDs y
subcasos realmente ejecutados. Sin SQL/Java/Docker o pruebas de proveedor.

Resultados futuros deben mapear HF a tests/operaciones/fronteras/oráculos efectivos,
con FAIL/NOT_RUN explícitos y pendientes del H02 no incluido. No cambiar dictámenes
I40/I42 o cerrar GI38 por suma de PASS. Este diseño no emite resultados empíricos.
