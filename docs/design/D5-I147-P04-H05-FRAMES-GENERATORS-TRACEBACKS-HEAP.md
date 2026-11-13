# I147 — H05 preparado sin cota completa de heap

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`a79acf8cdee443af5321bfc2b204e2d63af2a4f1`.

**P04-H05 queda preparado como expediente de evidencia insuficiente.** No hay
upper completo de heap de marcos, generadores y tracebacks ni ajuste verificado
a 134217728 bytes (128 MiB). E02 sigue abierta y PFC126-CANDIDATE-03/I122/PJC115-R2
mantienen la no admisión. El presupuesto permanece candidato, sin aplicarse como cuota.

## Ruta de comprobación

1. Leer los nueve campos y el dictamen del [expediente H05](../validation/D5-PFC126-03-E02-H05.json).
2. Contrastar el índice AST, doce proyecciones y anclas en la [revisión de preparación](../validation/D5-I147-P04-H05-preparation-review.json) y su output vinculado.
3. Ejecutar sólo el [auditor documental](../validation/D5-I147-audit.py): `python3 docs/validation/D5-I147-audit.py`.

Dos campos son definiciones documentales; siete siguen insuficientes. P01
independiente/P02 exacto permanecen pendientes. P03 disponibilidad y H01–H04 no
sustituyen la derivación H05. El productor es el asistente del chat, sin autoridad
de custodio o aceptación independiente. Sólo se revisan registros/fuentes
vinculados, sin contactos, muestreo actual o afirmación de ausencia global.

## Separaciones que conserva el expediente

| Dato o dominio | Alcance y límite |
| --- | --- |
| Heap dinámico de activación | H05 necesita el modelo exacto de materialización/backing y los bytes solicitados vivos pertinentes del worker |
| Stack nativo/RSS | Cuenta separada; no se renombran como heap ni se omite backing dinámico por llamarlo «stack» |
| `frames=4096` | Límite candidato de records de captura en self.frames; no es un inventario de marcos VM/Python vivos |
| `depth=32` | Guardia candidata de profundidad de datos; no acota por sí sola toda la pila de llamadas, marcos o almacenamiento |
| F/S y generaciones I124 | Se conservan 52018/1759, 53777 lotes y 53778 generaciones con inicial, sin convertirlos en tamaños o multiplicidades de marcos |
| Definiciones/generadores/comprehensions | Sintaxis, sin equivalencia automática de una declaración/llamada/comprehension a un objeto de heap de tamaño fijo |

El ABI y la identidad de intérprete/nativo exactos siguen sin aceptar. Faltan
modelos de materialización de marcos, backing dinámico, generadores/iteradores,
tracebacks/excepciones y su correspondencia con stack/heap/allocator. Los
metadatos históricos no los aportan; no se consulta el intérprete actual para llenarlos.

## Cobertura por justificar

Doce clases registran requisitos, sin declarar inventario completo o disjunto:

| Clase | Cardinalidad, tamaño y vida que faltan |
| --- | --- |
| R01 | Activaciones, marcos materializados y backing en el dominio de heap exacto |
| R02 | Activaciones recursivas de clone/digest/traversal, locales y operandos |
| R03 | Generadores de expresiones, suspensión/retoma, locales e iteradores retenidos |
| R04 | Otra iteración/suspensión y rutas generator/coroutine/native seleccionadas |
| R05 | Cadenas de traceback y referencias a marcos durante excepciones/rechazos |
| R06 | Carriers de excepción, args/context/cause y límites con payloads retenidos |
| R07 | Locales/celdas/backlinks y ciclos que mantienen draft/memo/valores/originales |
| R08 | Activaciones parciales de fork/IO/rechazo y errores capturados o relanzados |
| R09 | Estado post-return/exhaustion/except, caches o destrucción diferida |
| R10 | Activaciones de suite/framework, callbacks y wrappers durante toda la ruta |
| R11 | Estado de heap por thread participante, con hijos y stack separados |
| R12 | Soporte nativo, finalización/GC o rutas ocultas/residuales no encerradas |

Cada fila mantiene null cardinalidad completa, tamaño, pico y derivación de vida:
48 campos desconocidos del inventario, no todas las carencias. La enumeración no
materializa una prueba ni reabre los conteos fuente I124. Una derivación completa
debe identificar representaciones realmente seleccionadas, multiplicidades
activas/suspendidas/retenidas y coexistencia, antes de comparar su upper a 128 MiB.

