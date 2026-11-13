# I139 — preparación de P04-H01, heap de runtime/imports

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`451a629c53a7d0040b82e1bfba45fa10451795e9`.

**P04-H01 queda preparado como expediente de requisitos de cobertura y evidencia
insuficiente. No hay una cota completa de H01 ni ajuste verificado a 256 MiB.**
Se mantiene abierta E02 y la no admisión de PFC126-CANDIDATE-03/I122/PJC115-R2.
El presupuesto candidato de 268435456 bytes se conserva sin aplicarlo como cuota.

[H01 preparado](../validation/D5-PFC126-03-E02-H01.json) ·
[Revisión de preparación](../validation/D5-I139-P04-H01-preparation-review.json) ·
[Auditoría estática](../validation/D5-I139-audit.py) ·
[Integridad](../validation/D5-I139-integrity.json).

## Requisitos y dependencia de identidad exacta

El artefacto utiliza el destino y schema P04-H01 previstos en I132 y presenta
sus nueve campos específicos, incluido el literal de presupuesto del plan.
Identidad de propietario/métrica/unidad y presupuesto son definiciones
documentales; los otros siete campos siguen insuficientes para aceptar una
prueba completa. Se aplican las reglas de aceptación/rechazo del plan, sin
sustituir tamaños de archivos ejecutables o fuente por heap cargado.

P01 conserva conformidad técnica del ámbito, con aceptación independiente
pendiente. P02 sigue sin identidad runtime aceptada; faltan cierre seleccionado,
fuente/build/binario, ABI y modelos de asignación nativa/allocator. La referencia
histórica y los tamaños seleccionados de tipos no aportan ese modelo completo.
P03 sigue sin capacidad/servicio atestados según I138.

La cota de demanda de H01 y la disponibilidad de plataforma son obligaciones
distintas: P03 no es un sustituto de la derivación de propietario. Una prueba
completa de H01 permitiría comparar demanda con su presupuesto, aunque la
admisión aún necesitase capacidad verificada por separado. Aquí falta la propia
cota; no se calcula fit ni se afirma inviabilidad por carecer de P03.

Esta preparación negativa, autorizada en I139, no acepta las dependencias ni
inicia cálculos de cierre sustentados en una identidad runtime inventada. El
productor es el asistente del chat, sin autoridad de custodio runtime ni
aceptación de revisor independiente. El alcance se limita a fuentes y registros
vinculados, sin alegar ausencia global de documentación o hacer contactos externos.

## Inventario concreto por completar

H01 cubre heap solicitado vivo dinámico Python/nativo del runtime del worker,
incluidos startup/imports y estado pertinente durante la campaña. No se limita
a un baseline de arranque ni al coste añadido por clonar metadatos. La lista
siguiente fija cobertura necesaria, no demuestra que el inventario sea completo:

| Clase | Asignaciones cuya cardinalidad, tamaño y vida faltan |
| --- | --- |
| R01 | Estado dinámico del intérprete, configuración y soporte de evaluación/runtime |
| R02 | Maquinaria de import, registro de módulos, finders/loaders y caches |
| R03 | Representación de módulos/código/constantes/nombres/funciones/clases/defaults/anotaciones/decoradores |
| R04 | Temporales de lectura, decode, compilación y carga, con su coexistencia |
| R05 | Inicialización y estado privado de builtin/extensiones y dependencias nativas transitivas |
| R06 | Soporte runtime de threads, thread-local y sincronización |
| R07 | Efectos de inicialización de módulos, contenedores y registros globales |
| R08 | Estado de import/discovery/framework de la campaña original y su representación runtime |
| R09 | GC, caches/free-lists y estado retenido, en la métrica solicitada exacta |
| R10 | Inicialización parcial y prefijos de rechazo aplicables, con raíces/excepciones retenidas |
| R11 | Definiciones/clases/closures y referencias capturadas por el build atómico en import |
| R12 | Asignaciones runtime/nativas/transitivas o lazy restantes, que no se prueban ausentes |

Cada clase conserva cuatro valores null: cardinalidad, tamaño por asignación,
upper vivo y derivación de vida. Son 48 huecos de este inventario, no un conteo
exhaustivo de toda la evidencia que falta. No se supone GC inmediato, liberación
de caches, tamaño nativo cero o duración acotada de cada raíz.

Una derivación futura tendrá que cubrir todos los sitios de asignación del
runtime exacto, justificar tamaños/multiplicidades y coexistencia/reachability,
y obtener un upper conservador del propietario completo antes de compararlo
con 268435456. Enumerar requisitos o contar sintaxis no cumple esa derivación.
No se propone una fórmula numérica a partir de archivos, declaraciones o tamaños
ABI históricos sin correspondencia y cobertura acreditadas.

## Fuentes de startup/imports y límites de su contraste

