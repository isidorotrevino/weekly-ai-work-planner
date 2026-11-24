# I238 — revisión documental de W07 de I237

La revisión de W07 encuentra consistentes sus requisitos de trabajo, CPU, unidades compatibles y fronteras de fase con I223 y las fuentes vinculadas. No se identifica un nuevo defecto documental. Se mantiene la **no admisión**: faltan el inventario completo del sucesor, la correspondencia all30, las cotas derivadas, el servicio compatible y las revisiones y aceptación reales. SD01 permanece activo; D5 sigue abierto.

Fecha: 2026-11-24, Europe/Madrid. Base: `7360aec9aeefc1660c17a7afda09b718a606970f`.

El objeto es [W07 candidato de I237](../validation/D5-I223-W07-SUCCESSOR-WORK-CPU-UNITS-CANDIDATE.json). Esta revisión conserva sus bytes y todos los antecedentes. La metodología estática del mismo asistente no aporta independencia de actores, competencia R03/R06 ni aceptación separada R08.

## Dictamen y evidencia

| Aspecto | Resultado de la revisión | Pendiente real |
|---|---|---|
| Contrato W07 | Coinciden entregables, dependencias W03/W04/W05, tres salidas y rechazos de I223 | Autoridad de entrada, baseline y paquetes aceptados |
| Cobertura histórica | 10 actividades, 30 valores trabajo/CPU/wall y 20 vectores de proceso/fase conservados | Inventario y correspondencia completa del sucesor con all30 |
| Compatibilidad | 20 joins de unidades/proceso/fase, 10 requisitos de dueño de latencia y 9 categorías conservados | Identidades exactas, unidades, dominio, ventanas y derivación verificables |
| Conversión a tiempo | Dos rutas condicionales: servicio garantizado o WCET de plataforma exacta; ninguna seleccionada | Trabajo completo, hipótesis y prueba de la ruta aplicable |
| Costes por intento | Siete familias incluyen ambos Readers y el join global | Conteos, costes, composición y revisión reales |
| Fases y reservas | Marcadores y presupuestos candidatos coinciden con I130 | Cotas de fase demostradas y composición W08 |
| Handoff | W06 y W07 alimentan W08 en paralelo; W09 conserva aceptación conjunta | Reconciliación de hipótesis y evidencia de E01–E05 |

Los 30 valores escalares son diez ternas históricas; tampoco los 20 vectores de proceso/fase equivalen a treinta grupos del sucesor. Se preserva la exigencia all30 de I193 sin inventar identificadores de grupos. Los conteos abstractos de I124 no se transfieren automáticamente al sucesor ni se convierten en instrucciones, segundos o prueba de inviabilidad.

Las unidades de trabajo requieren una correspondencia exacta con runtime, plataforma, procesos, dominio de servicio y ventanas de validez. Una fórmula `L + W/r` exige trabajo completo y un teorema aplicable con llegadas, backlog, disponibilidad y concurrencia justificados. Una tasa de tiempo de CPU solo justifica ejecución de CPU; espera, IO, hijos y observación deben cubrirse antes de concluir wall. Tampoco una suma de CPU demuestra por sí sola tiempo transcurrido. No se deduce solapamiento sin prueba ni se interpreta una incógnita como cero.

Se incluyen originales, imports, native, crypto/codecs, asignación, GC/destrucción, locks, IO, hijos, threads, transitivos y rechazos. Las siete familias de coste conservan lookup, identidad, freshness, ledger, frames aceptados y rechazados, ambos pipes, copias y las dos escrituras finales. Los límites de bytes del Reader no son cotas de todo IO o CPU; los snapshots no sustituyen lecturas frescas. La construcción o inscripción offline no hace gratuita su verificación.

## Fronteras temporales y de fase

`tR` corresponde al cierre de RELEASE por el padre. El trabajo del worker después de recibir RELEASE puede empezar antes de ese cierre y debe quedar cubierto por Tpre. Tworker conserva la observación, reap y el retorno exacto `True` de `wait_worker` hasta `tW`, incluso cuando el worker ya terminó físicamente. Tpost comprende validación, cleanup, `finally` y las escrituras context/launch hasta el retorno normal `tF`.

