# D3 — planificador de capacidad, v0.2

> Estado posterior: **D3 aprobado y cerrado el 2026-10-19** por «si, cierra D3», con el [MVP conservador 1.0](D3-approved.md). Las referencias a D3 abierto en este documento describen la entrega anterior a esa aprobación. No hay promoción ni despliegue aprobado.
Estado: **DISEÑO v0.2 APROBADO; IMPLEMENTACIÓN POR ETAPAS AUTORIZADA E INICIADA; D3 ABIERTO, SIN APROBACIÓN DE CIERRE**. Fecha: 2026-10-18, Europe/Madrid.
Baseline: D1 1.0 y D2 final 1.0 aprobados. Referencia publicada D2: `69d71c3877e79bdfef088956b090d4eb6b447be9` (también HEAD al iniciar esta revisión). El usuario eligió «1A, 2A, 3A, 4A, 5A, 6B, 7A, 8B»: reglas de equidad, confianza, concurrencia, replanificación, incidentes y alcance confirmadas; objetivos numéricos de rendimiento aplazados. Se presentó v0.2 y su validación antes de escribir implementación, conforme a 8B; el usuario respondió después «si, adelante», autorizando I1–I3 sin aprobar cierre ni despliegue. El estado real consta en [implementación D3](D3-IMPLEMENTATION.md). Véase [registro D3](D3-DECISIONS.md).

Este documento conserva el diseño de referencia y la validación acotada previa a implementación. Existen ahora el núcleo Java puro y la persistencia/publicación JDBC/SQL de I2; todavía no hay aplicación Spring Boot, scheduler de producción, workers ni despliegue. Los contratos SQL futuros siguen siendo aditivos y requieren pruebas antes de habilitar sus rutas. Se preservan V1–V11 y D1/D2. El [handoff](../../HANDOFF-D3.md) fija autoridad y límites.

## 1. Inventario previo: qué ofrece D2

Las rutas SQL parten de la raíz. Son contratos de persistencia del prototipo aprobado, no APIs HTTP disponibles. El scheduler definitivo seguirá en Java 21+/Spring Boot con PostgreSQL y polling HTTPS para workers.

| Entrada/acción | Entidad, vista o entrypoint existente | Qué puede utilizar D3; qué falta |
|---|---|---|
| Prioridad, pausa y aplazamiento | V1 `projects`, `project_priority_history`, `tasks.deadline_at/urgency/deferred_count`, `task_deferrals` | Prioridad y pesos 8/4/2/1/0, override explícito. Faltan semántica de deadline, reloj de espera elegible y equidad entre ejecuciones |
| Trabajo y versiones | V1/V2 `tasks`, `operations`, `execution_attempts`, `operation_leases` | Estados, row_version, intentos y fencing; no hay DAG entre operaciones de una misma tarea ni estimador de duración |
| Dependencias y evidencia | V9 `d2.resolutions`, `capability_producers`, `capability_epochs`, `verifications`, `task_eligible`, `integration_eligible`, `active_blocking_edges`, `effective_priorities` | Reutilizar elegibilidad y herencia por camino; no convertir proyectos enteros en barreras. Faltan explicación del camino y proyección temporal de desbloqueo |
| Versiones compatibles | V11 `d2.compatible`, `compatibility_result`, `semver_preflight` | Único contrato SemVer/npm; diagnósticos y límites ya validados. No implementar otro parser en Java/Python |
| Oferta física | V8 `d2.accounts`, `capacity_limits`, `balances` | Identidad recurso/dimensión/tipo/ventana real; límite efectivo, compromiso, consumo y disponible por pool. NULL bloquea. No son presupuestos del calendario |
| Demanda estimada | V8 `d2.operation_accounts.units/calibration_ref` | Vector por cuenta vinculante; calibración referenciada. No hay catálogo de estimaciones alternativas por recurso, distribución de error ni confianza por estimación |
| Reservas y deuda | V8 `reservations`, `reservation_balances`, `plan_reservations`, `loans`, `journal` | Una reserva estable por operación; enlaces por plan no reservan otra vez; deuda no desaparece al replanificar |
| Observación | V2/V3 `capacity_observations`, `capacity_measurements` | Fuente, fecha, ventanas, confianza, tokens opcionales. No inferir cuota comercial ni conversión de unidades de un porcentaje aislado |
| Oferta técnica | V2 `resources`, `workers`, capabilities JSONB, heartbeat | Habilitación y compatibilidad técnica del CLAIM. Faltan calendario de disponibilidad, duración, concurrencia por host y comprobación real de CLI |
| Política y autorización | V2/V5/V9 `operations.policy_snapshot`, `approvals`, `execution_snapshots` | Contexto/política exactos, caducidad, hash PostgreSQL `jsonb::text`; no sustituir por hash de serialización Java |
| Ejecución | V9 `d2.execution(cid, req)` | CLAIM comprueba READY, intentos, guardas, recurso/worker y reserva o TOP_UP atómicamente. START/HEARTBEAT/CALLBACK/VERIFY y recuperación mantienen fencing |
| Cambiar estados | V9 `d2.transition(cid, req)` | CAS de estado/versión, historia/outbox atómicos. No es un permiso para forzar READY sin cumplir guardas |
| Contabilidad y preempción | V8/V9 `d2.capacity_command`, `d2.preempt`; `recalibrate` separado | BORROW/RETURN y RELEASE restringidos; checkpoint seguro antes de cancelar. Recalibrar/corregir exige administrador, no scheduler |
| Snapshot del plan | V2/V7/V10 `planning_runs`, budgets, allocations, schedule, deferrals, `d2.budget_accounts` | DRAFT y congelación al publicar; sucesor PUBLISHED explícito. Falta entrypoint de publicación, selección única del plan vigente y comprobación de obsolescencia completa |
| Eventos | V9/V10 `outbox_events`, `d2.ack_outbox`, recibos | Entrega al menos una vez; no es un bus ni un scheduler. Faltan coalescencia y cobertura de todos los eventos de replanificación |

