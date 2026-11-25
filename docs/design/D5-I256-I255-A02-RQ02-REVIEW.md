# I256 — revisión de A02/RQ02: personas, appointments, anchors y fases

**No se encuentran defectos documentales nuevos en A02/RQ02 de I255.** El dossier mantiene el bloqueo A01, los requisitos genuinos de identidad/competencia/appointments/anchors y las fronteras provisionales/finales de W02. A01/W01 y A02/W02 siguen sin aceptar; SD01 permanece activo y se mantiene la **no admisión**. RQ02 no se envía.

Fecha: 2026-11-25, Europe/Madrid. Base: `b01db76fdfaf658fc899c24b7f188f19757a03db`.

La revisión contrasta el [dossier I255](D5-I255-A02-RQ02-PEOPLE-APPOINTMENTS-ANCHORS.md) con [I251](D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.md), W02 y sus fuentes normativas de anchors, identidad y custodia. Es una revisión metodológica del mismo asistente: no aporta humanos canónicos, autoridad, appointment, revisión competente R06 o aceptación separada R08. Los hitos materiales M01/M02 continúan pendientes.

## Dictamen por frontera

| Frontera | Resultado documental y evidencia genuina pendiente |
|---|---|
| A01 → A02 | El requisito A01/W01 aceptado se conserva. I253/I254 documentales no lo satisfacen; preparar/revisar un borrador no inicia intake positivo, envío, contacto o nominación. |
| Humanos canónicos | Ocho roles y cinco categorías conservan sus requisitos completos. Identidad/aliases/organización, competencia/appointments y claves de propósito requieren autoridad/provenance auténticas. Nombres, strings, cuentas Git, asistente o principal software no prueban humanos o independencia. |
| Anchors previos | Expected digest/epochs, política, origen/provisión y aceptación previos deben ser auténticos y seleccionados independientemente de registry suministrado, repo, C/bundle/root o self-signature. |
| Política frente a aprobación | AP08-ANCHOR-POLICY pertenece al antecedente A02. Las tres aprobaciones reales sobre el mismo core pertenecen a W12/CE10 y no pueden autenticar sus propios anchors. |
| Intake frente a freeze | IR01–IR08 pertenecen al intake provisional; IR09 finaliza la completitud real en W10/CE08. No se exige registry final temprano ni se preaprueban autores futuros. |
| Autenticación de recursos | Autores/cuerpos W05–W08 y hechos baseline auténticos preceden a W09. W10 reconcilia esos mismos hechos; no los autentica retrospectivamente. |
| Handoff | A03/RQ03 permanece detenido; requiere A01 y A02 genuinamente aceptados, con autoridad y límites propios. Esta revisión no autoriza contactar o ejecutar. |

La posibilidad de preparar documentos bajo la petición actual no acredita autoridad de entrada o identidad. A02 tampoco puede aportar la única justificación futura de A01. Una eventual aportación sólo podrá considerarse con autoridad/provenance propias y respetando el gate previo; este trabajo no recibe o evalúa material externo.

## Roles, sujetos y separación

Se contrastan directamente las ocho filas R01–R08 con la matriz W02, incluidas sus competencias y ámbitos exactos de decisión: runtime/imagen, plataforma/servicio, recursos, custodia de componentes, revisión de componentes, admisión/provenance/Reader, emisión de autoridad y aceptación separada. El dossier no asigna personas, claves o facultades operativas. Ser autor/provider de una prueba no convierte automáticamente al sujeto en R03, R06 o R08.

Las cinco categorías abarcan autores de fuentes, todos los preparadores documentales, requester humano, autores/providers de pruebas y custodios/signatarios. La resolución genuina debe cubrir aliases y colisiones, organizaciones, scope/validez/revocación y provenance. El namespace de humanos está separado del principal software; una clave o firma aislada no prueba identidad, competencia, appointment o separación.

Se preservan catorce requisitos: ocho exclusiones S01, source-author/root-key y cuatro separaciones adicionales de custodia. Se aplican a todos los preparadores/autores pertinentes, no sólo a una lista parcial de nombres. R08 humano y clave siguen separados de R01/R02 bajo las reglas existentes. La coincidencia R01/R02 sólo se permite para el mismo humano genuinamente cualificado con aprobaciones por dominio distintas en su fase; no se añade una prohibición general ni se exige que esas aprobaciones futuras existan ya en A02.

