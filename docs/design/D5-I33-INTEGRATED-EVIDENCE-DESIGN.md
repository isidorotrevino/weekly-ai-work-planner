# D5 I33 — contrato de unión y evidencia integrada para revisión

Fecha: **2026-10-23**, Europe/Madrid. **PREPARED_FOR_REVIEW; sin implementación.**
[Matriz UI01–UI40](D5-I33-INTEGRATED-EVIDENCE-REVIEW.md) ·
[Comprobaciones documentales](../validation/D5-I33-design-review.json) ·
[Contrato I23](D5-I23-GLOBAL-INTEGRATION-DESIGN.md).

English: proposed synthetic integration boundaries and evidence inventory for
GI33/GI34/GI38/GI39/GI40. Design only; F was selected for further durable design,
not implementation. Isolated volatile PASS results do not establish integrated recovery.
No publication, real providers, activation, deployment or global D5 acceptance.

## Autoridad y estado

El usuario eligió **«P0 + A»**: conservar I32 y el handoff sin publicar y preparar
contrato integrado + matriz de los cinco criterios antes de implementar. Esta
selección autoriza esta preparación documental; no aprueba el contrato resultante,
una ampliación durable ni código. Después eligió **«F»** para completar el
[contrato durable](D5-I33-DURABLE-INTEGRATION-DESIGN.md) y su
[matriz de reinicio](D5-I33-DURABLE-INTEGRATION-REVIEW.md), solo para revisión.
F está seleccionado para diseño; el contrato resultante y su implementación
siguen pendientes de aprobación.

Base local observada: `79c696a66f85923173650f271995c69569b50b0d` (handoff), hijo
de I32 `7b64d87ef45b4973a5ea80dc676f1bd2eca220f7`. La lectura de `main` remoto
confirmó `8e90a87cce7edbefc6c854a73ff1f60a20ae8485` en esta sesión. Ninguno de
los dos commits pendientes está autorizado para publicación; tampoco esta propuesta.

D1–D4 cerrados y [D5-LOCAL-SYNTHETIC-I1-I20 aceptado](D5-LOCAL-SYNTHETIC-approved.md)
conservan sus perímetros. **D5 global y G01–G07 abiertos**. La cuenta sigue en
30/35 S con evidencia acotada; los cinco S integrados y los siete R siguen pendientes.
Ni este contrato ni sus comprobaciones son una campaña ejecutable nueva.

## Inventario y aplicabilidad — GI33/GI34

Una futura campaña deberá registrar run_id, commit base, diff/hash del árbol
realmente ejecutado (también archivos nuevos), Python/SO, comandos y códigos de
salida, código/parser/harness/config de fixture, perfiles/políticas/adaptadores,
esquemas/API declaradas, semillas/reloj y límites efectivos. Una etiqueta de versión
no sustituye SHA-256 del código; configuración declarada no acredita API real.
No leer `.env`, credenciales, corpus privado ni configuración de dev para construirlo.

Cada entrada de evidencia liga criterio, escenario, inputs exactos, frontera,
oráculo, grupo/target, resultado, exclusiones y recursos propios. Cambiar un input
relevante conserva el resultado histórico pero marca su aplicabilidad actual como
STALE_INPUTS o NOT_RUN hasta nueva validación. No reescribir informes sellados ni
extender invalidación a cierres históricos como si fueran revocados. Cambio solo
del índice se explica separadamente; no invalida por sí mismo código que no cambió.

Separar campaña nueva de regresiones efectivamente reejecutadas y evidencia
histórica solo verificada por hash. IDs distintos dentro de una campaña se cuentan
una vez; filas de matriz, assertions y suites acumulativas no son tests adicionales.
Conservar target V11/V12/…/V30 y propuestas V31–V39 donde corresponda, sin atribuir
V30 a todas las suites ni sumar campañas anteriores. No se propone ejecutar SQL,
Docker o D2–D4 en la primera unión en memoria; sus hashes no acreditan reejecución.

## Fronteras comprobadas y unión propuesta

