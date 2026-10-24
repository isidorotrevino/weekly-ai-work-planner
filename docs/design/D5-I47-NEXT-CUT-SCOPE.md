# D5 I47 — siguiente corte tras I46

Fecha: **2026-10-24**, Europe/Madrid. **A seleccionado; diseño preparado para revisión**.
Base: `585c5e91c2072e656f7296fd2f04af3f1fc7d1c1`.
[Resultados I46](../validation/D5-I46-results.md) ·
[Sello I46](../validation/D5-I46-results.json) ·
[Resultados I44](../validation/D5-I44-results.md) ·
[Resultados I42](../validation/D5-I42-results.md) ·
[Revisión I40](../validation/D5-I40-results.json).

«Sigue» autoriza preparar la decisión siguiente. La selección A anterior cubría
implementar/validar I45 en I46; no elige otro alcance material o publicación.
El usuario eligió ahora A. El [contrato](D5-I47-SUFFICIENCY-DELTA-DESIGN.md) y la
[matriz](D5-I47-SUFFICIENCY-DELTA-REVIEW.md) concretan la revisión propuesta, sin
ejecutarla, implementar código o reejecutar campañas. Las alternativas conservan
el planteamiento de la decisión original.

## Estado y evidencia comprobados

Git inicial limpio en el SHA indicado. main está dieciséis commits por delante
de la referencia local origin/main, aún en
`8e90a87cce7edbefc6c854a73ff1f60a20ae8485`; se comprobó ascendencia y conteo local.
No se consultó de nuevo el remoto, por lo que no se acredita su estado actual.

Verificación SHA-256 documental sin pruebas: 109 inputs y siete artefactos I46;
25 inputs I45; 100 inputs/cinco artefactos I44; 91 inputs/cinco artefactos I42;
42 inputs públicos/tres documentos I40. Todos coinciden. Esta integridad no
reescribe dictámenes ni convierte snapshots de desarrollo/contextos no aplicables
en CURRENT, ni reejecuta las campañas conservadas.

I46 registra 30 IC propios y regresiones HC24/HF40/Python321 separadas. Los 31
escenarios y 24 carreras con orden forzado no son tests adicionales. IC21–IC24
son negativos solo REMOTE con ticket extra no emitido: CLIENT conserva UNKNOWN/1,
sin reconcile/adopción y sin conclusión integrada. Una entidad única no acredita
autenticación de tickets o dos emisiones autorizadas.

I42, I44 e I46 añaden evidencia acotada sobre partes de H03/H02, con controles
históricos repetidos y límites explícitos. H02/H03 no se cerraron globalmente;
H07 y límites históricos H04/H05 siguen pendientes. No se infiere persistencia o
recuperación integrada de PASS aislados, reapertura pasiva o conteos de pruebas.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. D5 global,
G01–G07 y revisión global GI33/GI34/GI38/GI39/GI40 abiertos. Sin promoción
automática 30/35→35/35 o capacidades reales deducidas de fixtures.

## Opciones de diseño

**A — Recomendada: revisión conjunta de suficiencia con el delta I42/I44/I46.**
Preparar contrato/matriz para contrastar UI01–UI40, sus subcláusulas y controles
SR con código, tests, raw/contextos y pre/post hashes nuevos, tomando I40 como
base histórica inmutable. Separar obligación antes cubierta, estado/oráculo nuevo,
repetición, exclusión local y pendiente global. Revisar especialmente identidad
CLIENT/REMOTE, tickets no emitidos, precedencia de conflictos, UNKNOWN antes de
caer, fronteras reales y recursos por campaña. No elevar prueba negativa REMOTE,
replay histórico o modo CREATE a capacidad integrada, permiso o recuperación en
otros modos. La revisión futura sería documental, sin reejecutar HC/HF/IC/Python
ni SQL/Java/Docker. Emitiría informe nuevo y no cerraría automáticamente D5/GI/G.

**B — Alternativa: incertidumbre durable H07/GI38.** Preparar contrato/matriz para
resolver correspondencia entre prueba única/UNKNOWN T/R y múltiples coincidencias/
429 ambiguo de I28. Distinguir suficiencia de abstracción, escenarios representables
por API pública y cambios de modelo que necesitarían aprobación separada.
Los PASS volátiles PC08/PC26 no acreditan unión durable ni proveedor real.

**C — Alternativa: otras revocaciones/cambios pendientes de H03/GI39.** Preparar
contrato/matriz que priorice SOURCE/EVALUATION/BATCH frente a emisión/resultado,
fijando ámbito T/R, estados, autoridades, ambas ordenaciones y conflictos
admitidos. Decidir el subconjunto exacto antes de implementar; no incluir por
analogía cuenta/perfil/origen/grooming o todos los modos. Conservar hecho remoto
histórico y vigencia actual separados, sin rollback o revisión ficticios.

La recomendación A responde a las tres ampliaciones posteriores a I40: comprobar
qué obligación sostiene realmente cada evidencia antes de escoger otra expansión.
Elegir A/B/C autoriza **solo contrato y matriz**. Ejecutar una revisión, implementar
o correr pruebas requiere después aprobar el alcance concreto. No se presupone
cambio de producto o ampliación del registro fijo I38.

## Publicación independiente y límites

P0 mantiene I32, handoff y posteriores sin publicar. Destinos posibles para una
decisión separada posterior, ninguno autorizado ahora:

- Hasta I32: `7b64d87ef45b4973a5ea80dc676f1bd2eca220f7`.
- Incluir handoff: `79c696a66f85923173650f271995c69569b50b0d`.
- Incluir todo hasta I46: `585c5e91c2072e656f7296fd2f04af3f1fc7d1c1`, los
  dieciséis commits locales posteriores a I31 según el tracking disponible.

Antes de publicar se comprobarían remoto, ascendencia y diff del SHA exacto;
una autorización limitada no concede push de HEAD completo. Este borrador I47 no
está contenido en esos SHA. Seleccionar A/B/C no publica nada.

Sin proveedores/credenciales reales, corpus privado, consumo/reservas, operaciones,
activación, promoción, despliegue, D6 o inspección/limpieza de dev/run_data/D4 operativo.
