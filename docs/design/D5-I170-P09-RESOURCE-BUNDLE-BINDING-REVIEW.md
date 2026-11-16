# I170 — P09 conforme como expediente; extensión retenida no cabe en Reader

Fecha: 2026-11-16, Europe/Madrid. Base:
`b3c56370dee223322e84368600566682020af194`.

La revisión no encuentra defectos documentales bloqueantes en P09 preparado
por I169. **Confirma el exceso condicional de 19.404.836 bytes por Input Reader
para la extensión retenida descrita**, junto con las carencias de proveniencia
y aceptación de recursos. No admite el bundle ni demuestra imposibilidad de
otros empaquetados. E01–E05 y D5 siguen abiertos; I122/PJC115-R2 mantienen la
no admisión.

## Ruta de revisión y método

Leer el [dictamen](../validation/D5-I170-P09-documentary-review.json), con
dieciséis comprobaciones. La
[reconstrucción](../validation/D5-I170-P09-source-reconstruction.json) verifica
640 entradas contra Git, deriva el grafo original desde el registry, reconstruye
la selección desde P08 y recompone bytes, diferencias de conjuntos y metadata.
El [auditor](../validation/D5-I170-audit.py) conserva además la validación
semántica I169 y sustituye únicamente sus límites de publicación por los de
esta revisión. P09 y sus entradas conservan sus bytes.

Diez anclas AST vinculan InputPlan, Reader, PhaseBytes, admisión, launch y
worker.main. Se revisan los loops y el acumulador de bytes de la fuente, sin
ejecutar su calendario. No se importa, compila o ejecuta producto/componentes
ni se abren binarios externos o se muestrea runtime/plataforma.

La reconstrucción es metodológicamente separada, realizada por el mismo
asistente que preparó I169. No satisface independencia de actor u organización,
aceptación del revisor de proveniencia/Reader de I132 ni autoridad de custodio.
Esas identidades y aceptaciones siguen pendientes.

## Resultados de la revisión

| Objeto | Resultado |
| --- | --- |
| Plan y roles | Ocho campos presentes; 244 miembros congelados y seis dependencias vinculadas |
| Ledger | 636 rutas contrastadas con tamaño y SHA de Git, sin hashes placeholder nuevos |
| Proveniencia externa | Firma, confianza, validez y aceptación de recursos sin acreditar |
| Contratos y fuentes | Valores numéricos PFC/I122 y bindings de registry/certificado/manifest consistentes |
| Admisión vigente | Conjunto exacto impide añadir directamente el bundle; certificado no admitido y componentes NOT_RUN |
| Calendario y costes | Factor tres condicionado confirmado por los loops del mismo Reader |
| Metadata | Serialización completa del modelo parcial confirma 517.028 bytes; fit final sigue desconocido |
| Ciclos y autoridad | Publicación actual sin autopin; revisión futura del grafo y autoridad sigue requerida |

Los ocho campos permanecen insuficientes para aceptación del bundle completo.
Los hashes prueban correspondencia de bytes de repositorio; no prueban verdad
de una atestación, autoridad del firmante, validez temporal o cierre de recursos.
Las seis dependencias mantienen su no aceptación. P10 sigue sin producirse.

## Cota inferior reconstruida

El conjunto original se deriva de required_prior_inputs, implementation_sources
y los cuatro documentos I122 registry/contrato/certificado/manifest: 490 rutas,
87.104.500 bytes. La selección P08 y su evidencia I167/I168 contiene 244 miembros;
146 son adicionales, sumando 8.963.747 bytes. La unión evaluada tiene 636 rutas.

Para evitar depender de tamaños de documentos que podrían reescribirse en una
admisión futura, se excluyen por completo los cuatro cuerpos I122 mutables:
121.483 bytes. Los 486 originales restantes suman 86.983.017 bytes. Su unión
disjunta con la extensión tiene 632 rutas y 95.946.764 bytes congelados.

La fuente confirma que BEFORE lee cada miembro declarado, AFTER relee el mismo
conjunto de cuerpos y finish utiliza el mismo Reader para releer sus archivos
registrados. Reader.total acumula bytes; PhaseBytes devuelve cuerpos explícitos
sin hacerse pasar por lectura fresca. Bajo las premisas de retener los miembros,
declararlos en un único manifest futuro y completar ese mismo calendario, cada
uno exige tres lecturas físicas. No se aplica 3*N a un grafo diferente.