| Componente existente | API/estado relevante | Uso propuesto y límite |
|---|---|---|
| [I26](D5-I26-DRIVE-INCREMENTAL-LAB.md), `FixtureStore` | `advance`, `snapshot`, `read_command`, `inspect`; filesystem propio | Consumir evento de un commit alcanzable exacto, bytes/hash/ámbito/grado; cursor no elige referencia ni aprueba fuente |
| [I32](D5-I32-PROFILES-QUOTAS-LAB.md), `EligibilityLab` | `capture`, `review`, `prepare_evaluation`, `validate_evaluation`; volátil | Perfil seleccionado y evaluación revisada; resultado positivo es comprobación de fixture, nunca reserva o permiso de ejecución |
| [I24](D5-I24-OFFLINE-INTEGRATION-LAB.md), `MemoryLab` | `capture`, `prepare_effect`, `apply_effect`, `entity`; volátil | Recorrido principal TASK de registro, revisión SOURCE/EFFECT propias y efecto D2 simulado |
| [I30](D5-I30-RELATIONAL-BATCH-LAB.md), `BatchLab` | `capture`, `prepare`, `apply`, `inspect`; volátil | Recorrido tipado separado con relaciones aditivas; no convertirlo en registro I32 |
| [I28](D5-I28-PLANE-RECONCILIATION-LAB.md) | `ReconciliationLab.bind/prepare/review/dispatch/reconcile`, `PlaneFixture`; volátil | Proyectar una TASK exacta del efecto de fixture; preservar UNKNOWN y conflictos, sin Plane real |

Se propone un coordinador/adaptadores nuevos de fixture, sin editar parsers,
módulos históricos o sus almacenes. La compatibilidad se deberá probar; esta tabla
no afirma que exista un conector entre ellos ni una API común de restauración.
No acceder a atributos privados para fabricar revisiones, recibos o restauración.
Si una API no permite la guarda requerida, bloquear y revisar el contrato antes de
modificar componentes. `inspect` es una lectura privada de prueba, no una API durable.

**Recorrido T (principal):** evento Markdown sintético I26 → mismos bytes en I32 e
I24 con `task-register.v1` → revisiones SOURCE separadas → evaluación I32 revisada
→ efecto TASK I24 revisado → snapshot exacto de esa TASK → binding/proyección I28
revisados → envío simulado/conciliación → recibo integrado de evidencia.
No utilizar `MemoryLab.apply_projection` como sustituto de la conciliación I28.
El adaptador conserva el grado I26 en el envelope de unión: una captura I32/I24
LOCAL no eleva OBSERVED_EXPORT a revisión remota inmutable. La primera propuesta
T admite solo Markdown de fixture; exportación Docs queda pendiente de otro alcance.

**Recorrido R (relacional separado):** bytes del envelope I30 conservados como
artefacto de fixture → SOURCE/BATCH I30 propios → lote atómico → proyección I28
exclusivamente de TASK seleccionadas explícitamente. Requisitos, épicas y relaciones
no se proyectan a Plane. No pasar el JSON I30 por un parser Markdown I32, convertir
sus correspondencias, ni inventar perfil/gramática Gentle-AI. La evaluación I32
puede ser escenario separado; no se presenta como revisión de esa fuente R.
Primera implementación propuesta: T; R queda diseño/no ejecutado salvo alcance
expreso posterior. GI38/GI39 no se darán completos por cubrir únicamente T.

## Envelope, revisiones y vigencia entre fronteras

Propuesta conceptual `d5.integrated-evidence-fixture.v1`, sin decoder implementado:
run_id, scenario_id, recorrido, project_id/document_id, source identity, commit/event
I26, bytes_sha256, grado, perfil/hash/generación, IDs de captura/preview/manifiesto,
revisiones exactas por etapa, generaciones/hash de efecto local, binding/capabilities,
base remota, command_id/request_hash y recibos referenciados. Claves cerradas y
serialización canónica; excluir su propio hash y revisiones futuras del hash base.
Rechazar duplicados, campos desconocidos, discrepancias de ámbito/bytes/identidad,
versiones desconocidas y excesos antes de efectos; nunca truncar o adoptar por título.

