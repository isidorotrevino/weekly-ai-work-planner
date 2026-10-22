# D5 I24 — contratos y dobles offline G01–G07

Fecha: 2026-10-22. Implementa el primer corte del
[contrato I23](D5-I23-GLOBAL-INTEGRATION-DESIGN.md),
[matriz GI01–GI42](D5-I23-GLOBAL-INTEGRATION-REVIEW.md).
[Resultados propios](../validation/D5-I24-results.md).
**D5 global abierto; hito local I1–I20 y D1–D4 conservados.**

English: standard-library-only synthetic contract models with existing parsers,
in-memory capture/review/effects and Plane/quota doubles. No HTTP, SQL, Docker,
real provider CLI, persistent D2 application or activation. Model results never
establish real provider conformance, durable recovery or global D5 acceptance.

## Autoridad y uso

D5-A59: el usuario aprueba I23 y autoriza implementar/validar exclusivamente el
primer corte offline de 18 criterios, manteniendo G01–G07 abiertos. A54–A58
conservan extracción determinista, autoridad D2, perfiles separados, entrada Drive
textual y bloqueo de escritura Plane sin condición atómica acreditada.
I23 se publicó y verificó en `main` como `5a7ee951616a06a707b86ce3de6ff0984212a16c`.

Desde la raíz, Linux/Python 3 con biblioteca estándar:

```bash
python3 -m unittest discover -s testing/D5 -p test_offline_integration.py -v
python3 -m testing.D5.demo_offline_integration
python3 -m unittest discover -s testing/D5 -v
```

La demo lee únicamente `testing/D5/fixtures/register-before.md`, crea registros
en memoria y emite un resumen sin texto fuente. No acepta URL, contenedor, entorno
`.env`, credencial, petición HTTP o ruta de documento del operador. No guarda
artefactos, cursor o resultados en disco. Terminar el proceso pierde todo el modelo.
Los comandos de pruebas pueden generar caché Python ignorada; no requieren
imágenes, servicios o un bootstrap SQL.

## API y fronteras del modelo

[`source_ingest.offline`](../../source_ingest/offline.py) ofrece:

| Entrada | Comportamiento y límite |
|---|---|
| `MemoryLab.capture` / `capture_drive` | Bytes acotados y parsers existentes sin cambios; ID de artefacto por hash y copias independientes. Fuente/perfil bloqueados conservan bytes, sin revisión aplicable |
| `MemoryDrive` | Catálogo de fixtures con metadatos antes/después y mutación simulada. No es cliente Drive ni implementa páginas/cursor |
| `review(SOURCE/EFFECT/PROJECTION, …)` | Tres registros de revisión separados, con versión esperada. Rechazar/reaceptar invalida pins anteriores; exportación observada exige acknowledgment explícito |
| `prepare_effect` / `apply_effect` | Candidato explícito, UUID/clave elegidos, manifiesto completo y revisión propia; solo muta el diccionario de entidades del modelo |
| `bind_plane` / `prepare_projection` | Binding explícito de instancia sintética, workspace/proyecto, UUID y remoto. Solo TASK; no equivalencia automática de épicas/requisitos con tipos Plane |
| `MemoryPlane.patch` / `apply_projection` | Whitelist abstracta `name`/`description`, base remota completa/hash y copia local revisada. CAS del doble conserva campos ajenos; falta de capacidad o edición concurrente bloquea |
| `evaluate_route` | Validación pura de capacidad/permiso/cuota de fixture. Desconocida, caducada, agotada o fuera de ámbito bloquea; no consume cuota, ejecuta ni hace fallback |
| `summary` | 42 estados de cobertura clasificados; nunca produce aprobación global o afirma que se ejecutaron pruebas |

`SYNTHETIC_ONLY`, `SIMULATED_APPLIED` y `SIMULATED_PROJECTED` identifican efectos
del doble. Los recibos incluyen hashes/IDs y contadores cero de efectos externos;
son hechos del modelo, no evidencia firmada ni acuses Plane. Los diccionarios
retornados son copias. Replay del mismo command_id/request devuelve recibo histórico
sin restaurar contenido; otro request con ese ID da conflicto. No se promete
recuperarlo tras reiniciar el proceso.

