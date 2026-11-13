# I141 — H02 preparado sin cota completa de originales

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`6f71d9a52376933c92340e64a6cdcca781a8610b`.

**P04-H02 queda preparado como expediente de evidencia insuficiente.** No hay
upper completo de heap solicitado de originales ni ajuste verificado a 2 GiB.
E02 sigue abierta y PFC126-CANDIDATE-03/I122/PJC115-R2 mantienen la no admisión.
Los 2147483648 bytes son el presupuesto candidato intacto, sin aplicarlo como cuota.

## Ruta de comprobación

1. Leer los nueve campos y el dictamen del [expediente H02](../validation/D5-PFC126-03-E02-H02.json).
2. Revisar el [resumen de preparación](../validation/D5-I141-P04-H02-preparation-review.json), con dos definiciones documentales y siete campos insuficientes.
3. Ejecutar únicamente el [auditor documental](../validation/D5-I141-audit.py): `python3 docs/validation/D5-I141-audit.py`.

Se usa el destino/schema y las reglas de aceptación/rechazo P04-H02 de I132.
P01 independiente y P02 runtime exacto siguen pendientes. P03 disponibilidad y
H01 demanda son obligaciones distintas: no sustituyen la derivación privada de
H02 ni se convierten en dependencias aceptadas por preparar este expediente.
El productor documental es el asistente del chat, sin atestación de custodio o
aceptación independiente. El material se limita a registros/fuentes vinculados,
sin contactos externos, muestreo actual o afirmación de ausencia global.

## Qué significa «original parent-process»

| Proceso | Cuenta |
| --- | --- |
| Suite original dentro del worker I122, padre de sus hijos | H02 cubre su estado privado y originales retenidos, Python y nativos, en heap solicitado vivo |
| Coordinador de captura | Cuenta de proceso separada; no es el parent original de H02 |
| Hijos originales | Heaps separados; sus Process/Pipe/Thread wrappers, buffers y raíces que residen en el padre siguen necesitando cobertura allí |

CP03 acota operandos serializados concretos; no cubre por ello todo estado
privado, backing nativo, atributos no proyectados, temporales o retención.
Objetos opacos conservan identidad en el clonador, no coste cero.

## Cobertura por justificar

El inventario tiene doce clases de requisitos, sin afirmar completitud o partición:

| Clase | Estado original que requiere cardinalidad, tamaño y vida |
| --- | --- |
| R01 | Grafos fixture/client/remote/store/capture, configuración y atributos |
| R02 | Estado mutable, historiales, snapshots, manifests, tickets, resultados y coexistencia |
| R03 | Records/oráculos originales y registros globales/de clase retenidos entre tests |
| R04 | Suite/TestCase/result y originales conservados por framework/callbacks |
| R05 | Objetos Process/Pipe/IPC y buffers/bookkeeping nativos del padre |
| R06 | Threads, locks, eventos, thread-local y callbacks con referents vivos en el padre |
| R07 | Estado privado de store/reopen/transacción/IO y temporales de parse/serialización |
| R08 | Backing y asignaciones nativas privadas no reflejadas por payload o tamaño superficial |
| R09 | Originales referidos por record_refs, baselines, oracle_guards y causal_sources |
| R10 | Objetos antiguos/reabiertos/escapados que siguen alcanzables tras close/cleanup |
| R11 | Estado parcial y excepciones/rechazos aplicables con originales aún retenidos |
| R12 | Estado residual, oculto, lazy o aliased que las otras filas no prueban ausente |

Cada fila mantiene null cardinalidad, tamaño, upper vivo y derivación de vida:
48 valores desconocidos de este inventario, sin pretender enumerar toda carencia.
No se supone que todos los tests tengan vidas disjuntas, GC inmediato o eliminación
de toda raíz al cerrar un fixture. Una prueba completa debe cubrir también
coexistencia y retención de originales entre pasos/casos, bajo el ámbito P01/I124
fijo de 321 raíces/12 grupos y los prefijos aplicables. No se amplía ese ámbito a
control de flujo original inesperado, hooks nuevos o fuentes modificadas.

