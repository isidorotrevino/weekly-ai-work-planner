# I164 — P06 conforme como expediente; trabajo y WCET sin demostrar

Fecha: 2026-11-15, Europe/Madrid. Base:
`cd7c55435465ed86cc0b2ceccdd45d6af14e966c`.

La revisión de P06 no encuentra defectos documentales bloqueantes en la
preparación I163. Sus diez grupos y veinte vectores registran requisitos y
carencias de forma consistente con I132/PFC126-CANDIDATE-03/I122. **No acredita
trabajo completo, WCET ni cumplimiento de 900 segundos.** E03 permanece abierta;
PJC115-R2 e I122 mantienen la no admisión y D5 sigue abierto.

## Evidencia y alcance de la revisión

El [dictamen](../validation/D5-I164-P06-documentary-review.json) contiene quince
comprobaciones y separa conformidad documental de aceptación de recursos.
La [reconstrucción](../validation/D5-I164-P06-source-reconstruction.json) vuelve
a leer los blobs publicados, comprueba 224 pins, analiza sintaxis de 79 fuentes
y localiza veinte anclas de coste y cuatro marcadores mediante un índice AST.
Recompone explícitamente las combinaciones grupo/proceso/fase; contrasta además
los campos originales mediante el validador semántico I163 conservado en el
[auditor autocontenido](../validation/D5-I164-audit.py).

Es una reconstrucción metodológicamente separada realizada por el mismo
asistente que preparó I163. No es revisión de actor u organización independiente,
aceptación del revisor WCET previsto por I132 ni conformidad de custodio de
runtime/plataforma. Las anclas y el orden léxico no prueban duración, orden entre
procesos, calendario real ni cierre transitivo de todas las llamadas.

## Resultado por cobertura

| Cobertura | Dictamen |
| --- | --- |
| C01/C03, coordinador antes de tR | Requisitos y anclas consistentes; cotas sin demostrar |
| C02, startup del worker antes de READY/RELEASE | Incluye la obligación anterior a main; main no prueba el coste del arranque completo |
| C04/C05, worker y children a ambos lados de tR | Ventanas exigidas correctamente; partición real o sobreconteo completo sin justificar |
| C06, espera y observación del coordinador | tW ligado a retorno exacto True; demora de observación sin cota |
| C07/C08, cleanup y evidencia tras tW | Requisitos de coste presentes; originales/nativo/IO sin cierre |
| C09, finally de éxito hasta tF | Escrituras y closes finales incluidos; trabajo y progreso sin demostrar |
| C10, contribuciones transversales | Nativo, codecs, GC/destrucción, asignación y locks exigidos en los procesos/ventanas relevantes; cierre ausente |

Hay tres conjuntos de procesos requeridos, no una enumeración exacta de PIDs o
threads aceptada por plataforma. La reconstrucción obtiene veinte vectores:
C01/C02/C03 uno cada uno, C04/C05 dos cada uno, C06/C07/C08/C09 uno cada uno y
C10 nueve. Ninguno tiene trabajo completo, unidad, WCET, espera, scheduling o
derivación verificados: 120 valores seleccionados null. Las treinta cotas
trabajo/CPU/wall de los diez registros candidatos también siguen null. Estos
conteos describen el expediente; no cuantifican todo el trabajo pendiente.

Los ocho campos requeridos están presentes. Tres aportan vinculación documental
o transferencia parcial; cinco resultan insuficientes para aceptación. Los
cuatro criterios E03 conservan su disposición previa, con cero cierres.

## Marcadores que se conservan

t0 es la entrada a la invocación de launch; tR es el retorno normal del close
del canal RELEASE del coordinador tras JSON/newline; tW es el retorno exacto
True de su única llamada wait_worker(process); tF es el retorno normal de
launch después de finally, sujeto a elegibilidad de éxito independiente.
No se observan valores de reloj. Las ventanas candidatas siguen siendo
Tpre=tR−t0, Tworker=tW−tR y Tpost=tF−tW.

