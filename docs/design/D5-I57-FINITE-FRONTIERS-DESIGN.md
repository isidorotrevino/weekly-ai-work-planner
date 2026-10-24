# D5 I57 — contrato de matriz finita F1–F7

Fecha: **2026-10-24**, Europe/Madrid. **PREPARED_FOR_REVIEW**. Base local I56 `4070a2468634ba41e998c6fdb8e50f26c7847d40`.
[Matriz FL01–FL35 y FN01–FN64](D5-I57-FINITE-FRONTIERS-REVIEW.md) · [Sello, fuentes y punteros](../validation/D5-I57-design-review.json) · [Dictamen I56](../validation/D5-I56-results.md) · [Ruta de cierre](D5-I51-CLOSURE-PLAN.md).

## Autoridad y objetivo

El usuario eligió **A** tras I56: preparar contrato y matriz finita F1–F7 para UI22.2/GI38, distinguiendo evidencia existente, no aplicables justificados y cortes pendientes. I57 sólo lee documentos/fuentes/AST/JSON/hashes/Git y crea diseño. No autoriza código, campañas, auditor, SQL o push. Se propone un I58 concreto para revisar antes de implementar.

La obligación UI22 original exige caída/reinicio antes/después de F1–F7 con doble remoto superviviente, sin perder estado/recibos/conflictos ni duplicar efectos. El diseño original añade respuesta perdida cuando corresponde y excluye una transacción distribuida. Aquí se fija un inventario finito de salidas de dominio y sus variantes declaradas; no se multiplica toda operación, tipo de mutación, autoridad y estado imaginable. Un estado inicial distinto queda visible, sin convertirlo en fallo del runtime ni modificar la obligación histórica.

## Fronteras lógicas y puntos físicos

| Frontera original | T v1 | R v1 | Salida / autoridad |
|---|---|---|---|
| F1 importación/selección | IMPORT desde commit I26 y perfil previamente elegido | CAPTURE JSON, SELECT_SOURCE | Fuente exacta seleccionada, aún sin aceptación implícita |
| F2 preparación/revisiones/evaluación | SOURCE ACCEPT, PREPARE_EVALUATION, EVALUATION ACCEPT, PREPARE_EFFECT, EFFECT ACCEPT | PREPARE_SOURCE, SOURCE ACCEPT, PREPARE_BATCH, BATCH ACCEPT | Manifiestos/revisiones propios; ningún efecto local aplicado |
| F3 aplicación local | APPLY | APPLY_BATCH | TASK o lote completo + mapping/base/procedencia/generación/recibo atómicos |
| F4 snapshot/binding/paquete | BIND, PREPARE_PROJECTION, PROJECTION ACCEPT | SELECT_TASKS desde recibo, BIND, PREPARE_PROJECTION, PROJECTION ACCEPT | TASK/base/payload/capabilities y revisión exactos; sin envío |
| F5 intento/entrega | ISSUE CREATE y after_issue de dispatch | ISSUE CREATE y after_issue de dispatch | Un ticket durable UNKNOWN antes de cualquier llamada remota |
| F6 hecho remoto | EXECUTE CREATE, EXECUTE UPDATE, CLOSE | EXECUTE CREATE, EXECUTE UPDATE, CLOSE | Efecto o tombstone + índice/ticket/prueba juntos; CLIENT independiente |
| F7 respuesta/conciliación | QUERY, RESULT dispatch, RESULT query | QUERY, RESULT dispatch, RESULT query | Observación/ledger/pendientes/recibo correlacionados; lectura pasiva no ejecuta |

**FL01–FL35: 35 filas × cuatro puntos = 140 celdas de inventario**, no 140 tests ejecutados. Puntos: before_object, after_object, before_replace y after_head. Los tres primeros conservan HEAD/estado/recibos alcanzables previos; puede haber huérfano/temporal físico. after_head sucede tras fsync y antes de retornar transact: recibo/estado nuevos alcanzables con respuesta perdida al matar al hijo. Esa es la variante de pérdida de respuesta de cada commit local, sin contar otro test por cambiarle el nombre.

Los huecos after_issue, after_remote, after_query, before_result y before_observe son puntos de fachada distintos de Store.before_object. El catálogo lógico enlaza los casos que realmente los alcanzan. before_result prueba P recibida antes de invocar RESULT; no acredita cada punto interno de RESULT con query_id. after_head de APPLY/APPLY_BATCH prueba el hueco previo a binding; no acredita matar dentro de BIND.

