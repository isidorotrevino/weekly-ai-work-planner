# Después de I91 — propuesta I92 pendiente de decisión

Fecha:2026-10-27, Europe/Madrid. **PREPARED_NOT_AUTHORIZED_NOT_EXECUTED**.
[Resultado I91](../validation/D5-I91-results.md) ·
[Pins y presupuesto de preparación](../validation/D5-I91-next-capture-proposal.json).

I91 tiene NS01–NS12 **12/12 PASS sólo en componentes**, en0,82s externos.
Se propone I92: **P01 completo321 tests/12 grupos, una ejecución bajo900s externos,
sin reintentos automáticos ni publicación**. La aprobación I91 no la autoriza.
No se crearon autoridad, destino, launcher, canales o procesos funcionales I92.

El inventario candidato contiene **292 pins y 63,070,664 bytes únicos**,
incluidos los contratos heredados realmente leídos por read_registry y los once
artefactos/sello I91. No es la unión de los574 inputs documentales ni una
atribución de archivos ejecutados. Los hashes actuales coinciden.
El Reader estático acumulado quedó en **214,003,650 bytes leídos**, dentro de
128/256MiB; el JSON registra el ámbito. No incluye autoridad todavía inexistente
ni lecturas futuras por caso del worker. **No demuestra capacidad/presupuesto
final de una captura321/12**; mantiene cuotas exactas, sin recortar evidencia.

Sólo tras decisión expresa se crearía `docs/validation/D5-I92-capture-authorization.json`, schema
`d5.selector-capture-authority.v1`, fase `I92_EXPLICITLY_APPROVED`, scopes=[P01],
pins exactos y registro actual. Se reservarían los destinos exclusivos
`docs/validation/D5-I92-P01/` y `docs/validation/D5-I92-P01-launch.json`. Los pins se volverían a verificar;
cualquier cambio exige revisar su aplicabilidad.

I86/I89 permanecen INVALID_CAPTURE, sellados y sin sobrescribir, reanudar,
combinar paquetes ni reutilizar autorizaciones. I92 no autoriza P02–P10, I38/I67,
CT96/PR96/DW24/NS12 u otras campañas. Un fallo o incompatibilidad nueva se conserva
y presenta antes de ampliar o repetir. El máximo resultado de captura es
TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW: IR03/suficiencia y publicación necesitan
decisiones separadas, sin aceptación automática de UI04.1/H07/GI/D5 global.

Opciones: **A**, autorizar sólo I92 en ese alcance; **B**, revisión documental.
El requisito de decisión separada procede del handoff I84 y de la decisión I90/I91;
la autorización anterior de I86/I89 no cubre este perfil/destino nuevo.

P0;83/1, UI04.1 parcial. D1–D4 cerrados e I1–I20/A52 aceptado,30/35 sin promoción;
D5 global/H07/G01–G07/GI globales OPEN. Sin proveedores/credenciales/corpus reales,
consumo/reservas, activación, promoción, despliegue, nuevos SQL/Java/Docker o D6.
Ni componentes PASS ni una captura futura sustituyen evidencia integrada de
persistencia/recuperación, independencia o fsync nativo.
