# I161 — P05 preparado; cierre de memoria rechazado

Fecha: 2026-11-15, Europe/Madrid. Base:
`3d4a726586c9c2fcc2976b96ba71e2507fe9a5a3`.

**P05 integra los once expedientes sin admitir memoria.** Ningún propietario
aporta cota completa verificada y ajuste aceptado. La suma solicitada, la suma
con reserva, el overhead H11 y la suma comprometida siguen desconocidos. E02 y
D5 permanecen abiertos; PFC126-CANDIDATE-03/I122/PJC115-R2 sin admisión.

## Ruta de revisión

1. Leer el [rollup P05](../validation/D5-PFC126-03-E02-HEAP-ROLLUP.json): siete campos requeridos.
2. Contrastar los once hashes, revisiones y vector completo de ajuste.
3. Revisar la matriz de 55 parejas y el registro de rechazo antes de cualquier suma.
4. Consultar la [preparación I161](../validation/D5-I161-P05-preparation-review.json).

I161 termina la preparación documental solicitada; el estado histórico del plan
I132 conserva sus bytes. Este asistente no acredita aceptación independiente de
memoria/capacidad ni autoridad de custodio. Producir el rollup no prueba sus cotas.

## Resultado integrado

Los once archivos H01–H11 y sus once últimas revisiones quedan vinculados por
SHA256. Hay once cotas completas faltantes, 132 requisitos de inventario sin
verificar y 528 valores null de cantidad/tamaño/pico/vida. No es una enumeración
exhaustiva de todas las carencias del runtime. Las revisiones confirman coherencia
documental de insuficiencia, sin aceptación independiente de recursos.

Los diez propietarios solicitados conservan la métrica peak_requested_live_heap;
H11 conserva allocator_overhead. El parent de la suite de H02 está dentro del
worker y no se reclasifica como coordinador. Se conservan scope y precondiciones
P01/I124, incluidos prefijos aplicables y retención. Las 110 direcciones de frontera
forman 55 parejas todavía sin reconciliar. Se preserva el requisito de cobertura
completa o sobreconteo conservador explícito, sin omisiones, créditos por alias o
fusión de witnesses. No se afirma haber resuelto la matriz por reunir sus filas.

| Aritmética de presupuestos candidatos | Bytes |
| --- | ---: |
| H01–H10 | 10938744832 |
| Reserva solicitada no asignada, 832 MiB | 872415232 |
| Solicitado candidato, 11 GiB | 11811160064 |
| H11 overhead candidato, 1 GiB | 1073741824 |
| Comprometido candidato, 12 GiB | 12884901888 |

Estos presupuestos se suman; las cotas faltantes no. Sumas verificadas y slack
permanecen null, nunca cero. El modelo condicional H04 de unos 23 PB no se usa
como cota completa ni como demanda mínima que pruebe inviabilidad; no se sustituye
por 33 generaciones o GC inmediato. Los submodelos H08/H09/H10 tampoco se suman
como memoria total o se convierten en slack. H11 requiere correspondencia de
backing con solicitudes del mismo estado; restar picos o presupuestos no la prueba.

P03 no atesta memoria solicitada/comprometida disponible ni matching real del
runtime/procesos. La coincidencia declarativa de métricas y scope no es capacidad.
P01 sigue pendiente de aceptación independiente y P02 de identidad exacta.
No se suman heaps del coordinador/hijos ni RSS como capacidad del worker.

El registro de cero asignación conserva todas las reservas de heap/tiempo/nested
sin transferencia ni recursos reservados. Los ceros son documentales, no medidas
de uso o disponibilidad. Cualquier cambio de fuentes, contrato o presupuesto exige
otro alcance; P05 no optimiza I122 ni paga carencias con reservas.

## Disposición y verificación

Los siete campos están presentes: tres vinculaciones/reglas documentales y cuatro
insuficientes para aceptación. Se aplica el rechazo I132: cualquier término
faltante o sobrepresupuesto impide cierre. Aquí se rechazan once cotas faltantes,
cobertura incompleta y capacidad sin atestación, sin probar sobrepresupuesto real,
memoria ilimitada o inviabilidad. Los cuatro criterios E02 no cierran.

Quedan cinco outputs sin producir, P06–P10; no se inician en I161. E01–E05 abiertas,
E06 separado NOT_RUN y sin permiso de ejecución. I122 IMPLEMENTED_NOT_ADMITTED;
sin SOURCE_CAPACITY_VERIFIED, captura o propuesta habilitadas. D5/H07 de cierre
abiertos, IR03 NOT_READY. P0 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1, D1–D4 e
I1–I20/A52 intactos; brechas reales pendientes e I86/I89/I92 INVALID_CAPTURE
sin reanudar ni mezclar.

`python3 docs/validation/D5-I161-audit.py`: **PASS_STATIC_SOURCE_ONLY**.
Verifica Git/JSON, 212 pins, once propietarios/revisiones, matriz, sumas desconocidas
y ledger, preservando 283 archivos publicados e inputs heredados. No reejecuta
producto, componentes o pruebas de runtime de los propietarios.

Unidad de cinco archivos: rollup, preparación, este documento,
[auditor](../validation/D5-I161-audit.py) y [sello](../validation/D5-I161-integrity.json).
El diff supera 400 líneas por evidencia generada y auditor autocontenido; se informa
el exceso sin comprimir código ni borrar evidencia. Runtime harness N/A: no cambio
runtime. Rollback: sólo los cinco archivos enumerados en work_unit. Auditoría antes
del stage y después del commit; publicación y comprobación de remoto/árbol limpio.

Sin imports/compilación/ejecución de producto o componentes, tests, benchmarks,
introspección o sondeos de heap/IO/plataforma. Fuentes, cuotas, reservas, presupuestos,
capture_inputs y autoridad/destino intactos. Sin proveedores, credenciales, consumo,
activación, promoción, despliegue o D6. No se inspecciona ni limpia dev/run_data/D4.
