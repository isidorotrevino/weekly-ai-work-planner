# D4 — continuación con efectos parciales, propuesta para revisión

Fecha: 2026-10-19. Estado vigente: contrato A/A aprobado para el laboratorio;
[implementación I5 acotada](D4-I5-CHECKPOINT-LAB.md). El resto de este documento
conserva el diseño general; no acredita que todas sus variantes estén implementadas.
El usuario eligió continuidad con efectos parciales y grant acotado con cierre
durable. Esas decisiones iniciales ampliaron el diseño a preparar; A08/A09 posteriores
aprobaron el contrato acotado. No resuelven las contradicciones excluidas por D4-A04.

La [revisión concreta I5](D4-I5-REVIEW.md) añade comandos, procedencia,
contabilidad, guardas en observación/Java/publicación/despacho y opciones para
decidir el ciclo de vida y la frontera de lease. Sigue sin aprobación de transición.

## Unidad de efecto y prueba necesaria

La intención de operación define antes del primer arranque un manifiesto inmutable
de pasos: ID estable, revisión/hash de entrada, orden/dependencias, efecto esperado,
clave lógica idempotente y contrato de salida. La clave es operación/revisión/paso;
intento y generación son autoridad, no claves nuevas para repetir el mismo efecto.
Cambiar contenido bajo la misma clave produce conflicto, no otra aplicación.

Por paso, el receptor conserva transacción de deduplicación, aplicación y recibo.
Un checkpoint lista resultados APPLIED y pasos restantes, referencias de artefacto
con hash, consumo observado por cuenta y cursor de formato/versionado. La lista
del worker es candidata; el verificador consulta cada paso directamente y compara
el conjunto completo con la intención, no solo los recibos que el worker seleccione.

Todos los canales de efecto de esa generación deben quedar cerrados de forma
durable antes de concluir ausencia de pasos pendientes. Un cierre autentica la
identidad D2 exacta y un ID estable, serializa con aplicación dentro del receptor
y devuelve su secuencia final y manifiesto completo. Repetirlo devuelve el mismo
resultado; reinicio del receptor no reabre la generación. La parada del grupo de
procesos se prueba por canal independiente del payload del worker. Perder el
diario o no poder observar algún paso produce UNKNOWN y conserva exclusión.

El grant expira como máximo con la lease D2 observada; solo el control plane
autenticado puede instalar/renovar el grant, después de confirmación SQL. Lleva
operación/intento/worker/recurso/generación, intención y vencimiento. Renovar no
permite reabrir una generación cerrada. Un efecto admitido inmediatamente antes
del vencimiento puede quedar APPLIED y debe reconciliarse; no se promete transacción
distribuida. Sin grant comprobable, no aplicar. El reloj de prueba tiene skew
acotado declarado; si no es confiable, el receptor bloquea conservadoramente.

## Secuencia propuesta, separada de la cancelación ordinaria

1. Solicitud de preempción idempotente sobre operación/intento/generación vigente.
   No interrumpible devuelve DEFERRED_NONINTERRUPTIBLE y conserva compromiso.
2. Alcanzar checkpoint de fixture confiable, detener grupo, cerrar receptor y
   verificar artefactos/pasos/consumo por vía independiente. No liberar por timeout.
3. Persistir una prueba compuesta inmutable que referencia toda evidencia, hashes
   del contexto/política/manifiesto y secuencia final del receptor. Rechazar cualquier
   UNKNOWN, APPLIED no esperado, contradicción o falta de prueba de parada.
4. Entrada D4 nueva, bajo orden 742001→742002 y versión esperada, liquida consumo
   parcial comprobado mediante CONSUME y libera solo compromiso remanente. Cambio
   de estado/cancelación por checkpoint, contabilidad, historia, prueba y outbox
   quedan en un único commit. No llamar primero a `d2.preempt` V9: libera pendiente
   sin incorporar esta liquidación parcial y no implementa este contrato compuesto.
5. Una autorización explícita de continuación puede proponer CANCELLED→READY solo
   si la cancelación provino de ese checkpoint verificado. Conserva operación,
   reserva, vector de cuentas, recurso, pool, vía, intentos y consumo acumulado.
   No habilitar cancelación genérica ni convertir aprobación humana en evidencia.
6. La nueva publicación y entrada D4 de despacho para continuación validan plan,
   capacidades, dependencias, aprobación, ventana original y prueba compuesta.
   Crean un nuevo intento/generación D2 y enlazan el checkpoint. Reejecutar solo
   sufijo pendiente; los pasos APPLIED previos se consumen como resultados
   verificados, nunca se vuelven a facturar ni se convierten en ABSENT.

El entrypoint V13 actual rechaza retry cuando existen APPLIED/UNKNOWN en la
generación anterior. Se necesita una ruta aditiva específica y revisión de sus
guardas compartidas; no falsificar un recibo ABSENT ni llamar a D2 CLAIM omitiendo
las guardas D3. V16 de entrega durable **no habilita** esta ruta. No se cambia
V1–V15 ni se incorpora a la auditoría histórica D2.

Los límites D2 siguen aplicando: tres intentos totales por defecto/máximo veinte;
nuevo intento consume ese límite, aunque el checkpoint sea correcto. Una cuenta
vencida, capacidad desconocida, déficit o dependencia incompatible bloquean la
continuación. No hay rollover ni nueva operación para rejuvenecer el contador.

## Decisión contable A07

Ejemplo: vector congelado estima 10 unidades en una cuenta PLANNED; primer intento
consume 4 y checkpoint libera 6 pendientes. Quedan resultados parciales probados
y una estimación residual de 6, que no puede sobrescribir el mapping congelado.

| Opción | Nueva reserva de compromiso | Consecuencia |
|---|---|---|
| A propuesta conservadora | TOP_UP hasta las 10 unidades del vector original | Reutiliza la semántica contable actual; puede bloquear aunque haya 6 disponibles. El consumo real del segundo intento se registra solo una vez y el remanente se liquida conforme a las guardas aprobadas |
| B residual por checkpoint | TOP_UP de 6 sobre estimación residual inmutable enlazada a la prueba | Mayor aprovechamiento, pero cambia la guarda de TOP_UP/dispatch y exige demostrar que el residual incluye todas las cuentas vinculantes, costes de reinicio y confianza/vigencia. El vector original se conserva como hecho, no se edita |

El usuario eligió **A: TOP_UP conservador al vector original**. La tabla conserva
la alternativa consultada; B no se implementa. En ambas opciones, 4 consumidas siguen consumidas y las cuentas conservan 70/20/10.
No puede elegirse una cifra residual del cuerpo del worker. Elegir B autoriza
diseñar/revisar esa ampliación; requiere validación específica antes de habilitarla.

## Pruebas exigidas antes de implementar/habilitar

Fixture de dos pasos con primero APPLIED: perder respuesta del cierre, reiniciar
receptor y supervisor, conservar cierre y deduplicación, verificar parada real,
liquidación parcial sin doble CONSUME, nueva generación y ejecución exclusiva del
segundo paso. Repetir todos los comandos con mismo ID y cambiar contenido para
comprobar conflicto/rollback. El grant anterior nunca recupera autoridad.

Negativos: checkpoint truncado, paso extra/omitido, consumo sin procedencia,
callback tardío, límite de intentos, cuenta vencida, aprobación/contexto distintos,
UNKNOWN o contradicción en cualquier paso, receptor sin diario y continuación de
cancelación ordinaria. Todo conserva bloqueo/compromisos según su estado. No se
cuentan estas pruebas como ejecutadas por existir en este documento.
