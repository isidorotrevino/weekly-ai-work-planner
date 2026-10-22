# D5 I21 — auditoría de alcance y aceptación

Fecha: 2026-10-22. Base publicada: `d20f375`.
**Auditoría documental; D5 abierto. No declara cierre ni añade SQL.**
[Revisión y decisiones siguientes](D5-I21-ACCEPTANCE-REVIEW.md) ·
[Inventario y comprobaciones](../validation/D5-I21-audit.json).

English: scope and acceptance audit of D5 I1–I20. The recorded evidence supports a
bounded local synthetic lab baseline. It does not establish completion of the
broader D5 integration roadmap. Advanced local features are not automatically
closure requirements. No runtime re-execution, closure, promotion or deployment.

## Resultado y autoridad

D5-A50: el usuario elige auditar requisitos, decisiones y evidencias para distinguir
bloqueos de cierre de extensiones opcionales, sin declarar cierre ni añadir SQL.
No autoriza nuevas integraciones, fixtures, promoción, despliegue o D6.

La [arquitectura D1 aprobada](D1-architecture-baseline.md) define D5 como integraciones:
Gentle-AI/routing, documentos Drive hacia requisitos/épicas/tareas y sincronización
Plane. Sheets/Monday es proyección opcional. [D3 aprobado](D3-approved.md) asigna a
D5 conectores/parsers y proveedores/cuotas comerciales reales; [D2 aprobado](D2.9-approved.md)
conserva sus contratos pendientes de adaptador y la necesidad de muestras reales.
Estas obligaciones no se sustituyen por una importación tabular local.

A01–A49 aprobaron incrementos concretos y sus laboratorios sintéticos. Aprobar un
contrato, pasar pruebas o publicar su commit no equivale a aprobar cierre D5.
I20 conserva `D5_closed=false`, `real_data=false` y `operational_activation=false`.
No hay documento D5 aprobado/cerrado ni manifiesto D5-CLOSURE en las rutas de cierre
consultadas. D1–D4 siguen cerrados dentro de sus propios perímetros, especialmente
el [D4 sintético aprobado](D4-approved.md); sus exclusiones no reabren sus cierres.

**Conclusión:** existe evidencia técnica para proponer una línea base del
**laboratorio local sintético de fuentes y tareas BACKLOG**. Su aceptación formal
como hito acotado exige decidir ese perímetro; no completaría D5 global.
Para D5 global quedan brechas de integración, varias deliberadamente fuera de la
autorización actual. No se requiere implementar por defecto todas las extensiones
locales enumeradas históricamente como «pendientes».

## Trazabilidad de I1–I20

| Incremento/decisión | Resultado autorizado | Evidencia y límite |
|---|---|---|
| I1, A01–A02 | Captura local/hash/procedencia y preview estructural | [I1](../validation/D5-I1-results.md): 17 pruebas; lectura histórica de tres muestras privadas, sin importación ni gramática completa |
| I2, A03 | Perfil tabular estricto y comparación por documento+ID | [I2](../validation/D5-I2-results.md): 33 pruebas; el corpus ambiguo queda BLOCKED, no se fuerza aceptación |
| I3, A04–A05 | Compatibilidad optativa y anotaciones separadas | [I3](../validation/D5-I3-results.md): 44 pruebas; 627 filas en observación histórica del registro, sin semántica de ejecución |
| I4, A06–A09 | Fuentes/revisiones D2, bytes en PostgreSQL y referencia CAS | [I4](../validation/D5-I4-results.json): 21 SQL; target anterior V1–V11 + V31, no V30 |
| I5, A10–A12 | Comparación SQL, revisión por fila y simulación | [I5](../validation/D5-I5-results.json): 36 SQL; no escribe tareas/requisitos por esta variante |
| I6, A13 | Coexistencia en base nueva V30 | [I6](../validation/D5-I6-results.json): 41 SQL; catálogo/readset y roles dentro del alcance registrado |
| I7 diseño → I8, A14–A19 | Proyección Item/Objective a BACKLOG, correspondencia explícita y aplicación revisada | [I8](../validation/D5-I8-results.json): 68 SQL; V33 solo en laboratorio, sin operaciones; fecha en D5, no tasks.updated_at |
| I9 diseño → I10, A20–A23 | Bootstrap inicial explícito, revisión propia y continuidad | [I10](../validation/D5-I10-results.json): 96 SQL; V34, sin comparación/ACCEPT I5 ficticios |
| I11 diseño → I12, A24–A29 | Reaparición con identidad declarada y ausencia aplicada/versionada | [I12](../validation/D5-I12-results.json): 126 SQL; V35, misma tarea y sin activación |
| I13 diseño → I14, A30–A34 | Resolución origen/local para CHANGED presente | [I14](../validation/D5-I14-results.json): 158 SQL; V36, pareja completa y sin override permanente |
| I15 diseño → I16, A35–A40 | Adopción explícita de tarea existente elegible, preservando toda su fila | [I16](../validation/D5-I16-results.json): 192 SQL; V37, sin trabajo o task_sources previos |
| I17 diseño → I18, A41–A44 | Reaparición con divergencia local, revisión conjunta de identidad/texto | [I18](../validation/D5-I18-results.json): 228 SQL; V38, prueba de ausencia y ACCEPT I5 separados |
| I19 diseño → I20, A45–A49 | Resolución local aislada, base íntegra igual y prueba de cabeza presente | [I20](../validation/D5-I20-results.json): 264 SQL; V39, base intacta/cabeza +1, ausencia vigente bloqueada |

