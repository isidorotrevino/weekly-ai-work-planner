# Documentation / Documentación

[Project introduction](../README.md) · [Presentación en español](../README.es.md)

## Local development / Desarrollo local

[Development guide / Guía de desarrollo](DEVELOPMENT.md): persistent synthetic
Compose environment, loopback HTTPS, manual rebuild and selective reset.
[Validation / Validación](validation/DEV-ENV-results.md).

## Continuity / Continuidad

[Next session: Docker Compose development environment and friendlier README / Próxima sesión: entorno de desarrollo Docker Compose y README más amigable](../HANDOFF-DEV-ENV.md). Handoff de origen; implementación y límites vigentes en la guía de desarrollo.

[D4 session handoff / Handoff para D4](../HANDOFF-D4.md): closed D3 baseline, worker contracts, pending decisions and next-session prompt. [Docker lab preparation / Preparación del laboratorio Docker](../testing/D4/README.md): existing regression runner and the separate synthetic D4 Compose laboratory.

[D3 session handoff / Handoff para iniciar D3](../HANDOFF-D3.md): approved baseline, reading order, scheduler scope, deliverables and a ready-to-use prompt.

## D5 iniciado / D5 started

[Ingesta local y previsualización I1](design/D5-LOCAL-PREVIEW.md): primer corte
autorizado, sin activar tareas ni conectar proveedores. [Uso](../testing/D5/README.md)
y [evidencia I1](validation/D5-I1-results.md).
[I2: registro tabular y comparación](design/D5-REGISTER-COMPARISON.md), con
[evidencia propia](validation/D5-I2-results.md).
[I3: compatibilidad optativa y anotaciones](design/D5-REGISTER-COMPATIBILITY.md),
con [evidencia independiente](validation/D5-I3-results.md).
[I4: contrato de persistencia](design/D5-PERSISTENCE-DESIGN.md),
[revisión](design/D5-PERSISTENCE-REVIEW.md) e
[implementación del laboratorio sintético](design/D5-I4-PERSISTENCE-LAB.md), con
[evidencia propia](validation/D5-I4-results.md). Propuesta V31 aplicada únicamente
en bases D5 desechables; sin promoción.
[I5: comparación SQL, revisión por fila y simulación](design/D5-I5-REVIEW-SIMULATION.md),
con [evidencia independiente](validation/D5-I5-results.md). Sin aplicación operativa
a tareas o requisitos.
[I6: coexistencia SQL D5/V30](design/D5-I6-V30-COMPATIBILITY.md), con
[evidencia propia](validation/D5-I6-results.md), valida V1–V30 seguido de V31/V32
en otro laboratorio desechable.
[I7: contrato propuesto de mapeo a tareas D2](design/D5-I7-TASK-MAPPING-DESIGN.md) y
[matriz para revisión](design/D5-I7-TASK-MAPPING-REVIEW.md): diseño solamente, sin
SQL nuevo ni escrituras en tareas. D5 abierto; D6 pendiente.
[I8: implementación sintética del contrato aprobado](design/D5-I8-SYNTHETIC-TASK-LAB.md),
con [evidencia nueva](validation/D5-I8-results.md): V33 solo en laboratorio V30
desechable, tareas BACKLOG sin activación; ajuste de fecha registrado en D5.
[I9: contrato de bootstrap inicial](design/D5-I9-BOOTSTRAP-DESIGN.md) y
[matriz B01–B28 para revisión](design/D5-I9-BOOTSTRAP-REVIEW.md): diseño solamente,
sin SQL nuevo ni tareas; selección explícita y revisión propia del manifiesto.
[I10: bootstrap sintético aprobado](design/D5-I10-BOOTSTRAP-LAB.md), con
[evidencia propia](validation/D5-I10-results.md): V34 solo en otro laboratorio
V30 desechable, con continuidad hacia I8 y sin activar trabajo.
[I11: contrato de reaparición de IDs](design/D5-I11-REAPPEARANCE-DESIGN.md) y
[matriz R01–R30](design/D5-I11-REAPPEARANCE-REVIEW.md): diseño para revisión,
sin SQL nuevo; identidad declarada y ausencia aplicada con control de versión.
[I12: reaparición sintética aprobada](design/D5-I12-REAPPEARANCE-LAB.md), con
[evidencia propia](validation/D5-I12-results.md): V35 solo en otro laboratorio V30,
sin crear tareas durante la reaparición ni activar trabajo.
[I13: contrato de resolución de ediciones locales](design/D5-I13-LOCAL-EDIT-DESIGN.md)
y [matriz L01–L32](design/D5-I13-LOCAL-EDIT-REVIEW.md): diseño para revisión,
sin SQL nuevo; elección completa origen/local para cambios presentes, sin excepción
permanente ni extensión a reaparición con edición local.
[I14: resolución local sintética aprobada](design/D5-I14-LOCAL-EDIT-LAB.md), con
[evidencia propia](validation/D5-I14-results.md): V36 solo en otro laboratorio V30,
elección revisada origen/local y continuidad bajo los controles anteriores.
[I15: contrato de adopción explícita](design/D5-I15-ADOPTION-DESIGN.md) y
[matriz A01–A34](design/D5-I15-ADOPTION-REVIEW.md): diseño para revisión,
sin SQL nuevo; conservar tarea existente y materializar correspondencia/procedencia
solo al aplicar el paquete aprobado.
[I16: adopción sintética aprobada](design/D5-I16-ADOPTION-LAB.md), con
[evidencia propia](validation/D5-I16-results.md): V37 solo en otro laboratorio V30,
correspondencia/procedencia atómicas y ninguna escritura en la tarea adoptada.
[I17: contrato de reaparición con divergencia local](design/D5-I17-LOCAL-REAPPEARANCE-DESIGN.md)
y [matriz LR01–LR36](design/D5-I17-LOCAL-REAPPEARANCE-REVIEW.md): diseño para revisión,
sin SQL nuevo; prueba de ausencia e identidad conservadas y resolución origen/local
mediante una revisión conjunta del manifiesto completo.
[I18: laboratorio de resolución local de reaparición](design/D5-I18-LOCAL-REAPPEARANCE-LAB.md),
con [evidencia propia](validation/D5-I18-results.md): V38 solo en otra base V30
sintética, elección origen/local conjunta y conservación de identidad y ausencia.
[I19: contrato de resolución local aislada](design/D5-I19-ISOLATED-LOCAL-EDIT-DESIGN.md)
y [matriz IL01–IL36](design/D5-I19-ISOLATED-LOCAL-EDIT-REVIEW.md): diseño para revisión,
sin SQL nuevo; snapshot presente idéntico a la base aplicada, revisión propia y
avance de versión conservando la base del origen; ausencia aplicada vigente bloqueada.
[I20: laboratorio de resolución local aislada](design/D5-I20-ISOLATED-LOCAL-EDIT-LAB.md),
con [evidencia propia](validation/D5-I20-results.md): V39 solo en otra base V30
sintética, prueba de cabeza aplicada y elección revisada sin comparaciones I5 ficticias.

