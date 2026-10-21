# D5 I13 — revisión de resolución local y matriz de aceptación

Fecha: 2026-10-21. **Preparado para revisión; matriz no ejecutada.**
[Contrato propuesto](D5-I13-LOCAL-EDIT-DESIGN.md). Base publicada: `01eb985`.
D5 abierto; D1–D4 cerrados; D6 pendiente.

English: acceptance matrix for a future synthetic local-edit resolution lab.
Documentation checks do not establish that these scenarios pass.

A30 limita el corte a diseño/matriz; A31 permite origen completo o local completo;
A32 limita a cambios de fila presente; A33 exige nueva resolución ante cambios
posteriores mientras persista divergencia. El resto del contrato es propuesta
para revisión antes de SQL, roles, tareas o laboratorio nuevos.

## Matriz futura — L01–L32

| Caso | Situación | Resultado exigido |
|---|---|---|
| L01 | Tarea propia creada por I8/I10 o conservada tras I12, edición local y cambio presente válidos | Preparar sin escribir tarea; fijar B/L/S, cabeza, elección y destino |
| L02 | UUID/clave/proyecto/documento/perfil/política diferentes o destino no materializado | Conflicto sin adoptar, crear tarea ni cambiar identidad |
| L03 | L=B, o divergencia con/sin incremento de row_version | Rechazar variante si no hay divergencia; detectarla por valores aunque no aumente row_version |
| L04 | CHANGED con antes/después presentes frente a UNCHANGED sin fila, ADDED o ausencia | Solo cambio presente revisable; no fabricar comparación ni bootstrap/reaparición |
| L05 | Base semántica antes diferente, o igual con otra observación/posición | Conflicto en la primera; permitir la segunda con bases completas y referencia fijadas |
| L06 | Fuente no aceptada, ACCEPT I5 revocado/reaceptado o pins ajenos | Rechazar; versión monotónica, sin autorización heredada I8/I10/I12 |
| L07 | Referencia diferente o A→B→A | Conflicto aun si vuelve a la misma observación; no avanzar referencia |
| L08 | B/L/S, elección, razón, destino, snapshot o hashes alterados tras preparar | Nueva preparación/revisión; resultado libre, force y máscaras de campos rechazados |
| L09 | Elección inválida, razón vacía/solo blancos Unicode, controles o exceso de longitud | Rechazar; SAME_SOURCE_ENTITY no sustituye la elección de resolución |
| L10 | USE_SOURCE con S distinto de L | PATCH solo title/description, row_version +1, resto conservado; fecha en D5 |
| L11 | KEEP_LOCAL con S distinto de L | Fila tasks íntegra sin escritura; cabeza conserva fuente S y hecho registra resultado L |
| L12 | Convergencia S=L aunque L sea distinto de B, para ambas elecciones | Enlace/evidencia sin incremento de row_version; cabeza a S una vez |
| L13 | S=B y cambio en campos de evidencia, con divergencia local | USE_SOURCE puede restituir B; KEEP_LOCAL conserva L; revisión completa de ambas diferencias |
| L14 | Cambio local de título y remoto de descripción o viceversa | Ningún merge automático; elegir pareja completa, incluso si los campos son disjuntos |
| L15 | IDs largos, Unicode, pipes, Markdown, tachado y anotaciones | Identidad íntegra/texto literal/procedencia; no normalizar ni ejecutar contenido |
| L16 | Título origen inválido, título local inválido, descripción local NULL, Objective vacío/guion | Bloquear proyección inválida; conservar null local o string fuente exactos según elección |
| L17 | Origen Status=DONE/Verified=approved, bloqueos o anotaciones afirmativas | Solo evidencia; ninguna transición, verificación, dependencia o activación inferida |
| L18 | Edición de título/description después de preparar, sin cambio de row_version | CAS completo falla; no sobrescribir ni reconocer texto local no revisado |
| L19 | Cambio de campo no mapeado, estado, clave o row_version; convergencia y ABA observable | Snapshot/version obsoletos bloqueados; sin prometer detección de ABA externo sin rastro |
| L20 | Tarea no BACKLOG, operación o planificación histórica/cancelada | Bloquear ambas elecciones; fixtures operativas negativas siempre revertidas, sin ejecución |
| L21 | Revisión propia ausente/REJECT, revocación o reaceptación | Sin aplicar; versión/review_command_id exactos, ACCEPT I5 insuficiente |
| L22 | Paquete explícito con ambas elecciones, duplicados, límites o mezcla de variantes | Admitir elecciones distintas de esta variante; una por intención, 1–2.000, hash/lista exactos; rechazar mezcla I8/I10/I12 |
| L23 | Replay, command_id con otro contenido y mismo paquete con otro comando | Recibo histórico, conflicto o ALREADY_APPLIED; ninguna restauración de texto/cabeza |
| L24 | Dos paquetes o I8/I12 compiten; cambio de referencia/revisión durante APPLY | Sesiones reales; serialización y conflicto del perdedor, un único avance de cabeza |
| L25 | Paquete mixto inválido, backend abortado o fallo tardío tras primeras mutaciones | Rollback de tareas, vínculos, cabeza, hechos, auditoría y recibo de éxito |
| L26 | Commit confirmado, respuesta perdida y reinicio | Recuperar recibo exacto sin repetir PATCH ni avances; consultar no restaura estado |
| L27 | Vínculo después idéntico existente, localizador o SourceRevision ajenos | Reutilización coherente o rechazo; enlaces append-only, sin afirmar igualdad de texto con el origen |
| L28 | KEEP_LOCAL divergente y siguiente cambio real del origen | I8 sigue bloqueado; nueva resolución con comparación, ACCEPT y manifiesto propios; no override permanente |
| L29 | USE_SOURCE/convergencia y cambio siguiente; edición local posterior | Continuidad I5/I8 con nueva base y guards; edición posterior vuelve a bloquear |
| L30 | Ausencia después de KEEP_LOCAL y nueva reaparición | Ausencia conserva semántica; I12 bloquea si sigue divergencia; no saltar ausencia aplicada/versionada ni declaración de identidad |
| L31 | Locks cruzados, roles, helper, snapshot D3 antes y publicado | Orden vigente, permisos mínimos; PATCH invalida digest anterior sin reescribir snapshots; KEEP_LOCAL no escribe tarea |
| L32 | Regresiones I4–I12, catálogo previo y fixtures BACKLOG finales | Funciones/ACL anteriores y evidencias preservadas; cero tareas nuevas por resolución y cero operaciones/outbox/entregas/reservas/attempts finales |

