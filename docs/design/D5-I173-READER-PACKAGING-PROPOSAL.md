# I173 — Índice compacto propuesto: Reader cabe sin cambiar cuotas

Fecha: 2026-11-16, Europe/Madrid. Base:
`f7e5b70a424100b9e0c3dff6369cb2dd225587f8`.

**PRP173-INDEX-01 resuelve el exceso de lectura del empaquetado P09 bajo un
grafo alternativo concreto y límites explícitos de serialización.** Sustituye
las 146 incorporaciones directas por un índice candidato de 9.853 bytes, que
referencia la evidencia completa para revisión fuera del Input Reader. La
cota propuesta, incluyendo metadatos futuros, queda en 266.536.487 bytes por
Input Reader frente a 268.435.456: margen 1.898.969. No se aplica el rebind ni
se admite la candidata; E01–E05 siguen abiertos y E06 NOT_RUN.

## Artefactos para revisar

1. [Índice candidato](../validation/D5-PFC126-03-RESOURCE-ADMISSION-INDEX-CANDIDATE.json):
   veinte outputs P01–P10 y revisiones documentales con SHA reales.
2. [Propuesta](../validation/D5-I173-READER-PACKAGING-PROPOSAL.json): grafo, cambios
   de bindings pendientes, condiciones de tamaño y cuentas por Reader.
3. [Preparación](../validation/D5-I173-preparation-review.json),
   [auditor](../validation/D5-I173-audit.py) y [sello](../validation/D5-I173-integrity.json).

## Separación de bytes de captura y material de revisión

Se conservan los 480 required_prior_inputs históricos y las seis fuentes de
implementación. Una eventual incorporación añadiría sólo la ruta del índice
a required_prior_inputs y a los bindings correspondientes. El código actual
leerá y verificará sus bytes/SHA en BEFORE/AFTER/finish; no interpreta su
schema de recursos, sigue sus referencias o valida sus firmas.

La evidencia completa no se elimina ni comprime como sustituto de una prueba:
permanece en sus rutas y commit, fijada por hashes. El índice registra veinte
artefactos, sus revisiones y un compromiso SHA de las 652 entradas históricas
del cierre documental. Su codificación canónica y manifiesto de respaldo están
indicados para reconstruirlo. Los archivos de apoyo no se declaran como nuevos
miembros físicos de capture_inputs por el mero hecho de ser referenciados.

Un hash de índice o de árbol sólo prueba bindings de bytes. Los revisores y
custodios deben examinar la evidencia real y aportar aceptación independiente
exactamente acotada. El worker no sustituye ese proceso. No se llama a las
referencias lecturas frescas, PhaseBytes o implementación cargada del destino,
ni se insertan binarios externos en el repositorio o el Reader.

El índice actual es **CANDIDATE_NEGATIVE_NOT_ADMITTED**, sin aceptación firmada,
sin E01–E05 verificados y sin E06. Su existencia nunca lo hace promovible.
Una aprobación futura exige un índice sucesor revisado y evidencia aceptada
en rutas versionadas, sin sobrescribir inputs históricos o retcon de los
dictámenes negativos P01–P10.

## Grafo y rebind futuro, sin aplicarlo

| Binding | Actual | Propuesto |
| --- | ---: | ---: |
| required_prior_inputs | 480 | 481 |
| source_bindings del certificado | 488 | 489 |
| source_bindings de componentes | 9 | 9 |
| capture_inputs, sin autoridad | 493 | 494 |
| Unión física con autoridad | 494 | 495 |

El registry mantiene sus schemas y campos permitidos: sólo ampliaría su mapa
existente. La fuente verifica ese mapa mediante PhaseBytes, sin una nueva
lectura física adicional por check de schema. La igualdad exacta de admisión
obliga a actualizar pins de registry, certificado, manifest, componentes y
autoridad de forma coherente. Ninguno se modifica aquí.

La propuesta no exige editar código para este grafo Reader, pero sí requiere
revisión independiente del impacto de bindings y del protocolo de aceptación.
Los expedientes actuales están vinculados al snapshot histórico; no se declaran
automáticamente válidos para nuevos metadatos. El certificado verificado futuro
debería fijar el índice aceptado y las fuentes exactas. Los fallos de recursos
y atomicidad/componentes pendientes no desaparecen con el empaquetado.

## Cota completa de Input Reader

Se retienen 486 miembros originales fijos, con 86.983.017 bytes. Los cuatro
cuerpos I122 susceptibles de rebind se retiran de esa suma y se sustituyen por
cotas explícitas; se incluyen también índice, autoridad y raw/result/seal
futuros. Estas son **condiciones de tamaño de la propuesta**, inferiores a las
cuotas existentes: no cambian ni añaden controles runtime, configuración,
reservas o capacidad de producto.

| Cuerpo variable | Máximo serializado propuesto, bytes |
| --- | ---: |
| Registry | 65.536 |
| Certificado | 65.536 |
| Contrato de capacidad | 8.192 |
| Manifest de componentes | 4.096 |
| Índice sucesor | 32.768 |
| Autoridad | 65.536 |
| Raw de componentes | 512 |
| Resultado de componentes | 768 |
| Sello de componentes | 2.048 |
| Total | 244.992 |

