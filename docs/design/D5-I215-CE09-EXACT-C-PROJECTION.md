# I215 — CE09: proyección exacta de C pendiente

CE09 queda preparado como dossier documental negativo para PGO181 candidato 02. **No se crea ni emite C ni un registro positivo de acceptance.** CE08 carece de freeze y aceptación competente reales; faltan las identidades, pruebas previas, cuerpos, hashes, reloj y vigencias. Se mantiene la no admisión de PJC115-R2, E01–E05 abiertas, E06 sin ejecutar, D5 abierto e IR03 `NOT_READY`.

El [dossier CE09](../validation/D5-I193-CE09-EXACT-C-PROJECTION-CANDIDATE.json) conserva las tres evidencias, tres comprobaciones, seis reglas y frontera de autorización de [I193](../validation/D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json). [La revisión de preparación](../validation/D5-I215-preparation-review.json) y [el sello](../validation/D5-I215-integrity.json) permiten revisar esta unidad preservando CE08 y su revisión I214. El expediente exige sólo documentación negativa mientras recursos o antecedentes estén incompletos.

## Proyección sin valores inventados

| Contrato revisable | Requisito conservado | Estado real |
| --- | --- | --- |
| C | 19 campos requeridos de primer nivel, tipo cerrado y schema v3 sin cambios. | Cuerpo, bytes y digest ausentes. |
| Acceptance | 27 campos requeridos, decisión exclusivamente de custodia y tipo cerrado. | Cuerpo, bytes, hash y aceptación ausentes. |
| Tipos compartidos | 14 propiedades de tipo idéntico y seis definiciones transitivas iguales. | Valores reales y evidencia de proyección ausentes. |
| Evidencia previa | Basis, recursos, R01 runtime, R02 plataforma y R08 separado: cinco referencias a cuerpos genuinos. | Ningún cuerpo ni decisión competente aportados. |
| Predicados | Diez de proyección CE09 y dos de cobertura/validez del bundle CE10. | Todos pendientes, sin evaluación real. |

Los catorce campos compartidos son `accepted_resource_index_sha256`, `accepted_source_basis_sha256`, `acceptor`, `configuration_epoch`, `documentary_preparers`, `issuer`, `profile`, `proposal_scope`, `resource_scope_sha256`, `roles`, `runtime_requester_id`, `source_author_id`, `suite_scope_sha256` y `validity`. El campo `schema` de C y el de acceptance tienen constantes distintas; no forman parte de los catorce tipos compartidos.

Trece de esas propiedades requieren proyección exacta de valores aceptados. `validity` comparte tipo pero exige **contención del intervalo de C** en la validez de acceptance y de todos los antecedentes relevantes, no igualdad obligatoria de extremos. Todos deben usar el mismo epoch y estar vigentes bajo garantías de reloj aceptadas. La futura validez del bundle también deberá contener C en CE10; no se pide un bundle aún inexistente como única autenticación previa de CE09.

Los slots `null` describen carencias del wrapper documental, no campos admitidos de un C/acceptance positivo. No se serializa una instancia positiva con identidades, hashes o ceros ficticios. La igualdad estática de tipos tampoco verifica valores, firmas o evidencia real.

## Identidades, scope y bytes

Los roles, preparadores, autor, requester y claves deben resolver a humanos canónicos y appointments genuinos, respetando las ocho exclusiones S01, source-author/root-key y separación adicional R08 frente a R01/R02. R01/R02 no reciben una separación general nueva. La identidad del caller software no sustituye a un humano para evadir esas exclusiones. Las cinco plazas de revisión R01/R02/R03/R06/R08 permanecen sin persona ni appointment aceptado.

Cada preparador de C debe corresponder al actor y record ID de su preparation record completo, con `SHA256(JCS(record))`, perfil/schema exactos y evidencia real de contribución. El requester de C debe ser el accountable requester del caller aceptado. Registro, imagen, caller, constructor, dominio, plataforma y scope de recursos deben concordar por hechos y cuerpos auténticos, no por nombres o hashes declarados.

El scope de fuentes/runtime de C debe coincidir con la imagen y sus seis mappings exactos, con runtime completo independiente del digest de imagen. Basis, índice de recursos, scope de recursos y suite deben cubrir exactamente el mismo scope aceptado. CP03 heredado, atomicidad escrita, límites tipados o diez tests de componentes no sustituyen esas pruebas; E06 o un root futuros tampoco las suministran retroactivamente.