Las suites SQL de esta tabla se solapan. **No se suman** 21+36+41+…+264 como
pruebas distintas. La última campaña I20 incorpora 228 regresiones y 36 casos nuevos.
Sus grupos son 264 SQL V30/V31–V39, 51 Python locales y 157 D2 independientes;
D2 conserva su target histórico. Tampoco se suman los 638 casos D4 o sus 1.085
comprobaciones Compose como si fueran resultados nuevos D5 o I21.

## Línea base local respaldada por evidencia

Esta es una clasificación de auditoría, no una nueva especificación aprobada.

| ID | Capacidad dentro del perfil local sintético | Evidencia |
|---|---|---|
| L01 | Captura acotada de bytes, hashes y reconstrucción de artefactos | I1–I3 y regresiones Python de I20; no autentica autor/commit ni frescura externa |
| L02 | Perfiles versionados explícitos, duplicados/ambigüedad bloqueantes y anotaciones inertes | I2/I3; no parser CommonMark/Gentle-AI completo |
| L03 | Identidad registrada, snapshots/bytes/recibos durables y referencia seleccionada con CAS | I4/I5/I20; no elección por fecha ni avance por lectura |
| L04 | Revisión completa por fila, simulación y paquetes de manifiestos propios | I5/I8–I20; no inferir aprobación desde Status/Verified |
| L05 | Creación/PATCH/enlace/ausencia sin borrado, a tareas BACKLOG sintéticas | I8/I10 y regresiones I20; Item/Objective únicamente |
| L06 | Reaparición e identidad/versiones con conservación de destino | I12/I18; no ID reutilizado para otra entidad |
| L07 | Resolución local presente, reaparecida o aislada, sin mezcla/override | I14/I18/I20; origen y resultado local diferenciados |
| L08 | Adopción explícita sin escribir tarea y con registro/procedencia atómicos | I16; solo BACKLOG sin trabajo/planificación ni procedencia directa previos |
| L09 | CAS íntegro, replay, rollback, concurrencia y recuperación tras respuesta perdida/reinicio | Campaña I20 y casos identificados en su [informe](../validation/D5-I20-results.md) |
| L10 | Roles sintéticos mínimos, fronteras D3/D5 y catálogo/funciones históricos conservados | I20; no usuarios/permisos de producción ni aislamiento contra DDL del dueño |
| L11 | Sin operaciones, reservas, outbox o entregas; limpieza del laboratorio propio | I20: 259 tareas BACKLOG de fixtures/regresiones, resto de contadores operativos cero |
| L12 | CLI local y laboratorio independiente reproducible | [Guía I20](D5-I20-ISOLATED-LOCAL-EDIT-LAB.md) y [runners](../../testing/D5/README.md); SQL requiere laboratorio etiquetado sin red, no dev/producción |

I1–I3 documentan observaciones históricas del corpus autorizado. Este corte **no
relee ni publica** ese corpus, no repite esos conteos y no atribuye datos reales
a las campañas PostgreSQL sintéticas I4–I20. Las etiquetas del operador y hashes
no prueban identidad autenticada, orden remoto o veracidad de claims.

## Brechas respecto a D5 global

| ID | Obligación de origen | Estado y evidencia faltante | Efecto sobre aceptación |
|---|---|---|---|
| G01 | Gentle-AI y routing existentes, D1 y D2 §7 | Perfiles locales implementados; no hay contrato final aprobado del formato completo ni del routing. I1 registró que no encontró un contrato único en la inspección de entonces; no es una búsqueda actual | Impide afirmar integración Gentle-AI completa; requiere muestras representativas sin secretos, gramática/versión y aceptación explícita antes de implementar |
| G02 | Drive con revisión/procedencia de requisitos, D1 | D5 conserva fuentes locales; no acredita lectura incremental, paginación, permisos, cursores/errores de Drive o identidad de revisión remota | Brecha global; primero contrato/datos de prueba y alcance propio, sin conectar servicios bajo autorización actual |
| G03 | Plane incremental/conflictos y conciliación/idempotencia externa, D1/D2 §7 | Recibos SQL y task_sources no prueban efectos Plane; falta contrato de sincronización, colisiones, escrituras condicionadas equivalentes a If-Match y recuperación por proveedor | Brecha global; ningún exactly-once externo queda demostrado por outbox/recibo local |
| G04 | Adaptadores/CLI reales y observación de cuotas comerciales, D1/D3 | Fixtures D4 y seed SYNTHETIC D5 no validan sesiones Claude/Codex, límites observados, permisos unattended o comportamiento real LiteLLM | Brecha global expresamente excluida hoy; requiere autorización separada por proveedor/entorno y evidencia real sin fallback de pago |
| G05 | Requisitos/épicas y tareas groomed del objetivo D1; vocabularios D2 no completan grooming D5 | Proyección actual solo Item/Objective→BACKLOG y evidencia de otros campos; no hay aceptación de un pipeline completo de extracción/grooming | Brecha global de contrato/criterios; no convertir claims en dependencias/estados ni crear épicas ficticias para cubrirla |
| G06 | Criterios integrados de aceptación D5 | Hay matrices por incremento; no se ha aprobado un perímetro/criterio global único que cubra G01–G05 o acepte su aplazamiento como hito parcial | Decisión de alcance pendiente; la auditoría no modifica D1 ni declara completo D5 |
| G07 | Evidencia integrada de esas integraciones | I20 prueba un laboratorio SQL sintético y CLI, no un ciclo Gentle-AI/Drive→Plane con adaptadores/cuotas reales | No reutilizar los PASS locales o D4 como aceptación de conectores reales; sin ejecución nueva autorizada en I21 |

