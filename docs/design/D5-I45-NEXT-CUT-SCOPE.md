# D5 I45 — siguiente corte tras I44

Fecha: **2026-10-24**, Europe/Madrid. **A seleccionado; diseño preparado para revisión**.
Base: `71d142898ecedb4f1c44fc89ecedaa5d31bb81f5`.
[Resultados I44](../validation/D5-I44-results.md) ·
[Sello I44](../validation/D5-I44-results.json) ·
[Resultados I42](../validation/D5-I42-results.md) ·
[Hallazgos I40](../validation/D5-I40-results.json).

«Continúa» autoriza preparar la decisión siguiente. La A anterior autorizó I44,
no un alcance material nuevo ni publicación. El usuario eligió ahora A. El
[contrato](D5-I45-DURABLE-ISSUE-CREATE-DESIGN.md) y la
[matriz IC01–IC30](D5-I45-DURABLE-ISSUE-CREATE-REVIEW.md) concretan el diseño.
No implementa código, ejecuta campañas o modifica producto/evidencia histórica.
Las alternativas siguientes conservan el planteamiento de la decisión.

## Estado e integridad comprobados

Git inicial limpio, HEAD indicado arriba y main catorce commits por delante de
la referencia **local** origin/main, aún en
`8e90a87cce7edbefc6c854a73ff1f60a20ae8485`. No se consultó de nuevo el remoto;
no se presenta el tracking como estado remoto verificado.

Lectura/verificación SHA-256 sin pruebas: 100 inputs y cinco artefactos I44;
26 inputs I43; 91 inputs y cinco artefactos I42; 42 inputs públicos y tres
documentos I40. Todos coinciden. La verificación no reejecuta campañas, cambia
sus dictámenes o convierte snapshots de desarrollo/contextos no aplicables en
CURRENT. La campaña I44 ya registrada conserva sus tres grupos separados:
40 HF propios, 24 HC y 321 Python de regresión; no se suman como prueba integrada.

I42 amplió evidencia acotada de respuesta/consulta/revocación y EDIT/UPDATE. I44
amplió fronteras tempranas R, oráculo del hueco local y primera conciliación R
desde UNKNOWN. Sus repeticiones de controles históricos no son lagunas inéditas.
H02 no se cerró globalmente; CREATE no acredita UPDATE/CLOSE, y SIGKILL/OSError
no acreditan energía/disco/NFS/Windows/caller hostil. H03 restante, H07 y límites
históricos H04/H05 continúan explícitos. No se infiere persistencia/recuperación
integrada a partir de PASS aislados.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. D5 global,
G01–G07 y revisión global GI33/GI34/GI38/GI39/GI40 abiertos; sin promoción
30/35→35/35, cierre automático o capacidad real deducida de fixtures.

## Opciones de diseño

**A — Recomendada: doble ISSUE/CREATE pendiente de H03/GI39 en T/R.** Preparar
contrato/matriz de actores, autoridades, misma orden repetida frente a comandos
distintos, HEAD/ledger fijados, send/ticket/creation_key y payload/identidad
esperados. Separar competencia de ISSUE en CLIENT de EXECUTE/creación en REMOTE,
fijar ambas ordenaciones deliberadas con hooks existentes y oráculos independientes.
Distinguir ticket repetido de tickets diferentes para la misma identidad de
creación; no asumir por adelantado qué conflictos bastan. No extrapolar las
carreras I42 o el CREATE secuencial DF37 a esta competencia. Otras revocaciones,
cuenta/perfil/origen/grooming siguen fuera salvo nueva decisión explícita.

**B — Alternativa: incertidumbre durable H07/GI38.** Preparar contrato/matriz para
resolver la correspondencia de la prueba única/UNKNOWN T/R con múltiples
coincidencias/429 ambiguo de I28. Distinguir revisión semántica, escenarios
representables por la API pública y cambios de modelo que exigirían otra
aprobación. No transferir los PASS volátiles PC08/PC26 a la unión durable ni
fabricar capacidades de proveedor real mediante etiquetas de fixture.

**C — Alternativa: revisión documental del delta I42/I44 frente a I40.** Preparar
contrato/matriz para contrastar obligaciones afectadas con código, pruebas,
raws, pre/post hashes y límites de las tres campañas. Separar obligación
previamente cubierta, oráculo nuevo, repetición y pendiente; identificar qué
subcláusulas requieren más evidencia. Preservar I40/I42/I44, emitir informe nuevo
si se aprueba su ejecución y conservar revisión global abierta. No sustituir
análisis de suficiencia por conteos de tests ni ejecutar campañas dentro de una
revisión documental.

A/B/C autorizan **solo preparar contrato y matriz** para revisión. Antes de
implementar o ejecutar deben concretarse archivos, límites, hooks/lectores,
oráculos, evidencia y regresiones del corte elegido. Si aparece necesidad de
cambiar producto, no se presume autorizada. El registro fijo I38 no se amplía
por generar otra campaña.

## Publicación separada y límites permanentes

P0 mantiene I32, handoff y posteriores sin publicar. Posibles destinos para una
decisión independiente posterior, sin autorización actual:

- Hasta I32: `7b64d87ef45b4973a5ea80dc676f1bd2eca220f7`.
- Incluir handoff: `79c696a66f85923173650f271995c69569b50b0d`.
- Incluir todo hasta I44: `71d142898ecedb4f1c44fc89ecedaa5d31bb81f5`, catorce
  commits locales posteriores a I31 según el tracking disponible.

Publicar requeriría autorización del SHA concreto y comprobaciones de remoto,
ascendencia y diff; no push de HEAD entero por una autorización limitada.
El borrador I45 no está contenido en esos SHA. Elegir A/B/C no publica nada.

Sin proveedores/credenciales reales, corpus privado, consumo/reservas, operaciones,
activación, promoción, despliegue, D6 o inspección/limpieza de dev/run_data/D4 operativo.
