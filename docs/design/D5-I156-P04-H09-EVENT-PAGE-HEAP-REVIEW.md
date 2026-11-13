# I156 — H09 revisado, sin cota completa ni ajuste demostrado

Fecha: 2026-11-13, Europe/Madrid. Base publicada:
`9fbbb68f71cfe2be673a9ad555fff4dd3b454ccd`.

**La revisión confirma el dictamen de insuficiencia de P04-H09.** El expediente
negativo es documentalmente coherente y no requiere cambiar H09. El heap completo
de chunks, cuerpos pendientes y flush sigue sin prueba: upper, ajuste a
**201326592 bytes (192 MiB)** y slack desconocidos. E02 permanece abierta;
PFC126-CANDIDATE-03/I122/PJC115-R2 mantienen la no admisión. H09 y el presupuesto
candidato conservan sus bytes, sin aplicar cuotas ni reservas.

## Ruta de revisión

1. Leer los quince controles y nueve disposiciones de campo en la [revisión I156](../validation/D5-I156-P04-H09-documentary-review.json).
2. Contrastar blobs, vectores y relaciones en la [reconstrucción I156](../validation/D5-I156-P04-H09-source-reconstruction.json).
3. Consultar [H09](../validation/D5-PFC126-03-E02-H09.json) para clases requeridas, dependencias y fronteras pendientes.

Este mismo asistente preparó I155. El recorrido separado del AST aporta
contraste documental, sin acreditar independencia de actor/organización,
autoridad de custodio o aceptación independiente de memoria.

## Procedencia y alcance de las relaciones

La reconstrucción concuerda con **188 pins**, doce proyecciones JSON, 79 fuentes,
21 anclas y los vectores sintácticos por archivo/globales. Los once registros de
expresiones conservan cinco asignaciones a memo, dos sitios return value y dos
drains de finalización. Son sitios de fuente, no objetos o invocaciones vivos.

| Relaciones clasificadas | Qué permiten comprobar |
| --- | --- |
| Encode/body y controles posteriores | Construcción antes de las comprobaciones seleccionadas, conservando planning y otros controles anteriores |
| Flush anterior, reference y cola | Orden del flush previo al nuevo append y de reference antes de encolar el body |
| Cola/reset y tuple/publish | Encolado antes de reset de chunks y tuple local antes de publicar el draft |
| Publish/IO y events/reset de writes | Orden de publicación, escritura fuera del lock y reset de la lista publicada |

Las diez relaciones incluyen guardas, cargos, publicación y reset; no son diez
asignaciones anteriores a toda guarda ni pruebas de liberación. El body contiene
encode de header, slice, join y concatenaciones antes de los controles de página
y total. Que exista una cota de bytes aceptados no suministra el almacenamiento
pico anterior a un rechazo ni el workspace nativo del runtime seleccionado.

## Memo, writes y finalización

Las ramas dict/list/tuple/set/frozenset y el fallback escalar concuerdan con H09.
Bajo sus bindings/precondiciones, el fallback no recopia bytes mediante esas
ramas. No paga headers de contenedores, memo y ocurrencias de punteros ni permite
descontar witnesses. Tampoco se infieren N copias físicas del payload por N lotes.

Se contrastan draft._memo, body encolado y reset de chunks. El reset no elimina
por sí solo las listas retenidas por memo ni todos los callers/errores. La
retención histórica permanece en cobertura; no se afirma retención eterna.

En _atomic, writes=tuple(...) precede a _publish dentro del lock de metadatos.
write_all aparece después de salir de ese lock; el decremento pendiente precede
al retorno. _publish resetea la lista de writes de events, sin demostrar que
desaparezcan las raíces locales writes/body/draft o las retenidas por errores.
No se deduce serialización de todas las vidas del worker o liberación completa.

La finalización contiene drain, close mediante _atomic(seal=True) y otro drain.
_drain comprueba el contador pendiente. Esa secuencia de protocolo no prueba
colección global, liberación nativa, ausencia de referencias locales o pico de
heap. Se comprueba fuente sin ejecutar el observador o sus componentes.

