# I200 — CE02 requiere separar anchors previos de aprobaciones posteriores

La revisión documental de CE02 identifica **F199-01**, pendiente de reparación:
AP08 mezcla la selección externa de claves/política de anchors con aprobaciones
reales sobre el core del bundle que corresponden a CE10. CE02 queda sin confirmar
documentalmente y sin aceptar. PGO181 candidato 02/PJC115-R2 conservan la no
admisión; D5 sigue abierto e IR03 `NOT_READY`.

Fecha del cliente: 2026-11-16, Europe/Madrid. Base publicada I199:
`186c3f90722ad9c22220938da877fe9ea121be78`.

## F199-01 — política previa y prueba posterior sin frontera explícita

| Fuente exacta | Observación |
| --- | --- |
| [Dossier I199](../validation/D5-I193-CE02-ANCHOR-PROVENANCE-CANDIDATE.json), `/evidence_requirements/7` | AP08 exige “Genuine R01/R02/R08 approvals over the same signed core” entre las necesidades de evidencia de CE02, sin asignar esa prueba a una fase posterior |
| Mismo dossier, `/actual_anchor_state/actual_signature_or_custody_approvals` | Slot ausente de firmas/aprobaciones, sin distinguir aceptación previa de anchors de aprobación futura del bundle |
| [Documento I199](D5-I199-CE02-ANCHOR-PROVENANCE.md), AP08 | Repite el requisito de aprobaciones sobre core común dentro de CE02 |
| [Plan I193](../validation/D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json), `/steps/9` | CE10 exige la evidencia real de tres aprobaciones sobre core común y depende explícitamente de CE02, CE08 y CE09 |
| [Contrato I191](../validation/D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json), K01/K11 y `/record_order` | Anchors independientes preexistentes suministran las claves de confianza; el bundle depende de ANCHOR, no al revés |

**Prioridad P2; bloquea la confirmación documental.** Incluir K11 en CE02 permite
fijar las reglas de propósito/dominio/selección de claves y política, pero no
convierte las aprobaciones reales posteriores en prueba previa de su propio
anchor. AP08 no distingue esos dos usos de K11. “No crypto here” conserva la
prohibición de ejecución; no resuelve cuándo debe existir esa evidencia.

La reconstrucción confirma que el grafo publicado I193 es acíclico. Sólo **si**
AP08 se interpreta como requisito de cierre CE02 de aprobaciones reales CE10,
se añade CE02→CE10 a la dependencia existente CE10→CE02 y aparece el ciclo
condicional CE02→CE10→CE02. No hay un ciclo real observado ni ejecución, firma,
registry, aceptación o prueba de fallo del runtime.

La reparación propuesta, sin aplicarla a I199 en esta revisión, es:

| Obligación propuesta | Consumidor | Frontera |
| --- | --- | --- |
| `AP08-ANCHOR-POLICY` | CE02 | Procedencia/provisión y aceptación previa auténticas, autoridad de identidad, digest/epochs esperados externamente y bindings propósito/actor/clave. Fija política exacta de core/dominios/profile/pack/contrato, sin exigir firmas de un futuro bundle CE10 |
| `AP08-BUNDLE-APPROVAL` | CE10 | Evidencia real posterior de las tres aprobaciones sobre el mismo core exacto, tras antecedentes y C auténticos, usando las claves/política independientes de CE02. El bundle y sus firmas nunca autentican retrospectivamente sus propios anchors |

Debe distinguirse también la disponibilidad de aceptación previa de anchors de
las aprobaciones futuras, actualizar la tabla del candidato y comprobar
obligaciones por fase. No basta con que cada K-rule tenga alguna fila no vacía.
**No se elimina la aceptación previa genuina** exigida para CE02. No se crea un
dossier CE10, firma, clave, registro o autorización con esta propuesta.

## Cobertura documental y faltantes reconocidos

[La reconstrucción](../validation/D5-I200-I199-source-reconstruction.json) contrasta
797 pins con Git y disco, reproduce la preparación I199 sin su `main` de
publicación y reconstruye la incidencia de las cinco K-rules sobre AP01–AP09.
[El dictamen estructurado](../validation/D5-I200-I199-documentary-review.json)
recorre los tres requisitos CE02, dos checks, la frontera de autorización y
K01/K03/K11/K13/K16. E02 y K11 quedan parciales por F199-01.

