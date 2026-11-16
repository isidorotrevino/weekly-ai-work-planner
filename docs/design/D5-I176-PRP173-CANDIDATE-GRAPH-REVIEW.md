# I176 — Grafo I175 conforme como candidato negativo; cuatro bindings pendientes

Fecha: 2026-11-16, Europe/Madrid. Base:
`1ca7da0aa697ac88dc24271d86da861dd3e4d17e`.

La revisión no encuentra defectos documentales bloqueantes en el grafo y los
bindings I175 de PRP173-INDEX-01. **Confirma 495 rutas, 491 bindings reales y
cuatro cuerpos aún sin hash.** Las copias mantienen los gates negativos y están
separadas de los documentos vigentes. No hay grafo positivo íntegro aceptado,
rebind o autoridad. E01–E05 abiertos, E06 NOT_RUN y D5 sin cerrar;
I122/PJC115-R2 mantienen la no admisión.

## Ruta de revisión y método

Leer el [dictamen](../validation/D5-I176-I175-documentary-review.json), con
dieciséis comprobaciones. La
[reconstrucción](../validation/D5-I176-I175-source-reconstruction.json) verifica
671 entradas contra Git, deriva el conjunto de rutas desde el registry candidato
y resuelve sus aliases a bytes concretos. Contrasta las diferencias permitidas
respecto a los originales, los mapas del certificado/manifest y el descriptor.

Un segundo algoritmo, Kahn, reconstruye un orden acíclico con las dependencias
de hash y el prerrequisito de protocolo raw→manifest. También verifica que el
orden publicado en I175 satisface ambos. Nueve anclas AST vuelven a vincular
las reglas de InputPlan/Reader y admisión, sin ejecutar sus funciones.

El [auditor](../validation/D5-I176-audit.py) conserva además las comprobaciones
semánticas I175, sustituyendo sus límites de publicación por los de I176.
No se ejecuta el parser de autoridad del producto, componentes o calendario
Reader. Comparar JSON, hashes y sintaxis no proporciona evidencia runtime.

La reconstrucción es metodológicamente separada y la realiza el mismo asistente
que preparó I175. No satisface independencia de actor u organización, aceptación
de recursos/packaging o autoridad de custodio. Esas aceptaciones permanecen
pendientes.

## Bindings confirmados

| Objeto | Resultado de revisión |
| --- | --- |
| Registry candidato | Sólo añade el índice real a los 480 prior inputs conservados |
| Certificado candidato | Sólo cambia mapa/count de fuentes; 489 SHA resuelven a bytes reales y excluyen su propio hash |
| Manifest candidato | Sólo cambia su mapa de nueve fuentes, con los SHA candidatos correctos de registry/certificado |
| Alias de rutas | 491 fuentes de bytes distintas; previews no instalados ni añadidos como rutas de captura |
| Descriptor de autoridad | 491 pins conocidos, tres componentes pendientes, schema propio y fase NOT_AUTHORIZED |
| Pertenencia | 494 capture_inputs y 495 rutas con autoridad, sin duplicados |

La revisión compara los objetos completos de las copias con sus originales,
restaurando únicamente los campos de binding permitidos; el resto coincide.
Schemas, source_revision, valores numéricos, tests y autorizaciones no se
alteran. Cada SHA del ledger se contrasta con los bytes de su fuente candidata,
sin resolver una ruta lógica a los bytes activos cuando corresponde una copia.

El certificado sigue IMPLEMENTED_NOT_ADMITTED, CP07 false, atomicidad no
verificada y componentes NOT_RUN. El manifest sigue NOT_RUN_SOURCE_ONLY, sin
ejecución funcional o de componentes autorizada. El índice conserva el estado
negativo publicado en I173 y no aporta aprobación firmada de recursos.

## Cuatro pendientes y alcance del orden

Las rutas pendientes son raw, resultado y sello de componentes, más la
autoridad final. Sus cuerpos, hashes y tamaños son null; no se reemplazan con
digests de relleno o resultados inventados. El descriptor de 55.792 bytes no
es uno de esos cuerpos ni miembro físico extra del grafo. Su schema no es
d5.joint-capture-authority.v2 y no debe instalarse como autoridad.

Los tres hashes tardíos null del manifest son intencionados: resultado y sello
lo referenciarían después. No constituyen un mecanismo para cerrar las cuatro
rutas faltantes ni se rellenan creando un ciclo. La autoridad no se autopinnea;
certificado, resultado y sello fijan sus precedentes en sus respectivos mapas.

