# D5 I45 — contrato de doble ISSUE/CREATE durable T/R

Fecha: **2026-10-24**, Europe/Madrid. **PREPARED_FOR_REVIEW**.
Base: `71d142898ecedb4f1c44fc89ecedaa5d31bb81f5`.
[Selección A](D5-I45-NEXT-CUT-SCOPE.md) ·
[Matriz IC01–IC30](D5-I45-DURABLE-ISSUE-CREATE-REVIEW.md) ·
[Sello](../validation/D5-I45-design-review.json).

La selección A autoriza este diseño, no implementar o ejecutar. Se propone I46
como harness y evidencia nuevos. Producto, suites/runners históricos, I42/I44,
registro fijo I38, handoff e informes previos permanecen intactos. Si falta un
hook o se necesita corregir producto, registrar el impedimento y volver al alcance.
No añadir hooks ni cambiar reducers/fachadas bajo esta propuesta.

## Alcance y autoridad

Objetivo acotado H03/GI39: duplicación de ISSUE en CLIENT y entrega CREATE en
REMOTE, con ambas ordenaciones forzadas. UI31/UI32/UI33 parciales y UI34 en R;
GI33/GI34/GI40 para inventario, contabilidad y recursos propios. No cierra H03,
UI/GI completas o revisión global. No representa capacidades de proveedor real.

P0 vigente: no publicar I32, handoff o posteriores. D1–D4 cerrados y hito
D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. D5 global/G01–G07 y revisión global
GI33/GI34/GI38/GI39/GI40 abiertos; sin promoción 30/35→35/35 o recuperación integrada
inferida de PASS aislados. Sin proveedores/credenciales reales, corpus privado,
consumo/reservas, operaciones, activación, promoción, despliegue o D6. Sin
inspección/limpieza de dev/run_data/D4 operativo.

Fuera: dos paquetes aprobados de payload distinto, cambios/revocaciones concurrentes
de SOURCE/EVALUATION/BATCH/cuenta/perfil/origen, grooming, UPDATE/CLOSE, nuevas caídas
H02, colección múltiple/429 ambiguo H07, energía/disco/NFS/Windows/caller hostil.
H03 restante y límites históricos H04/H05 no desaparecen al pasar estas filas.
No reconstruir raw I34/I36 ni reescribir I40/I42/I44.

## Archivos, preparación y entradas

Archivos nuevos previstos en `testing/durable_issue_create/`: `support.py`,
`test_durable_issue_create.py`, `run_issue_create_lab.py` y README; documentos y
resultados I46 nuevos. Fuera de discovery D5/HC/HF. Puede reutilizar sin modificar
el lector independiente y funciones puras de metadatos I42, y setup público T/R.
Control de competencia nuevo o reutilización explícita sin modificar los módulos
anteriores; el inventario debe incluir las dependencias realmente usadas.

Un lab y una TASK por escenario. T usa captura I26, revisiones SOURCE/EVALUATION/
EFFECT y binding propios. R usa JSON SOURCE/BATCH, aplicación del lote y selección
TASK desde su recibo exacto; no EVALUATION Markdown o revisión I32 ficticias.
En ambos, una PROJECTION CREATE M revisada ACCEPT v1, binding B y creation_key K
válidos; entidad remota aún inexistente. Payload, target, identidad de almacenes,
revisiones y capacidades se fijan antes de competir. No cambios de reloj lógico.

Solo APIs públicas Client.perform, Remote.execute/lookup, snapshot/summary,
Store.read_command y hooks existentes. No escritura de HEAD/objetos de estado,
restauración de autoridad, `_head`, `_candidate`, pickle, rebase, reparación o GC.
El padre puede retener M como mensaje sintético de transporte; eso no restaura
revisiones o concede permiso CLIENT para emitir otro ticket.

Cada actor identifica cid, args/expected/request hashes, send/ticket, M/payload/K,
rol/operación/modo/stage, ronda y orden. Para ISSUE, Client.perform admite cid y
expected fijados; no usar dispatch para suplantar el ticket/cid que esa fachada
genera internamente. Para CREATE, Remote.execute genera cid determinista: uuid5
del remote store_id y `EXECUTE + ticket + digest(M)`; registrar/contrastar contra
el comando y recibo durables, sin sustituir su generación. Remote.execute devuelve
la prueba, no el flag historical del recibo: distinguir igualdad de pruebas de
replay histórico mediante cadena/recibos/read_command independientes.

## Barreras y ambas ordenaciones

Linux local con spawn y Pipe/Event. Ambos actores preparan argumentos antes de
before_lock. Ganador elegido W confirma READY y se pausa en before_object con
lock del almacén objetivo, transición calculada y todavía sin HEAD nueva. C,
preparado, abre descriptor regular propio sin symlink y prueba flock no bloqueante:
EAGAIN/EWOULDBLOCK acredita LOCK_HELD_OBSERVED. Solo entonces liberar W y dejar que
C continúe su llamada pública real. No sleeps, orden de arranque o azar como prueba.

