# Entorno local de desarrollo — validación independiente

Fecha: 2026-10-21, Europe/Madrid. Base Git:
`ac729b07c04ee3dc76545ce13ff94a277766a70c`.
Esta evidencia corresponde únicamente al entorno de desarrollo. Los cierres y
resultados D1–D4 se conservan; no se repite ni se atribuye aquí su matriz histórica.

## Configuración y decisiones

- El usuario eligió persistencia mediante bind mounts bajo `run_data/`, rebuild
  manual y HTTPS loopback configurable en `.env`.
- Al comprobar que Docker no publicaba puertos de las redes internas, se presentó
  el diseño concreto y el usuario aprobó un proxy TCP sin claves, SQL ni socket
  Docker. Conserva mTLS extremo a extremo y el aislamiento de los workers.
- Compose propio: [compose.dev.yaml](../../compose.dev.yaml). Ciclo de vida:
  [dev.py](../../dev/dev.py), [build](../../dev/build.sh),
  [proxy](../../dev/tcp-proxy.py). [Guía ejecutable](../DEVELOPMENT.md).
- No se alteraron SQL, contratos, ejecutables sellados D4 ni manifiestos de cierre.
  Sin proveedores/credenciales reales, promoción, despliegue, publicación Git ni
  inicio implícito de D5/D6.

## Entorno observado

Linux; Docker Engine 29.9.1, Compose 5.6.0, Python host 3.14.4, Bash 5.3.9,
OpenSSL 3.5.5. Java 21/Maven se ejecutaron dentro de Docker. PostgreSQL 16.15.
El primer build partió de una caché Maven de desarrollo nueva y descargó las
dependencias; no utilizó `work/d4/m2`. Las imágenes base están fijadas en el código:

| Imagen | Digest SHA-256 |
|---|---|
| Maven/Java | `99e61abcff91a9b1333463bd8451fb18495d6eba9250ac66a338b518f8278320` |
| PostgreSQL | `0ea6700a3b4f0ae6ce746519073558aed4d88a79d8d07622a9a644946c7319c4` |
| Python del proxy | `a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1` |

## Resultados

La campaña principal terminó con **22 controles de ciclo de vida satisfactorios**.
Los controles no equivalen a 22 pruebas JUnit ni a una nueva aceptación D4.

| Flujo comprobado | Resultado |
|---|---|
| `config`, primer `build`, `up` desde datos nuevos | Build Docker/Maven; bootstrap sintético V30 una sola vez; servicios sanos |
| HTTPS host en los cinco puertos | Acceso con CA/cliente válidos; rechazo sin certificado cliente; bindings solo 127.0.0.1 |
| Inspección de contenedores | Sin privilegios ni socket Docker; aplicaciones de solo lectura y capabilities retiradas |
| Primer `smoke` | Proceso real de fixture, observación host firmada y aceptación del verificador independiente |
| Smoke repetido | Mismo intento/reserva/efecto, consumo ocho y una aceptación; sin segunda ejecución |
| Aislamiento de workers | Sin acceso SQL ni conexión a Internet en el smoke final |
| `restart` | Servicios recuperados, nueva presencia y worker RECOVERY_REQUIRED; sin adopción automática |
| `stop` → `up` → `smoke` | Intentos, reservas, efectos, diario y aceptación idénticos antes/después |
| Cambio y `rebuild --service control-plane` | Comentario temporal en un recurso llegó a la imagen y al contenedor; smoke satisfactorio; bytes originales restaurados |
| `reset --instance local` con otra instancia activa | Contenedores/identidad/datos de `neighbor` intactos; datos seleccionados vacíos; logs/caché retenidos |
| `up` y `smoke` tras reset | Fixture e identidades nuevas, bootstrap limpio y nueva operación aceptada |
| Preservación histórica | 266 archivos de fuentes/diseños/SQL/evidencias comparados sin cambios; 242 entradas de hashes de los manifiestos D3/D4 verificadas |

El smoke actual contiene **16 comprobaciones al ejecutar y aceptar la primera
operación, y 14 al comprobar una aceptación existente**. No se suman como pruebas
únicas entre ejecuciones. El primer piloto interno tenía 14 comprobaciones en su
primera operación, antes de añadir la prueba de salida a Internet de cada worker.

Una validación suplementaria confirmó `status`, logs por servicio, `rebuild`
completo con el build final, smoke posterior, rechazo de adopción automática y
retirada terminal explícita mediante la ruta HTTPS documentada. La retirada
devuelve `ready: true` y pasa de RECOVERY_REQUIRED a IDLE; el smoke posterior
conserva el mismo intento/efecto/consumo. Logs en `work/dev-env/full-rebuild.log`,
`explicit-retirement.json` y `retirement-smoke.log`. La instancia `local` queda
**detenida con sus datos conservados**; se retoma con `python3 dev/dev.py up`.

Evidencia bruta local, excluida de Git: `work/dev-env/validate.py`, `result.json`
y logs separados por comando; snapshots, entradas SHA-256, reportes smoke y
metadatos de imagen en `run_data/builds/` y `run_data/local/logs/`. Las claves y
configuraciones sintéticas permanecen exclusivamente en las rutas locales privadas.
La instancia vecina se limpió por su nombre; no se ejecutaron borrados globales.

## Alcance y reproducción

Sigue los comandos de la [guía](../DEVELOPMENT.md), usando datos sintéticos nuevos.
Para repetir la prueba de selección, arranca una segunda instancia con otro nombre
y cinco puertos libres, conserva su identidad y sus IDs de contenedor, resetea
únicamente la primera y verifica que la segunda conserva esos IDs y sus datos.

El smoke repetido comprueba un resultado existente; no demuestra por sí solo una
nueva ejecución después del restart. Una sesión incierta exige los protocolos de
recuperación aprobados. Las identidades caducan a las 48 horas y este corte requiere
reset explícito tras su caducidad. No hay renovación automática, watch, UI de
producto, soporte Windows/macOS ni garantía de arranque offline. No se ejecutan
regresiones SQL completas porque no se modifican sus contratos ni componentes.

Comprobaciones finales: configuración Compose válida, sintaxis Python/Bash,
117 enlaces locales resueltos, coherencia de comandos y estado entre README inglés
y español, `python3 scripts/check-publication.py` y `git diff --check` satisfactorios.
