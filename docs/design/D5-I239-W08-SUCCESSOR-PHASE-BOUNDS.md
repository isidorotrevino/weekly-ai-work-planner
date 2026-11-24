# I239 — W08 preparado; cotas de fase y éxito en 900 pendientes

W08 queda preparado como expediente documental de requisitos del sucesor para I223. Define la evidencia necesaria para las tres fases y su composición, preserva los cuatro marcadores y mantiene la **no admisión**. No aporta cotas temporales verificadas, servicio garantizado, liveness ni aceptación de recursos. SD01 permanece activo; las tres salidas W08 siguen sin aceptar y D5 continúa abierto.

Fecha: 2026-11-24, Europe/Madrid. Base: `7722e3ed2b5965ff0043583efbbe3b05ffe7719f`.

El [candidato W08](../validation/D5-I223-W08-SUCCESSOR-PHASE-BOUNDS-CANDIDATE.json) vincula exactamente los entregables, dependencias W04/W05/W06/W07, salidas, rechazos y restricciones del [plan I223](../validation/D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json). Conserva las fuentes y revisiones previas sin cambiar sus bytes. La preparación del mismo asistente no proporciona independencia de actores ni revisión competente R03/R06 o aceptación separada R08.

## Evidencia que deberá aportar una propuesta admisible

| Objeto | Requisito preparado | Estado real |
|---|---|---|
| Baseline y autoridad | Scope efectivo auténtico y las dependencias W04/W05/W06/W07 aceptadas | Faltan; SD01 activo |
| Reloj y marcadores | Cuatro eventos del coordinador en un dominio monotónico compatible | Identidades, binding del sucesor, valores y garantías sin aportar |
| Tpre | Cobertura completa hasta el cierre RELEASE, incluido worker concurrente anterior a tR | Upper y derivación null; candidato 60 s |
| Tworker | Desde tR hasta retorno exacto True de wait_worker, con observación/reap | Upper y derivación null; candidato 750 s |
| Tpost | Validación y finalización exitosa hasta retorno normal tF | Upper y derivación null; candidato 60 s |
| Premisas | Siete requisitos históricos P08 conservados y exigencia de prueba completa del sucesor | Los siete sin satisfacer |
| Composición | Prueba de cobertura, unidades, servicio/WCET, delays y liveness compatibles | Join y upper extremo a extremo null |

Se requieren autor de prueba temporal y garante de servicio separados de revisores, revisión R03/R06 y aceptación separada R08. No se asignan personas ni se inventan identidades, firmas, cuerpos, hashes de evidencia real o autoridad. Los pins de este expediente identifican documentos, sin convertirlos en evidencia positiva de plataforma.

## Partición y alcance del teorema

Las definiciones históricas de I130 y el teorema condicional de P08 son antecedentes. Sus anclas I122 no vinculan automáticamente el sucesor PGO181: cada marcador exige correspondencia efectiva de fuente y evento, runtime, reloj, unidad, resolución y garantías compatibles. Ningún marcador se instrumenta ni se recoge.

La obligación es `t0 <= tR <= tW <= tF` en el reloj del coordinador. El auditor reconstruye las diferencias formales:

```text
Tpre    = tR - t0
Tworker = tW - tR
Tpost   = tF - tW
Tpre + Tworker + Tpost = tF - t0
```

La cancelación algebraica es verificable sin timestamps. No demuestra orden real, no negatividad, cobertura temporal, existencia de una ejecución exitosa ni progreso. Para concluir éxito dentro del objetivo hacen falta todas las premisas y cotas de fase derivadas en la misma unidad wall. La implicación condicional tampoco constituye una prueba de liveness por vacuidad.

`t0` es la entrada del coordinador en launch. `tR` es el retorno normal del cierre de RELEASE por el padre, después de completar la escritura y newline. El worker puede recibir RELEASE y trabajar antes de tR: Tpre debe cubrir startup anterior a main y ese trabajo concurrente o una sobrecota conservadora justificada. No se presupone una barrera adicional ni se atribuye todo lo posterior a la recepción a Tworker.

`tW` es el retorno exacto `True` de wait_worker. La salida física del worker, su recepción de RELEASE, un reap anterior o la validación posterior no lo sustituyen. Si el worker ya terminó antes de tR o de la llamada, dispatch, observación y retorno continúan dentro de Tworker. La cobertura no deja un hueco exit-to-wait-return.

`tF` es el retorno normal de launch después de finally y las escrituras y cierres finales. Tpost cubre cleanup, inputs frescos, after/finish, lectura y validación de evidencia, comprobaciones de paquete y las dos salidas context/launch exitosas. packet.finish no es tF. C10 sigue siendo transversal dentro de las fases, sin cola gratuita o presupuesto adicional.

El retorno True es necesario, pero la elegibilidad de captura exitosa requiere además salida cero, comprobaciones de autoridad/inputs/packet/páginas/funcionalidad/captura y finalización válida. Las comprobaciones posteriores no desplazan tW. False, excepción, timeout, salida no cero, rechazo o finalización inválida no proporcionan el claim de éxito. No se iguala un marcador ausente o upper desconocido a cero.

