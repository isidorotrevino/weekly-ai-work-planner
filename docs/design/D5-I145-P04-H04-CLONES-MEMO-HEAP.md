# I145 — H04 preparado sin cota completa ni ajuste a 6 GiB

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`f245a595125891774cf58c1aa9ecc05e99ea6ecb`.

**P04-H04 queda preparado como expediente de evidencia insuficiente.** Conserva
los conteos fuente y el modelo condicional heredados, con un registro aritmético
y requisitos de asignación/vidas. No hay upper completo H04 ni ajuste verificado
a 6442450944 bytes (6 GiB). E02 sigue abierta y PFC126-CANDIDATE-03/I122/PJC115-R2
mantienen la no admisión. No se cambia I122 para acomodarlo al presupuesto.

## Ruta de comprobación

1. Leer los nueve campos y el dictamen del [expediente H04](../validation/D5-PFC126-03-E02-H04.json).
2. Contrastar el registro aritmético, trece proyecciones y anclas en la [revisión de preparación](../validation/D5-I145-P04-H04-preparation-review.json) y su output vinculado.
3. Ejecutar sólo el [auditor documental](../validation/D5-I145-audit.py): `python3 docs/validation/D5-I145-audit.py`.

Dos campos son definiciones documentales; siete siguen insuficientes. P01
independiente/P02 exacto continúan pendientes. P03 disponibilidad y H01–H03 no
sustituyen una derivación H04. El productor es el asistente del chat, sin autoridad
de custodio o aceptación independiente. Sólo se revisan fuentes/registros
vinculados, sin contactos, muestreo actual o afirmación de ausencia global.

## Lotes clonados y generación inicial son magnitudes distintas

Se preservan sin cambios I123/I124/I125 y candidata03. Los conteos cerrados de
I124 son oportunidades fuente bajo P01, sin convertirlos en mediciones:

| Magnitud | Valor y alcance |
| --- | --- |
| Upper F | 52018 oportunidades de fork live, incluidos IO y rechazos aplicables |
| Upper S | 1759 lotes independientes de snapshot por proxy |
| Upper N = F + S | 53777 lotes clonados |
| Upper G = 1 + F + S | 53778 generaciones de metadata, incluida la inicial |
| IO pendiente ≤32 | Subconjunto de F, sin sumar otros 32 lotes al total |
| Fork rechazado/parcial | Se carga conservadoramente como lote completo dentro de F, sin otro F adicional |

Las rutas conservan todos los lotes y subestructuras escapadas hasta el final.
No se sustituyen por 33 generaciones, GC inmediato o vidas disjuntas sin prueba.
El grafo inicial está incluido en G; eso no crea un fork, memo o conjunto opaque
adicional ejecutado. Su propiedad/almacenamiento completo debe reconciliarse,
incluida H03, sin omitirlo o duplicarlo por etiqueta.

## Registro condicional de bytes, sin promoverlo a prueba completa

I123 conserva por lote C=159925565 contenedores, A=319179960 ocurrencias hijas,
V=319180022 invocaciones de clon y O=1998 intentos de inserción opaque. Son
mayorantes estructurales condicionados, no valores medidos o bytes de heap.
Los coeficientes heredados I124 producen:

```
B = 1024*C + 512*A + 512*C + 64*V + 1024 + 512*O
  = 429494352768 bytes condicionales por lote
N*B = 53777*429494352768 = 23096917808804736 bytes condicionales
```

Este subtotal de los lotes clonados usa N, no G. No se multiplica silenciosamente
por 53778 ni se declara que ya valora toda la generación inicial. Se comprueba
por separado la contabilidad estructural de G: 8600477034570 contenedores y
25765336923450 unidades contenedor/ocurrencia, en el ámbito fuente heredado.
No son tamaños de objetos del runtime objetivo.

Los 23096917808804736 bytes conservan la etiqueta de mayorante condicional de
storage builtin, con crecimiento acumulado sobrecontado. El registro no verifica
de nuevo los fuentes upstream ni acredita equivalencia de binario/ABI/allocator
con el objetivo. El mayorante excluye términos señalados por I124 y no es un
upper completo H04/heap/RSS. Superar 6 GiB con un mayorante tan holgado no prueba
un lower real, sobrepresupuesto efectivo o inviabilidad. Tampoco acredita fit.

