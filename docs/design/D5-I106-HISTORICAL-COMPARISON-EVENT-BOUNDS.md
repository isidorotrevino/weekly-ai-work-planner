# I106 — comparación histórica y cardinalidad de procedencia

Fecha: 2026-10-28, Europe/Madrid. Continuación documental local de I105.
**DF46 <=256 eventos y DR36 <=560 eventos**, condicionados por las fuentes,
bindings, tipos y ruta original completa PASS con observación válida.
El registro llega a **42 de88 raíces T/R**, con46 pendientes. No se importaron
módulos del producto ni se ejecutaron APIs históricas, tests, hijos o campañas.

[Cuenta de eventos y anclas](../validation/D5-I106-historical-comparison-event-bounds.json) ·
[Tipos, imports y llamadas históricas](../validation/D5-I106-historical-facade-source-review.json) ·
[Registro acumulado](../validation/D5-I106-event-bound-coverage.json).

## Tipos históricos y llamadas transitivas

DF46 construye MemoryLab con su MemoryPlane por defecto, EligibilityLab sin
hook y ReconciliationLab sobre una PlaneFixture exacta. DR36 construye BatchLab
sin hook. Estas clases no son Store, Client, Remote o FixtureStore observados,
ni heredan sus métodos. Se revisaron por AST/fuente los cuatro módulos y sus
dependencias de parsing preview/register, incluido el import local de parse.
El inventario guarda imports y expresiones de llamada de todo el módulo como
superconjunto; no pretende ser una traza ni una prueba general de Python.

No hay imports de los observers desde esos módulos. Las llamadas indirectas
relevantes quedan explícitas: operation de MemoryLab._command es la función
anidada de apply_effect; test_hook de EligibilityLab/BatchLab y before_send /
before_query de PlaneFixture permanecen None. Los modos send_mode son cadenas.
La clase de plane se comprueba por identidad exacta. Contenedores y entradas
son builtin del fixture; no se admiten objetos con métodos/callables inyectados,
monkeypatches nuevos ni import hooks. Parsers, hashes, JSON, locks, copias y
recursión conservan trabajo y excepciones. No llegan a observers, protocolos
parentales o aserciones unittest en esos segmentos, y por ello agregan0 eventos
adicionales bajo estas precondiciones.

No se extrapola a pruebas que sí instalen hooks, a clases distintas ni a
proveedores. Esta revisión no llama a ninguna API privada histórica.

## DF46: dos bloques y observaciones

| Parte | Envolvente de eventos |
|---|---:|
| Primer lab y ready(projection=False), comparaciones y operaciones | 113 |
| Segundo lab y ready completo, reconciliación y conflicto remoto | 140 |
| Lifecycle de raíz | 3 |
| Total | 256 |

Se cuentan los5 state y1 entities, las13 aserciones explícitas, y los2 eventos
del contexto de excepción esperado por separado. Ambos prepare_projection,
reviews, dispatch entregados, dispatch sin entrega, Remote.execute, reconcile
y Remote.edit conservan sus snapshots. El rechazo de VALIDATE_EVALUATION se
sobreestima por el perform completo más su contexto.

El bucle de observaciones contiene2 entradas: ready crea dos rows y publica
cada observation con su ID en un lab nuevo. Las llamadas de ref son métodos
históricos ya revisados; cero eventos adicionales no significa cero trabajo.
Los resultados de comparación siguen siendo parte de la prueba original,
sin declarar una compatibilidad funcional P01 nueva.

## DR36: las filas del oráculo también cuentan

source() por defecto produce4 entidades (REQ, EP, T0, T1) y4 relaciones
(ER, TE0, TE1, DEP), con endpoints entre esas cuatro entidades. Los planners
parten de copia del estado y generan claves de participantes, a lo sumo4 de
entidades y4 de relaciones. El génesis de ambos modelos tiene provenance vacío.
Sólo apply/APPLY_BATCH añade una fila por clave de plan; capture, review y
prepare no publican provenance. El segundo source cambia revision, conservando
IDs y targets. Por tanto hay como máximo8 filas por lado tras una aplicación
y16 tras dos. No se usa la igualdad final como premisa de esta cuenta.

assert_relational_equivalence realiza un state inicial, una aserción por fila
izquierda, un state más una aserción por fila derecha y la comparación final.
Con g aplicaciones su cota es **2+24g**:26 para g=1 y50 para g=2. inspect
retorna datos decodificados; reemplazar manifest_sha256 dentro de esa copia no
restaura ni modifica la autoridad histórica o durable.

| Parte | Envolvente de eventos |
|---|---:|
| Cinco labs y prepare(project=False) | 180 |
| Cinco comparaciones después de un apply | 130 |
| Dos planes y dos APPLY_BATCH positivos | 56 |
| Dos comparaciones después de dos applies | 100 |
| Tres planes negativos sobreestimados | 72 |
| Seis contextos esperados y tres comparaciones de códigos | 15 |
| EDIT_ENTITY del caso local | 4 |
| Lifecycle de raíz | 3 |
| Total | 560 |

Son cinco escenarios literales: dos positivos y tres negativos, sin subTest.
El cuerpo de plan rechazado usa la envolvente completa de seis perform; se
conservan los contextos de ambos modelos y el coste de los argumentos.

## Lo que falta para D5

Las dos raíces añaden816 a las cotas superiores parciales; las42 suman19090.
No es una cota global ni una cota inferior de eventos; superar16384 con esta
suma no demuestra exceso runtime. Tampoco se suma a I100/helpers solapados.
R>=19037>16384(I97) sigue siendo la cota inferior independiente de referencias.
Faltan46 raíces T/R y233 tests de otras familias, bytes/operandos, owners,
grupos/contextos y la composición de24 cuotas/Reader. No se crea certificado,
perfil, cuota, autorización o destino de captura nuevos.

Git HEAD b22bc4d9189896c12f35c648cf47a93937b76b58 y los nueve archivos locales
I104/I105 se preservan. I106 queda local, sin commit/push en este corte.
P0;83 SUPPORTS_BOUNDED/1 PARTIAL y UI04.1 parcial; D1–D4 cerrados e I1–I20/A52
aceptado. D5/H07/G01–G07 y GI33/34/38/39/40 globales abiertos. I83/CT96 permanece
evidencia de componentes, sin deducir persistencia/recuperación integrada o
compatibilidad funcional de PASS aislados. Captura funcional, IR03/suficiencia
global y publicación requieren sus decisiones separadas. Sin proveedores,
credenciales o corpus reales, consumo/reservas, activación, promoción,
despliegue ni D6. No se inspecciona ni limpia el estado operativo dev/run_data/D4.
