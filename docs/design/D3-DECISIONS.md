# D3 — registro de decisiones y autorización

Registro iniciado: 2026-10-18. Actualizado: 2026-10-19. Estado: **D3 aprobado y cerrado como MVP conservador 1.0**. Aprobación literal: «si, cierra D3». [Consolidación de cierre](D3-approved.md).
D1 y D2 siguen aprobados; D2 cerrado, referencia publicada `69d71c3`. Diseño vigente: [D3 v0.2](D3-capacity-scheduler-draft.md).

## Reglas aprobadas

| ID | Regla vigente y procedencia |
|---|---|
| P01 | Siete días civiles móviles desde as_of, Europe/Madrid y UTC al persistir; resets físicos independientes. Aprobado en la primera consulta |
| P02 | Deadlines objetivos, riesgo y prioridad por camino sin saltar guardas; deferral_allowed=false impide aplazamiento automático. Hasta 20% de PLANNED por cuenta para caminos con holgura ≤24 h. Aprobado en las consultas inicial y posterior |
| P03 | Reparto ponderado por recurso, servicio atribuido al proyecto ejecutor aunque herede prioridad; persistencia de servicio, espera elegible y uso de vías entre planes. Hasta 5% de PLANNED tras siete días elegibles; sin garantía si la operación no cabe. P4 solo por camino bloqueante de trabajo activo de mayor prioridad; PAUSED/ARCHIVED excluidos. Ante recalibración reconstruir desde hechos originales; si no es posible, nueva época explícita de equidad sin borrar contabilidad física. Elección 1A completa la consulta inicial |
| P04 | Confianza ≥0,8 tanto de límite como de estimación; coste por cuenta, duración conservadora, procedencia, calibración y caducidad obligatorios. Estimaciones manuales documentadas permitidas; confianza no equivale a probabilidad estadística demostrada. Elección 2A |
| P05 | Una operación simultánea por worker; exclusión adicional al compartir directorio de trabajo o entorno exclusivo; heartbeat fresco ≤90 s. Preferir fin más temprano, conservando recurso previo si retraso ≤10% de la duración estimada de esa operación. Reservas existentes fijan recurso/cuentas/pool. Elección 3A |
| P06 | Seguridad/SEV1/2 inmediatos, agrupación ordinaria 30 s, barrido 60 s. Proteger intención válida próxima de 15 min; romper protección por incidente crítico, invalidación, déficit, pérdida de disponibilidad, aprobación inválida o cambio explícito de prioridad. Hasta dos recálculos por obsolescencia; después diagnóstico y plan previo sujeto a guardas actuales. Elección 4A |
| P07 | SEV1/2 usan INCIDENT; SEV3/4 solo con clasificación explícita de respuesta activa en triaje; FOLLOW_UP va a PLANNED. Orden: severidad, antigüedad, desempate estable. Sin saldo INCIDENT → INCIDENT_SHORTFALL visible sin tomar PLANNED; UNCERTAINTY no se gasta y BORROW conserva las guardas globales D2. Elección 5A y aprobación posterior previa de déficit |
| P08 | Aplazar objetivos numéricos de rendimiento hasta una primera implementación medible; conservar límites de seguridad configurados, sin publicar resultados truncados o incompletos. Elección 6B: sustituye las metas iniciales ≤2 s y la propuesta ≤250 ms; 1.000 operaciones/cuatro recursos/5.000 aristas siguen como escala inicial de fixtures, no rendimiento demostrado ni techo de producción |
| P09 | Incorporar en implementación los contratos de publicación, despacho, estimaciones y equidad mediante cambios nuevos, preservando V1–V11. Primer MVP bloquea cambio de ventana tras reservar, continuación desde checkpoint sin contrato seguro y completitud MOCKABLE sin guarda real; diagnóstico explícito. Elección 7A |
| P10 | La revisión previa exigida por 8B se completó. Después de recibir v0.2 y la consulta explícita, el usuario respondió «si, adelante»: diseño revisado e inicio de implementación I1–I3 autorizados. Cierre, promoción y despliegue conservan aprobación separada |

