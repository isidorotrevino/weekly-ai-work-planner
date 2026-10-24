# D5 I41 — contrato de carreras durables T/R

Fecha: **2026-10-24**, Europe/Madrid. **PREPARED_FOR_REVIEW**.
Base: `900e837edfdd97d0b85f1b8c8b455f5797f24fa0`.
[Decisión A](D5-I41-NEXT-CUT-SCOPE.md) ·
[HC01–HC24](D5-I41-DURABLE-CONCURRENCY-REVIEW.md) ·
[Hallazgos I40](../validation/D5-I40-results.md).

English: proposed bounded synthetic concurrency campaign, with forced process
orders, independent file oracles and separately registered future evidence.
No implementation, runtime test execution, publication or global closure yet.

## Autoridad y perímetro

El usuario eligió A para preparar contrato/matriz sobre H03 de I40. Esta elección
no autoriza código, hooks o campañas. Se propone un incremento I42 exclusivamente
de pruebas/harness/documentación nuevos sobre las APIs públicas T/R existentes.
El kernel durable, reducers, parsers, fachadas, tests/runners históricos y registro
fijo I38 se conservarán sin cambios. Si faltan puntos de control o aparece un
defecto que exige cambiar producto, registrar el bloqueo y volver al alcance;
no añadir hooks o corregir silenciosamente bajo esta propuesta.

Foco: **respuesta frente a resultado de consulta**, **respuesta frente a revocación
de PROJECTION**, y **EDIT frente a UPDATE** sobre una TASK existente, en T y R.
Relaciona GI39/UI30/UI31/UI32/UI33/UI34; inventario y contabilidad GI33/GI34 y
recursos GI40 propios. No satisface automáticamente ninguna UI/GI ni cierra H03
completo. R es recorrido relacional de fixture, distinto de los siete criterios
que exigen evidencia real.

Fuera: dos ISSUE/CREATE simultáneos, revocación SOURCE/EVALUATION/BATCH y cambios
de cuenta/perfil/origen concurrentes, variantes de grooming, las caídas H02 y
múltiples coincidencias/429 ambiguo H07. Se conservan como pendientes, junto con
raw histórico ausente H04 y contexto histórico parcial H05. No se reconstruye
evidencia I34/I36 ni se amplía A52/D5-LOCAL-SYNTHETIC-I1-I20.

P0 vigente: no publicación de I32, handoff o posteriores. D1–D4 cerrados; D5 global,
G01–G07 y los cinco criterios abiertos para revisión global; Docs y siete criterios
reales pendientes. Sin proveedores/credenciales reales, corpus privado, consumo/
reservas, operaciones, activación, promoción, despliegue o D6.

## Arquitectura de campaña propuesta

Archivos nuevos previstos: `testing/durable_concurrency/support.py`,
`test_durable_concurrency.py`, `run_concurrency_lab.py` y README en ese directorio;
documentos/resultados I42 nuevos. Se mantienen fuera del discovery `testing/D5`
y de `source_ingest`. El runner propio no sustituye ni modifica al auditor I38.
Inventaría código público y dependencias de setup, incluidos los helpers de T/R
reutilizados, además de sus archivos propios. No bastan las etiquetas de perfil.

Usar labs nuevos propios, APIs públicas `Client`, `Remote`, `Store.transact`,
constructores T/R y setup de fixtures existente. No restaurar `_head`, usar
`_candidate`, pickle o escribir HEAD/objetos de estado desde el harness. Las
respuestas retenidas por el harness son mensajes de transporte sintético y se
contrastan contra el ticket durable de REMOTE; no reconstruyen autoridad CLIENT
o aprobaciones. Se conserva configuración/identidad/revisión propia de cada modelo:
R no recibe EVALUATION Markdown ni captura I26 inventada.

