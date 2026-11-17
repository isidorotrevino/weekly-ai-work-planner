# I213 — CE08: contrato de congelación final pendiente

CE08 queda preparado como dossier documental de congelación para PGO181 candidato 02. **No se congela ni acepta ningún registro real.** Las seis dependencias CE02–CE07 carecen de aceptación competente; siguen ausentes la identidad completa de los contribuyentes, los cuatro cuerpos antecedentes y sus pruebas. Se mantiene la no admisión de PJC115-R2, las cinco obligaciones E01–E05 abiertas, E06 sin ejecutar, D5 abierto e IR03 `NOT_READY`.

El [dossier CE08](../validation/D5-I193-CE08-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json) conserva las cuatro evidencias, tres comprobaciones, diez reglas y frontera de autorización de [I193](../validation/D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json). [La revisión de preparación](../validation/D5-I213-preparation-review.json) y [el sello](../validation/D5-I213-integrity.json) permiten revisar esta unidad sin alterar las fuentes anteriores. CE02 se vincula a su candidato 02 I201/revisión I202; el path del plan histórico también se conserva como historia, sin reescribirlo.

## Inventario de freeze

| Orden | Registro real requerido | Límite candidato de cuerpo | Falta por aportar y aceptar |
| --- | --- | --- | --- |
| 1 | `actor_registry` | 98 304 bytes | Todos los humanos canónicos, aliases, competencia y preparaciones, incluidos los autores reales de pruebas CE07 y contribuciones posteriores al intake CE03. |
| 2 | `image_manifest` | 98 304 bytes | Imagen final, identidad de runtime distinta de la imagen, seis fuentes y mapping autenticado, clausura loader/stdlib/frozen/native/crypto y evidencia de build/políticas. |
| 3 | `caller_identity` | 8 192 bytes | Requester canónico, principal software separado, registro/imagen, dominio de protección y constructor exacto con evidencia genuina. |
| 4 | `platform_custody` | 16 384 bytes | Mismos hashes y dominio, scope de recursos aceptado, ocho garantías reales, reloj/currentness y mecanismo global de un solo uso. |

El dossier contiene los cuatro contratos de schema y 61 slots de campos requeridos, todos pendientes, además de ocho definiciones auxiliares. Los `null` sólo describen ausencia en este wrapper negativo: no son cuerpos positivos I191 y no se admiten como sustitutos de valores reales. Los hashes de documentos existentes son referencias documentales, no hashes de registros finales inexistentes. No se ejecuta el codec, validador positivo ni crypto del protocolo.

## Cierre de autores antes de congelar

CE03 sigue siendo intake provisional. Deben conocerse y autenticarse todos los preparadores del scope aceptado, autores de fuentes y pruebas —incluido CE07—, custodios, requester y sujetos de roles/claves. La existencia de un archivo, este asistente, un nombre, alias o clave no identifica ni acredita por sí sola a un humano responsable. No se preaprueban autores futuros ni se emiten preparation records sintéticos.

El inventario completo debe cumplir preparadores 1..16, actores <=64, claves <=64 y dependencias de imagen <=128, con orden y unicidad canónicos. Los conteos reales siguen desconocidos; no se cuentan como cero ni se recortan listas para encajar. Los índices tipados no acotan por sí solos los cuerpos de prueba ni sus costes de recursos.

Se conservan las ocho exclusiones S01 y la separación de custodia R08 frente a R01 y R02, tanto de humanos como de claves. R01 y R02 pueden coincidir si existe competencia genuina para ambos y aprobaciones separadas por dominio de rol. Un caller software no es un humano alternativo para evadir exclusiones. Las cinco plazas R01/R02/R03/R06/R08 siguen sin persona ni appointment aceptado. Esta preparación por el mismo asistente no es aceptación independiente.

## Bytes, premisas y cambios

Cada referencia de evidencia debe tener un cuerpo completo realmente disponible y aceptable por el revisor competente. La regla futura exige bytes canónicos del registro completo y `SHA256(JCS(registro))`; los seis digests de fuentes deben coincidir con su mapping y `source_root_sha256`. No se usa un ancho de placeholder, hash de path o digest previsto como evidencia. README debe representar un documento; pertenecer a la imagen no prueba que tests/runner se hayan cargado.

