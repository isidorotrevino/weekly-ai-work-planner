# D4 — revisión final del alcance sintético

**Decisión posterior, 2026-10-20: cierre sintético aprobado expresamente.**
[Documento vigente](D4-approved.md) · [Manifiesto](../validation/D4-CLOSURE.json).
El texto de revisión siguiente conserva su estado anterior a esa aprobación.

Fecha: 2026-10-20. **D4 abierto; este documento prepara la decisión del usuario.**
No es un manifiesto de cierre ni autoriza promoción o despliegue.

La revisión reúne los contratos A01–A24 con la implementación I1–I12. Los informes
anteriores conservan el alcance y estado de su fecha. La [evidencia I12](../validation/D4-I12-INTEGRATED-results.json) registra **638 pruebas
positivas y 1.085 comprobaciones en 30 escenarios Compose sobre V30**, sin fallos
ni omisiones en los resultados finales. Los 30 proyectos y los 14 proyectos de
pilotos se comprobaron sin contenedores, redes ni volúmenes restantes. Las
correcciones de pilotos se excluyen de los totales positivos y se identifica
exactamente la imagen, fuentes y harness.

## Tabla de aceptación

| Tema del alcance D4 | Contrato revisable | Evidencia actual validada |
|---|---|---|
| Transporte e identidad | mTLS, catálogo autorizado, entrega/ACK separados de START y grant; replay ligado a cuerpo e identidad | S01/S02, HttpsTransportTest, DeliveryStoreTest |
| Presencia durable | Incarnación autorizada, CAS y secuencia exacta, reloj SQL; reemplazo sin adoptar entrega ni liberar | PresenceStoreTest, S28/S30 |
| Cuentas y reservas | Cuentas físicas, 70/20/10, reserva estable entre planes, dimensiones separadas y TOP_UP original | S02/S14/S15/S20, LatestResetTest y contabilidad |
| Dependencias y prioridad | HARD/MOCKABLE reales, SOFT/OPTIONAL, SemVer y prioridad heredada por camino bloqueante | S02, LatestReviewTest, regresión D2/D3 |
| Supervisor y fencing | Proceso/grupo exactos, watchdog, primer fallo de renovación, no rollover y ninguna parada deducida de timeout | S04/S06/S07/S08/S09, LatestResetTest |
| Evidencias y restauración | Artefactos/Git dentro de Java independiente, manifiesto congelado y parada fresca; restauración solo local | S26/S27, TreeVerifierTest, TreeStoreTest |
| Checkpoints y continuidad | v1/v2, cadena lineal, contador D2, consumo incremental exacto, autorización y rearme explícitos | S05/S13/S14/S28, LatestBoundaryTest |
| Reconciliación | UNKNOWN y contradicciones conservadores; cierre monotónico del mismo receptor, v1/v2 y aceptación terminal separada | S03/S16/S17/S18/S19, RecoveryStoreTest |
| Ausencia sin progreso | Sello independiente, RETRY_PENDING y autorización expresa, misma operación/reserva/contador | S20/S21, AbsenceStoreTest |
| Revisiones liquidadas | Cadena append-only, resultado/costes iguales, delta cero e invalidación de autorizaciones anteriores | S22/S25, LatestReviewTest |
| Reapertura y cuarentena | Caso separado, PASS/terminal históricos conservados, suspensión transitiva, cierre durable/parada/barrera y cierre explícito | S23/S24/S29, LatestReviewTest |
| Polling y reinicios | Backoff y presupuesto acotados, pausa global tras checkpoint/incertidumbre y RECOVERY_REQUIRED tras reinicio | S10/S11/S12/S13/S28/S29 |
| Validación reproducible | Base limpia V30, upgrade vivo, matriz actual y targets históricos separados; cleanup selectivo | Campaña S01–S30, informes SQL/Compose y hashes preservados |

Todas las filas tienen evidencia positiva dentro del alcance acotado registrado.
No quedan pendientes técnicos identificados de ese alcance; permanece la decisión
expresa del usuario sobre el cierre formal. No convertir
una comprobación SQL estructural del propietario en evidencia criptográfica o de
parada kernel. Los replays antiguos son recibos históricos, nunca grants nuevos.

## Inspección de fronteras

- Las funciones nuevas revocan acceso PUBLIC y DML directo. El control plane no
  obtiene autoridad para producir pruebas; el worker no obtiene SQL ni PASS.
- La observación host firma identidad, campaña y parada; el receptor firma el cierre
  ligado al diario y generación. El verificador obtiene hechos y archivos por
  separado, sin aceptar booleanos del driver como procedencia.
- Los mutex siguen D3→D2; no se ejecuta Git, procesos ni HTTP mientras se retienen
  locks SQL. Presencia, requisitos/pruebas y hechos de revisión entran en el readset.
- Los nuevos requisitos se congelan antes del primer CLAIM. Las migraciones no
  transforman historia ni crean leases, pruebas de parada o vínculos de incarnación
  para intentos heredados.
- El ingreso factual, la aceptación, la liquidación, la resolución de revisión y
  el rearme conservan autoridades distintas. Ninguno borra APPLIED ni consumo.

## Límites explícitos del cierre propuesto

La unidad de aceptación es el laboratorio acotado con fixtures confiables y
proveedor/receptor sintéticos. No es operación de producción ni aislamiento de
código hostil. Los hashes SHA-1 son identificadores Git de fixture; el contenido se
comprueba con SHA-256. Se construyen objetos en repositorios del verificador, sin
importar Git arbitrario de un worker. La restauración acredita el árbol esperado,
no una compensación de efectos externos.

Hashes incompatibles, APPLIED revocado, costes variables, diario perdido, varios
receptores o ejecución heredada sin transporte concluyente conservan bloqueo.
No se declara resolución universal ni exactly-once para servicios externos.

Conectores/cuotas/proveedores reales pertenecen a D5. Máquinas físicas, operación,
secretos productivos, retención y despliegue pertenecen a D6. No son trabajo
silenciosamente aprobado por una campaña verde de D4.

La matriz y la revisión técnica están completas para el alcance descrito. El
usuario puede aprobar su cierre o pedir cambios concretos. Hasta esa aprobación
D4 permanece abierto.
