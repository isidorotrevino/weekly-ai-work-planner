# D5 I17 — contrato propuesto de reaparición con divergencia local

Fecha: 2026-10-22. **Diseño para revisión; sin implementación ni SQL nuevo.**
Base publicada: `7083b18`, [reaparición I12](D5-I12-REAPPEARANCE-LAB.md),
[resolución local I14](D5-I14-LOCAL-EDIT-LAB.md) y
[adopción I16](D5-I16-ADOPTION-LAB.md).
[Matriz de aceptación y siguiente decisión](D5-I17-LOCAL-REAPPEARANCE-REVIEW.md).
D5 abierto; D1–D4 cerrados y D6 pendiente.

English: proposed reviewed resolution of local title/description divergence when
an existing source ID reappears. Retain the confirmed absence and identity proof,
review the whole source/local choice, and preserve task identity. Design only;
no SQL implementation, activation, promotion or deployment.

## Decisiones y garantías heredadas

| ID | Decisión del usuario | Consecuencia |
|---|---|---|
| D5-A41 | Continuar con contrato/matriz del siguiente pendiente: resolución local de reaparición | Diseño antes de SQL o laboratorio nuevo |
| D5-A42 | Cualquier divergencia actual al preparar, exista antes de la ausencia o aparezca durante/después | Revisar el snapshot actual completo; no exigir que ese texto estuviera ya en el recibo histórico |
| D5-A43 | Una revisión propia del manifiesto completo, con prueba, identidad y elección/razón origen-local | ACCEPT I5 separado; no reutilizar aceptaciones I12/I14 anteriores |

Se conservan las elecciones A31/A33 de I14: USE_SOURCE o KEEP_LOCAL completos,
sin campos sueltos, texto manual ni override permanente. Se mantienen A25–A28 de
I12: SAME_SOURCE_ENTITY con razón, ausencia I8 aplicada/versionada y posibilidad de
un «antes» ausente distinto, reconstruyendo y fijando ambas observaciones.
Las reglas siguientes concretan la propuesta para aprobación; estas decisiones
no autorizan implementarla todavía. Se conservan V1–V37, funciones, contratos,
parsers/perfiles, adaptadores, runners, manifiestos y evidencias anteriores.
No se reserva un número de migración ni se publica sin autorización del commit.

## Problema y unidad de resolución

I12 admite ADDED ausente→presente de una identidad materializada, pero rechaza
LOCAL_EDIT_CONFLICT si el texto local difiere de la proyección de origen guardada.
I14 resuelve cambios de fila presente CHANGED, no reapariciones. Usar uno como si
fuera el otro eliminaría la prueba de ausencia o inventaría una fila antes presente.
La variante propuesta tiene manifiesto, revisión, paquete y entradas propios.

La identidad sigue siendo `(project_id, document_id, source_key)` exacta, intención
D5 con destino materializado, UUID/task_key y perfil/política fijos. La tarea puede
proceder de I8, I10 o adopción I16 y conservar efectos posteriores I12/I14. Debe ser
la misma tarea del mismo proyecto, BACKLOG, sin operaciones ni planificación,
incluidas históricas/canceladas. No se crea, adopta, transfiere, reabre o reactiva
una tarea. Los vínculos task_sources existentes se conservan: esta variante no
exige que estén vacíos ni borra procedencia para admitirla.

El manifiesto distingue tres valores completos de title/description:

| Valor | Fuente | Significado |
|---|---|---|
| B | Cabeza D5 vigente | Última proyección **del origen** registrada; no necesariamente el texto que se conservó en la tarea |
| L | Snapshot completo actual de la tarea | Texto local sometido a esta revisión |
| S | Fila después de la comparación ADDED reconstruida | Proyección literal del ID reaparecido |

Se exige L distinto de B al preparar y validar el efecto. Si coinciden, corresponde
I12 ordinario; no se usa esta variante para eludir sus controles. S puede coincidir
con B o con L. La última base presente de cabeza es evidencia histórica, no una
fila presente en la observación «antes» actual, donde el ID debe estar ausente.

