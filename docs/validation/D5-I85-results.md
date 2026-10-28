# I85 — perfil parental validado sólo en componentes

La respuesta expresa **A** del usuario posterior a la revisión del handoff aprueba
I84 y autoriza este nuevo perfil/registro y PR96 exclusivamente sintéticos bajo
300 s externos. Base `7ff47485109306f90ecc4eebc6a6b3f6ec597d99`.
I84 permanece byte a byte con su estado histórico de diseño.

**PR01–PR96: 96/96 PASS**, cero fallos, errores o skips, en **2,10 s externos**
(1,973 s internos). Una ejecución; sin repetición de CT96 ni suites históricas.
16 raíces propias verificadas y retiradas, 16 controles hermanos conservados;
cinco procesos sintéticos terminados (0,0,0,2,2), cero pendientes. Los dos códigos
2 son los negativos sintéticos previstos de fallo TARGETS y autoridad rechazada.
Cero imports de producto/runners históricos y cero campañas funcionales.

[Raw PR96](D5-I85-tests-raw.json) · [Contexto externo](D5-I85-context.json) ·
[Resultados por caso](D5-I85-results.json) · [Integridad](D5-I85-integrity.json) ·
[Registro nuevo](D5-PARENTAL-CAPTURE-REGISTRY.json) ·
[Laboratorio/autoridad I85](../design/D5-I85-PARENTAL-CAPTURE-LAB.md).

El namespace nuevo implementa el registro directo DI07 por objetos exactos,
lectura previa mínima de target/run_id/endpoint y registro tras start original.
Root/scope se ignoran. Las quince políticas separan recibos Store/Drive, último
recibo público de dispatch, remote sin recibo, genesis y snapshots. Las tablas y
mensajes versionados quedan en el mismo sidecar. El lector rechaza asociaciones
incompletas/conflictivas, contexto ajeno, esquemas desconocidos y enlaces huérfanos;
la cadena DI07 exige snapshot parental compatible, digest completo recibido,
assertEqual/outcome originales y salida observada. No hay medición extra del
dominio, wrappers dentro del hijo o reconstrucción de command_id desde intención.

Se mantuvieron 516 inputs documentales, incluidos los 503 de preservación I84.
El reader de preservación y fuente por caso acumuló **115.494.889 bytes únicos y
238.079.415 leídos**, dentro de 128/256 MiB. Este ámbito no incluye todas las
lecturas stdlib/unitarias ni equivale a inputs runtime ejecutados. El runtime
funcional deberá completar y medir sus pins propios antes de autorizarse.
Los sellos I83, I84 y handoff siguen coincidiendo; ningún archivo previo cambió.

**Compatibilidad P01 no medida.** El spawn real fue de un productor nuevo; los
objetos unitarios con Popen sintético y los entrypoints inyectados son controles
de componentes. No se importó/ejecutó discovery ni target DI07 de dominio. PR96
no promete que una campaña 321/12 quepa ni que UI04.1 quede satisfecha. Intención
parental, READY/ACK/exit0 y PASS aislados no acreditan recibo, fsync nativo,
persistencia ni recuperación integrada. Remote sin recibo conserva la ausencia;
dispatch no acredita todos sus comandos internos.

Estado: **PARENTAL_COMPONENT_VALIDATED_PENDING_FUNCTIONAL_SCOPE_AND_SUFFICIENCY**.
I86 sigue bloqueado en **NOT_RUN_I86_AUTHORIZATION_REQUIRED**: requiere decisión
humana nueva, autoridad/pins y destino exclusivos; no se crearon ahora. Cualquier
incompatibilidad futura se conserva y presenta antes de ampliar o repetir.
IR03/suficiencia y publicaciones futuras también requieren decisiones separadas.
No se hizo commit ni push.

P0; **83 SUPPORTS_BOUNDED/1 PARTIAL**, UI04.1 parcial. D1–D4 cerrados, hito local
I1–I20/A52 aceptado, histórico 30/35 sin promoción; D5 global/H07/G01–G07 y GI
globales abiertos. Sin proveedores/credenciales/corpus reales, consumo/reservas,
activación, promoción, despliegue ni D6.
