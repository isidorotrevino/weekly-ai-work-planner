# D5 I84 — contrato de registro parental DI07 y cabeceras de hijos

Fecha: **2026-10-27**, Europe/Madrid. Base local `ed25961a401eb50de49102b9f1bd70495690a02d`. **PREPARED_FOR_REVIEW**.
[Matriz PR01–PR96](D5-I84-PARENTAL-CAPTURE-REVIEW.md) · [Selectores, políticas, schemas y pins](../validation/D5-I84-design-review.json) · [Integridad](../validation/D5-I84-integrity.json) · [Resultado I83](../validation/D5-I83-results.md).

## Autoridad y fases

La selección A posterior a I83 autoriza **sólo diseñar** un registro parental cerrado para DI07 y reglas de identidad/recibo de hijos. La selección separada A inicial conservaba los commits locales; la petición posterior del 2026-10-27 autoriza expresamente terminar, hacer commit/push de lo realizado y crear/publicar el handoff. Esta autorización nueva sustituye la preferencia de no publicar, sin autorizar I85/I86. I84 crea cuatro documentos: este contrato, matriz, JSON declarativo e integridad. No implementa perfil/registro ejecutable, importa producto/harness/runners, ejecuta componentes o campañas, crea actores. La única operación remota autorizada ahora es Git para publicación y verificación. AST y hashes son revisión documental, sin ejecutar factories.

La elección de diseñar antes de capturar sustituye **la planificación pendiente** de captura I84 de I83. No cambia su código, raw, flags o dictamen histórico. Su autoridad/destino/launcher I84 deben seguir ausentes y no reutilizarse. Propuesta posterior: **I85** implementaría un namespace/registro nuevos y PR96 sólo sintéticos bajo300s externos, previa aprobación. **I86** necesitaría otra autorización humana para P01 completo321/12 en destino nuevo bajo900s externos, dominando límites menores previos. Ninguna de esas fases se autoriza en I84. La transición evita que un mismo nombre identifique diseño y captura o que se reinterprete una autoridad antigua.

Máximo resultado futuro de una captura completa: TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW. IR03 requiere revisión posterior, sin cierre automático de UI04.1, GI o D5. CT96 sigue siendo evidencia de componentes I83; no prueba compatibilidad P01 ni recuperación integrada.

## Carencias observadas por fuente

DI07 (`IncrementalCaptureTest.test_DI07_fresh_process_recovers_state_from_disk`) obtiene un Pipe del contexto spawn, construye un Process con target `child_snapshot`, llama start y compara el snapshot recibido con otro ya obtenido en el padre. No pasa por start/spawn de los harness registrados en I83. Su conexión queda sin registrar bajo ese contrato; no es un fallo runtime observado en I83. `child_snapshot` llama al snapshot original en su hijo y envía ese retorno por la conexión ya existente.

Otros dos límites requieren reglas explícitas. T/R dispatch retorna exactamente `send_id,ticket,receipt`: su último recibo público es anidado. Remote.execute retorna `r['result']`, sin cabecera Store, aunque la fuente calcule un UUID5 interno. Tampoco coincide el catálogo READY I83 de nueve puntos con todos los literales de fuente: Client añade after_issue,after_remote,after_query,before_result en T/R. Se proponen **13 puntos cerrados**, conservando sus anclas como EXPECTED_SOURCE_POINT, nunca como medición de gate/fsync del hijo.

El JSON fija **37 anclas de repositorio, cinco bindings stdlib por AST, quince políticas CP01–CP15 y un selector directo DI07**. Se reutilizan los pins de tipos stdlib y demás reglas I82/I83. Son expectativas de fuente; no convierten nombres, hashes, ramas o multiplicidades en observaciones runtime.

## Registro directo propuesto: scope y binding

Única ampliación de observers para el registro directo: retornos de `multiprocessing.context.BaseContext.Pipe` y vista mínima previa/terminal de `multiprocessing.process.BaseProcess.start`, **sólo dentro del frame DI07 exacto, subcaso y hilo del test padre**. Fuera de ese selector se delega al original sin inspeccionar proceso, endpoints o payload. No es una autorización para interceptar todos los actores del runner.

Se comprueban clase/objeto/fuente/firma/puntero de TestCase, TemporaryFixtureLab, SpawnContext, SpawnProcess, Connection, Popen y funciones stdlib. El target debe ser el **mismo objeto función** `test_incremental_capture.child_snapshot`, con fuente/primera línea/firma pinneadas. Un nombre equivalente no basta. La clase y target aparecen durante discovery de main: binding tardío desde módulos ya cargados al entrar en el test autorizado, sin import/discovery nuevo, sin rebind tras invalidación. Alteración o falta requerida bloquea y exige presentar ajuste.

