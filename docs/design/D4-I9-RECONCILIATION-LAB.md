# D4 I9 — reconciliación concluyente y recuperación v1/v2

Fecha: 2026-10-20. **D4 abierto; V26 propuesta, sin promoción ni despliegue externo.**
[A17–A19](D4-DECISIONS.md) aprueban resolución monotónica del mismo receptor,
continuidad sellada y alcance v1 más recuperación completamente APPLIED.
La [revisión](D4-I9-RECONCILIATION-REVIEW.md) conserva las alternativas consultadas.
Esta ruta amplía A04/A09 solo para evidencia concluyente verificada; los entrypoints
RUNNING de V19/V24/V25 mantienen su frontera original de lease viva.

## Hechos y autoridad

V26 añade observaciones, pruebas y liquidaciones append-only. Un recibo anterior
UNKNOWN o ABSENT no se borra ni se cambia por APPLIED. La resolución referencia
el contenido completo, ordenado por ID, de los recibos de su generación. Otro
recibo posterior invalida su vigencia y vuelve a bloquear las guardas de admisión
o aceptación. No se selecciona únicamente el subconjunto favorable.

El verificador consulta por mTLS el receptor sintético y conserva observaciones
con ID del diario, paso, hash y generación. Para resolver, comprueba la observación
host firmada y fresca, la parada del grupo y los bytes stdout/stderr; consulta
un cierre firmado completo, serializado con aplicación, del mismo receptor/diario
ligado al grant SQL anterior. La pérdida/cambio de diario no acredita ausencia.
El worker y el driver no pueden ingresar pruebas o recibos mediante SQL.

Se exige intención congelada, contexto y política idénticos, identidad D2 exacta,
lease retenida y expirada, y estado RECONCILING o BLOCKED_APPROVAL. Solo se admiten
APPLIED con el hash esperado y ABSENT de canal cerrado, formando prefijo y sufijo
lineales. Un APPLIED anterior no puede convertirse en ABSENT; hashes históricos
incompatibles y UNKNOWN en el cierre siguen bloqueando. Los recibos antiguos sin
payload almacenado no ganan un hash retrospectivo: la resolución acredita el hash
canónico del receptor, conservando el recibo original sin enriquecerlo.

## Liquidación y ciclo de vida

El SQL recalcula costes congelados por cuenta y los contrasta con el journal. Si
CALLBACK ya liquidó el coste exacto, el delta es cero; si no llegó, consume solo la
diferencia probada. Un estado contable intermedio sin procedencia reconocida bloquea.
Libera solo el compromiso real restante. Tras esperar locks se vuelven a comprobar
las ventanas y el conjunto de recibos. El comando, liquidación, historia, checkpoint,
outbox y retirada de lease parcial se comprometen o revierten juntos.

- Parcial: RECONCILING→CANCELLED con checkpoint nativo v1/v2. Desde BLOCKED_APPROVAL
  se registra primero el retorno a RECONCILING sin liberar en esa transición; la
  liquidación sellada ocurre después, dentro de la misma transacción. No hay PASS.
  A08/A12 siguen exigiendo autorización y rearme explícitos. Replanificar y CLAIM
  conservan reserva, mapping, recurso, pool, contador e incrementan generación;
  TOP_UP vuelve al vector original completo.
- Terminal: RECONCILING→VERIFYING tras comprobar todos los pasos APPLIED y liquidar
  el delta exacto. Conserva la lease expirada y la exclusión hasta una entrada distinta
  del verificador que admite aceptación final y completa. No crea un intento nuevo. Tras aceptar, `/lab/recovery/retire` permite retirar
  explícitamente el estado local: vuelve a consultar identidad/COMPLETED, comprueba
  EXITED durable y espera a que termine el hilo del callback antes de archivar.
  No envía un callback tardío ni rearma polling. Antes de aceptación se rechaza.
  ACCEPTANCE_FAIL o dependencias de integración incompatibles impiden completar.

