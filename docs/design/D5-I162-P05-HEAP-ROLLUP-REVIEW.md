# I162 — P05 revisado; cierre de memoria sigue rechazado

Fecha: 2026-11-15, Europe/Madrid. Base de preparación I161:
`b44746d4fdebf5fd512f00d39005386732aea33e`.

**La revisión confirma el dictamen de insuficiencia de P05.** El expediente
negativo es documentalmente coherente y no requiere modificar el rollup. Ningún
propietario aporta una cota completa aceptada; suma solicitada, overhead H11,
suma comprometida, ajuste y slack siguen desconocidos. E02 y D5 abiertos;
PFC126-CANDIDATE-03/I122/PJC115-R2 sin admisión.

## Ruta de revisión

1. Leer los quince controles y siete disposiciones en la [revisión I162](../validation/D5-I162-P05-documentary-review.json).
2. Contrastar Git, propietarios y matriz en la [reconstrucción I162](../validation/D5-I162-P05-source-reconstruction.json).
3. Consultar el [rollup P05](../validation/D5-PFC126-03-E02-HEAP-ROLLUP.json).

I161 estaba pendiente de completar al recibir I162. Su preparación se terminó,
auditó y guardó en un commit separado antes de esta revisión, sin alterar los
propietarios. Se publican ambas unidades. Este mismo asistente prepara y revisa:
la reconstrucción separada no acredita independencia de actor/organización,
autoridad de custodio o aceptación independiente de memoria/capacidad.

## Contraste integrado

| Evidencia reconstruida | Resultado |
| --- | --- |
| 212 pins de entrada | Blobs Git de preparación y bytes actuales concordantes |
| Once archivos H01–H11 y once revisiones | Hashes, métricas, presupuestos y aceptación negativa concordantes |
| Vector de ajuste | Once cotas completas faltantes; upper/fit/slack desconocidos |
| Inventario | 132 requisitos sin verificar y 528 valores null de cantidad/tamaño/pico/vida |
| Matriz | 55 parejas únicas, 110 direcciones concordantes y no reconciliadas |
| Dependencias | Catorce outputs producidos, sin aceptación para cierre de recursos |
| Capacidad y ledger | Disponibilidad sin atestación; cero transferencias documentales |

Los hashes y las revisiones de coherencia de insuficiencia no demuestran memoria
completa. El vector contiene filas para todos los propietarios, sin convertir sus
unknowns en cero o sus presupuestos en demanda. La matriz preserva texto/hash
de ambos lados; reunir las filas no prueba reconciliación, cobertura o ausencia
de omisiones. Los 528 null corresponden a campos de inventario, sin pretender
enumerar cada carencia de ABI/nativo/lifetime/procedencia.

H01–H10 conservan requested-live del worker y H11 allocator_overhead. H02 es el
parent de la suite dentro del worker, no el coordinador. Scope/precondiciones
P01/I124 y prefijos aplicables permanecen intactos, sin alias gratuito, fusión
de witnesses o sobreconteo presentado como solicitud real del estado.

## Sumas y capacidad

| Cuenta | Cota verificada | Aritmética candidata separada |
| --- | --- | --- |
| Diez propietarios solicitados + reserva | null | 10938744832 + 872415232 = 11811160064 bytes (11 GiB) |
| H11 overhead | null | 1073741824 bytes (1 GiB) |
| Heap comprometido | null | 11 + 1 = 12 GiB candidatos |

No se suma ningún término faltante. La aritmética candidata no demuestra demanda,
slack, disponibilidad o permiso para usar reservas. La correspondencia del mismo
estado/dominios entre solicitudes y backing sigue pendiente; no se infiere H11
restando picos independientes o solicitudes sobrecontadas.

El modelo H04 condicional de unos 23 PB no es cota completa ni demanda mínima
que pruebe sobrepresupuesto o inviabilidad. No se cambia por 33 generaciones o
GC inmediato. Los payloads/modelos parciales H08–H10 tampoco se agregan como
memoria completa. P03 no atesta disponibilidad solicitada/comprometida o matching
real de runtime/procesos. Coincidencia declarativa no es capacidad del worker;
sin sumar RSS o heaps del coordinador/hijos como disponibilidad propia.

El ledger conserva cero asignaciones de reservas de heap/tiempo/nested, sin
préstamo H11, recursos reservados o cambios de cuotas. Sus ceros son estado
documental de transferencias, no uso medido, memoria liberada o capacidad sobrante.

## Disposición y publicación

Los siete campos mantienen tres vinculaciones/reglas documentales y cuatro
insuficientes para aceptación. Se aplica el rechazo I132: once cotas faltantes,
cobertura pendiente y capacidad sin atestación detienen el cierre de memoria.
No se prueba sobrepresupuesto real, memoria ilimitada, inviabilidad o servicio.
P01 independiente, P02 exacto y P03 no se sustituyen por el rollup.

Los cuatro criterios E02 no cierran. P06–P10 siguen ausentes y no se inician.
E01–E05 abiertas; E06 separado NOT_RUN y sin permiso de ejecución. I122 conserva
IMPLEMENTED_NOT_ADMITTED; sin SOURCE_CAPACITY_VERIFIED, captura o propuesta
habilitadas. D5/H07 de cierre abiertos, IR03 NOT_READY. P0 conserva
83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1; D1–D4 e I1–I20/A52 intactos y brechas
reales pendientes. I86/I89/I92 INVALID_CAPTURE sin reanudar ni mezclar.

`python3 docs/validation/D5-I162-audit.py`: **PASS_STATIC_SOURCE_ONLY**.
Verifica Git/JSON y coherencia del dictamen negativo, preservando 288 archivos
versionados e inputs heredados. No reejecuta producto, componentes o las pruebas
de runtime de los propietarios, ni prueba memoria, capacidad o independencia.

Cinco archivos I162 forman una unidad: este documento, revisión, reconstrucción,
[auditor](../validation/D5-I162-audit.py) y [sello](../validation/D5-I162-integrity.json).
El diff supera 400 líneas por evidencia generada y auditor autocontenido; se
informa el exceso sin comprimir código o retirar evidencia. Runtime harness N/A:
no cambio runtime. Rollback: sólo los cinco archivos I162 de work_unit, manteniendo
el commit separado de I161. Auditoría antes del stage/después del commit y push
de ambas unidades, con comprobación de remoto efectivo y árbol limpio.

Sin imports/compilación/ejecución de producto o componentes, tests, benchmarks,
introspección o sondeos de asignador/heap/IO/plataforma. Fuentes, contrato, cuotas,
reservas, presupuestos, capture_inputs y autoridad/destino intactos. Sin proveedores,
credenciales, consumo, activación, promoción, despliegue o D6. No se inspecciona
ni limpia dev/run_data/D4.
