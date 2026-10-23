# D5 I35 — contrato relacional durable R para revisión

Fecha: **2026-10-23**, Europe/Madrid. **PREPARED_FOR_REVIEW; no implementado.**
[Matriz DR01–DR40](D5-I35-DURABLE-RELATIONAL-REVIEW.md) ·
[Revisión de alcance](D5-I35-NEXT-CUT-SCOPE.md) ·
[Comprobaciones documentales](../validation/D5-I35-design-review.json).

English: proposed durable relational fixture path R, distinct from real-evidence
criteria also labelled R. Atomic local batches and individually reviewed TASK
projections; no distributed atomicity, legacy volatile-state restoration, real
providers, activation or global D5 closure. Design requires approval before code.

## Autoridad y perímetro

El usuario eligió **A — Diseñar la integración relacional durable R (UI25/UI34;
GI38/GI39), con TASK derivada de un lote y proyección revisada**. Autoriza preparar
este contrato y matriz; no aprueba el resultado ni autoriza implementación o campaña.
P0 conserva I32, handoff, I33, I34 y propuestas posteriores sin publicar.
Base local: `6a9932acec47f422249c94bc55bf83dc9a38b80b`.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20 aceptado conservan contratos, targets,
SQL y evidencia. **D5 global y G01–G07 abiertos**. Los siete criterios reales
GI06/12/18/24/30/36/42 siguen pendientes; R relacional no es esa etiqueta R.
GI33/GI34/GI40 exigen inventario, regresiones y auditoría propios del nuevo corte.

Propuesta de implementación posterior: Python estándar, Linux/filesystem local,
estado nuevo R-CLIENT y R-REMOTE de fixture, procesos spawn propios y reloj lógico.
Un proyecto/documento por run_id y un snapshot por lote. Relaciones A69/A70 de
[I29](D5-I29-RELATIONAL-BATCH-DESIGN.md) se conservan: requisito↔épica, tarea→épica
y dependencias explícitas entre tareas del mismo proyecto; adiciones sin borrar,
retirar, reasignar épica o convertir kind. Cualquier divergencia local bloquea todo
el lote. Sin SQL, HTTP, SDK/CLI/proveedores/credenciales reales, consumo/reservas,
operaciones, activación, promoción, despliegue, servicios permanentes o D6.

## Arquitectura y compatibilidad comprobada

| Componente actual | Decisión propuesta |
|---|---|
| I30 `BatchLab`, memoria volátil | Referencia de comportamiento mediante API pública; no restauración de `_head`, catálogos privados o replay de ACCEPT |
| I30 envelope `d5.relational-batch-fixture.v1` | Admitir sus bytes y validación pública `validate_source`; conservar límites/semántica y evidenciar parser/contrato/hash exactos |
| I34 `durable_store.Store` | Reutilizar kernel público de commits con reducers/genesis nuevos, sin modificar su código o esquemas existentes |
| I34 `Client` TASK Markdown | No importar datos/revisiones/mappings de T ni añadir perfil JSON a I32; T queda intacto y su regresión separada |
| I34 `Remote` y su manifiesto | No reutilizar su esquema de PROJECTION con evaluación Markdown ficticia. Nuevo protocolo R-REMOTE explícito para TASK del lote |

La raíz superior propia del harness contiene R-CLIENT, R-REMOTE, marcador y sentinel
hermano; no usa I26 para capturar JSON ni como outbox. La entrada R es un artefacto
**de fixture tipada**, no una captura Drive ni formato Gentle-AI. No aumenta la
cobertura de exportaciones Docs o perfiles de extracción I32. Se importan bytes
íntegros explícitos, nunca estado interno o recibos originales I30.

R-CLIENT tiene namespace de estado `d5.durable-relational-client.v1`; R-REMOTE
`d5.durable-relational-remote.v1`. Comparten el contenedor durable I34 de marca,
HEAD y commits, pero config incluye `path=RELATIONAL_FIXTURE` y namespaces exactos.
Abrir T como R o R como T debe fallar por esquema/config; no migrar automáticamente
ni adoptar almacenes por path/store_id parecido. Si el kernel público no permite
cumplir el contrato sin cambios, bloquear y revisar antes de modificar I34.

