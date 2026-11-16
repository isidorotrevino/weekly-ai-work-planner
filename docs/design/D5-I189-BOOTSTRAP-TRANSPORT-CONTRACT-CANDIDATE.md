# I189 — Bootstrap confiable y transporte candidatos, sin admisión

Fecha: 2026-11-16, Europe/Madrid. Base:
`faed688f34e0cda165f7630ca0ccb1fea973f4c3`.

**I189 prepara PGO181-BOOTSTRAP-TWO-PIPE-CANDIDATE-01 para el perfil 02.**
Reutiliza las dos pipes de READY/RELEASE y entrega contexto, solicitud e INVOKE
antes de READY; exige EOF de READY antes de RELEASE y EOF de RELEASE antes
del import funcional. El límite de bytes en ambos sentidos es 11.778.
Es un contrato por revisar, sin adoptar o implementar. El caller/runtime y su
entrada inmutable siguen sin acreditar; I122/PJC115-R2 continúa sin admisión,
F179-01 y D5 abiertos.

## Ruta de revisión

1. Leer el [contrato](../validation/D5-I189-BOOTSTRAP-TRANSPORT-CONTRACT-CANDIDATE.json):
   frontera de confianza, ownership, framing, plazos, one-use y fallos.
2. Contrastar la [gramática y dependencias](../validation/D5-I189-BOOTSTRAP-TRANSPORT-GRAMMAR-CANDIDATE.json).
3. Revisar la [preparación](../validation/D5-I189-preparation-review.json),
   el [auditor](../validation/D5-I189-audit.py) y el
   [sello documental](../validation/D5-I189-integrity.json).

Los bytes de perfil/protocolo 02 e I187 permanecen intactos. No se crean
fuentes sucesoras, procesos worker, pipes de protocolo, contextos, solicitudes,
claves, firmas, autoridad o captura. Las dos anclas AST muestran el flujo I122
actual: el nuevo orden de bootstrap requeriría código distinto, no un rebind
directo o interpretación nueva aplicada al parser existente.

## La confianza antecede al primer código de repositorio

La ruta elegida requiere un caller ya aceptado por custodia de runtime/
plataforma y una entrada de módulo en una imagen confiable. Interpreter,
loader/stdlib/nativo y las seis fuentes sucesoras deben estar autenticados e
inmutables desde la entrada hasta guard/import. R01/R02 deben acreditar el
mapeo exacto fuente-imagen; R06/R08 y las demás competencias deben aceptar
custodia, scope, roles y evidencia reales. Esa imagen no se suministra aquí.

No se admite ejecutar primero un módulo mutable desde cwd/PYTHONPATH/
sitecustomize y autenticarlo después. Si la plataforma no puede acreditar
la ruta inmutable, el arranque rechaza. La propuesta no presupone que el
runtime actual proporcione esas garantías ni autoriza construir/desplegar
una imagen en este incremento.

La procedencia del canal viene de una capacidad de creación de proceso del
caller aceptado, con endpoints exclusivos bajo custodia. Un fd, fstat, PID,
key_id, digest o argv no autentica por sí solo al caller. La plataforma debe
excluir inyección/duplicación de descriptores, tracing/mutación hostil del
proceso, sustitución de imagen y shadowing del loader. Sin esas garantías,
no se inicia el protocolo; una pipe arbitraria no es una capacidad confiable.

C y Q contienen contexto y solicitud auténticos congelados del caller.
Una vez recibidos, el worker vuelve a validar el schema/codec, perfil/tiempo/
roles, raíz y los nueve predicados de admisión sobre los cuerpos reales,
con su Input Reader existente. La validación del padre no sustituye la del
worker. No viajan claves privadas o secretos; las claves públicas declaradas
sólo se aceptan por custodia y verificación real, no por presencia o secreto.

## Cinco frames, dos streams existentes

| Frame | Schema del paquete 02 | Sentido | Body máximo | Con LF |
| --- | --- | --- | ---: | ---: |
| C | trust_context | Padre → worker | 8.192 | 8.193 |
| Q | runtime_request | Padre → worker | 2.048 | 2.049 |
| I | worker_invocation | Padre → worker | 511 | 512 |
| A | worker_ready | Worker → padre | 511 | 512 |
| L | parent_release | Padre → worker | 511 | 512 |

Cada frame es el cuerpo UTF-8 JCS del schema existente más un único LF 0x0a,
sin header, prefijo, tag o wrapper nuevo. C/Q mantienen los caps de perfil 02;
I/A/L mantienen el máximo de 512 incluido LF. El estado determina el schema
esperado, sin inferir autoridad de claves dentro de un JSON no confiable.

