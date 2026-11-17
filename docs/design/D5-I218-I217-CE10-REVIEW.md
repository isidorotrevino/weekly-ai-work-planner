# I218 — revisión documental de CE10/I217

CE10 se confirma como baseline documental de bundle/aprobaciones/mapping pendientes para PGO181 candidato 02, sin nuevos hallazgos documentales bloqueantes. **No se crea ni acepta bundle, firma o mapping real.** CE02/CE08/CE09 y todas las pruebas de identidad, provenance, tamaños, unicidad y currentness siguen sin aceptación competente. PJC115-R2 mantiene la no admisión; E01–E05 siguen abiertas, E06 sin ejecutar, D5 abierto e IR03 `NOT_READY`.

La revisión de [CE10 de I217](../validation/D5-I193-CE10-BUNDLE-APPROVAL-AND-CURRENT-MAPPING-CANDIDATE.json) contrasta I193 y las diez reglas I191 con los schemas cerrados, el perfil y la referencia de cotas I192. [La reconstrucción](../validation/D5-I218-I217-source-reconstruction.json), [el dictamen](../validation/D5-I218-I217-documentary-review.json) y [el sello](../validation/D5-I218-integrity.json) registran la comprobación sin modificar I217.

## Resultado de la revisión

| Aspecto | Confirmación documental y límite |
| --- | --- |
| Cuatro evidencias, tres comprobaciones y diez reglas | Conservadas con su frontera negativa de autorización; no se autorizan contactos con proveedores. |
| Dependencias | CE02 candidato 02/I202, CE08/I214 y CE09/I216 fijados por hash; los tres gates competentes siguen pendientes. |
| Cinco registros anidados | Tipos, cinco hashes y caps exactos preservados; suman 88 campos requeridos de primer nivel. No hay cuerpos, tamaños o aceptación reales. |
| Core y bundle | Core cerrado de ocho campos; bundle cerrado de tres. No se añade un cuerpo C ni una validez propia al bundle. |
| Tres aprobaciones | R01/R02/R08, dominios exactos con un byte NUL y mismo core completo. Ninguna firma o verificación genuina aportada. |
| Confianza | Registry/epoch/propósito/humanos/claves y pins de políticas seleccionados independientemente; sin auto-bootstrap desde C/bundle/root. |
| Mapping | Unicidad global por `(epoch, digest de C)` y un único destino bundle/caller/image/domain/ledger. No hay backend o configuración seleccionados. |
| Costes y evidencia | Referencias completas y trabajo por intento siguen incluidos en E01–E05 y fases. No se consideran gratuitos por ser offline. |

Las cuatro plazas R01/R02/R06/R08 siguen sin persona ni appointment aceptado. Se conservan las ocho exclusiones S01, source-author/root-key y la separación adicional R08 frente a R01/R02. La revisión la realiza el mismo asistente que preparó I217; no es aceptación independiente competente.

## Qué cubren las aprobaciones

Los dominios siguen siendo `D5/PGO181/CUSTODY/v1/R01`, `.../R02` y `.../R08`, cada uno seguido de un byte `0x00` antes de `JCS(signed_core completo)`. Las tres aprobaciones deben cubrir los mismos bytes de core bajo esos dominios; no se acepta una porción diferente por rol ni se sustituye la tercera por la política de dos firmas del root existente.

La exclusión de firmas/hash propio/Q/root/recibo se refiere a miembros externos al core. **No se recorta ningún campo del core de ocho miembros** para formar el mensaje. Los cinco registros y sus hashes permanecen dentro. C queda vinculado indirectamente por `acceptance_record.trust_context_sha256`; no se inserta un nuevo cuerpo C ni una firma propia en acceptance.

El schema de bundle sólo contiene `schema`, `signed_core`, `approvals`. Su vigencia efectiva procede de las vigencias actuales de sus cinco registros, incluido acceptance, con C contenido en todos los intervalos relevantes. No se añade un campo `validity` o un reloj elegido por el caller.

Se preservan pure-Ed25519 y las restricciones estrictas del perfil, sin ejecutar crypto, codecs o vectores positivos. R08 humano/clave sigue distinto de R01/R02. R01/R02 pueden compartir humano/clave sólo cuando las condiciones genuinas de competencia, propósito y aprobaciones separadas se cumplan; no se añade separación general entre ellos. Los pins de contrato/schema deben coincidir con la selección externa y la imagen real, no seleccionarse desde el bundle recibido.

## Mapping global y orden

K09 exige exactamente un mapping vigente por `(configuration_epoch, SHA256(JCS(C real)))` en todo el ámbito de callers/imágenes/dominios aprobados. Una partición de cada caller no demuestra esa unicidad. El destino debe fijar un solo bundle, caller, imagen, dominio de protección y dominio global de ledger, con evidencia auténtica contra conflictos, epoch obsoleto, rollback y estado desconocido.