## Respuestas explícitas

| Respuesta literal | Alcance |
|---|---|
| «si, están bien las reglas» | Horizonte y semántica de fechas de la primera consulta |
| «apruebo la excepción» | Excepción P4 y encuadre consultado de equidad/espera, concretados después con 1A |
| «si, buen punto de partida» | Estimaciones, recursos, estabilidad y escala inicial consultados; rendimiento actualizado después por 6B |
| «20% de planned a caminos con holgura de deadline <= 24 horas está bien» | Vía urgente de P02 |
| «que un incidente sin saldo incident produzca déficit visible sin tomar capacidad de planned está bien» | Regla de déficit de P07 |
| «1A, 2A, 3A, 4A, 5A, 6B, 7A, 8B» | Selección expresa de las ocho opciones presentadas: equidad, confianza, concurrencia, replanificación, incidentes, rendimiento aplazado, alcance de contratos y revisión antes de implementación |
| «si, adelante» | Aprobación de D3 v0.2 revisado e inicio por etapas I1–I3, tras entregar el diseño y 44 comprobaciones sintéticas; cierre D3 y despliegue pendientes |

No hay preguntas de política pendientes de aquella lista. El diseño revisado y el inicio de implementación por etapas están aprobados. Esa aprobación no demuestra validación de integración ni cierra D3. El [estado de implementación](D3-IMPLEMENTATION.md) distingue I1–I3 entregados como bibliotecas/prototipos.

## Contratos a completar durante la implementación autorizada

Se acepta su inclusión en el alcance por 7A. I2 ya incorpora APIs de captura/publicación y V12 aislada; I3 incorpora despacho protegido y el complemento posterior añade coordinación invocable; su alojamiento sigue pendiente. No se atribuyen estas garantías nuevas al prototipo D2.

| ID | Contrato y límite del primer MVP |
|---|---|
| C01 | Lectura consistente y read_set completo, publicación única por CAS y permisos; orden de mutex 742001→742002 y validación final transaccional. Pruebas futuras de dos conexiones y cambios de conjuntos |
| C02 | Estimaciones alternativas por recurso, calendarios, exclusión de directorio/entorno y preparación atómica de mapping+CLAIM; no escribir alternativas mezcladas |
| C03 | Guarda de ventana activa también en TOP_UP. Bloquear rollover/reasignación de mappings congelados; no crear nuevas operaciones para reiniciar intentos |
| C04 | Sin reanudación automática desde CANCELLED_AT_CHECKPOINT; conservar recibos/consumo/compromiso. No automatizar liberación/préstamo sin liquidación segura y evidencia confiable; coordinación real con workers pertenece a D4 |
| C05 | Diagnóstico de resoluciones incompatibles; no ampliar herencia silenciosamente. Bloquear completitud de integración MOCKABLE sin guarda real, incluidas aristas entre tareas |
| C06 | Espera elegible por intervalos, servicio y uso de vías por cuenta/ventana; proyección reconstruible, sin reinicio al publicar. Recalibración sin historia compatible abre época de equidad explícita |
| C07 | Cobertura de eventos incluida reapertura de incidente, despacho ligado al plan vigente, presupuesto vectorial y continuidad segura de retries |

No se modifica ni reabre D2. Los cambios futuros serán aditivos, revisables y probados; no se promueven V5–V11 automáticamente.

## Puerta de aprobación

1. Entregar v0.2 y evidencia sintética acotada con límites explícitos: realizado en esta revisión.
2. El usuario revisó y autorizó el inicio: **cumplido con «si, adelante», tras revisión 8B**.
3. I1 núcleo Java, I2 persistencia/publicación e I3 despacho protegido entregados y validados como prototipos. La evidencia I2 incluye concurrencia real de PostgreSQL, no workers reales.
4. Cierre de D3: **aprobado expresamente con «si, cierra D3»**, tras aceptar 1A/2A y recibir la optimización validada. Se cierra el MVP conservador definido en [D3 aprobado](D3-approved.md).
5. Despliegue/promoción: fuera de esta autorización.