El orden hash reconstruido y el prerrequisito manifest antes de raw son
compatibles. La aciclicidad demostrada cubre las dependencias de empaquetado
declaradas. Los documentos históricos fijos se tratan como hojas inmutables;
sus referencias archivadas conservan commit e identidad de bytes, sin
remapearse al registry/certificado candidatos. Esto no demuestra de nuevo todo
el grafo semántico histórico o el cierre de recursos.

## Cotas de lectura confirmadas

| Cuenta del estado negativo candidato | Bytes |
| --- | ---: |
| 491 cuerpos conocidos | 87.114.629 |
| Upper de cuatro cuerpos faltantes | 68.864 |
| Upper único | 87.183.493 |
| Tres pasadas más lecturas frescas heredadas | **266.402.939** |
| Límite vigente por Input Reader | 268.435.456 |
| Margen condicionado | **2.032.517** |

Se recalculan las sumas desde blobs publicados y los envelopes PRP173; el
descriptor no se usa como sustituto de los bytes futuros de autoridad. Las
cuentas de coordinador y worker permanecen separadas, sin reset o pooling,
con el mismo calendario y 4.852.460 bytes frescos heredados bajo sus premisas.

Los máximos de los cuerpos reales cumplen las condiciones publicadas. La cota
corresponde a estos bytes negativos concretos más las cotas de los cuatro
ausentes. Un certificado o índice positivo tendrá otros hashes y puede tener
otros tamaños: necesita regeneración y revisión. El envelope general de
PRP173, 266.536.487 con margen 1.898.969, sigue condicionado al mismo grafo,
nueve máximos, implementación/targets/bindings/rutas y listings. No acredita
fit final positivo, heap/CPU/servicio o duración de 900 segundos.

Los bindings de output, metadata/contexto/launcher/paquete y la aceptación
del protocolo fuera del Reader continúan pendientes. El worker sólo fijaría
el índice por hash; no evalúa firmas o verdad de sus pruebas. El resultado
negativo de P09 conserva el alcance de su antiguo grafo de 146 adiciones.

## Disposición y preservación

La membresía candidata es revisable, pero cuatro rutas no están materializadas
y faltan evidencia aceptada, custodios, revisores independientes, E06 y el
índice sucesor. Una futura cadena positiva exigiría metadatos regenerados,
resultados reales por vías separadas autorizadas, autoridad al final y revisión
de bytes/bindings/ciclos/output antes de una admisión independiente. I176 no
autoriza ejecutar, cambiar fuentes/cuotas o aplicar un rebind.

No se modifica ningún registry/certificado/manifest vigente ni capture_inputs,
contrato, presupuestos o reservas. Sin SOURCE_CAPACITY_VERIFIED, gate
actualizado, propuesta/captura habilitadas o autoridad/destino nuevos.
D5/H07 de cierre abiertos e IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/
1 PARTIAL UI04.1; D1–D4 e I1–I20/A52 intactos; brechas globales y reales
pendientes. I86/I89/I92 INVALID_CAPTURE no se reanudan ni mezclan.

`python3 docs/validation/D5-I176-audit.py`: resultado esperado
PASS_STATIC_SOURCE_ONLY. Verifica diferencias, fuentes de bytes, conjuntos,
dependencias, gates negativos, cotas y ausencias. Preserva 363 archivos
publicados e inputs heredados; no ejecuta producto/componentes o calendario.

Unidad de cinco archivos: este documento, dictamen, reconstrucción, auditor y
[sello](../validation/D5-I176-integrity.json). Rollback limitado a los cinco
archivos enumerados en work_unit. El diff supera 400 líneas por evidencia
trazable y auditor autocontenido; el exceso queda informado. Runtime harness
N/A: revisión documental sin cambio runtime. Auditoría antes del stage y tras
commit, push autorizado y comprobación de remoto/árbol limpio. Publicar no admite.

Sólo herramientas documentales Git/JSON/AST/bytes. Sin importar/compilar/ejecutar
producto/componentes, tests, benchmarks, schedule, introspección o mediciones.
Sin inspeccionar ni limpiar dev/run_data/D4; sin proveedores, credenciales,
consumo, activación, promoción, despliegue o D6.
