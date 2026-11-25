# I247 — W12 preparado; bundle, aprobaciones y mapping reales pendientes

W12 queda preparado como expediente documental de requisitos de bundle, aprobaciones y mapping global del plan I223. **Se mantiene la no admisión.** W02/W04/W10/W11 no están aceptados; faltan cuerpos, firmas, confianza independiente, unicidad global, custodia intrínseca y decisiones genuinas. No se crea o acepta bundle, aprobación, mapping o backend real; SD01 permanece activo y D5 abierto.

Fecha: 2026-11-25, Europe/Madrid. Base: `e68ed6276e9ea1018a9942e4d3599550e859f9cc`.

El [candidato W12](../validation/D5-I223-W12-BUNDLE-APPROVALS-GLOBAL-MAPPING-CANDIDATE.json) vincula literalmente entregables, dependencias, tres salidas, rechazos y restricciones I223. Usa CE10 y su revisión I218 como requisitos documentales; no copia como actuales sus afirmaciones históricas de disponibilidad de otros dossiers. Los antecedentes conservan bytes y fechas.

## Requisitos preparados

| Objeto | Requisito | Estado real |
|---|---|---|
| Registros anidados | Cinco cuerpos y hashes, con 88 campos requeridos en total y caps individuales | Cuerpos, tamaños, hashes, scope/custodia/reviews pendientes |
| Core/bundle | Core cerrado de ocho campos y bundle cerrado de tres | Bytes completos, digest y aceptación pendientes |
| Aprobaciones | R01/R02/R08 sobre el mismo core completo, con dominio exacto y un NUL | Actores, claves, mensajes, firmas y verificación/provenance pendientes |
| Confianza | Registry/anchors y políticas seleccionados independientemente | Autoridad, propósito, epoch/currentness/revocación y pins reales sin aportar |
| Mapping | Exactamente uno vigente por `(epoch, digest de C)` en todo el scope aprobado | Prueba global, destino, backend y reviews pendientes |
| Constructor | Custodia intrínseca protegida antes de código no confiable | Mecanismo y evidencia de enforcement sin aportar |
| Tamaño | Cota condicionada I192 bajo caps/encoding reales | Ningún supuesto o fit real verificado |

Los cinco registros son actor_registry, image_manifest, caller_identity, platform_custody y acceptance_record, con 8/26/13/14/27 campos requeridos. Sus cuerpos canónicos, bytes, hashes, referencias, autenticación previa, epoch/vigencias y aceptaciones permanecen null. Los slots de campo no son registros positivos ni prueba de completitud anidada. El core mantiene los cinco registros y sus cinco hashes, y los pins exactos de contrato/schema de custodia.

## Aprobaciones y confianza

Los tres dominios son `D5/PGO181/CUSTODY/v1/R01`, `.../R02` y `.../R08`, cada uno seguido por un único octeto NUL `0x00`, antes de JCS del mismo core real completo. La receta es un requisito; no se codifica mensaje, firma o vector positivo. Se conserva pure-Ed25519 y las restricciones estrictas del perfil, sin seleccionar librería, generar claves o ejecutar crypto.

Ningún campo del core de ocho miembros se recorta para formar mensajes por rol. Las exclusiones de firmas, hash propio del bundle, Q, root y recibo son miembros externos al core, no permiso para retirar sus registros o hashes. Las dos firmas del root existente no sustituyen las tres aprobaciones de custodia. Una firma sola no demuestra provenance, completitud, recursos o admisión.

C queda fijado indirectamente por acceptance.trust_context_sha256; no se añade un cuerpo C al signed_core ni un hash de bundle a C/Q. Acceptance no tiene firma propia. El bundle sólo tiene schema, signed_core y approvals, sin validity independiente. Sus decisiones de core/acceptance siguen siendo exclusivamente custodia, sin admisión runtime, de recursos o captura.

