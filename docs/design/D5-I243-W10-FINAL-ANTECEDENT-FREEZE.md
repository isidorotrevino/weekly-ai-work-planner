# I243 — W10 preparado; antecedentes reales sin congelar

W10 queda preparado como expediente documental de requisitos de congelación final de antecedentes de I223. **Se mantiene la no admisión.** Los registros, autores, cuerpos, autenticaciones previas, reconciliaciones y aceptaciones reales siguen pendientes. No se congela ni genera ningún snapshot operativo; SD01 permanece activo y D5 abierto.

Fecha: 2026-11-25, Europe/Madrid. Base: `e9a8c2e3f77b866e15c88bbf7aefae5239a199eb`.

El [candidato W10](../validation/D5-I223-W10-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json) vincula literalmente entregables, dependencias W02–W09, tres salidas, rechazos y restricciones de I223. Reutiliza requisitos documentales CE08/I191, sin transferir aceptación ni copiar como actuales las afirmaciones históricas sobre existencia de dossiers posteriores. Los antecedentes conservan sus bytes y fechas.

## Orden y evidencia exigidos

| Orden | Registro requerido | Campos requeridos de primer nivel | Cap candidato del cuerpo |
|---|---|---:|---:|
| 1 | actor_registry | 8 | 98 304 bytes |
| 2 | image_manifest | 26 | 98 304 bytes |
| 3 | caller_identity | 13 | 8 192 bytes |
| 4 | platform_custody | 14 | 16 384 bytes |

Los 61 slots permanecen sin valor real, al igual que cuerpos canónicos, hashes, tamaños, epoch, vigencias, autor/provider/custodia, evidencia referenciada y reviews. No son cuatro registros positivos. Los caps de serialización son requisitos candidatos sin aplicación como cuotas, y los tamaños reales son desconocidos, no cero. El conteo de campos de primer nivel no demuestra restricciones anidadas, completitud de evidencia, heap, CPU o fit.

Se incluyen ocho definiciones auxiliares exactas de I191 y diez reglas contractuales CE08. Las listas deben ser completas, canónicas, ordenadas y únicas: preparadores 1..16, actores y claves como máximo 64, dependencias como máximo 128. No se recortan para caber ni se inventan personas o preparation records. Todo cuerpo detrás de una referencia debe existir, ser auténtico y estar disponible, con bytes/digest, autor/provider/custodia, unidades, supuestos y validez completos. Los índices tipados no acotan por sí solos esa evidencia ni sus costes.

El auditor reconstruye el DAG I191 y sus descendientes afectados por cambios de anchor, registro, imagen, caller o plataforma. La aciclicidad es documental: no atesta autenticidad, currentness, aceptación o freeze. La secuencia registro → imagen → caller → plataforma requiere anchor/identidad y autenticación previa genuinos; no los crea la existencia de los schemas.

## Autores, identidades y políticas

Antes de la congelación real deben conocerse y autenticarse todos los autores efectivos W05–W09, providers, titulares de roles y preparadores documentales del scope aceptado, incluidas contribuciones posteriores relevantes. Deben constar aliases canónicos, competencia, appointments, custodia y claves genuinos. W02/CE03 siguen siendo intake provisional, sin declarar completitud antes de conocer autores ni preaprobar autores futuros. El registro final se prepara primero cuando esa evidencia esté disponible.

Se conservan los catorce requisitos de separación W02: ocho exclusiones S01, reglas de source author/emisor/aceptante y cuatro separaciones adicionales de custodia. R01/R02 mantienen la posible coincidencia bajo cualificación real y dominios de rol separados; no se introduce prohibición general. El principal software no sustituye a un humano para evadir exclusiones. Una cuenta Git, clave, etiqueta de asistente o hash de documento no acredita autoría humana, competencia o independencia.

W10 requiere revisiones genuinas R01/R02/R03/R06 y aceptación separada R08, con competencias y appointments reales. La preparación actual por el mismo asistente no satisface esas decisiones ni asigna identidades o contacta personas.

La imagen debe corresponder a las seis fuentes exactas, con mappings/digests auténticos y clausura completa de intérprete, loader, stdlib, frozen, native y crypto. README conserva DOCUMENT; pertenecer al manifiesto no demuestra que tests o runner se carguen. El digest de imagen no sustituye identidad de runtime y la imagen no incorpora su futuro hash de manifiesto/bundle.

Los schemas fijan constantes de perfil, protocolo, salidas, transporte, gramática y selección de custodia. Falta demostrar que una imagen real implemente esas políticas; nombrarlas no es implementarlas. No se añaden helpers fuera del scope histórico480/seis fuentes ni dependencias sin nueva revisión de grafo y costes.

## Hashes, vigencia y reconciliación W09

Los hashes de registros son SHA256(JCS del cuerpo real completo), y source_root el hash canónico de las source_bindings reales. No se sustituyen por path hashes, placeholders, ceros o predicciones. Caller, registro, imagen y plataforma deben coincidir en sus referencias cruzadas, requester, principal/constructor, dominio y resource scope; el epoch debe ser el mismo y las vigencias solaparse y estar actuales.

Se conservan not_before < expires_at, lifetime máximo 3600 segundos y error de reloj máximo 5 segundos, con trusted-now, epoch y revocación conocida en cada frontera. La fecha de este documento y el reloj del host no son evidencia del runtime. No hay fallback stale/TOFU, lookup oculto o garantía de descubrir instantáneamente toda revocación. Los snapshots genuinos se producirán sólo cuando la evidencia esté lista y bajo autoridad propia; un plan o cache no extiende su expiry. Aquí no se mide reloj ni se crea snapshot.