El probe no acredita que el flock bloqueante del producto ya se hubiera ejecutado.
No tomar locks CLIENT/REMOTE simultáneamente. Los hooks solo observan/detienen;
no modifican argumentos o decisiones de negocio. Ambos órdenes A→B y B→A se
ensayan en labs nuevos. No exigir before_object al perdedor: un replay histórico
o conflicto puede terminar antes de publicar; en dos tickets distintos el segundo
sí puede confirmar un recibo NO_EFFECT y requerir su gate de commit adicional.

Hooks existentes: before_lock de Store.transact, before_object y after_head de
Store._publish. Armar controles solo alrededor de la operación objetivo; el
snapshot previo de Client.perform no es el intento de ISSUE. Read_command y
lecturas de archivos se ejecutan después de terminar actores o en gates estables.
Gate equivocado/ausente, EOF, timeout, salida inesperada o orden incompleto son
FAIL/NOT_RUN, nunca PASS parcial. No se añaden puntos de crash en este corte.

## C — competencia ISSUE en CLIENT

Estado C: M revisada, sin send/ticket/pending y HEAD E común. Todos los ISSUE
usan review_version=1, capabilities exactas de M y retry=False. Variantes:

| Familia | Identidad de actores | Resultado de ronda competida |
|---|---|---|
| C1 exacta | mismo cid, mismos args/send/ticket/expected E | Uno confirma; otro devuelve recibo histórico idéntico (solo flag historical distinto); HEAD +1, un recibo |
| C2 órdenes distintas | cid/send/ticket distintos, mismo M/B y E | Uno confirma; otro CONFLICT_HEAD sin recibo |
| C3 cid distinto, negocio repetido | cid distintos, mismos args/send/ticket y E | Uno confirma; otro CONFLICT_HEAD sin recibo; no deduplicar solo por ticket |
| C4 colisión de comando | mismo cid y send, tickets distintos, mismo M y E | Uno confirma; otro COMMAND_CONFLICT por request hash distinto, antes de CAS; sin segundo recibo |

Los incrementos de commit/recibo se comparan con el baseline del setup: no
descartan sus recibos de preparación.

C1/C2/C3/C4 × T/R × dos órdenes = IC01–IC16. Al terminar cada ronda: un send,
una tentativa, un pendiente send, UNKNOWN/ledger 1/proof=None, revisiones/TASK/
generaciones intactas y REMOTE sin tickets/entidades. No contar los dos retornos
C1 como dos emisiones; no confundir COMMAND_CONFLICT con CONFLICT_HEAD.

C2/C3 tienen una ronda posterior explícita: mismo comando perdedor y args, pero
HEAD fresca y el mismo cid aún no confirmado. Esperar BINDING_UNRESOLVED (guardia
anterior a PACKAGE_COMMAND_CONFLICT/TICKET_EXISTS), sin nuevo recibo/send/ticket.
Registrar como petición nueva con request hash nuevo por expected distinto, no
replay exacto. C4 conserva COMMAND_CONFLICT al repetir la solicitud incompatible
con su expected original, sin cambiar nada; no rebautizarlo como conflicto HEAD.

Solo después se ejecuta explícitamente el **ticket ganador realmente emitido**
una vez en Remote.execute; una reconcile pública nueva en CLIENT observa P y
llega a EFFECT_CONFIRMED/ledger 2, sin segunda ejecución o ticket. Contar llamadas
locales lookup/execute aparte de remote_requests reales=0. Después, repetir el
comando ganador original con su cid/args/expected viejos debe devolver recibo
histórico UNKNOWN y conservar el estado actual EFFECT_CONFIRMED/ledger 2 y HEAD.
El recibo histórico no rebobina ledger, revisiones o payload ni autoriza reenvío.

## R — competencia CREATE en REMOTE

Estado R: un ISSUE válido ya confirmado en CLIENT, un único send/ticket T0,
UNKNOWN/ledger 1 y pendiente; M/K revisados y ningún efecto REMOTE. CLIENT no
se modifica durante la ronda REMOTE. Se distinguen dos autoridades:

**R1, entrega duplicada del ticket emitido:** dos actores ejecutan Remote.execute
con T0 y M idénticos. Mismo cid/request deterministas; ambos obtienen P idéntica,
pero HEAD/recibos/tickets REMOTE aumentan solo uno, una entidad versión 1 y payload
exacto. Read_command acredita el recibo histórico; no deducir su flag del retorno
de Remote.execute. Tras la carrera, reconcile nueva del send emitido confirma P,
ledger 2, consume pendientes y no llama execute/close. IC17–IC20 cubren T/R y
ambos órdenes. Este es el recorrido de entrega duplicada con ticket emitido.

**R2, tickets distintos para la misma creación:** T0 emitido y un ticket T1 extra
**no emitido por CLIENT**, ambos con M/K idénticos. Es control negativo de la
frontera REMOTE, no dos envíos autorizados ni prueba integrada de que CLIENT permite
emitir T1. CLIENT no lo emitirá y no se presentará T1 como autoridad de conciliación.
Ambos órdenes se prueban en IC21–IC24: el primero crea y confirma P; el segundo
confirma NO_EFFECT/CREATION_KEY_CONFLICT/retry_tick=None. HEAD/recibos/tickets
REMOTE +2, una entidad versión 1, mismo K/payload, sin adopción de otra entidad.

