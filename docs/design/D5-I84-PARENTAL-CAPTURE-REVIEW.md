# I84 — matriz propuesta PR01–PR96

[Contrato](D5-I84-PARENTAL-CAPTURE-DESIGN.md) · [Selectores, políticas y pins](../validation/D5-I84-design-review.json) · [Integridad](../validation/D5-I84-integrity.json).

96 casos **NOT_RUN**. Propuesta I85 sólo sintética bajo300s externos; no importa ni ejecuta producto/runners, CT96 u otras suites históricas. Cada caso deberá conservar método/ancla/hash pre/post, raw/contexto y observación del oráculo requerido; presencia de campos o conteos no sustituyen la comprobación.

| Caso | Familia | Disparador | Oráculo exigido |
|---|---|---|---|
| PR01 | AUTHORITY | Selección A posterior a I83 | Sólo cuatro documentos I84; flags de implementación/campaña/publicación falsos. |
| PR02 | AUTHORITY | Intento de capturar usando nombre I84 antiguo | No crear/reutilizar autoridad/destino; plan histórico I83 intacto. |
| PR03 | AUTHORITY | I85 sin aprobación posterior | No implementar ni ejecutar PR96 desde el diseño. |
| PR04 | AUTHORITY | Autoridad I83/I80 o scopes P02–P10 | Rechazar; futura autoridad I86 única y explícita P01. |
| PR05 | AUTHORITY | Plan futuro por defecto | NOT_RUN_I86_AUTHORIZATION_REQUIRED sin hijos/escrituras funcionales. |
| PR06 | AUTHORITY | Pins o catálogo15/selector DI07 alterados | Rechazar antes de importar runner o instrumentar. |
| PR07 | AUTHORITY | Caller controla fuente/manifiesto | Coherencia no atestación independiente ni permiso humano por archivo. |
| PR08 | AUTHORITY | Publicación solicitada junto al próximo corte | Aplicar autorización de publicación vigente por separado de I85/I86; ningún push se infiere de aprobar PR96. |
| PR09 | BINDINGS | BaseContext.Pipe original | Hash/firma/identidad exactos; contexto exactamente SpawnContext. |
| PR10 | BINDINGS | BaseProcess.start original | Fuente/firma/puntero y clase SpawnProcess exactos; sin método alternativo. |
| PR11 | BINDINGS | child_snapshot aún no descubierto | Binding diferido al test autorizado, sin import/discovery nuevo. |
| PR12 | BINDINGS | Mismo nombre de target con otra identidad/código | No registrar; missing/fallo cerrado y original intacto. |
| PR13 | BINDINGS | Clase/módulo/callable reemplazado | Latch, sin rebind; restaurar pointers propios exactos. |
| PR14 | BINDINGS | Private fields de clase ajena | No inspección; delegar fuera de selector, bloquear requisito afectado. |
| PR15 | BINDINGS | TestCase y lab no coinciden con pins | No usar el id textual como autorización suficiente. |
| PR16 | BINDINGS | Cambio de versión/AST/código stdlib | Bloquear alcance; no fallback genérico a properties o introspección libre. |
| PR17 | PIPE_PAIR | Pipe retorna par original en DI07 | Una llamada, mismo tuple/endpoints; registrar referencias locales sólo después. |
| PR18 | PIPE_PAIR | Pipe fuera del frame/subcaso/hilo DI07 | Delegar sin inspeccionar endpoints o payload. |
| PR19 | PIPE_PAIR | Retorno con tipo/cardinalidad no permitido | Latch conservando el retorno original; sin coerción. |
| PR20 | PIPE_PAIR | Mismo endpoint en ambas posiciones | Rechazar; no fabricar pareja válida. |
| PR21 | PIPE_PAIR | Dos pares o endpoint repetido ambiguo | No elegir por orden/fecha/fd/PID; propagar missing. |
| PR22 | PIPE_PAIR | Endpoint child cerrado por cleanup original | Usar referencia retenida por identidad; sin fileno/closed/read extra. |
| PR23 | PIPE_PAIR | ID de objeto reciclado | Referencias fuertes acotadas al ciclo propio; no publicar id() ni reutilizar. |
| PR24 | PIPE_PAIR | Pair sin start coincidente | Provisional no equivale a proceso/recibo; requisito DI07 incompleto. |
| PR25 | PROCESS_START | SpawnProcess antes de start | Leer _target/_args/_kwargs ya producidos; sólo campos/índices autorizados. |
| PR26 | PROCESS_START | Args exact tuple len4 con kwargs vacío | Extraer run_id y endpoint índice3; ignorar root/scope sin copiar/publicar/hash. |
| PR27 | PROCESS_START | Target y child endpoint coinciden por is | Un único par del mismo contexto y run_id del lab observado. |
| PR28 | PROCESS_START | start borra _args al retornar | Guardar vista mínima previa y borrar refs privadas transitorias; no releer campos borrados. |
| PR29 | PROCESS_START | start original exitoso | Registrar después de retorno None y Popen exacto/pid ya producido; no poll. |
| PR30 | PROCESS_START | start original lanza | Misma instancia de excepción; no registro exitoso ni actor adicional. |
| PR31 | PROCESS_START | Start duplicado/proceso con pareja distinta | Sin rebind; conflicto/missing y comportamiento original preservado. |
| PR32 | PROCESS_START | Start sin target/args/run/context válidos | No deducir desde source o proximidad; no impedir cleanup original. |
| PR33 | DI07_GRAPH | Registro directo DI07 completo | Conectar Pipe→endpoint child→target/start→parent conn→protocolo dentro del mismo frame. |
| PR34 | DI07_GRAPH | Snapshot recibido del hijo | CHILD_PROTOCOL_RETURN con run/version/head y digest completo original, no wrapper en hijo. |
| PR35 | DI07_GRAPH | Snapshot ya retornado al padre | Mantener OWN_FIXTURE_SNAPSHOT como autoridad distinta. |
| PR36 | DI07_GRAPH | assertEqual original de los dos snapshots | Ligar por digests completos compatibles y contexto; callback/outcome original sin reevaluación. |
| PR37 | DI07_GRAPH | Múltiples witnesses equivalentes | Conservar conjunto compatible; no asignar origen único por posición. |
| PR38 | DI07_GRAPH | Snapshot del hijo con otro run/head/version | Conflicto explícito; exit0 no rehabilita identidad o contenido. |
| PR39 | DI07_GRAPH | Join produjo returncode o queda pending | Leer escalar ya producido; pending conserva missing sin esperar/matar desde observer. |
| PR40 | DI07_GRAPH | DI07 no necesita command_id para snapshot | N/A sólo de campos de comando por política snapshot; no inventar recibo durable. |
| PR41 | CHILD_HEADERS | OK mutate/raw_mutate/reconcile T/R | Recibo Store exacto; command/request/seq/flags originales, sin payload arbitrario. |
| PR42 | CHILD_HEADERS | OK advance Drive | Recibo Drive exacto y commit_sha256 observado; no equiparar version con seq Store. |
| PR43 | CHILD_HEADERS | OK dispatch T/R | Forma exacta send_id/ticket/receipt; extraer sólo recibo anidado original. |
| PR44 | CHILD_HEADERS | Dispatch con múltiples comandos internos | LAST_PUBLIC_RECEIPT_ONLY; no declarar observada toda la operación. |
| PR45 | CHILD_HEADERS | OK remote sin recibo Store | REMOTE_RESULT_WITHOUT_STORE_RECEIPT; missing si el criterio pide esa cabecera. |
| PR46 | CHILD_HEADERS | Snapshot/summary de familia T/R/Drive | Schema de su política; digest/metadata cerrada, no nueva independencia por etiqueta. |
| PR47 | CHILD_HEADERS | OK initialize T devuelve None | GENESIS_NO_COMMAND_RECEIPT; no inferir publicación/fsync o command_id desde exit0. |
| PR48 | CHILD_HEADERS | Campo receipt en ubicación/tipo desconocido | Sin búsqueda recursiva ni whitelist aprendida; INVALID_CHILD_SCHEMA. |
| PR49 | IDENTITY_NEGATIVES | cid explícito en args del padre | REQUESTED_PARENT_COMMAND_ID separado del comando realmente observado en recibo. |
| PR50 | IDENTITY_NEGATIVES | cid generado sólo en hijo antes de crash | CHILD_LOCAL_NOT_OBSERVED; ParentIntentID/ticket/send_id nunca sustituyen cid. |
| PR51 | IDENTITY_NEGATIVES | Recibo observado contradice cid/request parental observado | Conflicto; no escoger uno ni recalcular el otro para hacer match. |
| PR52 | IDENTITY_NEGATIVES | UUID5 de Remote deducible por fuente | No recomputar ni promover a identidad runtime; conservar falta de recibo. |
| PR53 | IDENTITY_NEGATIVES | READY seguido de negativo prepublicación | Requiere protocolo real y oráculo no-efecto compatible; límite sin cid explícito. |
| PR54 | IDENTITY_NEGATIVES | Head cambia o frontera no es prepublicación cerrada | No aceptar no-efecto ni N/A; evidencia posterior y límites explícitos. |
| PR55 | IDENTITY_NEGATIVES | ERROR de protocolo original | Código cerrado ya recibido; no str/repr nuevo de excepción ni éxito por exit0. |
| PR56 | IDENTITY_NEGATIVES | ACK/READY/código0 sin recibo requerido | Missing obligatorio; no convertir en cabecera o recuperación integrada. |
| PR57 | READER_LINKS | Schema de registro/política/header versionado | Conjuntos exactos/tipos/alfabetos, source selectors y autoridades verificadas. |
| PR58 | READER_LINKS | Puntero a recibo anidado | Local al sidecar propio y mismo mensaje; no raw_pointer ficticio ni abrir archivos. |
| PR59 | READER_LINKS | Enlace huérfano/duplicado/ciclo | Rechazar en recorrido acotado, sin matching por cercanía. |
| PR60 | READER_LINKS | Hash Store/Drive/I70/bytes | Encoding y dominio exactos; no comparar after_data contra oracle state. |
| PR61 | READER_LINKS | Run/contexto/actor/endpoint difieren | Bloquear enlace aunque digest o nombre coincida. |
| PR62 | READER_LINKS | Registro directo y helper se solapan | Una instancia lógica; en caso ambiguo bloquear, sin doble crédito. |
| PR63 | READER_LINKS | Mensajes antiguos o tomados de I80/I71 | No rellenar captura nueva ni recuperar preimágenes históricas. |
| PR64 | READER_LINKS | Fila/header pendiente en test | Missing se propaga a test/grupo/campaña; ningún PASS lo elimina. |
| PR65 | BOUNDS | Evento o fila supera4096 bytes | Invalidar sin truncar, dividir semántica o descartar eventos previos. |
| PR66 | BOUNDS | 131072/campaña o2048/test | Mismos contadores compartidos incluyendo nuevos límites terminales. |
| PR67 | BOUNDS | Pipe/start provisional y registros nuevos | Consumir refs16384/frames4096/depth32/string4096; no pool paralelo/reset. |
| PR68 | BOUNDS | Tabla de registro/headers y canales | Dentro del sidecar12MiB;37 miembros/112MiB+4KiB intactos, sin archivo o pipe extra. |
| PR69 | BOUNDS | Hash/parse de argumentos/resultados | Operand16MiB con bytes auxiliares contabilizados; builtins exactos. |
| PR70 | BOUNDS | Reader de fuentes/autoridad/paquete | 128MiB únicos/256MiB leídos acumulados por ámbito; sin reset entre fases. |
| PR71 | BOUNDS | Tiempo de componente/futuro runner | 300s externos PR96/900s futuro; dominan límites menores previos. |
| PR72 | BOUNDS | Capacidad P01 no demostrada | PR96 no promete que321/12 quepan; detener y presentar ajuste antes de ampliar/repetir. |
| PR73 | PASSIVE | Wrapper normal de Pipe/start/recv/join | Original exactamente una vez; misma identidad del retorno y mismos argumentos. |
| PR74 | PASSIVE | Error de proyección antes o después de original | Latch conservando retorno/excepción; cleanup y parada entre tests. |
| PR75 | PASSIVE | Nada de mediciones auxiliares | Cero recv/poll/send/wait/kill/snapshot/lookup/FS de dominio añadidos. |
| PR76 | PASSIVE | No observers en hijo | Wrappers sólo padre; fuente target no acredita ejecución instrumentada en hijo. |
| PR77 | PASSIVE | Código desconocido en diagnóstico | Mapeo cerrado a SANITIZED_WORKER_ERROR preservando primera fase/código. |
| PR78 | PASSIVE | Sidecar parcial | Una escritura; no append/overwrite/reparación posterior. |
| PR79 | PASSIVE | Restauración alterada o excepción de instrumentación | Detectar sustitución, restaurar punteros propios, no cambiar fuente/global previo. |
| PR80 | PASSIVE | Barrera/hook/señal/checkpoint original | No añadir/envolver ni variar scheduling de actores originales; sin gate nativo inventado. |
| PR81 | PRESERVATION | I85 propuesto usa PR96 | Sólo módulos/suites/procesos sintéticos nuevos; sin producto/runners históricos. |
| PR82 | PRESERVATION | Capturas anteriores | I71/I74/I77/I80 e I83 intactos byte a byte; CT96 no se reejecuta. |
| PR83 | PRESERVATION | Helpers puros anteriores | Reutilización por hash sin mutar funciones/globals/registros; namespace nuevo. |
| PR84 | PRESERVATION | Regla DI07 I83 sustituida en perfil nuevo | Sólo cuando registro/links/predicado completos; no filtrar otros missing/errores. |
| PR85 | PRESERVATION | 83/1 y UI04.1 parcial | No cierre por diseño, campos presentes, PASS componentes o exit0. |
| PR86 | PRESERVATION | D1–D4/hito local/30 de35 | Cierres/aceptación conservados; no promoción histórica. |
| PR87 | PRESERVATION | P0 y requisitos reales/humanos | Sin proveedores/credenciales/corpus reales, consumo/reservas, activación/despliegue/D6. |
| PR88 | PRESERVATION | Git/publicación | Publicación actual autorizada expresamente el 2026-10-27; no concede implementación, campaña ni publicación futura automática. |
| PR89 | TRANSITION | Aprobación futura I85 | Autoriza sólo nuevo perfil/registro y PR96 sintético, no captura funcional. |
| PR90 | TRANSITION | Validación I85 falla o nueva API no encaja | Conservar fallo y alcance detenido; presentar ajuste, no ampliar automáticamente. |
| PR91 | TRANSITION | Validación I85 completa | Como máximo componente validado; aprobación humana I86 aún necesaria. |
| PR92 | TRANSITION | I86 autoridad/código/registro/evidencia | Pins exactos y destino nuevo exclusivo; ninguna autoridad antigua reutilizada. |
| PR93 | TRANSITION | P01 futuro | 321 IDs/12 grupos completos; no sumar/reanudar sólo DI07 ni mezclar paquetes previos. |
| PR94 | TRANSITION | Paquete futuro completo | TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW; IR03 separado. |
| PR95 | TRANSITION | Revisión de suficiencia posterior | Contrastar obligaciones, código, pruebas y límites; no cierre automático UI04.1/GI/global. |
| PR96 | TRANSITION | Nueva ausencia causal de hijo | Mantener CHILD_LOCAL_NOT_OBSERVED/missing; proponer corte concreto antes de nuevas campañas. |

Las quince políticas CP01–CP15 y el selector directo único DI07 están en el JSON. Sus ramas y13 puntos de fuente son expectativas, sin ejecución. I84 no crea perfil/registro ejecutable ni autoridad/destino I84/I86. P0;83/1 yglobales OPEN. Publicación de lo realizado autorizada por petición posterior del 2026-10-27; I85/I86 siguen sin autorizar.
