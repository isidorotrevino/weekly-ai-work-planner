# D5 I29 — contrato de relaciones y lotes sintéticos

Fecha: 2026-10-22. **PREPARADO PARA REVISIÓN; sin implementación nueva.**
Cobertura propuesta: GI28/GI29 de [I23](D5-I23-GLOBAL-INTEGRATION-DESIGN.md).
[Matriz RB01–RB34](D5-I29-RELATIONAL-BATCH-REVIEW.md) ·
[Comprobaciones documentales](../validation/D5-I29-design-review.json).
El [hito aceptado I1–I20](D5-LOCAL-SYNTHETIC-approved.md) permanece separado;
**G01–G07 y D5 global siguen abiertos**.

English: proposed single-project synthetic in-memory atomic batch of explicit
requirements, epics, tasks and additive relationships. Full-state CAS, source
and effect reviews, local-edit guards and whole-graph HARD cycle checks precede
one publication of entities, mappings, provenance and receipt. No SQL, persistent
D2 writes, provider access, activation, deployment or global acceptance.

## Decisiones expresas y perímetro

| ID | Decisión | Consecuencia |
|---|---|---|
| A68 | Priorizar relaciones y lotes GI28–GI29 | Contrato y matriz antes de implementar |
| A69 | Requisito↔épica, tarea→épica y dependencias entre tareas del mismo proyecto | Capabilities y dependencias entre proyectos quedan para otro corte |
| A70 | Creaciones y actualizaciones de contenido, con relaciones aditivas; cualquier divergencia local bloquea todo el lote | Sin borrados, retirada de vínculos ni resolución automática de texto local |

A68–A70 fijan decisiones; no aprueban todavía este contrato completo ni autorizan
su implementación. Propuesta: módulo/harness Python nuevo, biblioteca estándar,
memoria volátil y concurrencia en hilos con barreras propias. No modificar los
parsers, perfiles, dobles ni entradas históricas I1–I28. No SQL, HTTP, SDK/CLI,
Docker, filesystem de datos, procesos hijos o proveedores/credenciales reales.
Las regresiones anteriores conservarán sus targets y requisitos separados.

El primer corte es un proyecto y un snapshot de fuente por paquete. Reutiliza
conceptualmente la whitelist tipada I23/I24, pero no extiende silenciosamente
sus decodificadores. Las declaraciones de relaciones serán un protocolo nuevo
**de fixture sintética**, no un formato Gentle-AI, un perfil de registro Markdown
nuevo, una promoción de migración o una afirmación de grooming real suficiente.

## Fuente y correspondencias explícitas

Proponer un envelope cerrado `d5.relational-batch-fixture.v1`, modo SYNTHETIC_ONLY,
project_id/document_id UUID y revisión de fixture explícitos, elementos tipados y
declaraciones de relación. Conservar los bytes exactos y SHA-256; localizadores
por elemento/declaración dentro del snapshot. JSON con claves duplicadas, campos
extra, IDs ambiguos, tipos desconocidos, referencia inválida o exceso de tamaño
bloquea el snapshot/paquete completo; no reparar ni truncar datos silenciosamente.

Los elementos incluyen source_key estable, tipo REQUIREMENT/EPIC/TASK y campos
explícitos. Los destinos se eligen aparte, con UUID y clave interna registrados;
no adoptar por título, posición, similitud, ni generar una épica/requisito ausente.
Identidad de correspondencia: proyecto + documento + perfil de fixture versionado
+ source_key + tipo. Una identidad no recibe dos UUID y un UUID/clave de destino
no pertenece a dos identidades. Tipo, proyecto e identidad no cambian en PATCH.
Una versión de fuente o hash distinto no se convierte en el anterior por fecha.

Para referencias se exige correspondencia existente explícita o una creación
incluida en el mismo lote. El registro resuelve al UUID/clave/tipo/proyecto exactos;
no buscar en tareas no vinculadas ni inferir adopción. Entidades ya vinculadas
pueden ser endpoints de solo lectura, con snapshot/versión fijados en el paquete.
No se permite materializar una correspondencia nueva sobre una entidad existente:
la adopción I16 permanece otro flujo; este corte no la generaliza a otros tipos.

Cada declaración de relación fija tipo, extremos y localizador de origen. No
interpretar texto de Item/Objective/Status/Verified, narrativa o anotaciones como
instrucciones relacionales. La ausencia de una declaración posterior no elimina
una entidad, correspondencia, procedencia o relación. Un archivo completo no
implica sincronización destructiva ni aceptación automática de sus filas.

## Entidades y relaciones admitidas