Las 157 pruebas y los 29.829 vectores SemVer de D2 son **evidencia histórica registrada**, no ejecuciones nuevas de esta revisión. Véanse [matriz](../validation/D2-VALIDATION-MATRIX.md) y [resultados](../validation/latest-results.json).

### 1.1 Límites concretos encontrados al leer el SQL

Estos límites se documentan como necesidades de integración futuras, sin modificar D2:

- `operation_accounts` queda congelado desde que existe una reserva, incluso si el compromiso llega a cero. La reserva también fija recurso y pool. No es posible mover silenciosamente un retry a otra cuenta, ventana, recurso o pool. Sin reserva se puede proponer una alternativa; fijar el mapping exige una API futura revisada.
- RESERVE exige ventana activa. TOP_UP no repite explícitamente esa comprobación temporal en V8. D3 deberá rechazar mappings de ventana vencida también para retries; durante la futura implementación se prepararán un cambio aditivo y su prueba contractual, antes de habilitar esa ruta. No atribuir esa protección a CLAIM actual.
- El borrador puede prever siete días; solo las cuentas reales conocidas permiten admisión. Un reset futuro estimado no crea cuenta ni capacidad. Una operación que atraviese un reset requiere contrato de atribución/segmentación D4; por defecto no se admite ese cruce.
- `active_blocking_edges`/`effective_priorities` son vistas sin explicación de procedencia; una resolución incompatible con capability AVAILABLE puede bloquear `task_eligible` sin crear arista activa de herencia. D3 no inventará una elevación para ese caso: `UNRESOLVED_BLOCKER`, reparar resolución de forma explícita. La herencia cubre los caminos representados, no todos los bloqueos imaginables.
- `integration_eligible` comprueba requirements de capability MOCKABLE. Las aristas MOCKABLE entre tareas no tienen una guarda equivalente de integración real. Proponer metadato explícito de integración y endurecimiento futuro antes de admitir esas terminaciones; no afirmar cobertura actual de D2 para ellas.
- `preempt` termina en CANCELLED. No existe comando de reanudación desde ese checkpoint. D3 solicita checkpoint, conserva evidencia y expone `RESUME_CONTRACT_REQUIRED`; no crea una operación nueva que reinicie intentos o repita efectos automáticamente.
- El trigger de incidentes emite REPLAN_REQUIRED al insertar o cambiar severidad; reabrir sin cambiar severidad no lo emite. D3 debe observar también STATE_CHANGED y recalcular demanda crítica. BORROW bloquea ante cualquier SEV1/SEV2 abierto globalmente, aunque esté en otro recurso; conservar esta regla conservadora.
- No hay API/grants suficientes para leer un snapshot completo ni escribir mappings/publicar con un rol final de aplicación. No ejecutar con propietario para sortearlo. Un futuro contrato de control plane debe separar lectura, publicación y preparación de admisión.
- `capacity_budgets` tiene unicidad por plan/recurso/inicio y una unidad escalar: dos cuentas simultáneas con distintas dimensiones no se representan como suma. `d2.budget_accounts` conserva cada vector; el escalar legado puede quedar NULL si no representa una magnitud única. `allocations.consumed_units` no es saldo operativo.

## 2. Decisiones de planificación resueltas

Las decisiones P01–P10 del [registro](D3-DECISIONS.md) recogen las respuestas expresas. No quedan decisiones de aquella lista pendientes. Esta revisión concreta los mecanismos técnicos y las pruebas que faltan; no convierte una aprobación de política en evidencia de integración. La autorización de implementación ya se recibió después de revisar v0.2. P08 aplaza metas numéricas de rendimiento hasta medir una primera implementación.
Orden de objetivos propuesto: seguridad y evidencia → conservar compromisos reales → incidentes críticos elegibles → vía de equidad acotada → vía urgente por riesgo de fecha/camino bloqueante → reparto ponderado → estabilidad y utilización. Ningún objetivo blando convierte una restricción dura en puntuación negociable.

## 3. Contratos de entrada y salida propuestos

### 3.1 PlanningRequest v0.2

| Campo | Regla |
|---|---|
| `request_id`, `schema_version`, `algorithm_version` | Identidad idempotente de solicitud y versiones del contrato/algoritmo; no reutilizar ID con otro contenido |
| `trigger_ids[]`, `trigger_type` | IDs deduplicados y causa; MANUAL, INCIDENT, CAPACITY, DEPENDENCY, PRIORITY, APPROVAL, WORKER, TIMER |
| `as_of`, `timezone`, `horizon_start/end` | Instante suministrado por reloj confiable; UTC al persistir. Regla aprobada: siete días civiles desde `as_of` en Europe/Madrid, intervalo [inicio, fin), sujeto a cambios DST; nunca equivale al reset del proveedor |
| `expected_current_plan_id` | CAS del plan global vigente, NULL solo si no hay plan; alcance global MVP |
| `policy_ref/hash`, `calibration_refs[]` | Versiones inmutables. Parámetros desconocidos no reciben defaults comerciales |
| `mode`, `limits` | REVIEW_ONLY por defecto en D3; límite de tamaño y tiempo. No autoriza ejecutar ni publicar |

### 3.2 PlanningSnapshot v0.2

Lectura consistente MVCC REPEATABLE READ corta; copiar datos y cerrar transacción antes del cálculo. Congelar `as_of` para todo el cálculo. Datos ordenados por IDs estables; decimales exactos, unidades explícitas, sin aleatoriedad ni reloj interior.

Incluye proyectos/tareas/operaciones con estados/versiones; dependencias, resoluciones y evidencia exacta; recursos/workers y asignaciones; contexto/política/aprobaciones; cuentas y ventanas con vector por pool `(limit, outstanding, consumed, available)`; mappings/reservas/leases/deudas; intentos totales y evidencia de reconciliación; plan previo y deferrals. Confianza de límite: última `capacity_limits.confidence` si existe; de lo contrario `accounts.confidence`, nunca mezclar procedencias.

Además necesita datos propuestos, hoy no disponibles como contrato completo:

