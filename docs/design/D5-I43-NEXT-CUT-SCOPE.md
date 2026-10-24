# D5 I43 — siguiente corte tras I42

Fecha: **2026-10-24**, Europe/Madrid. **A seleccionado; diseño preparado para revisión**.
Base local: `98df91a05a43313e26c47dc8d80fd3c2f16018d5`.
[Informe I42](../validation/D5-I42-results.md) ·
[Sello I42](../validation/D5-I42-results.json) ·
[Hallazgos originales I40](../validation/D5-I40-results.json).

«Sigue» autoriza preparar la siguiente decisión. La selección A anterior autorizó
implementar/validar I41 en I42; no elige implícitamente otro alcance material.
El usuario eligió ahora A: H02. El [contrato](D5-I43-DURABLE-CRASH-BOUNDARIES-DESIGN.md)
y la [matriz HF01–HF40](D5-I43-DURABLE-CRASH-BOUNDARIES-REVIEW.md) concretan el
corte para revisión. No implementa código ni ejecuta campañas. Las alternativas
siguientes conservan el planteamiento de la decisión, sin ampliarla.

## Continuidad e integridad documental

Git inicial limpio: main doce commits por delante de la referencia local
origin/main, que sigue en `8e90a87cce7edbefc6c854a73ff1f60a20ae8485`.
No se ha consultado de nuevo el remoto; el tracking local no acredita su estado
actual. HEAD local es el SHA de I42 indicado arriba.

Verificados por SHA-256, sin ejecutar pruebas: 91 inputs y cinco artefactos
raw/contexto sellados en I42; 20 inputs I41; 42 inputs públicos y tres documentos
sellados I40. Todos coinciden con sus bytes actuales. Eso no convierte los
snapshots de desarrollo en evidencia aplicable actual ni el contexto externo
completo de regresión en CURRENT: las tres diferencias de harness posteriores a
esa regresión siguen declaradas. Los 78 inputs ejecutados por la regresión sí
permanecen idénticos, como documenta I42.

I42 conserva 24 tests propios PASS y 321 regresiones PASS por separado, doce
carreras con órdenes impuestos y 25 escenarios (HC22 T/R). Esta lectura no los
reejecuta ni añade PASS. No se deduce persistencia o recuperación integrada a
partir de esas cifras. El probe observa exclusión; la reapertura final no prueba
SIGKILL. El hallazgo H03 histórico de I40 no se reescribe: I42 añade evidencia
acotada sobre parte de sus obligaciones y deja las exclusiones explícitas.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado permanecen intactos.
D5 global, G01–G07 y la revisión global GI33/GI34/GI38/GI39/GI40 siguen abiertos.
Ninguna opción promueve automáticamente 30/35 a 35/35 ni atribuye capacidad real
a fixtures T/R. Sin inspección o limpieza de dev/run_data/D4 operativo.

## Alternativas para preparar contrato y matriz

**A — Recomendada: fronteras de fallo H02 / GI38.** Diseñar el corte de proceso
abrupto entre efecto local y binding/proyección; las fases R anteriores a
APPLY_BATCH (CAPTURE, SELECT_SOURCE, PREPARE_SOURCE, PREPARE_BATCH, REVIEW); y
la pérdida de prueba antes de RESULT partiendo realmente de UNKNOWN. Fijar
estado previo, operación/rol/modo/punto antes-después, señal de gate, SIGKILL,
reapertura pasiva, acción explícita posterior, recibos/versiones y oráculo
independiente por fila. Distinguir fases que no modifican el mismo almacén y
las posibles fronteras que el producto realmente expone. No prometer «cada
frontera» por sumar crashes, ni contar una segunda caída que ya parta de
EFFECT_CONFIRMED como cobertura del hueco UNKNOWN. Inventariar los hooks existentes
y cualquier falta antes de autorizar cambios. Evidencia futura nueva con raw y
hashes antes/después, sin reescribir I34/I36/I40/I42.

**B — Alternativa: doble emisión/CREATE pendiente de H03 / GI39.** Diseñar dos
actores T/R, diferencias entre ISSUE en CLIENT y EXECUTE/identidad de creación
en REMOTE, entradas y versiones fijadas, ambas ordenaciones, posible intento
único/ticket repetido/creation_key distinto, y conflictos exactos admitidos.
Separar misma orden repetida de comandos distintos y de nuevo envío autorizado.
No extrapolar las carreras RESULT/REVIEW/EDIT de I42. Otras revocaciones y cambios
de cuenta/perfil/origen/grooming se inventarían como pendientes separados; esta
opción no los incorpora automáticamente.

**C — Alternativa: alcance durable de incertidumbre H07 / GI38.** Preparar contrato
y matriz que decidan explícitamente la correspondencia entre la prueba única/
UNKNOWN de T/R y las obligaciones de múltiples coincidencias/429 ambiguo de I28.
Separar suficiencia de abstracción, escenarios representables con API pública y
cambios de modelo que requerirían otra aprobación. Los PASS volátiles PC08/PC26
no acreditan unión durable. No fabricar una colección o respuesta de proveedor
real bajo una etiqueta de fixture ni reconstruir evidencia histórica ausente.

Cualquier elección autoriza **solo preparar contrato y matriz para revisión**.
El alcance elegido deberá fijar archivos, hooks, presupuesto, oráculos y regresiones
antes de una decisión de implementación. La autorización anterior de I42 no se
extiende automáticamente a nuevas campañas o a cambios de producto. Los límites
históricos H04/H05 y restantes hallazgos no desaparecen al seleccionar una opción.

## Publicación como decisión independiente

P0 mantiene I32, handoff y posteriores sin publicar. Los posibles destinos exactos,
para una decisión posterior separada, son:

- Solo hasta I32: `7b64d87ef45b4973a5ea80dc676f1bd2eca220f7`.
- Incluir el handoff: `79c696a66f85923173650f271995c69569b50b0d`.
- Incluir todo hasta I42: `98df91a05a43313e26c47dc8d80fd3c2f16018d5`, que incluye
  los doce commits locales posteriores a I31 según el tracking disponible.

Ninguno está autorizado. Antes de una eventual publicación se verificarían remoto,
ascendencia y diff del destino exacto; una autorización limitada no concede push
de HEAD completo. Este borrador I43 no está incluido en esos SHA.

P0 sigue vigente en A/B/C. Sin proveedores/credenciales reales, corpus privado,
consumo/reservas, operaciones, activación, promoción, despliegue o D6.
