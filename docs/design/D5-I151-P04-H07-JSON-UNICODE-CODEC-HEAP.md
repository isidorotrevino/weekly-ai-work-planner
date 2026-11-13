# I151 — H07 preparado, sin cota completa de codecs y árboles

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`187871af4e964711f9226952407cdb7414c838b6`.

**P04-H07 queda preparado como expediente de insuficiencia.** Los sitios JSON/
Unicode, fragmentos y árboles decodificados están vinculados a fuentes fijadas,
sin una cota completa de heap solicitado vivo. Upper, ajuste al presupuesto
candidato de **268435456 bytes (256 MiB)** y slack permanecen desconocidos.
E02 sigue abierta y PFC126-CANDIDATE-03/I122/PJC115-R2 sin admisión. No se aplica
el presupuesto como cuota ni se trasladan reservas.

## Ruta de revisión

1. Leer los nueve campos y el inventario en [H07](../validation/D5-PFC126-03-E02-H07.json).
2. Contrastar source_evidence y codec_call_spelling_evidence con los blobs de Git.
3. Consultar la [preparación I151](../validation/D5-I151-P04-H07-preparation-review.json) para la disposición y el progreso del plan.

I132 conserva su registro histórico PLANNED_NOT_PRODUCED. I151 registra la
producción documental actual sin reescribir el plan o paquetes anteriores.
Este asistente prepara el expediente; no acredita aceptación del revisor
independiente de memoria previsto en I132 ni autoridad de custodio de runtime.

## Evidencia y límites

| Sitio | Lo que identifica la fuente |
| --- | --- |
| encode / canonical | dumps produce texto que se pasa a encode UTF8/ASCII; faltan tamaños, buffers y vidas del runtime seleccionado |
| strict_json | Guarda inicial de file_bytes, escaneo decode UTF8 y profundidad, después loads y check(out); STRING_BUDGET comprueba el árbol ya parseado |
| strict_json.pairs / reject | Construcción del dict del hook y rechazo de duplicados/no finitos; el almacenamiento de argumentos, árboles parciales y errores necesita el modelo exacto del parser |
| digest / Projector | iterencode, canonical y conversiones de fragmentos; distinguir H06 de storage de codec y Unicode H07 |
| worker.exercise | getvalue().encode() se pasa a strict_json y raw llega a finish; carriers de salida y árbol decodificado requieren fronteras H10/H07 |
| SideWriter.write / read_sidecar | encode(value), control de longitud y parseo del body; atribuir cada llamada al worker o a otro proceso antes de sumar demanda |
| schema / canonical_metadata | loads(dumps(base)) y codificaciones para verificar forma canónica; no se deduce reutilización de buffers |
| _typed_finish / Pages.flush | Construcción y comprobación de salida/páginas; H09/H10 no pagan implícitamente todo codec y scratch |

Ocho relaciones de orden y ocho registros de expresiones, con líneas y hashes
AST, permiten revisar estas afirmaciones locales. La primera relación conserva
una guarda **anterior** a decode; no son ocho asignaciones sin controles previos.
El escaneo de profundidad y los validadores anteriores siguen presentes. Que un
string se rechace después de loads no implica entrada arbitraria sin límite:
implica que la prueba completa debe cubrir su construcción antes del rechazo.

Se fijan **171 pins**, doce proyecciones JSON, 79 fuentes y 22 anclas. El índice
de nombres de llamada cuenta 106 json.dumps, 154 json.loads, 48 atributos encode,
24 decode y uno iterencode; no encuentra json.dump/load bajo esas grafías.
Las grafías no resuelven aliases, dispatch o codec real ni prueban ausencia en
otros helpers, stdlib o nativo. Tampoco cuentan invocaciones, bloques o bytes.

## Cobertura y vidas pendientes

Doce clases de requisitos cubren estado y fragmentos de encoder, Unicode, bytes y
conversiones, decode de escaneo, scanner/parser, contenedores decodificados,
escalares/keys, hooks y rechazo, raw, sidecar, round trips/originales y retención
fallida o concurrente. Cada clase mantiene null en cardinalidad, tamaño, pico y
vida completos: **48 valores desconocidos**. Es cobertura requerida, sin afirmar
un inventario exhaustivo ya probado.