Si T1 gana, el efecto remoto pertenece al ticket no emitido; no publicarlo como
éxito del send T0 ni fabricar vínculo CLIENT. CLIENT permanece UNKNOWN/ledger 1
con T0 como única tentativa durante toda esta fila; **no hay reconcile final**
en R2. La fixture REMOTE no comprueba el ledger CLIENT al recibir el ticket:
una sola entidad no acredita autenticación de tickets o permisos reales. Las dos
pruebas terminales se contrastan con sus tickets exactos y se conservan como hechos
sintéticos del dominio REMOTE. Ninguna se intercambia por igualdad de payload/K.

## Negativas de identidad y solicitud

IC25/IC26 T/R: primero crear P con el ticket emitido y M correctos. Solo después,
control de paquete alterado copia M y cambia task.title y payload.name de forma
coherente con el esquema, manteniendo el mismo ticket/K. No tiene revisión o
permiso nuevos: es una entrada negativa, jamás ganador concurrente. Esperar
TICKET_CONFLICT por hash de M distinto, sin otro commit/recibo/efecto o adopción.
No sustituirlo por un error de forma que no ejercite conflicto de ticket.

IC27/IC28 T/R: desde M/ticket emitidos y REMOTE vacío, paquete negativo con K
incorrecta pero formato válido produce REMOTE_SCOPE antes de crear/confirmar nada.
Por separado, Store.read_command del ISSUE existente con request hash distinto
produce COMMAND_CONFLICT; con hash exacto devuelve su recibo histórico sin
activar nada. No se fabrica una segunda TASK o un K válido para otra identidad:
la independencia de dos creaciones válidas de targets distintos queda fuera.

IC25–IC28 son secuencias controladas, no carreras o nuevos permisos de publicación.
IC29/IC30 añaden controles transversales de protocolo, recursos, raw e inventario.

## Oráculos, recursos y evidencia

Lector independiente de archivos para marker/HEAD/hash/cadena/recibos, TASK,
sends/attempts/pending/ledger, tickets/K/entidad/version/payload hash y revisiones.
Contrastar contra entradas fijadas y ambos retornos, sin usar solo el estado del
escritor. Registrar la procedencia de T0 emitido y T1 no emitido. No mezclar
HEAD, versión de entidad, ledger_version, recibos y número de llamadas locales.
Un lector nuevo final y apertura pública pasiva comprueban estado desde disco
sin emitir, ejecutar, conciliar o revisar; no son evidencia de crash/energía.

Un lab/TASK por escenario; dos actores y lectores posteriores; máximo cuatro
hijos vivos/caso, 20 s/gate, 120 s/caso, 900 s/campaña propia, 256 eventos/caso,
16 KiB/evento, 8 MiB/raw (JSON compacto si procede). No ampliar límites T/R/kernel
o crear reservas D3. Negativas reducidas de timeout no se cuentan como caída de
recuperación. Ownership/inodos/markers/sentinels; enlaces o propiedad inválidos
impiden borrado y dejan fallo/residuo registrado. Cero procesos/hilos/raíces propios
restantes en éxito; solo limpieza propia, sin inspección operativa.

Raw stdout nuevo anclado, inventario pertinente pre/post incluyendo dependencias
reutilizadas y contrato; contexto Python/build/plataforma/optimize/__debug__, exigir
optimize=0 y checks explícitos del lector. Cada evento/oráculo registra caso/path/
actor/rol/operación/modo/stage/punto/orden/ronda e IDs/hashes/versiones. Sin payload
íntegro, paths temporales/privados, credenciales o errores privados. Input cambiado/
añadido, raw faltante/incompatible o control incompleto invalidan PASS.

## Validación propuesta y decisión posterior

Si se aprueba: implementar/validar IC01–IC30 y evidencia propia, y ejecutar en
campañas separadas los runners sin modificar de HC24 (I42), HF40 (I44) y Python321
históricas. Cuatro grupos con raw/contexto/pre-post nuevos, sin reescribir raws
originales. IC son filas previstas, no promesa de 30 tests ni suma automática de
filas, escenarios, actores, retornos, probes o regresiones como tests nuevos.
Sin SQL/Java/Docker o pruebas de proveedor.

Informar novedad por obligación: DF37 y controles previos de ticket ya cubrían
secuencias; los nuevos órdenes forzados no convierten cada repetición en laguna
inédita. Distinguir recorrido CLIENT→ticket emitido→REMOTE→reconcile de controles
solo REMOTE con ticket no emitido. R2 no sostiene una conclusión integrada.
Los resultados futuros emitirán referencias nuevas, FAIL/NOT_RUN y límites, sin
cierre automático de H03/GI39/D5. Este diseño emite cero resultados empíricos.
