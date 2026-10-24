# D5 I53 — matriz dirigida y continuidad de I48

Fecha: **2026-10-24**. [Resultado](D5-I53-results.md) · [Fuentes y punteros](D5-I53-results.json).

**Seis partes revisadas; 78 heredadas sin reevaluación.** Declaración MAPPED y ejecución histórica REGISTERED_PASS se conservan separadas de la valoración semántica. Runtime nuevo NOT_RUN.

## Dictamen por parte revisada

| Parte / obligación I48 | I48 → I53 | Motivo y límite | Evidencia nueva leída |
|---|---|---|---|
| UI01.2 — Entorno/comando/run_id y resultado por escenario | PARTIAL → PARTIAL | RV/IC/UQ y sus contextos separados registran run/comando/build/optimización/debug e inputs pre/post. No aportan el raw/contexto original ausente I34/I36; I32 conserva integridad histórica con dos índices cambiados posteriormente. Se conserva PARTIAL respecto a la obligación histórica completa. | CP01/CP05; anexos públicos y UQ I50/I52, sin nueva ejecución |
| UI04.1 — Relación completa escenario/frontera/inputs/oráculo/resultado | PARTIAL → PARTIAL | Los enlaces I52 caso/método/autoridad/campo raw son resolubles y conservan causalidad del mismo ticket. El stdout original I34/I36 sigue NOT_RECORDED y no toda parametrización histórica tiene etiqueta empírica distinta. La trazabilidad futura mejorada no reconstruye campañas anteriores: PARTIAL. | CP01/CP05; anexos públicos y UQ I50/I52, sin nueva ejecución |
| UI09.2 — Comandos/versiones propios para todos los grupos | PARTIAL → PARTIAL | Los anexos públicos identifican D1 v1.0 como baseline de diseño sin comando ejecutable propio; D2 V1–V11 con comando/versiones; D3 con targets por grupo; D4 V30 separado de regresiones históricas. Falta normalizar exhaustivamente comandos/versiones por subgrupo del perímetro histórico I1–I20/A52. El inventario mejora, pero no se inventan valores ni se da por completo: PARTIAL. | CP01/CP05; anexos públicos y UQ I50/I52, sin nueva ejecución |
| UI20.3 — Múltiples coincidencias y 429 ambiguo específicos en T/R | PARTIAL → PARTIAL | UQ acredita pérdida antes/después de llamada sintética y rechazo de prueba malformada, no colección nativa de múltiples coincidencias ni semántica HTTP429. MG01–MG03 permanecen como límites del modelo; sin llamadas reales ni cambio de schema. PARTIAL conservado. | CP01/CP05; anexos públicos y UQ I50/I52, sin nueva ejecución |
| UI30.2 — Revocación o edición intercalada realmente durante llamada remota | PARTIAL → SUPPORTS_BOUNDED | RV05–RV16 sitúa READY dentro de Remote.execute real y confirma CLIENT REVOKE v2 antes de liberar, T/R y CREATE/UPDATE. RV01–RV04 bloquea la revocación previa. P recibida queda EFFECT_CONFIRMED + STALE; respuesta perdida conserva UNKNOWN/2 sin pending send hasta lookup explícito que confirma /3 + STALE, sin reenvío ni cambio REMOTE. Sostiene la alternativa de revocación PROJECTION dentro del perímetro aprobado; no acredita todas las ediciones ni otras autoridades. | RV01, RV02, RV03, RV04, RV05, RV06, RV07, RV08, RV09, RV10, RV11, RV12, RV13, RV14, RV15, RV16 |
| UI33.2 — Dos tickets CREATE/ISSUE simultáneos sin duplicar intento | PARTIAL → SUPPORTS_BOUNDED | UI33/DF37/F originales exigen competición y unicidad durable de intento/efecto/clave/ticket; no exigen que CLIENT emita dos tickets autorizados no resueltos para el mismo paquete, algo que su guarda prohíbe. IC05–IC08 contiene dos propuestas concurrentes cid/send/ticket distintos: un ISSUE, perdedor por HEAD y luego BINDING_UNRESOLVED con HEAD fresca. Cada caso ejecuta al ganador emitido, concilia P y reproduce historia sin rebobinar. IC17–IC20 acredita entrega duplicada del ticket emitido. IC21–IC24 conserva su exclusión: ticket extra no emitido, sólo negativo REMOTE. SUPPORTS_BOUNDED corrige esa premisa añadida en la lectura anterior, conserva texto y unicidad originales y no compone un ciclo ficticio desde PASS separados. | IC05, IC06, IC07, IC08, IC17, IC18, IC19, IC20, IC21, IC22, IC23, IC24 |

## Inventario completo: sólo dos cambios

