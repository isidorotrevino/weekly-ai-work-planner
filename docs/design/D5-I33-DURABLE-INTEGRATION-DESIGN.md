# D5 I33-F — contrato durable sintético para revisión

Fecha: **2026-10-23**, Europe/Madrid. **PREPARED_FOR_REVIEW; no aprobado ni implementado.**
[Contrato de unión I33](D5-I33-INTEGRATED-EVIDENCE-DESIGN.md) ·
[Matriz DF01–DF48](D5-I33-DURABLE-INTEGRATION-REVIEW.md) ·
[Comprobaciones documentales](../validation/D5-I33-design-review.json).

English: proposed durable synthetic TASK integration on Linux local filesystem.
Separate capture, client and remote-fixture stores; atomic local state and receipt,
write-ahead dispatch tickets, independent remote effects and explicit recovery.
Design only. No real Plane/Drive capability, SQL/D2 persistence, activation or D6.

## Decisión y alcance concreto

Tras «P0 + A», el usuario eligió **«F»**: completar el diseño durable adicional y
su matriz antes de implementar. No aprueba este contrato resultante ni autoriza
código, ejecución o publicación. P0 conserva I32/handoff/propuesta sin publicar.

Este documento concreta F y prevalece sobre las obligaciones todavía abiertas de
almacenamiento en el borrador I33. Se propone un módulo/runner **nuevo** de fixture
Python estándar, tres almacenes Linux locales propios y procesos de prueba propios.
Recorrido **T** únicamente: evento Markdown sintético I26, perfil explícito
`task-register.v1`, una TASK elegida por source_key, fuente/evaluación/efecto local/
proyección revisados separadamente, CREATE/UPDATE en doble remoto y conciliación.
Hasta ocho escenarios independientes por campaña. No daemon, HTTP, SDK/CLI real,
SQL, Docker, migraciones, corpus privado, credenciales, dev/run_data ni D6.

El recorrido R relacional I30 y exportaciones Docs siguen DESIGN_NOT_EXECUTED.
No se incorporan requisitos/épicas/relaciones, adopción, resolución de divergencias,
borrado, conversión de perfil o proyección de workflow. D1–D4 cerrados y A52 aceptado
conservan sus contratos. D5 global y G01–G07 abiertos; los cinco S integrados y siete
R siguen pendientes. No hay PASS nuevo ni promesa de completitud global.

## Autoridad durable nueva y compatibilidad con referencias

I24/I28/I32 no tienen APIs de restauración. F no serializa objetos Python, no
pickle, no acceso a privados ni reproducción de comandos ACCEPT al arrancar.
El módulo nuevo implementaría un estado durable propio con namespace/esquemas
`d5.durable-task-fixture.v1`, revisiones y recibos nuevos. No los etiqueta como
recibos originales I24/I28/I32 o SQL. Reutiliza `build_observation`/parser existente
sin cambios. Los modelos anteriores siguen intactos como oráculos acotados.

La matriz exige comparar mismas entradas admitidas/negativas con modelos I24,
I28 e I32 para identidad/proyección, revisiones, cuota, CAS, UNKNOWN y replay;
las diferencias deliberadas (persistencia y cierre de ticket nuevo) se identifican.
No se afirma paridad completa por esos casos. F no llama `MemoryLab.apply_effect`
y guarda después una copia: **el estado nuevo es dueño del efecto local de fixture**.
El snapshot entregado al doble procede de su misma raíz/transacción durable.

I26 sigue siendo almacén de captura independiente, no outbox. El adaptador usa
`snapshot`/`inspect` para leer y verificar commit/evento alcanzables. Se conserva
el contenido exacto y grado dentro del almacén nuevo al importar, con hash y pin
commit/evento/ámbito. No se modifica I26 ni se reclama una transacción conjunta.
Un cursor posterior no acepta referencia ni sustituye el evento seleccionado.
Si cambia la selección explícita, avanza generación y exige revisión nueva. Si el
pin deja de ser verificable, bloquear nuevos efectos hasta restaurar prueba; jamás
elegir otra captura automáticamente. Recibos previos siguen siendo históricos.

