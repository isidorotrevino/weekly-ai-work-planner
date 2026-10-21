# D5 I15 — revisión de adopción y matriz de aceptación

Fecha: 2026-10-21. **Preparado para revisión; matriz todavía no ejecutada.**
[Contrato propuesto](D5-I15-ADOPTION-DESIGN.md). Base publicada: `b8ab72d`.
D5 abierto; D1–D4 cerrados; D6 pendiente.

English: acceptance matrix for a future disposable synthetic adoption lab.
Existing BACKLOG task data stays unchanged; correspondence and first direct
provenance are committed only with an approved package. No case passes by design.

A35 autoriza contrato/matriz. A36 limita a tareas sin trabajo/plan, correspondencia
D5 o task_sources previos. A37 conserva íntegra la tarea, A38 usa snapshot y revisión
propia y A39 materializa solo al aplicar. El resto del contrato es propuesta para
revisión, sin autorizar SQL, roles, tareas o laboratorio nuevos.

## Matriz futura — A01–A34

| Caso | Situación | Resultado exigido |
|---|---|---|
| A01 | Fuente y tarea existentes elegibles, IDs explícitos | Preparar manifiesto sin intención/cabeza/destino, task_sources ni escritura de tarea |
| A02 | Dos propuestas aceptadas para el mismo origen o tarea | Preparar/revisar no reserva; ninguna gana por fecha; un solo APPLY puede materializar |
| A03 | UUID/clave/proyecto/documento/perfil/política incorrectos | Rechazar sin búsqueda por título, similitud o creación de otra tarea |
| A04 | Intención D5 previa v0 o materializada, mismo origen con otro perfil, UUID o clave ya reservados | Bloquear adopción; no resetear, transferir ni reutilizar correspondencia |
| A05 | Tarea con task_sources previo, incluso idéntico al vínculo propuesto | Primera adopción bloqueada; no confundir con replay confirmado ni borrar evidencia |
| A06 | Tarea no BACKLOG, operación o planificación histórica/cancelada | Bloquear; fixtures negativas transitorias con rollback y sin ejecución |
| A07 | Fila única presente, IDs largos, Unicode/Markdown/pipes, tachado/anotación | Identidades completas, reconstrucción determinista y texto/evidencia literales |
| A08 | Fila ausente/duplicada o diagnóstico bloqueante en fila no seleccionada | Rechazar snapshot/selección; no reparar ambigüedad mediante selección parcial |
| A09 | Avisos compatibles, filas no seleccionadas o distinto perfil de referencia | Conservar avisos; no importar otras filas; perfil/observación exactos requeridos |
| A10 | Sin referencia, referencia distinta o A→B→A | Exigir selección previa explícita/version exacta; ningún avance implícito |
| A11 | Otra observación con iguales bytes; hashes de fuente/preview/fila/localizador incoherentes | No sustituir observación ni dominios de hash; rechazar artefacto ajeno/alterado |
| A12 | Item local/origen inválido, Objective vacío/guion, descripción local NULL | Bloquear título/proyección inválidos; conservar NULL y strings exactos sin normalización |
| A13 | Proyección local igual o diferente de la fuente | Adoptar sin UPDATE tasks en ambos casos; registrar S, L y resultado=L diferenciados |
| A14 | Campos locales ajenos a proyección, epic_id, fechas, urgencia y dependencias existentes | Conservar datos y asociaciones; no crear requisitos/épicas ni inferir dependencias |
| A15 | Status=DONE/Verified=approved o anotación afirmativa en origen | Evidencia solamente; tarea sigue BACKLOG sin transición, aprobación ni activación |
| A16 | Razón vacía/solo blancos Unicode, controles, longitud o tipos inválidos | Rechazar; declaración de asociación y revisión no sustituyen autenticación D6 |
| A17 | Alterar origen, destino, razón, snapshot o proyección después de preparar | Manifiesto inmutable; nueva preparación/revisión, sin force, PATCH o resultado libre |
| A18 | ACCEPT I5/I8/I10/I12/I14 sin revisión propia de adopción | Insuficiente; no fabricar comparación/decisiones ni before ficticio |
| A19 | Revisión propia ausente/REJECT, revocación o reaceptación | Sin aplicación; pins exactos por comando/hash/version, ABA invalida aceptación vieja |
| A20 | Paquete explícito, duplicados, límites, dos orígenes para tarea o mezcla de observaciones/variantes | Lista ordenada 1–2.000; una fuente y destino por propuesta, un snapshot/perfil; rechazar mezcla I8/I10/I12/I14 |
| A21 | Cambiar tarea tras preparar, con/sin aumento de row_version; ABA observable | CAS completo falla; no adoptar snapshot no revisado ni prometer detectar ABA sin huella |
| A22 | Otra adopción gana origen, tarea o clave tras preparar | Sesiones reales; un ganador y conflicto del otro sin apropiarse de la correspondencia ganadora |
| A23 | I8 reserva el mismo origen para otro destino antes de APPLY; antiguo registro intenta UUID existente | Reserva v0 invalida adopción; REGISTER_TASK_INTENT antiguo sigue rechazando tarea ocupada |
| A24 | Inserción task_sources concurrente, ambos órdenes respecto al lock de tarea | FOR UPDATE/FK y READ COMMITTED cierran carrera; detectar evidencia anterior sin ignorarla ni borrar vínculos |
| A25 | Referencia o revisión cambia mientras APPLY espera; locks D3/D5 cruzados | Espera observada y validación vigente tras desbloqueo; orden fijo sin inversión |
| A26 | Aplicación válida y FK de intención al comando real | Intención con proposed_intent_id revisado, destino, cabeza v1/S, procedencia, hecho/auditoría/recibo atómicos; cero INSERT/UPDATE/DELETE tasks |
| A27 | Una fila inválida en paquete mixto, error tras primeros efectos o backend abortado | Rollback íntegro de intención/destino/cabeza/vínculo/hecho/auditoría y recibo de éxito; no reserva parcial |
| A28 | Replay, command_id global reutilizado o mismo paquete con comando nuevo | Resultado histórico, conflicto de contenido o ALREADY_APPLIED; sin restauración ni segunda adopción |
| A29 | Commit confirmado, respuesta perdida y reinicio | Recuperar mismo recibo e intent_id sin duplicar correspondencia, procedencia o efectos |
| A30 | L=S y comparación real posterior I5/I8 | PATCH/enlace/ausencia bajo nuevas base/versiones y revisiones propias; tarea adoptada conserva UUID/clave |
| A31 | L distinto de S y cambio presente posterior, o sin cambio revisable | I8 bloquea; I14 permite resolución revisada sobre base adoptada si existe cambio real; no override ni comparación ficticia |
| A32 | Ausencia I8 aplicada y reaparición posterior I12, con/sin divergencia local | Mantener prueba aplicada/versionada e identidad declarada; edición local sigue bloqueando reaparición |
| A33 | Roles, DML directo, READ COMMITTED, digest de tarea/readset D3 y snapshots publicados | Permisos mínimos; ningún UPDATE de tarea; medir efectos de evidencia por separado y preservar snapshots, sin activar |
| A34 | Regresiones I4–I14 y catálogo previo; fixtures BACKLOG finales | Funciones/ACL/cierres/evidencias intactos, cero tareas creadas por adopción y cero operaciones/outbox/entregas/reservas/attempts finales |

