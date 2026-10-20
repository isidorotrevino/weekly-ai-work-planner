# D4 — corrección aditiva de las fronteras de V24

Fecha: 2026-10-20. **D4 abierto; V24 intacta y V25 propuesta.**
La [revisión](D4-V24-BOUNDARY-REVIEW.md) describe los defectos reproducidos y la
elección de compatibilidad de campos adicionales. D4-A16 aprueba expresamente
el esquema v2 cerrado: se rechazan claves desconocidas en manifiesto, paso y cuenta.
Las intenciones anteriores incompatibles conservan todos sus hechos, pero no pueden
recibir nuevas admisiones. No se convierten ni se reparan silenciosamente.

## Reproducciones históricas

`V24BoundaryReproductionTest` usa exclusivamente target 24. Sus dos pruebas verdes
significan **defectos reproducidos**, no aceptación de V24: un ID JSON numérico
entró en la intención congelada y un checkpoint canceló/liberó después de vencer
la lease mientras esperaba un bloqueo de cuenta. Se conservan el source snapshot,
JUnit y logs propios, fuera del recuento de validación positiva de la corrección.

La lease corta de dos segundos se configura solo en ese test SQL sintético. El
vencimiento y la espera se observan en PostgreSQL real, sin cambiar el reloj host.
Una conexión mantiene el bloqueo de cuenta; otra alcanza efectivamente la espera;
el observador deja vencer el plazo antes de liberar el bloqueo. La prueba evita
que un timeout de SQL se confunda con la corrección de la guarda.

## V25 propuesta

`generate-v25-boundaries.py` deriva estáticamente las funciones afectadas desde V24,
con SHA-256 de origen y modo --check. No hay reescritura de SQL durante el runtime.
V1–V24 permanecen sin cambios; Flyway añade solo V25 en los clústeres desechables.

La validación pura `multi_manifest_typed` comprueba tipos de campos obligatorios,
objetos/arrays y límites antes de usar ->> o casts. El trigger conserva además todos
los controles V24 de hash, contexto, costes, mapping, ventanas y cuentas. Un ID o
hash numérico, coste textual o campo requerido ausente no se convierte silenciosamente.

También se comprueban intenciones antiguas: CLAIM e ingreso de prueba rechazan las
mal tipadas; una cabeza incompatible deja de ser elegible para autorización o
continuidad. Se conserva el manifiesto anterior sin editarlo ni crear otra operación.
`multi_inspect` sigue permitiendo observarlo y devuelve manifest_compatible=false;
la guarda SQL de lab_authorize rechaza un grant nuevo antes de HEARTBEAT, incluso
con un control plane anterior. El control plane actual añade otra comprobación.
Esa bandera informativa no concede
autoridad y no reemplaza las guardas SQL. No se invalidan hechos ya comprometidos
ni se borran recibos históricos.

La entrada multi_commit captura la expiración de la lease exacta bajo los locks
existentes y vuelve a comprobar clock_timestamp después de ejecutar la liquidación.
Si venció, la excepción revierte CONSUME, RELEASE, cancelación, retirada de lease,
checkpoint, comando, historia y outbox en conjunto. La prueba independiente ingresada
antes sigue siendo un hecho; el compromiso y la lease expirada permanecen para la
ruta de reconciliación. No se inventa ABSENT ni se retira exclusión por timeout.

La función V24 anterior queda accesible solo al propietario de migración. Los
permisos EXECUTE de servicios se trasladan a la entrada protegida, incluidos upgrades
con roles ya creados: no se deja un alias público con el que saltarse la guarda.
La repetición de un comando ya comprometido devuelve su recibo antes de volver a
consultar una lease que correctamente ya no existe. Otro contenido con el mismo ID
sigue produciendo conflicto.

La ruta HTTPS conserva autocommit y READ_COMMITTED. La nueva comprobación es la
última guarda de plazo antes del retorno de la función SQL; no constituye una
promesa de tiempo real sobre una pausa posterior de WAL, kernel o almacenamiento,
ni habilita transacciones arbitrariamente abiertas por un cliente. No se introduce
un contrato de ejecución en tiempo real ni una nueva transición de dominio.

## Validación separada y campaña

[Evidencia propia](../validation/D4-V25-CLOSED-SCHEMA-results.json), sin sobrescribir
I8.2. `V25BoundaryTest` comprueba tipos, esquema cerrado aprobado, intención antigua
conservada pero inadmisible, rollback íntegro al vencer durante la espera, replay,
traslado de permisos y upgrade desde un checkpoint V24 sellado, completando la
misma operación con su reserva e intentos originales.

`bash testing/D4/run-v24-boundary-lab.sh` ejecuta S15/S14/S13 sobre target 25.
S15 es nuevo: altera la observación firmada antes del ingreso y corrompe el stdout
observado, rechazando ambas pruebas nuevas. Comprueba cero pruebas/checkpoints/PASS,
ambos compromisos íntegros y ausencia todavía UNKNOWN en el canal no cerrado.
Tras restaurar los artefactos y obtener observación válida, el mismo comando puede
sellar el prefijo: consumo (4,1), sin aceptación final ni rearme automático.

S14 repite los dos checkpoints y tres intentos multicuentas; S13 conserva la pausa
y continuidad v1. Los workers siguen sin SQL, socket Docker ni autoaceptación.
Las reproducciones SQL no son pruebas Compose; las negativas de S15 no se cuentan
como resolución de UNKNOWN/contradicciones. El proveedor continúa siendo sintético.

Resultado final: 181 comprobaciones Compose (S15: 35, S14: 95, S13: 51) y
510 pruebas positivas (153 D4, 175 D3, 157 D2 y 25 verificadores locales),
sin fallos ni omisiones. Las dos reproducciones V24 se excluyen de esos recuentos.
Los tres proyectos quedaron sin contenedores, redes ni volúmenes propios.
Se verificaron los hashes de informes históricos, fuentes V1–V24 y cierres D2/D3.

## Pendientes conservados

La elección A16 queda aplicada; no añade nuevas transiciones de dominio.
No se incorpora Git importado desde workers, compensación de efectos, múltiples
receptores, costes variables, recuperación automática o RECONCILING para checkpoints.
Las reservas entre planes, reparto 70/20/10, TOP_UP original, dependencias,
prioridad por camino bloqueante y fencing no se cambian. Sin promoción, despliegue
fuera del laboratorio ni cierre de D4.
