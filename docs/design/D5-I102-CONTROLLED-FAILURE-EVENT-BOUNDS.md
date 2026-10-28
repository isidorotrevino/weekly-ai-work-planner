# I102 — nueve rutas adicionales de eventos parentales acotadas

Fecha: 2026-10-28, Europe/Madrid. Revisión documental por «continúa».
**DR27≤1.694, DF11≤1.317 y DR24≤523 eventos por fuente**, incluidos los fallos
controlados que sus aserciones originales deben aceptar. El desglose también
cierra las rutas DF08–DF10, DF12–DF13 y DR14 sin ejecutar ninguna prueba.

[Casos y anclas](../validation/D5-I102-controlled-failure-event-bounds.json) ·
[Cobertura y obligaciones restantes](../validation/D5-I102-event-bound-coverage.json).

| Raíz | Eventos como máximo | Diferencia respecto a2048 |
|---|---:|---:|
| DF08 |1173|875|
| DF09 |1173|875|
| DF10 |1173|875|
| DF11 |1317|731|
| DF12 |1245|803|
| DF13 |304|1744|
| DR14 |179|1869|
| DR24 |523|1525|
| DR27 |1694|354|

Son cotas de rutas completas de éxito original con observación válida, no
resultados ejecutados ni márgenes medidos. Las excepciones controladas siguen
siendo excepciones en sus eventos; no se transforman en retornos positivos.
No se cambia perfil/cuota ni se autoriza otra campaña.

## Reutilización de fases T y R sin perder ramas

Cada una de las12 fases T llama ready completo:936 eventos en conjunto.
phase_args añade1 en IMPORT,1 en PREPARE_PROJECTION,7 en QUERY y9 en RESULT:
18 adicionales, total954. QUERY incluye dispatch sin entrega y un oráculo;
RESULT añade además otro oráculo y Remote.execute. Los otros términos son0
eventos de esos boundaries, no trabajo0.

commit_crashes agrega por fase lab2, oráculos externos2, kill_at5, comparaciones2,
fresh_process5, resultado subtest1 y la rama final:1 si no publicado o7 si hay
fresh/replay/assertTrue. La raíz añade3 eventos de lifecycle. Por eso DF08–DF10
son1173 y DF12 es1245. Los cuatro roots mantienen sus puntos publicados/no
publicados exactos; no se suma la rama replay en todos para forzar un máximo.

DF11 agrega30 eventos por fase a954: lab/fresh, tres contextos de excepción,
los outcomes reales de perform/snapshot, oráculos, aserciones y fresh_process.
Total954+360+3=1317. Un error perform suma2 del contexto y4 del fallo de Store;
un snapshot en el Store envenenado suma2+2; el snapshot de recuperación con fresh
suma2 construcciones+2 contexto+2 outcomes. No se aplican7 refs de un comando
exitoso a esos comandos rechazados; las referencias siguen en otra cuenta.

Las6 fases R suman370 eventos de phase:24 para preparar APPLY_BATCH sin aplicar,
5×66 para las demás preparaciones y16 extras de state/dispatch/Remote.execute.
DR24 añade25 por fase, sin subTest:370+150+3=523. DF13/DR14 usan sus ramas sin
aplicar y bucles de4 puntos; sus aserciones y ausencia de subTest están explícitas.

## DR27:15 subcasos y dos formas de provocar el fallo

La tupla cruza CREATE/UPDATE/CLOSE con4 puntos de kill más fsync. UPDATE añade
25 eventos de dispatch entregado, prepare_projection y review en5 casos.
Los3 casos fsync hacen fresh2+contexto esperado2+Remote.execute fallido1=5;
los otros12 hacen kill_at5. La etiqueta fsync es el punto de fuente controlado,
sin afirmar que se haya medido fsync nativo.

yes es True en after_head y fsync:6 casos hacen fresh+reconcile lookup=14.
Los9 restantes hacen fresh+reconcile close=13. Se incluyen lookup de Remote
con su propio fresh, oráculos before/after/state y aserciones originales.
Los modos CREATE/CLOSE suman522 cada uno; UPDATE647. Con3 de lifecycle:
522+647+522+3=1694.

## Verificación y alcance

Cada ruta tiene una tabla de casos y otra cuenta por clases de evento que
coinciden. En rutas con fallos, snapshot_call_events y perform_outcome_events
incluyen CALL_EXCEPTION además de CALL_RETURN. Client.perform lleva su causal
dentro de ese mismo evento, sin terminal extra. join/exit/message conservan
sus cargos de refs/filas sin inventar eventos adicionales.

Con DR23/I101 hay **10 de88 raíces T/R** con esta cuenta completa de eventos;
su subtotal superior es10732. No es una cota de la campaña321/12 ni se extrapola
a otras raíces. Aún faltan78 T/R, otros grupos, referencias y bytes. R≥19037
de I97 mantiene insuficiente el techo actual16384, aunque un test quepa en eventos.
Las24 cuotas y Reader deben revisarse conjuntamente antes de proponer otro perfil.

Se preservan Git, cambios ajenos y sellos I83–I101. Cero tests/campañas nuevas,
imports de producto/runners, implementación/cuotas o publicación. P0;83/1 y
UI04.1 parcial, D1–D4 cerrados e I1–I20/A52 aceptado. D5/H07/G01–G07 y
GI33/34/38/39/40 globales abiertos. Sin proveedores/credenciales/corpus reales,
consumo/reservas, activación, promoción, despliegue ni D6; sin deducir recuperación
integrada desde estas cuentas o PASS aislados.
