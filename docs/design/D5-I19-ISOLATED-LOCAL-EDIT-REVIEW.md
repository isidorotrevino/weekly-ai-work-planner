# D5 I19 — revisión de resolución local aislada y matriz de aceptación

Fecha: 2026-10-22. **Preparado para revisión; matriz todavía no ejecutada.**
[Contrato propuesto](D5-I19-ISOLATED-LOCAL-EDIT-DESIGN.md). Base publicada: `dd9b4f6`.
D5 abierto; D1–D4 cerrados y D6 pendiente.

English: acceptance matrix for a future isolated-local-edit lab. A selected present
row must match the entire applied source basis. Review source/local choice without
fabricating I5 comparisons, preserve the source basis and version the local effect.
Documentation checks do not execute this matrix.

A45 limita el corte a contrato/matriz. A46 exige fila presente seleccionada y base
semántica íntegra igual a cabeza. A47 avanza una versión conservando base/proyección;
A48 bloquea mientras el efecto exacto vigente sea una ausencia aplicada, aunque se
seleccione una observación presente anterior. Se mantiene elección completa origen
/local y revisión propia sin excepción permanente. Implementación aún no autorizada.

## Matriz futura — IL01–IL36

| Caso | Situación | Resultado exigido |
|---|---|---|
| IL01 | Destino propio I8/I10/I16, con efectos presentes I12/I14/I18 o resolución aislada anterior | Preparar/replay sin escribir tarea/cabeza/procedencia, fijando identidad, B/L/S y prueba exacta |
| IL02 | Ámbito/UUID/clave/proyecto/documento/perfil/política distintos o intención v0 no materializada | Conflicto sin creación, adopción, transferencia o reinicialización |
| IL03 | L=B, incluso con row_version distinto; convergencia tras preparar | Rechazar como no divergente; ninguna confirmación automática ni versión nueva |
| IL04 | Divergencia directa actual, preservada por adopción o KEEP_LOCAL, con/sin incremento de row_version | Snapshot actual completo revisable; sin inferir autor/fecha ni exigir igualdad con target histórico |
| IL05 | Fila fuente íntegramente igual a source_basis y S=B | Admitir sin comparación, review_item o ACCEPT I5; la revisión propia autoriza el snapshot y efecto |
| IL06 | Igual Item/Objective pero distinto Status, Verified, componentes, bloqueos, tachado o anotación | Bloquear por diferencia de base íntegra; no absorber cambio remoto ni eludir I14 |
| IL07 | Snapshot con bytes/posiciones distintos, pero fila semántica idéntica | Permitir fijando observación/SourceRevision/localizador reales, hashes por dominio e identidad exacta |
| IL08 | Cabeza vigente producida por ausencia I8, referencia presente anterior y S=B | Bloquear ambas elecciones sin avanzar cabeza ni consumir/reversionar prueba; resolver reaparición por I12/I18 |
| IL09 | Prueba de otro efecto, versión, intención/tarea, paquete, pin o recibo; comando CONFLICT/ALREADY_APPLIED sin hecho original | No acreditan presencia aplicada de cabeza; sin selección por fecha ni audit_event aislado |
| IL10 | Inicialización I16 v1, reaparición presente confirmada tras ausencia antigua y futuras resoluciones aisladas encadenadas | Acreditar efecto real exacto y versión; no inventar cabeza v0 ni bloquear para siempre una ausencia superada |
| IL11 | Observación ausente, ID duplicado, diagnóstico bloqueante en otra fila o perfil ajeno | Bloquear todo el snapshot; no adoptar solo filas aparentemente válidas |
| IL12 | Referencia no seleccionada/distinta, versión errónea o A→B→A | Conflicto; no cambiar referencia, escoger mayor fecha o sustituir observación por hash igual |
| IL13 | Alterar bytes fuente/preview/fila, hashes, revision_id o localizador | Reconstrucción/ámbito/FK verificables; fallo sin éxito ni evidencia falsa |
| IL14 | ID largo, Unicode/Markdown/pipes, fila tachada y anotaciones | Igualdad completa de ID/texto y evidencia literal sin normalizar o inferir workflow |
| IL15 | Título local/origen inválido; descripción local NULL y Objective vacío/guion | Bloquear origen inválido incluso KEEP_LOCAL; conservar null/strings literalmente |
| IL16 | Razón vacía/solo blancos Unicode, controles, exceso/tipos inválidos; force, máscara o texto de resultado | Rechazar; elección USE_SOURCE/KEEP_LOCAL y resultado completo derivados |
| IL17 | Revisiones previas I5/I8/I10/I12/I14/I16/I18 o aceptación de otro manifiesto | Insuficientes; revisión propia completa y no transferible requerida |
| IL18 | Revisión propia REJECT, revocación/reaceptación o pin/comando/versión incorrectos | Bloquear paquetes anteriores; ABA no recupera vigencia |
| IL19 | Alterar elección, prueba, snapshot, base, proyección, razón o manifiesto/hash | Artefacto inmutable y reconstrucción verificable; nueva preparación y revisión |
| IL20 | USE_SOURCE con L distinto de B=S | PATCH title/description completos a B, row_version +1 una vez; todos los demás campos intactos |
| IL21 | KEEP_LOCAL con L distinto de B=S | Trigger negativo detecta cualquier UPDATE; conservar fila completa y row_version, resultado=L explícito |
| IL22 | Ambas elecciones, origen semántico sin cambios | Cabeza +1 exactamente; source_basis, digest y projection permanecen idénticos; no nueva revisión ficticia del origen |
| IL23 | Paquetes I8/I14/I18/aislados preparados antes, especialmente tras KEEP_LOCAL sin UPDATE | Conflicto por cabeza vieja; no rebase por igualdad de B o tarea ni avance en replay |
| IL24 | Cambio tras preparar sin row_version, otros campos, clave/estado, ABA observable | CAS/guards rechazan snapshot no revisado; no prometer detectar ABA externo sin huella |
| IL25 | Tarea no BACKLOG o con operaciones/planificación, incluso históricas/canceladas | Bloquear ambas elecciones al preparar/aplicar; fixtures negativas revertidas y nunca ejecutadas |
| IL26 | Paquete explícito, límites/duplicados, origen/tarea repetidos, varias observaciones/perfiles o mezcla de variantes | Lista ordenada de 1–2.000, una por intención y snapshot/perfil únicos; ninguna selección implícita |
| IL27 | Dos paquetes/variantes sobre misma cabeza | Sesiones simultáneas con espera observada, un avance ganador y conflicto del otro incluso si gana KEEP_LOCAL |
| IL28 | Referencia/revisión cambia durante espera; locks cruzados D3/D5 | Orden fijo y comprobación vigente tras desbloqueo, sin usar snapshot anterior a espera |
| IL29 | Fila inválida en paquete mixto, aborto real o fallo tardío tras comenzar efectos | Rollback íntegro de tarea/vínculo/cabeza/hecho/auditoría y éxito; ningún avance parcial |
| IL30 | Replay exacto, command_id global con otro contenido o mismo paquete con comando nuevo | Recibo histórico, conflicto o ALREADY_APPLIED; no restaurar texto/base/versiones |
| IL31 | Commit con respuesta perdida, reinicio y CLI | Recuperar el mismo recibo sin repetir PATCH, enlace o avance; JSON cerrado y duplicados rechazados |
| IL32 | Vínculo seleccionado idéntico existente, procedencia previa o FK/localizador ajenos | Añadir/reutilizar vínculo exacto append-only o rechazar incoherencia; no afirmar igualdad del texto conservado |
| IL33 | USE_SOURCE y siguiente cambio I8; KEEP_LOCAL y siguiente cambio I14; origen igual y nueva resolución aislada | Continuidad con controles/revisión propios, B conservada y sin override permanente |
| IL34 | Nueva ausencia/reaparición posterior y entradas anteriores | I8 conserva ausencia; I12/I18 exigen nueva prueba/version/identidad; rechazo de ausencia vigente intacto y sin relajar contratos antiguos |
| IL35 | Roles/DML directo, READ COMMITTED, captura/digest D3 y plan publicado | Permisos mínimos, orden observado; PATCH vuelve obsoleta captura y planes publicados permanecen inmutables |
| IL36 | Regresiones I4–I18, catálogo/evidencias y estado final | Funciones/ACL/cierres intactos; cero tareas nuevas por resolución y cero operaciones/outbox/entregas/intentos/reservas finales |

