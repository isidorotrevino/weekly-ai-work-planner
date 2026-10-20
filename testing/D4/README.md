# D4 — preparación del laboratorio Docker

Estado a 2026-10-20: **vertical sintética integrada; D4 abierto para revisión**.
[Contrato I4](../../docs/design/D4-I4-LAB.md) describe la conexión D2/HTTPS,
supervisor, receptor durable y verificador independiente. Los resultados efectivos
se registran en [evidencia I4](../../docs/validation/D4-I4-results.json).
A08/A09 autorizan la [continuación parcial I5](../../docs/design/D4-I5-CHECKPOINT-LAB.md)
en el laboratorio: un checkpoint, dos pasos y una cuenta. No se promueven migraciones.
[I6](../../docs/design/D4-I6-LONG-RUNNING-LAB.md) añade ejecución prolongada y
checkpoint cooperativo bajo A10/A11: nueve escenarios y 283 comprobaciones,
[evidencia propia](../../docs/validation/D4-I6-results.json). D4 permanece abierto.
[I7](../../docs/design/D4-I7-POLLING-LAB.md) añade polling normal y retirada
verificada: S01–S12, 367 comprobaciones y [evidencia propia](../../docs/validation/D4-I7-results.json).
A12 elige pausa completa tras CHECKPOINT_READY y rearme explícito. S13 prueba
esta decisión (51 comprobaciones) en una [campaña separada](../../docs/validation/D4-I7-A12-results.json);
el informe I7 anterior conserva su alcance e incertidumbres de aquella ejecución.

[I8.1](../../docs/design/D4-I8-COMPONENTS.md) prepara componentes para cadena lineal,
liquidación por cuenta y verificadores de archivos/Git/restauración bajo A13–A15.
Ese primer corte no ampliaba las rutas SQL/HTTPS ni Compose. Su evidencia
y cobertura son [independientes](../../docs/validation/D4-I8-COMPONENTS-results.json).

[I8.2](../../docs/design/D4-I8-INTEGRATION.md) integra SQL/HTTPS multicuentas y
checkpoints lineales sobre V24 propuesta. `bash testing/D4/run-multicount-lab.sh`
ejecuta S14 y regresiones S05/S13; [evidencia separada](../../docs/validation/D4-I8-INTEGRATION-results.json).
D4 sigue abierto.

[Revisión de fronteras V24 y corrección V25](../../docs/design/D4-V25-BOUNDARY-LAB.md):
V24 se conserva; la campaña adicional S15/S14/S13 prueba ingreso inválido y regresión
sobre V25 propuesta. A16 aprueba el esquema cerrado y bloquea nuevas admisiones
de intenciones antiguas con campos adicionales, conservando sus hechos.
[Evidencia final A16](../../docs/validation/D4-V25-CLOSED-SCHEMA-results.json);
[validación provisional anterior](../../docs/validation/D4-V24-BOUNDARY-results.json).

## Ejecutar el laboratorio nuevo

```bash
bash testing/D4/run-lab.sh
```

Necesita Docker/Compose, Python 3, OpenSSL, imágenes locales fijadas por digest y
la caché Maven de I2/I3 en `work/d4/m2`. Build offline y sin red; cuatro proyectos
Compose sucesivos con redes internas, cero puertos y credenciales solo sintéticas.
El runner recoge evidencia y elimina únicamente contenedores/redes/volúmenes de
cada proyecto. Guarda datos privados en `work/d4/<campaña>/`; la imagen local
construida se conserva. Fallos de bootstrap o aserción producen salida no cero.
[Configuración](compose.yaml), [build](build-lab.sh), [driver](lab-scenarios.py) y
[generación de identidades](lab-config.py) son archivos ejecutables existentes.

Los escenarios son éxito, competencia, callback perdido tras APPLIED y proceso
superviviente a lease real de 60 s. El último debe **bloquear** conservando
compromiso/exclusión, incluso después de demostrar parada. No es un fallo esperado
oculto ni aceptación del resultado del worker. Solo se ejecutan fixtures confiables.

Para la campaña ampliada S01–S05: `bash testing/D4/run-checkpoint-lab.sh`.
[Resultados I5](../../docs/validation/D4-I5-results.json) incluyen regresión separada.
Para S01–S09: `bash testing/D4/run-long-running-lab.sh`. Los runners Compose actuales
crean V25; los resultados históricos I4/I5/I6 conservan sus versiones originales.
Para S01–S12: `bash testing/D4/run-polling-lab.sh`.
Para S13 (checkpoint dentro del bucle y rearme A12):
`bash testing/D4/run-checkpoint-polling-lab.sh`.

