# D5 I36 — laboratorio relacional durable R

Fecha: **2026-10-23**, Europe/Madrid. Implementación del
[contrato I35](D5-I35-DURABLE-RELATIONAL-DESIGN.md) y
[matriz DR01–DR40](D5-I35-DURABLE-RELATIONAL-REVIEW.md), UI25/UI34 y auditoría
GI33/GI34/GI40 del alcance autorizado.
[Resultados](../validation/D5-I36-results.md) · [JSON](../validation/D5-I36-results.json).
**D5 global y G01–G07 abiertos; A52/I1–I20 sin ampliación.**

English: new synthetic durable relational client/remote authority. Whole local
batches commit atomically; selected TASKs have separate reviewed projections and
outcomes. Explicit restart/reconciliation, unchanged I34 kernel and legacy labs.
No distributed atomicity, real providers, SQL/D2 effects or execution authority.

## Autoridad y publicación

El usuario eligió A para diseñar R y después **A: aprobar y autorizar implementación/
validación R, DR01–DR40 y UI25/UI34, con regresiones Python separadas**. Esta decisión
aprueba el contrato I35 local `aee8b212ab766cc89483013045ebb3bad8ebf168` y el alcance
sintético descrito. I35 mantiene su estado histórico previo PREPARED_FOR_REVIEW;
este documento registra la autorización e implementación posteriores.

P0 sigue vigente: I32, handoff, I33–I36 no están autorizados para publicar. Una futura
autorización de SHA limitado no permite push de todo HEAD. D1–D4 cerrados y el hito
local D5-LOCAL-SYNTHETIC-I1-I20 aceptado conservan alcance/targets/hashes. Sin proveedores/
credenciales reales, consumo/reservas, operaciones, activación, promoción, despliegue
ni D6. R relacional no equivale a los siete criterios R que requieren evidencia real.

## Uso reproducible

Python estándar y Linux con filesystem local fsync/rename/flock, desde la raíz:

```bash
python3 -m testing.D5.demo_durable_relational
python3 -m unittest testing.D5.test_durable_relational -v
python3 -m testing.D5.run_relational_durable_lab
```

La demo confirma un lote de requisito/épica/dos TASK y relaciones en R-CLIENT.
Proyecta la primera TASK y deja la segunda UNKNOWN. Un proceso separado confirma
el efecto de la segunda en R-REMOTE; abrir otro cliente no lo infiere. Conciliar
explícitamente en otro proceso acredita el ticket. El lote local permanece aplicado
con un vector de resultados, sin rollback remoto o éxito distribuido ficticio.
Salida saneada, cero solicitudes reales, sin argumentos de URL/path/.env/corpus.
El runner imprime JSON a stdout; no guarda informe por sí mismo.

## Componentes nuevos y reutilización

[`relational_planner.py`](../../source_ingest/relational_planner.py) es un planificador
público puro adaptado del algoritmo de fixture GPL de I30 de este repositorio. No
invoca `_candidate`, restaura `_head` o importa atributos privados. Conserva guardas,
grafo, base, mappings y procedencia, con límites explícitos del nuevo estado. Usa
validación/constructores públicos I30; equivalencia observada solo en los casos
comparados, no conformance completo SQL/D2.

[`durable_relational_fixture.py`](../../source_ingest/durable_relational_fixture.py)
implementa reducers CLIENT/REMOTE con namespaces R nuevos. Reutiliza sin cambios
`durable_store.Store` de I34. El Remote R reutiliza únicamente la fachada pública
local de llamadas de I34 sobre su Store/reducer R: no adopta el schema de TASK T ni
inventa EVALUATION Markdown. Descripción TASK null/empty se conserva exactamente.

[`relational_support.py`](../../testing/D5/relational_support.py) crea un run_id con
un escenario/proyecto/documento y almacenes R-CLIENT/R-REMOTE propios. No utiliza
I26 para JSON/Drive, ni transforma el envelope I30 en perfil I32. Los inspect,
manifiestos y capturas contienen bytes/texto íntegros y son privados.

El kernel, parser y laboratorios históricos I1–I34 permanecen intactos. I30 se usa
por API pública como referencia de datos/guardas/errores. Los hashes de manifiesto
son distintos por schema; la comparación verifica las referencias en cada catálogo
y normaliza únicamente ese identificador para comparar los demás datos/evidencias.
No presenta las revisiones/recibos R como los originales I30.

## Lote, revisión y proyección

Captura conserva bytes originales y hash; capturar no selecciona ni acepta.
SOURCE liga captura y generación de selección propia; A→B→A no revive aprobación.
BATCH fija fuente/SOURCE, targets explícitos, datos/hash/generación y plan completo.
Aplicar revalida y confirma entidades, relaciones, mappings, bases, procedencia y
recibo en una sola raíz durable. Sin prefijo, rebase o aplicación por fila.

