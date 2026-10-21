# Handoff D4 — workers y laboratorio Docker

**Estado vigente, 2026-10-20: D4 sintético aprobado y cerrado por el usuario.**
Consultar [alcance aprobado](docs/design/D4-approved.md) y [manifiesto](docs/validation/D4-CLOSURE.json).
El handoff y sus cortes siguientes conservan el estado histórico de su emisión.

Fecha: 2026-10-19. Estado: preparación documental de D4; implementación de D4 pendiente.

Este es el handoff histórico de arranque. El estado posterior y las autorizaciones
expresas de la sesión se consultan en [decisiones D4](docs/design/D4-DECISIONS.md),
[I5 validado](docs/design/D4-I5-CHECKPOINT-LAB.md) e
[I6 validado con límites](docs/design/D4-I6-LONG-RUNNING-LAB.md) e
[I7 polling normal](docs/design/D4-I7-POLLING-LAB.md) e
[I8.2 multicuentas](docs/design/D4-I8-INTEGRATION.md),
[V25 y A16](docs/design/D4-V25-BOUNDARY-LAB.md) e
[I9, reconciliación A17–A19](docs/design/D4-I9-RECONCILIATION-LAB.md). Las frases de implementación
pendiente y decisiones por consultar que siguen pertenecen al punto de partida.

## Mandato y punto de partida

Diseñar D4: protocolo de workers, ejecución supervisada, evidencias, checkpoints y recuperación de efectos externos. Preparar después un laboratorio Docker reproducible para probar esos contratos con procesos reales y proveedores sintéticos. La petición que origina este documento autoriza escribir el handoff y la preparación documental; no equivale a aprobar decisiones pendientes, implementar toda D4, promover migraciones o desplegar servicios.

D1, D2 y D3 están aprobados. D2 está cerrado y su referencia publicada es `69d71c3877e79bdfef088956b090d4eb6b447be9`. D3 quedó cerrado por aprobación explícita «si, cierra D3» el 2026-10-19. Su autoridad vigente es [D3 aprobado](docs/design/D3-approved.md), con [manifiesto de cierre](docs/validation/D3-CLOSURE.json). `published_D3_commit` sigue siendo `null`: no inventar un commit publicado ni confundirlo con la referencia D2.

El árbol local contiene bibliotecas Java/SQL, pruebas y documentos D3 todavía sin publicar. Conservar los cambios existentes. El cierre de D3 no aprobó promoción de migraciones ni despliegue. Los textos antiguos sobre D3 abierto son históricos; prevalecen el diseño aprobado y su manifiesto. Este handoff no altera ese cierre ni inicia la implementación de D4.

## Lectura necesaria, en orden

1. [Índice documental](docs/README.md), [contribuciones](CONTRIBUTING.md) y [seguridad](SECURITY.md).
2. [D1 aprobado](docs/design/D1-architecture-baseline.md): monolito modular Java 21/Spring Boot, PostgreSQL y workers distribuidos mediante polling HTTPS. Sin introducir Kafka, Temporal o Kubernetes por defecto.
3. [D2 aprobado](docs/design/D2.9-approved.md) y [decisiones D2](docs/design/D2-DECISIONS.md): contratos transaccionales, roles, fencing, reservas, efectos y recuperación.
4. [D3 aprobado](docs/design/D3-approved.md), [cierre](docs/validation/D3-CLOSURE.json), [decisiones](docs/design/D3-DECISIONS.md) y [última evidencia](docs/validation/D3-OPTIMIZATION-results.json).
5. [Persistencia D3](docs/design/D3-I2-PERSISTENCE.md), [dispatcher D3](docs/design/D3-I3-DISPATCH.md), [coordinador](docs/design/D3-COORDINATOR.md) y [revisión integrada](docs/design/D3-REVIEW.md).
6. [Implementación](docs/design/D3-IMPLEMENTATION.md), [optimización y límites](docs/design/D3-OPTIMIZATION.md) y [batería D3](testing/D3/README.md).
7. [Preparación del laboratorio D4](testing/D4/README.md): topología propuesta, fases, pruebas y criterios de aceptación.

Después leer el código y SQL que materializan los contratos. Las rutas siguientes parten de la raíz:

| Entrada existente | Contrato que D4 debe reutilizar |
|---|---|
| `scheduler-core/src/main/java/io/github/isidorotrevino/planner/scheduler/PlanningModel.java` y `CapacityScheduler.java` | Snapshot `d3.snapshot.v1`, algoritmo `d3.greedy.v1`, propuestas `TENTATIVE`, `reviewOnly=true`; proponer no autoriza ejecutar |
| `scheduler-postgres/src/main/java/io/github/isidorotrevino/planner/postgres/PlanningStore.java` | Captura inmutable, observación y publicación CAS con readset completo; publicar no reserva capacidad |
| `scheduler-postgres/src/main/java/io/github/isidorotrevino/planner/postgres/DispatchStore.java` | `claim(...)` del plan vigente; `execute(...)` para el intento identificado; el payload no puede sobrescribir su identidad |
| `scheduler-postgres/src/main/java/io/github/isidorotrevino/planner/postgres/PlanningCoordinator.java` | `tick` invocable, inbox durable, debounce ordinario 30 s, eventos críticos inmediatos, sweep 60 s y recálculo inicial + hasta dos reintentos; no daemon |
| V1–V11 en `migrations/` y `migrations-proposed/` | Dominio y ejecución D2: CLAIM, lease, generación, reservas, evidencias y recuperación |
| V12–V15 en las cuatro ubicaciones `migrations-d3-*-proposed/` y `migrations-d3-proposed/` | Snapshots, despacho protegido, coordinador y corrección de reapertura crítica; revisar nombres exactos en el árbol |
| `testing/D3/run-postgres-tests.sh` | Regresión Docker disponible: grupos D3 separados y batería D2 sin modificar |

`DispatchStore` pertenece al control plane; no es un cliente SQL para workers remotos. Sus conexiones requieren autocommit y `READ_COMMITTED`. Mantener el orden de mutex 742001 antes de 742002; no ejecutar procesos externos bajo bloqueos SQL.

## Invariantes que D4 hereda

- Capacidad por cuenta física, dimensión y ventana de proveedor. Reparto por recurso 70% PLANNED / 20% INCIDENT / 10% UNCERTAINTY. Un déficit INCIDENT permanece visible y no toma PLANNED ni UNCERTAINTY. Replanificar no crea cuota ni mueve ventanas.
- Reserva estable por operación entre planes. Tras congelarse el mapping, conservar recurso, pool y cuentas. Reintentar conserva intentos anteriores y usa TOP_UP por delta cuando corresponda; no liberar compromisos por timeout de transporte ni duplicar reservas por redelivery.
- Pesos P0–P4: 8/4/2/1/0 por recurso; trabajo heredado se carga al proyecto ejecutor. Hasta 5% PLANNED para espera elegible de siete días; hasta 20% para caminos con holgura de deadline ≤24 h. P4 solo por excepción del camino bloqueante de trabajo activo de mayor prioridad. PAUSED/ARCHIVED excluidos.
- Dependencias HARD/SOFT/MOCKABLE/OPTIONAL, compatibilidad SemVer y evidencia conservan D2. Heredar prioridad por camino bloqueante no satisface dependencias ni acredita efectos.
- MVP D3 conservador: asignar solo trabajo actualmente elegible. Consumidores HARD siguen bloqueados hasta evidencia real; tienen explicación y cotas de riesgo, sin slots CONDITIONAL ni calendario crítico completo. Esa ampliación quedó separada, no pendiente para cerrar D3.
- Horizonte de siete días civiles Europe/Madrid y persistencia UTC; deadlines como objetivo. No saltar guardas ni proponer aplazamiento automático con `deferral_allowed=false`.
- Confianza mínima 0,8, calibración/procedencia y vigencia de estimaciones y límites; heartbeat de elegibilidad ≤90 s. Una operación por worker y exclusión compartida de workspace/entorno y de la misma tarea, incluso entre contenedores.
- START/renovación deben cubrir íntegramente la lease D2 de 60 s. No existe renovación parcial ni rollover automático a otra ventana. Un trabajo corto cerca del reset puede quedar bloqueado conservadoramente.
- UNKNOWN y evidencia contradictoria conservan compromiso y exclusión. Lease expirada implica reconciliación, no prueba de que el proceso haya terminado. Ningún callback de generación antigua puede modificar el intento vigente.

La última validación tiene 62 pruebas core, 4 de escala, 3 de paridad (82 escenarios diferenciales), 33 I2, 39 I3, 25 de coordinador, 9 de aceptación V15 y 157 de regresión D2, sin fallos, errores ni omisiones. Los grupos históricos usan sus propias versiones V11/V12/V13/V14; no afirmar que todos corrieron sobre V15. Los 29.829 vectores SemVer forman parte de una prueba JUnit.