- `EstimateCandidate(operation, resource, account_vector, duration_upper, confidence, calibration_ref, provenance, valid_until)`: alternativas separadas, no escrituras simultáneas en `operation_accounts`. Cota conservadora suministrada por estimador, sin afirmar un percentil sin datos. Ausencia de magnitud, calibración, confianza o duración impide slots admitibles.
- Calendario de recurso y host, máximo de concurrencia, bloqueos exclusivos de repositorio/entorno y duración restante de activos. Regla aprobada: una operación por worker; estimación restante desconocida ocupa todo el horizonte y produce diagnóstico.
- `eligible_wait_seconds`, `service_history` por proyecto/recurso/ventana física, y checkpoints de actualización. Persistencia futura necesaria: publicar/recalcular no reinicia espera ni servicio; no confundir creación de tarea con tiempo elegible.
- `read_set`: IDs/versiones y hashes de filas sin row_version, IDs de evidencia/generación, mapas de cuentas, último límite, contenido/saldos del diario, conjunto de incidentes y plan vigente. Un máximo de ID de journal/outbox **no basta** como versión de commit; secuencias admiten huecos y commits fuera de orden.

Los conjuntos también requieren detección de inserciones/borrados (phantoms); no basta comparar versiones de filas presentes. Cambios de elegibilidad se explican con guardas D2 y diagnósticos de lectura controlados, no con acceso libre del worker.

### 3.3 PlanningResult v0.2

`result_status = COMPLETE | PARTIAL | STALE | INVALID_INPUT | LIMIT_EXCEEDED`, con `publishable`, hashes de entrada/política, versiones, métricas y advertencias. PARTIAL significa cobertura incompleta del trabajo por restricciones conocidas; entrada truncada o cálculo interrumpido por límite → no publicable.

Cada operación obtiene exactamente una disposición dentro de este resultado:

| Disposición D3 | Contenido obligatorio |
|---|---|
| `CARRIED` | Reserva/lease existentes, recurso/pool/cuentas originales, compromiso pendiente ya incluido en saldos; no reserva nueva |
| `TENTATIVE` | Recurso/pool, slot, vector estimado y delta pendiente por cuenta; razones, confianza, prioridades base/efectiva y camino de herencia |
| `CONDITIONAL` | Dependencia prevista pero todavía no satisfecha, condición y slot orientativo; consume presupuesto virtual conservador si se muestra, jamás habilita CLAIM |
| `BLOCKED` | Restricción dura conocida: dependencia, aprobación, política, pausa, reconciliación, intentos agotados, etc. |
| `NEEDS_DATA` | Cuota/estimación/duración/calibración/ventana o resolución desconocida; no tratar como cero ni ilimitado |
| `DEFERRED` | Elegible pero no cabe; motivo, primera alternativa conocida y riesgo de deadline. Sin fecha inventada cuando no se conoce reset |
| `CONFLICT` | Deadlines incompatibles, aplazamiento prohibido o capacidad real en déficit que necesita decisión/observación |

Estas disposiciones son un DTO de diseño, no estados nuevos de D2. En persistencia futura, las explicaciones completas van en `config_snapshot` (manifiesto del resultado/read_set), `schedule_entries.reason/priority_snapshot` y artefacto referenciado con hash. Solo entradas reales se representan en schedule PLANNED/DEFERRED/CANCELLED; una no asignada sin recurso no recibe un recurso ficticio. `task_deferrals` solo registra traslado a semana posterior real; una espera intradía o desconocida queda en el manifiesto. No cambiar automáticamente el estado de la tarea al publicar.

Explicación mínima: `reason_codes[]`, guardas aprobadas/rechazadas, valores comparados, IDs de cuentas y evidencia, alternativas descartadas, restricción vinculante, saldo antes/después virtual, fórmula de selección, espera, deadline/slack, ruta de herencia, cambio frente al plan anterior y confianza. Códigos típicos: `UNKNOWN_CAPACITY`, `INSUFFICIENT_POOL`, `EXPIRED_MAPPING`, `DEPENDENCY_NOT_READY`, `STALE_APPROVAL`, `EFFECT_UNKNOWN`, `LOW_CONFIDENCE`, `FAIRNESS_BUDGET_EXHAUSTED`, `DEADLINE_AT_RISK`.

## 4. Elegibilidad y contabilidad virtual

1. Excluir terminales y proyectos ARCHIVED/PAUSED. P4 queda excluido de PLANNED por defecto, salvo excepción por camino aprobada P03; nunca eleva tareas ajenas. Un incidente explícito se evalúa por su política autorizada, no por un override implícito de pausa.
2. Separar activos/reconciliación de nuevas admisiones. RECONCILING o efecto UNKNOWN conservan compromiso y recursos afectados; no reintentar. WAITING_CAPACITY/BLOCKED_APPROVAL/RETRY_PENDING requieren transición D2 válida a READY antes de CLAIM; el plan solo propone dicha transición cuando procede.
3. Consultar `task_eligible`; HARD bloquea. SOFT propone preferencia por dependencia satisfecha solo en empates; OPTIONAL no bloquea ni hereda. MOCKABLE permite desarrollo marcado con mocks, con integración real obligatoria para completar; los huecos de §1.1 siguen explícitos.
4. Recurso habilitado, worker ONLINE con heartbeat fresco (máximo aprobado 90 s), capacidades y permisos correctos, disponibilidad/host/repositorio sin solapamiento. No habilitar fallback comercial de pago. No hay cuotas verificadas de las suscripciones todavía.
5. Contexto y política versionados, aprobación exacta vigente, intentos restantes y retry seguro. Una previsión posterior a caducidad de aprobación es CONDITIONAL, no ejecutable.
6. Vector estimado conocido para **todas** las cuentas vinculantes; confianza y duración según P04. Una dimensión distinta no compensa otra. Mapping existente tiene precedencia sobre alternativas; mapping vencido produce bloqueo contractual.
7. Encajar operación completa dentro de disponibilidad y cuentas conocidas, sin dividirla artificialmente en slots para ocultar coste/checkpoints. El backlog que no cabe permanece explicado.