Las seis fuentes sucesoras siguen ausentes. Se mantienen los schemas, perfil, salidas y contrato/gramática de transporte exactos, así como las referencias externas al contrato/schema de custodia. No se construye o mide imagen alguna, no se sustituye runtime por imagen y no se embebe un digest propio futuro de imagen/manifest/bundle. No se añaden helpers, entradas o canales.

El orden de antecedentes I191 se preserva: anchors auténticos antes del registro; registro, imagen, caller y plataforma antes de C. CE07 debe aportar pruebas previas aceptadas de BASIS/índices/recursos en el mismo scope final; su revisión documental I212 no las suministra. Las firmas de bundle CE10 no pueden ser la única autenticación prevista para hechos anteriores. Las seis dependencias siguen pendientes; un grafo acíclico no demuestra su cumplimiento.

Cualquier nuevo contribuyente, alias, cuerpo, fuente/runtime/imagen, caller/dominio/constructor, plataforma/recurso, epoch/clave/política invalida los digests y revisiones candidatos dependientes. Exige renovar el scope y las revisiones CE03–CE10 que correspondan, y CE11 antes de un futuro handoff. Cambios de anchor o clave requieren además volver a CE02 antes del freeze dependiente. No se reutilizan automáticamente hashes o aceptaciones, no se transfieren pruebas antiguas y no se aplica un rebind activo de `capture_inputs`.

## Freshness y fases posteriores

Los registros reales deben compartir epoch, validez actual solapada y hashes cruzados exactos. La validez exige `not_before < expires_at`, lifetime <=3600 segundos y reloj confiable con error <=5 segundos, con currentness y revocación conocida en cada frontera. No existe aquí evidencia de reloj/epoch ni snapshot fresco. La fecha del cliente o un cache no renuevan una validez; no se promete descubrir instantáneamente toda revocación ni se permite TOFU o lookup oculto.

CE08 sólo especifica el freeze de cuatro antecedentes. CE09 conserva la proyección de C y acceptance; CE10 conserva bundle, aprobaciones y mapping único. No se exige C/Q/root/recibo futuro para justificar el propio antecedente. CE11 no depende de CE12. El claim real antes del recibo CE12 continúa condicionado a admisión completa, autorización explícita separada y todos los prerrequisitos externos de I193. Nada de ello se emite o ejecuta en I213.

## Verificación y publicación

Comando exclusivamente documental: `python3 docs/validation/D5-I213-audit.py`.

Resultado requerido: `PASS_STATIC_SOURCE_ONLY_FINAL_RECORDS_MISSING`, que no es un PASS de recursos o cualificación. Se contrastan 862 pins con blobs del commit base I212 `f4bbc9782182ab0fed83dc89ef2fa1869c9c4838` y se preservan 554 archivos publicados. Se comprueban los DAGs, schemas/límites y doce mutaciones negativas en memoria; se reproduce la reconstrucción y revisión documental I212 sin invocar mains históricos de publicación.

El replay histórico proyecta como ausente sólo la consulta `Path.exists` de la ruta exacta CE08, que no existía en el commit base; los blobs y demás controles permanecen intactos. La consulta se restaura ante éxito y excepción. Fuera del replay CE01–CE08 existen y los cuatro dossiers CE09–CE12 siguen ausentes. No se crea un cuerpo positivo para hacer pasar la auditoría.

Harness runtime: N/A, porque esta unidad sólo procesa documentos/Git/hash/schema fragments y grafos. No se importan, compilan ni ejecutan producto o componentes, ni builds, probes, crypto/codec reales, clocks/ledger, claims, workers, benchmarks o contactos. No cambian cuotas, reservas, presupuesto, bindings, autoridad, destino o contrato activo.

Commit y push autorizados para una unidad documental de cinco archivos. Se declara el exceso de 400 líneas por los pins, contratos tipados y preservación. Reversión exacta: retirar este documento, el dossier CE08, `D5-I213-preparation-review.json`, `D5-I213-audit.py` y `D5-I213-integrity.json`. Publicar esta unidad no produce un freeze real ni admisión; el dossier queda preparado para revisión posterior.