[I21: auditoría de alcance y aceptación D5](design/D5-I21-SCOPE-AUDIT.md) y
[matriz de revisión](design/D5-I21-ACCEPTANCE-REVIEW.md): distingue el laboratorio
local sintético, las brechas de integración global y las extensiones opcionales;
[comprobaciones documentales](validation/D5-I21-audit.json). Sin SQL nuevo ni cierre D5.

[I22: propuesta de aceptación del hito local sintético](design/D5-I22-LOCAL-MILESTONE-ACCEPTANCE.md)
y [comprobaciones documentales](validation/D5-I22-acceptance-review.json): clasificación
I21 aceptada; aceptación formal del hito todavía pendiente. D5 global conserva
G01–G07 abiertos; sin SQL nuevo ni cierre global.

## Current design / Diseño vigente

**D4 sintético aprobado y cerrado:** [diseño vigente](design/D4-approved.md) y
[manifiesto](validation/D4-CLOSURE.json). Los cortes siguientes y sus informes
conservan el estado histórico al emitirse. Implementación: [workers y contratos](design/D4-workers-draft.md),
[decisiones aceptadas y pendientes](design/D4-DECISIONS.md),
[preparación ejecutable del laboratorio](../testing/D4/FIRST-CUT.md).
Sin promoción ni despliegue. [I2 HTTPS/mTLS](design/D4-I2-HTTPS.md) entrega
un adaptador sintético probado sobre V17.
[I3 componentes de proceso/efectos](design/D4-I3-PROCESS-EFFECTS.md) añade supervisor
y diario sintético probados; [I4](design/D4-I4-LAB.md) los conecta con D2/HTTPS,
Compose y un verificador independiente.
[I1 entrega durable y validación](design/D4-I1-DELIVERY.md) implementa persistencia
propuesta V16; [continuidad parcial](design/D4-CHECKPOINT-CONTINUATION.md) tiene una
implementación acotada aprobada en I5. I8/I9/I11 amplían multicuentas y reconciliación;
[I12](design/D4-I12-INTEGRATED-VERIFIERS-PRESENCE.md) integra verificadores Java y presencia
durable. La [revisión final](design/D4-I12-ACCEPTANCE-REVIEW.md) precede a la
aprobación expresa registrada en el manifiesto de cierre.