Por cuenta `a` y pool `p`, usar directamente `A[a,p] = effective_limit − outstanding − consumed` de D2. Se conserva cualquier negativo o NULL. Construir copia virtual `V=A`; si negativo, bloquear nuevas admisiones en esa cuenta/pool y declarar déficit. No recortar la realidad a cero en el resultado.

Para operación nueva, `delta[a] = estimate[a]`; para retry seguro con reserva estable, `delta[a] = max(mapping.units[a] − reservation_outstanding[a], 0)`; para activo CARRIED, `delta=0`. No restar otra vez consumo/compromiso ya presentes en `A`. Requerir `V[a,p] >= delta[a]` en todas las cuentas, incluso si delta=0 con saldo desconocido/deficitario. Aceptar tentativamente resta delta de V una sola vez. Las reservas en planes antiguos siguen descontadas aunque no aparezcan en el sucesor.

70/20/10 se aplica a cada cuenta del recurso; no se suman SECONDS, TOKENS u OPERATIONS. Ejemplo: cuenta de 100 → 70/20/10; una sesión con 7 PLANNED y semana con 40 PLANNED limita una operación de coste 8 en ambas: no cabe aunque su suma sea 47. Las ventanas históricas consumidas no se reutilizan ni se prorratean para crear saldo.

Un plan publicado contiene intención, no compromiso físico. No llama a RESERVE para cada TENTATIVE; la reserva se crea en CLAIM. El futuro despachador verifica plan vigente y resta solo saldos físicos actuales, **sin restar nuevamente el vector del plan**. Para activos, un plan DRAFT puede enlazar reserva existente; una reserva nacida después de publicar no se añade al snapshot congelado: se encuentra por operación en el estado operativo y en el siguiente plan.

## 5. Algoritmo MVP propuesto, determinista y explicable

Heurística greedy con reparto ponderado y coste normalizado por recurso; no se requiere solver externo. No garantiza óptimo global, fecha ni utilización máxima. Una selección local de recurso puede dejar capacidad fragmentada; el resultado conserva ese límite.

### 5.1 Prioridad, fechas y caminos

Reutilizar `effective_priorities`: `w_eff = max(w_base, pesos que llegan por aristas activamente bloqueantes)`. La prioridad base nunca cambia. Registrar IDs de tareas/capabilities y consumidor origen; varios consumidores no suman pesos. Propagar hacia atrás únicamente sobre el DAG activo, no sobre SOFT/OPTIONAL ni todo el proyecto productor.

Calcular earliest finish y latest start por camino representado, con duraciones conservadoras y calendarios. `slack = deadline − earliest_finish` incluye predecesores pendientes; sin duración, riesgo UNKNOWN. Deadline de consumidor informa el desbloqueador concreto; no inventa capacidad. MOCKABLE solo influye en el camino de integración real explícito. Regla aprobada P02: fecha objetivo blanda; slack negativo implica `DEADLINE_AT_RISK` y conflicto visible si no hay solución, incluso si se asigna parte del camino. `deferral_allowed=false` impide traslado automático; no impide informar que el trabajo no cabe.

### 5.2 Equidad y reparto

Todo cálculo es independiente por recurso; INCIDENT se atiende por severidad SEV1 antes de SEV2, después antigüedad de incidente e IDs estables. SEV3/4 y FOLLOW_UP no adquieren vía libre al pool INCIDENT: P07 exige clasificación explícita de respuesta activa para SEV3/4; FOLLOW_UP usa PLANNED. Sin clasificación no se admite gasto INCIDENT para SEV3/4. No consumir UNCERTAINTY. Regla aprobada P07: un incidente sin saldo INCIDENT produce déficit visible `INCIDENT_SHORTFALL`, sin tomar capacidad de PLANNED. No transferir PLANNED→INCIDENT, ruta que D2 no ofrece. Clasificación y orden aprobados por 5A.

Dentro de PLANNED, definir coste dominante adimensional para comparar **solo en el mismo recurso**:

`d(o,r) = max_a(delta[a] / base_planned_limit[a])`

Las bases son límites 70% conocidos y positivos de las cuentas vinculantes del recurso, antes de préstamos; no disponibles restantes. Si hay varias ventanas, cada restricción participa. El máximo compara fracciones, no suma unidades. El débito por cuenta sigue usando el vector exacto; `d` solo ordena. TOP_UP cero de un retry lleva coste histórico pendiente correspondiente y desempate estable; no genera prioridad infinita.

`S(project,r)` acumula servicio dominante del período físico conocido (consumo y compromiso atribuibles, más selecciones virtuales nuevas); recalcular/publicar no lo reinicia. Para impedir duplicados, servicio ya cargado por reserva no se vuelve a cargar al enlazarla. Si no hay historia/calibración compatible para calcular S, declarar inicio de época explícito, con incertidumbre; no prometer equidad histórica. La persistencia de esta proyección es una necesidad de contrato futuro.

Para cada proyecto y recurso, elegir su siguiente operación candidata con su **propio** peso efectivo. Puntuación normal:

`fair_finish(o,r) = (S(project,r) + d(o,r)) / w_eff(o)`

Seleccionar el menor fair_finish entre candidatos que caben; actualizar S al elegir. Esto aproxima reparto 8:4:2:1 con operaciones del mismo tamaño. No multiplicar el peso por cantidad de tareas, dividir un proyecto en buckets ni usar el máximo heredado de una tarea para todas las demás. El servicio del desbloqueador se carga al proyecto productor; el motivo heredado queda trazado. Overrides cero no se convierten en positivos salvo herencia autorizada.

Regla aprobada P03 para prevenir inanición: antes de la ronda normal, hasta 5% del **límite PLANNED base de cada cuenta** (dentro del 70%, sin reserva física adicional) para las operaciones con ≥7 días de espera elegible. Consumo/compromiso anterior de esta vía cuenta contra el cupo de su ventana. Orden: espera descendente, peso efectivo descendente, IDs. No se fuerza una operación que exceda ese cupo o no quepa físicamente; se emite `STARVATION_RISK`. Una tarea bloqueada no acumula espera elegible. Cálculos frecuentes no multiplican el 5%. P4 sin excepción aprobada no envejece hacia admisión.