## Esquemas y estado cerrado

Todos los objetos son JSON UTF-8 canónico, claves ordenadas, separadores compactos,
`ensure_ascii=False`, sin NaN/infinito, floats o claves duplicadas. UUID canónicos,
SHA-256 de 64 hex minúsculas, enteros (bool no equivale a entero), enums cerrados.
Reject de campos extra/esquema desconocido, rutas, comandos o blobs ejecutables.
Bytes fuente en base64 con round-trip exacto y SHA-256 verificado. Sin autocorrección,
normalización o truncamiento. Hash de objeto excluye su nombre/hash externo.

| Registro | Campos/obligaciones |
|---|---|
| Marca fija | schema, run_id, store_id UUID, role CAPTURE/CLIENT/REMOTE; marca no es autenticación |
| HEAD | schema, run_id, store_id, role, seq, commit_sha256; apunta solo a objeto del mismo almacén |
| Commit CLIENT/REMOTE | schema, run_id, store_id, role, seq, parent_sha256 o null en génesis, command_id, request_sha256, operation, state, receipt; sin hash propio |
| CLIENT state | clock_tick; generaciones de selección, perfil, política, cuenta y datos; capturas/manifiestos inmutables; revisiones por etapa; TASK/base aplicada/procedencia; bindings; comandos, intentos, consultas y conflictos; recibos e inventario de configuración |
| REMOTE state | capability descriptor/hash; TASK remotas y versiones; índice único creation_key→remote_id; tickets terminales con request hash/prueba o tombstone; reloj de fixture si procede |
| Manifest de etapa | identidad/bytes/perfil/grado, pins de revisiones y generaciones pertinentes, plan cerrado, snapshots/base local/remota, capacidades y payload; no incluye hash propio ni aprobación futura |
| Revisión | stage SOURCE/EVALUATION/EFFECT/PROJECTION, manifest hash, versión CAS, ACCEPT/REJECT/REVOKE, reason_code; namespace durable nuevo |
| Intento | command_id, manifest/request hash, binding, creation_key, attempt_id=ticket UUID, ordinal, base local/remota, versiones de revisiones y datos al emitir, ledger_version, status, proof/null |
| Recibo | command_id/request hash, resultado, versiones anteriores/posteriores y hashes, ticket/prueba cuando aplica, historical en vista; grants_execution_authority=false, consumo/reservas/activación cero |

Todas las identidades de scope (proyecto/documento/namespace/provider fixture) se
fijan en génesis. Un store_id no se cambia al reiniciar ni se adopta otro run por
nombre/ruta. State contiene los recibos para que efecto local y recibo se confirmen
juntos. Cadenas parent no añaden autoridad transferible ni firma criptográfica.
Cada mutación tiene command_id propio. Un envío lógico lleva además send_id estable
por manifest; retry/consulta/registro de respuesta usan command_id distintos y
referencian send_id + ticket/query_id y ledger_version. Así replay de una mutación
no inicia otro intento. Las fases internas llevan IDs deterministas de operación
y no reemplazan el request original.
Solicitudes CLIENT de mutación fijan expected_seq/head y versiones semánticas necesarias;
request hash incluye operación/argumentos/expectativas, excluye command_id. Buscar
command_id antes del CAS permite replay exacto incluso sobre una cabeza posterior;
otro request hash bloquea. Los comandos fallidos antes de commit no consumen ID.

## Layout, inicialización y protocolo de commit

Harness crea una raíz temporal propia 0700 con marcador y tres subraíces conocidas:
`capture/` (I26), `client/`, `remote/`. Un sentinel hermano sintético queda fuera.
No recibe rutas del usuario ni busca almacenes en dev/work/run_data. CLIENT/REMOTE
usan marca fija, `lock`, `head.json` y `objects/<sha256>.json`; temporales con UUID
propio. Abrir mediante descriptores de directorio, sin seguir symlinks; no reemplazar
marca o lock. Solo filesystem local Linux con rename atómico, fsync de archivo y
directorio, flock; NFS/Windows, disco/energía defectuosos y caller hostil excluidos.

