# D4 I8.2 — integración multicuentas y checkpoints lineales

Fecha: 2026-10-20. A13–A15 siguen aprobadas; **D4 abierto**. Implementación sintética
sobre V24 propuesta; sin promoción ni despliegue. El informe propio
[de integración](../validation/D4-I8-INTEGRATION-results.json) delimita las pruebas
finales, separado del [primer corte de componentes](D4-I8-COMPONENTS.md).
Resultado final: S14/S05/S13, 186 comprobaciones; 137 pruebas D4, 175 D3,
157 D2 y 25 verificadores locales, sin fallos, errores ni omisiones. Los tres
proyectos quedaron sin contenedores, redes ni volúmenes propios.

## Frontera y conservación de v1

V24 vive solo en migrations-d4-proposed y el bootstrap Compose apunta expresamente
a 24. V1–V23 no cambian. Manifiesto, pruebas, checkpoints, autorizaciones y enlaces
v2 tienen tablas propias append-only. La cabeza es una vista del último checkpoint;
la unicidad por operación/generación y por operación/padre impide raíces duplicadas
y ramas. Cada autorización y cada enlace sucesor se consumen una sola vez.

La intención se congela antes del primer CLAIM y liga bytes de contexto, recursos,
pool, cuentas físicas, dimensión, unidad y ventanas. Hasta 32 pasos y 8 cuentas,
con vector completo por paso, IDs únicos y costes exactos no negativos. La suma
por cuenta no supera el vector original. La integración limita a cuatro decimales
para coincidir exactamente con numeric(18,4) del journal D2: rechaza más precisión
en vez de redondear. La segunda cuenta de la campaña usa TOKENS, una unidad del
catálogo D2; no se añade REQUESTS ni se altera el dominio cerrado.

## Transacción y admisión

El verificador obtiene parada firmada por el observador externo, artefactos leídos
independientemente y cierre firmado del receptor. Comprueba identidad, contexto,
política, manifiesto, conjunto completo del sufijo y cada APPLIED heredado contra
el receptor. Los prefijos conservan la generación original. Reutiliza el cálculo
CheckpointAccounting y compara el journal real. El callback final ya ha liquidado
su delta: se calcula el resultado esperado desde el padre y se contrasta con consumo
acumulado y compromiso cero, sin volver a facturarlo.

SQL recalcula todos los costes desde la intención congelada y los recibos verificados;
no acepta un escalar o un delta declarado por el worker. Bajo 742001→742002 revalida
RUNNING/lease viva, versión, identidad, ausencia de UNKNOWN/contradicción, cabeza,
procedencia, mapping y journal completos. CONSUME por cuenta, RELEASE remanente,
CANCELLED, retirada de lease, checkpoint e historia/outbox hacen un único commit.
Un fallo conserva toda la transacción sin prefijos contables aplicados.

La autorización explícita exige la cabeza CANCELLED exacta, sin uso anterior,
contexto/política vigentes, journal igual al prefijo sellado y presupuesto de intentos.
No crea reserva ni intento. Una corrección legítima del journal que cambie ese
prefijo invalida la autorización; no se usa ADJUST para ocultar divergencias.

La observación y el adaptador D4 de planificación admiten la nueva cabeza por la
vista tipada existente. Las relaciones v2 se incluyen en snapshot y CAS. El despacho
contrasta su readset desde el primer CLAIM: añadir una intención después de capturar
el plan exige recapturar. Una prueba nueva después de publicar también invalida
el CLAIM. Se conservan todas las guardas D3, incluidas cuentas, dependencias, prioridad
por camino bloqueante, estimaciones, calendario, presencia y capacidades.
El mapping del manifiesto debe coincidir con la estimación y pool del plan desde
el primer intento. TOP_UP conserva el vector original completo; no es residual.

## HTTPS, ejecución y replays

Las entradas de laboratorio nuevas son /lab/multi/request, /commit, /authorize,
/verify, /finish y /finalize. No son APIs de SQL remoto. Se mantienen mTLS, roles,
catálogo y ownership del transporte. Driver solicita/autoriza; solo el verificador
restringido ingresa prueba/PASS y llama commit/finalize. Los cuerpos exigen campos
exactos y versiones enteras positivas representables sin truncamiento.