El seguimiento de la contribución I255 identifica la actividad documental y sus cinco archivos. No identifica por deducción al humano responsable, no acredita autoría por hash Git y no emite preparation_record positivo. Se mantienen los requisitos de contribución auténtica y pins exactos de perfil/schema, sin backpins a C/acceptance/bundle/root y sin declarar completitud final de preparadores.

## Anchors, política y currentness

El ledger se contrasta tanto con W02 como con cada fuente normativa de sus diecinueve filas. La selección independiente de expected digest/epochs debe preceder a los bytes suministrados. Calcular un digest de esos bytes sólo acredita integridad de ese cuerpo, sin convertirlo en valor esperado o autoridad. Repo, variable de entorno, archivo de claves, supplied key, C/bundle/root, self-signature, TOFU, cache obsoleta o fetch oculto no reemplazan autoridad externa y aceptación previas genuinas.

Se conservan orden y unicidad por `(purpose,key_id)`, actor canónico por binding y los tres propósitos de custodia. Los dominios exactos `D5/PGO181/CUSTODY/v1/R01`, `D5/PGO181/CUSTODY/v1/R02` y `D5/PGO181/CUSTODY/v1/R08` mantienen un único octeto NUL separador. Son reglas de selección, sin firma o aprobación creada por revisarlas.

Schemas cerrados y caps candidatos —65536 para anchor registry y 98304 para actor registry— siguen siendo exigencias, sin cortar keys, actores, aliases, preparadores o evidencia para caber. La completitud final y el fit del actor registry se revisan en W10; el cap de un índice no demuestra disponibilidad o coste de todos los cuerpos referenciados. No se crea registry, clave, snapshot, enrollment o validación positiva de codec/crypto.

Las reglas exactas de vigencia/epoch/currentness/revocación se preservan, con lifetime≤3600 y error confiable≤5 en sus fronteras aplicables, `not_before<expires_at`, contención y comprobación de intervalos. Los facts de enrollment/build de larga vida no se confunden con snapshots/C/bundle/claves actuales. La fecha de revisión no acredita frescura; status offline limitado por vigencia no promete revocación instantánea. Estados desconocidos, superseded, expired, revoked o ambiguos rechazan. No se consulta reloj/servicio ni se emiten snapshots frescos; hacerlo requiere evidencia lista y autoridad propia en su fase.

## Requisitos, retornos y fases diferidas

| Grupo | Tratamiento conservado |
|---|---|
| AP01–AP07, AP08-ANCHOR-POLICY, AP09 | Nueve requisitos previos de anchors/política para A02/W02 |
| IR01–IR08 | Ocho requisitos de intake humano/contribuciones/esquemas para A02/W02 |
| AP08-BUNDLE-APPROVAL | Diferido a W12/CE10, después de antecedentes auténticos y C/core exactos; tres roles sobre el mismo core |
| IR09 | Diferido a W10/CE08: completitud final y actor registry antes de imagen→caller→plataforma→C |

Los 17 requisitos aplicables a A02 son requisitos documentales todavía insatisfechos, sin progreso positivo actual. Los dos diferidos permanecen en el ledger y no se eliminan o convierten en prerrequisitos tempranos. Los metadatos históricos de las fuentes sobre creación de dossiers no se reinterpretan como ausencia actual: los dossiers CE posteriores existen documentalmente, sin aportar firmas, cuerpos o decisiones genuinos.

Los seis retornos IT01–IT06 cubren autoridad y A01; humanos/aliases; competencia/appointments; anchors; separaciones/contribuciones; e inventario/revisión/decisión. Los tres entregables originales W02 conservan sus textos y enlaces: personas/roles, anchors independientes y matriz de separación, todos con IT01 y revisión/decisión IT06. Los catorce criterios y las tres salidas W02 permanecen pendientes sobre el mismo scope y cuerpos, sin aceptar una lista parcial como cierre.

El contrato de entrega sigue exigiendo todos los cuerpos y referencias reales disponibles, bytes/digests/locators, autor/provider/custodia/provenance, scope, unidades y todos los supuestos, identidad/competencia/appointments/independencia, validez/currentness y motivos de revisión/decisión separados. Inventario null y cero cuerpos aportados/rechazados/evaluados no constituyen aceptación ni ausencia global o inviabilidad. Las 69 plantillas de referencia no son cuerpos únicos o clausura real.

