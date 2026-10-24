# D5 I50 — laboratorio de incertidumbre durable

Fecha: **2026-10-24**. Implementación/validación autorizada mediante A sobre I49,
base `1ef0bdf47c0c5cd4f68925c3ef6bec664e632748`.
[Contrato](D5-I49-DURABLE-UNCERTAINTY-DESIGN.md) ·
[Matriz](D5-I49-DURABLE-UNCERTAINTY-REVIEW.md) ·
[Resultados](../validation/D5-I50-results.md) ·
[Sello y campos raw](../validation/D5-I50-results.json).

Archivos nuevos exclusivamente en testing/durable_uncertainty/ y documentación/
evidencia I50. Producto, APIs, harness anteriores, handoff y registro I38 intactos.
El worker nuevo llama las APIs existentes; wrappers locales se restauran en finally.
execute anterior/posterior y lookup fallido registran llamadas reales por separado.
Los hooks de formatos invalidan proof; no simulan una colección nativa ni HTTP429.

Ejecutar desde raíz: `python3 -B -m testing.durable_uncertainty.run_uncertainty_lab`.
Los 24 métodos explícitos se corresponden con 26 escenarios: UQ17/UQ18 agregan
un contraste UNKNOWN en raíz independiente. Lector de archivos independiente y
apertura pública fresca spawn comparan HEAD/estado sin transporte. No nuevas
carreras/SIGKILL. Los retornos sustantivos, contadores y oráculos de archivo tienen
índices exactos en raw; los lectores grandes se registran por hash tras comparación.

Regresiones Python321, HC24, HF40 e IC30 ejecutadas separadamente: cada runner
histórico y sus dependencias efectivas tienen hashes/contexto antes/después propios.
Ningún PASS UQ cambia por sí mismo UI20.3/H07, MG01–MG03 o el dictamen I48.
D5 global/G01–G07 y todos los GI siguen abiertos. P0 y exclusiones permanentes
se conservan; sin publicación ni proveedor/credenciales reales, consumo/reservas,
activación, promoción, despliegue, D6 o intervención de dev/run_data/D4 operativo.