A42 admite divergencia preservada por adopción o KEEP_LOCAL y ediciones locales
anteriores, durante la ausencia o posteriores a observar la reaparición, siempre
que el snapshot actual completo se prepare/revise. Se conserva el target histórico
del recibo de ausencia como tal; no se lo reemplaza por L ni se exige que coincida
con L. Esos snapshots no demuestran por sí solos quién o cuándo editó cada campo.
Una edición después de preparar invalida el manifiesto; no queda autorizada por A42.

## Prueba de ausencia e identidad

Se fija la misma prueba histórica de I12: aplicación I8 OK confirmada y propuesta
KEEP_EXISTING_NO_DELETE para esa intención/tarea, con cadena commands → paquete →
propuesta/revisión histórica → aplicación/efecto/recibo. Debe haber antes presente y
después ausente en esa comparación de ausencia, y destino materializado entonces.
Observación, simulación, ACCEPT sin aplicación o recibo CONFLICT no bastan.
Se reconstruyen bytes y previews de aquella comparación, además de los actuales.

La versión producida por la ausencia debe ser exactamente la cabeza vigente fijada
por el nuevo manifiesto. Se contrasta la proyección conservada por el recibo con B;
no se elige prueba por fecha ni se acepta otro ciclo o intención. Un nuevo efecto
que avance cabeza obliga a preparar desde su estado real y aportar prueba válida.
ALREADY_APPLIED remite al hecho original, sin fabricar otra versión de ausencia.

La base semántica presente y B se toman de la cabeza vigente y se fijan con hashes.
No se deducen de before_basis de la ausencia: I8 permite que esa fila histórica
sea distinta de la última base aplicada para KEEP_EXISTING_NO_DELETE. La prueba
sigue acreditando su efecto y versión, sin reconstruir una base histórica falsa.
La procedencia de una tarea adoptada tampoco sustituye el recibo I8 de ausencia.

La comparación actual debe ser I5 PREVIEW_ONLY, mismo documento/proyecto/perfil,
ADDED con before.row nulo y after.row íntegro, sin diagnóstico bloqueante en
ninguna captura. Se exige ACCEPT I5 vigente por comando/versión y hashes de reporte
y fila; no se fabrica CHANGED, before presente, comparación o decisión I5.

La referencia actual debe ser la observación antes de esa comparación con versión
esperada exacta. Puede ser distinta de la observación después del recibo histórico:
se reconstruyen ambas y el mismo ID sigue ausente en el ámbito/perfil correctos.
Se fijan ambas observaciones; no se sustituye una por igualdad de hash o fecha.
ABA de referencia, revisión o cabeza deja obsoletos los pins antiguos.

El preparador declara SAME_SOURCE_ENTITY y una razón explícita. ID reutilizado para
otra entidad, identidad no confirmada o declaración distinta bloquean esta variante.
Elegir KEEP_LOCAL no exime de confirmar identidad: también añade procedencia y
actualiza la base del origen. Razón de identidad y razón de resolución son campos
separados, ambas de 1–1.024 caracteres, sin controles ni solo blancos Unicode.
No se infiere identidad a partir del título, texto local o claims de la fuente.

Revocar después la aceptación de una ausencia histórica no revierte el hecho
confirmado ni restaura la cabeza. Como en I12, prueba histórica y autorización
actual son conceptos distintos: la reaparición requiere ACCEPT I5 y revisión propia
actuales. Declaraciones, razones y etiquetas son afirmaciones sintéticas, no
identidad autenticada D6 ni prueba criptográfica de la entidad externa.

## Manifiesto y revisión conjunta

El manifiesto propuesto `d5.local-reappearance-task-manifest.v1`, modo
LOCAL_REAPPEARANCE, contiene:

- Intención/destino completos, ámbito/ID/perfil/política y versión de cabeza;
  última base semántica presente, su digest `d5.source-basis.v1` y B con su hash.
- Prueba íntegra de ausencia aplicada y versionada, observaciones histórica y
  actual ausentes, comparación/reporte/fila ADDED completos y sus hashes, ACCEPT
  I5 vigente, referencia/version, revisión fuente después y localizador exactos.
