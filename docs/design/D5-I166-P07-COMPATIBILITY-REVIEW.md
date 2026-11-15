# I166 — P07 conforme como expediente; compatibilidad sin demostrar

Fecha: 2026-11-15, Europe/Madrid. Base:
`7850738bd50ca58d827ecdc5102e17c68e2577d7`.

La revisión no encuentra defectos documentales bloqueantes en P07 preparado
por I165. Sus siete campos conservan los requisitos de I132 y la insuficiencia
de P02/P03/P06. **No acredita compatibilidad de trabajo/servicio, WCET ni
cumplimiento de 900 segundos.** E03/E04 y D5 siguen abiertos; I122 y PJC115-R2
mantienen la no admisión.

## Ruta de revisión y método

Leer primero el [dictamen](../validation/D5-I166-P07-documentary-review.json),
con diecisiete comprobaciones. La
[reconstrucción](../validation/D5-I166-P07-source-reconstruction.json) vuelve a
leer 232 entradas de Git y recompone la relación grupo/proceso/fase, las
categorías y el mapa de latencias. El
[auditor](../validation/D5-I166-audit.py) conserva además la validación semántica
de I165, sustituyendo únicamente los límites de archivos de publicación por
los de esta revisión. P07, sus entradas y sus decisiones conservan sus bytes.

El índice AST separado contrasta veinte anclas de coste y cuatro marcadores
en un corpus de 79 fuentes. Analiza sintaxis, sin importar, compilar o ejecutar
esas fuentes. No reconstruye un calendario real, mide clocks, verifica WCET o
demuestra cierre transitivo de todas las llamadas.

La reconstrucción es metodológicamente separada, realizada por el mismo
asistente que preparó I165. No satisface independencia de actor u organización,
aceptación del revisor de scheduling/IO/WCET previsto por I132 ni autoridad de
custodio de runtime/plataforma. Ambas aceptaciones continúan pendientes.

## Resultados de la revisión

| Objeto | Resultado |
| --- | --- |
| Plan, esquema y dependencias | Siete campos presentes; P02/P03/P06 correctamente vinculados sin aceptación de recursos |
| Correspondencia de trabajo | Veinte cruces reconstruidos por grupo/proceso/fase, sin pérdidas o duplicados |
| Runtime/plataforma/unidades | Correspondencia exacta y dominio de servicio sin acreditar |
| Conversión o WCET | Dos rutas condicionales sin seleccionar; trabajo, tasa, latencia y derivación sin demostrar |
| Atribución de latencias | Diez obligaciones requeridas; ninguna cota o composición verificada |
| Categorías por fase | Nueve registros con upper y derivación null; sin reserva extra |
| Hipótesis de servicio | Autoridad, validez, carga/interferencia, retries/señales y liveness pendientes |
| Vector de Tworker | 600/90/60 suma 750 como aritmética candidata; cobertura temporal sin probar |

Los veinte cruces contienen 200 valores null seleccionados: trabajo, unidad,
WCET, identidades de runtime/plataforma, dominio de proceso, unidad y tasa de
servicio, latencia y derivación. Es un conteo de campos del expediente, no una
medida de coste ni una lista exhaustiva de carencias. Los tres conjuntos de
procesos tampoco equivalen a una enumeración completa aceptada por plataforma.
P06 conserva sus treinta valores de grupo y 120 campos de vector sin demostrar.

## Conversión y latencias: alcance correcto del expediente

La expresión condicional L+W/r no se usa como teorema demostrado. Requiere una
curva de servicio inferior atestada y un argumento aplicable de trabajo
completo, llegadas, backlog inicial, readiness, concurrencia y ventanas. Una
curva por sí sola no convierte los conteos abstractos de clones en un bound de
campaña. W, r, L y esa derivación siguen sin evidencia aceptada.

El expediente distingue tasa por tiempo de CPU de tasa por wall. La primera
exige acotar servicio denegado, esperas y observación para concluir wall. La
segunda debe declarar qué latencias incluye. La composición por proceso y
ventana requiere prueba; no cabe descontar de nuevo latencia ya cubierta ni
confundir CPU concurrente agregada con elapsed del coordinador.

