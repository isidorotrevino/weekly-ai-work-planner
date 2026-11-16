# I179 — S01 preparado como candidato; roles y adopción siguen pendientes

Fecha: 2026-11-16, Europe/Madrid. Base:
`f1eb517283b3025ef555144e088c9803fd52e976`.

I179 prepara la matriz de roles, el scope y la semántica candidata de gates de
S01 del plan I177. **No inventa nombres, autoridad o aceptación:** ocho roles
siguen sin asignar y ninguna regla propuesta se adopta como contrato.
S01 aún no está aceptado; S02 no está listo para ejecución y la certificación
positiva S03 continúa bloqueada. E01–E05 abiertos, E06 NOT_RUN y cuatro bindings
pendientes; I122/PJC115-R2 sin admisión y D5 sin cerrar.

## Ruta de revisión

1. Leer la [matriz/scope/catálogo S01](../validation/D5-I179-S01-ROLES-SCOPE-GATES.json).
2. Revisar los ocho nombramientos faltantes y las separaciones de roles.
3. Contrastar los siete gates, las seis decisiones propuestas y F179-01 con
   las fuentes y el scope exacto de evidencia.
4. Consultar la [preparación](../validation/D5-I179-S01-preparation-review.json),
   el [auditor](../validation/D5-I179-audit.py) y el [sello](../validation/D5-I179-integrity.json).

I177/I178 conservan sus bytes y estados históricos. El asistente prepara el
expediente documental, sin reclamar independencia, custodia de runtime/plataforma
o potestad de autorizar acciones. La matriz nombra responsabilidades, no personas
reales; no se infiere autoridad de un autor Git, firma de commit o cuenta.

## Roles, autoridad y validez que deben completarse

| Rol | Responsabilidad de scope | Asignación actual |
| --- | --- | --- |
| R01 custodio runtime | Imagen/build, intérprete, stdlib/frozen/builtin/nativo, allocator y correspondencia fuente/binario | Pendiente |
| R02 custodio plataforma | Capacidad, procesos, servicio CPU/wall, reloj, IO/children, scheduler/carga y validez | Pendiente |
| R03 revisor de recursos | Evidencia completa E01–E05 e hipótesis, independiente del preparador | Pendiente |
| R04 custodio de componentes | Runs futuros autorizados, freeze de fuentes/runtime/manifest y custodia de raw | Pendiente |
| R05 revisor de componentes | Evidencia real y manifest final, distinto del productor R04 | Pendiente |
| R06 revisor de admisión/proveniencia/Reader | Semántica de gates, protocolo del índice, bindings, archivos y límites | Pendiente |
| R07 emisor de autoridad | Emisión genuina con scope, confianza, validez y permiso propio | Pendiente |
| R08 aceptación separada | Decisión final distinta de producción y revisiones primarias | Pendiente |

Cada fila deja null persona, documento de autoridad, confianza/firma, vigencia
y scope de competencia. R08 requiere separación de preparador/R03/R04/R06/R07;
R05 de R04; R03/R06 del preparador. No se presume que una persona u organización
cumpla esos roles. Un propietario autorizado debe aportar nombramientos reales
y su justificación antes de dar por satisfecha la matriz.

La atribución de un rol tampoco concede permiso de ejecución. Se separan seis
scopes, todos sin conceder: calificación de componentes, validación final,
emisión de autoridad, rebind real, producto/captura y cambios de fuente/schema/
protocolo/cuota. El alcance actual sólo cubre documentación y publicación Git.

## Scope exacto de esta preparación

Se fijan por SHA PFC126-CANDIDATE-03, las seis fuentes I122, los treinta sitios
integrados, el índice negativo, los metadatos candidatos y el grafo I175 de
495 rutas/491 bindings reales. Los aliases candidatos no se instalan; las
referencias archivadas conservan identidad de bytes y commit de respaldo.

El scope heredado de fuente conserva 321 raíces/12 grupos y las precondiciones
I115/I120/I123/I124, incluidos originales/errores esperados. Cambios inesperados
de control/imports u objetos hostiles no se cubren por extender un contador.
CP03 no se convierte en garantía de heap/CPU o servicio.

La validación futura de componentes se refiere a los diez IDs sintéticos
de R2CandidateTests fijados por AST y manifest. No son las 321 raíces originales
ni autorizan campañas funcionales. El runner y los tests están fijados por hash,
sin importarlos o ejecutar discovery.

El intérprete real, SHA, cierre nativo/allocator/kernel, dominio de reloj/servicio,
imagen/plataforma aceptada, raíz de staging, propietario, freeze y entorno
aprobado siguen desconocidos. I127 continúa como referencia histórica, sin
inspección local actual o atestación del destino. Se requiere proveniencia
transitiva antes/después y custodia stdout/stderr/exit; seis nombres o un
contador de módulos no la sustituyen.

## Catálogo de gates candidato

