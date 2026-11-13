# I146 — H04 sigue sin cota completa ni ajuste a 6 GiB

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`abb4a05e140fb188a2a51a8976b99c8f8aedeeb2`.

**La revisión confirma el dictamen de insuficiencia de P04-H04.** No se encuentran
defectos bloqueantes en la representación del expediente negativo. No se acepta
una prueba completa del heap de clones/memo: upper, ajuste a 6 GiB y slack siguen
desconocidos. E02 permanece abierta y PFC126-CANDIDATE-03/I122/PJC115-R2 mantienen
la no admisión. H04 conserva sus bytes y el presupuesto de 6442450944 bytes.

## Ruta de revisión

1. Leer los nueve campos y la decisión en la [revisión I146](../validation/D5-I146-P04-H04-documentary-review.json).
2. Contrastar pins, fuentes y desglose aritmético en la [reconstrucción desde Git](../validation/D5-I146-P04-H04-source-reconstruction.json).
3. Consultar el [expediente H04](../validation/D5-PFC126-03-E02-H04.json) para los doce requisitos de cobertura y diez límites de propiedad.

Este mismo asistente preparó I145. La recomputación separada es revisión técnica
documental, sin atestar independencia de actor/organización, autoridad de custodio
o aceptación por un revisor independiente de memoria.

## Resultado del contraste

| Área | Resultado I146 |
| --- | --- |
| Plan/identidad | Ruta/schema, nueve campos y registro canónico I132/contrato03/I122 concordantes |
| Procedencia | Blob H04 publicado y 150 pins coinciden con Git de preparación (`f245a59…`) y bytes actuales |
| Evidencia vinculada | Trece proyecciones recompuestas por puntero, valor y hash canónico; no se promueven referencias negativas a prueba nueva |
| Fuentes | Ocho archivos, once anclas léxicas más FIELDS y trece sitios de llamada clone_metadata concordantes |
| Conteos | F≤52018, S≤1759; N≤53777 lotes y G≤53778 generaciones con inicial preservados, bajo las condiciones fuente heredadas |
| Inventario | Doce clases requeridas con 48 valores desconocidos y diez fronteras H01/H02/H03/H05–H11 sin resolver |
| Campos/E02 | Dos definiciones documentales y siete campos insuficientes; cuatro criterios E02 conservan clasificación sin cierres |

## Aritmética: el subtotal de clones no valora toda la inicial

El desglose ponderado recompuesto del modelo heredado es:

| Término condicional por lote | Bytes |
| --- | ---: |
| Headers de contenedores | 163763778560 |
| Ocurrencias hijas | 163420139520 |
| Memo entries | 81881889280 |
| Temporales id | 20427521408 |
| Opaque fijo | 1024 |
| Intentos de inserción opaque | 1022976 |
| Total B | 429494352768 |

Se verifica N*B = 53777*429494352768 = 23096917808804736 bytes condicionales.
El multiplicador es N=F+S, mientras que G=1+F+S incluye el grafo inicial.
Su almacenamiento completo permanece desconocido: no se inventa un memo/lote
clonado adicional ni se dice que el subtotal ya lo incorpora. Su propiedad debe
reconciliarse, incluida H03, sin omitirlo o cobrarlo dos veces por etiqueta.

La contabilidad estructural separada coincide: G*C=8600477034570 contenedores y
G*(C+A)=25765336923450 unidades contenedor/ocurrencia. Son mayorantes fuente,
no tamaños medidos de objetos. IO pendiente ≤32 y rechazos/partial forks están
dentro de las oportunidades F; las filas de rutas no se suman como una partición
disjunta ni añaden otros 32 u otro F.

El subtotal builtin sigue condicionado al modelo fuente/runtime heredado. No
se ha verificado de nuevo el upstream ni su correspondencia con el binario/ABI/
allocator objetivo. Excluye términos señalados por I124 y no es upper completo
H04/heap/RSS. Un mayorante holgado mayor que 6 GiB no es un lower real ni prueba
sobrepresupuesto efectivo o inviabilidad. Su aritmética correcta tampoco acredita fit.

## Memo, escapes y vidas pendientes