Linux/filesystem local con flock/fsync/rename; procesos `spawn` independientes y
Pipe/Event para control. El reloj lógico no avanza por esperar o reiniciar. No
red, daemon, SQL, Docker o CLI de proveedor. Las llamadas son al doble local de
fixture, con CLIENT y REMOTE separados. Ningún control adquiere simultáneamente
locks de dominio de ambos almacenes.

## Estados iniciales e identidades fijadas

**L (ledger):** proyecto/documento y una TASK explícitos. Captura, revisión y efecto
T o lote/selección R aplicados; PROJECTION aprobada, send/ticket emitido durably en
UNKNOWN, ledger_version=1. REMOTE ya confirmó exactamente un efecto con prueba P.
CLIENT aún no publicó RESULT. La prueba retenida se verifica con el ticket real,
manifest/payload/creation_key/identidad/hash y snapshot independiente de REMOTE.
No volver a llamar EXECUTE para simular la respuesta tardía: no reenviar el ticket.

Para respuesta/consulta, un proceso Q usa **la fachada pública `reconcile`**:
confirma QUERY y observa P, se pausa antes de publicar RESULT. QUERY no aumenta
ledger_version; deja un query_id pendiente. El proceso D representa la respuesta
directa retenida: RESULT con P y query_id=None, para el pendiente send original.
Los dos se preparan con ledger_version=1 y la misma HEAD E posterior a QUERY.

**V (revocación):** mismo send/efecto posible o confirmado en REMOTE que L; revisión
PROJECTION actualmente ACCEPT versión 1. Compiten RESULT directo y REVIEW REVOKE
con expected_version=1. La revocación no cancela ticket emitido ni deshace el
efecto remoto. Solo se afirma vigencia STALE después de que REVOKE realmente
confirme; un comando que pierde por HEAD no ha revocado nada.

**U (update):** TASK ya creada/confirmada en REMOTE; binding y base exacta B de
entidad versión v, payload A y foreign sentinel. Preparar/aprobar un UPDATE cuyo
payload es distinto de la edición B propuesta por otro actor. Las bases de ambos
actores se fijan antes de competir. No rebasar automáticamente una edición sobre
la versión que produjo el otro actor.

Para fijar EDIT sin reread silencioso de `Remote.edit`, el harness puede usar
**`Remote.store.transact` público**, operación EDIT con los mismos campos cerrados
que construye la fachada: remote_id, expected_version=v, payload y foreign.
Declarar este uso en evidencia: se prueba el reducer/commit EDIT, no la selección
dinámica de versión de la fachada `Remote.edit`. UPDATE sí usa `Remote.execute`
con su manifiesto aprobado y base B. No modificación del reducer o evasión de CAS.

Cada escenario registra run/case/path T/R, actores/roles, IDs de almacén, TASK,
binding/send/ticket/manifiesto/revisión, hash de prueba/base/payload/contexto y
versiones esperadas. Texto sintético íntegro y paths temporales no se publican.

## Orden causal y evidencia de competencia

No sleeps, orden de arranque, duración o ganador aleatorio como oráculo. Ambos
procesos alcanzan READY tras preparar sus entradas y antes del intento de lock.
Usar los hooks **ya existentes** `before_lock`, `before_object`, `after_head`,
`after_query`, `before_result` con una máquina de control propia que identifica
operación y fase; no bloquear accidentalmente snapshots o commits de setup.

El padre libera al ganador elegido W. W se pausa en before_object sosteniendo
el lock, con transición calculada y todavía sin HEAD publicada. El contendiente
C, ya preparado, realiza una prueba no bloqueante sobre **ese lock propio**:
descriptor regular sin symlink, `flock(LOCK_EX|LOCK_NB)` debe devolver EWOULDBLOCK
o EAGAIN; cerrar descriptor. Publicar LOCK_HELD_OBSERVED y continuar su llamada
real. No usar el probe para escribir/ganar/saltar el protocolo. Solo tras recibir
ese evento se libera W. Una mera señal antes de flock no prueba espera efectiva.