SOURCE I32, EVALUATION, SOURCE/EFFECT I24, SOURCE/BATCH I30 y revisión I28 son actos
separados. El coordinador verifica las correspondencias exactas; no copia un ACCEPT
para producir otro. Se conserva cada manifest original y un enlace de unión nuevo.
Los recibos de unión son evidencia, con `grants_execution_authority=false`, y no
son recibos SQL ni comandos operativos D2/D3/D4. Una revalidación de evaluación
requiere comando nuevo sobre hechos/reloj actuales; `read_command` o replay de
un positivo histórico no la sustituyen.

No basta copiar una TASK a `ReconciliationLab.bind`: una edición posterior en el
almacén dueño podría dejar esa copia obsoleta. Se propone una generación de unión
monótona y un registro explícito de revisiones/selecciones. Toda mutación local de
fuente, selección, revisión, política o efecto de este harness debe pasar por una
puerta común que avanza esa generación, incluso A→B→A. Antes de cada efecto local
se revalidan bajo esa puerta los inputs/versiones exactos y el reloj. Se impide
mutación local entre esa comprobación y el CAS local; no llamar al doble Plane
mientras se retiene la puerta o un lock de dominio.

Al entregar un ticket al doble se fija un punto de autorización de envío de fixture.
Una revocación anterior bloquea; una revocación posterior no deshace un efecto ya
en vuelo. Tras respuesta se revalida: efecto confirmado histórico + STALE o UNKNOWN
no se convierte en éxito vigente. La edición remota concurrente depende del CAS
del doble; ninguna puerta local acredita atomicidad remota. Acceso directo a los
labs evita la puerta y queda fuera de la garantía del harness confiable; no se
promete aislamiento frente a un caller Python hostil.

Cambiar fuente/perfil/cuenta/política/observación/revisión/base local o binding
requiere nuevo paquete y revisiones pertinentes, sin remapear correspondencias.
Caducidad/horizonte se verifica por reloj aunque no cambie generación. Replay lee
recibo histórico por command_id/request_hash y no rebobina datos, revisiones o
conflictos. Mismo ID con otro request bloquea. Un positivo no consume/reserva cuota
ni habilita workers; A73/A74 y contratos D3 permanecen intactos.

## Fallos, reinicio y decisión de almacenamiento — GI38

Las fronteras a instrumentar son: F0 commit/cursor I26; F1 importación/selección de
captura; F2 preparación/revisiones/evaluación; F3 aplicación de efecto local;
F4 snapshot/binding y paquete Plane; F5 registro del intento/entrega al doble;
F6 efecto remoto simulado; F7 registro de respuesta/conciliación y recibo de unión.
Para cada una: fallo antes, después y respuesta perdida cuando corresponda. Cada
prueba compara estado previo/posterior, recibos y conflictos con un oráculo propio;
no solo comprobar que no hubo excepción. No prometer una transacción común F0–F7.

| Opción pendiente | Qué permitiría proponer | Qué seguiría pendiente |
|---|---|---|
| M — unión volátil acotada | T, fallos y carreras del mismo proceso, pérdida de respuesta con objetos vivos; I26 mantiene solo su recuperación de captura | Reinicio integrado F1–F7, R y GI38 completo; memoria perdida → RECOVERY_REQUIRED, sin reconstruir autoridad ni reenviar |
| F — contrato durable adicional primero (recomendación para avanzar GI38) | Diseñar filesystem sintético nuevo y separado: estado local/recibos/revisiones y ledger de intentos, más doble remoto con estado independiente superviviente | No autoriza implementarlo; formato/commit/locking/importación/restauración/matriz durable deben quedar completos y revisados antes de código |

F no consiste en guardar stdout, picklear objetos ni reproducir comandos ACCEPT.
Necesitaría fijar esquema versionado, raíz/commit atómico, fsync/rename/flock,
migración rechazada por defecto, snapshots íntegros, CAS multiproceso, continuidad
monótona de generaciones/revocaciones y registro durable del intento antes del envío.
El doble remoto tendría durabilidad independiente: matar al cliente sin borrar el
efecto remoto. Después de caída entre envío y respuesta, preservar UNKNOWN y
conciliar por ticket/identidad/hash antes de cualquier retry. Cero coincidencias
no acredita ausencia; perder/corromper ledger obliga a bloqueo y conservación de
evidencia, sin recreación automática. Un reloj reiniciado no renueva frescura.

