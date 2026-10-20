# D3 I3 — despacho protegido

> Estado posterior: **D3 aprobado y cerrado el 2026-10-19** por «si, cierra D3», con el [MVP conservador 1.0](D3-approved.md). Las referencias a D3 abierto en este documento describen la entrega anterior a esa aprobación. No hay promoción ni despliegue aprobado.
Fecha: 2026-10-19. I1–I3 autorizados e implementados como bibliotecas y propuestas SQL. **D3 sigue abierto; no hay aprobación de cierre ni despliegue.**

## Contrato y resultado

[DispatchStore](../../scheduler-postgres/src/main/java/io/github/isidorotrevino/planner/postgres/DispatchStore.java) añade dos entradas del control plane. `claim` recibe IDs explícitos de comando, plan, operación, recurso y worker; devuelve intento, reserva y generación. `execute` recibe ese vínculo, una acción y su carga; no permite sobrescribir identidad/fencing en la carga. Los workers no reciben conexiones SQL. Autenticación HTTP y asignación de identidades reales siguen en D4/D6.

La propuesta [V13](../../migrations-d3-dispatch-proposed/V13__guarded_dispatch.sql) es aditiva sobre V12 y conserva byte por byte V1–V12. El harness I2 sigue usando V1–V12; I3 tiene otra plantilla con las cuatro ubicaciones y prueba también upgrade V12→V13 con plan publicado, reserva y diario previos.

| Entrada | Comportamiento |
|---|---|
| `d3.dispatch` | Exige asignación TENTATIVE del head PUBLISHED vigente, slot iniciado y no caducado, mismas hipótesis de planificación y guardas actuales |
| Mapping | Solo antes de la primera reserva se sustituye el mapping tentativo por el vector completo de la estimación; después se conserva el congelado por D2 |
| CLAIM | Llama a D2 dentro de la misma transacción; reserva o TOP_UP por delta, intento, lease, vía, recibo e historial de despacho se confirman juntos |
| `d3.dispatches` | Hechos inmutables: plan, comando, operación, intento, reserva, estimación, worker, recurso y generación; no edita hijos del plan publicado |
| `d3.execution` | START, HEARTBEAT, CALLBACK, VERIFY y recuperación delegan a D2 con identidad exacta del intento D3; acciones ajenas se rechazan |
| Reintento | Contador original y misma reserva/recurso/pool/vector/vía; ABSENT de la generación anterior sin APPLIED ni UNKNOWN contradictorios |
| Repetición | El mismo comando/contenido devuelve su recibo aunque el plan ya se haya sustituido; no representa una nueva autorización para ejecutar |

## Seguridad y concurrencia

Ambas entradas exigen READ COMMITTED, mutex de publicación antes del global D2 y los locks de relaciones de I2. El adaptador exige autocommit: no mantiene locks durante cómputo, red o ejecución externa. Tras esperar se relee el estado. Dos dispatchers no pueden crear dos intentos de la misma operación.

El hash global de publicación no sirve como precondición de cada CLAIM: el primer CLAIM lo cambia legítimamente. Se comparan las hipótesis del capture —perfil, proyectos, grafo, capabilities/evidencia, heads de estimación/calendario y filas propias de operación/tarea/recurso— y se revalidan los hechos físicos actuales. Así dos workers independientes pueden despachar desde el mismo plan. Los cambios de contexto, prioridad, evidencia o configuración exigen recalcular; el alcance conservador puede invalidar también candidatos ajenos al cambio.

La admisión exige proyecto/tarea activos, excepción P4 todavía válida por camino bloqueante, heartbeat ≤90 s, capacidades JSONB exactas, aprobación vigente, contexto y estimación válida con confianza ≥0,8. D2 sigue verificando intentos y dependencias. Las fases de integración requieren evidencia real; el desarrollo MOCKABLE puede ejecutarse pero no superar VERIFY con una dependencia de tarea MOCKABLE pendiente de contrato de integración real.