## Baterías separadas

| Entrada | Cobertura |
|---|---|
| `testing/D3/run-postgres-tests.sh` | Bibliotecas/SQL históricas D3 y regresión D2; no levanta estos servicios |
| `run-delivery-tests.sh` | I1, persistencia V16/upgrade V15→V16 |
| `run-transport-tests.sh` | I2, HTTPS/mTLS V17 y upgrade V16→V17; clientes de prueba |
| `run-process-tests.sh` | I3, supervisor/grants/diario como componentes |
| `D4_OFFLINE=1 D4_TESTS=LabBridgeTest bash testing/D4/run-delivery-tests.sh` | Upgrade V17→V18 con lease activa y autoridad de evidencia |
| `run-checkpoint-lab.sh` | S01–S05, checkpoint parcial aprobado A/A; bootstrap actual V25 |
| `run-long-running-lab.sh` | S01–S09; renovación y cooperación, bootstrap actual V25 |
| `run-checkpoint-polling-lab.sh` | S13; bootstrap actual V25; pausa de checkpoint, sellado/autorización y rearme explícito del sufijo |
| `python3 -m unittest discover -s testing/D4 -p test_verifiers.py -v` | Componentes locales de archivos/Git/restauración I8.1; sin aceptación SQL/HTTPS |
| `D4_OFFLINE=1 D4_TESTS=CheckpointAccountingTest bash testing/D4/run-delivery-tests.sh` | Cálculo v2 puro y composición con receptor durable, no liquidación SQL multicuentas |
| `run-v24-boundary-lab.sh` | V25 propuesta: S15/S14/S13; pruebas nuevas inválidas y regresiones |
| `D4_OFFLINE=1 D4_TESTS=V25BoundaryTest bash testing/D4/run-delivery-tests.sh` | Upgrade V24→V25, tipos, plazo durante liquidación, permisos e historia |
| `run-multicount-lab.sh` | S14/S05/S13; bootstrap actual V25, evidencia I8.2 original V24; cadena de dos checkpoints, dos cuentas y regresión v1 |
| `D4_OFFLINE=1 D4_TESTS=MultiCheckpointStoreTest bash testing/D4/run-delivery-tests.sh` | V24, cadena/contabilidad/CAS/negativos; upgrade vivo V23→V24 |
| `run-polling-lab.sh` | I7, S01–S12; bootstrap actual V25, evidencia I7 original V23 |
| `D4_OFFLINE=1 D4_TESTS=PollingStoreTest bash testing/D4/run-delivery-tests.sh` | V22→V23, retirada normal y del sucesor verificado, ownership y bloqueos |
| `D4_OFFLINE=1 D4_TESTS=LongRunningStoreTest bash testing/D4/run-delivery-tests.sh` | Upgrade vivo V21→V22, señal propia, permisos y expiración |
| `D4_OFFLINE=1 D4_TESTS=CheckpointStoreTest bash testing/D4/run-delivery-tests.sh` | V21, upgrade V18→V21 y guardas de checkpoint/admisión |
| `run-lab.sh` | I4, procesos y servicios reales en Compose por HTTPS, verificaciones y fallos completos |

Las decisiones [A01–A19](../../docs/design/D4-DECISIONS.md) siguen vigentes.
[Continuidad con efectos parciales](../../docs/design/D4-CHECKPOINT-CONTINUATION.md)
con TOP_UP al vector original se concreta en I5 tras aprobación A/A. La fixture v1 conserva sus límites; I8.2 añade multicuentas/checkpoints lineales
acotados, sin RECONCILING.
UNKNOWN/contradicciones siguen bloqueados salvo la resolución concluyente y acotada
aprobada en I9; APPLIED incompatible y diario perdido conservan bloqueo.

## Especificación de preparación original

Las fases y listas siguientes documentan la especificación inicial. La cobertura
real y lo pendiente se delimitan en I4/I5/I6/I7 y sus informes; la matriz
amplia no equivale a afirmar que todos sus casos estén ejecutados en Compose.

## Fase 0: base ejecutable existente

