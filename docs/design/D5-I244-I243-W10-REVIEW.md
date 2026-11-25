# I244 — W10 revisado; congelación efectiva pendiente

La revisión documental de W10 de I243 encuentra consistentes sus requisitos de congelación final con I223, CE08 y los contratos/schemas I191. No se identifica un nuevo defecto documental. **Se mantiene la no admisión**: faltan los cuerpos, autores y autenticaciones reales, las diez reconciliaciones y las decisiones competentes. Ningún registro se congela o acepta; SD01 permanece activo y D5 abierto.

Fecha: 2026-11-25, Europe/Madrid. Base: `807187cfa35d96eab83aadbd2c86c9d9b7e556a3`.

El objeto es [W10 candidato de I243](../validation/D5-I223-W10-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json). Se conservan sus bytes y todos los antecedentes. El mismo asistente realiza la reconstrucción metodológica; esto no acredita identidad humana, independencia, competencia R01/R02/R03/R06 ni aceptación separada R08.

## Resultado del contraste

| Objeto | Resultado documental | Pendiente real |
|---|---|---|
| Contrato W10 | Entregables, ocho dependencias W02–W09, salidas y restricciones coinciden con I223 | Autoridad de entrada y dependencias aceptadas |
| Cuatro registros | Orden actor_registry → image_manifest → caller_identity → platform_custody preservado | Cuerpos auténticos completos y aceptación/freeze |
| Schemas y campos | Schemas exactos; 8/26/13/14 slots, total 61, sin valores reales | Restricciones y evidencia efectiva de cada cuerpo |
| Caps y listas | Caps 98 304/98 304/8 192/16 384; preparadores 1..16, actores/claves ≤64, dependencias ≤128 | Bytes/conteos completos y fit comprobado sin recorte |
| Autores y roles | Política W02, separaciones y autores W05–W09 conservados | Canonicalización, competencia, appointments y decisiones genuinos |
| DAG e invalidación | Orden y descendientes reconstruidos independientemente | Autenticidad, currentness y revisión de cambios reales |
| Reconciliación W09 | Diez comparaciones exactas vinculadas a los antecedentes | Hechos y hashes comparados, cuerpos y aceptación |

Los 61 slots son requisitos documentales, no registros positivos. Sus valores, cuerpos canónicos, hashes, tamaños, epoch, vigencias, providers/custodia, closures de evidencia y reviews permanecen null; actual_frozen y accepted siguen false. Los caps no se aplican como cuotas ni prueban heap, CPU o completitud. Los ocho schemas auxiliares mantienen las restricciones anidadas y la evidencia detrás de cada referencia.

Se contrastan diez reglas I191 y seis políticas seleccionadas de CE08, sin promover afirmaciones históricas de disponibilidad de otros dossiers a hechos actuales. Las listas deben ser completas, ordenadas y únicas; no se truncan, amplían cuotas o crean personas/records sintéticos para caber. Sus conteos reales son desconocidos, no cero. El límite de un índice tipado no limita automáticamente la evidencia subyacente o su coste.

## Autores, fuentes y autenticación

W02/CE03 conservan intake provisional, sin completitud final o preaprobación de autores futuros. El registro final exige autores efectivos W05–W09, providers y todos los preparadores del scope aceptado, incluidas contribuciones posteriores relevantes, con identidad/aliases, competencia, enrollment, appointments y custodia auténticos. El registro se prepara primero una vez conocidos esos sujetos y verificada la autoridad de identidad previa.

Las ocho exclusiones S01, cuatro separaciones adicionales de custodia y restricciones sobre source author y claves de emisor/aceptante se mantienen dentro de catorce requisitos. R01/R02 pueden coincidir sólo bajo cualificación genuina y dominios de rol separados; no se añade exclusión general. El principal software, una clave, una cuenta Git, un hash documental o un asistente no sustituyen identidad humana, autoría o independencia.

Las seis fuentes y sus mappings reales deben coincidir con la imagen y su clausura completa de intérprete, loader, stdlib, frozen, native y crypto. README conserva DOCUMENT; pertenecer al manifiesto no demuestra cargar tests o runner. El digest de imagen no sustituye la identidad runtime. Se conservan las constantes de perfil/protocolo/salidas/transporte/gramática y la selección de custodia, sin que nombrarlas pruebe implementación o se incorpore el propio hash futuro de imagen/manifiesto/bundle.

## DAG, hashes y vigencia

La reconstrucción usa las aristas de I191 y verifica que cada padre precede al hijo en el orden topológico. Un cálculo separado por adyacencia inversa reproduce los descendientes afectados de anchor, registro, imagen, caller y plataforma. Es una comprobación documental de dependencias, no prueba de autenticidad, progreso, currentness, aceptación o congelación.

Ninguno de los cuatro registros actuales depende de C, acceptance, bundle, Q, root, claim o recibo futuros. Los hashes requieren cuerpos reales completos y SHA256(JCS) en los dominios exactos; no sirven path hashes, placeholders, ceros o previsiones. Registro/imagen/caller/plataforma deben reconciliar requester, principal/constructor, dominio, recursos, hashes cruzados, epoch y vigencias.

