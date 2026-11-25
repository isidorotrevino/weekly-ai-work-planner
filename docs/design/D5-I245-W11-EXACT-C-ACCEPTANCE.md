# I245 — W11 preparado; C y aceptación reales pendientes

W11 queda preparado como expediente documental de requisitos de proyección exacta de C y acceptance de custodia del plan I223. **Se mantiene la no admisión.** W09/W10 no están aceptados; faltan hechos, valores, cuerpos, hashes, pruebas y decisiones genuinas. No se crea, emite, configura o acepta C ni un registro positivo de acceptance; SD01 permanece activo y D5 abierto.

Fecha: 2026-11-25, Europe/Madrid. Base: `cb96bff2667d476f19b1ddf8c2b24883b12cadbf`.

El [candidato W11](../validation/D5-I223-W11-EXACT-C-ACCEPTANCE-CANDIDATE.json) vincula literalmente los entregables, dependencias W09/W10, tres salidas, rechazos y restricciones I223. Contrasta los schemas C/acceptance y conserva CE09 y su revisión I216 como requisitos históricos, sin copiar como actuales sus afirmaciones de disponibilidad de otros dossiers. Los antecedentes mantienen sus bytes y fechas.

## Proyección requerida

| Objeto | Requisito preparado | Estado real |
|---|---|---|
| C | Schema cerrado v3 con 19 campos requeridos; cap candidato 8 192 bytes | Cuerpo, valores, bytes/digest y revisión null |
| acceptance | Schema cerrado con 27 campos requeridos; cap candidato 16 384 bytes | Cuerpo, evidencias y aceptación null |
| Tipos compartidos | 14 propiedades idénticas y seis definiciones transitivas | Compatibilidad estática de tipos; ninguna proyección real verificada |
| Valores compartidos | 13 igualdades de valores aceptados exactos | Valores/provenance sin aportar |
| validity | Mismo tipo, con contención de intervalo | Intervalos, currentness/revocación y prueba pendientes |
| Antecedentes | Cuatro hashes de registro/imagen/caller/plataforma reales de W10 | Sin cuerpos congelados o hashes aceptados |
| Evidencia previa | Cinco referencias basis/recursos/R01/R02/R08 | Cuerpos y decisiones genuinos pendientes |

Hay quince nombres comunes entre los dos schemas. `schema` tiene constantes distintas y no pertenece a los catorce tipos idénticos. `validity` comparte tipo, pero su relación de valor es contención; las otras trece propiedades exigen valores aceptados exactos. Las seis definiciones compartidas —identity, proposal_scope, sha256, trusted_key, validity y verifier_profile— se reconstruyen transitivamente por referencias locales, comparando ambos contratos.

Las 46 exigencias de campo son slots documentales fuera de cuerpos positivos. Todos sus valores reales siguen null, incluso los de campos con constantes conocidas: conocer el schema no aporta un hecho auténtico de C. Los caps no se aplican como cuotas ni demuestran tamaño medido, completitud de evidencia, heap/CPU o fit. No se usa una igualdad de tipos como aceptación de valores.

## Valores, constantes, identidad y scope

C conserva exactamente sus constantes de schema, repository_id, root_path y offline_key_status del perfil02. No se añade hash de bundle, campo nuevo o binding a un root futuro. acceptance conserva `IDENTITY_IMAGE_CUSTODY_ONLY_NOT_RESOURCE_OR_CAPTURE_ADMISSION`: su decisión es exclusivamente custodia, sin admisión de recursos o captura.

Roles, todos los preparadores, source author, requester, issuer/acceptor y claves deben proceder del registro canónico genuino con competencia, appointments y aceptaciones previas. Las referencias de preparadores deben coincidir por actor_id, record_id y SHA256(JCS del preparation record completo), con evidencia real de contribución y los mismos perfil/schema, sin recorte. Se conservan las ocho exclusiones S01, cuatro separaciones adicionales de custodia y las demás reglas W02; R01/R02 sólo pueden coincidir bajo las condiciones de cualificación y dominios de rol exigidas.

