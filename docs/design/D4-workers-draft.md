# D4 — protocolo y laboratorio sintético, borrador técnico 0.1

Avance validado: [I5](D4-I5-CHECKPOINT-LAB.md), continuidad parcial con contrato
A08/A09 aprobado y S01–S05 ejecutados. [I6](D4-I6-LONG-RUNNING-LAB.md) implementa
ejecución prolongada y cooperación bajo A10/A11; S01–S09 validados con límites explícitos.
[I7](D4-I7-POLLING-LAB.md) añade polling normal y retirada verificada; S01–S12
validados. A12 exige pausa completa tras checkpoint y rearme explícito; S13 documenta
la [validación posterior](../validation/D4-I7-A12-results.json).
Las secciones de huecos siguientes describen el punto de partida histórico.
Los documentos de cada incremento delimitan su implementación y evidencia efectiva.

Fecha: 2026-10-19. **Diseño en curso, no aprobado en conjunto; D4 abierto.**
Decisiones de dirección aceptadas: [D4-A01–A11](D4-DECISIONS.md).
Lecturas base: [handoff](../../HANDOFF-D4.md), índice, contribuciones, seguridad,
D1, D2 aprobado/decisiones, D3 aprobado/cierre/decisiones/última evidencia,
I2, I3, coordinador, revisión, implementación, optimización y README D3/D4.
Se contrastaron los entrypoints Java, V9/V13 y el runner Docker histórico;
esto es una revisión dirigida de contratos, no una nueva auditoría integral SQL.

## Contratos existentes y huecos comprobados al iniciar D4

| Área | Fuente existente | Qué falta en D4 |
|---|---|---|
| Planificación | `PlanningModel`, `CapacityScheduler`: `d3.snapshot.v1`, `d3.greedy.v1`, `reviewOnly=true`, TENTATIVE | Un transporte no puede convertir propuesta/publicación en permiso de arranque |
| Publicación | `PlanningStore`, V12: captura inmutable, readset completo, CAS | Hosting HTTPS y consultas de estado con permisos; publicar no reserva |
| Asignación | `DispatchStore.claim`, V13 `d3.dispatch`: mapping+CLAIM, reserva/intento/generación atómicos, plan vigente | Polling, entrega durable, confirmación y recuperación de respuesta perdida |
| Ciclo | `DispatchStore.execute`, V13 `d3.execution`: identidad exacta no sobrescribible | Vincular principal autenticado a esa identidad y restringir acciones por rol |
| Idempotencia | V8/V12: recibo persistente y comparación JSONB completa | Sobre HTTP, deduplicación de entrega, consulta tras timeout, límites y errores públicos |
| Coordinación | `PlanningCoordinator`, V14/V15: tick, inbox/outbox durable, 30 s/60 s y dos recálculos | Driver de ticks de laboratorio; no se presupone daemon de producción |
| Identidad | Worker/recurso/capacidades en dominio; roles NOLOGIN de prueba | CA sintética, registro autorizado, revocación/expiración, LOGIN mínimos de laboratorio |
| Proceso | V9 registra estados/intentos/lease | Diario local, supervisor, grupo de procesos, límites, recuperación y prueba de parada |
| Efectos | V9 `effect_receipts`, fencing D2; V13 bloquea contradicciones | Receptor que comprueba autoridad en cada efecto y consulta independiente APPLIED/ABSENT/UNKNOWN |
| Evidencia | Snapshots/receipts append-only, aceptación PASS sin FAIL | Almacén de bytes, procedencia, verificador independiente de Git/artefactos/checkpoint/parada |
| Preempción | V9 `d2.preempt`: solicitud, DEFERRED_NONINTERRUPTIBLE, recibo seguro y cancelación | V13 no expone preempt. Entrada aditiva protegida, sin bypass a D2 desde HTTP |
| Continuidad | CANCELLED bloqueado por `RESUME_CONTRACT_REQUIRED`; no arco autorizado | Diseñar continuación de la misma operación; decisión A03 no aprueba un arco concreto |
| Reconciliación | EXPIRE→RECONCILING; APPLIED→VERIFYING; ABSENT→RETRY_PENDING; UNKNOWN→BLOCKED_APPROVAL | Acreditar verdad y parada; contradicciones quedan bloqueadas por A04 |

Conexiones del control plane: autocommit READ_COMMITTED. Orden 742001→742002.
Ni procesos ni consultas al receptor ni red bajo locks SQL. Los workers nunca
reciben SQL ni permisos de verificador o administrador de capacidad.

## Invariantes que no se renegocian

Cuentas físicas por recurso/dimensión/ventana real, compartidas entre planes.
70/20/10 PLANNED/INCIDENT/UNCERTAINTY; déficit INCIDENT visible sin tomar los otros
pools. NULL bloquea. Sin rollover ni renovación parcial: START/HEARTBEAT deben
cubrir 60 s completos. Confianza ≥0,8 y heartbeat de elegibilidad ≤90 s.

