# I157 — H10 preparado, sin cota completa de Tee/StringIO y raw

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`076794c4fbaf9a42ea6d7b7fbab7b09e551d431e`.

**P04-H10 queda preparado como expediente de insuficiencia.** La representación
parcial de texto/UTF8 no prueba la memoria completa de Tee/StringIO, snapshots,
parseo raw y su coexistencia con finish. Upper, ajuste al presupuesto candidato
de **134217728 bytes (128 MiB)** y slack permanecen desconocidos. E02 sigue
abierta y PFC126-CANDIDATE-03/I122/PJC115-R2 sin admisión. No se aplican cuotas,
reservas o cambios de capture_inputs.

## Ruta de revisión

1. Leer los nueve campos y el inventario en [H10](../validation/D5-PFC126-03-E02-H10.json).
2. Contrastar source_evidence, output_source_relationships e inherited_representation_payload_reference.
3. Consultar la [preparación I157](../validation/D5-I157-P04-H10-preparation-review.json) para la disposición y el progreso del plan.

I132 y los paquetes anteriores conservan sus bytes. I157 registra la preparación
actual sin reescribir el estado histórico PLANNED_NOT_PRODUCED. Este asistente
no acredita aceptación del revisor independiente de memoria previsto en I132
ni autoridad de custodio de runtime.

## Submodelo de una pareja de representaciones

| Término histórico condicionado I125 | Bytes |
| --- | ---: |
| B = raw_bytes candidato, 12 MiB | 12582912 |
| Payload escalar de una representación Unicode, modelo 4B | 50331648 |
| Un payload UTF8 | 12582912 |
| Una pareja de representaciones, 5B | 62914560 |
| Presupuesto candidato H10 | 134217728 |
| Presupuesto menos 5B, aritmética solamente | 71303168 |

**Los 68 MiB de diferencia no son slack de heap verificado.** Si el payload UTF8
agregado aceptado está acotado por B, queda acotado su número de codepoints. El
factor histórico de cuatro bytes por codepoint sólo modela un payload escalar;
no atesta ABI, headers, capacidad o layout de StringIO. Una pareja de 60 MiB no
es el total de representaciones, buffers, snapshots o árboles raw vivos.

La precondición de output agregado no demuestra por sí sola serialización o
atomicidad del contador frente a escrituras concurrentes. Tampoco cubre todos
los errores: encode se evalúa antes del control de bytes, y la escritura al
stream subyacente precede a la del StringIO. Los prefijos rechazados o
parcialmente reenviados requieren contabilidad propia.

## Flujo fuente y vidas pendientes

| Sitio fuente | Requisito identificado |
| --- | --- |
| BoundedOutput.write | Guarda exact str, encode UTF8, RAW_BUDGET, target.write y actualización de count en ese orden |
| Tee | Base io.StringIO y stream retenido; self.stream.write precede a super().write; flush delega al stream |
| exercise | Restore/flush anteriores a getvalue().encode()→strict_json; raw pasa después a rec.finish(raw) |
| Finish/aggregate | Raw vuelve a usarse después de finish en scenario_metadata/aggregate_capture; falta la prueba completa de raíces coexistentes |
| _typed_finish | Construcción de out y encode para controlar sidecar; límites de payload no pagan todos los temporales |
| Parser/SideWriter | Decode/árboles raw y serialización/validación de sidecar necesitan fronteras explícitas con H07/H09 |

Se vinculan **196 pins**, doce proyecciones JSON, 79 fuentes y 21 anclas. Ocho
relaciones de orden y once registros de expresiones, con coordenadas y hashes
AST, documentan el flujo. No son ocho asignaciones sin guardas ni pruebas de
tamaños, copias, liberación o ejecución real.

StringIO requiere modelos del runtime exacto de capacidad/growth, storage
acumulado, representaciones internas y snapshots de getvalue. La fuente no
demuestra que getvalue siempre copie ni que siempre reutilice memoria. Ninguna
de esas suposiciones sustituye cardinalidades y vidas completas.

