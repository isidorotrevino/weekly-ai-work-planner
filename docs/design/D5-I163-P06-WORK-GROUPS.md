# I163 — P06 preparado, trabajo completo y WCET sin demostrar

Fecha: 2026-11-15, Europe/Madrid. Base:
`e3efaa2a620e192150b6fb674885e38ccc2785d0`.

**P06 prepara C01–C10 sin admitir trabajo/tiempo.** El inventario de obligaciones,
los vectores proceso/fase y las anclas están vinculados a las fuentes. Faltan
unidades compatibles, cotas completas de trabajo o WCET justificado y cobertura
de esperas/scheduling. E03 y D5 siguen abiertos; PFC126-CANDIDATE-03/I122/PJC115-R2
sin admisión. Se mantienen las restricciones previas: sin ejecución de producto
o componentes ni cambios de cuotas, fuentes, reservas o presupuestos.

## Ruta de revisión

1. Leer los ocho campos en [P06](../validation/D5-PFC126-03-E03-WORK-GROUPS.json).
2. Contrastar los diez grupos, veinte vectores y la transferencia condicionada I124.
3. Revisar las definiciones de marcadores y sus anclas, antes de cualquier conversión a segundos.
4. Consultar la [preparación I163](../validation/D5-I163-P06-preparation-review.json).

I132 conserva sus bytes y su estado histórico; I163 registra la preparación
actual. Este asistente no acredita aceptación del revisor independiente de
trabajo/WCET ni autoridad de custodio de runtime o plataforma.

## Grupos y ventanas del coordinador

| Grupo | Cobertura requerida | Ventana/procesos |
| --- | --- | --- |
| C01 | Registro, autoridad y descubrimiento inicial | Tpre, coordinador |
| C02 | Startup/imports/nativo, registro y canales antes de READY/RELEASE | Tpre, worker y todos sus threads |
| C03 | Popen, READY, RELEASE/newline y close | Tpre, coordinador |
| C04 | Trabajo post-recepción que pueda preceder a tR, incluidos suite, children y finish | Tpre, worker/children originales |
| C05 | Trabajo que continúa desde tR hasta salida del worker | Tworker, worker/children originales |
| C06 | Dispatch, observación/reap y retorno True de wait | Tworker, coordinador |
| C07 | Cleanup normal y comprobaciones frescas after/finish | Tpost, coordinador |
| C08 | Read/parse/hash/pages/aggregate/finish de evidencia | Tpost, coordinador |
| C09 | Finally, fd closes, listing/sizes/context y escrituras finales | Tpost, coordinador |
| C10 | Original/nativo/codecs/GC/destrucción/asignación/locks | Cada proceso relevante, cada ventana aplicable |

Tres conjuntos de proceso nombran coordinador, worker con todos sus threads y
children originales bajo el scope P01. No son una enumeración de PIDs ni una
correspondencia de plataforma probada. C10 es transversal dentro de las fases;
no un tail gratis, noncopy cero o presupuesto adicional. Los children conservan
su scope original, sin instrumentación nueva o reserva por proceso/thread.

Los veinte vectores conservan null en trabajo completo, unidad compatible, WCET,
espera, scheduling/observación y derivación: 120 campos seleccionados. Las treinta
cotas trabajo/CPU/wall heredadas de los diez grupos también siguen null. Son
registros de carencias, sin pretender enumerar todo el coste transitorio/nativo.
Una suma de CPU por procesos no equivale a duración wall ni servicio disponible.

## Marcadores y solapamiento

Se conservan t0≤tR≤tW≤tF y Tpre=tR−t0, Tworker=tW−tR, Tpost=tF−tW.
Los cuatro son definiciones normativas; no hay timestamps observados.

| Marcador | Definición conservada |
| --- | --- |
| t0 | Entrada a launch del coordinador antes de su primera sentencia |
| tR | Retorno normal de os.close(release_write) del coordinador tras RELEASE/newline |
| tW | La llamada única wait_worker(process) retorna exactamente True |
| tF | Retorno normal de launch tras finally y escrituras/closes, con elegibilidad independiente |

Recibir RELEASE en el worker no es tR. Imports/suite/observers/children o
finalización post-recepción pueden ocurrir antes del close del coordinador.
P06 exige cubrirlos en Tpre o un sobreconteo conservador justificado; no los coloca
automáticamente todos en Tworker. C02 también exige startup anterior a worker.main.
Las etiquetas de funciones no determinan ventanas reales.