Los autores conocidos y cuerpos auténticos antes de W09 son compatibles con un intake provisional: los nuevos autores o hechos posteriores requieren revisar lo afectado antes de aceptar sus pruebas. W10 no puede corregir retrospectivamente una falta de autenticación previa. Cambios de identidad/alias/autor/preparador/cuerpo/source/runtime/epoch/key/policy/revocación invalidan los dependientes, sin transferencia automática de appointments, pruebas o aprobación, refresh/rebind activo o nuevos permisos.

## Costes, handoff y no admisión

Ambos Readers y el join global mantienen los costes completos de lookup/freshness/identidad/crypto/native/IO/copias/registry/ledger/recibo/salidas/fallos/cleanup. Documentos o trabajo humano/offline no crean costes gratuitos, inputs/helpers/canales ocultos o salidas nuevas. Caps, presupuestos y firmas no prueban heap completo, disponibilidad, CPU/servicio o éxito900; cuotas y reservas permanecen intactas.

A03/RQ03 no se envía, inicia o acepta. Una eventual aceptación genuina de A02 sólo permitiría considerar el siguiente lote junto con A01 y sus límites propios; no autoriza contacto, nominación, provisión, firma, crypto/configuración, ejecución o cierre de D5. Esta revisión es del mismo asistente preparador, sin independencia organizativa/canónica acreditada y sin sustituir revisión competente R06 o aceptación separada R08.

CE12 sigue privado, diferido y no autorizado. Ejecución final E06/payload/Q/root/admisión/claim/recibo no se añade como nueva condición de aceptación prelaunch. Se conservan los cuatro prerrequisitos externos antes del claim y el claim/construcción protegida antes del recibo, sin claim como su propia precondición ni retry gratuito por estados inciertos, parciales, expirados o fallidos.

Se mantienen A01/W01 y A02/W02 sin aceptar, SD01 activo, cero lotes/gates/obligaciones cerrados, treinta gates pendientes y E01–E05 abiertas. I122 sigue IMPLEMENTED_NOT_ADMITTED, CP07 falso, atomicidad correlacionada sin verificar, componentes/E06 NOT_RUN, PJC115-R2 sin habilitar, D5/H07 abiertos e IR03 NOT_READY. Ningún cuerpo de fuentes/runtime, C/Q/root/binding, autoridad/destino, mapping/claim/worker/recibo o recurso reservado se crea aquí.

## Verificación y publicación

La [reconstrucción](../validation/D5-I256-I255-source-reconstruction.json) fija 1077 entradas contra blobs del commit base y registra 28 criterios. El [dictamen](../validation/D5-I256-I255-documentary-review.json) reproduce candidato/preparación I255 sin llamar mains de publicación históricos, conserva sus 39 rechazos documentales y añade 34 mutaciones en memoria sobre dependencia, roles, sujetos, requisitos, confianza, fases, separación, retornos, aceptación, costes y handoff. El [sello](../validation/D5-I256-integrity.json) preserva 769 archivos publicados y cuatro artefactos propios distintos del sello.

```text
python3 docs/validation/D5-I256-audit.py
PASS_STATIC_SOURCE_ONLY_A02_RQ02_REVIEW_A01_UNACCEPTED_PEOPLE_ANCHORS_AND_GENUINE_DECISIONS_PENDING_NOT_ADMITTED
```

Harness de runtime: **N/A**. Sólo JSON/Git/hashes/pointers/roles/requisitos/fases y comprobaciones documentales propias. Sin importar/compilar/ejecutar producto/componentes, discovery/tests/E06, build, benchmarks, crypto/codec positivos, firma/keygen/enrollment/provisión/contactos/configuración registry/mapping/reloj/ledger/servicio o probes CPU/IO/procesos/endpoints/replay/crash/restart. Sin cuotas/reservas/capture_inputs o nuevos inputs/outputs/helpers/canales. No se inspecciona/limpia dev/run_data/D4 ni se reanudan I86/I89/I92.

Una unidad documental, con exceso de 400 líneas declarado por reconstrucción, pins y preservación; sin PR solicitado. Reversión limitada a retirar exactamente:

- `docs/design/D5-I256-I255-A02-RQ02-REVIEW.md`
- `docs/validation/D5-I256-I255-source-reconstruction.json`
- `docs/validation/D5-I256-I255-documentary-review.json`
- `docs/validation/D5-I256-audit.py`
- `docs/validation/D5-I256-integrity.json`

I256 termina la revisión documental del borrador A02/RQ02. La autoridad de entrada A01 y el material/aceptación genuinos A02 siguen pendientes; esta publicación no cumple M01/M02 ni permite sustituir esos hitos por otro PASS documental.