| Document | Purpose / Propósito |
|---|---|
| [D1 architecture baseline](design/D1-architecture-baseline.md) | Approved functional architecture / Arquitectura funcional aprobada |
| [D2 decision register](design/D2-DECISIONS.md) | Approved decisions and closure / Decisiones y cierre aprobados |
| [D2 approved design](design/D2.9-approved.md) | Approved domain/PostgreSQL design, in Spanish / Diseño vigente aprobado |
| [D3 approved conservative MVP 1.0](design/D3-approved.md) | Approved and closed on 2026-10-19 / Aprobado y cerrado; sin despliegue |
| [D3 closure manifest](validation/D3-CLOSURE.json) | Explicit approval and evidence hashes / Aprobación y hashes de evidencia |
| [D3 capacity scheduler v0.2](design/D3-capacity-scheduler-draft.md) | Design baseline with historical approval sequence / Base de diseño e historial; estado vigente en D3 aprobado |
| [D3 accepted scope and optimization](design/D3-OPTIMIZATION.md) | 1A/2A accepted, equivalent slot optimization and repeated measurements / Alcance aceptado, optimización y nuevas medidas |
| [D3 optimization evidence](validation/D3-OPTIMIZATION-results.json) | Differential comparison, scale and regression groups / Comparación diferencial, escala y regresiones |
| [D3 integrated review](design/D3-REVIEW.md) | Contract coverage, V15 reopening fix and historical scope/performance proposals / Cobertura, corrección V15 y propuestas históricas |
| [D3 review evidence](validation/D3-REVIEW-results.json) | Separate integration/regression groups and measured scale fixtures / Integración y mediciones separadas |
| [D3 implementation status](design/D3-IMPLEMENTATION.md) | Core, publication, dispatch and callable coordination / Núcleo, publicación, despacho y coordinación invocable |
| [D3 I2 persistence](design/D3-I2-PERSISTENCE.md) | Immutable snapshots and transactional publication / Snapshots inmutables y publicación transaccional |
| [D3 I3 dispatch](design/D3-I3-DISPATCH.md) | Guarded mapping/CLAIM and lifecycle / Mapping/CLAIM y ejecución protegidos |
| [D3 coordinator](design/D3-COORDINATOR.md) | Durable callable ticks, batching, recovery and bounded retries / Ticks, agrupación, recuperación y recálculos acotados |
| [D3 coordinator results](validation/D3-COORDINATOR-results.json) | Separate core/I2/I3/coordinator/D2 groups / Grupos separados |
| [D3 I3 results](validation/D3-I3-results.json) | Historical dispatch evidence / Evidencia histórica de despacho |
| [D3 I2 results](validation/D3-I2-results.json) | PostgreSQL integration and separate D2 regression / Integración PostgreSQL y regresión D2 separada |
| [D3 Java test results](validation/D3-I1-results.json) | JUnit evidence for the implemented core / Evidencia JUnit del núcleo implementado |
| [D3 decision register](design/D3-DECISIONS.md) | Approved rules and implementation authorization / Reglas y autorización de implementación aprobadas |
| [D3 synthetic experiment](../testing/D3/README.md) | Bounded arithmetic validation and limitations / Validación aritmética acotada y límites |
| [D3 portable results](validation/D3-v0.2-results.json) | New evidence kept separate from D2 / Evidencia nueva separada de D2 |
| [Validation overview](validation/README.md) | How to interpret and reproduce the checks / Alcance y reproducción |
| [D2 validation matrix](validation/D2-VALIDATION-MATRIX.md) | Requirements, evidence, and limitations / Requisitos, evidencia y límites |
| [Portable results](validation/latest-results.json) | Recorded environment and counts, without machine-specific data / Resumen sin datos del equipo |

D1 and D2 are approved; D2 closed after successful validation and conditional user approval. Older documents contain statements that were accurate when written; use the consolidated review and validation overview for the current status. Migration paths in the design documents are relative to the repository root.

