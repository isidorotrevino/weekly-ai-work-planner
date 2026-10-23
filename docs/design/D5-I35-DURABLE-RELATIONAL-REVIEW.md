# D5 I35 — matriz del recorrido relacional durable

Fecha: **2026-10-23**, Europe/Madrid.
[Contrato propuesto](D5-I35-DURABLE-RELATIONAL-DESIGN.md).
**DR01–DR40: DESIGN_NOT_EXECUTED; cero pruebas nuevas ejecutadas.**

English: proposed acceptance cases for durable relational batches and individually
reviewed TASK projections. No legacy volatile PASS or TASK-only restart implies
these cases have executed. No implementation or publication authorization.

R-CLIENT (C) y R-REMOTE (P) son almacenes nuevos; I30/T son referencias separadas.
UI25/UI34 enlazan las obligaciones integradas; GI33/GI34/GI40 exigen evidencia nueva.

| ID | Criterio / UI | Entrada, frontera o fallo | Oráculo exigido |
|---|---|---|---|
| DR01 | GI33 | Inventario R | Código/kernel/planner/esquemas/config/contrato/campaña ligados por hashes; versión declarada no acredita API real |
| DR02 | GI34 | Preservación y grupos | Código/SQL/harness I1–I34, cierres D1–D4 y A52 intactos; regresiones reales vs históricos por hash, sin sumas acumulativas |
| DR03 | GI38 / UI25 | Captura JSON I30 exacta | SHA de bytes originales/base64/localizadores; no recanonicalización de fuente ni parser Markdown I32 o captura Drive ficticia |
| DR04 | GI38 / UI25 | Campos extra/duplicados/UUID/tipo/ámbito/perfil inválidos | Bloqueo sin reparar ni entidades, vínculos o aceptación parcial |
| DR05 | GI38 / UI25 | Selección y SOURCE | Capturar no selecciona/aprueba; generación CAS, revisión propia y cambio A→B→A invalidan paquete antiguo |
| DR06 | GI38 / UI25 | Destinos e identidad | Mapping exacto fuente/tipo/proyecto, claves por tipo, sin adopción/renombre/conversión T↔R por UUID/nombre |
| DR07 | GI38 / UI25 | Tipos y claims | REQUIREMENT DRAFT, EPIC/TASK BACKLOG; description EPIC solo evidencia; null/empty TASK exactos; Status/Verified inertes |
| DR08 | GI38 / UI25 | Referencias y endpoints | Extremos tipados registrados o del lote; inexistentes/cross-project y capabilities bloquean sin prefijo |
| DR09 | GI38 / UI25 | Relaciones aditivas | EPIC_REQUIREMENT/TASK_EPIC/DEPENDENCY exactos; no-op conserva identidad; cambio de épica/kind/retirada bloqueados |
| DR10 | GI38 / UI25 | Grafo resultante | Ciclo HARD con aristas previas y varias nuevas bloquea todo; self-loop cualquier kind bloquea; otros kinds no se elevan a HARD |
| DR11 | GI39 / UI34 | Divergencia local previa | Base completa de entidad/versión/campos ajenos/relaciones de cada participante, incluido endpoint de lectura; todo lote bloqueado |
| DR12 | GI39 / UI34 | Guardas de trabajo/estado | Requisito/épica comprueban tareas relacionadas y flag histórico; no crear operaciones o reservas para negativos |
| DR13 | GI38 / UI25 | SOURCE/BATCH y revisiones ajenas | Versiones propias, aceptación íntegra; revocación/reemplazo invalida; aceptar otro paquete no altera datos ni sustituye su aprobación |
| DR14 | GI38 / UI25 | Publicación BATCH | Entidades+relaciones+mappings+bases+procedencia+recibo durables juntos; fallo previo ninguno, posterior recibo único sin replay de ACCEPT |
| DR15 | GI38 / UI25 | Versiones/no-op/procedencia | Row_version una vez por cambio real, base/cabeza una vez por participante, endpoint de lectura preserva source_base; generación avanza por lote |
| DR16 | GI38 / UI25 | Replay tras cambios posteriores | Mismo request devuelve hecho histórico; otro request bloquea; no rebobina cabeza, selección, relaciones o proyecciones |
| DR17 | GI38 / UI25 | Selección de TASK aplicada | Solo TASK participante de recibo exacto; manifiesto sin recibo/UUID ajeno/requisito/épica bloquea; selección no envía |
| DR18 | GI38 / UI25 | PROJECTION por TASK | Fija recibo BATCH, selección, snapshot y contexto exactos; aprobación de una no autoriza otra; sin EVALUATION Markdown ficticia |
| DR19 | GI39 / UI34 | Cambio local o relacional después de preparar | Incluso otro vínculo/no-op con nuevo lote invalida generación/hash completos; no enviar desde copia obsoleta o igualdad solo de payload |
| DR20 | GI39 / UI34 | Fuente/selección/revisiones ABA | Paquetes no emitidos bloquean; ticket ya emitido conserva efecto posible y STALE, sin rollback o aprobación transferida |
| DR21 | GI38 / UI25 | Múltiples TASK y envío parcial | A confirmada/B UNKNOWN conserva vector por TASK y lote local aplicado; no rollback compensatorio o éxito grupal ficticio |
| DR22 | GI38 / UI25 | Namespace/binding/payload remoto | Nuevo esquema R y clave estable; T rechazado/adopción bloqueada; solo name/description TASK, con null/empty preservados y campos ajenos intactos |
| DR23 | GI38 / UI25 | C caída antes/después de HEAD | Parametrizar BATCH, selección, PROJECTION, ISSUE, QUERY/RESULT: antes ninguno; después recibo/historia íntegros, huérfanos no se promueven |
| DR24 | GI38 / UI25 | fsync incierto C/P | COMMIT_UNKNOWN/RECOVERY_REQUIRED; reapertura valida/fsync antes de confirmar; error persistente no implica rollback o recibo confirmado |
| DR25 | GI38 / UI25 | Ticket C durable, caída antes de P | UNKNOWN al reabrir; sin autoenvío/lookup/cierre/retry; consulta vacía no prueba no efecto |
| DR26 | GI38 / UI25 | P efecto durable, respuesta perdida y C muerto | Proceso nuevo concilia ticket/identidad/hash exactos; un efecto y recibo histórico, sin duplicar tarea ni reenviar |
| DR27 | GI38 / UI25 | P crash CREATE/UPDATE/cierre | Parametrizar before_object/after_object/before_replace/after_head y fsync incierto; estado/prueba conjuntos, CLIENT independiente |
| DR28 | GI39 / UI34 | Execute frente a cierre | Procesos concurrentes confirman efecto o tombstone, nunca ambos; llegada tardía cerrada no ejecuta, también tras reinicio |
| DR29 | GI38 / UI25 | Prueba incompatible o múltiples destinos | CONFLICT persistente; no escoger por fecha ni borrar bloqueo con otro lote/paquete |
| DR30 | GI38 / UI25 | NO_EFFECT/rate limit/retry | Ticket nuevo solo con no efecto concluyente, mismo payload/clave/paquete, guardas/tick y presupuesto persistidos; precondición exige revisión/base nuevas |
| DR31 | GI39 / UI34 | Dos lotes mismo expected_head/datos | Solo uno confirma, otro conflicto sin prefijo ni rebase; revisiones/catálogos conservados |
| DR32 | GI39 / UI34 | Respuesta frente a conciliación y revocación | CAS ledger evita sobrescribir; prueba histórica y vigencia actual separados; conflicto/STALE no desaparece al consultar |
| DR33 | GI39 / UI34 | Cambio remoto antes/durante UPDATE, incluido ABA | Precondición atómica rechaza paquete; campos ajenos intactos; no retry ciego por GET/fecha |
| DR34 | GI39 / UI34 | Nuevo lote local con ticket previo UNKNOWN | Puede aplicar local si cumple guardas, conserva ticket conciliable/STALE y bloquea nuevo envío de ese binding; no restaura payload previo |
| DR35 | GI38 / UI25 | Corrupción/esquema/layout | HEAD/objeto/cadena/marca/IDs/symlink inválidos bloquean; no elegir padre, migrar T→R, crear génesis o reconstruir privados I30 |
| DR36 | GI33/GI38 | Comparación pública con I30 | Positivos y negativos de mapping/lote/grafo/no-op/guardas/procedencia comparados por API; diferencias durables/revisiones R declaradas, sin equivalencia total |
| DR37 | GI40 | Límites y margen pendiente | Conteos/bytes/historia/pruebas bloquean antes de efecto o emisión; otros escritores no consumen margen de resultados; presupuesto reducido etiquetado |
| DR38 | GI40 | Procesos, locks y limpieza | Spawn real, caída libera flock sin omitir CAS; lector independiente; todos hijos/hilos propios terminados y raíces propias eliminadas; sentinel intacto |
| DR39 | GI40 | Auditoría de autoridad/salida | Cero HTTP/SQL/SDK/CLI real, operaciones/intentos operativos, consumo/reservas/activación; salida sin texto/paths privados; fixtures negativas identificadas |
| DR40 | GI33/GI34/GI40 | Informe y exclusiones | Mapa DR/UI→tests realmente ejecutados, hashes de cada combinación, regresiones separadas; R relacional no se confunde con siete R reales ni cierra G01–G07 |