Registry/anchors preexistentes deben estar aceptados por autoridad independiente, con propósito/actor/clave, epoch, vigencia y revocación genuinos. No se autofundan desde C, bundle, root, registry autofirmado o fichero de claves del repositorio. Los pins de contrato/schema deben coincidir con la selección externa y las políticas realmente implementadas en la imagen, no elegirse desde el bundle recibido.

Se mantienen las ocho exclusiones S01, source-author/root-key y cuatro separaciones adicionales de custodia. R08 humano/clave debe ser distinto de ambos R01/R02. Estos dos pueden compartir humano/clave sólo bajo cualificación, bindings de propósito y aprobaciones de dominio distintas; no se añade prohibición general. La preparación actual del mismo asistente no acredita review competente R01/R02/R06 ni aceptación separada R08, y no asigna/contacta personas.

## Unicidad global y constructor

La clave requerida es `(configuration_epoch, SHA256(JCS(C real completo)))`. Debe existir exactamente un mapping vigente en todos los callers, imágenes, dominios aprobados y restarts, hacia un solo bundle/caller/image/protection_domain/global_ledger_domain. No se extiende o particiona la clave por caller, imagen, dominio, proceso, restart o registry local. Una entrada observada o firma local no prueba ese cuantificador global.

La resolución autenticada debe ocurrir antes de P_ROOT_CHECK, seguida del freeze del mismo C/Q y constructor admitido. Conflictos, epoch obsoleto, rollback, revocación desconocida o estado global incierto rechazan. No se selecciona/configura backend, endpoint, registry, mapping o servicio; sus campos y la prueba de unicidad permanecen pendientes. No se define un nuevo schema positivo de mapping.

El worker nace en custodia intrínseca protegida, con primer entry inmutable, imagen/runtime/constructor exactos y endpoints heredados antes de código de repositorio no confiable. No deduce mapping de bytes ni recibe frame/recibo/canal I191 nuevo. No se presupone helper, proceso, pipe, fd, argv, confianza env o lectura oculta de repo/clave/schema. Un backend incapaz mantiene NOT_ADMITTED; no se añade transporte/attestation o cambia contrato automáticamente.

El dominio ledger del mapping debe concordar con el dominio global one-use aceptado. Mapping no equivale a claim: la atomicidad/durabilidad global de claim sigue siendo una obligación distinta, después de admisión completa del root y antes de paths/spawn, sin permiso por este dossier. No se crea worker o claim.

## Tamaño condicionado y costes

El modelo documental I192 se conserva y se recompone mediante aritmética de cotas publicadas, sin codificar un cuerpo positivo:

| Término efectivo del modelo | Bytes |
|---|---:|
| Actor registry / image manifest | 98 304 / 98 304 |
| Caller / plataforma / acceptance | 1 933 / 5 940 / 13 879 |
| Suma de registros | 218 360 |
| Estructura y aprobaciones del modelo | 3 284 |
| Bundle condicionado | 221 644 |
| Cap candidato / margen aritmético | 262 144 / 40 500 |

Cada término usa el mínimo entre upper de schema y cap individual, bajo los supuestos I192 de ASCII/safe-integer y escaping de strings a dos bytes por carácter. Los cinco cuerpos reales deben satisfacer sus caps separados, los schemas cerrados y las tres formas de aprobación. Si cambia el encoding, hace falta una cota revisada bajo los mismos límites, sin recorte. Ninguna de esas hipótesis, tamaños o fit se verifica aquí.

El upper histórico sin caps anidados de 368 348 tampoco demuestra tamaño real o inviabilidad. La cota condicionada no incluye toda la evidencia detrás de referencias, ni prueba heap/CPU/IO, servicio, fases o éxito en 900. El margen 40 500 no es reserva de recursos; no se convierte un coste desconocido en cero.

Los cuerpos de prueba completos deben existir y estar disponibles y revisados auténticamente. Lookup, freshness, identidad/crypto/measurement, copias, registry, recibo, native/IO y salidas siguen dentro de ambos Readers y el join global E01–E05 de launch/worker/finish, con fallos/cleanup. Enrollment/build offline no hace gratuitas esas operaciones. Un cambio de mapping, lookup, constructor, grafo, autores/cuerpos/claves/epoch/políticas o supuestos invalida dependientes y exige revalidar el join completo antes de avanzar. No se cambian cuotas, reservas o presupuestos ni se aplica rebind activo.