El worker puede recibir RELEASE y ejecutar imports, suite, observadores,
children o finalización antes de que el coordinador cierre el canal. C04 exige
cubrir ese trabajo en Tpre o justificar un sobreconteo completo. El orden léxico
de cada proceso no proporciona una barrera adicional ni una partición medida.

La salida física del worker puede preceder a tR o a wait; dispatch, reap,
observación y retorno siguen formando parte de la ventana hasta tW. True no
acredita éxito de captura: siguen pendientes comprobaciones de salida, inputs,
evidencia y finally. False, excepciones, timeout o cleanup posterior no sustituyen
el retorno calificado ni desplazan tW a una comprobación posterior.

packet.finish precede al finally y no es tF. La fuente conserva verify,
listing/sizes, codificación de context y creación/escritura/cierre de context y
launch hasta el retorno normal. La presencia de esas operaciones exige cubrir
sus costes y progreso; no demuestra que terminen dentro del presupuesto.

## Límites de la transferencia y evidencia que falta

I124 se conserva con sus precondiciones: 321 roots, F≤52018, S≤1759,
53777 lotes y 53778 generaciones con inicial. Sus 718 oportunidades de proceso
no enumeran procesos efectivos ni garantizan servicio. Kernel y colisiones
mantienen unidades abstractas; no se convierten en instrucciones, CPU o segundos.
No se deduce inviabilidad real de un upper laxo ni tasa garantizada de work/900.
Se conserva retain-all, sin sustituirlo por GC inmediato o 33 generaciones.

Falta una cota transitiva completa de originales, runtime/imports, nativo,
codecs, hashes/sorts, asignación y GC/destrucción, además de IO/children,
locks/scheduler/observación, retries/señales/interferencia y liveness. La ruta
trabajo/servicio compatible o WCET de plataforma exacta sigue sin seleccionar y
justificar. P02 y P03 no aportan identidad/servicio aceptados; P05 conserva su
dictamen negativo sobre heap. P07–P10 siguen sin producirse.

Los 60/750/60 segundos y reserva 30, y la partición candidata 600/90/60 de
Tworker, conservan sus valores. No son garantías de servicio/duración ni reservas
por grupo, proceso o thread; C04 no recibe otro presupuesto de CPU600. No se
resta solapamiento paralelo sin prueba ni se equipara suma de CPU a wall.
El watchdog 900 es límite de fallo; no prueba éxito o cleanup dentro de 900.

## Preservación y publicación

E01–E05 permanecen abiertas; E06 separado NOT_RUN y sin autorización de ejecución.
I122 conserva IMPLEMENTED_NOT_ADMITTED; sin SOURCE_CAPACITY_VERIFIED, admisión,
captura, rebind o autoridad/destino nuevos. D5/H07 de cierre abiertos e IR03
NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1; D1–D4 e
I1–I20/A52 intactos; brechas globales y reales pendientes. I86/I89/I92
INVALID_CAPTURE no se reanudan ni mezclan.

La unidad contiene este documento, dictamen, reconstrucción, auditor y
[sello](../validation/D5-I164-integrity.json). Preserva los bytes de 298 archivos
publicados y los inputs heredados. El diff supera 400 líneas por el auditor
autocontenido y la evidencia trazable; se documenta el exceso sin retirar pruebas.
Rollback limitado a los cinco archivos indicados en work_unit. Commit y push
autorizados por el usuario; su publicación no modifica el estado de admisión.

Verificación: `python3 docs/validation/D5-I164-audit.py`, resultado esperado
PASS_STATIC_SOURCE_ONLY, antes del stage y después del commit; verificación de
remoto y árbol limpio tras push. Runtime harness N/A: revisión documental sin
cambio runtime. Sólo se ejecutan herramientas documentales JSON/Git/AST.
Sin ejecutar, importar o compilar producto/componentes, tests, benchmarks,
schedule, introspección ni mediciones de runtime/plataforma. Sin cambiar fuentes,
cuotas, reservas, presupuestos o contrato. No se inspecciona ni limpia
dev/run_data/D4; sin proveedores, credenciales, consumo, activación, promoción,
despliegue o D6.
