# I133 — P01 RESOURCE-SCOPE preparado para PFC126-CANDIDATE-03/I122

Fecha: 2026-11-12, Europe/Madrid. Base publicada:
`9268d2fd095be9437e44d45746579260b9df2b80`.

**Se produce P01 en la ruta y schema previstos por I132.** Fija bytes, raíces,
métricas, procesos y marcadores para futuras pruebas. Está preparado para
revisión documental independiente, todavía no aceptado por un revisor
independiente. No es evidencia de capacidad, plataforma o tiempo, ni habilita
PJC115-R2/I122. Se mantiene IMPLEMENTED_NOT_ADMITTED y la no admisión.

[P01 RESOURCE-SCOPE](../validation/D5-PFC126-03-RESOURCE-SCOPE.json) ·
[Revisión de preparación](../validation/D5-I133-P01-preparation-review.json) ·
[Auditoría](../validation/D5-I133-audit.py) ·
[Integridad](../validation/D5-I133-integrity.json).

## Identidad y fuente de verdad

P01 usa `d5.pfc126-03.resource-scope.v1`, el schema del paquete P01 de I132.
Vincula por hash PFC126-CANDIDATE-03, I122-CANDIDATE-01, el plan/registro y sus
fuentes. El productor queda identificado como el asistente que prepara I133,
con autoridad del usuario para preparar documentos; no se atribuye autoridad
operadora de recursos. El rol revisor está indicado, con identidad/aceptación
pendientes, sin firma o revisión independiente inventada.

La vigencia de este ámbito depende de los hashes exactos y las condiciones
fuente declaradas. No es un intervalo de validez atestado de una plataforma.
Cambiar fuentes, contrato, rutas, tipos, imports/hooks o supuestos obliga a una
nueva revisión de ámbito, no a transferir silenciosamente las cotas.

## Pins de I122 y originales

Se separan los seis archivos sellados de I122: tres fuentes runtime
capture/atomic/worker, dos fuentes de componentes futuros NOT_RUN y README.
Ninguno se importa, compila o ejecuta durante la preparación.

Los imports locales se recorren por AST, incluidas ramas/imports internos y el
import relativo de atomic, sin ejecutar módulos. El conjunto protector resultante
contiene ocho archivos del observador y helpers heredados, con aristas y hashes.
Es un **superconjunto estático de fuentes locales**, no un manifiesto de módulos
efectivamente cargados. La selección dinámica/stdlib/frozen/builtin/extensiones
sigue pendiente de P02.

Se materializa documentalmente el registro heredado de I122 verificando el SHA
de su base y aplicando sus overrides como datos JSON. No se instancia Reader,
Recorder, runner o producto. Se conservan los79 inputs registrados del runner,
71 Python, sin confundir «registrado» con «ejecutado». El grafo original heredado
contiene33 registros de módulos y32 archivos fuente únicos, todos protegidos por
los inputs registrados. No se fusionan por ello objetos/witnesses físicos.

Los321 bindings de método conservan ID, símbolo, archivo/hash, intervalo y
factory_args. P01 añade un hash AST del FunctionDef de cada intervalo exacto;
varios IDs pueden compartir una definición/factory sin perder sus identidades.
Son expectativas fuente, no atestación de binding runtime. El runner queda
fijado como testing.D5.run_relational_durable_lab, función main, sin ejecutarlo.

## Aplicabilidad321 raíces/12 grupos

Se conserva la lista completa de IDs y el hash heredado de IDs ordenados, y se
reconcilia su reparto:

| Grupo | Raíces |
| --- | ---: |
| test_durable_integration | 48 |
| test_durable_relational | 40 |
| test_incremental_capture | 30 |
| test_local_preview | 17 |
| test_offline_integration | 35 |
| test_plane_reconciliation | 41 |
| test_postgres_adapter | 3 |
| test_profiles_quotas | 38 |
| test_register_comparison | 16 |
| test_register_compat | 11 |
| test_relational_batch | 38 |
| test_review_report | 4 |
| Total | **321** |

Los modos fuente88 T/R,30 Drive y203 sólo aserciones/contextos permanecen
separados; el inventario causal118 no se presenta como toda la campaña.
Se heredan íntegramente las precondiciones I115 y el ámbito I124: ruta original
completa declarada, datos y formas acotadas, fuentes/bindings fijos y observaciones
válidas. Las excepciones originales esperadas no se omiten; un cambio inesperado
de control de flujo o tipos hostiles no queda cubierto por extrapolación.

