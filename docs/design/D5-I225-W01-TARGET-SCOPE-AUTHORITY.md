# I225 — W01: scope objetivo y frontera de autoridad

Fecha: 2026-11-24 · Plan I223 · PGO181 candidato 02 · PFC126-CANDIDATE-03/I122.

W01 queda preparado como dossier documental de scope lógico, límites y autoridad por acción. **W01 no está aceptado y SD01 sigue activo**: faltan autoridad humana de entrada verificable, revisión competente R06 y aceptación separada R08. Se mantiene la no admisión de PJC115-R2, D5 abierto e IR03 `NOT_READY`; este trabajo no cierra gates ni E01–E05.

La especificación se conserva en [el candidato W01](../validation/D5-I223-W01-TARGET-SCOPE-AUTHORITY-CANDIDATE.json). Para revisar, comenzar por `entry_authority_boundary`, `entry_authority_inventory` y `action_authority_ledger`; después contrastar los tres entregables con `/work_packages/0` del [plan I223](../validation/D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json) y la precisión N01 de [I224](../validation/D5-I224-I223-documentary-review.json).

## Los tres entregables de W01

| Entregable del plan | Preparación I225 | Límite de la evidencia |
|---|---|---|
| Scope lógico exacto | Seis rutas sucesoras, cierre de runtime/imagen/loader, caller/plataforma/ledger y ocho documentos de política fijados por hash y versión | No hay cuerpos sucesores, hashes reales de esos cuerpos, imagen/runtime ni manifiesto efectivo. W03 deberá aportarlos y cualificarlos. |
| Ledger de caps, guards, fases y exclusiones | Inventarios reproducibles desde I130/I185/I187/I189/I191 y las fronteras heredadas de I223 | Los presupuestos y reglas son candidatos; no prueban capacidad, implementación ni los 900 segundos. No se aplican cuotas o reservas. |
| Autorización por acción | Cuatro clases documentales autorizadas y ocho clases operativas pendientes de autoridad específica futura | No se implementa, ejecuta, mide, firma, contacta ni configura infraestructura. |

El identificador previsto `W01-REAL-EVIDENCE-PACKAGE` se referencia para trazabilidad del plan. Este dossier no constituye ese paquete auténtico aceptado: `actual_real_evidence_package_created=false` y los tres predicados de salida siguen pendientes de autoridad y revisión genuinas.

## Scope que deberá autenticarse

Las seis rutas pertenecen a `testing/prospective_capture_joint_prp181/`: `README.md`, `atomic.py`, `capture.py`, `run_joint_lab.py`, `test_joint_capture.py` y `worker.py`. Todas siguen ausentes; los campos de digest, miembro de imagen, representación cargada y mapping permanecen nulos. No se trasladan hashes de I122 a estas rutas. La inclusión documental de README o tests no demuestra que el runtime los cargue.

El cierre efectivo debe identificar intérprete, loader, stdlib, módulos frozen, extensiones nativas/crypto, allocator/GC, kernel/servicio/scheduler/IO y receta/toolchain. Digest de imagen y digest de runtime son conceptos separados. Caller, dominio/constructor, servicio de plataforma, reloj/epoch y ledger global siguen sin seleccionar ni acreditar; las ocho garantías de plataforma permanecen obligaciones. El claim global y el mapping único no pueden fragmentarse por caller, dominio o reinicio.

Los ocho documentos de política son el contrato I130, schemas y perfil I185, schemas de salida I187, contrato y gramática I189, contrato y schemas de custodia I191. Sus hashes conocidos fijan **documentos**, sin acreditar adopción efectiva, identidad de runtime, imagen o prueba de fuente. El dossier conserva sus reglas exactas y la recualificación histórica 179/321/12/30, junto con todos los caminos nuevos de custodia/bootstrap/salida/fallo y sus costes; la evidencia histórica no cualifica automáticamente al sucesor.

## Caps, guards y fases conservados

Los ledgers distinguen los candidatos numéricos heredados, envelopes de protocolo/salida, ocho caps de records y guards de perfil, transporte y CP07. Reader `266693693` bytes y bundle superior `221644` bytes son envelopes de diseño condicionales, sin fit real demostrado. Los límites de bodies se conservan sin producir records positivos ni efectuar operaciones de firma/crypto.

El heap copia el contrato candidato completo I130, incluidas reservas y obligaciones de solapamiento/nativo/allocator/GC; no existe atestación de capacidad ni prueba completa. Ninguna reserva se transfiere o consume para forzar un ajuste.

