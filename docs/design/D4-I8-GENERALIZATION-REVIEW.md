# D4 I8 — checkpoints, cuentas y verificadores: revisión

Fecha: 2026-10-20. **D4 abierto. Diseño en revisión.** La petición de generalizar
permite preparar el incremento y sus componentes aislados; el usuario aprobó expresamente las tres opciones A (A13–A15). Su aprobación
autoriza implementar ese alcance; no acredita integración o pruebas aún no ejecutadas. A01–A12 permanecen vigentes.

## Contratos y huecos comprobados

| Componente vigente | Límite real | Cambio necesario |
|---|---|---|
| V19 `d4.checkpoints` | UNIQUE(operation_id), un checkpoint total | Historia enlazada, cabeza vigente y consumo de cada autorización una sola vez |
| V19 prueba/commit | Manifiesto fijo step-1/step-2, consumo escalar 4 y una cuenta | Manifiesto versionado con vector completo por paso/cuenta y deltas comprobados |
| V19/V20 admisión | Una procedencia, una autorización/enlace sucesor | Cabeza exacta en snapshot, readset, CAS y despacho; rechazar padre antiguo/ramificación |
| V21 aceptación y `CheckpointVerifier` | Sufijo step-2, prefijo en generación anterior inmediata | Composición de todos los prefijos, generación real de cada efecto y cierre por intento |
| Worker/fixture | PARTIAL/SUFFIX con salidas canónicas constantes | Cursor ligado al manifiesto, ejecución exclusiva de pasos aún no aplicados |
| Receptor | Clave lógica estable, recibos por generación, cierre firmado | Mantener; el paso no cambia de clave por pasar a un intento nuevo |
| `LabVerifier` | Comprueba stdout de SUCCESS y efecto sintético | Verificación independiente de bytes, objetos Git y estado restaurado |
| D2/D3 | Reservas, TOP_UP, límites y fencing aprobados | Reutilizar; sin cambiar V1–V23 ni rejuvenecer intentos |

## Decisión 1: forma del primer incremento

**A, aprobada (A13):** secuencia lineal congelada de hasta 32 pasos y 8 cuentas físicas
vinculantes. Checkpoints forman una cadena sin ramas. Campaña inicial: tres pasos,
dos cuentas de dimensiones distintas, dos checkpoints y tres intentos en la misma
operación/reserva. Dos checkpoints no amplían el límite D2: cada continuación consume
un intento; el máximo efectivo también depende de max_attempts vigente. Sin saltos,
paralelismo intratarea ni grafo de ejecución nuevo.

**B, descartada para este corte:** DAG de pasos y checkpoints sobre conjuntos cerrados por dependencias, con
planificación interna y posibles ramas concurrentes. Exige definir exclusión por
paso, convergencia y composición antes de liquidar. Amplía el modelo de ejecución.

En ambas opciones cada checkpoint requiere progreso APPLIED nuevo, parada probada,
cierre de todos sus canales, ausencia de UNKNOWN/contradicción, RUNNING y lease viva
al commit. Los APPLIED heredados se referencian en su generación original; ABSENT
se interpreta solo en el cierre/generación que lo acredita. No se transforma un
ABSENT antiguo en un hecho global ni se borra historia para permitir APPLIED posterior.

## Decisión 2: procedencia de consumo multidimensional

**A, aprobada (A14) para el proveedor sintético:** intención congelada antes de CLAIM
con costes exactos por paso y cuenta (unidades decimales, dimensión y ventana
explícitas). El verificador obtiene APPLIED del receptor; calcula el vector acumulado
por unión de pasos verificados, nunca sumando de nuevo un prefijo heredado. El delta
es acumulado menos journal asentado por cuenta. Rechazar cuentas faltantes/extra,
negativos, contradicciones y discrepancia con el mapping. No sumar dimensiones.
Los costes de reinicio son cero explícito en esta fixture; no se generaliza esa
suposición a un proveedor real.

**B, descartada para este corte:** además medir consumo variable de cada intento, incluidos reinicios y fallos,
mediante un contador sintético independiente y durable. Requiere watermark de
liquidación por intento/cuenta y separar coste de intento del resultado lógico
idempotente de un paso. Amplía pruebas de pérdida y duplicación de telemetría.