Cada cuenta física que limita la duración desde el inicio efectivo debe estar incluida, cubrir el intervalo y conservar confianza suficiente. Cuota desconocida, déficit o delta que no quepa bloquean sin alterar PLANNED/INCIDENT/UNCERTAINTY. Se verifica la ventana también para TOP_UP y al terminar el CLAIM SQL; un fallo revierte todo. Las vías AGED/URGENT conservan su consumo anterior y los topes 5%/20% por cuenta. La clasificación de incidente debe seguir activa; no se toman préstamos automáticos.

La exclusividad efectiva se comprueba contra leases, incluidos RECONCILING y BLOCKED_APPROVAL: un lease caducado no demuestra que haya cesado un efecto externo. Se excluyen worker, tarea y claves compartidas de directorio/entorno. Los slots futuros son intenciones: un inicio ligeramente tardío no impide despachar toda una cola contigua. Si el intervalo estimado desde el inicio efectivo se solapa con otra intención, se emite `D3_REPLAN_REQUESTED` sin modificar el plan; el siguiente CLAIM sigue bloqueado mientras exista el lease incompatible. No hay consumidor de ese evento en ejecución.

START/HEARTBEAT requieren que el plan vigente mantenga la operación, el recurso y su compromiso, y revalidan guardas, perfil, estimación, disponibilidad y ventanas. La renovación exige cobertura para los 60 s del lease D2: cerca de un reset puede bloquearse incluso un trabajo corto. Es un límite conservador de este prototipo; no hay renovación parcial ni checkpoint automático. Un bloqueo no mata el proceso, libera cuota ni acredita que el worker se haya detenido. El fencing y la expiración a RECONCILING conservan el contrato D2. La capa D3 bloquea además retirar el lease por ABSENT o completar recuperación APPLIED si existen recibos contradictorios de la misma generación: falta un protocolo concluyente de reconciliación D4, no se borran recibos para resolverlo.

CALLBACK y las rutas de recuperación permiten registrar hechos sin exigir que continúen vigentes las condiciones de admisión; mantienen el fencing/evidencia D2. Así un déficit o la caída de un worker no borra consumo real. VERIFY exige aceptación y compatibilidad real; este rol no puede fabricar evidencia ni llamar directamente a D2, contabilidad o configuración.

## Validación y límites

La [evidencia I3](../validation/D3-I3-results.json) separa núcleo, integración I2, despacho I3 y regresión histórica D2. Comprueba instalación y upgrade, atomicidad/rollback, repetición, publicación sustituida, dos dispatchers, espera real de mutex ante cambio HARD, dos workers independientes, cola contigua, workspace compartido, cuotas/confianza/ventanas, aprobación caducada sin mutación, capability invalidada, MOCKABLE, retries/UNKNOWN/contradicciones, fencing, renovación con CARRIED y aceptación.

No equivale a ejecutar un worker ni a probar proveedores reales. La suite D2 se conserva en sus bases V1–V11 y la de I2 en V1–V12; la compatibilidad con V13 se prueba mediante los escenarios I3. Los informes I1/I2 son evidencia histórica y permanecen intactos; el exportador usado al entregar I3 registra sus entradas originales.

Pendiente fuera de estas bibliotecas: servicio de solicitudes con recálculos acotados, consumidor de eventos/outbox con debounce/barrido y observaciones de elegibilidad, HTTP y autenticación de workers, checkpoints/preempción/efectos externos, retención y permisos reales. No hay SLA numérico ni plataforma completa. Cerrar D3 exige revisión y aprobación expresa del usuario.

Estado posterior: el [complemento de coordinación](D3-COORDINATOR.md) ya integra solicitudes, ingesta, agrupación y barridos invocables; siguen pendientes su alojamiento y los temporizadores activos. El exportador actual genera evidencia de ese complemento y verifica también las entradas I3 originales.