El padre conserva sólo release_write/ready_read; el worker sólo
release_read/ready_write. Se conservan los seis operandos observados de I187:
P01, sidecar fd, ready fd, release fd, directory fd y lease. Los cuatro fds
explícitos son distintos y mayores que 2; stdout es el raw regular, sidecar
otro regular y directory el directorio propio. Modos, tipos, fingerprints,
owner/lease, pid=pgid y sesión se verifican, además de la custodia de origen.

No se agrega una pipe de control, input de repositorio o proceso auxiliar.
Los descriptores internos de spawn/runtime siguen necesitando prueba exacta
de recursos y cierre; no se declaran gratuitos. Todos los extremos opuestos/
duplicados se cierran y ningún descendiente funcional hereda control abierto.

## Orden que evita esperar EOF demasiado pronto

1. Padre autentica caller, contexto/solicitud y raíz completa; reclama one-use
   antes de paths, pipes o spawn. Reserva owner y crea el worker aceptado.
2. Padre escribe C, Q, I mientras el worker consume bytes. Mantiene abierto
   el stream down para L. Worker **no espera EOF después de I**.
3. Worker verifica C/Q/I, raíz real, roles, owner y canales antes de A.
   Escribe A y cierra su writer up.
4. Padre exige A exacto y EOF sin bytes extra; revalida raíz/contexto/solicitud/
   owner/peer vigentes antes de escribir L y cerrar su writer down.
5. Worker exige L exacto y EOF sin bytes extra; hace el recheck final y sólo
   entonces podría llegar al import funcional ya autorizado por separado.

Los mensajes comparten exactamente raíz, invocación, contexto y solicitud.
El orden correcto del emisor y la custodia exclusiva son requisitos de las
fuentes aceptadas: los bytes no prueban por sí solos cuándo el peer los envió.
READY, firma, pipe o salida del padre nunca autorizan el import por separado.

La gramática tiene 12 estados locales del padre y 11 del worker: 23 nodos en
un grafo de precedencias acíclico. No es una enumeración del producto de estados
concurrentes, un calendario ejecutado o una prueba del kernel/implementación.
Todas las clases de fallo son terminales para la invocación.

## Lecturas cortas, plazos e intentos

Se propone lectura nonblocking de un byte para no sobreleer/cargar el siguiente
frame; se acumula sólo el body actual y su delimitador dentro de cap. El writer
pide hasta 4.096 bytes, avanza por el número realmente escrito y nunca repite
prefijos ya enviados. EOF a mitad de frame, bytes extra terminales, JSON no
canónico, mismatch, EPIPE o error fatal rechazan. EINTR/EAGAIN, cero progreso y
esperas consumen los mismos presupuestos; se espera readiness sin busy-spin.

