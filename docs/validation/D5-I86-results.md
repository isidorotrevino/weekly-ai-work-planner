# I86 — intento P01 bloqueado, sin reintento

El usuario autorizó expresamente una captura funcional **sintética P01 completa:
321 tests/12 grupos, pins y destino nuevos, 900 s externos, sin reintentos
automáticos ni publicación**. No autorizó proveedores reales ni cierre global.

La única ejecución terminó en **1,07 s externos**, exit 1, con
**BLOCKED_WORKER_FAILURE / INVALID_CAPTURE**. Sólo se ejecutaron **3/321 tests**:
DF01, DF02 y DF03, todos PASS. Los 318 restantes no se observaron; **DI07 no llegó
a ejecutarse**. El raw declara PASS sobre esos tres tests y el entrypoint devuelve
0; ninguno acredita P01 completo o captura válida.

[Resultados estructurados](D5-I86-results.json) ·
[Contexto externo](D5-I86-external-context.json) ·
[Autoridad específica](D5-I86-capture-authorization.json) ·
[Raw original](D5-I86-P01/runner-raw.json) ·
[Sidecar original](D5-I86-P01/sidecar.json) ·
[Contexto/cleanup](D5-I86-P01/context.json) · [Integridad](D5-I86-integrity.json).

El primer error conservado del sidecar es **ORACLE_DOMAIN_IDENTITY_MISSING**;
siguen CAUSAL_LINK_MISSING, INCOMPLETE_TEST_SET y SANITIZED_WORKER_ERROR. El
ledger mantiene fase **ENTRYPOINT** y código diagnóstico sanitizado. La parada
entre tests conservó el cleanup original: **OWN_GROUP_GONE**, observers restaurados,
cero raíces, hijos o hilos propios pendientes según raw/contexto. No se inspeccionó
ni limpió dev/run_data/D4. SQL/D2/D3/D4 no se reejecutaron.

## Hallazgo por fuente y alcance de la explicación

`CausalState.domain` en el perfil parental exige exactamente un candidato con el
mismo frame/subcaso y run/store/role. El wrapper de `independent` aplica esa regla
antes de retener el oráculo. La regla proviene de la fuente I83 y permanece sellada
allí. DF03 usa `lab.client`, reabre con `lab.fresh()` y obtiene el estado mediante
el oráculo original; su sidecar conserva, entre otras, las declaraciones O2 y O10
para el mismo run/store/role. Dos objetos legítimos pueden representar una misma
identidad de dominio. La unicidad de objeto no es unicidad de dominio.

Esto proporciona un mecanismo de fallo compatible con la fuente y los eventos.
**El conjunto interno de candidatos y el terminal del oráculo fallido no quedaron
retenidos**: no se reconstruyen, ni se atribuye una causa runtime única más allá
del error realmente registrado. El siguiente componente debe reproducir el caso
con objetos nuevos y comprobar el mecanismo antes de afirmar la reparación.

I85 ejercitó productores y entrypoints sintéticos, pero no este recorrido completo
de reapertura/oráculo de DF03. Sus 96/96 PASS siguen siendo evidencia sellada de
componentes; este intento demuestra que no bastaban para acreditar compatibilidad
P01. I86 se conserva completo, sin rellenar el oráculo faltante, borrar errores,
continuar sólo los 318 restantes o mezclar capturas anteriores.

Se fijaron **261 inputs, 60.305.046 bytes únicos**, todos aún coincidentes. Los pins
y los once artefactos del sello I85 se preservaron. No se modificó perfil, registro,
contrato o evidencia previa durante I86. El paquete ocupa su destino exclusivo;
una futura ejecución no podrá sobrescribirlo ni reutilizar esta autorización.

El [ajuste I87 propuesto](../design/D5-I87-DOMAIN-WITNESS-DESIGN.md) es documental:
conjuntos explícitos de witnesses de dominio y pruebas dirigidas antes de cualquier
nueva captura. No se implementó ni ejecutó por este hallazgo. La ruta global se
actualiza en [el plan posterior a I86](../design/D5-AFTER-I86-CLOSURE-ROADMAP.md).

P0; **83 SUPPORTS_BOUNDED/1 PARTIAL**, UI04.1 parcial; D1–D4 cerrados e hito local
I1–I20/A52 aceptado; D5 global/H07/G01–G07 y GI globales abiertos. No revisión IR03
de suficiencia positiva ni persistencia/recuperación integrada inferidas de PASS.
Sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción,
despliegue o D6. Sin commit/push. Una repetición/ampliación requiere presentar y
aprobar el ajuste concreto; publicaciones y aceptación global siguen separadas.
