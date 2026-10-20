# D4 I5 — contrato concreto de checkpoint para decisión

Estado: **opciones A/A aprobadas expresamente para implementar en el laboratorio**.
La [implementación I5](D4-I5-CHECKPOINT-LAB.md) delimita cobertura y pendientes.
El texto siguiente conserva el contrato sometido a decisión tras I4.
A01–A07 siguen vigentes. Este documento concreta la ruta candidata de
[D4-CHECKPOINT-CONTINUATION](D4-CHECKPOINT-CONTINUATION.md); no crea SQL, endpoints
ni cambios de estado ejecutables. D4 permanece abierto.

## Diferencias comprobadas frente a los contratos actuales

| Frontera | Guarda vigente | Extensión que necesita I5 |
|---|---|---|
| `d2.preempt`, V9 | Libera compromiso con un recibo booleano; no liquida consumo parcial | Nueva transacción compuesta, sin llamar primero a preempt |
| `d2.transition`, V9 | Rechaza CANCELLED→READY; tampoco existe ese arco en V4 | Entrada específica con procedencia y versión; no abrir la transición genérica |
| `d3.observe_eligibility`, V12 | Reintento exige ABSENT sin recibos contradictorios | Admisión explícita de checkpoint sellado, conservando las demás guardas |
| `PlanningStore.read` y `CapacityScheduler` | `retrySafe` se deriva de ausencia concluyente; false bloquea | Adaptador D4 versionado con prueba tipada de continuación; no inyectar true desde el worker |
| `d3.publish`, V12 y `d3.dispatch`, V13 | Ambos vuelven a exigir ABSENT para intentos anteriores | Publicación y despacho D4 protegidos; no basta añadir una ruta de CLAIM |
| Captura/CAS/coordinación, V12–V15 | Readset conocido, publicación CAS, ticks e inbox | Incluir intención, checkpoint y autorización de continuación en readset y eventos |
| Receptor I3/I4 | Cierre durable por generación; query por paso | Respuesta de cierre con manifiesto completo y hash/secuencia estable, recuperable tras respuesta perdida |
| Verificador I4 | Un fixture/efecto y aceptación final | Verificación de prefijo, sufijo y consumo por paso; checkpoint no es ACCEPTANCE_PASS final |

Cambiar solo el estado a READY no serviría: observación, adaptación Java,
publicación y despacho seguirían rechazando el APPLIED previo. Se conserva V1–V18
y el código de cierre D3; la implementación candidata requiere componentes D4 y
migraciones propuestas nuevas. No se modifica el readset sin su prueba de CAS.

## Propuesta A: CANCELLED con procedencia sellada

Se conserva la propuesta anterior. El checkpoint deja el intento CANCELLED y la
operación CANCELLED con un hecho inmutable `CHECKPOINT_COMMITTED`. Únicamente una
autorización explícita ligada a ese hecho permite CANCELLED→READY por una entrada
nueva. La transición genérica D2 sigue rechazándola. Una cancelación ordinaria no
puede convertirse en checkpoint ni recibir autorización retrospectiva.

No se implementa aún ninguna de las entradas candidatas siguientes:

| Comando candidato | Quién lo solicita | Resultado y atomicidad |
|---|---|---|
| REQUEST_CHECKPOINT | Control plane autorizado | Identidad completa, expected row_version, command_id y razón; registra solicitud. No libera ni liquida |
| COMMIT_CHECKPOINT | Control plane con prueba del verificador | Valida identidad y prueba, liquida consumo incremental, libera remanente, termina intento, elimina lease/exclusión, cancela operación y registra procedencia/historia/outbox en un commit |
| AUTHORIZE_CONTINUATION | Decisión explícita del control plane; driver solo en laboratorio | Enlaza checkpoint exacto, expected row_version, intención y motivo; cambia CANCELLED→READY. No reserva, no crea intento ni autoriza spawn |
| CLAIM_CONTINUATION | Despachador autenticado y plan publicado vigente | Revalida todas las guardas, TOP_UP original, nuevo intento/generación, enlace exclusivo del checkpoint y entrega durable en un commit |