La salida física del worker no es tW. Dispatch/observación/reap/retorno siguen
dentro de Tworker, incluso si ya salió antes de tR o de llamar a wait. True no
es éxito de captura: las comprobaciones posteriores deben pasar sin mover tW.
False, excepción, timeout o cleanup tardío no sustituyen el marcador calificado.

packet.finish no es tF. C09 incluye el finally de éxito, verify/listing/sizes,
context/launch create/write/close hasta el retorno normal. No se resta overlap
paralelo sin prueba ni se omiten contribuciones del coordinador en Tworker.
La cota de 900 segundos del watchdog es límite de fallo, no garantía de éxito;
el cleanup de fallo tampoco queda automáticamente garantizado dentro de 900.

## Conteos parciales y evidencia faltante

I124 conserva su scope fijo de 321 roots/12 grupos y sus precondiciones. Se
transfieren F≤52018, S≤1759, 53777 lotes y 53778 generaciones con inicial,
además de oportunidades de eventos/bindings/subtests/procesos y el modelo abstracto
de kernel/colisiones. Sus unidades siguen siendo oportunidades lógicas, no
instrucciones o segundos. Las 718 oportunidades de proceso no son PIDs o servicio.

No se reemplaza retain-all por 33 generaciones o GC inmediato. Un upper abstracto
muy laxo no demuestra duración, éxito o inviabilidad; work/900 no es una tasa de
servicio medida o garantizada. El conteo de clones no incluye por sí solo coste
completo de originales, imports, proyección, JSON/Unicode, hashes/sorts, nativo,
GC/destrucción, locks, IO, children, validación de evidencia o finally.

La ruta de prueba queda sin seleccionar: trabajo completo con servicio compatible
atestado, o WCET de plataforma exacta justificado. P02/P03 siguen sin proporcionar
esas unidades/servicios. Los 600/90/60 segundos candidatos CPU/IO-child/scheduler
de Tworker no son garantías ni se multiplican por proceso, grupo o ventana.
Tpre/C04 no recibe por defecto otro presupuesto de 600 segundos. No se asigna
reserva extra por categoría ni se convierten bytes de Input Reader en CPU/IO total.

Quedan pendientes políticas admisibles de retries/señales/interferencia/load,
liveness y cotas de delays IO/children/locks/scheduling/observación. Se registran
como requisitos y valores desconocidos, sin introducir nuevos controles operativos,
suposiciones de coste cero o cambios de watchdog/timer.

## Disposición y publicación

Ocho campos presentes: tres vinculaciones/requisitos/transferencias parciales y
cinco insuficientes para aceptación. Las anclas son evidencia de fuente, no cierre
de trabajo transitivo o WCET. Los criterios E03 conservan clasificación sin cierres.
P01 independiente, P02 exacto y P03 no se sustituyen con este inventario. P05
mantiene su rechazo de memoria; no se prepara compatibilidad P07 ni cotas P08.
Quedan P07–P10 sin producir.

E01–E05 abiertas; E06 separado NOT_RUN y sin permiso de ejecución. I122 conserva
IMPLEMENTED_NOT_ADMITTED; sin SOURCE_CAPACITY_VERIFIED, propuesta o captura.
D5/H07 de cierre abiertos, IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/
1 PARTIAL UI04.1; D1–D4 e I1–I20/A52 intactos y brechas reales pendientes.
I86/I89/I92 INVALID_CAPTURE sin reanudar ni mezclar.

`python3 docs/validation/D5-I163-audit.py`: **PASS_STATIC_SOURCE_ONLY**.
Verifica Git/JSON/AST, 220 pins, 79 fuentes, veinte anclas seleccionadas, veinte
anclas de coste adoptadas y cuatro definiciones de marcador, preservando 293
archivos publicados e inputs heredados. No ejecuta el schedule, reloj, producto
o componentes ni mide CPU, IO, wall o WCET.

Unidad de cinco archivos: P06, preparación, este documento,
[auditor](../validation/D5-I163-audit.py) y [sello](../validation/D5-I163-integrity.json).
El diff supera 400 líneas por evidencia generada y auditor autocontenido; se
informa el exceso sin comprimir código o retirar evidencia. Runtime harness N/A:
no cambio runtime. Rollback: sólo los cinco archivos enumerados en work_unit.
Auditoría antes del stage/después del commit y push con remoto/árbol limpio.

Sin imports/compilación/ejecución de producto/componentes, tests, benchmarks,
introspección o sondeos de runtime/plataforma. Fuentes, cuotas, reservas, contrato,
presupuestos, capture_inputs y autoridad/destino intactos. Sin proveedores,
credenciales, consumo, activación, promoción, despliegue o D6. No se inspecciona
ni limpia dev/run_data/D4.