Crear requiere ruta nueva y explícita del harness; escribir marca, lock y génesis
con fsync antes de devolver READY. Un directorio existente vacío, incompleto o sin
HEAD no se reinicializa. Un fallo de creación devuelve INITIALIZATION_INCOMPLETE;
conservar evidencia, limpiar solo mediante propietario/harness; crear otro run
nuevo no reclama recuperar el anterior. Apertura nunca llama create implícitamente.

Para CLIENT/REMOTE, todo escritor y lector que confirme recibos toma flock
**exclusivo** del lock fijo. Así lectores pueden completar fsync de recuperación.
Bajo lock: abrir/validar HEAD y cadena completa acotada hasta génesis, hashes,
roles/IDs/seq consecutivos y unicidad de comandos; verificar shapes, referencias,
revisiones y invariantes de estado/transiciones. No ejecutar comandos de la cadena.
Operaciones son un enum cerrado; validar transición determinista desde el padre.
No retroceder a un padre válido si HEAD u objeto alcanzable están corruptos.

Publicación de una mutación:

1. Resolver replay, validar expected_head/seq y guardas; construir nueva raíz state
   íntegra y recibo, incrementar seq. Las revisiones cambian su versión; datos y
   selecciones tienen generaciones separadas, incluso ABA. Otro ACCEPT no sustituye
   la versión fijada en un manifiesto ni invalida por sí mismo su propio contenido.
2. Escribir objeto temporal O_EXCL, fsync archivo, publicar nombre SHA por enlace
   exclusivo sin sobrescribir objeto; si existe exigir mismos bytes. Quitar temporal
   propio y fsync `objects/`. El objeto todavía no concede autoridad.
3. Escribir HEAD temporal O_EXCL y fsync archivo; `replace` atómico sobre HEAD;
   fsync directorio del almacén. Solo entonces confirmar recibo al llamante.
4. Liberar lock. No llamar a otro almacén mientras se retiene ese lock.

Fallo antes de replace conserva HEAD anterior; objeto/temporal huérfano no se
promueve. Tras replace pero sin fsync confirmado devolver COMMIT_UNKNOWN. Cualquier
error I/O de publicación deja el handle en RECOVERY_REQUIRED: sin otro write/envío
hasta reapertura validada. No afirmar rollback basándose en una excepción.

Reabrir valida la cabeza visible y cadena; fsync objetos y directorio antes de
confirmar recibos de esa cabeza. Si fallan, conservar COMMIT_UNKNOWN. Si HEAD válido
contiene command_id exacto, devolver su recibo histórico; si no, NOT_COMMITTED_AT_HEAD
bajo el modelo de crash de proceso y fsync descrito, sin inferir ausencia de efecto
remoto. Nunca confirmar candidato huérfano ni reconstruir HEAD por nombre/fecha.
No garbage collection/compactación/migración o reparación automática en este corte.

## Fuente, revisión y efecto local F1–F4

Importar F1 fija bytes I26 y namespace completo; no acepta fuente. SOURCE revisa
manifest/captura/perfil/selección exactos. Nueva versión de perfil/política exige
captura/preview/revisión propios; conserva y bloquea reutilización automática de
mappings anteriores (A73). Solo TASK explícita con source_key estable del registro;
checklist/narrativa/desconocido quedan preview/bloqueados. No crear épicas/requisitos.

EVALUATION F2 fija política y vector completo, cuenta única/scope, adaptador,
observaciones seleccionadas inmutables, generaciones y revisión SOURCE. Mantener
reglas A74/I31: todas las dimensiones/unidades/ventanas vigentes de la misma cuenta,
sin sumas/conversión; UNKNOWN/cero/caducado/revocado bloquean. Guardar evaluación no
consume ni reserva. Otro hecho/revocación/selección/política invalida la evaluación;
ABA no revive. Caducidad y horizonte se revalidan en cada efecto, no con replay.

