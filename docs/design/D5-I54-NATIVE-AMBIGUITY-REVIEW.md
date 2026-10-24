# D5 I54 — matriz de ambigüedad durable nativa

Fecha: **2026-10-24**. **PREPARED_FOR_REVIEW**.
[Contrato](D5-I54-NATIVE-AMBIGUITY-DESIGN.md) · [Sello](../validation/D5-I54-design-review.json).

**36 métodos propuestos, todos NOT_RUN / NOT_REVIEWED.** 32 filas de dominio y cuatro controles. Cada fila es un test, con subvariantes internas sin incrementar conteo. Todas mantienen la misma identidad de secuencia y reapertura independiente del contrato; CREATE de una TASK, no UPDATE/CLOSE. T conserva I26; R conserva lote/recibo/selección propios. Un catálogo observado nunca cuenta como segunda entidad creada por un ticket autorizado.

| ID | Variante | Familia / disparador | Oráculo exigido |
|---|---|---|---|
| NA01 | NATIVE_T | EMPTY_VIEW: Vista eventual vacía sin P; ISSUE sin entrega → QUERY/OBSERVE | UNKNOWN/ledger2/queries1, pending send conservado; no efecto ni retry; reopen pasivo idéntico. |
| NA02 | NATIVE_R | EMPTY_VIEW: Vista eventual vacía sin P; ISSUE sin entrega → QUERY/OBSERVE | UNKNOWN/ledger2/queries1, pending send conservado; no efecto ni retry; reopen pasivo idéntico. |
| NA03 | NATIVE_T | SINGLE_UNPROVEN: Una coincidencia del catálogo válida sin P de ticket | UNKNOWN/2/1, no adopción; catálogo no es efecto emitido; ausencia de P bloquea retry. |
| NA04 | NATIVE_R | SINGLE_UNPROVEN: Una coincidencia del catálogo válida sin P de ticket | UNKNOWN/2/1, no adopción; catálogo no es efecto emitido; ausencia de P bloquea retry. |
| NA05 | NATIVE_T | SINGLE_EXACT_PROOF: ISSUE sin entrega → execute_response SUCCESS real → query normal → OBSERVE | P exacta + match compatible, EFFECT_CONFIRMED/2/1, entidad única v1, pending vacío; consulta no escribe REMOTE. |
| NA06 | NATIVE_R | SINGLE_EXACT_PROOF: ISSUE sin entrega → execute_response SUCCESS real → query normal → OBSERVE | P exacta + match compatible, EFFECT_CONFIRMED/2/1, entidad única v1, pending vacío; consulta no escribe REMOTE. |
| NA07 | NATIVE_T | MULTIPLE_UNPROVEN: DECLARE_VIEW con dos IDs distintos; subvariante ID repetido; sin P | CONFLICT/hard_conflict/2/1, una observación con colección íntegra; no selección ni efecto core; retry bloqueado. |
| NA08 | NATIVE_R | MULTIPLE_UNPROVEN: DECLARE_VIEW con dos IDs distintos; subvariante ID repetido; sin P | CONFLICT/hard_conflict/2/1, una observación con colección íntegra; no selección ni efecto core; retry bloqueado. |
| NA09 | NATIVE_T | MULTIPLE_WITH_PROOF: CREATE real del ticket; catálogo múltiple con P exacta; después vista limpia y otra query | Primer OBSERVE CONFLICT/2/1, P no adoptada; segundo CONFLICT/3/2, historial intacto y un único efecto core. |
| NA10 | NATIVE_R | MULTIPLE_WITH_PROOF: CREATE real del ticket; catálogo múltiple con P exacta; después vista limpia y otra query | Primer OBSERVE CONFLICT/2/1, P no adoptada; segundo CONFLICT/3/2, historial intacto y un único efecto core. |
| NA11 | NATIVE_T | FOREIGN_MATCH: Un match de key/scope ajeno, envelope exterior correlacionado | CONFLICT/hard_conflict/2/1, sin adopción; registrar identidad ajena; sólo operaciones de catálogo modifican catálogo. |
| NA12 | NATIVE_R | FOREIGN_MATCH: Un match de key/scope ajeno, envelope exterior correlacionado | CONFLICT/hard_conflict/2/1, sin adopción; registrar identidad ajena; sólo operaciones de catálogo modifican catálogo. |
| NA13 | NATIVE_T | FOREIGN_PROOF: Envelope bien formado pero prueba de otro ticket/M/store/variante | CONFLICT/hard_conflict/2/1, nunca cruzar T/R ni adoptar; reapertura conserva conflicto. |
| NA14 | NATIVE_R | FOREIGN_PROOF: Envelope bien formado pero prueba de otro ticket/M/store/variante | CONFLICT/hard_conflict/2/1, nunca cruzar T/R ni adoptar; reapertura conserva conflicto. |
| NA15 | NATIVE_T | AMBIGUOUS_429_BEFORE: Dispatch con AMBIGUOUS_429_BEFORE nativo → reapertura → query vacía explícita | UNKNOWN/2/0 sin pending send ni P/entidad; luego UNKNOWN/3/1; registro transporte durable no prueba NO_EFFECT. |
| NA16 | NATIVE_R | AMBIGUOUS_429_BEFORE: Dispatch con AMBIGUOUS_429_BEFORE nativo → reapertura → query vacía explícita | UNKNOWN/2/0 sin pending send ni P/entidad; luego UNKNOWN/3/1; registro transporte durable no prueba NO_EFFECT. |
| NA17 | NATIVE_T | AMBIGUOUS_429_AFTER: Dispatch AMBIGUOUS_429_AFTER con efecto real oculto → reopen → query normal | UNKNOWN/2/0 con entidad/P reales; luego EFFECT_CONFIRMED/3/1 del mismo ticket y cero execute en reconcile. |
| NA18 | NATIVE_R | AMBIGUOUS_429_AFTER: Dispatch AMBIGUOUS_429_AFTER con efecto real oculto → reopen → query normal | UNKNOWN/2/0 con entidad/P reales; luego EFFECT_CONFIRMED/3/1 del mismo ticket y cero execute en reconcile. |
| NA19 | NATIVE_T | QUERY_429_WITH_PROOF_HIDDEN: ISSUE sin entrega; execute SUCCESS real; DECLARE_VIEW modo query429; luego restaurar modo normal | Primera query UNKNOWN/2/1, segunda EFFECT_CONFIRMED/3/2; P oculta no adoptada antes; ambas consultas sin efectos. |
| NA20 | NATIVE_R | QUERY_429_WITH_PROOF_HIDDEN: ISSUE sin entrega; execute SUCCESS real; DECLARE_VIEW modo query429; luego restaurar modo normal | Primera query UNKNOWN/2/1, segunda EFFECT_CONFIRMED/3/2; P oculta no adoptada antes; ambas consultas sin efectos. |
| NA21 | NATIVE_T | AMBIGUOUS_RETRY_AFTER: Dispatch 429 BEFORE con retry_after_tick=5 → CLOCK5 → retry expreso y nuevo paquete/cid del binding | UNKNOWN/2/0; ningún retry/ISSUE nuevo aunque tick cumpla; rechazo BINDING_UNRESOLVED, HEAD sin cambio frente a cada petición. |
| NA22 | NATIVE_R | AMBIGUOUS_RETRY_AFTER: Dispatch 429 BEFORE con retry_after_tick=5 → CLOCK5 → retry expreso y nuevo paquete/cid del binding | UNKNOWN/2/0; ningún retry/ISSUE nuevo aunque tick cumpla; rechazo BINDING_UNRESOLVED, HEAD sin cambio frente a cada petición. |
| NA23 | NATIVE_T | CONCLUSIVE_RATE_LIMIT: Dispatch 429 con P NO_EFFECT RATE_LIMIT exacta y tick5; retry antes/después CLOCK5 | NO_EFFECT/2/0; antes RETRY_NOT_ELIGIBLE; después retry expreso mismo M/send, ticket nuevo, EFFECT_CONFIRMED/4/0, dos intentos y un efecto. |
| NA24 | NATIVE_R | CONCLUSIVE_RATE_LIMIT: Dispatch 429 con P NO_EFFECT RATE_LIMIT exacta y tick5; retry antes/después CLOCK5 | NO_EFFECT/2/0; antes RETRY_NOT_ELIGIBLE; después retry expreso mismo M/send, ticket nuevo, EFFECT_CONFIRMED/4/0, dos intentos y un efecto. |
| NA25 | NATIVE_T | INVALID_ENVELOPE: Estructura/tipos/status no admitido, hash response_id incorrecto, límite8/+1 y bytes; 429+P positiva o tick incoherente | Estructura inválida: error sin OBSERVE ni cambio HEAD/ledger (QUERY pendiente); combinación bien formada incompatible: CONFLICT; no confundir ambos resultados. |
| NA26 | NATIVE_R | INVALID_ENVELOPE: Estructura/tipos/status no admitido, hash response_id incorrecto, límite8/+1 y bytes; 429+P positiva o tick incoherente | Estructura inválida: error sin OBSERVE ni cambio HEAD/ledger (QUERY pendiente); combinación bien formada incompatible: CONFLICT; no confundir ambos resultados. |
| NA27 | NATIVE_T | OBSERVATION_REPLAY: Query con P exacta; OBSERVE cid fijo; replay idéntico y cid con envelope cambiado | Un recibo/observación/incremento; replay no rebobina; solicitud cambiada rechazada; ledger CAS vieja rechaza segundo OBSERVE distinto. |
| NA28 | NATIVE_R | OBSERVATION_REPLAY: Query con P exacta; OBSERVE cid fijo; replay idéntico y cid con envelope cambiado | Un recibo/observación/incremento; replay no rebobina; solicitud cambiada rechazada; ledger CAS vieja rechaza segundo OBSERVE distinto. |
| NA29 | NATIVE_T | CRASH_BEFORE_OBSERVE: QUERY emitida, P recibida, READY before_observe; SIGKILL y reopen; reconcile explícita nueva | Al abrir UNKNOWN/1/1 con send+qid pending, cero OBSERVE; continuación EFFECT_CONFIRMED/2/2, sin execute ni nuevas entidades. |
| NA30 | NATIVE_R | CRASH_BEFORE_OBSERVE: QUERY emitida, P recibida, READY before_observe; SIGKILL y reopen; reconcile explícita nueva | Al abrir UNKNOWN/1/1 con send+qid pending, cero OBSERVE; continuación EFFECT_CONFIRMED/2/2, sin execute ni nuevas entidades. |
| NA31 | NATIVE_T | CRASH_AFTER_OBSERVE_HEAD: OBSERVE con P, READY dentro Store after_head, SIGKILL; reopen y replay cid | EFFECT_CONFIRMED/2/1, un recibo/observación alcanzable; replay exacto sin cambio HEAD ni repetir transporte. |
| NA32 | NATIVE_R | CRASH_AFTER_OBSERVE_HEAD: OBSERVE con P, READY dentro Store after_head, SIGKILL; reopen y replay cid | EFFECT_CONFIRMED/2/1, un recibo/observación alcanzable; replay exacto sin cambio HEAD ni repetir transporte. |
| NA33 | NATIVE_T | PROTOCOL_OWNERSHIP: Controles READY identidad/rol/variant/op/ticket/punto, EOF/normal/timeout e inode/marker/sentinel/symlink | Rechazo de mensajes/falsas caídas y limpieza insegura; restauración antes de limpiar propio; cero residuos. |
| NA34 | NATIVE_R | PROTOCOL_OWNERSHIP: Controles READY identidad/rol/variant/op/ticket/punto, EOF/normal/timeout e inode/marker/sentinel/symlink | Rechazo de mensajes/falsas caídas y limpieza insegura; restauración antes de limpiar propio; cero residuos. |
| NA35 | NATIVE_T | INVENTORY_RAW: Controles mapas NA36, inputs/raw/hash/schema/skip/budgets; aislamiento config T/R v1 y namespaces nuevos | Fallo explícito ante cambio/omisión/duplicado/límite, no sumar controles internos; seis regresiones separadas y rechazo de namespace cruzado. |
| NA36 | NATIVE_R | INVENTORY_RAW: Controles mapas NA36, inputs/raw/hash/schema/skip/budgets; aislamiento config T/R v1 y namespaces nuevos | Fallo explícito ante cambio/omisión/duplicado/límite, no sumar controles internos; seis regresiones separadas y rechazo de namespace cruzado. |