Reserva estable por operación y mapping/recurso/pool/vía congelados; retries por
delta TOP_UP y consumo anterior conservado. Tres intentos totales por defecto,
máximo configurable veinte. Una entrega HTTP repetida no crea un intento.
Una operación por worker; exclusión de tarea/workspace/entorno entre contenedores,
también durante UNKNOWN o reconciliación. Expirar lease no prueba parada.

Dependencias HARD/SOFT/MOCKABLE/OPTIONAL y SemVer D2 intactos. HARD requiere
evidencia real. P0–P4 8/4/2/1/0; herencia solo por camino bloqueante, excepción P4
aprobada, PAUSED/ARCHIVED excluidos. Servicio al ejecutor, vías 5%/20% vigentes.
Siete días civiles Europe/Madrid, persistencia UTC; `deferral_allowed=false`
conservado. No añadir CONDITIONAL ni calendario crítico completo.

## Sobre y API propuestos

Versión `d4.worker.v1`. JSON UTF-8 con campos explícitos: `command_id`,
`correlation_id`, `action`, `plan_id`, `operation_id`, `attempt_id`,
`reservation_id`, `worker_id`, `resource_id`, `generation`, `context_sha256`,
`policy_sha256`, `payload`. La generación es la real D2, no un contador D4.
El servidor reconstruye la identidad del dispatch persistido y compara el sobre.
Rechazar claves duplicadas JSON, acciones/campos desconocidos y cambio de identidad.
Los hashes de política siguen calculados por PostgreSQL sobre `jsonb::text`;
el hash de artefactos/contexto se comprueba contra sus bytes exactos.

| Entrada propuesta | Principal | Semántica |
|---|---|---|
| POST `/d4/v1/register`, `/presence` | Worker conocido | Registro observado contra catálogo autorizado; nunca autoalta de privilegios |
| POST `/d4/v1/poll` | Worker | Una asignación propia o vacío; recuperar entrega sin otro CLAIM |
| POST `/d4/v1/ack` | Worker | Confirma recepción, no inicia, renueva ni libera |
| POST `/d4/v1/execution` | Worker | Solo START, HEARTBEAT y CALLBACK sobre asignación propia |
| GET `/d4/v1/commands/{id}`, `/assignments/current` | Dueño o control plane | Estado durable; un recibo histórico no es permiso vigente |
| POST `/d4/v1/artifacts` | Worker/verificador según tipo | Ingreso de candidatos acotados; no aceptación automática |
| API interna de verificación/recuperación | Verificador/control plane | VERIFY, REJECT_VERIFICATION, EXPIRE, RECONCILE, RESUME_RECONCILIATION, RECOVERY_VERIFY según rol |

Propuesta de límites locales: sobre 64 KiB; artefacto 8 MiB; logs 1 MiB por stream,
con marca de truncado y hash de lo realmente conservado. Poll corto cada 2 s,
heartbeat de ejecución cada 15 s, timeout HTTP 5 s; backoff con jitter 1–10 s,
cinco retransmisiones por intercambio y después consulta/bloqueo visible.
Son límites de laboratorio, no SLA ni cambios de lease. Registrar reintentos y
duraciones. Acotar también cuerpo, conexiones y espera en servidor.

Mismo comando y JSONB normalizado completo devuelve recibo persistido; contenido
distinto produce 409. Normalización no elimina campos de identidad ni hashes.
Autenticar/autorizar antes de devolver recibos, incluso en replay. Guardar recibo
y cambio de dominio atómicamente; no escribir un segundo log HTTP desacoplado que
pueda afirmar éxito tras rollback. Retención sin borrado automático conforme D2.
El polling debe recuperar un CLAIM confirmado cuya respuesta se perdió: vínculo
durable de entrega/asignación, no una nueva selección ciega.

Errores públicos propuestos: 400 entrada; 401 identidad inválida cuando se alcance
HTTP (TLS puede rechazar antes); 403 ownership/rol; 409 conflicto/fencing/estado;
412 guarda de admisión; 413 tamaño; 429/503 saturación o infraestructura.
No mapear todo 40001 a retry del efecto: puede exigir replanificar o reconciliar.
Un timeout/5xx tiene resultado desconocido; consultar/repetir el mismo command ID.
No exponer SQL ni secretos en errores.

## Identidad y frontera de confianza

