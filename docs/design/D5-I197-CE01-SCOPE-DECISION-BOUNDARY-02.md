# I197 — CE01 candidato 02 separa el handoff de los requisitos finales

La revisión de CE01 prepara la reparación documental de **F195-01**: reemplaza
X09 por una obligación de handoff para CE11 y otra de evidencia final real para
CE12. Queda pendiente revisar esta versión exacta; no se declara aceptación ni
cierre competente del hallazgo. Se mantiene la no admisión de PGO181 candidato
02/PJC115-R2, D5 abierto e IR03 `NOT_READY`.

Fecha del cliente: 2026-11-16, Europe/Madrid. Base publicada I196:
`0885ea863a46c66b12b473ba63ee0f8389effdd4`.

## Versión y reparación trazables

[El candidato 02](../validation/D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json)
es un dossier documental nuevo. Su `revision_binding` fija el candidato I195 y
el hallazgo `/findings/0` del dictamen I196. El `plan_binding` conservado identifica
la entrega histórica de I193; `current_candidate_path` identifica esta revisión.
Ningún binding activo ni capture_inputs cambia. I195/I196 y el plan quedan
intactos, incluido el hallazgo histórico abierto y su diagnóstico de X09.

La tabla siguiente sustituye para **este candidato** la tabla I195. No reescribe
la evidencia que justificó I196 ni produce los dossiers futuros CE11 o CE12.

| Requisito | Consumidor | Obligación y frontera |
| --- | --- | --- |
| X01 | CE02 | Autoridad externa auténtica de anchors/identidad, digest/epoch/propósitos/claves anteriores a C |
| X02 | CE03, CE08 | Humanos canónicos, alias, autores completos y nombramientos/competencia reales |
| X03 | CE04, CE08 | Seis fuentes reales y procedencia exacta de build, imagen, runtime y correspondencia inmutable |
| X04 | CE05, CE06 | Principal caller, solicitante responsable, constructor y origen de endpoints/dominio |
| X05 | CE06, CE08–CE10 | Reloj confiable, frescura, epochs y revocación conocidos |
| X06 | CE06, CE12 | Ledger global atómico de un uso, resistente a reinicio/rollback/crash |
| X07 | CE07, CE08 | Recursos y compatibilidad completos del sucesor, heap/CPU/IO/Reader/900 s |
| X08 | CE01, CE11 | R06/R08 realmente designados, competentes y separados; decisiones auténticas |
| **X09-PRELAUNCH-HANDOFF** | **CE11** | Handoff documental de la ruta final pendiente y sus responsables. No exige completar esa ruta ni obtener recibo/claim/spawn para aceptar hechos de custodia CE11. Todos los hechos/revisiones reales de CE01–CE10 siguen exigidos |
| **X09-FINAL-PREREQUISITES** | **CE12** | E06/payload/Q/root confiable/firmas y admisión completa reales antes del claim autorizado por separado; todos los prerrequisitos de recibo I193 siguen vigentes |
| X10 | CE12 | Recibo auténtico de claim/construcción correlacionados, sólo tras la ruta final real y autorización separada |

Las nueve filas ajenas a X09 son idénticas al candidato anterior. Las once filas
siguen sin aceptar, con proveedor, localizador, nombramiento, hash y tamaño reales
ausentes, sin permiso de contacto. Hay diez requisitos externos de evidencia real
y uno de handoff documental aún no suministrado. La fila de handoff usa
`required_documentary_handoff`, sin campo `required_actual_evidence`; su tipo y
consumidor impiden confundir la enumeración de pendientes con su satisfacción.

## Orden de las obligaciones por paso

`step_obligation_boundary.CE11` exige los pasos reales CE01–CE10 y el handoff de
los pendientes de la ruta final. Declara falsos tanto el requisito de completar
esa ruta como el de disponer de recibo/claim/spawn CE12. No libera un gate de
ejecución y no exime a los siete conjuntos de evidencia de custodia previa.
No hay requisito final X09 asignado a CE11.

`step_obligation_boundary.CE12` y la fila final conservan las cinco condiciones
externas de `/closure_boundaries/external_prerequisites_for_receipt` de I193,
con una fase explícita para cada una:

| Fase | Condición auténtica exigida |
| --- | --- |
| Antes del claim | Autorización explícita y separada de ejecución |
| Antes del claim | E06 final y payload reales |
| Antes del claim | Q real y root final confiable |
| Antes del claim | Admisión completa del root real |
| Después del claim/construcción, antes del recibo | Claim atómico de un uso y construcción protegida reales |