Pipe se llama una sola vez con los argumentos originales. Sólo **después de retornar** se valida el tuple exacto de dos Connection distintos y se conservan referencias fuertes locales a ambos endpoints y su contexto. No se publica id(), fd, fileno, repr, path o payload. Una pareja provisional no acredita proceso ni protocolo. Se permite como máximo una pareja y un start exitoso para este selector cuya fuente contiene una sola creación; otra cardinalidad queda incompleta, sin ampliar ni rellenar.

Antes de start original se permite una excepción nueva y explícita de lectura de memoria stdlib: dict directo de SpawnProcess exacto, `_target`, `_args`, `_kwargs`, `_popen`. `_args` debe ser tuple exacto de longitud4; `_kwargs`, dict exacto vacío; `_popen`, None antes del start. Se extraen únicamente el run_id del índice1 y el endpoint child del índice3. Los índices0(root) y2(scope) se ignoran: no copiar, publicar, hashear, abrir ni inspeccionar esos valores. No usar descriptors personalizados, `__getattr__`, coerción, str/repr o callstack genérico.

La conexión child debe coincidir por **is** con exactamente una pareja del mismo frame/subcaso/hilo; el run_id observado debe coincidir con el campo público run_id del lab exacto del TestCase activo. Esa lectura nueva se limita a TestCase.__dict__.lab y TemporaryFixtureLab.__dict__.run_id; nunca root/scope. No se une por orden de listas, tiempo, PID, fd, semejanza de nombre o UUID del collector.

start original se llama exactamente una vez. CPython elimina `_target/_args/_kwargs` al retornar; por ello la vista mínima se toma antes y se elimina su referencia transitoria después. Sólo tras retorno exitoso None se verifica `_popen` exacto y el pid escalar ya producido, y se registra proceso→pareja→conexión parental. PID es metadata, no llave de correlación. Si start lanza, se relanza **la misma instancia** y no se registra éxito. Si falla la instrumentación, el original y su cleanup conservan su comportamiento; se latchea el fallo y se detiene entre tests, sin crear señales/cleanup de dominio desde el observer.

## Evidencia DI07 y cadena de autoridades

El registro propuesto `d5.parental-registration.v1` tiene claves exactas en JSON y vive en `parental_registrations` del mismo sidecar. Referencias Pipe/proceso/endpoints/target/contexto consumen la cuota compartida. El registro termina PROVISIONAL, START_OBSERVED o INCOMPLETE según lo realmente observado; no se rellena un resultado esperado de fuente. No se solapa con el registro start/spawn anterior: el nuevo scope es sólo el caso directo DI07; si se detecta doble asociación, bloquear en vez de contar dos pruebas.

recv se sigue llamando una sola vez sobre el canal original; sólo una conexión registrada recibe proyección. El snapshot del hijo conserva autoridad **CHILD_PROTOCOL_RETURN**, run/version/head y digest I70 del retorno completo ya producido, con flags pasivos observados. Se valida la forma exacta de doce claves del snapshot de fuente; sólo su cabecera/digest permitidos se retienen, sin state completo. El snapshot del padre mantiene **OWN_FIXTURE_SNAPSHOT** y el digest de su retorno original; no se llama snapshot/independent otra vez.

Recorrido propuesto: frame/input/entorno/método → subcaso ROOT_FRAME observado → pareja Pipe → endpoint child del target exacto/start → conexión parental registrada → snapshot recibido → predicado assertEqual y resultado originales. El enlace al predicado requiere digests completos compatibles de los operandos realmente registrados y el mismo actor/run/contexto. No se reevalúa assertEqual, invoca id del subTest ni añade una prueba. Varios witnesses compatibles se conservan como conjunto, sin atribuir origen único por cercanía; si la obligación exige unicidad no resuelta, queda missing.

join/finish originales no se alteran. Tras un join ya producido se puede leer returncode directamente del Popen exacto, sin poll/wait/is_alive/kill/exitcode auxiliares. Pending no significa0; ausencia o conflicto se propaga. El cleanup original de DI07 conserva sus propias llamadas y límites, sin nuevas señales del capturador. Fuente del target y mensaje parental no equivalen a wrappers ejecutados en hijo, lectura independiente del collector o fsync nativo medido.

DI07 es un snapshot: sus campos de command_id/recibo son N/A **sólo bajo esa política**, no una razón genérica para dispensar recibos de mutaciones. El avance previo del padre y su cid pertenecen a otra llamada; nunca se prestan al hijo.

## Quince políticas de retorno e identidad de hijos