mTLS con CA por campaña, SAN ligado a identidad sintética y allowlist del servidor
con serial, vigencia y revocación. Identidades distintas para workers, verificador
y driver. Validar cadena, SAN y uso; revocación comprobada por petición, incluidas
conexiones ya abiertas. No confiar en `worker_id` del cuerpo ni cabeceras de proxy.
El catálogo fija capacidades y versión/hash de fixtures permitidos; el anuncio
observado puede reducir disponibilidad, nunca ampliar autoridad. mTLS acredita
principal, no que un worker arbitrario sea honesto ni su host esté aislado.

Contextos por contenido, política inmutable y manifiesto autorizado de fixture;
verificar bytes antes de spawn. El worker no recibe un comando shell libre.
LOGIN efímeros separados: migrador, control plane, verificador y auditor.
Grants enumerados sobre entrypoints; sin dueño de esquema en runtime ni DML libre.
Persistir registro de presencia mediante API limitada es trabajo aditivo pendiente.

## Supervisor y autorización de efectos

Diario por intento en volumen del worker: RECEIVED, START_REQUESTED,
START_CONFIRMED, SPAWN_INTENT, RUNNING, EXITED y UNKNOWN son estados locales,
no nuevos estados SQL. Escritura durable antes de spawn; guardar identidad de
arranque, grupo de procesos, argumentos de fixture, workspace y salida estructurada.
El PID solo no identifica un proceso tras reinicio/reutilización. Si hay hueco
entre spawn y registro, no volver a ejecutar: UNKNOWN y verificación.

Supervisor no root, grupo de procesos propio, timeout de fixture, TERM y KILL
acotados, esperar/recolectar descendientes. Reinicio de supervisor impide nuevo
spawn hasta conciliar su diario. Diario ausente/corrupto no acredita NOT_STARTED.
Solo NOT_STARTED probado permite considerar ausencia; exit code no prueba efecto.
La parada independiente se observa desde el host sobre el contenedor identificado
y su grupo de procesos; el worker no puede fabricar `process_stopped=true`.

Separar START confirmado de capacidad de producir efectos. Un replay START puede
devolver éxito antiguo: comprobar estado vigente antes del spawn y, sobre todo,
en el receptor al admitir cada efecto. Ninguna comprobación HTTP previa elimina
por sí sola la carrera con expiración; el fixture calcula localmente y todos sus
efectos pasan por el receptor controlado. No se generaliza a CLI real.

Clave estable de efecto: operación + nombre lógico de paso + revisión de intención;
no incluye intento ni generación. Payload distinto con la misma clave se rechaza.
La generación identifica autoridad, nunca sustituye la clave de deduplicación.
Receptor durable: transacción local única para comprobar grant activo, deduplicar,
aplicar efecto sintético y anexar recibo. El grant procede del control plane
autenticado, con identidad D2 y vencimiento máximo de la lease. No basta aceptar
el mayor número que envía un worker. Revocación/cierre y aplicación se serializan
en el receptor; grant perdido/no comprobable implica rechazo/UNKNOWN.

La sincronización exacta de grants con commit SQL es un punto de integración
pendiente: autorización SQL primero, habilitación del receptor después; fallos
entre ambos conservan compromiso y se consultan. Cerrar receptor y probar parada
antes de retirar exclusión. Un efecto autorizado justo antes de expirar puede
terminar aplicado; reconciliarlo, nunca inferir ABSENT por reloj. No se promete
atomicidad entre dos bases ni exactly-once universal.

## Evidencias y secuencias

Manifiesto de artefacto: versión, ID, tipo, tamaño, SHA-256, medio, referencia local
por contenido, identidad completa, productor autenticado, instante de observación
y método/versión del verificador. Almacén sin rutas arbitrarias, enlaces simbólicos
ni extracción insegura; escritura temporal, hash y promoción atómica a inmutable.
Sin borrado automático. Separar candidato del worker de evidencia verificada.

El verificador obtiene bytes y consulta directamente el receptor; contrasta
workspace y proceso por canal de observación independiente. Git requiere inspección
del repositorio fixture/objetos y árbol esperado; rollback exige comprobar estado
restaurado. Un booleano, log o hash válido solo no prueba aceptación o ausencia.
Pruebas del receptor solo acreditan verdad dentro del proveedor sintético.

1. Éxito: tick→plan publicado→poll/CLAIM→ACK→START→grant→spawn→efecto durable→
   CALLBACK→aceptación independiente→VERIFY. Comprobar reserva, consumo y exclusión.
2. Competencia: dos workers, misma operación/cuenta física; un CLAIM ganador,
   ninguna reserva duplicada. Segunda operación disputa saldo y clave exclusiva.
   Dos workers no crean dos saldos: el fixture usa recursos ligados al worker y
   cuentas reales del modelo; una cuenta común solo mediante recurso válido,
   sin relajar `resource.worker_id`. Dos planes enlazan la misma reserva.
