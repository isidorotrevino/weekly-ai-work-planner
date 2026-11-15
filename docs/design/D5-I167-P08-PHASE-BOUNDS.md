# I167 — P08 preparado; cotas por fases y éxito en 900 sin demostrar

Fecha: 2026-11-15, Europe/Madrid. Base:
`b7ec299a4ae9be0d7b18fd6b1418e6bc8d5593fa`.

P08 prepara el argumento condicionado de fases para PFC126-CANDIDATE-03/I122.
**Los siete campos están presentes y siguen siendo insuficientes para
aceptación.** Las cotas verificadas de Tpre, Tworker y Tpost permanecen null.
La identidad algebraica y la contabilidad candidata son consistentes; faltan
las premisas de heap, runtime, reloj, trabajo, servicio y progreso. E05 y D5
siguen abiertos; I122 y PJC115-R2 mantienen la no admisión.

## Ruta de revisión

1. Leer los siete campos de [P08](../validation/D5-PFC126-03-E05-PHASE-BOUNDS.json).
2. Contrastar las definiciones de marcadores y la elegibilidad independiente de éxito.
3. Revisar las tres fases, sus requisitos P06/P07 y las siete premisas no satisfechas.
4. Consultar la [preparación I167](../validation/D5-I167-P08-preparation-review.json)
   y el [sello](../validation/D5-I167-integrity.json).

Las seis dependencias P01/P02/P03/P05/P06/P07 conservan sus bytes y disposiciones.
Estar preparadas o revisadas documentalmente no les otorga aceptación de
recursos. I132 mantiene su estado histórico; este expediente registra la
preparación actual. No se produce P09 ni P10.

## Marcadores y éxito calificado

| Marcador | Evento del coordinador conservado |
| --- | --- |
| t0 | Entrada a la invocación de launch, antes de su primera sentencia |
| tR | Retorno normal de close del canal RELEASE tras JSON completo y newline |
| tW | Retorno exacto True de la única llamada wait_worker(process) |
| tF | Retorno normal de launch tras finally y escrituras/closes finales, con elegibilidad de éxito independiente |

Se vinculan las cuatro definiciones a AST y SHA de fuente. El reloj monotónico
común, sus unidades/dominio, la ocurrencia de los eventos y sus valores no están
atestados. No se recogen timestamps ni se instrumenta ningún timer.

El retorno True de wait no prueba éxito de captura: requiere salida normal cero
y comprobaciones independientes de autoridad, inputs, packet, páginas, resultado
funcional, captura y finally. Las comprobaciones posteriores nunca desplazan tW.
False, excepción, timeout o reap posterior no sustituyen el retorno calificado.
Se mantienen los controles actuales de fuente, sin instalar una nueva puerta
de éxito. Tampoco se deduce existencia o progreso de una ejecución exitosa de
una implicación condicional que pueda resultar vacua.

## Partición y argumento condicionado

Las definiciones Tpre=tR−t0, Tworker=tW−tR y Tpost=tF−tW dan, por cancelación
algebraica, Tpre+Tworker+Tpost=tF−t0. El auditor suma sus vectores de coeficientes
y comprueba esa identidad. La no negatividad requiere t0≤tR≤tW≤tF en el dominio
monotónico aceptado. La identidad no demuestra el orden real ni la cobertura
completa del trabajo y latencias de todos los procesos.

| Fase | Objetivo candidato | Cota verificada | Cobertura pendiente |
| --- | --- | --- | --- |
| Tpre | 60 s | null | Coordinador y worker, startup anterior a main y trabajo post-recepción anterior a tR |
| Tworker | 750 s | null | Trabajo completo, IO/children, locks/scheduler y observación hasta retorno exacto True |
| Tpost | 60 s | null | Cleanup, inputs, evidencia y success-finally hasta el retorno normal tF |

Las fases vinculan los veinte requisitos de vector P06 y los veinte cruces P07.
Son exigencias de cobertura, sin asignación temporal o sobreconteo completo ya
probados. Recibir RELEASE en el worker no es tR; imports, suite, children o
finish pueden preceder al close del coordinador. La salida física del worker
no es tW, incluso si precede a tR o a wait. Dispatch/reap/observación/retorno deben
quedar cubiertos. packet.finish no es tF: quedan verify, listing/sizes,
codificación, creación/escritura/cierre de context y launch y retorno normal.