IL01/IL04 incluyen adopción divergente, KEEP_LOCAL previo y ediciones sin aumento
de row_version. IL05 comprueba que ni preparar/revisar ni aplicar inventan
comparaciones, review_items o row_decisions I5; no basta etiquetar la acción como
«sin comparación» si se escriben esos hechos.

IL06 cubre todas las partes de `d5.source-basis.v1`, incluidas anotaciones y tachado;
IL07 distingue semántica de posición/procedencia. IL08 se ejecuta con referencia
presente antigua explícitamente seleccionada y para ambas elecciones: la igualdad
B=S no prueba presencia de la cabeza. IL09 usa cadenas válidas de otro ámbito o
versión, además de recibos incoherentes negativos revertidos; solo un pin no basta.
IL10 incluye presencia de I16 sin una cabeza previa v0 ficticia y nueva prueba tras
una resolución aislada anterior. Una revisión histórica revocada tras un efecto
confirmado no revierte ese hecho; la revisión actual sigue siendo obligatoria.

IL20 conserva también epic_id, urgencia, fecha, diferimientos y dependencias.
IL21 instala un trigger negativo para demostrar que no hubo UPDATE de tasks,
además de comparar snapshots completos. IL22 compara exactamente base, digest y
proyección antes/después, no solo Item/Objective o row_version de tarea.

