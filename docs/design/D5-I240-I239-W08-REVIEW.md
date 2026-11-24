# I240 — W08 revisado; las cotas temporales siguen pendientes

La revisión documental de W08 de I239 encuentra consistentes sus requisitos de fases, marcadores y reservas con I223 y los antecedentes vinculados. No se identifica un nuevo defecto documental. Se mantiene la **no admisión**: las tres cotas de fase siguen sin derivación, las siete premisas sin satisfacer y las tres salidas W08 sin aceptar. SD01 permanece activo; D5 continúa abierto.

Fecha: 2026-11-24, Europe/Madrid. Base: `d391a30f85807fa34ce1be28b1e92bd5e0175c86`.

El objeto es [W08 candidato de I239](../validation/D5-I223-W08-SUCCESSOR-PHASE-BOUNDS-CANDIDATE.json). La revisión conserva sus bytes y los antecedentes. El mismo asistente realiza una reconstrucción metodológica separada; esto no acredita independencia de actores, competencia R03/R06 ni aceptación separada R08.

## Resultados del contraste

| Objeto | Resultado documental | Evidencia real pendiente |
|---|---|---|
| Contrato W08 | Entregables, dependencias W04/W05/W06/W07, salidas y rechazos coinciden con I223 | Autoridad de entrada, baseline y dependencias aceptadas |
| Marcadores | Cuatro definiciones exactas de I130, en el dominio requerido del coordinador | Binding del sucesor, identidad/garantías del reloj y valores |
| Partición | Diferencias reconstruidas desde los extremos; cancelación formal correcta | Orden, no negatividad, cobertura temporal y progreso |
| Fases | Tres requisitos 60/750/60, con referencias históricas 8/6/6 por fase | Tres uppers completos, unidades y derivaciones compatibles |
| Premisas | Siete requisitos condicionales de P08 conservados | Pruebas efectivas de todas las premisas del sucesor |
| Reserva | 870+30=900 y reglas externas/anidadas conservadas | Ninguna transferencia aplicada; servicio y cotas sin verificar |
| Handoff | W06/W07 paralelos hacia W08; W09 conserva aceptación conjunta | Reconciliación de hechos y revisión/aceptación competente |

Los cuatro marcadores y las anclas I122 de I130 son definiciones históricas. P08 aporta una formulación condicional, sin prueba del sucesor. W08 conserva esa frontera y exige correspondencia efectiva de evento, fuente, runtime, plataforma y reloj. No recoge timestamps ni instala instrumentación.

La reconstrucción toma las expresiones de I130 `tR-t0`, `tW-tR` y `tF-tW`, forma sus coeficientes y obtiene `[-1,0,0,1]`. Esto confirma `Tpre+Tworker+Tpost=tF-t0`. La identidad no prueba orden real, no negatividad, cobertura completa, existencia de una captura exitosa ni liveness. Las tres cotas verificadas continúan null. Los siete requisitos históricos A01–A07 se conservan sin satisfacer, con evidencia efectiva del sucesor ausente.

El ledger de fases referencia exactamente veinte vectores históricos W07 y veinte joins de compatibilidad: ocho en Tpre, seis en Tworker y seis en Tpost. Sus etiquetas no son PIDs reales ni una cobertura all30 completa del sucesor. Sigue siendo necesaria la correspondencia íntegra, sin reducirla a diez actividades o treinta valores escalares.

## Marcadores, éxito y demoras

Tpre incluye startup anterior a main y el trabajo del worker que, tras recibir RELEASE, pueda ocurrir antes del cierre de RELEASE del coordinador tR. El orden léxico no crea una barrera adicional. No se asigna por suposición todo ese trabajo a Tworker.

Tworker termina en el retorno exacto `True` de wait_worker, tW. La salida física del worker, recepción de RELEASE, reap o validación posterior no lo sustituyen. Dispatch, observación y retorno hasta tW siguen incluidos aunque el worker ya haya terminado antes de tR o de la llamada.

Tpost conserva cleanup, inputs frescos, after/finish, validación y comprobaciones de paquete, finally y escrituras/cierres context/launch hasta el retorno normal tF. packet.finish no es tF. C10 sigue dentro de la composición de fases, sin cola gratuita ni presupuesto añadido.

True es necesario, pero la elegibilidad exitosa requiere además salida cero y las comprobaciones independientes de autoridad, inputs, packet, páginas, funcionalidad, captura y finalización válida. Estas comprobaciones no desplazan tW. False, excepción, timeout, rechazo o finalización inválida no establecen el claim de éxito; ningún marcador ausente o upper desconocido se convierte en cero.