El teorema preparado exige siete premisas: identidad exacta y reloj; heap y
capacidad completos; trabajo/servicio o WCET compatibles; latencias e hipótesis
de progreso; marcadores y éxito calificados; partición completa no negativa; y
las tres cotas verificadas dentro de 60/750/60. **Ninguna se registra satisfecha.**
Sólo bajo esas premisas se concluye tF−t0≤870≤900. No hay upper verificado de la
suma de fases o del extremo a extremo. P02/P03 no acreditan runtime/plataforma;
P05 mantiene su dictamen negativo de heap; P06/P07 no cierran trabajo y servicio.

## Contabilidad y fallos

La aritmética candidata es 60+750+60=870 y 870+30=900. La reserva no asignada de
30 se cuenta una vez; todas las asignaciones de fase y categoría siguen en
cero. No es holgura autorizada para rebasar fases ni capacidad de servicio.
La partición anidada 600CPU/90IO-child/60scheduler conserva 750, sin prueba de
cobertura y sin otro CPU600 para C04/Tpre. No hay crédito extra por fase, grupo,
proceso, thread o categoría, conversión byte/segundo ni préstamo de H11.

El watchdog existente de 900 corresponde a process.wait después de RELEASE;
no es deadline extremo a extremo ni garantía de éxito o cleanup. Se excluyen
de la conclusión de éxito: wait False/excepción, salida no cero/failure envelope,
rechazo de autoridad/inputs/packet/páginas/funcional/captura y finalización
excepcional o inválida. No se fuerza un marcador ausente o un tiempo desconocido
a cero, ni se usa un timeout/rechazo como evidencia temporal de éxito.

Excluir esos caminos de la afirmación de éxito no reduce el scope de memoria:
siguen pendientes heap de prefijos acotados de rechazo del observador y
tracebacks retenidos, bajo el scope original fijo y sus precondiciones.
No se demuestra heap de rechazo, liveness de cleanup o un deadline para todos
los fallos. Se preservan las reglas de fallo existentes, sin ampliar autoridad.

## Disposición y verificación

Los cuatro criterios E05 heredan su clasificación sin cierres. Los siete campos
son insuficientes para aceptación, aunque aporten definiciones, álgebra,
contabilidad y reglas de scope. El bloqueo de evidencia externa se mantiene
sin afirmar ausencia global de fuentes o inviabilidad real. Este asistente no
atribuye aceptación a un revisor temporal independiente ni a custodios; las
identidades y aceptaciones siguen ausentes.

E01–E05 abiertas; E06 separado NOT_RUN y sin autorización de ejecución. I122
conserva IMPLEMENTED_NOT_ADMITTED, sin SOURCE_CAPACITY_VERIFIED, propuesta o
captura habilitadas, rebind o autoridad/destino nuevos. D5/H07 de cierre abiertos;
IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1; D1–D4 e
I1–I20/A52 intactos; brechas globales y reales pendientes. I86/I89/I92
INVALID_CAPTURE no se reanudan ni mezclan.

`python3 docs/validation/D5-I167-audit.py`: resultado esperado
PASS_STATIC_SOURCE_ONLY. Verifica 236 pins contra Git, sintaxis de 79 fuentes,
veinte anclas de coste, cuatro marcadores y cinco relaciones léxicas, además de
los campos, las dependencias, la cancelación simbólica y las asignaciones cero.
Preserva 313 archivos publicados e inputs heredados. No ejecuta el programa,
sus componentes o un calendario; no mide reloj, CPU, IO, heap o plataforma.

Una unidad de cinco archivos: P08, preparación, este documento,
[auditor](../validation/D5-I167-audit.py) y sello. Rollback limitado a los cinco
archivos enumerados en work_unit. El diff supera 400 líneas por evidencia
trazable y auditor autocontenido; el exceso queda informado. Runtime harness
N/A: preparación documental sin cambio runtime. Auditoría antes del stage y
después del commit, push autorizado y comprobación de remoto/árbol limpio.
Publicar el expediente no admite la candidata.

Sólo herramientas documentales Git/JSON/AST. Sin ejecutar, importar o compilar
producto/componentes, tests, benchmarks, schedule, introspección o mediciones.
Sin cambiar fuentes, cuotas, reservas, presupuestos, contrato o inputs. Sin
inspeccionar ni limpiar dev/run_data/D4; sin proveedores, credenciales, consumo,
activación, promoción, despliegue o D6.