OSError en directory_fsync/recovery_fsync se inventaría aparte de SIGKILL. Hay evidencia T DF11, R DR24 y HF25–HF30 R temprano; no se transfiere a una primera revisión ACCEPT/BIND/RESULT_QUERY ni se interpreta como corte físico de energía. I58 propuesto no añade OSError; esa ampliación queda fuera de su alcance y visible para revisión posterior.

## Lectura del inventario histórico

Las 140 celdas se clasifican: **41 EXISTING_BOUNDED_EVIDENCE**, **15 EXISTING_HISTORICAL_METADATA_ONLY**, **24 EXISTING_MODE_UNLABELLED**, **40 PARTIAL_EXISTING_DIFFERENT_STATE** y **20 PENDING_NO_MATCHING_CASE**. Son clases de evidencia y estado inicial; no son porcentajes de cobertura aceptada ni sumas de pruebas nuevas.

T DF08–DF12 parte de ready: IMPORT repite una fuente, las revisiones son REVOKE v1→v2 y algunas preparaciones ya existen. Esos casos sí ensayan el commit descrito; no se les adjudica primera publicación o ACCEPT v0→v1. R DR23 cambia selección ya existente, prepara PROJECTION existente y usa RESULT(query_id=None); no incluye BIND ni REVIEW PROJECTION. HF01–HF24 sí tiene primeras fases SOURCE/BATCH R con raw propio. HF31/HF32 aporta un oráculo explícito para efecto local antes de binding. Se reutiliza evidencia donde corresponde, sin reconstruir stdout original I34/I36.

El raw Python321 de I55 registra los crashes R, pero no un detalle T por fase: T se referencia mediante metadata publicada I34 y fuente pinneada. Los registros remotos DF/DR agrupan CREATE/UPDATE/CLOSE y no tienen campo mode; el bucle literal da una correspondencia estática posible, no modo empíricamente observado. Las mismas referencias compartidas entre tres filas no cuentan tres pruebas acreditadas distintas. En T before_replace y after_head pertenecen a DF20; DF19 es OSError, no se usa como SIGKILL.

El JSON conserva por celda path/pointer/hash de evidencia y razón de aplicabilidad; las fuentes de factories/loops y writers tienen símbolo/líneas/hash. El PASS del método padre no sustituye la identificación del caso. La clasificación no altera I34/I36/I44/I55/I56 ni la matriz fija I38.

## Perímetro de I58 propuesto

Sólo archivos nuevos en `testing/durable_frontier_gaps/` (support, tests, runner y README) y documentos/raw I58. Sin cambios de Store, producto, fixtures T/R o nativa, helpers/runners históricos, schemas, hooks, registro I38 o handoff. APIs públicas y hooks existentes. Linux local, spawn y Pipe; cero manipulación de HEAD/objetos/recibos de dominio para construir estados, cero pickle de autoridad.

**FN01–FN60**: 15 salidas/estados concretos × cuatro puntos; un método explícito, una raíz y un SIGKILL por fila. **FN61–FN64**: cuatro controles T/R de protocolo/ownership e inventario/raw. Todos NOT_RUN/NOT_REVIEWED. La novedad está en la primera publicación/ACCEPT/BIND o la rama QUERY de RESULT, no en añadir un hook genérico.

Las 15 precondiciones exactas figuran en la matriz. Los setups T nuevos se detienen en el punto preciso mediante comandos públicos y factories sintéticas conocidas; ready completo no sirve para preparar una primera importación/evaluación/revisión. Conservar pin I26 real para T, bytes exactos y grados. La cuenta/política/observaciones son sólo fixture, sin consumo o reserva. R usa su SOURCE/BATCH y recibo APPLY_BATCH, TASK participante y selección propios; no adopta EVALUATION Markdown ni I32. Ninguna precondición aplica un estado por escritura directa de archivos.

Para primeros commits: antes del punto objetivo, baseline exacto con la salida ausente/revisión0; sólo el comando objetivo puede publicarla. Antes de HEAD, salida ausente y sin recibo cid; tras HEAD, exactamente una salida/revisión1 y un recibo correlacionado, sin fases posteriores implícitas. Para BIND y preparación/revisión PROJECTION, exigir cero sends y cero efecto REMOTE. No confundir manifiesto preparado con efecto aplicado o permiso de envío.