La batería [D3](../D3/README.md) ya ejecuta Java/Maven y PostgreSQL en contenedores desechables, sin puertos publicados. Desde la raíz del repositorio, cuando se quiera repetir la línea base:

```bash
bash testing/D3/run-postgres-tests.sh
python3 scripts/summarize-d3-postgres.py > work/d4-baseline-summary.json
```

Ejecutar el exportador solo si la batería termina correctamente. El informe nuevo es local; no sobrescribir los resultados históricos D3. La batería limpia los directorios `target` de sus tres módulos; evitar ejecutarla simultáneamente con otro build de esos módulos. No necesita Java/Maven/PostgreSQL instalados en el host; sí Bash, Docker accesible y Python 3 para resumir.

Las imágenes predeterminadas existentes son `postgres:16-bookworm` y `maven:3.9-eclipse-temurin-21`. Son tags, no digests inmutables. Registrar el digest realmente utilizado antes de reclamar reproducción exacta. No inventar hashes ni actualizar versiones como efecto lateral de D4.

El runner acepta `D3_PG_IMAGE`, `D3_MAVEN_IMAGE`, `D3_MAVEN_CACHE` y `D3_OFFLINE`. Tras disponer de imágenes y dependencias en caché, el modo aislado se ejecuta así:

```bash
D3_OFFLINE=1 bash testing/D3/run-postgres-tests.sh
```

En ese modo usa red Docker interna, `--pull never` y Maven offline. Una imagen/dependencia ausente debe fallar claramente. El modo ordinario permite obtener dependencias; no equivale a una prueba de aislamiento de Internet. Conservar la separación entre bootstrap con descargas y ejecución offline.

La base D3 usa PostgreSQL en tmpfs y autenticación `trust` exclusivamente dentro de su red de auditoría desechable. Esa configuración no es el modelo de autenticación del nuevo laboratorio. El runner guarda logs en `work/d3-postgres/`, marca éxito al completar ambas baterías y elimina solo sus contenedores/red. No montar clústeres reales ni ejecutar limpiezas globales.

## Fase 1: topología propuesta

Preparar un proyecto Compose con nombre único por ejecución y dos workers que compitan por las mismas cuentas físicas sintéticas cuando el fixture lo indique. Los dos workers no crean dos saldos. El objetivo es una operación elegible completa y después sus fallos, con procesos reales y efectos simulados.

| Servicio propuesto | Responsabilidad | Acceso permitido |
|---|---|---|
| `db` | PostgreSQL de laboratorio con volumen propio | Red de persistencia; sin puerto al host ni acceso desde workers |
| `migrate` | Aplicar ubicaciones/versiones expresamente elegidas y fixtures | Credencial propietaria efímera; termina antes del arranque funcional |
| `control-plane` | Adaptador HTTPS Java/Spring Boot sobre bibliotecas D2/D3, sin reimplementar sus guardas | Red de persistencia con rol restringido y red de workers |
| `worker-a`, `worker-b` | Polling HTTPS, supervisor y subprocesos sintéticos | Red de workers y receptor sintético; sin SQL ni privilegios de verificación |
| `effect-receiver` | Receptor sintético con deduplicación y fencing atómicos, historial APPLIED/ABSENT/UNKNOWN | Red de efectos y canal de consulta del verificador; su historial sobrevive al reinicio probado |
| `verifier` | Contrastar proceso, artefactos y efectos; aportar evidencia autorizada | Consulta al receptor y acceso mínimo al contrato de evidencia del control plane |
| `test-driver` | Preparar escenarios, provocar fallos y verificar invariantes | APIs de prueba y credenciales sintéticas separadas; orquestación Docker desde el host |

Separar redes de persistencia, workers y efectos. El control plane y el verificador tendrán solo las conexiones necesarias. El driver puede consultar la base mediante un rol de auditoría limitado para comprobar hechos, pero el camino funcional del worker pasa siempre por HTTPS. No permitir al driver fabricar el resultado cuya veracidad pretende probar.

La CA y credenciales efímeras dependen de la decisión de identidad de D4. Probar expiración, revocación y suplantación además del caso válido. Definir roles LOGIN de laboratorio y permisos mínimos; no convertir los roles NOLOGIN históricos ni el usuario auditor propietario en identidad de runtime. Los secretos se generan localmente, se montan solo donde corresponda y no se incluyen en Git ni en el informe público.