IL23 debe incluir un paquete ordinario I8 y otro de resolución I14 preparados sobre
la misma cabeza, y dos propuestas aisladas con decisiones distintas. Un paquete I18
aplicable parte de una ausencia: mientras siga vigente esa ausencia, IL08 bloquea
la variante aislada; si otra ruta gana y cambia cabeza, los pins I18 anteriores
siguen inválidos. No se fabrica un escenario I18 aceptable sobre una cabeza presente
para demostrar la invalidación. Se comprueba también que una preparación aislada
anterior pierde vigencia si una ausencia I8 gana una carrera.

IL27/IL28/IL35 requieren sesiones reales y espera observada. IL29/IL31 requieren
transacciones reales, aborto/fallo y recuperación. IL25 conserva A18: operación
sintética solo dentro de transacción negativa con rollback obligatorio, nunca
ejecutada, sin entregas/reservas persistentes. Los planes publicados de fixture
no implican d3.publish o despacho. No se inicia worker/heartbeat/transporte.

IL33/IL34 llaman las entradas antiguas sin modificarlas: no se convierte KEEP_LOCAL
en preferencia permanente ni se reutiliza una prueba antigua de ausencia tras
avanzar cabeza. IL35 distingue cambio de tarea de efectos de evidencia; no reclama
invariancia global del readset ante otros cambios concurrentes.

## Verificación documental de este corte

Se revisan la base semántica/proyección y KEEP_EXISTING_NO_DELETE de V33, snapshot
seleccionado/revisión propia de I16/V37 y resolución local de I14/V36 e I18/V38.
La propuesta distingue prueba de efecto presente, igualdad de fuente y snapshot
actual de tarea; ninguna de esas evidencias sustituye a las otras.

Se comprueban enlaces, formato, publicación y hashes históricos. No se modifican
SQL, código, harness ni documentos consumidos por pruebas, ni se inicia Docker.
No se ejecuta IL01–IL36 y ningún caso se declara PASS mediante controles documentales.

Resultados documentales (2026-10-22):

- 114 enlaces locales válidos; 36 casos únicos ordenados IL01–IL36.
- Scanner de publicación: 394 archivos de texto sin patrones configurados;
  no sustituye la revisión del diff.
- 245 entradas SHA-256 de cierre D3/D4 y documento canónico D4 intactos.
- Entradas históricas I4/I5/I6/I8/I10/I12/I14/I16/I18:
  20/27/47/51/55/60/66/72/78, todos los hashes coinciden.
- 391 archivos históricos del inventario previo coinciden; formato comprobado con
  `git diff --check`, sin incidencias.

## Siguiente decisión

Revisar el contrato completo y aprobar por separado implementación y validación
IL01–IL36 en otro laboratorio V30 desechable con fixtures BACKLOG sintéticas,
separado de dev/D4. Publicación del diseño sobre commit concreto, distinta de la
aprobación de implementación. Sin activación, promoción, despliegue o D6.

D5 conserva pendientes IDs reutilizados/transferencias, adopción con trabajo o
procedencia previos, perfil/política, múltiples orígenes y Gentle-AI/routing completo.
Proveedores/credenciales reales siguen fuera; D1–D4 y sus evidencias se conservan.