REQUIREMENT DRAFT, EPIC/TASK BACKLOG. Description de EPIC queda solo en evidencia;
TASK/REQUIREMENT nullable/empty se conservan. Vínculos aditivos del mismo proyecto;
HARD acíclico sobre grafo completo. No retirar vínculos, reasignar épica/kind,
adoptar por UUID/nombre o inventar estructura. Cualquier divergencia local de base,
versión/campo ajeno/relación de participante o endpoint bloquea todo el lote. Guardas
de estado y trabajo actual/histórico son flags de fixture, sin operaciones creadas.

Selección de TASK exige command_id/request_hash de recibo aplicado y participantes
TASK exactos. Un manifiesto sin recibo no acredita aplicación. Seleccionar no envía.
Cada PROJECTION exige revisión propia y fija selección, recibo BATCH, SOURCE/BATCH,
snapshot TASK, contexto completo del proyecto y base/capacidades remotas. Cambio
local/relacional o lote no-op nuevo invalida generación aunque el payload coincida.
Solo name/description de TASK llegan al doble; no requisito/épica/vínculos/epic_id,
workflow o claims de ejecución. Confirmar una TASK no aprueba otra.

Cada envío tiene ticket UNKNOWN durable antes de salir de CLIENT, sin locks de dos
almacenes anidados. REMOTE confirma efecto/índice único/ticket/prueba juntos. Lookup
vacío no prueba no efecto. El cierre atómico de ticket es capacidad **solo de fixture**:
confirma CLOSED_NO_EFFECT y frena llegada tardía, o devuelve efecto ya acreditado.
Reabrir no envía/consulta/cierra/reintenta automáticamente.

UNKNOWN/CONFLICT del binding bloquea nuevos envíos aunque cambie el lote; nuevo
lote local puede aplicar si cumple guardas, conservando incertidumbre previa. La
conciliación del ticket viejo no restaura texto ni convierte el recibo en autoridad
actual. Si confirma una creación mientras otro CREATE esperaba, este último queda
STALE_DESTINATION: preparar UPDATE nuevo con base/revisión vigentes. Precondición
remota rechazada exige paquete nuevo; no retry ciego del paquete viejo.

## Durabilidad, recursos y límites

I34 kernel comprueba marca/role/schema/config/cadena/transition, flock exclusivo,
objetos SHA-256 fsync y HEAD temporal fsync/replace/fsync de directorio. Antes de
HEAD no confirma; tras replace incierto COMMIT_UNKNOWN, handle bloqueado hasta
reapertura validada/fsync. Sin promover huérfanos, elegir padre, reparar, migrar T↔R
u obtener autoridad de un almacén incompleto. Replay exacto es histórico y no rebobina.

El harness usa API local síncrona del doble con estado filesystem separado y
procesos spawn nuevos para crash/reinicio/concurrencia. No servidor o aislamiento
de seguridad entre roles. Se registran failpoints/exitcodes/HEAD antes-después y
oráculos independientes de archivos; no usar excepciones o fechas como prueba de
rollback. El reloj lógico persiste y solo avanza explícitamente por CAS del harness;
reiniciar no crea frescura real ni renueva un presupuesto de retry.

Límites I35 y el más restrictivo del kernel: catálogos/estado/bytes/historia, tres
intentos y seis consultas. Margen lógico persistido para todos los resultados
pendientes, sin reservas de cuota/capacidad D3. Ensayos de límites con presupuestos
reducidos se identifican como tales; no prueba de todos los máximos simultáneos o
benchmark. Fuente >2 MiB rechazada en la frontera de captura antes de parsear.

Limpieza solo de raíces propias, con marca/IDs/inodos y sentinel hermano. Symlinks/
propiedad incoherente bloquean borrado y se reportan. Todos hijos/hilos propios
deben terminar; raíces/procesos de regresión T e I26 se contabilizan separados.
No inspección/parada/borrado de dev/run_data/D4 o evidencia ajena.

## Alcance de resultados

La evidencia R documenta su unión real de fixture durable en UI25/UI34, sin deducirla
de sumar I30 volátil e I34 T. No implica completar GI38/GI39 o D5 global sin revisión
del alcance restante. GI33/GI34/GI40 reciben auditoría de esta campaña autorizada,
no de instancias/proveedores reales. Docs y los siete criterios reales siguen
pendientes; no se crea D5-approved/D5-CLOSURE ni se amplía A52.

SQL/D2/D3/D4 no se reejecutan. Sin prueba de energía/disco fallido/NFS/Windows,
caller Python hostil, attestation del host o exactly-once externo. Hashes/escaneo
no son garantía exhaustiva de secretos/defectos. Publicación requiere SHA autorizado
independiente y continúa bloqueada por P0.
