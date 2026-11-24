# I228 — W02 consistente documentalmente; personas y anchors siguen pendientes

Fecha: 2026-11-24 · I223/W02 · PGO181 candidato 02 · PFC126-CANDIDATE-03/I122.

La revisión de [W02 preparado en I227](D5-I227-W02-PEOPLE-AND-ANCHORS.md) confirma la consistencia documental de personas, anchors y fronteras de fase con I223 y sus políticas de referencia. **Cero hallazgos de corrección documental. W01 y W02 siguen sin aceptar; SD01 permanece activo.** Faltan autoridad de entrada, evidencia auténtica de personas/anchors y decisiones competentes. Se mantiene la no admisión de PJC115-R2, D5 abierto e IR03 `NOT_READY`.

El [dictamen estructurado](../validation/D5-I228-I227-documentary-review.json) registra cinco precisiones de alcance. La [reconstrucción](../validation/D5-I228-I227-source-reconstruction.json) fija 937 pins, 16 criterios y el mapping exacto de requisitos por consumidor. El [candidato W02](../validation/D5-I223-W02-PEOPLE-AND-ANCHORS-CANDIDATE.json) y todos los antecedentes permanecen intactos. El mismo asistente preparó I227 y realiza esta revisión metodológica: no acredita independencia de actor, competencia R06 ni aceptación separada R08.

## Tres entregables, sin aceptación real

| Entregable I223/W02 | Contraste documental | Pendiente real |
|---|---|---|
| Personas y claves por propósito | Ocho roles R01–R08 y cinco categorías adicionales cubren autores, preparadores, requester, proveedores de pruebas y custodios/firmantes | Humanos canónicos, organizaciones/alias, competencia, appointments, vigencia, evidencia y bindings propósito/clave genuinos |
| Política y registro de anchors | Requisitos de provisión/origen/aceptación previa independientes, expectativa externa de digest/epochs, cuerpos y currentness conservados | Autoridad externa auténtica, registry realmente provisionado/aceptado, claves, pruebas completas, reloj/revocación y decisiones reales |
| Separaciones | Ocho exclusiones S01, dos source-author/root-key y cuatro de custodia: 14 reglas sin comparaciones reales verificadas | Resolución canónica y evidencia de separaciones sobre humanos y claves auténticos |

Ocho roles más cinco categorías no implican trece personas. La compatibilidad de scopes y las separaciones se decidirán sobre humanos canónicos autenticados. El principal software caller no sustituye al humano responsable. Nombres, cuentas Git, strings distintos, claves distintas o flags aceptados no demuestran identidades diferentes, competencia ni independencia.

El tracking de preparación de I227 declara la actividad documental del asistente, sin convertirlo en humano enrolado. Humano canónico, organización, prueba de autoría, hash de contribución auténtica y preparation_record positivo siguen nulos. La completitud final deberá cubrir todos los preparadores pertinentes, no sólo autores de fuentes o participantes de este chat.

## Fronteras de fase confirmadas

| Consumidor | Requisitos exactos | Dictamen |
|---|---|---|
| W02 / CE02 | Nueve: AP01–AP07, AP08-ANCHOR-POLICY, AP09 | Provisión y aceptación previa genuinas siguen exigidas; política de firma no equivale a firmas disponibles |
| W02 / CE03 provisional | Ocho: IR01–IR08 | Intake de personas conocidas, con evidencia auténtica cuando exista; sin final completeness ni preaprobación de autores futuros |
| W10 / CE08 | IR09 | Freeze final tras conocer autores y pruebas; actor_registry → image_manifest → caller_identity → platform_custody antes de C |
| W12 / CE10 | AP08-BUNDLE-APPROVAL | Tres aprobaciones reales del mismo core tras anchors/antecedentes/C aceptados; obligación diferida, sin eximirla ni anticiparla a W02 |

El mapping 17/1/1 coincide con los 19 requisitos originales. La reparación F199-01 de CE02 candidato 02, confirmada documentalmente en I202, permanece: un bundle futuro no autentica sus propios anchors y su firma no puede ser la única autenticación previa. La política exacta de dominios/core/profile/pack/contrato sigue seleccionándose independientemente. Los dossiers CE08/CE10 existentes son documentos; no prueban registries, freeze, core o aprobaciones reales.

W02 no requiere el freeze final W10 para su intake provisional. Aun así, los autores reales W05–W08, los cuerpos completos y los hechos baseline deben existir y estar autenticados antes de aceptar las pruebas en W09. W10 sólo reconcilia los mismos hechos/scope aceptados; no aporta autenticación retrospectiva. Cambios de contribuyentes, alias, cuerpos, sources/runtime/imagen, dominio, epoch/key, política o scope invalidan hashes/revisiones dependientes y requieren recualificación/revisión de lo afectado.

Ningún autor de prueba se convierte automáticamente en revisor R03/R06 o aceptante R08. La política incluye todos los preparadores auténticos y sus exclusiones. R08 conserva separación de humano/key frente a R01 y R02, además de source-author y root-key; R01/R02 pueden coincidir para el mismo humano genuinamente competente en ambos scopes, con aprobaciones de dominio separadas en su fase. No se añade una prohibición general R01/R02.

