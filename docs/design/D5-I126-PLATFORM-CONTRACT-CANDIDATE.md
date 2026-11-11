# I126 — contrato candidato de plataforma para I122

Fecha: 2026-11-11, Europe/Madrid. Referencia fuente:
`50c49678568bae2abeefbe5fec0285f26c628283`.

**PFC126-CANDIDATE-01 queda preparado para revisión; no es una garantía del host
ni habilita PJC115-R2.** El contrato propone un presupuesto completo por partida
de heap y una condición de900 segundos extremo a extremo, y enumera qué pruebas
permitirían aceptarlos. Conserva el dictamen I125 y el certificado I122
IMPLEMENTED_NOT_ADMITTED. No ejecuta ni modifica producto/componentes o cuotas.

[Contrato candidato](../validation/D5-I126-PLATFORM-CONTRACT-CANDIDATE.json) ·
[Revisión y no admisión](../validation/D5-I126-platform-candidate-review.json) ·
[Auditoría](../validation/D5-I126-audit.py) ·
[Integridad](../validation/D5-I126-integrity.json).

## Identidad y ámbito

El sujeto es I122-CANDIDATE-01, con las fuentes y anclajes de I125 fijados por
SHA/AST. Se conserva como referencia el intérprete local CPython3.14.4,64bit,
GIL, incluido el hash del binario identificado en I124. Faltan attestations de
stdlib/extensiones/libc/allocator/kernel y dominio de servicio CPU/IO. Identificar
un binario no acredita su equivalencia con fuentes ni su consumo máximo.

El heap incluye asignaciones dinámicas Python y nativas del worker: runtime,
originales y observador. Se distingue solicitado de comprometido por allocator;
no se declara RSS. Los stacks/mappings y los otros procesos necesitan cuentas
separadas si después se afirma capacidad agregada del host. No se presupone que
la máquina actual disponga de los recursos propuestos, ni se reserva memoria.

Los resultados F<=52018, S<=1759 y53778 generaciones de I124 permanecen intactos.
Son evidencia transferible bajo su ámbito original321/12; no son nuevos límites
por hilo ni descuentan witnesses físicos. Los originales opacos siguen contando
como memoria original aunque no se clonen. La prueba de heap debe cubrir
prefixes de rechazo y tracebacks dentro de aquel ámbito, sin confiar en GC
inmediato. Nuevos hooks/rutas/runtime exigirían revisar la transferencia.

## Presupuesto candidato de heap

Se propone para revisión **11GiB de heap solicitado y12GiB de heap comprometido
del worker**. Son decisiones de diseño, no cifras medidas, demanda demostrada,
capacidad disponible o cuotas nuevas del producto. Las partidas dejan una
reserva visible y dan a cada propietario una obligación concreta:

| Partida I125 | MiB candidatos | Prueba exigida |
| --- | ---: | --- |
| H01 runtime/imports/nativo | 256 | Base y asignaciones vivas fuera de FIELDS |
| H02 originales/fixtures | 2048 | Estado privado y originales retenidos |
| H03 observador persistente/hojas | 512 | Objetos, callbacks, locks, parches y escalares |
| H04 clones/memo/id/opaque | 6144 | Contenedores, tablas/buffers y vidas correlacionadas |
| H05 marcos/generadores/tracebacks | 128 | Tamaños y multiplicidad sobre el runtime exacto |
| H06 proyección/digest/fase | 256 | sorted, registros/fila nueva y temporales |
| H07 JSON/Unicode/árboles | 256 | Codificación/parse y coexistencias |
| H08 Reader/PhaseBytes | 512 | Chunks, cuerpos, mapas/listados y headers |
| H09 páginas y flush | 192 | Cuerpos, chunks, listas y temporales |
| H10 Tee/StringIO/raw | 128 | Capacidad, copias y árboles coexistentes |
| Subtotal solicitado H01–H10 | **10432** | Cotas completas por propietario |
| Reserva solicitada explícita | **832** | Asignación revisada, nunca relleno de desconocidos |
| Total solicitado | **11264 =11GiB** | Suma y comparación con capacidad atestada |
| H11 overhead de allocator | **1024** | Arenas/retención/fragmentación, sin confundir RSS |
| Total comprometido | **12288 =12GiB** | Solicitado más overhead |

Cada partida tiene proof_upper_bytes=null, evidencia vacía y estado UNPROVED.
Para probar ajuste hace falta una cota completa en bytes<=su presupuesto, con
vidas y aliases contabilizados. Se permite sobrecontar; no omitir memoria ni
convertir payload/bytes serializados en heap. La reserva832 se cuenta una sola
vez y no puede absorber silenciosamente partidas sin prueba.

El modelo actual de H04 en I124 tiene un mayorante condicional de
23096917808804736 bytes, superior al presupuesto propuesto6442450944. **Ese
mayorante no demuestra ajuste**; tampoco es una necesidad real ni demuestra que
I122 sea inviable. Haría falta una prueba más ajustada de asignaciones/vidas o
una implementación revisada con su propia evidencia. No se ajusta la cuota de
referencias ni se recortan tablas para fingir que cabe.