No se proponen observaciones de cuota ni EVALUATION R: no hay proveedor/ejecución
autorizable en este doble. SOURCE/BATCH/PROJECTION no equivalen a evaluación I32,
elegibilidad D3 o reserva. El manifiesto R no fabrica una referencia EVALUATION.
La prueba de cuotas T permanece evidencia distinta y no se presenta enlazada a R.

## Esquemas, identidades y estado durable

JSON UTF-8 canónico I34 para commits/manifiestos, claves cerradas, sin floats/NaN,
claves duplicadas, campos desconocidos o comandos ejecutables. Los **bytes de fuente
I30 se conservan sin recanonicalizarlos**: su SHA-256 es de bytes originales; su
JSON se valida con el decoder público I30 que rechaza duplicados. El hash del plan
y manifiesto R usa la codificación canónica separada. UUID/hash/tipos/versiones
estrictos; bool no sustituye entero. Campos ausentes/ambiguos bloquean sin reparar.

| Registro | Contenido e invariantes |
|---|---|
| Config | run/store/role en contenedor; proyecto/documento/instancia/workspace/proyecto remoto, schema R y límites inmutables en génesis |
| Captura R | source_id=SHA-256 de bytes, base64 exacto, perfil I30, revisión declarada, diagnóstico/localizadores; artefacto privado, sin aceptación implícita |
| Referencia seleccionada | source_id o null, selección CAS y generación monótona. Capturar no selecciona; seleccionar/restaurar A→B→A avanza generación, no aprueba |
| Datos R | entities, mappings, relations, bases, entity_provenance, relation_provenance; misma semántica de identidad que I30; data_generation monótona |
| Revisiones | SOURCE por captura **y generación de selección**, BATCH por manifiesto, PROJECTION por TASK/manifiesto; versiones CAS propias, ACCEPT/REJECT/REVOKE y reason_code; nunca inferidas entre etapas |
| Manifiesto BATCH | fuente/selección/revisión exactas, destinos explícitos, data_generation/hash y snapshots completos, plan candidato íntegro, locators y proyecciones permitidas |
| Recibo BATCH | command/request/manifest/fuente/revisiones, data_generation antes/después, hash de datos, created/participants/relaciones; historia sin autoridad operativa |
| Selección de TASK | batch command/request y recibo exactos, lista ordenada sin duplicados de UUID TASK participantes, generación CAS; elegir no aprueba enviar |
| Manifiesto PROJECTION R | selección/generación, recibo BATCH, TASK/snapshot/generación/hash de datos y contexto relacional, SOURCE/BATCH revisiones, binding/capabilities/base remota/payload; sin evaluación Markdown |
| Ledger R | comandos, send_id por manifiesto, tickets/intentos/queries/pruebas/conflictos y márgenes pendientes; sin operaciones o intentos D2 |

Identidad de mapping: proyecto + documento + perfil I30 + source_key + tipo.
UUID y claves internas se suministran aparte. Una identidad→un UUID, un UUID→una
identidad; claves únicas por proyecto/tipo. Tipo/proyecto/clave no cambian en UPDATE;
no adopción por nombre/posición/UUID existente sin mapping propio ni conversión T↔R.

## Preparación, revisiones y aplicación del lote

1. Capturar valida bytes/shape/modo/proyecto/documento y límites; no ejecuta claims
   Status/Verified. Selección explícita fija la fuente actual y generación.
2. SOURCE revisa esa captura/perfil/selección y fija la generación en un contexto
   SOURCE propio. Reseleccionar los mismos bytes requiere versión SOURCE nueva;
   una aprobación de la generación anterior no sirve. Cambiar selección/revocar/reemplazar
   revisión invalida manifiestos no aplicados y proyecciones no emitidas que la fijan.
   Otro archivo capturado, sin seleccionarlo, no reemplaza la referencia por fecha.
