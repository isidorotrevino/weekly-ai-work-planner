# D4 I4 — integración del laboratorio sintético

Estado: cuatro escenarios completos superados (117 comprobaciones), 50 pruebas
D4 y 157 de regresión D2 sin fallos; implementación para revisión; **D4 abierto**. Conserva D1/D2/D3 y sus
fuentes de cierre. V18 es una propuesta exclusiva del harness D4. No introduce
continuidad, promueve migraciones ni configura un despliegue.

## Camino funcional

`testing/D4/lab/` conecta el controlador HTTPS existente y las bibliotecas de
supervisor/receptor. El worker hace POLL → ACK → START por mTLS. El control plane
obtiene la identidad de la entrega y renueva mediante HEARTBEAT D2/D3 antes de
firmar un grant Ed25519 acotado a la lease real. El grant liga receptor, operación,
intento, worker, recurso, generación, contexto, política y pasos autorizados.
El receptor valida ese grant y registra el efecto lógico por operación/intención/paso.
El supervisor abre un proceso de fixture en un grupo Linux propio, conserva su
identidad y recoge salidas limitadas y sus hashes antes de CALLBACK.

El callback informa consumo; no acredita aceptación. Un verificador separado
contrasta los bytes del contexto, la salida esperada del fixture, hashes del diario,
consumo y consulta HTTPS directa al receptor. El host observa `/proc` mediante una
sonda fija dentro del namespace del worker y firma los hechos con Ed25519: identidad
D2, campaña, contenedor, boot ID, PID/grupo/start ticks, miembros y hora. El verificador
rechaza firmas, identidad o campaña distintas y observaciones de más de 20 s.
La clave de observación se queda en el host; el worker no puede firmar evidencia.

Antes de permitir una aceptación se exige parada observada y respuesta durable de
cierre del receptor. El proof conserva hash de observación, stdout/stderr y recibo,
secuencia de cierre y contexto. El LOGIN del verificador es el único que ingresa
estos hechos por `d4.lab_record_evidence`; solicita VERIFY/recuperación al control
plane, que delega en `d3.execution`. Ni driver ni control plane pueden ingresar
ACCEPTANCE_PASS. Un recibo APPLIED prueba solo el efecto sintético.

## V18 y confianza

La propuesta añade intenciones de fixture, recibos de autorización y evidencias
inmutables, inspección acotada y auditoría de solo lectura. No cambia V1–V17.
La prueba de upgrade conserva una lease activa, intento, reserva y journal de V17;
la instalación limpia se ejecuta en cada proyecto Compose. El permiso SQL es por
función y LOGIN sintético, con autocommit/READ_COMMITTED y timeouts. No se ejecuta
ningún proceso bajo mutex SQL. UNKNOWN previo impide aceptar después un APPLIED;
este laboratorio no implementa resolución de evidencia contradictoria.

El inicializador propietario crea fixtures, catálogo autorizado y roles efímeros.
La CA dura dos días, cada servicio tiene su propio PKCS12 y registro por huella y
SAN URI. Los roles de laboratorio añaden SAN `principal:<rol>:<uuid>`; las rutas
`/d4/` admiten solo SAN de worker. El filtro conserva compatibilidad con el registro
UUID de I2. No se confía en cabeceras de proxy y el arranque exige mTLS directo.
La clave de firma de grants solo se monta en el control plane. Los workers no
reciben SQL, claves de firma, claves ajenas ni socket Docker.

## Compose y reproducción

Desde la raíz, con Docker/Compose, Python 3 y OpenSSL:

```bash
bash testing/D4/run-lab.sh
```

El build usa Maven offline con `work/d4/m2`, imágenes locales fijadas por digest y
`--network none`. La caché de I2/I3 debe estar preparada; una dependencia ausente
falla, sin descarga implícita. Spring Boot conserva las versiones fijadas en I2.
La imagen contiene clases/JARs y las siete ubicaciones SQL explícitas; ningún secreto.
El JAR de runtime se carga sin anidamiento para que el subproceso encuentre el fixture.