El dossier declara correctamente nueve necesidades de evidencia ausente, tres
slots R01/R02/R08 sin asignar y diez condiciones de rechazo no evaluadas.
Los proveedores, autoridad externa, digest/epochs esperados, claves públicas,
registry body, firmas, cuerpos de prueba, reloj/revocación y aceptaciones siguen
ausentes. No se genera ni solicita clave privada. Esa ausencia se reconoce como
prerrequisito externo; no se cuenta como un nuevo defecto documental adicional.

Los cuatro fragmentos de schema son exactos: nueve campos obligatorios de
registry, cinco de anchor_key, tres propósitos y entre tres y 64 entradas; también
referencias de evidencia y validez. Los 65.536 bytes limitan el futuro cuerpo
registry, no este wrapper con pins ni los cuerpos subyacentes de evidencia.
No se ejecuta codec, validator de componentes ni cripto sobre un cuerpo real.
Los hashes documentales no se reutilizan como expectativa externa de confianza.

El contrato conserva lifetime máximo 3.600 s, error confiable máximo 5 s, reglas
exactas de tiempo/currentness y rechazo de TOFU/stale-cache/lookup oculto. No se
acredita frescura real ni descubrimiento instantáneo de toda revocación.
Completitud, unicidad y aliases siguen requiriendo evidencia auténtica; los caps
del índice no demuestran recursos, costes de verificación o los 900 segundos.

La dependencia competente CE01 sigue insatisfecha, pese a la confirmación
documental de su candidato 02 y reparación F195-01 en I198. Preparar o revisar
CE02 no descarga esa dependencia. Los scopes, ocho exclusiones S01, cuatro
separaciones extra de custodia, nueve condiciones CP07 y candidatos numéricos
permanecen intactos. No cambian permisos, cuotas, reservas, schemas activos,
Reader, canales, capture_inputs, bindings, autoridad o destino.

I122 sigue `IMPLEMENTED_NOT_ADMITTED`, CP03 verdadero sólo en su alcance heredado,
CP07 falso, atomicidad correlacionada no verificada y componentes `NOT_RUN`.
Cero obligaciones E01–E05 cerradas; E06 separado y no ejecutado; F179-01/S01 sin
aceptación. Las seis fuentes sucesoras y ocho cuerpos I191 siguen faltando; los
otros diez dossiers planificados siguen ausentes. No hay admisión ni cierre D5.

La proyección histórica I199 de presencia CE02 se contrasta con Git: ausente en
su base I198 y presente en la base I199 de esta revisión. Sólo afecta esa ruta,
preserva otra ruta existente y otra ausente, y restaura `Path.exists` al salir
normalmente o ante una excepción documental controlada. El guard histórico CE01
sigue original. Los bytes actuales se verifican normalmente y ningún histórico
se reescribe. Son comprobaciones documentales, sin simulación de producto.

El mismo asistente/chat preparó y revisó I199. La reconstrucción metodológica
separada no establece independencia personal u organizativa, competencia R01/R02
ni aceptación separada R08. Esas decisiones genuinas siguen pendientes. El
candidato original queda intacto, incluida su declaración histórica de readiness;
este dictamen nuevo exige una revisión documental concreta.

## Verificación y publicación

```sh
python3 docs/validation/D5-I200-audit.py
```

Resultado exigido: `PASS_STATIC_SOURCE_ONLY_WITH_OPEN_FINDING_F199_01`. Significa
que el dictamen es reproducible con F199-01 abierto, no que CE02 esté confirmado,
aceptado o provisto de anchors. [El sello](../validation/D5-I200-integrity.json)
preserva 489 archivos publicados y fija los cuatro artefactos nuevos restantes.
Harness runtime: N/A, revisión JSON/Git/schema documental/dependencias; no producto,
componentes, cripto, codec registry, imagen, claim o protocolo. Sin contacto externo.

Unidad única superior a 400 líneas por pins y trazabilidad; se declara el exceso
sin reducir evidencia. Commit/push publica la revisión sin reparar silenciosamente
I199 ni emitir aceptación. La reversión se limita a estos cinco archivos:

- `docs/design/D5-I200-I199-CE02-REVIEW.md`
- `docs/validation/D5-I200-I199-source-reconstruction.json`
- `docs/validation/D5-I200-I199-documentary-review.json`
- `docs/validation/D5-I200-audit.py`
- `docs/validation/D5-I200-integrity.json`

El siguiente alcance es preparar una revisión CE02 que separe la política/provisión
previa de anchors de las aprobaciones diferidas CE10 y revisar esa versión exacta.
La evidencia externa auténtica y la aceptación competente de CE01/CE02 continúan
pendientes por separado, sin permitir ejecución, cuotas o cierre D5.
