# I91 — selectores nullable validados sólo en componentes

La respuesta expresa **A** aprueba I90 y autoriza perfil/registro nuevos y
NS01–NS12 sintéticos bajo300s externos. No autoriza I92 funcional o publicación.
I90 conserva sus flags históricos de propuesta; la decisión se registra en I91.
HEAD base `7ff47485109306f90ecc4eebc6a6b3f6ec597d99`; árbol tracked intacto.

**12/12 PASS**, sin fallos, errores o skips, en **0,82 s externos** (0,705 s
internos), una ejecución. Cuatro raíces propias verificadas/retiradas con cuatro
controles hermanos preservados; cero procesos hijos iniciados o pendientes.
Sin producto/runners/tests históricos, DF08/DI07/P01 u otras campañas funcionales.

[Raw NS12](D5-I91-tests-raw.json) · [Contexto externo](D5-I91-context.json) ·
[Resultados por caso](D5-I91-results.json) · [Integridad](D5-I91-integrity.json) ·
[Registro nuevo](D5-SELECTOR-CAPTURE-REGISTRY.json) ·
[Laboratorio y decisión](../design/D5-I91-SELECTOR-CAPTURE-LAB.md).

NS01 reproduce COMMAND_HEADER_INVALID del selector heredado con una prueba
sintética nueva y retry_tick=None. No reconstruye el retorno/terminal ausente de
I89 ni atribuye una causa runtime única. I86/I89 conservan INVALID_CAPTURE.
NS02/NS03 y NS10 recorren recorder y lector completos con Stores/oráculos nuevos
T/R, retorno original idéntico, una llamada original por oráculo, recibo/enlace
real dentro del paquete sintético y rechazo de manipulación del grupo.

NP00 permanece estricto por defecto. Sólo NP01 T/NP02 R aceptan null presente en
retry_tick con schema/13 claves exactas, identidad/familia/rol REMOTE y operación
EXECUTE/CLOSE compatibles. No se inserta un campo ausente, no se coacciona a0 ni
se admiten bool/float/string/fuera de rango. Otros enteros siguen estrictos.
Las proyecciones versionadas explicitan metadata_policy_ref/selector_policy_ref;
el lector rechaza referencias forjadas, claves extra y contexto cruzado.

NS09 registra dos protocolos sintéticos CP07/CP13, sin iniciar procesos, y valida
las cabeceras recibidas por el lector. Su resultado remoto conserva null, pero
receipt/command_id permanecen ausentes y CHILD_LOCAL_NOT_OBSERVED: no se infiere
UUID5 ni se promociona intención del padre. Permanecen grupos/witnesses I88,
quince políticas parentales, cuotas y observadores; sin nuevas llamadas o lecturas
de dominio, actores o canales auxiliares. NS11 verifica identidad de retorno y
excepción, primera fase/diagnóstico sanitizado, salida parcial no reparada,
restauración y límite acumulado del Reader.

Se preservaron **574 inputs documentales**: **121.289.130 bytes únicos y
243.118.545 leídos**, dentro de128/256MiB. Este ámbito no representa todas las
lecturas unitarias/stdlib/OS ni inputs runtime ejecutados. Sellos I83–I90 y sus
artefactos coinciden byte a byte. No se modificaron archivos anteriores, ni hubo
commit/push.

Estado **SELECTOR_COMPONENT_VALIDATED_PENDING_FUNCTIONAL_SCOPE_AND_SUFFICIENCY**.
I92 completo321/12 sigue NOT_RUN, con autoridad/destino/launcher ausentes.
Necesita decisión expresa separada sobre pins/presupuesto nuevos y límite900s,
sin reintentos automáticos ni publicación. Cualquier incompatibilidad se conserva
y presenta antes de ampliar/repetir. IR03 y publicación/aceptación global siguen
siendo decisiones separadas. PASS de componentes no prueba capacidad funcional,
persistencia, recuperación integrada, independencia, fsync nativo ni UI04.1.

P0;83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1). D1–D4 cerrados; I1–I20/A52 aceptado;
30/35 sin promoción. D5 global/H07/G01–G07/GI globales OPEN. Sin proveedores,
credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue,
SQL/Java/Docker nuevos o D6.