Por tanto, el coste requerido del conjunto fijo es al menos
3×95.946.764=287.840.292 bytes. El límite intacto es 268.435.456 y el exceso es
19.404.836. La cota omite los cuerpos mutables, autoridad, raw/result/seal
futuros y checks adicionales; no usa el upper histórico como consumo exacto.
Una ejecución que aborte antes por cuota no aporta un calendario completo ni
contradice esta cota de lecturas requeridas.

Es un incumplimiento de la extensión retenida bajo esas premisas, sin concluir
que todos los paquetes alternativos sean imposibles o que CPU, heap y servicio
real de plataforma resulten inviables. El registro de esta cota tampoco aplica
un rebind: el conjunto exacto vigente ya rechaza una incorporación directa.

## Readers y proyección parcial de metadata

La cuenta se conserva separada para el Input Reader del coordinador y el del
worker. No se juntan, resetean o pagan con Evidence Reader. Los archivos fijos
cumplen file16MiB; 95.946.764 bytes y 632 rutas conocidos quedan bajo unique128MiB
y 4096 paths. Son comprobaciones parciales, sin fit final ni compensación del
exceso de read256MiB. Los checks frescos heredados siguen adicionales. Las
cuotas de salida no se usan como capacidad para fuentes de recursos.

La revisión realiza además una segunda comprobación de metadata: copia sólo
en memoria el modelo histórico de 483.286 bytes y añade a ambos mapas las
146 entradas SHA/path reales congeladas. La serialización completa confirma
16.871 bytes por mapa, 33.742 de incremento y 517.028 finales bajo el supuesto
de conservar iguales todos los demás campos. Quedan 7.260 frente al allowance
histórico 524.288.

El modelo histórico contiene widths de referencia y no se emite como resultado
de captura o atestación. No se generan placeholders nuevos. La autoridad,
registry, certificado/manifest, atestaciones y P09/P10 finales exigen otros
bytes y pins; su fit completo continúa desconocido. El margen parcial no es
una autorización ni sustituye los límites de contexto/launcher/paquete.

Las dieciocho referencias históricas I127 incluyen intérprete, doce archivos
stdlib y cinco registros de extensiones, algunos declarados builtin. Se
mantienen como referencias de aquel manifiesto, sin abrir sus rutas o candidatos
externos, copiarlos al repositorio o llamarlos observaciones frescas de Reader,
implementación cargada o evidencia actual del destino. La presencia o ausencia
de candidatos de archivo tampoco cierra la implementación builtin/nativa.

## Disposición, ciclos y preservación

La selección congelada excluye los archivos I169; la revisión I170 tampoco se
incorpora silenciosamente a ella. Los sellos excluyen su propio hash. La fuente
prohíbe autoridad autopinneada y el certificado excluye su propio hash. Estas
comprobaciones de publicación no prueban la ausencia de ciclos en un grafo
futuro todavía sin finalizar: requiere orden topológico, pins y revisión nueva.
No se reutilizan autoridades históricas o INVALID_CAPTURE/NOT_RUN como evidencia.

E01–E05 abiertas; E06 separado NOT_RUN y sin autorización de ejecución. I122
conserva IMPLEMENTED_NOT_ADMITTED, sin SOURCE_CAPACITY_VERIFIED, propuesta o
captura habilitadas, rebind o autoridad/destino nuevos. D5/H07 de cierre abiertos;
IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1; D1–D4 e
I1–I20/A52 intactos; brechas globales y reales pendientes. I86/I89/I92
INVALID_CAPTURE no se reanudan ni mezclan.

`python3 docs/validation/D5-I170-audit.py`: resultado esperado
PASS_STATIC_SOURCE_ONLY. Comprueba fuentes, Git/JSON, bindings, byte sums,
cuentas por Reader y serialización condicional; preserva 328 archivos publicados
e inputs heredados. No ejecuta el producto, componentes o un calendario Reader.

Unidad de cinco archivos: este documento, dictamen, reconstrucción, auditor y
[sello](../validation/D5-I170-integrity.json). Rollback limitado a los cinco
archivos enumerados en work_unit. El diff supera 400 líneas por evidencia
trazable y auditor autocontenido; el exceso queda informado. Runtime harness
N/A: revisión documental sin cambio runtime. Auditoría antes del stage y tras
commit, push autorizado y comprobación de remoto/árbol limpio. Publicar no admite.

Sólo herramientas documentales Git/JSON/AST/bytes. Sin tests, benchmarks,
schedule, introspección o mediciones de runtime/plataforma. Sin modificar
fuentes, cuotas, reservas, presupuestos, contrato o capture_inputs; sin
inspeccionar ni limpiar dev/run_data/D4. Sin proveedores, credenciales, consumo,
activación, promoción, despliegue o D6.
