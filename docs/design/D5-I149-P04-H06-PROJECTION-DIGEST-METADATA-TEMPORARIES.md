# I149 — H06 preparado, sin cota completa de temporales

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`dd2db0ca8a4e168f148a91734656e397c503b159`.

**P04-H06 queda preparado como expediente de insuficiencia.** Las fuentes fijadas
identifican temporales de proyección, digest y operaciones de metadatos, incluidas
construcciones anteriores a guardas. No demuestran el pico completo de heap
solicitado vivo ni su ajuste a **268435456 bytes (256 MiB)**. Upper, ajuste y slack
permanecen desconocidos; E02 abierta y PFC126-CANDIDATE-03/I122/PJC115-R2 sin
admisión. El presupuesto sigue siendo candidato, sin aplicarlo como cuota.

## Ruta de revisión

1. Leer los nueve campos y la disposición en [H06](../validation/D5-PFC126-03-E02-H06.json).
2. Contrastar `source_evidence`: blobs de Git, doce proyecciones, anclas y orden léxico.
3. Revisar las carencias y progreso en la [preparación I149](../validation/D5-I149-P04-H06-preparation-review.json).

El plan I132 y los paquetes anteriores conservan sus bytes. Su estado histórico
PLANNED_NOT_PRODUCED no se reescribe: el progreso documental actual se registra
en I149. La preparación por este asistente no constituye aceptación por el
revisor independiente de memoria previsto en el plan ni autoridad de custodio.

## Construcción antes de las guardas

| Sitio fuente | Evidencia estática y límite de la inferencia |
| --- | --- |
| digest_value.visit | sorted(x), parts y sorted(parts) requieren listas/registros y scratch; sus bytes no se deducen del contador de representación digerida |
| digest_value.add / Projector.observe.leaf | chunk.encode() y canonical(node) se evalúan como argumentos antes de que add/emit cobren su longitud; falta el almacenamiento previo y el de soporte |
| Projector.observe.visit | texto lexical antes de comprobar longitud y chunk codificado antes de charge; falta el modelo exacto de pathlib, HMAC, Unicode y codec |
| canonical_hash / store_request / drive_request | digest previo no elimina la construcción de body antes de su comprobación posterior; falta la coexistencia con entradas, árboles y workspace |
| legacy_selectors | out recibe campos antes del máximo seleccionado; la guarda no prueba el pico de construcción en prefijos rechazados |
| CausalState / DomainState | filas, grupos, records, listas y ordenación pueden preceder a row_budget/charge o publicarse en drafts; falta propiedad y vida por operación |
| Bindings.check | snapshots rows/states son asignaciones de operación; los contadores de clones no las cubren por sí solos |
| _typed_finish / PageSink.append / Pages.flush | out, b o body se construyen antes del control de longitud; requieren correspondencia con H07/H09/H10 y sus vidas |

Hay **trece relaciones de orden léxico** y siete expresiones vinculadas, con
líneas, hashes AST y pins de fuente. Incluyen orden hacia una publicación y no
sólo guardas. Son evidencia de sintaxis y dependencias de evaluación; no prueban
alcanzabilidad, frecuencia, máximo de asignación, tiempo de liberación o que una
guarda sea el primer control aplicable. Los validadores previos se conservan,
pero no sustituyen una derivación completa de almacenamiento y coexistencia.

El censo de 79 fuentes cuenta 23802 Call, 835 List, 3096 Tuple, 493 Dict,
146 Set, 224/45/175 ListComp/SetComp/DictComp, 389 GeneratorExp y 217 handlers.
Son sitios sintácticos, sin convertirlos en invocaciones, objetos materiales,
bytes, cierre stdlib/nativo o demostración de cobertura completa del runtime.
Las 28 anclas seleccionadas permiten comprobar las afirmaciones locales.

## Inventario y vidas pendientes

H06 registra doce requisitos: estado de digest, ordenación de claves,
agregación por elemento, fragmentos escalares, proyección tipada, argumentos y
selectores, transformaciones de requests/receipts, filas/grupos, bindings/setup,
finalización/rechecks, demanda original/nativa no clonada y prefijos retenidos
o rechazados. Cada requisito conserva null en cardinalidad completa, tamaño,
pico vivo y derivación de vida: **48 valores desconocidos** del inventario.
Son requisitos de cobertura, no doce clases exhaustivas ya demostradas.

