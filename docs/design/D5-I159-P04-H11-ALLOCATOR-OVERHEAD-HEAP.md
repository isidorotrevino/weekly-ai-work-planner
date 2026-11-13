# I159 — H11 preparado, sin cota completa de overhead

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`8f919d08ec79ca6c8b51a9c04c4d997a4059ffb3`.

**P04-H11 queda preparado como expediente de insuficiencia.** Faltan la
correspondencia del asignador exacto y una cota completa de overhead de backing,
retención y fragmentación. Upper, ajuste al presupuesto candidato de
**1073741824 bytes (1 GiB)** y slack permanecen desconocidos. E02 sigue abierta y
PFC126-CANDIDATE-03/I122/PJC115-R2 sin admisión. H11 no es reserva adicional de
heap solicitado ni RSS. No se aplican cuotas, reservas o cambios de capture_inputs.

## Ruta de revisión

1. Leer los nueve campos y el inventario en [H11](../validation/D5-PFC126-03-E02-H11.json).
2. Contrastar metric_and_coverage_requirements, los requisitos de dominios y la aritmética candidata.
3. Consultar la [preparación I159](../validation/D5-I159-P04-H11-preparation-review.json) para la disposición y el progreso del plan.

I132 y los paquetes anteriores conservan sus bytes; I159 registra la preparación
actual sin reescribir el estado histórico PLANNED_NOT_PRODUCED. Este asistente
no acredita aceptación del revisor independiente de memoria previsto en I132
ni autoridad de custodio de runtime.

## Métrica y cobertura por demostrar

H01–H10 cubren solicitudes de almacenamiento vivo; H11 debe cubrir overhead del
asignador no pagado ya como almacenamiento solicitado. P01 exige backing
comprometido del heap del worker, sin equipararlo a toda reserva de espacio
virtual, RSS, stacks, kernel o heaps del coordinador/hijos. P02 deja sin establecer
el backend/configuración nativos y su correspondencia source/binario/target.

La obligación es demostrar, para el mismo estado t y dominios probados:

`C_worker(t) <= R_worker(t) + O_worker(t)`

C representa backing comprometido según el modelo exacto; R, solicitudes vivas
reales distintas; O, overhead no negativo que cubra el resto aplicable. La
correspondencia no está probada. Si se prueban esa cobertura y ambas cotas
completas, sumar sus superiores puede acotar C. No se obtiene O restando picos
independientes ni restando a C una cuenta R con duplicados/sobreconteo conservador.
Tampoco se supone una identidad de backend sin prueba.

## Aritmética candidata, sin prueba de demanda

| Cuenta candidata03 | Bytes |
| --- | ---: |
| Suma de presupuestos solicitados H01–H10 | 10938744832 |
| Reserva solicitada no asignada, 832 MiB | 872415232 |
| Heap solicitado candidato, 11 GiB | 11811160064 |
| Overhead H11 candidato, 1 GiB | 1073741824 |
| Heap comprometido candidato, 12 GiB | 12884901888 |

Las sumas concuerdan con el contrato. **12−11 GiB es una asignación de diseño,
no una cota de overhead, slack o capacidad disponible.** La reserva solicitada
de 832 MiB sigue separada: no se transfiere a H11 ni se presta H11 a H01–H10.
No hay subcota numérica conocida de overhead; su valor desconocido no se hace cero.

## Dominios, geometría y retención pendientes

Se vinculan **204 pins**, doce proyecciones JSON, 79 fuentes y 24 anclas Python
de carga de trabajo. Ocho relaciones de orden y once registros de expresiones
identifican copias/growth, memo, resets, join, listings, fases, output y trabajo
fuera del lock. Son requisitos de historial y retención, sin probar geometría
nativa, packing, compromiso o liberación de backing. El censo sintáctico no
resuelve el backend ni constituye inventario nativo exhaustivo.

Cinco grupos exigen correspondencia del runtime: dominios de objetos del
intérprete, backing/raw general, extensiones/crypto/codecs/IO, soporte de todos
los threads y frontera de compromiso/mappings/procesos. Son requisitos
condicionados, sin seleccionar por suposición un asignador ni fijar sus fuentes,
binarios, configuración, tamaños de bloque/pool/arena o política de caches.

