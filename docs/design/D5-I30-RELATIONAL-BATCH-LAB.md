# D5 I30 — laboratorio de relaciones y lotes sintéticos

Fecha: 2026-10-22. Implementa [I29](D5-I29-RELATIONAL-BATCH-DESIGN.md) y
[RB01–RB34](D5-I29-RELATIONAL-BATCH-REVIEW.md), solo GI28/GI29 como modelo en
memoria. [Resultados propios](../validation/D5-I30-results.md).
**D5 global y G01–G07 abiertos; el hito aceptado I1–I20 conserva su perímetro.**

English: isolated volatile single-project atomic batch fixture. Explicit typed
entities and additive relationships, full-state CAS, local-edit guards and whole
HARD-graph validation precede one publication of data, provenance and receipt.
No SQL/D2 conformance claim, durable restart, providers, activation or deployment.

## Autoridad y ejecución

D5-A71: el usuario aprueba I29 y autoriza implementar/validar RB01–RB34 con fixtures
en memoria, conservando A68–A70, sin SQL, HTTP, efectos persistentes D2, activación,
promoción, despliegue ni D6. I29 publicado y verificado en `main`:
`ca7efeae73bb39db64f217ee18e46823f52d2961`.

Desde la raíz, Python 3 con biblioteca estándar:

```bash
python3 -m testing.D5.demo_relational_batch
python3 -m unittest discover -s testing/D5 -p test_relational_batch.py -v
python3 -m testing.D5.run_batch_lab
```

La demo crea un requisito, una épica y una tarea de fixture, declara sus dos
vínculos, revisa fuente y lote por separado y simula pérdida de respuesta tras
confirmación. Replay recupera el mismo recibo y deja una sola generación aplicada.
Imprime estados/contadores sin texto fuente/IDs de destinos; pierde todo estado
al salir. No recibe archivos, URL, `.env` o credenciales de servicios.

La suite nueva usa memoria y dos hilos propios; no crea carpetas de datos o hijos
de proceso. El runner completo reejecuta I24/I26/I28 y Python anterior. **La
regresión I26** mantiene requisitos Linux/fsync/flock, raíces temporales marcadas,
hijos propios y SIGKILL controlado. Esos reinicios no son persistencia del lote
I30. El runner emite JSON saneado a stdout; no guarda un informe por sí mismo.

## Fuente, identidad y proyección

[`batch_fixture.py`](../../source_ingest/batch_fixture.py) añade un protocolo
cerrado `d5.relational-batch-fixture.v1`, modo SYNTHETIC_ONLY, con IDs explícitos de
proyecto/documento, revisión, elementos y declaraciones relacionales. No modifica
parsers/perfiles históricos, `offline.py`, `plane_fixture.py` o el almacén I26.

Los bytes exactos se conservan con SHA-256 y base64 en la inspección privada de
captura. JSON duplicado, shape/tipo/UUID inválido, perfil/modo desconocido o límite
excedido bloquea sin reparación. Cada elemento y declaración conserva su localizador
`/elements/N` o `/relations/N`; claims Status/Verified y texto de instrucciones
permanecen datos. No se infieren relaciones, épicas o requisitos de narrativa.

Los destinos se suministran aparte: source_key, UUID y clave interna. El código no
genera identidad por título, nombre o posición. Una correspondencia fija proyecto,
documento, perfil, source_key y tipo; UUID es único, y clave de destino es única por
proyecto/tipo, conforme a los espacios de claves D2. No se permite renombrar,
convertir tipo o adoptar un UUID existente sin correspondencia propia. Los endpoints
pueden venir del lote o del registro aplicado, con identidad/tipo/proyecto exactos.

REQUIREMENT proyecta título/descripción y permanece DRAFT; EPIC título y BACKLOG;
TASK título/descripción y BACKLOG. Description de EPIC se conserva en evidencia
sin crear columna. Campos ajenos registrados se preservan. El conjunto actual de
entidades no representa una base D2 completa ni admite trabajo operativo.

## Relaciones, guardas y procedencia

| Relación | Comportamiento |
|---|---|
| EPIC_REQUIREMENT | Unión explícita de épica y requisito del mismo proyecto; adiciones sin sustitución |
| TASK_EPIC | Nulo→épica explícita; repetición exacta no-op; cambiar a otra o retirar queda bloqueado |
| TASK_DEPENDENCY | Extremos TASK distintos, mismo proyecto, kind HARD/SOFT/MOCKABLE/OPTIONAL explícito; kind de un par existente no cambia |

Se valida la coherencia de **todas** las relaciones finales, incluidas preexistentes
fuera del paquete. El grafo HARD completo debe ser acíclico; se comprueban ciclos
que combinan aristas existentes y varias adiciones. Un self-loop bloquea para
cualquier kind. Ciclos SOFT/MOCKABLE/OPTIONAL no se promueven a HARD. No se modelan
capabilities, dependencias cross-project, retirada de vínculos o adopción.

