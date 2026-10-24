# D5 I49 — matriz de incertidumbre durable

Fecha: **2026-10-24**. **PREPARED_FOR_REVIEW**. [Contrato](D5-I49-DURABLE-UNCERTAINTY-DESIGN.md) · [Sello y fuentes](../validation/D5-I49-design-review.json).

**24 métodos propuestos; todos NOT_RUN, semántica NOT_REVIEWED.** Cada fila corresponde a un recorrido explícito, sin multiplicar escenarios o controles internos como tests. Estas son obligaciones del futuro harness, no resultados ni cobertura global aceptada.

| ID | Recorrido / clase | Familia / disparador | Oráculo requerido | Límite semántico |
|---|---|---|---|---|
| UQ01 | T / NATIVE | LOOKUP_EMPTY: ISSUE sin entrega; lookup real devuelve None | UNKNOWN/ledger2/queries1, un intento; pending send conservado; REMOTE sin entidad/prueba | Ausencia por ticket, no colección de cero matches ni prueba de no efecto |
| UQ02 | R / NATIVE | LOOKUP_EMPTY: ISSUE sin entrega; lookup real devuelve None | UNKNOWN/ledger2/queries1, un intento; pending send conservado; REMOTE sin entidad/prueba | Ausencia por ticket, no colección de cero matches ni prueba de no efecto |
| UQ03 | T / INJECTABLE_NEGATIVE | LOOKUP_ERROR_EMPTY: ISSUE sin entrega; wrapper lookup lanza OSError antes de llamar al lookup real | UNKNOWN/2/1, send pending; lookup real=0; ninguna escritura REMOTE | Excepción de transporte sintética; no respuesta HTTP ni 429 |
| UQ04 | R / INJECTABLE_NEGATIVE | LOOKUP_ERROR_EMPTY: ISSUE sin entrega; wrapper lookup lanza OSError antes de llamar al lookup real | UNKNOWN/2/1, send pending; lookup real=0; ninguna escritura REMOTE | Excepción de transporte sintética; no respuesta HTTP ni 429 |
| UQ05 | T / INJECTABLE_NEGATIVE | EXECUTE_ERROR_BEFORE: dispatch público; wrapper execute lanza OSError sin invocar execute real | ISSUE+RESULT(None): UNKNOWN/2/queries0; no entidad/ticket REMOTE; rechazo de retry conserva HEAD | Posible entrega desconocida desde CLIENT; saber que fixture no ejecutó no autoriza retry |
| UQ06 | R / INJECTABLE_NEGATIVE | EXECUTE_ERROR_BEFORE: dispatch público; wrapper execute lanza OSError sin invocar execute real | ISSUE+RESULT(None): UNKNOWN/2/queries0; no entidad/ticket REMOTE; rechazo de retry conserva HEAD | Posible entrega desconocida desde CLIENT; saber que fixture no ejecutó no autoriza retry |
| UQ07 | T / INJECTABLE_NEGATIVE | EXECUTE_ERROR_AFTER: dispatch público; execute real publica P y wrapper lanza OSError al retornar | UNKNOWN/2/0 con un efecto REMOTE v1; reapertura no consulta; reconcile explícita confirma ledger3/queries1 sin execute | Pérdida de respuesta tras efecto demostrado, no semántica HTTP 429 |
| UQ08 | R / INJECTABLE_NEGATIVE | EXECUTE_ERROR_AFTER: dispatch público; execute real publica P y wrapper lanza OSError al retornar | UNKNOWN/2/0 con un efecto REMOTE v1; reapertura no consulta; reconcile explícita confirma ledger3/queries1 sin execute | Pérdida de respuesta tras efecto demostrado, no semántica HTTP 429 |
| UQ09 | T / INJECTABLE_NEGATIVE | LOOKUP_ERROR_WITH_PROOF: ISSUE sin entrega, execute real del ticket emitido; wrapper lookup oculta P mediante OSError antes de lookup real | UNKNOWN/2/1 y send pending con REMOTE intacto; nueva reconcile real confirma ledger3/queries2, cero execute durante consultas | La prueba existe pero no se observó en la primera consulta |
| UQ10 | R / INJECTABLE_NEGATIVE | LOOKUP_ERROR_WITH_PROOF: ISSUE sin entrega, execute real del ticket emitido; wrapper lookup oculta P mediante OSError antes de lookup real | UNKNOWN/2/1 y send pending con REMOTE intacto; nueva reconcile real confirma ledger3/queries2, cero execute durante consultas | La prueba existe pero no se observó en la primera consulta |
| UQ11 | T / INJECTABLE_NEGATIVE | LIST_DUPLICATE_PROOFS: Una P válida del ticket emitido; proof_hook devuelve [P,P] sobre reconcile real | CONFLICT/2/queries1, hard_conflict=true; ningún efecto adicional; prueba correcta posterior no limpia conflicto | Lista incompatible con proof_ok; NO acredita colección múltiple válida del dominio |
| UQ12 | R / INJECTABLE_NEGATIVE | LIST_DUPLICATE_PROOFS: Una P válida del ticket emitido; proof_hook devuelve [P,P] sobre reconcile real | CONFLICT/2/queries1, hard_conflict=true; ningún efecto adicional; prueba correcta posterior no limpia conflicto | Lista incompatible con proof_ok; NO acredita colección múltiple válida del dominio |
| UQ13 | T / INJECTABLE_NEGATIVE | MATCH_ENVELOPE: proof_hook devuelve dict(matches=[match,match],proof=P) sobre reconcile real | CONFLICT/2/queries1 persistente al observar después P correcta; REMOTE no cambia | Envelope ajeno al schema durable, NO consulta nativa de múltiples resultados; match sintético sólo negativo |
| UQ14 | R / INJECTABLE_NEGATIVE | MATCH_ENVELOPE: proof_hook devuelve dict(matches=[match,match],proof=P) sobre reconcile real | CONFLICT/2/queries1 persistente al observar después P correcta; REMOTE no cambia | Envelope ajeno al schema durable, NO consulta nativa de múltiples resultados; match sintético sólo negativo |
| UQ15 | T / INJECTABLE_NEGATIVE | WRONG_TICKET: proof_hook copia P y cambia únicamente ticket por UUID sintético distinto | CONFLICT/2/queries1, hard_conflict; P correcta posterior conserva bloqueo; sin adopción | Control de correlación existente repetido, no nuevo caso de múltiples coincidencias |
| UQ16 | R / INJECTABLE_NEGATIVE | WRONG_TICKET: proof_hook copia P y cambia únicamente ticket por UUID sintético distinto | CONFLICT/2/queries1, hard_conflict; P correcta posterior conserva bloqueo; sin adopción | Control de correlación existente repetido, no nuevo caso de múltiples coincidencias |
| UQ17 | T / NATIVE | RATE_LIMIT_CONCLUSIVE: dispatch reject=RATE_LIMIT, retry_tick=5; retry antes del tick y tras CLOCK 5 | NO_EFFECT/2 y proof correlacionada sin entidad; antes RETRY_NOT_ELIGIBLE; tras tick un retry explícito emite ticket nuevo y un único efecto | RATE_LIMIT con prueba de no efecto; no ambigüedad HTTP. Nunca retry automático |
| UQ18 | R / NATIVE | RATE_LIMIT_CONCLUSIVE: dispatch reject=RATE_LIMIT, retry_tick=5; retry antes del tick y tras CLOCK 5 | NO_EFFECT/2 y proof correlacionada sin entidad; antes RETRY_NOT_ELIGIBLE; tras tick un retry explícito emite ticket nuevo y un único efecto | RATE_LIMIT con prueba de no efecto; no ambigüedad HTTP. Nunca retry automático |
| UQ19 | T / NATIVE | RATE_LIMIT_NO_DELAY: dispatch reject=RATE_LIMIT, retry_tick=None; CLOCK 5 y retry explícito | NO_EFFECT/2 con proof, sin entidad; RETRY_NOT_ELIGIBLE aun pasado el tick y sin nuevo ticket/recibo de intento | Prueba no equivale a elegibilidad; None no concede espera cero |
| UQ20 | R / NATIVE | RATE_LIMIT_NO_DELAY: dispatch reject=RATE_LIMIT, retry_tick=None; CLOCK 5 y retry explícito | NO_EFFECT/2 con proof, sin entidad; RETRY_NOT_ELIGIBLE aun pasado el tick y sin nuevo ticket/recibo de intento | Prueba no equivale a elegibilidad; None no concede espera cero |
| UQ21 | T / CONTROL | OWNERSHIP_PASSIVE: Nuevo lector de archivos y CLIENT en proceso spawn; negativos inode/marker/sentinel/link restaurados | Lectura pasiva no modifica HEAD/estado ni consulta/ejecuta; limpieza sólo raíz propia; restantes cero | Control repetido de propiedad/reapertura; no SIGKILL ni recuperación nueva |
| UQ22 | R / CONTROL | OWNERSHIP_PASSIVE: Nuevo lector de archivos y CLIENT en proceso spawn; negativos inode/marker/sentinel/link restaurados | Lectura pasiva no modifica HEAD/estado ni consulta/ejecuta; limpieza sólo raíz propia; restantes cero | Control repetido de propiedad/reapertura; no SIGKILL ni recuperación nueva |
| UQ23 | T / CONTROL | INVENTORY_RAW: Negativos entradas cambiadas/añadidas, raw faltante/incompatible/hash, IDs duplicados/omitidos/skips/residuos y budgets reducidos | Guardas rechazan; mapa UQ01–UQ24 exacto; contexto y hashes pre/post; campañas separadas | Metacontrol no suma escenarios/probes como tests ni completa UI20.3 |
| UQ24 | R / CONTROL | INVENTORY_RAW: Negativos entradas cambiadas/añadidas, raw faltante/incompatible/hash, IDs duplicados/omitidos/skips/residuos y budgets reducidos | Guardas rechazan; mapa UQ01–UQ24 exacto; contexto y hashes pre/post; campañas separadas | Metacontrol no suma escenarios/probes como tests ni completa UI20.3 |