Reloj lógico entero confiable del harness, persistido en CLIENT; `advance_clock`
es explícito, CAS y monótono. Reabrir conserva tick; no deriva tiempo de PID, mtime o
reloj monotónico nuevo. Una campaña que quiera simular tiempo transcurrido durante
parada avanza tick antes de evaluar/aplicar/enviar. Sin avance no afirma frescura
real tras espera: toda frescura es de fixture. Descriptores/versiones/observaciones
y revisiones se restauran como datos validados del esquema nuevo, no nuevos ACCEPT.

EFFECT F3 fija plan TASK y target UUID/key explícitos; title/description únicamente,
BACKLOG, sin estado operativo. CREATE exige identidad no usada; UPDATE exige mapping
propio y snapshot/version/base D5 actuales sin divergencia local, incluso campos
ajenos/guardas de trabajo. `has_work` solo fixture negativa, cero operaciones reales.
Ausencia no borra/cierra. Una transacción CLIENT confirma entidad, mapping,
procedencia/base aplicada, generaciones y recibo juntos. Falla antes → ninguno;
respuesta perdida → mismo recibo histórico, sin reaplicar ni restaurar texto.

PROJECTION F4 lee TASK de esa misma raíz; fija binding UUID, capabilities remotas,
whitelist name/description, base remota para UPDATE y revisión propia. Preparar/revisar
no envía. Edición posterior de fuente, revisiones, cuenta/política/observaciones,
TASK/base/binding o capacidad invalida por pins exactos. Identidad/base remota no
se elige por similitud/fecha; remoto editado requiere base/paquete/revisión nuevos.

## Emisión, doble remoto y conciliación F5–F7

No hay transacción distribuida CLIENT/REMOTE. Antes de emisión se toma snapshot de
capabilities remotas **sin lock CLIENT**; al ejecutar, REMOTE verifica ese hash otra
vez. CLIENT bajo su lock revalida todos los pins/estado/revisiones/reloj y límites.
Commit durable F5 crea ticket, consume un intento, fija request/payload/base y deja
status **UNKNOWN**, aunque todavía no se haya llamado al doble. Es el punto de
emisión/autorización de fixture; el emisor vivo puede usar ese ticket una sola vez
fuera del lock. Si el commit no se confirma, no llama al doble. Caer después puede
dejar UNKNOWN sin efecto: recuperación no reenvía el ticket.

Revocar antes de F5 bloquea. Revocar después de F5 no retira un ticket ya emitido;
puede existir efecto en vuelo y se registra por separado la vigencia STALE. Ni un
reinicio ni otro proceso obtiene permiso de envío leyendo el ledger. Duplicación
accidental del mismo ticket en el doble es idempotente, pero no es API de recuperación.
No leases de envío ni reasignación por timeout. Un binding UNKNOWN/CONFLICT bloquea
cualquier nueva escritura aunque cambie paquete/command_id.

REMOTE es un almacén durable **independiente**, abierto por procesos nuevos en cada
llamada local de fixture. El request de execute/lookup/settle_or_close fija ticket,
manifest/payload y capability hash; no incluye una HEAD remota efímera. El lock
REMOTE elige la HEAD actual y el CAS de TASK usa la base del manifest. IDs internos
de mutación se derivan por UUID5(store_id, operación + ticket + request_hash),
separando execute y cierre sin cambiar la identidad de ticket. Un replay consulta
primero el ticket terminal y nunca restaura el efecto. El descriptor de fixture
fija release/version/generación y booleanos create_unique, conditional_update,
effect_lookup y settle_or_close; desconocido/ausente bloquea. Cambiarlo es mutación
CAS y no borra tickets terminales ni genera permisos reales. No servidor/puerto/red. `execute(ticket, manifest)` toma
solo lock REMOTE y confirma atómicamente efecto + índice único + ticket/prueba:

- CREATE: creation_key estable de instancia fixture/workspace/proyecto remoto y
  proyecto/TASK local; no incluye contenido, comando o fecha. Unicidad atómica.
  No hay adopción de otro destino; identidad incompatible bloquea.
