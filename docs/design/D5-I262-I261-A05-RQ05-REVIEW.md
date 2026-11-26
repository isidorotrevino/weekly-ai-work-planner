# I262 — revisión de A05/RQ05: recualificación, cotas completas y fases

**No se encuentran defectos documentales nuevos en A05/RQ05 de I261.** El dossier conserva el alcance completo de W05–W08, el orden de sus dependencias y las exigencias de pruebas genuinas sobre el sucesor efectivo. A03/A04/A05 y sus antecedentes siguen sin aceptar, SD01 está activo y se mantiene la **no admisión**. RQ05 no se envía.

Fecha: 2026-11-26, Europe/Madrid. Base: `327cb757387b330bb4afddaf204918464679384d`.

La revisión metodológica contrasta el [dossier I261](D5-I261-A05-RQ05-REQUALIFICATION-COMPLETE-BOUNDS.md) con [I251](D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.md), I223 y W05–W08. El mismo asistente no aporta revisión competente R03/R05/R06 ni aceptación separada R08. No se realiza cualificación o ejecución de producto/componentes ni se producen derivaciones de fuente, heap, trabajo o temporalidad del sucesor.

## Dictamen por paquete

| Paquete | Resultado documental y prueba genuina pendiente |
|---|---|
| W05 — recualificación | Se conservan 179 casos, 321 raíces/12 grupos/30 sitios y doce familias nuevas como obligaciones a recualificar, no prueba transferida de CP03, código escrito o diez tests. Faltan mappings, derivaciones y cuerpos efectivos completos. |
| W06 — heap y vidas | Once owners, 132 clases históricas y 55 pares de overlap conservan sus exigencias. Se necesitan cotas completas de allocation/vidas/picos/native/allocator/GC y rollups requested/committed del mismo estado, más capacidad independiente real. |
| W07 — trabajo/unidades | Se mantiene all30 del sucesor sin reducirlo a10 actividades/30 slots/20 vectores o inventar IDs. Faltan todo trabajo/CPU/wall/espera, unidades compatibles/servicio o WCET y todos los supuestos/delays. |
| W08 — fases | Marcadores exactos, cobertura de ventanas, finally/doble salida y éxito/liveness siguen pendientes. La identidad algebraica y sumar presupuestos no acreditan ejecución exitosa o900 segundos. |
| Handoff | Cada W necesita reviews propias y R08 genuinos. A05 alimenta A06/W09; no cierra automáticamente el join independiente E01–E05/BASIS/índices/CP03/ATOMICITY. |

Las 57 secciones fijadas preservan el contenido completo de los dossiers. Sus dimensiones son longitudes de contenedores documentales, sin valor de inventario completo de pruebas, unidades runtime o cotas verificadas. Los hechos reales, autores, cuerpos y decisiones siguen ausentes; inventario null y cero cuerpos aportados/rechazados/evaluados no acreditan verdad, ausencia global o inviabilidad.

## Dependencias y roles

Se reconstruye el grafo directamente desde I223 y el lote A05. A03/W03 y A04/W04 genuinos preceden a W05; W06 y W07 siguen a W03/W04/W05 y pueden revisarse en paralelo; W08 necesita W04/W05/W06/W07 completos y compatibles. El recorrido por etapas verifica que cada dependencia esté en una etapa previa; no se añade dependencia W06↔W07 o aceptación futura W09/W10 como antecedente inverso.

| Paquete | Reviews primarias exactas | Aceptación propia |
|---|---|---|
| W05 | R03, R05, R06 | R08 separado |
| W06 | R03 | R08 separado |
| W07 | R03, R06 | R08 separado |
| W08 | R03, R06 | R08 separado |

Los cuatro paquetes conservan deliverables, salidas, rechazos y autoridad futura I223 completos. Competencia, appointments, identidad/provenance e independencia genuinos deben sustentar cada review/decisión sobre los mismos cuerpos/scope. Un preparador/autor/provider no se convierte automáticamente en revisor o aceptante; el mismo asistente y su auditor no cubren esas funciones.

## Recualificación y evidencia previa

Los 179 casos de operandos, 321 raíces, doce grupos y treinta sitios mantienen sus enlaces históricos. Se requieren mappings y derivaciones de dominio/reachability/correlación para las fuentes/runtime/imagen/plataforma efectivas. CP03 heredado, reparación de atomicidad escrita, conteos, nombres de tests o certificado negativo no cualifican al sucesor cambiado.

Las doce familias nuevas de rutas custodia/bootstrap/crypto/Reader/salida/fallo y todos los transitivos/procesos/hilos/hijos/guards se conservan. La atomicidad debe cubrir metadata/carga/páginas/aliases/originales/publicación/locks/draft/excepciones/finalización y los prefijos de fallo reales; no se sustituye con contar fases o señalar código. Cada ruta contribuye a heap/work/lifetime y a las salidas/rechazos.

