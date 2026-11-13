# I152 — H07 revisado, sin cota completa ni ajuste demostrado

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`d8acb2bf24a2a70240f0bd9cf3fc9a30f1c007a8`.

**La revisión confirma el dictamen de insuficiencia de P04-H07.** El expediente
negativo es documentalmente coherente y no requiere cambiar H07. La prueba de
heap completo de codecs JSON/Unicode, fragmentos y árboles decodificados sigue
rechazada: upper, ajuste a **268435456 bytes (256 MiB)** y slack desconocidos.
E02 permanece abierta; PFC126-CANDIDATE-03/I122/PJC115-R2 mantienen la no admisión.
El presupuesto candidato y H07 conservan sus bytes, sin aplicar cuotas o reservas.

## Ruta de revisión

1. Leer los quince controles y nueve disposiciones de campo en la [revisión I152](../validation/D5-I152-P04-H07-documentary-review.json).
2. Contrastar blobs, vectores y comprobaciones fuente en la [reconstrucción I152](../validation/D5-I152-P04-H07-source-reconstruction.json).
3. Consultar [H07](../validation/D5-PFC126-03-E02-H07.json) para los requisitos, dependencias y fronteras pendientes.

Este mismo asistente preparó I151. Un recorrido separado del AST aporta
contraste documental, sin acreditar independencia de actor/organización,
autoridad de custodio o aceptación del revisor independiente de memoria.

## Qué queda contrastado

| Área | Resultado y límite |
| --- | --- |
| Identidad | I132 y candidata03 concuerdan con H07, unidad de bytes exactos y métrica requested-live del worker |
| Procedencia | Blob publicado H07 y 171 pins coinciden con Git de preparación y bytes actuales |
| Evidencia | Doce proyecciones JSON, 79 fuentes, 22 anclas, censo sintáctico y hashes de vectores concordantes |
| Orden | Ocho relaciones y ocho registros de expresiones; W01 conserva una guarda anterior al decode |
| strict_json | Escaneo antes de loads; check(out) después de parse satisfactorio; guarda de duplicados antes de insertar en el dict del hook |
| Pipelines | Sitios de dumps/encode, raw/getvalue/parse/finish y sidecar encode/validación/write concordantes |
| Inventario | Doce requisitos con 48 valores desconocidos, sin cota completa de cantidad/tamaño/pico/vida |
| Propiedad | Diez fronteras H01–H06/H08–H11 siguen pendientes, con scope P01/I124 heredado |

El índice de grafías reproduce 106 json.dumps, 154 json.loads, cero json.dump/
load, 48 atributos encode, 24 decode y uno iterencode. Son nombres de llamada
en las fuentes fijadas: no resuelven aliases, dispatch, codec real, acelerador
nativo o frecuencia. Los ceros no demuestran ausencia en todo el runtime.

La primera relación es byte guard antes del escaneo decode; las ocho relaciones
no son ocho asignaciones anteriores a toda guarda. Se conservan file_bytes,
profundidad y validadores previos. Tras un parse satisfactorio, check(out)
comprueba strings y árbol: esa comprobación posterior no aporta por sí sola la
asignación pico anterior. Los callbacks pairs/reject están vinculados por nombre
en loads, pero su firma no prueba el almacenamiento concreto de argumentos,
estructuras internas, árboles parciales o errores del parser seleccionado.

## Buffers, vidas y procesos

Los sitios de dumps→encode y canonical concuerdan con H07. Texto, UTF8/ASCII y
longitud serializada no sustituyen headers, capacidades, growth, fragmentos,
scratch nativo y árboles decodificados. No se aplica un factor fijo de Unicode.
El bucle del escaneo decode acaba antes del sitio de parse en la fuente; no
demuestra reutilización, liberación inmediata ni que todo el texto del escaneo
coexista con todo el árbol completo. Ambas inferencias de vida siguen abiertas.

worker.exercise contiene getvalue().encode()→strict_json y rec.finish(raw).
SideWriter.write ordena encode, guarda de bytes, read_sidecar y write_all.
worker.main llama al writer; el launcher tiene dos llamadas a read_sidecar en
sus caminos normal/error. Se comprueba contexto fuente, sin atribución exhaustiva
de runtime ni suma automática del heap del padre al worker. Descartar el retorno
de validación tampoco demuestra cuándo desaparecen sus árboles y temporales.

F≤52018, S≤1759, 53777 lotes y 53778 generaciones con inicial conservan el
alcance condicional P01/I124. No pasan a ser multiplicidad completa de operaciones
codec o árboles vivos. Retorno, cleanup y nombre «temporal» no prueban liberación
inmediata ni retención eterna; falta el modelo de vidas y concurrencia aplicable.

Las diez fronteras conservan sin resolver baseline nativo, originales, roots,
clones, carriers, proyección/digest, Reader, páginas, salida y overhead. Hay que
asignar bloques y vidas explícitamente, incluidos prefijos rechazados. Un carrier
no paga su referente ni H11 suministra reserva libre. Sin descuentos por alias,
interning o fusión de witnesses; el sobreconteo conservador requiere cobertura.

## Disposición y publicación

Los nueve campos siguen presentes: dos definiciones documentales y siete
insuficientes. Los cuatro criterios E02 conservan su clasificación sin cierres.
Se mantiene el rechazo I132 contra rebautizar cotas de texto/UTF8/serialización
como heap completo. Upper, ajuste y slack null: no se prueba sobrepresupuesto
real, memoria ilimitada, inviabilidad, capacidad o servicio. P01 independiente,
P02 exacto y P03 siguen pendientes; este expediente no los sustituye ni afirma
ausencia global de evidencia.

E01–E05 abiertas; E06 separado, pendiente, NOT_RUN y sin autorización de
ejecución. Diez outputs continúan ausentes, sin iniciar otro paquete. I122 sigue
IMPLEMENTED_NOT_ADMITTED, sin SOURCE_CAPACITY_VERIFIED, propuesta o captura.
D5/H07 de cierre abiertos e IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/
1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados y brechas/obligaciones reales
pendientes. I86/I89/I92 INVALID_CAPTURE no se reanudan ni mezclan.

`python3 docs/validation/D5-I152-audit.py`: **PASS_STATIC_SOURCE_ONLY**.
Verifica Git/JSON/AST y coherencia del dictamen negativo, con **238 archivos
publicados** e inputs heredados preservados. No prueba heap, ABI, vidas,
capacidad, CPU/tiempo o independencia.

Cinco archivos I152 forman una unidad de revisión: este documento, revisión,
reconstrucción, [auditor](../validation/D5-I152-audit.py) y
[sello](../validation/D5-I152-integrity.json). El diff supera 400 líneas por
evidencia generada y auditoría autocontenida; se informa el exceso sin comprimir
código o retirar evidencia. Runtime harness: N/A, sin cambio de comportamiento
runtime. Rollback: retirar sólo los cinco archivos enumerados en work_unit.
Se audita antes del stage y después del commit, con push y verificación del
remoto efectivo y árbol limpio.

Sin producto/componentes importados, compilados o ejecutados, tests, benchmarks,
introspección, instrumentación o sondeos de runtime/plataforma. Fuentes,
candidata03, cuotas, presupuestos, reservas, capture_inputs y autoridad/destino
intactos. Sin recursos reservados, contactos externos, proveedores, credenciales,
consumo, activación, promoción, despliegue o D6. No se inspecciona ni limpia
dev/run_data/D4.