| Gate/campo | Qué comprueba la fuente | Disposición S01 candidata |
| --- | --- | --- |
| G00 status SOURCE_CAPACITY_VERIFIED | Igualdad literal del estado del certificado | Mantener IMPLEMENTED_NOT_ADMITTED: faltan evidencia y gates verdaderos aceptados |
| G01 CP03_global_resolved | Booleano exacto True | Conservar el True heredado bajo su scope original, sin emitir verificación nueva o ampliarlo a recursos |
| G02 CP07_exact_admission_resolved | Booleano exacto True | Mantener False: bindings/Reader documentales no son admisión completa |
| G03 correlated_atomicity_verified | Booleano exacto True | Mantener False: reparación escrita y diez fixtures no prueban por sí solos validación completa de treinta sitios |
| G04 component_validation | No hay lookup directo de este campo en require_admission | Conservar NOT_RUN como estado veraz; no reemplaza las comprobaciones reales de componentes |
| G05 componentes aceptados | Raw/resultado PASS, diez tests, condiciones y hashes reales con manifest/sello | Cuerpos ausentes: E06 y sus tres hashes siguen pendientes |
| G06 autoridad y scope exacto | Schema/fase/P01, sin autopin y capture_inputs/registry/fuentes/componentes exactos | Autoridad ausente; confianza/validez del emisor no la autentica por sí sola el parser |

Siete anclas AST fijan los consumidores y productor relevantes. Para authority
se toma la definición final del módulo, que sustituye las heredadas anteriores.
Se distingue lo que el código consume de lo que una persona competente debe
justificar como verdad de la afirmación. No se cambia ningún booleano, estado,
schema o comprobación del producto.

## F179-01: CP07 completo y orden de evidencia

Las fuentes históricas I119/I122 distinguen expresamente CP07 de bindings y
capacidad numérica de CP07 de admisión real. La primera parte puede estar
revisada documentalmente mientras faltan hashes y evidencia futura aceptada.
Por tanto, I175 y la cota Reader no justifican poner CP07=true.

El parser exige ese booleano, pero no define por sí solo una afirmación firmada
sobre cuándo puede emitirse el certificado predecesor. Si el significado de
CP07/atomicidad exige evidencia que sólo existiría después de ese mismo
certificado, el orden de bytes acíclico no resuelve la dependencia semántica.

F179-01 mantiene abierta esa adjudicación. La propuesta es no reducir CP07 a
un checklist estático ni pronosticar PASS para avanzar. R06/R03 y R08 deben
acotar y aceptar la frontera de la afirmación y su evidencia anterior, o exigir
una separación de evidencia/protocolo versionada y revisada en otro alcance.
I179 no adopta esa separación, modifica el código o declara que sea imposible
todo protocolo alternativo. Tampoco invalida el DAG negativo acotado de I175.

La atomicidad necesita un argumento revisado para los treinta sitios y la
evidencia real de componentes que corresponda al scope adoptado. Una eventual
base calificadora no es E06 final automáticamente; diez tests no demuestran
todos los interleavings ni la capacidad completa. El campo informativo
component_validation no permite anticipar validación final o saltar raw/result/
seal reales. Este límite se incorpora a las seis decisiones propuestas,
todas sin adoptar y sin firmante/validez.

## Readiness y entrega a revisores

La preparación documental está completa, pero quedan sin satisfacer:
nombramientos R06/R04 y demás roles competentes; autoridad/validez de sus
decisiones; scope exacto de runtime/plataforma; adopción semántica de gates y
resolución de F179-01; base anterior aceptada o ruta calificadora separada.
S01 no se marca aceptado y no autoriza S02 o S03.

El propietario autorizado debe aportar nombres y documentos de competencia,
independencia, autoridad, validez y scope. Los revisores deben adoptar o rechazar
las decisiones candidatas sin debilitar CP07. Sólo después cabe decidir sobre
evidencia previa o necesidad de calificación, todavía sin permiso de ejecución.
Si no hay base veraz para el certificado, se mantiene el bloqueo, sin cambiar
fuentes, protocolo o cuotas dentro de esta tarea.

El upper PRP173 266.536.487 y el del candidato negativo 266.402.939 conservan
sus premisas; un sucesor positivo requiere revisar bytes, bindings, listings,
metadatos y outputs finales. Ninguna definición de gate los transforma en
capacidad real o en una cota de 900 segundos.

## Preservación y verificación

E01–E05 abiertos, E06 NOT_RUN y cuatro bindings pendientes. Certificado activo
y candidato IMPLEMENTED_NOT_ADMITTED, CP07/correlación false; sin
SOURCE_CAPACITY_VERIFIED, autoridad/destino nuevos o gate actualizado.
D5/H07 de cierre abiertos e IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/
1 PARTIAL UI04.1; D1–D4 e I1–I20/A52 intactos; brechas globales y reales
pendientes. I86/I89/I92 INVALID_CAPTURE no se reanudan ni mezclan.

`python3 docs/validation/D5-I179-audit.py`: resultado esperado
PASS_STATIC_SOURCE_ONLY. Verifica 684 pins contra Git, ocho roles, siete gates,
seis decisiones, seis scopes sin permiso, treinta sitios, diez IDs y siete
anclas AST. Preserva 378 archivos publicados e inputs heredados. No ejecuta
el runner, parser, componentes o producto; no mide runtime/plataforma.

Unidad de cinco archivos: expediente S01, preparación, este documento,
auditor y sello. Rollback limitado a los cinco archivos enumerados en work_unit.
El diff supera 400 líneas por la matriz, decisiones y auditor autocontenido;
el exceso queda informado. Runtime harness N/A: preparación documental sin
cambio runtime. Auditoría antes del stage y tras commit, push autorizado y
comprobación de remoto/árbol limpio. Publicar no nombra, adopta o autoriza.

Sin ejecutar/importar/compilar producto/componentes, tests, benchmarks,
schedule, introspección o mediciones. Sin cambiar cuotas, reservas,
presupuestos, contratos, fuentes o inputs vigentes; sin inspeccionar ni limpiar
dev/run_data/D4. Sin proveedores, credenciales, consumo, activación, promoción,
despliegue o D6.
