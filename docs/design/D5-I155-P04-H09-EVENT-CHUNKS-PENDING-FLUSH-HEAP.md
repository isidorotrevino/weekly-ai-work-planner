# I155 — H09 preparado, sin cota completa de chunks y flush

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`bb41c1185358ffe959adc6f80e136e899df2b746`.

**P04-H09 queda preparado como expediente de insuficiencia.** Los chunks,
cuerpos pendientes y temporales de flush están vinculados a fuentes fijadas,
sin una cota completa de heap solicitado vivo. Upper, ajuste al presupuesto
candidato de **201326592 bytes (192 MiB)** y slack permanecen desconocidos.
E02 sigue abierta y PFC126-CANDIDATE-03/I122/PJC115-R2 sin admisión. No se aplican
cuotas ni reservas, ni se modifica capture_inputs.

## Ruta de revisión

1. Leer los nueve campos y el inventario en [H09](../validation/D5-PFC126-03-E02-H09.json).
2. Contrastar source_evidence, page_source_relationships e inherited_page_payload_reference.
3. Consultar la [preparación I155](../validation/D5-I155-P04-H09-preparation-review.json) para la disposición y el progreso del plan.

El plan I132 y los paquetes anteriores conservan sus bytes; I155 registra la
preparación actual sin reescribir el estado histórico PLANNED_NOT_PRODUCED.
Este asistente no acredita aceptación del revisor independiente de memoria
previsto en I132 ni autoridad de custodio de runtime.

## Payload heredado y presupuesto

| Término condicionado del modelo I123/I124 | Bytes |
| --- | ---: |
| Cuerpos pendientes, payload | 67108864 |
| Todos los chunks históricos distintos, incluido memo | 67108864 |
| Cuerpos + chunks distintos, payload | 134217728 |
| Presupuesto candidato H09 | 201326592 |
| Presupuesto menos payload, aritmética solamente | 67108864 |

**Los 64 MiB de diferencia no son slack de heap verificado.** La subcota de
128 MiB omite cabeceras, listas/mapas/tuplas, capacidades/growth, ocurrencias de
punteros, join/concat, Unicode/codecs y soporte nativo. Tampoco constituye cota
del observador global ni de todos los prefijos rechazados. Se conserva el ámbito
exitoso condicionado de I123/I124 bajo P01/I124.

32 páginas × 2097152 bytes coincide con los 67108864 bytes candidatos de páginas
totales; esa aritmética no aporta tamaños de objetos o vidas. El modelo no se
amplía por multiplicar payload distinto por cada lote como si fueran nuevas
asignaciones reales, ni concede storage gratis por compartir referencias.
Un sobreconteo conservador explícito requiere todavía cobertura completa.

## Construcción, publicación y retención

| Sitio fuente | Requisito identificado |
| --- | --- |
| PageSink.append | encode(event) precede al control de event_bytes; flush del lote anterior puede preceder al append del nuevo chunk |
| Pages.flush | Guarda planning anterior al body; join/concat y header encode preceden a los controles de página y total |
| Cola/manifest | reference precede a encolar el body; se construyen nombre, tupla, manifest y scalars antes de resetear chunks |
| clone_metadata / _fork | Ramas exactas de contenedores y fallback escalar; memo mantiene listas clonadas y sus referencias a chunks, con raíz draft._memo |
| _atomic / _publish | Se forma writes=tuple(...) antes de publicar; resetear _writes no elimina todas las raíces locales de writes/body |
| IO / drain | write_all está fuera del lock de metadatos; decremento pendiente ocurre antes del retorno, sin prueba de colección completa |

Se vinculan **188 pins**, doce proyecciones JSON, 79 fuentes y 21 anclas. Diez
relaciones de orden y once registros de expresiones, con coordenadas y hashes
AST, documentan guardas, construcción, publicación, reset e IO. No son diez
asignaciones sin controles previos ni pruebas de liberación, frecuencia o bytes.

La fuente de clone_metadata incluye ramas dict/list/tuple/set/frozenset y
fallback return value. Bajo sus bindings/precondiciones, los bytes escalares no
se recopian mediante esas ramas. Eso no paga los headers de listas, memo y
punteros, ni establece el layout del runtime. Los chunks antiguos siguen en el
requisito de retención: resetear pages.chunks no demuestra que desaparezcan de
draft._memo o de otros callers/errores. Tampoco se afirma retención eterna.