Doce clases requeridas cubren bookkeeping de dominios, alineación/redondeo,
metadatos, fragmentación de backing parcial, slack de grandes asignaciones,
storage liberado pero retenido, realloc/migraciones, caches por thread, dominios
nativos, errores/cleanup, compromiso y residuo global de historial. Cada una
mantiene null en cardinalidad, tamaño, pico y vida completos: **48 valores
desconocidos**. No se da por hecho que el backend seleccionado use cada mecanismo.

No se aplica un porcentaje fijo de fragmentación, una geometría no fijada o un
factor sobre payload/objetos. Fin de scope, reset, retorno o GC no demuestran
trim/decommit. A la vez, un objeto o freelist que siga reteniendo una solicitud
viva pertenece a R hasta que se pruebe lo contrario; no se convierte libremente
en overhead de almacenamiento ya liberado. Crecimiento/realloc puede requerir
coexistencia de solicitudes y backing que necesita asignación explícita.

Las diez fronteras con H01–H10 siguen abiertas. Headers/capacidades de objetos,
scratch nativo, bloques vivos y referidos permanecen en sus cuentas solicitadas;
metadatos/slack/retención del asignador necesitan correspondencia propia, sin
omitir ni descontar dos veces. Un carrier no paga su referente, ni H11 da una
reserva por thread. Sobreconteo conservador explícito exige cobertura completa,
sin crédito por alias, interning, fusión de witnesses o liberación supuesta.

F≤52018, S≤1759, 53777 lotes y 53778 generaciones con inicial conservan el
contexto condicional P01/I124. No dan tamaños de arena, ocupación, backing
retenido o multiplicidad completa de dominios/threads. Falta el teorema completo
de geometría, historial e interleavings bajo el target exacto, incluidos los
prefijos de rechazo acotados y tracebacks retenidos de la fuente aplicable.

## Disposición y publicación

Los nueve campos están presentes: dos definiciones documentales y siete
insuficientes. Se conserva la regla I132 contra tratar H11 como reserva solicitada,
RSS u overhead cero. Sin upper, ajuste, slack, sobrepresupuesto real o memoria
ilimitada demostrados. P01 independiente, P02 exacto y P03 siguen pendientes;
otros propietarios o capacidad no sustituyen demanda H11. La carencia se refiere
al material suministrado, sin afirmar ausencia global o inviabilidad.

Los once expedientes H01–H11 existen documentalmente, sin aceptación completa
de recursos. Quedan seis outputs del plan sin producir. No se prepara el rollup
P05 ni otro paquete en I159, y la aritmética de presupuestos no lo sustituye.
E01–E05 abiertas; E06 separado, pendiente, NOT_RUN y sin permiso de ejecución.
I122 conserva IMPLEMENTED_NOT_ADMITTED; sin SOURCE_CAPACITY_VERIFIED, propuesta
o captura. D5/H07 de cierre abiertos e IR03 NOT_READY. P0 conserva
83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados y brechas/
obligaciones reales pendientes. I86/I89/I92 INVALID_CAPTURE sin reanudar ni mezclar.

`python3 docs/validation/D5-I159-audit.py`: **PASS_STATIC_SOURCE_ONLY**.
Contrasta Git/JSON/AST, métricas, aritmética candidata y no admisión, con **273
archivos publicados** e inputs heredados preservados. No prueba backend, overhead,
vidas, capacidad, CPU/tiempo o independencia.

H11, preparación, este documento, [auditor](../validation/D5-I159-audit.py) y
[sello](../validation/D5-I159-integrity.json) forman una unidad documental de
cinco archivos. El diff supera 400 líneas por evidencia generada y auditoría
autocontenida; se informa el exceso sin comprimir código o retirar evidencia.
Runtime harness: N/A, sin cambio de comportamiento runtime. Rollback: retirar
sólo los cinco archivos enumerados en work_unit. Se audita antes del stage y
después del commit, con push y verificación de remoto efectivo y árbol limpio.

Sin producto/componentes importados, compilados o ejecutados, tests, benchmarks,
consumo de generadores, introspección, instrumentación, consulta de configuración
runtime/entorno o sondeos de asignador/heap/RSS/IO. Fuentes, candidata03, cuotas,
presupuestos, reservas, capture_inputs y autoridad/destino intactos. Sin recursos
reservados, contactos externos, proveedores, credenciales, consumo, activación,
promoción, despliegue o D6. No se inspecciona ni limpia dev/run_data/D4.
