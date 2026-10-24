# I42 — carreras durables sintéticas T/R

Implementación del [contrato I41](../../docs/design/D5-I41-DURABLE-CONCURRENCY-DESIGN.md)
y la [matriz HC01–HC24](../../docs/design/D5-I41-DURABLE-CONCURRENCY-REVIEW.md),
aprobados por selección A posterior al commit `cd97028`.

Desde la raíz, `python3 -B -m testing.durable_concurrency.run_concurrency_lab`
emite JSON raw propio. No escribe resultados históricos ni modifica producto,
suites/runners previos o registro I38. El runner exige optimización deshabilitada;
el lector independiente utiliza comprobaciones explícitas, incluso bajo `-O`.

HC01–HC12 fuerzan dos actores preparados y ambas ordenaciones en escenarios
separados. Ganador pausado bajo lock, contendiente comprueba EAGAIN/EWOULDBLOCK
con descriptor propio y después continúa su llamada real. No se afirma que la
llamada bloqueante ya comenzó. QUERY usa reconcile público, lookup observado y
RESULT real; EDIT usa Store.transact público con versión fijada. HC13–HC20 son
secuencias/negativas explícitas; HC21–HC24 validan controles, ownership, inventario
y contabilidad. Reapertura posterior desde otro proceso no demuestra SIGKILL.

Solo labs temporales propios y fixtures T/R. Recursos de campaña y regresiones
se contabilizan por separado. La regresión aprobada usa, sin modificarlo,
`python3 -B -m testing.D5.run_relational_durable_lab`; su stdout nuevo se conserva
como regresión I42, nunca como raw original I34/I36. Los 24 IDs HC no se suman a
subcasos, eventos, rondas o observaciones como tests adicionales.

Límites: 20 s/espera, 120 s/caso, 900 s/campaña propia; cuatro hijos vivos/caso,
256 eventos/caso, 16 KiB/evento, 8 MiB/raw. Las negativas de timeout usan un
presupuesto reducido de 0,02 s y terminan/esperan solo su hijo propio. El fallo
de ownership impide borrar y se señala como fallo/residuo. No inspecciona ni
limpia estado operativo. Los reportes públicos contienen IDs/hashes/conteos,
sin payload íntegro, paths temporales ni mensajes privados.

Persisten pendientes de H03 excluidos (doble ISSUE/CREATE, otras revocaciones,
cambios de cuenta/perfil/origen), H02, H07 y límites históricos H04/H05. P0,
D1–D4 cerrados, hito I1–I20 aceptado y D5 global/G01–G07 abiertos se conservan.
Sin proveedores/credenciales reales, consumo/reservas, activación, promoción,
despliegue o D6. Ningún PASS aislado acredita recuperación integrada o cierre GI.
