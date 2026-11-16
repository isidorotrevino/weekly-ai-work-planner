# I199 — CE02 preparado con evidencia de anchors ausente

CE02 (ANCHOR-PROVENANCE) queda **preparado como dossier documental de evidencia
faltante**, sin registro de anchors, autoridad, identidad, claves o aceptación
reales. I193 permite en el estado actual únicamente declarar esa ausencia.
PGO181 candidato 02/PJC115-R2 conservan la no admisión; D5 sigue abierto e IR03
`NOT_READY`.

Fecha del cliente: 2026-11-16, Europe/Madrid. Base publicada I198:
`8d63df3249a99c68cdab50849618357742b61726`.

## Entrega y dependencia de CE01

[CE02 candidato](../validation/D5-I193-CE02-ANCHOR-PROVENANCE-CANDIDATE.json) ocupa
la ruta exacta de `/steps/1` de I193. Fija los tres requisitos de evidencia,
dos checks, frontera de autorización y K01/K03/K11/K13/K16, junto con el gate
`FAMILY-ANCHOR_REGISTRY` de la checklist. Es un wrapper negativo con schema
documental propio; no es una instancia positiva I191 rellenada con nulos.

La dependencia CE01 sigue sin satisfacer en términos de aceptación real.
[CE01 candidato 02](../validation/D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json)
y [su dictamen I198](../validation/D5-I198-I197-documentary-review.json) confirman
la reparación documental de F195-01, sin adopción competente R06/R08. La petición
I199 autoriza preparar este dossier de pendientes; no permite saltar ese gate ni
aceptar CE02. El plan y los registros históricos permanecen intactos.

## Evidencia requerida y estado actual

El inventario fija 14 documentos por hash y tamaño físico: I193, checklist,
I191/pack, CE01/I198, S01/I122 y las referencias I192/perfil02/protocolo/output/
transporte. Son fuentes documentales, no origen externo de confianza ni digest
esperado de un registry. Los 792 pins se contrastan con Git y disco.

| Obligación | Evidencia auténtica necesaria | Estado |
| --- | --- | --- |
| AP01 — origen y provisión | Configuración preexistente del dominio protegido, seleccionada y provisionada independientemente fuera de repo/C/bundle | Ausente |
| AP02 — expectativa externa | Digest/epochs esperados auténticos y aceptación previa competente; no derivados del objeto suministrado | Ausente |
| AP03 — autoridad e identidad | Autoridad de identidad, humanos canónicos/alias, competencia y nombramientos genuinos | Ausente |
| AP04 — propósito/actor/clave | Bindings públicos completos, ordenados y únicos por `(purpose,key_id)` y actor canónico | Ausente |
| AP05 — cuerpos completos | Todos los cuerpos de evidencia referenciados, localizadores, digests y alcance disponibles para revisión competente | Ausente |
| AP06 — vigencia | Epoch actual, reloj confiable, revocación conocida, límites temporales y currentness en cada frontera | Ausente |
| AP07 — cuerpo canónico | Registry real, codec/schema cerrados, hash físico auténtico y tamaño dentro de 65.536 bytes | Ausente; no validado |
| AP08 — aprobaciones | R01/R02/R08 genuinos y separados según política, claves externas por propósito y core común con dominios exactos | Ausente; sin cripto |
| AP09 — custodia y recursos | Entrega acotada, cuerpos subyacentes y costes completos de lookup/frescura/verificación/copias/nativo/IO | Ausente; no hay prueba de capacidad |

Las nueve filas conservan proveedor, localizador, nombramiento, hash, tamaño y
aceptación reales ausentes. No se nomina ni contacta con proveedores. No hay
registry body, digest esperado, epoch, clave pública, firma, reloj o evidencia
real suministrados. No se solicitan ni generan claves privadas, ni se fabrican
hashes, firmas, atestaciones, PASS o estados de confianza.

Los slots de revisión R01/R02/R08 conservan sus scopes y separaciones, sin
persona, identidad canónica, nombramiento, competencia, clave/vigencia o permiso
actual. El mismo asistente/chat prepara el dossier; no acredita independencia
personal u organizativa ni actúa como autoridad externa o aceptador competente.

## Frontera de confianza y controles pendientes

La expectativa de digest/epoch y la aceptación de la autoridad deben existir
independientemente del registry suministrado. Ni una firma del propio registro,
ni su `key_id`, ni C/bundle/repo pueden seleccionar sus propios anchors o convertir
un hash documental en una expectativa externa auténtica. Ningún esquema o
aprobación sustituye procedencia, completitud o verdad de los cuerpos de prueba.

El dossier conserva como obligaciones, sin implementarlas ni ejecutarlas:

- Registry cerrado de nueve campos; entradas anchor_key de cinco campos, tres
  propósitos y entre tres y 64 claves; referencias de evidencia y validez exactas.
- Completitud y orden/uniquidad por propósito/key_id con un actor canónico por
  binding. No se truncan listas para caber. R01/R02 sólo pueden compartir para
  el mismo humano genuinamente cualificado, con aprobaciones de dominio separadas;
  las separaciones adicionales de R08 por humano y clave siguen vigentes.
