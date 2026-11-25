# I248 — W12 revisado; bundle, aprobaciones y mapping pendientes

La revisión documental de W12 de I247 encuentra consistentes sus requisitos de bundle, aprobaciones y mapping global con I223, CE10 y los contratos/schemas de custodia. No se identifica un nuevo defecto documental. **Se mantiene la no admisión**: faltan cuerpos, confianza independiente, firmas/provenance, unicidad global, constructor y decisiones genuinas. No se crea o acepta bundle o mapping real; SD01 permanece activo y D5 abierto.

Fecha: 2026-11-25, Europe/Madrid. Base: `0030e67825766179278b1b5b43b5073262f591d8`.

El objeto es [W12 candidato de I247](../validation/D5-I223-W12-BUNDLE-APPROVALS-GLOBAL-MAPPING-CANDIDATE.json). Se conservan sus bytes y los antecedentes. La reconstrucción metodológica del mismo asistente no acredita identidad, independencia, competencia R01/R02/R06 o aceptación separada R08.

## Resultado del contraste

| Objeto | Resultado documental | Pendiente real |
|---|---|---|
| Contrato W12 | Entregables, dependencias W02/W04/W10/W11, salidas y restricciones exactos I223 | Autoridad y dependencias aceptadas |
| Estructura | Cinco registros/88 campos; core cerrado ocho y bundle cerrado tres | Cuerpos, hashes, bytes, closures y aceptación |
| Aprobaciones | Tres roles, dominios exactos y un NUL sobre el mismo core completo | Actores/claves, mensajes, firmas, provenance y verificación |
| Confianza | Selección externa de anchors/políticas y separaciones conservadas | Registry/purpose/epoch/currentness y políticas reales aceptados |
| Mapping | Clave global de dos campos, destino único de cinco | Cuantificador global, provider/backend y evidencia contra conflictos/rollback |
| Constructor | Requisitos K07 y dominio global K14 conservados | Origen intrínseco, enforcement y capacidad reales |
| Tamaño | Aritmética condicionada I192 recompuesta sin codificar cuerpos | Supuestos de encoding/caps y fit real |

Los cinco registros conservan los schemas exactos y 8/26/13/14/27 campos requeridos. Sus valores, cuerpos canónicos, tamaños, hashes, autenticación previa, scope/epoch/vigencias y reviews siguen null. Los 88 slots no son cuerpos positivos, y los caps separados no demuestran completitud anidada o recursos. Las tres definiciones bundle/core/approval, las diez reglas y las siete políticas seleccionadas CE10 coinciden con sus fuentes, sin promover afirmaciones históricas de disponibilidad a hechos actuales.

## Cobertura completa y confianza independiente

R01/R02/R08 deben cubrir el mismo core real completo con dominios `D5/PGO181/CUSTODY/v1/R01`, `.../R02` y `.../R08`, cada uno seguido de un único octeto `0x00` antes de JCS del core. No se codifica un mensaje o vector positivo. Las firmas, hash propio del bundle, Q/root/recibo excluidos son miembros externos al core; no se recorta ningún campo de los ocho ni se cambia el payload por rol.

Los cinco registros y sus cinco hashes permanecen dentro del core. C se vincula indirectamente mediante acceptance.trust_context_sha256; no se añade un cuerpo C al signed_core o un hash del bundle a C/Q. Acceptance no tiene firma propia. El bundle sólo contiene schema, signed_core y approvals, sin validity independiente. Las decisiones de core/acceptance siguen siendo exclusivamente custodia, sin admisión runtime, de recursos o captura.

Se preservan pure-Ed25519 y las restricciones estrictas del perfil como requisitos sin verificar. Las dos firmas del root existente no sustituyen tres aprobaciones de custodia. Una firma o resultado crypto aislado tampoco prueba provenance, completitud, recursos o admisión. No se selecciona librería, genera clave o ejecuta verificación/signing/codec positivo.