## Payload heredado y carencias

| Aritmética condicionada I123/I124 | Bytes |
| --- | ---: |
| 32×2097152 de páginas candidatas totales | 67108864 |
| Cuerpos pendientes, payload | 67108864 |
| Todos los chunks históricos distintos, incluido memo | 67108864 |
| Cuerpos + chunks distintos, payload | 134217728 |
| 201326592−134217728, aritmética solamente | 67108864 |

**64 MiB de diferencia no son slack verificado.** La subcota de 128 MiB conserva
su alcance exitoso condicionado y los chunks históricos de memo. Excluye headers,
listas/mapas/tuplas, capacidades/growth, punteros, join/concat, Unicode/codecs y
soporte nativo. No es prueba completa del propietario de 192 MiB, cota global
del observador ni cobertura completa de intentos fallidos de encode/flush/IO.

Doce requisitos mantienen **48 valores null** de cardinalidad, tamaño, pico y
vida completos. Las diez fronteras H01–H08/H10–H11 siguen abiertas: baseline
nativo, originales, roots, clones/memo, carriers, proyección/digest, codecs,
Reader, salida y overhead precisan asignación explícita de bloques y vidas.
H11 no es reserva libre; sin nuevas cuotas por página/thread o crédito por alias,
interning, fusión de witnesses o GC supuesto. Se admite sobreconteo conservador
explícito sólo con cobertura completa, sin asumir un tamaño faltante como cero.

F≤52018, S≤1759, 53777 lotes y 53778 generaciones con inicial conservan el
contexto condicional P01/I124, sin dar tamaños o máximo completo de storage IO
pendiente. P01 independiente, P02 exacto y P03 siguen pendientes. La carencia
se refiere al material suministrado, sin afirmar ausencia global o inviabilidad.

## Disposición y publicación

Los nueve campos conservan dos definiciones documentales y siete disposiciones
insuficientes. Los cuatro criterios E02 no cierran. Upper, ajuste y slack null;
no se prueba sobrepresupuesto real, memoria ilimitada, capacidad o servicio.
Ocho outputs siguen ausentes, sin iniciar otro paquete.

E01–E05 abiertas; E06 separado, pendiente, NOT_RUN y sin permiso de ejecución.
I122 conserva IMPLEMENTED_NOT_ADMITTED; sin SOURCE_CAPACITY_VERIFIED, propuesta
o captura. D5/H07 de cierre abiertos e IR03 NOT_READY. P0 conserva
83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados y brechas/
obligaciones reales pendientes. I86/I89/I92 INVALID_CAPTURE sin reanudar ni mezclar.

`python3 docs/validation/D5-I156-audit.py`: **PASS_STATIC_SOURCE_ONLY**.
Verifica Git/JSON/AST y coherencia del dictamen negativo, con **258 archivos
publicados** e inputs heredados preservados. No prueba heap, ABI, vidas,
capacidad, CPU/tiempo o independencia.

Cinco archivos I156 forman una unidad: este documento, revisión, reconstrucción,
[auditor](../validation/D5-I156-audit.py) y [sello](../validation/D5-I156-integrity.json).
El diff supera 400 líneas por evidencia generada y auditoría autocontenida;
se informa el exceso sin comprimir código o retirar evidencia. Runtime harness:
N/A, sin cambio de comportamiento runtime. Rollback: retirar sólo los cinco
archivos enumerados en work_unit. Se audita antes del stage y después del commit,
con push y verificación de remoto efectivo y árbol limpio.

Sin producto/componentes importados, compilados o ejecutados, tests, benchmarks,
consumo de generadores, introspección, instrumentación o sondeos de PageSink/IO/
runtime/memoria. Fuentes, candidata03, cuotas, presupuestos, reservas,
capture_inputs y autoridad/destino intactos. Sin recursos reservados, contactos
externos, proveedores, credenciales, consumo, activación, promoción, despliegue
o D6. No se inspecciona ni limpia dev/run_data/D4.
