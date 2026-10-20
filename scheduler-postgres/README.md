# D3 PostgreSQL adapter — I2

Estado vigente: [D3 aprobado y cerrado como MVP conservador 1.0](../docs/design/D3-approved.md) por «si, cierra D3». Las notas anteriores de cierre pendiente son históricas; no hay despliegue aprobado.
Biblioteca JDBC Java 21 y propuesta SQL V12 para conectar el núcleo puro con PostgreSQL. Diseño e inicio de implementación aprobados; **D3 continúa abierto**. No arranca Spring Boot, workers ni un despachador.

## Flujo ejecutable

1. Un administrador configura perfil explícito, época de equidad con motivo y calibración, estimaciones versionadas por recurso y calendarios mediante `d3.configure`. Las estimaciones tienen vector completo por cuentas, duración, confianza, procedencia y caducidad. Sus revisiones son inmutables; cambiar el head usa comparación del predecesor esperado.
2. El control plane puede llamar a `observeEligibility` al procesar eventos o barridos. La muestra registra su validez máxima; no acumula espera indefinida después de caducar heartbeat, estimación, aprobación, calendario o cuenta. Comenzar un intento cierra el intervalo anterior. No hay un consumidor de eventos en ejecución.
3. `PlanningStore.capture(connection, commandId)` devuelve un token y un snapshot tipado procedente de un cuerpo inmutable. El hash completo se calcula en PostgreSQL, con JSONB y UTC. Releer el token devuelve el mismo contenido aunque el estado vivo cambie.
4. El cálculo Java ocurre después de finalizar la transacción de captura. Dependencias/SemVer/evidencia y compatibilidad técnica vienen de D2; no existe un segundo intérprete SemVer. Los requisitos JSONB anidados de recurso y worker se conservan mediante marcadores por operación calculados por SQL.
5. `publish` solicita explícitamente publicar la intención. Revalida todo el estado bajo locks, comprueba el head esperado y confirma snapshot, hijos, supersesión y outbox juntos. No reserva capacidad para operaciones nuevas; enlaza reservas existentes sin repetirlas.

```java
var store = new PlanningStore();
// connection: control plane restringido, autocommit y READ COMMITTED.
var captured = store.capture(connection, java.util.UUID.randomUUID());
var result = new io.github.isidorotrevino.planner.scheduler.CapacityScheduler()
    .plan(captured.request(), captured.snapshot());
var planId = store.publish(connection, commandId, newPlanId, captured, result);
```

Usar IDs de comando estables para reintentar el mismo contenido confirmado; cambiar contenido con el mismo ID da conflicto. SQLSTATE 40001 exige nuevo snapshot/cálculo; la política aprobada permite dos recálculos antes de informar STALE. El bucle de solicitudes, temporizadores y consumo/acuse de outbox no están implementados por esta biblioteca.

La conexión se exige en autocommit READ COMMITTED para no conservar locks durante el cálculo. Las funciones SQL no llaman a servicios externos. Un `Result` del núcleo sigue siendo una propuesta `reviewOnly`; solo la invocación explícita del publicador crea el snapshot PUBLISHED, y eso tampoco autoriza CLAIM.

## Datos y límites

- Settings y épocas son explícitos. Cambiar una época no borra diario, consumo, deuda, reservas, intentos ni espera observada. El gasto AGED/URGENT se deriva de saldos de reservas y atribuciones inmutables, sin filtrarlo por época.
- La historia sin atribución conserva diagnóstico de incertidumbre. La atribución de reservas legadas exige un administrador y motivo; el despachador I3 tendrá que atribuir nuevas reservas al confirmar CLAIM.
- Ventanas desconocidas o vencidas, confianza baja, evidencia incompatible y aprobaciones caducadas bloquean admisión. Reintentos requieren evidencia ABSENT y se bloquean conservadoramente si hay APPLIED o UNKNOWN en la misma generación; resolver esos historiales contradictorios necesita un protocolo de reconciliación concluyente, no editar recibos.
- El read_set contiene conjuntos completos, no máximos de IDs ni solo row_version. Eso detecta inserciones/borrados y cambios sin versión. Su coste crece con la historia; no hay benchmark ni SLA de escalabilidad.
- La publicación revalida seguridad/capacidad y no ejecuta un segundo solver. Se confía en el núcleo del control plane para el orden y la puntuación; no es un endpoint para aceptar planes arbitrarios de un worker.
- Captures/manifests conservan trazabilidad. No existe retención/borrado automático ni adopción automática de un PUBLISHED legado ajeno al head D3.

## Validación

```bash
bash testing/D3/run-postgres-tests.sh
python3 scripts/summarize-d3-postgres.py > docs/validation/D3-OPTIMIZATION-results.json
```

Requiere Docker. La ejecución crea PostgreSQL desechable sin puertos publicados y usa Maven/Java 21. Por defecto puede descargar imágenes/dependencias; `D3_OFFLINE=1` exige imágenes/caché presentes y usa una red interna sin salida. `D3_MAVEN_CACHE` selecciona la caché local; `D3_PG_IMAGE` y `D3_MAVEN_IMAGE` permiten fijar imágenes. El runner elimina solo sus contenedores/red y los `target` de los tres módulos de pruebas para evitar informes obsoletos.

La suite añade bases d3_case/d3_upgrade desechables y ejecuta también el núcleo y la batería histórica D2 sobre sus bases V1–V11. Nunca apuntar las pruebas a una instalación con datos reales. Evidencia, cobertura y diferencias de alcance: [I2](../docs/design/D3-I2-PERSISTENCE.md).

## Despacho protegido I3

[Contrato I3](../docs/design/D3-I3-DISPATCH.md): `DispatchStore.claim` admite únicamente una asignación TENTATIVE del plan vigente y confirma mapping+CLAIM+vía+trazabilidad juntos. `DispatchStore.execute` mantiene el intento y su fencing para START/HEARTBEAT/CALLBACK/VERIFY y recuperación D2. La nueva propuesta V13 está aislada en `migrations-d3-dispatch-proposed/`; no se modifica V12.

```java
var dispatch = new DispatchStore();
var claimed = dispatch.claim(connection, commandId, planId, operationId, resourceId, workerId);
dispatch.execute(connection, startCommandId, claimed, "START", java.util.Map.of());
```

Son entradas del control plane, no endpoints públicos para workers. No arrancan un servicio ni ejecutan procesos externos. El runner actual prueba I2 sobre V12 e I3 sobre V13; la ejecución I3 está registrada en `docs/validation/D3-I3-results.json`. El informe I2 se conserva como evidencia histórica.

## Coordinación invocable

[PlanningCoordinator](../docs/design/D3-COORDINATOR.md) integra recepción durable, agrupación, barrido, observación, cómputo sin locks y publicación con dos recálculos máximos. `tick` es una llamada explícita; no inicia threads ni servidores. V14 está en `migrations-d3-coordinator-proposed/` y tiene una plantilla de pruebas separada. El rol del coordinador no recibe permisos de dispatcher ni publicación directa.

El exportador actual escribe `docs/validation/D3-OPTIMIZATION-results.json`; conserva los informes históricos I2/I3/coordinación. Alojamiento y temporizadores activos, workers reales y despliegue siguen pendientes.

La [revisión integrada](../docs/design/D3-REVIEW.md) añade V15 y pruebas completas sobre esa versión, sin modificar las plantillas históricas.
