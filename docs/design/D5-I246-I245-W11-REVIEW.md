# I246 — W11 revisado; proyección y aceptación reales pendientes

La revisión documental de W11 de I245 encuentra consistentes sus requisitos de proyección exacta de C y acceptance con I223, CE09 y los schemas/contratos vinculados. No se identifica un nuevo defecto documental. **Se mantiene la no admisión**: faltan hechos aceptados W09/W10, valores, cuerpos, digests, vigencias, evidencias y decisiones competentes. No se crea o emite C ni aceptación real; SD01 sigue activo y D5 abierto.

Fecha: 2026-11-25, Europe/Madrid. Base: `1eedb75402652a5e8d5d68d33a9a5a3fc3a64074`.

El objeto es [W11 candidato de I245](../validation/D5-I223-W11-EXACT-C-ACCEPTANCE-CANDIDATE.json). Sus bytes y antecedentes se conservan. La reconstrucción metodológica del mismo asistente no acredita identidad humana, independencia, competencia R01/R02/R03/R06 o aceptación separada R08.

## Resultado del contraste

| Objeto | Resultado documental | Pendiente real |
|---|---|---|
| Contrato W11 | Entregables, dependencias W09/W10, salidas y restricciones exactos de I223 | Autoridad y dependencias genuinas aceptadas |
| C/acceptance | Schemas cerrados con 19/27 campos y caps candidatos 8192/16384 | Cuerpos, valores, bytes/digests y revisión |
| Tipos | 14 propiedades idénticas entre 15 nombres comunes y seis definiciones transitivas | Aceptación de valores efectivos |
| Valores | 13 proyecciones exactas más contención de validity | Hechos fuente, comparaciones, vigencia/currentness |
| Antecedentes/evidencias | Cuatro hashes y cinco referencias previas trazables | Cuerpos congelados, pruebas y decisiones competentes |
| Predicados | PJ01–PJ10 W11; PJ11–PJ12 diferidos W12 | Todos sin evaluar por falta de evidencia |
| Cobertura | Acceptance sin firma propia; C cubierto indirectamente por digest | Aprobaciones CE10 genuinas, sin sustituir autenticación previa |

Los 46 slots de campo permanecen sin valores reales, incluidos los campos con constantes conocidas. Cuerpos, bytes, hashes y provenance siguen null; ninguna aceptación o proyección real está verificada. Los límites C8192/acceptance16384 no se aplican como cuotas ni prueban completitud de evidencia, heap, CPU o tamaño medido. Son requisitos documentales fuera de cuerpos positivos.

## Tipos, proyección y contención

La reconstrucción obtiene directamente de los dos schemas quince nombres comunes. `schema` tiene constantes distintas; las otras catorce propiedades tienen tipos idénticos. Un recorrido iterativo separado reproduce seis definiciones transitivas idénticas: identity, proposal_scope, sha256, trusted_key, validity y verifier_profile. Esta igualdad estática no acepta valores.

Las trece propiedades distintas de validity exigen el mismo valor genuino aceptado. validity comparte tipo, pero C debe estar contenido en cada intervalo vigente pertinente de antecedentes y acceptance; no se igualan obligatoriamente los extremos. Epoch sí debe concordar. Se preservan not_before < expires_at, lifetime ≤3600, `error_plataforma <= C.clock_error_seconds <=5` y las comprobaciones de trusted-now a ambos lados de los intervalos.

No existen aquí intervalos, trusted-now o pruebas de contención/currentness/revocación reales. La fecha del cliente o reloj del host no constituyen tiempo confiable del runtime. No se selecciona reloj o snapshot ni se admite stale/TOFU o lookup oculto; tampoco se promete revocación instantánea. Las incógnitas no se rellenan con cero.

Se conservan las cuatro constantes exactas de C —schema, repository_id, root_path y offline_key_status— y el cierre sin campos nuevos o hash de bundle. La constante de decision en acceptance es `IDENTITY_IMAGE_CUSTODY_ONLY_NOT_RESOURCE_OR_CAPTURE_ADMISSION`. Conocer esas constantes no proporciona hechos genuinos ni convierte aceptación de custodia en admisión de recursos o captura.

## Identidad, scope y evidencia previa

Se mantienen las políticas W02 de identidad canónica, catorce requisitos de separación, ocho exclusiones S01 y cuatro separaciones adicionales de custodia. R01/R02 pueden coincidir sólo bajo la cualificación y los dominios de rol requeridos, sin añadir una exclusión general. Roles, todos los preparadores, author/requester, issuer/acceptor y claves exigen registry, competencia, appointments y aceptación previos auténticos. Un principal software, Git, asistente, clave o etiqueta de rol no sustituye identidad humana o independencia.

Los preparadores deben concordar por actor_id, record_id y SHA256(JCS del preparation record completo), con contribuciones reales y perfil/schema exactos, sin recorte. Requester/caller, constructor/dominio, registry/imagen/plataforma y source/runtime/profile/BASIS/index/resource/suite/epoch deben corresponder al mismo scope genuino aceptado. Digest de imagen y runtime siguen siendo identidades distintas. W09 y W10 permanecen sin aceptación real o freeze.

Los cuatro hashes de antecedentes mantienen correspondencia exacta con actor_registry, image_manifest, caller_identity y platform_custody W10. Las cinco referencias previas exigen evidencia de basis, recursos, R01 runtime, R02 plataforma y R08 separado, con cuerpos completos disponibles, bytes/digest, autores/providers/custodia, unidades/supuestos/validez y reviews genuinos aceptados. Nada de ello se aporta como material positivo en I246.

