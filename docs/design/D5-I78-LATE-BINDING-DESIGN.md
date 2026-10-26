# D5 I78 — contrato de binding tardío y diagnóstico del worker

Fecha: **2026-10-26**, Europe/Madrid. Base local `6ffff6c17165fb0e1bcde69af4cfade6715432bf`. Estado **PREPARED_FOR_REVIEW**.
[Matriz LB01–LB64](D5-I78-LATE-BINDING-REVIEW.md) · [Selectores, esquema y pins](../validation/D5-I78-design-review.json) · [Integridad](../validation/D5-I78-integrity.json) · [Resultado I77](../validation/D5-I77-results.md) · [Contrato tipado I75](D5-I75-TYPED-ADAPTER-DESIGN.md).

## Autoridad y fases

La selección A posterior a I77 autoriza **sólo diseñar** este contrato y matriz: binding tardío exacto y diagnóstico sanitizado acotado. I78 añade cuatro documentos, sin implementación, nuevo registro ejecutable, imports de producto/runners, discovery, tests ni captura. La verificación de JSON, hashes, AST y enlaces es documental.

I79 propuesto requeriría aprobar este contrato e implementar un perfil separado con **LB64 sólo sintéticos**, bajo 300 segundos externos. No incluiría reejecutar PG64/AT80 ni campañas funcionales. Tras validar I79, una autorización posterior I80 sería necesaria para P01 completo (321 ocurrencias/12 grupos) en destino nuevo. No se autoriza ninguna de esas ejecuciones con I78. Publicación y cierre de criterios permanecen separados.

## Hechos y límites de I77

I77 conserva un intento con worker exit 2, raw y sidecar vacíos, sin páginas; `OWN_GROUP_GONE`, inputs MATCH. El launcher registró INVALID_JSON al leer esos archivos. No retuvo stderr: no hay código/fase interna observada, informe funcional, inventario ni cobertura. Cero ocurrencias reportadas no prueba que runtime ejecutara cero tests.

La fuente muestra `loaded_bindings` antes de `module.main`; el grafo AST local inicial no incluye plane_fixture y el discovery está dentro de main. Exigir PlaneError ya cargada es una explicación probable, **no una confirmación runtime de CLASS_MODULE_NOT_LOADED**. I78 no reconstruye el error ni completa los archivos de I77; éstos y los de I71/I74/I76 permanecen byte a byte.

## Binding al primer rol requerido

El nuevo resolver empieza con sólo `builtins.dict` ligado. Las otras dos entradas de la whitelist I75 empiezan UNRESOLVED. No llama `loaded_bindings` sobre toda la whitelist antes de main. No importa clases/módulos para anticiparlas, no añade discovery ni mueve el discovery original fuera de main. El runner mantiene una única llamada original a main.

Dispatch por **ID de test + helper + slot de operando exactos** ya fijados I75. Después de que el helper original retorne, se determinan las referencias de clase que ese rol permite. Sólo esas referencias se resuelven desde `sys.modules` y el diccionario exacto del módulo ya cargado. Un rol Path/builtin no fuerza clases ajenas; una assertion que lanza no genera proyección positiva ni obliga a resolver operandos no observados. No se reevalúan comparación, isinstance o issubclass.

Para PlaneError/EligibilityError: identidad de módulo y objeto clase exportado; metaclass exactamente type, bases exactamente `(ValueError,)`, módulo/nombre declarados y fuente/hash sellados. Se conservan los descriptores y fuentes I75. No acceso arbitrario a properties, str/repr, import hooks ni clases por parecido. Las suites futuras inyectarán módulos/clases sintéticos nuevos; no importarán clases reales para validar el componente.

Estados por referencia: UNRESOLVED → BOUND una sola vez; cualquier ausencia al primer uso requerido o contradicción pasa a INVALID. No rebind automático si el módulo reaparece, cambia de objeto o reemplaza el export, aunque conserve nombre y bytes fuente. Antes/después de cada proyección y al finalizar se comprueban los bindings ya ligados. Finish no exige clases jamás requeridas: la completitud sigue dependiendo de inventario, frames y operandos observados, no de que se carguen nombres esperados.

La ausencia genera CLASS_MODULE_NOT_LOADED latcheado fuera del stream. No se lanza una excepción instrumental al producto: se conserva retorno/excepción del original, se permite concluir el test y su cleanup propio y se detiene en frontera segura. Primera identidad y primer fallo permanecen conservados. Las lecturas de fuente usan el contador acumulado de inputs de la captura: no abrir un Reader nuevo por consulta para eludir cuotas. Los tres bindings como máximo y sus referencias cuentan dentro de los límites existentes; sin ampliar whitelist o scopes.

