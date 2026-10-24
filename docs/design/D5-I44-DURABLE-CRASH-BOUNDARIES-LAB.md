# D5 I44 — laboratorio de fronteras H02 en T/R

Fecha: **2026-10-24**, Europe/Madrid. Implementación del
[contrato I43](D5-I43-DURABLE-CRASH-BOUNDARIES-DESIGN.md) y la
[matriz HF01–HF40](D5-I43-DURABLE-CRASH-BOUNDARIES-REVIEW.md), aprobados por
selección A del usuario posterior a `d34538adb8ad9e6c04208cd26ed1072654beddc0`.
[Harness](../../testing/durable_crash_boundaries/README.md) ·
[Resultados I44](../validation/D5-I44-results.md).

Solo incorpora archivos nuevos de harness/documentos/evidencia I44. Producto,
suites/runners históricos, I42, I40, handoff y registro fijo I38 no cambian.
La aprobación de implementación no modifica P0 ni autoriza publicación.

## Protocolo y alcance

HF01–HF24: CAPTURE, SELECT_SOURCE, PREPARE_SOURCE, REVIEW SOURCE, PREPARE_BATCH y
REVIEW BATCH, cada uno en before_object/after_object/before_replace/after_head.
Cid/args/expected se fijan antes del hijo. Los tres puntos previos a HEAD conservan
estado alcanzable y no tienen recibo; after_head conserva commit/recibo exactos.
La evidencia distingue objetos huérfanos y temporales de HEAD del estado alcanzable.
No limpia o promueve esos archivos entre caída y observación. El replay explícito
recalcula la transición pública o recupera su recibo histórico, sin duplicación.

HF25–HF30: OSError sintético después del rename en directory_fsync y después otro
en recovery_fsync de un CLIENT nuevo; exigen COMMIT_UNKNOWN y RECOVERY_REQUIRED.
Otro CLIENT nuevo valida/fsync y recupera el commit visible de ese proceso local.
Son seis filas y doce eventos de falla, no doce tests ni garantía de energía.

HF31/HF32: SIGKILL en after_head de APPLY/APPLY_BATCH concretos, antes de que
perform retorne y antes de binding/proyección. Conservan efecto y recibo locales;
no inventan indicador durable de «fase pendiente». Lectura/replay no generan
proyección. Solo una continuación explícita hace BIND/PREPARE_PROJECTION/REVIEW,
y SELECT_TASKS R desde el recibo exacto del lote. No ISSUE o efecto remoto.
En T, BIND incrementa data_generation: el final 2 comprende APPLY y BIND, sin
segunda aplicación. R conserva data_generation 1 durante selección/binding.

HF33–HF38: CREATE de una TASK desde UNKNOWN/ledger 1 y sin conciliación previa.
Se mata dispatch tras execute retornado, o la primera reconcile tras lookup
retornado, o tras QUERY antes de lookup. Observadores del transporte delegan sin
alterar respuestas y registran hashes/counters. La apertura pública pasiva no
confirma el efecto. Una reconcile nueva explícita publica P exacta, ledger 2,
queries finales 1/2 y vacía pendientes; lookup=1, execute=0 y REMOTE intacto.

Cada caso tiene hijo mutador, lector independiente de archivos en proceso nuevo,
apertura pública pasiva en otro proceso y continuación explícita posterior.
El lector I42 reutilizado no llama Store/reducer; comprueba cadena/hash/recibos.
No se escribe HEAD/estado desde harness ni se restauran autoridades en memoria.
HF39/HF40 validan negativas de protocolo, propiedad, inventario, raw y contabilidad.
El SIGKILL de timeout negativo se separa de las fronteras positivas.

## Evidencia y límites

Comando propio: `python3 -B -m testing.durable_crash_boundaries.run_crash_boundaries_lab`.
El raw stdout se emite como JSON compacto, conservando todos sus campos y hashes.
Regresiones en procesos/campañas separados y runners sin modificar:
`python3 -B -m testing.durable_concurrency.run_concurrency_lab` y
`python3 -B -m testing.D5.run_relational_durable_lab`.
Cada grupo conserva su raw nuevo y pre/post hashes de inputs de ejecución.
No se atribuye a I44 el raw original de I34/I36 ni los «new_tests=40» históricos
del runner I36 como nuevos tests de I44.

Límites del contrato: 20 s/espera, 120 s/caso, 900 s/campaña propia, cuatro hijos
vivos/caso, 256 eventos/caso, 16 KiB/evento, 8 MiB/raw. Optimize=0 requerido;
lector con checks explícitos. Limpieza/inodos/markers/sentinels solo propios;
rechazo de propiedad impide borrar y señala fallo/residuo. Sin inspección operativa.

DF20/DF21/DR26 ya cubrían parte de los controles de respuesta perdida; no se
presenta cada HF como laguna inédita. La ampliación acotada incluye fases tempranas
R, oráculo del hueco local y primera reconcile R desde UNKNOWN. No se acredita
cada F1–F7/modo/etapa de revisión ni UPDATE/CLOSE de incertidumbre, energía/disco,
NFS/Windows/caller hostil, restantes H03/H07 o contexto/raw histórico ausente.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado se conservan. D5 global,
G01–G07 y revisión global GI33/GI34/GI38/GI39/GI40 siguen abiertos; sin promoción
30/35→35/35 ni recuperación integrada inferida de PASS aislados. Sin proveedores/
credenciales reales, corpus privado, consumo/reservas, activación, promoción,
despliegue, SQL/Java/Docker o D6. P0 sigue vigente.