Cambios de autores, cuerpos, fuentes, imagen/runtime, dominio/recurso, epoch/clave o política invalidan los candidatos afectados y requieren revisión. No se transfieren automáticamente hashes o aceptaciones y no se aplica refresh/rebind activo. Un documento revisado, schema o flag no subsana el baseline ausente.

## Digest, firma y fases posteriores

Se conserva SHA256(JCS del C genuino completo), sin digest de path, parcial, placeholder o predicción. La cobertura futura de C en CE10 sigue la ruta `signed_core.records.acceptance_record.trust_context_sha256`. La revisión comprueba el core cerrado de ocho campos, con cinco registros, incluido acceptance; no contiene un cuerpo C adicional.

Acceptance no tiene firma propia. La futura cobertura de las tres aprobaciones por dominios R01/R02/R08 es sobre el mismo signed_core con acceptance y su digest exacto de C. Se mantiene la lectura conjunta de K12, el schema cerrado y la revisión I216; no se añade firma al registro. Contrato/schema y anchors se seleccionan independientemente, sin confiar automáticamente en claves declaradas en C/bundle.

El bundle cerrado sólo tiene schema, signed_core y approvals. No posee validity independiente: PJ12 se refiere a la validez/currentness efectiva de los cinco registros, con C contenido en sus intervalos aceptados. No se crea una vigencia de bundle o una dependencia inversa que exija aceptación W12 antes de W11.

PJ01–PJ10 conservan sus requisitos W11 de identidad/preparadores, requester/caller, imagen/runtime, pruebas previas, epoch/contención/reloj, constantes, digest/hashes y custodia/evidencia. PJ11–PJ12 permanecen diferidos a W12. Las futuras firmas CE10, E06/root/recibo no pueden proporcionar la única autenticación previa de W09/W10 o de las cinco evidencias.

W12 conserva bundle/aprobaciones/mapping; W13 gates y las fases finales E06/payload/Q/root/claim/recibo siguen separados. CE11 no depende del recibo CE12. Los costes de C/acceptance/evidencia, registry, copias/JCS/hashing, lookup/freshness/identidad/crypto y salidas permanecen dentro de ambos Readers y la composición de heap/trabajo/servicio/fases, fallos y cleanup. Se requiere revisión del grafo y cotas si cambian mecanismos o cuerpos. No hay costes gratuitos offline, cuotas, reservas o recursos reservados nuevos.

## Verificación y publicación

La [reconstrucción](../validation/D5-I246-I245-source-reconstruction.json) registra 29 criterios y 1027 pins contra los blobs del commit base. El [dictamen](../validation/D5-I246-I245-documentary-review.json) conserva 42 rechazos documentales I245 y añade 22 sobre campos/tipos/definiciones, relaciones de valor, constantes/caps, hashes/evidencias, consumidores de predicados, reloj/firma/cobertura, fases posteriores e independencia.

El auditor contrasta fuentes primarias y pointers JSON; reproduce candidato y preparación I245 sin invocar mains históricos ni nuevas proyecciones de presencia. El [sello](../validation/D5-I246-integrity.json) preserva 719 archivos publicados y los cuatro artefactos distintos del propio sello.

```text
python3 docs/validation/D5-I246-audit.py
PASS_STATIC_SOURCE_ONLY_W11_REVIEW_C_ACCEPTANCE_AND_ACCEPTED_FACTS_MISSING_NOT_ADMITTED
```

Harness de runtime: **N/A**. Sólo documentos, Git, hashes, metadatos y comprobaciones documentales propias en memoria. Sin emitir/configurar C, ejecutar codec/crypto positivos, importar/compilar/ejecutar producto/componentes, discovery/tests, build, firma, keygen, inscripción, provisión, benchmarks o probes de reloj/CPU/IO/schedule/plataforma/servicio/ledger/claim/replay/procesos/endpoints. Sin contactos, selección/configuración de identidad/clave/anchor/servicio, nuevos helpers/canales/inputs/outputs, cuotas, reservas, bindings, autoridades o destinos. No se inspecciona ni limpia dev/run_data/D4 ni se reanudan I86/I89/I92.

I122 sigue IMPLEMENTED_NOT_ADMITTED, PJC115-R2 sin habilitar, E06 NOT_RUN, cero paquetes reales aceptados, cero gates de prelaunch cerrados y cero obligaciones E01–E05 cerradas. D5/H07 abiertos e IR03 NOT_READY. Publicar no crea C, acepta custodia/recursos o autoriza ejecución.

Unidad documental de cinco archivos; se declara el exceso de 400 líneas por trazabilidad y preservación. Reversión limitada a retirar exactamente:

- `docs/design/D5-I246-I245-W11-REVIEW.md`
- `docs/validation/D5-I246-I245-source-reconstruction.json`
- `docs/validation/D5-I246-I245-documentary-review.json`
- `docs/validation/D5-I246-audit.py`
- `docs/validation/D5-I246-integrity.json`

El siguiente paquete documental I223 es W12, conservando la falta de evidencia y aceptación reales de sus antecedentes. El cierre efectivo sigue exigiendo esas pruebas y decisiones competentes; commit y push no las sustituyen.
