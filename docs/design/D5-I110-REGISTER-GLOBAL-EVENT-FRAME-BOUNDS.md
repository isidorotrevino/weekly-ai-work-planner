# I110 — comparación y compatibilidad:27 cotas más y frames de raíz

Fecha:2026-11-04, Europe/Madrid. **139 de321 pruebas tienen cotas de eventos
por fuente**. Restan182 tests de5 familias y discovery/finalización.
No se ejecutaron suites, CLI del producto, parsers o campañas; no se importó
producto/runner. La evidencia funcional sellada permanece sin cambios.

[Desglose de27 raíces, mutadores y frames](../validation/D5-I110-register-comparison-event-bounds.json) ·
[Registro global139/321](../validation/D5-I110-global-event-bound-coverage.json).

| Grupo adicional | Raíces | Suma de cotas superiores |
|---|---:|---:|
| test_register_comparison | 16 | 149 |
| test_register_compat | 11 | 104 |

El subtotal nuevo es253; el acumulado de139 raíces, **28131**. Son
cotas de ruta original completa PASS con observación válida, sin atribuir una
captura nueva o predecir que vaya a ser válida. La composición sigue:

`E_global <= 28131 + U_remaining182 + U_discovery_and_recorder_finalization + 0_post_suite`

El techo global es131072 eventos;16384 es referencias. El margen aritmético
102941 no es admisión. No se sustituyen términos desconocidos por0,
ni se suman helpers de I100/I109 otra vez.

## Bucles, mutación de JSON y CLI

Todas las iteraciones de estos27 tests tienen cardinalidad literal. Se
conservan los resultados subTest, las aserciones y los dos eventos de cada
contexto esperado; lambdas de campos forjados son8 mutadores update sobre
contenedores builtin de json.loads. No llaman assertions u observers; su
trabajo y cambios se mantienen. La closure de observe/save_preview/load_preview/
compare_previews es la revisada en I109, con fuentes y bindings preservados.
SetUp/capture/unsafe_artifact conservan IO/cleanup privados originales, no
asignaciones de Store o llamadas a Drive/protocolos observados.

El test de CLI contiene2 subprocess.run con las mismas entradas/límites fuente.
Cada vuelta conserva3 aserciones y1 resultado subTest. No son BaseProcess.start,
join o mensajes de Connection registrados. El hijo de CLI no hereda los observers
ni ejecuta una suite de tests; no se cuentan sus operaciones como si fueran
fronteras parentales. Esto no acota tiempo/CPU/bytes de subprocess, ni acredita
éxito de CLI nuevo: **no se ha lanzado ninguno en I110**.

## Cota de frames de raíz

Para la suite original completa, bajo los bindings pinneados y sin ejecución
anidada/sustitución de run, hay **321 frames de raíz**, frente al techo4096
(margen3775). Esta es una expectativa por fuente, no una observación runtime.
El inventario original contiene321 IDs únicos/12 grupos; TestCase.run inicia
cada caso una vez y TextTestResult delega al startTest observado. Recorder.start
crea una entrada frames por ese callback. _SubTest.__init__ inicializa su objeto,
pero subTest sólo reporta addSubTest: no ejecuta otro TestCase.run/startTest.
Se inspeccionaron los12 módulos de pruebas: no llaman runners o lifecycle
anidados; la única llamada .run es el subprocess de CLI ya descrito.

Se guardan los cuerpos/hash de TestCase.run, _SubTest.__init__, TextTestResult.
startTest y TestSuite.run leídos de stdlib. El hash de unittest.case coincide
con el pin del registro. No se ejecutaron esos métodos. Cambiar discovery,
hooks/run o las identidades invalida la aplicabilidad; no se tolera un callback
extra para mantener la cifra. **Frames no son contextos, subcasos, owners o
referencias**:321 no limita la cardinalidad de esas tablas ni acredita capacidad
conjunta, y no hay certificado numérico completo.

## Pendientes y conservación

Quedan las familias incremental_capture30, offline_integration35,
plane_reconciliation41, profiles_quotas38 y relational_batch38:182 tests.
Siguen pendientes discovery/finalización, referencias, operandos y bytes de
filas/eventos/tablas/páginas; Reader y24 cuotas deben componerse. I97 conserva
R>=19037>16384. I86/I89/I92 siguen INVALID_CAPTURE; no existe P01 completo
válido e IR03 permanece NOT_READY. No se crea perfil/cuota/autoridad/destino.
Contrato/implementación/componentes y captura futura requieren decisiones
concretas posteriores; suficiencia global y publicación son separadas.

HEAD b22bc4d9189896c12f35c648cf47a93937b76b58 y27 archivos locales I104–I109 se
conservan. I110 queda local, sin commit/push. P0;83 SUPPORTS_BOUNDED/1 PARTIAL,
UI04.1 parcial; D1–D4 cerrados e I1–I20/A52 aceptado. D5/H07/G01–G07 y
GI33/34/38/39/40 globales abiertos. Sin proveedores/credenciales/corpus reales,
consumo/reservas, activación, promoción, despliegue ni D6. No se infiere
persistencia/recuperación integrada de PASS aislados ni se inspecciona o limpia
estado operativo dev/run_data/D4.