La resolución autenticada debe ocurrir antes de `P_ROOT_CHECK`, seguida del freeze de C/Q y constructor admitido. El worker nace en esa custodia protegida; no la infiere de bytes ni recibe un nuevo frame/recibo I191. No se define un nuevo schema positivo de mapping ni se elige endpoint, backend, servicio o configuración. Su capacidad efectiva para mantener el mapping sigue sin demostrar.

El DAG permanece acíclico. CE10 tiene CE01–CE09 como ancestros; mapping sigue a bundle/C y no depende del root, claim o recibo futuros. Las aprobaciones de bundle no autentican retrospectivamente sus propios antecedentes. CE11 conserva revisión previa al handoff y no depende del recibo CE12. Claim y recibo requieren admisión completa, autorización explícita separada y los prerrequisitos externos de I193.

## Cota de bytes condicionada

La reconstrucción reproduce el envelope documental I192, sin instanciar un cuerpo positivo:

| Término | Cota efectiva en el modelo condicionado |
| --- | ---: |
| Actor registry | 98 304 |
| Image manifest | 98 304 |
| Caller identity | 1 933 |
| Platform custody | 5 940 |
| Acceptance | 13 879 |
| Suma de registros | 218 360 |
| Estructura y aprobaciones del modelo | 3 284 |
| Bundle condicionado | 221 644 |
| Cap candidato completo / margen aritmético | 262 144 / 40 500 |

Los términos usan el mínimo entre el envelope del schema y el cap correspondiente, con todos los caps reales obligatorios. El upper histórico sin caps anidados es 368 348 dentro del modelo de codificación; no demuestra inviabilidad de un bundle ni tamaño real. La cota condicionada exige los supuestos ASCII/safe-integer y escape de strings de I192 que I217 conserva expresamente. Si un cuerpo no los satisface, requiere una cota revisada bajo los mismos límites.

No se han verificado esos supuestos, caps o bytes en cuerpos reales. El margen no es reserva de heap/CPU y la cota no incluye todos los cuerpos de prueba referenciados ni demuestra servicio, IO, fases o éxito en 900 segundos. No se recortan listas ni se convierten costes desconocidos en cero. Los dos Reader y el join global, lookup/freshness/identidad/crypto/measurement/copias/registry/recibo/native/IO siguen dentro de los costes requeridos de launch/worker/finish.

## Efectos y verificación

I122 conserva `IMPLEMENTED_NOT_ADMITTED`, CP03 heredado sólo en su scope original, CP07 falso, atomicidad correlacionada sin verificar y componentes `NOT_RUN`. No se emite `SOURCE_CAPACITY_VERIFIED`, no se cierra ninguna obligación de recursos ni se transfiere automáticamente un hash, aprobación, mapping o aceptación antigua a un scope cambiado. No se emite C/Q/root/request/constructor/claim/recibo ni se añade canal, archivo, helper o Input Reader member.

Comando exclusivamente documental: `python3 docs/validation/D5-I218-audit.py`.

Resultado: `PASS_STATIC_SOURCE_ONLY_BUNDLE_APPROVALS_MAPPING_MISSING`. Contrasta 887 pins con blobs del commit base I217 `0bcd5fc4a5d8c1a9a4cc336f50e16b7b514f2e81`, preserva 579 archivos publicados y exige cinco archivos nuevos. Reconstruye schemas, dominios, mapping, composición condicionada y fases, y reproduce el build documental I217 y sus doce rechazos en memoria sin invocar mains históricos de publicación. No es un PASS de crypto, mapping real, recursos o cualificación.

El guard histórico se revisa directamente: CE10 estaba ausente en la base I217 y presente en la base I218. Sólo se proyecta aquella consulta exacta `Path.exists`, con restauración ante éxito y excepción, sin cambiar blobs ni controles de otras rutas. CE01–CE10 siguen presentes y los dossiers CE11/CE12 ausentes.

Harness runtime: N/A; sólo se procesan documentos/Git/hash, schemas, dominios y grafos. No se importan, compilan ni ejecutan producto/componentes, signing/crypto/codec positivos, builds, probes, clocks/ledger, claims, procesos, benchmarks, enrollment, provisioning, servicios o contactos. No se cambian cuotas, reservas, presupuesto, bindings, autoridades, destinos o contratos activos.

Una unidad documental con commit y push autorizados; se declara el exceso de 400 líneas por sus pins, matrices y preservación. Reversión exacta: retirar este documento, `D5-I218-I217-source-reconstruction.json`, `D5-I218-I217-documentary-review.json`, `D5-I218-audit.py` y `D5-I218-integrity.json`. Publicar no acepta bundle, aprobaciones o mapping. CE10 queda disponible como baseline documental para una preparación CE11 solicitada por separado, con toda evidencia y aceptación reales pendientes.