Regla aprobada P02: para caminos con holgura de deadline (slack) ≤24 h, vía urgente de hasta 20% del límite PLANNED por cuenta, contabilizada entre planes igual que equidad, sin duplicar gasto entre vías. Propuesta técnica de orden: slack ascendente, peso efectivo descendente, espera, IDs. La vía de equidad va antes para que fechas permanentemente urgentes no la absorban; el 75% restante o más usa reparto normal. Los cupos sin demanda vuelven al reparto normal. Una operación mayor que el cupo urgente puede entrar por la vía normal; se informa el riesgo. Los límites 20%/24 h están aprobados; el orden y el funcionamiento detallado de las vías siguen propuestos. Son repartos internos de PLANNED, sin cambios al 70/20/10 ni garantías de fecha.

Desempate normal: fair_finish ascendente → slack conocido ascendente (sin deadline al final) → mayor espera elegible → dependencia SOFT satisfecha → urgency descendente → created_at → UUID de proyecto/tarea/operación/recurso/cuenta en orden byte estable. Ningún orden depende del orden de consulta. No usar un epsilon de floats; racionales/decimales con regla de redondeo conservadora hacia arriba a 4 decimales al admitir unidades.

### 5.3 Elección de recurso, slots y pseudocódigo

Por operación elegida, entre alternativas que caben: fin previsto más temprano, después menor coste dominante y UUID; P05 conserva recurso previo si el fin empeora ≤10% de la duración estimada de esa operación. Se comprueban todos los slots de host/worker/repositorio y cuentas; no se compara suma de cuotas entre recursos. Una reserva existente fija recurso y pool siempre.

```text
plan(request):
  snapshot = read_consistent_snapshot(request)
  validate_shape_units_graph_and_versions(snapshot)  # sin reparaciones silenciosas
  if size_exceeded: return LIMIT_EXCEEDED, publishable=false
  V = copy_physical_balances(snapshot)                # incluye todos los planes
  carry_active_leases_reservations_and_unresolved_effects()
  graph = active_D2_graph_with_reason_paths()
  priorities = D2_effective_priorities(graph)
  candidates, blocked, needs_data = hard_filters(snapshot, priorities)
  derive_earliest_finish_slack_and_explicit_conditional_forecast(graph)
  initialise_service_and_lane_usage_from_persistent_history()
  for lane in [critical_incident, other_authorised_incident,
               aged_planned, urgent_planned, weighted_planned]:
    while some_candidate_fits(lane):
      choices = feasible_resource_slot_account_vectors(lane, V)
      choice = stable_min_by_lane_rules(choices)
      record_explanation_and_tentative_vector(choice)
      subtract_only_incremental_deltas(V, choice)
      charge_service_and_lane_once(choice)
      occupy_worker_host_repo_slot(choice)
    # no espera infinita ante operación grande; explicar y explorar las restantes
  classify_every_remaining_operation_and_deadline_conflict()
  verify_all_virtual_invariants_and_emit_result()     # sin CLAIM/BORROW/publicación
```

HARD todavía no satisfecho no entra en la cola ejecutable, aunque se pronostique que su productor terminará. Una proyección CONDITIONAL puede ocupar capacidad virtual para evitar sobrepromesa, pero no se usa para afirmar que el consumidor se desbloqueó. Se recalcula tras evidencia AVAILABLE/DONE real. Serializar operaciones de una tarea por defecto en ausencia de DAG explícito; no inferir que se pueden ejecutar en paralelo.

Con N operaciones, R alternativas, E aristas y K cuentas por alternativa: DAG O(N+E); proyección explicativa de todos los orígenes puede crecer O(N·(N+E)), acotada por límites de entrada; greedy simple con reescaneo y búsqueda lineal de slots O(N³·R·K) en peor caso. Un índice de intervalos/heap puede mejorarlo después de medir; v0.2 no promete O(N log N); las metas numéricas de rendimiento se aplazan por 6B hasta disponer de mediciones. Si el cálculo excede su límite, no publicar un prefijo que oculte dependencias o reservas.

## 6. Replanificación, consistencia y publicación futura

Regla aprobada P06: incidentes SEV1/2, invalidación, déficit, pérdida de worker, cambios de aprobación o guardas generan solicitud inmediata sin debounce. Inmediato significa encolar y recalcular desde snapshot nuevo; no garantiza empezar un incidente si no existe capacidad/checkpoint. Otros eventos se agrupan 30 s desde el primero, sin postergación infinita por flujo continuo; reintentos/cálculo obsoleto quedan auditados. TIMER cada 60 s recupera cambios que no tengan evento explícito en D2. Acknowledgment posterior a registrar el trabajo idempotente, no antes.

Congelar solo intención aún válida de los próximos 15 min; no reservar por anticipado al congelar. Incidente crítico, invalidación, déficit, pérdida de disponibilidad, aprobación inválida o cambio explícito de prioridad rompen esta preferencia. Fuera de esa franja, mantener candidatos previos dentro de tolerancia P05; toda expulsión recibe motivo. Los leases activos siguen según D2, no según franja.

Publicación futura propuesta (todavía sin API):

