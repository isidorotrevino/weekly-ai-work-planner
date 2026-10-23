# D5 I35 — revisión del siguiente corte tras I34

Fecha: **2026-10-23**, Europe/Madrid. **SCOPE_REVIEW; sin implementación nueva.**
Base: `6a9932acec47f422249c94bc55bf83dc9a38b80b`.
[Implementación I34](D5-I34-DURABLE-TASK-LAB.md) ·
[Resultados I34](../validation/D5-I34-results.md) ·
[Contrato integrado I33](D5-I33-INTEGRATED-EVIDENCE-DESIGN.md).

English: next-cut scope review after bounded durable TASK integration. No new
runtime tests, publication, implementation authorization or global closure.

## Solicitud y preservación

El usuario pide «continúa». Se revisan los pendientes y se prepara el próximo
alcance antes de implementar; no se interpreta como autorización de publicar.
P0 sigue vigente para I32, handoff, I33, I34 y propuestas posteriores. D1–D4
cerrados y D5-LOCAL-SYNTHETIC-I1-I20 aceptado conservan alcance y evidencia.
**D5 global, G01–G07 y los siete criterios reales siguen abiertos.**

Git local limpio al iniciar: main, cuatro commits por delante de la referencia
local origin/main. No se ha consultado de nuevo el remoto en esta revisión ni
se atribuye ese tracking local a una verificación remota actual.

## Comprobaciones actuales y límite de inferencia

Los **73 inputs de campaña** y **siete inputs documentales** de I34 coinciden con
los bytes actuales. Todos los IDs referenciados en los mapas de 48 DF, 33 UI de
base y cinco UI durables pertenecen a los 281 IDs PASS registrados. Esta es una
comprobación de integridad/aplicabilidad, **no una reejecución** de esas pruebas.
I34 y sus resultados se conservan sin reescribirlos.

| Criterio | Evidencia que aporta I34 | Pendiente que no debe ocultarse |
|---|---|---|
| GI33 | Inventario/hash y aplicabilidad sobre el recorrido T; mapas de casos/inputs | Delimitar cobertura de otros recorridos y configuraciones; no inferir APIs reales |
| GI34 | Regresiones Python ejecutadas y grupos/targets históricos separados | No afirmar SQL/D1–D4 reejecutados o equivalencia de targets por comprobar hashes |
| GI38 | Reinicio/commit incierto/tickets y respuesta perdida en T durable | UI25 relacional, otras exclusiones de integración; ningún PASS aislado I30 lo satisface |
| GI39 | Carreras/CAS/revocación en T y doble remoto de fixture | UI34: cambios locales/relacionales frente al snapshot proyectado desde un lote |
| GI40 | Auditoría/limpieza selectiva de la campaña T autorizada | Auditoría nueva del siguiente alcance, sin trasladar automáticamente los conteos de I34 |

No se convierte 30/35 en 35/35 por completar una matriz de un recorrido. R significa
recorrido relacional en UI25/UI34; es distinto de la etiqueta R de siete criterios
que exigen evidencia real GI06/12/18/24/30/36/42. Diseñar R relacional no autoriza
esos casos reales, cuentas, credenciales o capacidades comerciales.

## Decisión posterior y opciones de alcance material

El usuario eligió **A**, explícitamente para diseñar R durable/UI25/UI34. El
[contrato I35](D5-I35-DURABLE-RELATIONAL-DESIGN.md) y su
[matriz DR01–DR40](D5-I35-DURABLE-RELATIONAL-REVIEW.md) concretan esa elección
para revisión; no hay implementación ni publicación autorizadas. Las opciones
siguientes conservan el planteamiento de la decisión.

**A — Propuesta recomendada:** contrato y matriz de integración relacional durable
para UI25/UI34, con inventario/auditoría propios GI33/GI34/GI40. Usar I30 como
referencia acotada, no objeto restaurable. Fijar antes esquema durable, entidades/
vínculos/base/procedencia/recibo atómicos, revisión BATCH íntegra, selección explícita
de TASK y revisión de proyección. Requisitos/épicas/relaciones no se proyectan a
Plane. El lote de origen local y las proyecciones remotas de TASK son transacciones
distintas: no prometer atomicidad distribuida ni convertir un envío parcial remoto
en rollback del lote. No pasar el JSON relacional por el perfil Markdown I32.

**B — Alternativa:** contrato y matriz de auditoría ejecutable de inventario y
aplicabilidad GI33/GI34, sin ampliar el recorrido funcional. Fijar artefactos,
versiones/targets, reglas de invalidación y oráculos para detectar evidencia
obsoleta, mapas incompletos o doble contabilidad. UI25/UI34 siguen pendientes.

La selección del corte autoriza preparar su diseño, no implementarlo. Primero
contrato/matriz revisables; después aprobación de diseño y alcance de código.
No reabrir decisiones A69/A70 de I29 por defecto, ampliar relaciones a otros
proyectos, introducir SQL o convertir correspondencias sin decisión expresa.

Sin proveedores/credenciales reales, consumo/reservas, activación, promoción,
despliegue ni D6. La publicación necesita autorización del SHA concreto por
separado; «continúa» no revoca P0.