Las fases candidatas son 60/750/60 segundos más 30 de reserva dentro de 900. Se conservan los cuatro marcadores y sus reglas de orden, latencia de observación y cualificación de éxito. `tW` corresponde al retorno exacto `True` de `wait_worker`, no al exit físico ni a validación posterior; el camino de éxito incluye el `finally` hasta `tF`. No se toman muestras de reloj y ningún coste o marcador ausente se convierte en cero.

## Autoridad de entrada y acciones

| Slot | Requisito | Estado actual |
|---|---|---|
| EA01 | Autoridad humana auténtica y preexistente para definir/aprobar el scope lógico y sus restricciones | Identidad, competencia, nombramiento, prueba y custodia ausentes |
| EA02 | R06 competente e independiente para revisar scope, procedencia y frontera | Nombramiento y revisión genuinos ausentes |
| EA03 | R08 separado para aceptar/rechazar, conservando las ocho exclusiones S01 y las reglas de custodia/keys | Nombramiento y aceptación genuinos ausentes |

Ser el primer nodo del grafo no autoautoriza W01. Las futuras designaciones W02 o un bundle todavía inexistente no pueden constituir su única autoridad pronosticada. La petición actual permite preparar, auditar y publicar este dossier; no designa actores canónicos ni adopta el scope. El mismo asistente preparador no acredita independencia R06 ni aceptación R08. No se hacen contactos, nombramientos implícitos ni enrollment.

Las acciones permitidas son lectura documental/Git/hashes, preparación del dossier, auditoría documental propia y commit/push. El registro mantiene sin autorizar ejecución de producto/componentes; implementación/build; probes de plataforma/reloj/ledger; firma/keygen/crypto positiva; contacto; provisioning/enrollment/configuración de servicio; cambios activos de capture_inputs/root/autoridad/destino; cambios de cuotas o reservas. Cada acción futura exige autoridad exacta y cobertura de costes propia; no se incluyen comandos operativos.

La aportación externa sólo podrá evaluarse si se recibe material genuino con procedencia autorizada. Actualmente no hay proveedor, material ni revisión. Documentar el scope no congela un snapshot efectivo ni inicia W02/W03. Cualquier cambio de cuerpo, actor, imagen/runtime, dominio, epoch/key, política o límite exige análisis de impacto y nueva revisión; no hereda automáticamente hashes, mappings o aceptación.

## Frontera de cierre

Los tres predicados del plan se reproducen literalmente, con contenido documental preparado y aceptación pendiente. El handoff conserva la separación entre evidencia prelaunch/recursos y la ruta final E06/Q/root/claim. Los 30 gates y E01–E05 siguen pendientes; CE12 continúa `DEFERRED_NOT_AUTHORIZED`, sin claim, worker ni recibo creado. Ninguna aceptación de W01 podrá completarse tomando datos futuros aún no aceptados como si ya fueran autoridad válida.

## Verificación y unidad publicable

Comando documental: `python3 docs/validation/D5-I225-audit.py`.

Resultado esperado: `PASS_STATIC_SOURCE_ONLY_W01_ENTRY_AUTHORITY_MISSING_NOT_ACCEPTED`. La revisión de preparación fija el resultado y los conteos exactos; la auditoría verifica 922 pins contra el commit base, preserva 614 archivos publicados, reproduce la reconstrucción/revisión documental I224 sin ejecutar sus mains de publicación y rechaza doce mutaciones negativas en memoria. No añade proyecciones históricas de presencia. Estas comprobaciones metodológicas no sustituyen una revisión competente independiente.

Runtime harness: **N/A**. Sólo se leen JSON, Git, hashes y políticas; no se ejecutan/importan/compilan producto o componentes, codecs/crypto positivos, procesos de captura, builds, probes de servicio/reloj/ledger, tests ni benchmarks.

La unidad excede 400 líneas por los inventarios exactos y pins de preservación; se declara el exceso sin comprimir evidencia. No se crea PR. Rollback limitado a estos cinco archivos nuevos, sin modificar antecedentes:

- `docs/design/D5-I225-W01-TARGET-SCOPE-AUTHORITY.md`
- `docs/validation/D5-I223-W01-TARGET-SCOPE-AUTHORITY-CANDIDATE.json`
- `docs/validation/D5-I225-preparation-review.json`
- `docs/validation/D5-I225-audit.py`
- `docs/validation/D5-I225-integrity.json`

La siguiente revisión puede evaluar la preparación documental de W01 y estas fronteras. La aceptación real sigue detenida por SD01 hasta aportar autoridad de entrada y revisiones genuinas, sin inferir permisos operativos de esta publicación.