| Tipo/relación | Proyección/guardas | Fuera de alcance |
|---|---|---|
| REQUIREMENT | key/title/description, CREATE DRAFT; UPDATE conserva estado DRAFT | Aprobar o promover workflow por contenido de fuente |
| EPIC | key/title, CREATE/UPDATE BACKLOG; description se conserva solo como evidencia | Añadir columna description o inventar contenedor por narrativa |
| TASK | key/title/description, CREATE/UPDATE BACKLOG; guardas sin trabajo | Activar, planificar, asignar operadores o crear operaciones |
| EPIC_REQUIREMENT | Unión explícita épica/requisito del mismo proyecto, equivalente conceptual a epic_requirements | Vínculo directo tarea→requisito inventado o proyecto ajeno |
| TASK_EPIC | Asignación explícita: epic_id nulo→UUID aprobado; mismo UUID ya ligado es no-op con evidencia | Cambiar a otra épica, quitarla o crear varias épicas por tarea |
| TASK_DEPENDENCY | Predecessor/successor TASK distintos, mismo proyecto, tipo HARD/SOFT/MOCKABLE/OPTIONAL explícito | Capabilities, dependencias cross-project o cambio de kind existente |

Las claves internas se fijan al crear y no se renombran en este corte. Para
relaciones de conjuntos, repetir exactamente el vínculo conserva uno solo y
permite añadir procedencia; cambiar los extremos es otro vínculo sujeto a guardas,
nunca sustituye el anterior. Un par de tareas ya ligado con otro kind bloquea;
no se degrada HARD ni se elimina/reemplaza una dependencia existente.

Se comprueba el grafo completo resultante del proyecto: dependencias existentes
más todas las adiciones del lote. HARD debe ser acíclico. Un ciclo que solo se
cierra por la unión de varias adiciones también bloquea, aunque cada arista
parezca válida aislada. SOFT/MOCKABLE/OPTIONAL mantienen su semántica D2 y sus
ciclos no se convierten en HARD. El self-loop se rechaza para cualquier kind.
No basta con revisar solo el subgrafo del paquete ni con ordenar sus filas.

Esta comprobación parcial de dominio no acredita el grafo de capabilities o de
proyectos D2: ambos quedan fuera por A69. Las reglas se contrastan con
[V1](../../migrations/V1__core_domain.sql),
[V6](../../migrations-proposed/V6__movement_and_epic_ownership_draft.sql),
[V9](../../migrations-proposed/V9__execution_guards_contract_draft.sql),
[V10](../../migrations-proposed/V10__provenance_and_delivery_contract_draft.sql) y
[D2 aprobado](D2.9-approved.md), preservados; no se ejecutan migraciones.

## Edición local, procedencia y revisiones

Para UPDATE o uso relacional de un endpoint existente se fija su snapshot completo,
versión y base D5 aplicada. Se exige correspondencia propia, entidad en DRAFT o
BACKLOG según tipo y sin trabajo asociado en las guardas de fixture, incluidas
asociaciones históricas. En requisitos/épicas se incluye la guarda de trabajo de
las tareas relacionadas en el estado del proyecto. Son flags/snapshots controlados
del harness: no se insertarán operaciones o reservas para probarlos.

El snapshot completo actual debe coincidir con la última base aplicada D5,
incluidos versión, campos ajenos registrados y relaciones administradas. Si existe
divergencia local, incluso anterior a preparar, bloquear el lote completo. También se compara el snapshot completo al
aplicar para detectar cualquier cambio posterior, aunque afecte a un campo ajeno
a la proyección. No se sobrescriben campos ajenos ni se decide un ganador por fecha.
La resolución de texto I14/I18/I20 y la reaparición no se ejecutan como parte del
batch. Un paquete nuevo tampoco convierte una edición local en base de origen.

Capturar, revisar la fuente, preparar el lote y aprobar su efecto son actos
separados. La revisión SOURCE confirma hash/identidad/perfil/grado y versión del
snapshot. Preparar fija esa versión y las correspondencias antes/después, snapshots
de endpoints, proyecciones, relaciones, bases del grafo y guardas. La revisión
BATCH propia cubre el manifiesto completo; no admite selección de campos sueltos.
Revocar/reemplazar SOURCE o BATCH invalida un paquete preparado. La revisión de
publicación Git, la aceptación local A52 o un ACCEPT de otro flujo no las sustituyen.

Cada entidad/vínculo materializado conserva procedencia exacta de fuente,
source_key/declaración/localizador y manifiesto/revisión aplicada. Para épicas,
texto no proyectado sigue en evidencia. No se fabrican revisiones/ACCEPT I5, recibos
SQL I8 o tareas operativas; los registros de este modelo tienen schema propio.

## Atomicidad, CAS y replay

El almacén mantiene una raíz inmutable que incorpora datos, revisiones y recibos.
Se distinguen `root_revision` (toda publicación) y `data_generation` (solo cambios
de entidades, correspondencias, relaciones, bases o guardas del proyecto), ambas
monótonas. Una revisión SOURCE/BATCH cambia root_revision y su versión propia,
pero no data_generation. Una edición de datos del harness avanza ambas aunque
restaure después el texto (ABA). El manifiesto fija data_generation y hash de datos,
snapshots/versiones y revisión SOURCE; ninguna fecha decide vigencia.

