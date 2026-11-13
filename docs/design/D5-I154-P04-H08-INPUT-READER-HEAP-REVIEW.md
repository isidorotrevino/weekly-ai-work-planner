# I154 — H08 revisado, sin cota completa ni ajuste demostrado

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`4bb168540f6c801cecc5d18ece919b764536b51a`.

**La revisión confirma el dictamen de insuficiencia de P04-H08.** El expediente
negativo es documentalmente coherente y no requiere cambiar H08. La subcota
histórica de payload sigue sin demostrar el heap completo de Input Reader y
PhaseBytes: upper, ajuste a **536870912 bytes (512 MiB)** y slack desconocidos.
E02 permanece abierta; PFC126-CANDIDATE-03/I122/PJC115-R2 mantienen la no admisión.
H08 y el presupuesto candidato conservan sus bytes, sin cuotas o reservas nuevas.

## Ruta de revisión

1. Leer los quince controles y nueve disposiciones de campo en la [revisión I154](../validation/D5-I154-P04-H08-documentary-review.json).
2. Contrastar blobs, vectores y comprobaciones en la [reconstrucción I154](../validation/D5-I154-P04-H08-source-reconstruction.json).
3. Consultar [H08](../validation/D5-PFC126-03-E02-H08.json) para las clases requeridas, dependencias y fronteras pendientes.

Este mismo asistente preparó I153. El recorrido separado del AST aporta
contraste documental, sin acreditar independencia de actor/organización,
autoridad de custodio o aceptación independiente de memoria.

## Aritmética histórica y procedencia

La reconstrucción concuerda con **180 pins**, doce proyecciones JSON, 79 fuentes,
veinte anclas y los vectores sintácticos por archivo/globales. Los pins incluyen
el registro histórico de vinculación I122. Su declaración de 490 archivos y
87104500 bytes no equivale a revalidar ahora los 490 cuerpos de archivo ni a
crear una nueva unión de inputs del repositorio actual.

| Operación sobre el modelo I122 | Resultado |
| --- | ---: |
| Cuatro anchos de metadatos futuros sumados | 57277 bytes |
| R = 3×(87104500+57277)+4852460 | 266337791 bytes de lectura del worker |
| 268435456−R | 2097665 bytes de margen de lectura física |
| 2R, payload chunks + join del grafo fijo exitoso | 532675582 bytes |
| 536870912−2R | 4195330 bytes de diferencia aritmética |

**La diferencia aritmética no es slack de heap.** Los metadatos futuros siguen
sin crear; sus anchos son modelos condicionados, sin hashes reales o resultados
de ejecución. La lectura del launcher, 261485331 bytes, es otra cuenta. Ni esa
cuenta ni el margen del contador físico se suman o convierten en heap del worker.

Los cambios de input o protocolo requieren revisar U y pins de los bytes finales.
La regla +3×nuevos_bytes depende de conservar un grafo válido de tres pasadas;
no autoriza incorporaciones automáticas. I153/I154 no entran en capture_inputs,
no se reescriben inputs, no se crean futuros outputs ni se habilita captura.

## Fuente, fases y vidas

Se clasifican ocho relaciones: guarda/open, contador/check, read/append,
metadatos/join, listing/check, lectura/reemplazo de vista, lectura/inserción de
mapa y rechecks/flag FINISHED. No son ocho asignaciones sin guardas ni pruebas
de liberación. Los nueve registros de expresiones coinciden con el AST fijado.

Reader conserva controles iniciales de tamaño y de bytes, reads acotados por
min(left,65536), append, sonda EOF y join final. files[name] guarda fingerprint y
digest, sin constituir un caché de cuerpos crudos en ese mapa. Eso no impide que
otras raíces, como joint_plan/view/bodies, retengan bytes. Listing construye
os.listdir, sorted y tuple antes del control de cantidad; faltan tamaños y
vidas de nombres, capacidades y scratch, incluidos prefijos rechazados.

