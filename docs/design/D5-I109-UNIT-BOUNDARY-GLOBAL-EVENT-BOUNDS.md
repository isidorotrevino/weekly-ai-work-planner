# I109 — previews, adaptador simulado y reportes en la cuenta global

Fecha:2026-11-04, Europe/Madrid. **112 de321 raíces tienen ahora cotas de
eventos por fuente**:88 T/R y24 pruebas adicionales de tres grupos completos.
No se ejecutaron suites, callbacks del producto, consultas SQL, threads,
procesos o campañas. I108 y los paquetes funcionales sellados se conservan.

[Desglose de24 raíces y closure de llamadas](../validation/D5-I109-unit-boundary-event-bounds.json) ·
[Registro global112/321](../validation/D5-I109-global-event-bound-coverage.json).

| Grupo adicional | Raíces | Suma de cotas superiores |
|---|---:|---:|
| test_local_preview | 17 | 150 |
| test_postgres_adapter | 3 | 16 |
| test_review_report | 4 | 33 |

El incremento es199 eventos y el subtotal de112 raíces es **27878**.
Cada raíz conserva TEST_START/TEST_RESULT/TEST_END, las aserciones observadas,
los dos eventos de cada contexto esperado y un TEST_RESULT por subTest.
Las cuotas2048/test y131072/campaña permanecen;16384 es referencias.

## Qué se contó y qué trabajo permanece

LocalPreviewTest sólo añade eventos de unittest en estas rutas. observe/
save_preview y sus dependencias se inspeccionaron como closure nominal por AST:
lecturas, escritura de artefactos temporales, hashes, parser y cleanup siguen
haciendo trabajo, sin llamar Store/Drive o protocolos observados. changing_read
es el callback local de lectura/escritura descrito por fuente, sin aserciones.
No se ejecutó ese callback ni se creó un archivo temporal de producto en I109.

AdapterBoundary construye LabClient con __new__ y asigna query=Mock. submit
conserva la verificación y la preparación de SQL, pero la llamada final alcanza
el Mock. No se invoca __init__, query original, Docker/psql o main.
Mock.assert_not_called no pertenece a la allowlist TestCase instrumentada;
se conserva como trabajo y oráculo original, sin inventar un evento capturado.

ReportBoundary conserva todos sus checks y los tres contextos negativos.
Para su bucle de review_items se usa una cota6, sin deducirla del primer
assert: los dos fixtures tienen3 filas cada uno; parse propone a lo sumo una
fila por línea, compare_previews emite como máximo una entrada por clave de
la unión y build_report como máximo un review_item por cambio. Es una cota
conservadora de6, no una medición del número de elementos devueltos.
La closure incluye el import local register.parse, helpers de payload/compare
y las llamadas nominales de record. No es una prueba general de despacho Python:
requiere los bindings, tipos builtin y fixtures pinneados, sin callbacks nuevos.

## Tramo posterior a la suite

La cola de run_relational_durable_lab.main, después de TextTestRunner.run,
añade **0 eventos observados** bajo sus bindings originales. Itera recursos,
llama is_alive/wasSuccessful, crea cobertura, cuenta, lee/hash inputs y emite
JSON; no llama Store/Drive, start/receive/finish/join/recv ni asserts instrumentados.
Se inspeccionó fuente de stdlib CPython3.14.4 para Thread.is_alive,
BaseProcess.is_alive y TestResult.wasSuccessful; el hash de process.py coincide
con el pin del registro. No se invocaron esos métodos para sondear recursos.
Thread.is_alive usa Event.is_set y el handle is_done; BaseProcess usa poll,
sin join adicional. Los callbacks de resultado durante suite ya están en cada
raíz y no se suman otra vez. Las lecturas/CPU/errores de la cola siguen existiendo.

Esto no cierra discovery/imports antes de suite ni la finalización del recorder/
worker o los caminos de fallo. La composición global queda:

`E_global <= 27878 + U_remaining209 + U_discovery_and_recorder_finalization + 0_post_suite`

El margen aritmético condicional es103194; no es admisión ni una cuota
nueva. Los dos términos desconocidos no se sustituyen por0. Restan209 raíces
de7 familias; el registro las enumera por ID, grupo y cardinalidad.

## Capacidad y evidencia funcional

Siguen pendientes referencias, operandos, bytes de filas/eventos/tablas/páginas
y la composición de24 cuotas/Reader. R>=19037>16384(I97) sigue bloqueando la
representación original. I86/I89/I92 permanecen INVALID_CAPTURE, sin sumar ni
reanudar prefijos; no existe captura P01 completa válida e IR03 sigue NOT_READY.
No se crea contrato, perfil, autoridad o destino nuevos. La captura futura y
la implementación/componentes requieren sus decisiones concretas posteriores;
suficiencia global y publicación permanecen separadas.

HEAD b22bc4d9189896c12f35c648cf47a93937b76b58 y los23 archivos locales I104–I108
se preservan. I109 sólo añade documentación local, sin commit/push. P0;83
SUPPORTS_BOUNDED/1 PARTIAL, UI04.1 parcial; D1–D4 cerrados e I1–I20/A52 aceptado.
D5/H07/G01–G07 y GI33/34/38/39/40 globales abiertos. Sin proveedores, credenciales
o corpus reales, consumo/reservas, activación, promoción, despliegue ni D6.
No se deduce persistencia o recuperación integrada de PASS aislados; no se
inspecciona ni limpia estado operativo dev/run_data/D4.
