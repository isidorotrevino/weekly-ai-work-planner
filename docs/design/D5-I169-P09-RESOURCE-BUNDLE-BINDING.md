# I169 — P09 preparado; bundle sin admisión y extensión retenida fuera de Reader

Fecha: 2026-11-16, Europe/Madrid. Base:
`d979f5ab7071a6f9a22c6ff93406eaa7b46c6492`.

P09 vincula bytes, hashes y roles del paquete documental de
PFC126-CANDIDATE-03/I122. **No admite el bundle:** faltan atestaciones y aceptación
de recursos; el conjunto exacto vigente rechaza una incorporación directa.
Además, la extensión retenida analizada exige al menos **287.840.292 bytes por
Input Reader**, frente a 268.435.456, bajo el calendario y las premisas descritos
abajo. E01–E05 y D5 siguen abiertos; I122/PJC115-R2 mantienen la no admisión.

## Ruta de revisión

1. Leer los ocho campos de [P09](../validation/D5-PFC126-03-RESOURCE-BUNDLE-BINDING-REVIEW.json).
2. Contrastar el ledger de bytes/SHA, el conjunto congelado y las premisas del grafo.
3. Revisar las cuentas separadas de cada Reader y el alcance de la proyección de metadata.
4. Consultar la [preparación I169](../validation/D5-I169-P09-preparation-review.json),
   el [auditor](../validation/D5-I169-audit.py) y el [sello](../validation/D5-I169-integrity.json).

La selección congela los 236 inputs de P08 más sus ocho registros de salida,
preparación, auditoría y sellado I167/I168: 244 miembros. Incluye los dieciocho
outputs anteriores de I132, sus fuentes y apoyos documentales. No incorpora
los archivos nuevos I169 ni el futuro P10. Es una selección concreta y revisable,
sin afirmar que sea el único empaquetado posible o un grafo final de admisión.

## Proveniencia y consistencia

Cada miembro tiene SHA real, tamaño de sus bytes publicados y rol documental.
El ledger del grafo contrastado abarca 636 rutas: la unión de la selección con
los 490 miembros conocidos del plan I122. Los hashes se verifican contra Git y
los archivos actuales. Hash y publicación no sustituyen firma, confianza,
validez de la atestación o aceptación de la afirmación de recursos.

P02/P03 mantienen identidad de custodio/autoridad, firma, trust anchor y validez
sin acreditar. No se obtiene ni fabrica material externo. Las dieciocho
referencias históricas I127 —intérprete, doce archivos stdlib y cinco
extensiones— se registran como referencias de aquel manifiesto: no se abren,
restatéan, copian o reclasifican como implementación cargada, evidencia actual
del destino, PhaseBytes o lecturas frescas de Reader. Sus binarios no entran
silenciosamente en el grafo de repositorio.

Registry, contrato de capacidad, certificado y manifest I122 conservan sus
schemas, revisión y bindings de fuente. Los valores numéricos coinciden; el
certificado continúa IMPLEMENTED_NOT_ADMITTED y componentes NOT_RUN. PFC126
es un contrato candidato de plataforma, sin reemplazar el contrato de capacidad
que consume el código de admisión. No hay correspondencia aceptada con una
plataforma externa.

El código exige igualdad exacta entre capture_inputs y el conjunto derivado
del registry, fuentes y componentes. Añadir las 146 rutas nuevas directamente
incumpliría esa igualdad. Una eventual incorporación necesitaría revisar y
finalizar registry, certificado, manifest, autoridad y sus pins compatibles;
P09 no realiza ese rebind ni crea sus archivos futuros.

## Grafo concreto y cota inferior de lecturas

| Concepto | Rutas | Bytes actuales congelados |
| --- | ---: | ---: |
| Grafo conocido original I122 | 490 | 87.104.500 |
| Registry/contrato/certificado/manifest excluidos de la cota por posible reescritura | 4 | 121.483 |
| Originales retenidos e inmutables para este análisis | 486 | 86.983.017 |
| Selección adicional, disjunta del grafo original | 146 | 8.963.747 |
| Retenidos fijos más extensión | 632 | 95.946.764 |

La cota se aplica sólo si se retienen esos miembros y bytes, se declaran en un
único manifest futuro del InputPlan, se conserva el mismo Reader físico y se
completan BEFORE, AFTER y finish. La fuente lee físicamente cada miembro antes,
relee la unión después y Reader.finish relee los archivos registrados. Bajo
esas premisas se demuestra el factor tres; no se aplica 3*N a cualquier grafo.
Los checks frescos de targets y late bindings permanecen adicionales.
PhaseBytes es una vista explícita, sin representar una lectura fresca.

Así, 3×95.946.764=287.840.292 bytes. Excede el límite por **19.404.836 bytes**.
Es una cota inferior incluso retirando de la suma los cuatro cuerpos mutables,
la autoridad futura, raw/result/seal de componentes y las lecturas adicionales.
No depende de tratar el upper histórico como consumo exacto.