TOP_UP sigue siendo el vector original completo por cuenta, no el residual. COMMIT
liquida deltas y libera remanentes de todas las cuentas en una única transacción;
un déficit o una cuenta vencida bloquea el conjunto. Reparto 70/20/10, cuentas,
ventanas, mapping, pool y reserva entre planes se conservan. Ninguna aprobación
cambia esas guardas ni permite rollover, ADJUST corrector o nuevas operaciones.

## Decisión 3: qué acredita rollback

**A, aprobada (A15):** verificador de artefactos y Git en repositorio sintético aislado,
propiedad del verificador; comprueba objetos/ancestría y árbol completo esperado.
Rollback acredita únicamente que una copia de archivos local vuelve al manifiesto
anterior, comprobado por observación independiente con proceso detenido. No revierte
efectos APPLIED ni consumo ni crea ABSENT. No ejecuta hooks, filtros, red ni scripts
del candidato. En el primer corte no incluye submódulos, symlinks ni Git LFS.

**B, descartada para este corte:** incluir también compensación de efectos externos sintéticos. Necesita una
intención de compensación, nueva clave de efecto y evidencia de su resultado; los
recibos APPLIED originales y su consumo siguen existiendo. Requiere revisar por
separado cómo afecta a aceptación y reconciliación; no resuelve A04 automáticamente.

## Diseño aditivo aprobado para concretar

Propuesta V24 separada, solo en migrations-d4-proposed y configurada expresamente en
el harness. Tablas nuevas/versionadas para manifiesto, cabeza/cadena, prueba por
paso/cuenta y enlaces; conservar la fixture v1 y su evidencia. La ruta v2 no debe
admitir una operación ya arrancada sin intención v2 congelada. Misma orden de locks
742001→742002 y ninguna llamada de red/proceso dentro de la transacción. Los comandos
mantienen idempotencia por ID/contenido y los resultados verificados son append-only.

Cada prueba enlaza operación, intento, worker, recurso, generación, contexto,
política, manifiesto, padre, conjunto aplicado, cierres y hashes de artefactos.
La cabeza y journal deben coincidir al commit. Solo la cabeza cancelada y todavía
no consumida admite autorización explícita; cada sucesor enlaza una sola vez.
Cada CHECKPOINT_READY pausa todo el bucle (A12). Sellar, autorizar o planificar no
lo rearman. El siguiente CLAIM hace TOP_UP y valida dependencias/prioridad heredada,
catálogo/presencia, estimaciones y calendario como D3, sin atajos de admisión.

Antes de SQL se preparan verificadores locales puros: manifiesto completo de bytes
y una copia de Git sintética, sin autoridad para registrar ACCEPTANCE_PASS ni para
mutar el control plane. Sus pruebas unitarias no son evidencia de integración Compose.
El origen firmado, frescura, identidad, parada y cierre se seguirán verificando en
la frontera existente; un hash o árbol correcto por sí solo no acredita aceptación.

## Campaña propuesta, todavía no ejecutada

- Tres pasos, dos cuentas, prefijos crecientes y dos checkpoints; un solo PASS final,
  misma operación/reserva, tres intentos y tres generaciones D2.
- Deltas por cuenta, cero doble consumo y TOP_UP original completo en cada continuación.
- Padre antiguo, autorización usada, ausencia de progreso y límite de intentos rechazados.
- Cuenta omitida/extra, coste alterado, déficit/vencimiento de una cuenta: rollback íntegro.
- Recibo faltante, UNKNOWN/contradicción o cierre/parada inválidos: bloqueo conservado.
- Artefacto alterado/omitido/extra, árbol Git o base equivocados, symlink/submódulo,
  rollback incompleto y efecto previo APPLIED todavía visible tras restaurar archivos.
- Upgrade con ejecución v1 viva, preservación del journal y regresión histórica separada.

Esta lista es un criterio de aceptación, no una afirmación de pruebas ejecutadas.
Sin proveedores/credenciales reales, promoción, despliegue ni cierre de D4.

El [primer corte I8.1](D4-I8-COMPONENTS.md) ya implementa y prueba componentes
independientes. La campaña Compose y la ampliación SQL descritas arriba siguen
pendientes: no se acreditan por esas pruebas locales.

Integración posterior: [I8.2](D4-I8-INTEGRATION.md) implementa el puente SQL/HTTPS
y la campaña Compose acotada. Los límites y resultados anteriores de I8.1 son históricos.
