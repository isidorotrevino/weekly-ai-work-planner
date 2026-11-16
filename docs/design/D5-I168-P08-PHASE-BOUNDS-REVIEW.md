# I168 — P08 conforme como expediente; éxito en 900 sin demostrar

Fecha: 2026-11-16, Europe/Madrid. Base:
`18f5e64d531e78794c9c064a47bc7b8acb6c5719`.

La revisión no encuentra defectos documentales bloqueantes en P08 preparado
por I167. Conserva los siete campos de I132, las seis dependencias y la
insuficiencia de sus premisas. **No acredita cotas por fases ni éxito dentro
de 900 segundos.** Las tres cotas verificadas permanecen null; las siete
premisas del teorema siguen sin satisfacer. E05 y D5 abiertos; I122/PJC115-R2
mantienen la no admisión.

## Ruta de revisión y método

El [dictamen](../validation/D5-I168-P08-documentary-review.json) contiene
dieciséis comprobaciones. La
[reconstrucción](../validation/D5-I168-P08-source-reconstruction.json) vuelve a
leer 240 entradas de Git, recompone las diferencias por extremos y contrasta
las fases con P06/P07 y las asignaciones de reserva. El
[auditor](../validation/D5-I168-audit.py) conserva además la validación semántica
I167 y sustituye sus límites de publicación por los de esta revisión. Los
documentos I167 mantienen su fecha histórica, 2026-11-15, y sus bytes.

Se contrastan veinte anclas de coste y cuatro marcadores mediante un índice
AST separado en 79 fuentes. La sintaxis confirma definiciones y relaciones
léxicas, no timestamps, calendario entre procesos, servicio, liveness o WCET.
El análisis no importa, compila ni ejecuta las fuentes objetivo.

La reconstrucción es metodológicamente separada y la realiza el mismo
asistente que preparó I167. No satisface independencia de actor u organización,
aceptación del revisor temporal independiente previsto en I132 ni autoridad de
custodio de runtime/plataforma. Esas aceptaciones siguen pendientes.

## Resultados

| Objeto revisado | Resultado |
| --- | --- |
| Plan y dependencias | Siete campos presentes; seis vinculaciones conservadas sin aceptación de recursos |
| Marcadores | Definiciones y fuentes coinciden; dominio monotónico común sin acreditar |
| Éxito calificado | Retorno exacto True separado de comprobaciones posteriores y progreso |
| Partición | Cancelación algebraica válida bajo condiciones; orden real y cobertura completa sin probar |
| Cotas de fase | Tres upper null; siete premisas no satisfechas |
| Presupuesto | 870+30=900 como aritmética candidata, con asignaciones externas/anidadas cero |
| Fallos y heap | Regla de exclusión temporal preserva prefijos de rechazo/tracebacks; sus cotas siguen abiertas |

Los siete campos continúan insuficientes para aceptación. Los cuatro criterios
E05 conservan su disposición heredada, sin cierres. P01/P02/P03/P05/P06/P07
mantienen sus carencias de revisión independiente, identidad, plataforma, heap,
trabajo y compatibilidad. Preparación o revisión documental no implica aceptación
de recursos. P09/P10 siguen sin producirse.

## Álgebra frente a prueba temporal

La reconstrucción parte de los extremos de cada fase: t0→tR, tR→tW y tW→tF.
Sus coeficientes suman −t0+tF, confirmando
Tpre+Tworker+Tpost=tF−t0. No presupone valores de los marcadores. La no negatividad
requiere su orden y un dominio monotónico común aceptado; la identidad por sí
sola no prueba ese orden, el progreso o la cobertura de procesos y latencias.

Cada fase vuelve a enlazar los requisitos P06 y los cruces P07: veinte de cada
tipo en total. Son obligaciones, no una asignación temporal verificada. C02
incluye startup anterior a main; C04 mantiene el trabajo post-recepción del
worker/children que puede preceder al close del coordinador. No se deduce una
barrera adicional del orden léxico ni se coloca automáticamente todo en Tworker.

