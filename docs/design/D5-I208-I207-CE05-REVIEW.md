# I208 — CE05 confirmado documentalmente, sin capacidad o caller reales

La revisión confirma **CE05 de I207 como baseline documental de procedencia
faltante**, sin nuevos bloqueos documentales. Identidad, capacidad y permiso
bootstrap permanecen separados; I189 conserva su transporte y las obligaciones
posteriores tienen consumidores propios. No se selecciona caller/backend,
emite capacidad, acepta registro ni crea constructor, claim o worker. PGO181
candidato 02/PJC115-R2 mantienen la no admisión, D5 abierto e IR03 `NOT_READY`.

Fecha del cliente: 2026-11-17, Europe/Madrid. Base publicada I207:
`528f4ae4bae9ddcf5fe4ed55464962817610da68`. La fecha documental no acredita
currentness o reloj de plataforma. I207 permanece íntegro con su disposición
histórica de preparación; este dictamen aporta la revisión posterior.

## Dictamen de las fronteras de CE05

| Fuente de [CE05 candidato](../validation/D5-I193-CE05-CALLER-CONSTRUCTOR-DOMAIN-CANDIDATE.json) | Resultado documental |
| --- | --- |
| `/identity_and_capability_policy` | Humano solicitante y principal software distintos; appointment, fd/PID/UID/env/module/cwd/key/hash no son capacidad por sí solos |
| `/inherited_transport_policy` | Requisitos I189 completos, dos pipes/seis operandos y cero extensiones implícitas, sin valores ni evidencia de endpoints reales |
| `/cross_record_and_mapping_policy` | Relaciones de C y mapping conservadas como obligaciones posteriores; no confianza anticipada desde un bundle futuro |
| `/step_obligation_boundary` | Seis requisitos baseline CE05 y uno en cada CE06/07/08/09/10/12, sin dependencias inversas ni aceptación de sus pruebas |
| `/actual_caller_state` | Principal, humano, backend, dominio, constructor, endpoints, C/mapping/claim/records y decisiones reales ausentes; flags de selección/ejecución falsos |
| `/schema_obligations` | Caller cerrado de 13 campos/cap candidato 8.192, no wrapper positivo ni permiso real; cuerpo final y checks en CE08 |

[La reconstrucción](../validation/D5-I208-I207-source-reconstruction.json) contrasta
837 pins con Git y disco y reproduce I207 sin su `main` de publicación.
[El dictamen estructurado](../validation/D5-I208-I207-documentary-review.json)
recorre tres requisitos, dos checks, frontera de autorización y
K02/K06/K07/K08/K09/K15. No registra nuevos hallazgos; la confirmación queda
limitada a los bytes exactos de este dossier, sin aceptar los hechos externos.

## Identidad, capacidad y autorización

El principal software no reemplaza al humano responsable ni a la resolución
canónica de roles/preparadores/autor/solicitante/custodios mediante autoridad
aceptada. Nombres, claves, strings o un rol designado no prueban identidad humana,
separación efectiva o acceso funcional a un dominio. Todos esos valores y las
pruebas de enrollment continúan ausentes.

El literal `BOOTSTRAP_CUSTODY_ONLY_FULL_ROOT_AND_SEPARATE_REQUEST_REQUIRED` es
política del schema. I207 no lo entrega como capacidad o permiso efectivo. Un
frame C/I, READY, firma, appointment o aserción de descriptor/peer no autoriza
capture, claim, spawn o import funcional. El mecanismo concreto de constructor/
loader/privilegios/aislamiento debe existir y estar genuinamente acreditado;
el record y sus hashes no son ese mecanismo.

Se conserva la autenticación previa real de actor/imagen/caller/dominio/constructor
como antecedente. Las firmas del bundle posterior fijan sus bindings, pero no
pueden ser la única fuente anticipada de esos hechos. Ninguna declaración de
baseline o confirmación documental descarga la dependencia competente de CE04,
aunque su alcance se haya revisado en I206. CE01–CE05 siguen sin adopción real.