El snapshot y su conversión UTF8 llegan al parser mientras existen otras raíces
de Tee/callers. Raw pasa por finish y usos posteriores, pero el orden no da por
sí solo la suma de bloques vivos o el tiempo de liberación de cada buffer. El
retorno de un helper, restore, flush o un cambio de contador no demuestra cierre,
shrink, desaparición de todos los referentes ni retención eterna.

## Cobertura y fronteras

Doce requisitos cubren Tee/StringIO, texto original, encode anterior a guarda,
stream subyacente, growth, snapshots, input de parseo, árboles decodificados,
finish/raw, metadatos/flush, errores y concurrencia/nativo. Cada uno mantiene
null en cardinalidad, tamaño, pico vivo y vida completos: **48 valores
desconocidos**. Es cobertura requerida, sin inventario exhaustivo ya demostrado.

Las diez fronteras con H01–H09/H11 siguen abiertas. Baseline nativo, originales,
roots persistentes, clones/memo, carriers, proyección/digest, codecs/árboles,
Reader, páginas y overhead requieren asignación explícita. Que H07 incluya codecs
no elimina la obligación de mapear las asignaciones del raw de H10, ni viceversa.
No se suman automáticamente buffers del padre, hijos, kernel o RSS al heap
solicitado vivo del worker. El stream nativo/userspace necesita atribución.

H11 no es reserva libre, sin nuevas cuotas por thread ni descuentos por alias,
interning, fusión de witnesses o GC supuesto. Se admite sobreconteo conservador
explícito sólo con cobertura completa, sin convertir términos desconocidos en cero.
F≤52018, S≤1759, 53777 lotes y 53778 generaciones con inicial conservan el
contexto condicional P01/I124, sin dar capacidad de StringIO o árboles vivos.

P01 independiente, P02 exacto y P03 siguen pendientes. Faltan inventario completo
y modelos de StringIO, snapshots, buffers de stream/codec, raw/finish y vidas de
error/concurrencia. La carencia se refiere al material suministrado, sin afirmar
ausencia global o inviabilidad.

## Disposición y publicación

Los nueve campos están presentes: dos definiciones documentales y siete
insuficientes. Se aplica el rechazo I132 contra convertir 62914560 bytes de una
pareja Unicode/UTF8 en memoria total raw/StringIO. Sin upper, ajuste, slack,
sobrepresupuesto real o memoria ilimitada demostrados. Capacidad u otros
propietarios no sustituyen demanda H10. Quedan siete outputs sin producir;
I157 no inicia otro paquete.

E01–E05 abiertas; E06 separado, pendiente, NOT_RUN y sin permiso de ejecución.
I122 conserva IMPLEMENTED_NOT_ADMITTED; sin SOURCE_CAPACITY_VERIFIED, propuesta
o captura. D5/H07 de cierre abiertos e IR03 NOT_READY. P0 conserva
83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados y brechas/
obligaciones reales pendientes. I86/I89/I92 INVALID_CAPTURE sin reanudar ni mezclar.

`python3 docs/validation/D5-I157-audit.py`: **PASS_STATIC_SOURCE_ONLY**.
Contrasta Git/JSON/AST, aritmética parcial, presupuesto y no admisión, con
**263 archivos publicados** e inputs heredados preservados. No prueba heap,
ABI, vidas, capacidad, CPU/tiempo o independencia.

H10, preparación, este documento, [auditor](../validation/D5-I157-audit.py) y
[sello](../validation/D5-I157-integrity.json) forman una unidad documental de
cinco archivos. El diff supera 400 líneas por evidencia generada y auditoría
autocontenida; se informa el exceso sin comprimir código o retirar evidencia.
Runtime harness: N/A, sin cambio de comportamiento runtime. Rollback: retirar
sólo los cinco archivos enumerados en work_unit. Se audita antes del stage y
después del commit, con push y verificación de remoto efectivo y árbol limpio.

Sin producto/componentes importados, compilados o ejecutados, tests, benchmarks,
consumo de generadores, introspección, instrumentación o sondeos de StringIO/
streams/raw/IO/runtime/memoria. Fuentes, candidata03, cuotas, presupuestos,
reservas, capture_inputs y autoridad/destino intactos. Sin recursos reservados,
contactos externos, proveedores, credenciales, consumo, activación, promoción,
despliegue o D6. No se inspecciona ni limpia dev/run_data/D4.
