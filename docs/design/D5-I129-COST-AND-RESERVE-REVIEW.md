# I129 — F127-02, costes y reservas de PFC126-CANDIDATE-02

Fecha: 2026-11-12, Europe/Madrid. Base publicada:
`33dec048f58879b25de13e80f44f9934495c9fc6`.

**Se completa la revisión de F127-02; su evidencia de costes y servicio sigue
abierta.** Se documentan diez grupos de coste, las11 partidas de heap y reglas
propuestas de conservación de reservas. No se asigna reserva ni se modifica
PFC126-CANDIDATE-02, la implementación o las24 cuotas. La frontera resuelta en
I128 permanece: tW es el retorno exacto True de wait_worker del coordinador.
No hay atestación, cierre de E01–E05 o admisión de PJC115-R2/I122.

[Libro de costes](../validation/D5-I129-cost-coverage-ledger.json) ·
[Revisión de F127-02 y reservas](../validation/D5-I129-F127-02-cost-reserve-review.json) ·
[Auditoría](../validation/D5-I129-audit.py) ·
[Integridad](../validation/D5-I129-integrity.json).

## Atribución por ventanas del coordinador

Se conservan t0<=tR<=tW<=tF y las ventanas Tpre=tR−t0, Tworker=tW−tR,
Tpost=tF−tW. Hay que atribuir costes por esos intervalos, no sólo por el nombre
de una función ni por el momento en que el hijo recibe RELEASE.

| Grupo | Proceso/contribución | Ventana a cubrir |
| --- | --- | --- |
| C01 | Coordinador:registry/authority/discovery inicial | Tpre |
| C02 | Worker:startup/registry/authority/canales antes de READY | Tpre |
| C03 | Coordinador:Popen/READY/escritura y cierre de RELEASE | Tpre |
| C04 | Worker/hijos:trabajo posterior a recibir RELEASE que ocurra antes de tR | Tpre |
| C05 | Worker/hijos:trabajo que continúa desde tR hasta exit | Tworker |
| C06 | Coordinador:dispatch/observación/reap y retorno True en tW | Tworker |
| C07 | Coordinador:cleanup y after/finish de inputs | Tpost |
| C08 | Coordinador:paquete/parse/hash/páginas/agregación/finish | Tpost |
| C09 | Coordinador:finally, listado/tamaños/contexto/launch/cierres/retorno | Tpost |
| C10 | Cada proceso:proyección/codecs/hash/sort/GC/destrucción/nativo/locks | Dentro de las ventanas correspondientes |

**F129-01:** el worker puede leer la línea RELEASE y comenzar imports, suite u
observación antes de que el coordinador cierre su descriptor en tR. Si el
coordinador queda sin servicio tras escribir la línea, incluso puede haber
trabajo significativo del worker antes de tR. No es correcto asignar por defecto
todo el trabajo posterior a recibir RELEASE exclusivamente a Tworker.

Esto no reabre F127-01: las fronteras de I128 siguen ordenadas en el coordinador.
Es una obligación de cobertura de coste. Una prueba puede partir los costes por
intervalo, acotar el solapamiento o sobrecontarlos conservadoramente; necesita
evidencia para hacerlo. El interleaving descrito es lógica de fuente, no una
traza, simulación o ejecución realizada.

La latencia exit físico→retorno True permanece en Tworker. El éxito validado
posteriormente no desplaza tW. El finally de launch sí cuenta en Tpost, aunque
packet.finish se haya llamado antes. No quedan costes gratuitos por cerrar el
worker o terminar la validación principal.

## CPU, espera y bytes no son la misma cuenta

El reparto600CPU+90IO/hijos+60scheduling suma750, pero sigue siendo un presupuesto.
Falta definir/probar el dominio de procesos y unidades de servicio y demostrar
que esos términos cubren el wall time de Tworker. La suma de CPU de procesos
concurrentes puede diferir del camino crítico wall; un sobreconteo conservador
es válido, pero restar solapamientos sin prueba puede omitir demora real. El
modelo debe incluir proyección/JSON/hash/sort, nativo, GC/destrucción, locks,
servicio de hijos, IO y reanudación/observación del coordinador.

Los calendarios heredados de **inputs** fijan266337791 bytes worker y261485331
bytes coordinador; su suma diagnóstica es527823122 bytes en ledgers separados.
No se comparte una cuota entre ellos ni se resetea un Reader. No son segundos,
no incluyen todo el IO stdlib/nativo/paquete y no dan por sí solos un reparto por
fase. Tampoco cubren por omisión una futura incorporación de I126–I129 a los
inputs: eso requeriría rebind y nueva cuenta sobre bytes finales.

Las diez filas de coste conservan cotas de trabajo/CPU/wall null. Los recuentos
fuente I124 se mantienen, pero no sustituyen trabajo no-copy o un WCET completo.

## Reserva de heap:832MiB una sola vez