## Correspondencia y decisión futura

| Obligación / límite | Filas propuestas | Valoración en I54 |
|---|---|---|
| UI20.1 vacío / hecho ausente | NA01–NA04 | Soporte histórico preservado; pruebas nuevas NOT_RUN |
| UI20.2 prueba incompatible / conflicto persistente | NA07–NA14 | Soporte histórico preservado; no nuevo dictamen |
| UI20.3 / H07 múltiples coincidencias / 429 | NA07–NA22, NA25–NA32 | PARTIAL / OPEN, no cierre por diseño |
| DF26 múltiples identidades / no adoptar | NA07–NA14, NA27–NA28 | Propuesta de soporte acotado, no aceptación |
| DF27 retry concluyente / tick y guardas | NA23–NA24 | Control separado; 429 sólo no basta |
| DF28 / binding UNKNOWN no reenvía | NA15–NA22 | Futuro oráculo integrado por identidad |
| MG01 colección nativa válida | NA03–NA12 | MODEL_GAP actual; nueva capacidad propuesta |
| MG02 429 durable con dos desenlaces | NA15–NA24 | MODEL_GAP actual; protocolo sintético, no HTTP real |
| MG03 selección/adopción humana | Ninguna | Fuera de alcance; no se añade a UI20.3 |
| Dos fronteras acotadas de OBSERVE | NA29–NA32 | No completa F1–F7/UI22.2 |
| Guardas / inventario / namespaces | NA33–NA36 | Controles, no evidencia de efecto |

Cada raw futuro indicará ID, método/fuente/líneas, path/variant, run/store/send/ticket/M, cid/request/response_id, canal/status/tick, envelope íntegro/hash y snapshot remoto, catálogo/recibo versus entidades core, llamadas execute/query reales, evento READY/punto/SIGKILL, lector/reopen y oráculos antes/después. No probar persistencia sumando PASS aislados. El runner y sus regresiones no se han ejecutado.

Aplicar los límites, precedencias, errores estructurales versus conflictos, contadores y guardas del contrato. Error estructural tras QUERY deja ledger1/queries1 y query pending; CONFLICT observado pasa ledger2/queries1. Rechazo de namespace al abrir no ejecuta operación ni cambia HEAD. Capacidad nueva implementada no cambia retrospectivamente los MODEL_GAP de I49/I50 ni declara la adopción humana implementada.

D1–D4 y A52 intactos; D5 global/G01–G07 y cinco GI abiertos. I53/I54 locales; sin publicación nueva, proveedor/credenciales reales, consumo/reservas, activación, promoción, despliegue ni D6.