El comportamiento de streams y transferencias parciales está documentado en
[read(2)](https://man7.org/linux/man-pages/man2/read.2.html),
[write(2)](https://man7.org/linux/man-pages/man2/write.2.html) y
[pipe(7)](https://man7.org/linux/man-pages/man7/pipe.7.html). Esta ruta no
presupone tamaño de pipe, atomicidad de mensajes, una lectura por escritura o
que write exitoso pruebe validación del receptor. No se aumenta su capacidad.

Cada endpoint tiene un único plazo absoluto de 20 segundos: el padre desde
inmediatamente antes de crear proceso; el worker desde su entrada confiable.
Son orígenes distintos, no timestamps compartidos. Ningún frame/byte/retry
reinicia el plazo. La expiración del contexto/raíz o de la fase también rechaza.
El launch t0..tR incluye freeze y admisión previos, setup, spawn y todo el
handshake hasta LF/cierre de RELEASE; no se oculta trabajo fuera de fase.

Hay como máximo 65.536 intentos IO/readiness combinados por endpoint durante
todo el handshake, incluidos retries y comprobación de EOF. Se recalcula tiempo
restante en cada espera; el reloj y las garantías de bloqueo/scheduler deben
ser realmente aceptados. Exceder plazo/contador rechaza, no promete servicio.

| Partida de diseño | Cota |
| --- | ---: |
| Padre → worker, C+Q+I+L | 11.266 bytes |
| Worker → padre, A | 512 bytes |
| Ambos streams | **11.778 bytes** |
| Bytes transferidos contando lectura y escritura | 23.556 |
| Llamadas de progreso byte a byte más dos lecturas EOF | 23.558 |
| Intentos totales, ambos endpoints | 131.072 |

Las cotas son de bytes/progreso y límites de rechazo. No prueban heap, número
real de syscalls, CPU, reloj, latencia o 900 segundos. Parsing, copia, firma,
fstat/owner, poll/clock, startup, cierre, errores, limpieza, writes y todos los
costes nativos necesitan composición E01–E05 y cotas de fase completas.

Las pipes no reemplazan lecturas del repositorio. Cada dominio coordinador/
worker conserva su mismo ledger BEFORE/AFTER/FINISH; lecturas duplicadas entre
procesos y bytes transportados deben contarse en el join global de recursos.
Las 496 rutas/266.693.693 siguen siendo aritmética Reader condicionada de las
fuentes aún pendientes, no una prueba agregada del nuevo código.

## One-use, fallos y salida compatibles con I187

La reclamación del caller es atómica y anterior a paths/spawn. Una invocación
fallida queda gastada; no se reconecta, reinicia stream o reutiliza la raíz
tras timeout, write parcial o spawn fallido. El worker es el hijo correlacionado
de esa única reclamación, no una segunda solicitud o consumo independiente.
Reintentar exige otra autorización/contexto/solicitud/raíz genuinos y futuros.
La unicidad y el estado persistente ante reinicio siguen sin implementarse.

Sin canales/owner confiables no se escribe diagnóstico a sidecar/raw ni se
manda control; se cierran sólo recursos propios y se para sólo el grupo de
propiedad demostrada. Tras custodia aceptada puede preservarse el primer fallo
real mediante diagnóstico acotado y código sanitizado; no hay error frames
nuevos o READY/RELEASE inventados. C/Q/clave/contexto no se vuelcan a raw,
sidecar, environment o artefactos adicionales.

I187 ya admite los seis argumentos y recibos I/A/L con su binding común.
C/Q quedan representados por los digests de contexto/solicitud existentes,
sin extender schema o fingir que se grabó un transcript de bootstrap.
La salida usa observaciones reales y las reglas de fallback/no-pair y par
parcial de I187. Un fallo conserva binding histórico tras admisión, no permiso
vigente ni aceptación de paquete.

## Verificación y estado

`python3 docs/validation/D5-I189-audit.py`: PASS_STATIC_SOURCE_ONLY esperado.
Comprueba 739 pins contra Git y preserva 431 archivos publicados. Verifica
refs/caps, secuencias y dependencias declaradas, exclusiones de orden, dos anclas
AST, aritmética y compatibilidad de formatos, sin crear canales/worker ni
implementar/ejecutar un parser de streams. Reproduce sólo herramientas
Git/JSON/AST/grafos documentales; no importa producto o componentes.

El mismo asistente prepara este contrato y las etapas anteriores. No hay
independencia de actor/organización, nombramientos, imagen/runtime, claves,
clock/custodia o aceptación real. Siguen pendientes revisión/adopción del
contrato, implementación autorizada del loader/guard/transporte/output,
mapeo fuente-imagen, requalification de 179/321/12/30 y E01–E05, pruebas reales
Reader/heap/CPU/servicio/900, E06 final y toda evidencia/decisión de admisión.
F183-01 conserva su reparación documental y las ocho exclusiones; F179-01 y
D5 siguen abiertos. I189 no habilita producto, componentes o captura.

La unidad consta de seis archivos en work_unit.rollback_files: documento,
contrato, gramática, preparación, auditor y sello. Rollback limitado a ellos.
El diff supera 400 líneas por especificación/evidencia trazables; se informa
el exceso. Runtime harness N/A: sólo preparación documental. Auditoría antes
de stage y tras commit; commit/push solicitados y comprobación remoto/árbol
limpio. La publicación no adopta ni concede autoridad.

E01–E05 abiertos, E06 NOT_RUN; I122 IMPLEMENTED_NOT_ADMITTED, CP07/correlación
false y cuatro bindings I175 pendientes. Sin SOURCE_CAPACITY_VERIFIED, rebind,
autoridad/destino nuevos, propuesta/captura habilitadas o D5/H07 cerrados;
IR03 NOT_READY. P0 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1, D1–D4 e I1–I20/A52
intactos; brechas globales/reales pendientes. I86/I89/I92 INVALID_CAPTURE no
se reanudan ni mezclan.

Sin ejecutar/importar/compilar producto/componentes, tests, discovery,
benchmarks, criptografía o calendarios runtime ni medir plataforma. Sin cambiar
fuentes, schemas/contratos activos, cuotas, presupuestos, reservas o inputs;
sin inspeccionar ni limpiar dev/run_data/D4. Sin procesos/canales de protocolo,
claves, firmas, autoridad o evidencia positiva reales creados; sin proveedores,
credenciales, consumo, activación, promoción, despliegue o D6.