Para el primer corte no hacen falta UI Angular, proveedores comerciales, claves API, Kafka ni un scheduler residente de producción. Un driver puede invocar ticks explícitos y controlar los tiempos de prueba sin modificar el reloj del host. Si se inyecta un reloj, su interfaz es de test y la campaña también debe comprobar expiración real en PostgreSQL.

## Aislamiento y ciclo de vida

- Contenedores de aplicación sin root, filesystem de imagen de solo lectura cuando sea compatible, capabilities eliminadas, `no-new-privileges`, límites de CPU/memoria/PIDs y almacenamiento temporal acotado. Documentar las excepciones concretas de PostgreSQL y herramientas de build.
- Workspaces sintéticos por ejecución, sin montar el home, repositorios personales, agentes SSH, credenciales de proveedores ni el socket Docker. Los worktrees separan código, no son un sandbox de seguridad. El primer laboratorio solo ejecuta fixtures confiables; no acredita aislamiento suficiente para código hostil.
- Construir imágenes antes de la campaña; ejecutar en redes internas sin salida externa. Publicar cero puertos por defecto. Si se necesita depuración, usar un perfil explícito limitado a loopback y documentarlo.
- Base y diario de efectos en volúmenes exclusivos del proyecto para probar reinicios. Distinguir reinicio conservando datos de pérdida deliberada de volumen. La falta del diario de efectos produce UNKNOWN, nunca ABSENT inferido.
- `healthcheck`, esperas acotadas y terminación con timeout. Recoger evidencia antes de limpiar. Un fallo de arranque/imagen/fixture es fallo de infraestructura, no prueba funcional superada.
- El host provoca `stop`/`kill` y cortes de red solo sobre recursos del proyecto identificado. No usar `docker system prune`, red del host o contenedores privilegiados. La limpieza debe ser idempotente, preservar otros proyectos y detectar procesos/volúmenes huérfanos propios.

## Destinos de la preparación y archivos actuales

Los destinos se concretan ahora en `compose.yaml`, `images/Dockerfile`, `run-lab.sh`,
`lab-config.py`, `lab-scenarios.py`, `lab/` y V18. Las fixtures viven en `LabBootstrap`
y los contextos se congelan en SQL; no hay carpetas vacías de fixtures/escenarios.
La tabla siguiente conserva los nombres propuestos al preparar el corte:

| Destino propuesto | Contenido esperado |
|---|---|
| `testing/D4/compose.yaml` | Servicios, redes internas, healthchecks, volúmenes y perfiles de debug |
| `testing/D4/images/` | Builds reproducibles y manifiesto con digests reales y dependencias |
| `testing/D4/run-lab.sh` | Preflight, nombre único, bootstrap/ejecución separados, timeouts, evidencia y cleanup propios |
| `testing/D4/fixtures/` | Contextos, cuentas, workers, dependencias y fallos completamente sintéticos |
| `testing/D4/scenarios/` | Aserciones end-to-end y orquestación de fallos |
| `migrations-d4-proposed/` | Solo si D4 necesita SQL aditivo; ubicación nueva con upgrade explícito desde V15 |
| `docs/validation/D4-*-results.json` | Resúmenes saneados de campañas efectivamente ejecutadas |

Los logs, certificados, volúmenes exportados y artefactos brutos deben quedar bajo `work/d4/<run-id>/`, ya excluido de publicación, con permisos locales apropiados. No ofrecer `docker compose up` como procedimiento disponible hasta crear, revisar y validar la configuración. Incluir después instrucciones precisas de build, ejecución offline, inspección y limpieza selectiva.

## Matriz mínima de validación

Cada prueba debe observar tanto respuesta HTTP como estados, reservas, intentos, generaciones y efectos reales del fixture. Correlacionar comando/plan/operación/intento/worker/recurso/generación sin exponer secretos. Los casos de tiempo usan límites D2/D3 reales o un reloj de test documentado, sin esperas ilimitadas.

