# I258 — revisión de A03/RQ03: fuentes, imagen, runtime y fases

**No se encuentran defectos documentales nuevos en A03/RQ03 de I257.** El dossier conserva las seis fuentes, la clausura y correspondencias de imagen/runtime, las políticas y la bifurcación entre artefactos genuinos existentes y gaps pendientes. A01/A02/A03 siguen sin aceptar, SD01 permanece activo y se mantiene la **no admisión**. RQ03 no se envía.

Fecha: 2026-11-25, Europe/Madrid. Base: `02cde01999cb79930d9bfc28e7a4cc1aa0dcd374`.

La revisión metodológica contrasta el [dossier I257](D5-I257-A03-RQ03-SOURCES-IMAGE-RUNTIME.md) con [I251](D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.md), W03 y sus fuentes normativas. El mismo asistente realiza esta revisión, sin actuar como R01/R06 competente o R08 separado. No se revisa código sucesor real inexistente ni se cualifican componentes o se recibe evidencia genuina.

## Dictamen de las fronteras

| Frontera | Resultado documental y límite |
|---|---|
| Antecedentes | A01/W01 y A02/W02 siguen sin aceptar. Los PASS de preparación/revisión no permiten enviar, contactar o iniciar intake positivo. A03 no autentica retrospectivamente a sus predecesores. |
| Seis fuentes | Paths, representación, cuerpos/bytes/digests/source_root/autores/custodia/mapping y cualificación se conservan como requisitos. Los cuerpos locales siguen ausentes; no hay hash predictivo o transferencia de I122. |
| Imagen frente a runtime | Se requieren imagen externa auténtica y runtime identity completos por separado, con correspondencia source/binario/imagen y provenance. Un digest de imagen no sustituye P02 ni prueba implementación. |
| Clausura y políticas | Ocho clases CL y siete políticas permanecen completas; los pins documentales fijan requisitos y no acreditan valores compilados, selección externa o conformidad real. |
| Baseline frente a fases diferidas | IM01–IM06 pertenecen al baseline W03. IM07–IM10 conservan sus consumidores W04, W05–W09 y W10, sin nueva dependencia inversa. |
| Material existente o gaps | Sólo artefactos completos existentes, genuinamente calificados y con autoridad/provenance propias permiten considerar aceptación. SR06 registra gaps y trabajo separado; no acepta A03 ni autoriza producir lo ausente. |
| Handoff | A04/RQ04 permanece detenido y exige A02/A03 genuinos, con sus propios límites. Publicar I258 no habilita contacto, ejecución o cierre D5. |

La falta local de material no demuestra ausencia global o inviabilidad. Tampoco permite designar proveedor, prometer fechas, tratar ausencias como cero o fabricar cuerpos/autoridad. El usuario autorizó esta revisión documental y su publicación, sin alterar el bloqueo de los lotes reales.

## Fuentes, representación y scope

Se contrastan las seis rutas exactas bajo `testing/prospective_capture_joint_prp181/`: `README.md`, `atomic.py`, `capture.py`, `run_joint_lab.py`, `test_joint_capture.py` y `worker.py`. Cada fila conserva su enlace W03 y los slots reales ausentes de cuerpo, bytes/digest/source_root, miembro/representación/digest de imagen, mapping y cualificación.

README sigue siendo DOCUMENT; las otras cinco rutas conservan su política permitida PYTHON_SOURCE/FROZEN_CODE/DOCUMENT sin representación efectiva seleccionada. La pertenencia de tests/runner a una imagen no prueba carga, import, ejecución o cualificación. El techo total 262144 debe justificarse con seis cuerpos reales completos; no es suma de fuentes ausentes o capacidad disponible, ni permiso para recortar o ampliar scope.

El scope histórico480 más seis conserva la prohibición de helpers de repositorio no enlazados, lecturas extra heredadas, canales/fds/argv/inputs/outputs ocultos o confianza ambiental. Las bibliotecas y dependencias runtime requieren su clausura/provenance propia completa; el límite del scope de fuentes no permite omitirlas. No se añaden fuentes ni se inspecciona el runtime del host.

## Imagen, runtime y políticas

