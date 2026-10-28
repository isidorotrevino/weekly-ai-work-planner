# I103 — DF44 y DR37: envolventes de eventos acotadas

Fecha: 2026-10-28, Europe/Madrid. Revisión documental por «continúa».
**DF44≤1.474 y DR37≤1.549 eventos**, bajo el límite2048/test, con las
condiciones de fuente indicadas. Cero ejecución de pruebas, helpers o campañas.
No se cambia implementación, perfil, cuota ni autoridad.

[Bloques, anclas y vectores](../validation/D5-I103-budget-test-event-bounds.json) ·
[Registro acumulado](../validation/D5-I103-event-bound-coverage.json).

## DF44: ramas por categoría, sin omitir continue

| Bloque | Cota de eventos |
|---|---:|
| Dos presupuestos iniciales de comandos/historia |38|
| Perfiles |12|
| SOURCE_BUDGET sobre clon |84|
| Seis categorías con subTest |516|
| Tres límites de valores/forma |249|
| Seis reconcile y uno rechazado |172|
| Dos búsquedas de límite de bytes |200|
| Dos rechazos de dispatch |200|
| Lifecycle raíz |3|
| Total |1474|

Cada categoría del bloque de6 aporta≤86. tickets hace Remote.execute, oráculo
remoto y self.error de reductor; continue sale del with subTest y conserva su
resultado. Las otras5 hacen self.error y state/assert. Los reductores directos
no generan eventos de observers, pero mantienen sus cálculos, valores y excepción.

El bloque SOURCE_BUDGET incluye los2 state evaluados: al copiar src y dentro de
los argumentos de self.error. El contexto esperado no vuelve gratuitos sus argumentos.
Las llamadas reconcile/dispatch que se espera rechazar se sobreestiman con sus
contratos completos de12/13 eventos más2 de contexto. No se presupone un rechazo
temprano para reducir la cota.

## DR37: las13 claves eligen una rama cada una

| Bloque | Cota de eventos |
|---|---:|
| Cuatro búsquedas de límite CLOCK |400|
| Once claves ordinarias,≤71 cada una |781|
| remote_tasks |99|
| tickets |86|
| Dos rechazos de dispatch |172|
| Capture sobredimensionado |8|
| Lifecycle raíz |3|
| Total |1549|

En remote_tasks, ids procede de prepare con2 TASKs: hay2 proyecciones y por
tanto2 dispatch. El cambio de bounds se hace en s=deepcopy(state); no cambia
el lab ni ids.projections. Se cuentan también los2 oráculos de esa rama. En
tickets hay1 dispatch y2 oráculos, incluido el state evaluado dentro de self.error.
Las otras11 ramas tienen1 contexto esperado y0 eventos de sus reductores/planner
directos, según el cierre de fuente I100. No hay subTest en DR37.

## Búsquedas CLOCK finitas y envolventes conservadoras

range(1,20) tiene19 elementos. Cada intento tiene before oracle y perform:
≤5 eventos. La ruta que termina PASS sale por un único except/break que añade
after oracle y2 aserciones:≤3. Con2 Store construidos por lab:

`E_config≤19×5+3+2=100`.

No se deduce en qué intento se alcanza la cuota. Si se agotan todos sin rechazo,
self.fail impide PASS y esa ruta no queda certificada aquí. Los límites de
producto probados son datos del fixture; el techo de eventos no se usa como
cota circular de demanda. Cero lecturas/operaciones de recursos ajenos.

La descomposición por clases de evento coincide con la cuenta por bloques. Sus
vectores son envolventes componente a componente, no conteos exactos ni trazas:
un dispatch rechazado puede recorrer sólo un prefijo. No se derivan refs de
esos máximos ni se aplican7 cargos de éxito a un comando fallido.

## Refinamiento de self.error y composición

Con las ramas literales resueltas, DF44 y DR37 invocan self.error16 veces cada
uno en su ruta completa de PASS. I99 daba cotas mayores25 y133 al sumar ramas
alternativas. Esas sobreestimaciones siguen siendo válidas y sus artefactos/sellos
se conservan byte a byte; esto es un refinamiento, no una nueva ejecución.

El registro reúne12 de88 raíces T/R con cotas completas de eventos: subtotal
superior13755. Esas raíces son disjuntas; no sumar ese subtotal a21203 de partes
globales I100, porque se solapan. Sustituir las partes parciales de cada root
al completar su cuenta. Quedan76 T/R y los otros grupos hasta321/12.

Faltan referencias y bytes completos. I97 mantiene R≥19037>16384; ningún margen
de eventos lo resuelve. Hace falta composición conjunta de24 cuotas y Reader
antes de proponer otro contrato/perfil y sus decisiones correspondientes.

Git, cambios previos y evidencia I83–I102 preservados. P0;83/1 y UI04.1 parcial,
D1–D4 cerrados e I1–I20/A52 aceptado. D5/H07/G01–G07 y GI33/34/38/39/40
globales abiertos. Sin proveedores/credenciales/corpus reales, consumo/reservas,
activación, promoción, despliegue, publicación ni D6. No se deduce persistencia,
recuperación integrada o fsync nativo de estas cuentas o de PASS aislados.