| Escenario | Resultado que debe demostrarse |
|---|---|
| Camino feliz | Solo plan vigente; CLAIM, START, proceso, callback, verificación y resultado; una reserva y consumo trazable |
| Competencia entre workers y planes | Sin doble ejecución autorizada; misma cuenta física y exclusiones compartidas; propuestas TENTATIVE no ejecutables por sí solas |
| Redelivery y respuesta perdida | Mismo command ID y contenido recupera el resultado sin duplicar efecto/reserva; otro contenido con ese ID se rechaza |
| Worker/identidad inválidos | Certificado/token inválido, worker ajeno o payload que cambia identidad rechazados; worker sin acceso SQL ni autoaceptación |
| Contexto/capacidad/política | Hash alterado, capacidad insuficiente o aprobación caducada impiden START/renovación; distinguir callback factual válido de nueva autorización |
| Lease y proceso superviviente | Expirar lease pasa a reconciliación; proceso antiguo que sigue vivo no permite liberar exclusión; generación obsoleta rechazada |
| Efecto aplicado y callback perdido | Receptor acredita APPLIED; recuperar sin repetir el efecto lógico; comprobar clave idempotente y fencing en el receptor |
| Ausencia, desconocimiento y contradicción | ABSENT autoritativo permite solo la transición prevista; UNKNOWN/contradicción mantienen compromiso; no borrar evidencia anterior |
| Reinicio de servicios | Reinicio de worker/control plane/receptor preservando diario recupera identidad y resultado; pérdida del diario queda visible como UNKNOWN |
| Checkpoint/preempción | Checkpoint truncado/falso rechazado; parada probada antes de liberar; no interrumpible conserva compromiso; CANCELLED no se reanuda automáticamente |
| Reset y capacidad | Sin rollover, préstamo ni liberación ficticios; START/renovación que no cubre 60 s bloqueado; INCIDENT agotado no consume PLANNED |
| Dependencias y prioridad | HARD sin evidencia sigue bloqueado, incluso urgente; herencia solo por camino bloqueante y excepción P4 prevista; exclusión PAUSED/ARCHIVED |
| Outbox y coordinación | Entrega duplicada, reinicio y reapertura crítica conservan efectos idempotentes y prioridad; tick invocable sin asumir daemon de producción |
| Aislamiento y limpieza | Worker no alcanza DB ni Internet; sin montajes sensibles; fallo de campaña limpia solo recursos propios y conserva evidencia saneable |

Empezar por camino feliz, competencia, callback perdido y proceso superviviente. Extender a checkpoints cuando su contrato se haya decidido; marcar los casos todavía no implementados como pendientes, sin contarlos como superados. Para receptores externos sin fencing, el resultado esperado puede ser bloqueo conservador: el simulador no acredita garantías de un proveedor real.

## Evidencia y aceptación del primer corte

Registrar fecha UTC, versión Docker/Compose, revisión o hashes del árbol sucio, digests utilizados, versiones Java/PostgreSQL/Flyway, configuración de red, seed, escenarios y duración. Diferenciar build, infraestructura, aserciones funcionales y regresión. Los tiempos son observaciones, no SLA nuevo.

La regresión histórica debe conservar sus plantillas V11/V12/V13/V14/V15 y ejecutarse cuando cambien contratos o integración relevante. El harness D4 usará una plantilla propia con sus ubicaciones explícitas; no añadir migraciones D4 al descubrimiento D2. Conservar informes de cierre: comprobar sus hashes es distinto de afirmar una nueva ejecución sobre código cambiado.

El primer corte estará listo para revisión cuando otro entorno con caché preparada pueda ejecutar la campaña aislada, los fallos produzcan los bloqueos conservadores esperados, se puedan rastrear reservas/efectos y el cleanup sea selectivo. Presentar resultados y limitaciones al usuario. Un laboratorio verde no cierra D4, no valida cuotas comerciales y no autoriza despliegue.

[I9: recuperación v1/v2 y resolución monotónica](../../docs/design/D4-I9-RECONCILIATION-LAB.md), A17–A19. Runner: `bash testing/D4/run-reconciliation-lab.sh`; no altera las migraciones anteriores ni cierra D4.

[I10.1, ausencia sin progreso](../../docs/design/D4-I10-ABSENCE-LAB.md), A20.
Runner: `bash testing/D4/run-absence-lab.sh` (S20/S21 y regresiones S16/S19), V27
propuesta, build offline y proyectos desechables. A21/A22 están aprobadas, pero
las revisiones y cuarentena siguen sin habilitarse: `sql/review-core.sql` es un
borrador excluido de migraciones y bootstrap. D4 permanece abierto.

[Evidencia I10.1](../../docs/validation/D4-I10-ABSENCE-results.json): 226 pruebas
D4/locales y 169 comprobaciones Compose positivas; no vuelve a contar las suites
D2/D3 históricas. La cuarentena/reapertura no forma parte de V27.
