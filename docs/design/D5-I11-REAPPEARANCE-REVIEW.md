# D5 I11 — revisión de reaparición y matriz de aceptación

Fecha: 2026-10-21. **Preparado para revisión; matriz todavía no ejecutada.**
[Contrato propuesto](D5-I11-REAPPEARANCE-DESIGN.md). Base: `31fd074`.
D5 abierto; D1–D4 cerrados y D6 pendiente.

A24 autoriza solo contrato/matriz. A25 exige declaración de misma entidad y razón;
A26 admite PATCH o enlace de evidencia en tarea propia BACKLOG sin trabajo/edición
local; A27 exige ausencia aplicada I8 fijada por versión. A28 admite una observación
antes distinta, reconstruida con el mismo ID ausente, conservando ambas referencias.
Ninguna decisión autoriza todavía SQL, roles, tareas o un laboratorio nuevo.

## Matriz futura — R01–R30

| Caso | Situación | Resultado exigido |
|---|---|---|
| R01 | Tarea creada por I8 o I10, ausencia I8 aplicada y comparación ADDED válida | Preparar sin escribir tarea; fijar identidad, recibo, versiones y declaración |
| R02 | UUID/clave/proyecto/perfil/intención diferentes o destino no materializado | Conflicto sin adoptar, crear tarea o cambiar identidad |
| R03 | Declaración SAME_SOURCE_ENTITY y razón frente a ID reutilizado/no confirmado/razón vacía | Solo la declaración explícita válida permite preparar; otros casos bloqueados |
| R04 | Solo observación ausente, simulación, ACCEPT o ausencia aplicada a intención sin tarea | No acreditan la ausencia requerida de una correspondencia materializada |
| R05 | Recibo CONFLICT, de otro ámbito/tarea o cadena command/paquete/propuesta/efecto incoherente | Rechazar prueba; auditoría aislada o valor de fecha no basta |
| R06 | Versión del recibo no coincide con cabeza vigente, con otro efecto intermedio | Rechazar prueba obsoleta; no buscar automáticamente la de fecha mayor |
| R07 | Before de la ausencia distinto semánticamente de la última base aplicada | Conservar la base/proyección reales de cabeza; no sustituirlas por before_basis histórico ni autorizar edición local |
| R08 | «Antes» actual distinto del snapshot de ausencia por cambios en otras filas/posiciones | Permitido si ambos snapshots reconstruidos conservan ese ID ausente, ámbito/perfil y cabeza/version; fijar ambos |
| R09 | «Antes» actual contiene ID, after no lo contiene, CHANGED/UNCHANGED o snapshot bloqueante | No es una reaparición válida; no fabricar before nulo ni importar parcialmente |
| R10 | Comparación válida sin ACCEPT I5 vigente o pins obsoletos/ABA | Bloquear preparación/aplicación; no sustituir con aceptación I8/bootstrap |
| R11 | Sin referencia exacta a «antes», versión distinta o A→B→A | Conflicto sin avance automático de referencia |
| R12 | ID largo, Unicode/Markdown/pipes, tachado/anotación y hashes/localizadores | Identidad completa, texto literal, fila íntegra y procedencia verificables |
| R13 | Item vacío/solo blancos, Objective vacío/guion o fuente Status=DONE/Verified=approved | Bloquear título inválido, conservar descripción y evidencia, no inferir workflow |
| R14 | Item/Objective cambian, destino propio sin edición local y CAS coincidente | PATCH solo title/description, row_version +1, created_at y demás campos conservados; fecha en D5 |
| R15 | Proyección coincide, pero reaparece fila con igual/diferente evidencia de origen | LINK sin reescribir tarea o row_version; cabeza/base y procedencia reflejan la fila presente |
| R16 | Edición local antes/durante ausencia o tras preparar, con/sin aumento de row_version | LOCAL_EDIT_CONFLICT incluso al preparar de nuevo; no force/merge |
| R17 | Otros campos locales, identidad, estado o trabajo/plan cambian tras preparar | CAS/guards bloquean; no sobrescribir ni aplicar parcialmente |
| R18 | Tarea no BACKLOG o con operación/entrada de planificación, incluso histórica | Bloquear PATCH/enlace; no reactivar ni borrar trabajo para admitir la reaparición |
| R19 | Alteración de snapshot, recibo, declaración/razón, destino, política o manifiesto | Revisión no transferible; nuevas preparación/aceptación para otro contenido |
| R20 | Revisión propia ausente/REJECT, revocación y reaceptación | Versión monotónica y conflicto de pins obsoletos; ACCEPT I5 no aprueba destino |
| R21 | Paquete explícito ordenado, duplicados, límites o mezcla I8/bootstrap | Una propuesta por intención; lista/hash exactos; rechazar mezcla o selección implícita |
| R22 | Replay exacto, command_id reutilizado con otro contenido o mismo paquete con otro comando | Recibo histórico, conflicto de contenido o ALREADY_APPLIED; sin restaurar tarea/cabeza |
| R23 | Dos paquetes y otra ruta compiten sobre la misma cabeza o cambian referencia/revisión | Sesiones reales; un avance ganador y conflicto del otro, sin doble vínculo o pérdida de cambios |
| R24 | Fila inválida en paquete mixto; backend abortado o fallo estructural tras comenzar efectos | Rollback íntegro de tarea, vínculos, base/cabeza, auditoría y recibo de éxito |
| R25 | Commit confirmado, respuesta perdida y reinicio | Recuperar mismo recibo sin repetir PATCH o aumento de versiones |
| R26 | Procedencia después y vínculo idéntico ya existente | FK/coherencia exactas, append-only o reutilización verificada; ningún enlace a fila ausente |
| R27 | Otro ciclo ausencia/reaparición y revocación posterior de revisión de ausencia antigua | Exigir nueva ausencia/version para el ciclo nuevo; no deshacer hechos históricos ni usar pins viejos |
| R28 | PATCH, enlace y ausencia posterior por entrypoints I5/I8 existentes | Continuidad con la nueva base; I8 antiguo sigue bloqueando ADDED materializado e I10 exige v0 |
| R29 | Locks cruzados, roles mínimos, captura D3 y snapshot publicado | Orden vigente sin inversión; helper de administrador; denegar DML/autoridad D3/D4; PATCH vuelve obsoleta base D3 sin reescribir snapshots |
| R30 | BACKLOG eligible; regresiones anteriores y ausencia de activación | Cero tareas nuevas por reaparición, operaciones/entregas/outbox/reservas; campañas/manifiestos previos intactos |