### Rama RESULT_QUERY

Un ticket CREATE realmente emitido, efecto REMOTE confirmado una vez y CLIENT UNKNOWN/ledger1. QUERY pública explícita y durable crea queries1 y pendiente qid junto a send; sin RESULT anterior. El hijo abre un CLIENT fresco y realiza Remote.lookup real del ticket/M antes de construir RESULT(query_id=qid). El padre puede comparar hashes de prueba como observación, pero no pasar una P como autoridad del hijo. Usar cid/expected fijos para RESULT; calcular request_hash con la prueba devuelta realmente por lookup y señalarlos en READY. Armado del hook después del setup, sólo para ese RESULT; no matar la QUERY previa por error.

Antes de HEAD: UNKNOWN/ledger1/queries1 y send+qid pending; sin recibo RESULT. Lector independiente y lector público spawn pasivos sin llamadas. Sólo una reconcile posterior explícita añade otra QUERY y registra P: EFFECT_CONFIRMED/ledger2/queries2, pendientes vacíos, cero execute/close. Después de HEAD: EFFECT_CONFIRMED/ledger2/queries1, un recibo RESULT y pendientes vacíos; read_command/replay exactos históricos, sin duplicar observación ni mover HEAD. REMOTE HEAD/entidad/índice/ticket/P/version/payload/campos ajenos permanecen iguales en consulta y continuación. Un ticket emitido es requisito; no usar candidato o segundo ticket no autorizado.

## Oráculos, protocolo y continuación

READY identifica run/stores/path/rol/operación/stage/modo/punto/cid/request/expected y, si corresponde, M/send/ticket/qid/proof hash. El padre filtra exactamente el comando objetivo, recibe READY y sólo entonces mata ese hijo y verifica exitcode=-SIGKILL. EOF, salida normal o timeout son negativos; no se contabilizan como caída positiva. No sleeps/azar para acreditar una frontera.

Después de matar: lector de archivos independiente en proceso nuevo verifica hashes/cadena/HEAD/recibos; otro CLIENT público spawn verifica snapshot/summary/read_command pasivos. Mantener manifiestos, revisiones, pins/procedencia, generaciones, TASK/lote/selección/binding, ledger/attempts/queries/pending, P/tickets/entidades/campos ajenos y hashes antes/después. No limpiar huérfanos/temporales antes del oráculo ni promoverlos al abrir. Comparar estado alcanzable; no exigir igualdad física del directorio cuando puede existir un objeto huérfano legítimo.

Continuación de primeros commits: read_command exacto primero. Si no confirmó, replay expreso mismo cid/args/expected confirma una vez; si confirmó, replay devuelve histórico sin mutar. Ningún ACCEPT se recrea al abrir. Para RESULT_QUERY se sigue la continuación específica anterior. No reenviar un intento UNKNOWN ni usar la prueba histórica para renovar vigencia. Después de un commit confirmado se puede avanzar CLOCK en una comprobación explícita de no rebobinado; el replay conserva ese cambio posterior, sin fuente/revisión nuevas implícitas.

Registrar en raw: FN/celda FL, estado inicial, comando completo o hashes cerrados cuando proceda, rol/stage/modo/punto, run/stores/cid/request/expected y HEADs, P/ticket/qid, orden/ronda, recursos y oráculos. Mapas FN→método/fuente/FL/punteros y resultado esperado/observado separados. No deducir persistencia/recuperación integrada de PASS aislados: cada secuencia mantiene la misma identidad hasta su continuación.

## No aplicables, auxiliares y extensión nativa

Las seis exclusiones tipadas de la matriz no borran una obligación: R no tiene I26/EVALUATION T, T no tiene BATCH/SELECT_TASKS R, lookup remoto de sólo lectura no tiene commit REMOTE a matar y F0 queda fuera del corte F1–F7 como prerrequisito. CLOSE legacy sí tiene commit/tombstone y permanece en FL14/FL32. La fachada nueva I54 no expone CLOSE; su alcance es CREATE. No se llama N/A a evidencia ausente de una operación existente.

