# I136 — revisión de P02 RUNTIME-IDENTITY

Fecha: 2026-11-12, Europe/Madrid. Base publicada:
`a0e4c540bea9120b9efb4f17ff8daa2f448252a8`.

**Se confirma el dictamen de evidencia insuficiente de P02.** El dossier
representa correctamente los límites de sus fuentes y no se encuentran defectos
bloqueantes de esa representación. Esto no permite aceptar la identidad del
runtime objetivo: los seis campos siguen insuficientes, E01 permanece abierta
y PFC126-CANDIDATE-03/I122/PJC115-R2 siguen sin admisión. P02 conserva sus bytes.

[Revisión documental](../validation/D5-I136-P02-documentary-review.json) ·
[Reconstrucción desde Git](../validation/D5-I136-P02-source-reconstruction.json) ·
[P02 revisado](../validation/D5-PFC126-03-E01-RUNTIME-IDENTITY.json) ·
[Auditoría](../validation/D5-I136-audit.py) ·
[Integridad](../validation/D5-I136-integrity.json).

## Contraste realizado

Se lee el blob de P02 publicado en I135 y se recomponen sus 125 pins desde el
commit de preparación declarado (`6a9469a…`). Todos coinciden con sus SHA256 y
los bytes actuales. Se cotejan ruta/schema, registro canónico de la tarea P02,
contrato03/I122 y dependencia P01. El plan y las fuentes históricas permanecen
intactos; no se reescribe ningún snapshot para declarar aceptación nueva.

Desde los blobs se analizan las 79 fuentes Python del ámbito P01 y las seis
anclas de P02. Se reconstruyen el vector de 770 imports sintácticos y los 13
sitios de importación dinámica registrados, con los mismos hashes/resultados.
Los 12 argumentos literales y el argumento `entry['runner_module']` permanecen
diferenciados. Este último se vincula a la declaración del registro:
`testing.D5.run_relational_durable_lab`, con ruta y hash de fuente concordantes.
No se ejecutan imports, discovery, factories, runner, producto o componentes.

La comprobación semántica del AST confirma:

- El command del worker usa `sys.executable`, `-B` y el módulo fijo de I122;
  Popen recibe el entorno explícito declarado y una sesión nueva.
- La invocación pública normaliza su command como `python3`. El `path_sha256`
  heredado calcula un hash de los bytes de la ruta `sys.executable`, sin leer el
  binario. No puede acreditar la identidad del ejecutable seleccionado.
- Los dos contextos de soporte declaran `multiprocessing.get_context('spawn')`.
  Esa sintaxis no acredita los binarios de hijos ni cubre todos los procesos.

El inventario sintáctico de imports conserva límites relevantes. En ImportFrom,
el vector resume módulo y nivel, sin enumerar los nombres importados o sus alias;
no es un inventario semántico completo. La detección de los 13 sitios explícitos
no cubre todos los loaders, alias o mecanismos arbitrarios posibles. Incluye
ramas anidadas o inalcanzables y no resuelve cierre stdlib/nativo transitivo.
P02 ya lo clasifica como resumen de fuente sin completitud ni identidad cargada;
esta precisión no obliga a alterar su dictamen negativo. Tampoco la declaración
del runner prueba qué módulo o binario cargaría el objetivo real.

## Disposición de las seis obligaciones de identidad

| Campo P02 | Disposición I136 |
| --- | --- |
| Cierre intérprete/stdlib/frozen/builtin/extensiones | Insuficiente: referencia histórica parcial, sin manifiestos completos del objetivo seleccionado |
| Dependencias nativas/allocator/kernel/configuración | Insuficiente: no se acredita correspondencia ni cierre nativo y de configuración |
| Correspondencia fuente/binario/build | Insuficiente: no se aporta proveniencia autenticada de fuente, toolchain, opciones y binarios |
| Objetivo real frente a referencia local | Insuficiente: selección, imagen/release, pins completos y validez no acreditados |
| Productor autorizado/firma/validez | Insuficiente: custodio, autoridad, firma/confianza y aceptación independiente ausentes |
| Identidad de reloj/procesos/dominio de servicio | Insuficiente: definición contractual preservada, implementación y dominio real sin atestación |

