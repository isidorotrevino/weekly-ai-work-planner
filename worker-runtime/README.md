# D4 — componentes sintéticos de proceso y efectos

Java 21, sin dependencias externas de producción. Son bibliotecas para el
laboratorio, **no un worker distribuido conectado todavía a D2/HTTPS**.

## Supervisor

`FixtureSupervisor` lanza únicamente fixtures enumeradas mediante `setsid`, sin
shell ni comandos arbitrarios. Limpia el entorno del subproceso; no le transmite
credenciales SQL, claves de firma o variables del harness. Persiste START_INTENT
antes de spawn y RUNNING antes de abrir la compuerta de la fixture. Una operación
por workspace mediante lock de fichero; el mismo intento no vuelve a lanzarse.

Observa boot ID, PID, grupo y ticks de inicio de Linux. Un timeout solicita TERM,
después KILL si sigue vivo, espera y comprueba desaparición del grupo. No confunde
un PID reutilizado o un diario incompleto con un proceso detenido. Una recuperación
incierta bloquea otro arranque. No adopta ni mata automáticamente procesos desde
un diario recuperado: solo observa, sin reconstruir una autorización SQL.

Recoge stdout/stderr mientras drena toda la salida, conserva hasta 64 KiB por
stream y marca truncado. Fuerza logs y eventos locales a disco, registra hashes
y los contrasta al recuperar EXITED. Son observaciones candidatas del supervisor,
no evidencia independiente ACCEPTANCE_PASS ni prueba SQL de checkpoint.

Las fixtures confiables cubren éxito, espera, salida abundante, resistencia a TERM
y un descendiente que el padre recoge. No se acredita un sandbox para código hostil,
descendientes que escapan del grupo o contenedores privilegiados. La exclusión
distribuida sigue siendo D2/D3; este lock local no la sustituye.

## Receptor de efectos

`EffectJournal` representa un efecto sintético mediante un evento durable de su
propio diario; no escribe en una API/proveedor externo. Valida grants Ed25519 de
una clave del control plane, nunca un entero enviado por el worker como autoridad.
El grant liga identidad D2 completa, hashes de intención/contexto/política, pasos
permitidos, identidad del almacén y vencimiento ≤ lease declarada y ≤60 s.
La biblioteca no consulta PostgreSQL: los tests construyen grants sintéticos.
El futuro adaptador deberá emitirlos solo desde autorización D2 vigente comprobada.

La clave lógica es operación/intención/paso, independiente de intento/generación.
La aplicación, deduplicación y recibo comparten un evento serializado bajo lock y
fsync. Igual clave y distinto contenido se rechaza; generación obsoleta, grant
caducado o paso no autorizado no aplica efectos. La renovación conserva el binding;
no reabre una generación cerrada. Una generación nueva necesita cierre previo.

El cierre requiere firma distinta de dominio de la del grant y command ID estable;
serializa con aplicación y conserva su secuencia final al reabrir el diario. Un
recibo APPLIED se conserva entre intentos. Ausencia de un paso solo es concluyente
para la generación/intención autorizadas que siguen cerradas; antes es UNKNOWN.
Una generación posterior vuelve incierta la ausencia que ya no cubre su autoridad.

Cada frame tiene cadena SHA-256 y hay un head durable separado. Archivo perdido,
truncado o incoherente produce UNKNOWN y bloquea nuevas escrituras; no se repara
ni trunca automáticamente. Un almacén nuevo tiene otro UUID y rechaza grants
dirigidos al anterior. Ese UUID identifica el destino del diario: **no sustituye
ni incrementa el fencing D2**. La capa de control tampoco podrá firmar otro grant
para ocultar pérdida de evidencia de una ejecución anterior.

Límites de fixture: 16 pasos autorizados, payload de 64 KiB, diario inferior a
2.000 eventos. No son cuotas de proveedor. El filesystem y la clave del receptor
son de confianza: no se ofrece resistencia a un atacante con control de esos
ficheros. No hay garantía exactly-once para terceros.

## Comprobaciones

```bash
D4_OFFLINE=1 bash testing/D4/run-process-tests.sh
```

Necesita caché/imágenes preparadas por los runners D4 y herramientas Linux de la
imagen (`setsid`, `kill`, `/proc`). La ausencia de herramientas es fallo, no skip.
No se construye ni despliega un servicio permanente. El runner conserva fuentes
y resultados bajo su directorio privado `work/d4/`; las pruebas usan volúmenes de
filesystem temporal y reapertura de objetos, no reinicios de contenedores durables.

[I3: evidencia y límites](../docs/design/D4-I3-PROCESS-EFFECTS.md). La continuación
con efectos parciales sigue pendiente de revisión de contrato: estos componentes
no crean intentos D2 ni liberan reservas ni reanudan CANCELLED.