Todos los comandos tienen schema_version y request completo inmutable. Mismo ID y
contenido devuelve el recibo original, aunque el estado posterior haya cambiado;
mismo ID con contenido/principal distinto rechaza. Un comando nuevo no vuelve a
liquidar un checkpoint consumido. La cadena checkpoint→intento sucesor es única:
una autorización no permite crear dos hijos ni rejuvenece el límite de intentos.
Los locks siguen 742001→742002; SQL no espera procesos ni consultas HTTPS.

Para el primer incremento se propone COMMIT_CHECKPOINT solo desde RUNNING con
lease aún vigente. Verificador, parada y cierre ocurren fuera de SQL; el commit
comprueba de nuevo estado, lease, generación y versión. Si vence o cambia antes del
commit, rollback completo: permanece el compromiso y se exige reconciliación.
No se rebautiza una recuperación tardía como checkpoint vivo. Incluir desde ahora
RECONCILING requeriría otra guarda de recuperación parcial, fuera de esta propuesta
acotada. LEASED sin spawn y operaciones no interrumpibles no entran en este fixture:
la solicitud no interrumpible devuelve DEFERRED_NONINTERRUPTIBLE sin modificar saldo.

## Intención, prueba y cierre

Antes del primer CLAIM se congela `d4.steps.v1`: pasos y dependencias, hashes de
entradas/salidas esperadas, clave lógica operación/revisión/paso y asignación del
consumo por cuenta. Cambiar un paso conserva el conflicto bajo su clave, no crea
una intención sustituta. La política y el contexto originales siguen congelados.

La prueba del verificador liga operación/intento/worker/recurso/generación,
checkpoint y solicitud, intención/contexto/política, artefactos y hashes, observación
independiente de parada y cierre firmado por el receptor con secuencia/manifiesto
final. Por cada paso de la intención debe haber APPLIED esperado o ABSENT concluyente
tras cierre. No puede omitir pasos, canales ni efectos aplicados inesperados.

El primer fixture tiene dos pasos ordenados: step-1 APPLIED, step-2 ABSENT después
de cierre. El sufijo es exactamente step-2. Ni APPLIED parcial ni checkpoint
acreditan tarea DONE, capacidad AVAILABLE o ACCEPTANCE_PASS final. Si todos los
pasos ya están APPLIED, corresponde verificación final, no crear un intento vacío.
UNKNOWN o evidencia contradictoria en cualquier generación de la cadena bloquean;
esta propuesta no contiene un mecanismo para resolverlos.

El nuevo grant autoriza solo el sufijo. El receptor conserva la misma intención,
deduplicación de step-1 y cierre de la generación anterior; no instala generación
nueva sin ese cierre. Solo el control plane firma tras CLAIM/START/renovación SQL.
Un fallo al entregar/instalar grant no borra la lease ni permite repetir el CLAIM.

## Contabilidad exacta y procedencia

Por cada cuenta vinculante se toma el consumo acumulado verificado C y el consumo
ya asentado para esa misma cadena S. Se registra únicamente delta=C−S, con delta
no negativo y procedencia completa de todos los pasos. No se acepta la suma libre
del worker. Un delta negativo, una cuenta omitida o repetida, o un recibo de consumo
no verificable rechazan el commit; no se corrige automáticamente mediante ADJUST.

El ejemplo revisable usa consumo aditivo de 4 y 6 unidades. La fixture tiene costes
por paso preautorizados; no generaliza esta calibración a un proveedor real.

| Momento, cuenta física con capacidad 100 | Comprometido PLANNED | Consumido acumulado | Disponible PLANNED |
|---|---:|---:|---:|
| CLAIM inicial | 10 | 0 | 60 |
| COMMIT_CHECKPOINT, step-1 verificado | 0 | 4 | 66 |
| CLAIM_CONTINUATION: TOP_UP conservador original | 10 | 4 | 56 |
| Callback final: solo consumo incremental step-2 | 0 | 10 | 60 |

La primera liquidación puede usar CONSUME settled=4/consumed=4 y RELEASE settled=6,
dentro del mismo commit; un fallo entre ambos hace rollback de ambos. Si existe
consumo asentado previo, el plan de liquidación se deriva del journal y de la prueba,
no se vuelve a facturar el acumulado. La fixture inicial no cubre sobrecoste por
encima del compromiso: se conserva bloqueo hasta revisión, sin inventar financiación.

