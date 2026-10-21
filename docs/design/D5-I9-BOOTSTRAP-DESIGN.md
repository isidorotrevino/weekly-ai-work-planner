# D5 I9 — contrato propuesto de carga inicial

Fecha: 2026-10-21. **Diseño para revisión; sin implementación ni SQL nuevo.**
Base publicada: `81d54db`, [laboratorio I8](D5-I8-SYNTHETIC-TASK-LAB.md).
[Matriz de aceptación y gate siguiente](D5-I9-BOOTSTRAP-REVIEW.md).
D5 abierto; D1–D4 cerrados; D6 pendiente.

## Decisiones expresas

| ID | Elección del usuario | Consecuencia |
|---|---|---|
| D5-A20 | Diseñar bootstrap inicial y matriz, para revisión antes de implementar SQL nuevo | Este corte solo añade documentación; no crea bases, roles o tareas |
| D5-A21 | Lista explícita de IDs con correspondencia registrada, sin destino materializado y versión D5 cero | No importar todo el documento; no adoptar, reiniciar o reutilizar correspondencias con efectos previos |
| D5-A22 | Revisión específica del manifiesto completo de bootstrap, con fila íntegra, snapshot, destino y proyección | No fabricar ACCEPT I5 ni comparación contra una captura vacía |

Las reglas siguientes concretan una propuesta que requiere revisión antes de una
implementación. A20–A22 no autorizan nuevo SQL o una campaña de creación de tareas.
No se reserva un número de migración. Se conservan V1–V33, parsers/perfiles,
adaptadores, runners, contratos y evidencias anteriores como entradas históricas.

## Problema y alcance

I8 requiere un cambio de origen entre dos observaciones reales. Una fila UNCHANGED
no genera propuesta y una comparación consigo misma no permite importar un
registro inicial. Fabricar una captura vacía para convertir todas las filas en
ADDED ocultaría esa diferencia. El bootstrap propuesto toma una sola observación
real y expresa una acción propia: `CREATE_INITIAL_BACKLOG`.

La unidad sigue siendo `(project_id, document_id, source_key)` exacta, con intención
I8 registrada que fija perfil, política `d5.task-projection.v1`, task UUID y task_key
explícitos. El proyecto y el documento ya existen. Ruta, candidato, título o fecha
no sustituyen la identidad. El perfil es `task-register.v1` o
`task-register-compat.v1`; no se cambia el parser ni se completa Gentle-AI/routing.

La selección es una lista cerrada no vacía de IDs exactos, cada uno con su intención
explícita. Se ordena de forma determinista y rechaza duplicados. Una misma clave no
se abrevia ni se adopta por similitud; el índice por hash conserva y compara el
valor completo, incluidos IDs largos. La intención debe pertenecer al mismo
proyecto/documento/perfil y tener cabeza D5 versión 0, base/proyección nulas, ningún
destino materializado y ningún hecho previo de aplicación para esa intención.

Una intención que reconoció una ausencia y avanzó su versión ya no cumple este
perfil inicial, aunque nunca haya creado una tarea. No se resetea, borra o sustituye
para volver a cero. Su tratamiento requiere otro contrato. Una clave nueva tampoco
permite eludir un UUID/task_key ocupado o una identidad de origen ya reservada.

## Observación y referencia explícitas

Se reutiliza la selección de referencia aprobada en D5: la observación elegida debe
ser la referencia actual del mismo documento/perfil, con versión esperada exacta.
Si aún no hay referencia, el operador debe seleccionarla expresamente antes de
preparar el bootstrap. No se elige por fecha, no se acepta una versión implícita y
ningún paso de bootstrap selecciona o avanza esa referencia automáticamente.

Cada fila seleccionada debe existir exactamente una vez en esa observación. Se
verifican los bytes almacenados de fuente y preview, sus hashes y la reconstrucción
determinista con el perfil fijado, igual que en I4/I5. El preview debe carecer de
diagnósticos bloqueantes: una ambigüedad o ID duplicado bloquea la observación
completa, incluso si afecta a una fila no seleccionada. No se acepta una lista
parcial como si reparara una fuente ambigua.

Los avisos no bloqueantes del perfil compatible se conservan: blancos admitidos,
anotaciones y líneas no interpretadas no se convierten en aprobación ni completitud.
Una fila no seleccionada no necesita intención registrada y no se materializa.
Un título vacío en una fila no seleccionada no bloquea por sí solo el bootstrap de
otras filas si el parser no emitió diagnóstico bloqueante; el control de proyección
se aplica a cada fila seleccionada. La selección no acredita haber importado todo
el documento.