## Decisión técnica de integración I2 — 2026-10-19

V12 se mantiene en `migrations-d3-proposed/`, separada de las ubicaciones históricas D2. Su prueba V10→V11 exige exactamente una migración; descubrir V12 automáticamente alteraría ese contrato de auditoría. El nuevo harness D3 configura las tres carpetas explícitamente y valida también V11→V12. Es una decisión de organización dentro del alcance aditivo autorizado, sin modificar D1/D2 o V1–V11 y sin aprobar despliegue ni cierre.

## Incremento técnico I3 — 2026-10-19

V13 aislada y DispatchStore materializan el despacho autorizado, sin modificar V1–V12. [Contrato, evidencia y límites](D3-I3-DISPATCH.md). El inicio de un intento no cambia el snapshot publicado: un hecho inmutable enlaza plan/intento/reserva. I1–I3 son bibliotecas y SQL probados con datos sintéticos; el servicio de eventos/solicitudes, workers y despliegue siguen pendientes. No se deriva cierre de D3.

## Continuación de coordinación — 2026-10-19

Tras entregar I3, «sigue» autoriza completar el coordinador de solicitudes/eventos pendiente. Se mantiene la política aprobada: agrupación 30 s, seguridad inmediata, barrido 60 s y como máximo dos recálculos adicionales. [Implementación invocable y límites](D3-COORDINATOR.md), sin iniciar servicios ni ampliar a workers reales. La ingesta usa recibos propios de consumidor; no altera la entrega global D2. V14 es una propuesta aislada y el cierre de D3 continúa pendiente.

## Revisión integrada — decisiones nuevas pendientes

[Revisión y propuestas concretas](D3-REVIEW.md). La revisión detectó y corrigió C07 con V15, conservando V1–V14. Se registran las primeras mediciones P08. Queda pendiente que el usuario decida el alcance de previsiones (MVP conservador frente a completar CONDITIONAL/calendario crítico) y si optimizar ahora o aceptar expresamente el límite medido. No son respuestas inventadas ni una reapertura de P01–P10; tampoco se da por cerrado D3.

## Respuestas a la revisión integrada y optimización — 2026-10-19

Estas opciones 1A/2A corresponden a la revisión integrada posterior y no sustituyen las ocho elecciones iniciales:

- **1A aceptada:** «Aceptar el MVP conservador y dejar las previsiones como ampliación separada». El MVP solo asigna trabajo actualmente elegible; consumidores HARD conservan bloqueo, explicación y cotas, sin slots CONDITIONAL ni calendario crítico completo.
- **2A autorizada:** «Optimizar ahora el caso independiente y repetir las mismas mediciones, preservando guardas». Implementada mediante caché temporal acotada por asignación y unión exacta de ocupaciones, con comparación contra la fuente anterior y mediciones repetidas. No se fija SLA.

[Resultado, pruebas y limitaciones](D3-OPTIMIZATION.md). El cambio intencional del núcleo queda trazado; SQL y ejecutables de los adaptadores se conservan. Cierre de D3, promoción y despliegue siguen sin aprobación.

## Aprobación expresa de cierre — 2026-10-19

El usuario respondió **«si, cierra D3»** a la pregunta de cierre del MVP conservador aceptado en 1A, después de recibir el resultado 2A y su evidencia. **D3 queda aprobado y cerrado**, con el alcance de [D3 aprobado 1.0](D3-approved.md) y el [manifiesto de cierre](../validation/D3-CLOSURE.json). Las frases de estado abierto de las entradas anteriores describen su momento histórico.

Se verificaron los inputs de la última ejecución satisfactoria; este cierre documental no exige ni simula nuevas pruebas. No se aprueba despliegue, promoción, publicación Git ni inicio de D4. Las restricciones y mediciones sin SLA quedan conservadas.
