# I113 —cota global de eventos por fuente, capacidad conjunta pendiente

Fecha:2026-11-04, Europe/Madrid. **Las321 raíces de12 grupos están acotadas
por fuente para eventos**. El techo global derivado es **30129 eventos**,
menor que131072, con margen100943. No es una ejecución nueva, una
predicción de captura válida o un certificado conjunto de capacidad.
No se importó producto/runner ni se ejecutaron suites, procesos, hooks o campañas.

[Drive, wrappers, helpers y tramo exterior](../validation/D5-I113-drive-global-event-bounds.json) ·
[Registro global321/321](../validation/D5-I113-global-event-bound-coverage.json).

## Últimas30 raíces y envolventes conservadoras

Drive aporta como máximo564 eventos. Cada raíz incluye setup,3 eventos
lifecycle, aserciones/contextos/subTest y los helpers transitivos. command se
sobreestima con1 snapshot aunque el caller pueda suministrarlo. advance añade
1 terminal. read_command/inspect no llaman snapshot/advance. Los constructores
se sobreestiman con1 incluso fuera de DI28, sin cargar dos veces el Store
interno de TemporaryFixtureLab. Son envolventes, no trazas exactas.

message añade1 assertTrue; spawn añade1 terminal y kill_at incluye spawn,
message y3 aserciones más. Raw Connection.recv, BaseProcess.join y el start
directo DI07 retienen witnesses/registros/exit, pero no emiten otro evento:
no se equiparan a los wrappers start/receive/finish T/R. Esa carga de referencias
sí existe y queda pendiente. El hijo no tiene observers; no contar sus Store
como si fueran trabajo instrumentado del padre. Cleanup conserva sus joins y
comprobaciones originales, aunque no añada un evento unittest nuevo.

DI22 construye8 alternativas (4+2+1+1) y DI23 cuatro páginas bad. Se deriva
la cardinalidad de append/loops literales, sin inferirla del resultado. Los
mutadores/corrupciones/links del fixture sólo se inspeccionaron por fuente.
No se ha accedido a stores de producto ni limpiado recursos operativos.

## Discovery y finalización

El grafo estático de imports contiene33 nombres de módulo (superconjunto,
incluidos imports locales y alias de la misma fuente). Sus expresiones
superiores sólo construyen dict/set, regex, contexto spawn, encabezado de tabla
y aliases T/R mediante range/getattr/setattr; no invocan Store o métodos de test.
Se revisaron guardas main, ausencia de load_tests/module getattr/custom metaclass
y los cuerpos stdlib de loader/construcción TestCase. Su contribución de eventos
es0 bajo los bindings normales, sin hooks de importación o clases nuevas.

Después del entrypoint, exercise restaura los parches antes de finish. El MRO
activo verifica valores/bindings, cierra páginas y arma sidecar/diagnóstico;
no emite nuevos eventos ni invoca métodos originales del fixture. La cola de
runner posterior a suite ya estaba acotada por0(I109). **No se declara gratis
la finalización**: sigue gastando referencias, IO, bytes, CPU y Reader.
La cota de eventos es, por tanto:

`E_global <= 30129 + 0_discovery + 0_post_suite + 0_finalize = 30129`

Scope: ruta original completa PASS, fuentes/bindings pinneados, observación
válida y datos builtin. Errores inesperados/importers/hook nuevos o cambio de
perfil exigen reevaluación. Ninguna cota se ha derivado imponiendo131072 o2048
como sustituto de los cuerpos source; el margen no autoriza una captura.

## Falta la capacidad conjunta y la evidencia funcional

321 frames de raíz(I110) y el máximo de eventos no limitan contextos, owners,
grupos, tablas, operandos o referencias. **R>=19037>16384(I97)** sigue vigente.
Hace falta la cota superior de charging en30 sitios y los bytes de valores,
filas/eventos/tablas/páginas/raw/sidecar/contexto/launcher, más Reader/24 cuotas.
No se crea cifra de refs, perfil, contrato aprobado, autoridad o destino nuevos.

I86/I89/I92 permanecen INVALID_CAPTURE; no se fusionan/reanudan y no hay P01
completo válido. IR03 sigue NOT_READY. Contrato/perfil/implementación/componentes
y captura requieren decisiones concretas posteriores; suficiencia global y
publicación son separadas. Las7 obligaciones reales no quedan aceptadas por
estas cuentas o por los componentes sellados.

HEAD50c49678568bae2abeefbe5fec0285f26c628283 e I111/I112 se conservan. I113
queda local, sin commit/push. P0;83 SUPPORTS_BOUNDED/1 PARTIAL, UI04.1 parcial;
D1–D4 cerrados e I1–I20/A52 aceptado. D5/H07/G01–G07 y GI33/34/38/39/40 globales
abiertos. Sin proveedores/credenciales/corpus reales, consumo/reservas,
activación, promoción, despliegue ni D6. No se infiere persistencia/recuperación
integrada de PASS aislados ni se inspecciona/limpia estado operativo dev/run_data/D4.