- UPDATE: destino previamente ligado, versión y hash base exactos, CAS; edición
  incluso A→B→A avanza versión. Conservar campos ajenos. Capacidades/hash distintos
  bloquean; GET seguido de UPDATE sin CAS no sirve.
- Mismo ticket y request devuelve prueba histórica, sin reaplicar. Otro request con
  ese ticket bloquea. Cada intento tiene su resultado terminal; rechazo concluyente
  registra NO_EFFECT y no cambia entidad. Timeout/error/respuesta parcial del cliente
  deja UNKNOWN hasta prueba; ningún código real HTTP se interpreta aquí.
- Confirmar prueba solo después de fsync del commit REMOTE. Caída tras efecto antes
  de respuesta se recupera de esa raíz, aunque se pierda por completo CLIENT vivo.

`lookup(ticket, request_hash)` devuelve prueba durable exacta o UNKNOWN. Cero
resultados/lectura eventual, destino ausente o ACK cliente no prueba no efecto.
Para el hueco F5 sin llamada, se propone una capacidad **nueva y solo de fixture**:
`settle_or_close(ticket, request_hash, creation_key, manifest_hash)` toma lock REMOTE.
Si ticket terminal existe devuelve su prueba exacta; si no existe, confirma tombstone
**CLOSED_NO_EFFECT**. Una ejecución tardía del mismo ticket recibe ese cierre y jamás
produce efecto. Si execute y close compiten, solo una transacción gana: efecto probado
o cierre probado. No se deduce capacidad equivalente de I28 ni de Plane real.
Esta operación requiere hash de capability admitida y no borra otros tickets/efectos.
No es cancelación/rollback de un efecto ya confirmado.

F7 `reconcile` hace una consulta explícita (lookup o settle_or_close), sin lock
CLIENT; luego CAS de ledger_version y registro durable de prueba/resultado/historia.
Identidad/ticket/request/correlation/remoto/hash de prueba incompatibles o múltiples
destinos → CONFLICT persistente. Una carrera que pierde CAS no sobreescribe: devolver
CONFLICT_LEDGER y permitir otra consulta explícita. El recibo anterior no se reescribe;
observaciones/pruebas nuevas se añaden y pueden señalar STALE por datos actuales.

Recuperación de arranque lista UNKNOWN/CONFLICT y recibos históricos; **no consulta,
no cierra, no reintenta ni envía automáticamente**. Llamada explícita reconcile puede
confirmar efecto o cierre, aunque se haya revocado la revisión: lectura/cierre de
un ticket histórico no otorga otra autorización. Un conflicto de identidad no se
elimina con otro paquete ni con una consulta posterior positiva.

Solo NO_EFFECT/CLOSED_NO_EFFECT concluyente de todos los intentos anteriores permite
retry explícito, nuevo ticket y mismas clave/payload/paquete, bajo guardas actuales
y presupuesto original. Antes de retry se comprueba tick mínimo si hubo rate limit
concluyente; dato faltante/inválido bloquea. Cambiar payload requiere paquete/revisión
nuevos y no borra UNKNOWN anterior. Presupuesto de tres intentos por manifiesto
persistido; un command_id nuevo no lo reinicia (un comando de envío por manifiesto).
Crear nuevos manifiestos no evita bloqueo por binding pendiente ni historial.

## Concurrencia, límites y limpieza

Toda mutación CLIENT pasa por commit CAS/puerta durable común, incluido cambio de
revisión, datos, selección y reloj. Snapshot copiado no reemplaza lectura del dueño.
Dos procesos con expected_head común: uno confirma, otro CONFLICT_HEAD; no rebase
silencioso. Si concurren revisión independiente y preparación, relectura explícita,
sin omitir versiones semánticas. Locks de CLIENT y REMOTE nunca se anidan entre sí
ni con I26. Pausas/barreras fuera de locks salvo failpoints de crash de commit.
La muerte del proceso libera flock; un timeout de lock no concede propiedad.