## Contraste fuente de identidad y retención

Se verifican 140 pins contra blobs Git de la base publicada y bytes actuales,
con once proyecciones JSON de candidata03, H02 histórico I125, P01/P02/P03 y H01,
y sus revisiones pertinentes. No aportan una identidad runtime o cota nueva.

Los 79 inputs originales registrados contienen 71 archivos Python. Su índice
AST encuentra 477 sitios sintácticos de escritura en atributos `self`, con
resúmenes/hashes por archivo y del vector completo. No cubre automáticamente
setattr dinámico, aliases, estado nativo u objetos ocultos; tampoco prueba carga,
frecuencia de ejecución, número de instancias o almacenamiento vivo.

Diez anclas fijan clone_metadata, opaque_originals, el fork atómico, retención de
records/oráculos, tres constructores fixture y dos helpers de procesos padres.
Los tres constructores ilustran raíces concretas, sin reducir toda la campaña a
tres fixtures. La comprobación es sólo AST; no se construyen fixtures ni procesos.

El clonador retorna `value` cuando su identidad está en `opaque`. Las cuatro
raíces declaradas por opaque_originals son record_refs, record_baselines,
_causal_data.oracle_guards y causal_sources. Los sitios de append conservan el
valor original junto a su binding/digest. Esto exige una derivación de retención;
el digest o contenedor de referencia del observador no paga el heap del referent.
No se infiere una vida numérica ni un tamaño de esos sitios fuente.

## Propiedad, cota y disposición

Los diez límites H01/H03–H11 quedan explícitos y sin resolver: representación
runtime, roots del observador, clones/memo, frames/excepciones, proyección/codecs,
Reader, páginas, IO/raw y overhead allocator deben reconciliarse con originales
privados. Compartir identidad no autoriza descontar/fusionar witnesses u omitir
raíces. Puede sobrecontarse conservadoramente, sin usar H11 como reserva libre.

Upper completo/derivación, fits y slack siguen null. El resultado es
NOT_EVALUABLE_NO_COMPLETE_H02_BOUND; no se prueba ajuste, sobrepresupuesto,
memoria realmente ilimitada o inviabilidad. Dos definiciones documentales y
siete campos insuficientes no cierran una obligación de recursos. Los cuatro
criterios E02 conservan clasificación y se aplica el rechazo del plan.

E01–E05 siguen abiertas, E06 separado, pendiente, NOT_RUN y sin permiso. Los otros
15 outputs del plan siguen ausentes. No se ejecutan producto/componentes, imports
de objetivo, builds, escenarios, benchmarks o sondeos. Cuotas, presupuestos y
reglas de reserva intactos, transferencias cero. Se conservan fuentes/candidata03,
plan/paquetes anteriores, certificado IMPLEMENTED_NOT_ADMITTED, capture_inputs y
autoridad/destino. Sin SOURCE_CAPACITY_VERIFIED o captura habilitada.

D5/H07 abiertos e IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL
(UI04.1); D1–D4 e I1–I20/A52 aceptados sin cambios. Brechas/obligaciones reales
pendientes; I86/I89/I92 INVALID_CAPTURE sin reanudar/mezclar. Sin proveedores,
credenciales, consumo, reservas operativas, activación, promoción, despliegue o
D6. No se inspecciona ni limpia dev/run_data/D4.

## Verificación y publicación

El [sello I141](../validation/D5-I141-integrity.json) fija cuatro artefactos sin
self pin. El auditor conserva 183 archivos publicados e inputs heredados; verifica
hashes/blobs, JSON/AST, nueve campos, inventario, presupuesto y no admisión.
PASS_STATIC_SOURCE_ONLY valida la preparación negativa, no heap o capacidad.
Se usan helpers documentales estándar/Git. El auditor funciona antes del stage y
después del commit; se hace commit y push de los cinco archivos I141 y se verifica
la referencia remota efectiva y el árbol limpio.
