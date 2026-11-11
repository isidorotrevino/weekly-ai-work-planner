# I124 — conteos globales, vidas y decisión de recursos de I122

Fecha: 2026-11-11, Europe/Madrid. Base:
`50c49678568bae2abeefbe5fec0285f26c628283`.

**Se cierran los conteos globales de oportunidades de clonación y una envolvente
finita de sus vidas. No se puede habilitar PJC115-R2 con una certificación de
recursos completa a partir de estas fuentes.** La cota de trabajo del clonador
queda numérica; no se convierte en segundos ni en RAM disponible. La decisión
es conservar I122 IMPLEMENTED_NOT_ADMITTED. Los diez componentes permanecen
NOT_RUN y CP07 de admisión real sigue pendiente. No se cambian fuentes ni cuotas.

El JSON de prueba contiene321 filas, una por raíz,115 accesos/dispatches AST y
pins del grafo de33 módulos heredado. El JSON de decisión distingue conteo,
almacenamiento de builtins, memoria total y tiempo; no declara un PASS de los
recursos completos por haber cerrado una fórmula parcial.

## R123-01: F y S ya no son incógnitas

F cuenta entradas en _fork; S cuenta lotes independientes de clone_metadata de
lectura. Son cotas superiores de oportunidades, incluidas las que fallan antes
de completarse; no predicciones del número exacto que se ejecutaría.

| Familia de fases | Cota global |
| --- | ---: |
| Una fase que publica por oportunidad de evento | 30.129 |
| PRECALL compañero de perform/boundary | 11.945 |
| prepare de bindings, incluso sin binding nuevo:2*A | 6.652 |
| subcase anterior al callback addSubTest:L−3*321 | 197 |
| recv/message sin evento propio | 934 |
| join/exit sin evento propio, incluido cleanup | 1.438 |
| started parental por oportunidad de proceso, aun con preview=None | 718 |
| DI07:pipe_return, preview, bind | 3 |
| Inicialización de binding y sello final | 2 |
| **F** | **52.018** |

La columna de eventos se usa para contar oportunidades de llamada observada,
no como contador runtime tras un fallo. Cada constructor/retorno/excepción,
start/stop, resultado y emisión explícita tiene una sola fase de publicación.
El wrapper boundary y el de perform pueden añadir una PRECALL. Retorno y
excepción son ramas alternativas. La suma11945 procede del primitivo C de I115,
no de la cuota de referencias ni de los30 sitios lógicos.

La lista de operandos del wrapper de aserción sólo se evalúa a profundidad cero.
Los helpers admitidos tienen como máximo dos argumentos distintos de self/msg;
assertRaises/Regex omiten esa lista. Así,2*A cubre incluso prepares sin cargo.
El addsub adicional no se confunde con la fase de resultado que viene después.
M/X de I115 cuentan recv/join que no emiten evento propio. P=H+DI07 sobreestima
los procesos porque H incluye también receive/finish; cubre un Pipe/start por
lanzamiento. En el grafo original efectivo los otros tests concurrentes usan
Thread, que no entra en BaseProcess.start.

El detalle que faltaba era started: el wrapper parental lo llama también cuando
selected es falso. Se cuentan las718 oportunidades globales, no sólo DI07.
pipe_return/preview/bind sí se limitan a la selección directa DI07, una vez cada
uno. Los checks Reader no crean nuevos drafts por sí mismos.

| Familia de snapshots puros vivos | Cota |
| --- | ---: |
| selected en start de cada raíz | 321 |
| selected en cada Pipe | 718 |
| selected en cada BaseProcess.start | 718 |
| check_retained y tables de finish | 2 |
| **S** | **1.759** |

No se cuentan como S las consultas dentro de una fase: allí causal es el estado
crudo del draft, no CausalProxy. Los métodos antiguos start/stop/finish y wrappers
reemplazados no se suman otra vez. Las mutaciones anidadas sobre un draft usan
el fast path y no vuelven a llamar _fork. El censo AST conserva también las
referencias de métodos heredados para que estas exclusiones por MRO se revisen
sobre los bytes exactos.