C10 es transversal y se compone dentro de las fases. Los candidatos Tpre/Tworker/Tpost de 60/750/60 segundos y la partición worker 600/90/60 no constituyen cotas verificadas. No se asignan otros 600 segundos a C04, grupos, procesos, threads o ventanas. Los 30 segundos de reserva continúan sin asignar; no se transfieren ni se aplican cuotas. El objetivo de 900 segundos sigue sin prueba y un watchdog no demuestra terminación exitosa.

W06 y W07 comparten las dependencias W03/W04/W05 y alimentan W08. W07 no necesita aceptación previa de W06 como dependencia inversa; sí exige justificar y reconciliar las hipótesis de memoria, caché, allocator, carga e interferencia usadas por una eventual derivación. No toma prestado un heap todavía no demostrado. W04 conserva el servicio sin cualificar; W08 deberá componer las fases; W09 deberá revisar conjuntamente E01–E05. W10 reconcilia los mismos hechos y cualquier cambio invalida las cotas afectadas.

La autenticidad del baseline, los autores, los cuerpos y sus hipótesis deben resolverse antes de W09. La congelación final, C, mapping, E06, payload, Q, root, claim y recibo no sustituyen prueba antecedente. Se conservan las exclusiones de scope, los gates negativos y la frontera CE12 de I223. Las tres salidas de W07 permanecen sin aceptar.

## Verificación y límites

La [reconstrucción](../validation/D5-I238-I237-source-reconstruction.json) registra 23 criterios y 987 pins de entrada. El [dictamen legible por máquina](../validation/D5-I238-I237-documentary-review.json) conserva las 33 mutaciones documentales rechazadas por I237 y añade 10 rechazos propios sobre unidades, vectores, latencias, WCET desconocido, hipótesis de servicio, native, bytes/IO, C10, memoria e invalidación por cambios.

El audit reconstruye los requisitos desde I223, I130, P06/P07, CE01/CE07 y W04/W05, comprueba los enlaces JSON y sus hashes y reproduce el candidato y la preparación de I237. No invoca los `main()` de publicación anteriores ni introduce nuevas proyecciones de presencia. El sello preserva 679 archivos publicados y los cuatro artefactos de esta unidad distintos del propio sello.

Comando de comprobación documental:

```text
python3 docs/validation/D5-I238-audit.py
```

Resultado exigido: `PASS_STATIC_SOURCE_ONLY_W07_REVIEW_WORK_CPU_UNITS_MISSING_NOT_ADMITTED`.

Harness de runtime: **N/A**. Solo se leen documentos, Git, hashes y metadatos, y se alteran copias documentales en memoria. No se ejecutan producto ni componentes, imports, compilación, discovery/tests, benchmarks, WCET experimental, probes ni mediciones de CPU/IO, plataforma, servicio o reloj. No se contactan proveedores, asignan actores, crean identidades o pruebas positivas, cambian cuotas, reservas, bindings, fuentes o destinos de ejecución.

La unidad supera 400 líneas por sus pins, reconstrucción y preservación; se declara el exceso sin reducir evidencia. Reversión: retirar exactamente estos cinco archivos nuevos, sin tocar antecedentes:

- `docs/design/D5-I238-I237-W07-REVIEW.md`
- `docs/validation/D5-I238-I237-source-reconstruction.json`
- `docs/validation/D5-I238-I237-documentary-review.json`
- `docs/validation/D5-I238-audit.py`
- `docs/validation/D5-I238-integrity.json`

## Siguiente paso

El siguiente trabajo documental del orden I223 es preparar W08 (cotas de fase), conservando la ausencia de evidencia real de W04/W05/W06/W07. Para aceptación efectiva de W07 siguen siendo necesarios autores y cuerpos genuinos, cobertura completa all30, unidades/servicio o WCET compatibles, composición de costes y revisión R03/R06 con aceptación separada R08. La publicación de I238 no concede esa autoridad ni cierra gates.
