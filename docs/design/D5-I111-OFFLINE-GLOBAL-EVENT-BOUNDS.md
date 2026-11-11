# I111 —35 raíces offline y publicación Git anterior

Fecha:2026-11-04, Europe/Madrid. **174 de321 pruebas tienen cotas de eventos
por fuente**. Este corte añade35 pruebas offline con340 eventos como máximo;
el subtotal de174 raíces asciende a **28471**. Faltan147 tests de4 familias
y discovery/finalización. No se ejecutaron suites, parsers, simulaciones o
campañas ni se importó producto/runner.

[Desglose, helpers y anclas](../validation/D5-I111-offline-model-event-bounds.json) ·
[Registro global174/321](../validation/D5-I111-global-event-bound-coverage.json) ·
[Commit/push autorizado y verificado](../validation/D5-I111-prior-publication-context.json).

## Las aserciones dentro de helpers también cuentan

applied, projection y applied_from_capture aportan1 aserción cada vez que se
invocan. La cuenta expande sus llamadas transitivas, incluidos los argumentos
antes de entrar al helper, y conserva los contextos esperados/subTest. Los otros
helpers no llaman a unittest; su trabajo de captura, revisión, construcción,
validación, hashing o mutation sigue ocurriendo en la prueba original.

Los bucles son listas literales, incluidas changes de GI19 (5 elementos) y
values de GI23 (5 elementos), asignadas en la misma raíz. No se derivan sus
cardinalidades de PASS, del presupuesto o de los resultados del modelo.
Los patches de GI37 se mantienen como barreras de la prueba original, sin
instalarlos ni invocar callbacks/IO del producto durante esta revisión.

## Clases en memoria y límites de la cuenta

MemoryLab, MemoryPlane y MemoryDrive son los tipos exactos de offline.py.
Sus nombres no los convierten en Store/Remote/FixtureStore/Drive observados.
La revisión por fuente del módulo completo en I106 y parser/funciones I109
permanece aplicable con los mismos hashes. operation de _command es el callback
anidado cerrado de apply_effect/apply_projection; las ediciones programadas en
MemoryPlane son datos builtin. No se admiten sustituciones de métodos o callees
arbitrarios para sostener la cota. evaluate_route valida y calcula sobre datos
sintéticos, sin transporte ni consumo/reservas reales.

Esta es una envolvente de la ruta original completa PASS con observación válida,
no nueva evidencia funcional ni una prueba general de despacho Python. No se
extrae persistencia/recuperación integrada, ni se acepta una obligación global
por assertions o PASS aislados. IO de fixtures/bytes, CPU y posibles errores
conservan su coste, aunque no generen eventos del registro en esos segmentos.

## Composición global

`E_global <= 28471 + U_remaining147 + U_discovery_and_recorder_finalization + 0_post_suite`

La cuota global es131072 eventos;16384 es referencias. El margen condicional
102601 no constituye admisión ni sustituye los términos desconocidos.
Se conserva la cota condicional321 frames de raíz de I110; no limita contextos,
subcasos, owners o referencias. Quedan incremental_capture30,
plane_reconciliation41, profiles_quotas38 y relational_batch38 (147 tests).
Faltan las cotas y composición de referencias, operandos, bytes/filas/tablas/
páginas y Reader/24 cuotas. R>=19037>16384(I97) sigue vigente.

I86/I89/I92 permanecen INVALID_CAPTURE, sin fusionar/reanudar prefijos. No hay
P01 completo válido e IR03 sigue NOT_READY. No se crea perfil/cuota/autoridad/
destino. Las decisiones concretas posteriores de contrato/implementación/
componentes/captura, suficiencia global y publicación permanecen separadas.

## Git publicado y continuación local

El usuario pidió «haz git commit y push y sigue». Se verificaron31 documentos
I104–I110 (1369545 bytes),31 sellos y428 paths de entrada de la revisión previa.
Los31 archivos staged coincidieron con sus hashes y diff --check pasó. Se creó
**50c49678568bae2abeefbe5fec0285f26c628283** en main y se publicó en origin/main;
ls-remote confirmó el mismo SHA. El árbol quedó limpio. Los flags históricos
publication_authorized=false se conservan en sus cortes sellados: el registro
nuevo documenta la autorización posterior, sin reescribirlos.

I111 es trabajo documental local después de ese push, fuera de aquel commit.
No se publica en este corte. P0;83 SUPPORTS_BOUNDED/1 PARTIAL, UI04.1 parcial;
D1–D4 cerrados e I1–I20/A52 aceptado. D5/H07/G01–G07 y GI33/34/38/39/40 globales
abiertos. Sin proveedores/credenciales/corpus reales, consumo/reservas,
activación, promoción, despliegue ni D6. No se inspecciona ni limpia estado
operativo dev/run_data/D4.
