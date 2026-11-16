# I187 — Contexto y launch completos como contrato candidato

Fecha: 2026-11-16, Europe/Madrid. Base:
`ade0fa496cba1507155c177daae4ae84af41b975`.

**I187 prepara los schemas completos de contexto/launch para PGO181 candidato
02:** siete ramas cerradas, un cuerpo idéntico para ambas copias físicas y
binding obligatorio incluso en fallback. La cota estructural más alta es
10.798.483 bytes por cuerpo, inferior al cap conservado de 12.582.912.
Es una propuesta documental sin adoptar ni implementar; no acredita capacidad
runtime o admisión. F179-01 y D5 siguen abiertos e I122/PJC115-R2 sin admisión.

## Ruta de revisión

1. Leer el [contrato candidato](../validation/D5-I187-CONTEXT-LAUNCH-CONTRACT-CANDIDATE.json):
   representación, ramas, reglas O01–O13, prioridad y proyección legacy.
2. Contrastar el [paquete completo de schemas](../validation/D5-I187-CONTEXT-LAUNCH-SCHEMAS-CANDIDATE.json).
3. Revisar la [preparación y cotas](../validation/D5-I187-preparation-review.json),
   el [auditor](../validation/D5-I187-audit.py) y el
   [sello documental](../validation/D5-I187-integrity.json).

El paquete tiene 55 definiciones locales acíclicas y siete alternativas finales
con discriminadores record_kind distintos. Todos los objetos de campos fijos
son cerrados y obligatorios; los mapas/arrays tienen tipos y cardinalidades
finitas. Los estados no registrados usan tags explícitos, sin null, objetos
abiertos, campos extra o extensiones opacas.

## Dos archivos, un cuerpo exacto

context_record y launch_record son aliases de final_record. Las futuras rutas
son docs/validation/D5-PRP181-P01/context.json y
docs/validation/D5-PRP181-P01-launch.json. Deben contener exactamente el mismo
cuerpo UTF-8 JCS, sin BOM, LF o bytes sobrantes. No se crea una tercera copia
launch.json dentro del directorio. Cada copia física se cobra por separado.
No se crea ahora ninguna de esas rutas.

Es un formato nuevo, incompatible con los contextos legacy. Se conserva el
perfil candidato 02 y su contrato de protocolo sin cambiar sus bytes. El
paquete complementario I187 debe quedar seleccionado por digest en las seis
fuentes sucesoras revisadas y, por esas fuentes, en el scope de la raíz y la
suite E06. output_schema_pack_sha256 debe coincidir con esa constante aceptada.
No se añade una lectura gratuita de schema, una nueva fuente o un pin de
salida al grafo antecedente. El código y sus hashes reales aún no existen.

## Ramas completas y selección

| record_kind | capture_status | Condición principal |
| --- | --- | --- |
| TRACE | TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW | Todos los predicados positivos, sin cerrar suficiencia o D5 |
| BLOCKED | BLOCKED | Bloqueo real: exit no cero, captura incompleta, descendientes u otro predicado explícito |
| WORKER_FAILURE | BLOCKED_WORKER_FAILURE | Diagnóstico FAILED auténtico y válido; prioridad sobre otros fallos ordinarios |
| TIMEOUT | BLOCKED | Retorno false real de wait_worker, sin diagnóstico FAILED válido |
| LAUNCH_ABORTED | INVALID_CAPTURE | Aborto anterior a READY sin inventar proceso, handshake o observaciones |
| INVALID | INVALID_CAPTURE | Fallo real de parent/root/inputs/packet/package |
| BUDGET_FALLBACK | INVALID_CAPTURE | No cabe o no se puede serializar el registro completo; conserva binding y errores reales |

Todas las ramas conservan scope P01, perfil 02, binding de raíz/invocación/
contexto/solicitud, owner verificado y flags closure/D5_closed/publicación false.
El literal funcional describe la admisión previa requerida; un archivo no
concede autoridad. Una expiración o fallo posterior no borra el binding
histórico ni afirma permiso vigente.

