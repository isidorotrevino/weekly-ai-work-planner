# D4 I7 — polling ordinario y retirada de ejecuciones

Estado: polling normal [implementado](D4-I7-POLLING-LAB.md) y
[validado](../validation/D4-I7-results.json); opción A aprobada expresamente el 2026-10-20 (A12).
**D4 abierto**. No introduce
transiciones D2/D3 ni autoriza despliegue, migraciones o cierre.

El bucle se activa explícitamente una vez en el laboratorio, con presupuesto de
tiempo y operaciones. Repite POLL con backoff acotado cuando no hay trabajo. Cada
comando conserva su ID y contenido en sus reintentos; un resultado de transporte
incierto pausa el bucle. No se interpreta un timeout de POLL como ausencia de CLAIM.
ACK, START, grant, supervisor, callback y verificador mantienen los contratos I1–I6.

El callback confirmado deja el worker esperando la aceptación independiente. Para
retirar la ejecución local se exige: estado remoto COMPLETED ligado a delivery,
intento, worker, recurso y generación; evidencia aceptada con receptor cerrado y
proceso parado; ausencia de lease; y evento local EXITED con hashes intactos.
Se archiva el estado antes de volver a IDLE. No basta con que la asignación actual
sea null. No se libera cuota desde el worker. Una consulta autenticada de solo
lectura comprueba ownership; no expone SQL, evidencia ni comandos de verificación.

Reiniciar con historia local mantiene RECOVERY_REQUIRED y no respawnea. El bucle
no se rearma automáticamente. Se conserva la autorización explícita de continuidad
de A08, el TOP_UP original, mapping, contador, cuentas físicas y fencing.

## Decisión sobre checkpoint durante el bucle

**A, elegida por el usuario (A12):** CHECKPOINT_READY pausa todo el bucle. El driver
debe verificar/sellar, autorizar la continuación si procede y rearmar explícitamente.
UNKNOWN, contradicción y callback incierto siempre pausan. Es la extensión mínima
del comportamiento I5/I6, con un punto de intervención visible.

**B, descartada para este corte:** tras comprobar un checkpoint sellado, el worker vuelve automáticamente a
polling y puede recibir otro trabajo mientras la operación original espera la
autorización explícita. No autoriza continuar esa operación. Requiere además una
retirada local específica de checkpoint y probar competencia con trabajo nuevo.

## Validación del corte normal

- Dos operaciones SUCCESS del mismo worker, una por vez, con verificación externa
  entre ellas y planificación explícita de la segunda. Misma cuenta física y pools.
- Callback confirmado sin aceptación no permite pasar a la operación siguiente.
- POLL vacío, reintentos de lectura, arranque duplicado y presupuesto finito.
- Reinicio con historia no inicia polling ni respawnea; callback incierto pausa.
  A12 exige además pausa tras checkpoint y rearme explícito; se valida por separado en S13.
- Upgrade V22→V23 de lectura de estado sin alterar lease, intentos ni journal;
  ownership, mínimo privilegio y rechazo de evidencia incompleta.

No se añade un daemon de planificación: los ticks siguen siendo explícitos.
Generalización de cuentas/checkpoints y verificadores Git/rollback siguen pendientes.

La campaña [S13 / A12](../validation/D4-I7-A12-results.json) pasó 51
comprobaciones, con 30 pruebas D4 y 332 de regresión histórica separadas.
La elección A12 queda validada en este alcance sintético; D4 sigue abierto.