- Los tres dominios `D5/PGO181/CUSTODY/v1/R01`, `/R02`, `/R08`, cada uno seguido
  de un único octeto 0x00, y el mismo core canónico. Claves, pack/contrato y
  propósitos se seleccionan externamente, sin ejecutar firmas o verificación.
- `not_before < expires_at`, lifetime máximo 3.600 s, error confiable máximo 5 s
  y condiciones exactas de tiempo del perfil02 en cada frontera; rechazo ante
  estado desconocido, cambiado, expirado, revocado o ambiguo. No se promete
  descubrir instantáneamente todas las revocaciones ni se usa la fecha del chat
  como prueba de reloj o frescura.
- No TOFU, stale-cache, lookup online/archivo oculto ni fallback de confianza.
  Los cuerpos subyacentes y el trabajo por intento siguen en el alcance completo
  de recursos; llamar offline al trabajo no lo hace gratuito ni lo saca de t0.

Se enumeran diez causas de rechazo, todas **no evaluadas sobre datos reales**:
autoridad/origen ausentes; bootstrap autofirmado o por clave suministrada;
expectativa derivada del objeto; mismatch de digest/epoch; identidad/propósito/
clave desconocidos; evidencia incompleta; snapshot inválido; reloj/currentness
ausentes; cuerpo no canónico/schema/cap inválidos; y aceptación previa ausente.
El presente dictamen de preparación no realiza esos controles reales.

**65.536 bytes es la cota candidata del futuro cuerpo registry**, no una cuota
aplicada ni el límite de este dossier documental. El wrapper contiene pins y
fragmentos de schemas, no el registry. No se ha ejecutado codec, schema validator
de componentes, firma, lookup o medición sobre un cuerpo real. El cap del índice
no limita por sí solo los cuerpos de evidencia, el heap o los costes de CPU/IO.

## Preservación y no admisión

Siguen las ocho exclusiones S01, cuatro separaciones extra de custodia, nueve
condiciones completas CP07, todos los candidatos numéricos y las cotas anteriores.
I122 continúa `IMPLEMENTED_NOT_ADMITTED`, CP03 verdadero sólo en su alcance
heredado sellado, CP07 falso, atomicidad correlacionada no verificada y componentes
`NOT_RUN`. E01–E05 permanecen abiertos, cero obligaciones cerradas; E06 separado y
sin ejecutar. No se transfiere prueba al sucesor ni se acepta F179-01/S01.

No cambian producto, componentes, schemas activos, cuotas, reservas, presupuestos,
Reader, canales, capture_inputs o bindings activos. No se crea autoridad/root,
destino, imagen/runtime, claim, worker o registro de confianza. Las seis fuentes
sucesoras y los ocho cuerpos reales I191 siguen ausentes. Los otros diez dossiers
planificados siguen sin crear; CE01 original y su candidato 02 permanecen intactos.

## Verificación histórica y actual

Crear CE02 en la ruta I193 no reescribe las afirmaciones históricas de ausencia.
La auditoría I199 prueba con `git ls-tree` que esta ruta exacta estaba ausente en
la base I198. Sólo durante la reproducción de funciones documentales heredadas
I198 proyecta esa consulta de presencia al estado base. El guard histórico CE01
de I195 continúa original, con sus comprobaciones de restauración heredadas.

La proyección exterior CE02 se restaura en `finally`. Todas las otras rutas,
bytes, hashes y comprobaciones de confianza siguen sus reglas originales. Fuera
de esa reproducción, la auditoría exige el CE02 real presente y sus bytes/pins
correctos, CE01 preservado y los otros diez slots ausentes. No ejecuta los `main`
de publicación históricos ni cambia sus fuentes. La adaptación se declara en
[la preparación reproducible](../validation/D5-I199-preparation-review.json).

```sh
python3 docs/validation/D5-I199-audit.py
```

Resultado exigido: `PASS_STATIC_SOURCE_ONLY_EVIDENCE_MISSING`, CE02 preparado y
no aceptado, sin registry creado ni dependencia CE01 descargada, cero evidencia
externa aceptada, cero recursos cerrados y D5 abierto. [El sello](../validation/D5-I199-integrity.json)
preserva 484 archivos publicados y fija los otros cuatro artefactos de la unidad.
Harness runtime: N/A, preparación documental sin producto/componentes/cripto/
codec de registry/imagen/claim o protocolo.

Unidad única, superior a 400 líneas por pins, matrices y preservación; se declara
el exceso sin reducir evidencia. Commit/push publica para revisión estos cinco
archivos y limita la reversión a ellos:

- `docs/design/D5-I199-CE02-ANCHOR-PROVENANCE.md`
- `docs/validation/D5-I193-CE02-ANCHOR-PROVENANCE-CANDIDATE.json`
- `docs/validation/D5-I199-preparation-review.json`
- `docs/validation/D5-I199-audit.py`
- `docs/validation/D5-I199-integrity.json`

El siguiente alcance posible es revisar este dossier CE02 y su declaración de
faltantes. La aceptación real requiere evidencia externa auténtica, dependencia
CE01 competente y decisiones R01/R02/R08 genuinas; no se genera por preparar o
publicar documentación ni autoriza acciones para suplir las carencias.