Por tanto, **F+S<=53777**. Se mantiene el ámbito heredado:321 raíces/12 grupos,
ruta original completa con observaciones de forma acotada, bindings/imports
fijados, sin nuevos hooks ni cambio del control de flujo original. Un fallo
inesperado que cambie esa ruta exige reevaluación; no se concede una garantía
universal para programas Python arbitrarios.

## R123-02: vidas cerradas sin esperar GC

Se retienen conservadoramente todos los53777 lotes hasta el final y un grafo
inicial adicional: **53778 generaciones de metadata**. Esto incluye retornos que
conservan subestructuras antiguas, snapshots que escapan al caller/sidecar,
metadata/memo en E/S pendiente y ciclos/tracebacks de una clonación rechazada.
Un fork parcial se cuenta como uno completo. Los rechazos son un subconjunto
de las oportunidades F; no se añaden F lotes por segunda vez. No se presupone
que el refcount o GC liberen una generación antes de que comience otra.

La prueba de vidas ya no necesita un número desconocido de lotes simultáneos:

```
contenedores de metadata <= 53778*159925565 = 8600477034570
contenedores + ocurrencias hijas <= 53778*479105525 = 25765336923450
```

Son unidades topológicas conservadoras de I123; no bytes ni referencias
contabilizadas. Los memos, marcos y temporales se tratan separadamente. El
máximo32 sólo limita las fases pendientes con páginas, no todo el observador.
La suma de cuerpos pendientes<=64MiB y de chunks históricos distintos<=64MiB
se conserva: **128MiB de payload**, más objetos y temporales. Se incluyen los
chunks que siguen alcanzables desde _memo después de resetear Pages.chunks.

Se concreta además un modelo de almacenamiento **para la parte de builtins del
clonador** en CPython3.14.4 con GIL y punteros de8 bytes. La introspección usada
es únicamente metadata del intérprete y tamaños declarados de tipos; no importa
la candidata ni crea o ejecuta un componente suyo. El modelo usa márgenes por
header/slot/memo/id y crecimiento; no modifica un límite de producto:

```
H = 1024*C + 512*A + 512*C + 64*V + 1024 + 512*1998
  = 429494352768 bytes por lote
(F+S)*H = 23096917808804736 bytes solicitados en el modelo global
```

