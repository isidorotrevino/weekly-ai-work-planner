# I74 — P01 funcional completo, captura incompleta

[Contrato I72](../design/D5-I72-PAGED-CAPTURE-DESIGN.md) · [Componente I73](D5-I73-results.md) · [Autorización I74](D5-I74-capture-authorization.json) · [Raw original](D5-I74-P01/runner-raw.json) · [Índice original](D5-I74-P01/sidecar.json) · [Contexto del launcher](D5-I74-P01/context.json) · [Diagnóstico y ajuste](D5-I74-diagnosis.json) · [Resultados estructurados](D5-I74-results.json) · [Integridad](D5-I74-integrity.json).

Base `3cb96c86335743afae0d5c2a9e5cffe75bc63fea`. La selección A autoriza una captura nueva P01 con perfil I73, deteniendo el alcance afectado ante incompatibilidad. Se registraron19 pins y se verificaron los161 inputs I73 antes de ejecutar. Se ejecutó una única campaña P01, sin reintento, cambios de código, registro, producto, fixtures, hooks, oráculos o presupuestos. I71 y P02–P10 intactos.

**Raw funcional PASS:321/321 ocurrencias,12 grupos, sin failures/errors/skips, 243.314 s. Captura BLOCKED: sidecar INCOMPLETE_CAPTURE.** El entrypoint devolvió0, el worker1 por incompletitud. No se confunde PASS funcional con captura completa o suficiencia. Las77 ocurrencias I71 no se añaden a I74 ni se usan para rellenarlo.

| Dimensión | Resultado |
|---|---|
| Frames | 321;286 con campos capturados pendientes de revisión y35 incompletos |
| Identidad de dominio |30 frames de test_incremental_capture sin identidad proyectada |
| Operand metadata |5 frames,6 eventos y11 slots UNSUPPORTED_OPERAND |
| Transporte |22.452 eventos,3 páginas,6,074,703 bytes de páginas |
| Integridad estructural posterior |Hashes/bytes/rangos/lifecycle/referencias de páginas verificados por lectura; no acepta la metadata incompleta |
| Inputs |Runner antes/después coincidente;19 pins de captura coincidentes |
| Limpieza |Raw cleanup_verified y OWN_GROUP_GONE; cero roots/children/threads propios vivos reportados |

No se agotó ningún presupuesto. La lectura estructural posterior usa el verificador puro de páginas, sin ejecutar campañas, PG64 o I38/I67. El contexto original del launcher conserva NOT_ACCEPTED_INCOMPLETE_CAPTURE; no se altera para aparentar aceptación. Nombres/bytes exactos del paquete comprobados; los archivos parciales no se reparan ni sobrescriben.

## Causas y ajuste concreto propuesto

En29 de los30 frames incrementales hay retornos de snapshot observados, pero FixtureStore.snapshot devuelve schema/run_id/version/head_sha256 en el nivel superior. El extractor heredado sólo identifica retornos con diccionario head. El digest del retorno no permite reconstruir ahora su UUID. Propuesta para diseño I75: adaptador de ese schema con autoridad propia de fixture Drive y campos ya producidos; no inventar store_id o scope_sha256 ausentes, no nuevas llamadas snapshot ni lecturas de recuperación, no equipararlo a un Store.head o a recuperación integrada.

DI28 no tiene snapshot retornado en el stream. Su fuente define un caso negativo de cleanup/ownership con sentinel. El adaptador anterior no basta para él: se propone diseñar una observación de run_id ligado a FixtureStore.__init__ tras su retorno normal, y una política NEGATIVE_DOMAIN de cleanup por ID exacto. Esa declaración futura no verifica un head, no se observó en I74 y no permite declararlo N/A ni rellenar su identidad retrospectivamente.

Cinco frames contienen operandos no soportados. La fuente indica Paths/contenedores de Paths en dos tests de preview y clases/excepciones en tres tests de hilos. La captura registró retorno exitoso de esos helpers y UNSUPPORTED_OPERAND, **no sus tipos concretos ni valores como metadata de runtime**; el diagnóstico está tipado como explicación estática. Propuesta I75: contrato y matriz para representaciones tipadas/acotadas de esos operandos, con whitelist y hashes/predicados fieles, sin repr, rutas privadas publicadas, coerción arbitraria o digest ficticio. Tipos/schemas no soportados seguirán incompletos, sin exenciones por PASS o grupo unitario.

Las siete políticas I72 funcionaron en su alcance: cinco controles sin Store con N/A sólo de dominio y DF07/DF43 con declaración de construcción observada. Ninguno de esos siete frames tiene missing; esto no acredita head durable ni instrumentación del hijo. Los35 pendientes quedan fuera de esas excepciones, que no se amplían automáticamente.

El ajuste propuesto sólo se presenta: no autoriza diseñar I75, implementar adaptadores, ejecutar nuevos tests o repetir P01. Tras aprobar diseño se prepararán contrato y matriz antes de cualquier implementación; una captura posterior tendrá aprobación y destino nuevos. El paquete I74 queda preservado como evidencia incompleta.

P0 y agregado81/3 intactos; UI01.2/UI04.1/UI09.2 PARTIAL. D1–D4 cerrados e hito D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. D5 global/H07/G01–G07 y GI globales abiertos, histórico30/35 sin promoción. Los PASS aislados no demuestran persistencia o recuperación integrada. Sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue ni D6. Sin publicación ni acceso de red nuevo.
