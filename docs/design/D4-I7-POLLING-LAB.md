# D4 I7 — bucle de polling sintético

Estado: polling normal implementado y validado en el laboratorio.
**D4 abierto**. [Contrato y decisión A12 aprobada](D4-I7-POLLING-REVIEW.md).

[Resultados I7](../validation/D4-I7-results.json): S01–S12, 367 comprobaciones;
92 pruebas D4, 175 D3 y 157 D2 sin fallos, errores ni omisiones en las ejecuciones
finales. Cleanup de los doce proyectos sin contenedores, redes ni volúmenes propios.

## Flujo y límites

`POST /lab/loop/start` exige principal driver y exactamente command_id,
max_operations (1–4) y duration_seconds (10–240). Registra y fuerza a disco el
comando antes de iniciar. Un replay idéntico devuelve la misma confirmación y
no rearma; otro contenido con el mismo ID se rechaza, también tras reinicio y
después de ejecutar otros comandos. Un solo bucle/asignación local a la vez.

El bucle usa el transporte D4 HTTPS existente. POLL vacío confirmado vuelve a IDLE
y espera 250 ms, 500 ms, 1 s, 2 s, 4 s y hasta 5 s, más jitter de 0–100 ms.
El presupuesto temporal limita nuevas peticiones POLL, no convierte el trabajo
no interrumpible ya admitido en una cancelación. Una ejecución admitida puede
superar ese presupuesto: conserva los límites de fixture y watchdog de I6.

Una operación sigue ACK/START/grant/supervisor/efecto/callback. Un callback
confirmado pasa a WAITING_ACCEPTANCE. El worker consulta su estado remoto y
solo retira tras aceptación independiente y salida local íntegra. Archivo por
intento antes de limpiar el estado, y después POLL para la siguiente operación.
El contador del bucle cuenta retiradas verificadas; no reemplaza intentos D2.
En S10 ambas estimaciones duran un minuto para que el segundo slot protegido
venza su espera dentro de la campaña. El piloto con estimaciones de quince minutos
esperó correctamente: no se modificó D3 para adelantarlo. Archivo y directorios se
fuerzan a disco antes de sustituir el estado local por IDLE; no se inyectó un corte
de alimentación del filesystem.

V23 añade una consulta de solo lectura, `d4.worker_execution_status(worker,delivery)`.
Revalida catálogo, ownership e identidad. `retirable=true` exige COMPLETED en la
operación e intento exactos, generación vigente, ausencia de lease y compromiso
pendiente, PASS sin FAIL, sin UNKNOWN ni contradicciones y prueba independiente
ligada al delivery con cierre del receptor y parada. Admite la aceptación final
del sucesor I5; el delivery anterior no se vuelve retirable por completar el sucesor.
El rol runtime recibe solo EXECUTE. No hay nueva transición, RELEASE ni evidencia.

`/lab/execution/status` es un puente de laboratorio mTLS, no una API de SQL remoto.
Solo acepta delivery_id; el principal worker procede del certificado. La prueba
de parada en SQL proviene del verificador restringido; además, el worker contrasta
su evento local EXITED y hashes mediante el supervisor. Un callback, un PASS
aislado o una asignación null no bastan para la retirada automática.

## Pausas y reinicio

Transporte incierto, fallo de fixture, UNKNOWN, contradicción o un estado remoto
inesperado pausan el bucle. No se hacen nuevos CLAIM ni se libera compromiso.
A12, aprobada expresamente el 2026-10-20, fija CHECKPOINT_READY como pausa de
todo el bucle. Sellar el checkpoint y autorizar su continuidad no rearman polling.
El driver retira explícitamente el estado local (`/lab/next`) y emite un nuevo
`/lab/loop/start`. La autorización A08 sigue siendo imprescindible para admitir
el sufijo de la operación original; el nuevo presupuesto local no reinicia el
contador de intentos D2. La campaña I7 original no incluía esta decisión posterior.

Tras reinicio con estado, comando de bucle o historia de ejecución, permanece
RECOVERY_REQUIRED. Repetir start no vuelve a ejecutar. El rearme explícito de una
historia sin identidad requiere asignación remota null y todos los intentos locales
resueltos, incluso si son cero. Historia ausente/corrupta o logs alterados bloquean.
Una identidad recuperada sigue la ruta manual previa; no se respawnea un intento.

`/lab/next` puede retirar explícitamente un callback confirmado solo con las mismas
guardas de COMPLETED/prueba/EXITED; nunca mientras el bucle esté activo. Conserva
la ruta de checkpoint y recuperación anterior, con autorización explícita de
continuidad A08 y lease viva para COMMIT según A09.

## Campaña ejecutada

`bash testing/D4/run-polling-lab.sh` construye offline y ejecuta S01–S12 en dos
grupos de proyectos independientes. S01–S09 son regresión I4/I5/I6. S10 comprueba
dos operaciones del mismo worker, espera de aceptación y archivo, sin cambiar
cuenta física ni pools. La siguiente planificación sigue siendo explícita por el
driver (`/lab/plan`, alias de captura/cálculo/publicación CAS acotados).

S11 comprueba trabajo sin aprobación: POLL vacío, presupuesto/backoff, deduplicación
durable, reinicio sin respawn y rearme explícito vacío. S12 pierde el callback tras
APPLIED y comprueba pausa sin retirar ni volver a reclamar. Una prueba SQL separada
cubre el sucesor I5 y el rechazo del delivery antiguo.

No hay daemon de planificación o despliegue D6. Siguen pendientes la generalización
a varias cuentas/pasos/checkpoints, verificadores genéricos y parte de la matriz
negativa. A04 conserva UNKNOWN/contradicciones bloqueados; no se amplía A09.

## Ampliación A12: checkpoint dentro del bucle

`bash testing/D4/run-checkpoint-polling-lab.sh` ejecuta solo S13, con evidencia
[aditiva A12](../validation/D4-I7-A12-results.json). Reutiliza el worker y SQL V23
sin cambios: la pausa ya era conservadora. Se mantiene separada la campaña
S01–S12 anterior; sus cifras no se suman como si se hubieran repetido ahora.

S13 pasó 51 comprobaciones; la regresión separada pasó 30 pruebas D4, 175 D3
y 157 D2, sin fallos, errores ni omisiones. El proyecto Compose quedó sin
contenedores, redes ni volúmenes propios.

S13 comprueba pausa antes y después del sellado, ausencia de nuevos intentos
tras autorización y planificación, rechazo de start mientras permanece el estado
de checkpoint y rearme explícito. Después verifica el sufijo de la misma operación,
nuevo intento/generación, misma reserva, TOP_UP original y consumo total 10 sin
reaplicar el prefijo. El callback y grant anteriores siguen fenced. Solo la
aceptación independiente del sufijo permite retirada normal y vuelta a IDLE.

El archivo del prefijo procede de la retirada manual; el del sufijo añade el
recibo de retirada normal. No se generaliza a checkpoints encadenados, múltiples
cuentas ni recuperación automática tras reinicio. D4 continúa abierto.
