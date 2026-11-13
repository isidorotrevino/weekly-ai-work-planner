# I153 — H08 preparado, sin cota completa de Reader y fases

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`f2290da117ed838ffc7944dce3cff47222f9b4eb`.

**P04-H08 queda preparado como expediente de insuficiencia.** La subcota histórica
de payload del grafo fijo no prueba el heap completo de Input Reader/PhaseBytes.
Upper, ajuste al presupuesto candidato de **536870912 bytes (512 MiB)** y slack
permanecen desconocidos. E02 sigue abierta y PFC126-CANDIDATE-03/I122/PJC115-R2
sin admisión. No se aplican cuotas, reservas o cambios de capture_inputs.

## Ruta de revisión

1. Leer los nueve campos y el inventario en [H08](../validation/D5-PFC126-03-E02-H08.json).
2. Contrastar source_evidence y fixed_read_graph_and_partial_payload_reference.
3. Consultar la [preparación I153](../validation/D5-I153-P04-H08-preparation-review.json) para la disposición y el progreso del plan.

I132 conserva sus bytes y su estado histórico PLANNED_NOT_PRODUCED; I153
registra la preparación actual. Este asistente no acredita aceptación del revisor
independiente de memoria previsto en I132 ni autoridad de custodio de runtime.

## Qué significa la subcota de payload

| Término del modelo histórico I122 | Bytes o cantidad |
| --- | ---: |
| Unión conocida del modelo, 490 archivos | 87104500 |
| Cuatro metadatos futuros, anchos modelados | 57277 |
| Tres pasadas más comprobaciones frescas | 3×(87104500+57277)+4852460 |
| Lectura física superior del worker, R | 266337791 |
| Límite de lectura del worker y margen físico | 268435456 y 2097665 |
| Payload chunks + join en el grafo fijo exitoso, 2R | 532675582 |
| Presupuesto candidato H08 menos ese payload | 4195330 |

**4195330 no es slack de heap verificado.** El payload omite cabeceras,
capacidades/growth, mapas, nombres/listings, metadatos, workspace nativo y vidas
completas. Los contadores de lectura no son demanda de heap solicitado vivo.
La cota de lectura del launcher, 261485331, es otra cuenta; no se suma al heap
del worker por compartir helpers.

Se reconstruye la aritmética del registro I122, no una unión nueva del repositorio
actual. Los cuatro archivos futuros continúan sin crear: sus anchos son modelos
históricos condicionados, no resultados ni hashes reales de una ejecución.
El protocolo de tres pasadas y los controles frescos conservan sus supuestos.
Ni el payload exitoso ni su diferencia al presupuesto cubren automáticamente
todos los prefijos rechazados.

Si un documento posterior pasa a ser input de captura, requiere revisar U y
pins de sus bytes finales. +3×nuevos_bytes sólo es aplicable si sigue siendo válido
el mismo grafo de tres pasadas. I153 no añade sus archivos a capture_inputs ni
recalcula una admisión futura por el mero crecimiento de documentación.

## Reader, PhaseBytes y fronteras de vida

| Sitio fuente | Requisito de prueba |
| --- | --- |
| Reader.read | Guardas iniciales de tamaño/cargas/paths, chunks os.read de hasta 65536, digest, fingerprints y join; faltan bloques completos y vidas |
| EOF y estabilidad | La sonda os.read(h,1) y los rechazos por cambios precisan cobertura propia; el modelo exitoso no cubre todo almacenamiento parcial fallido |
| Reader.listing | os.listdir, sorted y tuple se construyen antes de len(names); la cuota de paths no prueba el pico anterior al rechazo |
| Reader.finish | Copias tuple de claves y relecturas/relistados; descartar retornos no demuestra liberación inmediata |
| PhaseBytes | dict(bodies) copia el mapa compartiendo referencias; read devuelve el body guardado y listing delega en Reader |
| InputPlan.after | Construye bodies mientras self.view aún refiere la fase anterior, después reemplaza la vista; faltan vidas de callers, errores y vistas antiguas |
| Bindings/targets | Lecturas frescas siguen pasando por Input Reader; una consulta de PhaseBytes no es otra lectura física ni certifica frescura por sí sola |
| MemberReader | Reader de evidencia con caps/lock propios; no transfiere automáticamente esas propiedades al Input Reader del worker |

