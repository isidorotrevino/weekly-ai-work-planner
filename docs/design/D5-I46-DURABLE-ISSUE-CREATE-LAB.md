# D5 I46 — laboratorio de doble ISSUE/CREATE T/R

Fecha: **2026-10-24**, Europe/Madrid. Implementa el
[contrato I45](D5-I45-DURABLE-ISSUE-CREATE-DESIGN.md) y la
[matriz IC01–IC30](D5-I45-DURABLE-ISSUE-CREATE-REVIEW.md), aprobados mediante
selección A del usuario posterior a `7af5362f2aad0513ccd2a655aa212a5e731eae54`.
[Harness](../../testing/durable_issue_create/README.md) ·
[Resultados](../validation/D5-I46-results.md).

Solo añade harness/documentos/evidencia I46. Producto, suites/runners anteriores,
I42/I44, registro fijo I38, handoff e informes previos se conservan sin cambios.
La aprobación no autoriza publicación ni cambia P0.

## Órdenes y autoridades

Dos procesos spawn abren las fachadas correspondientes. Ambos preparan entradas
antes de before_lock; el ganador se detiene en before_object bajo lock. El
contendiente observa ese lock con descriptor propio y flock no bloqueante, y solo
después se libera el commit. Se fuerzan A→B y B→A en labs independientes. Un
replay histórico/conflicto puede terminar sin segundo before_object; R2 requiere
el segundo commit de recibo NO_EFFECT. El probe no acredita que el flock bloqueante
del producto ya se hubiera ejecutado. No hay locks CLIENT/REMOTE simultáneos.

IC01–IC16 prueban cuatro familias CLIENT: misma orden exacta, órdenes distintas,
negocio repetido con cid distinto y colisión de cid con request diferente. Separan
CONFLICT_HEAD, COMMAND_CONFLICT y petición posterior con HEAD fresca rechazada por
BINDING_UNRESOLVED. Solo se ejecuta el ticket ganador emitido; reconcile posterior
confirma P con lookup=1/execute=0. El replay del ISSUE viejo devuelve su recibo
UNKNOWN histórico sin cambiar el ledger actual EFFECT_CONFIRMED/2.

IC17–IC20 duplican la entrega del único ticket emitido: dos retornos de P, un
commit/recibo/ticket/entidad remotos. El cid determinista de execute se contrasta
con cadena/recibos/read_command; la fachada no devuelve un flag historical y no
se le atribuye uno. Conciliación explícita posterior conserva efecto/versión y
no ejecuta ni cierra otro ticket.

IC21–IC24 son controles únicamente REMOTE: A lleva T0 emitido, B T1 extra nunca
emitido por CLIENT. Ambos órdenes dejan una entidad versión 1 y dos pruebas por
ticket: EFFECT_CONFIRMED y NO_EFFECT/CREATION_KEY_CONFLICT. Si gana T1, su efecto
no se adopta ni se concilia en CLIENT. CLIENT conserva UNKNOWN/ledger 1 y única
tentativa T0, aun cuando T0 sea ganador. Estas filas no demuestran dos emisiones
autorizadas, autenticación de tickets o recuperación integrada.

IC25–IC28 son negativas seriales posteriores a preparación válida: paquete mutado
sin revisión nueva, K falsa y request hash incorrecto. No participan como ganadores
concurrentes ni crean autoridad. IC29/IC30 prueban protocolo, propiedad, inventario,
raw y conteos. Una lectura independiente nueva y una apertura pública pasiva al
final de cada escenario no emiten, ejecutan o concilian. No equivalen a SIGKILL.

## Ejecución, evidencia y límites

Comando propio:
`python3 -B -m testing.durable_issue_create.run_issue_create_lab`.
Raw JSON compacto con pre/post hashes de dependencias reales, contrato y fixture;
contexto Python/build/plataforma/optimize/__debug__, optimize=0 y lector con checks
explícitos. Los oráculos registran HEAD/recibos/ledger/tickets/K/entidad/versiones,
TASK/revisiones y hashes, separados de llamadas locales lookup/execute y de
remote_requests reales=0. Sin payload íntegro o paths privados en los informes.

Regresiones separadas y runners sin modificar: HC24 de I42, HF40 de I44 y
Python321 históricas. Cada grupo conserva raw/contexto/pre-post nuevos; no se
reemplaza el raw original de otra campaña. Actores, retornos, filas y escenarios
no se suman como tests adicionales. Se señalan los controles ya presentes de
DF37 y las diferencias entre fronteras CLIENT/REMOTE.

Presupuestos del contrato: un lab/TASK por escenario, cuatro hijos vivos/caso,
20 s/espera, 120 s/caso, 900 s/campaña propia, 256 eventos/caso, 16 KiB/evento y
8 MiB/raw. Limpieza/ownership/inodos/markers/sentinels solo propios; propiedad o
enlaces inválidos impiden borrado y hacen fallar con residuo señalado. Timeouts
negativos matan/esperan solo su hijo; no se cuentan como recuperación. Sin
inspección/limpieza del host operativo o dev/run_data/D4.

Fuera: paquetes aprobados distintos, dos targets válidos distintos, otros modos,
otras revocaciones/cuenta/perfil/origen/grooming, nuevas caídas H02, H07 y límites
históricos H04/H05; energía/disco/NFS/Windows/caller hostil. Raw I34/I36 original
sigue NOT_RECORDED. D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos.
D5 global/G01–G07 y revisión global de los cinco GI abiertos, sin promoción
30/35→35/35 ni cierre H03/GI39 por suma de PASS. P0 sigue vigente. Sin proveedores/
credenciales reales, corpus privado, consumo/reservas, activación, promoción,
despliegue, SQL/Java/Docker o D6.