## Transporte e identidad del worker

Las reglas de ownership, argv, trust boundary, permisos/one-use y gramática se
comparan íntegramente con I189. Se conservan dos pipes explícitos DOWN/UP y los
seis operandos observados, sin pipe/proceso/input adicional. El origen, modos,
tipos y exclusividad de descriptores, raw/stdout/sidecar, OWNER/lease y sesión/grupo
requieren evidencia real. No hay números fd/PID/UID/dominio ni probes suministrados;
los nombres o fstat por sí solos no acreditan custodia.

No se presupone gratuito el cierre/ownership/coste de descriptores internos de
runtime/spawn ni se permite exponerlos a código funcional. Un backend que necesite
un canal/fd/argv/helper/file/env/attestation extra exige rechazo de la ruta sin
cambios o contratos/grafo/bounds/costes versionados revisados. No se amplía scope
ni se cambia cuota en esta revisión.

El worker correlacionado hereda origen intrínseco de un constructor/dominio
aceptados; no recibe un mapping, recibo o confianza nuevos por wire/argv/canal.
Conserva sus checks independientes C/Q/root antes de READY y `W_RELEASED` como
frontera funcional, con las condiciones actuales/EOF/rechecks I189. La revisión
de esa política no ejecuta máquinas de protocolo, crea endpoints ni prueba origen.

## Consumidores y orden de evidencia

| Requisito | Consumidor | Frontera preservada |
| --- | --- | --- |
| CC01–CC06 | CE05 | Baseline de procedencia de humano/principal, relaciones previas y mecanismo/custodia concretos; sin C, mapping o freeze futuros exigidos ahora |
| CC07 | CE06 | Plataforma completa, reloj/currentness y dominio global de un uso |
| CC08 | CE07 | Composición completa de recursos/costes por intento y alcance efectivo |
| CC09 | CE08 | Freeze actor→image→caller→platform con autores y antecedentes reales antes de C |
| CC10 | CE09 | C exacto: requester, hashes, constantes/tiempo/clock y relaciones entre registros |
| CC11 | CE10 | Un mapping actual autenticado por epoch/digest C hacia un bundle/caller/image/domain/ledger |
| CC12 | CE12 | Claim/construcción reales sólo con root/Q/admisión completa y autorización explícita separada |

Un DFS independiente I193 confirma CE01–CE04 como únicos antecedentes de CE05;
ninguna fase posterior se añade como dependencia inversa. CE08 conserva CE02–CE07,
CE09 sigue a CE08, CE10 conserva CE02/CE08/CE09 y CE12 depende de CE11, sin recibo
CE12 como prerrequisito CE11. Otro DFS I191 conserva actor/image antes de caller,
caller antes de plataforma/C y mapping externo/root antes de claim, que precede
al recibo. Son checks documentales de orden, no ejecución o garantía del backend.

La igualdad futura `C.runtime_requester_id == caller.accountable_requester_actor_id`
y `platform.domain_id == caller.protection_domain_id`, junto con K08 completo,
no produce C ni un hash aceptado ahora. K09 conserva unicidad/currentness del
mapping y rechazo de conflicto/rollback/estado obsoleto. Nada se consulta o emite
para completarlo. Los cinco requisitos externos de recibo I193 permanecen: las
condiciones previas al claim no se confunden con el evento real claim/construcción
que deberá constar para el recibo. No hay CLAIMED o retry inferidos desde un plan.

Los costes necesarios de lookup/frescura/identidad/verificación/copias/clock/
registry/receipt y nativo/IO siguen dentro de t0/phases/global E01–E05. Enrollment
previo o llamar al trabajo offline no lo hace gratuito. No se acredita heap,
CPU/IO, servicio o los 900 segundos. Refresh de fuentes/autores/bindings/epoch/
claves/scope invalida dependientes conforme al plan, sin rebind activo.

## Evidencia ausente y límites de la confirmación

