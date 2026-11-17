# I217 — CE10: bundle, aprobaciones y mapping pendientes

CE10 queda preparado como dossier documental negativo para PGO181 candidato 02. **No se crea bundle, aprobación o mapping real ni se acepta custodia.** CE02, CE08 y CE09 carecen de aceptación competente; faltan los registros finales, C, anchors, firmas y evidencia de unicidad/currentness. Se mantiene la no admisión de PJC115-R2, E01–E05 abiertas, E06 sin ejecutar, D5 abierto e IR03 `NOT_READY`.

El [dossier CE10](../validation/D5-I193-CE10-BUNDLE-APPROVAL-AND-CURRENT-MAPPING-CANDIDATE.json) conserva las cuatro evidencias, tres comprobaciones y diez reglas de [I193](../validation/D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json). [La revisión de preparación](../validation/D5-I217-preparation-review.json) y [el sello](../validation/D5-I217-integrity.json) fijan el alcance sin alterar fuentes históricas. Se usan CE02 candidato 02/I202, CE08/I214 y CE09/I216, preservando aparte los paths del plan histórico.

## Qué falta para el bundle

| Pieza | Contrato conservado | Estado actual |
| --- | --- | --- |
| Cinco registros | Actor registry, image manifest, caller identity, platform custody y acceptance, con cuerpos completos auténticos y hashes canónicos exactos. | Ningún cuerpo, tamaño, hash o aceptación real. |
| `signed_core` | Ocho campos cerrados; cinco registros y sus cinco hashes, epoch de autoridad, anchor digest y pins exactos de políticas. | Core real ausente. |
| Bundle | Sólo tres campos superiores: `schema`, `signed_core`, `approvals`. | Cuerpo y digest ausentes; no tiene `validity` o C propios. |
| Aprobaciones | R01_RUNTIME, R02_PLATFORM y R08_ACCEPTANCE sobre el mismo core exacto. | Tres aprobaciones, claves, provenance y verificaciones genuinas pendientes. |
| Mapping vigente | Un único destino global para cada `(configuration_epoch, SHA256(JCS(C)))`. | Registry/backend, unicidad, snapshot, revocación y revisión competente ausentes. |

Los cinco contratos anidados suman 88 campos requeridos de primer nivel. Las listas y cuerpos de evidencia completos siguen siendo obligatorios; el conteo de campos no los acredita. Los `null` del wrapper expresan carencias y no instancian registros positivos con identidades, firmas o hashes ficticios.

## Selección de confianza y tres aprobaciones

El registry de anchors debe ser configuración preexistente aceptada independientemente del bundle, C, root y repositorio. Deben verificarse el digest esperado externo, epoch, propósito, humano canónico, claves, vigencia y revocación. Una clave suministrada, registry autofirmado o hash del bundle no puede fundar su propia confianza. No se provisiona registry, persona, servicio o clave.

Los pins de contrato/schema I191 deben seleccionarse externamente y coincidir con los del core e imagen aceptados; no se eligen a partir del bundle recibido. Los hashes de esos documentos en el dossier sólo fijan requisitos candidatos, no acreditan una selección real de plataforma ni que una imagen los implemente.

Cada aprobación usa su dominio ASCII exacto, seguido de **un byte `0x00`** y `JCS(el mismo signed_core real completo)`:

| Rol | Dominio antes del byte NUL |
| --- | --- |
| R01_RUNTIME | `D5/PGO181/CUSTODY/v1/R01` |
| R02_PLATFORM | `D5/PGO181/CUSTODY/v1/R02` |
| R08_ACCEPTANCE | `D5/PGO181/CUSTODY/v1/R08` |

Se preservan las restricciones strict pure-Ed25519 del perfil y K11, sin ejecutar un verificador o codec positivo. Firmas, hash propio del bundle, Q, root y recibo se excluyen del mensaje; no se firma un core diferente por rol. La regla de dos firmas del root existente no sustituye las tres aprobaciones de custodia. R08 humano/clave permanece distinto de R01 y R02; R01/R02 pueden compartir humano/clave sólo bajo competencia genuina y aprobaciones separadas por dominio. Todas las exclusiones S01/source-author/root-key y bindings de propósito permanecen intactos.

La cobertura de C es indirecta mediante `acceptance_record.trust_context_sha256` dentro del core, no mediante un nuevo cuerpo C. Acceptance no adquiere firma propia. Las firmas tampoco reemplazan provenance, completitud de referencias, recursos o admisión. Se exigen registros de verificación competente y provenance genuinos si llegan a proporcionarse con autorización propia; este trabajo no autoriza firma, generación de claves, verificación criptográfica o contacto con proveedores.

## Mapping global y frontera de canales

K09 exige exactamente una correspondencia actual por `(epoch, digest canónico del C real)` **en todo el ámbito aprobado de callers/imágenes/dominios**. Debe fijar un solo bundle, caller, imagen, dominio de protección y dominio global de ledger. No basta la unicidad en una partición de cada caller. Conflictos, estado ambiguo, epoch obsoleto o rollback rechazan; faltan todas las pruebas reales de esa propiedad.

