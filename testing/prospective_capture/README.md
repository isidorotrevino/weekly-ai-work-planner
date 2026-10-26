# I70 — componentes de captura prospectiva

[Contrato I69](../../docs/design/D5-I69-PROSPECTIVE-CAPTURE-DESIGN.md) y matriz PF60. Sólo stdlib y módulos nuevos; ningún import de producto o runner histórico al cargar el capturador.

- `python3 -B -m testing.prospective_capture.run_capture_lab`: PF60 sintéticos; no ejecuta P01–P10.
- `python3 -B -m testing.prospective_capture.capture`: plan cerrado de lectura, sin lanzar campañas.
- El modo `--capture P01` (hasta P10) queda bloqueado sin autorización I71 y pins explícitos de los componentes validados. No se ejecuta en I70.

La autorización futura se registraría en el path fijo `docs/validation/D5-I71-capture-authorization.json`, schema `d5.capture-authority.v1`: fase I71_EXPLICITLY_APPROVED, scopes cerrados, hash del registro y hashes de código/evidencia I70. Ese archivo no existe ni se crea en I70. Es una puerta de coherencia de la herramienta; quien controla código y manifest no obtiene atestación independiente ni aprobación humana por inventar un archivo. El agente necesita autorización humana I71 antes de crearlo o lanzar campañas.

Workers propios, READY/RELEASE correlacionados y archivos nuevos bajo `docs/validation/D5-I71-Pxx/` con OWNER. Un archivo/directorio existente bloquea; no overwrite ni root/módulo/URL/command libre. Contexto y argv normalizados del worker se distinguen de la declaración del runner. Observadores temporales conservan retorno/exception y restauran originales; no llaman snapshots extra. Frames del capturador son distintos de los IDs del dueño. Métodos generados tienen bindings de fuente tipados. Metadata anidada se referencia y la incompletitud de hijos se propaga.

Los PF prueban suites/Stores/records y procesos sintéticos nuevos; no prueban compatibilidad de captura sobre las692 ocurrencias futuras. Cualquier incompatibilidad/budget en I71 debe bloquearse y presentarse, sin debilitar oráculos, alterar producto o ampliar límites para pasar. No se reescribe historia ni se cierra D5 por presencia de campos o PASS aislados. P0 y agregado81/3 vigentes; publicación aparte.
