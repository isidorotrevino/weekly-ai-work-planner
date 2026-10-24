# D5 I49 — siguiente corte tras la revisión I48

Fecha: **2026-10-24**, Europe/Madrid. **AWAITING_SCOPE_SELECTION**.
Base: `4fb66473efbb8fbe5934da96e3484ce34d9ae711`.
[Resultado I48](../validation/D5-I48-results.md) ·
[Matriz de 84 partes](../validation/D5-I48-matrix.md) ·
[Registro I48](../validation/D5-I48-results.json) ·
[Handoff](../../HANDOFF-D5-I32.md).

«Continúa» permite preparar la siguiente decisión. No selecciona uno de estos
alcances materiales ni autoriza publicación. Elegir A/B/C autorizará preparar
contrato y matriz del corte elegido; después se decidirá sobre ese alcance
concreto antes de implementar o ejecutar una campaña. Este documento no contiene
un contrato aprobado ni una nueva revisión semántica.

## Estado verificado

Git inicial limpio, main con 18 commits por delante del seguimiento local
origin/main `8e90a87cce7edbefc6c854a73ff1f60a20ae8485`, cuya ascendencia se comprobó.
Sin fetch ni consulta nueva del remoto: este tracking no acredita su estado actual.
Se verificaron por SHA-256 las 159 entradas y los tres documentos sellados por
I48, sin reejecutar auditor, producto, harness o pruebas.

I48 conserva diez partes PARTIAL: UI01.2, UI04.1, UI09.2, UI20.3, UI22.2,
UI26.2, UI27.2, UI30.2, UI33.2 y UI34.3. Sus 74 SUPPORTS_BOUNDED son valoraciones
documentales acotadas. GI33/GI34/GI38/GI39 siguen PARTIAL y GI40 conserva soporte
acotado; todos mantienen revisión global OPEN y closure=false. D5 y G01–G07
siguen abiertos; no se promueve el 30/35.

## Opciones para contrato y matriz

**A — Recomendada: incertidumbre durable H07 / UI20.3 / GI38.**
Precisar la correspondencia de múltiples coincidencias y 429 ambiguo de I28 con
la API durable T/R de prueba única y UNKNOWN. El diseño deberá separar: hechos
representables por las APIs actuales, negativos inyectables sin alterar producto,
y capacidades ausentes que requerirían un cambio de modelo aprobado aparte.
Fijar identidad del ticket/prueba, ausencia frente a ambigüedad/conflicto, ledger,
reapertura y conciliación explícita, con oráculos y límites por recorrido. No
crear una etiqueta AMBIGUOUS_429 sobre un caso distinto para aparentar cobertura;
no transferir PASS volátil PC08/PC26 ni justificar reenvío por ausencia de prueba.

La lectura preparatoria localiza DUPLICATES/AMBIGUOUS_429 en plane_fixture y sus
tests volátiles. Remote.lookup durable devuelve una prueba por ticket o None;
Client.reconcile T/R convierte DurableError/OSError en prueba ausente antes de
RESULT. Esto orienta la pregunta del contrato, no resuelve por sí solo UI20.3 ni
autoriza añadir listas, códigos de proveedor o una API nueva.

**B — Revocación durante llamada REMOTE / UI30.2 / GI39.**
Diseñar el intercalado que HC05–HC08 no observa: barrera mientras la operación
remota está realmente en curso, revisión confirmada por separado y continuación
controlada hasta prueba/resultado. Definir T/R, operación y autoridad exactas,
órdenes relevantes, hecho remoto frente a vigencia STALE, conservación de UNKNOWN
cuando proceda y ausencia de retry/rollback automáticos. No llamar «durante
REMOTE» a una carrera RESULT/REVIEW posterior al efecto ni incluir por analogía
cambios de origen, cuenta, perfil o todas las variaciones relacionales.

**C — Precisar el pendiente de tickets / UI33.2 / GI39.**
Preparar contrato y matriz que distingan dos propuestas ISSUE, duplicación de
entrega del mismo ticket emitido y dos tickets efectivamente autorizados. Fijar
cuál exige la obligación original y cuál admite el modelo actual, sin introducir
una obligación nueva por interpretación de I48. IC21–IC24 permanece negativo solo
REMOTE con ticket extra no emitido; no se concilia ni adopta como integración.
Si la necesidad excede el modelo actual, documentar el límite y la decisión
material necesaria antes de diseñar una ampliación de autoridad.

A atiende H07, que sigue sin evidencia durable específica tras las ampliaciones
HC/HF/IC. B y C son alternativas concretas sobre GI39. UI01.2/UI04.1 históricos no
se reparan fabricando raw I34/I36; UI09.2 no requiere reabrir D1–D4. Ninguna opción
cierra automáticamente esos pendientes ni selecciona un segundo corte implícito.

## Publicación: decisión independiente

P0 conserva sin publicar I32, handoff y posteriores. Estos son destinos concretos
para una propuesta separada, **ninguno autorizado por continuar o elegir A/B/C**:

| Alcance | SHA exacto | Base de comparación local |
|---|---|---|
| Solo hasta I32 | `7b64d87ef45b4973a5ea80dc676f1bd2eca220f7` | origin/main en I31 |
| Hasta handoff | `79c696a66f85923173650f271995c69569b50b0d` | origin/main en I31 |
| Todo hasta I48 | `4fb66473efbb8fbe5934da96e3484ce34d9ae711` | Los 18 commits locales posteriores al tracking I31 |

I49 no está contenido en esos destinos. Una decisión posterior especificará SHA
y rama/destino; antes de publicar se verificarán remoto, ascendencia y diff del
rango autorizado. Autorizar un SHA limitado no autoriza push del HEAD completo.
No se ejecuta fetch, push ni creación de PR en esta preparación.

## Continuidad y exclusiones

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado se conservan. D5 global,
G01–G07 y revisión global de GI33/GI34/GI38/GI39/GI40 abiertos. No se deduce
persistencia ni recuperación integrada de PASS aislados.

Sin proveedores/credenciales reales, corpus privado, consumo/reservas, operaciones,
activación, promoción, despliegue o D6. Sin inspeccionar/limpiar dev/run_data/D4
operativo. Solo dos documentos nuevos de preparación, sin código de producto o
harness, contratos históricos alterados, auditor o pruebas ejecutados.
