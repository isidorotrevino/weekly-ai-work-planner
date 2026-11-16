# I196 — CE01 requiere separar el handoff de CE11 de los requisitos finales

La revisión documental de CE01 identifica **F195-01**, pendiente de reparación:
X09 agrupa un requisito de evidencia final E06/payload/Q/root/admisión completa
para CE11 y CE12, sin separar lo que corresponde a cada frontera. CE01 permanece
sin confirmar documentalmente y sin aceptar. Se mantiene la no admisión de
PGO181 candidato 02/PJC115-R2, con D5 abierto e IR03 `NOT_READY`.

Fecha del cliente: 2026-11-16, Europe/Madrid. Base publicada I195:
`05876a14c9e3e614df9581a991b9c76140a96161`.

## F195-01 — obligación final y handoff en una misma fila

| Fuente exacta | Observación |
| --- | --- |
| [Dossier I195](../validation/D5-I193-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE.json), `/external_evidence_requirements/8` | X09 apunta a `CE11, CE12` y exige conjuntamente evidencia final real E06/payload/Q/root/firmas y admisión completa |
| [Documento I195](D5-I195-CE01-SCOPE-DECISION-BOUNDARY.md), fila X09 | Repite la asociación de evidencia final con ambos pasos |
| [Plan I193](../validation/D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json), `/steps/10/required_evidence/2` | CE11 pide un handoff explícito al trabajo final E06/payload/Q/root/admisión, manteniendo visibles sus pendientes |
| Mismo plan, `/steps/10/authorization_boundary` y `/closure_boundaries` | CE11 es frontera de evidencia previa, sin liberar ejecución; CE12 continúa diferido y requiere prerrequisitos reales posteriores |

**Prioridad P2; bloquea la confirmación documental.** El lector no puede resolver
con la fila X09 si el trabajo final debe estar completado para aceptar los hechos
de custodia de CE11 o si debe quedar como handoff pendiente. La palabra “future”
y la ausencia de permiso de ejecución conservan la no admisión, pero no separan
las obligaciones de los dos pasos.

No se afirma un ciclo real, una ejecución observada ni un cambio en el grafo
publicado: X10 sigue limitado a CE12 y CE11 no depende de su recibo. El hallazgo
es una ambigüedad de asignación documental, no una prueba de fallo de runtime.

La reparación propuesta, sin aplicarla a I195 en esta revisión, es:

| Fila propuesta | Consumidor | Evidencia exigible en esa frontera |
| --- | --- | --- |
| `X09-PRELAUNCH-HANDOFF` | CE11 | Handoff documental de la ruta final pendiente y sus responsables. No añade la realización de E06/payload/Q/root/admisión como requisito de cierre de custodia CE11. Mantiene todos los hechos y revisiones reales exigidos por CE01–CE10 |
| `X09-FINAL-PREREQUISITES` | CE12 | Evidencia final auténtica E06/payload/Q/root confiable/firmas y admisión completa, antes de cualquier claim/construcción/recibo realmente autorizado por separado |

Una revisión del candidato debe actualizar también la tabla I195 y verificar las
obligaciones por paso. Comprobar sólo que la unión de `downstream_steps` cubra
CE01–CE12 permite que esta ambigüedad pase la auditoría estructural de I195.
CE12 conserva todos los prerrequisitos externos del plan; ninguna fila propuesta
nombra personas ni autoriza contacto, ejecución, emisión o aceptación.

## Cobertura restante y límites del dictamen

[La reconstrucción](../validation/D5-I196-I195-source-reconstruction.json) contrasta
777 pins con blobs Git y bytes actuales. [El dictamen completo](../validation/D5-I196-I195-documentary-review.json)
recorre los tres requisitos de evidencia CE01, dos checks, su frontera de
autorización y K01/K10/K12/K15/K16. E03 y K12 quedan parciales por F195-01.

