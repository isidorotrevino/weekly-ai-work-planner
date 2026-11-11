# I123 — memoria y CPU transitorias de I122

Fecha: 2026-11-11 (Europe/Madrid). Base:
`50c49678568bae2abeefbe5fec0285f26c628283`.

**La candidata I122 conserva la reparación integrada de los30 sitios, pero no
queda habilitada para captura.** Esta revisión cuantifica el coste estructural
por clonación y las páginas pendientes, y deja una condición explícita para la
capacidad global. No certifica RAM del proceso ni los900 segundos. El certificado
I122 sigue IMPLEMENTED_NOT_ADMITTED; no se modifican fuentes, cuotas, registro,
contrato ni pins anteriores. Los diez componentes siguen NOT_RUN.

## Qué se copia y qué se comparte

El censo AST del JSON adjunto recoge62 llamadas raíz de clone_metadata por
_fork:22 FIELDS,24 atributos causales,14 atributos de Pages y rows/states de
bindings. Un memo compartido conserva alias dentro de una fase; no reutiliza
copias entre fases. El recorrido incluye calls, domains, objects, threads,
subobjects, stacks, group_keys y object_identities, aunque no sean tablas del
sidecar. Incluye también spec y contract fijos. Las copias superficiales de los
__dict__ del Recorder/Projector/bindings son otro coste y no convierten sus
atributos enteros en grafos copiados recursivamente.

Sólo se expanden dict/list/tuple/set/frozenset exactos. Los originales retenidos
por record_refs, record_baselines, oracle_guards y causal_sources son opacos;
los objetos de producto/clases/módulos/weakrefs son hojas. Los bytes/str tampoco
se duplican mediante clone_metadata. Esto preserva CP03 de I120: la cota del
operando original no se multiplica por el número de drafts. Sí se crean las
claves enteras id del memo, tablas, contenedores, slots, generadores y marcos de
recorrido. No se trata de una estimación de RSS ni de bytes Python serializados.

## Envolvente estructural por lote de clonación

El modelo usa la campaña fuente321 raíces/12 grupos y sus30129 eventos, no el
límite131072 como demanda. Reutiliza5190 owners,1718 subcases,6615 grupos,
9285 membresías físicas,997 originales y46936 claves causales. No rebaja ni
fusiona witnesses. Es conservador: cuenta de nuevo aliases y algunas tablas.

| Bloque JSON de referencia | Bytes usados como mayorante topológico |
| --- | ---: |
| Sidecar condicional de I117 | 30.996.862 |
| calls internos:30129*4096 | 123.408.384 |
| domains internos:9285*512 | 4.753.920 |
| Cinco filas parentales privadas:5*4096 | 20.480 |
| spec/contract y dos limits fijos | 58.365 |
| Manifest:32*512 | 16.384 |
| Total B | **159.254.395** |

Los4096 por call requieren las formas proyectadas de la campaña válida; el
check row_budget después de construir una fila no protege por sí solo una
asignación arbitraria previa. La fila cerrada y su prefijo abierto se consideran
dentro de ese modelo. Un domain contiene identidad/contexto con UUIDs, refs y
role, sin estado/chain originales. Su clave tuple se cuenta aparte. Los JSON
fijos se miden documentalmente, sin cargar la candidata. El censo incluye otros
671170 elementos auxiliares de contenedor/slot, con fórmulas por raíz en el JSON.
La reserva4096 para raíces pequeñas/bindings es una premisa conservadora del
modelo, no una medición ni una asignación de memoria autorizada.

Para JSON compacto, B bytes pagan como máximo B contenedores y2B ocurrencias
hijas, incluyendo claves de dict. Añadiendo auxiliares y62 llamadas raíz:

- C, contenedores/memo entries por lote: **<=159925565**.
- A, ocurrencias hijas: **<=319179960**.
- V, entradas en clone_metadata: **<=319180022**.
- Operaciones lógicas sobre memo: **<=798285609**; consultas a opaque:<=V.
- Construcción de opaque: **<=1998 intentos de inserción** por lote.

Son cotas deliberadamente holgadas y **condicionales a las formas del ledger y
al grafo de metadata sin ciclos por tuple/frozenset**. No significan que la
campaña asigne esas cantidades, ni que haya159 millones de referencias
contabilizadas. Tampoco son una prueba completa de memoria o CPU del proceso.
Los accesos a dict/set no tienen coste constante garantizado: colisiones,
comparación de claves y crecimiento de tablas requieren un modelo aparte.

## Vida de las copias y memoria global

_atomic conserva draft y su memo mientras escribe fuera del lock. Otra fase
puede publicar durante esa E/S: un lock único no implica una sola generación
retenida. Los guards de flush permiten como máximo32 páginas publicadas y
64MiB de cuerpos de páginas pendientes, compartidos por las referencias que
apuntan al mismo body. Eso limita a32 fases distintas detenidas con escrituras
pendientes; no limita todos los drafts/snapshots/retornos del proceso.

El memo conserva también la lista de chunks clonada antes de flush, aunque
Pages.chunks se sustituya por[]. Por tanto, no basta con añadir sólo el buffer
actual de2MiB: quedan chunks históricos retenidos. En la campaña válida, la suma
de todos los payloads de chunks distintos no supera64MiB, porque cada evento se
codifica una vez y su payload pertenece a las páginas del total limitado. Los
clones comparten esos bytes inmutables. Cuerpos y chunks distintos suman así
**hasta128MiB de payload**, antes de temporales del join y concatenaciones de
flush y del overhead de objetos. Este número tampoco es RAM total del proceso. Las codificaciones usan json.dumps(...).encode(...):
pueden coexistir texto Unicode y bytes. El guard de tamaño se aplica después de
codificar; page_bytes y peak_page_buffer_bytes no son techos de heap/RSS.
Las páginas, sus objetos Python, los elementos del manifest y las tablas
requieren costes distintos; los64MiB no incluyen todo ello.

