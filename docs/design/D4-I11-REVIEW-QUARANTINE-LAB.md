# D4 I11 — revisiones A21 y cuarentena A22

Fecha: 2026-10-20. Opciones A21/A22 aprobadas expresamente; implementación y
validación acotada registrada por separado. D4 abierto. No se promueven migraciones ni se usan
proveedores, credenciales o máquinas físicas reales.

## Revisión sin nueva liquidación

V28 propuesta conserva V1–V27. `review_revisions` es una cadena append-only por
entrega, con cabeza única y CAS de cabeza, versión de operación y conjunto completo
de recibos. El ancla histórica es una liquidación I9/A20, checkpoint v1/v2 o
aceptación final independiente. Los recibos y PASS anteriores permanecen intactos.

El verificador vuelve a comprobar artefactos y observación host firmada fresca y
solicita el sello del mismo receptor con el comando de cierre original. Se exige
el mismo receiver ID, secuencia de cierre, identidad y resultado canónico de cada
paso: estado, hash APPLIED y generación. Un APPLIED no puede desaparecer; un hash
histórico incompatible o diario perdido mantiene el bloqueo. Un ACCEPTANCE_FAIL
tardío abre cuarentena y no puede quedar oculto por una revisión de delta cero. Los recibos tardíos
UNKNOWN/ABSENT solo pueden explicarse mediante el mismo resultado concluyente ya
sellado. Una revisión no añade pasos aplicados después de un cierre ABSENT.

La contabilidad verifica el prefijo congelado y los costes exactos por cuenta.
Una liquidación de la generación vigente debe conservar consumo exacto y cero
compromiso pendiente. Revisar una generación anterior no borra consumo posterior
ni compromiso de otro intento. Una corrección ADJUST de esa reserva no se resuelve
por esta ruta de delta cero. `review_revise` no llama a CONSUME, RELEASE o ADJUST.

Cada revisión incrementa `row_version` e invalida autorizaciones antiguas. Tras el
cierre explícito del caso, la continuación de un checkpoint requiere una nueva
`review_authorization` y un CLAIM nuevo, enlazado mediante `review_links`. Las
credenciales nativas de checkpoint se conservan como procedencia histórica; no
sustituyen a la autorización vigente de revisión. `ReviewPlanningStore` admite
`SEALED_REVIEW_CHECKPOINT` y conserva los adaptadores anteriores. Se mantienen
operación, reserva, mapping, cuentas, contador D2 y TOP_UP al vector original.
Para sellos A20 se reutiliza la autorización explícita de ausencia, con cabeza
actual y sin fabricar un checkpoint de progreso.

## Reapertura como caso separado

La inserción de un recibo después de una liquidación/checkpoint o resultado terminal
abre un caso en la misma transacción, bajo los mutex D3/D2. Abrir/cerrar el caso no cambia el estado de la operación:
CANCELLED/COMPLETED se conservan cuando siguen vigentes. Una autorización anterior
que la llevó a READY queda invalidada, sin borrar su transición histórica.
El caso no fabrica una lease. Una revisión
válida no levanta por sí sola esta cuarentena.

`review_cases`, `review_affected`, `review_unbound_affected`, `review_containments`,
`review_barriers` y `review_closures` son hechos append-only. La cuarentena afecta
operación, tarea, recurso y claves de exclusión compartidas. Propaga suspensión a
consumidores HARD y MOCKABLE de integración real, incluidas capacidades resueltas;
SOFT/OPTIONAL conservan su semántica. No borra DONE, verificaciones ni PASS.

**Extensión aditiva del contrato aplicado en el laboratorio:** V28 conserva las
fuentes D2/D3 cerradas, pero amplía sus funciones de elegibilidad efectiva y las
guardas de ejecución D2/D3 bajo A22. La entrada directa `d2.execution`
adquiere primero el mutex D3 y aplica la misma guarda física antes de conceder
autoridad; se conserva el orden de bloqueo D3→D2. Captura, publicación, CLAIM, START, HEARTBEAT,
aceptación y retirada consultan la cuarentena. CALLBACK factual y EXPIRE siguen
siendo posibles; no equivalen a aceptación ni prueba de parada. El readset añade
los hechos de revisión. La prioridad, reparto 70/20/10 y reservas no cambian.

El conjunto de leases afectadas se captura al abrir el caso hasta punto fijo:
incluye actores que comparten exclusión física y los consumidores de esos actores.
La pertenencia al conjunto sigue bloqueando aunque cambien posteriormente sus
claves de política. Las que carecen de
entrega D4 se registran como desconocidas sin transporte y **bloquean el cierre**;
no se supone que no exista proceso ni se inventa una barrera. También se conserva
un hecho de origen heredado sin entrega: abre un caso sin ancla D4 revisable, que
permanece bloqueado. Esta ampliación no implementa resolución de esas leases/orígenes.

