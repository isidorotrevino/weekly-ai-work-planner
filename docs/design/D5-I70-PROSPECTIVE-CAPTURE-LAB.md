# D5 I70 — laboratorio del capturador prospectivo

Fecha: **2026-10-26**. [Contrato I69](D5-I69-PROSPECTIVE-CAPTURE-DESIGN.md) · [PF60](D5-I69-PROSPECTIVE-CAPTURE-REVIEW.md).

La selección A aprueba I69 y autoriza implementar componentes, registro fijo y PF60 con suites sintéticas. No autoriza importar runners/producto históricos o ejecutar P01–P10. La puerta I71 precede cualquier import funcional y lanzamiento, y el modo por defecto es plan de lectura.

El nuevo namespace prospective_capture implementa lectura/pins, callbacks de ciclo/resultados, assertions con context-manager observado conservando su identidad, retornos públicos ya producidos, restauración exacta, digest builtin streaming acotado, source/factory bindings, enlaces many-to-many, metadata anidada tipada, propagación de carencias, canales y ownership de workers y paquetes nuevos. El registro procede de los pins I69 sin aprenderlos al ejecutar. Ningún módulo I38/I67 se importa o ejecuta como dependencia.

PF60 usa exclusivamente suites y clases nuevas en memoria y temporales propios con sentinel. Prueba pasos positivos y negativos de protocolo mediante un productor sintético, además de EOF/timeout/exit y rechazo de cleanup ajeno. Los procesos falsos no son labs T/R ni SIGKILL positivos de dominio. No se inspecciona o limpia dev/run_data/D4. Las mismas llamadas originales devuelven los mismos objetos/excepciones; observación fallida/budget inválido se separa del resultado funcional y detiene captura en límite seguro.

El caller conservará raw original y sidecar/contexto/manifests separados. El contexto de worker incluye su argv/argumentos públicos observados y normalización del intérprete; context.argv del runner se etiqueta declaración, no execve real. Los snapshots nuevos no se invocan desde observadores. Source binding de factories es expectativa revisada de código, no atestación de sus argumentos efectivos en un proceso hijo.

Los tests de componente no demuestran compatibilidad, cobertura o presupuesto de las692 ocurrencias originales. Fase I71 sigue NOT_RUN hasta decisión humana con SHA concreto. Los P futuros tienen guards y validaciones; cualquier incompatibilidad de API, callbacks, schema o presupuesto deberá bloquear ese alcance y presentarse antes de ampliar. I70 sólo podrá quedar COMPONENT_CAPTURE_VALIDATED_PENDING_I71; suficiencia UI01.2/UI04.1/UI09.2 y agregado81/3 intactos.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. D5 global/G01–G07, los cinco GI globales y H07 abiertos, closure=false. Sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue ni D6. No publicación ni lectura nueva del remoto.