«Brecha global» no significa permiso para trabajar en ella ni defecto del perfil
local. Las prohibiciones de proveedores/credenciales reales y activación siguen
vigentes. Si se elige un hito local, G01–G07 deben quedar visibles como continuidad
de D5 global; no se eliminan ni se renombran D6 para simular su cumplimiento.

## Extensiones locales opcionales o condicionadas a un caso nuevo

| ID | Extensión pendiente | Motivo de clasificación |
|---|---|---|
| E01 | ID reutilizado para otra entidad; transferencia/cambio de destino | A25 exige bloquear; la resolución segura actual no obliga a reasignarlo. Se necesitaría caso y contrato nuevos |
| E02 | Adopción con task_sources o trabajo/planificación previos | A36 limita expresamente la adopción actual. Su rechazo es conforme, no un fallo pendiente del perfil aceptado por corte |
| E03 | Cambio de perfil/política de una correspondencia | I7 los fija. Un perfil futuro podría requerir contrato/migración de identidad, sin exigir hoy una conversión in situ |
| E04 | Múltiples orígenes/fusión de tareas, merge por campos o texto manual | Excluidos de I7/I13/I19; no son necesarios para cumplir la proyección mínima actualmente aprobada |
| E05 | Generalizar a Markdown arbitrario o reparar fuentes ambiguas | I2/I3 son perfiles léxicos acotados y preservan el bloqueo; no se normaliza la fuente para lograr PASS |
| E06 | Ejecutar D5 SQL dentro del Compose dev persistente, UI/daemon o servicio de producto | I4–I20 autorizan laboratorios propios y clientes restringidos. No está integrado en dev ni se promete como producto; requiere otro alcance si se desea |
| E07 | Proyección Sheets/Monday | D1 la define opcional. No bloquea por sí sola el hito local ni debe hacerse obligatoria sin decisión expresa |

Esta clasificación es una propuesta de aceptación para revisión. Si un caso real
necesita E01–E07, habrá que acordar requisitos y validación propios; no se habilita
por el nombre de «pendiente» ni se considera resuelto por esta auditoría.

## Separación de D6 y documentación actual

Hosting/timers activos, identidades y secretos reales, retención operativa,
promoción y despliegue permanecen en D6 según D2/D3/D4. No se piden ni se instalan
aquí. La interfaz Angular está prevista «later» en D1; no hay criterio que obligue
este corte a entregarla. Las garantías de producción/SLA, DDL hostil o aislamiento
de código no confiable tampoco se deducen de las pruebas sintéticas.

Los README principales resumían D5 hasta preview/comparación/simulación. Se actualiza
su breve entrada bilingüe para incluir las tareas BACKLOG/revisión del laboratorio
y enlazar esta auditoría, manteniendo límites y el detalle en subdocumentos.
Los documentos de incrementos conservan sus frases históricas «diseño», «sin SQL» o
«pendiente»; la aprobación posterior/implementación se consulta en su siguiente
corte. No se reescriben informes ni manifiestos anteriores.

## Qué se ha comprobado ahora

I21 verifica hashes, coherencia de autoridad/alcance, matrices y enlaces; no inicia
Docker ni reejecuta parser, SQL, D2 o D4. El inventario JSON identifica fuentes y
resultados consultados y distingue esta auditoría de la campaña I20. Un hash vigente
vincula contenido a evidencia registrada; no constituye una ejecución nueva,
prueba de ausencia de defectos o aceptación humana del cierre.

Siguiente decisión concreta en la [tabla de revisión](D5-I21-ACCEPTANCE-REVIEW.md):
aprobar o ajustar la clasificación y elegir continuidad de D5 global o preparar
la aceptación formal de un hito local. Nada de ello se da por aprobado al publicar.