## Cobertura y vidas que faltan

Doce clases de requisitos cubren contenedores builtin/capacidades y crecimiento,
slots/temporales, memo/keys/values, enteros id, conjuntos opaque, generación
inicial, snapshots independientes, resultados publicados/escapados, drafts/memo
pendientes durante IO, rechazos/tracebacks, wrappers de soporte y términos
residuales. Cada fila mantiene null cardinalidad completa, tamaño, pico y vida:
48 huecos del inventario, no reapertura de los conteos fuente F/S ya cerrados.

Se verifican 150 pins con blobs Git y bytes actuales, trece proyecciones JSON
y ocho fuentes del superconjunto del observador de P01. Once símbolos y la
declaración de FIELDS proporcionan doce anclas AST. Se identifican trece sitios
sintácticos de llamada clone_metadata; no son trece invocaciones de campaña.

El fork declara un memo y opaque compartidos por sus cinco sitios de clonación,
y guarda memo en draft._memo. Dos rutas de lectura del proxy declaran memo fresco.
_atomic publica estado, puede retornar un valor escapado y mantiene draft/writes
mientras realiza IO fuera del lock; la ruta de error conserva excepción y puede
retener frames/draft. Se identifican también drain, flush y finish, sin ejecutarlos.
Estas fuentes justifican mantener obligaciones de alcance/retención, no una
reducción automática del pico, bytes vivos o latencia de colección.

Una mejora compatible necesita un teorema completo de reachability/coexistencia
y tamaños nativos/ABI del runtime exacto, incluyendo prefijos de rechazo del
ámbito P01/I124. No se presupone liberación al retornar, publicar o vaciar páginas.
El modelo heredado no es una garantía para control original inesperado o fallo
de asignación arbitrario fuera de su aplicabilidad.

Diez fronteras H01/H02/H03/H05–H11 siguen sin resolver: originales opacos no son
gratis, hojas/soporte persistente no desaparecen por compartirlas, y frames,
proyección/codecs, Reader, páginas/raw y overhead necesitan correspondencia.
El payload histórico de cuerpos/chunks no es propietario completo. H11 no es
reserva libre. Sin interning oculto, descuentos por alias o fusión de witnesses.

## Dictamen, verificación y unidad de commit

Upper completo/derivación, fits y slack siguen null: el resultado es
NOT_EVALUABLE_NO_COMPLETE_H04_BOUND. Se aplica el rechazo I132. Los cuatro
criterios E02 conservan clasificación, E01–E05 siguen abiertas y E06 separado,
pendiente, NOT_RUN y sin permiso. Otros 13 outputs siguen ausentes.

Fuentes, candidata03, plan/paquetes anteriores, cuotas/presupuestos/reservas,
certificado IMPLEMENTED_NOT_ADMITTED, capture_inputs y autoridad/destino intactos.
Sin SOURCE_CAPACITY_VERIFIED o captura habilitada. D5/H07 abiertos e IR03 NOT_READY.
P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados.
Brechas/obligaciones reales pendientes; I86/I89/I92 INVALID_CAPTURE sin reanudar
ni mezclar. Sin proveedores, credenciales, consumo, reservas operativas,
activación, promoción, despliegue o D6. No se inspecciona ni limpia dev/run_data/D4.

El [sello I145](../validation/D5-I145-integrity.json) fija cuatro artefactos sin
self pin. Resultado comprobado: PASS_STATIC_SOURCE_ONLY, H04 no verificado,
cero cierres, producto/componentes ejecutados cero y cuotas intactas. El auditor
conserva 203 archivos publicados e inputs heredados; JSON/AST, hashes y aritmética
no prueban identidad, capacidad, heap, CPU o tiempo de campaña.

Se publica una unidad documental cohesionada de cinco archivos, con diff superior
a 400 líneas orientativas por evidencia generada y verificación autocontenida;
se informa el exceso sin comprimir código o borrar evidencia. Runtime harness:
N/A, fase documental sin cambio de frontera runtime, con producto/componentes
prohibidos; sin imports de objetivo, builds, discovery, benchmarks o sondeos.
Rollback: retirar sólo los cinco archivos I145 enumerados en work_unit de la
revisión. Se hace commit y push de todos los cambios, con auditoría antes del
stage y después del commit, verificando referencia remota efectiva/árbol limpio.