3. Preparar BATCH exige selección/SOURCE vigentes, destinos completos y snapshots
   de datos/base/guardas. Planner público nuevo construye candidato sin efectos.
   No invocar `_candidate` o mutar privados I30. Contrastar casos con `BatchLab`
   público, incluidas guardas/relaciones y no-ops, sin declarar equivalencia completa.
4. BATCH ACCEPT verifica datos/selección/SOURCE aún vigentes, fija su propia versión
   sobre el plan entero. No aprobar filas/campos separados ni copiar SOURCE ACCEPT.
   Aceptar o cambiar una revisión ajena no altera data_generation ni se incorpora
   como si fuera dato; conservar el catálogo actual al confirmar.
5. Apply reconstruye candidato, contrasta plan/manifiesto y revalida bajo el lock
   durable datos/hash, snapshots, selección y versiones exactas SOURCE/BATCH.
   Publica juntos entidades, relaciones, mappings, bases, toda procedencia y recibo.
   No efecto por fila, lote parcial, publicación separada del recibo o rebase automático.

Proyección local: REQUIREMENT key/title/description DRAFT, EPIC key/title BACKLOG
(description solo evidencia), TASK key/title/description BACKLOG. Description
nullable/empty en REQUIREMENT/TASK conserva exactamente null/"" de I30; no sustituir
por título ni convertir silenciosamente null. No columnas inventadas o workflow.

Relaciones admitidas y guardas I29/I30: EPIC_REQUIREMENT, TASK_EPIC null→UUID o
repetición exacta, TASK_DEPENDENCY HARD/SOFT/MOCKABLE/OPTIONAL. Extremos explícitos
existentes con mapping propio o creados en el lote, mismo proyecto/tipo. Self-loop
rechazado; mismo par con otro kind bloquea. Comprobar todo el grafo final: HARD
acíclico, incluidos ciclos que cierran varias adiciones y aristas ya existentes.
No promover ciclos SOFT/MOCKABLE/OPTIONAL a HARD ni incluir capabilities/cross-project.

Snapshot/base de cada participante existente incluye entidad, versión, campos
ajenos y relaciones incidentes. Divergencia previa o durante preparación invalida
el lote entero, aunque afecte solo a relaciones o a endpoint de lectura. Guardas
de trabajo actual/histórico y estado se extienden de requisito/épica a tareas
relacionadas; `has_work` es flag negativo, no crear operaciones para probarlo.
Ausencia de elemento/declaración no borra ni cierra. Adopción/resolución local y
reaparición aprobadas en otros flujos no se ejecutan implícitamente aquí.

CREATE row_version 0; cambio de contenido/epic_id avanza una vez por entidad;
no-op puro conserva row_version. Cada participante/endpoints aprobado avanza una
vez su cabeza de procedencia y mapping, conservando source_base anterior si solo
participa como endpoint de lectura. Relaciones tienen identidad/evidencia propias,
sin row_version SQL inventada. Data_generation avanza una vez por lote aplicado,
incluso si solo añade procedencia; preserva invalidación de paquetes preparados.

## Selección y proyección individual desde recibo aplicado

Solo TASK participante del **recibo aplicado** elegido puede seleccionarse; UUID
arbitrario, requisito, épica o entidad no participante bloquean. El recibo se busca
por command_id/request_hash en la raíz durable, con fuente/manifiesto/revisión y
snapshot exactos. Un hash de manifiesto sin recibo no acredita aplicación. No crear
una TASK nueva por copiar un título de I30 a T, ni reutilizar su aprobación BATCH.

La selección completa contiene hasta 16 TASK y su generación. Preparar cada
PROJECTION R fija esa selección, recibo BATCH y generación/hash de **todos los
datos del proyecto**, incluyendo relaciones/bases/procedencia, más TASK/guardas y
revisiones SOURCE/BATCH vigentes. Es una política conservadora: cualquier cambio
local del proyecto, aunque sea otro vínculo y el payload TASK quede igual, invalida
todos esos paquetes no emitidos. ABA o lote no-op nuevo no revive generación vieja.
No reducir silenciosamente la guarda a title/description o a entidades del paquete.

