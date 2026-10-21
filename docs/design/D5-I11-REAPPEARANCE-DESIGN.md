# D5 I11 — contrato propuesto de reaparición de IDs

Fecha: 2026-10-21. **Diseño para revisión; sin implementación ni SQL nuevo.**
Base publicada: `31fd074`, [bootstrap I10](D5-I10-BOOTSTRAP-LAB.md) y
[mapeo I8](D5-I8-SYNTHETIC-TASK-LAB.md).
[Matriz de aceptación y gate siguiente](D5-I11-REAPPEARANCE-REVIEW.md).
D5 abierto; D1–D4 cerrados; D6 pendiente.

## Decisiones expresas

| ID | Elección del usuario | Consecuencia |
|---|---|---|
| D5-A24 | Diseñar reaparición, con contrato y matriz antes de SQL | Solo documentación; no crear tareas, roles, migraciones o laboratorio |
| D5-A25 | Declaración expresa de misma entidad de origen y razón; bloquear si el ID se reutilizó para otra entidad | No deducir continuidad por similitud, título o coincidencia de clave solamente |
| D5-A26 | PATCH Item/Objective si cambian o enlace de evidencia si coinciden; BACKLOG sin trabajo ni edición local | Conservar la tarea y su identidad; no reactivar, adoptar o sobrescribir cambios locales |
| D5-A27 | Recibo I8 de ausencia aplicada a la correspondencia, fijado por versión | Una observación ausente o un ACCEPT/simulación sin aplicación no bastan |
| D5-A28 | Admitir otro «antes» reconstruido con el mismo ID ausente y ámbito/perfil, fijando ambas observaciones | Cambios ajenos en el documento no fuerzan a reutilizar un snapshot antiguo; no sustituyen el recibo o su versión |

Las reglas siguientes concretan la propuesta para revisión. No autorizan
implementarla. No se reserva un número de migración. Se conservan V1–V34,
funciones, parsers/perfiles, adaptadores, runners y evidencias anteriores.

## Problema y unidad de identidad

I8 reconoce ausencias con KEEP_EXISTING_NO_DELETE: conserva tarea, base presente,
proyección y vínculos, avanzando la versión de correspondencia. Cuando una
comparación posterior muestra ADDED para una identidad materializada, devuelve
REAPPEARANCE_REVIEW_REQUIRED. I10 tampoco sirve: exige intención inicial v0 sin
destino. La reaparición propuesta tiene una variante propia y una tarea ya existente.

La identidad sigue siendo `(project_id, document_id, source_key)` exacta, con perfil
y política `d5.task-projection.v1` fijados en la intención I8. UUID y task_key no se
regeneran. El destino debe ser la misma tarea de esa correspondencia, con UUID,
proyecto y clave actual coincidentes con la intención, y FK materializada válida.
No se busca otra tarea por nombre, no se crea otra intención ni se adopta un destino.
IDs largos y texto Unicode se conservan sin truncar o normalizar.

La tarea puede haberse creado mediante I8 o bootstrap I10. Debe seguir en BACKLOG,
sin ninguna operación ni entrada de planificación asociada, incluida histórica.
No basta con que no haya trabajo activo. Otros estados no se convierten a BACKLOG;
la reaparición no redefine transiciones D2 ni introduce operaciones.

## Identidad declarada y revisión separada

El preparador debe declarar `SAME_SOURCE_ENTITY` y aportar una razón explícita,
conservadas íntegramente en el manifiesto. Una declaración de identidad diferente,
reutilizada o no confirmada bloquea este perfil. Rechazar no libera la clave para
crear otra tarea bajo la misma identidad. La resolución de reutilización exige
otro contrato; no se rebautiza automáticamente la entidad o el ID de origen.

La declaración es una afirmación del llamante, no una prueba criptográfica de la
entidad externa. La revisión debe mostrar la última base presente, fila reaparecida,
procedencia, destino y declaración/razón para aceptarlas juntas. La etiqueta del
revisor sigue siendo sintética; no se implementa autenticación real D6.

Se requiere una comparación I5 reconstruida, PREVIEW_ONLY y del mismo
proyecto/documento/perfil, con esa clave ausente «antes» y presente «después»:
ADDED, before.row nulo y after.row íntegro. Un diagnóstico bloqueante en cualquier
captura invalida la comparación completa. Ni UNCHANGED ni CHANGED sustituyen esta
variante. No se fabrica una captura vacía o una fila antes con la última base.

El ACCEPT I5 debe estar vigente y fijarse por comando, hash de fila/reporte y versión.
Revisa la observación de origen; no aprueba por sí solo reutilizar la tarea o la
declaración de identidad. Hace falta una revisión propia del manifiesto completo
de reaparición. No se usa un ACCEPT I8/bootstrap como aceptación de esta variante.

## Prueba de ausencia aplicada