C/A/V son159925565/319179960/319180022 de I123. Los coeficientes sobrecuentan
buffers de construcción y crecimiento, claves id y el set opaque. Se fija también path/SHA/tamaño del binario local
del intérprete, sin ejecutarlo como programa objetivo; identificarlo no atestigua
su equivalencia con las fuentes upstream. Los tipos
locales observados son dict48, list40, tuple32+8/elemento, set/frozenset200 e
int24+4/dígito, antes de datos externos. El modelo de crecimiento se apoya en
las fuentes primarias versionadas de
[list](https://raw.githubusercontent.com/python/cpython/v3.14.4/Objects/listobject.c),
[dict](https://raw.githubusercontent.com/python/cpython/v3.14.4/Objects/dictobject.c)
y [set](https://raw.githubusercontent.com/python/cpython/v3.14.4/Objects/setobject.c).
Una lista fresca se cubre con capacidad2*n+8; para dict/set frescos sin borrados
se sobrecuentan tablas y sus reemplazos mediante los márgenes por slot.

**Ese resultado no es una cota completa de heap/RSS ni una necesidad real de
23petabytes.** Es un mayorante muy holgado de una parte de las asignaciones bajo
un modelo upstream, sin atestación de equivalencia del binario distribuido.
Faltan marcos Python/C, wrappers fuera del grafo, hojas nuevas de metadata,
proyecciones, JSON/Unicode, runtime, allocator/fragmentación, originales y OS.
Conservar todos los lotes evita una suposición sobre GC, pero no convierte un
modelo parcial de almacenamiento en un certificado de memoria de proceso.
Tampoco se demuestra inviabilidad física de I122 a partir de ese mayorante.

## R123-03: trabajo numérico;900s no demostrados

La sustitución de los conteos globales produce:

| Trabajo del clonador en toda la campaña | Cota |
| --- | ---: |
| Entradas en clone_metadata | 17.164.544.043.094 |
| Operaciones lógicas sobre memo | 42.929.405.195.193 |
| Intentos de inserción en opaque | 107.446.446 |

Se agrega un modelo conservador de colisiones, sin suponer lookup constante:
capacidad<=3832860192 slots,13 rondas de perturbación de64 bits,10 oportunidades
de sondeo lineal y65 etapas por operación para incluir crecimientos. Resulta
un techo abstracto de **192478912238762047131262250 inspecciones de sondeo**.
La comparación de claves builtin planas se sobrecuenta con524288 unidades-byte
por sondeo. Son modelos de trabajo, no instrucciones de máquina ni tiempos;
las reglas de probing se contrastaron con las fuentes dict/set enlazadas.
No se incorporan claves con hooks arbitrarios o mutaciones concurrentes.

La CPU total sigue incluyendo proyecciones/digests, codificación/hash/sort,
búsquedas lineales y link_receipt_candidates, destrucción/GC, Reader, E/S y
runtime. No hay una cota WCET/servicio de plataforma que convierta ese trabajo
en segundos y permita sumar el margen del producto. El watchdog900 y wait20
invalidan una ejecución que se demora; no prueban que la ruta exitosa termine.
Por tanto, **no se puede cerrar afirmativamente la admisión de tiempo dentro del
alcance actual**. trabajo/900 sólo fijaría una exigencia de servicio, no sería
prueba de disponer de él. No se ejecuta un benchmark para rellenar esa carencia.

## Decisión concreta de admisión

- R123-01: cerrado el conteo fuente F/S, con321 filas recalculables.
- R123-02: cerradas las vidas mediante retención total y concretado el modelo
  parcial de almacenamiento; capacidad completa de heap/RSS no demostrada.
- R123-03: cerrado el trabajo abstracto del núcleo, incluido modelo de
  colisiones; tiempo de CPU/campaña completo no demostrado.

**La habilitación solicitada no se declara.** Una revisión afirmativa necesitaría
un modelo completo para runtime/plataforma exactos, o una implementación que
reduzca las copias y vincule su prueba, además de evidencia de componentes y
CP07. Esta revisión no traslada nuevamente F/S a una obligación futura: sus
cifras y sus vidas quedan resueltas. Sí identifica qué afirmaciones de capacidad
no pueden derivarse de ellas.

CP03 original se conserva, los30 sitios fuente siguen integrados y los diez
componentes permanecen NOT_RUN. El certificado I122 permanece idéntico. Los
archivos I123/I124 no se insertan silenciosamente en capture_inputs: el plan
Reader vigente conserva266337791 bytes, límite268435456 y margen2097665 sólo
para su grafo original. Cualquier incorporación futura debe recalcular pins,
metadatos y lecturas finales. La auditoría muestra aparte el coste hipotético
de añadir los cinco archivos I124 con el mismo calendario3x; no los admite.

## Verificación y límites conservados

`python3 docs/validation/D5-I124-audit.py` verifica AST,321 sumas, MRO/anclajes,
pins, fórmulas globales, flags de admisión y conservación de97 archivos previos.
No importa, compila ni ejecuta producto/candidata/componentes. Su resultado es
PASS_STATIC_SOURCE_ONLY, no PASS de memoria/CPU o atomicidad runtime.

P0 conserva83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 conservan
aceptación. D5/H07/G01–G07 y GI globales abiertos; GI06/12/18/24/30/36/42 reales
pendientes; IR03 NOT_READY. I86/I89/I92 siguen INVALID_CAPTURE, sin combinarse ni
reanudarse. Sin autoridad/destino, cuotas activas, proveedores/credenciales,
consumo, reservas operativas, activación, promoción, despliegue, D6 ni commit/push.
No se inspecciona ni limpia dev/run_data/D4.
