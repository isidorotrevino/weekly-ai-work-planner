# I46 — competencia ISSUE/CREATE sintética T/R

Implementa el [contrato I45](../../docs/design/D5-I45-DURABLE-ISSUE-CREATE-DESIGN.md)
y la [matriz IC01–IC30](../../docs/design/D5-I45-DURABLE-ISSUE-CREATE-REVIEW.md),
aprobados por selección A posterior al commit `7af5362`.

Comando propio desde la raíz:
`python3 -B -m testing.durable_issue_create.run_issue_create_lab`.
Stdout es raw JSON compacto nuevo, con hashes pre/post y contexto de ejecución.
Usa setup T/R y lector/checks puros I42 sin modificarlos. El control spawn/Pipe es
propio, con READY antes del lock, ganador en before_object, probe no bloqueante
del contendiente y liberación causal. El probe no afirma que el flock bloqueante
del producto ya comenzó. Histórico o conflicto no requieren otro before_object;
los dos tickets distintos sí pueden confirmar recibos de resultados distintos.

IC01–IC16: cuatro familias CLIENT, T/R y dos órdenes. Misma solicitud/cid devuelve
historia; cid distintos compiten por HEAD; mismo cid con args distintos rechaza
COMMAND_CONFLICT antes de CAS. La petición posterior con HEAD fresca queda
separada del replay exacto y exige BINDING_UNRESOLVED. Solo el ticket ganador
emitido se ejecuta explícitamente y se concilia; recuperar luego el recibo ISSUE
UNKNOWN no rebobina el ledger EFFECT_CONFIRMED/2.

IC17–IC20: entrega duplicada del único ticket emitido. Dos pruebas iguales, un
commit/recibo/ticket/entidad remotos; read_command verifica el recibo histórico
sin inventar un flag en la fachada execute. Conciliación posterior usa lookup,
sin execute. IC21–IC24 son **solo controles REMOTE**: T0 emitido y T1 extra nunca
emitido por CLIENT. Si gana T1, su efecto no se adopta por CLIENT. No hay
reconcile en esas filas y CLIENT permanece UNKNOWN/1 con única tentativa T0.
Una entidad única no acredita autenticación o dos envíos autorizados.

IC25–IC28: paquete mutado después de creación válida, K falsa y request hash
incorrecto; negativas seriales sin revisión nueva ni competencia de permisos.
IC29/IC30: protocolo, EOF/salida/timeout, ownership/inodos/markers/sentinels/enlaces,
inventario/raw/contabilidad y límites. Timeout negativo mata solo su hijo y no
cuenta como recuperación. Lector nuevo y apertura pública pasiva final no emiten,
ejecutan o concilian. Todo recurso/limpieza es propio; no inspección operativa.

Límites: 20 s/espera, 120 s/caso, 900 s/campaña propia; cuatro hijos vivos/caso,
256 eventos/caso, 16 KiB/evento, 8 MiB/raw; optimize=0 y lector con checks explícitos.
Regresiones en campañas separadas, runners intactos y raw/contexto nuevos:
`python3 -B -m testing.durable_concurrency.run_concurrency_lab` (24 HC),
`python3 -B -m testing.durable_crash_boundaries.run_crash_boundaries_lab` (40 HF),
`python3 -B -m testing.D5.run_relational_durable_lab` (321 Python existentes).
No sumar actores, retornos, escenarios o controles como tests nuevos.

P0 y cierres/hito aceptado se conservan; D5 global/G01–G07 y revisión global GI
abiertos. Fuera: otros paquetes/targets/modos, revocaciones/cuenta/perfil/origen,
grooming, nuevas caídas H02, H07 y límites históricos H04/H05, energía/disco/
NFS/Windows/caller hostil. No inferir persistencia o recuperación integrada de
PASS aislados. Sin proveedores/credenciales reales, consumo/reservas, activación,
promoción, despliegue, SQL/Java/Docker o D6. No modifica producto o evidencia previa.