Las constantes de C se conservan literalmente desde el schema: `repository_id=github.com/isidorotrevino/weekly-ai-work-planner`, `root_path=docs/validation/D5-PRP181-FINAL-ADMISSION-ROOT.json` y `offline_key_status=BOTH_KEYS_APPROVED_NOT_REVOKED_AT_CONTEXT_ISSUANCE`. Son requisitos, no afirmaciones de que existan dos claves aprobadas ni un root real. No se añade un campo o hash del bundle a C.

`trust_context_sha256` sólo puede ser `SHA256(JCS(C real completo))`; los cuatro hashes de antecedentes deben corresponder a sus cuerpos reales canónicos. Esos cuerpos y el digest siguen ausentes. Los límites candidatos de 8 192 bytes para C y 16 384 para acceptance no se aplican como cuotas ni prueban heap/CPU, disponibilidad de evidencia o admisión. Los hashes documentales fijan fuentes, no sustituyen esos hashes positivos.

## Reloj, aceptación y fases

Se exige `not_before < expires_at`, lifetime <=3600 y `error_plataforma <= C.clock_error_seconds <=5`. Cada frontera real debe cumplir `trusted_now - error >= not_before` y `trusted_now + error < expires_at`, con epoch actual y revocación conocida. No hay aquí valores confiables de reloj/error/epoch/vigencias, ni snapshot seleccionado. La fecha del cliente o el reloj del host no son prueba; no se permite TOFU, cache obsoleto o lookup oculto ni se promete revocación instantánea.

La decisión de acceptance sigue siendo `IDENTITY_IMAGE_CUSTODY_ONLY_NOT_RESOURCE_OR_CAPTURE_ADMISSION`. Necesita las cinco evidencias previas auténticas y aceptación competente; no cierra recursos ni autoriza ejecución. El registro **no tiene firma independiente**. La expresión de K12 sobre firmar el digest se aplica mediante la cobertura de los mismos C/acceptance en `signed_core` y las tres aprobaciones de bundle de CE10, sin añadir una firma al schema cerrado de acceptance.

K11 mantiene las restricciones pure-Ed25519, dominios de rol y anchors externos seleccionados independientemente, así como el contrato/schema de custodia exactos. No se genera ni verifica aquí ninguna firma, clave o aprobación; claves de C/bundle no se convierten automáticamente en anchors. Las firmas futuras del bundle no suplen autenticación o aceptación de recursos previas ausentes.

CE10 conserva bundle, aprobaciones y mapping; CE11 no depende del recibo CE12. El claim real antes del recibo requiere admisión completa, autorización explícita separada y los prerrequisitos externos de I193. No se emiten C wire, Q, request, root, bundle, mapping, claim ni recibo. Cambiar autor, cuerpo, scope, fuente/runtime/imagen, dominio/recurso, epoch/clave/política exige revisar los candidatos afectados desde CE02/CE03 y CE11 antes de un futuro handoff; no hay transferencia automática de hashes o aceptaciones ni rebind activo.

## Verificación y publicación

Comando exclusivamente documental: `python3 docs/validation/D5-I215-audit.py`.

Resultado requerido: `PASS_STATIC_SOURCE_ONLY_C_AND_ACCEPTANCE_MISSING`. Contrasta 872 pins con blobs del commit base I214 `4d005e0470ada3d1af1654973e15d595d5bb24f2`, preserva 564 archivos publicados y exige cinco archivos nuevos. Reconstruye documentalmente I214 sin invocar mains históricos de publicación y rechaza doce mutaciones inseguras sólo en memoria. No es un PASS de recursos o cualificación.

El replay proyecta como ausente sólo la consulta exacta `Path.exists` de CE09, que no existía en la base. Se restauran las consultas tras éxito y excepción y no se alteran blobs ni controles de otras rutas. Fuera del replay CE01–CE09 están presentes y los tres dossiers CE10–CE12 siguen ausentes.

Harness runtime: N/A; sólo se comprueban JSON/Git/hash, fragments de schemas, tipos y fases. No se importan, compilan ni ejecutan producto o componentes, crypto/codec positivos, builds, probes, clocks/ledger, claims, procesos, benchmarks, enrollment, firmas o contactos. No se cambian cuotas, reservas, presupuesto, bindings, autoridades, destinos ni contratos activos. El mismo asistente prepara y comprueba; no representa revisión independiente competente ni aceptación R08.

Una unidad documental con commit y push autorizados; el exceso de 400 líneas se declara por los pins, contratos y matrices de preservación. Reversión exacta: retirar este documento, el dossier CE09, `D5-I215-preparation-review.json`, `D5-I215-audit.py` y `D5-I215-integrity.json`. La publicación no emite un C ni acepta evidencia; el expediente queda preparado para revisión posterior.
