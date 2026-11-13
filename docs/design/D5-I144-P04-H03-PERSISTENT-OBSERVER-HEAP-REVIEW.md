# I144 — H03 sigue sin cota completa ni admisión

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`9db9e526959579d43fe6fe3351de46b20f037c8b`.

**La revisión confirma el dictamen de insuficiencia de P04-H03.** No se encuentran
defectos bloqueantes en la representación del expediente negativo. Sigue sin
aceptarse una prueba completa del heap del observador: upper, ajuste a 512 MiB
y slack desconocidos. E02 permanece abierta y PFC126-CANDIDATE-03/I122/PJC115-R2
mantienen la no admisión. H03 conserva sus bytes.

## Ruta de revisión

1. Leer los nueve campos y la decisión en la [revisión I144](../validation/D5-I144-P04-H03-documentary-review.json).
2. Contrastar pins, proyecciones y anclas en la [reconstrucción desde Git](../validation/D5-I144-P04-H03-source-reconstruction.json).
3. Consultar el [expediente H03](../validation/D5-PFC126-03-E02-H03.json) para sus doce clases de cobertura y diez límites de propiedad.

La revisión es técnica y documental. Este mismo asistente preparó I143;
recomponer fuentes no acredita independencia de actor/organización, autoridad de
custodio runtime o aceptación de memoria por un tercero. No se atribuye ese respaldo.

## Resultado del contraste

| Área | Resultado I144 |
| --- | --- |
| Plan e identidad | Ruta/schema, nueve campos y registro canónico I132/contrato03/I122 concordantes |
| Métrica y presupuesto | H03 cubre heap solicitado vivo del observador en el worker; 536870912 = 512 MiB permanece como presupuesto candidato |
| Procedencia | Blob publicado y 145 pins coinciden con Git de preparación (`89725dd…`) y bytes actuales |
| Proyecciones | Once punteros/valores/hashes canónicos recompuestos; referencias históricas o negativas no aportan cota nueva |
| Fuentes y anclas | Ocho resúmenes fuente, trece símbolos y declaración de FIELDS concordantes por posición/hash AST |
| Índice de candidatos | Coinciden 22 nombres FIELDS y ocho listas de atributos de constructores; no son un inventario completo de heap |
| Inventario y propiedad | Doce clases requeridas, 48 valores desconocidos y diez fronteras H01/H02/H04–H11 sin resolver |
| Campos y E02 | Dos definiciones documentales y siete campos insuficientes; cuatro criterios E02 con clasificación preservada, sin cierres |

## Aliases, callbacks y limpieza

La fuente atómica declara RLock, sus aliases _ref_lock/_emit_lock y Condition,
además de backlinks del binding al recorder y su callback. Llama directamente al
inicializador typed. El fork comienza con una copia superficial del __dict__;
la publicación reasigna callbacks y estado. Esto obliga a justificar raíces
compartidas, soporte nativo y coexistencia live/draft, sin deducir bytes libres,
multiplicidad total o descuentos por alias.

Las fuentes heredadas declaran threading.local, weakref.ref y almacenamiento de
cls/name/old/replacement en patches; restore limpia la lista. Un weakref no
retiene por sí solo su referent, pero su estructura y mapas siguen necesitando
cobertura. Las otras raíces fuertes permanecen distintas. Limpiar una lista no
prueba desaparición de todos los callbacks/closures/thread-locals o GC inmediato.

Los contrastes son de fuente, sin ejecutar el observador. La identidad cargada,
MRO/dispatch completo y layout nativo/ABI exactos siguen pendientes. Las ocho
listas sólo indexan escrituras literales a self en constructores seleccionados;
no encierran todas las mutaciones dinámicas, estructuras anidadas o raíces
transitivas. Los 22 FIELDS describen parte de la copia, no el propietario completo:
hojas escalares/inmutables y referencias compartidas también requieren tamaño,
cardinalidad y vida justificados.

## Límites de la prueba pendiente

Las doce clases de cobertura mantienen null cardinalidad, tamaño, pico y vida:
48 campos desconocidos, no toda la evidencia faltante ni 48 witnesses físicos.
Las filas pueden solaparse y el término residual permanece abierto. Los límites
lógicos refs/frames/filas y los bytes de archivos/payload no son una cota del
conjunto de objetos Python/nativos o de sus temporales y coexistencia.

Diez fronteras H01/H02/H04–H11 siguen pendientes. Raíces del observador no pagan
el heap privado original; clones, frames, codecs, Reader, páginas/raw y overhead
necesitan correspondencia. H11 no es reserva libre. No se descuentan términos
por interning o aliases ni se fusionan witnesses. Se conserva el sobreconteo
conservador sujeto a cobertura, y la aplicabilidad P01/I124 con prefijos de
rechazo, sin introducir hooks/control original inesperados o GC inmediato.

P01 independiente y P02 exacto siguen sin aceptar. La capacidad P03 y las otras
demandas no sustituyen una derivación H03. Sus carencias tampoco prueban por sí
mismas inviabilidad: aquí falta el propio upper completo. Se confirma
NOT_EVALUABLE_NO_COMPLETE_H03_BOUND, sin ajuste, sobrepresupuesto o memoria
realmente ilimitada demostrados.

## Disposición y publicación

Los 14 controles respaldan la coherencia del dictamen negativo, sin requerir
cambiar H03. Se confirma el rechazo I132, sin aceptar dependencias o revisión
independiente. E01–E05 siguen abiertas; E06 separado, pendiente, NOT_RUN y sin
permiso. Otros 14 outputs siguen ausentes, sin iniciar paquetes.

Fuentes, candidata03, plan/paquetes anteriores, cuotas/presupuestos/reservas,
certificado IMPLEMENTED_NOT_ADMITTED, capture_inputs y autoridad/destino intactos.
Sin SOURCE_CAPACITY_VERIFIED o captura habilitada. D5/H07 abiertos e IR03 NOT_READY.
P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados.
Brechas/obligaciones reales pendientes; I86/I89/I92 INVALID_CAPTURE sin reanudar
ni mezclar. Sin proveedores, credenciales, consumo, reservas operativas,
activación, promoción, despliegue o D6. No se inspecciona ni limpia dev/run_data/D4.

[Auditor I144](../validation/D5-I144-audit.py) y [sello de integridad](../validation/D5-I144-integrity.json).
`python3 docs/validation/D5-I144-audit.py` verifica blobs/JSON/AST, raíces,
presupuesto y no admisión; conserva 198 archivos publicados e inputs heredados.
Resultado comprobado: PASS_STATIC_SOURCE_ONLY, H03 no verificado, cero cierres,
ejecución de producto/componentes cero y cuotas sin cambios. No prueba heap,
identidad, capacidad o independencia. No se invocan los auditores históricos con
sus antiguos supuestos de working tree; sus artefactos permanecen íntegros.

Se publica una unidad documental: documento, revisión, reconstrucción, auditor y
sello. Se informa que el diff supera 400 líneas orientativas por evidencia
generada y verificación autocontenida, sin comprimir código o borrar evidencia.
Runtime harness: N/A, revisión documental sin cambios de frontera runtime;
producto/componentes prohibidos, sin builds/imports de objetivo/discovery/sondeos.
Rollback: retirar sólo los cinco archivos I144 enumerados en work_unit de la
revisión; fuentes/contratos/paquetes anteriores quedan íntegros. Se hace commit y
push de todos los cambios, con auditoría antes del stage y después del commit,
y se verifica remoto efectivo y árbol limpio.
