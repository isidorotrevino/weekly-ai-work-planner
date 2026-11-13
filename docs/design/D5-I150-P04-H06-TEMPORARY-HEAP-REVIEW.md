# I150 — H06 revisado, sin cota completa ni ajuste demostrado

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`89c341ff6e45c273fbcdfdf5b33952f0a0221f6a`.

**La revisión confirma el dictamen de insuficiencia de P04-H06.** El expediente
negativo es documentalmente coherente, sin defectos bloqueantes que requieran
cambiar H06. No se acepta una prueba completa de heap de temporales: upper,
ajuste a **268435456 bytes (256 MiB)** y slack siguen desconocidos. E02 permanece
abierta; PFC126-CANDIDATE-03/I122/PJC115-R2 mantienen la no admisión. El
presupuesto candidato y todos los archivos publicados conservan sus bytes.

## Ruta de revisión

1. Leer los quince controles y nueve disposiciones de campo en la [revisión I150](../validation/D5-I150-P04-H06-documentary-review.json).
2. Contrastar blobs, proyecciones y sitios en la [reconstrucción I150](../validation/D5-I150-P04-H06-source-reconstruction.json).
3. Consultar el [expediente H06](../validation/D5-PFC126-03-E02-H06.json) para los requisitos completos y las fronteras pendientes.

Este mismo asistente preparó I149. La reconstrucción por un recorrido separado
del AST es revisión técnica documental; no acredita independencia de actor u
organización, autoridad de custodio o aceptación independiente de memoria.

## Alcance exacto de las relaciones de orden

| Relaciones reconstruidas | Cantidad | Interpretación |
| --- | ---: | --- |
| Construcción hacia guarda o validación posterior | 10 | body/out/text/chunk/group preceden al control seleccionado; no prueban que sea la primera guarda aplicable |
| Construcción hacia publicación en el draft | 1 | open_call crea row antes de stack.append; no acredita publicación externa ni admisión |
| Validación hacia guarda de tamaño o cobro | 2 | row_budget valida antes del tamaño codificado; DomainState valida record antes de charge |

Son trece relaciones léxicas, sin convertirlas en trece asignaciones nuevas antes
de la primera guarda. En W05/W08, el nombre histórico construction_prefix apunta
a una expresión de validación. Sus expresiones reales y su clasificación quedan
explícitas en I150; H06 ya las limita a orden léxico y no necesita reescritura.

Se contrastan además dos cadenas locales de evaluación: chunk.encode() como
argumento de add antes de su guarda, y canonical(node) como argumento de emit,
que llama a charge antes de actualizar el digest. Las definiciones léxicas
coinciden, bajo los bindings y precondiciones fijados. Eso no atesta el dispatch
del runtime, ejecución, tamaños, multiplicidad o vidas de objetos.

Se identifican seis validadores previos en canonical_hash, store_request,
drive_request, PageSink.append y Pages.flush. Los ejemplos de guardas posteriores
no borran esos controles ni permiten afirmar entrada arbitraria sin restricciones.
Un control de representación o tipo no suministra por sí solo el pico completo
de asignaciones solicitadas, capacidades, growth y workspace que coexisten.

## Procedencia, cobertura y retención

La reconstrucción desde Git concuerda con **163 pins**, doce proyecciones JSON,
79 fuentes, 28 anclas y siete registros de expresiones. Reproduce el censo y
los hashes de vectores por archivo/globales: 23802 Call, 835 List, 3096 Tuple,
493 Dict, 146 Set, 224/45/175 comprehensions, 389 GeneratorExp y 217 handlers.
Son sitios sintácticos; no invocaciones, bloques vivos ni cierre stdlib/nativo.

Los doce requisitos de inventario siguen sin cardinalidad, tamaño, pico vivo y
derivación de vida completos: 48 valores null. Las diez fronteras con H01–H05 y
H07–H11 no están resueltas. El requisito de cobertura original/nativa no equivale
a haberla demostrado; codecs, páginas, Reader, carriers y sus referentes precisan
propiedad explícita. H04 y H11 no pagan implícitamente temporales no clonados.

La operación de _atomic está léxicamente dentro de _state_lock y write_all fuera;
error=ex y raise error permanecen. No se deduce serialización de todas las vidas
del worker, liberación inmediata ni retención eterna. Siguen pendientes las vidas
solapadas de temporales, originales, errores y trabajo fuera de la fase protegida.

F≤52018, S≤1759, 53777 lotes y 53778 generaciones con inicial conservan su
alcance condicional P01/I124. No se transforman en número de operaciones no
clonadas ni se sustituyen tamaños con operand_bytes, depth, refs, frames,
payloads o longitudes de archivo. Sin descuentos por alias, interning, fusión
de witnesses o suposición de GC; el sobreconteo conservador requiere cobertura.

## Disposición y verificación

Los nueve campos siguen presentes: dos definiciones documentales y siete
insuficientes para aceptación. Se conserva la regla I132 sobre construcción
anterior a guardas y temporales no clonados. Los cuatro criterios E02 no cierran.
La cota completa, ajuste y slack siguen null; no se prueba sobrepresupuesto real,
memoria ilimitada, inviabilidad, capacidad o servicio. P01 independiente, P02
exacto y P03 continúan pendientes, sin sustituir demanda H06 con otros paquetes.

E01–E05 abiertas; E06 separado, pendiente, NOT_RUN y sin permiso de ejecución.
Once outputs siguen ausentes, sin iniciar otro paquete. I122 conserva
IMPLEMENTED_NOT_ADMITTED, sin SOURCE_CAPACITY_VERIFIED, propuesta o captura.
D5/H07 abiertos e IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL
(UI04.1); D1–D4 e I1–I20/A52 aceptados y brechas/obligaciones reales pendientes.
I86/I89/I92 INVALID_CAPTURE no se reanudan ni mezclan.

`python3 docs/validation/D5-I150-audit.py`: **PASS_STATIC_SOURCE_ONLY**, con
**228 archivos publicados** e inputs heredados preservados. Verifica Git/JSON/AST,
clasificación de relaciones y coherencia del dictamen negativo. No prueba heap,
ABI, liberación, capacidad, CPU/tiempo o independencia.

Los cinco archivos I150 forman una unidad de revisión: este documento, revisión,
reconstrucción, [auditor](../validation/D5-I150-audit.py) y
[sello](../validation/D5-I150-integrity.json). El diff supera 400 líneas por
evidencia generada y auditoría autocontenida; se informa el exceso sin comprimir
código ni borrar evidencia. Runtime harness: N/A, sin cambio de comportamiento
runtime. Rollback: retirar sólo los cinco archivos enumerados en work_unit.
Se audita antes del stage y después del commit, con push y comprobación del
remoto efectivo y árbol limpio.

Sin ejecutar/importar/compilar producto o componentes, consumir generadores,
introspeccionar, medir asignaciones o sondear runtime/plataforma. Fuentes,
candidata03, cuotas, presupuestos, reservas, capture_inputs y autoridad/destino
intactos. Sin recursos reservados, contactos externos, proveedores, credenciales,
consumo, activación, promoción, despliegue o D6. No se inspecciona ni limpia
dev/run_data/D4.