Sólo puede considerarse cualificación previa auténtica con autoridad exacta, scope/validez, custodia R04, revisión R05 y provenance R06. La solicitud de componentes, runtime request y E06 final siguen separados. No se obtiene una prueba nueva mediante discovery/import/compile/run o se usa E06/root/bundle futuro como única autenticación antecedente. Las fuentes sucesoras locales siguen ausentes; no se realiza aquí revisión positiva de su implementación.

## Heap completo y same-state fit

H01–H11 conservan owners y presupuestos candidatos exactos, con cotas/bodies/fit/reviews reales desconocidos. Se exigen originales e hijos retenidos, observer persistente, clones/memo/id/opaque sets, frames/generadores/tracebacks, proyecciones/digests, codecs/Readers/eventos/texto/salidas y dominio de allocation, incluidos native/GC/destrucción/fragmentación y todos los prefijos de rechazo/timeout/fallo pertinentes.

Las 132 clases de allocation y 55 pares de overlap son requisitos de recualificación. Necesitan cardinalidad/tamaño/vida/pico y correspondencia de identidad/alias/owner/domain del mismo estado, o sobreconteo conservador explícito. No se asume GC/destrucción inmediata, reutilización o no solapamiento; no se omiten originales/nativos, mezclan witnesses físicos o acreditan dos veces presupuestos. Restar picos independientes no deriva H11.

Requested H01–H10 y committed/backing/overhead H11 requieren rollup y correspondencia completos del mismo estado y comparación con capacidad W04 genuinamente atestada. Se conservan11GiB requested/12GiB committed, 832MiB sin asignar y H11 separado, sin préstamo/transferencia. RSS, bytes serializados, getsizeof parcial, typed cap, reserva o límite configurado no prueban demanda, slack o disponibilidad. Unknown no es cero o inviabilidad; una prueba incompleta/no finita o que no ajuste mantiene no admisión sin ampliar cuotas.

## Trabajo, servicio y costes globales

El requisito all30 permanece fijado a I193 y exige inventario/correspondencia genuina y completa del sucesor. Las diez actividades históricas, treinta slots work/CPU/wall, veinte vectores proceso/fase y veinte joins de compatibilidad no equivalen automáticamente a treinta grupos sucesores. Tampoco se fabrican IDs para aparentar completitud.

Todo trabajo original/nuevo por actividad/proceso/hilo/hijo/fase debe cubrir CPU, wall, espera/IO/locks/scheduler/reap/observación, native/GC/destrucción, crypto/measurement, frames/rechazos y ambos Readers, registry/ledger/recibo, doble salida/fallo/cleanup. Las siete familias de coste por intento conservan sus fuentes/alcance. Trabajo offline/enrollment previo o un índice acotado no vuelve gratuitos esos costes ni permite lecturas/inputs/helpers ocultos.

La conversión requiere unidad compatible con servicio W04 o WCET justificado del runtime/plataforma exactos y teorema completo con scope/process/windows/validez, arrivals/backlog/readiness/concurrencia, carga/cache/memoria y demoras. `L+W/r` no se aplica a trabajo parcial o rate supuesto. CPU sumada, wall y espera son distintos; bytes/visitas/contadores, MHz/cores/cuota, presupuesto/watchdog o trabajo dividido por900 no son servicio. Overlap y latencia no se restan o acreditan dos veces sin prueba.

## Fases: álgebra frente a prueba real

Se reconstruyen los coeficientes `[-1, 1, 0, 0]`, `[0, -1, 1, 0]` y `[0, 0, -1, 1]`; su suma `[-1, 0, 0, 1]` verifica la identidad formal `(tR-t0)+(tW-tR)+(tF-tW)=tF-t0`. Esta comprobación de coeficientes no verifica orden/no negatividad de marcadores reales, cobertura temporal, existencia de éxito o liveness. Los flags reales de esas propiedades siguen falsos.

`tW` sigue siendo retorno exacto True de wait_worker del coordinador, no exit físico del worker ni validación posterior. Se necesita cubrir exit-to-wait-return incluso con worker ya salido, trabajo worker anterior al cierre RELEASE tR del padre y finally/validación/doble escritura/cierre hasta retorno normal tF. Los checks posteriores no mueven tW y las ventanas deben corresponder a las operaciones/procesos reales, sin asignar todo el worker a Tworker por suposición.

True es necesario e insuficiente para éxito: se requieren cuatro marcadores y comprobaciones independientes de elegibilidad/suficiencia, además de progreso/terminación/IO/lock/scheduler/retry/señales/entorno justificados. False/excepción/timeout, elapsed de un run, watchdog/deadline o marcador ausente no prueban éxito/cota cero. No se promete toda falla/cleanup dentro de900; tampoco se omiten sus costes o heap de traceback/rechazo.

Las peticiones Tpre/Tworker/Tpost conservan 60/750/60 más30 sin asignar y worker 600/90/60 anidado en750. No hay600 extra por C04/actividad/grupo/proceso/hilo/ventana/categoría ni doble crédito de reserva externa/anidada. La aritmética de presupuestos no demuestra servicio, cotas completas o éxito900; una incógnita no se financia con reserva. Los siete grupos históricos de premisas condicionales siguen pendientes para el sucesor.

