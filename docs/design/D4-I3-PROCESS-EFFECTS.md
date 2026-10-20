# D4 I3 — supervisor y receptor sintético, componentes

Fecha: 2026-10-19. **Implementado y validado a nivel de componentes; D4 abierto.**
Continuación autorizada por el usuario. Reutiliza A02 (fixtures supervisadas),
A06 (grant acotado/cierre) y conserva A04 (contradicciones bloqueadas). A05/A07
siguen definiendo el diseño de continuidad parcial, sin habilitar su transición.

## Implementación

[worker-runtime](../../worker-runtime/README.md) añade identidad D2 inmutable,
supervisor Linux de fixtures y receptor con diario durable. No se modifica SQL
V1–V17 ni los módulos scheduler existentes.

El supervisor registra intención antes del spawn, identidad de proceso/grupo y
observación final con logs acotados, truncado y hashes. Bloquea duplicación del
intento y otra ejecución en workspace ocupado o con historia incierta. TERM/KILL
y desaparición del grupo son hechos observados, no consecuencias de un timeout
HTTP o una lease expirada. El supervisor no acredita por sí mismo aceptación o
prueba independiente de parada para liberar compromisos SQL.

El receptor comprueba firma de control plane y grant completo antes de aplicar
un paso permitido. Deduplica por efecto lógico entre intentos; misma clave con
contenido distinto produce conflicto. Un cierre firmado impide nuevos efectos
de la generación y persiste al reabrir el diario. UNKNOWN ante pérdida/corrupción
y nueva identidad de almacén evitan recrear una ausencia o aceptar tokens antiguos.
El hash chain/head detecta incoherencia de ficheros; no es un log resistente a un
administrador malicioso con acceso al filesystem.

## Evidencia separada

[Resultados I3](../validation/D4-I3-results.json): **18 pruebas de componentes**,
sin fallos, errores ni omisiones. Algunas usan procesos Linux reales; otras son
fixtures dirigidas de corrupción/recuperación de diario y firma/tiempo.

| Grupo dentro de las 18 | Casos |
|---|---|
| Receptor | Reapertura y replay sin otro efecto; ausencia solo tras cierre; APPLIED conservado entre generaciones; firma/identidad falsas; command ID de cierre; corrupción/truncado/pérdida; epoch de almacén; expiración con reloj real; 16 aplicaciones concurrentes; cobertura de lease/60 s; pasos no autorizados |
| Supervisor | Éxito y no respawn; timeout y exclusión; logs con límite/drenaje; hueco sintético START_INTENT; fixture resistente a TERM; descendiente recogido; logs alterados que vuelven incierta la recuperación |

No sumar las 16 aplicaciones concurrentes como 16 tests adicionales. La prueba
de expiración real usa un grant corto de componente y reloj JVM: **no demuestra
expiración de lease PostgreSQL de 60 s**. El hueco de spawn se prepara en disco;
no es un kill del contenedor entre las dos instrucciones del supervisor.

Se repite la regresión histórica D2 por la ampliación del harness; su resultado
pertenece a V1–V11 y queda separado. I1/I2 conservan sus informes y alcance propios;
las pruebas HTTPS de I2 no se presentan como repetidas dentro de la campaña I3.

## Integración que falta

El supervisor todavía no obtiene START por HTTPS, el control plane no firma grants
desde una lectura de lease D2 y el receptor no tiene transporte propio. No hay un
verificador separado que contraste proceso/artefactos/receptor y aporte aceptación
al control plane. Las claves de firma de las pruebas son sintéticas en su JVM;
la separación de secretos entre servicios aún debe construirse/probarse.

Los componentes no llaman a d2.preempt, no fabrican ACCEPTANCE_PASS, no crean una
reserva/intento alternativo ni cambian cuentas físicas, 70/20/10 o TOP_UP. Tampoco
acreditan dependencias HARD ni liberan exclusión SQL. El orden de pasos y la
compatibilidad del checkpoint pertenecen al contrato de continuidad pendiente;
el receptor actual solo limita el conjunto de pasos autorizados por el grant.

Siguiente corte: conectar estos componentes con el adaptador I2 y un verificador
independiente; construir Compose con redes/roles/volúmenes y ejecutar D4-S01–S04,
incluidos reinicios de servicios y vencimiento real de lease. Mientras tanto esos
escenarios siguen pendientes y no se declara lista la vertical Docker.

No hay proveedor real, promoción de migraciones, despliegue ni cierre de D4.