1. Calcular sin locks, construir DRAFT completo con manifiesto y read_set.
2. Abrir transacción nueva; adquirir mutex de publicación `742001` **antes** de mutex global D2 `742002`, ambos antes de locks de filas. Unificar ese orden en todo futuro entrypoint que combine ambos; no llamar a publicación desde un comando que ya tomó el global en orden inverso.
3. CAS del plan vigente esperado; releer read_set y conjuntos, saldos, reloj, incidentes, mappings, evidencia, aprobaciones, workers/calendarios y presupuesto virtual. Rechazar cualquier cambio relevante como STALE; no retocar silenciosamente el resultado calculado.
4. Para filas mutables sin protocolo global, se necesita bloqueo/versionado coordinado o transacción SERIALIZABLE con reintento completo y validación de predicados. El mutex por sí solo no cubre escrituras que no lo toman. Diseñar ese entrypoint y permisos es trabajo posterior explícito.
5. Persistir hijos/enlaces completos, validar ausencia de doble cargo virtual, publicar sucesor y marcar anterior SUPERSEDED con sucesor explícito, todo en el mismo commit. CAS global propuesto evita dos planes vigentes; D2 por sí solo no impone esa unicidad.
6. No llamadas externas ni cálculo largo bajo locks. Si STALE, hasta dos recálculos aprobados y después diagnóstico visible; mantener plan previo como historia, ejecutar solo lo que pase guardas actuales.

CLAIM posterior debe pasar por un futuro despachador que compruebe operación perteneciente al plan vigente y elegibilidad fresca, serialice preparación del mapping y CLAIM en el mutex global, y vuelva a comprobar ventanas incluso en TOP_UP. El CLAIM D2 actual no recibe plan_id ni impone orden de schedule. No atribuirle esas garantías nuevas; proponer wrapper y permisos por separado. La seguridad contable final sigue siendo transaccional de D2; publicar no es una autorización de ejecución.

Préstamos: calcular necesidad sin mover dinero en el borrador; antes del CLAIM, futura transacción coordinada valida checkpoint verificable/política y ausencia global de demanda crítica, ejecuta BORROW solo por déficit necesario y CLAIM, o revierte todo. No mantener préstamos huérfanos si falla admisión. Incidente durante préstamo: solicitar checkpoint con `d2.preempt`; conservar compromiso hasta recibo de generación actual que confirme proceso parado y efectos resueltos. Antes de liberar debe reconocerse todo consumo ocurrido: el preempt actual libera outstanding pero no ingiere consumo, y CALLBACK cambia a VERIFYING, donde preempt ya no aplica. Esa coordinación necesita C04; hasta resolverla, no automatizar esta devolución como si ya fuera segura. Después de liquidación y liberación verificadas, retornar solo deuda y capacidad libre y recalcular. El consumo ya realizado no vuelve al pool INCIDENT: puede quedar deuda consumida e incidente sin capacidad. Trabajo no interrumpible permanece activo y se informa el aplazamiento del incidente; no matar procesos.

## 7. Invariantes y ejemplos de referencia

- I1: identidad y saldos físicos no dependen del número de planes; enlaces no duplican compromiso.
- I2: toda admisión valida el vector completo y conserva 70/20/10 por cuenta; NULL/negativo no habilitan nuevo gasto.
- I3: solo delta incremental se descuenta virtualmente; consumo real/déficit y deuda nunca se borran.
- I4: no préstamo de UNCERTAINTY; préstamo requiere checkpoint y ausencia crítica global; RETURN ≤ deuda y capacidad libre.
- I5: HARD/evidencia/aprobación/estado/fencing se comprueban de nuevo al ejecutar; proyección no satisface dependencia.
- I6: herencia solo por camino bloqueante; no cambia prioridad base ni favorece al resto del productor.
- I7: replanificar no reinicia intentos, espera elegible ni contadores de servicio/vías.
- I8: mismo snapshot + versiones + reloj produce resultado y razones idénticos ante permutación de entradas.
- I9: toda operación aparece una vez; toda no asignación tiene razón, procedencia y riesgo conocido o UNKNOWN.

Ejemplos en unidades **sintéticas**, sin equivalencia con suscripciones:

1. Cuenta 100, reserva activa 20 y consumo previo 10 en PLANNED: disponible 40. Dos planes enlazan la misma reserva; sigue 40. Nueva operación 12 → virtual 28; publicar no cambia el 40 físico; CLAIM posterior lo deja en 28, no 16.
2. Retry con estimación 20 y compromiso restante 7, consumo previo 9: delta 13. Con saldo físico 14, virtual 1. No reservar otros 20 ni borrar el 9 consumido; comprobar intentos/seguridad y ventana original.
3. Cuenta 100, préstamo 10: PLANNED 80, INCIDENT 10, UNCERTAINTY 10. Con 70 ya consumidos por otro trabajo y 6 por el prestatario, tras liberar el compromiso restante solo quedan 4 libres en PLANNED: RETURN puede devolver 4; INCIDENT llega a 14, deuda pendiente 6. Con más capacidad PLANNED libre se podría devolver más, siempre hasta la deuda; no prometer recuperar los 20 originales.
4. Tres proyectos P0/P1/P3 con operaciones unitarias en un recurso de PLANNED=65, sin urgencia ni vía de edad: selección ponderada ideal 40/20/5 (8:4:1), limitada por demanda y granularidad. Un segundo recurso repite su propio reparto, sin compensaciones entre ambos.
5. Consumidor P0 bloqueado por capability producida por una tarea P3: ese productor tiene peso 8; su tarea hermana conserva 1. Cuando AVAILABLE con evidencia compatible elimina el bloqueo, desaparece la herencia en el nuevo snapshot. Una resolución incompatible exige reparar datos, no elevar todo el proveedor.

## 8. Plan y evidencia de validación sintética acotada

[Experimento reproducible](../../testing/D3/README.md) y [resultados D3](../validation/D3-v0.2-results.json). La revisión ejecutó **44 comprobaciones satisfactorias**. El experimento usa aritmética exacta y modelos pequeños independientes: no instancia PostgreSQL ni sustituye una prueba de integración de D3. Su resultado no autoriza implementación ni cierre; valida solo las hipótesis/modelos expresamente descritos.