No se aplica un factor fijo a texto o UTF8 para sustituir headers, capacidades,
growth, buffers, objetos de árbol y workspace nativo. No se selecciona por
suposición la ruta Python o el acelerador JSON del runtime. El body serializado
y el número de codepoints no suministran por sí solos la suma de asignaciones
solicitadas vivas de H07.

El decode usado por el bucle de escaneo y el parseo posterior son sitios
distintos. La fuente no demuestra reutilización del texto ni que todo el texto
de escaneo permanezca durante todo el árbol completo. Sus vidas, errores y
coexistencia necesitan prueba; puede emplearse sobreconteo conservador explícito
con cobertura completa. No se afirma duplicación simultánea obligatoria.

Se heredan F≤52018, S≤1759, 53777 lotes y 53778 generaciones con inicial bajo
P01/I124. No son una cota de operaciones codec o árboles vivos. De igual modo,
file_bytes, string, depth, operand_bytes, refs, frames y límites de salida no se
rebautizan como heap completo. Retorno, cleanup o nombre «temporal» no prueban
liberación inmediata; tampoco se concluye retención eterna.

Para cerrar la demanda falta derivar, en cada estado aplicable del worker, el
tamaño solicitado de todos los bloques H07 vivos, incluidos parciales de rechazo,
y sus multiplicidades/vidas entre originales, observador, raw y sidecar.
P02 exacto y los modelos de representación, parser/encoder nativo y asignación
siguen pendientes. Esta carencia se refiere al material suministrado, sin
afirmación de ausencia global o inviabilidad.

## Fronteras y disposición

Las diez fronteras con H01–H06 y H08–H11 permanecen abiertas: baseline nativo,
originales, roots persistentes, clones, carriers de marcos, proyección/digest,
Reader, páginas, salida y overhead requieren asignación explícita de bloques y
vidas. Se hereda la separación worker/otros procesos de P01. La existencia de
un helper compartido no permite sumar automáticamente heap del padre al worker.
H11 no es reserva libre; sin descuentos por alias, interning o fusión de witnesses.

Los nueve campos están presentes: dos definiciones documentales y siete
insuficientes para aceptación. Se aplica el rechazo I132 contra convertir cotas
de texto/UTF8/serialización en heap completo del codec. No hay upper completo,
ajuste, slack, sobrepresupuesto real o memoria ilimitada demostrados. P01
independiente, P02 exacto y P03 siguen pendientes, sin sustituir demanda H07 con
capacidad o con otro propietario. Quedan diez outputs del plan sin producir;
I151 no inicia otro paquete.

E01–E05 abiertas; E06 separado, pendiente, NOT_RUN y sin autorización de
ejecución. I122 conserva IMPLEMENTED_NOT_ADMITTED; sin SOURCE_CAPACITY_VERIFIED,
propuesta o captura. D5/H07 de cierre abiertos e IR03 NOT_READY. P0 conserva
83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados y brechas/
obligaciones reales pendientes. I86/I89/I92 INVALID_CAPTURE sin reanudar ni mezclar.

## Verificación y publicación

`python3 docs/validation/D5-I151-audit.py`: **PASS_STATIC_SOURCE_ONLY**.
Contrasta Git/JSON/AST, inventario, presupuesto y no admisión; conserva **233
archivos publicados** e inputs heredados. No prueba heap, runtime, capacidad,
CPU/tiempo o independencia. Sin producto/componentes importados, compilados o
ejecutados, tests, benchmarks, introspección, instrumentación o sondeos.

H07, preparación, este documento, [auditor](../validation/D5-I151-audit.py) y
[sello](../validation/D5-I151-integrity.json) forman una unidad documental de
cinco archivos. El diff supera 400 líneas por evidencia generada y auditoría
autocontenida; se informa el exceso sin comprimir código o borrar evidencia.
Runtime harness: N/A, sin cambio de comportamiento runtime. Rollback: retirar
sólo los cinco archivos enumerados en work_unit. Se audita antes del stage y
después del commit, con push y verificación de remoto efectivo y árbol limpio.

Fuentes, candidata03, cuotas, presupuestos, reservas, capture_inputs y autoridad/
destino intactos. Sin recursos reservados, contactos externos, proveedores,
credenciales, consumo, activación, promoción, despliegue o D6. No se inspecciona
ni limpia dev/run_data/D4.
