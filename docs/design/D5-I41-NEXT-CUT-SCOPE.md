# D5 I41 — siguiente corte tras la revisión I40

Fecha: **2026-10-24**, Europe/Madrid. **A seleccionado; diseño preparado para revisión**.
Base: `900e837edfdd97d0b85f1b8c8b455f5797f24fa0`.
[Informe I40](../validation/D5-I40-results.md) ·
[Matriz revisada](../validation/D5-I40-matrix.md) ·
[Dictámenes y referencias](../validation/D5-I40-results.json).

English: next-cut alternatives derived from the documentary review. No runtime
changes, test rerun, publication or global closure is authorized by this scope note.

## Continuidad y estado comprobado

«Sigue» autoriza avanzar en la preparación del siguiente corte. No revoca P0 ni
elige implícitamente entre alcances materiales. D1–D4 cerrados y el hito local
D5-LOCAL-SYNTHETIC-I1-I20 aceptado mantienen alcance y evidencia. D5 global,
G01–G07 y la revisión global de los cinco criterios permanecen abiertos.

Git al iniciar: árbol limpio, main diez commits por delante de la referencia
local origin/main. No se ha consultado de nuevo el remoto; el tracking local no
acredita su estado actual. La preparación inicial solo incorporó esta nota; el corte I41 añade ahora contrato, matriz y sello documental.

Los **42 inputs públicos y tres documentos/lecturas propios** sellados en I40
coinciden con los bytes actuales. Es verificación documental, no repetición de
DF/DR/EA ni de pruebas SQL. Los dictámenes I40 se conservan: GI33/GI34/GI38/GI39
parciales, GI40 con soporte acotado; ningún cierre o ampliación de A52.

La revisión distingue lagunas de cobertura de fallos del runtime. DF14 no acredita
SIGKILL en el hueco efecto/proyección; DF39/DR32 son secuencias de ledger, DF36/DR33
editan antes de UPDATE y DF37 repite CREATE secuencialmente. Las carreras reales
de HEAD y execute/cierre no acreditan esas otras carreras por analogía. No se
deduce persistencia o recuperación integrada de PASS aislados.

## Opciones concretas de diseño

El usuario eligió **A**, carreras H03 priorizadas. El
[contrato I41](D5-I41-DURABLE-CONCURRENCY-DESIGN.md) y la
[matriz HC01–HC24](D5-I41-DURABLE-CONCURRENCY-REVIEW.md) concretan ese corte.
La elección autoriza su preparación, no implementar o ejecutar sus casos.
Las alternativas siguientes conservan el planteamiento de la decisión.

**A — Recomendada: carreras H03, priorizadas y acotadas.** Preparar contrato/matriz
para respuesta frente a consulta/revocación y EDIT frente a UPDATE en T/R. Fijar
actores/autoridades, punto de barrera, estado/payload/versiones iniciales, ambas
ordenaciones deliberadas, resultado admitido y oráculo independiente. Diferenciar
secuencia controlada y competencia simultánea; no confiar en azar o sleeps para
demostrar el orden. La doble emisión/CREATE de H03 se inventariará como pendiente
separado si no cabe en este corte: no atribuirla a los casos anteriores. Mantener
evidencia futura propia con raw y metadatos pertinentes, sin reescribir I34/I36.

**B — Alternativa: cortes de fallo H02.** Preparar contrato/matriz del SIGKILL entre
efecto y binding/proyección, fases de fuente/revisión anteriores a APPLY_BATCH R
y pérdida de prueba antes de RESULT partiendo de UNKNOWN. Fijar explícitamente
qué fronteras se añaden y qué queda fuera; no anunciar «cada frontera» a partir
de contadores o repetir una caída que ya parte de EFFECT_CONFIRMED.

**C — Alternativa: trazabilidad futura H04/H05.** Preparar contrato/matriz de una
campaña nueva con raw anclado, hashes antes/después, contexto de ejecución y
etiquetas individuales de caso/rol/operación/modo/punto/oráculo. No reconstruir
raw histórico I34/I36 ni presentar la nueva ejecución como la original. Este
corte no subsanaría por sí solo las carreras H03 o fronteras H02 ausentes.

La elección autoriza **preparar contrato y matriz para revisión**. No autoriza
todavía código, hooks de kernel/harness, reejecución de campañas o correcciones
documentales de informes históricos. La futura aprobación de implementación
debe nombrar el perímetro, recursos y regresiones concretos. El hecho de preparar
metadatos de una campaña nueva no amplía automáticamente el registro fijo I38.

## Publicación independiente y límites

P0 mantiene I32, handoff y posteriores sin publicar. Para una eventual decisión
separada: publicar solo I32 tendría origen exacto
`7b64d87ef45b4973a5ea80dc676f1bd2eca220f7`; incluir el handoff alcanzaría
`79c696a66f85923173650f271995c69569b50b0d`; publicar hasta I40 alcanzaría
`900e837edfdd97d0b85f1b8c8b455f5797f24fa0` e incluiría los diez commits locales
posteriores a I31. Ninguna alternativa está autorizada. Se comprobarían remoto,
ascendencia y diff del SHA concreto antes de actuar; nunca push de todo HEAD por
una autorización limitada.

Sin proveedores/credenciales reales, corpus privado, consumo/reservas, operaciones,
activación, promoción, despliegue ni D6. Sin inspección o limpieza de dev/run_data/
D4 operativo. Docs y los siete criterios reales permanecen pendientes; no
convertir automáticamente 30/35 en 35/35 ni crear un cierre global D5.