Cada participante existente se compara con su base aplicada completa: entidad,
versión, campos ajenos registrados y relaciones incidentes. Cualquier divergencia
local bloquea todo el lote, incluso si ya existía al preparar. Después de preparar,
un cambio de datos del proyecto invalida el ticket por generación/hash, aunque
restaure el texto después. No hay mezcla de campos, reaparición o resolución local
I14/I18/I20 implícitas.

Guardas de estado y trabajo se evalúan en entidades y tareas relacionadas con
requisitos/épicas. `has_work` representa cualquier asociación actual o histórica
en una fixture negativa; no se insertan operaciones, reservas ni planificaciones
para probarlo. Esta entrada controlada no acredita consultas/guardas SQL reales.
Los métodos `fixture_edit_entity` y `fixture_add_relation` son controles del
harness confiable, no comandos ejecutables desde contenido de fuente.

Una entidad creada tiene row_version 0 y cabeza D5 1. Cambios de contenido y
asignación de épica en el mismo lote incrementan row_version una sola vez. No-op
conserva row_version. Cada participante/endpoints aprobado avanza una vez su
cabeza de procedencia; el endpoint de solo lectura conserva la proyección anterior
del origen. Repetir un vínculo mantiene una sola identidad y añade evidencia con
todos los localizadores de declaración. No se inventa row_version para uniones o
dependencias D2. Ausencia de fila/declaración nunca borra/cierra datos.

## Publicación atómica y revisiones

`BatchLab` conserva una raíz como bytes canónicos/hash inmutables. Incluye datos,
bases, correspondencias, procedencia, revisiones y recibos. Las capturas y
manifiestos privados son catálogos de bytes inmutables verificados por hash.

`root_revision` avanza con cualquier publicación; `data_generation` solo con datos,
guardas o aplicación. SOURCE y BATCH tienen versiones CAS propias. Preparar fija
datos/hash, SOURCE y un plan completo, sin su propio hash o una aprobación futura.
Aprobar BATCH valida esos datos y emite versión/ticket: no invalida su propio
manifiesto. Revisiones independientes pueden coexistir sobre la misma generación.

Apply reconstruye la copia candidata y la contrasta con el plan sellado. Bajo un
lock corto revalida datos y revisiones exigidas, conserva el catálogo actual de
revisiones y cambia una sola vez el puntero de raíz. Entidades, relaciones, bases,
procedencia y recibo se publican juntos. No hay prefijos confirmados ni recibo
independiente de los efectos. Revocar/reemplazar SOURCE/BATCH antes del CAS bloquea.

Dos candidatos aprobados parten de una generación común y compiten mediante
barrera de prueba antes del CAS. Solo uno publica; el otro queda en conflicto sin
creaciones/vínculos parciales. Otro paquete no obtiene rebase de datos automático.
Un fallo antes de publicación conserva raíz previa; pérdida de respuesta después
permite lectura/replay por command_id/request_hash en la misma memoria. Cambiar
request de un command_id confirmado bloquea. Replay antiguo no rebobina una cabeza
posterior ni exige que la revisión histórica siga vigente: recupera un hecho,
no una autorización actual para volver a aplicar.

## Límites comprobados y alcance de la evidencia

Un proyecto/snapshot por paquete; 32 elementos, 64 declaraciones, fuente ≤2 MiB,
manifiesto ≤4 MiB, textos ≤8.192 caracteres. Estado de fixture: 128 entidades,
256 relaciones y 128 comandos confirmados. Se alcanzan realmente esos límites de
conteo en pruebas; el siguiente se rechaza sin truncar. El límite del manifiesto
se ejercita con 22 elementos UTF-8 multibyte cuyos bytes fuente caben en 2 MiB,
pero cuyo plan completo supera 4 MiB. No se usa un presupuesto reducido para
atribuir esas pruebas de capacidad a límites completos; tampoco son benchmarks.

38 tests nuevos cubren las 34 filas, con 157 regresiones: 195 distintos sin fallos,
errores u omisiones. Los dos hilos nuevos terminan. Las regresiones verifican sus
ocho hilos I28 terminados, 33 raíces I26 eliminadas y cero hijos propios vivos.
No se reejecutan SQL/D2/D3/D4 ni se suman sus cifras históricas.

Este modelo no prueba durabilidad/reinicio del batch, pérdida de energía, permisos,
HTTP, conformance SQL/D2/V30 o aislamiento frente a un caller Python hostil. Hooks
de fallo y mutaciones privadas son controles confiables. `source_artifact`,
`manifest` e `inspect` contienen texto/bytes completos y son privados; resúmenes,
recibos y runner evitan texto crudo. Los catálogos/estado se pierden al salir.

Con GI28/GI29 se llega a **27 de 35 criterios S con evidencia acotada**. Quedan
ocho S y siete R pendientes; GI30 real y GI38/GI39/GI40 integrados no se consideran
completos. No se cierra ninguna brecha G01–G07 ni se amplía el hito aceptado.
Sin proveedores reales, promoción, despliegue ni D6.