3. Callback perdido: efecto APPLIED confirmado; perder callback, expirar realmente
   lease→EXPIRE→RECONCILE(APPLIED)→aceptación→RECOVERY_VERIFY con consumo trazable.
   Si el callback pudo confirmar, consultar antes de recuperar para no contabilizar dos veces.
4. Proceso superviviente: cortar renovaciones, esperar vencimiento real PostgreSQL,
   EXPIRE; proceso aún vivo y efecto sin resolver mantienen exclusión/compromiso.
   Receptor rechaza efecto tardío sin grant vigente. Callback viejo no revive lease.
5. ABSENT solo tras cierre autoritativo del canal de efectos y parada probada;
   después RECONCILE y transición D2 protegida hacia READY, nunca CLAIM directo
   desde RETRY_PENDING. UNKNOWN→BLOCKED_APPROVAL conserva lease. Contradicciones
   siguen bloqueadas incluso si se añade un recibo más reciente, por A04.

## Continuación desde checkpoint: propuesta a revisar

V9 cancela y libera compromiso pendiente tras recibo seguro. No se cambiará esa
función histórica ni se tratará CANCELLED como pausa. Propuesta aditiva D4:
hecho `continuation_authorization` que enlaza operación, intento/generación anterior,
checkpoint verificado, parada/cierre de efectos, consumo parcial liquidado y hashes
compatibles. Solo cancelación originada por checkpoint, no cancelación genérica.

Entrada nueva candidata CANCELLED→READY, bajo mutex/row_version y command ID;
no reanuda proceso ni incrementa generación por sí sola. Un plan nuevo elegible
y `d3.dispatch` crearían el siguiente intento y generación D2, con misma reserva,
mapping/recurso/pool/vía y TOP_UP por delta sujeto a disponibilidad/ventanas.
No rejuvenecer contador ni crear operación sustituta. Si ventana original venció,
está agotado el límite o cambió contexto/política incompatible, bloquear.

**No implementable aún tal cual:** V13 exige ABSENT sin contradicciones para todo
retry; un checkpoint con efectos parciales APPLIED no cumple esa guarda. El diseño
definitivo necesita un guard específico de continuación por pasos ya acreditados,
sin convertir APPLIED en ABSENT ni repetir efectos. También necesita liquidación
atómica del consumo parcial antes de RELEASE y nueva estimación compatible con
mapping congelado. La elección posterior A05 fija diseñar efectos parciales;
A06 fija grant acotado y cierre durable, y A07 conserva TOP_UP al vector original.
El [contrato de continuidad propuesto](D4-CHECKPOINT-CONTINUATION.md) concreta esos
puntos; requiere aprobación del contrato concreto y upgrade propio antes de
habilitarse. V16 de entrega no modifica estas guardas.

## Preparación del primer corte y criterios de revisión

La [preparación del laboratorio](../../testing/D4/README.md) distingue runner
histórico de la campaña Compose nueva. [Plan de construcción](../../testing/D4/FIRST-CUT.md)
y escenarios enumeran archivos e hitos. Preflight ejecutable de solo lectura:
no arranca contenedores, construye, descarga, migra ni modifica targets D3.
V16 y su harness propio implementan entrega durable de persistencia, documentada
en [I1](D4-I1-DELIVERY.md). [I2](D4-I2-HTTPS.md) implementa el adaptador Spring/HTTPS,
catálogo de certificados autorizado, polling en servidor y recibos de sobre
completo sobre V17. Su evidencia es de transporte; no se atribuye a procesos
ni a escenarios completos solo por existir en un manifiesto.

[I3](D4-I3-PROCESS-EFFECTS.md) añade bibliotecas de supervisor y receptor que prueban
procesos/diario a nivel de componente. [I4](D4-I4-LAB.md) añade conexión al control
plane, grants derivados de lease real, verificación independiente y Compose. Sus
resultados se registran aparte de los de esas bibliotecas.

Primer incremento funcional revisable: cuatro escenarios iniciales con observación
HTTP+SQL+proceso+receptor, mTLS/ownership, cero salida externa, cero puertos,
reinicios conservando datos, evidencias antes de cleanup selectivo. Segundo:
checkpoint/preempción y contrato de continuidad aprobado. Contradicciones permanecen
conservadoras. Informes D4 separados con hashes/digests/versiones reales, seed,
duración y distinción infraestructura/aserción/regresión. No sobrescribir cierre D3.

[I8.1](D4-I8-COMPONENTS.md) añade cálculo generalizado y verificadores locales
bajo A13–A15. No modifica las rutas v1 ni acredita integración SQL/HTTPS multicuentas.

[I8.2](D4-I8-INTEGRATION.md) integra posteriormente SQL/HTTPS multicuentas y
checkpoints lineales: S14 y regresiones S05/S13 sobre V24 propuesta. Sigue abierto D4.