CP01–CP07 cubren siete acciones T; CP08–CP13 seis R; CP14–CP15 snapshot/advance Drive. Cada política fija familia, acción, forma del retorno, header_status y cobertura. La selección procede del start/spawn original autorizado y sus argumentos observados; no se aprende una forma desde un mensaje desconocido.

| Retorno original | Proyección permitida | Límite |
|---|---|---|
| mutate/raw_mutate/reconcile T/R | Recibo Store exacto, cabecera y selectores I83 | Sólo el recibo devuelto; no toda la historia interna |
| advance Drive | Recibo Drive exacto y commit_sha256 observado | version/head no son seq/Store T/R |
| dispatch T/R | Tuple de protocolo OK con dict exacto send_id/ticket/receipt; IDs UUID y recibo anidado proyectado | **LAST_PUBLIC_RECEIPT_ONLY**: ISSUE/RESULT/Remote intermedios no pasan a observados |
| remote T/R | Digest builtin y selectores cerrados del resultado público | **REMOTE_RESULT_WITHOUT_STORE_RECEIPT**; sigue missing si se exige cabecera Store |
| snapshot T/R | Schema durable-summary/relational-summary de fuente y digest original | Summary no es nuevo oráculo independiente |
| snapshot Drive DI07 | Schema fixture-drive-snapshot y cabecera/digest original | Sin command_id; autoridad de protocolo parental |
| initialize T | None exacto de Store.create | **GENESIS_NO_COMMAND_RECEIPT**; no prueba fsync/publicación desde exit0 |

Header normalizado `d5.child-header-observation.v1`, claves/statuses cerrados en JSON, dentro del mensaje de la instancia de protocolo existente. El puntero al recibo anidado sólo resuelve en ese sidecar y en ese mensaje; no se finge raw_pointer ni se busca recursivamente una clave receipt. Se conserva outer_result_digest separado del digest/proyección del recibo. send_id yticket son selectores propios, nunca command_id. Campos inesperados, ubicaciones alternativas o recibos parciales no se truncan ni se convierten en N/A.

Un cid explícito en args parentales se etiqueta REQUESTED_PARENT_COMMAND_ID: intención observada. El header.command_id se rellena sólo desde un **recibo realmente emitido por el protocolo**; su autoridad es ACTUAL_PROTOCOL_RECEIPT. Si falta, command_id queda null y CHILD_LOCAL_NOT_OBSERVED aunque la intención tenga cid. Valores contradictorios implican conflicto. No generar/recalcular cid desde uuid4/uuid5, ticket, fórmula de Remote, recibo posterior de otro actor o ParentIntentID. Esta última identidad pertenece al observer.

READY distingue expected_point del mensaje original observado y sólo acepta los13 literales pinneados; ERROR conserva un código público acotado ya recibido, sin nuevo str/repr de excepciones. Un ACK, un punto esperado o exit0 no sustituyen un recibo obligatorio. Las mutaciones que ocultan su cabecera siguen incompletas para esa obligación; este diseño no modifica producto, workers de dominio ni protocolo para hacerlas emitirla.

Un negativo previo a publicar sólo puede recibir soporte acotado cuando coinciden contexto/intención, protocolo real y oráculo ya retornado de no efecto. El catálogo de fuente no convierte cualquier nombre before_* en precommit: requiere el punto concreto y cabezas compatibles. after_object no prueba ausencia de objetos huérfanos; directory_fsync/recovery_fsync, prepared concurrente y puntos compuestos del cliente no garantizan no-efecto. Si falta cid, persiste ese límite; si cambia head o se exige identidad de ejecución real, queda missing. No se llama un reader de dominio para rellenarlo.

## Lector, esquemas y presupuesto

Propuesta de namespace `testing/prospective_capture_parental` con cinco archivos y registro nuevo `D5-PARENTAL-CAPTURE-REGISTRY.json`; schema normal `d5.parental-sidecar.v1`, fallo `d5.parental-worker-failure.v1`. Se conservan tablas I83 y se añade parental_registrations dentro del mismo sidecar; protocolos nuevos versionan la extensión registration_ref/policy_ref y header del mensaje, sin reescribir evidencia antigua. I85 deberá fijar el registro/lector exactos contra este JSON antes de ejecutar PR96.

El lector valida conjuntos de claves/tipos, referencias locales, actor/run/frame/subcaso/hilo, pin target, par único, estados de start, política de cada mensaje, schema del header, receipt/command/request y cobertura parcial. Huérfanos, duplicados, ciclos, cross-frame, valores mutados o asociaciones ambiguas bloquean. No basta un hash igual, estar en el mismo test o una fila con etiqueta correcta. Enlace recibo↔oráculo sólo por dominio y headers observados compatibles: **after_data_sha256 se calculó antes de insertar el recibo y no es oracle.state_sha256**. Se conservan encodings Store sin newline, Drive con newline e I70/bytes originales separados.