- Snapshot actual íntegro de tarea en UTC, row_version, formato/digest
  `d5.task-target.v1`, L y hash; distinguirlo del snapshot histórico de la prueba.
- Fila reaparecida íntegra, nueva base semántica y S con hashes por dominio;
  campos, tachado y texto de anotación como evidencia, posiciones como procedencia.
- Declaración/razón de identidad, elección USE_SOURCE/KEEP_LOCAL y razón de
  resolución, resultado derivado completo, acción y columnas de tarea a escribir.
- Metadatos de preparación no autoritativos y `activation_allowed=false`.

El resultado se deriva del origen o del snapshot local; el llamante no puede
proporcionar texto manual, máscara de campos o force. El revisor ve prueba,
identidad, B/L/S, razones, destino y efecto y acepta/rechaza el manifiesto íntegro.
A43 establece una sola revisión propia conjunta y versionada; ACCEPT I5 sigue
siendo requisito separado, no autorización del destino ni del descarte de texto.
No se aceptan dos revisiones de manifiestos distintos como si formaran esta revisión.

Otra fuente, prueba, declaración, razón, elección o snapshot requiere otra
preparación/revisión. Revocar/reaceptar incrementa versión e invalida pins viejos.
Se usan artefactos y dominios nuevos; no se modifican las revisiones, manifiestos
o verificadores anteriores para aceptar esta variante.

Los nombres siguientes son interfaces de diseño, todavía no disponibles:

| Paso | Contrato propuesto |
|---|---|
| PREPARE_LOCAL_REAPPEARANCE_TASK | Intención, comparación/hashes de reporte/fila, versiones esperadas de referencia/cabeza, aplicación/propuesta de ausencia, declaración/razón de identidad y elección/razón de resolución; prepara sin escribir tarea |
| REVIEW_LOCAL_REAPPEARANCE_TASK | proposal_id/hash, versión propia esperada, ACCEPT/REJECT, etiqueta/razón; revisión conjunta completa |
| PACKAGE_LOCAL_REAPPEARANCE_TASKS | Lista explícita ordenada de proposal_id/hash y review_command_id/version; una propuesta por intención |
| APPLY_LOCAL_REAPPEARANCE_TASKS | command_id global D5, ámbito y hash del paquete inmutable; sin texto de resultado ni force |

Paquetes de 1–2.000 propuestas, dominio `d5.local-reappearance-task-package.v1`,
sin duplicados ni mezcla con variantes I8/I10/I12/I14/I16. No se seleccionan todas
las aceptadas ni se descubre la de fecha más reciente. Se mantienen límites de
bytes existentes. El adaptador confiable verifica reconstrucción actual e histórica
antes de preparar, revisar, empaquetar y aplicar; SQL privilegiado no acredita por
sí solo parsing de los bytes fuente.

## Efectos y continuidad

| Elección | Condición | Acción propuesta | Tarea |
|---|---|---|---|
| USE_SOURCE | S distinto de L | PATCH_LOCAL_REAPPEARANCE_USE_SOURCE | Solo title/description a S, row_version +1 una vez |
| USE_SOURCE | S igual a L | LINK_LOCAL_REAPPEARANCE_EVIDENCE | Sin UPDATE ni incremento de row_version |
| KEEP_LOCAL | L distinto de B, cualquiera que sea S | KEEP_LOCAL_REAPPEARANCE | Conservar toda la fila sin UPDATE ni incremento de row_version |

S exige título válido no vacío/solo blancos Unicode y descripción string. L exige
título válido y puede conservar descripción SQL NULL según D2. S inválida bloquea
incluso KEEP_LOCAL. Texto literal sin normalizar Unicode, renderizar Markdown,
desescapar pipes o resolver URLs. Estado/verificación/bloqueos/tachado/anotaciones
del origen son evidencia, sin transiciones, aprobaciones o dependencias inferidas.

