# I130 — reglas de costes y reservas incorporadas a PFC126

Fecha: 2026-11-12, Europe/Madrid. Base publicada:
`e3f8dc292b6f8bda24ccf04bc3d54bdeede5058d`.

**PFC126-CANDIDATE-03 incorpora las reglas de I129 como requisitos del contrato
candidato.** No asigna reservas, no modifica presupuestos numéricos o cuotas y
no acredita costes, capacidad o servicio. PFC126-CANDIDATE-02 e I129 quedan
íntegros. Se mantiene IMPLEMENTED_NOT_ADMITTED, PJC115-R2/captura sin habilitar,
D5/H07 abiertos e IR03 NOT_READY.

[Contrato03](../validation/D5-I130-PLATFORM-CONTRACT-CANDIDATE.json) ·
[Revisión de incorporación](../validation/D5-I130-cost-reserve-rule-incorporation.json) ·
[Auditoría](../validation/D5-I130-audit.py) ·
[Integridad](../validation/D5-I130-integrity.json).

## Cobertura de costes ahora exigida

El nuevo bloque cost_coverage convierte los diez grupos de I129 en requisitos
explícitos, todos sin cotas verificadas. Hay que cubrir los procesos y el runtime
por las ventanas del coordinador, o justificar un sobreconteo conservador:

- Tpre incluye preparación del coordinador, startup/READY del worker y el trabajo
  que éste pueda realizar después de leer RELEASE pero antes del cierre tR del
  coordinador. El nombre de una función no decide su ventana temporal.
- Tworker incluye las contribuciones que continúan desde tR y la espera,
  observación/reap/reanudación del coordinador hasta el retorno exacto True tW.
- Tpost incluye cleanup, after/finish, paquete/parse/validación/agregación y el
  finally completo: listado/tamaños, encode, escrituras context/launch, cierres y
  retorno tF.
- Originales, proyección, JSON/Unicode, hash/sort, nativo, locks, asignación,
  GC/destrucción y servicio de hijos no quedan gratis o fuera de las ventanas.

Se exige declarar el dominio de procesos/servicio y unidades compatibles. CPU
acumulada de procesos paralelos, tiempo wall y espera/servicio denegado son
magnitudes distintas. La prueba debe cubrir todos los segmentos, mediante
partición justificada o cota aditiva conservadora; no puede restar solapamientos
sin evidencia, ni convertir presupuestos o bytes Reader en segundos.

Se preserva la resolución de F127-01 de I128, sin cambios:

```
t0 <= tR <= tW <= tF
Tpre=tR-t0; Tworker=tW-tR; Tpost=tF-tW
```

tW sigue siendo el retorno exacto True de la llamada única wait_worker del
coordinador. La validación posterior califica el éxito sin mover tW. No se usa
el exit físico ni un cleanup tardío para sustituirlo. No se instala reloj o
instrumentación, ni se ejecuta un interleaving para justificar la cobertura.

## Reserva de heap: regla incorporada, asignación cero

Se conservan H01–H10=10432MiB, reserva832MiB y total solicitado11GiB. H11 sigue
siendo overhead allocator1GiB; el total comprometido candidato sigue en12GiB.
Las once cotas completas continúan null y la capacidad no está atestada.

El bloque reserve_accounting.heap fija propietarios H01–H10, unidades exactas
de bytes, todas las asignaciones documentales actuales a0 y saldo832MiB:

```
x_i >= 0, bytes enteros exactos; sum(x_i) <= 832MiB
B_i_nuevo = B_i + x_i
R_heap_nueva = 832MiB - sum(x_i)
sum(B_i_nuevo) + R_heap_nueva = 11GiB
```

Cualquier asignación futura requiere revisión contractual/pins explícitos y
prueba de costes/vidas/capacidad de los presupuestos resultantes. No hay
transferencia automática, préstamo de H11, descuento de referencias, release o
reset. La diferencia presupuesto−subcota no se convierte en holgura probada;
un propietario sin cota no se cubre silenciosamente con reserva.