Se verifican 135 pins contra blobs Git de la base publicada y bytes actuales.
Nueve proyecciones JSON fijan punteros, valores y hashes canónicos de H01,
identidad/capacidad pendientes, revisiones I136/I138, I125 y ámbito P01.

Se analizan por AST las 79 fuentes Python ya incluidas en el ámbito estático de
P02. Sus 1745 sentencias de cuerpo de módulo tienen resúmenes por archivo y hash
del vector fuente. Es un índice de sintaxis: no prueba que todos los módulos o
ramas se carguen, ni cuántos objetos se asignen o permanezcan vivos. Definiciones,
defaults, decoradores y cuerpos compilados necesitan el modelo de ejecución
exacto; el índice no representa un cierre stdlib/frozen/builtin/nativo completo.

Seis anclas fijan import del capture por el worker, import de atomic.build,
llamada a `_atomic_build(sys.modules[__name__])` en el cuerpo de capture, definición
de build, worker.main e import dinámico del runner. Esto hace explícita una
fuente de definiciones y referencias runtime que no puede omitirse por llamarse
«metadata». No se ejecuta build ni otro componente para inspeccionarla.

El tamaño del binario histórico de I127, los bytes de archivos, las cotas de
serialización/Reader o los contadores F/S no constituyen upper completo H01.
Los archivos pueden tener cargas/representaciones/temporales y estado nativo
que requieren su propia justificación. Tampoco se sondea el runtime actual
mediante sys.getsizeof, tracemalloc, imports, loaders o medición de memoria.

## Propiedad, aliases y prefijos de rechazo

El expediente deja diez reconciliaciones explícitas con H02–H11. El runtime de
módulos originales y sus estructuras de import no se elimina por asignar datos
privados a H02; los objetos originales opacos no son memoria gratuita.
Clases/closures/globals/locks y raíces persistentes requieren correspondencia
con H03; clones/memo con H04; frames/generadores/tracebacks con H05; proyección y
codecs con H06/H07; Reader, páginas y StringIO/raw con H08–H10.

H11 mantiene separado el overhead de backing/arenas/retención/fragmentación del
allocator respecto de bloques solicitados vivos. Su 1 GiB no es una reserva
libre de H01. Una cache/free-list o bloque retenido necesita clasificación bajo
la métrica exacta, sin exclusión automática, préstamo de H11 ni doble crédito.
El sobreconteo conservador puede ser válido; una reducción por alias/compartición
requiere prueba y no autoriza fusión de witnesses u omisión de raíces.

Se conserva el ámbito fuente fijo de P01 y sus condiciones I124: éxito original
321 raíces/12 grupos y prefijos de rechazo del observador que correspondan.
Inicialización parcial, temporales, raíces y excepciones retenidas necesitan
cobertura en esos caminos. No se amplía el alcance a control de flujo original
inesperado, import hooks nuevos o fuentes cambiadas para fabricar una prueba.
Worker, coordinador e hijos conservan cuentas separadas conforme a P01.

## Dictamen y verificación

Upper completo/derivación, fits y slack permanecen null. El resultado es
NOT_EVALUABLE_NO_COMPLETE_H01_BOUND: no ajuste, sobrepresupuesto o memoria
realmente ilimitada demostrados. El presupuesto candidato de 256 MiB, las cuotas
y todas las reglas de reserva se conservan; transferencia cero no significa
uso real cero ni capacidad libre. No se emite certificado positivo o autoridad.

Los cuatro criterios E02 conservan su clasificación sin cierre. E01–E05 siguen
abiertas, E06 separado, pendiente, NOT_RUN y sin permiso. Los otros 16 outputs del
plan siguen ausentes. No se producen P04-H02…H11, agregación P05 o pruebas de
trabajo/compatibilidad/tiempo/binding/cierre posteriores.

Se mantienen candidata03, plan I132, P01/P02/P03 y fuentes, certificado
IMPLEMENTED_NOT_ADMITTED, capture_inputs, autoridad/destino y reservas operativas.
D5/H07 abiertos e IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL
(UI04.1); D1–D4 e I1–I20/A52 aceptados sin cambios. Brechas/obligaciones reales
pendientes; I86/I89/I92 INVALID_CAPTURE sin reanudar/mezclar. Sin proveedores,
credenciales, consumo, activación, promoción, despliegue o D6. No se inspecciona
ni limpia dev/run_data/D4.

`python3 docs/validation/D5-I139-audit.py` comprueba JSON, hashes/blobs, AST,
nueve campos, inventario, límites, presupuesto y dictamen negativo. Conserva
173 archivos publicados y los inputs heredados. PASS_STATIC_SOURCE_ONLY valida
la preparación, no demanda/capacidad, identidad runtime o cota de heap. Sólo se
ejecutan helpers documentales estándar/Git; sin producto/componentes, builds,
discovery, benchmarks o sondeos. El auditor funciona antes del stage y después
del commit; se hace commit y push de los cinco archivos I139 y se verifica remoto
efectivo/árbol limpio.
