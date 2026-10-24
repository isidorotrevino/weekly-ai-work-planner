# D5 I52 — laboratorio de revocación durante llamada remota

Fecha: **2026-10-24**. I51 aprobado mediante A; base
`21cbfe03342dfaf43b4707d87a7c4a0cd4ba0f98`.
[Contrato](D5-I51-INFLIGHT-REVOCATION-DESIGN.md) ·
[Matriz](D5-I51-INFLIGHT-REVOCATION-REVIEW.md) ·
[Resultados](../validation/D5-I52-results.md) ·
[CP01/CP05 preparado](../validation/D5-I52-CP01-CP05-preparation.md).

Implementación sólo en testing/durable_inflight_revocation/; sin cambios a
producto, APIs, modelo, módulos/harness anteriores o evidencia histórica.
Ejecutar desde raíz:
`python3 -B -m testing.durable_inflight_revocation.run_inflight_revocation_lab`.
El stdout JSON conserva la campaña RV20; las cinco regresiones tienen raw/contexto
separados y no se suman como tests nuevos o evidencia integrada global.

Remote.execute real se pausa dentro de Store._publish before_object/after_head.
Otro proceso confirma CLIENT REVIEW REVOKE v2, sin consultar REMOTE bajo su lock.
El padre verifica estado/recibo con lector independiente, luego libera mediante
ACK vinculado a cid/ticket. Después de respuesta/RESULT, la summary pública muestra
STALE; pérdida OSError conserva UNKNOWN hasta una reconcile explícita por lookup.
Los pins de autoridad T (I26/revisiones) y R (SOURCE/BATCH/selección/recibo) están
registrados por caso. La revocación no deshace el efecto ni autoriza reenviar.

Veinte casos, doce intercalados en vuelo, dos kills de timeout negativo: no nuevas
fronteras de recuperación ni prueba de energía/disco/host. Raíces/sentinels e hijos
son propios y se limpian selectivamente. No tocar dev/run_data/D4 operativo.
D1–D4/A52 preservados; D5/G01–G07 y revisión global de los cinco GI siguen abiertos.
Sin proveedor/credencial/corpus real, consumo/reservas, activación, promoción,
despliegue, publicación ni D6. La solicitud de push anterior sigue separada y
bloqueada por revisión automática a la espera de confirmación inequívoca.