tW sigue siendo el retorno exacto True de la única llamada wait_worker(process),
sin sustituirlo por salida física, reap o validación posterior. Si el worker ya
salió antes de tR o de wait, dispatch/observación/retorno aún necesitan cobertura.
True no prueba éxito de captura: salida cero, autoridad, inputs, packet, páginas,
resultado funcional, captura y finally deben calificarse por separado sin mover
tW. False/excepción no crea un tW calificado.

tF conserva el retorno normal después del finally y las escrituras/closes
finales. packet.finish lo precede. Las fuentes contienen creación de context,
escrituras de context/launch y closes, pero su presencia no demuestra duración
ni progreso. Los requisitos C07/C08/C09/C10 siguen sin cota completa.

Las siete premisas exigen identidad/reloj, heap/capacidad, trabajo/servicio o
WCET, delays e hipótesis de liveness, éxito/marcadores, partición completa y
cotas verificadas 60/750/60. Ninguna está satisfecha. La conclusión preparada
tF−t0≤870≤900 es condicional; no proporciona un upper real ni demuestra que una
ejecución exitosa exista o termine. Una implicación vacua tampoco habilita la
admisión. No se convierte null, marcador ausente o timeout en cero.

## Reserva y alcance de fallos

Se reconstruye 60+750+60=870 y 870+30=900. Las asignaciones de fase siguen en
cero, así como las de categorías anidadas CPU/IO-child/scheduler. La reserva
no asignada se cuenta una vez; no permite exceder una fase automáticamente,
no garantiza servicio y no aporta crédito por proceso, thread, grupo o
categoría. C04 no recibe otro CPU600; no hay préstamos de H11 o conversión
byte/segundo. La partición 600/90/60 conserva 750 sin probar su cobertura.

El watchdog existente de process.wait es límite de fallo después de RELEASE,
sin deadline extremo a extremo. P08 excluye wait False/excepción, salida no
cero/failure envelope, rechazos y finalización excepcional o inválida del
teorema de éxito. No afirma que todo fallo o cleanup termine dentro de 900.

Esa exclusión no reduce el scope de memoria. Se conservan prefijos acotados
de rechazo del observador y tracebacks retenidos bajo las precondiciones y
fuentes originales. P05 mantiene su dictamen negativo; no se prueba heap de
rechazo o liveness de cleanup con la revisión. El bloqueo por evidencia externa
permanece sin declarar ausencia global de material ni inviabilidad real.

## Preservación y publicación

E01–E05 abiertas; E06 separado NOT_RUN y sin autorización de ejecución. I122
conserva IMPLEMENTED_NOT_ADMITTED, sin SOURCE_CAPACITY_VERIFIED, propuesta o
captura habilitadas, rebind o autoridad/destino nuevos. D5/H07 de cierre abiertos;
IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1; D1–D4 e
I1–I20/A52 intactos; brechas globales y reales pendientes. I86/I89/I92
INVALID_CAPTURE no se reanudan ni mezclan.

`python3 docs/validation/D5-I168-audit.py`: resultado esperado
PASS_STATIC_SOURCE_ONLY. Verifica Git/JSON/AST, campos, premisas, fases y
contabilidad; preserva 318 archivos publicados e inputs heredados. No ejecuta
un programa objetivo o calendario, ni mide reloj, CPU, IO, heap o plataforma.

Unidad de cinco archivos: este documento, dictamen, reconstrucción, auditor y
[sello](../validation/D5-I168-integrity.json). Rollback limitado a los cinco
archivos enumerados en work_unit. El diff supera 400 líneas por evidencia
trazable y auditor autocontenido; se informa el exceso. Runtime harness N/A:
revisión documental sin cambio runtime. Auditoría antes del stage y después
del commit, push autorizado y comprobación de remoto/árbol limpio. Publicar
no admite la candidata.

Sólo herramientas documentales Git/JSON/AST. Sin ejecutar, importar o compilar
producto/componentes, tests, benchmarks, schedule, introspección o mediciones.
Sin cambiar fuentes, cuotas, reservas, presupuestos, contrato o inputs. Sin
inspeccionar ni limpiar dev/run_data/D4; sin proveedores, credenciales, consumo,
activación, promoción, despliegue o D6.
