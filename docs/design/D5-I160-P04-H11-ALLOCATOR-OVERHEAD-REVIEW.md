# I160 — H11 revisado, sin cota completa ni ajuste demostrado

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`5829b707d627e42fafce55fd3774df02a2e0c957`.

**La revisión confirma el dictamen de insuficiencia de P04-H11.** El expediente
negativo es documentalmente coherente y no requiere cambiar H11. La cota completa
de overhead y su ajuste a **1073741824 bytes (1 GiB)** siguen sin prueba; upper,
ajuste y slack desconocidos. E02 permanece abierta y PFC126-CANDIDATE-03/I122/
PJC115-R2 sin admisión. H11 sigue separado de heap solicitado, reserva y RSS,
con sus bytes y presupuesto candidato intactos, sin aplicar cuotas ni reservas.

## Ruta de revisión

1. Leer los quince controles y nueve disposiciones de campo en la [revisión I160](../validation/D5-I160-P04-H11-documentary-review.json).
2. Contrastar blobs, vectores, métricas y dominios en la [reconstrucción I160](../validation/D5-I160-P04-H11-source-reconstruction.json).
3. Consultar [H11](../validation/D5-PFC126-03-E02-H11.json) para inventario, dependencias y fronteras pendientes.

Este mismo asistente preparó I159. El recorrido separado del AST aporta
contraste documental, sin acreditar independencia de actor/organización,
autoridad de custodio o aceptación independiente de memoria.

## Qué queda contrastado

La reconstrucción concuerda con **204 pins**, doce proyecciones JSON, 79 fuentes,
24 anclas y los vectores sintácticos por archivo/globales. Ocho relaciones y once
registros de expresiones reproducen sitios de fork/publish, memo, reset, join,
listing, fases, output y trabajo fuera del lock. Son carga de trabajo Python;
no seleccionan un asignador nativo, ni prueban geometría, packing, compromiso,
retención de backing o decommit.

| Cuenta candidata03 recompuesta | Bytes |
| --- | ---: |
| Suma de presupuestos solicitados H01–H10 | 10938744832 |
| Reserva solicitada no asignada, 832 MiB | 872415232 |
| Heap solicitado candidato, 11 GiB | 11811160064 |
| Overhead H11 candidato, 1 GiB | 1073741824 |
| Heap comprometido candidato, 12 GiB | 12884901888 |

La aritmética concuerda. **12−11 GiB no demuestra overhead, slack o capacidad
disponible.** No se traslada la reserva solicitada a H11 ni se presta H11 a
H01–H10. No hay subcota numérica de overhead conocida; desconocido no equivale a cero.

## Métrica y correspondencia pendientes

Se conserva la obligación, para el mismo estado y dominios probados del worker:

`C_worker(t) <= R_worker(t) + O_worker(t)`

C es backing comprometido según el backend exacto; R, solicitudes vivas reales
distintas; O, overhead no negativo que cubra el resto aplicable no pagado ya
como solicitado. La correspondencia no está probada. Si se prueban esa cobertura
y las cotas completas de R/O, su suma puede dar un superior de C. Restar picos
independientes o presupuestos no deriva el overhead; tampoco puede restarse un
R duplicado/sobrecontado como si fuera la solicitud real del estado.

H01–H10 y H11 conservan sus métricas distintas. El backing del worker no se
equipara a toda reserva virtual, RSS, stacks, kernel o heaps del coordinador/hijos.
No se afirma una identidad automática del backend, disponibilidad física o
correspondencia de fuentes Python con binarios nativos.

P02 mantiene backend/configuración null, source/binario/build sin verificar y
referencia histórica sin promover a target. Los cinco grupos D01–D05 conservan
quince valores null de implementación/mapping/retención y cinco vectores vacíos
de pins source/binario/config. Son requisitos, sin inventario exhaustivo de
dominios seleccionados. Los pins vacíos describen este expediente suministrado,
sin afirmar ausencia global de material o consultar el asignador del host.

## Cobertura y vidas

Doce clases mantienen **48 valores null** de cardinalidad, tamaño, pico y vida
completos. Geometría, alineación/redondeo, metadatos, fragmentación, caches,
storage libre retenido, realloc, threads y dominios nativos necesitan pruebas
bajo el target exacto. No se presupone un mecanismo concreto, tamaño de arena,
porcentaje fijo de fragmentación o overhead cero.

Las diez fronteras H01–H10 siguen abiertas. Capacidad, headers, scratch y
referentes vivos solicitados no se convierten libremente en overhead de bloques
ya liberados. Un reset, fin de scope, retorno o GC no prueba trim/decommit;
tampoco se concluye retención eterna. Se requiere cubrir historiales y prefijos
de rechazo/error aplicables con la separación de procesos P01/I124.

Sin reserva adicional por thread, crédito por alias, interning o fusión de
witnesses. Sobreconteo conservador explícito exige cobertura completa y no sirve
como solicitud real para restar overhead. F≤52018, S≤1759, 53777 lotes y 53778
generaciones con inicial conservan el contexto condicional de clonación; no son
geometría u ocupación del asignador ni máximo completo de backing retenido.

## Disposición y publicación

Los nueve campos conservan dos definiciones documentales y siete disposiciones
insuficientes. Los cuatro criterios E02 no cierran. Upper de overhead, ajuste y
slack null; no se prueba sobrepresupuesto real, memoria ilimitada, inviabilidad,
capacidad o servicio. P01 independiente, P02 exacto y P03 siguen pendientes;
la carencia se refiere al material suministrado, sin afirmar ausencia global.

Los once expedientes H01–H11 existen documentalmente, sin aceptación completa
de recursos. Seis outputs siguen ausentes; I160 no prepara P05/rollup ni otro
paquete. E01–E05 abiertas; E06 separado, pendiente, NOT_RUN y sin permiso de
ejecución. I122 conserva IMPLEMENTED_NOT_ADMITTED; sin SOURCE_CAPACITY_VERIFIED,
propuesta o captura. D5/H07 de cierre abiertos e IR03 NOT_READY. P0 conserva
83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados y brechas/
obligaciones reales pendientes. I86/I89/I92 INVALID_CAPTURE sin reanudar ni mezclar.

`python3 docs/validation/D5-I160-audit.py`: **PASS_STATIC_SOURCE_ONLY**.
Verifica Git/JSON/AST y coherencia del dictamen negativo, con **278 archivos
publicados** e inputs heredados preservados. No prueba backend, overhead,
vidas, capacidad, CPU/tiempo o independencia.

Cinco archivos I160 forman una unidad: este documento, revisión, reconstrucción,
[auditor](../validation/D5-I160-audit.py) y [sello](../validation/D5-I160-integrity.json).
El diff supera 400 líneas por evidencia generada y auditoría autocontenida;
se informa el exceso sin comprimir código o retirar evidencia. Runtime harness:
N/A, sin cambio de comportamiento runtime. Rollback: retirar sólo los cinco
archivos enumerados en work_unit. Se audita antes del stage y después del commit,
con push y verificación de remoto efectivo y árbol limpio.

Sin producto/componentes importados, compilados o ejecutados, tests, benchmarks,
consumo de generadores, introspección, instrumentación, consulta de configuración
runtime/entorno o sondeos de asignador/heap/RSS/IO. Fuentes, candidata03, cuotas,
presupuestos, reservas, capture_inputs y autoridad/destino intactos. Sin recursos
reservados, contactos externos, proveedores, credenciales, consumo, activación,
promoción, despliegue o D6. No se inspecciona ni limpia dev/run_data/D4.
