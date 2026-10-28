# I89 — intento P01 bloqueado en DF08, sin reintento

La respuesta expresa **A** del usuario autorizó una captura sintética P01 completa,
321 tests/12 grupos, bajo 900 s externos, sin reintentos automáticos ni publicación.
Se creó autoridad nueva con **276 pins/61.664.783 bytes** y destino exclusivo I89.

La única ejecución terminó en **13,01 s externos**, exit 1:
**BLOCKED_WORKER_FAILURE / INVALID_CAPTURE**. Ejecutó **8/321 tests**, DF01–DF08,
todos PASS; **313 tests y once grupos no se observaron**, incluido DI07. El raw
PASS y entrypoint 0 sólo corresponden al subconjunto ejecutado. No hay captura
completa, compatibilidad P01 acreditada ni revisión IR03 positiva.

[Resultados estructurados](D5-I89-results.json) ·
[Contexto externo](D5-I89-external-context.json) ·
[Autoridad I89](D5-I89-capture-authorization.json) ·
[Raw original](D5-I89-P01/runner-raw.json) ·
[Sidecar original](D5-I89-P01/sidecar.json) ·
[Contexto/cleanup](D5-I89-P01/context.json) · [Integridad](D5-I89-integrity.json).

El primer error del sidecar es **COMMAND_HEADER_INVALID**; siguen
CAUSAL_LINK_MISSING, INCOMPLETE_TEST_SET y SANITIZED_WORKER_ERROR. El diagnóstico
conserva fase ENTRYPOINT y código sanitizado. DF01–DF07 no tienen missing en sus
frames, incluido DF03; eso no valida el paquete global. DF08 conserva
CAUSAL_LINK_MISSING. La llamada C1087 carece de terminal y diez llamadas posteriores
en el subcaso phase=RESULT/point=before_object apuntan a ella. El paquete inválido
conserva ese estado: no se eliminan errores, reparentan eventos o rellenan retornos.

## Incompatibilidad localizada por fuente

Los reducers remotos T/R inicializan la prueba y, en EXECUTE, asignan expresamente
`retry_tick=None`; una entrega confirmada sin rechazo no cambia ese valor. T usa
`d5.durable-remote-proof.v1` y R `d5.relational-remote-proof.v1`. Remote.execute
retorna result del recibo Store original; R reutiliza esa fachada pública T con su
propio reducer/esquema. DF08 prepara su fase RESULT llamando a Remote.execute en
el padre antes de lanzar el crash test original.

El selector heredado de I83/I85/I88 clasifica retry_tick como INTEGER y exige un
int exacto entre 0 y 1023; rechaza None. Esa regla es incompatible con la forma
permitida por la fuente remota. La proyección fallida puede dejar abierta la llamada
causal y producir los enlaces incompletos posteriores. Es un mecanismo compatible
con la fuente y el expediente, **no una reconstrucción del valor runtime ausente**:
el retorno/recibo que falló y el terminal C1087 no quedaron retenidos. No se lee
el dominio otra vez ni se recompone la prueba desde UUID5, estado posterior o fuente.

El [ajuste I90 preparado](../design/D5-I90-NULLABLE-SELECTOR-DESIGN.md) propone una
política nullable cerrada y contextual para retry_tick de esas pruebas, con
reproducción sintética antes de otro intento. No admite None para todos los campos,
no sustituye recibos/identidades ni elimina el fallo I89. No se implementó ni ejecutó
ese ajuste ahora.

## Preservación y límites

Se registraron 1672 eventos, una página de 1.742.646 bytes, 3582 refs compartidas,
máximo 1172 eventos en un frame; 18 oráculos retenidos, 39 grupos de witnesses,
310 links y 26 instancias de protocolo. Estos conteos no demuestran capacidad para
321/12 ni suficiencia causal. El reader no retuvo sus contadores runtime finales.

**OWN_GROUP_GONE**, observers restaurados y limpieza original confirmada: 38 raíces
T retiradas y 26 procesos de dominio terminados; cero raíces, hijos o hilos propios
pendientes. Los SIGKILL de crash pertenecen a los tests sintéticos originales
expresamente autorizados, no a mediciones nuevas del observer. No se inspeccionó
ni limpió dev/run_data/D4. SQL/D2/D3/D4 no se reejecutaron.

Todos los 276 pins siguen coincidiendo; I86 e I88 y sus sellos permanecen intactos.
No se repitió I89, no se reanudaron los 313 restantes, ni se ejecutaron P02–P10,
CT96/PR96/DW24, I38/I67 u otras campañas. No hubo cambios de código, commit o push.
Una nueva captura exige diseño/componentes y otra decisión sobre pins/destino.

P0;**83 SUPPORTS_BOUNDED/1 PARTIAL**,UI04.1 parcial; D1–D4 cerrados e hito local
I1–I20/A52 aceptado,30/35 sin promoción. D5 global/H07/G01–G07 y GI globales OPEN.
No persistencia/recuperación integrada o fsync nativo inferidos de PASS aislados.
Sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción,
despliegue ni D6. La [ruta global anterior](../design/D5-AFTER-I86-CLOSURE-ROADMAP.md)
conserva las 42 obligaciones y siete puertas reales/humanas: I89 no las cierra.