El digest de bytes de imagen y la identidad runtime son conceptos distintos. Los dossiers P02/P03 históricos, sus dictámenes negativos y las observaciones de I122 no cualifican el sucesor. El Python/OS/entorno del auditor documental tampoco es evidencia del target y no se muestrea para adoptarlo como tal.

CL01–CL08 conservan intérprete/version/config/ABI y stdlib/builtin/frozen/native/crypto; loader/resolución de carga/primera entrada; dependencias transitivas/allocator/GC/kernel; receta/toolchain y equivalencia source/binario/build/imagen; identidad efectiva del target; miembros/dependencias de imagen; compatibilidad P03 runtime/plataforma; y dominios relevantes de reloj/procesos/servicio. Un inventario o hash afirmado no aporta la derivación/provenance genuina que sigue faltando.

Las dependencias deben ser completas, disponibles, ordenadas y únicas. No se cortan a128 para satisfacer el índice; el cap 98304 del manifest final tampoco prueba fit de cuerpos subyacentes, heap, CPU o servicio. Esos límites candidatos no se aplican al wrapper documental ni se cambian por esta revisión. La validación/freeze del cuerpo final sigue en W10/CE08.

Se contrastan los siete campos de política con W03 y con los hashes reales de los documentos fijados: perfil, protocolo, salida, contrato/gramática de transporte y pack/contrato de custodia. La coincidencia documental o de constantes no prueba implementación o selección externa. Se mantiene la prohibición de seleccionar política desde el propio bundle y de embebido del digest propio futuro imagen/manifest/bundle.

## Orden de evidencia y fases

| Requisitos | Consumidor conservado |
|---|---|
| IM01–IM06 | W03/CE04: fuentes, mappings, clausura/build, imagen/runtime separados, políticas y baseline de entrada inmutable |
| IM07 | W04/CE05: caller/constructor/origen |
| IM08 | W04/CE06: enforcement completo de plataforma |
| IM09 | W05–W09/CE07: recualificación 179/321/12/30 y join de recursos |
| IM10 | W10/CE08: freeze final del manifest/antecedentes |

Cada una de las diez filas se contrasta también con su fuente normativa IM. El baseline exige primera entrada inmutable auténtica antes de código no confiable; no selecciona/invoca constructor ni prueba por sí solo dominio/canales/enforcement de W04. Las cuatro filas diferidas no se eliminan y tampoco requieren aceptación downstream como antecedente nuevo de W03.

La identidad genuina del artefacto imagen y el registro final de custodia image_manifest son distintos. No exigir manifest final ya congelado en esta fase no dispensa la imagen real, runtime completo o equivalencia exigidos por el baseline. Autores/cuerpos y hechos efectivos deben estar autenticados antes de aceptar W09; W10 después reconcilia esos mismos hechos en orden actor→imagen→caller→plataforma antes de C. No se permite autenticación retrospectiva, completitud anticipada o preaprobación de futuros autores.

## Retornos, aceptación y gaps

Los seis retornos cubren autoridad/antecedentes; fuentes/mappings; imagen/runtime/build; políticas/entrada; inventario/reviews/decisión; e informe de gaps. Los tres entregables originales W03 mantienen sus textos exactos y cobertura SR02/SR03/SR04, con SR01 de autoridad y SR05 de revisión. Los dieciséis criterios y tres salidas permanecen pendientes sobre el mismo scope y cuerpos.

La ruta de artefactos existentes exige fuentes ya calificadas, provenance autorizada y todas las correspondencias/cuerpos disponibles, sin obtener nueva cualificación por esta solicitud. La ruta SR06 exige identificar el elemento/ámbito ausente, requisito/dependiente afectado y alcance/autoridad separados de implementación/build/cualificación/medición necesarios. Registrar ese gap no equivale a completarlo, aceptar el lote o autorizar un run/build. Otro PASS documental tampoco lo sustituye.

R01/R06 deben aportar reviews competentes genuinos y R08 una decisión separada elegible con motivos por requisito/salida, bajo las reglas heredadas de humanos, competencia, appointments, claves y exclusiones. El mismo asistente/auditor no acredita esas funciones. Se siguen exigiendo todos los cuerpos/referencias reales, locators inmutables/bytes/digests/autores/providers/custodia/provenance, derivaciones, unidades y todos los supuestos, currentness/validez y disposiciones faltantes/rechazadas/aportadas. Las plantillas, hashes, firmas, flags o índices no acreditan verdad por sí solos.