Los trece sitios de clonación se sitúan léxicamente en seis llamadas recursivas,
cinco sitios del fork y dos rutas del proxy, una de ellas dentro de observed.
Son sitios sintácticos, sin afirmar número ejecutado o máximo vivo. El fork
comparte memo/opaque, conserva draft._memo y las rutas proxy declaran memo fresco.
El fast-path draft opera sin añadir un nuevo fork. Las fuentes concuerdan con
las cotas heredadas; esta revisión no deriva otro F/S ni reduce su alcance.

_atomic puede publicar estado y retornar subestructuras; draft/writes/memo y
valores escapados requieren reachability/coexistencia. La ruta de error conserva
excepción y puede retener frames/partial draft. IO fuera del lock, drain, flush
y finish no prueban liberación de todos los lotes. Se mantiene el mayorante que
retiene todos, sin reemplazarlo por 33 generaciones o GC inmediato sin un teorema
compatible. No se ejecutan clones, callbacks, IO, componentes o escenarios.

Los 48 nulls del inventario son cardinalidad completa, tamaño, pico y vida de sus
doce requisitos, no reapertura de los conteos fuente cerrados ni un inventario de
toda carencia. Crecimiento/temporales, memo/id/opaque, inicial, snapshots, resultados
escapados, errores y nativo residual siguen necesitando cobertura exacta.
Las diez fronteras de propietario no autorizan descuentos por alias/interning,
fusión de witnesses u omisión de originales, hojas, frames, páginas o payload.
H11 no es reserva libre de H04; el sobreconteo conservador requiere cobertura.

Se preserva el ámbito P01/I124, incluidos prefijos aplicables, sin ampliarlo a
hooks/control original inesperados o fallos arbitrarios fuera de sus supuestos.
P01 independiente/P02 exacto siguen pendientes. Capacidad P03 y otros propietarios
no sustituyen la derivación de H04 ni sus carencias prueban por sí solas inviabilidad.
No se cambia código, presupuesto o cuotas para acomodar la prueba.

## Disposición y publicación

Los 14 controles respaldan la coherencia del dictamen negativo sin requerir
cambiar H04. Se confirma el rechazo I132: E01–E05 siguen abiertas y E06 separado,
pendiente, NOT_RUN y sin permiso. Otros 13 outputs siguen ausentes, sin iniciar paquetes.

Fuentes, candidata03, plan/paquetes anteriores, cuotas/presupuestos/reservas,
certificado IMPLEMENTED_NOT_ADMITTED, capture_inputs y autoridad/destino intactos.
Sin SOURCE_CAPACITY_VERIFIED o captura habilitada. D5/H07 abiertos e IR03 NOT_READY.
P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados.
Brechas/obligaciones reales pendientes; I86/I89/I92 INVALID_CAPTURE sin reanudar
ni mezclar. Sin proveedores, credenciales, consumo, reservas operativas,
activación, promoción, despliegue o D6. No se inspecciona ni limpia dev/run_data/D4.

[Auditor I146](../validation/D5-I146-audit.py) y [sello de integridad](../validation/D5-I146-integrity.json).
`python3 docs/validation/D5-I146-audit.py` comprueba blobs/JSON/AST, aritmética,
inventario, presupuesto y no admisión, conservando 208 archivos publicados e
inputs heredados. Resultado comprobado: PASS_STATIC_SOURCE_ONLY, H04 no
verificado, cero cierres, producto/componentes ejecutados cero y cuotas intactas.
No prueba identidad, heap, capacidad, CPU/tiempo de campaña o independencia.

Se publica una unidad documental de cinco archivos. El diff supera 400 líneas
orientativas por evidencia generada y verificación autocontenida; se informa el
exceso sin comprimir código o borrar evidencia. Runtime harness: N/A, revisión
sin cambios de frontera runtime; producto/componentes prohibidos, sin builds,
imports de objetivo, discovery, benchmarks o sondeos. Rollback: retirar sólo los
cinco archivos I146 enumerados en work_unit de la revisión. Se hace commit y push,
con auditoría antes del stage y después del commit y verificación remoto/árbol limpio.