Cada grant contiene únicamente el sufijo todavía no aplicado. La fixture ejecuta
un paso por intento en S14 y el callback final liquida un vector por cuenta.
Cada CHECKPOINT_READY pausa todo el bucle; sellado, autorización y planificación
no lo rearman. El driver retira el estado local y emite un start nuevo bajo A12.
Los grants y callbacks de generaciones anteriores siguen fenced.

Un replay HTTP de verificación encuentra primero la prueba persistida y conserva
la versión original del request. Un replay final encuentra la aceptación ya ingresada.
No vuelve a sellar ni exige recrear la observación de una prueba ya aceptada. Antes
de ingreso nuevo sí se exige la observación independiente fresca. Identidad de
delivery/request y contenido de comando siguen comprobados; un ID ajeno se rechaza.

La retirada automática final reutiliza V23: COMPLETED exacto, PASS sin FAIL, ninguna
lease/compromiso ni UNKNOWN/contradicción, prueba ligada y EXITED local íntegro.
Los checkpoints intermedios no son PASS y se archivan por la ruta explícita.

## Campaña Compose y pruebas separadas

`bash testing/D4/run-multicount-lab.sh` construye offline por digest y ejecuta tres
proyectos separados: S14 nuevo y regresiones v1 S05/S13. Redes internas, sin puertos,
sin SQL/socket Docker en workers, credenciales efímeras exclusivamente sintéticas.
El runner recoge evidencia antes del cleanup selectivo de cada proyecto.

| Intento | Cuenta A OPERATIONS | Cuenta B TOKENS | Resultado |
|---|---:|---:|---|
| 1 | 4 | 1 | Checkpoint 1, libera remanente y exige autorización/rearme |
| 2 | 3 | 2 | Checkpoint 2, misma reserva y nuevo rearme explícito |
| 3 | 3 | 3 | Callback vectorial y aceptación independiente final |
| Total consumido | 10 | 6 | Una operación/reserva, tres intentos y generaciones |
| Compromisos positivos acumulados | 30 | 18 | Tres compromisos del vector original (10,6) |

S14 comprueba reinicio del receptor con prefijo conservado, replays de request,
commit, autorización y verificación HTTP, pausa A12, rechazo de checkpoint antiguo,
grant/callback antiguos y un solo PASS final. Para demostrar el replay persistido
altera temporalmente la observación disponible después del ingreso y repite el
mismo comando: reutiliza la prueba anterior; restaura el archivo para la evidencia.
No implica que una observación inválida pueda ingresar una prueba nueva.

Las pruebas SQL aparte cubren upgrade V23→V24 con ejecución v1 viva, rollback de ambas
cuentas ante expiración/lease ausente, UNKNOWN, prueba incompleta/padre incorrecto,
inmutabilidad, roles, límite de intentos, déficit de una cuenta, corrección del
journal y carreras de snapshot/publicación/CLAIM. No se llaman Compose ni pruebas
de firma: ese harness usa pruebas sintéticas ingresadas por su propietario.
La regresión histórica D3/D2 se ejecuta en copia con sus targets originales.

## Límites restantes

- Campaña de tres pasos, dos cuentas, dos checkpoints y tres intentos, con un receptor.
  No acredita todos los tamaños hasta 32/8 ni múltiples canales o ramas.
- Solo costes exactos congelados y coste de reinicio cero de fixture. Sin medición
  variable por intento, cuentas reales, rollover o cambios de TOP_UP.
- COMMIT solo RUNNING con lease viva. UNKNOWN/contradicciones conservan bloqueo;
  no se amplía A04/A09 ni hay continuidad desde RECONCILING.
- Los verificadores Python de Git/restauración siguen siendo componentes locales;
  no se añade importación de objetos del worker ni un puente genérico de PASS Git.
- No hay daemon de planificación, recuperación automática tras reinicio ni pruebas
  de corte de alimentación. Los ticks y rearmes siguen explícitos.

Los informes anteriores describen sus ejecuciones originales y no se sobrescriben.
D4 continúa abierto para revisión y requiere aprobación expresa para cerrarlo.
