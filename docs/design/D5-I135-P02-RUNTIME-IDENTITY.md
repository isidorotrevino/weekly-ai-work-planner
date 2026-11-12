# I135 — preparación de P02 RUNTIME-IDENTITY

Fecha: 2026-11-12, Europe/Madrid. Base publicada:
`6a9469ac2366b06651cd4a7b2f653d36cd07476c`.

**P02 queda preparado como dossier de evidencia insuficiente. E01 sigue abierta
y PFC126-CANDIDATE-03/I122/PJC115-R2 siguen sin admisión.** Los materiales
vinculados no aportan un cierre autenticado del runtime objetivo ni
correspondencia fuente/binario. Se aplica el rechazo previsto por I132: no se
presenta el expediente como identidad probada o plantilla de atestación firmada.

[P02](../validation/D5-PFC126-03-E01-RUNTIME-IDENTITY.json) ·
[Revisión de preparación](../validation/D5-I135-P02-preparation-review.json) ·
[Auditoría estática](../validation/D5-I135-audit.py) ·
[Integridad](../validation/D5-I135-integrity.json).

## Vinculación y procedencia

Se conservan los bytes de candidata03, plan I132, P01 y revisión I134. El nuevo
artefacto utiliza el destino y schema previstos para P02, incluye los seis campos
específicos y fija sus inputs por SHA256. Cada campo explica lo disponible, la
carencia y el material preexistente necesario para una futura aceptación.

P01 tiene conformidad técnica del ámbito fuente según I134; su aceptación de
actor independiente sigue pendiente. Preparar este dictamen negativo de P02 no
satisface ni omite esa dependencia. Los snapshots históricos permanecen intactos.

El productor documental es el asistente de este chat. No se atribuye la función
de custodio de imagen/build, autoridad operadora o revisor independiente. Las
identidades, firmas, confianza y validez ausentes permanecen null. No se contacta
a terceros, accede a cuentas externas o afirma ausencia global de documentos:
el dictamen se limita a los materiales de repositorio vinculados y suministrados.

## Resultado por campo obligatorio

| Campo del plan | Evidencia y disposición |
| --- | --- |
| exact_interpreter_stdlib_frozen_builtin_extension_closure | I127 sólo aporta un binario histórico, 12 archivos stdlib seleccionados y cinco registros de extensiones. Cierre seleccionado completo desconocido; no aceptado |
| native_dependency_allocator_kernel_config_pins | Dependencias nativas transitivas, libc/allocator y kernel/configuración sin pins acreditados; no aceptado |
| source_binary_build_correspondence | Sin registros autenticados que enlacen fuentes, toolchain, opciones y binarios; no aceptado |
| actual_target_not_just_observed_local_reference | Sin imagen/release objetivo, selección y validez acreditadas; no aceptado |
| producer_authority_signature_and_validity | Sin custodio competente identificado, autoridad, firma y confianza verificables; no aceptado |
| clock_and_process_service_domain_identity | Marcadores y procesos definidos por contrato, pero implementación/dominio real de reloj y servicio sin atestar; no aceptado |

Se incorpora la referencia histórica I127 íntegra, con su hash, fecha y límites;
no se vuelve a muestrear el intérprete, las bibliotecas o el kernel actuales.
Su hash de intérprete coincide con el candidato en los registros suministrados.
Esto conserva E01-R1 como referencia histórica y E01-R2 como consistencia
documental; E01-R3/R4 continúan sin evidencia completa. Ningún criterio cierra E01.

La ausencia de un archivo externo para una extensión no prueba ausencia de un
builtin. `_json`, `_struct` y `_posixsubprocess` figuran como referencias builtin;
los candidatos `_hashlib` y `_multiprocessing` tampoco prueban selección o cierre
nativo transitivo. La etiqueta histórica del kernel no es hash de imagen/config.
`pymalloc=1` y los tamaños históricos no justifican el backend ni el overhead H11.

## Contraste de fuentes, sin ejecutar discovery

