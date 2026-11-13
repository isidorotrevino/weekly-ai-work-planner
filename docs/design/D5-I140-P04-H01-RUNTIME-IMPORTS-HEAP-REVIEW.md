# I140 — H01 sigue sin cota completa ni admisión

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`e5cb55f8dcf30fbab217609538ed959764b2ac31`.

**La revisión confirma el dictamen de insuficiencia de P04-H01.** El expediente
representa correctamente los requisitos pendientes; no se encuentran defectos
bloqueantes de esa representación. No se acepta una prueba completa de H01:
upper, ajuste a 256 MiB y slack siguen desconocidos. E02 permanece abierta y
PFC126-CANDIDATE-03/I122/PJC115-R2 mantienen la no admisión. H01 conserva sus bytes.

## Ruta de revisión

1. Leer la decisión y los nueve campos en la [revisión I140](../validation/D5-I140-P04-H01-documentary-review.json).
2. Contrastar pins, proyecciones y anclas en la [reconstrucción desde Git](../validation/D5-I140-P04-H01-source-reconstruction.json).
3. Consultar el [expediente H01 original](../validation/D5-PFC126-03-E02-H01.json) para las doce clases de cobertura y diez límites H02–H11.

La revisión es técnica y documental. Este mismo asistente preparó I139; la
recomputación separada no acredita independencia de actor/organización, autoridad
de custodio runtime o aceptación por un tercero. No se fabrica ese respaldo.

## Qué queda confirmado

| Área | Resultado I140 |
| --- | --- |
| Identidad y presupuesto | Ruta/schema/tarea P04-H01 y contrato03/I122 coinciden. H01 usa bytes enteros de heap solicitado del worker; 268435456 = 256 MiB permanece como presupuesto candidato |
| Nueve campos del plan | Dos definiciones documentales y siete campos insuficientes; ninguno cierra una obligación de recursos |
| Procedencia | Blob H01 publicado y sus 135 pins coinciden con Git de preparación (`451a629…`) y bytes actuales; nueve proyecciones JSON recompuestas |
| Fuentes | Coinciden 79 archivos, resúmenes por archivo y hash del vector de 1745 sentencias de cuerpo de módulo; no son conteos de asignaciones ni cierre cargado |
| Inventario | Doce clases de cobertura requeridas, sin completitud demostrada; 48 valores de cardinalidad/tamaño/pico/vida siguen null |
| Límites de propiedad | Diez reconciliaciones H02–H11 siguen sin resolver; no hay crédito por alias, descarte de originales o préstamo de H11 |
| Cota y comparación | Sin upper completo o derivación; fits/slack null. No se prueba ajuste, sobrepresupuesto, memoria ilimitada o inviabilidad |
| Efectos | Se conservan las clasificaciones de los cuatro criterios E02, sin cierres, cuotas aplicadas o transferencias de reserva |

Las nueve proyecciones se recomponen por puntero, valor y hash canónico desde los
blobs fijados. La referencia histórica, tamaños ABI seleccionados y estado
negativo P02/P03 no se convierten en evidencia nueva de asignación o capacidad.

## Comprobación del build y sus límites

Las seis anclas coinciden en posición, hash AST y ámbito de módulo o símbolo
léxico. Se comprueba la cadena de fuente: el worker importa capture; capture
importa relativamente atomic.build como `_atomic_build` y declara una llamada
a `_atomic_build(sys.modules[__name__])` en su cuerpo de módulo. La asignación
recibe los nombres `Recorder, LateBindings`; build declara `Pages`, `CausalProxy`,
`Bindings` y `Recorder`, y retorna `Recorder, Bindings`. También se fija el import
dinámico del runner dentro de worker.main.

Esta cadena identifica una obligación concreta de cobertura runtime/imports.
Cuatro declaraciones de clase y dos nombres retornados no determinan bloques
vivos, tamaños, closure layout o retención real. No se ejecuta build ni se importa
el objetivo. Los defaults/decoradores, temporales de carga, caches, estado nativo
y asignaciones lazy restantes siguen necesitando el modelo exacto y una derivación.

El inventario conserva términos residuales y no se llama completo por enumerar
doce clases. Sus filas pueden solaparse; 48 nulls son campos contrastados, no
48 witnesses físicos o todas las carencias. La coexistencia de raíces/temporales,
GC, destrucción diferida y prefijos de rechazo aplicables siguen sin prueba.
No se asume liberación inmediata ni se extiende el ámbito P01/I124 a hooks o
control original inesperado. Originales opacos no significan memoria gratuita.

H11 mantiene separada la correspondencia solicitada/comprometida del allocator;
su presupuesto no financia automáticamente H01. Los requisitos H02–H11 tampoco
permiten omitir asignaciones o resolver propiedad por etiqueta. Una reducción
por alias exige prueba; se conserva la posibilidad de sobreconteo conservador.

## Dependencias y disposición

P01 independiente sigue pendiente y P02 no acredita aún el runtime/ABI/nativo
exactos. P03 no acredita capacidad/servicio. La disponibilidad P03 y la demanda
H01 son obligaciones distintas: faltar capacidad no refuta por sí mismo una
prueba de demanda. Aquí falta la cota completa de H01, por lo que su comparación
no es evaluable. La revisión no acepta ni omite esas dependencias.

Los 14 controles documentales respaldan el dictamen negativo y no requieren
cambiar H01. Se confirma el rechazo del plan I132, manteniendo 256 MiB, cuotas y
reservas intactos. E01–E05 permanecen abiertas; E06 separado, pendiente, NOT_RUN
y sin permiso. Los otros 16 outputs del plan siguen ausentes, sin iniciar paquetes.

Permanecen íntegros candidata03, plan I132, P01/P02/P03, fuentes, certificado
IMPLEMENTED_NOT_ADMITTED, capture_inputs y autoridad/destino. No se emite
SOURCE_CAPACITY_VERIFIED o habilitación de captura. D5/H07 abiertos e IR03
NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52
aceptados sin cambios. Brechas/obligaciones reales pendientes; I86/I89/I92
INVALID_CAPTURE sin reanudar/mezclar. Sin proveedores, credenciales, consumo,
reservas operativas, activación, promoción, despliegue o D6. No se inspecciona
ni limpia dev/run_data/D4.

## Verificación y publicación

[Auditor I140](../validation/D5-I140-audit.py) y [sello de integridad](../validation/D5-I140-integrity.json).
`python3 docs/validation/D5-I140-audit.py` verifica blobs, JSON, índice/símbolos/AST,
inventario, presupuesto y no admisión. Conserva 178 archivos publicados e inputs
heredados. Sólo añade documento, revisión, reconstrucción, auditor y sello I140.

PASS_STATIC_SOURCE_ONLY valida la revisión del expediente insuficiente, no heap,
capacidad, identidad o independencia. Se usan helpers documentales estándar/Git,
sin producto/componentes, builds, discovery, benchmarks o sondeos. El auditor
funciona antes del stage y después del commit; se hace commit y push de todos
los cambios I140 y se verifica la referencia remota efectiva y el árbol limpio.