Antes de admisión completa y reserva/owner seguros no existe par persistente.
no_pair_diagnostic tiene schema distinto, es sólo un retorno acotado en memoria
y nunca sustituye los archivos, autoriza paths o finge binding. Si no puede
conservarse verazmente el binding/owner, falta memoria para codificar o falla
owner/write/close, tampoco existe un par válido. No se garantiza un registro
completo ante cualquier fallo de recursos.

## Metadatos completos y fieles

Las ramas completas tipan invocación pública, interpreter/environment, argumentos
observados, snapshots de runner y de los 494 pins, comparación exacta, proceso/
wait/exit/diagnóstico, limpieza, recibos INVOKE/READY/RELEASE, páginas/causalidad,
inventario, contadores Reader, comprobación de paquete y errores del padre.
Se proyectan los 21 campos observados del constructor/actualizaciones de context
en I122, con seis anclas AST para las fuentes de launch/invocation/comparación/
limpieza/páginas. No se importan ni ejecutan esas funciones.

Los maps del runner deben corresponder a los inputs efectivos originales
(79 actualmente) y a lecturas/discovery reales; ni maps vacíos coincidentes
ni diferencias sólo documentales habilitan TRACE. Las listas de comparación
se calculan exactamente y permanecen ordenadas, sin duplicados o truncamiento.
Los snapshots de captura son exactamente los 494 pins reales del payload.

NOT_RECORDED no prueba que una operación no sucediera. Se distingue proceso
confirmado sin iniciar de identidad desconocida. El retorno true de wait_worker
no es prueba de salida física: TRACE exige además exit0 observado, diagnóstico
COMPLETED/run UUID real, grupo propio desaparecido, handshake auténtico,
rechecks completos y validación real de raw/sidecar/páginas/causalidad.

Los exit codes negativos se representan mediante sign/magnitude, conservando
la regla de enteros JSON no negativos seguros del perfil 02. NEGATIVE exige
magnitud positiva; exit desconocido nunca se transforma en cero. Strings de
runtime fuera del dominio ASCII/longitudes o desbordamientos producen fallo
explícito/fallback, sin recortar valores o inventar datos.

El diagnóstico preserva el primer fallo real latched y mantiene los errores de
artefacto/padre separados. COMPLETED no implica PASS funcional. Un diagnóstico
malformado/no confiable no se convierte en FAILED ficticio. El fallback conserva
el diagnóstico disponible y parent_error, y declara qué secciones omite;
ninguna omisión se interpreta como evidencia completa.

## Par, inventario y escrituras parciales

El inventario excluye ambos archivos de metadatos para evitar autopins o un
fixed point de tamaño/hash propio. Incluye sólo OWNER/raw/sidecar y las páginas
reales contiguas, con nombres únicos y caps existentes. El consumidor posterior
computa el paquete como suma de esos miembros más dos veces el tamaño del
cuerpo canónico, con hasta 37 miembros lógicos y cap 140.513.280 bytes para
aceptar el paquete de captura.

PLANNED_PAIR_WITHIN_LIMITS_EXISTING_MEMBERS_VERIFIED sólo afirma lecturas reales
de miembros existentes y presupuesto del cuerpo planeado. No acredita que las
dos copias se hayan escrito. El consumidor exige ambos archivos completos,
iguales y válidos, owner/procedencia y caps de metadatos para un par completo.
Aceptar el paquete de captura exige además inventario físico y todas las
relaciones/cotas de artefactos. Un par de fallo veraz sólo es diagnóstico:
no acepta un paquete incompleto o sobredimensionado. Un descriptor no puede
recortar el tamaño real; si no lo representa, debe declarar fallo/NOT_RECORDED
o fallback, sin convertir la ausencia de validación en conformidad. Una copia
ausente, distinta o parcial invalida el par; no se añade, sobrescribe o repara
una salida parcial para aparentar publicación. El owner se verifica antes de
escribir mediante los descriptores propios reservados de forma exclusiva.

## Cota estructural de bytes

