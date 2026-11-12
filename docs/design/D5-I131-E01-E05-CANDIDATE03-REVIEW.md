# I131 — revisión E01–E05 de PFC126-CANDIDATE-03

Fecha: 2026-11-12, Europe/Madrid. Base publicada:
`51a997ef03d7101d84b75a26ff409c9dd52f0bac`.

**E01–E05 quedan revisadas; ninguna cierra su prueba de recursos.** La candidata03
conserva coherencia documental en marcadores, cobertura, presupuestos y reservas,
pero las reglas nuevas no aportan cotas ni atestaciones. Se mantiene la no
admisión de I122/PJC115-R2, IMPLEMENTED_NOT_ADMITTED y D5/H07 abiertos. No se
modifica la candidata03 ni se prepara otra revisión del contrato.

[Matriz E01–E05](../validation/D5-I131-E01-E05-review.json) ·
[Comparación de evidencia](../validation/D5-I131-resource-evidence-delta.json) ·
[Auditoría](../validation/D5-I131-audit.py) ·
[Integridad](../validation/D5-I131-integrity.json).

## Qué se comprobó y qué puede concluirse

La matriz registra20 criterios con referencias JSON-pointer y hashes de sus
valores en los documentos vinculados. Nueve son comprobaciones de coherencia
candidata, uno es una referencia histórica parcial y diez requieren evidencia
de recursos todavía no suministrada. Ninguno de los20 criterios concede por sí
solo cierre de E01–E05. No se confunde aprobar una cuenta documental con probar
el runtime.

| Obligación | Lo que aporta la candidata03 | Lo que falta |
| --- | --- | --- |
| E01 identidad | Referencia heredada y pins fuente | Cierre real de runtime/plataforma y atestación |
| E02 heap |11 propietarios y reservas conservadas | Cotas completas y capacidad disponible |
| E03 trabajo |10 grupos exigidos por ventanas | Trabajo/WCET completo por actividad/proceso/fase |
| E04 servicio | Dominios/unidades compatibles exigidos | Curva de servicio o WCET y latencias atestadas |
| E05 éxito<=900 | Marcadores ordenados y conservación temporal | Cotas de fase, servicio y éxito cualificado probados |

No se encontraron nuevas incoherencias normativas en las comprobaciones
realizadas. Esto no cambia las carencias de evidencia ni equivale a aceptación
del contrato, de la plataforma o de una captura.

## Comparación entre regla y evidencia

Se comparan seis proyecciones explícitas de datos de prueba/referencia:

1. Runtime observado, pins y campos de atestación de candidatas02/03.
2. Cifras y campos de evidencia de heap, excluyendo los dos textos de reglas.
3. Marcadores, presupuestos y campos de prueba temporal, excluyendo las reglas
   y el texto añadido de atribución.
4. Estado normativo de no admisión.
5. Pins directos de fuentes testing.
6. Valores de evidencia de los diez grupos I129 frente a los incorporados en03.

Las seis proyecciones son idénticas. Es una comparación delimitada: no afirma
que todo el contrato tenga la misma semántica. La revisión03 sí añade requisitos
y reglas; su evidencia fuente documenta esas reglas, pero no cambia los valores
de prueba de capacidad. No se observa, importa o ejecuta un runtime nuevo para
esta comparación ni se renueva el manifiesto local I127.

La situación cuantificada sigue siendo:

- **11** cotas completas de propietario de heap null.
- **30** valores de upper de trabajo/CPU/wall null en10 actividades.
- **3** upper de fase null.
- Campos de atestación de operador todos null y curva de servicio sin
  unidad/rate/latency probados.
- Asignaciones documentales de heap, tiempo y categorías internas en0; reservas
  candidatas832MiB/30s intactas, sin disponibilidad efectiva acreditada.

Los desconocidos no se sustituyen por0. La falta de prueba tampoco demuestra
que I122 sea físicamente inviable o que su heap real sea infinito.

## E01 — referencia parcial, no entorno atestado

La referencia del intérprete y el manifiesto I127 siguen vinculados por SHA.
Son observaciones históricas seleccionadas: no demuestran el cierre de lo
cargado/frozen/builtin/extensiones, correspondencia fuente/binario, libc/allocator,
kernel/configuración o dominio de servicio. En I131 no se vuelven a muestrear.

La candidata no presenta responsable, artefacto, firma/validez o capacidad y
servicio atestados. Los pins de fuentes conservados permiten revisar los mismos
bytes; no convierten esas fuentes en garantías del binario o de la plataforma.
E01 permanece abierta.