R23/R29 requieren sesiones simultáneas, espera observada y estado tras desbloqueo.
R24/R25 requieren transacciones reales, fallo/aborto y recuperación; no solo mocks.
R01/R28 deben usar I5/I8 e I10 existentes y una misma correspondencia, sin reescribir
sus verificadores para aceptar la variante nueva. R07 evita confundir fila histórica
con última base aplicada; R27 distingue efecto histórico de autorización vigente.

## Verificación documental de este corte

Se revisan fuentes/referencias persistidas I4, reconstrucción y revisión I5,
correspondencias y efectos I8 y bootstrap I10. Se contrastan especialmente el hecho
KEEP_EXISTING_NO_DELETE, su avance de cabeza y las bases/proyecciones que conserva.
Se verifican enlaces locales, formato, publicación e integridad histórica, sin
arrancar servicios, añadir SQL ni repetir campañas que no cambian por este corte.
Ningún caso R01–R30 se declara PASS por el diseño.

Se conservan cierres D3/D4 y su documento canónico, más las entradas de ejecución
registradas en I4/I5/I6/I8/I10. Las evidencias anteriores siguen reflejando los
contratos/targets que tenían al emitirse. La publicación previa de I10 corresponde
a `31fd074`; la publicación de este diseño se plantea sobre otro commit concreto.

Resultado documental: 97 enlaces locales válidos, formato correcto y revisión de
publicación sobre 358 archivos de texto sin patrones configurados detectados.
Coinciden 245 entradas de cierre D3/D4, el documento canónico D4 y las
20/27/47/51/55 entradas de ejecución de I4/I5/I6/I8/I10. Esas comprobaciones
no validan R01–R30 ni acreditan una implementación de reaparición.

## Decisión siguiente

Revisar el contrato completo y, si se aprueba, autorizar por separado implementar
y validar R01–R30 en otro laboratorio V30 desechable con fixtures sintéticas y
campaña propia, separado de dev/D4. Sin activación, promoción, despliegue ni
ampliación de D6. Adopción, reutilización de ID para otra entidad, resolución local,
cambio de perfil/política, múltiples orígenes y Gentle-AI/routing completo siguen
pendientes o excluidos según el contrato. Este corte no cierra D5.