Los cuatro documentos actuales caben en esas cotas; el índice real ocupa
9.853, pero se cobra el máximo 32.768. Para autoridad y metadatos de componentes
se reconstruyen anchos del schema cerrado con SHA de 64 hex, contadores
acotados y newline opcional: 55.142, 327, 417 y 1.529 bytes. No se fabrican hashes,
firmas, autoridades o resultados PASS; sólo se calculan longitudes.

| Cuenta por cada Input Reader | Cota |
| --- | ---: |
| Bytes únicos, fijos más variables | 87.228.009 |
| Tres pasadas físicas | 261.684.027 |
| Checks frescos adicionales heredados | 4.852.460 |
| Total leído | **266.536.487** |
| Límite vigente | 268.435.456 |
| Margen | **1.898.969** |

Se cobra al coordinador el upper fresco mayor del worker como sobreconteo
conservador. No se agrupan, resetean o reemplazan Readers. El factor tres deriva
del mismo InputPlan antes/después/finish; los targets y late bindings conservan
sus checks frescos. La cota adicional heredada sólo se transfiere si no cambian
implementación, runner, targets, bindings, source_revision o sus rutas. El nuevo
índice sólo añade las tres lecturas de manifest: no hay dereferencia recursiva.

Los 495 paths caben en 4096; los bytes únicos dejan 46.989.719 frente a 128MiB.
El máximo individual es 9.755.833 frente a 16MiB. Las listas de directorio deben
conservar estabilidad y el cap de 4096 entradas. Todos los cuerpos finales
deben cumplir las cotas y el mismo grafo; si cambian o se superan, este cálculo
no autoriza consumir margen o mover cuota: se recalcula y revisa.

Esto reemplaza la extensión retenida P09 cuya cota inferior era 287.840.292.
No invalida esa prueba: son grafos distintos. La nueva cota es un upper finito
bajo las condiciones publicadas, sin demostrar capacidad heap/CPU, servicio
de plataforma o duración de 900 segundos.

## Metadata, ciclos y orden de aceptación

Los mapas capture_inputs_before/after añadirían una entrada SHA/path, no los
cuerpos del índice o de la evidencia. El delta real es 138 bytes por mapa,
276 en total. Manteniendo iguales los demás campos del modelo histórico, el
top metadata pasa de 483.286 a 483.562, bajo el allowance histórico 524.288,
con margen 40.726. La materialización del registry añade esa misma entrada;
su cuerpo en memoria no se carga como lectura física nueva.

Sigue pendiente la revisión de bytes y bindings finales de contexto, launcher
y paquete. El modelo histórico de widths no es medición ni evidencia de
captura. Evidence Reader permanece separado; sus cuotas no pagan fuentes de
recursos y sus envelopes de salida no se vuelven a demostrar aquí.

El orden propuesto evita ciclos: una aprobación separada firmaría el root de
evidencia/candidato/fuentes anteriores, excluyendo hashes de registry,
certificado o autoridad posteriores. El índice sucesor fija esa aprobación;
registry y certificado lo fijan después, luego manifest/componentes y al final
la autoridad, sin autopin. No se reutilizan autorizaciones históricas. No se
crea ahora aprobación, firma o componente PASS.

Antes de cualquier rebind real harían falta: aceptación competente de E01–E05,
E06 por su vía separada y autorizada, revisión del protocolo de empaquetado y
de su impacto en pruebas, finales reales dentro de las cotas, pins topológicos
y revisión de admisión independiente. Esta propuesta no da permiso de ejecución.

## Preservación y verificación

E01–E05 abiertas, E06 NOT_RUN, I122 IMPLEMENTED_NOT_ADMITTED; sin
SOURCE_CAPACITY_VERIFIED, propuesta/captura habilitadas o gate actualizado.
D5/H07 de cierre abiertos e IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/
1 PARTIAL UI04.1; D1–D4 e I1–I20/A52 intactos; brechas globales y reales
pendientes. I86/I89/I92 INVALID_CAPTURE no se reanudan ni mezclan.

`python3 docs/validation/D5-I173-audit.py`: resultado esperado
PASS_STATIC_SOURCE_ONLY. Verifica 652 pins históricos contra Git, veinte
outputs/revisiones del índice, nueve anclas AST, widths, grafo, cuentas y cero
activaciones. Preserva 343 archivos publicados e inputs heredados.

Unidad de seis archivos: índice, propuesta, preparación, este documento,
auditor y sello. Rollback limitado a esos seis archivos enumerados en work_unit.
El diff supera 400 líneas por la propuesta, evidencia y auditor autocontenido;
el exceso queda informado. Runtime harness N/A: trabajo documental sin cambio
runtime. Auditoría antes del stage y tras commit, push autorizado y comprobación
de remoto/árbol limpio. Publicar no admite ni aplica el rebind.

Sólo herramientas documentales Git/JSON/AST/bytes. Sin ejecutar, importar o
compilar producto/componentes, tests, benchmarks, schedule, introspección o
mediciones. Sin cambiar fuentes, cuotas, reservas, presupuestos, contratos o
inputs vigentes; sin inspeccionar ni limpiar dev/run_data/D4. Sin proveedores,
credenciales, consumo, activación, promoción, despliegue o D6.