Registro/selección de perfil, cuenta/política/observaciones, CLOCK y VALIDATE_EVALUATION son precondiciones, mutaciones de elegibilidad o recibos auxiliares; este catálogo no afirma una cobertura universal de sus intercalados. Se conservan los casos originales y pendientes de otras UI. La partición por salidas F1–F7 no demuestra cualquier combinación de esos cambios ni sustituye UI26/UI27.

NATIVE_T/NATIVE_R tiene NA29–NA32 en F7, con schemas y operación OBSERVE distintos. No se transfiere a RESULT legacy ni por el uso común de Store a todas sus fases CORE. I58 propone sólo T/R v1 y cero casos nativos. La extensión de recuperación completa del namespace nuevo permanece NOT_ASSESSED y necesitaría decisión de perímetro/contrato propia si se exige en el expediente final; no se impone automáticamente un producto cartesiano nuevo por admitir UI20.3 acotada. La vista I56 de UI20.3 sigue intacta.

## Ejecución futura y aceptación

Comando nuevo propuesto: `python3 -B -m testing.durable_frontier_gaps.run_frontier_gaps_lab`. Antes/después: discovery completo de source_ingest/*.py, testing/D5/*.py y fixtures/*.md, helpers reutilizados, harness/README nuevos, contrato/matriz/sello I57 y fuentes de evidencia efectivas. Registrar lista y reglas, Python/build/plataforma/optimize/debug y comando; rechazar optimize!=0, entradas cambiadas/añadidas, mapa incompleto/duplicado, skips, errores, raw inválido/hash distinto y recursos restantes. Hashes no bastan para declarar suficiencia de la lista.

Límites del harness nuevo: cuatro hijos vivos,20s espera,120s/caso,900s/campaña,256 eventos/caso,16KiB/evento,12MiB/raw, sin ampliar límites kernel/T/R. Máximos y +1 o límites reducidos identificados en controles. Ownership inode/marker/sentinel/symlink se restaura antes de limpiar sólo raíces propias; cero hijos/hilos/raíces restantes. No inspección/limpieza operativa dev/run_data/D4.

Siete regresiones separadas, raws/contextos pre/post propios: Python321 mediante `testing.D5.run_relational_durable_lab` (mismo discovery unittest con inventario JSON), HC24 `testing.durable_concurrency.run_concurrency_lab`, HF40 `testing.durable_crash_boundaries.run_crash_boundaries_lab`, IC30 `testing.durable_issue_create.run_issue_create_lab`, UQ24 `testing.durable_uncertainty.run_uncertainty_lab`, RV20 `testing.durable_inflight_revocation.run_inflight_revocation_lab`, NA36 `testing.durable_native_ambiguity.run_native_ambiguity_lab`, todos `python3 -B -m`. Si el inventario descubierto difiere del esperado, detener y explicar antes de interpretar conteos. Regresiones no son tests nuevos, ni nuevas caídas I58. No ejecutar SQL/Java/Docker/auditor I38 ni recuperar raws originales ausentes.

I58 entregará harness/README, raw FN64, siete pares raw/contexto, results.md/json y mapa FL/FN/oráculo/estado. Tras evidencia fuente/lector/reapertura/continuación revisada, emitir otro dictamen de UI22.2. FN64 PASS por sí solo no completa todas las celdas calificadas, modos sin etiqueta, OSError, targets nativos o GI38/D5; los pendientes deben seguir visibles. Si falta hook/API o un oráculo contradice el código, detener esa ampliación y presentar el cambio concreto de contrato; no modificar producto ni reducir el oráculo silenciosamente.

**A — Aprobar I57 y autorizar I58:** implementar FN01–FN64 y las siete regresiones separadas descritas. **B — Conservar sólo diseño. C — Ajustar la matriz o el corte antes de implementar.** La A que preparó este documento no autorizó la implementación. Ninguna opción publica ni acepta criterios globales.

UI22.2 sigue PARTIAL; agregado I56 77/7 y UI20.3 con soporte acotado sólo en NATIVE_T/NATIVE_R intactos. H07, D5 global/G01–G07 y los cinco GI abiertos, closure=false; sin promoción 30/35→35/35. D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. Los siete requisitos reales/humanos siguen sus puertas propias, sin traslado a D6. Publicado sólo hasta I52 `ce44158`; I53–I57 locales, sin push nuevo. Sin proveedor/credenciales/corpus real, consumo/reservas, activación, promoción, despliegue ni D6.