Las 1.000 operaciones independientes completaron en 6,575 s con presupuesto de 30 s; con 5 s todavía abortan de forma segura sin prefijo publicable. Son observaciones sintéticas, no SLA. El fixture DAG de 1.000 operaciones y 5.000 aristas solo tenía un productor elegible; no demuestra ejecutar o asignar las mil.

## Contratos que faltan en D4

### Transporte e identidad

Definir versión del protocolo HTTPS, registro de capacidades, polling, entrega y confirmación, START, HEARTBEAT, CALLBACK y consultas de estado. Separar entrega de trabajo, autorización vigente de inicio y resultado factual. Versionar sobres con `command_id`, correlación y la identidad de ejecución operación/intento/worker/recurso/generación; ligar contexto y política inmutables a sus hashes. Reutilizar la identidad real D2, sin introducir un contador alternativo que compita con fencing.

Concretar idempotencia de comandos, retención de deduplicación, errores reintentables, backoff acotado y respuesta perdida. Una repetición con igual ID y otro contenido debe rechazarse. El worker autenticado solo puede actuar sobre su identidad/asignación; no obtiene credenciales SQL ni permisos de verificador. La veracidad del contexto y las capacidades anunciadas necesita un mecanismo explícito, no confianza automática en el cuerpo HTTP.

### Proceso y efectos

Diseñar supervisor de subprocesos, límites, workspace, salida estructurada, recogida de logs y recuperación tras reinicio. El worker debe poder distinguir «no iniciado», «en curso», «terminado» y «resultado desconocido», sin convertir ausencia de respuesta en ausencia de efecto.

La exclusión SQL evita asignaciones incompatibles, pero no impide por sí sola que un proceso antiguo siga produciendo efectos. Definir qué receptor comprueba fencing, qué clave deduplica un efecto lógico entre reintentos y cómo se obtiene evidencia autoritativa de APPLIED/ABSENT/UNKNOWN. Separar la clave estable del efecto de la generación de autoridad; no prometer exactly-once en sistemas externos que no lo soportan. Ante un receptor sin deduplicación/consulta fiable, conservar UNKNOWN y requerir resolución conforme a política.

### Evidencia, checkpoints y recuperación

Definir esquema, hash, tamaño, almacenamiento y procedencia de artefactos; validación independiente de Git, checkpoint, rollback y aceptación. Un booleano del worker o un recibo sintético no acredita verdad externa. El ingreso de resultados no concede al worker capacidad de autoaprobar ACCEPTANCE_PASS ni fabricar prueba de parada.

Reutilizar las acciones existentes de `d3.execution`: START, HEARTBEAT, CALLBACK, VERIFY, REJECT_VERIFICATION, EXPIRE, RECONCILE, RESUME_RECONCILIATION y RECOVERY_VERIFY. Diseñar cómo se alimentan de evidencia fiable. VERIFY exige aceptación y dependencias reales compatibles; no omitir guardas por introducir HTTP.

La preempción no interrumpible devuelve DEFERRED_NONINTERRUPTIBLE conservando compromisos. Para trabajo interrumpible, separar solicitud, checkpoint verificado, parada confirmada y liberación. No hay continuación automática desde CANCELLED. Diseñar la continuación como contrato explícito compatible, sin inventar una transición ni reutilizar una generación revocada. Evidencia ABSENT antigua contradicha por UNKNOWN/APPLIED no basta para quitar exclusión; proponer nueva evidencia autoritativa y su transición sin borrar recibos anteriores.

## Decisiones materiales a consultar con opciones

Estas son propuestas para la siguiente sesión, no decisiones ya aprobadas. Primero contrastarlas con los documentos y evitar volver a preguntar acuerdos existentes.

| Decisión | Opción A propuesta | Opción B y coste |
|---|---|---|
| Primer corte ejecutable | Vertical sintética: control plane Java 21/Spring Boot, dos workers de fixture y un receptor de efectos | Adaptador de CLI real desde el inicio: añade credenciales, compatibilidad y reconciliación de proveedor; entra en D5 |
| Identidad del worker | mTLS con CA efímera del laboratorio y certificado ligado a worker; autorización por asignación en servidor | TLS de servidor y token efímero por worker: revocación, almacenamiento y replay requieren diseño adicional |
| Aislamiento inicial | Worker contenedorizado con supervisor de subprocesos de fixtures confiables y workspace propio | Contenedor desechable por operación: mayor aislamiento, requiere un provisionador externo; nunca montar el socket Docker en el worker |
| Continuación de checkpoint | Checkpoint verificado y nuevo intento/generación mediante una transición expresamente diseñada | Solo cancelar y proponer nueva operación enlazada: simplifica la primera entrega, conserva trazabilidad pero no continuidad transparente |
| Efectos sin prueba concluyente | Mantener UNKNOWN y exclusión hasta resolución autoritativa; probarlo en el simulador | Soportar un adaptador real que permita consulta y deduplicación: ampliar alcance por proveedor, sin asumir garantías universales |
| Primera campaña de fallos | Procesos reales, reinicios y red controlada dentro de Docker; proveedor sintético | Incorporar ya laptop/PC/servidor físicos: añade red, identidades y operación D6 antes de cerrar el protocolo |

