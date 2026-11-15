# I165 — P07 preparado; compatibilidad y servicio sin demostrar

Fecha: 2026-11-15, Europe/Madrid. Base:
`ddee9044329da00965c80f95d3a3c3087304c6f0`.

P07 reúne los requisitos de compatibilidad de trabajo, runtime, plataforma y
latencias de PFC126-CANDIDATE-03/I122. **Los siete campos están preparados y son
insuficientes para aceptación.** P02/P03 no acreditan identidad y servicio del
destino; P06 no aporta trabajo completo, unidades compatibles o WCET verificados.
E03/E04 continúan abiertas; PJC115-R2 conserva la no admisión y D5 sigue abierto.

## Ruta de revisión

1. Consultar los siete campos de [P07](../validation/D5-PFC126-03-E03-E04-COMPATIBILITY.json).
2. Revisar los veinte cruces de P06 y sus valores desconocidos antes de evaluar conversiones.
3. Contrastar el mapa de latencias, las hipótesis y la desigualdad requerida de Tworker.
4. Leer la [preparación I165](../validation/D5-I165-P07-preparation-review.json),
   las dependencias y el [sello](../validation/D5-I165-integrity.json).

I132 y los expedientes anteriores conservan sus bytes y estados históricos.
P07 registra la preparación actual; no convierte la existencia de un documento
dependiente en aceptación de recursos. La revisión I164 de P06 es conformidad
documental del mismo asistente, sin independencia de actor ni aceptación WCET.

## Contenido de los siete campos

| Campo I132 | Resultado concreto de la preparación |
| --- | --- |
| Correspondencia runtime/plataforma/proceso/unidad | Veinte cruces de P06, sin identidades exactas ni servicio compatible verificados |
| Conversión trabajo/servicio o WCET | Dos rutas condicionales, ninguna seleccionada; parámetros y derivación null |
| Propiedad de latencias | Diez obligaciones de cobertura; ninguna latencia acotada, sin deducciones por overlap |
| CPU/IO/children/scheduler/nativo | Nueve registros fase/categoría; cotas verificadas y derivaciones null |
| Hipótesis de proveedor/carga/interferencia | Material P03 vinculado; autoridad, validez y cumplimiento sin acreditar |
| Trabajo antes de tR y salida hasta tW | Ventanas y obligaciones conservadas; sobreconteo, observación y finally sin cota |
| Vector de Tworker y desigualdad | Objetivo 600/90/60 conservado; vector verificado y suma verificada null |

Los veinte cruces mantienen el grupo, conjunto de proceso y fase de P06.
Faltan trabajo/unidad o WCET, runtime y plataforma exactos, dominio de servicio,
unidad/tasa/latencia y derivación. Los tres conjuntos de proceso requeridos no
equivalen a enumeración completa de PIDs/threads. Las treinta cotas de los grupos
y los 120 campos seleccionados de los vectores P06 continúan sin demostrar.

## Condiciones para una conversión revisable

La ruta de servicio exige trabajo transitivo completo y garantía inferior
atestada en unidades y dominio compatibles. Debe justificar llegadas, backlog
inicial, readiness, concurrencia, ventanas de servicio y composición de todos
los contribuyentes. Una eventual curva beta(dt)=r·max(0,dt−L), con r>0, sólo
permite usar L+W/r si un teorema aplicable demuestra que todo el trabajo W queda
servido bajo esas condiciones. P07 no aporta ese teorema, W, r o L aceptados.

La tasa por tiempo de CPU sólo da tiempo de ejecución CPU bajo sus hipótesis;
requiere además cotas de servicio denegado, IO/children, scheduling y observación
antes de concluir wall. Una tasa por wall debe declarar qué latencias ya incluye.
Se debe justificar la composición de latencias por proceso/ventana y evitar
créditos dobles o deducciones sin prueba. La suma de CPU concurrente no equivale
por sí sola al elapsed del coordinador.

La ruta alternativa exige WCET justificado para runtime/plataforma exactos y
todos los originales, imports, nativo, codecs, asignación, GC/destrucción y
supuestos de memoria/cache/carga. Debe declarar si acota CPU o wall y cubrir los
delays restantes. Ninguna ruta usa MHz, número de cores, cuotas ordinarias,
watchdog o W/presupuesto como garantía de servicio. Bytes y clones abstractos
de I124 no se convierten en segundos; se preservan sus precondiciones.

## Ventanas y atribución