El inventario de 14 documentos fija I191/I192/perfil02/protocolo/output/transporte
y los gates heredados. Los ocho roles conservan scopes, ocho exclusiones S01 y
cuatro separaciones adicionales de custodia. Personas, nombramientos, competencia,
claves y vigencias siguen ausentes. Hay cuatro acciones documentales permitidas
y 14 clases denegadas; ocho decisiones propuestas siguen sin adoptar.

Las diez necesidades X01–X10 no identifican proveedores reales, localizadores,
nombramientos, hashes ni tamaños de evidencia auténtica. Las seis fuentes
sucesoras y las ocho familias de registros I191 siguen ausentes; los otros once
dossiers permanecen sin crear. Estos pendientes se declaran honestamente y no se
cuentan como nuevos defectos documentales ni como evidencia aceptada.

K15 sigue vigente íntegramente: lookup, frescura, resolución de identidad,
verificación, copias/registry/recibo y trabajo nativo/IO necesario durante los
intentos debe estar incluido en la composición global de recursos y fases.
Llamarlo offline no lo hace gratuito ni lo mueve fuera de t0. No se añaden
miembros Reader, canales, helpers ni cuerpos activos, ni se demuestra ajuste.

La auditoría documental I195 se reproduce sin ejecutar su `main` de publicación.
Su proyección histórica de presencia se revisa con Git: CE01 estaba ausente en
la base I194 y presente en I195. Se comprueba que afecta sólo a esa ruta,
conserva otras rutas presentes/ausentes y restaura `Path.exists` tanto al salir
normalmente como ante una excepción documental controlada. Los bytes actuales
siempre se verifican; no se cambia ningún auditor ni registro histórico.

El mismo asistente/chat preparó y revisó CE01. La reconstrucción es una metodología
separada, sin independencia personal u organizativa acreditada. No es una
revisión competente R06 ni aceptación R08; ambas permanecen pendientes. La
preparación histórica de I195 queda intacta y su declaración de readiness no
sustituye este dictamen de revisión.

I122 sigue `IMPLEMENTED_NOT_ADMITTED`, CP03 verdadero sólo en su alcance heredado,
CP07 falso, atomicidad correlacionada no verificada y componentes `NOT_RUN`.
Permanecen las nueve condiciones completas de CP07 y todos los candidatos
numéricos/cotas heredados. E01–E05 siguen abiertos, cero obligaciones cerradas;
E06 continúa separado y sin ejecutar. No se transfiere prueba al sucesor ni se
resuelve F179-01/S01. No hay rebind, cambio de cuotas/reservas, autoridad o destino.

## Verificación y publicación

```sh
python3 docs/validation/D5-I196-audit.py
```

Resultado exigido: `PASS_STATIC_SOURCE_ONLY_WITH_OPEN_FINDING_F195_01`.
El resultado significa que la revisión y preservación son reproducibles, con
F195-01 abierto; no significa que CE01 esté confirmado o aceptado. El sello
preserva 469 archivos publicados y fija los cuatro artefactos nuevos restantes.
Harness runtime: N/A, revisión documental sin ejecución de producto, componentes,
cripto, imagen, claim o protocolo. No se contacta con proveedores/revisores.

Una única unidad de revisión, superior a 400 líneas por pins y trazabilidad;
se declara el exceso sin recortar evidencia. Commit/push publica este dictamen,
sin reparar silenciosamente I195 ni crear aceptación o autoridad. La reversión
queda limitada a estos cinco archivos:

- `docs/design/D5-I196-I195-CE01-REVIEW.md`
- `docs/validation/D5-I196-I195-source-reconstruction.json`
- `docs/validation/D5-I196-I195-documentary-review.json`
- `docs/validation/D5-I196-audit.py`
- `docs/validation/D5-I196-integrity.json`

El siguiente alcance concreto es preparar una revisión de CE01 que separe X09,
actualice su tabla y compruebe el significado de cada obligación por paso.
Después deberá revisarse esa versión exacta. La adopción competente R06/R08 y
la evidencia externa auténtica siguen siendo prerrequisitos separados pendientes.