| ID | Escenario y criterio esperado | Evidencia en v0.2 |
|---|---|---|
| S01 | Varios proyectos y recursos; reparto independiente ponderado y límite por cuenta | Experimento aritmético de reparto 8:4:1 por recurso |
| S02 | Cuota NULL o una de dos ventanas insuficiente; rechazo conjunto sin descuento parcial | Experimento vectorial |
| S03 | Sobreconsumo y recalibración menor; saldo negativo conservado, nueva admisión bloqueada | Experimento contable |
| S04 | Replan repetido enlaza reserva estable; delta retry y CLAIM sin doble resta | Experimento contable |
| S05 | Incidente durante préstamo; checkpoint antes de liberar, deuda consumida no recuperable, UNCERTAINTY intacto | Aritmética de préstamo ejecutada; checkpoint/efectos: escenario pendiente de integración D3/D4 |
| S06 | Operación no interrumpible; mantener lease/compromiso, informar incidente aplazado | Escenario especificado; contrato D2 con evidencia histórica, sin ejecución nueva |
| S07 | Camino entre proyectos, varios niveles/productores, hermano ajeno sin herencia | Modelo DAG sintético; paridad SQL y explicación pendientes |
| S08 | Invalidar capability entre cálculo y ejecución; STALE y bloqueo/reconciliación | Escenario de carrera pendiente de integración; D2 ya tiene evidencia histórica de invalidación |
| S09 | P4 bloqueante y PAUSED, excepción P03; deferral con razón y fecha conocida o desconocida | Política P03 aprobada; prueba integrada de scheduler pendiente |
| S10 | P3 con cola P0 permanente; vía de edad acotada, operación grande muestra riesgo | Experimento de cupo por cuenta; garantía temporal y reloj persistente pendientes |
| S11 | Deadlines incompatibles/deferral_allowed=false; no violar cuota, producir conflicto | Ejemplo vectorial de imposibilidad y liquidación de vía urgente; orden/slack completo pendiente |
| S12 | Dos publicaciones con mismo predecessor, claim o recalibración durante cálculo | CAS/read_set/serialización especificados; no ejecutados, requieren wrapper futuro y dos conexiones |
| S13 | Empates y permutación del mismo snapshot; resultado estable | Modelo ponderado y DAG permutados; resultado completo/serialización pendiente |
| S14 | Reset real/DST, ventana vencida en retry; no inventar capacidad | DST calculado; caso TOP_UP documentado, endurecimiento/prueba SQL pendientes |
| S15 | Mocks permiten desarrollo, integración real incompatible impide completar | D2 histórico para capability MOCKABLE; aristas de tarea requieren contrato adicional |
| S16 | Estimación sin calibración/confianza baja; recurso técnicamente apto pero no admitido | Oráculos de confianza, calibración y caducidad ejecutados; fixture integrado pendiente |
| S17 | CLAIM tras publicar: aprobación caducada/worker caído/contexto cambiado/UNKNOWN | Heartbeat y datos de estimación en oráculos; ejecución SQL/estados sigue pendiente |
| S18 | Escala inicial de 1.000 operaciones/4 recursos/5.000 aristas, peor caso slots y límite excedido | Fixtures futuros; objetivos numéricos aplazados por 6B, sin benchmark del scheduler |

Antes de una futura aprobación de cierre: completar las etapas autorizadas y ejercer las pruebas de scheduler completo, concurrencia y contratos indicadas abajo. La revisión v0.2 y la autorización de inicio según 8B ya se recibieron. Las decisiones de política están respondidas; no se condiciona iniciar implementación a tener ya implementado el scheduler. El cierre seguirá requiriendo aprobación expresa y evidencia pertinente, sin objetivos numéricos de rendimiento hasta medir conforme a 6B.

## 9. Concreciones técnicas de la revisión v0.2

### Confianza, concurrencia y estabilidad

- `EstimateCandidate` exige vector positivo con todas las cuentas vinculantes, `duration_upper>0`, confianza entre 0 y 1 y ≥0,8, referencia de calibración, procedencia, `observed_at` y `valid_until>as_of`. Un límite físico conocido con confianza NULL o <0,8 también bloquea nueva admisión. Se permite procedencia MANUAL documentada; no se infiere que 0,8 sea un percentil de acierto.
- Una estimación caducada o que caduque antes de su inicio previsto no habilita CLAIM; marcar NEEDS_DATA o proyección CONDITIONAL. Caducidad de evidencia comercial no modifica una cuenta automáticamente: requiere observación/recalibración autorizada. Un activo ya comprometido conserva su contabilidad aunque su confianza se degrade.
- Intervalos temporales [inicio,fin); trabajos adyacentes no se solapan. Una operación por worker incluso si ofrece varios recursos. Un mismo directorio de trabajo y un entorno marcado exclusivo no pueden ocuparse a la vez; repositorios con worktrees distintos no implican exclusión global por sí solos. Dependencias y políticas pueden añadir exclusiones concretas.
- Heartbeat aceptado si `0 <= as_of-last_heartbeat <=90 s`; ausente o futuro requiere dato confiable. La renovación de lease de D2 mantiene sus propios plazos: este filtro no amplía un lease.
- Tolerancia de recurso: `previous_finish-best_finish <= 0.10*duration_upper(previous_resource)`; considerar solo alternativas elegibles y sin reserva fija. Por ejemplo duración previa 30 min tolera hasta 3 min de retraso. El desempate posterior es estable por UUID; no redondear para admitir un retraso mayor.
- Dos recálculos tras el cálculo inicial: máximo tres cálculos por solicitud. Si siguen obsoletos, devolver STALE no publicable y diagnóstico. Eventos nuevos forman nueva solicitud deduplicada, no un bucle oculto sobre la anterior.

### Proyección de servicio y vías, sin doble cargo

La futura persistencia necesita hechos de intervalo elegible y atribución de vía, identificados por operación/reserva, cuenta física, epoch de equidad y comando idempotente. Se añaden durante implementación; no se escriben sobre snapshots publicados ni se convierten en nuevos movimientos de capacidad.

`eligible_wait_seconds` suma intervalos no solapados donde pasan las guardas duras y técnicas pero falta turno/capacidad; no exige que haya capacidad libre para acumular espera. Dependencia/aprobación ausente, pausa o NEEDS_DATA detienen el reloj. Publicar no lo reinicia. Al iniciar ejecución se cierra el período de espera; un retry seguro abre otro período sin borrar la historia ni reiniciar intentos.