Revisión PROJECTION separada por TASK y payload/base exactos. Preparar/aceptar no
envía; aceptar una TASK no aprueba las demás seleccionadas. Solo se proyectan
name=title y description exacta de TASK; null/empty están explícitamente admitidos
en el **nuevo doble R**. Nunca requisito/épica/relación/epic_id/Status/Verified/workflow,
ni contador de ejecución. Campos remotos ajenos se conservan.

Binding R fija proyecto/TASK/instancia/workspace/proyecto remoto; clave de creación
estable incluye namespace R y esas identidades, no texto/fecha/paquete/comando.
Otro store/namespace T o tarea ajena no se adopta por coincidir UUID/nombre. CREATE
exige unicidad atómica del doble; UPDATE destino ya ligado y base remota/version/hash
exactos. El nuevo esquema `d5.relational-projection-fixture.v1` es rechazado por
la API T antigua; no hacerla aceptar el esquema rellenando campos ficticios.

El efecto BATCH local y cada TASK remota son transacciones distintas. Si se confirma
TASK A y TASK B queda UNKNOWN/rechazada, conservar A y B por separado; lote local
sigue aplicado, sin rollback ni borrado compensatorio. Resumen del grupo: vectores
de estado/validez por TASK; no éxito global por una TASK confirmada ni exactamente
una operación distribuida. No hay dispatch automático del conjunto o retry por fila.

## Protocolo durable, tickets y concurrencia R

Reutilizar el kernel de I34 sin cambios: validación completa de cadena/estado y
transición pura cerrada; flock exclusivo por almacén; objeto fsync/publicación sin
reemplazo/fsync objects; HEAD temporal fsync/replace/fsync directorio. Error antes
no promueve huérfanos; después de replace incierto → COMMIT_UNKNOWN y handle
RECOVERY_REQUIRED. Abrir no repara, migra, elige padre válido o crea génesis en raíz
incompleta. Reabrir/fsync confirma solo la cabeza visible íntegra. Mismo comando/
request da recibo histórico; otro request bloquea sin retroceder datos/generaciones.

R-CLIENT emite ticket UNKNOWN durable antes de llamar a R-REMOTE y consume intento.
Revalida selección/fuente/SOURCE/BATCH/PROJECTION, datos completos y capacidades;
libera el lock antes de otra llamada de almacén. Revocar antes bloquea; después no
deshace un efecto ya en vuelo. Resultado histórico puede quedar STALE respecto a
lote/selección/revisiones actuales. Ni otro proceso ni restart obtiene permiso de
reenviar un ticket desde el ledger; sin daemon, reasignación por tiempo o rearme.

R-REMOTE es filesystem independiente con API local síncrona, ejecutable en hijos
spawn de prueba; sin servidor/red. Schema R propio y capability descriptor de
fixture versionado para unicidad, CAS, lookup y `settle_or_close`. Confirma efecto,
índice único, ticket/prueba atómicamente. Prueba liga run/store/ticket/request/hash
R/creation_key/remote_id/version/payload, con identidad exacta y código cerrado.
Lookup vacío mantiene UNKNOWN. Cierre atómico del ticket ausente conserva tombstone
que impide llegada tardía; execute frente a cierre produce efecto probado **o**
cierre probado. Ninguna capacidad es atribución a Plane real ni al viejo I30.

