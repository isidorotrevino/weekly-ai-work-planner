# I114 — referencias en30 sitios y composición de bytes

Fecha:2026-11-10, Europe/Madrid. **Envolvente de referencias por fuente preparada;
capacidad conjunta NOT_ESTABLISHED**. HEAD sigue siendo
`50c49678568bae2abeefbe5fec0285f26c628283`; este corte es local, sin commit/push.

[Desglose de referencias y anclas](../validation/D5-I114-reference-source-envelope.json) ·
[24 recursos y composición](../validation/D5-I114-joint-resource-envelope.json) ·
[Auditoría documental reproducible](../validation/D5-I114-audit.py) ·
[Sello](../validation/D5-I114-integrity.json).

## Referencias: una cota finita todavía demasiado amplia

Se reutilizan E<=30129 y F=321 de I113, sin rehacer ni ampliar el recuento de
eventos. Para la misma ruta original completa PASS, observación válida y
bindings/MRO pinneados, se deriva **R<=10945598127** mediante los30 sitios activos
I96. Es una envolvente deliberadamente muy suelta, **no una cuota propuesta**,
una medida, un máximo alcanzable o un certificado conjunto. Se mantiene
**R>=19037>16384(I97)**: la representación original sigue bloqueada.

La cuenta acota la demanda de la ruta completa si no se corta antes por refs;
no afirma que el perfil actual pueda observar esa ruta. No usa16384 para acotar
R ni los4096 bytes de fila para limitar witnesses. Los8 sitios inactivos siguen
excluidos. Las condiciones de observación válida no son resultados funcionales.

Las primitivas explicitan constructores K<=E (Store y los FixtureStore DI28
observados), retornos con owner H<=E, llamadas causales C<=E, independent I<=E,
oráculos retenidos V<=E y protocolos P<=E+1. independent añade como máximo un
ORACLES después de recorrer la cadena; sus iteraciones no son nuevas altas.
Los dos ORACLES son las únicas record_sources: Q14<=E. No se añaden CRASHES o
CHILDREN como si fueran fuentes declaradas, ni se eliminan los enlaces ORACLES.

Las altas de owners tienen envolvente A=5E+7=150652: constructor, retorno,
objeto de llamada, proceso/conexión de protocolo y margen fijo DI07. Las
llamadas de metadatos reutilizan el owner ya establecido. Cada frame retiene
cada owner como máximo una vez; se sobreestima su suma con F*A. Q15<=F+F*A
incluye321 constantes y48359292 membresías, sin resets ni descuento por interning.
Q20 cuenta además las asociaciones fuertes, aunque conserven el mismo puntero.

Las declaraciones de dominio D<=K+H+C<=3E=90387 acotan grupos y primeras altas
de witnesses. El tamaño de un grupo se acota por D, sin presuponer que su fila
cabe. Se retienen por separado las autoridades adicionales, el puntero de grupo
y cada copia de witnesses en retained/close/link. Los enlaces son como máximo
C+2V<=3E; sólo los dos enlaces por oracle pueden llevar grupo. El grupo compartido
limita la unión de witnesses, sin fusionar los objetos físicos ni sus autoridades.
Las cotas cuadráticas de Q34/Q36/Q38 dominan esta sobreestimación.

Q19 merece una cuenta distinta: las raíces no acotan subcasos/hilos. El JSON
retiene13 familias de orígenes de context/subcase, con multiplicidades derivadas
de los cuerpos activos. Su suma U<=26E+F+8=783683 incluye begin en321 frames,
addSubTest, emit, declarations, retain, independent, receipt candidates, llamadas,
registro, enlaces, group_for_object y DI07/message. Cada entrada crea como máximo
un S y efectúa como máximo dos consultas de thread; se usa T<=2U, aun cuando la
segunda consulta normal reutiliza el hilo. Las demás claves C/V/P/G/W/L se suman
separadamente. No se infiere una sola identidad de hilo de un solo frame.

Se cuentan también receives/joins que no añaden evento propio: T/R receive
retiene un mensaje por boundary; Drive message tiene una aserción por recv.
M<=2E. T/R finish observa join y exit por separado; Drive conserva cleanup por
spawn, kill_at, dos joins DI14 y hasta dos DI07: X<=4E+4. Las ramas de timeout/
CHILD_ALIVE que lanzan error no pertenecen a la ruta original completa PASS.
La instrumentación parental no observa Store del hijo. Los sitios fijos DI07,
DI28 y late conservan I96/I97; no se reescriben sus sellos.