La ruta WCET también queda sin seleccionar. Requiere runtime/plataforma exactos,
originales/imports/nativo/codecs/GC/destrucción, memoria/cache/allocator y carga,
además de declarar qué delays cubre. MHz, cores, cuotas, watchdog y W/presupuesto
no sustituyen garantías. Las oportunidades lógicas I124 no son segundos.

El mapa de diez owners es una exigencia de cobertura, sin partición exclusiva
probada. Los términos mixtos deben separarse o cubrirse por sobreconteo aditivo
justificado. Las superposiciones entre requisitos generales y específicos no
dan descuentos o crédito adicional; C10 sigue siendo transversal. Todas las
latencias y su composición permanecen sin cota verificada.

## Ventanas y presupuestos conservados

C02 mantiene el arranque anterior a main. C04 exige cubrir el trabajo del
worker/children posterior a recibir RELEASE que pueda preceder a tR, el retorno
normal del close del coordinador. No se asigna automáticamente todo ese trabajo
a Tworker ni se infiere una barrera entre procesos del orden léxico.

tW sigue siendo el retorno exacto True de la única llamada wait_worker(process).
La salida física anterior a tR o a wait no elimina dispatch/reap/observación
hasta ese retorno. True no prueba éxito de captura: comprobaciones posteriores
independientes conservan tW; False, excepción o cleanup no lo sustituyen.

C07/C08/C09 mantienen cleanup, inputs, validación y finally hasta tF, el retorno
normal de launch con escrituras y closes finales. packet.finish no es tF. No se
declara que esas operaciones o el cleanup de fallo terminen dentro de 900.

La desigualdad requerida Tworker≤U_CPU+U_IO_child_wait+U_scheduler_observation≤750
conserva sus tres U y suma verificada null. Los objetivos 600/90/60 no son
servicio garantizado ni cotas ya demostradas. Tpre/Tpost necesitan cobertura
completa separada, con objetivos 60/60; C04 no recibe otro CPU600. Se conserva
60+750+60+30=900, reserva una vez, cero transferencias y cero reserva extra por
grupo, proceso, thread o categoría. El watchdog 900 sigue siendo límite de fallo.

## Disposición, preservación y publicación

Los siete campos continúan insuficientes para aceptación. Los ocho criterios
E03/E04 heredan su clasificación, con cero cierres. P02/P03/P06 no se aceptan
por existir; P05 conserva su dictamen negativo de heap. P08–P10 siguen sin
producirse. Se mantiene el bloqueo por evidencia externa sin declarar ausencia
global de fuentes o inviabilidad real.

E01–E05 abiertas; E06 separado NOT_RUN y sin autorización de ejecución. I122
conserva IMPLEMENTED_NOT_ADMITTED, sin SOURCE_CAPACITY_VERIFIED, propuesta,
captura, rebind o autoridad/destino nuevos. D5/H07 de cierre abiertos; IR03
NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1; D1–D4 e
I1–I20/A52 intactos; brechas globales y reales pendientes. I86/I89/I92
INVALID_CAPTURE no se reanudan ni mezclan.

`python3 docs/validation/D5-I166-audit.py`: resultado esperado
PASS_STATIC_SOURCE_ONLY. Comprueba los campos, evidencia y presupuesto,
preservando 308 archivos publicados e inputs heredados. Unidad de cinco
archivos: este documento, dictamen, reconstrucción, auditor y
[sello](../validation/D5-I166-integrity.json). Rollback limitado a los cinco
archivos enumerados en work_unit. El diff supera 400 líneas por la evidencia y
el auditor autocontenido; el exceso queda informado. Runtime harness N/A:
revisión documental sin cambio runtime. Auditoría antes del stage y tras commit,
push autorizado y comprobación de remoto/árbol limpio; publicar no admite.

Sólo herramientas documentales Git/JSON/AST. Sin ejecutar, importar o compilar
producto/componentes, tests, benchmarks, schedule, introspección o mediciones
de runtime/plataforma. Sin cambiar fuentes, cuotas, reservas, presupuestos,
contrato o inputs; sin inspeccionar ni limpiar dev/run_data/D4. Sin proveedores,
credenciales, consumo, activación, promoción, despliegue o D6.