Conciliar es acción explícita: consume consulta durable antes de salir, registra
prueba/resultado por CAS de ledger_version y conserva historia/conflictos. Conflicto
de identidad queda persistente; otro paquete o dato más reciente no lo borra.
NO_EFFECT/CLOSED_NO_EFFECT concluyente permite retry explícito, ticket nuevo, mismo
paquete/clave/payload y presupuesto original, bajo guardas actuales. Rechazo de
precondición/clave no permite retry del paquete anterior; exige base/revisión nuevas.
UNKNOWN del binding bloquea nuevos envíos aunque haya cambiado el lote de origen.
Nuevo lote local sí puede aplicarse si cumple sus guardas: no cancela tickets remotos
anteriores, que quedan conciliables e históricos/STALE; ningún recibo autoriza
restaurar el payload viejo. No resolver UNKNOWN por GET vacío, fecha o ausencia.

Reloj lógico confiable persistido, solo avance CAS explícito; no renovar tick por
reinicio o mtime. Requerimientos de rate-limit/retry_after de fixture se expresan
como tick mínimo válido; desconocido/ausente bloquea. Sin capacidades comerciales,
cuotas, consumo/reservas o garantías de frescura real.

## Límites y pruebas exigidas

Por run_id: un proyecto/documento, un escenario R, ≤32 elementos/64 declaraciones
por lote, fuente ≤2 MiB, texto ≤8.192 caracteres, manifiesto BATCH ≤4 MiB, proyección
≤1 MiB; ≤128 entidades/256 relaciones; ≤16 TASK seleccionadas/bindings/destinos
remotos; ≤128 capturas/manifiestos/revisiones y ≤128 comandos CLIENT, tres intentos
por manifiesto de proyección y seis consultas por envío. REMOTE ≤384 tickets, sujeto
a límites inferiores del kernel: commit ≤32 MiB, ≤256 commits y almacén ≤256 MiB,
prueba ≤64 KiB. Se aplica siempre el límite más restrictivo, sin truncar ni prometer
que todos los máximos caben simultáneamente. Presupuesto de comandos incluye
revisiones/preparaciones/queries/resultados, no solo lotes aplicados.

Usar márgenes persistidos para todos los resultados pendientes: slots de recibo,
historia y bytes; cualquier mutación los preserva antes de emitir intento/consulta.
No son reservas D3. Cerrar los almacenes propios y limpiar solo raíces identificadas
por marca/IDs/inodos; rechazar symlinks/propiedad incoherente y reportar residuos,
no borrarlos por heurística. Mantener sentinel hermano; terminar todos hijos/hilos
propios y contar regresiones aparte. No inspeccionar/parar/borrar dev/run_data/D4.

Matriz DR parametriza commits BATCH, selección, PROJECTION, ISSUE, QUERY/RESULT y
CREATE/UPDATE/cierre REMOTE con before_object/after_object/before_replace/after_head
y fsync incierto. Fallos R-CLIENT dejan R-REMOTE intacto; lector independiente de
archivos compara hashes/cadena/HEAD/datos/recibos y resultados antes/después. Cada
combinación realmente ejecutada queda registrada, sin inflar tests por filas o
subcasos. Validar límites reducidos con etiqueta explícita; no presentarlos como
capacidad máxima o benchmark. Regresiones T/I30 y anteriores efectivamente ejecutadas
se separan de SQL/D1–D4 históricos comprobados solo por hash.

## Aprobación pendiente

Puerta propuesta: aprobar I35 y autorizar implementar/validar R sintético durable
DR01–DR40, UI25/UI34 y auditoría propia GI33/GI34/GI40, con kernel I34 y laboratorios
históricos intactos, módulos/harness nuevos, filesystem/hijos propios y regresiones
Python separadas. Alternativa: aprobar solo diseño o pedir ajustes. Publicación de
SHA exige decisión independiente; no crear cierre D5 ni ampliar A52.

Este documento y sus hashes no son ejecución ni prueba de recuperación. No se
concluye GI38/GI39 completos por sumar I30+I34; la futura campaña R deberá acreditar
su unión y exclusiones. Siete criterios reales, Docs y G01–G07 siguen pendientes.
Sin pérdida de energía/disco fallido/NFS/Windows, aislamiento de caller Python
hostil, attestation del host o exactly-once externo. Sin proveedores/credenciales
reales, consumo/reservas, activación, promoción, despliegue ni D6.