En todas las acciones la cabeza avanza una vez con base semántica reaparecida y
`projection=S`. No se guarda L como proyección del origen ni se redefine B. El hecho
inmutable/recibo conserva resultado real, S, elección, razones y prueba; `writes_task`
se distingue de escritura de procedencia D2. Fecha de aplicación en D5 según A19;
no añadir tasks.updated_at ni modificar created_at u otros campos locales.

Se añade o reutiliza task_sources exacto a la fila después, con FK y localizador
coherentes, sin editar vínculos anteriores o añadir vínculo a la fila ausente.
Acredita procedencia, no igualdad del texto conservado. No se crean tareas,
intenciones, destinos o identidades nuevos, ni se mueven referencia D5, puntero
público de fuente o cursor de proveedor.

Tras USE_SOURCE o convergencia L=S, I8 puede continuar desde la base nueva con
comparación real, referencia/version y revisiones propias. KEEP_LOCAL con L distinto
de S mantiene el conflicto local en el siguiente cambio: exige otra resolución
I14 si la fila sigue presente. No concede preferencia permanente, ni resuelve una
edición local aislada sin cambio revisable del origen.

Otro ciclo de ausencia/reaparición exige otra ausencia I8 aplicada que produzca
la versión vigente. Si vuelve a haber divergencia, esta variante exige nueva
preparación/revisión; I12 ordinario sigue bloqueándola y sirve cuando L=B. I14 sigue
exigiendo CHANGED presente→presente. Ninguna aceptación antigua se convierte en
permiso para un ciclo nuevo, restauración de estado o adopción de otro destino.

## Atomicidad, permisos y siguiente decisión

APPLY futuro exige READ COMMITTED y helper fijo de administrador vigente:
742001 → 742002 → relaciones D3 → mutex D5 742005 → intenciones/cabezas y destinos
ordenados. No se toman locks de escritura D2 al preparar/revisar. Se comprueba el
paquete entero antes del primer efecto: prueba/versión, identidad/cabeza, revisiones,
referencia, B/L/S/resultado, snapshot/digest íntegro y BACKLOG sin trabajo/plan.
A42 no autoriza un cambio de tarea posterior a preparar, incluso sin aumento de
row_version. ABA observable invalida el pin; ABA externo sin ninguna huella de
versión/evidencia no se presenta como detectable.

Una fila inválida deja CONFLICT sin efectos parciales. Aborto/error estructural
revierte tarea, vínculo, cabeza, hecho, auditoría y recibo de éxito. command_id es
global D5; replay exacto conserva el recibo histórico, contenido distinto entra
en conflicto y otro comando del mismo paquete confirmado solo ALREADY_APPLIED,
sin restaurar texto o versiones. Paquetes distintos sobre una misma cabeza se
serializan con un ganador y conflicto del otro, incluso entre variantes.

Implementación futura aditiva, cabeza/destino compartidos y propietario NOLOGIN,
con roles writer/reviewer/applier/reader separados, sin DML directo para callers
ni autoridad general D3/D4. Se mantienen las entradas/rechazos antiguos: I8 no
resuelve ADDED materializado, I12 no sobrescribe divergencia e I14 no trata ADDED.
La auditoría usa D5_TASK_IMPORT y acción propia, no STATE_CHANGED ni outbox.
PATCH cambia el digest de tarea D3; se detecta captura obsoleta sin reescribir
snapshots publicados. Enlace/KEEP_LOCAL no escriben tarea y se miden por separado
los efectos de evidencia. BACKLOG eligible no significa activación.

El siguiente paso exige aprobar este contrato completo y autorizar por separado
implementación y matriz en otro laboratorio V30 desechable con fixtures BACKLOG
sintéticas, separado de dev/D4. Este corte solo verifica documentos e integridad;
no ejecuta la matriz ni inicia servicios. D5 sigue abierto: edición local sin cambio
revisable del origen, IDs reutilizados para otra entidad, transferencias, adopción
con trabajo o procedencia previos, perfil/política, múltiples orígenes y Gentle-AI/routing completo
conservan pendientes. Sin proveedores/credenciales reales, activación, promoción,
despliegue ni ampliación D6; D1–D4 y sus evidencias se conservan.