La prueba temporal de éxito no promete que todo fallo o cleanup termine dentro de 900 segundos. Esta exclusión conserva el inventario de costes de fallos de W07 y la cobertura de prefijos de rechazo, tracebacks y vidas de heap de W06. Liveness de cleanup tampoco queda demostrada. IO, locks, scheduler, hijos, observación, reintentos, señales y entorno requieren hipótesis justificadas.

## Reservas y fronteras de fase

La suma 60+750+60=870 y los 30 segundos sin asignar conservan el total candidato de 900. La partición worker 600 CPU + 90 IO/hijos + 60 scheduler/observación conserva 750. Son presupuestos candidatos; no verifican servicio, capacidad o terminación exitosa. No se asigna otro CPU600 a C04, grupos, procesos, threads, ventanas o categorías.

Se conservan literalmente las reglas I130 de reserva externa y anidada, con transferencias de tiempo, categorías y heap en cero. La reserva no paga automáticamente una incógnita ni se cuenta dos veces. No se cambian cuotas, presupuestos o reglas de reloj. El watchdog histórico de process.wait, posterior a RELEASE, no es deadline extremo a extremo ni prueba de liveness o éxito. La ausencia de prueba tampoco establece inviabilidad.

W04/W05/W06/W07 siguen sin aceptar. Sus hechos efectivos de scope, memoria, allocator, caché, carga, unidades, servicio/WCET y validez deben justificarse y reconciliarse. W06 y W07 alimentan W08 en paralelo; W08 no subsana sus pruebas ausentes. Ambos Readers y su join global, originales/native/transitivos y los costes añadidos de identidad, crypto, frames, custodia, ledger, salida, rechazo y cleanup permanecen exigidos. No se resta solapamiento sin prueba ni se usa suma de CPU como wall.

W09 conserva el join de E01–E05 con baseline auténtico, autores conocidos, cuerpos y supuestos completos. W10 congela los mismos hechos y los cambios invalidan las cotas afectadas. C, mapping, E06, payload, Q, root, claim y recibo no sustituyen evidencia o autoridad antecedente. Se preservan las exclusiones, gates negativos y frontera CE12, sin records positivos, refresh o rebind.

## Verificación y publicación

La [reconstrucción](../validation/D5-I240-I239-source-reconstruction.json) registra 25 criterios y 997 pins. El [dictamen](../validation/D5-I240-I239-documentary-review.json) conserva los 39 rechazos documentales de I239 y añade 13 propios: orden/definición de marcadores, reloj, álgebra, omisión de fases/vectores, joins de fase incorrecta, premisas, liveness, doble reserva, transferencia de heap, upper desconocido cero e invalidación por cambios.

El auditor contrasta fuentes primarias y pointers JSON; reproduce el candidato y la preparación de I239 sin invocar mains anteriores ni introducir proyecciones nuevas de presencia. El [sello](../validation/D5-I240-integrity.json) preserva 689 archivos publicados y los cuatro artefactos de revisión distintos del propio sello.

```text
python3 docs/validation/D5-I240-audit.py
PASS_STATIC_SOURCE_ONLY_W08_REVIEW_PHASE_MARKERS_RESERVES_MISSING_NOT_ADMITTED
```

Harness de runtime: **N/A**. Solo comprobaciones documentales propias de JSON/Git/hashes/metadatos, álgebra formal y mutaciones de documentos en memoria. Sin ejecutar, importar o compilar producto/componentes, discovery/tests, WCET experimental, benchmarks, probes ni muestreo de reloj, CPU/IO, schedule, plataforma o servicio. Sin contactos, provisión, inscripción, keygen, firma, claims o nuevos canales/inputs/outputs de producto. Sin modificar cuotas, reservas, fuentes, bindings o destinos. No se inspecciona ni limpia dev/run_data/D4; no se reanudan I86/I89/I92.

La revisión no admite W08, no habilita PJC115-R2 ni ejecución y no cierra gates o E01–E05. I122 conserva IMPLEMENTED_NOT_ADMITTED, D5/H07 abiertos e IR03 NOT_READY. Publicar no constituye atestación de servicio o aceptación de recursos.

La unidad supera 400 líneas por sus pins, reconstrucción y preservación; se declara el exceso. Rollback limitado a retirar exactamente estos cinco archivos nuevos:

- `docs/design/D5-I240-I239-W08-REVIEW.md`
- `docs/validation/D5-I240-I239-source-reconstruction.json`
- `docs/validation/D5-I240-I239-documentary-review.json`
- `docs/validation/D5-I240-audit.py`
- `docs/validation/D5-I240-integrity.json`

El siguiente paquete documental de I223 es W09, conservando el bloqueo por falta de evidencia y aceptación reales de sus antecedentes. El cierre efectivo exige las pruebas y decisiones competentes pendientes; el commit y push de I240 no las sustituyen.