## E02 — aritmética y reglas correctas, heap sin cota completa

Se conserva10432MiB por H01–H10 más832MiB sin asignar:11GiB solicitados. H11
sigue como overhead1GiB, para12GiB comprometidos candidatos. La separación de
H11 y las reglas x_i/B_i/R_heap están incorporadas; no hay préstamo automático
ni doble crédito de reserva. Son presupuestos de diseño, no cuotas aplicadas.

Las once proof_upper_bytes siguen null. El modelo condicional H04 y los payloads
parciales H08/H09/H10 no sustituyen cotas completas, ni la diferencia hasta un
presupuesto acredita holgura. Faltan originales/runtime, tamaños/vidas, nativo,
codecs, marcos, allocator y capacidad disponible en el dominio declarado.
Conservar una reserva no completa esas pruebas. E02 permanece abierta.

## E03 — requisitos de cobertura adoptados, trabajo aún desconocido

Los diez grupos de I129 están ahora exigidos por contrato. Se incluyen el worker
antes de READY, su posible trabajo después de leer RELEASE pero antes del
cierre tR del coordinador, la observación hasta tW y el finally hasta tF.
Originales, proyección, JSON/hash/sort, GC/destrucción y nativo no quedan gratis.

Los30 upper por actividad siguen null y no hay upper global de cobertura CPU/wall
o noncopy. Las visitas lógicas al clonador y los bytes de inputs no son segundos
ni trabajo de todos los procesos. Para cerrar E03 faltan cotas compatibles de
cada contribución y el proceso/ventana que cubren. E03 permanece abierta.

## E04 — exigir servicio no acredita disponer de él

El reparto600CPU/90IO-hijos/60scheduling=750 y la jerarquía y_worker/z son
coherentes, sin reserva interna extra. El contrato exige dominio de procesos y
unidades compatibles, no descontar solapamientos sin prueba y cubrir latencias
de observación. No declara que esos objetivos estén disponibles o reservados.

La curva de servicio mantiene unidad/rate/latency null y evidencia vacía. No hay
prueba de CPU, IO/hijos, clock/scheduling o cobertura del wall. Frecuencia,
identidad de CPU, presupuesto o W/budget no reemplazan una garantía sustentada.
E04 permanece abierta.

## E05 — fronteras resueltas, duración no probada

Se conserva t0<=tR<=tW<=tF, con tW en el retorno exacto True de wait_worker. La
calificación posterior de éxito no desplaza ese punto; False/excepción no se
convierten en éxito por cleanup. F127-01 conserva su resolución contractual.

60/750/60+30=900 y las reglas de transferencia y/z evitan omitir intervalos o
multiplicar créditos. Ninguna transferencia se aplica. Los tres upper de fase,
la garantía de reloj/servicio y la terminación exitosa siguen sin probarse. El
watchdog process.wait900 permanece separado del objetivo extremo a extremo.
E05 permanece abierta.

## Disposición y verificación

F127-02 tiene sus reglas incorporadas, pero evidencia de costes/servicio abierta.
F129-01 conserva la cobertura requerida antes de tR y F129-02 la conservación y
jerarquía sin asignaciones. E06 no se revisa ni ejecuta: componentes separados,
pendientes y NOT_RUN. No se emite SOURCE_CAPACITY_VERIFIED ni autoridad/destino,
no se habilita captura y no se cambian capture_inputs, código, presupuestos o
cuotas. Un rebind futuro tendría que revisar fuentes y calendario Reader sobre
bytes finales; estos nuevos documentos no se incorporan silenciosamente.

`python3 docs/validation/D5-I131-audit.py` verifica hashes, AST, referencias de los
20 criterios, comparación de proyecciones, cantidades y no admisión. Conserva
133 archivos previamente publicados. PASS_STATIC_SOURCE_ONLY significa
consistencia documental, no prueba de recursos o ejecución. Sólo se usan helpers
estándar para datos y Git; no se ejecutan producto, componentes o benchmarks.
El auditor sirve antes de stage y después del commit de todos los cambios I131,
cuyo push se verifica en Git sin self hashes.

P0 sigue83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados.
D5/H07 y brechas globales/obligaciones reales pendientes; IR03 NOT_READY.
I86/I89/I92 INVALID_CAPTURE sin reanudación/mezcla. Sin proveedores/credenciales,
consumo/reservas operativas, activación, promoción, despliegue o D6. No se
inspecciona ni limpia dev/run_data/D4.