Se leen los blobs de los 71 archivos Python del input registrado y los ocho
archivos del superconjunto local del observador: 79 fuentes distintas. Se
comprueban sus hashes contra P01 y los bytes actuales. El AST registra 770 imports
sintácticos y 13 sitios explícitos `__import__`/`import_module`, con argumentos
literales o AST de argumentos dinámicos. El resumen fija el hash del vector de
imports; no lo denomina cierre stdlib, frozen, builtin, nativo o realmente cargado.
Incluye ramas anidadas o inalcanzables y no resuelve recursivamente dependencias
externas, alias o mecanismos arbitrarios de carga.

Seis anclas AST fijan command/Popen, las invocaciones normalizadas y los dos
contextos spawn originales. En particular:

- El lanzamiento declara `sys.executable`, `-B`, un módulo fijo y un entorno
  explícito. La fuente no acredita el contenido de ese ejecutable o la selección
  del loader, configuración de inicio o dependencias en el objetivo.
- El comando público `python3` es lógico y normalizado. `path_sha256` en la
  invocación base resume los bytes de la ruta, no los bytes del binario; no
  reemplaza una identidad de ejecutable autenticada.
- Los contextos spawn de los dos módulos de soporte no son un inventario completo
  de procesos, runtimes hijos, CLI o dependencias nativas. No se presume que todos
  compartan automáticamente un pin de intérprete o dominio de servicio.

El expediente conserva el reloj monótono requerido y los marcadores t0/tR/tW/tF,
así como la separación de heap worker, coordinador e hijos de P01. No recoge
timestamps ni acredita implementación, resolución, tasa, sincronización, CPU,
scheduling o latencia IO/hijos. Identidad y servicio deben vincularse con P03;
ninguno de ellos se deduce de 900 segundos, watchdog, cores o cuotas.

## Disposición y límites de esta entrega

Se prepara un archivo P02 real cuyo tipo de evidencia es un análisis documental
de insuficiencia, sin firma ni cierre simulado. El material requerido queda
concreto por campo: inventario de release/imagen, configuración y selección,
proveniencia de build, mapeo fuente/binario y dependencias, confianza/validez y
mapeo de procesos/reloj/dominio. Cualquier evaluación posterior deberá verificar
el contenido y la autoridad de registros preexistentes, sin dar por obtenidos sus
hashes o garantías por enumerarlos aquí.

Se aplica el early stop de I132: las pruebas afectadas E01/E02/E03/E04 permanecen
abiertas. No se promete cierre del heap o de los 900 segundos. Los otros 18
outputs previstos siguen ausentes; P03 y paquetes posteriores no se producen.
E01–E05 no cierran y E06 sigue separado, pendiente, NOT_RUN y sin permiso de
ejecución. No se importa, construye, lanza o sondea runtime/producto/componentes.

La política numérica y de transferencia de P01 se conserva íntegra: cuotas y
presupuestos intactos, reservas asignadas cero, missing no equivale a cero. No se
modifican fuentes I122, certificado IMPLEMENTED_NOT_ADMITTED, capture_inputs,
autoridad/destino o reservas operativas. PJC115-R2 no habilitada, D5/H07 abiertos,
IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e
I1–I20/A52 aceptados sin cambios. I86/I89/I92 INVALID_CAPTURE sin reanudar/mezclar;
brechas/obligaciones reales pendientes. Sin proveedores/credenciales, consumo,
activación, promoción, despliegue o D6. No se inspecciona ni limpia dev/run_data/D4.

## Verificación y publicación

`python3 docs/validation/D5-I135-audit.py` verifica hashes, blobs Git, AST, seis
campos, límites de procedencia y dictamen negativo. Conserva 153 archivos
publicados, los inputs heredados y los cinco archivos nuevos de I135. Funciona
antes del stage y después del commit; no ejecuta los auditores históricos cuyos
supuestos de snapshot ya no corresponden al working tree actual.

PASS_STATIC_SOURCE_ONLY valida la consistencia de esta preparación, no identidad
runtime, independencia de actor, capacidad o tiempo. Se hace commit y push de
todos los cambios I135 y se verifica la referencia remota efectiva.
