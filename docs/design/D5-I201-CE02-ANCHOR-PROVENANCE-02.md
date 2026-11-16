# I201 — CE02 candidato 02 separa anchors previos de aprobaciones CE10

CE02 candidato 02 prepara la reparación documental de **F199-01**: la política,
provisión y aceptación previa genuinas de anchors permanecen en CE02; las
aprobaciones reales del core del bundle quedan expresamente diferidas a CE10.
La reparación requiere revisión de esta versión exacta, sin confirmación ni cierre
aceptado del hallazgo. Se mantiene la no admisión de PGO181 candidato 02/PJC115-R2,
D5 abierto e IR03 `NOT_READY`.

Fecha del cliente: 2026-11-16, Europe/Madrid. Base publicada I200:
`473507bacda8146813970011ec35acb24e941fd1`.

## Revisión trazable, sin reescribir los históricos

[El candidato 02](../validation/D5-I201-CE02-ANCHOR-PROVENANCE-CANDIDATE-02.json)
es un nuevo wrapper documental de evidencia faltante. `revision_binding` fija
el dossier I199 y `/findings/0` del dictamen I200. El `plan_binding` conservado
identifica la ruta histórica de entrega I193; `current_candidate_path` identifica
esta revisión. No se aplica ningún binding activo ni cambio en capture_inputs.

I199, I200 y el plan permanecen intactos. El hallazgo histórico sigue abierto en
su registro original; I201 registra `REPAIR_PREPARED_PENDING_DOCUMENTARY_REVIEW`,
con confirmación documental y cierre aceptado falsos. La tabla siguiente sustituye
AP08 sólo para esta versión, sin crear un dossier CE10 ni sus aprobaciones.

| Requisito | Consumidor | Evidencia o frontera exigida |
| --- | --- | --- |
| AP01 | CE02 | Origen y provisión independiente de configuración preexistente fuera de repo/C/bundle |
| AP02 | CE02 | Expectativa externa auténtica de digest/epochs y aceptación previa competente |
| AP03 | CE02 | Autoridad de identidad, humanos canónicos/alias y nombramientos/competencia genuinos |
| AP04 | CE02 | Bindings completos propósito/actor/clave, ordenados y únicos, sin truncar ni suplir identidades |
| AP05 | CE02 | Cuerpos completos de prueba realmente disponibles para revisión competente |
| AP06 | CE02 | Validez, epoch, reloj confiable, currentness y revocación conocida reales |
| AP07 | CE02 | Cuerpo registry real canónico/schema/hash y cap candidato 65.536 bytes |
| **AP08-ANCHOR-POLICY** | **CE02** | Provisión y aceptación previa auténticas, autoridad, expectativa externa y bindings de anchors; política exacta de dominios/core/profile/pack/contrato. No exige firmas futuras del bundle CE10 |
| **AP08-BUNDLE-APPROVAL** | **CE10, diferido** | Tres aprobaciones R01/R02/R08 reales sobre el mismo core, tras antecedentes/C auténticos y usando anchors CE02 ya aceptados independientemente. No autentican sus propios anchors |
| AP09 | CE02 | Custodia acotada y evidencia/costes completos; no prueba de capacidad a partir de caps de índices |

Las ocho filas ajenas a AP08 permanecen idénticas. Las diez filas siguen
`MISSING_NOT_EVALUATED`, sin proveedor, localizador, nombramiento, hash, tamaño,
registro de aceptación ni permiso de contacto. Nueve corresponden a obligaciones
previas CE02; una describe evidencia posterior CE10, sin hacerla requisito CE02.
No se crean personas, claves, firmas, C/core, registry o evidencia externa real.

## Política de aprobación y prueba de aprobación

`step_obligation_boundary.CE02` conserva CE01 como dependencia real y enumera los
nueve requisitos previos. Exige provisión/aceptación previa genuinas y autoridad
externa, digest/epochs y bindings auténticos; distingue política de aprobación
de aprobación real. Declara que no requiere aprobaciones futuras CE10 y que ni
C ni el bundle pueden proporcionar confianza retrospectiva a sus anchors.

`step_obligation_boundary.CE10` conserva exactamente CE02, CE08 y CE09 como
prerrequisitos I193. La aprobación real del core común sigue siendo necesaria en
esa fase, después de anchors aceptados y C/antecedentes exactos. Eliminar el
requisito prematuro de CE02 no elimina esa prueba posterior ni autoriza obtenerla.
El orden declarado sigue acíclico y ANCHOR precede a BUNDLE en I191.

Los dominios de firma y sus terminadores 0x00 se conservan como **política de
selección previa**, no como firmas disponibles. También permanecen completos los
requisitos K11 de selección independiente de profile/pack/contrato/propósito/clave
y de aprobaciones reales en su fase. Ninguna firma, clave suministrada, key_id,
hash de repo/C/bundle o autoafirmación crea su propia autoridad de confianza.

## Disponibilidad separada, sin sustituir aceptación previa