## Capacidades no representadas por este modelo

Estas tres filas no son tests, no reciben PASS y no autorizan implementación de capacidad. UI20.3 permanece PARTIAL. MG03 es una capacidad eventual ajena a este contrato; no añade una obligación de adopción o selección a UI20.3.

| ID | Obligación | Límite | Estado |
|---|---|---|---|
| MG01 | Colección de múltiples coincidencias válidas T/R | lookup devuelve una prueba por ticket; lista/envelope rechazados no ensayan una colección válida | MODEL_GAP; NO_NATIVE_MODEL; sin cierre |
| MG02 | 429 ambiguo durable con semántica de transporte | No existe status HTTP ni metadata de respuesta 429 en API durable; OSError sólo representa falta de prueba | MODEL_GAP; NO_NATIVE_MODEL; sin cierre |
| MG03 | Persistencia del conjunto ambiguo y selección/adopción explícita | No hay contrato de conjunto ni autoridad para adoptar; no inventar campos/migraciones/reglas de selección | MODEL_GAP; NO_NATIVE_MODEL; sin cierre |

## Criterios de lectura de la evidencia futura

- H07/UI20.3: las secuencias de incertidumbre podrán aportar soporte acotado; las colecciones válidas y HTTP429 continúan fuera del modelo. No convertir formato inválido en equivalencia de dominio.
- GI33/GI34: metadatos nuevos ayudan a trazabilidad futura; no reconstruyen raw/contexto histórico ni inventarían exhaustivamente targets D1–D4.
- GI38: oráculos de una misma secuencia/run/store/ticket, con reapertura y consulta explícita; sin declarar nuevas caídas o cierre de cada frontera.
- GI39: sin nuevas carreras, dos tickets autorizados, origen/perfil/cuenta o variaciones relacionales inferidas de UQ.
- GI40: presupuestos propios, contadores y límites de host explícitos; ningún permiso operacional o despliegue.

Todos los casos conservarán baseline/revisión/procedencia T/R, no efecto por lookup, transporte real frente a wrapper, estado de ledger/pending, recursos y campos raw según contrato. Regresiones separadas; cero ejecuciones realizadas en I49.
