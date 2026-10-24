# D5 I51 — contrato de revocación durante Remote.execute

Fecha: **2026-10-24**, Europe/Madrid. **PREPARED_FOR_REVIEW**.
Base: `0b083f50ee8589b90fedb3eb6720978303642b21`.
[Plan de cierre](D5-I51-CLOSURE-PLAN.md) ·
[Matriz RV01–RV20](D5-I51-INFLIGHT-REVOCATION-REVIEW.md) ·
[Revisión I48](../validation/D5-I48-results.md) ·
[Fuentes y sello](../validation/D5-I51-design-review.json).

## Autoridad y obligación exacta

La petición de avanzar hacia el cierre de D5 autoriza preparar este siguiente
contrato y matriz. Implementar I52 requiere aprobar el alcance concreto siguiente.
Se atiende **UI30.2/GI39**: revocación realmente intercalada durante llamada remota.
HC05–HC08 ya prueba RESULT/REVIEW cuando el efecto remoto ocurrió antes; no se
reescribe ni se presenta como el mismo intercalado. No se declara H03 resuelto.

Sólo nuevos archivos en testing/durable_inflight_revocation/ y documentos/raw I52.
No modificar producto, kernel, reducers, APIs, harness previos, sellos, handoff,
registro fijo I38 o cierres D1–D4. No proveedor/credencial/corpus real ni SQL,
consumo/reservas, activación, promoción, despliegue, D6 o acceso operativo dev/D4.

## Casos, modos y autoridad

RV01–RV16 son cuatro familias × T/R × CREATE/UPDATE. RV17/18 son controles de
protocolo/propiedad; RV19/20 inventario/raw/budgets. Veinte métodos explícitos con
IDs propios, sin contar lectores, actores o regresiones como tests nuevos.

Preparar una TASK y PROJECTION ACCEPT revisión1. T mantiene captura I26 y
SOURCE/EVALUATION/EFFECT; R conserva SOURCE/BATCH y TASK seleccionada desde recibo
exacto. UPDATE parte de un CREATE previamente confirmado y una nueva proyección
UPDATE revisada con base B exacta y foreign sentinel. Identificar send/ticket
activo por separado de sends/recibos del baseline; no exigir cero histórico al
ensayar UPDATE. No cambiar SOURCE/BATCH/EVALUATION, cuenta, perfil, origen o datos
locales durante estos casos: esos intercalados son CP04 posteriores independientes.

## Operación real y barrera causal

El actor de envío usará **Client.dispatch público**, con Remote.store hook mediante
el mecanismo existente de apertura T/R. El hook sólo se arma alrededor de la
invocación real Remote.execute del ticket activo; snapshots iniciales/recovery_fsync
no cuentan como barrera. READY incluirá case/path/run/store CLIENT y REMOTE,
actor/rol REMOTE/operación EXECUTE/modo/stage PROJECTION/punto, manifest/hash,
send/ticket y cid/request que identifique el commit EXECUTE.

Dos puntos existentes dentro de Store._publish:

- before_object: reducer evaluado, antes de publicar el nuevo objeto/HEAD; el
  Remote.execute real está en curso y mantiene su propio lock.
- after_head: commit/HEAD publicado y fsync retornado, pero Remote.execute aún
  no retornó; sigue bajo su lock. No es el checkpoint CLIENT after_remote.

El padre confirma READY y que actor sigue vivo, sin DONE. Lee CLIENT/REMOTE sólo
mediante oráculo independiente de archivos: estado alcanzable, cadena/hashes y
recibos. Mientras el lock REMOTE está retenido, no usar Remote.snapshot,
Client.summary, dispatch/reconcile adicional o una apertura que lea REMOTE:
causaría bloqueo o cambiaría el orden. La operación de revocación es otro proceso
que usa **Client.perform('REVIEW', …)** / review público con expected_version=1,
PROJECTION exacta, REVOKE y reason_code sintético; esa ruta sólo transacciona CLIENT.
Confirmar el recibo y observar revisión2 REVOKE en CLIENT antes de liberar al
actor REMOTE mediante ACK propio. No adquirir simultáneamente locks de dominio.

Secuencia de evidencia exigida: ISSUE confirmado → READY dentro de EXECUTE real
→ oráculo estable antes de revocar → REVIEW/recibo v2 realmente confirmado →
oráculo CLIENT v2 → ACK de liberación → retorno/error de transporte → RESULT.
READY sin revisión confirmada o un timeout no demuestra el intercalado. No llamar
REMOTE para sintetizar una respuesta tardía adicional. La revocación no cancela
retroactivamente la autorización del ticket ni hace rollback de un efecto remoto.

## Familias y oráculos

**BEFORE_ISSUE (RV01–RV04).** REVOKE v2 se confirma antes de dispatch. ISSUE falla
REVIEW_REQUIRED: ningún send/ticket/recibo de intento o efecto nuevo frente al
baseline; las llamadas preparatorias de lectura de capabilities no son execute.

**INFLIGHT_BEFORE_PUBLISH (RV05–RV08).** Pausar en before_object. HEAD/estado
alcanzable REMOTE aún es baseline; CLIENT ya tiene ticket UNKNOWN/ledger1.
Revocar en otro proceso y liberar. Remote confirma P y dispatch registra RESULT:
EFFECT_CONFIRMED/ledger2/queries0 con vigencia STALE. Una ejecución remota para el
ticket activo, sin reenvío ni segundo efecto. El hecho P y la revisión revocada
coexisten; STALE no elimina P ni devuelve el estado anterior.