El ledger prepara diez comparaciones pendientes entre los hechos baseline autenticados que sostuvieron W09 y los propuestos para el freeze: autores/aliases/claves, fuentes/imagen/runtime, caller/constructor/dominio, plataforma/servicio/reloj/ledger, scope de operandos/atomicidad, heap/vidas/capacidad, trabajo/unidades/costes, fases/reservas, BASIS/índices/E01–E05 y autenticación antecedente. Cada valor, comparación y revisión real permanece null; same_facts_verified y accepted continúan false.

W09 exige hechos actor/imagen/caller/plataforma y autores/cuerpos auténticos antes de aceptar recursos. W10 sucede a W09 y no suministra retrospectivamente su única autenticación ni introduce una dependencia inversa de aceptación. Las futuras firmas CE10 no autentican su propio antecedente por pronóstico. El freeze debe reconciliar los mismos effective source/runtime/image/caller/domain/resource scope, actores, autores, políticas, supuestos y hashes.

Un nuevo autor, alias, cuerpo, fuente, runtime/imagen, constructor/dominio, plataforma/servicio/recurso, epoch, clave, política o schema relevante detiene el avance e invalida los digests, reviews y aceptaciones dependientes. Cambios de anchor/clave requieren volver primero a la política de anchors. Se recualifican y revisan competentemente los paquetes afectados W02–W09 y posteriores antes de avanzar. No hay reutilización automática de pruebas o hashes, recomputación aplicada ni rebind activo de capture_inputs.

## Recursos y fases posteriores

Las pruebas reales BASIS/index y E01–E05 permanecen sin aceptar. Cualquier nuevo cuerpo, contribución o mecanismo de custodia debe integrarse en los costes de memoria/registry, lookup, freshness, verificación crypto, copias, native/IO y salidas. Ambos Readers y su join global, originales/native, hijos, fallos/cleanup y tracebacks retenidos continúan en scope. Ningún coste se hace gratuito por llamarse offline.

Si cambian costes, hipótesis o grafo, se revisan de nuevo las cotas completas de heap, trabajo, servicio, fases y Reader. Los presupuestos no demuestran capacidad disponible, servicio o éxito en 900; no se cambian cuotas, presupuestos, reservas o recursos reservados. La no admisión tampoco demuestra inviabilidad.

W10 sólo prepara los cuatro antecedentes. W11 conserva la proyección de C y aceptación; W12 bundle/aprobaciones/mapping y W13 gates. C, acceptance, bundle, Q, root, claim y recibo no son antecedentes futuros exigidos para este freeze. CE11 no depende del recibo CE12. Se preserva la frontera final de I223, sin emitir ninguno de esos objetos ni autoridad operativa.

## Verificación y publicación

La [preparación revisada](../validation/D5-I243-preparation-review.json) registra cuatro cuerpos requeridos, 61 slots, ocho schemas auxiliares, diez reglas, seis políticas heredadas, diez reconciliaciones y cinco roles sin asignar. El [auditor](../validation/D5-I243-audit.py) verifica 1012 pins, schemas/pointers/DAG y requisitos negativos, reproduce reconstrucción y revisión I242 sin invocar mains históricos ni nuevas proyecciones de presencia, y rechaza 42 mutaciones documentales en memoria. El [sello](../validation/D5-I243-integrity.json) preserva 704 archivos publicados y los cuatro artefactos distintos del propio sello.

```text
python3 docs/validation/D5-I243-audit.py
PASS_STATIC_SOURCE_ONLY_W10_FINAL_ANTECEDENTS_MISSING_NOT_FROZEN_NOT_ADMITTED
```

Harness de runtime: **N/A**. Sólo documentos, Git, hashes, metadatos y comprobaciones documentales propias en memoria. Sin ejecutar, importar o compilar producto/componentes, discovery/tests, build, crypto/codec positivos, firma, keygen, inscripción, provisión, WCET experimental, benchmarks, probes, sampling de reloj/CPU/IO/schedule/plataforma/servicio, ledger, claim, replay, crash/restart, procesos o endpoints. Sin contactos, selección/configuración de identidad/plataforma/política/servicio, nuevos helpers/canales/inputs/outputs, cuotas, reservas, bindings, autoridades o destinos. No se inspecciona ni limpia dev/run_data/D4; no se reanudan I86/I89/I92.

I122 sigue IMPLEMENTED_NOT_ADMITTED, PJC115-R2 sin habilitar, E06 NOT_RUN, cero paquetes reales aceptados, cero gates de prelaunch cerrados y cero obligaciones E01–E05 cerradas. D5/H07 abiertos e IR03 NOT_READY. Publicar este expediente no congela, autentica, acepta o autoriza ejecución.

Unidad documental de cinco archivos, con exceso de 400 líneas declarado por trazabilidad y preservación. Reversión limitada a retirar exactamente:

- `docs/design/D5-I243-W10-FINAL-ANTECEDENT-FREEZE.md`
- `docs/validation/D5-I223-W10-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json`
- `docs/validation/D5-I243-preparation-review.json`
- `docs/validation/D5-I243-audit.py`
- `docs/validation/D5-I243-integrity.json`

El siguiente paso documental es revisar W10 y sus fronteras. La congelación efectiva y el cierre siguen exigiendo la evidencia y decisiones competentes pendientes; commit y push no las sustituyen.
