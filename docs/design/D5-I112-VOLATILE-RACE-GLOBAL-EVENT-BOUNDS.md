# I112 —117 cotas de perfiles, batches y conciliación en memoria

Fecha:2026-11-04, Europe/Madrid. **291 de321 pruebas tienen cotas de eventos
por fuente**. Quedan30 de incremental_capture y discovery/finalización.
No se ejecutaron tests, hooks, threads, barreras, parsers o campañas; no se
importó producto/runner. Se conservaron I111 y todos los paquetes sellados.

[Desglose, helpers, callbacks y anclas](../validation/D5-I112-volatile-race-event-bounds.json) ·
[Registro global291/321](../validation/D5-I112-global-event-bound-coverage.json).

| Grupo | Nuevas raíces | Suma de cotas superiores |
|---|---:|---:|
| test_profiles_quotas | 38 | 319 |
| test_relational_batch | 38 | 359 |
| test_plane_reconciliation | 41 | 416 |

El incremento es1094 y el subtotal291 es **29565**. Cada raíz incluye sus
3 eventos lifecycle, aserciones/contextos/subTest, helpers y callbacks conocidos.
Son cotas condicionadas por fuente para la ruta original completa PASS con
observación válida; no son ejecuciones nuevas ni validación funcional P01.

## Callbacks y threads que sí cuentan

No se transfiere sin revisión la precondición hooks=None de I106: estas pruebas
instalan callbacks concretos de validación/publicación/envío/query. Se revisan
sus cuerpos, acciones de hilo y helpers. Los hooks de perfiles y batches sólo
modifican datos/revisiones del fixture, levantan errores o esperan barreras;
no llaman a unittest ni observers durables bajo sus tipos/bindings source.
Los cuerpos con0 eventos conservan trabajo, mensajes, excepciones y tiempo.

En Plane, created/unknown y los helpers join añaden1 assertion por llamada.
Hay **dos callbacks PC20 con2 eventos cada uno**: join añade assertFalse y
el callback añade assertEqual. En el primer test se invoca1 send/execute,
que llama before_send una vez. En el segundo se hace unknown antes de instalar
el callback y luego1 query/reconcile, que llama before_query una vez. Ambos
extras se cargan, sin contarlos también como mero cuerpo definido en la raíz.
Las demás funciones/lambdas enumeradas tienen0 assertions bajo su closure.

Thread.start/join pertenecen a threading.Thread y no al protocolo BaseProcess/
Connection del perfil. Los caller/helper asserts se conservan. Los resultados
de las carreras son oráculos del fixture original, no pruebas de concurrencia
real o persistencia integrada de proveedores. No se creó ningún hilo en I112.

## Cardinalidades de datos y bucles de presupuesto

PQ19 parte del setUp con3 constraints/observaciones seleccionadas; no publica
otras. prepare_evaluation sólo copia las seleccionadas: su bucle tiene<=3
aserciones, sin usar el check posterior del test como premisa.
RB13 parte de TASK T y añade el paquete T,U,E,R con uid determinístico paraT;
_candidate sólo crea destinations explícitos de elements y no inventa endpoints:
la unión tiene<=4 claves, con3 asserts por clave. RB23 usa una list literal2
threads. DEPENDENCIES es tuple literal4. Los demás loops son secuencias/ranges
literales o listas locales de tamaño fijado. Se mantienen loops de128 recibos,
125 observaciones y presupuestos llenos, aunque el cuerpo de fixture no emita
un observer; **no se truncan ni se omiten sus operaciones**.

## Composición y puertas pendientes

`E_global <= 29565 + U_Drive30 + U_discovery_and_recorder_finalization + 0_post_suite`

La cuota global sigue131072 eventos (refs16384). El margen condicional
101507 no es admisión ni se sustituyen los dos términos pendientes por0.
321 frames de raíz sigue siendo la cota condicional I110, distinta de contexts,
subcasos, owners y referencias. R>=19037>16384(I97) sigue bloqueando la
representación original; faltan cota superior, operandos/bytes y composición de
24 cuotas/Reader. No se crea perfil, cuota, certificado o autoridad/destino.

I86/I89/I92 permanecen INVALID_CAPTURE, sin fusionar o reanudar sus prefijos.
No existe captura P01 completa válida e IR03 sigue NOT_READY. Contrato/perfil,
implementación/componentes y captura futura requieren sus decisiones concretas;
suficiencia global y publicación permanecen separadas. Las obligaciones reales
GI06/12/18/24/30/36/42 siguen pendientes: los fixtures no las aceptan.

HEAD50c49678568bae2abeefbe5fec0285f26c628283 y los5 documentos I111 se conservan.
I112 queda local, sin commit/push. P0;83 SUPPORTS_BOUNDED/1 PARTIAL, UI04.1 parcial;
D1–D4 cerrados e I1–I20/A52 aceptado. D5/H07/G01–G07 y GI33/34/38/39/40 globales
abiertos. Sin proveedores/credenciales/corpus reales, consumo/reservas,
activación, promoción, despliegue ni D6. No se deduce persistencia/recuperación
integrada de PASS aislados ni se inspecciona o limpia estado operativo
 dev/run_data/D4.