El manifiesto fija una aplicación I8 confirmada y su propuesta KEEP_EXISTING_NO_DELETE.
La prueba enlaza explícitamente command_id de aplicación, hash de paquete,
proposal_id y hash del manifiesto de ausencia, comparación/fila y sus hashes,
identidad/tarea y versión de correspondencia producida. Debe comprobarse la cadena
real entre commands, task_applications, paquete, propuesta y efecto confirmado.
Un resultado de simulación, una propuesta aceptada pero no aplicada, una auditoría
suelta o un recibo CONFLICT no acreditan ausencia aplicada. También se reconstruye
la comparación/fila de aquella ausencia desde sus bytes y previews; no basta con
verificar únicamente el reporte de reaparición actual.

El manifiesto de ausencia debe corresponder a esa intención materializada, con
fila antes presente y después nula. Su aplicación tiene que conservar la última
base/proyección presentes y avanzar la cabeza a `mapping_version + 1`. Esa versión
debe ser exactamente la cabeza vigente que fija el nuevo manifiesto. Se contrastan
también la base semántica y proyección conservadas: una versión o recibo de otra
intención, tarea, documento, perfil o ciclo no puede sustituirla.

No se elige el recibo por fecha, máximo UUID o último resultado leído. Otra
aplicación posterior que avance la cabeza invalida esa prueba para un paquete nuevo.
Un ALREADY_APPLIED enlaza al hecho original; no produce otra versión de ausencia.
Una nueva reaparición tras otro ciclo exige una nueva ausencia aplicada.

La última base/proyección aplicadas se toman de la cabeza vigente y se fijan con
sus valores y hashes. No se deducen de before_basis del manifiesto de ausencia:
ese campo describe la fila de aquella comparación, que I8 no obliga a ser la última
aplicada para KEEP_EXISTING. El recibo fija su versión y su before_projection; la
nueva propuesta debe comprobar que no hubo otro efecto y conservar el estado
aplicado real. No exige igualdad artificial con una fila histórica diferente.

Según A28, la observación «antes» de la reaparición puede ser distinta de la
observación «después» del recibo de ausencia. Se reconstruyen ambas por separado:
el mismo ID debe seguir ausente, con documento/proyecto/perfil compatibles y sin
diagnósticos bloqueantes. El manifiesto conserva sus identidades y hashes, además
del recibo y de la versión vigente de cabeza. No se equiparan solo por hash, fecha
o ausencia de fila en un índice parcial. El ACCEPT I5 y la referencia/version
apuntan a la comparación actual; no se reemplaza esa referencia por la antigua.

El recibo histórico acredita el efecto confirmado, no que su revisión antigua siga
siendo una autorización actual. Revocar después una aceptación de aquella ausencia
no revierte el hecho ni restaura la cabeza. La autorización de reaparición exige sus
propias revisiones vigentes y el ACCEPT I5 de su comparación actual.

## Manifiesto y comandos propuestos

Las interfaces siguientes son nombres de diseño, todavía no implementados:

| Paso | Contrato propuesto |
|---|---|
| PREPARE_REAPPEARANCE_TASK | Fija intención/cabeza, comparación/fila, ACCEPT I5, referencia/version, prueba de ausencia aplicada y declaración/razón; prepara sin escribir tarea |
| REVIEW_REAPPEARANCE_TASK | ACCEPT/REJECT del manifiesto íntegro por ID/hash y versión esperada de revisión propia, con etiqueta/razón |
| PACKAGE_REAPPEARANCE_TASKS | Lista explícita ordenada de manifiestos aceptados y pins de sus revisiones; una fila por intención |
| APPLY_REAPPEARANCE_TASKS | Solo ámbito, command_id y hash del paquete inmutable; todo o nada bajo locks |

La referencia actual debe ser la observación «antes» de la comparación actual,
con versión esperada exacta. No se selecciona por fecha ni se mueve al preparar,
revisar o aplicar. ABA de referencia, aceptación o cabeza invalida el pin anterior.

El esquema propuesto `d5.reappearance-task-manifest.v1` contiene:

- Modo REAPPEARANCE, proyecto/documento/ID/perfil, intención completa y versión
  esperada de correspondencia, UUID/task_key fijos y política de proyección.
- Comparación/reporte y fila completos con hashes, observaciones antes/después,
  SourceRevision y localizador exactos de la fila presente, ACCEPT I5 y versión.
- Prueba completa de ausencia aplicada, observación que acreditó esa ausencia,
  versión resultante y última base presente/proyección con sus hashes I8.
- Declaración SAME_SOURCE_ENTITY y razón, sin inferirlas del texto de la fuente.
- Snapshot completo de la tarea en UTC, row_version, formato y digest propios
  `d5.task-target.v1`, junto con la acción y proyección antes/después propuestas.
- Nueva base semántica de la fila reaparecida y digest `d5.source-basis.v1`, con
  todos los campos, tachado y texto de anotación; posiciones solo como procedencia.
- Metadatos de preparación no autoritativos y `activation_allowed=false`.

La última base presente se muestra como evidencia histórica, no como una fila que
existiera en la captura antes. Su diferencia con la fila reaparecida es revisable;
no se exige igualdad, porque el ID puede reaparecer con cambios. La declaración
explícita y la revisión propia autorizan esa continuidad y el efecto concreto.

