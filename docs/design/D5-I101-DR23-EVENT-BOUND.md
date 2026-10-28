# I101 — DR23: cota completa de eventos parentales por fuente

Fecha: 2026-10-28, Europe/Madrid. Revisión documental, sin ejecución nueva.
**DR23 completo tiene una cota de1.951 eventos parentales bajo las condiciones
de fuente indicadas, frente a2.048/test.** La diferencia97 es aritmética de
fuente, no margen medido ni certificado de que una captura P01 sea admisible.

[24 subcasos, anclas y doble cuenta](../validation/D5-I101-DR23-event-bound.json).
Se conservan fuente/perfil/cuotas anteriores, sin implementar ni ejecutar campañas.

## Expansión de los24 subcasos

La tupla literal cruza6 kinds con4 puntos. prepare usa apply=False sólo para
APPLY_BATCH. En los otros5 kinds prepara las2 TASKs de source() por defecto.
phase añade0/0/1/1/6/8 eventos respectivamente: no se usa el máximo66 de prepare
para la rama que sólo prepara sin aplicar.

| Kind | Eventos de sus4 subcasos completos |
|---|---:|
| APPLY_BATCH |174|
| SELECT_TASKS |342|
| PREPARE_PROJECTION |346|
| ISSUE |346|
| QUERY |366|
| RESULT |374|
| Subcasos, incluidos sus resultados |1948|
| TEST_START/TEST_RESULT raíz/TEST_END |3|
| Total DR23 |1951|

Cada subcaso incluye2 eventos de construir Store del lab,2 independent externos,
kill_at(5),2 comparaciones unittest y reprocess(5). kill_at cuenta sus2 oráculos
internos más start/receive/finish; los assert de Python no son wrappers unittest.
reprocess cuenta esos3 boundaries parentales y2 assertEqual. El summary del
hijo no ejecuta los observers parentales.

yes depende del point literal:6 casos after_head y18 restantes. La rama yes
añade2 Store construidos por fresh,4 eventos de perform replay y1 assertTrue;
la otra añade1 assertEqual. Total de esa decisión:6×7+18×1=60. No se sobreestima
yes24 veces ni se presupone una condición dinámica favorable.

Los24 subTest generan24 resultados y la raíz otros3 eventos de lifecycle.
No se añade otro terminal al CALL_RETURN de Client.perform (publish=False).
join/finish guardan exit_observations, pero CausalState.exit no emite un evento
adicional. Las observaciones de recv tampoco emiten otro evento de message.
Esas operaciones sí cargan referencias/filas, que permanecen en su otra cuenta.

## Contraste por clase de evento

| Contribución | Eventos |
|---|---:|
| Client.perform |318|
| Store.transact |322|
| Retornos snapshot |852|
| Oráculos independent |108|
| start/receive/finish parentales |144|
| Construcciones Store |60|
| Aserciones unittest |120|
| Lifecycle y resultados de subtest |27|
| Total |1951|

Por fuente se esperan48 protocolos hijos:24 mutate y24 snapshot; no son nuevos
hijos observados ni una verificación de cleanup. Los108 independent añaden como
máximo108 filas de oráculo originales; sus bytes y enlaces/fanout no quedan
certificados por contar sus eventos. No se infiere persistencia/recuperación
integrada ni fsync nativo de estas etiquetas o de un replay previsto.

## Condiciones y límites de la conclusión

Se cuenta la ruta original completa de éxito con los mismos métodos/selectores,
2 TASKs, observación/serialización válida y sin callbacks, fallos o reintentos
adicionales. Rutas de excepción inesperada/cleanup de hijo vivo requieren otra
cuenta y conservan su fallo; no se transforman en PASS. Los cleanups originales
de labs cerrados y setUp no añaden eventos de los observers registrados, aunque
mantienen su trabajo real.

Esto resuelve el componente events_test para esta ruta DR23. No resuelve sus
refs, bytes de filas/operandos ni el acumulado de campaña. El techo global de
refs actual sigue insuficiente por I97. Tampoco cubre las87 raíces T/R restantes
ni otros grupos de321/12. Hace falta extender el cierre y componer las24 cuotas
antes de proponer otro perfil y sus decisiones correspondientes.

I83–I100 preservados. P0;83 SUPPORTS_BOUNDED/1 PARTIAL y UI04.1 parcial;
D1–D4 cerrados, I1–I20/A52 aceptado. D5/H07/G01–G07 y GI33/34/38/39/40
globales abiertos. Sin proveedores/credenciales/corpus reales, consumo/reservas,
activación, promoción, despliegue, publicación ni D6.