Se contrastan 35 valores null explícitos en estos seis registros. Son una lista
de campos desconocidos, no el número total de hechos o artefactos faltantes.
No se sustituyen por cero, un manifiesto vacío, valores del helper actual o una
firma ilustrativa. El material preexistente requerido por campo en P02 sigue
siendo necesario; enumerarlo no lo convierte en evidencia aportada.

La referencia I127 coincide íntegramente con P02: 12 archivos stdlib y cinco
registros de extensiones seleccionados. `_json`, `_struct` y `_posixsubprocess`
son referencias declaradas builtin; ausencia de fichero externo no significa
ausencia de implementación. `_hashlib` y `_multiprocessing` sólo aportan
candidatos de archivo, sin selección o cierre nativo demostrados. La etiqueta de
kernel y `pymalloc=1` tampoco acreditan imagen/configuración ni modelo allocator.
No se muestrea de nuevo el sistema actual.

El reloj requerido, los marcadores t0/tR/tW/tF y el ámbito de procesos coinciden
con contrato/P01. No hay timestamps, correspondencia real de runtimes hijos o
garantías de CPU/scheduling/IO. Se mantiene separado el servicio de P03 y las
pruebas de heap/trabajo/900 segundos posteriores.

## Aceptación, independencia y efectos

Los 12 controles documentales confirman la coherencia del dossier insuficiente.
No se requiere modificar P02 para expresar ese resultado. E01-R1 conserva
HISTORICAL_REFERENCE_ONLY, E01-R2 DOCUMENTARY_CONSISTENCY_ONLY y E01-R3/R4
COMPLETE_EVIDENCE_NOT_SUPPLIED. Ninguno cierra E01; se confirma la aplicación
de la regla de rechazo de P02 y del early stop de I132.

Este mismo asistente preparó I135. La reconstrucción separada es una revisión
técnica documental, sin atestar independencia de actor/organización, competencia
de custodio, firma o aprobación de un tercero. La aceptación independiente de
P01 y de P02 sigue pendiente; no se omite la dependencia por existir esta revisión.
La conformidad documental del dictamen negativo no equivale a aceptación runtime.

Los otros 18 outputs del plan siguen ausentes, sin iniciar paquetes posteriores.
E01–E05 siguen abiertas, E06 separado, pendiente y NOT_RUN. No se concede permiso
de ejecución ni se produce atestación de plataforma, garantía de recursos,
SOURCE_CAPACITY_VERIFIED o habilitación de captura.

P02, candidata03, plan I132, P01 y fuentes mantienen sus bytes. Cuotas y
presupuestos intactos, reservas asignadas cero; certificado
IMPLEMENTED_NOT_ADMITTED, capture_inputs y autoridad/destino sin cambios.
PJC115-R2 no admitida; D5/H07 abiertos e IR03 NOT_READY. P0 conserva
83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados sin cambios.
Brechas/obligaciones reales pendientes; I86/I89/I92 INVALID_CAPTURE sin reanudar
ni mezclar. Sin proveedores/credenciales, consumo, reservas operativas,
activación, promoción, despliegue o D6. No se inspecciona ni limpia dev/run_data/D4.

## Verificación y publicación

`python3 docs/validation/D5-I136-audit.py` reproduce hashes/blobs/AST, semántica
de las seis anclas, declaración del runner, campos desconocidos y decisión de
no admisión. Conserva 158 archivos publicados y los inputs heredados. Sólo hay
cinco archivos nuevos I136: documento, revisión, reconstrucción, auditor y sello.
No se ejecutan los auditores históricos con sus supuestos de snapshot antiguos.

PASS_STATIC_SOURCE_ONLY significa consistencia de la revisión documental;
no prueba de identidad runtime, independencia, capacidad o tiempo. El auditor
funciona antes del stage y después del commit. Se hace commit y push de todos
los cambios I136 y se verifica la referencia remota efectiva y el árbol limpio.
