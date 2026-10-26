# I82 — matriz propuesta CT01–CT96

[Contrato](D5-I82-CAUSAL-CAPTURE-DESIGN.md) · [Inventario118/pins/esquemas](../validation/D5-I82-design-review.json) · [Integridad](../validation/D5-I82-integrity.json).

96 casos NOT_RUN, propuestos para I83 sólo sintético bajo300s externos. Sin imports de producto/runners o pruebas antiguas, ni captura P01. Cada caso futuro deberá conservar método/ancla, raw/contexto, hashes pre/post y oráculo observado; no completar por conteo.

| Caso | Familia | Disparador | Oráculo exigido |
|---|---|---|---|
| CT01 | AUTHORITY | Sólo I82 aprobado para diseño | Cuatro documentos; no código/registro/campaña, ni imports de producto/harness. |
| CT02 | AUTHORITY | I83 componentes propuestos sin I84 | CT96 sólo sintéticos; bloquear import/ejecución funcional antes de worker. |
| CT03 | AUTHORITY | Autoridad antigua I80 o pins distintos | No reutilizar; I84_EXPLICITLY_APPROVED y contrato/registro/código/evidencia propios. |
| CT04 | AUTHORITY | Scope,321 IDs/12 grupos o118 selectores alterados | Rechazar;203 unitarios previos conservados sin nuevo crédito causal. |
| CT05 | AUTHORITY | Plan por defecto | NOT_RUN_I84_AUTHORIZATION_REQUIRED, sin crear autoridad/destino/hijos. |
| CT06 | AUTHORITY | P02–P10 o I80 como datos de la nueva captura | Sólo referencias selladas; no sumar ni completar historia. |
| CT07 | AUTHORITY | Destino fijo existente o symlink | Sin overwrite; capacidad propia y correlación READY/RELEASE intactas. |
| CT08 | AUTHORITY | Caller controla código y manifiesto | Coherencia, no atestación independiente o autorización humana por archivo. |
| CT09 | INVENTORY | Cada uno de118 IDs y sus helpers | Ancla AST/hash, clasificación y requisitos condicionales; nunca ejecutar factories o helpers en diseño. |
| CT10 | INVENTORY | Cinco controles sin Store | N/A de dominio motivado; no añadir comando/oráculo durable ficticio. |
| CT11 | INVENTORY | DF07/DF43 yDI28 negativos | Conservar construcción tipada, excepción/cleanup y protocolo cuando exista; no head por constructor. |
| CT12 | INVENTORY | 203 tests unitarios/volátiles | Conservar su evidencia I79; no dar recuperación integrada por instrumentación causal. |
| CT13 | INVENTORY | Subcaso/variante dentro de un test | Contexto observado + objeto/run/intento; no asignación por índice de bucle o proximidad. |
| CT14 | INVENTORY | Rama inexistente o no ejecutada | NOT_OBSERVED/NOT_APPLICABLE sólo si motivo cerrado lo permite; nada desde source. |
| CT15 | INVENTORY | Nueva API/schema/callsite o tipo inesperado | Bloquear alcance y proponer ajuste, sin ampliar whitelist. |
| CT16 | INVENTORY | Counts254/221/43/114 históricos | Diagnóstico de I80, no cardinalidades a imponer o rellenar en la futura captura. |
| CT17 | ORACLE_VALUES | Fila T añadida al ORACLES del harness | Retener exactamente case/role/store_id/seq/commit_sha256/state_sha256/receipts/tasks, validar hash I70. |
| CT18 | ORACLE_VALUES | Fila R y su raw_pointer existentes | Reutilizar valor/puntero válido; extensión tipada no sustituye evidencia existente. |
| CT19 | ORACLE_VALUES | Oráculo con tipo/clave adicional o valor inválido | INCOMPLETE/INVALID; no copiar payload ni truncar para hacerlo pasar. |
| CT20 | ORACLE_VALUES | Lectura original independent retorna | Una llamada, mismo retorno; extraer sólo resumen y cabecera ya producidos, cero IO extra. |
| CT21 | ORACLE_VALUES | Mutación/rewind de lista o valor tras observar | Detectar con hash/snapshot before/after, conservar fallo; no reescribir raw. |
| CT22 | ORACLE_VALUES | store_id ambiguo o sin run observado en mismo ámbito | No generar run_id ni unir con otro frame; vínculo obligatorio faltante. |
| CT23 | ORACLE_VALUES | Puntero retenido en sidecar | Campo sidecar_pointer distinto de raw_pointer; resolución local, exacta y hash/tipo verificados. |
| CT24 | ORACLE_VALUES | Resumen de oráculo ychain devuelta | Proyección de cabecera/recibo válida, no estado completo ni nuevo oráculo independiente. |
| CT25 | COMMAND_HEADERS | Store.transact recibe cid/kind/args/expected | Capturar cabecera real y hashes canónicos/I70 con namespaces separados; sin llamar API extra. |
| CT26 | COMMAND_HEADERS | Client.perform genera cid/expected internos | Ligar al Store.transact anidado observado; no inventar desde defaults o source. |
| CT27 | COMMAND_HEADERS | Retorno de recibo normal o histórico | Retener cabecera permitida, result digest/selectores; histórico no rebobina ni crea efecto. |
| CT28 | COMMAND_HEADERS | Excepción original del comando | Conservar objeto/outcome y código sólo desde tipo exacto/args permitidos; no str/repr. |
| CT29 | COMMAND_HEADERS | Argumentos inválidos en negativo cerrado | Registrar estado INVALID_INPUT_EXPECTED_NEGATIVE y excepción real; no fabricar request_hash válido. |
| CT30 | COMMAND_HEADERS | Argumentos mutables o coerción personalizada | Sólo builtins exactos, cuotas y guardas; cambio de vista invalida sin mutación de producto. |
| CT31 | COMMAND_HEADERS | Receipt.request_sha256 vs hash de operación | Comparación por encoding Store pinneado; digest I70 no es request_sha256. |
| CT32 | COMMAND_HEADERS | Metadata result contiene texto/data/capture/proof arbitrarios | Sólo selectores UUID/hash/int/bool cerrados; resto digest, nunca payload ni recibo completo ficticio. |
| CT33 | DRIVE | advance recibe dict válido | Retener command_id/expected_version/expected_head y hash canónico Drive, sin page/event payload. |
| CT34 | DRIVE | advance recibe bytes JSON | Distinguir hash de bytes y hash de request decodificado; stdlib cerrado y cuotas sin llamar decode del producto. |
| CT35 | DRIVE | Recibo Drive confirmado | Cabecera exacta ycommit_sha256 observado; no homologar con Store T/R. |
| CT36 | DRIVE | Snapshot ya retornado | Reutilizar114 observaciones I80 sólo como referencia; nuevo run produce las suyas, sin snapshot auxiliar. |
| CT37 | DRIVE | Snapshot del hijo recibido por protocolo | CHILD_PROTOCOL_RETURN, no wrapper heredado ni lector de archivos independiente. |
| CT38 | DRIVE | Request corrupto/oversize/schema negativo | Motivo negativo por selector, sin parser/digest ilimitado ni N/A de una ausencia inesperada. |
| CT39 | DRIVE | Identidad Drive cambia en mismo objeto | Invalidar preservando primer valor; versión/head pueden variar sin cambiar run_id. |
| CT40 | DRIVE | Caso exige independencia que sólo ofrece snapshot propio | Marcar límite/missing; no reclasificar ese snapshot como oráculo independiente. |
| CT41 | SUBCASES | Root del frame sin subTest | Subcaso ROOT_FRAME, actores/intentos diferenciados por objetos y keys observadas. |
| CT42 | SUBCASES | subTest activo exacto de unittest pinneado | Leer campos de memoria cerrados, sin reemplazar context manager ni llamar id/repr. |
| CT43 | SUBCASES | Parámetros permitidos ytipos escalares | Sólo ocho nombres inventariados y valores acotados; mensaje/raw y valores desconocidos no se publican. |
| CT44 | SUBCASES | SubTest anidado | Recorrido de mapas exactos y precedencia, hasta profundidad32; sin __iter__/getitem de usuario. |
| CT45 | SUBCASES | Callback addSubTest original | Vincular mismo objeto al resultado observado; no tests nuevos por subcaso. |
| CT46 | SUBCASES | Hilo distinto al del test | Thread ref explícito, no heredar subTest por suposición; missing si falta correlación necesaria. |
| CT47 | SUBCASES | ID de objeto reutilizado o contexto reemplazado | Referencias propias acotadas por lifecycle, detectar cambio y no fusionar. |
| CT48 | SUBCASES | Store/result varios bajo mismo frame | No construir secuencia por orden de listas; keys de run/store/subcaso y llamadas/protocolo. |
| CT49 | CHILD_PROTOCOL | start/spawn original retorna proceso/conexión | Registrar sólo objetos y metadata permitida del padre tras retorno; no actor/canal nuevo. |
| CT50 | CHILD_PROTOCOL | receive/recv de conexión registrada retorna READY | Correlacionar por conexión/intento; distinguir punto esperado del mensaje observado. |
| CT51 | CHILD_PROTOCOL | recv de conexión ajena | Delegar sin observar ni registrar payload; sin lectura extra o cambio de identidad. |
| CT52 | CHILD_PROTOCOL | OK/ERROR/snapshot del protocolo existente | Proyección cerrada; código recibido ya es dato, no str nuevo de la excepción. |
| CT53 | CHILD_PROTOCOL | join/finish original produjo returncode | Leer dato escalar ya producido con stdlib exacta; no poll/wait/is_alive extra. |
| CT54 | CHILD_PROTOCOL | Proceso pendiente después de join con timeout | PENDING/INCOMPLETE; no esperar, matar o afirmar cero desde observer. |
| CT55 | CHILD_PROTOCOL | CID generado sólo en hijo que muere antes de emitirlo | CHILD_LOCAL_NOT_OBSERVED; ParentIntentID nunca command_id; negativos cerrados requieren protocolo y no efecto observados. |
| CT56 | CHILD_PROTOCOL | Efecto confirmado sin recibo/identidad observables | Missing obligatorio; ACK/READY/código de exit no lo sustituyen. |
| CT57 | LINKS_HASH_DOMAINS | Igualdad exacta run/store/frame/subcaso | Enlace sólo dentro de captura y autoridad compatibles; no por nombre/UUID de expediente. |
| CT58 | LINKS_HASH_DOMAINS | Recibo de comando y oráculo del mismo Store | Ligar mediante command/request/seq/head observados donde existan; conflicto invalida. |
| CT59 | LINKS_HASH_DOMAINS | after_data_sha256 vs state_sha256 de oráculo | Dominios diferentes: after_data antes de insertar recibo, oracle incluye receipts. Nunca igualdad automática. |
| CT60 | LINKS_HASH_DOMAINS | Oracle.commit/head ySnapshot.head | Comparar sólo mismo algoritmo/schema/seq/Store; no sustituir un hash de otra autoridad. |
| CT61 | LINKS_HASH_DOMAINS | Frontera etiquetada,checkpoint esperado o READY | Etiquetas tipadas; sin elevarlas a fsync nativo o gate medido directamente en hijo. |
| CT62 | LINKS_HASH_DOMAINS | Replay,múltiples comandos/variantes/concurrencia | Conservar todas las identidades yconflictos; no elegir por posición/fecha. |
| CT63 | LINKS_HASH_DOMAINS | Input/entorno/método/oráculo/assert/result | Cadena con referencias verificables y predicado original observado; hash/source no crea valor ausente. |
| CT64 | LINKS_HASH_DOMAINS | Puntero huérfano/duplicado/ciclo o asociación ambigua | Bloquear, no emparejar por cercanía ni por estar en el mismo test solamente. |
| CT65 | PASSIVE_OBSERVATION | Wrapper retorna normalmente | Una llamada original, identidad de retorno intacta; sólo lectura exacta de argumentos/retornos ya producidos. |
| CT66 | PASSIVE_OBSERVATION | Wrapper original lanza | Misma excepción/outcome; fallo de instrumentación queda latcheado, no en producto. |
| CT67 | PASSIVE_OBSERVATION | Sin hooks/checkpoints/disco auxiliares | No envolver ni invocar checkpoints; no reenviar, snapshot/reopen/lookup/FS ni crash nuevos. |
| CT68 | PASSIVE_OBSERVATION | Callbacks anidados y alias de métodos | Punteros exactos/firma/source; una observación por límite, no doble invocación de fachada. |
| CT69 | PASSIVE_OBSERVATION | Captura ante fallo de instrumentación | Finalizar llamada/test/cleanup y parar entre tests; no rellenar evento final. |
| CT70 | PASSIVE_OBSERVATION | Restauración o binding tardío cambian | Detectar sustitución; restaurar objetos propios exactos ypreservar primer fallo. |
| CT71 | PASSIVE_OBSERVATION | Stdlib/private fields fuera del pin exacto | Rechazar API, sin fallback genérico a properties/str/repr. |
| CT72 | PASSIVE_OBSERVATION | Código/env del nuevo perfil | Namespace/registro propios; globals y fuentes I70/I73/I76/I79/harness/producto intactos. |
| CT73 | BOUNDS | Metadato de evento supera4KiB | Invalidar sin truncar o dividir un objeto semántico para eludir límite. |
| CT74 | BOUNDS | 131072 eventos o2048/test acumulados | Mismos topes, incluso eventos causales nuevos; ratios I80 no prueban capacidad. |
| CT75 | BOUNDS | Páginas/sidecar/raw/contexto/paquete | 32x2MiB,64MiB páginas,12MiB cada canal,112MiB+4KiB y37 miembros; retención dentro del sidecar. |
| CT76 | BOUNDS | Frames4096/refs16384/depth32/string4096 | Incluye subcasos, procesos, oráculos y enlaces nuevos; no cuota paralela. |
| CT77 | BOUNDS | Hash/JSON de args/retornos uoráculo | Operand16MiB por valor con charging acumulado; tipos exactos, no repr ni payload publicado. |
| CT78 | BOUNDS | Lectores de inputs/evidencia | 128MiB únicos/256MiB leídos por ámbito; runtime pins específicos, sin reset o unión de historia no ejecutada. |
| CT79 | BOUNDS | Tiempo300s componente/900s futuro ylímites menores | Sin ampliar kernel/runner/hijo/hook; detener presupuesto y presentar ajuste. |
| CT80 | BOUNDS | Peor frame I80 DR23 1377 eventos | Suplemento propuesto sólo terminal, sin CALL_START adicional ni checkpoint; validar cuota, no garantizar que cabe. |
| CT81 | READER_DIAGNOSTIC | Retained_oracles yeventos de cabecera | Schema versionado, hash/puntero/tipos exactos en recorrido acotado, sin objetos globales ilimitados. |
| CT82 | READER_DIAGNOSTIC | Sidecar normal yfallo anterior a raw | Conservar diagnóstico I78 de4096 bytes en canal existente; no confundir error artifact con causa. |
| CT83 | READER_DIAGNOSTIC | Escritura parcial o diagnóstico ausente | Preservar parcial, no append/overwrite ni causa inventada desde AST. |
| CT84 | READER_DIAGNOSTIC | Resumen/puntero no concuerda con digest de fila | INVALID_CAPTURE; contador o PASS no lo rehabilitan. |
| CT85 | READER_DIAGNOSTIC | Completitud por test ysubcaso | Propagar missing de campo obligatorio, huérfano o rama incompatible al grupo/campaña. |
| CT86 | READER_DIAGNOSTIC | N/A con motivo genérico para tipo no soportado | Rechazar; sólo control/negativo cerrado previamente según campo yselector. |
| CT87 | READER_DIAGNOSTIC | Frontera yresultado conservan autoridades distintas | EXPECTED_SOURCE,OBSERVED_PARENT,CHILD_PROTOCOL,RETAINED_ORACLE no intercambiables. |
| CT88 | READER_DIAGNOSTIC | Captura nueva completa | Sólo TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW; IR03 requiere revisión separada. |
| CT89 | PRESERVATION | CT96 usa clases/módulos/child producers nuevos | Cero imports de producto/runners yde PF60/PG64/AT80/LB64; temporales propios ysentinels preservados. |
| CT90 | PRESERVATION | I83 finaliza conPASS | No crear autoridad/destino I84 ni ejecutar P01/P02–P10. |
| CT91 | PRESERVATION | P01 futuro completo | 321/12 en destino nuevo, sin sumar I71/I74/I80 ni recuperar sus datos ausentes. |
| CT92 | PRESERVATION | I81 mantiene83/1 yUI04.1 parcial | Contrato, componente ycaptura no cambian dictamen automáticamente. |
| CT93 | PRESERVATION | Historia ycierres anteriores | Bytes sellados intactos; D1–D4/hito local aceptado y30/35 sin promoción. |
| CT94 | PRESERVATION | P0 yrequisitos reales/humanos | Sin proveedor/credenciales/corpus real, consumo/reservas, activación/promoción/despliegue/D6. |
| CT95 | PRESERVATION | Publicación o acceso remoto | Separados del alcance; sin push ni lectura remota en I82. |
| CT96 | PRESERVATION | Nueva incompatibilidad de API/oráculo/budget | Conservar ydetener; presentar ajuste antes de ampliar, repetir o promover suficiencia. |

## Inventario por test/subcaso

118 IDs exactos en el JSON:48 T,40 R,30 Drive;110 de dominio, cinco controles sin Store, dos negativos de construcción Store yDI28 negativo Drive.203 tests restantes conservan el perfil previo sin crédito causal nuevo. El cierre estático de helpers identifica13 métodos con subTest y ocho nombres de parámetro; no mide ramas o multiplicidades runtime. Cada fila conserva source/callsites tipados como expectativa, enlace I80 y requisitos condicionales.

Los254 oráculos T/37 frames,221 R,43 crash R y114 snapshots Drive son referencias I80, no una cuota que rellenar. Toda falta obligatoria bloquea; CT96 no promete resolver UI04.1. P0,83/1 yglobales OPEN; sin implementación/captura/publicación.
