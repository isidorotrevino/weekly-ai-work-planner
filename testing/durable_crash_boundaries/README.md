# I44 — fronteras H02 sintéticas T/R

Implementa el [contrato I43](../../docs/design/D5-I43-DURABLE-CRASH-BOUNDARIES-DESIGN.md)
y su [matriz HF01–HF40](../../docs/design/D5-I43-DURABLE-CRASH-BOUNDARIES-REVIEW.md),
aprobados por selección A posterior al commit `d34538a`.

Desde la raíz: `python3 -B -m testing.durable_crash_boundaries.run_crash_boundaries_lab`.
Stdout es raw nuevo, sin reescribir evidencia. Cuarenta tests/filas previstos,
con HF39 en T y R; el runner informa los IDs y escenarios realmente ejecutados.
HF01–HF24 fijan seis operaciones/stages R por cuatro hooks existentes. HF25–HF30
son OSError en directory_fsync y recuperación fallida, no SIGKILL. HF31/32 matan
APPLY/APPLY_BATCH en after_head antes de binding/proyección; la continuación
posterior es explícita y no emite ISSUE. HF33–HF38 parten de UNKNOWN y distinguen
execute retornado, lookup retornado y QUERY anterior a lookup.

El lector independiente reutilizado de I42 no llama Store/reducer. Cada caída
incluye lectura de archivos en proceso nuevo y apertura pública pasiva separada,
antes de replay/continuación/reconcile explícitos en otro proceso. Metadata de
objetos huérfanos/temporales no concede autoridad. El mismo cid/args/expected se
repite explícitamente en las filas locales; dispatch/reconcile generan sus IDs
internos y se observan sin sustituirlos. Lookup/execute observados delegan sin
alterar respuesta; hashes/counters permiten distinguir recepción de prueba y
reenvío. Reconcile posterior exige lookup=1, execute=0 y REMOTE intacto.

Controles HF39/HF40: gate equivocado, identidad, EOF, salida normal, timeout reducido,
ownership/inodo/marker/sentinel/enlace, input cambiado/añadido, raw ausente/
incompatible/hash incorrecto, límites de salida/eventos y contabilidad. El control
negativo de timeout mata solo su hijo y no cuenta como frontera de recuperación.
Límites: 20 s/espera, 120 s/caso, 900 s/campaña propia; cuatro hijos vivos/caso,
256 eventos/caso, 16 KiB/evento, 8 MiB/raw. Optimize=0 requerido; lector con checks
explícitos. Recursos y limpieza solo propios; no inspección de dev/run_data/D4.

Regresiones aprobadas, cada una con raw/contexto/pre-post nuevos separados:
`python3 -B -m testing.durable_concurrency.run_concurrency_lab` (24 HC existentes)
y `python3 -B -m testing.D5.run_relational_durable_lab` (321 Python existentes).
Los runners no cambian. Filas, escenarios, gates, OSError y SIGKILL no se suman
como tests adicionales. Controles/fronteras ya presentes DF20/DF21/DR26 se señalan
como tales; los resultados no inventan cuarenta lagunas inéditas.

P0, D1–D4 cerrados, hito local I1–I20/A52 aceptado y D5 global/G01–G07 abiertos.
Sin cierre automático GI38 o recuperación integrada por suma de PASS. Fuera:
UPDATE/CLOSE de incertidumbre, restantes H03/H07, energía/disco/NFS/Windows/caller
hostil y raw/contexto históricos ausentes. Sin proveedores/credenciales reales,
consumo/reservas, activación, promoción, despliegue, SQL/Java/Docker o D6.