No pedir al usuario resolver detalles rutinarios de nombres o puertos internos. Sí consultar cambios a contratos aprobados, semántica de continuidad, frontera de confianza o ampliación a proveedores reales. La elección A/B de esta tabla no altera las respuestas A/B históricas de D3.

## Secuencia y entregables de la siguiente sesión

1. Inventariar contratos existentes frente a huecos D4 y confirmar decisiones materiales con propuestas concretas. Escribir `docs/design/D4-workers-draft.md` y `docs/design/D4-DECISIONS.md` como documentos nuevos, marcando pendiente/aprobado y sin inferir aprobación por silencio.
2. Precisar entradas/salidas y secuencias de éxito, fallo y recuperación. Incluir autorización, ownership, estados, claves, ventanas, límites de reintento y quién puede aportar cada evidencia.
3. Tras acordar el primer corte, convertir la [especificación del laboratorio](testing/D4/README.md) en archivos ejecutables y pruebas acotadas. Mantener separadas la validación SQL histórica y la nueva validación de transporte/procesos.
4. Registrar resultados D4 propios: entorno, versiones/digests reales, revisión o hashes de entradas, escenarios, tiempos, fallos y limitaciones. No sobrescribir informes ni manifiesto de cierre D3.
5. Presentar resultados y lo pendiente. No cerrar D4 ni desplegar sin aprobación explícita del usuario.

Conservar V1–V15 y sus ubicaciones. Cualquier SQL D4 aditivo tendrá una ubicación propuesta nueva, configurada explícitamente en su harness, con plantilla y pruebas de upgrade propias. No incorporarlo al descubrimiento de D2: su prueba V10→V11 espera exactamente una migración. Una corrección a D2/D3 debe identificarse como cambio de contrato aprobado y someterse a decisión; no ocultarla en el transporte.

El hosting, los timers de producción, las identidades LOGIN reales, secretos de producción, retención operativa y promoción/despliegue pertenecen a D6. D4 sí debe definir y probar la semántica de autenticación/autorización con identidades sintéticas. Los conectores comerciales, parsers de cuota y límites reales pertenecen a D5; una cuota desconocida bloquea, sin fallback de pago.

## Prompt listo para continuar

> Lee HANDOFF-D4.md y los documentos que indica, incluido testing/D4/README.md. D1, D2 y D3 están aprobados y cerrados; D2 publicado en 69d71c3, D3 con referencia local en su manifiesto de cierre. Inicia el diseño técnico de D4 y prepara el primer corte del laboratorio Docker sintético. Primero identifica contratos existentes y huecos de transporte, identidad, ejecución supervisada, evidencias, checkpoints y reconciliación; pregúntame las decisiones materiales con opciones concretas. Conserva cuentas físicas, reservas entre planes, reparto 70/20/10, dependencias, prioridad por camino bloqueante y fencing. Distingue la batería Docker existente del laboratorio por construir. No uses proveedores ni credenciales reales, no promociones migraciones ni despliegues, y no cierres D4 sin mi aprobación. Mantén diseño y validación acotada y responde en español.

A20–A22 posteriores aprueban ausencia sin progreso, revisión con delta cero y caso
separado con cuarentena. [I10.1](docs/design/D4-I10-ABSENCE-LAB.md) distingue la
ruta de ausencia implementada de las barreras de revisión/reapertura entonces pendientes.

[I11](docs/design/D4-I11-REVIEW-QUARANTINE-LAB.md) implementa A21/A22 mediante
revisión de delta cero y cuarentena separada con contención independiente. V28
sigue propuesta de laboratorio; consultar su evidencia y límites, sin cerrar D4.

[I12](docs/design/D4-I12-INTEGRATED-VERIFIERS-PRESENCE.md) porta verificadores a Java
bajo A23=B e incorpora presencia durable A24=A. La revisión final y evidencia
actual se consultan junto a su tabla de aceptación; D4 sigue abierto.