Sea F el número total de _fork vivos invocados durante la campaña y S el número
de lotes de snapshot independientes del proxy. Una cota conservadora que evita
suponer liberación inmediata es retener todos los lotes:

```
topología <= (1+F+S)*(C+A) + O(opaque+F+S)
heap solicitado <= (1+F+S)*(h*C+p*A+m*C+w+L)
                  + payload de páginas + temporales de codificación
```

L recoge las hojas escalares de metadata retenidas por generación, aunque no
se copien al clonar; no incluye operandos originales opacos.
h/p/m/w/L deben justificarse para el intérprete exacto y su política de crecimiento,
profundidad y marcos. No se asignan valores de bytes arbitrarios ni se presenta
esta fórmula como un techo residente. F/S no están cerrados por esta revisión:
refs333109 o eventos30129 no los sustituyen. Hay fases de cargo cero, prepare,
lecturas puras y snapshots de atributos/tablas. Un retorno puede retener una
subestructura anterior. Los fallos pueden retener tracebacks/ciclos y diferir
liberación hasta GC; la cota de32 páginas no resuelve esas vidas. La memoria
original, stacks nativos, runtime, allocator, fragmentación y OS quedan fuera.

## CPU y900 segundos

El trabajo añadido de clonación queda expresado como:

```
entradas de clone_metadata <= (F+S)*319180022
operaciones lógicas de memo <= (F+S)*798285609
intentos de inserción en opaque <= (F+S)*1998
```

F no es el número de sitios lógicos30. Los callbacks anidados que reciben un
draft usan el fast path y no cuentan otro _fork. Los snapshots de lectura tienen
memo nuevo y sí cuentan otro lote. Incluso sin duplicar operandos originales,
las copias completas suman prefijos: O(F*N_final), potencialmente cuadrático si
N crece con F. Al coste de copia se agregan proyecciones/digests, JSON/hash,
sort, búsquedas lineales de identidad/domains y link_receipt_candidates sobre
calls, publicación, destrucción/GC, lecturas frescas y E/S/locks.

Ninguna frecuencia mínima de servicio ni margen de tiempo del producto se ha
justificado. El cociente trabajo/900 sería una exigencia de rendimiento, no una
prueba de cumplirla. El timeout del coordinador/Condition limita espera o
invalida una ejecución futura; no prueba que la campaña exitosa termine dentro
del plazo. Por ello no se declara una cota de segundos ni un PASS experimental.

## Decisión de capacidad y siguiente obligación concreta

La propuesta revisable es mantener I122 como **IMPLEMENTED_NOT_ADMITTED** y
separar tres obligaciones documentales verificables:

1. R123-01: contar F/S desde el grafo de invocaciones original y de observación,
   incluidos caminos de cargo cero, snapshots y finalización; sin presupuestos
   por hilo, reset ni sustitución por límites configurados.
2. R123-02: cerrar bytes solicitados y vidas de generaciones para normal/rechazo,
   con ABI/allocator fijados, o reducir la copia completa conservando atomicidad.
   No basta con el máximo de páginas ni con el tamaño final del sidecar.
3. R123-03: cerrar trabajo ajeno a clone y coste de hash/scan/sort/encoding, y una
   condición sustentada de servicio/margen para900 segundos. La cota topológica
   holgada por sí sola no demuestra inviabilidad ni capacidad suficiente.

La validación runtime de atomicidad y los diez componentes siguen pendientes.
CP03 original permanece resuelto; CP07 de admisión real, autoridad nueva y
componentes reales siguen pendientes. Los archivos I123 no se agregan a los
inputs admitidos ni se falsifica un certificado de capacidad completo.

El plan Reader I122 sigue siendo266337791/268435456 bytes, margen2097665, para
sus inputs actuales. Si I123 se incorpora después, deben rehacerse pins y U
sobre bytes finales y el grafo exacto de lecturas. Sólo si se conserva aquel
grafo de tres pasadas, incorporar N bytes añade3*N; no se extiende el margen a
memoria, CPU ni artefactos futuros por omisión.

## Auditoría y conservación

`python3 docs/validation/D5-I123-audit.py` sólo analiza AST, JSON, tamaños, hashes
y aritmética. Verifica el censo/anclajes, fórmulas, cuotas/certificado intactos,
92 archivos previos conservados y el conjunto exacto de archivos nuevos. Su
PASS_STATIC_SOURCE_ONLY no importa, compila ni ejecuta fuentes candidatas,
producto o componentes. Tampoco valida el ledger condicional como ejecución.

P0 permanece83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 mantienen
aceptación. D5/H07/G01–G07 y GI globales siguen abiertos; GI06/12/18/24/30/36/42
humanos/reales pendientes. IR03 NOT_READY. I86/I89/I92 siguen INVALID_CAPTURE,
sin reanudación ni combinación. Sin autoridad/destino nuevo, cuotas aplicadas,
consumo, reservas operativas, activación, promoción, despliegue, D6 ni commit/push.
No se inspecciona ni limpia dev/run_data/D4.