A22–A25 exigen sesiones simultáneas, espera observada y estado tras desbloqueo;
no bastan llamadas secuenciales ni mocks. A24 debe probar un insert de procedencia
antes del lock de tarea y otro después, verificando la FK/bloqueo y el punto de
serialización, no una prohibición eterna de escrituras externas tras commit.
A23 reserva con otro destino nuevo, porque el registro I8 existente no permite
reservar directamente la tarea ocupada. A26/A33 deben detectar cualquier escritura
de tarea —por ejemplo con trigger negativo—, no solo igualdad de valores finales.

A27/A29 requieren transacciones reales y recuperación. A06 mantiene A18 histórico:
operación sintética solo en transacción negativa con rollback, nunca ejecutada,
sin entregas ni reservas. Ese permiso no autoriza dejar operaciones persistentes.
Los planes publicados son fixtures de propietario, sin despacho ni d3.publish.

A30–A32 usan entradas y adaptadores anteriores sin relajarlos. El nuevo intent_id
se enlaza al comando verdadero de preparación de adopción; no se cambia el historial
para aparentar REGISTER_TASK_INTENT. A31 comprueba que la cabeza mantiene la
proyección del origen y que I14 reconstruye la comparación desde esa base exacta.
A32 no equivale a resolver reaparición con edición local, que sigue pendiente.

## Verificación documental de este corte

Se contrastan identidad/correspondencia V33, procedencia inmutable V10, snapshot y
revisión de bootstrap V34, ausencia/reaparición V35 y separación origen/local V36.
La propuesta inicializa las mismas cabezas/destinos existentes con una entrada
propia, sin cambiar los rechazos de I8/I10 ni los dominios de hashes anteriores.

Se comprueban enlaces, formato, publicación y hashes de cierres y campañas
históricas. No cambian SQL, código, harness o documentos consumidos por pruebas;
no se inicia Docker ni se repiten baterías SQL por este corte documental.
Ningún caso A01–A34 se declara PASS mediante estas comprobaciones.

Resultado documental: 107 enlaces locales válidos, matriz A01–A34 completa y sin
duplicados, formato correcto y revisión de publicación sobre 376 archivos de texto
sin patrones configurados detectados. Coinciden 245 entradas de cierre D3/D4 y el
documento canónico D4, más las 20/27/47/51/55/60/66 entradas de ejecución de
I4/I5/I6/I8/I10/I12/I14. Los 43 documentos, propuestas SQL y evidencias D5 de la
base previa permanecen idénticos. Estas comprobaciones no validan adopción SQL.

## Siguiente decisión

Revisar el contrato completo y, si se aprueba, autorizar por separado implementar
y validar A01–A34 en otro laboratorio V30 desechable con fixtures BACKLOG sintéticas
existentes, sin operaciones de producto, separado de dev/D4. Preservar D1–D4,
manifiestos y evidencias, sin promoción, despliegue, activación o ampliación D6.
La publicación se solicita sobre el commit documental concreto una vez preparado.

D5 sigue abierto; adopción con trabajo/procedencia previa, transferencias de
correspondencia, IDs reutilizados para otra entidad, resolución local de reaparición
o sin cambio presente, perfil/política, múltiples orígenes y Gentle-AI/routing
completo conservan pendientes. Proveedores y credenciales reales siguen fuera.