Conjunto de referencia: cuentas conocidas y activas del recurso en la época. Para cada reserva PLANNED, conservar vector de consumo reconocido y compromiso pendiente por cuenta. Servicio dominante de esa reserva = máximo de `(consumo+compromiso)/límite_PLANNED_base` entre sus cuentas de referencia; S es suma de esos servicios por proyecto ejecutor, sin sumar dos veces la misma reserva. Operaciones tentativas añaden únicamente compromiso virtual, descartado al recalcular desde hechos. INCIDENT no altera el servicio de reparto PLANNED.

Para un retry ya comprometido, el incremento de servicio es `S_proyectado_tras_delta-S_actual`, no cobrar de nuevo toda la reserva. Por ello, la expresión S+d de §5.2 usa el coste dominante directo para operaciones nuevas y este incremento exacto para retries. Calcular fair_finish sobre S proyectado preserva la ausencia de doble cargo incluso si cambia la cuenta dominante. delta=0 no da prioridad infinita.

Los contadores de vía conservan consumo+compromiso atribuible en unidades de cada cuenta, no porcentajes sumados entre cuentas. Reintento con TOP_UP ocupa solo el incremento; liquidar compromiso por consumo sustituye cantidades sin duplicarlas. Si el consumo supera su estimación/cupo, conservar el exceso y cerrar esa vía a nuevas admisiones en la cuenta afectada. Resto no usado del cupo se ofrece a reparto normal dentro del mismo cálculo. Reserva nacida del plan atribuye una única vía; publicar una intención sin CLAIM no gasta cupo físico ni duplica consumo.

Recalibrar reconstruye denominadores y contadores desde hechos brutos con versión nueva; puede mostrar vías excedidas. Al cambiar el conjunto de ventanas, reconstruir la proyección sobre las cuentas nuevas, sin trasladar cuota de ventanas vencidas. Si falta historia comparable, abrir época nueva de equidad con motivo y marca de incertidumbre, manteniendo saldos, reservas, deudas, intentos y la espera ya registrada. Nunca hacerlo solo por replanificar. Las reglas de orden detallado de §5 permanecen parte de este diseño sometido a revisión, no una garantía de reparto exacto con operaciones de tamaño desigual.

### Etapas autorizadas tras revisión 8B

| Etapa | Contenido concreto | Criterio de aceptación antes de habilitar la ruta |
|---|---|---|
| I1: núcleo puro | DTO versionado, snapshots sintéticos, filtro vectorial, grafo D2, explicación, asignación determinista y reloj inyectado; Java 21 | Seguridad vectorial, ausencia de doble descuento, 5%/20% entre planes, límites y explicación de todas las operaciones, permutación del resultado completo |
| I2: persistencia/publicación | Nuevos contratos C01/C02/C06/C07, lectura restringida, publicación atómica con sucesor/CAS y atribución de vía | Dos conexiones: publicaciones rivales, claims/recalibración/invalidación simultáneos, inserciones/borrados de conjuntos, rollback sin plan vigente doble ni presupuesto duplicado |
| I3: despacho protegido | Comprobar plan vigente, ventana incluso en TOP_UP, mapping+CLAIM atómicos y permisos; bloquear C03/C04/C05 sin contrato seguro | Pruebas PostgreSQL de retry vencido, cambios de aprobación/worker/contexto, no bypass de wrappers y no reinicio de intentos |

Cambios SQL aditivos y revisables; preservar bytes V1–V11, sin promoción ni despliegue. Primer MVP no remapea reservas a ventanas nuevas, no reanuda CANCELLED_AT_CHECKPOINT automáticamente y no completa integraciones MOCKABLE sin guarda real. Los préstamos/liberaciones automáticos siguen deshabilitados donde falte liquidación segura; registrar `SAFE_SETTLEMENT_REQUIRED`, sin asumir que un recibo sintético demuestra terminación de procesos reales. D4 validará workers/checkpoints reales, D5 integraciones/parsers y D6 permisos de despliegue/retención.

6B conserva la regla de rechazo por límites: toda ejecución futura necesita un perfil explícito de `max_operations/max_edges/max_candidates/max_compute_time`; si falta ese perfil, INVALID_INPUT no publicable. Sus valores se fijarán con la primera implementación medible. Al excederlo: LIMIT_EXCEEDED no publicable, sin truncar grafo ni ocultar compromisos. La escala 1.000/4/5.000 es fixture de exploración, no un SLA. Medir tiempos y características del entorno entonces, sin exigir ahora ≤2 s ni ≤250 ms.

**Autorización recibida:** «si, adelante» después de presentar v0.2. Los incrementos I1–I3 existen como prototipos validados según el [estado de implementación](D3-IMPLEMENTATION.md). El cierre de D3 y el despliegue no están aprobados.

### Revisión integrada posterior

La tabla S01–S18 anterior registra la evidencia existente en v0.2, antes de implementar I1–I3. El [estado revisado por contrato](D3-REVIEW.md) y los [resultados de revisión](../validation/D3-REVIEW-results.json) añaden implementación, carreras SQL, flujos V15 y primera medición de escala. No se han implementado slots CONDITIONAL ni un calendario crítico completo; no se interpreta silenciosamente su ausencia como cumplimiento de toda esta especificación. Se han presentado dos decisiones concretas de alcance/rendimiento para revisión del usuario. D3 permanece abierto.

### Addenda de alcance aprobada tras la revisión integrada

El usuario eligió 1A (MVP conservador) y 2A (optimización). Las referencias anteriores a CONDITIONAL y calendario crítico completo describen una ampliación separada, fuera del MVP aceptado; no se presentarán como funcionalidad ya implementada. [Alcance vigente y optimización](D3-OPTIMIZATION.md). El consumidor HARD sigue bloqueado hasta evidencia real y conserva explicación/cotas de riesgo. No cambia D1/D2 ni autoriza cierre o despliegue.