Una observación, destino, prueba, declaración o proyección distinta requiere otra
preparación/revisión. El paquete usa dominio `d5.reappearance-task-package.v1`,
lista exacta de proposal_id/hash y comando/versión de revisión, sin mezclar variantes
I8/bootstrap ni seleccionar automáticamente todos los ACCEPT. Se mantienen límites
1–2.000 filas y límites de bytes existentes aplicables, sin ampliación implícita.

## Efectos permitidos y conservación local

| Proyección de fila reaparecida respecto a la última aplicada | Acción propuesta | Efecto |
|---|---|---|
| title/description distintos | PATCH_REAPPEARED_BACKLOG | Modificar solo Item/Objective proyectados, row_version +1 una vez |
| title/description iguales | LINK_REAPPEARANCE_EVIDENCE | No reescribir tarea ni aumentar su row_version |

Ambas acciones requieren tarea propia BACKLOG y sin operaciones/planificación.
La comparación del destino actual con la última proyección aplicada precede al
CAS: una edición local de title/description bloquea aunque no haya aumentado
row_version o se prepare después de verla. También bloquea si ocurrió durante la
ausencia y el recibo KEEP_EXISTING la conservó. No hay force, mezcla o selección
de campos sueltos. Los demás campos locales se conservan, con snapshot completo
para detectar cualquier cambio entre preparación y aplicación.

Se usan strings del parser sin renderizar Markdown, desescapar pipes, resolver
URLs o normalizar Unicode. Título vacío/solo blancos bloquea; Objective vacío o
guion se conserva. Status, Verified, componentes, bloqueos, tachado y anotaciones
son evidencia, sin transiciones, aprobaciones, dependencias o ejecución inferidas.
PATCH preserva created_at y demás campos; la fecha de efecto queda en D5 según A19,
sin añadir tasks.updated_at. Enlace conserva la fila de tarea completa.

Ambas acciones añaden o reutilizan un task_sources idéntico, tras comprobar revisión,
documento/proyecto, UUID y localizador exacto de la fila «después». No crean vínculo
que afirme una fila en la observación ausente. No modifican vínculos anteriores.
La cabeza compartida avanza una vez, con nueva base semántica/proyección presentes;
el hecho de reaparición, auditoría y recibo quedan inmutables. No se crea tarea,
no se cambia identidad y no se avanza referencia D5, puntero público o cursor.

## Atomicidad, concurrencia y siguiente gate

APPLY futuro exige READ COMMITTED y el helper fijo vigente: d3.lock_state
742001 → 742002 → relaciones vigentes → mutex D5 742005, seguido de correspondencias
y destinos en orden. Reconstrucción/I/O fuera de locks; preparar/revisar sin locks
de escritura D2 antes de esa frontera. Se comprueban todas las filas antes del
primer efecto: pruebas, versiones, revisiones, referencia, ownership, estado/trabajo,
edición local y snapshot/digest. No se llama a funciones D3/D4 de ejecución.

Tarea, vínculo, base/cabeza, auditoría y recibo se confirman juntos. Una fila inválida
invalida el paquete entero y deja recibo de negocio sin efectos parciales; un fallo
estructural revierte todo sin recibo de éxito. command_id sigue siendo global D5.
Replay exacto conserva el resultado histórico; otro comando sobre el mismo paquete
aplicado solo ALREADY_APPLIED enlazado al original, sin restaurar tarea o cabeza.
Un paquete distinto con base/versiones obsoletas entra en conflicto.

Una implementación sería aditiva, con artefactos/entradas/adaptador propios y
cabeza/destino compartidos I8/I10. No se relaja REAPPEARANCE_REVIEW_REQUIRED en las
entradas I8 antiguas ni se convierte bootstrap en adopción. Se mantienen roles
mínimos y propietario separado NOLOGIN, helper de administrador y ausencia de DML
directo/autoridad general D3/D4 para callers. La carrera entre paquetes o variantes
sobre la misma cabeza debe producir un solo avance, sin sobrescribir otro efecto.

Tras una reaparición aplicada, I5/I8 continúan mediante comparaciones reales cuya
fila antes coincida con la nueva base semántica. PATCH cambia el digest D3 y vuelve
obsoleta una captura anterior; un enlace no reescribe la tarea. Los snapshots
publicados deben conservarse, sin prometer invariancia global del readset I6.
`task_eligible=true` en BACKLOG sigue sin significar activación.

Este corte solo verifica documentación e integridad histórica. El siguiente gate
es aprobar el contrato y autorizar por separado implementación/matriz en otro
laboratorio V30 desechable, sintético y separado de dev/D4. No se ejecuta la matriz
por esta revisión ni se inicia SQL. Adopción, reutilización de IDs para otra entidad,
resolución de edición local, cambios de perfil/política, múltiples orígenes,
Gentle-AI/routing completo, proveedores/credenciales reales, activación, promoción,
despliegue y D6 permanecen fuera. D5 no se cierra con esta propuesta.