Se conservan F≤52018, S≤1759, 53777 lotes y 53778 generaciones con inicial bajo
los supuestos heredados de P01/I124. Esas cotas de clonación no son un conteo
completo de operaciones no clonadas ni de sus temporales vivos. No se multiplica
un tamaño supuesto por F/S para declarar completo H06. Tampoco se confunden
operand_bytes, depth, refs, frames, tamaño de archivo o payload serializado con
una cota de heap del propietario.

Para completar la prueba se necesita, en cada estado aplicable del worker,
acotar la suma del tamaño solicitado de cada bloque vivo asignado a H06. Falta
derivar tamaños/capacidades/growth, scratch nativo y de ordenación, multiplicidad
y coexistencia de operaciones originales y del observador, y retención en
prefijos de error. Se admite sobreconteo conservador explícito, sin hacer cero
un término desconocido ni descontar por alias, interning o fusión de witnesses.

La exclusión mutua de metadatos no serializa todas las vidas del worker:
originales e I/O están fuera de esa fase, y pueden persistir locales, errores o
grafos anteriores. Llamar «temporal» a un valor, retornar o ejecutar cleanup no
demuestra liberación inmediata. No se afirma tampoco retención eterna de todo
temporal: ambas conclusiones exigirían evidencia que aquí falta.

## Fronteras y disposición

Las diez fronteras con H01–H05 y H07–H11 permanecen sin resolver. Hay que asignar
explícitamente baseline nativo, originales, filas publicadas, clones, carriers de
marcos/tracebacks, codecs/árboles, Reader, páginas y salida. Una referencia desde
un temporal no paga su referente; un clone tampoco paga automáticamente el sort
o la proyección que lo acompaña. Los sitios de encode/flush no completan H07/H09
ni permiten omitir esas asignaciones de la cuenta conjunta. H11 no es reserva
libre. Se hereda la separación entre heap del worker y otros procesos de P01.

P01 sigue pendiente de aceptación independiente; P02 no aporta aún la identidad
y el modelo exacto de asignación/ABI necesarios. P03 y los otros propietarios no
sustituyen la demanda H06. La falta de prueba en el material suministrado no es
una afirmación de ausencia global, sobrepresupuesto real o inviabilidad.

Los nueve campos requeridos están presentes: dos definiciones documentales y
siete insuficientes para aceptación. Se aplica la regla I132 contra inferir una
cota a partir del umbral de rechazo. No hay prueba completa, ajuste, slack,
aceptación independiente ni cierre de obligaciones de recursos. Quedan once
outputs del plan sin producir; no se inicia otro paquete en I149.

E01–E05 continúan abiertas y E06 separado, pendiente, NOT_RUN y sin autorización
de ejecución. I122 conserva IMPLEMENTED_NOT_ADMITTED; no se emite
SOURCE_CAPACITY_VERIFIED ni se habilitan propuesta o captura. D5/H07 abiertos,
IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e
I1–I20/A52 aceptados, con brechas y obligaciones reales pendientes.
I86/I89/I92 INVALID_CAPTURE no se reanudan ni mezclan.

## Verificación y unidad de publicación

`python3 docs/validation/D5-I149-audit.py` contrasta Git/JSON/AST sin importar,
compilar, ejecutar ni introspeccionar producto o componentes. Verifica 163 pins,
doce proyecciones, los sitios y relaciones de orden, presupuesto, carencias,
no admisión e integridad de **223 archivos publicados** y de inputs heredados.
Resultado: **PASS_STATIC_SOURCE_ONLY**. Sin tests, campañas, benchmarks,
instrumentación ni sondeos de runtime, memoria o plataforma.

Cinco archivos forman una unidad documental: H06, revisión de preparación,
este documento, [auditor](../validation/D5-I149-audit.py) y
[sello](../validation/D5-I149-integrity.json). El diff supera 400 líneas por
evidencia generada y auditoría autocontenida; se informa el exceso sin comprimir
código o eliminar evidencia. Runtime harness: N/A, sin cambio de comportamiento
runtime. Rollback: retirar sólo esos cinco archivos enumerados en work_unit.
Se verifica antes del stage y después del commit, con push y comprobación de
remoto efectivo y árbol limpio.

Fuentes, candidata03, planes, paquetes previos, cuotas, presupuestos, reservas,
capture_inputs y autoridad/destino permanecen intactos. Sin recursos reservados,
contactos externos, proveedores, credenciales, consumo, activación, promoción,
despliegue o D6. No se inspecciona ni limpia dev/run_data/D4.