1. Capturar/preparar/revisar no publica efectos. El paquete declara cada creación,
   actualización, vínculo y no-op con evidencia; no existen efectos implícitos.
2. Apply construye una copia candidata y comprueba todas las identidades, campos,
   guardas, referencias y grafo final. El orden del JSON no concede autoridad ni
   permite publicar entidades antes de resolver una relación posterior inválida.
3. Bajo un lock corto, revalidar generación/hash de datos, revisiones exigidas y
   snapshots exactos. Cualquier cambio de datos del proyecto devuelve conflicto;
   no hay rebase de datos ni incorporación silenciosa de cambios de otro lote.
   Revisiones de otros paquetes pueden coexistir: conservar el catálogo actual
   tras revalidar las revisiones exactas requeridas por el ticket.
4. Publicar en una única sustitución de raíz entidades, correspondencias, vínculos,
   bases D5, procedencia y recibo. Un fallo anterior deja la raíz previa completa;
   no hay confirmaciones por fila ni diario de efectos confirmado por separado.
5. Una pérdida de respuesta posterior se resuelve por command_id/request_hash en
   la raíz alcanzable. Replay devuelve el recibo histórico sin aplicar de nuevo,
   sin recuperar snapshots viejos ni rebobinar una cabeza posterior.

El request hash fija manifiesto y versión de aprobación; el mismo command_id con
otro request bloquea. Dos comandos/lotes sobre la misma generación no confirman
ambos: solo uno publica, el otro devuelve conflicto sin prefijo. Repetir exactamente
el comando confirmado devuelve su recibo aunque luego cambie la fuente/revisión;
eso es lectura histórica, no aplicación vigente ni aceptación de nuevo contenido.

Preparar fija la generación/hash de datos y SOURCE; aprobar BATCH produce una
versión/ticket de aprobación sobre esos mismos datos si siguen vigentes. El
manifiesto no se reescribe para incluir su propio hash o aprobación futura. El
request fija manifiesto + versión BATCH + generación aprobada. Cambiar una revisión
exigida o cualquier dato posterior invalida el ticket, salvo replay confirmado.
Aprobar otro paquete no modifica esos datos ni esas revisiones: dos paquetes pueden
competir sobre la misma data_generation, pero solo uno la avanza al publicar.
La raíz nueva conserva el catálogo de revisiones validado y sustituye los datos y
recibo juntos. Así se evita un ciclo de hashes y que aprobar invalide su paquete.

Una creación empieza row_version 0 y versión de correspondencia aplicada 1;
UPDATE de contenido/epic_id avanza row_version una vez por entidad afectada,
aunque varias declaraciones la toquen. Un no-op puro conserva row_version. Una
entidad participante materializada/actualizada o usada como endpoint aprobado
avanza su cabeza de procedencia D5 una vez por lote, incluso si solo añade
evidencia; los snapshots/guardas fijados impiden que ese avance adopte una edición
local. Un endpoint de solo lectura conserva su base/proyección anterior del origen;
la referencia relacional no fabrica una nueva fila de contenido para ese endpoint.
Las dependencias y uniones tienen identidad de relación y evidencia propias,
sin inventar row_version en tablas D2 donde no existe.

## Límites propuestos y evidencia esperada

Un proyecto, un snapshot, ≤32 elementos y ≤64 declaraciones por paquete; bytes de
fuente ≤2 MiB, manifiesto canónico ≤4 MiB y textos ≤8.192 caracteres por campo.
Estado de fixture ≤128 entidades, ≤256 relaciones y ≤128 comandos confirmados.
Fuera de límites se bloquea antes de publicar, sin truncar ni reiniciar presupuesto
cambiando command_id. Son límites de laboratorio, no límites SQL o de proveedor.
No sleeps, polling, daemon, red o llamadas externas durante locks.

Se propone un modelo nuevo en memoria con fallos controlados antes de publicación
y tras publicación/antes de respuesta, más hilos propios que compiten desde una
misma generación preparada. No se probará reinicio de proceso, disco/energía,
outbox durable, SQL o equivalencia completa del dominio D2/V30. Perder la memoria
pierde prueba de aplicación; otro almacén no hereda recibos ni autoridad.

El incremento de implementación, si se autoriza, deberá mapear RB01–RB34 a tests
realmente ejecutados y registrar inputs/entorno, concurrencia, cero activación y
limpieza de recursos propios. Las regresiones I24/I26/I28 se contabilizarán aparte;
sus procesos/temporales de I26 no prueban persistencia del batch nuevo. No cambiar
historia/manifiestos ni atribuirse campañas SQL por comprobar sus hashes.

GI28/GI29 recibirían evidencia acotada de modelo; GI30 real, GI38/GI39/GI40
integrados y todas las brechas G01–G07 seguirían pendientes. La puerta propuesta
es aprobar I29 y autorizar implementar/validar RB01–RB34 exclusivamente con
fixtures en memoria. Alternativa: aprobar solo diseño o pedir ajustes. Ninguna
publicación equivale a implementación, aceptación global, promoción o despliegue.
