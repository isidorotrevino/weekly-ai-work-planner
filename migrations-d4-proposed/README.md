# Propuestas D4, aisladas de D2/D3

V16 añade entrega durable y acciones de worker restringidas sobre `d3.dispatch`
y `d3.execution`. No cambia V1–V15, no promueve migraciones ni crea LOGIN reales.
Su harness usa las siete ubicaciones explícitas y prueba upgrade V15→V16.

V17 añade sobres de comandos de transporte, polling elegido por el servidor,
presencia sin autoalta de capacidades y consulta de recibos propios. El grupo I1
conserva target V16; el grupo HTTPS usa V17 y comprueba upgrade V16→V17 con entrega
activa. Runtime recibe únicamente los entrypoints de transporte, no d4.deliver.

La identidad `principal_worker` procede del adaptador mTLS de confianza. Solo el
control plane recibe EXECUTE; un worker remoto nunca recibe conexión SQL. Esta
propuesta no acredita por sí misma autenticación HTTPS, veracidad de capacidades,
grants de efecto, checkpoints o verificación independiente.

Un ACK confirma recepción. Una respuesta guardada, incluido START, es un recibo
histórico; nunca autorización nueva para un proceso o efecto. Un CLAIM confirmado
con respuesta perdida se recupera por asignación vigente o reentrega, sin otro
intento/reserva. Las renovaciones mantienen íntegra la guarda D3 de 60 s.

La configuración del catálogo y los LOGIN sintéticos pertenecen al bootstrap del
laboratorio; no son APIs para autoalta desde workers. No se modifica el descubrimiento
de migraciones histórico D2. La continuidad sigue pendiente de decisión/revisión.

V26 propuesta añade resolución monotónica append-only del mismo receptor,
checkpoint de recuperación desde RECONCILING/BLOCKED_APPROVAL y recuperación
terminal v1/v2 con aceptación separada, bajo A17–A19. Su derivación estática se
comprueba con `python3 testing/D4/generate-recovery-admission.py --check`.
V1–V25 e informes anteriores permanecen intactos. Alcance y límites en
[I9](../docs/design/D4-I9-RECONCILIATION-LAB.md); sin promoción ni cierre D4.

V27 propuesta implementa A20: sello de ausencia sin pasos nuevos aplicados,
RETRY_PENDING, autorización explícita y nueva generación en la misma reserva.
Derivación: `python3 testing/D4/generate-absence-admission.py --check`.
Conserva V1–V26 y sus generadores. A21/A22 siguen pendientes de integración; el
borrador `testing/D4/sql/review-core.sql` no se aplica.