## Reglas de ejecución futura y lectura de cobertura

Cada prueba de crash debe usar otro proceso sin memoria heredada, control por
pipes/Event/barreras y SIGKILL solo tras señal del hijo propio. Lector de archivos
independiente del escritor verifica bytes/hash/cadena/HEAD, estados y conteos;
registrar rol, operación, punto, exitcode, HEAD antes/después y casos no ejecutados.
Fixtures y snapshots íntegros son privados; publicar solo códigos/hashes/contadores.

DR23/DR24 cubren commits CLIENT; DR27 cubre CREATE/UPDATE/cierre REMOTE. Un PASS
parcial no acredita toda la parametrización. UI25/UI34 exigen el recorrido R unido,
no sumar el PASS I30 en memoria y el T durable I34. R/I30/I34 y SQL/D1–D4 conservan
inputs/targets separados; filas/aserciones/subcasos no se suman como tests distintos.

Los 40 casos están **pendientes**. Seleccionar A autorizó el diseño, no su código.
La aprobación propuesta debe nombrar contrato, DR01–DR40, UI25/UI34 y alcance R
sintético durable con recursos propios. Alternativas: aprobar solo diseño o pedir
ajustes. P0 y exclusiones permanentes se conservan; D5 global/G01–G07 abiertos.