## Contención y cierre

El verificador cierra duraderamente cada canal afectado y conserva el sello firmado.
El grant anterior puede ser válido hasta su vencimiento o hasta que el cierre se
serialice con el receptor; el flag SQL no lo revoca físicamente. La denegación de
renovación activa la parada del supervisor conforme a A10, y la observación host
independiente acredita después la desaparición del proceso/grupo exactos. Una
observación que aún dice «vivo» no puede convertirse en una barrera.

Cerrar exige revisión canónica y contabilidad vigentes, todas las barreras y
expiración/reconciliación de las leases retenidas. La lease de una recuperación
terminal ya liquidada puede conservarse en VERIFYING únicamente para aceptación
posterior independiente, con prueba de parada/cierre, vencimiento y liquidación
vigente. No se convierte en autoridad de ejecución. El caso no libera ni consume
compromisos de los actores afectados; estos necesitan su propia reconciliación.

El driver solicita explícitamente el cierre con motivo. No autoriza continuar ni
rearma un worker. Un recibo posterior abre otro caso y exige otra revisión/barrier;
las revisiones y cierres anteriores siguen en la historia. Se reutiliza el comando
real de un cierre anterior cuando el receptor ya había cerrado esa identidad.

## Ingreso y campañas

Las rutas `/lab/review/capture`, `/ingest`, `/revise`, `/contain`, `/barriers` y
`/expire` viven en el verificador; el driver proporciona IDs, versión/cabeza CAS o
selección de paso, nunca pruebas propias. La captura durable conserva el recibo
real consultado antes del efecto para poder demostrar entrega tardía. El replay
no vuelve a consultar ese hecho como si fuera nuevo. Las pruebas criptográficas
se obtienen del host, artefactos montados de solo lectura y receptor mTLS.
`/lab/review/close` y `/authorize`, en control plane, exigen driver explícito.
Los workers no reciben SQL ni autoridad para revisar o cerrar casos.

`bash testing/D4/run-review-lab.sh` construye offline y ejecuta:

- S22: checkpoint v2, dos reaperturas sucesivas, autorización anterior inválida,
  revisión con delta cero, autorización/rearme nuevos y continuación completa.
- S25: checkpoint parcial v1, recibo tardío y continuación revisada hasta PASS.
- S23: SUCCESS completado; PASS conservado, aceptación efectiva suspendida y cierre
  explícito sin nueva liquidación ni intento.
- S24: consumidor HARD ya ejecutándose; cierre del receptor, renovación denegada,
  parada real, barrera independiente y expiración real. El actor queda RECONCILING
  con su compromiso, mientras se cierra el caso del productor. El host marca la
  tarea del productor DONE como administración de fixture **después** del PASS
  independiente; ni worker ni verificador reciben esa facultad.
- S20/S16: regresiones de ausencia A20 multicuentas y reconciliación I9.

Las pruebas SQL del propietario usan pruebas sintéticas y no acreditan firmas ni
parada kernel. Las suites históricas D2/D3 se ejecutan aparte en sus targets, sin
presentarlas como pruebas de V28. El [informe I11](../validation/D4-I11-REVIEW-QUARANTINE-results.json)
registra 222 pruebas D4 (21 nuevas), 175 de regresión D3, 157 D2 y 25 verificadores
locales: 579 pruebas positivas. La campaña nueva reúne 231 comprobaciones en seis
proyectos Compose limpiados selectivamente. No vuelve a ejecutar todos los casos
históricos sobre V28 ni sobrescribe informes anteriores. Los pilotos excluidos
y sus correcciones quedan identificados en el mismo informe.

## Límites y pendientes de D4

Esta ruta no resuelve costes variables, compensaciones, diario perdido, hashes
incompatibles, receptores múltiples ni leases sin transporte D4. En esos casos se
conserva el bloqueo. Quedan la integración general de verificadores Git/archivos/
restauración con aceptación SQL/HTTPS, presencia durable, matriz completa de fallos,
resets/dependencias sobre el último target y campaña específica de polling/reinicio
con revisiones. Operación física, proveedores reales y promoción siguen en D5/D6.
La revisión final y el cierre D4 requieren aprobación expresa del usuario.

Ampliación posterior: [I12](D4-I12-INTEGRATED-VERIFIERS-PRESENCE.md) aborda los
pendientes anteriores de verificadores integrados, presencia, matriz actual y
polling/reinicio. La [revisión final](D4-I12-ACCEPTANCE-REVIEW.md) conserva separado
el cierre formal sujeto a aprobación del usuario.