El probe demuestra exclusión observada y entradas preparadas concurrentemente;
no se afirma que la instrucción flock bloqueante del producto ya se hubiera
ejecutado. Las dos ordenaciones se ensayan en escenarios nuevos, intercambiando
W/C. Una barrera simultánea sin ganador impuesto puede ser diagnóstica opcional,
pero no sustituye esas dos ordenaciones ni añade cobertura por azar.

Los hooks no toman decisiones de negocio ni cambian argumentos/estado. Un wrapper
de observación del transporte puede registrar el hash de la prueba devuelta por
lookup y devolverla idéntica; debe delegar a la fachada real y no fabricar P,
suprimir conflictos o resolver UNKNOWN. Los procesos se abren desde Store nuevo,
sin memoria de autoridad heredada del cliente padre.

## Resultados obligatorios: ledger y revisión

**D frente a Q:** ambos RESULT parten de E y ledger 1. W confirma; C falla
CONFLICT_HEAD porque E ya cambió. Estado final de esa ronda: ledger 2,
EFFECT_CONFIRMED, prueba P exacta, un efecto REMOTE y pendientes de ese send
consumidos. No interpretar CONFLICT_HEAD como prueba de CONFLICT_LEDGER.

Una fase explícita separada abre cliente nuevo y presenta el resultado viejo con
ledger 1 pero **HEAD fresca**: debe fallar CONFLICT_LEDGER sin modificar estado,
crear recibo o reenviar. Después, conciliación explícita nueva (QUERY/RESULT con
ledger vigente) conserva P, alcanza ledger 3 y no aumenta versiones/destinos de
REMOTE. Registrar rondas/comandos distintos; no retry automático del comando viejo.

**RESULT frente a REVOKE:** misma E, W confirma y C pierde CONFLICT_HEAD. Si gana
RESULT, hay efecto confirmado y revisión sigue ACCEPT hasta que una nueva acción
explícita confirme REVOKE con HEAD/review frescas. Si gana REVOKE, CLIENT sigue
UNKNOWN y STALE hasta una conciliación explícita nueva que acredite el efecto ya
existente en REMOTE. Tras esa acción posterior en ambos casos: EFFECT_CONFIRMED
histórico + STALE, revisión REVOKE versión 2, un efecto, sin restaurar payload,
aprobar otra proyección o enviar un ticket nuevo.

El acto posterior no disfraza el fracaso de C como éxito. Se registran separados
resultado de carrera, acción humana simulada posterior y resultado final. Negativo
de control: REVOKE antes de ISSUE bloquea la entrega sin crear send/ticket/efecto.

Prueba incompatible primero: una respuesta con identidad/hash alterado aceptada
como observación debe producir CONFLICT persistente. Una consulta posterior con
P correcto no borra hard_conflict ni habilita nuevo envío. El efecto ya registrado
en REMOTE permanece hecho histórico, no se adopta desde la prueba incompatible.

## Resultados obligatorios: EDIT frente a UPDATE

REMOTE serializa ambas operaciones bajo su lock; no usa expected_head de CLIENT.
No imponer que ambos actores confirmen. Se fijan estas ordenaciones:

| Ganador | EDIT con expected_version=v | UPDATE con base B | Estado comprobable |
|---|---|---|---|
| EDIT primero | Confirma payload de edición, versión v+1 | Ticket NO_EFFECT/REMOTE_PRECONDITION, retry_tick=None | Payload editado intacto; foreign preservado; solo EDIT cambia entidad |
| UPDATE primero | Falla REMOTE_CAS sin recibo ni cambio | Confirma P, payload proyectado, versión v+1 | Solo UPDATE cambia entidad; edición vieja no se rebasa |

En EDIT primero, el ticket NO_EFFECT también confirma historia REMOTE: HEAD avanza
dos commits (EDIT y resultado de UPDATE), pero entidad solo una versión. En UPDATE
primero, EDIT rechazado no confirma: HEAD avanza un commit, entidad una versión.
No confundir versiones de entidad, HEAD y tickets. CLIENT publica explícitamente
la prueba de UPDATE y comprueba que un rechazo por precondición no permite retry
del paquete viejo. Un futuro UPDATE necesitaría base/manifiesto/revisión nuevos.