Se conserva not_before < expires_at, lifetime ≤3600 y error de reloj ≤5 segundos, junto a trusted-now, epoch y revocación conocida en cada frontera. Reloj, currentness, vigencias y snapshots reales permanecen pendientes. La fecha del documento y el reloj del host no son evidencia del runtime. No se crea snapshot, se extiende expiry por cache/plan ni se habilita stale/TOFU o lookup oculto; tampoco se promete descubrimiento instantáneo de toda revocación.

## Reconciliación e invalidación

Las diez filas enlazan exactamente identidad/autores, fuentes/imagen/runtime, caller/constructor/dominio, plataforma/servicio/reloj/ledger, scope de operandos/atomicidad, heap/vidas/capacidad, trabajo/unidades/costes, fases/reservas, BASIS/índices/E01–E05 y autenticación previa a W09. Los hechos baseline y de freeze, sus comparaciones y la revisión de paquetes afectados siguen null; same_facts_verified y accepted permanecen false.

W10 sucede a W09 y no puede autenticarlo retrospectivamente ni convertirse en su dependencia inversa. El baseline actor/imagen/caller/plataforma, autores y cuerpos genuinos deben preceder a la aceptación de recursos. Las futuras firmas CE10 no pueden ser su única autenticación prevista. El freeze debe reconciliar el mismo source/runtime/image/caller/domain/resource scope, actores, autores, políticas, supuestos y hashes.

Cambiar autores, aliases, cuerpos, fuentes, imagen/runtime, constructor/dominio, plataforma/servicio/recurso, epoch/clave o política/schema detiene el avance e invalida los dependientes. Anchor/clave requieren volver a la política de anchors antes del freeze dependiente. Se recualifican y revisan competentemente W02–W09 y los paquetes posteriores afectados antes de progresar; no hay reutilización automática de hashes/pruebas, refresh aplicado o rebind activo de capture_inputs.

Los costes añadidos por nueva evidencia/custodia, memoria/registry, lookup/freshness/crypto, copias, native/IO y salidas permanecen dentro de ambos Readers y la composición global. Originales/native, hijos, fallos/cleanup y tracebacks siguen en scope. Un cambio de costes, hipótesis o grafo exige revisar cotas completas de heap/trabajo/servicio/fases/Reader. Nada es gratuito por ser offline, y los presupuestos no prueban capacidad, servicio o éxito en 900. No se cambian cuotas, reservas o recursos reservados.

W11 conserva C y acceptance; W12 bundle/mapping y W13 gates. CE11 no depende del recibo CE12. Se preservan los prerrequisitos finales I223 sin emitir C/Q/root/claim/recibo o autoridad. La revisión tampoco acepta las pruebas BASIS/index/E01–E05 que siguen pendientes.

## Comprobación y publicación

La [reconstrucción](../validation/D5-I244-I243-source-reconstruction.json) registra 28 criterios y 1017 pins contra los blobs del commit base. El [dictamen](../validation/D5-I244-I243-documentary-review.json) conserva los 42 rechazos documentales de I243 y añade veinte sobre orden, schemas/campos, caps/listas, constantes/mapping, DAG/descendientes, reconciliación, vigencia/reloj, invalidación, costes y fases diferidas.

El auditor contrasta fuentes primarias y pointers JSON; reproduce el candidato y la preparación I243 sin invocar mains históricos ni nuevas proyecciones de presencia. El [sello](../validation/D5-I244-integrity.json) preserva 709 archivos publicados y los cuatro artefactos distintos del propio sello.

```text
python3 docs/validation/D5-I244-audit.py
PASS_STATIC_SOURCE_ONLY_W10_REVIEW_FINAL_ANTECEDENTS_MISSING_NOT_FROZEN_NOT_ADMITTED
```

Harness de runtime: **N/A**. Sólo documentos, Git, hashes, metadatos y comprobaciones documentales propias en memoria. Sin ejecutar, importar o compilar producto/componentes, discovery/tests, build, crypto/codec positivos, firma, keygen, inscripción, provisión, benchmarks, probes o muestreos de reloj/CPU/IO/schedule/plataforma/servicio/ledger/claim/replay/procesos/endpoints. Sin selección/configuración de identidad, política, claves o servicio, contactos o nuevos helpers/canales/inputs/outputs. Sin cuotas, reservas, bindings, autoridades o destinos nuevos. No se inspecciona ni limpia dev/run_data/D4 y no se reanudan I86/I89/I92.

Se mantiene I122 IMPLEMENTED_NOT_ADMITTED, PJC115-R2 sin habilitar, E06 NOT_RUN, cero paquetes reales aceptados, cero gates de prelaunch cerrados y cero obligaciones E01–E05 cerradas. D5/H07 abiertos e IR03 NOT_READY. Publicar no congela, autentica, acepta ni autoriza ejecución.

Unidad documental de cinco archivos; se declara el exceso de 400 líneas por trazabilidad y preservación. Reversión limitada a retirar exactamente:

- `docs/design/D5-I244-I243-W10-REVIEW.md`
- `docs/validation/D5-I244-I243-source-reconstruction.json`
- `docs/validation/D5-I244-I243-documentary-review.json`
- `docs/validation/D5-I244-audit.py`
- `docs/validation/D5-I244-integrity.json`

El siguiente paquete documental I223 es W11, conservando la falta de evidencia y aceptación reales de sus antecedentes. La congelación y cierre efectivos siguen requiriendo las pruebas y decisiones competentes pendientes; el commit y push I244 no las sustituyen.