La cifra0 significa **ninguna asignación documental**, no consumo runtime0 ni
memoria físicamente libre. La adopción de la regla no autoriza aplicarla en
producto, cambiar cuotas o ejecutar componentes.

## Reserva temporal y jerarquía de Tworker

Los presupuestos siguen60/750/60 y30 segundos sin asignar: total900. La nueva
regla usa segundos racionales exactos, finitos y no negativos:

```
y_pre,y_worker,y_post >= 0; sum(y) <= 30
fase_nueva = fase_base + y_fase
R_tiempo_nueva = 30 - sum(y)
sum(fase_nueva) + R_tiempo_nueva = 900
```

Todas las asignaciones actuales son0; el saldo documental sigue30. El30 no
permite automáticamente exceder60/750/60, no es servicio garantizado y no paga
una fase de coste desconocido o no acotado. Una asignación futura necesitaría
revisión y evidencia compatibles, conservando el total y el saldo explícito.

Tworker mantiene600CPU+90IO/hijos+60scheduling=750, sin reserva adicional interna.
Si una futura revisión asignase y_worker a la fase, debe registrar también:

```
z_CPU,z_IO,z_scheduler >= 0
z_CPU + z_IO + z_scheduler = y_worker
suma_categorías_nueva = 750 + sum(z) = 750 + y_worker
```

No se reutiliza el crédito externo como tres créditos independientes, ni se
convierte un presupuesto IO/scheduling supuestamente sobrante en servicio CPU.
No se gasta la reserva original y el saldo restante a la vez. No se convierten
bytes en segundos. Las categorías internas y sus transferencias actuales también
permanecen en sus valores anteriores, con ampliación0 y evidencia pendiente.

## Efecto sobre obligaciones y hallazgos

| Elemento | Estado de la revisión03 |
| --- | --- |
| F127-01 | Resolución contractual de I128 conservada |
| F129-01 | Regla de atribución por ventanas incorporada; cotas pendientes |
| F129-02 | Conservación y jerarquía incorporadas; transferencias no aplicadas |
| F127-02 | Reglas incorporadas; evidencia de costes y servicio abierta |
| E01–E05 | Sin cierre de recursos |
| E06/componentes | Separados, pendientes, NOT_RUN |

Se precisan los textos de evidencia E02–E05 para exigir estas reglas. E01/E06,
los marcadores, el runtime observado/no atestado y los estados de no admisión
se preservan. La regla de admisión no cambia: hacen falta pruebas y gates
independientes, no sólo un contrato mejor definido.

No se alteran las24 cuotas ni el certificado/registro/contrato de captura I122.
La candidata03 es un documento separado: no se incorpora a capture_inputs ni
se habilita desde el worker. Un rebind futuro requeriría revisar fuentes/pins y
el calendario Reader sobre bytes finales. Tampoco se crean autoridad/destino,
recursos reservados, consumo, activación, promoción, despliegue o D6.

## Verificación y publicación

`python3 docs/validation/D5-I130-audit.py` comprueba diferencias permitidas respecto
a la candidata02, adopción exacta de los diez grupos, once propietarios,
marcadores, ceros de asignación, cantidades e identidades simbólicas. Comprueba
AST/hashes y conserva128 archivos publicados anteriormente. No ejecuta producto,
componentes, transferencias o escenarios; Git se usa como helper de metadata y
para el commit/push autorizado. PASS_STATIC_SOURCE_ONLY no es una prueba runtime
de costes, servicio, heap o900 segundos.

Se hace commit y push de todos los cambios de I130. Los antecedentes conservan
sus bytes y significado histórico; el resultado real Git se comprueba fuera de
los documentos, sin self hashes.

P0 sigue83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados.
Brechas globales y obligaciones reales pendientes; I86/I89/I92 INVALID_CAPTURE
sin reanudación/mezcla. No se inspecciona ni limpia dev/run_data/D4.