Las definiciones del coordinador se conservan sin timestamps: t0 entrada a
launch; tR retorno normal del close tras RELEASE/newline; tW retorno exacto True
de la única llamada wait_worker(process); tF retorno normal de launch tras
finally y escrituras/closes, con elegibilidad de éxito independiente.

C02 exige el arranque anterior a main. C04 cubre el trabajo del worker y children
que puede seguir a recibir RELEASE y preceder al close del coordinador. Hace
falta partición justificada o sobreconteo conservador completo; el orden léxico
no demuestra el calendario entre procesos.

La salida física del worker no es tW, incluso si precede a tR o a wait. Dispatch,
reap, observación y retorno del coordinador pertenecen a Tworker y necesitan
cota. True no prueba éxito de captura; las comprobaciones posteriores no mueven
tW. False, excepción, timeout o cleanup posterior no sustituyen el marcador.

C07/C08 cubren cleanup, inputs y evidencia; C09 incluye verify, listing/sizes,
codificación y context/launch create/write/close hasta tF. packet.finish no es
tF. C10 atraviesa procesos y ventanas; su nativo, GC/destrucción y locks no se
omiten ni reciben presupuesto extra. El mapa requiere separar términos mixtos
o justificar sobreconteo aditivo. No acredita cierre transitivo ni progreso.

La desigualdad pendiente es:
`Tworker <= U_CPU + U_IO_child_wait + U_scheduler_observation <= 600+90+60 = 750`.
Los tres U y su suma verificada siguen null. Es un requisito de cobertura bajo
dominio/unidades compatibles, no una desigualdad ya probada. Tpre y Tpost
requieren coberturas completas separadas con objetivos 60 y 60; C04 no obtiene
otro CPU600. Los objetivos 60/750/60 más reserva 30 conservan el total 900,
sin transferencias ni reserva adicional por grupo, categoría, proceso o thread.
El watchdog 900 es límite de fallo de wait, sin garantía de éxito o cleanup.

## Dictamen y límites

Los ocho criterios heredados E03/E04 conservan su clasificación, sin cierres.
La no aceptación de P02/P03/P06 se propaga a P07; P05 mantiene su dictamen
negativo de heap. Se conserva el bloqueo por evidencia externa y no se afirma
ausencia global de material o inviabilidad real. No se prepara el teorema de
fases P08; P08–P10 siguen sin producirse.

Este asistente prepara el expediente sin atribuir aceptación al revisor
independiente de scheduling/IO/WCET ni a custodios de runtime/plataforma. Quedan
pendientes sus identidades, autoridad, validez y material de respaldo, junto con
las hipótesis de señales/retries, carga/interferencia, IO/children y liveness.
E01–E05 abiertas; E06 separado NOT_RUN y sin autorización de ejecución.

I122 sigue IMPLEMENTED_NOT_ADMITTED, sin SOURCE_CAPACITY_VERIFIED, habilitación
de propuesta/captura, rebind o autoridad/destino nuevos. D5/H07 de cierre abiertos;
IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1; D1–D4 e
I1–I20/A52 intactos; brechas globales y reales pendientes. I86/I89/I92
INVALID_CAPTURE no se reanudan ni mezclan.

## Verificación y publicación

`python3 docs/validation/D5-I165-audit.py`: resultado esperado
PASS_STATIC_SOURCE_ONLY. Comprueba 228 pins contra Git, 79 fuentes por AST,
veinte anclas de coste, cuatro marcadores, siete campos y presupuestos,
preservando 303 archivos publicados e inputs heredados. Sólo se ejecutan
herramientas documentales; no se importan, compilan o ejecutan fuentes objetivo.

Una unidad de cinco archivos: P07, preparación, este documento,
[auditor](../validation/D5-I165-audit.py) y sello. Rollback limitado a esos cinco
archivos enumerados en work_unit. El diff supera 400 líneas por la evidencia
trazable y auditor autocontenido; se informa el exceso. Runtime harness N/A:
preparación documental sin cambio runtime. Auditoría antes del stage y tras
commit; push autorizado y comprobación de remoto/árbol limpio. Publicar no admite.

Sin ejecutar producto/componentes, tests, benchmarks, schedule, introspección o
mediciones de runtime/plataforma; sin cambiar fuentes, cuotas, reservas,
presupuestos, contrato o inputs. Sin inspeccionar ni limpiar dev/run_data/D4.
Sin proveedores, credenciales, consumo, activación, promoción, despliegue o D6.
