# I88 — witnesses de dominio validados sólo en componentes

La respuesta expresa **A** del usuario aprueba I87 y autoriza el perfil/registro
nuevos y DW01–DW24 sintéticos bajo 300 s externos. No autoriza I89 ni publicación.
Los documentos I87 conservan sus flags históricos de propuesta; la decisión nueva
se registra aquí. HEAD base `7ff47485109306f90ecc4eebc6a6b3f6ec597d99`.

**DW01–DW24: 24/24 PASS**, cero fallos, errores o skips, en **1,73 s externos**
(1,608 s internos). Una ejecución. Siete raíces propias verificadas y retiradas y
siete controles hermanos conservados; un productor spawn sintético terminado con
exit 0, cero hijos pendientes. Sin imports de producto/tests/runners históricos,
CT96/PR96/DF03/DI07/P01 ni otras campañas funcionales.

[Raw DW24](D5-I88-tests-raw.json) · [Contexto externo](D5-I88-context.json) ·
[Casos/resultados](D5-I88-results.json) · [Integridad](D5-I88-integrity.json) ·
[Registro nuevo](D5-DOMAIN-CAPTURE-REGISTRY.json) ·
[Laboratorio/autoridad I88](../design/D5-I88-DOMAIN-CAPTURE-LAB.md).

DW05 reprodujo el rechazo del selector heredado copiado con dos objetos nuevos que
comparten run/store/role. La resolución nueva conservó ambos witnesses, sin elegir
uno por posición. No reconstruye el conjunto privado ausente de I86 ni atribuye
una causa runtime única a aquel expediente. I86 permanece inválido e inmutable.

DW12 ejercitó un recorder completo con dos instancias Store sintéticas reabiertas,
un independent original llamado exactamente una vez y retorno idéntico, recibo y
oráculo retenido, y diez eventos recorridos por el lector. DW17 verificó rechazo
de ciclos/huérfanos/duplicados, sin eludir las comprobaciones por actualizar hashes.
DW23 ejercitó un protocolo parental estilo DI07 con un productor nuevo y siete
eventos recorridos; no ejecutó el DI07 histórico. Las pruebas de agrupación y del
lector rechazan contexto incompatible, identidad mutada y witnesses sin evidencia.

Los grupos retienen object_ref y autoridades por contexto completo, sin fusionar
estados, versiones o heads. Construcción sigue siendo NOT_HEAD. Los enlaces de
recibo requieren command/request/seq y head/commit observados además del grupo;
varias llamadas compatibles bloquean la unicidad exigida. Se mantienen las quince
políticas parentales, ausencias de remote, último recibo de dispatch y separación
de hashes Store/Drive/I70. Sin mediciones, actores, canales o lecturas de dominio
nuevos; tablas en el mismo sidecar y cuotas heredadas intactas.

Se preservaron **546 inputs documentales**. El reader de preservación y fuente
por caso acumuló **117.505.424 bytes únicos y 236.476.501 leídos**, dentro de
128/256 MiB. No representa todas las lecturas unitarias/stdlib/OS ni inputs runtime
ejecutados. Los sellos I83/I84/I85/I86/I87 coinciden y sus archivos permanecen
byte a byte. No hubo cambios previos, commit ni push.

Estado: **DOMAIN_COMPONENT_VALIDATED_PENDING_FUNCTIONAL_SCOPE_AND_SUFFICIENCY**.
La compatibilidad P01 completa y su capacidad 321/12 siguen **no medidas**. Los
PASS sintéticos no acreditan persistencia, recuperación integrada, fsync nativo o
suficiencia UI04.1. I89 requiere decisión expresa posterior sobre pins/presupuesto
y destino exclusivos; no se creó su autoridad ni se lanzó captura. Una futura
incompatibilidad se conserva y presenta antes de ampliar o repetir. IR03 y la
publicación/aceptación global siguen siendo decisiones separadas.

P0;**83 SUPPORTS_BOUNDED/1 PARTIAL**,UI04.1 parcial. D1–D4 cerrados, hito local
I1–I20/A52 aceptado,30/35 sin promoción; D5 global/H07/G01–G07 y GI globales OPEN.
Sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción,
despliegue, SQL/Java/Docker nuevos ni D6.