## Semántica tipada preservada

I75 se mantiene exactamente: 29 IDs snapshot Drive, DI28 construcción negativa, cinco IDs de operandos/seis eventos esperados/11 slots históricos, tres clases y siete políticas I72. El registro nuevo copiará los mismos 321 IDs/12 grupos y bindings de métodos. No se crea N/A ni equivalencia entre identidad Drive, declaración de construcción y head Store T/R.

Encoding tipado, prefijos, HMAC-SHA256 por captura, clave efímera de 32 bytes, tags y roles no cambian. Path sólo léxico stdlib pinneado, sin filesystem ni clave/ruta publicada o pasada a hijos. El lector sólo valida formato y enlaces de valores ocultos, sin recomputación independiente. Excepción: TYPE_AND_ARGS_PROJECTION_NOT_FULL_EXCEPTION_OBJECT. Builtin-only delega al digest I70 byte idéntico; records y retornos no cambian. Subtests, fallos, skip, callbacks y restauración conservan su significado. Los bindings tardíos no acreditan persistencia, fsync ni recuperación integrada.

## Diagnóstico cerrado en el sidecar existente

No se retiene stderr libre ni se añade archivo, pipe o cuota. Se usa el descriptor sidecar existente, validado con autoridad/canales/owner. Diagnóstico `d5.worker-diagnostic.v1`, claves exactas:

`schema, status, phase, code, scope, lease, pid, pgid, capture_run_id`.

Máximo **4096 bytes UTF-8 serializados**, incluidos dentro del límite sidecar de 12MiB y del paquete. Schema/scope P01 son literales; lease es nonce canónico de la capacidad propia; pid/pgid enteros exactos positivos iguales al worker/grupo correlacionados por READY. capture_run_id es UUID canónico si se creó Recorder; en fallo previo es null, sin inventarlo. En sidecar completo coincide con el run_id de captura. No campos adicionales, texto de error, args, traceback, rutas, payloads, keys HMAC o entorno privado. Nunca serializar directamente `ex.code`: sólo elegir un literal de la lista cerrada del JSON. Código desconocido u otra excepción → SANITIZED_WORKER_ERROR, sin str/repr de la excepción.

Estados: COMPLETED sólo con phase=COMPLETE/code=OK tras finalizar; esto declara terminación del protocolo y **no PASS funcional, captura suficiente ni cierre**. FAILED requiere fase distinta de COMPLETE y código distinto de OK. Las fases y códigos permitidos quedan enumerados en el JSON. El primer fallo latcheado fija fase/código; cleanup/finalización no lo sustituyen por OK o por un error de parseo posterior. Errores secundarios del padre se registran por códigos cerrados y acotados en contexto, separados del diagnóstico del worker. Un sidecar completo que sea instrumentalmente INVALID/INCOMPLETE debe llevar FAILED con primera causa permitida o CAPTURE_INVALID/CAPTURE_INCOMPLETE, nunca COMPLETED/OK. Un FAIL funcional con protocolo e instrumentación completos puede llevar COMPLETED/OK; el resultado funcional y exit code siguen fallando y el launcher bloquea.

Dos formas exclusivas en **el mismo sidefd**, un único documento JSON:

- Finalización normal: schema `d5.late-sidecar.v1`, campos del sidecar I76 más `worker_diagnostic`; validación normal de raw, inventario, referencias, páginas y completitud sin relajación.
- Fallo antes de iniciar escritura final: schema `d5.late-worker-failure.v1`, claves exactamente `schema, worker_diagnostic`, con FAILED. Envelope completo ≤4096 bytes. No agregar frames/raw/resultado funcional ficticios.

El worker prepara/valida el JSON y su tamaño antes de empezar a escribirlo. Si la escritura ya empezó y falla, no intenta append de un segundo JSON, truncado, reparación u overwrite. Conserva parcial; el padre marca SIDECAR_PARTIAL_OR_INVALID y diagnóstico NOT_RECORDED cuando no puede validarlo. Fallos anteriores a validar autoridad/capacidad no escriben al fd no confiable; el padre sólo declara ausencia, sin atribuirles una fase o causa interna. El contrato no promete diagnóstico para SIGKILL, falta de capacidad o escritura parcial.

