# D4 I10.1 — ausencia sin progreso y reintento explícito

Fecha: 2026-10-20. A20 aprobada; incremento sintético validado con límites. D4 abierto.
A21/A22 también están aprobadas: sus revisiones y cuarentena siguen pendientes de
integración y validación. El borrador `testing/D4/sql/review-core.sql` no forma parte
de ninguna migración ni bootstrap; no constituye una barrera física implementada.

## Contrato implementado

V27 propuesta conserva V1–V26. Añade `absence_seals`, `absence_authorizations` y
`absence_links` append-only, un sobre `d4.absence.proof.v1` y entrada de verificador
separada de los checkpoints de progreso. La prueba mantiene las guardas I9 de
identidad exacta, lease expirada retenida, contexto/política, conjunto completo de
recibos CAS, mismo receptor anclado al grant, parada independiente, cierre durable,
cuentas físicas y liquidación verificable. Exige cero pasos APPLIED nuevos y
presupuesto de intentos disponible; un APPLIED histórico de la generación actual
no puede convertirse en ABSENT. El prefijo probado de otro intento se conserva.

El commit recalcula la evaluación, libera solamente compromiso pendiente y pasa
RECONCILING→RETRY_PENDING. No registra CONSUME, no crea un checkpoint de progreso,
no emite PASS y retira la lease solo después de la prueba de parada/cierre. El
intento conserva su identidad y queda FAILED, conforme al modelo de retry D2.
BLOCKED_APPROVAL pasa primero por RECONCILING, sin liberar durante ese retorno.

La autorización expresa pasa a READY con versión nueva. Captura, publicación y
CLAIM incluyen los sellos/autorizaciones/enlaces. El adaptador `AbsencePlanningStore`
admite el tipo capturado `SEALED_ABSENCE`; se conserva el adaptador anterior y su
generador. CLAIM conserva operación, reserva, mapping y vector original, aplica
TOP_UP D2 y crea un intento/generación nuevo, enlazado al sello utilizado una sola
vez. Un déficit de una cuenta impide el incremento completo. No se toma cuota
INCIDENT o UNCERTAINTY para cubrir PLANNED.

La cadena v2 permite atravesar únicamente intentos intermedios con ausencia
sellada y enlace de autorización, hasta su checkpoint padre real o el primer
intento. No transforma un número arbitrario de intento en procedencia válida.
El calculador independiente aditivo `AbsenceCheckpointAccounting` valida cada
enlace fuente/destino (identidad completa, generación y contador) obtenido de
sellos/autorizaciones/CLAIM durables por el verificador. Conserva el calculador
I8 original; una lista de enlaces vacía mantiene la continuidad consecutiva.
No se presenta un intento de ausencia como checkpoint de progreso.
El checkpoint v1 posterior consulta hechos todavía no resueltos; los hechos de
la ausencia anterior permanecen en el diario y se explican por su resolución.

## HTTPS y supervisor

- `/lab/absence/settle`, en el verificador: el driver aporta exclusivamente IDs.
  Obtiene observación host firmada fresca, artefactos acotados y cierre firmado del
  receptor. Consulta durable de replay evita repetir la liquidación.
- `/lab/absence/commit`, en control plane: solo principal verificador mTLS.
- `/lab/absence/authorize`, en control plane: decisión expresa del driver con
  sello, versión y motivo. No arranca ni rearma ningún worker.
- La retirada explícita se realiza antes de autorizar READY y comprueba estado
  RETRY_PENDING, procedencia
  de ausencia vigente, ausencia de lease/compromiso y salida local del supervisor.
  No basta el estado SQL para declarar parada; se conserva el chequeo local EXITED.

S20/S21 congelan antes de CLAIM un fallo sintético que omite efectos solo en la
primera generación. El proceso real produce sus artefactos normales; el receptor
real del laboratorio acredita la ausencia. La generación siguiente ejecuta los
pasos pendientes; no se fabrican recibos del proceso ni consumo de reinicio.
Esta fixture conserva el coste de reinicio cero autorizado por A14.

## Validación y reproducción

`bash testing/D4/run-absence-lab.sh` construye offline la imagen y ejecuta S20
(v2, dos cuentas), S21 (v1), S16 y S19 (regresión I9), en proyectos Compose
sucesivos, internos y desechables. Los grupos SQL usan PostgreSQL separado y no
sustituyen esta campaña de procesos/HTTPS. La [evidencia propia](../validation/D4-I10-ABSENCE-results.json) registra 201
pruebas D4 (26 nuevas, 175 de regresión) y 25 verificadores locales, sin fallos,
errores u omisiones. Los grupos históricos conservan sus targets; los nuevos
stores validan V27, incluidos upgrades con ejecución/reconciliación retenida.
Compose pasa S20/S21/S16/S19 con 60/44/39/26 comprobaciones (169 en total).
Los cuatro proyectos quedaron sin contenedores, redes ni volúmenes propios, con
recomprobación posterior en `work/d4/d4-absence-20261020T122405-1718906/cleanup-rechecked.json`.
V1–V26 y los informes anteriores se conservan byte a byte, al igual que 35 fuentes
existentes de scheduler/control/runtime y los tres generadores anteriores.
Las suites D2/D3 no se reejecutan aquí ni se suman al total; su evidencia anterior
sigue separada. Los pilotos fallidos y sus correcciones quedan registrados fuera
del recuento positivo, sin sobrescribir I9.

## Pendientes de I10

1. A21: cabeza de revisión append-only sobre ancla histórica, CAS completo,
   resultados/costes canónicos idénticos, cero apuntes contables; invalidación de
   autorizaciones previas y nueva autorización explícita cuando corresponda.
2. A22: caso separado que conserva CANCELLED/COMPLETED y PASS históricos, pero
   suspende su aceptación efectiva y bloquea recursos, tareas, claves físicas y
   consumidores HARD/MOCKABLE reales en captura/publicación/CLAIM/verificación.
3. Contención de ejecutores ya afectados: negar renovación/nuevos grants, cerrar
   durablemente el canal de efectos y comprobar parada host independiente. El
   grant anterior puede seguir siendo válido hasta su vencimiento/cierre; un flag
   SQL no prueba contención. No fabricar leases ni quitar reservas de otro actor.
4. Revisar y probar el cierre explícito del caso solo con revisión vigente y todas
   las barreras verificadas. Cerrar el caso no autoriza continuación ni rearme.
5. Campaña Compose de recibo tardío después de liquidar/COMPLETED, conservación
   de PASS/consumo, consumidor bloqueado y ejecutor físico afectado, con negativos
   para hash/diario incompatible y hechos nuevos durante la revisión.

Estas decisiones no necesitan consultarse de nuevo: A21/A22 ya están aprobadas.
Ni este incremento ni una campaña verde autorizan cerrar D4, promover migraciones,
utilizar proveedores reales o desplegar fuera del laboratorio desechable.

Estado posterior: [I11](D4-I11-REVIEW-QUARANTINE-LAB.md) implementa A21/A22 con
evidencia separada. La lista anterior conserva lo que quedaba pendiente en I10.1.