ABA de control: dos EDIT explícitos vuelven al payload A pero suben a v+2 antes
de liberar UPDATE; este rechaza la base antigua. Registrar dos commits/versiones,
no fingir una edición atómica doble. Otro control cambia solo foreign: la base
completa queda obsoleta y UPDATE no debe borrar ese campo. No anunciar carrera
ABA simultánea o edición sin versión; son ordenaciones controladas específicas.

## Oráculos, evidencia y presupuesto

Lector propio de archivos, independiente de Store/reducer para leer/hashear
marker/HEAD/cadena/objetos/recibos/estado y contar entidades/tickets/pendientes.
Las assertions de resultado comparan P/base/versiones esperadas explícitas, no
el estado devuelto por el propio escritor como única verdad. Inspeccionar en
gates donde la HEAD es estable y después de terminar cada actor. Reapertura final
en proceso nuevo valida desde disco; no es prueba nueva de caída abrupta H02.

Campaña futura propia con raw stdout anclado, contexto Python/plataforma y
`sys.flags.optimize`/`__debug__`, hashes antes/después y conjunto de archivos
pertinentes. Assertions del lector deben estar habilitadas o ser comprobaciones
explícitas que no dependan de optimización; fallo de precondición = campaña inválida.
Etiquetar caso/recorrido/actor/rol/operación/modo/punto/orden/ronda y oráculo.
Eventos causales por pipe y ACK/gates, no timestamps como autoridad. Cualquier
secuencia incompleta/fallo/timeout se conserva como FAIL/NOT_RUN, no PASS parcial.

Límites propuestos del harness: un lab y TASK por escenario, dos actores en la
carrera y un lector de reapertura posterior; máximo cuatro hijos vivos por caso,
20 s por espera de control, 120 s por caso, 900 s por campaña de pruebas propias,
256 eventos/caso, salida raw 8 MiB y metadatos de evento 16 KiB. Sin ampliar límites
T/R/kernel, reservar cuota D3 o usar tiempo lógico como permiso de ejecución.
Timeout mata/espera solo hijos propios y registra el fallo; no se cuenta como caso
de recuperación satisfactorio. Probar negativas de control con presupuestos
reducidos y etiquetarlas, sin benchmark o máximos simultáneos.

Ownership/marker/inodos/sentinels y limpieza solo de temporales creados por el
harness. Cero procesos/hilos vivos o raíces propias restantes al terminar; fallos
de ownership/enlaces bloquean borrado y dejan residuo señalado. No inspeccionar
ni limpiar dev/run_data/D4 operativo o estado privado. Salida saneada sin fuente,
payload íntegro, paths temporales/home, credenciales o errores privados.

## Regresiones y aceptación futura del corte

Si se aprueba implementar, ejecutar HC01–HC24 y una campaña de las **321 regresiones
Python existentes**, separada mediante runner histórico sin modificar, capturando
su salida nueva como regresión de I42. No reemplazar informes I34/I36 o llamarla
su raw original. Sin SQL/Java/Docker o pruebas de proveedor. No prometer 345 tests
distintos hasta comprobar IDs/parametrización realmente ejecutados; filas HC,
rondas, eventos, probes y subcasos no son tests adicionales.

Los resultados futuros distinguirán cumplimiento acotado de HC, regresiones y
pendientes H03 no incluidos. Actualizar evaluación de suficiencia requerirá informe
nuevo con referencias, sin reescribir I40 ni cerrar GI39 por suma de PASS.

**Decisión pendiente A:** aprobar I41 e implementar/validar harness/casos HC01–HC24,
evidencia propia y regresiones Python separadas bajo estos límites, con todo el
producto histórico intacto. **B:** aprobar solo diseño. **C:** ajustar contrato/matriz.
En todas las opciones, P0 y las exclusiones permanentes continúan.