**INFLIGHT_AFTER_COMMIT (RV09–RV12).** Pausar en after_head. Oráculo independiente
ya encuentra P/efecto alcanzables, CLIENT sigue UNKNOWN/1. Revocar antes del retorno
real; liberar y registrar P como hecho histórico con vigencia STALE. No equiparar
la observación del padre a prueba ya recibida por CLIENT.

**INFLIGHT_LOST_RESPONSE (RV13–RV16).** Igual pausa after_head y revocación
confirmada, pero wrapper de instancia captura únicamente hash de P al retornar
execute real y lanza OSError en lugar de entregar P. Se restaura en finally.
Client.dispatch público registra RESULT(None): UNKNOWN/ledger2/queries0, pending
send retirado. Sigue un intento emitido y bloqueo: ausencia de pending no autoriza
retry. Lector nuevo y apertura pasiva no consultan ni cambian estado. Sólo una
reconcile explícita nueva observa P por lookup, cero execute, y confirma
EFFECT_CONFIRMED/ledger3/queries1 + STALE. No fake HTTP429, cierre de ticket,
rollback, reconstrucción de aceptación o reenvío.

En todas las familias, la revisión antigua v1 nunca revive. Replay exacto del
recibo de revocación no avanza revisión/HEAD; una nueva petición con expected_version
vieja falla CONFLICT_REVIEW. Después de liberar el lock, summary pública debe
confirmar STALE. Un intento de dispatch/retry bajo la proyección revocada falla
REVIEW_REQUIRED en su orden de guardas, sin nuevo recibo/ticket/efecto. No inventar
BINDING_UNRESOLVED cuando una guarda previa es la que rechaza realmente.

Comparar cadena/HEAD/seq/hash/cid/request/recibos, revisión, send activo/attempts,
ledger/queries/pending, proof y versión/identidad/payload/foreign remotos. CREATE
produce una entidad nueva versión1, UPDATE produce B.version+1 con foreign
conservado; comparar también entidades ajenas y sends históricos sin restaurarlos.
La revisión CLIENT no altera datos/bindings localmente ni ejecuta REMOTE. Tras
respuesta perdida, el único efecto es el del ticket autorizado y la conciliación
no parchea payload ni modifica REMOTE. Ningún exitcode o PASS sustituye estos
oráculos anteriores/posteriores de la misma secuencia e identidad.

## Lectores, controles y evidencia

Después del intercalado, ejecutar lector independiente y CLIENT fresco spawn.
Comparar HEAD/estado completos. Apertura pasiva: cero execute/lookup/review nuevos;
la consulta posterior explícita se etiqueta con sus propios contadores. No nuevas
caídas positivas o garantías de energía: los puntos son barreras de intercalado.

RV17/18 rechazará READY con identidad/rol/punto/operación/modo/stage erróneos,
EOF/salida normal o timeout reducido que se quiera pasar por protocolo correcto.
Timeout negativo sólo termina el hijo propio y no cuenta como recuperación.
Negativos inode/marker/sentinel/link se restauran antes de cerrar la raíz propia;
ningún lector/actor/hilo o raíz propia restante. RV19/20 comprobará inputs añadidos/
cambiados, raw ausente/incompatible/hash, IDs duplicados/incompletos/skips/residuos
y budgets reducidos. Esos controles no acreditan UI30.2 por sí mismos.

Límites: cuatro hijos vivos,20s espera,120s caso,900s campaña,256 eventos/caso,
16KiB/evento,8MiB/raw; rige también el límite heredado más restrictivo. Runner
rechaza optimize!=0 y registra debug/build/python/platform/comando, inputs antes/
después, dependencias efectivas y discovery. Incluir nuevas fuentes/README,
source_ingest, helpers T/R/HC reutilizados, contratos/sellos I51 e informes que
fijan baseline. No cambiar entradas durante una campaña ni heredar PASS ante
inventario incompleto. Sin datos privados ni paths temporales crudos en salida.

Raw nuevo I52: ID/path/rol/op/modo/stage/punto/ronda/actor, run/store/send/ticket/M,
READY, versión/recibo/cid/request de revocación y ACK en orden causal; estado
alcanzable antes/después, proof/hash, contadores wrapper frente a llamadas reales,
resultado/summary, salida y recursos. En SOURCE T/R fijar referencias exactas,
no representar la autoridad de otro modelo. Mapping método→caso→campo/índice raw
resoluble; separar declaración, semántica y ejecución, sin cierre global automático.

Si se aprueba I52: campaña RV20 propia y regresiones **Python321, HC24, HF40, IC30,
UQ24**, cada una con raw/contexto/hashes pre/post y recursos propios. Conservar IDs
e intersecciones por campaña; ninguna suma es integración global. No reejecutar
SQL/Java/Docker, auditor o cierres D1–D4. Cero pruebas ejecutadas al preparar I51.

## Decisión concreta posterior

**A — Aprobar este contrato y autorizar I52:** implementar/validar únicamente
RV01–RV20 y las cinco regresiones separadas indicadas, con producto/API/modelo e
historia intactos. Preparar también la revisión documental CP01/CP05, sin cambio
automático de valoraciones. **B — Aprobar sólo diseño**, sin ejecutar.
**C — Ajustar matriz/alcance** antes de implementar. La publicación es otra decisión.

D5 global/G01–G07, H03 y los cinco GI quedan abiertos; UI30.2 no mejora antes de
revisar evidencia. Los otros nueve parciales I48 no desaparecen por este contrato.
D1–D4 y A52 aceptados se conservan. Sin proveedores/credenciales/corpus reales,
consumo/reservas, activación, promoción, despliegue, D6 o intervención dev/D4.