Requester debe coincidir con caller accountable_requester_actor_id. Principal software, constructor, dominio, registry e imagen/plataforma deben tener vinculación auténtica; el software no es un alias humano para eludir exclusiones. Una cuenta Git, asistente, clave o etiqueta de rol no acredita identidad o independencia. La preparación actual del mismo asistente no satisface revisión competente R01/R02/R03/R06 ni aceptación separada R08.

Source/runtime/image/profile, BASIS/index, resource/suite scope, epoch, roles y claves deben concordar con los antecedentes aceptados W09/W10. El digest de imagen no sustituye identidad runtime. Falta una reconciliación genuina del mismo baseline, autores, cuerpos, políticas y supuestos de recursos; no se transfieren pruebas automáticamente. Nuevos contribuidores, cuerpos, fuentes, imagen/runtime, dominio/recurso, epoch/clave/política invalidan los dependientes afectados y exigen nueva revisión, sin refresh o rebind activo aplicado aquí.

## Digest y evidencias de aceptación

El digest requerido es SHA256(JCS del C genuino completo), no un hash de path, documento modelo, parte del cuerpo o valor predictivo. acceptance debe fijar ese digest y los cuatro hashes exactos de actor_registry, image_manifest, caller_identity y platform_custody. Todos los cuerpos, digests y comparaciones reales permanecen pendientes.

Las cinco evidencias previas son prior_basis_acceptance_evidence, prior_resource_acceptance_evidence, R01_runtime_acceptance_evidence, R02_platform_acceptance_evidence y R08_separate_acceptance_evidence. Deben identificar cuerpos completos disponibles y auténticos con bytes/digest, autor/provider/custodia, scope, unidades, supuestos, validez y revisiones genuinas aceptadas. La futura firma CE10, E06 o un root final no sustituyen evidencia previa ausente.

acceptance **no tiene firma propia**. La expresión de K12 sobre firmar el digest se interpreta con el schema cerrado y la revisión I216: las tres aprobaciones por dominio R01/R02/R08 de CE10 cubren el mismo signed_core, que incluye acceptance con trust_context_sha256. La cobertura de C es indirecta por ese digest. No se añade el cuerpo C a signed_core ni una firma al registro. Contrato/schema y anchors se seleccionan independientemente, sin convertir claves declaradas en C/bundle en anchors por sí mismas.

El bundle tampoco tiene un campo validity independiente. La validez/currentness efectiva de PJ12 corresponde a sus cinco registros, incluido acceptance, con C contenido en sus intervalos aceptados. No se inventa una vigencia del bundle ni se exige un bundle futuro real como única autenticación previa de W11.

## Contención, reloj y predicados diferidos

C debe estar contenido en las vigencias actuales relevantes de antecedentes y acceptance, sin forzar igualdad de extremos. El epoch sí debe concordar. Se exige not_before < expires_at, lifetime ≤3600 y `error_plataforma <= C.clock_error_seconds <=5`, con trusted_now-error >= not_before y trusted_now+error < expires_at en cada frontera pertinente. No se selecciona o mide reloj ni se produce snapshot; la fecha del cliente o reloj del host no prueba currentness del runtime.

Se conservan epoch conocido, revocación conocida y ausencia de TOFU, stale-cache o lookup oculto. No se promete descubrimiento instantáneo de toda revocación. Los valores de error, intervalos, trusted-now y prueba de contención permanecen null; ningún marcador o hecho ausente se convierte en cero.

El ledger conserva PJ01–PJ12 de CE09 sin evaluarlos. PJ01–PJ10 son requisitos de W11: identidad/separación, preparadores, caller/requester, imagen/runtime, pruebas previas, epoch/contención, reloj, constantes, digest/hashes y custodia/evidencias. PJ11–PJ12 corresponden a W12: cobertura de bundle/aprobaciones/anchors y validez efectiva/proyección de C. Esta distribución no exige aceptación de W12 como prerrequisito de W11.