El padre lee de forma acotada, discrimina schema y valida tipo/keys/allowlist/correlación antes de publicar el diagnóstico. Un fallo válido produce BLOCKED_WORKER_FAILURE con su fase/código observado; raw vacío puede figurar como error de artifact separado, sin convertir INVALID_JSON en causa del worker. Envelope inválido/ausente: INVALID_WORKER_DIAGNOSTIC o WORKER_DIAGNOSTIC_NOT_RECORDED, causa interna desconocida. Archivo bien formado no es atestación independiente; un caller que controla código/manifest no gana autoridad humana.

## Transporte, presupuestos y perfil propuesto

Namespace **nuevo** `testing/prospective_capture_late/{capture.py,worker.py,test_late_capture.py,run_late_lab.py,README.md}`, registro fijo `docs/validation/D5-LATE-CAPTURE-REGISTRY.json`. Helpers puros I70/I73/I76 pueden reutilizarse sin cambiar funciones/constantes globales, fuentes o registros anteriores. Nuevo worker/launcher integran las formas del sidecar y resolver; no reutilizar el main/authority/launch I77 para el nuevo destino. Normal/failure son schemas distintos y nunca se agregan como metadata funcional equivalente.

Autoridad futura `docs/validation/D5-I80-capture-authorization.json`, schema `d5.late-capture-authority.v1`, claves exactas `schema/phase/scopes/registry_sha256/capture_inputs`, fase I80_EXPLICITLY_APPROVED, scopes=[P01]. Requiere aprobación humana posterior a I79 y pins del contrato/registro/código/evidencia I79 validada y dependencias I69–I78; incluir seal I79 y sus artifacts. No crear en I78/I79, ni reutilizar I77. Destino exclusivo `docs/validation/D5-I80-P01/`, copia fija hermana `D5-I80-P01-launch.json`. Captura completa de 321 ocurrencias en 12 grupos, sin sumar77 I71 o321 I74, sin reanudar sólo los35 frames históricos.

OWNER y correlación READY/RELEASE nonce/PID/PGID/fds/directorio intactos. Diagnóstico correlacionado no autoriza señalizar grupos distintos. EOF/timeout/recursos no confirmados bloquean; limpieza sólo propia y confirmada, sin inspeccionar dev/run_data/D4 operativo ni terceros. No introducir actores adicionales para completar la campaña.

**Ningún techo aumenta**: 131072 eventos/campaña,2048/test,4KiB/evento,32 páginas de2MiB y64MiB acumulados; raw/índice/contexto/launcher≤12MiB, paquete≤112MiB+4KiB y37 miembros lógicos como máximo contando copia launcher. Diagnóstico es parte del sidecar, sin miembro adicional. Operand16MiB, depth32, string4096, frames4096, refs16384; inputs4096 paths/16MiB archivo/128MiB únicos/256MiB leídos; evidencia128MiB únicos/256MiB leídos acumulados por ámbito. Resolver, páginas y diagnóstico no reinician contadores. 300s externos I79,900s externos futuros y límites menores del runner/hijo/hook; sin ampliación de alarmas/kernel. No capacidad funcional probada por el diseño o por los futuros PASS sintéticos.

## Evidencia propuesta y continuidad

LB01–LB64 sólo propuestos, NOT_RUN. I79 usaría clases/módulos/productores y procesos sintéticos nuevos para reproducir carga temprana/tardía, ausencia/reemplazo, fallos pre-raw y escritura parcial; cuotas, restauración, separación de resultados y ownership. Debe registrar comando/contexto/versiones, raw por caso, anclas AST/hashes pre/post, temporales/sentinels/grupos propios. Cero imports de producto/runners/I38/I67 y cero PG64/AT80/P01/P02–P10, SQL/Java/Docker. En una futura captura, toda nueva incompatibilidad de API/oráculo/presupuesto se conserva y presenta antes de ampliar o repetir; sin aprender whitelist o pins desde PASS.

I71/I74/I77 bloqueados e inmutables; P02–P10 I71 pendientes de suficiencia. Como máximo captura futura TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW, seguida de revisión separada por obligación. P0, **81 SUPPORTS_BOUNDED /3 PARTIAL**, UI01.2/UI04.1/UI09.2 parciales. D1–D4 cerrados e hito D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. D5 global/H07/G01–G07 y GI33/GI34/GI38/GI39/GI40 globales abiertos; histórico30/35 sin promoción. Límites finitos/fsync/nativos intactos. Sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue o D6. Sólo I52 publicado; Git local se verificará, sin acceso remoto ni push. Una publicación requeriría decisión separada sobre SHA concreto.