Cada preparation_record futuro debe acreditar actor y contribución auténticos, perfil02/schema exactos y correspondencia completa con la proyección C. No puede pinchar C, acceptance, bundle o root futuro; un hash documental no suple la prueba de autoría ni crea autoridad.

## Autoridad, currentness y recursos

W01 sigue sin aceptar y SD01 activo. Preparar/revisar/publicar W02 es trabajo documental autorizado; no satisface la dependencia W01 ni aporta nombramientos genuinos. W02 o las aprobaciones futuras tampoco pueden ser la única autoridad pronosticada de entrada. No se nomina ni contacta a personas, no se provisionan claves ni se ejecuta enrollment o verificación operativa.

La política de anchors exige configuración previa independiente de repo/C/bundle/root, digest esperado externo, epochs y bindings completos/ordenados/únicos por propósito y clave. Registry autofirmado, clave suministrada o key_id no crea confianza. La aceptación previa competente no se sustituye por política, hash, firma futura o estado del plan.

Se conservan los tres dominios de custodia y terminador 0x00, vida máxima 3.600 segundos y error confiable máximo 5 segundos, sin tomar muestras ni ejecutar crypto/codec. La fecha del chat no prueba currentness. No se admite TOFU, cache obsoleta o lookup oculto online/archivo, ni se promete descubrir instantáneamente toda revocación. Epoch, validez, reloj, revocación y cuerpos referenciados siguen ausentes.

Los siete fragmentos I191 permanecen exactos. Los caps candidatos son 65.536 bytes para anchor_registry y 98.304 para actor_registry: no son cuotas activas, límites de este wrapper o prueba de fit del registro desconocido y sus cuerpos subyacentes. No se trunca evidencia para cumplirlos ni se atribuye capacidad de heap/CPU/IO/servicio/900 segundos a schemas o índices.

El trabajo por intento de lookup/frescura/identidad/verificación/copias/registry/recibo/nativo/IO sigue dentro de la composición completa de recursos y fases. Enrollment humano previo o llamar offline a los hechos no permite omitir trabajo requerido durante launch. No se aplican cuotas, reservas, rebind, configuración activa, nuevos helpers/canales/miembros Reader o salidas.

## Dictamen y estado preservado

Los tres predicados de salida se conservan y permanecen sin evidencia, revisión primaria R06 o aceptación R08 reales. `W02-REAL-EVIDENCE-PACKAGE` sigue siendo el entregable previsto, sin paquete auténtico aceptado ni registro I191 positivo. La ausencia de evidencia está declarada como impedimento real; este PASS documental no la remedia ni acredita viabilidad/capacidad operativa.

Después de I228 continúan cero paquetes aceptados, cero de los 30 gates cerrados y cero obligaciones E01–E05 cerradas. I122 conserva `IMPLEMENTED_NOT_ADMITTED`, CP03 sólo en scope heredado, CP07/atomicidad correlacionada sin verificar y componentes `NOT_RUN`. No se emite `SOURCE_CAPACITY_VERIFIED` ni se habilita ejecución. Prelaunch/recursos permanecen separados de E06/Q/root/admisión/claim/recibo finales; CE12 sigue privado y deferido, sin eventos reales creados aquí.

## Verificación y publicación

Comando exclusivamente documental: `python3 docs/validation/D5-I228-audit.py`.

Resultado: `PASS_STATIC_SOURCE_ONLY_W02_REVIEW_PEOPLE_ANCHORS_MISSING_NOT_ADMITTED`. La auditoría compara independientemente I223/CE01/CE02/CE03/I191 con los ledgers de I227, resuelve JSON pointers y verifica 937 pins contra blobs de la base I227 `4a6f0613d583de09d4aca0c3f4e7ecc4b21a3410`. Preserva 629 archivos publicados y exige cinco nuevos. Reproduce candidato y revisión de preparación I227 sin ejecutar mains históricos de publicación ni añadir proyección de presencia, y comprueba restauración del método de consulta. Veintidós mutaciones documentales en memoria se rechazan. Estas comprobaciones metodológicas no sustituyen aceptación competente independiente.

Runtime harness: **N/A**. Sólo documentos/JSON/Git/hashes y comprobaciones propias; sin ejecución/import/compile de producto o componentes, tests/benchmarks, builds, codecs/crypto positivos, probes/reloj/ledger/claim/procesos de captura, signing/keygen, enrollment/provisioning/servicios ni contactos. No se cambian cuotas, reservas, fuentes, authorities/destinos, bindings o configuración activa.

Unidad documental única con commit/push solicitados, sin PR. Se declara el exceso de 400 líneas por pins, mapping, comprobaciones y preservación. La reversión exacta retira sólo:

- `docs/design/D5-I228-I227-W02-REVIEW.md`
- `docs/validation/D5-I228-I227-source-reconstruction.json`
- `docs/validation/D5-I228-I227-documentary-review.json`
- `docs/validation/D5-I228-audit.py`
- `docs/validation/D5-I228-integrity.json`