## Cobertura, parada y handoff

Los siete retornos RB01–RB07 cubren autoridad/scope, W05, W06, W07, W08, reviews/referencias y gaps. Los veinte criterios preservan los doce deliverables y doce salidas originales con autoridad RB01 y revisión/decisión RB06. Todos permanecen pendientes de antecedentes, material y decisiones genuinos.

Se exigen cuerpos/referencias/locators/bytes/digests/autores/providers/custodia/provenance, unidades y todos los supuestos, currentness/validez y motivos por requisito/salida completos y disponibles. Caps, plantillas, hashes, flags o firmas no acreditan verdad. Los autores y baseline deben estar autenticados antes de W09; W10 sólo finaliza/reconcilia los mismos hechos, sin autoridad retrospectiva, completitud anticipada o futuros autores preaprobados.

RB07 conserva SD04/SD05 ante prueba incompleta/no finita/incompatible/overbudget o premisa/autor/review faltante. El gap identifica el requisito/scope/cuerpo/dependiente y trabajo/autoridad separados necesarios, sin ejecutar/profilar/medir/WCET experimental/benchmark/probe/firma/configuración o cambiar cuotas/reservas. Falta de evidencia no prueba ausencia global o inviabilidad.

Una eventual aceptación genuina de W05–W08 completa A05, pero no el join independiente A06/W09 de E01–E05/BASIS/índices/CP03/ATOMICITY. No se añade W09 aceptado como predecesor inverso de sí mismo o de estos paquetes. A06 necesita A02/A03/A04/A05 genuinos y sus límites propios; RQ06 no se envía, inicia o acepta. Cambios de autor/body/source/runtime/image/platform/heap/lifetime/workunit/service/load/epoch/key/policy invalidan afectados, sin transferencia automática de derivación/prueba/approval/aceptación ni refresh/rebind activo.

CE12 sigue privado, diferido y no autorizado. La ejecución final E06/payload/Q/root/admisión/claim/recibo no es nueva condición prelaunch. Se conservan cuatro prerrequisitos externos antes del claim y claim/construcción protegida antes del recibo; claim no es su propia precondición y estados inciertos/parciales/expirados/fallidos no habilitan retry gratuito.

Se mantiene I122 IMPLEMENTED_NOT_ADMITTED, CP07 falso, atomicidad correlacionada sin verificar, componentes/E06 NOT_RUN, PJC115-R2 sin habilitar, D5/H07 abiertos e IR03 NOT_READY. Cero lotes/gates/obligaciones cerrados; treinta gates pendientes y E01–E05 abiertas. No se crean fuentes/runtime records, pruebas positivas, C/Q/root/bindings, autoridad/destino, mapping/claim/worker/recibo o recursos reservados.

## Verificación y publicación

La [reconstrucción](../validation/D5-I262-I261-source-reconstruction.json) fija 1107 entradas contra blobs del commit base y registra 32 criterios. El [dictamen](../validation/D5-I262-I261-documentary-review.json) reproduce candidato/preparación I261 sin llamar mains de publicación históricos, conserva 42 rechazos documentales y añade 38 mutaciones en memoria sobre orden, roles, cobertura, heap/all30/fases, reservas, éxito, gaps/autoridad y join adelantado. El [sello](../validation/D5-I262-integrity.json) preserva 799 archivos publicados y cuatro artefactos propios distintos del sello.

```text
python3 docs/validation/D5-I262-audit.py
PASS_STATIC_SOURCE_ONLY_A05_RQ05_REVIEW_REQUALIFICATION_COMPLETE_BOUNDS_AND_GENUINE_DECISIONS_PENDING_NOT_ADMITTED
```

Harness de runtime: **N/A**. Sólo JSON/Git/hashes/pointers/orden/requisitos, aritmética formal de coeficientes y comprobaciones documentales propias. Sin importar/compilar/ejecutar producto/componentes, discovery/tests/E06, build, profiling/medición/WCET experimental/benchmarks, crypto/codec positivos, firma/keygen/enrollment/provisión/contactos/configuración registry/mapping/reloj/ledger/servicio o probes CPU/IO/procesos/endpoints/replay/crash/restart. Sin cuotas/reservas/capture_inputs o nuevos inputs/outputs/helpers/canales. No se inspecciona/limpia dev/run_data/D4 ni se reanudan I86/I89/I92.

Unidad documental con exceso de 400 líneas declarado por revisión de los cuatro handoffs, reconstrucción, pins y preservación; sin PR solicitado. Rollback limitado a retirar exactamente:

- `docs/design/D5-I262-I261-A05-RQ05-REVIEW.md`
- `docs/validation/D5-I262-I261-source-reconstruction.json`
- `docs/validation/D5-I262-I261-documentary-review.json`
- `docs/validation/D5-I262-audit.py`
- `docs/validation/D5-I262-integrity.json`

I262 termina esta revisión documental. Antecedentes y derivaciones/aceptaciones genuinas A05 siguen pendientes; publicar no satisface esos hitos ni habilita A06 o D5.