El registry/anchor de confianza debe ser preexistente y aceptado por autoridad independiente, con propósito/actor/clave, epoch, vigencia y revocación auténticos. No se autofunda desde C, bundle, root, registry autofirmado o una clave del repositorio. Los pins de contrato/schema deben coincidir con la selección externa y políticas realmente implementadas en la imagen, sin elegirse desde el bundle recibido. Las futuras firmas no autentican retrospectivamente sus propios antecedentes.

Se conservan las ocho exclusiones S01, source-author/root-key y cuatro separaciones adicionales de custodia. R08 humano/clave sigue distinto de ambos R01/R02; estos dos sólo pueden coincidir bajo cualificación, bindings de propósito y aprobaciones de dominio separadas. No se añade prohibición general. Los cuatro roles siguen sin persona/appointment aceptado y no se contacta a personas o proveedores.

## Mapping global y constructor

La clave sigue siendo exactamente `(configuration_epoch, SHA256(JCS(C real completo)))`, con un único destino bundle/caller/image/protection_domain/global_ledger_domain en todo el ámbito de callers, imágenes, dominios aprobados y restarts. No se particiona o extiende por caller, imagen, dominio, proceso, restart o registry local. Una entrada observada o firma local no demuestra esa unicidad global.

La resolución autenticada debe preceder a P_ROOT_CHECK, seguida del freeze del mismo C/Q y constructor admitido. Conflicto, epoch obsoleto, rollback, revocación desconocida o estado global incierto rechazan. Ningún backend, endpoint, servicio o registry está seleccionado/configurado; prueba global, snapshot, destino y reviews reales siguen pendientes. No se define un schema positivo nuevo de mapping.

K07 mantiene primer entry inmutable e imagen/runtime/constructor auténticos antes del código no confiable. El worker nace en el dominio protegido; no infiere custodia de bytes ni recibe un frame/recibo/canal I191 nuevo. No se presupone helper, proceso, pipe, fd, argv, confianza env o lectura oculta de repo/clave/schema. Si el backend no puede establecer ese origen intrínseco, sigue NOT_ADMITTED; no se añade transporte/attestation ni cambia contrato automáticamente.

El ledger del mapping debe concordar con el dominio global one-use aceptado de K14. Mapping no es claim ni prueba atomicidad/durabilidad: el claim real sigue sujeto a admisión completa del root y previo a paths/spawn, con sus garantías globales y sin autorización por esta revisión. No se crea worker o claim.

## Cota condicionada y costes

La reconstrucción lee los uppers I192 y caps I191 y recompone términos efectivos sin ejecutar encoding de cuerpos:

| Término del modelo condicionado | Bytes |
|---|---:|
| Actor registry / image manifest | 98 304 / 98 304 |
| Caller / plataforma / acceptance | 1 933 / 5 940 / 13 879 |
| Suma de registros | 218 360 |
| Estructura y aprobaciones | 3 284 |
| Bundle condicionado | 221 644 |
| Cap candidato / margen | 262 144 / 40 500 |

Los términos son mínimos entre upper de schema y cap individual. La conclusión exige los supuestos ASCII/safe-integer, escaping a dos bytes por carácter, caps reales de los cinco cuerpos, schemas cerrados y tres formas de aprobación de I192. No se prueban aquí esos supuestos o tamaños. Encoding distinto exige una cota revisada bajo límites sin cambiar, sin recorte.

El upper sin caps anidados de 368 348 no demuestra tamaño real o inviabilidad. El margen 40 500 tampoco es reserva de heap/CPU. La cota no cubre toda la evidencia detrás de referencias ni demuestra servicio, IO, fases o éxito en 900. No se convierte un coste desconocido en cero o una suma candidata en aceptación.

Lookup/freshness, identidad/crypto/measurement, copias, registry, recibo, native/IO y salidas permanecen dentro de ambos Readers y el join global E01–E05, con fallos/cleanup. Lo offline no los hace gratuitos. Cambiar mapping/lookup/constructor/operaciones, grafo, autores/cuerpos/claves/epoch/políticas o supuestos invalida dependientes y requiere revalidar el join antes de avanzar. No se transfieren automáticamente hashes, aprobaciones, mapping o aceptación ni se cambia cuota/reserva o aplica rebind.