## Contraste fuente, sin introspección de marcos

Se verifican 155 pins con blobs Git y bytes actuales, doce proyecciones JSON y
79 fuentes Python originales/observador del ámbito estático de P01/P02. El
índice registra por archivo definiciones, generadores/comprehensions, yields,
handlers y raises, con hash del vector completo. Incluye ramas anidadas o no
seleccionadas: no prueba ejecución, cierre stdlib/nativo ni ausencia de otros
mecanismos de activación. Ceros sintácticos no significan ausencia en el objetivo.

Doce anclas fijan clone/proxy, _atomic/_observe/finish/wrap_boundary, strict_json,
digest/visit, start de metadatos y worker.exercise/main. Se identifican cuatro
expresiones generadoras en clone_metadata. No se consumen generadores ni se
construyen marcos para medirlos. Tampoco se compila el objetivo o se usan tracing,
sys._getframe, introspección de frames, sizeof/tracemalloc o cambios de recursion limit.

_atomic declara error=ex y raise error, además de locales draft/writes/value y
retorno de resultados; requiere cubrir posibles carriers/referents retenidos
por excepción y IO. _observe capturando y retornando None no prueba colección
completa. Worker exercise/finally/restore y los caminos de finish tampoco
justifican liberación inmediata de todos los generadores, tracebacks o locales.
No se afirma que todo handler retenga para siempre: esas vidas necesitan prueba.

## Propiedad y dictamen

Diez fronteras H01–H04/H06–H11 siguen sin resolver. El carrier frame/traceback no
paga los grafos originales, memo/draft, Reader, páginas o buffers a los que apunta;
sus propietarios tampoco pagan automáticamente el carrier. Runtime, callbacks,
codecs/temporales y backing nativo necesitan correspondencia. H11 no es reserva
libre. No se descuentan aliases/interning ni se fusionan witnesses, y se permite
sobreconteo conservador con cobertura sustentada.

Se conserva el ámbito P01/I124 y prefijos de rechazo aplicables, sin hooks,
instrumentación o control original inesperado nuevos. Upper completo/derivación,
fits y slack siguen null: NOT_EVALUABLE_NO_COMPLETE_H05_BOUND, sin ajuste,
sobrepresupuesto, memoria ilimitada o inviabilidad demostrados. Se aplica el
rechazo I132; los cuatro criterios E02 conservan clasificación sin cierres.

E01–E05 siguen abiertas; E06 separado, pendiente, NOT_RUN y sin permiso. Otros
12 outputs siguen ausentes, sin iniciar paquetes. Fuentes, candidata03,
plan/paquetes anteriores, cuotas/presupuestos/reservas, certificado
IMPLEMENTED_NOT_ADMITTED, capture_inputs y autoridad/destino intactos. Sin
SOURCE_CAPACITY_VERIFIED o captura habilitada. D5/H07 abiertos e IR03 NOT_READY.
P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados.
Brechas/obligaciones reales pendientes; I86/I89/I92 INVALID_CAPTURE sin reanudar
ni mezclar. Sin proveedores, credenciales, consumo, reservas operativas,
activación, promoción, despliegue o D6. No se inspecciona ni limpia dev/run_data/D4.

## Verificación y unidad de commit

El [sello I147](../validation/D5-I147-integrity.json) fija cuatro artefactos sin
self pin. Resultado comprobado: PASS_STATIC_SOURCE_ONLY, H05 no verificado,
cero cierres, producto/componentes ejecutados cero y cuotas intactas. El auditor
conserva 213 archivos publicados e inputs heredados. JSON/AST e índices no
prueban heap, identidad, capacidad, CPU/tiempo o independencia.

Se publica una unidad documental de cinco archivos. El diff supera 400 líneas
orientativas por evidencia generada y verificación autocontenida; se informa el
exceso sin comprimir código o borrar evidencia. Runtime harness: N/A, fase
documental sin cambio de frontera runtime; producto/componentes prohibidos,
sin builds/imports de objetivo/discovery/benchmarks/sondeos. Rollback: retirar
sólo los cinco archivos I147 enumerados en work_unit de la revisión. Se hace
commit y push, con auditoría antes del stage y después del commit y verificación
de remoto efectivo y árbol limpio.