H01–H10 suman10432MiB candidatos. Con832MiB sin asignar se obtiene11264MiB,
11GiB solicitados. H11 es un presupuesto de overhead allocator de1024MiB:
no es otra reserva libre. El total comprometido propuesto sigue siendo12GiB.
No se acredita disponibilidad física o memoria libre del host.

Para una futura asignación documental explícitamente revisada se propone:

```
x_i >= 0; sum(x_i) <= 832MiB, para H01–H10
B_i_nuevo = B_i + x_i
R_heap_nueva = 832MiB - sum(x_i)
sum(B_i_nuevo) + R_heap_nueva = 11GiB
```

No se aumenta el propietario y se sigue contando al mismo tiempo la reserva
original entera. La asignación propuesta necesitaría evidencia completa de
costes y una revisión contractual; en I129 todos los x_i son **sin asignar**, no
se aplica transferencia alguna. No se trasladan automáticamente H11 u otros
propietarios para ocultar un exceso de heap solicitado o overhead.

Una diferencia presupuesto−subcota no es holgura probada. En H08 esa diferencia
es4195330 bytes; faltan mapas/headers y el resto de su obligación completa. H09 y
H10 también tienen sólo subcotas de payload. H04 conserva el modelo condicional
23096917808804736 frente a un presupuesto6442450944 bytes. Incluso la suma
hipotética de todo el832MiB daría7314866176: el modelo actual no demostraría
ajuste. No se hace esa asignación ni se deduce inviabilidad real de un mayorante
suelto. Las11 cotas completas siguen null y la holgura verificada es desconocida.

## Reserva de tiempo:30 segundos, sin multiplicarla

Los presupuestos60/750/60 suman870 segundos y dejan30 sin asignar. Los30 no
permiten automáticamente exceder un presupuesto de fase, no garantizan servicio
y no convierten una fase sin cota en una fase acotada. Como regla de revisión
futura se propone:

```
y_pre,y_worker,y_post >= 0; sum(y) <= 30
fase_nueva = fase_base + y_fase
R_tiempo_nueva = 30 - sum(y)
sum(fase_nueva) + R_tiempo_nueva = 900
```

Hay además una jerarquía:600+90+60 ya usa todo el750 interno de Tworker. Si en una
revisión futura se asignase y_worker al presupuesto de750, se tendría que
repartir expresamente entre categorías z_CPU,z_IO,z_sched con sum(z)=y_worker.
Entonces la suma interna sería750+y_worker. No se usa y_worker como crédito
nuevo e independiente en cada categoría ni se confunde una supuesta holgura de
IO/scheduler con CPU disponible. No hay reserva interna adicional de categorías.

**F129-02:** las reglas de conservación, dominio y jerarquía anteriores quedan
propuestas para revisión, sin adoptarse en el contrato. En I129 se asignan0
bytes y0 segundos; permanecen832MiB y30s candidatos sin asignar. Es aritmética
documental, no recursos reservados o disponibles. No se convierten bytes en
segundos ni se hace release/reset, descuento de referencias o cambio de cuota.

## Disposición de F127-02

La cobertura por fuente y la conservación de reservas quedan revisadas con
criterios concretos. F127-02 permanece **OPEN_COST_AND_SERVICE_EVIDENCE**: faltan
las cotas por propietario/fase y un modelo atestado de servicio/latencias.
Las reglas de transferencia son propuestas, no una nueva revisión de PFC126.
F127-01 conserva su resolución contractual de I128; E01–E05 siguen abiertas y
E06/componentes permanecen separados, pendientes y NOT_RUN.

No se emite SOURCE_CAPACITY_VERIFIED ni se cambia el certificado
IMPLEMENTED_NOT_ADMITTED. PJC115-R2/captura sin habilitar; D5/H07 abiertos e
IR03 NOT_READY. Contrato02, cuotas, fuentes, autoridad/destino y capture_inputs
quedan intactos. La publicación Git no concede admisión operativa.

## Verificación y publicación

`python3 docs/validation/D5-I129-audit.py` lee AST/JSON/hashes y verifica los
anclajes, diez grupos de coste,11 propietarios, cantidades y conservación
simbólica de ambas reservas, sin ejecutar producto, componentes o interleavings.
PASS_STATIC_SOURCE_ONLY es consistencia documental, no prueba de capacidad,
servicio o tiempo. Se conservan123 archivos publicados previamente; el auditor
funciona antes de stage y después del commit. Git se usa sólo para metadata y
el commit/push de todos los cambios autorizados para I129.

P0 conserva83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados.
Brechas globales y obligaciones reales pendientes; I86/I89/I92 INVALID_CAPTURE
sin reanudación/mezcla. Sin proveedores/credenciales, consumo/reservas operativas,
activación, promoción, despliegue o D6. No se inspecciona ni limpia dev/run_data/D4.
