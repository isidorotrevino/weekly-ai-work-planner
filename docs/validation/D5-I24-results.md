# D5 I24 — resultados de contratos offline

Fecha: 2026-10-22. Base: `5a7ee95` publicado en `main`.
[Implementación y uso](../design/D5-I24-OFFLINE-INTEGRATION-LAB.md) ·
[Informe verificable](D5-I24-results.json) ·
[Contrato I23](../design/D5-I23-GLOBAL-INTEGRATION-DESIGN.md).
**PASS sintético offline; G01–G07 y D5 global permanecen abiertos.**

D5-A59 aprueba I23 y autoriza exclusivamente los 18 criterios del primer corte.
Se añaden contratos Python y dobles en memoria; no SQL, HTTP, Docker, CLI de
proveedores, aplicación persistente D2 o activación. Se reutilizan sin cambios los
parsers y fixtures anteriores. No se leyó de nuevo el corpus privado ni se usaron
credenciales/configuración de proveedores.

## Campaña ejecutada

Linux, Python **3.14.4**, biblioteca estándar. Descubrimiento `unittest` de
`testing/D5` (`test*.py`), con resultado por ID conservado en el JSON:

| Grupo | Pruebas | Fallos / errores / omisiones |
|---|---:|---|
| I24 offline nuevo | 35 | 0 / 0 / 0 |
| Python local anterior | 51 | 0 / 0 / 0 |
| Total distinto de esta campaña | **86** | **0 / 0 / 0** |

La demo fija se ejecutó dos veces con salida idéntica. Registra un efecto D2
simulado y una proyección Plane simulada, dos recibos, cero escrituras D2
persistentes y cero solicitudes remotas. El modelo pierde todos sus datos al
terminar; no hay contenedor/volumen que limpiar. El elapsed registrado es una
observación de campaña, no un benchmark o garantía de rendimiento.

No se reejecutan las 264 SQL de I20, las 157 D2 independientes o D3/D4. Sus informes
siguen históricos y no entran en los 86 casos nuevos de esta campaña. Las 51
regresiones Python aquí sí son una ejecución actual, no un número copiado de I20.

## Cobertura de los 18 criterios autorizados

Los IDs de test se vinculan a GIxx en el JSON; un criterio puede tener varios tests.
Todas estas filas son **evidencia de modelo sintético**, no conformance real.

| Criterio | Comprobación observada |
|---|---|
| GI01 | Bytes/hash/localizadores y parsers originales; perfil desconocido conserva bytes y bloquea; compatibilidad optativa; tamper detectado |
| GI02 | Duplicados y separadores ambiguos bloquean toda fuente, sin efecto parcial |
| GI03 | Mover/duplicar checklist no crea identidad persistente ni adopta tarea |
| GI05 | Comandos y routing en el texto permanecen datos; capacidad desconocida y override extra no habilitan ejecución |
| GI10 | Cambio durante captura incluso sin bump de versión bloquea; Docs conserva OBSERVED_EXPORT y exige acknowledgment; PDF/DOCX fuera |
| GI13 | Binding explícito/ámbito correcto; whitelist preserva etiquetas/comentarios/estado remoto y no altera BACKLOG D2 |
| GI14 | Falta de capacidad o valor UNKNOWN bloquean; edición antes/durante CAS se conserva; cambios ajenos no se pierden |
| GI19 | Cuota desconocida/caducada/cero/inválida no concede trabajo; observación no consume ni crea cuota |
| GI21 | Proveedor caído, permiso solo declarado o capacidad incompatible bloquean sin fallback de pago |
| GI23 | JSON cerrado/duplicados/no finitos/campos de credencial rechazados; errores/recibos no hacen eco del texto fuente de prueba |
| GI25 | Narrativa no inventa requisitos/épicas/dependencias; registro solo produce TASK |
| GI26 | Fixture tipada explícita, UUID/clave registrados, sin adopción por título; description de EPIC sigue como evidencia; duplicados/campos extra bloquean |
| GI27 | SOURCE no autoriza EFFECT ni PROJECTION; versiones/rechazo/reaceptación y avance local invalidan pins; claims no deciden workflow |
| GI31 | Los 42 estados se clasifican: 18 modelados, 17 no implementados en este corte, siete de evidencia real pendientes |
| GI32 | Publicación/contrato/aceptación global/activación no son fases de revisión del doble |
| GI35 | G01–G07 permanecen D5 abiertos; la evidencia real no se desplaza a D6 |
| GI37 | Flujo completo por dobles con hashes/identidad; replay no restaura edición posterior; request distinto colisiona; guardas detectan I/O prohibido en el flujo probado |
| GI41 | El resumen declara modelo volátil/sintético, límites y pendientes; no cuenta sus etiquetas como pruebas ejecutadas ni cierre |

Los otros 17 S y los siete R de I23 están **NOT_RUN en I24**. No se validaron feed
incremental/cursor durable, conciliación de creación remota UNKNOWN, relaciones y
ciclos de grooming, concurrencia SQL o comportamiento real de proveedores.

## Preservación y límites

El inventario compara los archivos existentes con la base exacta. Solo se amplían
`docs/README.md` y `testing/D5/README.md`; fuentes/tests/fixtures históricos, SQL,
contratos aprobados e informes/manifiestos de cierre permanecen intactos. Se
comprueban las 245 entradas SHA-256 D3/D4, el documento canónico D4 y las 560
entradas de inputs de las campañas D5 anteriores. Los hashes de índices/guías de
revisiones documentales se contrastan con sus commits, conservando esos informes.

Se verifican enlaces, `git diff --check` y los patrones del chequeo de publicación.
No se publican logs brutos ni snapshots privados; estos chequeos no prueban ausencia
de todo secreto o defecto posible. Capturas/manifiestos del modelo contienen bytes
completos y deben tratarse como privados; el contrato no detecta todo secreto
posible en texto arbitrario. La API en memoria no es autenticación o sandbox de
llamantes Python hostiles y sus recibos no acreditan efectos externos.

D5 sigue abierto. El hito aceptado I1–I20 no se amplía por este PASS y no se
promueven migraciones, despliegan servicios o inicia D6.
