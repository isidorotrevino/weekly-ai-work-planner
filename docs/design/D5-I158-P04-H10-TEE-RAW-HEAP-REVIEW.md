# I158 — H10 revisado, sin cota completa ni ajuste demostrado

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`c025f9e1aecd98066acae503e6aa6b6d545c1ad3`.

**La revisión confirma el dictamen de insuficiencia de P04-H10.** El expediente
negativo es documentalmente coherente y no requiere cambiar H10. La prueba
completa de Tee/StringIO, texto de salida y raw sigue pendiente: upper, ajuste
a **134217728 bytes (128 MiB)** y slack desconocidos. E02 permanece abierta;
PFC126-CANDIDATE-03/I122/PJC115-R2 mantienen la no admisión. H10 y el presupuesto
candidato conservan sus bytes, sin aplicar cuotas ni reservas.

## Ruta de revisión

1. Leer los quince controles y nueve disposiciones de campo en la [revisión I158](../validation/D5-I158-P04-H10-documentary-review.json).
2. Contrastar blobs, vectores y relaciones en la [reconstrucción I158](../validation/D5-I158-P04-H10-source-reconstruction.json).
3. Consultar [H10](../validation/D5-PFC126-03-E02-H10.json) para clases requeridas, dependencias y fronteras pendientes.

Este mismo asistente preparó I157. El recorrido separado del AST aporta
contraste documental, sin acreditar independencia de actor/organización,
autoridad de custodio o aceptación independiente de memoria.

## Fuente y límites de las relaciones

La reconstrucción concuerda con **196 pins**, doce proyecciones JSON, 79 fuentes,
21 anclas y los vectores sintácticos por archivo/globales. Once registros de
expresiones y ocho relaciones léxicas permiten comprobar lo siguiente:

| Sitio | Orden conservado y límite |
| --- | --- |
| BoundedOutput.write | Tipo str antes de encode; RAW_BUDGET después de encode y antes de target.write; count se actualiza después del reenvío |
| Tee.write | self.stream.write precede a super().write sobre la base io.StringIO declarada |
| exercise | Restore/flush, getvalue().encode()→strict_json, finish(raw) y uso posterior condicionado en aggregate |
| Finish | Puente a _typed_finish(raw), construcción de out y control posterior de tamaño serializado |

No son ocho asignaciones sin guardas ni pruebas de bytes, copias o liberación.
El orden check/forward/count no establece atomicidad global o serialización de
todos los escritores. Los errores anteriores a count, incluido encode antes de
la guarda y reenvío parcial, necesitan cobertura propia. No se afirma que el
submodelo de output agregado sea un teorema nuevo sobre toda concurrencia.

## Una pareja de representaciones no es memoria total

| Aritmética condicionada I125 | Bytes |
| --- | ---: |
| B = raw_bytes candidato | 12582912 |
| Payload escalar de una representación Unicode, modelo 4B | 50331648 |
| Un payload UTF8 | 12582912 |
| Una pareja, 5B | 62914560 |
| 134217728−5B, aritmética solamente | 71303168 |

**68 MiB de diferencia no son slack verificado.** El modelo presupone payload
UTF8 agregado aceptado acotado por B; no deriva esa garantía para todo escritor
concurrente. Su factor histórico de cuatro bytes por codepoint no atesta ABI,
layout o capacidad de StringIO, headers o buffers nativos. Una pareja de 60 MiB
no es total raw/StringIO ni máximo de todas las representaciones simultáneas.

Se conserva la ausencia de una prueba de que getvalue siempre copie o siempre
reutilice storage. Faltan capacidad/growth, snapshots y sus raíces, temporales de
encode, buffers de stream, parser/árboles raw y su coexistencia con finish.
El raw pasa como argumento a finish y, cuando aplica, a aggregate posterior;
el orden fuente no da por sí solo la suma de bloques vivos o sus vidas completas.

Restore, flush y retorno no prueban close, shrink, desaparición de todos los
referentes o colección inmediata. Tampoco se concluye retención eterna. La base
de Tee y los métodos de forwarding están fijados en fuente, sin ejecución ni
atribución exhaustiva del dispatch/native del runtime seleccionado.

## Cobertura y disposición

Doce requisitos mantienen **48 valores null** de cardinalidad, tamaño, pico y
vida completos. Las diez fronteras H01–H09/H11 siguen abiertas: baseline nativo,
originales, roots, clones/memo, carriers, proyección/digest, codecs/árboles,
Reader, páginas y overhead precisan asignación explícita. H07 no paga
automáticamente todo raw de H10, ni H10 todo codec de H07. Los buffers del stream
userspace/nativo requieren atribución al worker; sin suma automática de RSS,
kernel o heaps de padre/hijos.

H11 no es reserva libre, sin nuevas cuotas por thread o créditos por alias,
interning, fusión de witnesses o GC supuesto. Un sobreconteo conservador
explícito requiere cobertura completa, sin hacer cero un término desconocido.
F≤52018, S≤1759, 53777 lotes y 53778 generaciones con inicial conservan su
contexto condicional P01/I124; no dan capacidad de StringIO o árboles vivos.

Los nueve campos conservan dos definiciones documentales y siete disposiciones
insuficientes. Los cuatro criterios E02 no cierran. Se aplica el rechazo I132
contra convertir 62914560 bytes de una pareja Unicode/UTF8 en memoria total.
Upper, ajuste y slack null; no se prueba sobrepresupuesto real, memoria ilimitada,
capacidad o servicio. P01 independiente, P02 exacto y P03 siguen pendientes,
sin sustituir demanda H10 o afirmar ausencia global de evidencia. Siete outputs
siguen ausentes, sin iniciar otro paquete.

E01–E05 abiertas; E06 separado, pendiente, NOT_RUN y sin permiso de ejecución.
I122 conserva IMPLEMENTED_NOT_ADMITTED; sin SOURCE_CAPACITY_VERIFIED, propuesta
o captura. D5/H07 de cierre abiertos e IR03 NOT_READY. P0 conserva
83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados y brechas/
obligaciones reales pendientes. I86/I89/I92 INVALID_CAPTURE sin reanudar ni mezclar.

## Verificación y publicación

`python3 docs/validation/D5-I158-audit.py`: **PASS_STATIC_SOURCE_ONLY**.
Verifica Git/JSON/AST y coherencia del dictamen negativo, con **268 archivos
publicados** e inputs heredados preservados. No prueba heap, ABI, vidas,
capacidad, CPU/tiempo o independencia.

Cinco archivos I158 forman una unidad: este documento, revisión, reconstrucción,
[auditor](../validation/D5-I158-audit.py) y [sello](../validation/D5-I158-integrity.json).
El diff supera 400 líneas por evidencia generada y auditoría autocontenida;
se informa el exceso sin comprimir código o retirar evidencia. Runtime harness:
N/A, sin cambio de comportamiento runtime. Rollback: retirar sólo los cinco
archivos enumerados en work_unit. Se audita antes del stage y después del commit,
con push y verificación de remoto efectivo y árbol limpio.

Sin producto/componentes importados, compilados o ejecutados, tests, benchmarks,
consumo de generadores, introspección, instrumentación o sondeos de StringIO/
streams/raw/IO/runtime/memoria. Fuentes, candidata03, cuotas, presupuestos,
reservas, capture_inputs y autoridad/destino intactos. Sin recursos reservados,
contactos externos, proveedores, credenciales, consumo, activación, promoción,
despliegue o D6. No se inspecciona ni limpia dev/run_data/D4.