El caller debe resolver el mapping autenticado antes de `P_ROOT_CHECK` y congelar C/Q y el estado del constructor admitido. El worker nace en ese dominio protegido aceptado; no recibe un nuevo frame I191 ni deduce la custodia de los bytes. No se selecciona backend, endpoint o formato positivo nuevo para mapping. Si no puede establecerse esa custodia intrínseca, permanece `NOT_ADMITTED`.

Se conservan C/Q, dos pipes, seis operandos, 494 miembros de payload y 496 rutas físicas, así como los schemas de salida I187. No se añade campo, archivo, helper, Input Reader member, canal o recibo a los artefactos. Los cuerpos externos sólo pueden entrar por custodia de memoria/constructor aceptada y acotada, sin lookup oculto de archivos o red.

## Cotas condicionadas y evidencia completa

Cada registro debe satisfacer su cap real: actor/image 98 304 bytes cada uno, caller 8 192, platform/acceptance 16 384 cada uno. Bundle completo <=262 144. La reconstrucción documental reproduce I192: upper del schema sin caps anidados 368 348; upper condicionado 221 644; margen aritmético 40 500.

El resultado condicionado usa el envelope ASCII/safe-integer de I192, su hipótesis de escape de strings y los cinco caps obligatorios. Si los cuerpos no satisfacen esas hipótesis se necesita una cota revisada bajo los mismos límites. No se valida un cuerpo real ni se concluye inviabilidad a partir del upper sin caps. No se suman los caps para sustituir la composición del schema y no se usan anchos de placeholders como prueba de ajuste.

Los 221 644 bytes y su margen no acotan los cuerpos referenciados, heap, CPU, IO, servicio, reloj o 900 segundos. Ningún coste desconocido se convierte en cero ni se recortan listas para encajar. Lookup, freshness, identidad, crypto/measurement, copias, registry/recibo y native/IO por intento siguen dentro de launch/worker/finish y del join E01–E05, incluidos ambos ledgers Reader. Llamar offline al enrollment/build no hace gratuita su verificación.

## Vigencias, fases y efectos

La validez efectiva del bundle deriva de sus cinco registros actuales, incluido acceptance; no se crea un campo `validity` independiente. C debe estar contenido en las vigencias relevantes, con mismo epoch, `not_before < expires_at`, lifetime <=3600 y error conservador <=5. Reloj, trusted-now, revocación conocida y ausencia de conflicto requieren evidencia real; no hay snapshot fresco ni se promete descubrir instantáneamente toda revocación.

CE10 requiere CE02/CE08/CE09 genuinamente aceptados. Sus aprobaciones no pueden ser la única autenticación prevista de sus antecedentes. CE11 conserva revisión previa al handoff y no depende del recibo CE12. Claim y recibo reales exigen admisión completa, autorización explícita separada y los prerrequisitos externos de I193. No se crea C/Q/request/root/constructor/claim/recibo ni se ejecuta servicio alguno.

Cambios de anchor/clave, autor/cuerpo, scope, imagen/runtime, dominio/recurso, epoch o política invalidan candidatos afectados y exigen revisión CE02/CE03–CE10 y CE11 según corresponda; no se transfieren hashes, aprobaciones o mappings automáticamente. Las cuatro plazas R01/R02/R06/R08 siguen sin persona ni appointment aceptado. El mismo asistente prepara y comprueba; no representa revisión independiente competente ni aceptación R08.

## Verificación y publicación

Comando exclusivamente documental: `python3 docs/validation/D5-I217-audit.py`.

Resultado requerido: `PASS_STATIC_SOURCE_ONLY_BUNDLE_APPROVALS_MAPPING_MISSING`. Contrasta 882 pins con blobs del commit base I216 `bdb7f82f13dffc92a90b75d10efea8ca80a92177`, preserva 574 archivos publicados y exige cinco archivos nuevos. Reconstruye documentalmente I216 sin invocar mains históricos de publicación, reproduce la cota condicionada por aritmética de schemas y rechaza doce mutaciones inseguras sólo en memoria. No es un PASS de recursos, crypto, mapping real o cualificación.

El replay proyecta como ausente sólo la consulta exacta `Path.exists` de CE10, ausente en la base. Se restaura ante éxito y excepción sin cambiar blobs ni controles de otras rutas. Fuera del replay CE01–CE10 existen y los dossiers CE11/CE12 siguen ausentes.

Harness runtime: N/A; sólo se procesan documentos/Git/hash, fragments de schemas, cotas condicionadas y grafos. No se importan, compilan ni ejecutan producto/componentes ni signing/crypto/codec positivos, builds, probes, clocks/ledger, claims, procesos, benchmarks, enrollment, provisioning, servicios o contactos. No cambian cuotas, reservas, presupuesto, bindings, autoridades, destinos o contratos activos.

Commit y push autorizados para una unidad documental; se declara el exceso de 400 líneas por sus contratos, pins y matrices de preservación. Reversión exacta: retirar este documento, el dossier CE10, `D5-I217-preparation-review.json`, `D5-I217-audit.py` y `D5-I217-integrity.json`. Publicar no crea ni acepta bundle, firmas o mapping. El dossier queda preparado para revisión posterior.
