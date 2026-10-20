# D4 I5 — checkpoint parcial y continuación sintética

Estado: implementación del contrato A/A aprobado, para revisión; **D4 abierto**.
[A08/A09](D4-DECISIONS.md) autorizan CANCELLED→READY exclusivamente con checkpoint
sellado y autorización explícita, y COMMIT solo desde RUNNING con lease vigente.
No se habilita continuación desde RECONCILING ni resolución de UNKNOWN.

Validación registrada: S01–S05, 157 comprobaciones; 73 pruebas D4, 175 D3
y 157 D2 sin fallos/errores/omisiones. Regresión D3/D2 en copia y con sus targets
históricos separados; [informe I5](../validation/D4-I5-results.json).

Incremento posterior: [I6](D4-I6-LONG-RUNNING-LAB.md) añade solicitud cooperativa
durante proceso vivo y renovaciones. Los límites y resultados de este documento
describen la campaña I5 original; no se reescribe su evidencia histórica.

## Implementación y frontera

V19 añade intención de pasos, solicitud/prueba/checkpoint, autorización, enlace
único al intento sucesor y recibos de comandos inmutables. La intención se liga a
los bytes del contexto antes del primer CLAIM; no admite backfill de una ejecución
ya iniciada. Un trigger verifica hash/manifiesto y ausencia de intentos previos.

COMMIT revalida RUNNING, lease, versión e identidad exactas, contexto/política del
snapshot de ejecución, prueba independiente y ausencia de evidencia contradictoria
o efectos inesperados. CONSUME incremental, RELEASE del remanente, cancelación del
intento/operación, retirada de lease, procedencia e historia/outbox hacen un solo
commit. Si la lease venció o falla cualquier guarda, rollback íntegro. La parada y
el cierre ocurren antes, fuera de SQL; ningún mutex espera al proceso o a HTTPS.

AUTHORIZE exige el checkpoint exacto y su versión de cancelación. Conserva la misma
operación y reserva, cambia a READY y registra decisión/outbox. No reserva ni crea
intento. La transición genérica D2 sigue rechazando CANCELLED→READY. El despacho
posterior hace TOP_UP al vector original y crea un intento/generación D2 nuevo,
enlazado una sola vez al checkpoint y autorización. No reinicia max_attempts.

El corte ejecutable se limita a un checkpoint, dos pasos ordenados y una cuenta
vinculante sintética por operación: coste aditivo 4+6 y vector original 10. Un
vector con varias cuentas se rechaza antes de liquidar; no se interpreta un escalar
como consumo multidimensional. Generalizar costes, pasos/canales y checkpoints
encadenados queda fuera de esta fixture. Las cuentas físicas, pool, ventana,
recurso y vía permanecen congelados; no hay rollover ni reparto residual nuevo.

| Momento | Pendiente | Consumido acumulado | Disponible PLANNED (límite 70) |
|---|---:|---:|---:|
| Primer CLAIM | 10 | 0 | 60 |
| Checkpoint sellado | 0 | 4 | 66 |
| TOP_UP de continuación | 10 | 4 | 56 |
| Callback final y aceptación | 0 | 10 | 60 |

INCIDENT 20 y UNCERTAINTY 10 no cambian. Con solo 6 disponibles, el TOP_UP de 10
rechaza el CLAIM. Consumo ya asentado no se vuelve a facturar; no se usa ADJUST
para ocultar divergencia ni se fabrica un ABSENT del primer paso.

## Observación, planificación, publicación y despacho

V20 contiene copias aditivas de las funciones aprobadas de observación, publicación,
despacho, entrega y transporte, conservando sus guardas. Solo amplía el predicado
de ausencia previa con una admisión de checkpoint sellado/autorizado. Es SQL
estático revisable, sin reescribir funciones al arrancar ni flags de sesión para
saltar guardas. `generate-continuation-admission.py --check` reproduce y contrasta
estas copias y el adaptador Java contra sus fuentes con SHA256; un cambio inesperado
falla la comprobación. No modifica los archivos V1–V18 ni el código cerrado D3.

`ContinuationPlanningStore` es un adaptador D4 separado. Lee la admisión tipada
SEALED_CHECKPOINT de la captura inmutable; los recibos APPLIED/ABSENT reales siguen
intactos. La respuesta de planificación se identifica con
`d4.continuation.snapshot.v1`; el cálculo reutiliza internamente el modelo/algoritmo
D3 y su manifiesto. El adaptador histórico sigue considerando inseguro ese retry y
las entradas D3 de publicación/CLAIM siguen rechazándolo. El worker no proporciona
un booleano de admisión.