El tuple de writes, draft, body/name y errores puede mantener raíces más allá
de la publicación y del lock. Un contador pendiente, drain, cleanup o retorno
no es una prueba completa de vidas o serialización de todas las asignaciones
del worker. Los intentos fallidos de encode/flush, buffers parciales y errores de
IO/finalización requieren cotas adicionales; no se cubren por el payload exitoso.

## Cobertura y disposición

Doce clases requeridas cubren chunks, listas, cuerpos, join/concat, codificación,
headers/manifest, writes, memo histórico, transición fork/publish, IO pendiente,
rechazos y concurrencia/nativo. Cada una mantiene null en cardinalidad, tamaño,
pico vivo y vida completos: **48 valores desconocidos**. Son requisitos de
cobertura, sin inventario exhaustivo ya demostrado.

Las diez fronteras H01–H08/H10–H11 permanecen abiertas. Baseline nativo,
originales, roots persistentes, clones/memo, carriers, proyección/digest, codecs,
Reader, salida y overhead requieren asignación explícita de bloques y vidas.
Un carrier no paga su referente; H11 no es reserva libre. Se hereda el scope
worker/otros procesos P01, sin sumar automáticamente heaps de padre o hijos,
crear cuotas por página/thread o descontar por alias, interning o fusión de witnesses.

F≤52018, S≤1759, 53777 lotes y 53778 generaciones con inicial conservan el
contexto condicional P01/I124, sin dar tamaños o máximo completo de storage
pendiente. Faltan P02 exacto y los modelos de objetos, codec/nativo, growth,
generaciones retenidas y vidas conjuntas. La carencia se refiere al material
suministrado, sin afirmar ausencia global o inviabilidad.

Los nueve campos requeridos están presentes: dos definiciones documentales y
siete insuficientes para aceptación. Se conserva el rechazo I132 contra usar
128 MiB distintos como prueba completa de 192 MiB o cota global del observador.
Sin upper, ajuste, slack, sobrepresupuesto real o memoria ilimitada demostrados.
P01 independiente, P02 exacto y P03 siguen pendientes; otros propietarios o la
capacidad no sustituyen la demanda H09. Quedan ocho outputs sin producir y no
se inicia otro paquete en I155.

E01–E05 abiertas; E06 separado, pendiente, NOT_RUN y sin permiso de ejecución.
I122 conserva IMPLEMENTED_NOT_ADMITTED; sin SOURCE_CAPACITY_VERIFIED, propuesta
o captura. D5/H07 de cierre abiertos e IR03 NOT_READY. P0 conserva
83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados y brechas/
obligaciones reales pendientes. I86/I89/I92 INVALID_CAPTURE sin reanudar ni mezclar.

## Verificación y publicación

`python3 docs/validation/D5-I155-audit.py`: **PASS_STATIC_SOURCE_ONLY**.
Contrasta Git/JSON/AST, aritmética heredada, presupuesto y no admisión, con
**253 archivos publicados** e inputs heredados preservados. No prueba heap,
ABI, vidas, capacidad, CPU/tiempo o independencia.

H09, preparación, este documento, [auditor](../validation/D5-I155-audit.py) y
[sello](../validation/D5-I155-integrity.json) forman una unidad documental de
cinco archivos. El diff supera 400 líneas por evidencia generada y auditoría
autocontenida; se informa el exceso sin comprimir código o retirar evidencia.
Runtime harness: N/A, sin cambio de comportamiento runtime. Rollback: retirar
sólo los cinco archivos enumerados en work_unit. Se audita antes del stage y
después del commit, con push y verificación de remoto efectivo y árbol limpio.

Sin producto/componentes importados, compilados o ejecutados, tests, benchmarks,
consumo de generadores, introspección, instrumentación o sondeos de PageSink/IO/
runtime/memoria. Fuentes, candidata03, cuotas, presupuestos, reservas,
capture_inputs y autoridad/destino intactos. Sin recursos reservados, contactos
externos, proveedores, credenciales, consumo, activación, promoción, despliegue
o D6. No se inspecciona ni limpia dev/run_data/D4.