| Parte | I48 | I53 derivado | Tipo de lectura |
|---|---|---|---|
| UI01.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI01.2 | PARTIAL | PARTIAL | TARGETED_DOCUMENTARY_REVIEW_EXECUTED |
| UI02.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI02.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI03.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI03.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI04.1 | PARTIAL | PARTIAL | TARGETED_DOCUMENTARY_REVIEW_EXECUTED |
| UI04.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI05.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI05.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI06.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI06.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI07.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI07.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI08.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI08.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI09.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI09.2 | PARTIAL | PARTIAL | TARGETED_DOCUMENTARY_REVIEW_EXECUTED |
| UI10.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI10.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI11.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI11.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI12.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI12.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI13.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI13.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI13.3 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI14.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI14.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI15.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI15.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI16.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI16.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI17.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI17.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI18.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI18.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI19.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI19.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI20.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI20.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI20.3 | PARTIAL | PARTIAL | TARGETED_DOCUMENTARY_REVIEW_EXECUTED |
| UI21.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI21.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI22.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI22.2 | PARTIAL | PARTIAL | INHERITED_I48_NOT_REREVIEWED |
| UI23.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI23.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI24.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI24.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI25.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI25.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI25.3 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI26.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI26.2 | PARTIAL | PARTIAL | INHERITED_I48_NOT_REREVIEWED |
| UI27.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI27.2 | PARTIAL | PARTIAL | INHERITED_I48_NOT_REREVIEWED |
| UI28.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI28.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI29.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI29.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI30.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI30.2 | PARTIAL | SUPPORTS_BOUNDED | TARGETED_DOCUMENTARY_REVIEW_EXECUTED |
| UI31.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI31.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI32.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI32.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI33.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI33.2 | PARTIAL | SUPPORTS_BOUNDED | TARGETED_DOCUMENTARY_REVIEW_EXECUTED |
| UI34.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI34.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI34.3 | PARTIAL | PARTIAL | INHERITED_I48_NOT_REREVIEWED |
| UI35.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI35.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI36.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI36.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI37.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI37.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI38.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI38.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI39.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI39.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI40.1 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |
| UI40.2 | SUPPORTS_BOUNDED | SUPPORTS_BOUNDED | INHERITED_I48_NOT_REREVIEWED |

## Criterios integrados

| GI | Soporte acotado derivado | PARTIAL restantes | Estado global |
|---|---|---|---|
| GI33 | PARTIAL | UI01.2, UI04.1 | OPEN; closure=false |
| GI34 | PARTIAL | UI09.2 | OPEN; closure=false |
| GI38 | PARTIAL | UI20.3, UI22.2 | OPEN; closure=false |
| GI39 | PARTIAL | UI26.2, UI27.2, UI34.3 | OPEN; closure=false |
| GI40 | SUPPORTS_BOUNDED | — | OPEN; closure=false |

## Inventario público CP01 ampliado

| Grupo | Target / referencia | Comando registrado | Ejecución I53 |
|---|---|---|---|
| D1 | Architecture baseline v1.0, approved — docs/design/D1-architecture-baseline.md | NOT_APPLICABLE_DESIGN_BASELINE | NOT_RUN |
| D2 | {'baseline': 'V1-V4', 'proposals': 'V5-V11'} — docs/validation/latest-results.json | bash testing/D2/run-docker-audit.sh | NOT_RUN |
| D3 | {'D2': 'V1-V11, unchanged', 'D3': 'V12-V15 isolated proposals, not promoted; V15 replaces only D3 event classification and appends pending-reopening correction events'} — docs/validation/D3-OPTIMIZATION-results.json | bash testing/D3/run-postgres-tests.sh | NOT_RUN |
| D4 | {'new_scenarios_V30': 30, 'historical_groups': 'Own targets preserved; not all V30'} — docs/validation/D4-I12-INTEGRATED-results.json | bash testing/D4/run-latest-matrix.sh | NOT_RUN |
| A52 | fresh V1-V30 then V31-V39; no promotion or deployment — docs/validation/D5-I20-results.json | NOT_RECORDED_AT_I20_ROOT; public runner inventory remains to be completed per subgroup | NOT_RUN |

Se conserva la distinción entre ausencia en el root y ausencia en todo el expediente. Los comandos citados se leen como evidencia histórica, no se ejecutan. El inventario global de subgrupos I1–I20 aún no se declara completo.

## Premisas que no se afirman

- Dos candidatos ISSUE concurrentes no son dos tickets autorizados emitidos; la exclusión de IC21–IC24 no cambia.
- La misma secuencia de IC05–IC08 o RV sí tiene identidad/oráculos correlacionados; sumar PASS independientes no fabrica una integración nueva.
- Sólo se soporta el perímetro de revisión PROJECTION y el modelo de intento único admitido; no cualquier autoridad/paquete/target o modo arbitrario.
- Lectura pasiva, timeout negativo, publicación o integridad de hashes no equivalen a recuperación, suficiencia universal o aceptación global.

D5/G01–G07 y todos los GI globales siguen abiertos. D1–D4/A52 intactos; cero ejecuciones nuevas y ninguna obligación real movida a D6.
