# I143 — H03 preparado sin cota completa del observador

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`89725ddaa0e5d056362fa106a40036bf251b0234`.

**P04-H03 queda preparado como expediente de evidencia insuficiente.** No hay
upper completo del observador persistente ni ajuste verificado a 512 MiB.
E02 sigue abierta y PFC126-CANDIDATE-03/I122/PJC115-R2 mantienen la no admisión.
Los 536870912 bytes son el presupuesto candidato intacto, sin aplicarlo como cuota.

## Ruta de comprobación

1. Leer los nueve campos y el dictamen del [expediente H03](../validation/D5-PFC126-03-E02-H03.json).
2. Contrastar raíces, anclas y resumen en la [revisión de preparación](../validation/D5-I143-P04-H03-preparation-review.json).
3. Ejecutar sólo el [auditor documental](../validation/D5-I143-audit.py): `python3 docs/validation/D5-I143-audit.py`.

P01 independiente/P02 exacto siguen pendientes. La capacidad P03 y las demandas
H01/H02 no sustituyen la derivación de H03. Esta preparación negativa no acepta
las dependencias ni inicia los otros 14 outputs todavía ausentes. El productor
es el asistente del chat; no atesta autoridad de custodio o aceptación independiente.

## Raíces y cobertura pendientes

Se verifican 145 pins contra blobs Git de la base y bytes actuales, con once
proyecciones JSON y ocho fuentes del superconjunto local del observador de P01.
Trece anclas de símbolos más la declaración de FIELDS fijan el contraste AST.
Las ocho listas de atributos candidatos de constructores comparan nombres con
los 22 FIELDS. No son un cierre cargado, MRO/dispatch completo o inventario de
heap: faltan mutaciones dinámicas, estructuras anidadas, nativo y reachability.

| Clase | Cobertura cuya cardinalidad, tamaño y vida faltan |
| --- | --- |
| R01 | Entry/profile/policies/specs, schemas y mapas de configuración |
| R02 | Bindings/projector, lookup/Reader y callbacks de propietario |
| R03 | Patches, old/replacement, wrappers, firmas y closures capturadas |
| R04 | Objetos weakref, mapas de owners/context y su metadata |
| R05 | RLock/Condition, waiters y soporte de sincronización Python/nativo |
| R06 | threading.local y diccionarios/valores de cada thread pertinente |
| R07 | Raíces/tables/callbacks de estados causal/parental/domain |
| R08 | Hojas escalares/inmutables, strings/bytes/IDs/keys/digests |
| R09 | Raíces compartidas live/draft y objetos reemplazados coexistentes |
| R10 | Ledger/owner/helpers/channels y soporte auxiliar del observador |
| R11 | Raíces retenidas durante restore, rechazo, error o finalización aplicables |
| R12 | Raíces residuales/transitivas/ocultas no probadas ausentes |

Cada clase conserva null cardinalidad, tamaño, pico y derivación de vida: 48
valores desconocidos de este inventario. Las filas no se declaran completas ni
disjuntas por enumerarlas. Los límites lógicos refs/frames/filas y los bytes
serializados no convierten en memoria acotada todos sus objetos, hojas o soporte.

## Qué prueban las anclas

La fuente declara un RLock y lo asigna también a _ref_lock/_emit_lock, más un
Condition ligado a él. Declara callbacks/backlinks del binding hacia self. El
constructor atómico llama directamente al inicializador typed; el fork hace una
copia superficial inicial del __dict__ antes de clonar campos concretos.
Estos hechos identifican obligaciones de alias/retención y coexistencia, sin
medir objetos, garantizar vidas o asignar descuentos numéricos.

El inicializador base declara threading.local. El owner base declara weakref.ref;
patch conserva cls/name/old/replacement y restore limpia la lista de patches.
Son sitios fuente heredados, sin afirmar un dispatch ejecutado o una derivación
completa de todos los caminos. Un weakref no retiene por sí solo su referent,
pero el weakref/mapa ocupa memoria y otras raíces fuertes siguen siendo distintas.
Limpiar una lista no prueba que closures, callbacks, clases o threads hayan
eliminado todas las demás referencias ni que GC libere inmediatamente.

No se importa ni construye el observador para obtener estos datos. El ABI,
backing nativo de sincronización/thread-local/weakrefs y modelo allocator del
runtime exacto siguen sin acreditar. FIELDS enumera parte de la copia de
metadatos, no la propiedad completa del heap: incluso dentro de esos grafos las
hojas compartidas requieren tamaño, multiplicidad y dueño justificados.

## Límites y dictamen

Diez fronteras H01/H02/H04–H11 quedan explícitas y sin resolver. Los contenedores
del observador no pagan el heap privado de originales; código/runtime, clones,
frames, proyección/codecs, Reader, páginas/raw y overhead requieren reconciliación.
H11 no es reserva libre. No se deduce slack por aliases o interning, ni se
fusionan witnesses. Puede sobrecontarse conservadoramente con cobertura sustentada.

Se conserva P01/I124 y sus prefijos de rechazo aplicables, sin extender a hooks o
control original inesperado. No hay prueba completa de roots/vidas/native: upper,
derivación, fits y slack siguen null. El resultado es
NOT_EVALUABLE_NO_COMPLETE_H03_BOUND, sin ajuste, sobrepresupuesto, memoria
ilimitada o inviabilidad demostrados. Se aplica el rechazo del plan I132.

Dos campos son definiciones documentales y siete insuficientes. Los cuatro
criterios E02 conservan clasificación sin cierre. E01–E05 siguen abiertas;
E06 separado, pendiente, NOT_RUN y sin permiso. Fuentes, candidata03, plan y
paquetes anteriores, cuotas/presupuestos/reservas, certificado
IMPLEMENTED_NOT_ADMITTED, capture_inputs y autoridad/destino intactos; sin
SOURCE_CAPACITY_VERIFIED o captura habilitada. D5/H07 abiertos e IR03 NOT_READY.
P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados.
Brechas/obligaciones reales pendientes; I86/I89/I92 INVALID_CAPTURE sin reanudar.
Sin proveedores, credenciales, consumo, reservas operativas, activación, promoción,
despliegue o D6. No se inspecciona ni limpia dev/run_data/D4.

## Verificación, unidad de commit y rollback

El [sello I143](../validation/D5-I143-integrity.json) fija cuatro artefactos sin
self pin. El auditor conserva 193 archivos publicados e inputs heredados.
Resultado comprobado: PASS_STATIC_SOURCE_ONLY, con H03 no verificado, cero
cierres, ejecución de producto/componentes cero y cuotas sin cambios.

Se publica una unidad documental cohesionada: expediente, revisión de preparación,
auditor, documento y sello. El diff completo supera el presupuesto orientativo de
400 líneas por sus registros de evidencia generados y verificaciones; se informa
el exceso sin comprimir código ni eliminar evidencia para aparentar ajuste.
La revisión puede empezar por el dictamen y seguir los hashes/anclas del expediente.
Runtime harness: N/A, fase documental sin cambio de frontera runtime y con
producto/componentes expresamente prohibidos. No se ejecutan builds, imports de
objetivo, discovery, benchmarks o sondeos.

Rollback: retirar exactamente los cinco archivos I143 enumerados en work_unit
de la revisión de preparación; no afecta fuentes, contratos o paquetes anteriores.
El auditor funciona antes del stage y después del commit. Se hace commit y push
de todos los cambios I143 y se verifica la referencia remota efectiva/árbol limpio.
