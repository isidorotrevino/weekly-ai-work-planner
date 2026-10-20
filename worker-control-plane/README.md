# D4 — adaptador HTTPS sintético

Java 21/Spring Boot 4.1.1; versión fijada tras consultar sus
[requisitos oficiales](https://docs.spring.io/spring-boot/system-requirements.html).
El módulo implementa transporte de laboratorio sobre V16/V17 propuestas, sin
modificar contratos D1/D2/D3 ni aplicar migraciones al arrancar.

## Entrada de worker

| Ruta | Contrato |
|---|---|
| POST `/d4/v1/commands` | Sobre `d4.worker.v1` con command_id, correlation_id y request. POLL, ACK, START, HEARTBEAT, CALLBACK o PRESENCE |
| GET `/d4/v1/commands/{id}` | Recibo propio persistido; una identidad ajena o comando inexistente se rechaza |
| GET `/d4/v1/assignments/current` | Estado propio y vencimiento actuales; nunca un grant de efectos |

Ejemplo de forma, con identificadores ficticios:

```json
{
  "schema_version": "d4.worker.v1",
  "command_id": "00000000-0000-4000-8000-000000000001",
  "correlation_id": "00000000-0000-4000-8000-000000000002",
  "request": {"action": "POLL"}
}
```

POLL no admite selectores de plan/operación/worker enviados por el cliente: el
servidor recupera la entrega vigente o elige una asignación debida del head D3.
Un poll vacío queda como recibo vacío: el siguiente poll es un comando nuevo.
Reintentar una petición cuyo resultado se desconoce conserva ID y sobre completos.
Cambiar incluso correlation_id con el mismo command_id produce conflicto.

ACK usa `delivery_id`. START/HEARTBEAT usan ese vínculo, sin payload de identidad.
CALLBACK solo admite `payload.entries` conforme D2. PRESENCE actualiza únicamente
el heartbeat observado; no pone ONLINE ni añade capacidades. No hay autoalta,
VERIFY, ingesta de evidencia, preempción, continuidad ni grants de efectos en esta API.

## Identidad y límites

HTTPS directo con certificado cliente obligatorio, CA sintética y SAN URI exacto
`urn:weekly-ai-planner:worker:<uuid>`. Un fichero local autorizado enlaza fingerprint
SHA-256 de certificado a UUID. Se comprueban pin, SAN, validez y uso clientAuth en
cada petición; sustituir atómicamente el fichero revoca el pin para las siguientes
peticiones, incluidas conexiones TLS ya abiertas. No se promete cancelar una
petición que ya había sido admitida. No se confía en CN, worker_id del cuerpo ni
cabeceras reenviadas. Registro ilegible → 503 y bloqueo conservador.

El arranque exige SSL habilitado, client-auth=need y forward-headers-strategy=none.
Sin keystore/truststore/configuración explícitos no arranca. Las variables D4_*
obligatorias están en `src/main/resources/application.properties`; las pruebas
las generan sin reutilizar secretos o certificados reales.

Límite de sobre 64 KiB y profundidad 32; claves JSON duplicadas rechazadas. SQL
usa parámetros y una conexión autocommit READ COMMITTED por llamada; sin red o
procesos bajo locks. Se acotan conexión/socket, sentencia y espera de lock. Los
errores HTTP no devuelven texto SQL ni credenciales. 409 indica conflicto/guarda;
503/500 indican consultar o repetir el mismo comando, no reejecutar un efecto.

El LOGIN runtime de prueba solo tiene USAGE d4 y EXECUTE en transport,
read_transport_command y current_assignment. Se prueba una conexión LOGIN real,
sin DML/tablas ni acceso directo a d2.execution/d3.dispatch/d4.deliver. El propietario
migrador se mantiene en el harness, fuera del camino de la aplicación.

## Validación disponible

Desde la raíz:

```bash
# Bootstrap público de dependencias y después pruebas offline en red interna:
bash testing/D4/run-transport-tests.sh
# Con imágenes y caché ya preparadas:
D4_OFFLINE=1 bash testing/D4/run-transport-tests.sh
```

Los scripts usan PostgreSQL desechable y servidor/clientes TLS dentro del contenedor
Maven, sin puertos publicados al host. El runtime Java usa un LOGIN restringido;
el harness de pruebas conserva un dueño para preparar/auditar fixtures. No se
demuestra separación de procesos/hosts entre ambos con esta batería.

[I2, resultados y límites](../docs/design/D4-I2-HTTPS.md). El JAR ejecutable se
genera durante bootstrap; no se distribuye ni despliega por estos comandos. El
reactor raíz histórico queda intacto: el runner añade este módulo solo a su copia
local de fuentes. Supervisor, receptor, verificador y Compose siguen pendientes.