Las cuatro primeras son prerrequisitos del claim. La quinta exige el evento real
para emitir el recibo; el claim no es prerrequisito de sí mismo. El handoff no
realiza ni satisface ninguna condición. Actualmente no hay autorización, evidencia
final, claim, construcción o recibo generado por esta revisión.

## Qué conserva la revisión

El candidato conserva los tres requisitos CE01, dos checks y K01/K10/K12/K15/K16,
el inventario de 14 documentos, ocho roles sin asignar, sus ocho exclusiones S01,
cuatro separaciones adicionales de custodia y ocho decisiones sin adoptar.
La matriz mantiene las cuatro acciones documentales y 14 clases denegadas;
sólo actualiza la base de autorización documental a la petición I197.

No cambian perfil/protocolo/output/transporte, candidatos numéricos, cotas,
presupuestos, cuotas, reservas, schemas activos, miembros Reader ni canales.
K15 exige contabilizar todo el trabajo de lookup/frescura/identidad/verificación,
copias/registro/recibo y nativo/IO requerido durante los intentos; llamarlo offline
no lo vuelve gratuito ni lo desplaza fuera de t0. No se acredita capacidad real.

Las seis fuentes sucesoras, imagen/runtime auténticos y ocho cuerpos I191 siguen
faltando. No se crea ningún dossier de los otros once pasos del plan. I122 sigue
`IMPLEMENTED_NOT_ADMITTED`: CP03 verdadero sólo en su alcance heredado sellado,
CP07 falso, atomicidad correlacionada no verificada y componentes `NOT_RUN`.
Las nueve condiciones completas de CP07 permanecen; cero obligaciones E01–E05
cerradas, E06 separado y sin ejecutar, F179-01/S01 sin aceptación.

El mismo asistente/chat prepara la revisión; no hay independencia personal u
organizativa acreditada ni nombramiento competente R06/R08. El estado de la
reparación es `REPAIR_PREPARED_PENDING_DOCUMENTARY_REVIEW`, con confirmación y
cierre aceptado falsos. Ni la publicación ni los checks sustituyen esa revisión
o la adopción auténtica. No se inventan identidades, firmas, hashes o PASS real.

## Verificación documental y publicación

```sh
python3 docs/validation/D5-I197-audit.py
```

Resultado exigido: `PASS_STATIC_SOURCE_ONLY_REPAIR_PREPARED_PENDING_REVIEW`.
[La preparación reproducible](../validation/D5-I197-preparation-review.json)
contrasta 782 pins con Git y bytes actuales, reproduce el dictamen I196 sin su
`main` de publicación y compara esta revisión con I195 mediante una lista cerrada
de cambios permitidos. Los históricos se reconstruyen con su estado original;
este candidato se comprueba en su ruta real, sin nuevas proyecciones de presencia.

La validación comprueba obligaciones por consumidor, tipo y fase. Seis
contraejemplos sólo en memoria deben rechazarse: asignar evidencia final a CE11;
exigir evidencia final real en el handoff; quitar un prerrequisito final; quitar
un paso CE01–CE10; autorizar CE12 desde el handoff; o exigir el claim antes de sí
mismo. Son controles documentales, sin ejecutar producto ni componentes.

El sello conserva 474 archivos publicados y fija los otros cuatro artefactos de
esta unidad. Harness runtime: N/A, candidato documental sin ejecución de producto,
componentes, cripto, imagen, claim o protocolo, y sin contacto con terceros.

Unidad única superior a 400 líneas por pins, matrices y preservación; se declara
el exceso sin recortar evidencia. Commit/push publica únicamente estos cinco
archivos; la reversión queda limitada a ellos:

- `docs/design/D5-I197-CE01-SCOPE-DECISION-BOUNDARY-02.md`
- `docs/validation/D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json`
- `docs/validation/D5-I197-preparation-review.json`
- `docs/validation/D5-I197-audit.py`
- `docs/validation/D5-I197-integrity.json`

El siguiente alcance es revisar el candidato 02 exacto y su reparación de F195-01.
Los nombramientos/decisiones competentes R06/R08 y la evidencia externa auténtica
siguen pendientes por separado, sin habilitar producto, componentes, cuotas o D5.