Las doce filas siguen sin proveedor, localizador, nombramiento, cuerpo/hash/tamaño,
aceptación o permiso de contacto reales. El estado conserva 24 valores ausentes
y siete flags falsos; no hay caller, domain, constructor, endpoints, C, mapping,
aprobaciones, claim/worker o caller record suministrados. Los 15 documentos y
sus hashes son fuentes documentales, no enrollment o capacidad auténticos.

Los cuatro fragmentos de schema son exactos. Caller_identity conserva 13 campos
cerrados, sin nuevos C/Q/bundle/receipt/root hashes, y cap candidato de 8.192 bytes.
El cap no se aplica al wrapper ni demuestra ajuste del cuerpo o su evidencia
subyacente; codec/hash/schema/cripto final quedan sin ejecutar y en CE08.

R01/R02/R06/R08 siguen sin persona, identidad canónica, nombramiento, competencia,
clave/vigencia o aceptación. El mismo asistente/chat preparó y revisa I207: la
reconstrucción metodológica separada no acredita independencia personal u
organizativa, revisión competente o aceptación R08. Cambiar el candidato o sus
fuentes exige revisar dependencias, scope y evidencia antes de reutilizar el dictamen.

Permanecen ocho exclusiones S01, cuatro separaciones extra, nueve condiciones
CP07, cuatro acciones documentales/14 clases denegadas y candidatos numéricos.
I122 sigue `IMPLEMENTED_NOT_ADMITTED`, CP03 verdadero sólo en su alcance heredado,
CP07 falso, atomicidad correlacionada no verificada y componentes `NOT_RUN`.
E01–E05 abiertos, cero obligaciones cerradas, E06 separado y no ejecutado,
F179-01/S01 sin aceptación. Fuentes sucesoras, ocho cuerpos I191 y otros siete
dossiers siguen ausentes. No cambian cuota, reserva, presupuesto, schema activo,
Reader, capture_inputs, binding, autoridad/root o destino.

## Verificación y publicación

Se contrasta con Git la presencia histórica de CE05: ausente en la base I206 y
presente en la base I207 de esta revisión. El guard afecta sólo a esa ruta durante
replay, conserva CE01–CE04 presentes/CE06 ausente y restaura `Path.exists` al salir
normalmente o ante una excepción documental controlada. Los guards originales
siguen anidados sin editar fuentes; los hashes y estado actuales se verifican
normalmente. No se añade una proyección nueva para I208.

```sh
python3 docs/validation/D5-I208-audit.py
```

Resultado exigido: `PASS_STATIC_SOURCE_ONLY`, CE05 confirmado documentalmente,
cero bloqueos nuevos, sin aceptación, capacidad o registro creado/finalizado.
Se reproducen diez rechazos de contraejemplos I207 como checks documentales,
no tests de componentes. [El sello](../validation/D5-I208-integrity.json) preserva
529 archivos publicados y fija los otros cuatro artefactos nuevos de la unidad.
Harness runtime: N/A, revisión JSON/Git/política de capacidad/transporte/schema/
grafos, sin seleccionar/enrolar backend o ejecutar proceso/probe/producto/
componentes/cripto/codec/claim/protocolo. No se contacta con proveedores.

Unidad única superior a 400 líneas por pins, cobertura y preservación; se declara
el exceso sin recortar evidencia. Commit/push publica únicamente estos cinco
archivos y limita la reversión a ellos:

- `docs/design/D5-I208-I207-CE05-REVIEW.md`
- `docs/validation/D5-I208-I207-source-reconstruction.json`
- `docs/validation/D5-I208-I207-documentary-review.json`
- `docs/validation/D5-I208-audit.py`
- `docs/validation/D5-I208-integrity.json`

Un posible siguiente encargo documental es preparar CE06, sin inventar garantías
de plataforma/reloj/ledger ni ejecutar probes/claim/replay/procesos. Toda evidencia
y aceptación competente real permanece pendiente, sin admitir producto o cerrar D5.