No se afirma que todo fallo o cleanup termine en 900 segundos. Esta exclusión temporal conserva la cobertura de costes de fallos de W07 y de prefijos de rechazo, tracebacks retenidos y vidas de memoria de W06. Tampoco demuestra liveness de cleanup. Se deberán justificar IO, locks, scheduler, observación, hijos, carga, reintentos, señales y demás hipótesis ambientales usadas en una prueba efectiva.

## Trabajo, heap, servicio y reserva

El ledger enlaza por fase los 20 requisitos históricos de vectores y sus 20 joins de W07: 8 para Tpre, 6 para Tworker y 6 para Tpost. Son requisitos históricos, sin asignación verificada del sucesor. Se conserva all30 completo y no se reduce a diez actividades o treinta valores escalares. Originales, native, hijos, threads y transitivos siguen dentro del inventario requerido.

W06 y W07 son entradas paralelas de W08. Sus pruebas de heap, vidas, allocator, caché, carga, unidades y servicio deben referirse a los mismos hechos y reconciliar sus hipótesis. W08 no subsana mediante esta preparación las pruebas ausentes de W04/W05/W06/W07. Ambos Readers, el join global y cada coste añadido de identidad, crypto, freshness, frames, custodia, ledger, rechazo, cleanup y salida deben quedar cubiertos. No se convierten bytes, clones o visitas en segundos ni se resta solapamiento no probado. La suma de CPU tampoco demuestra wall.

La aritmética candidata conserva `60+750+60=870` y `870+30=900`. La partición worker conserva `600 CPU + 90 IO/hijos + 60 scheduler/observación = 750`. No son cotas verificadas ni capacidad o servicio atestados; no se añaden otros 600 segundos a C04, grupos, procesos, threads, ventanas o categorías. Los 30 segundos de reserva siguen sin asignar, con transferencias externas y anidadas cero. Un coste desconocido no se paga por reserva ni se obtiene crédito doble por categoría. No se cambian cuotas, presupuestos o reloj.

El watchdog histórico de process.wait opera después de RELEASE y no es un deadline extremo a extremo ni garantía de éxito o liveness. Si falta una demora acotada compatible o la cota demostrada excediera el objetivo, el resultado sigue siendo no admisión. La falta actual de prueba tampoco demuestra inviabilidad.

## Handoff y verificación

W09 deberá revisar conjuntamente E01–E05 con baseline auténtico, autores conocidos, cuerpos y supuestos completos. W10 congelará esos mismos hechos; cambios posteriores invalidan las cotas afectadas. C, mapping, E06, payload, Q, root, claim y recibo no sustituyen evidencia o autoridad antecedente. No se crean records positivos de fase, BASIS o index, ni se aplica refresh o rebind; se conserva la frontera CE12 de I223.

La [preparación revisada](../validation/D5-I239-preparation-review.json) registra cuatro marcadores, tres fases, siete premisas pendientes, tres roles sin asignar y tres salidas sin aceptar. El [auditor](../validation/D5-I239-audit.py) comprueba 992 pins de entrada, reproduce la reconstrucción y revisión I238 sin invocar mains anteriores, verifica los enlaces JSON, la cancelación formal y la conservación candidata, y rechaza 39 mutaciones documentales en memoria. El [sello](../validation/D5-I239-integrity.json) preserva 684 archivos publicados y los cuatro artefactos de esta unidad distintos del propio sello.

Comando documental y resultado exigido:

```text
python3 docs/validation/D5-I239-audit.py
PASS_STATIC_SOURCE_ONLY_W08_PHASE_BOUNDS_MISSING_SD01_ACTIVE_NOT_ADMITTED
```

Harness de runtime: **N/A**. Solo documentos, Git, hashes, metadatos y álgebra formal propia. Sin ejecutar, importar o compilar producto/componentes, discovery/tests, WCET experimental, benchmarks, probes o muestreo de reloj, CPU/IO, schedule, plataforma o servicio. Sin helpers, nuevos canales/inputs/outputs de producto, contactos, provisión, firma, keygen, inscripción, claims, cuotas o reservas. No se inspecciona ni limpia dev/run_data/D4 y no se reanudan I86/I89/I92.

Se mantiene I122 IMPLEMENTED_NOT_ADMITTED, sin SOURCE_CAPACITY_VERIFIED, propuesta/captura habilitadas o permiso de ejecución. Permanecen cero paquetes reales aceptados, cero gates de prelaunch cerrados y cero obligaciones E01–E05 cerradas; D5/H07 abiertos e IR03 NOT_READY.

Unidad documental única de cinco archivos, con exceso de 400 líneas declarado por trazabilidad y preservación. Reversión limitada a retirar estos cinco archivos nuevos:

- `docs/design/D5-I239-W08-SUCCESSOR-PHASE-BOUNDS.md`
- `docs/validation/D5-I223-W08-SUCCESSOR-PHASE-BOUNDS-CANDIDATE.json`
- `docs/validation/D5-I239-preparation-review.json`
- `docs/validation/D5-I239-audit.py`
- `docs/validation/D5-I239-integrity.json`

El siguiente paso documental es revisar W08 y sus fronteras; la aceptación efectiva requerirá la evidencia y las decisiones competentes pendientes. El commit y push publican este expediente y no lo convierten en admisión.
