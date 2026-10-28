# I85 — perfil parental y laboratorio PR96

La respuesta expresa **A** del usuario tras la revisión de HANDOFF-D5-I84.md
aprueba el contrato I84 y autoriza exclusivamente el nuevo perfil/registro parental
y PR01–PR96 sintéticos bajo 300 s externos. No autoriza captura funcional I86 ni
publicaciones nuevas. Fecha: 2026-10-27, Europe/Madrid; base Git 7ff4748.

Se preservan los cuatro documentos I84 con su estado histórico PREPARED_FOR_REVIEW
y PR96 NOT_RUN. La decisión posterior se registra aquí y en los resultados I85.

Namespace nuevo `testing/prospective_capture_parental` con cinco archivos;
registro `docs/validation/D5-PARENTAL-CAPTURE-REGISTRY.json`. La base causal I83
se deriva por copia de su fuente pinneada, sin modificarla ni importar sus tests.
Los helpers puros I70/I73/I76/I79 conservan identidad, fuentes y registros.
Los observers stdlib se instalan sólo en el padre y se restauran; fuera del
selector DI07 exacto Pipe/start delegan sin inspección. Root/scope nunca se
copian, hashean o publican en el registro directo. El PID es metadata posterior.

PR96 utiliza clases y productores nuevos. La prueba de spawn real verifica
Pipe/start/recv/join con un snapshot sintético propio. Las pruebas de
launcher/worker inyectan un entrypoint sintético en procesos propios; no prueban
el runner funcional ni P01. Los pares/procesos con Popen construido para tests
unitarios se etiquetan como datos sintéticos; no son procesos reales ejecutados.
Los tests prueban políticas y rechazo de grafos inválidos, topes de eventos,
refs, operandos, reader y paquete, restauración, excepción y sidecar parcial.

Se conserva raw de cada ejecución y sus fallos; no hay repetición automática ante
incompatibilidades de API, oráculo o presupuesto. La lectura documental de los
503 inputs no los convierte en entradas ejecutadas por el worker. El reader de
preservación acumula antes/después y fuente por caso; las lecturas stdlib y de
validación unitarias se distinguen explícitamente, sin afirmar que son lecturas
del futuro worker. El runtime funcional deberá medirse con sus pins finales.

El resultado máximo I85 es componente sintético validado, pendiente de
compatibilidad funcional y suficiencia. El plan bloquea en
NOT_RUN_I86_AUTHORIZATION_REQUIRED. I86 requiere decisión humana nueva y sus
pins/autoridad/destino exclusivos; nada de ello se crea en I85. No reejecutar CT96,
PF60/PG64/AT80/LB64, P01/P02–P10, I38/I67, SQL/Java/Docker ni suites históricas.

P0; 83 SUPPORTS_BOUNDED/1 PARTIAL, UI04.1 parcial; D1–D4 cerrados, hito local
I1–I20/A52 aceptado, 30/35 sin promoción; D5 global/H07/G01–G07 y GI globales
abiertos. PASS aislados no acreditan persistencia, recuperación integrada o fsync
nativo. Sin proveedores/credenciales/corpus reales, consumo/reservas, activación,
promoción, despliegue ni D6. Publicación separada.