Una observación con otra etiqueta pero los mismos bytes sigue siendo otra
observación; un manifiesto no se sustituye por ella. Cambiar la referencia y volver
a la misma observación invalida la versión anterior: ABA no recupera vigencia.

## Preparación y revisión propuestas

Los nombres siguientes expresan interfaces futuras, todavía no disponibles:

| Paso | Contrato propuesto |
|---|---|
| PREPARE_BOOTSTRAP_TASK | Recibe command_id, proyecto/documento, intención, source_key, observación, hashes fuente/preview/fila y versión esperada de referencia; reconstruye y prepara un manifiesto sin crear tarea |
| REVIEW_BOOTSTRAP_TASK | Acepta/rechaza el manifiesto íntegro fijando proposal_id, manifest_sha256 y versión esperada de su revisión propia; registra etiqueta y razón sintéticas |
| PACKAGE_BOOTSTRAP_TASKS | Fija la lista explícita de manifiestos aceptados y sus pins de revisión; no descubre filas nuevas |
| APPLY_BOOTSTRAP_TASKS | Recibe únicamente ámbito, command_id y hash de ese paquete inmutable; comprueba vigencia y aplica todo o nada |

Preparar se hace por fila para revisarla individualmente; empaquetar reúne solo las
filas seleccionadas. El manifiesto usa una variante y dominio propios, propuestos
como `d5.bootstrap-task-manifest.v1`, inequívocamente `BOOTSTRAP_INITIAL`. Contiene:

- Proyecto/documento/ID/perfil, intención completa y versión inicial esperada cero,
  UUID/task_key explícitos y política de proyección.
- Observación, SourceRevision del mismo ámbito, hash de bytes fuente y preview,
  versión de referencia y fila completa del preview con su hash canónico propio,
  candidato, campos, tachado, anotación y localizador exacto hash+línea.
- Acción CREATE_INITIAL_BACKLOG, proyección literal título/descripción, base
  semántica inicial y su digest `d5.source-basis.v1`, con reglas I8.
- Expectativa de ausencia de UUID y `(project_id, task_key)`; versión del formato
  de esa expectativa. No se admite un snapshot de tarea existente como destino.
- Ausencia explícita de base aplicada previa, fecha de preparación como metadato
  no autoritativo y `activation_allowed=false`.

El snapshot completo se identifica por observación/hashes y permanece recuperable
con sus bytes inmutables en PostgreSQL; no se duplica la fuente entera en cada
manifiesto. La fila íntegra sí forma parte del manifiesto. La revisión permite
inspeccionar el snapshot reconstruido y esa fila con su destino y efecto completo.
No se reinterpreta un hash de fila canónica como hash semántico o de JSONB SQL.

No existen comparison_id, before_observation_id o decisión I5 para este caso.
No se insertan valores ficticios o NULL para colarlo por las entradas I8; no se
presenta como ADDED o UNCHANGED. Una decisión I5 o I8 tampoco autoriza bootstrap.
La revisión propia exige ACCEPT del manifiesto completo, sin elegir campos sueltos.
Las etiquetas siguen siendo afirmaciones sintéticas, sin autenticación real D6.

Rechazar no libera identidad ni avanza la base. Volver a aceptar incrementa la
versión de revisión, por lo que los pins anteriores quedan obsoletos. Un manifiesto
es inmutable: otra observación, fila, destino o proyección exige otra preparación y
revisión. Se mantiene el límite de 1–2.000 filas por paquete y los límites de bytes
I4/I5/I8 aplicables; no se amplían silenciosamente para la carga inicial.

## Aplicación y continuidad con I8

El paquete tiene dominio propio `d5.bootstrap-task-package.v1` y lista determinista
por proposal_id. Cada pin incluye identidad/hash de manifiesto y comando/versión de
revisión. No admite dos filas de la misma intención, identidades duplicadas o
mezclar propuestas bootstrap con propuestas de comparación I8. Otro comando sobre
la misma lista exacta no crea una selección distinta por fecha.