D1 y D2 están aprobados; D2 se cerró tras validar la condición de aprobación del usuario. Los documentos históricos reflejan su momento de redacción; consulta la consolidación y la validación para el estado vigente. Las rutas de migraciones indicadas en los documentos parten de la raíz del repositorio.

## Design history / Historial

- [Original domain model](design/history/D2-domain-model-draft.md).
- [D2.3 — state, capacity, recovery](design/history/D2.3-state-capacity-recovery.md).
- [D2.4 — transitions and test plan](design/history/D2.4-transitions-integrity-tests.md).
- [D2.5 — integrity proposal](design/history/D2.5-integrity-proposal.md).
- [D2.6 — physical capacity and transactions](design/history/D2.6-capacity-transaction-contract.md).
- [D2.7 — relational corrections](design/history/D2.7-relational-corrections.md).
- [D2.8 — consolidated review before SemVer validation](design/D2.8-consolidated-review.md).
- [Archived SQL mirrors](archive/sql-markdown/README.md).

The original D1, D2 v0.4 documents, V1–V4 SQL, and SQL mirrors retain their content after relocation. Original import manifests, handoffs, and raw evidence remain local in ignored directories. The test harness reads the relocated D2.4 transition specification directly.

El contenido de D1, los documentos originales de D2 v0.4, SQL V1–V4 y sus mirrors se conserva tras la reorganización. Los manifiestos de importación, handoffs y evidencia bruta permanecen locales, fuera de Git. Las pruebas leen directamente la especificación D2.4 reubicada.

[D4 I4 integrado](design/D4-I4-LAB.md): control plane HTTPS/D2, dos workers, receptor
durable y verificador separados en Compose; [resultados I4](validation/D4-I4-results.json).
D4 abierto; I5 añade continuidad de checkpoint acotada. Sin promoción/despliegue.

[D4 I5: contrato aprobado A/A](design/D4-I5-REVIEW.md) e
[implementación sintética acotada](design/D4-I5-CHECKPOINT-LAB.md): checkpoint parcial
y continuación con nueva generación, sin cierre de D4.

[D4 I6: ejecución prolongada y cooperación](design/D4-I6-LONG-RUNNING-LAB.md):
renovación D2/HTTPS, watchdog independiente y checkpoint con proceso vivo;
[resultados S01–S09](validation/D4-I6-results.json), 283 comprobaciones y 416 pruebas
JUnit separadas D4/D3/D2. D4 sigue abierto; generalización y
verificadores genéricos permanecen pendientes. I7 incorpora el polling normal.

[D4 I7: polling normal](design/D4-I7-POLLING-LAB.md) y
[resultados S01–S12](validation/D4-I7-results.json): 367 comprobaciones, 92 pruebas
D4 y regresión histórica separada D3/D2. Polling vacío con backoff, espera de
aceptación independiente, retirada y recuperación explícita; A12 exige pausa
completa tras checkpoint y rearme explícito, con [evidencia S13 separada](validation/D4-I7-A12-results.json). Sin cierre de D4.

[I8.1: componentes de generalización y verificadores](design/D4-I8-COMPONENTS.md)
bajo A13–A15; aquel corte mantiene evidencia de componentes.
[I8.2: integración multicuentas](design/D4-I8-INTEGRATION.md) añade el puente
SQL/HTTPS V24 y la campaña Compose acotada, con D4 abierto.

[Revisión de V24 y corrección aditiva V25](design/D4-V25-BOUNDARY-LAB.md):
tipos JSON, esquema cerrado aprobado A16 y comprobación de lease después de liquidar;
V24 permanece intacta.

[I9: reconciliación concluyente](design/D4-I9-RECONCILIATION-LAB.md) implementa A17–A19 con V26 propuesta y evidencia separada; D4 abierto.

[I10.1 D4: ausencia sin progreso y retry explícito](design/D4-I10-ABSENCE-LAB.md)
separa la implementación A20 de las revisiones/cuarentena A21/A22 pendientes.

[I11 D4: revisiones A21 y cuarentena A22](design/D4-I11-REVIEW-QUARANTINE-LAB.md)
integra la reapertura separada y las campañas de contención; D4 permanece abierto.

[D4 I12 — verificadores Java, presencia durable y matriz actual](design/D4-I12-INTEGRATED-VERIFIERS-PRESENCE.md).