No hay continuación READY directa ni reapertura de la generación cerrada. Los
replays devuelven hechos persistidos sin renovar autoridad; reutilizar un ID con
otro contenido/ownership produce conflicto. La aceptación terminal es un comando
explícito del verificador sobre su prueba ya verificada, no un booleano del worker.

## Admisión y persistencia

`generate-recovery-admission.py --check` reproduce V26 desde un núcleo revisable
y copias estáticas de las guardas históricas. No se reescribe SQL durante ejecución.
Las guardas originales siguen tratando como bloqueantes todos los recibos no
cubiertos exactamente por una liquidación vigente. v1 usa sus checkpoints y
autorizaciones originales; v2 conserva cabeza, cadena y sus enlaces exclusivos.
Resoluciones/observaciones/pruebas forman parte de snapshot/readset; publicación y
CLAIM revalidan la procedencia, además de elegibilidad y todas las guardas D2/D3.
Los roles no obtienen DML libre, permisos de migrador ni acceso al alias sin guarda.

La normalización v1 solo soporta fixtures sintéticas ya definidas: PARTIAL de dos
pasos 4/6 en una cuenta, su sufijo y SUCCESS de un paso con coste calibrado. No
transforma la intención histórica en v2 ni crea otra operación. v2 conserva el
esquema cerrado A16 y los límites 32 pasos/8 cuentas, con campaña 3 pasos/2 cuentas.

## Campaña y evidencia

`bash testing/D4/run-reconciliation-lab.sh`: S16 (v2, UNKNOWN→APPLIED del mismo diario,
checkpoint tras vencimiento y continuación), S17 (v1 parcial y luego terminal sin
callback), S18 (v2 terminal tras callback ya comprometido), S19 (SUCCESS terminal),
S15 (pruebas inválidas) y S14 (regresión de cadena normal). En S18 el bucle puede
quedar pausado al observar RECONCILING; la aceptación terminal no lo rearma. Si quedó
pausado, el driver retira explícitamente el estado completado mediante la ruta
existente y conserva la pausa. No se exige finalización automática del polling. Cada proyecto tiene
expiración real cuando corresponde, observación host, red interna y limpieza propia.
Las pruebas SQL de propietario usan evidencia sintética; no se presentan como
pruebas criptográficas o de procesos. Mantienen targets históricos y prueban upgrade.

La [evidencia final](../validation/D4-I9-RECONCILIATION-results.json) registra
318 comprobaciones Compose y 532 pruebas positivas: 175 D4 (22 nuevas de
recuperación), 175 D3, 157 D2 y 25 verificadores locales. Cero fallos, errores
u omisiones en los grupos finales. Los seis proyectos quedaron sin contenedores,
redes ni volúmenes propios, con comprobación posterior. Los informes históricos,
fuentes V1–V25 y cierres D2/D3 se verificaron sin cambios. Los pilotos fallidos
se conservan fuera del recuento positivo y se explican en el informe.

## Pendientes que este incremento no elimina

Integrar verificadores genéricos de Git/archivos/restauración con aceptación SQL/HTTPS;
registro durable de presencia de workers; campaña completa de negativos, resets y
dependencias y repetición de escenarios antiguos sobre el último target; revisión
final de aceptación y aprobación expresa de cierre D4.

Continúan fuera del corte: costes variables, múltiples receptores/canales, ramas,
compensación o invalidación externa de APPLIED, resolución tras perder el diario,
recuperación automática y fallos de alimentación. Solo hay una liquidación por operación/generación. Un hecho nuevo que contradice una
resolución ya liquidada mantiene bloqueo; no se añade una revisión que vuelva a liquidar
la misma generación; no se añade una transición de reapertura
para operaciones CANCELLED/COMPLETED. Proveedores comerciales y operación física
pertenecen a D5/D6. Los casos sin progreso (todos ABSENT), la reapertura tras hechos posteriores y
fixtures v1 distintas de las calibradas no ganan una nueva transición en I9.
No se cambia reparto 70/20/10, reservas entre planes, dependencias,
prioridad por camino bloqueante, fencing ni los cierres D1/D2/D3.
