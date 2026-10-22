# D5 I17 — revisión de reaparición local y matriz de aceptación

Fecha: 2026-10-22. **Preparado para revisión; matriz todavía no ejecutada.**
[Contrato propuesto](D5-I17-LOCAL-REAPPEARANCE-DESIGN.md). Base publicada: `7083b18`.
D5 abierto; D1–D4 cerrados; D6 pendiente.

English: acceptance matrix for a future synthetic local-reappearance lab. Confirmed
absence and current local text remain distinct evidence; review identity and the
whole source/local choice together. Documentation checks do not execute this matrix.

A41 limita el corte a contrato/matriz. A42 cubre cualquier divergencia local vigente
al preparar, con snapshot actual completo; A43 exige una revisión propia conjunta
de prueba, identidad y resolución, separada del ACCEPT I5. Se conservan A25–A28 y
A31/A33. El resto del contrato es propuesta para revisión, sin SQL ni laboratorio.

## Matriz futura — LR01–LR36

| Caso | Situación | Resultado exigido |
|---|---|---|
| LR01 | Destino propio de I8/I10/I16, incluso con efecto I14 previo; ausencia aplicada y divergencia actual | Preparar sin escribir tarea/cabeza, fijando identidad, prueba y B/L/S actuales |
| LR02 | UUID/clave/proyecto/documento/perfil/política distintos o destino no materializado | Conflicto sin crear/adoptar/transferir tarea o intención |
| LR03 | L=B, aunque S difiera | Rechazar variante local; I12 ordinario mantiene su función y revisión propia |
| LR04 | Divergencia anterior a ausencia, durante ausencia o posterior a observar reaparición, con/sin incremento de row_version | Admitir preparación si snapshot actual elegible y revisable; no exigir igualdad con target histórico de ausencia ni inferir autor/fecha |
| LR05 | Solo observación/ACCEPT/simulación de ausencia, recibo CONFLICT o cadena/ámbito/propuesta ajenos | No acreditan ausencia I8 aplicada para esta identidad materializada |
| LR06 | Versión producida por prueba diferente de cabeza vigente u otro efecto intermedio | Conflicto, sin buscar por fecha el recibo o restaurar versión |
| LR07 | Before histórico de ausencia diferente de última base de origen registrada | Conservar base/B reales de cabeza y sus hashes; no convertir fila histórica o texto local en base |
| LR08 | «Antes» actual distinto de observación que acreditó ausencia; cambios ajenos en documento | Permitir solo tras reconstruir ambos snapshots con mismo ID ausente y ámbito/perfil; fijar ambos |
| LR09 | CHANGED/UNCHANGED/ausencia, before presente, after ausente o diagnóstico bloqueante | Rechazar; solo ADDED ausente→presente real y no bloqueante |
| LR10 | SAME_SOURCE_ENTITY frente a ID distinto/reutilizado/no confirmado, para ambas elecciones | Declaración válida y razón requeridas; KEEP_LOCAL no exime ni libera clave |
| LR11 | Razones de identidad/resolución vacías, solo blancos Unicode, controles, exceso o tipos inválidos | Rechazar independientemente ambos campos; una razón no sustituye a la otra |
| LR12 | ACCEPT I5 ausente, revocado/reaceptado o pin obsoleto | Bloquear; la revisión conjunta no reemplaza la revisión de origen |
| LR13 | Referencia distinta, versión incorrecta o A→B→A | Conflicto sin avance implícito ni sustitución por referencia histórica de ausencia |
| LR14 | Solo aceptación I12/I14 anterior, dos aceptaciones de manifiestos diferentes o ACCEPT I5 | Insuficiente; una revisión propia del nuevo manifiesto completo es obligatoria |
| LR15 | Alterar prueba, declaración, razones, elección, B/L/S, destino, resultado o hashes | Manifiesto inmutable y reconstrucción verificable; nueva preparación/revisión, sin force o resultado libre |
| LR16 | Revisión conjunta ausente/REJECT, revocación/reaceptación o pin transferido | Sin aplicar; comando/hash/version exactos y ABA invalida pins anteriores |
| LR17 | ID largo, Unicode/Markdown/pipes, fila tachada, anotaciones y localizadores | Identidad/texto íntegros, evidencia literal sin normalizar o inferir aprobación |
| LR18 | Título local/origen inválido, descripción local NULL, Objective vacío/guion, claims DONE/Verified | Bloquear proyección inválida incluso KEEP_LOCAL; conservar NULL/strings y evidencia sin workflow |
| LR19 | USE_SOURCE con S distinto de L | PATCH solo title/description a S, row_version +1; fecha en D5 y resto conservado |
| LR20 | USE_SOURCE con S=L, aunque L sea distinto de B | Enlace/evidencia sin UPDATE tasks ni incremento de row_version |
| LR21 | KEEP_LOCAL con S distinto o igual a L/B | Conservar fila tasks íntegra; cabeza +1 con nueva base de origen y projection=S, resultado=L explícito |
| LR22 | Fila reaparece con S=B y L diferente | Ambas elecciones revisables: restaurar proyección origen o conservar pareja local completa, sin merge |
| LR23 | Editar título/description tras preparar con/sin versión, otros campos, estado/clave o convergencia observable | CAS/guards bloquean snapshot no revisado; ABA externo sin huella no se promete detectable |
| LR24 | Tarea no BACKLOG o con operaciones/planificación, incluso históricas/canceladas | Bloquear PATCH/enlace/KEEP_LOCAL; fixtures negativas revertidas, nunca ejecutadas |
| LR25 | Paquete explícito, duplicados/límites, mezcla I8/I10/I12/I14/I16 o selección automática | Lista ordenada de 1–2.000, una propuesta por intención y pins exactos; rechazar mezcla/descubrimiento implícito |
| LR26 | Dos paquetes o rutas compiten sobre misma cabeza; ausencia I8 posterior avanza versión | Sesiones reales, un avance ganador y conflicto del otro; prueba/cabeza viejas no recuperan vigencia |
| LR27 | Referencia o revisión cambia durante espera; locks cruzados D3/D5 | Espera observada, orden vigente y comprobación actual tras desbloqueo |
| LR28 | Fila inválida en paquete mixto, backend abortado o error tardío tras empezar efectos | Rollback íntegro de tarea/vínculo/cabeza/hecho/auditoría y recibo de éxito |
| LR29 | Replay, command_id reutilizado con otro contenido o mismo paquete con comando nuevo | Recibo histórico, conflicto o ALREADY_APPLIED; no restaurar texto, prueba o versiones |
| LR30 | Commit confirmado, respuesta perdida y reinicio | Recuperar mismo recibo sin repetir PATCH, vínculo o avance; CLI conserva esa semántica |
| LR31 | Vínculo después idéntico existente o FK/localizador/SourceRevision ajenos | Reutilización coherente o rechazo, procedencia append-only; ningún enlace a fila ausente ni afirmación de igualdad textual |
| LR32 | USE_SOURCE/convergencia y siguiente cambio I8; KEEP_LOCAL divergente y siguiente cambio I14 | Continuidad con base de origen nueva, revisiones propias y sin excepción permanente; sin fabricar cambio local aislado |
| LR33 | Nuevo ciclo ausencia/reaparición y revocación posterior de antigua revisión de ausencia | Exigir otra ausencia aplicada/versionada; revocar revisión histórica no deshace hecho ni autoriza ciclo nuevo |
| LR34 | Entradas I8/I12/I14/I16 existentes tras la variante nueva | Rechazos y funciones anteriores intactos: I12 bloquea divergencia, I14 solo CHANGED presente; no adopción implícita |
| LR35 | Roles, DML directo, READ COMMITTED, captura/digest D3 y snapshot publicado | Permisos mínimos y orden fijo; PATCH vuelve obsoleta captura de tarea, enlace/KEEP_LOCAL no escribe tarea y preserva snapshots |
| LR36 | Regresiones I4–I16, catálogo y fixtures BACKLOG finales | Cierres/funciones/ACL/evidencias preservados; cero tareas nuevas por resolución y cero operaciones/outbox/entregas/intentos/reservas finales |