## Vigencia y fases posteriores

Los cinco registros, C y pruebas previas deben corresponder al mismo scope auténtico W10/W11. PJ11 requiere tres aprobaciones y confianza reales; PJ12 currentness efectiva de los registros y C contenido en los intervalos pertinentes, sin inventar intervalo del bundle o igualdad de extremos. Se conservan epoch concordante, lifetime ≤3600, error conservador ≤5, trusted-now y revocación conocida, sin mapping conflictivo. Fecha del host/cliente, TOFU, cache o lookup oculto no suministran esa prueba; no se crea snapshot.

Las futuras aprobaciones no autentican retrospectivamente sus antecedentes o W09/W10/W11. Mapping sigue a bundle/C y precede a P_ROOT_CHECK, sin depender del root/claim/recibo futuros. W13 conserva la decisión de gates y CE11 el handoff sin dependencia del recibo CE12. La autorización separada, admisión completa y claim/recibo reales siguen diferidos según I223. No se crean C/Q/request/root/bundle/mapping/claim/recibo ni autoridad.

## Comprobación y publicación

La [preparación revisada](../validation/D5-I247-preparation-review.json) registra tres schemas, cinco registros/88 campos, core ocho, bundle tres, tres aprobaciones/nueve slots, diez reglas y mapping de dos campos de clave/cinco de destino. El [auditor](../validation/D5-I247-audit.py) verifica 1032 pins, schemas/pointers/dominios/requisitos de mapping y modelo aritmético, reproduce reconstrucción y revisión I246 sin invocar mains históricos ni nuevas proyecciones de presencia, y rechaza 47 mutaciones documentales en memoria. El [sello](../validation/D5-I247-integrity.json) preserva 724 archivos publicados y los cuatro artefactos distintos del propio sello.

```text
python3 docs/validation/D5-I247-audit.py
PASS_STATIC_SOURCE_ONLY_W12_BUNDLE_APPROVALS_GLOBAL_MAPPING_MISSING_NOT_ADMITTED
```

Harness de runtime: **N/A**. Sólo documentos, Git, hashes, metadatos y comprobaciones documentales propias en memoria. Sin signing/keygen/crypto/codec positivos, import/compile/ejecución producto/componentes, discovery/tests, build, enrollment/provisión, configuración registry/mapping/backend/servicio, contactos, benchmarks o probes de reloj/CPU/IO/schedule/plataforma/ledger/claim/replay/crash/restart/procesos/endpoints. Sin nuevos helpers/canales/inputs/outputs, cuotas, reservas, bindings, autoridades o destinos. No se inspecciona ni limpia dev/run_data/D4 ni se reanudan I86/I89/I92.

I122 sigue IMPLEMENTED_NOT_ADMITTED, PJC115-R2 sin habilitar, E06 NOT_RUN, cero paquetes reales aceptados, cero gates de prelaunch cerrados y cero obligaciones E01–E05 cerradas. D5/H07 abiertos e IR03 NOT_READY. Publicar no acepta bundle, firmas, mapping, recursos o ejecución.

Unidad documental de cinco archivos; se declara el exceso de 400 líneas por trazabilidad y preservación. Reversión limitada a retirar exactamente:

- `docs/design/D5-I247-W12-BUNDLE-APPROVALS-GLOBAL-MAPPING.md`
- `docs/validation/D5-I223-W12-BUNDLE-APPROVALS-GLOBAL-MAPPING-CANDIDATE.json`
- `docs/validation/D5-I247-preparation-review.json`
- `docs/validation/D5-I247-audit.py`
- `docs/validation/D5-I247-integrity.json`

El siguiente paso documental es revisar W12 y sus fronteras de confianza, mapping, tamaño y costes. Su aceptación efectiva sigue exigiendo cuerpos, garantías y decisiones competentes genuinos; commit y push no los sustituyen.