Ocho relaciones de orden y nueve registros de expresiones, con hashes AST,
documentan controles, construcción, publicación y fase. No son ocho pruebas de
asignación ni de liberación. Se conservan guardas de tamaño, read/unique/path y
estabilidad, sin interpretar su existencia como una cota completa de objeto.

Compartir referencias de bytes en el mapa no significa copia profunda, un nuevo
Reader.read o inmutabilidad profunda demostrada del objeto PhaseBytes. Tampoco
se concede descuento por alias o identidad reutilizada. Las raíces antes/después,
chunks, cuerpo unido, errores y concurrencia necesitan prueba de coexistencia;
no se supone una sola vista viva, dos vistas como máximo, GC inmediato o
retención eterna.

## Cobertura y disposición

Se vinculan **180 pins**, doce proyecciones JSON, 79 fuentes y veinte anclas.
Doce clases de requisitos cubren Reader/metadata, chunks/listas, join, paths,
stat/hash, listings, mapas before, reemplazo after, finish/checks frescos,
rechazos/EOF, procesos/evidencia y concurrencia/nativo/futuros inputs. Cada una
mantiene null en cardinalidad, tamaño, pico vivo y vida completos: **48 valores
desconocidos**. Es cobertura requerida, sin inventario exhaustivo ya demostrado.

Las diez fronteras con H01–H07/H09–H11 permanecen abiertas. Baseline nativo,
originales, roots persistentes, clones, carriers, digest/sort, codecs/árboles,
páginas, salida y overhead requieren asignación explícita. Se hereda el scope
worker/otros procesos de P01 y la aplicabilidad P01/I124; sin extenderla a rutas
arbitrarias. Un carrier no paga su referente; H11 no es reserva libre.

F≤52018, S≤1759, 53777 lotes y 53778 generaciones con inicial conservan el
contexto de clonación heredado, sin convertirlos en número de lecturas o cuerpos
vivos. Falta el modelo exacto P02 de bytes/mapas/nombres/listas/tuplas, growth,
path/stat/hash nativo y vidas de fase. La carencia se refiere al material
suministrado, sin afirmar ausencia global o inviabilidad.

Los nueve campos requeridos están presentes: dos definiciones documentales y
siete insuficientes para aceptación. Se aplica el rechazo I132: 532675582 bytes
de payload no son prueba completa del propietario de 512 MiB. Sin upper, ajuste,
slack, sobrepresupuesto real o memoria ilimitada demostrados. P01 independiente,
P02 exacto y P03 siguen pendientes, sin sustituir demanda H08 con otros paquetes.
Quedan nueve outputs del plan sin producir; I153 no inicia otro paquete.

E01–E05 abiertas; E06 separado, pendiente, NOT_RUN y sin permiso de ejecución.
I122 conserva IMPLEMENTED_NOT_ADMITTED; sin SOURCE_CAPACITY_VERIFIED, propuesta
o captura. D5/H07 de cierre abiertos e IR03 NOT_READY. P0 conserva
83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados y brechas/
obligaciones reales pendientes. I86/I89/I92 INVALID_CAPTURE sin reanudar ni mezclar.

## Verificación y publicación

`python3 docs/validation/D5-I153-audit.py`: **PASS_STATIC_SOURCE_ONLY**.
Contrasta Git/JSON/AST, aritmética histórica, presupuesto y no admisión, con
**243 archivos publicados** e inputs heredados preservados. No ejecuta Reader
ni componentes, importa/compila el objetivo, enumera inputs con su protocolo,
realiza tests, benchmarks, introspección o sondeos de IO/runtime/memoria.

H08, preparación, este documento, [auditor](../validation/D5-I153-audit.py) y
[sello](../validation/D5-I153-integrity.json) forman una unidad documental de
cinco archivos. El diff supera 400 líneas por evidencia generada y auditoría
autocontenida; se informa el exceso sin comprimir código o retirar evidencia.
Runtime harness: N/A, sin cambio de comportamiento runtime. Rollback: retirar
sólo los cinco archivos enumerados en work_unit. Se audita antes del stage y
después del commit, con push y verificación de remoto efectivo y árbol limpio.

Fuentes, candidata03, cuotas, presupuestos, reservas, capture_inputs y autoridad/
destino intactos. Sin recursos reservados, contactos externos, proveedores,
credenciales, consumo, activación, promoción, despliegue o D6. No se inspecciona
ni limpia dev/run_data/D4.
