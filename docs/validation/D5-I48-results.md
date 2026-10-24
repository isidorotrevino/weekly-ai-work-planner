# D5 I48 — revisión documental de suficiencia

Fecha: **2026-10-24**, Europe/Madrid. Contrato I47 aprobado mediante selección **A**; ejecución limitada a lectura/Git/JSON/AST/hashes. Base local: `f7826c1cc770ffbaf1b0b58ca10abb3eb2c24f17`.

La revisión de **40 UI, 84 subcláusulas, 14 SR y 12 DC** está completa. El resultado es **74 SUPPORTS_BOUNDED y 10 PARTIAL**; no quedan NOT_ESTABLISHED ni aparece CONTRADICTED dentro del perímetro leído. **D5 global, G01–G07 y los cinco GI siguen OPEN, closure=false**. El soporte acotado no constituye aprobación global ni promueve el 30/35.

[Matriz y razones de cada parte](D5-I48-matrix.md) · [Registro completo](D5-I48-results.json) · [Integridad](D5-I48-integrity.json) · [Contrato](../design/D5-I47-SUFFICIENCY-DELTA-DESIGN.md) · [Baseline I40](D5-I40-results.md).

## Cambios respecto a I40

- **UI17.2: NOT_ESTABLISHED → SUPPORTS_BOUNDED.** HF31/HF32 registran SIGKILL after_head de APPLY/APPLY_BATCH antes de BIND. El lector nuevo observa efecto/recibo sin binding/proyección/envío; replay no duplica y la continuación explícita crea proyección revisada sin ISSUE. BIND T incrementa su propia generación; no se inventa flag F3/F4.
- **UI31.2: PARTIAL → SUPPORTS_BOUNDED.** HC09–HC12 compiten EDIT con versión fijada contra UPDATE, en T/R y ambos órdenes. Oráculos de versión, HEAD, recibos, resultado NO_EFFECT/REMOTE_CAS y campos ajenos distinguen cada rama. La versión se fija en Store.transact, sin atribuirlo al selector dinámico de Remote.edit.
- **UI32.2: NOT_ESTABLISHED → SUPPORTS_BOUNDED.** HC01–HC08 fijan barreras para RESULT/QUERY y REVIEW en ambos órdenes T/R; distinguen CONFLICT_HEAD, CONFLICT_LEDGER y followup explícito. El probe muestra lock ocupado, sin probar entrada al flock bloqueante.

Las otras **81** valoraciones se conservan con razón propia y referencias. UI33.2 amplía soporte con competición de propuestas ISSUE y doble entrega del mismo ticket emitido, pero permanece **PARTIAL**: IC21–IC24 agrega un ticket no emitido como negativo REMOTE, conserva CLIENT UNKNOWN/1 y omite conciliación; no completa dos tickets autorizados integrados.

## Pendientes y límites

Las diez partes parciales son **UI01.2, UI04.1, UI09.2, UI20.3, UI22.2, UI26.2, UI27.2, UI30.2, UI33.2, UI34.3**. Abarcan contexto/trazabilidad históricos, targets no exhaustivos, múltiples coincidencias/429 ambiguo durable, amplitud de fronteras, cambios concurrentes de origen/perfil/cuenta, revocación durante REMOTE, dos tickets autorizados integrados y variaciones relacionales con entrega.

HC05–HC08 ejecuta el efecto remoto antes de competir RESULT/REVIEW: no prueba revocación durante la llamada remota. HF amplía puntos concretos SOURCE/BATCH, hueco local y primera reconcile desde UNKNOWN CREATE; no acredita todas las combinaciones F1–F7 ni modos. after_query aún no observó P; before_result sí.

H01–H08 se conservan como registros históricos, con delta por parte. Raw I34/I36 sigue **NOT_RECORDED**. I38 no se reejecutó ni amplió su registro fijo. El contexto amplio de regresión I42 difiere en tres archivos HC del estado final; los 78 inputs del runner efectivo sí coinciden. Los nuevos metadatos no reparan retrospectivamente los antiguos.

## Evidencia y contabilidad

Los 94 casos finales HC24/HF40/IC30 resuelven a **97 escenarios** por controles T/R. Se verificaron **406 anclajes de fuente** con símbolo/líneas/hash/commit, **2.759 punteros** de eventos/oráculos y **123 comprobaciones documentales** sobre sus registros. Cada caso dinámico identifica factory, parámetros y línea de registro estático. Los retornos resumidos por hash no se presentan como volcados completos de cada proof; las aserciones se citan como evidencia de código.

Las nueve campañas históricas se mantienen separadas: I42 HC24 + Python321; I44 HF40 + HC24 + Python321; I46 IC30 + HC24 + HF40 + Python321. Las intersecciones de IDs están registradas; no se suman regresiones, actores, escenarios, probes o recibos como tests nuevos. HF tiene 32 SIGKILL positivos y 12 OSError en seis filas; sus dos kills de timeout negativo no son fronteras positivas. Recursos restantes en cero describen cada campaña propia, no certifican host/dev/D4.

El desarrollo HC10/HC12 con expectativa errónea del harness se conserva separado de la campaña final; los snapshots de desarrollo no están todos versionados. Los ensayos enfocados/preliminares no se añaden al conteo final ni se reconstruye su raw ausente.

## Validación y continuidad

**Cero tests, campañas o auditor ejecutados en I48.** Solo se leen fuentes/evidencia; se validan inventarios, JSON/AST, hashes, blobs Git, referencias, agregados, enlaces locales, whitespace e higiene documental. La comprobación de integridad de I48 no es una campaña funcional ni certificación de suficiencia universal.

El estado Git inicial era main limpio, **17 commits por delante** del seguimiento local origin/main `8e90a87cce7edbefc6c854a73ff1f60a20ae8485`, sin consultar el remoto. Los nuevos documentos I48 se guardarán en un commit local separado. Publicación requiere decisión separada sobre el rango concreto desde ese seguimiento hasta el commit I48 resultante; ni I32, handoff ni cambios posteriores tienen autorización de publicación. No se hizo fetch/push/PR.

D1–D4 cerrados y **D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado** permanecen. P0 conserva exclusiones: proveedores/credenciales reales, corpus privado, consumo/reservas, activación, promoción, despliegue y D6. No se deduce persistencia ni recuperación integrada de PASS aislados.
