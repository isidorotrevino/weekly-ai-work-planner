# D5 I70 — componentes de captura prospectiva

Fecha: **2026-10-26**, Europe/Madrid. Base I69 `f3b51e0d808a7722a76d8de9bdced76571ebab84`. **COMPONENT_CAPTURE_VALIDATED_PENDING_I71**.
[Contrato I69](../design/D5-I69-PROSPECTIVE-CAPTURE-DESIGN.md) · [PF60](../design/D5-I69-PROSPECTIVE-CAPTURE-REVIEW.md) · [Laboratorio](../design/D5-I70-PROSPECTIVE-CAPTURE-LAB.md) · [Resultados estructurados](D5-I70-results.json) · [Integridad](D5-I70-integrity.json).

La selección A aprueba I69 y autoriza implementar capturador, registro fijo y PF60 con suites sintéticas. **60/60 componentes PASS; cero campañas funcionales y cero imports de runners/producto históricos.** No ejecuta las692 ocurrencias. Los flags I69 de preparación permanecen como historia. Producto/Store/fixtures/hooks/tests/helpers/runners/handoff previos y registros/auditores I38/I67 intactos.

## Implementación y validación propia

Nuevo namespace [prospective_capture](../../testing/prospective_capture/README.md) y [registro fijo](D5-PROSPECTIVE-CAPTURE-REGISTRY.json) conservan P01–P10 y pins I69. El plan por defecto es de lectura. El modo funcional comprueba un manifest I71 de autoridad y hashes antes de crear salida, lanzar worker o importar el runner; el worker repite la puerta antes de su único sitio de import funcional. **El manifest I71 no existe ni se crea en I70.** Los campos del archivo son coherencia de la herramienta, no aprobación humana ni atestación criptográfica.

[Raw PF60](D5-I70-tests-raw.json):60 IDs distintos,60 casos, anclas AST y375 entradas pre/post idénticas. PF01–PF10 verifican metadatos/pins y expectativas de invocación sin cargar módulos históricos. PF11–PF60 usan suites/clases/registros nuevos y procesos de protocolo propios. Siete temporales con OWNER/identidad verificados y eliminados; cuatro procesos sintéticos terminados/esperados (normal0, salida7 y dos interrupciones negativas SIGINT), cero hijos pendientes o SIGKILL positivos de dominio. Tests internos de una suite sintética fallan/se saltan deliberadamente para comprobar fidelidad; no son campañas de producto ni casos extra de PF60.

Los wrappers observan callbacks y resultados originales, retornos ya producidos y assertions con digests exactos de builtins soportados. Las llamadas originales se ejecutan una vez y conservan objeto devuelto/excepción; los context managers assertRaises conservan identidad y separan declaración de cierre observado. Se restauran los objetos originales al terminar incluso ante captura inválida. Falta/error de observación se etiqueta, sin alterar la llamada de fixture ni convertirla en éxito de captura. No se hacen snapshots, consultas o efectos adicionales para medir un caso.

Frames/capture_run_id son del capturador, distintos de run/Store IDs realmente observados. Métodos generados HF/IC y aliases DF/DR conservan source bindings/factory/argumentos declarados, sin presentar derivación estática como medición. Se enlazan registros nacidos durante cada lifecycle; se preservan variantes y se propagan carencias del escenario al test/grupo. Un predicado unitario y un campo presente no acreditan una frontera durable. Tipos no serializables, source binding o identidad ausentes quedan explícitos e incompletos.

PF43 prueba el intercambio positivo READY/RELEASE con productor sintético y dos canales raw/sidecar, más EOF/timeout/exit propios. PF50 rechaza cleanup con lease ajena antes de actuar; PF46/PF47 prueban no overwrite, symlink/FIFO/cambio de bytes y preservación de sentinel hermano. PF49 comprueba que faltando I71 no se llama a importlib para cargar runners ni a Popen para lanzarlos. Los límites reducidos se etiquetan como negativos, sin ampliar12MiB de raw/sidecar ni modificar límites kernel.

Durante desarrollo se corrigieron fixtures (decorador expectedFailure compartido, path de nombre reservado, registro de limpieza bajo excepción y escapes de un productor falso), además de precisar validación de status/bindings, argumentos públicos, identidad y propagación de faltantes. No se alteraron contrato, producto, presupuestos o archivos previos. Sólo la campaña completa definitiva estable se conserva como PF60; selecciones anteriores no se suman como aceptación.

## Plan separado y fase funcional pendiente

[Raw del plan](D5-I70-plan-raw.json) y [contexto](D5-I70-plan-context.json): CLI nuevo exit0, stderr vacío, diez scopes **NOT_RUN_I71_AUTHORIZATION_REQUIRED**,375 hashes pre/post iguales a PF60. No es una ejecución del capturador sobre producto. El nuevo programa usa sólo stdlib y componentes propios; el sitio diferido de import funcional no se ha ejercido con runners históricos.

Una fase I71 autorizada propondría P01 Python321, P02 GX90 y P03–P10 HC24/HF40/IC30/UQ24/RV20/NA36/FN64/CE43:692 ocurrencias en21 grupos,388 filas del formato original esperadas más frames nuevos. El launcher tiene sesión/grupo propios, canales correlacionados, archivos nuevos sin overwrite, chequeos pre/post y paquete raw/sidecar/contexto separado; si no confirma ownership/terminación o el paquete es incompatible, bloquea. **PF60 no demuestra compatibilidad, suficiencia o presupuesto sobre esas692 ocurrencias**. La primera ejecución real puede detectar una incompatibilidad; se deberá detener y presentar un ajuste concreto sin debilitar oráculos o límites.

El comando normalizado del worker, sus argumentos observados y el entrypoint se separan del context.argv literal del runner, etiquetado RUNNER_DECLARATION. El contexto nuevo no rellena el pasado. No se sustituyen raw/argv/kernel/run_id ausentes de I34/I36/I64. Los dict/objetos de dominio no se copian a diagnósticos; se conservan digests o referencias saneadas. No se ejecuta I38/I67 ni se reescriben las clasificaciones limitadas en I68.

## Integridad y criterios

La verificación documental comprueba schema/pins,60 casos,375 inputs, anclas AST y las fuentes/expansiones de692 bindings, estado NOT_RUN de diez scopes, ausencia de imports prohibidos y recursos propios. Los hashes previos permanecen intactos. Higiene de contenido completa con mismos patrones y umbral temporal12MiB registrada en integridad, manteniendo once advertencias históricas de tamaño sin cambiar el checker. No autoriza publicación.

**UI01.2/UI04.1/UI09.2 siguen PARTIAL; agregado81 SUPPORTS_BOUNDED /3 PARTIAL.** I70 sólo valida componentes de captura. I71 requiere autorización humana posterior y la suficiencia de sus resultados seguirá siendo otra revisión. No persistencia/recuperación integrada deducida de PASS aislados. UI22.2 mantiene I62 y límites fsync, UI20.3 sólo CREATE nativo I56 y GI39 alcance finito I65.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. D5 global/G01–G07, GI33/GI34/GI38/GI39/GI40 y H07 abiertos, closure=false, histórico30/35 sin promoción. GI06/GI12/GI18/GI24/GI30/GI36/GI42 reales/humanos conservan sus puertas propias, sin traslado a D6. P0: sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue ni D6; sin inspección/limpieza de dev/run_data/D4 operativo. Publicado sólo hasta I52; I53–I70 locales, sin push ni nueva lectura remota.