Cada escenario genera un proyecto, DB y tres volúmenes de estado nuevos. No publica
puertos. Persistencia, workers y efectos son redes internas distintas. Aplicaciones:
UID/GID del usuario, rootfs de solo lectura, capabilities vacías,
no-new-privileges, 1 CPU, 384 MiB, 128 PIDs y tmpfs 64 MiB. Excepciones: PostgreSQL
necesita su inicialización habitual y volumen de datos; `migrate` usa root con grupo
del usuario y únicamente CHOWN para inicializar esos tres volúmenes. Termina antes
de los servicios. Build y herramientas del host quedan fuera de la prueba de
runtime. No se monta el repositorio ni el home en las aplicaciones.

El inicializador crea una sola vez diario del receptor y supervisor. Los servicios
solo abren datos existentes: no reconstruyen en blanco un historial perdido. El UUID
del receptor queda fijado para la campaña. Reiniciar conservando datos y perderlos
son casos distintos. Las pruebas I3 conservan la cobertura de corrupción/pérdida;
la campaña Compose prueba reinicios conservando volúmenes.

El host guarda configuración privada, PKI, observaciones, logs, auditoría, estado
exportado y resultados en `work/d4/<campaña>/`. El runner ejecuta `down -v` solo
sobre cada proyecto propio después de recoger evidencia y verifica que no queden
sus contenedores. Las imágenes de build quedan disponibles localmente. Un fallo de
infraestructura o aserción detiene la campaña y no acredita el escenario.

## Los cuatro escenarios

| Caso | Acción real | Aserciones principales |
|---|---|---|
| S01 | SUCCESS, efecto, callback, verificador y VERIFY | Una reserva/intento/efecto, consumo 8/10, replay del mismo callback, contenido cambiado rechazado, cierre del receptor, prohibición de autoaceptación |
| S02 | Polls rivales, dos workers, replanificación con A activo y B independiente | Misma entrega y reserva, ownership, CARRIED en sucesor, pools físicos 70/20/10, P4 bloqueante hereda 8, HARD sin evidencia bloqueado, P4 ajeno excluido, workspace compartido diferido |
| S03 | Efecto aplicado, corte de red antes de CALLBACK, reconexión y reinicios | Callback no confirmado ni persistido, receptor conserva APPLIED, worker no respawnea, EXPIRE/RECONCILE/RECOVERY_VERIFY tras 60 s reales, consumo una sola vez |
| S04 | Fixture sin watchdog sobrevive a lease de 60 s | Grupo vivo tras expiración, grant caducado rechazado, UNKNOWN bloquea con reserva/exclusión, parada posterior y cierre durable sin resolver automáticamente UNKNOWN, callback tardío rechazado |

S02/S04 inyectan deliberadamente la ausencia de watchdog con el fixture SURVIVOR;
no son el diseño de un worker general. PRESENCE no renueva la lease de ejecución.
S03/S04 esperan el reloj real PostgreSQL, sin adelantar relojes ni editar la lease.
El driver manipula exclusivamente los contenedores/red de su proyecto desde el host.

## Límites y siguientes revisiones

Es un laboratorio de fixtures confiables, no aislamiento para código hostil ni un
verificador de Git/proveedores reales. Las claves viven solo durante la campaña;
rotación operativa, disponibilidad, retención y provisión real son D6. La semántica
de grant admite un efecto autorizado justo antes de su vencimiento: la seguridad
de liberar exclusión depende de parada más cierre serializado, nunca solo del reloj.
El reinicio del worker exige recuperación y no repite automáticamente el spawn.
Los fallos/timeout de respuestas del verificador pueden requerir revisión y mantienen
compromiso; no se ofrece recuperación automática ilimitada de todas las fases.

[Continuidad parcial](D4-CHECKPOINT-CONTINUATION.md), resolución concluyente,
campaña extensa de reset/dependencias y proveedores siguen fuera de este corte.
Ningún resultado verde cierra D4 ni aprueba la transición propuesta de checkpoint.
Los [resultados I4](../validation/D4-I4-results.json) deben leerse separando Compose,
pruebas de componentes, upgrade y regresión histórica D2.