Cada página del manifiesto es no vacía: Q16<=E por fuente, sin presuponer32 páginas.
La cota32 de I96 sigue siendo válida **para un paquete admitido**; la cota nueva
evita usar ese guard como prueba de que toda la demanda cabe. El desglose conserva
q_i, fórmula, unidades y ancla por sitio; los subtotales son cargos, no invocaciones.

## Bytes: condición de paginación y Reader separados

El PageSink activo es el de **typed**, no una clase paged en el MRO. Su overhead
por página se sobreestima con256 bytes; el encabezado construido con extremos
monótonos de E ocupa189 bytes incluido el contenedor de eventos. Una página
no final se vuelca cuando el siguiente evento no cabe. Si todos los eventos
codifican como máximo B bytes, sus chunks/comas previos superan
`2097152-256-(B+1)`. Por tanto:

`pages <= floor(E*(B+1)/(2097152-256-(B+1)))+1`

`pages_bytes <= E*(B+1)+256*pages`

Con **B=4096, todavía no probado para los valores reales**, la envolvente es
**59 páginas /123453617 bytes**, frente a32/67108864. Esto no demuestra un exceso
real: demuestra que ese argumento uniforme aún no certifica capacidad. No se
propone subir páginas o bytes. Como objetivo suficiente de refinamiento, probar
B<=2223 daría32 páginas/67015088 bytes con esta fórmula;2223 es un objetivo de
análisis, no una cuota, truncado o modificación de evidencia. También puede
refinarse la suma de tamaños heterogéneos sin exigir ese máximo uniforme.

La matriz actualiza los24 recursos sin sustituir incógnitas por0. eventos_test,
events_campaign y frames reutilizan I113. Valor/operandos, profundidad, strings,
filas, raw, sidecar, contexto y launcher siguen necesitando envolventes de la
carga semántica real. El máximo32MiB de fixture no prueba operand<=16MiB.
El tamaño pequeño de un digest tampoco prueba la entrada ni sus auxiliares.

El conjunto original de input Reader se comprueba por sus292 pins más autoridad:
293 paths,63104330 bytes únicos y archivo máximo9755833 bytes, menor que16MiB.
El calendario I96 conserva160864585 bytes leídos en el worker normal original,
incluidos checks repetidos late, bajo256MiB. Estos documentos nuevos no se
presentan como inputs de una captura futura; ese ámbito deberá recalcularse.

Para evidence Reader original, si raw/sidecar/páginas ya caben en sus techos:

`unique = raw + sidecar + pages + 36 <= 92274724`

`read = 2*(raw+sidecar) + 3*pages + 36 <= 251658276`

Es el calendario I96 normal, con sus exclusiones; no es evidencia de que el
paquete real cumpla tamaños. Contexto y launcher siguen siendo miembros del
paquete, aunque ese Reader no los lea. Manteniendo todos los techos individuales,
37 miembros suman como máximo117440548 bytes, margen4060 frente a117444608.
No se unen ledgers, no se resetean antes/después/autoridad y no se traslada ese
calendario a un perfil nuevo. Ampliar páginas obligaría a reevaluar también Reader
y paquete; un límite aislado no es una solución revisada.

## Próximo corte y puertas conservadas

Antes de proponer implementación queda refinar las multiplicidades por raíz y
el tamaño de sus valores/proyecciones, filas/tablas, raw/sidecar/contexto/launcher;
reemplazar la envolvente cuadrática por fanout realmente justificable y componer
todas las cuotas y calendarios. La cifra superior grande no justifica asignarla
como cuota. No hay todavía contrato/perfil/namespace/registro nuevos aprobables
con cifras conjuntas: no se solicita autorización prematura ni se implementa.
El siguiente corte documental libre será I115, si no existe al continuar.

Sólo tras preparar el expediente concreto proceden sus decisiones separadas:
contrato/perfil/implementación y componentes; después captura funcional nueva
con pins/destino propios321/12 bajo900s; después IR03, suficiencia/aceptación global
y publicación. La auditoría de este corte verifica hashes, anclas AST y aritmética,
no ejecuta componentes ni demuestra automáticamente las premisas semánticas.

I86/I89/I92 siguen INVALID_CAPTURE, sin suma/reanudación; IR03 NOT_READY. Se
conservan P0;83 SUPPORTS_BOUNDED/1 PARTIAL, UI04.1 parcial, D1–D4 cerrados e
I1–I20/A52 aceptado. D5/H07/G01–G07 y GI globales siguen abiertos. GI06/12/18/24/
30/36/42 requieren sus evidencias reales o decisiones humanas, no otro hito parcial.
Sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción,
despliegue, SQL/Java/Docker nuevos, D6 o inspección/limpieza operativa dev/run_data/D4.
No se deduce persistencia/recuperación integrada de PASS aislados o exit0.