LR04 debe incluir una tarea adoptada conservando texto local y casos en que el
recibo de ausencia ya lo mostraba o aún mostraba otro texto. No se altera ese
recibo para hacerlo coincidir con el target actual. LR07 evita sustituir la base
real de cabeza por before_basis histórico; LR08 mantiene ambas observaciones.
LR10/LR11 se prueban para USE_SOURCE y KEEP_LOCAL: conservar texto también aprueba
nueva evidencia de origen y exige identidad. LR14 no reutiliza ACCEPT I12/I14.

LR20/LR21 deben detectar cualquier UPDATE de tarea —por ejemplo con trigger
negativo—, no solo igualdad de valores finales; probar también convergencia L=S.
LR26/LR27/LR35 requieren sesiones simultáneas y espera observada, no solo llamadas
secuenciales. LR28/LR30 requieren transacciones reales, fallo/aborto y recuperación.
LR24 conserva A18 histórico: operación sintética solo en transacción negativa con
rollback obligatorio, nunca ejecutada y sin entregas o reservas persistentes.

LR32–LR34 llaman a entradas y adaptadores anteriores sin relajarlos. Se prueban
una continuación ordinaria y otra que conserva divergencia, seguidas de un nuevo
ciclo con prueba nueva y de replay histórico que no restaura estado. Una ausencia
I8 que gane una carrera puede conservar el texto local y avanzar cabeza; eso no
autoriza aplicar un paquete preparado con otra prueba/version anterior.