El antiguo upper worker 266.337.791 y su margen 2.097.665 corresponden al grafo
I122 anterior; no se transfieren a esta extensión. Tampoco se atribuyen a un
Reader nuevo, se resetea su ledger o se eliminan checks frescos para aparentar
fit. El incumplimiento es del paquete retenido bajo estas premisas, sin prueba
de imposibilidad de todos los futuros empaquetados o de CPU/heap/servicio real.

## Cuentas por Reader y metadatos

Coordinador y worker conservan Input Readers separados, cada uno con
file16MiB, unique128MiB, read256MiB y 4096 paths. Cada uno recibe la misma cota
inferior de tres pasadas en el escenario analizado. Los archivos fijos cumplen
su cap individual; los 95.946.764 bytes y 632 paths conocidos quedan por debajo
de los caps unique/path. Esas comprobaciones parciales no demuestran el fit
final y no compensan la violación de read_bytes. Los tamaños y conteos finales,
incluidos cuerpos futuros, continúan desconocidos.

El Evidence Reader permanece separado, con sus límites candidatos de 128MiB
únicos y 297.799.680 bytes leídos. Los documentos fuente de recursos no se
convierten en miembros del paquete de salida. P09 no vuelve a demostrar sus
envelopes ni usa sus cuotas para pagar Input Reader.

La proyección de top metadata parte del modelo histórico I122 de 483.286 bytes,
que contiene widths de referencia, no evidencia real de captura. Añadir las
146 entradas reales SHA/path a cada mapa capture_inputs_before/after aporta
16.871 bytes por mapa, 33.742 en total. Manteniendo todos los demás campos del
modelo iguales, resulta **517.028 bytes**, margen 7.260 frente al allowance
histórico 524.288. No se generan hashes placeholder nuevos ni se publica el
modelo como resultado funcional.

La proyección no acota el metadata final: cambios de autoridad, registry,
certificado/manifest, nuevas atestaciones, P09/P10 y demás variaciones exigen
recalcular bytes, pins, maps, contexto, launcher y paquete finales. Quedan null
los tamaños finales; no hay aceptación derivada del margen parcial.

## Ciclos, disposición y límites

P09 no incluye su propio hash ni bytes en la selección congelada. P10 aún no
existe. Inputs congelados preceden a P09; preparación y sello lo pueden fijar
después, sin hash de vuelta. El sello excluye su propio hash. La autoridad no
puede autopinnearse y el certificado excluye su propio hash. Un futuro rebind
requiere ordenar y revisar el grafo final, no reciclar autoridad I71/I77/I86/I89/I92
ni transformar INVALID_CAPTURE o NOT_RUN en evidencia nueva.

Los ocho campos están preparados pero son insuficientes para aceptación del
bundle completo. P02/P03/P05/P06/P07/P08 conservan su no aceptación de recursos.
P10 sigue sin producirse. No se atribuye revisión independiente de proveniencia/
Reader ni autoridad de custodio a este asistente. El bloqueo por evidencia
externa y el incumplimiento concreto de read_bytes quedan registrados; no se
autoriza cambiar cuotas, fuentes, contrato, empaquetado o capture_inputs.

E01–E05 abiertas; E06 separado NOT_RUN y sin autorización de ejecución. I122
conserva IMPLEMENTED_NOT_ADMITTED, sin SOURCE_CAPACITY_VERIFIED, propuesta o
captura habilitadas, rebind o autoridad/destino nuevos. D5/H07 de cierre abiertos;
IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1; D1–D4 e
I1–I20/A52 intactos; brechas globales y reales pendientes. I86/I89/I92
INVALID_CAPTURE no se reanudan ni mezclan.

## Verificación y publicación

`python3 docs/validation/D5-I169-audit.py`: resultado esperado
PASS_STATIC_SOURCE_ONLY. Contrasta 636 pins contra Git, diez anclas AST, bytes,
intersecciones, bindings, límites, cota inferior y proyección condicional de
metadata. Preserva 323 archivos publicados e inputs heredados. No importa,
compila o ejecuta producto/candidata/componentes ni el calendario Reader.

Unidad de cinco archivos: P09, preparación, este documento, auditor y sello.
Rollback limitado a esos cinco archivos enumerados en work_unit. El diff supera
400 líneas por el ledger real y auditor autocontenido; el exceso queda informado.
Runtime harness N/A: preparación documental sin cambio runtime. Auditoría antes
del stage y después del commit, push autorizado y verificación de remoto/árbol
limpio. Publicar el expediente no admite la candidata.

Sólo herramientas documentales Git/JSON/AST. Sin tests, benchmarks, schedule,
introspección o mediciones de runtime/plataforma. Sin modificar fuentes, cuotas,
reservas, presupuestos, contrato o inputs. Sin inspeccionar ni limpiar
dev/run_data/D4; sin proveedores, credenciales, consumo, activación, promoción,
despliegue o D6.