## Vigencia y fases posteriores

Las vigencias efectivas proceden de los cinco registros actuales con C contenido en los intervalos pertinentes, sin intervalo nuevo del bundle o igualdad forzada de extremos. Se mantienen epoch concordante, lifetime ≤3600, error conservador ≤5, trusted-now y revocación conocida, sin mapping conflictivo. Fecha del cliente/host, stale/TOFU, cache o lookup oculto no suministran esa evidencia. No se genera snapshot.

Los hechos W10/W11, valores de C, cuerpos de prueba y reviews previos siguen sin aceptación real. PJ11 exige cobertura de tres aprobaciones y confianza reales, y PJ12 currentness efectiva/proyección de C; no se satisfacen con flags o firmas futuras. W13 conserva la decisión de gates y CE11 el handoff sin dependencia del recibo CE12. La autorización separada, admisión completa y claim/recibo reales siguen diferidos según I223. No se emite C/Q/request/root/bundle/mapping/claim/recibo o autoridad.

## Comprobación y publicación

La [reconstrucción](../validation/D5-I248-I247-source-reconstruction.json) registra treinta criterios y 1037 pins contra los blobs del commit base. El [dictamen](../validation/D5-I248-I247-documentary-review.json) conserva los 47 rechazos I247 y añade 24 sobre estructura, registros/campos, dominios/delimitador/core, crypto, clave/destino/proof global, constructor/claim, modelo de tamaño, freshness/anchors, fases y costes.

El auditor contrasta fuentes primarias y pointers JSON y reproduce candidato/preparación I247 sin invocar mains históricos ni nuevas proyecciones de presencia. El [sello](../validation/D5-I248-integrity.json) preserva 729 archivos publicados y los cuatro artefactos distintos del propio sello.

```text
python3 docs/validation/D5-I248-audit.py
PASS_STATIC_SOURCE_ONLY_W12_REVIEW_BUNDLE_APPROVALS_GLOBAL_MAPPING_MISSING_NOT_ADMITTED
```

Harness de runtime: **N/A**. Sólo documentos, Git, hashes, metadatos y comprobaciones documentales propias en memoria. Sin signing/keygen/crypto/codec positivos, import/compile/ejecución producto/componentes, discovery/tests, build, enrollment/provisión, configuración registry/mapping/backend/servicio, contactos, benchmarks o probes de reloj/CPU/IO/schedule/plataforma/ledger/claim/replay/crash/restart/procesos/endpoints. Sin nuevos helpers/canales/inputs/outputs, cuotas, reservas, bindings, autoridades o destinos. No se inspecciona ni limpia dev/run_data/D4 ni se reanudan I86/I89/I92.

I122 sigue IMPLEMENTED_NOT_ADMITTED, PJC115-R2 sin habilitar, E06 NOT_RUN, cero paquetes reales aceptados, cero gates de prelaunch cerrados y cero obligaciones E01–E05 cerradas. D5/H07 abiertos e IR03 NOT_READY. Publicar no acepta bundle, firmas, mapping, recursos o ejecución.

Unidad documental de cinco archivos; se declara el exceso de 400 líneas por trazabilidad y preservación. Reversión limitada a retirar exactamente:

- `docs/design/D5-I248-I247-W12-REVIEW.md`
- `docs/validation/D5-I248-I247-source-reconstruction.json`
- `docs/validation/D5-I248-I247-documentary-review.json`
- `docs/validation/D5-I248-audit.py`
- `docs/validation/D5-I248-integrity.json`

El siguiente paquete documental I223 es W13, conservando la falta de evidencia y aceptación reales de sus antecedentes. El cierre efectivo sigue exigiendo las pruebas y decisiones competentes pendientes; commit y push no las sustituyen.