INCIDENT=20 y UNCERTAINTY=10 permanecen intactos. Reserva, recurso, cuentas,
ventanas, pool y vía se conservan. La contabilidad no mueve consumos a otro plan ni
ventana. Con solo 6 disponibles, el TOP_UP de 10 bloquea como exige A07. La estimación
de duración sigue siendo conservadora; no se introduce ahora una estimación residual.

## Admisión y publicación de la continuación

El contrato externo candidato `d4.continuation.snapshot.v1` incluye la prueba de
admisión tipada (inicial, ausencia concluyente o checkpoint sellado), IDs/hashes y
readset. No altera el significado del snapshot d3.v1 ni fabrica ABSENT de step-1.
Un adaptador D4 podrá reutilizar el cálculo Java solo después de validar ese contrato;
no cambiará la guarda mediante un booleano enviado por el worker.

Observación, publicación y CLAIM vuelven a comprobar identidad/chain única,
checkpoint y autorización, versión, límite de intentos, plan vigente, dependencias
HARD e integración real, aprobación fresca, capacidades autorizadas y presencia,
confianza/calibración/vigencia, calendario, todas las cuentas/ventanas vinculantes,
TOP_UP, vía/pool, exclusiones de worker/tarea/workspace y prioridad por camino
bloqueante. No se introducen slots CONDITIONAL, rollover, préstamo entre pools ni
excepción P4 ajena al camino. La prueba forma parte del CAS: invalidarla o cambiar
la autorización entre captura y publicación invalida esa publicación.

## Campaña propuesta, todavía no ejecutada

| Grupo | Debe demostrar |
|---|---|
| Upgrade aislado | V18→versión propuesta con lease I4 activa; sin mutar journal, identidad ni reservas existentes |
| S05 parcial | step-1, parada/cierre, consumo 4, checkpoint, autorización, publicación, TOP_UP 10, nueva generación, solo step-2, consumo total 10 y aceptación final independiente |
| Respuestas perdidas | Cierre persistido con respuesta perdida; consultar/repetir el mismo cierre tras reinicio. COMMIT/AUTHORIZE/CLAIM perdidos se recuperan sin repetir liquidación/intento |
| Concurrencia | Dos commits, autorizaciones y claims rivales producen un checkpoint, un enlace sucesor y un TOP_UP |
| Evidencia inválida | Truncada, firma/hash/campaña distintos, paso extra/omitido, consumo sin procedencia, proceso vivo, diario perdido, UNKNOWN/contradicción: sin liberación |
| Frontera de lease | Vence entre verificación y commit: rollback y compromiso retenido; grant anterior nunca recupera autoridad |
| Revalidación | Cuenta vencida/desconocida, déficit, aprobación/contexto distintos, dependencia invalidada, max_attempts agotado, plan obsoleto o workspace ocupado: sin CLAIM |
| Procedencia | Cancelación ordinaria, checkpoint viejo consumido o intento/generación ajenos: sin continuación |
| Regresión | I4 S01–S04 y pruebas D2 inalteradas; grupos D3 afectados en copia separada, además de sus hashes de cierre |

Preparar estos casos no cuenta como ejecutarlos. La aprobación A/A de las decisiones siguientes autoriza implementar este corte;
no convierte la matriz completa en pruebas ejecutadas.

## Decisiones materiales: A/A elegidas por el usuario

1. **Ciclo de vida. A recomendada:** aprobar para el laboratorio el contrato anterior
   con CANCELLED→READY exclusivamente por procedencia sellada y autorización
   explícita. **B:** usar un estado nuevo CHECKPOINTED→READY; mejora la distinción
   visible, pero exige ampliar restricciones, transiciones y lectores del dominio.
   Ambas opciones conservan operación/reserva/cuentas y crean nuevo intento/generación.
2. **Primera frontera de lease. A recomendada:** implementar primero checkpoint
   RUNNING con lease vigente; vencimiento antes del commit queda en reconciliación
   sin continuidad automática. **B:** incluir ya commit desde RECONCILING con
   recuperación parcial concluyente; amplía contrato, permisos y pruebas y no
   permite resolver UNKNOWN/contradicción automáticamente.