No hay archivo, canal, actor, barrera, hook, checkpoint, llamada de medición o reserva nuevos. Se enriquecen eventos existentes o se añade como máximo un terminal por límite nuevo; ninguna CALL_START de evento ni muestreo/descarte de evidencia previa para caber. I85 conserva dentro de16384 refs también parejas provisionales, contextos, mensajes, registros y links; no contadores paralelos ni reset al cambiar clase/hilo/página.

Todos los techos I72/I75/I78/I83 siguen exactos:131072 eventos/campaña,2048/test,4096 bytes/evento/fila,32 páginas de2MiB/64MiB acumulados,12MiB raw/sidecar/contexto/launcher,37 miembros y112MiB+4KiB;4096 frames,16384 refs,depth32,string4096 y16MiB por valor con hash/encoding auxiliar contabilizado. Inputs/evidencia:128MiB únicos/256MiB leídos por ámbito, Reader acumulado antes/después/autoridad, sin reset para eludir cuotas. Pares pendientes no justifican memoria ilimitada ni retención de root/scope/args completos.

Los503 inputs de preservación documental no se convierten en inputs runtime ejecutados. El JSON fija una base runtime específica de58.670.898 bytes conocidos, que habrá que completar con contrato/registro/código/evidencia/sello nuevos y medir de nuevo antes de autorizar captura. PR96 ensayará límites, preservación de llamadas/excepciones, actores sintéticos propios y restauración bajo300s; no importa producto/runners ni ejecuta CT96 o suites antiguas. No prueba capacidad P01. Cualquier incompatibilidad de API/oráculo/presupuesto detiene el alcance y se presenta antes de ampliar o repetir.

Diagnóstico I78 conserva schema, allowlist, primera fase/código y4096 bytes en el sidefd existente. Nuevos fallos de registro/header quedan en errores cerrados del sidecar y se mapean a SANITIZED_WORKER_ERROR si no tienen literal diagnóstico previo. Una escritura JSON; no append/overwrite tras parcial ni causa runtime inventada desde AST. Se preservan nonce/OWNER/PID/PGID/fds, READY/RELEASE, destino exclusivo y retirada confirmada del grupo propio del launcher. No se inspeccionan o limpian recursos ajenos, dev/run_data/D4.

## Continuidad y decisión siguiente

Aprobar este contrato autorizaría, sólo si se elige expresamente, I85: perfil/registro nuevos y **PR01–PR96 sintéticos**, sin P01/P02–P10, I38/I67, SQL/Java/Docker, producto/runners históricos ni reejecución de CT96/PF60/PG64/AT80/LB64. Helpers puros previos pueden reutilizarse por hash sin mutar sus globals/funciones/registros. La regla DI07 incompleto de I83 sólo se sustituye en el perfil nuevo cuando sus registros/predicados estén completos; no se filtran otros missing o errores ni se parchea I83 en memoria.

Tras I85 validado, otra aprobación I86 exigiría autoridad `D5-I86-capture-authorization.json`, schema d5.parental-capture-authority.v1, fase I86_EXPLICITLY_APPROVED, claves exactas schema/phase/scopes/registry_sha256/capture_inputs y scopes=[P01]. Tendría pins del perfil/contrato/registro/evidencia/sello y artifacts/dependencias pertinentes. Destino nuevo exclusivo `D5-I86-P01/`, launcher hermano `D5-I86-P01-launch.json`. Nada de eso se crea en I84 o I85. Se capturarían321 IDs/12 grupos completos, sin reanudar sólo DI07 ni sumar paquetes I71/I74/I80. Suficiencia posterior separada; sin cierre por PASS.

P0; **83 SUPPORTS_BOUNDED/1 PARTIAL**, UI04.1 parcial; UI01.2/UI09.2 mantienen soporte acotado I81. D1–D4 cerrados e hito D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos;30/35 sin promoción. D5 global/H07/G01–G07 y GI33/GI34/GI38/GI39/GI40 globales abiertos. Sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue ni D6. I83 y toda historia anterior permanecen byte a byte; no se deduce persistencia o recuperación integrada de PASS aislados. La base documental tenía sólo I52 publicado. La petición posterior del 2026-10-27 autoriza publicar los commits locales, I84 y su handoff, sin force; los SHA/resultados reales se registrarán en el handoff tras el push. No autoriza proveedores ni campañas o nuevas publicaciones futuras.