APPLY futuro debe adquirir la frontera vigente I8: helper fijo de administrador
→ d3.lock_state (742001, 742002 y relaciones vigentes) → mutex D5 742005 →
correspondencias ordenadas. Exige READ COMMITTED; reconstrucción e I/O se hacen
antes de esa transacción. Preparar/revisar no bloquean escritura D2 antes de la
frontera. Se reutiliza el helper aprobado sin ampliar su SQL o sus callers.

Bajo esos locks comprueba todos los manifiestos, revisiones ACCEPT y versiones,
referencia/observación exactas, ámbito y procedencia, intención/base cero y ausencia
del destino tanto por UUID como por clave. Una sola fila inválida bloquea todo el
paquete. Que otra transacción ocupe la clave tras preparar no autoriza adopción.

Para cada fila, el efecto atómico propuesto es:

1. Crear exactamente una tarea BACKLOG, row_version 0, epic_id NULL, urgency 0,
   deadline_at NULL y deferred_count 0. Item y Objective se conservan literalmente
   como title/description; título vacío o solo blancos bloquea. Objective vacío o
   guion se conserva. Status, Verified, bloqueos, tachado y anotación son evidencia.
2. Materializar la correspondencia I8 con FK tarea/proyecto e insertar task_sources
   con SourceRevision de esa observación, documento/proyecto y localizador exacto.
   Preservar cualquier procedencia anterior; no se adopta una tarea para reutilizarla.
3. Inicializar la cabeza compartida de correspondencia a versión 1 con base
   semántica y proyección aplicadas de la fila real. Conservar el registro de
   intención; no crear una identidad paralela solo para bootstrap.
4. Añadir hecho inmutable de aplicación, auditoría explícita D5_TASK_IMPORT y
   recibo, con fecha en D5 según A19. No añadir tasks.updated_at, STATE_CHANGED,
   outbox, operaciones, entregas, reservas, dependencias o planes.

Tarea, vínculo, correspondencia, base, auditoría y recibo se confirman juntos.
Un conflicto de negocio deja recibo CONFLICT sin efectos parciales; un fallo
estructural revierte todo y no reconoce éxito. command_id sigue siendo global D5:
replay exacto conserva el recibo histórico y un contenido distinto entra en conflicto.
Otro comando del mismo paquete ya aplicado devuelve ALREADY_APPLIED enlazado al
original, sin comprobarlo como una solicitud de segunda creación ni restaurar datos.
Otro paquete nuevo sobre la misma intención ya avanzada entra en conflicto.

Tras un bootstrap correcto, I8 puede continuar con dos observaciones reales: la
fila «antes» debe coincidir semánticamente con la base inicial; mantienen vigencia
su propia referencia/version, revisión de origen I5, revisión de manifiesto I8 y CAS
del destino. Se valida PATCH, enlace de evidencia y ausencia sin borrado. No se
automatiza esa comparación ni se mueve la referencia al crear la tarea. Un manifiesto
I8 preparado sobre versión cero queda obsoleto si gana primero bootstrap, y a la
inversa. Se comprueba la carrera entre ambas rutas sin alterar entradas anteriores.

## Aislamiento, permisos y siguiente gate

Una implementación futura sería aditiva: artefactos, entradas y adaptador propios,
sin modificar V33 o el verificador I8 para que acepte manifiestos sin comparación.
Reutilizaría las correspondencias/cabezas y el propietario separado NOLOGIN
aprobados. Los callers writer/reviewer/reader/applier recibirían solo las entradas
nuevas pertinentes; sin DML directo ni autoridad general D3/D4. El helper privilegiado
seguiría perteneciendo al administrador. Se validaría esa separación efectiva.

El laboratorio futuro sería otro V30 desechable con fixtures sintéticas y evidencia
propia, separado de Compose dev/D4 y de las campañas anteriores. CREATE cambia el
digest D3: se debe detectar la obsolescencia de una captura anterior y conservar los
snapshots publicados de fixture; no se promete conservación del digest I6.
`task_eligible=true` en BACKLOG sigue sin significar activación.

Este corte solo prepara contrato/matriz y verifica enlaces, formato, publicación e
integridad histórica. No ejecuta la matriz nueva ni requiere repetir baterías SQL.
El siguiente gate es aprobar el contrato y autorizar expresamente implementar y
validar ese laboratorio, sin promoción o despliegue. Reaparición, adopción,
resolución de ediciones locales, cambio de perfil/política, múltiples orígenes,
Gentle-AI/routing completo, proveedores/credenciales reales y D6 siguen fuera.