Las subcotas de payload H08/H09/H10 se preservan como tales; estar numéricamente
por debajo de un presupuesto no concede PASS al propietario completo.

##900 segundos como condición propuesta, no como timeout demostrado

El contrato propone una afirmación más fuerte y explícita que el watchdog
actual: **éxito desde la entrada en launch hasta su retorno final<=900 segundos**,
incluida la escritura final del contexto y el cleanup normal. Se usa un dominio
monotónico del mismo host. El cambio es del objeto de revisión documental;
no se instala un timer ni se cambia campaign_seconds=900.

| Ventana propuesta | Presupuesto |
| --- | ---: |
| Tpre:entrada en launch→RELEASE escrito/cerrado | 60s |
| Tworker:RELEASE completo→salida del worker | 750s |
| Tpost:salida→retorno final con checks/cleanup/contexto | 60s |
| Reserva temporal sin asignar | 30s |
| Total | **900s** |

Dentro de Tworker se propone un reparto conservador600s CPU,90s espera de
IO/hijos y60s scheduling/bloqueo. Son obligaciones, no garantías existentes.
GC, destrucción, codecs, proyección y trabajo nativo se cargan a CPU; hijos/IO y
latencias de servicio tienen cuentas expresas. La suma debe sobrecontar o separar
intervalos de forma verificable, sin vacíos ni doble uso de reservas.

La prueba puede tomar una ruta WCET estática para runtime/plataforma exactos o
una cota de trabajo total más curva de servicio inferior y demoras acotadas. La
ruta aún no se selecciona; rate,latency y pruebas permanecen null/vacías.
No se inventa una frecuencia a partir de trabajo/900. Deben cubrirse originales,
no-copy, native, IO, hijos y scheduling, no sólo clone_metadata.

El process.wait(900) existente empieza después de RELEASE y no cubre Tpre/Tpost;
queda intacto y no prueba el nuevo objetivo. Tampoco se promete que toda ruta de
fallo/cleanup termine en900: el contrato temporal exige éxito en la ruta normal.
La detección/cleanup por timeout sigue teniendo su semántica original, sin otra
habilitación ni modificación de límites.

## Evidencia y decisión de admisión

Se preparan seis entregables concretos:

1. E01:identidades y correspondencia fuente/binario de runtime y plataforma.
2. E02:prueba completa de las11 partidas y capacidad de memoria atestada.
3. E03:trabajo/WCET completo por ventana, incluidas asignaciones/destrucción.
4. E04:servicio CPU y latencias de scheduling/IO/hijos en la misma plataforma.
5. E05:prueba de ajuste60+750+60+30<=900 con anclajes exactos y reservas explícitas.
6. E06:evidencia separada de componentes y CP07/autoridad para admisión real.

Todos están MISSING. E01–E05 permitirían revisar una atestación de recursos;
no autorizan por sí mismos ejecutar. La admisión de PJC/captura requiere además
E06 y los gates independientes. No se convierte la propuesta en garantía
firmada ni se crea un certificado SOURCE_CAPACITY_VERIFIED.

La respuesta I125 «No; dejar dictamen de no admisión» permanece como hecho
histórico. El nuevo contrato es candidato, no una atestación retroactiva.
PJC115-R2/captura siguen deshabilitadas; D5/H07 abiertos e IR03 NOT_READY.

## Conservación y publicación Git autorizada

I126 incorpora la nueva instrucción expresa de hacer commit y push de **todos
los cambios**. Incluye los108 archivos locales acumulados I111–I125 y los cinco
nuevos de I126; no altera los snapshots históricos que decían sin commit/push.
Aquellos campos describen sus respectivos incrementos. Publicar fuentes y
pruebas en Git no concede ejecución, cuotas, captura, promoción o despliegue.
El estado real del commit/push se comprueba en Git, sin introducir self hashes.

La auditoría nueva funciona antes de stage, con índice preparado y después de
commit: usa hashes, conjunto de cambios respecto a la base y ancestro Git.
Los auditores históricos quedan byte a byte como evidencia de sus snapshots;
no se ejecutan después de publicar para hacerles pasar artificialmente sus
supuestos históricos de HEAD/untracked. El auditor I126 verifica sus sellos.

Sólo se usan AST, JSON, hashes y aritmética documental. No se importa, compila o
ejecuta la candidata/producto/componentes ni un benchmark. No cambian las24
cuotas, contrato/registro/certificado I122 o autoridad/destino. Los archivos I126
no se añaden a capture_inputs; una incorporación futura exigirá rebind y nueva
cuenta Reader sobre los bytes finales, incluido Git si formara parte del ámbito.

P0 sigue83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 conservan
aceptación. Brechas globales y obligaciones reales pendientes; I86/I89/I92
INVALID_CAPTURE sin reanudación/mezcla. Sin proveedores/credenciales, consumo,
reservas operativas, activación, promoción, despliegue ni D6. No se inspecciona
ni limpia dev/run_data/D4.
