# I78 — matriz propuesta LB01–LB64

[Contrato](D5-I78-LATE-BINDING-DESIGN.md) · [Selectores, pins y esquema cerrado](../validation/D5-I78-design-review.json) · [Integridad](../validation/D5-I78-integrity.json).

64 casos **NOT_RUN**, propuestos para I79 sólo sintético bajo 300 segundos externos. No se importan clases de producto/runners ni se reejecutan PG64/AT80. Cada caso futuro deberá enlazar método AST, raw, comando/contexto, hashes pre/post y resultado observado; no completar por conteo ni expectativa de fuente.

| Caso | Familia | Disparador | Oráculo exigido |
|---|---|---|---|
| LB01 | AUTHORITY | Falta autoridad humana futura I80, aunque existe I77 | Bloquear antes de importar runner/producto o crear proceso funcional; no reutilizar I77. |
| LB02 | AUTHORITY | Pins de contrato, registro, código o evidencia alterados | STALE_AUTHORITY/STALE_INPUTS; no aprender hashes durante captura. |
| LB03 | AUTHORITY | Scope, IDs, grupos o políticas distintos de P01 sellado | Rechazar; conservar 321 IDs/12 grupos, siete políticas I72 y scopes I75. |
| LB04 | AUTHORITY | Import de componentes o modo plan | NOT_RUN_I80_AUTHORIZATION_REQUIRED, cero imports históricos y cero campañas. |
| LB05 | AUTHORITY | Sólo se aprueba diseño I78 | No crear namespace/registro/autoridad/paquete funcional ni ejecutar componentes. |
| LB06 | AUTHORITY | I79 sólo componentes sintéticos | No importar producto/runners, ni reejecutar PG64/AT80 ni P01/P02–P10. |
| LB07 | AUTHORITY | Autoridad coherente controlada por caller | Puerta de coherencia, no atestación independiente ni autorización humana por JSON. |
| LB08 | AUTHORITY | Destino futuro existente, symlink o path arbitrario | Rechazar sin overwrite de I71/I74/I77; nuevo destino fijo exclusivo. |
| LB09 | BINDING_TIMING | PlaneError ausente al importar el runner sintético | Crear resolver con builtin dict; no exigir todas las clases antes de main. |
| LB10 | BINDING_TIMING | Discovery normal carga clase antes del primer rol permitido | Resolver entonces desde sys.modules, sin import ni discovery auxiliar. |
| LB11 | BINDING_TIMING | EligibilityError ya estaba cargada | Resolver sólo al rol correspondiente; mismo contrato que carga tardía. |
| LB12 | BINDING_TIMING | Operando builtin-only o Path sin referencia a clase | Delegar digest/proyección sin resolver clases innecesarias. |
| LB13 | BINDING_TIMING | ID/helper/slot fuera de whitelist | No resolver ni extender; comportamiento anterior y propagación de missing. |
| LB14 | BINDING_TIMING | Módulo sigue ausente al primer uso permitido | CLASS_MODULE_NOT_LOADED en latch; preservar retorno original y detener entre tests. |
| LB15 | BINDING_TIMING | Clase permitida nunca requerida por operandos observados | No exigirla en finish por expectativa estática; inventario/missing mantienen sus guardas. |
| LB16 | BINDING_TIMING | Dos clases se requieren en momentos distintos | Estados independientes UNRESOLVED/BOUND/INVALID; no reset ni cambio por orden. |
| LB17 | BINDING_IDENTITY | Clase exacta y fuente pinneada disponibles | type exactamente type, base ValueError, módulo/nombre y hash de fuente exactos. |
| LB18 | BINDING_IDENTITY | Export sustituido tras primer binding | CLASS_BINDING_CHANGED; conservar primera identidad y no rebind automático. |
| LB19 | BINDING_IDENTITY | Objeto módulo sustituido en sys.modules | Invalidar antes/después de proyección y en finish, aunque nombre/hash coincidan. |
| LB20 | BINDING_IDENTITY | Fuente alterada antes o después del binding | STALE_CLASS_SOURCE/STALE_INPUTS; no resolver desde fuente nueva. |
| LB21 | BINDING_IDENTITY | Subclase, metaclass custom o clase con nombre parecido | Rechazar sin __instancecheck__/__subclasscheck__/repr/str de usuario. |
| LB22 | BINDING_IDENTITY | Dos objetos clase distintos comparten nombre | Aceptar sólo objeto exportado exacto; no homologar por strings. |
| LB23 | BINDING_IDENTITY | Módulo eliminado o clase reemplazada al finalizar | Finalización invalida; no aceptar witnesses anteriores como coherencia global. |
| LB24 | BINDING_IDENTITY | Resolver consulta varias veces el mismo binding | Comprobar binding original; lector acumulado y referencias acotados, sin reimport. |
| LB25 | OBSERVATION | Assertion original retorna en rol permitido | Una llamada original; resolver/proyectar después, sin reevaluar predicado. |
| LB26 | OBSERVATION | Assertion original lanza | Conservar misma excepción y outcome; no generar witness exitoso ni forzar binding. |
| LB27 | OBSERVATION | Fallo de resolver/proyector durante callback | Latch fuera de stream, sin excepción instrumental al producto; parada segura entre tests. |
| LB28 | OBSERVATION | Dict builtin y clase dict | Digest I70 del valor intacto; witness sólo para objeto clase permitido. |
| LB29 | OBSERVATION | Instancias exactas PlaneError/EligibilityError | Sólo tipo/args permitidos, etiqueta de proyección parcial; sin objeto completo. |
| LB30 | OBSERVATION | Path escalar, tuple(Path,str), list(Path) | Mismos tags, HMAC efímero, encoding y scope I75; sin FS ni claves/rutas publicadas. |
| LB31 | OBSERVATION | Snapshots Drive y DI28 | 29 scopes snapshot y constructor negativo separados de Store; sin crédito adicional por late binding. |
| LB32 | OBSERVATION | Subtests, skip, fallos y restauración | Conservar resultados, callbacks y punteros exactos; record/return digests I70 intactos. |
| LB33 | DIAGNOSTICS | Worker completa captura e informe válido | Diagnóstico COMPLETED/COMPLETE/OK sólo tras finalización; no equivale a suficiencia. |
| LB34 | DIAGNOSTICS | Fallo previo a entrypoint tras validar capacidad | Envelope FAILED con fase/código cerrados, raw/sidecar funcional no inventados. |
| LB35 | DIAGNOSTICS | CaptureFault con código permitido | Emitir sólo literal de allowlist; nunca mensaje, args o traceback de excepción. |
| LB36 | DIAGNOSTICS | Excepción desconocida o código no permitido | SANITIZED_WORKER_ERROR fijo; sin str/repr de la excepción. |
| LB37 | DIAGNOSTICS | Binding falla dentro de ENTRYPOINT | Primer fallo latcheado conserva fase/código; diagnóstico no se sustituye por FINALIZE/OK. |
| LB38 | DIAGNOSTICS | Múltiples fallos durante cleanup/finalización | Primera causa conservada; causas secundarias sólo códigos cerrados acotados del contexto. |
| LB39 | DIAGNOSTICS | Raw vacío con diagnóstico válido | BLOCKED_WORKER_FAILURE; artifact_error separado, sin enmascarar código observado con INVALID_JSON. |
| LB40 | DIAGNOSTICS | Worker muere sin diagnóstico, como pérdida del canal | WORKER_DIAGNOSTIC_NOT_RECORDED y causa interna desconocida; no rellenar desde AST. |
| LB41 | CHANNELS | Diagnóstico antes de validar autoridad y capacidad de escritura | No usar fd no confiable ni crear archivos; registrar ausencia desde padre. |
| LB42 | CHANNELS | READY/RELEASE con nonce/PID/PGID/fds/directorio correctos | Correlación exacta; sólo proceso/grupo/capacidad propios. |
| LB43 | CHANNELS | Nonce/PID/PGID/capture_run_id incoherentes en diagnóstico | INVALID_WORKER_DIAGNOSTIC; no conceder crédito a envelope bien formado pero ajeno. |
| LB44 | CHANNELS | Envelope con campos extra, fase/código/schema/tipos inválidos | Rechazo estricto y sanitizado; nunca publicar valores no validados. |
| LB45 | CHANNELS | Fallo antes de empezar escritura final del sidecar | Emitir un único JSON de fallo por sidefd existente; no nuevo archivo/pipe/stderr retenido. |
| LB46 | CHANNELS | Escritura final ya comenzó y falla parcialmente | No append de segundo JSON ni overwrite; preservar parcial y causa no registrada si falta. |
| LB47 | CHANNELS | EOF, timeout, proceso hijo o canal pendiente | Sólo parar grupo propio, confirmar retirada; si no se confirma bloquear sin afirmar cero. |
| LB48 | CHANNELS | Diagnóstico válido pero raw/sidecar/exit no concuerdan | Separar diagnóstico válido de captura inválida; ninguna promoción por presencia de OK. |
| LB49 | BOUNDS | Diagnóstico serializado excede 4096 bytes | Rechazar antes de escribir; campos cerrados no permiten expansión arbitraria. |
| LB50 | BOUNDS | Diagnóstico dentro de sidecar de 12MiB | Cuenta en cuota existente; no canal, archivo o presupuesto adicional. |
| LB51 | BOUNDS | Paquete completo y copia launcher | Mismo máximo 37 miembros lógicos y 112MiB+4KiB; fracaso mínimo también contabiliza. |
| LB52 | BOUNDS | 131072 eventos/campaña y 2048/test | Topes sin cambio y counters acumulados; resolver/diagnóstico no los reinician. |
| LB53 | BOUNDS | Páginas de 2MiB, hasta32 y64MiB acumulados | Mismos rangos/hashes/lifecycle; no cortar eventos ni completar metadata ausente. |
| LB54 | BOUNDS | Inputs/evidencia releídos por binding/finalización | Mismos 128MiB únicos/256MiB leídos acumulados por ámbito, sin lector nuevo para eludir topes. |
| LB55 | BOUNDS | Frames4096, refs16384, depth32, string4096, operand16MiB | Binding acotado a tres clases y ledger a fases fijas; cuotas previas intactas. |
| LB56 | BOUNDS | Tiempo de componentes300s/futuro900s o límite menor | No ampliar runner/hijo/hook ni añadir actores; bloqueo y preservación. |
| LB57 | PRESERVATION | Fixtures y proceso productor sintéticos nuevos | Cero imports de producto/runners/PG64/AT80; temporales propios y sentinels preservados. |
| LB58 | PRESERVATION | Productor sintético reproduce carga tardía y fallo temprano | Ejercitar worker/launcher nuevos sin entrypoint histórico ni campaña funcional. |
| LB59 | PRESERVATION | I71/I74/I77 y evidencia I76 existentes | Bytes y hashes intactos; diagnóstico nuevo no rellena retrospectivamente I77. |
| LB60 | PRESERVATION | RAW PASS parcial o conteos sin metadata | Sin completitud/suficiencia por suma; inventario/transportes/resultados separados. |
| LB61 | PRESERVATION | Captura futura completa y íntegra | Como máximo TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW; no cierre automático. |
| LB62 | PRESERVATION | Publicación del diseño o componentes | Separada del alcance; sólo I52 publicado y sin acceso remoto nuevo. |
| LB63 | PRESERVATION | Estado D1–D4/hito local y81/3 | Inmutable; UI01.2/UI04.1/UI09.2 PARTIAL y D5 global/H07/G01–G07/GI abiertos. |
| LB64 | PRESERVATION | Reaparece incompatibilidad de API/oráculo/presupuesto | Conservar intento, detener y presentar ajuste concreto; sin retry/whitelist/techo automáticos. |

La matriz no confirma retrospectivamente el error de I77. I79 requerirá aprobación separada; I80 exigiría otra para P01 completo en destino nuevo. Ninguna fase publica o cierra criterios. P0,81/3 y estados globales abiertos.