PhaseBytes copia el mapa mediante dict(bodies), devuelve el body ya guardado y
delega listing en Reader. Su read no llama a Reader.read. El bucle after usa las
claves de la vista anterior y hace lecturas frescas antes de reemplazar self.view.
Esta estructura no prueba inmutabilidad profunda, frescura de un body almacenado,
reutilización gratuita, liberación inmediata o un máximo fijo de una/dos vistas.

Reader.finish vuelve a leer/listar y InputPlan.finish usa el mismo Reader. El
worker declara c.Reader; MemberReader tiene caps/lock de evidencia propios.
No se transfieren esas propiedades al Input Reader ni se deduce serialización
de todas las vidas o suma de heaps de padre/worker. Se comprueba fuente, sin
ejecutar lecturas ni atribuir exhaustivamente dispatch o asignaciones del runtime.

## Disposición y límites

Doce requisitos mantienen **48 valores null** de cardinalidad, tamaño, pico y
vida completos. Diez fronteras H01–H07/H09–H11 siguen sin resolver: headers,
mapas, paths/stat/hash, chunks/bodies, codecs, carriers, páginas, salida y nativo
precisan asignación explícita. El payload exitoso no cubre por sí solo listings,
sondas fallidas, árboles de error o retención concurrente. H11 no es reserva
libre; sin descuentos por alias, interning, fusión de witnesses o GC supuesto.

F≤52018, S≤1759, 53777 lotes y 53778 generaciones con inicial conservan el
contexto condicional P01/I124, sin convertirse en número de lecturas o cuerpos
vivos. P01 independiente, P02 exacto y P03 siguen pendientes. La carencia se
refiere al material suministrado, sin afirmar ausencia global o inviabilidad.

Los nueve campos conservan dos definiciones documentales y siete disposiciones
insuficientes. Los cuatro criterios E02 no cierran. Se mantiene el rechazo I132
contra convertir 532675582 bytes de payload en prueba completa de 512 MiB.
Upper, ajuste y slack siguen null; no se prueba sobrepresupuesto real, memoria
ilimitada, capacidad o servicio. Nueve outputs continúan ausentes, sin iniciar
otro paquete.

E01–E05 abiertas; E06 separado, pendiente, NOT_RUN y sin permiso de ejecución.
I122 conserva IMPLEMENTED_NOT_ADMITTED; sin SOURCE_CAPACITY_VERIFIED, propuesta
o captura. D5/H07 de cierre abiertos e IR03 NOT_READY. P0 conserva
83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados y brechas/
obligaciones reales pendientes. I86/I89/I92 INVALID_CAPTURE sin reanudar ni mezclar.

## Verificación y publicación

`python3 docs/validation/D5-I154-audit.py`: **PASS_STATIC_SOURCE_ONLY**.
Verifica Git/JSON/AST y coherencia del dictamen negativo, con **248 archivos
publicados** e inputs heredados preservados. No prueba heap, ABI, vidas,
capacidad, CPU/tiempo o independencia.

Cinco archivos I154 forman una unidad: este documento, revisión, reconstrucción,
[auditor](../validation/D5-I154-audit.py) y [sello](../validation/D5-I154-integrity.json).
El diff supera 400 líneas por evidencia generada y auditoría autocontenida;
se informa el exceso sin comprimir código o retirar evidencia. Runtime harness:
N/A, sin cambio de comportamiento runtime. Rollback: retirar sólo los cinco
archivos enumerados en work_unit. Se audita antes del stage y después del commit,
con push y verificación de remoto efectivo y árbol limpio.

Sin producto/componentes importados, compilados o ejecutados, tests, benchmarks,
introspección, instrumentación o sondeos de Reader/IO/runtime/memoria. Fuentes,
candidata03, cuotas, presupuestos, reservas, capture_inputs y autoridad/destino
intactos. Sin recursos reservados, contactos externos, proveedores, credenciales,
consumo, activación, promoción, despliegue o D6. No se inspecciona ni limpia
dev/run_data/D4.