Las clases constituyen una API Python de pruebas, no autenticación, aislamiento o
una barrera contra un llamante que altere atributos privados. La revisión simula
la frontera de autoridad; no acredita una identidad humana ni integra roles SQL.
El bloqueo CAS real de A58 sigue intacto: que el doble se configure con CAS no
habilita una instancia real ni implementa un adaptador HTTP.

## Fuentes, identidad y candidatos tipados

Se reutiliza `build_observation` de I1–I3 con `markdown-structure.v1`,
`task-register.v1` y `task-register-compat.v1`. Se conservan límites de bytes,
líneas y objetos; no cambia la gramática. Duplicados/filas ambiguas bloquean el
conjunto y compatibilidad sigue optativa. Checklists sin identidad persistente y
narrativa quedan preview aunque se revise su captura; no se adopta por título/línea.

El registro produce únicamente TASK con Item→title y Objective→description.
Status, Verified, bloqueos, tachado y anotaciones se conservan como evidencia, sin
inferir ejecución, aprobación, épicas o relaciones. Los IDs de candidato I1 no se
convierten en identidad estable entre revisiones.

REQUIREMENT/EPIC se prueban mediante **fixture tipada explícita**, distinta del
formato Gentle-AI: envelope cerrado `d5.offline-envelope.v1`, modo SYNTHETIC_ONLY,
payload `d5.offline-typed-fixture.v1` con `elements`. Cada elemento solo contiene
kind, source_key, title y description; duplicados/campos extra/tipos desconocidos
se rechazan. `source_kind=TYPED_FIXTURE` identifica esta vía, que no se aplica a
un documento real por reconocer texto parecido a JSON. No añade gramática o
marcadores a las muestras privadas.

Los estados iniciales son DRAFT para REQUIREMENT y BACKLOG para EPIC/TASK. EPIC
no recibe description: permanece en la evidencia del candidato. No hay adopción
por similitud ni transferencia. En este corte no se implementan enlaces,
dependencias, ciclos, batch SQL o grooming de negocio; esos criterios siguen pendientes.

## Captura, confidencialidad y evidencia

El doble Drive distingue blob Markdown/texto de Google Docs exportado como texto;
PDF/DOCX o un MIME incompatible quedan bloqueados. Captura cambiante bloquea incluso
si los bytes cambian sin cambiar la etiqueta de versión. OBSERVED_EXPORT conserva
su grado y formato/exportador de fixture: metadatos iguales no prueban atomicidad
ni revisión inmutable. Revisar ese grado no cambia su autoridad.

Envelopes se limitan a 32 MiB; fuentes a los límites I1 (2 MiB y límites de líneas,
longitud/objetos), sin truncar. JSON rechaza duplicados, valores no finitos y campos
no admitidos; errores son códigos fijos. No existe un campo de credencial aceptado
en los contratos de fixture. No se afirma detectar todo secreto posible dentro de
texto arbitrario: **las capturas/manifiestos sí contienen el texto completo** y
permanecen privados en memoria. Demo, recibos y resúmenes evitan emitirlo.

La validación de un flujo instala guardas sobre apertura de archivos, procesos y
sockets para detectar I/O no autorizado durante ese flujo en memoria. Esto se
complementa con la inspección del código; no es una prueba universal de sandbox.
Las lecturas de fixtures del runner ocurren antes de esas guardas.

## Cobertura y continuidad

Se validan con dobles los 18 criterios autorizados:
GI01/GI02/GI03/GI05/GI10/GI13/GI14/GI19/GI21/GI23/GI25/GI26/GI27/GI31/GI32/
GI35/GI37/GI41. La evidencia propia contiene 35 tests nuevos y 51 regresiones
Python existentes; ningún criterio real se presenta como PASS.

Los otros 17 criterios S y los siete R permanecen pendientes. No se implementan
inventario/paginación/cursor durable Drive, creación/conciliación remota UNKNOWN,
cuotas empíricas, durabilidad/reinicio, concurrencia SQL, relaciones de grooming o
campaña real integrada. No se reejecutan SQL/D2/D3/D4 ni se suman sus pruebas previas.
Sin proveedores reales, credenciales, activación, promoción, despliegue ni D6.