El slot ambiguo `actual_signature_or_custody_approvals` se elimina sólo de esta
revisión. Se mantiene `genuine_prior_acceptance_record` ausente y se añade
`genuine_prior_anchor_provisioning_acceptance_evidence`, también ausente, dentro
de `actual_anchor_state`. Esos hechos deben ser auténticos para aceptar CE02.
No se rebaja el requisito de aceptación previa ni se lo sustituye por una firma
futura o por esta reparación documental.

`future_CE10_bundle_approval_availability` registra por separado el consumidor
CE10 y la obligación diferida: aprobaciones, hash del core y hash de C ausentes,
evidencia/aceptación falsas, codec/cripto `NOT_RUN`, sin acción autorizada ni dossier
CE10 creado. Es metadato negativo del dossier CE02, no una instancia de registro
I191 ni un paquete CE10.

La dependencia competente CE01 continúa insatisfecha, aunque su candidato 02 y
la reparación F195-01 fueron confirmados documentalmente en I198. Las autoridades
externas, expected digest/epochs, identidades, claves, reloj/revocación, cuerpos
y decisiones R01/R02/R08 siguen ausentes. La fecha del chat no prueba currentness.
No se solicita contacto, enrollment, claves, firma, cripto o medición para suplirlas.

## Alcance conservado y límites de la preparación

Se conservan los tres requisitos CE02, dos checks, frontera de autorización y
K01/K03/K11/K13/K16, inventario de 14 documentos, tres slots de revisión sin
asignar y diez condiciones de rechazo no evaluadas. No cambia la política de
roles, ocho exclusiones S01, cuatro separaciones extra, completitud/aliases,
propósitos, orden/uniquidad, reglas de tiempo 3.600 s/error 5 s ni TOFU/fallback.
Los cuatro fragmentos de schema son idénticos; no se ejecuta validator o codec.

El cap candidato de 65.536 bytes se aplica al futuro cuerpo registry real, no a
este wrapper con pins. No demuestra capacidad de sus cuerpos subyacentes, heap,
CPU/IO o 900 s. El trabajo por intento de lookup/frescura/identidad/verificación,
copias/registry y nativo/IO sigue dentro de la composición completa de recursos
y fases; llamarlo offline no lo hace gratuito ni lo desplaza fuera de t0.
No cambian cuotas, reservas, presupuestos, schemas activos, canales o miembros Reader.

I122 permanece `IMPLEMENTED_NOT_ADMITTED`, CP03 verdadero sólo en su alcance
heredado sellado, CP07 falso, atomicidad correlacionada no verificada y componentes
`NOT_RUN`. Siguen las nueve condiciones completas CP07, E01–E05 abiertos, cero
obligaciones cerradas, E06 separado y no ejecutado, F179-01/S01 sin aceptación.
Las seis fuentes sucesoras y ocho cuerpos I191 siguen ausentes; los otros diez
dossiers planificados no se crean. No hay autoridad/root, destino, claim, worker,
rebind o cambio de capture_inputs.

El mismo asistente/chat prepara la revisión: no acredita independencia personal u
organizativa, competencia R01/R02 ni aceptación R08. Publicación y controles
documentales no satisfacen esas decisiones. CE02 queda preparado para revisión,
sin evidencia real, adopción, aceptación, admisión o cierre de D5.

## Verificación y publicación

```sh
python3 docs/validation/D5-I201-audit.py
```

Resultado exigido: `PASS_STATIC_SOURCE_ONLY_REPAIR_PREPARED_EVIDENCE_MISSING`.
[La preparación reproducible](../validation/D5-I201-preparation-review.json)
contrasta 802 pins con Git/disco, reproduce I200 sin sus `main` de publicación y
compara con I199 mediante una lista cerrada de cambios. Los históricos conservan
sus propias proyecciones de presencia; esta revisión se exige en su ruta real.
[El sello](../validation/D5-I201-integrity.json) preserva 494 archivos publicados y
fija los otros cuatro artefactos de esta unidad.

Siete contraejemplos sólo en memoria deben rechazarse: asignar aprobación futura
a CE02; exigirla para CE02; eximir aceptación previa genuina; permitir al bundle
autenticar sus anchors; autorizar CE10 desde esta revisión; omitir CE02 como
prerrequisito CE10; o volver a mezclar la disponibilidad previa y futura. Son
controles documentales, sin ejecutar producto, componentes, protocolo o cripto.
Harness runtime: N/A, revisión documental sin registry codec/imagen/claim real.

Unidad única superior a 400 líneas por pins, matrices y preservación; se declara
el exceso sin reducir evidencia. Commit/push publica para revisión estos cinco
archivos y limita la reversión a ellos:

- `docs/design/D5-I201-CE02-ANCHOR-PROVENANCE-02.md`
- `docs/validation/D5-I201-CE02-ANCHOR-PROVENANCE-CANDIDATE-02.json`
- `docs/validation/D5-I201-preparation-review.json`
- `docs/validation/D5-I201-audit.py`
- `docs/validation/D5-I201-integrity.json`

El siguiente alcance es revisar el candidato 02 exacto y su reparación F199-01.
La evidencia externa genuina y la aceptación competente CE01/CE02 siguen pendientes
por separado, sin habilitar ejecución, cuotas o cierre D5.