## Recursos, autoridad y fases posteriores

Los costes de cuerpos de evidencia, registry, C/acceptance, copias, hashing/JCS, lookup/freshness, identidad/crypto y salidas siguen dentro de la composición global de heap, trabajo, servicio y fases, incluidos ambos Readers, fallos y cleanup. No son gratuitos por ser offline. Si se añaden mecanismos, cuerpos o lecturas, requieren revisión del grafo y cotas completas. Los límites C8192/acceptance16384 no prueban fit ni activan cuotas; no se cambian presupuestos, reservas o recursos reservados.

W11 requiere hechos y pruebas aceptados W09/W10; la revisión documental de W10 no equivale a congelación real. W12 conserva bundle, aprobaciones y mapping; W13 gates y las fases finales E06/payload/Q/root/claim/recibo permanecen separadas. CE11 no depende del recibo CE12. Se conserva la frontera final I223 sin emitir C wire, Q/request, bundle, mapping, root, claim, recibo o autoridad.

## Comprobación y publicación

La [preparación revisada](../validation/D5-I245-preparation-review.json) registra 19/27 campos, catorce tipos, trece proyecciones exactas y contención, seis definiciones transitivas, cuatro hashes, cinco evidencias, doce predicados y seis reglas contractuales. El [auditor](../validation/D5-I245-audit.py) verifica 1022 pins, tipos/referencias/pointers y estados negativos, reproduce reconstrucción y revisión I244 sin invocar mains históricos ni nuevas proyecciones de presencia, y rechaza 42 mutaciones documentales en memoria. El [sello](../validation/D5-I245-integrity.json) preserva 714 archivos publicados y los cuatro artefactos distintos del propio sello.

```text
python3 docs/validation/D5-I245-audit.py
PASS_STATIC_SOURCE_ONLY_W11_C_ACCEPTANCE_AND_ACCEPTED_FACTS_MISSING_NOT_ADMITTED
```

Harness de runtime: **N/A**. Sólo documentos, Git, hashes, metadatos y comprobaciones documentales propias en memoria. Sin emitir/configurar C, ejecutar codecs/crypto positivos, importar/compilar/ejecutar producto/componentes, discovery/tests, build, firma, keygen, inscripción, provisión, benchmarks o probes de reloj/CPU/IO/schedule/plataforma/servicio/ledger/claim/replay/procesos/endpoints. Sin contactos, selección/configuración de identidad/clave/anchor/servicio, nuevos helpers/canales/inputs/outputs, cuotas, reservas, bindings, autoridades o destinos. No se inspecciona ni limpia dev/run_data/D4 ni se reanudan I86/I89/I92.

I122 sigue IMPLEMENTED_NOT_ADMITTED, PJC115-R2 sin habilitar, E06 NOT_RUN, cero paquetes reales aceptados, cero gates de prelaunch cerrados y cero obligaciones E01–E05 cerradas. D5/H07 abiertos e IR03 NOT_READY. Publicar no emite C, acepta custodia/recursos o autoriza ejecución.

Unidad documental de cinco archivos; se declara el exceso de 400 líneas por trazabilidad y preservación. Reversión limitada a retirar exactamente:

- `docs/design/D5-I245-W11-EXACT-C-ACCEPTANCE.md`
- `docs/validation/D5-I223-W11-EXACT-C-ACCEPTANCE-CANDIDATE.json`
- `docs/validation/D5-I245-preparation-review.json`
- `docs/validation/D5-I245-audit.py`
- `docs/validation/D5-I245-integrity.json`

El siguiente paso documental es revisar W11 y sus fronteras de proyección/contención/cobertura. Su aceptación efectiva sigue requiriendo los hechos, pruebas y decisiones competentes pendientes; commit y push no los sustituyen.