Estas eran las obligaciones iniciales de F. La selección posterior **F** se
concreta en el [contrato durable para revisión](D5-I33-DURABLE-INTEGRATION-DESIGN.md),
que prevalece para almacenamiento y autoridad nueva. El siguiente párrafo conserva
la lista de obligaciones de partida: haría
falta decidir atomicidad de estado local/recibo, tratamiento de commits inciertos,
arranque y recuperación, integridad/cadenas/tamaños, persistencia del doble,
presupuestos, matriz por proceso y limpieza antes de aprobar implementación.
No reutilizar I26 como outbox ni restaurar autoridad con `inspect` de I28/I30/I32.
SQL es otra alternativa de alcance futuro; no está incluida en M o F.

## Concurrencia, auditoría y límites — GI39/GI40

Carreras propuestas con barreras/Event: origen/revisión frente a efecto local;
perfil/política/observación/reloj frente a evaluación; edición local frente al
snapshot y envío; edición Plane frente al CAS; conciliación frente a respuesta.
Ejercitar ABA y revocación durante envío. La ausencia de sobrescritura se comprueba
con campos ajenos/sentinels y generaciones, sin elegir ganador por fecha. Preservar
conflictos/UNKNOWN después de otro paquete, cambio de fuente o replay.

Límites iniciales M propuestos: un proyecto/documento por escenario, ≤8 escenarios,
≤16 enlaces de frontera por escenario, fuente ≤2 MiB, envelope de unión ≤1 MiB,
≤128 recibos de unión. También rigen los límites de cada componente; gana el más
restrictivo y excederlo bloquea antes de publicar efecto. No benchmark ni cobertura
a tamaño completo por probar un presupuesto reducido. F debe fijar sus límites
durables antes de implementación. R conserva sus límites originales sin ampliarlos.

Una futura campaña debe acreditar cero HTTP/SDK/CLI de proveedores, cero SQL/D2
persistente, consumo/reservas/operaciones/intentos operativos/activación. Los intentos
Plane de fixture se cuentan aparte; no son intentos de ejecución D2. No crear
operaciones para probar una guarda: usar flags de fixture negativos identificados.
Datos e inspecciones íntegros quedan privados; salida pública solo códigos, hashes
y contadores permitidos, sin texto fuente, rutas privadas o cuerpos de error.

Inventariar recursos creados por la campaña y comprobar terminación de hilos/hijos,
limpieza solo de sus raíces con marca y sentinels hermanos sintéticos intactos.
No inspeccionar, parar o borrar dev/run_data/D4. Tal comprobación sintética no
prueba por sí misma el estado de toda instancia externa. M propone una raíz I26
propia para T y hilos nuevos; esa raíz conserva únicamente captura, no estado
F1–F7. No añade hijos nuevos para probar reinicio integrado. Los temporales/hijos
de regresión I26 se contabilizan aparte de la raíz T. F necesitaría recursos
y procesos nuevos explícitos. Sin limpieza global/prune ni borrado de evidencia ajena.

## Puertas de continuación

1. **F seleccionado para diseño.** Revisar esta propuesta, el contrato F y su
   matriz DF01–DF48; T es el recorrido inicial. No hay implementación autorizada.
2. Para M, aprobar contrato + alcance T y autorizar expresamente su implementación,
   manteniendo los casos durables y R pendientes. Aprobar solo diseño no inicia código.
3. Validar solo lo autorizado con inputs actuales y evidencia nueva; GI33/GI34/
   GI38/GI39/GI40 continúan pendientes hasta evaluar cobertura y exclusiones reales.
4. Publicación requiere autorización de commit concreto independiente de esas decisiones.

Sin proveedores/credenciales reales, consumo/reservas, activación, promoción,
despliegue o D6 en ninguna opción. No crear cierre global D5 ni ampliar A52.