El inventario recibido permanece null, las listas aportadas/rechazadas vacías y las evaluaciones reales a cero. Cambios de autor/body/source/image/runtime/epoch/key/policy/scope invalidan afectados antes de avanzar, sin transferencia automática de cualificación, prueba, aprobación o aceptación ni refresh/rebind activo. A04 sólo podrá considerarse con A02 y A03 genuinamente aceptados y sus límites propios.

## Costes y no admisión

Ambos Readers y el join global mantienen costes completos por intento de lookup/freshness/identidad/firma/medición/native/IO/copias/registry/recibo/salidas/fallos/cleanup y nuevas rutas dentro de heap/trabajo/servicio/fases. Provenance de build y trabajo offline no vuelven gratuitos esos costes. Caps, presupuestos o 262144 no prueban disponibilidad, heap completo, CPU/servicio o éxito900; no se cambian cuotas/reservas o se reservan recursos.

CE12 sigue privado, diferido y no autorizado. E06/payload/Q/root/admisión/claim/recibo finales no se añaden como nueva condición de aceptación prelaunch. Se conservan cuatro prerrequisitos externos antes del claim y claim/construcción protegida antes del recibo; claim no es su propia precondición y estados inciertos/parciales/expirados/fallidos no habilitan retry gratuito.

Se mantienen cero lotes/gates/obligaciones cerrados, treinta gates pendientes y E01–E05 abiertas. I122 sigue IMPLEMENTED_NOT_ADMITTED, CP07 falso, atomicidad correlacionada sin verificar, componentes/E06 NOT_RUN, PJC115-R2 sin habilitar, D5/H07 abiertos e IR03 NOT_READY. No se crean fuentes/runtime records, C/Q/root/bindings finales, autoridad/destino, mapping/claim/worker/recibo o recursos reservados.

## Verificación y publicación

La [reconstrucción](../validation/D5-I258-I257-source-reconstruction.json) fija 1087 entradas contra los blobs del commit base y registra 26 criterios. El [dictamen](../validation/D5-I258-I257-documentary-review.json) reproduce candidato/preparación I257 sin llamar mains de publicación históricos, conserva sus 41 rechazos documentales y añade 32 mutaciones en memoria sobre antecedentes, fuentes, clausura, políticas, fases, gaps/autoridad, cobertura, costes y aceptación. El [sello](../validation/D5-I258-integrity.json) preserva 779 archivos publicados y cuatro artefactos propios distintos del sello.

```text
python3 docs/validation/D5-I258-audit.py
PASS_STATIC_SOURCE_ONLY_A03_RQ03_REVIEW_PREDECESSORS_AND_GENUINE_SOURCES_IMAGE_RUNTIME_PENDING_NOT_ADMITTED
```

Harness de runtime: **N/A**. Sólo JSON/Git/hashes/pointers/fuentes/clausura/políticas/fases y comprobaciones documentales propias. Sin importar/compilar/ejecutar producto/componentes, discovery/tests/E06, build, medición, benchmarks, crypto/codec positivos, firma/keygen/enrollment/provisión/contactos/configuración registry/mapping/reloj/ledger/servicio o probes CPU/IO/procesos/endpoints/replay/crash/restart. Sin cuotas/reservas/capture_inputs o nuevos inputs/outputs/helpers/canales. No se inspecciona/limpia dev/run_data/D4 ni se reanudan I86/I89/I92.

Una unidad documental con exceso de 400 líneas declarado por reconstrucción, pins y preservación; sin PR solicitado. Reversión limitada a retirar exactamente:

- `docs/design/D5-I258-I257-A03-RQ03-REVIEW.md`
- `docs/validation/D5-I258-I257-source-reconstruction.json`
- `docs/validation/D5-I258-I257-documentary-review.json`
- `docs/validation/D5-I258-audit.py`
- `docs/validation/D5-I258-integrity.json`

I258 termina esta revisión documental. La autoridad/aceptación genuina A01/A02 y los artefactos/decisiones genuinos A03 siguen pendientes; publicar no satisface los hitos materiales ni autoriza enviar solicitudes o producir lo ausente.