Límites por escenario: un proyecto/documento, ≤16 perfiles, ≤16 cuentas de fixture,
≤16 restricciones, ≤128 observaciones, ≤16 TASK/bindings, ≤128 comandos CLIENT,
≤128 revisiones totales y ≤128 manifests. Tres intentos por manifiesto, seis consultas
por comando de envío; consultas se consumen en commit CLIENT **antes** de salir al
doble, incluso si respuesta/CAS se pierde. Intentos/tombstones remotos ≤384; entidades
remotas ≤16. Fuente ≤2 MiB, texto ≤8.192 caracteres/campo, manifest/unión ≤1 MiB,
state/commit canónico ≤32 MiB, ≤256 commits por CLIENT/REMOTE incluidos génesis,
y ≤256 MiB de archivos por almacén incluyendo huérfanos/temporales propios. También
rigen límites I26 y parser existentes. Exceder cualquier límite bloquea sin truncar.
Margen lógico para respuesta: al emitir intento/consulta se debe probar
que caben **dos commits** (emisión y resultado), slot de recibo y máximo de prueba
≤64 KiB. State contabiliza el margen de **todos** los resultados pendientes; toda
otra mutación debe preservarlo y solo el resultado correspondiente lo libera.
No son reservas de cuota/capacidad D3. Si no cabe, bloquear antes de emitir.
Fallo físico de disco sigue siendo UNKNOWN.
No borrar historial para liberar presupuesto; una raíz nueva no recupera la anterior.

Harness mantiene inventario de raíces/store_id, hijos/PID propios y hilos. Control
por pipes/Event y failpoints de enum cerrado, nunca instrucciones de fuente. Matar
solo PID propio esperando señal exacta; terminar/join y comprobar exitcodes. Crash
CLIENT deja REMOTE y CAPTURE intactos; crash REMOTE deja CLIENT UNKNOWN. Auditoría
cuenta effects/tickets fixture separados de cero operaciones/intentos operativos,
consumo/reservas/activación, permisos de ejecución y solicitudes reales.

Limpieza explícita del harness tras conservar evidencia saneada: cerrar handles,
terminar hijos propios, verificar marca/IDs/path dentro de raíz creada, rechazar
symlink/propiedad incoherente y borrar solo sus tres subraíces/raíz. Sentinel hermano
permanece. Si validación falla, informar residuo y no borrar por heurística. Jamás
prune global, tocar dev/D4 o publicar capturas/inspect/logs crudos. Resultado público
solo códigos, hashes, counts y mapa casos/inputs; no rutas privadas ni texto fuente.

## Evidencia y aprobación pendiente

[DF01–DF48](D5-I33-DURABLE-INTEGRATION-REVIEW.md) concreta failpoints, procesos,
oráculos e invariantes. Incluye los 33 UI de base como obligaciones aplicables a F;
los cinco UI durables se desglosan y los dos R siguen fuera. No sumar UI+DF como
pruebas distintas sin IDs ejecutados. Regresiones I24/I26/I28/I30/I32 se contabilizan
separadas; SQL/D2–D4 históricos no son nuevas ejecuciones por verificar sus hashes.

Este diseño no prueba persistencia por sí mismo, exactly-once externo, seguridad
frente al propietario hostil, pérdida de energía/disco o frescura comercial real.
El cierre atómico es capacidad inventada y explícita del doble; GI18 y GI42 reales
siguen pendientes, junto al resto de siete R. Implementar/validar solo T no cierra
GI38/GI39 globales ni G01–G07 automáticamente; revisar exclusiones R/exportaciones.

Puerta concreta: aprobar I33 + este contrato F y autorizar, si se desea, implementar
y validar **T durable, 33 UI aplicables y DF01–DF48**, con modelos históricos intactos,
parser existente, nuevos recursos temporales/hijos propios y regresiones Python
separadas. Alternativa: aprobar solo diseño o pedir ajustes. Ninguna opción publica
I32/handoff/diseño, promueve migraciones, despliega o inicia D6.