L24/L31 requieren sesiones simultáneas, espera observada y estado final tras
liberar locks; no basta secuenciar llamadas. L25/L26 requieren transacciones reales,
fallo/aborto y recuperación. L20 mantiene el límite A18: cualquier operación
sintética de prueba negativa es transitoria, no se ejecuta y termina en rollback.
No se convierte esa fixture en trabajo persistente del laboratorio.

L11/L28 deben comprobar expresamente que projection en la cabeza es S, no L,
y que I8 existente sigue bloqueando por sus propios controles sin modificarlos.
L12 debe probar ambas elecciones sin UPDATE tasks; L27 debe distinguir vínculo de
procedencia y resultado efectivo. L30 usa funciones I8/I12 existentes, no versiones
relajadas. L31 exige evidencia del digest afectado y catálogo/ACL conservados.

## Verificación documental de este corte

Se contrastan los contratos e implementación V33/V35, las bases/proyecciones I8,
la continuidad bootstrap I10 y los controles de edición/ausencia I12. Se verifica
que KEEP_LOCAL pueda conservar la semántica actual de la cabeza: fuente aceptada
por un lado y resultado local reconocido por otro, con hechos propios y sin
excepciones para importaciones futuras.

Se comprueban enlaces locales, formato, publicación e integridad de cierres y
entradas históricas. No se modifican SQL, código, harness ni documentación consumida
por pruebas. No se repiten baterías SQL ni se inicia Compose por este corte.
Ningún caso L01–L32 se declara PASS mediante estas comprobaciones documentales.

Resultado documental: 102 enlaces locales válidos; revisión de publicación sobre
367 archivos de texto sin patrones configurados detectados; formato correcto.
Coinciden 245 entradas de cierre D3/D4 y el documento canónico D4, además de las
20/27/47/51/55/60 entradas de ejecución de I4/I5/I6/I8/I10/I12.
Los 40 documentos, propuestas SQL y evidencias capturados antes de este corte
permanecen idénticos. Estas comprobaciones no validan L01–L32 ni una implementación.

## Siguiente decisión

Revisar este contrato y, si se aprueba, autorizar por separado implementación y
validación L01–L32 en otro laboratorio V30 desechable con fixtures BACKLOG
sintéticas, separado de dev/D4, sin activación, promoción, despliegue o D6.

La publicación se solicita sobre el commit documental concreto una vez preparado.
Los pendientes restantes de D5 y las exclusiones del contrato se conservan;
resolver ediciones locales presentes no cierra D5 ni habilita reaparición con
edición local, adopción, mezcla de campos o integraciones reales.