## Verificación documental de este corte

Se revisan prueba/cadena de ausencia V35, reconstrucción actual e histórica del
adaptador I12, cabeza/proyección y CAS de I14/V36, y continuidad de adopción I16/V37.
La propuesta preserva la base de origen frente al resultado local y permite
resolver la divergencia mediante una entrada propia con revisión conjunta.

Se comprueban enlaces, formato, publicación y hashes de cierres/campañas históricas.
No se modifican SQL, código, harness o documentos consumidos por pruebas; no se
inicia Docker ni se repiten campañas SQL. Ningún caso LR01–LR36 se declara PASS
mediante estas comprobaciones documentales.

Resultados del corte documental (2026-10-22):

- Scanner de publicación: 385 archivos de texto, sin patrones configurados;
  no sustituye la revisión del diff.
- 110 enlaces locales existentes y 36 casos únicos ordenados LR01–LR36.
- 245 entradas SHA-256 de cierres D3/D4 y documento canónico D4 intactos.
- Entradas históricas D5 I4/I5/I6: 20/27/47; I8/I10/I12/I14/I16:
  51/55/60/66/72, todos los hashes coinciden.
- 49 documentos, evidencias y propuestas SQL D5 anteriores coinciden con el
  inventario previo a este corte; `git diff --check` sin incidencias.

## Siguiente decisión

Revisar el contrato completo y, si se aprueba, autorizar por separado implementar
y validar LR01–LR36 en otro laboratorio V30 desechable con fixtures BACKLOG
sintéticas, separado de dev/D4. Publicación del diseño sobre commit concreto,
separada de esa aprobación. No se amplía activación, promoción, despliegue ni D6.

D5 sigue abierto: resolución local sin cambio revisable del origen, IDs reutilizados
para otra entidad, transferencias, adopción con procedencia/trabajo previos, cambios
de perfil/política, múltiples orígenes y Gentle-AI/routing completo conservan
pendientes. Proveedores y credenciales reales permanecen fuera.