F<=52018, S<=1759 y53778 generaciones se vinculan como resultados fuente
condicionales, no runtime PASS ni ajuste a recursos. No se añade presupuesto por
hilo ni descuento al cerrar frames. Las fuentes de los30 sitios se conservan;
la validación runtime de atomicidad sigue pendiente y separada.

## Procesos y métricas

| Dominio | Inclusión declarada |
| --- | --- |
| Heap del worker | Todas las asignaciones dinámicas Python/nativas:originales, observador y runtime,11 propietarios |
| Heap coordinador/hijos | Cuentas por proceso separadas; no se consideran incluidas en11/12GiB del worker |
| Tiempo extremo a extremo | Contribuciones pertinentes del coordinador, worker, hijos y servicio en C01–C10 |
| Stack/RSS/otros mappings | Dominios separados; no se llaman heap por omisión |
| Plataforma agregada | Sin afirmación de RAM/capacidad total del host |

El heap solicitado se define por tamaños pedidos de bloques dinámicos vivos,
con payload/objetos/buffers correspondientes. El comprometido del allocator
incluye almacenamiento de backing, metadatos y memoria retenida/desperdiciada:
P02/H11 deben vincular y probar el backend exacto y su cobertura. No se iguala
al espacio virtual reservado o a RSS. Estas definiciones no se pueden cambiar
posteriormente para fingir ajuste.

Los11GiB solicitados,12GiB comprometidos,832MiB de reserva y1GiB H11 son
presupuestos candidatos preservados. Las cotas completas y capacidad disponible
siguen null; originales opacos significa que no se copian, no que no ocupen
memoria. El heap debe cubrir prefixes de rechazo del observador/tracebacks dentro
de la ruta fijada, sin convertirlo en una garantía para fallos arbitrarios.

## Marcadores y políticas intactos

P01 copia los marcadores y la calificación de éxito de la candidata03:

```
t0 <= tR <= tW <= tF
Tpre=tR-t0; Tworker=tW-tR; Tpost=tF-tW
```

tW es el retorno exacto True de la llamada única wait_worker del coordinador.
Exit físico o validación posterior no lo sustituyen. La validación posterior
califica el éxito sin mover tW; False/excepción o captura/finalización inválida
no establecen la afirmación de éxito. Se conserva la latencia de observación
hasta tW y el finally completo hasta tF. No se recogen timestamps, no se
instrumenta ni se atesta un reloj/servicio.

Los presupuestos60/750/60+30 y600/90/60 permanecen candidatos. La afirmación900
es sólo para éxito cualificado extremo a extremo, no para todo cleanup fallido;
process.wait900 sigue siendo su watchdog local. Las24 cuotas, asignaciones0 de
reservas, política de costes antes de tR, no ejecución y no admisión se conservan.

## Estado de P01 y de los paquetes siguientes

P01 pasa de destino futuro a artefacto **preparado para revisión**. La revisión
I133 registra esa preparación y la aceptación independiente pendiente. Los
otros19 destinos P02–P10 siguen sin crear y no se inician automáticamente.
I132 se mantiene byte a byte como plan histórico; sus campos de «no producido»
describen aquel incremento, no se reescriben para simular una aceptación.

P02/P03 siguen sin evidencia externa; P01 sólo referencia el runtime observado
heredado y el manifiesto histórico I127. No se vuelve a muestrear el host ni se
asignan operadores o intervalos de garantía. E01–E05 continúan sin cierre y E06
permanece separado, componentes NOT_RUN. No se emite SOURCE_CAPACITY_VERIFIED,
autoridad/destino, captura o rebind de inputs. Una incorporación futura a admisión
real exigiría revisar hashes, schemas y calendario Reader sobre bytes finales.

`python3 docs/validation/D5-I133-audit.py` verifica datos, hashes, imports AST,
321 intervalos, grupos, métricas, marcadores y políticas. Conserva143 archivos
publicados anteriormente. PASS_STATIC_SOURCE_ONLY es preparación/coherencia
estática, no aceptación independiente o prueba de recursos. El auditor funciona
antes de stage y después del commit; sólo usa helpers estándar y Git, sin
importar/ejecutar producto o componentes. Se hace commit y push de todos los
cambios I133; el resultado real se comprueba por Git, sin hashes circulares.

P0 conserva83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados.
D5/H07 y brechas/obligaciones reales pendientes; IR03 NOT_READY. I86/I89/I92
INVALID_CAPTURE sin reanudación/mezcla. Sin proveedores/credenciales, consumo,
reservas operativas, activación, promoción, despliegue o D6. No se inspecciona ni
limpia dev/run_data/D4.