| Rama | Upper de bytes canónicos |
| --- | ---: |
| TRACE | 4.457.699 |
| BLOCKED | 10.798.475 |
| WORKER_FAILURE | 10.798.372 |
| TIMEOUT | 10.798.440 |
| LAUNCH_ABORTED | 10.795.692 |
| INVALID | **10.798.483** |
| BUDGET_FALLBACK | 2.314 |
| Diagnóstico sin par, sólo memoria | 315 |

La derivación recorre el schema acíclico: longitud exacta de literales/enums,
máximos de cardinalidad, delimitadores y hasta dos bytes por carácter ASCII
variable para cubrir escapes. Usa el máximo entre alternativas. Es una cota
conservadora de cuerpos que cumplan schema más dominio de codificación, no una
medición o simulación de ejecución. Las reglas semánticas pueden reducir las
combinaciones permitidas y deben verificarse por separado.

Cada copia conserva cap 12.582.912; fallback y diagnóstico sin par tienen
además techo propuesto 8.192. El presupuesto de paquete y todos los candidatos
numéricos quedan intactos. La cota serializada no demuestra memoria transitoria,
CPU, número de lecturas/escrituras, completitud de observaciones, aceptación
real de inputs o los 900 segundos. Todas las copias/maps/listas, validación,
encode/hash, dos escrituras, errores, IO/GC/nativo siguen dentro de E01–E05 y las
ventanas launch/worker/finish, sin trasladar trabajo fuera de fase.

## Estado y verificación

`python3 docs/validation/D5-I187-audit.py`: PASS_STATIC_SOURCE_ONLY esperado.
Contrasta 728 pins contra Git y preserva 420 archivos publicados. Reproduce la
revisión I186 sólo mediante funciones documentales; valida estructura/ref,
discriminadores, claves obligatorias, rechazos, cotas y la proyección AST.
Los placeholders existen sólo en memoria, con digests/identidades ficticios:
no son cuerpos positivos, autoridad o evidencia runtime emitida.

La reparación documental de F183-01 y las ocho exclusiones quedan preservadas.
Siguen pendientes revisión/adopción de este contrato, implementación/guard y
bootstrap transport exactos, biblioteca y caller/custodia reales; requalification
de 179 casos/321 raíces/12 grupos/30 sitios, todo E01–E05 y todas las rutas de
metadatos/fallo; E06 final real, requests/contexto/raíces/firmas y decisiones
separadas. Este trabajo prepara los formatos completos; no implementa su
productor/consumidor ni cierra F179-01, admisión o D5.

La unidad son los seis archivos de work_unit.rollback_files: documento,
paquete, contrato, preparación, auditor y sello. Rollback limitado a ellos.
El diff supera 400 líneas por contratos cerrados y evidencia trazable; se
informa el exceso. Runtime harness N/A: preparación documental sin cambio
runtime. Auditoría antes de stage y tras commit; commit/push solicitados y
verificación de remoto/árbol limpio. Publicar no adopta ni concede autoridad.

E01–E05 abiertos, E06 NOT_RUN; I122 IMPLEMENTED_NOT_ADMITTED, CP07/correlación
false, cuatro bindings I175 pendientes, sin SOURCE_CAPACITY_VERIFIED/rebind/
autoridad o destino nuevos/propuesta o captura habilitadas. D5/H07 abiertos e
IR03 NOT_READY. P0 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1, D1–D4 e I1–I20/A52
intactos; brechas globales/reales pendientes. I86/I89/I92 INVALID_CAPTURE no
se reanudan ni mezclan.

Sin ejecutar/importar/compilar producto/componentes, tests, discovery,
benchmarks, criptografía o calendarios runtime ni medir plataforma. Sin cambiar
fuentes, schemas/contratos activos, cuotas, presupuestos, reservas o inputs;
sin inspeccionar ni limpiar dev/run_data/D4. Sin cuerpos context/launch,
claves, firmas, autoridad o evidencia positiva reales creados; sin proveedores,
credenciales, consumo, activación, promoción, despliegue o D6.