Intenciones, solicitudes, pruebas, checkpoints, autorizaciones, enlaces y admisión
forman parte del readset de captura/CAS. Cambiar evidencia entre captura y publicación
invalida el plan. El CLAIM revalida prueba vigente y todas las guardas heredadas:
plan, límites/intentos, dependencias e integración, prioridad por camino bloqueante,
aprobaciones/contexto, capacidades/presencia, estimación, calendario, cuentas,
confianza, cuotas/pools/vías y exclusiones físicas. APPLIED inesperado o UNKNOWN
posterior a autorización impiden el nuevo CLAIM.

El laboratorio usa tick explícito de continuación; no hay daemon. El coordinador
histórico conserva su admisión conservadora y no autoautoriza continuaciones. Los
nuevos hechos de checkpoint/autorización quedan en outbox para una integración
operativa posterior; no se afirma que exista ya un consumidor D6 de esos eventos.

## Receptor y verificación independientes

El cierre devuelve un manifiesto completo, firmado por una clave Ed25519 exclusiva
del receptor. Se deriva del diario justo en su secuencia de cierre y conserva el
mismo resultado tras respuesta perdida, reinicio e incluso efectos de la generación
sucesora. No recalcula ausencia histórica a partir de efectos posteriores. El
verificador conserva el sobre firmado original dentro de su prueba.

El verificador consulta y comprueba firma/identidad del receptor, manifiesto completo,
hashes de efectos, bytes/salidas PARTIAL o SUFFIX y observación del host firmada,
ligada a identidad/campaña y de menos de 20 s. La primera prueba exige step-1 APPLIED
y step-2 ABSENT después del cierre; no crea ACCEPTANCE_PASS. La segunda exige ambos
APPLIED, consume solo el sufijo y registra aceptación del segundo intento antes de
VERIFY. El grant nuevo solo autoriza step-2; callback y grant anteriores quedan
fenced. El worker no recibe SQL ni claves de firma.

V21 contiene los entrypoints mínimos del laboratorio y su auditoría. Verificador y
control plane tienen LOGIN separados: solo el primero ingresa pruebas/aceptación;
solo el segundo hace commit/autorización y verifica a través de D3. Driver tiene
solo auditoría SQL y APIs de escenario. Las consultas de permisos comprueban
prohibiciones para ambas entradas nuevas de evidencia, además de las I4.

## Reproducir y leer la evidencia

Con la misma caché/imágenes locales de I4, desde la raíz:

```bash
D4_OFFLINE=1 D4_TESTS=CheckpointStoreTest bash testing/D4/run-delivery-tests.sh
bash testing/D4/run-checkpoint-lab.sh
```

El segundo comando construye offline y ejecuta S01–S05 en proyectos Compose distintos.
S05 congela intención, ejecuta el prefijo, verifica parada/cierre, liquida 4, reinicia
receptor/worker, autoriza, publica, hace TOP_UP 10 y ejecuta solo el sufijo. Comprueba
reserva única, dos intentos, generación nueva, consumo total 10 y aceptación final.
Reutiliza aislamiento y limpieza selectiva de I4.

[Resultados I5](../validation/D4-I5-results.json) separan pruebas D4, S01–S05,
regresión D3/D2 en copia y los targets de cada grupo. No se presentan las pruebas
históricas D3 como si hubieran corrido sobre V21. La prueba de upgrade nueva sí
comprueba V18→V21 con una lease activa y journal/intentos intactos.

## Límites

Solo fixtures confiables, sin proveedor real ni verificación de Git. El caso de
respuesta perdida del cierre se prueba como componente; la campaña Compose prueba
reinicio conservando diario. Corrupción/pérdida conserva cobertura de I3 y bloquea
la nueva prueba; no se transforma UNKNOWN en ABSENT.

El caso SQL de vencimiento entre prueba y commit fuerza la lease a vencida para
validar rollback; S03/S04 conservan la expiración real PostgreSQL. La matriz amplia
de la revisión I5 no queda acreditada entera por esta fixture: siguen pendientes
campañas Compose específicas de todos los negativos, varios checkpoints/cuentas,
preempción de un proceso largo mientras alcanza su cursor y recuperación parcial
desde RECONCILING. Reintentos de respuestas del verificador pueden requerir revisión;
ninguna incertidumbre autoriza liberar compromiso o continuar automáticamente.

No se promueven migraciones, despliegan servicios ni cierra D4 con estos resultados.
